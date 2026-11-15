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
    headline(im, [("HẠ GỤC", WHITE), ("9 MÁY BAY MỸ", YEL)])
    tag(im, 640, 690, "CHIM CẮT SỐ 2 – THẤY LÀ PHẢI SỢ", bg=(220, 20, 30), fg=WHITE, size=64)
    im.save("thumb-coc-B.jpg", quality=93)
