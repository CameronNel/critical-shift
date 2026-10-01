import bpy,json,importlib.util,math,re
from pathlib import Path
from mathutils import Vector
import numpy as np
from collections import defaultdict
ROOT=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');OUT=ROOT/'revamp/production/critics/full-f04-technical';S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S;DG=bpy.context.evaluated_depsgraph_get()
spec=importlib.util.spec_from_file_location('dv',ROOT/'validate_dock.py');dv=importlib.util.module_from_spec(spec);spec.loader.exec_module(dv);shapes={}
def shape(n):
 if n not in shapes:shapes[n]=dv.Shape(S.objects[n],DG)
 return shapes[n]
r={'scope':'Supplemental true-surface and consumed-chart probes','coplanar':[],'drawer_end_fits':[],'cloth_edge_bearing':[],'stable_signed_volumes':[]}
# Correct volume arithmetic: float64, translate each connected component near zero.
prior=json.loads((OUT/'probe.json').read_text())
for rec in prior['topology']:
 if not rec['negative_closed_components']:continue
 sh=shape(rec['object']);edges=defaultdict(list);adj=defaultdict(list)
 for i,t in enumerate(sh.triangles):
  for a,b in zip(t,t[1:]+t[:1]):edges[tuple(sorted((a,b)))].append(i)
 for fs in edges.values():
  if len(fs)==2:adj[fs[0]].append(fs[1]);adj[fs[1]].append(fs[0])
 seen=set();vol=[]
 for i in range(len(sh.triangles)):
  if i in seen:continue
  component=[];todo=[i];seen.add(i)
  while todo:
   f=todo.pop();component.append(f)
   for n in adj[f]:
    if n not in seen:seen.add(n);todo.append(n)
  origin=np.array(sh.vertices[sh.triangles[i][0]],dtype=np.float64)
  total=0.
  for f in component:
   p=[np.array(sh.vertices[v],dtype=np.float64)-origin for v in sh.triangles[f]];total+=np.dot(p[0],np.cross(p[1],p[2]))/6
  vol.append(total)
 r['stable_signed_volumes'].append({'object':sh.name,'components':len(vol),'minimum':min(vol),'negative_components':sum(v<-1e-12 for v in vol)})
# Actual pull boundary loops and stud surfaces, not centerline ray hits on uncapped pipes.
for k,y in enumerate([8.3,9.1]):
 st=shape(f'CD | Joined CD | Office file cabinet {k} / steel')
 for j in range(4):
  sh=shape(f'Drawer pull {k}_{j}');edge=defaultdict(int)
  for t in sh.triangles:
   for a,b in zip(t,t[1:]+t[:1]):edge[tuple(sorted((a,b)))]+=1
  adj=defaultdict(list)
  for (a,b),n in edge.items():
   if n==1:adj[a].append(b);adj[b].append(a)
  seen=set()
  for v in adj:
   if v in seen:continue
   todo=[v];ring=[];seen.add(v)
   while todo:
    w=todo.pop();ring.append(w)
    for u in adj[w]:
     if u not in seen:seen.add(u);todo.append(u)
   p=sum((sh.vertices[v] for v in ring),Vector())/len(ring);nearest=st.bvh.find_nearest(p);dist=[];wits=[]
   for v in ring:
    q=sh.vertices[v];loc,n,face,d=st.bvh.find_nearest(q);dist.append(d);wits.append(dict(pull_surface=list(q),stud_surface=list(loc),distance=d))
   r['drawer_end_fits'].append(dict(object=sh.name,end_center=list(p),end_plane_axis_x_range=[min(sh.vertices[v].x for v in ring),max(sh.vertices[v].x for v in ring)],stud_nearest_center=list(nearest[0]),surface_distance_range=[min(dist),max(dist)],closest_surface_witness=min(wits,key=lambda x:x['distance']),classification='Uncapped tube mouth; stud fits inside with approximately 1mm radial clearance, not a default planar seat'))
# Continuous top/bottom cut chart distortion at exact worst triangle and quantiles.
o=S.objects['Covered Trolley Draped Tarp'];e=o.evaluated_get(DG);m=e.to_mesh();m.calc_loop_triangles();layer=m.uv_layers['CD_Fabric_Cut_1m'];values=[]
for t in m.loop_triangles:
 p=[o.matrix_world@m.vertices[i].co for i in t.vertices];u=[layer.data[i].uv for i in t.loops];q0=p[1]-p[0];q1=p[2]-p[0]
 if q0.length<1e-12:continue
 axis=q0.normalized();g=np.array([[q0.length,q1.dot(axis)],[0,max(0,q1.length_squared-q1.dot(axis)**2)**.5]])
 if abs(np.linalg.det(g))<1e-12:continue
 J=np.column_stack((np.array(u[1])-u[0],np.array(u[2])-u[0]))@np.linalg.inv(g);sv=np.linalg.svd(J,compute_uv=False)
 if min(sv)>1e-6:values.append((float(min(sv)),float(max(sv)),int(t.index),[list(x) for x in p],[list(x) for x in u]))
r['cloth_cut_chart']={'worst_maximum_singular_value':max(values,key=lambda x:x[1]),'worst_minimum_singular_value':min(values,key=lambda x:x[0]),'stretch_quantiles':list(np.quantile([x[1] for x in values],[.5,.9,.95,.99,1])),'compression_quantiles':list(np.quantile([x[0] for x in values],[0,.01,.05,.1,.5]))}
e.to_mesh_clear()
# Perimeter drape over the deck outer edges, flexible contact measured separately from flat seats.
cloth=shape('Covered Trolley Draped Tarp');bed=shape('Trolley bed perimeter')
for x in [-6.225,-5.475]:
 samples=[]
 for yi in range(45):
  y=12.2+2.1*yi/44;hc=cloth.ray(Vector((x,y,1.2)),Vector((0,0,-1)),.8);hb=bed.ray(Vector((x,y,1.1)),Vector((0,0,-1)),.6)
  if hc and hb:
   # Cloth lower skin second hit, or nearest .002 below outside upper skin.
   hc2=cloth.ray(hc['point']-Vector((0,0,.00001)),Vector((0,0,-1)),.03)
   c=hc2 if hc2 else hc;samples.append({'cloth_lower':list(c['point']),'deck':list(hb['point']),'gap':c['point'].z-hb['point'].z,'cloth_normal':list(c['normal'])})
 r['cloth_edge_bearing'].append({'x':x,'samples':len(samples),'gap_range':[min(q['gap'] for q in samples),max(q['gap'] for q in samples)],'worst_gap':max(samples,key=lambda q:q['gap']),'worst_penetration':min(samples,key=lambda q:q['gap']),'classification':'Flexible cover-over-edge; flat bearing angle rule is inapplicable to a drape'})
# Geometry overlap witnesses: same-facing plane distance<=2um; exact projected triangle clipping.
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def clipped(A,B):
 poly=[np.array(x) for x in A];clip=[np.array(x) for x in B]
 if cross(clip[1]-clip[0],clip[2]-clip[0])<0:clip=clip[::-1]
 for a,b in zip(clip,clip[1:]+clip[:1]):
  new=[]
  if not poly:break
  for p,q in zip(poly,poly[1:]+poly[:1]):
   dp=cross(b-a,p-a);dq=cross(b-a,q-a);ip=dp>=-1e-10;iq=dq>=-1e-10
   if ip:new.append(p)
   if ip!=iq:new.append(p+(q-p)*dp/(dp-dq))
  poly=new
 if len(poly)<3:return 0,None
 area=abs(sum(cross(a,b) for a,b in zip(poly,poly[1:]+poly[:1])))/2
 return area,np.mean(poly,axis=0)
patterns=['North wall','North lintel','P2 frame','Office front','Office rear','D1 frame','D2 frame','Scanner portal','Scanner lintel face','Terminal monitor housing','Terminal CRT screen bezel','Terminal screen face','Conveyor monitor housing','Conveyor monitor screen','Floor slab','Drainage trench','P1 threshold','Support privacy screen wall','Support screen']
names=[o.name for o in S.objects if o.type=='MESH' and any(o.name.startswith(p) for p in patterns)]
for ai,an in enumerate(names):
 a=shape(an)
 for bn in names[ai+1:]:
  b=shape(bn)
  if not dv.overlaps(a.bounds,b.bounds,.000002):continue
  area=0;witness=None
  for i,ta in enumerate(a.triangles):
   na=a.normals[i]
   if na.length<.5:continue
   pa=[a.vertices[v] for v in ta];ab=dv.bounds(pa);axis=max(range(3),key=lambda k:abs(na[k]));keep=[k for k in range(3) if k!=axis]
   for j,tb in enumerate(b.triangles):
    if na.dot(b.normals[j])<.999999:continue
    pb=[b.vertices[v] for v in tb]
    if max(abs((p-pa[0]).dot(na)) for p in pb)>.000002 or not dv.overlaps(ab,dv.bounds(pb),.000002):continue
    ar,centre=clipped([[p[k] for k in keep] for p in pa],[[p[k] for k in keep] for p in pb])
    if ar<1e-9:continue
    ar/=abs(na[axis]);area+=ar
    if witness is None:
     q=Vector((0,0,0));q[keep[0]]=float(centre[0]);q[keep[1]]=float(centre[1]);q[axis]=(na.dot(pa[0])-sum(na[k]*q[k] for k in keep))/na[axis]
     witness=dict(point=list(q),normal=list(na),a_triangle=i,b_triangle=j,intersection_area_m2=ar)
  if area>1e-7:r['coplanar'].append(dict(a=an,b=bn,same_facing_overlap_area_m2=area,witness=witness))
r['webbing_nearest']=[]
for j in range(4):
 sh=shape('Trolley strap '+str(j));rows=[]
 for p in sh.vertices[:50]:
  loc,n,fi,d=cloth.bvh.find_nearest(p)
  if loc is not None:rows.append(dict(strap_surface=list(p),cloth_surface=list(loc),distance_m=d,signed_gap_m=(p-loc).dot(cloth.normals[fi]),cloth_triangle=fi,cloth_normal=list(cloth.normals[fi])))
 r['webbing_nearest'].append(dict(object=sh.name,max_distance=max(rows,key=lambda x:x['distance_m']),max_signed_gap=max(rows,key=lambda x:x['signed_gap_m']),min_signed_gap=min(rows,key=lambda x:x['signed_gap_m'])))
print('SUPPLEMENT_COMPLETE',len(r['coplanar']),flush=True)
(OUT/'supplement.json').write_text(json.dumps(dv.json_safe(r),indent=2,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)))
