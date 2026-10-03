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
# Explicit intended roots, rather than nearby object or bounding-box searches.
for i in range(4):
 suf='' if i==0 else '.%03d'%i
 pair('Chamber sole shoe'+suf,'Floor',(0,0,-1),'OCRU floor shoe bearing')
 pair('Fabricated chamber foot'+suf,'Chamber sole shoe'+suf,(0,0,-1),'fabricated foot to sole shoe')
 pair('Bed non-marking foot'+suf,'Floor',(0,0,-1),'recovery foot bearing')
 pair('Tubular recovery leg'+suf,'Bed non-marking foot'+suf,(0,0,-1),'recovery tubular leg socket')
 pair('Supply bench leg'+suf,'Floor',(0,0,-1),'bench floor bearing')
 pair('Console steel leg'+suf,'Floor',(0,0,-1),'console floor bearing')
 pair('Caster rubber tyre'+suf,'Floor',(0,0,-1),'cart tyre floor bearing')
 pair('Cabinet wall spacer'+suf,'East wall',(1,0,0),'cabinet spacer to wall')
 pair('Supply cabinet back','Cabinet wall spacer'+suf,(1,0,0),'cabinet back to wall spacer')
for name in ['Reserve folded side','Reserve folded side.001','Reserve folded back']:
 pair(name,'Battery plinth',(0,0,-1),'reserve folded chassis to plinth')
pair('Battery plinth','Floor',(0,0,-1),'reserve floor bearing')
for suf in ('','.001'):
 pair('Reserve battery module'+suf,'MED_R2 | Battery resilient bearing pad '+suf,(0,0,-1),'battery downward bearing pad')
 pair('MED_R2 | Battery resilient bearing pad '+suf,'Battery supported drawer rail'+suf,(0,0,-1),'battery pad on drawer rail')
 pair('Battery supported drawer rail'+suf,'MED_R2 | Reserve drawer rear mounting return '+suf,(0,1,0),'drawer rail back fixing')
 pair('MED_R2 | Reserve drawer rear mounting return '+suf,'Reserve folded back',(0,1,0),'reserve rear return to back sheet')
 pair('Jamb folded cover'+suf,'Access jamb graphite return'+suf,(-1,0,0),'OCRU folded cover retained backing')
 pair('Access jamb graphite return'+suf,'Chamber structural upright'+suf,(0,-1 if not suf else 1,0),'OCRU jamb backing to structural end upright')
 pair('Chamber structural upright'+suf,'Sealed chamber pan',(0,0,-1),'OCRU structural end upright to pan')
 pair('Formed end service panel'+suf,'Chamber structural upright'+suf,(0,1 if not suf else -1,0),'OCRU manufactured service end panel to upright')
 pair('Cabinet formed edge'+suf,'Supply cabinet back',(1,0,0),'cabinet edge return to back')
 pair('Clear cabinet sliding pane'+suf,'MED_R2 | Glazing captive slide guide '+suf+' 1.46',(1,0,0),'captured lower sliding glazing guide')
 pair('MED_R2 | Glazing captive slide guide '+suf+' 1.46','Cabinet formed edge'+suf,(1,0,0),'sliding guide to cabinet edge')
 pair('Berth pedestal foot'+suf,'Sealed chamber pan',(0,0,-1),'treatment lift base to chamber pan')
 pair('Telescopic lift outer'+suf,'Berth pedestal foot'+suf,(0,0,-1),'treatment column to base socket')
 pair('Rail support crosshead'+suf,'Telescopic lift inner'+suf,(0,0,-1),'treatment crosshead to lift inner')
for suf in ('','.001','.002'):
 pair('Supply cabinet shelf'+suf,'Supply cabinet back',(1,0,0),'stock shelf back return')
for i in range(12):
 suf='' if i==0 else '.%03d'%i
 pair('Sealed supply case'+suf,'MED_R2 | Sterile stock shelf bearing '+str(i),(0,0,-1),'sterile case downward load to paired pressed feet')
 reg=json.loads((R/'revamp-review/production/support-registry.json').read_text());t=next(x['target'] for x in reg if x['object']=='MED_R2 | Sterile stock shelf bearing '+str(i))
 pair('MED_R2 | Sterile stock shelf bearing '+str(i),t,(0,0,-1),'pressed stock feet downward load to intended shelf')
for i in range(12):
 suf='' if i==0 else '.%03d'%i; shelf='' if i//3==0 else '.%03d'%(i//3)
 pair('Cartridge bottom seal'+suf,'Folded storage shelf'+shelf,(0,0,-1),'cartridge end-seal downward shelf bearing')
for i in range(3):
 suf='' if i==0 else '.%03d'%i
 pair('Sealed consumable carton'+suf,'Bench lower shelf',(0,0,-1),'bench stored carton downward shelf bearing')
pair('Sink load-bearing wall packer','East wall',(1,0,0),'sink packer at intended wall')
pair('Sink wall bracket','Sink load-bearing wall packer',(1,0,0),'sink bracket to packer')
pair('Basin bottom','Sink wall bracket',(0,0,-1),'basin resting on wall bracket')
pair('Handwash soap dispenser','East wall',(1,0,0),'wall soap dispenser rear mounting')
for suf in ('','.001'):pair('Identity wall spacer'+suf,'East wall',(1,0,0),'identity sign spacer wall mount')
pair('Inner removable liner.001','West wall',(-1,0,0),'rear treatment liner wall-backed sheet')
pair('Receiver cast housing','MED_R2 | Receiver fixed steel mounting arm',(0,-1,0),'receiver retained fixed arm')
pair('MED_R2 | Receiver fixed steel mounting arm','Jamb folded cover',(0,-1,0),'receiver arm to retained jamb cover')
for z in ('1.12','1.4'):
 pair('Suit service enclosure','MED_R2 | Suit service fixed mounting arm '+z,(0,1,0),'suit service fixed arm')
 pair('MED_R2 | Suit service fixed mounting arm '+z,'Jamb folded cover.001',(0,1,0),'suit arm to retained jamb cover')
pair('Decon ceiling lamp','MED_R2 | Decon fixture ceiling mounting return',(0,0,1),'decon ceiling fixture mounting return')
pair('MED_R2 | Decon fixture ceiling mounting return','Decon ceiling',(0,0,1),'decon mounting return to ceiling')
pair('Recovery release slip','MED_R2 | Recovery foot chart holder',(0,0,-1),'recovery card folded chart holder')
pair('MED_R2 | Recovery foot chart holder','Recovery bed pan',(0,0,-1),'chart holder lower folded flange')
reports=[]
for name,target,d,mechanism in pairs:
 if name not in s.objects or target not in s.objects:
  reports.append({'object':name,'target':target,'status':'MISSING','mechanism':mechanism});continue
 v,f,ed,ot=data(name);_,_,_,tree=data(target);direction=Vector(d).normalized();candidates=list(v)
 for face in f:candidates.append(sum((v[i] for i in face),Vector())/len(face))
 for ai,bi in ed:
  a,b=v[ai],v[bi];delta=b-a;candidates.append((a+b)/2)
  if delta.length>1e-10:
   hit=tree.ray_cast(a,delta.normalized(),delta.length)[0]
   if hit is not None:candidates.append(hit)
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
(W/'independent-support.json').write_text(json.dumps(result,indent=2));print('INDEPENDENT_SUPPORT',len(reports),sum(r['status']=='CONTACT' for r in reports),flush=True)
