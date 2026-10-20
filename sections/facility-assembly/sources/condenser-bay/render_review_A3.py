"""Review renders of a condenser blend on the CPU (the owner's choice for review renders), with the manifest the cold comparison policy asks for
(sections/condenser-bay/production/COLD_COMPARISON_POLICY.md): blend and script hashes, process id, settings, camera transforms and image hashes.

    blender -b --factory-startup module_aaa_A3.blend --python render_review_A3.py -- <outdir> <res_x> <samples> [CAM1,CAM2,...|ALL]

Writes <outdir>/<camera>.png and <outdir>/manifest.json. The device is always the CPU: this tool is for the cloud review renders only.
"""
import bpy, sys, os, time, json, hashlib
from pathlib import Path

a = sys.argv[sys.argv.index('--') + 1:]
out, rx, spp = Path(a[0]).resolve(), int(a[1]), int(a[2]); cams = a[3] if len(a) > 3 else 'ALL'
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
sc.cycles.samples = spp; sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'; sc.cycles.seed = 0
sc.render.resolution_x = rx; sc.render.resolution_y = rx * 9 // 16; sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '8'
names = sorted(o.name for o in sc.objects if o.type == 'CAMERA') if cams == 'ALL' else cams.split(',')
out.mkdir(parents=True, exist_ok=True)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
man = dict(blend=Path(bpy.data.filepath).name, blend_sha256=sha(bpy.data.filepath), script_sha256=sha(__file__), pid=os.getpid(),
           blender=bpy.app.version_string, device='CPU', resolution=[sc.render.resolution_x, sc.render.resolution_y], samples=spp, seed=0,
           denoiser='OPENIMAGEDENOISE', view_transform=sc.view_settings.view_transform, look=sc.view_settings.look, exposure=sc.view_settings.exposure,
           images={})
for n in names:
    cam = sc.objects.get(n)
    if cam is None or cam.type != 'CAMERA': print('RENDER missing camera', n); continue
    sc.camera = cam; f = out / (n + '.png'); sc.render.filepath = str(f); t = time.time()
    bpy.ops.render.render(write_still=True)
    man['images'][n] = dict(file=f.name, sha256=sha(f), seconds=round(time.time() - t, 1), lens_mm=round(cam.data.lens, 3),
                            matrix=[[round(v, 5) for v in row] for row in cam.matrix_world])
    print('RENDER %s %.1fs' % (n, time.time() - t), flush=True)
    (out / 'manifest.json').write_text(json.dumps(man, indent=1) + '\n')
