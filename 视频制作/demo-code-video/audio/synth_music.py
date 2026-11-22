#!/usr/bin/env python3
"""10s 120 BPM code-synthesized soundtrack + synced UI/transition SFX."""
import pathlib
import wave
import numpy as np

SR = 48000
DUR = 10.0
N = int(SR * DUR)
OUT = pathlib.Path(__file__).resolve().parent / "mix.wav"


def env(n, attack=0.005, decay=0.2):
    x = np.arange(n) / SR
    return np.minimum(1.0, x / max(attack, 1e-4)) * np.exp(-x / decay)


def lowpass(sig, cutoff):
    a = np.exp(-2.0 * np.pi * cutoff / SR)
    out = np.zeros_like(sig)
    y = 0.0
    for i, s in enumerate(sig):
        y = (1.0 - a) * s + a * y
        out[i] = y
    return out


def highpass(sig, cutoff):
    return sig - lowpass(sig, cutoff)


def soft_kick(length=0.28):
    n = int(length * SR)
    f = np.geomspace(135.0, 46.0, n)
    phase = 2.0 * np.pi * np.cumsum(f) / SR
    return np.sin(phase) * env(n, 0.002, 0.09)


def crisp_hat(length=0.045, seed=11):
    n = int(length * SR)
    rng = np.random.default_rng(seed)
    noise = rng.standard_normal(n)
    return highpass(noise, 5500) * env(n, 0.001, 0.012)


def warm_chord(freqs, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for f in freqs:
        # 基频 + 失谐双声部 + 2/3次泛音，避免纯正弦单薄
        sig += 0.50 * np.sin(2 * np.pi * f * t)
        sig += 0.25 * np.sin(2 * np.pi * (f * 1.003) * t + 0.4)
        sig += 0.25 * np.sin(2 * np.pi * (f * 0.997) * t + 1.1)
        sig += 0.14 * np.sin(2 * np.pi * (f * 2.0) * t)
        sig += 0.05 * np.sin(2 * np.pi * (f * 3.0) * t)
    sig /= max(1, len(freqs))
    # 柔和起音与尾音衰减，防止切段爆音
    fade_in = np.minimum(1.0, t / 0.06)
    fade_out = np.minimum(1.0, (dur - t) / 0.14)
    return sig * fade_in * np.maximum(0.0, fade_out) * np.exp(-t / 1.9)


def warm_bass(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = 0.72 * np.sin(2 * np.pi * freq * t) + 0.28 * np.sin(2 * np.pi * (freq * 2.0) * t)
    fade_in = np.minimum(1.0, t / 0.02)
    fade_out = np.minimum(1.0, (dur - t) / 0.08)
    return sig * fade_in * np.maximum(0.0, fade_out)


def add_at(buf, sig, t_sec, gain=1.0):
    i = int(round(t_sec * SR))
    if i >= len(buf) or i < 0:
        return
    n = min(len(sig), len(buf) - i)
    buf[i : i + n] += sig[:n] * gain


def sfx_click():
    n = int(0.04 * SR)
    rng = np.random.default_rng(3)
    x = np.arange(n) / SR
    n_part = rng.standard_normal(n) * env(n, 0.0005, 0.004) * 0.5
    t_part = np.sin(2 * np.pi * 2300 * x) * env(n, 0.001, 0.008) * 0.6
    return n_part + t_part


def sfx_tick(freq=2900):
    n = int(0.035 * SR)
    x = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * x) * env(n, 0.001, 0.007)


def sfx_pop():
    n1 = int(0.05 * SR)
    x1 = np.arange(n1) / SR
    p1 = np.sin(2 * np.pi * 880 * x1) * env(n1, 0.002, 0.025)
    n2 = int(0.28 * SR)
    x2 = np.arange(n2) / SR
    p2 = 0.5 * (np.sin(2 * np.pi * 1175 * x2) + np.sin(2 * np.pi * 1760 * x2)) * env(n2, 0.002, 0.09)
    return np.concatenate([p1, p2])


def sfx_whoosh():
    n = int(0.36 * SR)
    rng = np.random.default_rng(9)
    return lowpass(rng.standard_normal(n), 2200) * np.hanning(n) * 1.4


def sfx_success():
    n1 = int(0.08 * SR)
    x1 = np.arange(n1) / SR
    p1 = np.sin(2 * np.pi * 1318.5 * x1) * env(n1, 0.002, 0.05)
    n2 = int(0.45 * SR)
    x2 = np.arange(n2) / SR
    p2 = 0.5 * (np.sin(2 * np.pi * 1318.5 * x2) + np.sin(2 * np.pi * 1975.5 * x2)) * env(n2, 0.002, 0.14)
    return np.concatenate([p1, p2])


def main():
    mix = np.zeros(N, dtype=np.float64)

    # 1. 和弦铺底与贝斯（对应 4 个镜头：0.0-2.5, 2.5-5.2, 5.2-7.8, 7.8-10.0）
    sections = [
        (0.0, 2.5, 87.31, [174.61, 220.00, 261.63, 329.63]),  # Fmaj7
        (2.5, 2.7, 82.41, [164.81, 196.00, 246.94, 293.66]),  # Em7
        (5.2, 2.6, 73.42, [146.83, 174.61, 220.00, 261.63]),  # Dm7
        (7.8, 2.2, 65.41, [196.00, 246.94, 261.63, 329.63]),  # Cmaj7
    ]
    for st, d, bass_f, ch in sections:
        add_at(mix, warm_chord(ch, d), st, gain=0.28)
        add_at(mix, warm_bass(bass_f, d), st, gain=0.16)

    # 点缀轻音符琶音（每 0.5s 拍点温柔弹一颗电钢音）
    arp_notes = [329.63, 349.23, 440.00, 523.25, 392.00, 493.88, 587.33, 523.25]
    for b in range(20):
        t_b = b * 0.5
        f = arp_notes[b % len(arp_notes)]
        n_note = int(0.45 * SR)
        tn = np.arange(n_note) / SR
        plk = (0.65 * np.sin(2 * np.pi * f * tn) + 0.25 * np.sin(2 * np.pi * f * 2 * tn)) * env(n_note, 0.004, 0.16)
        add_at(mix, plk, t_b, gain=0.14)

    # 2. 120 BPM 鼓组（每 0.5s 一拍底鼓，每 0.25s 轻踩镲）
    k = soft_kick()
    for b in range(20):
        t_b = b * 0.5
        add_at(mix, k, t_b, gain=0.40 if b % 2 == 0 else 0.24)
        if t_b + 0.25 < DUR:
            add_at(mix, crisp_hat(seed=b + 1), t_b + 0.25, gain=0.07)

    # 3. 精准对齐画面关键帧的动作音效
    add_at(mix, sfx_pop(), 0.50, gain=0.35)
    add_at(mix, sfx_whoosh(), 2.46, gain=0.28)
    for t_clk in (2.85, 3.45, 4.05, 4.65):
        add_at(mix, sfx_click(), t_clk, gain=0.38)
    add_at(mix, sfx_whoosh(), 5.16, gain=0.28)
    for idx, t_card in enumerate((5.42, 5.64, 5.86)):
        add_at(mix, sfx_tick(2400 + idx * 350), t_card, gain=0.25)
    add_at(mix, sfx_success(), 6.70, gain=0.40)
    add_at(mix, sfx_whoosh(), 7.76, gain=0.28)
    for idx, t_asp in enumerate((8.05, 8.40, 8.75)):
        add_at(mix, sfx_tick(2600 + idx * 320), t_asp, gain=0.24)
    add_at(mix, sfx_success(), 9.10, gain=0.34)

    # 简易自然混响（短延迟反馈）+ 淡出保护
    delay = int(0.11 * SR)
    wet = np.zeros_like(mix)
    wet[delay:] = mix[:-delay] * 0.18
    mix = mix + wet
    tail = int(0.12 * SR)
    mix[-tail:] *= np.linspace(1.0, 0.0, tail)

    # 温和限幅与输出
    peak = np.abs(mix).max() or 1.0
    mix = (mix / peak) * 0.85
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print(f"wrote {OUT} ({DUR}s, peak={peak:.3f})")


if __name__ == "__main__":
    main()
