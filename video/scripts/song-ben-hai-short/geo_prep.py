"""Chuẩn bị hình học (Web Mercator, đơn vị px tại zoom 0 = 256): Việt Nam, Bắc/Nam, Quảng Trị, sông Bến Hải, giới tuyến."""
import json, math, pickle
from shapely.geometry import shape, LineString, Polygon, MultiPolygon, Point
from shapely.ops import unary_union, linemerge

D = "data/"


def merc(lon, lat):
    return (lon + 180) / 360 * 256, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * 256


def polys_of(g):
    g = g.buffer(0)
    out = []
    for p in (g.geoms if isinstance(g, MultiPolygon) else [g]):
        if p.is_empty or p.area < 1e-6: continue
        out.append([[merc(*c) for c in p.exterior.coords]] + [[merc(*c) for c in r.coords] for r in p.interiors])
    return out


c = json.load(open(D + "ne_10m_admin_0_countries.geojson"))
VN = [shape(f["geometry"]) for f in c["features"] if f["properties"]["ADMIN"] == "Vietnam"][0]
a = json.load(open(D + "ne_10m_admin_1_states_provinces.geojson"))
QT = [shape(f["geometry"]) for f in a["features"] if f["properties"].get("admin") == "Vietnam" and f["properties"].get("name") == "Quảng Trị"][0]
bh = shape(json.load(open(D + "benhai.json"))[0]["geojson"])
river = linemerge(bh) if bh.geom_type == "MultiLineString" else bh
if river.geom_type == "MultiLineString":
    river = max(river.geoms, key=lambda g: g.length)
rc = list(river.coords)
if rc[0][0] > rc[-1][0]: rc = rc[::-1]          # tây -> đông
print("river", len(rc), rc[0], rc[-1])
mouth = (107.1064, 17.0286)                      # cửa Tùng
if rc[-1][0] < mouth[0] - 0.003: rc.append(mouth)
# giới tuyến: kéo dài về phía tây dọc vĩ tuyến tới biên giới Lào
west = [(100.0, rc[0][1]), (rc[0][0] - 0.02, rc[0][1])]
line = west + rc + [(mouth[0] + 0.25, mouth[1] + 0.02), (112.0, mouth[1] + 0.02)]
north_box = Polygon(line + [(112.0, 30.0), (100.0, 30.0)])
VN_N = VN.intersection(north_box); VN_S = VN.difference(north_box)
QT_N = QT.intersection(north_box); QT_S = QT.difference(north_box)
demarc = [c_ for c_ in line if 106.0 < c_[0] < 107.2]
demarc = [(c_[0], c_[1]) for c_ in LineString(west[-1:] + rc).coords]
# giới tuyến phía tây (đoạn thẳng theo vĩ tuyến tới biên giới Lào)
laos_w = [(106.52, rc[0][1]), rc[0]]
dmz_line = laos_w + rc
L = LineString(dmz_line)
dmzN = list(L.parallel_offset(0.045, "left").coords); dmzS = list(L.parallel_offset(0.045, "right").coords)
out = {
    "VN": polys_of(VN), "VN_N": polys_of(VN_N), "VN_S": polys_of(VN_S),
    "QT_N": polys_of(QT_N), "QT_S": polys_of(QT_S),
    "river": [merc(*p) for p in rc], "dmz": [merc(*p) for p in dmz_line],
    "dmzN": [merc(*p) for p in dmzN], "dmzS": [merc(*p) for p in dmzS],
    "glow": [merc(*p) for p in [(106.40, rc[0][1] + 0.02)] + laos_w + rc + [(107.30, 17.08)]],
    "hoangsa": [merc(111.6, 16.55), merc(112.3, 16.45), merc(111.8, 16.0), merc(112.7, 16.8), merc(111.2, 15.8)],
    "truongsa": [merc(114.3, 11.4), merc(113.8, 10.4), merc(114.9, 9.9), merc(112.9, 8.65), merc(115.6, 10.3), merc(114.1, 8.9)],
    "pts": {k: merc(*v) for k, v in {"hienluong": (107.0515, 17.0039), "cuatung": (107.1064, 17.0286), "vinhlinh": (106.98, 17.08),
                                      "giolinh": (106.98, 16.90), "bandong": (110.6, 17.8), "vn": (105.2, 21.3), "mbac": (105.0, 20.4),
                                      "mnam": (106.6, 12.4), "vt17": (106.70, 17.0), "hoangsa": (111.9, 16.4), "truongsa": (114.2, 10.0),
                                      "dmz": (106.80, 17.0)}.items()},
}
pickle.dump(out, open("geo.pkl", "wb"))
print({k: (len(v) if isinstance(v, list) else len(v)) for k, v in out.items()})
