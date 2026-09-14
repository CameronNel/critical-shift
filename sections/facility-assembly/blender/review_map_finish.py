import bpy,json,math,os,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'connections/map-finish';sys.path.insert(0,str(R/'blender'))
bpy.ops.wm.open_mainfile(filepath=str(R/'blender'/os.environ.get('FINISH_FILE','facility_walkthrough_A11_map_finish.blend')),load_ui=False)
L=json.loads((R/'production/LAYOUT_A08.json').read_text());hits=[];count=0
def overlap(poly1,poly2):
 for poly in [poly1,poly2]:
  for a,b in zip(poly,poly[1:]+poly[:1]):
   e=b-a
   if e.length<1e-6:continue
   n=Vector((-e.y,e.x)).normalized();x=[v.dot(n) for v in poly1];y=[v.dot(n) for v in poly2]
   if max(x)<=min(y)+.015 or max(y)<=min(x)+.015:return False
 return True
for ob in bpy.data.collections['15_FINISHED_NETWORK_SCENERY'].objects:
 if ob.type not in {'MESH','CURVE','FONT'}:continue
 p=[ob.matrix_basis@Vector(v) for v in ob.bound_box];lo=min(v.z for v in p);hi=max(v.z for v in p)
 if hi<.08 or lo>2.3:continue
 count+=1;hull=[p[i].xy for i in [0,4,6,2]]
 if len({(round(v.x,5),round(v.y,5)) for v in hull})<3:hull=[Vector((min(v.x for v in p),min(v.y for v in p))),Vector((max(v.x for v in p),min(v.y for v in p))),Vector((max(v.x for v in p),max(v.y for v in p))),Vector((min(v.x for v in p),max(v.y for v in p)))]
 for r in L['routes']:
  if r['id']=='R19':continue
  for aa,bb in zip(r['points'],r['points'][1:]):
   a,b=Vector(aa).xy,Vector(bb).xy;v=b-a
   if v.length<.01:continue
   n=Vector((-v.y,v.x)).normalized()*r['width_m']/2
   if overlap(hull,[a+n,b+n,b-n,a-n]):hits.append({'object':ob.name,'route':r['id']});break
(O/'CLEARANCE.json').write_text(json.dumps({'objects_checked':count,'obstacle_candidates':hits,'pass':not hits,'method':'Oriented bounds against all full-width ground route rectangles; new finishing objects only.'},indent=2));print('FINISH_CLEARANCE',count,len(hits),hits[:8],flush=True)
if os.environ.get('FINISH_AUDIT_ONLY')=='1':raise SystemExit(0 if not hits else 1)
# Original room display caches provide stable context; new scenery uses authored geometry.
reviewlights=bpy.data.collections.new('REVIEW_LIGHTS');bpy.context.scene.collection.children.link(reviewlights)
for n in ['09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD']:
 for ob in list(bpy.data.collections[n].all_objects):
  if ob.type=='LIGHT':cp=ob.copy();reviewlights.objects.link(cp);cp.matrix_world=ob.matrix_basis;cp.hide_render=False
for n in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD']:
 c=bpy.data.collections[n];c.hide_render=True;c.hide_viewport=True
for n in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE']:
 c=bpy.data.collections[n];c.hide_render=False;c.hide_viewport=False
 for ob in c.objects:
  if 'GREYBOX' not in ob.name:ob.hide_render=False
for n in ['13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY','17_REACTOR_EXTERIOR_FINISH']:bpy.data.collections[n].hide_viewport=False
if '20_ROOF_SERVICE_GEOMETRY' in bpy.data.collections:bpy.data.collections['20_ROOF_SERVICE_GEOMETRY'].hide_viewport=False
if '22_EXTERIOR_FINISH_GEOMETRY' in bpy.data.collections:bpy.data.collections['22_EXTERIOR_FINISH_GEOMETRY'].hide_viewport=False
import facility_access_tools as access
for ob in access.doors():
 if not ob.get('group') and 'lift_gate_z' not in ob and not ob.get('cabin_gate'):access.request_door(ob,True)
for i in range(30):access.step(.04)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='GPU';p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='HIP';p.refresh_devices()
for d in p.devices:d.use=d.type=='HIP'
if hasattr(p,'use_hiprt'):p.use_hiprt=True
s.cycles.samples=32;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.05;s.render.use_persistent_data=False;s.view_settings.view_transform='AgX'
s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100
cam=bpy.data.objects.new('A11_REVIEW_CAMERA',bpy.data.cameras.new('A11_REVIEW_CAMERA'));s.collection.objects.link(cam);s.camera=cam;cam.data.lens=28;cam.data.clip_end=600
views=[('ROOF_CLOSE',(71,25,8),(66.745,21.223,5.5),None),('MEDICAL_ROOF',(-10,45,7),(-16.75,38.29,4.3),None),('SPAWN_EXIT',(-28,10.2,1.7),(-28,18,1.7),None),('MINE_EDGE',(-61,5,8),(-50,-14,0),None),('PERIMETER',(74,-56,7),(42,-67,1),None),('TOP',(-14,10,200),(-14,10,0),220),('PROCESS',(8,28,1.7),(18,28,1.7),None),('TRANSFER',(-5,-4,1.7),(3,-4,1.7),None),('POWER',(80,51,16),(69,35,0),None),('PROMENADE',(-35,28,1.7),(-10,28,1.7),None),('COOLING',(-31,47,14),(-10,57,0),None),('WASTE',(54,20,13),(46,11,0),None),('COMPLIANCE',(-49,9,12),(-41,20,0),None),('LOWER',(30,-13,15),(28,-3,0),None),('MINE',(4,-37,12),(-3,-25,0),None),('PASSAGE',(35.4,44.9,-4.3),(48.2,44.9,-4.6),None),('ACCESS_REVERSE',(45.2,44.9,-4.3),(34,44.9,-4.5),None),('STAIR',(31.1,45.9,1.7),(31.1,40,-2),None),('LIFT',(34,36,1.7),(30,34.8,1),None),('REACTOR',(12.2,92.5,10),(12.2,46.5,7),None)]
if os.environ.get('FINISH_NATIVE_RENDER')=='1':
 reviewlights.hide_render=True
 for n in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE','18_REACTOR_FINISH_VIEWPORT_CACHE']:bpy.data.collections[n].hide_render=True
 for n in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD']:
  bpy.data.collections[n].hide_render=False;bpy.data.collections[n].hide_viewport=False
selected=os.environ.get('FINISH_VIEWS','').split(',');dest=O/os.environ.get('FINISH_RENDER_DIR','renders-A11');dest.mkdir(exist_ok=True)
for name,pos,target,ortho in views:
 if selected!=[''] and name not in selected:continue
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if ortho else 'PERSP';cam.data.lens=23 if name in ['PASSAGE','ACCESS_REVERSE','STAIR','LIFT'] else 28
 bpy.context.view_layer.update()
 nearby=[]
 for door in access.doors():
  if not door.get('group'):continue
  q=door.matrix_world.inverted()@Vector(pos);dist=max(abs(q.x)-door['width']/max(.01,door.scale.x)/2,0)**2+q.y*q.y
  if -.2<q.z<2.5 and dist<3.3**2:nearby.append((dist,door))
 seen=set()
 for dist,door in sorted(nearby,key=lambda p:p[0]):
  if door['group'] not in seen:access.request_door(door,True);seen.add(door['group'])
 for i in range(40):access.step(.04)
 if ortho:cam.data.ortho_scale=ortho
 s.render.filepath=str(dest/(name+'.png'));bpy.ops.render.render(write_still=True);print('RENDERED_A11',name,flush=True)
(O/'REVIEW_CAMERAS.json').write_text(json.dumps(views,indent=2))
