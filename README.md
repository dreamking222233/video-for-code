# 自媒体视频工程（video-for-code）

这是一个**「用代码做视频」**的自媒体工程：画面不是剪辑软件做出来的，而是 HTML/CSS/Canvas + JS 时间函数，由无头浏览器逐帧截图、FFmpeg 合成；配音由云端 TTS API 生成；配乐和音效由 numpy 从零合成。

当前已有成片：**EP01《如何在国内稳定使用 Claude》**（CodeDeck 产品向，**97.47s**，1920×1080；画面 v2 已按官网设计语言重做，旁白 qwen_v2_24 / rate 1.36 / 5.3 字每秒）。

> 本文写给「接手的人或 AI」。所有命令都可以直接复制执行。若你在另一台电脑上，请先看 §2 的路径替换说明。

---

## 1. 这个仓库里都是什么

| 目录 | 作用 |
|---|---|
| `视频制作/claude-codedeck-ep01/` | **主力项目**：EP01 成片、渲染页、配音/配乐/母带脚本、QA 抽帧 |
| `视频制作/demo-code-video/` | 早期动效 demo（学习/参考用，不是成片） |
| `视频制作/素材稿件/` | 原始稿件（第一期素材制作.md，key 已脱敏） |
| `音频训练/` | **配音产线**：TTS 封装、音色克隆、参考音频处理（详见 `音频训练/配音生成说明.md`） |
| `.agents/skills/code-video-studio/` | 技能包：方法论文档 + 4 个通用脚本（渲染/音频分析/视频分析/环境自检） |
| `醍醐测试/` | 单个 HTML 动效实验 |
| `抖音/`、`小红书/` | 空目录，预留给竖屏/方屏导出版本 |
| `out/`（在项目内） | 成片输出 |

核心思路一句话：**一个 HTML 页面暴露 `window.render(t)`，t 是秒；渲染器以 30fps 逐帧调用它并截图，最后拼成视频。**

---

## 2. 环境准备

### 2.1 依赖

| 依赖 | 说明 |
|---|---|
| Python ≥ 3.9 | 本机用的是 `/Volumes/environment/Python/anaconda3/bin/python3` |
| `numpy`, `scipy` | 合成配乐/音效、频谱分析 |
| `playwright`（Python 包） | 驱动无头 Chromium 逐帧截图 |
| Chromium | `python3 -m playwright install chromium`（或本机装 Chrome/Edge，脚本会自动回退） |
| `ffmpeg` + `ffprobe` | macOS `brew install ffmpeg`；Windows `winget install ffmpeg`；Linux `apt install ffmpeg` |
| `DASHSCOPE_API_KEY` | 只有**重新生成配音**时才需要，放环境变量，禁止写进文件/提交 |

### 2.2 一条命令自检

```bash
cd /Volumes/文件/自媒体
python3 .agents/skills/code-video-studio/scripts/check_env.py
```

全部 `[ok]` 并以 `ready` 结尾即可开工。它会检查 ffmpeg、numpy、playwright、浏览器、WebGL2、chromakey 支持。

### 2.3 换机器时改路径

所有脚本内部**只用相对路径**（`pathlib` 基于脚本自身位置），所以整个目录复制到任何位置都能跑。唯一需要改的是你自己命令里的绝对路径：

```bash
# 新机器上建议这样起手
export ROOT="/你的路径/自媒体"
export PY="python3"                 # 或你本机的解释器绝对路径
cd "$ROOT"
```

> 文中出现的 `/Volumes/文件/自媒体` 与 `/Volumes/environment/Python/anaconda3/bin/python3` 都只是本机示例。

---

## 3. 30 秒验证渲染链路

先不碰音频，确认浏览器渲染能跑通：

```bash
cd "$ROOT/视频制作/claude-codedeck-ep01"

# 出一张静帧（第 30 秒）
$PY "$ROOT/.agents/skills/code-video-studio/scripts/render.py" \
   index.html /tmp/shot30.png --still 30 --size 1920x1080

# 出一小段视频（0-6 秒，无声）
$PY "$ROOT/.agents/skills/code-video-studio/scripts/render.py" \
   index.html /tmp/clip.mp4 --size 1920x1080 --fps 30 --duration 6
```

看到 PNG / MP4 就说明工具链是通的。

**实时预览**：浏览器打开 `视频制作/claude-codedeck-ep01/index.html?play=1`，会按真实时间播放。

### `render.py` 参数速查

| 参数 | 作用 |
|---|---|
| `page` | 要渲染的 HTML（可带 query，如 `"page.html?raw=1"`） |
| `out` | 输出 `.mp4` 或 `.png` |
| `--size WxH` | 画布尺寸，默认 `1920x1080` |
| `--fps` | 帧率，默认 30 |
| `--duration` | 渲染秒数（视频模式） |
| `--start` | 从第几秒开始（可分段渲染） |
| `--still` | 只渲染这一秒的单帧 PNG |
| `--subframes` | 每帧多次采样做运动模糊 |
| `--audio` | 混入的音轨（自动裁剪到视频长度） |
| `--crf` | x264 质量，默认 16 |

---

## 4. 出片全流程（EP01）

```bash
export ROOT="/Volumes/文件/自媒体"
export PY="/Volumes/environment/Python/anaconda3/bin/python3"
cd "$ROOT/视频制作/claude-codedeck-ep01"
```

### 4.1 情形 A：只换旁白（已有现成 wav + marks）★ 当前成片走的就是这条路

旁白文件放在 `audio/final/`，需要「wav + marks.json」一对：

| 旁白 | marks | 时长 |
|---|---|---|
| `audio/final/vo_qv2_92s22.wav` | `vo_marks_qv2_92s22.json` | 92.22s（**音色最新、最推荐**） |
| `audio/final/vo_qv2_matched_91s78.wav` | `vo_marks_qv2_91s78.json` | 91.76s |
| `audio/final/vo_v2_matched_91s78.wav` | `vo_marks_v2_91s78.json` | 91.78s（旧成片用过这条） |

```bash
# ① 旁白接入时间轴（校验时长、降噪、补偿滤波器延迟、桥接字幕间隙）
$PY audio/use_v2_vo.py

# ② 配乐 + 音效（设计不变，落点跟随新 marks）
$PY audio/synth_mix.py --stems

# ③ 母带 → -14 LUFS / TP ≤ -1.5
$PY audio/master.py

# ④ 重建渲染页（字幕、镜头、定版卡按新 marks 重排）
$PY build_html.py

# ⑤ 渲全片
DUR=$($PY -c "import json;print(json.load(open('audio/vo_timeline.json'))['total'])")
$PY "$ROOT/.agents/skills/code-video-studio/scripts/render.py" \
   index.html out/final.mp4 --size 1920x1080 --fps 30 \
   --duration $DUR --audio audio/mix_norm.wav
```

> `use_v2_vo.py` 里的源文件是**写死**的（`VO_SRC` / `MARKS` 两个常量）。换旁白 = 改这两个常量，或在同目录覆盖同名文件。
> 渲染 97.47s ≈ 3.5 分钟（2924 帧，Apple Silicon 实测 206s）。

### 4.2 情形 B：改文案、重新合成配音

```bash
export DASHSCOPE_API_KEY=sk-xxx      # 只放环境变量
# 1. 改 audio/vo_lines.json 里的 6 段文案（id 保持不变）
$PY audio/make_vo.py --rate 1.36 --gap 0.28 --tail 2.6
#   调 音频训练/tts.py 逐镜合成（默认音色 qwen_v2_24）+ 出 marks
#   单镜想单独放慢：在该条文案里加 "rate": 1.20
#   rate 实测：1.36 ≈ 5.3 字/秒（舒服）；1.18 ≈ 4.6 字/秒（很慢）；1.45 ≈ 6.4 字/秒（偏快）
$PY audio/synth_mix.py --stems
$PY audio/master.py
$PY build_html.py
# 2. 渲片，命令同上
```

### 4.3 情形 C：只换音轨、画面不动（不重渲，10 秒搞定）

```bash
ffmpeg -y -i out/final.mp4 -i audio/mix_norm.wav \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest out/tmp.mp4 \
  && mv out/tmp.mp4 out/final.mp4
```

---

## 5. 渲染技术原理与硬性规则

### 5.1 页面契约

`index.html`（由 `build_html.py` 生成，**不要手改**）暴露：

```js
window.render = (t) => { /* 把第 t 秒的画面完全画出来 */ }
window.ready = false;      // 素材/字体没加载完时
// 加载完成后置 true，渲染器会等这个标志
```

时间轴数据以 JSON 注入页面：

```js
const TL = {/* total, vo_end, scenes:[{id,start,end,text}], subs:[[start,end,text]] */};
const SCN = TL.scenes, SUBS = TL.subs, DURATION = TL.total;
```

每个场景的渲染函数里写 `const lt = t - SCN[i].start;`（场景内相对时间），**不要硬编码绝对秒数**。

### 5.2 五条硬性规则

1. **画面必须 100% 由 `t` 决定**——同一 t 渲两次必须像素级一致（否则逐帧渲染会闪）。
2. **禁止 `Math.random()`**——需要随机用带种子的 hash（页面里有 `hash(n)`）。
3. **禁止 CSS `transition` / `animation`**——所有动效由 JS 求值。
4. **默认不跑 `requestAnimationFrame`**——只有 URL 带 `?play=1` 时才实时播放。
5. **缩放容器不加 `will-change`**——会让文字发糊。

动效基元只有两个：欠阻尼弹簧 `spring(x, w, z)` 与 `smoothstep(a, b, t)`。

### 5.3 版式要点（EP01 · v2 官网设计语言版）

- **视觉语言对齐 CodeDeck 官网**：浅色纸面 + 淡网格、`1px #e7e7e3` 细分隔线、官网同款叠层柔和阴影（`--shadow-card` / `--shadow-float`）、24–30px 大圆角卡片、紧字距无衬线大标题（`letter-spacing:-.035em`）、带绿点的 eyebrow 胶囊、官网同款线性图标（`<symbol id="i-*">`）。不再使用旧版的硬边偏移阴影与粗黑描边。
- 设计变量照搬官网：墨 `#18181b` / 次墨 `#3f3f46` / 弱字 `#6a6a73` / 分隔线 `#e7e7e3` / 纸 `#f4f4f0` / CodeDeck 绿 `#10b981`·`#047857` / Claude 橙 `#d97757`；Logo 用内联 SVG 重绘（蓝色渐变底 + 叠卡 + `>_`）。
- 字体栈：`-apple-system, "SF Pro Text", "Inter", "PingFang SC", "Noto Sans CJK SC"`；等宽 `"SF Mono", "JetBrains Mono"`。macOS 渲染走 SF + 苹方，Linux 走 Inter + 思源黑体（`apt install fonts-inter fonts-noto-cjk fonts-noto-color-emoji fonts-jetbrains-mono`）。
- 第 5/6 镜按官网示意图用 DOM 重建（不是截图）：痛点卡 → Hero → Mac mini 对比 → 连接路线 → 五地区点阵地球（陆地点阵数据取自官网，存于 `source/globe_land.b64`）→ 启动器一键连接 → 审批弹窗 → 全天候时间线 + 手机推送 → 安全四支柱 → 桌面端 + 手机主视觉 → 深色 CTA 定版。
- 单文件、离线、零外网依赖；两张真实素材以 Base64 内嵌（`build_html.py` 读 `source/asset_indo_hd.jpg`、`source/asset_moments_hd.jpg`，由原图 `indonesia-kyc.jpg` / `agent-moments.png` 缩放而来）。
- 顶栏：Logo + 期号 + 当前章节胶囊 + 6 段进度条 + 时间码；底部：深色圆角字幕，价格/数字标黄、CodeDeck 标绿。
- **全片不得出现任何网址/域名**，只出现产品名「CodeDeck」——`build_html.py` 生成时会自动断言，命中即报错退出。

### 5.4 场景与定版卡

- 每镜显示到「下一镜 `start`」为止（marks 之间有 0.2s 静音，落在间隙里会回落到第 1 镜）
- 定版卡落点 = `TL.vo_end + 0.15s`（最后一句读完即落卡），画面与音效共用同一公式

---

## 6. 配音生成（重点）

**完整契约见 [`音频训练/配音生成说明.md`](音频训练/配音生成说明.md)，下面是必读摘要。**

### 6.1 音色

| 项 | 值 |
|---|---|
| 默认音色键 | `qwen_v2_24`（`tts.py` 默认就是它，**不要传 `--voice`**） |
| voice_id | `qwen-audio-3.1-tts-plus-dshqv24-d8be9edf745547a3863a47252725836e` |
| 模型 | `qwen-audio-3.1-tts-plus` |
| 参考音频 | `音频训练/processed/ref_v2_volc_24s.wav`（24.0s，SNR 39.2 dB） |

**弃用音色**：`cosy_plus` / `cosy_flash` / `qwen_plus` / `cosy_v1_legacy` —— 用旧录音（SNR 21 dB）训练，成品有 +15 dB 高频嘶声。

### 6.2 调用方式（唯一正确姿势：走 `tts.py`，不要自己写 HTTP）

```bash
export DASHSCOPE_API_KEY=sk-xxx     # 只从环境变量读
cd "$ROOT/音频训练"

$PY tts.py \
  --text-file <文案.txt> \
  --out <输出.wav> \
  --rate 1.45 \
  --unit sentence \
  --marks-out <时间轴.json> \
  --json
```

| 参数 | 说明 |
|---|---|
| `--text` / `--text-file` | 二选一 |
| `--out` | 输出 wav（48k / mono / 16-bit） |
| `--rate` | `1.0` 自然语速（≈4.7 字/秒）；`1.45` ≈6.5 字/秒，接近现有剪辑节奏 |
| `--gap` | 句间停顿，默认 0.22s |
| `--lufs` | 默认 −18（VO stem 电平）；`0` 关闭归一化 |
| `--unit sentence` | 一句一请求，逐句时间轴（**动画必需**） |
| `--marks-out` | 每段起止写 JSON，供视频对轴 |
| `--json` | stdout 只输出一行 JSON，便于解析 |

`tts.py` 已内置：≤340 汉字自动分段、429/5xx 指数退避重试、拼接、响度归一、真峰值限制。

**退出码**：0 成功 / 2 参数或环境错（如缺 key）/ 3 API 错 / 4 音频处理错。

**计费**：1 汉字 = 2 字符，`qwen-audio-3.1-tts-plus` ≈ 2.8 元/万汉字；EP01 全文 590 汉字 ≈ 0.14 元/次。

### 6.3 长度对齐技巧

`rate` 不是严格线性。先按 1.45 生成，量出纯语音 T，则
`新 rate ≈ 1.45 × T / (目标 L − 0.22 × (句数−1))`。

### 6.4 禁止事项（会直接搞坏别人流程）

1. 不要改 `音频训练/voices.json`
2. 不要调用 `create_voice` 重建音色（voice_id 一变，所有引用失效）
3. 不要改 `音频训练/processed/` 下的参考音频
4. 不要把 key 写进代码或提交

---

## 7. 音频链路（配乐 / 音效 / 母带）

```
vo_clone.wav ──(anlmdn 降噪 + 群延迟补偿)──> vo_clean.wav ─┐
                                                          ├─> mix.wav ──(增益+限制器)──> mix_norm.wav ──> 成片
numpy 合成 120BPM 配乐（ducking）+ 音效（锚在 marks）──────┘
```

| 脚本 | 作用 |
|---|---|
| `audio/make_vo.py` | 改文案时：逐镜调 `tts.py` → `clone/*.wav` → `vo_clone.wav` → `vo_timeline.json` |
| `audio/use_v2_vo.py` | 用现成旁白：校验时长 → 降噪 → 补偿延迟 → 由 marks 生成 `vo_timeline.json` |
| `audio/synth_mix.py` | 120BPM 四个和弦（Fmaj7→Em7→Dm7→Cmaj7）+ kick + 琶音；人声自动闪避；音效按 marks 定位；`--stems` 导 `stem_vo/bgm/sfx.wav` |
| `audio/master.py` | 线性增益 + `alimiter`（−2.8 dBFS，留采样间过冲余量）→ −14 LUFS，**不做动态压缩** |

### 三个必须知道的坑

1. **不要用 loudnorm 动态模式**：会把句间底噪整体抬 8 dB，听感发毛。只用「增益 + 前视限制器」。
2. **IIR 滤波器与限制器都有延迟**：`anlmdn` ≈ 7.92ms、`alimiter` 5ms，两个脚本都已补偿，**改参数要同步改补偿**（`use_v2_vo.py` 的 `_lag()`、`master.py` 的 `ATTACK_MS`）。
3. **配乐里不要用白噪声当 hi-hat、不要 `tanh` 软削波**：前者是「沙沙声」元凶，后者加谐波发毛。

---

## 8. 成片规格与验收

当前 `视频制作/claude-codedeck-ep01/out/final.mp4`：

```
97.467s · 1920×1080 · 30fps · H.264 + AAC 192k · 17.0 MB · 2924 帧（v2 画面）
-14.2 LUFS · 真峰值 -1.8 dBTP · 无削波（≥-0.1dBFS 采样 0 个）
```

### 验收命令

```bash
cd "$ROOT/视频制作/claude-codedeck-ep01"

# 抽帧拼图 + 镜头切换检测（空帧/残影）
$PY "$ROOT/.agents/skills/code-video-studio/scripts/analyze_video.py" \
   out/final.mp4 --out qa/final-analyze

# 手机可读性（缩到 300px 宽拼图）
ffmpeg -y -i out/final.mp4 -vf "fps=1/3.1,scale=300:-1,tile=6x5" -frames:v 1 qa/mobile-360.png

# 响度/真峰值/波形/频谱
ffmpeg -y -i out/final.mp4 -vn -ac 1 -ar 48000 qa/final_audio.wav
$PY "$ROOT/.agents/skills/code-video-studio/scripts/audio_tools.py" \
   check qa/final_audio.wav --out qa/final-audio
```

### 合格线

| 项 | 标准 |
|---|---|
| 无空帧 / 无跨镜残影 | 抽帧目检 |
| 360px 宽下标题与价格可读 | `qa/mobile-360.png` |
| 旁白时长 = marks total | ±0.05s |
| 成片对位偏差 | ≤ 1 帧（33ms） |
| 响度 / 真峰值 | −14 LUFS / ≤ −1.5 dBTP |
| 无削波、无异常静音 | 波形图 + 采样统计 |
| 全片无网址 | `grep -oE "https?://|www\.|codedeck\.top" index.html` 应为空（`build_html.py` 也会自动断言） |

---

## 9. 常见问题

| 现象 | 原因 / 处理 |
|---|---|
| 渲染报 “No usable browser” | `python3 -m playwright install chromium` |
| 帧与帧之间闪烁 | 页面里用了 `Math.random()` 或 CSS animation |
| 旁白比字幕晚一点 | 忘了补偿 `anlmdn`(7.92ms) / `alimiter`(5ms) |
| 字幕条一闪一闪 | marks 间有静音，字幕按 marks 断开；用「桥接 ≤0.3s 间隙」 |
| 镜间出现第 1 镜画面 | 场景窗口没延伸到下一镜 `start` |
| 成片峰值超限 | `master.py` 会自动回退增益；若仍超，降低 `LIMIT_DB` |
| `tts.py` 退 2 | 缺 `DASHSCOPE_API_KEY` |
| `tts.py` 退 3 `ResourceNotExist` | voice_id 与 model 不匹配，或音色被删 |
| 生成的配音太长 | 提高 `--rate`，见 §6.3 |
| 配音有嘶声 | 音色用了旧录音训练的模型；换 `qwen_v2_24` |
| 渲片太慢 | 降低 `--fps`、或用 `--start/--duration` 分段渲再 concat |

---

## 10. 接手 checklist

1. 跑 §2.2 环境自检，确认 `ready`。
2. 跑 §3 出静帧 + 6 秒片段，确认渲染链路通。
3. 读 `视频制作/claude-codedeck-ep01/brief.md`（制作规格）与 `audio/vo_lines.json`（文案）。
4. 看 `qa/sheet-full.png`、`qa/mobile-360.png`、`qa/v4_boundaries.png`，建立画面印象。
5. 要改配音 → 先读 `音频训练/配音生成说明.md`，再用 §4.1 / §4.2 的流程。
6. 任何改动都要能回答：**「改完之后哪一项验收指标变好了？」**

---

## 11. 待办

- [ ] **9:16 竖屏版（抖音）**：`index.html` 目前是 1920×1080 的固定版式，竖屏需要重排版式安全区（顶部避让 ~140px、底部 ~340px、右侧 ~120px），**不能直接裁切 16:9**。配音与 marks 可直接复用。
- [ ] 3:4 方屏版（小红书）
- [ ] EP02 剧本

---

## 12. 许可与注意

- 仓库为 **public**：`音频训练/录音.m4a`、`新录音.m4a`、`processed/` 是你本人声音素材，已被公开。
- `音频训练/voices.json` 只含 voice_id，不含密钥；调用仍需自己的 `DASHSCOPE_API_KEY`。
- 历史提交里曾出现过明文 key，**建议在阿里百炼控制台重置该 key**。

---

*最后更新：2026-11-22（旁白放慢版 97.47s）*
