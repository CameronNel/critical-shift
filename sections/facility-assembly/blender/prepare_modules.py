"""Survey immutable inputs and create portable collection wrappers; no source writes."""
import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'production/SOURCES.json').read_text())
for row in rows:
    sid=row['id']; dest=ROOT/'sources'/sid
    if (dest/'module.blend').exists() and (dest/'survey.json').exists() and (sid!='reactor-room' or json.loads((dest/'survey.json').read_text()).get('presentation_exclusions')):continue
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/row['frozen']),load_ui=False)
    scene=bpy.context.scene
    exclusions=[]
    if sid=='reactor-room':
        sky=bpy.data.objects.get('RF outdoor sky proxy')
        if sky:
            sky.hide_render=True;sky.hide_viewport=True;exclusions.append(sky.name)
    deps=bpy.context.evaluated_depsgraph_get()
    records=[];missing=[]
    for ob in scene.objects:
        rec={'name':ob.name,'type':ob.type,'location':list(ob.matrix_world.translation),'hide_render':ob.hide_render,'visible':ob.visible_get(),'collections':[c.name for c in ob.users_collection]}
        if ob.type in {'MESH','CURVE','FONT','SURFACE'}:
            ev=ob.evaluated_get(deps);corners=[ev.matrix_world@Vector(v) for v in ev.bound_box]
            rec['bounds']=[[min(v[i] for v in corners) for i in range(3)],[max(v[i] for v in corners) for i in range(3)]]
        if ob.type=='EMPTY' or any(s in ob.name.lower() for s in ['portal','door','threshold','interface','floor','entry','exit','adit']):
            rec['properties']={k:str(ob[k])[:250] for k in ob.keys() if k!='_RNA_UI'}
        records.append(rec)
    # Resolve original relative dependencies before changing the copy's location.
    for img in bpy.data.images:
        if img.source=='FILE' and not img.packed_file:
            path=Path(bpy.path.abspath(img.filepath))
            if not path.exists() and img.filepath.startswith('//'):
                path=(Path(row['original_parent'])/img.filepath[2:]).resolve()
            if path.exists():img.filepath=str(path)
            else:missing.append({'image':img.name,'path':str(path),'users':img.users})
    missing_used=[x for x in missing if x['users']>0]
    if missing_used:raise RuntimeError((sid,missing_used))
    bpy.ops.file.pack_all()
    wrapper=bpy.data.collections.new('MODULE_'+sid)
    for col in list(scene.collection.children):wrapper.children.link(col)
    for ob in list(scene.collection.objects):wrapper.objects.link(ob)
    scene.collection.children.link(wrapper)
    excluded=[]
    def layers(layer):
        if layer.exclude:excluded.append(layer.name)
        for child in layer.children:layers(child)
    layers(bpy.context.view_layer.layer_collection)
    bounds=[r['bounds'] for r in records if 'bounds' in r and not r['hide_render']]
    survey=dict(presentation_exclusions=exclusions,id=sid,scene=scene.name,units=scene.unit_settings.scale_length,objects=len(records),export_collection=wrapper.name,excluded_layers=excluded,missing_unused_images=missing,all_visible_bounds=[[min(b[0][i] for b in bounds) for i in range(3)],[max(b[1][i] for b in bounds) for i in range(3)]],records=records)
    (dest/'survey.json').write_text(json.dumps(survey,indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(dest/'module.blend'),compress=True)
    print('MODULE_READY',sid,len(records),survey['all_visible_bounds'],'excluded',excluded,flush=True)
print('ALL_MODULES_PREPARED',flush=True)
