"""Build the ~10 minute HMS Coventry film from script_data.py.

  python build.py timeline            -> timeline.json (scene durations from narration/radio lengths)
  python build.py render [ids...]     -> clips/<id>.mp4 (raw visuals, parallel) + norm/<id>.mp4 (captions, subs)
  python build.py assemble <out.mp4>  -> crossfaded video + mixed audio
"""
import json, math, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from script_data import SCENES, MUSIC

W, H, FPS, XF, SR = 1920, 1080, 30, 0.6, 44100
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
AUD = os.path.join(HERE, "aud")
CLIPS, NORM, TMP = (os.path.join(HERE, d) for d in ("clips", "norm", "tmp"))
for d in (CLIPS, NORM, TMP):
    os.makedirs(d, exist_ok=True)
SPEAKER = {"pilot1": "Phi công A-4 · trưởng biên đội", "pilot2": "Phi công A-4 · số 2",
           "ops": "HMS Coventry · phòng tác chiến"}
CAPT = {"radar_contact": "HMS Coventry · chỉ huy", "radar_second": "HMS Broadsword",
        "map_geometry": "HMS Broadsword", "abandon": "HMS Coventry · thuyền trưởng", "rescue2": "HMS Coventry"}


def run(cmd):
    subprocess.run(cmd, check=True)


def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", path]).decode().strip())


# ------------------------------------------------------------------ timeline
def timeline():
    voices = json.load(open(os.path.join(AUD, "voices.json")))
    scenes, t = [], 0.0
    for sc in SCENES:
        v = voices.get(sc["id"], {})
        ev, cur = [], 0.6
        nar = v.get("nar")
        radios = v.get("radio", [])

        def add_radio(cur):
            for r in radios:
                d = dur(r["file"])
                ev.append({"type": "radio", "file": r["file"], "at": cur, "dur": d, "sub": r["sub"],
                           "speaker": CAPT.get(sc["id"], "HMS Broadsword") if r["speaker"] == "capt" else SPEAKER[r["speaker"]]})
                cur += d + 0.35
            return cur
        if sc.get("radio_first") or not nar:
            cur = add_radio(cur)
            if nar:
                cur += 0.3
        if nar:
            d = dur(nar)
            ev.append({"type": "nar", "file": nar, "at": cur, "dur": d})
            cur += d + 0.4
        if not (sc.get("radio_first") or not nar):
            cur = add_radio(cur)
        D = round(max(sc["min"], cur + 1.6), 2)
        scenes.append({"id": sc["id"], "start": round(t, 3), "dur": D, "events": ev})
        t += D - XF
    total = round(t + XF, 2)
    json.dump({"scenes": scenes, "total": total}, open(os.path.join(HERE, "timeline.json"), "w"), ensure_ascii=False, indent=1)
    print("total", total, "sec =", round(total / 60, 2), "min")


# ------------------------------------------------------------------ visuals
def cover_frame(src, dst, scale=2):
    im = Image.open(src).convert("RGB")
    tw, th = W * scale, H * scale
    r = im.width / im.height
    s = max(tw / im.width, th / im.height)
    if 1.2 <= r <= 2.2:
        im2 = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        x, y = (im2.width - tw) // 2, (im2.height - th) // 2
        out = im2.crop((x, y, x + tw, y + th))
    else:
        bg = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        x, y = (bg.width - tw) // 2, (bg.height - th) // 2
        bg = bg.crop((x, y, x + tw, y + th)).filter(ImageFilter.GaussianBlur(40))
        bg = Image.eval(bg, lambda v: int(v * 0.45))
        s2 = min(tw / im.width, th / im.height) * 0.94
        fg = im.resize((round(im.width * s2), round(im.height * s2)), Image.LANCZOS)
        bg.paste(fg, ((tw - fg.width) // 2, (th - fg.height) // 2))
        out = bg
    out.save(dst, quality=95)


GRADE = "eq=saturation=0.72:contrast=1.08:brightness=-0.02,vignette=PI/4.5,noise=alls=7:allf=t+u"


def photo(sid, p, D, out):
    src = next(os.path.join(HERE, "photos", p["key"] + e) for e in (".jpg", ".png")
               if os.path.exists(os.path.join(HERE, "photos", p["key"] + e)))
    frame = os.path.join(TMP, sid + "_frame.jpg")
    cover_frame(src, frame)
    n = int(D * FPS)
    z0, z1 = p.get("zoom", [1.0, 1.12])
    xs = {"center": "iw/2-(iw/zoom/2)", "lr": f"(iw-iw/zoom)*on/{n}", "rl": f"(iw-iw/zoom)*(1-on/{n})"}[p.get("pan", "center")]
    vf = [f"zoompan=z='{z0}+({z1}-{z0})*on/{n}':x='{xs}':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}", GRADE]
    if p.get("dark"):
        vf.append("eq=saturation=0.25:brightness=-0.08")
    run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-t", str(D), "-i", frame,
         "-vf", ",".join(vf) + ",format=yuv420p", "-c:v", "libx264", "-crf", "18", "-r", str(FPS), out])


def card(sid, p, D, out):
    vf = []
    lines = p["lines"]
    for i, line in enumerate(lines):
        tf = os.path.join(TMP, f"{sid}_card{i}.txt"); open(tf, "w", encoding="utf-8").write(line)
        size = 78 if i == 0 else 38
        y = H // 2 - 90 if i == 0 else H // 2 + 20
        vf.append(f"drawtext=fontfile={BOLD if i == 0 else REG}:textfile={tf}:fontsize={size}:fontcolor=0xF2EDE0:"
                  f"x=(w-text_w)/2:y={y}:alpha='min(1,max(0,(t-0.5-{i * 0.5})/0.8))*min(1,max(0,({D}-t-0.3)/0.6))'")
    vf += ["noise=alls=6:allf=t+u", "format=yuv420p"]
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c=0x07090b:s={W}x{H}:r={FPS}:d={D}",
         "-vf", ",".join(vf), "-c:v", "libx264", "-crf", "18", out])


def credits(sid, p, D, out):
    cr = json.load(open(os.path.join(HERE, "photos", "credits.json")))
    used = ["ship1", "ship2", "hermes", "broadsword", "antelope", "a4faa", "action"]
    lines = ["Nguồn tư liệu"] + [f"{cr[k]['title'][5:][:60]} — {cr[k]['artist'][:34]} ({cr[k]['license']})"
                                 for k in used if k in cr] + [
        "Ảnh: Wikimedia Commons · Bản đồ: Natural Earth · Giọng đọc, âm thanh, nhạc: ElevenLabs",
        "Cảnh chiến đấu, phòng tác chiến và tàu chìm: mô phỏng đồ họa, không phải cảnh quay thật",
        "Lời thoại bộ đàm được tái hiện để minh họa, không phải ghi âm gốc"]
    vf, y = [], (H - (48 + 40 + (len(lines) - 1) * 40)) // 2
    for i, line in enumerate(lines):
        tf = os.path.join(TMP, f"cred_{i}.txt"); open(tf, "w", encoding="utf-8").write(line)
        size = 48 if i == 0 else 24
        vf.append(f"drawtext=fontfile={BOLD if i == 0 else REG}:textfile={tf}:fontsize={size}:fontcolor=0xD8D2C2:"
                  f"x=(w-text_w)/2:y={y}:alpha='min(1,t/0.6)'")
        y += size + (40 if i == 0 else 16)
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c=0x07090b:s={W}x{H}:r={FPS}:d={D}",
         "-vf", ",".join(vf) + ",format=yuv420p", "-c:v", "libx264", "-crf", "18", out])


def render_raw(sc, D):
    out = os.path.join(CLIPS, sc["id"] + ".mp4")
    if os.path.exists(out) and abs(dur(out) - D) < 0.1:
        return out
    kind, p = sc["vis"]
    if kind == "photo":
        photo(sc["id"], p, D, out)
    elif kind == "card":
        card(sc["id"], p, D, out)
    elif kind == "credits":
        credits(sc["id"], p, D, out)
    elif kind == "map":
        run([sys.executable, os.path.join(HERE, "maps2.py"), p["kind"], str(D), out])
    elif kind == "vfx":
        params = {k: v for k, v in p.items() if k != "kind"}
        run([sys.executable, os.path.join(HERE, "vfx2.py"), p["kind"], str(D), out, json.dumps(params)])
    return out


def text_filters(lines, D, start=0.5, top=False):
    fs = []
    y = 70 if top else H - 90 - (len(lines) - 1) * 52 - 46
    end = D - 0.6
    alpha = f"if(lt(t,{start}),0,if(lt(t,{start + 0.5}),(t-{start})/0.5,if(gt(t,{end}),max(0,({end + 0.4}-t)/0.4),1)))"
    for i, line in enumerate(lines):
        tf = os.path.join(TMP, f"cap_{abs(hash((line, i)))}.txt"); open(tf, "w", encoding="utf-8").write(line)
        size = 46 if i == 0 else 32
        fs.append(f"drawtext=fontfile={BOLD if i == 0 else REG}:textfile={tf}:fontsize={size}:fontcolor=0xF2EDE0:"
                  f"x=90:y={y}:alpha='{alpha}':shadowcolor=black@0.8:shadowx=3:shadowy=3")
        y += size + 22
    return fs


def sub_filters(events):
    fs = []
    for k, e in enumerate(e for e in events if e["type"] == "radio"):
        a, b = e["at"], e["at"] + e["dur"] + 0.3
        t1 = os.path.join(TMP, f"sub_{abs(hash((e['sub'], a)))}.txt"); open(t1, "w", encoding="utf-8").write(e["sub"])
        t2 = os.path.join(TMP, f"spk_{abs(hash((e['speaker'], a)))}.txt"); open(t2, "w", encoding="utf-8").write("📻 " + e["speaker"] if False else "[ " + e["speaker"] + " ]")
        en = f"between(t,{a:.2f},{b:.2f})"
        fs.append(f"drawtext=fontfile={BOLD}:textfile={t2}:fontsize=28:fontcolor=0xF0B54A:x=(w-text_w)/2:y=h-200:"
                  f"enable='{en}':shadowcolor=black@0.9:shadowx=2:shadowy=2")
        fs.append(f"drawtext=fontfile={REG}:textfile={t1}:fontsize=40:fontcolor=white:x=(w-text_w)/2:y=h-150:"
                  f"enable='{en}':box=1:boxcolor=black@0.55:boxborderw=14")
    return fs


def normalize(sc, tl, raw):
    out = os.path.join(NORM, sc["id"] + ".mp4")
    D = tl["dur"]
    vf = [f"scale={W}:{H}", f"tpad=stop_mode=clone:stop_duration={D}", f"trim=0:{D}", "setpts=PTS-STARTPTS"]
    if sc.get("cap"):
        vf += text_filters(sc["cap"], D, top=any(e["type"] == "radio" for e in tl["events"]))
    vf += sub_filters(tl["events"])
    vf.append("format=yuv420p")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-vf", ",".join(vf), "-an", "-c:v", "libx264",
         "-crf", "18", "-r", str(FPS), out])
    return out


def render(ids=None):
    tl = {s["id"]: s for s in json.load(open(os.path.join(HERE, "timeline.json")))["scenes"]}
    todo = [sc for sc in SCENES if not ids or sc["id"] in ids]
    # heavy procedural shots first so the pool stays busy
    todo.sort(key=lambda sc: (sc["vis"][0] != "vfx", -tl[sc["id"]]["dur"]))

    def job(sc):
        raw = render_raw(sc, tl[sc["id"]]["dur"])
        normalize(sc, tl[sc["id"]], raw)
        print("done", sc["id"], flush=True)
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(job, todo))


# ------------------------------------------------------------------ audio
def load(path, gain=1.0):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2) * gain


def rms_norm(x, target_db):
    r = np.sqrt(np.mean(x ** 2) + 1e-12)
    return x * (10 ** (target_db / 20) / r)


def place(buf, x, t):
    i = int(t * SR)
    if i >= len(buf):
        return
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n]


def mix(total, out_wav):
    tl = json.load(open(os.path.join(HERE, "timeline.json")))
    N = int((total + 1) * SR)
    voice = np.zeros((N, 2), np.float32); fx = np.zeros((N, 2), np.float32); mus = np.zeros((N, 2), np.float32)
    starts = {s["id"]: s["start"] for s in tl["scenes"]}
    sfx_dir = [AUD, os.path.join(HERE, "..", "audio")]
    find = lambda n: next(os.path.join(d, n + ".mp3") for d in sfx_dir if os.path.exists(os.path.join(d, n + ".mp3")))
    cache = {}
    for s, sc in zip(tl["scenes"], SCENES):
        for e in s["events"]:
            x = load(e["file"])
            x = rms_norm(x, -19 if e["type"] == "nar" else -21)
            place(voice, x, s["start"] + e["at"])
        for name, off, vol in sc.get("sfx", []):
            if name not in cache:
                cache[name] = rms_norm(load(find(name)), -20)
            x = cache[name].copy()
            maxlen = int((s["dur"] - off + 0.6) * SR)
            x = x[:maxlen]
            fade = min(len(x), int(0.5 * SR))
            if fade > 0:
                x[-fade:] *= np.linspace(1, 0, fade)[:, None]
            place(fx, x * vol, s["start"] + off)
    # wind bed through the whole film
    wind = rms_norm(load(find("wind")), -20) * 0.22
    for t0 in np.arange(0, total, len(wind) / SR - 1):
        place(fx, wind, t0)
    # music cues with crossfades
    cues = sorted(MUSIC, key=lambda m: starts[m[1]])
    for i, (name, sid, vol) in enumerate(cues):
        p = os.path.join(AUD, name + ".mp3")
        if not os.path.exists(p):
            p = os.path.join(HERE, "..", "audio", "music.mp3")
        x = rms_norm(load(p), -20) * vol
        st = starts[sid]
        end = starts[cues[i + 1][1]] + 2.5 if i + 1 < len(cues) else total
        x = x[:int((end - st) * SR)]
        fi, fo = int(2.0 * SR), int(3.0 * SR)
        x[:fi] *= np.linspace(0, 1, fi)[:, None]
        x[-fo:] *= np.linspace(1, 0, fo)[:, None]
        place(mus, x, st)
    # duck music + effects under speech
    env = np.abs(voice).max(axis=1)
    k = int(0.3 * SR)
    cs = np.concatenate([[0.0], np.cumsum(env, dtype=np.float64)])
    idx = np.arange(len(env))
    lo = np.clip(idx - k // 2, 0, len(env)); hi = np.clip(idx + k // 2, 0, len(env))
    env = ((cs[hi] - cs[lo]) / np.maximum(hi - lo, 1)).astype(np.float32)
    duck = 1 - 0.55 * np.clip(env / (env.max() * 0.05 + 1e-9), 0, 1)
    mixd = voice * 1.0 + fx * (0.75 + 0.25 * duck[:, None]) + mus * duck[:, None]
    mixd = np.tanh(mixd * 1.2) / 1.2
    mixd = mixd[:int(total * SR)]
    fo = int(4 * SR); mixd[-fo:] *= np.linspace(1, 0, fo)[:, None]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-",
                          "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), out_wav], stdin=subprocess.PIPE)
    p.stdin.write(mixd.astype(np.float32).tobytes()); p.stdin.close(); p.wait()


def assemble(out):
    tl = json.load(open(os.path.join(HERE, "timeline.json")))
    inputs, chain, prev, t = [], [], "0:v", 0.0
    for i, s in enumerate(tl["scenes"]):
        inputs += ["-i", os.path.join(NORM, s["id"] + ".mp4")]
        if i == 0:
            t = s["dur"]; continue
        off = t - XF
        trans = "fadeblack" if s["id"] in ("title", "map_atlantic", "map_sancarlos", "map_picket", "takeoff_pov",
                                             "radar_dark", "conveyor", "memorial", "credits") else "fade"
        chain.append(f"[{prev}][{i}:v]xfade=transition={trans}:duration={XF}:offset={off:.3f}[v{i}]")
        prev, t = f"v{i}", off + s["dur"]
    video = os.path.join(TMP, "video_only.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(chain), "-map", f"[{prev}]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", video])
    wav = os.path.join(TMP, "mix.wav")
    mix(tl["total"], wav)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", "-movflags", "+faststart", out])
    print("done", out, dur(out))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "timeline":
        timeline()
    elif cmd == "render":
        render(sys.argv[2:] or None)
    elif cmd == "assemble":
        assemble(sys.argv[2])
    elif cmd == "mix":
        mix(json.load(open(os.path.join(HERE, "timeline.json")))["total"], sys.argv[2])
