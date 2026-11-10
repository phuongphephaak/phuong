"""Render the shot list to video frames (piped into ffmpeg) or preview PNGs."""
import subprocess
import sys
import cairo
from engine import W, H
from story import SHOTS

FPS = 30


def vignette():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, W * 0.72)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.38)
    c.set_source(g)
    c.paint()
    return s


VIG = vignette()


def frame(surface, shot, t):
    ctx = cairo.Context(surface)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    cam = shot.camera(t)
    fx, fy, z = cam
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-fx, -fy)
    shot.world(ctx, t)
    ctx.restore()
    ctx.set_source_surface(VIG)
    ctx.paint()
    if shot.screen:
        shot.screen(ctx, t, cam)


def timeline():
    out, t0 = [], 0.0
    for sh in SHOTS:
        out.append((t0, sh))
        t0 += sh.dur
    return out, t0


def preview(dirname, at=0.75):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    for i, sh in enumerate(SHOTS):
        frame(surf, sh, sh.dur * at)
        surf.write_to_png(f"{dirname}/shot{i + 1:02d}.png")


def render(path):
    tl, total = timeline()
    n = int(round(total * FPS))
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                           "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", path],
                          stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    k = 0
    for f in range(n):
        t = f / FPS
        while k + 1 < len(tl) and t >= tl[k + 1][0]:
            k += 1
        t0, sh = tl[k]
        frame(surf, sh, t - t0)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
        if f % 300 == 0:
            print(f"frame {f}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()


if __name__ == "__main__":
    if sys.argv[1] == "preview":
        preview(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.75)
    else:
        render(sys.argv[2])
