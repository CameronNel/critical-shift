"""Add C01 courtyard and route greybox to new A06 assembly; retain A05."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'connections/rescue-courtyard'
report={'revision':'A06_C01_R04','source_preservation':{},'files':[]}
for mode,source,dest in [('master','facility_master_A05_exteriors.blend','facility_master_A06_connections.blend'),('walk','facility_walkthrough.blend','facility_walkthrough_A06_connections.blend')]:
 path=ROOT/'blender'/source;report['source_preservation'][source]=hashlib.sha256(path.read_bytes()).hexdigest()
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
 sc=bpy.context.scene;sc.name='FACILITY_A06_CONNECTIONS'
 moved=[]
 for name in ['medical-reanimation','EXTERIOR_INSTANCE_medical-reanimation','WALK_PROXY_medical-reanimation','WALK_PROXY_EXTERIOR_INSTANCE_medical-reanimation']:
  ob=bpy.data.objects.get(name)
  if ob:ob.location+=Vector((11,-6,0));moved.append(name)
 assert 'medical-reanimation' in moved and 'EXTERIOR_INSTANCE_medical-reanimation' in moved,moved
 added=[]
 for filename,colname in [('courtyard-R04.blend','CONNECTION_C01_RESCUE_COURTYARD'),('all-routes-greybox.blend','CONNECTIONS_ALL_ROUTES_GREYBOX')]:
  with bpy.data.libraries.load(str(OUT/filename),link=False) as (src,dst):dst.collections=[colname]
  col=dst.collections[0];sc.collection.children.link(col);added.append(col)
 if mode=='walk':
  # Two disposable mesh batches keep draw-call cost bounded; authoring retained.
  cache=bpy.data.collections['07_FAST_WALKTHROUGH_PROXIES']
  for col in added:
   copies=[]
   bpy.ops.object.select_all(action='DESELECT')
   for ob in list(col.objects):
    if ob.type not in {'MESH','FONT','CURVE'}:continue
    cp=ob.copy();cp.data=ob.data.copy();cache.objects.link(cp);cp.hide_render=False;cp.hide_set(False);cp.select_set(True);copies.append(cp)
   bpy.context.view_layer.objects.active=copies[0]
   bpy.ops.object.convert(target='MESH');bpy.ops.object.join()
   cp=bpy.context.view_layer.objects.active;cp.name='WALK_PROXY_'+col.name;cp.hide_render=True
   col.hide_viewport=True
  assert len(cache.objects)==26,len(cache.objects)
  bpy.context.preferences.inputs.walk_navigation.use_gravity=False
  for area in bpy.context.screen.areas:
   if area.type=='VIEW_3D':
    sp=area.spaces.active;sp.shading.type='SOLID';sp.shading.color_type='MATERIAL'
    sp.region_3d.view_location=Vector((-21,21,1.7));sp.region_3d.view_distance=.05
    sp.region_3d.view_rotation=(Vector((-18,30,1.7))-Vector((-21,21,1.7))).to_track_quat('-Z','Y')
    sp.region_3d.view_perspective='PERSP'
 for name in ['02_UNBUILT_CONNECTION_RESERVATIONS','03_RESERVED_VOLUMES','04_PLANNING_LABELS']:
  if name in bpy.data.collections:bpy.data.collections[name].hide_viewport=True;bpy.data.collections[name].hide_render=True
 sc['connection_scope']='C01 rescue courtyard R04; remaining routes greybox. R19 vertical access unbuilt. No game collision/navmesh certification.'
 bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender'/dest),compress=True)
 report['files'].append({'mode':mode,'path':str(ROOT/'blender'/dest),'moved':moved,'sha256':hashlib.sha256((ROOT/'blender'/dest).read_bytes()).hexdigest()})
 assert hashlib.sha256(path.read_bytes()).hexdigest()==report['source_preservation'][source]
(ROOT/'production/CONNECTIONS_A06_MANIFEST.json').write_text(json.dumps(report,indent=2))
print('A06_INTEGRATION_PASS',flush=True)
