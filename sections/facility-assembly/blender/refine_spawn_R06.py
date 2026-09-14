"""R05 -> R06: daylight fill on exterior vertical faces; consistent four-view review."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_spawn_concept02_R05.blend'),load_ui=False)
s=bpy.context.scene
for name,pos,energy in [('South',(-28,-14,10),4500),('East',(-3,7,12),3200),('West',(-52,7,12),3200)]:
 ld=bpy.data.lights.new('S01 '+name+' sky fill','AREA');ld.energy=energy;ld.shape='DISK';ld.size=22;ld.color=(.88,.92,1);ld.use_shadow=True
 ob=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((-28,7,1.7))-ob.location).to_track_quat('-Z','Y').to_euler()
s.name='FACILITY_SPAWN_CONCEPT02_R06';dest=R/'blender/facility_spawn_concept02_R06.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
b=json.loads((O/'BUILD_R05.json').read_text());b.update(revision='R06',file=str(dest),exterior_skylight_fill='Three broad area sources for sky illumination on shaded exterior walls');(O/'BUILD_R06.json').write_text(json.dumps(b,indent=2));print('R06_SAVED',flush=True)
