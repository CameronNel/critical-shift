"""Read immutable protected original for planning counters; never save."""
import bpy,json,hashlib
from pathlib import Path
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock')
O=R/'revamp/production/critics/full-c02-technical'
bpy.ops.wm.open_mainfile(filepath=str(R/'module.blend'),load_ui=False)
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
triangles=submeshes=0;materials=set()
for ob in s.objects:
    if ob.type not in {'MESH','FONT','CURVE','SURFACE','META'}:continue
    e=ob.evaluated_get(dg);m=e.to_mesh()
    if m is None:continue
    m.calc_loop_triangles();triangles+=len(m.loop_triangles)
    used={p.material_index for p in m.polygons};submeshes+=len(used)
    for i in used:
        if i<len(e.material_slots) and e.material_slots[i].material:
            materials.add(e.material_slots[i].material.name)
    e.to_mesh_clear()
out={'source':str(R/'module.blend'),'sha256':hashlib.sha256((R/'module.blend').read_bytes()).hexdigest(),
     'scene':s.name,'scene_objects':len(s.objects),'evaluated_triangles':triangles,
     'authoring_material_submeshes':submeshes,'used_material_families':len(materials),'saved':False}
(O/'baseline-planning-counts.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out),flush=True)
