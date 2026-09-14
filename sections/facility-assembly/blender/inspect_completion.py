import bpy,json,os,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'connections/completion';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A11_map_finish.blend'),load_ui=False)
bpy.context.view_layer.update()
report={}
for name in ['Whole map continuous concrete floor','WALK_PROXY_reactor-room','WALK_PROXY_mine','WALK_PROXY_turbine-room','WALK_PROXY_condenser-bay']:
 o=bpy.data.objects[name];p=[o.matrix_world@Vector(v) for v in o.bound_box];report[name]={'bounds':[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)],'verts':len(o.data.vertices),'faces':len(o.data.polygons)}
report['access']=[{'name':o.name,'pos':list(o.location),'size':list(o.dimensions)} for o in bpy.data.collections['11_ACCESS_ARCHITECTURE'].objects if any(k in o.name.lower() for k in ['wall','floor','landing'])]
report['exterior_collections']=[c.name for c in bpy.data.collections if any(k in c.name.lower() for k in ['reactor','mine','turbine','condenser'])]
(O/'INSPECTION.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
