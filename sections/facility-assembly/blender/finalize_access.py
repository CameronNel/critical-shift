import bpy,bmesh,json,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'connections/access';sys.path.insert(0,str(ROOT/'blender'))
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/facility_walkthrough_A08_access.blend'),load_ui=False)
s=bpy.context.scene;dynamic=bpy.data.collections['12_ACCESS_MOVING_PARTS']
o=bpy.data.objects['Lift branch west retaining wall'];o.location.x=33.68;o.dimensions.x=.20
# Remove the three unsupported old post feet, including their display-cache triangles.
network=bpy.data.collections['09_FINISHED_HORIZONTAL_CONNECTIONS'];boxes=[];removed=[]
for o in list(network.objects):
 if o.type!='MESH' or o.name in ['Continuous horizontal network paving','Network joined roof decks']:continue
 vs=[o.matrix_basis@Vector(v) for v in o.bound_box];lo=Vector([min(v[i] for v in vs) for i in range(3)]);hi=Vector([max(v[i] for v in vs) for i in range(3)])
 if hi.z<-.1 or lo.z>2.5:continue
 if any(lo.x<b and hi.x>a and lo.y<d and hi.y>c for a,b,c,d in [(30.25,31.95,37.9,44.4),(28.78,31.3,33.15,36.55)]):
  boxes.append((lo-Vector((.015,.015,.015)),hi+Vector((.015,.015,.015))));removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
proxy=bpy.data.objects['WALK_PROXY_HORIZONTAL_NETWORK'];bm=bmesh.new();bm.from_mesh(proxy.data);m=proxy.matrix_basis
vs={v for v in bm.verts if any(all(lo[i]-.002<=(m@v.co)[i]<=hi[i]+.002 for i in range(3)) for lo,hi in boxes)}
bmesh.ops.delete(bm,geom=[f for f in bm.faces if all(v in vs for v in f.verts)],context='FACES');bm.to_mesh(proxy.data);bm.free()
# The compliance source had a solid scenic back wall behind its decorative leaf.
# Exclude only that wall from the local override; rebuild its sides and lintel.
inst=bpy.data.objects['compliance-dock'];wall=next(o for o in inst.instance_collection.all_objects if o.name=='P1 deep back wall')
def unlink_wall(c):
 if wall.name in c.objects:c.objects.unlink(wall)
 for ch in c.children:unlink_wall(ch)
unlink_wall(inst.instance_collection)
p=bpy.data.objects['WALK_PROXY_compliance-dock'];bm=bmesh.new();bm.from_mesh(p.data);inv=inst.matrix_basis.inverted()@p.matrix_basis
vv={v for v in bm.verts if -1.32<(inv@v.co).x<1.32 and -2.12<(inv@v.co).y<-1.98 and -.02<(inv@v.co).z<2.62}
bmesh.ops.delete(bm,geom=[f for f in bm.faces if all(v in vv for v in f.verts)],context='FACES');bm.to_mesh(p.data);bm.free()
ext=bpy.data.collections['11_ACCESS_ARCHITECTURE']
def box(name,loc,size,material):
 x,y,z=size;verts=[(a*x/2,b*y/2,c*z/2) for a,b,c in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];me=bpy.data.meshes.new(name);me.from_pydata(verts,[],[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]);o=bpy.data.objects.new(name,me);ext.objects.link(o);o.location=loc;me.materials.append(material);return o
mat=bpy.data.materials['EXT mineral painted concrete'];steel=bpy.data.materials['EXT charcoal coated steel']
for x in [-1.055,1.055]:
 o=box('Compliance open portal wall return',inst.matrix_basis@Vector((x,-2.05,1.3)),(.49,.1,2.6),mat);o.rotation_euler.z=inst.rotation_euler.z
o=box('Compliance open portal lintel',inst.matrix_basis@Vector((0,-2.05,2.4)),(1.62,.1,.4),mat);o.rotation_euler.z=inst.rotation_euler.z
for x in [30.14,32.06]:box('R19 actual stair portal jamb',(x,43.7,1.65),(.14,.22,3.3),steel)
box('R19 actual stair portal header',(31.10,43.7,3.3),(2.06,.22,.18),steel)
box('R04 stair portal wall return',(29.947,43.7,1.75),(.602,.22,3.5),mat)
# Add a travelling cabin gate. It closes with the landing gates before travel.
lift=bpy.data.objects['ACCESS_CART_LIFT'];template=bpy.data.objects['DOOR_lift_0']
def dup(o,parent=None):
 cp=o.copy();dynamic.objects.link(cp);cp.parent=parent
 for ch in o.children:dup(ch,cp)
 return cp
cab=dup(template,lift);cab.name='DOOR_lift_cabin';cab.location.x=31.08;del cab['lift_gate_z'];cab['cabin_gate']=True
# Merge each curtain's small rigid parts into one mesh, preserving material slots.
for root in [o for o in dynamic.objects if o.get('door_leaf')]:
 parts=[o for o in root.children if o.type=='MESH'];verts=[];faces=[];mats=[];mi=[]
 for o in parts:
  offset=len(verts);verts.extend([tuple(o.matrix_basis@v.co) for v in o.data.vertices])
  mapping=[]
  for mat in o.data.materials:
   if mat not in mats:mats.append(mat)
   mapping.append(mats.index(mat))
  for p in o.data.polygons:faces.append(tuple(offset+i for i in p.vertices));mi.append(mapping[p.material_index])
 if not parts:continue
 me=bpy.data.meshes.new(root.name+' curtain mesh');me.from_pydata(verts,[],faces)
 for mat in mats:me.materials.append(mat)
 for p,i in zip(me.polygons,mi):p.material_index=i
 ob=bpy.data.objects.new(root.name+' batched curtain',me);dynamic.objects.link(ob);ob.parent=root
 for o in parts:bpy.data.objects.remove(o,do_unlink=True)
import facility_access_tools as access
for o in access.doors():
 o['open']=0. if o.get('group') or o.get('lift_gate_z',0)==-6 else 1.;o['target']=o['open']
 for ch in o.children:
  if ch.get('door_leaf'):ch.scale.z=1-.985*o['open']
eye=Vector((31.1,46,1.7));rot=(Vector((31.1,40,-2))-eye).to_track_quat('-Z','Y')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.shading.type='SOLID';sp.shading.color_type='MATERIAL';sp.overlay.show_overlays=False;rv=sp.region_3d;rv.view_perspective='PERSP';rv.view_distance=1;rv.view_rotation=rot;rv.view_location=eye+rot@Vector((0,0,-1))
text=bpy.data.texts.new('ACCESS_CONTROLS_README');text.write('Enable facility_access_tools add-on. N > Walkthrough: automatic proximity doors, nearest door toggle, lift to ground/condenser. Shift F safe walk. Gravity disabled; engine collision and navmesh are step 3. Source room libraries remain untouched.')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/facility_walkthrough_A08_access.blend'),compress=True)
for name in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE']:
 bpy.data.collections[name].hide_viewport=True;bpy.data.collections[name].hide_render=True
for name in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD']:
 c=bpy.data.collections.get(name)
 if c:c.hide_viewport=False;c.hide_render=False
s.name='FACILITY_A08_ACCESS_MASTER'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/facility_master_A08_access.blend'),compress=True)
(OUT/'FINALIZE.json').write_text(json.dumps({'removed_access_obstructions':removed,'compliance_scenic_back_wall_replaced_with_open_portal':True,'moving_collection_objects':len(dynamic.objects),'door_count':len(access.doors()),'walk_and_master_saved':True},indent=2));print('A08_FINALIZED',flush=True)
