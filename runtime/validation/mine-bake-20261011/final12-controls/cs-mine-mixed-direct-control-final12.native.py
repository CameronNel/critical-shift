from pathlib import Path
import subprocess,shutil,json,hashlib,numpy as np,OpenEXR
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';output=Path('/tmp/cs-mine-mixed-direct-control-final12');helper=project/'Assets/CriticalShift/Bootstrap/Player/Editor/CsMineMixedDirectControlFinal12.cs'
if helper.exists() or output.exists():raise RuntimeError('Existing mixed-control output/helper')
inputs=[Path('/tmp/cs-mine-mixed-direct-control-final12.cs.txt'),Path(__file__),project/'Assets/CriticalShift/Features/Player/BlenderSurface.shader',project/'Assets/CriticalShift/Features/Player/BlenderPointLighting.cginc']
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
shutil.copy2(inputs[0],helper)
try:
 with (audit/'mixed-direct-control-final12.wrapper.log').open('w') as log:
  subprocess.run(['xvfb-run','-a','-s','-screen 0 640x360x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CsMineMixedDirectControlFinal12.Run','-logFile',str(audit/'mixed-direct-control-final12.native.log')],stdout=log,stderr=subprocess.STDOUT,cwd=root,check=True)
 for p in inputs:
  if hashlib.sha256(p.read_bytes()).hexdigest()!=hashes[str(p)]:raise RuntimeError('Changed control input '+str(p))
 cases=json.loads((output/'cases.json').read_text());assert [c['name'] for c in cases]==['Mixed1','Mixed6Overlap','Baked1'];assert len(list(output.glob('*.exr')))==27;assert all(c['probeCount']==8 and len(c['interpolatedProbeCoefficients'])==27 for c in cases);assert sum(l['channel']<0 for l in cases[1]['lights'])>=2;records=[]
 for case in cases:
  images={}
  for mode in ['realtime-reference','post-bake-on','post-bake-off','actor-zeroSH-on','actor-zeroSH-off','actor-BlendProbes-on','actor-BlendProbes-off','static-moving-blocker','actor-zeroSH-moving-blocker']:
   name=case['name']+'-'+mode+'.exr';file=OpenEXR.File(str(output/name));pixels=next(iter(file.channels().values())).pixels[...,:3]
   if pixels.shape!=(64,64,3):raise RuntimeError('Unexpected HDR shape '+name)
   if not np.isfinite(pixels).all():raise RuntimeError('Nonfinite '+name)
   images[mode]=pixels[24:40,24:40].astype(float)
  reference=images['realtime-reference'].mean((0,1));on=images['post-bake-on'].mean((0,1));off=images['post-bake-off'].mean((0,1))
  expected=100*.18/(4*np.pi*np.pi*4);assert np.min(reference)>.05 and np.max(np.abs(reference-expected))/expected<.1 and np.ptp(reference)<1e-5,('Invalid positive neutral radiometric reference',case['name'],reference,expected)
  error=float(np.max(np.abs(on-reference)/np.maximum(reference,1e-8)))
  record={'case':case,'additionalCentreMeans':{name:image.mean((0,1)).tolist() for name,image in images.items() if name.startswith('actor') or name.endswith('blocker')},'centreRGBRealtime':reference.tolist(),'centreRGBPostBakeOn':on.tolist(),'centreRGBPostBakeOff':off.tolist(),'postBakeOnRelativeErrorVsRealtime':error}
  if case['name'].startswith('Mixed'):
   record['classificationPass']=bool(error<.02 and np.max(np.abs(off))<1e-4 and np.max(np.abs(images['actor-zeroSH-on'].mean((0,1))-reference)/np.maximum(reference,1e-8))<.02 and np.max(np.abs(images['actor-zeroSH-off']))<1e-4 and np.max(np.abs(images['actor-BlendProbes-on'].mean((0,1))-reference)/np.maximum(reference,1e-8))<.02 and np.max(np.abs(images['actor-BlendProbes-off']))<1e-4 and np.max(np.abs(images['static-moving-blocker'].mean((0,1)))/np.maximum(reference,1e-8))<.1 and np.max(np.abs(images['actor-zeroSH-moving-blocker'].mean((0,1)))/np.maximum(reference,1e-8))<.1)
  else:record['classificationPass']=bool(error<.05 and np.max(np.abs(off-on))<1e-4)
  records.append(record)
 proof={'status':'PassedDirectClassificationOnly' if all(r['classificationPass'] for r in records) else 'RejectedDirectClassification','indirectMultiplier':0,'purpose':'Isolate Mixed direct classification including greater-than-four overlapping shadow-mask volumes; no world/bounce or actor acceptance','limits':['source-near-field mismatch unresolved','no current map bake','neutral dynamic receiver mechanism only, no imported actor acceptance','no full63-point performance measurement'],'inputs':hashes,'cases':records,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir() if p.is_file()}}
 (output/'review.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
 if proof['status']!='PassedDirectClassificationOnly':raise RuntimeError('Mixed direct classification failed')
finally:helper.unlink(missing_ok=True);Path(str(helper)+'.meta').unlink(missing_ok=True)
