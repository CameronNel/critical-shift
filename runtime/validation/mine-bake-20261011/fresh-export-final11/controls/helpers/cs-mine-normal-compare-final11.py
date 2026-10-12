from pathlib import Path
import OpenEXR,numpy as np,json
from PIL import Image,ImageDraw
src=Path('/tmp/cs-mine-aov-linked-context-final11');out=Path('/tmp/cs-mine-normal-native-final11');report={}
def load(p):return {k:v.pixels for part in OpenEXR.File(str(p)).parts for k,v in part.channels.items()}
for p in sorted(out.glob('*-ProductionNormal.exr')):
 name=p.stem.removesuffix('-ProductionNormal');s=load(src/(name+'-original.exr'));n=load(p)['RGBA'][:,:,:3];a=s['ViewLayer.ShadingNormal'][:,:,:3][:,:,[0,2,1]];one=s['ViewLayer.DiagnosticOne'][:,:,0];m=load(Path('/tmp/cs-mine-aov-native-final11')/(name+'-SupportedMask.exr'))['RGBA'][:,:,0]>.99;valid=m&(one>.99)
 sv=a*2-1;nv=n*2-1;sv=sv/np.maximum(np.linalg.norm(sv,axis=2,keepdims=True),1e-6);nv=nv/np.maximum(np.linalg.norm(nv,axis=2,keepdims=True),1e-6);angles=np.degrees(np.arccos(np.clip((sv*nv).sum(axis=2),-1,1)))
 report[name]={'pixels':int(valid.sum()),'angleDegreesMean':float(angles[valid].mean()),'angleDegreesMedian':float(np.median(angles[valid])),'angleDegreesP90':float(np.percentile(angles[valid],90))}
 if 'TUNNEL' in name:
  f=valid.copy();f[:250]=False;f[:, :230]=False;f[:,440:]=False;report[name]['floorCentralAngleMean']=float(angles[f].mean());report[name]['floorSourceNormalMean']=sv[f].mean(axis=0).tolist();report[name]['floorNativeNormalMean']=nv[f].mean(axis=0).tolist()
 image=Image.new('RGB',(1280,390),(24,24,24));image.paste(Image.fromarray(np.uint8(np.clip(a,0,1)*255)),(0,30));image.paste(Image.fromarray(np.uint8(np.clip(n,0,1)*255)),(640,30));draw=ImageDraw.Draw(image);draw.text((10,8),'Blender shading normal - Unity xyz, diagnostic only',fill='white');draw.text((650,8),'Unity production shading normal - diagnostic only',fill='white');image.save(out/(name+'-Normal-comparison.png'))
(out/'normal-comparison-metrics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
