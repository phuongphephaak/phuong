"""Âm thanh tổng hợp cho cảnh Waterloo 24s: nhạc nền trầm + pháo xa + súng hỏa mai + vó ngựa + tiếng lướt hiệu ứng."""
import os
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000; DUR = 24.0; N = int(SR * DUR)
r = np.random.default_rng(4)
t = np.arange(N) / SR


def lp(x, f, o=4): return signal.sosfilt(signal.butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, a, b, o=2): return signal.sosfilt(signal.butter(o, [a, b], "band", fs=SR, output="sos"), x)


def env(a, b, fi, fo):
    e = np.clip((t - a) / fi, 0, 1) * np.clip((b - t) / fo, 0, 1); return e * e * (3 - 2 * e)


def place(buf, snd, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf): return
    n = min(len(snd), len(buf) - i); buf[i:i + n] += snd[:n] * gain


def reverb(x, sec=2.2, mix=0.35):
    n = int(sec * SR); ir = r.standard_normal(n) * np.exp(-np.arange(n) / SR * 3.2)
    ir = lp(ir, 3000); ir /= np.abs(ir).sum() ** 0.5 * 30
    wet = signal.fftconvolve(x, ir)[:len(x)]
    return x * (1 - mix) + wet * mix * 6


mix = np.zeros(N)
# ---- nhạc nền: hợp âm Rê thứ trầm, dây đàn tổng hợp, phồng dần
pad = np.zeros(N)
for f, g in [(73.42, 1.0), (110.0, 0.7), (146.83, 0.55), (174.61, 0.45), (220.0, 0.30), (293.66, 0.18)]:
    for det in (-0.25, 0.0, 0.31):
        ph = r.uniform(0, 6.28)
        vib = 1 + 0.003 * np.sin(2 * np.pi * 5.1 * t + ph)
        pad += g * signal.sawtooth(2 * np.pi * f * (1 + det / 100) * t * vib + ph)
pad = lp(pad, 900) * (0.55 + 0.45 * np.clip(t / 8, 0, 1))
# đổi hợp âm sang Si giáng trưởng lúc kỵ binh xung phong
pad2 = np.zeros(N)
for f, g in [(58.27, 1.0), (116.54, 0.7), (174.61, 0.55), (233.08, 0.4), (293.66, 0.3)]:
    for det in (-0.2, 0.25):
        pad2 += g * signal.sawtooth(2 * np.pi * f * (1 + det / 100) * t + r.uniform(0, 6.28))
pad2 = lp(pad2, 1200)
xf = np.clip((t - 18.0) / 1.5, 0, 1)
music = pad * (1 - xf) + pad2 * xf * 1.15
# trống trầm nhịp hành quân khi Pháp tiến (9-17s)
drum = np.zeros(N)
for bt in np.arange(8.8, 17.6, 0.5):
    n = int(0.35 * SR); k = np.arange(n) / SR
    hit = np.sin(2 * np.pi * (62 + 40 * np.exp(-k * 30)) * k) * np.exp(-k * 9)
    hit += 0.25 * lp(r.standard_normal(n), 400) * np.exp(-k * 25)
    place(drum, hit, bt, 0.9 if int(bt * 2) % 4 == 0 else 0.55)
music = music / np.abs(music).max() * 0.20 + drum * 0.22
music *= env(0, 24, 1.5, 1.2)
mix += music

# ---- gió đồng nội
wind = lp(np.cumsum(r.standard_normal(N)) * 0.002, 500); wind = hp(wind, 40)
wind = wind / np.abs(wind).max() * 0.05 * (0.7 + 0.3 * np.sin(2 * np.pi * t / 7))
mix += wind


def boom(dist=1.0):
    n = int(2.5 * SR); k = np.arange(n) / SR
    s = lp(r.standard_normal(n), 180 / dist) * np.exp(-k * (5 / dist))
    s += 0.6 * np.sin(2 * np.pi * 42 * k) * np.exp(-k * 7)
    s += 0.25 * lp(r.standard_normal(n), 1500) * np.exp(-k * 40)
    return s / np.abs(s).max()


fx = np.zeros(N)
for bt in np.sort(r.uniform(0.3, 10.5, 16)):
    place(fx, boom(r.uniform(1, 1.6)), bt, r.uniform(0.35, 0.6))
for bt in np.sort(r.uniform(4, 18, 10)):
    place(fx, boom(r.uniform(1.6, 2.4)), bt, r.uniform(0.15, 0.25))
# hỏa mai: chuỗi nổ lách tách
for bt in np.sort(r.uniform(14.0, 19.8, 120)):
    n = int(0.25 * SR); k = np.arange(n) / SR
    s = bp(r.standard_normal(n), 700, 4000) * np.exp(-k * r.uniform(28, 45))
    place(fx, s / np.abs(s).max(), bt, r.uniform(0.06, 0.16) * (1 + 0.8 * ((bt > 15.5) & (bt < 18.5))))
# vó ngựa: rền + nhịp phi
gal = lp(r.standard_normal(N), 220) * (0.6 + 0.4 * np.clip(np.sin(2 * np.pi * 2.7 * t), 0, 1) ** 2)
gal = gal / np.abs(gal).max() * env(18.2, 23.8, 1.2, 1.6) * 0.55
fx += gal
for bt in np.arange(18.4, 23.2, 0.123):
    n = int(0.08 * SR); k = np.arange(n) / SR
    place(fx, lp(r.standard_normal(n), 900) * np.exp(-k * 60), bt + r.uniform(-0.03, 0.03), 0.08 * min(1, (bt - 18.3) / 1.2))
# tiếng hô xung phong (nhiễu băng hẹp mô phỏng đám đông xa)
crowd = bp(r.standard_normal(N), 300, 900, 3) * (1 + 0.5 * np.sin(2 * np.pi * 0.7 * t))
fx += crowd / np.abs(crowd).max() * env(18.8, 22.6, 0.8, 1.5) * 0.10
fx = reverb(fx, 2.4, 0.4)
mix += fx * 0.8


def whoosh(d=0.9, up=True):
    n = int(d * SR); k = np.arange(n) / SR; s = r.standard_normal(n)
    out = np.zeros(n)
    for i in range(0, n, 2400):
        u = i / n; fc = 300 + (2500 if up else 1500) * (u if up else 1 - u)
        seg = bp(s[i:i + 2400], fc * 0.7, fc * 1.3); out[i:i + len(seg)] = seg
    e = np.sin(np.pi * k / d) ** 2
    return out * e / (np.abs(out).max() + 1e-9)


ui = np.zeros(N)
for at in (4.3, 17.1):            # đổi giờ
    place(ui, whoosh(0.7), at, 0.10)
    n = int(1.2 * SR); k = np.arange(n) / SR
    place(ui, (np.sin(2 * np.pi * 880 * k) + 0.5 * np.sin(2 * np.pi * 1320 * k)) * np.exp(-k * 5), at + 0.25, 0.035)
place(ui, whoosh(1.2), 4.9, 0.10)     # vòng tròn
for at in (9.0, 9.25, 9.5, 9.75):     # mũi tên
    place(ui, whoosh(1.6), at, 0.06)
place(ui, whoosh(1.8, False), 18.4, 0.10)
mix += reverb(ui, 1.5, 0.3)

mix = hp(mix, 25)
mix *= env(0, 24, 0.6, 1.0)
mix = np.tanh(mix / np.abs(mix).max() * 1.4) * 0.85
st = np.stack([mix, np.roll(mix, 37)], -1)
wavfile.write(os.path.join(os.environ.get("WORK", os.getcwd()), "audio.wav"), SR, (st * 32767).astype(np.int16))
print("ok")
