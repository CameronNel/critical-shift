"""Read-only cold-open inventory. Never saves, packs, unpacks, or renders scenes."""
import bpy
import hashlib
import json
import os
from pathlib import Path
import sys

args = sys.argv[sys.argv.index('--') + 1:]
scene_path, output_path = args
root = Path.cwd().resolve()
bpy.ops.wm.open_mainfile(filepath=str((root / scene_path).resolve()), load_ui=False, use_scripts=False)

def normalized(value):
    return os.path.normpath(str(value).replace('\\', '/'))

def absolute(value, library=None):
    return normalized(bpy.path.abspath(value, library=library))

def sha_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

libraries = []
for library in bpy.data.libraries:
    path = absolute(library.filepath)
    parent = getattr(library, 'parent', None)
    if parent and library.filepath.startswith('//'):
        path = absolute(library.filepath, parent)
    exists = Path(path).is_file()
    pointer = exists and Path(path).open('rb').read(80).startswith(b'version https://git-lfs')
    libraries.append({'path': path, 'missing': bool(getattr(library, 'is_missing', False)) or not exists or pointer, 'sha256': sha_file(path) if exists and not pointer else None})

images = []
for image in bpy.data.images:
    if image.source in {'VIEWER', 'GENERATED'} and not image.filepath:
        continue
    packed = []
    for item in image.packed_files:
        payload = item.packed_file
        packed.append({'path': item.filepath, 'bytes': payload.size, 'sha256': hashlib.sha256(payload.data).hexdigest()})
    if image.packed_file and not packed:
        payload = image.packed_file
        packed.append({'path': image.filepath, 'bytes': payload.size, 'sha256': hashlib.sha256(payload.data).hexdigest()})
    resolved = absolute(image.filepath, image.library) if image.filepath else ''
    images.append({'name': image.name_full, 'path': image.filepath, 'absolute': resolved, 'source': image.source, 'users': image.users, 'packed': packed, 'external_exists': bool(resolved and Path(resolved).is_file())})

# Blender path traversal also covers non-image datablocks and sequencer media.
paths = sorted(set(normalized(p) for p in bpy.utils.blend_paths(absolute=True, packed=True, local=False)))
objects = []
for obj in bpy.data.objects:
    data = obj.data
    objects.append({'name': obj.name_full, 'type': obj.type, 'matrix': [round(v, 7) for row in obj.matrix_world for v in row], 'data': data.name_full if data else None, 'vertices': len(data.vertices) if obj.type == 'MESH' else None, 'polygons': len(data.polygons) if obj.type == 'MESH' else None, 'materials': [slot.material.name_full if slot.material else None for slot in obj.material_slots]})
objects.sort(key=lambda item: (item['name'], item['type']))
report = {'scene': scene_path, 'blender': bpy.app.version_string, 'scene_sha256': sha_file(root / scene_path), 'object_count': len(objects), 'geometry_digest': hashlib.sha256(json.dumps(objects, sort_keys=True).encode()).hexdigest(), 'libraries': sorted(libraries, key=lambda item: item['path']), 'images': sorted(images, key=lambda item: (item['name'], item['path'])), 'all_paths': paths}
Path(output_path).write_text(json.dumps(report, indent=2), encoding='utf-8')
print('SCENE_AUDIT', json.dumps({'scene': scene_path, 'objects': len(objects), 'libraries': len(libraries), 'missing_libraries': sum(x['missing'] for x in libraries), 'image_datablocks': len(images), 'packed_image_payloads': sum(len(x['packed']) for x in images)}), flush=True)
if any(item['missing'] for item in libraries):
    raise RuntimeError('Incomplete library graph: refuse to delete any image')
