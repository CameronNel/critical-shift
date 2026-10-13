from pathlib import Path
import numpy as np,OpenEXR,json
from PIL import Image,ImageDraw
src=Path('/tmp/cs-mine-aov-no-volume-final11');dst=Path('/tmp/cs-mine-aov-native-final11');report={}
def load(p):return {k:v.pixels for part in OpenEXR.File(str(p)).parts for k,v in part.channels.items()}
def rgb(c,key):
 a=c[key];return a[:,:,:3] if a.ndim==3 else np.repeat(a[:,:,None],3,axis=2)
def disp(a):return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055),0,1)*255+.5)
for p in sorted(src.glob('*-original.exr')):
 name=p.stem.removesuffix('-original');s=load(p);base=rgb(s,'ViewLayer.BaseColor');rough=rgb(s,'ViewLayer.Roughness');one=rgb(s,'ViewLayer.DiagnosticOne');n=rgb(load(dst/(name+'-BaseColor.exr')),'RGBA');nr=rgb(load(dst/(name+'-Roughness.exr')),'RGBA');mask=rgb(load(dst/(name+'-SupportedMask.exr')),'RGBA')[:,:,0]>.99
 valid=mask&(one[:,:,0]>.99)&(base.max(axis=2)>.001)
 entry={'validPixels':int(valid.sum()),'oneOnNativeSupportedMean':float(one[mask].mean()),'sourceBaseColorMean':base[valid].mean(axis=0).tolist(),'nativeBaseColorMean':n[valid].mean(axis=0).tolist(),'baseColorMeanAbsoluteError':np.abs(base-n)[valid].mean(axis=0).tolist(),'sourceRoughnessMean':rough[valid].mean(axis=0).tolist(),'nativeRoughnessMean':nr[valid].mean(axis=0).tolist(),'roughnessMeanAbsoluteError':np.abs(rough-nr)[valid].mean(axis=0).tolist()};report[name]=entry
 for mode,a,b in [('BaseColor',base,n),('Roughness',rough,nr)]:
  image=Image.new('RGB',(1280,390),(24,24,24));image.paste(Image.fromarray(disp(a)),(0,30));image.paste(Image.fromarray(disp(b)),(640,30));draw=ImageDraw.Draw(image);draw.text((10,8),'Blender '+mode+' - volume disabled, diagnostic only',fill='white');draw.text((650,8),'Unity '+mode+' - diagnostic only',fill='white');image.save(src/(name+'-'+mode+'-comparison.png'))
(src/'material-comparison-metrics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
