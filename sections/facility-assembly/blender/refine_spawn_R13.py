"""R12 -> R13: expose existing exterior rock planes without moving geometry."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_spawn_concept02_R12.blend'),load_ui=False)
records=[]
for name in ['S01 exterior quarried front material override','S01 exterior upper mountain material override']:
 ob=bpy.data.objects[name];ob.data=ob.data.copy()
 for p in ob.data.polygons:p.use_smooth=False
 records.append({'object':name,'faces':len(ob.data.polygons),'vertices':len(ob.data.vertices),'modifiers':[(m.name,m.type) for m in ob.modifiers],'change':'flat face normals only; positions and topology unchanged'})
s=bpy.context.scene;s.name='FACILITY_SPAWN_CONCEPT02_R13';dest=R/'blender/facility_spawn_concept02_R13.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
b=json.loads((O/'BUILD_R12.json').read_text());b.update(revision='R13',file=str(dest),exterior_rock_shading=records);(O/'BUILD_R13.json').write_text(json.dumps(b,indent=2));print('R13_SAVED',records,flush=True)
