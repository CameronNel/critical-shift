import bpy,json,math,collections,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S;DG=bpy.context.evaluated_depsgraph_get()
raw=json.loads((P/'inventory.json').read_text());contact=json.loads((P/'contacts.json').read_text());byname={};windings=[]
for O in S.objects:
 if O.type not in {'MESH','CURVE','FONT','SURFACE'}:continue
 E=O.evaluated_get(DG);M=E.to_mesh();M.calc_loop_triangles();V=[O.matrix_world@v.co for v in M.vertices];T=[tuple(t.vertices)for t in M.loop_triangles];edge=collections.defaultdict(list)
 for tri in T:
  for i,j in zip(tri,tri[1:]+tri[:1]):
   a=tuple(round(x,7)for x in V[i]);b=tuple(round(x,7)for x in V[j]);edge[tuple(sorted((a,b)))].append((a,b))
 bad=[e for e,rows in edge.items()if len(rows)==2 and rows[0]==rows[1]]
 if bad:windings.append({'object':O.name,'inconsistent_shared_edges':len(bad),'examples':bad[:8]})
 byname[O.name]={'v':V,'t':T}
 E.to_mesh_clear()
def tree(part):
 # Reconstruct same welded-component triangle order from original vertex graph.
 O=byname[part['object']]
 parent=list(range(len(O['v'])));weld={}
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 def union(i,j):parent[find(i)]=find(j)
 for i,v in enumerate(O['v']):
  k=tuple(round(x,7)for x in v)
  if k in weld:union(i,weld[k])
  else:weld[k]=i
 for t in O['t']:union(t[0],t[1]);union(t[1],t[2])
 groups=collections.defaultdict(list)
 for t in O['t']:groups[find(t[0])].append(t)
 T=list(groups.values())[part['component']];inds=sorted({i for t in T for i in t});mp={v:i for i,v in enumerate(inds)};V=[O['v'][i]for i in inds];T=[tuple(mp[i]for i in t)for t in T]
 return {'bvh':BVHTree.FromPolygons(V,T,all_triangles=True),'samples':V+[(V[a]+V[b]+V[c])/3 for a,b,c in T],'bounds':part['bounds'],'closed':part['closed_winding']}
needed={i for r in contact['intersections']for i in [r['a'],r['b']]};trees={i:tree(raw['parts'][i]) for i in needed}
directions=[Vector((1,.371,.219)).normalized(),Vector((-.273,1,.193)).normalized()]
def inside(p,Q):
 answer=[]
 for d in directions:
  start=p.copy();hits=0
  for _ in range(200):
   co,n,f,dist=Q['bvh'].ray_cast(start,d,100.)
   if co is None:break
   hits+=1;start=co+d*.00001
  answer.append(hits%2==1)
 return all(answer)
rows=[]
for count,row in enumerate(contact['intersections']):
 a,b=row['a'],row['b'];result={'a':a,'b':b,'objects':[raw['parts'][a]['object'],raw['parts'][b]['object']],'owners':[raw['parts'][a]['owner'],raw['parts'][b]['owner']],'crossing_pairs':row['pairs'],'deep_samples':0,'max_penetration_m':0}
 for i,j in [(a,b),(b,a)]:
  Q=trees[j]
  if not Q['closed']:continue
  for p in trees[i]['samples']:
   if not all(Q['bounds'][0][k]+.002<p[k]<Q['bounds'][1][k]-.002 for k in range(3)):continue
   co,n,f,dist=Q['bvh'].find_nearest(p)
   if dist>.002 and inside(p,Q):
    result['deep_samples']+=1
    if dist>result['max_penetration_m']:result['max_penetration_m']=dist;result['witness']={'from':i,'point':list(p),'target_point':list(co),'target_triangle':f}
 rows.append(result)
 if count%200==0:print('INTERSECTIONS',count,flush=True)
(P/'intersections-detail.json').write_text(json.dumps({'method':'Actual evaluated triangle vertices and face centres; closed solids only; nearest surface distance >2mm, interior parity agreed by two independent oblique rays. Intentional joint overlaps must be classified; these samples do not measure overlap volume or prove all intersections benign.','inconsistent_winding':windings,'pairs':rows},indent=2));print('DETAIL_COMPLETE',len(rows),len(windings),flush=True)
