# Analysis only. Reads immutable native/source HDR and writes numeric statistics, no grading.
from pathlib import Path
import hashlib,json
import numpy as np,OpenEXR
ROOT=Path('/workspace/critical-shift-spawn-runtime');native=Path('/tmp/cs-mine-fog-split-final13');source=Path('/tmp/cs-mine-restored-source-fog-final13');effective_off=ROOT/'runtime/validation/mine-bake-20261011/fresh-export-final11/current-controls/diagnostics/cs-mine-aov-linked-context-final11';out=Path('/tmp/cs-mine-fog-contribution-final13.json');assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
provenance=json.loads((native/'provenance.json').read_text());assert provenance['status']=='PassedBoundedFogSplitOnly'
snapshot=ROOT/'runtime/out/spawn-export-source/combined-runtime-source.blend';source_sha=sha(snapshot)
for folder in [source/'cs-mine-aov-final11',effective_off]:
 p=json.loads((folder/'provenance.json').read_text());assert p['sourceBlenderSha256']==source_sha and p['resolution']==[640,360] and p['samples']==16
 for r in p['files']:
  if r['mode']=='original':assert sha(folder/Path(r['file']).name)==r['sha256']
with_volume=json.loads((source/'cs-mine-aov-final11/provenance.json').read_text());without_volume=json.loads((effective_off/'provenance.json').read_text());assert set(without_volume['diagnosticVolumesDisabledInMemory'])=={'R38 | Tunnel haze','R39 | Shed haze'}
def load(path,combined=False):
 ch=OpenEXR.File(str(path)).channels()
 if combined:
  name=next(k for k in ch if k.endswith('.Combined') and not k.startswith('Cryptomatte'));p=ch[name].pixels[...,:3]
 else:p=ch.get('RGB',ch.get('RGBA')).pixels[...,:3]
 assert p.shape==(360,640,3) and np.isfinite(p).all();return p.astype(np.float64)
def measure(off,on):
 delta=on-off;lum=np.asarray([.2126,.7152,.0722]);delta_luma=delta@lum
 return {'offMeanRGB':off.mean((0,1)).tolist(),'onMeanRGB':on.mean((0,1)).tolist(),'meanRGBChange':delta.mean((0,1)).tolist(),'meanAbsoluteRGBChange':np.abs(delta).mean((0,1)).tolist(),'deltaLumaQuantiles':np.quantile(delta_luma,[.01,.1,.5,.9,.99]).tolist(),'meanLumaChange':float(delta_luma.mean()),'noiseLimit':'Source separate16sample runs include stochastic differences; aggregate diagnostic only'}
records=[]
for name in ['R39_01_PORTAL_APPROACH','R39_02_TUNNEL','R39_04_SHED_FRONT']:
 no=native/(name+'-no-volume.exr');yes=native/(name+'-with-volume.exr');so=effective_off/(name+'-original.exr');sy=source/'cs-mine-aov-final11'/(name+'-original.exr')
 records.append({'camera':name,'native':measure(load(no),load(yes)),'sourceHistorical':measure(load(so,True),load(sy,True)),'inputHashes':{str(p):sha(p) for p in [no,yes,so,sy]}})
result={'status':'MeasuredFogContributionOnly','sourceSnapshotSha256':source_sha,'nativeProvenanceSha256':sha(native/'provenance.json'),'restorationSha256':sha(source/'restoration.json'),'effectiveSourceOffProvenanceSha256':sha(effective_off/'provenance.json'),'rejectedSourceOff':'cs-mine-aov-no-volume-final11 copy/user_remap does not affect indirect libraryusers','helperSha256':sha(Path(__file__)),'views':records,'limits':['Native640MSAA4 versus historicalCycles64016samples; no exact pixel agreement claim','Source cameras use storedauthoring eye/aim/lens; nativeposes verified separately, no newSourcepose metadata','No omittedMixed-cause conclusion, retuning, full fidelity score, gameplay orPlayer pass']};out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
