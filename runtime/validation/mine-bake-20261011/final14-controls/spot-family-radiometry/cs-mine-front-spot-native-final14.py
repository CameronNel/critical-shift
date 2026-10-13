# Bounded actual engine spot radiometry. Never opens/saves the main game scene.
from pathlib import Path
import hashlib,json,shutil,subprocess,traceback
import OpenEXR,numpy as np
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';receipt=Path('/tmp/cs-mine-front-spot-native-final14.json');assert not receipt.exists();folder=project/'Assets/CsFrontSpotControlDiagnostic';assert not folder.exists() and not (project/'Temp/UnityLockfile').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();generated=project/'Assets/CriticalShift/Generated/Spawn';pins={str(generated/n):sha(generated/n) for n in ['prepared-scene.json','AssembledMap.unity','map-bindings.json','rig-bindings.json','mine-point-bake-output.json']}
source=Path('/tmp/cs-mine-front-spot-source-control-final14');sp=json.loads((source/'provenance.json').read_text());assert sp['resolution']==[64,64] and sp['samples']==512 and len(sp['frames'])==8
for r in sp['frames']:
 p=source/(r['name']+'.exr');assert sha(p)==r['sha256'];rgb=OpenEXR.File(str(p)).channels()['RGBA'].pixels[...,:3];assert rgb.shape==(64,64,3) and np.isfinite(rgb).all();pins[str(p)]=sha(p)
for p in [source/'provenance.json',Path('/tmp/cs-mine-front-spots-source-final13.json'),Path('/tmp/cs-mine-front-spot-source-control-final14.py'),Path('/tmp/cs-mine-front-spot-control-final14.cs.txt'),Path('/tmp/cs-mine-front-spot-control-final14.cginc.txt'),Path('/tmp/cs-mine-front-spot-control-final14.shader.txt'),Path('/tmp/cs-mine-fog-split-final13.asmdef.txt'),Path(__file__)]:pins[str(p)]=sha(p)
assert sp['helperSha256']==pins['/tmp/cs-mine-front-spot-source-control-final14.py'] and sp['sourceInventorySha256']==pins['/tmp/cs-mine-front-spots-source-final13.json']
api=json.loads(Path('/tmp/cs-mine-front-spot-api-final14-r3.json').read_text());assert api['status']=='PassedApiCompileOnly' and api['helperSha256']==pins['/tmp/cs-mine-front-spot-control-final14.cs.txt']
result={'state':'RunningBoundedNativeSpotControl','pins':pins,'limits':['Numericspotfamily control; neutral-node equivalence independently gated; no full-map shadow certification','No Source/main scene save, Player, full-map fidelity or98 claim']};receipt.write_text(json.dumps(result,indent=2)+'\n');owned=False
try:
 folder.mkdir();owned=True
 for src,dest in [('cs-mine-front-spot-control-final14.cs.txt','CsMineFrontSpotControlFinal14.cs'),('cs-mine-front-spot-control-final14.cginc.txt','SpotControl.cginc'),('cs-mine-front-spot-control-final14.shader.txt','SpotControl.shader')]:shutil.copyfile(Path('/tmp')/src,folder/dest)
 assembly=json.loads(Path('/tmp/cs-mine-fog-split-final13.asmdef.txt').read_text());assembly['name']='CriticalShift.Diagnostics.FrontSpotControlFinal14';(folder/'CriticalShift.Diagnostics.FrontSpotControlFinal14.asmdef').write_text(json.dumps(assembly,indent=2)+'\n')
 log=audit/'front-spot-control-final14.native.log';wrapper=audit/'front-spot-control-final14.wrapper.log';assert not log.exists() and not wrapper.exists()
 args=['xvfb-run','-a','-s','-screen 0 1440x810x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CsMineFrontSpotControlFinal14.Render','-logFile',str(log)]
 with wrapper.open('x') as f:subprocess.run(args,cwd=root,stdout=f,stderr=subprocess.STDOUT,check=True)
 text=log.read_text(errors='replace');assert text.count('CS_ACTUAL_SPOT_CONTROL_OK')==1 and 'Shader error in' not in text
 out=Path('/tmp/cs-mine-front-spot-native-control-final14');expected={r['name']+'-'+mode for r in sp['frames'] for mode in ['realtime-tagged','baked-tagged']}|{'d1-a0-baked-white','d4-a50-baked-white'};assert len(expected)==18 and {p.name for p in out.iterdir()}=={n+e for n in expected for e in ['.exr','.json']}
 frames=[]
 for name in sorted(expected):
  p=out/(name+'.exr');m=json.loads(p.with_suffix('.json').read_text());r=next(r for r in sp['frames'] if name.startswith(r['name']+'-'));assert m['name']==name and m['fileSha256']==sha(p) and m['nonfiniteRGBPixels']==0 and (m['width'],m['height'])==(64,64)
  assert m['range']==32 and m['shadows']=='Soft' and m['cookieKind']==('WhiteRGB' if name.endswith('white') else 'IdentityMarkerRGB') and m['cookieProfile']=='128x128_sourceCosineSmoothstep_linearRGBAHalf' and abs(m['spotBlend']-sp['sourceParameters']['spotBlend'])<1e-5
  if name.startswith('d') and '-baked-' in name:assert ('CS_SPOT_EXTRACTION '+name+' intensity=') in text and ('CS_SPOT_BAKE_CALLBACK_OK '+name+' calls=') in text
  assert abs(m['distance']-r['distance'])<1e-5 and abs(m['angle']-r['angleDegrees'])<1e-5 and abs(m['radius']-sp['sourceParameters']['radius'])<1e-5 and abs(m['power']-sp['sourceParameters']['power'])<1e-4
  assert abs(m['outerAngle']-sp['sourceParameters']['spotSizeRadians']*180/np.pi)<1e-4 and abs(m['innerAngle']-m['outerAngle'])<1e-4
  V=lambda a:np.asarray([a[0],a[2],a[1]],dtype=float);native_vector=lambda v:np.asarray([v[k] for k in ['x','y','z']])
  assert np.max(np.abs(native_vector(m['receiver'])-V(r['receiverPosition'])))<1e-5 and np.max(np.abs(native_vector(m['normal'])-V(r['receiverNormal'])))<1e-5 and np.max(np.abs(native_vector(m['camera'])-V(r['cameraPosition'])))<1e-5
  rgb=OpenEXR.File(str(p)).channels()['RGBA'].pixels[...,:3];assert rgb.shape==(64,64,3) and np.isfinite(rgb).all();centre=rgb[28:36,28:36].astype(float).mean((0,1));
  if 'realtime' in name:assert m['lightmapIndex']==-1 and m['lightmapCount']==0 and m['probeCount']==0
  if r['angleDegrees']==0:assert centre[0]>0.25*(11.686 if r['distance']==1 else 2.953 if r['distance']==2 else .740),name
  frames.append({'name':name,'sha256':sha(p),'metadataSha256':sha(p.with_suffix('.json')),'meanCentreRGB':rgb[28:36,28:36].astype(float).mean((0,1)).tolist()})
 for p,h in pins.items():assert sha(Path(p))==h,p
 result.update(state='PassedBoundedTechnicalChecksAwaitingIndependentRadiometry',frames=frames,command=args,logSha256=sha(log));receipt.write_text(json.dumps(result,indent=2)+'\n');print(result['state'],flush=True)
except BaseException as e:
 result.update(state='FailedBoundedSpotControl',error=repr(e),traceback=traceback.format_exc());receipt.write_text(json.dumps(result,indent=2)+'\n');raise
finally:
 if owned and folder.exists():shutil.rmtree(folder);folder.with_suffix('.meta').unlink(missing_ok=True)
