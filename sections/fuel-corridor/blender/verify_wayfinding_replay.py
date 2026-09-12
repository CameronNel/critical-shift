"""CPU-only replay check against the live correction, without saving a scene."""
import bpy,json,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def labels():
    return {o.name:{'text':o.data.body,'size':o.data.size,'matrix':[v for row in o.matrix_world for v in row]} for o in bpy.context.scene.objects if o.type=='FONT'}
bpy.ops.wm.open_mainfile(filepath=str(root/'production/checkpoints/walkthrough/corrected.blend'))
expected=labels()
bpy.ops.wm.open_mainfile(filepath=str(root/'production/checkpoints/walkthrough/live-before.blend'))
runpy.run_path(str(root/'blender/wayfinding.py'))['apply_wayfinding']()
actual=labels();errors=[]
for name,ref in expected.items():
    row=actual.get(name)
    if row is None or row['text']!=ref['text'] or abs(row['size']-ref['size'])>1e-6 or max(abs(a-b) for a,b in zip(row['matrix'],ref['matrix']))>1e-5:errors.append(name)
report={'pass':not errors,'font_objects':len(expected),'errors':errors,'scope':'Replays exact text content, sizes and world transforms from preserved live state; no render or save'}
(root/'production/evidence/walkthrough/replay-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report));assert report['pass'],errors
