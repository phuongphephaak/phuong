import math, os, urllib.request, json, numpy as np
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
L = "s2cloudless_3857"
def t(lon, lat, z):
    n = 2 ** z; return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
LEV = {5: (82, -6, 128, 36), 7: (95, 2, 121, 28), 10: (104.5, 14.0, 109.5, 20.0), 13: (106.55, 16.55, 107.42, 17.42)}
os.makedirs("tiles", exist_ok=True); meta = {}
for z, (lo0, la0, lo1, la1) in LEV.items():
    x0, y0 = t(lo0, la1, z); x1, y1 = t(lo1, la0, z)
    xs = range(int(x0), int(x1) + 1); ys = range(int(y0), int(y1) + 1)
    def get(xy):
        x, y = xy; p = f"tiles/{z}_{x}_{y}.jpg"
        if not os.path.exists(p) or os.path.getsize(p) < 500:
            for k in range(5):
                try:
                    req = urllib.request.Request(f"https://tiles.maps.eox.at/wmts/1.0.0/{L}/default/g/{z}/{y}/{x}.jpg", headers={"User-Agent": "map-research/1.0"})
                    open(p, "wb").write(urllib.request.urlopen(req, timeout=60).read()); break
                except Exception as e: print("retry", z, x, y, e)
        return p
    with ThreadPoolExecutor(6) as ex: list(ex.map(get, [(x, y) for y in ys for x in xs]))
    M = Image.new("RGB", (len(xs) * 256, len(ys) * 256))
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            M.paste(Image.open(f"tiles/{z}_{x}_{y}.jpg").convert("RGB"), (i * 256, j * 256))
    M.save(f"mosaic_{z}.jpg", quality=95); meta[z] = [xs[0], ys[0], len(xs), len(ys)]
    print(z, M.size, flush=True)
json.dump(meta, open("mosaic_meta.json", "w"))
