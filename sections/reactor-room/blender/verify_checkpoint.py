"""Read-only saved-scene/source/dependency integrity check; never saves the blend."""
import hashlib
import json
from pathlib import Path

import bpy

section = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
revision = scene['art_revision']
source = section / 'production' / 'revisions' / revision / 'build_scene.py'
digest = hashlib.sha256(source.read_bytes()).hexdigest()
active_digest = hashlib.sha256((section / 'blender' / 'build_scene.py').read_bytes()).hexdigest()
images = [dict(name=i.name, source=i.source, packed=bool(i.packed_file),
               width=i.size[0], height=i.size[1])
          for i in bpy.data.images if i.name not in ('Render Result', 'Viewer Node')]
checks = {
    'immutable_source_matches_saved_scene': digest == scene['source_sha256'],
    'active_source_matches_saved_scene': active_digest == digest,
    'surface_images_packed': all(i['packed'] and i['width'] > 0 for i in images),
    'ten_perspective_cameras': sum(o.type == 'CAMERA' and o.name != 'PLAN_DIAGNOSTIC' for o in bpy.data.objects) == 10,
    'no_linked_libraries': not bpy.data.libraries,
    'metric_scale': scene.unit_settings.scale_length == 1 and scene.unit_settings.system == 'METRIC',
}
report = dict(revision=revision, source_sha256=digest, blend_file=bpy.data.filepath,
              checks=checks, images=images, passed=all(checks.values()),
              limitation='Integrity check only; not visual acceptance or ten-image reproduction.')
output = section / 'production' / 'revisions' / revision / 'checkpoint-integrity.json'
output.write_text(json.dumps(report, indent=2), encoding='utf-8')
print('CHECKPOINT_INTEGRITY', json.dumps(report), flush=True)
if not report['passed']:
    raise RuntimeError('Saved checkpoint integrity failed')
