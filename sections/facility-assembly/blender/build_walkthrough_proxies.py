"""Bake evaluated visible geometry into per-section solid-viewport meshes.

Original authoring assets are read only. These disposable meshes preserve faces,
positions and material colors, but omit UVs/animation and are not render assets.
"""
import bpy, numpy as np, json, hashlib, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'blender/facility_walkthrough_before_optimization.blend'
before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
sections=json.loads((ROOT/'exteriors/CURRENT.json').read_text())
groups={}
for inst in dg.object_instances:
 if not inst.show_self or inst.object.type not in {'MESH','CURVE','FONT','SURFACE'}:continue
 parent=inst.parent.name if inst.parent else ''
 if parent not in sections and not parent.startswith('EXTERIOR_INSTANCE_'):continue
 # Iterator-owned evaluated object handles are reused; retain stable originals.
 groups.setdefault(parent,[]).append((inst.object.original,inst.matrix_world.copy()))
col=bpy.data.collections.new('07_FAST_WALKTHROUGH_PROXIES')
bpy.context.scene.collection.children.link(col)
report=[]
for name,items in groups.items():
 chunks=[];materials=[];material_map={};nv=nl=nf=0
 expected_min=np.full(3,np.inf);expected_max=np.full(3,-np.inf)
 for original,matrix in items:
  obj=original.evaluated_get(dg)
  mesh=obj.to_mesh(preserve_all_data_layers=False,depsgraph=dg)
  if not mesh or not mesh.polygons:
   obj.to_mesh_clear();continue
  v=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',v);v=v.reshape(-1,3)
  m=np.asarray(matrix,dtype=np.float32);v=v@m[:3,:3].T+m[:3,3]
  loop=np.empty(len(mesh.loops),dtype=np.int32);mesh.loops.foreach_get('vertex_index',loop)
  starts=np.empty(len(mesh.polygons),dtype=np.int32);mesh.polygons.foreach_get('loop_start',starts)
  totals=np.empty(len(mesh.polygons),dtype=np.int32);mesh.polygons.foreach_get('loop_total',totals)
  mi=np.empty(len(mesh.polygons),dtype=np.int32);mesh.polygons.foreach_get('material_index',mi)
  smooth=np.empty(len(mesh.polygons),dtype=np.bool_);mesh.polygons.foreach_get('use_smooth',smooth)
  mapping=[]
  for slot in obj.material_slots:
   mat=slot.material
   key=mat.as_pointer() if mat else 0
   if key not in material_map:
    material_map[key]=len(materials);materials.append(mat)
   mapping.append(material_map[key])
  if not mapping:
   if 0 not in material_map:material_map[0]=len(materials);materials.append(None)
   mapping=[material_map[0]]
  mi=np.asarray(mapping,dtype=np.int32)[np.minimum(mi,len(mapping)-1)]
  if np.linalg.det(m[:3,:3])<0:
   for start,total in zip(starts,totals):loop[start:start+total]=loop[start:start+total][::-1]
  expected_min=np.minimum(expected_min,v.min(axis=0));expected_max=np.maximum(expected_max,v.max(axis=0))
  chunks.append((v,loop+nv,starts+nl,totals,mi,smooth))
  nv+=len(v);nl+=len(loop);nf+=len(starts)
  obj.to_mesh_clear()
 mesh=bpy.data.meshes.new('WALK_MESH_'+name)
 mesh.vertices.add(nv);mesh.loops.add(nl);mesh.polygons.add(nf)
 mesh.vertices.foreach_set('co',np.concatenate([c[0] for c in chunks]).ravel())
 mesh.loops.foreach_set('vertex_index',np.concatenate([c[1] for c in chunks]))
 mesh.polygons.foreach_set('loop_start',np.concatenate([c[2] for c in chunks]))
 mesh.polygons.foreach_set('loop_total',np.concatenate([c[3] for c in chunks]))
 for mat in materials:mesh.materials.append(mat)
 mesh.polygons.foreach_set('material_index',np.concatenate([c[4] for c in chunks]))
 mesh.polygons.foreach_set('use_smooth',np.concatenate([c[5] for c in chunks]))
 mesh.update(calc_edges=True)
 ob=bpy.data.objects.new('WALK_PROXY_'+name,mesh);col.objects.link(ob)
 ob.hide_render=True
 ob['source_instance']=name
 ob['proxy_scope']='Disposable solid viewport cache; originals retained for editing/rendering'
 assert len(mesh.polygons)==nf
 actual=np.asarray([v.co[:] for v in mesh.vertices],dtype=np.float32)
 assert np.max(np.abs(actual.min(axis=0)-expected_min))<.001
 assert np.max(np.abs(actual.max(axis=0)-expected_max))<.001
 report.append({'source':name,'source_draw_objects':len(items),'faces':nf,'vertices':nv,'materials':len(materials),'bounds_preserved':True})
 print('PROXY_DONE',name,len(items),'objects -> 1 mesh',nf,'faces',flush=True)
 del chunks,actual
assert len(report)==24
dest=ROOT/'blender/walkthrough_proxy_meshes.blend'
bpy.data.libraries.write(str(dest),{col},path_remap='RELATIVE',fake_user=True,compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
(ROOT/'production/WALKTHROUGH_PROXY_BUILD.json').write_text(json.dumps({'source_sha256':before,'proxy_file':str(dest),'proxy_count':24,'sections':report,'scope':'Evaluated face and material-color consolidation; no decimation, no source edits; solid viewport only'},indent=2))
print('PROXY_BUILD_COMPLETE',flush=True)
