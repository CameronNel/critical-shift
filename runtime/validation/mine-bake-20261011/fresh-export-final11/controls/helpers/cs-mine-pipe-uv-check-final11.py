from pathlib import Path
import numpy as np,OpenEXR,json
from PIL import Image
root=Path('/workspace/critical-shift-spawn-runtime');p=Path('/tmp/cs-mine-normal-uv-native-final11');r={}
def load(p):return next(iter(OpenEXR.File(str(p)).channels().values())).pixels
uv=load(p/'R39_02_TUNNEL-NormalAtlasUV.exr')[70:125,505:610];sample=load(p/'R39_02_TUNNEL-NormalAtlasSample.exr')[70:125,505:610]
m=json.loads((root/'runtime/unity/Assets/CriticalShift/Generated/Spawn/map-bindings.json').read_text());pkg=next(x for x in m['materials'] if x['room']=='mine');definition=next(d for d in pkg['definitions'] if d['source']=='R39 | Riveted duct iron');record=pkg['atlases'][definition['atlas']]['normal'];im=np.asarray(Image.open(root/'runtime/unity/Assets/CriticalShift/Generated/Spawn'/record['file']).convert('RGB'),dtype=np.float32)/255;h,w=im.shape[:2]
x=np.clip((uv[:,:,0]*w).astype(int),0,w-1);y=np.clip(((1-uv[:,:,1])*h).astype(int),0,h-1);raw=im[y,x];valid=uv[:,:,3]>.99
r={'sourceNormal':record,'pipeSourceDefinition':definition['key'],'validPipePixels':int(valid.sum()),'normalAtlasMipPercentiles':np.percentile(uv[:,:,2][valid],[0,50,90,100]).tolist(),'rawSourceNegativeTangentZPixels':int((raw[:,:,2][valid]<.499).sum()),'rawSourceTangentZEncodedMean':float(raw[:,:,2][valid].mean()),'sourceEncodedRGBMean':raw[valid].mean(axis=0).tolist(),'nativeGpuSampleRGBMean':sample[:,:,:3][valid].mean(axis=0).tolist(),'sourceVsNativeRGNearestMAE':np.abs(raw[:,:,:2]-sample[:,:,:2])[valid].mean(axis=0).tolist()};print(json.dumps(r,indent=2));(p/'pipe-atlas-audit.json').write_text(json.dumps(r,indent=2)+'\n')
for directory in ['cs-mine-sun-caster-native-final11']:
 sun={}
 for file in sorted((Path('/tmp')/directory).glob('*.exr')):
  a=load(file);sun[file.stem]={'centre':a[60:68,60:68,:3].mean(axis=(0,1)).tolist(),'nonfinite':int((~np.isfinite(a[:,:,:3])).sum())}
 print(json.dumps(sun,indent=2));(Path('/tmp')/directory/'measurements.json').write_text(json.dumps(sun,indent=2)+'\n')
