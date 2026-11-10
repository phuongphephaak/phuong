"""Channel branding for WhatIfBean: profile logo (800x800) and banner (2560x1440)."""
import math
import sys
import cairo
from engine import draw_char, font, text_w, setc, fill_rrect, poly, circle, ellipse, counter_label
from story_full import ME, MIA, GMA, JAY, WALTER, MOM, DAD

NAVY_TOP, NAVY_BOT = (0.09, 0.1, 0.16), (0.17, 0.18, 0.27)
ORANGE, CORAL = "#e8833a", "#ff6b5e"


def bg(ctx, w, h):
    g = cairo.LinearGradient(0, 0, 0, h)
    g.add_color_stop_rgb(0, *NAVY_TOP)
    g.add_color_stop_rgb(1, *NAVY_BOT)
    ctx.rectangle(0, 0, w, h)
    ctx.set_source(g)
    ctx.fill()
    for i in range(int(w * h / 22000)):
        x = (i * 397.3) % w
        y = (i * 263.7 + (i % 7) * 91) % h
        circle(ctx, x, y, 1.5 + i % 3, (1, 1, 1, 0.05 + 0.03 * (i % 3)))


def q_label(ctx, x, y, s=1.0, text="?"):
    """Counter-style pill with a question mark (brand mark)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    font(ctx, 64)
    tw = text_w(ctx, text)
    w, h = max(tw + 70, 120), 96
    fill_rrect(ctx, -w / 2, -h - 22, w, h, 26, CORAL)
    poly(ctx, [(-20, -24), (20, -24), (0, 0)], CORAL)
    ctx.move_to(-tw / 2, -h / 2 - 22 + 23)
    setc(ctx, "#ffffff")
    ctx.show_text(text)
    ctx.restore()


def wordmark(ctx, cx, y, size):
    parts = [("WhatIf", "#ffffff"), ("Bean", ORANGE)]
    font(ctx, size)
    total = sum(text_w(ctx, p) for p, _ in parts)
    x = cx - total / 2
    for p, col in parts:
        ctx.move_to(x, y)
        ctx.text_path(p)
        ctx.set_line_width(size * 0.12)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        setc(ctx, "#0e0f12")
        ctx.stroke_preserve()
        setc(ctx, col)
        ctx.fill()
        x += text_w(ctx, p)


def logo(path):
    S = 800
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
    ctx = cairo.Context(surf)
    bg(ctx, S, S)
    # orange disc behind the character (stays inside YouTube's circular crop)
    g = cairo.RadialGradient(400, 430, 50, 400, 430, 340)
    g.add_color_stop_rgba(0, 0.98, 0.62, 0.3, 1)
    g.add_color_stop_rgba(1, 0.91, 0.51, 0.23, 1)
    ctx.arc(400, 430, 300, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.save()
    ctx.arc(400, 430, 300, 0, 2 * math.pi)
    ctx.clip()
    draw_char(ctx, ME, 400, 1010, 1.05, 0.5, expr="happy", look=0.3)
    ctx.restore()
    q_label(ctx, 400, 268, 1.2)
    surf.write_to_png(path)


def banner(path):
    Wb, Hb = 2560, 1440
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, Wb, Hb)
    ctx = cairo.Context(surf)
    bg(ctx, Wb, Hb)
    # warm glow in the middle band (TV-safe area is the centre 1546x423)
    g = cairo.RadialGradient(1280, 720, 50, 1280, 720, 900)
    g.add_color_stop_rgba(0, 0.95, 0.55, 0.25, 0.35)
    g.add_color_stop_rgba(1, 0.95, 0.55, 0.25, 0)
    ctx.rectangle(0, 0, Wb, Hb)
    ctx.set_source(g)
    ctx.fill()
    # cast on both sides of the wordmark, inside the 423px band visible on desktop/mobile
    cast = [(GMA, 96440, 240), (MOM, 9998, 460), (MIA, 2303, 680),
            (JAY, 712, 1880), (DAD, 11400, 2100), (WALTER, 0, 2320)]
    s = 0.4
    ground = 935
    for k, (c, v, x) in enumerate(cast):
        draw_char(ctx, c, x, ground, s, k * 0.7, expr="happy", look=0.6 if x < 1280 else -0.6, flip=x > 1280)
        counter_label(ctx, x, ground - 700 * s, v, s=0.72)
    # wordmark + tagline inside the safe area
    wordmark(ctx, 1280, 700, 140)
    font(ctx, 42, weight="normal")
    tag = "Animated stories about strange superpowers"
    ctx.move_to(1280 - text_w(ctx, tag) / 2, 775)
    setc(ctx, (1, 1, 1, 0.85))
    ctx.show_text(tag)
    surf.write_to_png(path)


def guide(path, src):
    """Preview with YouTube crop guides (not for upload)."""
    img = cairo.ImageSurface.create_from_png(src)
    ctx = cairo.Context(img)
    for (w, h, col) in ((1546, 423, (0.2, 1, 0.4)), (2560, 423, (1, 1, 0.2)), (1855, 423, (0.3, 0.7, 1))):
        ctx.rectangle(1280 - w / 2, 720 - h / 2, w, h)
        ctx.set_source_rgba(*col, 0.9)
        ctx.set_line_width(4)
        ctx.stroke()
    img.write_to_png(path)


if __name__ == "__main__":
    out = sys.argv[1]
    logo(f"{out}/whatifbean-logo-800.png")
    banner(f"{out}/whatifbean-banner-2560x1440.png")
    guide(f"{out}/_banner-guides.png", f"{out}/whatifbean-banner-2560x1440.png")
