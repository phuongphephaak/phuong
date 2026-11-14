"""Build the Dien Bien Phu film.
  python build_m.py timeline | render [ids] | assemble out.mp4
"""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/phuong/video/dienbienphu")
from script_dbp import SCENES as _SC
SPEAKERS = {}
from vis_d import VIS, SFX, MUSIC, MUSIC_DIP, NO_LOGO, BLACK_TRANS, BED

SCENES = []
for sc in _SC:
    SCENES.append(sc)
    if sc["id"] == "title":
        SCENES.append(dict(id="sting", part=1, hold=3.2))

W, H, FPS, XF, SR = 1920, 1080, 30, 0.5, 44100
INTER = subprocess.run(["fc-match", "-f", "%{file}", "Inter:extrabold"], capture_output=True, text=True).stdout
INTER_SB = subprocess.run(["fc-match", "-f", "%{file}", "Inter:semibold"], capture_output=True, text=True).stdout
AUD = os.path.join(HERE, "aud")
ARCH = os.path.join(HERE, "arch")
SRC = {"wv": "why_vietnam.mpeg", "in2": "indo2.mpeg", "in88": "indo2388.mpeg"}
CROP = {"t": "scale=2016:1512,setsar=1,crop=1920:1080,", "tc": "scale=2112:1584,setsar=1,crop=1920:1080,"}
CLIPS, NORM, TMP = (os.path.join(HERE, d) for d in ("clips", "norm", "tmp"))
for d in (CLIPS, NORM, TMP):
    os.makedirs(d, exist_ok=True)


def run(cmd):
    subprocess.run(cmd, check=True)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode().strip())


# ------------------------------------------------------------------ timeline
def timeline():
    voices = json.load(open(os.path.join(AUD, "voices.json")))
    out, t = [], 0.0
    for sc in SCENES:
        v = voices.get(sc["id"], {})
        ev, cur = [], 0.5
        if v.get("nar") and sc.get("radio"):
            d = dur(v["nar"]); ev.append({"type": "nar", "file": v["nar"], "at": cur, "dur": d}); cur += d + 0.4
        elif v.get("nar"):
            d = dur(v["nar"]); ev.append({"type": "nar", "file": v["nar"], "at": cur, "dur": d}); cur += d + 0.35
        for r in v.get("radio", []):
            d = dur(r["file"])
            ev.append({"type": "radio", "file": r["file"], "at": cur, "dur": d, "sub": r["sub"], "speaker": SPEAKERS[r["speaker"]]})
            cur += d + 0.4
        D = round(max(3.0, cur + sc.get("hold", 0) + 0.45), 2)
        out.append({"id": sc["id"], "start": round(t, 3), "dur": D, "events": ev})
        t += D - XF
    total = round(t + XF, 2)
    json.dump({"scenes": out, "total": total}, open(os.path.join(HERE, "timeline.json"), "w"), ensure_ascii=False, indent=1)
    print("total", total, "s =", round(total / 60, 2), "min")


# ------------------------------------------------------------------ visuals
FLOW_GRADE = "crop=iw/1.045:ih/1.045,scale=1920:1080:flags=lanczos,eq=saturation=0.86:contrast=1.05:gamma=0.97,noise=alls=5:allf=t"
ARCH_GRADE = "scale=1920:1080:flags=lanczos,eq=contrast=1.08:brightness=-0.01,noise=alls=7:allf=t"


def seg_files(sid, kind, segs):
    parts = []
    for j, s in enumerate(segs):
        part = os.path.join(TMP, f"{sid}_s{j}.mp4")
        k = kind
        if kind == "mix":
            k, s = {"f": "flow", "p": "pre", "a": "arch"}[s[0]], s[1:]
        if k in ("flow", "pre"):
            name, st, en = s
            src = os.path.join(HERE, k if k == "flow" else "pre", name + ".mp4")
            d = (en if en is not None else dur(src)) - st
            vf = (FLOW_GRADE if k == "flow" else "scale=1920:1080") + f",fps={FPS},format=yuv420p"
        else:
            name, st, d, crop = s
            src = os.path.join(ARCH, SRC[name])
            vf = CROP[crop] + ARCH_GRADE + f",fps={FPS},format=yuv420p"
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(st), "-t", f"{d:.3f}", "-i", src, "-vf", vf, "-an",
             "-c:v", "libx264", "-crf", "17", "-preset", "veryfast", part])
        parts.append(part)
    return parts


def fit(parts, D, out, sid):
    lst = os.path.join(TMP, f"{sid}_list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    joined = os.path.join(TMP, f"{sid}_joined.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
    L = dur(joined)
    json.dump({"L": L, "parts": [dur(p) for p in parts]}, open(os.path.join(TMP, f"{sid}_fit.json"), "w"))
    vf = []
    if L < D:
        sp = max(0.55, L / D)
        vf.append(f"setpts=PTS/{sp:.4f}")
        if sp < 0.97:
            vf.append(f"minterpolate=fps={FPS}:mi_mode=blend")
    vf += [f"tpad=stop_mode=clone:stop_duration={D}", f"trim=0:{D}", "setpts=PTS-STARTPTS", "format=yuv420p"]
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", joined, "-vf", ",".join(vf), "-an", "-c:v", "libx264", "-crf", "17",
         "-preset", "veryfast", "-r", str(FPS), out])


def photo(sid, p, D, out):
    from PIL import Image, ImageFilter
    src = next(os.path.join(HERE, "photos", p["key"] + e) for e in (".jpg", ".png") if os.path.exists(os.path.join(HERE, "photos", p["key"] + e)))
    im = Image.open(src).convert("RGB")
    tw, th = W * 2, H * 2
    s = max(tw / im.width, th / im.height)
    r = im.width / im.height
    if r >= 1.25:
        im2 = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        x, y = (im2.width - tw) // 2, (im2.height - th) // 2
        fr = im2.crop((x, y, x + tw, y + th))
    else:
        bg = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        x, y = (bg.width - tw) // 2, (bg.height - th) // 2
        bg = bg.crop((x, y, x + tw, y + th)).filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * 0.45))
        s2 = min(tw / im.width, th / im.height) * 0.94
        fg = im.resize((round(im.width * s2), round(im.height * s2)), Image.LANCZOS)
        bg.paste(fg, ((tw - fg.width) // 2, (th - fg.height) // 2)); fr = bg
    frame = os.path.join(TMP, sid + "_frame.jpg"); fr.save(frame, quality=95)
    n = int(D * FPS)
    vf = f"zoompan=z='1.0+0.1*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}," \
         "eq=saturation=0.75:contrast=1.08,vignette=PI/4.5,noise=alls=7:allf=t"
    if p.get("dark"):
        vf += ",eq=brightness=-0.08:saturation=0.5"
    run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-t", str(D), "-i", frame,
         "-vf", vf + ",format=yuv420p", "-c:v", "libx264", "-crf", "17", "-preset", "veryfast", out])


def render_raw(sc, D):
    out = os.path.join(CLIPS, sc["id"] + ".mp4")
    if os.path.exists(out) and abs(dur(out) - D) < 0.08:
        return out
    kind, p = VIS[sc["id"]]
    if kind in ("flow", "pre", "arch", "mix"):
        fit(seg_files(sc["id"], kind, p["segs"]), D, out, sc["id"])
    elif kind == "photo":
        photo(sc["id"], p, D, out)
    elif kind == "gfx":
        run([sys.executable, os.path.join(HERE, "gfx3.py"), p["kind"], str(D), out, json.dumps(p["spec"], ensure_ascii=False)])
    return out


def esc_file(text, tag):
    f = os.path.join(TMP, f"txt_{abs(hash((text, tag)))}.txt")
    open(f, "w", encoding="utf-8").write(text)
    return f


def captions(sc, D, has_radio):
    kind = VIS[sc["id"]][0]
    if not sc.get("cap") or kind == "gfx":
        return []
    cap = sc["cap"]
    big, small = (cap[0].split(" – ", 1) + [""])[:2] if " – " in cap[0] else (cap[0], cap[1] if len(cap) > 1 else "")
    if re.fullmatch(r"\d\d:\d\d", big.strip()):
        big = big.strip().replace(":", " : ")
    a = f"if(lt(t,0.4),0,if(lt(t,0.9),(t-0.4)/0.5,if(gt(t,{D - 0.7}),max(0,({D - 0.3}-t)/0.4),1)))"
    x, y = (90, H - 110) if not has_radio else (90, 250)
    fs = []
    if small:
        fs.append(f"drawtext=fontfile={INTER}:textfile={esc_file(small, 's')}:fontsize=32:fontcolor=0x40D6FF:x={x}:y={y - 112}:"
                  f"alpha='{a}':shadowcolor=black@0.85:shadowx=3:shadowy=3")
    fs.append(f"drawtext=fontfile={INTER}:textfile={esc_file(big, 'b')}:fontsize=72:fontcolor=white:x={x}:y={y - 60}:"
              f"alpha='{a}':shadowcolor=black@0.85:shadowx=4:shadowy=4")
    return fs


def subs(events):
    fs = []
    for e in (e for e in events if e["type"] == "radio"):
        a, b = e["at"], e["at"] + e["dur"] + 0.3
        en = f"between(t,{a:.2f},{b:.2f})"
        fs.append(f"drawtext=fontfile={INTER}:textfile={esc_file('[ ' + e['speaker'] + ' ]', 'k')}:fontsize=28:fontcolor=0xF0B54A:"
                  f"x=(w-text_w)/2:y=h-205:enable='{en}':shadowcolor=black@0.9:shadowx=2:shadowy=2")
        fs.append(f"drawtext=fontfile={INTER_SB}:textfile={esc_file(e['sub'], 'u')}:fontsize=40:fontcolor=white:x=(w-text_w)/2:"
                  f"y=h-152:enable='{en}':box=1:boxcolor=black@0.55:boxborderw=14")
    return fs


def normalize(sc, tl, raw):
    out = os.path.join(NORM, sc["id"] + ".mp4")
    D = tl["dur"]
    has_radio = any(e["type"] == "radio" for e in tl["events"])
    vf = [f"scale={W}:{H}", f"tpad=stop_mode=clone:stop_duration={D}", f"trim=0:{D}", "setpts=PTS-STARTPTS"]
    vf += captions(sc, D, has_radio) + subs(tl["events"])
    lab = f"drawtext=fontfile={INTER_SB}:text='HÌNH ẢNH MINH HỌA':fontsize=20:fontcolor=white@0.55:x=w-text_w-40:y=h-46"
    kind, p = VIS[sc["id"]]
    if kind == "flow":
        vf.append(lab)
    elif kind == "mix" and any(sg[0] == "f" for sg in p["segs"]):
        fj = json.load(open(os.path.join(TMP, f"{sc['id']}_fit.json")))
        sp = max(0.55, fj["L"] / D) if fj["L"] < D else 1.0
        t, wins = 0.0, []
        for sg, pd in zip(p["segs"], fj["parts"]):
            if sg[0] == "f":
                wins.append(f"between(t,{t / sp:.2f},{(t + pd) / sp:.2f})")
            t += pd
        vf.append(lab + ":enable='" + "+".join(wins) + "'")
    vf.append("format=yuv420p")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-vf", ",".join(vf), "-an", "-c:v", "libx264", "-crf", "17",
         "-preset", "veryfast", "-r", str(FPS), out])


def render(ids=None):
    tl = {s["id"]: s for s in json.load(open(os.path.join(HERE, "timeline.json")))["scenes"]}
    todo = [sc for sc in SCENES if not ids or sc["id"] in ids]
    todo.sort(key=lambda sc: (VIS[sc["id"]][0] != "gfx", -tl[sc["id"]]["dur"]))

    def job(sc):
        try:
            raw = render_raw(sc, tl[sc["id"]]["dur"])
            normalize(sc, tl[sc["id"]], raw)
            import glob
            for f in [raw] + glob.glob(os.path.join(TMP, sc["id"] + "_s*.mp4")) + glob.glob(os.path.join(TMP, sc["id"] + "_joined.mp4")):
                if os.path.exists(f) and f != os.path.join(NORM, sc["id"] + ".mp4"):
                    os.remove(f)
            print("done", sc["id"], flush=True)
        except Exception as e:
            print("FAIL", sc["id"], e, flush=True)
    with ThreadPoolExecutor(5) as ex:
        list(ex.map(job, todo))


# ------------------------------------------------------------------ audio
def load(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def rms(x, db):
    return x * (10 ** (db / 20) / np.sqrt(np.mean(x ** 2) + 1e-12))


def place(buf, x, t):
    i = int(t * SR)
    if i >= len(buf) or i < 0:
        return
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n]


def find_sfx(n):
    for d in (AUD, os.path.join(HERE, "..", "midway", "aud"), os.path.join(HERE, "..", "doc10", "aud"), os.path.join(HERE, "..", "audio")):
        p = os.path.join(d, n + ".mp3")
        if os.path.exists(p):
            return p
    raise FileNotFoundError(n)


def looped(x, n):
    if len(x) >= n:
        return x[:n]
    xf = int(3 * SR)
    out = x.copy()
    while len(out) < n:
        a = out[:-xf]; tail = out[-xf:] * np.linspace(1, 0, xf)[:, None]; head = x[:xf] * np.linspace(0, 1, xf)[:, None]
        out = np.concatenate([a, tail + head, x[xf:]])
    return out[:n]


def sub_times(tl):
    """Pick ~4 moments for the subscribe reminder: scene without radio/captions/gfx text, not in the climax."""
    sc_by = {s["id"]: s for s in SCENES}
    picks, targets = [], [140, 400, 640, 900]
    for tg in targets:
        best = None
        for s in tl["scenes"]:
            sc = sc_by[s["id"]]
            if sc.get("part") in (7,) or s["id"] in NO_LOGO or any(e["type"] == "radio" for e in s["events"]):
                continue
            if sc.get("cap") or VIS[s["id"]][0] == "gfx" or s["dur"] < 7.5:
                continue
            t0 = s["start"] + 0.8
            if best is None or abs(t0 - tg) < abs(best - tg):
                best = t0
        if best and all(abs(best - p) > 120 for p in picks):
            picks.append(round(best, 2))
    return picks


def mix(out_wav):
    tl = json.load(open(os.path.join(HERE, "timeline.json")))
    total = tl["total"]
    N = int((total + 1) * SR)
    voice, fx, mus = (np.zeros((N, 2), np.float32) for _ in range(3))
    starts = {s["id"]: s["start"] for s in tl["scenes"]}
    durs = {s["id"]: s["dur"] for s in tl["scenes"]}
    cache = {}
    for s in tl["scenes"]:
        for e in s["events"]:
            place(voice, rms(load(e["file"]), -19 if e["type"] == "nar" else -21), s["start"] + e["at"])
        for name, off, vol in SFX.get(s["id"], []):
            if name not in cache:
                cache[name] = rms(load(find_sfx(name)), -20)
            x = cache[name][:int((s["dur"] - off + XF) * SR)].copy()
            f = min(len(x), int(0.5 * SR))
            if f:
                x[-f:] *= np.linspace(1, 0, f)[:, None]
            place(fx, x * vol, s["start"] + off)
    bed = rms(load(find_sfx(BED)), -20) * 0.12
    place(fx, looped(bed, N), 0)
    for t0 in tl.get("subscribe", []):
        place(fx, rms(load(find_sfx("click_bell")), -20) * 0.8, t0 + 2.3)
    cues = sorted(MUSIC, key=lambda m: starts[m[1]])
    for i, (name, sid, vol) in enumerate(cues):
        st = starts[sid]
        end = starts[cues[i + 1][1]] + 2.5 if i + 1 < len(cues) else total
        x = looped(rms(load(find_sfx(name)), -20), int((end - st) * SR)) * vol
        fi, fo = int(2 * SR), int(3 * SR)
        x[:fi] *= np.linspace(0, 1, fi)[:, None]; x[-fo:] *= np.linspace(1, 0, fo)[:, None]
        place(mus, x, st)
    gain = np.ones(N, np.float32)
    for sid in MUSIC_DIP:
        a, b = int(starts[sid] * SR), int((starts[sid] + durs[sid]) * SR)
        ramp = int(0.6 * SR)
        g = np.full(b - a, 0.12, np.float32); g[:ramp] = np.linspace(1, 0.12, ramp); g[-ramp:] = np.linspace(0.12, 1, ramp)
        gain[a:b] = np.minimum(gain[a:b], g)
    env = np.abs(voice).max(axis=1)
    k = int(0.3 * SR)
    cs = np.concatenate([[0.0], np.cumsum(env, dtype=np.float64)])
    idx = np.arange(len(env)); lo = np.clip(idx - k // 2, 0, len(env)); hi = np.clip(idx + k // 2, 0, len(env))
    env = ((cs[hi] - cs[lo]) / np.maximum(hi - lo, 1)).astype(np.float32)
    duck = 1 - 0.55 * np.clip(env / (env.max() * 0.05 + 1e-9), 0, 1)
    m = voice + fx * (0.75 + 0.25 * duck[:, None]) + mus * (duck * gain)[:, None]
    m = np.tanh(m * 1.2) / 1.2
    m = m[:int(total * SR)]
    fo = int(4 * SR); m[-fo:] *= np.linspace(1, 0, fo)[:, None]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-",
                          "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), out_wav], stdin=subprocess.PIPE)
    p.stdin.write(m.astype(np.float32).tobytes()); p.stdin.close(); p.wait()


# ------------------------------------------------------------------ assemble
def xfade_chain(items, out, first_offset_base=0.0):
    """items: list of (path, dur, transition_into_this)."""
    inputs, chain, prev, t = [], [], "0:v", items[0][1]
    for i, (p, d, tr) in enumerate(items):
        inputs += ["-i", p]
        if i == 0:
            continue
        off = t - XF
        chain.append(f"[{prev}][{i}:v]xfade=transition={tr}:duration={XF}:offset={off:.3f}[v{i}]")
        prev, t = f"v{i}", off + d
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(chain), "-map", f"[{prev}]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out])
    return t


def assemble(out):
    tlj = json.load(open(os.path.join(HERE, "timeline.json")))
    sc = tlj["scenes"]
    tr = lambda s: "fadeblack" if s["id"] in BLACK_TRANS else "fade"
    chunks, size = [], 18
    video = os.path.join(TMP, "video_only.mp4")
    reuse = os.environ.get("REUSE") and os.path.exists(video)
    for c in range(0, 0 if reuse else len(sc), size):
        grp = sc[c:c + size]
        path = os.path.join(TMP, f"chunk{c // size}.mp4")
        d = xfade_chain([(os.path.join(NORM, s["id"] + ".mp4"), s["dur"], tr(s)) for s in grp], path)
        chunks.append((path, d, tr(grp[0])))
        print("chunk", c // size, round(d, 2), flush=True)
    if not reuse:
        xfade_chain(chunks, video)
        for c in chunks:
            os.remove(c[0])
    # overlays: logo (except title/sting/end) and subscribe reminders
    subt = sub_times(tlj); tlj["subscribe"] = subt
    json.dump(tlj, open(os.path.join(HERE, "timeline.json"), "w"), ensure_ascii=False, indent=1)
    logo = os.path.join(TMP, "logo.png"); subm = os.path.join(TMP, "subscribe.mov")
    if not os.path.exists(logo):
        run([sys.executable, os.path.join(HERE, "gfx3.py"), "logo", logo])
    if not os.path.exists(subm):
        run([sys.executable, os.path.join(HERE, "gfx3.py"), "subscribe", subm])
    nolog = "+".join(f"between(t,{s['start']:.2f},{s['start'] + s['dur']:.2f})" for s in sc if s["id"] in NO_LOGO)
    inputs = ["-i", video, "-loop", "1", "-i", logo]
    for t0 in subt:
        inputs += ["-itsoffset", f"{t0:.2f}", "-i", subm]
    fc = [f"[1:v]format=rgba[lg]", f"[0:v][lg]overlay=36:28:enable='not({nolog})'[b0]"]
    prev = "b0"
    for i, t0 in enumerate(subt):
        fc.append(f"[{prev}][{i + 2}:v]overlay=0:0:eof_action=pass:enable='between(t,{t0:.2f},{t0 + 6:.2f})'[b{i + 1}]")
        prev = f"b{i + 1}"
    wav = os.path.join(TMP, "mix.wav")
    mix(wav)
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-i", wav, "-filter_complex", ";".join(fc), "-map", f"[{prev}]",
         "-map", f"{len(subt) + 2}:a", *(["-c:v", "libx264", "-preset", "medium", "-b:v", os.environ["FINAL_BR"], "-maxrate", "3600k", "-bufsize", "7200k"]
           if os.environ.get("FINAL_BR") else ["-c:v", "libx264", "-preset", "medium", "-crf", "19"]), "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k" if os.environ.get("FINAL_BR") else "192k", "-t", str(tlj["total"]), "-movflags", "+faststart", out])
    print("done", out, dur(out), "subscribe at", subt)


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "timeline":
        timeline()
    elif c == "render":
        render(sys.argv[2:] or None)
    elif c == "assemble":
        assemble(sys.argv[2])
