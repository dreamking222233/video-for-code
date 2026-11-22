#!/usr/bin/env python3
"""
一条命令完成「新录音 -> 参考音频 -> 建音色 -> 写回 voices.json」。

    export DASHSCOPE_API_KEY=sk-xxx
    python3 train_voice.py 新录音.m4a --key cosy_v2
    python3 train_voice.py 新录音.m4a --key cosy_v2 --model cosyvoice-v3.5-plus --tag v2

流程：
  1. prepare_ref.py 解码 + 按语音密度选窗 + 归一（只做不伤音色的处理）
  2. voice-enrollment 上传参考音频建音色（免费）
  3. 轮询到 OK，把 voice_id / ref / model 写进 voices.json

退出码：0 成功 / 2 参数或环境错误 / 3 API 错误 / 4 音频处理错误
"""
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://dashscope.aliyuncs.com/api/v1"
sys.path.insert(0, HERE)


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def die(c, m):
    log(f"ERROR {m}"); sys.exit(c)


def api(path, payload, key, timeout=300, retries=3):
    import urllib.error, urllib.request
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", help="新录音（m4a/wav/mp3 均可）")
    ap.add_argument("--key", required=True, help="voices.json 里的键，如 cosy_v2")
    ap.add_argument("--model", default="cosyvoice-v3.5-plus",
                    choices=["cosyvoice-v3.5-plus", "cosyvoice-v3.5-flash",
                             "qwen-audio-3.1-tts-plus"])
    ap.add_argument("--prefix", default="dsh", help="音色名前缀，<=10 字符")
    ap.add_argument("--tag", default="", help="参考音频文件名后缀")
    ap.add_argument("--ref", help="跳过整理，直接用这个已处理好的 wav")
    ap.add_argument("--price", type=float, default=1.5)
    ap.add_argument("--no-train", action="store_true", help="只整理参考音频，不建音色")
    a = ap.parse_args()

    key = os.environ.get("DASHSCOPE_API_KEY")
    if not key:
        die(2, "缺少环境变量 DASHSCOPE_API_KEY")
    if len(a.prefix) > 10:
        die(2, "prefix 不能超过 10 个字符")

    # 1) 参考音频
    if a.ref:
        ref = a.ref
        if not os.path.exists(ref):
            die(2, f"参考音频不存在: {ref}")
        log(f"[1/3] 使用现成参考音频 {ref}")
    else:
        log(f"[1/3] 整理录音 {a.audio}")
        cmd = [sys.executable, os.path.join(HERE, "prepare_ref.py"), a.audio,
               "-o", os.path.join(HERE, "processed"), "--json-out", "/tmp/_ref.json"]
        if a.tag:
            cmd += ["--tag", a.tag]
        if subprocess.run(cmd).returncode != 0:
            die(4, "prepare_ref.py 执行失败")
        rep = json.load(open("/tmp/_ref.json", encoding="utf-8"))
        if "bailian" not in rep:
            die(4, f"录音太短，没有可用的参考窗口: {list(rep)}")
        ref = os.path.join(HERE, "processed", rep["bailian"]["file"])
        log(f"      参考音频 {ref}  {rep['bailian']['duration']}s  "
            f"语音密度 {rep['bailian']['density']}%  {rep['bailian']['lufs']} LUFS")

    if a.no_train:
        log(f"完成（未训练）。参考音频: {ref}")
        return

    # 2) 建音色
    import base64
    log(f"[2/3] 建音色 model={a.model} prefix={a.prefix}")
    raw = base64.b64encode(open(ref, "rb").read()).decode()
    r = api("/services/audio/tts/customization", {
        "model": "voice-enrollment",
        "input": {"action": "create_voice", "target_model": a.model,
                  "prefix": a.prefix, "audio": "data:audio/wav;base64," + raw}}, key)
    vid = (r.get("output") or {}).get("voice_id")
    if not vid:
        die(3, f"建音色失败: {json.dumps(r, ensure_ascii=False)[:400]}")

    # 3) 等部署
    for i in range(60):
        q = api("/services/audio/tts/customization", {
            "model": "voice-enrollment",
            "input": {"action": "query_voice", "voice_id": vid}}, key)
        st = (q.get("output") or {}).get("status")
        if st == "OK":
            break
        if st not in (None, "DEPLOYING"):
            die(3, f"音色状态异常 {st}")
        time.sleep(1)
    else:
        die(3, "音色部署超时")

    # 4) 写回配置
    vpath = os.path.join(HERE, "voices.json")
    voices = json.load(open(vpath, encoding="utf-8")) if os.path.exists(vpath) else {}
    voices[a.key] = {"model": a.model, "voice_id": vid, "prefix": a.prefix,
                     "sample_rate": 24000, "price": a.price,
                     "ref": os.path.abspath(ref),
                     "created": time.strftime("%Y-%m-%d %H:%M")}
    json.dump(voices, open(vpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    log(f"[3/3] 已写入 voices.json 的 {a.key}")
    print(json.dumps({"ok": True, "key": a.key, "voice_id": vid, "model": a.model,
                      "ref": os.path.abspath(ref), "voices_json": vpath},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
