"""Cold-open verification for the isolated revamp baseline."""
import hashlib
import json
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parent
ASSEMBLY = ROOT.parents[1]
baseline = json.loads((ROOT / 'revamp-review/baseline.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'module_overhaul_R1.blend'), load_ui=False)
room = bpy.data.scenes['REANIMATION_EDIT_LOCAL']
assert room.library is None
assert len(room.objects) == len(baseline['objects'])
for rec in baseline['objects']:
    obj = room.objects[rec['name']]
    assert obj.library is None, rec['name']
    assert max(abs(obj.matrix_world[i][j] - rec['matrix_world'][i][j])
               for i in range(4) for j in range(4)) < 0.000001, rec['name']
    assert max(abs(obj.dimensions[i] - rec['dimensions'][i]) for i in range(3)) < 0.000001, rec['name']
missing = [lib.filepath for lib in bpy.data.libraries if not Path(bpy.path.abspath(lib.filepath)).exists()]
assert not missing, missing
map_scene = [s for s in bpy.data.scenes if s.library and Path(bpy.path.abspath(s.library.filepath)).name == 'facility_environment.blend']
assert map_scene, 'No linked current map scene'
assert bpy.data.collections.get('MODULE_medical-reanimation').library is None
for path, expected in baseline['protected_sha256'].items():
    assert hashlib.sha256((ASSEMBLY / path).read_bytes()).hexdigest() == expected, path
result = {'cold_open': 'PASS', 'local_objects_unchanged': len(room.objects),
          'missing_libraries': missing, 'linked_current_map': True,
          'protected_files_unchanged': True,
          'art_revamp': 'Not started; this is the isolated baseline workspace.'}
(ROOT / 'revamp-review/verification.json').write_text(json.dumps(result, indent=2))
print('REVAMP_VERIFIED', json.dumps(result), flush=True)
