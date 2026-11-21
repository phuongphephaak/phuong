"""AI illustration stills for the Ham Rong film (Gemini image). python gen_ai.py [ids]"""
import base64, json, os, sys, urllib.request, concurrent.futures as cf
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "ai")
STYLE = (" Cinematic photoreal historical war documentary still, April 1965, North Vietnam. Muted, slightly desaturated "
         "film colour grade, soft haze, fine film grain, 16:9 widescreen composition. Historically accurate aircraft. "
         "No text, no captions, no watermark, no logos.")
MIG = ("Soviet-built MiG-17F fighter of the North Vietnamese air force: small subsonic swept-wing jet, round open nose air "
       "intake, swept wings with wing fences, tall swept tail fin, bare silver natural-metal finish, small red disc with "
       "a yellow five-pointed star roundel")
F105 = ("US Air Force Republic F-105D Thunderchief: very long slender pointed fuselage, mid-mounted swept wings with "
        "forward-swept air intakes at the wing roots, bare silver natural-metal finish, bombs under the wings")
F8 = ("US Navy Vought F-8 Crusader: long slender fuselage with a wide open chin air intake under the nose, high "
      "shoulder-mounted swept wing, light gull grey over white US Navy paint")
F100 = "US Air Force North American F-100 Super Sabre: silver jet with an oval open nose intake and swept wings"
VN = "Vietnamese"
S = {
 "h_clock": f"A large formation of {F105} jets flying above a sea of white clouds in bright morning light, seen from slightly above and behind.",
 "h_dive": f"Four {MIG} jets diving steeply out of a thick cloud bank from above, seen from behind a formation of silver F-105 jets flying below them.",
 "h_impact": f"A {F105} hit by cannon fire, flames and black smoke pouring from its fuselage, falling toward the grey sea near a coast with small rocky islands.",
 "plan": "Inside a dim 1965 North Vietnamese air-defence command bunker: officers in olive-green uniforms around a large plotting table with a hand-drawn map, a round green radar scope glowing, field telephones, a kerosene lamp.",
 "lan_up": f"Four {MIG} jets flying very low in loose formation over bright green rice paddies and jagged limestone karst mountains, morning haze.",
 "lan_attack": f"View from just behind and above a {MIG} chasing a {F8} ahead of it, anti-aircraft flak bursts in the sky, a steel truss bridge over a wide river far below.",
 "lan_hit": f"A {F8} hit by cannon shells, flame and grey smoke streaming from its rear fuselage, banking away over a coastline.",
 "lan_fuel": f"A {MIG} after a belly landing on a wide sandy riverbank, dust settling, the pilot in a leather flight helmet standing on the wing, {VN} villagers in conical hats running toward the jet.",
 "hanh_up": f"Four {MIG} jets taking off one after another from a simple airfield runway in early morning mist, ground crew watching.",
 "spot": f"Point-of-view from inside the cockpit of a {MIG}: canopy frame and a round gunsight in the foreground, looking down through thin broken clouds at a formation of silver F-105 jets far below.",
 "attack": f"A {MIG} diving through wisps of white cloud, seen from the side, sunlight glinting on its silver skin, a formation of jets visible below ahead.",
 "fire": f"Close view behind a {MIG} as its nose cannons fire, bright tracer shells streaking forward into a {F105} ahead which bursts into flame.",
 "two_down": f"Two {F105} jets trailing fire and smoke falling toward the sea, a single white parachute descending, a small island on the horizon.",
 "chase": f"A {F100} chasing a {MIG} at very low altitude over forested hills, dark anti-aircraft flak bursts in the sky.",
 "hanh_back": f"A lone {MIG} flying low through a valley between limestone karst mountains, late morning haze, lonely mood.",
 "final": "Golden sunset over the Ham Rong bridge in Thanh Hoa: a steel truss railway bridge spanning the wide Ma river between two rocky hills, four faint jet contrails high in the orange sky, peaceful elegiac mood.",
 "tuyen": f"A slender 19-year-old {VN} militia girl in a simple brown blouse and a camouflaged conical hat, carrying two heavy wooden ammunition boxes on her shoulders up a hillside path, anti-aircraft guns and smoke on the hill behind her.",
 "vpaf": f"A row of {MIG} jets parked on a 1964 North Vietnamese airfield, young {VN} pilots in flight suits and leather helmets walking toward them.",
 "young": f"Three young {VN} fighter pilots in their twenties, wearing leather flight helmets and flight suits, standing beside a {MIG}, serious and determined faces.",
 "training": f"Young {VN} pilots in 1960s flight suits in a simple classroom studying a small wooden model airplane held by an instructor, chalkboard with diagrams of turns.",
 "edge": f"A {MIG} in a very tight banking turn at low altitude over green hills, white vapour trails streaming from its wingtips.",
 "sao_vang": f"Hundreds of {VN} youth volunteers with bamboo baskets and shoulder poles building a long earthen airstrip by hand in 1965, red flags, dust.",
 "lesson": f"{VN} MiG pilots in 1965 flight suits sitting around a wooden table, one holding small model airplanes on sticks to explain an attack from above and behind.",
 "price": "Three leather pilot flight helmets placed on a wooden table beside white flowers and burning incense sticks, a red flag with a yellow star in the soft background, dim respectful light.",
 "three": "White flowers and incense on the bank of the wide Ma river at dusk, the rocky Ham Rong hills and a steel truss bridge in the distance, calm water.",
 "defense": f"{VN} anti-aircraft gun crews in pith helmets manning 37mm guns on a rocky hillside above a steel truss bridge over a wide river, militia women carrying shells, smoke.",
 "claims": f"Wreckage of a crashed silver US jet in a rice paddy, {VN} militia men and women in conical hats with rifles standing beside it.",
 "bridge_ai": "A 1965 steel truss railway and road bridge spanning the wide Ma river between two steep rocky hills, Ham Rong, Thanh Hoa, North Vietnam, a steam train crossing, misty morning.",
}
def gen(k):
    path = os.path.join(OUT, k + ".png")
    if os.path.exists(path): return k, "exists"
    body = json.dumps({"model": os.environ.get("IMG_MODEL", "gpt-image-2"), "prompt": S[k] + STYLE,
                       "size": "1536x1024", "quality": os.environ.get("IMG_Q", "medium"), "n": 1}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=body,
                                 headers={"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "application/json"})
    for a in range(3):
        try:
            data = json.load(urllib.request.urlopen(req, timeout=600)); break
        except urllib.error.HTTPError as e:
            msg = f"HTTP {e.code} {e.read()[:300]!r}"
            if e.code not in (429, 500, 502, 503): return k, msg
        except Exception as e:
            msg = repr(e)
    else:
        return k, msg
    open(path, "wb").write(base64.b64decode(data["data"][0]["b64_json"])); return k, "ok " + json.dumps(data.get("usage", {}))[:120]
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with cf.ThreadPoolExecutor(4) as ex:
        for k, st in ex.map(gen, sys.argv[1:] or list(S)): print(k, st, flush=True)
