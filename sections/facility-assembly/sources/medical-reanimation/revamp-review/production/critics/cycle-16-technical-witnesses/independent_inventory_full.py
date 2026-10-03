import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation');W=R/'revamp-review/production/critics/cycle-16-technical-witnesses'
source=R/'module_overhaul_R2.blend'; before=hashlib.sha256(source.read_bytes()).hexdigest()
with bpy.data.libraries.load(str(source),link=False) as (a,b):b.scenes=['REANIMATION_EDIT_LOCAL']
s=bpy.data.scenes['REANIMATION_EDIT_LOCAL'];bpy.context.window.scene=s;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
objs=[];uvs=[];parts=[];triangles=0
for o in s.objects:
 rec={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'library':o.library.filepath if o.library else None,'location':list(o.matrix_world.translation),'dimensions':list(o.dimensions),'hide_render':o.hide_render,'modifiers':[{'name':m.name,'type':m.type,'show_render':m.show_render} for m in o.modifiers]}
 if o.type=='MESH':
  ev=o.evaluated_get(dg);md=ev.to_mesh();md.calc_loop_triangles();triangles+=len(md.loop_triangles)
  vs=[o.matrix_world@v.co for v in md.vertices];rec['bounds']=[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
  rec['vertices']=len(md.vertices);rec['polygons']=len(md.polygons);rec['triangles']=len(md.loop_triangles);rec['materials']=[m.name if m else None for m in md.materials];rec['uv_layers']=[u.name for u in md.uv_layers]
  active=any(m and m.use_nodes and any(n.type=='UVMAP' and n.uv_map=='MED_Physical_1m' and n.outputs[0].is_linked for n in m.node_tree.nodes) for m in md.materials)
  authored=o.name.startswith('MED_R2 |') or o.data.name.startswith('MED | Skill revised') or o.data.name.startswith('MED_R2 |')
  if active or authored:
   uv=md.uv_layers.get('MED_Physical_1m');bad=[];ratios=[]
   for face in md.polygons:
    if uv is None:bad.append(face.index);continue
    p=[Vector(uv.data[i].uv) for i in face.loop_indices]
    area=abs(sum(p[i].x*p[(i+1)%len(p)].y-p[(i+1)%len(p)].x*p[i].y for i in range(len(p)))/2)
    if not all(math.isfinite(c) for v in p for c in v) or area<1e-12:bad.append(face.index)
    if face.area>1e-10:ratios.append(area/face.area)
   uvs.append({'object':o.name,'active_named_material_user':active,'authored_or_revised':authored,'faces':len(md.polygons),'missing_or_degenerate_faces':bad,'area_ratio_uv_to_local_geometry_min':min(ratios) if ratios else None,'area_ratio_max':max(ratios) if ratios else None})
  if o.get('assembly_contact_contracts'):
   ids=md.attributes.get('med_assembly_part');declared=json.loads(o['assembly_contact_contracts']);actual=set(a.value for a in ids.data) if ids else set();decl=set(r['part_id'] for r in declared)
   parts.append({'object':o.name,'part_attribute_present':bool(ids),'domain':ids.domain if ids else None,'actual_ids':sorted(actual),'declared_ids':sorted(decl),'uncontracted_ids':sorted(actual-decl),'contracts':declared,'polygons_crossing_part_ids':sum(len({ids.data[i].value for i in p.vertices})>1 for p in md.polygons) if ids else None})
  ev.to_mesh_clear()
 objs.append(rec)
result={'source_sha256':before,'blender':bpy.app.version_string,'editable_scene_local':s.library is None,'objects':objs,'physical_uv':uvs,'part_coverage':parts,'evaluated_mesh_triangles':triangles,'file_images':[{'name':i.name,'filepath':i.filepath,'packed':bool(i.packed_file),'size':list(i.size)} for i in bpy.data.images if i.source=='FILE'],'source_sha256_after':hashlib.sha256(source.read_bytes()).hexdigest()}
assert before==result['source_sha256_after'];(W/'independent-inventory-full.json').write_text(json.dumps(result,indent=2));print('INVENTORY',len(objs),triangles,len(uvs),len(parts),flush=True)
