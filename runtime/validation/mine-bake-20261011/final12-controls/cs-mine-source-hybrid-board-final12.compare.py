from pathlib import Path
import json,hashlib,numpy as np,OpenEXR
from PIL import Image,ImageDraw
out=Path('/tmp/cs-mine-source-hybrid-board-final12')
def load(path):
 f=OpenEXR.File(str(path));d={p.name():next(iter(p.channels.values())).pixels[...,:3] for p in f.parts}
 for name,a in d.items():
  if not np.isfinite(a).all():raise RuntimeError('Nonfinite '+str(path)+' '+name)
 return d
source=load(out/'SourceContextShed.exr');native={p.stem:next(iter(load(p).values())) for p in out.glob('Native*.exr')}
mask=source['ViewLayer.SourceShedBoard'][...,0]>.99;nmask=native['NativeNativeTargetMask'][...,0]>.99
both=mask & nmask
for dy in [-1,0,1]:
 for dx in [-1,0,1]:both &= np.roll(np.roll(mask & nmask,dy,0),dx,1)
both[[0,-1]]=False;both[:,[0,-1]]=False
if both.sum()<50:raise RuntimeError('Insufficient shared board interior '+str(both.sum()))
sourceDiffuse=(source['ViewLayer.Diffuse Direct']+source['ViewLayer.Diffuse Indirect'])*source['ViewLayer.Diffuse Color'];sourceTotal=source['ViewLayer.Combined'];sourceBase=source['ViewLayer.SourceBoardBaseColor']
original=load(Path('/tmp/cs-mine-aov-linked-context-final11/R39_04_SHED_FRONT-original.exr'));oldNative=next(iter(load(Path('/tmp/cs-mine-transport-split-final12/Total.exr')).values()))
def metric(a,b):
 return {'aMean':a[both].mean(0).tolist(),'bMean':b[both].mean(0).tolist(),'relativeMeanAbsError':float(np.abs(a[both]-b[both]).mean()/np.maximum(np.abs(b[both]).mean(),1e-8)),'relativeMeanSignedError':float((a[both]-b[both]).mean()/np.maximum(np.abs(b[both]).mean(),1e-8))}
normal=native['NativeNativeWorldNormal']*2-1;sn=original['ViewLayer.ShadingNormal']*2-1;sn=sn[...,[0,2,1]]
# Source AOV worldnormal encoding is documented in the retained original helper.
normal/=np.maximum(np.linalg.norm(normal,axis=-1,keepdims=True),1e-8);sn/=np.maximum(np.linalg.norm(sn,axis=-1,keepdims=True),1e-8)
angles=np.degrees(np.arccos(np.clip(np.sum(normal*sn,axis=-1),-1,1)))
result={'status':'BoundedSingleBoardDiagnosticOnly','sourceMaskPixels':int(mask.sum()),'nativeMaskPixels':int(nmask.sum()),'sharedInteriorPixels':int(both.sum()),'maskIntersectionOverUnion':float((mask&nmask).sum()/(mask|nmask).sum()),'sourceBakeTransferVsRenderedSourceDiffuse':metric(native['NativeSourceDiffuseReference'],sourceDiffuse),'nativeBaseColourVsCopiedSource':metric(native['NativeNativeBaseColor'],sourceBase),'copiedSourceBaseColourVsIntactOriginal':metric(sourceBase,original['ViewLayer.BaseColor']),'hybridVsCopiedSourceTotal':metric(native['NativeHybrid'],sourceTotal),'historicalNativeVsCopiedSourceTotal':metric(oldNative,sourceTotal),'nativeWorldNormalVsIntactSource':{'meanDegrees':float(angles[both].mean()),'medianDegrees':float(np.median(angles[both]))},'closureHybridDirectSpecNonRuntime':metric(native['NativeHybrid'],native['NativeNativeDirectDiffuse']+native['NativeNativeSpecular']+native['NativeSourceNonRuntime']),'limits':['single connected shed board only','native explicit-light runtime cutoffs and realtime SUN penumbra remain','NativeSpecular probe selection can differ due to renderer bounds','fullscene/background uses historical bake and must not be scored','moving shadows actors probes and full-map validation not certified'],'hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file() and p.suffix in ['.exr','.fbx']}}
(out/'bounded-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
y,x=np.where(mask);box=(max(0,int(x.min())-8),max(0,int(y.min())-8),min(640,int(x.max())+9),min(360,int(y.max())+9))
def display(a):
 rgb=np.clip(a,0,1);rgb=np.where(rgb<=.0031308,12.92*rgb,1.055*np.maximum(rgb,0)**(1/2.4)-.055);return Image.fromarray(np.uint8(np.clip(rgb*255+.5,0,255)))
columns=[('Blender source',sourceTotal),('Unity final11',oldNative),('Unity bounded hybrid',native['NativeHybrid']),('Source diffuse only',sourceDiffuse),('Transferred diffuse',native['NativeSourceDiffuseReference'])]
width=(box[2]-box[0])*4;height=(box[3]-box[1])*4;panel=Image.new('RGB',(width*len(columns),height+56),(22,22,22));draw=ImageDraw.Draw(panel)
for i,(label,a) in enumerate(columns):
 panel.paste(display(a).crop(box).resize((width,height),Image.Resampling.NEAREST),(i*width,56));draw.text((i*width+4,10),label,fill='white')
draw.text((4,32),'Same source-camera crop; linear RGB displayed as sRGB; bounded diagnostic, no fullscene acceptance',fill='white');panel.save(out/'bounded-board-comparison.png')
print(json.dumps(result,indent=2))
