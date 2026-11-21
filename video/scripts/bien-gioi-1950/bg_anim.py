"""Dựng hoạt cảnh chiến thuật Waterloo 13:00-14:00 (d'Erlon tấn công, kỵ binh Anh phản kích).
python3 wl_anim.py test 0 300 450 ...   |   python3 wl_anim.py render [start end]
"""
import math, os, sys, json, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(HERE)
AUD_T = [1.0, 9.2, 18.3, 23.4, 30.2, 37.4, 46.2, 54.5]   # mốc bắt đầu 8 câu lời dẫn
W, H = 1920, 1080
FPS = 30
DUR = 62.0
NF = int(DUR * FPS)
FOV = math.radians(36)
FOC = (W / 2) / math.tan(FOV / 2)
OSWALD = os.path.join(S, "gfx", "oswald-700.ttf")
BARLOW = os.path.join(S, "gfx", "barlow-condensed-700.ttf")
CORM = os.path.join(S, "gfx", "dl", "cormsc700.ttf")
GEO = json.load(open(os.path.join(HERE, "geo_old.json")))
GEO_NEW = json.load(open(os.path.join(HERE, "geo.json")))
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
    (0.0, 2950, 2100, 4000, -4, 25), (8.5, 2650, 2150, 3700, -4, 26), (17.5, 2450, 2350, 3300, -3, 26),
    (21.5, 1980, 2330, 2300, -3, 28), (29.0, 1960, 2230, 2250, -3, 28), (35.0, 2150, 1800, 2700, -3, 27),
    (41.0, 2300, 1480, 2150, -2, 28), (50.0, 2350, 1400, 1750, -2, 29), (57.0, 2420, 1620, 2700, -3, 27),
    (62.0, 2700, 1900, 3600, -4, 25)]


def cam_at(t):
    ks = globals()["CAM"]
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



B = (1900, 2350)            # lòng chảo Cốc Xá
P477 = tuple(GEO["p477"])   # điểm cao 477


def appear(t0, x, y, hd, extra=()):
    return [(0, x, y, hd, 0), (t0, x, y, hd, 0), (t0 + 0.6, x, y, hd, 1)] + list(extra)


def build_oob():
    r = np.random.default_rng(5); U = []; STD = []
    # ---------- binh đoàn Le Page trong lòng chảo ----------
    lp = []
    for i in range(11):
        x = B[0] + r.uniform(-330, 330); y = B[1] + r.uniform(-150, 160); hd = r.uniform(-0.5, 0.5)
        lp.append((x, y, hd))
    survivors = {2, 5, 8}
    for i, (x, y, hd) in enumerate(lp):
        if i in survivors:
            path = [(0, x, y, hd, 1), (23.4, x, y, hd, 1), (26.0, x + r.uniform(-30, 30), y + r.uniform(-30, 30), hd + 0.4, 1), (30.4, 2080, 2000 + i * 6, -1.4, 1),
                    (33.5, 2250, 1680 + i * 5, -1.3, 1), (36.6, P477[0] + 60 + i * 10, P477[1] + 70, -1.0, 1),
                    (49.0, P477[0] + 60 + i * 10, P477[1] + 70, -1.0, 1), (51.0, P477[0] + 60 + i * 10, P477[1] + 70, -1.0, 0)]
        else:
            die = r.uniform(24.8, 29.2)
            path = [(0, x, y, hd, 1), (23.4, x, y, hd, 1), (die - 0.8, x + r.uniform(-50, 50), y + r.uniform(-40, 40), hd + r.uniform(-0.9, 0.9), 1),
                    (die, x + r.uniform(-60, 60), y + r.uniform(-50, 50), hd + r.uniform(-1.2, 1.2), 0)]
        U.append(Unit("fl", path))
        for k in range(2):
            ox, oy = r.uniform(-60, 60), r.uniform(-50, 50)
            pk = [(kk[0], kk[1] + ox, kk[2] + oy, kk[3], kk[4]) for kk in path]
            U.append(Unit("skl", pk))
    STD.append(dict(kind="france2", label="LE PAGE", side="fr", keys=[(0, 2020, 2300, 1), (26.0, 2020, 2300, 1), (30.4, 2090, 1990, 1), (33.5, 2260, 1660, 1),
                                                                      (36.6, P477[0] + 140, P477[1] + 40, 1), (56.0, P477[0] + 140, P477[1] + 40, 1), (57.6, P477[0] + 140, P477[1] + 60, 0)]))
    # ---------- binh đoàn Charton trên đường mòn phía bắc ----------
    track = GEO["tracks"]["charton"]
    for i in range(9):
        s0 = 0.12 + i * 0.035
        x0 = lerp(track[1][0], track[2][0], s0 * 2) + r.uniform(-40, 40); y0 = lerp(track[1][1], track[2][1], s0 * 2)
        ang = r.uniform(0, 6.28); rr = r.uniform(60, 230)
        x1, y1 = P477[0] + rr * math.cos(ang), P477[1] + rr * math.sin(ang) * 0.8
        gone = r.uniform(49.2, 52.0)
        path = [(0, x0, y0, 1.2, 1), (2.0, x0, y0, 1.2, 1), (38.5 + r.uniform(0, 1.5), x1, y1, r.uniform(-0.6, 0.6), 1),
                (gone - 0.8, x1 + r.uniform(-30, 30), y1 + r.uniform(-30, 30), r.uniform(-1, 1), 1), (gone, x1, y1, 0, 0)]
        U.append(Unit("fl", path))
        for k in range(2):
            ox, oy = r.uniform(-50, 50), r.uniform(-40, 40)
            U.append(Unit("skl", [(kk[0], kk[1] + ox, kk[2] + oy, kk[3], kk[4]) for kk in path]))
    STD.append(dict(kind="france2", label="CHARTON", side="fr", keys=[(0, 2680, 640, 1), (2.0, 2680, 640, 1), (39.0, P477[0] - 40, P477[1] - 30, 1),
                                                                      (50.0, P477[0] - 40, P477[1] - 30, 1), (51.6, P477[0] - 40, P477[1] - 10, 0)]))
    # ---------- Đại đoàn 308 vây lòng chảo ----------
    ring = []
    for i in range(14):
        a = i / 14 * 2 * math.pi + 0.2
        x = B[0] + 820 * math.cos(a) + r.uniform(-40, 40); y = B[1] + 560 * math.sin(a) + r.uniform(-30, 30)
        if abs(x - 2250) < 120 and y < 1900: continue          # chừa đường mòn phía bắc
        hd = a + math.pi / 2
        t0 = 1.6 + i * 0.42
        U.append(Unit("vn", appear(t0, x, y, hd)))
        for k in range(2):
            U.append(Unit("skv", appear(t0 + 0.2, x + r.uniform(-40, 40) - 90 * math.cos(a), y + r.uniform(-30, 30) - 70 * math.sin(a), 0)))
        ring.append((x, y, a))
    STD.append(dict(kind="vietnam", label="ĐẠI ĐOÀN 308", side="vn", keys=[(0, 1450, 1830, 0), (3.0, 1450, 1830, 0), (3.6, 1450, 1830, 1)]))
    # ---------- Trung đoàn 209 chặn phía bắc, 174 chặn Cốc Tồn – Khau Pia ----------
    for (cx, cy, hd, t0) in [(2120, 1830, 0.3, 10.0), (2330, 1880, 0.1, 10.3), (2230, 1760, 0.2, 10.6)]:
        U.append(Unit("vn", appear(t0, cx, cy, hd)))
        U.append(Unit("skv", appear(t0 + 0.2, cx + 40, cy + 60, 0)))
    STD.append(dict(kind="vietnam", label="TRUNG ĐOÀN 209", side="vn", keys=[(0, 2450, 1720, 0), (10.2, 2450, 1720, 0), (10.8, 2450, 1720, 1)]))
    for (cx, cy, hd, t0) in [(3250, 2800, 0.4, 12.6), (3480, 2930, 0.4, 12.9), (3700, 3020, 0.4, 13.2)]:
        U.append(Unit("vn", appear(t0, cx, cy, hd)))
        U.append(Unit("skv", appear(t0 + 0.2, cx - 40, cy - 50, 0)))
    STD.append(dict(kind="vietnam", label="TRUNG ĐOÀN 174", side="vn", keys=[(0, 3560, 2760, 0), (12.8, 3560, 2760, 0), (13.4, 3560, 2760, 1)]))
    # ---------- Trung đoàn 36 tấn công lòng chảo ----------
    starts = [(1750, 2980), (2000, 3000), (2500, 2860), (2700, 2380), (1150, 2300), (1250, 2600)]
    for j, (sx, sy) in enumerate(starts):
        for k in range(2):
            x0, y0 = sx + k * 80, sy + k * 30
            tx, ty = B[0] + (sx - B[0]) * 0.18 + r.uniform(-80, 80), B[1] + (sy - B[1]) * 0.18 + r.uniform(-60, 60)
            hd = math.atan2(ty - y0, tx - x0) - math.pi / 2
            U.append(Unit("vn", appear(17.6 + j * 0.15, x0, y0, hd, [(19.2 + j * 0.2, x0, y0, hd, 1), (28.0, tx, ty, hd, 1)])))
            for q in range(2):
                ox, oy = r.uniform(-60, 60), r.uniform(-40, 40)
                U.append(Unit("skv", appear(17.8 + j * 0.15, x0 + ox, y0 + oy - 60, 0, [(19.0, x0 + ox, y0 + oy - 60, 0, 1), (27.0, tx + ox, ty + oy - 60, 0, 1)])))
    STD.append(dict(kind="vietnam", label="TRUNG ĐOÀN 36", side="vn", keys=[(0, 1900, 3080, 0), (17.6, 1900, 3080, 0), (18.2, 1900, 3080, 1),
                                                                            (28.0, 1950, 2600, 1)]))
    # ---------- vòng vây quanh điểm cao 477 ----------
    for i in range(12):
        a = i / 12 * 2 * math.pi
        x0, y0 = P477[0] + 720 * math.cos(a), P477[1] + 560 * math.sin(a)
        x1, y1 = P477[0] + 360 * math.cos(a), P477[1] + 290 * math.sin(a)
        x2, y2 = P477[0] + 170 * math.cos(a), P477[1] + 140 * math.sin(a)
        hd = a + math.pi / 2
        U.append(Unit("vn", appear(38.6 + i * 0.12, x0, y0, hd, [(40.5, x0, y0, hd, 1), (45.0, x1, y1, hd, 1), (47.0, x1, y1, hd, 1), (51.5, x2, y2, hd, 1)])))
        for q in range(2):
            ox, oy = r.uniform(-50, 50), r.uniform(-40, 40)
            U.append(Unit("skv", appear(38.8 + i * 0.12, x0 + ox, y0 + oy, 0, [(40.5, x0 + ox, y0 + oy, 0, 1), (45.0, x1 + ox, y1 + oy, 0, 1),
                                                                                  (47.0, x1 + ox, y1 + oy, 0, 1), (51.5, x2 + ox * 0.6, y2 + oy * 0.6, 0, 1)])))
    STD.append(dict(kind="vietnam", label="TRUNG ĐOÀN 88", side="vn", keys=[(0, P477[0] + 420, P477[1] + 160, 0), (54.6, P477[0] + 420, P477[1] + 160, 0),
                                                                            (55.2, P477[0] + 420, P477[1] + 160, 1), (57.5, P477[0] + 250, P477[1] + 90, 1)]))
    for k in range(6):
        a = k / 6 * 2 * math.pi
        U.append(Unit("skv", appear(54.8 + k * 0.1, P477[0] + 140 + 160 * math.cos(a), P477[1] + 40 + 120 * math.sin(a), 0,
                                    [(56.2, P477[0] + 140 + 160 * math.cos(a), P477[1] + 40 + 120 * math.sin(a), 0, 1),
                                     (57.6, P477[0] + 140 + 60 * math.cos(a), P477[1] + 40 + 50 * math.sin(a), 0, 1)])))
    return U, STD, []


UNITS, STDS, ADV = build_oob()


# ============================ sprites ============================
PPM = 4  # px trên mét cho sprite gốc
COL = {"vn": (210, 28, 26), "fl": (30, 62, 205), "br": (215, 22, 22), "hn": (225, 60, 50), "nl": (235, 115, 30), "fr": (28, 58, 205), "frg": (20, 40, 150),
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
            if kind == "vn":
                td.polygon([(ww * 0.36, hh), (ww * 0.50, hh), (ww * 0.64, 0), (ww * 0.50, 0)], fill=(255, 214, 0, 255))
            elif kind in ("fr", "frg", "fl"):
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
    """lính tán binh tí hon: mũ đen, áo màu phe, đai chéo trắng, quần, súng hỏa mai dựng đứng có lưỡi lê"""
    if kind in _spr: return _spr[kind]
    coat = (200, 28, 26) if kind in ("skb", "skv") else (32, 62, 200)
    trou = (205, 205, 200) if kind == "skf" else ((150, 138, 96) if kind in ("skv", "skl") else (110, 110, 118))
    o = (18, 14, 12, 255)
    im = Image.new("RGBA", (60, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # chân
    d.polygon([(19, 112), (29, 112), (28, 160), (18, 160)], fill=trou + (255,), outline=o)
    d.polygon([(31, 112), (41, 112), (42, 160), (32, 160)], fill=trou + (255,), outline=o)
    d.rectangle((17, 156, 29, 164), fill=(25, 20, 18, 255)); d.rectangle((31, 156, 43, 164), fill=(25, 20, 18, 255))
    # áo
    d.polygon([(15, 48), (45, 48), (47, 116), (13, 116)], fill=coat + (255,), outline=o)
    if kind == "skv":
        d.line([(15, 92), (45, 92)], fill=(120, 100, 60, 255), width=5)
    else:
        d.line([(17, 52), (43, 108)], fill=(250, 250, 248, 255), width=5); d.line([(43, 52), (17, 108)], fill=(250, 250, 248, 255), width=5)
    # tay giữ súng
    d.polygon([(40, 54), (50, 60), (50, 86), (44, 86)], fill=coat + (255,), outline=o)
    # đầu + mũ shako
    d.ellipse((21, 30, 39, 50), fill=(230, 190, 160, 255), outline=o)
    if kind == "skv":      # mũ lá
        d.ellipse((6, 22, 54, 38), fill=(196, 178, 120, 255), outline=o, width=2)
        d.ellipse((18, 12, 42, 32), fill=(206, 188, 128, 255), outline=o, width=2)
    elif kind == "skl":    # kê-pi trắng Lê dương
        d.rectangle((20, 12, 40, 34), fill=(245, 245, 240, 255), outline=o)
        d.rectangle((18, 30, 42, 35), fill=(30, 30, 40, 255))
    else:
        d.rectangle((19, 10, 41, 34), fill=(22, 20, 22, 255), outline=o)
        d.rectangle((17, 30, 43, 35), fill=(22, 20, 22, 255))
    # súng hỏa mai + lưỡi lê
    d.rectangle((47, 20, 56, 152), fill=(38, 26, 18, 255), outline=o)
    d.rectangle((49, 4, 54, 24), fill=(170, 172, 178, 255), outline=o)
    d.polygon([(49, 5), (51.5, -4), (54, 5)], fill=(235, 236, 240, 255))
    # sáng phía trái
    a = np.asarray(im).astype(np.float32); xx = np.linspace(1.18, 0.85, im.width)[None, :, None]
    a[..., :3] *= xx; im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
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
    elif kind == "vietnam":
        d.rectangle((0, 0, w, h), fill=(214, 34, 30))
        cx, cy, R = w / 2, h / 2, h * 0.36; pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5; rr = R if k % 2 == 0 else R * 0.382
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        d.polygon(pts, fill=(255, 214, 0))
    elif kind == "france2":
        for i, c in enumerate([(20, 50, 160), (250, 250, 248), (215, 25, 35)]):
            d.rectangle((i * w / 3, 0, (i + 1) * w / 3, h), fill=c)
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
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def wave_flag(fl, t, ph0, cloth=True):
    """vải cờ gợn sóng: nếp chạy ngang, mép dưới đung đưa, sáng tối theo nếp"""
    from scipy.ndimage import map_coordinates
    a = np.asarray(fl).astype(np.float32); h, w = a.shape[:2]; padb = 10
    a = np.concatenate([a, np.zeros((padb, w, 4), np.float32)], 0)
    yy, xx = np.mgrid[0:h + padb, 0:w].astype(np.float32)
    u = xx / w; v = np.clip(yy / h, 0, 1)
    amp = 1.0 if cloth else 0.55
    ph = 2 * np.pi * (1.25 * u - 0.55 * t) + ph0
    ph2 = 2 * np.pi * (2.3 * u - 0.9 * t) + ph0 * 1.7
    dy = amp * (3.2 * np.sin(ph) + 1.0 * np.sin(ph2)) * v ** 1.2
    dx = amp * 1.4 * np.sin(ph * 0.5 + 1.0) * v
    sy, sx = yy - dy, xx - dx
    out = np.stack([map_coordinates(a[..., c], [sy, sx], order=1, mode="constant", cval=0) for c in range(4)], -1)
    shade = 1 + amp * (0.15 * np.cos(ph) + 0.06 * np.cos(ph2)) * (0.35 + 0.65 * v)
    out[..., :3] *= shade[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def std_tex(kind, label, t=0.0, side_=None):
    key = ("std", kind, label)
    if key not in _spr:
        fl = flag_img(kind).convert("RGBA")
        d = ImageDraw.Draw(fl); d.rectangle((0, 0, fl.width - 1, fl.height - 1), outline=(25, 20, 20), width=2)
        side = (190, 30, 30) if side_ == "vn" else (40, 60, 160)
        fw, fh = fl.size
        plate_h = 26; pole = 40
        im = Image.new("RGBA", (fw + 20, fh + plate_h + pole + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        x0 = 10; y0 = 14
        # cán cờ (sau tấm vải)
        d.rectangle((x0 + fw / 2 - 2, y0 + plate_h + fh - 6, x0 + fw / 2 + 2, im.height - 2), fill=(70, 60, 50))
        top = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(top)
        d.rectangle((x0 - 2, y0, x0 + fw + 2, y0 + plate_h), fill=(245, 242, 235), outline=side, width=3)
        f = F(BARLOW, 17)
        d.text((x0 + fw / 2, y0 + plate_h / 2 + 1), label, font=f, fill=(30, 25, 25), anchor="mm")
        d.ellipse((x0 + fw / 2 - 5, y0 - 10, x0 + fw / 2 + 5, y0), fill=(200, 160, 60) if side[2] > 100 else (90, 90, 95), outline=(40, 30, 10))
        _spr[key] = (im, top, fl, (x0, y0 + plate_h + 1), (x0 + fw / 2, im.height - 2), not kind.startswith("portrait"))
    base, top, fl, fpos, anchor, cloth = _spr[key]
    ph0 = (sum(map(ord, label)) * 0.37) % (2 * math.pi)
    im = base.copy()
    im.alpha_composite(wave_flag(fl, t, ph0, cloth), fpos)
    im.alpha_composite(top)
    return im, anchor


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
    for t in np.arange(18.8, 30.5, 0.07):          # trận đánh trong lòng chảo
        a = r.uniform(0, 6.28); rr = r.uniform(80, 520)
        ev.append((t, B[0] + rr * math.cos(a), B[1] + rr * math.sin(a) * 0.6, r.uniform(14, 26)))
    for t in np.arange(19.0, 26.0, 0.25):          # súng cối từ sườn núi
        a = r.uniform(0, 6.28)
        ev.append((t, B[0] + 800 * math.cos(a), B[1] + 560 * math.sin(a), r.uniform(12, 18)))
    for t in np.arange(46.4, 53.5, 0.06):          # tấn công điểm cao 477
        a = r.uniform(0, 6.28); rr = r.uniform(60, 380)
        ev.append((t, P477[0] + rr * math.cos(a), P477[1] + rr * math.sin(a) * 0.8, r.uniform(12, 22)))
    for t in np.arange(40.0, 46.0, 0.3):
        a = r.uniform(0, 6.28); rr = r.uniform(150, 450)
        ev.append((t, P477[0] + rr * math.cos(a), P477[1] + rr * math.sin(a) * 0.8, r.uniform(10, 16)))
    return ev


SMOKE = smoke_events()
CHURN = [(B[0] + 260 * math.cos(k), B[1] + 140 * math.sin(k), 260, 20.0 + 1.2 * (k % 5)) for k in range(8)] + [(B[0], B[1], 380, 23.0)]
CHURN += [(P477[0] + 120 * math.cos(k), P477[1] + 100 * math.sin(k), 200, 47.5 + 0.8 * (k % 4)) for k in range(6)]
ARROWS = [
    dict(p=[(2560, 1560), (2350, 1720), (2200, 1800)], w=60, t=(9.8, 11.4, 16.4, 17.4)),
    dict(p=[(3560, 3420), (3480, 3180), (3420, 2980)], w=60, t=(12.3, 13.9, 16.4, 17.4)),
]
for i, (sx, sy, ex, ey) in enumerate([(1800, 3050, 1860, 2520), (2550, 2950, 2120, 2500), (2780, 2330, 2300, 2340), (1080, 2280, 1530, 2330)]):
    ARROWS.append(dict(p=[(sx, sy), (ex, ey)], w=85, t=(18.6 + 0.25 * i, 21.2 + 0.25 * i, 26.4, 27.6)))
ARROWS.append(dict(p=[(2020, 2180), (2120, 1900), (2260, 1620), (2330, 1460)], w=55, t=(30.6, 32.8, 35.8, 36.8)))
for i, (sx, sy) in enumerate([(2360, 700), (3050, 1350), (2380, 1980), (1700, 1350)]):
    ex, ey = lerp(sx, P477[0], 0.78), lerp(sy, P477[1], 0.78)
    ARROWS.append(dict(p=[(sx, sy), (ex, ey)], w=80, t=(46.5 + 0.25 * i, 48.8 + 0.25 * i, 52.0, 53.0)))
RINGS = [dict(c=B, r=640, w=38, t=(2.6, 3.8, 7.8, 8.7)),
         dict(c=P477, r=230, w=22, t=(31.6, 32.5, 35.8, 36.6)),
         dict(c=P477, r=520, w=30, t=(40.6, 41.8, 45.0, 45.8))]
CLOCK = [(0, "06/10/1950"), (18.0, "06/10 · 05:30"), (26.0, "06/10 · 12:00"), (46.0, "07/10/1950"), (54.2, "08/10/1950")]
LABELS = [("Cốc Xá", "Cốc Xá", (0, 230)), ("Đông Khê", "Đông Khê", (0, -200)), ("Cốc Tồn", "Cốc Tồn", (0, 110)),
          ("Khau Pia", "Khau Pia", (60, 110)), ("Quang Liệt", "Quang Liệt", (0, -90)), ("Nà Pá", "Nà Pá", (0, -90)),
          (tuple(GEO["p477"]), "Điểm cao 477", (-330, -40)), ((4930, 2600), "Đường số 4", (0, 0))]
CARDS = [dict(text="CÒN ~650 NGƯỜI", at=(2250, 1760), t=(31.0, 36.6), side="fr")]


# ============================ ground rasters ============================
# ---------------- chuyển sang hệ toạ độ bản đồ 8K thật ----------------
_oB, _oP = np.array(B, float), np.array(P477, float)
_nB, _nP = np.array(GEO_NEW["B"], float), np.array(GEO_NEW["P477"], float)
_vo, _vn = _oP - _oB, _nP - _nB
SIM_S = float(np.hypot(*_vn) / np.hypot(*_vo)); SIM_R = math.atan2(_vn[1], _vn[0]) - math.atan2(_vo[1], _vo[0])
_c, _s = math.cos(SIM_R) * SIM_S, math.sin(SIM_R) * SIM_S


def TX(x, y):
    dx, dy = x - _oB[0], y - _oB[1]
    return (_nB[0] + _c * dx - _s * dy, _nB[1] + _s * dx + _c * dy)


for u in UNITS:
    u.keys = [(k[0], *TX(k[1], k[2]), k[3] + SIM_R, k[4]) for k in u.keys]
for sd in STDS:
    sd["keys"] = [(k[0], *TX(k[1], k[2]), k[3]) for k in sd["keys"]]
for ar in ARROWS:
    ar["p"] = [TX(*q) for q in ar["p"]]; ar["w"] *= SIM_S
for rg in RINGS:
    rg["c"] = TX(*rg["c"]); rg["r"] *= SIM_S
SMOKE = [(e[0], *TX(e[1], e[2]), e[3]) for e in SMOKE]
CHURN = [(*TX(e[0], e[1]), e[2] * SIM_S, e[3]) for e in CHURN]
for c in CARDS:
    c["at"] = TX(*c["at"])
CAM = [(k[0], *TX(k[1], k[2]), k[3] * SIM_S, k[4], k[5]) for k in CAM]
_rc4 = GEO_NEW["routes"]["rc4"]
LABELS = [(tuple(GEO_NEW["villages"][k]) if k in GEO_NEW["villages"] else k, txt, off) for (k, txt, off) in LABELS
          if not (isinstance(k, tuple) and k == tuple(GEO["p477"])) and txt != "Đường số 4"]
LABELS += [(tuple(GEO_NEW["P477"]), "Điểm cao 477", (-330, -40)), (tuple(_rc4[len(_rc4) * 3 // 4]), "Đường số 4", (60, 0))]
CHURN_BBOX = (int(min(e[0] for e in CHURN)) - 500, int(min(e[1] for e in CHURN)) - 500, int(max(e[0] for e in CHURN)) + 500, int(max(e[1] for e in CHURN)) + 500)


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
    res = 6.0; x0, y0, x1, y1 = CHURN_BBOX

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
    if L == 0: return tex
    key = (id(tex), L)
    hit = _mip.get(key)
    if hit is None or hit[0] is not tex:
        im = tex
        for _ in range(L):
            im = im.resize((max(1, im.width // 2), max(1, im.height // 2)), Image.LANCZOS)
        if len(_mip) > 400: _mip.clear()
        _mip[key] = hit = (tex, im)
    return hit[1]


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


def card_tex(txt, side):
    key = ("card", txt)
    if key not in _lab:
        f = F(BARLOW, 56); tw = int(f.getlength(txt)) + 60
        im = Image.new("RGBA", (tw, 90), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        col = (40, 60, 160) if side == "fr" else (190, 30, 30)
        d.rectangle((2, 2, tw - 3, 87), fill=(245, 242, 235, 255), outline=col + (255,), width=5)
        d.text((tw / 2, 46), txt, font=f, fill=(30, 25, 25, 255), anchor="mm")
        _lab[key] = im
    return _lab[key]


def label_tex(txt):
    if txt not in _lab:
        f = F(CORM, 64)
        lay = Image.new("RGBA", (int(f.getlength(txt)) + 60, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((lay.width / 2 + 2, 64), txt, font=f, fill=(10, 8, 0, 235), anchor="mm")
        lay = lay.filter(ImageFilter.GaussianBlur(6)); d = ImageDraw.Draw(lay)
        d.text((lay.width / 2, 60), txt, font=f, fill=(246, 242, 228, 255), anchor="mm")
        _lab[txt] = lay
    return _lab[txt]


# ============================ vũ khí minh hoạ (đúng thời 1815) ============================
WEAPONS_ICONS = [  # loại, tên, gắn vào (cờ hoặc toạ độ), lệch (mét), (hiện, ẩn), phe
    dict(kind="cannon", label="12-POUNDER", at=(3420, 1990), off=(0, 0), t=(1.0, 7.6), side="fr"),
    dict(kind="charleville", label="CHARLEVILLE M1777", at="france:2ND DIVISION", off=(-190, -110), t=(10.0, 16.2), side="fr"),
    dict(kind="brownbess", label="BROWN BESS", at=(3560, 1330), off=(0, 0), t=(13.4, 18.4), side="br"),
    dict(kind="baker", label="BAKER RIFLE \u00b7 95TH", at=(2905, 1700), off=(-150, -40), t=(14.0, 18.4), side="br"),
    dict(kind="sabre", label="1796 HEAVY CAVALRY SWORD", at="union:UNION BDE", off=(95, 25), t=(18.9, 23.4), side="br"),
]
WEAPONS = []   # bật lại bằng WEAPONS = WEAPONS_ICONS nếu muốn biểu tượng vũ khí riêng
WOOD, WOOD_D, STEEL, STEEL_D, BRASS = (122, 74, 38), (70, 40, 18), (168, 172, 178), (78, 80, 86), (196, 160, 70)


def weapon_tex(kind):
    key = ("wpn", kind)
    if key in _spr: return _spr[key]
    Wc, Hc = 720, 220
    im = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    o = (25, 18, 12, 255)
    if kind in ("brownbess", "charleville", "baker"):
        L = 640 if kind != "baker" else 520
        x0 = 30; y = 110
        bar_end = x0 + L
        # nòng thép
        d.rectangle((x0 + 150, y - 9, bar_end, y + 1), fill=STEEL + (255,), outline=o, width=3)
        d.line([(x0 + 160, y - 6), (bar_end - 4, y - 6)], fill=(225, 228, 232, 255), width=2)
        # báng gỗ + thân dưới nòng
        stock = [(x0, y + 52), (x0 + 6, y - 6), (x0 + 120, y - 10), (x0 + 175, y - 2), (bar_end - (70 if kind != "baker" else 40), y - 2),
                 (bar_end - (70 if kind != "baker" else 40), y + 12), (x0 + 210, y + 14), (x0 + 175, y + 20), (x0 + 120, y + 26), (x0 + 22, y + 60)]
        d.polygon(stock, fill=WOOD + (255,), outline=o)
        d.line([(x0 + 14, y + 4), (x0 + 120, y - 2)], fill=(160, 104, 58, 255), width=3)
        # que thông nòng
        d.line([(x0 + 215, y + 8), (bar_end - 10, y + 8)], fill=STEEL_D + (255,), width=3)
        # cò súng + vòng che cò
        d.arc((x0 + 150, y + 6, x0 + 200, y + 40), 0, 180, fill=(BRASS if kind == "brownbess" else STEEL_D) + (255,), width=4)
        d.line([(x0 + 172, y + 12), (x0 + 168, y + 26)], fill=o, width=3)
        # bộ khoá đá lửa
        d.rectangle((x0 + 170, y - 16, x0 + 222, y + 4), fill=STEEL_D + (255,), outline=o, width=2)
        d.polygon([(x0 + 176, y - 16), (x0 + 168, y - 34), (x0 + 184, y - 36), (x0 + 190, y - 16)], fill=STEEL + (255,), outline=o)
        # vòng đai nòng
        bands = [x0 + 330, x0 + 460, bar_end - 74] if kind == "charleville" else ([x0 + 400] if kind == "baker" else [])
        for bx in bands:
            d.rectangle((bx, y - 11, bx + 9, y + 13), fill=(STEEL if kind == "charleville" else BRASS) + (255,), outline=o, width=2)
        if kind == "brownbess":
            d.rectangle((x0 + 2, y + 38, x0 + 20, y + 58), fill=BRASS + (255,))
        if kind == "baker":   # hộp đồng ở báng + thước ngắm
            d.rounded_rectangle((x0 + 40, y + 8, x0 + 110, y + 26), 6, fill=BRASS + (255,), outline=o, width=2)
            d.rectangle((bar_end - 30, y - 18, bar_end - 22, y - 9), fill=STEEL_D + (255,))
        if kind in ("brownbess", "charleville"):   # lưỡi lê
            d.rectangle((bar_end - 18, y + 1, bar_end - 4, y + 12), fill=STEEL_D + (255,), outline=o, width=2)
            d.polygon([(bar_end - 6, y + 8), (Wc - 8, y + 2), (bar_end - 6, y + 16)], fill=(205, 208, 214, 255), outline=o)
    elif kind == "cannon":
        # nòng đồng
        d.polygon([(150, 70), (600, 92), (600, 122), (150, 140), (120, 132), (120, 78)], fill=(176, 128, 58, 255), outline=o)
        d.line([(160, 86), (590, 100)], fill=(226, 186, 110, 255), width=4)
        for bx in (220, 330, 560): d.rectangle((bx, 80 + (bx - 150) * 0.05, bx + 12, 130 - (bx - 150) * 0.05), fill=(150, 104, 44, 255), outline=o)
        d.ellipse((96, 92, 126, 118), fill=(150, 104, 44, 255), outline=o, width=2)
        d.rectangle((600, 88, 618, 126), fill=(150, 104, 44, 255), outline=o, width=2)
        # giá gỗ
        d.polygon([(30, 190), (250, 130), (330, 136), (330, 158), (60, 206)], fill=(92, 104, 70, 255), outline=o)
        # bánh xe
        cx, cy, r = 280, 150, 62
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=o, width=12)
        d.ellipse((cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3), outline=(92, 104, 70, 255), width=7)
        for k in range(12):
            a = k * math.pi / 6; d.line([(cx, cy), (cx + (r - 6) * math.cos(a), cy + (r - 6) * math.sin(a))], fill=(80, 90, 60, 255), width=5)
        d.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), fill=STEEL_D + (255,), outline=o, width=2)
    elif kind == "sabre":
        # lưỡi thẳng, mũi kiểu "rìu" (mẫu 1796 kỵ binh nặng)
        d.polygon([(190, 98), (650, 96), (686, 108), (650, 120), (190, 118)], fill=(212, 216, 222, 255), outline=o)
        d.line([(196, 104), (640, 102)], fill=(250, 252, 255, 255), width=3)
        d.line([(200, 111), (600, 110)], fill=STEEL_D + (255,), width=2)
        # chắn tay + chuôi
        d.rounded_rectangle((170, 70, 196, 150), 8, fill=STEEL + (255,), outline=o, width=3)
        d.arc((60, 60, 200, 168), 90, 270, fill=STEEL + (255,), width=9)
        d.rounded_rectangle((70, 96, 172, 122), 10, fill=(40, 30, 24, 255), outline=o, width=2)
        for gx in range(80, 165, 12): d.line([(gx, 98), (gx + 6, 120)], fill=(120, 100, 70, 255), width=2)
        d.ellipse((50, 94, 76, 124), fill=STEEL + (255,), outline=o, width=2)
    # viền sáng mỏng cho nổi trên nền bản đồ
    a = im.split()[3]
    rim = Image.new("RGBA", im.size, (250, 244, 225, 0)); rim.putalpha(a.filter(ImageFilter.MaxFilter(7)).point(lambda v: int(v * 0.85)))
    rim.alpha_composite(im); im = rim
    bb = im.getbbox(); im = im.crop((bb[0] - 4, bb[1] - 4, bb[2] + 4, bb[3] + 4))
    _spr[key] = im
    return im


def weapon_card(w):
    """biểu tượng vũ khí + biển tên bên dưới"""
    key = ("wcard", w["kind"], w["label"])
    if key in _spr: return _spr[key]
    ic = weapon_tex(w["kind"])
    f = F(BARLOW, 34)
    tw = int(f.getlength(w["label"])) + 40
    side = (190, 30, 30) if w["side"] == "br" else (40, 60, 160)
    Wd = max(ic.width, tw) + 20; Hd = ic.height + 70
    im = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
    im.alpha_composite(ic, ((Wd - ic.width) // 2, 0))
    d = ImageDraw.Draw(im)
    px0 = (Wd - tw) // 2; py0 = ic.height + 12
    d.rectangle((px0, py0, px0 + tw, py0 + 48), fill=(245, 242, 235, 255), outline=side + (255,), width=4)
    d.text((Wd / 2, py0 + 25), w["label"], font=f, fill=(30, 25, 25, 255), anchor="mm")
    _spr[key] = (im, (Wd / 2, Hd))
    return _spr[key]


def std_pos(sd, t):
    ks = sd["keys"]
    if len(ks) == 1 or t <= ks[0][0]: return ks[0][1:]
    for i in range(len(ks) - 1):
        if ks[i][0] <= t <= ks[i + 1][0]:
            e = ease((t - ks[i][0]) / (ks[i + 1][0] - ks[i][0]))
            return lerp(ks[i][1], ks[i + 1][1], e), lerp(ks[i][2], ks[i + 1][2], e)
    return ks[-1][1:]


def draw_weapons(img, cam, t):
    for w in WEAPONS:
        t0, t1 = w["t"]
        if t < t0 or t > t1 + 0.5: continue
        if isinstance(w["at"], str):
            kd, lb = w["at"].split(":", 1)
            sd = [d for d in STDS if d["label"] == lb and d["kind"] == kd][0]; x, y = std_pos(sd, t)
        else:
            x, y = w["at"]
        x += w["off"][0]; y += w["off"][1]
        uu, vv, s = cam.proj([(x, y)])
        k = (t - t0) / 0.45
        pop = 1 + 0.12 * math.sin(min(1, k) * math.pi) if k < 1 else 1.0      # nảy nhẹ khi hiện
        op = ease(k) * (1 - ease((t - t1) / 0.5))
        ic = weapon_tex(w["kind"])
        L_m = 64 if w["kind"] != "cannon" else 50          # dài cỡ một khối tiểu đoàn
        sc = L_m * float(s[0]) / ic.width * pop
        blit(img, ic, (ic.width / 2, ic.height / 2), (float(uu[0]), float(vv[0])), sc, alpha=op,
             shadow=(4 * float(s[0]), 5 * float(s[0]), 1.8 * float(s[0]), 0.55))

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
        f = F(OSWALD, 76)
        lay = Image.new("RGBA", (760, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((740, 80), s, font=f, anchor="rm", fill=(0, 0, 0, 255))
        msk = lay.split()[3]
        grad = Image.linear_gradient("L").resize((760, 160)).point(lambda v: int(232 - v * 0.42))
        face = Image.merge("RGBA", (grad, grad, grad, msk))
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(msk.filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * 0.75)))
        edge = Image.new("RGBA", lay.size, (40, 40, 40, 0)); edge.putalpha(msk.filter(ImageFilter.MaxFilter(3)))
        hl = Image.new("RGBA", lay.size, (255, 255, 255, 0)); hl.putalpha(ImageChops.subtract(msk, ImageChops.offset(msk, 0, 2)).point(lambda v: int(v * 0.6)))
        comp = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        comp.alpha_composite(sh, (3, 4)); comp.alpha_composite(edge); comp.alpha_composite(face); comp.alpha_composite(hl)
        if op < 1: comp.putalpha(comp.split()[3].point(lambda v: int(v * op)))
        img.alpha_composite(comp, (W - 760 - 70, 18))


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
        ks = sd["keys"]; k0 = ks[0]
        if t <= ks[0][0]: x, y, al_ = ks[0][1:]
        elif t >= ks[-1][0]: x, y, al_ = ks[-1][1:]
        else:
            for i in range(len(ks) - 1):
                if ks[i][0] <= t <= ks[i + 1][0]:
                    e = ease((t - ks[i][0]) / (ks[i + 1][0] - ks[i][0]))
                    x, y, al_ = lerp(ks[i][1], ks[i + 1][1], e), lerp(ks[i][2], ks[i + 1][2], e), lerp(ks[i][3], ks[i + 1][3], e); break
        if al_ <= 0.01: continue
        uu, vv, s = cam.proj([(x, y)])
        if not (-200 < uu[0] < W + 200 and -50 < vv[0] < H + 300): continue
        items.append((vv[0] + 1e4, "s", sd, x, y, 0, al_, uu[0], s[0]))
    items.sort(key=lambda it: it[0])
    for it in items:
        _, typ, obj, x, y, hd, al, u0, s = it
        v0 = float(it[0] - (1e4 if typ == "s" else 0)); u0 = float(u0); s = float(s)
        if typ == "u":
            if obj.kind in ("skb", "skf", "skv", "skl"):
                p = pin_tex(obj.kind); sc_ = s * 17 / 170
                blit(img, p, (30, 162), (u0, v0), sc_, M=[[1, -0.75], [0, 0.42]], tint=(15, 18, 5), alpha=0.40 * al)
                blit(img, p, (30, 162), (u0, v0), sc_, alpha=al)
                continue
            ang = cam.screen_angle(x, y, hd)
            tex = gun_tex() if obj.kind == "gun" else bar_tex(obj.kind)
            blit(img, tex, (tex.width / 2, tex.height / 2), (u0, v0), s / PPM, ang=ang, alpha=al,
                 shadow=(5 * s, 6 * s, 2.2 * s, 0.55))
        else:
            sc_ = s * 0.56
            tex, (ax, ay) = std_tex(obj["kind"], obj["label"], t, obj.get("side"))
            pop = 1 + 0.10 * math.sin(min(1, al) * math.pi) if al < 1 else 1.0
            blit(img, tex, (ax, ay), (u0, v0), sc_ * pop, M=[[1, -0.75], [0, 0.42]], tint=(15, 18, 5), alpha=0.42 * al)
            blit(img, tex, (ax, ay), (u0, v0), sc_ * pop, alpha=al)
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
    # --- vũ khí minh hoạ
    draw_weapons(img, cam, t)
    # --- nhãn địa danh
    for (key, txt, off) in LABELS:
        vx, vy = key
        uu, vv, s = cam.proj([(vx + off[0], vy + off[1])])
        if not (-200 < uu[0] < W + 200 and -40 < vv[0] < H + 40): continue
        fs = max(14.0, 30 * float(s[0]))
        lt = label_tex(txt)
        blit(img, lt, (lt.width / 2, 60), (float(uu[0]), float(vv[0])), fs / 64)
    for c in CARDS:
        t0, t1 = c["t"]
        if t0 <= t <= t1 + 0.5:
            uu, vv, s = cam.proj([c["at"]]); ct = card_tex(c["text"], c["side"])
            op = ease((t - t0) / 0.4) * (1 - ease((t - t1) / 0.5))
            blit(img, ct, (ct.width / 2, ct.height / 2), (float(uu[0]), float(vv[0])), max(0.35, min(0.6, 0.55 * float(s[0]))), alpha=op,
                 shadow=(4, 5, 4, 0.5))
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
    d_ = ImageDraw.Draw(img)
    d_.text((40, H - 40), "ĐỊA HÌNH THẬT (SRTM) · VỊ TRÍ ĐƠN VỊ MANG TÍNH MINH HOẠ", font=F(BARLOW, 22), fill=(235, 230, 215, 150), anchor="ls")
    if t > DUR - 1.2:
        img = Image.blend(img, Image.new("RGBA", img.size, (0, 0, 0, 255)), ease((t - (DUR - 1.2)) / 1.2))
    if t < 0.6:
        img = Image.blend(Image.new("RGBA", img.size, (0, 0, 0, 255)), img, ease(t / 0.6))
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
