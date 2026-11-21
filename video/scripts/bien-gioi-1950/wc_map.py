"""Bản đồ địa hình Waterloo kiểu sa bàn chiến thuật (1 px = 1 m).  python3 wl_map.py"""
import math, os, sys, time, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.spatial import cKDTree
from scipy import ndimage

HERE = os.path.abspath(os.environ.get("WORK", os.getcwd()))
MW, MH = 8192, 5120
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
    """khoảng cách tới polyline (nhanh: vẽ đường rồi biến đổi khoảng cách)"""
    m = Image.new("1", (xx.shape[1], xx.shape[0]), 1); ImageDraw.Draw(m).line([tuple(p) for p in pts], fill=0, width=1)
    return ndimage.distance_transform_edt(np.asarray(m)).astype(np.float32)


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
# ---- địa lý Biên giới 1950 (cùng hệ toạ độ với geo.json của phần dựng chuyển động)
from skimage.graph import route_through_array
GEO = json.load(open(os.path.join(HERE, "geo.json"))); GIN = json.load(open(os.path.join(HERE, "geo_in.json")))
_D = np.load(os.path.join(HERE, "dem.npy"))[350:1150, 700:1981].astype(np.float32)
_Ds = ndimage.gaussian_filter(_D, 4.5)
_cs = 8
_E8 = np.asarray(Image.fromarray(_Ds).resize((MW // _cs, MH // _cs), Image.BILINEAR), np.float64)


def _route(pts_, cost):
    out = []
    for (ax, ay), (bx, by) in zip(pts_[:-1], pts_[1:]):
        p, _ = route_through_array(cost, (int(ay / _cs), int(ax / _cs)), (int(by / _cs), int(bx / _cs)), fully_connected=True, geometric=True)
        out += [(c * _cs + _cs / 2, r * _cs + _cs / 2) for r, c in p]
    o = np.array(out, float); o = ndimage.uniform_filter1d(o, 31, axis=0, mode="nearest")
    return [tuple(v) for v in o[::6]]


_gy, _gx = np.gradient(_E8, 8 * 1.38); _sl = np.hypot(_gx, _gy)
ROADS = {k: _route(v, 1 + (_sl * 12) ** 2) for k, v in GIN["routes"].items()}
_B = GIN["B"]; _DK = GIN["villages"]["Đông Khê"][:2]
_sc = 1 + ((_E8 - _E8.min()) / 10) ** 2
STREAMS = [_route([(_B[0] - 1400, _B[1] + 900), _B, (_B[0] + 1500, _B[1] + 1300), (_B[0] + 2600, MH - 10)], _sc),
           _route([(_DK[0] - 200, 10), _DK, (_DK[0] + 300, MH - 10)], _sc)]
VILLAGES = {k: ((v[0], v[1]), v[2], v[3]) for k, v in GIN["villages"].items()}

ys, xs = np.mgrid[0:MH, 0:MW].astype(np.float32)
log("grid")
Z = (np.asarray(Image.fromarray(_Ds).resize((MW, MH), Image.BICUBIC), np.float32) - _Ds.min()) * 0.085
Z += 1.2 * fbm((MH, MW), 4, 2, base=60)
sd = np.full(xs.shape, 1e9, np.float32)
for s in STREAMS:
    sd = np.minimum(sd, poly_dist(xs, ys, s))
Z -= 32 * np.exp(-(sd / 260) ** 2) + 12 * np.exp(-(sd / 700) ** 2)
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
for (px, py, rr) in []:
    dr.ellipse((px - rr, py - rr * 0.6, px + rr, py + rr * 0.6), fill=(70, 120, 150, 255), outline=(60, 75, 40, 160), width=3)
log("streams")

# ---------------- đường ----------------
for k, (nm, p) in enumerate(ROADS.items()):
    main = nm == "rc4"
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
_gyZ, _gxZ = np.gradient(ndimage.gaussian_filter(Z, 6)); steep = np.hypot(_gxZ, _gyZ); del _gyZ, _gxZ
wgt = 0.42 * np.clip((steep - 0.04) / 0.08, 0, 1) - 0.12
nf2 = nf + 0.25 * fbm((MH, MW), 4, 62, base=50)
forest |= (nf2 + wgt) > 0.70
forest &= (sd > 40)
rd = np.full(xs.shape, 1e9, np.float32)
for nm in ("rc4",):
    rd = np.minimum(rd, poly_dist(xs, ys, ROADS[nm]))
forest &= rd > 30
for (vx, vy), n, r in VILLAGES.values():
    forest &= np.hypot(xs - vx, ys - vy) > r * 2.2
del rd, nf, nf2, wgt, sd, steep
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
for k_, nm_ in enumerate(("rc4", "lepage", "charton")):
    pp = wobble(ROADS[nm_], 25, 30, 300 + list(ROADS).index(nm_))
    for (ax, ay), (bx, by) in zip(pp[:-1], pp[1:]):
        L_ = math.hypot(bx - ax, by - ay); n_ = int(L_ / 4.5)
        if n_ == 0: continue
        nx_, ny_ = -(by - ay) / L_, (bx - ax) / L_
        for side in (-1, 1):
            if rng.random() < (0.55 if side < 0 else 0.8): continue
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
log("done")
