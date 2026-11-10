"""Render two animated map clips (1920x1080, 30 fps) for the HMS Coventry draft.
Usage: python make_maps.py <land.geojson> <out_dir>
"""
import json, math, os, subprocess, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib import patheffects as pe

W, H, FPS = 1920, 1080, 30
SEA, LAND, EDGE, GRID = "#0d1b24", "#5a5547", "#a39a80", "#1c2f3a"
RED, AMBER, WHITE = "#e04a3a", "#f0b54a", "#e8e4d8"
FONT = "DejaVu Sans"
plt.rcParams["font.family"] = FONT

RIO_GALLEGOS = (-69.31, -51.63)
SHIP = (-59.72, -51.08)          # approx. position north of Pebble Island, 25 May 1982
STANLEY = (-57.85, -51.69)

land = json.load(open(sys.argv[1]))
out = sys.argv[2]
os.makedirs(out, exist_ok=True)

polys = []
for f in land["features"]:
    g = f["geometry"]
    rings = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
    for poly in rings:
        ring = np.array(poly[0])
        if ring[:, 0].max() < -80 or ring[:, 0].min() > -45 or ring[:, 1].max() < -60 or ring[:, 1].min() > -40:
            continue
        polys.append(ring)

ASPECT = 1 / math.cos(math.radians(51.5))


def new_fig():
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(SEA)
    fig.patch.set_facecolor(SEA)
    ax.add_collection(PolyCollection(polys, facecolors=LAND, edgecolors=EDGE, linewidths=1.0, zorder=2))
    for lon in range(-80, -40, 2):
        ax.axvline(lon, color=GRID, lw=0.8, zorder=1)
    for lat in range(-60, -40, 1):
        ax.axhline(lat, color=GRID, lw=0.8, zorder=1)
    ax.set_aspect(ASPECT)
    ax.axis("off")
    return fig, ax


def set_view(ax, cx, cy, half_w):
    half_h = half_w * (H / W) / ASPECT
    ax.set_xlim(cx - half_w, cx + half_w)
    ax.set_ylim(cy - half_h, cy + half_h)


def label(ax, x, y, text, size=26, color=WHITE, weight="bold", **kw):
    return ax.text(x, y, text, fontsize=size, color=color, weight=weight, zorder=10,
                   path_effects=[pe.withStroke(linewidth=5, foreground="#000000aa")], **kw)


def ease(t):
    t = min(max(t, 0), 1)
    return t * t * (3 - 2 * t)


def encode(name, frames_fn, n):
    path = os.path.join(out, name)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt",
                          "yuv420p", "-crf", "18", path], stdin=subprocess.PIPE)
    for i in range(n):
        fig = frames_fn(i / FPS)
        fig.canvas.draw()
        p.stdin.write(fig.canvas.buffer_rgba().tobytes())
        plt.close(fig)
    p.stdin.close(); p.wait()
    print("wrote", path, flush=True)


# --- Map A: region overview, zoom to the ship's patrol position -----------------------------
def map_a(t):
    fig, ax = new_fig()
    k = ease((t - 1.0) / 6.0)
    cx = -64.5 + (SHIP[0] + 0.3 - -64.5) * k
    cy = -51.0 + (SHIP[1] - 0.2 - -51.0) * k
    set_view(ax, cx, cy, 9.0 - 6.6 * k)
    a = min(1, t / 0.8)
    label(ax, -68.8, -49.2, "ARGENTINA", 34, alpha=a * (1 - k))
    label(ax, -60.6, -52.6, "QUẦN ĐẢO FALKLAND\n(MALVINAS)", 26, alpha=a * (1 - k), ha="center")
    ax.plot(*RIO_GALLEGOS, "o", color=AMBER, ms=12, zorder=9, alpha=a * (1 - k))
    label(ax, RIO_GALLEGOS[0] + 0.3, RIO_GALLEGOS[1] - 0.45, "Río Gallegos", 22, AMBER, alpha=a * (1 - k))
    if t > 4.5:
        b = min(1, (t - 4.5) / 0.8)
        pulse = 18 + 8 * math.sin(t * 6)
        ax.plot(*SHIP, "o", color=RED, ms=14, zorder=9, alpha=b)
        ax.plot(*SHIP, "o", mfc="none", mec=RED, mew=3, ms=pulse + 14, zorder=9, alpha=b * 0.7)
        label(ax, SHIP[0] + 0.12, SHIP[1] + 0.12, "HMS Coventry\n& HMS Broadsword", 26, alpha=b)
        label(ax, -59.45, -51.38, "Đảo Pebble", 20, "#cfc6aa", weight="normal", alpha=b)
    label(ax, 0.03, 0.05, "25/05/1982  ·  Nam Đại Tây Dương", 30, transform=ax.transAxes)
    return fig


# --- Map B: A-4 attack route from Río Gallegos -------------------------------------------------
route_ctrl = np.array([RIO_GALLEGOS, (-65.0, -50.6), (-61.5, -50.75), (SHIP[0] - 0.05, SHIP[1] + 0.02)])


def bezier(pts, n=400):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = pts
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


ROUTE = bezier(route_ctrl)


def map_b(t):
    fig, ax = new_fig()
    set_view(ax, -63.4, -51.2, 6.4)
    ax.plot(*RIO_GALLEGOS, "o", color=AMBER, ms=12, zorder=9)
    label(ax, RIO_GALLEGOS[0] + 0.25, RIO_GALLEGOS[1] - 0.45, "Río Gallegos", 22, AMBER)
    ax.plot(*SHIP, "o", color=RED, ms=14, zorder=9)
    label(ax, SHIP[0] - 0.3, SHIP[1] + 0.3, "HMS Coventry", 24, ha="right")
    k = ease((t - 0.8) / 6.0)
    n = max(2, int(k * len(ROUTE)))
    seg = ROUTE[:n]
    for off, a in ((0.0, 1.0), (0.07, 0.6)):
        ax.plot(seg[:, 0], seg[:, 1] + off, color=AMBER, lw=4, ls=(0, (6, 4)), alpha=a, zorder=8)
    if k < 1:
        p, q = seg[-1], seg[-2]
        ang = math.degrees(math.atan2((p[1] - q[1]) * ASPECT, p[0] - q[0]))
        for off in (0.0, 0.07):
            ax.plot(p[0], p[1] + off, marker=(3, 0, ang - 90), color=AMBER, ms=24, zorder=9)
    label(ax, 0.03, 0.88, "Cường kích A-4 Skyhawk · Không quân Argentina", 30, transform=ax.transAxes)
    label(ax, 0.03, 0.82, "Bay sát mặt biển để tránh radar", 24, "#cfc6aa", weight="normal",
          transform=ax.transAxes)
    if k >= 1:
        b = min(1, (t - 6.8) / 0.4)
        r = 20 + 60 * b
        ax.plot(*SHIP, "o", mfc="none", mec=RED, mew=4, ms=r, zorder=9, alpha=1 - b * 0.6)
        label(ax, 0.62, 0.12, "TẤN CÔNG", 44, RED, transform=ax.transAxes, alpha=b)
    return fig


import sys as _s
if "b" not in _s.argv[3:]: encode("map_a.mp4", map_a, int(8 * FPS))
encode("map_b.mp4", map_b, int(8.5 * FPS))
