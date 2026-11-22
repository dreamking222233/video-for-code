#!/usr/bin/env python3
"""
把文本合成为「已克隆的专属音色」音频。供其它 Agent / 流水线调用。

    export DASHSCOPE_API_KEY=sk-xxx
    python3 tts.py --text-file 文案.txt --out vo.wav
    python3 tts.py --text "一句话" --out a.wav --rate 1.3 --lufs -18
    python3 tts.py --text-file 文案.txt --out vo.wav --json

成功时 stdout 只输出 JSON（--json 时）或一行摘要；日志走 stderr。
退出码：0 成功 / 2 参数或环境错误 / 3 API 错误 / 4 音频处理错误
"""
import argparse, json, os, re, subprocess, sys, tempfile, time
import urllib.error, urllib.request

BASE = "https://dashscope.aliyuncs.com/api/v1"
HERE = os.path.dirname(os.path.abspath(__file__))
MAX_CHARS = 340          # 单次请求汉字上限（阿里按 1 汉字=2 字符计费）
SENT_END = "。！？；…!?;\n"


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def die(code, msg):
    log(f"ERROR {msg}")
    sys.exit(code)


def api(path, payload, timeout=240, retries=3):
    key = os.environ.get("DASHSCOPE_API_KEY")
    if not key:
        die(2, "缺少环境变量 DASHSCOPE_API_KEY")
    body = json.dumps(payload).encode()
    last = ""
    for i in range(retries):
        req = urllib.request.Request(
            BASE + path, data=body, method="POST",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            txt = e.read().decode(errors="replace")[:400]
            if e.code in (429, 500, 502, 503) and i < retries - 1:
                last = f"HTTP {e.code} {txt}"; time.sleep(2 ** i); continue
            die(3, f"HTTP {e.code}: {txt}")
        except Exception as e:
            last = str(e); time.sleep(2 ** i)
    die(3, f"请求失败: {last}")


def split_sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    out, buf = [], ""
    for ch in text:
        buf += ch
        if ch in SENT_END:
            out.append(buf.strip()); buf = ""
    if buf.strip():
        out.append(buf.strip())
    return [x for x in out if x]


def split_text(text, limit=MAX_CHARS):
    """按句子贪心切块，保证每块 <= limit 汉字，不切断句子。"""
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return [text]
    sents, buf = [], ""
    for ch in text:
        buf += ch
        if ch in SENT_END:
            sents.append(buf); buf = ""
    if buf.strip():
        sents.append(buf)
    chunks, cur = [], ""
    for s in sents:
        while len(s) > limit:              # 超长单句强制切
            chunks.append(cur + s[:limit]); s = s[limit:]; cur = ""
        if len(cur) + len(s) <= limit:
            cur += s
        else:
            chunks.append(cur); cur = s
    if cur.strip():
        chunks.append(cur)
    return [c.strip() for c in chunks if c.strip()]


def synth(chunk, voice_id, model, sr, rate):
    inp = {"text": chunk, "voice": voice_id, "format": "wav", "sample_rate": sr}
    if abs(rate - 1.0) > 1e-6:
        inp["rate"] = rate
    r = api("/services/audio/tts/SpeechSynthesizer", {"model": model, "input": inp})
    url = ((r.get("output") or {}).get("audio") or {}).get("url")
    if not url:
        die(3, f"无音频返回: {json.dumps(r, ensure_ascii=False)[:300]}")
    fd, tmp = tempfile.mkstemp(suffix=".wav"); os.close(fd)
    urllib.request.urlretrieve(url, tmp)   # 签名 URL 会过期，必须立即下载
    return tmp, (r.get("usage") or {}).get("characters", 0)


def dur(p):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", p], capture_output=True, text=True).stdout.strip() or 0)


def join(parts, gap, sr, out):
    if len(parts) == 1:
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-i", parts[0], "-ar", str(sr), "-ac", "1",
                        "-c:a", "pcm_s16le", out], check=True)
        return
    d = tempfile.mkdtemp()
    sil = os.path.join(d, "s.wav")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
                    "-i", f"anullsrc=r={sr}:cl=mono", "-t", str(gap),
                    "-c:a", "pcm_s16le", sil], check=True)
    lst = os.path.join(d, "l.txt")
    with open(lst, "w") as f:
        for i, p in enumerate(parts):
            f.write(f"file '{os.path.abspath(p)}'\n")
            if i < len(parts) - 1:
                f.write(f"file '{sil}'\n")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-f", "concat", "-safe", "0", "-i", lst,
                    "-ar", str(sr), "-ac", "1", "-c:a", "pcm_s16le", out], check=True)


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--text")
    src.add_argument("--text-file")
    ap.add_argument("--out", required=True)
    ap.add_argument("--voice", default=None,
                    help="voices.json 里的键；省略则用 _default")
    ap.add_argument("--rate", type=float, default=1.0, help="语速 0.5~2，1.0 为自然语速")
    ap.add_argument("--gap", type=float, default=0.22, help="分段间停顿秒数")
    ap.add_argument("--lufs", type=float, default=-18.0,
                    help="输出响度；设 0 关闭归一化")
    ap.add_argument("--unit", choices=["chunk", "sentence"], default="chunk",
                    help="chunk=按 340 字合并（少请求）；sentence=一句一请求（要精确时间轴用这个）")
    ap.add_argument("--marks-out", help="把每段起止时间写入 JSON，供视频对时间轴")
    ap.add_argument("--json", action="store_true", help="stdout 输出 JSON")
    a = ap.parse_args()

    cfg_path = os.path.join(HERE, "voices.json")
    if not os.path.exists(cfg_path):
        die(2, f"找不到 {cfg_path}")
    voices = json.load(open(cfg_path, encoding="utf-8"))
    if a.voice is None:
        a.voice = voices.get("_default", "cosy_v2")
    if a.voice not in voices:
        die(2, f"未知音色 {a.voice}，可选: {list(voices)}")
    v = voices[a.voice]
    if not v.get("voice_id"):
        die(2, f"{a.voice} 还没有 voice_id，先用 --create-voice 建音色")

    text = a.text if a.text is not None else open(a.text_file, encoding="utf-8").read()
    if not text.strip():
        die(2, "文本为空")

    sr = v.get("sample_rate", 24000)
    chunks = split_sentences(text) if a.unit == "sentence" else split_text(text)
    log(f"音色 {a.voice} / {v['model']} | {len(text)} 字 -> {len(chunks)} 段 | rate={a.rate} sr={sr}")

    parts, chars, marks, t = [], 0, [], 0.0
    for i, c in enumerate(chunks, 1):
        p, n = synth(c, v["voice_id"], v["model"], sr, a.rate)
        d = dur(p)
        parts.append(p); chars += n
        marks.append({"i": i, "text": c, "start": round(t, 2),
                      "end": round(t + d, 2), "dur": round(d, 2)})
        t += d + (a.gap if i < len(chunks) else 0)
        log(f"  [{i}/{len(chunks)}] {len(c)}字 {d:6.2f}s 计费{n}字符")

    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    stage = tempfile.mktemp(suffix=".wav")
    try:
        join(parts, a.gap, sr, stage)
        if a.lufs and a.lufs != 0:
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", stage,
                            "-af", f"loudnorm=I={a.lufs}:TP=-1.5:LRA=11,"
                                   f"aresample=48000:osf=s16:dither_method=triangular",
                            "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", a.out], check=True)
        else:
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", stage,
                            "-c:a", "pcm_s16le", a.out], check=True)
    except subprocess.CalledProcessError as e:
        die(4, f"ffmpeg 处理失败: {e}")
    finally:
        for p in parts + [stage]:
            if os.path.exists(p):
                os.remove(p)

    total = dur(a.out)
    if a.marks_out:
        json.dump({"voice": a.voice, "model": v["model"], "rate": a.rate,
                   "gap": a.gap, "total": round(total, 2), "marks": marks},
                  open(a.marks_out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        log(f"时间轴 -> {a.marks_out}")
    result = {"ok": True, "out": os.path.abspath(a.out), "voice": a.voice,
              "model": v["model"], "duration_s": round(total, 2),
              "chars_billed": chars, "est_cost_cny": round(chars / 10000 * v.get("price", 1.5), 4),
              "sample_rate": 48000 if a.lufs else sr,
              "characters_per_sec": round(len(text) / total, 2) if total else None,
              "segments": len(chunks), "marks": os.path.abspath(a.marks_out) if a.marks_out else None}
    if a.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        log(f"DONE {a.out} {total:.2f}s 计费{chars}字符")


if __name__ == "__main__":
    main()
