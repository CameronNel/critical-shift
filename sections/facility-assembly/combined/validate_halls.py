"""Repeatable audit of the combined map's hall network. Run on the built scene (about 10 minutes on the cloud container):

    blender --background --disable-autoexec -noaudio combined_map.blend --python validate_halls.py -- validation/halls_report.json

For every hall in build_combined_map.LINKS it records: a ray walk along the centre line at three lateral offsets and three heights (0.5 m steps, rays one step long, so a hit is
an obstruction on that line), sphere rays from four points inside the hall (a ray that escapes means a gap to the outside), and junction probes through each branch opening.
Then centre-line clearance between every pair of halls away from junctions, and clearance of each hall against the measured room footprints away from its ends.
It also counts evaluated triangles per room instance. This is geometry evidence only: no player capsule, no door state, no lighting, no Unity. Unreviewed."""
import sys, os, json, math, random, bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_combined_map as BM, reactor_links as R
from mathutils import Vector
out = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else 'halls_report.json'
for o in bpy.data.objects:
    if 'haze' in o.name.lower(): o.hide_viewport = True          # volumes would be hit by the rays
dg = bpy.context.evaluated_depsgraph_get(); sc = bpy.context.scene
random.seed(4)
BOXES = {'turbine': (-4.52, 10.25, 16.64, 42.4), 'electrical': (14.0, 28.3, 26.0, 43.22), 'waste': (27.68, 46.7, -31.6, -17.7), 'cooling': (-57.4, -44.1, -24.8, -13.2), 'hall': (-11.6, 11.6, -11.6, 11.6),
         'concourse': (-11.1, 6.15, -19.9, -14.5), 'fuel_corridor': (-27.9, -4.9, -43.6, -19.6), 'spine': (5.85, 10.15, -48, -14.5), 'medical': (26, 38.4, -75.5, -64.8), 'refinery': (-33.8, -18.8, -57.7, -40.3),
         'frontend_hall': (-4, 32, -60, -48), 'dock': (57.9, 76.1, -86.2, -71.8)}      # measured outer plan bounds, COMBINED_MAP.md
P = {k: R.Path(R.fillet(L['pts'], L['r'])) for k, L in BM.LINKS.items() if all(r in BM.INCLUDED or True for r in L.get('requires', ()))}
report = {'halls': {}, 'pairs': [], 'rooms': {}, 'triangles': {}}
def hit(o, d, dist): 
    ok, loc, n, i, ob, m = sc.ray_cast(dg, Vector(o), Vector(d).normalized(), distance=dist); return (ok, ob.name[:30] if ok else None, tuple(round(c, 2) for c in loc) if ok else None)
for k, L in BM.LINKS.items():
    p = P[k]; w = L.get('w', 5.0); h = L.get('h', 5.0); blocked = []
    lats = (-0.9, 0.0, 0.9) if w > 3 else (-0.5, 0.0, 0.5)
    for s in [i * 0.5 for i in range(int(p.length / 0.5))]:
        a, d, n = p.at(s); b = p.at(s + 0.5)[0]
        for lat in lats:
            for z in (0.4, 1.2, min(2.2, h - 0.4)):
                o = Vector((a.x + n.x * lat, a.y + n.y * lat, z)); dv = Vector((b.x + n.x * lat, b.y + n.y * lat, z)) - o
                ok, name, loc = hit(o, dv, dv.length * 0.98)
                if ok: blocked.append((round(s, 1), lat, z, name))
    esc = 0; n_ = 0
    for s in [p.length * f for f in (0.2, 0.4, 0.6, 0.8)]:
        c = p.at(s)[0]
        for i in range(250):
            z = random.uniform(-0.7, 0.95); t = random.uniform(0, 6.2832); rr = math.sqrt(1 - z * z); n_ += 1
            if not hit((c.x, c.y, 1.6), (rr * math.cos(t), rr * math.sin(t), z), 500)[0]: esc += 1
    junc = []
    for t in ('into', 'outof'):
        if t in L:
            end = p.at(p.length if t == 'into' else 0)
            e, d = end[0], end[1] * (1 if t == 'into' else -1)
            for lat in (-0.5, 0, 0.5):
                nn = Vector((-d.y, d.x)); a = e - d * 1.5 + nn * lat; b = e + d * 2.0 + nn * lat
                ok, name, loc = hit((a.x, a.y, 1.4), (b.x - a.x, b.y - a.y, 0), (b - a).length)
                junc.append(dict(to=L[t][0], lat=lat, clear=not ok, blocked_by=name))
    report['halls'][k] = dict(length=round(p.length, 1), walk_blocked=len(blocked), walk_blocked_sample=blocked[:5], sphere_escapes=esc, sphere_rays=n_, junction_probes=junc)
    print('HALL', k, 'len', round(p.length, 1), 'walk blocked', len(blocked), 'escapes', esc, '/', n_, 'junctions clear', sum(j['clear'] for j in junc), '/', len(junc), flush=True)
J = [Vector(L[t][2]) for L in BM.LINKS.values() for t in ('into', 'outof') if t in L] + [Vector(p.at(0)[0]) for p in P.values()] + [Vector(p.at(p.length)[0]) for p in P.values()]
keys = list(P)
for i, a in enumerate(keys):
    for b in keys[i + 1:]:
        worst = None; lim = (BM.LINKS[a].get('w', 5.0) + BM.LINKS[b].get('w', 5.0)) / 2 + 0.6
        for s in [x * 0.5 for x in range(int(P[a].length / 0.5) + 1)]:
            pa = P[a].at(s)[0]
            for u in [x * 0.5 for x in range(int(P[b].length / 0.5) + 1)]:
                pb = P[b].at(u)[0]; dd = (pa - pb).length
                if dd < lim and not any((pa - j).length < 4.5 or (pb - j).length < 4.5 for j in J) and (worst is None or dd < worst[0]): worst = (round(dd, 2), round(s, 1), round(u, 1))
        if worst: report['pairs'].append(dict(a=a, b=b, closest=worst))
for k, p in P.items():
    half = BM.LINKS[k].get('w', 5.0) / 2 + 0.3; res = {}
    for s in [i * 0.25 for i in range(int(p.length / 0.25) + 1)]:
        if s < 3.2 or s > p.length - 3.2: continue                    # the ends meet rooms by design
        pos = p.at(s)[0]
        for bn, (x0, x1, y0, y1) in BOXES.items():
            d = math.hypot(max(x0 - pos.x, 0, pos.x - x1), max(y0 - pos.y, 0, pos.y - y1)) - half
            if d < res.get(bn, (99, 0))[0]: res[bn] = (round(d, 2), round(s, 1))
    report['rooms'][k] = {bn: v for bn, v in sorted(res.items(), key=lambda kv: kv[1][0])[:3]}
tri = {}
for inst in dg.object_instances:
    o = inst.object
    if o.type not in ('MESH', 'CURVE', 'FONT') or o.hide_render: continue
    try: m = o.to_mesh()
    except Exception: continue
    key = inst.parent.name if inst.parent else 'scene'
    if o.name.startswith(('CONNECTOR', 'HALL')) or key == 'scene' and False: key = 'connectors'
    tri[key] = tri.get(key, 0) + sum(len(q.vertices) - 2 for q in m.polygons); o.to_mesh_clear()
report['triangles'] = dict(sorted(tri.items(), key=lambda kv: -kv[1])); report['triangles_total'] = sum(tri.values())
ok = all(v['walk_blocked'] == 0 and v['sphere_escapes'] == 0 and all(j['clear'] for j in v['junction_probes']) for v in report['halls'].values()) and not report['pairs']
report['summary'] = 'PASS (geometry audit only)' if ok else 'ISSUES: see halls / pairs'
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True); json.dump(report, open(out, 'w'), indent=1)
print('VALIDATE', report['summary'], 'triangles', report['triangles_total'])
