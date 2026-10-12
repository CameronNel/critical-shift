from pathlib import Path
import json,hashlib,shutil
root=Path('/workspace/critical-shift-spawn-runtime');dst=root/'runtime/validation/mine-bake-20261011/fresh-export-final11/controls';dst.mkdir(parents=True,exist_ok=True)
directories=['cs-mine-point-control-final11','cs-mine-point-native-final11','cs-mine-transport-native-final11','cs-mine-world-control-final11','cs-mine-physical-point-native-final11','cs-mine-production-point-native-final11','cs-mine-near-source-final11','cs-mine-radius-corrected-final11','cs-mine-sun-caster-native-final11','cs-mine-normal-compression-final11','cs-mine-normal-uv-native-final11','cs-mine-source-geometry-position-final11','cs-mine-density-lamp-final11']
files=[]
for name in directories:
 folder=Path('/tmp')/name
 if not folder.exists():continue
 for p in sorted(folder.glob('*')):
  if not p.is_file():continue
  # Keep raw radiometry/cookie/shadow controls; geometry/material full EXRs
  # remain scratch diagnostics, not accepted final camera evidence.
  if p.suffix not in {'.json','.png'} and not (p.suffix=='.exr' and 'point' in name or p.suffix=='.exr' and ('radius' in name or 'sun-caster' in name or 'near-source' in name)):continue
  q=dst/name/p.name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);files.append({'file':str(q.relative_to(dst)),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()})
for p in sorted(Path('/tmp').glob('cs-mine-*final11*')):
 if p.is_file() and (p.suffix in {'.py','.shader','.cginc'} or p.name.endswith('.cs.txt')):
  q=dst/'helpers'/p.name;q.parent.mkdir(exist_ok=True);shutil.copyfile(p,q);files.append({'file':str(q.relative_to(dst)),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()})
for name in ['cs-mine-radius-corrected-final11.native.log','cs-mine-radius-corrected-final11.wrapper.log','CsMineProductionPointFinal11.Render.native.log','CsMineSunCasterFinal11.Render.native.log','cs-mine-normal-compression-final11.native.log','cs-mine-density-lamp-final11.log','cs-mine-source-geometry-position-final11.log']:
 p=root/'runtime/out/mine-bake-audit'/name
 if p.exists():
  q=dst/'logs'/name;q.parent.mkdir(exist_ok=True);shutil.copyfile(p,q);files.append({'file':str(q.relative_to(dst)),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()})
records={'status':'Diagnostic controls; no final visual acceptance','sourceBlenderSha256':hashlib.sha256((root/'runtime/out/spawn-export-source/combined-runtime-source.blend').read_bytes()).hexdigest(),'canonicalSourcesChanged':False,'sourcePositionShiftNormalResult':'Duct normal unchanged; not the normal artifact cause','uncompressedNormalResult':'Duct ROI mean12.99deg versusBC512.96deg; compression not cause','pointRuntimeNear':'Matches source <0.15% at .06/.12/.24m; old cap rejected','pointInverseSquareNativeGI':'REJECTED: emitter radius ignored in attenuation; source near controls and nearest visible lamp surfaces disprove production use','legacyGI':'Temporary diagnostic baseline retained; no final lighting parity claim','SUNCaster':'Static deep-umbra and dynamic BlendProbes wall-occlusion controls pass; real actor and soft-edge/full-scene gates pending','files':files}
(dst/'control-provenance.json').write_text(json.dumps(records,indent=2)+'\n')
print('CS_FINAL11_CONTROLS_ARCHIVED',len(files),sum((dst/f['file']).stat().st_size for f in files))
