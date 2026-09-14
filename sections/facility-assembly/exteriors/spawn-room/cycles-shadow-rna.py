import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
for sid,rev in [('spawn-room','R04'),('turbine-room','R01')]:
 out=root/'exteriors'/sid
 bpy.ops.wm.open_mainfile(filepath=str(out/f'exterior-{rev}.blend'),load_ui=False)
 rows=[]
 for ob in bpy.data.objects:
  if ob.type!='LIGHT':continue
  d=ob.data;c=getattr(d,'cycles',None)
  props={}
  if c:
   for p in c.bl_rna.properties:
    if 'shadow' in p.identifier:
     props[p.identifier]={'value':getattr(c,p.identifier),'description':p.description}
   try:props['cast_shadow_direct']={'value':c.cast_shadow}
   except Exception as e:props['cast_shadow_direct']={'error':str(e)}
  rows.append({'object':ob.name,'library':str(ob.library.filepath) if ob.library else None,'data_library':str(d.library.filepath) if d.library else None,'use_shadow':d.use_shadow,'use_shadow_description':d.bl_rna.properties['use_shadow'].description,'cycles_shadow':props,'cycles_keys':list(c.keys()) if c else []})
 meshes=[{'name':o.name,'visible_shadow':o.visible_shadow,'is_holdout':o.is_holdout,'hide_render':o.hide_render} for o in bpy.data.objects if o.type=='MESH' and (not o.visible_shadow or o.is_holdout or any(t in o.name.lower() for t in ['membrane','roof','ceiling']))]
 r={'section':sid,'revision':rev,'engine':bpy.context.scene.render.engine,'lights':rows,'relevant_mesh_visibility':meshes}
 (out/f'cycles-shadow-rna-{rev}.json').write_text(json.dumps(r,indent=2))
 print(json.dumps({'section':sid,'lights':rows},indent=2))
