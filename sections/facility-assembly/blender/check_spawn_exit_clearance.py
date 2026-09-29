"""Read-only sampled clearance through the established spawn service exit."""
import bpy, hashlib, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[3]
src = Path(bpy.data.filepath)
before = hashlib.sha256(src.read_bytes()).hexdigest()
dg = bpy.context.evaluated_depsgraph_get()
trees = []
for inst in dg.object_instances:
    o = inst.object
    if o.type != 'MESH' or o.hide_render:
        continue
    m = inst.matrix_world
    pts = [m @ Vector(p) for p in o.bound_box]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    if any(hi[i] < a or lo[i] > b for i, (a, b) in enumerate(
            [(-28.8, -27.2), (11.8, 13.2), (.2, 2.3)])):
        continue
    me = o.to_mesh(preserve_all_data_layers=False, depsgraph=dg)
    if me and me.polygons:
        trees.append((o.original.name, BVHTree.FromPolygons(
            [m @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])))
    o.to_mesh_clear()
rows = []
for x in [-28.8, -28, -27.2]:
    for z in [.2, 1, 1.8, 2.3]:
        origin = Vector((x, 13.2, z))
        hits = []
        for name, tree in trees:
            hit, normal, index, distance = tree.ray_cast(origin, Vector((0, -1, 0)), 1.4)
            if hit is not None:
                hits.append(dict(name=name, position=list(hit)))
        rows.append(dict(origin=list(origin), hits=hits))
assert hashlib.sha256(src.read_bytes()).hexdigest() == before
report = dict(source_sha256=before, rays=rows, method='12 sampled rays through existing portal; not navmesh certification')
(root / 'runtime/out/spawn-integration/exit-clearance.json').write_text(json.dumps(report, indent=2))
print('SPAWN_EXIT_CLEARANCE', [r for r in rows if r['hits']], flush=True)
assert not any(r['hits'] for r in rows), 'The sampled service exit rays hit geometry; inspect the report'
