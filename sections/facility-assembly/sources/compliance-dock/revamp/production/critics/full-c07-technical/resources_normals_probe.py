import bpy,json,hashlib,collections,math
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');P=R/'revamp/production';O=P/'critics/full-c07-technical';S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S;D=bpy.context.evaluated_depsgraph_get()
def sha(data):return hashlib.sha256(data).hexdigest()
resources={'images':[],'fonts':[],'libraries':[],'material_graphs':[],'orientations':[]}
for im in bpy.data.images:
 packed=[{'size':p.packed_file.size,'sha256':sha(bytes(p.packed_file.data))} for p in im.packed_files]
 resources['images'].append({'name':im.name,'library':im.library.filepath if im.library else None,'path':im.filepath,'source':im.source,'size':list(im.size),'packed':packed})
for f in bpy.data.fonts:
 resources['fonts'].append({'name':f.name,'path':f.filepath,'builtin':f.filepath in {'','<builtin>'},'packed_sha256':sha(bytes(f.packed_file.data)) if f.packed_file else None})
for li in bpy.data.libraries:
 p=Path(bpy.path.abspath(li.filepath,library=li.parent));p=p if p.exists() else Path(bpy.path.abspath(li.filepath));resources['libraries'].append({'path':li.filepath,'resolved':str(p),'relative':li.filepath.startswith('//'),'exists':p.exists(),'sha256':sha(p.read_bytes()) if p.exists() else None})
materials={m for o in S.objects if o.type in {'MESH','CURVE','FONT'} for m in o.data.materials if m}
for m in materials:
 reached=set()
 def reach(n):
  if n.name in reached:return
  reached.add(n.name)
  for s in n.inputs:
   for l in s.links:reach(l.from_node)
 for n in m.node_tree.nodes if m.use_nodes else []:
  if n.type=='OUTPUT_MATERIAL' and n.is_active_output:reach(n)
 resources['material_graphs'].append({'name':m.name,'used_by':[o.name for o in S.objects if o.type in {'MESH','CURVE','FONT'} and m in list(o.data.materials)],'output_connected_nodes':sorted(reached),'consumed_uv_maps':[n.uv_map for n in m.node_tree.nodes if n.type=='UVMAP' and n.name in reached] if m.use_nodes else [],'output_image_nodes':[{'node':n.name,'image':n.image.name if n.image else None} for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.name in reached] if m.use_nodes else [],'output_object_coords':[n.name for n in m.node_tree.nodes if n.type=='TEX_COORD' and n.name in reached and n.outputs['Object'].is_linked] if m.use_nodes else []})
for o in S.objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 ev=o.evaluated_get(D);m=ev.to_mesh();m.calc_loop_triangles();ps=[o.matrix_world@v.co for v in m.vertices];parent=list(range(len(ps)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for e in m.edges:
  a=find(e.vertices[0]);b=find(e.vertices[1])
  if a!=b:parent[b]=a
 groups=collections.defaultdict(list)
 for t in m.loop_triangles:groups[find(t.vertices[0])].append(t)
 for i,ts in enumerate(groups.values()):
  edges=collections.defaultdict(list);p0=ps[ts[0].vertices[0]];vol=0
  for t in ts:
   v=t.vertices;p=[ps[x]-p0 for x in v];vol+=p[0].dot(p[1].cross(p[2]))/6
   for a,b in [(v[0],v[1]),(v[1],v[2]),(v[2],v[0])]:edges[tuple(sorted((a,b)))].append((a,b))
  boundary=sum(len(x)==1 for x in edges.values());nonman=sum(len(x)>2 for x in edges.values());inconsistent=sum(len(x)==2 and x[0]==x[1] for x in edges.values());
  resources['orientations'].append({'object':o.name,'island':i,'triangles':len(ts),'boundary_edges':boundary,'nonmanifold_edges':nonman,'inconsistent_edge_orientation':inconsistent,'signed_volume_m3':vol,'negative_closed_volume':boundary==0 and nonman==0 and vol<-1e-12})
 ev.to_mesh_clear()
(O/'resources-normals.json').write_text(json.dumps(resources,indent=2));print('DONE',len(resources['images']),len(resources['orientations']),flush=True)
