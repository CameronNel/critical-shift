"""NotRun candidate; manually launch only after full13 and strict visual review."""
from pathlib import Path
import subprocess,shutil,json,hashlib
import numpy as np
ROOT=Path('/workspace/critical-shift-spawn-runtime');PROJECT=ROOT/'runtime/unity';AUDIT=ROOT/'runtime/out/mine-bake-audit'
assert json.loads((AUDIT/'full-native-final13-state.json').read_text())['state']=='FinishedTechnicalChecksAwaitingStrictVisualReview'
technical=json.loads((AUDIT/'fresh-technical-receipt-final13.json').read_text())
assert technical['status']=='PassedTechnicalChecksAwaitingIndependentVisualReview'
review=Path('/tmp/cs-mine-strict-visual-review-final13.json')
if not review.exists():raise RuntimeError('Strict current visual review must happen before this diagnostic')
reviewed=json.loads(review.read_text())
folder=PROJECT/'Assets/CsMineFogSplitDiagnostic';log=AUDIT/'fog-split-final13.native.log';output=Path('/tmp/cs-mine-fog-split-final13')
if (PROJECT/'Temp/UnityLockfile').exists() or folder.exists() or log.exists() or output.exists():raise RuntimeError('Editor busy or existing diagnostic needs preservation')
generated=PROJECT/'Assets/CriticalShift/Generated/Spawn'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frozen={name:sha(generated/name) for name in ['prepared-scene.json','map-bindings.json','rig-bindings.json','AssembledMap.unity','mine-point-bake-output.json']}
proof=json.loads((generated/'prepared-scene.json').read_text())
assert reviewed['preparedScene']==technical['mine']['preparedScene']==technical['spawn']['preparedScene']==proof
expected_names={'R39_01_PORTAL_APPROACH','R39_02_TUNNEL','R39_04_SHED_FRONT'}
records=technical['mine']['mineCaptures'];views_review=reviewed['views']
assert len(records)==len(views_review)==3 and {x['name'] for x in records}=={x['camera'] for x in views_review}==expected_names
mine_folder=AUDIT/'unity-source-wood-final13'
for record in records:
    current=next(v for v in views_review if v['camera']==record['name'])
    assert current['nativePngSha256']==record['pngSha256']==sha(mine_folder/(record['name']+'.png'))
    assert current['nativeHdrSha256']==record['hdrSha256']==sha(mine_folder/(record['name']+'-linear.exr'))
    assert current['sourcePngSha256']==sha(AUDIT/'blender'/(record['name']+'.png'))
cameras_path=AUDIT/'cameras.json';cameras_sha=sha(cameras_path)
views=json.loads(cameras_path.read_text())['views']
assert len(views)==3 and {v['name'] for v in views}==expected_names
room=next(r for r in json.loads((generated/'map-bindings.json').read_text())['rooms'] if r['key']=='mine')
assert room['yaw']==0
convert=lambda v:np.asarray([v[0],v[2],v[1]],dtype=float)
helpers={name:sha(Path('/tmp')/name) for name in ['cs-mine-fog-split-final13.cs.txt','cs-mine-fog-split-final13.asmdef.txt','cs-mine-fog-split-final13.py']}
folder.mkdir()
try:
    shutil.copyfile('/tmp/cs-mine-fog-split-final13.cs.txt',folder/'CsMineFogSplitFinal13.cs')
    shutil.copyfile('/tmp/cs-mine-fog-split-final13.asmdef.txt',folder/'CriticalShift.Diagnostics.MineFogSplitFinal13.asmdef')
    args=['xvfb-run','-a','-s','-screen 0 1440x810x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(PROJECT),'-executeMethod','CsMineFogSplitFinal13.Render','-logFile',str(log)]
    with (AUDIT/'fog-split-final13.wrapper.log').open('x') as wrapper:subprocess.run(args,cwd=ROOT,stdout=wrapper,stderr=subprocess.STDOUT,check=True)
    text=log.read_text(errors='replace')
    if text.count('CS_MINE_FOG_SPLIT_DIAGNOSTIC_OK')!=1 or 'Shader error in' in text:raise RuntimeError('Fresh fog split did not complete')
    import OpenEXR
    frames=[];expected={name+'-'+mode+extension for name in ['R39_01_PORTAL_APPROACH','R39_02_TUNNEL','R39_04_SHED_FRONT'] for mode in ['no-volume','with-volume'] for extension in ['.exr','.json']}
    assert {p.name for p in output.iterdir()}==expected
    for path in sorted(output.glob('*.exr')):
        meta=json.loads(path.with_suffix('.json').read_text());assert meta['fileSha256']==sha(path) and meta['sceneFileSha256']==frozen['AssembledMap.unity'] and meta['pointOutputSha256']==frozen['mine-point-bake-output.json']
        view=next(v for v in views if v['name']==meta['camera']);mode=meta['mode']
        assert mode in {'no-volume','with-volume'} and path.name==view['name']+'-'+mode+'.exr'
        assert (meta['width'],meta['height'],meta['msaa'],meta['nonfiniteRGBPixels'])==(640,360,4,0)
        assert meta['preparedScene']==proof and meta['camerasFileSha256']==cameras_sha
        assert abs(meta['verticalFov']-view['verticalFov'])<1e-4
        position=np.asarray([meta['position'][k] for k in ['x','y','z']]);assert np.max(np.abs(position-convert(room['translation'])-convert(view['position'])))<1e-4
        q=meta['rotation'];vector=np.asarray([q[k] for k in ['x','y','z']]);w=q['w'];assert abs(np.linalg.norm(np.r_[vector,w])-1)<1e-4
        for axis,key in [(np.asarray([0.,0.,1.]),'forward'),(np.asarray([0.,1.,0.]),'up')]:
            actual=axis+2*np.cross(vector,np.cross(vector,axis)+w*axis);expected_direction=convert(view[key]);expected_direction/=np.linalg.norm(expected_direction)
            assert np.max(np.abs(actual-expected_direction))<1e-4
        channels=OpenEXR.File(str(path)).channels();pixels=channels.get('RGB',channels.get('RGBA')).pixels[...,:3];assert pixels.shape==(360,640,3) and np.isfinite(pixels).all()
        frames.append({'file':path.name,'sha256':sha(path),'metadataSha256':sha(path.with_suffix('.json')),'finiteRGB':True})
    assert all(sha(generated/name)==digest for name,digest in frozen.items())
    assert sha(cameras_path)==cameras_sha and all(sha(Path('/tmp')/name)==digest for name,digest in helpers.items())
    (output/'provenance.json').write_text(json.dumps({'status':'PassedBoundedFogSplitOnly','helpers':helpers,'preparedInputs':frozen,'camerasFileSha256':cameras_sha,'strictReviewFileSha256':sha(review),'frames':frames,'command':args,'limits':['Six finite actualNative640HDR frames; no Source/scene save','No visual score, Source scattering match, gameplay or Player claim','Current hero1440 images remain separate; Source noVolume16samples has noise and different sampling']},indent=2)+'\n')
finally:
    shutil.rmtree(folder);folder.with_suffix('.meta').unlink(missing_ok=True)
