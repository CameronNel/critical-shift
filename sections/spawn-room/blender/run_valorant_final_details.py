import sys,bpy
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import valorant_final_details as d
import valorant_polish as v
import revise_spawn as rev
# Physical corrections to pass06, also reflected in the full composition builder.
bpy.data.objects['V_LOCKER_draped_towel'].location.z-=.002
p=bpy.data.objects['V_LOCKER_corner_ficus'];p.location=(2.35,5.85,.006);p.scale=(.90,.90,1.04)
c=bpy.data.objects['DETAIL_FourLockers'];c.location=(6.12,4,1.77);c.rotation_euler=(Vector((3.6,4,1.45))-c.location).to_track_quat('-Z','Y').to_euler();c.data.sensor_width=60
d.run();rev.startup()
bpy.ops.wm.save_as_mainfile(filepath=str(v.HERE/'spawnroom_valorant_walk.blend'),compress=True)
sys.argv=['blender','--','--validate-only','--review','pass-07','--cameras','REFERENCE_HALL,REFERENCE_BRIEFING,REFERENCE_LOCKER,DETAIL_FourLockers']
v.main()
