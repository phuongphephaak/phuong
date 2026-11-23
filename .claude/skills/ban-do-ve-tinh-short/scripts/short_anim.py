"""Video dọc 'Sông Bến Hải – vết cắt chia đôi đất nước' theo nhịp video mẫu (ảnh vệ tinh, zoom ra/vào, tô vùng, nhãn).
python3 bh_anim.py test t1 t2 ... | render"""
import math, os, sys, json, pickle, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from shapely.geometry import Polygon, MultiPolygon, LineString, box
from shapely import affinity

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.abspath(os.environ.get("WORK", os.getcwd()))
SKILL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
W, H = 1080, 1920
FPS = 30
DUR = 26.3
NF = int(DUR * FPS)
SS = 2
G = pickle.load(open(os.path.join(HERE, "geo.pkl"), "rb"))
META = json.load(open(os.path.join(HERE, "mosaic_meta.json")))
FB = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
FX = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"

# ---- chữ trên màn hình theo ngôn ngữ: VLANG=vi (mặc định) | en ----
VLANG = os.environ.get("VLANG", "vi")
TXT = {
    "vi": {"north": "Miền Bắc", "south": "Miền Nam", "river": "Sông Bến Hải", "vinhlinh": "Vĩnh Linh", "giolinh": "Gio Linh",
           "vn": "Việt Nam", "hoangsa": "QĐ. Hoàng Sa", "truongsa": "QĐ. Trường Sa", "sea": "Biển Đông", "cuatung": "Cửa Tùng",
           "vt17": "Vĩ tuyến 17", "dmz": "Khu phi quân sự", "bridge": "Cầu Hiền Lương", "banner": "Vết cắt chia đôi đất nước",
           "credit": "Ảnh vệ tinh: Sentinel-2 cloudless 2016, EOX (CC BY 4.0)"},
    "en": {"north": "North", "south": "South", "river": "Bến Hải River", "vinhlinh": "Vĩnh Linh", "giolinh": "Gio Linh",
           "vn": "Vietnam", "hoangsa": "Paracel Is. (Vietnam)", "truongsa": "Spratly Is. (Vietnam)", "sea": "East Sea", "cuatung": "Cửa Tùng",
           "vt17": "17th Parallel", "dmz": "Demilitarized Zone", "bridge": "Hiền Lương Bridge", "banner": "The River That Split a Nation",
           "credit": "Satellite imagery: Sentinel-2 cloudless 2016 by EOX (CC BY 4.0)"},
}
T = TXT[VLANG]
_fc = {}


def F(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, max(6, int(s)))
    return _fc[k]


def ease(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


def ease_io(x):
    x = min(1.0, max(0.0, x)); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def merc(lon, lat):
    return (lon + 180) / 360 * 256, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * 256


# ============================ camera ============================
# (t, lon, lat, zoom, cut)  — cut=True: nhảy cảnh tại t
CAM = [(0.0, 107.00, 16.96, 12.55, 0), (1.15, 107.00, 16.96, 12.25, 0), (3.15, 106.4, 16.2, 6.85, 0),
       (3.15, 107.00, 16.97, 12.05, 1), (5.05, 107.00, 16.97, 12.30, 0), (6.4, 106.95, 16.88, 9.7, 0),
       (8.3, 108.6, 15.6, 6.85, 0), (10.1, 105.7, 19.6, 7.35, 0), (11.85, 107.2, 13.2, 7.25, 0),
       (11.85, 107.03, 17.00, 11.75, 1), (12.25, 107.03, 17.00, 11.70, 0), (14.8, 107.35, 17.08, 10.05, 0),
       (15.2, 107.35, 17.08, 10.05, 0), (20.7, 106.86, 17.00, 10.45, 0), (21.05, 106.86, 17.00, 10.45, 0),
       (22.6, 107.06, 17.03, 12.05, 0), (DUR, 107.06, 17.02, 12.22, 0)]


def cam_at(t):
    ks = CAM
    for i in range(len(ks) - 1):
        a, b = ks[i], ks[i + 1]
        if b[4] and abs(t - b[0]) < 1e-9: return b[1:4]
        if a[0] <= t < b[0] or (i == len(ks) - 2):
            if b[0] == a[0]: return b[1:4]
            u = ease_io((t - a[0]) / (b[0] - a[0]))
            ax, ay = merc(a[1], a[2]); bx, by = merc(b[1], b[2])
            z = a[3] + (b[3] - a[3]) * u
            # nội suy tâm theo không gian zoom để zoom ra/vào trông tự nhiên
            wa, wb = 2 ** -a[3], 2 ** -b[3]; w = 2 ** -z
            v = 0 if abs(wb - wa) < 1e-12 else (w - wa) / (wb - wa)
            v = u if abs(b[3] - a[3]) < 0.3 else min(1, max(0, v))
            return ax + (bx - ax) * v, ay + (by - ay) * v, z
    return merc(*ks[-1][1:3]) + (ks[-1][3],)


class Cam:
    def __init__(self, t):
        cx, cy, z = cam_at(t)
        if not isinstance(cx, float) or cx > 300:     # khoá đã ở dạng lon/lat
            pass
        self.cx, self.cy, self.z = cx, cy, z
        self.s = 2 ** z

    def P(self, x, y):
        return (x - self.cx) * self.s + W / 2, (y - self.cy) * self.s + H / 2


def _fix_cam():
    global CAM
    out = []
    for (t, lon, lat, z, c) in CAM: out.append((t, lon, lat, z, c))
    CAM = out


# cam_at trả về toạ độ mercator; khoá đầu vào là lon/lat — chuẩn hoá ở đây
def cam_at2(t):
    r = cam_at(t)
    return r


# ============================ ảnh nền vệ tinh (kim tự tháp nhiều mức) ============================
SRC = []


def load_src():
    if SRC: return SRC
    for zm in (13, 10, 7):
        x0, y0, nx, ny = META[str(zm)]
        im = Image.open(os.path.join(HERE, f"mosaic_{zm}.jpg")).convert("RGB")
        sea = Image.open(os.path.join(HERE, f"sea_{zm}.png")).convert("L")
        for k in range(3):
            SRC.append(dict(z=zm - k, im=im, sea=sea, ox=x0 * 256 / 2 ** k, oy=y0 * 256 / 2 ** k,
                            lon0x=x0 / 2 ** zm * 256, lat0y=y0 / 2 ** zm * 256, lon1x=(x0 + nx) / 2 ** zm * 256, lat1y=(y0 + ny) / 2 ** zm * 256))
            im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS); sea = sea.resize((sea.width // 2, sea.height // 2), Image.BILINEAR)
    return SRC


def background(cam):
    srcs = load_src()
    fx0, fy0 = cam.cx - W / 2 / cam.s, cam.cy - H / 2 / cam.s
    fx1, fy1 = cam.cx + W / 2 / cam.s, cam.cy + H / 2 / cam.s
    cov = [s for s in srcs if s["lon0x"] <= fx0 and s["lon1x"] >= fx1 and s["lat0y"] <= fy0 and s["lat1y"] >= fy1]
    if not cov: cov = sorted(srcs, key=lambda s: -(min(s["lon1x"], fx1) - max(s["lon0x"], fx0)) * (min(s["lat1y"], fy1) - max(s["lat0y"], fy0)))[:1]
    good = [s for s in cov if s["z"] >= cam.z - 0.5]
    s = min(good, key=lambda s: s["z"]) if good else max(cov, key=lambda s: s["z"])
    a = 2 ** (s["z"] - cam.z)
    c = cam.cx * 2 ** s["z"] - s["ox"] - W / 2 * a
    f = cam.cy * 2 ** s["z"] - s["oy"] - H / 2 * a
    bg = s["im"].transform((W, H), Image.AFFINE, (a, 0, c, 0, a, f), Image.BICUBIC, fillcolor=(14, 30, 52))
    sea = s["sea"].transform((W, H), Image.AFFINE, (a, 0, c, 0, a, f), Image.BILINEAR, fillcolor=255)
    return bg, sea


def grade_bg(im):
    a = np.asarray(im).astype(np.float32)
    g = a.mean(-1, keepdims=True); a = g + (a - g) * 1.28
    a = (a - 128) * 1.08 + 128 + 6
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ============================ vẽ vùng / đường ============================
def geom_screen(polys, cam):
    """polys: list [[ext],[holes]...] toạ độ z0 -> list polygon toạ độ màn hình x SS đã cắt khung"""
    out = []
    clip = box(-60, -60, W * SS + 60, H * SS + 60)
    for P in polys:
        ext = [((x - cam.cx) * cam.s * SS + W * SS / 2, (y - cam.cy) * cam.s * SS + H * SS / 2) for x, y in P[0]]
        xs = [p[0] for p in ext]; ys = [p[1] for p in ext]
        if max(xs) < 0 or min(xs) > W * SS or max(ys) < 0 or min(ys) > H * SS: continue
        holes = [[((x - cam.cx) * cam.s * SS + W * SS / 2, (y - cam.cy) * cam.s * SS + H * SS / 2) for x, y in h] for h in P[1:]]
        try:
            g = Polygon(ext, holes).buffer(0).intersection(clip)
        except Exception:
            continue
        for p in (g.geoms if hasattr(g, "geoms") else [g]):
            if p.is_empty or p.geom_type != "Polygon": continue
            out.append(p)
    return out


def region_mask(polys, cam):
    m = Image.new("L", (W * SS, H * SS), 0); d = ImageDraw.Draw(m)
    for p in geom_screen(polys, cam):
        d.polygon(list(p.exterior.coords), fill=255)
        for r in p.interiors: d.polygon(list(r.coords), fill=0)
    return m.resize((W, H), Image.LANCZOS)


def fill(img, mask, col, alpha, edge=None):
    if alpha <= 0.005: return
    a = np.asarray(mask, np.float32) / 255 * alpha
    lay = Image.new("RGBA", (W, H), col + (0,)); lay.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    img.alpha_composite(lay)
    if edge:
        e = mask.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(0.6))
        ea = np.clip(np.asarray(e, np.float32) / 255 * 2.2, 0, 1) * alpha * edge[1]
        el = Image.new("RGBA", (W, H), edge[0] + (0,)); el.putalpha(Image.fromarray((ea * 255).astype(np.uint8)))
        img.alpha_composite(el)


def line_pts(pts, cam, frac=1.0):
    P = [cam.P(x, y) for x, y in pts]
    if frac >= 1: return P
    L = np.r_[0, np.cumsum(np.hypot(*np.diff(np.array(P), axis=0).T))]; tgt = L[-1] * frac
    out = [P[0]]
    for i in range(1, len(P)):
        if L[i] <= tgt: out.append(P[i])
        else:
            u = (tgt - L[i - 1]) / max(L[i] - L[i - 1], 1e-6)
            out.append((P[i - 1][0] + (P[i][0] - P[i - 1][0]) * u, P[i - 1][1] + (P[i][1] - P[i - 1][1]) * u)); break
    return out


def glow_line(img, P, col, width, glow, alpha=1.0, core=(255, 255, 255)):
    if len(P) < 2 or alpha <= 0.01: return
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    Q = [(x * SS, y * SS) for x, y in P]
    d.line(Q, fill=col + (255,), width=int(width * SS * 2.6), joint="curve")
    gl = lay.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(glow))
    lay2 = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d2 = ImageDraw.Draw(lay2)
    d2.line(Q, fill=col + (255,), width=int(width * SS), joint="curve")
    if core: d2.line(Q, fill=core + (255,), width=max(1, int(width * SS * 0.35)), joint="curve")
    ln = lay2.resize((W, H), Image.LANCZOS)
    for L_, k in ((gl, 0.9), (ln, 1.0)):
        if alpha * k < 1: L_.putalpha(L_.split()[3].point(lambda v: int(v * alpha * k)))
        img.alpha_composite(L_)


def dashed(img, P, col, width, dash, gap, phase, alpha=1.0, glow=3):
    if len(P) < 2 or alpha <= 0.01: return
    A = np.array(P); seg = np.diff(A, axis=0); L = np.hypot(*seg.T); cum = np.r_[0, np.cumsum(L)]
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    s = -((phase) % (dash + gap))
    while s < cum[-1]:
        a0, a1 = max(0, s), min(cum[-1], s + dash)
        if a1 > a0:
            pts = []
            for q in np.linspace(a0, a1, 4):
                i = min(np.searchsorted(cum, q, "right") - 1, len(L) - 1); u = (q - cum[i]) / max(L[i], 1e-6)
                pts.append(((A[i, 0] + seg[i, 0] * u) * SS, (A[i, 1] + seg[i, 1] * u) * SS))
            d.line(pts, fill=col + (255,), width=int(width * SS))
        s += dash + gap
    ln = lay.resize((W, H), Image.LANCZOS)
    gl = ln.filter(ImageFilter.GaussianBlur(glow))
    for L_ in (gl, ln):
        if alpha < 1: L_.putalpha(L_.split()[3].point(lambda v: int(v * alpha)))
        img.alpha_composite(L_)


# ============================ chữ ============================
_tx = {}


def smallcaps(text, size, col, font=FB, stroke=None, shadow=True, upper_only=False):
    key = (text, size, col, font, stroke, shadow, upper_only)
    if key in _tx: return _tx[key]
    words = text.split(" "); runs = []
    for wi, w_ in enumerate(words):
        if upper_only: runs.append((w_.upper(), size))
        else:
            runs.append((w_[0].upper(), size)); runs.append((w_[1:].upper(), size * 0.76))
        if wi < len(words) - 1: runs.append((" ", size * 0.95))
    tw = sum(F(font, s).getlength(r) for r, s in runs)
    pad = int(size * 0.6)
    im = Image.new("RGBA", (int(tw) + pad * 2, int(size * 1.9) + pad), (0, 0, 0, 0))
    base = pad + size * 1.2
    def draw(d, fill, off=(0, 0), sw=0, sf=None):
        x = pad + off[0]
        for r, s in runs:
            f = F(font, s); d.text((x, base + off[1]), r, font=f, fill=fill, anchor="ls", stroke_width=sw, stroke_fill=sf)
            x += f.getlength(r)
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); draw(ImageDraw.Draw(sh), (0, 0, 0, 200), (size * 0.05, size * 0.07), int(size * 0.08), (0, 0, 0, 200))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(size * 0.07)))
    if stroke: draw(ImageDraw.Draw(im), col + (255,), (0, 0), int(size * stroke[1]), stroke[0] + (255,))
    draw(ImageDraw.Draw(im), col + (255,))
    bb = im.getbbox(); im = im.crop(bb)
    _tx[key] = im
    return im


def blit(img, spr, cx, cy, scale=1.0, alpha=1.0):
    if alpha <= 0.01 or scale <= 0.01: return
    w, h = spr.size
    sc = scale
    ow, oh = int(w * sc) + 4, int(h * sc) + 4
    x0, y0 = cx - w * sc / 2, cy - h * sc / 2
    ix, iy = math.floor(x0) - 2, math.floor(y0) - 2
    a = 1 / sc
    lay = spr.transform((ow + 4, oh + 4), Image.AFFINE, (a, 0, (ix - x0) * a, 0, a, (iy - y0) * a), Image.BICUBIC)
    if alpha < 1: lay.putalpha(lay.split()[3].point(lambda v: int(v * alpha)))
    img.alpha_composite(lay, (0, 0), (0, 0)) if False else None
    # dán an toàn trong khung
    sx0, sy0 = max(0, -ix), max(0, -iy); sx1, sy1 = min(lay.width, W - ix), min(lay.height, H - iy)
    if sx1 > sx0 and sy1 > sy0:
        img.alpha_composite(lay, (ix + sx0, iy + sy0), (sx0, sy0, sx1, sy1))


def pop(t, t0, t1=1e9, dur=0.28):
    """(scale, alpha) cho hiệu ứng nảy khi hiện, mờ khi tắt"""
    if t < t0 or t > t1 + 0.25: return 0, 0
    k = (t - t0) / dur
    sc = 0.55 + 0.45 * ease(k) + 0.10 * math.sin(min(1, k) * math.pi)
    al = ease(k * 1.6) * (1 - ease((t - t1) / 0.25))
    return sc, al


def arrow_label(img, cam, pt, text, t0, t1, t, size, dx, dy, col=(255, 255, 255), stroke=((0, 0, 0), 0.06)):
    sc, al = pop(t, t0, t1)
    if al <= 0: return
    px, py = cam.P(*pt)
    lx, ly = px + dx, py + dy
    spr = smallcaps(text, size, col, stroke=stroke)
    # mũi tên cong từ chân nhãn tới điểm
    sx, sy = lx, ly + spr.height * sc / 2 + 4
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    k = ease((t - t0 - 0.1) / 0.3)
    ex, ey = sx + (px - sx) * k, sy + (py - 6 - sy) * k
    mx, my = (sx + ex) / 2 + (ey - sy) * 0.12, (sy + ey) / 2
    pts = [((1 - u) ** 2 * sx + 2 * (1 - u) * u * mx + u * u * ex, (1 - u) ** 2 * sy + 2 * (1 - u) * u * my + u * u * ey) for u in np.linspace(0, 1, 16)]
    Q = [(x * SS, y * SS) for x, y in pts]
    w_ = max(2, size * 0.09)
    d.line(Q, fill=(0, 0, 0, 160), width=int(w_ * SS * 2.2)); d.line(Q, fill=col + (255,), width=int(w_ * SS))
    if k > 0.6:
        ang = math.atan2(Q[-1][1] - Q[-3][1], Q[-1][0] - Q[-3][0]); hl = w_ * SS * 3.2
        tip = Q[-1]; L_ = (tip[0] - hl * math.cos(ang - 0.5), tip[1] - hl * math.sin(ang - 0.5)); R_ = (tip[0] - hl * math.cos(ang + 0.5), tip[1] - hl * math.sin(ang + 0.5))
        d.polygon([tip, L_, R_], fill=col + (255,), outline=(0, 0, 0, 160))
    lay = lay.resize((W, H), Image.LANCZOS)
    if al < 1: lay.putalpha(lay.split()[3].point(lambda v: int(v * al)))
    img.alpha_composite(lay)
    blit(img, spr, lx, ly, sc, al)


def geo_label(img, cam, pt, text, t0, t1, t, size, col=(255, 255, 255), dx=0, dy=0, stroke=((0, 0, 0), 0.06), upper_only=False, font=FB):
    sc, al = pop(t, t0, t1)
    if al <= 0: return
    px, py = cam.P(*pt)
    spr = smallcaps(text, size, col, stroke=stroke, upper_only=upper_only, font=font)
    hw = spr.width / 2 + 24                  # giữ nhãn trong khung (chữ tiếng Anh thường dài hơn)
    cx = px + dx
    if px > -200 and px < W + 200: cx = min(max(cx, hw), W - hw)
    blit(img, spr, cx, py + dy, sc, al)


def fade(t, t0, t1, fi=0.35, fo=0.3):
    if t < t0 or t > t1 + fo: return 0.0
    return ease((t - t0) / fi) * (1 - ease((t - t1) / fo))



# ============================ xe tăng, máy bay, tàu (sprite 3D từ Blender) ============================
_vs = {}


def veh_sprite(name, ang_deg):
    k = int(round(ang_deg / 15.0)) % 24; res = ang_deg - k * 15
    key = (name, k)
    if key not in _vs: _vs[key] = Image.open(os.path.join(SKILL, "assets", "sprites", f"{name}_{k * 15:03d}.png")).convert("RGBA")
    im = _vs[key]
    return im.rotate(res, Image.BICUBIC) if abs(res) > 0.3 else im


SPAN = {"tank": 8.0, "plane": 15.0, "ship": 25.0}
LEN = {"tank": 7.4, "plane": 11.5, "ship": 23.0}
VEH = [  # loại, [(t, lon, lat)], cỡ px (dài) tại zoom 11, độ cao bóng (px)
    ("ship", [(12.4, 107.40, 17.30), (21.0, 107.24, 17.06), (DUR, 107.215, 17.03)], 140, 5),
    ("ship", [(12.4, 107.42, 17.17), (21.0, 107.18, 17.24), (DUR, 107.15, 17.25)], 120, 5),
    ("ship", [(14.0, 107.00, 17.27), (DUR, 107.20, 17.12)], 110, 5),
    ("plane", [(15.6, 106.45, 17.10), (20.8, 107.45, 16.94)], 150, 70),
    ("plane", [(16.4, 106.40, 17.20), (21.0, 107.40, 17.06)], 120, 90),
    ("tank", [(21.0, 106.93, 17.075), (25.0, 107.015, 17.045), (DUR, 107.02, 17.043)], 75, 4),
    ("tank", [(21.0, 106.875, 17.093), (25.0, 106.96, 17.063), (DUR, 106.965, 17.061)], 75, 4),
    ("tank", [(21.0, 106.82, 17.111), (25.0, 106.905, 17.081), (DUR, 106.91, 17.079)], 75, 4),
]


def veh_pos(keys, t):
    if t < keys[0][0] or t > keys[-1][0] + 1e-6: return None
    for a, b in zip(keys[:-1], keys[1:]):
        if a[0] <= t <= b[0]:
            u = (t - a[0]) / (b[0] - a[0]); ax, ay = merc(a[1], a[2]); bx, by = merc(b[1], b[2])
            return ax + (bx - ax) * u, ay + (by - ay) * u, math.atan2(-(by - ay), bx - ax)
    return None


def draw_vehicles(img, cam, t, kinds):
    for name, keys, size, sh in VEH:
        if name not in kinds: continue
        st = veh_pos(keys, t)
        if st is None: continue
        x, y, hd = st; u, v = cam.P(x, y)
        if not (-200 < u < W + 200 and -200 < v < H + 200): continue
        al = min(1, (t - keys[0][0]) / 0.4, (keys[-1][0] - t) / 0.4 + (1 if keys[-1][0] >= DUR else 0))
        px = size * 2 ** ((cam.z - 11) * 0.3)
        spr = veh_sprite(name, math.degrees(hd))
        sc = px / (LEN[name] / SPAN[name] * spr.width)
        if name == "ship":         # vệt sóng sau tàu
            trail = [veh_pos(keys, t - d) for d in np.linspace(0, 2.2, 14)]
            P_ = [cam.P(q[0], q[1]) for q in trail if q is not None]
            if len(P_) > 2:
                lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
                for i in range(len(P_) - 1):
                    a_ = int(170 * (1 - i / len(P_)) * al)
                    d.line([P_[i], P_[i + 1]], fill=(235, 245, 255, a_), width=max(2, int(px * 0.12 * (1 + i / len(P_)))))
                img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2)))
        a = spr.split()[3]
        shd = Image.new("RGBA", spr.size, (0, 0, 0, 0)); shd.putalpha(a.point(lambda q: int(q * 0.55)))
        shd = shd.filter(ImageFilter.GaussianBlur(4 if sh < 20 else 10))
        off = sh * (1 if name != "plane" else 2 ** ((cam.z - 11) * 0.3))
        blit(img, shd, u + off, v + off, sc, al)
        blit(img, spr, u, v, sc, al)

# ============================ khung hình ============================
YEL = (255, 228, 30)


def render(fi):
    t = fi / FPS
    cam = Cam(t)
    bg, sea = background(cam)
    img = grade_bg(bg).convert("RGBA")
    zk = 2 ** (cam.z - 12)
    # ---- biển xanh đậm (Biển Đông) ----
    a_sea = fade(t, 12.45, 99, 0.6)
    if a_sea > 0:
        sm = sea.filter(ImageFilter.GaussianBlur(2.5))
        fill(img, sm, (22, 28, 235), 0.88 * a_sea)
        glow = sm.filter(ImageFilter.GaussianBlur(14)); ga = np.clip((np.asarray(glow, np.float32) - np.asarray(sm, np.float32) * 0.6) / 255, 0, 1)
        gl = Image.new("RGBA", (W, H), (120, 130, 255, 0)); gl.putalpha(Image.fromarray((ga * 170 * a_sea).astype(np.uint8))); img.alpha_composite(gl)
    # ---- Bắc / Nam lúc zoom ra đầu video ----
    a_n0 = fade(t, 1.85, 3.12, 0.35, 0.05); a_s0 = fade(t, 2.35, 3.12, 0.35, 0.05)
    if a_n0 > 0: fill(img, region_mask(G["VN_N"], cam), (110, 225, 150), 0.82 * a_n0)
    if a_s0 > 0: fill(img, region_mask(G["VN_S"], cam), (222, 128, 58), 0.82 * a_s0)
    # ---- Quảng Trị (2 bờ) ----
    a_qt = fade(t, 5.15, 6.75, 0.3, 0.35)
    if a_qt > 0:
        for k in ("QT_N", "QT_S"): fill(img, region_mask(G[k], cam), (120, 248, 200), 0.85 * a_qt)
    # ---- Việt Nam đỏ -> Bắc xanh lá / Nam cam ----
    a_vn = fade(t, 6.35, 11.82, 0.4, 0.05)
    if a_vn > 0:
        a_g = ease((t - 8.35) / 0.45); a_o = ease((t - 10.15) / 0.45)
        mn, ms = region_mask(G["VN_N"], cam), region_mask(G["VN_S"], cam)
        fill(img, mn, (224, 58, 72), 0.86 * a_vn * (1 - a_g)); fill(img, mn, (110, 225, 150), 0.86 * a_vn * a_g)
        fill(img, ms, (224, 58, 72), 0.86 * a_vn * (1 - a_o)); fill(img, ms, (222, 128, 58), 0.86 * a_vn * a_o)
        # Hoàng Sa, Trường Sa (Việt Nam)
        for key, colk in (("hoangsa", a_o), ("truongsa", a_o)):
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            c = tuple(int(x * (1 - colk) + y * colk) for x, y in zip((224, 58, 72), (222, 128, 58)))
            for (x, y) in G[key]:
                u, v = cam.P(x, y); r = max(3, 5 * 2 ** (cam.z - 7))
                d.ellipse((u - r, v - r, u + r, v + r), fill=c + (int(235 * a_vn),), outline=(255, 255, 255, int(200 * a_vn)))
            img.alpha_composite(lay)
    # ---- đường sáng xanh lam ban đầu ----
    a_gl = fade(t, 0.0, 3.1, 0.15, 0.06)
    if a_gl > 0:
        glow_line(img, line_pts(G["glow"], cam, ease((t - 0.05) / 1.0)), (70, 215, 255), max(3.5, 6.5 * min(1, zk ** 0.3)), 14, a_gl)
    # ---- sông Bến Hải xanh đậm ----
    if t >= 3.15:
        a_r = 1.0
        wr = max(2.4, 5.5 * zk ** 0.6)
        glow_line(img, line_pts(G["river"], cam, ease((t - 3.2) / 0.5)), (20, 50, 255), wr, 3, a_r, core=None)
    # ---- giới tuyến vĩ tuyến 17 + khu phi quân sự (nét đứt động) ----
    a_d = fade(t, 15.45, 99, 0.5)
    if a_d > 0:
        ph = t * 60
        grow = ease((t - 15.45) / 1.6)
        dashed(img, line_pts(G["dmz"], cam, grow), (255, 255, 255), 4.0, 22, 14, ph, a_d, glow=4)
        a_z = fade(t, 16.9, 99, 0.6)
        if a_z > 0:
            dashed(img, line_pts(G["dmzN"], cam, ease((t - 16.9) / 1.2)), (255, 245, 200), 2.6, 12, 10, -ph, a_z * 0.95, glow=3)
            dashed(img, line_pts(G["dmzS"], cam, ease((t - 16.9) / 1.2)), (255, 245, 200), 2.6, 12, 10, -ph, a_z * 0.95, glow=3)
    draw_vehicles(img, cam, t, ("ship", "tank"))
    # ---- vòng tròn đỏ cầu Hiền Lương ----
    if t >= 22.45:
        k = ease((t - 22.45) / 0.35); u, v = cam.P(*G["pts"]["hienluong"])
        r = 34 * (0.4 + 0.6 * k) * (1 + 0.06 * math.sin((t - 22.45) * 7))
        lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.ellipse(((u - r) * SS, (v - r) * SS, (u + r) * SS, (v + r) * SS), outline=(230, 30, 40, 255), width=int(6 * SS))
        d.ellipse(((u - r) * SS, (v - r) * SS, (u + r) * SS, (v + r) * SS), fill=(230, 30, 40, 60))
        lay = lay.resize((W, H), Image.LANCZOS); gl = lay.filter(ImageFilter.GaussianBlur(6))
        img.alpha_composite(gl); img.alpha_composite(lay)
    # ---- nhãn ----
    P = G["pts"]
    geo_label(img, cam, P["mbac"], T["north"], 1.95, 3.1, t, 78, (255, 255, 255), dy=0, stroke=((40, 40, 40), 0.04))
    geo_label(img, cam, P["mnam"], T["south"], 2.45, 3.1, t, 78, (255, 255, 255), stroke=((40, 40, 40), 0.04))
    arrow_label(img, cam, P["hienluong"], T["river"], 3.45, 5.1, t, 34, -40, -150)
    geo_label(img, cam, P["vinhlinh"], T["vinhlinh"], 5.3, 6.35, t, 30, dy=-55 * zk ** 0.2)
    geo_label(img, cam, P["giolinh"], T["giolinh"], 5.4, 6.35, t, 30, dy=40 * zk ** 0.2)
    geo_label(img, cam, P["vn"], T["vn"], 6.75, 8.15, t, 70, stroke=((40, 40, 40), 0.04))
    geo_label(img, cam, P["hoangsa"], T["hoangsa"], 7.0, 11.75, t, 30, dx=-40, dy=-40)
    geo_label(img, cam, P["truongsa"], T["truongsa"], 7.15, 11.75, t, 30, dx=-60, dy=-46)
    geo_label(img, cam, P["mbac"], T["north"], 8.55, 11.75, t, 120, stroke=((40, 40, 40), 0.04))
    geo_label(img, cam, P["mnam"], T["south"], 10.35, 11.75, t, 120, stroke=((40, 40, 40), 0.04))
    arrow_label(img, cam, P["hienluong"], T["river"], 11.85, 99, t, 46 if t < 21 else 52, -60, -230 if t < 21 else -260)
    if t < 21.05:
        sc, al = pop(t, 12.65)
        blit(img, smallcaps(T["sea"], 72, YEL, stroke=((0, 0, 0), 0.05)), W * 0.70, H * 0.27, sc, al)
    else:
        k = ease((t - 21.05) / 1.5); u, v = cam.P(*merc(107.155, 17.13))
        blit(img, smallcaps(T["sea"], 92, YEL, stroke=((0, 0, 0), 0.05)), W * 0.70 + (u - W * 0.70) * k, H * 0.27 + (v - H * 0.27) * k, 0.78 + 0.22 * k, 1.0)
    arrow_label(img, cam, P["cuatung"], T["cuatung"], 13.6, 20.9, t, 28, 110, -90, YEL)
    geo_label(img, cam, P["vt17"], T["vt17"], 15.6, 20.9, t, 34, YEL, dy=-46, stroke=((0, 0, 0), 0.05))
    geo_label(img, cam, P["dmz"], T["dmz"], 17.1, 20.9, t, 24, dy=70)
    geo_label(img, cam, P["hienluong"], T["bridge"], 22.7, 99, t, 30, dy=62)
    draw_vehicles(img, cam, t, ("plane",))
    # ---- băng tiêu đề ----
    if t >= 23.35:
        k = ease((t - 23.35) / 0.35)
        f = F(FX, 52); txt = T["banner"]; tw = f.getlength(txt)
        bw, bh_ = tw + 50, 84; x0 = W / 2 - bw / 2 + (1 - k) * -W * 0.6; y0 = 330
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rectangle((x0, y0, x0 + bw, y0 + bh_), fill=(255, 255, 255, 255))
        d.text((x0 + bw / 2, y0 + bh_ / 2 + 2), txt, font=f, fill=(10, 10, 10, 255), anchor="mm")
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(5)).point(lambda v: v) if False else lay)
    # ---- nguồn ảnh ----
    d = ImageDraw.Draw(img)
    d.text((W - 20, H - 18), T["credit"], font=F(FX, 17), fill=(255, 255, 255, 120), anchor="rs")
    # ---- chuyển cảnh nhanh (cut): chớp sáng nhẹ ----
    for tc in (3.15, 11.85):
        if 0 <= t - tc < 0.12:
            img = Image.blend(img, Image.new("RGBA", img.size, (255, 255, 255, 255)), 0.25 * (1 - (t - tc) / 0.12))
    if t > DUR - 0.4: img = Image.blend(img, Image.new("RGBA", img.size, (0, 0, 0, 255)), ease((t - DUR + 0.4) / 0.4))
    return img.convert("RGB")


# chuẩn hoá khoá camera: lon/lat -> mercator
_c2 = []
for (t_, lo, la, z_, c_) in CAM:
    x, y = merc(lo, la); _c2.append((t_, lo, la, z_, c_))
_cam_merc = [(t_, *merc(lo, la), z_, c_) for (t_, lo, la, z_, c_) in CAM]


def cam_at(t):  # noqa: F811  (bản dùng toạ độ mercator)
    ks = _cam_merc
    for i in range(len(ks) - 1):
        a, b = ks[i], ks[i + 1]
        if b[0] == a[0]: continue
        if a[0] <= t < b[0]:
            u = ease_io((t - a[0]) / (b[0] - a[0]))
            z = a[3] + (b[3] - a[3]) * u
            if abs(b[3] - a[3]) > 0.3:
                wa, wb, w = 2 ** -a[3], 2 ** -b[3], 2 ** -z
                v = min(1, max(0, (w - wa) / (wb - wa)))
            else:
                v = u
            return a[1] + (b[1] - a[1]) * v, a[2] + (b[2] - a[2]) * v, z
    return ks[-1][1], ks[-1][2], ks[-1][3]


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "test":
        os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
        for s in sys.argv[2:]:
            t0 = time.time(); fi = int(float(s) * FPS)
            render(fi).save(os.path.join(HERE, "test", f"t_{float(s):05.2f}.jpg"), quality=90); print(s, round(time.time() - t0, 2), flush=True)
    else:
        from multiprocessing import Pool
        out = os.path.join(HERE, "frames"); os.makedirs(out, exist_ok=True)
        todo = [i for i in range(NF) if not os.path.exists(os.path.join(out, f"f_{i:04d}.jpg"))]
        def job(i):
            render(i).save(os.path.join(out, f"f_{i:04d}.jpg"), quality=93); return i
        with Pool(4) as p:
            for k, i in enumerate(p.imap_unordered(job, todo, chunksize=4)):
                if k % 60 == 0: print("frame", k, "/", len(todo), flush=True)
        print("RENDER_DONE")
