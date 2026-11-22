#!/usr/bin/env python3
"""生成两套符合抖音科普赛道与 3:4/9:16 双安全区的封面 HTML。

- qa/cover_v1.html -> out/cover_douyin_v1.png / .jpg (暖纸刊物科普风)
- qa/cover_v2.html -> out/cover_douyin_v2.png / .jpg (深墨高对比硬核科普风)
"""
import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "source"
QA = ROOT / "qa"
QA.mkdir(exist_ok=True)

B64_INDO = base64.b64encode((SRC / "asset_indo_hd.jpg").read_bytes()).decode("ascii")

# 精致扁平手绘风格小摩托 SVG（内联离线，高辨识度）
MOTO_SVG = """
<svg viewBox="0 0 260 150" class="moto-svg" aria-hidden="true">
  <ellipse cx="132" cy="136" rx="102" ry="8" fill="rgba(24,24,27,0.12)"/>
  <!-- 速度线 -->
  <line x1="8" y1="74" x2="46" y2="74" stroke="#D95B38" stroke-width="5" stroke-linecap="round"/>
  <line x1="16" y1="92" x2="54" y2="92" stroke="#10B981" stroke-width="4" stroke-linecap="round"/>
  <line x1="22" y1="56" x2="48" y2="56" stroke="#18181B" stroke-width="3.5" stroke-linecap="round" opacity="0.35"/>
  <!-- 车轮 -->
  <circle cx="82" cy="112" r="24" fill="#18181B"/>
  <circle cx="82" cy="112" r="11" fill="#E4E4E7"/>
  <circle cx="196" cy="112" r="24" fill="#18181B"/>
  <circle cx="196" cy="112" r="11" fill="#E4E4E7"/>
  <!-- 车身 -->
  <path d="M52 104 C48 70, 74 56, 114 60 C130 62, 136 78, 132 94 L120 104 Z"
        fill="#D95B38" stroke="#18181B" stroke-width="4" stroke-linejoin="round"/>
  <rect x="112" y="84" width="76" height="16" rx="8" fill="#D95B38" stroke="#18181B" stroke-width="4"/>
  <path d="M174 94 L188 46 C202 48, 214 68, 218 94 Z"
        fill="#D95B38" stroke="#18181B" stroke-width="4" stroke-linejoin="round"/>
  <!-- 把手与头灯 -->
  <path d="M180 90 L198 28 L208 30 L191 92 Z" fill="#B84B2C" stroke="#18181B" stroke-width="3.5" stroke-linejoin="round"/>
  <line x1="186" y1="26" x2="216" y2="32" stroke="#18181B" stroke-width="5" stroke-linecap="round"/>
  <circle cx="215" cy="54" r="7.5" fill="#FDE68A" stroke="#18181B" stroke-width="3.5"/>
  <!-- 坐垫 -->
  <rect x="66" y="48" width="60" height="15" rx="7.5" fill="#27272A"/>
  <!-- 小旗杆与红旗 -->
  <line x1="76" y1="62" x2="62" y2="14" stroke="#18181B" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M62 14 Q36 8 10 18 L14 42 Q38 32 66 36 Z" fill="#DC2626" stroke="#18181B" stroke-width="3" stroke-linejoin="round"/>
  <!-- 骑手 -->
  <path d="M98 48 L124 72 L120 102" fill="none" stroke="#18181B" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M98 48 L124 72 L120 102" fill="none" stroke="#334155" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M96 46 L112 18 L148 36 L186 30" fill="none" stroke="#18181B" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M96 46 L112 18 L148 36 L186 30" fill="none" stroke="#10B981" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- 头盔 -->
  <circle cx="118" cy="14" r="14" fill="#FAFAF8" stroke="#18181B" stroke-width="3.5"/>
  <path d="M120 8 C128 8, 132 14, 130 20 L118 20 Z" fill="#18181B"/>
</svg>
"""

COMMON_CSS = r"""
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    width: 1080px;
    height: 1920px;
    overflow: hidden;
    font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif;
    -webkit-font-smoothing: antialiased;
  }
  .canvas {
    position: relative;
    width: 1080px;
    height: 1920px;
    overflow: hidden;
  }
  /* 兼容抖音主页 3:4 居中裁切 (y:240..1680) + 信息流右/底部交互避让 */
  .safe {
    position: absolute;
    left: 52px;
    right: 84px;
    top: 266px;
    bottom: 356px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .mono {
    font-family: "SF Mono", "Menlo", "Monaco", Consolas, monospace;
  }
  .serif {
    font-family: "Songti SC", "STSong", "Noto Serif SC", Georgia, serif;
  }
"""


def render_v1() -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<title>抖音科普封面 V1 - 暖纸刊物风</title>
<style>
{COMMON_CSS}
  .canvas {{
    background:
      radial-gradient(920px 620px at 80% 18%, rgba(217, 91, 56, 0.10), transparent 70%),
      radial-gradient(880px 580px at 18% 82%, rgba(16, 185, 129, 0.08), transparent 72%),
      #F5F1E8;
    color: #18181B;
  }}
  .grid-bg {{
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(24, 24, 27, 0.045) 1px, transparent 1px),
      linear-gradient(90deg, rgba(24, 24, 27, 0.045) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
  }}
  .eyebrow-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .pill {{
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 12px 24px;
    border-radius: 999px;
    background: #FFFFFF;
    border: 1.5px solid rgba(24, 24, 27, 0.12);
    font-size: 27px;
    font-weight: 700;
    color: #18181B;
    box-shadow: 0 8px 20px -12px rgba(24, 24, 27, 0.25);
  }}
  .pill .dot {{
    width: 13px;
    height: 13px;
    border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 0 5px rgba(16, 185, 129, 0.20);
  }}
  .pill.sub-tag {{
    background: #18181B;
    color: #FAFAF8;
    border-color: #18181B;
    font-size: 24px;
  }}
  .title-block {{
    margin-top: 8px;
  }}
  .h1-top {{
    font-size: 112px;
    font-weight: 900;
    line-height: 1.05;
    letter-spacing: -0.03em;
    color: #18181B;
  }}
  .h1-bot {{
    margin-top: 6px;
    font-size: 102px;
    font-weight: 900;
    line-height: 1.08;
    letter-spacing: -0.03em;
    color: #D95B38;
    display: inline-block;
    position: relative;
    z-index: 1;
  }}
  .h1-bot::after {{
    content: "";
    position: absolute;
    left: 0;
    right: 8px;
    bottom: 6px;
    height: 22px;
    background: rgba(251, 191, 36, 0.48);
    z-index: -1;
    border-radius: 6px;
  }}
  .lead {{
    margin-top: 22px;
    font-size: 36px;
    font-weight: 600;
    color: #52525B;
    line-height: 1.35;
  }}
  .bento {{
    display: grid;
    grid-template-columns: 452px 468px;
    grid-template-rows: 1fr;
    gap: 24px;
    height: 670px;
    min-height: 0;
  }}
  .photo-card {{
    background: #FFFFFF;
    border-radius: 28px;
    padding: 16px;
    border: 1.5px solid rgba(24, 24, 27, 0.10);
    box-shadow: 0 28px 50px -24px rgba(24, 24, 27, 0.28);
    display: flex;
    flex-direction: column;
    position: relative;
    height: 100%;
    min-height: 0;
    overflow: hidden;
  }}
  .photo-frame {{
    position: relative;
    flex: 1;
    min-height: 0;
    border-radius: 20px;
    overflow: hidden;
    background: #E4E4E7;
  }}
  .photo-frame img {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: 50% 60%;
    transform: scale(1.24);
    transform-origin: 50% 64%;
    display: block;
  }}
  .photo-badge {{
    position: absolute;
    top: 16px;
    left: 16px;
    background: #DC2626;
    color: #FFFFFF;
    font-size: 24px;
    font-weight: 800;
    padding: 8px 18px;
    border-radius: 999px;
    box-shadow: 0 6px 14px rgba(220, 38, 38, 0.35);
  }}
  .photo-foot {{
    padding: 16px 8px 4px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 24px;
    font-weight: 700;
    color: #27272A;
  }}
  .photo-foot span.tag {{
    font-size: 20px;
    color: #047857;
    background: rgba(16, 185, 129, 0.14);
    padding: 5px 12px;
    border-radius: 999px;
  }}
  .right-col {{
    display: flex;
    flex-direction: column;
    gap: 22px;
  }}
  .code-card {{
    height: 312px;
    background: #18181B;
    color: #FAFAF8;
    border-radius: 28px;
    padding: 26px 28px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 24px 44px -22px rgba(24, 24, 27, 0.45);
  }}
  .egg-tag {{
    display: inline-flex;
    align-self: flex-start;
    align-items: center;
    gap: 8px;
    background: rgba(16, 185, 129, 0.20);
    color: #34D399;
    border: 1px solid rgba(52, 211, 153, 0.35);
    padding: 7px 16px;
    border-radius: 999px;
    font-size: 23px;
    font-weight: 700;
  }}
  .egg-main {{
    font-size: 40px;
    font-weight: 800;
    line-height: 1.25;
  }}
  .egg-main em {{
    font-style: normal;
    color: #FDBA74;
  }}
  .egg-code {{
    background: rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 12px 16px;
    font-size: 22px;
    color: #A7F3D0;
    border: 1px solid rgba(255, 255, 255, 0.10);
  }}
  .moto-card {{
    flex: 1;
    background: #FFFFFF;
    border-radius: 28px;
    padding: 22px 26px;
    border: 1.5px solid rgba(24, 24, 27, 0.10);
    box-shadow: 0 22px 42px -24px rgba(24, 24, 27, 0.22);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .route-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 24px;
    font-weight: 800;
    color: #18181B;
  }}
  .route-dist {{
    color: #D95B38;
    font-size: 24px;
  }}
  .moto-wrap {{
    display: flex;
    align-items: center;
    justify-content: center;
    height: 158px;
  }}
  .moto-svg {{
    width: 270px;
    height: 152px;
  }}
  .cost-pill {{
    background: #FAF6EE;
    border: 1.5px solid rgba(217, 91, 56, 0.28);
    border-radius: 14px;
    padding: 10px 16px;
    font-size: 23px;
    font-weight: 700;
    color: #18181B;
    text-align: center;
  }}
  .cost-pill b {{
    color: #DC2626;
  }}
  .cost-pill em {{
    font-style: normal;
    color: #047857;
  }}
  .bottom-pills {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
  }}
  .nav-pill {{
    flex: 1;
    text-align: center;
    padding: 18px 12px;
    background: #FFFFFF;
    border: 1.5px solid rgba(24, 24, 27, 0.12);
    border-radius: 20px;
    font-size: 27px;
    font-weight: 800;
    color: #18181B;
    box-shadow: 0 12px 24px -16px rgba(24, 24, 27, 0.25);
  }}
</style>
</head>
<body>
<div class="canvas">
  <div class="grid-bg"></div>
  <div class="safe">
    <div class="eyebrow-row">
      <div class="pill"><span class="dot"></span>AI 科技科普 · EP01</div>
      <div class="pill sub-tag">全片纯代码渲染</div>
    </div>

    <div class="title-block">
      <div class="h1-top">800 层风控</div>
      <div class="h1-bot">竟被小摩托破防？</div>
      <div class="lead">跨岛 1500 公里实拍 · 揭秘克劳德使用门槛与云端解法</div>
    </div>

    <div class="bento">
      <div class="photo-card">
        <div class="photo-frame">
          <img id="indo-img" src="data:image/jpeg;base64,{B64_INDO}" alt="" />
          <div class="photo-badge">📍 1500km 实拍</div>
        </div>
        <div class="photo-foot">
          <span>苏门答腊现场合影</span>
          <span class="tag">人物已脱敏</span>
        </div>
      </div>

      <div class="right-col">
        <div class="code-card">
          <div class="egg-tag">★ 隐藏彩蛋</div>
          <div class="egg-main">整条视频 <em>2924 帧</em><br>全是克劳德写代码渲的</div>
          <div class="egg-code mono">window.render(t) → 97s</div>
        </div>

        <div class="moto-card">
          <div class="route-bar">
            <span>巴厘岛</span>
            <span class="route-dist mono">━━ 1500km ━━▶</span>
            <span>苏门答腊</span>
          </div>
          <div class="moto-wrap">{MOTO_SVG}</div>
          <div class="cost-pill">实体机 <b>¥2500+/月</b> → <em>云端轻方案</em></div>
        </div>
      </div>
    </div>

    <div class="bottom-pills">
      <div class="nav-pill">① 跨岛真事拆解</div>
      <div class="nav-pill">② 代码做视频</div>
      <div class="nav-pill">③ 云端部署思路</div>
    </div>
  </div>
</div>
<script>
window.render = function () {{}};
window.ready = false;
Promise.all([
  document.fonts ? document.fonts.ready : Promise.resolve(),
  document.getElementById('indo-img').decode().catch(() => {{}})
]).then(() => {{ window.ready = true; }});
</script>
</body>
</html>
"""


def render_v2() -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<title>抖音科普封面 V2 - 深墨硬核科普风</title>
<style>
{COMMON_CSS}
  .canvas {{
    background:
      radial-gradient(760px 540px at 16% 18%, rgba(249, 115, 82, 0.22), transparent 72%),
      radial-gradient(820px 620px at 85% 78%, rgba(52, 211, 153, 0.16), transparent 70%),
      #121418;
    color: #FAFAF8;
  }}
  .grid-bg {{
    position: absolute;
    inset: 0;
    background-image: radial-gradient(rgba(255, 255, 255, 0.10) 1.5px, transparent 1.5px);
    background-size: 40px 40px;
    pointer-events: none;
  }}
  .eyebrow-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .pill-dark {{
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 12px 24px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.08);
    border: 1.5px solid rgba(255, 255, 255, 0.16);
    font-size: 27px;
    font-weight: 700;
    color: #FAFAF8;
  }}
  .pill-dark .dot {{
    width: 13px;
    height: 13px;
    border-radius: 50%;
    background: #34D399;
    box-shadow: 0 0 12px #34D399;
  }}
  .pill-time {{
    padding: 11px 22px;
    border-radius: 999px;
    background: rgba(52, 211, 153, 0.16);
    border: 1.5px solid rgba(52, 211, 153, 0.36);
    color: #6EE7B7;
    font-size: 24px;
    font-weight: 700;
  }}
  .h1-w {{
    font-size: 102px;
    font-weight: 900;
    line-height: 1.06;
    letter-spacing: -0.025em;
    color: #FAFAF8;
  }}
  .h1-c {{
    margin-top: 6px;
    font-size: 108px;
    font-weight: 900;
    line-height: 1.06;
    letter-spacing: -0.025em;
    color: #34D399;
  }}
  .h1-c em {{
    font-style: normal;
    color: #F97352;
  }}
  .egg-banner {{
    background: linear-gradient(90deg, rgba(249, 115, 82, 0.22), rgba(52, 211, 153, 0.18));
    border: 1.5px solid rgba(249, 115, 82, 0.45);
    border-radius: 18px;
    padding: 16px 24px;
    font-size: 31px;
    font-weight: 800;
    color: #FDE68A;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .mid-row {{
    display: grid;
    grid-template-columns: 468px 450px;
    grid-template-rows: 1fr;
    gap: 24px;
    height: 632px;
    min-height: 0;
    align-items: stretch;
  }}
  .glass-card {{
    position: relative;
    background: rgba(255, 255, 255, 0.06);
    border: 1.5px solid rgba(255, 255, 255, 0.14);
    border-radius: 28px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
    min-height: 0;
    overflow: hidden;
  }}
  .g-title {{
    font-size: 28px;
    font-weight: 800;
    color: #E4E4E7;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .g-title span.tag {{
    font-size: 20px;
    color: #FCA5A5;
    background: rgba(220, 38, 38, 0.22);
    padding: 5px 12px;
    border-radius: 999px;
    border: 1px solid rgba(248, 113, 113, 0.38);
  }}
  .layers {{
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}
  .layer-row {{
    background: rgba(18, 20, 24, 0.72);
    border: 1.5px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    padding: 15px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .layer-row b {{
    font-size: 25px;
    color: #FAFAF8;
  }}
  .layer-row small {{
    font-size: 21px;
    color: #F87171;
    font-weight: 700;
  }}
  .bypass-stamp {{
    position: absolute;
    right: 22px;
    top: 342px;
    border: 4.5px solid #EF4444;
    color: #EF4444;
    background: rgba(18, 20, 24, 0.94);
    font-size: 32px;
    font-weight: 900;
    padding: 7px 18px;
    border-radius: 12px;
    transform: rotate(-10deg);
    box-shadow: 0 10px 22px rgba(0, 0, 0, 0.48);
    letter-spacing: 0.04em;
    z-index: 5;
  }}
  .moto-dark-box {{
    background: #F5F1E8;
    border-radius: 20px;
    padding: 12px 14px 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  .moto-dark-box .moto-svg {{
    width: 240px;
    height: 132px;
  }}
  .moto-cap {{
    font-size: 20px;
    font-weight: 800;
    color: #18181B;
    margin-top: 4px;
    white-space: nowrap;
  }}
  .polaroid {{
    background: #FAFAF8;
    border-radius: 26px;
    padding: 16px 16px 20px;
    color: #18181B;
    transform: rotate(-1.5deg);
    box-shadow: 0 32px 60px -20px rgba(0, 0, 0, 0.72);
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
    overflow: hidden;
  }}
  .polaroid-img {{
    position: relative;
    flex: 1;
    min-height: 0;
    border-radius: 18px;
    overflow: hidden;
    background: #E4E4E7;
  }}
  .polaroid-img img {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: 50% 60%;
    transform: scale(1.24);
    transform-origin: 50% 64%;
    display: block;
  }}
  .polaroid-cap {{
    margin-top: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 25px;
    font-weight: 800;
    color: #18181B;
  }}
  .polaroid-cap small {{
    font-size: 20px;
    color: #52525B;
    font-weight: 700;
  }}
  .bottom-pills {{
    display: flex;
    gap: 16px;
  }}
  .nav-pill-dark {{
    flex: 1;
    text-align: center;
    padding: 18px 12px;
    background: rgba(255, 255, 255, 0.08);
    border: 1.5px solid rgba(255, 255, 255, 0.16);
    border-radius: 20px;
    font-size: 27px;
    font-weight: 800;
    color: #FAFAF8;
  }}
</style>
</head>
<body>
<div class="canvas">
  <div class="grid-bg"></div>
  <div class="safe">
    <div class="eyebrow-row">
      <div class="pill-dark"><span class="dot"></span>AI 硬核科普 · 第一期</div>
      <div class="pill-time">97s 深度拆解</div>
    </div>

    <div>
      <div class="h1-w">硅谷 800 层风控</div>
      <div class="h1-c">败给一辆<em>小摩托</em></div>
    </div>

    <div class="egg-banner">★ 全片零剪映 · 2924 帧全是克劳德写代码生成</div>

    <div class="mid-row">
      <div class="glass-card">
        <div class="g-title">三层防线拦截<span class="tag">已突破</span></div>
        <div class="layers">
          <div class="layer-row"><b>01 · 出口 IP 封锁</b><small>拦截</small></div>
          <div class="layer-row"><b>02 · 环境指纹交叉比对</b><small>预警</small></div>
          <div class="layer-row"><b>03 · 真人实名与号码核验</b><small>校验</small></div>
        </div>
        <div class="bypass-stamp">物理破防</div>
        <div class="moto-dark-box">
          {MOTO_SVG}
          <div class="moto-cap">成本对比：实体机 ¥2500+ vs 云端轻方案</div>
        </div>
      </div>

      <div class="polaroid">
        <div class="polaroid-img">
          <img id="indo-img" src="data:image/jpeg;base64,{B64_INDO}" alt="" />
        </div>
        <div class="polaroid-cap">
          <span>📍 苏门答腊 · 1500km</span>
          <small>实拍已打码</small>
        </div>
      </div>
    </div>

    <div class="bottom-pills">
      <div class="nav-pill-dark">真实成本账单</div>
      <div class="nav-pill-dark">代码渲染原理</div>
      <div class="nav-pill-dark">云端工位架构</div>
    </div>
  </div>
</div>
<script>
window.render = function () {{}};
window.ready = false;
Promise.all([
  document.fonts ? document.fonts.ready : Promise.resolve(),
  document.getElementById('indo-img').decode().catch(() => {{}})
]).then(() => {{ window.ready = true; }});
</script>
</body>
</html>
"""


FORBIDDEN = ["代理", "机场", "节点", "梯子", "收号", "下载", "微信", "朋友圈"]


def verify_compliance(html_str: str, label: str):
    no_style = re.sub(r"<style>.*?</style>", "", html_str, flags=re.S)
    no_script = re.sub(r"<script>.*?</script>", "", no_style, flags=re.S)
    visible = re.sub(r"<[^>]+>", " ", no_script)
    for bad in FORBIDDEN:
        assert bad not in visible, f"{label} 出现违规词：{bad}"
    assert not re.search(r"claude", visible, re.I), f"{label} 可见文案出现英文 Claude"
    assert not re.search(r"https?://|www\.|codedeck\.top|[A-Za-z0-9-]\.(?:com|cn|net|io)\b", visible), f"{label} 出现网址或域名"


def main():
    v1 = render_v1()
    v2 = render_v2()
    verify_compliance(v1, "cover_v1")
    verify_compliance(v2, "cover_v2")
    (QA / "cover_v1.html").write_text(v1, encoding="utf-8")
    (QA / "cover_v2.html").write_text(v2, encoding="utf-8")
    print("Wrote qa/cover_v1.html and qa/cover_v2.html (compliance checks passed)")


if __name__ == "__main__":
    main()
