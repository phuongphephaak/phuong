"""Bản đồ vùng Cốc Xá – Đông Khê (sơ đồ minh hoạ, 1 px = 1 m): núi đá vôi, rừng, lòng chảo ruộng lúa."""
import math, os, time, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.spatial import cKDTree
from scipy import ndimage

HERE = os.path.abspath(os.environ.get("WORK", os.getcwd()))
MW, MH = 6144, 4096
t0 = time.time(); rng = np.random.default_rng(19)


def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)


def fbm(shape, octaves, seed, base=4, persist=0.55):
    r = np.random.default_rng(seed); out = np.zeros(shape, np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        f = base * 2 ** o
        gh, gw = int(f * shape[0] / max(shape)) + 3, int(f * shape[1] / max(shape)) + 3
        g = r.standard_normal((gh, gw)).astype(np.float32)
        out += amp * np.asarray(Image.fromarray(g).resize((shape[1], shape[0]), Image.BICUBIC)); tot += amp; amp *= persist
    return out / tot


def poly_dist(xx, yy, pts):
    d = np.full(xx.shape, 1e9, np.float32)
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        vx, vy = bx - ax, by - ay; L2 = vx * vx + vy * vy
        t = np.clip(((xx - ax) * vx + (yy - ay) * vy) / L2, 0, 1)
        d = np.minimum(d, np.hypot(xx - ax - t * vx, yy - ay - t * vy))
    return d


def wobble(pts, amp, step, seed):
    r = np.random.default_rng(seed); out = []
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        L = math.hypot(bx - ax, by - ay); n = max(2, int(L / step)); nx, ny = -(by - ay) / L, (bx - ax) / L
        for i in range(n):
            u = i / n; w = amp * (math.sin(u * math.pi * 2.3 + seed) * 0.6 + r.uniform(-0.5, 0.5)) * math.sin(u * math.pi)
            out.append((ax + (bx - ax) * u + nx * w, ay + (by - ay) * u + ny * w))
    out.append(pts[-1]); return out


def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)


# ---------------- địa lý (sơ đồ minh hoạ, không theo tỉ lệ chính xác) ----------------
ROADS = {"rc4": [(6144, 250), (5600, 800), (5050, 1300), (4800, 1700), (4700, 2300), (4950, 3000), (5300, 3600), (5500, 4096)]}
TRACKS = {"lepage": [(4700, 2300), (4150, 2470), (3550, 2560), (2950, 2470), (2430, 2390)],
          "charton": [(2950, 0), (2780, 480), (2560, 900), (2420, 1250), (2280, 1650), (2080, 2060)],
          "coctontrack": [(2300, 2650), (2800, 2900), (3300, 2950), (3700, 3120), (4300, 3300), (4950, 3000)]}
STREAMS = [[(1400, 2200), (1900, 2420), (2500, 2700), (3100, 3150), (3600, 3700), (3900, 4096)],
           [(4300, 1000), (4650, 1550), (4600, 2200), (4800, 2900), (5100, 3500), (5250, 4096)]]
BASINS = [(1900, 2350, 560, 360), (4780, 1720, 620, 430), (3250, 2930, 260, 150), (3700, 3150, 220, 140)]
VILLAGES = {"Cốc Xá": ((1950, 2380), 14, 110), "Đông Khê": ((4800, 1700), 45, 170), "Cốc Tồn": ((3260, 2930), 8, 60),
            "Khau Pia": ((3700, 3150), 7, 55), "Quang Liệt": ((2860, 300), 10, 70), "Nà Pá": ((5150, 1150), 8, 60)}
POINT477 = (2360, 1330)

ys, xs = np.mgrid[0:MH, 0:MW].astype(np.float32)
log("grid")
# ---- thung lũng (không có núi)
V = np.zeros((MH, MW), np.float32)
nv = fbm((MH, MW), 4, 3, base=24)
for (cx, cy, rx, ry) in BASINS:
    V = np.maximum(V, sstep(1.15, 0.85, np.hypot((xs - cx) / rx, (ys - cy) / ry) + 0.12 * nv))
dr = poly_dist(xs, ys, ROADS["rc4"]); V = np.maximum(V, sstep(260, 140, dr + 40 * nv))
for k, tpts in TRACKS.items():
    V = np.maximum(V, 0.85 * sstep(110, 45, poly_dist(xs, ys, tpts) + 20 * nv))
sd = np.full(xs.shape, 1e9, np.float32)
for s in STREAMS: sd = np.minimum(sd, poly_dist(xs, ys, s))
V = np.maximum(V, sstep(170, 70, sd + 30 * nv))
log("valleys")
# ---- núi đá vôi: chóp nhọn dày đặc
Z = 28 * fbm((MH, MW), 4, 1, base=3, persist=0.5)
towers = []
for gy in np.arange(-100, MH + 100, 150):
    for gx in np.arange(-100, MW + 100, 150):
        towers.append((gx + rng.uniform(-70, 70), gy + rng.uniform(-70, 70), rng.uniform(60, 150), rng.uniform(55, 150)))
towers.append((POINT477[0], POINT477[1], 210, 230))
T = np.zeros((MH, MW), np.float32)
for (tx, ty, r, h) in towers:
    x0, x1 = int(max(0, tx - 2.6 * r)), int(min(MW, tx + 2.6 * r)); y0, y1 = int(max(0, ty - 2.6 * r)), int(min(MH, ty + 2.6 * r))
    if x1 <= x0 or y1 <= y0: continue
    d = np.hypot(xs[y0:y1, x0:x1] - tx, (ys[y0:y1, x0:x1] - ty) * 1.1) / (r * 1.5)
    T[y0:y1, x0:x1] = np.maximum(T[y0:y1, x0:x1], h * np.clip(1 - d, 0, 1) ** 1.6)
T *= (1 + 0.12 * fbm((MH, MW), 3, 5, base=80))
Z += T * (1 - V)
Z -= 10 * V
del T
log("towers")
Z = ndimage.gaussian_filter(Z, 3.0)
gy_, gx_ = np.gradient(Z)
slope = np.hypot(gx_, gy_)
ex = 1.6
nx, ny, nz = -gx_ * ex, -gy_ * ex, np.ones_like(gx_)
nl = np.sqrt(nx * nx + ny * ny + nz * nz)
L = np.array([-0.55, -0.62, 0.56]); L /= np.linalg.norm(L)
shade = np.clip((nx * L[0] + ny * L[1] + nz * L[2]) / nl, 0, 1); shade /= shade.mean()
del gx_, gy_, nx, ny, nz, nl
log("shade")

# ---- ruộng lúa trong thung lũng (ô nhỏ, vân luống)
pts = np.array([(x + rng.uniform(-30, 30), y + rng.uniform(-20, 20)) for y in np.arange(-50, MH + 50, 45) for x in np.arange(-50, MW + 50, 75)], np.float32)
kd = cKDTree(pts); fid = np.empty((MH, MW), np.int32); fe = np.empty((MH, MW), np.float32)
for r0 in range(0, MH, 256):
    q = np.c_[xs[r0:r0 + 256].ravel() + 6 * nv[r0:r0 + 256].ravel(), ys[r0:r0 + 256].ravel()]
    dd, ii = kd.query(q, k=2); ab = np.hypot(*(pts[ii[:, 0]] - pts[ii[:, 1]]).T)
    fid[r0:r0 + 256] = ii[:, 0].reshape(-1, MW); fe[r0:r0 + 256] = ((dd[:, 1] ** 2 - dd[:, 0] ** 2) / (2 * ab)).reshape(-1, MW)
NP = len(pts)
PAL = np.array([[0.62, 0.62, 0.38], [0.60, 0.62, 0.36], [0.64, 0.62, 0.38], [0.58, 0.60, 0.35], [0.63, 0.63, 0.40]], np.float32)
ft = PAL[rng.integers(0, len(PAL), NP)]; fa = rng.uniform(0, np.pi, NP).astype(np.float32)
paddy = ft[fid]
a = fa[fid]; paddy *= (1 + 0.08 * np.sin(2 * np.pi * (xs * np.cos(a) + ys * np.sin(a)) / 5.0))[..., None]
paddy *= (1 - 0.10 * np.clip(1.4 - fe, 0, 1))[..., None]          # bờ ruộng
del a, fid
# ---- sườn núi: nền rừng xanh sẫm, vách đá xám ở chỗ dốc
n1 = fbm((MH, MW), 5, 51, base=10)
hill = np.stack([0.27 + 0.04 * n1, 0.31 + 0.04 * n1, 0.17 + 0.03 * n1], -1)
rock = sstep(1.5, 2.1, slope + 1.2 * fbm((MH, MW), 4, 52, base=90))
hill = hill * (1 - rock[..., None]) + np.array([0.56, 0.55, 0.48], np.float32) * rock[..., None]
C = paddy * V[..., None] + hill * (1 - V[..., None])
del paddy, hill
C = C * (0.62 + 0.62 * shade[..., None] ** 1.3)
lum = C.mean(-1); p5, p95 = np.percentile(lum[::7, ::7], [5, 95])
nl_ = 0.26 + (lum - p5) / (p95 - p5) * (0.72 - 0.26); nl_ = np.where(nl_ > 0.62, 0.62 + (nl_ - 0.62) * 0.6, nl_)
C *= (nl_ / np.maximum(lum, 1e-3))[..., None]; del lum, nl_
g_ = C.mean(-1, keepdims=True); C = g_ + (C - g_) * 0.78
log("colour")
img = Image.fromarray((np.clip(C, 0, 1) * 255).astype(np.uint8)); del C
dr_ = ImageDraw.Draw(img, "RGBA")
for k, s in enumerate(STREAMS):
    p = wobble(wobble(s, 50, 40, 100 + k), 5, 8, 200 + k)
    dr_.line(p, fill=(50, 65, 35, 140), width=10, joint="curve"); dr_.line(p, fill=(70, 118, 140, 255), width=5, joint="curve")
    dr_.line(p, fill=(130, 172, 190, 190), width=2, joint="curve")
p = wobble(wobble(ROADS["rc4"], 30, 30, 300), 3, 6, 301)
dr_.line(p, fill=(80, 64, 40, 190), width=8, joint="curve"); dr_.line(p, fill=(176, 150, 100, 200), width=3, joint="curve")
for k, tp in enumerate(TRACKS.values()):
    p = wobble(wobble(tp, 25, 25, 400 + k), 3, 6, 410 + k)
    dr_.line(p, fill=(90, 72, 45, 170), width=4, joint="curve")
log("roads")
# ---- cây rừng phủ sườn núi
forest = (V < 0.35) & (rock < 0.5) & (fbm((MH, MW), 4, 61, base=40) > -0.85)
fy, fx = np.nonzero(forest[::4, ::4]); fy = fy * 4; fx = fx * 4
sel = rng.random(len(fx)) < 0.75
tx = fx[sel] + rng.uniform(-2, 2, sel.sum()); ty = fy[sel] + rng.uniform(-2, 2, sel.sum())
order = np.argsort(ty); tx, ty = tx[order], ty[order]
sh_l = Image.new("RGBA", (MW, MH), (0, 0, 0, 0)); td = ImageDraw.Draw(sh_l)
rad = rng.uniform(2.6, 4.6, len(tx))
for x, y, r in zip(tx, ty, rad): td.ellipse((x - r + 2.5, y - r + 2.5, x + r + 3.5, y + r + 3.5), fill=(15, 20, 8, 140))
sh_l = sh_l.filter(ImageFilter.GaussianBlur(1.2))
tr = Image.new("RGBA", (MW, MH), (0, 0, 0, 0)); td = ImageDraw.Draw(tr)
sh_s = shade[ty.astype(int).clip(0, MH - 1), tx.astype(int).clip(0, MW - 1)]
tone = rng.uniform(0.85, 1.12, len(tx)) * np.clip(0.45 + 0.62 * sh_s, 0.45, 1.35)
for x, y, r, k in zip(tx, ty, rad, tone):
    td.ellipse((x - r, y - r, x + r, y + r), fill=(int(40 * k), int(56 * k), int(22 * k), 255))
    r2 = r * 0.55
    td.ellipse((x - r * 0.75, y - r * 0.75, x - r * 0.75 + r2 * 1.6, y - r * 0.75 + r2 * 1.6), fill=(int(86 * k), int(104 * k), int(46 * k), 255))
img = Image.alpha_composite(Image.alpha_composite(img.convert("RGBA"), sh_l), tr).convert("RGB")
del sh_l, tr
log("trees", len(tx))
dr_ = ImageDraw.Draw(img, "RGBA")
for nm, ((vx, vy), n, r) in VILLAGES.items():
    for i in range(n):
        a_ = rng.uniform(0, 6.28); d_ = r * math.sqrt(rng.random()); hx, hy = vx + d_ * math.cos(a_), vy + d_ * math.sin(a_) * 0.8
        w, h = rng.uniform(9, 15), rng.uniform(6, 9); ang = rng.uniform(0, 3.14); c, s_ = math.cos(ang), math.sin(ang)
        q = [(hx + c * u - s_ * v, hy + s_ * u + c * v) for u, v in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
        dr_.polygon([(x + 4, y + 4) for x, y in q], fill=(30, 28, 15, 120))
        dr_.polygon(q, fill=((150, 120, 70) if rng.random() < 0.7 else (120, 112, 100)) + (255,), outline=(60, 45, 30, 255))
log("villages")
img.save(os.path.join(HERE, "map_full.png"))
img.resize((MW // 4, MH // 4), Image.LANCZOS).save(os.path.join(HERE, "map_prev.jpg"), quality=90)
json.dump({"villages": {k: v[0] for k, v in VILLAGES.items()}, "p477": POINT477, "roads": ROADS, "tracks": TRACKS},
          open(os.path.join(HERE, "geo.json"), "w"), ensure_ascii=False)
log("done")
