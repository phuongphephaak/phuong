"""Sa bàn 3D Điện Biên Phủ v3 – học từ Verdun 3D: nỉ cỏ sợi mịn, đường sỏi trắng, vùng đỏ/xanh,
quân cờ vát cạnh, cây búm, nhà gỗ, tilt-shift.  Quân ta = XANH, Pháp = ĐỎ.
blender -b -P scene3.py -- [test F.. | render s e | labels]"""
import bpy, math, json, os, sys
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from dbp_common import *

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SHOTS = {"A": (1, 270), "B": (271, 450), "C": (451, 630)}
OUT = os.environ.get("OUT", "frames3")
rng = np.random.default_rng(7)

xs, ys, XX, YY, Z, Dv, _, _, _ = terrain(560, 635, np.float64)
FF = french_field(XX, YY, 0)


def zat(x, y):
    i = np.clip((y - Y0) / (Y1 - Y0) * (len(ys) - 1), 0, len(ys) - 1); j = np.clip((x - X0) / (X1 - X0) * (len(xs) - 1), 0, len(xs) - 1)
    i0, j0 = int(i), int(j); i1, j1 = min(i0 + 1, len(ys) - 1), min(j0 + 1, len(xs) - 1); fi, fj = i - i0, j - j0
    return float(Z[i0, j0] * (1 - fi) * (1 - fj) + Z[i0, j1] * (1 - fi) * fj + Z[i1, j0] * fi * (1 - fj) + Z[i1, j1] * fi * fj)


def ffat(x, y):
    return max(ZR[k] - math.hypot(x - px, y - py) for k, (px, py) in POS.items())


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.fps = 30


# ------------------------------------------------------------------ node helpers
class NB:
    def __init__(self, nt): self.nt = nt; self.N = nt.nodes; self.L = nt.links

    def node(self, t, **kw):
        n = self.N.new(t)
        for k, v in kw.items(): setattr(n, k, v)
        return n

    def link(self, a, b): self.L.new(a, b)

    def math(self, op, a, b=None, clamp=False):
        n = self.N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        for i, v in enumerate([a, b]):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: self.L.new(v, n.inputs[i])
        return n.outputs[0]

    def smooth(self, v, lo, hi):
        n = self.N.new("ShaderNodeMapRange"); n.interpolation_type = "SMOOTHSTEP"
        self.L.new(v, n.inputs[0]); n.inputs[1].default_value = lo; n.inputs[2].default_value = hi
        return n.outputs[0]

    def mix(self, fac, a, b, blend="MIX"):
        n = self.N.new("ShaderNodeMixRGB"); n.blend_type = blend
        for i, v in enumerate([fac, a, b]):
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            elif isinstance(v, tuple): n.inputs[i].default_value = (*v, 1) if len(v) == 3 else v
            else: self.L.new(v, n.inputs[i])
        return n.outputs[0]

    def noise(self, vec, scale, detail=4, rough=0.55, out="Fac"):
        n = self.N.new("ShaderNodeTexNoise"); self.L.new(vec, n.inputs["Vector"])
        n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail; n.inputs["Roughness"].default_value = rough
        return n.outputs[out]

    def voronoi(self, vec, scale, out="Distance", rand=1.0):
        n = self.N.new("ShaderNodeTexVoronoi"); self.L.new(vec, n.inputs["Vector"]); n.inputs["Scale"].default_value = scale
        n.inputs["Randomness"].default_value = rand
        return n.outputs[out]


def srgb(c): return tuple(x ** 2.2 for x in c)


# ------------------------------------------------------------------ terrain mesh + vật liệu nỉ
h_, w_ = Z.shape
V = np.c_[XX.ravel(), YY.ravel(), Z.ravel()]
idx = np.arange(h_ * w_).reshape(h_, w_)
Fc = np.c_[idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()]
me = bpy.data.meshes.new("terrain"); me.vertices.add(len(V)); me.vertices.foreach_set("co", V.astype(np.float32).ravel())
me.loops.add(Fc.size); me.loops.foreach_set("vertex_index", Fc.ravel().astype(np.int32))
me.polygons.add(len(Fc)); me.polygons.foreach_set("loop_start", (np.arange(len(Fc)) * 4).astype(np.int32))
me.update(); me.validate()
me.shade_smooth() if hasattr(me, "shade_smooth") else None
uv = me.uv_layers.new(name="UV")
loops = np.zeros(len(me.loops), np.int32); me.loops.foreach_get("vertex_index", loops)
uvs = np.c_[(V[loops, 0] - X0) / (X1 - X0), (V[loops, 1] - Y0) / (Y1 - Y0)].astype(np.float32)
uv.data.foreach_set("uv", uvs.ravel())

tm = bpy.data.materials.new("terrain"); tm.use_nodes = True; nb = NB(tm.node_tree)
bsdf = nb.N["Principled BSDF"]
tc = nb.node("ShaderNodeTexCoord"); obj_co = tc.outputs["Object"]
img_c = bpy.data.images.load(os.path.join(HERE, "tex3_col.png"))
img_m = bpy.data.images.load(os.path.join(HERE, "tex3_mask.png")); img_m.colorspace_settings.name = "Non-Color"
tcol = nb.node("ShaderNodeTexImage", image=img_c, interpolation="Linear")
tmsk = nb.node("ShaderNodeTexImage", image=img_m, interpolation="Linear")
uvn = nb.node("ShaderNodeUVMap", uv_map="UV"); nb.link(uvn.outputs[0], tcol.inputs[0]); nb.link(uvn.outputs[0], tmsk.inputs[0])
sep = nb.node("ShaderNodeSeparateColor"); nb.link(tmsk.outputs["Color"], sep.inputs[0])
mR, mG, mB = sep.outputs[0], sep.outputs[1], sep.outputs[2]
# nhiễu: mảng (n1), hạt nỉ (n2), sợi (v1/v2 màu ngẫu nhiên từng sợi), sỏi (vg)
n1 = nb.noise(obj_co, 9, 3)
n2 = nb.noise(obj_co, 160, 3)
n3 = nb.noise(obj_co, 55, 4)
def cell(vec, S, out="Value"):
    vm = nb.node("ShaderNodeVectorMath", operation="SCALE"); nb.link(vec, vm.inputs[0]); vm.inputs["Scale"].default_value = S
    fl = nb.node("ShaderNodeVectorMath", operation="FLOOR"); nb.link(vm.outputs[0], fl.inputs[0])
    wn = nb.node("ShaderNodeTexWhiteNoise", noise_dimensions="3D"); nb.link(fl.outputs[0], wn.inputs["Vector"])
    return wn.outputs[out]


# xoay nhẹ toạ độ để ô sợi không thẳng hàng
rot = nb.node("ShaderNodeVectorRotate", rotation_type="Z_AXIS"); nb.link(obj_co, rot.inputs["Vector"]); rot.inputs["Angle"].default_value = 0.37
rco = rot.outputs[0]
fib = cell(rco, 650)                 # sợi nỉ (2-3 px khi cận cảnh)
v2 = cell(obj_co, 260, "Color")      # đốm màu lấm tấm
fib2 = cell(obj_co, 180)
vg = cell(rco, 420)                  # hạt sỏi
v1d = fib
# màu nỉ = texture × biến thiên sợi (mỗi sợi sáng/tối khác nhau, ánh màu nhẹ)
fibmul = nb.math("ADD", nb.math("MULTIPLY", fib, 0.7), 0.66)
c0 = nb.mix(1.0, tcol.outputs["Color"], nb.math("ADD", nb.math("MULTIPLY", n2, 0.5), 0.78), "MULTIPLY")
c0 = nb.mix(1.0, c0, nb.math("ADD", nb.math("MULTIPLY", n3, 0.35), 0.85), "MULTIPLY")
c1 = nb.mix(1.0, c0, fibmul, "MULTIPLY")
c1 = nb.mix(0.22, c1, v2, "OVERLAY")
# đường sỏi trắng: lõi đặc + mép rắc muối lởm chởm
jit = nb.math("SUBTRACT", nb.math("ADD", nb.math("MULTIPLY", n3, 0.25), nb.math("MULTIPLY", fib2, 0.22)), 0.235)
road_core = nb.smooth(nb.math("ADD", mR, jit), 0.74, 0.79)
road_salt = nb.math("MULTIPLY", nb.smooth(nb.math("ADD", mR, jit), 0.30, 0.80), nb.smooth(fib, 0.50, 0.58))
road = nb.math("MAXIMUM", road_core, road_salt)
gravel = nb.mix(nb.smooth(vg, 0.0, 0.5), srgb((0.55, 0.55, 0.53)), srgb((0.93, 0.92, 0.89)))
gravel = nb.mix(1.0, gravel, nb.math("ADD", nb.math("MULTIPLY", fib, 0.25), 0.85), "MULTIPLY")
c2 = nb.mix(road, c1, gravel)
# sông: bờ đá xám trắng, lòng nước đen bóng
jg = nb.math("SUBTRACT", nb.math("MULTIPLY", n3, 0.12), 0.06)
bank = nb.smooth(nb.math("ADD", mG, jg), 0.50, 0.55)
bank_salt = nb.math("MULTIPLY", nb.smooth(nb.math("ADD", mG, jg), 0.40, 0.55), nb.smooth(fib, 0.5, 0.6))
bankm = nb.math("MAXIMUM", bank, bank_salt)
water = nb.smooth(nb.math("ADD", mG, jg), 0.66, 0.70)
c3 = nb.mix(bankm, c2, nb.mix(nb.smooth(vg, 0.0, 0.6), srgb((0.42, 0.42, 0.42)), srgb((0.80, 0.80, 0.78))))
c3 = nb.mix(water, c3, nb.mix(nb.smooth(n2, 0.3, 0.7), srgb((0.06, 0.065, 0.07)), srgb((0.14, 0.15, 0.16))))
# nét đậm: tiền tuyến + giao thông hào
jl = nb.math("SUBTRACT", nb.math("MULTIPLY", n2, 0.06), 0.03)
line = nb.smooth(nb.math("ADD", mB, jl), 0.86, 0.90)
c4 = nb.mix(nb.math("MULTIPLY", line, 0.92), c3, srgb((0.05, 0.045, 0.04)))
frost = nb.math("MULTIPLY", nb.smooth(fib, 0.90, 0.93), nb.math("SUBTRACT", 1, nb.math("MAXIMUM", water, line)))
c4 = nb.mix(nb.math("MULTIPLY", frost, 0.45), c4, srgb((0.95, 0.94, 0.90)))
nb.link(c4, bsdf.inputs["Base Color"])
rough = nb.math("SUBTRACT", 0.93, nb.math("MULTIPLY", water, 0.45))
nb.link(rough, bsdf.inputs["Roughness"])
# bump: sợi nỉ + sỏi nổi + nước lõm + hào lõm
hgt = nb.math("ADD", nb.math("MULTIPLY", v1d, 0.6), nb.math("MULTIPLY", n2, 0.5))
hgt = nb.math("ADD", hgt, nb.math("MULTIPLY", nb.math("MULTIPLY", road, nb.math("SUBTRACT", 1, vg)), 1.2))
hgt = nb.math("SUBTRACT", hgt, nb.math("MULTIPLY", water, 1.5))
hgt = nb.math("SUBTRACT", hgt, nb.math("MULTIPLY", line, 1.0))
bump = nb.node("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.45; bump.inputs["Distance"].default_value = 0.002
nb.link(hgt, bump.inputs["Height"]); nb.link(bump.outputs["Normal"], bsdf.inputs["Normal"])
me.materials.append(tm)
ter = bpy.data.objects.new("terrain", me); sc.collection.objects.link(ter)
for p in me.polygons: p.use_smooth = True

# khung sa bàn: viền da đen
ring = list(idx[0, :]) + list(idx[:, -1]) + list(idx[-1, ::-1]) + list(idx[::-1, 0])
sv = [tuple(V[i]) for i in ring] + [(V[i][0], V[i][1], -0.3) for i in ring]
n = len(ring); sk = bpy.data.meshes.new("skirt"); sk.from_pydata(sv, [], [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)])


def mat(name, col, rough=0.6, metal=0.0, emis=None, estr=0.0, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*srgb(col), 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if coat: b.inputs["Coat Weight"].default_value = coat
    if emis:
        b.inputs["Emission Color"].default_value = (*emis, 1); b.inputs["Emission Strength"].default_value = estr
    return m


sk.materials.append(mat("skirt", (0.06, 0.055, 0.05), 0.55)); sco = bpy.data.objects.new("skirt", sk); sc.collection.objects.link(sco)
bpy.ops.mesh.primitive_cube_add(size=1, location=((X0 + X1) / 2, (Y0 + Y1) / 2, -0.33))
tbl = bpy.context.object; tbl.scale = (X1 - X0 + 1.2, Y1 - Y0 + 1.2, 0.1)
tbl.data.materials.append(mat("leather", (0.05, 0.045, 0.04), 0.45))
bv = tbl.modifiers.new("b", "BEVEL"); bv.width = 0.15; bv.segments = 4


# ------------------------------------------------------------------ meshes vát cạnh (dùng chung)
def mk(kind, bev=0.0, segs=2, **kw):
    getattr(bpy.ops.mesh, f"primitive_{kind}_add")(**kw); o = bpy.context.object
    if bev:
        b = o.modifiers.new("b", "BEVEL"); b.width = bev; b.segments = segs; b.limit_method = "ANGLE"
        bpy.ops.object.modifier_apply(modifier="b")
    m = o.data
    for p in m.polygons: p.use_smooth = True
    bpy.data.objects.remove(o); return m


def obj(name, mesh, m, loc, scale=(1, 1, 1), rot=(0, 0, 0)):
    o = bpy.data.objects.new(name, mesh); sc.collection.objects.link(o)
    o.location = loc; o.scale = scale; o.rotation_euler = rot
    if len(mesh.materials) == 0: mesh.materials.append(None)
    o.material_slots[0].link = "OBJECT"; o.material_slots[0].material = m
    return o


def pop(o, f, dur=6):
    s = tuple(o.scale); o.scale = (0, 0, 0); o.keyframe_insert("scale", frame=f)
    o.scale = s; o.keyframe_insert("scale", frame=f + dur)


hex_me = mk("cylinder", 0.004, 3, vertices=6, radius=0.06, depth=0.022)
disc_me = mk("cylinder", 0.0025, 3, vertices=32, radius=0.022, depth=0.009)
bdisc_me = mk("cylinder", 0.004, 3, vertices=40, radius=0.075, depth=0.02)
bunk_me = mk("cube", 0.006, 3, size=1)
rub_me = mk("cylinder", 0.003, 2, vertices=6, radius=0.02, depth=0.012)
cyl_me = mk("cylinder", 0, vertices=16, radius=1, depth=1)
sph_me = mk("ico_sphere", 0, subdivisions=3, radius=1)

RED = mat("red", (0.80, 0.10, 0.09), 0.38, coat=0.3)
REDD = mat("redd", (0.55, 0.07, 0.06), 0.45)
BLUE = mat("blue", (0.20, 0.42, 0.86), 0.38, coat=0.3)
CONC = mat("conc", (0.84, 0.82, 0.76), 0.55)
CONCB = mat("concb", (0.66, 0.74, 0.86), 0.5)
METAL = mat("metal", (0.30, 0.32, 0.30), 0.4, 0.6)
DARK = mat("dark", (0.04, 0.04, 0.04), 0.9)
RUB = mat("rubble", (0.26, 0.26, 0.27), 0.85)
STAR = mat("star", (1.0, 0.82, 0.10), 0.35, emis=(1, 0.8, 0.1), estr=0.4)

# ------------------------------------------------------------------ cây búm (rừng trên đồi)
trees = []
TRUNK = mat("trunk", (0.25, 0.18, 0.12), 0.9); FOLPH = mat("folph", (0.45, 0.42, 0.22), 0.85)
for v in range(4):
    tv, tf = [], []
    getattr(bpy.ops.mesh, "primitive_cylinder_add")(vertices=6, radius=0.0022, depth=0.05, location=(0, 0, 0.025))
    trunk = bpy.context.object
    parts = [trunk]
    r_ = np.random.default_rng(100 + v)
    for j in range(int(r_.integers(4, 7))):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r_.uniform(0.012, 0.02),
                                              location=(r_.normal(0, 0.009), r_.normal(0, 0.009), 0.045 + r_.uniform(0, 0.025)))
        s_ = bpy.context.object; tex = bpy.data.textures.new("tn", "VORONOI"); tex.noise_scale = 0.012
        dm = s_.modifiers.new("d", "DISPLACE"); dm.texture = tex; dm.strength = 0.006
        bpy.ops.object.modifier_apply(modifier="d"); parts.append(s_)
    trunk.data.materials.append(TRUNK)
    for p in parts[1:]: p.data.materials.append(FOLPH)
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts: p.select_set(True)
    bpy.context.view_layer.objects.active = parts[-1]; bpy.ops.object.join()
    t = bpy.context.object; trees.append(t.data); bpy.data.objects.remove(t)
FOL = []
for c in [(0.42, 0.40, 0.20), (0.50, 0.44, 0.24), (0.34, 0.38, 0.18), (0.58, 0.46, 0.26)]:
    m = mat("fol", c, 0.85)
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Subsurface Weight"].default_value = 0.0
    FOL.append(m)
for me_ in trees:
    print('treemats', [m.name for m in me_.materials])
cnt = 0
for (x, y) in rng.uniform([X0 + .1, Y0 + .1], [X1 - .1, Y1 - .1], (60000, 2)):
    z = zat(x, y)
    if z < 0.10 or ffat(x, y) > -0.1: continue
    if rng.random() > min(0.32, (z - 0.1) * 0.5): continue
    if min(math.hypot(x - vx, y - vy) for vx, vy in VN_POS) < 0.4: continue
    for c_ in range(int(rng.integers(1, 4))):
        cx, cy = x + rng.normal(0, 0.04), y + rng.normal(0, 0.04)
        o = bpy.data.objects.new("tree", trees[int(rng.integers(0, 4))]); sc.collection.objects.link(o)
        o.location = (cx, cy, zat(cx, cy) - 0.003); sz = rng.uniform(0.75, 1.35); o.scale = (sz, sz, sz * rng.uniform(0.9, 1.2))
        o.rotation_euler = (rng.normal(0, 0.06), rng.normal(0, 0.06), rng.uniform(0, 6.28))
        fm_ = FOL[int(rng.integers(0, 4))]
        for sl in o.material_slots:
            if sl.material and sl.material.name.startswith("folph"):
                sl.link = "OBJECT"; sl.material = fm_
        cnt += 1
print("trees", cnt)

# ------------------------------------------------------------------ nhà gỗ (khối be, mái dốc) – gộp 1 mesh
hv, hf, hc = [], [], []
def house(x, y, a, w, l, hgt):
    z = zat(x, y); ca, sa = math.cos(a), math.sin(a)
    P = lambda u, v, h: (x + u * ca - v * sa, y + u * sa + v * ca, z + h)
    b0 = len(hv)
    for (u, v) in [(-l, -w), (l, -w), (l, w), (-l, w)]: hv.append(P(u, v, -0.004))
    for (u, v) in [(-l, -w), (l, -w), (l, w), (-l, w)]: hv.append(P(u, v, hgt))
    hv.append(P(-l, 0, hgt * 1.6)); hv.append(P(l, 0, hgt * 1.6))
    hf.extend([(b0, b0 + 1, b0 + 5, b0 + 4), (b0 + 2, b0 + 3, b0 + 7, b0 + 6),
               (b0 + 1, b0 + 2, b0 + 6, b0 + 9, b0 + 5), (b0 + 3, b0 + 0, b0 + 4, b0 + 8, b0 + 7),
               (b0 + 4, b0 + 5, b0 + 9, b0 + 8), (b0 + 6, b0 + 7, b0 + 8, b0 + 9)])
    col = np.array([0.80, 0.62, 0.42]) * rng.uniform(0.8, 1.1); hc.extend([col] * 10)
for (vx, vy) in VILLAGES:
    for j in range(int(rng.integers(6, 12))):
        x, y = vx + rng.normal(0, 0.07), vy + rng.normal(0, 0.07)
        if abs(x - river_x(y)) < 0.09: continue
        house(x, y, rng.uniform(0, 3.14), 0.009, rng.uniform(0.012, 0.02), rng.uniform(0.008, 0.012))
hm = bpy.data.meshes.new("houses"); hm.from_pydata(hv, [], hf); hm.update()
ca_ = hm.color_attributes.new("col", "FLOAT_COLOR", "POINT")
ca_.data.foreach_set("color", np.c_[np.array(hc) ** 2.2, np.ones(len(hc))].astype(np.float32).ravel())
hmm = bpy.data.materials.new("house"); hmm.use_nodes = True
vc = hmm.node_tree.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "col"
hmm.node_tree.links.new(vc.outputs["Color"], hmm.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
hmm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.75
hm.materials.append(hmm); ho = bpy.data.objects.new("houses", hm); sc.collection.objects.link(ho)
bvh = ho.modifiers.new("b", "BEVEL"); bvh.width = 0.0012; bvh.segments = 1

# ------------------------------------------------------------------ cờ
pole = mat("pole", (0.85, 0.85, 0.85), 0.4)


def flag_mat(kind):
    m = bpy.data.materials.new("flag_" + kind); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes["Principled BSDF"]; t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(os.path.join(HERE, f"flag_{kind}.png"))
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"]); nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 0.15; return m


FR, VNF = flag_mat("fr"), flag_mat("vn")


def flag(x, y, z, fm, s=1.0, seed=0.0):
    obj("pole", cyl_me, pole, (x, y, z + 0.035 * s), (0.0018 * s, 0.0018 * s, 0.07 * s))
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x + 0.017 * s, y, z + 0.058 * s))
    f = bpy.context.object; f.scale = (0.034 * s, 0.023 * s, 1); f.rotation_euler = (math.pi / 2, 0, 0.6)
    bpy.ops.object.transform_apply(scale=True, rotation=False); f.data.materials.append(fm)
    f.modifiers.new("s", "SUBSURF").levels = 2
    w = f.modifiers.new("w", "WAVE"); w.height = 0.002 * s; w.width = 0.02 * s; w.speed = 0.01; w.use_normal = False; w.time_offset = seed


# ------------------------------------------------------------------ Pháp (đỏ): lô cốt bê tông trên đế lục giác đỏ
def bunker(x, y, big=1.0, fl=False):
    z = zat(x, y)
    obj("rb", hex_me, RED, (x, y, z + 0.009 * big), (big, big, big), (0, 0, rng.uniform(0, 1)))
    a = rng.uniform(0, 3.14)
    obj("bk", bunk_me, CONC, (x, y, z + 0.03 * big), (0.06 * big, 0.045 * big, 0.026 * big), (0, 0, a))
    obj("sl", bunk_me, DARK, (x + 0.03 * big * math.cos(a), y + 0.03 * big * math.sin(a), z + 0.033 * big),
        (0.004 * big, 0.03 * big, 0.006 * big), (0, 0, a))
    if fl: flag(x - 0.015 * big, y + 0.01 * big, z + 0.042 * big, FR, 1.4 * big, x)


for k, (px, py) in POS.items():
    big = 1.35 if k in ("hq", "himlam", "doclap", "isabelle") else 1.05
    bunker(px, py, big, True)
    for j in range(4):
        a = j * 1.57 + px * 3; r = 0.17 + 0.03 * (j % 2)
        bunker(px + r * math.cos(a), py + r * math.sin(a), 0.6)
    # bộ binh Pháp: đĩa đỏ dọc giao thông hào
    for j in range(16):
        a = j / 16 * 2 * math.pi; rr = 0.3175 + 0.015 * math.sin(a * 7 + px)
        x_, y_ = px + rr * math.cos(a), py + rr * math.sin(a)
        obj("rd", disc_me, RED, (x_, y_, zat(x_, y_) + 0.005))
    # đá vụn xám (hố bom) quanh cứ điểm
    for j in range(16):
        a = rng.uniform(0, 6.28); d = rng.uniform(0.08, 0.5)
        x_, y_ = px + d * math.cos(a), py + d * math.sin(a); s_ = rng.uniform(0.6, 1.3)
        obj("rub", rub_me, RUB, (x_, y_, zat(x_, y_) + 0.003), (s_, s_ * rng.uniform(0.7, 1), s_), (rng.normal(0, .15), rng.normal(0, .15), rng.uniform(0, 6)))


# ------------------------------------------------------------------ ta (xanh): pháo trên đế tròn xanh, sao vàng
def star_mesh(R=1.0, r=0.42, h=0.25):
    v = []
    for j in range(10):
        rr = R if j % 2 == 0 else r; a = math.pi / 2 + j * math.pi / 5
        v.append((rr * math.cos(a), rr * math.sin(a), 0))
    v += [(x, y, h) for (x, y, _) in v]
    f = [tuple(range(9, -1, -1)), tuple(range(10, 20))] + [(j, (j + 1) % 10, 10 + (j + 1) % 10, 10 + j) for j in range(10)]
    m = bpy.data.meshes.new("star"); m.from_pydata(v, [], f); m.update(); return m


star_me = star_mesh()


def gun(x, y, a):
    G = 1.0; z = zat(x, y); ca, sa = math.cos(a), math.sin(a)
    R = lambda u, v: (x + G * (u * ca - v * sa), y + G * (u * sa + v * ca))
    obj("gb", bdisc_me, BLUE, (x, y, z + 0.008))
    obj("gs", bunk_me, METAL, (*R(0.0, 0), z + 0.03), (0.07, 0.04, 0.018), (0, 0, a))
    obj("gsh", bunk_me, METAL, (*R(0.03, 0), z + 0.042), (0.006, 0.06, 0.03), (0, 0, a))
    for v in (-0.028, 0.028):
        obj("gw", cyl_me, DARK, (*R(0.01, v), z + 0.035), (0.016, 0.016, 0.006), (math.pi / 2, 0, a))
    el = math.radians(25)
    bx, by = R(0.07, 0)
    obj("gn", cyl_me, METAL, (bx, by, z + 0.05), (0.005, 0.005, 0.09), (0, math.pi / 2 - el, a))
    tip = R(0.07 + 0.045 * math.cos(el), 0)
    return (tip[0], tip[1], z + 0.05 + 0.045 * math.sin(el))


GUNS = []
for i, (px, py) in enumerate(VN_POS):
    a = math.atan2(-py, -px); tx, ty = -math.sin(a), math.cos(a)
    for j in (-1, 0, 1):
        GUNS.append(gun(px + j * 0.19 * tx - 0.03 * abs(j) * math.cos(a), py + j * 0.19 * ty - 0.03 * abs(j) * math.sin(a), a))
    bx, by = px - 0.17 * math.cos(a), py - 0.17 * math.sin(a); z = zat(bx, by)
    obj("hq", hex_me, BLUE, (bx, by, z + 0.01), (0.9, 0.9, 1.0))
    obj("st", star_me, STAR, (bx, by, z + 0.021), (0.032, 0.032, 0.03), (0, 0, a))
    flag(bx + 0.04, by + 0.03, z + 0.02, VNF, 1.5, i)

# vòng vây: đĩa xanh hiện dần 320→440 (bám mép vùng đỏ, hơi lùi ra)
RP = []
for k in ["himlam", "doclap", "bankeo", "hq", "isabelle"]:
    px, py = POS[k]; R = ZR[k] + (0.75 if k == "hq" else 0.28); nr = int(R * 34)
    for t_ in np.linspace(0, 2 * math.pi, nr, endpoint=False):
        x, y = px + R * math.cos(t_), py + R * math.sin(t_)
        if ffat(x, y) < -0.12: RP.append((x, y, t_))
RP.sort(key=lambda p: math.atan2(p[1] - 1, p[0] - 0.4))
for i, (x, y, _) in enumerate(RP):
    o = obj("ring", disc_me, BLUE, (x, y, zat(x, y) + 0.005), (1.3, 1.3, 1.2)); pop(o, 320 + int(i * 120 / len(RP)), 5)

# bộ binh ta: hàng đĩa xanh tiến vào Him Lam 495→615
HL = POS["himlam"]
for li, (sx, sy, mx, my) in enumerate([(4.2, 3.9, 3.6, 3.5), (3.9, 1.8, 3.4, 2.2), (3.1, 4.9, 2.9, 4.0), (1.5, 3.9, 1.9, 3.5)]):
    tt = np.linspace(0, 1, 160)
    px_ = (1 - tt) ** 2 * sx + 2 * (1 - tt) * tt * mx + tt ** 2 * HL[0]; py_ = (1 - tt) ** 2 * sy + 2 * (1 - tt) * tt * my + tt ** 2 * HL[1]
    L = np.r_[0, np.cumsum(np.hypot(np.diff(px_), np.diff(py_)))]
    stop = L[-1] - 0.24; k = 0; d_ = 0.0
    while d_ < stop:
        x = np.interp(d_, L, px_); y = np.interp(d_, L, py_)
        o = obj("inf", disc_me, BLUE, (x, y, zat(x, y) + 0.005), (1.15, 1.15, 1.1)); pop(o, 495 + li * 6 + k * 3, 4)
        k += 1; d_ += 0.058

# ------------------------------------------------------------------ nổ: chớp + đất văng + bụi + hố
FLASH = mat("flash", (1, 0.6, 0.3), 0.5, emis=(1.0, 0.45, 0.12), estr=25)
DIRT = mat("dirt", (0.20, 0.15, 0.11), 0.95)
DIRT2 = mat("dirt2", (0.36, 0.30, 0.24), 0.95)
def soft_mat(name, col, edge=1.6):
    """khói mềm: rìa trong suốt theo góc nhìn"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes
    b = N["Principled BSDF"]; b.inputs["Base Color"].default_value = (*srgb(col), 1); b.inputs["Roughness"].default_value = 1
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
    mr = N.new("ShaderNodeMapRange"); nt.links.new(lw.outputs["Facing"], mr.inputs[0]); mr.inputs[1].default_value = 0.15; mr.inputs[2].default_value = 0.85
    mr.inputs[3].default_value = 1.0; mr.inputs[4].default_value = 0.0
    tr = N.new("ShaderNodeBsdfTransparent"); mx = N.new("ShaderNodeMixShader")
    nt.links.new(mr.outputs[0], mx.inputs[0]); nt.links.new(b.outputs[0], mx.inputs[2]); nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
    return m


DUST = soft_mat("dust", (0.52, 0.47, 0.41))
CRATER = mat("crater", (0.05, 0.045, 0.04), 0.95)
RIM = mat("rim", (0.30, 0.25, 0.20), 0.95)
chunk_me = mk("ico_sphere", 0, subdivisions=1, radius=1)
puff_me = mk("ico_sphere", 0, subdivisions=4, radius=1)
torus_me = mk("torus", 0, major_radius=1, minor_radius=0.25, major_segments=24, minor_segments=8)
clouds = bpy.data.textures.new("clouds", "CLOUDS"); clouds.noise_scale = 0.35


def burst(x, y, f, big=1.0, light=True):
    z = zat(x, y)
    fl = obj("fl", puff_me, FLASH, (x, y, z + 0.012), (0, 0, 0))
    for fr, s in [(f - 1, 0), (f, 0.02 * big), (f + 2, 0.032 * big), (f + 4, 0)]:
        fl.scale = (s, s, s * 0.8); fl.keyframe_insert("scale", frame=fr)
    if light:
        Ld = bpy.data.lights.new("L", "POINT"); Ld.color = (1, 0.6, 0.25); Ld.shadow_soft_size = 0.02
        lo = bpy.data.objects.new("L", Ld); sc.collection.objects.link(lo); lo.location = (x, y, z + 0.07)
        for fr, e in [(f - 1, 0), (f, 18 * big), (f + 5, 0)]:
            Ld.energy = e; Ld.keyframe_insert("energy", frame=fr)
    cr = obj("cr", bdisc_me, CRATER, (x, y, z - 0.006), (0.5 * big, 0.5 * big, 0.5)); pop(cr, f, 2)
    rim = obj("rim", torus_me, RIM, (x, y, z + 0.002), (0.042 * big, 0.042 * big, 0.01 * big)); pop(rim, f, 3)
    for i in range(30):
        ang = rng.uniform(0, 2 * math.pi); dist = rng.uniform(0.03, 0.2) * big; hmax = rng.uniform(0.05, 0.22) * big
        T = int(rng.integers(14, 26)); sz = rng.uniform(0.004, 0.011) * big
        ex, ey = x + dist * math.cos(ang), y + dist * math.sin(ang); ez = zat(ex, ey) + sz * 0.5
        c = obj("ch", chunk_me, DIRT if i % 3 else DIRT2, (x, y, z), (0, 0, 0))
        c.keyframe_insert("scale", frame=f - 1); c.scale = (sz, sz * 0.8, sz * 0.7); c.keyframe_insert("scale", frame=f)
        for s in range(7):
            u = s / 6; fr = f + round(u * T)
            c.location = (x + (ex - x) * u, y + (ey - y) * u, z + (ez - z) * u + 4 * hmax * u * (1 - u))
            c.rotation_euler = (u * rng.uniform(3, 9), u * rng.uniform(3, 9), 0)
            c.keyframe_insert("location", frame=fr); c.keyframe_insert("rotation_euler", frame=fr)
        for fc in c.animation_data.action.fcurves:
            if fc.data_path == "location":
                for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
        c.keyframe_insert("scale", frame=f + T + 70); c.scale = (0, 0, 0); c.keyframe_insert("scale", frame=f + T + 120)
    for j in range(3):
        p = obj("pf", puff_me, DUST, (x + rng.normal(0, 0.015 * big), y + rng.normal(0, 0.015 * big), z), (0, 0, 0))
        dm = p.modifiers.new("d", "DISPLACE"); dm.texture = clouds; dm.strength = 0.22; dm.mid_level = 0.5
        p.keyframe_insert("scale", frame=f + j); p.keyframe_insert("location", frame=f + j)
        s = rng.uniform(0.010, 0.018) * big
        p.scale = (s, s, s * 1.1); p.location.z = z + 0.018 * big * (j + 1); p.keyframe_insert("scale", frame=f + 10 + 4 * j)
        p.keyframe_insert("location", frame=f + 10 + 4 * j)
        p.scale = (s * 2.2, s * 2.2, s * 1.7); p.location.z = z + 0.045 * big * (j + 1); p.keyframe_insert("scale", frame=f + 75)
        p.keyframe_insert("location", frame=f + 75)
        p.scale = (0, 0, 0); p.keyframe_insert("scale", frame=f + 140)


hx, hy = HL
for i in range(22):
    burst(hx + rng.normal(0, 0.15), hy + rng.normal(0, 0.15), 468 + i * 6 + int(rng.integers(0, 5)), rng.uniform(0.9, 1.3), i % 2 == 0)
for k in ["dominique", "eliane", "a1", "bankeo", "doclap", "huguette", "hq"]:
    for i in range(2):
        burst(POS[k][0] + rng.normal(0, 0.12), POS[k][1] + rng.normal(0, 0.12), 462 + 60 * i + int(rng.integers(0, 40)), 1.0, False)
GUNSMOKE = soft_mat("gunsmoke", (0.80, 0.78, 0.74))
for (gx, gy, gz) in GUNS:
    for i in range(3):
        f = 455 + int(rng.integers(0, 160))
        fl = obj("mf", puff_me, FLASH, (gx, gy, gz), (0, 0, 0))
        for fr, s in [(f - 1, 0), (f, 0.018), (f + 2, 0)]:
            fl.scale = (s, s, s); fl.keyframe_insert("scale", frame=fr)
        p = obj("ms", puff_me, GUNSMOKE, (gx, gy, gz), (0, 0, 0))
        p.modifiers.new("d", "DISPLACE").texture = clouds; p.modifiers["d"].strength = 0.3
        p.keyframe_insert("scale", frame=f); p.keyframe_insert("location", frame=f)
        p.scale = (0.025, 0.025, 0.025); p.location.z = gz + 0.035; p.keyframe_insert("scale", frame=f + 12); p.keyframe_insert("location", frame=f + 12)
        p.scale = (0, 0, 0); p.location.z = gz + 0.09; p.keyframe_insert("scale", frame=f + 60); p.keyframe_insert("location", frame=f + 60)

# ------------------------------------------------------------------ ánh sáng: nắng xiên ấm + trời mềm
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 4.2; sun.color = (1.0, 0.94, 0.86); sun.angle = math.radians(6)
so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(52), 0, math.radians(-135))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; nt = w.node_tree
bgL = nt.nodes["Background"]; bgL.inputs["Color"].default_value = (0.62, 0.66, 0.72, 1); bgL.inputs["Strength"].default_value = 0.75
bgC = nt.nodes.new("ShaderNodeBackground"); bgC.inputs["Color"].default_value = (0.02, 0.02, 0.022, 1)
lp = nt.nodes.new("ShaderNodeLightPath"); mx = nt.nodes.new("ShaderNodeMixShader")
nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0]); nt.links.new(bgL.outputs[0], mx.inputs[1]); nt.links.new(bgC.outputs[0], mx.inputs[2])
nt.links.new(mx.outputs[0], nt.nodes["World Output"].inputs["Surface"])


# ------------------------------------------------------------------ máy quay (tilt-shift nhẹ khi nghiêng)
def cam(name, keys, lens):
    c = bpy.data.cameras.new(name); c.lens = lens; c.dof.use_dof = True; c.clip_start = 0.01
    o = bpy.data.objects.new(name, c); sc.collection.objects.link(o)
    tgt = bpy.data.objects.new(name + "_t", None); sc.collection.objects.link(tgt)
    tc_ = o.constraints.new("TRACK_TO"); tc_.target = tgt; tc_.track_axis = "TRACK_NEGATIVE_Z"; tc_.up_axis = "UP_Y"
    c.dof.focus_object = tgt
    for (fr, loc, look, fs) in keys:
        o.location = loc; o.keyframe_insert("location", frame=fr); tgt.location = look; tgt.keyframe_insert("location", frame=fr)
        c.dof.aperture_fstop = fs; c.dof.keyframe_insert("aperture_fstop", frame=fr)
    for ac in [o.animation_data.action, tgt.animation_data.action, c.animation_data.action]:
        for fc in ac.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = "BEZIER"; kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
    return o


A, B, C = SHOTS["A"], SHOTS["B"], SHOTS["C"]
camA = cam("camA", [
    (A[0], (0.4, 0.3, 14.0), (0.4, 0.75, 0.0), 16),
    (110, (-0.2, -2.2, 8.0), (0.3, 0.6, 0.0), 8),
    (200, (-1.6, -3.2, 4.0), (0.2, 0.7, 0.05), 2.2),
    (A[1], (-1.3, -2.7, 2.7), (0.5, 0.8, 0.05), 1.4)], 30)
camB = cam("camB", [
    (B[0], (6.6, -1.6, 2.4), (4.4, 1.2, 0.45), 1.2),
    (350, (6.7, 1.6, 2.4), (4.1, 3.6, 0.45), 1.2),
    (B[1], (6.5, -5.5, 8.5), (0.5, 0.9, 0.0), 6)], 30)
orb = []
for i, fr in enumerate(np.linspace(C[0], C[1], 5).astype(int)):
    a = math.radians(-100 + 60 * i / 4); r = 1.75 - 0.3 * i / 4; h = 1.35 - 0.2 * i / 4
    orb.append((int(fr), (HL[0] + r * math.cos(a), HL[1] + r * math.sin(a), zat(*HL) + h), (HL[0], HL[1] + 0.05, zat(*HL) + 0.02), 1.0))
camC = cam("camC", orb, 35)
for nm, (s, e) in SHOTS.items():
    mk_ = sc.timeline_markers.new(nm, frame=s); mk_.camera = {"A": camA, "B": camB, "C": camC}[nm]
sc.camera = camA; sc.frame_start, sc.frame_end = 1, C[1]

r = sc.render; r.engine = "CYCLES"; r.resolution_x, r.resolution_y = 1920, 1080
r.resolution_percentage = int(os.environ.get("PCT", 100))
sc.cycles.device = "CPU"; sc.cycles.samples = int(os.environ.get("SAMPLES", 20)); sc.cycles.use_denoising = True
sc.cycles.denoiser = "OPENIMAGEDENOISE"; sc.cycles.max_bounces = 3; sc.cycles.diffuse_bounces = 2
sc.cycles.glossy_bounces = 1; sc.cycles.transparent_max_bounces = 4; sc.cycles.use_adaptive_sampling = True
sc.cycles.adaptive_threshold = 0.03
sc.cycles.texture_limit_render = "OFF"; r.use_persistent_data = True
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
r.image_settings.file_format = "JPEG"; r.image_settings.quality = 95

from bpy_extras.object_utils import world_to_camera_view


def export_labels():
    out = {}
    for f in range(1, C[1] + 1):
        sc.frame_set(f); row = {}
        for k, (x, y) in POS.items():
            p = world_to_camera_view(sc, sc.camera, Vector((x, y, zat(x, y) + 0.1)))
            row[k] = [round(p.x, 4), round(1 - p.y, 4), round(p.z, 3)]
        out[f] = row
    json.dump(out, open(os.path.join(HERE, "labels3.json"), "w"))


if ARGS and ARGS[0] == "test":
    os.makedirs(os.path.join(HERE, "t3"), exist_ok=True)
    for f in ARGS[1:]:
        sc.frame_set(int(f)); r.filepath = os.path.join(HERE, "t3", f"t_{int(f):04d}.jpg"); bpy.ops.render.render(write_still=True)
elif ARGS and ARGS[0] == "render":
    sc.frame_start, sc.frame_end = int(ARGS[1]), int(ARGS[2])
    r.filepath = os.path.join(HERE, OUT, "f_####"); bpy.ops.render.render(animation=True)
elif ARGS and ARGS[0] == "labels":
    export_labels()
