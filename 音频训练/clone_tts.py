#!/usr/bin/env python3
"""
用已克隆的音色把文案批量合成音频（阿里百炼 / CosyVoice、Qwen-Audio-TTS）。

用法:
    export DASHSCOPE_API_KEY=sk-xxx          # 只从环境变量读，不落盘
    python3 clone_tts.py 文案.txt -o out/
    python3 clone_tts.py --text "一句话" --voice cosy --out out/a.wav

前置: 先用 create_voice.py 建好音色，把 voice_id 写进 voices.json。
"""
import argparse, json, os, subprocess, sys, tempfile, time, urllib.error, urllib.request

BASE = "https://dashscope.aliyuncs.com/api/v1"
HERE = os.path.dirname(os.path.abspath(__file__))
CHUNK = 400          # 单次请求最大汉字数，按句切分
SENT_END = "。！？；…\n"


def api(path, payload, timeout=180, retries=3):
    key = os.environ.get("DASHSCOPE_API_KEY")
    if not key:
        sys.exit("请先 export DASHSCOPE_API_KEY=sk-xxx")
    body = json.dumps(payload).encode()
    last = None
    for i in range(retries):
        req = urllib.request.Request(
            BASE + path, data=body,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            txt = e.read().decode(errors="replace")
            if e.code in (429, 500, 502, 503) and i < retries - 1:
                time.sleep(2 ** i)
                last = txt
                continue
            sys.exit(f"HTTP {e.code}: {txt[:500]}")
        except Exception as e:
            last = str(e)
            time.sleep(2 ** i)
    sys.exit(f"请求失败: {last}")


def split_text(text, limit=CHUNK):
    """按句子切，保证每块 <= limit 个汉字。"""
    text = text.strip()
    chunks, buf = [], ""
    for ch in text:
        buf += ch
        if ch in SENT_END and len(buf) >= limit * 0.6:
            chunks.append(buf.strip()); buf = ""
        elif len(buf) >= limit:
            cut = max(buf.rfind(c) for c in SENT_END)
            if cut < limit // 3:
                cut = len(buf) - 1
            chunks.append(buf[:cut + 1].strip()); buf = buf[cut + 1:]
    if buf.strip():
        chunks.append(buf.strip())
    return [c for c in chunks if c]


def synth(text, voice_id, model, sample_rate=24000):
    r = api("/services/audio/tts/SpeechSynthesizer", {
        "model": model,
        "input": {"text": text, "voice": voice_id,
                  "format": "wav", "sample_rate": sample_rate}})
    url = ((r.get("output") or {}).get("audio") or {}).get("url")
    if not url:
        sys.exit(f"没返回音频: {json.dumps(r, ensure_ascii=False)[:400]}")
    fd, tmp = tempfile.mkstemp(suffix=".wav"); os.close(fd)
    urllib.request.urlretrieve(url, tmp)
    return tmp, (r.get("usage") or {}).get("characters", 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script", nargs="?", help="文案 txt 文件")
    ap.add_argument("--text", help="直接给一段文字")
    ap.add_argument("--voice", default="cosy", help="voices.json 里的键")
    ap.add_argument("-o", "--out", default="out.wav")
    ap.add_argument("--gap", type=float, default=0.18, help="分段之间的停顿秒数")
    args = ap.parse_args()

    cfg = json.load(open(os.path.join(HERE, "voices.json"), encoding="utf-8"))
    if args.voice not in cfg:
        sys.exit(f"未知音色 {args.voice}，可选: {list(cfg)}")
    v = cfg[args.voice]

    if args.text:
        text = args.text
    elif args.script:
        text = open(args.script, encoding="utf-8").read()
    else:
        sys.exit("要么给文案文件，要么用 --text")

    chunks = split_text(text)
    total_chars = 0
    parts = []
    print(f"音色 {args.voice} ({v['model']}) | {len(chunks)} 段 | 共 {len(text)} 字")
    for i, c in enumerate(chunks, 1):
        p, chars = synth(c, v["voice_id"], v["model"])
        parts.append(p); total_chars += chars
        print(f"  [{i}/{len(chunks)}] {len(c)}字 -> {os.path.getsize(p)/1024:.0f}KB  计费{chars}字符")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    if len(parts) == 1:
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-i", parts[0], "-c:a", "pcm_s16le", args.out], check=True)
    else:
        sil = tempfile.mktemp(suffix=".wav")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono",
                        "-t", str(args.gap), "-c:a", "pcm_s16le", sil], check=True)
        with open(os.path.join(tempfile.mkdtemp(), "list.txt"), "w") as f:
            pass
        inputs = []
        for p in parts:
            inputs += ["-i", p]
        inputs += ["-i", sil]
        n = len(parts)
        stream = "".join(f"[{i}:a]" for i in range(n))
        filt = stream + f"[{n}:a]" * (n - 1) + f"concat=n={2*n-1}:v=0:a=1[out]"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs,
                        "-filter_complex", filt, "-map", "[out]",
                        "-c:a", "pcm_s16le", args.out], check=True)

    for p in parts:
        os.remove(p)
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", args.out],
                         capture_output=True, text=True).stdout.strip()
    print(f"\n完成: {args.out}  {float(dur):.2f}s  计费合计 {total_chars} 字符 "
          f"(约 {total_chars/10000:.4f} 元按 1 元/万字符 估)")


if __name__ == "__main__":
    main()
