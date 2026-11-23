"""Mô hình 3D đơn giản (xe tăng, máy bay cánh quạt, tàu tuần tra) chụp thẳng từ trên xuống ở 24 hướng.
blender -b -P models.py -- <out_dir>"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

OUT = sys.argv[sys.argv.index("--") + 1]; os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


def mat(name, col, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    return m


def cube(name, loc, size, m, bevel=0.0, parent=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.location = loc
    if bevel:
        md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 3
    o.data.materials.append(m); o.parent = parent; return o


def cyl(name, loc, r, d, m, rot=(0, 0, 0), verts=24, parent=None, r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=d, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(m); o.parent = parent
    bpy.ops.object.shade_smooth(); return o


def sphere(name, loc, sc_, m, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=loc); o = bpy.context.active_object
    o.scale = sc_; o.data.materials.append(m); o.parent = parent; bpy.ops.object.shade_smooth(); return o


# ---------------- xe tăng (hướng +X) ----------------
olive = mat("olive", (0.07, 0.09, 0.035), 0.7); dark = mat("dark", (0.03, 0.03, 0.025), 0.9)
red = mat("red", (0.75, 0.02, 0.02), 0.5); yel = mat("yel", (0.9, 0.7, 0.05), 0.5)
tank = bpy.data.objects.new("tank", None); sc.collection.objects.link(tank)
cube("hull", (0, 0, 0.65), (6.2, 2.7, 1.0), olive, 0.12, tank)
cube("glacis", (2.9, 0, 0.8), (0.9, 2.6, 0.5), olive, 0.15, tank)
for s in (-1, 1):
    cube("track", (0, s * 1.75, 0.5), (6.8, 0.8, 1.0), dark, 0.2, tank)
    for k in range(13): cube("tread", (-3.0 + k * 0.5, s * 1.75, 1.0), (0.18, 0.82, 0.04), olive, 0, tank)
tur = sphere("turret", (-0.3, 0, 1.15), (1.55, 1.4, 0.55), olive, tank)
cyl("barrel", (2.4, 0, 1.3), 0.13, 4.4, olive, rot=(0, math.pi / 2, 0), parent=tank)
cyl("hatch", (-0.6, 0.45, 1.62), 0.35, 0.12, olive, parent=tank)
star_me = bpy.data.meshes.new("star"); bm = bmesh.new(); pts = []
for k in range(10):
    a = math.pi / 2 + k * math.pi / 5; rr = 0.42 if k % 2 == 0 else 0.17; pts.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), 0)))
c = bm.verts.new((0, 0, 0))
for k in range(10): bm.faces.new((c, pts[k], pts[(k + 1) % 10]))
bm.to_mesh(star_me); st = bpy.data.objects.new("star", star_me); sc.collection.objects.link(st)
st.location = (-0.3, 0, 1.71); st.rotation_euler = (0, 0, -math.pi / 2); st.data.materials.append(red); st.parent = tank

# ---------------- máy bay cánh quạt (hướng +X) ----------------
grey = mat("grey", (0.30, 0.32, 0.31), 0.45, 0.3); glass = mat("glass", (0.05, 0.08, 0.12), 0.1)
plane = bpy.data.objects.new("plane", None); sc.collection.objects.link(plane)
sphere("fus", (0, 0, 3), (5.5, 0.75, 0.75), grey, plane)
cube("wing", (0.6, 0, 3), (1.6, 13.0, 0.18), grey, 0.08, plane)
cube("tail", (-4.8, 0, 3.1), (0.9, 4.4, 0.14), grey, 0.05, plane)
cube("fin", (-4.9, 0, 3.8), (1.0, 0.12, 1.4), grey, 0.05, plane)
sphere("cockpit", (2.6, 0, 3.55), (1.1, 0.45, 0.35), glass, plane)
for s in (-1, 1):
    sphere("eng", (1.6, s * 2.6, 3.0), (1.4, 0.45, 0.45), grey, plane)
    cyl("prop", (3.05, s * 2.6, 3.0), 1.3, 0.05, dark, rot=(0, math.pi / 2, 0), verts=32, parent=plane)

# ---------------- tàu tuần tra (hướng +X) ----------------
hullm = mat("hull", (0.20, 0.23, 0.25), 0.5, 0.2); deck = mat("deck", (0.45, 0.42, 0.36), 0.8); white = mat("white", (0.75, 0.76, 0.74), 0.5)
ship = bpy.data.objects.new("ship", None); sc.collection.objects.link(ship)
me = bpy.data.meshes.new("hullm"); bm = bmesh.new()
prof = [(-11, 1.6), (-8, 2.1), (0, 2.3), (5, 2.0), (9, 1.0), (12, 0.0)]
top = [bm.verts.new((x, y, 1.4)) for x, y in prof] + [bm.verts.new((x, -y, 1.4)) for x, y in prof[::-1][1:-1]]
bot = [bm.verts.new((x * 0.97, y * 0.7, 0)) for x, y in prof] + [bm.verts.new((x * 0.97, -y * 0.7, 0)) for x, y in prof[::-1][1:-1]]
bm.faces.new(top); bm.faces.new(bot[::-1])
n = len(top)
for i in range(n): bm.faces.new((top[i], top[(i + 1) % n], bot[(i + 1) % n], bot[i]))
bm.normal_update(); bm.to_mesh(me); h = bpy.data.objects.new("hull", me); sc.collection.objects.link(h); h.data.materials.append(hullm); h.parent = ship
cube("deckp", (-0.5, 0, 1.45), (19, 3.6, 0.05), deck, 0, ship)
cube("bridge", (-1.0, 0, 2.4), (5.0, 2.6, 1.9), white, 0.15, ship)
cube("bridge2", (-0.6, 0, 3.6), (2.4, 2.0, 0.8), white, 0.1, ship)
cyl("mast", (-1.2, 0, 4.8), 0.12, 2.6, grey, parent=ship)
cyl("gun", (5.6, 0, 1.9), 0.75, 0.6, grey, parent=ship); cyl("gunb", (7.0, 0, 2.0), 0.1, 2.4, grey, rot=(0, math.pi / 2, 0), parent=ship)
cube("aft", (-7.5, 0, 1.9), (2.5, 2.2, 0.9), grey, 0.1, ship)

# ---------------- ánh sáng, camera ----------------
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.0; sun.angle = math.radians(4)
so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(38), 0, math.radians(-135))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.6, 0.65, 0.75, 1); w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5
cd = bpy.data.cameras.new("cam"); cd.type = "ORTHO"; co = bpy.data.objects.new("cam", cd); sc.collection.objects.link(co)
co.location = (0, 0, 50); sc.camera = co
sc.render.engine = "CYCLES"; sc.cycles.samples = 24; sc.cycles.use_denoising = True
sc.render.film_transparent = True; sc.render.resolution_x = sc.render.resolution_y = 384
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"
sc.view_settings.view_transform = "Standard"
objs = {"tank": (tank, 8.0), "plane": (plane, 15.0), "ship": (ship, 25.0)}
for name, (o, span) in objs.items():
    for other, _ in objs.values():
        for ch in [other] + list(other.children_recursive): ch.hide_render = other is not o
    cd.ortho_scale = span
    for k in range(24):
        o.rotation_euler = (0, 0, math.radians(k * 15))
        sc.render.filepath = os.path.join(OUT, f"{name}_{k * 15:03d}.png"); bpy.ops.render.render(write_still=True)
    print("done", name, flush=True)
