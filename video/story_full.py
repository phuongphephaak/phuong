"""Full episode: What If You Could See Everyone's Lie Count? (~9 min)."""
from engine import Char, W, H, font, text_w, setc, fill_rrect, ease_out_back, counter_label, ease, line
from scenes import GROUND, street, kitchen, living, couch, table, desk_note, dark_card
from scenes2 import (office, desk, market, stall, jewelry_stall, cafe_in, cafe_table, poker_table, karaoke,
                     hallway, stairs, park, bench, pigeons, bathroom, bedroom_mirror, hospital, hands_closeup,
                     phone_screen, tv_window, sunset, tint)
from director import Beat, Actor as A, Counter as C

# ------------------------------------------------------------------ cast
ME = Char("#f2c9a0", "#e8833a", hair="short", hair_c="#3b2a20", blink_phase=0.3)
COWORKER = Char("#c98e64", "#6c8ebf", hair="bowl", hair_c="#2b2420", blink_phase=1.1)
MIA = Char("#f2c9a0", "#c55a7a", pants="#4a3f55", hair="ponytail", hair_c="#5a3a28", blink_phase=2.0)
MIA_COOK = Char("#f2c9a0", "#c55a7a", pants="#4a3f55", hair="ponytail", hair_c="#5a3a28", extra=("apron",),
                blink_phase=2.0)
GMA = Char("#efc6a6", "#8a7aa8", pants="#5b5470", hair="bun", hair_c="#dcd7cf", extra=("glasses", "wrinkles"),
           blink_phase=0.7)
JAY = Char("#8d5a3b", "#4f9a6b", pants="#2f3a4a", hair="spiky", hair_c="#1e1714", blink_phase=2.6)
MOM = Char("#f0c49b", "#5aa39a", pants="#4a4a5a", hair="bob", hair_c="#6b3f2a", blink_phase=1.4)
DAD = Char("#eab98f", "#8a6d4f", pants="#3d4250", hair="slick", hair_c="#4a3a2e", extra=("glasses",),
           blink_phase=0.5)
KENT = Char("#e2b48c", "#4a5568", pants="#2d3340", shoes="#2a2522", hair="bald", hair_c="#8a7a6a",
            extra=("suit",), blink_phase=1.9)
BRAD = Char("#e9bf98", "#c9d6e3", pants="#2f3a4a", hair="slick", hair_c="#c8a050", blink_phase=0.8)
WALTER = Char("#e8bf9e", "#7d6b58", pants="#4a4038", shoes="#5a4636", hair="bald", hair_c="#cfcac2",
              extra=("wrinkles",), blink_phase=1.3)
SON = Char("#e8bf9e", "#3f6f8f", pants="#2f3a4a", hair="short", hair_c="#6b5a4a", blink_phase=2.2)
GPA = Char("#eec7a5", "#4a5a78", pants="#2d3340", shoes="#2a2522", hair="slick", hair_c="#3a2a20",
           extra=("suit", "tie_orange"), blink_phase=0.4)
VENDOR = Char("#d2a07a", "#8b4b3a", pants="#3b3f45", hair="cap", hair_c="#2f4858", blink_phase=1.0)
OLDLADY = Char("#f0caa8", "#b88aa0", pants="#5b5470", hair="bun", hair_c="#e8e4dc", extra=("wrinkles",),
               blink_phase=2.4)
BOY = Char("#f0c49b", "#e9c46a", pants="#3d5a80", hair="short", hair_c="#7a4a2a", extra=("choc",), blink_phase=0.6)
BOYMOM = Char("#f0c49b", "#9a6fb0", pants="#3d4250", hair="ponytail", hair_c="#7a4a2a", blink_phase=1.5)
BARISTA = Char("#c98e64", "#2f2f2f", pants="#2f2f2f", hair="bob", hair_c="#1e1714", extra=("apron",),
               blink_phase=2.1)
POL = Char("#e2b48c", "#2c3e66", pants="#2d3340", hair="slick", hair_c="#bdbdbd", extra=("suit",))
MAILMAN = Char("#b07a55", "#3d5a80", pants="#2d3340", hair="cap", hair_c="#3d5a80", blink_phase=0.1)
JOGGER = Char("#f0c49b", "#e76f51", pants="#2b2d42", hair="ponytail", hair_c="#e9c46a", blink_phase=1.6)
SALES = Char("#d9a47a", "#3a3f5c", pants="#2c3045", shoes="#2a2522", hair="slick", hair_c="#1f1a17",
             extra=("suit",), blink_phase=1.6)
CUST = Char("#8d5a3b", "#a3b18a", pants="#4a4038", hair="short", hair_c="#1e1714", blink_phase=2.8)
COUS1 = Char("#c98e64", "#d17a22", pants="#3d4250", hair="cap", hair_c="#264653", blink_phase=0.2)
COUS2 = Char("#8d5a3b", "#6d597a", pants="#3d4250", hair="bob", hair_c="#1e1714", blink_phase=1.8)
KF1 = Char("#efc6a6", "#2a9d8f", pants="#3d4250", hair="ponytail", hair_c="#3b2a20", blink_phase=0.6)
KF2 = Char("#d9a47a", "#e76f51", pants="#3d4250", hair="short", hair_c="#1e1714", blink_phase=2.3)

S = 0.82
G = GROUND


def label_card(lines, t0s, sizes, colors, counter=None):
    def screen(ctx, t, b):
        for i, (txt, t0, size, col) in enumerate(zip(lines, t0s, sizes, colors)):
            age = t - t0
            if age < 0:
                continue
            k = ease_out_back(age / 0.3)
            font(ctx, size)
            tw = text_w(ctx, txt)
            ctx.save()
            ctx.translate(W / 2, 480 + i * 125)
            ctx.scale(k, k)
            ctx.move_to(-tw / 2, 0)
            ctx.text_path(txt)
            ctx.set_line_width(10)
            setc(ctx, "#0e0f12")
            ctx.stroke_preserve()
            setc(ctx, col)
            ctx.fill()
            ctx.restore()
        if counter is not None and t > 0.6:
            v = counter + int((t - 0.6) / 0.45)
            counter_label(ctx, W / 2, 330, v, s=1.3)
    return screen


def kitchen_ev(ctx, t):
    kitchen(ctx, t, evening=True)


def living_day(ctx, t):
    living(ctx, t, evening=False)


def front_table(x, w):
    return lambda ctx, t, b: table(ctx, x, G, w)


# Counters (persisting values across beats are written explicitly)
BEATS = [
    # ---------------------------------------------------------------- PART 0: HOOK
    Beat(lambda c, t: street(c, t, 0), crowd=4,
         lines=[("vo", "It's a normal Tuesday. You're walking to work, coffee in hand, when your coworker steps "
                       "out of the bakery with the worst haircut you have ever seen. It looks like someone put a "
                       "bowl on his head and missed.")],
         actors=[A("me", ME, -150, to=820, at=0.2, prop=("coffee",), expr="happy"),
                 A("cw", COWORKER, 1550, to=1180, at="s0%0.45", expr="happy", face=-1)],
         cams=[(0, ("track", "me", 1.05)), ("s0%0.55", ("two", "me", "cw", 1.1)), ("s0%0.8", ("on", "cw", 1.6))]),
    Beat(lambda c, t: street(c, t, 0), crowd=4,
         lines=[("me", "Whoa! Love the new haircut!"),
                ("vo", "And the second the words leave your mouth, a number appears above your head. Four thousand, "
                       "eight hundred and twelve. Then... tick... four thousand, eight hundred and thirteen. You just "
                       "lied. And somehow... the universe noticed.")],
         actors=[A("me", ME, 820, expr=[(0, "happy"), ("s1%0.15", "shock")], pose=[(0, "present"), ("e0", "down")],
                   face=1, label=C(4812, ["s1%0.52"]), label_at="s1%0.12", prop=("coffee",)),
                 A("cw", COWORKER, 1180, expr="happy", pose="hips", face=-1)],
         cams=[(0, ("two", "me", "cw", 1.1)), ("s1%0.1", ("on", "me", 1.8)), ("s1%0.48", ("on", "me", 2.1)),
               ("s1%0.75", ("wide", 1.0))],
         sfx=[("s1%0.15", "sting")]),
    Beat(lambda c, t: street(c, t, 0), crowd=5,
         lines=[("vo", "By the end of this week, you'll find out that everyone has a number. Your sister. Your best "
                       "friend. Your sweet little grandma. And one of those numbers is going to completely break "
                       "your heart.")],
         actors=[A("me", ME, 820, expr="shock", face=1, label=C(4813), prop=("coffee",)),
                 A("cw", COWORKER, 1180, to=2700, at=0.3, expr="happy")],
         cams=[(0, ("wide", 1.0)), ("s0%0.6", ("on", "me", 1.5))]),
    Beat(dark_card, dur=3.6, screen=label_card(["WHAT IF YOU COULD SEE", "EVERYONE'S LIE COUNT?"], [0.15, 0.45],
                                               [76, 104], ["#ffffff", "#ff6b5e"], counter=1204),
         sfx=[(0.0, "whoosh")] + [(0.6 + i * 0.45, "tick") for i in range(7)]),

    # ---------------------------------------------------------------- PART 1: DISCOVERY
    Beat(kitchen, tags=[("THE NEXT MORNING", 0)],
         lines=[("vo", "You wake up hoping it was a dream. It wasn't."),
                ("vo", "Your sister Mia is pouring cereal. Above her head: two thousand, three hundred and one.")],
         actors=[A("me", ME, -200, to=480, at=0.2, style="slow", expr="think", label=C(4813)),
                 A("mia", MIA, 1150, face=-1, expr="neutral", pose="hold", prop=("bowl",), label=C(2301),
                   label_at="s1%0.4")],
         cams=[(0, ("track", "me", 1.05)), ("s1", ("on", "mia", 1.5))]),
    Beat(kitchen,
         lines=[("vo", "Your dad walks in, reading the news on his phone. Eleven thousand, four hundred."),
                ("dad", "Morning, champ. Slept great!"),
                ("vo", "He did not sleep great. Then your mom walks in right behind him.")],
         actors=[A("me", ME, 480, face=1, expr="neutral", label=C(4813)),
                 A("mia", MIA, 850, face=-1, pose="hold", prop=("bowl",), label=C(2301)),
                 A("dad", DAD, 2300, to=1250, at=0.0, pose="phone", prop=("phone",), expr="happy",
                   label=C(11399, ["e1+0.15"]), label_at="s0%0.6"),
                 A("mom", MOM, 2500, to=1650, at="s2%0.4", expr="happy", hide_before="s2%0.3")],
         cams=[(0, ("track", "dad", 1.1)), ("s1-0.05", ("on", "dad", 1.55)), ("s2", ("wide", 1.0))]),
    Beat(kitchen,
         lines=[("mom", "Honey, I love the new shirt you bought."),
                ("vo", "Nine thousand, nine hundred and ninety-eight. Okay. So your parents' marriage is built on "
                       "small, polite lies. Good to know.")],
         actors=[A("me", ME, 480, face=1, expr=[(0, "neutral"), ("s1%0.5", "suspicious")], label=C(4813)),
                 A("mia", MIA, 850, face=-1, pose="hold", prop=("bowl",), label=C(2301)),
                 A("dad", DAD, 1250, face=1, expr="happy", label=C(11400)),
                 A("mom", MOM, 1650, face=-1, pose="present", expr="happy", label=C(9997, ["e0+0.15"]))],
         cams=[(0, ("two", "dad", "mom", 1.35)), ("s1", ("on", "mom", 1.6)), ("s1%0.45", ("on", "me", 1.5))]),
    Beat(kitchen,
         lines=[("vo", "And then Grandma Rose walks in slowly with her cane, smiling like an angel. "
                       "And above her head...")],
         actors=[A("me", ME, 480, face=1, expr="neutral", label=C(4813)),
                 A("gma", GMA, 150, to=700, at=0.0, style="cane", pose="cane", expr="happy",
                   label=C(96440), label_at="end-0.35")],
         cams=[(0, ("track", "gma", 1.15)), ("end-0.4", ("on", "gma", 1.9))],
         sfx=[("end-0.35", "sting")]),
    Beat(kitchen,
         lines=[("vo", "Ninety-six THOUSAND. Grandma. The woman who knits you socks every Christmas.")],
         actors=[A("me", ME, 300, face=1, expr="shock", label=C(4813)),
                 A("gma", GMA, 760, face=-1, pose="cane", expr="happy", label=C(96440))],
         cams=[(0, ("on", "gma", 1.9)), ("s0%0.4", ("on", "me", 1.8)), ("s0%0.7", ("on", "gma", 1.5))]),
    Beat(kitchen,
         lines=[("vo", "You look at the cat. Nothing. No number at all. Cats don't lie. They just don't care.")],
         actors=[A("cat", None, -300, to=1300, at=0.0, s=0.9, cat=True, style="walk")],
         cams=[(0, ("track", "cat", 1.25))]),
    Beat(lambda c, t: None, dur=0,
         lines=[("vo", "You grab your phone and search: \"Why can I see numbers above people's heads?\" "
                       "The first result says you need more sleep. The second result says you might be a wizard. "
                       "Neither is helpful.")],
         screen=None),

    # ---------------------------------------------------------------- PART 2: RULES
    Beat(lambda c, t: street(c, t, 1), crowd=9,
         lines=[("vo", "Outside, it's chaos. Everyone has a number. The mailman: eight thousand. "
                       "A jogger: twenty-two thousand.")],
         actors=[A("me", ME, -100, to=1500, at=0.0, style="slow", expr="shock", label=C(4813)),
                 A("mail", MAILMAN, 2300, to=600, at="s0%0.2", label=C(8000)),
                 A("jog", JOGGER, -600, to=3000, at="s0%0.6", style="run", label=C(22000), expr="happy")],
         cams=[(0, ("track", "me", 1.0)), ("s0%0.4", ("on", "mail", 1.5)), ("s0%0.72", ("track", "jog", 1.2))]),
    Beat(lambda c, t: street(c, t, 2), crowd=5,
         lines=[("vo", "A little boy with chocolate all over his face, holding his mom's hand."),
                ("bmom", "Did you eat the candy?"), ("boy", "No."), ("vo", "Three. Nice try, kid.")],
         actors=[A("bmom", BOYMOM, 1150, face=-1, expr="suspicious", pose="hips", label=C(4100)),
                 A("boy", BOY, 880, s=0.5, face=1, expr="happy", label=C(2, ["e2+0.1"])),
                 A("me", ME, 300, face=1, expr="neutral", label=C(4813))],
         cams=[(0, ("two", "boy", "bmom", 1.3)), ("s2-0.05", ("at", 880, 640, 2.0)), ("s3", ("at", 880, 600, 1.6))]),
    Beat(lambda c, t: street(c, t, 2), crowd=4,
         lines=[("bar", "Sorry, we're out of oat milk!"),
                ("vo", "They are not out of oat milk. They just don't want to make it.")],
         actors=[A("bar", BARISTA, 1260, face=-1, expr="happy", pose="present", label=C(15210, ["e0+0.1"])),
                 A("me", ME, 200, to=900, at=0.0, expr=[(0, "neutral"), ("s1", "suspicious")], label=C(4813))]),
    Beat(lambda c, t: street(c, t, 1), crowd=3,
         lines=[("vo", "Across the street, the car salesman is shaking hands with a customer. Thirty-eight thousand, "
                       "nine hundred. No surprise there.")],
         actors=[A("sales", SALES, 900, face=1, pose="present", expr="happy", label=C(38899, ["s0%0.85"])),
                 A("cust", CUST, 1180, face=-1, pose="present", expr="neutral")],
         cams=[(0, ("two", "sales", "cust", 1.3)), ("s0%0.5", ("on", "sales", 1.6))]),
    Beat(lambda c, t: tv_window(c, t, POL),
         lines=[("vo", "And on a TV screen in a shop window, a politician is giving a speech. His number doesn't "
                       "even fit. The label just says... \"ERROR.\"")],
         actors=[A("me", ME, -200, to=380, at=0.0, expr=[(0, "neutral"), ("s0%0.75", "shock")], label=C(4813))],
         cams=[(0, ("wide", 1.0)), ("s0%0.6", ("at", 960, 470, 1.8))],
         sfx=[("s0%0.4", "static"), ("s0%0.85", "static")]),
    Beat(park,
         lines=[("vo", "You need to test this properly. So you meet your best friend Jay at the park, and you ask "
                       "him the most dangerous question a friend can ask.")],
         actors=[A("me", ME, 700, face=1, expr="neutral", label=C(4813)),
                 A("jay", JAY, 2400, to=1180, at=0.2, style="run", expr="happy", label=C(711))],
         cams=[(0, ("track", "jay", 1.1)), ("s0%0.6", ("two", "me", "jay", 1.15))]),
    Beat(park,
         lines=[("me", "Do you like my new shoes?"), ("jay", "Yeah... they're great!"),
                ("vo", "Seven hundred and twelve, Jay. Wow. So you go home and write down everything you know.")],
         actors=[A("me", ME, 700, face=1, pose=[(0, "point"), ("e0", "down")],
                   expr=[(0, "happy"), ("e1+0.3", "suspicious")], label=C(4813)),
                 A("jay", JAY, 1180, face=-1, expr="happy", pose="hips", label=C(711, ["e1+0.15"]))],
         cams=[(0, ("two", "me", "jay", 1.15)), ("s0", ("at", 700, 860, 1.8)), ("s1-0.05", ("on", "jay", 1.6)),
               ("s2", ("on", "jay", 1.9)), ("s2%0.5", ("wide", 1.0))]),
    Beat(lambda c, t: desk_note(c, t, [("RULES", t - 0.3), ("1. Number = lies told", t - 1.0),
                                       ("2. Goes up in real time", t - 1.9), ("3. Babies start at zero", t - 2.8),
                                       ("4. Cats are honest", t - 3.7)]),
         dur=5.4, cams=[(0, ("wide", 1.0))],
         sfx=[(0.3, "scribble"), (1.0, "scribble"), (1.9, "scribble"), (2.8, "scribble"), (3.7, "scribble")]),

    # ---------------------------------------------------------------- PART 3: SUPERPOWER
    Beat(office, tags=[("MONDAY", 0)],
         lines=[("vo", "And just like that, you become a human lie detector. At work, your boss, Mr. Kent, stops by "
                       "your desk."),
                ("kent", "Great job this month. That raise is coming very soon."),
                ("vo", "It is not coming soon. You quietly open a new tab and start updating your resume.")],
         actors=[A("me", ME, 700, face=1, expr=[(0, "neutral"), ("s1", "happy"), ("e1+0.3", "suspicious")],
                   label=C(4813)),
                 A("kent", KENT, 2600, to=1350, at=0.3, expr="happy",
                   pose=[(0, "down"), ("s1", "present")], label=C(27650, ["e1+0.1"]))],
         front=lambda c, t, b: desk(c, 430, 560),
         cams=[(0, ("track", "kent", 1.0)), ("s1-0.05", ("on", "kent", 1.5)), ("s2", ("on", "me", 1.5))]),
    Beat(market,
         lines=[("vo", "On Saturday, you and Jay walk through the weekend market. A man at a stall is selling "
                       "necklaces to an old lady.")],
         actors=[A("me", ME, -400, to=520, at=0.0, expr="happy", label=C(4813)),
                 A("jay", JAY, -650, to=260, at=0.0, expr="happy", label=C(712)),
                 A("vendor", VENDOR, 1600, face=-1, pose="present", expr="happy", label=C(50998)),
                 A("lady", OLDLADY, 1250, face=1, pose="down", expr="neutral", label=C(3200))],
         back=lambda c, t, b: jewelry_stall(c, 1380),
         cams=[(0, ("track", "me", 1.0)), ("s0%0.6", ("two", "lady", "vendor", 1.25))]),
    Beat(market,
         lines=[("vendor", "Real gold, ma'am. Only two hundred dollars."),
                ("vo", "Fifty-one thousand lies, and he's adding more by the second. You step in.")],
         actors=[A("jay", JAY, 260, face=1, expr="neutral", label=C(712)),
                 A("me", ME, 520, to=1000, at="s1%0.75", style="fast", expr="suspicious", label=C(4813)),
                 A("vendor", VENDOR, 1600, face=-1, pose="present", expr="happy",
                   label=C(50998, ["e0+0.1", "e0+0.5"])),
                 A("lady", OLDLADY, 1250, face=1, expr="happy", label=C(3200))],
         back=lambda c, t, b: jewelry_stall(c, 1380),
         cams=[(0, ("on", "vendor", 1.5)), ("s1", ("at", 1600, 400, 1.9)), ("s1%0.7", ("wide", 1.0))]),
    Beat(market,
         lines=[("me", "Sir, can you scratch it for us? Real gold doesn't change color."),
                ("vo", "The old lady hugs you. Jay stares at you like you're a superhero. Honestly? You feel like "
                       "one.")],
         actors=[A("jay", JAY, 260, to=700, at="s1", face=1, expr=[(0, "neutral"), ("s1", "shock")], label=C(712)),
                 A("me", ME, 1000, face=1, expr=[(0, "suspicious"), ("s1", "happy")], pose=[(0, "point"),
                                                                                             ("e0", "down")],
                   label=C(4813)),
                 A("vendor", VENDOR, 1600, to=3200, at="e0+0.2", style="run", expr="shock", label=C(51000)),
                 A("lady", OLDLADY, 1250, face=-1, expr=[(0, "neutral"), ("s1", "happy")],
                   pose=[(0, "down"), ("s1", "hug")], label=C(3200))],
         back=lambda c, t, b: jewelry_stall(c, 1380),
         cams=[(0, ("on", "me", 1.5)), ("e0+0.2", ("wide", 1.0)), ("s1%0.55", ("on", "jay", 1.5))]),
    Beat(living,
         lines=[("vo", "That night is poker night with Jay's cousins."),
                ("vo", "\"I've got nothing,\" says one cousin. Tick. You fold."),
                ("vo", "\"I'm bluffing,\" says Jay. No tick. You fold again."),
                ("vo", "By midnight, you've won forty-three dollars, and everyone thinks you're some kind of genius.")],
         actors=[A("me", ME, 560, face=1, expr=[(0, "neutral"), ("s3", "happy")], label=C(4813)),
                 A("c1", COUS1, 900, face=-1, expr="happy", label=C(6230, ["s1%0.55"])),
                 A("jay", JAY, 1250, face=-1, expr="happy", label=C(712)),
                 A("c2", COUS2, 1580, face=-1, expr="neutral", label=C(9400))],
         front=lambda c, t, b: poker_table(c, t, chips=0 if t < b.ref("s3") else min(15, (t - b.ref("s3")) * 8)),
         cams=[(0, ("wide", 1.0)), ("s1", ("on", "c1", 1.6)), ("s2", ("on", "jay", 1.6)), ("s3", ("on", "me", 1.5))]),
    Beat(cafe_in,
         lines=[("vo", "Sunday, Jay has a first date. You sit two tables away, pretending to read a newspaper. "
                       "Upside down.")],
         actors=[A("jay", JAY, -300, to=1150, at=0.0, expr="happy", label=C(712)),
                 A("brad", BRAD, 1650, face=-1, expr="happy", label=C(24311)),
                 A("me", ME, 0, to=420, at="s0%0.35", style="tiptoe", expr="suspicious", label=C(4813),
                   pose=[(0, "down"), ("end-0.9", "paper")], prop=[(0, None), ("end-0.9", ("paper", "NEWS"))])],
         front=lambda c, t, b: (cafe_table(c, 1400), cafe_table(c, 420)),
         cams=[(0, ("track", "jay", 1.05)), ("s0%0.4", ("track", "me", 1.1)), ("s0%0.8", ("on", "me", 1.5))]),
    Beat(cafe_in,
         lines=[("brad", "I'm a doctor."), ("brad", "I love dogs."), ("brad", "I've never done this before.")],
         actors=[A("jay", JAY, 1150, face=1, expr=[(0, "happy"), ("s1", "neutral"), ("s2", "suspicious")],
                   label=C(712)),
                 A("brad", BRAD, 1650, face=-1, expr="happy", pose="present",
                   label=C(24311, ["e0+0.1", "e1+0.1", "e2+0.1"])),
                 A("me", ME, 420, face=1, expr="suspicious", label=C(4813), pose="paper", prop=("paper", "NEWS"))],
         front=lambda c, t, b: (cafe_table(c, 1400), cafe_table(c, 420)),
         cams=[(0, ("on", "brad", 1.5)), ("s1", ("on", "brad", 1.8)), ("s2", ("on", "brad", 1.5))]),
    Beat(cafe_in,
         lines=[("vo", "Jay leaves before dessert. On the walk home, you feel incredible. Nobody can fool you. "
                       "Nobody.")],
         actors=[A("jay", JAY, 1150, to=-500, at="s0%0.15", style="fast", expr="neutral", label=C(712)),
                 A("brad", BRAD, 1650, face=-1, expr="shock", label=C(24314)),
                 A("me", ME, 420, face=1, expr="happy", label=C(4813), pose="paper", prop=("paper", "RUN"))],
         front=lambda c, t, b: (cafe_table(c, 1400), cafe_table(c, 420)),
         cams=[(0, ("on", "me", 1.6)), ("s0%0.15", ("wide", 1.0))]),
    Beat(sunset, crowd=2, music="none", dur=3.0,
         actors=[A("me", ME, -300, to=1100, at=0.0, expr="happy", label=C(4813)),
                 A("jay", JAY, -560, to=840, at=0.0, expr="neutral", label=C(712))],
         cams=[(0, ("track", "me", 1.0))]),
    Beat(sunset, music="none",
         lines=[("jay", "Thanks, man. But... it's kind of creepy how you always know. Like I can't say anything "
                        "around you anymore.")],
         actors=[A("me", ME, 1100, face=-1, expr=[(0, "happy"), ("s0%0.4", "sad")], label=C(4813)),
                 A("jay", JAY, 840, face=1, expr="sad", label=C(712), path=[("e0+0.4", 840), (None, -600)],
                   style="slow")],
         cams=[(0, ("two", "jay", "me", 1.2)), ("s0%0.5", ("on", "me", 1.5)), ("e0+0.4", ("wide", 1.0))],
         hold=2.2),

    # ---------------------------------------------------------------- PART 4: NO MORE LIES
    Beat(karaoke,
         lines=[("vo", "So you make a decision. If lying makes your number go up, then you just... won't lie anymore. "
                       "Ever. How hard can it be? Very hard, it turns out.")],
         actors=[A("kf1", KF1, -400, to=320, at=0.0, expr="happy", label=C(3300)),
                 A("me", ME, -650, to=620, at=0.1, expr="think", label=C(4813)),
                 A("kf2", KF2, 2400, to=1560, at=0.0, expr="happy", label=C(5120)),
                 A("jay", JAY, 2600, to=1100, at="s0%0.4", expr="happy", pose="mic", prop=("mic",), label=C(712))],
         cams=[(0, ("wide", 1.0)), ("s0%0.5", ("on", "me", 1.5)), ("s0%0.8", ("wide", 1.0))]),
    Beat(karaoke, music="none",
         lines=[("vo", "At karaoke that Friday, Jay sings his heart out. It's the worst singing you have ever heard.")],
         actors=[A("kf1", KF1, 320, face=1, expr="shock", label=C(3300)),
                 A("me", ME, 620, face=1, expr="shock", label=C(4813)),
                 A("jay", JAY, 1100, face=-1, expr="happy", pose="mic", prop=("mic",), label=C(712)),
                 A("kf2", KF2, 1560, face=-1, expr="shock", label=C(5120))],
         back=None, sfx=[(0.2, "offkey"), ("s0%0.6", "offkey")],
         cams=[(0, ("on", "jay", 1.5)), ("s0%0.55", ("wide", 1.0))]),
    Beat(karaoke, music="none",
         lines=[("jay", "So? How was I?"),
                ("vo", "Everyone looks at you. You open your mouth. Your number waits.")],
         actors=[A("kf1", KF1, 320, face=1, expr="neutral", label=C(3300)),
                 A("me", ME, 620, face=1, expr="think", label=C(4813)),
                 A("jay", JAY, 1100, face=-1, expr="happy", pose="mic", prop=("mic",), label=C(712)),
                 A("kf2", KF2, 1560, face=-1, expr="neutral", label=C(5120))],
         cams=[(0, ("on", "jay", 1.5)), ("s1", ("wide", 1.0)), ("s1%0.6", ("on", "me", 2.0))]),
    Beat(karaoke, music="none",
         lines=[("me", "Honestly? You sounded like a cat in a washing machine.")],
         actors=[A("kf1", KF1, 320, face=1, expr=[(0, "neutral"), ("e0", "shock")], label=C(3300)),
                 A("me", ME, 620, face=1, expr="neutral", label=C(4813)),
                 A("jay", JAY, 1100, face=-1, expr=[(0, "happy"), ("e0", "sad")], pose="mic", prop=("mic",),
                   label=C(712)),
                 A("kf2", KF2, 1560, face=-1, expr=[(0, "neutral"), ("e0", "shock")], label=C(5120))],
         cams=[(0, ("on", "me", 1.6)), ("e0+0.1", ("wide", 1.0))], hold=2.6, sfx=[("e0+0.3", "crickets")]),
    Beat(karaoke, music="calm",
         lines=[("vo", "Your number doesn't move. Not even one. You told the truth. So why does everyone suddenly "
                       "hate you?")],
         actors=[A("kf1", KF1, 320, face=1, expr="suspicious", label=C(3300)),
                 A("me", ME, 620, face=1, expr="sad", label=C(4813)),
                 A("jay", JAY, 1100, to=2600, at=0.2, style="slow", expr="sad", label=C(712)),
                 A("kf2", KF2, 1560, face=-1, expr="suspicious", label=C(5120))],
         cams=[(0, ("wide", 1.0)), ("s0%0.3", ("on", "me", 1.9))]),

    # ---------------------------------------------------------------- PART 5: TRUTH HURTS
    Beat(kitchen_ev, tags=[("THAT EVENING", 0)], music="calm",
         lines=[("vo", "Then there's Mia. She's been quiet all week. Leaving the house every morning at eight, "
                       "coming home at five. Same as always. But something's off.")],
         actors=[A("me", ME, 600, face=1, expr="neutral", label=C(4813)),
                 A("mia", MIA, 2400, to=1300, at=0.2, style="slow", expr="sad", label=C(2301))],
         cams=[(0, ("track", "mia", 1.1)), ("s0%0.7", ("on", "mia", 1.5))]),
    Beat(kitchen_ev, music="calm",
         lines=[("me", "Hey... you okay?"), ("mia", "I'm fine."),
                ("vo", "You push. And push. Until she finally breaks.")],
         actors=[A("me", ME, 600, face=1, expr=[(0, "neutral"), ("e1+0.3", "suspicious")], label=C(4813)),
                 A("mia", MIA, 1300, face=-1, expr="neutral", label=C(2301, ["e1+0.1"]))],
         cams=[(0, ("two", "me", "mia", 1.15)), ("s1-0.05", ("on", "mia", 1.6)), ("s2", ("on", "me", 1.5)),
               ("s2%0.6", ("on", "mia", 1.9))]),
    Beat(kitchen_ev, music="calm",
         lines=[("mia", "I lost my job, okay? Three weeks ago. I've been sitting in the library all day, every day. "
                        "I didn't want Mom to worry. Promise me you won't tell her.")],
         actors=[A("mia", MIA, 1300, face=-1, expr="sad", label=C(2302))],
         cams=[(0, ("on", "mia", 1.7))]),
    Beat(kitchen_ev, music="calm",
         lines=[("vo", "You promise. And you mean it. But at dinner the next night, Mom smiles across the table."),
                ("mom", "So, Mia, how's work going?"), ("mia", "Busy, but good.")],
         actors=[A("me", ME, 560, face=1, expr="neutral", label=C(4813)),
                 A("mia", MIA, 860, face=1, expr="neutral", label=C(2302, ["e2+0.1"])),
                 A("dad", DAD, 1500, face=-1, expr="happy", label=C(11400)),
                 A("mom", MOM, 2100, to=1180, at="s0%0.3", pose="hold", prop=("plate",), expr="happy",
                   label=C(9998))],
         front=front_table(420, 1300),
         cams=[(0, ("wide", 1.0)), ("s1-0.05", ("on", "mom", 1.5)), ("s2-0.05", ("on", "mia", 1.6))]),
    Beat(kitchen_ev, music="calm",
         lines=[("vo", "And you just... can't stand it. You've spent all week catching lies. It's a reflex now."),
                ("me", "She got fired.")],
         actors=[A("me", ME, 560, face=1, expr=[(0, "suspicious"), ("s1", "neutral")], label=C(4813)),
                 A("mia", MIA, 860, face=-1, expr=[(0, "neutral"), ("e1", "shock")], label=C(2303)),
                 A("dad", DAD, 1500, face=-1, expr=[(0, "happy"), ("e1", "shock")], label=C(11400)),
                 A("mom", MOM, 1180, face=-1, expr=[(0, "happy"), ("e1", "shock")], label=C(9998))],
         front=front_table(420, 1300),
         cams=[(0, ("on", "me", 1.7)), ("s1-0.05", ("on", "me", 2.0)), ("e1+0.2", ("wide", 1.0))], hold=1.0),
    Beat(kitchen_ev, music="none",
         lines=[("vo", "Mom drops her fork. Dad stops chewing. Mia looks at you like you've stabbed her in the back, "
                       "and walks away without a word.")],
         actors=[A("me", ME, 560, face=1, expr="sad", label=C(4813)),
                 A("mia", MIA, 860, face=-1, expr="sad", label=C(2303), path=[("s0%0.6", 860), (None, 2600)],
                   style="fast"),
                 A("dad", DAD, 1500, face=-1, expr="shock", label=C(11400)),
                 A("mom", MOM, 1180, face=-1, expr="shock", label=C(9998))],
         front=front_table(420, 1300),
         cams=[(0, ("on", "mom", 1.6)), ("s0%0.2", ("on", "dad", 1.6)), ("s0%0.4", ("on", "mia", 1.6)),
               ("s0%0.65", ("wide", 1.0))],
         sfx=[(0.1, "clock"), ("s0%0.62", "scrape"), ("end-0.4", "slam")]),
    Beat(kitchen_ev, music="calm",
         lines=[("vo", "You look up at your own number. It didn't move. You told the truth. One hundred percent "
                       "honest. So why does it feel like the worst thing you've ever done?")],
         actors=[A("me", ME, 560, face=1, expr="sad", label=C(4813))],
         front=front_table(420, 1300),
         cams=[(0, ("on", "me", 2.0)), ("s0%0.5", ("on", "me", 1.5))], hold=1.2),

    # ---------------------------------------------------------------- PART 6: GRANDMA'S SECRET
    Beat(living, music="calm",
         lines=[("vo", "You can't sleep. So you sneak downstairs, and Grandma Rose is still awake, doing a crossword. "
                       "You sit next to her. You stare at her number. Ninety-six thousand, four hundred and forty. "
                       "And finally, you ask.")],
         actors=[A("gma", GMA, 1050, y=G - 40, face=-1, expr="neutral", pose="hold", prop=("book",),
                   label=C(96440)),
                 A("me", ME, -400, y=G - 40, to=700, at=0.2, style="tiptoe", expr="neutral", label=C(4813))],
         front=lambda c, t, b: couch(c, 480, G + 20, 880),
         cams=[(0, ("track", "me", 1.1)), ("s0%0.55", ("two", "me", "gma", 1.25)), ("s0%0.75", ("on", "gma", 1.9))]),
    Beat(living, music="calm",
         lines=[("me", "Grandma... have you ever lied?"), ("gma", "Oh, sweetheart. All the time.")],
         actors=[A("gma", GMA, 1050, y=G - 40, face=-1, expr=[(0, "neutral"), ("s1", "happy")], pose="hold",
                   prop=("book",), label=C(96440)),
                 A("me", ME, 700, y=G - 40, face=1, expr="neutral", label=C(4813))],
         front=lambda c, t, b: couch(c, 480, G + 20, 880)),
    Beat(bedroom_mirror, sepia=True, music="calm",
         lines=[("vo", "She tells you about Grandpa. For sixty years, every single morning, he'd fix his tie in the "
                       "mirror and ask, \"Rose, do I look handsome?\"")],
         actors=[A("gpa", GPA, -300, to=1000, at=0.2, expr="happy", pose=[(0, "down"), ("s0%0.55", "present")])],
         back=None,
         cams=[(0, ("track", "gpa", 1.1)), ("s0%0.6", ("on", "gpa", 1.6))]),
    Beat(living, music="calm",
         lines=[("gma", "And every morning, I said yes. Even the morning he wore the orange tie.")],
         actors=[A("gma", GMA, 1050, y=G - 40, face=-1, expr="happy", pose="hold", prop=("book",), label=C(96440)),
                 A("me", ME, 700, y=G - 40, face=1, expr=[(0, "neutral"), ("s0%0.75", "happy")], label=C(4813))],
         front=lambda c, t, b: couch(c, 480, G + 20, 880),
         cams=[(0, ("on", "gma", 1.6)), ("s0%0.7", ("two", "me", "gma", 1.25))]),
    Beat(kitchen, sepia=True, music="calm",
         lines=[("vo", "Twenty-one thousand mornings. Twenty-one thousand lies. And then there was the soup. "
                       "Every Sunday, Grandpa made the same terrible soup. She ate every single bowl and called it "
                       "delicious. That's another three thousand.")],
         actors=[A("gpa", GPA, 1900, to=1150, at="s0%0.3", expr="happy", pose="hold", prop=("bowl",)),
                 A("ygma", Char("#efc6a6", "#8a7aa8", pants="#5b5470", hair="bun", hair_c="#6b4a3a"), 520,
                   face=1, expr="happy")],
         cams=[(0, ("wide", 1.0)), ("s0%0.45", ("on", "gpa", 1.5)), ("s0%0.75", ("on", "ygma", 1.5))]),
    Beat(living, music="calm",
         lines=[("gma", "The last one was in the hospital. He asked me if he was going to be okay. I held his hand and "
                        "said, 'You'll be home by Sunday.'")],
         actors=[A("gma", GMA, 1050, y=G - 40, face=-1, expr="sad", pose="hold", prop=("book",), label=C(96440))],
         front=lambda c, t, b: couch(c, 480, G + 20, 880),
         cams=[(0, ("on", "gma", 1.7)), ("s0%0.6", ("on", "gma", 2.0))]),
    Beat(hands_closeup, sepia=True, music="none",
         lines=[("gma", "He wasn't. But he fell asleep smiling.")], bubbles=False,
         cams=[(0, ("at", 960, 650, 1.2))], hold=1.6),
    Beat(living, music="calm",
         lines=[("vo", "You look at the number above her head. And for the first time, it doesn't look like a crime. "
                       "It looks like sixty years of love... counted one by one.")],
         actors=[A("gma", GMA, 1050, y=G - 40, face=-1, expr="happy", pose="hold", prop=("book",), label=C(96440)),
                 A("me", ME, 700, y=G - 40, face=1, expr="sad", label=C(4813))],
         front=lambda c, t, b: couch(c, 480, G + 20, 880),
         cams=[(0, ("at", 1050, 340, 2.0)), ("s0%0.5", ("two", "me", "gma", 1.25))], hold=1.2),

    # ---------------------------------------------------------------- PART 7: THE ZERO MAN
    Beat(park, tags=[("THE NEXT DAY", 0)], crowd=3,
         lines=[("vo", "The next morning, you walk to the park to clear your head. And you see something you've never "
                       "seen before. An old man, alone on a bench, feeding pigeons. Above his head: zero.")],
         actors=[A("me", ME, -300, to=820, at=0.2, style="slow", expr="sad", label=C(4813)),
                 A("walter", WALTER, 1500, face=-1, expr="neutral", label=C(0), label_at="end-0.6")],
         back=lambda c, t, b: bench(c, 1520),
         front=lambda c, t, b: pigeons(c, 1450, t),
         cams=[(0, ("track", "me", 1.0)), ("s0%0.6", ("on", "walter", 1.4)), ("end-0.7", ("on", "walter", 2.0))],
         sfx=[("end-0.6", "sting")]),
    Beat(park,
         lines=[("vo", "Zero. Seventy years old, and not a single lie. You have to talk to him.")],
         actors=[A("me", ME, 820, to=1130, at="s0%0.6", expr="neutral", label=C(4813)),
                 A("walter", WALTER, 1500, face=-1, expr="neutral", label=C(0))],
         back=lambda c, t, b: bench(c, 1520),
         front=lambda c, t, b: pigeons(c, 1450, t, fly=b.ref("s0%0.75")),
         sfx=[("s0%0.75", "flutter")],
         cams=[(0, ("on", "walter", 2.0)), ("s0%0.5", ("wide", 1.0))]),
    Beat(park,
         lines=[("me", "Excuse me... have you ever told a lie?"), ("walter", "Never. Not once. Name's Walter."),
                ("vo", "You expect him to be proud. He isn't.")],
         actors=[A("me", ME, 1130, face=1, expr="neutral", label=C(4813)),
                 A("walter", WALTER, 1500, face=-1, expr=[(0, "neutral"), ("s2%0.5", "sad")], label=C(0))],
         back=lambda c, t, b: bench(c, 1520)),
    Beat(park, music="calm",
         lines=[("walter", "When my wife asked if I liked her paintings, I said no. When my son asked if I was proud "
                           "of him, I said, 'Not yet.' He was nineteen. He hasn't called me in twenty years.")],
         actors=[A("me", ME, 1130, face=1, expr="sad", label=C(4813)),
                 A("walter", WALTER, 1500, face=-1, expr="sad", label=C(0))],
         back=lambda c, t, b: bench(c, 1520),
         cams=[(0, ("on", "walter", 1.6)), ("s0%0.6", ("on", "walter", 1.9))]),
    Beat(park, music="calm",
         lines=[("walter", "Every word I ever said was true. And now there's no one left to hear them. The truth is a "
                           "tool, kid. Not a weapon.")],
         actors=[A("me", ME, 1130, face=1, expr="sad", label=C(4813)),
                 A("walter", WALTER, 1500, face=-1, expr="sad", label=C(0))],
         back=lambda c, t, b: bench(c, 1520),
         cams=[(0, ("wide", 1.0)), ("s0%0.5", ("on", "walter", 1.6))]),
    Beat(park, music="calm",
         lines=[("vo", "You sit with him for a long time. Before you leave, you tell him one thing."),
                ("me", "Call your son. Tell him the truth. The real one. That you're proud of him.")],
         actors=[A("me", ME, 1130, face=1, expr=[(0, "sad"), ("s1", "neutral")], label=C(4813),
                   path=[("e1+0.6", 1130), (None, -500)]),
                 A("walter", WALTER, 1500, face=-1, expr="neutral", label=C(0),
                   pose=[(0, "down"), ("e1+1.0", "phone")], prop=[(0, None), ("e1+1.0", ("phone",))])],
         back=lambda c, t, b: bench(c, 1520),
         cams=[(0, ("two", "me", "walter", 1.2)), ("s1-0.05", ("on", "me", 1.6)), ("e1+0.5", ("wide", 1.0)),
               ("e1+1.2", ("on", "walter", 1.6))], hold=3.0),

    # ---------------------------------------------------------------- PART 8: MAKING IT RIGHT
    Beat(lambda c, t: hallway(c, t, 0.0), music="calm",
         lines=[("vo", "You go home and knock on Mia's door. She doesn't answer. So you talk through it.")],
         actors=[A("me", ME, 200, to=1080, at=0.1, style="walk", expr="sad", label=C(4813),
                   pose=[(0, "down"), ("s0%0.72", "knock")])],
         sfx=[("s0%0.75", "knock")],
         cams=[(0, ("track", "me", 1.05)), ("s0%0.6", ("on", "me", 1.4))]),
    Beat(lambda c, t: hallway(c, t, 0.0), music="calm",
         lines=[("me", "I'm sorry. It wasn't my secret to tell. I thought being honest made me a good person. It "
                       "doesn't. Not on its own.")],
         actors=[A("me", ME, 1080, face=1, expr="sad", label=C(4813))],
         cams=[(0, ("on", "me", 1.5))]),
    Beat(lambda c, t: hallway(c, t, min(1.0, max(0.0, t - 0.2) * 1.5)), music="calm",
         lines=[("mia", "Mom's actually being really nice about it. She's helping me with my resume."),
                ("vo", "She crosses her arms."), ("mia", "I'm still mad at you.")],
         actors=[A("me", ME, 1000, face=1, expr="neutral", label=C(4813)),
                 A("mia", MIA, 1420, face=-1, expr=[(0, "neutral"), ("s2", "suspicious")],
                   pose=[(0, "down"), ("s1%0.5", "cross")], label=C(2303), hide_before=0.6)],
         cams=[(0, ("two", "me", "mia", 1.2)), ("s1", ("on", "mia", 1.6))]),
    Beat(lambda c, t: hallway(c, t, 1.0), music="calm",
         lines=[("vo", "No tick. She means it. Fair enough."),
                ("mia", "...But I'm making dinner tonight. And you're eating it.")],
         actors=[A("me", ME, 1000, face=1, expr=[(0, "neutral"), ("e1", "happy")], label=C(4813)),
                 A("mia", MIA, 1420, face=-1, expr=[(0, "suspicious"), ("s1%0.4", "happy")], pose="cross",
                   label=C(2303))],
         cams=[(0, ("at", 1420, 330, 2.0)), ("s1", ("two", "me", "mia", 1.2))]),
    Beat(kitchen_ev,
         lines=[("vo", "Dinner is... a disaster. The pasta is somehow both burnt AND raw. The sauce is a color that "
                       "does not exist in nature. Mia watches you take the first bite.")],
         actors=[A("me", ME, 560, face=1, expr=[(0, "neutral"), ("s0%0.3", "shock")], label=C(4813)),
                 A("dad", DAD, 1700, face=-1, expr="shock", label=C(11400)),
                 A("mom", MOM, 1480, face=-1, expr="neutral", label=C(9998)),
                 A("mia", MIA_COOK, -300, to=900, at=0.1, pose="hold", prop=("pot",), expr="happy", label=C(2303)),
                 A("gma", GMA, -200, to=280, at="s0%0.4", style="cane", pose="cane", expr="happy", label=C(96440))],
         front=front_table(420, 1400), sfx=[(0.2, "sizzle")],
         cams=[(0, ("track", "mia", 1.0)), ("s0%0.4", ("wide", 1.0)), ("s0%0.75", ("on", "me", 1.6))]),
    Beat(kitchen_ev,
         lines=[("mia", "So? How's my cooking?"),
                ("vo", "You think about Grandpa's orange tie. About Walter, alone on his bench. And you smile.")],
         actors=[A("gma", GMA, 280, face=1, pose="cane", expr="neutral", label=C(96440)),
                 A("me", ME, 560, face=1, expr=[(0, "think"), ("s1%0.8", "happy")], label=C(4813)),
                 A("mia", MIA_COOK, 900, face=-1, pose="hold", prop=("pot",), expr="happy", label=C(2303)),
                 A("mom", MOM, 1480, face=-1, expr="neutral", label=C(9998)),
                 A("dad", DAD, 1700, face=-1, expr="neutral", label=C(11400))],
         front=front_table(420, 1400),
         cams=[(0, ("on", "mia", 1.6)), ("s1", ("on", "me", 1.8))]),
    Beat(kitchen_ev,
         lines=[("me", "...Perfect.")],
         actors=[A("gma", GMA, 280, face=1, pose="cane", expr=[(0, "neutral"), ("e0+0.6", "happy")],
                   label=C(96440)),
                 A("me", ME, 560, face=1, expr="happy", label=C(4813, ["e0+0.2"])),
                 A("mia", MIA_COOK, 900, face=-1, pose="hold", prop=("pot",), expr="happy", label=C(2303)),
                 A("mom", MOM, 1480, face=-1, expr="happy", label=C(9998)),
                 A("dad", DAD, 1700, face=-1, expr="happy", label=C(11400))],
         front=front_table(420, 1400), hold=2.4,
         cams=[(0, ("on", "me", 1.8)), ("e0+0.15", ("on", "me", 2.1)), ("e0+0.9", ("wide", 1.0))]),
    Beat(park, dur=6.0, music="calm",
         actors=[A("walter", WALTER, 1500, face=-1, expr=[(0, "sad"), (2.6, "happy")], label=C(0)),
                 A("son", SON, 2200, to=1180, at=0.2, style="walk", expr=[(0, "neutral"), (2.6, "happy")],
                   pose=[(0, "down"), (3.4, "hug")], label=C(14200))],
         back=lambda c, t, b: bench(c, 1520),
         cams=[(0, ("wide", 1.0)), (2.6, ("two", "son", "walter", 1.4))]),

    # ---------------------------------------------------------------- PART 9: ENDING
    Beat(bathroom, music="calm",
         lines=[("vo", "That night, you look at your reflection. Four thousand, eight hundred and fourteen. And you "
                       "finally understand. The number was never about how bad someone is. It's about how many times "
                       "they had to choose between the truth... and someone they love.")],
         actors=[A("me", ME, -300, to=960, at=0.1, expr="think", label=C(4814))],
         cams=[(0, ("track", "me", 1.05)), ("s0%0.3", ("on", "me", 1.6)), ("s0%0.7", ("on", "me", 1.9))]),
    Beat(bathroom, music="none",
         lines=[("vo", "But then, a second number appears. Right below yours. A blue one. \"Lies told to you: "
                       "thirty-one thousand, five hundred and sixty.\" Which means somebody... has a lot of explaining "
                       "to do.")],
         actors=[A("me", ME, 960, face=1, expr=[(0, "think"), ("s0%0.2", "shock")], label=C(4814))],
         sfx=[("s0%0.12", "sting")],
         cams=[(0, ("at", 960, 340, 1.8)), ("s0%0.75", ("on", "me", 1.6))]),
    Beat(dark_card,
         lines=[("vo", "So here's the question. If you could see everyone's lie count, would you really want to know? "
                       "Or would you rather keep believing the soup is delicious?")],
         screen=label_card(["Would YOU want this power?", "Comment below"], [0.3, 2.0], [92, 60],
                           ["#ffffff", "#ff6b5e"]),
         sfx=[(0.0, "whoosh")], hold=2.5),
]


# ---------------------------------------------------------------- special overlays
def _phone(ctx, t, b):
    phone_screen(ctx, t, "Why can I see numbers above people's heads?",
                 [(b.ref("s0%0.5"), "You need more sleep", "Health tips  ·  Sleep better tonight"),
                  (b.ref("s0%0.68"), "You might be a wizard", "Quiz  ·  Which wizard are you?")], t_type=0.6)


_ph = BEATS[10]
_ph.bg = lambda c, t: None
_ph.screen = _phone
_ph.cams = [(0, ("wide", 1.0))]


def _blue(ctx, t, b):
    t0 = b.ref("s0%0.12")
    if t < t0:
        return
    k = ease_out_back((t - t0) / 0.35)
    fill_rrect(ctx, W / 2 - 330 * k, 770, 660 * k, 82, 18, (0.16, 0.42, 0.85, 0.95))
    if k > 0.7:
        font(ctx, 36)
        txt = "Lies told to you: 31,560"
        ctx.move_to(W / 2 - text_w(ctx, txt) / 2, 824)
        setc(ctx, "#ffffff")
        ctx.show_text(txt)


BEATS[-2].screen = _blue

for _i in (11, 12, 13, 14, 49):
    BEATS[_i].crowd_labels = True
