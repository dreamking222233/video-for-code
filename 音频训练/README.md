# 声音克隆 · 已建音色与用法

> 参考音频：`cosy_v2` 用 `processed/ref_v2_bailian_17s.wav`（新录音，SNR 39.2 dB）
> `cosy_plus`/`cosy_flash`/`qwen_plus` 用 `processed/ref_bailian_17s.wav`（旧录音，SNR 21.0 dB）
> 创建时间：2026-11-21

## 已建好的音色

| 键 | 模型 | voice_id | 档位 |
|---|---|---|---|
| `cosy_v2` | cosyvoice-v3.5-plus | `cosyvoice-v3.5-plus-dshv2-de51050804324850ad05118b2b3cde4d` | **生产用**，干净参考训练 |
| `cosy_plus` | cosyvoice-v3.5-plus | `cosyvoice-v3.5-plus-dshcp-e71a2c12219a4d389b6c1abcb8f71837` | 旧版，参考带嘶声 |
| `qwen_plus` | qwen-audio-3.1-tts-plus | `qwen-audio-3.1-tts-plus-dshqwen-3447f83037734fa4904f09cb3faee0ea` | 顶配，内容创作向 |
| `cosy_flash` | cosyvoice-v3.5-flash | `cosyvoice-v3.5-flash-dshvoice-bd4d6c58c2ca4dee97491e938400ba2e` | 廉价档，0.8 元/万字符 |

音色绑定 `target_model`，不能跨模型复用；每个账号上限 1000 个音色；创建免费。

## 客观指标（vs 你的原始录音）

| 模型 | F0 中位 | 频谱包络相关 | 说明 |
|---|---|---|---|
| 参考 | 101.1 Hz | 1.000 | — |
| cosyvoice-v3.5-plus | 99.2 Hz | **0.9787** | 音色最接近 |
| qwen-audio-3.1-tts-plus | 100.0 Hz | 0.9617 | 略偏亮；返回音频峰值 +0.3 dBTP，需压限 |

结论：**cosyvoice-v3.5-plus 胜出**，作为默认生产模型。

## 重新生成

```bash
export DASHSCOPE_API_KEY=sk-xxx          # 只从环境变量读，不写盘

# 自然语速
python3 make_vo.py --voice cosy_plus --lines lines.json --outdir ../视频制作/xxx/audio/new

# 原生变速（口播赶一点，rate 0.5~2 实测生效）
python3 make_vo.py --voice cosy_plus --lines lines.json --outdir out --rate 1.38

# 重建音色（换参考音频时）
python3 make_vo.py --voice cosy_plus --lines lines.json --outdir out --create-voice
```

`lines.json` 格式：`[{"id":"s1","text":"..."}, ...]`，逐句合成并输出 `vo_marks.json` 时间轴。

## 本次产出（`视频制作/claude-codedeck-ep01/audio/final/`）

| 文件 | 时长 | 用途 |
|---|---|---|
| `vo_clone_matched_91s78.wav` | 91.78 s | **首选**，直接替换 `vo_48k.wav` |
| `vo_clone_92s_tight.wav` | 89.47 s | 同上，未补尾静音 |
| `vo_clone_92s.wav` | 92.42 s | 句间隔 0.35s 的原始拼接版 |
| `vo_clone_natural.wav` | 126.87 s | 自然语速，适合重新卡点 |
| `vo_qwen_natural.wav` | 128.79 s | 对照组 |

全部：48 kHz / 单声道 / 16-bit / **−18 LUFS / 真峰值 −1.5 dBFS**（VO stem 电平，混音后再统一 −14 LUFS）。
逐句文件在 `clone_cosy_r138/`、`clone_cosy/`、`clone_qwen/`，时间轴在同目录 `vo_marks*.json`。

## 成本

本次共消耗约 **4500 字符**（cosy_plus ≈3260 / qwen_plus ≈1140 / cosy_flash ≈110），
三个模型各有 1 万字符免费额度（90 天），**实际花费 0 元**。
超出后按 1.5 元 / 1.4 元 / 0.8 元每万字符计（阿里计费：1 个汉字 = 2 字符）。

## 注意

- 这次用于测试的 API Key 已在聊天中出现，**建议到百炼控制台作废重发**。
- 音色是绑定账号的资产，`voices.json` 里只有 voice_id，没有密钥，可以安全分享。
- 阿里侧音色不会过期，但请勿删除——删了要重新建。
