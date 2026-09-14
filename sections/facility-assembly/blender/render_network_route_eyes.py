"""Independent cold process, fixed first-person geometry review for every route."""
import bpy,json,os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'connections/network';REV='R03'
bpy.ops.wm.open_mainfile(filepath=str(OUT/f'review-{REV}.blend'),load_ui=False)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=False;s.display.shading.show_cavity=True;s.render.resolution_x=1100;s.render.resolution_y=720;s.render.resolution_percentage=100
L=json.loads((ROOT/'production/LAYOUT_CONNECTIONS_PLAN.json').read_text());dest=OUT/'route-eyes-R03';dest.mkdir(exist_ok=True)
cam=s.camera;cam.data.type='PERSP';cam.data.lens=24;report=[]
for r in L['routes']:
 if r['id']=='R19':continue
 seg=max(zip(r['points'],r['points'][1:]),key=lambda ab:(Vector(ab[1])-Vector(ab[0])).length)
 a,b=map(Vector,seg);v=b-a;u=v.normalized();loc=a+u*min(2,v.length*.2)+Vector((0,0,1.7));target=loc+u*5
 cam.location=loc;cam.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(dest/f"{r['id']}.png");bpy.ops.render.render(write_still=True)
 report.append({'route':r['id'],'eye':list(loc),'direction':list(u),'render':str(dest/f"{r['id']}.png")})
(OUT/'ROUTE_EYES.json').write_text(json.dumps(report,indent=2));print('COLD_ROUTE_EYES_COMPLETE',len(report),flush=True)
