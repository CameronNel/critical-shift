"""Build the new turbine room from an empty scene.

blender --background --factory-startup --disable-autoexec --python-exit-code 1 \
  --python sections/facility-assembly/blender/turbine_rebuild/run.py -- OUT_DIR

Nothing from the previous room is loaded: only the 14 x 24 x 7.2 m footprint and the
door / utility interface positions (see contracts/interface.json) are kept.
"""
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import lib, arch, machinery, props

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = os.path.abspath(argv[0] if argv else '/tmp/turbine_v2'); os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.system = 'METRIC'; sc.unit_settings.scale_length = 1.0
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
atlas, orm = lib.make_atlas(os.path.join(OUT, 'turbine_atlas.png'))

def make_mats(grp):
    """Bake-ready PBR material (albedo atlas on UV0) and the emissive twin for lamps / screens."""
    def mk(name, emissive):
        m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
        out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (700, 0)
        uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'UVMap'; uvn.location = (-500, 0)
        tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = atlas; tex.interpolation = 'Linear'; tex.name = 'ALBEDO'; tex.location = (-250, 0)
        nt.links.new(uvn.outputs[0], tex.inputs[0])
        if emissive:
            e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Strength'].default_value = 3.0; e.location = (300, 0)
            nt.links.new(tex.outputs[0], e.inputs['Color']); nt.links.new(e.outputs[0], out.inputs['Surface'])
        else:
            p = nt.nodes.new('ShaderNodeBsdfPrincipled'); p.location = (300, 0)
            nt.links.new(tex.outputs[0], p.inputs['Base Color'])
            ot = nt.nodes.new('ShaderNodeTexImage'); ot.image = orm; ot.name = 'ORM'; ot.location = (-250, -300); nt.links.new(uvn.outputs[0], ot.inputs[0])
            sp = nt.nodes.new('ShaderNodeSeparateColor'); sp.location = (50, -300); nt.links.new(ot.outputs[0], sp.inputs[0])
            nt.links.new(sp.outputs['Green'], p.inputs['Roughness']); nt.links.new(sp.outputs['Blue'], p.inputs['Metallic'])
            nt.links.new(p.outputs[0], out.inputs['Surface'])
        return m
    return mk(f'M_{grp}', False), mk(f'M_{grp}_emissive', True)

coll = bpy.data.collections.new('TURBINE_ROOM_V2'); sc.collection.children.link(coll)
b = lib.Builder()
arch.build(b)
machinery.train(b); machinery.services(b); machinery.controls(b); machinery.maintenance(b)
props.build(b)
mats = {g: make_mats(g) for g in b.g if g != 'OCC'}
objs = b.build(coll, mats)


# ---- cull invisible faces (outside the shell, buried against other solids). Culled faces are kept in a
# non-shipping occluder mesh so the light bake still sees a sealed room (no light leaks through seams). ----
def cull(objs):
    import bmesh
    from mathutils.bvhtree import BVHTree
    V, F = [], []
    occ0 = objs.get('OCC')
    for ob in objs.values():
        base = len(V); V += [v.co[:] for v in ob.data.vertices]
        F += [tuple(base + i for i in p.vertices) for p in ob.data.polygons]
    tree = BVHTree.FromPolygons(V, F)
    dirs = []
    for i in range(24):                                   # fibonacci hemisphere
        z = (i + .5) / 24; r = math.sqrt(1 - z * z); a = i * 2.399963
        dirs.append(Vector((r * math.cos(a), r * math.sin(a), z)))
    hx0, hx1, hy0, hy1 = arch.HOLE
    occ_v, occ_f, kept, removed = [], [], 0, 0
    for ob in objs.values():
        if ob is occ0: continue
        bm = bmesh.new(); bm.from_mesh(ob.data); dele = []
        sl = bm.faces.layers.int.get('swatch'); keep_idx = lib.SWATCH['backing']
        for f in bm.faces:
            c = f.calc_center_median(); n = f.normal
            inside = -4.005 <= c.x <= 10.005 and -.005 <= c.y <= 24.005 and -.005 <= c.z <= 7.205
            in_hole = hx0 - .1 <= c.x <= hx1 + .1 and hy0 - .1 <= c.y <= hy1 + .1 and c.z < 0
            if not inside and not in_hole: dele.append(f); continue
            if sl is not None and f[sl] == keep_idx: continue
            t = n.cross(Vector((0, 0, 1)) if abs(n.z) < .9 else Vector((1, 0, 0))).normalized(); bt = n.cross(t)
            open_ = False
            pts = [(c, dirs)] + [(c + (v.co - c) * .6, dirs[::3]) for v in f.verts]          # centre + points toward each corner (big n-gons)
            for pc, dd in pts:
                o = pc + n * .004
                for d in dd:
                    w = t * d.x + bt * d.y + n * d.z
                    if tree.ray_cast(o, w, .18)[0] is None: open_ = True; break
                if open_: break
            if not open_: dele.append(f)
        for f in dele:
            base = len(occ_v); occ_v += [v.co[:] for v in f.verts]; occ_f.append(tuple(range(base, base + len(f.verts))))
        removed += len(dele); kept += len(bm.faces) - len(dele)
        bmesh.ops.delete(bm, geom=dele, context='FACES'); bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
        # keep the UV/material layers consistent: bmesh preserves them on from_mesh/to_mesh
        bm.to_mesh(ob.data); bm.free()
    base = len(occ0.data.vertices); em = occ0.data
    import bmesh as _bm
    bm = _bm.new(); bm.from_mesh(em)
    vs = [bm.verts.new(v) for v in occ_v]
    off = 0
    for f in occ_f:
        try: bm.faces.new([vs[i] for i in f])
        except ValueError: pass
    bm.to_mesh(em); bm.free()
    return kept, removed
cull_kept, cull_removed = cull({k: o for k, o in objs.items()})
bevelled = {k: lib.finalize(o) for k, o in objs.items() if k != 'OCC'}      # weld + bevel marked edges + shade by angle

# animated shaft: origin on the rotation axis
sh = objs.get('SHAFT')
if sh:
    org = Vector((machinery.CX, 15.0, machinery.AZ)); me = sh.data
    for v in me.vertices: v.co -= org
    sh.location = org; sh.name = 'ANIM_TURBINE_SHAFT'

# ---- lighting rig (used for the bake; light-map result is what ships) ----
def area(name, loc, size, power, color=(1, .90, .74)):
    d = bpy.data.lights.new(name, 'AREA'); d.shape = 'RECTANGLE'; d.size, d.size_y = size; d.energy = power; d.color = color
    o = bpy.data.objects.new(name, d); o.location = loc; coll.objects.link(o); return o
n = 0
for y in (4, 8, 12, 16, 20):
    for x in (-1.2, 4.6, 8.6):
        area(f'LAMP_{n:02d}', (x, y, 5.27), (1.1, .15), 190); n += 1
area('LAMP_broken', (2.0, 20.5, 4.9), (1.1, .15), 160, (1, .8, .55)).rotation_euler = (.9, 0, 0)
sun = bpy.data.lights.new('SUN_EAST', 'SUN'); sun.energy = 3.0; sun.angle = math.radians(1.2); sun.color = (1.0, .93, .80)
so = bpy.data.objects.new('SUN_EAST', sun); coll.objects.link(so)
so.rotation_euler = Vector((-.62, .40, -.67)).to_track_quat('-Z', 'Y').to_euler()          # coming from the east, ~34 deg elevation
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (.55, .68, .86, 1); bg.inputs['Strength'].default_value = .7

# ---- named review cameras ----
CAMS = {   # all positions are in open aisle space
    'CAM_A_entry_north':   ((0.0, 1.4, 1.65), (4.6, 14, 2.0)),
    'CAM_B_ne_high':       ((9.1, 23.0, 4.6), (-1, 6, 1.5)),
    'CAM_C_east_aisle':    ((7.9, 12.5, 1.65), (2, 20, 2.2)),
    'CAM_D_maintenance':   ((-3.2, 12.6, 1.65), (-.5, 19.5, 1.2)),
    'CAM_E_controls':      ((2.2, 8.0, 1.65), (-3.8, 5.6, 1.6)),
    'CAM_F_sw_high':       ((-2.4, 1.6, 4.2), (6, 16, 1.5)),
    'CAM_G_generator':     ((8.3, 15.0, 1.65), (4.6, 18.5, 2.2)),
    'CAM_H_roof':          ((1.0, 4.0, 1.65), (4.6, 14, 6.4)),
    'CAM_J_north_back':    ((1.0, 22.3, 1.7), (5, 2, 2.4)),
    'CAM_K_door_d01':      ((0.2, 7.6, 1.65), (-2.4, .3, 1.7)),
    'CAM_L_desk':          ((7.7, 19.8, 1.6), (8.4, 23.5, 1.0)),
}
for name, (loc, tgt) in CAMS.items():
    cd = bpy.data.cameras.new(name); cd.lens = 24; co = bpy.data.objects.new(name, cd); coll.objects.link(co); co.location = loc
    co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
sc.camera = bpy.data.objects['CAM_A_entry_north']

report = dict(group_stats={k: v for k, v in b.stats().items()}, total_tris_before_cull=sum(v['tris'] for v in b.stats().values()), total_tris=sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for k, o in objs.items() if k != 'OCC'),
              bevelled_edges=bevelled, faces_kept=cull_kept, faces_culled=cull_removed, materials=len(bpy.data.materials), images=[i.name for i in bpy.data.images], objects=len(bpy.data.objects))
print('REPORT', json.dumps(report))
json.dump(report, open(os.path.join(OUT, 'build_report.json'), 'w'), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'turbine_room_v2_geo.blend'), compress=True)
