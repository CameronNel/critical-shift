import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A11_map_finish.blend'),load_ui=False)
inst=bpy.data.objects['spawn-room'];q=Vector((-28,12.3,.6));res=[]
for o in inst.instance_collection.all_objects:
 if o.type!='MESH':continue
 m=inst.matrix_basis@o.matrix_basis;p=[m@Vector(v) for v in o.bound_box]
 if all(min(v[i] for v in p)<hi and max(v[i] for v in p)>lo for i,(lo,hi) in enumerate([(-29.3,-26.7),(12.1,12.6),(.01,2.7)])):res.append({'name':o.name,'bounds':[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]})
print('SPAWN_FINDINGS',json.dumps(res),flush=True)
