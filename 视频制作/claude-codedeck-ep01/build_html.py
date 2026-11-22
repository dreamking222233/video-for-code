#!/usr/bin/env python3
"""Assemble the self-contained offline index.html with embedded Base64 photos."""
import base64, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "source"

b64_indo = base64.b64encode((SRC / "asset_indo.jpg").read_bytes()).decode("ascii")
b64_moments = base64.b64encode((SRC / "asset_moments.jpg").read_bytes()).decode("ascii")

HTML_TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<title>如何在国内稳定使用 Claude · CodeDeck 第一期</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    width: 1920px; height: 1080px; overflow: hidden;
    background: #F5F1E8;
    color: #18181B;
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    -webkit-font-smoothing: antialiased;
    user-select: none;
  }
  #viewport {
    position: relative; width: 1920px; height: 1080px;
    background: #F5F1E8;
    overflow: hidden;
  }
  /* Paper dot matrix texture */
  #paper-grid {
    position: absolute; inset: 0; pointer-events: none; z-index: 1;
    background-image: radial-gradient(rgba(24, 24, 27, 0.085) 1.5px, transparent 1.5px);
    background-size: 28px 28px;
  }
  /* Top editorial bar */
  #topbar {
    position: absolute; top: 34px; left: 72px; right: 72px; height: 54px;
    z-index: 20;
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 2.5px solid #18181B;
    padding-bottom: 12px;
  }
  .tb-left {
    display: flex; align-items: center; gap: 16px;
    font-family: "SF Mono", "Menlo", monospace;
    font-size: 20px; font-weight: 800;
  }
  .tb-pill {
    background: #18181B; color: #F5F1E8;
    padding: 5px 14px; border-radius: 6px;
    letter-spacing: 0.04em;
  }
  .tb-chap {
    color: #D9462F; font-weight: 900;
  }
  .tb-center {
    display: flex; gap: 8px; align-items: center;
  }
  .prog-seg {
    width: 48px; height: 7px; border-radius: 99px;
    background: rgba(24,24,27,0.14);
    overflow: hidden;
  }
  .prog-fill {
    height: 100%; width: 0%;
    background: #10B981;
  }
  .tb-right {
    font-family: "SF Mono", "Menlo", monospace;
    font-size: 20px; font-weight: 700; color: #5C5850;
    display: flex; align-items: center; gap: 16px;
  }
  .tb-url {
    background: rgba(16, 185, 129, 0.15);
    color: #047857; border: 1.5px solid rgba(16,185,129,0.45);
    padding: 4px 12px; border-radius: 6px; font-weight: 800;
  }

  /* Scene container: leaves bottom 125px for subtitle bar */
  .scene {
    position: absolute; top: 104px; left: 72px; right: 72px; bottom: 118px;
    z-index: 10; display: none;
  }

  /* Common typography */
  .serif-h1 {
    font-family: "Songti SC", "STSong", "Noto Serif SC", serif;
    font-size: 64px; font-weight: 900; line-height: 1.14;
    color: #141413; letter-spacing: -0.02em;
  }
  .hl-red { color: #D9462F; }
  .hl-orange { color: #D97757; }
  .hl-green { color: #047857; }
  .kicker-tag {
    display: inline-flex; align-items: center; gap: 10px;
    font-family: "SF Mono", "Menlo", monospace;
    font-size: 21px; font-weight: 800;
    padding: 7px 18px; border-radius: 999px;
    margin-bottom: 14px;
  }

  /* ================= SCENE 1: HOOK & SCOOTER CRASH ================= */
  .s1-head {
    display: flex; justify-content: space-between; align-items: flex-end;
    margin-bottom: 26px;
  }
  .s1-arena {
    position: relative; width: 100%; height: 615px;
    background: #EBE4D5;
    border: 3px solid #18181B; border-radius: 28px;
    box-shadow: 10px 12px 0 #18181B;
    overflow: hidden;
  }
  .s1-wall-grid {
    position: absolute; inset: 34px 42px;
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px;
    align-items: center;
  }
  .fw-card {
    background: #FFFFFF;
    border: 3px solid #18181B;
    border-radius: 22px; padding: 30px 28px;
    height: 430px;
    box-shadow: 8px 10px 0 #D9462F;
    display: flex; flex-direction: column; justify-content: space-between;
    position: relative;
  }
  .fw-num {
    font-family: "SF Mono", monospace; font-size: 22px; font-weight: 900;
    color: #FFFFFF; background: #D9462F;
    padding: 6px 16px; border-radius: 8px; width: fit-content;
  }
  .fw-icon {
    font-size: 64px; margin: 10px 0;
  }
  .fw-title {
    font-size: 38px; font-weight: 900; color: #18181B; line-height: 1.2;
  }
  .fw-desc {
    font-size: 23px; font-weight: 600; color: #5C5850; line-height: 1.45;
  }
  .fw-stamp {
    font-family: "SF Mono", monospace; font-size: 20px; font-weight: 900;
    color: #D9462F; border-top: 2px dashed rgba(217,70,47,0.35);
    padding-top: 12px;
  }
  #s1-canvas {
    position: absolute; inset: 0; width: 1776px; height: 615px;
    pointer-events: none; z-index: 15;
  }
  .s1-crash-banner {
    position: absolute; left: 50%; top: 50%;
    background: #18181B; color: #FAF7F0;
    border: 4px solid #F59E0B;
    border-radius: 22px; padding: 22px 44px;
    font-size: 48px; font-weight: 900;
    box-shadow: 12px 14px 0 #D9462F;
    z-index: 25; white-space: nowrap;
  }
  .s1-alert {
    position: absolute; left: 50%; top: 46%;
    transform-origin: 50% 50%;
    background: #D9462F; color: #FFFFFF;
    border: 5px solid #18181B;
    border-radius: 24px; padding: 26px 52px;
    font-size: 62px; font-weight: 900; letter-spacing: 0.02em;
    box-shadow: 14px 16px 0 #18181B;
    z-index: 30; white-space: nowrap; text-align: center; line-height: 1.24;
  }
  .s1-alert small {
    display: block; font-size: 30px; font-weight: 800;
    color: #FFE5D9; letter-spacing: 0.06em; margin-top: 6px;
  }

  /* ================= SCENE 2: INDONESIA 1500KM & REAL PHOTO ================= */
  .s2-grid {
    display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 36px;
    height: 100%;
  }
  .s2-left {
    display: flex; flex-direction: column; justify-content: space-between;
  }
  .s2-map-card {
    position: relative; height: 420px;
    background: #EFE9DB; border: 3px solid #18181B;
    border-radius: 24px; overflow: hidden;
    box-shadow: 8px 10px 0 #18181B;
  }
  #s2-map-canvas {
    width: 100%; height: 100%;
  }
  .s2-auntie-card {
    background: #FFFFFF; border: 3px solid #18181B;
    border-radius: 22px; padding: 22px 28px;
    box-shadow: 8px 10px 0 #D97757;
    display: flex; align-items: center; justify-content: space-between;
    position: relative;
  }
  .aunt-avatar {
    width: 86px; height: 86px; border-radius: 20px;
    background: #FFE5D9; border: 2.5px solid #18181B;
    display: flex; align-items: center; justify-content: center;
    font-size: 48px; flex-shrink: 0;
  }
  .aunt-info {
    flex: 1; margin-left: 22px;
  }
  .aunt-title {
    font-size: 30px; font-weight: 900; color: #18181B;
  }
  .aunt-sub {
    font-size: 23px; font-weight: 700; color: #5C5850; margin-top: 4px;
  }
  .aunt-badges {
    display: flex; gap: 10px; margin-top: 10px;
  }
  .claude-acc-pill {
    background: #D97757; color: #FFFFFF;
    font-family: "SF Mono", monospace; font-size: 20px; font-weight: 800;
    padding: 5px 14px; border-radius: 8px;
  }
  .s2-right {
    position: relative; display: flex; align-items: center; justify-content: center;
  }
  .polaroid {
    background: #FFFFFF;
    border: 3px solid #18181B;
    border-radius: 22px;
    padding: 20px 20px 26px 20px;
    box-shadow: 14px 16px 0 #18181B;
    width: 760px; height: 830px;
    display: flex; flex-direction: column; justify-content: space-between;
    position: relative;
  }
  .pol-img-wrap {
    position: relative; width: 100%; height: 675px;
    border-radius: 14px; overflow: hidden;
    border: 2px solid #18181B; background: #18181B;
  }
  .pol-img-wrap img {
    width: 100%; height: 100%;
    object-fit: cover; object-position: center 46%;
  }
  .wb-highlight-box {
    position: absolute; left: 34%; top: 53%; width: 32%; height: 22%;
    border: 4px solid #EF4444; border-radius: 12px;
    box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.22);
    pointer-events: none;
  }
  .wb-zoom-callout {
    position: absolute; left: 16px; bottom: 12px; right: 16px;
    background: rgba(24, 24, 27, 0.93); color: #FAF7F0;
    border: 2px solid #F59E0B; border-radius: 14px;
    padding: 10px 18px;
    display: flex; justify-content: space-between; align-items: center;
  }
  .pol-caption {
    display: flex; justify-content: space-between; align-items: center;
    padding-top: 12px;
  }

  /* ================= SCENE 3: AGENT MOMENTS & COST RECEIPT ================= */
  .s3-grid {
    display: grid; grid-template-columns: 0.95fr 1.05fr; gap: 38px;
    height: 100%;
  }
  .phone-frame {
    background: #FFFFFF; border: 3px solid #18181B;
    border-radius: 26px; padding: 18px;
    box-shadow: 12px 14px 0 #18181B;
    display: flex; flex-direction: column; height: 840px;
    position: relative; overflow: hidden;
  }
  .pf-bar {
    display: flex; justify-content: space-between; align-items: center;
    padding: 8px 14px 14px 14px; border-bottom: 2px solid #E4E4DF;
    font-size: 22px; font-weight: 800;
  }
  .pf-viewport {
    position: relative; flex: 1; overflow: hidden;
    border-radius: 14px; background: #F8F8F6;
    border: 1.5px solid #E4E4DF;
  }
  .pf-viewport img {
    width: 100%; height: auto; display: block;
  }
  .pf-tag-overlay {
    position: absolute; left: 18px; bottom: 18px; right: 18px;
    background: rgba(24,24,27,0.92); color: #FFFFFF;
    padding: 14px 20px; border-radius: 14px;
    border: 2px solid #D97757;
    font-size: 23px; font-weight: 800;
    display: flex; justify-content: space-between; align-items: center;
  }
  .s3-right {
    display: flex; flex-direction: column; justify-content: space-between;
  }
  .receipt-card {
    background: #FFFFFF; border: 3px solid #18181B;
    border-radius: 26px; padding: 34px 38px;
    box-shadow: 12px 14px 0 #D9462F;
    flex: 1; display: flex; flex-direction: column; justify-content: space-between;
    position: relative;
  }
  .rc-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 20px 24px; border-radius: 16px;
    background: #FAF9F5; border: 2px dashed rgba(24,24,27,0.22);
    margin-bottom: 16px;
  }
  .rc-name { font-size: 28px; font-weight: 800; color: #18181B; }
  .rc-sub { font-size: 21px; font-weight: 600; color: #5C5850; margin-top: 4px; }
  .rc-price {
    font-family: "SF Mono", monospace; font-size: 34px; font-weight: 900;
    color: #D9462F; text-align: right;
  }
  .rc-total {
    border-top: 3px solid #18181B; padding-top: 22px;
    display: flex; justify-content: space-between; align-items: baseline;
  }
  .big-stamp {
    position: absolute; right: 28px; top: 18px;
    border: 5px solid #D9462F; color: #D9462F;
    background: rgba(255,255,255,0.96);
    padding: 8px 22px; border-radius: 12px;
    font-size: 32px; font-weight: 900; letter-spacing: 0.06em;
    z-index: 20;
    box-shadow: 0 8px 20px rgba(217,70,47,0.18);
  }

  /* ================= SCENE 4: WHY CLAUDE & META VIDEO REVEAL ================= */
  .s4-wrap {
    width: 100%; height: 100%;
    display: flex; flex-direction: column; justify-content: space-between;
    position: relative;
  }
  .s4-cards {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px;
    height: 350px;
  }
  .power-card {
    background: #FFFFFF; border: 3px solid #18181B;
    border-radius: 24px; padding: 28px 30px;
    box-shadow: 8px 10px 0 #18181B;
    display: flex; flex-direction: column; justify-content: space-between;
  }
  .power-card.featured {
    background: #18181B; color: #FAF7F0;
    border-color: #D97757;
    box-shadow: 10px 12px 0 #D97757;
  }
  .pc-badge {
    font-family: "SF Mono", monospace; font-size: 20px; font-weight: 800;
    padding: 6px 14px; border-radius: 8px; width: fit-content;
  }
  .pc-title { font-size: 36px; font-weight: 900; line-height: 1.2; }
  .pc-code {
    font-family: "SF Mono", monospace; font-size: 20px;
    padding: 12px 16px; border-radius: 12px;
    background: rgba(24,24,27,0.06); color: #047857; font-weight: 700;
  }
  .power-card.featured .pc-code {
    background: rgba(255,255,255,0.1); color: #FDBA74;
  }
  /* Meta studio reveal box */
  .meta-studio {
    height: 300px;
    background: #141619; color: #F4F4F0;
    border: 3px solid #18181B; border-radius: 24px;
    box-shadow: 12px 14px 0 #10B981;
    padding: 24px 32px;
    display: flex; flex-direction: column; justify-content: space-between;
    position: relative; overflow: hidden;
  }
  .ms-top {
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1.5px solid #2A2E37; padding-bottom: 14px;
  }
  .ms-rec {
    display: flex; align-items: center; gap: 12px;
    font-family: "SF Mono", monospace; font-size: 22px; font-weight: 800;
    color: #34D399;
  }
  .rec-dot {
    width: 14px; height: 14px; border-radius: 50%; background: #EF4444;
    box-shadow: 0 0 12px #EF4444;
  }
  .ms-body {
    display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 28px;
    align-items: center;
  }
  .ms-code {
    font-family: "SF Mono", monospace; font-size: 22px; line-height: 1.6;
    color: #D4D4D8;
  }
  .ms-callout {
    background: linear-gradient(135deg, rgba(16,185,129,0.22), rgba(217,119,87,0.22));
    border: 2px solid #34D399; border-radius: 18px;
    padding: 20px 24px;
    font-size: 28px; font-weight: 900; line-height: 1.38; color: #FFFFFF;
  }

  /* ================= SCENE 5: CODEDECK VS MAC MINI PRICE BOMBSHELL ================= */
  .s5-wrap {
    width: 100%; height: 100%;
    display: flex; flex-direction: column; justify-content: space-between;
  }
  .pain-strip {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 22px;
  }
  .pain-pill {
    background: #FEE2E2; border: 2.5px solid #DC2626;
    color: #991B1B; border-radius: 16px;
    padding: 14px 20px; font-size: 24px; font-weight: 800;
    display: flex; align-items: center; gap: 12px;
  }
  .vs-arena {
    display: grid; grid-template-columns: 0.82fr 1.18fr; gap: 34px;
    height: 550px; position: relative;
  }
  .vs-mystery {
    position: absolute; right: 0; bottom: 0; width: 58.2%; height: 100%;
    border: 3px dashed rgba(24,24,27,0.26); border-radius: 26px;
    background: rgba(255,255,255,0.42);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 10px; z-index: 1;
  }
  .vs-mystery b {
    font-family: "Songti SC", serif; font-size: 96px; font-weight: 900;
    color: rgba(24,24,27,0.22); line-height: 1;
  }
  .vs-mystery span {
    font-size: 25px; font-weight: 800; color: rgba(24,24,27,0.34);
    letter-spacing: 0.06em;
  }
  .vs-old {
    background: #EBE4D5; border: 3px dashed rgba(24,24,27,0.35);
    border-radius: 26px; padding: 34px 36px;
    display: flex; flex-direction: column; justify-content: space-between;
    position: relative;
  }
  .strike-line {
    position: absolute; left: 24px; right: 24px; top: 52%;
    height: 8px; background: #D9462F; border-radius: 99px;
    transform: rotate(-12deg);
  }
  .vs-new {
    background: #FFFFFF; border: 4px solid #18181B;
    border-radius: 28px; padding: 36px 42px;
    box-shadow: 14px 16px 0 #10B981;
    display: flex; flex-direction: column; justify-content: space-between;
    position: relative; z-index: 2;
  }
  .price-huge {
    font-family: "Songti SC", "PingFang SC", serif;
    font-size: 86px; font-weight: 900; color: #047857;
    line-height: 1.05; letter-spacing: -0.02em;
  }
  .benefit-tags {
    display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px;
  }
  .b-tag {
    background: #FAF9F5; border: 2px solid #18181B;
    border-radius: 14px; padding: 14px 18px;
    font-size: 24px; font-weight: 800; color: #18181B;
    display: flex; align-items: center; gap: 10px;
  }

  /* ================= SCENE 6: CODEDECK WORKBENCH & FINAL CTA ================= */
  .s6-wrap {
    width: 100%; height: 100%;
    position: relative;
  }
  .wb-window {
    width: 100%; height: 835px;
    background: #141619; color: #F4F4F0;
    border: 3px solid #18181B; border-radius: 26px;
    box-shadow: 12px 14px 0 #18181B;
    padding: 26px 34px;
    display: flex; flex-direction: column; justify-content: space-between;
  }
  .wb-top {
    display: flex; justify-content: space-between; align-items: center;
    padding-bottom: 18px; border-bottom: 1.5px solid #2A2E37;
  }
  .node-row {
    display: flex; gap: 12px; align-items: center;
  }
  .node-chip {
    font-family: "SF Mono", monospace; font-size: 20px; font-weight: 700;
    padding: 8px 16px; border-radius: 999px;
    background: #1E222A; color: #A1A1AA; border: 1px solid #2E3440;
  }
  .node-chip.active {
    background: rgba(16, 185, 129, 0.2); color: #34D399;
    border: 2px solid #10B981; font-weight: 900;
  }
  .wb-grid {
    display: grid; grid-template-columns: 1.08fr 0.92fr; gap: 28px;
    height: 490px;
  }
  .wb-panel {
    background: #0D0F12; border: 1.5px solid #2A2E37;
    border-radius: 20px; padding: 24px 28px;
    display: flex; flex-direction: column; justify-content: space-between;
    position: relative;
  }
  .approve-modal {
    background: #181C23; border: 2.5px solid #10B981;
    border-radius: 16px; padding: 20px 24px;
  }
  .am-btns {
    display: flex; gap: 14px; margin-top: 16px;
  }
  .am-btn {
    padding: 12px 24px; border-radius: 10px;
    font-size: 22px; font-weight: 900;
  }
  .am-allow {
    background: #10B981; color: #052E16; flex: 1; text-align: center;
  }
  .am-deny {
    background: #272B33; color: #A1A1AA;
  }
  .night-timeline {
    background: #181C23; border: 1.5px solid #2E3440;
    border-radius: 16px; padding: 20px 24px;
  }
  .nt-bar {
    height: 16px; background: #272B33; border-radius: 99px;
    overflow: hidden; margin: 14px 0;
  }
  .nt-fill {
    height: 100%; background: linear-gradient(90deg, #D97757, #10B981);
    border-radius: 99px;
  }

  /* Final Endcard Overlay inside Scene 6 */
  .final-card {
    position: absolute; inset: 0;
    background: #F5F1E8;
    border: 4px solid #18181B; border-radius: 28px;
    box-shadow: 16px 18px 0 #18181B;
    padding: 48px 64px;
    display: flex; flex-direction: column; justify-content: space-between;
    align-items: center; text-align: center;
    z-index: 30;
  }
  .fc-url-box {
    background: #18181B; color: #34D399;
    font-family: "SF Mono", "Menlo", monospace;
    font-size: 64px; font-weight: 900;
    padding: 22px 56px; border-radius: 24px;
    border: 4px solid #10B981;
    box-shadow: 10px 12px 0 #10B981;
    letter-spacing: 0.02em;
  }
  .fc-pillars {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 22px;
    width: 100%;
  }
  .fc-pil {
    background: #FFFFFF; border: 2.5px solid #18181B;
    border-radius: 18px; padding: 20px;
    font-size: 26px; font-weight: 900;
    box-shadow: 6px 8px 0 #18181B;
  }

  /* Vector cursor */
  #cursor {
    position: absolute; left: 0; top: 0; width: 42px; height: 42px;
    pointer-events: none; z-index: 50; display: none;
  }

  /* ================= BOTTOM SUBTITLE BAR ================= */
  #subbar {
    position: absolute; left: 80px; right: 80px; bottom: 22px; min-height: 74px;
    z-index: 40;
    display: flex; justify-content: center; align-items: center;
    pointer-events: none;
  }
  #sub-pill {
    background: rgba(20, 20, 19, 0.93);
    color: #FAF7F0;
    border: 2px solid rgba(255, 255, 255, 0.18);
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.25);
    padding: 11px 40px;
    border-radius: 30px;
    font-size: 30px; font-weight: 800;
    letter-spacing: 0.01em;
    max-width: 1640px;
    line-height: 1.34;
    text-align: center;
    white-space: normal;
  }
  #sub-pill .sub-hl {
    color: #34D399;
  }
  #sub-pill .sub-warn {
    color: #FDBA74;
  }
</style>
</head>
<body>
<div id="viewport">
  <div id="paper-grid"></div>

  <!-- Top Editorial Navigation Bar -->
  <div id="topbar">
    <div class="tb-left">
      <span class="tb-pill">CLAUDE 国内稳定指南 · EP01</span>
      <span class="tb-chap" id="tb-chap">// 01 · 物理破防</span>
    </div>
    <div class="tb-center">
      <div class="prog-seg"><div class="prog-fill" id="pf-0"></div></div>
      <div class="prog-seg"><div class="prog-fill" id="pf-1"></div></div>
      <div class="prog-seg"><div class="prog-fill" id="pf-2"></div></div>
      <div class="prog-seg"><div class="prog-fill" id="pf-3"></div></div>
      <div class="prog-seg"><div class="prog-fill" id="pf-4"></div></div>
      <div class="prog-seg"><div class="prog-fill" id="pf-5"></div></div>
    </div>
    <div class="tb-right">
      <span class="tb-url">CodeDeck · 海外直连</span>
      <span id="tb-tc">00:00.0 / __DURATION_LABEL__</span>
    </div>
  </div>

  <!-- ==================== SCENE 1 (0.0 - 13.0s) ==================== -->
  <div class="scene" id="scene-1">
    <div class="s1-head">
      <div>
        <div class="kicker-tag" style="background:rgba(217,70,47,0.14);color:#B93824;border:2px solid #D9462F;">
          🚨 离谱真事 · 当硅谷八百层风控遇上中国号商
        </div>
        <div class="serif-h1" style="font-size:60px;" id="s1-title">
          算尽了 <span class="hl-red">IP · 指纹 · 人脸核身</span><br>却没算到<span class="hl-orange">「物理下乡」</span>！
        </div>
      </div>
      <div style="font-family:'SF Mono',monospace;font-size:24px;font-weight:800;color:#5C5850;text-align:right;">
        DEFENSE LEVEL: PENTAGON<br><span style="color:#D9462F;">STATUS: 物理破防 🤣</span>
      </div>
    </div>

    <div class="s1-arena">
      <div class="s1-wall-grid">
        <div class="fw-card" id="fw-1">
          <div>
            <div class="fw-num">LAYER 01 · 封锁 IP</div>
            <div class="fw-icon">🧱</div>
            <div class="fw-title">机房 IP 段连坐封杀</div>
            <div class="fw-desc" style="margin-top:12px;">万人共享代理节点、跳出口 IP，秒触发账号风控拦截</div>
          </div>
          <div class="fw-stamp">STRICT IP BLOCKING</div>
        </div>

        <div class="fw-card" id="fw-2">
          <div>
            <div class="fw-num">LAYER 02 · 设备指纹</div>
            <div class="fw-icon">🔍</div>
            <div class="fw-title">浏览器与硬件特征核查</div>
            <div class="fw-desc" style="margin-top:12px;">时区、系统环境、支付卡属地交叉比对，严防虚拟环境</div>
          </div>
          <div class="fw-stamp">FINGERPRINT LOCK</div>
        </div>

        <div class="fw-card" id="fw-3">
          <div>
            <div class="fw-num">LAYER 03 · 实名 KYC</div>
            <div class="fw-icon">🪪</div>
            <div class="fw-title">当地手机号 + 真人验证</div>
            <div class="fw-desc" style="margin-top:12px;">要求海外本地真实身份与账单核验，号称铜墙铁壁</div>
          </div>
          <div class="fw-stamp">BIOMETRIC KYC</div>
        </div>
      </div>

      <canvas id="s1-canvas" width="3552" height="1230"></canvas>
      <div class="s1-alert" id="s1-alert">
        🚨 八百层风控警报
        <small>ACCOUNT BAN RATE · 99.9%</small>
      </div>
      <div class="s1-crash-banner" id="s1-banner">
        🛵 中国老哥骑摩托直接下乡收号 · 物理破防！
      </div>
    </div>
  </div>

  <!-- ==================== SCENE 2 (13.0 - 30.6s) ==================== -->
  <div class="scene" id="scene-2">
    <div class="s2-grid">
      <div class="s2-left">
        <div>
          <div class="kicker-tag" style="background:#FFE5D9;color:#B93824;border:2px solid #D97757;">
            🛵 摩旅 1500 公里 · 从巴厘岛杀进苏门答腊村里
          </div>
          <div class="serif-h1" style="font-size:56px;">
            进村当面打款过 KYC<br>村口大妈竟成<span class="hl-orange">“中国 AI 基石”</span>？
          </div>
        </div>

        <div class="s2-map-card">
          <canvas id="s2-map-canvas" width="1800" height="840"></canvas>
        </div>

        <div class="s2-auntie-card" id="s2-auntie">
          <div class="aunt-avatar">👵🏽</div>
          <div class="aunt-info">
            <div class="aunt-title">苏门答腊村口大妈 · 代码经验：0 行</div>
            <div class="aunt-sub">一辈子没摸过键盘，名下却挂着 3 个顶配号 😂</div>
            <div class="aunt-badges">
              <span class="claude-acc-pill">✓ Claude #01</span>
              <span class="claude-acc-pill">✓ Claude #02</span>
              <span class="claude-acc-pill">✓ Claude #03</span>
              <span style="background:#18181B;color:#F0C97A;font-weight:900;padding:5px 14px;border-radius:8px;font-size:20px;">
                🏆 莫名其妙成了中国科研基石
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="s2-right">
        <div class="polaroid" id="s2-polaroid">
          <div class="pol-img-wrap">
            <img id="img-indo" src="data:image/jpeg;base64,__B64_INDO__" alt="印尼老哥助力中国科研实拍" />
            <div class="wb-highlight-box" id="s2-hlbox"></div>
            <div class="wb-zoom-callout" id="s2-callout">
              <div>
                <div style="font-size:20px;color:#FDBA74;font-weight:800;">📋 现场白板原字放大：</div>
                <div style="font-size:28px;font-weight:900;color:#FFFFFF;margin-top:2px;">
                  “印尼老哥助力 中国科研·中国AI China No.1”
                </div>
              </div>
              <span style="background:#D9462F;color:#FFF;padding:8px 16px;border-radius:10px;font-weight:900;font-size:22px;">
                真实合影
              </span>
            </div>
          </div>
          <div class="pol-caption">
            <span style="font-size:25px;font-weight:900;color:#18181B;">📍 印尼苏门答腊 · 面对面打款过实名现场</span>
            <span style="font-family:'SF Mono',monospace;font-size:22px;font-weight:800;color:#D9462F;">1,500 KM TRIP</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ==================== SCENE 3 (30.6 - 48.6s) ==================== -->
  <div class="scene" id="scene-3">
    <div class="s3-grid">
      <div class="phone-frame" id="s3-phone">
        <div class="pf-bar">
          <div style="display:flex;gap:8px;align-items:center;">
            <span style="width:14px;height:14px;border-radius:50%;background:#EF4444;display:inline-block;"></span>
            <span style="width:14px;height:14px;border-radius:50%;background:#F59E0B;display:inline-block;"></span>
            <span style="width:14px;height:14px;border-radius:50%;background:#10B981;display:inline-block;"></span>
            <span style="margin-left:10px;">朋友圈 · 海外 Mac mini 物理机代部署实况</span>
          </div>
          <span style="color:#5C5850;font-family:'SF Mono',monospace;font-size:19px;">真实截图素材</span>
        </div>
        <div class="pf-viewport">
          <img id="img-moments" src="data:image/jpeg;base64,__B64_MOMENTS__" alt="代理朋友圈海外Macmini部署" />
          <div class="pf-tag-overlay">
            <span>📦 海外机房实体 Mac mini M4 阵列</span>
            <span style="color:#FDBA74;font-family:'SF Mono',monospace;">印尼区独立部署</span>
          </div>
        </div>
      </div>

      <div class="s3-right">
        <div>
          <div class="kicker-tag" style="background:rgba(217,70,47,0.14);color:#B93824;border:2px solid #D9462F;">
            💸 算一笔扎心账单 · 普通人在国内稳用 Claude 要花多少钱？
          </div>
          <div class="serif-h1" style="font-size:56px;margin-bottom:22px;">
            单租物理机 + 顶配订阅<br>每月硬掏 <span class="hl-red">两三千块</span> 谁顶得住？
          </div>
        </div>

        <div class="receipt-card" id="s3-receipt">
          <div class="big-stamp" id="s3-stamp">门槛劝退！</div>
          <div>
            <div style="font-family:'SF Mono',monospace;font-size:21px;font-weight:800;color:#5C5850;margin-bottom:18px;">
              OVERSEAS MAC MINI + CLAUDE SUBSCRIPTION BILL
            </div>

            <div class="rc-row" id="rc-1">
              <div>
                <div class="rc-name">01 · 单独租一台海外 Mac mini 实体机</div>
                <div class="rc-sub">海外机房托管物理机月租（不含账号订阅）</div>
              </div>
              <div class="rc-price">$159 /月<br><span style="font-size:24px;color:#18181B;">≈ ¥1,060 元</span></div>
            </div>

            <div class="rc-row" id="rc-2">
              <div>
                <div class="rc-name">02 · 代开 Claude Max 高阶套餐</div>
                <div class="rc-sub">高频写代码必备大额度档位</div>
              </div>
              <div class="rc-price">$360 /月<br><span style="font-size:24px;color:#5C5850;">≈ ¥2,500+ 元</span></div>
            </div>

            <div class="rc-row" id="rc-3">
              <div>
                <div class="rc-name">03 · 代开 Claude Ultra 顶配套餐</div>
                <div class="rc-sub">重度 Agent 全天候满血档位</div>
              </div>
              <div class="rc-price">$520 /月<br><span style="font-size:24px;color:#5C5850;">≈ ¥3,700+ 元</span></div>
            </div>
          </div>

          <div class="rc-total">
            <div>
              <div style="font-size:28px;font-weight:900;color:#18181B;">每月综合硬性开支</div>
              <div style="font-size:21px;font-weight:700;color:#D9462F;">对于绝大多数普通开发者是一笔巨款</div>
            </div>
            <div style="font-family:'SF Mono',monospace;font-size:58px;font-weight:900;color:#D9462F;" id="s3-total-num">
              ¥2,500–3,700+
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ==================== SCENE 4 (48.6 - 60.8s) ==================== -->
  <div class="scene" id="scene-4">
    <div class="s4-wrap">
      <div>
        <div class="kicker-tag" style="background:rgba(16,185,129,0.16);color:#047857;border:2px solid #10B981;">
          ⚡ 为什么大家非用 Claude 不可？ · 降维打击的全能生产力
        </div>
        <div class="serif-h1" style="font-size:56px;">
          不止能<span class="hl-green">通读项目写代码</span>，连<span class="hl-orange">你看的这条视频</span>都是它做的！
        </div>
      </div>

      <div class="s4-cards">
        <div class="power-card" id="pc-1">
          <div class="pc-badge" style="background:#EBE4D5;color:#18181B;">CAPABILITY 01</div>
          <div>
            <div class="pc-title">通读整个代码库<br>跨几十个文件重构</div>
            <div style="font-size:23px;color:#5C5850;font-weight:600;margin-top:10px;">
              不是一句句问答，而是真正理解工程架构的 AI 主力工程师
            </div>
          </div>
          <div class="pc-code">● Edit 42 files (+640 −180)</div>
        </div>

        <div class="power-card" id="pc-2">
          <div class="pc-badge" style="background:rgba(16,185,129,0.16);color:#047857;">CAPABILITY 02</div>
          <div>
            <div class="pc-title">自动跑测试修 Bug<br>一口气交付闭环</div>
            <div style="font-size:23px;color:#5C5850;font-weight:600;margin-top:10px;">
              自己写迁移、跑单测、过 Lint，报错自动排查直到全绿通过
            </div>
          </div>
          <div class="pc-code">✓ Bash npm test → 42 passed</div>
        </div>

        <div class="power-card featured" id="pc-3">
          <div class="pc-badge" style="background:#D97757;color:#FFFFFF;">CAPABILITY 03 · 破圈大招</div>
          <div>
            <div class="pc-title" style="color:#FFFFFF;">直接写代码做视频<br>自动合成配乐剪辑</div>
            <div style="font-size:23px;color:#D4D4D8;font-weight:600;margin-top:10px;">
              弹簧动画、手绘插画、节拍配乐、FFmpeg 渲染成片一条龙包办
            </div>
          </div>
          <div class="pc-code">★ window.render(t) → final.mp4</div>
        </div>
      </div>

      <div class="meta-studio" id="s4-meta">
        <div class="ms-top">
          <div class="ms-rec">
            <span class="rec-dot"></span>
            <span>META REVEAL · 正在由 Claude Code 实时渲染当前视频帧</span>
          </div>
          <div style="font-family:'SF Mono',monospace;font-size:20px;color:#F0C97A;" id="s4-frame-counter">
            RENDERING FRAME #1680 / 2805 · 1920x1080 @ 30fps
          </div>
        </div>
        <div class="ms-body">
          <div class="ms-code">
            <div><span style="color:#D97757;font-weight:800;">$ claude</span> "把第一期素材做成刊物风动画视频并合成配乐"</div>
            <div style="color:#34D399;">● Write  index.html (window.render 闭式弹簧 + 拍立得实拍图)</div>
            <div style="color:#34D399;">● Synth  audio/mix_norm.wav (120 BPM 电子配乐 + -14 LUFS)</div>
            <div style="color:#F0C97A;">● Mux    out/final.mp4 ➔ 100% 由 Claude 代码生成！</div>
          </div>
          <div class="ms-callout">
            🎬 不瞒你说：你现在看到的每一帧画面、排版和卡点音效，都是 <span style="color:#FDBA74;">Claude 写代码</span> 制作出来的！
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ==================== SCENE 5 (60.8 - 75.3s) ==================== -->
  <div class="scene" id="scene-5">
    <div class="s5-wrap">
      <div>
        <div class="kicker-tag" style="background:rgba(16,185,129,0.18);color:#047857;border:2px solid #10B981;">
          🚀 破局方案 · 我自己开发的平台 CodeDeck
        </div>
        <div class="serif-h1" style="font-size:56px;">
          不用花上千块租实体 Mac mini，每月<span class="hl-green">只需几十块</span>享同等稳定环境！
        </div>
      </div>

      <div class="pain-strip" id="s5-pains">
        <div class="pain-pill">✗ 本地挂代理：网络一抖 ECONNRESET 断连封号</div>
        <div class="pain-pill">✗ 笔记本跑长任务：一合盖休眠会话当场中断</div>
        <div class="pain-pill">✗ 本地直接跑命令：乱装依赖容易把主力机搞乱</div>
      </div>

      <div class="vs-arena">
        <div class="vs-mystery" id="s5-mystery">
          <b>?</b>
          <span>破局方案 · 正在揭晓</span>
        </div>

        <div class="vs-old" id="s5-old">
          <div class="strike-line" id="s5-strike"></div>
          <div>
            <div style="font-family:'SF Mono',monospace;font-size:21px;font-weight:800;color:#B93824;">
              × 传统方案：租海外实体 Mac mini
            </div>
            <div style="font-size:38px;font-weight:900;color:#18181B;margin-top:12px;">
              海外物理机单独月租
            </div>
            <div style="font-size:24px;color:#5C5850;font-weight:600;margin-top:10px;line-height:1.5;">
              • 光租机器就要 $159/月<br>
              • 还要自己折腾远程桌面与网络<br>
              • 排队预约，普通人成本太高
            </div>
          </div>
          <div style="font-family:'SF Mono',monospace;font-size:56px;font-weight:900;color:#B93824;">
            ¥1,060 <span style="font-size:28px;">/月 (仅机器)</span>
          </div>
        </div>

        <div class="vs-new" id="s5-new">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="background:#10B981;color:#052E16;font-size:22px;font-weight:900;padding:8px 20px;border-radius:999px;">
              ✓ CodeDeck · 专为 Claude Code 打造的远程工作台
            </span>
            <span style="font-family:'SF Mono',monospace;font-size:22px;font-weight:900;color:#047857;">
              独立海外服务器
            </span>
          </div>

          <div style="display:flex;justify-content:space-between;align-items:baseline;margin:10px 0;">
            <div>
              <div style="font-size:32px;font-weight:900;color:#18181B;">独立海外服务器直连 · 开机即用</div>
              <div style="font-size:23px;font-weight:700;color:#5C5850;margin-top:4px;">
                不用买实体机，享受一模一样稳定的专属海外服务器环境
              </div>
            </div>
            <div style="text-align:right;">
              <div style="font-size:22px;font-weight:800;color:#047857;">每月仅需</div>
              <div class="price-huge" id="s5-price">¥几十块<span style="font-size:32px;color:#18181B;">/月</span></div>
            </div>
          </div>

          <div class="benefit-tags">
            <div class="b-tag">🌍 独立公网 IP · 一人一台</div>
            <div class="b-tag">⚡ 机房原生网络 · 不靠本地代理</div>
            <div class="b-tag">💻 桌面端 / 浏览器 / 手机一键直连</div>
            <div class="b-tag">🛡️ 命令隔离运行 · 不碰本地电脑</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ==================== SCENE 6 (75.3 - 93.5s) ==================== -->
  <div class="scene" id="scene-6">
    <div class="s6-wrap">
      <div class="wb-window" id="s6-wb">
        <div class="wb-top">
          <div style="display:flex;align-items:center;gap:14px;">
            <span style="width:16px;height:16px;border-radius:50%;background:#10B981;display:inline-block;box-shadow:0 0 12px #10B981;"></span>
            <span style="font-size:28px;font-weight:900;color:#FFFFFF;">CodeDeck 远程工作台</span>
            <span style="font-family:'SF Mono',monospace;font-size:20px;color:#34D399;background:rgba(16,185,129,0.14);padding:5px 14px;border-radius:8px;">
              root@sg-01 · 已自动登录
            </span>
          </div>
          <div class="node-row">
            <span class="node-chip active">🇸🇬 新加坡 ~12ms</span>
            <span class="node-chip">🇲🇾 马来西亚 ~22ms</span>
            <span class="node-chip">🇰🇷 韩国 ~28ms</span>
            <span class="node-chip">🇯🇵 日本 ~35ms</span>
            <span class="node-chip">🇺🇸 美国 ~120ms</span>
          </div>
        </div>

        <div class="wb-grid">
          <div class="wb-panel">
            <div>
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                <span style="font-size:24px;font-weight:900;color:#F0C97A;">🔒 每一步操作由你亲自批准（隔离保护主力机）</span>
                <span style="font-family:'SF Mono',monospace;font-size:18px;color:#A1A1AA;">默认审批模式</span>
              </div>
              <div style="font-family:'SF Mono',monospace;font-size:21px;line-height:1.65;color:#D4D4D8;">
                <div><span style="color:#D97757;font-weight:800;">Claude Opus 4.7</span> 正在重构订单与支付模块…</div>
                <div style="color:#34D399;">● Read   db/schema.prisma (212 行)</div>
                <div style="color:#34D399;">● Write  db/migrations/0042_refund.sql (+12)</div>
                <div style="color:#34D399;">● Edit   src/orders/refund.ts (+18 −3)</div>
              </div>
            </div>

            <div class="approve-modal" id="s6-modal">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:22px;font-weight:900;color:#FBBF24;">! Claude 请求在服务器上运行 Bash 命令：</span>
                <span style="font-family:'SF Mono',monospace;font-size:19px;color:#34D399;">不碰你的本地电脑</span>
              </div>
              <div style="font-family:'SF Mono',monospace;font-size:24px;font-weight:800;color:#FFFFFF;margin-top:8px;">
                $ npm run db:migrate &amp;&amp; npm test
              </div>
              <div class="am-btns">
                <div class="am-btn am-deny">拒绝</div>
                <div class="am-btn am-allow" id="s6-allow-btn">允许并记住 ✓</div>
              </div>
            </div>
          </div>

          <div class="wb-panel">
            <div class="night-timeline">
              <div style="font-size:24px;font-weight:900;color:#34D399;">🌙 合上电脑照样跑 · systemd 7×24 全天候守护</div>
              <div style="display:flex;justify-content:space-between;font-family:'SF Mono',monospace;font-size:19px;color:#A1A1AA;margin-top:10px;">
                <span>23:30 笔记本合盖离线</span>
                <span>01:30 重构完成</span>
                <span style="color:#34D399;font-weight:800;">05:00 42项测试全过 ✓</span>
              </div>
              <div class="nt-bar"><div class="nt-fill" id="s6-nt-fill" style="width:100%;"></div></div>
              <div style="font-size:21px;color:#D4D4D8;font-weight:600;">
                第二天打开电脑，断线期间的终端与对话输出自动完整补齐！
              </div>
            </div>

            <div class="night-timeline" style="border-color:#F0C97A;">
              <div style="font-size:24px;font-weight:900;color:#F0C97A;">🛡️ 代码、会话与账号凭据 100% 留在你自己服务器</div>
              <div style="font-size:21px;color:#D4D4D8;font-weight:600;margin-top:10px;line-height:1.55;">
                • 单用户独占实例，不经过任何来路不明的第三方中转<br>
                • 桌面端钥匙串加密自动登录 · 浏览器门户一键免密直达<br>
                • 手机浏览器随时查看进度、随时点审批
              </div>
            </div>
          </div>
        </div>

        <div style="display:flex;justify-content:space-between;align-items:center;font-size:22px;color:#A1A1AA;padding-top:8px;">
          <span>一条命令自动装好 Node 22 与守护服务 · 内置对话 / 终端 / 文件 Diff / Git / 任务看板</span>
          <span style="color:#34D399;font-family:'SF Mono',monospace;font-weight:900;font-size:24px;">CodeDeck · 7×24h 在线</span>
        </div>
      </div>

      <!-- Final Endcard Overlay (86.1s - 93.5s) -->
      <div class="final-card" id="s6-final">
        <div class="kicker-tag" style="background:rgba(16,185,129,0.18);color:#047857;border:2.5px solid #10B981;font-size:24px;padding:10px 28px;">
          ✨ 告别骑摩托下乡收号 · 告别千元租海外物理机
        </div>

        <div class="serif-h1" style="font-size:74px;">
          每月几十块，给你的 Claude 安个<br><span class="hl-green">稳如泰山的海外专属工位</span>
        </div>

        <div class="fc-url-box" id="fc-url" style="font-family:'PingFang SC',sans-serif;font-size:54px;">
          CodeDeck · 海外服务器直连，开机即用
        </div>

        <div class="fc-pillars">
          <div class="fc-pil">🇸🇬 新加坡 12ms 直连<br><span style="font-size:20px;color:#5C5850;font-weight:700;">五大海外节点 · 独立公网 IP</span></div>
          <div class="fc-pil">🛡️ 远端隔离执行<br><span style="font-size:20px;color:#5C5850;font-weight:700;">每一步由你审批 · 不碰本机</span></div>
          <div class="fc-pil">🌙 合上电脑照常跑<br><span style="font-size:20px;color:#5C5850;font-weight:700;">7×24h 守护 · 断线自动续流</span></div>
          <div class="fc-pil">🔐 数据凭据自持<br><span style="font-size:20px;color:#5C5850;font-weight:700;">100% 留在你自己的服务器</span></div>
        </div>
      </div>

      <!-- Vector Cursor -->
      <svg id="cursor" viewBox="0 0 36 36">
        <path d="M6 4 L29 15 L18 19 L23 30 L18 32 L13 21 L6 27 Z" fill="#18181B" stroke="#FFFFFF" stroke-width="2.5" stroke-linejoin="round"/>
      </svg>
    </div>
  </div>

  <!-- Bottom Subtitle Pill -->
  <div id="subbar">
    <div id="sub-pill">家人们谁懂啊！</div>
  </div>
</div>

<script>
// Deterministic math utilities (zero Math.random)
function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
function smoothstep(a, b, x) {
  const u = clamp((x - a) / (b - a), 0, 1);
  return u * u * (3 - 2 * u);
}
function hash(n) {
  const x = Math.sin(n * 127.1 + 311.7) * 43758.5453123;
  return x - Math.floor(x);
}
function jitter(seed, amp) {
  return (hash(seed) - 0.5) * 2 * amp;
}
function spring(x, w = 15, z = 0.74) {
  if (x <= 0) return 0;
  const wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * x) * (Math.cos(wd * x) + (z * w / wd) * Math.sin(wd * x));
}

// Timeline injected at build time from audio/vo_timeline.json (tts.py marks driven)
const TL = __TIMELINE_JSON__;
const SCN = TL.scenes;
const SUBS = TL.subs;
const DURATION = TL.total;

const CHAPTER_TITLES = [
  '// 01 · 物理破防',
  '// 02 · 摩旅 1500KM 下乡收号',
  '// 03 · 海外物理机真实账单',
  '// 04 · 这条视频就是 Claude 做的',
  '// 05 · CodeDeck 每月仅需几十块',
  '// 06 · 12ms 直连 · 审批隔离 · 通宵跑'
];

function fmtTime(s) {
  const m = Math.floor(s / 60);
  const sec = (s % 60).toFixed(1).padStart(4, '0');
  return `0${m}:${sec}`;
}

function drawWobblyCircle(ctx, cx, cy, r, seed, amp = 2.2) {
  ctx.beginPath();
  const steps = 24;
  for (let i = 0; i <= steps; i++) {
    const a = (i / steps) * Math.PI * 2;
    const rr = r + jitter(seed + i * 5.3, amp);
    const x = cx + Math.cos(a) * rr;
    const y = cy + Math.sin(a) * rr;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.stroke();
}

function drawScooter(ctx, x, y, scale, boil) {
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(scale, scale);
  ctx.lineWidth = 5;
  ctx.strokeStyle = '#18181B';

  // Exhaust smoke puffs
  for (let k = 0; k < 3; k++) {
    ctx.fillStyle = 'rgba(24,24,27,0.14)';
    ctx.beginPath();
    ctx.arc(-78 - k * 28 + jitter(boil * 7 + k, 4), 14 - k * 6, 12 + k * 5, 0, Math.PI * 2);
    ctx.fill();
  }

  // Wheels
  ctx.fillStyle = '#18181B';
  drawWobblyCircle(ctx, -42, 26, 22, boil * 3 + 1, 1.8);
  drawWobblyCircle(ctx, 44, 26, 22, boil * 3 + 9, 1.8);

  // Scooter body
  ctx.fillStyle = '#F97316';
  ctx.beginPath();
  ctx.moveTo(-48, 20);
  ctx.lineTo(-18, -22);
  ctx.lineTo(28, -22);
  ctx.lineTo(48, 20);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();

  // Handlebar & headlight
  ctx.beginPath();
  ctx.moveTo(24, -22);
  ctx.lineTo(38, -54);
  ctx.lineTo(22, -56);
  ctx.stroke();

  // Rider helmet
  ctx.fillStyle = '#FACC15';
  ctx.beginPath();
  ctx.arc(0, -56 + jitter(boil * 11, 2), 22, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();

  // Flag on back
  ctx.strokeStyle = '#D9462F';
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(-36, -18);
  ctx.lineTo(-56, -78);
  ctx.stroke();
  ctx.fillStyle = '#D9462F';
  ctx.beginPath();
  ctx.roundRect(-170, -108, 118, 40, 8);
  ctx.fill();
  ctx.fillStyle = '#FFFFFF';
  ctx.font = '900 20px "PingFang SC", sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('下乡收号', -111, -81);

  ctx.restore();
}

function renderScene1(t) {
  const boil = Math.floor(t * 12);
  const s1 = spring(t - 0.1, 14, 0.78);
  document.getElementById('s1-title').style.transform = `translateY(${(1 - s1) * 28}px)`;
  document.getElementById('s1-title').style.opacity = clamp(s1 * 1.4, 0, 1);

  const crashT = t - 8.35; // Scooter crash moment
  const cardTimes = [0.45, 1.65, 2.85];
  const scatterCfg = [
    { dx: -95, dy: -65, rot: -16 },
    { dx: 15,  dy: -110, rot: 14 },
    { dx: 110, dy: 55,  rot: 19 }
  ];

  for (let i = 0; i < 3; i++) {
    const el = document.getElementById(`fw-${i + 1}`);
    const se = spring(t - cardTimes[i], 16, 0.72);
    const sc = spring(crashT - i * 0.12, 18, 0.55);
    const tx = sc * scatterCfg[i].dx;
    const ty = (1 - se) * 70 + sc * scatterCfg[i].dy;
    const rot = sc * scatterCfg[i].rot;
    el.style.opacity = clamp(se * 1.5, 0, 1);
    el.style.transform = `translate(${tx}px, ${ty}px) rotate(${rot}deg) scale(${1 - sc * 0.12})`;
  }

  // Draw scooter across canvas
  const c = document.getElementById('s1-canvas');
  const ctx = c.getContext('2d');
  ctx.save();
  ctx.scale(2, 2);
  ctx.clearRect(0, 0, 1776, 615);

  if (t >= 7.8) {
    const u = smoothstep(7.8, 9.6, t);
    const sx = -160 + u * 2080;
    const sy = 340 + Math.sin(t * 22) * 8;
    // Speed lines
    ctx.strokeStyle = 'rgba(217, 70, 47, 0.35)';
    ctx.lineWidth = 4;
    for (let l = 0; l < 6; l++) {
      const ly = 140 + l * 72;
      ctx.beginPath();
      ctx.moveTo(sx - 180 - l * 40, ly);
      ctx.lineTo(sx - 420 - l * 60, ly);
      ctx.stroke();
    }
    drawScooter(ctx, sx, sy, 1.55, boil);
  }
  ctx.restore();

  // Crash banner
  const banner = document.getElementById('s1-banner');
  const sb = spring(t - 8.65, 18, 0.52);
  banner.style.opacity = clamp(sb * 1.6, 0, 1);
  banner.style.transform = `translate(-50%, -50%) scale(${0.5 + 0.5 * sb}) rotate(${-3 * sb}deg)`;

  // Opening alert seal: slams in at t=0, flies out before the cards land
  const alertEl = document.getElementById('s1-alert');
  const sin = spring(t - 0.0, 20, 0.5);
  const sout = smoothstep(1.30, 1.72, t);
  alertEl.style.opacity = clamp(sin * 1.6 * (1 - sout), 0, 1);
  alertEl.style.transform =
    `translate(-50%, -50%) rotate(${-6 + (1 - sin) * 12}deg) scale(${(0.55 + 0.45 * sin) * (1 - sout * 0.55)})`;
  alertEl.style.display = sout > 0.99 ? 'none' : 'block';
}

function renderScene2(t) {
  const lt = t - SCN[1].start;
  const boil = Math.floor(t * 12);

  // Draw Indonesia 1500km route map
  const c = document.getElementById('s2-map-canvas');
  const ctx = c.getContext('2d');
  ctx.save();
  ctx.scale(2, 2); // 900 x 420 logical
  ctx.clearRect(0, 0, 900, 420);

  // Ocean waves
  ctx.strokeStyle = 'rgba(29, 53, 87, 0.18)';
  ctx.lineWidth = 2.5;
  for (let y = 55; y < 380; y += 75) {
    for (let x = 45; x < 840; x += 150) {
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x + 48, y + jitter(boil * 19 + x + y, 2.5));
      ctx.stroke();
    }
  }

  // Sumatra island (top-left)
  ctx.fillStyle = '#D8E2DC';
  ctx.strokeStyle = '#18181B';
  ctx.lineWidth = 3.5;
  ctx.beginPath();
  const sum = [[70, 95], [180, 65], [335, 145], [405, 225], [345, 268], [195, 200], [82, 145]];
  sum.forEach((p, i) => {
    const px = p[0] + jitter(boil * 13 + i, 2);
    const py = p[1] + jitter(boil * 17 + i, 2);
    if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
  });
  ctx.closePath(); ctx.fill(); ctx.stroke();

  // Java + Bali (bottom-right)
  ctx.beginPath();
  const java = [[430, 295], [655, 310], [720, 342], [650, 368], [420, 348]];
  java.forEach((p, i) => {
    if (i === 0) ctx.moveTo(p[0], p[1]); else ctx.lineTo(p[0], p[1]);
  });
  ctx.closePath(); ctx.fill(); ctx.stroke();

  // Bali circle
  ctx.fillStyle = '#FFE5D9';
  ctx.beginPath(); ctx.arc(778, 345, 28, 0, Math.PI * 2); ctx.fill(); ctx.stroke();

  // Animated route curve from Bali (778, 345) to Sumatra (235, 148)
  const prog = smoothstep(0.4, 5.2, lt);
  ctx.save();
  ctx.strokeStyle = '#D9462F';
  ctx.lineWidth = 6;
  ctx.setLineDash([14, 10]);
  ctx.beginPath();
  const steps = Math.floor(40 * prog);
  for (let i = 0; i <= steps; i++) {
    const u = i / 40;
    const qx = (1 - u) * (1 - u) * 778 + 2 * (1 - u) * u * 520 + u * u * 235;
    const qy = (1 - u) * (1 - u) * 345 + 2 * (1 - u) * u * 185 + u * u * 148;
    if (i === 0) ctx.moveTo(qx, qy); else ctx.lineTo(qx, qy);
  }
  ctx.stroke();
  ctx.restore();

  // Scooter position along curve
  const u = prog;
  const sx = (1 - u) * (1 - u) * 778 + 2 * (1 - u) * u * 520 + u * u * 235;
  const sy = (1 - u) * (1 - u) * 345 + 2 * (1 - u) * u * 185 + u * u * 148;
  drawScooter(ctx, sx, sy, 0.62, boil);

  // Labels
  ctx.fillStyle = '#18181B';
  ctx.font = '900 22px "PingFang SC", sans-serif';
  ctx.fillText('📍 出发：巴厘岛', 680, 398);
  ctx.fillText('🎯 终点：苏门答腊 (进村当面KYC)', 72, 46);

  // Distance badge
  ctx.fillStyle = '#D9462F';
  ctx.beginPath(); ctx.roundRect(475, 115, 235, 48, 12); ctx.fill();
  ctx.fillStyle = '#FFFFFF';
  ctx.font = '900 23px "SF Mono", "PingFang SC", sans-serif';
  ctx.fillText('🛵 摩旅 1500 KM', 495, 147);

  ctx.restore();

  // Right Polaroid photo entrance (at t=14.1s, lt=1.1s)
  const pol = document.getElementById('s2-polaroid');
  const sp = spring(lt - 1.1, 15, 0.72);
  pol.style.opacity = clamp(sp * 1.5, 0, 1);
  pol.style.transform = `translateY(${(1 - sp) * 60}px) rotate(${(1 - sp) * 8 - 1.5}deg) scale(${0.92 + 0.08 * sp})`;

  // Whiteboard highlight box & callout (at t=18.2s, lt=5.2s)
  const shl = spring(lt - 5.2, 16, 0.68);
  const hlbox = document.getElementById('s2-hlbox');
  const callout = document.getElementById('s2-callout');
  hlbox.style.opacity = clamp(shl * 1.5, 0, 1);
  hlbox.style.transform = `scale(${1.25 - 0.25 * shl})`;
  callout.style.opacity = clamp(shl * 1.5, 0, 1);
  callout.style.transform = `translateY(${(1 - shl) * 30}px)`;

  // Auntie card entrance (at t=23.3s, lt=10.3s)
  const sa = spring(lt - 10.3, 17, 0.62);
  const aunt = document.getElementById('s2-auntie');
  aunt.style.opacity = clamp(sa * 1.5, 0, 1);
  aunt.style.transform = `translateY(${(1 - sa) * 45}px) scale(${0.9 + 0.1 * sa})`;
}

function renderScene3(t) {
  const lt = t - SCN[2].start;
  const sp = spring(lt - 0.15, 15, 0.74);
  const phone = document.getElementById('s3-phone');
  phone.style.opacity = clamp(sp * 1.5, 0, 1);
  phone.style.transform = `translateX(${-(1 - sp) * 50}px)`;

  // Smooth vertical pan of the WeChat Moments screenshot so viewer sees both Mac mini rack & order cards
  const pan = smoothstep(1.2, 13.5, lt);
  const imgM = document.getElementById('img-moments');
  imgM.style.transform = `translateY(${-pan * 105}px)`;

  // Receipt rows
  const rTimes = [3.0, 10.5, 12.6];
  for (let i = 0; i < 3; i++) {
    const sr = spring(lt - rTimes[i], 16, 0.74);
    const row = document.getElementById(`rc-${i + 1}`);
    row.style.opacity = clamp(sr * 1.5, 0, 1);
    row.style.transform = `translateX(${(1 - sr) * 45}px)`;
  }

  // Stamp & total
  const sst = spring(lt - 15.0, 20, 0.5);
  const stamp = document.getElementById('s3-stamp');
  stamp.style.opacity = clamp(sst * 1.6, 0, 1);
  stamp.style.transform = `rotate(${-12 + (1 - sst) * 25}deg) scale(${1.6 - 0.6 * sst})`;
}

function renderScene4(t) {
  const lt = t - SCN[3].start;
  const cTimes = [0.4, 2.0, 3.6];
  for (let i = 0; i < 3; i++) {
    const sc = spring(lt - cTimes[i], 16, 0.72);
    const card = document.getElementById(`pc-${i + 1}`);
    card.style.opacity = clamp(sc * 1.5, 0, 1);
    card.style.transform = `translateY(${(1 - sc) * 45}px) scale(${0.94 + 0.06 * sc})`;
  }

  // Meta studio appears right after the cards so the lower half is never empty
  const sm = spring(lt - 3.15, 15, 0.72);
  const meta = document.getElementById('s4-meta');
  meta.style.opacity = clamp(sm * 1.5, 0, 1);
  meta.style.transform = `translateY(${(1 - sm) * 55}px) scale(${0.95 + 0.05 * sm})`;

  // 侧栏高亮在「你现在看到的这条视频」那句话落下时再强调一次
  const sc2 = spring(lt - 7.35, 20, 0.5);
  const calloutEl = document.querySelector('.ms-callout');
  if (calloutEl) {
    calloutEl.style.transform = `scale(${0.90 + 0.10 * sc2})`;
    calloutEl.style.transformOrigin = '50% 50%';
    calloutEl.style.boxShadow = `0 0 ${18 * sc2}px rgba(16,185,129,${0.45 * sc2})`;
  }

  const frameNo = Math.round(t * 30);
  document.getElementById('s4-frame-counter').textContent =
    `RENDERING FRAME #${frameNo} / ${Math.round(DURATION * 30)} · window.render(${t.toFixed(2)}s)`;
}

function renderScene5(t) {
  const lt = t - SCN[4].start;
  const sp = spring(lt - 0.15, 16, 0.75);
  const pains = document.getElementById('s5-pains');
  pains.style.opacity = clamp(sp * 1.5, 0, 1);
  pains.style.transform = `translateY(${(1 - sp) * 30}px)`;

  // Mystery placeholder sits in the right column so the stage is never empty
  const sm = spring(lt - 0.55, 16, 0.74);
  const mystery = document.getElementById('s5-mystery');
  const reveal = smoothstep(3.95, 4.75, lt);
  mystery.style.opacity = clamp(sm * 1.5 * (1 - reveal), 0, 1);
  mystery.style.transform = `scale(${0.94 + 0.06 * sm})`;

  // Old Mac mini card lands early so the stage is never empty
  const so = spring(lt - 1.15, 15, 0.74);
  const oldC = document.getElementById('s5-old');
  oldC.style.opacity = clamp(so * 1.5, 0, 1);
  oldC.style.transform = `translateX(${-(1 - so) * 40}px)`;

  // Strike line crosses the old price when narration says "完全不需要花上千块"
  const sk = spring(lt - 6.35, 18, 0.65);
  const strike = document.getElementById('s5-strike');
  strike.style.opacity = clamp(sk * 1.5, 0, 1);
  strike.style.transform = `rotate(-12deg) scaleX(${sk})`;

  // New CodeDeck card reveals at "所以我自己开发了 CodeDeck 平台"
  const sn = spring(lt - 4.05, 15, 0.70);
  const newC = document.getElementById('s5-new');
  newC.style.opacity = clamp(sn * 1.5, 0, 1);
  newC.style.transform = `translateY(${(1 - sn) * 50}px) scale(${0.94 + 0.06 * sn})`;

  // Price punch when narration says "每月只需要花几十块钱"
  const spr = spring(lt - 6.65, 19, 0.55);
  const priceEl = document.getElementById('s5-price');
  priceEl.style.transform = `scale(${0.82 + 0.18 * spr})`;
  priceEl.style.transformOrigin = '100% 60%';
  priceEl.style.opacity = clamp(0.35 + spr, 0, 1);
}

function renderScene6(t) {
  const lt = t - SCN[5].start;
  const sw = spring(lt - 0.15, 15, 0.75);
  const wb = document.getElementById('s6-wb');
  wb.style.opacity = clamp(sw * 1.5, 0, 1);
  wb.style.transform = `translateY(${(1 - sw) * 35}px)`;

  // Cursor moves to click "允许并记住 ✓" at t=81.4s (lt=6.1s)
  const cur = document.getElementById('cursor');
  const btn = document.getElementById('s6-allow-btn');
  if (lt >= 4.5 && lt < 10.6) {
    cur.style.display = 'block';
    const m = smoothstep(4.5, 5.9, lt);
    const cx = 1010 - m * 470;
    const cy = 300 + m * 300;
    const clickPulse = (lt >= 5.95 && lt <= 6.35) ? 0.82 : 1.0;
    cur.style.transform = `translate(${cx}px, ${cy}px) scale(${clickPulse})`;
  } else {
    cur.style.display = 'none';
  }

  if (lt >= 6.05) {
    btn.textContent = '✓ 已批准执行 · 42 passed';
    btn.style.background = '#34D399';
  } else {
    btn.textContent = '允许并记住 ✓';
    btn.style.background = '#10B981';
  }

  // Night timeline progress bar
  const ntProg = clamp(smoothstep(6.2, 10.2, lt), 0.25, 1.0);
  document.getElementById('s6-nt-fill').style.width = `${(ntProg * 100).toFixed(1)}%`;

  // Final Endcard Overlay (at t=86.2s, lt=10.9s)
  const finalCard = document.getElementById('s6-final');
  const endAt = Math.max(0, (TL.vo_end ?? SCN[5].end) - SCN[5].start + 0.15);  // 最后一句读完即定版
  const fadeOut = clamp(smoothstep(endAt - 0.30, endAt + 0.05, lt), 0, 1);
  wb.style.opacity = clamp(sw * 1.5, 0, 1) * (1 - fadeOut);
  if (lt >= endAt) {
    finalCard.style.display = 'flex';
    const sf = spring(lt - endAt, 11, 0.86);
    finalCard.style.opacity = clamp(sf * 1.5, 0, 1);
    finalCard.style.transform = `scale(${0.92 + 0.08 * sf})`;
  } else {
    finalCard.style.display = 'none';
  }
}

window.ready = false;
window.render = function(t) {
  t = clamp(t, 0, DURATION);

  // Update topbar timecode & chapter & progress segments
  document.getElementById('tb-tc').textContent =
    `${fmtTime(t)} / ${fmtTime(DURATION)}`;

  // 每镜显示到「下一镜开始」为止，把镜间 0.35s 静音留作上一镜的收尾定格，
  // 否则落在间隙里会没有任何镜头命中而回落到第 1 镜。
  let activeIdx = SCN.length - 1;
  for (let i = 0; i < SCN.length; i++) {
    const winEnd = (i === SCN.length - 1) ? DURATION + 1 : SCN[i + 1].start;
    if (t >= SCN[i].start - 1e-6 && t < winEnd) { activeIdx = i; break; }
  }
  document.getElementById('tb-chap').textContent = CHAPTER_TITLES[activeIdx];
  for (let i = 0; i < SCN.length; i++) {
    const p = clamp((t - SCN[i].start) / Math.max(0.001, SCN[i].end - SCN[i].start), 0, 1);
    document.getElementById(`pf-${i}`).style.width = `${(p * 100).toFixed(1)}%`;
  }

  // Update bottom subtitle pill
  const subPill = document.getElementById('sub-pill');
  let activeSub = '';
  for (let i = 0; i < SUBS.length; i++) {
    if (t >= SUBS[i][0] && t <= SUBS[i][1]) {
      activeSub = SUBS[i][2];
      break;
    }
  }
  if (activeSub) {
    subPill.style.display = 'block';
    subPill.innerHTML = activeSub;
  } else {
    subPill.style.display = 'none';
  }

  // Toggle active scene strictly (no overlap)
  const scenes = ['scene-1', 'scene-2', 'scene-3', 'scene-4', 'scene-5', 'scene-6'];
  scenes.forEach((id, idx) => {
    document.getElementById(id).style.display = (idx === activeIdx) ? 'block' : 'none';
  });

  if (activeIdx === 0) renderScene1(t);
  else if (activeIdx === 1) renderScene2(t);
  else if (activeIdx === 2) renderScene3(t);
  else if (activeIdx === 3) renderScene4(t);
  else if (activeIdx === 4) renderScene5(t);
  else if (activeIdx === 5) renderScene6(t);
};

// Wait for fonts + embedded Base64 images before flipping window.ready = true
Promise.all([
  document.fonts.ready,
  document.getElementById('img-indo').decode().catch(() => {}),
  document.getElementById('img-moments').decode().catch(() => {})
]).then(() => {
  window.render(0);
  window.ready = true;
  if (location.search.includes('play=1')) {
    const t0 = performance.now();
    function loop(now) {
      const t = ((now - t0) / 1000) % DURATION;
      window.render(t);
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  }
});
</script>
</body>
</html>
"""

# ---------- inject timeline from audio/vo_timeline.json ----------
import json, re

TL_PATH = ROOT / "audio" / "vo_timeline.json"
tl = json.loads(TL_PATH.read_text(encoding="utf-8"))
total = float(tl["total"])

# 字幕高亮：数字/价格标黄，CodeDeck 标绿，其余保持
HL_WORDS = ["CodeDeck", "Claude", "百万级"]

def highlight(txt: str) -> str:
    esc = (txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    esc = re.sub(r"(\$\s?\d[\d.,]*|¥[\d.,]+|\d+(?:\.\d+)?\s?(?:毫秒|公里|km|KM|个|块|元|美金|美元|美金))",
                 r'<span class="sub-warn">\1</span>', esc)
    for w in ("CodeDeck",):
        esc = esc.replace(w, f'<span class="sub-hl">{w}</span>')
    return esc

subs = [[round(a, 3), round(b, 3), highlight(c)] for a, b, c in tl["subs"]]
scenes = [{"id": x["id"], "start": round(x["start"], 3), "end": round(x["end"], 3)} for x in tl["scenes"]]

tl_js = json.dumps({"total": total, "scenes": scenes, "subs": subs}, ensure_ascii=False)
dur_label = "0%d:%s" % (int(total // 60), ("%.1f" % (total % 60)).zfill(4))

html_out = (HTML_TEMPLATE
            .replace("__B64_INDO__", b64_indo)
            .replace("__B64_MOMENTS__", b64_moments)
            .replace("__TIMELINE_JSON__", tl_js)
            .replace("__DURATION_LABEL__", dur_label))

out_file = ROOT / "index.html"
out_file.write_text(html_out, encoding="utf-8")
print(f"Wrote {out_file} ({len(html_out) / 1024:.1f} KB) · {total}s · {len(scenes)} scenes · {len(subs)} subs")
