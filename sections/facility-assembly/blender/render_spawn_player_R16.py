"""Additional 1080p eye-height evidence; never replaces the four locked cameras."""
import os,runpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
os.environ.update(SPAWN_FILE='facility_spawn_concept02_R16.blend',SPAWN_OUTPUT='player-R16',SPAWN_VIEWS='NONE')
d=runpy.run_path(str(R/'blender/review_spawn_exterior_locked.py'))
s=d['s'];cam=d['cam'];Vector=d['Vector'];D=d['D']
cam.location=(-25,24,1.7);target=Vector((-28,12.5,1.65));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=24
s.render.resolution_x=1920;s.render.resolution_y=1080;s.eevee.shadow_resolution_scale=1.0
s.render.filepath=str(D/'PLAYER_1080P.png')
d['bpy'].ops.render.render(write_still=True)
m=json.loads((D/'MANIFEST.json').read_text());m.update(resolution=[1920,1080],views=[{'id':'PLAYER_1080P','eye':list(cam.location),'target':list(target),'lens':24}],rule='Additional eye-height view, fixed review cameras unchanged.',shadow_resolution_scale=s.eevee.shadow_resolution_scale)
(D/'MANIFEST.json').write_text(json.dumps(m,indent=2))
print('PLAYER_RENDER_COMPLETE',flush=True)
