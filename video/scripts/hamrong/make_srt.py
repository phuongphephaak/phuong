"""Tạo phụ đề .srt và mốc chương từ timeline.json + script_midway.py."""
import json, re, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../hamrong"))
from script_hamrong import SCENES, PARTS

tl, out = sys.argv[1], sys.argv[2]
sc = {s["id"]: s for s in SCENES}
T = json.load(open(tl))

def chunks(text, maxc=84):
    out = []
    for sent in re.split(r"(?<=[.?!])\s+", text.strip()):
        while len(sent) > maxc:
            cut = sent.rfind(", ", 0, maxc)
            if cut < maxc * 0.35:
                cut = sent.rfind(" ", 0, maxc)
            out.append(sent[:cut + 1].strip()); sent = sent[cut + 1:].strip()
        if sent: out.append(sent)
    return out

def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

subs, chap, seen = [], [], set()
for s in T["scenes"]:
    meta = sc.get(s["id"], {})
    p = meta.get("part")
    if p and p not in seen:
        seen.add(p); chap.append((s["start"], PARTS[p]))
    for e in s["events"]:
        t0 = s["start"] + e["at"]
        if e["type"] == "nar" and meta.get("nar"):
            parts = chunks(meta["nar"]); tot = sum(len(c) for c in parts); t = t0
            for c in parts:
                d = e["dur"] * len(c) / tot
                subs.append((t, t + d - 0.05, c)); t += d
        elif e["type"] == "radio":
            subs.append((t0, t0 + e["dur"], "[Bộ đàm] " + e["sub"]))
subs.sort()
with open(out, "w", encoding="utf-8") as f:
    for i, (a, b, c) in enumerate(subs, 1):
        f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{c}\n\n")
for t, n in chap:
    print(f"{int(t)//60}:{int(t)%60:02} {n}")
