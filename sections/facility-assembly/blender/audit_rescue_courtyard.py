import bpy,json,math,os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'connections/rescue-courtyard';REV=os.environ.get('COURTYARD_REVISION','R01')
bpy.ops.wm.open_mainfile(filepath=str(OUT/f'review-{REV}.blend'),load_ui=False)
L=json.loads((ROOT/'production/LAYOUT_CONNECTIONS_PLAN.json').read_text());hits=[]
for ob in bpy.data.collections['CONNECTION_C01_RESCUE_COURTYARD'].objects:
 if ob.type not in {'MESH','CURVE','FONT'}:continue
 p=[ob.matrix_world@Vector(c) for c in ob.bound_box];lo=Vector(tuple(min(q[i] for q in p) for i in range(3)));hi=Vector(tuple(max(q[i] for q in p) for i in range(3)))
 if hi.z<.08 or lo.z>2.25:continue
 for r in L['routes']:
  if r['id']=='R19':continue
  for a,b in zip(r['points'],r['points'][1:]):
   a,b=Vector(a),Vector(b);v=b-a
   if abs(a.z)>.1 or abs(b.z)>.1 or v.xy.length<.01:continue
   u=v.xy.normalized();n=Vector((-u.y,u.x));corners=[Vector((x,y)) for x in [lo.x,hi.x] for y in [lo.y,hi.y]]
   along=[(q-a.xy).dot(u) for q in corners];cross=[(q-a.xy).dot(n) for q in corners]
   if max(along)>0 and min(along)<v.xy.length and max(cross)>-r['width_m']/2 and min(cross)<r['width_m']/2:
    hits.append({'object':ob.name,'route':r['id']});break
report={'method':'Conservative world AABB vs route strip SAT projections, 0.08 to 2.25m obstacle band. Floors and overhead canopy omitted. Source rooms separately checked by planning audit.','candidates':hits,'pass':not hits}
(OUT/f'CLEARANCE_{REV}.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))

