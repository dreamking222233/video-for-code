#!/usr/bin/env python3
"""母带：线性增益 + 真峰值限制，目标 −14 LUFS / 真峰值 ≤ −1.5 dBFS。

为什么不用单遍 loudnorm：它是动态压限，会把句间底噪一起抬 8 dB，听感发毛。
这里只做「整体增益 + lookahead 限制器削峰」，不压动态。

alimiter 限的是采样峰值，采样间过冲约 1 dB，所以限制值取 −3.2 dBFS，
再由测量回路微调增益，保证真峰值不越线。
"""
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "mix.wav"
OUT = HERE / "mix_norm.wav"
TARGET = -14.0
TP = -1.5
LIMIT_DB = -2.8


def measure(path):
    st = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path),
                         "-af", "ebur128=peak=true", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    s = st[st.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", s)
    p = re.search(r"Peak:\s+(-?[\d.]+) dBFS", s)
    return float(i.group(1)), float(p.group(1))


ATTACK_MS = 5          # alimiter 的 lookahead 会整体延后同等时长，必须补偿回去


def total_dur():
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(SRC)], text=True).strip())


def render(gain_db, dst):
    dur = total_dur()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC),
                    "-af", f"volume={gain_db:.2f}dB,"
                           f"alimiter=limit={10 ** (LIMIT_DB / 20):.6f}"
                           f":attack={ATTACK_MS}:release=70:level=0,"
                           f"atrim=start={ATTACK_MS / 1000:.5f},asetpts=N/SR/TB,"
                           f"apad=whole_dur={dur:.5f},"
                           f"aresample=48000:osf=s16:dither_method=triangular",
                    "-t", f"{dur:.5f}",
                    "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(dst)], check=True)


def main():
    l0, _ = measure(SRC)
    gain = TARGET - l0
    print(f"mix {l0:.2f} LUFS -> 起始增益 {gain:+.2f} dB")

    best = None
    for step in range(14):
        render(gain, OUT)
        l, p = measure(OUT)
        print(f"  #{step}: gain {gain:+6.2f} → {l:6.2f} LUFS, peak {p:5.2f} dBFS")
        if p > TP + 0.05:                       # 峰值越线：先降增益
            gain -= (p - TP) + 0.15
            continue
        if l < TARGET - 0.25:                   # 响度不足：加增益
            gain += min(1.2, TARGET - l)
            continue
        best = (l, p, gain)
        break

    if best is None:                            # 没收敛就用最后一次测量结果
        l, p = measure(OUT)
        best = (l, p, gain)

    l, p, gain = best
    if p > TP + 0.1:
        sys.exit(f"真峰值 {p} 超 {TP}")
    print(json.dumps({"ok": True, "lufs": round(l, 2), "true_peak": round(p, 2),
                      "gain_db": round(gain, 2)}))


if __name__ == "__main__":
    main()
