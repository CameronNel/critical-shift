"""Check actual gantry return rails/posts and the fixed-rail access opening.

Run through rh_stage_runner.py -- rh_gantry_guard_audit.py SCENE REPORT.
The finite saved-mesh inventory catches the remote components lost by the old
gate Boolean; it complements contact registrations rather than replacing them.
"""
import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

source, output = map(Path, sys.argv[sys.argv.index('--') + 1:][:2])
bpy.ops.wm.open_mainfile(filepath=str(source))
bpy.context.scene.frame_set(1)
ob = bpy.data.objects['RH pool platform YELLOW']
ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh = ev.to_mesh()
tree = BVHTree.FromPolygons(
    [ev.matrix_world @ v.co for v in mesh.vertices],
    [tuple(p.vertices) for p in mesh.polygons], all_triangles=False)
ev.to_mesh_clear()
rows = []

def sample(label, point, present=True):
    for sign in (-1, 1):
        direction = Vector((sign, 0, 0))
        hit, normal, face, distance = tree.ray_cast(Vector(point), direction, .032)
        passed = (hit is not None and .014 <= distance <= .028
                  and normal.dot(direction) > .85) if present else hit is None
        rows.append(dict(assembly=label, point=point, direction=tuple(direction),
                         expected_present=present, hit_face=face,
                         distance_m=distance if hit is not None else None,
                         pass_check=passed))

for x in (-7.0, -2.8, 2.8):
    for z in (14.42, 14.95):
        for y in (.86, 1.10, 1.30):
            sample('non-gate end return', (x, y, z))

for x in (-7.0, -6.16, -5.32, -4.48, -3.64, -2.8,
          2.8, 3.64, 4.48, 5.32, 6.16, 7.0):
    for z in (14.10, 14.65):
        sample('longitudinal rail post', (x, 1.42, z))
for x in (-7.0, -2.8, 2.8, 7.0):
    for z in (14.10, 14.65):
        sample('end-return post', (x, .74, z))

for z in (14.42, 14.95):
    for y in (.777, 1.38):
        sample('gate-adjacent fixed rail stub', (7.0, y, z))
    for y in (.90, 1.10, 1.25):
        sample('opening free of fixed return rail', (7.0, y, z), False)

failures = [r for r in rows if not r['pass_check']]
report = dict(source=str(source), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              scope='Finite actual platform-mesh inventory and fixed-rail gate opening; '
                    'the separate movable gate, global collisions and animation are outside this check.',
              samples=len(rows), failures=failures, records=rows, pass_check=not failures)
output.write_text(json.dumps(report, indent=2)+'\n')
print('GANTRY_GUARD '+('PASS' if not failures else 'FAIL')+' '+str(len(failures)), flush=True)
assert not failures, 'Missing gantry guard component or obstructed fixed-rail opening'
