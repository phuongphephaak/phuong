"""Download chosen Wikimedia Commons files (1920px) and write credits.json."""
import json, os, re, sys, time, urllib.parse, urllib.request

UA = {"User-Agent": "PhuongVideoDraft/1.0 (https://github.com/phuongphephaak/phuong) python-urllib"}
PICKS = {
    "ship1": "File:British destroyer HMS COVENTRY (D118) underway (330-CFD-DN-SC-87-05083).jpg",
    "ship2": "File:HMS Coventry (D118) underway in the Atlantic Ocean, circa in 1981 (6417242).jpg",
    "broadsword": "File:HMS Broadsword, 1982 (IWM).jpg",
    "kh9": "File:British warships during the Battle of San Carlos - KH-9 image.png",
    "antelope": "File:HMS Antelope 1982.jpg",
    "a4museum": "File:Avión Douglas A4 Skyhawk de la Fuerza Aérea Argentina que participó en la Guerra de Malvinas en 1982 como parte de un museo que entonces funcionaba en un sector del Aeroparque Metropolitano \"Jorge Newbery\" (1997).jpg",
    "a4faa": "File:C-240 Douglas A-4 Skyhawk Fuerza Aerea Argentina (8164188365).jpg",
    "a4flight": "File:Douglas TA-4J Skyhawk - 51168561465.jpg",
    "action": "File:Action stations Falklands 1982.JPG",
    "hermes": "File:HMS Broadsword and Hermes, 1982 (IWM).jpg",
}


def get(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(45 * (attempt + 1))
    raise RuntimeError("rate limited: " + url)


out = sys.argv[1]
os.makedirs(out, exist_ok=True)
credits = json.load(open(os.path.join(out, "credits.json"))) if os.path.exists(os.path.join(out, "credits.json")) else {}
for key, title in PICKS.items():
    if key in credits:
        continue
    q = urllib.parse.urlencode({"action": "query", "format": "json", "titles": title, "prop": "imageinfo",
                                "iiprop": "url|size|extmetadata", "iiurlwidth": 1920})
    page = next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?" + q))["query"]["pages"].values()))
    ii = page["imageinfo"][0]
    if ii.get("thumbwidth", 0) >= ii.get("width", 0):  # original <= 1920px: ask for a slightly smaller thumb
        q = q.replace("iiurlwidth=1920", "iiurlwidth=%d" % (ii["width"] - 1))
        ii = next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?" + q))["query"]["pages"].values()))["imageinfo"][0]
    md = ii["extmetadata"]
    clean = lambda k: re.sub(r"\s+", " ", re.sub("<[^>]+>", "", md.get(k, {}).get("value", ""))).strip()
    url = (ii.get("thumburl") or ii["url"]).split("?")[0]
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower() or ".jpg"
    try:
        blob = get(url)
    except Exception as e:
        print("SKIP", key, e, flush=True); time.sleep(60); continue
    with open(os.path.join(out, key + ext), "wb") as f:
        f.write(blob)
    credits[key] = {"title": title, "license": clean("LicenseShortName"), "artist": clean("Artist")[:80],
                    "page": ii["descriptionurl"]}
    json.dump(credits, open(os.path.join(out, "credits.json"), "w"), ensure_ascii=False, indent=1)
    print(key, credits[key]["license"], "|", credits[key]["artist"], flush=True)
    time.sleep(40)
json.dump(credits, open(os.path.join(out, "credits.json"), "w"), ensure_ascii=False, indent=1)
