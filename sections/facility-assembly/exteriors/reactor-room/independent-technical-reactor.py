import bpy,bmesh,json,hashlib,re
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sig(o):
 r={'type':o.type,'matrix':[list(v) for v in o.matrix_world]}
 if o.type=='MESH':r.update(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons])
 return hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest()
manifest=json.loads((root/'production/SOURCES.json').read_text())
for sid in ['reactor-room']:
 out=root/'exteriors'/sid;path=out/'exterior-R01.blend';row=next(r for r in manifest if r['id']==sid);accepted=root/row['frozen'];module=root/'sources'/sid/'module.blend';hashes={str(p):sha(p) for p in [path,accepted,module]}
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ext=bpy.data.collections['EXTERIOR_'+sid]
 instance=bpy.data.objects.get('READ_ONLY_ORIGINAL_'+sid);original=instance.instance_collection if instance else bpy.data.collections.get('MODULE_'+sid)
 linked={o.name:sig(o) for o in original.all_objects};r={'section':sid,'unit_scale':bpy.context.scene.unit_settings.scale_length,'source_instance_matrix':[list(v) for v in instance.matrix_world] if instance else None,'source_linked':bool(original.library),'source_object_count':len(linked),'accepted_sha_match':sha(accepted)==row['source_sha256'],'mesh_issues':[],'nonunit_scales':[],'missing_materials':[],'binding_issues':[],'source_binding_count':0,'images':[],'libraries':[]}
 for o in ext.objects:
  if any(abs(v-1)>1e-5 for v in o.scale):r['nonunit_scales'].append(o.name)
  if o.type=='MESH':
   eo=o.evaluated_get(dg);me=eo.to_mesh();bm=bmesh.new();bm.from_mesh(me);vol=bm.calc_volume(signed=True);bad=[sum(not e.is_manifold for e in bm.edges),sum(e.is_manifold and not e.is_contiguous for e in bm.edges),sum(f.calc_area()<1e-12 for f in bm.faces)]
   if vol<=0 or any(bad):r['mesh_issues'].append({'name':o.name,'volume':vol,'nonmanifold_inconsistent_degenerate':bad})
   bm.free();eo.to_mesh_clear()
   if not o.data.materials or any(m is None for m in o.data.materials):r['missing_materials'].append(o.name)
  bind=o.get('source_panel') or o.get('source_wall')
  if bind:
   r['source_binding_count']+=1;src=bpy.data.objects.get(bind)
   if not src:r['binding_issues'].append({'object':o.name,'missing_source':bind});continue
   if o.get('source_panel'):
    inv=src.matrix_world.inverted();pts=[inv@o.matrix_world@Vector(v) for v in o.bound_box];verts=[v.co for v in src.data.vertices];lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)];sl=[min(v[i] for v in pts) for i in range(3)];sh=[max(v[i] for v in pts) for i in range(3)]
    if sl[0]<lo[0]-1e-4 or sh[0]>hi[0]+1e-4 or sl[2]<lo[2]-1e-4 or sh[2]>hi[2]+1e-4 or sl[1]<hi[1]-1e-4:r['binding_issues'].append({'object':o.name,'source':bind,'skin_local_bounds':[sl,sh],'source_bounds':[lo,hi]})
 for im in bpy.data.images:r['images'].append({'name':im.name,'source':im.source,'packed':bool(im.packed_file),'has_data':im.has_data,'exists':Path(bpy.path.abspath(im.filepath,library=im.library)).exists() if im.filepath else False})
 for lib in bpy.data.libraries:r['libraries'].append({'path':lib.filepath,'exists':Path(bpy.path.abspath(lib.filepath)).exists()})
 r['audit']=json.loads((out/'audit-R01.json').read_text())
 r['portal_candidates']=[{'name':o.name,'location':list(o.matrix_world.translation)} for o in original.all_objects if any(t in o.name.lower() for t in ['cooling','portal','utility']) and o.type=='EMPTY']
 bpy.ops.wm.open_mainfile(filepath=str(accepted),load_ui=False);bpy.context.view_layer.update();a={o.name:sig(o) for o in bpy.data.objects};r['source_geometry_transform_differences']=[n for n,s in linked.items() if a.get(n)!=s];r['hashes_unchanged']=all(sha(p)==h for p,h in hashes.items());r['hashes']=hashes
 (out/'independent-technical-R01.json').write_text(json.dumps(r,indent=2));print(sid, 'binding issues',len(r['binding_issues']),'source differences',len(r['source_geometry_transform_differences']),flush=True)

