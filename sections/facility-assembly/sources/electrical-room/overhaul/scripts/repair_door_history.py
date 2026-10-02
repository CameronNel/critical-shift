"""Apply the reproducible door-only correction to a reviewed checkpoint."""
import argparse, hashlib, json, os, sys
from pathlib import Path
import bpy
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit as k
from door_history import apply

p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
p.add_argument('--receipt', required=True)
a = p.parse_args(sys.argv[sys.argv.index('--')+1:])
source = Path(bpy.data.filepath).resolve(); out = Path(a.output).resolve()
assert out != source
source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
assert not bpy.context.scene.get('electrical_door_history_revision')
def signature(o):
    rec={'matrix':sum((list(row) for row in o.matrix_world),[]),'type':o.type,
         'hidden':[o.hide_render,o.hide_viewport],
         'materials':[slot.material.name if slot.material else None for slot in o.material_slots]}
    if o.type=='MESH':
        rec['vertices']=[list(v.co) for v in o.data.vertices]
        rec['polygons']=[(list(p.vertices),p.material_index,p.use_smooth) for p in o.data.polygons]
    elif o.type=='FONT':rec['body']=o.data.body
    elif o.type=='LIGHT':rec['light']=[o.data.energy,list(o.data.color)]
    elif o.type=='CAMERA':rec['lens']=o.data.lens
    return hashlib.sha256(json.dumps(rec,sort_keys=True).encode()).hexdigest()
before={o.name:signature(o) for o in bpy.context.scene.objects}
m = {name:bpy.data.materials[k.PREFIX+name] for name in ['oxide', 'steel', 'zinc']}
apply(k, m)
bpy.context.view_layer.update()
retired=json.loads(bpy.context.scene['electrical_retired_door_wear'])
unchanged=[name for name in before if name not in retired]
assert all(bpy.data.objects.get(name) and signature(bpy.data.objects[name])==before[name] for name in unchanged)
out.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(out), compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_sha
Path(a.receipt).resolve().write_text(json.dumps({
    'input_sha256':source_sha, 'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
    'scope':'Door-only cosmetic wear replacement. All other original geometry/interfaces remain subject to unchanged baseline checks.',
    'retired_original_decorative_wear':retired,
    'unchanged_original_object_signatures':len(unchanged),
    'all_other_matrices_geometry_material_assignments_visibility_lights_unchanged':True,
    'distinct_leaf_histories':4, 'new_supported_contact_assemblies':8,
    'source_bytes_unchanged':True
}, indent=2)+'\n')
print('DOOR_HISTORY_SAVED', out, flush=True)
sys.stdout.flush(); sys.stderr.flush(); os._exit(0)
