"""Narration + radio for the Midway film (ElevenLabs). python audio_m.py voices|sfx"""
import hashlib, json, os, subprocess, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/home/user/phuong/video/midway")
from script_midway import SCENES
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "doc10"))
from audio import radio_fx, dur  # reuse walkie-talkie chain

KEY = os.environ["ELEVENLABS_API_KEY"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aud")
os.makedirs(OUT, exist_ok=True)
NARRATOR = "47rM9DW5VmjOw23BVHWi"
VOICES = {"pby": ("onwK4e9ZLuTAKqWW03F9", None), "scout_us": ("pNInz6obpgDQGcFmaJgB", None),
          "tomonaga": ("BSPow8LcoXJ0UVg1ws3x", "第二次攻撃の要あり。"),
          "scout": ("jyogAI7BN5DyoykAgSk6", "敵らしきもの、十隻見ゆ。")}


def post(url, payload, path):
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return True
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            open(path, "wb").write(r.read())
        print("ok", os.path.basename(path), flush=True); return True
    except urllib.error.HTTPError as e:
        print("FAIL", os.path.basename(path), e.code, e.read()[:300], flush=True); return False


h = lambda *p: hashlib.md5("|".join(p).encode()).hexdigest()[:10]
NAR_SET = {"stability": 0.5, "similarity_boost": 0.8, "style": 0.25, "use_speaker_boost": True}
RAD_SET = {"stability": 0.45, "similarity_boost": 0.75, "style": 0.4, "use_speaker_boost": True}


def tts(voice, text, model, path, st):
    return post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
                {"text": text, "model_id": model, "voice_settings": st}, path)


def one(sc):
    entry = {}
    if sc.get("nar"):
        p = os.path.join(OUT, f"nar_{sc['id']}_{h(sc['nar'])}.mp3")
        if tts(NARRATOR, sc["nar"], "eleven_v3", p, NAR_SET):
            entry["nar"] = p
    rl = []
    for j, (v, text, sub) in enumerate(sc.get("radio", [])):
        vid, alt = VOICES[v]
        say = alt or text
        raw = os.path.join(OUT, f"rawradio_{sc['id']}_{j}_{h(v, say)}.mp3")
        if tts(vid, say, "eleven_multilingual_v2", raw, RAD_SET):
            wav = raw.replace("rawradio_", "radio_").replace(".mp3", ".wav")
            radio_fx(raw, wav)
            rl.append({"file": wav, "sub": sub, "speaker": v})
    entry["radio"] = rl
    return sc["id"], entry


def voices():
    with ThreadPoolExecutor(4) as ex:
        man = dict(ex.map(one, SCENES))
    json.dump(man, open(os.path.join(OUT, "voices.json"), "w"), ensure_ascii=False, indent=1)
    print("voices done", sum(1 for v in man.values() if v.get("nar")))


SFX = {
    "prop_flyby": ("1940s propeller warplane flying fast and low overhead, radial engine roar passing by", 5),
    "dive_scream": ("WWII dive bomber diving steeply, rising engine scream and wind howl, then pull-out roar", 6),
    "flak": ("WWII anti-aircraft guns firing from a warship, rapid pom-pom cannons and heavy flak bursts", 8),
    "carrier_deck": ("WWII aircraft carrier flight deck ambience: several radial engines idling, wind, shouted orders", 10),
    "morse": ("Old 1940s telegraph morse code beeping, radio static, receiving a message", 6),
    "typewriter": ("1940s office typewriter typing fast, carriage return bell", 6),
    "stamp": ("Heavy rubber stamp slammed down on paper on a wooden desk, single loud thud", 2),
    "click_bell": ("Soft mouse click followed by a bright small notification bell ding", 2),
    "ocean_calm": ("Calm open ocean waves, gentle wind, seagulls far away", 12),
    "big_explosion": ("Massive explosion on a ship, deep boom with burning debris and secondary blasts", 6),
}


def sfx():
    for name, (text, d) in SFX.items():
        post("https://api.elevenlabs.io/v1/sound-generation",
             {"text": text, "duration_seconds": d, "prompt_influence": 0.5}, os.path.join(OUT, name + ".mp3"))


if __name__ == "__main__":
    {"voices": voices, "sfx": sfx}[sys.argv[1]]()
