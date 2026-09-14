"""Versioned assembly transforms and reserved, UNBUILT connection geometry."""
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# All room scales remain 1.0. +Z up; metre coordinates.
placements={
 'spawn-room':([-28,0,0],0),
 'mine':([-38,-29,0],90),
 'refinery':([-4.084283176858165,-16.606663706334526,0],90),
 'fuel-corridor':([0,0,0],0),
 'reactor-room':([14.2,46.5,0],180),
 'cooling-plant':([-2.5,63.2,0],45),
 'turbine-room':([40.9,46.5,0],-90),
 'condenser-bay':([48.3,44.9,-6],-90),
 'electrical-room':([66,27,0],180),
 'waste-storage':([66,2.6,0],180),
 'medical-reanimation':([-29,37,0],0),
 'compliance-dock':([-49,16,0],90),
}
def world(sid,p):
 t,a=placements[sid];c=math.cos(math.radians(a));s=math.sin(math.radians(a))
 return [round(t[0]+c*p[0]-s*p[1],5),round(t[1]+s*p[0]+c*p[1],5),round(t[2]+(p[2] if len(p)>2 else 0),5)]
ports={
 'spawn.exit':world('spawn-room',[0,12.3,0]),
 'mine.entry':world('mine',[0,-27.51,0]),
 'refinery.intake':world('refinery',[-8.606663706334526,-4.084283176858165,0]),
 'refinery.dispatch':world('refinery',[8.606663706334526,-4.084283176858165,0]),
 'refinery.personnel':world('refinery',[-1.8,-6.734283,0]),
 'fuel.entry':[0,0,0],'fuel.reactor':[14.2,24,0],'fuel.service':[-5.4,17.4,0],'fuel.clean':[6.6,21,0],'fuel.waste':[16.4,16,0],
 'reactor.fuel':world('reactor-room',[0,14.5,0]),
 'reactor.turbine':world('reactor-room',[-14.5,0,0]),
 'reactor.cooling':world('reactor-room',[11.0162950904,-11.0162950904,0]),
 'cooling.entry':world('cooling-plant',[0,0,0]),
 'turbine.entry':world('turbine-room',[0,0,0]),'turbine.exit':world('turbine-room',[0,25.4,0]),
 'condenser.entry':world('condenser-bay',[0,-2.56,0]),
 'electrical.entry':world('electrical-room',[0,-.25,0]),'electrical.exit':world('electrical-room',[0,16.97,0]),
 'waste.entry':world('waste-storage',[0,-.32,0]),'waste.personnel':world('waste-storage',[6.3,2.4,0]),'waste.dispatch':world('waste-storage',[0,20.43,0]),
 'medical.entry':world('medical-reanimation',[0,-.69,0]),
 'compliance.entry':world('compliance-dock',[0,-2.1,0]),'compliance.arrival':world('compliance-dock',[0,16.6,0]),
}
routes=[]
def route(id,kind,width,points,note=''):
 pts=[ports[x] if isinstance(x,str) else list(x) for x in points]
 routes.append(dict(id=id,kind=kind,width_m=width,height_m=3.5 if kind!='freight' else 4.5,points=pts,status='RESERVED_UNBUILT',note=note))
route('R01','freight',5,['mine.entry',[0,-29,0],'refinery.intake'],'Cart approach; mine descending adit retained, no invented mine lift.')
route('R02','freight',4.5,['refinery.dispatch','fuel.entry'],'Eight metre connector reserve; refinery sill/bollards stay unchanged.')
route('R03','freight',6,['fuel.reactor','reactor.fuel'],'Eight metre gap; source reactor doors remain closed until integration.')
route('R04','service',4,['reactor.turbine','turbine.entry'],'12.2 metre reserve accommodates protruding turbine utilities and condenser access junction.')
route('R05','service',4,['turbine.exit',[74,46.5,0],[74,36,0],[66,36,0],'electrical.entry'],'U-shaped power wing, leaving bus adapter and corner pockets.')
route('R06','freight',4.5,['electrical.exit','waste.entry'],'Separated shells; future receiving connector.')
route('R07','maintenance',4.5,[[0,-29,0],[6,-29,0],[6,-4,0],[-15,-4,0],[-15,28,0]],'Alternate north/south route; no doorway cut into any room.')
route('R08','service',4,['fuel.service',[-15,17.4,0]])
route('R09','clean',4.5,[[-41,28,0],[34,28,0]],'Clean/recovery header; controlled crossing at maintenance junction, no waste storage access required.')
route('R10','clean',4.5,['spawn.exit',[-28,28,0]])
route('R11','clean',4.5,['medical.entry',[-29,28,0]],'Two-person rescue/cart approach.')
route('R12','controlled',4,['compliance.entry',[-41,16,0],[-41,28,0]],'Future lockable compliance approach with a bend before the clean header.')
route('R13','clean',4,['fuel.clean',[6.6,28,0]])
route('R14','maintenance',4,[[34,28,0],[34,46.5,0]],'Independent rescue access to reactor/turbine junction.')
route('R15','service',4,[[-15,28,0],[-15,55,0],[-5,55,0],[-1.7,59.5,0],[-.5,61.2,0],'cooling.entry'],'Cooling recovery/portable battery route.')
route('R16','service',6,['reactor.cooling','cooling.entry'],'Offset follows the existing southeast reactor stub; remote door/loop still unbound.')
route('R17','service',4,[[34,28,0],[51,28,0],[51,31,0],[74,31,0],[74,36,0]],'Completes the maintenance loop through turbine and electrical approaches.')
route('R18','waste',4.5,['fuel.waste',[49,16,0],[49,3.2,0],'waste.personnel'],'Separate waste branch; personnel portal is a bottleneck, bulk loads use receiving/dispatch.')
route('R19','service',3.5,[[33,46.5,0],[33,44.9,0],[33,44.9,-6],'condenser.entry'],'Vertical line is a reserved stair/lift link, NOT a built stair or walkable ramp.')
route('R20','clean',4,['refinery.personnel',[6,-18.40666,0],[6,-4,0],[0,-4,0]],'Refinery personnel approach joins upstream connector; source doorway untouched.')
route('R21','maintenance',4,[[6,-4,0],[49,-4,0],[49,28,0]],'Emergency materials/recovery crossover closes the lower maintenance loop; does not bypass required fuel processing.')
reserves=[
 dict(id='V01_CONDENSER_ACCESS',kind='stair_and_freight_lift',center=[33,40,-2.75],size=[5.5,10,6.5],note='Future two-flight switchback stairs plus cart/lift solution; actual design and headroom pending.'),
 dict(id='U01_UTILITY_GALLERY',kind='utility_only',center=[49,32,5.0],size=[26,4,2.4],note='Separate steam/CW/power routing allowance; not an installed utility loop.'),
 dict(id='A01_EXTERNAL_ARRIVAL',kind='external_arrival',center=[-75.6,16,2.5],size=[20,12,5],note='Keep clear beyond dock gate; external approach unbuilt.'),
 dict(id='A02_WASTE_DISPATCH',kind='dispatch_apron',center=[66,-24,2.5],size=[12,12,5],note='Retain external dispatch turning/loading room.'),
]
data=dict(revision='A04',units='metres',scope='Spatial assembly of existing rooms; connecting structures explicitly unbuilt',placements={k:{'translation':v[0],'rotation_z_degrees':v[1],'scale':[1,1,1]} for k,v in placements.items()},ports=ports,routes=routes,reserved_volumes=reserves,travel_assumptions={'normal_walk_m_s':4.5,'loaded_cart_m_s':1.5,'note':'4.5 m/s is a disclosed layout assumption, not a verified engine controller. Loaded speed is inherited from fuel-corridor planning.'})
(ROOT/'production/LAYOUT.json').write_text(json.dumps(data,indent=2))
print('A04:12 rooms,21 reserved connections,4 reserved volumes; no connector construction.')
