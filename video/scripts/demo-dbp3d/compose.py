"""Ghép đoạn demo 30s: python3 compose.py out.mp4"""
import json, math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(HERE)
W, H, FPS = 1920, 1080, 30
PH = os.path.join(S, "dbp", "photos")
OSWALD = os.path.join(S, "gfx", "oswald-700.ttf")
INTER = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
SERIF_B = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
SERIF_I = "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"
SERIF = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
_fc = {}
def F(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]
ease = lambda x: 0 if x <= 0 else 1 if x >= 1 else x * x * (3 - 2 * x)
LAB = json.load(open(os.path.join(HERE, "labels3.json")))
LOGO = Image.open(os.path.join(HERE, "logo.png")).convert("RGBA")
rnd = random.Random(5)

SEGS = [("globe", 0.0, 6.4), ("A", 6.4, 15.4), ("B", 15.4, 21.4), ("C", 21.4, 27.4),
        ("photo", 27.4, 30.4), ("giap", 30.4, 33.4), ("end", 33.4, 36.0)]
sys.path.insert(0, HERE)
from globe import globe_frame
SHOT0 = {"A": 1, "B": 271, "C": 451}
XF = 0.35  # crossfade seconds


def text_sp(d, xy, s, f, fill, sp=0, anchor="la"):
    """letter-spaced text"""
    if sp == 0:
        d.text(xy, s, font=f, fill=fill, anchor=anchor); return
    wsum = sum(d.textlength(c, font=f) for c in s) + sp * (len(s) - 1)
    x, y = xy
    if anchor[0] == "m": x -= wsum / 2
    elif anchor[0] == "r": x -= wsum
    for c in s:
        d.text((x, y), c, font=f, fill=fill, anchor="l" + anchor[1]); x += d.textlength(c, font=f) + sp


def shadow(img, fn, blur=6, off=(0, 3), alpha=200):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); fn(ImageDraw.Draw(lay), (0, 0, 0, alpha))
    lay = lay.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(lay, off)
    top = Image.new("RGBA", img.size, (0, 0, 0, 0)); fn(ImageDraw.Draw(top), None); img.alpha_composite(top)


def with_alpha(layer, a):
    if a >= 1: return layer
    l = layer.copy(); l.putalpha(l.getchannel("A").point(lambda v: int(v * a))); return l


# ---------------- reusable look: grade / grain / vignette ----------------
VIG = None
def vignette(arr, strength=0.55):
    global VIG
    if VIG is None:
        y, x = np.mgrid[0:H, 0:W]; r = np.hypot((x - W / 2) / (W / 2), (y - H / 2) / (H / 2))
        VIG = (1 - strength * np.clip(r - 0.35, 0, 1) ** 1.6)[..., None].astype(np.float32)
    return arr * VIG

GRAIN = [np.random.default_rng(i).normal(0, 1, (H // 2, W // 2)).astype(np.float32) for i in range(8)]
def grain(arr, amt, i):
    g = GRAIN[i % 8]; g = np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]
    return arr + g * amt


def sepia(im, warm=1.0):
    g = ImageOps.grayscale(im)
    a = np.asarray(g).astype(np.float32)[..., None] / 255
    tint = np.array([1.0, 0.88, 0.70]) * warm + np.array([1, 1, 1]) * (1 - warm)
    return Image.fromarray(np.clip(a * tint * 255, 0, 255).astype(np.uint8))


def cover(im, w, h, zoom=1.0, cx=0.5, cy=0.5):
    s = max(w / im.width, h / im.height) * zoom
    im2 = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    x = int((im2.width - w) * cx); y = int((im2.height - h) * cy)
    return im2.crop((x, y, x + w, y + h))


# ---------------- date badge (khung viền kép, góc dưới phải) ----------------
def date_badge(img, s, a=1.0):
    f = F(SERIF_B, 44); d0 = ImageDraw.Draw(img); tw = d0.textlength(s, font=f) + 8 * len(s)
    w, h = int(tw + 56), 74; x, y = W - w - 60, H - h - 56
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle((x, y, x + w, y + h), fill=(10, 10, 10, 215))
    d.rectangle((x + 5, y + 5, x + w - 5, y + h - 5), outline=(235, 225, 200, 255), width=2)
    d.rectangle((x + 10, y + 10, x + w - 10, y + h - 10), outline=(235, 225, 200, 120), width=1)
    text_sp(d, (x + w / 2, y + h / 2 + 2), s, f, (240, 232, 210, 255), 8, "mm")
    img.alpha_composite(with_alpha(lay, a))


def tag(img, x, y, s, sub=None, a=1.0, bar=(200, 30, 30)):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = F(OSWALD, 40); tw = d.textlength(s, font=f)
    d.rectangle((x, y, x + 8, y + (92 if sub else 54)), fill=(*bar, 255))
    def draw(dd, sh):
        dd.text((x + 24, y + 4), s, font=f, fill=sh or (255, 255, 255, 255))
        if sub: text_sp(dd, (x + 26, y + 60), sub, F(INTER, 22), sh or (225, 215, 190, 255), 2)
    shadow(lay, draw, 8, (0, 3), 230)
    img.alpha_composite(with_alpha(lay, a))


def callout(img, px, py, l1, l2, a=1.0):
    """hộp chú thích đen có mũi nhọn (kiểu Epic History)"""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f1, f2 = F(SERIF_B, 38), F(SERIF_B, 28)
    w = int(max(d.textlength(l1, font=f1) + 4 * len(l1), d.textlength(l2, font=f2)) + 60); h = 100
    x0, y0 = int(px - w / 2), int(py - h - 70)
    d.rounded_rectangle((x0 + 4, y0 + 6, x0 + w + 4, y0 + h + 6), 14, fill=(0, 0, 0, 120))
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 14, fill=(14, 14, 14, 235), outline=(230, 225, 210, 255), width=3)
    d.polygon([(px - 18, y0 + h - 2), (px + 18, y0 + h - 2), (px, y0 + h + 30)], fill=(14, 14, 14, 235))
    d.line([(px - 18, y0 + h), (px, y0 + h + 30), (px + 18, y0 + h)], fill=(230, 225, 210, 255), width=3)
    d.line([(px, y0 + h + 30), (px, py)], fill=(230, 225, 210, 200), width=2)
    d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)
    text_sp(d, (x0 + w / 2, y0 + 38), l1, f1, (255, 255, 255, 255), 4, "mm")
    d.text((x0 + w / 2, y0 + 76), l2, font=f2, fill=(230, 210, 160, 255), anchor="mm")
    img.alpha_composite(with_alpha(lay, a))


def place_label(img, px, py, s, a):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    f = F(INTER, 40)          # nhãn kiểu Verdun: chữ trắng đậm lớn, bóng mềm, không chấm
    def draw(dd, sh):
        text_sp(dd, (px, py - 20), s, f, sh or (255, 255, 255, 255), 3, "md")
    shadow(lay, draw, 7, (0, 3), 235)
    img.alpha_composite(with_alpha(lay, a))


def finish(img, t, i, logo=True):
    if logo:
        img.alpha_composite(LOGO, (36, 28))
    return img


# ---------------- projector / cinema frame (khung theo thời đại) ----------------
def cinema_bg():
    p = os.path.join(HERE, "cinema_bg.png")
    if os.path.exists(p): return Image.open(p).convert("RGB")
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W, 3), np.float32) + np.array([14, 10, 9])
    # red curtains with folds
    for side in (0, 1):
        xx = x if side == 0 else (W - 1 - x)
        m = (xx < 300).astype(np.float32)
        fold = 0.55 + 0.45 * np.sin(xx / 300 * 2 * math.pi * 3.2 + 0.3 * np.sin(y / 120)) ** 2
        shade = np.clip(1 - xx / 330, 0.2, 1)
        base = base * (1 - m[..., None]) + m[..., None] * (np.array([120, 14, 16]) * fold[..., None] * (0.35 + 0.65 * shade[..., None]))
    top = (y < 70).astype(np.float32)[..., None]
    fold = 0.6 + 0.4 * np.sin(x / 40) ** 2
    base = base * (1 - top) + top * np.array([105, 12, 14]) * fold[..., None]
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    im.save(p); return im


def heads_layer():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); r = random.Random(2)
    for i in range(9):
        cx = 120 + i * 215 + r.randint(-40, 40); hy = H - r.randint(70, 140); s = r.uniform(0.85, 1.2)
        d.ellipse((cx - 62 * s, hy - 80 * s, cx + 62 * s, hy + 70 * s), fill=(4, 4, 5, 255))
        d.rounded_rectangle((cx - 160 * s, hy + 40 * s, cx + 160 * s, H + 200), int(90 * s), fill=(4, 4, 5, 255))
    return lay.filter(ImageFilter.GaussianBlur(3))


CIN = None; HEADS = None
SCR = (330, 100, 1590, 830)   # màn chiếu


def proj(photo, t, dur, i, zoom0=1.0, zoom1=1.08, cx=0.5, cy=0.5):
    global CIN, HEADS
    if CIN is None: CIN = cinema_bg(); HEADS = heads_layer()
    x0, y0, x1, y1 = SCR; sw, sh = x1 - x0, y1 - y0
    k = t / dur
    ph = sepia(Image.open(os.path.join(PH, photo)).convert("RGB"), 0.9)
    pic = cover(ph, sw, sh, zoom0 + (zoom1 - zoom0) * k, cx, cy)
    a = np.asarray(pic).astype(np.float32)
    fl = 1.0 + 0.07 * math.sin(i * 2.1) * rnd.random()
    a = a * fl
    yy, xx = np.mgrid[0:sh, 0:sw]; r = np.hypot((xx - sw / 2) / (sw / 2), (yy - sh / 2) / (sh / 2))
    a = a * (1 - 0.6 * np.clip(r - 0.5, 0, 1))[..., None]
    a = grain(np.pad(a, ((0, H - sh), (0, W - sw), (0, 0))), 10, i)[:sh, :sw]
    if rnd.random() < 0.25:   # vết xước phim
        sx = rnd.randint(0, sw - 2); a[:, sx:sx + 2] = a[:, sx:sx + 2] * 0.6 + 90
    pic = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    img = CIN.copy()
    # ánh sáng hắt từ màn chiếu
    glow = Image.new("RGB", (W, H), (0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.rectangle((x0 - 60, y0 - 40, x1 + 60, y1 + 80), fill=tuple(int(v * 0.35 * fl) for v in (200, 180, 150)))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    img = Image.fromarray(np.clip(np.asarray(img).astype(np.int16) + np.asarray(glow), 0, 255).astype(np.uint8))
    jx, jy = rnd.randint(-2, 2), rnd.randint(-2, 2)
    img.paste(pic, (x0 + jx, y0 + jy))
    img = img.convert("RGBA"); img.alpha_composite(HEADS)
    return img


def archive(photo, t, dur, i, zoom0=1.0, zoom1=1.08, cx=0.5, cy=0.5):
    """ảnh tư liệu toàn khung: Ken Burns + sepia + hạt phim + vết xước (không khung rạp)"""
    k = t / dur
    ph = sepia(Image.open(os.path.join(PH, photo)).convert("RGB"), 0.85)
    pic = cover(ph, W, H, zoom0 + (zoom1 - zoom0) * ease(k), cx, cy)
    a = np.asarray(pic).astype(np.float32) * (1.0 + 0.04 * math.sin(i * 2.1) * rnd.random())
    a = grain(vignette(a, 0.75), 9, i)
    if rnd.random() < 0.3:
        sx = rnd.randint(0, W - 3); a[:, sx:sx + 2] = a[:, sx:sx + 2] * 0.6 + 80
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def legend(img, a=1.0):
    if a <= 0: return
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = F(INTER, 22); rows = [((40, 100, 220), "QUÂN ĐỘI NHÂN DÂN VIỆT NAM"), ((200, 25, 30), "QUÂN PHÁP")]
    w = int(max(d.textlength(s, font=f) + 2 * len(s) for _, s in rows) + 90); h = 32 + 44 * len(rows)
    x0, y0 = W - w - 50, 40
    d.rectangle((x0, y0, x0 + w, y0 + h), fill=(12, 12, 12, 200)); d.rectangle((x0 + 5, y0 + 5, x0 + w - 5, y0 + h - 5), outline=(235, 225, 200, 160), width=1)
    for j, (c, s) in enumerate(rows):
        cy = y0 + 38 + 44 * j
        d.ellipse((x0 + 24, cy - 13, x0 + 50, cy + 13), fill=(*c, 255), outline=(255, 255, 255, 230), width=2)
        text_sp(d, (x0 + 66, cy), s, f, (240, 235, 220, 255), 2, "lm")
    img.alpha_composite(with_alpha(lay, a))


# ---------------- segments ----------------
def frame_3d(shot, t):
    f = min(SHOT0[shot] + int(round(t * FPS)), {"A": 270, "B": 450, "C": 630}[shot])
    p = os.path.join(HERE, "frames3", f"f_{f:04d}.jpg")
    im = Image.open(p).convert("RGB")
    if im.size != (W, H): im = im.resize((W, H), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(1.2, 40, 2))
    return im, f


def seg_render(name, t, dur, i):
    if name == "globe":
        img = globe_frame(t, dur)
        a = grain(np.asarray(img.convert("RGB")).astype(np.float32), 4, i)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        date_badge(img, "13 · 03 · 1954", ease((t - 0.8) / 0.5))
        return img
    if name == "proj1":
        img = proj("dbp002.jpg", t, dur, i, 1.0, 1.1, 0.5, 0.45)
        s = "13 · 03 · 1954"; n = int(min(len(s), max(0, (t - 0.3) / 0.07)))
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        def draw(dd, sh):
            text_sp(dd, (W / 2, 470), s[:n], F(SERIF_B, 120), sh or (245, 238, 220, 255), 10, "mm")
            if t > 1.6:
                text_sp(dd, (W / 2, 575), "ĐIỆN BIÊN PHỦ", F(INTER, 34), sh or (230, 200, 140, int(255 * ease((t - 1.6) / 0.5))), 12, "mm")
        shadow(lay, draw, 10, (0, 4), 255)
        img.alpha_composite(with_alpha(lay, 1 - ease((t - 3.0) / 0.5)))
        return img
    if name in "ABC":
        im, f = frame_3d(name, t)
        a = np.asarray(im).astype(np.float32) * np.array([1.04, 1.0, 0.94])
        a = grain(vignette(a, 0.45), 3, i)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        lab = LAB[str(f)]
        if name == "A":
            for j, (k, s) in enumerate([("hq", "MƯỜNG THANH"), ("himlam", "HIM LAM"), ("doclap", "ĐỘC LẬP"),
                                        ("bankeo", "BẢN KÉO"), ("a1", "ĐỒI A1"), ("isabelle", "HỒNG CÚM")]):
                x, y, z = lab[k]
                if z > 0 and 0.03 < x < 0.97 and 0.05 < y < 0.95 and not (x < 0.42 and y < 0.5 and 2.7 < t < 8.3):
                    place_label(img, x * W, y * H, s, ease((t - 1.0 - 0.25 * j) / 0.5) * (1 - ease((t - 8.4) / 0.4)))
            ka = ease((t - 3.2) / 0.5) * (1 - ease((t - 7.8) / 0.5))
            if ka > 0:
                lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
                def draw(dd, sh):
                    dd.text((110, 210), "49", font=F(OSWALD, 190), fill=sh or (255, 255, 255, 255))
                    dd.text((330, 250), "CỨ ĐIỂM", font=F(OSWALD, 86), fill=sh or (255, 255, 255, 255))
                    text_sp(dd, (118, 440), "TẬP ĐOÀN CỨ ĐIỂM CỦA PHÁP", F(INTER, 28), sh or (255, 125, 110, 255), 4)
                shadow(lay, draw, 12, (0, 4), 255); img.alpha_composite(with_alpha(lay, ka))
            date_badge(img, "11 · 1953 – 03 · 1954", ease(t / 0.5))
        elif name == "B":
            tag(img, 90, 760, "VÒNG VÂY", "PHÁO BINH QĐND VIỆT NAM TRÊN CÁC ĐỈNH NÚI", ease((t - 1.0) / 0.5) * (1 - ease((t - 5.5) / 0.4)), (40, 100, 220))
            date_badge(img, "13 · 03 · 1954")
        else:
            x, y, z = lab["himlam"]
            callout(img, x * W, y * H, "CỨ ĐIỂM HIM LAM", "Mục tiêu đầu tiên · 17:05", ease((t - 0.6) / 0.5))
            date_badge(img, "13 · 03 · 1954   17:05")
        legend(img, ease((t - 0.3) / 0.5))
        # trung thực: đây là sa bàn mô phỏng
        d = ImageDraw.Draw(img); text_sp(d, (60, H - 50), "SA BÀN MÔ PHỎNG", F(INTER, 20), (235, 230, 215, 170), 4, "ls")
        return img
    if name == "photo":
        img = archive("xungphong.jpg", t, dur, i, 1.0, 1.12, 0.5, 0.5)
        tag(img, 110, 820, "HIM LAM", "ĐÊM 13/03/1954 · CỨ ĐIỂM ĐẦU TIÊN THẤT THỦ", ease((t - 0.4) / 0.4), (200, 30, 30))
        return img
    if name == "giap":
        k = t / dur
        bg = Image.new("RGB", (W, H), (90, 8, 10)); bd = ImageDraw.Draw(bg)
        cx, cy, R, r = 1380 - 60 * k, 430, 330, 130   # ngôi sao lớn mờ phía sau (parallax chậm)
        pts = [(cx + (R if j % 2 == 0 else r) * math.sin(j * math.pi / 5), cy - (R if j % 2 == 0 else r) * math.cos(j * math.pi / 5)) for j in range(10)]
        bd.polygon(pts, fill=(200, 150, 30))
        for j in range(7): bd.rectangle((j * 300 - 40 * k * 3, 0, j * 300 + 22 - 40 * k * 3, H), fill=(70, 5, 8))
        bg = bg.filter(ImageFilter.GaussianBlur(28))
        a = np.asarray(bg).astype(np.float32); a = vignette(a, 0.9)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        cut = Image.open(os.path.join(HERE, "giap_cut.png")).convert("RGBA")
        g = sepia(cut.convert("RGB"), 0.5).convert("RGBA"); g.putalpha(cut.getchannel("A"))
        sc = 1080 * (1.02 + 0.06 * k) / cut.height
        g = g.resize((int(cut.width * sc), int(cut.height * sc)), Image.LANCZOS)
        img.alpha_composite(g, (int(1480 - g.width / 2 + 30 * k), H - g.height + 40))
        tag(img, 110, 700, "VÕ NGUYÊN GIÁP", "ĐẠI TƯỚNG · TỔNG TƯ LỆNH CHIẾN DỊCH", ease((t - 0.2) / 0.4), (230, 180, 40))
        qa = ease((t - 0.6) / 0.6)
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        def draw(dd, sh):
            dd.text((110, 330), "“Đánh chắc,", font=F(SERIF_I, 96), fill=sh or (250, 240, 215, 255))
            dd.text((190, 450), "tiến chắc.”", font=F(SERIF_I, 96), fill=sh or (250, 240, 215, 255))
        shadow(lay, draw, 10, (0, 4), 255); img.alpha_composite(with_alpha(lay, qa))
        return img
    if name == "end":
        k = t / dur
        ph = sepia(Image.open(os.path.join(PH, "vittoria.jpg")).convert("RGB"), 0.8)
        bg = cover(ph, W, H, 1.05 + 0.05 * k, 0.5, 0.4).filter(ImageFilter.GaussianBlur(3))
        a = np.asarray(bg).astype(np.float32) * 0.42; a = grain(vignette(a, 0.8), 6, i)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        def draw(dd, sh):
            text_sp(dd, (W / 2, 500), "ĐIỆN BIÊN PHỦ", F(SERIF_B, 150), sh or (250, 242, 222, 255), 14, "mm")
            if not sh:
                dd.line([(W / 2 - 420, 600), (W / 2 + 420, 600)], fill=(200, 40, 40, 255), width=3)
            text_sp(dd, (W / 2, 650), "56 NGÀY ĐÊM  ·  13/03 – 07/05/1954", F(INTER, 34), sh or (230, 205, 150, 255), 6, "mm")
        shadow(lay, draw, 12, (0, 4), 255)
        img.alpha_composite(with_alpha(lay, ease((t - 0.2) / 0.7)))
        return img


def render_frame(i):
    t = i / FPS
    act = [(n, s, e) for (n, s, e) in SEGS if s - XF / 2 <= t < e + XF / 2]
    out = None
    for (n, s, e) in act:
        lt = min(max(t - s, 0), e - s - 1e-3)
        im = seg_render(n, lt, e - s, i).convert("RGB")
        w = 1.0
        if len(act) > 1:
            w = ease((t - (s - XF / 2)) / XF) if t < s + XF / 2 else 1 - ease((t - (e - XF / 2)) / XF)
        out = im if out is None else Image.blend(out, im, w if t < s + XF / 2 else 1 - w) if False else (Image.blend(out, im, w))
    out = out.convert("RGBA")
    return finish(out, t, i, logo=t < SEGS[-1][1]).convert("RGB")


if __name__ == "__main__":
    out = sys.argv[1]
    if len(sys.argv) > 2:      # preview frames: compose.py out.jpg t1 t2 ...
        for tt in sys.argv[2:]:
            render_frame(int(float(tt) * FPS)).save(out.replace(".jpg", f"_{tt}.jpg"), quality=90)
        sys.exit()
    n = int(SEGS[-1][2] * FPS)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(render_frame(i).tobytes())
        if i % 60 == 0: print(i, flush=True)
    p.stdin.close(); p.wait()
