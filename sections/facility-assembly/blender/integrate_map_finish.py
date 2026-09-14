import bpy,bmesh,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'connections/map-finish'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A09_access_finish.blend'),load_ui=False)
# Replace only this finishing package with its corrected preview iteration.
for name in ['13_FINISHED_ACCESS_SCENERY','14_ACCESS_FINISH_VIEWPORT_CACHE']:
 col=bpy.data.collections[name]
 for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.collections.remove(col)
for file,names in [('access-finish-A09.blend',['13_FINISHED_ACCESS_SCENERY','14_ACCESS_FINISH_VIEWPORT_CACHE']),('network-finish-A10.blend',['15_FINISHED_NETWORK_SCENERY','16_NETWORK_FINISH_VIEWPORT_CACHE'])]:
 with bpy.data.libraries.load(str(O/file),link=False) as (src,dst):dst.collections=names
 for col in dst.collections:bpy.context.scene.collection.children.link(col)
# Remove obsolete short pipe pieces from the authoring network and its disposable cache.
net=bpy.data.collections['09_FINISHED_HORIZONTAL_CONNECTIONS'];bounds=[];removed=[]
for o in list(net.objects):
 if any(s in o.name for s in ['supported overhead pipe','pipe hanger','pipe coupling']):
  pts=[o.matrix_basis@Vector(v) for v in o.bound_box];lo=Vector([min(v[i] for v in pts)-.008 for i in range(3)]);hi=Vector([max(v[i] for v in pts)+.008 for i in range(3)]);bounds.append((lo,hi));removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
proxy=bpy.data.objects['WALK_PROXY_HORIZONTAL_NETWORK'];bm=bmesh.new();bm.from_mesh(proxy.data);mat=proxy.matrix_basis
coords=np.empty(len(proxy.data.vertices)*3,dtype=np.float32);proxy.data.vertices.foreach_get('co',coords);coords=coords.reshape(-1,3);matrix=np.asarray(mat);coords=coords@matrix[:3,:3].T+matrix[:3,3];mask=np.zeros(len(coords),dtype=bool)
for lo,hi in bounds:mask|=((coords>=np.asarray(lo))&(coords<=np.asarray(hi))).all(axis=1)
bm.verts.ensure_lookup_table();vs={bm.verts[int(i)] for i in np.flatnonzero(mask)}
bmesh.ops.delete(bm,geom=[f for f in bm.faces if all(v in vs for v in f.verts)],context='FACES');bm.to_mesh(proxy.data);bm.free()
# Remove text and bolts left over from the condenser's old scenic blanking panel.
inst=bpy.data.objects['condenser-bay'];names={o.name for o in inst.instance_collection.all_objects if o.name.startswith('D01 blanking')}
def unlink(c):
 for o in list(c.objects):
  if o.name in names:c.objects.unlink(o)
 for ch in c.children:unlink(ch)
unlink(inst.instance_collection)
proxy=bpy.data.objects['WALK_PROXY_condenser-bay'];bm=bmesh.new();bm.from_mesh(proxy.data);inv=inst.matrix_basis.inverted()@proxy.matrix_basis
vs={v for v in bm.verts if -1.10<(inv@v.co).x<1.10 and -2.26<(inv@v.co).y<-2.20 and .12<(inv@v.co).z<2.4}
bmesh.ops.delete(bm,geom=[f for f in bm.faces if all(v in vs for v in f.verts)],context='FACES');bm.to_mesh(proxy.data);bm.free()
# Fine plaster grain and concrete roughness at real-world scales on assembly-owned surfaces.
owned=bpy.data.collections['11_ACCESS_ARCHITECTURE'];seen=set()
for o in owned.objects:
 if o.type!='MESH':continue
 for m in o.data.materials:
  if not m or m.library or m.name in seen or not m.use_nodes:continue
  if not any(s in m.name for s in ['concrete','mineral']):continue
  seen.add(m.name);n=m.node_tree.nodes;links=m.node_tree.links;geo=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=36
  bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.013
  links.new(geo.outputs['Position'],noise.inputs['Vector']);links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
world=bpy.data.worlds.new('A10 clear afternoon sky');world.use_nodes=True;world.node_tree.nodes.get('Background').inputs[0].default_value=(.58,.68,.84,1);world.node_tree.nodes.get('Background').inputs[1].default_value=.40;bpy.context.scene.world=world
d=bpy.data.lights.new('A10 afternoon sun','SUN');d.energy=2.5;d.angle=.12;o=bpy.data.objects.new(d.name,d);bpy.context.scene.collection.objects.link(o);o.rotation_euler=(.55,-.55,-.8)
for cname in ['13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY']:bpy.data.collections[cname].hide_viewport=True
bpy.context.scene.name='FACILITY_A10_MAP_FINISH'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_walkthrough_A10_map_finish.blend'),compress=True)
for cname in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE']:bpy.data.collections[cname].hide_viewport=True
for cname in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD','13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY']:bpy.data.collections[cname].hide_viewport=False
bpy.context.scene.name='FACILITY_A10_MAP_FINISH_MASTER'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_master_A10_map_finish.blend'),compress=True)
(O/'INTEGRATION.json').write_text(json.dumps({'short_overhead_parts_replaced':len(removed),'remaining_D01_blanking_parts_removed':len(names),'old_source_files_untouched':True,'new_detail_viewport_batches':2},indent=2));print('A10_MAP_FINISH_SAVED',flush=True)
