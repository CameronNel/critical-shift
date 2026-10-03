import bpy,json,math,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');P=R/'revamp/production';O=P/'critics/full-c07-technical';S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S;D=bpy.context.evaluated_depsgraph_get()
old=json.loads((O/'island-surface-contacts.json').read_text())['islands'];bad={(x['object'],x['island']) for x in old if x['support_class']=='assembly_component' and not x['contacts_within_5mm']}
def vec(x):return [float(q) for q in x]
I=[]; plane=collections.defaultdict(list);allp=[];allt=[]
for o in S.objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 ev=o.evaluated_get(D);me=ev.to_mesh();me.calc_loop_triangles();pt=[o.matrix_world@x.co for x in me.vertices];parent=list(range(len(pt)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for e in me.edges:
  a=find(e.vertices[0]);b=find(e.vertices[1])
  if a!=b:parent[b]=a
 comps=collections.defaultdict(list)
 for i in range(len(pt)):comps[find(i)].append(i)
 ts=collections.defaultdict(list)
 for t in me.loop_triangles:ts[find(t.vertices[0])].append(t)
 for ci,inds in enumerate(comps.values()):
  tr=ts[find(inds[0])]
  if not tr:continue
  remap={x:i for i,x in enumerate(inds)};ps=[pt[x] for x in inds];tri=[tuple(remap[x] for x in t.vertices) for t in tr];bvh=BVHTree.FromPolygons(ps,tri,all_triangles=True);bounds=[[min(p[a] for p in ps) for a in range(3)],[max(p[a] for p in ps) for a in range(3)]];I.append((o.name,ci,ps,tri,bvh,bounds))
  off=len(allp);allp.extend(ps);allt.extend([tuple(x+off for x in t) for t in tri])
  if o.type=='FONT':continue
  for k,t in enumerate(tr):
   points=[pt[x] for x in t.vertices];n=(points[1]-points[0]).cross(points[2]-points[0]);area=n.length*.5
   if area<.000001:continue
   n.normalize();d=n.dot(points[0]);key=tuple(round(float(x),5) for x in n)+(round(float(d),5),);plane[key].append((o.name,ci,t.index,points,n,area))
 ev.to_mesh_clear()
refined=[]
for name,ci,ps,tr,b,bounds in I:
 if (name,ci) not in bad:continue
 matches=[]
 for n,j,qp,qt,qb,qbounds in I:
  if (n,j)==(name,ci):continue
  gap=math.sqrt(sum(max(0,bounds[0][a]-qbounds[1][a],qbounds[0][a]-bounds[1][a])**2 for a in range(3)))
  if gap>.04:continue
  overlap=b.overlap(qb);best=None
  for p in ps:
   h=qb.find_nearest(p)
   if h[0] is not None and (best is None or h[3]<best[0]):best=(h[3],vec(p),vec(h[0]),int(h[2]))
  for p in qp:
   h=b.find_nearest(p)
   if h[0] is not None and (best is None or h[3]<best[0]):best=(h[3],vec(h[0]),vec(p),int(h[2]))
  matches.append({'object':n,'island':j,'surface_intersection_pairs':len(overlap),'first_intersection_pairs':overlap[:4],'vertex_surface_min_m':best[0] if best else None,'witness':best[1:] if best else None})
 refined.append({'object':name,'island':ci,'matches':sorted(matches,key=lambda x:0 if x['surface_intersection_pairs'] else x['vertex_surface_min_m'] or 1e9)[:15]})
(O/'refined-contact-candidates.json').write_text(json.dumps({'method':'All evaluated vertices to opposite BVH in both directions; BVH triangle intersection distinguishes legitimate interlocked seats from sparse-sample false negatives. Fully contained solids may have no intersection; nearest-distance alone is not a penetration test.','results':refined},indent=2))
# convex clipping of coplanar triangles; same outward orientation only.
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def sub(a,b):return (a[0]-b[0],a[1]-b[1])
def clip(poly,tri):
 sign=1 if cross(sub(tri[1],tri[0]),sub(tri[2],tri[0]))>0 else -1
 for k in range(3):
  a=tri[k];edge=sub(tri[(k+1)%3],a);res=[]
  if not poly:break
  for i,p in enumerate(poly):
   q=poly[(i+1)%len(poly)];cp=sign*cross(edge,sub(p,a));cq=sign*cross(edge,sub(q,a));pin=cp>=-1e-10;qin=cq>=-1e-10
   if pin:res.append(p)
   if pin!=qin:
    t=cp/(cp-cq);res.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
  poly=res
 return poly
world=BVHTree.FromPolygons(allp,allt,all_triangles=True);pairs=[]
for key,rs in plane.items():
 if len(rs)<2:continue
 axis=max(range(3),key=lambda a:abs(key[a]));axes=[a for a in range(3) if a!=axis];cells=collections.defaultdict(list);tested=set()
 for i,r in enumerate(rs):
  xy=[(p[axes[0]],p[axes[1]]) for p in r[3]];lo=[math.floor(min(p[a] for p in xy)/.5) for a in range(2)];hi=[math.floor(max(p[a] for p in xy)/.5) for a in range(2)]
  for x in range(lo[0],hi[0]+1):
   for y in range(lo[1],hi[1]+1):
    for j in cells[(x,y)]:
     if (j,i) in tested:continue
     tested.add((j,i));q=rs[j]
     if q[0]==r[0] and q[1]==r[1]:continue
     qxy=[(p[axes[0]],p[axes[1]]) for p in q[3]];poly=clip(xy,qxy)
     if len(poly)<3:continue
     area=abs(sum(cross(poly[k],poly[(k+1)%len(poly)]) for k in range(len(poly)))*.5/abs(r[4][axis])
     if area<1e-6:continue
     # Test both face centroids and the actual overlap centroid for external visibility.
     center2=[sum(p[a] for p in poly)/len(poly) for a in range(2)];center=Vector((0,0,0));center[axes[0]]=center2[0];center[axes[1]]=center2[1];center[axis]=(key[3]-key[axes[0]]*center2[0]-key[axes[1]]*center2[1])/key[axis]
     h=world.ray_cast(center+r[4]*.001,r[4],.25)
     pairs.append({'a':[q[0],q[1],q[2]],'b':[r[0],r[1],r[2]],'same_orientation_overlap_m2':area,'center':vec(center),'normal':vec(r[4]),'outward_blocked_within_250mm':h[0] is not None,'outward_first_hit_distance_m':h[3]})
    cells[(x,y)].append(i)
(O/'coplanar-overlap.json').write_text(json.dumps({'method':'evaluated triangles; same outward plane rounded1e-5; 2D convex intersection area >1e-6m2; pair counts may double count overlapping areas; outward occlusion ray is limited250mm and cannot establish visibility from a named camera','pairs':pairs},indent=2));print('DONE refined',len(refined),'coplanar',len(pairs),flush=True)
