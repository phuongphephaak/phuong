"""Cut vertical 9:16 Shorts from a 16:9 master: blurred background, title on top, burned Vietnamese captions."""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
SRC, SRT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
SHORTS = json.load(open(sys.argv[4]))
W, H = 1080, 1920
FB = "/home/user/phuong/video/brand/fonts/BarlowCondensed-ExtraBold.ttf"
FS = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
OUT = os.path.abspath(OUT); os.makedirs(OUT, exist_ok=True)

def ts(x):
    h, m, s = x.replace(",", ".").split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
subs = []
for b in open(SRT, encoding="utf-8").read().strip().split("\n\n"):
    l = b.split("\n"); a, c = l[1].split(" --> "); subs.append((ts(a), ts(c), " ".join(l[2:])))

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]

def title_png(path, parts):
    im = Image.new("RGBA", (W, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = 150
    for text, col, size in parts:
        f = ImageFont.truetype(FB, size)
        for line in wrap(d, text, f, W - 90):
            d.text((W / 2, y), line, font=f, fill=tuple(col), anchor="mt", stroke_width=7, stroke_fill=(0, 0, 0))
            y += int(size * 1.02)
    im.save(path)

def cap_png(path, text):
    im = Image.new("RGBA", (W, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im); f = ImageFont.truetype(FS, 54)
    lines = wrap(d, text, f, W - 120)[:3]; y = 10
    for line in lines:
        d.text((W / 2, y), line, font=f, fill=(255, 255, 255), anchor="mt", stroke_width=6, stroke_fill=(0, 0, 0)); y += 70
    im.save(path)

for sh in SHORTS:
    name = sh["name"]; tmp = os.path.join(OUT, name + "_tmp"); os.makedirs(tmp, exist_ok=True)
    parts, cues, off = [], [], 0.0
    for j, (a, b) in enumerate(sh["segs"]):
        p = os.path.join(tmp, f"seg{j}.mp4"); d = b - a
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", str(a), "-t", str(d), "-i", SRC,
                        "-af", f"afade=t=in:d=0.25,afade=t=out:st={d - 0.35}:d=0.35", "-vf", f"fade=t=in:d=0.2,fade=t=out:st={d - 0.25}:d=0.25",
                        "-c:v", "libx264", "-crf", "17", "-preset", "veryfast", "-c:a", "aac", "-b:a", "192k", p], check=True)
        parts.append(p)
        for s0, s1, t in subs:
            if s1 > a and s0 < b:
                cues.append((max(s0, a) - a + off, min(s1, b) - a + off, t))
        off += d
    lst = os.path.join(tmp, "list.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    joined = os.path.join(tmp, "joined.mp4")
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined], check=True)
    title_png(os.path.join(tmp, "title.png"), sh["title"])
    inputs = ["-i", joined, "-loop", "1", "-i", os.path.join(tmp, "title.png")]
    fc = ["[0:v]split[a][b]",
          f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:3,eq=brightness=-0.18[bg]",
          f"[b]scale={W}:-2[fg]", "[bg][fg]overlay=0:(H-h)/2-60[v0]", "[v0][1:v]overlay=0:120:shortest=1[v1]"]
    prev = "v1"
    for k, (c0, c1, t) in enumerate(cues):
        cp = os.path.join(tmp, f"c{k}.png"); cap_png(cp, t); inputs += ["-i", cp]
        fc.append(f"[{prev}][{k + 2}:v]overlay=0:1300:enable='between(t,{c0:.2f},{c1:.2f})'[v{k + 2}]"); prev = f"v{k + 2}"
    out = os.path.join(OUT, name + ".mp4")
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", f"[{prev}]",
                    "-map", "0:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-t", f"{off:.2f}", out], check=True)
    subprocess.run(["rm", "-rf", tmp])
    print(name, round(off, 1), "s", os.path.getsize(out) // 1048576, "MB", flush=True)
