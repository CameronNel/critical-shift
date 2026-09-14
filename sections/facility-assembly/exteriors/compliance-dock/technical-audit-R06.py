import bpy,bmesh,json,hashlib,runpy,os,math
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent
root=out.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=json.loads((root/'production/SOURCES.json').read_text())
row=next(r for r in manifest if r['id']=='compliance-dock')
files={'exterior':out/'exterior-R06.blend','accepted':root/row['frozen'],'module':root/'sources/compliance-dock/module.blend','original':Path(row['original'])}
before={k:sha(p) for k,p in files.items()}
bpy.ops.wm.open_mainfile(filepath=str(files['exterior']),load_ui=False)
bpy.context.view_layer.update()
scene=bpy.context.scene;ext=bpy.data.collections['EXTERIOR_compliance-dock'];dg=bpy.context.evaluated_depsgraph_get()
report={'hashes':before,'accepted_manifest_match':before['accepted']==row['source_sha256'],'original_manifest_match':before['original']==row['source_sha256'],'module_sha_recorded_in_source_manifest':False,'unit_scale':scene.unit_settings.scale_length,'libraries':[],'images':[],'cameras':[],'meshes':[]}
for lib in bpy.data.libraries:
 p=Path(bpy.path.abspath(lib.filepath));report['libraries'].append({'path':str(p),'exists':p.exists(),'sha256':sha(p) if p.exists() else None})
for im in bpy.data.images:
 p=bpy.path.abspath(im.filepath,library=im.library) if im.filepath else ''
 report['images'].append({'name':im.name,'source':im.source,'packed':bool(im.packed_file),'has_data':im.has_data,'path_exists':Path(p).exists() if p else False})
for ob in scene.objects:
 if ob.type=='CAMERA':report['cameras'].append({'name':ob.name,'location':list(ob.location),'rotation':list(ob.rotation_euler),'lens':ob.data.lens,'type':ob.data.type,'clip':[ob.data.clip_start,ob.data.clip_end]})
report['render']={'size':[scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage],'engine':scene.render.engine,'samples':scene.cycles.samples,'view':scene.view_settings.view_transform}
inst=bpy.data.objects['READ_ONLY_ORIGINAL_compliance-dock'];report['source_instance']={'matrix':[list(r) for r in inst.matrix_world],'collection':inst.instance_collection.name,'linked':bool(inst.instance_collection.library),'objects':len(inst.instance_collection.all_objects)}
report['non_unit_additive_scales']=[o.name for o in ext.objects if any(abs(s-1)>1e-6 for s in o.scale)]
report['interior_core_aabb_intrusions']=[]
for ob in ext.objects:
 if ob.type!='MESH':continue
 eo=ob.evaluated_get(dg);me=eo.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 report['meshes'].append({'name':ob.name,'signed_volume':bm.calc_volume(signed=True),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'noncontiguous_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-12 for f in bm.faces)})
 pts=[ob.matrix_world@Vector(p) for p in ob.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 if all(min(hi[i],[6.7,15.7,4.3][i])-max(lo[i],[-6.7,.4,.05][i])>.003 for i in range(3)):report['interior_core_aabb_intrusions'].append(ob.name)
 bm.free();eo.to_mesh_clear()
report['support_metadata_count']=sum(any('support' in k.lower() for k in o.keys()) for o in ext.objects)
# Compare linked mesh/object content with accepted original by deterministic signatures.
def sig(ob):
 d={'type':ob.type,'matrix':[list(r) for r in ob.matrix_world]}
 if ob.type=='MESH':d.update(v=[list(v.co) for v in ob.data.vertices],p=[list(p.vertices) for p in ob.data.polygons])
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
linked={o.name:sig(o) for o in inst.instance_collection.all_objects}
# Audit script only writes its prescribed JSON, does not save blend or render.
os.environ['EXTERIOR_SECTION']='compliance-dock';os.environ['EXTERIOR_REVISION']='R06'
runpy.run_path(str(root/'blender/audit_exterior.py'),run_name='__main__')
report['rerun_audit']=json.loads((out/'audit-R06.json').read_text())['status']
bpy.ops.wm.open_mainfile(filepath=str(files['accepted']),load_ui=False)
accepted={o.name:sig(o) for o in bpy.data.objects}
report['linked_object_geometry_or_transform_differences']=[n for n,s in linked.items() if accepted.get(n)!=s]
report['linked_objects_compared']=len(linked)
report['files_unchanged']={k:sha(p)==before[k] for k,p in files.items()}
(out/'technical-audit-R06.json').write_text(json.dumps(report,indent=2))
print('TECH_AUDIT_DONE',len(report['meshes']),'negative volumes',sum(m['signed_volume']<0 for m in report['meshes']),'changed source objects',len(report['linked_object_geometry_or_transform_differences']),flush=True)

