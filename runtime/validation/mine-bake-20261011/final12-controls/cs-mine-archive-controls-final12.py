from pathlib import Path
import shutil,json,hashlib
root=Path('/workspace/critical-shift-spawn-runtime');target=root/'runtime/validation/mine-bake-20261011/final12-controls';target.mkdir(exist_ok=True)
audit=root/'runtime/out/mine-bake-audit'
folders=['cs-mine-source-inventory-final12','cs-mine-shadow-preview-final12','cs-mine-shed-shadow-preview-final12','cs-mine-transport-split-final12','cs-mine-gi-radius-extraction-final12','cs-mine-soft-radius-control-final12','cs-mine-sun-occlusion-source-final12','cs-mine-source-hybrid-board-final12','cs-mine-hybrid-independent-final12','cs-mine-source-stable-board-final12','cs-mine-source-hybrid-lambert-probe-final12','cs-mine-lambert-probe-review-final12','cs-mine-probe-uniform-preflight-final12','cs-mine-probe-visibility-control-final12','cs-mine-probe-camera-only-preflight-final12','cs-mine-source-probe-field-final12-rejected-open-face-guard','cs-mine-source-probe-field-final12','cs-mine-sh-basis-rejected-assumed-normalization-final12','cs-mine-sh-basis-measured-final12','cs-mine-sh-fit-final12','cs-mine-sh-fitted-gpu-final12','cs-mine-mixed-direct-control-final12','cs-mine-mixed-no-mask-control-final12']
for name in folders:
 source=Path('/tmp')/name
 if source.is_dir():shutil.copytree(source,target/name,dirs_exist_ok=True)
for path in Path('/tmp').glob('cs-mine-*final12*'):
 if path.is_file() and path.suffix in ['.py','.txt','.shader','.json']:shutil.copy2(path,target/path.name)
for path in audit.iterdir():
 if path.is_file() and 'final12' in path.name:shutil.copy2(path,target/path.name)
 if path.is_dir() and path.name.startswith(('final12-rejected-','final12-interrupted-')):shutil.copytree(path,target/path.name,dirs_exist_ok=True)
records={str(p.relative_to(target)):hashlib.sha256(p.read_bytes()).hexdigest() for p in target.rglob('*') if p.is_file() and p.name!='index.json'}
(target/'index.json').write_text(json.dumps({'status':'DiagnosticEvidenceOnly','limits':'Includes deliberately rejected helpers and bounded Source/native controls, not a fresh export/bake/Player or98% acceptance','files':records},indent=2)+'\n')
print('FINAL12_EVIDENCE',len(records),'files',sum(p.stat().st_size for p in target.rglob('*') if p.is_file()),'bytes')
