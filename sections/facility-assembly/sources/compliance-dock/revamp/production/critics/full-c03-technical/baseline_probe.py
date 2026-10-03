import bpy,json
from pathlib import Path
p=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock')
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();tris=0;subs=0;used=set();objects=[]
for o in s.objects:
    row={'name':o.name,'matrix':[list(x) for x in o.matrix_world],'dimensions':list(o.dimensions)}
    if o.type in {'MESH','CURVE','FONT','SURFACE','META'}:
        ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();tris+=len(m.loop_triangles);idx={f.material_index for f in m.polygons};subs+=len(idx);used.update(m.materials[i] for i in idx if i<len(m.materials) and m.materials[i]);ev.to_mesh_clear()
    objects.append(row)
r={'triangles':tris,'material_submeshes':subs,'used_material_datablocks':len(used),'objects':objects}
(p/'revamp/production/critics/full-c03-technical/baseline-probe.json').write_text(json.dumps(r,indent=2));print('BASELINE',tris,subs,len(used),len(objects))
