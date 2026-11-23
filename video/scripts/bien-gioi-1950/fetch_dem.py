import math, os, urllib.request, numpy as np
from PIL import Image
Z = 14
LAT0, LAT1, LON0, LON1 = 22.355, 22.475, 106.300, 106.470
def tile(lat, lon):
    n = 2 ** Z; x = (lon + 180) / 360 * n; y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n; return x, y
x0, y1 = tile(LAT0, LON0); x1, y0 = tile(LAT1, LON1)
tx = range(int(x0), int(x1) + 1); ty = range(int(y0), int(y1) + 1)
rows = []
for y in ty:
    row = []
    for x in tx:
        p = f"dem/{Z}_{x}_{y}.png"
        if not os.path.exists(p):
            urllib.request.urlretrieve(f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z}/{x}/{y}.png", p)
        a = np.asarray(Image.open(p).convert("RGB")).astype(np.float64)
        row.append(a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768)
    rows.append(np.hstack(row))
E_ = np.vstack(rows)
# cắt đúng bbox
px = lambda v0, v: (v - v0) * 256
cx0, cy0 = px(tx[0], x0), px(ty[0], y0); cx1, cy1 = px(tx[0], x1), px(ty[0], y1)
E_ = E_[int(cy0):int(cy1), int(cx0):int(cx1)]
np.save("dem.npy", E_.astype(np.float32))
km_w = (LON1 - LON0) * 111.32 * math.cos(math.radians((LAT0 + LAT1) / 2)); km_h = (LAT1 - LAT0) * 110.57
print(E_.shape, E_.min(), E_.max(), f"{km_w:.2f} x {km_h:.2f} km", len(tx) * len(ty), "tiles")
