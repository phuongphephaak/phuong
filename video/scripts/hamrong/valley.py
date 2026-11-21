"""Sơ đồ minh họa lòng chảo Điện Biên Phủ (tọa độ km, gốc = hầm chỉ huy Mường Thanh, x đông, y bắc)."""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
EXT = (-18.0, 18.0, -13.0, 13.0)   # x0 x1 y0 y1 km
PPK = 90                           # px per km in base raster
POS = {"himlam": (2.6, 2.8), "doclap": (0.6, 5.8), "bankeo": (-1.8, 2.8), "huguette": (-0.75, 0.9),
       "claudine": (-0.6, -0.9), "dominique": (1.55, 0.75), "eliane": (1.35, -0.55), "a1": (1.15, -0.25),
       "isabelle": (0.2, -5.6), "hq": (0.0, 0.0)}
RIVER = [(1.4, 11), (1.0, 8), (0.7, 5), (0.35, 2), (0.3, 0), (0.25, -2.5), (0.5, -5), (0.9, -8), (1.3, -11)]
RUNWAY = [(-0.38, -0.5), (-0.18, 1.7)]
BUMPS = [(2.6, 2.8, 0.45, 60), (0.6, 5.8, 0.5, 70), (1.55, 0.75, 0.35, 45), (1.35, -0.55, 0.35, 40), (1.15, -0.25, 0.28, 45),
         (-1.8, 2.8, 0.3, 20)]


def _relief():
    p = os.path.join(HERE, "tmp", "valley_base.png")
    if os.path.exists(p):
        return Image.open(p)
    x0, x1, y0, y1 = EXT
    w, h = int((x1 - x0) * PPK), int((y1 - y0) * PPK)
    xs = np.linspace(x0, x1, w)[None, :]; ys = np.linspace(y1, y0, h)[:, None]
    rng = np.random.default_rng(7)
    def noise(scale, amp):
        g = rng.random((int(h / scale) + 3, int(w / scale) + 3)).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((w + 3 * scale, h + 3 * scale), Image.BICUBIC)
        return (np.asarray(im)[:h, :w].astype(np.float32) / 255 - 0.5) * amp
    half = 3.2 + 0.6 * np.sin(ys / 3.0) + 0.25 * np.cos(ys / 1.3)          # valley half-width
    cxv = 0.4 + 0.5 * np.sin(ys / 5.0)
    d = np.abs(xs - cxv) - half
    elev = np.where(d > 0, 180 * (1 - np.exp(-d / 2.2)) + 25 * d, 0.0)
    elev = elev + noise(90, 160) * (d > -0.5) + noise(30, 50) * (d > -0.5) + noise(12, 14) * np.where(d > 0, 1.0, 0.25)
    for bx, by, r, hgt in BUMPS:
        elev += hgt * np.exp(-(((xs - bx) ** 2 + (ys - by) ** 2) / (r * r)))
    gy, gx = np.gradient(elev)
    shade = np.clip(0.55 + (-gx * 0.9 + gy * 0.7) * 0.22, 0, 1)
    hn = np.clip(elev / 260, 0, 1)
    low = np.array([150, 150, 96], np.float32); mid = np.array([70, 92, 52], np.float32); hi = np.array([44, 62, 40], np.float32)
    col = np.where(hn[..., None] < 0.25, low + (mid - low) * (hn[..., None] / 0.25), mid + (hi - mid) * ((hn[..., None] - 0.25) / 0.75))
    rgb = col * (0.45 + 0.9 * shade[..., None])
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    d2 = ImageDraw.Draw(im)
    P = lambda x, y: ((x - x0) * PPK, (y1 - y) * PPK)
    d2.line([P(*q) for q in RIVER], fill=(70, 110, 130), width=9, joint="curve")
    (ax, ay), (bx, by) = RUNWAY
    d2.line([P(ax, ay), P(bx, by)], fill=(150, 140, 110), width=22)
    d2.line([P(0.0, -5.0), P(0.05, -6.0)], fill=(150, 140, 110), width=16)
    os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p)
    return im


class Valley:
    def __init__(self, v0, v1, W, H):
        self.v0, self.v1, self.W, self.H = v0, v1, W, H

    def frame(self, k):
        k = k * k * (3 - 2 * k)
        self.cx, self.cy, self.wk = (a + (b - a) * k for a, b in zip(self.v0, self.v1))
        self.ppk = self.W / self.wk
        base = _relief(); x0, x1, y0, y1 = EXT
        hk = self.wk * self.H / self.W
        box = ((self.cx - self.wk / 2 - x0) * PPK, (y1 - self.cy - hk / 2) * PPK,
               (self.cx + self.wk / 2 - x0) * PPK, (y1 - self.cy + hk / 2) * PPK)
        return base.resize((self.W, self.H), Image.BICUBIC, box=box).convert("RGBA")

    def P(self, at):
        x, y = POS[at] if isinstance(at, str) else at
        return (self.W / 2 + (x - self.cx) * self.ppk, self.H / 2 - (y - self.cy) * self.ppk)
