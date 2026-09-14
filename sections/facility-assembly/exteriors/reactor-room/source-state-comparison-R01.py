import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
r=[]
for p in [root/'exteriors/reactor-room/exterior-R01.blend',root/'sources/reactor-room/module.blend',root/'sources/reactor-room/accepted.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False);bpy.context.view_layer.update();row={'file':str(p),'frame':bpy.context.scene.frame_current,'objects':[]}
 for n in ['Reactor exterior Shell 1 field','Shell 1 field','BANK_A_MOVING','A moving flange','MF PLAYER WALKTHROUGH']:
  o=bpy.data.objects.get(n)
  if o:row['objects'].append({'name':n,'library':o.library.filepath if o.library else None,'location':list(o.location),'matrix':[list(v) for v in o.matrix_world],'data_name':o.data.name if o.data else None})
 r.append(row)
(root/'exteriors/reactor-room/source-state-comparison-R01.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
