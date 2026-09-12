from pathlib import Path
import json
r=Path(__file__).resolve().parents[1];p=r/'interface.json';d=json.loads(p.read_text());original_ports=json.dumps(d['ports'],sort_keys=True)
d['revision']='P05'
d['status']='P05 local head enclosures and gate pocket corrections, 2026-09-10. External measured seams unchanged; full geometry verification pending. Separate local mappings only; no global assembly or runtime passage verified. Existing reactor fuel doors remain closed.'
for c in d['floor_cells']:
 if c['id']=='inlet':c['height']=3.9
 if c['id']=='reactor_adapter':c['height']=5.9
 if c['id']=='freight_gate_south_pocket':c['bounds'][2]=6.15
 if c['id']=='freight_gate_north_pocket':c['bounds'][3]=13.85
q=d['freight_gate_pockets'];q['south_bounds_xy']=[6.07,6.78,6.15,7.8];q['north_bounds_xy']=[6.07,6.78,12.2,13.85];q['status']='P05 enlarged to1.65m pocket length for actual interior lining/steelwork; full evaluated leaf travel verification required.'
d['implementation_decisions']['port_head_enclosures']='F01 inlet ceiling3.90m and reactor adapter5.90m accommodate3/5m nominal openings plus0.55m head hardware and ceiling steelwork. Frames0.50m inside their unchanged external thresholds, supported by dedicated structural foundation shoes. PLANT/CLEAN service doors use manual heads beneath3.00m ceilings.'
d['implementation_decisions']['service_air_feed']='Recessed inlet lowered toZ2.14m; continuous ceiling-fed branch remains above2.20m across the bypass, dropping beside its west edge into the recess. Full route and service continuity checks pending.'
assert original_ports==json.dumps(d['ports'],sort_keys=True)
p.write_text(json.dumps(d,indent=2)+'\n')
p=r/'blender/build.py';s=p.read_text();a=s.index("        root('Longitudinal_tray'");b=s.index("        root('Service_pipework'",a);v=s[a:b]
for old,new in [('3.762','4.102'),('3.78','4.12'),('3.73','4.07'),('3.69','4.03'),('3.704','4.044')]:v=v.replace(old,new)
s=s[:a]+v+s[b:];p.write_text(s)
print('P05 source and unchanged external ports recorded; no full build performed')
