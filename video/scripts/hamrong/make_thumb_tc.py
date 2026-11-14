import sys, math
sys.path.insert(0, ".")
from tc import base, headline, tag, W, H, YEL, WHITE
from PIL import Image, ImageDraw, ImageFilter

def us_pin(im, x, y, r=34):
    d = ImageDraw.Draw(im)
    d.polygon([(x - r*.55, y - r*.4), (x + r*.55, y - r*.4), (x, y + r*.9)], fill=WHITE, outline=(0,0,0))
    m = Image.new("RGB", (2*r, 2*r), WHITE); md = ImageDraw.Draw(m)
    for i in range(7): md.rectangle([0, i*2*r/7, 2*r, i*2*r/7 + r/7], fill=(190, 20, 40))
    md.rectangle([0, 0, r, r], fill=(20, 40, 110))
    for i in range(3):
        for j in range(3): md.ellipse([6+j*9, 6+i*9, 10+j*9, 10+i*9], fill=WHITE)
    mask = Image.new("L", (2*r, 2*r)); ImageDraw.Draw(mask).ellipse([3, 3, 2*r-3, 2*r-3], fill=255)
    d.ellipse([x-r, y-2*r, x+r, y], fill=WHITE, outline=(0,0,0), width=3)
    im.paste(m, (int(x-r), int(y-2*r)), mask)

def circle(im, x, y, r, col=(230, 20, 20), w=10):
    ImageDraw.Draw(im).ellipse([x-r, y-r, x+r, y+r], outline=col, width=w)

def arrow(im, x0, y0, x1, y1, col=(230, 20, 20), w=26):
    d = ImageDraw.Draw(im); a = math.atan2(y1-y0, x1-x0); L = 60
    d.line([(x0, y0), (x1 - L*.6*math.cos(a), y1 - L*.6*math.sin(a))], fill=col, width=w)
    d.polygon([(x1, y1), (x1 - L*math.cos(a-0.5), y1 - L*math.sin(a-0.5)), (x1 - L*math.cos(a+0.5), y1 - L*math.sin(a+0.5))], fill=col)

def frame(src, box): return src, box

v = sys.argv[1]
if v == "a":   # F-105 lọt vòng ngắm
    im = base("f1101.jpg", (0, 60, 720, 465))
    us_pin(im, 470, 225, r=40)
    headline(im, [("TỪ ĐÁM MÂY", WHITE), ("LAO XUỐNG...", YEL)])
    tag(im, 640, 690, "F-105 LỌT VÀO VÒNG NGẮM", bg=(220, 20, 30), fg=WHITE, size=64)
    im.save("thumb-hamrong-A.jpg", quality=93)
elif v == "b":  # F-105 bay trên mây
    im = base("f977.jpg", (60, 0, 660, 337))
    us_pin(im, 560, 270, r=44)
    headline(im, [("ĐÁNH ÚP", WHITE), ("THẦN SẤM F-105", YEL)])
    tag(im, 640, 690, "4 MiG-17 VIỆT NAM vs 80 MÁY BAY MỸ", bg=YEL, size=64)
    im.save("thumb-hamrong-B.jpg", quality=93)
elif v == "c":  # quả cầu lửa
    im = base("p119.jpg", (0, 0, 720, 405))
    headline(im, [("TRẬN ĐẦU", WHITE), ("BẮN RƠI F-105", YEL)])
    im.save("thumb-hamrong-C.jpg", quality=93)
