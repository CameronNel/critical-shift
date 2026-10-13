from pathlib import Path
import hashlib,json,subprocess,shutil,traceback
import OpenEXR,numpy as np

root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit'
name='CsMineSpotBakeLifecycleFinal15';source=Path('/tmp/cs-mine-spot-bake-lifecycle-final15.cs.txt')
helper=project/'Assets/CriticalShift/Bootstrap/Player/Editor'/(name+'.cs')
folder=project/'Assets/CsSpotBakeLifecycleDiagnosticFinal15';out=Path('/tmp/cs-mine-spot-bake-lifecycle-final15')
state=Path('/tmp/cs-mine-spot-bake-lifecycle-native-final15.json');api=Path('/tmp/cs-mine-spot-bake-lifecycle-api-final15.json')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not state.exists() and not helper.exists() and not folder.exists() and not out.exists() and not (project/'Temp/UnityLockfile').exists()
previous=json.loads(Path('/tmp/cs-mine-production-spot-api-final14-r5.json').read_text())
sources=list((project/'Assets/CriticalShift/Bootstrap/Player/Editor').glob('*.cs'))+[source]
cmd=[c for c in previous['command'] if not c.endswith('.cs') and not c.endswith('.cs.txt') and not c.startswith('-out:')]
cmd+=['-out:/tmp/cs-mine-spot-bake-lifecycle-api-final15.dll']+list(map(str,sources))
p=subprocess.run(cmd,capture_output=True,text=True)
api.write_text(json.dumps({'status':'PassedApiCompileOnly' if p.returncode==0 else 'FailedApiCompileOnly','returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'command':cmd,'sources':{str(s):sha(s) for s in sources}},indent=2)+'\n')
assert p.returncode==0,p.stdout+p.stderr
generated=project/'Assets/CriticalShift/Generated/Spawn'
cookie=generated/'Surfaces/MineSpot-3df5c28f-400ba058-3f4ccccd.asset';assert not cookie.exists()
pins={str(p):sha(p) for p in sources+[project/'Assets/CriticalShift/Features/Player/BlenderPointLighting.cginc',project/'Assets/CriticalShift/Features/Player/BlenderSurface.shader',Path(__file__),api]+[generated/n for n in ['prepared-scene.json','AssembledMap.unity','map-bindings.json','rig-bindings.json','mine-point-bake-output.json']]}
result={'status':'RunningActualBakePersistentRealtimeAndFreshReload','pins':pins,'limits':['Direct-light isolated receiver after actual Bake; not full map GI','No cookie GPU probe, force import or bakingOutput reset before first capture','Actual Generate scene and canonical map remain untouched']};state.write_text(json.dumps(result,indent=2)+'\n')
owned=False
try:
 shutil.copyfile(source,helper);owned=True
 for method in ['Bake','Reload']:
  log=audit/('spot-bake-lifecycle-final15-'+method.lower()+'.native.log');wrapper=log.with_suffix('.wrapper.log');assert not log.exists() and not wrapper.exists()
  args=['xvfb-run','-a','-s','-screen 0 1440x810x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod',name+'.'+method,'-logFile',str(log)]
  with wrapper.open('x') as f:subprocess.run(args,cwd=root,stdout=f,stderr=subprocess.STDOUT,check=True)
  t=log.read_text(errors='replace');marker='CS_LIFECYCLE_'+method.upper()+'_PHASE_OK';assert t.count(marker)==1 and 'Shader error in' not in t
  if method=='Bake':
   # Save every serialized referenced asset before the second editor starts.
   dest=out/'serialized-assets';dest.mkdir();assets=[]
   for relative in (out/'scene-dependencies.txt').read_text().splitlines():
    p=project/relative
    if not p.is_file():continue
    for candidate in [p,p.with_name(p.name+'.meta')]:
     if not candidate.is_file():continue
     target=dest/candidate.relative_to(project);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(candidate,target);assert sha(candidate)==sha(target)
     assets.append({'path':str(candidate.relative_to(project)),'sha256':sha(candidate),'bytes':candidate.stat().st_size})
   (out/'serialized-assets.json').write_text(json.dumps(assets,indent=2)+'\n')
   result['bakePhase']='PassedTechnicalAwaitingReloadAndPixels';state.write_text(json.dumps(result,indent=2)+'\n');print(result['bakePhase'],flush=True)
  else:
   for r in json.loads((out/'serialized-assets.json').read_text()):assert sha(project/r['path'])==r['sha256'],r['path']
 frames=[]
 for p in sorted(out.glob('*.exr')):
  m=json.loads(p.with_suffix('.json').read_text());assert sha(p)==m['sha256'];x=OpenEXR.File(str(p)).channels()['RGBA'].pixels[...,:3];assert x.shape==(64,64,3) and np.isfinite(x).all()
  frames.append({'name':p.stem,'sha256':sha(p),'meanCentreRGB':x[28:36,28:36].astype(float).mean((0,1)).tolist(),'mode':m['mode'],'outputIsBaked':m['outputIsBaked'],'cookieGuid':m['cookieGuid']})
 assert len(frames)==16
 for p,h in pins.items():assert sha(Path(p))==h,p
 result.update(status='CompletedLifecycleTechnicalChecksAwaitingIndependentPixels',frames=frames);state.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],flush=True)
except BaseException as e:
 result.update(status='FailedLifecycleControl',error=repr(e),traceback=traceback.format_exc());state.write_text(json.dumps(result,indent=2)+'\n');raise
finally:
 if owned:
  helper.unlink(missing_ok=True);helper.with_suffix('.cs.meta').unlink(missing_ok=True)
  if folder.exists():shutil.rmtree(folder);folder.with_suffix('.meta').unlink(missing_ok=True)
  if cookie.exists():
   dest=out/'owned-cookie';dest.mkdir(exist_ok=False)
   for p in [cookie,cookie.with_suffix('.asset.meta')]:
    if p.exists():shutil.copyfile(p,dest/p.name);assert sha(p)==sha(dest/p.name);p.unlink()
