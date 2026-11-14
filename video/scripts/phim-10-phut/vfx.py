"""Procedural combat VFX shots for the HMS Coventry draft (1920x1080, 30 fps).

Shots:
  approach.mp4 - two A-4 Skyhawks racing toward camera just above a rough sea
  attack.mp4   - A-4s cross over the real Coventry photo, ship fires tracers, bombs drop
  impact.mp4   - three bomb hits on the hull: flash, fireballs, debris, rising smoke

Usage: python vfx.py <bg_ship1.jpg> <bg_ship2.jpg> <out_dir> [shot ...]
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H, FPS = 1920, 1080, 30
rng = np.random.default_rng(7)


# ---------------------------------------------------------------- helpers
def encode(path, frames, n):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "17",
                          "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(n):
        f = frames(i, i / FPS)
        p.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
    print("wrote", path, flush=True)


def blob(r, soft=2.2):
    """Gaussian-ish radial falloff sprite, values 0..1, size (2r+1)^2."""
    y, x = np.mgrid[-r:r + 1, -r:r + 1].astype(np.float32)
    d = np.sqrt(x * x + y * y) / max(r, 1)
    return np.clip(np.exp(-(d * soft) ** 2) - math.exp(-soft ** 2), 0, None) / (1 - math.exp(-soft ** 2))


BLOBS = {}
SMOKE = {}


def fractal(n, octaves=5, seed=0):
    r = np.random.default_rng(seed)
    acc = np.zeros((n, n), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        g = max(2, n >> (o + 1) if o else 4) if False else 4 * 2 ** o
        small = Image.fromarray((r.random((g, g)) * 255).astype(np.uint8))
        acc += amp * np.asarray(small.resize((n, n), Image.BICUBIC), np.float32) / 255
        tot += amp; amp *= 0.55
    return acc / tot


def smoke_sprite(r, variant):
    r = int(max(4, r // 4 * 4))
    key = (r, variant)
    if key not in SMOKE:
        n = 2 * r + 1
        nz = fractal(n, 5, seed=variant * 1000 + r)
        sp = blob(r, soft=1.7) * np.clip((nz - 0.25) * 1.9, 0, 1.2)
        SMOKE[key] = np.clip(sp, 0, 1)
    return SMOKE[key]


def get_blob(r):
    r = int(max(2, r))
    if r not in BLOBS:
        BLOBS[r] = blob(r)
    return BLOBS[r]


def blit(canvas, x, y, sprite, color, alpha, mode="over"):
    r = sprite.shape[0] // 2
    x0, y0 = int(x) - r, int(y) - r
    x1, y1 = x0 + sprite.shape[1], y0 + sprite.shape[0]
    cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if cx0 >= cx1 or cy0 >= cy1:
        return
    s = sprite[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0, None] * alpha
    region = canvas[cy0:cy1, cx0:cx1]
    col = np.asarray(color, np.float32)
    if mode == "add":
        region += s * col
    else:
        region *= (1 - s)
        region += s * col


def fire_color(heat):
    """heat 1 -> white-yellow, 0 -> dark red."""
    stops = [(0.0, (60, 10, 0)), (0.35, (200, 50, 5)), (0.65, (255, 140, 30)), (0.85, (255, 220, 120)),
             (1.0, (255, 255, 230))]
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if heat <= b:
            k = (heat - a) / (b - a)
            return tuple(ca[i] + (cb[i] - ca[i]) * k for i in range(3))
    return stops[-1][1]


def shake(img, t, t0, dur, amp):
    if not (t0 <= t <= t0 + dur):
        return img
    k = (t0 + dur - t) / dur
    dx = int(amp * k * math.sin(t * 97)); dy = int(amp * 0.7 * k * math.cos(t * 83))
    return np.roll(np.roll(img, dy, axis=0), dx, axis=1)


def grade(img, t, grain=7.0):
    g = img * np.array([0.98, 1.0, 1.02], np.float32)
    lum = g.mean(axis=2, keepdims=True)
    g = lum + (g - lum) * 0.8                                     # desaturate a bit
    g += rng.normal(0, grain, (H // 4, W // 4, 1)).repeat(4, 0).repeat(4, 1).astype(np.float32)
    return g * VIGNETTE


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIGNETTE = (1 - 0.45 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 2)[..., None]


# ---------------------------------------------------------------- A-4 silhouette
# side view, x: 0 tail -> 1 nose, y up; units of aircraft length
A4_SIDE = [(0.0, 0.035), (0.30, -0.03), (0.75, -0.06), (0.90, -0.04), (1.0, 0.02), (0.92, 0.07),
           (0.82, 0.095), (0.77, 0.155), (0.70, 0.165), (0.62, 0.145), (0.55, 0.13), (0.40, 0.115),
           (0.22, 0.095), (0.13, 0.09), (0.05, 0.33), (-0.04, 0.33), (-0.01, 0.095), (-0.04, 0.07),
           (-0.035, 0.03)]
A4_WING = [(0.30, 0.02), (0.64, 0.03), (0.60, -0.01), (0.20, -0.06), (0.22, -0.02)]
A4_TANK = [(0.42, -0.06), (0.62, -0.06), (0.66, -0.075), (0.62, -0.09), (0.42, -0.09), (0.38, -0.075)]


def draw_a4_side(draw, x, y, length, facing=1, color=(26, 28, 31), alpha=255, bombs=True):
    def tr(pts):
        return [(x + facing * px * length - (length if facing < 0 else 0) * 0, y - py * length) for px, py in pts]
    c = color + (alpha,)
    draw.polygon(tr(A4_SIDE), fill=c)
    draw.polygon(tr(A4_WING), fill=c)
    if bombs:
        draw.polygon(tr(A4_TANK), fill=c)
    p = tr([(0.88, 0.05), (1.13, 0.055)])                          # refuelling probe
    draw.line(p, fill=c, width=max(2, int(length * 0.012)))
    cp = tr([(0.70, 0.13), (0.79, 0.11), (0.74, 0.135)])             # canopy glint
    draw.polygon(cp, fill=(120, 130, 140, alpha))


def draw_a4_front(draw, x, y, span, color=(30, 32, 36), alpha=255):
    """Head-on: thin wings, round fuselage, intakes, tall fin."""
    c = color + (alpha,)
    h = span * 0.5
    draw.polygon([(x - h, y + span * 0.02), (x + h, y + span * 0.02), (x + h, y + span * 0.045),
                  (x - h, y + span * 0.045)], fill=c)                    # wings
    r = span * 0.075
    draw.ellipse([x - r, y - r * 0.9, x + r, y + r], fill=c)              # fuselage
    for s in (-1, 1):
        draw.ellipse([x + s * r * 1.15 - r * 0.45, y - r * 0.2, x + s * r * 1.15 + r * 0.45, y + r * 0.6], fill=c)
        draw.polygon([(x + s * h * 0.35, y + span * 0.045), (x + s * h * 0.38, y + span * 0.12),
                      (x + s * h * 0.32, y + span * 0.12)], fill=c)       # pylons / tanks
    draw.polygon([(x - span * 0.018, y - r * 0.8), (x + span * 0.018, y - r * 0.8), (x, y - span * 0.17)], fill=c)
    draw.ellipse([x - r * 0.45, y - r * 1.25, x + r * 0.45, y - r * 0.55], fill=(90, 100, 110, alpha))


def layer_to_np(layer):
    a = np.asarray(layer, np.float32)
    return a[..., :3], a[..., 3:4] / 255.0


# ---------------------------------------------------------------- shot 1: approach over the sea
def make_sea():
    horizon = int(H * 0.42)
    sky = np.zeros((H, W, 3), np.float32)
    k = (yy / horizon)[..., None]
    sky[:] = (1 - k) * np.array([150, 156, 160]) + k * np.array([196, 198, 196])
    return horizon, sky


HORIZON, SKY = make_sea()
row = np.arange(H, dtype=np.float32)
depth = np.where(row > HORIZON, 260.0 / np.maximum(row - HORIZON, 1), 0)[:, None]


SEA_TEX = fractal(1024, 6, seed=3)
SEA_TEX = (SEA_TEX - SEA_TEX.mean()) / SEA_TEX.std()


def sea_frame(t, cam_y=0.0):
    img = SKY.copy()
    z = depth
    x = (xx - W / 2)
    def samp(uf, vf):
        ui = np.abs((uf % 2046) - 1023).astype(np.int32)      # mirrored tiling: no seams
        vi = np.abs((vf % 2046) - 1023).astype(np.int32)
        return SEA_TEX[vi, ui]
    big = samp(x * z * 2.2 + 400, z * 2600 - t * 700)
    mid = samp(x * z * 6.0 + 150, z * 7000 - t * 1500 + 300)
    fine = samp(x * z * 15.0, z * 17000 - t * 3000 + 700)
    wv = big * 0.6 + mid * 0.45 + fine * 0.25
    base = np.array([58, 68, 72], np.float32)
    fog = np.clip(z / 5.0, 0, 1)                          # far rows fade into haze
    sea = base + wv[..., None] * np.array([14, 16, 16])
    caps = np.clip((mid + fine * 0.8 - 2.3) * 1.4, 0, 1)[..., None] * 85 * (1 - fog[..., None])
    sea = sea + caps
    sea = sea * (1 - fog[..., None]) + np.array([176, 180, 180]) * fog[..., None]
    mask = (row > HORIZON)[:, None, None]
    img = np.where(mask, sea, img)
    return img


def shot_approach(path, dur=4.5):
    n = int(dur * FPS)
    sprays = []

    def frame(i, t):
        img = sea_frame(t)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for j, (ox, delay) in enumerate(((-0.08, 0.0), (0.10, 0.35))):
            k = max(0.0, min(1.0, (t - delay) / (dur - 0.3)))
            k = k ** 2.4                                       # accelerate toward camera
            span = 40 + 1150 * k
            x = W / 2 + ox * W * (0.4 + 1.6 * k) + 30 * math.sin(t * 1.7 + j)
            y = HORIZON + 6 + 260 * k ** 1.2
            if span > 2600:
                continue
            draw_a4_front(d, x, y, span, alpha=int(min(255, 120 + 600 * k)))
            if span > 120:
                for _ in range(3):
                    sprays.append([x + rng.normal(0, span * 0.15), y + span * 0.18, rng.uniform(0.6, 1.0) * span * 0.05,
                                   t, rng.normal(0, span * 0.004)])
        jets = np.asarray(layer.filter(ImageFilter.GaussianBlur(1.2)), np.float32)
        a = jets[..., 3:4] / 255.0
        img = img * (1 - a) + jets[..., :3] * a
        for s in sprays:
            age = t - s[3]
            if age > 1.2:
                continue
            blit(img, s[0] + s[4] * age * FPS, s[1] - age * 30, get_blob(s[2] * (1 + age * 1.5)),
                 (215, 220, 222), 0.35 * (1 - age / 1.2))
        img = shake(img, t, 0, dur, 5 + 25 * (t / dur) ** 3)
        return grade(img, t)

    encode(path, frame, n)


# ---------------------------------------------------------------- shot 2: attack run over the ship
def shot_attack(bg_path, path, dur=5.0):
    bg = np.asarray(Image.open(bg_path).convert("RGB"), np.float32)
    n = int(dur * FPS)
    guns = [(1355, 600), (1060, 560), (560, 600)]    # 4.5in gun / Sea Dart area / aft deck (approx.)
    tracers, bombs, smoke = [], [], []
    planes = [dict(t0=0.6, y=330, len=290), dict(t0=1.35, y=270, len=260)]
    for p in planes:
        p["drop"] = p["t0"] + 1.15

    def plane_pos(p, t):
        k = (t - p["t0"]) / 2.4
        return -500 + k * (W + 1000), p["y"] + 60 * k

    def frame(i, t):
        z = 1.0 + 0.04 * t / dur
        img = np.asarray(Image.fromarray(bg.astype(np.uint8)).resize((int(W * z), int(H * z)), Image.BILINEAR)
                         .crop((int((W * z - W) / 2), int((H * z - H) / 2), int((W * z - W) / 2) + W,
                                int((H * z - H) / 2) + H)), np.float32).copy()
        # tracer fire from the ship toward the jets
        if 0.4 < t < dur - 0.6 and i % 2 == 0:
            for gx, gy in guns[:2]:
                tgt = plane_pos(planes[0], t + 0.4)
                ang = math.atan2(tgt[1] - gy, tgt[0] - gx) + rng.normal(0, 0.08)
                tracers.append([gx, gy, math.cos(ang) * 95, math.sin(ang) * 95, t])
        glow = np.zeros_like(img)
        for tr in tracers:
            age = t - tr[4]
            if age < 0 or age > 0.9:
                continue
            x, y = tr[0] + tr[2] * age * FPS, tr[1] + tr[3] * age * FPS + 400 * age * age
            for s in range(6):
                blit(glow, x - tr[2] * s * 0.08, y - tr[3] * s * 0.08, get_blob(5), (255, 190, 90), 0.5 * (1 - s / 6), "add")
        # jets + bombs
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for p in planes:
            if t < p["t0"]:
                continue
            x, y = plane_pos(p, t)
            for mb in range(3, -1, -1):                      # motion blur trail, main body last
                draw_a4_side(d, x - mb * 9, y - mb * 0.3, p["len"], alpha=255 if mb == 0 else 30,
                             bombs=t < p["drop"])
            blit(glow, x - 0.02 * p["len"], y - 0.05 * p["len"], get_blob(14), (255, 150, 60), 0.6, "add")
            if abs(t - p["drop"]) < 0.5 / FPS * 2 and not any(b[5] is p for b in bombs):
                bombs.append([x + 0.5 * p["len"], y + 0.09 * p["len"], (W + 1000) / 2.4 / FPS, 0.0, t, p])
        for b in bombs:
            age = t - b[4]
            bx = b[0] + b[2] * age * FPS * 0.85
            by = b[1] + 0.5 * 2200 * age * age
            if by > 560:
                continue
            ang = math.degrees(math.atan2(2200 * age, b[2] * FPS * 0.85))
            bl = Image.new("RGBA", (90, 30), (0, 0, 0, 0))
            ImageDraw.Draw(bl).ellipse([5, 8, 85, 22], fill=(25, 25, 25, 255))
            bl = bl.rotate(-ang, expand=True)
            layer.alpha_composite(bl, (int(bx - bl.width / 2), int(by - bl.height / 2)))
        rgb, a = layer_to_np(layer.filter(ImageFilter.GaussianBlur(0.8)))
        img = img * (1 - a) + rgb * a
        glow_img = Image.fromarray(np.clip(glow, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))
        img += np.asarray(glow_img, np.float32) * 1.6 + glow
        # gun smoke puffs
        if 0.4 < t < dur - 0.6 and i % 3 == 0:
            for gx, gy in guns[:2]:
                smoke.append([gx + rng.normal(0, 6), gy, rng.uniform(10, 18), t])
        for s in smoke:
            age = t - s[3]
            if age > 2:
                continue
            blit(img, s[0] - 25 * age, s[1] - 18 * age, smoke_sprite(s[2] * (1 + age * 2), int(s[2]) % 5), (205, 205, 200), 0.35 * (1 - age / 2))
        img = shake(img, t, 0.5, dur, 4)
        return grade(img, t)

    encode(path, frame, n)


# ---------------------------------------------------------------- shot 3: bomb impacts
def shot_impact(bg_path, path, dur=6.5):
    bg = np.asarray(Image.open(bg_path).convert("RGB"), np.float32)
    n = int(dur * FPS)
    hits = [(0.6, 1080, 470), (1.15, 760, 455), (1.75, 1300, 480)]      # (time, x, y) on hull/superstructure
    fire, smoke, debris = [], [], []
    spawned = set()

    def frame(i, t):
        z = 1.06 + 0.06 * t / dur
        sw, sh = int(W * z), int(H * z)
        img = np.asarray(Image.fromarray(bg.astype(np.uint8)).resize((sw, sh), Image.BILINEAR)
                         .crop(((sw - W) // 2, (sh - H) // 2, (sw - W) // 2 + W, (sh - H) // 2 + H)), np.float32).copy()
        to_screen = lambda x, y: (W / 2 + (x - W / 2) * z, H / 2 + (y - H / 2) * z)
        flash = 0.0
        for k, (ht, hx, hy) in enumerate(hits):
            sx, sy = to_screen(hx, hy)
            if t >= ht and k not in spawned:
                spawned.add(k)
                for _ in range(70):
                    a = rng.uniform(math.pi * 1.05, math.pi * 1.95)
                    v = rng.uniform(2, 13)
                    fire.append([sx, sy, math.cos(a) * v, math.sin(a) * v * 1.2, rng.uniform(18, 46), t, rng.uniform(0.7, 1.5)])
                for _ in range(45):
                    a = rng.uniform(math.pi * 1.1, math.pi * 1.9)
                    v = rng.uniform(10, 28)
                    debris.append([sx, sy, math.cos(a) * v, math.sin(a) * v, t])
                for _ in range(6):
                    smoke.append([sx + rng.normal(0, 30), sy - 20, rng.uniform(40, 70), t + rng.uniform(0.2, 0.8), k])
            if ht <= t < ht + 0.25:
                flash = max(flash, 1 - (t - ht) / 0.25)
        # continuous smoke columns from each hit
        for k, (ht, hx, hy) in enumerate(hits):
            if t > ht + 0.4 and i % 2 == 0:
                sx, sy = to_screen(hx, hy)
                smoke.append([sx + rng.normal(0, 18), sy - 25, rng.uniform(22, 42), t, k])
        # smoke (behind fire)
        for s in smoke:
            age = t - s[3]
            if age < 0 or age > 4.5:
                continue
            x = s[0] - 40 * age - 10 * age * age
            y = s[1] - 85 * age
            r = s[2] * (1 + age * 1.1)
            dark = 28 + 45 * min(1, age / 3)
            blit(img, x, y, smoke_sprite(r, int(s[2]) % 5), (dark, dark - 2, dark - 4),
                 0.75 * min(1, age * 3) * (1 - age / 4.5))
        # fireballs
        glow = np.zeros_like(img)
        for f in fire:
            age = t - f[5]
            life = f[6]
            if age < 0 or age > life:
                continue
            k = age / life
            x = f[0] + f[2] * age * FPS * (1 - 0.5 * k)
            y = f[1] + f[3] * age * FPS * (1 - 0.6 * k) - 40 * age
            r = f[4] * (0.6 + 1.6 * k)
            heat = max(0.0, 1 - k * 1.3)
            if heat > 0:
                blit(glow, x, y, get_blob(r), fire_color(heat), 0.9 * (1 - k), "add")
            blit(img, x, y - r * 0.3, get_blob(r * 1.2), (40, 34, 30), 0.35 * k)
        img += glow
        img += np.asarray(Image.fromarray(np.clip(glow, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(25)),
                          np.float32) * 0.9
        # debris streaks
        for dbr in debris:
            age = t - dbr[4]
            if age < 0 or age > 1.4:
                continue
            x = dbr[0] + dbr[2] * age * FPS * 0.6
            y = dbr[1] + dbr[3] * age * FPS * 0.6 + 900 * age * age
            hot = age < 0.5
            blit(img if not hot else glow, x, y, get_blob(3), (255, 200, 120) if hot else (25, 25, 25), 0.9, "add" if hot else "over")
        if flash:
            img = img * (1 - 0.75 * flash) + np.array([255, 245, 225], np.float32) * 0.75 * flash
        # warm firelight wash on the scene after the hits
        if t > hits[0][0]:
            img = img * (1 + np.array([0.10, 0.03, -0.04], np.float32) * min(1, (t - hits[0][0]) / 0.5))
        for ht, _, _ in hits:
            img = shake(img, t, ht, 0.9, 26)
        return grade(img, t)

    encode(path, frame, n)


if __name__ == "__main__":
    bg1, bg2, out = sys.argv[1:4]
    want = set(sys.argv[4:]) or {"approach", "attack", "impact"}
    os.makedirs(out, exist_ok=True)
    if "approach" in want:
        shot_approach(os.path.join(out, "approach.mp4"))
    if "attack" in want:
        shot_attack(bg1, os.path.join(out, "attack.mp4"))
    if "impact" in want:
        shot_impact(bg2, os.path.join(out, "impact.mp4"))
