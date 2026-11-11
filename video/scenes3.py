"""Backgrounds and props for episode 2."""
import math
import cairo
from engine import (W, H, rect, fill_rrect, ellipse, circle, line, poly, setc, shade, font, text_w, rrect,
                    draw_char)
from scenes import GROUND, haze, window, street


def _wall(ctx, wall, floor):
    rect(ctx, -800, -400, W + 1600, GROUND + 400, wall)
    for x in range(-800, W + 800, 90):
        rect(ctx, x, -400, 40, GROUND + 400, (1, 1, 1, 0.06))
    rect(ctx, -800, GROUND - 6, W + 1600, H - GROUND + 410, floor)


def bedroom(ctx, t=0, night=False):
    _wall(ctx, "#b9c9d9" if not night else "#3a4560", "#8d6b50" if not night else "#4a3b40")
    window(ctx, 1250, 170, 380, 320, glass="#cfe6f2" if not night else "#1e2a48")
    if night:
        circle(ctx, 1520, 250, 40, "#f4efd8")
        g = cairo.RadialGradient(1440, 330, 20, 1440, 500, 900)
        g.add_color_stop_rgba(0, 0.75, 0.82, 1, 0.28)
        g.add_color_stop_rgba(1, 0.75, 0.82, 1, 0)
        ctx.rectangle(-800, -400, W + 1600, H + 800)
        ctx.set_source(g)
        ctx.fill()
    for i, c in enumerate(["#e76f51", "#2a9d8f", "#e9c46a"]):
        fill_rrect(ctx, 200 + i * 130, 260, 100, 140, 6, c)
    # nightstand
    fill_rrect(ctx, 1700, GROUND - 260, 220, 260, 12, "#7a5a40")
    rect(ctx, 1715, GROUND - 200, 190, 6, "#6a4c3a")
    haze(ctx, a=0.08)


def bed(ctx, x=500, w=1100, night=False):
    """Bed (draw before a lying character) with pillow."""
    fill_rrect(ctx, x - 40, GROUND - 520, 60, 520, 14, "#6a4c3a")
    fill_rrect(ctx, x, GROUND - 300, w, 180, 24, "#f4f1ea")
    rect(ctx, x + 20, GROUND - 120, 30, 120, "#6a4c3a")
    rect(ctx, x + w - 50, GROUND - 120, 30, 120, "#6a4c3a")
    fill_rrect(ctx, x + 20, GROUND - 360, 260, 90, 40, "#ffffff")


def blanket(ctx, x=500, w=1100, night=False):
    col = "#4f7cac" if not night else "#3b5578"
    ctx.move_to(x + 230, GROUND - 330)
    ctx.curve_to(x + 500, GROUND - 390, x + 900, GROUND - 380, x + w, GROUND - 330)
    ctx.line_to(x + w, GROUND - 200)
    ctx.line_to(x + 230, GROUND - 200)
    ctx.close_path()
    setc(ctx, col)
    ctx.fill()
    for i in range(5):
        line(ctx, [(x + 300 + i * 160, GROUND - 360), (x + 300 + i * 160, GROUND - 205)], 3, shade(col, 0.85))


def lying_char(ctx, c, x, y, s, t, expr="neutral"):
    """Character lying on a bed, head at (x, y)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-math.pi / 2)
    draw_char(ctx, c, 0, 0 + 560 * s, s, t, expr=expr, look=0)
    ctx.restore()


def jay_room(ctx, t=0):
    _wall(ctx, "#cdd8c0", "#8d6b50")
    window(ctx, 200, 200, 360, 300, glass="#cfe6f2")
    fill_rrect(ctx, 760, 210, 300, 200, 8, "#2c2f36")
    font(ctx, 46)
    ctx.move_to(800, 330)
    setc(ctx, "#e9c46a")
    ctx.show_text("GAME ON")
    fill_rrect(ctx, 1150, GROUND - 330, 620, 40, 8, "#a07a5c")
    rect(ctx, 1170, GROUND - 290, 30, 290, "#7a5a40")
    rect(ctx, 1720, GROUND - 290, 30, 290, "#7a5a40")
    haze(ctx, a=0.08)


def front_yard(ctx, t=0, variant=0):
    street(ctx, t, variant)
    for x in range(-800, W + 800, 60):
        rect(ctx, x, GROUND - 160, 26, 160, "#f4f1ea")
        poly(ctx, [(x, GROUND - 160), (x + 13, GROUND - 185), (x + 26, GROUND - 160)], "#f4f1ea")
    rect(ctx, -800, GROUND - 120, W + 1600, 18, "#f4f1ea")
    rect(ctx, -800, GROUND - 60, W + 1600, 16, "#f4f1ea")
    # gate gap
    rect(ctx, 880, GROUND - 190, 180, 190, (0, 0, 0, 0))


def porch(ctx, t=0):
    g = cairo.LinearGradient(0, 0, 0, GROUND)
    g.add_color_stop_rgb(0, 0.98, 0.84, 0.6)
    g.add_color_stop_rgb(1, 0.95, 0.75, 0.55)
    ctx.rectangle(-800, -400, W + 1600, GROUND + 400)
    ctx.set_source(g)
    ctx.fill()
    rect(ctx, -800, 120, 1500, GROUND, "#c9a27a")
    for y in range(140, GROUND, 40):
        rect(ctx, -800, y, 1500, 4, "#b48b62")
    window(ctx, 100, 280, 300, 260, glass="#f2d9a0")
    fill_rrect(ctx, 480, 360, 160, GROUND - 360, 6, "#7a5a40")
    rect(ctx, -800, 80, 1600, 50, "#8a5a3a")
    for x in (-300, 300, 680):
        rect(ctx, x, 120, 26, GROUND - 120, "#f4f1ea")
    for i in range(-1, 6):
        circle(ctx, 1000 + i * 260, 520, 170, ["#7fb069", "#6a9f58"][i % 2])
    haze(ctx, (1, 0.9, 0.7), 0.15)
    rect(ctx, -800, GROUND - 6, W + 1600, H - GROUND + 410, "#9cc47a")
    rect(ctx, -800, GROUND - 6, 1500, 60, "#a8865f")


def porch_bench(ctx, x):
    fill_rrect(ctx, x - 220, GROUND - 300, 440, 26, 8, "#7a5a40")
    fill_rrect(ctx, x - 230, GROUND - 180, 460, 30, 8, "#8a6a52")
    rect(ctx, x - 210, GROUND - 150, 18, 150, "#5a4636")
    rect(ctx, x + 192, GROUND - 150, 18, 150, "#5a4636")


def vet(ctx, t=0):
    _wall(ctx, "#e3eef0", "#b8c4c0")
    fill_rrect(ctx, 1300, 160, 420, 120, 14, "#2a9d8f")
    font(ctx, 52)
    ctx.move_to(1350, 240)
    setc(ctx, "#ffffff")
    ctx.show_text("PAWS VET")
    poly(ctx, [(1660, 190), (1690, 220), (1660, 250)], "#ffffff")
    fill_rrect(ctx, 600, GROUND - 300, 700, 40, 10, "#c9d6dc")
    rect(ctx, 620, GROUND - 260, 660, 260, "#aebec5")
    for i in range(3):
        fill_rrect(ctx, 200 + i * 120, 300, 90, 120, 10, ["#e9c46a", "#e76f51", "#7fb3d5"][i])
    haze(ctx, a=0.08)


def flyer(ctx, t, b):
    """Screen overlay: neighborhood flyer."""
    a = min(1, t / 0.3)
    ctx.save()
    ctx.translate(1450, 330)
    ctx.rotate(0.05)
    fill_rrect(ctx, -230, -170, 460, 300, 10, (1, 0.98, 0.9, a))
    font(ctx, 46)
    for i, tx in enumerate(["PET PROBLEMS?", "ASK ME!"]):
        ctx.move_to(-text_w(ctx, tx) / 2, -80 + i * 70)
        setc(ctx, "#b23a30" if i == 0 else "#1f4fa3", a)
        ctx.show_text(tx)
    font(ctx, 28, weight="normal")
    tx = "Dogs · Cats · Parrots · Fish"
    ctx.move_to(-text_w(ctx, tx) / 2, 90)
    setc(ctx, "#2a2522", a)
    ctx.show_text(tx)
    ctx.restore()
