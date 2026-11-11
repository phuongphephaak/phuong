import sys, cairo, importlib, production as p
s = importlib.import_module(sys.argv[4] if len(sys.argv) > 4 else "story_full")
from engine import W, H
p.prepare(s.BEATS)
vig = p.vignette()
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
out = sys.argv[1]
idx = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 and sys.argv[2] != "all" else range(len(s.BEATS))
fr = float(sys.argv[3]) if len(sys.argv) > 3 else 0.6
for i in idx:
    b = s.BEATS[i]
    p.render_frame(surf, b, b.dur * fr, vig)
    surf.write_to_png(f"{out}/b{i:02d}.png")
