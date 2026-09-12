"""Read-only evaluated detail witness for newly detected F02 hood obstruction."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
base=Path(__file__).resolve().parent
snap=base.parent/'checkpoints/eng03'
dg=bpy.context.evaluated_depsgraph_get()
report={'blend_sha256':hashlib.sha256((snap/'Fuel_Corridor.blend').read_bytes()).hexdigest(),'objects':[],'saved':False,'scope':'Two evaluated hood meshes only; transverse witness is not a global minimum or complete assembly support test.'}
for name,direction in [('Reactor_left_key_hood',(-1,0,0)),('Reactor_right_key_hood',(1,0,0))]:
    ob=bpy.data.objects[name];eo=ob.evaluated_get(dg);mesh=eo.to_mesh()
    try:
        vs=[eo.matrix_world@v.co for v in mesh.vertices];polys=[tuple(p.vertices) for p in mesh.polygons]
        b=[[round(f(v[i] for v in vs),7) for i in range(3)] for f in [min,max]]
        tree=BVHTree.FromPolygons(vs,polys);point,normal,index,distance=tree.ray_cast(Vector((14.2,22.8,2.575)),Vector(direction),4)
        report['objects'].append({'object':name,'parent':ob.parent.name,'bounds_xyz':b,'ray_origin':[14.2,22.8,2.575],'ray_hit':[round(v,7) for v in point] if point is not None else None,'ray_distance':distance,'collision_policy':ob.get('collision_handoff')})
    finally:eo.to_mesh_clear()
report['witness_clear_width_m']=sum(o['ray_distance'] for o in report['objects'])
(base/'astra-eng03-branch-hood-evidence.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
