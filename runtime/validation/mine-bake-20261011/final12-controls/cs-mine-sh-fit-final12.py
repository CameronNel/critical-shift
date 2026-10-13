from pathlib import Path
import json,hashlib,numpy as np,OpenEXR
probe=Path('/tmp/cs-mine-source-probe-field-final12');basis=Path('/tmp/cs-mine-sh-basis-measured-final12');output=Path('/tmp/cs-mine-sh-fit-final12');output.mkdir(exist_ok=True)
def rgb(name):
 file=OpenEXR.File(str(probe/name));a=next(iter(file.channels().values())).pixels[...,:3]
 if a.shape!=(32,64,3):raise RuntimeError('Unexpected probe EXR shape '+name+': '+str(a.shape))
 if not np.isfinite(a).all():raise RuntimeError('Nonfinite '+name)
 return a
p=json.loads((probe/'provenance.json').read_text());b=json.loads((basis/'basis.json').read_text());assert b['status']=='PassedBasisControlOnly'
for name,digest in p['files'].items():assert hashlib.sha256((probe/name).read_bytes()).hexdigest()==digest
field=rgb('SourceProbeAllIndirect.exr')+rgb('SourceProbeNonExplicitDirect.exr');normals=rgb('SourceProbeActualWorldNormals.exr')*2-1;coverage=rgb('SourceProbeValidTexels.exr')[...,0]>.99;length=np.linalg.norm(normals,axis=-1);valid=coverage&(length>.85)&(length<1.15);assert valid.sum()>1800
normals=normals/np.maximum(length[...,None],1e-8);directions=normals[...,[0,2,1]]
def polynomial(n):
 x,y,z=n.T;return np.array([np.ones(len(x)),x,y,z,x*y,x*z,y*z,x*x-y*y,3*z*z-1]).T
measured=np.array([[r['direction'][key] for key in ['x','y','z']] for r in b['rows']]);actual=np.array([r['cpuOffsetBasis'] for r in b['rows']]);assert measured.shape==(26,3) and actual.shape==(26,9) and np.isfinite(measured).all() and np.isfinite(actual).all()
assert np.max(np.abs(np.linalg.norm(measured,axis=1)-1))<1e-5 and np.linalg.matrix_rank(polynomial(measured))==9
calibration=np.linalg.lstsq(polynomial(measured),actual,rcond=None)[0];basisResidual=polynomial(measured)@calibration-actual;assert np.abs(basisResidual).max()<.001
nativeBasis=polynomial(directions[valid])@calibration
# Actual image stores outgoing Lambert E/pi. Fit it directly; neither additional
# /pi nor a second clamped-cosine convolution belongs here. Lat-long UV texels
# carry sin(theta) quadrature weights, using measured source normal elevation.
weights=np.sqrt(np.maximum(1-normals[valid,2]**2,1e-8));target=field[valid];weighted=nativeBasis*np.sqrt(weights[:,None]);assert np.linalg.matrix_rank(weighted)==9 and np.isfinite(weighted).all()
coeff=np.linalg.lstsq(weighted,target*np.sqrt(weights[:,None]),rcond=None)[0];assert np.isfinite(coeff).all();fit=nativeBasis@coeff;clipped=np.maximum(fit,0);difference=fit-target
rms=np.sqrt(np.sum(weights[:,None]*difference**2,axis=0)/weights.sum());mean=np.sum(weights[:,None]*target,axis=0)/weights.sum()
train=np.arange(len(target))%2==0;assert np.linalg.matrix_rank(weighted[train])==9 and np.isfinite(np.linalg.cond(weighted)) and np.isfinite(np.linalg.cond(polynomial(measured)));heldCoeffs=np.linalg.lstsq(weighted[train],target[train]*np.sqrt(weights[train,None]),rcond=None)[0];assert np.isfinite(heldCoeffs).all();held=(nativeBasis@heldCoeffs)[~train]-target[~train];assert np.isfinite(held).all()
record={'status':'BoundedL2FitOnly','quantity':'White Lambert outgoing E/pi fitted to actual signedUnityCPUbasis verifiedagainstactualsourceShaderGPU','sourceProbeWorldBlenderXYZ':p['worldCentreBlenderXYZ'],'validTexels':int(valid.sum()),'coefficientsRGBByNativeIndex':coeff.T.tolist(),'quadrature':'Lat-long sin(theta) from measured sourceWorldnormal elevation, not equalUVtexelweights','extraPiConversion':False,'extraCosineConvolution':False,'basisCalibrationConditionNumber':float(np.linalg.cond(polynomial(measured))),'weightedFieldFitConditionNumber':float(np.linalg.cond(weighted)),'weightedClampedRmsRGB':np.sqrt(np.sum(weights[:,None]*(clipped-target)**2,axis=0)/weights.sum()).tolist(),'weightedNegativeFractionRGB':(np.sum(weights[:,None]*(fit<0),axis=0)/weights.sum()).tolist(),'basisCalibrationMaxResidual':float(np.abs(basisResidual).max()),'weightedFieldMeanRGB':mean.tolist(),'weightedRmsRGB':rms.tolist(),'relativeWeightedRmsRGB':(rms/np.maximum(mean,1e-8)).tolist(),'signedFitNegativeFractionRGB':(fit<0).mean(0).tolist(),'clampedFitMeanAbsErrorRGB':np.abs(clipped-target).mean(0).tolist(),'heldoutEveryOtherTexelMeanAbsErrorRGB':np.abs(held).mean(0).tolist(),'limits':['onevirtualpoint','alternatetexelholdout isnearby angularinterpolation, notindependent MonteCarlovalidation','L2truncation and sourceMonteCarlovariance aremeasured, notexactSourceprobeclaim','actualneutralSource/nativeGPUreceiver at fittedfield notyettested','othernativeSH/ambient mustbereplaced, notadded','nofull216probes, actor ormapacceptance'],'inputs':{str(probe/'provenance.json'):hashlib.sha256((probe/'provenance.json').read_bytes()).hexdigest(),str(basis/'basis.json'):hashlib.sha256((basis/'basis.json').read_bytes()).hexdigest()}}
(output/'fit.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
