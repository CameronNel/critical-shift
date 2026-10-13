# Sequential bounded Source/native controls. No scene saves or production changes.
from pathlib import Path
import hashlib,json,shutil,subprocess,traceback
import numpy as np,OpenEXR
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';out=Path('/tmp/cs-mine-timber-diagnostics-final13-r2.json');assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((audit/'full-native-final13-state.json').read_text())['state']=='FinishedTechnicalChecksAwaitingStrictVisualReview'
assert json.loads(Path('/tmp/cs-mine-fog-split-final13/provenance.json').read_text())['status']=='PassedBoundedFogSplitOnly'
assert not (project/'Temp/UnityLockfile').exists()
review=json.loads(Path('/tmp/cs-mine-strict-visual-review-final13.json').read_text());generated=project/'Assets/CriticalShift/Generated/Spawn';proof=json.loads((generated/'prepared-scene.json').read_text());assert review['preparedScene']==proof
sources=json.loads((audit/'preservation.json').read_text())['sourceRecords'];pins={str(root/'runtime/out/spawn-export-source/map'/r['path']):r['sha256'] for r in sources};pins[str(root/'runtime/out/spawn-export-source/combined-runtime-source.blend')]='255fe337aacd602e81bd2940be7bf2a1da2541954f6c8446c8a06f5aae413b72'
for name in ['prepared-scene.json','map-bindings.json','rig-bindings.json','AssembledMap.unity','mine-point-bake-output.json']:pins[str(generated/name)]=sha(generated/name)
for p in [audit/'cameras.json',audit/'blender-views.json',Path('/tmp/cs-mine-source-closure-inspect-final13.py'),Path('/tmp/cs-mine-timber-source-final13.py'),Path('/tmp/cs-mine-timber-native-final13.cs.txt'),Path('/tmp/cs-mine-timber-native-final13.shader.txt'),Path('/tmp/cs-mine-timber-object-id-final13.shader.txt'),Path('/tmp/cs-mine-fog-split-final13.asmdef.txt'),Path(__file__)]:pins[str(p)]=sha(p)
def unchanged():
 for p,d in pins.items():assert sha(Path(p))==d,p
unchanged();origin=json.loads(Path('/tmp/cs-mine-timber-diagnostics-final13.json').read_text());assert origin['state']=='FailedBoundedDiagnostic' and any(r['step']=='cs-mine-timber-source-final13.py' and r['status']=='Completed' for r in origin['steps'])
allowed_changed={'/tmp/cs-mine-timber-diagnostics-final13.py','/tmp/cs-mine-timber-native-final13.cs.txt'}
for p,digest in origin['pins'].items():
 if p not in allowed_changed:assert pins[p]==digest,p
api=json.loads(Path('/tmp/cs-mine-timber-native-api-final13-r2.json').read_text());assert api['status']=='PassedApiCompileOnly' and api['helperSha256']==pins['/tmp/cs-mine-timber-native-final13.cs.txt']
records=[];result={'sourceReusedFromVerifiedCompletedAttempt':True,'priorAttempt':'/tmp/cs-mine-timber-diagnostics-final13.json','state':'RunningNativeTimberDiagnosticRetry','pins':pins,'steps':records,'overallScore':None};out.write_text(json.dumps(result,indent=2)+'\n')
folder=project/'Assets/CsTimberSplitDiagnostic';owned=False
try:
 inspection=json.loads(Path('/tmp/cs-mine-source-closure-inspect-final13.json').read_text());assert inspection['snapshotSha256']==pins[str(root/'runtime/out/spawn-export-source/combined-runtime-source.blend')] and inspection['helperSha256']==pins['/tmp/cs-mine-source-closure-inspect-final13.py']
 source=Path('/tmp/cs-mine-timber-source-final13');sp=json.loads((source/'provenance.json').read_text());assert sp['sourceSnapshotSha256']==pins[str(root/'runtime/out/spawn-export-source/combined-runtime-source.blend')] and sp['helperSha256']==pins['/tmp/cs-mine-timber-source-final13.py']==origin['pins']['/tmp/cs-mine-timber-source-final13.py']
 source_image=source/'R39_04_SHED_FRONT.exr';assert sha(source_image)==sp['imageSha256'];ch={k:v.pixels[...,:3] for part in OpenEXR.File(str(source_image)).parts for k,v in part.channels.items()};assert all(a.shape==(360,640,3) and np.isfinite(a).all() for a in ch.values());mask=ch['ViewLayer.CsExactTimberMask'][...,0]
 counts={str(i):int((np.abs(mask-i)<1e-5).sum()) for i in [1,2]};assert all(n>100 for n in counts.values()),'Source object mask not effective: '+str(counts);result['sourceMaskCounts']=counts;assert counts==origin['sourceMaskCounts']
 assert not folder.exists() and not (project/'Temp/UnityLockfile').exists();folder.mkdir();owned=True;shutil.copyfile('/tmp/cs-mine-timber-native-final13.cs.txt',folder/'CsMineTimberSplitFinal13.cs');shutil.copyfile('/tmp/cs-mine-timber-native-final13.shader.txt',folder/'CsMineTimberSplitFinal13.shader');shutil.copyfile('/tmp/cs-mine-timber-object-id-final13.shader.txt',folder/'CsMineTimberObjectIdFinal13.shader');assembly=json.loads(Path('/tmp/cs-mine-fog-split-final13.asmdef.txt').read_text());assembly['name']='CriticalShift.Diagnostics.TimberSplitFinal13';(folder/'CriticalShift.Diagnostics.TimberSplitFinal13.asmdef').write_text(json.dumps(assembly,indent=2)+'\n')
 log=audit/'timber-split-final13-r2.native.log';wrapper=audit/'timber-split-final13-r2.wrapper.log';assert not log.exists() and not wrapper.exists()
 args=['xvfb-run','-a','-s','-screen 0 1440x810x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CsMineTimberSplitFinal13.Render','-logFile',str(log)]
 with wrapper.open('x') as f:subprocess.run(args,cwd=root,stdout=f,stderr=subprocess.STDOUT,check=True)
 text=log.read_text(errors='replace');assert text.count('CS_TIMBER_SPLIT_OK')==1 and 'Shader error in' not in text
 native=Path('/tmp/cs-mine-timber-native-final13');modes={'RealtimeDiffuse','BakedAndProbeDiffuse','BaseColor','WorldNormal','ExactObjectMask'};assert {p.name for p in native.iterdir()}=={m+e for m in modes for e in ['.exr','.json']}|{'bindings.json'}
 view=next(v for v in json.loads((audit/'cameras.json').read_text())['views'] if v['name']=='R39_04_SHED_FRONT');room=next(r for r in json.loads((generated/'map-bindings.json').read_text())['rooms'] if r['key']=='mine');assert room['yaw']==0;V=lambda a:np.asarray([a[0],a[2],a[1]])
 for mode in sorted(modes):
  p=native/(mode+'.exr');m=json.loads(p.with_suffix('.json').read_text());assert m['mode']==mode and m['fileSha256']==sha(p) and m['preparedScene']==proof and m['camera']==view['name']
  assert m['sceneFileSha256']==pins[str(generated/'AssembledMap.unity')] and m['pointFileSha256']==pins[str(generated/'mine-point-bake-output.json')]
  assert (m['width'],m['height'],m['msaa'],m['nonfiniteRGBPixels'])==(640,360,1,0) and abs(m['verticalFov']-view['verticalFov'])<1e-4
  pos=np.asarray([m['position'][k] for k in ['x','y','z']]);assert np.max(np.abs(pos-V(room['translation'])-V(view['position'])))<1e-4
  q=m['rotation'];vector=np.asarray([q[k] for k in ['x','y','z']]);w=q['w'];assert abs(np.linalg.norm(np.r_[vector,w])-1)<1e-4
  for axis,key in [(np.asarray([0.,0.,1.]),'forward'),(np.asarray([0.,1.,0.]),'up')]:
   direction=axis+2*np.cross(vector,np.cross(vector,axis)+w*axis);expected=V(view[key]);expected/=np.linalg.norm(expected);assert np.max(np.abs(direction-expected))<1e-4
  pixels=OpenEXR.File(str(p)).channels()['RGBA'].pixels[...,:3];assert pixels.shape==(360,640,3) and np.isfinite(pixels).all();records.append({'step':'Native'+mode,'status':'Completed','fileSha256':sha(p),'metadataSha256':sha(p.with_suffix('.json'))})
 unchanged();result['nativeBindingsSha256']=sha(native/'bindings.json');result['state']='PassedBoundedTechnicalChecksAwaitingIndependentPixelAudit';result['limits']=['Exact Source/native masks require shared-interior audit; no allscene score','BakedAndProbeDiffuse includes baked direct; not SourceIndirect alone','Native targetwood emission suppressed, selected zero-emission assumption must be checked','Unsupported materials/casters kept; NativeMSAA1 versus Source32sample edges excluded','No production/source scene save, full newbake, Player or98 claim'];out.write_text(json.dumps(result,indent=2)+'\n');print(result['state'],flush=True)
except BaseException as e:
 result['state']='FailedBoundedDiagnostic';result['error']=repr(e);result['traceback']=traceback.format_exc();out.write_text(json.dumps(result,indent=2)+'\n');raise
finally:
 if owned and folder.exists():shutil.rmtree(folder);folder.with_suffix('.meta').unlink(missing_ok=True)
