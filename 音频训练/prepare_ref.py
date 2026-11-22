#!/usr/bin/env python3
"""
把一段录音整理成语音克隆模型可用的参考音频。

用法:
    python3 prepare_ref.py 输入.m4a [-o 输出目录]

做四件事，且只做这四件（多做会伤音色，实测已排除）:
  1. 解码并修容器坏帧 —— 转成标准 PCM WAV
  2. 按语音密度自动选窗 —— 切点落在停顿处，不切半句
  3. 线性电平归一 —— 不改动态，目标 -20 LUFS，真峰值留 2 dB 余量
  4. 输出厂商要求的规格 —— 48 kHz / 单声道 / 16-bit，带三角抖动

刻意不做: 降噪、EQ、压缩、门限。实测这段素材加这些只会损失相似度。
"""
import argparse, json, os, re, subprocess, sys, wave
import numpy as np

SR = 48000
TARGET_LUFS = -20.0
MAX_TRUE_PEAK = -2.0

# 目标时长: 阿里推荐 10~20s, 火山要求 14~30s
TARGETS = {"bailian": 17.0, "volc": 24.0}


def sh(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg 失败:\n{' '.join(cmd)}\n{r.stderr[-1500:]}")
    return r


def load(path):
    with wave.open(path, "rb") as w:
        n, ch, _, sr = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
        buf = w.readframes(n)
    x = np.frombuffer(buf, dtype="<i2").astype(np.float64) / 32768.0
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    return x, sr


def analyse(x):
    fl = int(SR * 0.02)
    nf = len(x) // fl
    db = 20 * np.log10(np.sqrt((x[: nf * fl].reshape(nf, fl) ** 2).mean(axis=1)) + 1e-20)
    noise = np.percentile(db, 10)
    voiced = db > noise + 9.0
    return db, voiced, noise


def pick_window(voiced, seconds):
    """在语音密度最高、切点落在静音处、且窗内最长停顿最小的位置开窗。"""
    wl = int(seconds / 0.02)
    best = None
    for i in range(nf := len(voiced) - wl + 1):
        seg = voiced[i:i + wl]
        if voiced[i] or voiced[i + wl - 1]:
            continue  # 切点必须落在静音, 否则会切半句
        density = seg.mean()
        run = maxrun = 0
        for v in seg:
            run = 0 if v else run + 1
            maxrun = max(maxrun, run)
        score = density * 100 - maxrun * 0.4
        if best is None or score > best[0]:
            best = (score, i, density, maxrun)
    if best is None:
        sys.exit("找不到切点落在静音处的窗口")
    _, i, density, maxrun = best
    return i * 0.02, (i + wl) * 0.02, density, maxrun * 0.02


def integrated_lufs(path):
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", path,
         "-af", "ebur128=peak=true", "-f", "null", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stderr
    i = re.findall(r"I:\s+(-?\d+\.\d+) LUFS", out)
    p = re.findall(r"Peak:\s+(-?\d+\.\d+) dBFS", out)
    return float(i[-1]), float(p[-1])


def trim(src, dst, a, b, fade_in=0.05, fade_out=0.10):
    d = b - a
    sh(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src,
        "-af", f"atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,"
               f"afade=t=in:st=0:d={fade_in},afade=t=out:st={d-fade_out:.3f}:d={fade_out}",
        "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", dst])


def normalize(src, dst, gain_db):
    sh(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src,
        "-af", f"volume={gain_db:.2f}dB,aresample={SR}:osf=s16:dither_method=triangular",
        "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", dst])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--outdir", default="processed")
    ap.add_argument("--tag", default="", help="文件名后缀，便于区分多段参考音频")
    ap.add_argument("--json-out", help="把报告写入 JSON 文件")
    args = ap.parse_args()
    tag = f"_{args.tag}" if args.tag else ""

    os.makedirs(args.outdir, exist_ok=True)
    tmp = os.path.join(args.outdir, "_tmp_decode.wav")
    print(f"[1/4] 解码 {args.input}")
    sh(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", args.input,
        "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", tmp])

    x, _ = load(tmp)
    db, voiced, noise = analyse(x)
    dur = len(x) / SR
    peak = 20 * np.log10(np.abs(x).max() + 1e-30)
    print(f"      时长 {dur:.2f}s  峰值 {peak:.2f} dBFS  底噪 {noise:.1f} dB  语音占比 {voiced.mean()*100:.1f}%")

    print("[2/4] 选窗")
    report = {}
    for name, seconds in TARGETS.items():
        if dur < seconds:
            print(f"      跳过 {name}: 素材只有 {dur:.1f}s")
            continue
        a, b, density, maxpause = pick_window(voiced, seconds)
        stage = os.path.join(args.outdir, f"_tmp_{name}.wav")
        trim(tmp, stage, a, b)

        print("[3/4] 归一 + 导出")
        lufs, tp = integrated_lufs(stage)
        gain = TARGET_LUFS - lufs
        if tp + gain > MAX_TRUE_PEAK:          # 安全阀: 不让峰值撞顶
            gain = MAX_TRUE_PEAK - tp
        dst = os.path.join(args.outdir, f"ref{tag}_{name}_{seconds:.0f}s.wav")
        normalize(stage, dst, gain)
        os.remove(stage)

        l2, p2 = integrated_lufs(dst)
        report[name] = dict(file=os.path.basename(dst), start=round(a, 2), end=round(b, 2),
                            duration=round(b - a, 2), density=round(density * 100, 1),
                            max_pause=round(maxpause, 2), gain_db=round(gain, 2),
                            lufs=round(l2, 1), true_peak=round(p2, 1),
                            size_mb=round(os.path.getsize(dst) / 1e6, 2))
        print(f"      {os.path.basename(dst)}: {b-a:.2f}s  {density*100:.0f}% 语音  "
              f"最长停顿 {maxpause:.2f}s  增益 {gain:+.1f}dB  {l2:.1f} LUFS  TP {p2:.1f} dBFS")

    os.remove(tmp)
    print("[4/4] 完成\n")
    out = json.dumps(report, ensure_ascii=False, indent=2)
    print(out)
    if args.json_out:
        open(args.json_out, "w", encoding="utf-8").write(out)


if __name__ == "__main__":
    main()
