"""Sa bàn 3D Điện Biên Phủ – phong cách "bàn cờ" (học từ Verdun 3D).
Quân ta = XANH, quân Pháp (địch) = ĐỎ. Đạn nổ: đất văng + bụi + hố.
blender -b -P scene2.py -- [test F.. | render s e | labels]
1 BU = 1 km, gốc = hầm chỉ huy Mường Thanh."""
import bpy, math, json, os, sys
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SHOTS = {"A": (1, 270), "B": (271, 450), "C": (451, 630)}
rng = np.random.default_rng(7)
X0, X1, Y0, Y1 = -7.5, 7.5, -8.0, 9.0


def fbm(shape, octaves, seed, base=4):
    r = np.random.default_rng(seed); out = np.zeros(shape)
    for o in range(octaves):
        f = 2 ** o
        g = r.standard_normal((base * f + 3, base * f + 3))
        gy = np.linspace(0, g.shape[0] - 1.001, shape[0]); gx = np.linspace(0, g.shape[1] - 1.001, shape[1])
        iy = gy.astype(int); ix = gx.astype(int); fy = (gy - iy)[:, None]; fx = (gx - ix)[None, :]
        fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
        a = g[iy][:, ix]; b = g[iy][:, ix + 1]; c = g[iy + 1][:, ix]; d = g[iy + 1][:, ix + 1]
        out += ((a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy) / (1.7 ** o)
    return out


POS = {"himlam": (2.6, 2.8), "doclap": (0.6, 5.8), "bankeo": (-1.8, 2.8), "huguette": (-0.75, 0.9),
       "claudine": (-0.6, -0.9), "dominique": (1.55, 0.75), "eliane": (1.35, -0.55), "a1": (1.15, -0.25),
       "isabelle": (0.2, -5.6), "hq": (0.0, 0.0)}
RIVER = [(1.4, 11), (1.0, 8), (0.7, 5), (0.35, 2), (0.3, 0), (0.25, -2.5), (0.5, -5), (0.9, -8), (1.3, -11)]
ry = np.array([p[1] for p in RIVER])[::-1]; rx = np.array([p[0] for p in RIVER])[::-1]


def terrain(nx, ny):
    xs = np.linspace(X0, X1, nx); ys = np.linspace(Y0, Y1, ny); XX, YY = np.meshgrid(xs, ys)
    half = 3.0 + 0.5 * np.sin(YY / 3.0) + 0.25 * np.cos(YY / 1.3)
    d = np.abs(XX - (0.4 + 0.5 * np.sin(YY / 5.0))) - half
    n1 = fbm(XX.shape, 6, 11); n2 = fbm(XX.shape, 7, 23)
    hills = np.clip(d, 0, None)
    Z = 1.05 * (1 - np.exp(-hills / 1.6)) * (0.8 + 0.25 * (1 - np.abs(n2) * 0.9)) + 0.05 * hills
    Z += np.where(d > -0.4, 0.16 * n1 * np.clip((d + 0.4) / 1.5, 0, 1), 0) + 0.01 * n1
    for (bx, by, r, h) in [(2.6, 2.8, 0.45, 0.30), (0.6, 5.8, 0.5, 0.36), (1.55, 0.75, 0.35, 0.22),
                           (1.35, -0.55, 0.35, 0.2), (1.15, -0.25, 0.28, 0.22), (-1.8, 2.8, 0.3, 0.1)]:
        Z += h * np.exp(-((XX - bx) ** 2 + (YY - by) ** 2) / (r * r))
    rvx = np.interp(YY, ry, rx)
    Z -= 0.03 * np.exp(-((XX - rvx) / 0.06) ** 2)
    return xs, ys, XX, YY, Z, d, n1, n2, rvx


xs, ys, XX, YY, Z, _, _, _, _ = terrain(400, 453)


def zat(x, y):
    i = np.clip((y - Y0) / (Y1 - Y0) * (len(ys) - 1), 0, len(ys) - 1); j = np.clip((x - X0) / (X1 - X0) * (len(xs) - 1), 0, len(xs) - 1)
    i0, j0 = int(i), int(j); i1, j1 = min(i0 + 1, len(ys) - 1), min(j0 + 1, len(xs) - 1); fi, fj = i - i0, j - j0
    return float(Z[i0, j0] * (1 - fi) * (1 - fj) + Z[i0, j1] * (1 - fi) * fj + Z[i1, j0] * fi * (1 - fj) + Z[i1, j1] * fi * fj)


# ------------------------------------------------------------------ texture (bản đồ vẽ tay kiểu Verdun)
def build_texture(path):
    TW, TH = 3000, 3400
    _, _, TX, TY, TZ, Td, m1, m2, rvx = terrain(TW, TH)
    p1 = fbm(TX.shape, 7, 101, 6); p2 = fbm(TX.shape, 6, 202, 10); p3 = fbm(TX.shape, 5, 303, 3)
    s = lambda c: np.array(c, dtype=np.float32)
    floor_a, floor_b = s([0.78, 0.74, 0.62]), s([0.70, 0.70, 0.58])
    hill_a, hill_b = s([0.56, 0.58, 0.50]), s([0.84, 0.84, 0.80])
    C = np.where((p1 > 0.15)[..., None], floor_b, floor_a) * (0.93 + 0.07 * p3[..., None])
    # ruộng bậc nhỏ (vân lưới mờ)
    ca, sa = math.cos(0.35), math.sin(0.35); U = TX * ca - TY * sa; V = TX * sa + TY * ca
    grid = ((np.abs((U * 14 + 0.8 * m1) % 1 - 0.5) > 0.47) | (np.abs((V * 10 + 0.8 * m2) % 1 - 0.5) > 0.47))
    pass  # bỏ vân lưới
    H = np.where((p2 > 0.25)[..., None], hill_b, hill_a) * (0.9 + 0.1 * p3[..., None])
    t = np.clip((TZ - 0.07) / 0.22, 0, 1)[..., None]
    C = C * (1 - t) + H * t
    # mạng đường mòn trắng ngà (đường đồng mức của nhiễu)
    road = np.zeros(TX.shape, bool)
    for sd, w in [(404, 0.009), (505, 0.007)]:
        q = fbm(TX.shape, 3, sd, 3)
        road |= np.abs(q) < w
    edge_soft = np.abs(fbm(TX.shape, 3, 404, 3)) < 0.02
    C = np.where(edge_soft[..., None] & ~road[..., None], C * 0.9, C)
    C = np.where(road[..., None], s([0.90, 0.88, 0.80]) * (0.95 + 0.05 * p3[..., None]), C)
    # đường 41 dọc lòng chảo
    r41 = np.abs(TX - (rvx - 0.55 + 0.15 * np.sin(TY * 1.3))) < 0.012
    C = np.where(r41[..., None], s([0.92, 0.90, 0.82]), C)
    # đất trống quanh cứ điểm + chiến hào kép tối màu
    for k, (px, py) in POS.items():
        r = np.hypot(TX - px, TY - py); ang = np.arctan2(TY - py, TX - px)
        bare = np.clip(1 - (r - 0.18) / 0.12, 0, 1)[..., None]
        C = C * (1 - bare * 0.8) + s([0.62, 0.55, 0.45]) * bare * 0.8
        wob = 0.012 * np.sin(ang * 9 + px)
        for rr in (0.22, 0.25):
            C = np.where((np.abs(r - rr - wob) < 0.0045)[..., None], s([0.20, 0.17, 0.14]), C)
    # sân bay
    ang = math.atan2(2.2, 0.2); dx, dy = math.cos(ang), math.sin(ang)
    lx = (TX + 0.28) * dx + (TY - 0.6) * dy; ly = -(TX + 0.28) * dy + (TY - 0.6) * dx
    C = np.where(((np.abs(lx) < 1.15) & (np.abs(ly) < 0.03))[..., None], s([0.74, 0.73, 0.70]), C)
    # sông Nậm Rốm: lòng xám xanh, mép ngà
    dr = np.abs(TX - rvx)
    C = np.where((dr < 0.065)[..., None], s([0.86, 0.85, 0.78]), C)
    C = np.where((dr < 0.05)[..., None], s([0.30, 0.35, 0.38]) * (0.95 + 0.1 * p3[..., None]), C)
    C = np.clip(C, 0, 1) ** 2.2
    img = bpy.data.images.new("terrain_tex", TW, TH, alpha=True, float_buffer=False)
    px = np.ones((TH, TW, 4), np.float32); px[..., :3] = C
    img.pixels.foreach_set(px.ravel()); img.filepath_raw = path; img.file_format = "PNG"; img.save()
    return img


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.fps = 30
TEX = os.path.join(HERE, "terrain_tex.png")
img = bpy.data.images.load(TEX) if os.path.exists(TEX) else build_texture(TEX)


def mat(name, col, rough=0.6, metal=0.0, emis=None, estr=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emis:
        b.inputs["Emission Color"].default_value = (*emis, 1); b.inputs["Emission Strength"].default_value = estr
    return m


def link(name, mesh, loc=(0, 0, 0), m=None):
    o = bpy.data.objects.new(name, mesh); sc.collection.objects.link(o); o.location = loc
    if m is not None:
        o.material_slots and None
        o.data.materials and None
        o.active_material = m if not o.data.materials else o.active_material
    return o


def prim(kind, **kw):
    getattr(bpy.ops.mesh, f"primitive_{kind}_add")(**kw); o = bpy.context.object; me = o.data
    bpy.data.objects.remove(o); return me


# terrain mesh (UV = vị trí chuẩn hoá)
h_, w_ = Z.shape
V = np.c_[XX.ravel(), YY.ravel(), Z.ravel()]
idx = np.arange(h_ * w_).reshape(h_, w_)
F = np.c_[idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()]
me = bpy.data.meshes.new("terrain"); me.from_pydata(V.tolist(), [], F.tolist()); me.update()
for p in me.polygons: p.use_smooth = True
uv = me.uv_layers.new(name="UV")
loops = np.zeros(len(me.loops), int); me.loops.foreach_get("vertex_index", loops)
uvs = np.c_[(V[loops, 0] - X0) / (X1 - X0), (V[loops, 1] - Y0) / (Y1 - Y0)]
uv.data.foreach_set("uv", uvs.ravel())
tm = bpy.data.materials.new("terrain"); tm.use_nodes = True; nt = tm.node_tree; b = nt.nodes["Principled BSDF"]
ti = nt.nodes.new("ShaderNodeTexImage"); ti.image = img; ti.interpolation = "Cubic"
nt.links.new(ti.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.95
bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25; bump.inputs["Distance"].default_value = 0.004
nt.links.new(ti.outputs["Color"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
me.materials.append(tm)
ter = bpy.data.objects.new("terrain", me); sc.collection.objects.link(ter)
# thành sa bàn
ring = list(idx[0, :]) + list(idx[:, -1]) + list(idx[-1, ::-1]) + list(idx[::-1, 0])
sv = [tuple(V[i]) for i in ring] + [(V[i][0], V[i][1], -0.35) for i in ring]
n = len(ring); sk = bpy.data.meshes.new("skirt"); sk.from_pydata(sv, [], [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)])
sk.materials.append(mat("skirt", (0.07, 0.06, 0.05), 0.8)); sco = bpy.data.objects.new("skirt", sk); sc.collection.objects.link(sco)

# ------------------------------------------------------------------ bụi cây (merged)
tv, tf, tc = [], [], []
for (x, y) in rng.uniform([X0 + .05, Y0 + .05], [X1 - .05, Y1 - .05], (40000, 2)):
    z = zat(x, y)
    if z < 0.08 or rng.random() > min(0.55, z * 0.6): continue
    for c_ in range(int(rng.integers(1, 4))):
        cx, cy = x + rng.normal(0, 0.02), y + rng.normal(0, 0.02); cz = zat(cx, cy); s_ = rng.uniform(0.012, 0.024)
        b0 = len(tv); col = np.array([0.40, 0.43, 0.34]) * rng.uniform(0.75, 1.25)
        for j in range(5):
            a = 2 * math.pi * j / 5; tv.append((cx + s_ * math.cos(a), cy + s_ * math.sin(a), cz + s_ * 0.5))
        tv.append((cx, cy, cz + s_ * 1.6)); tv.append((cx, cy, cz - 0.005))
        for j in range(5):
            tf.append((b0 + j, b0 + (j + 1) % 5, b0 + 5)); tf.append((b0 + (j + 1) % 5, b0 + j, b0 + 6))
        tc += [col] * 7
tm_ = bpy.data.meshes.new("shrubs"); tm_.from_pydata(tv, [], tf); tm_.update()
ca_ = tm_.color_attributes.new("col", "FLOAT_COLOR", "POINT")
ca_.data.foreach_set("color", np.c_[np.array(tc) ** 2.2, np.ones(len(tc))].astype(np.float32).ravel())
shm = bpy.data.materials.new("shrub"); shm.use_nodes = True
vc = shm.node_tree.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "col"
shm.node_tree.links.new(vc.outputs["Color"], shm.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
shm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
tm_.materials.append(shm); sh = bpy.data.objects.new("shrubs", tm_); sc.collection.objects.link(sh)

# nhà dân (khối cam nhỏ như Verdun)
house_me = prim("cube", size=1); house_me.materials.append(mat("house", (0.78, 0.52, 0.33), 0.7))
for i in range(90):
    x, y = rng.uniform(-2.4, 2.8), rng.uniform(-6.8, 6.8)
    if abs(x - np.interp(y, ry, rx)) < 0.12 or zat(x, y) > 0.06: continue
    if min(math.hypot(x - px, y - py) for px, py in POS.values()) < 0.35: continue
    for j in range(int(rng.integers(2, 5))):
        hx, hy = x + rng.normal(0, 0.03), y + rng.normal(0, 0.03)
        o = bpy.data.objects.new("h", house_me); sc.collection.objects.link(o)
        o.location = (hx, hy, zat(hx, hy) + 0.009); o.scale = (0.03, 0.022, 0.018); o.rotation_euler[2] = rng.uniform(0, 3)

# ------------------------------------------------------------------ cờ
pole = mat("pole", (0.85, 0.85, 0.85), 0.4)


def flag_mat(kind):
    m = bpy.data.materials.new("flag_" + kind); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes["Principled BSDF"]; t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(os.path.join(HERE, f"flag_{kind}.png"))
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"]); nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 0.3; return m


FR, VN = flag_mat("fr"), flag_mat("vn")


def flag(x, y, z, fm, s=1.0, seed=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.003 * s, depth=0.12 * s, location=(x, y, z + 0.06 * s))
    bpy.context.object.data.materials.append(pole)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x + 0.033 * s, y, z + 0.1 * s))
    f = bpy.context.object; f.scale = (0.066 * s, 0.044 * s, 1); f.rotation_euler = (math.pi / 2, 0, 0.6)
    bpy.ops.object.transform_apply(scale=True, rotation=False); f.data.materials.append(fm)
    f.modifiers.new("s", "SUBSURF").levels = 2
    w = f.modifiers.new("w", "WAVE"); w.height = 0.004 * s; w.width = 0.04 * s; w.speed = 0.01; w.use_normal = False; w.time_offset = seed


# ------------------------------------------------------------------ quân cờ
RED = mat("red_base", (0.62, 0.03, 0.04), 0.35)
BLUE = mat("blue_base", (0.16, 0.38, 0.85), 0.35)
CONC = mat("concrete", (0.80, 0.78, 0.72), 0.6)
METAL = mat("metal", (0.55, 0.56, 0.58), 0.35, 0.7)
disc_me = prim("cylinder", vertices=40, radius=1, depth=1)
dome_me = prim("uv_sphere", segments=24, ring_count=12, radius=1)
cube_me = prim("cube", size=1)
cyl_me = prim("cylinder", vertices=12, radius=1, depth=1)
dot_me = prim("cylinder", vertices=16, radius=1, depth=1)


def obj(name, mesh, m, loc, scale, rot=(0, 0, 0)):
    o = bpy.data.objects.new(name, mesh); sc.collection.objects.link(o)
    o.location = loc; o.scale = scale; o.rotation_euler = rot
    o.material_slots and None
    if len(mesh.materials) == 0:
        o.data.materials.append(None)
    o.material_slots[0].link = "OBJECT"; o.material_slots[0].material = m
    return o


def pop(o, f, dur=6):
    s = tuple(o.scale); o.scale = (0, 0, 0); o.keyframe_insert("scale", frame=f)
    o.scale = s; o.keyframe_insert("scale", frame=f + dur)


def bunker(x, y, big=1.0):
    big *= 1.7; z = zat(x, y)
    obj("rb", disc_me, RED, (x, y, z + 0.007 * big), (0.055 * big, 0.055 * big, 0.012 * big))
    obj("dm", dome_me, CONC, (x, y, z + 0.013 * big), (0.034 * big, 0.034 * big, 0.022 * big))
    obj("sl", cube_me, mat("slit", (0.05, 0.05, 0.05), 0.9), (x + 0.03 * big, y, z + 0.022 * big), (0.012 * big, 0.02 * big, 0.004 * big))


for k, (px, py) in POS.items():
    big = 1.35 if k in ("hq", "himlam", "doclap", "isabelle") else 1.0
    bunker(px, py, big)
    for j in range(3):
        a = j * 2.09 + px * 3
        bunker(px + 0.19 * math.cos(a), py + 0.19 * math.sin(a), 0.7)
    flag(px - 0.02, py + 0.02, zat(px, py) + 0.03, FR, 1.6 * big, px)
    # bộ binh Pháp: vòng chấm đỏ phòng ngự
    for j in range(12):
        a = j / 12 * 2 * math.pi; r = 0.33 + 0.02 * math.sin(j * 2.3)
        dx_, dy_ = px + r * math.cos(a), py + r * math.sin(a)
        obj("rd", dot_me, RED, (dx_, dy_, zat(dx_, dy_) + 0.006), (0.022, 0.022, 0.01))


def gun(x, y, a, m_base):
    """pháo dã chiến trên đế tròn xanh, nòng hướng góc a"""
    G = 1.8; z = zat(x, y); ca, sa = math.cos(a), math.sin(a)
    R = lambda u, v: (x + G * (u * ca - v * sa), y + G * (u * sa + v * ca))
    obj("gb", disc_me, m_base, (x, y, z + 0.007), (0.062 * G, 0.062 * G, 0.012 * G))
    obj("gc", cube_me, METAL, (*R(-0.015, 0), z + 0.026 * G), (0.06 * G, 0.016 * G, 0.012 * G), (0, 0, a))
    obj("gs", cube_me, METAL, (*R(0.012, 0), z + 0.038 * G), (0.005 * G, 0.05 * G, 0.032 * G), (0, 0, a))
    for v in (-0.026, 0.026):
        obj("gw", cyl_me, METAL, (*R(0.005, v), z + 0.03 * G), (0.017 * G, 0.017 * G, 0.006 * G), (math.pi / 2, 0, a))
    el = math.radians(28)
    bx, by = R(0.04, 0)
    obj("gn", cyl_me, METAL, (bx, by, z + 0.05 * G), (0.0065 * G, 0.0065 * G, 0.075 * G), (0, math.pi / 2 - el, a))
    tip = R(0.04 + 0.037 * math.cos(el), 0)
    return (tip[0], tip[1], z + G * (0.05 + 0.037 * math.sin(el)))


VN_POS = [(4.6, 3.6), (4.4, 1.2), (4.8, -1.4), (3.9, 5.6), (1.6, 7.6), (-1.4, 7.4), (-4.3, 4.4), (-4.5, 1.0),
          (-4.6, -2.6), (3.8, -4.4), (-3.4, -6.0), (3.4, 4.5)]
GUNS = []
for i, (px, py) in enumerate(VN_POS):
    a = math.atan2(-py, -px); tx, ty = -math.sin(a), math.cos(a)
    for j in (-1, 0, 1):
        GUNS.append(gun(px + j * 0.26 * tx, py + j * 0.26 * ty, a, BLUE))
    flag(px - 0.1 * math.cos(a), py - 0.1 * math.sin(a), zat(px, py) + 0.02, VN, 1.7, i)

# vòng vây: chấm xanh hiện dần 320→440
RP = []
for t_ in np.linspace(0, 2 * math.pi, 170, endpoint=False):
    yy = 1.0 + 6.2 * math.sin(t_); xx = 0.4 + 0.5 * math.sin(yy / 5) + (3.0 + 0.5 * math.sin(yy / 3) + 0.45) * math.cos(t_)
    RP.append((xx, yy))
for i, (x, y) in enumerate(RP):
    o = obj("ring", dot_me, BLUE, (x, y, zat(x, y) + 0.008), (0.045, 0.045, 0.014)); pop(o, 320 + int(i * 120 / len(RP)), 5)

# bộ binh ta: hàng chấm xanh tiến vào Him Lam 495→610
HL = POS["himlam"]
for li, (sx, sy, mx, my) in enumerate([(4.3, 4.2, 3.6, 3.7), (3.9, 1.6, 3.4, 2.1), (3.0, 5.2, 2.9, 4.1), (1.2, 3.9, 1.8, 3.5)]):
    tt = np.linspace(0, 1, 120)
    px_ = (1 - tt) ** 2 * sx + 2 * (1 - tt) * tt * mx + tt ** 2 * HL[0]; py_ = (1 - tt) ** 2 * sy + 2 * (1 - tt) * tt * my + tt ** 2 * HL[1]
    L = np.r_[0, np.cumsum(np.hypot(np.diff(px_), np.diff(py_)))]
    stop = L[-1] - 0.27; k = 0; d_ = 0.0
    while d_ < stop:
        x = np.interp(d_, L, px_); y = np.interp(d_, L, py_)
        o = obj("inf", dot_me, BLUE, (x, y, zat(x, y) + 0.008), (0.03, 0.03, 0.012)); pop(o, 495 + li * 6 + k * 4, 4)
        k += 1; d_ += 0.085

# ------------------------------------------------------------------ nổ: chớp + đất văng + bụi + hố
FLASH = mat("flash", (1, 0.6, 0.25), 0.5, emis=(1.0, 0.55, 0.18), estr=35)
DIRT = mat("dirt", (0.16, 0.12, 0.09), 0.95)
DUST = mat("dust", (0.30, 0.25, 0.20), 1.0)
CRATER = mat("crater", (0.10, 0.08, 0.07), 0.95)
RIM = mat("rim", (0.26, 0.21, 0.16), 0.95)
chunk_me = prim("ico_sphere", subdivisions=1, radius=1)
puff_me = prim("ico_sphere", subdivisions=4, radius=1)
torus_me = prim("torus", major_radius=1, minor_radius=0.25, major_segments=24, minor_segments=8)
clouds = bpy.data.textures.new("clouds", "CLOUDS"); clouds.noise_scale = 0.35


def burst(x, y, f, big=1.0, light=True):
    z = zat(x, y)
    fl = obj("fl", puff_me, FLASH, (x, y, z + 0.015), (0, 0, 0))
    for fr, s in [(f - 1, 0), (f, 0.04 * big), (f + 2, 0.06 * big), (f + 5, 0)]:
        fl.scale = (s, s, s * 0.8); fl.keyframe_insert("scale", frame=fr)
    if light:
        Ld = bpy.data.lights.new("L", "POINT"); Ld.color = (1, 0.6, 0.25); Ld.shadow_soft_size = 0.02
        lo = bpy.data.objects.new("L", Ld); sc.collection.objects.link(lo); lo.location = (x, y, z + 0.08)
        for fr, e in [(f - 1, 0), (f, 25 * big), (f + 5, 0)]:
            Ld.energy = e; Ld.keyframe_insert("energy", frame=fr)
    # hố + gờ đất
    cr = obj("cr", disc_me, CRATER, (x, y, z + 0.002), (0.045 * big, 0.045 * big, 0.003)); pop(cr, f, 2)
    rim = obj("rim", torus_me, RIM, (x, y, z + 0.003), (0.055 * big, 0.055 * big, 0.012 * big)); pop(rim, f, 3)
    # đất văng theo đường parabol
    for i in range(22):
        ang = rng.uniform(0, 2 * math.pi); dist = rng.uniform(0.04, 0.22) * big; hmax = rng.uniform(0.06, 0.26) * big
        T = int(rng.integers(14, 26)); sz = rng.uniform(0.005, 0.013) * big
        ex, ey = x + dist * math.cos(ang), y + dist * math.sin(ang); ez = zat(ex, ey) + sz * 0.5
        c = obj("ch", chunk_me, DIRT, (x, y, z), (0, 0, 0))
        c.keyframe_insert("scale", frame=f - 1); c.scale = (sz, sz * 0.8, sz * 0.7); c.keyframe_insert("scale", frame=f)
        steps = 6
        for s in range(steps + 1):
            u = s / steps; fr = f + round(u * T)
            c.location = (x + (ex - x) * u, y + (ey - y) * u, z + (ez - z) * u + 4 * hmax * u * (1 - u))
            c.rotation_euler = (u * rng.uniform(3, 9), u * rng.uniform(3, 9), 0)
            c.keyframe_insert("location", frame=fr); c.keyframe_insert("rotation_euler", frame=fr)
        for fc in c.animation_data.action.fcurves:
            if fc.data_path == "location":
                for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
        # đất rơi xuống rồi lẫn vào mặt đất
        c.keyframe_insert("scale", frame=f + T + 60); c.scale = (0, 0, 0); c.keyframe_insert("scale", frame=f + T + 110)
    # bụi khói nâu
    for j in range(3):
        p = obj("pf", puff_me, DUST, (x + rng.normal(0, 0.015 * big), y + rng.normal(0, 0.015 * big), z), (0, 0, 0))
        dm = p.modifiers.new("d", "DISPLACE"); dm.texture = clouds; dm.strength = 0.45; dm.mid_level = 0.5
        p.keyframe_insert("scale", frame=f + j); p.keyframe_insert("location", frame=f + j)
        s = rng.uniform(0.018, 0.03) * big
        p.scale = (s, s, s * 1.1); p.location.z = z + 0.02 * big * (j + 1); p.keyframe_insert("scale", frame=f + 10 + 4 * j)
        p.keyframe_insert("location", frame=f + 10 + 4 * j)
        p.scale = (s * 2.0, s * 2.0, s * 1.6); p.location.z = z + 0.05 * big * (j + 1); p.keyframe_insert("scale", frame=f + 70)
        p.keyframe_insert("location", frame=f + 70)
        p.scale = (0, 0, 0); p.keyframe_insert("scale", frame=f + 130)


hx, hy = HL
for i in range(20):
    burst(hx + rng.normal(0, 0.14), hy + rng.normal(0, 0.14), 470 + i * 7 + int(rng.integers(0, 5)), rng.uniform(0.9, 1.3), i % 2 == 0)
for k in ["dominique", "eliane", "a1", "bankeo", "doclap", "huguette"]:
    for i in range(2):
        burst(POS[k][0] + rng.normal(0, 0.1), POS[k][1] + rng.normal(0, 0.1), 462 + 60 * i + int(rng.integers(0, 40)), 1.0, False)
# chớp đầu nòng + khói nhẹ tại các khẩu pháo xanh (bắt đầu 17:05 = khung 455)
GUNSMOKE = mat("gunsmoke", (0.75, 0.73, 0.70), 1.0)
for (gx, gy, gz) in GUNS:
    for i in range(3):
        f = 455 + int(rng.integers(0, 160))
        fl = obj("mf", puff_me, FLASH, (gx, gy, gz), (0, 0, 0))
        for fr, s in [(f - 1, 0), (f, 0.022), (f + 2, 0)]:
            fl.scale = (s, s, s); fl.keyframe_insert("scale", frame=fr)
        p = obj("ms", puff_me, GUNSMOKE, (gx, gy, gz), (0, 0, 0))
        p.modifiers.new("d", "DISPLACE").texture = clouds; p.modifiers["d"].strength = 0.3
        p.keyframe_insert("scale", frame=f); p.keyframe_insert("location", frame=f)
        p.scale = (0.03, 0.03, 0.03); p.location.z = gz + 0.04; p.keyframe_insert("scale", frame=f + 12); p.keyframe_insert("location", frame=f + 12)
        p.scale = (0, 0, 0); p.location.z = gz + 0.1; p.keyframe_insert("scale", frame=f + 60); p.keyframe_insert("location", frame=f + 60)

# ------------------------------------------------------------------ ánh sáng
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 4.6; sun.color = (1.0, 0.93, 0.84); sun.angle = math.radians(4)
so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(48), 0, math.radians(-140))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; nt = w.node_tree
bgL = nt.nodes["Background"]; bgL.inputs["Color"].default_value = (0.55, 0.58, 0.62, 1); bgL.inputs["Strength"].default_value = 0.9
bgC = nt.nodes.new("ShaderNodeBackground"); bgC.inputs["Color"].default_value = (0.03, 0.03, 0.035, 1)
lp = nt.nodes.new("ShaderNodeLightPath"); mx = nt.nodes.new("ShaderNodeMixShader")
nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0]); nt.links.new(bgL.outputs[0], mx.inputs[1]); nt.links.new(bgC.outputs[0], mx.inputs[2])
nt.links.new(mx.outputs[0], nt.nodes["World Output"].inputs["Surface"])


# ------------------------------------------------------------------ máy quay
def P(x, y, dz): return (x, y, zat(x, y) + dz)


def cam(name, keys, fstop, lens):
    c = bpy.data.cameras.new(name); c.lens = lens; c.dof.use_dof = True; c.dof.aperture_fstop = fstop; c.clip_start = 0.01
    o = bpy.data.objects.new(name, c); sc.collection.objects.link(o)
    tgt = bpy.data.objects.new(name + "_t", None); sc.collection.objects.link(tgt)
    tc = o.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
    c.dof.focus_object = tgt
    for k in keys:
        fr, loc, look = k[:3]
        o.location = loc; o.keyframe_insert("location", frame=fr); tgt.location = look; tgt.keyframe_insert("location", frame=fr)
        if len(k) > 3:
            c.dof.aperture_fstop = k[3]; c.dof.keyframe_insert("aperture_fstop", frame=fr)
    acts = [o.animation_data.action, tgt.animation_data.action] + ([c.animation_data.action] if c.animation_data else [])
    for ac in acts:
        for fc in ac.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = "BEZIER"; kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
            fc.keyframe_points[0].interpolation = "BEZIER"
    return o


A, B, C = SHOTS["A"], SHOTS["B"], SHOTS["C"]
# A: lượn sát mặt sa bàn qua các cứ điểm đỏ → xoay vòng, bay lên nhìn toàn cảnh từ trên cao
camA = cam("camA", [
    (A[0], (0.4, -0.9, 13.5), (0.4, 0.7, 0.0), 3.0),
    (110, (-4.5, -5.8, 6.2), (0.3, 0.6, 0.0), 0.9),
    (200, (-3.0, -3.4, 1.7), (0.1, 0.4, 0.05), 0.45),
    (A[1], (-1.6, -2.7, 0.95), (0.5, 0.7, 0.05), 0.35)], 0.5, 30)
# B: lướt thấp dọc trận địa pháo xanh trên núi phía đông → bay lên thấy vòng vây khép kín
camB = cam("camB", [
    (B[0], (6.6, -3.6, 1.9), (4.6, -0.4, 0.5), 0.5),
    (340, (6.9, -0.6, 1.9), (4.5, 2.4, 0.5), 0.5),
    (B[1], (8.5, -7.5, 9.5), (0.5, 0.9, 0.0), 1.5)], 0.4, 28)
# C: quỹ đạo xoay quanh Him Lam khi pháo dội xuống
orb = []
for i, fr in enumerate(np.linspace(C[0], C[1], 5).astype(int)):
    a = math.radians(-95 + 55 * i / 4); r = 1.7 - 0.25 * i / 4; h = 1.45 - 0.2 * i / 4
    orb.append((int(fr), (HL[0] + r * math.cos(a), HL[1] + r * math.sin(a), zat(*HL) + h), (HL[0], HL[1] + 0.05, zat(*HL) + 0.02), 0.5))
camC = cam("camC", orb, 0.5, 38)
for nm, (s, e) in SHOTS.items():
    mk = sc.timeline_markers.new(nm, frame=s); mk.camera = {"A": camA, "B": camB, "C": camC}[nm]
sc.camera = camA; sc.frame_start, sc.frame_end = 1, C[1]

r = sc.render; r.engine = "CYCLES"; r.resolution_x, r.resolution_y = 1280, 720
sc.cycles.device = "CPU"; sc.cycles.samples = int(os.environ.get("SAMPLES", 12)); sc.cycles.use_denoising = True
sc.cycles.denoiser = "OPENIMAGEDENOISE"; sc.cycles.max_bounces = 3; sc.cycles.use_adaptive_sampling = True
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "None"
r.image_settings.file_format = "JPEG"; r.image_settings.quality = 94

from bpy_extras.object_utils import world_to_camera_view


def export_labels():
    out = {}
    for f in range(sc.frame_start, sc.frame_end + 1):
        sc.frame_set(f); row = {}
        for k, (x, y) in POS.items():
            p = world_to_camera_view(sc, sc.camera, Vector((x, y, zat(x, y) + 0.12)))
            row[k] = [round(p.x, 4), round(1 - p.y, 4), round(p.z, 3)]
        out[f] = row
    json.dump(out, open(os.path.join(HERE, "labels.json"), "w"))


if ARGS and ARGS[0] == "test":
    for f in ARGS[1:]:
        sc.frame_set(int(f)); r.filepath = os.path.join(HERE, "t2", f"t_{int(f):04d}.jpg"); bpy.ops.render.render(write_still=True)
elif ARGS and ARGS[0] == "render":
    export_labels(); sc.frame_start, sc.frame_end = int(ARGS[1]), int(ARGS[2])
    r.filepath = os.path.join(HERE, "frames2", "f_####"); bpy.ops.render.render(animation=True)
elif ARGS and ARGS[0] == "labels":
    export_labels()
