import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'exteriors/reactor-room';states=[]
for p in [out/'exterior-R03.blend',root/'sources/reactor-room/accepted.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False);bpy.context.scene.frame_set(1);bpy.context.view_layer.update();col=bpy.data.collections.get('MODULE_reactor-room');obs=col.all_objects if col else bpy.data.objects
 states.append({o.name:{'matrix':[list(r) for r in o.matrix_world],'vertices':[list(v.co) for v in o.data.vertices] if o.type=='MESH' else None,'polygons':[list(f.vertices) for f in o.data.polygons] if o.type=='MESH' else None,'type':o.type} for o in obs})
r=[]
for n,a in states[0].items():
 b=states[1].get(n)
 if b and a!=b:r.append({'name':n,'type':a['type'],'matrix_max_delta':max(abs(a['matrix'][i][j]-b['matrix'][i][j]) for i in range(4) for j in range(4)),'mesh_changed':a['vertices']!=b['vertices'] or a['polygons']!=b['polygons']})
(out/'same-frame-source-R03.json').write_text(json.dumps(r,indent=2));print('DIFFS',len(r),'mesh',sum(x['mesh_changed'] for x in r),'max_delta',max([x['matrix_max_delta'] for x in r],default=0));print(r[:3])
