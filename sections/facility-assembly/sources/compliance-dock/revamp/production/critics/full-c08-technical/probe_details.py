import bpy,hashlib,json,math,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');O=R/'revamp/production/critics/full-c08-technical';S=R/'module_overhaul_R1.blend';H='d2514e668ea2b24e8b4ede6bde870e12f10c1afd6d6e1892b12c016266bd7b35'
sha=lambda:hashlib.sha256(S.read_bytes()).hexdigest();assert sha()==H
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False);sc=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=sc;dg=bpy.context.evaluated_depsgraph_get()
report={'source_sha256':H,'surface_gaps':[],'winding_defects':[],'cloth_jacobian':[],'coincident_polygon_groups':[]};sh={};faces=collections.defaultdict(list)
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b):return sum(x*y for x,y in zip(a,b))
for ob in sc.objects:
 if ob.type not in {'MESH','CURVE','FONT','SURFACE','META'}:continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vs=[ob.matrix_world@v.co for v in me.vertices];vt=[tuple(float(c) for c in v) for v in vs];tris=[tuple(t.vertices) for t in me.loop_triangles]
 if not vs:ev.to_mesh_clear();continue
 sh[ob.name]={'v':vs,'bvh':BVHTree.FromPolygons(vs,tris,all_triangles=True),'lo':[min(v[k] for v in vs) for k in range(3)],'hi':[max(v[k] for v in vs) for k in range(3)]}
 edge=collections.defaultdict(list)
 for p in me.polygons:
  for i,a in enumerate(p.vertices):
   b=p.vertices[(i+1)%len(p.vertices)];edge[tuple(sorted((a,b)))].append((p.index,a<b))
  key=tuple(sorted(tuple(round(c,6) for c in vt[i]) for i in p.vertices))
  faces[key].append((ob.name,p.index,p.area))
 bad=[(e,v) for e,v in edge.items() if len(v)==2 and v[0][1]==v[1][1]]
 if bad:report['winding_defects'].append({'object':ob.name,'same_direction_shared_edges':len(bad),'witnesses':bad[:3]})
 if all(len(v)==2 for v in edge.values()):
  centre=tuple(sum(p[k] for p in vt)/len(vt) for k in range(3));vol=sum(dot(sub(vt[t[0]],centre),cross(sub(vt[t[1]],centre),sub(vt[t[2]],centre)))/6 for t in tris)
  if vol < -1e-10:report['winding_defects'].append({'object':ob.name,'closed_centered_double_precision_signed_volume':vol})
 layer=me.uv_layers.get('CD_Fabric_Cut_1m')
 if layer:
  measures=[]
  for t in me.loop_triangles:
   a,b,c=[vt[i] for i in t.vertices];e1=sub(b,a);e2=sub(c,a);l1=math.sqrt(dot(e1,e1));crosslen=math.sqrt(dot(cross(e1,e2),cross(e1,e2)));height=crosslen/l1 if l1 else 0
   if height<1e-9:continue
   along=dot(e1,e2)/l1;u0,u1,u2=[layer.data[i].uv.copy() for i in t.loops];d1=u1-u0;d2=u2-u0
   j00=d1.x/l1;j10=d1.y/l1;j01=(d2.x-j00*along)/height;j11=(d2.y-j10*along)/height
   aa=j00*j00+j10*j10;bb=j01*j01+j11*j11;ab=j00*j01+j10*j11;disc=math.sqrt((aa-bb)**2+4*ab*ab);smax=math.sqrt(max(0,(aa+bb+disc)/2));smin=math.sqrt(max(0,(aa+bb-disc)/2));measures.append((crosslen/2,smax/max(smin,1e-20),smin,smax,t.index))
  total=sum(m[0] for m in measures)
  def weighted(col,p):
   acc=0
   for m in sorted(measures,key=lambda x:x[col]):
    acc+=m[0]
    if acc>=total*p:return m[col]
  report['cloth_jacobian'].append({'object':ob.name,'actual_materials':[m.name for m in me.materials if m],'area_m2':total,'area_anisotropy_gt_1_1_fraction':sum(a for a,r,*_ in measures if r>1.1)/total,'area_anisotropy_gt_1_25_fraction':sum(a for a,r,*_ in measures if r>1.25)/total,'area_weighted_anisotropy_p50':weighted(1,.5),'area_weighted_anisotropy_p95':weighted(1,.95),'maximum_anisotropy':max(m[1] for m in measures),'witness_max':max(measures,key=lambda m:m[1]),'stretch_min':min(m[2] for m in measures),'stretch_max':max(m[3] for m in measures)})
 ev.to_mesh_clear()
report['coincident_polygon_groups']=[v for v in faces.values() if len({x[0] for x in v})>1]
islands=[{'Cable tray longitudinal -1.5',*[f'Cable bundle -1.5_{i}' for i in range(4)]},{'P1 corridor overhead sign','P1 deep sign text'}]
for island in islands:
 best=None;lower=None
 for name in island:
  a=sh[name]
  for other,b in sh.items():
   if other in island:continue
   bound=math.sqrt(sum(max(0,a['lo'][k]-b['hi'][k],b['lo'][k]-a['hi'][k])**2 for k in range(3)))
   if lower is None or bound<lower[0]:lower=(bound,name,other)
   if best and bound>best['distance_m']:continue
   for p in a['v']:
    q,n,fi,d=b['bvh'].find_nearest(p)
    if q is not None and (best is None or d<best['distance_m']):best={'from':name,'to':other,'from_surface_vertex':list(p),'to_surface_point':list(q),'target_triangle':fi,'distance_m':d}
 report['surface_gaps'].append({'island':sorted(island),'rigorous_all_external_surface_gap_lower_bound_m':lower[0],'lower_bound_pair':lower[1:],'actual_nearest_vertex_to_surface_witness':best})
for name,p,d in [('Cable tray to truss',(-1.5,2.2,3.51),(0,0,1)),('P1 sign to ceiling',(0,-1.85,2.45),(0,0,1))]:
 hits=[]
 for oname,b in sh.items():
  q,n,fi,length=b['bvh'].ray_cast(Vector(p)+Vector(d)*.00001,Vector(d),1)
  if q is not None:hits.append({'object':oname,'point':list(q),'distance_from_query_m':length+.00001,'triangle':fi})
 report['surface_gaps'].append({'ray':name,'from':p,'direction':d,'hits':sorted(hits,key=lambda v:v['distance_from_query_m'])[:4]})
assert sha()==H
(O/'details.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
