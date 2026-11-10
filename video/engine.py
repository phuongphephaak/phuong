"""Tiny 2D vector animation engine (cairo) for flat-style story videos."""
import math
import cairo

W, H = 1920, 1080
FONT = "Inter"


# ---------------------------------------------------------------- helpers
def hexc(h, a=1.0):
    if not isinstance(h, str):
        return tuple(h) if len(h) == 4 else (*h, a)
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def setc(ctx, c, a=None):
    r, g, b, aa = hexc(c) if isinstance(c, str) else c
    ctx.set_source_rgba(r, g, b, aa if a is None else a)


def shade(c, k):
    r, g, b, a = hexc(c)
    f = (lambda v: max(0, min(1, v * k))) if k < 1 else (lambda v: max(0, min(1, v + (1 - v) * (k - 1))))
    return (f(r), f(g), f(b), a)


def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def fill_rrect(ctx, x, y, w, h, r, c, a=None):
    rrect(ctx, x, y, w, h, r)
    setc(ctx, c, a)
    ctx.fill()


def rect(ctx, x, y, w, h, c, a=None):
    ctx.rectangle(x, y, w, h)
    setc(ctx, c, a)
    ctx.fill()


def ellipse(ctx, x, y, rx, ry, c, a=None, rot=0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    setc(ctx, c, a)
    ctx.fill()


def circle(ctx, x, y, r, c, a=None):
    ellipse(ctx, x, y, r, r, c, a)


def line(ctx, pts, w, c, cap=cairo.LINE_CAP_ROUND, a=None):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.set_line_width(w)
    ctx.set_line_cap(cap)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    setc(ctx, c, a)
    ctx.stroke()


def poly(ctx, pts, c, a=None):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()
    setc(ctx, c, a)
    ctx.fill()


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ease_out_back(x):
    x = max(0.0, min(1.0, x))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def font(ctx, size, weight="bold", italic=False):
    ctx.select_font_face(
        FONT,
        cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_BOLD if weight == "bold" else cairo.FONT_WEIGHT_NORMAL,
    )
    ctx.set_font_size(size)


def text_w(ctx, s):
    return ctx.text_extents(s).x_advance


def wrap(ctx, s, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if text_w(ctx, test) > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


def fmt(n):
    return f"{n:,}"


# ---------------------------------------------------------------- characters
class Char:
    def __init__(self, skin, top, pants="#3d4250", shoes="#f1ece4", hair="short",
                 hair_c="#3b2a20", extra=(), blink_phase=0.0):
        self.skin, self.top, self.pants, self.shoes = skin, top, pants, shoes
        self.hair, self.hair_c, self.extra, self.blink_phase = hair, hair_c, set(extra), blink_phase


ARMS = {
    # (elbow, hand) for the character's left arm (x<0); right arm mirrors unless given
    "down": (((-112, -310), (-110, -215)), ((112, -310), (110, -215))),
    "hips": (((-160, -330), (-82, -262)), ((160, -330), (82, -262))),
    "shrug": (((-165, -320), (-185, -420)), ((165, -320), (185, -420))),
    "wave": (((-112, -310), (-110, -215)), ((175, -470), (165, -590))),
    "point": (((-112, -310), (-110, -215)), ((190, -400), (265, -420))),
    "hold": (((-130, -300), (-60, -300)), ((130, -300), (60, -300))),
    "cane": (((-112, -310), (-110, -215)), ((140, -300), (150, -230))),
    "chin": (((-112, -310), (-110, -215)), ((150, -360), (55, -450))),
    "present": (((-112, -310), (-110, -215)), ((175, -340), (240, -330))),
}


def draw_char(ctx, c, x, y, s=1.0, t=0.0, expr="neutral", pose="down", look=0.0,
              talking=False, flip=False):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(-s if flip else s, s)
    bob = 3 * math.sin(t * 2.4 + c.blink_phase)

    # legs + shoes
    for sx in (-1, 1):
        line(ctx, [(sx * 34, -205), (sx * 36, -22)], 46, c.pants)
        ellipse(ctx, sx * 44, -14, 40, 18, c.shoes)
        ellipse(ctx, sx * 44, -4, 40, 6, shade(c.shoes, 0.8))

    ctx.translate(0, bob)
    # arms (behind torso for the far side)
    arms = ARMS.get(pose, ARMS["down"])
    wave_off = 16 * math.sin(t * 11) if pose == "wave" else 0
    sleeve = shade(c.top, 0.9)

    def arm(sh, el, hd):
        line(ctx, [sh, el, hd], 40, sleeve)
        circle(ctx, hd[0], hd[1], 21, c.skin)

    # torso
    if "suit" in c.extra:
        fill_rrect(ctx, -100, -440, 200, 255, 48, c.top)
        poly(ctx, [(-34, -440), (34, -440), (0, -360)], "#f4f1ea")
        poly(ctx, [(-10, -430), (10, -430), (14, -330), (0, -305), (-14, -330)], "#b8433b")
        line(ctx, [(-34, -440), (-6, -330)], 6, shade(c.top, 0.75))
        line(ctx, [(34, -440), (6, -330)], 6, shade(c.top, 0.75))
    else:
        ellipse(ctx, 0, -440, 92, 38, shade(c.top, 0.78))  # hood
        fill_rrect(ctx, -100, -440, 200, 255, 50, c.top)
        fill_rrect(ctx, -58, -300, 116, 58, 18, shade(c.top, 0.88))
        if "apron" in c.extra:
            fill_rrect(ctx, -70, -380, 140, 200, 20, "#f3efe6")
            line(ctx, [(-50, -380), (-30, -430)], 6, "#f3efe6")
            line(ctx, [(50, -380), (30, -430)], 6, "#f3efe6")
        else:
            line(ctx, [(-24, -425), (-26, -372)], 5, "#f3efe6")
            line(ctx, [(24, -425), (26, -372)], 5, "#f3efe6")
    (el1, hd1), (el2, hd2) = arms
    arm((-88, -410), el1, hd1)
    arm((88, -410), (el2[0] + wave_off * 0.3, el2[1]), (hd2[0] + wave_off, hd2[1]))
    if pose == "cane":
        line(ctx, [(150, -232), (156, 10 - bob)], 9, "#5b3f2b")
        line(ctx, [(150, -232), (128, -248)], 9, "#5b3f2b")

    # head
    hy = -560
    hc = c.hair_c
    if c.hair == "ponytail":
        ellipse(ctx, 108, hy + 10, 38, 85, hc, rot=-0.35)
    if c.hair == "bob":
        fill_rrect(ctx, -132, hy - 70, 264, 190, 60, hc)
    if c.hair == "bun":
        circle(ctx, 0, hy - 125, 46, hc)
    for sx in (-1, 1):
        circle(ctx, sx * 112, hy + 8, 22, c.skin)
    circle(ctx, 0, hy, 118, c.skin)
    ctx.save()
    ctx.arc(0, hy, 118, 0, 2 * math.pi)
    ctx.clip()
    ellipse(ctx, 40, hy + 80, 120, 70, (0, 0, 0, 0.06))
    ctx.restore()

    # hair on top
    ctx.save()
    ctx.arc(0, hy, 121, 0, 2 * math.pi)
    ctx.clip()
    if c.hair in ("short", "ponytail", "bob", "bun", "slick"):
        ellipse(ctx, 0, hy - 88, 140, 66, hc)
        if c.hair == "short":
            for i in range(5):
                circle(ctx, -70 + i * 35, hy - 40, 22, hc)
        if c.hair == "slick":
            ellipse(ctx, -40, hy - 50, 90, 30, hc, rot=0.25)
            ellipse(ctx, 20, hy - 100, 60, 10, (1, 1, 1, 0.25), rot=0.1)
        if c.hair in ("bob", "ponytail"):
            ellipse(ctx, -50, hy - 45, 80, 30, hc, rot=0.35)
        if c.hair == "bun":
            ellipse(ctx, 0, hy - 70, 130, 40, hc)
    elif c.hair == "bowl":
        rect(ctx, -130, hy - 140, 260, 105, hc)
        for i in range(-3, 4):
            poly(ctx, [(i * 34 - 17, hy - 36), (i * 34 + 17, hy - 36), (i * 34, hy - 18)], hc)
        line(ctx, [(70, hy - 110), (90, hy - 80), (75, hy - 60), (95, hy - 40)], 9, shade(hc, 1.6))
    elif c.hair == "spiky":
        ellipse(ctx, 0, hy - 95, 135, 55, hc)
    elif c.hair == "bald":
        pass
    ctx.restore()
    if c.hair == "spiky":
        for i in range(6):
            bx = -95 + i * 38
            poly(ctx, [(bx - 26, hy - 88), (bx + 26, hy - 88), (bx + 10, hy - 158 + (i % 2) * 18)], hc)
    if c.hair == "bowl":
        pass

    # face
    blink = 1.0
    bt = (t + c.blink_phase) % 3.3
    if bt < 0.13:
        blink = 0.12
    ex, ey = 44, hy + 5
    big = expr in ("shock",)
    for sx in (-1, 1):
        cx = sx * ex
        if expr in ("happy", "laugh"):
            line(ctx, [(cx - 18, ey + 6), (cx, ey - 12), (cx + 18, ey + 6)], 9, "#2a2522")
            continue
        rx, ry = (27, 34) if big else (21, 26)
        ellipse(ctx, cx, ey, rx, ry * blink, "#ffffff")
        pr = 8 if big else 12
        if blink > 0.5:
            circle(ctx, cx + look * 8, ey + 3, pr, "#2a2522")
            circle(ctx, cx + look * 8 + 4, ey - 2, pr * 0.35, "#ffffff")
        if expr == "suspicious":
            rect(ctx, cx - 30, ey - 40, 60, 38, c.skin)
            line(ctx, [(cx - 22, ey - 2), (cx + 22, ey - 2)], 6, "#2a2522")
        if expr == "sad":
            pass
    # brows
    bcol = shade(c.hair_c, 0.8) if c.hair != "bald" else "#7a6a5a"
    for sx in (-1, 1):
        if expr == "shock":
            pts = [(sx * 26, ey - 62), (sx * 62, ey - 66)]
        elif expr == "sad":
            pts = [(sx * 22, ey - 50), (sx * 60, ey - 36)]
        elif expr == "suspicious":
            pts = [(sx * 22, ey - 36), (sx * 62, ey - 46)]
        elif expr == "think":
            pts = [(sx * 22, ey - 42 - (8 if sx > 0 else 0)), (sx * 62, ey - 46 - (8 if sx > 0 else 0))]
        else:
            pts = [(sx * 24, ey - 44), (sx * 60, ey - 46)]
        line(ctx, pts, 10, bcol)
    if "glasses" in c.extra:
        for sx in (-1, 1):
            ctx.arc(sx * ex, ey, 34, 0, 2 * math.pi)
            ctx.set_line_width(6)
            setc(ctx, "#4a3b33")
            ctx.stroke()
        line(ctx, [(-10, ey - 4), (10, ey - 4)], 6, "#4a3b33")
    if expr not in ("shock",):
        for sx in (-1, 1):
            ellipse(ctx, sx * 76, hy + 52, 20, 12, "#e98b7c", a=0.35)
    # mouth
    my = hy + 66
    if talking:
        o = abs(math.sin(t * 13)) * 14 + 3
        ellipse(ctx, 0, my, 18, o, "#4a2320")
    elif expr == "shock":
        ellipse(ctx, 0, my + 6, 15, 22, "#4a2320")
    elif expr in ("happy", "laugh"):
        ctx.move_to(-34, my - 8)
        ctx.curve_to(-30, my + 34, 30, my + 34, 34, my - 8)
        ctx.close_path()
        setc(ctx, "#4a2320")
        ctx.fill()
        ellipse(ctx, 0, my + 14, 14, 7, "#e0766a")
    elif expr == "sad":
        ctx.move_to(-24, my + 10)
        ctx.curve_to(-10, my - 8, 10, my - 8, 24, my + 10)
        ctx.set_line_width(8)
        setc(ctx, "#4a2320")
        ctx.stroke()
    elif expr == "suspicious":
        line(ctx, [(-20, my + 2), (22, my - 4)], 8, "#4a2320")
    elif expr == "think":
        line(ctx, [(-14, my), (16, my)], 8, "#4a2320")
    else:
        ctx.move_to(-22, my - 4)
        ctx.curve_to(-10, my + 10, 10, my + 10, 22, my - 4)
        ctx.set_line_width(8)
        setc(ctx, "#4a2320")
        ctx.stroke()
    ctx.restore()


def draw_cat(ctx, x, y, s=1.0, t=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    col, dk = "#d98b45", "#b86e33"
    sw = math.sin(t * 2.5) * 0.25
    ctx.move_to(70, -30)
    ctx.curve_to(170, -20, 160 + 30 * sw, -150, 120 + 40 * sw, -170)
    ctx.set_line_width(22)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    setc(ctx, col)
    ctx.stroke()
    ellipse(ctx, 0, -80, 95, 85, col)
    ellipse(ctx, 0, -60, 50, 55, "#f2d2a9")
    ellipse(ctx, -45, -8, 30, 14, col)
    ellipse(ctx, 45, -8, 30, 14, col)
    poly(ctx, [(-70, -230), (-60, -300), (-15, -250)], col)
    poly(ctx, [(70, -230), (60, -300), (15, -250)], col)
    poly(ctx, [(-60, -240), (-56, -280), (-30, -250)], "#f0a8a0")
    poly(ctx, [(60, -240), (56, -280), (30, -250)], "#f0a8a0")
    circle(ctx, 0, -205, 80, col)
    for i in range(3):
        line(ctx, [(-30 + i * 22, -280), (-26 + i * 22, -255)], 7, dk)
    for sx in (-1, 1):
        ellipse(ctx, sx * 30, -210, 15, 9, "#c9e06a")
        ellipse(ctx, sx * 30, -210, 3, 9, "#2a2522")
        line(ctx, [(sx * 45, -178), (sx * 105, -185)], 3, "#f6eee2")
        line(ctx, [(sx * 45, -170), (sx * 105, -165)], 3, "#f6eee2")
    poly(ctx, [(-8, -185), (8, -185), (0, -176)], "#e07b7b")
    line(ctx, [(-14, -165), (0, -172), (14, -165)], 4, "#5a3a2a")
    ctx.restore()


# ---------------------------------------------------------------- UI elements
def counter_label(ctx, x, y, value, pop=0.0, flash=0.0, s=1.0):
    """Lie counter pill anchored at (x,y) = tip of the pointer."""
    ctx.save()
    ctx.translate(x, y)
    sc = s * (1 + 0.35 * pop)
    ctx.scale(sc, sc)
    font(ctx, 40)
    txt = fmt(value)
    tw = text_w(ctx, txt)
    w, h = tw + 96, 64
    base = (0.11 + 0.62 * flash, 0.12 + 0.08 * flash, 0.15 + 0.06 * flash, 0.94)
    fill_rrect(ctx, -w / 2, -h - 16, w, h, 18, base)
    poly(ctx, [(-14, -17), (14, -17), (0, 0)], base)
    # icon: small "nose" pinocchio-style chevron -> generic lie symbol: a crossed-fingers-like mark
    ix = -w / 2 + 34
    circle(ctx, ix, -h / 2 - 16, 15, "#ff6b5e" if flash < 0.5 else "#ffffff")
    font(ctx, 22)
    ctx.move_to(ix - 5.5, -h / 2 - 8)
    setc(ctx, "#1c1d22")
    ctx.show_text("!")
    font(ctx, 40)
    ctx.move_to(-w / 2 + 62, -h / 2 + 14 - 16)
    setc(ctx, "#ffffff")
    ctx.show_text(txt)
    ctx.restore()


def plus_one(ctx, x, y, age):
    if age < 0 or age > 1.0:
        return
    a = 1 - ease(age)
    font(ctx, 46)
    ctx.move_to(x + 20, y - 40 - age * 90)
    ctx.text_path("+1")
    ctx.set_line_width(8)
    setc(ctx, "#1c1d22", a)
    ctx.stroke_preserve()
    setc(ctx, "#ff6b5e", a)
    ctx.fill()


def bubble(ctx, ax, ay, text, age, side=1, size=40, maxw=640):
    """Speech bubble in screen space; (ax,ay) = point the tail aims at."""
    if age < 0:
        return
    k = ease_out_back(age / 0.22)
    font(ctx, size)
    lines = wrap(ctx, text, maxw)
    lh = size * 1.25
    tw = max(text_w(ctx, l) for l in lines)
    bw, bh = tw + 64, lh * len(lines) + 40
    bx = ax + (30 if side > 0 else -30 - bw)
    by = ay - bh - 70
    bx = max(40, min(W - 40 - bw, bx))
    by = max(30, by)
    ctx.save()
    ctx.translate(ax, ay)
    ctx.scale(k, k)
    ctx.translate(-ax, -ay)
    tx = max(bx + 40, min(bx + bw - 40, ax + 40 * side))
    ctx.move_to(tx - 26, by + bh - 4)
    ctx.line_to(ax, ay - 8)
    ctx.line_to(tx + 26, by + bh - 4)
    ctx.close_path()
    setc(ctx, "#2a2522")
    ctx.set_line_width(10)
    ctx.stroke_preserve()
    setc(ctx, "#fffdf8")
    ctx.fill()
    rrect(ctx, bx, by, bw, bh, 28)
    ctx.set_line_width(6)
    setc(ctx, "#2a2522")
    ctx.stroke_preserve()
    setc(ctx, "#fffdf8")
    ctx.fill()
    ctx.move_to(tx - 24, by + bh - 6)
    ctx.line_to(tx + 24, by + bh - 6)
    ctx.set_line_width(10)
    ctx.stroke()
    setc(ctx, "#2a2522")
    for i, l in enumerate(lines):
        ctx.move_to(bx + 32, by + 20 + size + i * lh - 6)
        ctx.show_text(l)
    ctx.restore()


def caption(ctx, text, age, y=1000, size=54):
    if age < 0:
        return
    a = ease(age / 0.2)
    font(ctx, size)
    lines = wrap(ctx, text, 1500)
    lh = size * 1.22
    y0 = y - (len(lines) - 1) * lh
    for i, l in enumerate(lines):
        tw = text_w(ctx, l)
        ctx.move_to(W / 2 - tw / 2 + 4, y0 + i * lh + (1 - a) * 12 + 5)
        ctx.text_path(l)
        setc(ctx, "#000000", 0.45 * a)
        ctx.fill()
        ctx.move_to(W / 2 - tw / 2, y0 + i * lh + (1 - a) * 12)
        ctx.text_path(l)
        ctx.set_line_width(7)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        setc(ctx, "#15161a", a)
        ctx.stroke_preserve()
        setc(ctx, "#ffffff", a)
        ctx.fill()


def tag(ctx, text, x, y, age, size=34):
    """Small dark chapter tag like 'THE NEXT DAY'."""
    if age < 0:
        return
    a = ease(age / 0.2)
    font(ctx, size)
    tw = text_w(ctx, text)
    fill_rrect(ctx, x, y, tw + 44, size + 26, 14, "#1c1d22", 0.85 * a)
    ctx.move_to(x + 22, y + size + 6)
    setc(ctx, "#ffffff", a)
    ctx.show_text(text)
