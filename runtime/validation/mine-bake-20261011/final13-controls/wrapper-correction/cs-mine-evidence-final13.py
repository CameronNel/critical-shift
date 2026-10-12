"""Parent technical audit; independent visual scoring remains a separate gate."""
from pathlib import Path
import hashlib,json,math,re,xml.etree.ElementTree as ET
import numpy as np
import OpenEXR
from PIL import Image,ImageDraw,ImageFont

ROOT=Path('/workspace/critical-shift-spawn-runtime')
AUDIT=ROOT/'runtime/out/mine-bake-audit'
GENERATED=ROOT/'runtime/unity/Assets/CriticalShift/Generated/Spawn'
MINE_NAMES={'R39_01_PORTAL_APPROACH','R39_02_TUNNEL','R39_04_SHED_FRONT'}
SPAWN_NAMES={'VALIDATE_Spawn','VALIDATE_BriefingDoor','VALIDATE_LockerDoor'}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def record(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def require_absent(*paths):
    occupied=[str(path) for path in paths if path.exists() or path.is_symlink()]
    if occupied:raise RuntimeError('Preserve prior attempt before retry; owned outputs already exist: '+str(occupied))
def validate_proof():
    proof=json.loads((GENERATED/'prepared-scene.json').read_text())
    assert proof['lightmaps']>0
    for key,name in [('mapBindingsSha256','map-bindings.json'),('rigBindingsSha256','rig-bindings.json'),('sceneSha256','AssembledMap.unity')]:
        assert proof[key]==sha(GENERATED/name),name
    digest=hashlib.sha256()
    for directory in ['Assets/CriticalShift/Features/Player','Assets/CriticalShift/Bootstrap/Player']:
        for path in sorted(p for p in (ROOT/'runtime/unity'/directory).rglob('*') if p.suffix in {'.cs','.shader','.cginc'}):digest.update(path.read_bytes())
    assert proof['sourceSha256']==digest.hexdigest(),'Prepared source changed'
    return proof
def validate_points():
    path=GENERATED/'mine-point-bake-output.json';result=json.loads(path.read_text())
    mapping=json.loads((GENERATED/'map-bindings.json').read_text())
    source=next(room for room in mapping['rooms'] if room['key']=='mine')
    expected={light['name'] for light in source['lights'] if light['type']=='POINT'}
    points=result['points'];assert len(points)==len(expected)==63
    assert len({p['name'] for p in points})==63 and {p['name'] for p in points}==expected
    assert result['unityVersion']=='6000.4.3f1'
    assert all(p['isBaked'] and all(math.isfinite(p[k]) and p[k]>=0 for k in ['intensity','radius']) for p in points)
    configured={kind:sum(p['configuredMode']==kind for p in points) for kind in ['Mixed','Baked']}
    actual={kind:sum(p['bakedMode']==kind for p in points) for kind in ['Mixed','Baked']}
    assert configured=={'Mixed':24,'Baked':39} and sum(actual.values())==63
    assert all(result['configured'+kind]==configured[kind] and result['actual'+kind]==actual[kind] for kind in configured)
    return {'fileSha256':sha(path),'configured':configured,'actual':actual,'limits':'Actual output recorded; Baked outputs do not acquire realtime direct illumination by restoring intensity.'}
def validate_spawn():
    folder=AUDIT/'unity-spawn-source-wood-final13'
    assert {p.name for p in folder.iterdir()}=={name+'.png' for name in SPAWN_NAMES}
    proof=validate_proof();records=[]
    for name in sorted(SPAWN_NAMES):
        path=folder/(name+'.png')
        with Image.open(path) as img:assert img.size==(1440,810);img.load()
        records.append({'name':name,'pngSha256':sha(path),'dimensions':[1440,810]})
    result={'status':'Passed','preparedScene':proof,'preparedSceneFileSha256':sha(GENERATED/'prepared-scene.json'),'spawnCaptures':records,'actualPointBakeOutput':validate_points(),'limits':'Fresh complete spawn files only; independent visual regression review pending.'}
    record(AUDIT/'fresh-spawn-receipt-final13.json',result)
    return result
def validate_mine():
    folder=AUDIT/'unity-source-wood-final13';proof=validate_proof()
    assert {p.name for p in folder.iterdir()}=={name+suffix for name in MINE_NAMES for suffix in ['.png','-linear.exr','-linear.json']}
    mapping=json.loads((GENERATED/'map-bindings.json').read_text());room=next(r for r in mapping['rooms'] if r['key']=='mine');assert room['yaw']==0
    convert=lambda v:np.asarray([v[0],v[2],v[1]],dtype=float)
    views=json.loads((AUDIT/'cameras.json').read_text())['views'];assert len(views)==3 and {v['name'] for v in views}==MINE_NAMES
    records=[]
    for view in views:
        name=view['name'];png=folder/(name+'.png');raw=folder/(name+'-linear.exr');metadata=folder/(name+'-linear.json');meta=json.loads(metadata.read_text())
        assert meta['preparedScene']==proof and meta['nonfiniteRGBPixels']==0
        assert (meta['width'],meta['height'],meta['msaa'])==(1440,810,4)
        assert abs(meta['verticalFov']-view['verticalFov'])<1e-4 and abs(meta['nearClip']-.05)<1e-5 and meta['farClip']==250
        assert meta['captureSha256']==sha(raw)
        actual=np.asarray([meta['position'][k] for k in ['x','y','z']]);assert np.max(np.abs(actual-convert(room['translation'])-convert(view['position'])))<1e-4
        q=meta['rotation'];v=np.asarray([q[k] for k in ['x','y','z']]);w=q['w'];assert abs(np.linalg.norm(np.r_[v,w])-1)<1e-4
        def rotate(axis):return axis+2*np.cross(v,np.cross(v,axis)+w*axis)
        for axis,key in [(np.asarray([0.,0.,1.]),'forward'),(np.asarray([0.,1.,0.]),'up')]:
            expected=convert(view[key]);expected/=np.linalg.norm(expected);assert np.max(np.abs(rotate(axis)-expected))<1e-4
        channels=OpenEXR.File(str(raw)).channels();pixels=channels.get('RGB',channels.get('RGBA')).pixels[:,:,:3]
        assert pixels.shape==(810,1440,3) and np.isfinite(pixels).all()
        with Image.open(png) as image:assert image.size==(1440,810);image.load()
        records.append({'name':name,'dimensions':[1440,810],'nonfiniteRGBPixels':0,'pngSha256':sha(png),'hdrSha256':sha(raw),'metadataSha256':sha(metadata),'cameraPoseVerified':True,'meanLinearRGB':[float(x) for x in pixels.mean(axis=(0,1))]})
    result={'status':'Passed','preparedScene':proof,'mineCaptures':records,'limits':'Parent full-resolution HDR/hash/camera audit only; no independent visual fidelity score.'}
    record(AUDIT/'fresh-mine-receipt-final13.json',result)
    return result
def validate_tests():
    path=AUDIT/'native-playmode-source-wood-final13.xml';result=ET.parse(path).getroot();cases=list(result.iter('test-case'));expected=set()
    for source in (ROOT/'runtime/unity/Assets/CriticalShift/Tests/Player').glob('*.cs'):
        for name in re.findall(r'\[(?:UnityTest|Test)\]\s+public\s+(?:void|IEnumerator)\s+(\w+)\(',source.read_text()):expected.add('CriticalShift.Tests.Player.'+source.stem+'.'+name)
    assert len(expected)==len(cases)==18 and {c.attrib['fullname'] for c in cases}==expected
    assert all(c.attrib.get('result')=='Passed' for c in cases) and result.attrib.get('result')=='Passed'
    assert int(result.attrib['total'])==int(result.attrib['passed'])==18 and int(result.attrib['failed'])==int(result.attrib['skipped'])==0
    return {'status':'Passed','exactCaseCount':18,'xmlSha256':sha(path),'run':result.attrib,'cases':sorted(expected)}
def comparisons():
    folder=AUDIT/'comparison-source-wood-final13';require_absent(folder);folder.mkdir()
    reviewed=json.loads(Path('/tmp/cs-mine-strict-visual-review-final11.json').read_text())
    source_hashes={v['camera']:v['sourcePngSha256'] for v in reviewed['views']}
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24);records=[]
    for name in sorted(MINE_NAMES):
        left=AUDIT/'blender'/(name+'.png');right=AUDIT/'unity-source-wood-final13'/(name+'.png')
        assert sha(left)==source_hashes[name],'Source reference changed'
        with Image.open(left) as a,Image.open(right) as b:
            assert a.size==b.size==(1440,810);width,height=a.size
            panel=Image.new('RGB',(width*2,height+50),(24,24,24));draw=ImageDraw.Draw(panel)
            draw.text((20,12),'Blender source',font=font,fill='white');draw.text((width+20,12),'Unity — fresh final13 native lighting',font=font,fill='white')
            panel.paste(a.convert('RGB'),(0,50));panel.paste(b.convert('RGB'),(width,50));destination=folder/(name+'.png');panel.save(destination)
        records.append({'name':name,'sourceSha256':sha(left),'nativeSha256':sha(right),'panelSha256':sha(destination),'panel':str(destination)})
    record(AUDIT/'comparisons-source-wood-final13.json',{'images':records,'manipulation':'Labels/layout only; source/native images neither resized nor colour/exposure/content altered','acceptance':'Independent visual review pending'})
def complete():
    spawn=validate_spawn();mine=validate_mine();tests=validate_tests();comparisons()
    result={'status':'PassedTechnicalChecksAwaitingIndependentVisualReview','spawn':spawn,'mine':mine,'tests':tests,'overallScore':None,'player':'NotRun','limits':'No visual score, Player pass, target-hardware performance or 98% claim.'}
    record(AUDIT/'fresh-technical-receipt-final13.json',result)
    return result
