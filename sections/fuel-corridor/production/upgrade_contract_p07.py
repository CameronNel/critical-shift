"""Own-section envelope corrections from evaluated full01 evidence."""
import json
from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=r/'interface.json';d=json.loads(p.read_text(encoding='utf-8'))
assert d['revision']=='P06'
d['revision']='P07'
d['status']='P07 local frame and rescue-turn margins, 2026-09-11. External measured seams unchanged; full correction verification pending. Separate local mappings only; no global assembly or runtime passage verified. Existing reactor fuel doors remain closed.'
changes={'inlet':[-1.6,1.6,0,1.2],'reactor_adapter':[11.4,17.0,21,24],'bypass_turn':[-1.5,1.2,18,21]}
found=set()
for cell in d['floor_cells']:
    if cell['id'] in changes:cell['bounds']=changes[cell['id']];found.add(cell['id'])
assert found==set(changes),found
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
p=r/'architecture/CONNECTION_CONTRACTS.md';s=p.read_text(encoding='utf-8').replace('— P06 connection contracts','— P07 connection contracts').replace('Updated 10 September 2026','Updated 11 September 2026').replace('pending at P06 source stage','pending at P07 correction stage')
s+='\nP07 responds to evaluated full01 geometry. The inlet enclosure is3.20m gross (X−1.60..1.60) and reactor adapter5.60m gross (X11.40..17.00), reserving wall/frame depth outside the unchanged2.60/5.00m nominal port openings. The service turning bay extends toX−1.50 overY18.00..21.00, outside the unchanged bypass centerline, to clear the nominal2.20×.75m stretcher spin. External port centers/normals/mappings and route lengths remain unchanged. Correction validation is pending.\n'
p.write_text(s,encoding='utf-8')
p=r/'architecture/build_plan.py';s=p.read_text(encoding='utf-8').replace('P06','P07').replace('range(-5,18)','range(-5,19)').replace('xy(16.7,24)','xy(17.0,24)').replace('22.10 m overall floor envelope','22.40 m overall floor envelope').replace('world_dim_x(11.7,16.7,22.35,"5.00 clear")','world_dim_x(11.4,17.0,22.35,"5.60 enclosure")');p.write_text(s,encoding='utf-8')
print('P07 local envelopes authored; external contracts and route lengths unchanged')
