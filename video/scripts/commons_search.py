"""Search Wikimedia Commons files and print title, size, license, author.
Usage: python commons_search.py "query" [limit]
"""
import json, sys, urllib.parse, urllib.request, re

UA = {"User-Agent": "VideoDraft/1.0 (educational project)"}


def search(q, limit=15):
    params = {"action": "query", "format": "json", "generator": "search", "gsrsearch": q,
              "gsrnamespace": 6, "gsrlimit": limit, "prop": "imageinfo",
              "iiprop": "url|size|extmetadata", "iiurlwidth": 1920}
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    import time
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                data = json.load(r)
            break
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(int(e.headers.get("Retry-After", 0) or 0) or 5 * (attempt + 1))
    out = []
    for p in data.get("query", {}).get("pages", {}).values():
        ii = p["imageinfo"][0]
        md = ii.get("extmetadata", {})
        g = lambda k: re.sub("<[^>]+>", "", md.get(k, {}).get("value", "")).strip()[:60]
        out.append({"title": p["title"], "w": ii["width"], "h": ii["height"],
                    "license": g("LicenseShortName"), "artist": g("Artist"),
                    "thumb": ii.get("thumburl"), "page": ii.get("descriptionurl")})
    return out


if __name__ == "__main__":
    for r in search(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 15):
        print(f'{r["w"]}x{r["h"]} | {r["license"]} | {r["artist"]} | {r["title"]}')
