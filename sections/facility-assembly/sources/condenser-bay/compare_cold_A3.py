"""Cold comparison of two complete render sets made by render_review_A3.py in separate Blender processes
(sections/condenser-bay/production/COLD_COMPARISON_POLICY.md, CPU screen: mean channel difference at most 0.01/255, maximum 2/255).

    python3 compare_cold_A3.py <set A dir> <set B dir> <report.json>

Checks that both sets come from the same blend hash, script hash and settings, in different processes, with every image's hash matching its
manifest; then measures each camera pair. Exit code 1 when anything differs from the policy. A numerical pass is not art acceptance.
"""
import sys, json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image

A, B, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
ma, mb = (json.loads((d / 'manifest.json').read_text()) for d in (A, B))
problems = []
for k in ('blend_sha256', 'script_sha256', 'blender', 'device', 'resolution', 'samples', 'seed', 'denoiser', 'view_transform', 'look', 'exposure'):
    if ma[k] != mb[k]: problems.append('%s differs: %s / %s' % (k, ma[k], mb[k]))
if ma['pid'] == mb['pid']: problems.append('same process id: not a separate cold open')
if sorted(ma['images']) != sorted(mb['images']): problems.append('camera sets differ')
rows = {}
for n in sorted(set(ma['images']) & set(mb['images'])):
    ia, ib = ma['images'][n], mb['images'][n]
    for d, i in ((A, ia), (B, ib)):
        if hashlib.sha256((d / i['file']).read_bytes()).hexdigest() != i['sha256']: problems.append('%s: image hash does not match its manifest in %s' % (n, d))
    if ia['matrix'] != ib['matrix'] or ia['lens_mm'] != ib['lens_mm']: problems.append('%s: camera differs' % n)
    pa = np.asarray(Image.open(A / ia['file']).convert('RGB'), dtype=np.int16); pb = np.asarray(Image.open(B / ib['file']).convert('RGB'), dtype=np.int16)
    diff = np.abs(pa - pb)
    r = dict(mean=round(float(diff.mean()), 5), max=int(diff.max()), changed_fraction=round(float((diff.max(axis=2) > 0).mean()), 6))
    if r['mean'] > 0.01 or r['max'] > 2: problems.append('%s: over the CPU screen (mean %.5f, max %d)' % (n, r['mean'], r['max']))
    rows[n] = r
report = dict(set_a=str(A.name), set_b=str(B.name), pid_a=ma['pid'], pid_b=mb['pid'], blend_sha256=ma['blend_sha256'], settings=dict(
    resolution=ma['resolution'], samples=ma['samples'], device=ma['device']), screen=dict(mean_max=0.01, max_max=2), cameras=rows,
    ok=not problems, problems=problems)
OUT.write_text(json.dumps(report, indent=1) + '\n')
for n, r in rows.items(): print('COLD %-20s mean %.5f max %d changed %.6f' % (n, r['mean'], r['max'], r['changed_fraction']))
print('COLD', 'PASS' if not problems else 'FAIL: %s' % problems)
sys.exit(0 if not problems else 1)
