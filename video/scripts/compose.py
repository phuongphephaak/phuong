"""Assemble the HMS Coventry draft video (no narration).
Usage: python compose.py <work_dir> <output.mp4>
work_dir holds photos/, clips/map_*.mp4, audio/*.mp3
"""
import json, os, subprocess, sys
from PIL import Image, ImageFilter

WORK, OUTPUT = sys.argv[1], sys.argv[2]
W, H, FPS, XF = 1920, 1080, 30, 0.6
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
TMP = os.path.join(WORK, "build")
os.makedirs(TMP, exist_ok=True)
P = lambda *a: os.path.join(WORK, *a)


def run(cmd):
    subprocess.run(cmd, check=True)


def find_photo(key):
    for ext in (".jpg", ".png", ".jpeg"):
        if os.path.exists(P("photos", key + ext)) and os.path.getsize(P("photos", key + ext)) > 0:
            return P("photos", key + ext)
    return None


def cover_frame(src, dst, scale=2):
    """Fit image into a 16:9 frame (2x res). Portrait/odd images get a blurred fill background."""
    im = Image.open(src).convert("RGB")
    tw, th = W * scale, H * scale
    r = im.width / im.height
    if 1.2 <= r <= 2.2:
        s = max(tw / im.width, th / im.height)
        im2 = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        x, y = (im2.width - tw) // 2, (im2.height - th) // 2
        out = im2.crop((x, y, x + tw, y + th))
    else:
        s = max(tw / im.width, th / im.height)
        bg = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        x, y = (bg.width - tw) // 2, (bg.height - th) // 2
        bg = bg.crop((x, y, x + tw, y + th)).filter(ImageFilter.GaussianBlur(40))
        bg = Image.eval(bg, lambda v: int(v * 0.45))
        s2 = min(tw / im.width, th / im.height) * 0.94
        fg = im.resize((round(im.width * s2), round(im.height * s2)), Image.LANCZOS)
        bg.paste(fg, ((tw - fg.width) // 2, (th - fg.height) // 2))
        out = bg
    out.save(dst, quality=95)


def text_filters(lines, start=0.4, dur=None, y0=None, big=False):
    """drawtext filters for a caption block bottom-left, with fade in/out."""
    fs = [];
    size_main, size_sub = (64, 36) if big else (46, 32)
    y = y0 if y0 is not None else H - 90 - (len(lines) - 1) * 52 - size_main
    end = (dur - 0.5) if dur else 999
    alpha = f"if(lt(t,{start}),0,if(lt(t,{start + 0.5}),(t-{start})/0.5,if(gt(t,{end}),max(0,({end + 0.4}-t)/0.4),1)))"
    for i, line in enumerate(lines):
        tf = os.path.join(TMP, f"txt_{abs(hash((line, i, start)))}.txt")
        open(tf, "w", encoding="utf-8").write(line)
        main = i == 0
        fs.append(f"drawtext=fontfile={BOLD if main else REG}:textfile={tf}:fontsize={size_main if main else size_sub}:"
                  f"fontcolor=0xF2EDE0:x=90:y={y}:alpha='{alpha}':shadowcolor=black@0.8:shadowx=3:shadowy=3")
        y += (size_main if main else size_sub) + 22
    return fs


GRADE = "eq=saturation=0.72:contrast=1.08:brightness=-0.02,vignette=PI/4.5,noise=alls=7:allf=t+u"


def photo_clip(name, key, dur, lines, zoom=(1.0, 1.12), pan="center", extra=None, dark=False):
    src = find_photo(key)
    if not src:
        print("missing photo", key); return None
    frame = os.path.join(TMP, key + "_frame.jpg")
    cover_frame(src, frame)
    n = int(dur * FPS)
    z0, z1 = zoom
    z = f"{z0}+({z1}-{z0})*on/{n}"
    xs = {"center": "iw/2-(iw/zoom/2)", "lr": "(iw-iw/zoom)*on/%d" % n, "rl": "(iw-iw/zoom)*(1-on/%d)" % n}[pan]
    vf = [f"zoompan=z='{z}':x='{xs}':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}", GRADE]
    if dark:
        vf.append("eq=saturation=0.25:brightness=-0.08")
    if extra:
        vf += extra
    vf += text_filters(lines, dur=dur)
    vf.append("format=yuv420p")
    out = os.path.join(TMP, name + ".mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-t", str(dur), "-i", frame,
         "-vf", ",".join(vf), "-c:v", "libx264", "-crf", "18", "-r", str(FPS), out])
    return out, dur


def video_clip(name, src, dur, lines=None):
    vf = ["scale=1920:1080", "noise=alls=5:allf=t+u"] + (text_filters(lines, dur=dur) if lines else []) + ["format=yuv420p"]
    out = os.path.join(TMP, name + ".mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-t", str(dur), "-vf", ",".join(vf),
         "-c:v", "libx264", "-crf", "18", "-r", str(FPS), out])
    return out, dur


def card_clip(name, dur, lines, big=True, sub_lines=None):
    vf = text_filters(lines, start=0.5, dur=dur, y0=H // 2 - 70, big=big)
    vf = [f.replace("x=90", "x=(w-text_w)/2") for f in vf] + ["noise=alls=6:allf=t+u", "format=yuv420p"]
    out = os.path.join(TMP, name + ".mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c=0x07090b:s={W}x{H}:r={FPS}:d={dur}",
         "-vf", ",".join(vf), "-c:v", "libx264", "-crf", "18", out])
    return out, dur


def credits_clip(name, dur):
    credits = json.load(open(P("photos", "credits.json")))
    used = [k for k in USED_PHOTOS if k in credits]
    lines = ["Nguồn tư liệu"] + [
        f"{credits[k]['title'][5:][:62]} — {credits[k]['artist'][:34]} ({credits[k]['license']})" for k in used] + [
        "Ảnh: Wikimedia Commons · Bản đồ: Natural Earth · Âm thanh & nhạc: ElevenLabs"]
    vf = []
    y = (H - (48 + 40 + (len(lines) - 1) * 40)) // 2
    for i, line in enumerate(lines):
        tf = os.path.join(TMP, f"cred_{i}.txt")
        open(tf, "w", encoding="utf-8").write(line)
        size = 48 if i == 0 else 24
        vf.append(f"drawtext=fontfile={BOLD if i == 0 else REG}:textfile={tf}:fontsize={size}:fontcolor=0xD8D2C2:"
                  f"x=(w-text_w)/2:y={y}:alpha='min(1,t/0.6)'")
        y += size + (40 if i == 0 else 16)
    vf.append("format=yuv420p")
    out = os.path.join(TMP, name + ".mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c=0x07090b:s={W}x{H}:r={FPS}:d={dur}",
         "-vf", ",".join(vf), "-c:v", "libx264", "-crf", "18", out])
    return out, dur


# --- explosion effect: white flash, orange tint, camera shake ---------------------------------
BOOM_T = 1.2
SHAKE = [f"crop=w=1840:h=1034:x='40+if(between(t,{BOOM_T},{BOOM_T + 1.4}),28*sin(t*95)*({BOOM_T + 1.4}-t),0)':"
         f"y='23+if(between(t,{BOOM_T},{BOOM_T + 1.4}),18*cos(t*80)*({BOOM_T + 1.4}-t),0)'",
         "scale=1920:1080",
         f"drawbox=x=0:y=0:w=iw:h=ih:color=white@0.85:t=fill:enable='between(t,{BOOM_T},{BOOM_T + 0.12})'",
         f"drawbox=x=0:y=0:w=iw:h=ih:color=0xff5a1e@0.22:t=fill:enable='between(t,{BOOM_T + 0.12},{BOOM_T + 1.8})'"]

USED_PHOTOS = ["ship1", "broadsword", "kh9", "antelope", "a4faa", "action", "ship2"]
SEQ = [
    ("title", lambda: card_clip("title", 4.5, ["25 THÁNG 5, 1982", "Chiến tranh Falklands · Nam Đại Tây Dương"])),
    ("map_a", lambda: video_clip("map_a", P("clips", "map_a.mp4"), 8.0)),
    ("ship1", lambda: photo_clip("ship1", "ship1", 6.0, ["HMS Coventry (D118)",
                                                          "Tàu khu trục Type 42 · Hải quân Hoàng gia Anh"], pan="lr")),
    ("broadsword", lambda: photo_clip("broadsword", "broadsword", 5.0, ["HMS Broadsword",
                                                                        "Khinh hạm hộ tống, đi cùng Coventry"])),
    ("kh9", lambda: photo_clip("kh9", "kh9", 5.0, ["Eo San Carlos, tháng 5/1982",
                                                    "Ảnh vệ tinh: tàu Anh liên tục bị không kích"], zoom=(1.0, 1.18))),
    ("antelope", lambda: photo_clip("antelope", "antelope", 5.0, ["23/5 · HMS Antelope",
                                                                   "Bốc khói sau khi trúng bom của A-4 ở eo San Carlos"],
                                    zoom=(1.05, 1.2))),
    ("a4faa", lambda: photo_clip("a4faa", "a4faa", 5.0, ["Đối thủ: A-4 Skyhawk",
                                                                   "Cường kích của Không quân Argentina (ảnh trưng bày)"],
                                    pan="rl")),
    ("map_b", lambda: video_clip("map_b", P("clips", "map_b.mp4"), 8.5)),
    ("action", lambda: photo_clip("action", "action", 5.0, ["BÁO ĐỘNG CHIẾN ĐẤU",
                                                             "Thủy thủ Anh vào vị trí chiến đấu, Falklands 1982"])),
    ("ship2", lambda: photo_clip("ship2", "ship2", 5.5, ["Ba quả bom xuyên vào thân tàu"], zoom=(1.08, 1.2),
                                 extra=SHAKE)),
    ("end", lambda: photo_clip("end", "ship1", 7.5, ["Chưa đầy 20 phút sau, Coventry lật nghiêng và chìm.",
                                                      "19 thủy thủ thiệt mạng."], zoom=(1.15, 1.0), dark=True)),
    ("credits", lambda: credits_clip("credits", 6.0)),
]

clips = []
for name, fn in SEQ:
    r = fn()
    if r:
        clips.append((name, *r))
        print("clip", name, r[1], flush=True)

# --- concat with crossfades --------------------------------------------------------------------
starts, t = {}, 0.0
inputs, chain, prev = [], [], "0:v"
for i, (name, path, dur) in enumerate(clips):
    inputs += ["-i", path]
    starts[name] = t if i == 0 else t
    if i == 0:
        t = dur
        continue
    off = t - XF
    starts[name] = off
    label = f"v{i}"
    trans = "fadeblack" if name in ("end", "credits", "map_b") else "fade"
    chain.append(f"[{prev}][{i}:v]xfade=transition={trans}:duration={XF}:offset={off:.3f}[{label}]")
    prev, t = label, off + dur
total = t
video_only = os.path.join(TMP, "video_only.mp4")
run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(chain), "-map", f"[{prev}]",
     "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", video_only])
print("timeline", json.dumps({k: round(v, 2) for k, v in starts.items()}), "total", round(total, 2))

# --- audio mix ----------------------------------------------------------------------------------
A = lambda n: P("audio", n + ".mp3")
events = [  # (file, start_sec, volume)
    ("jet_approach", starts.get("map_b", 0) + 2.0, 0.9),
    ("jet_flyby", starts.get("map_b", 0) + 6.3, 1.0),
    ("alarm", starts.get("action", 0) + 0.2, 0.55),
    ("explosion", starts.get("ship2", 0) + BOOM_T - 0.05, 1.0),
    ("creak", starts.get("end", 0) + 0.3, 0.7),
]
ain = ["-stream_loop", "-1", "-i", A("wind"), "-i", A("music")]
fc = [f"[0:a]atrim=0:{total:.2f},volume=0.30,afade=t=in:d=2,afade=t=out:st={total - 4:.2f}:d=4[wind]",
      f"[1:a]atrim=0:{total - 1.5:.2f},adelay=1500|1500,volume=0.55,afade=t=out:st={total - 5:.2f}:d=5[music]"]
mix = ["[wind]", "[music]"]
for j, (f, st, vol) in enumerate(events):
    ain += ["-i", A(f)]
    ms = int(st * 1000)
    fc.append(f"[{j + 2}:a]volume={vol},adelay={ms}|{ms}[e{j}]")
    mix.append(f"[e{j}]")
fc.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0,alimiter=limit=0.9,atrim=0:{total:.2f}[aout]")
audio = os.path.join(TMP, "mix.m4a")
run(["ffmpeg", "-y", "-loglevel", "error", *ain, "-filter_complex", ";".join(fc), "-map", "[aout]",
     "-c:a", "aac", "-b:a", "192k", "-ac", "2", audio])
run(["ffmpeg", "-y", "-loglevel", "error", "-i", video_only, "-i", audio, "-c:v", "copy", "-c:a", "copy",
     "-shortest", "-movflags", "+faststart", OUTPUT])
print("done", OUTPUT)
