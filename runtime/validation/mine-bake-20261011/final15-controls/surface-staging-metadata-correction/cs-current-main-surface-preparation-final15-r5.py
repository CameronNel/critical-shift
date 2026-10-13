from pathlib import Path
import os,json,hashlib,subprocess,traceback,time
root=Path('/workspace/critical-shift-spawn-runtime');source=Path('/tmp/cs-compact-main342-final14');out=Path('/tmp/cs-compact-main342-geometry-final15')
geometry_state=Path('/tmp/cs-compact-main342-geometry-export-final15.json');state=Path('/tmp/cs-current-main-surface-preparation-final15-r5.json')
audit=Path('/tmp/cs-current-main-surface-audit-final15-r5');assert not state.exists() and not audit.exists();audit.mkdir()
import sys
sys.path.insert(0,str(root/'runtime/tools'))
from map_source_snapshot import verified_snapshot
verified_snapshot(source,'342af0003fec9dbe80b5acb40d1477c23b5a3169')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=list((root/'runtime/tools').glob('export_*.py'))+[root/'runtime/tools'/n for n in ['prepare_mine.py','prepare_spawn.py','prepare_player.py','map_source_snapshot.py','mine_context_lights.py','mine_delivery_uv.py','mine_lightmap_uv.py','mine_join_rays.py','normal_bake_pixels.py']]
old=root/'runtime/unity/Assets/CriticalShift/Generated/Spawn'
def records(value):
 if isinstance(value,dict):
  if 'file' in value and 'sha256' in value:yield value
  for child in value.values():yield from records(child)
 elif isinstance(value,list):
  for child in value:yield from records(child)
rig=json.loads((old/'rig-bindings.json').read_text())
assert sha(old/'CrewWorker.fbx')==rig['fbx_sha256']
assert sha(old/rig['animationFile'])==rig['animationSha256']
rig_inputs=[old/n for n in ['rig-bindings.json','CrewWorker.fbx',rig['animationFile']]]
for r in records(rig):
 p=old/r['file'];assert sha(p)==r['sha256'];rig_inputs.append(p)
rig_inputs+= [Path(str(p)+'.meta') for p in rig_inputs]
files+=rig_inputs
pins={str(p):sha(p) for p in files+[Path(__file__),source/'map-config.json',source/'combined-runtime-source.blend']};result={'status':'WaitingForCompletedIsolatedGeometry','pins':pins,'limits':['Actual native integration/lighting/Player remain pending','Fresh Spawn and mine derivatives, canonical Source and Generated map unchanged until adoption']};state.write_text(json.dumps(result,indent=2)+'\n')
try:
 while True:
  j=json.loads(geometry_state.read_text())
  if j['status'].startswith('Failed'):raise RuntimeError('Geometry prerequisite failed: '+repr(j))
  if j['status']=='PassedIsolatedCurrent13GeometryAndCollisionRoundtrip_NotUnityAccepted':break
  time.sleep(5)
 for p,h in pins.items():assert sha(Path(p))==h,p
 result.update(status='PreparingFreshCurrentMainSurfaces',geometryStateSha256=sha(geometry_state));state.write_text(json.dumps(result,indent=2)+'\n')
 # Resume the completed Spawn base bake; preserve the failed lettering attempt.
 prior_path=Path('/tmp/cs-current-main-surface-preparation-final15-r4.json');prior=json.loads(prior_path.read_text())
 assert prior['status']=='FailedCurrentMainSurfacePreparation' and prior['activeStep']=='spawn-lettering'
 assert [r['name'] for r in prior['completedSteps']]==['spawn-surfaces']
 assert sha(Path('/tmp/cs-current-main-surface-audit-final15-r4/spawn-surfaces.log'))==prior['completedSteps'][0]['logSha256']
 permitted={str(root/'runtime/tools/export_spawn_floor.py'),str(root/'runtime/tools/export_spawn_suits.py'),str(Path('/tmp/cs-current-main-surface-preparation-final15-r4.py'))}
 for p,h in prior['pins'].items():
  if p not in permitted:assert sha(Path(p))==h,p
 result['resumedCompletedBaseBake']={'stateSha256':sha(prior_path),'completedSteps':prior['completedSteps']}
 metas=json.loads(Path('/tmp/cs-current-main-surface-audit-final15-r4/retained-importer-metadata.json').read_text())
 assert all(sha(out/r['path'])==r['sha256'] for r in metas)
 import shutil
 blender='/home/agent/.local/bin/blender';spawn=source/'map/sections/facility-assembly/sources/spawn-room/module.blend'
 steps=[  ('spawn-lettering',[blender,'-b',str(spawn),'-t','4','--disable-autoexec','--python-exit-code','1','--python',str(root/'runtime/tools/export_spawn_floor.py'),'--',str(out),'--lettering']),
  ('spawn-walls',[blender,'-b',str(spawn),'-t','4','--disable-autoexec','--python-exit-code','1','--python',str(root/'runtime/tools/export_spawn_floor.py'),'--',str(out),'--walls']),
  ('spawn-suits',[blender,'-b',str(spawn),'-t','4','--disable-autoexec','--python-exit-code','1','--python',str(root/'runtime/tools/export_spawn_suits.py'),'--',str(out)]),
  ('mine-surfaces',[ '/home/agent/.local/share/critical-shift/venv/bin/python',str(root/'runtime/tools/prepare_mine.py'),'--map-ref','342af0003fec9dbe80b5acb40d1477c23b5a3169','--source-snapshot',str(source),'--output',str(out),'--audit',str(audit/'mine'),'--blender',blender,'--size','4096','--batched'])]
 env=dict(os.environ,OMP_NUM_THREADS='4');env.pop('CS_SKIP_SURFACES',None)
 for name,args in steps:
  for p,h in pins.items():assert sha(Path(p))==h,p
  result.update(activeStep=name);state.write_text(json.dumps(result,indent=2)+'\n');print('START',name,flush=True)
  with (audit/(name+'.log')).open('x') as f:subprocess.run(args,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
  result.setdefault('completedSteps',[]).append({'name':name,'command':args,'logSha256':sha(audit/(name+'.log'))});state.write_text(json.dumps(result,indent=2)+'\n');print('DONE',name,flush=True)
 # Preserve the complete existing rig package, including referenced textures.
 for name in ['CrewWorker.fbx','CrewWorkerAnimations.fbx','rig-bindings.json']:
  target=out/name;assert not target.exists();shutil.copyfile(old/name,target);assert sha(old/name)==sha(target)
 def records(value):
  if isinstance(value,dict):
   if 'file' in value and 'sha256' in value:yield value
   for child in value.values():yield from records(child)
  elif isinstance(value,list):
   for child in value:yield from records(child)
 assert sha(out/'CrewWorker.fbx')==rig['fbx_sha256']
 assert sha(out/rig['animationFile'])==rig['animationSha256']
 dependencies={}
 for r in records(rig):
  relative=Path(r['file']);assert not relative.is_absolute() and '..' not in relative.parts
  if r['file'] in dependencies:assert dependencies[r['file']]==r['sha256']
  dependencies[r['file']]=r['sha256']
 for relative,digest in dependencies.items():
  p=old/relative;target=out/relative;assert sha(p)==digest
  if target.exists():assert sha(target)==digest,'Shared fresh/rig dependency differs: '+relative
  else:target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);assert sha(target)==digest
  metadata=Path(str(p)+'.meta');target_meta=Path(str(target)+'.meta');assert metadata.is_file()
  if target_meta.exists():assert sha(target_meta)==sha(metadata)
  else:shutil.copyfile(metadata,target_meta)
 manifest=json.loads((out/'map-bindings.json').read_text());delivered=[]
 for r in list(records(manifest))+list(records(rig)):
  p=out/r['file'];assert p.is_file() and sha(p)==r['sha256'],r['file'];delivered.append({'path':r['file'],'sha256':sha(p)})
 for r in manifest['rooms']:
  for key,h in [('mesh','meshSha256'),('collision','collisionSha256')]:assert sha(out/r[key])==r[h]
 for p,h in pins.items():assert sha(Path(p))==h,p
 (audit/'recursive-delivery-validation.json').write_text(json.dumps({'status':'PassedAllDeclaredMeshTextureAndRigDependencies','records':delivered,'rigSurfaceDependencies':dependencies},indent=2)+'\n')
 from map_source_snapshot import verified_snapshot
 verified_snapshot(source,'342af0003fec9dbe80b5acb40d1477c23b5a3169')
 for p,h in pins.items():assert sha(Path(p))==h,p
 result.update(status='CompletedFreshCurrentMainSurfaces_NotNativeUnityAccepted',manifestSha256=sha(out/'map-bindings.json'));state.write_text(json.dumps(result,indent=2)+'\n')
except BaseException as e:
 result.update(status='FailedCurrentMainSurfacePreparation',error=repr(e),traceback=traceback.format_exc());state.write_text(json.dumps(result,indent=2)+'\n');raise
