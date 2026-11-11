"""Dramatic YouTube thumbnails (1280x720): big faces, neon counters, rim light, rays."""
import math
import sys
import cairo
from PIL import Image, ImageFilter, ImageEnhance
from engine import draw_char, font, text_w, setc, poly, circle, ellipse, line
from scenes import kitchen
from scenes2 import park, bench, pigeons
from story_full import ME, GMA, WALTER

SC = 2
W, H = 1280 * SC, 720 * SC


def to_pil(s):
    s.flush()
    return Image.frombuffer("RGBA", (W, H), bytes(s.get_data()), "raw", "BGRa", 0, 1)


def px_layer(draw):
    """Layer drawn in 1280x720 thumbnail pixel coordinates."""
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    c.scale(SC, SC)
    draw(c)
    return to_pil(s)


def world_layer(draw, z, fx, fy):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    c.translate(W / 2, H / 2)
    c.scale(z * SC * 1280 / 1920, z * SC * 1280 / 1920)
    c.translate(-fx, -fy)
    draw(c)
    return to_pil(s)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def colored_from_alpha(img, color, blur, gain=1.0):
    a = img.split()[3].filter(ImageFilter.GaussianBlur(blur * SC)).point(lambda v: min(255, int(v * gain)))
    out = Image.new("RGBA", img.size, hexrgb(color) + (0,))
    out.putalpha(a)
    return out


def outline(img, px=6, color=(18, 14, 22)):
    a = img.split()[3].filter(ImageFilter.MaxFilter(px * SC * 2 + 1))
    base = Image.new("RGBA", img.size, color + (0,))
    base.putalpha(a)
    base.alpha_composite(img)
    return base


def neon(text, size, color, cx, cy, rot=0.0):
    def d(c):
        c.translate(cx, cy)
        c.rotate(rot)
        font(c, size)
        tw = text_w(c, text)
        c.move_to(-tw / 2, 0)
        c.text_path(text)
        c.set_line_width(size * 0.17)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        setc(c, color)
        c.stroke_preserve()
        setc(c, "#ffffff")
        c.fill()
        ty = size * 0.22
        poly(c, [(-22, ty), (22, ty), (0, ty + 30)], color)
    core = px_layer(d)
    glow = Image.alpha_composite(colored_from_alpha(core, color, 34, 1.2), colored_from_alpha(core, color, 12, 1.6))
    return Image.alpha_composite(glow, core)


def rays(cx, cy, color, n=18, alpha=0.22, r=1400):
    def d(c):
        for i in range(n):
            a0 = i * 2 * math.pi / n
            a1 = a0 + math.pi / n
            c.move_to(cx, cy)
            c.line_to(cx + r * math.cos(a0), cy + r * math.sin(a0))
            c.line_to(cx + r * math.cos(a1), cy + r * math.sin(a1))
            c.close_path()
        g = cairo.RadialGradient(cx, cy, 20, cx, cy, r * 0.7)
        rr, gg, bb = [v / 255 for v in hexrgb(color)]
        g.add_color_stop_rgba(0, rr, gg, bb, alpha)
        g.add_color_stop_rgba(1, rr, gg, bb, 0)
        c.set_source(g)
        c.fill()
        g = cairo.RadialGradient(cx, cy, 10, cx, cy, 420)
        g.add_color_stop_rgba(0, rr, gg, bb, 0.55)
        g.add_color_stop_rgba(1, rr, gg, bb, 0)
        c.rectangle(0, 0, 1280, 720)
        c.set_source(g)
        c.fill()
    return px_layer(d)


def vignette(strength=0.8):
    def d(c):
        g = cairo.RadialGradient(640, 360, 250, 640, 360, 820)
        g.add_color_stop_rgba(0, 0, 0, 0, 0)
        g.add_color_stop_rgba(1, 0, 0, 0, strength)
        c.rectangle(0, 0, 1280, 720)
        c.set_source(g)
        c.fill()
    return px_layer(d)


def sweat_and_shock(c, hx, hy, r):
    # sweat drop
    x, y = hx + r * 0.95, hy - r * 0.45
    c.move_to(x, y - 46)
    c.curve_to(x + 30, y, x + 22, y + 34, x, y + 34)
    c.curve_to(x - 22, y + 34, x - 30, y, x, y - 46)
    setc(c, "#7fd3ff")
    c.fill_preserve()
    c.set_line_width(5)
    setc(c, "#0e2a3d")
    c.stroke()
    ellipse(c, x - 6, y + 10, 6, 10, (1, 1, 1, 0.8))
    # shock lines
    for a in (-2.5, -2.15, -1.8):
        x0, y0 = hx + (r + 25) * math.cos(a), hy + (r + 25) * math.sin(a)
        x1, y1 = hx + (r + 75) * math.cos(a), hy + (r + 75) * math.sin(a)
        line(c, [(x0, y0), (x1, y1)], 12, "#ffffff")


def crossed_fingers(c, x, y, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    skin = "#efc6a6"
    line(c, [(0, 40), (0, -10)], 30, skin)
    line(c, [(-6, 0), (14, -62)], 15, skin)
    line(c, [(10, 0), (-12, -60)], 15, skin)
    circle(c, 0, 18, 30, skin)
    c.restore()


def grade(img, tint, a, bright=1.0, sat=1.25, contrast=1.15):
    img = ImageEnhance.Brightness(img).enhance(bright)
    t = Image.new("RGBA", img.size, tint + (int(255 * a),))
    img = Image.alpha_composite(img, t)
    return ImageEnhance.Contrast(ImageEnhance.Color(img).enhance(sat)).enhance(contrast)


# ------------------------------------------------------------------ A: sly grandma
def thumb_grandma(path):
    bg = world_layer(lambda c: kitchen(c, 2.0, evening=True), 1.3, 1100, 420)
    bg = grade(bg.filter(ImageFilter.GaussianBlur(9 * SC)), (40, 10, 30), 0.35, bright=0.55)
    img = Image.alpha_composite(bg, rays(900, 330, "#ff2e63", alpha=0.28))

    gx, gy, gs = 900, 915, 0.95
    gma = px_layer(lambda c: draw_char(c, GMA, gx, gy, gs, 0.2, expr="sly", look=-1, flip=True, pose="down"))
    fingers = px_layer(lambda c: crossed_fingers(c, gx + 135, 660, 1.3))
    img = Image.alpha_composite(img, colored_from_alpha(gma, "#ff2e63", 14, 2.2))   # red rim light
    img = Image.alpha_composite(img, outline(fingers, 4))
    img = Image.alpha_composite(img, outline(gma, 5))
    img = Image.alpha_composite(img, colored_from_alpha(fingers, "#ffd166", 10, 1.4))
    img = Image.alpha_composite(img, outline(fingers, 4))

    mx, my, ms = 245, 1110, 1.45
    me = px_layer(lambda c: (draw_char(c, ME, mx, my, ms, 0.1, expr="shock", pose="shrug", look=1),
                             sweat_and_shock(c, mx, my - 610 * ms, 118 * ms)))
    img = Image.alpha_composite(img, vignette(0.75))
    img = Image.alpha_composite(img, outline(me, 6))
    img = Image.alpha_composite(img, neon("96,440", 168, "#ff2e63", 905, 205, rot=-0.06))
    img.convert("RGB").resize((1280, 720), Image.LANCZOS).save(path, quality=95)


# ------------------------------------------------------------------ B: lonely zero
def thumb_zero(path):
    bg = world_layer(lambda c: (park(c, 0), bench(c, 1520)), 1.25, 1250, 520)
    bg = grade(bg.filter(ImageFilter.GaussianBlur(8 * SC)), (10, 25, 60), 0.45, bright=0.5)
    img = Image.alpha_composite(bg, rays(905, 360, "#ff2e63", alpha=0.2))

    wx, wy, ws = 905, 930, 0.95
    walter = px_layer(lambda c: (draw_char(c, WALTER, wx, wy, ws, 0.3, expr="sad", look=-0.8, flip=True),
                                 pigeons(c, wx + 40, 0.4)))
    img = Image.alpha_composite(img, colored_from_alpha(walter, "#ff2e63", 14, 2.0))
    img = Image.alpha_composite(img, outline(walter, 5))

    mx, my, ms = 245, 1110, 1.45
    me = px_layer(lambda c: (draw_char(c, ME, mx, my, ms, 0.1, expr="shock", pose="shrug", look=1),
                             sweat_and_shock(c, mx, my - 610 * ms, 118 * ms)))
    img = Image.alpha_composite(img, vignette(0.8))
    img = Image.alpha_composite(img, outline(me, 6))
    img = Image.alpha_composite(img, neon("0", 250, "#ff2e63", 905, 250, rot=-0.05))
    img.convert("RGB").resize((1280, 720), Image.LANCZOS).save(path, quality=95)


if __name__ == "__main__":
    out = sys.argv[1]
    thumb_grandma(f"{out}/thumb-A-grandma.jpg")
    thumb_zero(f"{out}/thumb-B-zero.jpg")
