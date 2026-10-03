import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation');W=R/'revamp-review/production/critics/cycle-16-technical-witnesses';SOURCE=R/'module_overhaul_R2.blend';BEFORE=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
with bpy.data.libraries.load(str(SOURCE),link=False) as (a,b):b.scenes=['REANIMATION_EDIT_LOCAL']
s=bpy.data.scenes['REANIMATION_EDIT_LOCAL'];bpy.context.window.scene=s;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cache={}
def data(name):
 if name in cache:return cache[name]
 o=s.objects[name];e=o.evaluated_get(dg);m=e.to_mesh();v=[o.matrix_world@x.co for x in m.vertices];f=[tuple(x.vertices) for x in m.polygons];edges=[tuple(x.vertices) for x in m.edges];t=BVHTree.FromPolygons(v,f)
 cache[name]=(v,f,edges,t);e.to_mesh_clear();return cache[name]
pairs=[]
def pair(o,t,d,mechanism):pairs.append((o,t,d,mechanism))
for suf in ('','.001'):
 pair('Cartridge bank formed upright'+suf,'Floor',(0,0,-1),'cartridge rack upright floor bearing')
 pair('Chamber roof load beam','Chamber structural upright'+suf,(0,0,-1),'OCRU roof beam supported at structural ends')
 pair('Chassis longitudinal channel'+suf,'Fabricated chamber foot'+('' if not suf else '.001'),(0,0,-1),'OCRU chassis floor foot bearing')
for i in range(7):
 suf='' if i==0 else '.%03d'%i
 for upr,di in [('Cartridge bank formed upright',(-1,0,0)),('Cartridge bank formed upright.001',(1,0,0))]:
  pair('Folded storage shelf'+suf,upr,di,'folded rack shelf fixed to structural upright')
for suf in ('','.001','.002'):
 pair('Inner removable liner'+suf,'Rear machine skin',(-1,0,0),'treatment liner mounted to retained rear skin')
for i in range(5):
 suf='' if i==0 else '.%03d'%i
 pair('Stool glide'+suf,'Floor',(0,0,-1),'operator stool glide floor bearing')
reports=[]
for name,target,d,mechanism in pairs:
 if name not in s.objects or target not in s.objects:
  reports.append({'object':name,'target':target,'status':'MISSING','mechanism':mechanism});continue
 v,f,ed,ot=data(name);tv,tf,te,tree=data(target);direction=Vector(d).normalized();candidates=list(v)
 for face in f:candidates.append(sum((v[i] for i in face),Vector())/len(face))
 for ai,bi in ed:
  a,b=v[ai],v[bi];delta=b-a;candidates.append((a+b)/2)
  if delta.length>1e-10:
   hit=tree.ray_cast(a,delta.normalized(),delta.length)[0]
   if hit is not None:candidates.append(hit)
 # Independently project actual target face samples back onto the source.
 # This catches a small mount in the interior of a large source panel.
 for face in tf:
  centre=sum((tv[i] for i in face),Vector())/len(face)
  point=ot.ray_cast(centre+direction*.03,-direction,1.0)[0]
  if point is not None:candidates.append(point)
 for ai,bi in te:
  a,b=tv[ai],tv[bi];delta=b-a
  if delta.length>1e-10:
   point=ot.ray_cast(a,delta.normalized(),delta.length)[0]
   if point is not None:candidates.append(point)
 hits=[]
 for point in candidates:
  surface,normal,index,distance=tree.ray_cast(point-direction*.03,direction,1.0)
  if surface is None:continue
  angle=math.degrees(normal.angle(-direction));gap=distance-.03
  if angle<=12:
   hits.append({'signed_gap_m':gap,'normal_angle_degrees':angle,'object_point':list(point),'target_surface':list(surface),'target_face_index':index,'source_witness_distance_m':ot.find_nearest(point)[3]})
 valid=[x for x in hits if -.002-1e-7<=x['signed_gap_m']<=.005+1e-7 and x['source_witness_distance_m']<=.0011]
 best=min(valid or hits,key=lambda x:abs(x['signed_gap_m'])) if hits else None
 reports.append({'object':name,'target':target,'approach_world':list(direction),'mechanism':mechanism,'samples':len(candidates),'oriented_hits':len(hits),'passing_actual_surface_witnesses':len(valid),'best':best,'status':'CONTACT' if valid else 'REVIEW_DIRECTION_OR_CLEARANCE'})
result={'source_sha256':BEFORE,'method':'Independently specified intended support pairs; evaluated polygon BVH, face/vertex/edge samples and real edge intersections. Fixed bearing/mount directions; ambiguous misses require mechanism review rather than automatic blocker.','reports':reports,'source_sha256_after':hashlib.sha256(SOURCE.read_bytes()).hexdigest()};assert result['source_sha256_after']==BEFORE
(W/'independent-root-extension.json').write_text(json.dumps(result,indent=2));print('INDEPENDENT_SUPPORT',len(reports),sum(r['status']=='CONTACT' for r in reports),flush=True)
