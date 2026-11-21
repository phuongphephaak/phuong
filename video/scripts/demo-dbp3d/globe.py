"""Mở đầu: địa cầu xoay → zoom vào Đông Dương → Tây Bắc Việt Nam → ghim Điện Biên Phủ.
Dùng: from globe import globe_frame; globe_frame(t, dur) -> PIL RGBA 1920x1080"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import map_coordinates

HERE = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(HERE)
W, H = 1920, 1080
INTER = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
INTER_R = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
SERIF_B = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
OSWALD = os.path.join(S, "gfx", "oswald-700.ttf")
_fc = {}
def F(p, s):
    if not os.path.exists(p): p = INTER
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]
ease = lambda x: 0 if x <= 0 else 1 if x >= 1 else x * x * (3 - 2 * x)

EARTH = np.asarray(Image.open(os.path.join(S, "gfx", "dl", "earth-blue-marble.jpg")).convert("RGB")).astype(np.float32)
EH, EW = EARTH.shape[:2]
TOPO = np.asarray(Image.open(os.path.join(S, "gfx", "dl", "earth-topology.png")).convert("L")).astype(np.float32) / 255
TOPO = np.asarray(Image.fromarray((TOPO * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))).astype(np.float32) / 255
TH_, TW_ = TOPO.shape
DBP = (103.02, 21.39); HN = (105.85, 21.03)

# biên giới quốc gia (Natural Earth 1:50m), chỉ lấy vùng Đông Nam Á
_geo = json.load(open(os.path.join(S, "mapdata", "ne", "admin0_50m.geojson")))
POLYS = []   # (iso, [ring arrays])
for f in _geo["features"]:
    iso = f["properties"].get("ADM0_A3"); g = f["geometry"]
    rings = g["coordinates"] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
    if g["type"] == "Polygon": rings = [rings[0]]
    keep = []
    for r in rings:
        a = np.array(r)
        if a[:, 0].max() > 80 and a[:, 0].min() < 130 and a[:, 1].max() > -12 and a[:, 1].min() < 40: keep.append(a)
    if keep: POLYS.append((iso, keep))

rs = np.random.default_rng(4)
STARS = [(rs.uniform(0, W), rs.uniform(0, H), rs.uniform(0.3, 1.0), rs.uniform(0.6, 1.8)) for _ in range(380)]


def fwd(lon, lat, lon0, lat0, R):
    l, p = np.radians(lon), np.radians(lat); l0, p0 = math.radians(lon0), math.radians(lat0)
    x = R * np.cos(p) * np.sin(l - l0)
    y = R * (math.cos(p0) * np.sin(p) - math.sin(p0) * np.cos(p) * np.cos(l - l0))
    vis = math.sin(p0) * np.sin(p) + math.cos(p0) * np.cos(p) * np.cos(l - l0)
    return W / 2 + x, H / 2 - y, vis


def satellite(lon0, lat0, R):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    x = (xx - W / 2) / R; y = -(yy - H / 2) / R
    rho = np.hypot(x, y); inside = rho < 1
    c = np.arcsin(np.clip(rho, 0, 1)); p0 = math.radians(lat0)
    with np.errstate(invalid="ignore", divide="ignore"):
        lat = np.arcsin(np.clip(np.cos(c) * math.sin(p0) + np.where(rho > 0, y * np.sin(c) * math.cos(p0) / rho, 0), -1, 1))
        lon = math.radians(lon0) + np.arctan2(x * np.sin(c), rho * np.cos(c) * math.cos(p0) - y * np.sin(c) * math.sin(p0))
    u = ((np.degrees(lon) + 180) % 360) / 360 * EW; v = (90 - np.degrees(lat)) / 180 * EH
    global LASTUV
    LASTUV = (u / EW, v / EH)
    out = np.zeros((H, W, 3), np.float32)
    for ch in range(3):
        out[..., ch] = map_coordinates(EARTH[..., ch], [v, u], order=1, mode="wrap")
    # chiếu sáng nhẹ + tối dần ở rìa cầu
    shade = np.clip(np.cos(c), 0, 1) ** 0.35
    out = out * (0.55 + 0.45 * shade)[..., None] * np.array([0.92, 0.97, 1.05])
    return out, inside, rho


def starfield():
    im = Image.new("RGB", (W, H), (4, 6, 12)); d = ImageDraw.Draw(im)
    for (x, y, b, s) in STARS:
        v = int(70 + 160 * b); d.ellipse((x - s / 2, y - s / 2, x + s / 2, y + s / 2), fill=(v, v, min(255, v + 15)))
    return np.asarray(im).astype(np.float32)


STAR = None


def poly_layer(lon0, lat0, R, styl):
    """vẽ lục địa/biên giới kiểu bản đồ (vẽ 2x rồi thu nhỏ để mịn)"""
    SS = 2
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    vn = []
    for iso, rings in POLYS:
        for a in rings:
            x, y, vis = fwd(a[:, 0], a[:, 1], lon0, lat0, R)
            if vis.max() <= 0: continue
            if x.max() < -200 or x.min() > W + 200 or y.max() < -200 or y.min() > H + 200: continue
            pts = list(zip((x * SS).tolist(), (y * SS).tolist()))
            if len(pts) < 3: continue
            if iso == "VNM":
                vn.append(pts); continue
            if styl:
                d.polygon(pts, fill=(176, 166, 140, int(255 * styl)))
            d.line(pts + [pts[0]], fill=(245, 240, 225, 150), width=2 * SS)
    for pts in vn:
        if styl:
            d.polygon(pts, fill=(226, 206, 160, int(255 * styl)))
        d.line(pts + [pts[0]], fill=(225, 45, 40, 255), width=3 * SS, joint="curve")
    return lay.resize((W, H), Image.LANCZOS)


def label(img, x, y, s, size, a, color=(250, 245, 230), sp=6, font=INTER, dot=False):
    if a <= 0: return
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); f = F(font, size)
    wsum = sum(d.textlength(c, font=f) for c in s) + sp * (len(s) - 1)
    def draw(dd, col, dy=0):
        if dot: dd.ellipse((x - 7, y - 7, x + 7, y + 7), fill=col, outline=(0, 0, 0, int(200 * a)) if col[0] > 100 else None, width=2)
        xx = x - wsum / 2 if not dot else x + 18
        yy = y if not dot else y
        for c in s:
            dd.text((xx, yy + dy), c, font=f, fill=col, anchor="lm"); xx += dd.textlength(c, font=f) + sp
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); draw(ImageDraw.Draw(sh), (0, 0, 0, int(230 * a)), 2)
    sh = sh.filter(ImageFilter.GaussianBlur(5)); img.alpha_composite(sh)
    draw(d, (*color, int(255 * a))); img.alpha_composite(lay)


def pin(img, x, y, t, a):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k in range(2):
        ph = (t * 0.9 + k * 0.5) % 1
        r = 14 + 70 * ph; al = int(220 * (1 - ph) * a)
        d.ellipse((x - r, y - r, x + r, y + r), outline=(255, 70, 50, al), width=4)
    d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=(230, 40, 35, int(255 * a)), outline=(255, 255, 255, int(255 * a)), width=4)
    img.alpha_composite(lay)


def box(img, px, py, l1, l2, a):
    if a <= 0: return
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f1, f2 = F(SERIF_B, 46), F(INTER_R, 26)
    w = int(max(d.textlength(l1, font=f1) + 5 * len(l1), d.textlength(l2, font=f2)) + 70); h = 116
    x0, y0 = int(px - w / 2), int(py - h - 95)
    d.rounded_rectangle((x0 + 5, y0 + 7, x0 + w + 5, y0 + h + 7), 14, fill=(0, 0, 0, 120))
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 14, fill=(14, 14, 14, 238), outline=(235, 228, 210, 255), width=3)
    d.polygon([(px - 20, y0 + h - 2), (px + 20, y0 + h - 2), (px, y0 + h + 32)], fill=(14, 14, 14, 238))
    d.line([(px - 20, y0 + h), (px, y0 + h + 32), (px + 20, y0 + h)], fill=(235, 228, 210, 255), width=3)
    xx = x0 + w / 2 - (d.textlength(l1, font=f1) + 5 * (len(l1) - 1)) / 2
    for c in l1:
        d.text((xx, y0 + 44), c, font=f1, fill=(255, 255, 255, 255), anchor="lm"); xx += d.textlength(c, font=f1) + 5
    d.text((x0 + w / 2, y0 + 88), l2, font=f2, fill=(235, 210, 150, 255), anchor="mm")
    sc = 0.85 + 0.15 * ease(a)
    if sc < 1:
        lay = lay.resize((int(W * sc), int(H * sc)), Image.LANCZOS)
        big = Image.new("RGBA", (W, H), (0, 0, 0, 0)); big.alpha_composite(lay, (int(px * (1 - sc)), int(py * (1 - sc))))
        lay = big
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    img.alpha_composite(lay)


def dashed(img, p0, p1, k, a):
    if a <= 0 or k <= 0: return
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    (x0, y0), (x1, y1) = p0, p1; L = math.hypot(x1 - x0, y1 - y0); n = int(L / 22)
    for i in range(n):
        u0, u1 = i / n, (i + 0.55) / n
        if u0 > k: break
        u1 = min(u1, k)
        d.line([(x0 + (x1 - x0) * u0, y0 + (y1 - y0) * u0), (x0 + (x1 - x0) * u1, y0 + (y1 - y0) * u1)], fill=(255, 245, 225, int(235 * a)), width=4)
    img.alpha_composite(lay)


def globe_frame(t, dur):
    global STAR
    if STAR is None: STAR = starfield()
    # quỹ đạo camera: xoay địa cầu tới Đông Dương rồi zoom liên tục (log)
    kr = ease((t - 0.2) / 2.6)
    lon0 = 62 + (104.3 - 62) * kr; lat0 = 8 + (21.25 - 8) * kr
    kz = ease((t - 0.9) / (dur - 1.6)) ** 1.15
    R = math.exp(math.log(330) + (math.log(25000) - math.log(330)) * kz)
    styl = ease((R - 1800) / 3500)          # chuyển từ ảnh vệ tinh sang bản đồ vẽ
    sat, inside, rho = satellite(lon0, lat0, R)
    if styl < 1:
        a = np.where(inside[..., None], sat, STAR)
        # quầng khí quyển
        glow = np.clip(1 - np.abs(rho - 1) / 0.06, 0, 1) * (rho > 0.97)
        a = a + glow[..., None] * np.array([70, 130, 220]) * 0.8
    else:
        a = np.zeros((H, W, 3), np.float32)
    if styl > 0:
        sea = np.zeros((H, W, 3), np.float32) + np.array([22, 36, 50])
        a = a * (1 - styl) + sea * styl
    a *= ease(t / 0.6)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    ba = ease((R - 600) / 900)
    if ba > 0:
        pl = poly_layer(lon0, lat0, R, styl)
        if ba < 1: pl.putalpha(pl.getchannel("A").point(lambda v: int(v * ba)))
        img.alpha_composite(pl)
    if styl > 0:   # bóng đổ địa hình (núi Tây Bắc) trên bản đồ vẽ
        u, v = LASTUV
        hgt = map_coordinates(TOPO, [v * TH_, u * TW_], order=3, mode="wrap")
        gy, gx = np.gradient(hgt)
        k = R / 2500.0
        sh = np.clip(1 + (-gx + gy) * 40 / max(1.0, k ** 0.5), 0.55, 1.3)
        land = np.asarray(img.getchannel("A"))  # placeholder
        arr = np.asarray(img.convert("RGB")).astype(np.float32)
        isl = (arr.mean(-1) > 90)[..., None]
        arr = np.where(isl, arr * (1 + (sh[..., None] - 1) * styl * 0.9), arr)
        hy_, hx_ = np.mgrid[0:H, 0:W]; r = np.hypot((hx_ - W / 2) / (W / 2), (hy_ - H / 2) / (H / 2))
        arr = arr * (1 - 0.45 * styl * np.clip(r - 0.45, 0, 1) ** 1.5)[..., None]
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    # vân giấy nhẹ + vignette
    P = lambda lon, lat: fwd(np.array([lon]), np.array([lat]), lon0, lat0, R)[:2]
    pp = lambda lon, lat: tuple(float(v[0]) for v in P(lon, lat))
    # nhãn vùng (mờ dần khi zoom sâu)
    la = ease((R - 900) / 700) * (1 - ease((R - 7000) / 3000))
    x, y = pp(106.9, 14.2); label(img, x, y, "VIỆT NAM", 46, la, (255, 236, 200), 10)
    x, y = pp(114.8, 12.6); label(img, x, y, "BIỂN ĐÔNG", 30, la * 0.9, (170, 205, 235), 10)
    x, y = pp(111.9, 16.5); label(img, x, y, "QĐ. HOÀNG SA", 20, la * 0.9, (230, 220, 200), 3, dot=True)
    x, y = pp(114.2, 9.6); label(img, x, y, "QĐ. TRƯỜNG SA", 20, la * 0.9, (230, 220, 200), 3, dot=True)
    lb = ease((R - 2500) / 1500)
    x, y = pp(102.2, 19.6); label(img, x, y, "LÀO", 38, lb * 0.85, (225, 215, 195), 12)
    x, y = pp(104.4, 23.0); label(img, x, y, "TRUNG QUỐC", 34, lb * 0.85, (225, 215, 195), 10)
    x, y = pp(100.5, 16.5); label(img, x, y, "THÁI LAN", 30, lb * 0.7, (225, 215, 195), 10)
    # Hà Nội + đường chim bay + ghim ĐBP + hộp chú thích
    t1 = dur - 2.3
    hx, hy = pp(*HN); dx, dy = pp(*DBP)
    ha = ease((t - (t1 - 0.4)) / 0.4)
    label(img, hx, hy, "HÀ NỘI", 30, ha, (255, 255, 255), 4, dot=True)
    dashed(img, (hx, hy), (dx, dy), ease((t - t1) / 0.8), ha)
    if ha > 0:
        mx, my = (hx + dx) / 2, (hy + dy) / 2
        label(img, mx, my + 34, "≈ 300 KM", 26, ease((t - t1 - 0.6) / 0.4), (255, 230, 170), 4)
    pa = ease((t - (t1 + 0.3)) / 0.35)
    if pa > 0: pin(img, dx, dy, t, pa)
    box(img, dx, dy, "ĐIỆN BIÊN PHỦ", "Lòng chảo Mường Thanh · Tây Bắc Việt Nam", ease((t - (t1 + 0.6)) / 0.45))
    # zoom cuối hơi tối dần về sa bàn
    return img


if __name__ == "__main__":
    import sys
    for tt in sys.argv[1:]:
        globe_frame(float(tt), 6.4).convert("RGB").save(os.path.join(HERE, "t2", f"g_{tt}.jpg"), quality=88)
