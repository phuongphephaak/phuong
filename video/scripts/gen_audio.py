"""Generate sound effects + music with ElevenLabs. Usage: python gen_audio.py <out_dir>"""
import json, os, sys, urllib.request

KEY = os.environ["ELEVENLABS_API_KEY"]
SFX = {
    "wind": ("Cold strong wind over a rough grey ocean, waves crashing, lonely ambience, no music", 22),
    "jet_approach": ("Distant military jet engines approaching fast at very low altitude, rumble growing louder", 6),
    "jet_flyby": ("Low-altitude military attack jet screaming past overhead from left to right, loud roar", 5),
    "alarm": ("1980s Royal Navy warship action stations alarm klaxon repeating, metallic, echo in steel corridor", 6),
    "explosion": ("Massive bomb explosion inside a steel warship hull, deep boom, metal tearing, debris falling into water", 6),
    "creak": ("Large steel ship hull groaning and creaking as it capsizes, water rushing in, low rumble", 8),
}
MUSIC = ("Somber cinematic orchestral underscore for a war documentary: low sustained strings, slow distant "
         "timpani pulse, building tension in the middle, ending in a quiet mournful solo cello. No vocals.")


def post(url, payload, path):
    if os.path.exists(path):
        print("exists", path); return
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            open(path, "wb").write(r.read())
        print("ok", path, flush=True)
    except urllib.error.HTTPError as e:
        print("FAIL", path, e.code, e.read()[:300], flush=True)


out = sys.argv[1]
os.makedirs(out, exist_ok=True)
for name, (text, dur) in SFX.items():
    post("https://api.elevenlabs.io/v1/sound-generation",
         {"text": text, "duration_seconds": dur, "prompt_influence": 0.5}, os.path.join(out, name + ".mp3"))
post("https://api.elevenlabs.io/v1/music",
     {"prompt": MUSIC, "music_length_ms": 75000, "force_instrumental": True}, os.path.join(out, "music.mp3"))
