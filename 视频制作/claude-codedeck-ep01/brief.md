<role>
你是一位动态设计师，也是一位创意程序员，擅长用纯前端代码与音频信号合成制作刊物质感、节奏紧凑的自媒体科普与产品种草视频。
</role>

<inputs>
主题：如何在国内稳定使用 Claude —— 从「骑摩托 1500km 印尼下乡收号」到「每月几十块的 CodeDeck 海外专属工位」
想让观众记住的一句话：不用下乡骑摩托收号，也不用每月花上千块租海外实体 Mac mini，用 CodeDeck 每月几十块即可拥有独立海外服务器，Claude Code 开机即用。
原材料：
- 稿件：source/raw-notes.md
- 真实图片 1：source/indonesia-kyc.jpg（印尼老哥举白板「印尼老哥助力 中国科研·中国AI China No.1」现场合影）
- 真实图片 2：source/agent-moments.png（代理朋友圈：海外 Mac mini M4 实体机阵列 + 印尼区预订凭证）
- 产品能力描述：raw-notes.md 中关于 CodeDeck 的功能条目（全片不出现任何网址）
规格：94.6 秒，1920×1080（16:9），30fps（2839 帧）
品牌：暖米纸色 #F5F1E8、墨黑 #18181B、卡片白 #FFFFFF / 暖灰 #EBE4D5、CodeDeck 翠绿 #10B981（深墨绿 #047857）、Claude 陶土橙 #D97757、警示朱砂红 #D9462F；字体 Songti SC（主标题）+ PingFang SC（正文/字幕）+ SF Mono（代码与价格）。
声音：**由 `音频训练/tts.py` 生成**（默认音色 cosy_plus，本人克隆音色，`--rate 1.55 --unit sentence --marks-out`），实测 6.3 字/秒、总长 93.44s；配乐为 120 BPM numpy 代码合成（人声自动闪避），音效全部锚在 marks 上；母带为线性增益 + lookahead 限制器（`audio/master.py`），成片 −14.2 LUFS / 真峰值 −1.6 dBFS。
</inputs>

<direction>
风格（v2 · 2026-11-22 起）：**对齐 CodeDeck 官网设计语言**。浅色纸面 + 淡网格，`1px #e7e7e3` 细分隔线，官网同款叠层柔和阴影，24–30px 大圆角白卡，紧字距无衬线大标题，带绿点的 eyebrow 胶囊，官网同款线性图标；小摩托保留为扁平矢量插画点缀，真实素材放在浮起的照片卡 / 窗口卡里。
介绍 CodeDeck 的画面一律参照官网示意图，用 DOM 重建（不贴截图）：应用窗口（侧栏会话 + 聊天 + 工具调用）、手机推送、五地区点阵地球、启动器、审批弹窗、全天候时间线、连接路线、深色 CTA。
全片统一顶栏（左：Logo + 期号，右：章节胶囊 + 6 段进度条 + 时间码），底部深色圆角字幕。
每镜只讲一件事，主标题停留 ≥ 3.5s，360px 手机宽度下标题与价格对比仍可读。
动画只用闭式弹簧与 smoothstep；转场靠卡片进出场、面板交叉淡化、标题上下替换（先出后进，不叠字）。
禁止：旧版硬边偏移阴影 / 粗黑描边、深色渐变居中大字淡入、新旧文字叠字、缩放容器加 will-change、外网 CDN/字体、Math.random()、**任何网址或域名**（只出现 CodeDeck 这个名字）。
</direction>

<structure>
时间轴由 `audio/vo_timeline.json` 驱动（tts.py 逐句 marks，`--rate 1.55`），画面/字幕/音效全部按它计算，换文案后整片自动重排。

镜头 1｜0.00–12.10s（// 01 · 物理破防）
- 0.0s：「八百层风控警报 · BAN RATE 99.9%」红章重拍落下，抓人。
- 0.45 / 1.65 / 2.85s：三层防线卡（封锁 IP / 设备指纹 / 实名 KYC）依次弹簧落下。
- 7.9s 起：12fps 手绘小摩托从左侧轰鸣冲出，8.55s 撞散三张卡，黑底黄边横幅砸下「物理破防」。
- 音效：开场重击 + 三次卡点 tick + 摩托 vroom + 撞击 impact。

镜头 2｜12.45–30.08s（// 02 · 摩旅 1500km 下乡收号）
- 左侧手绘地图：巴厘岛 → 苏门答腊 1500km 虚线生长，小摩托沿线推进（0.4→5.2s）。
- 13.75s：真实合影拍立得甩入，白板文字红框放大 + 原字放大条。
- 22.65s：大妈人物档案卡弹出（代码经验 0 行 → 3 个 Claude 号），13.0s 处盖朱砂章。
- 音效：whoosh / 相机快门 / pop / 印章 impact。

镜头 3｜30.43–49.52s（// 03 · 海外物理机真实账单）
- 左侧朋友圈截图卡片，图片平滑上下浏览（0→105px）展示机柜与订单。
- 右侧账单：36.0s 第 1 项 $159/月（≈¥1,060），40.5s 第 2 项 $360，42.4s 第 3 项 $520。
- 45.0s 总计栏跳至 ¥2,500–3,700+，斜盖「门槛劝退」红章。

镜头 4｜49.87–62.13s（// 04 · 这条视频就是 Claude 做的）
- 50.3 / 51.9 / 53.5s：三张能力卡（读全库重构 / 跑测试修 Bug / 写代码做视频）。
- 53.0s：Meta 面板滑入 ——「正在由 Claude Code 实时渲染当前视频帧」+ 帧号实时跳动，直接打破第四面墙。
- 56.4s：右侧金色 callout 二次强调「你现在看到的每一帧都是 Claude 写代码做的」。
- 音效：三次 pop + success 和弦。

镜头 5｜62.48–76.54s（// 05 · 破局：不用千元租机，每月几十块）
- 三条本地痛点红条先行（ECONNRESET / 合盖中断 / 搞乱主力机）。
- 63.6s 左卡「海外物理机月租 ¥1,060」落位，右侧虚线「?」占位（悬念）。
- 66.5s CodeDeck 卡揭晓（Spring 弹入），69.1s 红斜杠划掉 ¥1,060，69.4s「¥几十块/月」放大强调。
- 音效：whoosh ×2 + success。

镜头 6｜76.89–93.44s（// 06 · 12ms 直连 · 审批隔离 · 通宵跑）
- 工作台展开：5 个节点胶囊，🇸🇬 新加坡 ~12ms 高亮。
- 81.4–83.6s：矢量光标移到「允许并记住 ✓」点击，按钮变绿显示「已批准 · 42 passed」，夜间时间轴 23:30→05:00 推进。
- 87.44s：工作台淡出，品牌定版卡落定（spring w=11, z=0.86）：CodeDeck · 海外服务器直连，开机即用 + 四个支柱。
- 音效：whoosh / click / pop / success 收尾。
</structure>

<build>
1. 画面：单文件离线 index.html，内嵌 Base64 的两张真实素材；DOM 排版 + Canvas 2D（手绘摩托、地图）+ SVG 光标。
2. `window.render(t)` 纯时间函数；伪随机用 seeded hash；无 CSS transition/animation；`?play=1` 才开 rAF。
3. 时间轴：`audio/make_vo.py` → `音频训练/tts.py`（cosy_plus, rate 1.55, sentence marks）→ `audio/vo_timeline.json`；`build_html.py` 把 SCN / SUBS / DURATION 注入页面。
4. 声音：`audio/synth_mix.py` 读同一份 timeline 摆配乐与音效 → `audio_tools.py normalize`。
5. 渲染：`render.py index.html out/final.mp4 --size 1920x1080 --fps 30 --duration 94.636 --audio audio/mix_norm.wav`。
6. 质检：关键帧静帧 → 整片 → analyze 16 宫格 + 360px 手机拼图 + 波形/频谱。
</build>

<gotchas>
- **镜间 0.35s 静音**：tts.py 拼接留白，场景窗口必须延伸到「下一镜开始」，否则落在间隙里会没有镜头命中、回落第 1 镜（已修）。
- 内嵌 Base64 图必须 `img.decode()` + `document.fonts.ready` 都完成后再置 `window.ready = true`。
- 缩放卡片上不加 `will-change`，文字才不糊。
- 定版卡进场前先让工作台淡出，避免两层文字叠着发灰。
- 换文案必须重跑 `make_vo.py`，字幕与动画会跟着 marks 整体重排。
- **tts.py 输出自带宽带嘶声**（4–8k 约 −48 dBFS，rate 越高越重：1.38 时 −56.6，1.55 时 −48.1）。母带会整体 +10 dB，不处理就会变成明显的「电磁」底噪。`make_vo.py` 已内置 `highpass=75, anlmdn=s=7:p=0.002:r=0.006`，可压掉约 21 dB 且不伤齿音。
- **配乐里不要用白噪声做 hi-hat**：宽带嘶声是「沙沙底噪」的最大来源，节奏交给 kick + 琶音即可。
- **不要用 tanh 软削波 + acompressor + loudnorm 三级串联**：会把句间底噪抬 8dB 且加谐波。母带只用线性增益 + 限制器。
</gotchas>

<start>
改文案 → 跑 make_vo.py → synth_mix.py + normalize → build_html.py → 静帧自检 → 渲整片 → 抽帧/波形验收。
</start>
