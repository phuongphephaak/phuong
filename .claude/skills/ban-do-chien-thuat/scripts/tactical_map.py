"""Bản đồ địa hình Waterloo kiểu sa bàn chiến thuật (1 px = 1 m).  python3 wl_map.py"""
import math, os, sys, time, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.spatial import cKDTree
from scipy import ndimage

HERE = os.path.abspath(os.environ.get("WORK", os.getcwd()))   # thư mục làm việc (đầu ra)
MW, MH = 6144, 4096
t0 = time.time()
rng = np.random.default_rng(7)


def log(*a):
    print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)


def fbm(shape, octaves, seed, base=4, persist=0.55):
    r = np.random.default_rng(seed); out = np.zeros(shape, np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        f = base * 2 ** o
        gh, gw = int(f * shape[0] / max(shape)) + 3, int(f * shape[1] / max(shape)) + 3
        g = r.standard_normal((gh, gw)).astype(np.float32)
        out += amp * np.asarray(Image.fromarray(g).resize((shape[1], shape[0]), Image.BICUBIC))
        tot += amp; amp *= persist
    return out / tot


def poly_dist(xx, yy, pts):
    d = np.full(xx.shape, 1e9, np.float32)
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        vx, vy = bx - ax, by - ay; L2 = vx * vx + vy * vy
        t = np.clip(((xx - ax) * vx + (yy - ay) * vy) / L2, 0, 1)
        d = np.minimum(d, np.hypot(xx - ax - t * vx, yy - ay - t * vy))
    return d


def wobble(pts, amp, step, seed):
    """chia nhỏ polyline và làm lệch tự nhiên"""
    r = np.random.default_rng(seed); out = []
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        L = math.hypot(bx - ax, by - ay); n = max(2, int(L / step))
        nx, ny = -(by - ay) / L, (bx - ax) / L
        for i in range(n):
            u = i / n; w = amp * (math.sin(u * math.pi * 2.3 + seed) * 0.6 + r.uniform(-0.5, 0.5)) * math.sin(u * math.pi)
            out.append((ax + (bx - ax) * u + nx * w, ay + (by - ay) * u + ny * w))
    out.append(pts[-1]); return out


# ---------------- dữ liệu địa lý (tự thiết kế theo bố trí lịch sử) ----------------
ROADS = {
    "brussels": [(2650, 0), (2700, 500), (2760, 1100), (2850, 1700), (2930, 2400), (2980, 3100), (3050, 4096)],
    "nivelles": [(2760, 1100), (2500, 1500), (2200, 1950), (1900, 2500), (1500, 3200), (1100, 4096)],
    "ohain": [(700, 1550), (1500, 1680), (2200, 1580), (2800, 1470), (3500, 1260), (4300, 1020), (5200, 780), (6144, 600)],
    "plancenoit": [(2950, 2450), (3600, 2900), (4300, 3150), (5000, 3300), (6144, 3450)],
    "papelotte": [(4200, 1600), (4300, 2000), (4350, 2600), (4400, 3150)],
    "braine_s": [(700, 1550), (900, 2500), (1000, 4096)],
    "braine_n": [(700, 1550), (400, 900), (200, 0)],
    "waterloo_e": [(2650, 300), (4000, 250), (5300, 200), (6144, 300)],
    "msj_w": [(2760, 1100), (1700, 1450), (700, 1550)],
    "frisch": [(4300, 1020), (4500, 1450), (4850, 1560), (5300, 1900)],
    "rossomme": [(2980, 3100), (2200, 3400), (1300, 3700)],
}
STREAMS = [
    [(5650, 0), (5350, 450), (5000, 900), (4700, 1350), (4650, 1700), (4900, 2200), (5150, 2800), (5500, 3400), (5900, 4096)],
    [(250, 0), (450, 700), (560, 1400), (420, 2200), (280, 3100), (330, 4096)],
    [(4650, 1700), (4300, 2400), (4450, 3200), (4300, 4096)],
    [(1300, 0), (1450, 500), (1500, 900), (1350, 1300)],
]
VILLAGES = {  # tên, vị trí, số nhà, bán kính
    "Waterloo": ((2660, 260), 60, 160), "Mont St Jean": ((2770, 1080), 30, 90), "Braine l'Alleud": ((690, 1560), 70, 170),
    "La Haye Sainte": ((2855, 1745), 6, 25), "Papelotte": ((4210, 1610), 8, 40), "La Haye": ((4500, 1450), 12, 50),
    "Frischermont": ((4860, 1570), 10, 45), "Plancenoit": ((4420, 3160), 45, 130), "La Belle Alliance": ((2950, 2490), 5, 30),
    "Rossomme": ((3000, 3300), 8, 45), "Maransart": ((5620, 2900), 25, 90), "Ohain": ((5750, 580), 35, 120),
    "Merbe Braine": ((1700, 1480), 18, 70), "Hougoumont": ((2050, 2260), 4, 20),
}
RIDGE1 = [(300, 1600), (1500, 1700), (2200, 1600), (2800, 1460), (3500, 1250), (4300, 1000), (5200, 780), (6144, 650)]
RIDGE2 = [(900, 2750), (2200, 2620), (2950, 2470), (3700, 2230), (4500, 2050), (5000, 1950)]

# ---------------- độ cao + đổ bóng đồi ----------------
ys, xs = np.mgrid[0:MH, 0:MW].astype(np.float32)
log("grid")
Z = 34 * fbm((MH, MW), 4, 1, base=2, persist=0.5) + 1.2 * fbm((MH, MW), 4, 2, base=60)
d1 = poly_dist(xs, ys, RIDGE1); Z += 34 * np.exp(-(d1 / 420) ** 2) + 10 * np.exp(-(d1 / 900) ** 2)
d2 = poly_dist(xs, ys, RIDGE2); Z += 26 * np.exp(-(d2 / 380) ** 2)
sd = np.full(xs.shape, 1e9, np.float32)
for s in STREAMS:
    sd = np.minimum(sd, poly_dist(xs, ys, s))
Z -= 32 * np.exp(-(sd / 260) ** 2) + 12 * np.exp(-(sd / 700) ** 2)
del d2
log("height")
gy, gx = np.gradient(ndimage.gaussian_filter(Z, 4))
ex = 5.5
nx, ny, nz = -gx * ex, -gy * ex, np.ones_like(gx)
nl = np.sqrt(nx * nx + ny * ny + nz * nz)
L = np.array([-0.55, -0.62, 0.56]); L /= np.linalg.norm(L)
shade = (nx * L[0] + ny * L[1] + nz * L[2]) / nl
del gx, gy, nx, ny, nz, nl
shade = np.clip(shade, 0, 1)
s0 = shade.mean(); shade = shade / s0          # 1 = trung tính
log("shade", float(s0))

# ---------------- ô ruộng (Voronoi) ----------------
pts = []
for gy_ in np.arange(-200, MH + 300, 95):
    for gx_ in np.arange(-200, MW + 300, 260):
        pts.append((gx_ + rng.uniform(-110, 110) + (gy_ // 95 % 2) * 130, gy_ + rng.uniform(-35, 35)))
pts = np.array(pts, np.float32); kd = cKDTree(pts); NP = len(pts)
fid = np.empty((MH, MW), np.int32); fe = np.empty((MH, MW), np.float32)
CH = 256
phi = 0.9 * fbm((MH, MW), 2, 33, base=2) - 0.35
cx0, cy0 = MW / 2, MH / 2
wx = cx0 + (xs - cx0) * np.cos(phi) + (ys - cy0) * np.sin(phi) + 14 * fbm((MH, MW), 4, 31, base=20)
wy = cy0 - (xs - cx0) * np.sin(phi) + (ys - cy0) * np.cos(phi) + 14 * fbm((MH, MW), 4, 32, base=20)
del phi
for r0 in range(0, MH, CH):
    q = np.c_[wx[r0:r0 + CH].ravel(), wy[r0:r0 + CH].ravel()]
    dd, ii = kd.query(q, k=2)
    ab = np.hypot(*(pts[ii[:, 0]] - pts[ii[:, 1]]).T)
    fid[r0:r0 + CH] = ii[:, 0].reshape(-1, MW)
    fe[r0:r0 + CH] = ((dd[:, 1] ** 2 - dd[:, 0] ** 2) / (2 * ab)).reshape(-1, MW)
del wx, wy
log("fields")
PAL = np.array([[0.64, 0.61, 0.37], [0.60, 0.59, 0.35], [0.66, 0.62, 0.39], [0.68, 0.63, 0.41],
                [0.58, 0.58, 0.34], [0.65, 0.60, 0.38], [0.62, 0.61, 0.37], [0.70, 0.65, 0.43]], np.float32)
ftint = PAL[rng.integers(0, len(PAL), NP)] * rng.uniform(0.96, 1.04, (NP, 1)).astype(np.float32)
fang = rng.uniform(0, np.pi, NP).astype(np.float32)
fper = rng.uniform(4.5, 7.5, NP).astype(np.float32)
fcon = rng.choice([0.0, 0.04, 0.06, 0.08, 0.10], NP).astype(np.float32)
C = ftint[fid]
a = fang[fid]
hatch = np.sin(2 * np.pi * (xs * np.cos(a) + ys * np.sin(a)) / fper[fid])
C *= (1 + fcon[fid] * hatch * (0.6 + 0.4 * fbm((MH, MW), 3, 41, base=60)))[..., None]
del a, hatch
# biến thiên màu lớn + nhỏ
n1 = fbm((MH, MW), 5, 51, base=6); n2 = fbm((MH, MW), 4, 52, base=140)
C *= (1 + 0.07 * n1 + 0.04 * n2)[..., None]
# viền ô ruộng
C *= (1 - 0.08 * np.clip(1.6 - fe, 0, 1))[..., None]
log("field colour")

# ---------------- phối màu theo đổ bóng: sáng -> vàng kem, tối -> ô liu sẫm
lit = np.clip((shade - 1) * 1.6, -1, 1.2)
C = C * (0.62 + 0.62 * shade[..., None] ** 1.3)
warm = np.array([1.05, 1.0, 0.86], np.float32); cool = np.array([0.80, 0.90, 0.72], np.float32)
C *= np.where(lit[..., None] > 0, 1 + (warm - 1) * lit[..., None], 1 + (cool - 1) * (-lit[..., None]))
# thung lũng ẩm xanh hơn
C = C * (1 - 0.25 * np.exp(-(sd / 350) ** 2))[..., None] + np.array([0.30, 0.40, 0.16], np.float32) * 0.25 * np.exp(-(sd / 350) ** 2)[..., None]
g_ = C.mean(-1, keepdims=True); C = g_ + (C - g_) * 0.9
lum = C.mean(-1); p5, p95 = np.percentile(lum[::7, ::7], [5, 95])
nl_ = 0.30 + (lum - p5) / (p95 - p5) * (0.74 - 0.30)
nl_ = np.where(nl_ > 0.62, 0.62 + (nl_ - 0.62) * 0.6, nl_)
C *= (nl_ / np.maximum(lum, 1e-3))[..., None]; del lum, nl_, g_
log("colour")

img = Image.fromarray((np.clip(C, 0, 1) * 255).astype(np.uint8)); del C
dr = ImageDraw.Draw(img, "RGBA")

# ---------------- suối ----------------
for k, s in enumerate(STREAMS):
    p = wobble(s, 60, 40, 100 + k); p = wobble(p, 6, 8, 200 + k)
    dr.line(p, fill=(60, 75, 40, 140), width=11, joint="curve")
    dr.line(p, fill=(70, 120, 150, 255), width=6, joint="curve")
    dr.line(p, fill=(130, 175, 195, 200), width=2, joint="curve")
for (px, py, rr) in [(4650, 1700, 28), (5520, 3420, 40), (5040, 2450, 22), (560, 1400, 25), (4620, 1530, 18)]:
    dr.ellipse((px - rr, py - rr * 0.6, px + rr, py + rr * 0.6), fill=(70, 120, 150, 255), outline=(60, 75, 40, 160), width=3)
log("streams")

# ---------------- đường ----------------
for k, (nm, p) in enumerate(ROADS.items()):
    main = nm in ("brussels", "nivelles", "ohain")
    p = wobble(p, 25 if main else 45, 30, 300 + k); p = wobble(p, 3, 6, 400 + k)
    dr.line(p, fill=(80, 64, 40, 170), width=7 if main else 5, joint="curve")
    dr.line(p, fill=(150, 128, 88, 150), width=3 if main else 2, joint="curve")
# lối mòn giữa ruộng (cạnh voronoi ngẫu nhiên)
for i in range(140):
    a0 = pts[rng.integers(0, NP)]; ang = rng.uniform(0, 6.28); L_ = rng.uniform(250, 900)
    p = [(a0[0], a0[1]), (a0[0] + L_ * math.cos(ang), a0[1] + L_ * math.sin(ang))]
    p = wobble(p, 40, 25, 500 + i)
    dr.line(p, fill=(95, 80, 50, 70), width=2, joint="curve")
log("roads")

# ---------------- rừng + hàng rào ----------------
forest = np.zeros((MH, MW), bool)
nf = fbm((MH, MW), 5, 61, base=8)
wgt = 0.55 * np.exp(-((sd - 450) / 380) ** 2) * (1 / (1 + np.exp(-(xs - 4300) / 250)))
for (fx_, fy_, rx_, ry_, w_) in [(5400, 2550, 800, 650, 0.8), (3300, 300, 700, 300, 0.45), (1000, 350, 600, 350, 0.5),
                                 (5900, 1300, 500, 600, 0.6), (300, 2700, 400, 700, 0.45), (3900, 3800, 600, 350, 0.45)]:
    wgt += w_ * np.exp(-(((xs - fx_) / rx_) ** 2 + ((ys - fy_) / ry_) ** 2))
nf2 = nf + 0.25 * fbm((MH, MW), 4, 62, base=50)
forest |= (nf2 + wgt) > 0.70
forest |= (np.abs(xs - 2020) < 150) & (np.abs(ys - 2330) < 170)          # rừng Hougoumont
forest &= ~((np.abs(xs - 2050) < 80) & (np.abs(ys - 2240) < 60))
forest &= (sd > 40)
rd = np.full(xs.shape, 1e9, np.float32)
for nm in ("brussels", "nivelles", "ohain"):
    rd = np.minimum(rd, poly_dist(xs, ys, ROADS[nm]))
forest &= rd > 30
forest &= d1 > 260          # sườn núi chính trống trải
del rd, nf, nf2, wgt, sd
fy, fx = np.nonzero(forest[::3, ::3]); fy = fy * 3; fx = fx * 3
sel = rng.random(len(fx)) < 0.62
tx = fx[sel] + rng.uniform(-1.5, 1.5, sel.sum()); ty = fy[sel] + rng.uniform(-1.5, 1.5, sel.sum())
# hàng rào: cây dọc viền ô ruộng gần làng
hy, hx = np.nonzero((fe[::2, ::2] < 1.2)); hy = hy * 2; hx = hx * 2
near = np.zeros(len(hx), bool)
for (vx, vy), n, r in VILLAGES.values():
    near |= np.hypot(hx - vx, hy - vy) < r * 2.6
hedge_keep = ((fid[hy, hx] * 7919) % 5 == 0)
hxs, hys = [], []
for k_, nm_ in enumerate(("ohain", "papelotte", "frisch", "plancenoit")):
    pp = wobble(ROADS[nm_], 25, 30, 300 + list(ROADS).index(nm_))
    for (ax, ay), (bx, by) in zip(pp[:-1], pp[1:]):
        L_ = math.hypot(bx - ax, by - ay); n_ = int(L_ / 4.5)
        if n_ == 0: continue
        nx_, ny_ = -(by - ay) / L_, (bx - ax) / L_
        for side in (-1, 1):
            if rng.random() < (0.55 if side < 0 else 0.8) or (nm_ == "ohain" and ax < 2950): continue
            for i in range(n_):
                u = i / n_
                hxs.append(ax + (bx - ax) * u + side * nx_ * 9 + rng.uniform(-1, 1)); hys.append(ay + (by - ay) * u + side * ny_ * 9 + rng.uniform(-1, 1))
tx = np.r_[tx, hxs]; ty = np.r_[ty, hys]
log("trees", len(tx))
order = np.argsort(ty); tx, ty = tx[order], ty[order]
trees = Image.new("RGBA", (MW, MH), (0, 0, 0, 0)); td = ImageDraw.Draw(trees)
rad = rng.uniform(2.8, 5.0, len(tx))
for x, y, r in zip(tx, ty, rad):
    td.ellipse((x - r + 2.5, y - r + 2.5, x + r + 3.5, y + r + 3.5), fill=(25, 30, 12, 150))
shadow_l = trees.filter(ImageFilter.GaussianBlur(1.2))
trees = Image.new("RGBA", (MW, MH), (0, 0, 0, 0)); td = ImageDraw.Draw(trees)
tone = rng.uniform(0.75, 1.2, len(tx))
for x, y, r, k in zip(tx, ty, rad, tone):
    td.ellipse((x - r, y - r, x + r, y + r), fill=(int(46 * k), int(56 * k), int(24 * k), 255))
    r2 = r * 0.55
    td.ellipse((x - r * 0.75 - r2 * 0.2, y - r * 0.75 - r2 * 0.2, x - r * 0.75 + r2 * 1.6, y - r * 0.75 + r2 * 1.6),
               fill=(int(96 * k), int(104 * k), int(52 * k), 255))
img = Image.alpha_composite(Image.alpha_composite(img.convert("RGBA"), shadow_l), trees).convert("RGB")
del trees, shadow_l
dr = ImageDraw.Draw(img, "RGBA")
log("trees drawn")

# ---------------- làng, nông trại ----------------
houses = []
for nm, ((vx, vy), n, r) in VILLAGES.items():
    for i in range(n):
        a_ = rng.uniform(0, 6.28); d_ = r * math.sqrt(rng.random())
        hx_, hy_ = vx + d_ * math.cos(a_), vy + d_ * math.sin(a_) * 0.8
        w, h = rng.uniform(9, 16), rng.uniform(6, 9); ang = rng.choice([0.2, 0.2 + math.pi / 2]) + rng.uniform(-0.15, 0.15)
        houses.append((hx_, hy_, w, h, ang))
# trang trại có tường bao
for (cx, cy, w, h) in [(2050, 2240, 70, 55), (2855, 1745, 45, 40), (4860, 1570, 50, 40)]:
    dr.rectangle((cx - w, cy - h, cx + w, cy + h), outline=(120, 100, 75, 255), width=3)
# vườn cây ăn quả Hougoumont: hàng cây thẳng
for gx_ in range(1975, 2130, 11):
    for gy_ in range(2310, 2400, 11):
        dr.ellipse((gx_ - 3 + 2, gy_ - 3 + 2, gx_ + 3 + 2, gy_ + 3 + 2), fill=(25, 30, 12, 120))
        dr.ellipse((gx_ - 3, gy_ - 3, gx_ + 3, gy_ + 3), fill=(62, 78, 30, 255))
for (hx_, hy_, w, h, ang) in houses:
    c, s_ = math.cos(ang), math.sin(ang)
    q = [(hx_ + c * u - s_ * v, hy_ + s_ * u + c * v) for u, v in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
    dr.polygon([(x + 4, y + 4) for x, y in q], fill=(30, 28, 15, 120))
    roof = (150, 82, 55) if rng.random() < 0.6 else (120, 112, 100)
    dr.polygon(q, fill=roof + (255,), outline=(60, 40, 30, 255))
    dr.line([((q[0][0] + q[3][0]) / 2, (q[0][1] + q[3][1]) / 2), ((q[1][0] + q[2][0]) / 2, (q[1][1] + q[2][1]) / 2)],
            fill=tuple(min(255, int(v * 1.25)) for v in roof) + (255,), width=1)
log("villages")

img.save(os.path.join(HERE, "map_full.png"))
img.resize((MW // 4, MH // 4), Image.LANCZOS).save(os.path.join(HERE, "map_prev.jpg"), quality=90)
json.dump({"villages": {k: v[0] for k, v in VILLAGES.items()}, "roads": ROADS, "ridge1": RIDGE1, "ridge2": RIDGE2},
          open(os.path.join(HERE, "geo.json"), "w"))
log("done")
