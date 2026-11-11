"""Shot list for: What If You Could See Everyone's Lie Count? (60s silent cut)."""
import math
from engine import (W, H, Char, draw_char, draw_cat, counter_label, plus_one, bubble, caption,
                    tag, ease, ease_out_back, font, text_w, setc, fill_rrect, circle, ellipse, line)
from scenes import GROUND, street, kitchen, living, couch, table, desk_note, dark_card

ME = Char("#f2c9a0", "#e8833a", hair="short", hair_c="#3b2a20", blink_phase=0.3)
COWORKER = Char("#c98e64", "#6c8ebf", hair="bowl", hair_c="#2b2420", blink_phase=1.1)
SIS = Char("#f2c9a0", "#c55a7a", pants="#4a3f55", hair="ponytail", hair_c="#5a3a28", blink_phase=2.0)
SIS_COOK = Char("#f2c9a0", "#c55a7a", pants="#4a3f55", hair="ponytail", hair_c="#5a3a28",
                extra=("apron",), blink_phase=2.0)
GRANDMA = Char("#efc6a6", "#8a7aa8", pants="#5b5470", hair="bun", hair_c="#dcd7cf",
               extra=("glasses",), blink_phase=0.7)
SALES = Char("#d9a47a", "#3a3f5c", pants="#2c3045", shoes="#2a2522", hair="slick", hair_c="#1f1a17",
             extra=("suit",), blink_phase=1.6)
FRIEND = Char("#8d5a3b", "#4f9a6b", pants="#2f3a4a", hair="spiky", hair_c="#1e1714", blink_phase=2.6)


def head_top(x, s):
    return x, GROUND - 725 * s


class Counter:
    def __init__(self, base, ticks=()):
        self.base, self.ticks = base, list(ticks)

    def state(self, t):
        v = self.base + sum(1 for tt in self.ticks if t >= tt)
        pop = flash = 0.0
        last = None
        for tt in self.ticks:
            if t >= tt:
                d = t - tt
                pop = max(pop, math.exp(-d * 9) * math.sin(min(d * 25, math.pi)))
                flash = max(flash, math.exp(-d * 4))
                last = tt
        return v, pop, flash, last


def show_counter(ctx, x, y, counter, t, appear=0.0, s=1.0):
    if t < appear:
        return
    v, pop, flash, last = counter.state(t)
    k = ease_out_back((t - appear) / 0.25)
    counter_label(ctx, x, y, v, pop=pop + (1 - k) * -0.9, flash=flash, s=s)
    if last is not None:
        plus_one(ctx, x + 60 * s, y - 40 * s, t - last)


class Shot:
    def __init__(self, dur, cam, world, screen=None, sfx=()):
        self.dur, self.cam, self.world, self.screen, self.sfx = dur, cam, world, screen, list(sfx)

    def camera(self, t):
        fx, fy, z0, z1 = self.cam[:4]
        shake = self.cam[4] if len(self.cam) > 4 else None
        z = z0 + (z1 - z0) * ease(t / self.dur)
        ox = oy = 0
        if shake is not None and t >= shake:
            d = t - shake
            amp = 14 * math.exp(-d * 7)
            ox, oy = amp * math.sin(d * 60), amp * math.cos(d * 47)
        return fx + ox, fy + oy, z


def to_screen(cam, x, y):
    fx, fy, z = cam
    return (x - fx) * z + W / 2, (y - fy) * z + H / 2


# ------------------------------------------------------------------ shots
S = 0.82


def s1_world(ctx, t):
    street(ctx, t, 0)
    draw_char(ctx, COWORKER, 760, GROUND, S, t, expr="happy" if t > 1.0 else "neutral", pose="hips")
    draw_char(ctx, ME, 1180, GROUND, S, t, expr="shock" if t > 2.7 else "happy",
              pose="present" if t < 1.6 else "down", talking=0.3 < t < 1.3, flip=True, look=1)
    show_counter(ctx, *head_top(1180, S), C_ME1, t, appear=1.7)


C_ME1 = Counter(4812, [2.5])


def s1_screen(ctx, t, cam):
    ax, ay = to_screen(cam, 1180 - 90 * S, GROUND - 655 * S)
    bubble(ctx, ax, ay, "Love the new haircut!", t - 0.3, side=-1)


def s2_world(ctx, t):
    street(ctx, t, 0)
    draw_char(ctx, ME, 1180, GROUND, S, t, expr="shock", pose="shrug", flip=True, look=-0.3)
    v = C_ME1.base + 1
    counter_label(ctx, *head_top(1180, S), v)


def s2_screen(ctx, t, cam):
    caption(ctx, "Wait... what is THAT?", t - 0.25)


def s3_world(ctx, t):
    dark_card(ctx, t)


TITLE_C = Counter(1204, [0.9 + i * 0.45 for i in range(6)])


def s3_screen(ctx, t, cam):
    lines = [("WHAT IF YOU COULD SEE", 0.15, 76, "#ffffff"), ("EVERYONE'S LIE COUNT?", 0.45, 104, "#ff6b5e")]
    for i, (txt, t0, size, col) in enumerate(lines):
        age = t - t0
        if age < 0:
            continue
        k = ease_out_back(age / 0.3)
        font(ctx, size)
        tw = text_w(ctx, txt)
        ctx.save()
        ctx.translate(W / 2, 470 + i * 130)
        ctx.scale(k, k)
        ctx.move_to(-tw / 2, 0)
        ctx.text_path(txt)
        ctx.set_line_width(10)
        setc(ctx, "#0e0f12")
        ctx.stroke_preserve()
        setc(ctx, col)
        ctx.fill()
        ctx.restore()
    show_counter(ctx, W / 2, 330, TITLE_C, t, appear=0.7, s=1.3)


C_SIS = Counter(2301)
C_GMA = Counter(96440)


def s4_world(ctx, t):
    kitchen(ctx, t)
    draw_char(ctx, SIS, 1150, GROUND, S, t, expr="neutral", pose="down", look=-1)
    show_counter(ctx, *head_top(1150, S), C_SIS, t, appear=0.4)
    draw_char(ctx, ME, 420, GROUND + 120, 1.05, t, expr="suspicious", pose="down", look=1)


def s4_screen(ctx, t, cam):
    tag(ctx, "THE NEXT MORNING", 60, 50, t)
    caption(ctx, "Your sister: 2,301 lies.", t - 0.7)


def s5_world(ctx, t):
    living(ctx, t)
    draw_char(ctx, GRANDMA, 900, GROUND - 40, S, t, expr="happy", pose="cane", look=0)
    couch(ctx, 500, GROUND + 20)
    show_counter(ctx, 900, GROUND - 40 - 725 * S, C_GMA, t, appear=0.4)


def s5_screen(ctx, t, cam):
    caption(ctx, "Grandma: 96,440?!", t - 0.8)


def s6_world(ctx, t):
    kitchen(ctx, t)
    draw_cat(ctx, 960, GROUND - 10, 1.1, t)
    if t > 0.5:
        k = ease_out_back((t - 0.5) / 0.3)
        fill_rrect(ctx, 960 - 45 * k, 520 - 80 * k, 90 * k, 80 * k, 18, (0.11, 0.12, 0.15, 0.94))
        if k > 0.6:
            font(ctx, 56)
            ctx.move_to(960 - 14, 520 - 20)
            setc(ctx, "#ffffff")
            ctx.show_text("?")


def s6_screen(ctx, t, cam):
    caption(ctx, "The cat: nothing. Cats don't lie. They just don't care.", t - 0.6)


C_SALES = Counter(38900, [1.6, 2.2])


def s7_world(ctx, t):
    street(ctx, t, 1)
    draw_char(ctx, SALES, 960, GROUND, S, t, expr="happy", pose="present", talking=0.4 < t < 2.4)
    show_counter(ctx, *head_top(960, S), C_SALES, t, appear=0.2)


def s7_screen(ctx, t, cam):
    ax, ay = to_screen(cam, 960 + 90 * S, GROUND - 655 * S)
    bubble(ctx, ax, ay, "Trust me, it runs like new!", t - 0.4, side=1)
    caption(ctx, "The car salesman: no surprise there.", t - 1.9)


C_FRIEND = Counter(711, [2.8])


def s8_world(ctx, t):
    street(ctx, t, 2)
    draw_char(ctx, ME, 720, GROUND, S, t, expr="happy" if t < 1.6 else "suspicious", pose="point" if t < 1.6 else "down",
              talking=0.2 < t < 1.3, look=1)
    draw_char(ctx, FRIEND, 1220, GROUND, S, t, expr="happy", pose="hips", talking=1.6 < t < 2.6, flip=True, look=1)
    # shoes highlight
    show_counter(ctx, *head_top(1220, S), C_FRIEND, t, appear=0.0)


def s8_screen(ctx, t, cam):
    if t < 1.5:
        ax, ay = to_screen(cam, 720 + 90 * S, GROUND - 655 * S)
        bubble(ctx, ax, ay, "Do you like my new shoes?", t - 0.2, side=1)
    ax, ay = to_screen(cam, 1220 - 90 * S, GROUND - 655 * S)
    bubble(ctx, ax, ay, "Yeah... they're great!", t - 1.6, side=-1)
    caption(ctx, "Every lie. +1. In real time.", t - 3.3)


def s9_world(ctx, t):
    desk_note(ctx, t, [("RULES", t - 0.2), ("1. Number = lies told", t - 0.8),
                       ("2. Goes up in real time", t - 1.6), ("3. Cats are honest", t - 2.5)])


def s9_screen(ctx, t, cam):
    pass


C_SIS2 = Counter(2301, [2.3])


def s10_world(ctx, t):
    kitchen(ctx, t, evening=True)
    draw_char(ctx, ME, 620, GROUND, S, t, expr="neutral" if t < 2.5 else "suspicious", pose="down",
              talking=0.2 < t < 0.9, look=1)
    draw_char(ctx, SIS, 1300, GROUND, S, t, expr="neutral", pose="down", talking=1.4 < t < 2.0, flip=True,
              look=0.4)
    table(ctx, 520, GROUND, 900)
    show_counter(ctx, *head_top(1300, S), C_SIS2, t, appear=0.0)


def s10_screen(ctx, t, cam):
    tag(ctx, "THAT EVENING", 60, 50, t)
    if t < 1.4:
        ax, ay = to_screen(cam, 620 + 90 * S, GROUND - 655 * S)
        bubble(ctx, ax, ay, "Hey... you okay?", t - 0.2, side=1)
    ax, ay = to_screen(cam, 1300 - 90 * S, GROUND - 655 * S)
    bubble(ctx, ax, ay, "I'm fine.", t - 1.4, side=-1)


def s11_world(ctx, t):
    kitchen(ctx, t, evening=True)
    draw_char(ctx, SIS, 1300, GROUND, S, t, expr="sad", pose="down", talking=0.3 < t < 3.2, flip=True, look=0.6)
    table(ctx, 520, GROUND, 900)
    counter_label(ctx, *head_top(1300, S), 2302, s=1.0)


def s11_screen(ctx, t, cam):
    ax, ay = to_screen(cam, 1300 - 90 * S, GROUND - 655 * S)
    bubble(ctx, ax, ay, "I lost my job. I didn't want Mom to worry.", t - 0.3, side=-1, maxw=560)


def s12_world(ctx, t):
    living(ctx, t)
    draw_char(ctx, GRANDMA, 900, GROUND - 40, S, t, expr="happy" if t > 2.6 else "neutral", pose="cane",
              talking=(0.2 < t < 2.3) or (2.7 < t < 3.6), look=0.4)
    couch(ctx, 500, GROUND + 20)
    counter_label(ctx, *head_top(900, S), 96440)


def s12_screen(ctx, t, cam):
    ax, ay = to_screen(cam, 900 + 90 * S, GROUND - 40 - 655 * S)
    if t < 2.6:
        bubble(ctx, ax, ay, "For 60 years, Grandpa asked if he looked handsome.", t - 0.2, side=1, maxw=600)
    else:
        bubble(ctx, ax, ay, "I always said yes.", t - 2.6, side=1)


def s13_world(ctx, t):
    living(ctx, t, evening=True)
    draw_char(ctx, ME, 960, GROUND, S, t, expr="think", pose="chin", look=-0.6)
    counter_label(ctx, *head_top(960, S), 4813)


def s13_screen(ctx, t, cam):
    caption(ctx, "Maybe the number isn't about how BAD someone is...", t - 0.3)


C_ME2 = Counter(4813, [3.0])


def s14_world(ctx, t):
    kitchen(ctx, t, evening=True)
    draw_char(ctx, SIS_COOK, 1300, GROUND, S, t, expr="happy", pose="hold", talking=0.2 < t < 1.2, flip=True, look=1)
    # burnt pot + smoke
    fill_rrect(ctx, 1300 - 120, GROUND - 330 * S - 40, 240, 90, 20, "#3b3f45")
    for i in range(3):
        k = (t * 0.6 + i / 3) % 1
        circle(ctx, 1300 - 150 - k * 140 + i * 40 + 20 * math.sin(t * 3 + i), GROUND - 330 * S - 60 - k * 200, 30 + 30 * k,
               (0.35, 0.35, 0.38, 0.6 * (1 - k)))
    draw_char(ctx, ME, 620, GROUND, S, t, expr="happy" if t > 2.2 else "neutral", pose="down",
              talking=2.0 < t < 2.6, look=1)
    table(ctx, 520, GROUND, 520)
    show_counter(ctx, *head_top(620, S), C_ME2, t, appear=0.0)


def s14_screen(ctx, t, cam):
    if t < 2.0:
        ax, ay = to_screen(cam, 1300 - 90 * S, GROUND - 655 * S)
        bubble(ctx, ax, ay, "How's my cooking?", t - 0.2, side=-1)
    ax, ay = to_screen(cam, 620 + 90 * S, GROUND - 655 * S)
    bubble(ctx, ax, ay, "...Perfect.", t - 2.0, side=1)


def s15_world(ctx, t):
    dark_card(ctx, t)


def s15_screen(ctx, t, cam):
    for i, (txt, t0, size, col) in enumerate([("Would YOU want this power?", 0.2, 92, "#ffffff"),
                                               ("Tell us in the comments", 1.0, 54, "#ff6b5e")]):
        age = t - t0
        if age < 0:
            continue
        k = ease_out_back(age / 0.3)
        font(ctx, size)
        tw = text_w(ctx, txt)
        ctx.save()
        ctx.translate(W / 2, 520 + i * 120)
        ctx.scale(k, k)
        ctx.move_to(-tw / 2, 0)
        setc(ctx, col)
        ctx.show_text(txt)
        ctx.restore()


TOP = 680  # rough world y of head area for S scale


SHOTS = [
    Shot(4.0, (960, 560, 1.0, 1.12), s1_world, s1_screen, [(0.3, "pop"), (1.7, "pop"), (2.5, "tick")]),
    Shot(2.8, (1180, 470, 1.75, 1.95, 0.0), s2_world, s2_screen, [(0.0, "sting")]),
    Shot(4.0, (960, 540, 1.0, 1.0), s3_world, s3_screen,
         [(0.0, "whoosh")] + [(0.9 + i * 0.45, "tick") for i in range(6)]),
    Shot(3.4, (1000, 560, 1.05, 1.15), s4_world, s4_screen, [(0.4, "pop")]),
    Shot(3.4, (900, 520, 1.15, 1.3), s5_world, s5_screen, [(0.4, "pop"), (0.8, "sting")]),
    Shot(3.4, (960, 640, 1.2, 1.3), s6_world, s6_screen, [(0.5, "pop")]),
    Shot(3.2, (960, 540, 1.1, 1.25), s7_world, s7_screen, [(0.2, "pop"), (0.4, "pop"), (1.6, "tick"), (2.2, "tick")]),
    Shot(5.0, (970, 560, 1.0, 1.1), s8_world, s8_screen, [(0.2, "pop"), (1.6, "pop"), (2.8, "tick")]),
    Shot(4.0, (960, 540, 1.0, 1.08), s9_world, s9_screen, [(0.2, "scribble"), (0.8, "scribble"), (1.6, "scribble"),
                                                           (2.5, "scribble")]),
    Shot(4.6, (960, 560, 1.0, 1.08), s10_world, s10_screen, [(0.2, "pop"), (1.4, "pop"), (2.3, "tick")]),
    Shot(4.4, (1300, 460, 1.6, 1.75), s11_world, s11_screen, [(0.3, "pop")]),
    Shot(5.0, (900, 500, 1.2, 1.35), s12_world, s12_screen, [(0.2, "pop"), (2.6, "pop")]),
    Shot(3.6, (960, 520, 1.25, 1.4), s13_world, s13_screen, []),
    Shot(5.2, (960, 560, 1.0, 1.1), s14_world, s14_screen, [(0.2, "pop"), (2.0, "pop"), (3.0, "tick")]),
    Shot(3.6, (960, 540, 1.0, 1.0), s15_world, s15_screen, [(0.0, "whoosh"), (1.0, "pop")]),
]
