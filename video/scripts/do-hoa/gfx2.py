"""Infographic kit in the style of Vietnamese military-history channels.

render(name, dur, out) – each sample is a function frame(t) -> PIL.Image (1920x1080).
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1920, 1080, 30
INTER = "/usr/share/fonts/truetype/inter/Inter-ExtraBold.ttf"
if not os.path.exists(INTER):
    INTER = subprocess.run(["fc-match", "-f", "%{file}", "Inter:extrabold"], capture_output=True, text=True).stdout
INTER_SB = subprocess.run(["fc-match", "-f", "%{file}", "Inter:semibold"], capture_output=True, text=True).stdout
OSWALD = os.path.join(HERE, "oswald-700.ttf")
CYAN = (64, 214, 255)
WHITE = (255, 255, 255)
_fc = {}


def font(path, size):
    k = (path, int(size))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, int(size))
    return _fc[k]


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def back(x):  # ease-out-back (small overshoot) for pop-ins
    x = min(max(x, 0.0), 1.0)
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def shadow_text(img, xy, text, fnt, fill=WHITE, anchor="la", blur=6, offset=3, alpha=1.0, stroke=0):
    if alpha <= 0:
        return
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text((xy[0] + offset, xy[1] + offset), text, font=fnt, fill=(0, 0, 0, int(220 * alpha)), anchor=anchor,
           stroke_width=stroke, stroke_fill=(0, 0, 0, int(220 * alpha)))
    lay = lay.filter(ImageFilter.GaussianBlur(blur))
    d = ImageDraw.Draw(lay)
    d.text(xy, text, font=fnt, fill=fill + (int(255 * alpha),), anchor=anchor)
    img.alpha_composite(lay)


def vignette(strength=0.55):
    y, x = np.mgrid[0:H, 0:W]
    r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    v = 1 - strength * np.clip(r - 0.35, 0, 1) ** 1.4
    return v[..., None]


VIG = vignette()


def finish(img, grain=6, vig=True):
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    if vig:
        a *= VIG
    if grain:
        a += np.random.normal(0, grain, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ------------------------------------------------------------------ satellite map
_EARTH = None


def earth():
    """Blue Marble (NASA, public domain), rolled so the Pacific (lon 180) is in the middle."""
    global _EARTH
    if _EARTH is None:
        im = Image.open(os.path.join(HERE, "dl", "earth-blue-marble.jpg")).convert("RGB")
        a = np.roll(np.asarray(im), im.width // 2, axis=1)  # now x=0 is lon 0 -> center lon 180
        f = a.astype(np.float32) / 255
        ocean = np.clip((f[..., 2] - f[..., 0] - 0.04) * 8, 0, 1)[..., None]
        lit = f ** 0.7
        sea = lit * np.array([0.55, 0.95, 1.35]) + np.array([0.02, 0.10, 0.22])
        f = lit * (1 - ocean) + sea * ocean
        im = Image.fromarray(np.clip(f * 255, 0, 255).astype(np.uint8))
        im = ImageEnhance.Contrast(im).enhance(1.15)
        im = ImageEnhance.Color(im).enhance(1.2)
        _EARTH = im
    return _EARTH


def lonlat_to_px(lon, lat):
    e = earth()
    lon = lon % 360  # 0..360, 180 = center
    x = (lon / 360.0) * e.width  # rolled: x for lon L is (L+180+180)%360 -> L%360
    y = (90 - lat) / 180.0 * e.height
    return x, y


class SatMap:
    """Tilted, slowly pushing satellite map. view = (lon_c, lat_c, width_deg) keyframes."""

    def __init__(self, v0, v1, tilt=0.16):
        self.v0, self.v1, self.tilt = v0, v1, tilt

    def view(self, k):
        k = ease(k)
        return tuple(a + (b - a) * k for a, b in zip(self.v0, self.v1))

    def frame(self, k):
        lonc, latc, wdeg = self.view(k)
        e = earth()
        ppd = e.width / 360.0
        cx, cy = lonlat_to_px(lonc, latc)
        cw = wdeg * ppd * 1.25
        ch = cw * H / W * 1.25
        box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
        flat = e.resize((int(W * 1.25), int(H * 1.25)), Image.BICUBIC, box=box)
        if cw < W * 0.5:  # strong upscale: soften JPEG blocks before sharpening
            flat = flat.filter(ImageFilter.GaussianBlur(2))
        flat = flat.filter(ImageFilter.UnsharpMask(2, 60, 2))
        # perspective tilt: top edge narrower
        Wf, Hf = flat.size
        t = self.tilt
        src = [(Wf * t, 0), (Wf * (1 - t), 0), (Wf, Hf), (0, Hf)]
        dst = [(0, 0), (W, 0), (W, H), (0, H)]
        coeffs = _persp_coeffs(dst, src)
        img = flat.transform((W, H), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
        # darken + cool tint toward the top (atmosphere)
        a = np.asarray(img).astype(np.float32)
        gy = np.linspace(0.72, 1.0, H)[:, None, None]
        a = a * gy + np.array([10, 20, 40]) * (1 - gy)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        self._state = (box, flat.size, src)
        return img

    def project(self, lon, lat):
        """lon/lat -> screen xy after crop + perspective."""
        box, (Wf, Hf), src = self._state
        x, y = lonlat_to_px(lon, lat)
        u = (x - box[0]) / (box[2] - box[0]) * Wf
        v = (y - box[1]) / (box[3] - box[1]) * Hf
        # inverse of the perspective: flat (u,v) -> screen
        t = self.tilt
        fy = v / Hf
        left = Wf * t * (1 - fy)
        right = Wf - Wf * t * (1 - fy)
        sx = (u - left) / (right - left) * W
        sy = fy * H
        return sx, sy


def _persp_coeffs(pa, pb):
    m = []
    for (x, y), (X, Y) in zip(pa, pb):
        m.append([x, y, 1, 0, 0, 0, -X * x, -X * y])
        m.append([0, 0, 0, x, y, 1, -Y * x, -Y * y])
    A = np.array(m, dtype=float)
    B = np.array(pb, dtype=float).reshape(8)
    return np.linalg.solve(A, B).tolist()


def draw_pin(img, x, y, s=1.0, alpha=1.0, color=(255, 120, 70)):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    r = 17 * s
    a = int(255 * alpha)
    d.ellipse((x - r * 0.6, y - 3 * s, x + r * 0.6, y + 3 * s), fill=(0, 0, 0, int(120 * alpha)))
    d.polygon([(x, y), (x - r * 0.75, y - r * 1.3), (x + r * 0.75, y - r * 1.3)], fill=WHITE + (a,))
    d.ellipse((x - r, y - r * 2.3, x + r, y - r * 0.3), fill=WHITE + (a,))
    d.ellipse((x - r * 0.55, y - r * 1.85, x + r * 0.55, y - r * 0.75), fill=color + (a,))
    img.alpha_composite(lay)


def label2(img, x, y, small, big, alpha=1.0, size=58, anchor="l"):
    """Two-line place label: small cyan line over big white bold line (with shadow)."""
    fb, fs = font(INTER, size), font(INTER, size * 0.5)
    ax = {"l": "l", "m": "m", "r": "r"}[anchor]
    if small:
        shadow_text(img, (x, y - size * 0.62), small, fs, fill=CYAN, anchor=ax + "s", alpha=alpha, blur=4)
    shadow_text(img, (x, y + size * 0.42), big, fb, anchor=ax + "s", alpha=alpha)


def tag_box(img, x, y, text, alpha=1.0, size=26):
    """Black-on-white condensed label box (unit / aircraft name)."""
    f = font(OSWALD, size)
    d = ImageDraw.Draw(img)
    l, t, r, b = d.textbbox((x, y), text, font=f, anchor="lm")
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    dl.rectangle((l - 8, t - 5, r + 8, b + 5), fill=(255, 255, 255, int(235 * alpha)), outline=(0, 0, 0, int(255 * alpha)), width=2)
    dl.text((x, y), text, font=f, fill=(10, 10, 10, int(255 * alpha)), anchor="lm")
    img.alpha_composite(lay)


def ship_icon(img, x, y, ang, s=1.0, color=WHITE, alpha=1.0, carrier=True):
    """Top-down carrier/ship silhouette pointing along ang (radians, 0 = east)."""
    L, Wd = (46 if carrier else 30) * s, (11 if carrier else 7) * s
    pts = [(-L / 2, -Wd / 2), (L / 2 - Wd, -Wd / 2), (L / 2, 0), (L / 2 - Wd, Wd / 2), (-L / 2, Wd / 2)]
    c, sn = math.cos(ang), math.sin(ang)
    P = [(x + px * c - py * sn, y + px * sn + py * c) for px, py in pts]
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon([(p[0] + 3, p[1] + 3) for p in P], fill=(0, 0, 0, int(140 * alpha)))
    d.polygon(P, fill=color + (int(255 * alpha),), outline=(0, 0, 0, int(200 * alpha)))
    if carrier:  # island
        ix, iy = x + (L * 0.1) * c - (-Wd * 0.35) * sn, y + (L * 0.1) * sn + (-Wd * 0.35) * c
        d.ellipse((ix - 3 * s, iy - 3 * s, ix + 3 * s, iy + 3 * s), fill=(40, 40, 40, int(255 * alpha)))
    img.alpha_composite(lay)


def plane_icon(img, x, y, ang, s=1.0, color=CYAN, alpha=1.0):
    pts = [(22, 0), (4, -4), (2, -22), (-4, -22), (-6, -4), (-16, -3), (-20, -10), (-24, -10), (-21, 0),
           (-24, 10), (-20, 10), (-16, 3), (-6, 4), (-4, 22), (2, 22), (4, 4)]
    c, sn = math.cos(ang), math.sin(ang)
    P = [(x + (px * c - py * sn) * s, y + (px * sn + py * c) * s) for px, py in pts]
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon([(p[0] + 3, p[1] + 4) for p in P], fill=(0, 0, 0, int(130 * alpha)))
    d.polygon(P, fill=color + (int(255 * alpha),))
    img.alpha_composite(lay)


def path_arrow(img, pts, k, color=(255, 70, 60), width=7, alpha=1.0, dashed=False):
    """Draw polyline pts progressively (k in 0..1) with an arrow head."""
    if k <= 0:
        return None
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total, want = sum(seg), sum(seg) * min(k, 1)
    out, acc = [pts[0]], 0
    for i, sl in enumerate(seg):
        if acc + sl >= want:
            f = (want - acc) / sl
            out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f))
            break
        out.append(pts[i + 1]); acc += sl
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    col = color + (int(255 * alpha),)
    d.line([(p[0] + 3, p[1] + 3) for p in out], fill=(0, 0, 0, int(120 * alpha)), width=width, joint="curve")
    if dashed:
        for a, b in zip(out, out[1:]):
            n = max(1, int(math.dist(a, b) / 22))
            for j in range(0, n, 2):
                d.line([(a[0] + (b[0] - a[0]) * j / n, a[1] + (b[1] - a[1]) * j / n),
                        (a[0] + (b[0] - a[0]) * (j + 1) / n, a[1] + (b[1] - a[1]) * (j + 1) / n)], fill=col, width=width)
    else:
        d.line(out, fill=col, width=width, joint="curve")
    (x0, y0), (x1, y1) = out[-2], out[-1]
    ang = math.atan2(y1 - y0, x1 - x0)
    hs = width * 3.4
    head = [(x1 + math.cos(ang) * hs * 0.6, y1 + math.sin(ang) * hs * 0.6),
            (x1 + math.cos(ang + 2.5) * hs, y1 + math.sin(ang + 2.5) * hs),
            (x1 + math.cos(ang - 2.5) * hs, y1 + math.sin(ang - 2.5) * hs)]
    d.polygon(head, fill=col)
    img.alpha_composite(lay)
    return out[-1], ang


# ------------------------------------------------------------------ samples
LOC = {"midway": (-177.37, 28.21), "pearl": (-157.95, 21.35), "tokyo": (139.7, 35.68),
       "kido": (-179.3, 31.0), "us": (-173.0, 32.2), "aleut": (-174.0, 51.8)}


def s_map_pacific(t, dur):
    m = SatMap((-190, 33, 100), (-186, 32, 84), tilt=0.12)
    img = m.frame(t / dur)
    pins = [("tokyo", "THỦ ĐÔ NHẬT BẢN", "TOKYO", 0.8, "l"), ("midway", "ĐẢO SAN HÔ", "MIDWAY", 1.6, "l"),
            ("pearl", "CĂN CỨ HẠM ĐỘI MỸ", "TRÂN CHÂU CẢNG", 2.4, "m")]
    for key, small, big, t0, anc in pins:
        x, y = m.project(*LOC[key])
        k = (t - t0) / 0.5
        if k > 0:
            draw_pin(img, x, y, s=0.6 + 0.4 * back(k), alpha=ease(k))
            if anc == "m":
                label2(img, x, y + 90, small, big, alpha=ease(k), size=52, anchor="m")
            else:
                label2(img, x + 34, y - 44, small, big, alpha=ease(k), size=52, anchor=anc)
    # distance line Pearl -> Midway
    k = (t - 3.2) / 1.2
    if k > 0:
        a, b = m.project(*LOC["pearl"]), m.project(*LOC["midway"])
        path_arrow(img, [a, b], ease(k), color=(255, 220, 90), width=5, dashed=True)
        if k > 0.9:
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 40
            tag_box(img, mx - 90, my - 80, "KHOẢNG 2.100 KM", alpha=ease((k - 0.9) * 4))
    return finish(img)


_OCEAN = None


def ocean_tex():
    """Procedural deep-ocean texture (fractal noise), 2x screen size for slow drift."""
    global _OCEAN
    if _OCEAN is None:
        rng = np.random.default_rng(7)
        acc = np.zeros((H * 2 // 4, W * 2 // 4), np.float32)
        for o, amp in ((6, 1.0), (12, 0.5), (24, 0.25), (48, 0.14), (96, 0.08)):
            n = rng.random((o, int(o * 16 / 9))).astype(np.float32)
            acc += amp * np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize(acc.shape[::-1], Image.BICUBIC),
                                    np.float32) / 255
        acc = (acc - acc.min()) / (acc.max() - acc.min())
        c0, c1 = np.array([8, 30, 66]), np.array([30, 92, 150])
        rgb = c0 + (c1 - c0) * acc[..., None] ** 1.3
        _OCEAN = Image.fromarray(rgb.astype(np.uint8)).resize((W * 2, H * 2), Image.BICUBIC)
    return _OCEAN


def tactical_bg(m, t, dur, step=2):
    """Ocean texture under the satellite map's projection + lat/lon graticule with degree labels."""
    k = t / dur
    img = ocean_tex().crop((int(200 + 60 * k), int(150 + 30 * k), int(200 + 60 * k) + W, int(150 + 30 * k) + H)).convert("RGBA")
    a = np.asarray(img).astype(np.float32)
    a *= np.linspace(0.75, 1.0, H)[:, None, None]
    img = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    lonc, latc, wd = m.view(k)
    f = font(INTER_SB, 20)
    for lon in range(int(lonc - wd) // step * step, int(lonc + wd) + step, step):
        pts = [m.project(lon, la) for la in np.linspace(latc - wd, latc + wd, 30)]
        d.line(pts, fill=(160, 210, 255, 70), width=2)
        x, y = m.project(lon, latc - wd * 0.26)
        if 0 < x < W:
            L = ((lon + 180) % 360) - 180
            d.text((x + 6, H - 30), f"{abs(L)}°{'T' if L < 0 else 'Đ'}", font=f, fill=(190, 225, 255, 150))
    for lat in range(int(latc - wd) // step * step, int(latc + wd) + step, step):
        pts = [m.project(lo, lat) for lo in np.linspace(lonc - wd, lonc + wd, 30)]
        d.line(pts, fill=(160, 210, 255, 70), width=2)
        x, y = m.project(lonc - wd * 0.45, lat)
        if 0 < y < H:
            d.text((14, y - 26), f"{lat}°B", font=f, fill=(190, 225, 255, 150))
    img.alpha_composite(lay)
    return img


def s_map_attack(t, dur):
    """Japanese strike force vs US carriers near Midway, with animated aircraft paths."""
    m = SatMap((-176.0, 30.8, 21), (-175.9, 30.7, 18), tilt=0.2)
    m.frame(t / dur)
    img = tactical_bg(m, t, dur)
    mx, my = m.project(*LOC["midway"])
    draw_pin(img, mx, my, s=0.9)
    label2(img, mx + 30, my - 40, "ĐẢO SAN HÔ", "MIDWAY", size=48)
    jp = [m.project(-179.0 + dx, 31.0 + dy) for dx, dy in ((0, 0), (0.9, 0.5), (0.3, -0.8), (1.2, -0.3))]
    for i, (x, y) in enumerate(jp):
        ship_icon(img, x, y, math.radians(-20), s=1.5, color=(240, 240, 240), alpha=ease((t - 0.3 - i * 0.15) * 3))
    jx, jy = jp[0]
    if t > 0.8:
        tag_box(img, jx - 150, jy + 120, "4 TÀU SÂN BAY NHẬT", alpha=ease((t - 0.8) * 3))
    us = [m.project(-173.4 + dx, 32.4 + dy) for dx, dy in ((0, 0), (1.0, 0.4), (0.5, -0.8))]
    for i, (x, y) in enumerate(us):
        ship_icon(img, x, y, math.radians(200), s=1.5, color=(90, 200, 255), alpha=ease((t - 1.0 - i * 0.15) * 3))
    if t > 1.4:
        ux, uy = us[0]
        tag_box(img, ux - 200, uy - 90, "3 TÀU SÂN BAY MỸ: ENTERPRISE · HORNET · YORKTOWN", alpha=ease((t - 1.4) * 3))
    # Japanese strike on Midway (red), US strike on carriers (cyan)
    r = path_arrow(img, [(jx + 30, jy + 10), ((jx + mx) / 2 + 40, (jy + my) / 2 - 30), (mx - 18, my - 30)],
                   ease((t - 1.6) / 1.8), color=(255, 70, 60), width=6)
    if r:
        plane_icon(img, *r[0], r[1], s=0.9, color=(255, 90, 80))
    r = path_arrow(img, [(us[0][0] - 30, us[0][1] + 6), ((us[0][0] + jx) / 2, (us[0][1] + jy) / 2 - 70), (jx + 40, jy - 30)],
                   ease((t - 3.2) / 1.8), color=CYAN, width=6)
    if r:
        plane_icon(img, *r[0], r[1], s=0.9, color=CYAN)
    shadow_text(img, (W - 70, 90), "SÁNG 04/06/1942", font(INTER, 40), fill=WHITE, anchor="rs")
    return finish(img)


def grid_bg(t, offset=True):
    img = Image.new("RGBA", (W, H), (12, 13, 16, 255))
    d = ImageDraw.Draw(img)
    step, sh = 90, (t * 12) % 90 if offset else 0
    for x in np.arange(-step, W + step, step):
        d.line([(x + sh, 0), (x + sh, H)], fill=(48, 50, 56), width=1)
    for y in np.arange(-step, H + step, step):
        d.line([(0, y + sh * 0.5), (W, y + sh * 0.5)], fill=(48, 50, 56), width=1)
    return img


def portrait(img, photo, cx, cy, h, k, name, sub=None):
    p = ImageOps.grayscale(Image.open(photo)).convert("RGB")
    p = ImageOps.fit(p, (int(h * 0.8), h), centering=(0.5, 0.3))
    p = ImageEnhance.Contrast(p).enhance(1.15)
    s = 0.85 + 0.15 * back(k)
    pw, ph = int(p.width * s), int(p.height * s)
    p = p.resize((pw, ph))
    card = Image.new("RGBA", (pw + 14, ph + 14), (255, 255, 255, 255))
    card.paste(p, (7, 7))
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 170))
    lay.paste(sh, (int(cx - card.width / 2) + 10, int(cy - card.height / 2) + 12))
    lay = lay.filter(ImageFilter.GaussianBlur(12))
    img.alpha_composite(lay)
    card.putalpha(int(255 * ease(k * 1.5)))
    img.alpha_composite(card, (int(cx - card.width / 2), int(cy - card.height / 2)))
    ty = cy + card.height / 2 + 64
    shadow_text(img, (cx, ty), name, font(INTER, 60), anchor="ms", alpha=ease((k - 0.3) * 2))
    if sub:
        shadow_text(img, (cx, ty + 50), sub, font(INTER, 30), fill=CYAN, anchor="ms", alpha=ease((k - 0.5) * 2))


def s_portrait_grid(t, dur):
    img = grid_bg(t)
    portrait(img, os.path.join(HERE, "photos", "nimitz.jpg"), W / 2, 450, 560, t / 0.8,
             "Chester Nimitz", "TỔNG TƯ LỆNH HẠM ĐỘI THÁI BÌNH DƯƠNG")
    return finish(img, vig=True)


def s_portrait_map(t, dur):
    m = SatMap((128, 35, 36), (130, 35, 31))
    img = m.frame(t / dur)
    x, y = m.project(*LOC["tokyo"])
    draw_pin(img, x, y, s=1.0, alpha=ease((t - 0.6) * 2))
    label2(img, x + 30, y - 40, "THỦ ĐÔ", "TOKYO", size=50, alpha=ease((t - 0.6) * 2))
    portrait(img, os.path.join(HERE, "photos", "nagumo.jpg"), 420, 470, 520, t / 0.8, "Nagumo Chuichi",
             "PHÓ ĐÔ ĐỐC – LỰC LƯỢNG CƠ ĐỘNG")
    return finish(img)


def kenburns(photo, t, dur, z0=1.0, z1=1.12, gray=False, dark=0.0):
    p = Image.open(photo).convert("RGB")
    if gray:
        p = ImageOps.grayscale(p).convert("RGB")
    p = ImageOps.fit(p, (W, H))
    z = z0 + (z1 - z0) * t / dur
    cw, ch = W / z, H / z
    p = p.resize((W, H), Image.BICUBIC, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
    if dark:
        p = ImageEnhance.Brightness(p).enhance(1 - dark)
    return p.convert("RGBA")


def s_time(t, dur):
    img = kenburns(os.path.join(HERE, "photos", "dauntless.jpg"), t, dur, gray=False)
    k = ease(t / 0.6)
    shadow_text(img, (90 - 40 * (1 - k), 980), "10 : 22 SÁNG", font(INTER, 80), anchor="ls", alpha=k)
    shadow_text(img, (92 - 40 * (1 - k), 900), "NGÀY 4 THÁNG 6 NĂM 1942", font(INTER, 30), fill=CYAN, anchor="ls",
                alpha=ease((t - 0.3) / 0.6))
    return finish(img, grain=8)


def s_stats(t, dur):
    img = Image.new("RGBA", (W, H), (14, 15, 18, 255))
    ph = Image.open(os.path.join(HERE, "photos", "dauntless.jpg")).convert("RGB")
    ph = ImageOps.fit(ph, (1100, 600))
    z = 1 + 0.05 * t / dur
    ph = ph.resize((int(1100 * z), int(600 * z)))
    mask = Image.new("L", ph.size, 0)
    dm = ImageDraw.Draw(mask)
    dm.rounded_rectangle((0, 0, ph.width, ph.height), 0, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0))
    # feather edges
    fe = np.ones((ph.height, ph.width), np.float32)
    for i in range(80):
        a = i / 80
        fe[i, :] *= a; fe[-1 - i, :] *= a; fe[:, i] *= a; fe[:, -1 - i] *= a
    ph = ph.convert("RGBA"); ph.putalpha(Image.fromarray((fe * 255 * ease(t / 0.6)).astype(np.uint8)))
    img.alpha_composite(ph, (int(W / 2 - ph.width / 2), 70))
    shadow_text(img, (W / 2, 120), "SBD DAUNTLESS", font(OSWALD, 64), anchor="ms", alpha=ease((t - 0.2) / 0.5))
    stats = [("TỐC ĐỘ TỐI ĐA", 410, " KM/H"), ("MANG BOM", 454, " KG"), ("TỔ LÁI", 2, " NGƯỜI")]
    for i, (lab, val, unit) in enumerate(stats):
        x = W / 2 + (i - 1) * 480
        k = (t - 0.6 - i * 0.25) / 0.8
        if k <= 0:
            continue
        shadow_text(img, (x, 800), lab, font(INTER, 34), fill=CYAN, anchor="ms", alpha=ease(k))
        v = int(round(val * ease(k)))
        shadow_text(img, (x, 880), f"{v}{unit}", font(INTER, 66), anchor="ms", alpha=ease(k))
    return finish(img)


def s_keyword(t, dur):
    img = kenburns(os.path.join(HERE, "photos", "pearl.jpg"), t, dur, gray=True, dark=0.45)
    k = ease(t / 0.35)
    s = 1.25 - 0.25 * k
    f = font(OSWALD, 150 * s)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((W / 2, H / 2), "TRÂN CHÂU CẢNG", font=f, fill=(0, 0, 0, int(200 * k)), anchor="mm")
    lay = lay.filter(ImageFilter.GaussianBlur(10))
    ImageDraw.Draw(lay).text((W / 2, H / 2), "TRÂN CHÂU CẢNG", font=f, fill=(225, 30, 30, int(255 * k)), anchor="mm",
                             stroke_width=2, stroke_fill=(120, 0, 0, int(255 * k)))
    shadow_text(lay, (W / 2, H / 2 + 120), "NGÀY 7 THÁNG 12 NĂM 1941", font(INTER, 40), anchor="ms",
                alpha=ease((t - 0.5) / 0.5))
    img.alpha_composite(lay)
    return finish(img, grain=10)


def s_signal(t, dur):
    img = Image.new("RGBA", (W, H), (6, 8, 10, 255))
    d = ImageDraw.Draw(img)
    cx, top, base = W / 2, 330, 860
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    # waveform
    xs = np.arange(0, W, 4)
    amp = 70 * (0.5 + 0.5 * np.sin(t * 3))
    ys = 400 + amp * np.sin(xs / 37 + t * 9) * np.exp(-((xs - cx) / 700) ** 2) * (1 + 0.5 * np.sin(xs / 11 + t * 17))
    dl.line(list(zip(xs, ys)), fill=CYAN + (255,), width=4)
    # rings
    for i in range(3):
        r = ((t * 160 + i * 160) % 480) + 60
        a = int(255 * (1 - (r - 60) / 480))
        dl.arc((cx - r, top - r * 0.8, cx + r, top + r * 0.8), 200, 340, fill=(255, 255, 255, a), width=5)
        dl.arc((cx - r, top - r * 0.8, cx + r, top + r * 0.8), 20, 160, fill=(255, 255, 255, a), width=5)
    glow = lay.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(glow); img.alpha_composite(lay)
    # tower
    d = ImageDraw.Draw(img)
    hw = 150
    d.line([(cx, top), (cx - hw, base)], fill=WHITE, width=8)
    d.line([(cx, top), (cx + hw, base)], fill=WHITE, width=8)
    for i in range(1, 7):
        y0 = top + (base - top) * i / 7
        w0 = hw * i / 7
        y1 = top + (base - top) * (i + 1) / 7
        w1 = hw * (i + 1) / 7
        d.line([(cx - w0, y0), (cx + w0, y0)], fill=WHITE, width=5)
        d.line([(cx - w0, y0), (cx + w1, y1)], fill=WHITE, width=4)
        d.line([(cx + w0, y0), (cx - w1, y1)], fill=WHITE, width=4)
    d.ellipse((cx - 22, top - 22, cx + 22, top + 22), fill=WHITE)
    # quote (typewriter)
    q = "“AF ĐANG THIẾU NƯỚC NGỌT.”"
    n = int(len(q) * min(1, max(0, (t - 0.5) / 1.6)))
    if n:
        f = font(OSWALD, 64)
        box = ImageDraw.Draw(img).textbbox((cx, 960), q, font=f, anchor="ms")
        ImageDraw.Draw(img).rectangle((box[0] - 20, box[1] - 14, box[2] + 20, box[3] + 14), fill=(0, 0, 0, 200))
        shadow_text(img, (box[0], 960), q[:n], f, fill=(240, 240, 240), anchor="ls")
    shadow_text(img, (70, 80), "ĐIỆN TÍN NHẬT BỊ CHẶN BẮT – THÁNG 5/1942", font(INTER, 30), fill=CYAN, anchor="ls")
    return finish(img, grain=4, vig=False)


def s_casualty(t, dur):
    flash = max(0.0, 1 - t / 0.5)
    base = 235 - 30 * min(t / dur, 1)
    img = Image.new("RGBA", (W, H), (int(base), int(base), int(base) - 5, 255))
    k = ease((t - 0.3) / 0.8)
    f = font(OSWALD, 120)
    ImageDraw.Draw(img).text((W / 2, H / 2), "4 TÀU SÂN BAY NHẬT", font=f, fill=(30, 30, 30, int(255 * k)), anchor="mm")
    ImageDraw.Draw(img).text((W / 2, H / 2 + 110), "BỊ HẠ GỤC TRONG MỘT NGÀY", font=font(INTER, 44),
                             fill=(160, 20, 20, int(255 * ease((t - 0.8) / 0.6))), anchor="mm")
    img = finish(img, grain=8, vig=True)
    if flash:
        img = Image.blend(img, Image.new("RGB", (W, H), "white"), flash)
    return img


SAMPLES = {"map_pacific": (s_map_pacific, 6.5), "map_attack": (s_map_attack, 7.0),
           "portrait_grid": (s_portrait_grid, 4.0), "portrait_map": (s_portrait_map, 4.5),
           "time": (s_time, 4.0), "stats": (s_stats, 4.5), "keyword": (s_keyword, 3.5),
           "signal": (s_signal, 4.5), "casualty": (s_casualty, 3.5)}


def render(name, out):
    fn, dur = SAMPLES[name]
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        p.stdin.write(fn(i / FPS, dur).convert("RGB").tobytes())
    p.stdin.close(); p.wait()
    return out


def still(name, t, out):
    fn, dur = SAMPLES[name]
    fn(t, dur).convert("RGB").save(out)


if __name__ == "__main__":
    if sys.argv[1] == "still":
        still(sys.argv[2], float(sys.argv[3]), sys.argv[4])
    else:
        render(sys.argv[1], sys.argv[2])
