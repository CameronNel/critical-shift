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
            e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Strength'].default_value = 7.0; e.location = (300, 0)
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
KEEP_OUTSIDE = [(-1.5, 1.5, -1.85, 0.005, -.05, 2.9), (-1.5, 1.5, 23.995, 25.85, -.05, 2.9),      # door passages
                (8.0, 8.8, -.4, .005, 4.4, 5.4), (9.2, 9.8, -.4, .005, .2, .7), (-4.7, -3.5, 23.995, 25.6, 3.5, 4.3)]   # U01, U02, U03 stubs
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
            if not inside:
                inside = any(x0 <= c.x <= x1 and y0 <= c.y <= y1 and z0 <= c.z <= z1 for x0, x1, y0, y1, z0, z1 in KEEP_OUTSIDE)
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
def area(name, loc, size, power, color=(1, .84, .64)):
    d = bpy.data.lights.new(name, 'AREA'); d.shape = 'RECTANGLE'; d.size, d.size_y = size; d.energy = power; d.color = color
    o = bpy.data.objects.new(name, d); o.location = loc; coll.objects.link(o); return o
# ---- night rig: amber hooded pendants (pools with dark gaps), red warning light, cold moon through the clerestories ----
def spot(name, loc, power, size_deg, color, blend=.55):
    d = bpy.data.lights.new(name, 'SPOT'); d.energy = power; d.spot_size = math.radians(size_deg); d.spot_blend = blend; d.color = color; d.shadow_soft_size = .12
    o = bpy.data.objects.new(name, d); o.location = loc; coll.objects.link(o); return o
def point(name, loc, power, color, radius=.1):
    d = bpy.data.lights.new(name, 'POINT'); d.energy = power; d.color = color; d.shadow_soft_size = radius
    o = bpy.data.objects.new(name, d); o.location = loc; coll.objects.link(o); return o
AMBER, RED = (1.0, .58, .22), (1.0, .12, .06)
n = 0
for y in arch.LAMP_Y:
    for x in arch.LAMP_X: spot(f'LAMP_{n:02d}', (x, y, 5.27), 1900, 100, AMBER, .7); n += 1
def aim(o, frm, to):
    o.rotation_euler = (Vector(to) - Vector(frm)).to_track_quat('-Z', 'Y').to_euler()
spot('LAMP_rotor', (machinery.CX, 11.25, 4.1), 800, 65, (1.0, .66, .3), .5)                    # lights the exposed gold blading
point('GLOW_coupling', (machinery.CX, 15.6, machinery.AZ + .35), 150, (1.0, .55, .18))
for k, y in enumerate((5.0, 11.0, 18.0)):                                                      # warm floor uplights give the casings a rim
    aim(spot(f'UP_W{k}', (1.35, y, .2), 260, 42, AMBER, .5), (1.35, y, .2), (3.2, y, 2.2)); aim(spot(f'UP_E{k}', (7.65, y, .2), 260, 42, AMBER, .5), (7.65, y, .2), (6.0, y, 2.2))
spot_c = spot('SPOT_consoles', (-2.3, 5.65, 4.8), 520, 46, (1.0, .62, .26)); aim(spot_c, (-2.3, 5.65, 4.8), (-3.5, 5.65, 1.4))
spot_b = spot('SPOT_bay', (-1.6, 17.0, 5.2), 420, 50, (1.0, .62, .26)); aim(spot_b, (-1.6, 17.0, 5.2), (-.9, 17.0, .8))
for k, y in enumerate((9.0, 12.5, 16.0, 19.5)):                                                # wall washers reveal the west wall and lead the eye along it
    aim(spot(f'WASH_W{k}', (-3.25, y, 4.4), 260, 58, AMBER, .6), (-3.25, y, 4.4), (-4.0, y, 2.0))
point('RED_gen', (machinery.CX - 1.9, 20.0, machinery.AZ + 1.4), 70, RED, .05); point('RED_hood', (machinery.CX, 16.6, 4.0), 40, RED, .05)
point('GLOW_consoles', (-3.1, 5.65, 1.9), 40, (1.0, .6, .25), .15)
for nm, loc in (('RED_D01', (1.7, .25, 3.35)), ('RED_D02', (1.7, 23.75, 3.35))): point(nm, loc, 90, RED, .06)
for nm, yy in (('PASS_D01', -.9), ('PASS_D02', 24.9)): point(nm, (0, yy, 2.5), 45, (1.0, .45, .2), .1)
sun = bpy.data.lights.new('MOON_EAST', 'SUN'); sun.energy = 4.5; sun.angle = math.radians(2.0); sun.color = (.50, .64, 1.0)
so = bpy.data.objects.new('MOON_EAST', sun); coll.objects.link(so)
so.rotation_euler = Vector((-.62, .40, -.67)).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (.04, .075, .18, 1); bg.inputs['Strength'].default_value = 2.6

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
    'CAM_M_turbine_close': ((6.7, 8.5, 2.95), (4.6, 11.6, 2.2)),
    'CAM_L_desk':          ((7.7, 19.8, 1.6), (8.4, 23.5, 1.0)),
}
for name, (loc, tgt) in CAMS.items():
    cd = bpy.data.cameras.new(name); cd.lens = 24; co = bpy.data.objects.new(name, cd); coll.objects.link(co); co.location = loc
    co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
sc.camera = bpy.data.objects['CAM_A_entry_north']

hz = bpy.data.materials.new('M_haze'); hz.use_nodes = True; hn = hz.node_tree; hn.nodes.clear()
vs = hn.nodes.new('ShaderNodeVolumeScatter'); vs.inputs['Density'].default_value = .006; vs.inputs['Anisotropy'].default_value = .45; vs.inputs['Color'].default_value = (1, .78, .55, 1)
ho = hn.nodes.new('ShaderNodeOutputMaterial'); hn.links.new(vs.outputs[0], ho.inputs['Volume'])
hm = bpy.data.meshes.new('HAZE'); hm.from_pydata([(x, y, z) for x in (-3.95, 9.95) for y in (.05, 23.95) for z in (.05, 7.15)], [], [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)])
ho_ = bpy.data.objects.new('HAZE_VOLUME', hm); hm.materials.append(hz); coll.objects.link(ho_); ho_.hide_render = os.environ.get('HAZE') != '1'; ho_['shipping'] = False
report = dict(group_stats={k: v for k, v in b.stats().items()}, total_tris_before_cull=sum(v['tris'] for v in b.stats().values()), total_tris=sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for k, o in objs.items() if k != 'OCC'),
              bevelled_edges=bevelled, faces_kept=cull_kept, faces_culled=cull_removed, materials=len(bpy.data.materials), images=[i.name for i in bpy.data.images], objects=len(bpy.data.objects))
print('REPORT', json.dumps(report))
json.dump(report, open(os.path.join(OUT, 'build_report.json'), 'w'), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'turbine_room_v2_geo.blend'), compress=True)
