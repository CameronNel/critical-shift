"""Cold-open extracted portable source and reject dependencies outside its root.

Blender --background --factory-startup --disable-autoexec --threads 1 --python-exit-code 1
  --python verify_delivery.py -- --root /path/to/extracted/source --report /path/to/report.json
Never saves any scene or library.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy

parser = argparse.ArgumentParser()
parser.add_argument('--root', required=True)
parser.add_argument('--report', required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
root = Path(args.root).resolve()
room = root / 'sections/facility-assembly/sources/medical-reanimation'
source = room / 'module_overhaul_R2.blend'
expected = json.loads((room / 'revamp-review/production/dependency-manifest.json').read_text())
before = hashlib.sha256(source.read_bytes()).hexdigest()
errors = []
if before != expected['source_sha256']:
    errors.append('Packaged source differs from dependency evidence')
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
scene = bpy.data.scenes.get('REANIMATION_EDIT_LOCAL')
if scene is None or scene.library:
    errors.append('Editable local room scene is missing or linked')
libraries = []
for lib in bpy.data.libraries:
    resolved = Path(bpy.path.abspath(lib.filepath)).resolve()
    inside = resolved.is_relative_to(root)
    exists = resolved.is_file()
    libraries.append({'path': str(resolved), 'inside_package': inside, 'exists': exists})
    if not inside or not exists:
        errors.append('Unresolved or external library: ' + str(resolved))
if len(libraries) != len(expected['linked_libraries']):
    errors.append('Linked-library count differs from validated source')
images = []
for im in bpy.data.images:
    if im.source != 'FILE':
        continue
    valid = min(im.size) > 0
    packed = bool(im.packed_file)
    external = Path(bpy.path.abspath(im.filepath, library=im.library)).resolve() if im.filepath else None
    images.append({'name': im.name, 'packed': packed, 'valid_loaded_pixels': valid})
    if not valid or (not packed and (external is None or not external.is_relative_to(root) or not external.is_file())):
        errors.append('Unavailable portable image: ' + im.name)
if hashlib.sha256(source.read_bytes()).hexdigest() != before:
    errors.append('Source was modified')
report = {'status': 'PASS' if not errors else 'FAIL', 'source_sha256': before,
          'extracted_root': str(root), 'blender': bpy.app.version_string,
          'source_saved': False, 'editable_objects': len(scene.objects) if scene else 0,
          'libraries': libraries, 'file_images': images, 'errors': errors}
Path(args.report).write_text(json.dumps(report, indent=2) + '\n')
print('PORTABLE_DELIVERY_VERIFY', report['status'], len(libraries), len(images), errors, flush=True)
if errors:
    raise SystemExit(1)
