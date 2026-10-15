# Headless Blender build: models props in code, exports one FBX per asset, renders previews,
# writes stats.json, and saves the source .blend.
#   Blender -b --factory-startup --python build-template.py -- <staging dir> <preview dir>
import bpy, bmesh, math, json, os, sys
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT, PREVIEW = ARGS[0], ARGS[1]
os.makedirs(OUT, exist_ok=True)
os.makedirs(PREVIEW, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hexcol(h):
    return tuple(lin(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5))


# name: (hex colour, roughness, metallic). Names carry into Unity as material slot names.
MAT_DEFS = {
    "Wood_Dark":  ("#5a3d26", 0.8, 0.0),
    "Wood_Light": ("#b08a5a", 0.7, 0.0),
    "Hay_Gold":   ("#d1a94f", 0.9, 0.0),
    "Hay_Pale":   ("#e6cf8a", 0.9, 0.0),
}
_mats = {}


def material(name):
    if name in _mats:
        return _mats[name]
    h, rough, metal = MAT_DEFS[name]
    rgb = hexcol(h)
    m = bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*rgb, 1.0)  # viewport colour, used by the workbench previews
    m.roughness = rough
    m.metallic = metal
    _mats[name] = m
    return m


class MB:
    """Mesh builder: faces carry material names; finalize() makes the object."""

    def __init__(self):
        self.bm = bmesh.new()
        self.mats = []

    def mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def face(self, verts, m):
        f = self.bm.faces.new(verts)
        f.material_index = self.mi(m)
        return f

    def box(self, center, size, m):
        c = Vector(center)
        hx, hy, hz = (s / 2 for s in size)
        pts = [c + Vector((sx * hx, sy * hy, sz * hz)) for sz in (-1, 1)
               for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        v = [self.bm.verts.new(p) for p in pts]
        for q in ((0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            self.face([v[i] for i in q], m)

    def loft(self, rings, m, cap0=None, cap1=None, capm=None):
        # skin a list of equal-length vertex rings; a cap is 'ngon' or an apex point
        vr = [[self.bm.verts.new(p) for p in r] for r in rings]
        n = len(rings[0])
        for a, b in zip(vr, vr[1:]):
            for j in range(n):
                self.face((a[j], a[(j + 1) % n], b[(j + 1) % n], b[j]), m)
        for rg, spec in ((vr[0], cap0), (vr[-1], cap1)):
            if spec is None:
                continue
            if spec == 'ngon':
                self.face(rg, capm or m)
            else:
                c = self.bm.verts.new(Vector(spec))
                for j in range(n):
                    self.face((rg[j], rg[(j + 1) % n], c), capm or m)


def ring(c, r, sides, u=Vector((1, 0, 0)), v=Vector((0, 1, 0)), phase=0.0):
    return [Vector(c) + r * (math.cos(phase + 2 * math.pi * j / sides) * u
                             + math.sin(phase + 2 * math.pi * j / sides) * v)
            for j in range(sides)]


def finalize(mb, name, coll, location=(0, 0, 0), smooth=None):
    # smooth: None = flat shading; a number = smooth, keeping edges sharper than that many degrees hard
    bm = mb.bm
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
    for f in bm.faces:
        f.smooth = smooth is not None
    if smooth is not None:
        thr = math.radians(smooth)
        for e in bm.edges:
            lf = e.link_faces
            if len(lf) != 2:
                e.smooth = False
            elif e.calc_face_angle(0.0) > thr or lf[0].material_index != lf[1].material_index:
                e.smooth = False
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for mname in mb.mats:
        me.materials.append(material(mname))
    ob = bpy.data.objects.new(name, me)
    ob.location = location  # a part's pivot: geometry is built around (0,0,0), then located here
    coll.objects.link(ob)
    return ob


def new_coll(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c


# Each builder returns its asset's objects: origin at the bottom centre, front toward -Y.

def signpost():
    # Post sits at the origin; Board is its own object so Unity can parent a label to it.
    # Board's pivot is the centre of its front (-Y) face: geometry is built around that pivot.
    c = new_coll("Signpost")
    post = MB()
    post.box((0, 0, 1.1), (0.12, 0.12, 2.2), "Wood_Dark")
    board = MB()
    board.box((0, 0.025, 0), (1.4, 0.05, 0.5), "Wood_Light")
    return [finalize(post, "Post", c),
            finalize(board, "Board", c, location=(0, -0.11, 1.75))]


def haybale():
    # one object lying along X: a rounded cylinder with pale ends (the cap material)
    c = new_coll("HayBale")
    mb = MB()
    prof = [(-0.6, 0.68), (-0.56, 0.735), (-0.5, 0.75), (0.5, 0.75), (0.56, 0.735), (0.6, 0.68)]
    rings = [ring((x, 0, 0.75), r, 20, Vector((0, 1, 0)), Vector((0, 0, 1)), phase=-math.pi / 2)
             for x, r in prof]
    mb.loft(rings, "Hay_Gold", (-0.6, 0, 0.75), (0.6, 0, 0.75), capm="Hay_Pale")
    return [finalize(mb, "HayBale", c, smooth=40)]


BUILDERS = [("Signpost", signpost), ("HayBale", haybale)]

EXPORT = dict(use_selection=True, object_types={'MESH'}, axis_forward='-Y', axis_up='Z',
              use_space_transform=False, apply_scale_options='FBX_SCALE_ALL', bake_anim=False,
              check_existing=False)

# build, then measure what Unity will import
ASSETS, stats = {}, {}
for name, fn in BUILDERS:
    objs = fn()
    ASSETS[name] = objs
    bpy.context.view_layer.update()
    lo = Vector((1e9,) * 3)
    hi = Vector((-1e9,) * 3)
    tris, mats, per = 0, [], {}
    for ob in objs:
        for v in ob.data.vertices:
            w = ob.matrix_world @ v.co
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
        assert all(len(p.vertices) == 3 for p in ob.data.polygons)
        per[ob.name] = {"tris": len(ob.data.polygons), "location": [round(x, 4) for x in ob.location],
                        "rotation": list(ob.rotation_euler), "scale": list(ob.scale)}
        tris += len(ob.data.polygons)
        for m in ob.data.materials:
            if m.name not in mats:
                mats.append(m.name)
    stats[name] = {"tris": tris, "materials": mats, "objects": per,
                   "bbox_min": [round(x, 4) for x in lo], "bbox_max": [round(x, 4) for x in hi],
                   "size": [round(h - l, 4) for l, h in zip(lo, hi)]}

# export one FBX per asset: select only that asset's objects
for name, objs in ASSETS.items():
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, name + ".fbx"), **EXPORT)

# previews: a workbench render per asset from the front-right, to check the front faces -Y
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.render.resolution_x, scene.render.resolution_y = 800, 600
scene.world = bpy.data.worlds.new("PreviewWorld")
cam_data = bpy.data.cameras.new("PreviewCam")
cam = bpy.data.objects.new("PreviewCam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
for name in ASSETS:
    for other in ASSETS:
        bpy.data.collections[other].hide_render = other != name
    s = stats[name]
    ctr = Vector([(a + b) / 2 for a, b in zip(s["bbox_min"], s["bbox_max"])])
    d = Vector((0.75, -1.6, 0.55)).normalized()
    cam.location = ctr + d * max(s["size"]) * 2.3
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = os.path.join(PREVIEW, name + ".png")
    bpy.ops.render.render(write_still=True)

bpy.data.objects.remove(cam)
bpy.data.cameras.remove(cam_data)
for name in ASSETS:
    bpy.data.collections[name].hide_render = False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Props.blend"))

with open(os.path.join(PREVIEW, "stats.json"), "w") as f:
    json.dump(stats, f, indent=1)
print("STATS", json.dumps({k: (v["tris"], v["size"], v["materials"]) for k, v in stats.items()}))
