"""Open the proven blocked spawn-to-clean-route transition in the assembly only."""
import bpy,bmesh,json,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'connections/completion'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A12_complete.blend'),load_ui=False)
inst=bpy.data.objects['spawn-room'];names=['SERVICE_end','SERVICE_end_washable_dado','SERVICE_end_coved_skirt','SERVICE_end_dado_cap'];removed=[]
def unlink(c,o):
 if o.name in c.objects:
  assert c.library is None
  c.objects.unlink(o)
 for ch in c.children:unlink(ch,o)
for name in names:
 o=next((o for o in inst.instance_collection.all_objects if o.name==name),None)
 if o is None:continue
 assert inst.instance_collection.library is None
 unlink(inst.instance_collection,o);removed.append(name)
p=bpy.data.objects['WALK_PROXY_spawn-room'];bm=bmesh.new();bm.from_mesh(p.data);bm.verts.ensure_lookup_table()
a=np.array([v.co[:] for v in bm.verts]);m=np.array(p.matrix_basis);a=a@m[:3,:3].T+m[:3,3]
mask=(a[:,0]>=-29.701)&(a[:,0]<=-26.299)&(a[:,1]>=12.261)&(a[:,1]<=12.463)&(a[:,2]>=-.001)&(a[:,2]<=3.401)
vs={bm.verts[i] for i in np.flatnonzero(mask)};fs=[f for f in bm.faces if all(v in vs for v in f.verts)];num=len(fs)
bmesh.ops.delete(bm,geom=fs,context='FACES');bm.to_mesh(p.data);bm.free()
col=bpy.data.collections['19_MAP_COMPLETION'];mat=bpy.data.materials['EXT mineral painted concrete']
def box(name,c,s):
 if any(o.name==name and abs(o.location.x-c[0])<.01 for o in col.objects):return
 v=[(c[0]+a*s[0]/2,c[1]+b*s[1]/2,c[2]+d*s[2]/2) for a,b,d in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]);me.materials.append(mat);o=bpy.data.objects.new(name,me);col.objects.link(o)
if 'Spawn clean-route portal lintel' not in bpy.data.objects:
 for x in [-29.5,-26.5]:box('Spawn clean-route portal jamb',(x,12.38,1.7),(.4,.18,3.4))
 box('Spawn clean-route portal lintel',(-28,12.38,3.05),(2.6,.18,.7))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_walkthrough_A12_complete.blend'),compress=True)
for n in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE','18_REACTOR_FINISH_VIEWPORT_CACHE']:bpy.data.collections[n].hide_viewport=True
for n in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD','13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY','17_REACTOR_EXTERIOR_FINISH']:bpy.data.collections[n].hide_viewport=False
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_master_A12_complete.blend'),compress=True)
(O/'SPAWN_FIX.json').write_text(json.dumps({'removed_assembly_wall_objects':removed,'cache_faces_removed':num,'opening_width':2.6,'opening_height':2.7,'source_file_modified':False},indent=2));print('SPAWN_TRANSITION_FIXED',num,flush=True)
