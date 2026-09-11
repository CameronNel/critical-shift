"""Refresh current evidence documentation without assigning reviewer scores."""
from pathlib import Path
import json, sys

root=Path(__file__).resolve().parents[1]
revision=sys.argv[1]
manifest=json.loads((root/f'production/renders/review/{revision}/render_manifest.json').read_text(encoding='utf-8'))
rows=['# Evaluation cameras','',f'Current full-room evidence: {revision}, {manifest["resolution"][0]} × {manifest["resolution"][1]}, {manifest["samples"]} samples, {manifest["backend"]}. Transforms below are read from the actual render manifest. Rotation is XYZ Euler in radians.','',
'Ten primary cameras C01–C10 remain fixed from R04. C05/C06/C09 were widened at R04; supplementary W04/W06 changed at R06 and W08 at R07. Earlier frames remain in their historical folders. Eight supplementary eye-height views cover approaches, service routes and withdrawal clearance.','',
'| Camera | Position XYZ, metres | Rotation XYZ, radians | Lens mm |','|---|---|---|---:|']
for c in manifest['cameras']:
    rows.append('| '+c['camera']+' | '+', '.join(f'{v:.4f}' for v in c['location'])+' | '+', '.join(f'{v:.4f}' for v in c['rotation'])+f' | {c["lens"]:g} |')
(root/'production/CAMERAS.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
(root/'production/RUBRIC.md').write_text('''# Independent integration-readiness rubric

Luna independently inspects actual rendered pixels and measured evidence. Each category must reach 90/100; no average can conceal a failure. Categories: specification coverage, layout/flow, machinery, navigation/readability, construction, materials, lighting and reference fidelity. Geometry checks alone never establish art approval.

Hard failures include obstructed routes or maintenance access, missing required machinery, unsupported assemblies, obscured signage, teal palette, plastic-looking uniform materials, inadequate lighting, material departure from the approved Valorant concepts, or invented evidence. Concepts are guidance and cannot change specification requirements.

The September11 user instruction supersedes the historical slice-first gate and fixed four-cycle/two-stable-cycle rules: deliver the complete integration-ready room, correct every relevant category below90, and verify the saved artifact. Earlier reviews remain intact as history; their old workflow language does not govern this resumed run. Current reviews are in critics/luna-Rxx-full-review.md. No whole-map/runtime approval is implied.
''',encoding='utf-8')
p=root/'production/technical/README.md'
s=p.read_text(encoding='utf-8').replace('--revision S02',f'--revision {revision}')
s=s.replace('independent scores of at least 90 in every required category, four genuine full review cycles, ten fixed-camera final renders, stable last two cycles and a fresh-process render comparison are mandatory.','independent scores of at least 90 in every required category, ten fixed-camera final renders and a fresh-process render comparison are required by the current user workflow.')
p.write_text(s,encoding='utf-8')
print('EVIDENCE_INDEX_UPDATED',revision)
