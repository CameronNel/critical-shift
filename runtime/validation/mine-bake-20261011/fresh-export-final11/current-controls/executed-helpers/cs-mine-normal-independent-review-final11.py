"""Strict normal-AOV comparison only; no heavy process launch or final score."""
from pathlib import Path
import argparse,hashlib,json
import OpenEXR,numpy as np
from PIL import Image,ImageDraw


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def exr(path):
    out={}
    for part in OpenEXR.File(str(path)).parts:
        for key,value in part.channels.items():
            if key in out:raise ValueError('Duplicate EXR channel')
            out[key]=value.pixels.astype(np.float32,copy=False)
    return out

def erode(mask,radius=3):
    out=mask.copy()
    for _ in range(radius):
        p=np.pad(out,1,constant_values=False)
        out=np.logical_and.reduce([p[y:y+mask.shape[0],x:x+mask.shape[1]] for y in range(3) for x in range(3)])
    return out

def stats(a,mask):
    values=a[mask]
    if values.size<100:raise ValueError('Insufficient interior normal evidence')
    return {'pixels':int(values.size),'meanDegrees':float(values.mean()),'medianDegrees':float(np.median(values)),'p90Degrees':float(np.percentile(values,90))}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fresh',type=Path,default=Path('/tmp/cs-mine-normal-fresh-final11'));ap.add_argument('--old',type=Path,default=Path('/tmp/cs-mine-normal-native-final11'));ap.add_argument('--source',type=Path,default=Path('/tmp/cs-mine-aov-linked-context-final11'));ap.add_argument('--support',type=Path,default=Path('/tmp/cs-mine-aov-native-final11'));ap.add_argument('--output',type=Path,default=Path('/tmp/cs-mine-normal-independent-review-final11'));args=ap.parse_args()
    expected=['R39_01_PORTAL_APPROACH','R39_02_TUNNEL','R39_04_SHED_FRONT']
    if sorted(p.name for p in args.fresh.glob('*-ProductionNormal.exr'))!=sorted(n+'-ProductionNormal.exr' for n in expected):raise ValueError('Require exactly three fresh normal views')
    source_proof=json.loads((args.source/'provenance.json').read_text());records={Path(r['file']).name:r['sha256'] for r in source_proof['files']}
    report={'status':'Independent material-normal control only; no final visual acceptance','overallScore':None,'sourceBlenderSha256':source_proof['sourceBlenderSha256'],'views':{},'limits':['Normal-only shaders exclude transport','Native support mask comes from earlier identical canonical geometry; fresh geometry input provenance must be checked','No Player or current native lighting acceptance']}
    args.output.mkdir(exist_ok=True)
    for name in expected:
        source_path=args.source/(name+'-original.exr');old_path=args.old/(name+'-ProductionNormal.exr');fresh_path=args.fresh/(name+'-ProductionNormal.exr');mask_path=args.support/(name+'-SupportedMask.exr')
        if records.get(source_path.name)!=sha(source_path):raise ValueError('Source AOV provenance mismatch')
        s=exr(source_path);old=exr(old_path)['RGBA'][:,:,:3];fresh=exr(fresh_path)['RGBA'][:,:,:3];source=s['ViewLayer.ShadingNormal'][:,:,:3][:,:,[0,2,1]]
        if any(x.shape!=(360,640,3) or not np.isfinite(x).all() for x in [source,old,fresh]):raise ValueError('Invalid/nonfinite matched normal RGB')
        support=exr(mask_path)['RGBA'][:,:,0]>.99;one=s['ViewLayer.DiagnosticOne'][:,:,0]>.99
        normals=[x*2-1 for x in [source,old,fresh]];lengths=[np.linalg.norm(x,axis=2) for x in normals]
        valid=support & one & np.logical_and.reduce([np.isfinite(length)&(length>.8)&(length<1.2) for length in lengths])
        interior=erode(valid)
        normalized=[n/np.maximum(length[:,:,None],1e-6) for n,length in zip(normals,lengths)]
        def angles(a,b):return np.degrees(np.arccos(np.clip((a*b).sum(2),-1,1)))
        old_angle=angles(normalized[0],normalized[1]);fresh_angle=angles(normalized[0],normalized[2]);change=angles(normalized[1],normalized[2])
        length_diagnostics={label:{'median':float(np.median(length[support&one])),'p01':float(np.percentile(length[support&one],1)),'p99':float(np.percentile(length[support&one],99)),'outside08to12Pixels':int(((length<.8)|(length>1.2))[support&one].sum())} for label,length in zip(['source','old','fresh'],lengths)}
        view={'decodedNormalLengthDiagnostics':length_diagnostics,'hashes':{'sourceEXR':sha(source_path),'oldEXR':sha(old_path),'freshEXR':sha(fresh_path),'supportMaskEXR':sha(mask_path)},'oldVsSourceInterior':stats(old_angle,interior),'freshVsSourceInterior':stats(fresh_angle,interior),'freshVsOldInterior':stats(change,interior),'rawRGBNonfinitePixels':0}
        if name=='R39_02_TUNNEL':
            roi=np.zeros_like(valid);roi[70:125,505:610]=True
            # Exact historical ROI uses no erosion for old13-degree comparability.
            same=valid & roi
            view['pipeROI']={'boundsXY':[505,610,70,125],'scope':'Same fixed foreground pipe rectangle as original13deg observation','oldVsSource':stats(old_angle,same),'freshVsSource':stats(fresh_angle,same),'freshVsOld':stats(change,same)}
            pipe_interior=interior & roi
            view['pipeROIEroded']={'oldVsSource':stats(old_angle,pipe_interior),'freshVsSource':stats(fresh_angle,pipe_interior)}
            floor=np.zeros_like(valid);floor[250:,230:440]=True;floor &=interior
            view['centralFloorControl']={'oldVsSource':stats(old_angle,floor),'freshVsSource':stats(fresh_angle,floor)}
        report['views'][name]=view
        panel=Image.new('RGB',(1920,390),(24,24,24));draw=ImageDraw.Draw(panel)
        for x,rgb,label in [(0,source,'Blender source normal'),(640,old,'Old production normal'),(1280,fresh,'Fresh production normal')]:
            show=rgb.copy();show[~interior]=0;panel.paste(Image.fromarray(np.uint8(np.clip(show,0,1)*255)),(x,30));draw.text((x+10,8),label+' - common interior',fill='white')
        panel.save(args.output/(name+'-normal-three-way.png'))
    provenance=args.fresh/'current-input-provenance.json'
    if provenance.exists():report['freshInputProvenance']={'file':str(provenance),'sha256':sha(provenance),'record':json.loads(provenance.read_text())}
    else:report['freshInputProvenance']={'status':'Not present; controlled render input provenance still needs independent confirmation'}
    (args.output/'normal-control-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
