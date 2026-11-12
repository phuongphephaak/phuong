"""Thumbnail kiểu Trạm Cuối: 1 dòng chữ to (trắng + vàng), viền đen, dải tối phía trên, ảnh chính bão hoà mạnh."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
FONT = "/home/user/phuong/video/brand/fonts/BarlowCondensed-ExtraBold.ttf"
W, H = 1280, 720
YEL, WHITE = (255, 230, 0), (255, 255, 255)

def base(path, crop=None):
    im = Image.open(path).convert("RGB")
    if crop: im = im.crop(crop)
    im = im.resize((W, H), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(1.35); im = ImageEnhance.Contrast(im).enhance(1.2)
    im = im.filter(ImageFilter.UnsharpMask(2, 120, 2))
    # dải tối trên cùng
    g = Image.new("L", (W, H)); d = ImageDraw.Draw(g)
    for y in range(260): d.line([(0, y), (W, y)], fill=int(235 * (1 - y / 260) ** 1.6))
    im.paste((0, 0, 0), (0, 0), g)
    return im

def headline(im, parts, y=18, maxw=1220):
    d = ImageDraw.Draw(im); size = 200
    while True:
        f = ImageFont.truetype(FONT, size); gap = size * 0.22
        ws = [d.textlength(t, font=f) for t, _ in parts]
        tot = sum(ws) + gap * (len(parts) - 1)
        if tot <= maxw or size < 60: break
        size -= 4
    x = (W - tot) / 2; sw = max(6, size // 18)
    for (t, col), w in zip(parts, ws):
        # bóng đổ
        d.text((x + 6, y + 8), t, font=f, fill=(0, 0, 0), stroke_width=sw, stroke_fill=(0, 0, 0))
        d.text((x, y), t, font=f, fill=col, stroke_width=sw, stroke_fill=(0, 0, 0))
        x += w + gap

def jp_pin(im, x, y, r=34):
    d = ImageDraw.Draw(im)
    d.polygon([(x - r * 0.55, y - r * 0.4), (x + r * 0.55, y - r * 0.4), (x, y + r * 0.9)], fill=WHITE, outline=(0, 0, 0))
    d.ellipse([x - r, y - 2 * r, x + r, y], fill=WHITE, outline=(0, 0, 0), width=3)
    d.ellipse([x - r * 0.45, y - r * 1.45, x + r * 0.45, y - r * 0.55], fill=(200, 16, 36))
    return y - 2 * r

def tag(im, x, y, text, bg=YEL, fg=(0, 0, 0), size=40):
    d = ImageDraw.Draw(im); f = ImageFont.truetype(FONT, size)
    w = d.textlength(text, font=f); pad = 10
    d.rectangle([x - w / 2 - pad, y - size - 6, x + w / 2 + pad, y + 4], fill=bg, outline=(0, 0, 0), width=3)
    d.text((x - w / 2, y - size - 4), text, font=f, fill=fg)

if __name__ == "__main__":
    src, out, variant = sys.argv[1], sys.argv[2], sys.argv[3]
    C=(100, 60, 100 + 1700, 60 + 956)
    im = base(src, C)
    sx, sy = W / 1700, H / 956
    ships = [(190, 705, "SORYU"), (930, 700, "AKAGI"), (1630, 700, "KAGA")]
    for x, y, n in ships:
        X, Y = (x - C[0]) * sx, (y - C[1]) * sy - 20
        top = jp_pin(im, X, Y)
        tag(im, X, top - 8, n)
    if variant == "a":
        headline(im, [("ĐÁNH ÚP", WHITE), ("HẠM ĐỘI NHẬT", YEL)])
    else:
        headline(im, [("6 PHÚT", WHITE), ("ĐỊNH MỆNH...", YEL)])
    im.save(out, quality=93)
