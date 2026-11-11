"""Episode 2: What If You Could Hear What Pets Really Think? (~9 min)."""
import math
from engine import Char, W, H, font, text_w, setc, fill_rrect, ellipse, circle, rect, line, ease_out_back
from scenes import GROUND, street, kitchen, living, couch, desk_note, dark_card
from scenes2 import park, bench, pigeons, cafe_in, cafe_table
from scenes3 import (bedroom, bed, blanket, lying_char, jay_room, front_yard, porch, porch_bench, vet, flyer)
from animals import dog, cat_walk, fish_tank, hamster_cage, parrot, rabbit, squirrel
from director import Beat, Actor as A
from story_full import ME, MIA, GMA, JAY, MOM, DAD, MAILMAN, label_card

G = GROUND
S = 0.82

LEE = Char("#e8bf9e", "#c77d9b", pants="#5b5470", hair="bun", hair_c="#bdb6ad", extra=("glasses",), blink_phase=1.2)
GIRL = Char("#f0c49b", "#f2c94c", pants="#3d5a80", hair="ponytail", hair_c="#7a4a2a", blink_phase=0.4)
SADMAN = Char("#d9a47a", "#6b7a8f", pants="#3d4250", hair="short", hair_c="#3b2a20", blink_phase=2.1)
BENCHMAN = Char("#c98e64", "#a3b18a", pants="#4a4038", hair="cap", hair_c="#c0392b", blink_phase=1.7)
SHOEMAN = Char("#efc6a6", "#4a5568", pants="#2d3340", hair="slick", hair_c="#3a2a20", blink_phase=0.9)
VETDOC = Char("#d2a07a", "#f4f6f6", pants="#7fb3d5", hair="bob", hair_c="#2b2420", extra=("glasses",),
              blink_phase=2.4)
KID_ME = Char("#f2c9a0", "#7fb3d5", hair="short", hair_c="#3b2a20", blink_phase=0.3)

# thought-bubble colours per animal
PURPLE, YELLOW, BLUE, BROWN, ORANGE, GREEN, GRAY = ((0.7, 0.5, 0.95), (0.95, 0.75, 0.2), (0.3, 0.6, 0.95),
                                                     (0.65, 0.45, 0.3), (0.95, 0.55, 0.35), (0.3, 0.75, 0.4),
                                                     (0.6, 0.6, 0.65))


def noop(ctx, x, y, s, t, **_):
    pass


def biscuit(name="biscuit", x=900, y=None, s=0.62, **kw):
    return A(name, None, x, s=s, y=G if y is None else y, drawfn=cat_walk, head=300, thought=PURPLE, **kw)


def max_dog(x=900, **kw):
    kw.setdefault("kw", {"expr": "happy"})
    return A("max", None, x, s=0.72, drawfn=dog, head=310, thought=YELLOW, **kw)


def pepper(x=900, **kw):
    kw.setdefault("kw", {"expr": "neutral", "body": "#8a6a52", "old": True, "size": 0.9})
    return A("pepper", None, x, s=0.72, drawfn=dog, head=290, thought=BROWN, **kw)


def lying(c, expr):
    return lambda ctx, t, b: (bed(ctx), lying_char(ctx, c, 640, G - 330, S, t, expr=pick_expr(expr, t, b)),
                              blanket(ctx))


def lying_night(c, expr):
    return lambda ctx, t, b: (bed(ctx, night=True), lying_char(ctx, c, 640, G - 330, S, t,
                                                               expr=pick_expr(expr, t, b)), blanket(ctx, night=True))


def pick_expr(expr, t, b):
    if isinstance(expr, list):
        cur = expr[0][1]
        for tt, v in expr:
            if t >= b.ref(tt):
                cur = v
        return cur
    return expr


def bowl(shiny):
    def d(ctx, t, b):
        on = shiny if not callable(shiny) else shiny(t, b)
        x, y = 1300, G
        if on:
            ellipse(ctx, x, y - 20, 70, 26, "#c9d1d9")
            ellipse(ctx, x, y - 30, 56, 16, "#eef2f5")
            circle(ctx, x + 10, y - 32, 9, "#e0a84a")
        else:
            ellipse(ctx, x, y - 20, 70, 26, "#c0392b")
            ellipse(ctx, x, y - 32, 52, 14, "#7a4a2a")
    return d


def vacuum_cat(ctx, x, y, s, t, walk=None, facing=1, **_):
    ellipse(ctx, x, y - 25, 120, 30, "#3b3f45")
    ellipse(ctx, x, y - 40, 110, 24, "#5a5f68")
    circle(ctx, x + 60, y - 42, 6, "#5fd18b")
    cat_walk(ctx, x, y - 50, s, t, walk=None, facing=facing)


def tank_counter(x=600):
    return A("bubbles", None, x, s=0.8, y=560, drawfn=fish_tank, head=230, thought=BLUE)


BEATS = [
    # ---------------------------------------------------------------- PART 0
    Beat(bedroom, music="calm",
         lines=[("vo", "You wake up, and the first thing you see is your cat, Biscuit, staring at you. That's normal. "
                       "She does that every morning. But today, you hear something."),
                ("biscuit", "If he doesn't feed me in three minutes, the glass goes on the floor.")],
         back=lying(ME, [(0, "sleep"), ("s0%0.12", "neutral"), ("s1", "shock")]),
         actors=[biscuit(x=1810, y=G - 260, s=0.5)],
         front=lambda c, t, b: (fill_rrect(c, 1730 + min(60, t * 4), G - 330, 40, 70, 6, (0.8, 0.9, 1, 0.8))),
         cams=[(0, ("wide", 1.0)), ("s0%0.35", ("at", 1810, 560, 1.8)), ("s1-0.1", ("at", 1500, 520, 1.3))],
         sfx=[("s1-0.25", "ding")]),
    Beat(bedroom,
         lines=[("vo", "You look around. No one else is here. Just you... and the cat."),
                ("biscuit", "Two minutes.")],
         back=lambda c, t, b: (bed(c), lying_char(c, ME, 640, G - 330, S, t, expr="shock") if t < b.ref("e1+0.3")
                               else None, blanket(c)),
         actors=[biscuit(x=1810, y=G - 260, s=0.5),
                 A("me", ME, 900, expr="shock", hide_before="e1+0.3", path=[("e1+0.3", 900), (None, -500)],
                   style="run")],
         front=lambda c, t, b: fill_rrect(c, 1790, G - 330, 40, 70, 6, (0.8, 0.9, 1, 0.8)),
         cams=[(0, ("at", 640, 600, 1.5)), ("s1", ("at", 1810, 560, 1.8)), ("e1+0.2", ("wide", 1.0))], hold=1.4),
    Beat(bedroom,
         lines=[("vo", "You don't know what's happening yet. But by the end of this week, you'll find out what every "
                       "animal in your life really thinks about you. And one of them has been keeping a secret for "
                       "years.")],
         back=lambda c, t, b: (bed(c), blanket(c)),
         actors=[biscuit(x=1500, s=0.6, path=[(0.3, 1500), (None, -400)], style="slow")],
         cams=[(0, ("track", "biscuit", 1.2))]),
    Beat(dark_card, dur=3.6, screen=label_card(["WHAT IF YOU COULD HEAR", "WHAT PETS REALLY THINK?"], [0.15, 0.45],
                                               [76, 96], ["#ffffff", "#ff6b5e"]),
         sfx=[(0.0, "whoosh")]),

    # ---------------------------------------------------------------- PART 1
    Beat(kitchen, tags=[("THE NEXT MORNING", 0)],
         lines=[("vo", "In the kitchen, your dog Max runs in so fast he slides into the fridge."),
                ("max", "BEST DAY EVER! BEST DAY EVER! ...Also, yesterday was the best day ever. Every day is the "
                        "best day ever!"),
                ("vo", "Okay. That one makes sense.")],
         actors=[A("me", ME, 420, expr=[(0, "neutral"), ("s1", "happy")]),
                 max_dog(x=-400, path=[(0.3, -400), (None, 1380)], style="run")],
         sfx=[("s0%0.85", "scrape"), ("s0%0.97", "slam")],
         cams=[(0, ("track", "max", 1.0)), ("s1", ("on", "max", 1.5)), ("s2", ("two", "me", "max", 1.05))]),
    Beat(kitchen,
         lines=[("mom", "Who's a good boy? Who's the best boy in the world?"),
                ("max", "ME! It's me! I'm the good boy! ...Wait, is there another dog? Is HE the good boy?"),
                ("vo", "Max spins around three times looking for the other dog. There is no other dog.")],
         actors=[A("me", ME, 420, expr="happy"),
                 A("mom", MOM, 2300, path=[(0, 2300), (None, 1500)], expr="happy", pose=[(0, "down"), ("s0", "present")]),
                 A("dad", DAD, 2700, path=[(0.6, 2700), (None, 1800)], expr="neutral"),
                 max_dog(x=1150, path=[("s2", 1150), (None, 1050), (None, 1150), (None, 1050), (None, 1150),
                                       (None, 1050), (None, 1150)], style="run")],
         cams=[(0, ("wide", 1.0)), ("s0", ("on", "mom", 1.5)), ("s1", ("on", "max", 1.5)), ("s2", ("wide", 1.05))]),
    Beat(kitchen,
         lines=[("captainS", "Hello! Hello! Pretty bird!"),
                ("captain", "I know exactly what I'm saying. I just like watching them get excited."),
                ("vo", "Even the parrot next door is smarter than he looks.")],
         actors=[A("captain", None, 960, y=530, s=0.75, drawfn=parrot, head=190, thought=GREEN),
                 A("captainS", None, 960, y=530, s=0.75, drawfn=noop, head=190)],
         cams=[(0, ("at", 960, 420, 1.7)), ("s2", ("at", 960, 470, 1.3))]),
    Beat(kitchen,
         lines=[("bubbles", "Whoa, a castle! ...Whoa, a castle! ...Whoa, a castle!"),
                ("vo", "So it's true. Goldfish really do forget everything in three seconds.")],
         actors=[tank_counter(450)],
         cams=[(0, ("at", 450, 430, 2.0)), ("s1", ("at", 450, 450, 1.6))]),
    Beat(kitchen,
         lines=[("vo", "You need to be sure you're not going crazy. So you kneel down next to Biscuit and whisper,"),
                ("me", "Can you understand me?"),
                ("biscuit", "Obviously. I'm just ignoring you."),
                ("vo", "Great. Your cat has been understanding you this whole time. She just doesn't care.")],
         actors=[A("mia", MIA, 2500, path=[(0.2, 2500), (None, -500)], pose="phone", prop=("phone",)),
                 A("me", ME, 600, face=1, expr=[(0, "neutral"), ("s3", "sad")]),
                 biscuit(x=900, s=0.62, path=[("e2+0.3", 900), (None, 2600)], style="walk")],
         sfx=[("e2+0.1", "scrape")],
         cams=[(0, ("wide", 1.0)), ("s1", ("on", "me", 1.5)), ("s2", ("on", "biscuit", 1.6)),
               ("s3", ("wide", 1.0))]),

    # ---------------------------------------------------------------- PART 2
    Beat(park, crowd=4,
         lines=[("vo", "You take Max for a walk, and the park is suddenly very, very loud.")],
         actors=[A("me", ME, -300, path=[(0, -300), (None, 900)]),
                 max_dog(x=0, path=[(0, 0), (None, 1200)])],
         cams=[(0, ("track", "me", 1.0))]),
    Beat(park,
         lines=[("d1", "That man's shoes smell like cheese. Ten out of ten."),
                ("d2", "I am a wolf. I am a wolf. I am a... is that a leaf?")],
         actors=[A("shoe", SHOEMAN, 1350, face=-1, expr="neutral"),
                 A("d1", None, 1080, s=0.65, drawfn=dog, head=300, thought=GRAY,
                   kw={"expr": "happy", "body": "#f1ece4", "ear": "#d9cfc0", "size": 0.95}),
                 A("d2", None, 450, s=0.5, drawfn=dog, head=300, thought=GRAY,
                   kw={"expr": "neutral", "body": "#4a4038", "size": 0.8})],
         back=lambda c, t, b: (ellipse(c, 560 + 30 * math.sin(t), G - 30, 22, 10, "#c98e3a")),
         cams=[(0, ("two", "d1", "shoe", 1.4)), ("s1", ("on", "d2", 1.8))]),
    Beat(park, dur=3.4,
         lines=[("dogs", "SQUIRREL!")],
         actors=[A("sq", None, -200, s=1.0, drawfn=squirrel, head=100, path=[(0.2, -200), (None, 2400)],
                   style="run"),
                 A("d1", None, 1080, s=0.65, drawfn=dog, head=300, thought=GRAY,
                   kw={"expr": "happy", "body": "#f1ece4", "ear": "#d9cfc0", "size": 0.95},
                   path=[("e0", 1080), (None, 2600)], style="run"),
                 A("dogs", None, 700, s=0.72, drawfn=dog, head=310, thought=GRAY,
                   kw={"expr": "happy", "body": "#e0a84a"}, path=[("e0+0.2", 700), (None, 2600)], style="run"),
                 A("d2", None, 450, s=0.5, drawfn=dog, head=300, thought=GRAY,
                   kw={"expr": "shock", "body": "#4a4038", "size": 0.8},
                   path=[("e0+0.1", 450), (None, 2600)], style="run")],
         cams=[(0, ("wide", 1.0))], sfx=[("e0", "bark")]),
    Beat(park, music="calm",
         lines=[("sad", "He doesn't laugh anymore. I bring him the ball every day. Maybe tomorrow he'll laugh."),
                ("vo", "And for a second, the park doesn't feel funny anymore. Some of these thoughts are jokes. "
                       "Some of them aren't.")],
         actors=[A("sadman", SADMAN, 2200, path=[(0, 2200), (None, -400)], style="slow", expr="sad"),
                 A("sad", None, 2450, s=0.5, drawfn=dog, head=300, thought=GRAY,
                   kw={"expr": "sad", "body": "#c9a27a", "size": 0.8}, path=[(0, 2450), (None, -150)],
                   style="slow")],
         cams=[(0, ("track", "sad", 1.4)), ("s1", ("track", "sadman", 1.1))]),
    Beat(park,
         lines=[("vo", "On a bench, a group of pigeons is watching people eat."),
                ("pig", "Okay, the guy with the sandwich. On three, we all look sad."),
                ("vo", "It works. He gives them half his sandwich. That night, you write down everything you know.")],
         actors=[A("benchman", BENCHMAN, 1520, face=-1, expr=[(0, "happy"), ("s2", "sad")],
                   pose=[(0, "hold"), ("s2", "present")]),
                 A("pig", None, 1100, y=G + 20, s=1.0, drawfn=noop, head=40, thought=GRAY)],
         back=lambda c, t, b: bench(c, 1520),
         front=lambda c, t, b: pigeons(c, 1150, t),
         sfx=[("s1", "flutter")],
         cams=[(0, ("wide", 1.0)), ("s1", ("at", 1150, 760, 1.8)), ("s2", ("two", "benchman", "pig", 1.2))]),
    Beat(lambda c, t: desk_note(c, t, [("RULES", t - 0.3), ("1. I can hear animals think", t - 1.0),
                                       ("2. They can't hear me (I hope)", t - 1.9),
                                       ("3. Goldfish really forget", t - 2.8),
                                       ("4. Pigeons are criminals", t - 3.7)]),
         dur=5.4, cams=[(0, ("wide", 1.0))],
         sfx=[(0.3, "scribble"), (1.0, "scribble"), (1.9, "scribble"), (2.8, "scribble"), (3.7, "scribble")]),

    # ---------------------------------------------------------------- PART 3
    Beat(lambda c, t: front_yard(c, t, 0), tags=[("THE NEXT DAY", 0)],
         lines=[("vo", "The next day, you decide to use your power for good. Your neighbor, Mrs. Lee, is worried. "
                       "Her dog won't eat."),
                ("lee", "He hasn't touched his food in three days. I don't know what's wrong.")],
         actors=[A("me", ME, -300, path=[(0, -300), (None, 600)]),
                 A("lee", LEE, 2300, path=[(0.5, 2300), (None, 1000)], expr="sad"),
                 A("leedog", None, 1550, s=0.6, drawfn=dog, head=300, thought=GRAY, face=-1,
                   kw={"expr": "sad", "body": "#a86f4c"})],
         back=bowl(True),
         cams=[(0, ("wide", 1.0)), ("s1", ("on", "lee", 1.5))]),
    Beat(lambda c, t: front_yard(c, t, 0),
         lines=[("leedog", "There's a scary dog living in my new bowl. He copies everything I do."),
                ("vo", "It's his reflection. You swap the shiny bowl for an old one. He eats everything in ten "
                       "seconds.")],
         actors=[A("me", ME, 600, face=1),
                 A("lee", LEE, 1000, face=1, expr=[(0, "sad"), ("s1%0.7", "happy")]),
                 A("leedog", None, 1550, s=0.6, drawfn=dog, head=300, thought=GRAY, face=-1,
                   kw={"expr": [(0, "shock"), ("s1%0.55", "happy")], "body": "#a86f4c"})],
         back=bowl(lambda t, b: t < b.ref("s1%0.45")),
         cams=[(0, ("at", 1400, 700, 1.8)), ("s1%0.5", ("wide", 1.0))]),
    Beat(lambda c, t: front_yard(c, t, 0), crowd=0,
         lines=[("vo", "By the weekend, you're the neighborhood pet expert. A parrot that won't stop screaming? "
                       "He's bored. He wants a new toy. A cat that keeps hiding? She hates the new vacuum cleaner. "
                       "And honestly, so do you.")],
         actors=[A("me", ME, 500, face=1, expr="happy"),
                 A("lee", LEE, 820, face=-1, expr="happy", pose="hug"),
                 A("n1", MOM, 2400, path=[(0.8, 2400), (None, 1250)], expr="happy"),
                 A("n2", DAD, 2800, path=[(1.4, 2800), (None, 1550)], expr="neutral", pose="hold", prop=("book",)),
                 A("n3", JAY, 3200, path=[(2.0, 3200), (None, 1850)], expr="happy")],
         screen=flyer,
         cams=[(0, ("wide", 1.0))]),
    Beat(lambda c, t: front_yard(c, t, 1),
         lines=[("vo", "A little girl brings you her rabbit. She says he keeps barking. Rabbits don't bark."),
                ("rab", "I live with three dogs. I am also a dog. Woof."),
                ("vo", "You decide not to tell him.")],
         actors=[A("me", ME, 600, face=1, expr=[(0, "neutral"), ("s2", "think")]),
                 A("girl", GIRL, 1250, s=0.55, face=-1, expr="happy"),
                 A("rab", None, 1050, s=0.7, drawfn=rabbit, head=250, thought=GRAY)],
         cams=[(0, ("wide", 1.0)), ("s1", ("at", 1060, 720, 1.9)), ("s2", ("on", "me", 1.5))]),
    Beat(lambda c, t: front_yard(c, t, 2),
         lines=[("vo", "Even Max has a secret. Every day, he barks at the mailman like a monster. Everyone thinks he "
                       "hates him."),
                ("max", "HI! HI! I LOVE YOU! PLEASE PET ME! WHY DO YOU ALWAYS RUN AWAY?!")],
         actors=[A("mail", MAILMAN, 2300, path=[(0, 2300), (None, 1400), ("s1%0.5", 1400), (None, 1700)],
                   expr=[(0, "neutral"), ("s0%0.6", "shock")]),
                 max_dog(x=900, kw={"expr": "excited"}, face=1)],
         sfx=[("s0%0.55", "bark"), ("s1%0.3", "bark")],
         cams=[(0, ("track", "mail", 1.0)), ("s1", ("on", "max", 1.5))]),
    Beat(lambda c, t: front_yard(c, t, 2),
         lines=[("vo", "He doesn't hate the mailman. He's in love with the mailman."),
                ("mail", "Huh. Fifteen years on this street, and nobody's dog has ever liked me."),
                ("vo", "He laughs. It's the first time you've ever seen him laugh.")],
         actors=[A("me", ME, 300, path=[(0.2, 300), (None, 800)]),
                 A("mail", MAILMAN, 1700, face=-1, expr=[(0, "neutral"), ("s1", "happy")],
                   pose=[(0, "down"), ("s1", "present")]),
                 max_dog(x=900, path=[(0.6, 900), (None, 1450)], kw={"expr": "excited"})],
         cams=[(0, ("wide", 1.0)), ("s1", ("on", "mail", 1.5)), ("s2", ("two", "mail", "max", 1.3))]),
    Beat(jay_room,
         lines=[("vo", "Then you visit Jay. He has a hamster named Nugget. And Nugget has a lot to say.")],
         actors=[A("me", ME, -300, path=[(0.1, -300), (None, 700)]),
                 A("nugget", None, 1450, y=G - 330, s=0.8, drawfn=hamster_cage, head=300, thought=ORANGE)],
         cams=[(0, ("track", "me", 1.0)), ("s0%0.6", ("at", 1450, 560, 1.6))]),
    Beat(jay_room,
         lines=[("nugget", "Every night, he tells me about a girl. Mia. Mia this, Mia that. Mia laughed at my joke. "
                           "I'm a hamster. I don't care.")],
         actors=[A("me", ME, 700, face=1, expr="neutral"),
                 A("nugget", None, 1450, y=G - 330, s=0.8, drawfn=hamster_cage, head=300, thought=ORANGE)],
         cams=[(0, ("at", 1450, 520, 1.7))]),
    Beat(jay_room,
         lines=[("vo", "Mia. Your sister Mia. Your best friend has a crush on your sister. And the hamster knows "
                       "everything.")],
         actors=[A("me", ME, 700, face=1, expr="shock"),
                 A("nugget", None, 1450, y=G - 330, s=0.8, drawfn=hamster_cage, head=300, thought=ORANGE)],
         sfx=[(0.1, "sting")],
         cams=[(0, ("on", "me", 2.0)), ("s0%0.6", ("wide", 1.0))]),

    # ---------------------------------------------------------------- PART 3.5
    Beat(lambda c, t: bedroom(c, t, night=True), tags=[("THAT NIGHT", 0)], music="calm",
         lines=[("vo", "But there's a problem. Animals never stop thinking. Not even at night."),
                ("stray", "Is that a bird? No, it's a bag."),
                ("max", "Running... running... the ball... so many balls..."),
                ("bubbles", "Whoa, a castle!"),
                ("vo", "You haven't slept properly in three days. And you're starting to learn things you really "
                       "didn't need to know.")],
         back=lying_night(ME, [(0, "neutral"), ("s4", "sad")]),
         actors=[A("stray", None, 1440, y=490, s=0.35, drawfn=cat_walk, head=300, thought=GRAY,
                   kw={"body": "#5a5f68"}),
                 max_dog(x=1400, kw={"expr": "neutral", "lying": True}),
                 A("bubbles", None, 1810, y=G - 260, s=0.45, drawfn=fish_tank, head=230, thought=BLUE)],
         cams=[(0, ("wide", 1.0)), ("s1", ("at", 1440, 380, 1.8)), ("s2", ("on", "max", 1.6)),
               ("s3", ("at", 1810, 560, 1.8)), ("s4", ("at", 640, 600, 1.6))]),

    # ---------------------------------------------------------------- PART 4
    Beat(jay_room,
         lines=[("vo", "And you can't help yourself."), ("me", "So... Mia, huh?"),
                ("jay", "Who told you that? I never told anyone. Only..."),
                ("jay", "...Only Nugget.")],
         actors=[A("me", ME, 600, face=1, expr="sly"),
                 A("jay", JAY, -300, path=[(0, -300), (None, 1000)], expr=[(0, "happy"), ("s2", "shock")],
                   face=-1),
                 A("nugget", None, 1450, y=G - 330, s=0.8, drawfn=hamster_cage, head=300, thought=ORANGE,
                   kw={"running": [(0, True), ("s3", False)]})],
         sfx=[("e1+0.1", "can")],
         cams=[(0, ("wide", 1.0)), ("s1", ("on", "me", 1.6)), ("s2", ("on", "jay", 1.6)),
               ("s3", ("at", 1300, 520, 1.4))]),
    Beat(jay_room,
         lines=[("vo", "You try to explain. You can hear animals think. Jay stares at you for a long time."),
                ("jay", "So you've been spying on me. Through my hamster."),
                ("me", "It's not like that! I didn't ask him! He just... thinks really loudly!"),
                ("jay", "Do you know how weird that sounds? Do you know how weird ALL of this sounds?")],
         actors=[A("me", ME, 600, face=1, expr=[(0, "neutral"), ("s2", "shock")], pose=[(0, "down"), ("s2", "shrug")]),
                 A("jay", JAY, 1000, face=-1, expr="suspicious", pose=[(0, "down"), ("s3", "hips")]),
                 A("nugget", None, 1450, y=G - 330, s=0.8, drawfn=hamster_cage, head=300, thought=ORANGE,
                   kw={"running": False})]),
    Beat(jay_room,
         lines=[("vo", "Okay. When you say it like that, it sounds bad.")],
         actors=[A("me", ME, 600, path=[(0.3, 600), (None, -500)], style="slow", expr="sad"),
                 A("jay", JAY, 1000, face=-1, expr="suspicious", pose="point")],
         sfx=[("end-0.5", "slam")], hold=1.0),

    # ---------------------------------------------------------------- PART 5
    Beat(porch, tags=[("SUNDAY", 0)], music="calm",
         lines=[("vo", "On Sunday, you visit Grandma Rose. Her old dog, Pepper, walks next to her like always. "
                       "Slowly. Carefully. Pepper is fourteen years old."),
                ("gma", "Look at her. Still my best walking partner."),
                ("gma", "Fourteen years, and she's never missed a single walk. Not one. Not even in the snow.")],
         actors=[A("me", ME, 300, face=1, expr="happy"),
                 A("gma", GMA, 2000, path=[(0.2, 2000), (None, 1200)], style="cane", pose="cane", expr="happy"),
                 pepper(x=2250, path=[(0.2, 2250), (None, 1500)], style="cane")],
         cams=[(0, ("track", "pepper", 1.1)), ("s1", ("on", "gma", 1.5)), ("s2", ("two", "gma", "pepper", 1.3))]),
    Beat(porch, music="calm",
         lines=[("vo", "Grandma smiles. And then you hear Pepper."),
                ("pepper", "My legs hurt. They hurt every day now. But Rose smiles when we walk together. So I walk.")],
         actors=[A("gma", GMA, 1200, face=1, pose="cane", expr="happy"), pepper(x=1500)],
         cams=[(0, ("on", "gma", 1.5)), ("s1", ("on", "pepper", 1.8))]),
    Beat(porch, music="calm",
         lines=[("vo", "You look at Pepper. She's been hiding her pain. For Grandma."),
                ("pepper", "Don't tell her. She has enough to worry about."),
                ("vo", "Last week, you learned that some secrets aren't yours to tell. But this one is different. "
                       "This one is hurting someone.")],
         actors=[A("me", ME, 900, face=1, expr="sad"), pepper(x=1300, face=-1)],
         cams=[(0, ("on", "me", 1.6)), ("s1", ("on", "pepper", 1.8)), ("s2", ("two", "me", "pepper", 1.2))]),
    Beat(porch, music="calm",
         lines=[("me", "Grandma... I think Pepper's legs hurt. A lot. I think she's hiding it so you won't worry."),
                ("gma", "Oh, Pepper. You silly old girl. You don't have to be strong for me."),
                ("pepper", "Yes, I do. That's my job.")],
         actors=[A("me", ME, 300, path=[(0, 300), (None, 640)], face=1, expr="sad"),
                 A("gma", GMA, 980, face=-1, expr=[(0, "neutral"), ("s1", "sad")], pose=[(0, "cane"), ("s1", "hug")]),
                 pepper(x=1350, face=-1)],
         back=lambda c, t, b: porch_bench(c, 820),
         cams=[(0, ("two", "me", "gma", 1.25)), ("s1", ("on", "gma", 1.5)), ("s2", ("on", "pepper", 1.8))]),
    Beat(vet, tags=[("ONE WEEK LATER", 0)], music="calm",
         lines=[("vo", "The vet says it's arthritis. Pepper gets medicine, a soft new bed, and shorter walks. "
                       "A week later, she's walking better than she has in years.")],
         actors=[A("doc", VETDOC, 1500, face=-1, expr="happy", pose="present", prop=("coffee",)),
                 A("gma", GMA, 1100, face=1, pose="cane", expr="happy"),
                 pepper(x=750, y=G - 300, kw={"expr": "happy", "body": "#8a6a52", "old": True, "size": 0.9})],
         cams=[(0, ("wide", 1.0))]),
    Beat(porch,
         lines=[("pepper", "Thank you, kid. Don't tell Rose I said thanks. I have a reputation.")],
         actors=[A("me", ME, 1500, face=-1, expr="happy"),
                 pepper(x=-200, path=[(0, -200), (None, 1150)], style="walk",
                        kw={"expr": "happy", "body": "#8a6a52", "old": True, "size": 0.9})],
         cams=[(0, ("track", "pepper", 1.2)), ("s0%0.5", ("on", "pepper", 1.7))], hold=1.0),

    # ---------------------------------------------------------------- PART 6
    Beat(living_day := (lambda c, t: living(c, t, evening=False)),
         lines=[("biscuit", "Your hair looks like a broom."), ("biscuit", "You call that singing?"),
                ("biscuit", "I'm sitting on your homework because your homework is wrong.")],
         actors=[A("me", ME, 700, face=1, expr=[(0, "neutral"), ("s1", "happy"), ("s2", "sad")],
                   pose=[(0, "down"), ("s1", "mic"), ("s2", "down")], prop=[(0, None), ("s1", ("mic",)), ("s2", None)]),
                 biscuit(x=1150, s=0.62)],
         front=lambda c, t, b: fill_rrect(c, 1080, G - 20, 160, 22, 4, "#f6f2e8") if t > b.ref("s2") else None,
         cams=[(0, ("two", "me", "biscuit", 1.3)), ("s1", ("on", "me", 1.5)), ("s2", ("on", "biscuit", 1.7))]),
    Beat(lambda c, t: living(c, t, evening=False),
         lines=[("vo", "Meanwhile, Biscuit has been insulting you all week. You're pretty sure she hates you. You're "
                       "also pretty sure she's planning to replace you with the robot vacuum. She seems to like it "
                       "more.")],
         actors=[A("me", ME, 500, face=1, expr=[(0, "sad"), ("s0%0.55", "suspicious")]),
                 A("vac", None, 2200, s=0.62, drawfn=vacuum_cat, head=330,
                   path=[("s0%0.5", 2200), (None, 900), (None, 1500)], style="slow")],
         cams=[(0, ("on", "me", 1.5)), ("s0%0.5", ("track", "vac", 1.2))]),
    Beat(lambda c, t: bedroom(c, t, night=True), tags=[("3:00 AM", 0)], music="calm",
         lines=[("vo", "Then, one night, you can't sleep. You keep your eyes closed. And you feel Biscuit climb "
                       "onto your chest. Like she does every night.")],
         back=lying_night(ME, "sleep"),
         actors=[biscuit(x=1700, y=G - 300, s=0.5, path=[("s0%0.45", 1700), (None, 860)], style="tiptoe")],
         cams=[(0, ("wide", 1.0)), ("s0%0.45", ("track", "biscuit", 1.3))]),
    Beat(lambda c, t: bedroom(c, t, night=True), music="calm",
         lines=[("biscuit", "Still breathing. Good."),
                ("biscuit", "I check every night. Ever since he got that fever when he was six. Nobody else was "
                            "awake. I was.")],
         back=lying_night(ME, "sleep"),
         actors=[biscuit(x=860, y=G - 300, s=0.5)],
         cams=[(0, ("at", 820, 560, 1.7)), ("s1", ("at", 860, 520, 2.0))]),
    Beat(lambda c, t: bedroom(c, t, night=False), sepia=True, music="calm",
         lines=[("vo", "You remember that fever. You were six. Mom said the cat wouldn't leave your bed for three "
                       "days. You always thought it was a funny story. Mom tells it at every family dinner. Nobody "
                       "ever asked why the cat stayed.")],
         back=lambda c, t, b: (bed(c), lying_char(c, KID_ME, 640, G - 330, 0.55, t, expr="sad"), blanket(c)),
         actors=[biscuit(x=980, y=G - 300, s=0.48), A("mom", MOM, 1650, face=-1, expr="sad")],
         cams=[(0, ("wide", 1.0)), ("s0%0.4", ("at", 900, 560, 1.5))]),
    Beat(lambda c, t: bedroom(c, t, night=True), music="calm",
         lines=[("biscuit", "Silly human. Somebody has to watch you."),
                ("vo", "You don't open your eyes. You don't say a word. But for the first time, you understand. "
                       "Biscuit doesn't hate you. She's been guarding you your whole life.")],
         back=lying_night(ME, [(0, "sleep"), ("s1%0.6", "sleep_smile")]),
         actors=[biscuit(x=860, y=G - 300, s=0.5)],
         cams=[(0, ("at", 860, 520, 2.0)), ("s1", ("at", 760, 600, 1.4))], hold=1.4),

    # ---------------------------------------------------------------- PART 7
    Beat(lambda c, t: front_yard(c, t, 3), tags=[("THE NEXT MORNING", 0)],
         lines=[("vo", "The next morning, you go to Jay's house."),
                ("me", "I'm sorry. I shouldn't have listened to Nugget. And I really shouldn't have said anything.")],
         actors=[A("me", ME, -300, path=[(0, -300), (None, 700)], expr="sad"),
                 A("jay", JAY, 1150, face=-1, expr="suspicious", pose="cross", hide_before="s0%0.7")],
         cams=[(0, ("track", "me", 1.0)), ("s1", ("on", "me", 1.5))]),
    Beat(lambda c, t: front_yard(c, t, 3),
         lines=[("vo", "Jay is quiet for a moment. Then he looks at the floor."),
                ("jay", "...Did Nugget say if Mia likes me back?"),
                ("me", "Nugget's a hamster, man. Ask her yourself.")],
         actors=[A("me", ME, 700, face=1, expr=[(0, "sad"), ("s2", "happy")]),
                 A("jay", JAY, 1150, face=-1, expr=[(0, "suspicious"), ("s1", "sad"), ("e2", "happy")],
                   pose=[(0, "cross"), ("s1", "down")])]),
    Beat(jay_room,
         lines=[("nugget", "Finally. Maybe now he'll talk to HER instead of me.")],
         actors=[A("me", ME, 600, face=1, expr="happy"), A("jay", JAY, 950, face=-1, expr="happy"),
                 A("nugget", None, 1450, y=G - 330, s=0.8, drawfn=hamster_cage, head=300, thought=ORANGE)],
         cams=[(0, ("two", "me", "jay", 1.2)), ("s0", ("at", 1450, 520, 1.6))]),
    Beat(cafe_in, tags=[("TWO DAYS LATER", 0)],
         lines=[("vo", "Two days later, Jay finally does it. He walks up to Mia at the coffee shop. No hamster. "
                       "No secret messages. Just Jay."),
                ("jay", "Hey, Mia. Do you... maybe want to get pizza sometime?"),
                ("mia", "Took you long enough.")],
         actors=[A("me", ME, 420, face=1, expr="happy", pose=[(0, "down"), ("e2", "present")]),
                 A("jay", JAY, -300, path=[(0.3, -300), (None, 1150)], expr=[(0, "neutral"), ("e2", "happy")]),
                 A("mia", MIA, 1650, face=-1, expr="happy")],
         front=lambda c, t, b: (cafe_table(c, 1400), cafe_table(c, 420)),
         cams=[(0, ("track", "jay", 1.05)), ("s1", ("on", "jay", 1.5)), ("s2", ("on", "mia", 1.5)),
               ("e2+0.3", ("wide", 1.0))]),
    Beat(kitchen,
         lines=[("vo", "At home, you feed Biscuit. Right on time. She takes one bite and looks up at you."),
                ("biscuit", "Acceptable."),
                ("vo", "From Biscuit, that's basically \"I love you.\"")],
         actors=[A("me", ME, -300, path=[(0, -300), (None, 650)], expr="happy"),
                 biscuit(x=1000, s=0.62)],
         back=lambda c, t, b: (ellipse(c, 1110, G - 14, 55, 18, "#7a5cb8"), ellipse(c, 1110, G - 24, 40, 10, "#b8733a")),
         cams=[(0, ("wide", 1.0)), ("s1", ("on", "biscuit", 1.8)), ("s2", ("two", "me", "biscuit", 1.2))]),

    # ---------------------------------------------------------------- PART 8
    Beat(lambda c, t: living(c, t, evening=True),
         lines=[("vo", "That evening, Biscuit jumps onto the couch and stares at you. A long, slow stare."),
                ("biscuit", "So. You can hear us now."),
                ("biscuit", "Don't look so surprised. We've always been able to hear YOU.")],
         actors=[A("me", ME, 760, y=G - 40, face=1, expr=[(0, "neutral"), ("s1", "shock")]),
                 biscuit(x=1080, y=G - 150, s=0.55)],
         front=lambda c, t, b: couch(c, 480, G + 20, 880),
         sfx=[("s1", "sting")],
         cams=[(0, ("two", "me", "biscuit", 1.25)), ("s1", ("on", "biscuit", 1.8)), ("s2", ("on", "me", 1.8))]),
    Beat(lambda c, t: living(c, t, evening=True), music="none",
         lines=[("biscuit", "Every song you sing in the shower. Every time you talk to yourself. Every time you said "
                            "you'd clean your room."),
                ("biscuit", "We heard all of it.")],
         actors=[A("me", ME, 760, y=G - 40, face=1, expr="shock"),
                 biscuit(x=1080, y=G - 150, s=0.55),
                 max_dog(x=200, kw={"expr": "neutral"}),
                 A("bubbles", None, 1700, y=G - 230, s=0.5, drawfn=fish_tank, head=230),
                 A("captain", None, 1560, y=380, s=0.5, drawfn=parrot, head=190)],
         back=lambda c, t, b: fill_rrect(c, 1640, G - 230, 140, 230, 8, "#7a5a40"),
         front=lambda c, t, b: couch(c, 480, G + 20, 880),
         cams=[(0, ("on", "biscuit", 1.6)), ("s0%0.4", ("at", 500, 600, 1.3)), ("s0%0.7", ("at", 1600, 480, 1.3)),
               ("s1", ("wide", 1.0))], hold=1.2),
    Beat(dark_card,
         lines=[("vo", "So here's the question. If you could hear what your pet really thinks... would you want to "
                       "know? Or are some thoughts better left unheard?")],
         screen=label_card(["What would YOUR pet", "say about you?"], [0.3, 0.6], [88, 88], ["#ffffff", "#ff6b5e"]),
         sfx=[(0.0, "whoosh")], hold=2.5),
]
