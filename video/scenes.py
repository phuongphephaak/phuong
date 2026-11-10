"""Backgrounds for the lie-counter story."""
import math
import cairo
from engine import (W, H, rect, fill_rrect, ellipse, circle, line, poly, setc, shade, font,
                    text_w, rrect)

GROUND = 930


def haze(ctx, c=(0.95, 0.9, 0.82), a=0.16):
    ctx.rectangle(-800, -400, W + 1600, H + 800)
    ctx.set_source_rgba(c[0], c[1], c[2], a)
    ctx.fill()


def window(ctx, x, y, w, h, glass="#6f8593", frame="#e9e0d0", lit=False):
    fill_rrect(ctx, x - 8, y - 8, w + 16, h + 16, 4, frame)
    rect(ctx, x, y, w, h, "#f0d79a" if lit else glass)
    poly(ctx, [(x, y + h), (x + w * 0.55, y), (x + w * 0.75, y), (x + w * 0.2, y + h)], (1, 1, 1, 0.12))
    line(ctx, [(x + w / 2, y), (x + w / 2, y + h)], 6, frame, cap=cairo.LINE_CAP_BUTT)


def awning(ctx, x, y, w, c1="#3f7f8c", c2="#efe6d6", n=8):
    sw = w / n
    for i in range(n):
        rect(ctx, x + i * sw, y, sw, 70, c1 if i % 2 == 0 else c2)
        ctx.arc(x + i * sw + sw / 2, y + 70, sw / 2, 0, math.pi)
        setc(ctx, c1 if i % 2 == 0 else c2)
        ctx.fill()
    rect(ctx, x - 10, y - 14, w + 20, 18, shade(c1, 0.7))


def shop(ctx, x, w, name, wall, awn):
    rect(ctx, x, 300, w, GROUND - 300, wall)
    fill_rrect(ctx, x + 40, 330, w - 80, 70, 10, "#2c2f36")
    font(ctx, 40)
    tw = text_w(ctx, name)
    ctx.move_to(x + w / 2 - tw / 2, 380)
    setc(ctx, "#f3e9d6")
    ctx.show_text(name)
    awning(ctx, x + 20, 430, w - 40, awn)
    rect(ctx, x + 50, 540, w - 100, GROUND - 600, "#f2d9a0")
    for i in range(4):
        fill_rrect(ctx, x + 80 + i * (w - 160) / 4, 640, (w - 200) / 4, 30, 6, shade("#c98b55", 1.0 + i * 0.05))
    rect(ctx, x + 50, GROUND - 60, w - 100, 60, shade(wall, 0.8))
    poly(ctx, [(x + 50, GROUND - 60), (x + 50 + (w - 100) * 0.5, 540), (x + 50 + (w - 100) * 0.62, 540),
               (x + 50 + (w - 100) * 0.12, GROUND - 60)], (1, 1, 1, 0.14))


def street(ctx, t=0, variant=0):
    g = cairo.LinearGradient(0, 0, 0, GROUND)
    g.add_color_stop_rgb(0, 0.93, 0.86, 0.75)
    g.add_color_stop_rgb(1, 0.86, 0.78, 0.66)
    ctx.rectangle(-800, -400, W + 1600, GROUND + 400)
    ctx.set_source(g)
    ctx.fill()
    cols = ["#b4876b", "#8fa3a6", "#c9b18f", "#a07a6a", "#93a08a"]
    xs = list(range(-800, W + 800, 520))
    for i, x in enumerate(xs):
        c = cols[(i + variant) % len(cols)]
        top = 40 + ((i * 97 + variant * 53) % 160)
        rect(ctx, x, top - 400, 520, GROUND - top + 400, c)
        rect(ctx, x, top - 30, 520, 30, shade(c, 0.8))
        for r in range(2):
            for k in range(3):
                window(ctx, x + 60 + k * 150, top + 50 + r * 0 - 200 * (1 - r) + 0, 90, 120)
        if (i + variant) % 2 == 0:
            shop(ctx, x + 30, 460, ["CRUMB BAKERY", "PAGE & INK", "BEAN THERE", "FIXIT"][(i + variant) % 4],
                 shade(c, 0.9), ["#3f7f8c", "#b4503e", "#6b8f4e", "#7b5c99"][(i + variant) % 4])
        else:
            window(ctx, x + 80, top + 260, 140, 200)
            window(ctx, x + 300, top + 260, 140, 200)
            fill_rrect(ctx, x + 200, GROUND - 330, 120, 330, 8, shade(c, 0.6))
            circle(ctx, x + 300, GROUND - 170, 7, "#e9c46a")
    haze(ctx)
    # sidewalk
    rect(ctx, -800, GROUND - 10, W + 1600, H - GROUND + 410, "#a39686")
    rect(ctx, -800, GROUND - 14, W + 1600, 10, "#8a7d6e")
    for x in range(-800, W + 800, 170):
        line(ctx, [(x, GROUND), (x - 60, H + 400)], 3, "#8f8273", cap=cairo.LINE_CAP_BUTT)
    # props
    for lx in (-300, 1350 if variant % 2 == 0 else 600, 2400):
        rect(ctx, lx - 9, 330, 18, GROUND - 330, "#3b3f45")
        fill_rrect(ctx, lx - 34, 290, 68, 60, 14, "#3b3f45")
        ellipse(ctx, lx, 340, 26, 14, "#f6dfa0")
    fill_rrect(ctx, 1600 if variant != 1 else 250, GROUND - 120, 80, 120, 10, "#4f7a5a")


def kitchen(ctx, t=0, evening=False):
    rect(ctx, -800, -400, W + 1600, GROUND + 400, "#e8d9c0" if not evening else "#c7b49a")
    for x in range(-800, W + 800, 90):
        rect(ctx, x, -400, 40, GROUND + 400, (1, 1, 1, 0.08))
    # window
    window(ctx, 760, 220, 400, 300, glass="#bcd6e0" if not evening else "#40516e")
    fill_rrect(ctx, 920, 440, 80, 80, 12, "#b5654a")
    for a in (-0.6, -0.2, 0.2, 0.6):
        ellipse(ctx, 960 + 50 * math.sin(a), 420 - 40 * math.cos(a), 18, 42, "#5f8f5a", rot=a)
    # cabinets
    for i in range(3):
        fill_rrect(ctx, 80 + i * 200, 140, 180, 280, 10, "#8fae9b")
        line(ctx, [(160 + i * 200, 380), (200 + i * 200, 380)], 8, "#e9e0d0")
    rect(ctx, 0, 560, 700, 60, "#d8cfc2")
    rect(ctx, 0, 620, 700, GROUND - 620, "#8fae9b")
    for i in range(3):
        rrect(ctx, 30 + i * 220, 650, 200, GROUND - 690, 8)
        setc(ctx, shade("#8fae9b", 0.9))
        ctx.set_line_width(4)
        ctx.stroke()
    # fridge
    fill_rrect(ctx, 1500, 200, 300, GROUND - 200, 30, "#eef0ee")
    line(ctx, [(1500, 480), (1800, 480)], 5, "#c9cdcc")
    line(ctx, [(1530, 320), (1530, 420)], 10, "#b7bcbb")
    for i, c in enumerate(["#e76f51", "#2a9d8f", "#e9c46a"]):
        fill_rrect(ctx, 1580 + i * 60, 540 + (i % 2) * 40, 40, 40, 6, c)
    # clock
    circle(ctx, 1300, 180, 60, "#fbf7ef")
    ctx.arc(1300, 180, 60, 0, 2 * math.pi)
    ctx.set_line_width(8)
    setc(ctx, "#5a4a3f")
    ctx.stroke()
    line(ctx, [(1300, 180), (1300 + 36 * math.sin(t * 0.3), 180 - 36 * math.cos(t * 0.3))], 6, "#5a4a3f")
    line(ctx, [(1300, 180), (1325, 190)], 7, "#5a4a3f")
    # lamp
    line(ctx, [(1000, -400), (1000, 80)], 4, "#3b3f45")
    poly(ctx, [(940, 130), (1060, 130), (1030, 80), (970, 80)], "#e07a4f")
    if evening:
        g = cairo.RadialGradient(1000, 140, 10, 1000, 140, 700)
        g.add_color_stop_rgba(0, 1, 0.85, 0.55, 0.35)
        g.add_color_stop_rgba(1, 1, 0.85, 0.55, 0)
        ctx.rectangle(-800, -400, W + 1600, H + 800)
        ctx.set_source(g)
        ctx.fill()
    haze(ctx, a=0.12)
    rect(ctx, -800, GROUND - 6, W + 1600, H - GROUND + 410, "#b88f6a")
    for x in range(-800, W + 800, 160):
        line(ctx, [(x, GROUND), (x, H + 400)], 3, "#a57d5a", cap=cairo.LINE_CAP_BUTT)


def living(ctx, t=0, evening=True):
    rect(ctx, -800, -400, W + 1600, GROUND + 400, "#c9b6a0" if not evening else "#a99682")
    rect(ctx, -800, 640, W + 1600, 14, "#8d7a66")
    window(ctx, 1380, 200, 360, 340, glass="#e6b27a" if evening else "#bcd6e0")
    for i, (x, y, w, h, c) in enumerate([(300, 220, 180, 140, "#e9c46a"), (520, 260, 120, 160, "#2a9d8f"),
                                         (680, 230, 160, 120, "#e76f51")]):
        fill_rrect(ctx, x - 10, y - 10, w + 20, h + 20, 4, "#5a4636")
        rect(ctx, x, y, w, h, c)
        ellipse(ctx, x + w / 2, y + h * 0.65, w * 0.3, h * 0.2, (1, 1, 1, 0.35))
    # floor lamp
    rect(ctx, 1170, 300, 12, GROUND - 300, "#3b3f45")
    poly(ctx, [(1110, 300), (1240, 300), (1210, 210), (1140, 210)], "#f2e3c2")
    g = cairo.RadialGradient(1176, 300, 10, 1176, 300, 650)
    g.add_color_stop_rgba(0, 1, 0.88, 0.6, 0.45)
    g.add_color_stop_rgba(1, 1, 0.88, 0.6, 0)
    ctx.rectangle(-800, -400, W + 1600, H + 800)
    ctx.set_source(g)
    ctx.fill()
    haze(ctx, a=0.10)
    rect(ctx, -800, GROUND - 6, W + 1600, H - GROUND + 410, "#7d604a")
    ellipse(ctx, 800, GROUND + 70, 700, 60, "#b5654a", a=0.8)


def couch(ctx, x, y, w=760):
    """Drawn in front of characters' legs."""
    fill_rrect(ctx, x, y - 260, w, 170, 50, "#6f6185")
    fill_rrect(ctx, x - 40, y - 170, 120, 170, 40, "#62567a")
    fill_rrect(ctx, x + w - 80, y - 170, 120, 170, 40, "#62567a")
    fill_rrect(ctx, x + 40, y - 150, w - 80, 130, 30, "#7b6c93")
    rect(ctx, x + 20, y - 20, 20, 20, "#3b2f28")
    rect(ctx, x + w - 40, y - 20, 20, 20, "#3b2f28")


def table(ctx, x, y, w=900):
    fill_rrect(ctx, x, y - 250, w, 34, 10, "#8a6a52")
    rect(ctx, x + 14, y - 222, w - 28, 50, "#f1e9dc")
    for i in range(0, int(w) - 28, 48):
        rect(ctx, x + 14 + i, y - 222, 24, 50, "#c9706a", a=0.55)
    rect(ctx, x + 60, y - 172, 24, 172, "#6a4c3a")
    rect(ctx, x + w - 84, y - 172, 24, 172, "#6a4c3a")


def desk_note(ctx, t, lines_shown):
    rect(ctx, -800, -400, W + 1600, H + 800, "#7a5a40")
    for i in range(-10, 40):
        y = i * 38 + 10 * math.sin(i)
        line(ctx, [(-800, y), (W + 800, y + 20)], 2, "#6b4e37", cap=cairo.LINE_CAP_BUTT)
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.rotate(-0.04)
    fill_rrect(ctx, -520 + 12, -400 + 16, 1040, 800, 10, (0, 0, 0, 0.25))
    fill_rrect(ctx, -520, -400, 1040, 800, 10, "#f7f3e8")
    for i in range(12):
        line(ctx, [(-480, -300 + i * 62), (480, -300 + i * 62)], 2, "#b9cfe0", cap=cairo.LINE_CAP_BUTT)
    line(ctx, [(-400, -400), (-400, 400)], 3, "#e8a0a0", cap=cairo.LINE_CAP_BUTT)
    for k in range(6):
        circle(ctx, -470, -320 + k * 130, 14, "#7a5a40")
    for i, (txt, age) in enumerate(lines_shown):
        if age < 0:
            continue
        a = min(1, age / 0.25)
        font(ctx, 60 if i == 0 else 50, italic=(i > 0))
        y = -230 + i * 124
        ctx.move_to(-370, y)
        setc(ctx, "#1f3a6b" if i else "#b23a30", a)
        ctx.show_text(txt)
        if i == 0:
            line(ctx, [(-370, y + 16), (-370 + text_w(ctx, txt) * min(1, age * 2), y + 16)], 6, "#b23a30")
    ctx.restore()
    # pen
    ctx.save()
    ctx.translate(1580, 760)
    ctx.rotate(-0.7)
    fill_rrect(ctx, -20, -250, 40, 420, 18, "#2a4b7c")
    poly(ctx, [(-20, 165), (20, 165), (0, 220)], "#e8d7b8")
    ctx.restore()


def dark_card(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.09, 0.1, 0.13)
    g.add_color_stop_rgb(1, 0.16, 0.17, 0.22)
    ctx.rectangle(-800, -400, W + 1600, H + 800)
    ctx.set_source(g)
    ctx.fill()
    for i in range(40):
        x = (i * 397) % W
        y = (i * 263 + t * 30 * (1 + i % 3)) % H
        circle(ctx, x, H - y, 2 + i % 3, (1, 1, 1, 0.08 + 0.04 * (i % 3)))
