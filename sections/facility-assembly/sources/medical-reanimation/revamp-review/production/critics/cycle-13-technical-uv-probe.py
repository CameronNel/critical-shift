import bpy,json,hashlib,math
from pathlib import Path
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation');O=R/'revamp-review/production/critics'
sha=hashlib.sha256((Path('/workspace/scratch/medical-skill-full-cycle13.blend')).read_bytes()).hexdigest()
with bpy.data.libraries.load(str(Path('/workspace/scratch/medical-skill-full-cycle13.blend')),link=False) as(a,b):b.scenes=['REANIMATION_EDIT_LOCAL']
s=bpy.data.scenes['REANIMATION_EDIT_LOCAL'];bpy.context.window.scene=s;bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get()
reports=[];coord=[]
for o in s.objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(dep);m=ev.to_mesh();m.calc_loop_triangles()
 for mi,mat in enumerate(m.materials):
  if not mat or not mat.use_nodes:continue
  nt=mat.node_tree;active_outputs=[n for n in nt.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output];visited=set();todo=list(active_outputs)
  while todo:
   n=todo.pop()
   if n.name in visited:continue
   visited.add(n.name);todo.extend(l.from_node for l in nt.links if l.to_node==n)
  uvnames={n.uv_map for n in nt.nodes if n.type=='UVMAP' and n.name in visited}
  image_nodes=[n for n in nt.nodes if n.type=='TEX_IMAGE' and n.name in visited]
  implicit_images=[n for n in image_nodes if not n.inputs['Vector'].is_linked]
  if implicit_images:uvnames.add(next((u.name for u in m.uv_layers if u.active_render),'<missing active render UV>'))
  triangles=[t for t in m.loop_triangles if t.material_index==mi]
  if not triangles:continue
  for name in sorted(uvnames):
   uv=m.uv_layers.get(name);finite=True;deg=0;outside=0
   if uv:
    for t in triangles:
     a,b,c=[uv.data[i].uv for i in t.loops];finite&=all(math.isfinite(z) for v in (a,b,c) for z in v);area=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))*.5;deg+=area<1e-12;outside+=any(z<0 or z>1 for v in(a,b,c) for z in v)
   reports.append({'object':o.name,'material':mat.name,'UV':name,'triangles':len(triangles),'present':uv is not None,'finite':finite,'degenerate_used_triangles':deg,'outside_unit_used_triangles':outside,'interpretation':'physical tiled surface' if name=='MED_Physical_1m' else 'explicit printed atlas' if name=='Clinical_Label' else 'active UV printed artwork'})
  if mat.name not in {x['material'] for x in coord}:
   coord.append({'material':mat.name,'live_coord_nodes':[{'node':n.name,'type':n.type,'UV':getattr(n,'uv_map',None),'output_links':[(l.from_socket.name,l.to_node.name,l.to_socket.name) for l in nt.links if l.from_node==n and l.to_node.name in visited]} for n in nt.nodes if n.name in visited and n.type in {'UVMAP','TEX_COORD','NEW_GEOMETRY','MAPPING','NORMAL_MAP','BUMP','TEX_IMAGE'}],'images':[{'image':n.image.name if n.image else None,'colorspace':n.image.colorspace_settings.name if n.image else None,'vector_linked':n.inputs['Vector'].is_linked,'color_links':[(l.to_node.name,l.to_socket.name) for l in nt.links if l.from_node==n]} for n in image_nodes]})
 ev.to_mesh_clear()
result={'source_sha256':sha,'material_face_UV_checks':reports,'active_material_mapping':coord,'missing_layers':[x for x in reports if not x['present']],'invalid_coverage':[x for x in reports if not x['finite'] or x['degenerate_used_triangles']],'source_saved':False,'source_checksum_unchanged':sha==hashlib.sha256((Path('/workspace/scratch/medical-skill-full-cycle13.blend')).read_bytes()).hexdigest()}
(O/'cycle-13-technical-uv-probe.json').write_text(json.dumps(result,indent=2)+'\n');print('UV_PROBE',len(reports),'missing',len(result['missing_layers']),'invalid',len(result['invalid_coverage']),flush=True)
