import bpy, importlib.util, json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
spec=importlib.util.spec_from_file_location('dock_validator',str(ROOT/'validate_dock.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
bpy.context.window.scene=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];S=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
names=['CD | D1 ID enamel','D1 door leaf','CD | D1 die-pressed leaf.001']
shapes={n:v.Shape(S.objects[n],dg) for n in names}
rows=[]
for x,z in [(-5.4,1.90),(-5.4,1.94),(-5.3,1.90)]:
    hits={n:shapes[n].ray(Vector((x,3.45,z)),Vector((0,1,0)),.3) for n in names}
    hit={n:{'point':list(h['point']),'normal':list(h['normal']),'triangle':h['face']} if h else None for n,h in hits.items()}
    back=shapes[names[0]].ray(Vector((x,3.65,z)),Vector((0,-1,0)),.3)
    supports=[h for n,h in hits.items() if n!=names[0] and h]
    rows.append({'sample':[x,z],'enamel_back':list(back['point']) if back else None,'hits':hit,'nearest_actual_support_gap_m':min(h['point'].y-back['point'].y for h in supports) if back and supports else None})
(OUT/'id-bearing.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
