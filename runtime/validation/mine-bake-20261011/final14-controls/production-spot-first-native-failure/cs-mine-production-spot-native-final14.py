from pathlib import Path
import hashlib,json,subprocess,shutil,traceback
import OpenEXR,numpy as np
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';helper=project/'Assets/CriticalShift/Bootstrap/Player/Editor/CsMineProductionSpotControlFinal14.cs';folder=project/'Assets/CsProductionSpotControlDiagnostic';state=Path('/tmp/cs-mine-production-spot-native-final14.json');assert not state.exists() and not helper.exists() and not folder.exists() and not (project/'Temp/UnityLockfile').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();generated=project/'Assets/CriticalShift/Generated/Spawn';sources=list((project/'Assets/CriticalShift/Bootstrap/Player/Editor').glob('*.cs'))+[project/'Assets/CriticalShift/Features/Player/BlenderPointLighting.cginc',project/'Assets/CriticalShift/Features/Player/BlenderSurface.shader',root/'runtime/tools/mine_context_lights.py']
inputs=[generated/n for n in ['prepared-scene.json','AssembledMap.unity','map-bindings.json','rig-bindings.json','mine-point-bake-output.json']]+sources+[Path('/tmp')/n for n in ['cs-mine-production-spot-control-final14.cs.txt','cs-mine-production-spot-baseline-final14.shader.txt','cs-mine-production-spot-source-control-input-final14.json','cs-mine-production-spot-source-final14.json','cs-mine-production-spot-api-final14-r3.json','cs-mine-front-spot-source-control-final14/provenance.json','cs-mine-production-spot-native-final14.py']]
pins={str(p):sha(p) for p in inputs};api=json.loads(Path('/tmp/cs-mine-production-spot-api-final14-r3.json').read_text());assert api['status']=='PassedApiCompileOnly' and api['helperSha256']==pins['/tmp/cs-mine-production-spot-control-final14.cs.txt'];assert all(sha(Path(p))==h for p,h in api['sources'].items())
contract=json.loads(Path('/tmp/cs-mine-production-spot-source-final14.json').read_text());assert len(contract['lights'])==6 and contract['exporterSha256']==pins[str(root/'runtime/tools/mine_context_lights.py')]
sp=json.loads(Path('/tmp/cs-mine-front-spot-source-control-final14/provenance.json').read_text());expected={r['name']+'-'+mode for r in sp['frames'] for mode in ['realtime-tagged','baked-tagged']}|{'d4-a0-shadow-clear','d4-a0-shadow-blocker','d4-a0-fallback-production','d4-a0-fallback-stock'};assert len(expected)==20
result={'state':'RunningActualProductionSpotControl','pins':pins,'limits':['20 boundedfixtures; no Source/Generatedscene save, mainmap bake or98 claim']};state.write_text(json.dumps(result,indent=2)+'\n');owned=False
cookie=generated/'Surfaces/MineSpot-3df5c28f-400ba058-3f4ccccd.asset';assert not cookie.exists(),cookie
try:
 shutil.copyfile('/tmp/cs-mine-production-spot-control-final14.cs.txt',helper);folder.mkdir();owned=True;shutil.copyfile('/tmp/cs-mine-production-spot-baseline-final14.shader.txt',folder/'StockSpotBaseline.shader')
 log=audit/'production-spot-control-final14.native.log';wrapper=audit/'production-spot-control-final14.wrapper.log';assert not log.exists() and not wrapper.exists()
 args=['xvfb-run','-a','-s','-screen 0 1440x810x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CsMineProductionSpotControlFinal14.Render','-logFile',str(log)]
 with wrapper.open('x') as f:subprocess.run(args,cwd=root,stdout=f,stderr=subprocess.STDOUT,check=True)
 t=log.read_text(errors='replace');assert t.count('CS_ACTUAL_PRODUCTION_SPOT_CONTROL_OK')==1 and t.count('CS_PRODUCTION_SPOT_CONTRACT_SCOPE_OK')==1 and 'Shader error in' not in t
 out=Path('/tmp/cs-mine-production-spot-native-control-final14');assert {p.name for p in out.iterdir()}=={n+e for n in expected for e in ['.json','.exr']}|{'ProductionCookie.asset','ProductionCookie.asset.meta'}
 frames=[]
 for name in sorted(expected):
  p=out/(name+'.exr');m=json.loads(p.with_suffix('.json').read_text());assert sha(p)==m['fileSha256'] and m['nonfiniteRGBPixels']==0 and (m['width'],m['height'])==(64,64);x=OpenEXR.File(str(p)).channels()['RGBA'].pixels[...,:3];assert x.shape==(64,64,3) and np.isfinite(x).all();mean=x[28:36,28:36].astype(float).mean((0,1));assert m['shadows']=='Soft' and m['range']==32
  if '-baked-' in name:assert ('CS_SPOT_BAKE_CALLBACK_OK '+name+' calls=') in t and ('CS_SPOT_EXTRACTION '+name+' intensity=') in t and m['lightmapIndex']>=0 and m['lightmapCount']>0
  else:assert m['lightmapIndex']==-1 and m['lightmapCount']==0 and m['probeCount']==0
  if 'realtime' in name and m['angle']==0:assert mean[0]>.1
  frames.append({'name':name,'sha256':sha(p),'metadataSha256':sha(p.with_suffix('.json')),'meanCentreRGB':mean.tolist()})
 for p,h in pins.items():assert sha(Path(p))==h,p
 result.update(state='PassedActualProductionBoundedTechnicalChecksAwaitingIndependentPixels',frames=frames,command=args,logSha256=sha(log));state.write_text(json.dumps(result,indent=2)+'\n');print(result['state'],flush=True)
except BaseException as e:
 result.update(state='FailedActualProductionSpotControl',error=repr(e),traceback=traceback.format_exc());state.write_text(json.dumps(result,indent=2)+'\n');raise
finally:
 helper.unlink(missing_ok=True);helper.with_suffix('.cs.meta').unlink(missing_ok=True)
 if owned and folder.exists():shutil.rmtree(folder);folder.with_suffix('.meta').unlink(missing_ok=True)
 # Preserve a failed fixture cookie's exact asset/meta bytes before releasing only that owned path.
 if cookie.exists():
  target=Path('/tmp/cs-mine-production-spot-failed-cookie-final14');target.mkdir(exist_ok=False)
  for p in [cookie,cookie.with_suffix('.asset.meta')]:
   if p.exists():shutil.copyfile(p,target/p.name);assert sha(p)==sha(target/p.name);p.unlink()
