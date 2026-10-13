from pathlib import Path
import json,hashlib,subprocess,time,traceback
import OpenEXR,numpy as np
from PIL import Image
source=Path('/tmp/cs-compact-main342-final14');helper=Path('/tmp/cs-main342-source-renders-final15-r2.blender.py');state=Path('/tmp/cs-main342-source-renders-native-final15-r2.json')
prep=Path('/tmp/cs-current-main-surface-preparation-final15-r6.json');log=Path('/tmp/cs-main342-source-renders-native-final15-r2.log')
assert not state.exists() and not log.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins={str(p):sha(p) for p in [helper,Path(__file__),source/'combined-runtime-source.blend',source/'map-config.json',Path('/workspace/critical-shift-spawn-runtime/runtime/out/mine-bake-audit/cameras.json')]}
result={'status':'WaitingForCompletedCurrentMainSurfaces','pins':pins};state.write_text(json.dumps(result,indent=2)+'\n')
try:
 while True:
  j=json.loads(prep.read_text())
  if j['status'].startswith('Failed'):raise RuntimeError('Surface preparation failed; Source render not launched')
  if j['status']=='CompletedFreshCurrentMainSurfaces_NotNativeUnityAccepted':break
  time.sleep(5)
 for p,h in pins.items():assert sha(Path(p))==h,p
 result.update(status='RenderingCurrentCompactSource',preparationStateSha256=sha(prep));state.write_text(json.dumps(result,indent=2)+'\n')
 args=['/home/agent/.local/bin/blender','-b',str(source/'combined-runtime-source.blend'),'-t','4','--disable-autoexec','--python-exit-code','1','--python',str(helper)]
 with log.open('x') as f:subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,check=True)
 out=Path('/tmp/cs-main342-source-renders-final15-r2');proof=json.loads((out/'provenance.json').read_text());assert len(proof['views'])==3
 expected={'R39_01_PORTAL_APPROACH','R39_02_TUNNEL','R39_04_SHED_FRONT'}
 assert {r['name'] for r in proof['views']}==expected
 assert {p.name for p in out.iterdir()}=={'provenance.json'}|{n+e for n in expected for e in ['.png','-linear.exr']}
 for r in proof['views']:
  png=out/(r['name']+'.png');assert sha(png)==r['pngSha256']
  with Image.open(png) as image:assert image.size==(1440,810);image.load()
  p=out/(r['name']+'-linear.exr');assert sha(p)==r['hdrSha256'];channels=OpenEXR.File(str(p)).channels();x=channels.get('RGB',channels.get('RGBA')).pixels[:,:,:3];assert x.shape==(810,1440,3) and np.isfinite(x).all()
 for p,h in pins.items():assert sha(Path(p))==h,p
 result.update(status='PassedCurrentSourceRenderTechnicalChecks_IndependentComparisonPending',provenanceSha256=sha(out/'provenance.json'),command=args,logSha256=sha(log));state.write_text(json.dumps(result,indent=2)+'\n')
except BaseException as e:
 result.update(status='FailedCurrentSourceRender',error=repr(e),traceback=traceback.format_exc());state.write_text(json.dumps(result,indent=2)+'\n');raise
