"""Dữ liệu dùng chung cho sa bàn Điện Biên Phủ v3 (1 BU = 1 km, gốc = hầm chỉ huy Mường Thanh)."""
import math
import numpy as np

X0, X1, Y0, Y1 = -7.5, 7.5, -8.0, 9.0

POS = {"himlam": (2.6, 2.8), "doclap": (0.6, 5.8), "bankeo": (-1.8, 2.8), "huguette": (-0.75, 0.9),
       "claudine": (-0.6, -0.9), "dominique": (1.55, 0.75), "eliane": (1.35, -0.55), "a1": (1.15, -0.25),
       "isabelle": (0.2, -5.6), "hq": (0.0, 0.0)}
RIVER = [(1.4, 11), (1.0, 8), (0.7, 5), (0.35, 2), (0.3, 0), (0.25, -2.5), (0.5, -5), (0.9, -8), (1.3, -11)]
ry = np.array([p[1] for p in RIVER])[::-1]
rx = np.array([p[0] for p in RIVER])[::-1]
VN_POS = [(4.6, 3.6), (4.4, 1.2), (4.8, -1.4), (3.9, 5.6), (1.6, 7.6), (-1.4, 7.4), (-4.3, 4.4), (-4.5, 1.0),
          (-4.6, -2.6), (3.8, -4.4), (-3.4, -6.0), (3.4, 4.5)]
# bán kính vùng kiểm soát của Pháp quanh từng cứ điểm
ZR = {"himlam": 0.75, "doclap": 0.75, "bankeo": 0.7, "huguette": 0.95, "claudine": 0.95, "dominique": 0.85,
      "eliane": 0.85, "a1": 0.75, "isabelle": 0.95, "hq": 1.3}
# đường hào tiếp cận của ta (vào Him Lam, Độc Lập, Bản Kéo)
SAPS = [[(4.4, 3.4), (3.9, 3.1), (3.4, 2.95), (3.05, 2.85)],
        [(3.8, 5.3), (3.4, 4.4), (3.0, 3.7), (2.8, 3.3)],
        [(1.5, 7.3), (1.1, 6.7), (0.85, 6.3)],
        [(-4.1, 4.2), (-3.2, 3.6), (-2.3, 3.0)]]
VILLAGES = [(-1.2, -0.3), (0.9, 1.9), (-0.4, 3.6), (1.9, -2.2), (-0.9, -3.4), (0.8, -4.2), (-0.3, -6.6),
            (1.8, 4.3), (-1.5, 5.4), (2.3, -0.9)]


def river_x(y):
    """sông Nậm Rốm uốn khúc"""
    return np.interp(y, ry, rx) + 0.12 * np.sin(y * 3.1 + 0.4) + 0.05 * np.sin(y * 5.3 + 1.1) + 0.03 * np.sin(y * 9.7 + 2.0) + 0.012 * np.sin(y * 23.0)


def fbm(shape, octaves, seed, base=4, dtype=np.float32):
    r = np.random.default_rng(seed); out = np.zeros(shape, dtype)
    for o in range(octaves):
        f = 2 ** o
        g = r.standard_normal((base * f + 3, base * f + 3)).astype(dtype)
        gy = np.linspace(0, g.shape[0] - 1.001, shape[0]); gx = np.linspace(0, g.shape[1] - 1.001, shape[1])
        iy = gy.astype(int); ix = gx.astype(int)
        fy = (gy - iy).astype(dtype)[:, None]; fx = (gx - ix).astype(dtype)[None, :]
        fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
        a = g[iy][:, ix]; b = g[iy][:, ix + 1]; c = g[iy + 1][:, ix]; d = g[iy + 1][:, ix + 1]
        out += ((a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy) / dtype(1.7 ** o)
    return out


def terrain(nx, ny, dtype=np.float32):
    xs = np.linspace(X0, X1, nx, dtype=dtype); ys = np.linspace(Y0, Y1, ny, dtype=dtype)
    XX, YY = np.meshgrid(xs, ys)
    half = 3.0 + 0.5 * np.sin(YY / 3.0) + 0.25 * np.cos(YY / 1.3)
    d = np.abs(XX - (0.4 + 0.5 * np.sin(YY / 5.0))) - half
    n1 = fbm(XX.shape, 6, 11, dtype=dtype); n2 = fbm(XX.shape, 7, 23, dtype=dtype)
    hills = np.clip(d, 0, None)
    Z = 0.95 * (1 - np.exp(-hills / 1.6)) * (0.8 + 0.25 * (1 - np.abs(n2) * 0.9)) + 0.04 * hills
    Z += np.where(d > -0.4, 0.13 * n1 * np.clip((d + 0.4) / 1.5, 0, 1), 0) + 0.01 * n1
    for (bx, by, r, h) in [(2.6, 2.8, 0.45, 0.22), (0.6, 5.8, 0.5, 0.28), (1.55, 0.75, 0.35, 0.18),
                           (1.35, -0.55, 0.35, 0.16), (1.15, -0.25, 0.28, 0.18), (-1.8, 2.8, 0.3, 0.08)]:
        Z += h * np.exp(-((XX - bx) ** 2 + (YY - by) ** 2) / (r * r))
    rvx = river_x(YY).astype(dtype)
    Z -= 0.025 * np.exp(-((XX - rvx) / 0.07) ** 2)
    return xs, ys, XX, YY, Z.astype(dtype), d, n1, n2, rvx


def french_field(XX, YY, noise):
    """>0 trong vùng Pháp kiểm soát (đơn vị ≈ BU)."""
    k = 0.18; acc = np.zeros(XX.shape, XX.dtype)
    for key, (px, py) in POS.items():
        acc += np.exp((ZR[key] - np.hypot(XX - px, YY - py)) / k)
    return k * np.log(acc + 1e-30) + 0.10 * noise
