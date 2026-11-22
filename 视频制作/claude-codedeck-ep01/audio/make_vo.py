#!/usr/bin/env python3
"""调用 音频训练/tts.py（默认音色 qwen_v2_24）逐句生成配音，并产出 marks 驱动的时间轴。

用法：
    export DASHSCOPE_API_KEY=sk-xxx
    python3 audio/make_vo.py

产出：
    audio/clone/sN.wav            逐镜配音（-18 LUFS / -1.5 dBTP stem 电平）
    audio/clone/sN_marks.json     每镜的句级时间轴
    audio/vo_clone.wav            拼接后的整段配音（48k mono）
    audio/vo_timeline.json        {total, scenes:[{id,start,end,text}], subs:[[s,e,text],...]}
"""
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
TTS = pathlib.Path("/Volumes/文件/自媒体/音频训练/tts.py")
SR = 48000


def run_tts(text, out_wav, marks_out, rate):
    cmd = [
        sys.executable, str(TTS),
        "--text", text,
        "--out", str(out_wav),
        "--rate", str(rate),
        "--unit", "sentence",
        "--marks-out", str(marks_out),
        "--json",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:], file=sys.stderr)
        sys.exit(r.returncode)
    return json.loads(r.stdout.strip().splitlines()[-1])


def dur(path):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True).stdout.strip())


def concat(parts, gap, out):
    sil = HERE / "clone" / "_gap.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                    "-i", f"anullsrc=r={SR}:cl=mono", "-t", str(gap),
                    "-c:a", "pcm_s16le", str(sil)], check=True)
    lst = HERE / "clone" / "_concat.txt"
    with open(lst, "w") as f:
        for i, p in enumerate(parts):
            f.write(f"file '{p.resolve()}'\n")
            if i < len(parts) - 1:
                f.write(f"file '{sil.resolve()}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-ar", str(SR), "-ac", "1",
                    "-c:a", "pcm_s16le", str(out)], check=True)


def split_display(text, max_chars=24):
    """把一镜的文案切成字幕块：优先按标点切，单块不超过 max_chars。"""
    import re
    parts, buf = [], ""
    for ch in text:
        buf += ch
        if ch in "。！？；，、：":
            parts.append(buf)
            buf = ""
    if buf:
        parts.append(buf)
    # 合并过短的块，拆开过长的块
    merged = []
    for p in parts:
        if merged and len(merged[-1]) + len(p) <= max_chars:
            merged[-1] += p
        else:
            merged.append(p)
    out = []
    for p in merged:
        while len(p) > max_chars * 1.6:
            cut = max(p.rfind("，", 0, int(max_chars * 1.4)), int(max_chars * 1.2))
            out.append(p[:cut])
            p = p[cut:]
        out.append(p)
    return [x.strip() for x in out if x.strip()]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rate", type=float, default=1.18, help="语速倍率；1.0≈4.7字/秒，1.18≈5.4")
    ap.add_argument("--gap", type=float, default=0.28, help="镜间停顿")
    ap.add_argument("--tail", type=float, default=2.6, help="片尾留给定版卡的秒数")
    a = ap.parse_args()
    rate, gap, tail = a.rate, a.gap, a.tail

    if not os.environ.get("DASHSCOPE_API_KEY"):
        print("缺少 DASHSCOPE_API_KEY（tts.py 需要它，缺失会 exit 2）", file=sys.stderr)
        sys.exit(2)

    lines = json.loads((HERE / "vo_lines.json").read_text(encoding="utf-8"))
    cdir = HERE / "clone"
    cdir.mkdir(exist_ok=True)

    scenes, parts, t = [], [], 0.0
    for i, ln in enumerate(lines):
        wav = cdir / f"{ln['id']}.wav"
        mk = cdir / f"{ln['id']}_marks.json"
        info = run_tts(ln["text"], wav, mk, float(ln.get("rate", rate)))
        d = dur(wav)
        parts.append(wav)
        scenes.append({"id": ln["id"], "text": ln["text"],
                       "start": round(t, 3), "end": round(t + d, 3)})
        print(f"  [{i+1}/{len(lines)}] {ln['id']}: {d:.2f}s  (cps {info.get('characters_per_sec')})",
              file=sys.stderr)
        t += d + gap

    vo = HERE / "vo_clone.wav"
    concat(parts, gap, vo)
    total_vo = dur(vo)

    # 降噪：压掉底噪，但要补偿 anlmdn 的群延迟（实测 380 采样 = 7.92ms），
    # 否则整条旁白会比字幕/画面晚 1/4 帧。
    clean = HERE / "vo_clean.wav"
    LAG = 380
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vo),
                    "-af", f"highpass=f=75,anlmdn=s=7:p=0.002:r=0.006,"
                           f"atrim=start_sample={LAG},asetpts=N/SR/TB,"
                           f"apad=whole_dur={total_vo:.5f}",
                    "-t", f"{total_vo:.5f}",
                    "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(clean)], check=True)
    if abs(dur(clean) - total_vo) > 0.02:
        sys.exit(f"降噪后时长 {dur(clean)} 与旁白 {total_vo} 不一致")
    print(f"  denoised -> {clean}", file=sys.stderr)

    # 字幕：镜内按字数比例分配时间
    subs = []
    for sc in scenes:
        text = sc["text"]
        chunks = split_display(text)
        span = sc["end"] - sc["start"]
        weights = [len(c) for c in chunks]
        acc = sum(weights)
        cursor = sc["start"]
        for c, w in zip(chunks, weights):
            d = span * w / acc
            subs.append([round(cursor, 3), round(cursor + d, 3), c])
            cursor += d

    # 字幕行尾不要挂「，」「、」：把标点并到下一行开头
    for i in range(len(subs) - 1):
        while subs[i][2] and subs[i][2][-1] in "，、":
            subs[i + 1][2] = subs[i][2][-1] + subs[i + 1][2]
            subs[i][2] = subs[i][2][:-1]

    # 桥接镜间小间隙，避免字幕条"消失-再出现"闪一下
    for i in range(len(subs) - 1):
        g = subs[i + 1][0] - subs[i][1]
        if 0 < g <= 0.30:
            subs[i][1] = round(subs[i + 1][0], 3)

    vo_end = round(scenes[-1]["end"], 3)
    total = round(vo_end + tail, 3)
    cps = sum(len(x["text"]) for x in lines) / total_vo
    tl = {"total": total, "vo_total": round(total_vo, 3), "vo_end": vo_end,
          "rate": rate, "gap": gap, "scenes": scenes, "subs": subs}
    (HERE / "vo_timeline.json").write_text(
        json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"VO {total_vo:.2f}s ({cps:.2f} 字/秒) -> 片长 {total}s, {len(subs)} 条字幕",
          file=sys.stderr)
    print(json.dumps({"ok": True, "total": total, "scenes": len(scenes), "subs": len(subs)}))


if __name__ == "__main__":
    main()
