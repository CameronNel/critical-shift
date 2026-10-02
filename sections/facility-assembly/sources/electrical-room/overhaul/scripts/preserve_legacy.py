"""Preserve original map-requested material IDs without editing visible geometry."""
import bpy, argparse, hashlib, json, os, sys
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--baseline',required=True)
p.add_argument('--requests',required=True)
p.add_argument('--output',required=True)
p.add_argument('--receipt',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath).resolve(); baseline=Path(a.baseline).resolve()
output=Path(a.output).resolve()
assert output!=source and output!=baseline
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
before=sha(source);baseline_before=sha(baseline)
requested=json.loads(Path(a.requests).read_text())['canonical_map_electrical_id_requests']
assert all(not names for kind,names in requested.items() if kind!='materials')
missing=[name for name in requested['materials'] if name not in bpy.data.materials]
visible_before={o.name:tuple(slot.material.name if slot.material else None for slot in o.material_slots)
                for o in bpy.context.scene.objects if hasattr(o,'material_slots')}
with bpy.data.libraries.load(str(baseline),link=False) as (src,dst):
    assert set(missing).issubset(src.materials)
    # Blender mutates the assigned list from names to datablocks on context exit.
    # Keep the original string list for exact-name assertions and the receipt.
    dst.materials=list(missing)
for material in dst.materials:
    assert material is not None and material.name in missing
    material.use_fake_user=True
for name in requested['materials']:
    bpy.data.materials[name].use_fake_user=True
visible_after={o.name:tuple(slot.material.name if slot.material else None for slot in o.material_slots)
               for o in bpy.context.scene.objects if hasattr(o,'material_slots')}
assert visible_before==visible_after
output.parent.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
assert sha(source)==before and sha(baseline)==baseline_before
report={'input_sha256':before,'baseline_sha256':baseline_before,'output_sha256':sha(output),
        'restored_original_material_ids':missing,'all_requested_material_ids_retained':requested['materials'],
        'visible_material_assignments_unchanged':True,
        'scope':'Original unused material definitions retained for current map cache compatibility. No scene geometry, light, camera or visible material assignment changed.'}
Path(a.receipt).write_text(json.dumps(report,indent=2)+'\n')
print('LEGACY_MATERIAL_IDS_PRESERVED',len(missing),flush=True)
sys.stdout.flush();sys.stderr.flush();os._exit(0)
