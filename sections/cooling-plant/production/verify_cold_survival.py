"""Verify saved-artifact survival separately from the retained exact-pixel test."""
from pathlib import Path
import json,hashlib,sys
r=Path(__file__).resolve().parents[1];rev=sys.argv[1]
read=lambda p:json.loads((r/p).read_text(encoding='utf-8'))
comparison=read(f'production/technical/{rev}-cold-start.json')
review=read(f'production/critics/luna-{rev}-cold-review.json')
audit=read(f'production/technical/{rev}-validation.json')
digest=hashlib.sha256((r/'blender/cooling_plant.blend').read_bytes()).hexdigest()
passed=all([comparison['artifact_unchanged'],comparison['settings_equal'],comparison['all_ten_primary_cameras'],review['artifact_survival_approved'],review['visual_stability_approved'],audit['objective_status']=='PASS',digest==comparison['blend_sha256']])
report=dict(revision=rev,status='PASS' if passed else 'REVIEW',blend_sha256=digest,artifact_unchanged=digest==comparison['blend_sha256'],
    exact_pixel_test_status=comparison['status'],bit_identical=all(c['decoded_pixels_equal'] for c in comparison['cameras']),
    max_channel_difference=max(c['max_channel_difference'] for c in comparison['cameras']),
    maximum_changed_channel_percent=max(100*c['changed_channels']/(c['dimensions'][0]*c['dimensions'][1]*c['dimensions'][2]) for c in comparison['cameras']),
    maximum_mean_absolute_difference=max(c['mean_absolute_difference'] for c in comparison['cameras']),
    acceptance_basis='Fresh-file geometry/dependency/camera checks plus all ten successful renders and independent Luna inspection of cold images. User requires saved-artifact survival; bit-exact GPU pixels are reported separately and are not claimed.',
    independent_review=review,
    retained_comparison=f'{rev}-cold-start.json',
    limitations='Not bit-identical. Differences over one 8-bit channel step localize to conformed HX shell lettering; numerical surface sensitivity is an inference, not a proven renderer diagnosis. Historical exact-pixel REVIEW is retained unchanged. No runtime or whole-map claim.')
(r/f'production/technical/{rev}-cold-survival.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(r/f'production/technical/{rev}-cold-survival.md').write_text(f'''# {rev} saved-artifact cold-open verification

**{report['status']} for artifact survival and independently reviewed visual stability. Not bit-identical.**

The exact comparison remains [REVIEW]({rev}-cold-start.md), with every numerical difference recorded. Across ten images, at most {report['maximum_changed_channel_percent']:.5f}% of RGB channels changed; maximum difference {report['max_channel_difference']}/255, maximum mean absolute difference {report['maximum_mean_absolute_difference']:.7f}/255. No comparison tolerance was increased or failed result overwritten.

{report['acceptance_basis']}

Independent assessment: [Luna cold review](../critics/luna-{rev}-cold-review.md). Saved Blender SHA256: `{digest}`. Geometry, assigned materials, native text, cameras and connection metadata survive reopening. Live MCP's built-in-font sentinel warning is retained in the live inspection report.

{report['limitations']}
''',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='independent_review'}))
if not passed:sys.exit(2)
