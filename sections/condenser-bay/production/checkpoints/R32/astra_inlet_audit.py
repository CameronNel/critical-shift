"""Test the saved local exhaust path into the vessel, beyond the slab bore."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();rows=[]
for x in [2.15,3,3.85]:
    for y in [3.60,4.05,4.50]:
        hit,point,normal,index,obj,matrix=s.ray_cast(deps,Vector((x,y,5.50)),Vector((0,0,-1)),distance=2.50)
        rows.append({'xy':[x,y],'ok':not hit,'blocker':obj.name if hit else None,'hit_z':point.z if hit else None})
rev=str(s.get('source_revision'));root=Path(__file__).resolve().parent.parent
report={'revision':rev,'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'scope':'Nine saved-scene downward rays from z5.50 to z3.00 inside the local inlet. Verifies an open path into the vessel volume, not thermodynamics or a remote facility loop.',
        'status':'PASS' if all(r['ok'] for r in rows) else 'FAIL','samples':rows}
out=root/'production/validation'/rev/'exhaust-plenum-continuity.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2))
print('EXHAUST_PLENUM_CONTINUITY',rev,report['status'],rows,flush=True)
sys.exit(0 if report['status']=='PASS' else 1)
