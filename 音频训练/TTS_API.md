# 专属音色 TTS 调用契约

给视频制作流程 / 其它 Agent 用。**目标：输入文本，输出你本人音色的配音 wav。**

音色已建好，无需再训练。目录：`音频训练/`

---

## 0. 前置：只要一个环境变量

```bash
export DASHSCOPE_API_KEY=sk-xxx
```

- 不要写进代码、不要提交进仓库。
- 阿里云百炼控制台 → API-KEY 管理里取。
- 本文档不含任何密钥。

---

## 1. 最简调用（推荐）

```bash
cd 音频训练

# 整段配音：自动分段、拼接、归一化
python3 tts.py --text-file 文案.txt --out /path/vo.wav --rate 1.38 --json

# 逐句配音 + 时间轴（视频对动画用这个）
python3 tts.py --text-file 文案.txt --out /path/vo.wav \
        --unit sentence --marks-out /path/vo_marks.json --json
```

成功时 stdout 只有一行 JSON：

```json
{"ok": true, "out": "/abs/path/vo.wav", "voice": "cosy_plus",
 "model": "cosyvoice-v3.5-plus", "duration_s": 88.68, "chars_billed": 1029,
 "est_cost_cny": 0.1544, "sample_rate": 48000, "characters_per_sec": 6.65,
 "segments": 2, "marks": null}
```

日志走 stderr，**stdout 只有 JSON**，可直接 `| jq`。

### 参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `--text` / `--text-file` | 必填 | 二选一 |
| `--out` | 必填 | 输出 wav 路径，父目录会自动建 |
| `--voice` | `cosy_plus` | 见下方音色表 |
| `--rate` | `1.0` | 语速 0.5~2。1.0 自然（≈4.6 字/秒），1.38 ≈6.6 字/秒 |
| `--unit` | `chunk` | `chunk` 按 340 字合并少请求；`sentence` 一句一请求、出精确时间轴 |
| `--gap` | `0.22` | 分段之间插入的静音秒数 |
| `--lufs` | `-18` | 输出响度；设 `0` 关闭归一化（保留原始电平） |
| `--marks-out` | 无 | 时间轴 JSON 路径 |
| `--json` | 关 | stdout 输出 JSON |

### 退出码

`0` 成功 / `2` 参数或环境错误（含缺 Key）/ `3` API 错误 / `4` ffmpeg 处理失败

---

## 2. 直接用 HTTP（不想跑本地脚本时）

```
POST https://dashscope.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer
Authorization: Bearer $DASHSCOPE_API_KEY
Content-Type: application/json

{
  "model": "cosyvoice-v3.5-plus",
  "input": {
    "text": "要合成的文字",
    "voice": "cosyvoice-v3.5-plus-dshcp-e71a2c12219a4d389b6c1abcb8f71837",
    "format": "wav",
    "sample_rate": 24000,
    "rate": 1.38
  }
}
```

返回：

```json
{"output": {"audio": {"url": "http://dashscope-result-bj.oss-...wav?Expires=...&Signature=...",
                      "expires_at": 1795301905, "id": "audio_xxx"},
            "finish_reason": "stop"},
 "usage": {"characters": 109},
 "request_id": "..."}
```

**`output.audio.url` 是带签名的临时地址，会过期，必须立刻下载。**
`usage.characters` 是本次计费字符数。

### 最小 Python 实现

```python
import json, os, urllib.request, urllib.error

def tts(text, out, voice_id="cosyvoice-v3.5-plus-dshcp-e71a2c12219a4d389b6c1abcb8f71837",
        model="cosyvoice-v3.5-plus", rate=1.0):
    payload = {"model": model,
               "input": {"text": text, "voice": voice_id,
                         "format": "wav", "sample_rate": 24000, "rate": rate}}
    req = urllib.request.Request(
        "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer",
        data=json.dumps(payload).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['DASHSCOPE_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.loads(r.read())
    urllib.request.urlretrieve(d["output"]["audio"]["url"], out)
    return d["usage"]["characters"]
```

---

## 3. 音色表（`voices.json`）

| 键 | 模型 | voice_id |
|---|---|---|
| `cosy_plus` | cosyvoice-v3.5-plus | `cosyvoice-v3.5-plus-dshcp-e71a2c12219a4d389b6c1abcb8f71837` |
| `qwen_plus` | qwen-audio-3.1-tts-plus | `qwen-audio-3.1-tts-plus-dshqwen-3447f83037734fa4904f09cb3faee0ea` |
| `cosy_flash` | cosyvoice-v3.5-flash | `cosyvoice-v3.5-flash-dshvoice-bd4d6c58c2ca4dee97491e938400ba2e` |

**默认用 `cosy_plus`**：实测频谱包络相关 0.9787（最高），F0 偏差 1.2%。

`qwen_plus` 的 API 返回真峰值达 +0.3 dBTP，用它必须做压限，否则削波。

---

## 4. 计费

- 阿里按**输入字符**计费，输出音频不计费。
- **1 个汉字 = 2 个字符**；标点、字母、数字、空格各算 1 个。
- 单价：cosy_plus 1.5 元/万字符 ≈ **3 元/万汉字**；qwen_plus 1.4；cosy_flash 0.8。
- 每个模型有 1 万字符免费额度（开通后 90 天）。
- 换算：590 汉字文案 ≈ 1029 字符 ≈ 0.15 元。

---

## 5. 硬约束（踩了会报错）

| 约束 | 说明 |
|---|---|
| 音色绑模型 | 每个 voice_id 只能配它创建时的 `model`，换模型必须重建音色 |
| 文本长度 | 单请求别超 ~340 汉字，长文用 `tts.py` 自动分段 |
| 签名 URL | 几小时内过期，拿到就下载 |
| 音色别删 | 删了要重新建（免费，但 voice_id 会变，需更新 `voices.json`） |
| 音色数量 | 单账号上限 1000 个 |

### 常见错误

| 报错 | 原因 |
|---|---|
| `401 invalid_api_key` | Key 错 / 没设环境变量 |
| `BadRequest.ResourceNotExist` | voice_id 不存在或与 model 不匹配 |
| `InvalidParameter: ... longer than` | 文本过长，分段 |
| `Throttling` | 触发 180 RPM 限流，脚本已内置重试 |

---

## 6. 给视频流水线的建议

1. **时长要和已有剪辑对齐**时，先算目标：`rate ≈ 自然时长 / 目标时长`。
   本项目实测：自然 126.87s，`rate=1.38` → 92.42s，裁掉句尾静音并补尾 → **91.78s**。
2. **要精准对动画**就加 `--unit sentence --marks-out`，用 marks 里的 `start/end` 逐句触发。
3. 输出默认 **−18 LUFS / 真峰值 −1.5 dBFS**，是混音用的 stem 电平；
   最终成片再统一到 −14 LUFS（和现有 `mix_norm.wav` 一致）。
4. 换文案后时间轴必然变，字幕/动画要按新 `marks` 重排，别复用旧时间。

---

## 7. 相关文件

| 文件 | 用途 |
|---|---|
| `tts.py` | 主入口，上文的 CLI |
| `voices.json` | 音色 ID 与价格（**无密钥**，可共享） |
| `make_vo.py` | 旧版：读 `lines.json` 按句生成，保留兼容 |
| `lines.json` | 本项目 6 句旁白文本 |
| `README.md` | 音色建立记录与本次产出清单 |
