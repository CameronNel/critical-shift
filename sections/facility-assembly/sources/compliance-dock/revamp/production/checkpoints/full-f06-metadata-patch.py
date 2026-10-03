"""Bounded root-authored repair of moving-leaf support claims, with no mesh edits.

The full construction recipe has the same correction. This patch avoids a
geometry rebuild and records the exact saved f05 input and properties changed.
"""
import bpy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
P=ROOT/'revamp/production'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
native=ROOT/'module_overhaul_R1.blend'
state=json.loads((P/'build-state.json').read_text())
assert state['revision']=='f05' and sha(native)==state['source_sha256']
prior=state['source_sha256']
recipes={n:sha(ROOT/n) for n in state['recipe_sha256']}
patch_sha=sha(Path(__file__))
bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False)
S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S
registered=set(json.loads(S['contact_assemblies']))
before={o.name:tuple(v for row in o.matrix_world for v in row) for o in S.objects}
changes=[]
for error in json.loads((P/'validation-full-f05.json').read_text())['errors']:
    assert error['code']=='invalid_assembly_ancestry'
    o=S.objects[error['object']];assert o.name.startswith('CD | Joined ')
    parent=o.parent
    while parent and parent.name not in registered:parent=parent.parent
    assert parent is not None
    changes.append(dict(object=o.name,parent=o.parent.name,old_claim=o['assembly'],new_claim=parent.name))
    o['assembly']=parent.name
assert len(changes)==15
assert before=={o.name:tuple(v for row in o.matrix_world for v in row) for o in S.objects}
S['revision']='f06'
S['recipe_sha256']=json.dumps(recipes,sort_keys=True)
lineage=dict(input_sha256=prior,patch_script='repair_support_metadata.py',patch_script_sha256=patch_sha,changed_properties=changes,geometry_materials_uvs_and_poses_unchanged=True)
S['incremental_repair_provenance']=json.dumps(lineage,sort_keys=True)
assert all(sha(ROOT/n)==digest for n,digest in recipes.items()) and sha(Path(__file__))==patch_sha
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
state.update(revision='f06',source_sha256=sha(native),recipe_sha256=recipes,incremental_repair=lineage)
(P/'build-state.json').write_text(json.dumps(state,indent=2)+'\n')
print('METADATA_REPAIRED',len(changes),state['source_sha256'],flush=True)
