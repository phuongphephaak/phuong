"""Sa bàn 3D lòng chảo Điện Biên Phủ (minh họa). blender -b -P scene.py -- [test FRAME | render]
Đơn vị: 1 BU = 1 km. x đông, y bắc. Gốc = hầm chỉ huy Mường Thanh."""
import bpy, bmesh, math, json, os, sys
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
FPS = 30
SHOTS = {"A": (1, 270), "B": (271, 450), "C": (451, 630)}   # 9 s + 6 s + 6 s
rng = np.random.default_rng(3)

# ---------------- terrain ----------------
X0, X1, Y0, Y1 = -7.5, 7.5, -8.0, 9.0
N = 360
xs = np.linspace(X0, X1, N); ys = np.linspace(Y0, Y1, int(N * (Y1 - Y0) / (X1 - X0)))
XX, YY = np.meshgrid(xs, ys)


def fbm(shape, octaves, seed):
    r = np.random.default_rng(seed); out = np.zeros(shape)
    from numpy.fft import fft2, ifft2
    for o in range(octaves):
        f = 2 ** o
        g = r.standard_normal((4 * f + 3, 4 * f + 3))
        # bilinear upsample
        gy = np.linspace(0, g.shape[0] - 1.001, shape[0]); gx = np.linspace(0, g.shape[1] - 1.001, shape[1])
        iy = gy.astype(int); ix = gx.astype(int); fy = (gy - iy)[:, None]; fx = (gx - ix)[None, :]
        fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
        a = g[iy][:, ix]; b = g[iy][:, ix + 1]; c = g[iy + 1][:, ix]; d = g[iy + 1][:, ix + 1]
        out += ((a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy) / (1.7 ** o)
    return out


half = 3.0 + 0.5 * np.sin(YY / 3.0) + 0.25 * np.cos(YY / 1.3)
cxv = 0.4 + 0.5 * np.sin(YY / 5.0)
d = np.abs(XX - cxv) - half
n1 = fbm(XX.shape, 6, 11)
hills = np.clip(d, 0, None)
n2 = fbm(XX.shape, 7, 23)
ridge = 1 - np.abs(n2) * 0.9
Z = 1.9 * (1 - np.exp(-hills / 1.5)) * (0.75 + 0.35 * ridge) + 0.08 * hills
Z += np.where(d > -0.4, 0.32 * n1 * np.clip((d + 0.4) / 1.5, 0, 1), 0)
Z += 0.012 * n1                                             # paddy micro relief
POS = {"himlam": (2.6, 2.8), "doclap": (0.6, 5.8), "bankeo": (-1.8, 2.8), "huguette": (-0.75, 0.9),
       "claudine": (-0.6, -0.9), "dominique": (1.55, 0.75), "eliane": (1.35, -0.55), "a1": (1.15, -0.25),
       "isabelle": (0.2, -5.6), "hq": (0.0, 0.0)}
for (bx, by, r, hgt) in [(2.6, 2.8, 0.45, 0.30), (0.6, 5.8, 0.5, 0.36), (1.55, 0.75, 0.35, 0.22),
                         (1.35, -0.55, 0.35, 0.2), (1.15, -0.25, 0.28, 0.22), (-1.8, 2.8, 0.3, 0.1)]:
    Z += hgt * np.exp(-((XX - bx) ** 2 + (YY - by) ** 2) / (r * r))
Z *= 1.0
RIVER = [(1.4, 11), (1.0, 8), (0.7, 5), (0.35, 2), (0.3, 0), (0.25, -2.5), (0.5, -5), (0.9, -8), (1.3, -11)]
ry = np.array([p[1] for p in RIVER])[::-1]; rx = np.array([p[0] for p in RIVER])[::-1]
riv_x = np.interp(YY, ry, rx)
Z -= 0.035 * np.exp(-((XX - riv_x) / 0.06) ** 2)


def zat(x, y):
    i = np.clip((y - Y0) / (Y1 - Y0) * (len(ys) - 1), 0, len(ys) - 1); j = np.clip((x - X0) / (X1 - X0) * (N - 1), 0, N - 1)
    i0, j0 = int(i), int(j); i1, j1 = min(i0 + 1, len(ys) - 1), min(j0 + 1, N - 1); fi, fj = i - i0, j - j0
    return float(Z[i0, j0] * (1 - fi) * (1 - fj) + Z[i0, j1] * (1 - fi) * fj + Z[i1, j0] * fi * (1 - fj) + Z[i1, j1] * fi * fj)


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS


def mat(name, col, rough=0.85, emis=None, estr=0.0, attr=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough
    if attr:
        a = m.node_tree.nodes.new("ShaderNodeVertexColor"); a.layer_name = attr
        m.node_tree.links.new(a.outputs["Color"], b.inputs["Base Color"])
    if emis:
        b.inputs["Emission Color"].default_value = (*emis, 1); b.inputs["Emission Strength"].default_value = estr
    return m


def mesh_obj(name, verts, faces, material=None, colors=None):
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces]); me.update()
    for p in me.polygons: p.use_smooth = True
    if colors is not None:
        ca = me.color_attributes.new("col", "FLOAT_COLOR", "POINT")
        ca.data.foreach_set("color", np.c_[colors, np.ones(len(colors))].astype(np.float32).ravel())
    ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob)
    if material: me.materials.append(material)
    return ob


# terrain mesh with skirt (sa bàn có thành)
h_, w_ = Z.shape
V = np.c_[XX.ravel(), YY.ravel(), Z.ravel()]
idx = np.arange(h_ * w_).reshape(h_, w_)
F = np.c_[idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()]
# colours
slope = np.hypot(*np.gradient(Z, xs[1] - xs[0]))
paddy = np.array([0.36, 0.40, 0.17]); paddy2 = np.array([0.48, 0.44, 0.22]); forest = np.array([0.22, 0.27, 0.12])
rock = np.array([0.33, 0.28, 0.20]); dry = np.array([0.42, 0.33, 0.19])
ca, sa = math.cos(0.35), math.sin(0.35)
U = XX * ca - YY * sa; Vv = XX * sa + YY * ca
cell = (np.floor(U * 9 + 1.2 * n1).astype(int) * 7919 + np.floor(Vv * 6.5 + 0.8 * n2).astype(int) * 104729) % 9973
pal = np.array([[0.42, 0.45, 0.20], [0.47, 0.47, 0.22], [0.39, 0.43, 0.18], [0.50, 0.46, 0.25], [0.44, 0.42, 0.22], [0.40, 0.44, 0.19]])
C = pal[cell % len(pal)] * (0.92 + 0.08 * fbm(XX.shape, 5, 5)[..., None])
edge = ((np.abs(((U * 9 + 1.2 * n1) % 1) - 0.5) > 0.46) | (np.abs(((Vv * 6.5 + 0.8 * n2) % 1) - 0.5) > 0.46))[..., None]
C = np.where(edge, C * 0.7, C)
t = np.clip((Z - 0.06) / 0.3, 0, 1)[..., None]
C = C * (1 - t) + (forest + 0.04 * n1[..., None]) * t
C = C * (1 - np.clip(slope[..., None] - 0.9, 0, 1)) + rock * np.clip(slope[..., None] - 0.9, 0, 1)
# bare/cleared earth around strongpoints (bom đạn cày xới)
for k, (px, py) in POS.items():
    m = np.exp(-((XX - px) ** 2 + (YY - py) ** 2) / 0.12)[..., None]
    C = C * (1 - m) + dry * m
riv = np.exp(-((XX - riv_x) / 0.05) ** 2)[..., None]
C = C * (1 - riv) + np.array([0.08, 0.16, 0.20]) * riv
C = np.clip(C, 0, 1) ** 2.2                      # to linear
terrain = mesh_obj("terrain", V, F, mat("terrain", (1, 1, 1), 0.92, attr="col"), C.reshape(-1, 3))
# skirt
base = -0.35
ring = list(idx[0, :]) + list(idx[:, -1]) + list(idx[-1, ::-1]) + list(idx[::-1, 0])
sv = [V[i] for i in ring] + [(V[i][0], V[i][1], base) for i in ring]
n = len(ring); sf = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
mesh_obj("skirt", sv, sf, mat("skirt", (0.09, 0.07, 0.05), 0.7))

# ---------------- trees (one merged mesh) ----------------
tv, tf, tc = [], [], []
cand = rng.uniform([X0 + 0.05, Y0 + 0.05], [X1 - 0.05, Y1 - 0.05], (60000, 2))
K, R_ = 6, 3
for (x, y) in cand:
    z = zat(x, y)
    if z < 0.07 or rng.random() > min(1, z * 1.2): continue
    s_ = rng.uniform(0.022, 0.04); b0 = len(tv); col = np.array([0.14, 0.22, 0.07]) * rng.uniform(0.7, 1.4) + rng.uniform(0, 0.02)
    for i in range(1, R_):
        ph = math.pi * i / R_
        for j in range(K):
            th = 2 * math.pi * j / K
            tv.append((x + s_ * math.sin(ph) * math.cos(th), y + s_ * math.sin(ph) * math.sin(th), z + s_ * 0.6 + s_ * 1.1 * math.cos(ph)))
    tv.append((x, y, z + s_ * 1.75)); tv.append((x, y, z - 0.01))
    top, bot = b0 + (R_ - 1) * K, b0 + (R_ - 1) * K + 1
    for j in range(K):
        j2 = (j + 1) % K
        tf.append((b0 + j, b0 + j2, top))
        for i in range(R_ - 2):
            tf.append((b0 + i * K + j, b0 + (i + 1) * K + j, b0 + (i + 1) * K + j2, b0 + i * K + j2))
        tf.append((b0 + (R_ - 2) * K + j2, b0 + (R_ - 2) * K + j, bot))
    tc += [col] * ((R_ - 1) * K + 2)
mesh_obj("trees", tv, tf, mat("tree", (1, 1, 1), 0.95, attr="col"), np.array(tc) ** 2.2)

# ---------------- runway, houses ----------------
def box(name, c, size, material, rotz=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.object; o.name = name
    o.scale = size; o.rotation_euler[2] = rotz; o.data.materials.append(material); return o


ang = math.atan2(1.7 + 0.5, -0.18 + 0.38)
box("runway", (-0.28, 0.6, zat(-0.28, 0.6) + 0.004), (0.06, 2.3, 0.01), mat("runway", (0.30, 0.27, 0.22), 0.9), ang - math.pi / 2)
hm = mat("house", (0.35, 0.22, 0.12), 0.8)
for i in range(70):
    x, y = rng.uniform(-2.2, 2.6), rng.uniform(-6.5, 6.5)
    if abs(x - np.interp(y, ry, rx)) < 0.12 or zat(x, y) > 0.06: continue
    box(f"h{i}", (x, y, zat(x, y) + 0.012), (0.035, 0.05, 0.025), hm, rng.uniform(0, 3))

# ---------------- flags (textures) ----------------
def flag_tex(kind):
    return os.path.join(HERE, f"flag_{kind}.png")


def flag_mat(kind):
    m = bpy.data.materials.new("flag_" + kind); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes["Principled BSDF"]; t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(flag_tex(kind))
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"]); nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 0.35; b.inputs["Roughness"].default_value = 0.6
    return m


FR, VN = flag_mat("fr"), flag_mat("vn")
pole = mat("pole", (0.8, 0.8, 0.8), 0.4)


def flag(x, y, z, fm, s=1.0, wave_seed=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.004 * s, depth=0.16 * s, location=(x, y, z + 0.08 * s))
    bpy.context.object.data.materials.append(pole)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x + 0.045 * s, y, z + 0.13 * s))
    f = bpy.context.object; f.scale = (0.09 * s, 0.06 * s, 1); f.rotation_euler = (math.pi / 2, 0, 0.6)
    bpy.ops.object.transform_apply(scale=True, rotation=False)
    f.data.materials.append(fm)
    mod = f.modifiers.new("sub", "SUBSURF"); mod.levels = 2; mod.render_levels = 2
    w = f.modifiers.new("wave", "WAVE"); w.height = 0.006 * s; w.width = 0.05 * s; w.speed = 0.012; w.use_normal = False
    w.time_offset = wave_seed
    return f


# French positions: blue blocks + sandbag ring + tricolour
blue = mat("fr_block", (0.32, 0.55, 0.85), 0.5, emis=(0.2, 0.4, 0.8), estr=0.15)
sand = mat("sand", (0.45, 0.40, 0.30), 0.95)
for k, (px, py) in POS.items():
    z = zat(px, py)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.17, minor_radius=0.022, location=(px, py, z + 0.01))
    bpy.context.object.data.materials.append(sand)
    for j in range(3 if k != "hq" else 1):
        a = j * 2.1 + px
        box(f"fr_{k}{j}", (px + 0.08 * math.cos(a), py + 0.08 * math.sin(a), z + 0.035), (0.11, 0.08, 0.06), blue, a)
    flag(px + 0.02, py - 0.02, z + 0.05, FR, 1.6, px)

# Vietnamese artillery & infantry on surrounding hills
red = mat("vn_block", (0.75, 0.08, 0.06), 0.5, emis=(0.8, 0.05, 0.03), estr=0.25)
VN_POS = [(4.6, 3.6), (4.4, 1.2), (4.8, -1.4), (3.9, 5.6), (1.6, 7.6), (-1.4, 7.4), (-4.3, 4.4), (-4.5, 1.0),
          (-4.6, -2.6), (3.8, -4.4), (-3.4, -6.0), (2.7, 4.6)]
GUNS = []
for i, (px, py) in enumerate(VN_POS):
    z = zat(px, py)
    for j in range(2):
        a = math.atan2(-py, -px)
        o = box(f"vn{i}{j}", (px + 0.09 * j * math.cos(a + 1.5), py + 0.09 * j * math.sin(a + 1.5), z + 0.03), (0.13, 0.09, 0.07), red, a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.008, depth=0.12, location=(px, py, z + 0.07))
    g = bpy.context.object; g.rotation_euler = (0, math.radians(70), a); g.data.materials.append(red); GUNS.append((px, py, z + 0.08, a))
    flag(px - 0.06, py + 0.05, z + 0.06, VN, 1.7, i)

# river
rc = bpy.data.curves.new("river", "CURVE"); rc.dimensions = "3D"; sp = rc.splines.new("POLY")
pts = [(np.interp(y, ry, rx), y) for y in np.linspace(Y0 + 0.05, Y1 - 0.05, 120)]
sp.points.add(len(pts) - 1)
for p, (x, y) in zip(sp.points, pts): p.co = (x, y, zat(x, y) + 0.012, 1)
rc.bevel_depth = 0.03; rc.bevel_resolution = 2
ro = bpy.data.objects.new("river", rc); sc.collection.objects.link(ro); ro.scale[2] = 0.25
ro.data.materials.append(mat("water", (0.05, 0.18, 0.26), 0.08))

# ---------------- animated red encirclement ring ----------------
def tube(name, pts, radius, m, start, end, lift=0.04):
    c = bpy.data.curves.new(name, "CURVE"); c.dimensions = "3D"; s = c.splines.new("POLY"); s.points.add(len(pts) - 1)
    for p, (x, y) in zip(s.points, pts): p.co = (x, y, zat(x, y) + lift, 1)
    c.bevel_depth = radius; c.bevel_resolution = 3; c.use_fill_caps = True
    o = bpy.data.objects.new(name, c); sc.collection.objects.link(o); c.materials.append(m)
    c.bevel_factor_end = 0.0; c.keyframe_insert("bevel_factor_end", frame=start)
    c.bevel_factor_end = 1.0; c.keyframe_insert("bevel_factor_end", frame=end)
    return o


ringm = mat("ring", (0.9, 0.05, 0.04), 0.3, emis=(1.0, 0.04, 0.02), estr=1.6)
rp = []
for t_ in np.linspace(0, 2 * math.pi, 220):
    yy = 1.0 + 6.4 * math.sin(t_); xx = 0.4 + 0.5 * math.sin(yy / 5) + (3.0 + 0.5 * math.sin(yy / 3) + 0.55) * math.cos(t_)
    rp.append((xx, yy))
tube("ring", rp, 0.022, ringm, 300, 420)

# attack arrows onto Him Lam (shot C)
arrows = []
arrm = mat("arrow", (1.0, 0.25, 0.05), 0.3, emis=(1.0, 0.35, 0.05), estr=4.0)
for (sx, sy), (mx, my) in [((4.4, 4.2), (3.6, 3.6)), ((3.7, 1.6), (3.3, 2.2)), ((2.9, 5.2), (2.8, 4.0))]:
    tt = np.linspace(0, 1, 40)
    ex, ey = 2.75, 2.85
    px = (1 - tt) ** 2 * sx + 2 * (1 - tt) * tt * mx + tt ** 2 * ex; py = (1 - tt) ** 2 * sy + 2 * (1 - tt) * tt * my + tt ** 2 * ey
    pts = [(a, b) for a, b in zip(px, py)][:-6]
    arrows.append(tube(f"arrow{len(arrows)}", pts, 0.04, arrm, 470 + 20 * len(arrows), 540 + 20 * len(arrows), 0.12))
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.09, depth=0.18, location=(pts[-1][0], pts[-1][1], zat(*pts[-1]) + 0.12))
    hd = bpy.context.object; hd.data.materials.append(arrm)
    dx, dy = pts[-1][0] - pts[-3][0], pts[-1][1] - pts[-3][1]
    hd.rotation_euler = (math.pi / 2, 0, math.atan2(dy, dx) - math.pi / 2)
    f0 = 540 + 20 * (len(arrows) - 1)
    hd.scale = (0, 0, 0); hd.keyframe_insert("scale", frame=f0 - 2)
    hd.scale = (1, 1, 1); hd.keyframe_insert("scale", frame=f0 + 4)

# ---------------- explosions + smoke ----------------
smokem = bpy.data.materials.new("smoke"); smokem.use_nodes = True
sb = smokem.node_tree.nodes["Principled BSDF"]; sb.inputs["Base Color"].default_value = (0.20, 0.18, 0.16, 1)
sb.inputs["Roughness"].default_value = 1.0
flashm = mat("flash", (1, 0.6, 0.2), 0.5, emis=(1.0, 0.55, 0.15), estr=40)
tex = bpy.data.textures.new("clouds", "CLOUDS"); tex.noise_scale = 0.012


def burst(x, y, f, big=1.0):
    z = zat(x, y)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.05 * big, location=(x, y, z + 0.02))
    fl = bpy.context.object; fl.data.materials.append(flashm)
    for fr, s in [(f - 1, 0.0), (f, 1.0), (f + 3, 1.5), (f + 7, 0.0)]:
        fl.scale = (s, s, s * 0.7); fl.keyframe_insert("scale", frame=fr)
    L = bpy.data.lights.new(f"L{f}{x}", "POINT"); L.color = (1, 0.55, 0.2)
    lo = bpy.data.objects.new(L.name, L); sc.collection.objects.link(lo); lo.location = (x, y, z + 0.12)
    for fr, e in [(f - 1, 0), (f, 60 * big), (f + 6, 0)]:
        L.energy = e; L.keyframe_insert("energy", frame=fr)
    for k in range(3):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=0.035 * big, location=(x + rng.normal(0, 0.03), y + rng.normal(0, 0.03), z))
        p = bpy.context.object; p.data.materials.append(smokem)
        dm = p.modifiers.new("d", "DISPLACE"); dm.texture = tex; dm.strength = 0.022 * big
        p.scale = (0, 0, 0); p.keyframe_insert("scale", frame=f + k)
        s = rng.uniform(0.9, 1.4)
        p.scale = (s, s, s * 1.3); p.location[2] = z + 0.05 * big * (k + 1); p.keyframe_insert("scale", frame=f + 18 + 8 * k)
        p.keyframe_insert("location", frame=f + 18 + 8 * k)
        p.scale = (s * 1.5, s * 1.5, s * 2.2); p.location[2] = z + 0.16 * big * (k + 1); p.keyframe_insert("scale", frame=f + 160)
        p.keyframe_insert("location", frame=f + 160)


hx, hy = POS["himlam"]
for i in range(14):
    burst(hx + rng.normal(0, 0.15), hy + rng.normal(0, 0.15), 468 + i * 11 + int(rng.integers(0, 6)), rng.uniform(0.55, 0.85))
for k in ["dominique", "eliane", "a1", "bankeo", "doclap"]:   # pháo bắn tạm vào các cứ điểm khác
    for i in range(3):
        burst(POS[k][0] + rng.normal(0, 0.12), POS[k][1] + rng.normal(0, 0.12), 456 + 45 * i + int(rng.integers(0, 30)), 0.7)
# muzzle flashes at Vietnamese guns
for (gx, gy, gz, a) in GUNS:
    for i in range(4):
        f = 452 + int(rng.integers(0, 170))
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.03, location=(gx + 0.08 * math.cos(a), gy + 0.08 * math.sin(a), gz + 0.04))
        fl = bpy.context.object; fl.data.materials.append(flashm)
        for fr, s in [(f - 1, 0), (f, 1), (f + 2, 0)]:
            fl.scale = (s, s, s); fl.keyframe_insert("scale", frame=fr)

# ---------------- lights / world ----------------
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 4.5; sun.color = (1.0, 0.80, 0.58); sun.angle = math.radians(3)
so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(62), 0, math.radians(-125))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (0.045, 0.05, 0.06, 1); bg.inputs["Strength"].default_value = 1.0
sc.world.light_settings if False else None
fill = bpy.data.lights.new("fill", "AREA"); fill.energy = 1800; fill.size = 12; fill.color = (0.6, 0.7, 1.0)
fo = bpy.data.objects.new("fill", fill); sc.collection.objects.link(fo); fo.location = (-6, -10, 9); fo.rotation_euler = (math.radians(50), 0, math.radians(-30))

# ---------------- cameras ----------------
def cam(name, keys, focus_keys, fstop, lens=40):
    c = bpy.data.cameras.new(name); c.lens = lens; c.dof.use_dof = True; c.dof.aperture_fstop = fstop
    c.clip_start = 0.01; o = bpy.data.objects.new(name, c); sc.collection.objects.link(o)
    tgt = bpy.data.objects.new(name + "_t", None); sc.collection.objects.link(tgt)
    tc = o.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
    c.dof.focus_object = tgt
    for fr, loc, look in keys:
        o.location = loc; o.keyframe_insert("location", frame=fr)
        tgt.location = look; tgt.keyframe_insert("location", frame=fr)
    for fc in list(o.animation_data.action.fcurves) + list(tgt.animation_data.action.fcurves):
        for kp in fc.keyframe_points: kp.interpolation = "BEZIER"; kp.easing = "EASE_IN_OUT"
    return o


A, B, C = SHOTS["A"], SHOTS["B"], SHOTS["C"]
def P(x, y, dz): return (x, y, zat(x, y) + dz)
camA = cam("camA", [(A[0], (6.5, -12.5, 9.0), (0.4, 0.5, 0.0)), (A[1], (3.2, -5.6, 2.2), (0.4, 0.4, 0.05))], None, 0.10, 38)
camB = cam("camB", [(B[0], P(6.4, 1.2, 1.7), (0.6, 2.4, 0.15)), (B[1], P(6.0, -1.2, 2.1), (0.4, 2.0, 0.1))], None, 0.08, 30)
camC = cam("camC", [(C[0], P(0.3, -0.6, 1.9), (2.8, 3.1, 0.3)), (C[1], P(0.9, 0.2, 1.4), (2.8, 3.1, 0.3))], None, 0.3, 40)
for nm, (s, e) in SHOTS.items():
    m = sc.timeline_markers.new(nm, frame=s); m.camera = {"A": camA, "B": camB, "C": camC}[nm]
sc.camera = camA
sc.frame_start, sc.frame_end = 1, SHOTS["C"][1]

# ---------------- render settings ----------------
r = sc.render; r.engine = "CYCLES"; r.resolution_x, r.resolution_y = 1280, 720; r.resolution_percentage = 100
sc.cycles.device = "CPU"; sc.cycles.samples = int(os.environ.get("SAMPLES", 20)); sc.cycles.use_denoising = True
sc.cycles.denoiser = "OPENIMAGEDENOISE"; sc.cycles.max_bounces = 3; sc.cycles.use_adaptive_sampling = True
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"
r.image_settings.file_format = "JPEG"; r.image_settings.quality = 94
r.use_motion_blur = False

# ---------------- label projection export ----------------
from bpy_extras.object_utils import world_to_camera_view
LAB = {"himlam": "HIM LAM", "doclap": "ĐỘC LẬP", "bankeo": "BẢN KÉO", "a1": "ĐỒI A1", "hq": "MƯỜNG THANH",
       "isabelle": "HỒNG CÚM", "dominique": "", "eliane": ""}


def export_labels():
    out = {}
    for f in range(sc.frame_start, sc.frame_end + 1):
        sc.frame_set(f); camo = sc.camera; row = {}
        for k, (x, y) in POS.items():
            p = world_to_camera_view(sc, camo, Vector((x, y, zat(x, y) + 0.2)))
            row[k] = [round(p.x, 4), round(1 - p.y, 4), round(p.z, 3)]
        out[f] = row
    json.dump(out, open(os.path.join(HERE, "labels.json"), "w"))


if ARGS and ARGS[0] == "test":
    for f in ARGS[1:]:
        sc.frame_set(int(f)); r.filepath = os.path.join(HERE, f"test_{f}.jpg"); bpy.ops.render.render(write_still=True)
elif ARGS and ARGS[0] == "render":
    export_labels()
    s, e = int(ARGS[1]), int(ARGS[2])
    sc.frame_start, sc.frame_end = s, e
    r.filepath = os.path.join(HERE, "frames", "f_####"); bpy.ops.render.render(animation=True)
elif ARGS and ARGS[0] == "labels":
    export_labels()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "dbp_diorama.blend")) if ARGS and ARGS[0] == "save" else None
