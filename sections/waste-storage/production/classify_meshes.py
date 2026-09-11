"""Read-only seam classification; run with Blender against saved artifact."""
import bpy, bmesh, json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
dg=bpy.context.evaluated_depsgraph_get(); rows=[]
for ob in bpy.context.scene.objects:
    if ob.type not in {'MESH','CURVE','FONT'}: continue
    ev=ob.evaluated_get(dg); mesh=ev.to_mesh(); bm=bmesh.new(); bm.from_mesh(mesh)
    before=sum(e.is_boundary for e in bm.edges)
    if before:
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
        after=sum(e.is_boundary for e in bm.edges)
        role='coincident tessellation seams' if not after else ('text face' if ob.type=='FONT' else 'open surface: inspect')
        rows.append({'name':ob.name,'type':ob.type,'boundary_before_weld':before,'boundary_after_1um_weld':after,'classification':role})
    bm.free(); ev.to_mesh_clear()
out=root/'production/validation'/bpy.context.scene.get('revision','unknown')/'mesh_classification.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({'read_only':True,'temporary_mesh_weld_m':.000001,'objects':rows},indent=2))
print('REMAINING_OPEN',[(r['name'],r['boundary_after_1um_weld']) for r in rows if r['boundary_after_1um_weld'] and r['type']!='FONT'])
