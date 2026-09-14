import bpy,bmesh,json,math,os
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'connections/access'
kind=os.environ.get('ACCESS_TARGET','walkthrough')
source=ROOT/f'blender/facility_{kind}_A07_horizontal_network.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene;scene.name='FACILITY_A08_ACCESS'
bindings=json.loads((OUT/'DOOR_BINDINGS.json').read_text());poses=json.loads((ROOT/'production/LAYOUT_A07.json').read_text())['placements']
report={'kind':kind,'source':str(source),'source_exclusions':{},'cache_removed_faces':{}}
# Copy collection membership, never modify linked source objects or files.
for sid in sorted(set(d['sid'] for d in bindings if d['exclude_names'])):
 excluded=set(n for d in bindings if d['sid']==sid for n in d['exclude_names'])
 inst=bpy.data.objects.get(sid);assert inst and inst.instance_collection,sid
 def clone(col):
  c=bpy.data.collections.new('A08_'+col.name)
  for o in col.objects:
   if o.name not in excluded:c.objects.link(o)
  for ch in col.children:c.children.link(clone(ch))
  return c
 original=inst.instance_collection;inst.instance_collection=clone(original)
 actual={o.name for o in original.all_objects}&excluded
 assert actual==excluded,(sid,len(actual),len(excluded))
 report['source_exclusions'][sid]=len(actual)
 proxy=bpy.data.objects.get('WALK_PROXY_'+sid)
 if proxy:
  p=poses[sid];m=Matrix.Translation(Vector(p['translation']))@Matrix.Rotation(math.radians(p['rotation_z_degrees']),4,'Z');inv=m.inverted()@proxy.matrix_basis
  boxes=[d['cut'] for d in bindings if d['sid']==sid and d['cut']]
  bm=bmesh.new();bm.from_mesh(proxy.data)
  inside=set()
  for v in bm.verts:
   q=inv@v.co
   if any(all(lo[i]-.025<=q[i]<=hi[i]+.025 for i in range(3)) for lo,hi in boxes):inside.add(v)
  remove=[f for f in bm.faces if all(v in inside for v in f.verts)]
  report['cache_removed_faces'][sid]=len(remove);assert remove,sid
  bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(proxy.data);bm.free();proxy.data.update()
print('SOURCE_DOORS_OVERRIDDEN',flush=True)
# Ground surface rebuilt with two access holes in addition to the original basement voids.
holes=[(-101,-10.49,-58,0),(-4.51,28.7,32,59.5),(40.54,66.3,36.25,51.02),(45.74,57.98,35.02,47),(30.25,31.95,37.9,44.4),(28.78,31.3,33.15,36.55)]
o=bpy.data.objects['Whole map continuous concrete floor'];old=o.data
xs=sorted(set([-111,83]+[v for h in holes for v in h[:2]]));ys=sorted(set([-68,87]+[v for h in holes for v in h[2:]]));verts=[];faces=[]
for a,b in zip(xs,xs[1:]):
 for c,d in zip(ys,ys[1:]):
  x=(a+b)/2;y=(c+d)/2
  if any(x1<x<x2 and y1<y<y2 for x1,x2,y1,y2 in holes):continue
  k=len(verts);verts.extend([(a,c,-.065),(b,c,-.065),(b,d,-.065),(a,d,-.065)]);faces.append((k,k+1,k+2,k+3))
me=bpy.data.meshes.new('A08 ground with real access openings');me.from_pydata(verts,[],faces)
for mat in old.materials:me.materials.append(mat)
o.data=me
network=bpy.data.collections['09_FINISHED_HORIZONTAL_CONNECTIONS'];network.hide_viewport=False
paving=bpy.data.objects['Continuous horizontal network paving']
# Exact solid cuts through the joined paving.
for a,b,c,d in holes[-2:]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=((a+b)/2,(c+d)/2,-.1));cutter=bpy.context.object;cutter.dimensions=(b-a,d-c,1)
 bpy.context.view_layer.update();mod=paving.modifiers.new('A08 access opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.context.view_layer.objects.active=paving;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
removed=[]
for o in list(network.objects):
 p=o.location
 if ('retracted sliding leaf' in o.name or (o.name.startswith('R14') and 30.7<p.x<31.4 and 33<p.y<44.5 and p.z<3.2 and ('upright' in o.name or 'base' in o.name or 'column' in o.name))):
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
report['network_replaced']=removed
# Remove the old joined cache and bake the modified network as one mesh.
oldcache=bpy.data.collections.get('10_NETWORK_VIEWPORT_CACHE')
if oldcache:
 for o in list(oldcache.objects):bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.collections.remove(oldcache)
cache=bpy.data.collections.new('10_NETWORK_VIEWPORT_CACHE');scene.collection.children.link(cache)
bpy.ops.object.select_all(action='DESELECT');items=[]
for o in network.objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 cp=o.copy();cp.data=o.data.copy();cache.objects.link(cp);cp.hide_viewport=False;cp.select_set(True);items.append(cp)
bpy.context.view_layer.objects.active=items[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();bpy.context.object.name='WALK_PROXY_HORIZONTAL_NETWORK';cache.hide_render=True
for name in ['11_ACCESS_ARCHITECTURE','12_ACCESS_MOVING_PARTS']:
 with bpy.data.libraries.load(str(OUT/'access-A08.blend'),link=False) as (src,dst):dst.collections=[name]
 scene.collection.children.link(dst.collections[0])
# Doors at observed existing network frames, using their actual dimensions/orientation.
dynamic=bpy.data.collections['12_ACCESS_MOVING_PARTS']
# Replace preliminary airlock positions with exact header locations.
for key in ['process_south','process_north','compliance_west','compliance_east']:
 root=bpy.data.objects.get('DOOR_'+key)
 if root:
  def delete_tree(o):
   for c in list(o.children):delete_tree(c)
   bpy.data.objects.remove(o,do_unlink=True)
  delete_tree(root)
template=bpy.data.objects['DOOR_medical_entry']
def new_door(key,loc,angle,w,h,group,side):
 def duplicate(o,parent=None):
  cp=o.copy();dynamic.objects.link(cp);cp.parent=parent
  for ch in o.children:duplicate(ch,cp)
  return cp
 root=duplicate(template);root.name='DOOR_'+key;root.location=loc;root.rotation_euler.z=angle;root.scale=(w/2,1,h/2.45)
 root['group']=group;root['side']=side;root['width']=w;root['height']=h;root['open']=0. if group else 1.;root['target']=root['open']
 for ch in root.children:
  if ch.get('door_leaf'):ch.scale.z=1-root['open']*.985
for o in network.objects:
 rid=o.name[:3]
 if 'airlock header' in o.name:
  g='process_airlock' if rid=='R03' else ('compliance_airlock' if rid=='R12' else '')
  side=('fuel' if o.location.y<28 else 'reactor') if rid=='R03' else o.name
  new_door(o.name,(o.location.x,o.location.y,0),o.rotation_euler.z-math.pi/2,o.dimensions.y-1.05,3.04,g,side)
 elif 'crossing portal lintel' in o.name and rid in {'R02','R03','R12'}:
  new_door(o.name,(o.location.x,o.location.y,0),o.rotation_euler.z,o.dimensions.x-.9,o.location.z-.10,'process_airlock' if rid=='R03' else '',o.name)
network.hide_viewport=kind=='walkthrough';cache.hide_viewport=kind!='walkthrough'
bpy.context.preferences.inputs.walk_navigation.use_gravity=False
scene['connection_scope']='A08: horizontal network, 6m condenser stairs/cart lift, assembly door overrides and Blender access controls. Engine collision/navmesh remains step 3.'
dest=ROOT/f'blender/facility_{kind}_A08_access.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
report['file']=str(dest);report['doors']=sum(bool(o.get('access_door')) for o in dynamic.objects)
(OUT/f'INTEGRATION_{kind}.json').write_text(json.dumps(report,indent=2));print('A08_SAVED',kind,flush=True)
