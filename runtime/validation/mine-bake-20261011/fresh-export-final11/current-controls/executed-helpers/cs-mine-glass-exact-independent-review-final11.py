"""Exact Fresnel + constant background control audit. No heavy process launches.
Expected source/native files: Source-{black,colour}-angle{0,40,65}.exr,
Native-exact-{black,colour}-angle{0,40,65}.exr. Source provenance records
files SHA256s, ior/color/worldLinear and optional backgrounds dict.
"""
from pathlib import Path
import argparse,hashlib,json,math
import OpenEXR,numpy as np

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def rgb(p):
    channels={k:v.pixels for part in OpenEXR.File(str(p)).parts for k,v in part.channels.items()}
    values=[v for k,v in channels.items() if k=='RGBA' or k.endswith('.Combined')]
    if len(values)!=1:raise ValueError('Unexpected raw EXR channels')
    a=values[0][:,:,:3]
    if a.shape!=(128,128,3) or not np.isfinite(a).all():raise ValueError('Invalid/nonfinite glass control')
    return a

def fresnel(angle,ior):
    c=math.cos(math.radians(angle));ct=math.sqrt(max(0,1-(1-c*c)/(ior*ior)))
    return .5*((c-ior*ct)/(c+ior*ct))**2+.5*((ior*c-ct)/(ior*c+ct))**2

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=Path('/tmp/cs-mine-glass-exact-final11'));ap.add_argument('--output',type=Path,default=Path('/tmp/cs-mine-glass-exact-independent-review-final11'));args=ap.parse_args()
    proof=json.loads((args.input/'source-provenance.json').read_text())
    for name,h in proof['files'].items():
        if sha(args.input/name)!=h:raise ValueError('Source provenance mismatch: '+name)
    tint=np.array(proof['color'][:3]);world=np.array(proof['worldLinear']);backgrounds=proof.get('backgrounds',proof.get('backplates',{'black':[0,0,0],'colour':[.04,.2,.3]}))
    result={'status':'Bounded exact-Fresnel/background diagnostic only','overallScore':None,'sourceBlenderSha256':proof['sourceBlenderSha256'],'sourceProvenanceSHA256':sha(args.input/'source-provenance.json'),'interiorXY':[16,112,16,112],'sourceSamples':proof.get('samples'),'angles':{},'limits':['Uniform-world and constant backplate control only','Analytic single-interface composition is a tested benchmark, not assumed actual source BTDF','Refraction/thickness/multiple panes/transparent sorting not certified','Roughness/direct specular/actual portal probe and Player not certified']}
    for angle in [0,40,65]:
        f=fresnel(angle,proof['ior']);a={'exactFresnel':f};means={}
        for back in ['black','colour']:
            row={}
            for mode,name in [('source',f'Source-{back}-angle{angle}.exr'),('native',f'Native-exact-{back}-angle{angle}.exr')]:
                path=args.input/name;values=rgb(path)[16:112,16:112].reshape(-1,3);mean=values.mean(0);means[(back,mode)]=mean
                row[mode]={'meanLinearRGB':mean.tolist(),'spatialStdRGB':values.std(0).tolist(),'sha256':sha(path),'nonfiniteRGBPixels':0}
            src=means[(back,'source')];nat=means[(back,'native')]
            row['nativeToSourceMeanRatioRGB']=(nat/np.maximum(src,1e-12)).tolist();row['relativeMeanErrorRGB']=(np.abs(nat-src)/np.maximum(src,1e-12)).tolist()
            row['thinInterfaceBenchmarkRGB']=(tint*(f*world+(1-f)*np.array(backgrounds[back]))).tolist();a[back]=row
        delta_source=means[('colour','source')]-means[('black','source')];delta_native=means[('colour','native')]-means[('black','native')]
        back=np.array(backgrounds['colour'])-np.array(backgrounds['black'])
        if np.any(back<=0):raise ValueError('Need positive known background contrast in all RGB channels')
        a['measuredBackgroundTransmissionRGB']={'source':(delta_source/back).tolist(),'native':(delta_native/back).tolist(),'thinInterfaceBenchmark':(tint*(1-f)).tolist(),'limit':'Single-interface/refraction radiance convention must be established from actual source measurement'}
        result['angles'][str(angle)]=a
    args.output.mkdir(exist_ok=True);(args.output/'exact-glass-control-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
