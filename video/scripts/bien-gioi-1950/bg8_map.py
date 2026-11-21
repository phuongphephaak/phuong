"""Bản đồ 8K vùng Đông Khê – Cốc Xá từ dữ liệu độ cao thật (Terrarium/SRTM), 8192x5120, 1 px ≈ 1,38 m."""
import math, os, time, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
from scipy.spatial import cKDTree
from skimage.graph import route_through_array

HERE = os.path.abspath(os.environ.get("WORK", os.getcwd()))
MW, MH = 8192, 5120
CROP = (700, 350, 1981, 1150)          # x0, y0, x1, y1 trên lưới DEM (8,83 m/px)
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
Dc = D[y0:y1, x0:x1].astype(np.float32)
Dc = ndimage.gaussian_filter(Dc, 0.7)
SC = MW / Dc.shape[1]                       # hệ số phóng
MPP = 8.83 / SC                             # mét / px bản đồ
E = np.array(Image.fromarray(Dc).resize((MW, MH), Image.BICUBIC), np.float32)
E += 2.5 * fbm((MH, MW), 4, 2, base=90) + 0.8 * fbm((MH, MW), 3, 3, base=400)
log("dem", Dc.shape, "m/px", round(MPP, 3))

# ---------------- địa hình: độ dốc, độ cao tương đối, đổ bóng ----------------
gy, gx = np.gradient(E, MPP)
slope = np.degrees(np.arctan(np.hypot(gx, gy)))
rel = E - ndimage.gaussian_filter(E, 120)
ex = 1.7
nx, ny, nz = -gx * ex, -gy * ex, np.ones_like(gx)
nl = np.sqrt(nx * nx + ny * ny + nz * nz); nx /= nl; ny /= nl; nz /= nl
del gx, gy, nl
def lambert(az, alt):
    a, b = math.radians(az), math.radians(alt)
    L = (math.sin(a) * math.cos(b), -math.cos(a) * math.cos(b), math.sin(b))
    return np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
sun = lambert(315, 38); sky = 0.5 + 0.5 * nz
cav = np.clip((E - ndimage.gaussian_filter(E, 25)) / 6, -1, 1)          # lõm tối, gờ sáng
log("terrain")

# ---------------- phân loại: ruộng thung lũng / rừng / vách đá ----------------
nv = fbm((MH, MW), 4, 11, base=30)
valley = sstep(13, 6, slope + 3 * nv) * sstep(22, 4, rel + 5 * nv)
valley = ndimage.gaussian_filter(valley, 3)
rock = sstep(42, 55, slope + 8 * fbm((MH, MW), 4, 12, base=120))
forest = np.clip(1 - valley - rock * 0.8, 0, 1)
log("classes")

# ---------------- ruộng bậc thang: ô ruộng + bờ theo đường đồng mức ----------------
pts = np.array([(x + rng.uniform(-22, 22), y + rng.uniform(-14, 14)) for y in np.arange(-40, MH + 40, 30) for x in np.arange(-40, MW + 40, 52)], np.float32)
kd = cKDTree(pts); NP = len(pts)
fid = np.empty((MH, MW), np.int32); fe = np.empty((MH, MW), np.float32)
for r0 in range(0, MH, 256):
    q = np.c_[np.tile(np.arange(MW, dtype=np.float32), min(256, MH - r0)) + 5 * nv[r0:r0 + 256].ravel(),
              np.repeat(np.arange(r0, min(MH, r0 + 256), dtype=np.float32), MW)]
    dd, ii = kd.query(q, k=2); ab = np.hypot(*(pts[ii[:, 0]] - pts[ii[:, 1]]).T)
    fid[r0:r0 + 256] = ii[:, 0].reshape(-1, MW); fe[r0:r0 + 256] = ((dd[:, 1] ** 2 - dd[:, 0] ** 2) / (2 * ab)).reshape(-1, MW)
PAL = np.array([[0.66, 0.62, 0.38], [0.62, 0.60, 0.36], [0.56, 0.58, 0.34], [0.60, 0.55, 0.38], [0.70, 0.65, 0.42], [0.52, 0.56, 0.34]], np.float32)
ft = PAL[rng.choice(len(PAL), NP, p=[0.28, 0.22, 0.16, 0.12, 0.12, 0.10])] * rng.uniform(0.94, 1.06, (NP, 1)).astype(np.float32)
fa = rng.uniform(0, np.pi, NP).astype(np.float32)
paddy = ft[fid]
yy = np.arange(MH, dtype=np.float32)[:, None]; xx = np.arange(MW, dtype=np.float32)[None, :]
a = fa[fid]; paddy *= (1 + 0.07 * np.sin(2 * np.pi * (xx * np.cos(a) + yy * np.sin(a)) / 4.0))[..., None]
del a
bund = np.clip(1.3 - fe, 0, 1) * 0.5
terr = np.abs(((E / 2.2) % 1.0) - 0.5) < 0.06                       # bờ bậc thang theo đồng mức
bund = np.maximum(bund, terr * sstep(1, 4, slope) * 0.8)
paddy = paddy * (1 - 0.22 * bund[..., None]) + np.array([0.42, 0.44, 0.24], np.float32) * 0.22 * bund[..., None]
del fid, fe, terr
log("paddies")

# ---------------- tán rừng: từng tán cây (Worley) ----------------
tp = []
step = 7.5
gyy, gxx = np.mgrid[0:MH:step, 0:MW:step]
tp = np.c_[gxx.ravel() + rng.uniform(-3, 3, gxx.size), gyy.ravel() + rng.uniform(-3, 3, gxx.size)].astype(np.float32)
keep = forest[np.clip(tp[:, 1].astype(int), 0, MH - 1), np.clip(tp[:, 0].astype(int), 0, MW - 1)] > 0.15
tp = tp[keep]; TR = rng.uniform(4.5, 7.5, len(tp)).astype(np.float32); TT = rng.uniform(0.75, 1.2, len(tp)).astype(np.float32)
tk = cKDTree(tp)
canopy = np.zeros((MH, MW), np.float32); ctint = np.ones((MH, MW), np.float32)
cnx = np.zeros((MH, MW), np.float32); cny = np.zeros((MH, MW), np.float32)
for r0 in range(0, MH, 128):
    rows = min(128, MH - r0)
    q = np.c_[np.tile(np.arange(MW, dtype=np.float32), rows), np.repeat(np.arange(r0, r0 + rows, dtype=np.float32), MW)]
    dd, ii = tk.query(q, k=1, distance_upper_bound=9)
    ok = np.isfinite(dd); ii2 = np.where(ok, ii, 0)
    rr = TR[ii2]; h = np.where(ok, np.clip(1 - (dd / rr) ** 2, 0, 1), 0)
    dx = np.where(ok, q[:, 0] - tp[ii2, 0], 0) / rr; dy = np.where(ok, q[:, 1] - tp[ii2, 1], 0) / rr
    canopy[r0:r0 + rows] = h.reshape(rows, MW); ctint[r0:r0 + rows] = np.where(ok, TT[ii2], 1).reshape(rows, MW)
    cnx[r0:r0 + rows] = (dx * (h > 0)).reshape(rows, MW); cny[r0:r0 + rows] = (dy * (h > 0)).reshape(rows, MW)
log("canopy", len(tp))
# đổ bóng tán: pháp tuyến vòm + hướng nắng; khe giữa tán tối
cl = np.clip(0.55 - 0.35 * (cnx * -0.62 + cny * -0.62) + 0.15 * canopy, 0, 1.2)
gap = 1 - canopy
fcol = np.stack([0.24 + 0.06 * cl, 0.28 + 0.07 * cl, 0.14 + 0.04 * cl], -1) * (0.9 + 0.1 * ctint[..., None])
fcol *= (1 - 0.35 * gap ** 2)[..., None]
del cnx, cny, ctint, cl

# ---------------- vách đá vôi ----------------
rn = fbm((MH, MW), 5, 21, base=150)
rcol = np.stack([0.52 + 0.05 * rn, 0.51 + 0.05 * rn, 0.46 + 0.04 * rn], -1)
streak = np.sin((xx * 0.9 + yy * 0.25 + 18 * fbm((MH, MW), 3, 22, base=60)) * 0.6) * 0.06
rcol *= (1 + streak)[..., None]

# ---------------- ghép + chiếu sáng ----------------
C = paddy * valley[..., None] + fcol * forest[..., None] + rcol * (rock * (1 - valley))[..., None]
wsum = valley + forest + rock * (1 - valley); C /= np.maximum(wsum, 1e-3)[..., None]
del paddy, fcol, rcol
light = 0.40 * sky + 0.95 * sun ** 1.1
light *= (1 + 0.35 * cav)
C *= light[..., None]
C *= (1 + 0.05 * fbm((MH, MW), 5, 31, base=8))[..., None]
lum = C.mean(-1); p5, p95 = np.percentile(lum[::9, ::9], [5, 95])
nl_ = 0.24 + (lum - p5) / (p95 - p5) * (0.72 - 0.24); nl_ = np.where(nl_ > 0.64, 0.64 + (nl_ - 0.64) * 0.55, nl_)
C *= (nl_ / np.maximum(lum, 1e-3))[..., None]
g_ = C.mean(-1, keepdims=True); C = g_ + (C - g_) * 0.72
del lum, nl_, g_, light
log("composite")
img = Image.fromarray((np.clip(C, 0, 1) * 255).astype(np.uint8)); del C

# ---------------- đường: theo thung lũng thật (đường đi ít dốc nhất) ----------------
cs = 8
cost = (1 + (slope[::cs, ::cs] / 4) ** 2 + 30 * rock[::cs, ::cs]).astype(np.float64)
def route(pts_):
    out = []
    for (ax, ay), (bx, by) in zip(pts_[:-1], pts_[1:]):
        p, _ = route_through_array(cost, (int(ay / cs), int(ax / cs)), (int(by / cs), int(bx / cs)), fully_connected=True, geometric=True)
        out += [(c * cs + cs / 2, r * cs + cs / 2) for r, c in p]
    o = np.array(out, float); o = ndimage.uniform_filter1d(o, 9, axis=0, mode="nearest")
    return [tuple(v) for v in o[::3]]
DK = ((1550.0 - x0) * SC, (567.0 - y0) * SC)             # Đông Khê (toạ độ thật)
G = json.load(open(os.path.join(HERE, "geo_in.json")))
roads = {k: route(v) for k, v in G["routes"].items()}
dr = ImageDraw.Draw(img, "RGBA")
for k, p in roads.items():
    if k == "rc4":
        dr.line(p, fill=(70, 55, 35, 200), width=11, joint="curve"); dr.line(p, fill=(190, 165, 115, 230), width=5, joint="curve")
    else:
        dr.line(p, fill=(95, 76, 48, 190), width=5, joint="curve"); dr.line(p, fill=(170, 145, 100, 140), width=2, joint="curve")
log("roads")
# ---------------- làng ----------------
for nm, (vx, vy, n, r) in G["villages"].items():
    for i in range(n):
        for _ in range(20):
            a_ = rng.uniform(0, 6.28); d_ = r * math.sqrt(rng.random()); hx, hy = vx + d_ * math.cos(a_), vy + d_ * math.sin(a_) * 0.8
            if 0 <= hx < MW and 0 <= hy < MH and slope[int(hy), int(hx)] < 12: break
        w, h = rng.uniform(10, 16), rng.uniform(7, 10); ang = rng.uniform(0, 3.14); c, s_ = math.cos(ang), math.sin(ang)
        q = [(hx + c * u - s_ * v, hy + s_ * u + c * v) for u, v in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
        dr.polygon([(x + 4, y + 4) for x, y in q], fill=(25, 22, 12, 120))
        dr.polygon(q, fill=((142, 112, 72) if rng.random() < 0.7 else (118, 110, 98)) + (255,), outline=(55, 40, 28, 255))
        dr.line([((q[0][0] + q[3][0]) / 2, (q[0][1] + q[3][1]) / 2), ((q[1][0] + q[2][0]) / 2, (q[1][1] + q[2][1]) / 2)], fill=(175, 145, 100, 255), width=1)
log("villages")
img.save(os.path.join(HERE, "map_full.png"))
img.resize((MW // 4, MH // 4), Image.LANCZOS).save(os.path.join(HERE, "map_prev.jpg"), quality=92)
json.dump({"routes": {k: v for k, v in roads.items()}, "DK": DK, "mpp": MPP, "villages": {k: v[:2] for k, v in G["villages"].items()},
           "B": G["B"], "P477": G["P477"]}, open(os.path.join(HERE, "geo.json"), "w"), ensure_ascii=False)
np.save(os.path.join(HERE, "elev_small.npy"), E[::8, ::8])
log("done")
