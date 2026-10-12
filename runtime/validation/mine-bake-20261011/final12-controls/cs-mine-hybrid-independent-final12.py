from pathlib import Path
import json,hashlib,numpy as np,OpenEXR
from PIL import Image,ImageDraw
root=Path('/tmp/cs-mine-source-hybrid-board-final12');out=Path('/tmp/cs-mine-hybrid-independent-final12');out.mkdir(exist_ok=True)
def load(p):return {k:v.pixels for part in OpenEXR.File(str(p)).parts for k,v in part.channels.items()}
def rgb(p):
 c=load(p);return next(iter(c.values()))[:,:,:3].astype(np.float64)
def erosion(m,n=2):
 p=np.pad(m,n);return np.logical_and.reduce([p[y:y+360,x:x+640] for y in range(2*n+1) for x in range(2*n+1)])
proof=json.loads((root/'provenance.json').read_text());nativeproof=json.loads((root/'native-hybrid-proof.json').read_text())
for name,h in proof['files'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==h,name
s=load(root/'SourceContextShed.exr');mask=s['ViewLayer.SourceShedBoard'][:,:,:3].min(axis=2)>.99
names={'hybrid':'NativeHybrid','direct':'NativeNativeDirectDiffuse','spec':'NativeNativeSpecular','nonruntime':'NativeSourceNonRuntime','reference':'NativeSourceDiffuseReference','normal':'NativeNativeWorldNormal','base':'NativeNativeBaseColor','mask':'NativeNativeTargetMask'}
a={k:rgb(root/(v+'.exr')) for k,v in names.items()}
assert all(x.shape==(360,640,3) and np.isfinite(x).all() for x in a.values())
nativemask=a['mask'].min(axis=2)>.99;valid=erosion(mask&nativemask);assert valid.sum()>500
c=s['ViewLayer.Diffuse Color'][:,:,:3];direct=s['ViewLayer.Diffuse Direct'][:,:,:3]*c;indirect=s['ViewLayer.Diffuse Indirect'][:,:,:3]*c;total=direct+indirect
base=s['ViewLayer.SourceBoardBaseColor'][:,:,:3]
def comparison(source,native):
 e=(native-source)[valid];den=np.maximum(np.mean(source[valid],axis=0),1e-9)
 return {'sourceMean':source[valid].mean(axis=0).tolist(),'nativeMean':native[valid].mean(axis=0).tolist(),'meanAbsoluteError':np.abs(e).mean(axis=0).tolist(),'relativeMeanDifference':(e.mean(axis=0)/den).tolist(),'relativeMeanAbsoluteError':(np.abs(e).mean(axis=0)/den).tolist()}
def display(a):return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055),0,1)*255+.5)
report={'status':'Bounded diagnostic measurements; no production/98 acceptance','sourceProof':proof,'nativeProof':nativeproof,'sourceMaskPixels':int(mask.sum()),'nativeMaskPixels':int(nativemask.sum()),'maskIntersectionPixels':int((mask&nativemask).sum()),'maskXorPixels':int((mask^nativemask).sum()),'erodedInteriorPixels':int(valid.sum()),'sourceDiffuseReferenceTransfer':comparison(total,a['reference']),'hybridDiffuseAgainstSourceTotal':comparison(total,a['hybrid']-a['spec']),'baseColourAgainstSourceContext':comparison(base,a['base']),'nativeExplicitDirectAgainstTransferredSourceExplicitDirect':comparison(a['reference']-a['nonruntime'],a['direct']),'sourceDiffuseDirectMean':direct[valid].mean(axis=0).tolist(),'sourceDiffuseIndirectMean':indirect[valid].mean(axis=0).tolist(),'nativeTerms':{k:x[valid].mean(axis=0).tolist() for k,x in a.items() if k!='mask'},'hybridClosureMaxAbs':float(np.abs(a['hybrid']-a['direct']-a['spec']-a['nonruntime'])[valid].max()),'limits':['Only one38face board, no-volume camera.','Native explicit sources restricted to current12m POINT range; source radiance has no equivalent range.','Native/non-explicit source diffuse fields are colour-included.','Diffuse direct/reference comparison does not validate native specular, actor/probe matching, dynamic soft shadows, wholemap or Player.']}
original=load('/tmp/cs-mine-aov-linked-context-final11/R39_04_SHED_FRONT-original.exr');sn=original['ViewLayer.ShadingNormal'][:,:,:3].astype(float)*2-1;sn=sn[:,:,[0,2,1]];nn=a['normal']*2-1
sl=np.linalg.norm(sn,axis=2);nl=np.linalg.norm(nn,axis=2);normalvalid=valid&(sl>.5)&(nl>.5);dot=np.sum(sn*nn,axis=2)/np.maximum(sl*nl,1e-9);angles=np.degrees(np.arccos(np.clip(dot[normalvalid],-1,1)));report['normalVsIntactSource']={'pixels':len(angles),'meanDegrees':float(angles.mean()),'medianDegrees':float(np.median(angles)),'p90Degrees':float(np.percentile(angles,90))}
report['nativeFileHashes']={v+'.exr':hashlib.sha256((root/(v+'.exr')).read_bytes()).hexdigest() for v in names.values()}
for name,left,right in [('diffuse-reference',total,a['reference']),('hybrid-diffuse',total,a['hybrid']-a['spec']),('base',base,a['base'])]:
 canvas=Image.new('RGB',(1280,390),(24,24,24));canvas.paste(Image.fromarray(display(np.where(valid[:,:,None],left,0))),(0,30));canvas.paste(Image.fromarray(display(np.where(valid[:,:,None],right,0))),(640,30));draw=ImageDraw.Draw(canvas);draw.text((8,8),'Source exact board interior '+name,fill='white');draw.text((648,8),'Native diagnostic '+name,fill='white');canvas.save(out/(name+'.png'))
(out/'review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['sourceProof','nativeProof','nativeFileHashes']},indent=2))
