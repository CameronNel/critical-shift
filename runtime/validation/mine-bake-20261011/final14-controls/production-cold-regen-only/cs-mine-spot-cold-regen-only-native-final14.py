from pathlib import Path
import hashlib,json,shutil,subprocess,traceback
import OpenEXR,numpy as np
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';folder=project/'Assets/CsSpotColdRegenOnlyDiagnostic';helper=project/'Assets/CriticalShift/Bootstrap/Player/Editor/CsMineSpotColdRegenOnlyFinal14.cs';state=Path('/tmp/cs-mine-spot-cold-regen-only-native-final14.json');assert not state.exists() and not helper.exists() and not folder.exists() and not (project/'Temp/UnityLockfile').exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
api=json.loads(Path('/tmp/cs-mine-production-spot-cold-regen-only-api-final14.json').read_text());assert api['status']=='PassedApiCompileOnly';assert all(sha(Path(p))==h for p,h in api['sources'].items())
generated=project/'Assets/CriticalShift/Generated/Spawn';paths=[generated/n for n in ['prepared-scene.json','AssembledMap.unity','map-bindings.json','rig-bindings.json','mine-point-bake-output.json']]+[project/'Assets/CriticalShift/Features/Player'/n for n in ['BlenderPointLighting.cginc','BlenderSurface.shader']]+[Path('/tmp')/n for n in ['cs-mine-spot-cold-regen-only-final14.cs.txt','cs-mine-spot-rt-isolation-clone-final14.shader.txt','cs-mine-spot-rt-isolation-explicit-final14.shader.txt','cs-mine-front-spot-control-final14.cginc.txt','cs-mine-production-spot-baseline-final14.shader.txt','cs-mine-production-spot-source-control-input-final14.json','cs-mine-spot-cold-regen-only-native-final14.py','cs-mine-front-spot-source-control-final14/provenance.json']];pins={str(p):sha(p) for p in paths}|api['sources'];result={'state':'RunningActualRealtimeIsolation_NoBake','pins':pins,'limits':['5cold diagnosticframes; regen-only before anyCamera/GPUprobe; noBake','No code/imagecorrection or mainScene save; no finalpixel/visual acceptance']};state.write_text(json.dumps(result,indent=2)+'\n');owned=False;cookie=generated/'Surfaces/MineSpot-3df5c28f-400ba058-3f4ccccd.asset';assert not cookie.exists()
try:
 folder.mkdir();owned=True;shutil.copyfile('/tmp/cs-mine-spot-cold-regen-only-final14.cs.txt',helper)

 log=audit/'spot-cold-regen-only-final14.native.log';wrapper=audit/'spot-cold-regen-only-final14.wrapper.log';assert not log.exists() and not wrapper.exists();args=['xvfb-run','-a','-s','-screen 0 1440x810x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CsMineSpotColdRegenOnlyFinal14.Render','-logFile',str(log)]
 with wrapper.open('x') as f:subprocess.run(args,cwd=root,stdout=f,stderr=subprocess.STDOUT,check=True)
 t=log.read_text(errors='replace');assert t.count('CS_ACTUAL_COLD_REGENONLY_OK')==1 and 'Shader error in' not in t and 'Lightmapping:Bake' not in t
 out=Path('/tmp/cs-mine-spot-cold-regen-only-final14');expected={n+'-cold-before-blit' for n in ['d1-a0','d2-a0','d4-a0','d4-a50','d4-a65']};assert len(expected)==5 and {p.name for p in out.iterdir()}=={n+e for n in expected for e in ['.json','.exr']}|{'ProductionCookie.asset','ProductionCookie.asset.meta'};frames=[]
 for p in sorted(out.glob('*.exr')):
  m=json.loads(p.with_suffix('.json').read_text());assert m['name']==p.stem and p.stem.endswith('-'+m['mode']) and sha(p)==m['fileSha256'] and m['actualLightType']=='Spot' and m['actualBakeType']=='Realtime' and not m['actualOutputIsBaked'] and m['lightmapIndex']==-1 and m['lightmapCount']==0 and m['probeCount']==0;x=OpenEXR.File(str(p)).channels()['RGBA'].pixels[...,:3];assert x.shape==(64,64,3) and np.isfinite(x).all();frames.append({'name':p.stem,'sha256':sha(p),'metadataSha256':sha(p.with_suffix('.json')),'meanCentreRGB':x[28:36,28:36].astype(float).mean((0,1)).tolist()})
 assert all(sha(Path(p))==h for p,h in pins.items());result.update(state='PassedBoundedRTIsolationTechnicalChecksAwaitingIndependentPixels',frames=frames,logSha256=sha(log));state.write_text(json.dumps(result,indent=2)+'\n');print(result['state'])
except BaseException as e:
 result.update(state='FailedRTIsolation',error=repr(e),traceback=traceback.format_exc());state.write_text(json.dumps(result,indent=2)+'\n');raise
finally:
 helper.unlink(missing_ok=True);helper.with_suffix('.cs.meta').unlink(missing_ok=True)
 if owned:shutil.rmtree(folder);folder.with_suffix('.meta').unlink(missing_ok=True)
 if cookie.exists():
  backup=Path('/tmp/cs-mine-spot-cold-regen-only-failed-cookie-final14');backup.mkdir()
  for p in [cookie,cookie.with_suffix('.asset.meta')]:
   if p.exists():shutil.copyfile(p,backup/p.name);assert sha(p)==sha(backup/p.name);p.unlink()
