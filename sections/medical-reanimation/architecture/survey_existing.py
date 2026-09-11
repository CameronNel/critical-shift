"""Read only: evaluate the existing saved Medical scene, never save or import."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();rows=[]
for o in s.objects:
    r={'name':o.name,'type':o.type,'collections':[c.name for c in o.users_collection],'parent':o.parent.name if o.parent else None,'location':list(o.location),'rotation':list(o.rotation_euler)}
    if o.type in {'MESH','CURVE','FONT'}:
        e=o.evaluated_get(dg);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices]
        if v:r.update(min=[min(p[k] for p in v) for k in range(3)],max=[max(p[k] for p in v) for k in range(3)])
        e.to_mesh_clear()
    if o.type=='FONT':r['text']=o.data.body
    rows.append(r)
report={'source':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'revision':s.get('revision'),'objects':rows,'count':len(rows),'collections':[c.name for c in s.collection.children],'read_only':True}
(R/'existing-saved-survey.json').write_text(json.dumps(report,indent=2));print('SURVEY',report['revision'],report['count'],report['collections'])
