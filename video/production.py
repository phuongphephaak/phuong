"""Full-episode production: TTS, timing, camera, crowd, render (parallel), audio mix."""
import hashlib
import json
import math
import os
import subprocess
import sys
import wave
from multiprocessing import Pool

import cairo
import numpy as np

from engine import W, H, Char, draw_char, bubble, tag, caption, ease
from scenes import GROUND, haze

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "voice", "cache")
VOICE_ID = "rU18Fk3uSDhmg5Xh41o4"  # Ryan Kurk - Pleasant and Smooth
FPS = 30
SR = 44100


# ------------------------------------------------------------------ TTS
def tts(text, who):
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.sha1(f"{VOICE_ID}|v2|{text}".encode()).hexdigest()[:16]
    wav = os.path.join(CACHE, key + ".wav")
    if not os.path.exists(wav):
        mp3 = os.path.join(CACHE, key + ".mp3")
        body = {"text": text, "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.45 if who != "vo" else 0.5, "similarity_boost": 0.75,
                                   "style": 0.3 if who != "vo" else 0.15, "use_speaker_boost": True}}
        for attempt in range(4):
            r = subprocess.run(["curl", "-sS", "-f", "-X", "POST",
                                f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128",
                                "-H", f"xi-api-key: {os.environ['ELEVENLABS_API_KEY']}",
                                "-H", "Content-Type: application/json", "-d", json.dumps(body), "-o", mp3])
            if r.returncode == 0:
                break
        else:
            raise RuntimeError("TTS failed: " + text)
        # trim leading/trailing silence, mono 44.1k
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse",
                        "-ac", "1", "-ar", str(SR), wav], check=True)
    with wave.open(wav) as w:
        return wav, w.getnframes() / SR


def prepare(beats):
    t = 0.0
    for b in beats:
        for ln in b.lines:
            ln.wav, ln.dur = tts(ln.text, ln.who)
        b.layout()
        b.start = t
        t += b.dur
    return t


# ------------------------------------------------------------------ crowd
POOL = [
    Char("#d9a47a", "#6c8ebf", hair="short", hair_c="#2b2420", blink_phase=0.2),
    Char("#8d5a3b", "#e9c46a", hair="bob", hair_c="#1e1714", blink_phase=1.2),
    Char("#f2c9a0", "#7b5c99", hair="ponytail", hair_c="#a0522d", blink_phase=2.2),
    Char("#c98e64", "#5f8f5a", hair="cap", hair_c="#c0392b", blink_phase=0.9),
    Char("#efc6a6", "#b4503e", hair="spiky", hair_c="#3b2a20", blink_phase=1.7),
    Char("#a86f4c", "#3a3f5c", hair="slick", hair_c="#1f1a17", extra=("suit",), blink_phase=2.9),
]


def crowd(ctx, b, t, labels):
    rng = np.random.default_rng(len(b.lines) * 31 + int(b.start * 7) + 3)
    for i in range(b.crowd):
        c = POOL[int(rng.integers(len(POOL)))]
        speed = float(rng.uniform(130, 210)) * (1 if rng.random() < 0.5 else -1)
        x0 = float(rng.uniform(-900, 2800))
        span = 3800
        x = -900 + ((x0 + 900 + speed * t) % span)
        s = float(rng.uniform(0.52, 0.6))
        y = GROUND - 40 - 10 * (i % 3)
        draw_char(ctx, c, x, y, s, t + i, expr="neutral", flip=speed < 0, walk=abs(speed * t) * 0.03,
                  stride=0.9, look=0.6)
        if labels:
            from engine import counter_label
            counter_label(ctx, x, y - 725 * s, int(rng.integers(300, 40000)), s=0.62)
    haze(ctx, a=0.12)


# ------------------------------------------------------------------ camera
def focus_of(b, spec, t):
    kind = spec[0]
    if kind == "wide":
        return 960, 560, spec[1]
    if kind == "at":
        return spec[1], spec[2], spec[3]
    if kind in ("on", "track"):
        a = next(a for a in b.actors if a.name == spec[1])
        x, *_ = b.actor_x(a, t)
        z = spec[2]
        fy = (a.y - (a.head * 0.75 if a.drawfn else 520) * a.s) if kind == "on" else 560
        return x, fy, z
    if kind == "two":
        a1 = next(a for a in b.actors if a.name == spec[1])
        a2 = next(a for a in b.actors if a.name == spec[2])
        x1, *_ = b.actor_x(a1, t)
        x2, *_ = b.actor_x(a2, t)
        return (x1 + x2) / 2, a1.y - 470 * a1.s, spec[3]
    raise ValueError(spec)


def auto_cams(b):
    cams = [(0.0, ("wide", 1.0))]
    names = {a.name for a in b.actors}
    multi = len([a for a in b.actors if not a.cat]) > 1
    for i, ln in enumerate(b.lines):
        if ln.who != "vo" and ln.who in names and multi:
            cams.append((ln.start - 0.05, ("on", ln.who, 1.5)))
            nxt = b.lines[i + 1] if i + 1 < len(b.lines) else None
            if nxt is None or nxt.who == "vo":
                cams.append((ln.end + 0.25, ("wide", 1.0)))
    return cams


def camera(b, t):
    cams = b.cams if b.cams is not None else auto_cams(b)
    cams = [(b.ref(r) if not isinstance(r, float) else r, s) for r, s in cams]
    cur, seg_start, seg_end = cams[0][1], cams[0][0], b.dur
    for i, (tt, spec) in enumerate(cams):
        if t >= tt:
            cur, seg_start = spec, tt
            seg_end = cams[i + 1][0] if i + 1 < len(cams) else b.dur
    fx, fy, z = focus_of(b, cur, t)
    k = (t - seg_start) / max(0.5, seg_end - seg_start)
    z *= 1 + 0.05 * ease(k)
    hw, hh = W / 2 / z, H / 2 / z
    fx = min(max(fx, -780 + hw), W + 780 - hw)
    fy = min(max(fy, -380 + hh), H + 380 - hh)
    return fx, fy, z


# ------------------------------------------------------------------ frame
def vignette():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, W * 0.72)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.38)
    c.set_source(g)
    c.paint()
    return s


def render_frame(surf, b, t, vig):
    ctx = cairo.Context(surf)
    fx, fy, z = camera(b, t)
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-fx, -fy)
    b.bg(ctx, t)
    if b.back:
        b.back(ctx, t, b)
    if b.crowd:
        crowd(ctx, b, t, labels=getattr(b, "crowd_labels", False))
    anchors = {}
    b.draw_actors(ctx, t, anchors)
    if b.front:
        b.front(ctx, t, b)
    ctx.restore()
    ctx.set_source_surface(vig)
    ctx.paint()
    if b.sepia:
        surf.flush()
        a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
        bb, gg, rr = a[..., 0].astype(np.float32), a[..., 1].astype(np.float32), a[..., 2].astype(np.float32)
        lum = 0.3 * rr + 0.59 * gg + 0.11 * bb
        a[..., 2] = np.clip(lum * 1.08 + 18, 0, 255)
        a[..., 1] = np.clip(lum * 0.92 + 8, 0, 255)
        a[..., 0] = np.clip(lum * 0.72, 0, 255)
        surf.mark_dirty()
        ctx = cairo.Context(surf)
    if b.bubbles:
        for ln in b.lines:
            if ln.who == "vo" or ln.who not in anchors:
                continue
            if ln.start - 0.05 <= t <= ln.end + 0.35:
                ax, ay, s, facing = anchors[ln.who]
                sx, sy = (ax - fx) * z + W / 2, (ay - fy) * z + H / 2
                side = facing if facing else 1
                act = next((a for a in b.actors if a.name == ln.who), None)
                if act is not None and act.thought:
                    from animals import thought
                    thought(ctx, sx, sy, ln.text, t - ln.start + 0.05, color=act.thought, side=side)
                    continue
                sx += side * 70 * s * z
                bubble(ctx, sx, sy, ln.text.replace("’", "'"), t - ln.start + 0.05, side=side,
                       size=40, maxw=620)
    for txt, tt in b.tags:
        if t >= tt:
            tag(ctx, txt, 60, 50, t - tt)
    if b.screen:
        b.screen(ctx, t, b)
    if b.cap:
        caption(ctx, b.cap[0], t - b.ref(b.cap[1]))
    # fade from/to black at beat edges for title cards
    if getattr(b, "fade_in", False) and t < 0.4:
        ctx.set_source_rgba(0, 0, 0, 1 - t / 0.4)
        ctx.paint()


_BEATS = None


def _render_chunk(args):
    idxs, path, beats_module = args
    mod = __import__(beats_module)
    beats = mod.BEATS
    prepare(beats)
    vig = vignette()
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "20", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    for i in idxs:
        b = beats[i]
        f0 = int(round(b.start * FPS))
        f1 = int(round((b.start + b.dur) * FPS))
        for f in range(f0, f1):
            render_frame(surf, b, f / FPS - b.start, vig)
            surf.flush()
            ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close()
    ff.wait()
    return path


def render_video(beats_module, out, workers=4):
    mod = __import__(beats_module)
    beats = mod.BEATS
    total = prepare(beats)
    # split beats into contiguous chunks of roughly equal duration
    chunks, cur, acc, target = [], [], 0.0, total / workers
    for i, b in enumerate(beats):
        cur.append(i)
        acc += b.dur
        if acc >= target and len(chunks) < workers - 1:
            chunks.append(cur)
            cur, acc = [], 0.0
    if cur:
        chunks.append(cur)
    tmp = os.path.abspath(os.path.join(os.path.dirname(out), "_chunks"))
    os.makedirs(tmp, exist_ok=True)
    jobs = [(c, os.path.join(tmp, f"c{k:02d}.mp4"), beats_module) for k, c in enumerate(chunks)]
    with Pool(len(jobs)) as p:
        paths = p.map(_render_chunk, jobs)
    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        for pth in paths:
            f.write(f"file '{pth}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out],
                   check=True)
    return total


# ------------------------------------------------------------------ audio
def build_audio(beats_module, out):
    import audio as A
    mod = __import__(beats_module)
    beats = mod.BEATS
    total = prepare(beats)
    n = int(total * SR) + SR
    voice = np.zeros(n)
    fx = np.zeros(n)
    calm, silent = [], []
    for b in beats:
        if b.music == "calm":
            calm.append((b.start, b.start + b.dur))
        if b.music == "none":
            silent.append((b.start, b.start + b.dur))
        for ln in b.lines:
            with wave.open(ln.wav) as w:
                x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
            peak = np.max(np.abs(x)) or 1
            A.add(voice, 0.9 * x / peak, b.start + ln.start)
            if ln.who != "vo" and b.bubbles:
                A.add(fx, 0.25 * A.sfx("pop"), b.start + ln.start - 0.02)
        for a in b.actors:
            if a.label is not None:
                if a.label_at > 0.05:
                    A.add(fx, 0.6 * A.sfx("pop"), b.start + a.label_at)
                for tt in a.label.ticks:
                    A.add(fx, A.sfx("tick"), b.start + tt)
        for tt, kind in b.sfx:
            A.add(fx, sfx2(kind) if kind in EXTRA else A.sfx(kind), b.start + tt)
    music = A.music(total + 1, calm)[:n]
    tt = np.arange(n) / SR
    g = np.ones(n)
    for a0, a1 in silent:
        fade = np.clip(np.minimum((tt - a0) / 0.3, (a1 - tt) / 0.3), 0, 1)
        g = np.minimum(g, 1 - fade)
    # ducking under voice
    env = np.convolve(np.abs(voice), np.ones(2048) / 2048, "same")
    duck = 1 - 0.6 * np.clip(env * 12, 0, 1)
    duck = np.convolve(duck, np.ones(8820) / 8820, "same")
    m = 0.32 * music / np.max(np.abs(music)) * g * duck
    mix = voice + m + 0.55 * fx
    mix = mix[: int(total * SR)]
    mix[-int(2 * SR):] *= np.linspace(1, 0, int(2 * SR))
    mix = np.tanh(mix * 1.05) / np.tanh(1.05)
    mix = 0.9 * mix / np.max(np.abs(mix))
    st = np.stack([mix, mix], 1)
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
    # subtitles (.srt) for the uploaded video
    srt = os.path.splitext(out)[0] + ".srt"
    with open(srt, "w") as f:
        k = 1
        for b in beats:
            for ln in b.lines:
                f.write(f"{k}\n{_ts(b.start + ln.start)} --> {_ts(b.start + ln.end)}\n{ln.text}\n\n")
                k += 1
    return total


def _ts(t):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"


rng = np.random.default_rng(11)
EXTRA = {"knock", "slam", "crickets", "static", "sizzle", "offkey", "clock", "flutter", "scrape", "bark", "ding",
         "can"}


def sfx2(kind):
    import audio as A
    if kind == "knock":
        out = np.zeros(int(0.9 * SR))
        for i in range(3):
            n = int(0.08 * SR)
            tt = np.arange(n) / SR
            x = np.sin(2 * np.pi * 140 * tt) * np.exp(-tt * 50) + 0.3 * rng.standard_normal(n) * np.exp(-tt * 80)
            A.add(out, 0.8 * x, i * 0.22)
        return out
    if kind == "slam":
        n = int(0.6 * SR)
        tt = np.arange(n) / SR
        return 0.9 * (np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 12) + 0.4 * rng.standard_normal(n) * np.exp(-tt * 30))
    if kind == "crickets":
        out = np.zeros(int(2.5 * SR))
        for i in range(8):
            n = int(0.12 * SR)
            tt = np.arange(n) / SR
            x = np.sin(2 * np.pi * 4300 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 60 * tt)) * np.sin(np.pi * tt / 0.12)
            A.add(out, 0.12 * x, i * 0.3)
        return out
    if kind == "static":
        n = int(1.0 * SR)
        x = rng.standard_normal(n)
        return 0.12 * (x - np.convolve(x, np.ones(3) / 3, "same"))
    if kind == "sizzle":
        n = int(2.5 * SR)
        x = rng.standard_normal(n) * (0.6 + 0.4 * rng.random(n))
        x = x - np.convolve(x, np.ones(5) / 5, "same")
        return 0.07 * x * np.sin(np.pi * np.arange(n) / n)
    if kind == "offkey":
        out = np.zeros(int(3.0 * SR))
        notes = [60, 63.4, 58.2, 66.7, 61.1, 55.5]
        for i, m in enumerate(notes):
            f = 440 * 2 ** ((m - 69) / 12)
            n = int(0.45 * SR)
            tt = np.arange(n) / SR
            vib = np.sin(2 * np.pi * f * tt + 3 * np.sin(2 * np.pi * 6 * tt))
            saw = sum(np.sin(2 * np.pi * f * k * tt) / k for k in range(1, 6))
            A.add(out, 0.12 * (0.5 * vib + 0.5 * saw) * np.minimum(1, tt / 0.03) * np.exp(-tt * 1.5), i * 0.48)
        return out
    if kind == "clock":
        out = np.zeros(int(3.0 * SR))
        for i in range(6):
            A.add(out, 0.25 * A.tone(2200 if i % 2 else 1800, 0.04, d=0.01), i * 0.5)
        return out
    if kind == "flutter":
        n = int(1.0 * SR)
        tt = np.arange(n) / SR
        x = rng.standard_normal(n) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 18 * tt)))
        return 0.2 * np.convolve(x, np.ones(20) / 20, "same") * np.exp(-tt * 2)
    if kind == "bark":
        out = np.zeros(int(1.2 * SR))
        for i in range(3):
            n = int(0.16 * SR)
            tt = np.arange(n) / SR
            f = 420 * np.exp(-tt * 6) + 180
            x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + 0.5 * rng.standard_normal(n)
            x = np.convolve(x, np.ones(12) / 12, "same") * np.exp(-tt * 14)
            A.add(out, 0.6 * x, i * 0.32)
        return out
    if kind == "ding":
        return sum(0.25 * A.tone(f, 1.4, "sine", 0.002, 0.6) for f in (1318.5, 1975.5))
    if kind == "can":
        out = np.zeros(int(1.5 * SR))
        for i in range(5):
            n = int(0.1 * SR)
            tt = np.arange(n) / SR
            x = sum(np.sin(2 * np.pi * f * tt) for f in (2100, 3300, 4700)) * np.exp(-tt * 40)
            A.add(out, 0.12 * x / (1 + i * 0.5), i * 0.22 * (1 - i * 0.12))
        return out
    if kind == "scrape":
        n = int(0.5 * SR)
        tt = np.arange(n) / SR
        return 0.25 * np.sin(2 * np.pi * (300 + 200 * tt) * tt) * rng.random(n) * np.sin(np.pi * tt / 0.5)
    raise ValueError(kind)


if __name__ == "__main__":
    cmd, mod = sys.argv[1], sys.argv[2]
    if cmd == "prepare":
        print("total", round(prepare(__import__(mod).BEATS), 1))
    elif cmd == "audio":
        print("audio", build_audio(mod, sys.argv[3]))
    elif cmd == "video":
        print("video", render_video(mod, sys.argv[3]))
