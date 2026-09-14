import bpy,json,os,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];sid=os.environ.get('EXTERIOR_SECTION','compliance-dock');rev=os.environ.get('EXTERIOR_REVISION','R05');out=ROOT/'exteriors'/sid
bpy.ops.wm.open_mainfile(filepath=str(out/f'exterior-{rev}.blend'),load_ui=False)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
ext=bpy.data.collections['EXTERIOR_'+sid]
layout=json.loads((ROOT/'production/LAYOUT.json').read_text());pose=layout['placements'][sid]
transform=Matrix.Translation(Vector(pose['translation']))@Matrix.Rotation(math.radians(pose['rotation_z_degrees']),4,'Z')
def bounds(ob,trans):
 eo=ob.evaluated_get(dg);pts=[trans@eo.matrix_world@Vector(p) for p in eo.bound_box]
 return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
def overlaps(a,b):return all(min(a[1][i],b[1][i])-max(a[0][i],b[0][i])>.003 for i in range(3))
portals_by_sid={
 'mine':[('Facility route',[[-2.09,-30,.01],[2.09,-14,3.37]]),('Adit',[[-2.92,-.4,.01],[2.92,1,4.89]])],
 'refinery':[('Personnel',[[-3,-9,.01],[-.6,-6.43,2.5]]),('Receiving',[[-10,-5.53,.01],[-7.50,-2.58,3]]),('Dispatch',[[7.50,-5.53,.01],[10,-2.58,3]]),('West utility',[[-9,-1.51,3.84],[-7.50,-1.28,4.08]]),('East utility',[[7.50,.31,3.84],[9,.55,4.08]]),('Exhaust',[[3.98,6.43,3.25],[4.33,8,3.61]])],
 'fuel-corridor':[('F01',[[-1.3,-3,.01],[1.3,.01,3]]),('F02',[[11.7,23.99,.01],[16.7,27,5]]),('S01',[[-8,16.4,.01],[-5.39,18.4,2.5]]),('S02',[[5.6,20.99,.01],[7.6,24,2.5]]),('S03',[[16.39,14.8,.01],[19,17.2,3]])],
 'reactor-room':[('Fuel portal',[[-2.5,10.8,.01],[2.5,15,5]]),('Main portal',[[-15,-3,.01],[-10.8,3,5.5]]),('Control portal',[[10.8,1.6,.01],[15,5.6,5]])],
 'cooling-plant':[('Entry',[[-2.5,-4,.01],[2.5,.6,5]]),('Overhead reserve',[[-2.65,0,5],[2.65,.6,5.8]]),('Front plane contract',[[-20,-10,-2],[20,0,15]]),('CW supply',[[4.79,-1,3.56],[5.19,.01,3.96]]),('CW return',[[-5.23,-1,3.56],[-4.83,.01,3.96]]),('Reserve',[[5.20,-1,2.93],[5.34,.01,3.07]]),('Secondary 1',[[5.49,5.65,2.85],[6.5,5.95,3.15]]),('Secondary 2',[[5.49,7.7,3.15],[6.5,8,3.45]]),('Drain',[[5.49,9.85,-.3],[6.5,10.15,.1]])],
 'condenser-bay':[('D01 stub',[[-1,-4,.01],[1,0,2.4]]),('U04',[[1.75,3.30,5.99],[4.25,4.8,7.3]]),('U02',[[7.75,-1,5.27],[8.05,.01,5.57]]),('CW supply',[[9.59,3,2.95],[10.6,3.4,3.35]]),('CW return',[[9.59,4.7,2.95],[10.6,5.1,3.35]]),('DRAIN',[[9.59,8.35,-.3],[10.6,8.75,.15]]),('VENT',[[2.8,9.39,5.35],[3.2,10.5,5.75]])],
 'compliance-dock':[('P1',[[-1.2,-3,.01],[1.2,0,2.6]]),('P2',[[-2.3,15.75,.01],[2.3,19,3.5]])],
 'spawn-room':[('Original entry',[[-.65,-2,.01],[.65,-.33,2.4]]),('Rear connection allowance',[[-1.7,12.3,.01],[1.7,14.3,3.4]])],
 'medical-reanimation':[('Stretcher entry',[[-1.1,-3,.01],[1.1,0,2.5]])],
 'waste-storage':[('Receiving',[[-1.5,-3,.01],[1.5,0,3.2]]),('Dispatch',[[-1.2,18,.01],[1.2,21,2.8]]),('Personnel',[[6,1.8,.01],[8,3,2.3]])],
 'electrical-room':[('D01',[[-1.2,-3,.01],[1.2,0,2.7]]),('D02',[[-1.2,16.4,.01],[1.2,19,2.7]]),('U01',[[-4.52,-1,3.73],[-4.12,0,4.03]]),('U02',[[-4.68,16.4,3.64],[-3.96,18,4.12]]),('U03',[[8.3,13.9,2.7],[9,14.1,2.9]])],
 'turbine-room':[('D01',[[-1.2,-3,.01],[1.2,0,2.7]]),('D02',[[-1.2,24,.01],[1.2,27,2.7]]),('U01',[[8.2,-1,4.7],[8.6,.01,5.1]]),('U02 cap',[[9.4,-1,.35],[9.6,.01,.55]]),('U03',[[-4.52,24,3.73],[-4.12,26,4.03]]),('U04',[[3.35,10.70,-1],[5.85,12.2,.01]])],
}
portals=portals_by_sid[sid]
hits=[];reservations=[];records=[]
for ob in ext.objects:
 if ob.type not in ['MESH','CURVE','FONT']:continue
 b=bounds(ob,Matrix.Identity(4));world=bounds(ob,transform)
 records.append({'name':ob.name,'bounds_local':b,'bounds_world':world,'runtime_binding':ob.get('runtime_binding')})
 if not ob.get('runtime_binding'):
  for name,p in portals:
   if overlaps(b,p):hits.append([name,ob.name])
  if sid=='reactor-room':
   cooling_frame=(Matrix.Translation(Vector((8.4,-8.4,0)))@Matrix.Rotation(math.radians(-135),4,'Z')).inverted()
   if overlaps(bounds(ob,cooling_frame),[[-2.5,0,.01],[2.5,3.7,5]]):hits.append(['Diagonal cooling portal',ob.name])
 for v in layout['reserved_volumes']:
  c=v['center'];s=v['size'];vb=[[c[i]-s[i]/2 for i in range(3)],[c[i]+s[i]/2 for i in range(3)]]
  if overlaps(world,vb):reservations.append([v['id'],ob.name])
report={'revision':rev,'portal_solid_intrusions':hits,'reserved_volume_intrusions':reservations,'records':records,'status':'PASS' if not hits and not reservations else 'FAIL','scope':'Evaluated object bounding boxes; closed-pose door ribs explicitly require engine leaf binding. No runtime animation acceptance.'}
(out/f'audit-{rev}.json').write_text(json.dumps(report,indent=2));print('EXTERIOR_AUDIT',report['status'],hits,reservations,flush=True)
