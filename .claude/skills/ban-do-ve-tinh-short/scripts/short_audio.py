import os, subprocess, numpy as np
from scipy import signal
from scipy.io import wavfile
HERE = os.path.abspath(os.environ.get("WORK", os.getcwd()))
SKILL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SR = 48000; DUR = 26.3; N = int(SR * DUR); t = np.arange(N) / SR; r = np.random.default_rng(2)
VO = [("l1", 0.15), ("l2", 3.30), ("l3", 5.15), ("l4", 8.40), ("l5", 10.15), ("l6", 12.20), ("l7", 15.20), ("l8", 21.00)]
def lp(x, f): return signal.sosfilt(signal.butter(4, f, "low", fs=SR, output="sos"), x)
def bp(x, a, b): return signal.sosfilt(signal.butter(2, [a, b], "band", fs=SR, output="sos"), x)
def place(buf, s, at, g=1.0):
    i = int(at * SR); n = min(len(s), len(buf) - i)
    if n > 0: buf[i:i + n] += s[:n] * g
def load(name):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(HERE, "aud", name + ".wav"), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)
voice = np.zeros(N)
for k, at in VO: place(voice, load(k), at)
voice /= np.abs(voice).max()
# nhạc nền: nhịp nhẹ, hợp âm Am - F - C - G, 100 bpm
bpm = 100; beat = 60 / bpm
chords = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (130.81, 164.81, 196.0), (196.0, 246.94, 293.66)]
mus = np.zeros(N)
for i in range(int(DUR / (beat * 4)) + 1):
    ch = chords[i % 4]; t0 = i * beat * 4; n = int(beat * 4 * SR); k = np.arange(n) / SR
    pad = sum(np.sin(2 * np.pi * f * k) + 0.3 * np.sin(4 * np.pi * f * k) for f in ch) * np.minimum(1, k / 0.3) * np.exp(-k * 0.25)
    place(mus, pad * 0.12, t0)
    for b in range(8):                       # arpeggio móc
        f = ch[b % 3] * 2; nn = int(0.18 * SR); kk = np.arange(nn) / SR
        place(mus, np.sin(2 * np.pi * f * kk) * np.exp(-kk * 18) * 0.10, t0 + b * beat / 2)
    for b in range(4):                       # kick + hat
        nn = int(0.25 * SR); kk = np.arange(nn) / SR
        place(mus, np.sin(2 * np.pi * (55 + 60 * np.exp(-kk * 40)) * kk) * np.exp(-kk * 12) * 0.35, t0 + b * beat)
        place(mus, bp(r.standard_normal(int(0.05 * SR)), 6000, 12000) * np.exp(-np.arange(int(0.05 * SR)) / SR * 80) * 0.05, t0 + b * beat + beat / 2)
mus = lp(mus, 9000)
# hiệu ứng: lướt khi zoom, bụp khi hiện nhãn
def whoosh(d, up=True):
    n = int(d * SR); k = np.arange(n) / SR; s = r.standard_normal(n); out = np.zeros(n)
    for i in range(0, n, 1200):
        u = i / n; fc = 400 + 3000 * (u if up else 1 - u); seg = bp(s[i:i + 1200], fc * 0.6, fc * 1.4); out[i:i + len(seg)] = seg
    return out * np.sin(np.pi * k / d) ** 2 / (np.abs(out).max() + 1e-9)
fx = np.zeros(N)
for at, d in [(1.2, 1.9), (5.2, 1.2), (6.5, 1.8), (8.3, 1.8), (10.1, 1.8), (12.3, 2.4), (21.1, 1.5)]: place(fx, whoosh(d), at, 0.22)
for at in (3.15, 11.85): place(fx, whoosh(0.35, False), at - 0.1, 0.35)
def popk():
    n = int(0.12 * SR); k = np.arange(n) / SR; return np.sin(2 * np.pi * (900 - 2500 * k) * k) * np.exp(-k * 40)
for at in (1.95, 2.45, 3.45, 5.3, 5.4, 6.75, 7.0, 7.15, 8.55, 10.35, 11.85, 12.65, 13.6, 15.6, 17.1, 22.7, 23.35): place(fx, popk(), at, 0.18)
n = int(1.2 * SR); k = np.arange(n) / SR
place(fx, (np.sin(2 * np.pi * 1320 * k) + 0.5 * np.sin(2 * np.pi * 1980 * k)) * np.exp(-k * 4), 22.45, 0.08)
env = np.ones(N); venv = lp(np.abs(voice), 5); env -= 0.45 * np.clip(venv / 0.15, 0, 1)
mix = voice * 0.9 + (mus * env * 0.6 + fx * 0.8)
mix *= np.clip((DUR - t) / 0.5, 0, 1)
mix = np.tanh(mix / np.abs(mix).max() * 1.2) * 0.9
wavfile.write(os.path.join(HERE, "audio.wav"), SR, (np.stack([mix, mix], -1) * 32767).astype(np.int16)); print("ok")
