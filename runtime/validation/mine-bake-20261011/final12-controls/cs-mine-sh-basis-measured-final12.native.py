from pathlib import Path
import subprocess,shutil,json,hashlib,numpy as np,OpenEXR
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';helper=project/'Assets/CriticalShift/Bootstrap/Player/Editor/CsMineShBasisMeasuredFinal12.cs'
output=Path('/tmp/cs-mine-sh-basis-measured-final12');assert not output.exists();inputs=[Path(__file__),Path('/tmp/cs-mine-sh-basis-measured-final12.cs.txt'),project/'Assets/CriticalShift/Features/Player/BlenderSurface.shader',project/'Assets/CriticalShift/Features/Player/BlenderPointLighting.cginc'];hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
assert not helper.exists();shutil.copy2('/tmp/cs-mine-sh-basis-measured-final12.cs.txt',helper)
try:
 with (audit/'sh-basis-measured-final12.wrapper.log').open('w') as log:
  p=subprocess.Popen(['xvfb-run','-a','-s','-screen 0 640x360x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CsMineShBasisMeasuredFinal12.Run','-logFile',str(audit/'sh-basis-measured-final12.native.log')],stdout=log,stderr=subprocess.STDOUT,cwd=root)
  print('SH_BASIS_PID',p.pid,flush=True);rc=p.wait();print('SH_BASIS_EXIT',rc,flush=True)
  if rc:raise SystemExit(rc)
 proof=json.loads((output/'basis.json').read_text());assert proof['status']=='PassedBasisControlOnly' and len(proof['rows'])==26
 images=sorted(output.glob('Basis-*.exr'));assert len(images)==286
 reread=[]
 for index,path in enumerate(images):
  pixels=next(iter(OpenEXR.File(str(path)).channels().values())).pixels[...,:3];assert pixels.shape==(16,16,3) and np.isfinite(pixels).all()
  row=proof['rows'][index//11];slot=index%11;expected=row['gpuKnownOne'] if slot==0 else row['gpuBase'] if slot==1 else row['gpuBase']+row['gpuOffsetBasis'][slot-2]
  centre=pixels[8,8]/.18;assert np.max(np.abs(centre-expected))<.0001
  reread.append({'file':path.name,'centreRGBOverAlbedo':centre.tolist(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 for p in inputs:assert hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p)]
 (output/'saved-HDR-reread.json').write_text(json.dumps({'status':'PassedSavedLinearHDRBasisOnly','files':reread,'inputs':hashes,'readOrder':'26 rows, eleven captures per row: knownconstantOne, positivebaselineFour, then nine positive-offset coefficients','notActorAcceptance':True},indent=2)+'\n')
finally:helper.unlink(missing_ok=True);Path(str(helper)+'.meta').unlink(missing_ok=True)
