"""Read-only CPU evidence from neighbouring saved files; never saves them."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[sys.argv.index('--')+1]);out.parent.mkdir(parents=True,exist_ok=True)
items=[];dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.context.scene.objects:
    if any(t in o.name.lower() for t in ['main access','d01','power_in','incoming','turbine','portal']):
        row={'name':o.name,'type':o.type,'position':list(o.matrix_world.translation)}
        if o.type in {'MESH','CURVE','FONT'}:
            e=o.evaluated_get(dg);m=e.to_mesh();v=[o.matrix_world@p.co for p in m.vertices]
            if v:row['evaluated_bounds']=[[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]]
            e.to_mesh_clear()
        items.append(row)
f=Path(bpy.data.filepath)
out.write_text(json.dumps({'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'method':'fresh background open, evaluated world-space bounding vertices; no mutation/save','objects':items},indent=2),encoding='utf-8')
print('SURVEY',out,len(items))
