"""More procedural combat shots for the 10-minute HMS Coventry film.

render(kind, params, dur, out_path)  — kinds: pov, radar, fleet, seadart, raid, bounce, aftermath,
                                         sink, rescue, calm, approach, attack, impact
Backgrounds: bg_ship1.jpg / bg_ship2.jpg (cover-cropped Commons photos) in BG_DIR.
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vfx as V                                       # helpers: encode, blob, blit, fire_color, shake, grade, sea_frame ...
from vfx import W, H, FPS, encode, blit, get_blob, fire_color, shake, grade, smoke_sprite, layer_to_np

BG_DIR = os.environ.get("BG_DIR", HERE)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
yy, xx = V.yy, V.xx


def load_bg(name):
    return np.asarray(Image.open(os.path.join(BG_DIR, name)).convert("RGB"), np.float32)


def zoom_crop(img, z, cx=W / 2, cy=H / 2):
    sw, sh = int(W * z), int(H * z)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((sw, sh), Image.BILINEAR)
    x0 = int(cx * z - W / 2); y0 = int(cy * z - H / 2)
    x0 = min(max(0, x0), sw - W); y0 = min(max(0, y0), sh - H)
    return np.asarray(im.crop((x0, y0, x0 + W, y0 + H)), np.float32).copy()


def composite(img, layer, blur=0.8):
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    rgb, a = layer_to_np(layer)
    return img * (1 - a) + rgb * a


def add_glow(img, glow, radius=18, k=0.9):
    g = Image.fromarray(np.clip(glow, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius))
    return img + glow + np.asarray(g, np.float32) * k


# ------------------------------------------------------------------ ship silhouettes (bow to the right)
SHIPS = {
    "t42": dict(hull=[(0, 0), (1.0, 0), (1.02, 0.05), (0.80, 0.042), (0.0, 0.038)],
                blocks=[(0.17, 0.038, 0.32, 0.075), (0.32, 0.038, 0.63, 0.088), (0.55, 0.088, 0.63, 0.105),
                        (0.40, 0.088, 0.47, 0.125), (0.76, 0.042, 0.80, 0.058), (0.85, 0.045, 0.89, 0.062)],
                masts=[(0.36, 0.088, 0.19), (0.58, 0.105, 0.17)], domes=[(0.25, 0.088, 0.022), (0.68, 0.06, 0.02)]),
    "t22": dict(hull=[(0, 0), (1.0, 0), (1.02, 0.055), (0.0, 0.05)],
                blocks=[(0.06, 0.05, 0.30, 0.092), (0.30, 0.05, 0.70, 0.10), (0.62, 0.10, 0.70, 0.12),
                        (0.45, 0.10, 0.52, 0.135), (0.80, 0.055, 0.85, 0.072), (0.12, 0.092, 0.16, 0.105)],
                masts=[(0.40, 0.10, 0.20), (0.60, 0.12, 0.21)], domes=[]),
    "t21": dict(hull=[(0, 0), (1.0, 0), (1.02, 0.05), (0.0, 0.045)],
                blocks=[(0.12, 0.045, 0.30, 0.08), (0.30, 0.045, 0.66, 0.10), (0.56, 0.10, 0.64, 0.12),
                        (0.40, 0.10, 0.48, 0.13), (0.82, 0.05, 0.86, 0.066)],
                masts=[(0.52, 0.12, 0.20)], domes=[]),
    "carrier": dict(hull=[(0, 0), (1.0, 0), (1.03, 0.095), (0.92, 0.082), (0.0, 0.075)],
                    blocks=[(0.55, 0.075, 0.70, 0.15), (0.60, 0.15, 0.66, 0.17)],
                    masts=[(0.63, 0.17, 0.22)], domes=[]),
    "container": dict(hull=[(0, 0), (1.0, 0), (1.02, 0.08), (0.0, 0.075)],
                      blocks=[(0.22, 0.075, 0.88, 0.125), (0.04, 0.075, 0.20, 0.17), (0.09, 0.17, 0.14, 0.205)],
                      masts=[(0.92, 0.08, 0.15)], domes=[]),
    "lsl": dict(hull=[(0, 0), (1.0, 0), (1.01, 0.08), (0.0, 0.075)],
                blocks=[(0.05, 0.075, 0.35, 0.15), (0.10, 0.15, 0.25, 0.18)],
                masts=[(0.20, 0.18, 0.24)], domes=[]),
}


def draw_ship(draw, kind, x0, yw, length, color=None, alpha=255, haze=0.0):
    """Royal Navy light-grey ship with dark boot-topping, shading, windows, reflection and bow wave.
    haze 0 = close, 1 = lost in mist."""
    s = SHIPS[kind]
    tr = lambda px, py: (x0 + px * length, yw - py * length)
    hz = lambda c: haze_color(c, haze * 0.85)
    hull_c, hull_dark, sup_c, sup_hi = hz((150, 156, 160)), hz((108, 114, 118)), hz((182, 186, 188)), hz((214, 216, 216))
    boot, dark = hz((26, 26, 28)), hz((40, 42, 46))
    A = (alpha,)
    # reflection / shadow on the water
    draw.polygon([tr(0.0, 0.0), tr(1.0, 0.0), tr(0.97, -0.03), tr(0.03, -0.03)], fill=hz((24, 30, 34)) + (int(alpha * 0.55),))
    hull = [tr(*p) for p in s["hull"]]
    draw.polygon(hull, fill=hull_c + A)
    deck_y = s["hull"][-1][1]
    draw.polygon([tr(0, deck_y * 0.45), tr(1.0, deck_y * 0.45), tr(1.0, 0), tr(0, 0)], fill=hull_dark + A)   # lower hull shade
    draw.polygon([tr(0, 0.0), tr(1.0, 0.0), tr(1.0, 0.008), tr(0, 0.008)], fill=boot + A)                    # boot-topping
    draw.line([tr(0.0, deck_y), tr(0.98, s["hull"][2][1] * 0.95)], fill=sup_hi + A, width=max(1, int(length * 0.003)))
    for (a_, b_, c_, d_) in s["blocks"]:
        draw.rectangle([tr(a_, d_), tr(c_, b_)], fill=sup_c + A)
        draw.rectangle([tr(a_, d_), tr(c_, d_ - 0.006)], fill=sup_hi + A)                                   # lit top edge
        if (c_ - a_) > 0.08 and (d_ - b_) > 0.03:                                                          # windows / ports
            wy = b_ + (d_ - b_) * 0.6
            for wx in np.arange(a_ + 0.02, c_ - 0.01, 0.025):
                draw.rectangle([tr(wx, wy + 0.004), tr(wx + 0.01, wy)], fill=dark + A)
    for (mx, base, top) in s["masts"]:
        w = max(1, length * 0.004)
        draw.polygon([tr(mx - 0.005, base), tr(mx + 0.005, base), tr(mx + 0.002, top), tr(mx - 0.002, top)], fill=dark + A)
        draw.line([tr(mx - 0.02, top - 0.02), tr(mx + 0.02, top - 0.02)], fill=dark + A, width=int(w))
    for (dx, base, r) in s["domes"]:
        cx, cy = tr(dx, base + r * 0.6)
        draw.ellipse([cx - r * length, cy - r * length, cx + r * length, cy + r * length], fill=hz((228, 230, 230)) + A)
    bx, by = tr(1.0, 0.0)                                                                                   # bow wave
    draw.ellipse([bx - length * 0.06, by - length * 0.006, bx + length * 0.015, by + length * 0.008],
                 fill=hz((225, 228, 228)) + (int(alpha * 0.8),))
    return tr


def haze_color(base, dist, fog=(176, 180, 180)):
    k = min(1.0, max(0.0, dist))
    return tuple(int(base[i] * (1 - k) + fog[i] * k) for i in range(3))


# ------------------------------------------------------------------ smoke / fire emitters
class Emitter:
    def __init__(self, rate, life, size, color, alpha, vel, spread, grow=1.2, kind="smoke", seed=0):
        self.p = []; self.rate, self.life, self.size = rate, life, size
        self.color, self.alpha, self.vel, self.spread, self.grow, self.kind = color, alpha, vel, spread, grow, kind
        self.acc = 0.0; self.rng = np.random.default_rng(seed)

    def step(self, x, y, t, dt=1 / FPS, on=True):
        if on:
            self.acc += self.rate * dt
            while self.acc >= 1:
                self.acc -= 1
                self.p.append([x + self.rng.normal(0, self.spread), y + self.rng.normal(0, self.spread * 0.4),
                               t, self.rng.uniform(0.7, 1.3) * self.size, self.rng.integers(0, 5),
                               self.vel[0] * self.rng.uniform(0.7, 1.3), self.vel[1] * self.rng.uniform(0.7, 1.3)])
        self.p = [q for q in self.p if t - q[2] < self.life]

    def draw(self, img, glow, t):
        for q in self.p:
            age = t - q[2]; k = age / self.life
            x = q[0] + q[5] * age; y = q[1] + q[6] * age
            r = q[3] * (1 + self.grow * k * 2)
            if self.kind == "fire":
                heat = max(0.0, 1 - k * 1.4)
                if heat > 0:
                    blit(glow, x, y, get_blob(r), fire_color(heat), 0.8 * (1 - k), "add")
            else:
                col = tuple(c + 20 * k for c in self.color)
                blit(img, x, y, smoke_sprite(r, int(q[4])), col, self.alpha * min(1, age * 4) * (1 - k))


# ------------------------------------------------------------------ RADAR / OPS ROOM
def radar(path, dur, mode="alarm", seed=0):
    rng = np.random.default_rng(seed + 5)
    n = int(dur * FPS)
    cx, cy, R = 980, 520, 400
    ys, xs = np.mgrid[cy - R:cy + R, cx - R:cx + R].astype(np.float32)
    dx, dy = xs - cx, ys - cy
    rad = np.sqrt(dx * dx + dy * dy) / R
    ang = (np.degrees(np.arctan2(dx, -dy)) + 360) % 360          # bearing, 0 = up
    inside = rad <= 1
    # land clutter: noisy blobs in the south-east quadrant (the islands) + west coast edge
    nz = V.fractal(2 * R, 5, seed=11)
    land = ((nz > 0.58) & (rad > 0.25) & (ang > 110) & (ang < 230)).astype(np.float32)
    land += ((nz > 0.55) & (rad > 0.85) & (ang > 230) & (ang < 300)).astype(np.float32) * 0.7
    persist = np.zeros_like(rad)
    # contacts: (start bearing, start range, end range)
    contacts = [(252, 0.95, 0.18), (247, 1.0, 0.24)] if mode != "calm" else [(30, 0.8, 0.75), (300, 0.9, 0.85)]
    if mode == "clutter":
        contacts = [(205, 0.75, 0.32), (210, 0.8, 0.36)]                    # contacts over land clutter
    if seed == 3:
        contacts = [(262, 0.9, 0.3), (258, 0.95, 0.34)]
    period = 2.6
    base = np.zeros((H, W, 3), np.float32) + np.array([10, 16, 18], np.float32)
    # console bezel and panels
    pan = Image.new("RGB", (W, H), (12, 18, 20))
    d = ImageDraw.Draw(pan)
    d.rectangle([0, 0, 470, H], fill=(18, 24, 26)); d.rectangle([1490, 0, W, H], fill=(18, 24, 26))
    for i in range(6):
        d.rectangle([60, 120 + i * 140, 410, 220 + i * 140], outline=(40, 60, 55), width=3)
        d.rectangle([1550, 120 + i * 140, 1860, 220 + i * 140], outline=(40, 60, 55), width=3)
    d.ellipse([cx - R - 30, cy - R - 30, cx + R + 30, cy + R + 30], fill=(25, 30, 30))
    base = np.asarray(pan, np.float32)
    fnt = ImageFont.truetype(FONT, 26); fnt_big = ImageFont.truetype(FONT, 46)

    def frame(i, t):
        nonlocal persist
        sweep = (t / period * 360) % 360
        diff = (sweep - ang) % 360
        wedge = (diff < 6).astype(np.float32)
        echo = land.copy() * (0.6 if mode != "dark" else 0.25)
        k = t / dur
        for b, r0, r1 in contacts:
            rr = r0 + (r1 - r0) * k
            ex = math.sin(math.radians(b)) * rr * R; ey = -math.cos(math.radians(b)) * rr * R
            echo += np.exp(-(((dx - ex) ** 2 + (dy - ey) ** 2) / (2 * 6.0 ** 2))) * 1.4
        echo += np.exp(-((dx ** 2 + dy ** 2) / (2 * 5.0 ** 2))) * 1.2         # own ship
        echo += np.exp(-(((dx - 30) ** 2 + (dy + 18) ** 2) / (2 * 5.0 ** 2))) * 1.0   # Broadsword close by
        if mode == "clutter":
            echo += (rng.random(echo.shape) > 0.985) * (rad < 0.6) * 0.8
        persist = persist * 0.965 + wedge * echo
        img = base.copy()
        g = np.clip(persist, 0, 1.2)
        scope = np.zeros((2 * R, 2 * R, 3), np.float32)
        scope[..., 0] = g * 60; scope[..., 1] = g * 255; scope[..., 2] = g * 120
        scope += (np.maximum(0, 1 - diff / 40) * 40)[..., None] * np.array([0.2, 1, 0.5]) * inside[..., None]
        rings = ((np.abs((rad * 4) % 1) < 0.012) | (np.abs(dx) < 1) | (np.abs(dy) < 1)) & inside
        scope += rings[..., None] * np.array([10, 45, 25], np.float32)
        scope *= inside[..., None]
        scope += (~inside)[..., None] * img[cy - R:cy + R, cx - R:cx + R]
        img[cy - R:cy + R, cx - R:cx + R] = scope
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
        txtc = (110, 255, 150, 230)
        dd.text((70, 60), "HMS COVENTRY  ·  OPS ROOM", font=fnt, fill=txtc)
        if mode in ("alarm", "clutter"):
            b, r0, r1 = contacts[0]
            rng_nm = 20 * (r0 + (r1 - r0) * t / dur)
            dd.text((1530, 60), f"BRG {b:03d}", font=fnt, fill=txtc)
            dd.text((1530, 100), f"RNG {rng_nm:4.1f} NM", font=fnt, fill=txtc)
            dd.text((1530, 140), "ALT  VERY LOW", font=fnt, fill=txtc)
        if mode == "clutter":
            blink = int(t * 3) % 2 == 0
            dd.text((1530, 200), "SEA DART:", font=fnt, fill=txtc)
            if blink:
                dd.text((1530, 240), "NO LOCK", font=fnt_big, fill=(255, 80, 60, 255))
        if mode == "alarm" and int(t * 2) % 2 == 0:
            dd.text((70, 980), "AIR RAID WARNING RED", font=fnt_big, fill=(255, 70, 50, 255))
        img = composite(img, lay, blur=0.6)
        # operator silhouettes (anti-flash hoods) in the foreground
        sil = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sil)
        for (hx, hy, s) in ((300, 1010, 1.0), (1650, 1030, 1.15)):
            ds.ellipse([hx - 110 * s, hy - 150 * s, hx + 110 * s, hy + 90 * s], fill=(8, 10, 11, 255))
            ds.rectangle([hx - 230 * s, hy + 40 * s, hx + 230 * s, H], fill=(8, 10, 11, 255))
        img = composite(img, sil, blur=4)
        # lighting
        if mode == "alarm":
            pulse = 0.5 + 0.5 * math.sin(t * math.pi * 2 / 1.2)
            img = img * (1 + np.array([0.55, -0.15, -0.2], np.float32) * pulse)
        elif mode == "dark":
            flick = 0.35 + 0.65 * (rng.random() > 0.12)
            img = img * flick * np.array([1.3, 0.75, 0.7], np.float32)
            haze = V.fractal(256, 4, seed=int(t * 2) % 7)
            hz = np.asarray(Image.fromarray((haze * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR),
                            np.float32)[..., None] / 255
            img = img * (1 - 0.45 * hz) + 50 * hz
        img = shake(img, t, 0, dur, 2.5 if mode != "calm" else 0.8)
        return grade(img, t, grain=6)

    encode(path, frame, n)


# ------------------------------------------------------------------ PILOT POV
def pov(path, dur, seed=0, ships=False):
    rng = np.random.default_rng(seed)
    n = int(dur * FPS)
    hills = V.fractal(512, 4, seed=seed + 40)[256]
    fnt = ImageFont.truetype(FONT, 22)

    def frame(i, t):
        img = V.sea_frame(t * 2.6)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        hz = V.HORIZON
        if not ships:                                         # distant coastline appears
            a = min(1, t / dur * 1.3)
            pts = [(x, hz + 2 - (hills[int(x / W * 511)] - 0.4) * 60 * a) for x in range(0, W + 1, 16)]
            d.polygon([(0, hz + 3)] + pts + [(W, hz + 3)], fill=(150, 156, 152, int(160 * a)))
        else:
            k = (t / dur) ** 1.6
            for kind, xo, base in (("t42", -180, 150), ("t22", 220, 170)):
                L = base * (1 + 3.2 * k)
                x0 = W / 2 + xo * (1 + 2.2 * k) - L / 2
                draw_ship(d, kind, x0, hz + 4 + 40 * k, L, haze=0.55 - 0.4 * k)
            if t > dur * 0.4:                                # flak bursts
                for _ in range(2):
                    bx = W / 2 + rng.normal(0, 260); by = hz - rng.uniform(20, 160)
                    r = rng.uniform(6, 14)
                    d.ellipse([bx - r, by - r, bx + r, by + r], fill=(40, 40, 40, 160))
        img = composite(img, lay, blur=1.2)
        # bank + vibration
        bank = 4 * math.sin(t * 0.6 + seed) + rng.normal(0, 0.25)
        im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).rotate(bank, resample=Image.BILINEAR,
                                                                          expand=False, center=(W / 2, H / 2))
        im = im.resize((int(W * 1.12), int(H * 1.12)), Image.BILINEAR)
        ox = int(W * 0.06 + rng.normal(0, 3)); oy = int(H * 0.06 + rng.normal(0, 3))
        img = np.asarray(im.crop((ox, oy, ox + W, oy + H)), np.float32).copy()
        # cockpit frame + gunsight
        ck = Image.new("RGBA", (W, H), (0, 0, 0, 0)); c = ImageDraw.Draw(ck)
        c.polygon([(0, 0), (W, 0), (W, 140), (W * 0.78, 60), (W * 0.22, 60), (0, 140)], fill=(14, 15, 16, 255))
        c.polygon([(0, 140), (W * 0.22, 60), (W * 0.26, 60), (90, H), (0, H)], fill=(14, 15, 16, 255))
        c.polygon([(W, 140), (W * 0.78, 60), (W * 0.74, 60), (W - 90, H), (W, H)], fill=(14, 15, 16, 255))
        c.rectangle([0, H - 170, W, H], fill=(18, 19, 20, 255))
        c.rectangle([W / 2 - 230, H - 230, W / 2 + 230, H - 170], fill=(24, 25, 26, 255))
        sx, sy = W / 2, H * 0.47
        for rr in (110, 4):
            c.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], outline=(255, 170, 60, 200), width=3)
        for a in range(0, 360, 30):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            c.line([(sx + ca * 100, sy + sa * 100), (sx + ca * 118, sy + sa * 118)], fill=(255, 170, 60, 200), width=3)
        c.text((W / 2 - 200, H - 215), f"ALT  {int(30 + 10 * math.sin(t * 2))} m    SPD 480 kt", font=fnt,
               fill=(255, 180, 80, 220))
        img = composite(img, ck, blur=1.0)
        return grade(img, t)

    encode(path, frame, n)


# ------------------------------------------------------------------ FLEET at sea (optionally burning ship)
def fleet(path, dur, seed=0, burning=False, pair=False, big=False):
    rng = np.random.default_rng(seed)
    n = int(dur * FPS)
    hz = V.HORIZON
    if pair:
        ships = [("t42", 360, 0.25, 0.0), ("t22", 1060, 0.3, 0.0)]
    elif burning:
        ships = [("container" if big else "t42", 640, 0.0, 0.0), ("t21", 1450, 0.6, 0.0)]
    else:
        ships = [("carrier", 520, 0.25, 0.0), ("t42", 120, 0.55, 0.0), ("t22", 1300, 0.4, 0.0),
                 ("lsl", 1620, 0.7, 0.0), ("t21", 950, 0.75, 0.0)]
    smoke = Emitter(14, 7, 34, (36, 34, 32), 0.75, (-22, -55), 18, grow=1.6, seed=seed)
    fire = Emitter(30, 0.8, 26, (0, 0, 0), 1, (0, -40), 22, kind="fire", seed=seed + 1)

    def frame(i, t):
        img = V.sea_frame(t * 0.6)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        burn_pt = None
        for j, (kind, x, dist, _) in enumerate(ships):
            L = (700 if burning and j == 0 else 520) * (1 - dist * 0.7)
            yw = hz + 8 + (1 - dist) * 70 + math.sin(t * 0.9 + j) * 2
            xs = x + 14 * t * (1 - dist) - L / 2
            col = haze_color((66, 72, 76), dist * 0.8)
            tr = draw_ship(d, kind, xs, yw, L, haze=dist * 0.8)
            if burning and j == 0:
                burn_pt = tr(0.45, 0.06)
                d.polygon([tr(0.3, 0.0), tr(0.6, 0.0), tr(0.6, 0.012), tr(0.3, 0.012)], fill=(30, 30, 30, 255))
        img = composite(img, lay, blur=1.0)
        glow = np.zeros_like(img)
        if burn_pt:
            smoke.step(burn_pt[0], burn_pt[1] - 10, t)
            fire.step(burn_pt[0], burn_pt[1], t)
            smoke.draw(img, glow, t)
            fire.draw(img, glow, t)
        img = add_glow(img, glow, 20, 0.8)
        return grade(img, t)

    encode(path, frame, n)


# ------------------------------------------------------------------ SEA DART launch from the real ship photo
def seadart(path, dur):
    bg = load_bg("bg_ship1.jpg")
    n = int(dur * FPS)
    launches = [1.2, 5.2]
    trail = Emitter(0, 4.5, 16, (215, 215, 210), 0.55, (-12, -8), 4, grow=1.4, seed=3)
    blast = Emitter(0, 2.5, 40, (200, 200, 195), 0.5, (-30, -10), 25, grow=1.2, seed=4)

    def mpos(age):
        return 1270 + 420 * age ** 1.6 * 1.2, 612 - 260 * age - 520 * age ** 1.8

    def frame(i, t):
        img = zoom_crop(bg, 1.05 + 0.03 * t / dur)
        glow = np.zeros_like(img)
        for L in launches:
            age = t - L
            if age < 0:
                continue
            if age < 0.25:
                blast.rate = 120
                blast.step(1270, 612, t)
            else:
                blast.rate = 0
                blast.step(1270, 612, t, on=False)
            if age < 3.0:
                x, y = mpos(age)
                trail.rate = 90
                trail.step(x, y, t)
                blit(glow, x, y, get_blob(16), (255, 230, 170), 1.0, "add")
                blit(glow, x, y, get_blob(40), (255, 150, 60), 0.5, "add")
            else:
                trail.step(0, 0, t, on=False)
        trail.draw(img, glow, t); blast.draw(img, glow, t)
        img = add_glow(img, glow, 16, 1.0)
        for L in launches:
            if L <= t < L + 0.15:
                img = img * 0.6 + 255 * 0.4
        for L in launches:
            img = shake(img, t, L, 0.6, 6)
        return grade(img, t)

    encode(path, frame, n)


# ------------------------------------------------------------------ San Carlos raid (hills, anchored ships, jets)
def raid(path, dur, seed=0, hit=False, shootdown=False):
    rng = np.random.default_rng(seed)
    n = int(dur * FPS)
    hz = int(H * 0.50)
    sky = np.zeros((H, W, 3), np.float32)
    kk = (yy / hz)[..., None]
    sky[:] = (1 - kk) * np.array([140, 146, 150]) + kk * np.array([186, 188, 186])
    r1 = V.fractal(1024, 5, seed=seed)[300]; r2 = V.fractal(1024, 5, seed=seed + 9)[500]
    ridge_far = hz - 120 - (r1[(np.arange(W) * 1023 // W)] - 0.5) * 220
    ridge_near = hz - 40 - (r2[(np.arange(W) * 1023 // W)] - 0.5) * 160
    land = sky.copy()
    m1 = yy > ridge_far[None, :]
    land[m1] = np.array([118, 122, 112], np.float32)
    m2 = yy > ridge_near[None, :]
    land[m2] = np.array([88, 92, 76], np.float32)
    tex = V.fractal(512, 5, seed=seed + 3)
    tex = np.asarray(Image.fromarray((tex * 255).astype(np.uint8)).resize((W, H)), np.float32)[..., None] / 255
    land = land * (0.85 + 0.3 * tex) * (m1[..., None] | ~m1[..., None])
    ships = [("t21", 300, hz + 140, 520), ("lsl", 980, hz + 70, 420), ("t22", 1400, hz + 200, 600)]
    target = ships[0] if hit else None
    jets = [dict(t0=0.6, y0=ridge_near[200] - 60, y1=hz + 20, len=170, dir=1),
            dict(t0=1.1, y0=ridge_near[300] - 40, y1=hz + 50, len=190, dir=1)]
    splashes = [(2.2 + 0.3 * j, s[1] + s[3] * rng.uniform(0.2, 0.9), s[2]) for j, s in enumerate(ships[1:])]
    fire = Emitter(32, 0.8, 24, (0, 0, 0), 1, (0, -45), 18, kind="fire", seed=seed)
    smoke = Emitter(16, 6, 30, (40, 38, 36), 0.75, (-20, -50), 16, grow=1.5, seed=seed + 1)
    tracers = []
    water_parts = []

    def jet_xy(j, t):
        k = (t - j["t0"]) / 2.6
        x = -300 + k * (W + 600)
        y = j["y0"] + (j["y1"] - j["y0"]) * min(1, k * 2.2)
        return x, y

    def frame(i, t):
        img = V.sea_frame(t * 0.4) * 0.92
        img = np.where((yy < hz)[..., None], land, img)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        tgt_pt = None
        for kind, x, yw, L in ships:
            tr = draw_ship(d, kind, x, yw + math.sin(t + x) * 1.5, L, haze=0.12)
            if target and kind == target[0]:
                tgt_pt = tr(0.5, 0.07)
        down = None
        for jn, j in enumerate(jets):
            if t < j["t0"]:
                continue
            x, y = jet_xy(j, t)
            if shootdown and jn == 1 and t > j["t0"] + 1.3:
                tt = t - (j["t0"] + 1.3)
                x0, y0 = jet_xy(j, j["t0"] + 1.3)
                x, y = x0 + 420 * tt, y0 + 180 * tt * tt + 60 * tt
                down = (x, y, tt)
                if y > hz + 260:
                    continue
            for mb in range(3, -1, -1):
                V.draw_a4_side(d, x - mb * 8, y, j["len"], alpha=255 if mb == 0 else 30, bombs=t < j["t0"] + 1.4)
        img = composite(img, lay, blur=0.9)
        glow = np.zeros_like(img)
        # tracers from the ships
        if i % 2 == 0 and t > 0.4:
            for kind, x, yw, L in ships:
                gx, gy = x + L * 0.85, yw - L * 0.07
                tracers.append([gx, gy, rng.uniform(-60, 20), rng.uniform(-90, -60), t])
        for tr_ in tracers:
            age = t - tr_[4]
            if 0 <= age < 0.8:
                for s in range(5):
                    blit(glow, tr_[0] + tr_[2] * (age - s * 0.01) * FPS, tr_[1] + tr_[3] * (age - s * 0.01) * FPS,
                         get_blob(4), (255, 190, 90), 0.5, "add")
        # near-miss water columns
        for (st, sx, sy) in splashes:
            if abs(t - st) < 0.5 / FPS:
                for _ in range(80):
                    water_parts.append([sx + rng.normal(0, 25), sy, rng.normal(0, 3), -rng.uniform(8, 26), t,
                                        rng.uniform(8, 20)])
        for p in water_parts:
            age = t - p[4]
            if age < 2.2:
                x = p[0] + p[2] * age * FPS; y = p[1] + p[3] * age * FPS + 0.5 * 1400 * age * age
                if y < p[1] + 10:
                    blit(img, x, y, get_blob(p[5] * (1 + age)), (225, 228, 228), 0.55 * (1 - age / 2.2))
        if tgt_pt and t > 2.4:
            fire.step(*tgt_pt, t); smoke.step(tgt_pt[0], tgt_pt[1] - 20, t)
            if t < 2.6:
                blit(glow, tgt_pt[0], tgt_pt[1], get_blob(120), (255, 200, 120), 1.0, "add")
        smoke.draw(img, glow, t); fire.draw(img, glow, t)
        if down:
            x, y, tt = down
            fire.step(x - 20, y, t)
            smoke.step(x - 30, y, t)
            if y > hz + 240 and y < hz + 260:
                blit(img, x, hz + 250, get_blob(80), (225, 228, 228), 0.8)
        img = add_glow(img, glow, 16, 0.9)
        img = shake(img, t, 2.4 if hit else 9e9, 0.8, 12)
        return grade(img, t)

    encode(path, frame, n)


# ------------------------------------------------------------------ BOUNCE: bomb skips into Broadsword
def bounce(path, dur):
    rng = np.random.default_rng(5)
    n = int(dur * FPS)
    L = 1250; x0 = 420; yw = V.HORIZON + 230
    jets = [dict(t0=0.6, y=yw - 260, len=230), dict(t0=0.95, y=yw - 330, len=210)]
    t_drop, t_water, t_deck, t_out = 1.5, 2.4, 3.0, 3.7
    sparks, water, debris = [], [], []
    smoke = Emitter(10, 5, 22, (60, 58, 56), 0.5, (-18, -40), 10, grow=1.3, seed=8)

    def bomb_pos(t):
        if t < t_water:
            k = (t - t_drop) / (t_water - t_drop)
            return 120 + 160 * k, yw - 220 + 230 * k * k
        if t < t_deck:
            k = (t - t_water) / (t_deck - t_water)
            return 280 + 260 * k, yw + 10 - 110 * math.sin(k * math.pi * 0.9)
        k = (t - t_deck) / (t_out - t_deck)
        return 540 + 380 * k, yw - 90 + 40 * k - 160 * math.sin(k * math.pi) * 0.5

    def frame(i, t):
        img = V.sea_frame(t * 0.8)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        draw_ship(d, "t22", x0 + 8 * t, yw + math.sin(t) * 2, L, haze=0.0)
        for j in jets:
            if t >= j["t0"]:
                k = (t - j["t0"]) / 2.2
                x = -350 + k * (W + 700)
                for mb in range(3, -1, -1):
                    V.draw_a4_side(d, x - mb * 9, j["y"] + 30 * k, j["len"], alpha=255 if mb == 0 else 30,
                                   bombs=t < t_drop)
        if t_drop <= t < t_out + 1.2:
            bx, by = bomb_pos(min(t, t_out + 1.2)) if t < t_out else (920 + 300 * (t - t_out), yw - 70 + 600 * (t - t_out) ** 2)
            if by < yw + 20:
                d.ellipse([bx - 26, by - 9, bx + 26, by + 9], fill=(28, 28, 28, 255))
        img = composite(img, lay, blur=0.8)
        glow = np.zeros_like(img)
        if abs(t - t_water) < 0.5 / FPS:
            for _ in range(70):
                water.append([280 + rng.normal(0, 20), yw + 8, rng.normal(0, 3), -rng.uniform(6, 20), t, rng.uniform(6, 16)])
        if abs(t - t_out - 0.6) < 0.5 / FPS:
            for _ in range(60):
                water.append([1150 + rng.normal(0, 20), yw + 30, rng.normal(0, 3), -rng.uniform(6, 18), t, rng.uniform(6, 14)])
        if abs(t - t_deck) < 0.5 / FPS:
            for _ in range(60):
                a = rng.uniform(-math.pi, 0); v = rng.uniform(4, 16)
                sparks.append([540 + 8 * t, yw - 90, math.cos(a) * v, math.sin(a) * v, t])
                debris.append([540 + 8 * t, yw - 90, math.cos(a) * v * 0.6, math.sin(a) * v * 0.7, t])
        for p in water:
            age = t - p[4]
            if age < 2.0:
                x = p[0] + p[2] * age * FPS; y = p[1] + p[3] * age * FPS + 700 * age * age
                if y < p[1] + 10:
                    blit(img, x, y, get_blob(p[5] * (1 + age)), (225, 228, 228), 0.55 * (1 - age / 2))
        for s in sparks:
            age = t - s[4]
            if age < 0.6:
                blit(glow, s[0] + s[2] * age * FPS, s[1] + s[3] * age * FPS + 900 * age * age, get_blob(3),
                     (255, 210, 130), 0.9, "add")
        for s in debris:
            age = t - s[4]
            if age < 1.4:
                blit(img, s[0] + s[2] * age * FPS, s[1] + s[3] * age * FPS + 900 * age * age, get_blob(4),
                     (30, 30, 30), 0.9)
        if t > t_deck:
            smoke.step(540 + 8 * t, yw - 100, t)
        smoke.draw(img, glow, t)
        img = add_glow(img, glow, 10, 1.0)
        img = shake(img, t, t_deck, 0.6, 7)
        return grade(img, t)

    encode(path, frame, n)


# ------------------------------------------------------------------ ship cut-out for aftermath / sinking
SHIP_POLY = [(160, 478), (350, 470), (350, 408), (520, 403), (528, 348), (560, 336), (592, 348), (602, 398),
             (640, 398), (640, 242), (622, 240), (622, 170), (705, 170), (705, 240), (712, 298), (752, 298),
             (757, 236), (878, 228), (884, 328), (926, 328), (930, 132), (955, 132), (960, 318), (998, 318),
             (1000, 240), (1070, 240), (1070, 298), (1118, 298), (1126, 318), (1157, 312), (1194, 318),
             (1198, 378), (1272, 378), (1292, 412), (1468, 416), (1478, 408), (1505, 400), (1544, 410),
             (1548, 438), (1768, 452), (1770, 470), (1742, 520), (1732, 564), (180, 560), (168, 520), (148, 484)]
WATERLINE = lambda x: 557 + (x - 180) * (5 / 1540)
HITS = [(1080, 470), (760, 455)]        # the two bombs that exploded (screen positions on bg_ship2)


def ship_layers():
    bg = load_bg("bg_ship2.jpg")
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(SHIP_POLY, fill=255)
    ImageDraw.Draw(mask).rectangle([855, 190, 940, 232], fill=255)          # ensign on the halyard
    m = np.asarray(mask.filter(ImageFilter.GaussianBlur(1.5)), np.float32)[..., None] / 255
    big = np.asarray(mask.filter(ImageFilter.MaxFilter(31)).filter(ImageFilter.GaussianBlur(12)), np.float32)[..., None] / 255
    plate = bg.copy()
    shifted = np.roll(bg, -470, axis=0)                     # sea from lower rows
    shifted2 = np.roll(bg, -520, axis=0)
    fill = np.where((yy < 600)[..., None], shifted, shifted2)
    # match each row's brightness/colour to the untouched sea on the same row
    sea_only = (big[..., 0] < 0.02)
    for y in range(80, 640):
        row_ok = sea_only[y]
        if row_ok.sum() > 50:
            target = bg[y][row_ok].mean(axis=0)
            fill[y] += target - fill[y].mean(axis=0)
    plate = plate * (1 - big) + fill * big
    return bg, m, plate


def aftermath(path, dur):
    bg, m, plate = ship_layers()
    n = int(dur * FPS)
    fires = [Emitter(36, 0.9, 26, (0, 0, 0), 1, (0, -50), 14, kind="fire", seed=k) for k in range(2)]
    smokes = [Emitter(18, 6, 34, (30, 28, 27), 0.8, (-28, -70), 14, grow=1.5, seed=10 + k) for k in range(2)]

    def frame(i, t):
        z = 1.1 + 0.05 * t / dur
        img = bg.copy()
        glow = np.zeros_like(img)
        for k, (hx, hy) in enumerate(HITS):
            smokes[k].step(hx, hy - 25, t); fires[k].step(hx, hy, t)
            smokes[k].draw(img, glow, t)
        for f in fires:
            f.draw(img, glow, t)
        img = add_glow(img, glow, 22, 1.0)
        img = img * (1 + np.array([0.08, 0.02, -0.03], np.float32))
        img = zoom_crop(img, z, 980, 470)
        return grade(img, t)

    encode(path, frame, n)


def sink(path, dur, part=1):
    bg, m, plate = ship_layers()
    n = int(dur * FPS)
    rng = np.random.default_rng(part)
    x0, x1, y0, y1 = 140, 1780, 120, 600
    sub = bg[y0:y1, x0:x1]; msub = m[y0:y1, x0:x1, 0]
    ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    wl = WATERLINE(xs)
    fires = [Emitter(30, 0.9, 24, (0, 0, 0), 1, (0, -45), 14, kind="fire", seed=k) for k in range(2)]
    smokes = [Emitter(16, 6, 34, (30, 28, 27), 0.8, (-28, -70), 14, grow=1.5, seed=10 + k) for k in range(2)]
    if part == 3:
        for e in smokes:
            e.life = 3.5
    rafts = [(rng.uniform(250, 1600), rng.uniform(590, 760), rng.uniform(0.5, 1.0)) for _ in range(9)]
    # (roll start, roll end, sink start, sink end) in degrees / px, per part
    plan = {1: (4, 16, 0, 6), 2: (16, 48, 6, 30), 3: (48, 92, 30, 175)}[part]

    def frame(i, t):
        k = t / dur
        roll = plan[0] + (plan[1] - plan[0]) * k
        sinkpx = plan[2] + (plan[3] - plan[2]) * (k ** 1.3 if part == 3 else k)
        pitch = 0.012 * sinkpx / 30
        img = plate.copy()
        c = max(math.cos(math.radians(min(roll, 89))), 0.02)
        dy = sinkpx + pitch * (xs - 960)
        hd = wl - ys
        hs = (hd + dy) / c
        sy = np.clip((wl - hs - y0).astype(np.int32), 0, y1 - y0 - 1)
        sx = (xs - x0).astype(np.int32)
        src = sub[sy, sx]; a = msub[sy, sx] * (hd > -2) * (hs >= -1)
        shade = 1 - 0.5 * min(1, roll / 90)
        hull_fade = 1.0
        if part == 3:
            hull_fade = max(0.0, 1 - max(0, roll - 60) / 25)
        region = img[y0:y1, x0:x1]
        region[:] = region * (1 - a[..., None] * hull_fade) + src * shade * a[..., None] * hull_fade
        # capsized keel (part 3)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        if part == 3 and roll > 55:
            kh = 95 * min(1, (roll - 55) / 22) - max(0, sinkpx - 95) * 1.4
            if kh > 0:
                top, line = [], []
                for xx_ in range(176, 1736, 12):
                    u = (xx_ - 176) / 1560
                    prof = math.sin(math.pi * min(1.0, u * 1.08)) ** 0.35 if u < 0.92 else math.sin(math.pi * 0.994) ** 0.35 * (1 - (u - 0.92) / 0.08 * 0.8)
                    top.append((xx_, WATERLINE(xx_) - kh * prof))
                    line.append((xx_, WATERLINE(xx_) - kh * prof * 0.35))
                base = [(1736, WATERLINE(1736) + 3), (176, WATERLINE(176) + 3)]
                d.polygon(top + base, fill=(92, 40, 30, 255))
                d.line(line, fill=(40, 30, 28, 255), width=5)
                d.line(top, fill=(130, 70, 52, 255), width=3)
        # foam along the waterline
        for xx_ in range(180, 1740, 14):
            if rng.random() < 0.45:
                fx = xx_ + rng.normal(0, 8); fy = WATERLINE(xx_) + rng.normal(2, 4); fw = rng.uniform(6, 22)
                d.ellipse([fx - fw, fy - 3, fx + fw, fy + 4], fill=(205, 210, 210, int(rng.uniform(30, 110))))
        # life rafts
        for j, (rx, ry, s) in enumerate(rafts):
            vis = part >= 2 or (part == 1 and t > dur * (0.4 + j * 0.05))
            if vis:
                drift = 12 * t + j * 3
                bob = math.sin(t * 1.4 + j) * 3
                w = 46 * s; hgt = 22 * s
                X = rx - drift if j % 2 else rx + drift * 0.5
                d.ellipse([X - w, ry + bob - hgt * 0.4, X + w, ry + bob + hgt * 0.5], fill=(40, 40, 40, 255))
                d.pieslice([X - w * 0.8, ry + bob - hgt * 1.3, X + w * 0.8, ry + bob + hgt * 0.6], 180, 360,
                           fill=(225, 95, 30, 255))
        img = composite(img, lay, blur=1.0)
        glow = np.zeros_like(img)
        on = not (part == 3 and roll > 70)
        for kk, (hx, hy) in enumerate(HITS):
            px = hx; py = min(hy + sinkpx * 0.6 + (1 - c) * 60, WATERLINE(hx) - 5)
            smoke_on = on if part < 3 else (k < 0.55)
            smokes[kk].step(px, py - 25, t, on=smoke_on); fires[kk].step(px, py, t, on=on and part < 3)
            smokes[kk].draw(img, glow, t)
        for f in fires:
            f.draw(img, glow, t)
        if part == 3 and t > dur * 0.7:            # bubbles where she went down
            for _ in range(6):
                bx = rng.uniform(300, 1600); by = WATERLINE(bx) + rng.normal(0, 6)
                blit(img, bx, by, get_blob(rng.uniform(4, 12)), (220, 225, 225), 0.5)
        img = add_glow(img, glow, 20, 0.9)
        img = zoom_crop(img, 1.08 + 0.04 * k, 960, 480)
        return grade(img, t)

    encode(path, frame, n)


# ------------------------------------------------------------------ RESCUE: rafts + Sea King helicopter
def rescue(path, dur, seed=1):
    rng = np.random.default_rng(seed)
    n = int(dur * FPS)
    hz = V.HORIZON
    rafts = [(rng.uniform(200, 1700), rng.uniform(hz + 120, H - 120), rng.uniform(0.6, 1.4)) for _ in range(7)]
    smoke = Emitter(10, 8, 30, (40, 38, 36), 0.6, (-10, -30), 10, grow=1.6, seed=seed)
    spray = []

    def frame(i, t):
        img = V.sea_frame(t * 0.35)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        if seed == 1:      # capsized keel on the horizon
            d.ellipse([1150, hz - 6, 1450, hz + 8], fill=(80, 70, 66, 220))
        else:              # Broadsword standing by
            draw_ship(d, "t22", 1100, hz + 12, 520, haze=0.45)
        for j, (rx, ry, s) in enumerate(sorted(rafts, key=lambda r: r[1])):
            bob = math.sin(t * 1.3 + j) * 5 * s
            w = 70 * s; h2 = 34 * s
            X = rx + math.sin(t * 0.3 + j) * 10
            d.ellipse([X - w, ry + bob - h2 * 0.3, X + w, ry + bob + h2 * 0.5], fill=(35, 35, 35, 255))
            d.pieslice([X - w * 0.8, ry + bob - h2 * 1.4, X + w * 0.8, ry + bob + h2 * 0.6], 180, 360,
                       fill=(220, 92, 30, 255))
        # Sea King
        hx = 760 + 60 * math.sin(t * 0.4); hy = 260 + 12 * math.sin(t * 1.1)
        d.ellipse([hx - 170, hy - 45, hx + 170, hy + 45], fill=(30, 32, 34, 255))
        d.polygon([(hx + 150, hy - 10), (hx + 330, hy - 25), (hx + 335, hy - 5), (hx + 150, hy + 20)], fill=(30, 32, 34, 255))
        d.polygon([(hx + 315, hy - 25), (hx + 345, hy - 70), (hx + 355, hy - 65), (hx + 335, hy - 5)], fill=(30, 32, 34, 255))
        d.rectangle([hx - 20, hy - 70, hx + 25, hy - 45], fill=(30, 32, 34, 255))
        ang = t * 40
        d.ellipse([hx - 330, hy - 92, hx + 330, hy - 62], fill=(30, 32, 34, 70))
        for b in range(5):
            a = ang + b * 2 * math.pi / 5
            d.line([(hx, hy - 75), (hx + 330 * math.cos(a), hy - 77 + 14 * math.sin(a))], fill=(25, 26, 28, 120), width=5)
        d.line([(hx + 20, hy + 40), (hx + 20, hy + 260)], fill=(20, 20, 20, 255), width=2)          # winch cable
        img = composite(img, lay, blur=1.0)
        glow = np.zeros_like(img)
        if seed == 1:
            smoke.step(1300, hz - 10, t)
            smoke.draw(img, glow, t)
        if i % 2 == 0:
            for _ in range(5):
                a = rng.uniform(0, 2 * math.pi)
                spray.append([hx + math.cos(a) * 90, hz + 330 + math.sin(a) * 20, math.cos(a) * 9, -rng.uniform(0, 2), t])
        for s in spray:
            age = t - s[4]
            if age < 1.5:
                blit(img, s[0] + s[2] * age * FPS, s[1] + s[3] * age * FPS, get_blob(14 + 20 * age), (210, 215, 215),
                     0.25 * (1 - age / 1.5))
        img = shake(img, t, 0, dur, 2)
        return grade(img, t)

    encode(path, frame, n)


def calm(path, dur):
    n = int(dur * FPS)

    def frame(i, t):
        img = V.sea_frame(t * 0.25)
        img = img * np.array([1.05, 0.92, 0.85], np.float32) * (0.85 - 0.15 * t / dur)
        return grade(img, t)

    encode(path, frame, n)


# ------------------------------------------------------------------ dispatcher
def render(kind, params, dur, out):
    p = dict(params)
    p.pop("kind", None)
    if kind == "approach":
        return V.shot_approach(out, dur)
    if kind == "attack":
        return V.shot_attack(os.path.join(BG_DIR, "bg_ship1.jpg"), out, dur)
    if kind == "impact":
        return V.shot_impact(os.path.join(BG_DIR, "bg_ship2.jpg"), out, dur)
    fn = {"pov": pov, "radar": radar, "fleet": fleet, "seadart": seadart, "raid": raid, "bounce": bounce,
          "aftermath": aftermath, "sink": sink, "rescue": rescue, "calm": calm}[kind]
    return fn(out, dur, **p)


if __name__ == "__main__":
    import json
    kind = sys.argv[1]; dur = float(sys.argv[2]); out = sys.argv[3]
    params = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
    render(kind, params, dur, out)
