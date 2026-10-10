"""Measure saved cone footprints against actual white arrows and yellow aisle-edge faces.

Run through rh_stage_runner.py -- rh_floor_guidance_audit.py SCENE REPORT.
This finite marking check complements the support and frontal lettering audits.
"""
import json
import hashlib
import sys
from pathlib import Path
import bpy
from mathutils import Vector

source, output = map(Path, sys.argv[sys.argv.index('--') + 1:][:2])
bpy.ops.wm.open_mainfile(filepath=str(source))
bpy.context.scene.frame_set(1)
dg = bpy.context.evaluated_depsgraph_get()

def cross(a, b, p):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])

def hull(points):
    points = sorted(set(points))
    def half(seq):
        result = []
        for p in seq:
            while len(result) >= 2 and cross(result[-2], result[-1], p) <= 0:
                result.pop()
            result.append(p)
        return result
    return half(points)[:-1]+half(reversed(points))[:-1]

def intersection_area(triangle, footprint):
    polygon = triangle
    for a, b in zip(footprint, footprint[1:]+footprint[:1]):
        clipped = []
        if not polygon:
            return 0.0
        prev = polygon[-1]
        dp = cross(a, b, prev)
        for cur in polygon:
            dc = cross(a, b, cur)
            if (dc >= 0) != (dp >= 0):
                t = dp/(dp-dc)
                clipped.append((prev[0]+t*(cur[0]-prev[0]), prev[1]+t*(cur[1]-prev[1])))
            if dc >= 0:
                clipped.append(cur)
            prev, dp = cur, dc
        polygon = clipped
    return abs(sum(a[0]*b[1]-a[1]*b[0] for a, b in zip(polygon, polygon[1:]+polygon[:1])))/2

markings = {'arrow': [], 'lane': []}
for ob in bpy.data.objects:
    if ob.type != 'MESH' or not ob.name.startswith(('RH floor paint chevron ', 'RH floor paint lane ')):
        continue
    family = 'arrow' if ob.name.startswith('RH floor paint chevron ') else 'lane'
    ev = ob.evaluated_get(dg)
    mesh = ev.to_mesh()
    mesh.calc_loop_triangles()
    for tri in mesh.loop_triangles:
        normal = ob.matrix_world.to_3x3() @ tri.normal
        if normal.z > .99:
            points = [ob.matrix_world @ mesh.vertices[i].co for i in tri.vertices]
            markings[family].append([(p.x, p.y) for p in points])
    ev.to_mesh_clear()
assert all(markings.values()), 'Missing directional markings'

records = []
for ob in bpy.data.objects:
    if ob.type != 'MESH' or ob.name not in ('RH stations props cone RUBBER', 'RH refine legacy cones RUBBER', 'RH stations props RUBBER'):
        continue
    ev = ob.evaluated_get(dg)
    mesh = ev.to_mesh()
    adjacency = {v.index: set() for v in mesh.vertices}
    for edge in mesh.edges:
        a, b = edge.vertices
        adjacency[a].add(b)
        adjacency[b].add(a)
    unseen = set(adjacency)
    while unseen:
        stack = [min(unseen)]
        component = set()
        while stack:
            i = stack.pop()
            if i in component:
                continue
            component.add(i)
            stack.extend(adjacency[i]-component)
        unseen.difference_update(component)
        points = [ob.matrix_world @ mesh.vertices[i].co for i in component]
        if ob.name=='RH stations props RUBBER':
            # Historical regrouped candidates: identify the five actual cone
            # base components by their measured dimensions, excluding casters/seats.
            spans=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
            if not (max(p.z for p in points)<.05 and min(p.z for p in points)<.001 and
                    abs(spans[0]-.4012)<.001 and abs(spans[1]-.4012)<.001):
                continue
        assert max(p.z for p in points) < .05, 'Unexpected geometry in cone foot mesh'
        footprint = hull([(p.x, p.y) for p in points])
        areas = {family: sum(intersection_area(tri, footprint) for tri in tris)
                 for family, tris in markings.items()}
        records.append(dict(object=ob.name, footprint=footprint, arrow_overlap_m2=areas['arrow'],
                            lane_overlap_m2=areas['lane'], pass_check=all(a<1e-8 for a in areas.values())))
    ev.to_mesh_clear()
assert len(records) == 8, 'Expected all five station and three legacy cone feet; found '+str(len(records))
records.sort(key=lambda r: (r['object'], min(r['footprint'])))
report = dict(source=str(source), sha256=hashlib.sha256(source.read_bytes()).hexdigest(), scope='All eight cone rubber footprints against saved white directional-arrow and yellow aisle-edge top faces; top surfaces counted once, not a general floor clearance test.',
              records=records, failures=sum(not r['pass_check'] for r in records))
output.write_text(json.dumps(report, indent=2)+'\n')
print('FLOOR_GUIDANCE', 'PASS' if report['failures']==0 else 'FAIL', report['failures'])
