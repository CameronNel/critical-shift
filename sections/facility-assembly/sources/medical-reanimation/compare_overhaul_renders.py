"""Compare immutable hot/cold room evidence; never alters either PNG set.

System Python (Pillow, NumPy): compare_overhaul_renders.py --hot cycle-5 --cold cycle-6
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
PRODUCTION = ROOT / 'revamp-review/production'
parser = argparse.ArgumentParser()
parser.add_argument('--hot', required=True)
parser.add_argument('--cold', required=True)
parser.add_argument('--art-regression',action='store_true',help='Compare prior/current art after metadata or checker cleanup; does not certify cold stability')
parser.add_argument('--renderer-change-note',help='Explicitly document a metadata-only renderer change; source, render settings, cameras and RGB still must match')
args = parser.parse_args()
hot_dir = PRODUCTION / 'renders' / args.hot
cold_dir = PRODUCTION / 'renders' / args.cold
hot = json.loads((hot_dir / 'manifest.json').read_text())
cold = json.loads((cold_dir / 'manifest.json').read_text())
errors = []
for label, manifest in [('hot', hot), ('cold', cold)]:
    if manifest.get('complete') is not True or len(manifest['shots']) != 24:
        errors.append(label + ' is not a complete 24-view render')
for key in (['engine','resolution','samples'] if args.art_regression else ['source_sha256', 'renderer_sha256', 'engine', 'resolution', 'samples']):
    if hot.get(key) != cold.get(key):
        if key=='renderer_sha256' and args.renderer_change_note:continue
        errors.append('Render provenance differs: ' + key)
current_sha = hashlib.sha256((ROOT / 'module_overhaul_R2.blend').read_bytes()).hexdigest()
if (cold if args.art_regression else hot).get('source_sha256') != current_sha:
    errors.append('Evidence differs from the current saved source')
if not args.art_regression and (hot.get('cold_open') is not False or cold.get('cold_open') is not True):
    errors.append('Expected local append followed by full-file cold open')
hot_shots = {shot['id']: shot for shot in hot['shots']}
cold_shots = {shot['id']: shot for shot in cold['shots']}
if hot_shots.keys() != cold_shots.keys():
    errors.append('Camera IDs differ')
results = []
for name in sorted(hot_shots.keys() & cold_shots.keys()):
    a, b = hot_shots[name], cold_shots[name]
    camera_errors = []
    for key in ['label', 'group', 'actual_lens_mm', 'projection', 'ortho_scale_m']:
        if a.get(key) != b.get(key):
            camera_errors.append(key)
    if set(a.get('temporary_hidden_geometry', [])) != set(b.get('temporary_hidden_geometry', [])):
        camera_errors.append('temporary_hidden_geometry')
    matrix_delta = float(np.max(np.abs(np.asarray(a['camera_matrix_world']) - np.asarray(b['camera_matrix_world']))))
    if matrix_delta > 1e-6:
        camera_errors.append('camera_matrix_world')
    pa, pb = hot_dir / (name + '.png'), cold_dir / (name + '.png')
    with Image.open(pa) as ia, Image.open(pb) as ib:
        ra, rb = np.asarray(ia.convert('RGB'), dtype=np.float32), np.asarray(ib.convert('RGB'), dtype=np.float32)
    if ra.shape != rb.shape:
        errors.append(name + ': image dimensions differ')
        continue
    difference = np.abs(ra - rb)
    mae = float(np.mean(difference))
    rms = float(np.sqrt(np.mean(difference ** 2)))
    changed = float(np.mean(np.max(difference, axis=2) > 3) * 100)
    # A deterministic CPU repeat normally matches exactly. Permit only negligible
    # quantization variation; any larger difference requires manual diagnosis.
    pixel_pass = mae <= .25 and rms <= .5 and changed <= .1
    passed = pixel_pass and not camera_errors
    if not passed:
        errors.append(name + ': camera or pixel comparison failed')
    results.append({'id': name, 'pass': passed, 'camera_errors': camera_errors,
                    'maximum_camera_matrix_delta': matrix_delta,
                    'byte_identical': pa.read_bytes() == pb.read_bytes(),
                    'mean_absolute_RGB_difference_255': mae,
                    'rms_RGB_difference_255': rms,
                    'maximum_RGB_difference_255': float(np.max(difference)),
                    'pixels_with_RGB_difference_above_3_percent': changed})
report = {'status': 'PASS' if not errors and len(results) == 24 else 'FAIL','mode':'art-regression' if args.art_regression else 'cold-stability',
          'renderer_hashes':{'hot':hot.get('renderer_sha256'),'cold':cold.get('renderer_sha256')},'renderer_change_note':args.renderer_change_note,
          'source_sha256': current_sha, 'hot_cycle': args.hot, 'cold_cycle': args.cold,
          'thresholds': {'mean_absolute_RGB_255': .25, 'rms_RGB_255': .5,
                         'pixels_above_3_RGB_levels_percent': .1, 'camera_matrix_delta': 1e-6},
          'errors': errors, 'views': results}
report_name=('art-render-comparison-'+args.hot+'-'+args.cold+'.json') if args.art_regression else 'cold-render-comparison.json'
(PRODUCTION / report_name).write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'status': report['status'], 'views': len(results),
                  'byte_identical_views': sum(v['byte_identical'] for v in results),
                  'errors': errors}, indent=2))
if report['status'] != 'PASS':
    raise SystemExit(1)
