"""Carry the exact R13 face-normal correction into the R12 material cache."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_spawn_material_preview_R12.blend'),load_ui=False)
count=0
for ob in bpy.data.collections['27_MATERIAL_PREVIEW'].objects:
 if ob.type!='MESH':continue
 slots={i for i,m in enumerate(ob.data.materials) if m and m.name=='S01 warm broad-plane exterior stone'}
 for p in ob.data.polygons:
  if p.material_index in slots:p.use_smooth=False;count+=1
s=bpy.context.scene;s.name='FACILITY_SPAWN_MATERIAL_PREVIEW_R13';dest=R/'blender/facility_spawn_material_preview_R13.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
b=json.loads((O/'MATERIAL_PREVIEW_R12.json').read_text());b.update(file=str(dest),revision='R13',parent_cache='facility_spawn_material_preview_R12.blend',rock_flat_faces=count);(O/'MATERIAL_PREVIEW_R13.json').write_text(json.dumps(b,indent=2));print('R13_PREVIEW_SAVED',count,flush=True)
