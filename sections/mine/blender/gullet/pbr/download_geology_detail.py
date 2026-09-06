#!/usr/bin/env python3
"""Extend the selected material library with two source-verified CC0 geological sets."""
from pathlib import Path
import json
from download_materials import DEFAULT, polyhaven

if __name__ == '__main__':
    dest = DEFAULT
    manifest_path = dest/'download_manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for name, size in [('rock_face_03', 3.0), ('quarry_wall', 1.8)]:
        record = polyhaven(dest, name, size)
        manifest['assets'] = [a for a in manifest['assets'] if a['asset'] != name] + [record]
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    with (dest/'PROVENANCE.md').open('a', encoding='utf-8') as file:
        file.write('\n## Geological detail extension\n\n')
        for name in ['rock_face_03', 'quarry_wall']:
            file.write('Poly Haven: https://polyhaven.com/a/' + name + '\n\n')
        file.write('Both sets: CC0-1.0, https://polyhaven.com/license\n')
    print('Six CC0 material sets are ready.', flush=True)
