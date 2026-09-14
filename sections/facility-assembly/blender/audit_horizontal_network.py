import bpy,json,os,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'connections/network';REV=os.environ.get('NETWORK_REVISION','R02')
bpy.ops.wm.open_mainfile(filepath=str(OUT/f'review-{REV}.blend'),load_ui=False)
L=json.loads((ROOT/'production/LAYOUT_CONNECTIONS_PLAN.json').read_text());hits=[];count=0
for ob in bpy.data.collections['09_FINISHED_HORIZONTAL_CONNECTIONS'].objects:
 if ob.type not in {'MESH','CURVE','FONT'}:continue
 p=[ob.matrix_world@Vector(c) for c in ob.bound_box];lo=min(v.z for v in p);hi=max(v.z for v in p)
 if hi<.08 or lo>2.3:continue
 count+=1
 # Exact projection separating-axis check of convex projected object bounds and route rectangle.
 hull=[p[i].xy for i in [0,4,6,2]]
 if len({(round(v.x,5),round(v.y,5)) for v in hull})<3:hull=[Vector((min(v.x for v in p),min(v.y for v in p))),Vector((max(v.x for v in p),min(v.y for v in p))),Vector((max(v.x for v in p),max(v.y for v in p))),Vector((min(v.x for v in p),max(v.y for v in p)))]
 def overlap(poly1,poly2):
  for poly in [poly1,poly2]:
   for a,b in zip(poly,poly[1:]+poly[:1]):
    e=b-a
    if e.length<1e-6:continue
    n=Vector((-e.y,e.x)).normalized();x=[v.dot(n) for v in poly1];y=[v.dot(n) for v in poly2]
    if max(x)<=min(y)+.015 or max(y)<=min(x)+.015:return False
  return True
 for r in L['routes']:
  for a,b in zip(r['points'],r['points'][1:]):
   if abs(a[2])>.1 or abs(b[2])>.1:continue
   a,b=Vector(a).xy,Vector(b).xy;v=b-a
   if v.length<.01:continue
   n=Vector((-v.y,v.x)).normalized()*r['width_m']/2;rect=[a+n,b+n,b-n,a-n]
   if overlap(hull,rect):hits.append({'object':ob.name,'route':r['id']});break
report={'revision':REV,'objects_checked':count,'method':'Projected oriented object-bound SAT against all route rectangles, z=0.08 to 2.3m. Not engine collision; source thresholds remain step 2.','obstacle_candidates':hits,'pass':not hits}
(OUT/f'CLEARANCE_{REV}.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
