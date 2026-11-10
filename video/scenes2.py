"""Extra backgrounds and props for the full episode."""
import math
import cairo
from engine import (W, H, rect, fill_rrect, ellipse, circle, line, poly, setc, shade, font, text_w,
                    rrect, draw_char, counter_label)
from scenes import GROUND, haze, window, awning, street, kitchen, living


def wall_floor(ctx, wall, floor, stripe=True):
    rect(ctx, -800, -400, W + 1600, GROUND + 400, wall)
    if stripe:
        for x in range(-800, W + 800, 90):
            rect(ctx, x, -400, 40, GROUND + 400, (1, 1, 1, 0.06))
    rect(ctx, -800, GROUND - 6, W + 1600, H - GROUND + 410, floor)


def tint(ctx, c, a):
    ctx.rectangle(-800, -400, W + 1600, H + 800)
    ctx.set_source_rgba(*c, a)
    ctx.fill()


def sunset(ctx, t=0):
    street(ctx, t, 3)
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, 1.0, 0.55, 0.3, 0.32)
    g.add_color_stop_rgba(1, 0.5, 0.2, 0.35, 0.22)
    ctx.rectangle(-800, -400, W + 1600, H + 800)
    ctx.set_source(g)
    ctx.fill()


def office(ctx, t=0):
    wall_floor(ctx, "#dfe3e1", "#9aa3a6", stripe=False)
    for i in range(4):
        window(ctx, -300 + i * 620, 140, 380, 300, glass="#a9c6d6")
    rect(ctx, -800, 520, W + 1600, 10, "#c5cbc9")
    font(ctx, 46)
    fill_rrect(ctx, 1380, 560, 360, 90, 12, "#2c2f36")
    ctx.move_to(1410, 620)
    setc(ctx, "#f3e9d6")
    ctx.show_text("BRIGHTLINE CO.")
    for x in (-500, 2300):
        fill_rrect(ctx, x, 650, 120, 280, 20, "#5f8f5a")
    haze(ctx, (0.95, 0.96, 0.96), 0.12)


def desk(ctx, x, w=520):
    """Front desk with monitor (drawn in front of a character)."""
    fill_rrect(ctx, x + w * 0.3, GROUND - 470, 240, 150, 10, "#2c2f36")
    rect(ctx, x + w * 0.3 + 10, GROUND - 460, 220, 120, "#8fb7d6")
    rect(ctx, x + w * 0.3 + 105, GROUND - 320, 30, 40, "#2c2f36")
    fill_rrect(ctx, x, GROUND - 290, w, 36, 8, "#b48b62")
    rect(ctx, x + 20, GROUND - 254, w - 40, 254, "#9a7550")
    rect(ctx, x + 30, GROUND - 230, w - 60, 4, "#86643f")


def market(ctx, t=0):
    g = cairo.LinearGradient(0, 0, 0, GROUND)
    g.add_color_stop_rgb(0, 0.73, 0.85, 0.92)
    g.add_color_stop_rgb(1, 0.92, 0.88, 0.78)
    ctx.rectangle(-800, -400, W + 1600, GROUND + 400)
    ctx.set_source(g)
    ctx.fill()
    for i in range(-2, 7):
        x = i * 420
        rect(ctx, x, 220 - (i % 3) * 40, 400, GROUND, ["#c9b18f", "#b4876b", "#93a08a"][i % 3])
        for k in range(2):
            window(ctx, x + 60 + k * 170, 300 - (i % 3) * 40, 100, 130)
    haze(ctx, a=0.25)
    rect(ctx, -800, GROUND - 6, W + 1600, H - GROUND + 410, "#b9ab98")
    for i, x in enumerate((-300, 520, 1900)):
        stall(ctx, x, ["#d9534f", "#3f7f8c", "#e9a23b"][i % 3])


def stall(ctx, x, col, w=560, goods="fruit"):
    line(ctx, [(x + 20, GROUND), (x + 20, 470)], 14, "#6a4c3a")
    line(ctx, [(x + w - 20, GROUND), (x + w - 20, 470)], 14, "#6a4c3a")
    awning(ctx, x - 10, 450, w + 20, col, "#f6efe2", n=7)
    fill_rrect(ctx, x, GROUND - 260, w, 40, 8, "#8a6a52")
    rect(ctx, x + 10, GROUND - 220, w - 20, 220, "#a07a5c")
    for i in range(8):
        c = ["#e76f51", "#e9c46a", "#7fb069", "#f4a261"][i % 4]
        circle(ctx, x + 50 + i * 62, GROUND - 285, 26, c)


def jewelry_stall(ctx, x, w=560):
    line(ctx, [(x + 20, GROUND), (x + 20, 470)], 14, "#6a4c3a")
    line(ctx, [(x + w - 20, GROUND), (x + w - 20, 470)], 14, "#6a4c3a")
    awning(ctx, x - 10, 450, w + 20, "#7b5c99", "#f6efe2", n=7)
    fill_rrect(ctx, x, GROUND - 260, w, 40, 8, "#3b2f28")
    rect(ctx, x + 10, GROUND - 220, w - 20, 220, "#4a3b33")
    for i in range(6):
        cx = x + 70 + i * 85
        ctx.arc(cx, GROUND - 300, 30, 0.2, math.pi - 0.2)
        ctx.set_line_width(6)
        setc(ctx, "#f2c94c")
        ctx.stroke()
        circle(ctx, cx, GROUND - 268, 9, "#f2c94c")
    font(ctx, 34)
    fill_rrect(ctx, x + 150, 560, 260, 60, 10, "#fff6d8")
    ctx.move_to(x + 172, 602)
    setc(ctx, "#b23a30")
    ctx.show_text("REAL GOLD!")


def cafe_in(ctx, t=0):
    wall_floor(ctx, "#e7d3b5", "#8a6a52")
    rect(ctx, -800, 560, W + 1600, GROUND - 560, "#a87e5a")
    for i in range(4):
        window(ctx, -200 + i * 600, 160, 380, 300, glass="#b9d3dc")
    fill_rrect(ctx, 1500, 120, 420, 220, 10, "#2f3a33")
    font(ctx, 36)
    for i, tx in enumerate(["MENU", "Latte  4", "Mocha  5", "Tea    3"]):
        ctx.move_to(1540, 175 + i * 46)
        setc(ctx, "#f3efe6")
        ctx.show_text(tx)
    for x in (300, 1000, 1700):
        line(ctx, [(x, -400), (x, 60)], 4, "#3b3f45")
        poly(ctx, [(x - 60, 110), (x + 60, 110), (x + 30, 60), (x - 30, 60)], "#e07a4f")
    haze(ctx, a=0.10)


def cafe_table(ctx, x):
    ellipse(ctx, x, GROUND - 300, 170, 26, "#5a4636")
    rect(ctx, x - 12, GROUND - 300, 24, 300, "#3b2f28")
    ellipse(ctx, x, GROUND - 6, 90, 14, "#3b2f28")
    fill_rrect(ctx, x - 70, GROUND - 350, 44, 50, 6, "#f4f1ea")
    fill_rrect(ctx, x + 30, GROUND - 345, 40, 45, 6, "#f4f1ea")


def poker_table(ctx, t=0, chips=0):
    ellipse(ctx, 960, GROUND - 210, 640, 90, "#2f6b45")
    ellipse(ctx, 960, GROUND - 220, 600, 70, "#3d8a59")
    rect(ctx, 400, GROUND - 210, 1120, 210, "#5a4636")
    for i in range(5):
        fill_rrect(ctx, 760 + i * 80, GROUND - 250, 60, 84, 6, "#fbf8f2")
        circle(ctx, 790 + i * 80, GROUND - 208, 12, "#c0392b" if i % 2 else "#2a2522")
    for i in range(int(chips)):
        ellipse(ctx, 640 + (i % 5) * 26, GROUND - 238 - (i // 5) * 10, 22, 8,
                ["#c0392b", "#2a6fb0", "#f2c94c"][i % 3])


def karaoke(ctx, t=0):
    rect(ctx, -800, -400, W + 1600, H + 800, "#2a2340")
    for i in range(12):
        a = t * 0.8 + i
        g = cairo.RadialGradient(960 + 700 * math.sin(a), 300 + 150 * math.cos(a * 1.3), 10,
                                 960 + 700 * math.sin(a), 300 + 150 * math.cos(a * 1.3), 260)
        col = [(1, 0.3, 0.6), (0.3, 0.7, 1), (1, 0.8, 0.3)][i % 3]
        g.add_color_stop_rgba(0, *col, 0.18)
        g.add_color_stop_rgba(1, *col, 0)
        ctx.rectangle(-800, -400, W + 1600, H + 800)
        ctx.set_source(g)
        ctx.fill()
    fill_rrect(ctx, 620, 120, 680, 380, 16, "#111111")
    rect(ctx, 640, 140, 640, 340, "#3a5ba0")
    font(ctx, 40)
    ctx.move_to(700, 330)
    setc(ctx, "#ffffff")
    ctx.show_text("~ la la laaa ~")
    rect(ctx, 700, 345, (t * 120) % 520, 6, "#ffd166")
    rect(ctx, -800, GROUND - 6, W + 1600, H - GROUND + 410, "#3d3350")
    fill_rrect(ctx, -300, GROUND - 230, 700, 230, 40, "#7b2f57")
    fill_rrect(ctx, 1550, GROUND - 230, 700, 230, 40, "#7b2f57")


def hallway(ctx, t=0, door_open=0.0):
    wall_floor(ctx, "#d8c8b0", "#8d6b50")
    rect(ctx, -800, 640, W + 1600, 12, "#a8957c")
    for x in (200, 760):
        fill_rrect(ctx, x, 260, 160, 120, 4, "#5a4636")
        rect(ctx, x + 10, 270, 140, 100, ["#e9c46a", "#2a9d8f"][x // 700])
    # Mia's door
    dx = 1300
    rect(ctx, dx - 20, 320, 340, GROUND - 320, "#efe6d6")
    rect(ctx, dx, 340, 300, GROUND - 340, "#3a2c24")
    w = 300 * (1 - 0.75 * door_open)
    rect(ctx, dx, 340, w, GROUND - 340, "#a8714d")
    rect(ctx, dx + 25, 380, w - 50, 200, shade("#a8714d", 0.9))
    rect(ctx, dx + 25, 620, w - 50, 230, shade("#a8714d", 0.9))
    circle(ctx, dx + w - 35, 640, 12, "#e9c46a")
    fill_rrect(ctx, dx + 90, 400, 120, 50, 8, "#f6efe2")
    font(ctx, 30)
    ctx.move_to(dx + 115, 435)
    setc(ctx, "#b4503e")
    ctx.show_text("MIA")
    haze(ctx, a=0.08)


def stairs(ctx, t=0, night=False):
    wall_floor(ctx, "#cdbda5" if not night else "#4b4660", "#7d604a" if not night else "#3b3243")
    for i in range(8):
        x = 200 + i * 110
        y = GROUND - i * 70
        rect(ctx, x, y - 70, 1000, 70, shade("#8d6b50" if not night else "#4a3c50", 1 - i * 0.02))
        rect(ctx, x, y - 74, 1000, 8, "#5a4636" if not night else "#2b2233")
    line(ctx, [(160, GROUND - 200), (1100, GROUND - 760)], 12, "#5a4636")
    if night:
        g = cairo.RadialGradient(1700, 600, 10, 1700, 600, 700)
        g.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.45)
        g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
        ctx.rectangle(-800, -400, W + 1600, H + 800)
        ctx.set_source(g)
        ctx.fill()


def park(ctx, t=0):
    g = cairo.LinearGradient(0, 0, 0, GROUND)
    g.add_color_stop_rgb(0, 0.72, 0.86, 0.93)
    g.add_color_stop_rgb(1, 0.93, 0.93, 0.85)
    ctx.rectangle(-800, -400, W + 1600, GROUND + 400)
    ctx.set_source(g)
    ctx.fill()
    for i in range(-3, 9):
        x = i * 330 + (i % 2) * 60
        rect(ctx, x - 18, 420, 36, GROUND - 420, "#7a5a40")
        for (dx, dy, r) in ((0, 360, 150), (-90, 420, 110), (90, 420, 110)):
            circle(ctx, x + dx, dy, r, ["#7fb069", "#6a9f58", "#8cbf74"][(i + dx // 90) % 3])
    haze(ctx, (0.95, 0.97, 0.9), 0.25)
    rect(ctx, -800, GROUND - 120, W + 1600, H - GROUND + 520, "#9cc47a")
    rect(ctx, -800, GROUND - 30, W + 1600, 90, "#d8c9a8")


def bench(ctx, x):
    fill_rrect(ctx, x - 260, GROUND - 330, 520, 30, 8, "#8a5a3a")
    fill_rrect(ctx, x - 260, GROUND - 280, 520, 30, 8, "#8a5a3a")
    fill_rrect(ctx, x - 270, GROUND - 200, 540, 34, 8, "#9a6a48")
    for dx in (-230, 230):
        rect(ctx, x + dx - 10, GROUND - 200, 20, 200, "#3b3f45")


def pigeons(ctx, x, t, fly=None):
    for i in range(5):
        px = x - 200 + i * 90 + 6 * math.sin(t * 3 + i)
        py = GROUND + 20 + (i % 2) * 18
        if fly is not None and t > fly:
            d = t - fly
            px += (i - 2) * 160 * d
            py -= 420 * d + 30 * math.sin(d * 20 + i)
            wing = 22 * math.sin(d * 30 + i)
            poly(ctx, [(px - 30, py - 10 - wing), (px, py - 10), (px + 30, py - 10 - wing)], "#8f96a3")
        ellipse(ctx, px, py, 26, 16, "#8f96a3")
        circle(ctx, px + 22, py - 14, 11, "#7a8290")
        poly(ctx, [(px + 32, py - 15), (px + 42, py - 12), (px + 32, py - 10)], "#e9a23b")


def bathroom(ctx, t=0):
    wall_floor(ctx, "#cfe0e3", "#9fb2b7", stripe=False)
    for x in range(-800, W + 800, 80):
        for y in range(0, GROUND, 80):
            ctx.rectangle(x, y, 80, 80)
    ctx.set_line_width(2)
    setc(ctx, "#b9cdd1")
    ctx.stroke()
    fill_rrect(ctx, 560, 260, 800, 520, 30, "#b9c3c6")
    rect(ctx, 590, 290, 740, 460, "#d9eef3")
    poly(ctx, [(600, 740), (900, 300), (1000, 300), (700, 740)], (1, 1, 1, 0.3))
    fill_rrect(ctx, 520, 800, 880, 60, 14, "#f4f6f6")
    rect(ctx, 600, 860, 720, GROUND - 860, "#e4e9ea")
    tint(ctx, (0.1, 0.12, 0.25), 0.25)


def bedroom_mirror(ctx, t=0):
    wall_floor(ctx, "#d9c3a5", "#8d6b50")
    fill_rrect(ctx, 1150, 180, 420, 640, 200, "#7a5a40")
    fill_rrect(ctx, 1175, 205, 370, 590, 180, "#cfdde0")
    poly(ctx, [(1220, 700), (1400, 260), (1460, 260), (1280, 700)], (1, 1, 1, 0.35))
    fill_rrect(ctx, 1100, 800, 520, 140, 12, "#6a4c3a")
    window(ctx, 200, 220, 360, 320, glass="#f2e3c2")


def hospital(ctx, t=0):
    wall_floor(ctx, "#dfe8e4", "#b8c4c0", stripe=False)
    window(ctx, 1300, 180, 420, 330, glass="#cfe3ea")
    fill_rrect(ctx, 300, GROUND - 330, 1000, 70, 20, "#f4f6f6")
    fill_rrect(ctx, 300, GROUND - 270, 1000, 120, 10, "#9bb9c9")
    rect(ctx, 330, GROUND - 150, 24, 150, "#8a959a")
    rect(ctx, 1246, GROUND - 150, 24, 150, "#8a959a")
    rect(ctx, 1450, 560, 14, GROUND - 560, "#8a959a")
    fill_rrect(ctx, 1400, 540, 120, 60, 10, "#2c2f36")
    pts = [(1410 + i * 10, 570 + 12 * math.sin(i * 1.7 + t * 6)) for i in range(11)]
    line(ctx, pts, 3, "#5fd18b")


def hands_closeup(ctx, t=0):
    hospital(ctx, t)
    tint(ctx, (0, 0, 0), 0.2)
    # old hand (grandpa) from right, Grandma's from left, holding
    line(ctx, [(2300, 760), (1150, 700)], 150, "#9bb9c9")
    line(ctx, [(-400, 640), (800, 620)], 150, "#8a7aa8")
    ellipse(ctx, 1020, 690, 150, 95, "#e7b996")
    ellipse(ctx, 900, 620, 140, 90, "#efc6a6")
    for i in range(4):
        ellipse(ctx, 980 + i * 32, 580 + i * 10, 22, 40, "#efc6a6", rot=0.4)


def phone_screen(ctx, t, query, results, t_type=0.3):
    rect(ctx, -800, -400, W + 1600, H + 800, "#2b3240")
    fill_rrect(ctx, 610, 40, 700, 1000, 70, "#121418")
    fill_rrect(ctx, 640, 70, 640, 940, 50, "#f5f6f8")
    fill_rrect(ctx, 690, 170, 540, 70, 35, "#ffffff")
    rrect(ctx, 690, 170, 540, 70, 35)
    ctx.set_line_width(3)
    setc(ctx, "#c9ced6")
    ctx.stroke()
    n = int(max(0, t - t_type) * 28)
    font(ctx, 30, weight="normal")
    q = query[:n]
    lines, cur = [], ""
    for w in q.split(" "):
        if text_w(ctx, (cur + " " + w).strip()) > 470:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    ctx.move_to(720, 215)
    setc(ctx, "#2a2522")
    ctx.show_text(lines[-1] + ("|" if int(t * 2) % 2 == 0 else ""))
    for i, (tt, title, body) in enumerate(results):
        if t < tt:
            continue
        y = 300 + i * 230
        fill_rrect(ctx, 690, y, 540, 200, 20, "#ffffff")
        font(ctx, 40)
        ctx.move_to(720, y + 70)
        setc(ctx, "#1f4fa3")
        ctx.show_text(title)
        font(ctx, 28, weight="normal")
        ctx.move_to(720, y + 130)
        setc(ctx, "#4a4f57")
        ctx.show_text(body)


def tv_window(ctx, t, pol):
    street(ctx, t, 4)
    fill_rrect(ctx, 560, 230, 800, 560, 16, "#2c2f36")
    font(ctx, 36)
    ctx.move_to(780, 280)
    setc(ctx, "#f3e9d6")
    ctx.show_text("ELECTRO WORLD")
    fill_rrect(ctx, 640, 320, 640, 400, 14, "#111111")
    ctx.save()
    ctx.rectangle(660, 340, 600, 360)
    ctx.clip()
    rect(ctx, 660, 340, 600, 360, "#2d4f7a")
    rect(ctx, 660, 600, 600, 100, "#1a2f4d")
    draw_char(ctx, pol, 960, 840, 0.62, t, expr="happy", pose="present", talking=True)
    fill_rrect(ctx, 800, 600, 320, 120, 10, "#8a5a3a")
    ctx.restore()
    if int(t * 4) % 2 == 0:
        fill_rrect(ctx, 870, 330, 180, 56, 14, "#c0392b")
        font(ctx, 34)
        ctx.move_to(895, 370)
        setc(ctx, "#ffffff")
        ctx.show_text("ERROR")
    for i in range(14):
        y = 340 + ((i * 47 + t * 400) % 360)
        rect(ctx, 660, y, 600, 2, (1, 1, 1, 0.06))
