"""Independent raw glass reflection controls; no Blender/Unity processes."""
from pathlib import Path
import argparse,hashlib,json,math
import OpenEXR,numpy as np

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def rgb(p):
    values={k:v.pixels for part in OpenEXR.File(str(p)).parts for k,v in part.channels.items()}
    choices=[v for k,v in values.items() if k=='RGBA' or k.endswith('.Combined')]
    if len(choices)!=1:raise ValueError('Unexpected glass raw EXR channels: '+str(values.keys()))
    out=choices[0][:,:,:3]
    if out.shape!=(128,128,3) or not np.isfinite(out).all():raise ValueError('Nonfinite or wrong-size glass RGB')
    return out

def smooth_fresnel(angle,ior):
    c=math.cos(math.radians(angle));t=math.sqrt(max(0,1-(1-c*c)/(ior*ior)))
    return .5*((c-ior*t)/(c+ior*t))**2+.5*((ior*c-t)/(ior*c+t))**2

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=Path('/tmp/cs-mine-glass-control-final11'));ap.add_argument('--output',type=Path,default=Path('/tmp/cs-mine-glass-independent-review-final11'));args=ap.parse_args()
    source_proof=json.loads((args.input/'source-provenance.json').read_text())
    if source_proof['anglesDegrees']!=[0,40,65] or source_proof['resolution']!=[128,128]:raise ValueError('Unmatched glass contract')
    for name,h in source_proof['files'].items():
        if sha(args.input/name)!=h:raise ValueError('Source glass provenance hash mismatch')
    out={'status':'Bounded independent reflection control; no production glass or final acceptance','overallScore':None,'sourceBlenderSha256':source_proof['sourceBlenderSha256'],'regionXY':[16,112,16,112],'centralPixels':96*96,'sourceSamples':source_proof['samples'],'sourceProvenanceSHA256':sha(args.input/'source-provenance.json'),'angles':{},'limits':['Uniform-world reflection with black transmitted background only','Premultiplied Standard/Schlick is an approximation','Full BTDF, thickness, coloured background transmission and shadow-ray closure not validated','Actual portal probes, vehicle, Player and final full scene not certified','Source32sample reflection/transmission variance remains; central averaging is not a convergence claim']}
    for angle in [0,40,65]:
        item={};means={}
        for label,name in [('source',f'Source-angle{angle}.exr'),('fade',f'Native-fade-angle{angle}.exr'),('diagnosticPremul',f'Native-premul-diagnostic-angle{angle}.exr')]:
            path=args.input/name;a=rgb(path);v=a[16:112,16:112].reshape(-1,3);mean=v.mean(0);means[label]=mean
            item[label]={'sha256':sha(path),'meanLinearRGB':mean.tolist(),'spatialStdRGB':v.std(0).tolist(),'centralP05RGB':np.percentile(v,5,axis=0).tolist(),'centralP95RGB':np.percentile(v,95,axis=0).tolist(),'nonfiniteRGBPixels':0}
        source=means['source']
        for label in ['fade','diagnosticPremul']:
            item[label]['meanToSourceRatioRGB']=(means[label]/np.maximum(source,1e-12)).tolist()
            item[label]['relativeCentralMeanErrorRGB']=(np.abs(means[label]-source)/np.maximum(source,1e-12)).tolist()
        f=smooth_fresnel(angle,source_proof['ior'])
        item['smoothDielectricBenchmark']={'reflectance':f,'expectedWorldTimesTintRGB':(f*np.array(source_proof['worldLinear'])*np.array(source_proof['color'][:3])).tolist(),'limit':'Analytic zero-roughness benchmark; actual source roughness is not zero'}
        out['angles'][str(angle)]=item
    args.output.mkdir(exist_ok=True);(args.output/'glass-control-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
