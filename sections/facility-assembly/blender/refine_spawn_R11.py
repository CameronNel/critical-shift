"""R10 -> R11: material-only finish of visible exterior quarried rock face."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_spawn_concept02_R10.blend'),load_ui=False)
m=bpy.data.materials['S01 warm broad-plane exterior stone'];changed=[]
for c in list(bpy.data.collections):
 if not c.name.startswith('EXT_LIGHTING_'):continue
 for ob in list(c.objects):
  if ob.name=='CSM_Mountain_quarried_front':
   cp=ob.copy();cp.name='S01 exterior quarried front material override';c.objects.unlink(ob);c.objects.link(cp)
   for sl in cp.material_slots:sl.link='OBJECT';sl.material=m
   changed.append(cp.name)
s=bpy.context.scene;s.name='FACILITY_SPAWN_CONCEPT02_R11';dest=R/'blender/facility_spawn_concept02_R11.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
b=json.loads((O/'BUILD_R10.json').read_text());b.update(revision='R11',file=str(dest),exterior_rock_material_overrides=b.get('context_material_only',[])+changed);(O/'BUILD_R11.json').write_text(json.dumps(b,indent=2));print('R11_SAVED',changed,flush=True)
