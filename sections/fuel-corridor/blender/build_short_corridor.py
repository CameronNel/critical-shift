"""Short fuel corridor S1 (2026-10-13): the reviewed F23ci corridor, cut down for the compact map. Run:

    blender --background --factory-startup --python sections/fuel-corridor/blender/build_short_corridor.py -- \
        [--source sections/fuel-corridor/production/checkpoints/fuel_full_F23ci.blend] [--output sections/facility-assembly/sources/fuel-corridor/module_short_S1.blend]

Owner instruction: rebuild the fuel corridor "to the same graphical fidelity as it was previously", after the grey-box test (combined/GREYBOX_FUEL_TEST.md).
Nothing is modelled new except plain closures: every visible part is F23ci's own geometry, materials, lights and dressing, cut and moved here.
F23ci itself is not modified (it is opened read-only and the result is saved under a new name). Unreviewed: F23ci's 99 review does not carry over.

Module frame as F23ci (F01 refinery door at (0, 0), outward -Y). What changes:
  1. North part removed (y > 14.0): the service bypass loop, the plant header with S01, the clean port S02, the delivery leg and the reactor adapter with F02.
     A concrete exterior wall closes the cut (x -2.54..16.74); the two openings left in the turn chambers (bypass mouth x -1.2..1.2 and delivery mouth
     x 12..16.4) become shallow alcoves backed by copies of the corridor's own lined wall bay (Wall_W12), turned to face south.
  2. New exit F02E on the east turn's east wall (x 16.4): the corridor's own waste-transfer door assembly (frame, header, leaves, roof closure; it stood
     on the same wall plane at y 14.62..17.38) is moved 7.55 m south to y 7.07..9.83 and relabelled. The wall lining and concrete are split around it
     (capped jambs). To make room, the wall's dressing slides north along the same wall: the hood header +1.50, the extraction collector +1.06,
     its inspection practical +1.50, the junction box group +0.69, the distribution board group +1.01, the east-turn practical +2.10. Removed with
     the delivery leg: the waste-bay sign, the waste handoff lettering, the seal and receipt station and the delivery cable ladder.
  3. Entry leg shortened by one wall-panel bay: the slab y 2.68..4.15 (1.47 m, the panel seams of both entry walls) is removed and everything north of
     it moves 1.47 m south. Long parts (walls, floor, ceiling cassettes, cable ladder, dry-air main, freight paint) are cut on the two planes and rejoined;
     props are never sliced: a prop that reaches into the slab moves whole to the north side.
Result: F02E exterior face at module (16.74, 6.98), outward +X, clear 2.38 x 3.0 m; F01 unchanged. Writes <output>.json with counts and ports."""
import bpy, bmesh, sys, os, json, math, hashlib
from mathutils import Vector, Matrix

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SRC = a[a.index('--source') + 1] if '--source' in a else os.path.join(ROOT, 'sections/fuel-corridor/production/checkpoints/fuel_full_F23ci.blend')
OUT = a[a.index('--output') + 1] if '--output' in a else os.path.join(ROOT, 'sections/facility-assembly/sources/fuel-corridor/module_short_S1.blend')
CUT_N = 14.0                      # remove y > CUT_N
SLAB = (2.68, 4.15)               # entry slab removed (panel seams: west wall step 1.5 from 1.2, east wall step 1.45 from 1.2)
DOOR_DY = 7.07 - 14.62            # waste-transfer assembly to the east turn's east wall
DOOR_Y = (7.07, 9.83, 3.34)       # frame y range and top on the east wall, before the entry cut

src_hash = hashlib.sha256(open(SRC, 'rb').read()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=SRC)
sc = bpy.context.scene
STRUCT = ('Wall_', 'FC | Wall_', 'Floor', 'FC | Floor', 'Ceiling', 'FC | Ceiling', 'FC | Freight paint', 'FC | Entry cable ladder', 'FC | Entry dry-air main')
log = {'removed': 0, 'cut': [], 'moved': [], 'deleted_named': []}

# 0. world transforms baked onto unparented objects (so every edit below is in the module frame)
mws = {o.name: o.matrix_world.copy() for o in bpy.data.objects}
for o in bpy.data.objects:
    if o.parent: o.parent = None
for o in bpy.data.objects: o.matrix_world = mws[o.name]
for o in bpy.data.objects:
    if o.type == 'MESH' and o.data.users > 1: o.data = o.data.copy()
# a full-height copy of the corridor's own Wall_W12 lined bay (y 13.18..18.02), kept for the alcove backs before the north cut shortens it
_w12 = next((o for o in bpy.data.objects if o.name.startswith('FC | Wall_W12_0_13.2')), None)
W12_MESH = _w12.data.copy() if _w12 else None
if W12_MESH: W12_MESH.transform(_w12.matrix_world)
W12_MODS = [m.type for m in _w12.modifiers] if _w12 else []

def bb(o):
    """Module-frame box from the actual vertices (bound_box goes stale after the mesh edits below until a depsgraph update)."""
    if o.type == 'MESH' and len(o.data.vertices):
        import numpy as np
        co = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        M = np.array(o.matrix_world, np.float32); w = co @ M[:3, :3].T + M[:3, 3]
        return Vector(w.min(0).tolist()), Vector(w.max(0).tolist())
    if o.type in ('CURVE', 'FONT'):
        q = [o.matrix_world @ Vector(c) for c in o.bound_box]
    else: q = [o.matrix_world.translation]
    return Vector([min(p[i] for p in q) for i in range(3)]), Vector([max(p[i] for p in q) for i in range(3)])

def kill(o):
    log['removed'] += 1; bpy.data.objects.remove(o, do_unlink=True)

def to_world_mesh(o):
    """Mesh data in the module frame with an identity matrix (curves and text become meshes)."""
    if o.type != 'MESH':
        dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); me.transform(o.matrix_world)
        n = bpy.data.objects.new(o.name, me)
        for c in o.users_collection: c.objects.link(n)
        bpy.data.objects.remove(o, do_unlink=True); n.name = n.name; return n
    o.data.transform(o.matrix_world); o.matrix_world = Matrix.Identity(4); return o

def clip(o, planes):
    """Keep the part of mesh o on the kept side of each (axis, value, keep 'lo' or 'hi'). Returns False when nothing is left."""
    bm = bmesh.new(); bm.from_mesh(o.data)
    for ax, v, keep in planes:
        co = [0.0, 0.0, 0.0]; co[ax] = v; no = [0.0, 0.0, 0.0]; no[ax] = 1.0
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=co, plane_no=no, clear_outer=(keep == 'lo'), clear_inner=(keep == 'hi'))
    ok = len(bm.faces) > 0; bm.to_mesh(o.data); bm.free(); o.data.update(); return ok

def move(o, dy):
    o.matrix_world = Matrix.Translation((0, dy, 0)) @ o.matrix_world

def named(prefix): return [o for o in bpy.data.objects if o.name.startswith(prefix)]

# 1. the east wall: dressing slides north, the waste-transfer assembly becomes the east exit
for prefix, dy in (('FC | East extraction service header', 1.50), ('FC | East extraction collector', 1.06), ('FC | Type EXTRACT / 03', 1.06),
                   ('FC | Extraction inspection practical', 1.50), ('FC | East-turn practical', 2.10), ('FC | Process distribution junction box', 0.69),
                   ('FC | Type JB / 04', 0.69), ('FC | Process retained junction leads', 0.69), ('FC | East electrical distribution', 1.01), ('FC | East distribution feed', 1.01)):
    for o in named(prefix): move(o, dy); log['moved'].append((o.name, dy))
for prefix in ('FC | Waste bay identification', 'FC | Type WASTE / HANDOFF', 'FC | Waste seal and receipt station', 'FC | Waste sealing task practical',
               'FC | Type SEAL / RECEIPT', 'FC | Type B / 017.001', 'FC | Type B / 017.002', 'FC | Delivery cable ladder'):
    for o in named(prefix): log['deleted_named'].append(o.name); kill(o)
door = [o for o in bpy.data.objects if o.name.startswith(('FC | Waste transfer', 'FC | Type WASTE / S03'))]
for o in door:
    move(o, DOOR_DY); o.name = o.name.replace('Waste transfer', 'Reactor transfer')
t = bpy.data.objects.get('FC | Type WASTE / S03')
if t and t.type == 'FONT': t.data.body = 'REACTOR / F02'; t.name = 'FC | Type REACTOR / F02'
log['door_objects'] = [o.name for o in door]
# the east wall lining and concrete split around the door (pieces beside the opening and a lintel above it; closed meshes capped)
y0, y1, zt = DOOR_Y
for o in list(bpy.data.objects):
    if o.name.startswith(('FC | Wall_E16.4_0_7', 'Wall_E16.4_0_7')) and o.type == 'MESH':
        base = to_world_mesh(o); keep = []
        for planes in ([(1, y0, 'lo')], [(1, y1, 'hi')], [(1, y0, 'hi'), (1, y1, 'lo'), (2, zt, 'hi')]):
            p = base.copy(); p.data = base.data.copy()
            for c in base.users_collection: c.objects.link(p)
            if clip(p, planes):
                bm = bmesh.new(); bm.from_mesh(p.data); e = [x for x in bm.edges if x.is_boundary]
                if e and base.name.endswith('_concrete'): bmesh.ops.holes_fill(bm, edges=e, sides=0)
                bm.to_mesh(p.data); bm.free(); keep.append(p.name)
            else: bpy.data.objects.remove(p, do_unlink=True)
        log['cut'].append((base.name, 'east door', keep)); bpy.data.objects.remove(base, do_unlink=True)

# 2. the north part goes
for o in list(bpy.data.objects):
    if o.type in ('CAMERA',): continue
    lo, hi = bb(o)
    if lo.y >= CUT_N - 1e-4: kill(o); continue
    if hi.y <= CUT_N + 1e-4 or o.type not in ('MESH', 'CURVE', 'FONT'): continue
    long_part = o.name.startswith(STRUCT) or (hi.y - lo.y) > 2.0
    if not long_part:
        if (lo.y + hi.y) / 2 > CUT_N: kill(o)
        continue
    m = to_world_mesh(o)
    if clip(m, [(1, CUT_N, 'lo')]): log['cut'].append((m.name, 'north', None))
    else: kill(m)
for cam in [o for o in bpy.data.objects if o.type == 'CAMERA' and o.matrix_world.translation.y > CUT_N]: kill(cam)

# closures: exterior concrete across the whole cut, lined alcove backs facing south (copies of the corridor's own Wall_W12 lined bay, turned -90 degrees)
conc_src = next(o for o in bpy.data.objects if o.name.startswith('Wall_S7_1_10_concrete'))
arch = conc_src.users_collection[0]
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts: v.co.x = -2.54 if v.co.x < 0 else 16.74; v.co.y = CUT_N if v.co.y < 0 else CUT_N + 0.30; v.co.z = 0.0 if v.co.z < 0 else 4.62
me = bpy.data.meshes.new('Wall_N14_closure_concrete'); bm.to_mesh(me); bm.free()
for mt in conc_src.data.materials: me.materials.append(mt)
cl = bpy.data.objects.new('Wall_N14_closure_concrete', me); arch.objects.link(cl)
for md in conc_src.modifiers:
    n = cl.modifiers.new(md.name, md.type)
    for k in ('width', 'segments', 'limit_method', 'keep_sharp', 'weight', 'mode'):
        if hasattr(md, k):
            try: setattr(n, k, getattr(md, k))
            except Exception: pass
lin_src = next((o for o in bpy.data.objects if o.name.startswith('FC | Wall_W12_0_13.2')), None)
log['lining_source'] = lin_src.name if lin_src else None
for tag, x0, x1, ztop in (('delivery', 12.0, 16.4, 4.41), ('bypass', -1.2, 1.2, 3.01)):
    if not W12_MESH: break
    p = bpy.data.objects.new('FC | Wall_N14_alcove_' + tag, W12_MESH.copy()); arch.objects.link(p)
    for t_ in W12_MODS: p.modifiers.new(t_.lower(), t_)
    clip(p, [(1, 13.18 + (x1 - x0), 'lo'), (2, ztop, 'lo')])
    # (x, y) -> (y + d, -x + c): the lined face (module x 12.19) lands on y 13.97 facing south, the bay's start (y 13.18) on x0
    c = 13.97 + 12.19; dd = x0 - 13.18
    p.data.transform(Matrix.Translation((dd, c, 0)) @ Matrix(((0, 1, 0, 0), (-1, 0, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))))
    p.data.update(); log['cut'].append((p.name, 'alcove back', [x0, x1]))

# port marker for the new exit
e = bpy.data.objects.new('IF_PORTAL_F02E_REACTOR', None); e.empty_display_type = 'ARROWS'; e.location = (16.74, (y0 + y1) / 2, 0.0); e.rotation_euler = (0, 0, 0)
e['port'] = 'F02E'; e['outward'] = '+X'; e['clear_w'] = 2.38; e['clear_h'] = 3.0
next(c for c in bpy.data.collections if c.name == '07_Runtime_handoff').objects.link(e)

# 3. entry slab out, everything north of it 1.47 m south
s0, s1 = SLAB; dS = s1 - s0
for o in list(bpy.data.objects):
    lo, hi = bb(o)
    if lo.y >= s1 - 1e-4: move(o, -dS); continue
    if hi.y <= s0 + 1e-4: continue
    if o.type in ('MESH', 'CURVE', 'FONT') and (o.name.startswith(STRUCT) or (lo.y < s0 and hi.y > s1)):
        m = to_world_mesh(o); north = m.copy(); north.data = m.data.copy()
        for c in m.users_collection: c.objects.link(north)
        ok_s = clip(m, [(1, s0, 'lo')]); ok_n = clip(north, [(1, s1, 'hi')])
        if ok_n: move(north, -dS); north.name = m.name + ' N'
        else: bpy.data.objects.remove(north, do_unlink=True)
        if not ok_s: bpy.data.objects.remove(m, do_unlink=True)
        log['cut'].append((o.name if ok_s else '(south part empty)', 'entry slab', None)); continue
    # a prop or light reaching into the slab moves whole to the north side, abutting the cut
    if (lo.y + hi.y) / 2 >= s0: move(o, (s0 - lo.y) if lo.y > s0 else -dS)
    else: move(o, min(0.0, s0 - hi.y))

for o in bpy.data.objects: o.select_set(False)
bpy.context.view_layer.update()       # without it the depsgraph is stale after the edits and the count misses modifiers (1.13 M counted vs 1.65 M)
dg = bpy.context.evaluated_depsgraph_get(); tris = 0
for o in bpy.data.objects:
    if o.type in ('MESH', 'CURVE', 'FONT'):
        try:
            me = o.evaluated_get(dg).to_mesh(); me.calc_loop_triangles(); tris += len(me.loop_triangles); o.evaluated_get(dg).to_mesh_clear()
        except Exception: pass
lo = Vector((1e9,) * 3); hi = Vector((-1e9,) * 3)
for o in bpy.data.objects:
    if o.type == 'MESH':
        l, h = bb(o); lo = Vector(map(min, lo, l)); hi = Vector(map(max, hi, h))
bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
rep = dict(source=os.path.relpath(SRC, ROOT), source_sha256=src_hash, output=os.path.relpath(OUT, ROOT), objects=len(bpy.data.objects), evaluated_triangles=tris,
           bounds=[[round(v, 3) for v in lo], [round(v, 3) for v in hi]], ports={'F01_REFINERY': dict(centre=[0, 0, 0], outward='-Y', clear=[2.6, 3.0]),
           'F02E_REACTOR': dict(centre=[16.74, round((y0 + y1) / 2 - dS, 3), 0], outward='+X', clear=[2.38, 3.0])},
           removed=log['removed'], moved=log['moved'], deleted_named=log['deleted_named'], cut=log['cut'][:200], door_objects=log['door_objects'], lining_source=log['lining_source'])
json.dump(rep, open(OUT + '.json', 'w'), indent=1)
print('SHORT corridor saved', OUT, 'objects', len(bpy.data.objects), 'triangles', tris, 'F02E at', rep['ports']['F02E_REACTOR']['centre'])
