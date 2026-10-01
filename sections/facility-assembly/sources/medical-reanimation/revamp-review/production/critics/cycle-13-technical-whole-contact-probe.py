"""Independent island connectivity contact search; read-only, no render or save."""
import bpy,json,math,hashlib,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation');O=R/'revamp-review/production/critics'
sha=hashlib.sha256((Path('/workspace/scratch/medical-skill-full-cycle13.blend')).read_bytes()).hexdigest()
with bpy.data.libraries.load(str(Path('/workspace/scratch/medical-skill-full-cycle13.blend')),link=False) as (a,b):b.scenes=['REANIMATION_EDIT_LOCAL']
s=bpy.data.scenes['REANIMATION_EDIT_LOCAL'];bpy.context.window.scene=s;bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get()
inherited={r['name'] for r in json.loads((R/'revamp-review/baseline.json').read_text())['objects']}
nodes=[];roots=[];groups={}
def geom(name,pts,faces,edges,obj,ids=None,materials=None,pids=None):
 return {'name':name,'pts':pts,'faces':faces,'edges':edges,'tree':BVHTree.FromPolygons(pts,faces),'lo':[min(p[i] for p in pts) for i in range(3)],'hi':[max(p[i] for p in pts) for i in range(3)],'object':obj,'island_ids':ids,'materials':materials,'part_ids':pids}
for o in s.objects:
 if o.type not in {'MESH','CURVE','FONT','SURFACE'}:continue
 ev=o.evaluated_get(dep);m=ev.to_mesh();pts=[o.matrix_world@v.co for v in m.vertices]
 if not pts or not m.polygons:ev.to_mesh_clear();continue
 if o.name in {'Floor','Decon floor','West wall','East wall','Entry wall','Entry wall.001','Rear west wall','Rear east wall','Decon west wall','Decon east wall','Ceiling','Decon ceiling','Decon rear wall pier','Decon rear wall pier.001','Decon rear wall below extract','Decon rear wall above extract'}:
  roots.append(geom(o.name,pts,[tuple(p.vertices) for p in m.polygons],[tuple(e.vertices) for e in m.edges],o.name));ev.to_mesh_clear();continue
 adjacency=[set() for _ in pts]
 for e in m.edges:a,b=e.vertices;adjacency[a].add(b);adjacency[b].add(a)
 pending=set(range(len(pts)));islands=[];vmap={}
 while pending:
  seed=pending.pop();todo=[seed];ids={seed}
  while todo:
   for n in adjacency[todo.pop()]:
    if n in pending:pending.remove(n);ids.add(n);todo.append(n)
  iid=len(islands)
  for i in ids:vmap[i]=iid
  islands.append(ids)
 faces=[[] for _ in islands];edges=[[] for _ in islands];mats=[set() for _ in islands]
 for p in m.polygons:
  ii=vmap[p.vertices[0]];faces[ii].append(tuple(p.vertices));mats[ii].add(m.materials[p.material_index].name if m.materials[p.material_index] else '<missing>')
 for e in m.edges:edges[vmap[e.vertices[0]]].append(tuple(e.vertices))
 attr=m.attributes.get('med_assembly_part')
 for ii,ids in enumerate(islands):
  if not faces[ii]:continue
  seq=sorted(ids);remap={v:i for i,v in enumerate(seq)};node=geom(o.name+'#'+str(ii),[pts[i] for i in seq],[tuple(remap[v] for v in f) for f in faces[ii]],[tuple(remap[v] for v in e) for e in edges[ii]],o.name,ii,sorted(mats[ii]),sorted({attr.data[i].value for i in ids}) if attr else [])
  groups.setdefault(o.name,[]).append(len(nodes));nodes.append(node)
 ev.to_mesh_clear()
def boxgap(a,b):return math.sqrt(sum(max(a['lo'][i]-b['hi'][i],b['lo'][i]-a['hi'][i],0)**2 for i in range(3)))
def witness(a,b):
 best=(math.inf,None,None,None)
 # A valid sampled distance proves contact; no sampled contact alone is not a separation proof.
 for source,target in ((a,b),(b,a)):
  for p in source['pts']:
   q,n,idx,d=target['tree'].find_nearest(p)
   if d<best[0]:best=(d,list(p),list(q),(p-q).dot(n))
   if d<=.0050001:return best
  for e in source['edges']:
   p,q=[source['pts'][v] for v in e];v=q-p
   if v.length>1e-8:
    hit=target['tree'].ray_cast(p,v.normalized(),v.length)[0]
    if hit is not None:return (0,list(hit),list(hit),0)
   mid=(p+q)/2;q,n,idx,d=target['tree'].find_nearest(mid)
   if d<best[0]:best=(d,list(mid),list(q),(mid-q).dot(n))
   if d<=.0050001:return best
  for f in source['faces']:
   p=sum((source['pts'][i] for i in f),Vector())/len(f);q,n,idx,d=target['tree'].find_nearest(p)
   if d<best[0]:best=(d,list(p),list(q),(p-q).dot(n))
   if d<=.0050001:return best
 return best
links=[set() for _ in nodes];ground=[[] for _ in nodes];proofs=[];near_tests=0
for i,a in enumerate(nodes):
 for root in roots:
  if boxgap(a,root)>.0050001:continue
  near_tests+=1;w=witness(a,root)
  if w[0]<=.0050001:ground[i].append(root['name']);proofs.append({'node':i,'target_root':root['name'],'distance_m':w[0],'witness':w[1:3],'signed_at_witness_m':w[3]})
 for j in range(i):
  b=nodes[j]
  if boxgap(a,b)>.0050001:continue
  near_tests+=1;w=witness(a,b)
  if w[0]<=.0050001:links[i].add(j);links[j].add(i);proofs.append({'node':i,'target_node':j,'distance_m':w[0],'witness':w[1:3],'signed_at_witness_m':w[3]})
 if i%100==0:print('CONTACT_PROGRESS',i,len(nodes),'tests',near_tests,flush=True)
pending=set(range(len(nodes)));clusters=[]
while pending:
 seed=pending.pop();todo=[seed];ids={seed}
 while todo:
  for n in links[todo.pop()]:
   if n in pending:pending.remove(n);ids.add(n);todo.append(n)
 targets=sorted({r for i in ids for r in ground[i]})
 clusters.append({'nodes':sorted(ids),'root_targets':targets,'rooted':bool(targets)})
detached=[i for c in clusters if not c['rooted'] for i in c['nodes']]
suspects=[]
for i in detached:
 a=nodes[i];candidates=sorted(roots+nodes,key=lambda b:boxgap(a,b) if b is not a else math.inf)[:25];best=(math.inf,None,None)
 for b in candidates:
  if b is a:continue
  w=witness(a,b)
  if w[0]<best[0]:best=(w[0],b['name'],w)
 suspects.append({'node':i,'name':a['name'],'materials':a['materials'],'bounds':[a['lo'],a['hi']],'part_ids':a['part_ids'],'nearest_sampled_distance_m':best[0],'nearest_target':best[1],'nearest_witness':best[2]})
serial=[{k:v for k,v in n.items() if k not in {'pts','faces','edges','tree'}} for n in nodes]
result={'source_sha256':sha,'source_saved':False,'source_checksum_unchanged':sha==hashlib.sha256((Path('/workspace/scratch/medical-skill-full-cycle13.blend')).read_bytes()).hexdigest(),'new_islands':len(nodes),'inherited_geometry_targets':len(roots),'near_pair_tests':near_tests,'clusters':clusters,'detached_islands':suspects,'nodes':serial,'contact_witnesses':proofs,'limits':['Architectural floor/wall/ceiling surfaces are the terminal roots. This tests possible connection paths for all evaluated room islands; creator-intended supports still require interpretation.','<=5mm vertex/edge-midpoint/face-centre proximity or an edge intersection proves a possible physical connection; it does not certify all contact areas or penetration.','A sampled minimum above tolerance is a suspect requiring exact follow-up; it is not a standalone defect verdict.']}
(O/'cycle-13-technical-whole-contact-probe.json').write_text(json.dumps(result,indent=2)+'\n')
print('INDEPENDENT_CONTACT_RESULT',len(nodes),len(clusters),len(detached),'tests',near_tests,flush=True)
