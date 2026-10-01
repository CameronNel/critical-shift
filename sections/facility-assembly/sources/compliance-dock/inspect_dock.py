"""Read-only input inventory; run in a fresh Blender process. Never saves scenes."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy

p = argparse.ArgumentParser()
p.add_argument('--input', required=True)
p.add_argument('--out', required=True)
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
source = Path(a.input).resolve()
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
scene = bpy.context.scene
deps = bpy.context.evaluated_depsgraph_get()
objects = []
triangles = 0
draw_submeshes = 0
for o in scene.objects:
    item = dict(name=o.name, type=o.type, parent=o.parent.name if o.parent else None,
                matrix=[list(v) for v in o.matrix_world], dimensions=list(o.dimensions),
                location=list(o.location), collections=[c.name for c in o.users_collection],
                hide_render=o.hide_render, materials=[s.material.name if s.material else None for s in o.material_slots],
                support_class=o.get('support_class'), support_target=o.get('support_target'),
                circulation_solid=bool(o.get('circulation_solid', False)),
                properties={k:str(v) for k,v in o.items()})
    if o.type in {'MESH','CURVE','FONT','SURFACE','META'}:
        ev=o.evaluated_get(deps)
        me=ev.to_mesh()
        if me:
            me.calc_loop_triangles()
            item['triangles']=len(me.loop_triangles)
            item['material_submeshes']=len({f.material_index for f in me.polygons})
            triangles += item['triangles']
            draw_submeshes += item['material_submeshes']
            coords=[ev.matrix_world @ v.co for v in me.vertices]
            if coords:
                item['bounds']={'min':[min(v[k] for v in coords) for k in range(3)],
                                'max':[max(v[k] for v in coords) for k in range(3)]}
            ev.to_mesh_clear()
    if o.type=='CAMERA':
        item['lens']=o.data.lens
    if o.type=='LIGHT':
        item['light']={'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color)}
    objects.append(item)
materials=[]
for m in bpy.data.materials:
    rec={'name':m.name,'diffuse_color':list(m.diffuse_color)}
    if m.use_nodes:
        bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if bs:
            for k in ['Base Color','Roughness','Metallic','Emission Color','Emission Strength']:
                if k in bs.inputs:
                    v=bs.inputs[k].default_value
                    rec[k]=list(v) if hasattr(v,'__len__') else float(v)
    materials.append(rec)
result={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'blender':bpy.app.version_string,'scene':scene.name,'scenes':[s.name for s in bpy.data.scenes],
        'objects':objects,'materials':materials,'evaluated_triangles':triangles,
        'authoring_material_submeshes':draw_submeshes,'runtime_draw_calls_measured':False,
        'collections':[c.name for c in bpy.data.collections],'text_blocks':[t.name for t in bpy.data.texts],
        'libraries':[{'path':l.filepath,'missing':l.is_missing} for l in bpy.data.libraries],
        'renderer':scene.render.engine,'view_transform':scene.view_settings.view_transform,
        'look':scene.view_settings.look,'exposure':scene.view_settings.exposure,
        'source_saved':False}
out=Path(a.out).resolve();out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2)+'\n')
print('INPUT_INVENTORY',scene.name,len(objects),triangles,draw_submeshes,len(materials),flush=True)
print('CAMERAS',[o.name for o in scene.objects if o.type=='CAMERA'],flush=True)
