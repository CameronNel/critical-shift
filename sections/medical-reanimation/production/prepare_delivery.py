"""Prepare stable metadata and provenance before the final scene build; never claims approval."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
p=R/'interface.json';d=json.loads(p.read_text());d['revision']='medical-interface-1';d['validation_status']='Acceptance is recorded separately in production/FINAL_EVIDENCE.json; this file is the geometric contract.';d['equipment_bounds_role']='Inherited R09 reservation rectangles, not final manufactured projection limits. Read evaluated equipment_envelopes in production/validation.'
p.write_text(json.dumps(d,indent=2),encoding='utf-8')
records=[]
for f in sorted((R/'art/concepts').glob('*.png')):
 records.append({'file':f.relative_to(R).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'provider':'OpenAI built-in ChatGPT image generation','prompt':f'art/concepts/{f.name[:3]}-prompt.txt'})
(R/'art/concepts/provenance.json').write_text(json.dumps({'concepts':records,'source_layout_blend_sha256':d['source_layout']['sha256'],'source_images':'Read-only fresh Grok R09 renders used for layout; reactor approved construction principles and user Valorant/no-teal direction used for style.','decisions':{'M01':'rejected, materials88','M02':'reverse guidance only; invented long OCRU expansion rejected','M03':'approved by independent Luna','M04':'approved by independent Luna','M05':'approved by independent Luna >90','M06':'approved targeted OCRU correction >90'},'authority':'Concepts guide style only, never override geometry/spec. See unedited independent reports.'},indent=2),encoding='utf-8')
print('DELIVERY_METADATA_PREPARED')
