---
name: code-video-studio
description: >-
  用代码生成与渲染高质量自媒体视频（HTML/CSS/SVG、Canvas 2D、WebGL 着色器、Three.js + numpy 代码合成配乐音效 + Playwright 逐帧截图 + FFmpeg 合成）。
  融合 xilo-opus-video、awesome-opus5-5-videos、lemo-opuscar、mg-styles-15 与 dashi-animationstyle 的工程方法论。
  当用户需要「用代码做视频」「做动效视频」「制作科普/宣传片/口播配画」「渲染视频」「写一个视频页面并导出 MP4」时立即触发使用。
---

# code-video-studio：自媒体代码视频制作工作流

本 Skill 将大模型的创意与编程能力转化为**可控、可复刻、电影级质感**的 MP4 成片：网页暴露纯时间函数 `window.render(t)`，由 Playwright 无头浏览器逐帧渲染截图，经 FFmpeg 合成视频，并用 Python (`numpy`) 合成节拍精准的配乐与音效（或与配音/绿幕素材混音）。

## 目录与输出约定

- **Skill 工具链目录**：`/Volumes/文件/自媒体/.agents/skills/code-video-studio/`
  - `scripts/check_env.py`：检查 Python、FFmpeg、Playwright、Chromium、WebGL2 与 `chromakey`
  - `scripts/render.py`：逐帧截图并管道直出 MP4（支持 `--still` 静帧、`--subframes` 运动模糊、`--start/--duration` 局部重渲、`--audio` 混音）
  - `scripts/audio_tools.py`：按时间轴生成 UI/转场音效、测量现有音乐节拍 `beats`、标准化响度 `-14 LUFS`、绘制波形与频谱图
  - `scripts/analyze_video.py`：分析参考视频或成片，输出 `ffprobe` 参数、镜头切点与抽帧拼图（含 `--cell-width 360` 手机可读性测试）
  - `references/`：`code-stack.md`、`craft-rules.md`、`brief-template.md`、`plan-format.md`、`ecosystem-styles.md`
- **视频项目输出目录**：统一放在 `/Volumes/文件/自媒体/视频制作/<slug>/`（若为平台专用成品，也可在成片阶段复制一份到 `抖音/` 或 `小红书/`）：
  ```text
  <slug>/
    source/        原材料、文稿、参考视频分析图与 beats.json
    previews/      方案预览（plan-a.png / plan-b.mp4 ...）
    brief.md       7 标签 XML 结构化分镜与技术规格
    index.html     离线自包含渲染页（暴露 window.render(t)）
    audio/         配乐脚本、mix.wav、mix_norm.wav
    qa/            关键帧静帧、抽帧拼图、360px 手机缩略图、音频波形图
    out/final.mp4  最终成片
  ```

---

## 执行流程（6 步法）

### 第 0 步：环境自检
首次制作或切换环境时先运行（本机完整依赖环境为 `/Volumes/environment/Python/anaconda3/bin/python3`，包含 `numpy` 与 `playwright`）：
```bash
/Volumes/environment/Python/anaconda3/bin/python3 /Volumes/文件/自媒体/.agents/skills/code-video-studio/scripts/check_env.py
```
确认输出 `ready`。若在其它机器使用且默认 `python3` 缺少依赖，先提示并补齐。

### 第 1 步：明确需求与画幅规格
整理用户提供的原材料（一句话想法 / 文案或口播稿 / 产品网址或代码 / 参考视频 / 背景音乐），确认 4 个关键参数（未指定时采用默认值）：
1. **画幅与分辨率**：B站/横屏默认 `1920x1080` (16:9)；抖音/视频号 `1080x1920` (9:16)；小红书 `1080x1440` (3:4)；方形动效 `1440x1440` (1:1)。安全区规则见 `references/ecosystem-styles.md`。
2. **时长与帧率**：默认 `15–30s`、`30fps`（快节奏卡点/弹簧动效可用 `60fps` 或 `--subframes 4`）。
3. **声音方案**：代码 `numpy` 合成节拍配乐 + 音效（默认）；若用户提供音乐，先用 `audio_tools.py beats` 测算节拍表；若有口播配音，先确定逐句时间戳再编排画面。
4. **视觉风格**：对照 `references/ecosystem-styles.md` 与 `references/code-stack.md` 选定风格与技术栈。

### 第 2 步：出三个差异化方案并做预览（探索/交互任务时）
按 `references/plan-format.md` 设计 **3 个明显拉开的方案**（如：A 稳妥刊物风 / B 风格化像素或手绘 / C 一镜到底或拟人主角），每个方案用 `render.py --still` 或 2–3 秒小样生成预览图/片供用户拍板。（若用户明确要求直接按指定方案/风格出片，可直接推进到第 3 步。）

### 第 3 步：固化 `brief.md`
按 `references/brief-template.md` 写入 `<role>`、`<inputs>`、`<direction>`、`<structure>`、`<build>`、`<gotchas>`、`<start>`。必须写明**禁止清单**（如禁止深色渐变居中大字淡入、禁止匀速运动、禁止元素重叠）。

### 第 4 步：编写画面代码与合成音频
严格遵守 `references/craft-rules.md` 的硬性工程规范：
1. **纯时间函数 `window.render(t)`**：
   - 画面状态 100% 由 `t` 决定，严禁 `Math.random()`（改用带种子的确定性哈希）、严禁 CSS `transition`/`animation`、严禁默认启动 `requestAnimationFrame` 循环（仅在 URL 含 `?play=1` 时启用人工预览播放，确保 Playwright 截图稳定）。
2. **闭式弹簧与缓动**：
   - 使用欠阻尼闭式弹簧公式 `spring(x, w, z)` 及多目标累加公式，按 4 档调校手感（按钮/光标快利落 `w=24, z=0.8`；卡片默认 `w=15, z=0.74`；大字定版沉稳 `w=10, z=0.9`；贴纸活泼 `w=18, z=0.5`）。
3. **离线字体与画质红线**：
   - 保持 `index.html` **100% 离线自包含**，不依赖外网 CDN 或 Google Fonts，中文字体优先 macOS 原生 `"Songti SC"`, `"PingFang SC"`, `"SF Mono"`。
   - **禁止在缩放容器或文字元素上使用 `will-change: transform`**；Canvas 内部按 `dpr = 2` 绘制，像素风关闭 `imageSmoothingEnabled`。
4. **代码合成配乐与音效**：
   - 使用 `numpy`（48kHz, 16-bit WAV）按 `BPM` 节拍合成鼓组、贝斯、带泛音/失谐的和弦铺底及动作音效，经 `audio_tools.py normalize` 标准化至 `-14 LUFS`（True Peak < `-1 dBTP`），再用 `audio_tools.py check` 生成波形图与频谱图核查削顶或异常静音。

### 第 5 步：分层渲染与导演自检闭环
1. **先出静帧验排版**：对每个镜头的关键时间点跑 `render.py --still`，直接查看 PNG 图片检查文字可读性、构图比例、字体加载与边界安全区。
2. **合成全片**：用 `render.py index.html out/final.mp4 --audio audio/mix_norm.wav` 导出成片。
3. **抽帧与手机视角验收**：用 `analyze_video.py` 生成 16 宫格全片抽帧图及 `--cell-width 360` 手机缩略拼图。
4. **7 项导演打分（均须 >= 8/10）**：开场抓人度、360px 手机可读性、动作流畅度（无匀速/死帧）、每 2–4 秒变化感、构图饱满度、风格与事实一致性、声画卡点同步。发现问题后局部修复并重渲，直到全部过线再交付。
