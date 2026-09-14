import bpy,sys,json,math,os
from pathlib import Path
from mathutils import Vector,Quaternion
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'connections/access';sys.path.insert(0,str(ROOT/'blender'))
bpy.ops.wm.open_mainfile(filepath=os.environ.get('ACCESS_VERIFY_FILE',str(ROOT/'blender/facility_walkthrough_A08_access.blend')),load_ui=False)
import facility_access_tools as access
ds=access.doors();assert len(ds)>=25
report={'doors':len(ds),'interlock_checks':0,'lift_checks':0,'door_geometry':[]}
for o in ds:
 if 'lift_gate_z' in o or o.get('cabin_gate'):continue
 for other in ds:other['target']=0.;other['open']=0.
 assert access.request_door(o,True)
 for i in range(30):access.step(.04)
 assert o['open']>.999,o.name
 for ch in o.children:
  if ch.get('door_leaf'):assert ch.scale.z<.016,o.name
 access.request_door(o,False)
 for i in range(30):access.step(.04)
 assert o['open']<.001,o.name
 report['door_geometry'].append(o.name)
group=[o for o in ds if o.get('group')=='process_airlock'];assert len(group)>=4
a=next(o for o in group if o['side']=='fuel');b=next(o for o in group if o['side']=='reactor')
access.request_door(a,True)
for i in range(30):access.step(.04)
access.request_door(b,True)
for i in range(60):
 access.step(.04);assert not (a['open']>.001 and b['open']>.001);report['interlock_checks']+=1
assert b['open']>.999
lift=bpy.data.objects['ACCESS_CART_LIFT'];gates=[o for o in ds if 'lift_gate_z' in o or o.get('cabin_gate')]
for z in [-6,0]:
 access.request_lift(z)
 for i in range(210):
  access.step(.04)
  if -5.999<lift.location.z<-.001:assert all(o['open']<.001 for o in gates)
  report['lift_checks']+=1
 assert abs(lift.location.z-z)<.001
 assert all((o['open']>.999)==(o.get('cabin_gate') or o.get('lift_gate_z')==z) for o in gates)
class Passenger:
 view_location=Vector((30.05,34.85,1.7));view_rotation=Quaternion();view_distance=0.
passenger=Passenger();access.request_lift(-6)
for i in range(210):access.step(.04,passenger)
assert abs(passenger.view_location.z+4.3)<.001
report['passenger_follow_delta_z']=-6
access.request_lift(0)
for i in range(210):access.step(.04,passenger)
assert abs(passenger.view_location.z-1.7)<.001
# Check original room display meshes along the removed door volumes, several samples each.
bindings=json.loads((OUT/'DOOR_BINDINGS.json').read_text());bpy.context.view_layer.update();blocked=[]
for d in bindings:
 if not d['cut']:continue
 proxy=bpy.data.objects.get('WALK_PROXY_'+d['sid']);ctrl=bpy.data.objects['DOOR_'+d['id']];inv=proxy.matrix_world.inverted()
 for xx in [-.35,0,.35]:
  for zz in [.4,1.2,1.8]:
   a=ctrl.matrix_world@Vector((xx,-.25,zz));b=ctrl.matrix_world@Vector((xx,.25,zz));a=inv@a;b=inv@b
   hit,loc,normal,face=proxy.ray_cast(a,(b-a).normalized(),distance=(b-a).length)
   if hit:blocked.append([d['id'],xx,zz])
report['source_door_blocked_rays']=blocked
headroom=[]
checks=[bpy.data.objects[n] for n in ['WALK_PROXY_HORIZONTAL_NETWORK','Whole map continuous concrete floor','WALK_PROXY_reactor-room','WALK_PROXY_turbine-room']]
checks += [o for o in bpy.data.collections['11_ACCESS_ARCHITECTURE'].objects if o.type=='MESH']
for fi,(x,sg) in enumerate([(31.1,-1),(32.78,1)]):
 for i in range(18):
  p=Vector((x,(44.4 if fi==0 else 39.64)+sg*(i+.5)*.28,-3*fi-(i+1)/6+.025))
  for ob in checks:
   inv=ob.matrix_basis.inverted();a=inv@p;b=inv@(p+Vector((0,0,2.1)));hit,loc,normal,idx=ob.ray_cast(a,(b-a).normalized(),distance=(b-a).length)
   if hit:headroom.append([fi+1,i+1,ob.name])
report['stair_headroom_blockers']=headroom
con=bpy.data.objects['WALK_PROXY_condenser-bay'];inv=con.matrix_world.inverted()
for zz in [-5.5,-4.3]:
 a=inv@Vector((45.4,44.9,zz));b=inv@Vector((48.35,44.9,zz));hit,*_=con.ray_cast(a,(b-a).normalized(),distance=(b-a).length)
 if hit:blocked.append(['condenser approach',zz])
report['status']='PASS' if not blocked and not headroom else 'FAIL';Path(os.environ.get('ACCESS_VERIFY_REPORT',str(OUT/'VALIDATION.json'))).write_text(json.dumps(report,indent=2));print('ACCESS_VALIDATE',report['status'],blocked,headroom,flush=True)
if os.environ.get('ACCESS_VERIFY_RENDER')=='0':
 assert not blocked and not headroom,(blocked,headroom)
 raise SystemExit(0)
# Workbench renders are fresh geometry review, not final art approval.
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True
s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100
for name in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE']:
 c=bpy.data.collections[name];c.hide_render=False;c.hide_viewport=False
for name in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD']:
 c=bpy.data.collections.get(name)
 if c:c.hide_render=True;c.hide_viewport=True
for c in [bpy.data.collections['07_FAST_WALKTHROUGH_PROXIES'],bpy.data.collections['10_NETWORK_VIEWPORT_CACHE']]:
 for o in c.objects:
  if 'GREYBOX' not in o.name:o.hide_render=False
cam=bpy.data.objects.new('A08_REVIEW_CAMERA',bpy.data.cameras.new('A08_REVIEW_CAMERA'));s.collection.objects.link(cam);s.camera=cam;cam.data.lens=22
for o in ds:
 if not o.get('group') and 'lift_gate_z' not in o:access.request_door(o,True)
for i in range(30):access.step(.04)
out=OUT/'renders';out.mkdir(exist_ok=True)
for name,pos,target in [('STAIR_TOP',(31.1,45.9,1.7),(31.1,40,-2)),('STAIR_BOTTOM',(34.7,45.8,-4.3),(32.3,40,-2.5)),('LIFT_UPPER',(34,36,1.7),(30,34.8,1)),('LOWER_HALL',(35.4,44.9,-4.3),(48.2,44.9,-4.6)),('TOP',(35,40,26),(35,40,0))]:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
assert not blocked and not headroom,(blocked,headroom)
