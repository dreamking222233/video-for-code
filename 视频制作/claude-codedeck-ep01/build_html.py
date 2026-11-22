#!/usr/bin/env python3
"""EP01 渲染页（v2 · 官网设计语言版）。

把 audio/vo_timeline.json 注入单文件离线 index.html，页面暴露 window.render(t)。

v2 改动：整片换成 CodeDeck 官网的视觉语言——浅色纸面、细分隔线、柔和叠层阴影、
大圆角卡片、紧字距无衬线大标题、带绿点的 eyebrow 胶囊、官网同款线性图标。
第 5/6 镜按官网示意图重建：痛点卡 → Hero → 对比 → 连接路线 → 五地区地球
（复用官网陆地点阵数据）→ 启动器 / 审批 / 全天候时间线 / 安全 → 桌面端 + 手机主视觉 → CTA。

素材：source/asset_indo_hd.jpg、source/asset_moments_hd.jpg、source/globe_land.b64
红线：页面里不出现任何网址或域名，只出现「CodeDeck」。
"""
import base64, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "source"

b64_indo = base64.b64encode((SRC / "asset_indo_hd.jpg").read_bytes()).decode("ascii")
b64_moments = base64.b64encode((SRC / "asset_moments_hd.jpg").read_bytes()).decode("ascii")
globe_b64 = (SRC / "globe_land.b64").read_text(encoding="utf-8").strip()


# ---------------------------------------------------------------- 组件（Python 侧拼 HTML）
def ico(name, cls="i"):
    return f'<svg class="{cls}"><use href="#i-{name}"/></svg>'


LOGO = '<svg class="logo" viewBox="0 0 64 64"><use href="#cd-logo"/></svg>'
CLAUDE = f'<span class="claude-mark">{ico("asterisk")}</span>'


def app_window(wid, fs, tab, side, title, sub, chat, mode="默认模式", ctx="上下文 15.5%"):
    return f'''
<div class="app" id="{wid}" style="font-size:{fs}px">
  <div class="app-bar"><span class="lights"><i></i><i></i><i></i></span>
    <div class="app-tabs">
      <span class="app-tab">{ico("home")}启动器</span>
      <span class="app-tab on"><span class="live"></span>{tab}<span class="x">×</span></span>
      <span class="app-tab">本机<span class="x">×</span></span>
    </div>
  </div>
  <div class="app-body">
    <div class="side">
      <div class="side-head">{LOGO}<div><b>CodeDeck</b><small>root@sg-01</small></div></div>
      <div class="side-search">{ico("search")}搜索会话、文件<kbd>⌘K</kbd></div>
      {side}
      <div class="side-new">{ico("plus")}新建会话</div>
    </div>
    <div class="app-main">
      <div class="main-head"><div><b>{title}</b><small>{sub}</small></div>
        <div class="seg"><span class="on">聊天</span><span>终端</span><span>文件</span><span>源代码管理</span><span>任务</span></div>
      </div>
      <div class="chat">{chat}</div>
      <div class="composer"><div class="ph">输入 / 调用命令，@ 选择文件，或向 Claude 提问…</div>
        <div class="composer-row"><span class="chip"><i class="d"></i>{mode}</span><span class="chip">Opus · 高</span><span class="chip">{ctx}</span><span class="send">{ico("up")}</span></div>
      </div>
    </div>
  </div>
</div>'''


def side_projects(items):
    out = []
    for name, path, sess in items:
        rows = "".join(
            f'<div class="sess{" on" if on else ""}">{"<span class=spin></span>" if run else ""}'
            f'<span class="t">{t}</span><small>{"运行中" if run else when}</small></div>'
            for t, when, run, on in sess)
        out.append(f'<div class="proj"><div class="proj-row">{ico("folder")}{name}<small>{path}</small></div>{rows}</div>')
    return "".join(out)


def phone(pid, fs, notif_id, notif_title, notif_body, chat_title, chat):
    return f'''
<div class="phone" id="{pid}" style="font-size:{fs}px">
  <div class="phone-screen">
    <div class="phone-island"></div>
    <div class="phone-status"><span>05:00</span><span class="bars"><i style="height:.45em"></i><i style="height:.65em"></i><i style="height:.85em"></i><i style="height:1.05em"></i></span></div>
    <div class="notif" id="{notif_id}">{LOGO}<div class="notif-body"><div class="notif-top"><span>CodeDeck</span><span>现在</span></div><b>{notif_title}</b><p>{notif_body}</p></div></div>
    <div class="phone-title">{ico("chat")}{chat_title}</div>
    <div class="phone-chat">{chat}</div>
    <div class="phone-nav"><span class="on">{ico("chat")}聊天</span><span>{ico("terminal")}终端</span><span>{ico("folder")}文件</span><span>{ico("branch")}Git</span><span>{ico("board")}任务</span></div>
  </div>
</div>'''


# 第 4 镜：Claude 正在做这条视频
APP_S4 = app_window(
    "s4-app", 19, "新加坡 · 主力机",
    side_projects([
        ("video-for-code", "~/video", [("做 EP01 动画视频", "", True, True), ("配音音色对比", "昨天", False, False)]),
        ("shop", "~/shop", [("给登录页加 Google 登录", "2 小时前", False, False)]),
        ("blog", "~/blog", []),
    ]),
    "做 EP01 动画视频", "video-for-code · Claude Code",
    f'''
<div class="bubble-user" id="s4-ask">把第一期素材做成动画视频：旁白、配乐、字幕都要</div>
<div class="ai" id="s4-ai">
  <div class="ai-head">{CLAUDE}Claude<small>Opus</small></div>
  <p>好，我先读素材，再写渲染页、配乐和母带脚本。</p>
  <div class="tools">
    <div id="s4-t1"><span class="ok">●</span><b>Read</b><span class="p">素材稿件/第一期素材制作.md</span><span class="m">62 行</span></div>
    <div id="s4-t2"><span class="ok">●</span><b>Write</b><span class="p">build_html.py</span><span class="m add">+1,640</span></div>
    <div id="s4-t3"><span class="ok">●</span><b>Bash</b><span class="p">python3 audio/synth_mix.py</span><span class="m">120 BPM</span></div>
    <div id="s4-t4"><span class="ok">●</span><b>Bash</b><span class="p">render.py index.html → final.mp4</span><span class="m">30fps</span></div>
  </div>
</div>
<div class="render-box" id="s4-render">
  <div class="rb-top"><span class="rec"></span><b>正在渲染</b><span class="mono" id="s4-frame">第 0000 / 2753 帧</span></div>
  <div class="rb-bar"><span id="s4-rbar"></span></div>
  <div class="rb-foot mono" id="s4-call">window.render(0.00)</div>
</div>
<div class="here-chip" id="s4-here">{ico("up")}就是你此刻看到的这一帧</div>''',
    mode="编辑模式")

# 第 6 镜：一键连上 + 每一步由你审批
APP_S6 = app_window(
    "s6-app", 19, "新加坡 · 主力机",
    side_projects([
        ("shop", "~/shop", [("给登录页加 Google 登录", "", True, True), ("CSV 导入改成流式处理", "2 小时前", False, False)]),
        ("api-gateway", "~/api", [("限流中间件改成令牌桶", "", True, False)]),
        ("blog", "~/blog", []),
    ]),
    "给登录页加 Google 登录", "shop · Claude Code",
    f'''
<div class="bubble-user">给登录页加上 Google 登录，然后跑一遍测试</div>
<div class="ai">
  <div class="ai-head">{CLAUDE}Claude<small>Opus</small></div>
  <p>我先看一下现有的登录流程，再接上 OAuth 回调。</p>
  <div class="tools">
    <div id="s6-t1"><span class="ok">●</span><b>Read</b><span class="p">src/pages/login.tsx</span><span class="m">84 行</span></div>
    <div id="s6-t2"><span class="ok">●</span><b>Write</b><span class="p">src/lib/oauth.ts</span><span class="m add">+64</span></div>
    <div id="s6-t3"><span class="ok">●</span><b>Edit</b><span class="p">src/pages/login.tsx</span><span class="m"><span class="add">+18</span> <span class="del">−2</span></span></div>
    <div id="s6-t4"><span class="ok">●</span><b>Bash</b><span class="p">npm test</span><span class="m add">42 passed</span></div>
  </div>
  <p id="s6-done">完成：登录页已支持 Google 登录，42 个测试全部通过。</p>
</div>
<div class="perm" id="s6-perm">
  <div class="perm-head"><span class="perm-ico">!</span><div><b>Claude 请求运行 Bash</b><code>npm test</code><p class="perm-rule">执行位置：root@sg-01（你的服务器）· 不碰你的电脑</p></div></div>
  <div class="perm-actions"><span class="pbtn">拒绝</span><span class="pbtn">允许并记住</span><span class="pbtn pri" id="s6-allow">允许一次</span></div>
</div>''')

# 主视觉：桌面端 + 手机
APP_HERO = app_window(
    "hero-app", 15, "新加坡 · 主力机",
    side_projects([
        ("shop", "~/shop", [("给登录页加 Google 登录", "", True, True), ("CSV 导入改成流式处理", "2 小时前", False, False), ("补齐支付模块单测", "昨天", False, False)]),
        ("api-gateway", "~/api-gateway", [("限流中间件改成令牌桶", "", True, False)]),
        ("blog", "~/blog", []),
    ]),
    "给登录页加 Google 登录", "shop · Claude Code",
    f'''
<div class="bubble-user">给登录页加上 Google 登录，然后跑一遍测试</div>
<div class="ai">
  <div class="ai-head">{CLAUDE}Claude<small>Opus</small></div>
  <p>我先看一下现有的登录流程，再接上 OAuth 回调。</p>
  <div class="tools">
    <div><span class="ok">●</span><b>Read</b><span class="p">src/pages/login.tsx</span><span class="m">84 行</span></div>
    <div><span class="ok">●</span><b>Write</b><span class="p">src/lib/oauth.ts</span><span class="m add">+64</span></div>
    <div><span class="ok">●</span><b>Edit</b><span class="p">src/pages/login.tsx</span><span class="m"><span class="add">+18</span> <span class="del">−2</span></span></div>
    <div><span class="ok">●</span><b>Bash</b><span class="p">npm test</span><span class="m">42 passed</span></div>
  </div>
  <p>完成：登录页已支持 Google 登录，42 个测试全部通过。</p>
</div>''', mode="计划模式")

PHONE_TL = phone("tl-phone", 15, "tl-notif", "任务完成", "重构订单模块：42 个测试全部通过，已推送",
                 "重构订单模块",
                 f'<div class="bubble-user">跑完回归就推送</div><div class="ai"><div class="ai-head">{CLAUDE}Claude</div>'
                 '<div class="tools"><div><span class="ok">●</span><b>Bash</b><span class="p">npm test</span></div>'
                 '<div><span class="ok">●</span><span class="p">42 passed</span></div>'
                 '<div><span class="ok">●</span><b>Bash</b><span class="p">git push</span></div></div></div>')

PHONE_HERO = phone("hero-phone", 12, "hero-notif", "任务完成", "给登录页加 Google 登录：42 个测试全部通过",
                   "给登录页加 Google 登录",
                   f'<div class="bubble-user">合并前再跑一遍 lint</div><div class="ai"><div class="ai-head">{CLAUDE}Claude</div>'
                   '<div class="tools"><div><span class="ok">●</span><b>Bash</b><span class="p">npm run lint</span></div>'
                   '<div><span class="ok">●</span><span class="p">0 errors, 0 warnings</span></div></div></div>')


HTML_TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<title>如何在国内稳定使用 Claude · CodeDeck 第一期</title>
<style>
:root{
  --ink:#18181b; --ink-soft:#3f3f46; --muted:#6a6a73; --muted-light:#a1a1aa;
  --rule:#e7e7e3; --rule-strong:#d4d4d0; --paper:#f4f4f0; --paper-warm:#faf9f5;
  --accent:#10b981; --accent-ink:#047857; --accent-soft:rgba(16,185,129,.16);
  --claude:#d97757; --red:#dc2626;
  --shadow-card:0 0 0 1px rgba(0,0,0,.06),0 1px 1px -.5px rgba(0,0,0,.06),0 3px 3px -1.5px rgba(0,0,0,.06),0 6px 6px -3px rgba(0,0,0,.04),0 12px 12px -6px rgba(0,0,0,.03),0 24px 48px -24px rgba(0,0,0,.08);
  --shadow-float:0 40px 80px -36px rgba(15,18,30,.38),0 0 0 1px rgba(15,18,30,.06);
  --sans:-apple-system,"SF Pro Text","Inter","PingFang SC","Noto Sans CJK SC","Hiragino Sans GB","Microsoft YaHei",sans-serif,"Apple Color Emoji","Noto Color Emoji";
  --mono:"SF Mono","JetBrains Mono",Menlo,Consolas,"PingFang SC","Noto Sans CJK SC",monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
ul{list-style:none}
html,body{width:1920px;height:1080px;overflow:hidden;background:#F3F3EF;color:var(--ink);font-family:var(--sans);-webkit-font-smoothing:antialiased;user-select:none}
.mono{font-family:var(--mono)}
.i{width:1em;height:1em;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;flex-shrink:0;display:inline-block;vertical-align:middle}
.logo{display:block;flex-shrink:0}

#viewport{position:relative;width:1920px;height:1080px;overflow:hidden;
  background:radial-gradient(1500px 820px at 50% -18%,#ffffff 0%,rgba(255,255,255,0) 72%),#F1F1EC}
#bg-grid{position:absolute;inset:0;pointer-events:none;
  background-image:linear-gradient(rgba(24,24,27,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(24,24,27,.035) 1px,transparent 1px);
  background-size:64px 64px;background-position:31px 31px;
  -webkit-mask-image:radial-gradient(ellipse 72% 62% at 50% 46%,#000 25%,transparent 88%)}

/* ---------------- 顶栏 ---------------- */
#topbar{position:absolute;left:72px;right:72px;top:0;height:100px;z-index:30;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--rule)}
.tb-brand{display:flex;align-items:center;gap:14px;font-size:25px}
.tb-brand .logo{width:42px;height:42px;border-radius:11px;box-shadow:0 6px 14px -6px rgba(7,87,206,.55)}
.tb-brand b{font-weight:700;letter-spacing:-.01em}
.tb-sep{width:1px;height:24px;background:var(--rule-strong);margin:0 4px}
.tb-ep{color:var(--muted);font-size:21px;font-weight:500}
.tb-right{display:flex;align-items:center;gap:24px}
.tb-chap{display:inline-flex;align-items:center;gap:11px;padding:8px 18px 8px 16px;border-radius:999px;background:#fff;border:1px solid var(--rule);font-size:20px;font-weight:600;color:var(--ink-soft);box-shadow:0 1px 2px rgba(0,0,0,.04)}
.tb-prog{display:flex;gap:6px}
.tb-seg{width:38px;height:5px;border-radius:99px;background:rgba(24,24,27,.1);overflow:hidden}
.tb-seg i{display:block;height:100%;width:0;border-radius:99px;background:var(--ink)}
#tb-tc{font-family:var(--mono);font-size:19px;color:var(--muted)}

/* ---------------- 通用 ---------------- */
.scene{position:absolute;left:96px;top:132px;width:1728px;height:812px;display:none;z-index:10}
.abs{position:absolute}
.eyebrow{display:inline-flex;align-items:center;gap:12px;padding:9px 20px;border-radius:999px;border:1px solid var(--rule);background:#fff;color:var(--ink-soft);font-size:22px;font-weight:600;white-space:nowrap;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.pip{display:inline-block;width:10px;height:10px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 4px var(--accent-soft);flex-shrink:0}
.pip.red{background:#ef4444;box-shadow:0 0 0 4px rgba(239,68,68,.16)}
.pip.orange{background:var(--claude);box-shadow:0 0 0 4px rgba(217,119,87,.18)}
.pip.gray{background:#a1a1aa;box-shadow:0 0 0 4px rgba(161,161,170,.18)}
.display{color:#262626;font-weight:700;letter-spacing:-.035em;line-height:1.14;font-size:72px;word-break:keep-all}
.display em{font-style:normal}
.hl-green{color:var(--accent-ink)} .hl-claude{color:var(--claude)} .hl-red{color:var(--red)}
.card{background:#fff;border-radius:24px;box-shadow:var(--shadow-card)}
.card-b{background:#fff;border-radius:24px;border:1px solid var(--rule)}
.tile{display:grid;place-items:center;width:60px;height:60px;border-radius:17px;background:var(--paper);font-size:30px;color:var(--ink);flex-shrink:0}
.tile.green{background:#ecfdf5;color:var(--accent-ink)}
.tile.red{background:#fef2f2;color:var(--red)}
.tile.ink{background:var(--ink);color:#fff}
.tile.claude{background:#fdf1ec;color:var(--claude)}
.claude-mark{display:inline-grid;place-items:center;width:1.6em;height:1.6em;border-radius:.42em;background:var(--claude);color:#fff;flex-shrink:0}
.claude-mark .i{width:.95em;height:.95em;stroke-width:2.4}
.chipx{display:inline-flex;align-items:center;gap:8px;padding:7px 15px;border-radius:999px;border:1px solid var(--rule);background:#fafaf8;color:var(--ink-soft);font-size:19px;font-weight:500;white-space:nowrap}
.chipx .i{font-size:18px}
.chipx.ok{background:#ecfdf5;border-color:rgba(16,185,129,.35);color:var(--accent-ink)}
.chipx.bad{background:#fef2f2;border-color:rgba(220,38,38,.25);color:var(--red)}
.chipx.dark{background:var(--ink);border-color:var(--ink);color:#fff}
.swap{position:relative;display:block;overflow:hidden;padding-bottom:.08em}
.swap>span{display:block;white-space:nowrap}
.swap>span+span{position:absolute;left:0;top:0}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:12px;height:68px;padding:0 36px;border-radius:999px;font-size:25px;font-weight:600;white-space:nowrap}
.btn-white{background:#fff;color:var(--ink)}
.btn-glass{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.22)}
.btn-ink{background:var(--ink);color:#fff}
.lights{display:flex;gap:.5em;flex-shrink:0}
.lights i{width:.85em;height:.85em;border-radius:50%;background:#ff5f57}
.lights i:nth-child(2){background:#febc2e}.lights i:nth-child(3){background:#28c840}
.spin{flex-shrink:0;width:.85em;height:.85em;border-radius:50%;border:.16em solid rgba(16,185,129,.25);border-top-color:var(--accent)}

/* mini 预览（官网痛点卡同款） */
.mini{width:100%;padding:20px 22px;border-radius:18px;font-size:19px;line-height:1.65}
.mini-dark{background:#1a1d26;color:rgba(255,255,255,.82);font-family:var(--mono);box-shadow:0 18px 36px -18px rgba(26,29,38,.8)}
.mini-navy{background:#0c2a4d;color:rgba(255,255,255,.86);font-family:var(--mono);box-shadow:0 18px 36px -18px rgba(12,42,77,.8)}
.mini-light{background:#fff;border:1px solid var(--rule);box-shadow:0 14px 30px -18px rgba(26,29,38,.3)}
.mini .dim{color:rgba(255,255,255,.45)} .mini .err{color:#ff8a8a} .mini .okc{color:#6ee7b7}
.mini-head{display:flex;align-items:center;gap:8px;margin-bottom:10px;font-size:18px;font-weight:600;color:var(--muted)}
.mini-list li{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:18px;color:var(--ink-soft)}
.mini-list li+li{margin-top:6px}
.mini-list li b{margin-left:auto;font-weight:600}
.mini-progress{display:flex;height:8px;margin-top:12px;overflow:hidden;border-radius:999px;background:rgba(255,255,255,.1)}
.mini-progress span{width:60%;background:rgba(255,255,255,.35)}

/* ---------------- 第 1 镜：风控 vs 小摩托 ---------------- */
.s1-head{position:absolute;left:0;top:0;width:1220px}
.s1-head .display{margin-top:24px;font-size:70px}
.s1-meter{position:absolute;right:0;top:4px;width:440px;padding:24px 28px 22px}
.m-lbl{display:flex;align-items:center;gap:11px;font-size:20px;font-weight:600;color:var(--ink-soft)}
.m-lbl .st{margin-left:auto}
.chipx.dark.st{background:var(--ink)}
.m-num{margin-top:10px;display:flex;align-items:baseline;gap:10px;font-family:var(--mono);font-size:88px;font-weight:700;letter-spacing:-.04em;line-height:1;color:var(--ink)}
.m-num small{font-family:var(--sans);font-size:28px;font-weight:600;color:var(--muted);letter-spacing:0}
.m-bar{margin-top:18px;height:10px;border-radius:99px;background:var(--paper);overflow:hidden}
.m-bar span{display:block;height:100%;width:0;border-radius:99px;background:linear-gradient(90deg,#f59e0b,#ef4444)}
.m-foot{margin-top:14px;display:flex;align-items:center;gap:10px;font-size:20px;color:var(--muted)}
.m-foot b{color:var(--red);font-weight:700}
.s1-wall{position:absolute;left:0;right:0;top:300px;height:488px;display:grid;grid-template-columns:repeat(3,1fr);gap:32px}
.s1-card{position:relative;padding:28px 28px 26px;display:flex;flex-direction:column}
.s1-card .row{display:flex;align-items:center;gap:16px}
.s1-card .tag{font-family:var(--mono);font-size:18px;color:var(--muted);letter-spacing:.06em}
.s1-card .row .chipx{margin-left:auto}
.s1-card h3{margin-top:20px;font-size:36px;font-weight:700;letter-spacing:-.02em}
.s1-card p{margin-top:6px;font-size:22px;line-height:1.55;color:var(--muted)}
.s1-card .prev{margin-top:auto;height:178px;border-radius:18px;background:var(--paper);display:flex;align-items:center;padding:0 20px}
.kyc{display:flex;align-items:center;gap:20px}
.kyc-face{position:relative;width:104px;height:104px;border-radius:22px;background:#f4f4f0;color:#71717a;display:grid;place-items:center;font-size:76px;overflow:hidden;flex-shrink:0}
.kyc-face .scan{position:absolute;left:8px;right:8px;height:3px;border-radius:2px;background:#ef4444;box-shadow:0 0 10px rgba(239,68,68,.7)}
.kyc b{display:block;font-size:22px}
.kyc small{display:block;margin-top:4px;font-size:18px;color:var(--muted)}
.s1-ring{position:absolute;inset:-2px;border-radius:26px;box-shadow:0 0 0 3px rgba(239,68,68,.55);pointer-events:none;opacity:0}
#s1-canvas{position:absolute;left:-96px;top:0;width:1920px;height:812px;pointer-events:none;z-index:6}
.s1-stamp{position:absolute;left:864px;top:520px;z-index:8;padding:6px 44px 10px;border:9px solid var(--red);border-radius:30px;color:var(--red);background:rgba(255,255,255,.92);font-size:128px;font-weight:900;letter-spacing:.06em;white-space:nowrap;box-shadow:var(--shadow-float)}
.s1-stamp small{display:block;margin-top:-6px;text-align:center;font-family:var(--mono);font-size:24px;font-weight:700;letter-spacing:.3em}

/* ---------------- 第 2 镜：摩旅 1500km ---------------- */
.s2-left{position:absolute;left:0;top:0;width:948px;height:812px}
.s2-left .display{margin-top:22px;font-size:66px}
.s2-stack{position:absolute;left:0;top:262px;width:948px;height:550px}
.map-card{position:absolute;inset:0;padding:22px 26px 20px;border-radius:28px}
.map-head{display:flex;align-items:center;justify-content:space-between}
.map-title{display:flex;align-items:center;gap:12px;font-size:22px;font-weight:600}
.map-dist{font-family:var(--mono);font-size:22px;font-weight:700;color:var(--accent-ink);background:#ecfdf5;padding:6px 16px;border-radius:999px}
.globe-box{position:relative;margin-top:16px;height:390px;border-radius:20px;overflow:hidden;background:radial-gradient(circle at 50% 50%,#fff 0%,#fbfbfb 62%,#f4f4f5 100%)}
.globe-box canvas{position:absolute;inset:0;width:100%;height:100%}
.map-foot{display:flex;gap:12px;margin-top:16px}
.acct-card{position:absolute;inset:0;padding:24px 28px;border-radius:28px}
.ac-head{display:flex;align-items:center;gap:20px;padding-bottom:16px;border-bottom:1px solid var(--rule)}
.ac-av{display:grid;place-items:center;width:72px;height:72px;border-radius:20px;background:#fdf1ec;font-size:42px}
.ac-head b{display:block;font-size:30px;font-weight:700;letter-spacing:-.01em}
.ac-head small{display:block;margin-top:4px;font-size:21px;color:var(--muted)}
.ac-head .chipx{margin-left:auto}
.ac-lbl{margin-top:14px;font-size:19px;font-weight:600;color:var(--muted)}
.ac-row{display:flex;align-items:center;gap:16px;margin-top:10px;padding:10px 16px;border-radius:18px;border:1px solid var(--rule);font-size:20px}
.ac-row .claude-mark{font-size:22px}
.ac-row b{display:block;font-size:22px;font-weight:600}
.ac-row small{display:block;font-family:var(--mono);font-size:16px;color:var(--muted)}
.ac-row .st{margin-left:auto;display:flex;align-items:center;gap:8px;font-size:19px;color:var(--accent-ink);font-weight:600}
.ac-foot{position:absolute;left:28px;right:28px;bottom:22px;display:flex;align-items:center;justify-content:center;gap:12px;height:60px;border-radius:18px;background:var(--ink);color:#fff;font-size:26px;font-weight:700}
.ac-foot em{font-style:normal;color:#fcd34d}
.s2-right{position:absolute;left:1000px;top:0;width:728px;height:812px}
.photo-card{position:absolute;left:150px;top:0;width:448px;padding:16px 16px 0;border-radius:26px;background:#fff;box-shadow:var(--shadow-float)}
.ph-img{position:relative;width:416px;height:735px;border-radius:16px;overflow:hidden;background:#18181b}
.ph-zoom{position:absolute;inset:0;transform-origin:52.5% 60.5%}
.ph-zoom img{display:block;width:100%;height:100%;object-fit:cover}
.ph-hl{position:absolute;left:37.4%;top:53.6%;width:30.4%;height:13.8%;border-radius:10px;border:4px solid var(--claude);box-shadow:0 0 0 2000px rgba(10,10,12,.38)}
.ph-cap{display:flex;align-items:center;justify-content:space-between;height:60px;font-size:20px;font-weight:600;color:var(--ink-soft)}
.ph-cap .chipx{font-size:17px;padding:5px 12px}
.quote-card{position:absolute;left:-8px;top:500px;width:430px;padding:22px 26px;border-radius:22px;background:#fff;box-shadow:var(--shadow-float)}
.quote-card .q-lbl{display:flex;align-items:center;gap:10px;font-size:18px;font-weight:600;color:var(--muted)}
.quote-card .q{margin-top:10px;font-size:34px;font-weight:700;line-height:1.3;letter-spacing:-.01em}
.quote-card .q em{font-style:normal;color:var(--red)}

/* ---------------- 第 3 镜：算账 ---------------- */
.s3-left{position:absolute;left:0;top:0;width:651px;height:812px}
.shot-win{position:absolute;inset:0;border-radius:22px;overflow:hidden;background:#fafafa;box-shadow:var(--shadow-float)}
.shot-win img{position:absolute;left:0;top:0;width:100%;height:100%;display:block;transform-origin:40% 30%}
.s3-src{position:absolute;left:24px;bottom:22px}
.callout{position:absolute;display:flex;align-items:center;gap:0;white-space:nowrap}
.callout .dot{width:16px;height:16px;border-radius:50%;background:var(--claude);box-shadow:0 0 0 6px rgba(217,119,87,.25);flex-shrink:0}
.callout .ln{width:44px;height:2px;background:var(--ink)}
.callout .bx{padding:10px 18px;border-radius:14px;background:var(--ink);color:#fff;font-size:22px;font-weight:600;box-shadow:0 14px 28px -14px rgba(0,0,0,.5)}
.callout .bx small{display:block;font-family:var(--mono);font-size:16px;color:#fcd34d;font-weight:500}
.s3-right{position:absolute;left:720px;top:0;width:1008px;height:812px}
.s3-right .display{margin-top:22px;font-size:66px}
.bill{position:absolute;left:0;right:0;top:262px;bottom:0;padding:26px 30px 24px;border-radius:28px}
.bill-head{display:flex;align-items:center;justify-content:space-between;font-size:20px;font-weight:600;color:var(--muted);padding-bottom:16px;border-bottom:1px dashed var(--rule-strong)}
.bill-row{display:flex;align-items:center;gap:20px;padding:15px 0;border-bottom:1px solid #f0f0ec}
.bill-row b{display:block;font-size:28px;font-weight:700;letter-spacing:-.01em}
.bill-row small{display:block;margin-top:2px;font-size:19px;color:var(--muted)}
.bill-row .pr{margin-left:auto;text-align:right}
.bill-row .usd{font-family:var(--mono);font-size:40px;font-weight:700;letter-spacing:-.03em;color:var(--ink)}
.bill-row .usd span{font-family:var(--sans);font-size:20px;font-weight:600;color:var(--muted);margin-left:4px;letter-spacing:0}
.bill-row .cny{font-family:var(--mono);font-size:20px;color:var(--red);font-weight:600}
.bill-total{position:absolute;left:30px;right:30px;bottom:24px;display:flex;align-items:center;justify-content:space-between;padding:20px 26px;border-radius:20px;background:#fef2f2}
.bill-total .lb b{display:block;font-size:28px;font-weight:700}
.bill-total .lb small{display:block;font-size:19px;color:#b91c1c}
.bill-total .v{font-family:var(--mono);font-size:58px;font-weight:700;letter-spacing:-.04em;color:var(--red)}
.stamp{position:absolute;right:26px;top:-38px;padding:6px 26px;border:6px solid var(--red);border-radius:18px;color:var(--red);background:rgba(255,255,255,.94);font-size:44px;font-weight:900;letter-spacing:.08em;box-shadow:0 16px 32px -16px rgba(220,38,38,.45)}

/* ---------------- 第 4 镜：为什么是 Claude ---------------- */
.s4-head{position:absolute;left:0;top:0;width:1728px}
.s4-head .display{margin-top:22px;font-size:64px}
.s4-left{position:absolute;left:0;top:186px;width:640px;height:626px;display:flex;flex-direction:column;gap:20px}
.cap{flex:1;display:flex;gap:22px;padding:24px 26px;border-radius:24px}
.cap h3{font-size:31px;font-weight:700;letter-spacing:-.015em}
.cap p{margin-top:4px;font-size:21px;color:var(--muted);line-height:1.5}
.cap code{display:inline-block;margin-top:12px;padding:5px 12px;border-radius:10px;background:var(--paper);font-family:var(--mono);font-size:18px;color:var(--accent-ink)}
.cap.feat{background:#1a1d26;box-shadow:0 30px 60px -30px rgba(26,29,38,.7)}
.cap.feat h3{color:#fff}.cap.feat p{color:#a1a1aa}
.cap.feat code{background:rgba(255,255,255,.08);color:#fdba74}
.s4-right{position:absolute;left:688px;top:186px;width:1040px;height:626px}
.render-box{margin-top:2px;padding:14px 18px;border-radius:.8em;background:#1a1d26;color:#e4e4e7}
.rb-top{display:flex;align-items:center;gap:12px;font-size:.92em}
.rb-top .rec{width:12px;height:12px;border-radius:50%;background:#ef4444;box-shadow:0 0 10px #ef4444}
.rb-top .mono{margin-left:auto;color:#fcd34d}
.rb-bar{margin-top:10px;height:8px;border-radius:99px;background:rgba(255,255,255,.1);overflow:hidden}
.rb-bar span{display:block;height:100%;width:0;background:linear-gradient(90deg,#10b981,#34d399)}
.rb-foot{margin-top:8px;font-size:.78em;color:#a1a1aa}
.here-chip{align-self:flex-start;display:inline-flex;align-items:center;gap:8px;padding:.35em .8em;border-radius:999px;background:#ecfdf5;color:var(--accent-ink);font-weight:700;font-size:.9em;border:1px solid rgba(16,185,129,.4)}

/* ---------------- 应用窗口（官网 Hero 同款，em 缩放） ---------------- */
.app{position:relative;display:flex;flex-direction:column;overflow:hidden;border-radius:.95em;background:#fff;line-height:1.3;color:var(--ink);box-shadow:0 1.6em 4em -.6em rgba(15,18,30,.32),0 0 0 .5px rgba(0,0,0,.2)}
.app-bar{flex-shrink:0;display:flex;align-items:center;gap:1em;height:2.7em;padding:0 .9em;background:#f3f3f1;border-bottom:1px solid #e6e6e2}
.app-tabs{display:flex;align-items:flex-end;align-self:stretch;gap:.3em;padding-top:.5em;min-width:0}
.app-tab{display:flex;align-items:center;gap:.45em;padding:0 .9em;border-radius:.55em .55em 0 0;font-size:.84em;color:#6b6b73;white-space:nowrap;height:100%}
.app-tab.on{background:#fff;color:var(--ink);font-weight:500;box-shadow:0 0 0 1px #e6e6e2}
.app-tab .live{width:.5em;height:.5em;border-radius:50%;background:var(--accent)}
.app-tab .x{color:#a1a1aa;margin-left:.15em}
.app-body{flex:1;display:flex;min-height:0}
.side{flex-shrink:0;width:27%;display:flex;flex-direction:column;gap:.75em;padding:.9em .75em;border-right:1px solid #ececea;background:#fafaf8}
.side-head{display:flex;align-items:center;gap:.55em}
.side-head .logo{width:1.9em;height:1.9em;border-radius:.45em}
.side-head b{display:block;font-size:.95em}.side-head small{display:block;font-size:.76em;color:#8a8a92}
.side-search{display:flex;align-items:center;gap:.45em;padding:.45em .6em;border-radius:.55em;background:#fff;border:1px solid #ececea;color:#9a9aa3;font-size:.8em}
.side-search kbd{margin-left:auto;padding:.05em .4em;border-radius:.3em;border:1px solid #e4e4e0;color:#71717a;font-size:.9em;font-family:var(--sans)}
.proj{display:flex;flex-direction:column;gap:.12em}
.proj-row{display:flex;align-items:center;gap:.45em;padding:.35em .45em;border-radius:.5em;font-size:.84em;font-weight:600;white-space:nowrap}
.proj-row .i{color:#71717a}
.proj-row small{margin-left:auto;font-weight:400;color:#a1a1aa;font-size:.86em}
.sess{display:flex;align-items:center;gap:.5em;margin-left:.9em;padding:.4em .5em;border-radius:.5em;font-size:.8em;color:#52525b}
.sess.on{background:#ececea;color:var(--ink);font-weight:500}
.sess .t{flex:1;min-width:0;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
.sess small{flex-shrink:0;color:#a1a1aa;font-size:.9em}
.side-new{margin-top:auto;display:flex;align-items:center;justify-content:center;gap:.4em;padding:.6em;border-radius:.6em;background:var(--ink);color:#fff;font-size:.82em;font-weight:500}
.app-main{flex:1;min-width:0;display:flex;flex-direction:column}
.main-head{flex-shrink:0;display:flex;align-items:center;justify-content:space-between;gap:1em;height:3.3em;padding:0 1.1em;border-bottom:1px solid #f0f0ee}
.main-head b{display:block;font-size:.98em;white-space:nowrap}.main-head small{display:block;font-size:.76em;color:#8a8a92}
.seg{display:flex;gap:.15em;padding:.22em;border-radius:.6em;background:#f4f4f2;font-size:.8em}
.seg span{padding:.3em .7em;border-radius:.45em;color:#71717a;white-space:nowrap}
.seg span.on{background:#fff;color:var(--ink);font-weight:500;box-shadow:0 1px 2px rgba(0,0,0,.08)}
.chat{flex:1;min-height:0;overflow:hidden;display:flex;flex-direction:column;gap:.8em;padding:1.1em 1.5em .6em;font-size:.92em}
.bubble-user{align-self:flex-end;max-width:80%;padding:.6em .9em;border-radius:.9em .9em .25em .9em;background:var(--ink);color:#fff}
.ai{display:flex;flex-direction:column;gap:.5em}
.ai-head{display:flex;align-items:center;gap:.5em;font-weight:600;font-size:.95em}
.ai-head .claude-mark{font-size:1em;width:1.6em;height:1.6em}
.ai-head small{font-weight:400;color:#a1a1aa;font-size:.85em}
.tools{display:flex;flex-direction:column;gap:.32em;padding-left:.8em;border-left:.18em solid rgba(217,119,87,.55);font-family:var(--mono);font-size:.86em}
.tools>div{display:flex;align-items:center;gap:.5em;min-width:0;white-space:nowrap}
.tools b{font-weight:600}
.tools .p{min-width:0;overflow:hidden;text-overflow:ellipsis;color:#52525b}
.tools .m{margin-left:auto;padding-left:.5em;color:#8a8a92}
.ok,.add{color:#059669}.del{color:#dc2626}
.composer{flex-shrink:0;display:flex;flex-direction:column;gap:.6em;margin:0 1.1em 1em;padding:.7em .85em;border-radius:.95em;border:1px solid #e6e6e2;background:#fff;box-shadow:0 .4em 1.2em -.6em rgba(0,0,0,.18);font-size:.88em}
.composer .ph{color:#a1a1aa;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.composer-row{display:flex;align-items:center;gap:.45em}
.chip{display:inline-flex;align-items:center;gap:.35em;padding:.25em .65em;border-radius:9999px;border:1px solid #e6e6e2;background:#fafaf8;color:#3f3f46;font-size:.9em;white-space:nowrap}
.chip .d{width:.45em;height:.45em;border-radius:50%;background:var(--accent)}
.send{display:grid;place-items:center;width:2em;height:2em;margin-left:auto;border-radius:50%;background:var(--ink);color:#fff}
.perm{padding:.85em .95em;border-radius:.8em;border:1px solid #fde68a;background:#fffbeb}
.perm-head{display:flex;gap:.6em;align-items:flex-start}
.perm-ico{display:grid;place-items:center;width:1.5em;height:1.5em;flex-shrink:0;border-radius:50%;background:#f59e0b;color:#fff;font-weight:700;font-size:.85em}
.perm-head b{display:block;font-weight:600}
.perm-head code{display:inline-block;margin-top:.3em;padding:.15em .45em;border-radius:.4em;background:rgba(0,0,0,.06);font-family:var(--mono);font-size:.85em}
.perm-rule{margin-top:.35em;font-size:.78em;color:#8a6d1f}
.perm-actions{display:flex;justify-content:flex-end;gap:.4em;margin-top:.7em}
.pbtn{padding:.32em .8em;border-radius:.55em;border:1px solid #e4e4e0;background:#fff;font-size:.82em;font-weight:500;white-space:nowrap}
.pbtn.pri{border-color:var(--ink);background:var(--ink);color:#fff}

/* 手机 */
.phone{position:absolute;aspect-ratio:9/19;padding:.5em;border-radius:2.6em;background:#0f0f12;box-shadow:0 2em 5em -1em rgba(0,0,0,.5),inset 0 0 0 .15em #2a2a2e;line-height:1.3}
.phone-screen{position:relative;display:flex;flex-direction:column;height:100%;overflow:hidden;border-radius:2.15em;background:#fff}
.phone-island{position:absolute;top:.6em;left:50%;z-index:2;width:32%;height:1.5em;transform:translateX(-50%);border-radius:9999px;background:#0f0f12}
.phone-status{display:flex;align-items:center;justify-content:space-between;padding:.8em 1.5em .3em;font-size:.8em;font-weight:600}
.phone-status .bars{display:flex;gap:.2em;align-items:flex-end}
.phone-status .bars i{width:.25em;border-radius:.1em;background:var(--ink)}
.notif{display:flex;gap:.6em;margin:.7em .6em .5em;padding:.7em .75em;border-radius:1.1em;background:rgba(244,244,240,.97);box-shadow:0 .5em 1.4em -.6em rgba(0,0,0,.35);font-size:.78em;line-height:1.35}
.notif .logo{width:2.3em;height:2.3em;border-radius:.55em}
.notif-body{min-width:0;flex:1}
.notif-top{display:flex;justify-content:space-between;color:#71717a;font-size:.9em}
.notif b{display:block;margin-top:.1em}
.notif p{color:#3f3f46}
.phone-title{display:flex;align-items:center;gap:.5em;padding:.45em .9em .55em;border-bottom:1px solid #f0f0ee;font-size:.8em;font-weight:600;white-space:nowrap;overflow:hidden}
.phone-title .i{color:#71717a}
.phone-chat{flex:1;min-height:0;overflow:hidden;display:flex;flex-direction:column;gap:.55em;padding:.7em .8em;font-size:.74em}
.phone-chat .bubble-user{max-width:88%}
.phone-chat .tools{font-size:.92em}
.phone-nav{flex-shrink:0;display:flex;justify-content:space-around;padding:.55em .4em 1em;border-top:1px solid #f0f0ee;font-size:.64em;color:#9a9aa3}
.phone-nav span{display:flex;flex-direction:column;align-items:center;gap:.25em}
.phone-nav span.on{color:var(--ink);font-weight:600}
.phone-nav .i{width:1.75em;height:1.75em}

/* ---------------- 第 5 镜：CodeDeck 登场 ---------------- */
.s5-pains{position:absolute;inset:0}
.s5-pains .display{margin-top:22px;font-size:64px}
.pain-grid{position:absolute;left:0;right:0;top:236px;display:grid;grid-template-columns:repeat(3,1fr);gap:30px}
.pain-card{padding:22px;border-radius:26px}
.pain-prev{height:282px;border-radius:18px;background:var(--paper);display:flex;align-items:center;justify-content:center;padding:0 28px}
.pain-card h3{margin:24px 6px 0;font-size:32px;font-weight:700;letter-spacing:-.015em}
.pain-card p{margin:8px 6px 6px;font-size:21px;line-height:1.6;color:var(--muted)}
.s5-hero{position:absolute;left:0;right:0;top:176px;display:flex;flex-direction:column;align-items:center;text-align:center}
.s5-core{display:flex;flex-direction:column;align-items:center;transform-origin:50% 0}
.brand-row{display:flex;align-items:center;gap:22px;margin-top:30px}
.brand-row .logo{width:92px;height:92px;border-radius:24px;box-shadow:0 18px 36px -14px rgba(7,87,206,.6)}
.brand-row b{font-size:76px;font-weight:700;letter-spacing:-.04em}
.s5-core .display{margin-top:26px;font-size:86px;letter-spacing:-.045em}
.hero-checks{display:flex;gap:40px;margin-top:34px;font-size:23px;color:var(--ink-soft)}
.hero-checks span{display:inline-flex;align-items:center;gap:10px}
.hero-checks .i{color:var(--accent-ink);stroke-width:2.4}
.cmp{position:absolute;left:0;right:0;top:250px;height:350px;display:grid;grid-template-columns:690px 1fr;gap:28px}
.cmp-old{position:relative;padding:28px 32px;border-radius:26px;background:#ecebe6;border:1px solid var(--rule)}
.cmp-new{position:relative;padding:28px 32px;border-radius:26px;background:#fff;box-shadow:0 0 0 2px rgba(16,185,129,.55),0 30px 70px -30px rgba(4,120,87,.45)}
.cmp-ph{position:absolute;inset:0;border-radius:26px;border:3px dashed rgba(24,24,27,.18);display:grid;place-items:center;font-size:120px;font-weight:700;color:rgba(24,24,27,.14)}
.cmp-h{display:flex;align-items:center;gap:16px}
.cmp-h b{font-size:30px;font-weight:700;letter-spacing:-.01em}
.cmp-h small{display:block;font-size:19px;color:var(--muted);font-weight:500}
.cmp-h .chipx{margin-left:auto}
.cmp-h .logo{width:60px;height:60px;border-radius:16px}
.price{position:relative;display:inline-flex;align-items:baseline;gap:10px;margin-top:22px}
.price .v{font-family:var(--mono);font-size:84px;font-weight:700;letter-spacing:-.05em;line-height:1}
.price .u{font-size:26px;font-weight:600;color:var(--muted)}
.cmp-old .price .v{color:#52525b}
.strike{position:absolute;left:-12px;right:-12px;top:52%;height:8px;border-radius:99px;background:var(--red);transform-origin:0 50%}
.cmp-old ul{margin-top:20px;display:flex;flex-direction:column;gap:8px;font-size:21px;color:var(--muted)}
.cmp-old li::before{content:"·";margin-right:10px}
.cmp-new .price .v{color:var(--accent-ink);font-family:var(--sans);font-size:96px;letter-spacing:-.05em}
.cmp-new .checks{position:absolute;right:32px;top:126px;width:470px;display:flex;flex-direction:column;gap:14px}
.cmp-new .checks span{display:flex;align-items:center;gap:12px;font-size:22px;color:var(--ink-soft)}
.cmp-new .checks .i{color:var(--accent-ink);stroke-width:2.4;font-size:22px}
.route{position:absolute;left:0;right:0;top:628px;height:184px;display:grid;grid-template-columns:1fr 1.15fr 1fr;gap:30px;align-items:center;padding:0 34px;border-radius:30px;background:#e9e9e3}
.route-end{display:flex;align-items:center;gap:18px;padding:20px 22px;border-radius:22px;background:#fff;box-shadow:var(--shadow-card)}
.route-ico{display:grid;place-items:center;width:62px;height:62px;flex-shrink:0;border-radius:18px;background:var(--paper);font-size:30px}
.route-end.srv .route-ico{background:var(--ink);color:#fff}
.route-end b{display:block;font-size:25px;font-weight:700}
.route-end small{display:block;margin-top:2px;font-size:18px;color:var(--muted)}
.route-mid{display:flex;flex-direction:column;align-items:center;gap:12px}
.route-pill{display:inline-flex;align-items:center;gap:8px;padding:7px 16px;border-radius:999px;border:1px solid var(--rule);background:#fff;font-size:19px;font-weight:600;color:var(--accent-ink)}
.route-track{position:relative;width:100%;height:14px}
.route-track::before{content:"";position:absolute;left:0;right:0;top:6px;height:2px;background:repeating-linear-gradient(90deg,#c2c2bb 0 8px,transparent 8px 16px)}
.route-track i{position:absolute;top:2px;width:10px;height:10px;margin-left:-5px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 5px var(--accent-soft)}
.route-tags{display:flex;gap:8px}
.route-tags span{padding:4px 12px;border-radius:999px;background:rgba(255,255,255,.8);font-size:16px;color:var(--ink-soft)}

/* ---------------- 第 6 镜：功能导览 + 主视觉 + CTA ---------------- */
.rail{position:absolute;left:0;top:0;width:600px;height:812px}
.rail-items{position:absolute;left:0;right:0;top:84px;display:flex;flex-direction:column;gap:12px}
.ri{position:relative;display:flex;gap:20px;padding:20px 24px;border-radius:22px;border:1px solid transparent}
.ri .n{font-family:var(--mono);font-size:20px;font-weight:700;color:var(--muted-light);padding-top:6px;width:30px}
.ri b{display:block;font-size:29px;font-weight:700;letter-spacing:-.015em;color:var(--ink)}
.ri small{display:block;margin-top:5px;font-size:20px;color:var(--muted);line-height:1.45}
.ri .bg{position:absolute;inset:0;border-radius:22px;background:#fff;box-shadow:var(--shadow-card)}
.ri .bar{position:absolute;left:0;top:22px;bottom:22px;width:4px;border-radius:4px;background:var(--accent)}
.ri>div,.ri>.n{position:relative}
.stage{position:absolute;left:660px;top:0;width:1068px;height:812px}
.pnl{position:absolute;inset:0}
.globe-card{position:absolute;inset:0;padding:24px 28px;border-radius:30px;background:#fff;border:1px solid var(--rule);box-shadow:0 8px 40px -8px rgba(0,0,0,.06)}
.globe-card .globe-box{height:540px;margin-top:18px}
.node-pills{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-top:20px;padding-top:20px;border-top:1px solid #f4f4f5}
.node-pill{display:flex;flex-direction:column;align-items:center;gap:2px;padding:12px 6px;border-radius:16px;border:1px solid var(--rule);background:#fff}
.node-pill .nt{font-size:21px;font-weight:600}
.node-pill .nm{font-family:var(--mono);font-size:17px;color:var(--accent-ink)}
.node-pill.active{background:var(--ink);border-color:var(--ink);color:#fff}
.node-pill.active .nm{color:#6ee7b7}
.launcher{position:absolute;left:84px;top:150px;width:900px;overflow:hidden;border-radius:1em;background:#fff;box-shadow:var(--shadow-float);font-size:20px;line-height:1.5}
.win-bar{display:flex;align-items:center;gap:.6em;height:2.4em;padding:0 .9em;border-bottom:1px solid #efefec;background:#fafaf8;color:#71717a;font-size:.8em}
.win-bar .title{flex:1;text-align:center;margin-right:3.4em;font-weight:500;color:#52525b}
.launcher-body{display:grid;grid-template-columns:8.6em 1fr;min-height:15em}
.l-side{padding:.85em .55em;border-right:1px solid #efefec;background:#fafaf8}
.l-lbl{padding:0 .5em .45em;font-size:.72em;font-weight:600;color:#8a8a92}
.l-nav{display:flex;align-items:center;gap:.45em;padding:.42em .5em;border-radius:.5em;font-size:.82em;color:#52525b;white-space:nowrap}
.l-nav.on{background:#ececea;color:var(--ink);font-weight:600}
.l-nav em{margin-left:auto;font-style:normal;font-size:.8em;color:#8a8a92}
.l-main{padding:1em 1.2em}
.l-head{display:flex;align-items:flex-start;justify-content:space-between}
.l-head h4{font-size:1em;font-weight:600}
.l-head p{font-size:.74em;color:#8a8a92}
.l-row{display:flex;align-items:center;gap:.7em;margin-top:.65em;padding:.7em .8em;border-radius:.75em;border:1px solid #ececea}
.l-row.on{border-color:rgba(16,185,129,.45);box-shadow:0 0 0 3px rgba(16,185,129,.1)}
.l-dot{width:.5em;height:.5em;border-radius:50%;background:var(--accent);flex-shrink:0}
.l-info{flex:1;min-width:0}
.l-info b{display:block;font-size:.86em;font-weight:600}
.l-info small{display:block;font-family:var(--mono);font-size:.7em;color:#8a8a92}
.gbtn{display:inline-flex;align-items:center;justify-content:center;gap:.4em;padding:.4em .9em;border-radius:.6em;border:1px solid #e4e4e0;background:#fff;font-size:.78em;font-weight:500;white-space:nowrap}
.gbtn.pri{border-color:var(--ink);background:var(--ink);color:#fff}
.remote-pill{position:absolute;left:50%;top:0;z-index:5;display:flex;align-items:center;gap:14px;padding:10px 20px;border-radius:14px;background:rgba(28,29,34,.92);color:rgba(255,255,255,.88);font-size:20px;white-space:nowrap;box-shadow:0 14px 30px -12px rgba(0,0,0,.6)}
.remote-pill b{font-weight:600;color:#fff}
.remote-pill .dv{width:1px;height:20px;background:rgba(255,255,255,.2)}
.remote-pill .loc{display:flex;align-items:center;gap:8px}
.remote-pill .loc i{width:10px;height:10px;border-radius:50%;background:#34d399}
.remote-pill .ms{color:rgba(255,255,255,.6);font-family:var(--mono)}
#s6-app{position:absolute;left:0;top:60px;width:1068px;height:752px}
.timeline{position:absolute;left:0;right:0;top:0;padding:32px 34px 74px;border-radius:26px}
.tl-axis-row,.tl-row{display:grid;grid-template-columns:230px 1fr;gap:20px;align-items:center}
.tl-axis{position:relative;height:28px;font-family:var(--mono);font-size:19px;color:var(--muted)}
.tl-axis span{position:absolute;transform:translateX(-50%);white-space:nowrap}
.tl-row{margin-top:20px}
.tl-label{display:flex;align-items:center;gap:10px;font-size:25px;font-weight:600}
.tl-label .i{color:var(--muted)}
.tl-bar{position:relative;height:70px;border-radius:14px;background:var(--paper)}
.tl-clip{position:absolute;inset:0;overflow:hidden;border-radius:14px}
.tl-seg{position:absolute;top:0;bottom:0;display:flex;align-items:center;padding:0 16px;overflow:hidden;border-radius:14px;font-size:21px;font-weight:500;white-space:nowrap}
.tl-on{background:#d4d4d8;color:var(--ink)}
.tl-off{background:repeating-linear-gradient(135deg,#f4f4f0 0 8px,#e6e6e0 8px 16px);color:var(--muted)}
.tl-run{background:linear-gradient(90deg,#059669,#10b981 60%,#34d399);color:#fff}
.tl-mark{position:absolute;top:50%;z-index:2;width:18px;height:18px;margin:-9px 0 0 -9px;border-radius:50%;background:#fff;box-shadow:0 0 0 3px #047857}
.tl-mark span{position:absolute;top:calc(100% + 14px);left:50%;transform:translateX(-50%);padding:6px 13px;border-radius:10px;background:var(--ink);color:#fff;font-size:19px;white-space:nowrap}
.tl-head{position:absolute;top:-6px;bottom:-6px;width:2px;margin-left:-1px;background:var(--ink);z-index:3}
.tl-head::after{content:"";position:absolute;left:-5px;top:-8px;width:12px;height:12px;border-radius:50%;background:var(--ink)}
.use-grid{position:absolute;left:0;top:372px;width:770px;display:grid;grid-template-columns:1fr 1fr;gap:20px}
.use{padding:30px;border-radius:24px;border:1px solid var(--rule);background:#fff;height:330px}
.use b{display:block;margin-top:26px;font-size:30px;font-weight:700}
.use p{margin-top:10px;font-size:21px;line-height:1.65;color:var(--muted)}
#tl-phone{right:30px;top:300px;width:236px}
.sec-vault{position:absolute;left:0;right:0;top:206px;height:238px;border-radius:26px;overflow:hidden;background:#fff;box-shadow:var(--shadow-card)}
.vault-head{display:flex;align-items:center;gap:14px;height:76px;padding:0 28px;background:var(--ink);color:#fff;font-size:24px;font-weight:600}
.vault-head .mono{margin-left:auto;font-size:19px;color:#6ee7b7;font-weight:500}
.vault-body{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;padding:26px 28px}
.vi{display:flex;align-items:center;gap:16px;padding:22px 20px;border-radius:20px;border:1px solid var(--rule);background:#fafaf8}
.vi b{display:block;font-size:24px;font-weight:700}
.vi small{display:block;font-family:var(--mono);font-size:16px;color:var(--muted)}
.vi .lk{margin-left:auto;color:var(--accent-ink);font-size:26px}
.pillars{position:absolute;left:0;right:0;top:472px;display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.pillar{padding:24px;border-radius:22px;border:1px solid var(--rule);background:#fff;height:300px}
.pillar .tile{width:54px;height:54px;font-size:27px;border-radius:15px}
.pillar b{display:block;margin-top:20px;font-size:25px;font-weight:700}
.pillar p{margin-top:8px;font-size:19px;line-height:1.55;color:var(--muted)}
.pillar.hl{border-color:rgba(16,185,129,.5);box-shadow:0 0 0 3px rgba(16,185,129,.12)}
#sec-route{top:0;height:180px}
.flow-chip{position:absolute;top:0;display:inline-flex;align-items:center;gap:8px;padding:8px 16px;border-radius:999px;background:#fff;box-shadow:var(--shadow-card);font-size:19px;font-weight:600;white-space:nowrap}
.flow-chip .i{color:var(--accent-ink)}

.hero-wrap{position:absolute;inset:0}
.desk{position:absolute;left:224px;top:0;width:1280px;height:800px;border-radius:20px;overflow:hidden;font-size:16px;line-height:1.3;
  background:linear-gradient(160deg,#eef0f3 0%,#d9dce2 50%,#c3c7cf 100%);box-shadow:0 50px 100px -40px rgba(15,18,30,.5),0 0 0 1px rgba(15,18,30,.08);transform-origin:50% 0}
.desk-amb{position:absolute;inset:0;background:radial-gradient(60% 50% at 15% 15%,rgba(255,255,255,.75) 0%,transparent 60%),radial-gradient(70% 60% at 85% 90%,rgba(150,156,168,.35) 0%,transparent 65%)}
.mb{position:absolute;left:0;right:0;top:0;display:flex;align-items:center;gap:1.45em;height:1.9em;padding:0 1.4em;background:rgba(255,255,255,.55);color:#1d1d1f;font-size:.92em}
.mb b{font-weight:600}.mb span{color:rgba(29,29,31,.85)}
.mb-r{margin-left:auto;display:flex;align-items:center;gap:1.2em}
.desk .remote-pill{top:2.7em;font-size:.95em;transform:translateX(-50%)}
#hero-app{position:absolute;left:3.5%;top:10.5%;width:75%;height:84%}
#hero-phone{right:3.5%;bottom:4%;width:21%}
.float-badge{position:absolute;z-index:6;display:flex;align-items:center;gap:16px;padding:18px 24px;border-radius:22px;background:#fff;box-shadow:var(--shadow-float)}
.float-badge .tile{width:56px;height:56px;font-size:28px;border-radius:16px}
.float-badge b{display:block;font-size:26px;font-weight:700;letter-spacing:-.01em}
.float-badge small{display:block;font-size:18px;color:var(--muted)}
.float-badge .big{font-size:38px;color:var(--accent-ink);letter-spacing:-.03em}
.cta{position:absolute;inset:0;z-index:20;border-radius:34px;overflow:hidden;background:#111113;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.cta-glow{position:absolute;left:-20%;right:-20%;bottom:-75%;height:125%;background:radial-gradient(50% 50% at 50% 50%,rgba(16,185,129,.36),transparent 70%)}
.cta>*:not(.cta-glow){position:relative}
.cta .brand-row{margin-top:0}
.cta .brand-row b{font-size:64px}
.cta .brand-row .logo{width:84px;height:84px;border-radius:22px}
.cta .display{color:#fafafa;margin-top:34px;font-size:78px}
.cta .display em{color:#6ee7b7}
.cta p{margin-top:24px;font-size:27px;color:#a1a1aa}
.cta .acts{display:flex;gap:18px;margin-top:40px}
.cta .ck{display:flex;gap:34px;margin-top:40px;font-size:22px;color:#d4d4d8}
.cta .ck span{display:inline-flex;align-items:center;gap:10px}
.cta .ck .i{color:#34d399;stroke-width:2.4}

#cursor{position:absolute;left:0;top:0;width:44px;height:44px;z-index:60;display:none;pointer-events:none;filter:drop-shadow(0 6px 8px rgba(0,0,0,.25))}

/* ---------------- 字幕 ---------------- */
#subbar{position:absolute;left:0;right:0;bottom:34px;z-index:40;display:flex;justify-content:center;pointer-events:none}
#sub-pill{max-width:1640px;padding:12px 34px 13px;border-radius:18px;background:rgba(24,24,27,.92);color:#fafafa;font-size:34px;font-weight:600;line-height:1.35;letter-spacing:.01em;text-align:center;box-shadow:0 24px 48px -24px rgba(0,0,0,.6),inset 0 0 0 1px rgba(255,255,255,.07)}
#sub-pill .sub-hl{color:#6ee7b7}
#sub-pill .sub-warn{color:#fcd34d}
</style>
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <defs>
    <linearGradient id="cd-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0757CE"/><stop offset="1" stop-color="#1874F5"/></linearGradient>
  </defs>
  <symbol id="cd-logo" viewBox="0 0 64 64">
    <rect width="64" height="64" rx="14" fill="url(#cd-grad)"/>
    <rect x="11" y="23" width="30" height="24" rx="4.5" fill="#0A5AD2" stroke="#fff" stroke-opacity=".38" stroke-width="2"/>
    <rect x="15.5" y="18" width="30" height="24" rx="4.5" fill="#0B5CD6" stroke="#fff" stroke-opacity=".62" stroke-width="2"/>
    <rect x="20" y="12.5" width="31" height="25" rx="4.5" fill="#0D61DD" stroke="#fff" stroke-width="2.4"/>
    <path d="M26.5 20.5l5 4.5-5 4.5" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M34.5 30.5h8" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/>
  </symbol>
  <symbol id="i-check" viewBox="0 0 24 24"><path d="M5 12.5l4.2 4.2L19 7"/></symbol>
  <symbol id="i-x" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></symbol>
  <symbol id="i-arrow" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></symbol>
  <symbol id="i-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></symbol>
  <symbol id="i-up" viewBox="0 0 24 24"><path d="M12 19V5M6 11l6-6 6 6"/></symbol>
  <symbol id="i-chat" viewBox="0 0 24 24"><path d="M20 15a2 2 0 0 1-2 2H9l-5 4V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2z"/></symbol>
  <symbol id="i-terminal" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M7 9.5l3 2.5-3 2.5M13 15h4"/></symbol>
  <symbol id="i-folder" viewBox="0 0 24 24"><path d="M3 7.5A2.5 2.5 0 0 1 5.5 5H9l2 2.2h7.5A2.5 2.5 0 0 1 21 9.7v7.8a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 17.5z"/></symbol>
  <symbol id="i-branch" viewBox="0 0 24 24"><circle cx="6" cy="6" r="2.2"/><circle cx="6" cy="18" r="2.2"/><circle cx="18" cy="6" r="2.2"/><path d="M6 8.2v7.6M18 8.2c0 4.8-7.5 3.6-11 7.6"/></symbol>
  <symbol id="i-board" viewBox="0 0 24 24"><rect x="3.5" y="4" width="17" height="16" rx="2.5"/><path d="M9.2 4v16M14.8 4v10"/></symbol>
  <symbol id="i-moon" viewBox="0 0 24 24"><path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/></symbol>
  <symbol id="i-layers" viewBox="0 0 24 24"><path d="M12 3.5l8.5 4.5L12 12.5 3.5 8z"/><path d="M3.5 12.5L12 17l8.5-4.5"/><path d="M3.5 16.5L12 21l8.5-4.5"/></symbol>
  <symbol id="i-devices" viewBox="0 0 24 24"><rect x="2.5" y="4.5" width="13" height="10" rx="1.6"/><path d="M6.5 18.5h5"/><rect x="17.5" y="8.5" width="4" height="11" rx="1.2"/></symbol>
  <symbol id="i-bolt" viewBox="0 0 24 24"><path d="M13 3L5 13.5h6L10 21l8-10.5h-6z"/></symbol>
  <symbol id="i-shield" viewBox="0 0 24 24"><path d="M12 3l7.5 3v5.5c0 4.6-3.2 8.3-7.5 9.5-4.3-1.2-7.5-4.9-7.5-9.5V6z"/><path d="M9 12l2 2 4-4"/></symbol>
  <symbol id="i-lock" viewBox="0 0 24 24"><rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/></symbol>
  <symbol id="i-server" viewBox="0 0 24 24"><rect x="3.5" y="4" width="17" height="6.5" rx="1.6"/><rect x="3.5" y="13.5" width="17" height="6.5" rx="1.6"/><path d="M7.5 7.25h.01M7.5 16.75h.01M11 7.25h6M11 16.75h6"/></symbol>
  <symbol id="i-key" viewBox="0 0 24 24"><circle cx="8" cy="15" r="4"/><path d="M11 12l8.5-8.5M16 7l2.5 2.5M14 9l2 2"/></symbol>
  <symbol id="i-download" viewBox="0 0 24 24"><path d="M12 4v11M7.5 10.5L12 15l4.5-4.5M5 19.5h14"/></symbol>
  <symbol id="i-laptop" viewBox="0 0 24 24"><rect x="4.5" y="5" width="15" height="10.5" rx="1.6"/><path d="M2.5 19h19"/></symbol>
  <symbol id="i-monitor" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="12" rx="1.8"/><path d="M8.5 20h7M12 16v4"/></symbol>
  <symbol id="i-globe" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/></symbol>
  <symbol id="i-search" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/></symbol>
  <symbol id="i-sparkle" viewBox="0 0 24 24"><path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 15.5l.8 2 2 .7-2 .8-.8 2-.7-2-2-.8 2-.7z"/></symbol>
  <symbol id="i-wifi" viewBox="0 0 24 24"><path d="M2.5 9a14 14 0 0 1 19 0M5.5 12.5a9.5 9.5 0 0 1 13 0M8.5 16a5 5 0 0 1 7 0"/><path d="M12 19.5h.01"/></symbol>
  <symbol id="i-home" viewBox="0 0 24 24"><path d="M4 10.5L12 4l8 6.5V19a1 1 0 0 1-1 1h-4.5v-5.5h-5V20H5a1 1 0 0 1-1-1z"/></symbol>
  <symbol id="i-asterisk" viewBox="0 0 24 24"><path d="M12 4v16M5.1 8l13.8 8M5.1 16l13.8-8"/></symbol>
  <symbol id="i-split" viewBox="0 0 24 24"><rect x="3" y="5" width="7.5" height="14" rx="1.6"/><rect x="13.5" y="5" width="7.5" height="14" rx="1.6"/></symbol>
  <symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></symbol>
  <symbol id="i-map" viewBox="0 0 24 24"><path d="M9 4L3.5 6v14L9 18l6 2 5.5-2V4L15 6z"/><path d="M9 4v14M15 6v14"/></symbol>
  <symbol id="i-card" viewBox="0 0 24 24"><rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="M3 10h18M7 15h4"/></symbol>
  <symbol id="i-finger" viewBox="0 0 24 24"><path d="M6.5 8.5A6.5 6.5 0 0 1 18.5 11v1.5"/><path d="M5.5 12.5v-1a6.5 6.5 0 0 1 .4-2.2"/><path d="M8.6 19.5c.9-1.9 1.4-4 1.4-6.4V11a2 2 0 0 1 4 0v1.8"/><path d="M12 13.3c0 3-.7 5.4-1.9 7.2"/><path d="M14 16.4c-.2 1.5-.6 2.8-1.1 4"/><path d="M16.3 15.6c-.1 1.6-.4 3.1-.9 4.4"/><path d="M7.4 16.6c.4-1.1.6-2.3.6-3.6V11a4 4 0 0 1 8 0v2"/></symbol>
  <symbol id="i-face" viewBox="0 0 24 24"><path d="M4 8V6a2 2 0 0 1 2-2h2M16 4h2a2 2 0 0 1 2 2v2M20 16v2a2 2 0 0 1-2 2h-2M8 20H6a2 2 0 0 1-2-2v-2"/><circle cx="12" cy="10.5" r="2.6"/><path d="M7.8 17c.9-1.9 2.4-2.8 4.2-2.8s3.3.9 4.2 2.8"/></symbol>
  <symbol id="i-alert" viewBox="0 0 24 24"><path d="M12 4l9 16H3z"/><path d="M12 10v4.5M12 17.5h.01"/></symbol>
  <symbol id="i-film" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M3 9h18M3 15h18M8 4v5M16 4v5M8 15v5M16 15v5"/></symbol>
  <symbol id="i-pin" viewBox="0 0 24 24"><path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.4"/></symbol>
</svg>

<div id="viewport">
  <div id="bg-grid"></div>

  <div id="topbar">
    <div class="tb-brand">__LOGO__<b>CodeDeck</b><span class="tb-sep"></span><span class="tb-ep">EP01 · 如何在国内稳定使用 Claude</span></div>
    <div class="tb-right">
      <span class="tb-chap"><i class="pip"></i><span id="tb-chap">01 · 风控破防</span></span>
      <div class="tb-prog"><div class="tb-seg"><i id="pf-0"></i></div><div class="tb-seg"><i id="pf-1"></i></div><div class="tb-seg"><i id="pf-2"></i></div><div class="tb-seg"><i id="pf-3"></i></div><div class="tb-seg"><i id="pf-4"></i></div><div class="tb-seg"><i id="pf-5"></i></div></div>
      <span id="tb-tc">00:00.0 / __DURATION_LABEL__</span>
    </div>
  </div>

  <!-- ===================== 01 风控 vs 小摩托 ===================== -->
  <div class="scene" id="scene-1">
    <div class="s1-head">
      <span class="eyebrow" id="s1-eb"><i class="pip red"></i>离谱真事 · 当硅谷风控遇上中国老哥</span>
      <h1 class="display"><span class="swap"><span id="s1-l1">算尽了 IP、指纹、人脸核身，</span></span><span class="swap"><span id="s1-l2">却没算到<em class="hl-claude">「物理下乡」</em></span></span></h1>
    </div>
    <div class="s1-meter card" id="s1-meter">
      <div class="m-lbl"><i class="pip red"></i>Anthropic 风控层数<span class="chipx bad st" id="s1-st">逐层加码</span></div>
      <div class="m-num"><span id="s1-count">0</span><small>层</small></div>
      <div class="m-bar"><span id="s1-bar"></span></div>
      <div class="m-foot" id="s1-foot">__ICO_shield__防护等级 · <b>五角大楼级</b></div>
    </div>
    <div class="s1-wall">
      <div class="s1-card card" id="fw-1"><div class="s1-ring" id="fr-1"></div>
        <div class="row"><span class="tile red">__ICO_globe__</span><span class="tag">LAYER 01</span><span class="chipx" id="fs-1">待命</span></div>
        <h3>锁 IP</h3><p>机房 IP、共享代理出口，一律拦截</p>
        <div class="prev"><div class="mini mini-dark"><p class="dim">$ 检测出口 IP…</p><p class="err">✗ 机房IP段·已拦截</p><p class="err">✗ 共享代理出口·已拉黑</p></div></div>
      </div>
      <div class="s1-card card" id="fw-2"><div class="s1-ring" id="fr-2"></div>
        <div class="row"><span class="tile red">__ICO_finger__</span><span class="tag">LAYER 02</span><span class="chipx" id="fs-2">待命</span></div>
        <h3>查指纹</h3><p>时区、系统、支付卡属地交叉比对</p>
        <div class="prev"><div class="mini mini-light"><ul class="mini-list"><li>时区<b class="hl-red">Asia/Shanghai ⚠</b></li><li>系统语言<b class="hl-red">zh-CN ⚠</b></li><li>支付卡属地<b class="hl-red">不匹配 ⚠</b></li></ul></div></div>
      </div>
      <div class="s1-card card" id="fw-3"><div class="s1-ring" id="fr-3"></div>
        <div class="row"><span class="tile red">__ICO_face__</span><span class="tag">LAYER 03</span><span class="chipx" id="fs-3">待命</span></div>
        <h3>人脸核身</h3><p>当地手机号 + 真人实名 KYC</p>
        <div class="prev"><div class="mini mini-light kyc"><div class="kyc-face">__ICO_face__<i class="scan" id="s1-scan"></i></div><div><b>请正对镜头</b><small>眨眨眼 · 缓慢转头</small><small class="mono">+62 本地号码校验</small></div></div></div>
      </div>
    </div>
    <canvas id="s1-canvas" width="3840" height="1624"></canvas>
    <div class="s1-stamp" id="s1-stamp">物理破防<small>PHYSICAL BYPASS</small></div>
  </div>

  <!-- ===================== 02 摩旅 1500km ===================== -->
  <div class="scene" id="scene-2">
    <div class="s2-left">
      <span class="eyebrow" id="s2-eb"><i class="pip orange"></i>真事儿 · 印尼 Claude 下乡收号</span>
      <h1 class="display" id="s2-title">骑摩托 1500 公里，<br>进村<em class="hl-claude">当面过实名</em></h1>
      <div class="s2-stack">
        <div class="map-card card" id="s2-map">
          <div class="map-head"><span class="map-title"><i class="pip orange"></i>摩旅路线 · 巴厘岛 → 苏门答腊</span><span class="map-dist" id="s2-dist">0 km</span></div>
          <div class="globe-box"><canvas id="s2-canvas" width="1792" height="780"></canvas></div>
          <div class="map-foot"><span class="chipx" id="s2-c1">__ICO_card__进村当面打款</span><span class="chipx" id="s2-c2">__ICO_face__现场过实名</span><span class="chipx" id="s2-c3">__ICO_pin__举白板合影</span></div>
        </div>
        <div class="acct-card card" id="s2-acct">
          <div class="ac-head"><span class="ac-av">👵🏽</span><div><b>苏门答腊 · 村口大妈</b><small>代码经验：<span class="mono">0 行</span> · 一辈子没摸过键盘</small></div><span class="chipx ok">__ICO_check__实名已通过</span></div>
          <div class="ac-lbl">名下 Claude 账号</div>
          <div class="ac-row" id="ac-1">__CLAUDE__<div><b>Claude 账号 #1</b><small>印尼区 · 已实名</small></div><span class="st"><i class="pip"></i>在用</span></div>
          <div class="ac-row" id="ac-2">__CLAUDE__<div><b>Claude 账号 #2</b><small>印尼区 · 已实名</small></div><span class="st"><i class="pip"></i>在用</span></div>
          <div class="ac-row" id="ac-3">__CLAUDE__<div><b>Claude 账号 #3</b><small>印尼区 · 已实名</small></div><span class="st"><i class="pip"></i>在用</span></div>
          <div class="ac-foot" id="ac-foot">🏆 莫名其妙成了<em>「中国 AI 基石」</em></div>
        </div>
      </div>
    </div>
    <div class="s2-right">
      <div class="photo-card" id="s2-photo">
        <div class="ph-img"><div class="ph-zoom" id="s2-zoom"><img id="img-indo" src="data:image/jpeg;base64,__B64_INDO__" alt=""/><div class="ph-hl" id="s2-hl"></div></div></div>
        <div class="ph-cap"><span>📍 印尼苏门答腊 · 现场合影</span><span class="chipx">真实素材</span></div>
      </div>
      <div class="quote-card" id="s2-quote"><div class="q-lbl"><i class="pip orange"></i>白板原文</div><div class="q">印尼老哥助力<br>中国科研 · 中国 AI<br><em>China No.1</em></div></div>
    </div>
  </div>

  <!-- ===================== 03 算账 ===================== -->
  <div class="scene" id="scene-3">
    <div class="s3-left">
      <div class="shot-win" id="s3-shot"><img id="img-moments" src="data:image/jpeg;base64,__B64_MOMENTS__" alt=""/></div>
      <span class="eyebrow s3-src" id="s3-src"><i class="pip orange"></i>代理朋友圈 · 真实截图</span>
      <div class="callout" id="s3-co1"><span class="dot"></span><span class="ln"></span><span class="bx">海外机房 · Mac mini 实体机<small>单租一台 · 月付</small></span></div>
      <div class="callout" id="s3-co2"><span class="dot"></span><span class="ln"></span><span class="bx">Max 预订凭证<small>印尼区 · 已支付</small></span></div>
    </div>
    <div class="s3-right">
      <span class="eyebrow" id="s3-eb"><i class="pip red"></i>笑归笑 · 算一笔账</span>
      <h1 class="display" id="s3-title">国内想稳用 Claude，<br>代价<em class="hl-red">真不小</em></h1>
      <div class="bill card" id="s3-bill">
        <div class="bill-head"><span>每月账单 · 海外实体机方案</span><span class="mono">USD → CNY</span></div>
        <div class="bill-row" id="br-1"><span class="tile">__ICO_server__</span><div><b>海外 Mac mini 实体机</b><small>单租一台，只是机器</small></div><div class="pr"><div class="usd">$<span class="mono" id="bu-1" style="font-size:40px;color:var(--ink);margin:0;font-weight:700;letter-spacing:-.03em">0</span><span>/月</span></div><div class="cny" id="bc-1">≈ ¥1,060</div></div></div>
        <div class="bill-row" id="br-2"><span class="tile claude">__ICO_asterisk__</span><div><b>Claude Max</b><small>高频写代码档位</small></div><div class="pr"><div class="usd">$<span class="mono" id="bu-2" style="font-size:40px;color:var(--ink);margin:0;font-weight:700;letter-spacing:-.03em">0</span><span>/月</span></div><div class="cny" id="bc-2">≈ ¥2,500+</div></div></div>
        <div class="bill-row" id="br-3"><span class="tile claude">__ICO_asterisk__</span><div><b>Claude Ultra</b><small>重度 Agent 档位</small></div><div class="pr"><div class="usd">$<span class="mono" id="bu-3" style="font-size:40px;color:var(--ink);margin:0;font-weight:700;letter-spacing:-.03em">0</span><span>/月</span></div><div class="cny" id="bc-3">≈ ¥3,700+</div></div></div>
        <div class="bill-total" id="s3-total"><div class="lb"><b>每月硬掏</b><small>普通人谁顶得住？</small></div><div class="v" id="s3-tv">¥2,500–3,700+</div></div>
        <div class="stamp" id="s3-stamp">门槛劝退</div>
      </div>
    </div>
  </div>

  <!-- ===================== 04 为什么是 Claude ===================== -->
  <div class="scene" id="scene-4">
    <div class="s4-head">
      <span class="eyebrow" id="s4-eb"><i class="pip orange"></i>为什么大家非用 Claude 不可</span>
      <h1 class="display"><span class="swap"><span id="s4-a">不止能写代码，还能<em class="hl-claude">做视频、剪视频</em></span><span id="s4-b">你正在看的这条视频，<em class="hl-green">就是 Claude 写代码做的</em></span></span></h1>
    </div>
    <div class="s4-left">
      <div class="cap card" id="cap-1"><span class="tile">__ICO_layers__</span><div><h3>通读整个项目</h3><p>几十个文件一起理解，成片重构</p><code>● Edit 42 files  +640 −180</code></div></div>
      <div class="cap card" id="cap-2"><span class="tile green">__ICO_terminal__</span><div><h3>写代码 · 跑测试</h3><p>自己跑单测、修 Bug，直到全绿</p><code>✓ npm test → 42 passed</code></div></div>
      <div class="cap feat" id="cap-3"><span class="tile claude">__ICO_film__</span><div><h3>做视频 · 剪视频</h3><p>写动画、合成配乐、渲染成片</p><code>★ window.render(t) → final.mp4</code></div></div>
    </div>
    <div class="s4-right">__APP_S4__</div>
  </div>

  <!-- ===================== 05 CodeDeck 登场 ===================== -->
  <div class="scene" id="scene-5">
    <div class="s5-pains" id="s5-pains">
      <span class="eyebrow" id="s5-eb"><i class="pip red"></i>但是 · 本地挂代理用 Claude</span>
      <h1 class="display" id="s5-pt">断连、封号、一合盖就停</h1>
      <div class="pain-grid">
        <div class="pain-card card" id="pc-1"><div class="pain-prev"><div class="mini mini-navy"><p>$ claude</p><p class="err">✗ 连接被重置（ECONNRESET）</p><p class="dim">代理节点切换中，需要重新验证…</p></div></div><h3>网络一抖，任务就停</h3><p>长连接说断就断，输出到一半没了</p></div>
        <div class="pain-card card" id="pc-2"><div class="pain-prev"><div class="mini mini-light"><div class="mini-head">__ICO_alert__账号安全提醒</div><ul class="mini-list"><li>出口 IP<b>频繁切换</b></li><li>共享节点<b>多人同 IP</b></li><li>账号状态<b class="hl-red">已暂停 ✗</b></li></ul></div></div><h3>共享出口，说封就封</h3><p>机场节点多人共用，风控一扫一片</p></div>
        <div class="pain-card card" id="pc-3"><div class="pain-prev"><div class="mini mini-dark"><p>$ claude</p><p class="dim">● 正在重构 42 个文件…</p><p class="err">✗ 电脑已睡眠，会话中断</p><div class="mini-progress"><span></span></div></div></div><h3>一合上电脑就断</h3><p>笔记本合盖、休眠，任务跟着停下</p></div>
      </div>
    </div>
    <div class="s5-hero" id="s5-hero">
      <span class="eyebrow" id="s5-heb"><span class="claude-mark" style="font-size:16px">__ICO_asterisk__</span>我自己开发的 · 专为 Claude Code 打造的远程工作台</span>
      <div class="s5-core" id="s5-core">
        <div class="brand-row">__LOGO__<b>CodeDeck</b></div>
        <h1 class="display">海外服务器直连，<br>Claude Code 开机即用</h1>
      </div>
      <div class="hero-checks" id="s5-checks"><span>__ICO_check__命令在服务器上执行，不碰你的电脑</span><span>__ICO_check__桌面端 / 浏览器一键连上</span><span>__ICO_check__合上电脑，Claude 照样在跑</span></div>
    </div>
    <div class="cmp" id="s5-cmp">
      <div class="cmp-old" id="s5-old">
        <div class="cmp-h"><span class="tile">__ICO_server__</span><div><b>租海外实体 Mac mini</b><small>代理朋友的方案</small></div><span class="chipx">传统方案</span></div>
        <div class="price"><span class="v">¥1,060</span><span class="u">/月 · 仅机器</span><i class="strike" id="s5-strike"></i></div>
        <ul><li>排队预约，看代理档期</li><li>自己折腾远程桌面和网络</li><li>还不含 Claude 订阅</li></ul>
      </div>
      <div style="position:relative">
        <div class="cmp-ph" id="s5-ph">?</div>
        <div class="cmp-new" id="s5-new" style="position:absolute;inset:0">
          <div class="cmp-h">__LOGO__<div><b>CodeDeck · 海外独立服务器</b><small>一台只给你用的服务器，Claude Code 就跑在上面</small></div></div>
          <div class="price" id="s5-price"><span class="v">几十块</span><span class="u">/月</span></div>
          <div class="checks"><span>__ICO_check__独立公网 IP · 一人一台</span><span>__ICO_check__机房原生网络 · 不靠本地代理</span><span>__ICO_check__桌面端 · 浏览器 · 手机直连</span><span>__ICO_check__合上电脑照样跑 · 7×24</span></div>
        </div>
      </div>
    </div>
    <div class="route" id="s5-route">
      <div class="route-end"><span class="route-ico">__ICO_devices__</span><div><b>你的电脑</b><small>桌面端 · 浏览器 · 手机</small></div></div>
      <div class="route-mid"><span class="route-pill">__ICO_lock__专属 HTTPS 地址</span><div class="route-track"><i id="s5-d1"></i><i id="s5-d2"></i></div><div class="route-tags"><span>自动登录</span><span>断线续流</span><span>草稿同步</span></div></div>
      <div class="route-end srv"><span class="route-ico">__ICO_server__</span><div><b>你的海外服务器</b><small>Claude Code 在这里运行 · 7×24</small></div></div>
    </div>
  </div>

  <!-- ===================== 06 功能导览 / 主视觉 / CTA ===================== -->
  <div class="scene" id="scene-6">
    <div class="rail" id="s6-rail">
      <span class="eyebrow"><i class="pip"></i>CodeDeck · 开机即用</span>
      <div class="rail-items">
        <div class="ri" id="ri-0"><i class="bg"></i><i class="bar"></i><span class="n">01</span><div><b>新加坡直连 · 低至 12ms</b><small>美国 · 新加坡 · 日本 · 韩国 · 马来西亚五地可选</small></div></div>
        <div class="ri" id="ri-1"><i class="bg"></i><i class="bar"></i><span class="n">02</span><div><b>桌面端 / 浏览器一键连上</b><small>填一次地址，之后打开自动登录</small></div></div>
        <div class="ri" id="ri-2"><i class="bg"></i><i class="bar"></i><span class="n">03</span><div><b>每一步操作由你审批</b><small>改文件、跑命令前先问你，不碰你的电脑</small></div></div>
        <div class="ri" id="ri-3"><i class="bg"></i><i class="bar"></i><span class="n">04</span><div><b>合上电脑，照样通宵跑</b><small>systemd 7×24 守护，断线输出自动补齐</small></div></div>
        <div class="ri" id="ri-4"><i class="bg"></i><i class="bar"></i><span class="n">05</span><div><b>代码和凭据留在你的服务器</b><small>单用户实例，不经任何第三方中转</small></div></div>
      </div>
    </div>
    <div class="stage" id="s6-stage">
      <div class="pnl" id="p-globe">
        <div class="globe-card">
          <div class="map-head"><span class="map-title"><i class="pip"></i>五个部署地区</span><span class="map-dist">独立公网 IP · 一人一台</span></div>
          <div class="globe-box"><canvas id="g-canvas" width="2024" height="1080"></canvas></div>
          <div class="node-pills"><div class="node-pill"><span class="nt">🇺🇸 美国</span><span class="nm">~120ms</span></div><div class="node-pill active"><span class="nt">🇸🇬 新加坡</span><span class="nm">~12ms</span></div><div class="node-pill"><span class="nt">🇯🇵 日本</span><span class="nm">~35ms</span></div><div class="node-pill"><span class="nt">🇰🇷 韩国</span><span class="nm">~28ms</span></div><div class="node-pill"><span class="nt">🇲🇾 马来西亚</span><span class="nm">~22ms</span></div></div>
        </div>
      </div>
      <div class="pnl" id="p-launch">
        <div class="launcher" id="s6-launcher">
          <div class="win-bar"><span class="lights"><i></i><i></i><i></i></span><span class="title">CodeDeck 启动器</span></div>
          <div class="launcher-body">
            <div class="l-side"><p class="l-lbl">启动器</p><div class="l-nav">__ICO_terminal__本机</div><div class="l-nav on">__ICO_monitor__远程服务器<em>2</em></div></div>
            <div class="l-main">
              <div class="l-head"><div><h4>远程服务器</h4><p>保存一次，之后打开自动登录</p></div><span class="gbtn pri">添加服务器</span></div>
              <div class="l-row on"><span class="l-dot"></span><div class="l-info"><b>新加坡 · 主力机</b><small>root@sg-01 · 专属 HTTPS 地址 · 已保存</small></div><span class="gbtn pri" id="s6-connect"><span id="s6-cbtn">连接</span></span></div>
              <div class="l-row"><span class="l-dot"></span><div class="l-info"><b>东京 · 备用机</b><small>root@jp-01 · 专属 HTTPS 地址 · 已保存</small></div><span class="gbtn">连接</span></div>
            </div>
          </div>
        </div>
      </div>
      <div class="pnl" id="p-app">
        <div class="remote-pill" id="s6-pill" style="transform:translateX(-50%)"><b id="s6-pill-a">CodeDeck 已连接</b><span class="dv"></span><span class="loc"><i></i>新加坡 · 主力机</span><span class="ms">12ms</span></div>
        __APP_S6__
      </div>
      <div class="pnl" id="p-time">
        <div class="timeline card">
          <div class="tl-axis-row"><span></span><div class="tl-axis" id="tl-axis"><span style="left:0;transform:none">18:00</span><span style="left:20%">21:00</span><span style="left:40%">00:00</span><span style="left:60%">03:00</span><span style="left:80%">06:00</span><span style="left:100%;transform:translateX(-100%)">09:00</span></div></div>
          <div class="tl-row"><span class="tl-label">__ICO_laptop__你的笔记本</span><div class="tl-bar"><div class="tl-clip" id="tl-c1"><span class="tl-seg tl-on" style="left:0;width:36.7%">在线</span><span class="tl-seg tl-off" style="left:36.7%;width:60%">23:30 合上电脑 · 离线</span><span class="tl-seg tl-on" style="left:96.7%;width:3.3%"></span></div><i class="tl-head" id="tl-h1"></i></div></div>
          <div class="tl-row"><span class="tl-label">__ICO_server__服务器上的会话</span><div class="tl-bar"><div class="tl-clip" id="tl-c2"><span class="tl-seg tl-run" style="left:0;width:100%">运行中 · 重构订单模块</span></div><i class="tl-head" id="tl-h2"></i><span class="tl-mark" id="tl-m1" style="left:50%"><span>01:30 重构完成</span></span><span class="tl-mark" id="tl-m2" style="left:73.3%"><span>05:00 测试通过</span></span></div></div>
        </div>
        <div class="use-grid">
          <div class="use" id="use-1"><span class="tile">__ICO_moon__</span><b>通宵跑长任务</b><p>大重构、批量补测试交给 Claude，关掉电脑也不会中断</p></div>
          <div class="use" id="use-2"><span class="tile">__ICO_clock__</span><b>断线自动补齐</b><p>第二天打开，离线期间的终端和对话输出一条不少</p></div>
        </div>
        __PHONE_TL__
      </div>
      <div class="pnl" id="p-sec">
        <div class="route" id="sec-route" style="grid-template-columns:1fr 1.05fr 1fr;padding:0 26px;gap:22px">
          <div class="route-end"><span class="route-ico">__ICO_devices__</span><div><b>你的电脑</b><small>只负责显示和审批</small></div></div>
          <div class="route-mid"><span class="route-pill">__ICO_lock__专属 HTTPS 地址</span><div class="route-track"><i id="sec-d1"></i><i id="sec-d2"></i></div><div class="route-tags"><span>HTTPS + HSTS</span><span>一次性登录码</span></div></div>
          <div class="route-end srv"><span class="route-ico">__ICO_server__</span><div><b>你的海外服务器</b><small>root@sg-01 · 单用户</small></div></div>
        </div>
        <div class="sec-vault" id="sec-vault">
          <div class="vault-head">__ICO_server__只存在你自己的服务器上<span class="mono">root@sg-01 · ~/.claude</span></div>
          <div class="vault-body">
            <div class="vi" id="vi-1"><span class="tile">__ICO_folder__</span><div><b>代码</b><small>~/shop · ~/api</small></div><span class="lk">__ICO_lock__</span></div>
            <div class="vi" id="vi-2"><span class="tile">__ICO_chat__</span><div><b>会话记录</b><small>对话 · 附件 · 终端</small></div><span class="lk">__ICO_lock__</span></div>
            <div class="vi" id="vi-3"><span class="tile claude">__ICO_key__</span><div><b>Claude 凭据</b><small>你自己的账号授权</small></div><span class="lk">__ICO_lock__</span></div>
          </div>
        </div>
        <div class="pillars">
          <div class="pillar" id="pl-1"><span class="tile green">__ICO_split__</span><b>和你的电脑隔离</b><p>依赖装坏、配置改乱，主力机都不受影响</p></div>
          <div class="pillar" id="pl-2"><span class="tile green">__ICO_shield__</span><b>每一步由你批准</b><p>允许一次、允许并记住，或者拒绝</p></div>
          <div class="pillar hl" id="pl-3"><span class="tile green">__ICO_server__</span><b>数据留在你的服务器</b><p>代码、会话和 Claude 凭据都不出你的机器</p></div>
          <div class="pillar" id="pl-4"><span class="tile green">__ICO_lock__</span><b>登录和访问有防护</b><p>HTTPS + HSTS，失败过多自动锁定</p></div>
        </div>
      </div>
    </div>

    <div class="hero-wrap" id="s6-hero">
      <div class="desk" id="s6-desk">
        <div class="desk-amb"></div>
        <div class="mb"><b>CodeDeck</b><span>文件</span><span>编辑</span><span>显示</span><span>环境</span><span>窗口</span><span>帮助</span><div class="mb-r">__ICO_wifi__<span>周四 05:00</span></div></div>
        <div class="remote-pill" style="left:50%"><b>CodeDeck 已连接</b><span class="dv"></span><span class="loc"><i></i>新加坡 · 主力机</span><span class="ms">12ms</span></div>
        __APP_HERO__
        __PHONE_HERO__
      </div>
      <div class="float-badge" id="fb-1" style="left:0;top:500px"><span class="tile green">__ICO_server__</span><div><small>海外独立服务器</small><b class="big">每月几十块</b></div></div>
      <div class="float-badge" id="fb-2" style="right:0;top:36px"><span class="tile ink">__ICO_bolt__</span><div><b>海外专属工位</b><small>独立公网 IP · 7×24 在线</small></div></div>
    </div>

    <div class="cta" id="s6-cta">
      <div class="cta-glow"></div>
      <div class="brand-row">__LOGO__<b>CodeDeck</b></div>
      <h1 class="display">每月几十块，给 Claude 安个<br><em>稳如泰山的海外专属工位</em></h1>
      <p>海外服务器直连，Claude Code 开机即用</p>
      <div class="acts"><span class="btn btn-white">__ICO_download__下载桌面端</span><span class="btn btn-glass">__ICO_globe__浏览器一键连上</span></div>
      <div class="ck"><span>__ICO_check__新加坡 12ms 直连</span><span>__ICO_check__每一步由你审批</span><span>__ICO_check__合上电脑照样跑</span><span>__ICO_check__凭据只在你的服务器</span></div>
    </div>

    <svg id="cursor" viewBox="0 0 36 36"><path d="M7 4.5 L28.5 16 L18.5 19 L23.5 29.5 L19 31.5 L14 21 L7 27 Z" fill="#18181B" stroke="#FFFFFF" stroke-width="2.4" stroke-linejoin="round"/></svg>
  </div>

  <div id="subbar"><div id="sub-pill"></div></div>
</div>

<script>
// ============ 纯时间函数工具（禁止 Math.random / CSS 动画） ============
function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
function smoothstep(a, b, x) { const u = clamp((x - a) / (b - a), 0, 1); return u * u * (3 - 2 * u); }
function easeOut(u) { u = clamp(u, 0, 1); return 1 - Math.pow(1 - u, 3); }
function easeInOut(u) { u = clamp(u, 0, 1); return u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2; }
function hash(n) { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453123; return x - Math.floor(x); }
function spring(x, w = 15, z = 0.74) {
  if (x <= 0) return 0;
  const wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * x) * (Math.cos(wd * x) + (z * w / wd) * Math.sin(wd * x));
}
const $ = (id) => document.getElementById(id);
const fmtN = (n) => Math.round(n).toLocaleString('en-US');
// 进场：s 为弹簧值；dy/dx 位移、sc 起始缩放
function enter(el, s, o = {}) {
  const dy = o.dy ?? 26, dx = o.dx ?? 0, sc = o.sc ?? 1, k = o.k ?? 1, rot = o.rot ?? 0;
  el.style.opacity = clamp(s * 1.6, 0, 1) * k;
  el.style.transform = `${o.pre || ''} translate(${(1 - s) * dx}px, ${(1 - s) * dy}px) scale(${sc + (1 - sc) * s}) rotate(${(1 - s) * rot}deg)`;
}
// 进场 + 出场的面板
function panel(el, lt, tin, tout, o = {}) {
  const s = spring(lt - tin, o.w ?? 14, o.z ?? 0.8);
  const out = tout == null ? 0 : smoothstep(tout - (o.fade ?? 0.28), tout, lt);
  const vis = lt >= tin - 0.001 && out < 0.999;
  el.style.display = vis ? '' : 'none';
  if (!vis) return 0;
  const dy = (1 - s) * (o.dy ?? 30) - out * (o.outDy ?? 18);
  const sc = (o.sc ?? 0.97) + (1 - (o.sc ?? 0.97)) * s;
  el.style.opacity = clamp(s * 1.5, 0, 1) * (1 - out);
  el.style.transform = `translateY(${dy}px) scale(${sc - out * 0.02})`;
  return s * (1 - out);
}
// 同一行里先出后进的文字切换（不叠字）
function swapText(a, b, lt, at) {
  const so = smoothstep(at, at + 0.22, lt);
  a.style.opacity = 1 - so; a.style.transform = `translateY(${-so * 40}px)`;
  const si = spring(lt - at - 0.2, 16, 0.82);
  b.style.opacity = clamp(si * 1.6, 0, 1); b.style.transform = `translateY(${(1 - si) * 44}px)`;
}
function reveal(el, lt, at) { // 从下往上露出（父级 .swap 裁切）
  const s = spring(lt - at, 15, 0.82);
  el.style.opacity = clamp(s * 1.6, 0, 1); el.style.transform = `translateY(${(1 - s) * 60}px)`;
}
function rectIn(el, host) { const a = el.getBoundingClientRect(), b = host.getBoundingClientRect(); return { x: a.left - b.left, y: a.top - b.top, w: a.width, h: a.height }; }

// ============ 时间轴（构建时由 audio/vo_timeline.json 注入） ============
const TL = __TIMELINE_JSON__;
const SCN = TL.scenes, SUBS = TL.subs, DURATION = TL.total;
const VO_END = TL.vo_end ?? SCN[SCN.length - 1].end;
const CHAPTERS = ['01 · 风控破防', '02 · 下乡收号', '03 · 算一笔账', '04 · 为什么是 Claude', '05 · CodeDeck 登场', '06 · 开机即用'];
function fmtTime(s) { const m = Math.floor(s / 60); return `0${m}:${(s % 60).toFixed(1).padStart(4, '0')}`; }

// ============ 第 1 镜：手绘小摩托 ============
function drawScooter(ctx, x, y, s, t, flag = true) {
  ctx.save();
  ctx.translate(x, y + Math.sin(t * 34) * 2.4 * s);
  ctx.scale(s, s);
  ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.strokeStyle = '#18181b'; ctx.lineWidth = 4.5;
  ctx.fillStyle = 'rgba(24,24,27,.10)'; ctx.beginPath(); ctx.ellipse(0, 4, 140, 11, 0, 0, Math.PI * 2); ctx.fill();
  if (flag) {
    ctx.beginPath(); ctx.moveTo(-100, -100); ctx.lineTo(-122, -236); ctx.stroke();
    const wv = Math.sin(t * 15) * 5;
    ctx.fillStyle = '#dc2626'; ctx.beginPath();
    ctx.moveTo(-122, -236); ctx.quadraticCurveTo(-176, -246 + wv, -236, -232);
    ctx.lineTo(-232, -184); ctx.quadraticCurveTo(-174, -198 + wv, -116, -190); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#fff'; ctx.font = '700 23px "PingFang SC","Noto Sans CJK SC",sans-serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('下乡收号', -176, -212 + wv * 0.5);
  }
  for (const wx of [-74, 80]) {               // 车轮
    ctx.fillStyle = '#18181b'; ctx.beginPath(); ctx.arc(wx, -32, 32, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#e4e4e7'; ctx.beginPath(); ctx.arc(wx, -32, 14, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = '#a1a1aa'; ctx.lineWidth = 3;
    for (let k = 0; k < 3; k++) { const a = t * 26 + k * 2.094; ctx.beginPath(); ctx.moveTo(wx, -32); ctx.lineTo(wx + Math.cos(a) * 13, -32 + Math.sin(a) * 13); ctx.stroke(); }
    ctx.strokeStyle = '#18181b'; ctx.lineWidth = 4.5;
  }
  ctx.fillStyle = '#d97757';                  // 车身
  ctx.beginPath(); ctx.moveTo(-136, -46); ctx.bezierCurveTo(-142, -96, -106, -116, -50, -110);
  ctx.bezierCurveTo(-26, -108, -20, -86, -24, -62); ctx.lineTo(-40, -46); ctx.closePath(); ctx.fill(); ctx.stroke();
  ctx.beginPath(); ctx.roundRect(-44, -74, 108, 20, 10); ctx.fill(); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(50, -60); ctx.lineTo(68, -128); ctx.bezierCurveTo(86, -126, 104, -98, 108, -60); ctx.closePath(); ctx.fill(); ctx.stroke();
  ctx.fillStyle = '#b85c3f'; ctx.beginPath(); ctx.moveTo(62, -66); ctx.lineTo(86, -156); ctx.lineTo(98, -153); ctx.lineTo(76, -64); ctx.closePath(); ctx.fill(); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(70, -160); ctx.lineTo(108, -152); ctx.stroke();
  ctx.fillStyle = '#fde68a'; ctx.beginPath(); ctx.arc(106, -118, 9, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  ctx.fillStyle = '#27272a'; ctx.beginPath(); ctx.roundRect(-118, -128, 86, 20, 10); ctx.fill();
  const limb = (pts, w, c) => {               // 人物四肢：先描边再填色
    for (const [lw, col] of [[w + 7, '#18181b'], [w, c]]) {
      ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]);
      for (let k = 1; k < pts.length; k++) ctx.lineTo(pts[k][0], pts[k][1]); ctx.stroke();
    }
  };
  limb([[-62, -124], [-4, -118], [6, -76]], 20, '#1e3a8a');      // 腿
  limb([[-66, -128], [-28, -206]], 40, '#0f766e');               // 躯干
  limb([[-26, -196], [26, -170], [74, -158]], 15, '#0f766e');    // 手臂
  ctx.strokeStyle = '#18181b'; ctx.lineWidth = 4.5;
  ctx.fillStyle = '#facc15'; ctx.beginPath(); ctx.arc(-18, -238, 28, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  ctx.fillStyle = '#18181b'; ctx.beginPath(); ctx.roundRect(-6, -246, 28, 15, 7); ctx.fill();
  ctx.restore();
}

// ============ 第 2 镜：印尼点阵地图 ============
const MAP = (() => {
  const W = 896, H = 390, LON0 = 95.2, LAT0 = 5.3, K = 26.5;
  const P = (lon, lat) => [(lon - LON0) * K, (LAT0 - lat) * K];
  const shapes = [
    [[95.3,5.6],[97.5,5.2],[98.7,3.8],[100.4,2.2],[101.6,1.7],[103.0,0.6],[103.8,-1.0],[104.6,-2.3],[106.0,-3.2],[105.9,-5.8],[104.6,-5.9],[103.4,-4.8],[102.3,-4.0],[101.0,-2.6],[100.3,-1.0],[99.2,0.2],[98.6,1.7],[97.4,2.6],[96.2,4.1]],
    [[105.2,-6.8],[106.1,-6.0],[107.0,-5.95],[108.3,-6.3],[110.4,-6.9],[111.5,-6.6],[112.7,-6.9],[114.4,-7.7],[114.5,-8.6],[113.2,-8.3],[111.0,-8.2],[109.0,-7.8],[107.5,-7.6],[106.4,-7.4],[105.4,-6.9]],
    [[114.5,-8.1],[115.2,-8.05],[115.7,-8.4],[115.2,-8.85],[114.6,-8.45]],
    [[116.0,-8.3],[116.7,-8.3],[116.7,-8.9],[116.0,-8.9]],
    [[117.0,-8.4],[119.0,-8.3],[119.0,-8.9],[117.0,-9.0]],
    [[108.9,0.4],[109.6,1.9],[111.3,2.6],[113.0,3.2],[115.5,5.0],[117.6,6.3],[119.2,5.2],[118.0,4.4],[117.9,1.0],[119.0,0.9],[117.5,-0.8],[116.5,-2.0],[116.3,-3.5],[114.6,-4.0],[113.0,-3.2],[111.7,-3.0],[110.2,-2.9],[110.0,-1.8],[109.1,-0.8]],
    [[100.3,6.4],[102.3,6.0],[103.4,4.8],[103.5,2.8],[104.2,1.5],[103.5,1.3],[102.3,2.0],[101.3,2.8],[100.6,4.2]],
    [[118.8,-2.6],[119.5,-0.5],[119.9,0.6],[120.9,1.3],[124.9,1.6],[123.3,0.4],[120.6,0.5],[120.9,-1.3],[123.3,-1.0],[121.8,-1.9],[122.9,-4.5],[121.5,-4.8],[120.3,-2.9],[120.4,-5.6],[119.4,-5.5],[119.5,-3.5]],
    [[105.1,-1.6],[106.2,-1.9],[106.8,-3.0],[106.0,-3.1],[105.4,-2.3]],
    [[107.6,-2.6],[108.3,-2.6],[108.3,-3.2],[107.6,-3.2]],
  ].map(s => s.map(([a, b]) => P(a, b)));
  const inside = (x, y, poly) => { let c = false; for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) { const [xi, yi] = poly[i], [xj, yj] = poly[j]; if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c; } return c; };
  const dots = [];
  for (let y = 5; y < H; y += 9) for (let x = 5 + ((y / 9) % 2) * 4.5; x < W; x += 9) if (shapes.some(p => inside(x, y, p))) dots.push([x, y]);
  const way = [[115.2,-8.65],[114.4,-8.2],[112.7,-7.35],[110.4,-7.05],[108.6,-6.8],[106.8,-6.25],[106.0,-5.95],[105.5,-5.5],[105.0,-4.6],[104.75,-3.0],[103.6,-1.6],[102.6,-0.4],[101.5,0.45]].map(([a, b]) => P(a, b));
  const pts = [];
  for (let i = 0; i < way.length - 1; i++) {        // Catmull-Rom 平滑
    const p0 = way[Math.max(0, i - 1)], p1 = way[i], p2 = way[i + 1], p3 = way[Math.min(way.length - 1, i + 2)];
    for (let k = 0; k < 16; k++) { const u = k / 16, u2 = u * u, u3 = u2 * u;
      pts.push([0, 1].map(d => 0.5 * ((2 * p1[d]) + (-p0[d] + p2[d]) * u + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * u2 + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * u3))); }
  }
  pts.push(way[way.length - 1]);
  const acc = [0]; for (let i = 1; i < pts.length; i++) acc.push(acc[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  const L = acc[acc.length - 1];
  const at = (p) => { const d = p * L; let i = 1; while (i < acc.length - 1 && acc[i] < d) i++; const u = (d - acc[i - 1]) / Math.max(1e-6, acc[i] - acc[i - 1]); return [pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * u, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * u, i]; };
  return { W, H, dots, pts, at, start: way[0], end: way[way.length - 1] };
})();
function pillLabel(ctx, x, y, text, dark, dir) {
  ctx.font = '600 20px "Inter","PingFang SC","Noto Sans CJK SC",sans-serif';
  const w = ctx.measureText(text).width + 30, h = 38;
  let bx = dir === 'left' ? x - w - 18 : dir === 'right' ? x + 18 : x - w / 2, by = dir === 'top' ? y - h - 18 : dir === 'bottom' ? y + 18 : y - h / 2;
  bx = clamp(bx, 6, MAP.W - w - 6); by = clamp(by, 6, MAP.H - h - 6);
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.14)'; ctx.shadowBlur = 12; ctx.shadowOffsetY = 3;
  ctx.fillStyle = dark ? '#18181b' : '#fff'; ctx.beginPath(); ctx.roundRect(bx, by, w, h, 19); ctx.fill(); ctx.restore();
  ctx.strokeStyle = dark ? '#18181b' : 'rgba(0,0,0,.1)'; ctx.lineWidth = 1; ctx.beginPath(); ctx.roundRect(bx, by, w, h, 19); ctx.stroke();
  ctx.fillStyle = dark ? '#fff' : '#18181b'; ctx.textBaseline = 'middle'; ctx.textAlign = 'left'; ctx.fillText(text, bx + 15, by + h / 2 + 1);
}
function drawMap(lt) {
  const c = $('s2-canvas'), ctx = c.getContext('2d');
  ctx.setTransform(2, 0, 0, 2, 0, 0); ctx.clearRect(0, 0, MAP.W, MAP.H);
  const grow = smoothstep(0.15, 0.9, lt);
  ctx.fillStyle = 'rgba(71,85,105,.58)'; ctx.beginPath();
  for (const [x, y] of MAP.dots) { if (hash(x * 3.1 + y * 7.7) > grow * 1.15) continue; ctx.moveTo(x + 2.7, y); ctx.arc(x, y, 2.7, 0, Math.PI * 2); }
  ctx.fill();
  const prog = easeInOut(clamp((lt - 0.7) / 3.3, 0, 1));
  ctx.setLineDash([3, 7]); ctx.strokeStyle = 'rgba(24,24,27,.22)'; ctx.lineWidth = 3;
  ctx.beginPath(); MAP.pts.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.stroke();
  const head = MAP.at(prog);
  ctx.setLineDash([10, 8]); ctx.lineDashOffset = -lt * 40; ctx.strokeStyle = '#d97757'; ctx.lineWidth = 5;
  ctx.beginPath(); for (let i = 0; i < head[2]; i++) i ? ctx.lineTo(MAP.pts[i][0], MAP.pts[i][1]) : ctx.moveTo(MAP.pts[i][0], MAP.pts[i][1]);
  ctx.lineTo(head[0], head[1]); ctx.stroke(); ctx.setLineDash([]);
  for (const [p, on] of [[MAP.start, true], [MAP.end, prog > 0.995]]) {
    ctx.fillStyle = on ? '#d97757' : '#18181b'; ctx.strokeStyle = '#fff'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.arc(p[0], p[1], 8, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  }
  const ring = (lt * 1.2) % 1;
  ctx.strokeStyle = `rgba(217,119,87,${(1 - ring) * 0.8})`; ctx.lineWidth = 2.5;
  ctx.beginPath(); ctx.arc(head[0], head[1], 8 + ring * 26, 0, Math.PI * 2); ctx.stroke();
  if (prog < 0.995) drawScooter(ctx, head[0] + 4, head[1] + 10, 0.24, lt, false);
  pillLabel(ctx, MAP.start[0], MAP.start[1], '🇮🇩 巴厘岛 · 出发', false, 'left');
  pillLabel(ctx, MAP.end[0], MAP.end[1], '苏门答腊 · 进村收号', prog > 0.995, 'right');
}

// ============ 第 6 镜：官网同款点阵地球（数据来自官网） ============
const GLOBE = (() => {
  const bin = atob('__GLOBE_B64__');
  const toSphere = (gx, gy) => { const lng = (20 + (gx / 132) * 360) * Math.PI / 180, lat = (75 - (gy / 58.02) * 140) * Math.PI / 180; return [Math.cos(lat) * Math.sin(lng), Math.sin(lat), Math.cos(lat) * Math.cos(lng)]; };
  const land = []; for (let i = 0; i + 3 < bin.length; i += 4) land.push(toSphere((bin.charCodeAt(i) | (bin.charCodeAt(i + 1) << 8)) / 10, (bin.charCodeAt(i + 2) | (bin.charCodeAt(i + 3) << 8)) / 10));
  const NODES = {
    us: { name: '美国', flag: '🇺🇸', ms: '120ms', dir: 'top', vec: toSphere(99.0, 20.8) },
    jp: { name: '日本', flag: '🇯🇵', ms: '35ms', dir: 'right', vec: toSphere(39.5, 19.9) },
    kr: { name: '韩国', flag: '🇰🇷', ms: '28ms', dir: 'left', vec: toSphere(33.5, 18.2) },
    my: { name: '马来西亚', flag: '🇲🇾', ms: '22ms', dir: 'left', vec: toSphere(18.5, 39.0) },
    sg: { name: '新加坡', flag: '🇸🇬', ms: '12ms', dir: 'bottom', vec: toSphere(22.0, 41.6) },
  };
  const ARCS = [['sg', 'my'], ['sg', 'jp'], ['jp', 'kr'], ['jp', 'us']];
  const rot = (v, rx, ry) => { const cy = Math.cos(ry), sy = Math.sin(ry), x1 = v[0] * cy - v[2] * sy, z1 = v[0] * sy + v[2] * cy, cx = Math.cos(rx), sx = Math.sin(rx); return [x1, v[1] * cx - z1 * sx, v[1] * sx + z1 * cx]; };
  const slerp = (a, b, t) => { const d = clamp(a[0] * b[0] + a[1] * b[1] + a[2] * b[2], -1, 1), om = Math.acos(d); if (om < 1e-3) return a; const so = Math.sin(om), s1 = Math.sin((1 - t) * om) / so, s2 = Math.sin(t * om) / so; return [s1 * a[0] + s2 * b[0], s1 * a[1] + s2 * b[1], s1 * a[2] + s2 * b[2]]; };
  const lift = (v, t) => { const s = 1 + Math.sin(t * Math.PI) * 0.14; return [v[0] * s, v[1] * s, v[2] * s]; };
  const aim = (k) => { const v = NODES[k].vec; return [Math.atan2(v[1], Math.hypot(v[0], v[2])), Math.atan2(v[0], v[2])]; };
  function draw(ctx, W, H, rx, ry, tms, active, S) {
    const cx = W / 2, cy = H / 2, R = Math.min(W, H) * 0.44, TAU = Math.PI * 2;
    ctx.clearRect(0, 0, W, H);
    const halo = ctx.createRadialGradient(cx, cy, R * 0.9, cx, cy, R * 1.18);
    halo.addColorStop(0, 'rgba(16,185,129,.12)'); halo.addColorStop(.5, 'rgba(16,185,129,.04)'); halo.addColorStop(1, 'rgba(16,185,129,0)');
    ctx.fillStyle = halo; ctx.beginPath(); ctx.arc(cx, cy, R * 1.18, 0, TAU); ctx.fill();
    const sph = ctx.createRadialGradient(cx - R * .35, cy - R * .35, R * .05, cx, cy, R);
    sph.addColorStop(0, '#ffffff'); sph.addColorStop(.65, '#f8fafc'); sph.addColorStop(1, '#e2e8f0');
    ctx.fillStyle = sph; ctx.beginPath(); ctx.arc(cx, cy, R, 0, TAU); ctx.fill();
    ctx.strokeStyle = 'rgba(226,232,240,.85)'; ctx.lineWidth = 1; ctx.stroke();
    const P = land.map(v => rot(v, rx, ry));
    ctx.fillStyle = 'rgba(203,213,225,.35)'; ctx.beginPath();
    for (const p of P) { if (p[2] >= 0) continue; const x = cx + p[0] * R, y = cy - p[1] * R; ctx.moveTo(x + 1.1 * S, y); ctx.arc(x, y, 1.1 * S, 0, TAU); } ctx.fill();
    ARCS.forEach((a, idx) => {
      const v1 = NODES[a[0]].vec, v2 = NODES[a[1]].vec, pts = []; let z = 0;
      for (let s = 0; s <= 28; s++) { const p = rot(lift(slerp(v1, v2, s / 28), s / 28), rx, ry); pts.push([cx + p[0] * R, cy - p[1] * R]); z += p[2]; }
      z /= 29; if (z <= -0.2) return;
      ctx.strokeStyle = `rgba(16,185,129,${clamp((z + .2) * 1.5, .15, .75).toFixed(3)})`; ctx.lineWidth = 1.5 * S; ctx.setLineDash([3 * S, 4 * S]);
      ctx.beginPath(); pts.forEach((p, j) => j ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.stroke(); ctx.setLineDash([]);
      const tp = (tms / 1800 + idx * .25) % 1, pp = rot(lift(slerp(v1, v2, tp), tp), rx, ry);
      if (pp[2] <= -0.1) return;
      ctx.fillStyle = '#10b981'; ctx.shadowColor = '#10b981'; ctx.shadowBlur = 8 * S;
      ctx.beginPath(); ctx.arc(cx + pp[0] * R, cy - pp[1] * R, 2.5 * S, 0, TAU); ctx.fill(); ctx.shadowBlur = 0;
    });
    for (let b = 0; b < 8; b++) {
      const lv = (b + .5) / 8, r = (1 + .5 * lv) * S * 0.95;
      ctx.fillStyle = `rgba(71,85,105,${(.35 + .65 * lv).toFixed(3)})`; ctx.beginPath();
      for (const p of P) { if (p[2] < 0 || Math.min(7, Math.floor(p[2] * 8)) !== b) continue; const x = cx + p[0] * R, y = cy - p[1] * R; ctx.moveTo(x + r, y); ctx.arc(x, y, r, 0, TAU); }
      ctx.fill();
    }
    const shown = [];
    Object.keys(NODES).forEach((k, n) => {
      const nd = NODES[k], p = rot(nd.vec, rx, ry); if (p[2] <= -0.15) return;
      const sx = cx + p[0] * R, sy = cy - p[1] * R, on = k === active; shown.push({ nd, sx, sy, sz: p[2], on });
      const tt = (tms / 30 + n * 25) % 45, ring = Math.max(0, (1 - tt / 45) * Math.max(.2, (p[2] + .15) * 1.2));
      ctx.strokeStyle = `rgba(16,185,129,${(on ? ring : ring * .7).toFixed(3)})`; ctx.lineWidth = 1.5 * S;
      ctx.beginPath(); ctx.arc(sx, sy, (4 + tt * .45) * S, 0, TAU); ctx.stroke();
      ctx.shadowColor = 'rgba(0,0,0,.2)'; ctx.shadowBlur = 4 * S; ctx.fillStyle = on ? '#10b981' : '#18181b';
      ctx.beginPath(); ctx.arc(sx, sy, (on ? 5.5 : 4.5) * S, 0, TAU); ctx.fill(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 2 * S; ctx.stroke(); ctx.shadowBlur = 0;
    });
    shown.forEach((it) => {
      if (it.sz <= .05) return;
      const nd = it.nd, lab = `${nd.flag} ${nd.name}`, ms = ` · ${nd.ms}`;
      ctx.save(); ctx.globalAlpha = Math.min(1, (it.sz - .05) * 4);
      ctx.font = `600 ${12 * S}px "Inter","PingFang SC","Noto Sans CJK SC",sans-serif`; const w1 = ctx.measureText(lab).width;
      ctx.font = `500 ${11 * S}px "JetBrains Mono","SF Mono",monospace`; const w2 = ctx.measureText(ms).width;
      const bw = w1 + w2 + 20 * S, bh = 24 * S, d = nd.dir;
      let bx = d === 'left' ? it.sx - bw - 14 * S : d === 'right' ? it.sx + 14 * S : it.sx - bw / 2;
      let by = d === 'left' || d === 'right' ? it.sy - bh / 2 : d === 'bottom' ? it.sy + 14 * S : it.sy - 30 * S;
      bx = clamp(bx, 4, W - bw - 4); by = clamp(by, 4, H - bh - 4);
      const lx = d === 'left' ? bx + bw : d === 'right' ? bx : clamp(it.sx, bx + 8, bx + bw - 8), ly = d === 'left' || d === 'right' ? by + bh / 2 : d === 'bottom' ? by : by + bh;
      ctx.strokeStyle = it.on ? '#18181b' : 'rgba(0,0,0,.2)'; ctx.lineWidth = 1; ctx.setLineDash([2, 2]); ctx.beginPath(); ctx.moveTo(it.sx, it.sy); ctx.lineTo(lx, ly); ctx.stroke(); ctx.setLineDash([]);
      ctx.shadowColor = it.on ? 'rgba(0,0,0,.25)' : 'rgba(0,0,0,.08)'; ctx.shadowBlur = (it.on ? 10 : 6) * S; ctx.shadowOffsetY = 2;
      ctx.fillStyle = it.on ? '#18181b' : '#fff'; ctx.beginPath(); ctx.roundRect(bx, by, bw, bh, bh / 2); ctx.fill();
      ctx.shadowBlur = 0; ctx.shadowOffsetY = 0; ctx.strokeStyle = it.on ? '#18181b' : 'rgba(0,0,0,.1)'; ctx.stroke();
      ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
      ctx.font = `600 ${12 * S}px "Inter","PingFang SC","Noto Sans CJK SC",sans-serif`; ctx.fillStyle = it.on ? '#fff' : '#18181b'; ctx.fillText(lab, bx + 10 * S, by + bh / 2 + 1);
      ctx.font = `500 ${11 * S}px "JetBrains Mono","SF Mono",monospace`; ctx.fillStyle = it.on ? '#6ee7b7' : '#047857'; ctx.fillText(ms, bx + 10 * S + w1, by + bh / 2 + 1);
      ctx.restore();
    });
  }
  return { draw, aim };
})();

// ============ 各镜头 ============
const S1 = { cardIn: [0.25, 0.4, 0.55], act: [4.0, 4.85, 5.65], foot: 6.55, l2: 9.0, ride0: 8.85, ride1: 10.95, stamp: 11.15 };
const s1X = (t) => -330 + 2560 * clamp((t - S1.ride0) / (S1.ride1 - S1.ride0), 0, 1);
const S1_HIT = [0, 1, 2].map(i => { const cx = 96 + 586 * i + 277; for (let k = 0; k < 400; k++) { const tt = S1.ride0 + k / 120; if (s1X(tt) + 120 >= cx - 140) return tt; } return 99; });
function renderScene1(t) {
  enter($('s1-eb'), spring(t - 0.0, 16, 0.8), { dy: 18 });
  reveal($('s1-l1'), t, 0.08);
  reveal($('s1-l2'), t, S1.l2);
  const sm = spring(t - 0.1, 14, 0.8); enter($('s1-meter'), sm, { dy: 20, sc: 0.96 });
  const n = 800 * easeOut((t - 0.4) / 2.4);
  $('s1-count').textContent = fmtN(Math.max(0, n));
  $('s1-bar').style.width = `${(Math.max(0, n) / 800 * 100).toFixed(1)}%`;
  const allOn = t >= S1.act[2], broken = t >= S1.stamp;
  $('s1-st').textContent = broken ? '已被破防' : allOn ? '全部启用' : '逐层加码';
  $('s1-st').className = broken ? 'chipx dark st' : 'chipx bad st';
  enter($('s1-foot'), spring(t - S1.foot, 18, 0.6), { dy: 10, sc: 0.9 });
  for (let i = 0; i < 3; i++) {   // 被小摩托撞飞：先轻轻弹起，再翻滚着掉出画面（只往右下走，不遮标题）
    const el = $(`fw-${i + 1}`), se = spring(t - S1.cardIn[i], 15, 0.74);
    const tau = clamp(t - S1_HIT[i], 0, 0.9);
    el.style.transformOrigin = '50% 100%';
    el.style.opacity = clamp(se * 1.6, 0, 1) * (1 - smoothstep(0.42, 0.72, tau));
    el.style.transform = `translate(${260 * tau}px, ${(1 - se) * 60 - 240 * tau + 1300 * tau * tau}px) rotate(${(36 + i * 6) * tau}deg)`;
    const on = t >= S1.act[i], pulse = spring(t - S1.act[i], 18, 0.55);
    const chip = $(`fs-${i + 1}`); chip.textContent = on ? '拦截中' : '待命'; chip.className = on ? 'chipx bad' : 'chipx';
    $(`fr-${i + 1}`).style.opacity = on ? clamp(pulse, 0, 1) * (1 - smoothstep(0, 0.25, tau)) : 0;
  }
  $('s1-scan').style.top = `${12 + 78 * (0.5 + 0.5 * Math.sin(t * 3.2))}px`;
  const c = $('s1-canvas'), ctx = c.getContext('2d');
  ctx.setTransform(2, 0, 0, 2, 0, 0); ctx.clearRect(0, 0, 1920, 812);
  if (t >= S1.ride0 && t <= S1.ride1 + 0.1) {
    const x = s1X(t), y = 778;
    ctx.strokeStyle = 'rgba(24,24,27,.16)'; ctx.lineWidth = 5; ctx.lineCap = 'round';
    for (let l = 0; l < 6; l++) { const ly = y - 46 - l * 40, len = 140 + hash(l * 3.3) * 220, x0 = x - 190 - hash(l) * 60; ctx.beginPath(); ctx.moveTo(x0, ly); ctx.lineTo(x0 - len, ly); ctx.stroke(); }
    for (let k = 0; k < 6; k++) { const px = x - 160 - k * 58, r = 12 + k * 6; ctx.fillStyle = `rgba(212,212,208,${0.55 * (1 - k / 6)})`; ctx.beginPath(); ctx.arc(px, y - 16 - k * 4, r, 0, Math.PI * 2); ctx.fill(); }
    drawScooter(ctx, x, y, 1.0, t);
  }
  const ss = spring(t - S1.stamp, 20, 0.5), st = $('s1-stamp');
  st.style.display = t >= S1.stamp ? '' : 'none';
  st.style.opacity = clamp(ss * 2, 0, 1);
  st.style.transform = `translate(-50%, -50%) rotate(${-8 + (1 - ss) * 10}deg) scale(${1.8 - 0.8 * ss})`;
}

function renderScene2(t) {
  const lt = t - SCN[1].start;
  enter($('s2-eb'), spring(lt, 16, 0.8), { dy: 18 });
  enter($('s2-title'), spring(lt - 0.08, 14, 0.82), { dy: 30 });
  const mapOut = 9.45;
  if (lt < mapOut + 0.3) { panel($('s2-map'), lt, 0.15, mapOut + 0.3, { dy: 40 }); drawMap(lt); } else $('s2-map').style.display = 'none';
  $('s2-dist').textContent = `${fmtN(1500 * easeInOut(clamp((lt - 0.7) / 3.3, 0, 1)))} km`;
  [[4.25, 's2-c1'], [5.3, 's2-c2'], [6.3, 's2-c3']].forEach(([at, id]) => { const el = $(id), on = lt >= at; el.className = on ? 'chipx ok' : 'chipx'; el.style.transform = `scale(${1 + 0.08 * Math.sin(Math.PI * clamp((lt - at) / 0.3, 0, 1))})`; });
  panel($('s2-acct'), lt, 9.6, null, { dy: 40, sc: 0.95 });
  [11.8, 12.2, 12.6].forEach((at, i) => enter($(`ac-${i + 1}`), spring(lt - at, 16, 0.7), { dx: 40, dy: 0 }));
  enter($('ac-foot'), spring(lt - 13.85, 16, 0.6), { dy: 20, sc: 0.9 });
  const sp = spring(lt - 0.45, 12, 0.78);
  $('s2-photo').style.opacity = clamp(sp * 1.6, 0, 1);
  $('s2-photo').style.transform = `translateY(${(1 - sp) * 80}px) rotate(${(1 - sp) * 6 + 1.6}deg)`;
  const z = smoothstep(7.0, 7.85, lt) * (1 - smoothstep(9.3, 10.1, lt));
  $('s2-zoom').style.transform = `scale(${1 + 0.6 * z})`;
  $('s2-hl').style.opacity = clamp(smoothstep(6.95, 7.3, lt) * 1, 0, 1) * (1 - smoothstep(9.3, 9.9, lt));
  enter($('s2-quote'), spring(lt - 7.45, 14, 0.7), { dx: -40, dy: 10, sc: 0.94, rot: -4 });
}

function renderScene3(t) {
  const lt = t - SCN[2].start;
  const sw = spring(lt - 0.05, 13, 0.8); enter($('s3-shot'), sw, { dx: -60, dy: 0, sc: 0.97 });
  const zm = 1 + 0.035 * easeInOut(clamp((lt - 0.5) / 16, 0, 1));   // 不裁窗口标题栏，只做缓慢推近
  $('img-moments').style.transform = `scale(${zm})`;
  const zx = (x) => 260 + (x - 260) * zm, zy = (y) => 244 + (y - 244) * zm;
  enter($('s3-src'), spring(lt - 3.0, 16, 0.75), { dy: 16 });
  const co = (id, at, x, y) => { const el = $(id); el.style.left = `${zx(x) - 8}px`; el.style.top = `${zy(y) - 30}px`; const s = spring(lt - at, 16, 0.72); el.style.opacity = clamp(s * 1.6, 0, 1); el.style.transform = `translateX(${(1 - s) * -20}px)`; };
  co('s3-co1', 5.2, 286, 213); co('s3-co2', 11.0, 280, 345);
  enter($('s3-eb'), spring(lt - 0.15, 16, 0.8), { dy: 16 });
  enter($('s3-title'), spring(lt - 0.25, 14, 0.82), { dy: 30 });
  enter($('s3-bill'), spring(lt - 0.6, 14, 0.8), { dy: 40, sc: 0.97 });
  const rows = [[5.2, 7.82, 159, 9.15], [11.0, 11.05, 360, 11.6], [12.74, 12.8, 520, 13.3]];
  rows.forEach(([rin, cnt, v, cny], i) => {
    const sr = spring(lt - rin, 16, 0.74), row = $(`br-${i + 1}`);   // 先占位（淡），念到时点亮
    row.style.opacity = 0.3 + 0.7 * clamp(sr * 1.6, 0, 1);
    row.style.transform = `translateX(${(1 - sr) * 24 * (lt >= rin ? 1 : 0)}px)`;
    $(`bu-${i + 1}`).textContent = lt < cnt ? '—' : fmtN(v * easeOut((lt - cnt) / 0.7));
    $(`bc-${i + 1}`).style.opacity = smoothstep(cny, cny + 0.3, lt);
  });
  enter($('s3-total'), spring(lt - 15.2, 15, 0.7), { dy: 24, sc: 0.96 });
  const tv = easeOut((lt - 15.25) / 0.8);
  $('s3-tv').textContent = `¥${fmtN(2500 * tv)}–${fmtN(3700 * tv)}+`;
  const ss = spring(lt - 16.3, 20, 0.5), st = $('s3-stamp');
  st.style.opacity = lt >= 16.3 ? clamp(ss * 2, 0, 1) : 0;
  st.style.transform = `rotate(${-10 + (1 - ss) * 14}deg) scale(${1.7 - 0.7 * ss})`;
}

function renderScene4(t) {
  const lt = t - SCN[3].start;
  enter($('s4-eb'), spring(lt, 16, 0.8), { dy: 16 });
  const sa = spring(lt - 0.08, 14, 0.82);
  if (lt < 7.39) { $('s4-a').style.opacity = clamp(sa * 1.6, 0, 1); $('s4-a').style.transform = `translateY(${(1 - sa) * 44}px)`; $('s4-b').style.opacity = 0; }
  else swapText($('s4-a'), $('s4-b'), lt, 7.39);
  [2.4, 3.6, 4.95].forEach((at, i) => enter($(`cap-${i + 1}`), spring(lt - at, 15, 0.74), { dx: -40, dy: 0, sc: 0.97 }));
  enter($('s4-app'), spring(lt - 0.3, 13, 0.8), { dx: 60, dy: 0, sc: 0.97 });
  enter($('s4-ask'), spring(lt - 0.75, 16, 0.75), { dy: 18 });
  enter($('s4-ai'), spring(lt - 1.4, 16, 0.75), { dy: 18 });
  [2.4, 3.4, 4.4, 5.5].forEach((at, i) => enter($(`s4-t${i + 1}`), spring(lt - at, 18, 0.8), { dx: 20, dy: 0 }));
  enter($('s4-render'), spring(lt - 7.39, 15, 0.75), { dy: 26, sc: 0.97 });
  const fr = Math.round(t * 30), tot = Math.round(DURATION * 30);
  $('s4-frame').textContent = `第 ${String(fr).padStart(4, '0')} / ${tot} 帧`;
  $('s4-rbar').style.width = `${(t / DURATION * 100).toFixed(2)}%`;
  $('s4-call').textContent = `window.render(${t.toFixed(2)}) · 1920×1080 · 30fps`;
  const sh = spring(lt - 9.3, 18, 0.55);
  $('s4-here').style.opacity = clamp(sh * 1.6, 0, 1);
  $('s4-here').style.transform = `translateY(${(1 - sh) * 16}px) scale(${0.9 + 0.1 * sh})`;
}

function renderScene5(t) {
  const lt = t - SCN[4].start;
  const pOut = smoothstep(2.85, 3.2, lt);
  const pains = $('s5-pains'); pains.style.display = pOut > 0.999 ? 'none' : '';
  pains.style.opacity = 1 - pOut; pains.style.transform = `translateY(${pOut * 30}px) scale(${1 - pOut * 0.03})`;
  enter($('s5-eb'), spring(lt, 16, 0.8), { dy: 16 });
  enter($('s5-pt'), spring(lt - 0.06, 14, 0.82), { dy: 30 });
  [0.15, 0.5, 1.45].forEach((at, i) => enter($(`pc-${i + 1}`), spring(lt - at, 15, 0.74), { dy: 46, sc: 0.96 }));
  const hero = $('s5-hero'); hero.style.display = lt >= 2.95 ? '' : 'none';
  const cmpAt = 5.55, cIn = spring(lt - cmpAt, 12, 0.86), fadeExtra = smoothstep(cmpAt, cmpAt + 0.25, lt);
  enter($('s5-heb'), spring(lt - 3.0, 16, 0.8), { dy: 16, k: 1 - fadeExtra });
  enter($('s5-checks'), spring(lt - 3.75, 16, 0.8), { dy: 16, k: 1 - fadeExtra });
  const core = $('s5-core'), sCore = spring(lt - 3.08, 12, 0.84);
  core.style.opacity = clamp(sCore * 1.6, 0, 1);
  core.style.transform = `translateY(${(1 - sCore) * 50 - cIn * 206}px) scale(${(0.94 + 0.06 * sCore) * (1 - cIn * 0.44)})`;
  const cmp = $('s5-cmp'); cmp.style.display = lt >= cmpAt ? '' : 'none';
  enter($('s5-old'), spring(lt - 5.75, 14, 0.78), { dx: -50, dy: 0, sc: 0.97, k: 1 - 0.35 * smoothstep(6.9, 7.4, lt) });
  const sk = spring(lt - 6.55, 20, 0.8); $('s5-strike').style.transform = `rotate(-8deg) scaleX(${sk})`; $('s5-strike').style.opacity = lt >= 6.55 ? 1 : 0;
  const ph = $('s5-ph'), sph = spring(lt - 5.95, 14, 0.78); ph.style.opacity = clamp(sph * 1.6, 0, 1) * (1 - smoothstep(8.4, 8.7, lt)); ph.style.transform = `scale(${0.96 + 0.04 * sph})`;
  enter($('s5-new'), spring(lt - 8.5, 13, 0.72), { dy: 30, sc: 0.94 });
  const pr = spring(lt - 9.2, 18, 0.5); $('s5-price').style.transform = `scale(${0.8 + 0.2 * pr})`; $('s5-price').style.transformOrigin = '0 70%';
  const rt = $('s5-route'); rt.style.display = lt >= 10.25 ? '' : 'none'; enter(rt, spring(lt - 10.3, 14, 0.8), { dy: 40, sc: 0.97 });
  [0, 0.5].forEach((o, i) => { const u = ((lt * 0.42 + o) % 1); const d = $(`s5-d${i + 1}`); d.style.left = `${u * 100}%`; d.style.opacity = Math.sin(u * Math.PI); });
}

// 第 6 镜节拍（相对本镜开始）
const B6 = { launch: 1.9, click: 2.55, app: 2.85, perm: 3.95, allow: 5.0, time: 5.72, sec: 7.78, hero: 10.48 };
function renderScene6(t) {
  const lt = t - SCN[5].start, scene = $('scene-6');
  const railOut = smoothstep(B6.hero - 0.2, B6.hero + 0.15, lt);
  const rail = $('s6-rail'); rail.style.display = railOut > 0.999 ? 'none' : '';
  enter(rail, spring(lt + 0.05, 14, 0.82), { dx: -40, dy: 0, k: 1 - railOut, pre: `translateX(${-railOut * 60}px)` });
  const act = lt < B6.launch ? 0 : lt < B6.perm ? 1 : lt < B6.time ? 2 : lt < B6.sec ? 3 : 4;
  const tAct = [0, B6.launch, B6.perm, B6.time, B6.sec][act];
  for (let i = 0; i < 5; i++) {
    const el = $(`ri-${i}`), on = i === act, s = on ? spring(lt - tAct, 18, 0.8) : 0;
    el.style.opacity = on ? 1 : 0.42;
    el.querySelector('.bg').style.opacity = on ? clamp(s * 1.5, 0, 1) : 0;
    el.querySelector('.bar').style.opacity = on ? clamp(s * 1.5, 0, 1) : 0;
    el.style.transform = `translateX(${on ? s * 8 : 0}px)`;
  }
  // (a) 地球
  const gs = panel($('p-globe'), lt, 0.12, B6.launch + 0.15, { dy: 30 });
  if ($('p-globe').style.display !== 'none') {
    const c = $('g-canvas'), ctx = c.getContext('2d'); ctx.setTransform(2, 0, 0, 2, 0, 0);
    const [ax, ay] = GLOBE.aim('sg'), e = easeOut((lt + 0.1) / 1.9);
    GLOBE.draw(ctx, 1012, 540, ax + 0.32 - 0.12 * e, ay - 1.15 * (1 - e) + 0.05 * lt, lt * 1000 + 600, 'sg', 1.7);
  }
  // (b) 启动器 → 一键连上
  panel($('p-launch'), lt, B6.launch, B6.app + 0.1, { dy: 30, sc: 0.95 });
  $('s6-cbtn').textContent = lt >= B6.click ? '连接中…' : '连接';
  const appOn = panel($('p-app'), lt, B6.app, B6.time + 0.12, { dy: 40, sc: 0.93 });
  const pill = $('s6-pill'), spl = spring(lt - B6.app - 0.25, 16, 0.7);
  pill.style.opacity = clamp(spl * 1.6, 0, 1); pill.style.transform = `translateX(-50%) translateY(${(1 - spl) * -24}px)`;
  [3.15, 3.4, 3.65].forEach((at, i) => enter($(`s6-t${i + 1}`), spring(lt - at, 18, 0.8), { dx: 16, dy: 0 }));
  const perm = $('s6-perm'), pIn = spring(lt - B6.perm, 16, 0.72), pOut = smoothstep(B6.allow + 0.12, B6.allow + 0.4, lt);
  perm.style.display = pOut > 0.999 ? 'none' : ''; perm.style.opacity = clamp(pIn * 1.6, 0, 1) * (1 - pOut);
  perm.style.transform = `translateY(${(1 - pIn) * 24}px) scale(${1 - pOut * 0.04})`;
  const allowEl = $('s6-allow'); allowEl.style.background = lt >= B6.allow ? '#059669' : ''; allowEl.style.borderColor = lt >= B6.allow ? '#059669' : '';
  enter($('s6-t4'), spring(lt - B6.allow - 0.3, 18, 0.8), { dx: 16, dy: 0 });
  enter($('s6-done'), spring(lt - B6.allow - 0.5, 16, 0.8), { dy: 12 });
  document.querySelectorAll('#s6-app .spin').forEach(sp => { sp.style.transform = `rotate(${lt * 360}deg)`; });
  // (c) 合上电脑照样跑
  panel($('p-time'), lt, B6.time, B6.sec + 0.12, { dy: 30 });
  const hp = easeInOut(clamp((lt - B6.time - 0.15) / 1.75, 0, 1)) * 100;
  $('tl-c1').style.clipPath = `inset(0 ${100 - hp}% 0 0)`; $('tl-c2').style.clipPath = `inset(0 ${100 - hp}% 0 0)`;
  $('tl-h1').style.left = `${hp}%`; $('tl-h2').style.left = `${hp}%`;
  [[50, 'tl-m1'], [73.3, 'tl-m2']].forEach(([p, id]) => { const el = $(id), tm = B6.time + 0.15 + 1.75 * (p / 100); const s = spring(lt - tm, 18, 0.6); el.style.opacity = clamp(s * 1.6, 0, 1); el.style.transform = `scale(${0.6 + 0.4 * s})`; });
  [B6.time + 0.3, B6.time + 0.45].forEach((at, i) => enter($(`use-${i + 1}`), spring(lt - at, 15, 0.78), { dy: 30 }));
  enter($('tl-phone'), spring(lt - B6.time - 0.35, 13, 0.8), { dy: 80 });
  enter($('tl-notif'), spring(lt - B6.time - 1.45, 16, 0.65), { dy: -40, sc: 0.9 });
  // (d) 代码和凭据留在你的服务器
  panel($('p-sec'), lt, B6.sec, B6.hero, { dy: 30 });
  [B6.sec + 0.4, B6.sec + 0.7, B6.sec + 1.0].forEach((at, i) => enter($(`vi-${i + 1}`), spring(lt - at, 16, 0.72), { dx: -60, dy: 0, sc: 0.96 }));
  [0, 1, 2, 3].forEach(i => enter($(`pl-${i + 1}`), spring(lt - B6.sec - 1.2 - i * 0.12, 15, 0.78), { dy: 30 }));
  [0, 0.5].forEach((o, i) => { const u = ((lt * 0.5 + o) % 1); const d = $(`sec-d${i + 1}`); d.style.left = `${u * 100}%`; d.style.opacity = Math.sin(u * Math.PI); });
  // (e) 主视觉：桌面端 + 手机
  const endAt = Math.max(0, VO_END - SCN[5].start + 0.15);
  const hero = $('s6-hero'), heroOut = smoothstep(endAt - 0.1, endAt + 0.35, lt);
  hero.style.display = lt >= B6.hero - 0.05 && heroOut < 0.999 ? '' : 'none';
  hero.style.opacity = 1 - heroOut;
  const sd = spring(lt - B6.hero, 9, 0.9), desk = $('s6-desk');
  const drift = smoothstep(B6.hero, endAt, lt);
  desk.style.opacity = clamp(sd * 1.6, 0, 1);
  desk.style.transform = `perspective(2000px) rotateX(${(1 - sd) * 16}deg) translateY(${(1 - sd) * 90}px) scale(${(0.9 + 0.1 * sd) * (1 - 0.03 * drift)})`;
  enter($('hero-phone'), spring(lt - B6.hero - 0.6, 13, 0.78), { dy: 120 });
  enter($('hero-notif'), spring(lt - B6.hero - 1.3, 16, 0.65), { dy: -30, sc: 0.9 });
  enter($('fb-1'), spring(lt - 11.0, 15, 0.65), { dx: -50, dy: 0, sc: 0.9 });
  enter($('fb-2'), spring(lt - 13.3, 15, 0.65), { dx: 50, dy: 0, sc: 0.9 });
  document.querySelectorAll('#hero-app .spin').forEach(sp => { sp.style.transform = `rotate(${lt * 360}deg)`; });
  // (f) CTA 定版
  const cta = $('s6-cta'); cta.style.display = lt >= endAt ? 'flex' : 'none';
  if (lt >= endAt) {   // 与主视觉交叉淡化；内容和底板几乎同时出现，避免出现空的深色底板
    const sc = spring(lt - endAt, 11, 0.9);
    cta.style.opacity = clamp(sc * 1.8, 0, 1); cta.style.transform = `scale(${0.97 + 0.03 * sc})`;
    [...cta.children].forEach((ch, i) => { if (i === 0) return; const s = spring(lt - endAt - 0.02 - (i - 1) * 0.06, 13, 0.85); ch.style.opacity = clamp(s * 1.8, 0, 1); ch.style.transform = `translateY(${(1 - s) * 22}px)`; });
  }
  // 光标：点「连接」→ 点「允许一次」
  const cur = $('cursor');
  let cp = null;
  if (lt >= B6.launch + 0.15 && lt < B6.app) {
    const r = rectIn($('s6-connect'), scene), m = easeInOut((lt - B6.launch - 0.15) / 0.45);
    cp = [1250 + (r.x + r.w * 0.5 - 1250) * m, 760 + (r.y + r.h * 0.6 - 760) * m, Math.abs(lt - B6.click) < 0.1 ? 0.84 : 1];
  } else if (lt >= B6.perm + 0.35 && lt < B6.allow + 0.6) {
    const r = rectIn($('s6-allow'), scene), m = easeInOut((lt - B6.perm - 0.35) / 0.6);
    cp = [1500 + (r.x + r.w * 0.5 - 1500) * m, 780 + (r.y + r.h * 0.6 - 780) * m, Math.abs(lt - B6.allow) < 0.1 ? 0.84 : 1];
  }
  cur.style.display = cp ? 'block' : 'none';
  if (cp) cur.style.transform = `translate(${cp[0] - 8}px, ${cp[1] - 6}px) scale(${cp[2]})`;
}

const RENDERERS = [renderScene1, renderScene2, renderScene3, renderScene4, renderScene5, renderScene6];
window.ready = false;
window.render = function (t) {
  t = clamp(t, 0, DURATION);
  $('tb-tc').textContent = `${fmtTime(t)} / ${fmtTime(DURATION)}`;
  // 每镜显示到「下一镜开始」，镜间静音留给上一镜收尾，避免回落到第 1 镜
  let idx = SCN.length - 1;
  for (let i = 0; i < SCN.length; i++) { const end = i === SCN.length - 1 ? DURATION + 1 : SCN[i + 1].start; if (t >= SCN[i].start - 1e-6 && t < end) { idx = i; break; } }
  $('tb-chap').textContent = CHAPTERS[idx];
  for (let i = 0; i < SCN.length; i++) $(`pf-${i}`).style.width = `${(clamp((t - SCN[i].start) / Math.max(.001, SCN[i].end - SCN[i].start), 0, 1) * 100).toFixed(1)}%`;
  let sub = ''; for (const s of SUBS) if (t >= s[0] && t <= s[1]) { sub = s[2]; break; }
  const pill = $('sub-pill'); pill.style.display = sub ? '' : 'none'; if (sub && pill.innerHTML !== sub) pill.innerHTML = sub;
  for (let i = 0; i < 6; i++) $(`scene-${i + 1}`).style.display = i === idx ? 'block' : 'none';
  RENDERERS[idx](t);
};

Promise.all([
  document.fonts.ready,
  $('img-indo').decode().catch(() => {}),
  $('img-moments').decode().catch(() => {}),
]).then(() => {
  window.render(0);
  window.ready = true;
  if (location.search.includes('play=1')) {
    const t0 = performance.now();
    const loop = (now) => { window.render(((now - t0) / 1000) % DURATION); requestAnimationFrame(loop); };
    requestAnimationFrame(loop);
  }
});
</script>
</body>
</html>
"""

# ---------------------------------------------------------------- 注入时间轴
TL_PATH = ROOT / "audio" / "vo_timeline.json"
tl = json.loads(TL_PATH.read_text(encoding="utf-8"))
total = float(tl["total"])


def highlight(txt: str) -> str:
    """字幕高亮：价格/数字标黄，CodeDeck 标绿。"""
    esc = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    esc = re.sub(r"(\$\s?\d[\d.,]*|¥[\d.,]+|\d+(?:\.\d+)?\s?(?:毫秒|公里|km|KM|个|块|元|美金|美元)|一千五百公里|八百层|三个|几十块钱?|两三千)",
                 r'<span class="sub-warn">\1</span>', esc)
    return esc.replace("CodeDeck", '<span class="sub-hl">CodeDeck</span>')


subs = [[round(a, 3), round(b, 3), highlight(c)] for a, b, c in tl["subs"]]
scenes = [{"id": x["id"], "start": round(x["start"], 3), "end": round(x["end"], 3)} for x in tl["scenes"]]
tl_js = json.dumps({"total": total, "vo_end": tl.get("vo_end", scenes[-1]["end"]), "scenes": scenes, "subs": subs},
                   ensure_ascii=False)
dur_label = "0%d:%s" % (int(total // 60), ("%.1f" % (total % 60)).zfill(4))

html = HTML_TEMPLATE
for key, val in {
    "__APP_S4__": APP_S4, "__APP_S6__": APP_S6, "__APP_HERO__": APP_HERO,
    "__PHONE_TL__": PHONE_TL, "__PHONE_HERO__": PHONE_HERO,
    "__LOGO__": LOGO, "__CLAUDE__": CLAUDE,
}.items():
    html = html.replace(key, val)
html = re.sub(r"__ICO_([a-z]+)__", lambda m: ico(m.group(1)), html)
html = (html.replace("__B64_INDO__", b64_indo)
            .replace("__B64_MOMENTS__", b64_moments)
            .replace("__GLOBE_B64__", globe_b64)
            .replace("__TIMELINE_JSON__", tl_js)
            .replace("__DURATION_LABEL__", dur_label))

leftover = re.findall(r"__[A-Z0-9_]+__", html)
assert not leftover, f"未替换的占位符：{sorted(set(leftover))}"
# 红线：不允许出现网址/域名
assert not re.search(r"https?://|www\.|codedeck\.top|[A-Za-z0-9-]\.(?:com|cn|net|io)\b", html), "页面里出现了网址或域名"

out_file = ROOT / "index.html"
out_file.write_text(html, encoding="utf-8")
print(f"Wrote {out_file} ({len(html) / 1024:.1f} KB) · {total}s · {len(scenes)} scenes · {len(subs)} subs")
