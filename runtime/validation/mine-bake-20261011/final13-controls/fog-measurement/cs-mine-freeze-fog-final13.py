from pathlib import Path
import shutil,hashlib,json
import OpenEXR,numpy as np
root=Path('/workspace/critical-shift-spawn-runtime');dest=root/'runtime/validation/mine-bake-20261011/final13-controls/fog-measurement';assert not dest.exists();dest.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();records=[]
def copy(p,relative):
 target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);assert sha(p)==sha(target);records.append({'file':relative,'bytes':target.stat().st_size,'sha256':sha(target)})
for p in Path('/tmp/cs-mine-fog-split-final13').iterdir():copy(p,'native/'+p.name)
for name in ['cs-mine-fog-contribution-final13.json','cs-mine-fog-independent-review-final13.json','cs-mine-volume-equation-independent-final13.json','cs-mine-source-fog-toggle-rejection-independent-final13.json','cs-mine-source-native-fog-independent-final13.json','cs-mine-source-closure-inspect-final13.json','cs-mine-source-closure-inspect-final13-preservation.json','cs-mine-measure-fog-split-final13.py','cs-mine-source-closure-inspect-final13.py','cs-mine-run-closure-inspect-final13.py','cs-mine-freeze-fog-final13.py']:
 copy(Path('/tmp')/name,name)
for name in ['fog-split-final13.native.log','fog-split-final13.wrapper.log','cs-mine-source-closure-inspect-final13.log','native-frame-relocation-final13.json']:copy(root/'runtime/out/mine-bake-audit'/name,name)
source_on=Path('/tmp/cs-mine-restored-source-fog-final13/cs-mine-aov-final11');source_off=root/'runtime/validation/mine-bake-20261011/fresh-export-final11/current-controls/diagnostics/cs-mine-aov-linked-context-final11';references=[]
for mode,folder in [('with-volume',source_on),('no-volume',source_off)]:
 metadata=json.loads((folder/'provenance.json').read_text());copy(folder/'provenance.json','source/'+mode+'-historical-provenance.json')
 for r in metadata['files']:
  if r['mode']!='original':continue
  original=folder/Path(r['file']).name;assert sha(original)==r['sha256'];pixels=OpenEXR.File(str(original)).channels()['ViewLayer.Combined'].pixels[...,:3];assert pixels.shape==(360,640,3) and np.isfinite(pixels).all()
  target=dest/'source'/(r['view']+'-'+mode+'.exr');OpenEXR.File({'compression':OpenEXR.ZIP_COMPRESSION,'type':OpenEXR.scanlineimage},{'RGB':pixels.copy()}).write(str(target));reread=OpenEXR.File(str(target)).channels()['RGB'].pixels;assert np.array_equal(pixels,reread) and pixels.dtype==reread.dtype
  records.append({'file':str(target.relative_to(dest)),'bytes':target.stat().st_size,'sha256':sha(target)});references.append({'file':str(target.relative_to(dest)),'originalFullMultilayerSha256':r['sha256'],'exactCombinedRGBPixelPreservation':True,'samples':metadata['samples'],'sourceSnapshotSha256':metadata['sourceBlenderSha256']})
receipt={'status':'BoundedFogMeasurementCompleteVisualStillRejected41of60','files':records,'sourceCombinedExtraction':references,'overallScore':None,'limits':['Native6 actualfinite640HDR unchanged; Source6 CombinedRGB losslessfloat extracts, no image correction','Source oldcopy/user_remap off state explicitly rejected; effective off mutates actual linkednodes','Same source snapshot; Source16samples versus NativeMSAA4; neither pairedmeanratio nor no-volume baseline is a physical lightscale','Fog doesnotfix pale exterior timber; mixed-direct/medium scattering gap not established as sole cause','Source closures/bounds/visibility inspected; no density/color/pi retune, production/source save, new Player or score']}
(dest/'provenance.json').write_text(json.dumps(receipt,indent=2)+'\n');assert all(sha(dest/r['file'])==r['sha256'] for r in records);print(json.dumps({'files':len(records),'bytes':sum(r['bytes'] for r in records),'status':receipt['status']},indent=2))
