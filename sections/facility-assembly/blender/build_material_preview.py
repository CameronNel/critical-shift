"""Material/UV preserving evaluated preview. Never writes source libraries."""
import bpy, numpy as np, json, time, os
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'blender'/os.environ.get('PREVIEW_SOURCE','facility_master_A14_exterior.blend')),load_ui=False)
s=bpy.context.scene
sources=['01_LINKED_ROOMS','06_LINKED_EXTERIORS','CONNECTION_C01_RESCUE_COURTYARD','09_FINISHED_HORIZONTAL_CONNECTIONS','13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY','17_REACTOR_EXTERIOR_FINISH','20_ROOF_SERVICE_GEOMETRY','22_EXTERIOR_FINISH_GEOMETRY']
caches=['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE','18_REACTOR_FINISH_VIEWPORT_CACHE','21_ROOF_SERVICE_VIEWPORT_CACHE','23_EXTERIOR_FINISH_VIEWPORT_CACHE']
if '29_SPAWN_APPROVED_EXTERIOR' in bpy.data.collections:sources.append('29_SPAWN_APPROVED_EXTERIOR')
for n in sources:bpy.data.collections[n].hide_viewport=False
for n in caches:bpy.data.collections[n].hide_viewport=True
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
groups={};lights=[];direct={}
for n in sources[2:]:
 for ob in bpy.data.collections[n].all_objects:direct[ob.as_pointer()]=n
for inst in dg.object_instances:
 ob=inst.object
 parent=inst.parent.name if inst.parent else ''
 group=parent if parent in {o.name for n in sources[:2] for o in bpy.data.collections[n].objects} else direct.get(ob.original.as_pointer())
 if not group or not inst.show_self or ob.hide_render:continue
 if ob.type=='LIGHT':lights.append((ob.original,inst.matrix_world.copy()));continue
 if ob.type not in {'MESH','CURVE','FONT','SURFACE'}:continue
 groups.setdefault(group,[]).append((ob.original,inst.matrix_world.copy()))
out=bpy.data.collections.new('27_MATERIAL_PREVIEW');s.collection.children.link(out)
lc=bpy.data.collections.new('28_MATERIAL_PREVIEW_LIGHTS');s.collection.children.link(lc)
report=[]
for name,items in groups.items():
 chunks=[];mats=[];mapping={};nv=nl=nf=0;uvnames=set();uvcount=0
 for original,matrix in items:
  ob=original.evaluated_get(dg);me=ob.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
  if not me or not me.polygons:ob.to_mesh_clear();continue
  v=np.empty(len(me.vertices)*3,'f');me.vertices.foreach_get('co',v);v=v.reshape(-1,3)
  mat=np.asarray(matrix,dtype='f');v=v@mat[:3,:3].T+mat[:3,3]
  loops=np.empty(len(me.loops),'i');me.loops.foreach_get('vertex_index',loops)
  starts=np.empty(len(me.polygons),'i');me.polygons.foreach_get('loop_start',starts)
  totals=np.empty(len(me.polygons),'i');me.polygons.foreach_get('loop_total',totals)
  mi=np.empty(len(me.polygons),'i');me.polygons.foreach_get('material_index',mi)
  smooth=np.empty(len(me.polygons),bool);me.polygons.foreach_get('use_smooth',smooth)
  local=[]
  for slot in ob.material_slots:
   m=slot.material.original if slot.material else None;k=m.as_pointer() if m else 0
   if k not in mapping:mapping[k]=len(mats);mats.append(m)
   local.append(mapping[k])
  if not local:
   if 0 not in mapping:mapping[0]=len(mats);mats.append(None)
   local=[mapping[0]]
  mi=np.asarray(local,'i')[np.minimum(mi,len(local)-1)]
  uvs={}
  for uv in me.uv_layers:
   arr=np.empty(len(me.loops)*2,'f');uv.data.foreach_get('uv',arr);uvs[uv.name]=arr.reshape(-1,2);uvnames.add(uv.name)
  # Preserve active UV under a common name as well as explicitly named UV maps.
  if me.uv_layers.active:
   uvs['PREVIEW_ACTIVE_UV']=uvs[me.uv_layers.active.name].copy();uvnames.add('PREVIEW_ACTIVE_UV');uvcount+=1
  if np.linalg.det(mat[:3,:3])<0:
   for st,num in zip(starts,totals):
    loops[st:st+num]=loops[st:st+num][::-1]
    for arr in uvs.values():arr[st:st+num]=arr[st:st+num][::-1]
  chunks.append((v,loops+nv,starts+nl,totals,mi,smooth,uvs))
  nv+=len(v);nl+=len(loops);nf+=len(starts);ob.to_mesh_clear()
 if not chunks:continue
 me=bpy.data.meshes.new('MATERIAL_PREVIEW_'+name);me.vertices.add(nv);me.loops.add(nl);me.polygons.add(nf)
 for seq,field,idx in [(me.vertices,'co',0),(me.loops,'vertex_index',1),(me.polygons,'loop_start',2),(me.polygons,'loop_total',3),(me.polygons,'material_index',4),(me.polygons,'use_smooth',5)]:seq.foreach_set(field,np.concatenate([c[idx] for c in chunks]).ravel())
 for m in mats:me.materials.append(m)
 for un in sorted(uvnames):
  uv=me.uv_layers.new(name=un)
  uv.data.foreach_set('uv',np.concatenate([c[6].get(un,np.zeros((len(c[1]),2),'f')) for c in chunks]).ravel())
 if 'PREVIEW_ACTIVE_UV' in me.uv_layers:me.uv_layers.active=me.uv_layers['PREVIEW_ACTIVE_UV'];me.uv_layers.active.active_render=True
 me.update(calc_edges=True)
 ob=bpy.data.objects.new('MATERIAL_PREVIEW_'+name,me);out.objects.link(ob);ob['preview_source']=name
 report.append({'source':name,'objects':len(items),'faces':nf,'materials':len(mats),'objects_with_uv':uvcount,'uv_layers':list(uvnames)})
 print('MATERIAL_CACHE',name,nf,len(mats),uvcount,flush=True)
 del chunks
interior_lights=bpy.data.collections.get('30_RETAINED_INTERIOR_LIGHTING')
if interior_lights:
 lights.extend((ob,ob.matrix_world.copy()) for ob in interior_lights.objects if ob.type=='LIGHT')
 interior_lights.hide_viewport=True;interior_lights.hide_render=True
for original,matrix in lights:
 cp=original.copy();cp.name='PREVIEW_LIGHT_'+original.name;lc.objects.link(cp);cp.matrix_world=matrix;cp.hide_viewport=False;cp.hide_render=False
for n in sources:bpy.data.collections[n].hide_viewport=True;bpy.data.collections[n].hide_render=True
for n in caches:bpy.data.collections[n].hide_viewport=True;bpy.data.collections[n].hide_render=True
s['material_preview']=True;s.render.engine='BLENDER_EEVEE';s.eevee.use_raytracing=False;s.eevee.use_fast_gi=False
if os.environ.get('PREVIEW_QUALITY')!='HIGH':s.eevee.taa_samples=8;s.eevee.use_shadow_jitter_viewport=False;s.eevee.shadow_resolution_scale=.5
else:s.eevee.shadow_resolution_scale=1.0
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
dest=R/'blender'/os.environ.get('PREVIEW_DEST','facility_material_preview_A14.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
(R/'production'/os.environ.get('PREVIEW_REPORT','MATERIAL_PREVIEW_BUILD.json')).write_text(json.dumps({'file':str(dest),'groups':report,'lights':len(lights),'raytracing':False,'limitations':['Merged meshes can change implicit Generated/Object procedural texture coordinates; UVs and material assignments preserved.','Preview of current authored art, not a final Unity build.']},indent=2))
print('MATERIAL_PREVIEW_SAVED',dest,flush=True)
