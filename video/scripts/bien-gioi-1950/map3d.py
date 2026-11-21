"""Dựng bản đồ sa bàn 3D trong Blender: địa hình thật + chất liệu đồng ruộng + cây 3D đổ bóng, chụp thẳng từ trên xuống.
blender -b -P map3d.py -- <res_x> <samples> <out.png>"""
import bpy, bmesh, math, os, sys, random
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
RX = int(argv[0]); SAMPLES = int(argv[1]); OUT = argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
MW, MH = 8192, 5120
Dc = np.load(os.path.join(HERE, "terrain_E.npy")).astype(np.float64)
GH, GW = Dc.shape
WM = 11315.0; HM = WM * MH / MW            # mét
EXAG = 1.8
Z0 = Dc.min()
rng = np.random.default_rng(3)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ---------------- địa hình ----------------
xs = np.linspace(-WM / 2, WM / 2, GW); ys = np.linspace(HM / 2, -HM / 2, GH)
X, Y = np.meshgrid(xs, ys); Z = (Dc - Z0) * EXAG
verts = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
ii = np.arange(GH * GW).reshape(GH, GW)
q = np.c_[ii[:-1, :-1].ravel(), ii[1:, :-1].ravel(), ii[1:, 1:].ravel(), ii[:-1, 1:].ravel()]
me = bpy.data.meshes.new("terrain")
me.vertices.add(len(verts)); me.vertices.foreach_set("co", verts.astype(np.float32).ravel())
me.loops.add(q.size); me.loops.foreach_set("vertex_index", q.ravel().astype(np.int32))
me.polygons.add(len(q)); me.polygons.foreach_set("loop_start", (np.arange(len(q)) * 4).astype(np.int32)); me.polygons.foreach_set("loop_total", np.full(len(q), 4, np.int32))
uv = me.uv_layers.new(name="UV")
U = (X.ravel() + WM / 2) / WM; V = (Y.ravel() + HM / 2) / HM
uvs = np.c_[U[q.ravel()], V[q.ravel()]]
uv.data.foreach_set("uv", uvs.astype(np.float32).ravel())
me.update(); me.validate()
for p in me.polygons: pass
me.shade_smooth() if hasattr(me, "shade_smooth") else None
ter = bpy.data.objects.new("terrain", me); sc.collection.objects.link(ter)
mat = bpy.data.materials.new("ground"); mat.use_nodes = True; nt = mat.node_tree
bsdf = nt.nodes["Principled BSDF"]
tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(os.path.join(HERE, "ground_tex.png")); tex.interpolation = "Linear"
nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.95
bsdf.inputs["Specular IOR Level"].default_value = 0.15
# vân bề mặt nhỏ (cỏ, đất) cho khỏi trơn
noi = nt.nodes.new("ShaderNodeTexNoise"); noi.inputs["Scale"].default_value = 900; noi.inputs["Detail"].default_value = 6
bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25; bump.inputs["Distance"].default_value = 0.5
nt.links.new(noi.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
ter.data.materials.append(mat)


def height_at(px, py):
    """px, py: toạ độ pixel bản đồ 8K -> z (m)"""
    gx = px / MW * (GW - 1); gy = py / MH * (GH - 1)
    x0 = np.clip(gx.astype(int), 0, GW - 2); y0 = np.clip(gy.astype(int), 0, GH - 2); fx = gx - x0; fy = gy - y0
    z = (Dc[y0, x0] * (1 - fx) * (1 - fy) + Dc[y0, x0 + 1] * fx * (1 - fy) + Dc[y0 + 1, x0] * (1 - fx) * fy + Dc[y0 + 1, x0 + 1] * fx * fy)
    return (z - Z0) * EXAG


def px2w(px, py):
    return px / MW * WM - WM / 2, HM / 2 - py / MH * HM


# ---------------- cây: lấy điểm theo mặt nạ rừng + hàng rào ----------------
fm = np.load(os.path.join(HERE, "forest_mask.npy")).astype(np.float32) / 255
hm = np.load(os.path.join(HERE, "hedge_mask.npy")).astype(np.float32) / 255
MPP = WM / MW


def sample(mask, n, thr):
    px = rng.uniform(0, MW - 1, n); py = rng.uniform(0, MH - 1, n)
    keep = mask[py.astype(int), px.astype(int)] > thr
    return px[keep], py[keep]


tx, ty = sample(fm, int(os.environ.get("NTREE", "2600000")), 0.5)
bx, by = sample(hm, int(os.environ.get("NBUSH", "9000000")), 0.5)
print("trees", len(tx), "bushes", len(bx), flush=True)


def make_points(name, px, py, smin, smax):
    wx, wy = px2w(px, py); wz = height_at(px, py)
    m = bpy.data.meshes.new(name); n = len(wx)
    m.vertices.add(n); m.vertices.foreach_set("co", np.c_[wx, wy, wz].astype(np.float32).ravel())
    a = m.attributes.new("tscale", "FLOAT", "POINT"); a.data.foreach_set("value", rng.uniform(smin, smax, n).astype(np.float32))
    a = m.attributes.new("tvar", "INT", "POINT"); a.data.foreach_set("value", rng.integers(0, 4, n).astype(np.int32))
    a = m.attributes.new("trot", "FLOAT", "POINT"); a.data.foreach_set("value", rng.uniform(0, 6.283, n).astype(np.float32))
    a = m.attributes.new("tcol", "FLOAT", "POINT"); a.data.foreach_set("value", rng.uniform(0, 1, n).astype(np.float32))
    o = bpy.data.objects.new(name, m); sc.collection.objects.link(o); return o


# mẫu tán cây: khối tròn lồi lõm
lib = bpy.data.collections.new("treelib"); sc.collection.children.link(lib)
tmat = bpy.data.materials.new("leaf"); tmat.use_nodes = True; tn = tmat.node_tree; tb = tn.nodes["Principled BSDF"]
at = tn.nodes.new("ShaderNodeAttribute"); at.attribute_name = "tcol"; at.attribute_type = "INSTANCER"
ramp = tn.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.035, 0.050, 0.012, 1); ramp.color_ramp.elements[1].color = (0.085, 0.100, 0.028, 1)
e = ramp.color_ramp.elements.new(0.6); e.color = (0.060, 0.072, 0.020, 1)
tn.links.new(at.outputs["Fac"], ramp.inputs["Fac"]); tn.links.new(ramp.outputs["Color"], tb.inputs["Base Color"])
tb.inputs["Roughness"].default_value = 0.85
tnoi = tn.nodes.new("ShaderNodeTexNoise"); tnoi.inputs["Scale"].default_value = 3.0
tbump = tn.nodes.new("ShaderNodeBump"); tbump.inputs["Strength"].default_value = 0.6
tn.links.new(tnoi.outputs["Fac"], tbump.inputs["Height"]); tn.links.new(tbump.outputs["Normal"], tb.inputs["Normal"])
for k in range(4):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0)
    o = bpy.context.active_object; o.name = f"tree{k}"
    r = random.Random(k)
    for v in o.data.vertices:
        f = 1 + 0.22 * math.sin(v.co.x * 5 + k) * math.cos(v.co.y * 4 - k) + r.uniform(-0.08, 0.08)
        v.co *= f; v.co.z = v.co.z * 0.75 + 0.55
    o.data.materials.append(tmat)
    for c in o.users_collection: c.objects.unlink(o)
    lib.objects.link(o)
lib.hide_render = True; bpy.context.view_layer.layer_collection.children["treelib"].exclude = True


def gn_instancer(obj):
    mod = obj.modifiers.new("inst", "NODES")
    ng = bpy.data.node_groups.new("inst_" + obj.name, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes; Lk = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    m2p = N.new("GeometryNodeMeshToPoints")
    ci = N.new("GeometryNodeCollectionInfo"); ci.inputs["Collection"].default_value = lib
    ci.inputs["Separate Children"].default_value = True; ci.inputs["Reset Children"].default_value = True
    iop = N.new("GeometryNodeInstanceOnPoints"); iop.inputs["Pick Instance"].default_value = True
    a_s = N.new("GeometryNodeInputNamedAttribute"); a_s.data_type = "FLOAT"; a_s.inputs["Name"].default_value = "tscale"
    a_v = N.new("GeometryNodeInputNamedAttribute"); a_v.data_type = "INT"; a_v.inputs["Name"].default_value = "tvar"
    a_r = N.new("GeometryNodeInputNamedAttribute"); a_r.data_type = "FLOAT"; a_r.inputs["Name"].default_value = "trot"
    cxyz = N.new("ShaderNodeCombineXYZ")
    Lk.new(a_r.outputs["Attribute"], cxyz.inputs["Z"])
    Lk.new(gi.outputs["Geometry"], m2p.inputs["Mesh"])
    Lk.new(m2p.outputs["Points"], iop.inputs["Points"])
    Lk.new(ci.outputs["Instances"], iop.inputs["Instance"])
    Lk.new(a_v.outputs["Attribute"], iop.inputs["Instance Index"])
    Lk.new(a_s.outputs["Attribute"], iop.inputs["Scale"])
    Lk.new(cxyz.outputs["Vector"], iop.inputs["Rotation"])
    Lk.new(iop.outputs["Instances"], go.inputs["Geometry"])
    mod.node_group = ng


lx, ly = sample(1 - fm, 9000, 0.5)
tx = np.r_[tx, lx]; ty = np.r_[ty, ly]
trees = make_points("trees", tx, ty, 2.6, 4.6); gn_instancer(trees)
bush = make_points("bushes", bx, by, 1.6, 2.8); gn_instancer(bush)

# ---------------- ánh sáng ----------------
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 5.0; sun.angle = math.radians(3.0); sun.color = (1.0, 0.95, 0.85)
so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so)
az, el = math.radians(300), math.radians(30)
d = (-math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), -math.sin(el))   # hướng ánh sáng (từ tây bắc)
import mathutils
so.rotation_euler = mathutils.Vector((-d[0], -d[1], -d[2])).to_track_quat("Z", "Y").to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.62, 0.75, 1); w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7

# ---------------- camera trực giao từ trên xuống ----------------
cd = bpy.data.cameras.new("cam"); cd.type = "ORTHO"; cd.ortho_scale = WM; cd.clip_start = 10; cd.clip_end = 20000
co = bpy.data.objects.new("cam", cd); sc.collection.objects.link(co); co.location = (0, 0, 6000); co.rotation_euler = (0, 0, 0)
sc.camera = co
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True; sc.cycles.denoiser = "OPENIMAGEDENOISE"
sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.02
sc.cycles.max_bounces = 3; sc.cycles.diffuse_bounces = 2
sc.cycles.use_auto_tile = False
sc.render.resolution_x = RX; sc.render.resolution_y = int(RX * MH / MW); sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "Standard"
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "16"
sc.render.filepath = OUT
if len(argv) > 3:      # vùng cắt để thử nhanh: x0 y0 x1 y1 (0..1)
    sc.render.use_border = True; sc.render.use_crop_to_border = True
    sc.render.border_min_x, sc.render.border_min_y, sc.render.border_max_x, sc.render.border_max_y = map(float, argv[3:7])
bpy.ops.render.render(write_still=True)
print("DONE", OUT)
