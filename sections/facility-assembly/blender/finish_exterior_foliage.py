"""Remove faceted shrub placeholders and extend fine leaf planting within existing beds."""
import bpy,json,random,math
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'connections/exterior-final'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A14_exterior.blend'),load_ui=False)
oldnames=('C01 olive leaves','NETWORK foliage olive','FINISH olive foliage');removed=0
for name in ['CONNECTION_C01_RESCUE_COURTYARD','09_FINISHED_HORIZONTAL_CONNECTIONS','15_FINISHED_NETWORK_SCENERY']:
 for o in list(bpy.data.collections[name].objects):
  if o.type=='MESH' and any(m and m.name.startswith(oldnames) for m in o.data.materials):bpy.data.objects.remove(o,do_unlink=True);removed+=1
for name in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE']:
 for ob in bpy.data.collections[name].objects:
  if ob.type!='MESH':continue
  bad={i for i,m in enumerate(ob.data.materials) if m and m.name.startswith(oldnames)}
  if not bad:continue
  old=ob.data;keep=[p for p in old.polygons if p.material_index not in bad];me=bpy.data.meshes.new(ob.name+' fine planting revision');me.from_pydata([v.co[:] for v in old.vertices],[],[tuple(p.vertices) for p in keep])
  for m in old.materials:me.materials.append(m)
  for p,q in zip(me.polygons,keep):p.material_index=q.material_index;p.use_smooth=q.use_smooth
  ob.data=me
col=bpy.data.collections.new('26_FINE_PLANTING');bpy.context.scene.collection.children.link(col);verts=[];faces=[];idx=[];random.seed(1421)
for ob in bpy.data.collections['09_FINISHED_HORIZONTAL_CONNECTIONS'].objects:
 if ob.type!='MESH' or 'planter' not in ob.name.lower():continue
 p=ob.location;t=Vector((math.cos(ob.rotation_euler.z),math.sin(ob.rotation_euler.z),0))
 for side in [-.62,.62]:
  center=p+t*side;center.z=.91
  for i in range(150):
   a=random.uniform(0,math.tau);r=.33*math.sqrt(random.random());q=center+Vector((r*math.cos(a),r*math.sin(a),random.uniform(-.23,.26)));d=Vector((math.cos(a),math.sin(a),.3))*.12;w=Vector((-math.sin(a),math.cos(a),.15))*.027;k=len(verts);verts.extend([q-d,q+w,q+d,q-w]);faces.append((k,k+1,k+2,k+3));idx.append(random.randrange(3))
me=bpy.data.meshes.new('Dense olive foliage in existing network beds');me.from_pydata(verts,[],faces)
for i in range(3):me.materials.append(bpy.data.materials['A14 olive leaf '+str(i)])
for p,i in zip(me.polygons,idx):p.material_index=i
ob=bpy.data.objects.new(me.name,me);col.objects.link(ob)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_walkthrough_A14_exterior.blend'),compress=True)
for name in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE','18_REACTOR_FINISH_VIEWPORT_CACHE','21_ROOF_SERVICE_VIEWPORT_CACHE','23_EXTERIOR_FINISH_VIEWPORT_CACHE']:bpy.data.collections[name].hide_viewport=True
for name in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD','13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY','17_REACTOR_FINISH_VIEWPORT_CACHE','20_ROOF_SERVICE_GEOMETRY','22_EXTERIOR_FINISH_GEOMETRY']:
 if name in bpy.data.collections:bpy.data.collections[name].hide_viewport=False
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_master_A14_exterior.blend'),compress=True)
(O/'FOLIAGE.json').write_text(json.dumps({'faceted_placeholders_removed':removed,'new_fine_leaves':len(faces)},indent=2));print('FINE_FOLIAGE_SAVED',removed,len(faces),flush=True)
