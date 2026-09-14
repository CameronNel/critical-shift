import json
from pathlib import Path
R=Path('.');out=[]
def add(sid,key,c,n,w,h,box=None,kind='slide',group='',side=''):
 out.append(dict(sid=sid,id=key,center=c,normal=n,width=w,height=h,cut=box,kind=kind,group=group,side=side))
add('spawn-room','spawn_airlock',[0,9.34,0],[0,1,0],2.6,2.7,[[-1.31,9.18,.001],[1.31,9.50,2.72]])
for key,c,n,w,h,cut in [
 ('fuel_refinery',[0,.38,0],[0,-1,0],2.6,3,[[-1.32,.25,.001],[1.32,.48,3.01]]),
 ('fuel_reactor',[14.2,23.62,0],[0,1,0],5,5,[[11.67,23.48,.001],[16.73,23.72,5.01]]),
 ('fuel_plant',[-5.02,17.4,0],[-1,0,0],2,2.5,[[-5.14,16.36,.001],[-4.9,18.44,2.51]]),
 ('fuel_clean',[6.6,20.62,0],[0,1,0],2,2.5,[[5.56,20.50,.001],[7.64,20.74,2.51]]),
 ('fuel_waste',[16.02,16,0],[1,0,0],2.4,3,[[15.9,14.76,.001],[16.14,17.24,3.01]])]:add('fuel-corridor',key,c,n,w,h,cut,group='process_airlock' if key=='fuel_reactor' else '',side='fuel')
add('reactor-room','reactor_fuel',[0,14.40,0],[0,1,0],5,5,[[-2.51,14.24,-.001],[2.51,14.52,5.01]],group='process_airlock',side='reactor')
add('reactor-room','reactor_main',[-14.40,0,0],[-1,0,0],6,5.5,[[-14.52,-3.01,-.001],[-14.24,3.01,5.51]])
add('compliance-dock','compliance_entry',[0,-2,0],[0,-1,0],1.6,2.2,[[-.82,-2.06,-.001],[.82,-1.94,2.22]])
add('compliance-dock','compliance_arrival',[0,15.8,0],[0,1,0],4.6,3.5,[[-2.32,15.66,.001],[2.32,15.93,3.51]],kind='roller')
# Already-open source portals retain their leaves; functional closures use a separate recessed roller.
for sid,key,c,n,w,h in [
 ('turbine-room','turbine_entry',[0,-.08,0],[0,-1,0],2.4,2.7),('turbine-room','turbine_exit',[0,25.2,0],[0,1,0],2.4,2.7),
 ('electrical-room','electrical_entry',[0,-.20,0],[0,-1,0],2.4,2.7),('electrical-room','electrical_exit',[0,16.8,0],[0,1,0],2.4,2.7),
 ('cooling-plant','cooling_entry',[0,.22,0],[0,-1,0],5,5.1),
 ('medical-reanimation','medical_entry',[0,-.35,0],[0,-1,0],2.0,2.45),
 ('condenser-bay','condenser_entry',[0,-.12,0],[0,-1,0],2,2.4),
 ('waste-storage','waste_receiving',[0,-.1,0],[0,-1,0],2.8,3.2),('waste-storage','waste_dispatch',[0,18.1,0],[0,1,0],2.2,2.8)]:add(sid,key,c,n,w,h,kind='roller')
# Export exact source-name exclusions, scoped to small door volumes, not room structure.
for d in out:
 d['exclude_names']=[]
 if d['cut']:
  lo,hi=d['cut'];records=json.loads((R/'sources'/d['sid']/'survey.json').read_text())['records']
  for o in records:
   b=o.get('bounds')
   if b and o['type'] in ['MESH','CURVE','FONT','SURFACE'] and all(b[0][i]>=lo[i]-.015 and b[1][i]<=hi[i]+.015 for i in range(3)):
    d['exclude_names'].append(o['name'])
  assert d['exclude_names'],d['id']
(R/'connections/access/DOOR_BINDINGS.json').write_text(json.dumps(out,indent=2))
print([(d['id'],len(d['exclude_names'])) for d in out])
