# 交接提示词（可直接粘贴给另一个 AI / Agent）

> 用法：把下面整段复制给新的 AI，它就能在不看历史对话的情况下接手。
> 或者让它先读本文件：`/Volumes/文件/自媒体/视频制作/claude-codedeck-ep01/HANDOFF.md`

---

你是一位动态设计师兼创意程序员，接手的是一支**已经出片、需要继续优化**的横屏科普/种草短视频。请先读完本文件再动手，不要推翻重做。

## 一、这支片子是什么

**主题**：如何在国内稳定使用 Claude —— 从「中国号商骑摩托 1500 公里去印尼下乡收号」这个离谱真事，讲到「每月几十块租一台专属海外服务器跑 Claude Code」的解决方案。

**产品**：CodeDeck，一个把 Claude Code 装在独立海外服务器上的远程工作台（官网 codedeck.top）。
**红线：全片任何位置都不允许出现网址或域名，只能出现「CodeDeck」这个名字。** 配音、字幕、画面大字、定版卡、顶部标识全部适用。

**叙事结构（6 个镜头）**：

| 镜号 | 时间（秒） | 内容 |
|---|---|---|
| 01 | 0.00–12.28 | 钩子：Anthropic 层层风控（IP/指纹/KYC）→ 被小摩托「物理破防」 |
| 02 | 12.50–28.27 | 摩旅 1500km 进村、面对面打款过 KYC、大妈名下 3 个 Claude 号 |
| 03 | 28.49–46.01 | 算账：海外 Mac mini $159/月 + Max $360 + Ultra $520 → 每月 ¥2500–3700+ |
| 04 | 46.23–58.25 | 为什么非用 Claude：读全库、跑测试、**还能写代码做视频**（本条片子就是 Claude 代码生成的） |
| 05 | 58.47–71.34 | 破局：CodeDeck，不用租实体 Mac mini，每月几十块享受同等稳定环境 |
| 06 | 71.56–88.07 | 12ms 直连 · 英文节点 · 审批隔离 · 合盖通宵跑 · 凭据自持（88.22 起定版，片长 91.78s） |

**画面上的真实素材**（只能用这两个，不许编）：
- `source/indonesia-kyc.jpg`：印尼老哥手举白板「印尼老哥助力 中国科研·中国AI China No.1」的现场合影
- `source/agent-moments.png`：代理朋友圈截图，海外 Mac mini M4 机柜 + 印尼区预订凭证

**事实清单（不可改动）**：Mac mini 月租 $159 ≈ ¥1060；Max $360/月；Ultra $520/月；新加坡节点延迟 ~12ms；五个部署地区（美/新/日/韩/马）；独立公网 IP 一人一台；systemd 守护、合盖不中断。

## 二、当前成片状态

```
/Volumes/文件/自媒体/视频制作/claude-codedeck-ep01/out/final.mp4
91.78 s · 1920×1080 · 30fps · H.264 + AAC 192k · 11.5 MB
响度 −14.2 LUFS，真峰值 −1.8 dBFS，2753 帧
```

## 三、目录结构

```
claude-codedeck-ep01/
├── index.html            单文件离线渲染页，暴露 window.render(t)（由 build_html.py 生成，别手改）
├── build_html.py         把 audio/vo_timeline.json 注入 index.html（SCN / SUBS / DURATION）
├── brief.md              7 标签 XML 制作规格（风格、禁则、分镜、坑点）
├── README.md             复现流程
├── source/
│   ├── raw-notes.md              原始稿件
│   ├── indonesia-kyc.jpg         真实素材原图
│   ├── agent-moments.png         真实素材原图
│   ├── asset_indo.jpg            压缩后的 base64 内嵌版（920px 高）
│   └── asset_moments.jpg         同上（860px 宽）
├── audio/
│   ├── final/vo_v2_matched_91s78.wav      ★ 当前旁白（cosy_v2，91.78s / 48k）
│   ├── final/vo_marks_v2_91s78.json       ★ 当前 marks（total 91.78，末句 end 88.07）
│   ├── use_v2_vo.py        用现成旁白接管时间轴（校验时长 / 降噪 / 补偿延迟 / 桥接字幕）
│   ├── vo_lines.json       ★ 6 镜文案（唯一的文字源，改文案只改这里）
│   ├── make_vo.py          调 tts.py 合成 + 拼接 + 降噪 + 产出 vo_timeline.json
│   ├── synth_mix.py        120BPM 代码配乐 + 音效，全部按 marks 定位；`--stems` 导分层
│   ├── master.py           母带：线性增益 + lookahead 限制 → −14 LUFS
│   ├── clone/              逐镜配音 s1_hook.wav … s6_features.wav（当前生产用）
│   ├── clone_oldvoice/     旧音色版本（噪音版，仅作对比，勿用）
│   ├── vo_clone.wav        拼接后的原始配音 89.93s
│   ├── vo_clean.wav        降噪后配音（混音实际用这个）
│   ├── stem_vo.wav / stem_bgm.wav / stem_sfx.wav   分层，排查噪音用
│   ├── mix.wav             混音（未母带）
│   ├── mix_norm.wav        ★ 成片音轨（−14 LUFS）
│   └── vo_timeline.json    ★ 时间轴：{total, scenes[], subs[]}，画面和字幕都靠它
├── qa/                     抽帧拼图、360px 手机图、波形频谱、A/B 样本
├── previews/               三套风格方案的静帧
└── out/final.mp4           ★ 成片
```

## 四、画面是怎么生成的（必须遵守）

1. **纯时间函数**：`window.render(t)` 决定第 t 秒的全部状态。禁止 `Math.random()`（用带种子的 hash）、禁止 CSS `transition/animation`、禁止默认开 `requestAnimationFrame`（只在 URL 带 `?play=1` 时预览）。
2. **渲染方式**：Playwright 逐帧调 `render(t)` 截图，FFmpeg 管道合成 MP4。工具在
   `/Volumes/文件/自媒体/.agents/skills/code-video-studio/scripts/render.py`。
3. **Python 环境**：`/Volumes/environment/Python/anaconda3/bin/python3`（已含 numpy / scipy / playwright / edge-tts）。
4. **技术栈**：中文排版用 DOM（Songti SC 标题 + PingFang SC 正文 + SF Mono 数字），手绘小摩托和地图用 Canvas 2D（12fps 笔触抖动），光标用内联 SVG。**零外网依赖**，两张真实素材以 Base64 内嵌。
5. **动画**：只用欠阻尼闭式弹簧 `spring(x, w, z)` 和 `smoothstep`。文字不要加 `will-change: transform`（会糊）。
6. **时间轴驱动**：每镜的起止来自 `vo_timeline.json` 的 `scenes[i].start`，渲染函数里写 `lt = t - SCN[i].start`。改文案后不要手改秒数。
   ⚠️ 关键坑：镜间有 0.35s 静音，场景窗口必须延伸到「下一镜开始」，否则间隙里没有镜头命中会闪回第 1 镜（已修，别再引入）。

## 五、音频是怎么生成的（**最重要的约束**）

**配音必须用 `音频训练/tts.py`，不要自己写 TTS，不要用 edge-tts。**

```
/Volumes/文件/自媒体/音频训练/tts.py       主入口
/Volumes/文件/自媒体/音频训练/TTS_API.md   完整契约（含 HTTP 直调示例）
/Volumes/文件/自媒体/音频训练/voices.json  音色表（只有 id，无密钥）
```

- 音色：**当前用 `cosy_v2`**（`cosyvoice-v3.5-plus`），不要传 `--voice` 改别的。
  voice_id：`cosyvoice-v3.5-plus-dshv2-de51050804324850ad05118b2b3cde4d`
  旧音色 `cosy_plus` / `cosy_flash` / `qwen_plus` 已弃用（背景有嘶声），不要回退。
- 语速：1.0 ≈4.7 字/秒；**1.38 ≈6.6 字/秒（对齐现有剪辑用这个）**；旧版用 1.55
- 必须带 `--unit sentence --marks-out`，拿到逐句时间轴；否则字幕和动画无法对齐
- 需要环境变量 `DASHSCOPE_API_KEY`（**只能放环境变量，不要写进任何文件**）
- 输出 −18 LUFS / 真峰值 −1.5 dBFS，属于混音 stem 电平，成片再统一到 −14

**噪音问题的来龙去脉（已经修过，别重复踩）**：
参考录音 `音频训练/processed/ref_bailian_17s.wav` 的信噪比只有 **24.2 dB**，克隆把这个房间噪声学进了音色，输出 4–8k 有约 −48 dBFS 宽带嘶声。
解决方式：先洗参考音频再重新克隆。
- 清洗后参考：`音频训练/processed/ref_bailian_17s_clean.wav`（`highpass=70, anlmdn=s=7:p=0.002:r=0.006, afftdn=nf=-40:nr=8`，SNR 24.2 → 40.3 dB）
- 备份：`ref_bailian_17s.orig.wav`、`voices.json.bak`
- 合成后还会兜底跑一次 `anlmdn`（在 `make_vo.py` 里）
- 效果：4–8k 底噪 −48.1 → −66.2 dBFS，1–3k 谱平坦度 0.668 → 0.622
- 当前成片用的是 **`cosy_v2` 新旁白**（`audio/final/vo_v2_matched_91s78.wav`），不是这版 cosy_plus

**配乐与音效**（`audio/synth_mix.py`）：
- 120 BPM，numpy 从零合成：Fmaj7→Em7→Dm7→Cmaj7 铺底 + kick + 琶音，人声自动闪避（duck 到 0.06）
- 音效全部锚在 marks 上：开场重击、三张卡落地、摩托 vroom、撞击、相机快门、盖章、点击、成功和弦
- ❌ 不要用白噪声做 hi-hat（这是之前「沙沙声」的元凶，已全删）
- ❌ 不要用 `tanh` 软削波（加谐波、听感发毛）
- 配乐整体 9kHz 低通，高频让给人声

**母带**（`audio/master.py`）：
- 线性增益 + `alimiter`（limit −2.8 dBFS，限的是采样峰值，留 1 dB 采样间过冲余量）
- 目标 −14 LUFS / 真峰值 ≤ −1.5 dBFS
- `alimiter` 的 5ms lookahead 会整体延后音频，`master.py` 已用 `atrim` 补偿；改 attack 要同步改 `ATTACK_MS`
- ❌ 不要用单遍 `loudnorm` 的动态模式（会把句间底噪抬 8 dB）

## 六、改文案后的一条龙（唯一正确流程）

```bash
export DASHSCOPE_API_KEY=sk-xxx
cd /Volumes/文件/自媒体/视频制作/claude-codedeck-ep01

# 1. 只改 audio/vo_lines.json 里的 6 段文字（保持 6 个 id 不变）
/Volumes/environment/Python/anaconda3/bin/python3 audio/make_vo.py      # 合成 + 降噪 + 出 marks
/Volumes/environment/Python/anaconda3/bin/python3 audio/synth_mix.py    # 配乐 + 音效
/Volumes/environment/Python/anaconda3/bin/python3 audio/master.py       # 母带 → mix_norm.wav

# 2. 用新时间轴重排画面与字幕
/Volumes/environment/Python/anaconda3/bin/python3 build_html.py

# 3. 渲全片（时长从 timeline 读，不要写死）
DUR=$(/Volumes/environment/Python/anaconda3/bin/python3 -c "import json;print(json.load(open('audio/vo_timeline.json'))['total'])")
/Volumes/environment/Python/anaconda3/bin/python3 \
  /Volumes/文件/自媒体/.agents/skills/code-video-studio/scripts/render.py \
  index.html out/final.mp4 --size 1920x1080 --fps 30 --duration $DUR --audio audio/mix_norm.wav
```

**只改音轨不改画面时**，不要重渲视频，直接重封装：

```bash
ffmpeg -y -i out/final.mp4 -i audio/mix_norm.wav \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest out/final_tmp.mp4 \
  && mv out/final_tmp.mp4 out/final.mp4
```

## 七、设计规范

- 配色：纸色 `#F5F1E8`、墨 `#18181B`、暖灰卡 `#EBE4D5`、Claude 橙 `#D97757`、CodeDeck 绿 `#10B981` / `#047857`、警示红 `#D9462F`
- 风格：编辑部刊物感（Bento 卡片 + 硬边偏移阴影 `box-shadow: 12px 14px 0 #18181B`）+ 拍立得实拍证据
- 顶部固定：左侧 EP01 胶囊 + 当前章节，中间 6 段进度条，右侧 CodeDeck 标识 + 时间码
- 底部：高对比黑底胶囊字幕，居中对齐，最多两行
- 安全区：距底 22px 起放字幕，主内容区底部预留 118px，绝不让字幕压住账单价签
- 禁止：深色渐变居中大字、新旧文字叠字、缩放容器加 `will-change`、外网字体/CDN、任何网址

## 八、验收标准（每项 ≥ 8/10 才算过）

```bash
# 16 宫格抽帧（看空帧、残影、跨镜残留）
/Volumes/environment/Python/anaconda3/bin/python3 \
  /Volumes/文件/自媒体/.agents/skills/code-video-studio/scripts/analyze_video.py \
  out/final.mp4 --out qa/final-analyze

# 360px 手机可读性
ffmpeg -y -i out/final.mp4 -vf "fps=1,scale=300:-1,tile=6x6" -frames:v 1 qa/mobile-360.png

# 响度 / 真峰值 / 波形 / 频谱
ffmpeg -y -i out/final.mp4 -vn -ac 1 -ar 48000 qa/final_audio.wav
/Volumes/environment/Python/anaconda3/bin/python3 \
  /Volumes/文件/自媒体/.agents/skills/code-video-studio/scripts/audio_tools.py \
  check qa/final_audio.wav --out qa/final-audio
```

必查：无空帧 / 无跨镜残影 / 文字不溢出 / 360px 下标题与价格可读 / 无削顶 / 无异常静音 / 全片无网址。

## 九、当前已知的可优化点（欢迎继续改）

1. **第 4 镜（47.7–59.65s）** 三张能力卡落地后到 Meta 面板出现之间仍有约 0.6s 的过渡空档，可以做得更紧。
2. **第 6 镜工作台**左右两个面板内部留白偏多，可以再加信息密度（例如节点切换、真实 diff 行）。
3. **大妈档案卡**（约 24–28s）信息量偏少，可以补一个「她的号码从哪来」的链条小图。
4. **转场**目前大多是卡片折叠/弹簧位移，第 3→4、5→6 两处可以尝试更「从内容长出来」的形变（例如账单纸直接卷成能力卡）。
5. **音频**：`stem_vo` 里仍有很轻的齿音颗粒，如果追求更干净可以试 `deesser` 或在 6–9k 做 −2 dB 高架衰减（注意别把人声弄闷）。
6. **平台适配**：现在只有 16:9。9:16 抖音 / 3:4 小红书需要重排安全区（顶部避让 140px、底部 340px、右侧 120px）。场景是按版式函数写的，可以只改布局不改内容，但**不要直接把 16:9 居中裁切**。

## 十、硬性禁止

- ❌ 不接受「再写一个 TTS」：配音只能来自 `音频训练/tts.py`
- ❌ 不要把 `DASHSCOPE_API_KEY` 写进任何文件或提交
- ❌ 不要改 `--voice`（必须 cosy_plus）
- ❌ 不要在任何画面上出现网址 / 域名
- ❌ 不要用 `Math.random()`、CSS 动画、默认 rAF
- ❌ 不要用白噪声 hi-hat、tanh 软削波、单遍 loudnorm 动态模式
- ❌ 不要直接改 `index.html`（它由 `build_html.py` 生成，改了会被覆盖）

## 十一、先做这三件事

1. 打开 `qa/sheet-2s.png` 和 `qa/mobile-360.png`，用挑毛病的眼光看一遍，列出你认为最严重的 3 个问题（带时间点）。
2. 读 `brief.md` 和 `audio/vo_lines.json`，确认你理解 6 镜的意图和文案。
3. 再决定动哪里；任何改动都要能回答「改完之后，哪一项验收指标变好了」。
