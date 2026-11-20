"""Tạo texture màu + mask (trường khoảng cách) cho sa bàn v3.  python3 tex3.py"""
import math, os, sys, time
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from dbp_common import *

t0 = time.time()
TW = 4096; TH = round(TW * (Y1 - Y0) / (X1 - X0))
_, _, TX, TY, TZ, Td, m1, m2, rvx = terrain(TW, TH)
px_bu = TW / (X1 - X0)
p1 = fbm(TX.shape, 7, 101, 6); p2 = fbm(TX.shape, 7, 202, 10); p3 = fbm(TX.shape, 6, 303, 3); p4 = fbm(TX.shape, 8, 404, 16)
print("noise", time.time() - t0, flush=True)
s = lambda c: np.array(c, np.float32)


def mix(C, col, a):
    a = np.asarray(a, np.float32)[..., None]; return C * (1 - a) + col * a


def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)


# ---------- nền nỉ cỏ: lòng chảo vàng-xanh, đồi xanh rêu đậm
C = mix(np.broadcast_to(s([0.60, 0.61, 0.30]), TX.shape + (3,)).copy(), s([0.47, 0.52, 0.24]), sstep(-0.3, 0.4, p1))
C = mix(C, s([0.66, 0.60, 0.38]), 0.55 * sstep(0.35, 0.8, p3))           # ruộng khô
C = mix(C, s([0.42, 0.36, 0.25]), 0.45 * sstep(0.55, 1.0, p2))           # đất nâu
H = mix(np.broadcast_to(s([0.30, 0.37, 0.17]), TX.shape + (3,)).copy(), s([0.40, 0.45, 0.21]), sstep(-0.4, 0.5, p2))
H = mix(H, s([0.22, 0.28, 0.13]), 0.6 * sstep(0.2, 0.9, p1))           # rừng rậm
H = mix(H, s([0.55, 0.52, 0.42]), 0.55 * sstep(0.62, 0.95, TZ) * sstep(0.0, 0.6, p3))  # đỉnh đá
C = mix(C, H, sstep(0.05, 0.22, TZ))
C *= (0.9 + 0.12 * p4[..., None])
del H

# ---------- vùng kiểm soát: đỏ = Pháp, xanh = Quân đội nhân dân VN
ff = french_field(TX, TY, m1 * 0.9 + p3 * 0.7 + p2 * 0.5)
red = sstep(-0.004, 0.004, ff)
# đỏ nỉ: đỏ son -> cam -> vàng đất (kiểu Verdun)
redcol = mix(np.broadcast_to(s([0.72, 0.17, 0.14]), TX.shape + (3,)).copy(), s([0.86, 0.42, 0.16]), 0.75 * sstep(0.1, 0.9, p1))
redcol = mix(redcol, s([0.80, 0.62, 0.30]), 0.45 * sstep(0.55, 1.1, p3))
redcol = mix(redcol, s([0.55, 0.12, 0.10]), 0.5 * sstep(0.2, 0.8, p2))
lum = C.mean(-1, keepdims=True)
C = mix(C, redcol * (0.75 + 0.5 * lum), 0.88 * red)
vnd = np.full(TX.shape, 9, np.float32)
for (vx, vy) in VN_POS:
    vnd = np.minimum(vnd, np.hypot(TX - vx, TY - vy))
ring = sstep(-0.35, 0.35, Td + 0.25 * p1) * sstep(2.6, 1.8, Td + 0.3 * p2)     # đồi bao quanh lòng chảo
ring = sstep(-0.15, 0.05, Td + 0.35 * p1 + 0.2 * p2) * sstep(2.2, 1.9, Td + 0.4 * p2)
blue_raw = np.maximum(ring, sstep(0.75, 0.6, vnd + 0.15 * p1))
# dải ô liu mảnh ở mép vùng đỏ (vùng tranh chấp)
band = sstep(-0.06, -0.035, ff + 0.01 * p4) * (1 - red)
blue_a = blue_raw * (1 - band) * (1 - red)
bluecol = mix(np.broadcast_to(s([0.26, 0.44, 0.74]), TX.shape + (3,)).copy(), s([0.36, 0.55, 0.82]), 0.6 * sstep(-0.3, 0.7, p2))
bluecol = mix(bluecol, s([0.20, 0.33, 0.60]), 0.4 * sstep(0.3, 0.9, p1))
C = mix(C, bluecol * (0.75 + 0.5 * lum), 0.90 * blue_a)
C = mix(C, s([0.50, 0.50, 0.24]), 0.9 * band * sstep(0.2, 0.6, blue_raw + 0.5))
del redcol, bluecol, lum
# vùng bị pháo kích quanh cứ điểm: đất xám nâu + vết cháy đen
rng = np.random.default_rng(5)
for k, (px, py) in POS.items():
    r = np.hypot(TX - px, TY - py)
    C = mix(C, s([0.40, 0.35, 0.31]) * (0.85 + 0.3 * p4[..., None]), 0.85 * sstep(0.30, 0.17, r + 0.06 * p4 + 0.04 * p2))
    for j in range(14):
        a = rng.uniform(0, 6.28); d = rng.uniform(0.05, 0.42); cx, cy = px + d * np.cos(a), py + d * np.sin(a)
        rr = rng.uniform(0.012, 0.03)
        sl = (slice(max(0, int((cy - 0.08 - Y0) * TH / (Y1 - Y0))), int((cy + 0.08 - Y0) * TH / (Y1 - Y0))),
              slice(max(0, int((cx - 0.08 - X0) * TW / (X1 - X0))), int((cx + 0.08 - X0) * TW / (X1 - X0))))
        q = np.hypot(TX[sl] - cx, TY[sl] - cy) + 0.012 * p4[sl] + 0.006 * p2[sl]
        C[sl] = mix(C[sl], s([0.07, 0.06, 0.055]), 0.92 * sstep(rr, rr * 0.6, q))
print("zones", time.time() - t0, flush=True)

# ---------- mask: R đường, G sông, B nét đậm (tiền tuyến + giao thông hào)
# mạng đường kiểu Verdun: cạnh của các ô Voronoi (đoạn gấp khúc nối nhau ở ngã ba)
from scipy.spatial import cKDTree
pr = np.random.default_rng(9); pts = []
for gy_ in np.arange(Y0 - 0.5, Y1 + 0.5, 1.35):
    for gx_ in np.arange(X0 - 0.5, X1 + 0.5, 1.35):
        pts.append((gx_ + pr.uniform(-0.5, 0.5), gy_ + pr.uniform(-0.5, 0.5)))
pts = np.array(pts); kd = cKDTree(pts)
WX = TX + 0.05 * m1 + 0.02 * p2; WY = TY + 0.05 * m2 + 0.02 * p1     # uốn nhẹ
road = np.empty(TX.shape, np.float32)
CH = 400
for r0 in range(0, TH, CH):
    q = np.c_[WX[r0:r0 + CH].ravel(), WY[r0:r0 + CH].ravel()]
    dd, ii = kd.query(q, k=2)
    ab = np.hypot(*(pts[ii[:, 0]] - pts[ii[:, 1]]).T)
    lo = np.minimum(ii[:, 0], ii[:, 1]); hi = np.maximum(ii[:, 0], ii[:, 1])
    keep = ((lo * 7919 + hi * 104729) % 100) < 62           # bỏ bớt cạnh -> có đường cụt
    e = (dd[:, 1] ** 2 - dd[:, 0] ** 2) / (2 * ab)
    road[r0:r0 + CH] = np.where(keep, e, 0.3).reshape(-1, TW)
road = road - 0.007 + 0.006 * p4 + 0.004 * p2 + 0.004 * sstep(0.25, 0.6, TZ)
del WX, WY
r41 = np.abs(TX - (np.interp(TY, ry, rx) - 0.6 + 0.15 * np.sin(TY * 1.3))) - 0.016 + 0.006 * p4
road = np.minimum(road, r41)
# sân bay Mường Thanh
ang = math.atan2(2.2, 0.2); dx, dy = math.cos(ang), math.sin(ang)
lx = (TX + 0.28) * dx + (TY - 0.6) * dy; ly = -(TX + 0.28) * dy + (TY - 0.6) * dx
road = np.minimum(road, np.maximum(np.abs(lx) - 1.15, np.abs(ly) - 0.035))
dr = np.abs(TX - rvx) - 0.03 + 0.006 * p4 + 0.006 * m2
road = np.where(dr < 0.03, np.maximum(road, 0.02), road)        # đường không đè lên sông
R = np.clip(1 - (road + 0.014) / 0.06, 0, 1)      # lõi đường: R > 0.766 ; muối rắc tới R≈0.3
G = np.clip(1 - (dr + 0.03) / 0.10, 0, 1)         # nước: G > 0.70, bờ: G > 0.52

line = np.abs(ff) - 0.006        # tiền tuyến


def poly_dist(pts):
    d = np.full(TX.shape, 9, np.float32)
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        vx, vy = bx - ax, by - ay; L2 = vx * vx + vy * vy
        t = np.clip(((TX - ax) * vx + (TY - ay) * vy) / L2, 0, 1)
        d = np.minimum(d, np.hypot(TX - ax - t * vx, TY - ay - t * vy))
    return d


for sap in SAPS:     # hào tiếp cận kép, gấp khúc
    pts = []
    for (a, b) in zip(sap[:-1], sap[1:]):
        for u in np.linspace(0, 1, 7)[:-1]:
            x = a[0] + (b[0] - a[0]) * u; y = a[1] + (b[1] - a[1]) * u
            nx_, ny_ = -(b[1] - a[1]), b[0] - a[0]; nl = math.hypot(nx_, ny_)
            z = 0.025 * (1 if len(pts) % 2 else -1)
            pts.append((x + nx_ / nl * z, y + ny_ / nl * z))
    pts.append(sap[-1])
    d = poly_dist(pts)
    line = np.minimum(line, np.abs(d - 0.009) - 0.0035)
for k, (px, py) in POS.items():   # giao thông hào kép quanh cứ điểm Pháp
    r = np.hypot(TX - px, TY - py); a = np.arctan2(TY - py, TX - px)
    for rr in (0.30, 0.335):
        line = np.minimum(line, np.abs(r - rr - 0.015 * np.sin(a * 7 + px)) - 0.003)
B = np.clip(1 - (line + 0.0035) / 0.03, 0, 1)     # nét: B > 0.883
print("masks", time.time() - t0, flush=True)

C = np.clip(C, 0, 1)
Image.fromarray((C[::-1] * 255 + 0.5).astype(np.uint8)).save(os.path.join(HERE, "tex3_col.png"))
M = np.stack([R, G, B], -1)
Image.fromarray((M[::-1] * 255 + 0.5).astype(np.uint8)).save(os.path.join(HERE, "tex3_mask.png"))
Image.fromarray((C[::-1][::4, ::4] * 255).astype(np.uint8)).save(os.path.join(HERE, "tex3_prev.jpg"))
print("done", time.time() - t0)
