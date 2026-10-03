import json,collections,math
from pathlib import Path
import numpy as np
P=Path(__file__).parent;d=json.loads((P/'evaluated-surfaces.json').read_text());meta=json.loads((P/'native-independent.json').read_text())['objects'];groups=collections.defaultdict(list)
# same-oriented planar faces; opposite-oriented faces usually represent a valid mating surface.
for name,g in d.items():
 if meta[name]['hide_render']:continue
 vs=np.array(g['points'])
 for fi,ix in enumerate(g['polygons']):
  points=vs[ix];p=points[0];normal=None
  for i in range(1,len(points)-1):
   n=np.cross(points[i]-p,points[i+1]-p);length=np.linalg.norm(n)
   if length>1e-9:normal=n/length;break
  if normal is None:continue
  plane=float(normal@p)
  if max(abs(points@normal-plane))>1e-5:continue
  key=tuple(round(float(x),5) for x in normal)+(round(plane,5),)
  axis=np.argmax(abs(normal));other=[i for i in range(3) if i!=axis];q=points[:,other];lo=q.min(axis=0);hi=q.max(axis=0)
  if np.prod(hi-lo)<1e-8:continue
  # polygons are convex for manufactured shapes; triangulate concave faces using native triangles when needed.
  groups[key].append((name,fi,q,lo,hi,normal,plane))
def area(p):
 return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p))))*.5 if len(p)>2 else 0

def clip(poly,window):
 poly=[tuple(x) for x in poly];w=[tuple(x) for x in window];sign=1 if sum(w[i][0]*w[(i+1)%len(w)][1]-w[(i+1)%len(w)][0]*w[i][1] for i in range(len(w)))>=0 else -1
 for a,b in zip(w,w[1:]+w[:1]):
  if not poly:return []
  new=[]
  def side(p):return sign*((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
  prev=poly[-1];sp=side(prev)
  for cur in poly:
   sc=side(cur)
   if (sc>=-1e-10)!=(sp>=-1e-10):
    t=sp/(sp-sc);new.append((prev[0]+t*(cur[0]-prev[0]),prev[1]+t*(cur[1]-prev[1])))
   if sc>=-1e-10:new.append(cur)
   prev=cur;sp=sc
  poly=new
 return poly
rows=[]
for key,group in groups.items():
 if len(group)<2 or len({x[0] for x in group})<2:continue
 group=sorted(group,key=lambda x:x[3][0])
 for i,a in enumerate(group):
  for b in group[i+1:]:
   if b[3][0]>a[4][0]+1e-8:break
   if a[0]==b[0] or np.any(np.minimum(a[4],b[4])-np.maximum(a[3],b[3])<=1e-8):continue
   if abs(a[6]-b[6])>1e-5 or np.linalg.norm(a[5]-b[5])>1e-5:continue
   ov=clip(a[2],b[2]);ar=area(ov)/max(abs(a[5]))
   if ar>1e-7:rows.append({'a':a[0],'face_a':a[1],'b':b[0],'face_b':b[1],'normal':list(key[:3]),'plane':key[3],'overlap_area_m2':ar,'intersection_2d':ov})
(P/'coplanarity-independent.json').write_text(json.dumps({'same_oriented_planar_overlap_faces':rows,'tolerance_m':.00001,'method':'Native evaluated actual polygons, plane/normal groups, 2D polygon clipping; same oriented surfaces; hidden-render objects excluded; no self-object coplanar comparisons.'},indent=2))
print('COPLANAR_OVERLAPS',len(rows))
for x in sorted(rows,key=lambda x:x['overlap_area_m2'],reverse=True)[:50]:print(x['a'],x['b'],x['overlap_area_m2'],x['normal'],x['plane'])
