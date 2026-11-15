import sys
sys.path.insert(0, ".")
from tc import base, headline, tag, W, H, YEL, WHITE
from hr_thumb import us_pin
v = sys.argv[1]
if v == "a":
    im = base("a950.png", (0, 0, 474, 266))
    us_pin(im, 420, 420, r=40); us_pin(im, 960, 330, r=44)
    headline(im, [("CHIM CẮT", WHITE), ("SỐ 2...", YEL)])
    tag(im, 640, 690, "1 PHI CÔNG VIỆT NAM · 9 MÁY BAY MỸ", bg=YEL, size=64)
    im.save("thumb-coc-A.jpg", quality=93)
else:
    im = base("../coc/photos/mig4324.jpg", (0, 50, 1012, 619))
    from PIL import ImageDraw, ImageFont
    from tc import FONT
    d = ImageDraw.Draw(im); f = ImageFont.truetype(FONT, 88); t = "CHIM CẮT SỐ 2 – THẤY LÀ PHẢI SỢ"
    w = d.textlength(t, font=f)
    d.rectangle([640 - w / 2 - 14, 40, 640 + w / 2 + 14, 166], fill=(220, 20, 30), outline=(0, 0, 0), width=4)
    a = "CHIM CẮT SỐ 2 – "; x0 = 640 - w / 2
    d.text((x0, 48), a, font=f, fill=WHITE)
    d.text((x0 + d.textlength(a, font=f), 48), "THẤY LÀ PHẢI SỢ", font=f, fill=YEL)
    im.save("thumb-coc-B.jpg", quality=93)
