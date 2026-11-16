"""Thumbnail Pol Pot kiểu Trạm Cuối. Chạy trong thư mục có tc.py; ảnh nguồn ở ../pp/photos."""
import sys
sys.path.insert(0, ".")
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from tc import base, headline, tag, W, H, YEL, WHITE
PH = "../pp/photos/"


def fit(path, w, h, cx=0.5, cy=0.5):
    im = Image.open(path).convert("RGB")
    s = max(w / im.width, h / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = int((im.width - w) * cx); y = int((im.height - h) * cy)
    return im.crop((x, y, x + w, y + h))


def comp(left, right, split, out, lc=(0.5, 0.3), rc=(0.5, 0.5), gray_left=True):
    c = Image.new("RGB", (W, H))
    src = Image.open(PH + left).convert("RGB")
    sc = split / src.width * 1.25
    src = src.resize((round(src.width * sc), round(src.height * sc)), Image.LANCZOS)
    L = Image.new("RGB", (split, H), (0, 0, 0))
    L.paste(src, ((split - src.width) // 2, 175))
    if gray_left:
        L = ImageEnhance.Color(L).enhance(0.0)
    c.paste(L, (0, 0))
    c.paste(fit(PH + right, W - split, H, *rc), (split, 0))
    d = ImageDraw.Draw(c); d.line([(split, 0), (split, H)], fill=(220, 20, 30), width=10)
    c.save(out, quality=95)


v = sys.argv[1]
if v == "a":
    comp("polpot.jpg", "stupa.jpg", 560, "_a.jpg", lc=(0.5, 0.25), rc=(0.5, 0.62))
    im = base("_a.jpg")
    headline(im, [("KẺ GIẾT", WHITE), ("1/4 DÂN SỐ", YEL)])
    tag(im, 640, 690, "POL POT – CAMPUCHIA 1975–1979", bg=(220, 20, 30), fg=WHITE, size=60)
    im.save("thumb-polpot-A.jpg", quality=93)
else:
    comp("polpot.jpg", "ts_cells.jpg", 560, "_b.jpg", lc=(0.5, 0.25), rc=(0.5, 0.5))
    im = base("_b.jpg")
    headline(im, [("THẦY GIÁO", WHITE), ("HIỀN LÀNH?", YEL)])
    tag(im, 640, 690, "1,7 TRIỆU NGƯỜI CHẾT TRONG 4 NĂM", bg=(220, 20, 30), fg=WHITE, size=60)
    im.save("thumb-polpot-B.jpg", quality=93)
