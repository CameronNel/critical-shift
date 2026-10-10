"""Finite saved-mesh regression for EC header cover faces and twenty bolt heads."""
import bpy, bmesh, sys, json, hashlib, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

source, output = map(Path, sys.argv[sys.argv.index('--')+1:][:2])
bpy.ops.wm.open_mainfile(filepath=str(source))
bpy.context.scene.frame_set(1)
names = ('RH stations south IRON', 'RH stations south STEEL', 'RH refine blind covers STEEL')
trees = {name: BVHTree.FromPolygons(
    [bpy.data.objects[name].matrix_world @ v.co for v in bpy.data.objects[name].data.vertices],
    [list(f.vertices) for f in bpy.data.objects[name].data.polygons]) for name in names}
failures = []
rows = []
registry = json.loads(bpy.context.scene.get('rh_support_registry', '[]'))
for axis_x, sign in ((1.62, -1), (3.48, 1)):
    direction = Vector((-sign, 0, 0))
    samples = [(0, 0)] + [(r*math.cos(2*math.pi*i/64), r*math.sin(2*math.pi*i/64))
                         for r in (.025, .05, .075, .10, .125, .13) for i in range(64)]
    bad = []
    for dy, dz in samples:
        origin = Vector((axis_x+sign*.10, -8.84+dy, .78+dz))
        hits = [(hit[3], name, hit[0]) for name, tree in trees.items()
                if (hit := tree.ray_cast(origin, direction, .2))[0] is not None]
        first = min(hits, default=None, key=lambda h: h[0])
        if first is None or first[1] != names[2] or abs(sign*(first[2].x-axis_x)-.052) > .000002:
            bad.append(dict(sample=[dy,dz], first_object=first[1] if first else None))
    if bad: failures.append('Covered or misplaced blind face at '+str(axis_x))
    records = [r for r in registry if r['owner']=='EC blind cover correction'
               and r['name']=='bolt seats '+str(axis_x)]
    seats = records[0]['anchors'] if len(records)==1 else []
    bolt_errors = []
    if len(seats) != 10: failures.append('Missing ten registered bolt seats at '+str(axis_x))
    for seat in seats:
        origin = Vector((axis_x+sign*.10, seat[1], seat[2]))
        hit = trees[names[1]].ray_cast(origin, direction, .2)
        offset = sign*(hit[0].x-axis_x) if hit[0] is not None else None
        if offset is None or abs(offset-.064)>.000002: bolt_errors.append(dict(seat=seat, front_offset=offset))
    if bolt_errors: failures.append('Buried or misplaced bolt heads at '+str(axis_x))
    rows.append(dict(axis_x=axis_x, face_samples=len(samples), obstructed_or_misplaced=len(bad),
                     bolt_seats=len(seats), bolt_errors=bolt_errors, bad_face_samples=bad[:10]))
bm = bmesh.new(); bm.from_mesh(bpy.data.objects[names[2]].data)
open_edges = sum(not e.is_manifold for e in bm.edges)
volume = bm.calc_volume(signed=True); bm.free()
if open_edges or volume<=0: failures.append('Blind plate mesh is open or inverted')
report = dict(source=str(source), sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              pass_check=not failures, failures=failures, ends=rows,
              plate_open_edges=open_edges, plate_signed_volume=volume,
              scope='Actual saved-mesh first-hit tests on two blind-cover centers (385 rays per end), '
                    'twenty registered bolt-head axes, and plate manifold/volume. '
                    'Registered plate/bolt contact seats are checked by the separate support audit. '
                    'No exhaustive flange collision or fluid-network claim.')
output.write_text(json.dumps(report,indent=2)+'\n')
print('BLIND_COVER', 'PASS 0' if not failures else 'FAIL '+str(len(failures)),flush=True)
if failures: raise SystemExit(1)
