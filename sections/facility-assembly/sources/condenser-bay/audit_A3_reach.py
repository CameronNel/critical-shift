"""Reach and headroom audit for the condenser bay (geometric, no engine): can a worker stand somewhere and reach each control?

    blender -b --factory-startup module_aaa_A3.blend --python audit_A3_reach.py [-- --ceiling <module z> --out reach-A3.json]

Model (the same as reach-check.json's, which had no committed tool): a worker 1.75 m tall, shoulder 1.45 m above the standing surface,
arm reach 0.70 m, body radius 0.22 m, 1.75 m headroom. Standing spots are up-facing surfaces (normal z > 0.7) of the floor, stairs and
gallery (objects in '01 Architecture', '02 Access D01' and '03 Stairs and gallery'), sampled every 0.10 m. A control is reachable when
some spot's shoulder lies within 0.70 m of it with a clear line of sight (the first thing the sight line meets is the control itself or lies
within 12 cm of the target: a hand on the control's housing). `--ceiling` lowers the roof for the headroom test (the map's roof underside, in module coordinates).
Exit code 1 when any contract hook is out of reach or the gallery headroom is under 2.0 m.
"""
import bpy, sys, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
CEIL = float(a[a.index('--ceiling') + 1]) if '--ceiling' in a else None
OUT = a[a.index('--out') + 1] if '--out' in a else None
SHOULDER, ARM, BODY, HEAD = 1.45, 0.70, 0.22, 1.75
WALKABLE = ('01 Architecture', '02 Access D01', '03 Stairs and gallery')
sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()

verts, tris, owner = [], [], []
walk_objs = set()
for o in sc.objects:
    if o.type not in ('MESH', 'CURVE', 'FONT') or o.hide_render: continue
    ev = o.evaluated_get(dg); me = ev.to_mesh(); M = o.matrix_world; base = len(verts)
    verts.extend(M @ v.co for v in me.vertices)
    for p in me.polygons:
        vs = list(p.vertices)
        for k in range(1, len(vs) - 1): tris.append((base + vs[0], base + vs[k], base + vs[k + 1])); owner.append(o.name)
    ev.to_mesh_clear()
    if any(c.name in WALKABLE for c in o.users_collection): walk_objs.add(o.name)
bvh = BVHTree.FromPolygons(verts, tris)
def cast(o, d, dist):
    loc, nrm, idx, dd = bvh.ray_cast(Vector(o), Vector(d).normalized(), dist)
    return (loc, nrm, owner[idx], dd) if loc is not None else None

# standing spots
xs = [x * 0.10 for x in range(-22, 100)]; ys = [y * 0.10 for y in range(-27, 97)]
spots = []
for x in xs:
    for y in ys:
        z = 6.2
        for _ in range(8):
            h = cast((x, y, z), (0, 0, -1), z + 1.0)
            if h is None: break
            loc, nrm, name, _ = h; z = loc.z - 0.005
            if nrm.z < 0.7 or name not in walk_objs: continue
            f = loc.z
            up = cast((x, y, f + 0.03), (0, 0, 1), HEAD)
            if up is not None: continue
            if CEIL is not None and CEIL - f < HEAD: continue
            if any(cast((x, y, f + hz), (math.cos(t), math.sin(t), 0), BODY) for hz in (0.35, 1.0, 1.6) for t in [k * math.pi / 4 for k in range(8)]): continue
            ceil = cast((x, y, f + 0.03), (0, 0, 1), 10.0); room = (ceil[0].z if ceil else 99.0)
            if CEIL is not None: room = min(room, CEIL)
            spots.append((x, y, f, room - f, name))
print('REACH standing spots', len(spots))

def reach(target, own=None):
    t = Vector(target); best = (9.9, None)
    for x, y, f, _, _ in spots:
        s = Vector((x, y, f + SHOULDER)); d = (t - s).length
        if d >= best[0] or d > ARM + 0.6: continue
        h = cast(s, t - s, d + 0.02)
        if h is not None and (t - h[0]).length > 0.12 and h[2] != own: continue
        best = (d, (round(x, 2), round(y, 2), round(f, 2)))
    return best

hooks = {o.name: o.matrix_world.translation.copy() for o in sc.objects if o.name.startswith('INTERACT_')}
report = {'model': dict(shoulder=SHOULDER, arm=ARM, body=BODY, headroom=HEAD, ceiling=CEIL), 'spots': len(spots), 'hooks': {}, 'parts': {}}
bad = []
for n, p in sorted(hooks.items()):
    d, at = reach(p); ok = d <= ARM
    report['hooks'][n] = dict(target=[round(v, 3) for v in p], reach_m=round(d, 3), from_spot=at, reachable=ok)
    print('REACH %-24s %.2f m %s' % (n, d, 'ok' if ok else 'OUT OF REACH')); bad += [] if ok else [n]
for n in ('WB west vent wheel rim', 'WB east vent wheel rim', 'A3 CW isol SUPPLY chain loop bottom', 'A3 CW isol RETURN chain loop bottom', 'OP trip mushroom'):
    o = sc.objects.get(n)
    if o is None: continue
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]; c = sum(pts, Vector()) / 8
    d, at = min((reach(p, n) for p in pts + [c]), key=lambda r: r[0])
    report['parts'][n] = dict(reach_m=round(d, 3), from_spot=at, reachable=d <= ARM); print('REACH part %-34s %.2f m' % (n, d))
gal = [r for r in spots if r[2] > 3.5]
if gal:
    lo = min(gal, key=lambda r: r[3])
    report['gallery'] = dict(spots=len(gal), deck_z=round(sum(r[2] for r in gal) / len(gal), 3), min_headroom_m=round(lo[3], 3), at=[round(v, 2) for v in lo[:3]])
    print('REACH gallery spots %d, min headroom %.3f m at %s' % (len(gal), lo[3], [round(v, 2) for v in lo[:3]]))
    if lo[3] < 2.0: bad.append('gallery headroom')
report['ok'] = not bad; report['problems'] = bad
if OUT: open(OUT, 'w').write(json.dumps(report, indent=1) + '\n')
print('REACH', 'OK' if not bad else 'FAILED: %s' % bad)
if bad: raise SystemExit(1)
