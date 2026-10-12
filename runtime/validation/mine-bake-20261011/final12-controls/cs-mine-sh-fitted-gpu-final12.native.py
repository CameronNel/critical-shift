from pathlib import Path
import json,hashlib,subprocess,shutil,numpy as np,OpenEXR
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';out=Path('/tmp/cs-mine-sh-fitted-gpu-final12');assert not out.exists();out.mkdir()
fit=Path('/tmp/cs-mine-sh-fit-final12/fit.json');basis=Path('/tmp/cs-mine-sh-basis-measured-final12/basis.json');f=json.loads(fit.read_text());b=json.loads(basis.read_text());assert b['status']=='PassedBasisControlOnly';coeff=np.array(f['coefficientsRGBByNativeIndex']).T;assert coeff.shape==(9,3) and np.isfinite(coeff).all()
def v(a):return dict(zip(['x','y','z'],map(float,a)))
data={'coefficients':[{'rgb':v(c)} for c in coeff],'samples':[{'direction':r['direction'],'expectedClampedEOverPi':v(np.maximum(np.array(r['cpuOffsetBasis'])@coeff,0))} for r in b['rows']]};(out/'inputs.json').write_text(json.dumps(data,indent=2)+'\n')
helper=project/'Assets/CriticalShift/Bootstrap/Player/Editor/CsMineShFittedGpuFinal12.cs';assert not helper.exists();inputs=[Path(__file__),Path('/tmp/cs-mine-sh-fitted-gpu-final12.cs.txt'),fit,basis,out/'inputs.json',project/'Assets/CriticalShift/Features/Player/BlenderSurface.shader',project/'Assets/CriticalShift/Features/Player/BlenderPointLighting.cginc'];hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs};shutil.copy2(inputs[1],helper)
try:
 with (audit/'sh-fitted-gpu-final12.wrapper.log').open('w') as log:subprocess.run(['xvfb-run','-a','-s','-screen 0 640x360x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CsMineShFittedGpuFinal12.Run','-logFile',str(audit/'sh-fitted-gpu-final12.native.log')],stdout=log,stderr=subprocess.STDOUT,cwd=root,check=True)
 proof=json.loads((out/'proof.json').read_text());assert proof['status']=='PassedFittedNeutralShaderOnly' and len(proof['rows'])==78 and len(list(out.glob('*.exr')))==78
 for row in proof['rows']:
  path=out/f"Fitted-{row['sample']:02d}-Albedo{row['albedoCase']}.exr";a=next(iter(OpenEXR.File(str(path)).channels().values())).pixels[...,:3];assert a.shape==(16,16,3) and np.isfinite(a).all();assert np.max(np.abs(a[8,8]-np.array(list(row['gpuOutgoingRGB'].values()))))<1e-6
 for p in inputs:assert hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p)]
 (out/'saved-HDR-review.json').write_text(json.dumps({'status':'PassedCoefficientPackingAndNeutralAlbedoOnly','inputs':hashes,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()},'limits':['Single sampled source location','Source sample variance/L2 truncation not accepted','No actual imported rig, actor movement/interpolation, whole map or Player proof']},indent=2)+'\n');print('CS_FITTED_NEUTRAL_GPU_SAVED_HDR_VERIFIED')
finally:helper.unlink(missing_ok=True);Path(str(helper)+'.meta').unlink(missing_ok=True)
