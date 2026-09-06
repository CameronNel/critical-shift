import sys,bpy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import valorant_composition as c
import revise_spawn as rev
import valorant_polish as v
c.run();rev.startup()
bpy.ops.wm.save_as_mainfile(filepath=str(v.HERE/'spawnroom_valorant_walk.blend'),compress=True)
sys.argv=['blender','--','--validate-only','--review','pass-06','--cameras','REFERENCE_HALL,REFERENCE_BRIEFING,REFERENCE_LOCKER,DETAIL_FourLockers']
v.main()
