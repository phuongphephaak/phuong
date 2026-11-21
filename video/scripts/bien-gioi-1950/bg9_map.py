"""Bản đồ 8K kiểu sa bàn chiến thuật (Waterloo) trên địa hình thật vùng Đông Khê – Cốc Xá.
Đồng ruộng vàng ô liu có vân luống, viền hàng cây bụi lấm tấm, đổ nắng mềm, khoảnh rừng sẫm, suối xanh, đường đất."""
import math, os, time, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
from scipy.spatial import cKDTree
from skimage.graph import route_through_array

HERE = os.path.abspath(os.environ.get("WORK", os.getcwd()))
MW, MH = 8192, 5120
CROP = (700, 350, 1981, 1150)
t0 = time.time(); rng = np.random.default_rng(23)


def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)


def fbm(shape, octaves, seed, base=4, persist=0.55):
    r = np.random.default_rng(seed); out = np.zeros(shape, np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        f = base * 2 ** o
        gh, gw = int(f * shape[0] / max(shape)) + 3, int(f * shape[1] / max(shape)) + 3
        g = r.standard_normal((gh, gw)).astype(np.float32)
        out += amp * np.asarray(Image.fromarray(g).resize((shape[1], shape[0]), Image.BICUBIC)); tot += amp; amp *= persist
    return out / tot


def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)


D = np.load(os.path.join(HERE, "dem.npy"))
x0, y0, x1, y1 = CROP
Dc = ndimage.gaussian_filter(D[y0:y1, x0:x1].astype(np.float32), 1.6)       # làm mềm: sa bàn, không phải ảnh vệ tinh
SC = MW / Dc.shape[1]; MPP = 8.83 / SC
E = np.array(Image.fromarray(Dc).resize((MW, MH), Image.BICUBIC), np.float32)
log("dem")
gy, gx = np.gradient(E, MPP)
slope = np.degrees(np.arctan(np.hypot(gx, gy)))
ex = 0.9                                                   # đổ bóng mềm
nx, ny, nz = -gx * ex, -gy * ex, np.ones_like(gx)
nl = np.sqrt(nx * nx + ny * ny + nz * nz); nx /= nl; ny /= nl; nz /= nl
del gx, gy, nl
az, alt = math.radians(300), math.radians(42)
L = (math.sin(az) * math.cos(alt), -math.cos(az) * math.cos(alt), math.sin(alt))
sun = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1); sun /= np.percentile(sun[::9, ::9], 60)
del nx, ny, nz
yy = np.arange(MH, dtype=np.float32)[:, None]; xx = np.arange(MW, dtype=np.float32)[None, :]
log("shade")

# ---------------- ô ruộng: Voronoi cong, mỗi ô một hướng luống ----------------
pts = np.array([(x + rng.uniform(-70, 70), y + rng.uniform(-60, 60)) for y in np.arange(-150, MH + 150, 120) for x in np.arange(-150, MW + 150, 150)], np.float32)
kd = cKDTree(pts); NP = len(pts)
wx_ = 25 * fbm((MH, MW), 4, 41, base=40); wy_ = 25 * fbm((MH, MW), 4, 42, base=40)
fid = np.empty((MH, MW), np.int32); fe = np.empty((MH, MW), np.float32)
for r0 in range(0, MH, 256):
    rows = min(256, MH - r0)
    q = np.c_[(np.tile(np.arange(MW, dtype=np.float32), rows) + wx_[r0:r0 + rows].ravel()),
              (np.repeat(np.arange(r0, r0 + rows, dtype=np.float32), MW) + wy_[r0:r0 + rows].ravel())]
    dd, ii = kd.query(q, k=2); ab = np.hypot(*(pts[ii[:, 0]] - pts[ii[:, 1]]).T)
    fid[r0:r0 + rows] = ii[:, 0].reshape(rows, MW); fe[r0:r0 + rows] = ((dd[:, 1] ** 2 - dd[:, 0] ** 2) / (2 * ab)).reshape(rows, MW)
del wx_, wy_
log("fields")
PAL = np.array([[0.60, 0.58, 0.30], [0.64, 0.60, 0.32], [0.56, 0.56, 0.28], [0.66, 0.62, 0.36], [0.58, 0.57, 0.33], [0.62, 0.57, 0.30]], np.float32)
ft = PAL[rng.integers(0, len(PAL), NP)] * 0.5 + np.array([0.61, 0.59, 0.32], np.float32) * 0.5
ft = ft * rng.uniform(0.96, 1.04, (NP, 1)).astype(np.float32)
fang = rng.uniform(0, np.pi, NP).astype(np.float32)
fstr = rng.choice([0.0, 0.10, 0.14, 0.18, 0.18, 0.22], NP).astype(np.float32)     # độ đậm vân luống
fper = rng.uniform(5.0, 7.0, NP).astype(np.float32)
C = ft[fid]
a = fang[fid]
phase = 2 * np.pi * (xx * np.cos(a) + yy * np.sin(a)) / fper[fid]
rows_ = 0.5 + 0.5 * np.sin(phase)
rows_ = sstep(0.35, 0.85, rows_)                                 # luống sắc nét
var = 0.6 + 0.4 * fbm((MH, MW), 3, 43, base=60)
C *= (1 - fstr[fid] * rows_ * var)[..., None]
del a, phase, rows_, var
C *= (1 + 0.06 * fbm((MH, MW), 5, 44, base=10) + 0.03 * fbm((MH, MW), 3, 45, base=300))[..., None]
log("rows")

# ---------------- hàng cây bụi lấm tấm dọc bờ ruộng ----------------
keep_edge = np.zeros(NP * 7 + 7, bool)
hedge = (fe < 3.2).astype(np.float32)
pair_keep = (fbm((MH, MW), 3, 46, base=70) > -0.15)
hedge *= pair_keep
dots = np.random.default_rng(47).random((MH // 2 + 1, MW // 2 + 1)).astype(np.float32)
dots = np.asarray(Image.fromarray(dots).resize((MW, MH), Image.NEAREST))[:MH, :MW]
dots = ndimage.gaussian_filter((dots > 0.45).astype(np.float32), 0.9)
hedge_d = hedge * sstep(0.25, 0.6, dots)
C = C * (1 - 0.55 * hedge_d[..., None]) + np.array([0.22, 0.24, 0.11], np.float32) * 0.55 * hedge_d[..., None]
# bóng nhẹ phía dưới-phải hàng cây
hs = ndimage.shift(hedge_d, (2, 2), order=0)
C *= (1 - 0.18 * hs * (1 - hedge_d))[..., None]
del hedge, dots, hs, pair_keep
log("hedges")

# ---------------- khoảnh rừng sẫm (sườn dốc, khe núi) ----------------
nf = fbm((MH, MW), 5, 51, base=14)
fm = sstep(0.55, 0.75, (slope / 40) * 0.8 + 0.55 * nf)
fm = ndimage.gaussian_filter(fm, 2)
fm = (fm > 0.5).astype(np.float32)
fm = ndimage.binary_opening(fm, iterations=2).astype(np.float32)
fm = ndimage.gaussian_filter(fm, 1.2)
tp = np.c_[rng.uniform(0, MW, 1_400_000), rng.uniform(0, MH, 1_400_000)].astype(np.float32)
tp = tp[fm[tp[:, 1].astype(int), tp[:, 0].astype(int)] > 0.5]
tk = cKDTree(tp); TR = rng.uniform(3.0, 5.0, len(tp)).astype(np.float32)
canopy = np.zeros((MH, MW), np.float32); lit = np.zeros((MH, MW), np.float32)
for r0 in range(0, MH, 128):
    rows = min(128, MH - r0)
    q = np.c_[np.tile(np.arange(MW, dtype=np.float32), rows), np.repeat(np.arange(r0, r0 + rows, dtype=np.float32), MW)]
    dd, ii = tk.query(q, k=1, distance_upper_bound=6)
    ok = np.isfinite(dd); ii2 = np.where(ok, ii, 0); rr = TR[ii2]
    h = np.where(ok, np.clip(1 - (dd / rr) ** 2, 0, 1), 0)
    l = np.where(ok, -((q[:, 0] - tp[ii2, 0]) + (q[:, 1] - tp[ii2, 1])) / rr, 0)
    canopy[r0:r0 + rows] = h.reshape(rows, MW); lit[r0:r0 + rows] = l.reshape(rows, MW)
fcol = np.stack([0.20 + 0.06 * lit, 0.23 + 0.07 * lit, 0.10 + 0.03 * lit], -1)
fcol *= (0.55 + 0.45 * canopy)[..., None]
fmask = fm * np.clip(canopy * 1.6 + 0.35, 0, 1)
C = C * (1 - fmask[..., None]) + fcol * fmask[..., None]
# bóng rừng đổ lên ruộng
fsh = ndimage.shift(ndimage.gaussian_filter(fm, 3), (5, 5), order=1)
C *= (1 - 0.30 * fsh * (1 - fm))[..., None]
del canopy, lit, fcol, fsh, tp
log("forest", len(TR))

# ---------------- chiếu sáng: đổ nắng mềm, đỉnh sáng vàng ----------------
light = 0.55 + 0.55 * sun
warm = np.clip(sun - 1, 0, 0.6)
C *= light[..., None]
C += np.array([0.10, 0.08, -0.02], np.float32) * warm[..., None]
lum = C.mean(-1); p5, p50, p95 = np.percentile(lum[::9, ::9], [5, 50, 95])
tgt = np.interp(lum, [lum.min(), p5, p50, p95, lum.max()], [0.10, 0.23, 0.45, 0.63, 0.75])
C *= (tgt / np.maximum(lum, 1e-3))[..., None]
del lum, tgt, light, warm, sun
log("tone")
img = Image.fromarray((np.clip(C, 0, 1) * 255).astype(np.uint8)); del C

# ---------------- suối theo đáy thung lũng thật ----------------
cs = 8
Es = E[::cs, ::cs].astype(np.float64)
G = json.load(open(os.path.join(HERE, "geo_in.json")))
def route(pts_, cost, meander=False):
    out = []
    for (ax, ay), (bx, by) in zip(pts_[:-1], pts_[1:]):
        p, _ = route_through_array(cost, (int(ay / cs), int(ax / cs)), (int(by / cs), int(bx / cs)), fully_connected=True, geometric=True)
        out += [(c * cs + cs / 2, r * cs + cs / 2) for r, c in p]
    o = np.array(out, float); o = ndimage.uniform_filter1d(o, 15, axis=0, mode="nearest")
    if meander:
        d = np.gradient(o, axis=0); d /= np.maximum(np.hypot(d[:, 0], d[:, 1]), 1e-6)[:, None]
        s_ = np.cumsum(np.hypot(*np.diff(o, axis=0, prepend=o[:1]).T))
        w = 22 * np.sin(s_ / 55) + 10 * np.sin(s_ / 23 + 1.3) + 4 * np.sin(s_ / 9)
        o = o + np.c_[-d[:, 1], d[:, 0]] * w[:, None]
    return [tuple(v) for v in o[::2]]
scost = 1 + ((Es - Es.min()) / 12) ** 2
B = G["B"]; DK = G["villages"]["Đông Khê"][:2]
streams = [route([(B[0] - 1400, B[1] + 900), B, (B[0] + 1500, B[1] + 1300), (B[0] + 2600, MH - 10)], scost, True),
           route([(DK[0] - 200, 10), DK, (DK[0] + 300, MH - 10)], scost, True)]
dr = ImageDraw.Draw(img, "RGBA")
for p in streams:
    dr.line(p, fill=(52, 58, 30, 170), width=13, joint="curve")
    dr.line(p, fill=(64, 112, 132, 255), width=7, joint="curve")
    dr.line(p, fill=(150, 190, 200, 170), width=2, joint="curve")
log("streams")
rcost = (1 + (slope[::cs, ::cs] / 5) ** 2).astype(np.float64)
roads = {k: route(v, rcost) for k, v in G["routes"].items()}
for k, p in roads.items():
    w = 8 if k == "rc4" else 5
    dr.line(p, fill=(78, 62, 38, 200), width=w, joint="curve")
    dr.line(p, fill=(150, 126, 82, 150), width=max(2, w - 5), joint="curve")
# lối mòn phụ giữa ruộng
for i in range(70):
    a0 = pts[rng.integers(0, NP)]; p = [tuple(a0)]
    ang = rng.uniform(0, 6.28)
    for k in range(rng.integers(6, 14)):
        ang += rng.uniform(-0.35, 0.35); p.append((p[-1][0] + 60 * math.cos(ang), p[-1][1] + 60 * math.sin(ang)))
    dr.line(p, fill=(92, 78, 48, 110), width=2, joint="curve")
log("roads")
for nm, (vx, vy, n, r) in G["villages"].items():
    for i in range(n):
        a_ = rng.uniform(0, 6.28); d_ = r * math.sqrt(rng.random()); hx, hy = vx + d_ * math.cos(a_), vy + d_ * math.sin(a_) * 0.8
        w, h = rng.uniform(11, 17), rng.uniform(7, 10); ang = rng.uniform(0, 3.14); c, s_ = math.cos(ang), math.sin(ang)
        q = [(hx + c * u - s_ * v, hy + s_ * u + c * v) for u, v in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
        dr.polygon([(x + 4, y + 4) for x, y in q], fill=(25, 22, 12, 130))
        dr.polygon(q, fill=((118, 72, 48) if rng.random() < 0.65 else (112, 104, 92)) + (255,), outline=(50, 34, 24, 255))
        dr.line([((q[0][0] + q[3][0]) / 2, (q[0][1] + q[3][1]) / 2), ((q[1][0] + q[2][0]) / 2, (q[1][1] + q[2][1]) / 2)], fill=(160, 112, 80, 255), width=1)
log("villages")
img.save(os.path.join(HERE, "map_full.png"))
img.resize((MW // 4, MH // 4), Image.LANCZOS).save(os.path.join(HERE, "map_prev.jpg"), quality=92)
geo = json.load(open(os.path.join(HERE, "geo.json")))
geo["routes"] = roads
json.dump(geo, open(os.path.join(HERE, "geo.json"), "w"), ensure_ascii=False)
log("done")
