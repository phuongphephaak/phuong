"""Pre-rendered labelled clips for the mig17 scene.  python make_pre.py"""
import os, subprocess, json
HERE = os.path.dirname(os.path.abspath(__file__))
INTER = subprocess.run(["fc-match", "-f", "%{file}", "Inter:extrabold"], capture_output=True, text=True).stdout
OSW = os.path.join(HERE, "..", "gfx", "oswald-700.ttf")
FPS = 30


def txt(name, s):
    p = os.path.join(HERE, "pre", name + ".txt"); open(p, "w", encoding="utf-8").write(s); return p


def labels(name, big, small, col="0xFFD75A"):
    a = "if(lt(t,0.3),0,if(lt(t,0.8),(t-0.3)/0.5,1))"
    return (f"drawtext=fontfile={OSW}:textfile={txt(name+'_b', big)}:fontsize=110:fontcolor={col}:x=90:y=h-250:alpha='{a}':"
            f"shadowcolor=black@0.85:shadowx=4:shadowy=4,"
            f"drawtext=fontfile={INTER}:textfile={txt(name+'_s', small)}:fontsize=40:fontcolor=white:x=94:y=h-120:alpha='{a}':"
            f"shadowcolor=black@0.85:shadowx=3:shadowy=3")


def photo_clip(name, photo, crop, D, big, small, col):
    out = os.path.join(HERE, "pre", name + ".mp4"); n = int(D * FPS)
    vf = (f"{crop},scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,"
          f"zoompan=z='1.0+0.08*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps={FPS},"
          "eq=contrast=1.08,vignette=PI/5,noise=alls=6:allf=t" + ("," + labels(name, big, small, col) if big else "") + ",format=yuv420p")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-t", str(D), "-i", photo,
                    "-vf", vf, "-c:v", "libx264", "-crf", "17", "-preset", "veryfast", out], check=True)


def arch_clip(name, src, st, D, big, small, col):
    out = os.path.join(HERE, "pre", name + ".mp4")
    vf = ("scale=2016:1512,setsar=1,crop=1920:1080,eq=contrast=1.08:brightness=-0.01,noise=alls=7:allf=t,fps=30,"
          + labels(name, big, small, col) + ",format=yuv420p")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(st), "-t", str(D), "-i", src, "-vf", vf, "-an",
                    "-c:v", "libx264", "-crf", "17", "-preset", "veryfast", out], check=True)


if __name__ == "__main__":
    ph = lambda k: next(os.path.join(HERE, "photos", k + e) for e in (".jpg", ".png") if os.path.exists(os.path.join(HERE, "photos", k + e)))
    photo_clip("mig_card", ph("mig_2047"), "null", 6.6, "MiG-17", "~6 TẤN · DƯỚI TỐC ĐỘ ÂM THANH · CHỈ CÓ PHÁO", "0xFFD75A")
    photo_clip("mig4_kb", ph("mig_4ship"), "null", 5.0, "", "", "")
    photo_clip("mig_fly_kb", ph("mig_gear"), "null", 5.0, "", "", "")
    arch_clip("f105_card", os.path.join(HERE, "arch", "gov.dod.dimoc.26592.mpeg"), 977, 7.0, "F-105",
              "NẶNG GẦN GẤP 4 · VƯỢT TỐC ĐỘ ÂM THANH", "0x5AC8FF")
    print("ok")
