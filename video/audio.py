"""Synthesize royalty-free lo-fi music + SFX matched to the shot timeline."""
import sys
import wave
import numpy as np
from story import SHOTS

SR = 44100
rng = np.random.default_rng(7)


def env(n, a=0.005, d=0.3):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def tone(freq, dur, kind="sine", a=0.005, d=0.3):
    n = int(dur * SR)
    t = np.arange(n) / SR
    if kind == "epiano":
        x = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t * 6) \
            + 0.12 * np.sin(2 * np.pi * 3 * freq * t) * np.exp(-t * 9)
    else:
        x = np.sin(2 * np.pi * freq * t)
    return x * env(n, a, d)


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):  # small arrays only
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def lp_fast(x, cutoff):
    # FFT brick-ish lowpass for long signals
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def add(buf, x, at):
    i = int(at * SR)
    if i >= len(buf):
        return
    x = x[: len(buf) - i]
    buf[i:i + len(x)] += x


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


def music(total, calm_ranges):
    bpm = 84
    beat = 60 / bpm
    buf = np.zeros(int(total * SR) + SR)
    drums = np.zeros_like(buf)
    chords = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 64]]  # Am7 Fmaj7 Cmaj7 G6
    bar = 4 * beat
    nb = int(total / bar) + 1
    for b in range(nb):
        t0 = b * bar
        ch = chords[b % 4]
        for hit, vel in ((0, 1.0), (1.5, 0.6), (2.5, 0.75)):
            for k, m in enumerate(ch):
                add(buf, 0.09 * vel * tone(midi(m), 1.6, "epiano", 0.01, 0.9), t0 + hit * beat + k * 0.012)
        add(buf, 0.22 * tone(midi(ch[0] - 24), bar * 0.9, "sine", 0.02, 1.2), t0)
        add(buf, 0.16 * tone(midi(ch[0] - 24 + 7), beat * 0.9, "sine", 0.02, 0.5), t0 + 2.5 * beat)
        # melody sprinkle
        mel = [ch[3] + 12, ch[2] + 12, ch[1] + 12, ch[2] + 12]
        for j, m in enumerate(mel):
            if (b + j) % 3 != 1:
                add(buf, 0.045 * tone(midi(m), 0.8, "sine", 0.005, 0.35), t0 + (j + 0.5) * beat)
        for q in range(4):
            tb = t0 + q * beat
            if q in (0, 2):
                n = int(0.35 * SR)
                tt = np.arange(n) / SR
                f = 50 + 70 * np.exp(-tt * 30)
                add(drums, 0.55 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9), tb)
            if q in (1, 3):
                n = int(0.2 * SR)
                nz = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 22)
                add(drums, 0.12 * (nz - np.convolve(nz, np.ones(8) / 8, "same")), tb)
            for e in (0, 0.5):
                n = int(0.05 * SR)
                nz = rng.standard_normal(n)
                nz = nz - np.convolve(nz, np.ones(4) / 4, "same")
                add(drums, 0.035 * nz * np.exp(-np.arange(n) / SR * 80), tb + e * beat + 0.012 * (e > 0))
    # duck drums during calm (emotional) ranges
    g = np.ones_like(buf)
    tt = np.arange(len(buf)) / SR
    for a, b in calm_ranges:
        fade = np.clip(np.minimum((tt - a) / 0.6, (b - tt) / 0.6), 0, 1)
        g = np.minimum(g, 1 - 0.9 * fade)
    mix = lp_fast(buf, 2600) + drums * g
    crackle = (rng.random(len(buf)) > 0.9993) * rng.standard_normal(len(buf)) * 0.05
    mix += crackle + 0.004 * rng.standard_normal(len(buf))
    return mix


def sfx(kind):
    if kind == "tick":
        x = np.concatenate([0.5 * tone(1320, 0.05, d=0.02), 0.6 * tone(1980, 0.35, d=0.12)])
        y = np.pad(tone(2640, 0.3, d=0.1), (int(0.05 * SR), 0))
        x = np.pad(x, (0, max(0, len(y) - len(x))))
        x[: len(y)] += 0.25 * y
        return x
    if kind == "pop":
        n = int(0.12 * SR)
        t = np.arange(n) / SR
        f = 900 * np.exp(-t * 18) + 300
        return 0.45 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)
    if kind == "whoosh":
        n = int(0.9 * SR)
        t = np.arange(n) / SR
        nz = rng.standard_normal(n)
        nz = lowpass(nz, 1800)
        return 0.9 * nz * np.sin(np.pi * t / 0.9) ** 2
    if kind == "sting":
        x = sum(0.18 * tone(midi(m), 1.2, "epiano", 0.003, 0.5) for m in (70, 73, 77))
        n = int(0.25 * SR)
        x[:n] += 0.3 * rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 25)
        return x
    if kind == "scribble":
        n = int(0.45 * SR)
        t = np.arange(n) / SR
        nz = rng.standard_normal(n)
        nz = nz - np.convolve(nz, np.ones(6) / 6, "same")
        return 0.18 * nz * (0.5 + 0.5 * np.sin(2 * np.pi * 14 * t)) * np.sin(np.pi * t / 0.45)
    raise ValueError(kind)


def build(path):
    total = sum(s.dur for s in SHOTS)
    t0, events, starts = 0.0, [], []
    for s in SHOTS:
        starts.append(t0)
        for rt, k in s.sfx:
            events.append((t0 + rt, k))
        t0 += s.dur
    # calm: sister confession + grandma + reflection (shots 11-13)
    calm = [(starts[10], starts[13])]
    m = music(total, calm)
    m = 0.55 * m / np.max(np.abs(m))
    fx = np.zeros_like(m)
    for at, k in events:
        add(fx, sfx(k), at)
    mix = m + 0.7 * fx
    n = int(total * SR)
    mix = mix[:n]
    fade = np.ones(n)
    fade[: int(0.4 * SR)] = np.linspace(0, 1, int(0.4 * SR))
    fade[-int(1.5 * SR):] = np.linspace(1, 0, int(1.5 * SR))
    mix *= fade
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix = 0.89 * mix / np.max(np.abs(mix))
    st = np.stack([mix, np.roll(mix, 220) * 0.98], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    build(sys.argv[1])
