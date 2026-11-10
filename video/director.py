"""Beat-based director: timing from voice clips, actors that walk, auto camera cuts."""
import math
import re
from engine import (W, H, draw_char, draw_cat, counter_label, plus_one, bubble, caption, tag, ease,
                    ease_out_back)
from scenes import GROUND

LEAD, GAP, TAIL = 0.35, 0.35, 0.55
SPEED = {"walk": 250, "run": 620, "slow": 140, "cane": 85, "tiptoe": 120, "fast": 380}
PHASE = {"walk": 0.028, "run": 0.021, "slow": 0.034, "cane": 0.045, "tiptoe": 0.04, "fast": 0.024}
STRIDE = {"walk": 1.0, "run": 1.45, "slow": 0.6, "cane": 0.45, "tiptoe": 0.55, "fast": 1.15}
LEAN = {"run": 0.12, "fast": 0.05, "tiptoe": 0.08}


class Line:
    def __init__(self, who, text):
        self.who, self.text = who, text
        self.dur = 0.0
        self.start = 0.0
        self.wav = None

    @property
    def end(self):
        return self.start + self.dur


class Actor:
    def __init__(self, name, c, x, s=0.82, y=None, to=None, at=0, style="walk", expr="neutral", pose="down",
                 face=None, look=None, label=None, label_at=0, prop=None, cat=False, hide_before=None,
                 hide_after=None, path=None):
        self.name, self.c, self.x0, self.s = name, c, x, s
        self.y = GROUND if y is None else y
        # path: list of (time_ref, x) waypoints; or simple to/at
        self.path = path or ([(at, x), (None, to)] if to is not None else None)
        self.style, self.expr, self.pose, self.face, self.look = style, expr, pose, face, look
        self.label, self.label_at, self.prop, self.cat = label, label_at, prop, cat
        self.hide_before, self.hide_after = hide_before, hide_after


class Counter:
    def __init__(self, base, ticks=(), color="dark"):
        self.base, self.ticks, self.color = base, list(ticks), color


class Beat:
    def __init__(self, bg, lines=(), actors=(), cams=None, dur=None, tags=(), sfx=(), front=None, back=None,
                 screen=None, sepia=False, crowd=0, music="normal", hold=TAIL, bubbles=True, cap=None):
        self.bg, self.actors, self.cams = bg, list(actors), cams
        self.lines = [Line(w, t) for (w, t) in lines]
        self.fixed, self.tags, self.sfx = dur, list(tags), list(sfx)
        self.front, self.back, self.screen, self.sepia = front, back, screen, sepia
        self.crowd, self.music, self.hold, self.bubbles, self.cap = crowd, music, hold, bubbles, cap
        self.dur = dur or 0
        self.start = 0.0

    # ------------------------------------------------------------ timing
    def layout(self):
        t = LEAD if self.lines else 0
        for ln in self.lines:
            ln.start = t
            t += ln.dur + GAP
        natural = (t - GAP + self.hold) if self.lines else 0
        self.dur = max(self.fixed or 0, natural)
        # resolve actor paths
        for a in self.actors:
            if a.path:
                pts = []
                for ref, x in a.path:
                    pts.append([None if ref is None else self.ref(ref), x])
                for i in range(1, len(pts)):
                    if pts[i][0] is None:
                        dist = abs(pts[i][1] - pts[i - 1][1])
                        pts[i][0] = pts[i - 1][0] + dist / SPEED[a.style]
                a._pts = pts
            for k in ("expr", "pose", "prop"):
                v = getattr(a, k)
                if isinstance(v, list):
                    setattr(a, k, [(self.ref(tt), val) for tt, val in v])
            for k in ("hide_before", "hide_after", "label_at"):
                v = getattr(a, k)
                if isinstance(v, str):
                    setattr(a, k, self.ref(v))
            if a.label is not None:
                a.label.ticks = [self.ref(r) for r in a.label.ticks]
        self.sfx = [(self.ref(r), k) for r, k in self.sfx]
        self.tags = [(txt, self.ref(r)) for txt, r in self.tags]

    def ref(self, r):
        """'s2' start of line 2, 'e2' end, 's2%0.5' fraction into line, 'e1+0.4', 'end-1', or float."""
        if isinstance(r, (int, float)):
            return float(r)
        m = re.fullmatch(r"(s|e|end)(\d*)(%[\d.]+)?([+-][\d.]+)?", r)
        kind, idx, frac, off = m.groups()
        if kind == "end":
            base = self.dur if self.dur else 999
        else:
            ln = self.lines[int(idx)]
            base = ln.start if kind == "s" else ln.end
            if frac:
                base = ln.start + ln.dur * float(frac[1:])
        return base + (float(off) if off else 0.0)

    # ------------------------------------------------------------ actor state
    def actor_x(self, a, t):
        if not a.path:
            return a.x0, False, 0.0, None
        pts = a._pts
        if t <= pts[0][0]:
            return pts[0][1], False, 0.0, None
        dist = 0.0
        for (t0, x0), (t1, x1) in zip(pts, pts[1:]):
            if t <= t1:
                k = (t - t0) / max(1e-6, t1 - t0)
                x = x0 + (x1 - x0) * k
                dist += abs(x - x0)
                return x, True, dist, 1 if x1 > x0 else -1
            dist += abs(x1 - x0)
        return pts[-1][1], False, dist, None

    def speaking(self, name, t):
        for ln in self.lines:
            if ln.who == name and ln.start <= t <= ln.end:
                return ln
        return None

    def draw_actors(self, ctx, t, anchors):
        order = sorted(self.actors, key=lambda a: a.y)
        for a in order:
            if a.hide_before is not None and t < a.hide_before:
                continue
            if a.hide_after is not None and t > a.hide_after:
                continue
            x, moving, dist, direction = self.actor_x(a, t)
            if a.face is not None and not moving:
                facing = a.face
            elif direction is not None:
                facing = direction
            else:
                facing = getattr(a, "_lastdir", 1) if a.path else (a.face or (1 if x < W / 2 else -1))
            if direction is not None:
                a._lastdir = direction
            if a.cat:
                draw_cat(ctx, x, a.y, a.s, t)
                anchors[a.name] = (x, a.y - 330 * a.s, a.s, facing)
                continue
            expr = pick(a.expr, t)
            pose = pick(a.pose, t)
            prop = pick(a.prop, t)
            talking = self.speaking(a.name, t) is not None
            look = a.look if a.look is not None else 0.6
            walk = dist * PHASE[a.style] if moving else None
            draw_char(ctx, a.c, x, a.y, a.s, t, expr=expr, pose=pose, look=look, talking=talking,
                      flip=facing < 0, walk=walk, stride=STRIDE[a.style],
                      lean=LEAN.get(a.style, 0.0) if moving else 0.0, prop=prop)
            hx, hy = x, a.y - 700 * a.s
            anchors[a.name] = (x, a.y - 600 * a.s, a.s, facing)
            if a.label is not None and t >= a.label_at:
                show_label(ctx, hx, hy, a.label, t, a.label_at, a.s)


def pick(v, t):
    if isinstance(v, list):
        cur = v[0][1]
        for tt, val in v:
            if t >= tt:
                cur = val
        return cur
    return v


def show_label(ctx, x, y, cnt, t, appear, s):
    v = cnt.base + sum(1 for tt in cnt.ticks if t >= tt)
    pop = flash = 0.0
    last = None
    for tt in cnt.ticks:
        if t >= tt:
            d = t - tt
            pop = max(pop, math.exp(-d * 9) * math.sin(min(d * 25, math.pi)))
            flash = max(flash, math.exp(-d * 4))
            last = tt
    k = ease_out_back((t - appear) / 0.25)
    sc = max(0.05, k) * min(1.25, s / 0.82)
    if cnt.color == "error":
        counter_label(ctx, x, y, 0, pop=pop, flash=1.0, s=sc)
        return
    counter_label(ctx, x, y, v, pop=pop, flash=flash, s=sc)
    if last is not None:
        plus_one(ctx, x + 60, y - 40, t - last)
