"""High-contrast YouTube thumbnails (1280x720) with neon counters."""
import sys
import cairo
from PIL import Image, ImageFilter, ImageChops, ImageEnhance
from engine import draw_char, font, text_w, setc, fill_rrect, poly
from scenes import kitchen, GROUND
from scenes2 import park, bench, pigeons
from story_full import ME, GMA, WALTER

SC = 2                       # supersample
W, H = 1280 * SC, 720 * SC


def surface_to_pil(s):
    s.flush()
    return Image.frombuffer("RGBA", (s.get_width(), s.get_height()), bytes(s.get_data()), "raw", "BGRa", 0, 1)


def layer(draw, z=1.0, fx=960, fy=540):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    c.translate(W / 2, H / 2)
    c.scale(z * SC * 1280 / 1920, z * SC * 1280 / 1920)
    c.translate(-fx, -fy)
    draw(c)
    return surface_to_pil(s)


def outline(img, px=10, color=(20, 16, 24)):
    a = img.split()[3]
    grown = a.filter(ImageFilter.MaxFilter(px * 2 + 1))
    base = Image.new("RGBA", img.size, color + (0,))
    base.putalpha(grown)
    base.alpha_composite(img)
    return base


def neon_number(text, size, color, cx, cy):
    """Glowing number with a pointer, returned as an RGBA layer."""
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    font(c, size * SC)
    tw = text_w(c, text)
    x, y = cx * SC - tw / 2, cy * SC
    c.move_to(x, y)
    c.text_path(text)
    c.set_line_width(size * SC * 0.16)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    setc(c, color)
    c.stroke_preserve()
    setc(c, "#ffffff")
    c.fill()
    # pointer triangle under the number
    ty = y + size * SC * 0.25
    poly(c, [(cx * SC - 22 * SC, ty), (cx * SC + 22 * SC, ty), (cx * SC, ty + 30 * SC)], color)
    core = surface_to_pil(s)
    glow = Image.new("RGBA", core.size, (0, 0, 0, 0))
    for r, k in ((44, 0.55), (20, 0.8), (8, 0.9)):
        g = core.filter(ImageFilter.GaussianBlur(r * SC / 2))
        rgb = Image.new("RGBA", core.size, hexrgb(color) + (0,))
        rgb.putalpha(g.split()[3].point(lambda v: min(255, int(v * 1.3 * k))))
        glow = Image.alpha_composite(glow, rgb)
    return Image.alpha_composite(glow, core)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def grade(img, warm=(255, 170, 90), strength=0.18):
    tint = Image.new("RGBA", img.size, warm + (int(255 * strength),))
    img = Image.alpha_composite(img, tint)
    vig = Image.radial_gradient("L").resize(img.size).point(lambda v: int(min(255, v * 1.1)))
    dark = Image.new("RGBA", img.size, (0, 0, 0, 255))
    dark.putalpha(vig.point(lambda v: int(v * 0.75)))
    img = Image.alpha_composite(img, dark)
    return ImageEnhance.Contrast(ImageEnhance.Color(img).enhance(1.25)).enhance(1.12)


def thumb_grandma(path):
    bg = layer(lambda c: kitchen(c, 2.0), z=1.25, fx=1000, fy=450)
    bg = bg.filter(ImageFilter.GaussianBlur(7 * SC))
    bg = grade(bg)
    chars = layer(lambda c: draw_char(c, GMA, 1350, 1250, 1.25, 0.3, expr="happy", pose="cane", look=-0.6,
                                      flip=True), z=1.0)
    me = layer(lambda c: draw_char(c, ME, 520, 1500, 1.55, 0.1, expr="shock", pose="shrug", look=1), z=1.0)
    img = bg
    for lay in (outline(chars, 7), outline(me, 7)):
        img = Image.alpha_composite(img, lay)
    img = Image.alpha_composite(img, neon_number("96,440", 150, "#ff2e63", 900, 175))
    img = Image.alpha_composite(img, neon_number("4,813", 70, "#2e9bff", 330, 92))
    img.convert("RGB").resize((1280, 720), Image.LANCZOS).save(path, quality=95)


def thumb_zero(path):
    bg = layer(lambda c: (park(c, 0), bench(c, 1520)), z=1.2, fx=1150, fy=520)
    bg = bg.filter(ImageFilter.GaussianBlur(7 * SC))
    bg = grade(bg, warm=(255, 200, 140), strength=0.12)
    walter = layer(lambda c: draw_char(c, WALTER, 1420, 1260, 1.3, 0.3, expr="sad", look=-0.5, flip=True), z=1.0)
    me = layer(lambda c: draw_char(c, ME, 500, 1500, 1.55, 0.1, expr="shock", pose="shrug", look=1), z=1.0)
    img = bg
    for lay in (outline(walter, 7), outline(me, 7)):
        img = Image.alpha_composite(img, lay)
    img = Image.alpha_composite(img, neon_number("0", 220, "#ff2e63", 945, 230))
    img = Image.alpha_composite(img, neon_number("4,813", 70, "#2e9bff", 330, 92))
    img.convert("RGB").resize((1280, 720), Image.LANCZOS).save(path, quality=95)


if __name__ == "__main__":
    out = sys.argv[1]
    thumb_grandma(f"{out}/thumb-A-grandma.jpg")
    thumb_zero(f"{out}/thumb-B-zero.jpg")
