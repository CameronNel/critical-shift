"""Resolve active electrical links and display caches without modifying the map."""
import bpy,json,sys,os,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[6]
p=root/json.loads((root/'MAP.json').read_text())['authoring_scene']
bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False)
report={'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'objects':[],'collections':[], 'layers':[]}
for o in bpy.context.scene.objects:
    props={key:str(val) for key,val in o.items()}
    if 'electrical' in (o.name+' '+str(props)).lower():
        report['objects'].append({'name':o.name,'type':o.type,'render_hidden':o.hide_render,'viewport_hidden':o.hide_viewport,
          'library':o.library.filepath if o.library else None,'instance_collection':o.instance_collection.name if o.instance_collection else None,
          'instance_library':o.instance_collection.library.filepath if o.instance_collection and o.instance_collection.library else None,'properties':props})
for c in bpy.data.collections:
    if 'electrical' in c.name.lower():report['collections'].append({'name':c.name,'library':c.library.filepath if c.library else None,'objects':len(c.all_objects),'render_hidden':c.hide_render,'viewport_hidden':c.hide_viewport})
def layer(c):
    if 'electrical' in c.name.lower():report['layers'].append({'name':c.name,'exclude':c.exclude,'hide_viewport':c.hide_viewport})
    for child in c.children:layer(child)
layer(bpy.context.view_layer.layer_collection)
report['libraries']=[{'stored':l.filepath,'resolved':bpy.path.abspath(l.filepath),'exists':Path(bpy.path.abspath(l.filepath)).is_file()} for l in bpy.data.libraries]
(Path(__file__).resolve().parents[1]/'map-link-inspection.json').write_text(json.dumps(report,indent=2))
print('MAP_LINK_INSPECTED',[(o['name'],o['instance_library']) for o in report['objects'] if o['instance_collection']],flush=True)
sys.stdout.flush();sys.stderr.flush();os._exit(0)
