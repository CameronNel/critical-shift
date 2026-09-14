import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];results=[]
def visibility(col):
 paths={};flags=[]
 def walk(c,render=True,view=True,path=''):
  p=path+'/'+c.name;render=render and not c.hide_render;view=view and not c.hide_viewport
  if c.hide_render or c.hide_viewport:flags.append({'path':p,'hide_render':c.hide_render,'hide_viewport':c.hide_viewport})
  for o in c.objects:paths.setdefault(o.name,[]).append({'path':p,'render':render and not o.hide_render,'viewport':view and not o.hide_viewport})
  for ch in c.children:walk(ch,render,view,p)
 walk(col);return paths,flags
for sid,rev in [('spawn-room','R05'),('turbine-room','R03'),('refinery','R01')]:
 bpy.ops.wm.open_mainfile(filepath=str(root/'exteriors'/sid/f'exterior-{rev}.blend'),load_ui=False)
 with bpy.data.libraries.load(str(root/'sources'/sid/'module.blend'),link=True) as (rs,rd):rd.collections=['MODULE_'+sid]
 src=rd.collections[0];inst=bpy.data.objects['READ_ONLY_ORIGINAL_'+sid];actual=inst.instance_collection
 orig,flags=visibility(src);dest,_=visibility(actual);changed=[]
 for n,ps in orig.items():
  ds=dest.get(n)
  if not ds:continue
  a=any(p['render'] for p in ps);b=any(p['render'] for p in ds);av=any(p['viewport'] for p in ps);bv=any(p['viewport'] for p in ds)
  if a!=b or av!=bv:changed.append({'name':n,'type':bpy.data.objects[n].type,'source_render':a,'wrapper_render':b,'source_viewport':av,'wrapper_viewport':bv,'source_paths':ps})
 r={'section':sid,'revision':rev,'wrapper':actual.name,'source_flags':flags,'visibility_changes':changed,'scope':'Collection/object hide_render and hide_viewport inherited along all membership paths; no per-view-layer exclusions, ray visibility, or render pixels. Corrected local light copies absent under original names require separate binding inspection.'};results.append(r)
 (root/'exteriors'/sid/f'collection-visibility-{rev}.json').write_text(json.dumps(r,indent=2));print(sid,actual.name,'changes',len(changed),'render_reveals',sum(not x['source_render'] and x['wrapper_render'] for x in changed),'flags',flags,flush=True)

