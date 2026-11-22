# EP01 · 如何在国内稳定使用 Claude（CodeDeck）

成片：`out/final.mp4` — **97.47s** / 1920×1080 / 30fps / AAC 192k，**−14.2 LUFS，真峰值 −2.4 dBFS**（v2 画面 + 放慢旁白）

配音：`cosy_v2`（`cosyvoice-v3.5-plus` / `voice_id: cosyvoice-v3.5-plus-dshv2-de51050804324850ad05118b2b3cde4d`）
旁白：`audio/clone/*.wav` 逐镜生成（`audio/make_vo.py`，音色 `qwen_v2_24`，rate 1.36，5.28 字/秒），拼接为 `vo_clone.wav` → 降噪 `vo_clean.wav`

## 三种改法，选一条走

### A. 只换旁白（已有 `vo_v2_matched_91s78.wav`，不重新合成）★ 当前成片用的就是这条

```bash
cd /Volumes/文件/自媒体/视频制作/claude-codedeck-ep01
PY=/Volumes/environment/Python/anaconda3/bin/python3

$PY audio/use_v2_vo.py     # marks → vo_timeline.json；轻度降噪并补偿 anlmdn 群延迟
$PY audio/synth_mix.py     # 配乐/音效跟随新 marks 重排（BGM 设计不变）
$PY audio/master.py        # → −14 LUFS / TP ≤ −1.5（已补偿 alimiter 5ms lookahead）
$PY build_html.py          # 字幕、镜头、定版卡按新 marks 重排
$PY /Volumes/文件/自媒体/.agents/skills/code-video-studio/scripts/render.py \
   index.html out/final.mp4 --size 1920x1080 --fps 30 --duration 97.483 --audio audio/mix_norm.wav
```

> 旁白时长与 `marks.total` 必须一致（±0.05s），脚本会先校验再动手。

### B. 改文案重新合成

```bash
export DASHSCOPE_API_KEY=sk-xxx          # 只放环境变量，不落盘
cd /Volumes/文件/自媒体/视频制作/claude-codedeck-ep01
PY=/Volumes/environment/Python/anaconda3/bin/python3

# 1. 改 audio/vo_lines.json 里的 6 段文案
$PY audio/make_vo.py --rate 1.36 --gap 0.28 --tail 2.6   # qwen_v2_24, 5.3 字/秒, 出 marks
$PY audio/synth_mix.py
$PY audio/master.py
$PY build_html.py

# 2. 渲全片（时长以 vo_timeline.json 的 total 为准）
DUR=$($PY -c "import json;print(json.load(open('audio/vo_timeline.json'))['total'])")
$PY /Volumes/文件/自媒体/.agents/skills/code-video-studio/scripts/render.py \
   index.html out/final.mp4 --size 1920x1080 --fps 30 --duration $DUR --audio audio/mix_norm.wav
```

### C. 只改音轨、画面不动

```bash
ffmpeg -y -i out/final.mp4 -i audio/mix_norm.wav \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest out/final_tmp.mp4 \
  && mv out/final_tmp.mp4 out/final.mp4
```

## 目录

| 路径 | 说明 |
|---|---|
| `source/` | 原始稿件、真实素材图、成品图 |
| `audio/vo_lines.json` | 6 镜文案（唯一文字源） |
| `audio/final/vo_v2_matched_91s78.wav` | ★ 当前旁白（cosy_v2，91.78s） |
| `audio/final/vo_marks_v2_91s78.json` | ★ 当前 marks（6 镜，total 91.78，末句 end 88.07） |
| `audio/use_v2_vo.py` | 把现成旁白接入时间轴：校验时长、降噪、补偿群延迟、桥接字幕间隙 |
| `audio/make_vo.py` | 改文案时调 `音频训练/tts.py`，出 `clone/*.wav` + `vo_clone.wav` + `vo_timeline.json` |
| `audio/synth_mix.py` | 120 BPM 代码配乐 + 音效，全部按 marks 定位；`--stems` 导分层 |
| `audio/master.py` | 母带：线性增益 + lookahead 限制器到 −14 LUFS，不压动态；已补偿限制器 5ms 延迟 |
| `audio/vo_timeline.json` | `{total, vo_end, scenes[], subs[]}`，画面/字幕/音效全读它 |
| `audio/stem_*.wav` | 人声/配乐/音效分层，排查噪音用 |
| `build_html.py` | 把 timeline 注入 index.html（SCN / SUBS / DURATION）；定版卡落点 = `vo_end + 0.15` |
| `index.html` | 单文件离线渲染页，暴露 `window.render(t)` |
| `qa/` | 抽帧拼图、360px 手机图、波形/频谱、A/B 样本 |
| `HANDOFF.md` | 交给别的 AI 接手用的完整提示词 |

预览：浏览器打开 `index.html?play=1` 可实时播放。

## 几个不能再踩的坑

1. **音频问题不要靠后处理硬抹**：上一版嘶声的根因是参考录音信噪比只有 24 dB，克隆把噪声学进了音色。换音色 / 重克隆才是解法，本版已换成 `cosy_v2`。
2. **IIR 滤波器与限制器都有延迟**：`anlmdn` 约 7.92ms、`alimiter` 5ms，脚本里都已补偿，改参数时记得同步改补偿。
3. **字幕不要严格按 marks 断开**：marks 之间有 0.22s 静音，严格断开会让字幕条闪一下，`use_v2_vo.py` 已把 ≤0.3s 的间隙桥接。
4. **镜间显示**：每镜显示到「下一镜开始」，否则落在 0.22s 间隙里会回落到第 1 镜。
5. **定版卡**：`endAt = vo_end - scene6.start + 0.15`，最后一句读完才落卡，不是固定「场景结束前 6s」。
6. 全片禁止出现网址，只出现「CodeDeck」。
