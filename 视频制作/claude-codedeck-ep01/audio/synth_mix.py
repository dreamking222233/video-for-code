#!/usr/bin/env python3
"""Time-aligned soundtrack: tts.py VO (cosy_plus clone) + 120 BPM synth bed (ducked) + synced SFX.

Reads audio/vo_timeline.json so every cue follows the marks produced by 音频训练/tts.py.
Outputs audio/mix.wav (mono 48k).
"""
import json
import pathlib
import sys
import wave

import numpy as np
from scipy.signal import butter, lfilter

SR = 48000
HERE = pathlib.Path(__file__).resolve().parent

TL = json.loads((HERE / "vo_timeline.json").read_text(encoding="utf-8"))
SCN = TL["scenes"]
DUR = float(TL["total"])
N = int(SR * DUR)


def s(i, off=0.0):
    """scene i 的绝对时间 + 偏移"""
    return SCN[i]["start"] + off


def read_wav_mono(path):
    with wave.open(str(path), "rb") as w:
        raw = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
        if w.getnchannels() > 1:
            raw = raw.reshape(-1, w.getnchannels()).mean(axis=1)
        assert w.getframerate() == SR, w.getframerate()
        return raw


def env(n, attack=0.004, decay=0.18):
    x = np.arange(n) / SR
    return np.minimum(1.0, x / max(attack, 1e-4)) * np.exp(-x / decay)


def lp(sig, cutoff):
    b, a = butter(2, cutoff / (SR * 0.5), btype="low")
    return lfilter(b, a, sig)


def hp(sig, cutoff):
    b, a = butter(2, cutoff / (SR * 0.5), btype="high")
    return lfilter(b, a, sig)


def add_at(buf, sig, t_sec, gain=1.0):
    i = int(round(t_sec * SR))
    if i >= len(buf) or i < 0:
        return
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += sig[:n] * gain


def soft_kick(length=0.26):
    n = int(length * SR)
    f = np.geomspace(132.0, 46.0, n)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.085)


def hat(length=0.05, seed=7):
    """窄带金属 tick：几个高频正弦叠加，不用白噪声，避免宽带嘶声。"""
    n = int(length * SR)
    t = np.arange(n) / SR
    sig = (0.60 * np.sin(2 * np.pi * 7420 * t)
           + 0.30 * np.sin(2 * np.pi * 9860 * t)
           + 0.18 * np.sin(2 * np.pi * 11330 * t))
    return sig * env(n, 0.0008, 0.010)


def warm_chord(freqs, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for f in freqs:
        sig += 0.50 * np.sin(2 * np.pi * f * t)
        sig += 0.24 * np.sin(2 * np.pi * (f * 1.003) * t + 0.4)
        sig += 0.24 * np.sin(2 * np.pi * (f * 0.997) * t + 1.1)
        sig += 0.12 * np.sin(2 * np.pi * (f * 2.0) * t)
    sig /= max(1, len(freqs))
    fade_in = np.minimum(1.0, t / 0.08)
    fade_out = np.minimum(1.0, np.maximum(0.0, (dur - t) / 0.18))
    return sig * fade_in * fade_out * np.exp(-t / 2.8)


def warm_bass(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = 0.75 * np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * (freq * 2.0) * t)
    fade_in = np.minimum(1.0, t / 0.03)
    fade_out = np.minimum(1.0, np.maximum(0.0, (dur - t) / 0.10))
    return sig * fade_in * fade_out


def sfx_impact():
    n = int(0.55 * SR)
    f = np.geomspace(165.0, 38.0, n)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.16)
    crunch = lp(np.random.default_rng(3).standard_normal(n), 1100) * env(n, 0.001, 0.06)
    return boom * 0.8 + crunch * 0.5


def sfx_vroom():
    n = int(0.85 * SR)
    t = np.arange(n) / SR
    f = 95 + 135 * np.sin(np.pi * np.minimum(1.0, t / 0.7))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (0.55 * np.sin(ph) + 0.30 * np.sin(2 * ph) + 0.20 * np.sin(3 * ph)) * np.hanning(n)


def sfx_shutter():
    rng = np.random.default_rng(19)
    n1, n2 = int(0.028 * SR), int(0.038 * SR)
    c1 = hp(rng.standard_normal(n1), 2200) * env(n1, 0.0005, 0.007)
    c2 = hp(rng.standard_normal(n2), 1800) * env(n2, 0.0005, 0.010)
    return np.concatenate([c1, np.zeros(int(0.035 * SR)), c2])


def sfx_pop(f0=880):
    n1, n2 = int(0.045 * SR), int(0.24 * SR)
    x1, x2 = np.arange(n1) / SR, np.arange(n2) / SR
    p1 = np.sin(2 * np.pi * f0 * x1) * env(n1, 0.002, 0.022)
    p2 = 0.5 * (np.sin(2 * np.pi * f0 * 1.33 * x2) + np.sin(2 * np.pi * f0 * 2 * x2)) * env(n2, 0.002, 0.08)
    return np.concatenate([p1, p2])


def sfx_tick(freq=2800):
    n = int(0.035 * SR)
    return np.sin(2 * np.pi * freq * np.arange(n) / SR) * env(n, 0.001, 0.007)


def sfx_whoosh():
    n = int(0.38 * SR)
    rng = np.random.default_rng(12)
    return lp(rng.standard_normal(n), 1500) * np.hanning(n) * 1.2


def sfx_success():
    n1, n2 = int(0.08 * SR), int(0.55 * SR)
    x1, x2 = np.arange(n1) / SR, np.arange(n2) / SR
    p1 = np.sin(2 * np.pi * 1046.5 * x1) * env(n1, 0.002, 0.05)
    p2 = (0.4 * np.sin(2 * np.pi * 1318.5 * x2)
          + 0.4 * np.sin(2 * np.pi * 1568.0 * x2)
          + 0.3 * np.sin(2 * np.pi * 2093.0 * x2)) * env(n2, 0.003, 0.18)
    return np.concatenate([p1, p2])


def compress_voice(x, sr, thr_db=-20.0, ratio=2.4, attack=0.008, release=0.14, makeup_db=0.0):
    """只压人声：`threshold+ratio` 提语声 RMS、降 crest，这样后面母带需要的增益更小，
    句间配乐底噪就不会被整体抬起来。"""
    env = np.abs(x)
    a_att = np.exp(-1.0 / (attack * sr))
    a_rel = np.exp(-1.0 / (release * sr))
    # 单极点双时间常数包络
    out = np.empty_like(env)
    prev = 0.0
    for i, v in enumerate(env):
        coef = a_att if v > prev else a_rel
        prev = coef * prev + (1 - coef) * v
        out[i] = prev
    db = 20 * np.log10(out + 1e-9)
    over = db - thr_db
    gr = np.where(over > 0, -over * (1 - 1 / ratio), 0.0)
    gr = np.maximum(gr, -24.0)
    return x * (10 ** ((gr + makeup_db) / 20))


def main():
    # 优先用降噪版：tts.py 的输出在 4-13k 有约 -65dBFS 的稳态嘶声，
    # 母带 +12dB 后会明显 audible，所以先用 anlmdn 压掉（不改变时长）。
    vo_src = HERE / "vo_clean.wav"
    if not vo_src.exists():
        vo_src = HERE / "vo_clone.wav"
    vo = np.zeros(N, dtype=np.float64)
    raw = read_wav_mono(vo_src)
    n = min(len(raw), N)
    vo[:n] = raw[:n]   # vo_clean.wav 已做过 highpass+anlmdn

    # ---- 120 BPM warm electronic bed ----
    bgm = np.zeros(N, dtype=np.float64)
    prog = [
        (87.31, [174.61, 220.00, 261.63, 329.63]),  # Fmaj7
        (82.41, [164.81, 196.00, 246.94, 293.66]),  # Em7
        (73.42, [146.83, 174.61, 220.00, 261.63]),  # Dm7
        (65.41, [196.00, 246.94, 261.63, 329.63]),  # Cmaj7
    ]
    arp = [329.63, 392.00, 440.00, 523.25, 392.00, 493.88, 587.33, 523.25]
    kick = soft_kick()
    coda = float(SCN[-1]["start"])          # CodeDeck 登场后加亮
    bars = int(DUR // 2.0) + 1
    for bar in range(bars):
        t0 = bar * 2.0
        if t0 >= DUR:
            break
        bf, ch = prog[bar % 4]
        bright = 1.22 if t0 >= coda else 1.0
        add_at(bgm, warm_chord(ch, 2.0), t0, gain=0.26 * bright)
        add_at(bgm, warm_bass(bf, 1.95), t0, gain=0.18)
        for sub in range(4):
            tb = t0 + sub * 0.5
            if tb >= DUR - 0.4:
                break
            add_at(bgm, kick, tb, gain=0.36 if sub % 2 == 0 else 0.22)
            # Hi-hat 全部去掉：它唯一的声源是噪声，是「沙沙声」的主要来源。
            # 节奏感交给 kick + 琶音，密度已经够。
            fn = arp[(bar * 4 + sub) % len(arp)]
            nn = int(0.42 * SR)
            tn = np.arange(nn) / SR
            plk = (0.65 * np.sin(2 * np.pi * fn * tn) + 0.25 * np.sin(2 * np.pi * fn * 2 * tn)) * env(nn, 0.004, 0.14)
            add_at(bgm, plk, tb, gain=0.11 * bright)

    # 配乐只在低频/中频，9kHz 以上让给人声，避免齿音区叠出沙沙感
    bgm = lp(bgm, 7500.0)

    # ---- 人声闪避 ----
    win = int(0.12 * SR)
    vo_env = np.convolve(np.abs(vo), np.ones(win) / win, mode="same")
    duck = np.clip(1.0 - 4.5 * vo_env, 0.06, 0.55)
    end_idx = int(max(0, DUR - 1.6) * SR)
    duck[end_idx:] = np.linspace(duck[end_idx], 0.72, N - end_idx)
    bgm *= duck

    # ---- 动作音效：全部锚在 marks 上 ----
    sfx = np.zeros(N, dtype=np.float64)
    add_at(sfx, sfx_impact(), s(0, 0.05), gain=0.34)          # 开场重击
    for dt in (0.45, 1.65, 2.85):                              # 三张风控卡落地
        add_at(sfx, sfx_tick(2200), s(0, dt), gain=0.28)
    add_at(sfx, sfx_whoosh(), s(0, 7.6), gain=0.24)            # 摩托冲入
    add_at(sfx, sfx_vroom(), s(0, 7.9), gain=0.42)
    add_at(sfx, sfx_impact(), s(0, 8.55), gain=0.46)           # 破防瞬间

    add_at(sfx, sfx_whoosh(), s(1, 0.15), gain=0.24)           # 转场：路线图
    add_at(sfx, sfx_shutter(), s(1, 1.30), gain=0.52)          # 拍立得照片甩入
    add_at(sfx, sfx_pop(920), s(1, 10.2), gain=0.36)           # 大妈档案卡
    add_at(sfx, sfx_impact(), s(1, 13.0), gain=0.32)           # 盖章

    add_at(sfx, sfx_whoosh(), s(2, 0.15), gain=0.24)           # 转场：账单
    for i, dt in enumerate((5.6, 10.6, 12.4)):                 # 三项账单累加
        add_at(sfx, sfx_tick(2600 + i * 320), s(2, dt), gain=0.30)
    add_at(sfx, sfx_impact(), s(2, 14.6), gain=0.42)           # 总额盖章

    add_at(sfx, sfx_whoosh(), s(3, 0.15), gain=0.24)           # 转场：为什么是 Claude
    for i, dt in enumerate((0.9, 2.3, 3.8)):                   # 三张能力卡
        add_at(sfx, sfx_pop(820 + i * 140), s(3, dt), gain=0.30)
    add_at(sfx, sfx_success(), s(3, 6.7), gain=0.44)           # 打破第四面墙

    add_at(sfx, sfx_whoosh(), s(4, 0.15), gain=0.24)           # 转场：破局
    add_at(sfx, sfx_whoosh(), s(4, 4.0), gain=0.24)            # CodeDeck 卡展开
    add_at(sfx, sfx_success(), s(4, 6.6), gain=0.46)           # 几十块价格揭晓

    add_at(sfx, sfx_whoosh(), s(5, 0.10), gain=0.24)           # 转场：工作台
    add_at(sfx, sfx_tick(2400), s(5, 4.9), gain=0.34)          # 光标点击
    add_at(sfx, sfx_pop(1046), s(5, 5.1), gain=0.34)
    # 定版卡落点：与 build_html.py 的 endAt 完全一致（最后一句读完 +0.15s）
    vo_end = float(TL.get("vo_end", SCN[-1]["end"]))
    add_at(sfx, sfx_success(), s(5, max(0.5, vo_end - SCN[5]["start"] + 0.15)), gain=0.48)

    # 人声为绝对主体；不再用 tanh 软削波（会加谐波、听感发毛）
    mix = vo * 1.00 + bgm * 0.26 + sfx * 0.34
    tail = int(0.6 * SR)
    mix[-tail:] *= np.linspace(1.0, 0.0, tail)
    peak = np.abs(mix).max() or 1.0
    mix = mix / peak * 0.72          # 留 6dB 余量给后面的 loudnorm

    # --stems 时额外导出分层，方便定位「噪音」到底来自哪一层
    if "--stems" in sys.argv:
        for nm, sig in (("stem_vo", vo), ("stem_bgm", bgm), ("stem_sfx", sfx)):
            with wave.open(str(HERE / f"{nm}.wav"), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
                w.writeframes((np.clip(sig, -1, 1) * 32767).astype(np.int16).tobytes())

    out = HERE / "mix.wav"
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print(f"Wrote {out} ({DUR}s, cues from marks of {len(SCN)} scenes)")


if __name__ == "__main__":
    main()
