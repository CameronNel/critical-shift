"""Fresh-process, read-only world bounds of a neighbouring saved artifact."""
import bpy,json,sys,hashlib
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]);out.parent.mkdir(parents=True,exist_ok=True)
dg=bpy.context.evaluated_depsgraph_get();rows=[]
for o in bpy.context.scene.objects:
 r={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'position':list(o.matrix_world.translation)}
 if o.type in {'MESH','CURVE','FONT'}:
  e=o.evaluated_get(dg);m=e.to_mesh();v=[o.matrix_world@p.co for p in m.vertices]
  if v:r['bounds']=[[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]]
  e.to_mesh_clear()
 rows.append(r)
f=Path(bpy.data.filepath);out.write_text(json.dumps({'source':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'method':'read-only fresh Blender open; evaluated world vertices; no save','objects':rows},indent=2),encoding='utf-8')
print('SURVEY',out,len(rows))
