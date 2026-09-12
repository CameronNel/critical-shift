from pathlib import Path
import json
r=Path(__file__).resolve().parents[1];p=r/'interface.json';d=json.loads(p.read_text(encoding='utf-8'));ports=json.dumps(d['ports'],sort_keys=True)
d['revision']='P06';d['status']=d['status'].replace('P05 local head enclosures and gate pocket corrections','P06 clean-header circulation bay and local head/gate corrections')
for c in d['floor_cells']:
 if c['id']=='bypass_north':c['bounds'][2]=18.0
for q in d['route_centerlines']['service_bypass'][1:]:q[1]=19.2
d['implementation_decisions']['clean_header_circulation']='North service leg widens to3.00m gross, Y18.00..21.00, with centerlineY19.20. This preserves a2.00m dressed through-route beside the clean-port frame0.50m inboard. West bypass remains2.40m gross. No external seam or freight timing changes.'
assert ports==json.dumps(d['ports'],sort_keys=True);p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
p=r/'architecture/CONNECTION_CONTRACTS.md';s=p.read_text(encoding='utf-8').replace('— P05 connection contracts','— P06 connection contracts').replace('(0,19.8) → (14.2,19.8), length 24.00 m','(0,19.2) → (14.2,19.2), length 23.40 m').replace('pending at P05 source stage','pending at P06 source stage');s+='\nP06 widens only the northern service leg to3.00m gross (Y18.00..21.00) and shifts its route centerline toY19.20. This gives the inboard clean-header jambs a separate margin beside the2.00m dressed through-route. The west service bypass remains2.40m gross. All external port coordinates and the38.20m freight route remain unchanged. The bypass length becomes23.40m; evaluated clearance and stretcher motion remain required.\n';p.write_text(s,encoding='utf-8')
p=r/'architecture/build_plan.py';s=p.read_text(encoding='utf-8').replace('P05','P06').replace('world_dim_y(10.6,18.6,21,"2.40")','world_dim_y(10.6,18.0,21,"3.00")');p.write_text(s,encoding='utf-8')
print('P06 north service circulation reservation recorded; external ports unchanged')
