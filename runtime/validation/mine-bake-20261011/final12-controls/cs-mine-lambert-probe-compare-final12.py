from pathlib import Path
import json,hashlib,numpy as np,OpenEXR
from PIL import Image,ImageDraw
source=Path('/tmp/cs-mine-source-stable-board-final12');native=Path('/tmp/cs-mine-source-hybrid-lambert-probe-final12');original=Path('/tmp/cs-mine-source-hybrid-board-final12');out=Path('/tmp/cs-mine-lambert-probe-review-final12');out.mkdir(exist_ok=True)
def layers(path):
 result={part.name():next(iter(part.channels.values())).pixels[...,:3].astype(float) for part in OpenEXR.File(str(path)).parts}
 if any(a.shape!=(360,640,3) or not np.isfinite(a).all() for a in result.values()):raise RuntimeError('Invalid HDR '+str(path))
 return result
def rgb(path):return next(iter(layers(path).values()))
proof=json.loads((source/'provenance.json').read_text())
for name,digest in proof['files'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest,name
s=layers(source/'SourceContextShed-256.exr');old=layers(original/'SourceContextShed.exr');n={name:rgb(native/(name+'.exr')) for name in ['HybridSmallBounds','SpecularSmallBounds','HybridOriginalBounds','SpecularOriginalBounds','LambertDirectOriginalBounds','LambertHybridOriginalBounds']}
mask=(s['ViewLayer.SourceShedBoard'][...,0]>.99)&(rgb(original/'NativeNativeTargetMask.exr')[...,0]>.99);padded=np.pad(mask,2);valid=np.logical_and.reduce([padded[y:y+360,x:x+640] for y in range(5) for x in range(5)]);assert valid.sum()>500
diffuse=(s['ViewLayer.Diffuse Direct']+s['ViewLayer.Diffuse Indirect'])*s['ViewLayer.Diffuse Color'];specular=s['ViewLayer.Combined']-diffuse;oldDiffuse=(old['ViewLayer.Diffuse Direct']+old['ViewLayer.Diffuse Indirect'])*old['ViewLayer.Diffuse Color']
def compare(reference,result):
 a=reference[valid];b=result[valid];den=np.maximum(a.mean(0),1e-9)
 return {'sourceMeanRGB':a.mean(0).tolist(),'nativeMeanRGB':b.mean(0).tolist(),'relativeMeanDifferenceRGB':((b-a).mean(0)/den).tolist(),'relativeMeanAbsoluteErrorRGB':(np.abs(b-a).mean(0)/den).tolist()}
nativeDiffuseOriginal=n['HybridOriginalBounds']-n['SpecularOriginalBounds'];nativeDiffuseLambert=n['LambertHybridOriginalBounds']-n['SpecularOriginalBounds']
normals=s['ViewLayer.SourceBoardShadingNormal']*2-1;normals=normals[...,[0,2,1]];nn=rgb(original/'NativeNativeWorldNormal.exr')*2-1;length=np.linalg.norm(normals,axis=-1);nl=np.linalg.norm(nn,axis=-1);nm=valid&(length>.5)&(nl>.5);angles=np.degrees(np.arccos(np.clip((normals*nn).sum(-1)[nm]/(length[nm]*nl[nm]),-1,1)))
record={'status':'BoundedHighSampleSingleBoardDiagnosticOnly','sourceSamples':256,'pixels':int(valid.sum()),'sourceDiffuseVsOriginalProbeDisney':compare(diffuse,nativeDiffuseOriginal),'sourceDiffuseVsOriginalProbeLambert':compare(diffuse,nativeDiffuseLambert),'sourceResidualSpecularVsSmallBounds':compare(specular,n['SpecularSmallBounds']),'sourceResidualSpecularVsOriginalBounds':compare(specular,n['SpecularOriginalBounds']),'sourceTotalVsLambertOriginalBounds':compare(s['ViewLayer.Combined'],n['LambertHybridOriginalBounds']),'source32VsSource256Diffuse':compare(diffuse,oldDiffuse),'reflectionBoundsDiffuseIsolationMaxAbs':float(np.abs((n['HybridSmallBounds']-n['SpecularSmallBounds'])-nativeDiffuseOriginal)[valid].max()),'normalVsHighSampleSource':{'meanDegrees':float(angles.mean()),'medianDegrees':float(np.median(angles)),'p90Degrees':float(np.percentile(angles,90))},'limits':['one board only','32-sample source atlas fields retained;256-sample camera reference only','SourceResidualSpecular is Combined minus Diffuse on opaque non-emissive board','Historical background is unscored','No actor, wholemap, performance or Player acceptance'],'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source/'provenance.json',source/'SourceContextShed-256.exr',*native.glob('*.exr')]}}
(out/'review.json').write_text(json.dumps(record,indent=2)+'\n')
y,x=np.where(mask);box=(int(x.min())-4,int(y.min())-4,int(x.max())+5,int(y.max())+5);width=(box[2]-box[0])*4;height=(box[3]-box[1])*4;columns=[('Blender256 source',s['ViewLayer.Combined']),('Unity hybrid original probes',n['HybridOriginalBounds']),('Unity Lambert original probes',n['LambertHybridOriginalBounds']),('Source diffuse',diffuse),('Unity Lambert diffuse',nativeDiffuseLambert)];panel=Image.new('RGB',(len(columns)*width,height+60),(24,24,24));draw=ImageDraw.Draw(panel)
for i,(label,array) in enumerate(columns):
 display=np.uint8(np.clip(np.where(array<=.0031308,array*12.92,1.055*np.maximum(array,0)**(1/2.4)-.055),0,1)*255+.5);panel.paste(Image.fromarray(display).crop(box).resize((width,height),Image.Resampling.NEAREST),(i*width,60));draw.text((i*width+4,8),label,fill='white')
draw.text((4,30),'Same camera / one board only / linear RGB shown as sRGB / no full-map acceptance',fill='white');panel.save(out/'comparison.png');print(json.dumps(record,indent=2))
