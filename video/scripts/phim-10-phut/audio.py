"""Generate narration, radio dialogue (with walkie-talkie FX), extra SFX and music via ElevenLabs.
Usage:
  python audio.py voices      # narration + radio lines
  python audio.py sfx         # extra sound effects
  python audio.py music <timeline.json>
Outputs into ./aud/
"""
import hashlib, json, os, subprocess, sys, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from script_data import SCENES, NARRATOR, VOICES, MUSIC

KEY = os.environ["ELEVENLABS_API_KEY"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aud")
os.makedirs(OUT, exist_ok=True)


def post(url, payload, path):
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return True
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            open(path, "wb").write(r.read())
        print("ok", os.path.basename(path), flush=True)
        return True
    except urllib.error.HTTPError as e:
        print("FAIL", os.path.basename(path), e.code, e.read()[:300], flush=True)
        return False


def h(*parts):
    return hashlib.md5("|".join(parts).encode()).hexdigest()[:10]


def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", path]).decode().strip())


def tts(voice, text, model, path, settings):
    return post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
                {"text": text, "model_id": model, "voice_settings": settings}, path)


def radio_fx(src, dst):
    """Band-limit, compress, crunch, add static and push-to-talk beeps."""
    if os.path.exists(dst):
        return
    d = dur(src)
    fc = ("[0:a]aresample=44100,pan=mono|c0=c0,highpass=f=380,lowpass=f=3000,"
          "acompressor=threshold=-24dB:ratio=8:attack=5:release=60:makeup=6,"
          "acrusher=bits=10:mode=log:aa=1:mix=0.35,volume=1.6,adelay=180[v];"
          f"anoisesrc=d={d + 0.6:.2f}:c=white:a=0.05,highpass=f=900,lowpass=f=4500,volume=0.55[n];"
          "sine=f=1250:d=0.07,volume=0.25[b1];"
          "sine=f=900:d=0.06,volume=0.2,adelay=" + str(int((d + 0.35) * 1000)) + "[b2];"
          "[v][n][b1][b2]amix=inputs=4:normalize=0:duration=longest,"
          f"atrim=0:{d + 0.6:.2f},afade=t=out:st={d + 0.45:.2f}:d=0.15")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", fc, "-ac", "1", dst],
                   check=True)


def voices():
    nar_settings = {"stability": 0.5, "similarity_boost": 0.8, "style": 0.25, "use_speaker_boost": True}
    rad_settings = {"stability": 0.4, "similarity_boost": 0.75, "style": 0.45, "use_speaker_boost": True}
    manifest = {}
    for sc in SCENES:
        entry = {}
        if sc.get("nar"):
            p = os.path.join(OUT, f"nar_{sc['id']}_{h(sc['nar'])}.mp3")
            ok = tts(NARRATOR, sc["nar"], "eleven_v3", p, nar_settings) or \
                tts(NARRATOR, sc["nar"], "eleven_turbo_v2_5", p, nar_settings)
            if ok:
                entry["nar"] = p
        rl = []
        for j, (v, text, sub) in enumerate(sc.get("radio", [])):
            raw = os.path.join(OUT, f"rawradio_{sc['id']}_{j}_{h(v, text)}.mp3")
            if tts(VOICES[v], text, "eleven_multilingual_v2", raw, rad_settings):
                wav = raw.replace("rawradio_", "radio_").replace(".mp3", ".wav")
                radio_fx(raw, wav)
                rl.append({"file": wav, "sub": sub, "speaker": v})
        entry["radio"] = rl
        manifest[sc["id"]] = entry
    json.dump(manifest, open(os.path.join(OUT, "voices.json"), "w"), ensure_ascii=False, indent=1)


SFX = {
    "jet_cockpit": ("Inside the cockpit of a 1970s attack jet flying very low over the sea, loud engine drone and wind roar", 10),
    "ops_room": ("1980s warship operations room ambience: electronic hum, radar beeps, ventilation, muffled voices", 15),
    "boom_far": ("Single distant heavy explosion rumbling across the sea", 5),
    "ship_sea": ("Warship bow cutting through heavy ocean swell, wind and spray, engine hum", 15),
    "missile": ("Surface-to-air missile launching from a warship: loud ignition blast then whooshing roar into the distance", 6),
    "fire_crackle": ("Large fire burning on a steel ship, crackling flames and secondary small explosions, wind", 15),
    "splash": ("Bomb exploding in the sea near a ship, huge water splash and spray falling back down", 4),
    "metal_hit": ("Heavy metal object smashing through a steel ship deck, loud clang and tearing metal", 3),
    "water_rush": ("Sea water rushing and pouring into a sinking ship, deep gurgling and turbulent flow", 10),
    "bubbles": ("Large air bubbles bursting on the sea surface as a ship disappears, quiet waves", 8),
    "helicopter": ("Military Sea King helicopter hovering low over the sea, rotor thumping and wind", 15),
}

MUSIC_PROMPTS = {
    "music_tension": "Dark cinematic orchestral underscore for a naval war documentary: low strings, distant brass, "
                     "slow pulsing percussion, growing tension. No vocals.",
    "music_battle": "Intense cinematic battle score for a 1982 naval air attack: driving low strings ostinato, "
                    "taiko and timpani hits, urgent brass, building to a climax. No vocals.",
    "music_mourn": "Mournful cinematic elegy for a sunken warship: solo cello, soft strings, sparse piano, "
                   "quiet and respectful, slowly fading. No vocals.",
}


def sfx():
    for name, (text, d) in SFX.items():
        post("https://api.elevenlabs.io/v1/sound-generation",
             {"text": text, "duration_seconds": d, "prompt_influence": 0.5}, os.path.join(OUT, name + ".mp3"))


def music(timeline_path):
    tl = json.load(open(timeline_path))
    starts = {s["id"]: s["start"] for s in tl["scenes"]}
    cues = sorted(MUSIC, key=lambda m: starts[m[1]])
    for i, (name, sid, vol) in enumerate(cues):
        end = starts[cues[i + 1][1]] + 3 if i + 1 < len(cues) else tl["total"]
        length = min(300, max(30, end - starts[sid] + 4))
        path = os.path.join(OUT, name + ".mp3")
        if os.path.exists(path) and dur(path) >= length - 5:
            continue
        if os.path.exists(path):
            os.remove(path)
        post("https://api.elevenlabs.io/v1/music",
             {"prompt": MUSIC_PROMPTS[name], "music_length_ms": int(length * 1000), "force_instrumental": True}, path)


if __name__ == "__main__":
    {"voices": voices, "sfx": sfx}.get(sys.argv[1], lambda: music(sys.argv[2]))()
