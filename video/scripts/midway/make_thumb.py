import sys; sys.path.insert(0,"midway")
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import gfx3
W,H=1280,720
bg=Image.open("thumb/bg6.5.png").convert("RGB")
bg=bg.resize((1600,900),Image.LANCZOS).crop((180,40,180+W,40+H))
bg=ImageEnhance.Contrast(bg).enhance(1.15); bg=ImageEnhance.Color(bg).enhance(1.1)
# left dark gradient
g=Image.new("L",(W,H))
for x in range(W):
    v=int(235*max(0,1-x/760)**1.3)
    ImageDraw.Draw(g).line([(x,0),(x,H)],fill=v)
bg.paste(Image.new("RGB",(W,H),(8,8,10)),(0,0),g)
d=ImageDraw.Draw(bg)
F=lambda p,s: ImageFont.truetype(p,s)
def txt(xy,s,f,fill,sw=6):
    d.text(xy,s,font=f,fill=fill,stroke_width=sw,stroke_fill=(0,0,0))
txt((48,60),"TRẬN MIDWAY 1942",F(gfx3.OSWALD,58),(255,255,255),4)
d.rectangle([52,146,330,152],fill=(214,30,30))
txt((40,150),"6 PHÚT",F(gfx3.OSWALD,230),(255,206,60),8)
txt((48,400),"ĐỊNH MỆNH",F(gfx3.OSWALD,120),(255,255,255),7)
d.rectangle([48,600,650,670],fill=(200,20,20))
d.text((64,608),"3 TÀU SÂN BAY NHẬT BỐC CHÁY",font=F(gfx3.OSWALD,44),fill=(255,255,255))
logo=Image.open("/home/user/phuong/video/brand/logo-ngang.png").convert("RGBA")
logo.thumbnail((260,80)); bg.paste(logo,(W-logo.width-30,H-logo.height-24),logo)
bg.save(sys.argv[1],quality=92)
