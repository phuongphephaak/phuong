"""Spec-driven infographics (Dien Bien Phu film).  python gfx3.py <kind> <dur> <out.mp4> '<json spec>'
Kinds: map, portrait, portraits, roster, keyword, telegram, codes, clock, stat, altitude, title, sting, memoir, end,
       and overlays: subscribe (RGBA .mov), logo (png)."""
import json, math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "gfx"))
import gfx2 as G
from gfx2 import W, H, FPS, CYAN, WHITE, font, ease, back, shadow_text, finish, SatMap, draw_pin, label2, tag_box, \
    ship_icon, plane_icon, path_arrow, grid_bg, portrait, kenburns, tactical_bg

INTER, INTER_SB, OSWALD = G.INTER, G.INTER_SB, G.OSWALD
RED = (226, 40, 36)
PH = os.path.join(HERE, "photos")
BRAND = "/home/user/phuong/video/brand"
COL = {"red": (255, 70, 60), "cyan": CYAN, "yellow": (255, 215, 90), "white": WHITE, "orange": (255, 140, 60)}


def ph(name):
    for e in (".jpg", ".png", ".jpeg"):
        p = os.path.join(PH, name + e)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


def kb(photo, t, D, z0=1.0, z1=1.1, gray=False, dark=0.0):
    return kenburns(ph(photo), t, D, z0, z1, gray, dark)


# ------------------------------------------------------------------ map
def f_map(t, D, s):
    m = SatMap(tuple(s["view0"]), tuple(s.get("view1", s["view0"])), tilt=s.get("tilt", 0.14))
    img = m.frame(t / D)
    if s.get("bg") == "tactical":
        img = tactical_bg(m, t, D, step=s.get("grid", 2))
    P = lambda ll: m.project(*ll)
    for it in s.get("items", []):
        k = (t - it.get("t", 0)) / it.get("fade", 0.5)
        if k <= 0:
            continue
        a = ease(k)
        ty = it["type"]
        if ty == "region":
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            c = tuple(it.get("color", (220, 40, 40)))
            ImageDraw.Draw(lay).polygon([P(p) for p in it["poly"]], fill=c + (int(it.get("alpha", 90) * a),),
                                        outline=c + (int(200 * a),))
            img.alpha_composite(lay)
        elif ty == "pin":
            x, y = P(it["at"])
            draw_pin(img, x, y, s=0.6 + 0.4 * back(k), alpha=a, color=COL.get(it.get("color", "orange")))
            anc = it.get("anchor", "l")
            if it.get("big"):
                if anc == "m":
                    label2(img, x, y + 92, it.get("small", ""), it["big"], alpha=a, size=it.get("size", 50), anchor="m")
                elif anc == "r":
                    label2(img, x - 34, y - 44, it.get("small", ""), it["big"], alpha=a, size=it.get("size", 50), anchor="r")
                else:
                    label2(img, x + 34, y - 44, it.get("small", ""), it["big"], alpha=a, size=it.get("size", 50), anchor="l")
        elif ty == "label":
            x, y = P(it["at"])
            label2(img, x + it.get("dx", 0), y + it.get("dy", 0), it.get("small", ""), it["big"], alpha=a,
                   size=it.get("size", 46), anchor=it.get("anchor", "m"))
        elif ty == "arrow":
            kk = ease((t - it["t"]) / it.get("dur", 2.0))
            r = path_arrow(img, [P(p) for p in it["path"]], kk, color=COL[it.get("color", "red")],
                           width=it.get("w", 6), dashed=it.get("dashed", False))
            if r and it.get("icon") == "plane":
                plane_icon(img, *r[0], r[1], s=0.9, color=COL[it.get("color", "red")])
            if r and it.get("icon") == "ship":
                ship_icon(img, *r[0], r[1], s=1.3, color=COL[it.get("color", "red")])
        elif ty == "ships":
            x0, y0 = P(it["at"])
            n, side = it.get("n", 4), it.get("side", "jp")
            col = (240, 240, 240) if side == "jp" else (90, 200, 255)
            offs = [(0, 0), (60, 34), (20, -50), (90, -16), (-40, 40), (120, 30)][:n]
            ang = math.radians(it.get("ang", -20))
            for i, (dx, dy) in enumerate(offs):
                ship_icon(img, x0 + dx, y0 + dy, ang, s=it.get("s", 1.5), color=col, alpha=ease(k - i * 0.15))
            if it.get("label"):
                tag_box(img, x0 + it.get("ldx", -60), y0 + it.get("ldy", 90), it["label"], alpha=a)
        elif ty == "tag":
            x, y = P(it["at"])
            tag_box(img, x + it.get("dx", 0), y + it.get("dy", 0), it["text"], alpha=a, size=it.get("size", 28))
        elif ty == "x":
            x, y = P(it["at"])
            d = ImageDraw.Draw(img)
            r = 22 * (0.6 + 0.4 * back(k))
            for sgn in (1, -1):
                d.line([(x - r, y - r * sgn), (x + r, y + r * sgn)], fill=(255, 60, 50, int(255 * a)), width=9)
        elif ty == "q":
            x, y = P(it["at"])
            shadow_text(img, (x, y), "?", font(INTER, 110 * (0.7 + 0.3 * back(k))), fill=(255, 215, 90), anchor="mm", alpha=a)
        elif ty == "subs":
            pts = [P(p) for p in it["path"]]
            n = it.get("n", 7)
            for i in range(n):
                f = i / (n - 1)
                x = pts[0][0] + (pts[1][0] - pts[0][0]) * f
                y = pts[0][1] + (pts[1][1] - pts[0][1]) * f
                aa = ease(k - i * 0.12)
                ImageDraw.Draw(img).ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 90, 80, int(255 * aa)),
                                            outline=(0, 0, 0, int(200 * aa)), width=2)
        elif ty == "fan":            # scout search lines from a point
            x0, y0 = P(it["at"])
            for j, (ang, delay) in enumerate(it["rays"]):
                kk = ease((t - it["t"] - delay) / 2.0)
                if kk <= 0:
                    continue
                L = it.get("len", 520) * kk
                x1, y1 = x0 + L * math.cos(math.radians(ang)), y0 - L * math.sin(math.radians(ang))
                late = delay > 1.0
                path_arrow(img, [(x0, y0), (x1, y1)], 1.0, color=COL["red" if late else "yellow"], width=4, dashed=True)
                if late and kk > 0.95:
                    tag_box(img, x1 + 10, y1 - 30, it.get("late_label", "TRỄ 30 PHÚT"), alpha=ease((t - it["t"] - delay - 2) * 2))
    if s.get("corner"):
        shadow_text(img, (W - 70, 90), s["corner"], font(INTER, 40), anchor="rs")
    if s.get("clock"):
        shadow_text(img, (W - 70, 160), s["clock"], font(INTER, 64), fill=(255, 215, 90), anchor="rs")
    return finish(img, grain=5)


# ------------------------------------------------------------------ people
def f_portrait(t, D, s):
    if s.get("bg") == "map":
        m = SatMap(tuple(s["view0"]), tuple(s.get("view1", s["view0"])))
        img = m.frame(t / D)
    elif s.get("bg") == "photo":
        img = kb(s["bgphoto"], t, D, gray=True, dark=0.55)
    else:
        img = grid_bg(t)
    cx = s.get("cx", W / 2 if s.get("bg") not in ("map",) else 430)
    try:
        photo = ph(s["photo"])
        if os.path.getsize(photo) < 1000:
            raise FileNotFoundError
    except FileNotFoundError:                     # no usable photo: big name card instead
        k = ease(t / 0.6)
        shadow_text(img, (cx, H / 2), s["name"].upper(), font(OSWALD, 130 * (1.1 - 0.1 * k)), anchor="mm", alpha=k)
        if s.get("sub"):
            shadow_text(img, (cx, H / 2 + 110), s["sub"], font(INTER, 34), fill=CYAN, anchor="mm", alpha=ease((t - 0.4) / 0.5))
        return finish(img)
    portrait(img, photo, cx, s.get("cy", 450), s.get("h", 560), t / 0.8, s["name"], s.get("sub"))
    return finish(img)


def f_portraits(t, D, s):
    img = grid_bg(t)
    ppl = s["people"]
    n = len(ppl)
    for i, (photo, name, sub) in enumerate(ppl):
        cx = W / 2 + (i - (n - 1) / 2) * (W / (n + 0.4))
        portrait(img, ph(photo), cx, 430, 420, (t - i * 0.5) / 0.8, name, sub)
    return finish(img)


def f_roster(t, D, s):
    img = kb(s["photo"], t, D, gray=True, dark=0.6)
    if s.get("portrait"):
        p = s["portrait"]
        portrait(img, ph(p[0]), 420, 450, 520, t / 0.8, p[1], p[2])
        x0 = 860
    else:
        x0 = W / 2 - 420
    shadow_text(img, (x0, 230), s["title"], font(INTER, 40), fill=CYAN, anchor="ls", alpha=ease((t - 0.3) / 0.5))
    for i, item in enumerate(s["items"]):
        name, sub = item[0], item[1]
        col = tuple(item[2]) if len(item) > 2 else WHITE
        k = (t - 0.8 - i * 0.55) / 0.5
        if k <= 0:
            continue
        y = 330 + i * 150
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        xx = x0 - 60 * (1 - ease(k))
        d.rectangle((xx, y - 70, xx + 840, y + 50), fill=(10, 12, 16, int(170 * ease(k))))
        d.rectangle((xx, y - 70, xx + 10, y + 50), fill=col + (int(255 * ease(k)),))
        img.alpha_composite(lay)
        shadow_text(img, (xx + 40, y), name, font(OSWALD, 74), anchor="ls", alpha=ease(k))
        if sub:
            shadow_text(img, (xx + 40, y + 38), sub, font(INTER_SB, 26), fill=col if col != WHITE else CYAN,
                        anchor="ls", alpha=ease(k))
    return finish(img)


# ------------------------------------------------------------------ text cards
def f_keyword(t, D, s):
    img = kb(s["photo"], t, D, gray=s.get("gray", True), dark=0.45)
    k = ease(t / 0.35)
    sc = 1.25 - 0.25 * k
    f = font(OSWALD, s.get("size", 150) * sc)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((W / 2, H / 2), s["word"], font=f, fill=(0, 0, 0, int(200 * k)), anchor="mm")
    lay = lay.filter(ImageFilter.GaussianBlur(10))
    ImageDraw.Draw(lay).text((W / 2, H / 2), s["word"], font=f, fill=RED + (int(255 * k),), anchor="mm",
                             stroke_width=2, stroke_fill=(120, 0, 0, int(255 * k)))
    if s.get("sub"):
        shadow_text(lay, (W / 2, H / 2 + 120), s["sub"], font(INTER, 40), anchor="ms", alpha=ease((t - 0.5) / 0.5))
    img.alpha_composite(lay)
    return finish(img, grain=10)


def f_title(t, D, s):
    img = kb(s["photo"], t, D, z0=1.08, z1=1.0, gray=True, dark=0.5)
    k = ease((t - 0.2) / 0.5)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = font(OSWALD, 170 * (1.15 - 0.15 * k))
    ImageDraw.Draw(lay).text((W / 2, H / 2 - 40), s["l1"], font=f, fill=(0, 0, 0, int(220 * k)), anchor="mm")
    lay = lay.filter(ImageFilter.GaussianBlur(12))
    ImageDraw.Draw(lay).text((W / 2, H / 2 - 40), s["l1"], font=f, fill=RED + (int(255 * k),), anchor="mm")
    img.alpha_composite(lay)
    shadow_text(img, (W / 2, H / 2 + 110), s["l2"], font(INTER, 64), anchor="ms", alpha=ease((t - 0.9) / 0.6))
    d = ImageDraw.Draw(img)
    w = 520 * ease((t - 1.2) / 0.6)
    d.rectangle((W / 2 - w, H / 2 + 150, W / 2 + w, H / 2 + 156), fill=RED)
    out = finish(img, grain=9)
    if t < 0.12:
        out = Image.blend(out, Image.new("RGB", (W, H), "white"), 1 - t / 0.12)
    return out


def f_telegram(t, D, s):
    img = Image.new("RGBA", (W, H), (6, 8, 10, 255))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    cx, top, base = W / 2, 330, 820
    xs = np.arange(0, W, 4)
    ys = 400 + 60 * (0.6 + 0.4 * np.sin(t * 3)) * np.sin(xs / 37 + t * 9) * np.exp(-((xs - cx) / 700) ** 2) * (1 + 0.5 * np.sin(xs / 11 + t * 17))
    dl.line(list(zip(xs, ys)), fill=CYAN + (255,), width=4)
    for i in range(3):
        r = ((t * 160 + i * 160) % 480) + 60
        a = int(255 * (1 - (r - 60) / 480))
        for st, en in ((200, 340), (20, 160)):
            dl.arc((cx - r, top - r * 0.8, cx + r, top + r * 0.8), st, en, fill=(255, 255, 255, a), width=5)
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10))); img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    hw = 140
    d.line([(cx, top), (cx - hw, base)], fill=WHITE, width=8); d.line([(cx, top), (cx + hw, base)], fill=WHITE, width=8)
    for i in range(1, 7):
        y0 = top + (base - top) * i / 7; w0 = hw * i / 7; y1 = top + (base - top) * (i + 1) / 7; w1 = hw * (i + 1) / 7
        d.line([(cx - w0, y0), (cx + w0, y0)], fill=WHITE, width=5)
        d.line([(cx - w0, y0), (cx + w1, y1)], fill=WHITE, width=4); d.line([(cx + w0, y0), (cx - w1, y1)], fill=WHITE, width=4)
    d.ellipse((cx - 22, top - 22, cx + 22, top + 22), fill=WHITE)
    q = s["quote"]
    n = int(len(q) * min(1, max(0, (t - 0.5) / 1.8)))
    if n:
        f = font(OSWALD, 62)
        box = d.textbbox((cx, 960), q, font=f, anchor="ms")
        d.rectangle((box[0] - 22, box[1] - 16, box[2] + 22, box[3] + 16), fill=(0, 0, 0))
        shadow_text(img, (box[0], 960), q[:n], f, fill=(240, 240, 240), anchor="ls")
    if s.get("header"):
        shadow_text(img, (70, 80), s["header"], font(INTER, 30), fill=CYAN, anchor="ls")
    if s.get("clock"):
        shadow_text(img, (W - 70, 100), s["clock"], font(INTER, 64), fill=(255, 215, 90), anchor="rs")
    return finish(img, grain=4, vig=False)


def f_codes(t, D, s):
    rnd = random.Random(3)
    img = Image.new("RGBA", (W, H), (8, 10, 12, 255))
    d = ImageDraw.Draw(img)
    f = font("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"
             if os.path.exists("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf") else INTER_SB, 34)
    rows, cols = 16, 9
    hot = {(7, 4)}
    for r in range(rows):
        for c in range(cols):
            x, y = 150 + c * 190, 90 + r * 58 - (t * 20) % 58
            g = f"{rnd.randint(0, 99999):05d}"
            if (r, c) in hot and t > D * 0.55:
                k = ease((t - D * 0.55) / 0.6)
                shadow_text(img, (x + 50, y + 18), "AF", font(OSWALD, 40 + 120 * k), fill=(255, 215, 90), anchor="mm")
                continue
            lit = rnd.random() < 0.1 and ((t * 3 + r + c) % 7 < 1)
            d.text((x, y), g, font=f, fill=(90, 255, 150) if lit else (70, 110, 90))
    shadow_text(img, (70, H - 60), s.get("label", "MẬT MÃ JN-25 – HẢI QUÂN NHẬT"), font(INTER, 30), fill=CYAN, anchor="ls")
    return finish(img, grain=5)


def f_clock(t, D, s):
    img = Image.new("RGBA", (W, H), (6, 7, 9, 255))
    hh, mm = map(int, s["time"].split(":"))
    sec = int(t * 1.0) % 60
    txt = f"{hh:02d}:{mm:02d}:{sec:02d}"
    k = ease(t / 0.4)
    shadow_text(img, (W / 2, H / 2 + 60), txt, font(OSWALD, 260), fill=WHITE, anchor="ms", alpha=k)
    if s.get("sub"):
        shadow_text(img, (W / 2, H / 2 + 150), s["sub"], font(INTER, 40), fill=CYAN, anchor="ms", alpha=ease((t - 0.4) / 0.5))
    return finish(img, grain=6)


def f_stat(t, D, s):
    white = s.get("bg") == "white"
    base = 235 - 30 * min(t / D, 1) if white else 12
    img = Image.new("RGBA", (W, H), (int(base), int(base), int(base) - (5 if white else 0), 255))
    if s.get("photo"):
        img = kb(s["photo"], t, D, gray=True, dark=0.62)
    lines = s["lines"]
    y = H / 2 - (len(lines) - 1) * 80
    for i, (txt, size, color) in enumerate(lines):
        k = ease((t - 0.3 - i * 0.6) / 0.7)
        col = tuple(color)
        if white:
            ImageDraw.Draw(img).text((W / 2, y), txt, font=font(OSWALD if size > 60 else INTER, size), fill=col + (int(255 * k),), anchor="mm")
        else:
            shadow_text(img, (W / 2, y), txt, font(OSWALD if size > 60 else INTER, size), fill=col, anchor="mm", alpha=k)
        y += 160
    out = finish(img, grain=8)
    if s.get("flash") and t < 0.5:
        out = Image.blend(out, Image.new("RGB", (W, H), "white"), 1 - t / 0.5)
    return out


def f_altitude(t, D, s):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    a = np.zeros((H, W, 3), np.float32)
    yy = np.linspace(0, 1, H)[:, None]
    a[:] = (np.array([30, 60, 110]) * (1 - yy) + np.array([120, 170, 210]) * yy)[:, None, :] * np.ones((1, W, 1))
    sea = int(H * 0.82)
    a[sea:] = [12, 40, 80]
    img = Image.fromarray(a.astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    for i in range(4):  # japanese carriers on the sea
        x = 1150 + i * 150
        d.polygon([(x - 60, sea - 8), (x + 60, sea - 8), (x + 50, sea + 6), (x - 50, sea + 6)], fill=(70, 70, 70))
        d.rectangle((x - 70, sea - 14, x + 66, sea - 8), fill=(170, 140, 90))
    shadow_text(img, (1380, sea + 70), "TÀU SÂN BAY NHẬT", font(INTER, 30), anchor="ms")
    for i in range(9):  # zeros near the sea, chasing
        x = (300 + i * 170 + t * 140) % (W + 200) - 100
        y = sea - 40 - (i % 3) * 25
        plane_icon(img, x, y, 0, s=0.8, color=(240, 240, 240))
    shadow_text(img, (120, sea - 130), "CHIẾN ĐẤU CƠ ZERO – SÁT MẶT BIỂN", font(INTER, 32), anchor="ls",
                alpha=ease((t - 0.8) / 0.5))
    k = ease((t - 1.6) / 0.7)
    d.line([(80, 120), (80, sea)], fill=(255, 255, 255, int(160 * k)), width=3)
    shadow_text(img, (100, 140), "~5.000 M", font(INTER, 30), anchor="ls", alpha=k)
    shadow_text(img, (W / 2, 330), "BẦU TRỜI BỎ NGỎ", font(OSWALD, 90), fill=(255, 215, 90), anchor="mm", alpha=k)
    for i in range(6):  # dauntless arriving high
        kk = ease((t - 2.4 - i * 0.15) / 1.5)
        if kk <= 0:
            continue
        x = -100 + kk * (900 + i * 60)
        plane_icon(img, x, 170 + (i % 2) * 40, 0.05, s=0.9, color=CYAN)
    if t > 2.6:
        shadow_text(img, (300, 110), "MÁY BAY NÉM BOM BỔ NHÀO MỸ", font(INTER, 30), fill=CYAN, anchor="ls",
                    alpha=ease((t - 2.6) / 0.5))
    return finish(img, grain=4)


def f_memoir(t, D, s):
    img = Image.new("RGBA", (W, H), (214, 200, 170, 255))
    a = np.asarray(img).astype(np.float32)
    rng = np.random.default_rng(1)
    a[..., :3] *= (0.85 + 0.15 * rng.random((H, W, 1)))
    img = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    f = font(INTER_SB, 40)
    lines = ["\"...chỉ cần thêm năm phút nữa,", "máy bay của chúng tôi đã kịp cất cánh", "và lịch sử có thể đã khác.\""]
    for i, l in enumerate(lines):
        d.text((260, 300 + i * 70), l, font=f, fill=(50, 40, 30))
    d.text((260, 530), "— Hồi ký của một sĩ quan Nhật (Fuchida Mitsuo)", font=font(INTER_SB, 30), fill=(90, 70, 50))
    k = ease((t - 1.8) / 0.4)
    if k > 0:
        shadow_text(img, (1500, 420), "5 PHÚT", font(OSWALD, 170), fill=(60, 50, 40), anchor="mm")
        d = ImageDraw.Draw(img)
        d.line([(1290, 470), (1290 + 420 * k, 360)], fill=RED, width=16)
    k2 = ease((t - 2.6) / 0.5)
    if k2 > 0:
        d.text((260, 720), "Các nhà sử học: KHÔNG ĐÚNG", font=font(OSWALD, 80), fill=RED + (int(255 * k2),))
    return finish(img, grain=6)


def f_sting(t, D, s):
    img = Image.new("RGBA", (W, H), (10, 10, 12, 255))
    av = Image.open(os.path.join(BRAND, "avatar-800.png")).convert("RGBA")
    # crop the circle (remove dark square corners)
    mask = Image.new("L", av.size, 0)
    ImageDraw.Draw(mask).ellipse((18, 18, av.width - 18, av.height - 18), fill=255)
    av.putalpha(mask)
    k = min(1.0, t / 0.35)
    sc = 2.4 - 1.4 * (k ** 2)                       # slams down
    size = int(460 * sc)
    a = av.resize((size, size), Image.LANCZOS)
    alpha = min(1.0, t / 0.2)
    a.putalpha(a.getchannel("A").point(lambda v: int(v * alpha)))
    shake = (random.Random(int(t * 60)).uniform(-8, 8) if 0.35 < t < 0.6 else 0)
    img.alpha_composite(a, (int(W / 2 - size / 2 + shake), int(H / 2 - size / 2 - 40 + shake)))
    k2 = ease((t - 0.8) / 0.5)
    if k2 > 0:
        shadow_text(img, (W / 2, H / 2 + 300), "NHỮNG TRẬN ĐÁNH LÀM THAY ĐỔI LỊCH SỬ", font(INTER, 38), anchor="ms", alpha=k2)
    out = finish(img, grain=8)
    if 0.33 < t < 0.5:
        out = Image.blend(out, Image.new("RGB", (W, H), "white"), 0.35 * (1 - (t - 0.33) / 0.17))
    return out


def f_end(t, D, s):
    img = Image.new("RGBA", (W, H), (10, 11, 14, 255))
    lg = Image.open(os.path.join(BRAND, "logo-ngang.png")).convert("RGBA")
    lg = lg.resize((900, int(900 * lg.height / lg.width)), Image.LANCZOS)
    k = ease(t / 0.8)
    lg.putalpha(lg.getchannel("A").point(lambda v: int(v * k)))
    img.alpha_composite(lg, (W // 2 - 450, 140))
    shadow_text(img, (W / 2, 520), "ĐĂNG KÝ KÊNH & BẬT CHUÔNG ĐỂ KHÔNG BỎ LỠ TRẬN ĐÁNH TIẾP THEO", font(INTER, 38),
                anchor="ms", alpha=ease((t - 0.6) / 0.6))
    d = ImageDraw.Draw(img)
    for i, (title, x) in enumerate((("VIDEO TIẾP THEO", 300), ("XEM THÊM", 1060))):
        kk = ease((t - 1.0 - i * 0.3) / 0.6)
        d.rounded_rectangle((x, 600, x + 560, 915), 18, outline=(255, 255, 255, int(120 * kk)), width=3)
        shadow_text(img, (x + 280, 960), title, font(INTER, 28), fill=CYAN, anchor="ms", alpha=kk)
    lines = s.get("credits", [])
    for i, l in enumerate(lines):
        shadow_text(img, (W / 2, 1010 + i * 26), l, font(INTER_SB, 20), fill=(170, 170, 170), anchor="ms",
                    alpha=ease((t - 1.5) / 0.8))
    return finish(img, grain=4, vig=False)


KINDS = {"map": f_map, "portrait": f_portrait, "portraits": f_portraits, "roster": f_roster, "keyword": f_keyword,
         "title": f_title, "telegram": f_telegram, "codes": f_codes, "clock": f_clock, "stat": f_stat,
         "altitude": f_altitude, "memoir": f_memoir, "sting": f_sting, "end": f_end}


def render(kind, D, out, spec):
    fn = KINDS[kind]
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(round(D * FPS))):
        p.stdin.write(fn(i / FPS, D, spec).convert("RGB").tobytes())
    p.stdin.close(); p.wait()


# ------------------------------------------------------------------ overlays
def subscribe_overlay(out, D=6.0):
    """Lower-third reminder (RGBA, qtrle .mov): pill with avatar, channel name, hint, red subscribe button -> clicked."""
    av = Image.open(os.path.join(BRAND, "avatar-800.png")).convert("RGBA").resize((96, 96), Image.LANCZOS)
    m = Image.new("L", (96, 96), 0); ImageDraw.Draw(m).ellipse((3, 3, 93, 93), fill=255); av.putalpha(m)
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", out], stdin=subprocess.PIPE)
    PW, PHt = 900, 124
    x0, y0 = (W - PW) // 2, H - PHt - 70
    for i in range(int(D * FPS)):
        t = i / FPS
        k_in, k_out = ease(t / 0.45), ease((D - t) / 0.45)
        k = min(k_in, k_out)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dy = int((1 - k) * 160)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rounded_rectangle((x0 + 6, y0 + dy + 8, x0 + PW + 6, y0 + PHt + dy + 8), 62, fill=(0, 0, 0, int(110 * k)))
        lay = lay.filter(ImageFilter.GaussianBlur(10))
        img.alpha_composite(lay)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x0, y0 + dy, x0 + PW, y0 + PHt + dy), 62, fill=(255, 255, 255, int(245 * k)))
        a2 = av.copy(); a2.putalpha(a2.getchannel("A").point(lambda v: int(v * k)))
        img.alpha_composite(a2, (x0 + 14, y0 + dy + 14))
        d.text((x0 + 128, y0 + dy + 22), "MẬT LỆNH", font=font(INTER, 40), fill=(20, 20, 24, int(255 * k)))
        d.text((x0 + 130, y0 + dy + 74), "Đăng ký & bật chuông để xem tập tiếp theo", font=font(INTER_SB, 22),
               fill=(90, 90, 96, int(255 * k)))
        clicked = t > 2.4
        bx0, by0, bx1, by1 = x0 + PW - 230, y0 + dy + 30, x0 + PW - 70, y0 + dy + 94
        press = 0.92 if 2.3 < t < 2.5 else 1.0
        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
        bw, bh = (bx1 - bx0) * press / 2, (by1 - by0) * press / 2
        d.rounded_rectangle((cx - bw, cy - bh, cx + bw, cy + bh), 10,
                            fill=((205, 205, 210) if clicked else (220, 30, 30)) + (int(255 * k),))
        d.text((cx, cy), "ĐÃ ĐĂNG KÝ" if clicked else "ĐĂNG KÝ", font=font(INTER, 22 if clicked else 26),
               fill=((60, 60, 66) if clicked else (255, 255, 255)) + (int(255 * k),), anchor="mm")
        # bell (rings after click)
        bxc, byc = x0 + PW - 36, y0 + dy + 62
        ang = math.sin((t - 2.6) * 30) * 25 * max(0, 1 - (t - 2.6) / 1.0) if t > 2.6 else 0
        bell = Image.new("RGBA", (60, 60), (0, 0, 0, 0)); bd = ImageDraw.Draw(bell)
        colb = ((30, 30, 34) if t > 2.6 else (150, 150, 156)) + (int(255 * k),)
        bd.pieslice((12, 8, 48, 48), 180, 360, fill=colb); bd.rectangle((12, 28, 48, 42), fill=colb)
        bd.polygon([(8, 44), (52, 44), (46, 38), (14, 38)], fill=colb); bd.ellipse((25, 44, 35, 54), fill=colb)
        bell = bell.rotate(ang, resample=Image.BICUBIC, center=(30, 10))
        img.alpha_composite(bell, (int(bxc - 30), int(byc - 30)))
        # cursor
        if 1.4 < t < 3.4:
            kc = ease((t - 1.4) / 0.8)
            px, py = W * 0.7 + (cx - W * 0.7) * kc, H * 0.95 + (cy + 10 - H * 0.95) * kc
            cur = [(px, py), (px, py + 34), (px + 9, py + 26), (px + 16, py + 40), (px + 22, py + 37), (px + 15, py + 23), (px + 27, py + 23)]
            d.polygon(cur, fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()


def logo_png(out, width=300):
    lg = Image.open(os.path.join(BRAND, "logo-ngang.png")).convert("RGBA")
    lg = lg.resize((width, int(width * lg.height / lg.width)), Image.LANCZOS)
    lg.putalpha(lg.getchannel("A").point(lambda v: int(v * 0.88)))
    sh = Image.new("RGBA", (lg.width + 20, lg.height + 20), (0, 0, 0, 0))
    blk = Image.new("RGBA", lg.size, (0, 0, 0, 255)); blk.putalpha(lg.getchannel("A").point(lambda v: int(v * 0.6)))
    sh.alpha_composite(blk, (12, 12)); sh = sh.filter(ImageFilter.GaussianBlur(5)); sh.alpha_composite(lg, (10, 10))
    sh.save(out)


# ------------------------------------------------------------------ Dien Bien Phu additions
from valley import Valley


def gun_icon(img, x, y, ang, s=1.0, alpha=1.0, color=(255, 215, 90)):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    c = color + (int(255 * alpha),)
    ca, sa = math.cos(ang), math.sin(ang)
    d.line([(x, y), (x + 46 * s * ca, y + 46 * s * sa)], fill=c, width=int(9 * s))
    d.ellipse((x - 14 * s, y - 14 * s, x + 14 * s, y + 14 * s), fill=c, outline=(0, 0, 0, int(200 * alpha)), width=3)
    img.alpha_composite(lay)


def f_valley(t, D, s):
    v = Valley(tuple(s["view0"]), tuple(s.get("view1", s["view0"])), W, H)
    img = v.frame(min(t / D, 1))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rectangle((0, 0, W, H), fill=(0, 0, 0, 60))
    img.alpha_composite(lay)
    for it in s.get("items", []):
        k = (t - it.get("t", 0)) / it.get("fade", 0.5)
        if k <= 0:
            continue
        a = ease(k); ty = it["type"]
        if ty == "pt":
            x, y = v.P(it["at"])
            col = COL.get(it.get("color", "red"))
            r = 16 * (0.6 + 0.4 * back(k))
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            d.ellipse((x - r * 2.2, y - r * 2.2, x + r * 2.2, y + r * 2.2), outline=col + (int(160 * a),), width=4)
            d.ellipse((x - r, y - r, x + r, y + r), fill=col + (int(255 * a),), outline=(0, 0, 0, int(220 * a)), width=3)
            img.alpha_composite(lay)
            if it.get("label"):
                anc = it.get("anchor", "l")
                dx = {"l": 44, "r": -44, "m": 0}[anc]; dy = 70 if anc == "m" else -8
                label2(img, x + dx, y + dy, it.get("sub", ""), it["label"], alpha=a, size=it.get("size", 44), anchor=anc)
        elif ty == "x":
            x, y = v.P(it["at"]); r = 34 * (1.4 - 0.4 * ease(k))
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            c = (255, 60, 50, int(255 * a))
            d.line([(x - r, y - r), (x + r, y + r)], fill=c, width=12); d.line([(x - r, y + r), (x + r, y - r)], fill=c, width=12)
            img.alpha_composite(lay)
        elif ty == "arrow":
            pts = [v.P(p) for p in it["path"]]
            path_arrow(img, pts, min(1, (t - it["t"]) / it.get("dur", 1.5)), color=COL.get(it.get("color", "yellow")),
                       width=it.get("w", 8), alpha=a, dashed=it.get("dashed", False))
        elif ty == "guns":
            for j, g in enumerate(it["at"]):
                kk = (t - it["t"] - j * it.get("stagger", 0.15)) / 0.4
                if kk <= 0:
                    continue
                x, y = v.P(g)
                tx, ty2 = v.P(it.get("aim", "hq"))
                ang = math.atan2(ty2 - y, tx - x)
                gun_icon(img, x, y, ang, s=it.get("s", 1.0), alpha=ease(kk))
                if it.get("fire") and t > it["fire"] + j * 0.08:
                    ph_ = ((t - it["fire"] - j * 0.08) % 1.6) / 1.6
                    if ph_ < 0.5:
                        q = ph_ / 0.5
                        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
                        px_, py_ = x + (tx - x) * q, y + (ty2 - y) * q
                        d.line([(x + (tx - x) * max(0, q - 0.12), y + (ty2 - y) * max(0, q - 0.12)), (px_, py_)],
                               fill=(255, 200, 90, 220), width=5)
                        img.alpha_composite(lay)
        elif ty == "ring":
            k2 = ease(min(1, max(0, (t - it["t"]) / it.get("dur", 3))))
            r = it["r0"] + (it["r1"] - it["r0"]) * k2
            cx, cy = v.P(it.get("at", "hq")); rp = r * v.ppk
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            n = 72
            for j in range(0, n, 2):
                a0, a1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
                d.line([(cx + rp * math.cos(a0), cy + rp * 1.25 * math.sin(a0)), (cx + rp * math.cos(a1), cy + rp * 1.25 * math.sin(a1))],
                       fill=(255, 215, 90, int(230 * a)), width=8)
            img.alpha_composite(lay)
        elif ty == "tag":
            x, y = v.P(it["at"]); tag_box(img, x, y + it.get("dy", 0), it["text"], alpha=a, size=it.get("size", 30))
        elif ty == "title":
            shadow_text(img, (W / 2, 120), it["text"], font(OSWALD, 76), anchor="mm", alpha=a)
            if it.get("sub"):
                shadow_text(img, (W / 2, 190), it["sub"], font(INTER, 32), fill=CYAN, anchor="mm", alpha=a)
    shadow_text(img, (W - 40, H - 36), "SƠ ĐỒ MINH HỌA", font(INTER_SB, 24), fill=(200, 200, 200), anchor="rs", alpha=0.8)
    return finish(img, grain=5)


def f_quote(t, D, s):
    img = kb(s["photo"], t, D, gray=True, dark=0.7) if s.get("photo") else grid_bg(t)
    lines = s["lines"]
    y0 = H / 2 - (len(lines) - 1) * 50 - 30
    for i, l in enumerate(lines):
        shadow_text(img, (W / 2, y0 + i * 100), l, font(INTER, s.get("size", 64)), fill=WHITE, anchor="mm",
                    alpha=ease((t - 0.3 - i * 0.5) / 0.6))
    if s.get("by"):
        shadow_text(img, (W / 2, y0 + len(lines) * 100 + 30), s["by"], font(INTER_SB, 36), fill=(255, 215, 90),
                    anchor="mm", alpha=ease((t - 0.6 - len(lines) * 0.5) / 0.6))
    return finish(img, grain=7)


def f_phrase(t, D, s):
    """Big phrase card (e.g. a doctrine) over a dark photo."""
    img = kb(s["photo"], t, D, gray=True, dark=0.6) if s.get("photo") else grid_bg(t)
    k = ease(t / 0.4)
    f = font(OSWALD, s.get("size", 130) * (1.15 - 0.15 * k))
    col = tuple(s.get("color", (255, 215, 90)))
    shadow_text(img, (W / 2, H / 2), s["text"], f, fill=col, anchor="mm", alpha=k)
    if s.get("strike") is not None and t > s["strike"]:
        kk = ease((t - s["strike"]) / 0.4)
        bb = ImageDraw.Draw(img).textbbox((W / 2, H / 2), s["text"], font=font(OSWALD, s.get("size", 130)), anchor="mm")
        ImageDraw.Draw(img).line([(bb[0] - 20, H / 2 + 10), (bb[0] - 20 + (bb[2] - bb[0] + 40) * kk, H / 2 - 10)], fill=RED, width=14)
    if s.get("sub"):
        shadow_text(img, (W / 2, H / 2 + 130), s["sub"], font(INTER, 40), fill=WHITE, anchor="mm", alpha=ease((t - 0.6) / 0.5))
    return finish(img, grain=8)


KINDS.update({"valley": f_valley, "quote": f_quote, "phrase": f_phrase})


if __name__ == "__main__":
    k = sys.argv[1]
    if k == "subscribe":
        subscribe_overlay(sys.argv[2])
    elif k == "logo":
        logo_png(sys.argv[2])
    elif k == "still":
        _, _, kind, tt, D, out, spec = sys.argv
        KINDS[kind](float(tt), float(D), json.loads(spec)).convert("RGB").save(out)
    else:
        render(k, float(sys.argv[2]), sys.argv[3], json.loads(sys.argv[4]) if len(sys.argv) > 4 else {})


