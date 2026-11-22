#!/usr/bin/env python3
"""把现成的新旁白（cosy_v2，91.78s）接入时间轴：不重新合成，只做对齐与重排。

输入：
    audio/final/vo_v2_matched_91s78.wav          旁白
    audio/final/vo_marks_v2_91s78.json           逐镜 marks
    audio/vo_lines.json                          6 镜文案（字幕用）
输出：
    audio/vo_clone.wav     旁白原始（48k mono）
    audio/vo_clean.wav     轻度降噪版（时长不变，供混音）
    audio/vo_timeline.json {total, vo_end, scenes[], subs[]}
"""
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SR = 48000

VO_SRC = HERE / "final" / "vo_v2_matched_91s78.wav"
MARKS = HERE / "final" / "vo_marks_v2_91s78.json"
LINES = HERE / "vo_lines.json"


def dur(p):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(p)], text=True).strip())


def split_display(text, max_chars=24):
    parts, buf = [], ""
    for ch in text:
        buf += ch
        if ch in "。！？；，、：":
            parts.append(buf)
            buf = ""
    if buf:
        parts.append(buf)
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


def _lag(ref, test):
    """测 test 相对 ref 的整数采样延迟（取中段 20s 互相关）。"""
    import numpy as np

    def load(p):
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1",
                            "-ar", str(SR), "-f", "f32le", "-"],
                           capture_output=True).stdout
        return np.frombuffer(r, dtype=np.float32).astype(np.float64)

    a, b = load(ref), load(test)
    a = a[int(20 * SR):int(40 * SR)]
    b = b[int(20 * SR):int(40 * SR)]
    m = min(len(a), len(b))
    a, b = a[:m], b[:m]
    best, bestv = 0, -1e30
    for lg in range(-960, 961):
        if lg >= 0:
            c = float(np.dot(a[lg:], b[:m - lg]))
        else:
            c = float(np.dot(a[:m + lg], b[-lg:]))
        if c > bestv:
            best, bestv = lg, c
    return -best          # 正值 = test 落后于 ref


def main():
    marks = json.loads(MARKS.read_text(encoding="utf-8"))
    lines = {x["id"]: x["text"] for x in json.loads(LINES.read_text(encoding="utf-8"))}
    total = float(marks["total"])

    src_dur = dur(VO_SRC)
    if abs(src_dur - total) > 0.05:
        sys.exit(f"旁白时长 {src_dur} 与 marks.total {total} 不符（±0.05s）")

    # 1) 旁白入库（统一 48k / mono / 16bit）
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(VO_SRC),
                    "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le",
                    str(HERE / "vo_clone.wav")], check=True)

    # 2) 轻度降噪（与之前同一套参数；改的是噪声，不改音色）
    #    anlmdn 有约 8ms 群延迟，必须补偿，否则旁白会比字幕晚 1/4 帧
    raw = HERE / "vo_clean_raw.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "vo_clone.wav"),
                    "-af", "highpass=f=75,anlmdn=s=7:p=0.002:r=0.006",
                    "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le",
                    str(raw)], check=True)

    lag = _lag(HERE / "vo_clone.wav", raw)
    print(f"  降噪群延迟 {lag} 采样 ({lag / SR * 1000:.2f} ms) → 补偿")
    af = []
    if lag > 0:
        af += [f"atrim=start_sample={lag}", "asetpts=N/SR/TB"]
    af.append(f"apad=whole_dur={total}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw),
                    "-af", ",".join(af), "-t", f"{total}",
                    "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le",
                    str(HERE / "vo_clean.wav")], check=True)
    raw.unlink(missing_ok=True)

    d2 = dur(HERE / "vo_clean.wav")
    if abs(d2 - total) > 0.02:
        sys.exit(f"降噪后时长变了：{d2} vs {total}")

    # 3) 场景
    scenes, vo_end = [], 0.0
    for m in marks["marks"]:
        sid = m["id"]
        if sid not in lines:
            sys.exit(f"marks 里的 id {sid} 在 vo_lines.json 中找不到文案")
        scenes.append({"id": sid, "text": lines[sid],
                       "start": round(float(m["start"]), 3),
                       "end": round(float(m["end"]), 3)})
        vo_end = max(vo_end, float(m["end"]))

    # 4) 字幕：镜内按字数比例分配
    subs = []
    for sc in scenes:
        chunks = split_display(sc["text"])
        span = sc["end"] - sc["start"]
        wsum = sum(len(c) for c in chunks) or 1
        cur = sc["start"]
        for c in chunks:
            d = span * len(c) / wsum
            subs.append([round(cur, 3), round(cur + d, 3), c])
            cur += d

    # 5) 桥接字幕间隙：marks 之间有 0.22s 静音，若严格按 marks 收尾，
    #    字幕条会“消失→再出现”闪一下。只桥接 <=0.3s 的小间隙，长停顿仍然隐藏。
    for i in range(len(subs) - 1):
        gap = subs[i + 1][0] - subs[i][1]
        if 0 < gap <= 0.30:
            subs[i][1] = round(subs[i + 1][0], 3)

    tl = {"total": round(total, 3), "vo_total": round(d2, 3),
          "vo_end": round(vo_end, 3), "source": VO_SRC.name,
          "scenes": scenes, "subs": subs}
    (HERE / "vo_timeline.json").write_text(
        json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")

    print(json.dumps({"ok": True, "total": tl["total"], "vo_end": tl["vo_end"],
                      "scenes": len(scenes), "subs": len(subs)},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
