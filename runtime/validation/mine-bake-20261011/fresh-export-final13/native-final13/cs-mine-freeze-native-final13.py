from pathlib import Path
import hashlib,json,shutil,subprocess
root=Path('/workspace/critical-shift-spawn-runtime');audit=root/'runtime/out/mine-bake-audit';dest=root/'runtime/validation/mine-bake-20261011/fresh-export-final13/native-final13'
assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tech=json.loads((audit/'fresh-technical-receipt-final13.json').read_text());review=json.loads(Path('/tmp/cs-mine-strict-visual-review-final13.json').read_text())
assert tech['status']=='PassedTechnicalChecksAwaitingIndependentVisualReview' and review['status']=='Rejected' and review['visualSubtotal']==41
assert review['preparedScene']==tech['mine']['preparedScene']==tech['spawn']['preparedScene']
files={}
for name in ['full-native-final13-state.json','native-launch-recipe-final13.json','native-bake-source-wood-final13.log','native-bake-source-wood-final13-wrapper.log','after-bake-source-wood-final13-wrapper.log','native-mine-render-source-wood-final13.log','native-playmode-source-wood-final13.log','native-playmode-source-wood-final13.xml','fresh-spawn-receipt-final13.json','fresh-mine-receipt-final13.json','fresh-technical-receipt-final13.json','comparisons-source-wood-final13.json','native-resource-final13-retry.jsonl','cameras.json']:
    files[name]=audit/name
for folder in ['unity-source-wood-final13','unity-spawn-source-wood-final13','comparison-source-wood-final13']:
    for p in (audit/folder).iterdir():
        assert p.is_file();files[folder+'/'+p.name]=p
for name in ['cs-mine-strict-visual-review-final13.json','cs-mine-hdr-technical-independent-final13.json','cs-mine-spawn-independent-review-final13.json']:
    files[name]=Path('/tmp')/name
for name in ['prepared-scene.json','mine-point-bake-output.json']:
    files[name]=root/'runtime/unity/Assets/CriticalShift/Generated/Spawn'/name
for p in audit.glob('mine-*-density.json'):files[p.name]=p
files['cs-mine-freeze-native-final13.py']=Path('/tmp/cs-mine-freeze-native-final13.py')
for v in review['views']:
    assert sha(audit/'blender'/(v['camera']+'.png'))==v['sourcePngSha256']
    assert sha(audit/'unity-source-wood-final13'/(v['camera']+'.png'))==v['nativePngSha256']
    assert sha(audit/'unity-source-wood-final13'/(v['camera']+'-linear.exr'))==v['nativeHdrSha256']
assert sha(files['prepared-scene.json'])==review['preparedSceneFileSha256']
assert sha(files['native-playmode-source-wood-final13.xml'])==tech['tests']['xmlSha256']
records=[]
for relative,p in sorted(files.items()):
    assert p.is_file();target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
    assert sha(p)==sha(target);records.append({'file':relative,'bytes':target.stat().st_size,'sha256':sha(target)})
receipt={'status':'TechnicalPassedVisualRejected41of60','productionCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'visualSubtotal':41,'visualMaximum':60,'overallScore':None,'preparedScene':review['preparedScene'],'sourceReferences':[{'file':v['camera']+'.png','sha256':v['sourcePngSha256']} for v in review['views']],'files':records,'limits':['All three untouched comparison panels and full-resolution finite HDR preserved','Three spawn views independently cleared and exact18 gameplay cases passed123.2007777 seconds','Actual63points5Mixed58Baked; no freshPlayer or target-hardware performance pass','SourcePNG images referenced by exact hashes; existing canonical validation refs retained','Initial exit137 preserved separately; no98 acceptance or assembly edits']}
(dest/'provenance.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert all(sha(dest/r['file'])==r['sha256'] for r in records)
print(json.dumps({'files':len(records),'bytes':sum(r['bytes'] for r in records),'status':receipt['status'],'folder':str(dest)},indent=2))
