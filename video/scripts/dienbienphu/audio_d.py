"""Narration + radio for the Dien Bien Phu film (ElevenLabs). python audio_m.py voices|sfx"""
import hashlib, json, os, subprocess, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/home/user/phuong/video/dienbienphu")
from script_dbp import SCENES
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
    "artillery_barrage": ("1950s field artillery barrage: many 105mm howitzers firing in sequence from mountains, deep booms echoing across a valley, distant shell impacts", 8),
    "howitzer_shot": ("Single heavy howitzer cannon shot, loud close boom with echo in mountains", 3),
    "jungle_night": ("Tropical mountain jungle at night, insects, cicadas, distant gibbon calls, light wind in leaves", 15),
    "rain_heavy": ("Heavy monsoon rain pouring on mud and trenches, water dripping, distant thunder", 12),
    "men_heave": ("Group of men pulling a heavy load with ropes up a muddy slope at night, rhythmic grunting, rope creaking, wooden wheel creak, mud", 8),
    "dakota_drone": ("1950s twin-engine propeller transport plane flying overhead, droning radial engines passing slowly", 7),
    "digging": ("Shovels digging into wet earth, soil thrown aside, several men working quietly", 6),
    "mg_fire": ("Distant machine gun bursts and rifle fire in a battle, echoes in hills", 6),
}


def sfx():
    for name, (text, d) in SFX.items():
        post("https://api.elevenlabs.io/v1/sound-generation",
             {"text": text, "duration_seconds": d, "prompt_influence": 0.5}, os.path.join(OUT, name + ".mp3"))


if __name__ == "__main__":
    {"voices": voices, "sfx": sfx}[sys.argv[1]]()
