"""Verify U04 actual saved exhaust opening with evaluated object ray casts."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
targets=['Structural floor','TRAIN foundation','TRAIN grout bed','LP exhaust pit flange','LP exhaust downhood']
samples=[]
for dx in [-1.24,-.62,0,.62,1.24]:
    for dy in [-.74,0,.74]:
        p=Vector((4.6+dx,11.45+dy,1.6));hits=[]
        for name in targets:
            o=bpy.data.objects[name];ev=o.evaluated_get(dg);inv=o.matrix_world.inverted()
            hit=ev.ray_cast(inv@p,inv.to_3x3()@Vector((0,0,-1)),distance=2.2)[0]
            if hit:hits.append(name)
        samples.append({'xy':[p.x,p.y],'blocked_by':hits})
o=bpy.data.objects['Structural floor'];ev=o.evaluated_get(dg);inv=o.matrix_world.inverted()
positive_control=bool(ev.ray_cast(inv@Vector((3.0,11.45,1)),Vector((0,0,-1)),distance=2)[0])
passed=positive_control and all(not p['blocked_by'] for p in samples)
r={'revision':s['source_revision'],'status':'PASS' if passed else 'FAIL','opening_m':[2.5,1.5],'centre':[4.6,11.45,0],'method':'15 evaluated downward rays inside nominal aperture through five target objects; adjacent solid floor positive control','samples':samples,'adjacent_floor_positive_control':positive_control,'limits':'Connection opening only; no condenser or flow simulation'}
out=Path(sys.argv[sys.argv.index('--')+1]);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r))
if not passed:raise SystemExit(2)
