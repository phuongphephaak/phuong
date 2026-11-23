import json, math, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
Image.MAX_IMAGE_PIXELS = None
meta = json.load(open("mosaic_meta.json"))
land = json.load(open("data/ne_10m_land.geojson"))  # tải: natural-earth-vector/geojson/ne_10m_land.geojson
def merc(lon, lat, z):
    n = 2 ** z * 256; return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
for z in (7, 10, 13):
    x0, y0, nx, ny = meta[str(z)]; W, H = nx * 256, ny * 256
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    lon0 = x0 / 2 ** z * 360 - 180; lon1 = (x0 + nx) / 2 ** z * 360 - 180
    for f in land["features"]:
        g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for P in polys:
            ring = P[0]; xs = [p[0] for p in ring]
            if max(xs) < lon0 - 1 or min(xs) > lon1 + 1: continue
            pts = [(merc(lo, la, z)[0] - x0 * 256, merc(lo, la, z)[1] - y0 * 256) for lo, la in ring]
            d.polygon(pts, fill=255)
            for hole in P[1:]:
                d.polygon([(merc(lo, la, z)[0] - x0 * 256, merc(lo, la, z)[1] - y0 * 256) for lo, la in hole], fill=0)
    sea = 255 - np.asarray(m)
    Image.fromarray(sea).save(f"sea_{z}.png"); print(z, (sea > 0).mean())
