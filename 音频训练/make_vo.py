#!/usr/bin/env python3
"""
用克隆音色合成整段旁白：逐句合成 -> 按停顿拼接 -> 输出 wav + 时间轴。

用法:
    export DASHSCOPE_API_KEY=sk-xxx
    python3 make_vo.py --voice qwen_plus --lines lines.json --outdir out/

lines.json: [{"id":"s1","text":"..."}, ...]
"""
import argparse, json, os, subprocess, sys, tempfile, time, urllib.error, urllib.request

BASE = "https://dashscope.aliyuncs.com/api/v1"
HERE = os.path.dirname(os.path.abspath(__file__))


def key():
    k = os.environ.get("DASHSCOPE_API_KEY")
    if not k:
        sys.exit("请先 export DASHSCOPE_API_KEY=sk-xxx")
    return k


def api(path, payload, timeout=240, retries=3):
    body = json.dumps(payload).encode()
    last = None
    for i in range(retries):
        req = urllib.request.Request(
            BASE + path, data=body,
            headers={"Authorization": f"Bearer {key()}", "Content-Type": "application/json"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            txt = e.read().decode(errors="replace")
            if e.code in (429, 500, 502, 503) and i < retries - 1:
                last, _ = txt, time.sleep(2 ** i)
                continue
            sys.exit(f"HTTP {e.code}: {txt[:400]}")
        except Exception as e:
            last = str(e); time.sleep(2 ** i)
    sys.exit(f"请求失败: {last}")


def create_voice(model, ref_wav, prefix):
    import base64
    raw = base64.b64encode(open(ref_wav, "rb").read()).decode()
    r = api("/services/audio/tts/customization", {
        "model": "voice-enrollment",
        "input": {"action": "create_voice", "target_model": model,
                  "prefix": prefix, "audio": "data:audio/wav;base64," + raw}})
    vid = (r.get("output") or {}).get("voice_id")
    if not vid:
        sys.exit(f"建音色失败: {json.dumps(r, ensure_ascii=False)[:400]}")
    for i in range(60):
        q = api("/services/audio/tts/customization", {
            "model": "voice-enrollment", "input": {"action": "query_voice", "voice_id": vid}})
        st = (q.get("output") or {}).get("status")
        if st == "OK":
            return vid
        if st not in (None, "DEPLOYING"):
            sys.exit(f"音色状态异常 {st}: {json.dumps(q, ensure_ascii=False)[:300]}")
        time.sleep(1)
    sys.exit("音色部署超时")


def synth(text, vid, model, sr, rate=1.0):
    inp = {"text": text, "voice": vid, "format": "wav", "sample_rate": sr}
    if abs(rate - 1.0) > 1e-6:
        inp["rate"] = rate
    r = api("/services/audio/tts/SpeechSynthesizer", {"model": model, "input": inp})
    url = ((r.get("output") or {}).get("audio") or {}).get("url")
    if not url:
        sys.exit(f"合成失败: {json.dumps(r, ensure_ascii=False)[:400]}")
    fd, tmp = tempfile.mkstemp(suffix=".wav"); os.close(fd)
    urllib.request.urlretrieve(url, tmp)
    return tmp, (r.get("usage") or {}).get("characters", 0)


def dur_of(p):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", p], capture_output=True, text=True).stdout.strip())


def concat(parts, gap, sr, out):
    """parts 之间插入 gap 秒静音，用 concat demuxer 拼接。"""
    tmpd = tempfile.mkdtemp()
    parts = [os.path.abspath(x) for x in parts]
    out = os.path.abspath(out)
    sil = os.path.join(tmpd, "sil.wav")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-f", "lavfi", "-i", f"anullsrc=r={sr}:cl=mono",
                    "-t", f"{gap}", "-c:a", "pcm_s16le", sil], check=True)
    lst = os.path.join(tmpd, "list.txt")
    with open(lst, "w") as f:
        for i, p in enumerate(parts):
            f.write(f"file '{p}'\n")
            if i < len(parts) - 1:
                f.write(f"file '{sil}'\n")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-f", "concat", "-safe", "0", "-i", lst,
                    "-ar", str(sr), "-ac", "1", "-c:a", "pcm_s16le", out], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", required=True, help="voices.json 的键")
    ap.add_argument("--lines", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--gap", type=float, default=0.35)
    ap.add_argument("--create-voice", action="store_true", help="先建音色并写回 voices.json")
    ap.add_argument("--tag", default="", help="输出文件后缀")
    ap.add_argument("--rate", type=float, default=1.0, help="原生语速倍率 0.5~2")
    ap.add_argument("--reuse", action="store_true", help="复用已存在的分段文件，不重新合成")
    a = ap.parse_args()

    vpath = os.path.join(HERE, "voices.json")
    voices = json.load(open(vpath, encoding="utf-8")) if os.path.exists(vpath) else {}
    if a.voice not in voices:
        sys.exit(f"未知音色 {a.voice}；已有 {list(voices)}")
    v = voices[a.voice]
    os.makedirs(a.outdir, exist_ok=True)

    if a.create_voice:
        print(f"[建音色] {a.voice} / {v['model']}")
        v["voice_id"] = create_voice(v["model"], v["ref"], v["prefix"])
        json.dump(voices, open(vpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("  voice_id =", v["voice_id"])

    lines = json.load(open(a.lines, encoding="utf-8"))
    sr = v.get("sample_rate", 24000)
    parts, marks, total = [], [], 0.0
    print(f"[合成] {a.voice} ({v['model']}) | {len(lines)} 句 | {sr}Hz")
    for i, ln in enumerate(lines, 1):
        exist = os.path.join(a.outdir, f"{ln['id']}{a.tag}.wav")
        if a.reuse and os.path.exists(exist):
            d = dur_of(exist); chars = 0
            parts.append(exist)
            marks.append({"id": ln["id"], "text": ln["text"],
                          "start": round(total, 3), "end": round(total + d, 3), "dur": round(d, 3)})
            total += d + (a.gap if i < len(lines) else 0)
            print(f"  [{i}/{len(lines)}] {ln['id']:14s} {d:6.2f}s  复用")
            continue
        p, chars = synth(ln["text"], v["voice_id"], v["model"], sr, a.rate)
        d = dur_of(p)
        dst = os.path.join(a.outdir, f"{ln['id']}{a.tag}.wav")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-i", p, "-ar", str(sr), "-ac", "1", "-c:a", "pcm_s16le", dst], check=True)
        os.remove(p); parts.append(dst)
        marks.append({"id": ln["id"], "text": ln["text"],
                      "start": round(total, 3), "end": round(total + d, 3), "dur": round(d, 3)})
        total += d + (a.gap if i < len(lines) else 0)
        print(f"  [{i}/{len(lines)}] {ln['id']:14s} {d:6.2f}s  计费{chars}字符")

    final = os.path.join(a.outdir, f"vo_full{a.tag}.wav")
    concat(parts, a.gap, sr, final)
    json.dump({"voice": a.voice, "model": v["model"], "sample_rate": sr,
               "gap": a.gap, "total": round(dur_of(final), 3), "marks": marks},
              open(os.path.join(a.outdir, f"vo_marks{a.tag}.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"\n输出 {final}  {dur_of(final):.2f}s  计费合计 {len(json.dumps(lines, ensure_ascii=False))} 字节文案")


if __name__ == "__main__":
    main()
