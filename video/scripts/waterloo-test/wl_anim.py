"""Dựng hoạt cảnh chiến thuật Waterloo 13:00-14:00 (d'Erlon tấn công, kỵ binh Anh phản kích).
python3 wl_anim.py test 0 300 450 ...   |   python3 wl_anim.py render [start end]
"""
import math, os, sys, json, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(HERE)
W, H = 1920, 1080
FPS = 30
DUR = 24.0
NF = int(DUR * FPS)
FOV = math.radians(36)
FOC = (W / 2) / math.tan(FOV / 2)
OSWALD = os.path.join(S, "gfx", "oswald-700.ttf")
BARLOW = os.path.join(S, "gfx", "barlow-condensed-700.ttf")
CORM = os.path.join(S, "gfx", "dl", "cormsc700.ttf")
GEO = json.load(open(os.path.join(HERE, "geo.json")))
_fc = {}


def F(p, s):
    k = (p, int(s))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(p, max(6, int(s)))
    return _fc[k]


def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)


def ease(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


def lerp(a, b, t):
    return a + (b - a) * t


# ============================ camera ============================
CAM = [  # t, cx, cy, viewW, yaw, tilt
    (0.0, 3020, 1930, 3700, -9, 24), (4.5, 3120, 1900, 3350, -8, 24), (8.0, 3260, 1870, 3050, -7, 25),
    (12.0, 3300, 1760, 2250, -5, 27), (17.0, 3240, 1680, 1950, -4, 27), (20.5, 3120, 1830, 2050, -3, 28), (24.0, 3060, 1960, 2150, -2, 28)]


def cam_at(t):
    ks = CAM
    if t <= ks[0][0]: return ks[0][1:]
    if t >= ks[-1][0]: return ks[-1][1:]
    for i in range(len(ks) - 1):
        if ks[i][0] <= t <= ks[i + 1][0]: break
    p0 = np.array(ks[max(i - 1, 0)][1:], float); p1 = np.array(ks[i][1:], float)
    p2 = np.array(ks[i + 1][1:], float); p3 = np.array(ks[min(i + 2, len(ks) - 1)][1:], float)
    u = (t - ks[i][0]) / (ks[i + 1][0] - ks[i][0])
    # Catmull-Rom
    return tuple(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))


class Cam:
    def __init__(self, t):
        cx, cy, vw, yaw, tilt = cam_at(t)
        th, ph = math.radians(yaw), math.radians(tilt)
        D = (vw / 2) / math.tan(FOV / 2)
        fg = np.array([math.sin(th), -math.cos(th)]); rg = np.array([math.cos(th), math.sin(th)])
        self.C = np.array([cx - fg[0] * D * math.sin(ph), cy - fg[1] * D * math.sin(ph), D * math.cos(ph)])
        self.look = np.array([fg[0] * math.sin(ph), fg[1] * math.sin(ph), -math.cos(ph)])
        self.right = np.array([rg[0], rg[1], 0.0])
        self.down = -np.array([fg[0] * math.cos(ph), fg[1] * math.cos(ph), math.sin(ph)])
        self.yaw = th

    def proj(self, xy, z=0.0):
        xy = np.atleast_2d(np.asarray(xy, float))
        P = np.c_[xy, np.full(len(xy), z) if np.isscalar(z) else z]
        d = P - self.C; zc = d @ self.look
        u = W / 2 + FOC * (d @ self.right) / zc; v = H / 2 + FOC * (d @ self.down) / zc
        return u, v, FOC / zc         # px per mét tại điểm đó

    def unproj(self, u, v):
        u = np.asarray(u, float); v = np.asarray(v, float)
        dr = self.look[None] + ((u - W / 2) / FOC)[:, None] * self.right[None] + ((v - H / 2) / FOC)[:, None] * self.down[None]
        t = -self.C[2] / dr[:, 2]
        return self.C[None, :2] + t[:, None] * dr[:, :2]

    def coeffs(self, A=(1, 0, 0, 0, 1, 0), size=(W, H), off=(0, 0)):
        """hệ số PERSPECTIVE của PIL: toạ độ màn hình -> toạ độ ảnh nguồn (map xy qua affine A)"""
        ou, ov = off; sw, sh = size
        scr = np.array([[ou, ov], [ou + sw, ov], [ou + sw, ov + sh], [ou, ov + sh]], float)
        m = self.unproj(scr[:, 0], scr[:, 1])
        src = np.c_[A[0] * m[:, 0] + A[1] * m[:, 1] + A[2], A[3] * m[:, 0] + A[4] * m[:, 1] + A[5]]
        M = []; b = []
        for (x, y), (X, Y) in zip(scr - [ou, ov], src):
            M.append([x, y, 1, 0, 0, 0, -X * x, -X * y]); b.append(X)
            M.append([0, 0, 0, x, y, 1, -Y * x, -Y * y]); b.append(Y)
        return np.linalg.solve(np.array(M), np.array(b))

    def screen_angle(self, x, y, heading):
        """góc trên màn hình (độ, ngược chiều kim đồng hồ) của hướng heading (rad, trên bản đồ)"""
        u0, v0, _ = self.proj([(x, y)]); u1, v1, _ = self.proj([(x + 10 * math.cos(heading), y + 10 * math.sin(heading))])
        return math.degrees(math.atan2(-(v1[0] - v0[0]), u1[0] - u0[0]))


# ============================ textures ============================
MAPS = None
CLOUD = None


def load_maps():
    global MAPS, CLOUD
    if MAPS is None:
        m = Image.open(os.path.join(HERE, "map_full.png")).convert("RGB")
        MAPS = [m, m.resize((m.width // 2, m.height // 2), Image.LANCZOS), m.resize((m.width // 4, m.height // 4), Image.LANCZOS)]
        cp = os.path.join(HERE, "cloud.png")
        if not os.path.exists(cp):
            r = np.random.default_rng(3); sz = (1200, 1600); out = np.zeros(sz, np.float32); amp = 1; tot = 0
            for o in range(6):
                f = 3 * 2 ** o; g = r.standard_normal((f + 3, int(f * 4 / 3) + 3)).astype(np.float32)
                out += amp * np.asarray(Image.fromarray(g).resize((sz[1], sz[0]), Image.BICUBIC)); tot += amp; amp *= 0.5
            out /= tot; c = sstep(0.12, 0.55, out)
            Image.fromarray((c * 255).astype(np.uint8)).save(cp)
        CLOUD = Image.open(cp)
    return MAPS


# ============================ order of battle ============================
def polyline_at(pts, s, off=0.0):
    """điểm trên polyline theo độ dài s + lệch vuông góc off (dương = phía nam/bên phải hướng đi)"""
    pts = np.array(pts, float); seg = np.diff(pts, axis=0); L = np.hypot(*seg.T); cum = np.r_[0, np.cumsum(L)]
    s = np.clip(s, 0, cum[-1]); i = min(np.searchsorted(cum, s, "right") - 1, len(L) - 1)
    u = (s - cum[i]) / L[i]; p = pts[i] + seg[i] * u; d = seg[i] / L[i]
    return p + np.array([-d[1], d[0]]) * off, math.atan2(d[1], d[0])


R1 = GEO["ridge1"]
OHAIN = GEO["roads"]["ohain"]


def s_of_x(x):
    """độ dài dọc đường Ohain gần với hoành độ x"""
    best, bs = 1e9, 0
    for s in np.arange(0, 6000, 10):
        p, _ = polyline_at(OHAIN, s)
        if abs(p[0] - x) < best: best, bs = abs(p[0] - x), s
    return bs


class Unit:
    def __init__(self, kind, keys, std=None):
        self.kind = kind; self.keys = keys; self.std = std    # keys: [(t, x, y, heading, alpha)]

    def at(self, t):
        k = self.keys
        if t <= k[0][0]: return k[0][1:]
        if t >= k[-1][0]: return k[-1][1:]
        for i in range(len(k) - 1):
            if k[i][0] <= t <= k[i + 1][0]:
                u = ease((t - k[i][0]) / (k[i + 1][0] - k[i][0]))
                a, b = k[i][1:], k[i + 1][1:]
                dh = (b[2] - a[2] + math.pi) % (2 * math.pi) - math.pi
                return (lerp(a[0], b[0], u), lerp(a[1], b[1], u), a[2] + dh * u, lerp(a[3], b[3], u))


def build_oob():
    rng = np.random.default_rng(11)
    U = []; STD = []
    face_s = None
    # ---------- quân Liên minh dọc sống núi Mont St Jean ----------
    for x in np.arange(1350, 4350, 95):
        s = s_of_x(x); p, hd = polyline_at(OHAIN, s, -45)
        face = hd + math.pi / 2           # hướng về phía nam (về phía địch)
        kind = "br"
        if 2880 < x < 3300: kind = "nl"      # lữ đoàn Bijlandt
        if 3700 < x < 4100: kind = "hn"
        jitter = rng.uniform(-12, 12)
        U.append(Unit(kind, [(0, p[0], p[1] + jitter, face - math.pi / 2, 1)]))
        p2, _ = polyline_at(OHAIN, s, -260)
        if rng.random() < 0.8:
            U.append(Unit("br" if rng.random() < 0.7 else "hn", [(0, p2[0] + rng.uniform(-20, 20), p2[1], face - math.pi / 2 + rng.uniform(-0.1, 0.1), 1)]))
        # tán binh
        for k in range(2):
            p3, _ = polyline_at(OHAIN, s + k * 45, 150 + rng.uniform(-30, 40))
            U.append(Unit("skb", [(0, p3[0], p3[1], face, 1)]))
    # Bijlandt lùi lại khi Pháp tới gần
    for u in U:
        x, y = u.keys[0][1:3]
        if u.kind == "nl":
            u.keys = [u.keys[0], (13.5, x, y, u.keys[0][3], 1), (17.0, x + 20, y - 170, u.keys[0][3], 1)]
    # sandpit: lính súng trường xanh
    U.append(Unit("rf", [(0, 2905, 1700, -0.35, 1)]))
    # kỵ binh nặng: Household (tây đường lớn) và Union (đông)
    cav = []
    for (cx, cy, nm) in [(2560, 1280, "HOUSEHOLD BDE"), (3180, 1200, "UNION BDE")]:
        for i in range(4):
            for j in range(3):
                x0, y0 = cx + (i - 1.5) * 62 + (j % 2) * 25, cy + j * 38
                cav.append((x0, y0))
                tgt = (x0 + (0 if cx < 3000 else 150) + 60 * (j - 0.5), y0 + 980 + rng.uniform(-40, 40))
                dl = rng.uniform(0, 0.35)
                U.append(Unit("brcav", [(0, x0, y0, 0.0, 1), (18.3 + dl, x0, y0, 0.0, 1), (22.3 + dl, tgt[0], tgt[1], 0.0, 1), (24, tgt[0] + rng.uniform(-20, 20), tgt[1] + 90, 0.0, 1)]))
        STD.append(dict(kind="union", label=nm, keys=[(0, cx + 140, cy + 20), (18.6, cx + 140, cy + 20), (22.3, cx + 140 + (0 if cx < 3000 else 150), cy + 1000)]))
    # pháo binh Liên minh
    for x in (1900, 2350, 2700, 3350, 3800):
        s = s_of_x(x); p, hd = polyline_at(OHAIN, s, 30)
        U.append(Unit("gun", [(0, p[0], p[1], hd + math.pi / 2, 1)]))
    # cờ hiệu Liên minh
    for (x, off, kind, lab) in [(1650, -200, "union", "1ST BRIGADE"), (2150, -330, "union", "3RD DIVISION"), (2480, -180, "union", "2ND BRIGADE"),
                                (3050, -330, "dutch", "2ND DIVISION"), (3450, -240, "union", "5TH DIVISION"), (3950, -300, "hanover", "HANOVER"),
                                (2620, -480, "portrait:wellington", "WELLINGTON")]:
        s = s_of_x(x); p, _ = polyline_at(OHAIN, s, off)
        STD.append(dict(kind=kind, label=lab, keys=[(0, p[0], p[1])]))
    # ---------- Pháp ----------
    # Quân đoàn I (d'Erlon): 4 sư đoàn đội hình cột
    divs = [(3080, 2200, "1ST DIVISION"), (3420, 2120, "2ND DIVISION"), (3760, 2030, "3RD DIVISION"), (4080, 1950, "4TH DIVISION")]
    adv = []
    for di, (dx, dy, lab) in enumerate(divs):
        # mục tiêu: sống núi phía bắc
        s = s_of_x(dx - 60); tp, _ = polyline_at(OHAIN, s, 150)
        vx, vy = tp[0] - dx, tp[1] - dy; L = math.hypot(vx, vy); hx, hy = vx / L, vy / L
        hd = math.atan2(hy, hx) - math.pi / 2       # thanh nằm ngang so với hướng tiến
        adv.append(((dx, dy), (tp[0], tp[1])))
        for r in range(3):
            for c in range(3):
                ox = (c - 1) * 82 + (r % 2) * 22; oy = r * 50 + rng.uniform(-6, 6)
                x0 = dx + ox * math.cos(hd) - oy * hx; y0 = dy + ox * math.sin(hd) - oy * hy
                travel = L - 40 - r * 5
                x1, y1 = x0 + hx * travel, y0 + hy * travel
                back = 380 + rng.uniform(0, 260) + (60 if di in (1, 2) else 0)
                bx, by = x1 - hx * back + rng.uniform(-60, 60), y1 - hy * back + rng.uniform(-40, 40)
                gone = 0.0 if (di in (1, 2) and rng.random() < 0.35) else 1.0
                d0 = 8.8 + 0.25 * di + rng.uniform(0, 0.4)
                U.append(Unit("fr", [(0, x0, y0, hd, 1), (d0, x0, y0, hd, 1), (17.6, x1, y1, hd, 1), (19.4, x1 - hx * 25, y1 - hy * 25, hd, 1),
                                     (22.8, bx, by, hd + rng.uniform(-0.6, 0.6), gone), (24, bx - hx * 30, by - hy * 30, hd, gone)]))
        # tán binh phía trước
        for k in range(6):
            x0 = dx + (k - 2.5) * 30 * math.cos(hd) + hx * 120; y0 = dy + (k - 2.5) * 30 * math.sin(hd) + hy * 120
            x1, y1 = x0 + hx * (L - 180), y0 + hy * (L - 180)
            U.append(Unit("skf", [(0, x0, y0, 0, 1), (8.6, x0, y0, 0, 1), (16.8, x1, y1, 0, 1), (19.5, x1, y1, 0, 0.0)]))
        sx, sy = dx - hx * 230, dy - hy * 230
        STD.append(dict(kind="france", label=lab, keys=[(0, sx, sy), (9.0, sx, sy), (17.6, sx + hx * (L - 100), sy + hy * (L - 100)),
                                                         (22.8, sx + hx * (L - 520), sy + hy * (L - 520))]))
    STD.append(dict(kind="portrait:derlon", label="D'ERLON", keys=[(0, 3500, 2420), (9.5, 3500, 2420), (17.6, 3480, 2050)]))
    STD.append(dict(kind="france", label="I CORPS", keys=[(0, 3260, 2400), (9.5, 3260, 2400), (17.6, 3250, 2080)]))
    # đại pháo đội trước quân đoàn I
    for i in range(9):
        x = 3000 + i * 130; y = 2170 - i * 32 - 60
        U.append(Unit("gun", [(0, x, y, -math.pi / 2 - 0.25, 1)]))
    # Quân đoàn II quanh Hougoumont
    for (x, y) in [(1850, 2420), (1930, 2470), (2250, 2480), (2330, 2520), (2450, 2420), (1780, 2560), (2150, 2650), (2240, 2680),
                   (2560, 2600), (2640, 2650)]:
        U.append(Unit("fr", [(0, x + rng.uniform(-15, 15), y, -0.2 + rng.uniform(-0.2, 0.2), 1)]))
    for i in range(14):
        a = rng.uniform(0, 6.28); r = rng.uniform(150, 210)
        U.append(Unit("skf", [(0, 2050 + r * math.cos(a), 2290 + r * math.sin(a) * 0.9, 0, 1)]))
    STD.append(dict(kind="france", label="II CORPS", keys=[(0, 2300, 2760)]))
    # kỵ binh Milhaud
    for (x, y) in [(3950, 2330), (4030, 2310), (4110, 2290), (3970, 2390), (4050, 2370), (4130, 2350), (2650, 2850), (2730, 2830), (2810, 2810)]:
        U.append(Unit("frcav", [(0, x, y, -0.25, 1)]))
    STD.append(dict(kind="france", label="IV CAV. CORPS", keys=[(0, 4180, 2440)]))
    # Cận vệ / dự bị dọc đường lớn
    for i in range(6):
        U.append(Unit("frg", [(0, 2990 + (i % 2) * 70, 2700 + (i // 2) * 60, -0.05, 1)]))
    STD.append(dict(kind="portrait:napoleon", label="NAPOLEON", keys=[(0, 2900, 2560)]))
    return U, STD, adv


UNITS, STDS, ADV = build_oob()

# ============================ sprites ============================
PPM = 4  # px trên mét cho sprite gốc
COL = {"br": (215, 22, 22), "hn": (225, 60, 50), "nl": (235, 115, 30), "fr": (28, 58, 205), "frg": (20, 40, 150),
       "frcav": (245, 245, 250), "brcav": (190, 20, 25), "rf": (30, 110, 50)}
_spr = {}


def bar_tex(kind):
    """thanh tiểu đoàn: 2 thanh song song có sọc chéo, khối 3D"""
    if kind in _spr: return _spr[kind]
    L, Wd, gap, th = (40, 8, 4, 2.4) if kind not in ("brcav", "frcav") else (30, 7, 5, 2.2)
    if kind == "rf": L = 22
    w, h = int(L * PPM) + 8, int((2 * Wd + gap + th) * PPM) + 8
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    base = COL[kind]; dark = tuple(int(c * 0.55) for c in base)
    for b in range(2):
        y0 = 4 + b * (Wd + gap) * PPM; x0 = 4
        # mặt bên (độ dày)
        d.rectangle((x0, y0 + Wd * PPM, x0 + L * PPM, y0 + (Wd + th) * PPM), fill=dark + (255,))
        top = Image.new("RGBA", (int(L * PPM), int(Wd * PPM)), base + (255,)); td = ImageDraw.Draw(top)
        ww, hh = top.size; sw = int(PPM * 1.6)
        if kind in ("frcav",):
            td.rectangle((0, 0, ww, hh), fill=(240, 240, 245, 255))
            td.line([(0, hh), (ww * 0.45, 0)], fill=(30, 60, 200, 255), width=sw * 2); td.line([(ww * 0.55, hh), (ww, 0)], fill=(30, 60, 200, 255), width=sw * 2)
        elif kind == "hn":
            td.rectangle((0, hh / 2 - sw / 2, ww, hh / 2 + sw / 2), fill=(250, 245, 240, 255))
            for k in range(1, 4): td.rectangle((ww * k / 4 - sw / 2, 0, ww * k / 4 + sw / 2, hh), fill=(250, 245, 240, 255))
        elif kind == "rf":
            td.line([(0, hh), (ww, 0)], fill=(230, 230, 220, 255), width=sw)
        else:
            if kind in ("fr", "frg"):
                for k in range(2):
                    a0 = ww * k / 2; a1 = ww * (k + 1) / 2
                    td.line([(a0, 0), (a1, hh)], fill=(248, 248, 250, 255), width=sw); td.line([(a0, hh), (a1, 0)], fill=(248, 248, 250, 255), width=sw)
            else:
                td.polygon([(ww * 0.36, hh), (ww * 0.50, hh), (ww * 0.64, 0), (ww * 0.50, 0)], fill=(250, 250, 250, 255))
                td.polygon([(ww * 0.05, hh), (ww * 0.12, hh), (ww * 0.26, 0), (ww * 0.19, 0)], fill=(250, 250, 250, 255))
        # chiếu sáng: mép trên sáng
        g = np.asarray(top).astype(np.float32)
        yy = np.linspace(1.18, 0.88, hh)[:, None, None]; g[..., :3] *= yy
        top = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8))
        im.alpha_composite(top, (x0, int(y0)))
        d.rectangle((x0, y0, x0 + L * PPM, y0 + (Wd + th) * PPM), outline=(20, 15, 15, 200), width=2)
    _spr[kind] = im
    return im


def gun_tex():
    if "gun" in _spr: return _spr["gun"]
    G = 1.6
    im = Image.new("RGBA", (int(60 * PPM), int(18 * PPM)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(3):
        x = 4 + k * 19 * PPM
        d.rectangle((x, 6 * PPM, x + 10 * PPM, 11 * PPM), fill=(120, 95, 65, 255), outline=(30, 22, 15, 255), width=2)
        d.rectangle((x + 9 * PPM, 7.2 * PPM, x + 17 * PPM, 9.8 * PPM), fill=(140, 140, 145, 255), outline=(30, 30, 30, 255), width=2)
        for wy in (3.5, 12.5):
            d.ellipse((x + 3 * PPM, wy * PPM, x + 7 * PPM, wy * PPM + 2.2 * PPM), fill=(70, 55, 40, 255), outline=(25, 18, 10, 255))
    _spr["gun"] = im; return im


def pin_tex(kind):
    """tán binh: ghim nhỏ đứng"""
    if kind in _spr: return _spr[kind]
    c = (200, 30, 28) if kind == "skb" else (30, 60, 210)
    im = Image.new("RGBA", (40, 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(20, 6), (33, 62), (20, 50), (7, 62)], fill=c + (255,), outline=(250, 250, 250, 255))
    d.ellipse((15, 0, 25, 10), fill=(240, 235, 225, 255), outline=(30, 20, 20, 255))
    _spr[kind] = im; return im


def shadowed(im, ang, scale, sh_off=(5, 6)):
    """xoay + co giãn + bóng đổ"""
    if scale <= 0: return None
    w, h = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    r = im.resize((w, h), Image.LANCZOS).rotate(ang, Image.BICUBIC, expand=True)
    pad = 12
    out = Image.new("RGBA", (r.width + pad * 2, r.height + pad * 2), (0, 0, 0, 0))
    a = r.split()[3]
    shp = Image.new("L", out.size, 0); shp.paste(a, (pad + int(sh_off[0] * scale * 4), pad + int(sh_off[1] * scale * 4)))
    shp = shp.filter(ImageFilter.GaussianBlur(max(0.8, 2.2 * scale * 4 / 4)))
    sh = Image.new("RGBA", out.size, (20, 22, 8, 0)); sh.putalpha(shp.point(lambda v: int(v * 0.55)))
    out.alpha_composite(sh); out.alpha_composite(r, (pad, pad))
    return out


_cache = {}


def unit_sprite(kind, ang, scale):
    key = (kind, int(round(ang / 3.0)) * 3, round(scale, 3) if scale < 0.2 else round(scale / 0.01) * 0.01)
    if key not in _cache:
        tex = gun_tex() if kind == "gun" else bar_tex(kind)
        _cache[key] = shadowed(tex, key[1], key[2])
        if len(_cache) > 3000: _cache.clear()
    return _cache[key]


# ---------- cờ hiệu ----------
def flag_img(kind):
    w, h = 150, 104
    im = Image.new("RGBA", (w, h), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
    if kind == "union":
        d.rectangle((0, 0, w, h), fill=(16, 38, 110))
        for (a, b) in [((0, 0), (w, h)), ((0, h), (w, 0))]:
            d.line([a, b], fill=(255, 255, 255), width=20)
        for (a, b) in [((0, 0), (w, h)), ((0, h), (w, 0))]:
            d.line([a, b], fill=(205, 20, 40), width=7)
        d.rectangle((w / 2 - 17, 0, w / 2 + 17, h), fill=(255, 255, 255)); d.rectangle((0, h / 2 - 17, w, h / 2 + 17), fill=(255, 255, 255))
        d.rectangle((w / 2 - 10, 0, w / 2 + 10, h), fill=(205, 20, 40)); d.rectangle((0, h / 2 - 10, w, h / 2 + 10), fill=(205, 20, 40))
    elif kind == "france":
        for i, c in enumerate([(20, 50, 160), (250, 250, 248), (215, 25, 35)]):
            d.rectangle((i * w / 3, 0, (i + 1) * w / 3, h), fill=c)
        f = F(CORM, 11)
        for j, s in enumerate(["VALEUR", "ET", "DISCIPLINE"]):
            d.text((w / 2, 38 + j * 13), s, font=f, fill=(205, 175, 95), anchor="mm")
        d.rectangle((0, 0, w - 1, h - 1), outline=(200, 160, 50), width=3)
    elif kind == "dutch":
        for i, c in enumerate([(200, 30, 40), (250, 250, 248), (25, 60, 150)]):
            d.rectangle((0, i * h / 3, w, (i + 1) * h / 3), fill=c)
    elif kind == "hanover":
        d.rectangle((0, 0, w, h), fill=(205, 25, 35))
        horse = [(40, 75), (48, 52), (60, 45), (88, 45), (98, 30), (104, 22), (112, 26), (108, 38), (102, 50), (104, 78), (97, 78), (95, 60),
                 (68, 60), (62, 80), (55, 80), (56, 62), (48, 66), (46, 80)]
        d.polygon(horse, fill=(250, 248, 240))
    elif kind.startswith("portrait:"):
        nm = kind.split(":")[1]
        p = Image.open(os.path.join(HERE, "img", nm + ".jpg")).convert("RGB")
        box = {"wellington": (0.22, 0.04, 0.80, 0.42), "napoleon": (0.30, 0.03, 0.66, 0.28), "derlon": (0.24, 0.05, 0.78, 0.45)}[nm]
        pw, ph = p.size; c = p.crop((int(box[0] * pw), int(box[1] * ph), int(box[2] * pw), int(box[3] * ph)))
        im = c.resize((w, int(w * 0.95)), Image.LANCZOS).convert("RGBA"); d = ImageDraw.Draw(im); h = im.height
        d.rectangle((0, 0, w - 1, h - 1), outline=(40, 30, 20), width=4)
    # nếp gấp vải
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    if not kind.startswith("portrait"):
        xx = np.arange(a.shape[1])[None, :, None]
        a[..., :3] *= 1 + 0.10 * np.sin(xx / a.shape[1] * 2 * math.pi * 1.6 + 0.7)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def std_tex(kind, label):
    key = ("std", kind, label)
    if key in _spr: return _spr[key]
    fl = flag_img(kind)
    side = (40, 60, 160) if kind in ("france",) or kind in ("portrait:napoleon", "portrait:derlon") else (190, 30, 30)
    fw, fh = fl.size
    plate_h = 26
    tw = max(fw, 0)
    pole = 40
    im = Image.new("RGBA", (fw + 20, fh + plate_h + pole + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0 = 10; y0 = 14
    # biển tên
    d.rectangle((x0 - 2, y0, x0 + fw + 2, y0 + plate_h), fill=(245, 242, 235), outline=side, width=3)
    f = F(BARLOW, 17)
    d.text((x0 + fw / 2, y0 + plate_h / 2 + 1), label, font=f, fill=(30, 25, 25), anchor="mm")
    d.ellipse((x0 + fw / 2 - 5, y0 - 10, x0 + fw / 2 + 5, y0), fill=(200, 160, 60) if side[2] > 100 else (90, 90, 95), outline=(40, 30, 10))
    im.alpha_composite(fl, (x0, y0 + plate_h + 2))
    d.rectangle((x0 - 1, y0 + plate_h + 1, x0 + fw, y0 + plate_h + fh + 2), outline=(25, 20, 20), width=2)
    # cán cờ
    d.rectangle((x0 + fw / 2 - 2, y0 + plate_h + fh + 2, x0 + fw / 2 + 2, im.height - 2), fill=(70, 60, 50))
    _spr[key] = (im, (x0 + fw / 2, im.height - 2))
    return _spr[key]


def std_sprite(kind, label, scale):
    key = ("stdc", kind, label, round(scale / 0.01) * 0.01)
    if key not in _cache:
        im, (ax, ay) = std_tex(kind, label)
        sc = key[3]
        w, h = max(1, int(im.width * sc)), max(1, int(im.height * sc))
        r = im.resize((w, h), Image.LANCZOS)
        # bóng đổ xuống mặt đất, lệch phải-xuống
        a = r.split()[3]
        shw = int(w + h * 0.9); shh = int(h * 0.55)
        sh_l = a.transform((shw, shh), Image.AFFINE, (1, -h * 0.9 / shh * 0 - 0.9 * h / shh * 0, 0, 0, 1 / 0.55, 0), Image.BILINEAR) if False else None
        sha = a.resize((w, int(h * 0.42)))
        shim = Image.new("L", (w + int(h * 0.75), int(h * 0.42) + 6), 0)
        # nghiêng (shear) để bóng đổ chéo
        shear = sha.transform((shim.width, shim.height), Image.AFFINE, (1, -h * 0.75 / sha.height * 1.0, h * 0.75 * 0, 0, 1, 0), Image.BILINEAR)
        shim.paste(shear, (0, 0))
        shim = shim.filter(ImageFilter.GaussianBlur(max(1, 3 * sc)))
        _cache[key] = (r, (ax * sc, ay * sc), shim)
    return _cache[key]


# ---------- khói ----------
def smoke_tex():
    if "smoke" in _spr: return _spr["smoke"]
    n = 128; r = np.random.default_rng(5)
    yy, xx = np.mgrid[0:n, 0:n] / n - 0.5
    acc = np.zeros((n, n))
    for k in range(9):
        cx, cy, rr = r.uniform(-0.18, 0.18), r.uniform(-0.18, 0.18), r.uniform(0.12, 0.22)
        acc = np.maximum(acc, np.clip(1 - np.hypot(xx - cx, yy - cy) / rr, 0, 1))
    acc = sstep(0, 0.6, acc)
    lit = np.clip(1.0 - 0.9 * (xx + yy), 0.6, 1.25)
    rgb = np.stack([248 * lit, 246 * lit, 238 * lit], -1)
    im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), acc * 235]).astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(1.5))
    _spr["smoke"] = im; return im


# ============================ events ============================
def smoke_events():
    r = np.random.default_rng(21); ev = []
    # đại pháo đội bắn 0-10s
    for t in np.arange(0.2, 10.5, 0.22):
        i = r.integers(0, 9); x = 3000 + i * 130 + r.uniform(-15, 15); y = 2170 - i * 32 - 60 - 40
        ev.append((t, x, y, r.uniform(16, 26)))
    # Hougoumont cháy liên tục
    for t in np.arange(0, 24, 0.35):
        ev.append((t, 2050 + r.uniform(-40, 40), 2240 + r.uniform(-30, 30), r.uniform(18, 30)))
    # tuyến Anh bắn khi Pháp tới
    for t in np.arange(14.0, 19.5, 0.08):
        x = r.uniform(2950, 4150); s = s_of_x(x); p, _ = polyline_at(OHAIN, s, r.uniform(20, 120))
        ev.append((t, p[0], p[1], r.uniform(12, 22)))
    # pháo Anh
    for t in np.arange(4, 18, 0.5):
        x = r.choice([1900, 2350, 2700, 3350, 3800]); s = s_of_x(x); p, _ = polyline_at(OHAIN, s, 60)
        ev.append((t, p[0] + r.uniform(-10, 10), p[1], r.uniform(14, 22)))
    return ev


SMOKE = smoke_events()
CHURN = []
for (a, b) in ADV:
    for k in range(10):
        u = k / 9
        CHURN.append((lerp(a[0], b[0], 0.55 + 0.45 * u), lerp(a[1], b[1], 0.55 + 0.45 * u), 150, 15.5 + 1.5 * u))
for i in range(9):
    CHURN.append((3000 + i * 130, 2170 - i * 32 - 60, 90, 2.0 + i * 0.3))
CHURN.append((2050, 2260, 260, 0.0))
ARROWS = [  # (start, end, width, t0 grow, t1 full, t2 fade start, t3 gone, curve)
]
for (a, b) in ADV:
    s = (a[0] - (b[0] - a[0]) * 0.05, a[1] - (b[1] - a[1]) * 0.05)
    e = (lerp(a[0], b[0], 0.86), lerp(a[1], b[1], 0.86))
    ARROWS.append(dict(p=[s, e], w=95, t=(9.0 + 0.25 * len(ARROWS), 11.6 + 0.25 * len(ARROWS), 15.2, 16.4)))
ARROWS.append(dict(p=[(2560, 1350), (2600, 1700), (2760, 2050), (2830, 2250)], w=80, t=(18.4, 20.6, 22.3, 23.3)))
ARROWS.append(dict(p=[(3180, 1260), (3260, 1650), (3380, 2000), (3450, 2220)], w=80, t=(18.6, 20.8, 22.3, 23.3)))
RINGS = [dict(c=(3560, 2140), r=560, w=34, t=(5.0, 6.1, 7.6, 8.4)),
         dict(c=(2860, 1745), r=120, w=16, t=(17.6, 18.3, 19.8, 20.4)), dict(c=(4210, 1610), r=120, w=16, t=(17.9, 18.6, 19.8, 20.4))]
CLOCK = [(0, "13:00"), (4.4, "13:30"), (17.2, "14:00")]
LABELS = [("Mont St Jean", "Mont St. Jean", (40, -95)), ("La Haye Sainte", "La Haye Sainte", (-170, 10)), ("Papelotte", "Papelotte", (0, 60)),
          ("La Haye", "La Haye", (40, -60)), ("Frischermont", "Frischermont", (60, 60)), ("Hougoumont", "Hougoumont", (-170, -120)),
          ("La Belle Alliance", "La Belle Alliance", (0, 80)), ("Plancenoit", "Plancenoit", (0, 150)), ("Merbe Braine", "Merbe Braine", (0, -80)),
          ("Braine l'Alleud", "Braine l'Alleud", (0, 130)), ("Waterloo", "Waterloo", (0, -110)), ("Rossomme", "Rossomme", (90, 0)),
          ("Maransart", "Maransart", (0, 100))]


# ============================ ground rasters ============================
def ground_layer(cam, draw_fn, bbox, res):
    """vẽ một lớp trong không gian bản đồ (bbox mét, res m/px) rồi chiếu ra màn hình"""
    x0, y0, x1, y1 = bbox
    w, h = int((x1 - x0) / res), int((y1 - y0) / res)
    if w < 2 or h < 2: return None
    lay = draw_fn(w, h)
    if lay is None: return None
    co = cam.coeffs(A=(1 / res, 0, -x0 / res, 0, 1 / res, -y0 / res))
    return lay.transform((W, H), Image.PERSPECTIVE, tuple(co), Image.BILINEAR)


def arrow_layer(cam, ar, t):
    t0, t1, t2, t3 = ar["t"]
    if t < t0 or t > t3: return None
    grow = ease((t - t0) / (t1 - t0)); fade = 1 - ease((t - t2) / (t3 - t2))
    pts = np.array(ar["p"], float)
    if len(pts) > 2:   # làm mượt đường cong
        from scipy.interpolate import splprep, splev
        tck, _ = splprep(pts.T, s=0, k=min(3, len(pts) - 1)); uu = np.linspace(0, 1, 60); pts = np.array(splev(uu, tck)).T
    seg = np.diff(pts, axis=0); Ls = np.hypot(*seg.T); cum = np.r_[0, np.cumsum(Ls)]; Ltot = cum[-1]
    Lc = max(1.0, Ltot * grow)
    wsh = ar["w"]; hw = wsh * 1.9 / 2; hl = wsh * 1.55
    pad = hw + 30
    x0, y0 = pts[:, 0].min() - pad, pts[:, 1].min() - pad; x1, y1 = pts[:, 0].max() + pad, pts[:, 1].max() + pad
    res = 2.0

    def draw(w, h):
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); X = x0 + xx * res; Y = y0 + yy * res
        best = np.full(X.shape, 1e9, np.float32); tpar = np.zeros(X.shape, np.float32); side = np.zeros(X.shape, np.float32)
        for i in range(len(seg)):
            ax, ay = pts[i]; vx, vy = seg[i]; L2 = Ls[i] ** 2
            u = np.clip(((X - ax) * vx + (Y - ay) * vy) / L2, 0, 1)
            dx, dy = X - ax - u * vx, Y - ay - u * vy; dd = np.hypot(dx, dy)
            m = dd < best; best = np.where(m, dd, best); tpar = np.where(m, cum[i] + u * Ls[i], tpar)
        # nửa bề rộng theo t (thân + đầu mũi tên ở vị trí Lc)
        hwid = np.where(tpar < Lc - hl, wsh / 2, hw * np.clip((Lc - tpar) / hl, 0, 1))
        inside = hwid - best
        a_shape = sstep(-2.5, 2.5, inside) * (tpar <= Lc + 0.5)
        tail = sstep(0, 0.55, tpar / max(Lc, 1))
        g = 0.30 + 0.70 * np.clip(tpar / max(Lc, 1), 0, 1) ** 1.3
        r_ = np.random.default_rng(int(Ltot))
        nz = np.asarray(Image.fromarray(r_.standard_normal((h // 6 + 2, w // 6 + 2)).astype(np.float32)).resize((w, h), Image.BICUBIC))
        streak = 0.92 + 0.08 * nz
        alpha = a_shape * (0.45 + 0.50 * g) * tail * fade
        glow = sstep(-26, 0, inside) * (1 - a_shape) * 0.22 * fade * tail * (tpar <= Lc - 1) * (best < hw + 30)
        col = np.stack([255 * streak, 246 * streak, 190 * streak], -1)
        al = np.clip(alpha + glow, 0, 1)
        return Image.fromarray(np.dstack([np.clip(col, 0, 255), al * 255]).astype(np.uint8), "RGBA")
    return ground_layer(cam, draw, (x0, y0, x1, y1), res)


def ring_layer(cam, rg, t):
    t0, t1, t2, t3 = rg["t"]
    if t < t0 or t > t3: return None
    sweep = ease((t - t0) / (t1 - t0)); fade = 1 - ease((t - t2) / (t3 - t2))
    cx, cy = rg["c"]; R = rg["r"]; wd = rg["w"]; pad = wd * 3 + 20; res = max(1.0, R / 300)

    def draw(w, h):
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); X = cx - R - pad + xx * res; Y = cy - R - pad + yy * res
        r = np.hypot(X - cx, Y - cy); ang = (np.arctan2(Y - cy, X - cx) + math.pi / 2) % (2 * math.pi) / (2 * math.pi)
        band = sstep(-wd / 2 - 2 * res, -wd / 2 + 2 * res, -(np.abs(r - R)))
        glow = np.exp(-((np.abs(r - R) - wd / 2).clip(0) / (wd * 0.9)) ** 2) * 0.35
        show = sstep(sweep - 0.012, sweep, -ang + 2 * sweep - sweep) if False else (ang <= sweep).astype(np.float32)
        show = np.clip((sweep - ang) / 0.01, 0, 1)
        core = np.exp(-((r - R) / (wd * 0.22)) ** 2)
        al = np.clip(band * 0.80 + glow, 0, 1) * show * fade
        col = np.stack([250 + 5 * core, 236 + 19 * core, 160 + 70 * core], -1)
        return Image.fromarray(np.dstack([np.clip(col, 0, 255), al * 255]).astype(np.uint8), "RGBA")
    return ground_layer(cam, draw, (cx - R - pad, cy - R - pad, cx + R + pad, cy + R + pad), res)


def churn_layer(cam, t):
    res = 6.0; x0, y0, x1, y1 = 1500, 1000, 4700, 2900

    def draw(w, h):
        im = Image.new("L", (w, h), 0); d = ImageDraw.Draw(im)
        for (x, y, r, ts) in CHURN:
            a = ease((t - ts) / 2.5)
            if a <= 0: continue
            rr = r / res
            d.ellipse(((x - x0) / res - rr, (y - y0) / res - rr * 0.8, (x - x0) / res + rr, (y - y0) / res + rr * 0.8), fill=int(255 * a))
        if im.getbbox() is None: return None
        im = im.filter(ImageFilter.GaussianBlur(6))
        nz = np.asarray(Image.open(os.path.join(HERE, "cloud.png")).resize((w, h)), np.float32) / 255
        a = np.asarray(im, np.float32) / 255 * (0.55 + 0.45 * nz)
        col = np.zeros((h, w, 3)) + np.array([92, 66, 40])
        return Image.fromarray(np.dstack([col, a * 0.62 * 255]).astype(np.uint8), "RGBA")
    return ground_layer(cam, draw, (x0, y0, x1, y1), res)



# ============================ đặt sprite mượt dưới mức pixel ============================
_mip = {}


def mip(tex, L):
    key = (id(tex), L)
    if key not in _mip:
        im = tex
        for _ in range(L):
            im = im.resize((max(1, im.width // 2), max(1, im.height // 2)), Image.LANCZOS)
        _mip[key] = im
    return _mip[key]


def blit(img, tex, anchor, uv, scale, ang=0.0, alpha=1.0, M=None, shadow=None, tint=None):
    """vẽ tex lên img: điểm anchor của tex nằm tại uv (float), co giãn scale, xoay ang độ (ngược kim đồng hồ),
    M = ma trận 2x2 thêm (bóng đổ nghiêng). shadow=(dx, dy, blur, opacity) theo px màn hình."""
    if scale <= 0.003 or alpha <= 0.003: return
    L = 0
    while scale * 2 ** (L + 1) < 1.0 and L < 6: L += 1
    T = mip(tex, L); s = scale * 2 ** L; ax, ay = anchor[0] / 2 ** L, anchor[1] / 2 ** L
    c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    F_ = np.array([[c, sn], [-sn, c]]) * s
    if M is not None: F_ = np.array(M) @ F_
    Fi = np.linalg.inv(F_)
    corners = np.array([[0, 0], [T.width, 0], [T.width, T.height], [0, T.height]], float) - [ax, ay]
    P = corners @ F_.T + uv
    pad = 3 + (int(abs(shadow[0]) + abs(shadow[1]) + 3 * shadow[2]) + 2 if shadow else 0)
    ox, oy = int(math.floor(P[:, 0].min())) - pad, int(math.floor(P[:, 1].min())) - pad
    ex, ey = int(math.ceil(P[:, 0].max())) + pad, int(math.ceil(P[:, 1].max())) + pad
    if ex < 0 or ey < 0 or ox > img.width or oy > img.height: return
    w, h = ex - ox, ey - oy
    # canvas (x,y) -> tex: q = anchor + Fi @ (p - uv),  p = (x+ox, y+oy)
    a, b = Fi[0]; d, e = Fi[1]
    cx = ax + a * (ox - uv[0]) + b * (oy - uv[1]); cy = ay + d * (ox - uv[0]) + e * (oy - uv[1])
    lay = T.transform((w, h), Image.AFFINE, (a, b, cx, d, e, cy), Image.BICUBIC)
    if tint is not None:
        sh_ = Image.new("RGBA", lay.size, tint + (0,)); sh_.putalpha(lay.split()[3]); lay = sh_
    if alpha < 1:
        lay.putalpha(lay.split()[3].point(lambda v: int(v * alpha)))
    if shadow:
        dx, dy, bl, op = shadow
        sa = lay.split()[3]
        sa = sa.transform(sa.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy), Image.BILINEAR).filter(ImageFilter.GaussianBlur(max(0.6, bl)))
        sh = Image.new("RGBA", lay.size, (20, 22, 8, 0)); sh.putalpha(sa.point(lambda v: int(v * op)))
        sh.alpha_composite(lay); lay = sh
    # cắt phần ngoài khung
    sx0, sy0 = max(0, -ox), max(0, -oy)
    sx1, sy1 = min(w, img.width - ox), min(h, img.height - oy)
    if sx1 <= sx0 or sy1 <= sy0: return
    img.alpha_composite(lay, (ox + sx0, oy + sy0), (sx0, sy0, sx1, sy1))


_lab = {}


def label_tex(txt):
    if txt not in _lab:
        f = F(CORM, 64)
        lay = Image.new("RGBA", (int(f.getlength(txt)) + 60, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((lay.width / 2 + 2, 64), txt, font=f, fill=(10, 8, 0, 235), anchor="mm")
        lay = lay.filter(ImageFilter.GaussianBlur(6)); d = ImageDraw.Draw(lay)
        d.text((lay.width / 2, 60), txt, font=f, fill=(246, 242, 228, 255), anchor="mm")
        _lab[txt] = lay
    return _lab[txt]

# ============================ frame ============================
def text_shadow(img, xy, s, font, fill, anchor="mm", blur=3, op=200, off=(2, 2)):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((xy[0] + off[0], xy[1] + off[1]), s, font=font, fill=(10, 8, 0, op), anchor=anchor)
    lay = lay.filter(ImageFilter.GaussianBlur(blur)); d = ImageDraw.Draw(lay)
    d.text(xy, s, font=font, fill=fill, anchor=anchor)
    img.alpha_composite(lay)


def clock(img, t):
    cur = [c for c in CLOCK if c[0] <= t]
    s_now = cur[-1][1]; tc = cur[-1][0]
    prev = cur[-2][1] if len(cur) > 1 else None
    a = ease((t - tc) / 0.45) if prev else 1.0
    for s, op in ([(prev, 1 - a)] if prev and a < 1 else []) + [(s_now, a)]:
        if op <= 0.01: continue
        f = F(OSWALD, 92)
        lay = Image.new("RGBA", (420, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((400, 80), s, font=f, anchor="rm", fill=(0, 0, 0, 255))
        msk = lay.split()[3]
        grad = Image.linear_gradient("L").resize((420, 160)).point(lambda v: int(232 - v * 0.42))
        face = Image.merge("RGBA", (grad, grad, grad, msk))
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(msk.filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * 0.75)))
        edge = Image.new("RGBA", lay.size, (40, 40, 40, 0)); edge.putalpha(msk.filter(ImageFilter.MaxFilter(3)))
        hl = Image.new("RGBA", lay.size, (255, 255, 255, 0)); hl.putalpha(ImageChops.subtract(msk, ImageChops.offset(msk, 0, 2)).point(lambda v: int(v * 0.6)))
        comp = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        comp.alpha_composite(sh, (3, 4)); comp.alpha_composite(edge); comp.alpha_composite(face); comp.alpha_composite(hl)
        if op < 1: comp.putalpha(comp.split()[3].point(lambda v: int(v * op)))
        img.alpha_composite(comp, (W - 420 - 70, 18))


def render(fi):
    t = fi / FPS
    maps = load_maps(); cam = Cam(t)
    # --- địa hình
    _, _, sc = cam.proj([cam.unproj([W / 2], [H / 2])[0]])
    lvl = 0 if sc[0] > 0.62 else (1 if sc[0] > 0.31 else 2)
    m = maps[lvl]; k = 1 / 2 ** lvl
    co = cam.coeffs(A=(k, 0, 0, 0, k, 0))
    img = m.transform((W, H), Image.PERSPECTIVE, tuple(co), Image.BICUBIC).convert("RGBA")
    # --- đất cày xới
    ch = churn_layer(cam, t)
    if ch: img.alpha_composite(ch)
    # --- bóng mây trôi (chỉ phủ mặt đất)
    wind = (t * 38 + 900, t * 14 + 400)
    res = 8.0
    co = cam.coeffs(A=(1 / res, 0, wind[0] / res, 0, 1 / res, wind[1] / res))
    cl = CLOUD.transform((W, H), Image.PERSPECTIVE, tuple(co), Image.BILINEAR)
    a = np.asarray(img).astype(np.float32)
    CL = np.asarray(cl, np.float32)[..., None] / 255
    a[..., :3] *= (1.08 - 0.40 * CL)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    # --- mũi tên + vòng tròn (dưới quân)
    for ar in ARROWS:
        l = arrow_layer(cam, ar, t)
        if l: img.alpha_composite(l)
    for rg in RINGS:
        l = ring_layer(cam, rg, t)
        if l: img.alpha_composite(l)
    # --- quân: sắp xếp theo v (xa trước)
    items = []
    for u in UNITS:
        x, y, hd, al = u.at(t)
        if al <= 0.01: continue
        uu, vv, s = cam.proj([(x, y)])
        if not (-80 < uu[0] < W + 80 and -80 < vv[0] < H + 80): continue
        items.append((vv[0], "u", u, x, y, hd, al, uu[0], s[0]))
    for sd in STDS:
        ks = sd["keys"]
        if len(ks) == 1: x, y = ks[0][1:]
        else:
            x, y = ks[-1][1:]
            for i in range(len(ks) - 1):
                if ks[i][0] <= t <= ks[i + 1][0]:
                    e = ease((t - ks[i][0]) / (ks[i + 1][0] - ks[i][0])); x, y = lerp(ks[i][1], ks[i + 1][1], e), lerp(ks[i][2], ks[i + 1][2], e); break
            if t < ks[0][0]: x, y = ks[0][1:]
        uu, vv, s = cam.proj([(x, y)])
        if not (-200 < uu[0] < W + 200 and -50 < vv[0] < H + 300): continue
        items.append((vv[0] + 1e4, "s", sd, x, y, 0, 1, uu[0], s[0]))
    items.sort(key=lambda it: it[0])
    for it in items:
        _, typ, obj, x, y, hd, al, u0, s = it
        v0 = float(it[0] - (1e4 if typ == "s" else 0)); u0 = float(u0); s = float(s)
        if typ == "u":
            if obj.kind in ("skb", "skf"):
                p = pin_tex(obj.kind)
                blit(img, p, (20, 62), (u0, v0), s * 13 / 70, alpha=al)
                continue
            ang = cam.screen_angle(x, y, hd)
            tex = gun_tex() if obj.kind == "gun" else bar_tex(obj.kind)
            blit(img, tex, (tex.width / 2, tex.height / 2), (u0, v0), s / PPM, ang=ang, alpha=al,
                 shadow=(5 * s, 6 * s, 2.2 * s, 0.55))
        else:
            sc_ = s * 0.56
            tex, (ax, ay) = std_tex(obj["kind"], obj["label"])
            # bóng cờ đổ nghiêng xuống mặt đất
            blit(img, tex, (ax, ay), (u0, v0), sc_, M=[[1, -0.75], [0, 0.42]], tint=(15, 18, 5), alpha=0.42)
            blit(img, tex, (ax, ay), (u0, v0), sc_)
    # --- khói (trên quân)
    st = smoke_tex()
    for (te, x, y, sz) in SMOKE:
        age = t - te
        if age < 0 or age > 3.2: continue
        uu, vv, s = cam.proj([(x + age * 9, y - age * 3)])
        if not (-60 < uu[0] < W + 60 and -60 < vv[0] < H + 60): continue
        grow = 0.55 + 0.45 * (1 - math.exp(-age * 2.2))
        op = min(1, age / 0.12) * (1 - ease((age - 1.2) / 2.0))
        px = sz * s[0] * grow * 2.3
        blit(img, st, (st.width / 2, st.height * 0.65), (float(uu[0]), float(vv[0])), px / st.width, alpha=op * 0.9)
    # --- nhãn địa danh
    for (key, txt, off) in LABELS:
        vx, vy = GEO["villages"][key]
        uu, vv, s = cam.proj([(vx + off[0], vy + off[1])])
        if not (-200 < uu[0] < W + 200 and -40 < vv[0] < H + 40): continue
        fs = max(14.0, 30 * float(s[0]))
        lt = label_tex(txt)
        blit(img, lt, (lt.width / 2, 60), (float(uu[0]), float(vv[0])), fs / 64)
    # --- grade: vignette + ấm + hạt
    a = np.asarray(img).astype(np.float32)[..., :3]
    a *= (1.0 - 0.10 * CL)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r2 = ((xx - W * 0.52) / (W * 0.62)) ** 2 + ((yy - H * 0.55) / (H * 0.66)) ** 2
    vig = 1 - 0.36 * np.clip(r2 - 0.15, 0, 1.6) ** 1.3
    a *= vig[..., None]
    a *= np.array([1.02, 1.0, 0.95])
    a += np.random.default_rng(fi).normal(0, 2.2, (H, W, 1))
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    clock(img, t)
    return img.convert("RGB")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "test":
        os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
        for f in sys.argv[2:]:
            t0 = time.time(); im = render(int(f)); im.save(os.path.join(HERE, "test", f"t_{int(f):04d}.jpg"), quality=92)
            print(f, round(time.time() - t0, 2), flush=True)
    elif mode == "render":
        from multiprocessing import Pool
        s = int(sys.argv[2]) if len(sys.argv) > 2 else 0; e = int(sys.argv[3]) if len(sys.argv) > 3 else NF
        out = os.path.join(HERE, "frames"); os.makedirs(out, exist_ok=True)
        todo = [i for i in range(s, e) if not os.path.exists(os.path.join(out, f"f_{i:04d}.jpg"))]

        def job(i):
            render(i).save(os.path.join(out, f"f_{i:04d}.jpg"), quality=93)
            return i
        with Pool(4) as p:
            for k, i in enumerate(p.imap_unordered(job, todo, chunksize=4)):
                if k % 30 == 0: print("frame", i, k, "/", len(todo), flush=True)
        print("RENDER_DONE")
