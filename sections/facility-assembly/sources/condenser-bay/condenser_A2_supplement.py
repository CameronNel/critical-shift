"""Run the original seven labelled R34 supplemental views in an isolated copy.
Use a fresh Blender process and an immutable saved checkpoint; no source is saved.
"""
import argparse, hashlib, json, os, runpy, shutil, sys, tempfile
from pathlib import Path
import bpy

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[3] / 'sections/condenser-bay/blender'

def main(label, selection, samples, resume=False):
    os.environ['ASTRA_RENDER_MODE'] = 'CPU'
    os.nice(10)
    destination = HERE / 'renders-A2' / label
    history=[]
    if destination.exists():
        assert resume, 'Evidence labels are immutable; explicit resume only'
        previous=json.loads((destination/'render_manifest.json').read_text())
        assert previous['blend_sha256']==hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
        assert previous['samples']==samples and previous['resolution']==[1920,1080]
        for entry in previous['cameras']:
            assert hashlib.sha256((destination/(entry['camera']+'.png')).read_bytes()).hexdigest()==entry['sha256']
        done={e['camera'] for e in previous['cameras']};requested=selection.split(',');assert done<=set(requested)
        selection=','.join(n for n in requested if n not in done);assert selection,'Complete packs must be skipped'
        history=[{'camera':e['camera'],'process_id':e['process_id'],'sha256':e['sha256']} for e in previous['cameras']]
    with tempfile.TemporaryDirectory(prefix='condenser-supplement-') as tmp:
        root = Path(tmp); tool = root / 'blender'; tool.mkdir()
        destination.mkdir(parents=True,exist_ok=resume)
        output = root / 'production/renders/review' / label
        output.parent.mkdir(parents=True)
        output.symlink_to(destination, target_is_directory=True)
        for source in TOOLS.glob('*.py'):shutil.copy2(source, tool / source.name)
        sys.path.insert(0, str(tool))
        import resource_guard
        resource_guard.THREADS = min(len(os.sched_getaffinity(0)), 5)
        original = resource_guard.configure_scene
        def cloud_scene(sc, spp=32):
            original(sc, spp)
            sc['astra_resource_policy'] = 'Cloud CPU Cycles; 5 threads; Linux nice 10; one render worker; CPU OIDN.'
            sc.cycles.adaptive_min_samples = 8
        resource_guard.configure_scene = cloud_scene
        sys.argv = ['blender', '--', label, selection, str(samples), '1920', '1080']
        runpy.run_path(str(tool / 'astra_evidence.py'), run_name='__main__')
    manifest = json.loads((destination / 'render_manifest.json').read_text())
    manifest['process_priority'] = 'NICE10'
    manifest['cloud_resource_adapter'] = {'file':Path(__file__).name,'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'linux_nice':os.nice(0),'cpu_threads':resource_guard.THREADS,'scene_saved':False,'original_scripts_unchanged':True}
    if history:manifest['resume_history']={'reason':'Environment restart; original frames verified and only missing cameras rendered against the same native/settings. Prior producer exit unknown.','retained_frames':history,'new_process_id':os.getpid()}
    (destination / 'render_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--label', required=True)
    ap.add_argument('--selection', default='S01_LOCAL_U02,S02_LOCAL_CW,S03_FULL_ROOF,S04_GLASS,S05_FEET,S06_OPERATOR_WORK,S07_U04_CUTAWAY')
    ap.add_argument('--samples', type=int, default=32)
    ap.add_argument('--resume',action='store_true')
    args = ap.parse_args(sys.argv[sys.argv.index('--')+1:])
    main(args.label, args.selection, args.samples,args.resume)
