"""Reuse the section's saved audits and renderer without overwriting R34 evidence.

Modes run inside Blender against the supplied blend. Audits execute byte-identical
copies of the original scripts in an isolated temporary directory. The original
renderer runs with a documented cloud CPU adapter (five threads, nice 10).
No modified scene is saved. Extra AAA cameras exist only for rendering.
"""
import argparse
import hashlib
import json
import os
import runpy
import shutil
import sys
import tempfile
from pathlib import Path
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SECTION = REPO / 'sections/condenser-bay'
TOOLS = SECTION / 'blender'
AAA_CAMERAS = {
 'AAA01_WIDE_NE': ((9.3, 8.8, 3.0), (3.2, 3.2, 1.7), 21),
 'AAA02_PUMPS': ((1.2, 5.8, 1.5), (4.0, 7.9, 1.0), 24),
 'AAA03_OPERATOR': ((0.0, 1.6, 1.6), (-1.2, 4.3, 1.3), 22),
 'AAA04_PULL_BAY': ((6.4, 6.4, 1.6), (9.0, 2.5, 1.8), 22),
}

def add_aaa():
    for name, (eye, target, lens) in AAA_CAMERAS.items():
        if bpy.data.objects.get(name):
            continue
        data = bpy.data.cameras.new(name); data.lens = lens; data.clip_start = .05
        ob = bpy.data.objects.new(name, data); bpy.context.scene.collection.objects.link(ob)
        ob.location = eye
        ob.rotation_euler = (Vector(target) - Vector(eye)).to_track_quat('-Z', 'Y').to_euler()

def audit(label):
    target = HERE / 'evidence-A2' / label
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='condenser-audit-') as tmp:
        root = Path(tmp); tool = root / 'blender'; tool.mkdir(); (root / 'architecture').mkdir()
        (root / 'production/validation').mkdir(parents=True)
        shutil.copy2(SECTION / 'interface.json', root / 'interface.json')
        hashes = {}
        for src in TOOLS.glob('*.py'):
            shutil.copy2(src, tool / src.name)
            hashes[src.name] = hashlib.sha256(src.read_bytes()).hexdigest()
        previous = bpy.context.scene.get('source_revision')
        bpy.context.scene['source_revision'] = label
        try:
            runpy.run_path(str(tool / 'astra_validate_saved.py'), run_name='__main__')
        finally:
            shutil.copytree(root / 'production/validation', target / 'room-audits', dirs_exist_ok=True)
            if (root / 'architecture/floorplan.svg').exists():
                shutil.copy2(root / 'architecture/floorplan.svg', target / 'measured-floorplan.svg')
            (target / 'audit-script-hashes.json').write_text(json.dumps(hashes, indent=2) + '\n')
            bpy.context.scene['source_revision'] = previous

def render(label, selection, samples, width, height, resume=False):
    os.environ['ASTRA_RENDER_MODE'] = 'CPU'
    os.nice(10)
    sys.path.insert(0, str(TOOLS))
    import resource_guard
    # Cloud task, not the historical Windows desktop policy. Record actual settings.
    resource_guard.THREADS = len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else 5
    resource_guard.THREADS = min(resource_guard.THREADS, 5)
    original = resource_guard.configure_scene
    def cloud_scene(sc, spp=32):
        original(sc, spp)
        sc['astra_resource_policy'] = 'Cloud CPU Cycles; 5 threads; Linux nice 10; one Blender worker; CPU OIDN; no GPU.'
        sc.cycles.adaptive_min_samples = 8
    resource_guard.configure_scene = cloud_scene
    import render as original_renderer
    add_aaa()
    names = selection if selection != 'all' else ','.join(sorted(o.name for o in bpy.context.scene.objects if o.type == 'CAMERA'))
    destination = HERE / 'renders-A2' / label
    prior = destination / 'render_manifest.json'
    history = []
    if prior.exists():
        assert resume, 'Existing evidence requires explicit resume; no frame overwrites'
        previous = json.loads(prior.read_text())
        assert previous['blend_sha256'] == hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
        assert previous['samples'] == samples and previous['resolution'] == [width,height]
        for entry in previous['cameras']:
            assert hashlib.sha256((destination/(entry['camera']+'.png')).read_bytes()).hexdigest() == entry['sha256']
        completed = {entry['camera'] for entry in previous['cameras']}
        requested = names.split(',');assert completed <= set(requested)
        names = ','.join(n for n in requested if n not in completed)
        history = [{'camera':e['camera'],'process_id':e['process_id'],'sha256':e['sha256']} for e in previous['cameras']]
        assert names, 'Complete packs are immutable; the queue must skip them'
    with tempfile.TemporaryDirectory(prefix='condenser-render-') as tmp:
        # Persist each genuine frame immediately, even if the environment restarts.
        destination.mkdir(parents=True, exist_ok=True)
        output = Path(tmp) / 'production/renders/review' / label
        output.parent.mkdir(parents=True)
        output.symlink_to(destination, target_is_directory=True)
        manifest = original_renderer.render_set(Path(tmp), label, names, samples, width, height)
    manifest['process_priority'] = 'NICE10'
    manifest['cloud_resource_adapter'] = {'file': Path(__file__).name, 'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'linux_nice': os.nice(0), 'cpu_threads': resource_guard.THREADS, 'scene_saved': False, 'extra_camera_policy': 'AAA cameras added only in this disposable process; all R34 cameras retained unchanged'}
    if history:manifest['resume_history']={'reason':'Environment restart interrupted the prior producer; its exit is unknown. Existing original PNG hashes verified, only missing cameras rendered with the original renderer/settings against the same native.','retained_frames':history,'new_process_id':os.getpid()}
    (destination / 'render_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['audit', 'render'])
    ap.add_argument('--label', required=True)
    ap.add_argument('--selection', default='all')
    ap.add_argument('--samples', type=int, default=32)
    ap.add_argument('--width', type=int, default=1920)
    ap.add_argument('--height', type=int, default=1080)
    ap.add_argument('--resume', action='store_true')
    p = ap.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if p.mode == 'audit':audit(p.label)
    else:render(p.label, p.selection, p.samples, p.width, p.height,p.resume)
