import bpy,json,hashlib,math,collections,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');P=R/'revamp/production';O=P/'critics/full-c07-technical'
S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S;D=bpy.context.evaluated_depsgraph_get()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def v(p):return [float(x) for x in p]
def owner(o):
 while o.parent:
  o=o.parent
  if o.get('support_class')=='supported_assembly':return o.name
 return None
base=json.loads((P/'baseline.json').read_text()); matrices=[];rows=[];islands=[];duplicate=collections.defaultdict(list); material_use=collections.Counter();sc=0;tc=0
for rec in base['objects']:
 o=S.objects.get(rec['name']); matrices.append({'object':rec['name'],'exists':bool(o),'matrix_delta':max(abs(o.matrix_world[i][j]-rec['matrix'][i][j]) for i in range(4) for j in range(4)) if o else None,'dimension_delta':[float(o.dimensions[i]-rec['dimensions'][i]) for i in range(3)] if o else None})
for o in S.objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 ev=o.evaluated_get(D);m=ev.to_mesh(preserve_all_data_layers=True,depsgraph=D);m.calc_loop_triangles();pts=[o.matrix_world@x.co for x in m.vertices];tri=[tuple(t.vertices) for t in m.loop_triangles];tc+=len(tri);used=set(p.material_index for p in m.polygons);sc+=len(used);edges=collections.Counter();zero=0; uvbad=0;uvmin=1e30;uvmax=0;uvcount=0;uvworst=[];finit=True
 layer=m.uv_layers.get('CD_Physical_1m');
 for t in m.loop_triangles:
  p=[pts[i] for i in t.vertices];area=(p[1]-p[0]).cross(p[2]-p[0]).length*.5
  if area==0:zero+=1
  if area>1e-14:
   key=tuple(sorted(tuple(round(float(x),6) for x in pt) for pt in p)); duplicate[key].append((o.name,t.index,area))
  if layer:
   uv=[layer.data[i].uv for i in t.loops]
   for i in range(3):
    d=(p[(i+1)%3]-p[i]).length
    if d>.0001:
     q=(uv[(i+1)%3]-uv[i]).length/d;uvmin=min(uvmin,q);uvmax=max(uvmax,q);uvcount+=1
     if abs(q-1)>.01:uvbad+=1;uvworst.append((abs(q-1),t.index,d,q))
 for poly in m.polygons:
  for a,b in poly.edge_keys:edges[tuple(sorted((a,b)))]+=1
 parent=list(range(len(pts)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for a,b in edges:
  a=find(a);b=find(b)
  if a!=b:parent[b]=a
 comps=collections.defaultdict(list)
 for i in range(len(pts)):comps[find(i)].append(i)
 ctri=collections.defaultdict(list)
 for t in m.loop_triangles:ctri[find(t.vertices[0])].append(t)
 objis=[]
 for ci,inds in enumerate(comps.values()):
  ts=ctri.get(find(inds[0]),[])
  if not ts:continue
  bmin=[min(pts[i][a] for i in inds) for a in range(3)];bmax=[max(pts[i][a] for i in inds) for a in range(3)];remap={i:k for k,i in enumerate(inds)};localpts=[pts[i] for i in inds];localtri=[tuple(remap[j] for j in t.vertices) for t in ts]
  bvh=BVHTree.FromPolygons(localpts,localtri,all_triangles=True)
  samples=[localpts[i] for i in range(0,len(localpts),max(1,len(localpts)//32))][:40]
  samples += [(pts[t.vertices[0]]+pts[t.vertices[1]]+pts[t.vertices[2]])/3 for t in ts[::max(1,len(ts)//20)]][:24]
  row={'object':o.name,'island':ci,'assembly':owner(o),'support_class':o.get('support_class'),'vertices':len(inds),'triangles':len(ts),'bounds':[bmin,bmax]};islands.append((row,bvh,samples));objis.append(row)
 for i in used:
  mat=m.materials[i] if i<len(m.materials) else None
  if mat:material_use[mat.name]+=1
 consumed=[]
 for mat in m.materials:
  if mat and mat.use_nodes:
   consumed.extend([n.uv_map for n in mat.node_tree.nodes if n.type=='UVMAP' and n.outputs[0].is_linked])
 rows.append({'object':o.name,'type':o.type,'assembly':owner(o),'properties':{k:str(o[k]) for k in o.keys()},'triangles':len(tri),'source_polygon_count':len(o.data.polygons) if o.type=='MESH' else None,'materials':[x.name if x else None for x in m.materials],'used_material_indices':sorted(used),'modifiers':[(x.name,x.type) for x in o.modifiers],'zero_area_triangles':zero,'boundary_edges':sum(x==1 for x in edges.values()),'nonmanifold_edges':sum(x>2 for x in edges.values()),'uv_layers':[x.name for x in m.uv_layers],'consumed_uv_layers':sorted(set(consumed)),'uv_edge_count':uvcount,'uv_ratio_min':uvmin if uvcount else None,'uv_ratio_max':uvmax if uvcount else None,'uv_bad_edges':uvbad,'uv_worst':sorted(uvworst,reverse=True)[:5],'island_count':len(objis),'bounds':[[min(float(p[a]) for p in pts) for a in range(3)],[max(float(p[a]) for p in pts) for a in range(3)]] if pts else None})
 ev.to_mesh_clear()
 print('mesh',o.name,len(tri),len(objis),flush=True)
(O/'native-inventory.json').write_text(json.dumps({'scene':S.name,'source_sha256':sha(R/'module_overhaul_R1.blend'),'counts':{'objects':len(S.objects),'evaluated_triangles':tc,'material_submeshes':sc,'local_material_families':len(material_use)},'material_families':dict(material_use),'inherited_matrices':matrices,'objects':rows,'scene_properties':{k:str(S[k]) for k in S.keys()},'exact_duplicate_triangles':[{'witnesses':x} for x in duplicate.values() if len(x)>1]},indent=2))
# Actual evaluated point-to-triangle nearest contacts for every disconnected island.
# Bounds filter selects candidates only; the measured distance is always BVH surface distance.
contacts=[]
for idx,(r,bvh,samples) in enumerate(islands):
 best=None;touch=[];candidate_count=0
 for j,(q,qb,qs) in enumerate(islands):
  if j==idx:continue
  gap=math.sqrt(sum(max(0,r['bounds'][0][a]-q['bounds'][1][a],q['bounds'][0][a]-r['bounds'][1][a])**2 for a in range(3)))
  if gap>.025:continue
  candidate_count+=1
  # Bidirectional samples catch a small fixing bearing against a large surface.
  nearest=None
  for pt in samples:
   hit=qb.find_nearest(pt)
   if hit[0] is not None and (nearest is None or hit[3]<nearest[0]):nearest=(hit[3],v(pt),v(hit[0]),int(hit[2]),'self_to_other')
  for pt in qs:
   hit=bvh.find_nearest(pt)
   if hit[0] is not None and (nearest is None or hit[3]<nearest[0]):nearest=(hit[3],v(hit[0]),v(pt),int(hit[2]),'other_to_self')
  if nearest:
   witness={'object':q['object'],'island':q['island'],'assembly':q['assembly'],'distance_m':float(nearest[0]),'self_point':nearest[1],'other_point':nearest[2],'triangle':nearest[3],'direction':nearest[4]}
   if best is None or nearest[0]<best['distance_m']:best=witness
   if nearest[0]<=.005001:touch.append(witness)
 contacts.append({**r,'nearby_candidate_count':candidate_count,'nearest_sampled_surface':best,'contacts_within_5mm':sorted(touch,key=lambda x:x['distance_m'])})
 if idx%100==0:print('contact',idx,'/',len(islands),flush=True)
(O/'island-surface-contacts.json').write_text(json.dumps({'method':'world evaluated triangle BVHs; vertex/face-centroid samples bidirectional; candidates bounds within25mm; finite sampling may miss a true narrow contact and cannot prove penetration depth; all islands independently reported','islands':contacts},indent=2))
print('DONE',tc,sc,len(material_use),len(islands),flush=True)
