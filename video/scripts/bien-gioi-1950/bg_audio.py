"""Âm thanh đoạn Cốc Xá: lời dẫn + nhạc trầm + súng, pháo, cối (tự tổng hợp)."""
import os, subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000; DUR = 62.0; N = int(SR * DUR); r = np.random.default_rng(4); t = np.arange(N) / SR
AUD_T = [1.0, 9.2, 18.3, 23.4, 30.2, 37.4, 46.2, 54.5]
def lp(x, f, o=4): return signal.sosfilt(signal.butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, a, b, o=2): return signal.sosfilt(signal.butter(o, [a, b], "band", fs=SR, output="sos"), x)
def env(a, b, fi, fo):
    e = np.clip((t - a) / fi, 0, 1) * np.clip((b - t) / fo, 0, 1); return e * e * (3 - 2 * e)
def place(buf, snd, at, g=1.0):
    i = int(at * SR); n = min(len(snd), len(buf) - i)
    if n > 0: buf[i:i + n] += snd[:n] * g
def reverb(x, sec=2.2, mix=0.35):
    n = int(sec * SR); ir = r.standard_normal(n) * np.exp(-np.arange(n) / SR * 3.2); ir = lp(ir, 3000); ir /= np.abs(ir).sum() ** 0.5 * 30
    return x * (1 - mix) + signal.fftconvolve(x, ir)[:len(x)] * mix * 6
# nhạc: hợp âm Rê thứ trầm, căng dần; trống trận khi tấn công
music = np.zeros(N)
for f, g in [(73.42, 1.0), (110.0, 0.7), (146.83, 0.5), (174.61, 0.4), (220.0, 0.25)]:
    for det in (-0.25, 0.0, 0.3):
        ph = r.uniform(0, 6.28); music += g * signal.sawtooth(2 * np.pi * f * (1 + det / 100) * t + ph)
music = lp(music, 800) * (0.5 + 0.5 * np.clip(t / 20, 0, 1))
music = music / np.abs(music).max() * 0.16
drum = np.zeros(N)
for bt in list(np.arange(18.2, 30.0, 0.5)) + list(np.arange(46.0, 54.0, 0.5)):
    n = int(0.35 * SR); k = np.arange(n) / SR
    hit = np.sin(2 * np.pi * (60 + 40 * np.exp(-k * 30)) * k) * np.exp(-k * 9) + 0.25 * lp(r.standard_normal(n), 400) * np.exp(-k * 25)
    place(drum, hit, bt, 0.8 if int(bt * 2) % 4 == 0 else 0.5)
bed = (music + drum * 0.18) * env(0, 62, 1.5, 2.0)
def boom(d=1.0):
    n = int(2.4 * SR); k = np.arange(n) / SR
    s = lp(r.standard_normal(n), 170 / d) * np.exp(-k * (5 / d)) + 0.5 * np.sin(2 * np.pi * 45 * k) * np.exp(-k * 7) + 0.2 * lp(r.standard_normal(n), 1500) * np.exp(-k * 40)
    return s / np.abs(s).max()
fx = np.zeros(N)
for bt in np.sort(r.uniform(18.6, 28.0, 18)): place(fx, boom(r.uniform(1, 1.8)), bt, r.uniform(0.25, 0.5))
for bt in np.sort(r.uniform(46.5, 53.0, 12)): place(fx, boom(r.uniform(1, 1.8)), bt, r.uniform(0.25, 0.45))
for lo, hi, cnt in [(18.8, 30.0, 260), (40.0, 46.0, 40), (46.4, 53.5, 200)]:
    for bt in np.sort(r.uniform(lo, hi, cnt)):
        n = int(0.2 * SR); k = np.arange(n) / SR; s = bp(r.standard_normal(n), 700, 4200) * np.exp(-k * r.uniform(30, 50))
        place(fx, s / np.abs(s).max(), bt, r.uniform(0.04, 0.12))
wind = hp(lp(np.cumsum(r.standard_normal(N)) * 0.002, 500), 40); fx += wind / np.abs(wind).max() * 0.04
fx = reverb(fx, 2.4, 0.4) * 0.7
# lời dẫn
voice = np.zeros(N)
for i, at in enumerate(AUD_T):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(HERE, "aud", f"c{i+1}.mp3"), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    place(voice, np.frombuffer(raw, np.float32).astype(np.float64), at)
venv = lp(np.abs(voice), 4); duck = 1 - 0.55 * np.clip(venv / (venv.max() * 0.25), 0, 1)
mix = (bed + fx) * duck + voice / np.abs(voice).max() * 0.85
mix = hp(mix, 25); mix = np.tanh(mix / np.abs(mix).max() * 1.3) * 0.88
wavfile.write(os.path.join(HERE, "bg_audio.wav"), SR, (np.stack([mix, np.roll(mix, 37)], -1) * 32767).astype(np.int16)); print("ok")
