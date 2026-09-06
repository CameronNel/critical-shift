import bpy,sys,json
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
specs={
 'HALL':[(1.0,8.95,1.6,56),(.8,8.95,1.6,60),(.8,8.75,1.6,54)],
 'BRIEFING':[(-2.4,1.08,1.53,58),(-2.42,1.1,1.53,62),(-2.45,1.15,1.6,58)],
 'LOCKER':[(7.80,1.02,1.6,58),(7.82,1.04,1.6,62),(7.65,1.02,1.6,60)]}
targets={'HALL':(0,1.3,1.42),'BRIEFING':(-5.25,4.4,1.3),'LOCKER':(3.65,4.6,1.3)}
for room,options in specs.items():
 cam=bpy.data.objects['REFERENCE_'+room];s.camera=cam
 for i,(x,y,z,sw) in enumerate(options):
  cam.location=(x,y,z);cam.rotation_euler=(Vector(targets[room])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.sensor_width=sw
  s.render.filepath=str(out/('%s_%d.png'%(room,i)));bpy.ops.render.render(write_still=True)
(out/'options.json').write_text(json.dumps({'specs':specs,'targets':targets},indent=2))
