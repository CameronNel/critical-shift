"""Declare original freight sliding-door pockets without changing any external port."""
import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'interface.json'
d=json.loads(p.read_text())
for key,value in list(d.items()):
    if isinstance(value,str) and value=='P03':d[key]='P04'
existing={c['id'] for c in d['floor_cells']}
for name,bounds in [('freight_gate_south_pocket',[6.07,6.78,6.30,7.8]),('freight_gate_north_pocket',[6.07,6.78,12.2,13.70])]:
    if name not in existing:d['floor_cells'].append({'id':name,'bounds':bounds,'height':4.4})
d['freight_gate_pockets']={'purpose':'Enclosed architectural cassettes for paired sliding freight leaves; outside walkable freight envelope','south_bounds_xy':[6.07,6.78,6.30,7.8],'north_bounds_xy':[6.07,6.78,12.2,13.70],'nominal_each_m':[.71,1.50,4.4],'external_port_changes':False,'movement_state':'Authored open pose; engine controller and moving sweep verification pending'}
p.write_text(json.dumps(d,indent=2)+'\n')
