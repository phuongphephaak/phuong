"""Animals for episode 2 (draw functions share the signature used by director.Actor.drawfn)."""
import math
import cairo
from engine import (ellipse, circle, line, poly, rect, fill_rrect, setc, shade, rrect, draw_cat, font, text_w)


def _eye(ctx, x, y, r=9, look=1.0, shock=False):
    if shock:
        circle(ctx, x, y, r * 1.5, "#ffffff")
        circle(ctx, x + look * 2, y, r * 0.55, "#1a1a1a")
    else:
        circle(ctx, x, y, r, "#1a1a1a")
        circle(ctx, x + 2.5, y - 3, r * 0.35, "#ffffff")


def dog(ctx, x, y, s, t, walk=None, facing=1, expr="happy", body="#e0a84a", ear=None, muzzle=None,
        size=1.0, wag=6.0, old=False, lying=False):
    """Side-view dog; head toward +x. Height ~ 330*size at s=1."""
    ear = ear or shade(body, 0.75)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * size * facing, s * size)
    bob = -6 * abs(math.sin(walk)) if walk is not None else 2 * math.sin(t * 3)
    # legs
    for i, lx in enumerate((-95, -60, 60, 95)):
        sw = 0 if walk is None else 26 * math.sin(walk + (0 if i in (0, 3) else math.pi))
        col = body if i % 2 else shade(body, 0.85)
        if lying:
            continue
        line(ctx, [(lx, -110 + bob), (lx + sw, -12)], 30, col)
        ellipse(ctx, lx + sw + 6, -10, 20, 11, shade(body, 0.7))
    ctx.translate(0, bob + (60 if lying else 0))
    # tail
    wa = math.sin(t * wag) * (0.6 if not old else 0.25)
    ctx.save()
    ctx.translate(-120, -160)
    ctx.rotate(-0.9 + wa)
    line(ctx, [(0, 0), (-10, -60), (-5, -100)], 22, body)
    ctx.restore()
    ellipse(ctx, 0, -150, 140, 70, body)
    ellipse(ctx, 20, -125, 95, 38, shade(body, 1.15))
    # head
    hx, hy = 150, -230
    ellipse(ctx, hx - 30, hy + 50, 40, 50, body, rot=0.5)
    circle(ctx, hx, hy, 70, body)
    ellipse(ctx, hx + 62, hy + 22, 48, 34, muzzle or shade(body, 1.2))
    circle(ctx, hx + 104, hy + 10, 14, "#1a1a1a")
    if expr in ("happy", "excited"):
        ctx.move_to(hx + 60, hy + 38)
        ctx.curve_to(hx + 70, hy + 75, hx + 100, hy + 70, hx + 102, hy + 40)
        ctx.close_path()
        setc(ctx, "#3a1a1a")
        ctx.fill()
        ellipse(ctx, hx + 84, hy + 62, 13, 18, "#e8737a")
    else:
        line(ctx, [(hx + 62, hy + 44), (hx + 98, hy + 40)], 6, "#3a1a1a")
    ellipse(ctx, hx - 28, hy - 8, 30, 62, ear, rot=0.35)
    _eye(ctx, hx + 26, hy - 18, 10, shock=(expr == "shock"))
    if expr == "sad" or old:
        line(ctx, [(hx + 12, hy - 42), (hx + 40, hy - 34)], 6, shade(body, 0.6))
    if old:
        ellipse(ctx, hx + 62, hy + 22, 48, 34, "#cfcac2", a=0.55)
    ctx.restore()


def cat_walk(ctx, x, y, s, t, walk=None, facing=1, sit=False, body="#d98b45"):
    if sit or walk is None:
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(facing, 1)
        draw_cat(ctx, 0, 0, s, t)
        ctx.restore()
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * facing, s)
    bob = -4 * abs(math.sin(walk))
    for i, lx in enumerate((-70, -40, 50, 80)):
        sw = 22 * math.sin(walk + (0 if i in (0, 3) else math.pi))
        line(ctx, [(lx, -80 + bob), (lx + sw, -10)], 20, body if i % 2 else shade(body, 0.85))
    ctx.translate(0, bob)
    ctx.move_to(-100, -110)
    ctx.curve_to(-170, -130, -150, -230, -120 + 15 * math.sin(t * 3), -250)
    ctx.set_line_width(20)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    setc(ctx, body)
    ctx.stroke()
    ellipse(ctx, 0, -110, 110, 50, body)
    circle(ctx, 115, -170, 58, body)
    poly(ctx, [(75, -205), (80, -265), (115, -220)], body)
    poly(ctx, [(140, -215), (160, -270), (165, -205)], body)
    ellipse(ctx, 135, -175, 12, 8, "#c9e06a")
    ellipse(ctx, 135, -175, 3, 8, "#2a2522")
    poly(ctx, [(165, -158), (175, -158), (170, -150)], "#e07b7b")
    for i in range(3):
        line(ctx, [(-40 + i * 25, -155), (-35 + i * 25, -135)], 6, shade(body, 0.8))
    ctx.restore()


def fish_tank(ctx, x, y, s, t, **_):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    fill_rrect(ctx, -170, -230, 340, 230, 16, (0.55, 0.8, 0.95, 0.55))
    rect(ctx, -160, -190, 320, 185, (0.3, 0.6, 0.85, 0.5))
    rrect(ctx, -170, -230, 340, 230, 16)
    ctx.set_line_width(6)
    setc(ctx, "#e9f4fa")
    ctx.stroke()
    rect(ctx, -160, -40, 320, 35, "#d9c27a")
    rect(ctx, 40, -120, 70, 80, "#9a8f86")
    for i in range(3):
        rect(ctx, 40 + i * 25, -135, 18, 18, "#9a8f86")
    rect(ctx, 65, -90, 20, 50, "#5a514b")
    for i in range(3):
        line(ctx, [(-120 + i * 18, -10), (-130 + i * 18 + 10 * math.sin(t * 2 + i), -90)], 8, "#5f9f5a")
    fx = -30 + 90 * math.sin(t * 0.8)
    fy = -110 + 15 * math.sin(t * 1.7)
    d = 1 if math.cos(t * 0.8) > 0 else -1
    ctx.save()
    ctx.translate(fx, fy)
    ctx.scale(d, 1)
    poly(ctx, [(-30, 0), (-55, -20), (-55, 20)], "#ff8c2a")
    ellipse(ctx, 0, 0, 38, 24, "#ff9f3a")
    circle(ctx, 18, -5, 6, "#1a1a1a")
    ctx.restore()
    for i in range(3):
        k = (t * 0.7 + i / 3) % 1
        circle(ctx, fx + 30, fy - 20 - k * 130, 5 + 3 * i, (1, 1, 1, 0.6 * (1 - k)))
    ctx.restore()


def hamster_cage(ctx, x, y, s, t, running=True, **_):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rect(ctx, -200, -20, 400, 20, "#3a6fa8")
    for i in range(17):
        line(ctx, [(-190 + i * 24, -20), (-190 + i * 24, -280)], 4, "#c9ced6")
    ctx.arc(0, -280, 200, math.pi, 2 * math.pi)
    ctx.set_line_width(5)
    setc(ctx, "#c9ced6")
    ctx.stroke()
    # wheel
    cx, cy, r = 80, -130, 90
    circle(ctx, cx, cy, r, "#e9c46a")
    circle(ctx, cx, cy, r - 14, "#fff3d0")
    a0 = t * (6 if running else 0)
    for k in range(10):
        a = a0 + k * math.pi / 5
        line(ctx, [(cx, cy), (cx + (r - 14) * math.cos(a), cy + (r - 14) * math.sin(a))], 3, "#e9c46a")
    line(ctx, [(cx, cy), (cx, -20)], 8, "#9a8f86")
    hx, hy = cx, cy + r - 40 + (3 * math.sin(t * 20) if running else 0)
    ellipse(ctx, hx, hy, 42, 30, "#e2a66b")
    ellipse(ctx, hx + 6, hy + 6, 30, 18, "#fbe3c4")
    circle(ctx, hx + 30, hy - 14, 10, "#e2a66b")
    circle(ctx, hx + 26, hy - 6, 5, "#1a1a1a")
    circle(ctx, hx + 44, hy - 2, 4, "#e8737a")
    ctx.restore()


def parrot(ctx, x, y, s, t, **_):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    line(ctx, [(-120, 0), (120, 0)], 14, "#6a4c3a")
    ctx.translate(0, 3 * math.sin(t * 2))
    poly(ctx, [(-20, -40), (-50, 60), (0, 20)], "#2a6fb0")
    ellipse(ctx, 0, -80, 45, 70, "#3db35a")
    ellipse(ctx, -15, -70, 25, 50, "#2e8f47")
    circle(ctx, 10, -160, 40, "#e2463a")
    poly(ctx, [(40, -168), (75, -150), (42, -132)], "#f2c94c")
    circle(ctx, 20, -170, 9, "#ffffff")
    circle(ctx, 22, -170, 5, "#1a1a1a")
    ctx.restore()


def rabbit(ctx, x, y, s, t, **_):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, -60, 70, 60, "#f4f1ea")
    circle(ctx, -70, -60, 20, "#ffffff")
    circle(ctx, 55, -120, 50, "#f4f1ea")
    for dx, rot in ((30, -0.2), (70, 0.25)):
        ellipse(ctx, dx, -210, 16, 60, "#f4f1ea", rot=rot)
        ellipse(ctx, dx, -205, 7, 42, "#f3b8c0", rot=rot)
    circle(ctx, 75, -125, 7, "#1a1a1a")
    circle(ctx, 102, -110, 6, "#e8737a")
    ctx.restore()


def squirrel(ctx, x, y, s, t, walk=None, facing=1, **_):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * facing, s)
    hop = -abs(math.sin((walk or 0) * 1.5)) * 30
    ctx.translate(0, hop)
    ctx.move_to(-40, -30)
    ctx.curve_to(-140, -40, -150, -170, -60, -160)
    ctx.set_line_width(46)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    setc(ctx, "#a0612e")
    ctx.stroke()
    ellipse(ctx, 0, -40, 50, 32, "#b8733a")
    circle(ctx, 48, -70, 26, "#b8733a")
    poly(ctx, [(40, -92), (46, -118), (58, -92)], "#b8733a")
    circle(ctx, 58, -74, 5, "#1a1a1a")
    ctx.restore()


def thought(ctx, ax, ay, text, age, color=(0.75, 0.6, 0.95), size=40, maxw=640, side=1):
    """Thought bubble (dashed outline + trailing circles) in screen space; (ax, ay) = thinker's head."""
    from engine import wrap, ease_out_back, W
    if age < 0:
        return
    k = ease_out_back(age / 0.22)
    font(ctx, size)
    lines = wrap(ctx, text, maxw)
    lh = size * 1.25
    tw = max(text_w(ctx, l) for l in lines)
    bw, bh = tw + 70, lh * len(lines) + 46
    bx = ax + (40 if side > 0 else -40 - bw)
    by = ay - bh - 95
    bx = max(40, min(W - 40 - bw, bx))
    by = max(30, by)
    ctx.save()
    ctx.translate(ax, ay)
    ctx.scale(k, k)
    ctx.translate(-ax, -ay)
    r, g, b = color
    for i, (f, rr) in enumerate(((0.25, 10), (0.55, 15))):
        px = ax + (bx + bw / 2 - ax) * f * 0.5
        py = ay + (by + bh - ay) * f
        circle(ctx, px, py, rr, (1, 1, 1, 1))
        ctx.arc(px, py, rr, 0, 2 * math.pi)
        ctx.set_line_width(4)
        ctx.set_source_rgb(r * 0.6, g * 0.6, b * 0.6)
        ctx.stroke()
    rrect(ctx, bx, by, bw, bh, 40)
    ctx.set_source_rgb(min(1, r * 0.25 + 0.78), min(1, g * 0.25 + 0.78), min(1, b * 0.25 + 0.78))
    ctx.fill_preserve()
    ctx.set_dash([14, 9])
    ctx.set_line_width(5)
    ctx.set_source_rgb(r * 0.6, g * 0.6, b * 0.6)
    ctx.stroke()
    ctx.set_dash([])
    setc(ctx, "#2a2522")
    font(ctx, size)
    for i, l in enumerate(lines):
        ctx.move_to(bx + 35, by + 23 + size + i * lh - 6)
        ctx.show_text(l)
    ctx.restore()
