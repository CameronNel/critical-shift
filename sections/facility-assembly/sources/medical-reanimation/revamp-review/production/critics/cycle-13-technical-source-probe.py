"""Independent read-only technical probe. Does not save Blender assets."""
import bpy, bmesh, json, hashlib, math, sys, time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation')
P=R/'revamp-review/production'
O=P/'critics'
before=hashlib.sha256((R/'module_overhaul_R2.blend').read_bytes()).hexdigest()
sys.argv += ['--cold','--dependencies']
src=(R/'verify_overhaul.py').read_text()
src=src.replace("(P/'dependency-manifest.json').write_text", "(O/'cycle-13-technical-root-dependencies.json').write_text")
src=src.replace("(P/('cold-verification.json' if '--cold' in sys.argv else 'objective-verification.json')).write_text", "(O/'cycle-13-technical-root-verification.json').write_text")
exec(compile(src,str(R/'verify_overhaul.py'),'exec'),{'__file__':str(R/'verify_overhaul.py'),'__name__':'__main__','O':O})
s=bpy.data.scenes['REANIMATION_EDIT_LOCAL'];bpy.context.window.scene=s;bpy.context.view_layer.update()
dep=bpy.context.evaluated_depsgraph_get()
baseline=json.loads((R/'revamp-review/baseline.json').read_text())
inherited={x['name'] for x in baseline['objects']}
reg={x['object']:x for x in json.loads((P/'support-registry.json').read_text())}
result={'source_sha256':before,'blender_version':bpy.app.version_string,'scene':s.name,'source_saved':False,'counts':{},'objects':[],'materials':[],'images':[],'libraries':[],'cameras':[],'errors':[]}
tri=0;draws=0;components=0
for o in s.objects:
 if o.type=='CAMERA':
  result['cameras'].append({'object':o.name,'matrix_world':[list(r) for r in o.matrix_world],'lens':o.data.lens,'projection':o.data.type})
 if o.type not in {'MESH','CURVE','FONT','SURFACE'}:continue
 ev=o.evaluated_get(dep);md=ev.to_mesh()
 md.calc_loop_triangles();tri+=len(md.loop_triangles)
 used=sorted({p.material_index for p in md.polygons});draws+=len(used)
 vs=[o.matrix_world@v.co for v in md.vertices]
 if not vs:ev.to_mesh_clear();continue
 lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
 adjacency=[set() for _ in vs]
 for e in md.edges:
  a,b=e.vertices;adjacency[a].add(b);adjacency[b].add(a)
 pending=set(range(len(vs)));islands=[];vmap={}
 while pending:
  seed=pending.pop();todo=[seed];island={seed}
  while todo:
   for n in adjacency[todo.pop()]:
    if n in pending:pending.remove(n);island.add(n);todo.append(n)
  iid=len(islands)
  for v in island:vmap[v]=iid
  islands.append(island)
 polys=[[] for _ in islands]
 for p in md.polygons:
  polys[vmap[p.vertices[0]]].append(p)
 attr=md.attributes.get('med_assembly_part')
 contracts=json.loads(o.get('assembly_contact_contracts','[]'))
 pids=sorted({d.value for d in attr.data}) if attr else []
 defined={x['part_id'] for x in contracts}
 details=[]
 for ii,ids in enumerate(islands):
  points=[vs[i] for i in ids];faces=polys[ii]
  edgecounts={};directions={};volume=0;origin=points[0]
  for f in faces:
   v=list(f.vertices)
   for a,b in zip(v,v[1:]+v[:1]):
    key=tuple(sorted((a,b)));edgecounts[key]=edgecounts.get(key,0)+1;directions[key]=directions.get(key,0)+(1 if a<b else -1)
   for j in range(1,len(v)-1):volume+=(vs[v[0]]-origin).dot((vs[v[j]]-origin).cross(vs[v[j+1]]-origin))/6
  closed=bool(edgecounts) and all(x==2 for x in edgecounts.values())
  inconsistent=sum(edgecounts[k]==2 and abs(directions[k])==2 for k in edgecounts)
  degenerate=sum((vs[t.vertices[1]]-vs[t.vertices[0]]).cross(vs[t.vertices[2]]-vs[t.vertices[0]]).length<1e-12 for t in md.loop_triangles if t.vertices[0] in ids)
  details.append({'island':ii,'vertices':len(ids),'faces':len(faces),'bounds':[[min(v[i] for v in points) for i in range(3)],[max(v[i] for v in points) for i in range(3)]],'part_ids':sorted({attr.data[i].value for i in ids}) if attr else [],'materials':sorted({md.materials[p.material_index].name if p.material_index<len(md.materials) and md.materials[p.material_index] else '<missing>' for p in faces}),'closed':closed,'signed_volume_m3':volume if closed else None,'inconsistent_edges':inconsistent,'degenerate_triangles':degenerate})
 components+=len(details)
 layers=[]
 for uv in md.uv_layers:
  finite=all(math.isfinite(q) for d in uv.data for q in d.uv)
  deg=0;area=0
  for t in md.loop_triangles:
   a,b,c=[uv.data[i].uv for i in t.loops];ta=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))*.5;area+=ta;deg+=ta<1e-12
  layers.append({'name':uv.name,'active_render':uv.active_render,'finite':finite,'uv_area':area,'degenerate_triangles':deg,'triangles':len(md.loop_triangles)})
 result['objects'].append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'inherited':o.name in inherited,'mesh_name':md.name,'bounds':[lo,hi],'vertices':len(vs),'triangles':len(md.loop_triangles),'used_materials':[md.materials[i].name if i<len(md.materials) and md.materials[i] else '<missing>' for i in used],'uv_layers':layers,'support_registry':reg.get(o.name),'support_target':o.get('support_target'),'surface_all_vertices':o.get('contact_check_surface_all_vertices'),'support_components':json.loads(o.get('support_components','[]')),'part_ids':pids,'uncontracted_part_ids':sorted(set(pids)-defined),'assembly_contracts':contracts,'components':details,'modifiers':[{'name':m.name,'type':m.type,'render':m.show_render} for m in o.modifiers],'matrix_world':[list(r) for r in o.matrix_world]})
 ev.to_mesh_clear()
for m in {m for o in s.objects if hasattr(o.data,'materials') for m in o.data.materials if m}:
 nodes=[]
 if m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type in {'UVMAP','TEX_IMAGE','TEX_COORD','MAPPING','TEX_NOISE','TEX_CHECKER','NORMAL_MAP','BUMP','OUTPUT_MATERIAL'}:
    nodes.append({'name':n.name,'type':n.type,'uv_map':getattr(n,'uv_map',None),'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None,'projection':getattr(n,'projection',None),'object':n.object.name if n.type=='TEX_COORD' and n.object else None,'links_in':[(l.from_node.name,l.from_socket.name,l.to_socket.name) for l in m.node_tree.links if l.to_node==n],'links_out':[(l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links if l.from_node==n]})
 result['materials'].append({'name':m.name,'users':m.users,'nodes':nodes})
for im in bpy.data.images:
 if im.source!='FILE':continue
 path=Path(bpy.path.abspath(im.filepath,library=im.library)) if im.filepath else None
 result['images'].append({'name':im.name,'packed':bool(im.packed_file),'path':str(path),'exists':path.is_file() if path else False,'size':list(im.size),'colorspace':im.colorspace_settings.name,'users':im.users,'loaded_pixel_sample':list(im.pixels[:4]) if min(im.size)>0 else []})
for lib in bpy.data.libraries:
 path=Path(bpy.path.abspath(lib.filepath)).resolve()
 result['libraries'].append({'stored_path':lib.filepath,'resolved':str(path),'exists':path.is_file(),'parent':lib.parent.filepath if lib.parent else None})
result['counts']={'scene_objects':len(s.objects),'inherited_objects':len(inherited),'geometry_objects':len(result['objects']),'evaluated_triangles':tri,'material_slots_used_estimate':draws,'mesh_islands':components,'materials':len(result['materials']),'file_images':len(result['images']),'libraries':len(result['libraries']),'cameras':len(result['cameras'])}
result['source_checksum_unchanged']=before==hashlib.sha256((R/'module_overhaul_R2.blend').read_bytes()).hexdigest()
(O/'cycle-13-technical-source-probe.json').write_text(json.dumps(result,indent=2)+'\n')
print('INDEPENDENT_SOURCE_PROBE',json.dumps(result['counts']), 'source_unchanged',result['source_checksum_unchanged'],flush=True)
