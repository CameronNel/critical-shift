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
import lib, arch, machinery, props, walldress, walltex, wallmesh, floormesh

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = os.path.abspath(argv[0] if argv else '/tmp/turbine_v2'); os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.system = 'METRIC'; sc.unit_settings.scale_length = 1.0
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
sc.view_settings.view_transform = 'AgX'
_looks = [i.identifier for i in sc.view_settings.bl_rna.properties['look'].enum_items]
sc.view_settings.look = next((l for l in _looks if 'Medium High Contrast' in l), 'None'); sc.view_settings.exposure = 0.0
atlas, orm = lib.make_atlas(os.path.join(OUT, 'turbine_atlas.png'))

RIM_STRENGTH = {'MACH': .24, 'PROPS': .21, 'ARCH': .14, 'SHAFT': .24}
def make_mats(grp):
    """Bake-ready PBR material (albedo atlas on UV0) and the emissive twin for lamps / screens."""
    def mk(name, emissive):
        m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
        out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (700, 0)
        uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'UVMap'; uvn.location = (-500, 0)
        tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = atlas; tex.interpolation = 'Linear'; tex.name = 'ALBEDO'; tex.location = (-250, 0)
        nt.links.new(uvn.outputs[0], tex.inputs[0])
        if emissive:
            e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Strength'].default_value = 2.0; e.location = (300, 0)
            nt.links.new(tex.outputs[0], e.inputs['Color']); nt.links.new(e.outputs[0], out.inputs['Surface'])
        else:
            p = nt.nodes.new('ShaderNodeBsdfPrincipled'); p.location = (300, 0)
            nt.links.new(tex.outputs[0], p.inputs['Base Color'])
            ot = nt.nodes.new('ShaderNodeTexImage'); ot.image = orm; ot.name = 'ORM'; ot.location = (-250, -300); nt.links.new(uvn.outputs[0], ot.inputs[0])
            sp = nt.nodes.new('ShaderNodeSeparateColor'); sp.location = (50, -300); nt.links.new(ot.outputs[0], sp.inputs[0])
            nt.links.new(sp.outputs['Green'], p.inputs['Roughness']); nt.links.new(sp.outputs['Blue'], p.inputs['Metallic'])
            # stylised silhouette rim (cool, thin, grazing-angle only): keeps dark hero forms readable. Must be reproduced in the runtime shader.
            lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = .3; lw.location = (50, 300)
            cr = nt.nodes.new('ShaderNodeValToRGB'); cr.location = (250, 300); cr.color_ramp.elements[0].position = .78; cr.color_ramp.elements[1].position = .985
            nt.links.new(lw.outputs['Facing'], cr.inputs['Fac'])
            mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = RIM_STRENGTH.get(grp, .5); mu.location = (450, 300); nt.links.new(cr.outputs['Color'], mu.inputs[0])
            em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (.5, .6, .8, 1); em.inputs['Strength'].default_value = 1.5; em.location = (450, 150)
            mx = nt.nodes.new('ShaderNodeMixShader'); mx.location = (550, 0)
            nt.links.new(mu.outputs[0], mx.inputs['Fac']); nt.links.new(p.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs['Surface'])
        return m
    return mk(f'M_{grp}', False), mk(f'M_{grp}_emissive', True)

coll = bpy.data.collections.new('TURBINE_ROOM_V2'); sc.collection.children.link(coll)
b = lib.Builder()
arch.build(b)
machinery.train(b); machinery.services(b); machinery.controls(b); machinery.maintenance(b)
props.build(b); walldress.build(b)
mats = {g: make_mats(g) for g in b.g if g not in ('OCC', 'GLASS')}
def make_glass():
    m = bpy.data.materials.new('M_GLASS'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); tr = nt.nodes.new('ShaderNodeBsdfTransparent'); gl = nt.nodes.new('ShaderNodeBsdfGlossy')
    gl.inputs['Roughness'].default_value = .06; gl.inputs['Color'].default_value = (.35, .5, .65, 1)
    mx = nt.nodes.new('ShaderNodeMixShader'); mx.inputs['Fac'].default_value = .07
    nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(gl.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs['Surface']); return m
if 'GLASS' in b.g: gm = make_glass(); mats['GLASS'] = (gm, gm)
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

occ_ob = objs.get('OCC')
if occ_ob:
    om = bpy.data.materials.new('M_occluder'); om.diffuse_color = (.02, .02, .02, 1); om.use_nodes = True
    om.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.02, .02, .02, 1); occ_ob.data.materials.append(om)
# ---- drum labels: flat texture decal (stripes + stencil text live in the image, zero thickness, no shadow) ----
import subprocess
dpng = os.path.join(OUT, 'drum_labels.png'); subprocess.run(['python3', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drumdecal.py'), dpng], check=True)
dimg = bpy.data.images.load(dpng); dimg.colorspace_settings.name = 'sRGB'
dm = bpy.data.materials.new('M_drum_decal'); dm.use_nodes = True; dnt = dm.node_tree; pb = dnt.nodes['Principled BSDF']
tx = dnt.nodes.new('ShaderNodeTexImage'); tx.image = dimg; tx.interpolation = 'Linear'
dnt.links.new(tx.outputs['Color'], pb.inputs['Base Color']); dnt.links.new(tx.outputs['Alpha'], pb.inputs['Alpha']); pb.inputs['Roughness'].default_value = .6
dm.surface_render_method = 'BLENDED'
NS, SPAN, ZB, ZT = 28, .9, .30, .62
for di, (dx, dy, _c, _t1, _t2) in enumerate(props.DRUMS):
    Rr = .27 + .0008; vs, ve = 1 - (di + 1) / len(props.DRUMS), 1 - di / len(props.DRUMS); vt = []; fc = []
    for i in range(NS + 1):
        th = -SPAN + 2 * SPAN * i / NS; vt += [(dx + Rr * math.sin(th), dy - Rr * math.cos(th), ZB), (dx + Rr * math.sin(th), dy - Rr * math.cos(th), ZT)]
    for i in range(NS): fc.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
    me = bpy.data.meshes.new(f'DRUM_DECAL_{di}'); me.from_pydata(vt, [], fc); me.update(); uv = me.uv_layers.new(name='UVMap'); k = 0
    for f in fc:
        for vi in f: uv.data[k].uv = ((vi // 2) / NS, vs if vi % 2 == 0 else ve); k += 1
    me.materials.append(dm); dob = bpy.data.objects.new(f'DRUM_DECAL_{di}', me); coll.objects.link(dob); dob.visible_shadow = False
# ---- the floor: one slab with holes + one texture set (wetness, flow, cracks, wear and paint live in the maps) ----
import floor as floor_layout, floortex, floormesh
tex_prefix = os.path.join(OUT, 'turbine_floor')
tex_info = None
if os.environ.get('REGEN_FLOOR', '1') == '1' or not os.path.exists(tex_prefix + '_albedo.png'): tex_info = floortex.generate(tex_prefix, floor_layout.LAYOUT)
mt, mw = floormesh.make_materials(tex_prefix)
floor_ob, floor_info = floormesh.make_floor(coll, floor_layout.LAYOUT, (mt, mw), arch.HOLE)
# ---- wall skins: one slab per wall with the real openings cut, one texture set per wall (96 px/m) ----
wall_info = {}
for nm, sp in arch.wall_specs().items():
    pre = os.path.join(OUT, f'turbine_wall_{nm}')
    L = sp['u1'] - sp['u0']
    if os.environ.get('REGEN_WALLS', '1') == '1' or not os.path.exists(pre + '_albedo.png'):
        walltex.generate(os.path.join(OUT, 'turbine_wall'), nm, L, sp['feat'], seed=11 + len(nm))
    wm, wmw = floormesh.make_materials(pre, f'wall_{nm}')
    wo, wi = wallmesh.make_wall(coll, nm, sp['frame'], sp['u0'], sp['u1'], sp['holes'], (wm, wmw)); wall_info[nm] = wi
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
    for x in arch.LAMP_X: spot(f'LAMP_{n:02d}', (x, y, 5.27), 2700, 56, (1.0, .55, .2), .12); n += 1
def aim(o, frm, to):
    o.rotation_euler = (Vector(to) - Vector(frm)).to_track_quat('-Z', 'Y').to_euler()
spot('LAMP_rotor', (machinery.CX, 11.25, 4.1), 1300, 62, (1.0, .66, .3), .4)
aim(spot('WORK_rotor', (6.38, 7.36, 3.55), 1000, 42, (1.0, .5, .2), .3), (6.38, 7.36, 3.55), (4.6, 11.0, 2.2))                     # work lamp on its stand
aim(spot('SPOT_desk', (8.0, 22.3, 4.8), 2600, 32, (1.0, .66, .32), .3), (8.0, 22.3, 4.8), (8.0, 23.4, .8))                    # lights the exposed gold blading
point('GLOW_coupling', (machinery.CX, 15.6, machinery.AZ + .35), 150, (1.0, .55, .18))
for k, y in enumerate((5.0, 11.0, 18.0)):                                                      # warm floor uplights give the casings a rim
    aim(spot(f'UP_W{k}', (1.35, y, .2), 180, 42, AMBER, .3), (1.35, y, .2), (3.2, y, 2.2)); aim(spot(f'UP_E{k}', (7.65, y, .2), 180, 42, AMBER, .3), (7.65, y, .2), (6.0, y, 2.2))
spot_c = spot('SPOT_consoles', (-1.6, 4.0, 4.6), 800, 44, (1.0, .62, .26)); aim(spot_c, (-1.6, 4.0, 4.6), (-3.0, 4.0, 1.2))
aim(spot('SPOT_desks', (-1.1, 4.0, 2.6), 650, 40, (1.0, .62, .26), .35), (-1.1, 4.0, 2.6), (-3.0, 4.0, 1.0))
aim(spot('POOL_A', (.9, 6.5, 4.6), 1800, 34, (1.0, .58, .24), .3), (.9, 6.5, 4.6), (.7, 6.5, 0)); aim(spot('POOL_K', (-.3, 3.6, 4.6), 1600, 34, (1.0, .58, .24), .3), (-.3, 3.6, 4.6), (-.5, 3.6, 0))
aim(spot('POOL_C', (7.2, 13.4, 5.0), 1800, 34, (1.0, .58, .24), .3), (7.2, 13.4, 5.0), (7.4, 13.4, 0)); aim(spot('POOL_J', (.7, 12.5, 5.0), 1800, 34, (1.0, .58, .24), .3), (.7, 12.5, 5.0), (.6, 12.5, 0)); aim(spot('POOL_M', (6.0, 9.3, 4.2), 1500, 34, (1.0, .58, .24), .3), (6.0, 9.3, 4.2), (6.5, 9.6, 1.0))
spot_b = spot('SPOT_bay', (-1.6, 17.0, 5.2), 420, 50, (1.0, .62, .26)); aim(spot_b, (-1.6, 17.0, 5.2), (-.9, 17.0, .8))
for k, y in enumerate((9.0, 12.5, 16.0, 19.5)):                                                # wall washers reveal the west wall and lead the eye along it
    aim(spot(f'WASH_W{k}', (-3.25, y, 4.4), 110, 52, (1.0, .66, .32), .3), (-3.25, y, 4.4), (-4.0, y, 2.0))
point('RED_gen', (machinery.CX - 1.9, 20.0, machinery.AZ + 1.4), 18, RED, .05); point('RED_hood', (machinery.CX, 16.6, 4.0), 12, RED, .05)
point('GLOW_consoles', (-2.6, 4.0, 1.9), 22, (1.0, .6, .25), .15)
for nm, loc in (('RED_D01', (1.7, 1.6, 3.0)), ('RED_D02', (1.7, 22.4, 3.0))): point(nm, loc, 22, RED, .1)
for nm, yy in (('PASS_D01', -.9), ('PASS_D02', 24.9)): point(nm, (0, yy, 2.5), 25, (1.0, .55, .25), .1)
for k, yy in enumerate((4, 12, 20)):
    d = bpy.data.lights.new(f'RIM_W{k}', 'AREA'); d.shape = 'RECTANGLE'; d.size, d.size_y = 2.0, .6; d.energy = 420; d.color = (.6, .7, .95)
    o = bpy.data.objects.new(f'RIM_W{k}', d); o.location = (-3.7, yy, 5.8); o.rotation_euler = (0, math.radians(50), 0); coll.objects.link(o)
sun = bpy.data.lights.new('MOON_EAST', 'SUN'); sun.energy = 4.5; sun.angle = math.radians(2.0); sun.color = (.38, .55, 1.0)
so = bpy.data.objects.new('MOON_EAST', sun); coll.objects.link(so)
so.rotation_euler = Vector((-.62, .40, -.67)).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (.075, .08, .095, 1); bg.inputs['Strength'].default_value = 1.15

aim(spot('KEY_casing_E', (8.7, 12.0, 3.6), 650, 66, (.62, .74, 1.0), .5), (8.7, 12.0, 3.6), (5.2, 10.0, 1.6))          # cool key on the casing flank so it separates from the dark hall
aim(spot('POOL_walk_E', (8.0, 13.8, 5.0), 2200, 38, (1.0, .6, .28), .25), (8.0, 13.8, 5.0), (7.6, 13.6, 1.0))             # warm pool on the walkway floor
aim(spot('KEY2_casing_E', (8.7, 11.0, 1.2), 380, 70, (.62, .74, 1.0), .5), (8.7, 11.0, 1.2), (5.2, 9.0, .6))
for k, yy in enumerate((7.0, 13.0, 19.0)):                                                                         # cool rim spots from the side walls (strips next to the trusses blew them out white)
    aim(spot(f'RIM_E{k}', (9.3, yy, 5.1), 1300, 38, (.86, .88, 1.0), .4), (9.3, yy, 5.1), (4.9, yy, 2.5)); aim(spot(f'RIM_W{k}', (-.5, yy, 5.2), 1300, 38, (.86, .88, 1.0), .4), (-.5, yy, 5.2), (4.3, yy, 2.5))
# cool/warm fills so silhouettes separate and shadows are not dead black (readability pass)
for k, (fx, fy) in enumerate(((-.5, 5), (3, 12), (7.5, 19), (3, 21))):
    d = bpy.data.lights.new(f'FILL_{k}', 'AREA'); d.shape = 'RECTANGLE'; d.size, d.size_y = 5.0, 5.0; d.energy = 70; d.color = (.8, .84, .95)
    o = bpy.data.objects.new(f'FILL_{k}', d); o.location = (fx, fy, 6.0); coll.objects.link(o)
# ---- named review cameras ----
CAMS = {   # all positions are in open aisle space
    'CAM_A_entry_north':   ((1.0, 1.4, 1.65), (3.5, 14, 2.0)),
    'CAM_B_ne_high':       ((8.8, 22.6, 4.6), (2.4, 6, 1.2)),
    'CAM_C_east_aisle':    ((7.7, 12.2, 1.8), (2.8, 20, 2.3)),
    'CAM_D_maintenance':   ((-3.2, 12.6, 1.65), (-.5, 19.5, 1.7)),
    'CAM_E_controls':      ((.9, 4.0, 1.55), (-3.5, 4.0, 1.9)),
    'CAM_F_sw_high':       ((-2.4, 1.6, 4.2), (5.0, 16, 1.5)),
    'CAM_G_generator':     ((8.4, 15.0, 2.4), (4.6, 18.5, 2.0)),
    'CAM_H_roof':          ((1.0, 4.0, 1.65), (3.4, 14, 6.4)),
    'CAM_J_north_back':    ((.9, 23.0, 2.1), (1.3, 2, 1.8)),
    'CAM_K_door_d01':      ((1.5, 8.8, 1.65), (-3.9, .3, 1.9)),
    'CAM_M_turbine_close': ((6.6, 7.4, 3.0), (4.6, 11.6, 1.45)),
    'CAM_P_west_wall':     ((1.0, 12.0, 1.65), (-4, 12, 2.6)),
    'CAM_Q_east_wall':     ((8.6, 3.2, 1.7), (10, 13, 3.0)),
    'CAM_R_south_wall':    ((6.0, 11.5, 1.8), (4.5, 0, 3.4)),
    'CAM_N_floor':         ((.2, 3.6, .95), (1.5, 13.5, .08)),
    'CAM_L_desk':          ((7.8, 19.8, 1.6), (8.55, 23.5, 1.05)),
}
for name, (loc, tgt) in CAMS.items():
    cd = bpy.data.cameras.new(name); cd.lens = {'CAM_E_controls': 16, 'CAM_K_door_d01': 19, 'CAM_J_north_back': 20, 'CAM_H_roof': 20, 'CAM_A_entry_north': 22}.get(name, 24); co = bpy.data.objects.new(name, cd); coll.objects.link(co); co.location = loc
    co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
sc.camera = bpy.data.objects['CAM_A_entry_north']
for _o in coll.objects:
    if _o.type == 'LIGHT': _o.visible_camera = False                                  # area lights must not show up as white shards in the frame

hz = bpy.data.materials.new('M_haze'); hz.use_nodes = True; hn = hz.node_tree; hn.nodes.clear()
vs = hn.nodes.new('ShaderNodeVolumeScatter'); vs.inputs['Density'].default_value = .006; vs.inputs['Anisotropy'].default_value = .45; vs.inputs['Color'].default_value = (1, .78, .55, 1)
ho = hn.nodes.new('ShaderNodeOutputMaterial'); hn.links.new(vs.outputs[0], ho.inputs['Volume'])
hm = bpy.data.meshes.new('HAZE'); hm.from_pydata([(x, y, z) for x in (-3.95, 9.95) for y in (.05, 23.95) for z in (.05, 7.15)], [], [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)])
ho_ = bpy.data.objects.new('HAZE_VOLUME', hm); hm.materials.append(hz); coll.objects.link(ho_); ho_.hide_render = os.environ.get('HAZE') != '1'; ho_['shipping'] = False
report = dict(group_stats={k: v for k, v in b.stats().items()}, total_tris_before_cull=sum(v['tris'] for v in b.stats().values()), total_tris=sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for k, o in objs.items() if k != 'OCC') + floor_info['tris'] + sum(w['tris'] for w in wall_info.values()), floor=floor_info, walls=wall_info, floor_textures=tex_info,
              bevelled_edges=bevelled, faces_kept=cull_kept, faces_culled=cull_removed, materials=len(bpy.data.materials), images=[i.name for i in bpy.data.images], objects=len(bpy.data.objects))
print('REPORT', json.dumps(report))
json.dump(report, open(os.path.join(OUT, 'build_report.json'), 'w'), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'turbine_room_v2_geo.blend'), compress=True)
