"""Animated maps for the 10-minute film.  render(kind, dur, out)
kinds: atlantic, region, sancarlos, picket, attack, geometry, end
"""
import json, math, os, subprocess, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib import patheffects as pe

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1920, 1080, 30
SEA, LAND, EDGE, GRID = "#0d1b24", "#5a5547", "#a39a80", "#1c2f3a"
RED, AMBER, WHITE, BLUE = "#e04a3a", "#f0b54a", "#e8e4d8", "#5fa8e0"
plt.rcParams["font.family"] = "DejaVu Sans"

RIO_GALLEGOS = (-69.31, -51.63)
SHIP = (-59.70, -51.06)
SAN_CARLOS = (-59.07, -51.50)
STANLEY = (-57.85, -51.69)
PORTSMOUTH = (-1.09, 50.80)
ASCENSION = (-14.36, -7.95)
PEBBLE = (-59.55, -51.31)

_land = json.load(open(os.path.join(HERE, "land10.geojson")))
ALL = []
for f in _land["features"]:
    g = f["geometry"]
    for poly in ([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]):
        ALL.append(np.array(poly[0]))


def polys_in(lon0, lon1, lat0, lat1, simplify=1):
    out = []
    for r in ALL:
        if r[:, 0].max() < lon0 or r[:, 0].min() > lon1 or r[:, 1].max() < lat0 or r[:, 1].min() > lat1:
            continue
        out.append(r[::simplify] if len(r) > 50 else r)
    return out


def label(ax, x, y, text, size=26, color=WHITE, weight="bold", **kw):
    return ax.text(x, y, text, fontsize=size, color=color, weight=weight, zorder=10,
                   path_effects=[pe.withStroke(linewidth=5, foreground="#000000aa")], **kw)


def ease(t):
    t = min(max(t, 0), 1)
    return t * t * (3 - 2 * t)


def encode(path, frames_fn, n):
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


class Map:
    def __init__(self, polys, aspect):
        self.polys, self.aspect = polys, aspect

    def fig(self, cx, cy, half_w, grid=(2, 1)):
        fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor(SEA); fig.patch.set_facecolor(SEA)
        ax.add_collection(PolyCollection(self.polys, facecolors=LAND, edgecolors=EDGE, linewidths=1.0, zorder=2))
        half_h = half_w * (H / W) / self.aspect
        x0, x1, y0, y1 = cx - half_w, cx + half_w, cy - half_h, cy + half_h
        for lon in np.arange(math.floor(x0 / grid[0]) * grid[0], x1, grid[0]):
            ax.axvline(lon, color=GRID, lw=0.8, zorder=1)
        for lat in np.arange(math.floor(y0 / grid[1]) * grid[1], y1, grid[1]):
            ax.axhline(lat, color=GRID, lw=0.8, zorder=1)
        ax.set_aspect(self.aspect); ax.axis("off")
        ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
        return fig, ax


def path_along(pts, k):
    pts = np.array(pts, float)
    seg = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(1)); cum = np.concatenate([[0], np.cumsum(seg)])
    d = k * cum[-1]
    i = min(np.searchsorted(cum, d, side="right") - 1, len(seg) - 1)
    f = (d - cum[i]) / max(seg[i], 1e-9)
    p = pts[i] + (pts[i + 1] - pts[i]) * f
    return np.vstack([pts[:i + 1], p]), p, pts[i + 1] - pts[i]


def bezier(pts, n=300):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = [np.array(p, float) for p in pts]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


# ------------------------------------------------------------------ kinds
def atlantic(out, dur):
    m = Map(polys_in(-80, 20, -65, 65, simplify=3), 1.0)
    route = [PORTSMOUTH, (-10, 40), (-18, 15), ASCENSION, (-30, -25), (-50, -45), (-58.5, -51.2)]
    route = np.vstack([bezier([route[0], route[1], route[2], route[3]], 120),
                       bezier([route[3], route[4], route[5], route[6]], 120)])

    def fr(t):
        z = ease((t - 0.5) / (dur - 1.5))
        fig, ax = m.fig(-30 - 20 * z, 8 - 44 * z, 62 - 28 * z, grid=(10, 10))
        label(ax, -50, -50, "QUẦN ĐẢO\nFALKLAND", 22, ha="left")
        label(ax, -64, -30, "ARGENTINA", 26)
        label(ax, 2, 54, "ANH", 28)
        ax.plot(*PORTSMOUTH, "o", color=AMBER, ms=11, zorder=9); label(ax, 3, 49, "Portsmouth", 20, AMBER)
        ax.plot(*ASCENSION, "o", color=AMBER, ms=9, zorder=9); label(ax, -12, -10, "Đảo Ascension", 20, AMBER)
        ax.plot(-59, -51.7, "o", color=RED, ms=12, zorder=9)
        k = ease((t - 0.8) / (dur - 2.0))
        n = max(2, int(k * len(route)))
        ax.plot(route[:n, 0], route[:n, 1], color=AMBER, lw=4, ls=(0, (6, 4)), zorder=8)
        if k < 1:
            p, q = route[n - 1], route[n - 2]
            ax.plot(p[0], p[1], marker=(3, 0, math.degrees(math.atan2(p[1] - q[1], p[0] - q[0])) - 90),
                    color=AMBER, ms=22, zorder=9)
        label(ax, 0.03, 0.92, "Hạm đội đặc nhiệm · khoảng 13.000 km", 30, transform=ax.transAxes)
        return fig
    encode(out, fr, int(dur * FPS))


def region(out, dur):
    m = Map(polys_in(-80, -45, -60, -40), 1 / math.cos(math.radians(51.5)))

    def fr(t):
        z = ease(t / dur)
        fig, ax = m.fig(-64.5 + 1.5 * z, -51.0, 9.5 - 1.5 * z)
        label(ax, -69.5, -48.7, "ARGENTINA", 34)
        label(ax, -59.0, -53.0, "QUẦN ĐẢO FALKLAND\n(MALVINAS)", 24, ha="center")
        ax.plot(*RIO_GALLEGOS, "o", color=AMBER, ms=12, zorder=9)
        label(ax, RIO_GALLEGOS[0] + 0.3, RIO_GALLEGOS[1] - 0.45, "Río Gallegos", 22, AMBER)
        k = ease((t - 1) / 3)
        xs = np.linspace(RIO_GALLEGOS[0], -61.3, 50)[:max(2, int(50 * k))]
        ys = np.linspace(RIO_GALLEGOS[1], -51.5, 50)[:len(xs)]
        ax.plot(xs, ys, color=WHITE, lw=2.5, ls=(0, (3, 3)), zorder=8)
        if k > 0.95:
            label(ax, -65.5, -51.1, "~ 500 km", 30, AMBER, ha="center")
        return fig
    encode(out, fr, int(dur * FPS))


def sancarlos(out, dur):
    m = Map(polys_in(-62, -57, -53, -50), 1 / math.cos(math.radians(51.5)))

    def fr(t):
        z = ease((t - 0.5) / 4)
        fig, ax = m.fig(-59.6 + 0.5 * z, -51.55, 2.6 - 1.6 * z, grid=(0.5, 0.25))
        label(ax, SAN_CARLOS[0] + 0.05, SAN_CARLOS[1] + 0.03, "San Carlos", 26, AMBER)
        ax.plot(*SAN_CARLOS, "o", color=AMBER, ms=12, zorder=9)
        label(ax, -59.45, -51.75, "Eo Falkland", 22, "#cfc6aa", weight="normal", rotation=50)
        label(ax, -58.6, -51.75, "ĐÔNG\nFALKLAND", 22, ha="center")
        label(ax, -60.2, -51.75, "TÂY\nFALKLAND", 22, ha="center")
        if t > 3:
            a = min(1, (t - 3) / 0.8)
            label(ax, SAN_CARLOS[0] - 0.35, SAN_CARLOS[1] - 0.12, "\"HẺM BOM\"", 34, RED, alpha=a)
            for j, (dx, dy) in enumerate(((-0.9, 0.25), (-0.95, -0.05), (-0.8, -0.3))):
                kk = ease((t - 3 - j * 0.4) / 1.5)
                x0, y0 = SAN_CARLOS[0] + dx, SAN_CARLOS[1] + dy
                ax.annotate("", xy=(x0 + (SAN_CARLOS[0] - 0.05 - x0) * kk, y0 + (SAN_CARLOS[1] - y0) * kk),
                            xytext=(x0, y0), zorder=9,
                            arrowprops=dict(arrowstyle="-|>", color=RED, lw=3, mutation_scale=28, alpha=a))
        return fig
    encode(out, fr, int(dur * FPS))


def picket(out, dur):
    m = Map(polys_in(-63, -56.5, -53, -50), 1 / math.cos(math.radians(51.5)))

    def fr(t):
        fig, ax = m.fig(-59.5, -51.35, 2.3, grid=(0.5, 0.25))
        ax.plot(*SAN_CARLOS, "o", color=AMBER, ms=12, zorder=9)
        label(ax, SAN_CARLOS[0] + 0.06, SAN_CARLOS[1] - 0.06, "San Carlos", 22, AMBER)
        label(ax, PEBBLE[0] + 0.1, PEBBLE[1] - 0.08, "Đảo Pebble", 20, "#cfc6aa", weight="normal")
        a = ease((t - 0.8) / 1.0)
        ax.plot(*SHIP, "o", color=BLUE, ms=13, zorder=9, alpha=a)
        ax.plot(SHIP[0] + 0.05, SHIP[1] + 0.02, "o", color=BLUE, ms=10, zorder=9, alpha=a)
        label(ax, SHIP[0] - 0.05, SHIP[1] + 0.09, "Coventry & Broadsword", 24, BLUE, alpha=a, ha="center")
        if t > 2.2:
            r = 0.55 * ease((t - 2.2) / 1.5)
            circ = plt.Circle(SHIP, r * 1.6, color=BLUE, fill=False, lw=2, ls="--", alpha=0.7, zorder=8)
            ax.add_patch(circ)
            ax.add_patch(plt.Circle(SHIP, r * 1.6, color=BLUE, alpha=0.08, zorder=7))
        for j in range(3):
            kk = ease((t - 3.5 - j * 0.7) / 2.0)
            if kk <= 0:
                continue
            y0 = -50.85 - j * 0.15
            x = -62.0 + (SHIP[0] - 0.4 + 62.0) * kk
            ax.annotate("", xy=(x, y0 - 0.1 * kk), xytext=(-62.0, y0), zorder=9,
                        arrowprops=dict(arrowstyle="-|>", color=RED, lw=3, mutation_scale=26))
        if t > 5.5:
            label(ax, 0.03, 0.88, "Chốt chặn phía tây bắc", 32, transform=ax.transAxes)
            label(ax, 0.03, 0.82, "Đánh chặn và thu hút đòn tấn công", 24, "#cfc6aa", weight="normal",
                  transform=ax.transAxes)
        return fig
    encode(out, fr, int(dur * FPS))


def attack(out, dur):
    m = Map(polys_in(-72, -55, -54, -48), 1 / math.cos(math.radians(51.5)))
    route = bezier([RIO_GALLEGOS, (-65.0, -50.6), (-61.5, -50.75), (SHIP[0] - 0.05, SHIP[1] + 0.02)], 400)

    def fr(t):
        fig, ax = m.fig(-63.4, -51.2, 6.4)
        ax.plot(*RIO_GALLEGOS, "o", color=AMBER, ms=12, zorder=9)
        label(ax, RIO_GALLEGOS[0] + 0.25, RIO_GALLEGOS[1] - 0.45, "Río Gallegos", 22, AMBER)
        ax.plot(*SHIP, "o", color=RED, ms=14, zorder=9)
        label(ax, SHIP[0] - 0.3, SHIP[1] + 0.3, "HMS Coventry", 24, ha="right")
        k = ease((t - 0.8) / (dur - 2.0))
        n = max(2, int(k * len(route)))
        for off, a in ((0.0, 1.0), (0.07, 0.6)):
            ax.plot(route[:n, 0], route[:n, 1] + off, color=AMBER, lw=4, ls=(0, (6, 4)), alpha=a, zorder=8)
        if k < 1:
            p, q = route[n - 1], route[n - 2]
            ang = math.degrees(math.atan2((p[1] - q[1]) * 1.6, p[0] - q[0]))
            for off in (0.0, 0.07):
                ax.plot(p[0], p[1] + off, marker=(3, 0, ang - 90), color=AMBER, ms=24, zorder=9)
        label(ax, 0.03, 0.88, "Hai cặp A-4 Skyhawk", 30, transform=ax.transAxes)
        label(ax, 0.03, 0.82, "Bay sát mặt biển để tránh radar", 24, "#cfc6aa", weight="normal", transform=ax.transAxes)
        return fig
    encode(out, fr, int(dur * FPS))


def geometry(out, dur):
    """Schematic: wave-2 attack from the west, Coventry turns across Broadsword's Sea Wolf arc."""
    def fr(t):
        fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(SEA); fig.patch.set_facecolor(SEA)
        ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.set_aspect(1); ax.axis("off")
        for g in range(0, 17):
            ax.axvline(g, color=GRID, lw=0.8)
        for g in range(0, 10):
            ax.axhline(g, color=GRID, lw=0.8)
        bx, by = 11.0, 3.2                                  # Broadsword
        k_turn = ease((t - 2.5) / 3.0)
        # Coventry path: from (12.2, 5.6) turning hard toward the west / south-west
        path = bezier([(12.8, 6.2), (12.6, 4.6), (10.8, 4.4), (8.7, 3.95)], 80)
        npts = max(2, int(len(path) * k_turn))
        seg = path[:npts]
        ax.plot(path[:, 0], path[:, 1], color=BLUE, lw=1.5, ls=":", alpha=0.35, zorder=5)
        ax.plot(seg[:, 0], seg[:, 1], color=BLUE, lw=3, ls="--", zorder=5)
        cvx, cvy = seg[-1]
        dvx, dvy = seg[-1] - seg[-2]
        ang = math.degrees(math.atan2(dvy, dvx))
        ax.add_patch(matplotlib.patches.Ellipse((cvx, cvy), 1.3, 0.32, angle=ang, color=BLUE, zorder=8))
        ax.add_patch(matplotlib.patches.Ellipse((bx, by), 1.4, 0.34, angle=90, color="#9fc6e8", zorder=8))
        label(ax, bx + 0.5, by - 0.6, "Broadsword", 24, "#9fc6e8")
        label(ax, cvx + 0.3, cvy + 0.35, "Coventry", 24, BLUE)
        # incoming A-4 pair from the west
        ka = ease((t - 0.5) / (dur - 1.5))
        ax_x = 1.0 + (bx - 1.0) * 0.85 * ka
        for off in (0, 0.45):
            ax.annotate("", xy=(ax_x, 4.4 + off), xytext=(1.0, 4.0 + off), zorder=9,
                        arrowprops=dict(arrowstyle="-|>", color=RED, lw=3.5, mutation_scale=30))
        label(ax, 1.0, 5.2, "Cặp A-4 thứ hai", 24, RED)
        # Sea Wolf line of fire from Broadsword to the attackers
        if t > 1.5:
            col = AMBER
            blocked = k_turn > 0.85
            ax.plot([bx, ax_x], [by, 4.6 + (bx - ax_x) * 0.0], color=RED if blocked else col, lw=3, alpha=0.9, zorder=6)
            ax.add_patch(matplotlib.patches.Wedge((bx, by), 7.0, 150, 175, color=col, alpha=0.08, zorder=4))
            label(ax, 0.03, 0.88, "Đường bắn của Sea Wolf", 30, AMBER, transform=ax.transAxes)
            if blocked and int(t * 3) % 2 == 0:
                label(ax, 0.55, 0.30, "BỊ CHẮN — KHÔNG THỂ BẮN", 38, RED, transform=ax.transAxes)
        label(ax, 0.03, 0.05, "Sơ đồ minh họa (không theo tỷ lệ)", 20, "#9a9484", weight="normal", transform=ax.transAxes)
        return fig
    encode(out, fr, int(dur * FPS))


def end(out, dur):
    m = Map(polys_in(-62, -56, -53, -50), 1 / math.cos(math.radians(51.5)))

    def fr(t):
        fig, ax = m.fig(-58.3, -52.0, 3.6, grid=(0.5, 0.25))
        ax.plot(*STANLEY, "o", color=AMBER, ms=12, zorder=9)
        label(ax, STANLEY[0] + 0.05, STANLEY[1] + 0.05, "Stanley", 26, AMBER)
        ax.plot(*SHIP, "x", color=RED, ms=16, mew=4, zorder=9)
        label(ax, SHIP[0] + 0.06, SHIP[1] + 0.05, "HMS Coventry", 20, RED)
        stats = [("74 ngày", "chiến tranh"), ("649", "quân nhân Argentina thiệt mạng"),
                 ("255", "quân nhân Anh thiệt mạng"), ("3", "người dân trên đảo thiệt mạng")]
        ax.add_patch(matplotlib.patches.FancyBboxPatch((0.63, 0.04), 0.35, 0.52, boxstyle="round,pad=0.01",
                     transform=ax.transAxes, color="#0b141a", alpha=0.85 * ease((t - 1.6) / 0.6), zorder=9))
        for j, (big, small) in enumerate(stats):
            a = ease((t - 2.0 - j * 1.4) / 0.8)
            if a > 0:
                label(ax, 0.66, 0.46 - j * 0.115, big, 40, AMBER, transform=ax.transAxes, alpha=a)
                label(ax, 0.66, 0.425 - j * 0.115, small, 22, WHITE, weight="normal", transform=ax.transAxes, alpha=a)
        return fig
    encode(out, fr, int(dur * FPS))


def render(kind, dur, out):
    {"atlantic": atlantic, "region": region, "sancarlos": sancarlos, "picket": picket, "attack": attack,
     "geometry": geometry, "end": end}[kind](out, dur)


if __name__ == "__main__":
    render(sys.argv[1], float(sys.argv[2]), sys.argv[3])
