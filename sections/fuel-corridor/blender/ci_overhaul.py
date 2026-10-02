"""Run the owned Blender review on a disposable GitHub runner when cloud execution is unavailable.

Only the task branch is publishable. A passing cold check and completed render
manifests are required before the generated native scene advances.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, shutil, subprocess, sys, urllib.request

ROOT=Path(__file__).resolve().parents[3]
TASK=ROOT/'sections/fuel-corridor'
SOURCE=ROOT/'sections/facility-assembly/sources/fuel-corridor/module.blend'
BRANCH='codex/fuel-corridor-overhaul-20261001'
BASE='75983b95efb99536b1cda1a5533d9b265a4c581f'
CONTROL=json.loads((TASK/'production/CI_RUN.json').read_text())
CYCLE=CONTROL['cycle']
assert re.fullmatch(r'[A-Za-z0-9_-]{1,24}',CYCLE)
LOGS=TASK/'production/ci'/CYCLE
CHECK=TASK/'production/checkpoints'
NATIVE=CHECK/('fuel_full_'+CYCLE+'.blend')
MANIFEST=CHECK/(CYCLE+'_BUILD_MANIFEST.json')
COLD=CHECK/(CYCLE+'_COLD_VALIDATION.json')
FULL=TASK/'production/renders/review'/('full-'+CYCLE)
CLOSED=TASK/'production/renders/review'/('closed-'+CYCLE)
CAMERAS='C01_ENTRY,C02_PRIMARY_ROUTE,C03_HERO,C04_REVERSE,C05_EAST_TURN,C06_REACTOR_THRESHOLD,C07_BYPASS,C08_SERVICE_JUNCTION,C09_MATERIALS,C10_PLANT_HEADER,D01_CARRIER_OPERATION,D02_WORKBENCH,D03_UTILITY,D04_REACTOR_WIDE,D05_GATE_MECHANISM,D06_SERVICE_RECESS,E01_WASTE_APPROACH,E02_CLEAN_APPROACH,E03_FREIGHT_LEAF'
# Six workers reduce review latency without changing pixels, samples or coverage.
# The last worker also renders the closed freight diagnostic.
CAMERA_GROUPS=[CAMERAS.split(',')[a:c] for a,c in [(0,4),(4,7),(7,10),(10,13),(13,16),(16,19)]]
DETAIL_CAMERAS=['P01_BENCH_POWER','P02_PROCESS_JUNCTION','P03_REACTOR_INTERCOM','P04_FLOOR_STRAINER']

def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args]).decode().strip()

def run(name,args,env=None):
    LOGS.mkdir(parents=True,exist_ok=True)
    path=LOGS/(name+'.log')
    print('FUEL_CI_START',name,flush=True)
    with path.open('w') as out:
        result=subprocess.run(args,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,env=env)
    print('\n'.join(path.read_text(errors='replace').splitlines()[-14:]),flush=True)
    if result.returncode:raise RuntimeError(name+' failed: '+str(result.returncode))
    print('FUEL_CI_PASS',name,flush=True)

def prepare():
    # Compile without importing bpy so source errors fail before installing Blender.
    for path in (TASK/'blender').glob('*.py'):compile(path.read_text(),str(path),'exec')
    selected=ROOT/'sections/facility-assembly/sources/spawn-room/module.blend'
    with selected.open('rb') as f:header=f.read(128)
    if header.startswith(b'version https://git-lfs.github.com/spec/v1'):
        pointer=selected.read_text()
        oid=re.search(r'oid sha256:([a-f0-9]{64})',pointer).group(1)
        size=int(re.search(r'size (\d+)',pointer).group(1))
        url='https://media.githubusercontent.com/media/CameronNel/critical-shift/'+BASE+'/'+str(selected.relative_to(ROOT))
        with urllib.request.urlopen(url,timeout=180) as response:data=response.read()
        assert len(data)==size and hashlib.sha256(data).hexdigest()==oid,'LFS source verification failed'
        selected.write_bytes(data)
    if os.environ.get('GITHUB_ENV'):
        with open(os.environ['GITHUB_ENV'],'a') as out:out.write('FUEL_CYCLE='+CYCLE+'\n')
    print('FUEL_CI_PREPARED',CYCLE,sys.version,flush=True)

def export_pixel_bytes():
    """Expose large repository renders as exact-byte text chunks for connector review."""
    import base64
    destination=LOGS/'pixel_bytes'
    destination.mkdir(parents=True,exist_ok=True)
    records=[]
    images=list((TASK/'production/renders/reference').glob('*.png'))
    images += [p for folder in [FULL,CLOSED] for p in folder.glob('*.png') if p.stat().st_size>=1000000]
    for source in images:
        data=source.read_bytes()
        encoded=base64.b64encode(data).decode('ascii')
        chunks=[]
        stem=source.parent.name+'__'+source.stem
        for i,start in enumerate(range(0,len(encoded),720000)):
            part=destination/(stem+'.'+str(i)+'.base64.txt')
            part.write_text(encoded[start:start+720000])
            chunks.append(str(part.relative_to(ROOT)))
        records.append({'source':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'chunks':chunks})
    (destination/'INDEX.json').write_text(json.dumps({'schema':'fuel-exact-render-bytes/1','editing':'None; base64 is a reversible representation of the original PNG bytes','images':records},indent=2)+'\n')
    print('FUEL_CI_EXACT_BYTES',len(records),flush=True)


def native():
    blender=shutil.which('blender');assert blender
    common=[blender,'-b','-t','4','--disable-autoexec','--python-exit-code','1']
    run('build',common+['--factory-startup','--python',str(TASK/'blender/build_overhaul.py'),'--','--stage','full'])
    CHECK.mkdir(parents=True,exist_ok=True)
    shutil.copy2(SOURCE,NATIVE);shutil.copy2(TASK/'production/BUILD_MANIFEST.json',MANIFEST)
    run('cold',common+[str(NATIVE),'--python',str(TASK/'blender/validate_overhaul.py'),'--','--manifest',str(MANIFEST),'--report',str(COLD)])
    report=json.loads(COLD.read_text());assert report['status']=='PASS' and not report['failures']

def views(group):
    # Every worker restores exactly the native bytes produced by the cold-checked job.
    CHECK.mkdir(parents=True,exist_ok=True);shutil.copy2(SOURCE,NATIVE)
    report=json.loads(COLD.read_text())
    sha=hashlib.sha256(NATIVE.read_bytes()).hexdigest()
    assert report['status']=='PASS' and report['sha256']==sha
    selected=CAMERA_GROUPS[group]
    blender=shutil.which('blender');assert blender
    common=[blender,'-b','-t','4','--disable-autoexec','--python-exit-code','1']
    env=os.environ.copy();env.update(RES='1280x853',SAMPLES='32',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='4')
    run('full_render_'+str(group),common+['--factory-startup','--python',str(TASK/'blender/render_review.py'),'--',str(NATIVE),str(FULL),','.join(selected)],env)
    evidence=json.loads((FULL/'RENDER_MANIFEST.json').read_text())
    assert evidence['scene_sha256']==sha and [c['name'] for c in evidence['cameras']]==selected
    (FULL/'RENDER_MANIFEST.json').rename(FULL/('GROUP_'+str(group)+'.json'))
    if group==len(CAMERA_GROUPS)-1:
        run('closed_render',common+['--factory-startup','--python',str(TASK/'blender/render_closed_gate.py'),'--',str(NATIVE),str(CLOSED)],env)
    if group<len(DETAIL_CAMERAS):
        detail=DETAIL_CAMERAS[group]
        run('detail_render_'+str(group),common+['--factory-startup','--python',str(TASK/'blender/render_detail_proofs.py'),'--',str(NATIVE),str(LOGS/'details'/detail),detail],env)
    assert hashlib.sha256(NATIVE.read_bytes()).hexdigest()==sha

def verify_evidence():
    sha=hashlib.sha256(NATIVE.read_bytes()).hexdigest()
    report=json.loads(COLD.read_text())
    assert report['status']=='PASS' and not report['failures'] and report['sha256']==sha
    for folder,count in [(FULL,19),(CLOSED,1)]:
        evidence=json.loads((folder/'RENDER_MANIFEST.json').read_text())
        assert evidence['scene_sha256']==sha and len(evidence['cameras'])==count
        if folder==FULL:assert [c['name'] for c in evidence['cameras']]==CAMERAS.split(',')
        for camera in evidence['cameras']:
            assert hashlib.sha256((folder/camera['image']).read_bytes()).hexdigest()==camera['sha256']
    full_evidence=json.loads((FULL/'RENDER_MANIFEST.json').read_text())
    for name in DETAIL_CAMERAS:
        folder=LOGS/'details'/name
        evidence=json.loads((folder/'RENDER_MANIFEST.json').read_text())
        assert evidence['scene_sha256']==sha and len(evidence['cameras'])==1
        camera=evidence['cameras'][0];assert camera['name']==name
        assert all(evidence[k]==full_evidence[k] for k in ['blender','engine','device','samples','seed','denoise','resolution','view_transform','look','exposure'])
        assert hashlib.sha256((folder/camera['image']).read_bytes()).hexdigest()==camera['sha256']
    return sha,report

def assemble():
    CHECK.mkdir(parents=True,exist_ok=True);shutil.copy2(SOURCE,NATIVE)
    groups=[json.loads((FULL/('GROUP_'+str(i)+'.json')).read_text()) for i in range(len(CAMERA_GROUPS))]
    settings=['scene','scene_sha256','blender','engine','device','samples','seed','denoise','resolution','view_transform','look','exposure']
    for group in groups[1:]:
        assert all(group[key]==groups[0][key] for key in settings),'Render workers disagree'
    cameras=[camera for group in groups for camera in group['cameras']]
    assert [c['name'] for c in cameras]==CAMERAS.split(',')
    combined=dict(groups[0]);combined['cameras']=cameras
    combined['worker_manifests']=['GROUP_'+str(i)+'.json' for i in range(len(CAMERA_GROUPS))]
    (FULL/'RENDER_MANIFEST.json').write_text(json.dumps(combined,indent=2)+'\n')
    sha,report=verify_evidence();export_pixel_bytes()
    shutil.copy2(COLD,TASK/'production/COLD_VALIDATION.json')
    state=TASK/'production/TASK_STATE.md'
    state.write_text(state.read_text()+'\n## '+CYCLE+' hosted execution\n\nNative SHA256 '+sha+'. Cold validation PASS, zero failures.\nAll 19 full views and the closed-leaf diagnostic are rendered and hash-verified.\nAll workers used the identical cold-checked native bytes.\nIndependent visual review is pending; no art or Unity acceptance is claimed.\n\nAuthoring geometry: '+json.dumps(report['geometry_budget'])+'.\n')
    print('FUEL_CI_EVIDENCE_READY',CYCLE,sha,flush=True)

def build():
    if CONTROL.get('mode')=='export':
        verify_evidence();export_pixel_bytes();return
    native()
    for i in range(len(CAMERA_GROUPS)):views(i)
    assemble()

def publish():
    assert os.environ.get('GITHUB_REF_NAME')==BRANCH,'This runner may only publish the owned task branch'
    subprocess.run(['git','fetch','origin',BRANCH],cwd=ROOT,check=True)
    assert git('rev-parse','FETCH_HEAD')==os.environ['GITHUB_SHA'],'Task branch advanced; preserve artifacts instead of publishing stale results'
    report=json.loads(COLD.read_text());assert report['status']=='PASS'
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==report['sha256']
    paths=[SOURCE,TASK/'production/BUILD_MANIFEST.json',TASK/'production/COLD_VALIDATION.json',TASK/'production/TASK_STATE.md',NATIVE,MANIFEST,COLD,FULL,CLOSED,LOGS]
    rel=[str(p.relative_to(ROOT)) for p in paths]
    subprocess.run(['git','add','--',*rel],cwd=ROOT,check=True)
    allowed=set(rel)
    for p in git('diff','--cached','--name-only').splitlines():
        assert p in allowed or any(p.startswith(a+'/') for a in allowed),p
    for key,expected in json.loads(MANIFEST.read_text())['recipe_inputs'].items():
        assert hashlib.sha256((ROOT/key).read_bytes()).hexdigest()==expected,'Construction inputs changed'
    subprocess.run(['git','config','user.name','Critical Shift Asset Builder'],cwd=ROOT,check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],cwd=ROOT,check=True)
    subprocess.run(['git','commit','-m','Publish verified '+CYCLE+' fuel scene and complete visual evidence [skip ci]'],cwd=ROOT,check=True)
    subprocess.run(['git','push','origin','HEAD:'+BRANCH],cwd=ROOT,check=True)
    print('FUEL_CI_PUBLISHED',git('rev-parse','HEAD'),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('stage',choices=['prepare','native','views','assemble','build','publish'])
    parser.add_argument('--group',type=int,choices=range(len(CAMERA_GROUPS)),default=0)
    args=parser.parse_args()
    if args.stage=='views':views(args.group)
    else:globals()[args.stage]()
