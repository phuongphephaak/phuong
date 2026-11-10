"""5-second walk-cycle test: tracking camera, passers-by, cane walk, run."""
import math
import subprocess
import sys
import cairo
from engine import W, H, draw_char, counter_label
from scenes import GROUND, street
from story import ME, FRIEND, GRANDMA, SALES, COWORKER

FPS, DUR = 30, 6.0


def frame(ctx, t):
    mx = 300 + 260 * t                       # protagonist walks right
    fx = min(max(mx, 960), 1900)             # camera tracks
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.translate(-fx, -540)
    street(ctx, t, 0)
    # background passers-by (smaller, walking left)
    draw_char(ctx, SALES, 2600 - 200 * t, GROUND - 40, 0.6, t, walk=t * 7.0, flip=True)
    draw_char(ctx, GRANDMA, 1500 - 70 * t, GROUND - 30, 0.62, t, pose="cane", walk=t * 3.5, stride=0.45, flip=True)
    # protagonist
    draw_char(ctx, ME, mx, GROUND, 0.82, t, expr="happy", walk=t * 7.0, look=1)
    counter_label(ctx, mx, GROUND - 700 * 0.82, 4813)
    # friend jogging past in foreground
    draw_char(ctx, FRIEND, -200 + 600 * t, GROUND + 90, 0.95, t, expr="happy", walk=t * 13.0, stride=1.4,
              lean=0.12)
    ctx.restore()


out = sys.argv[1]
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                       "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", out],
                      stdin=subprocess.PIPE)
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
for f in range(int(DUR * FPS)):
    frame(cairo.Context(surf), f / FPS)
    surf.flush()
    ff.stdin.write(bytes(surf.get_data()))
ff.stdin.close()
ff.wait()
