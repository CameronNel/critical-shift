"""Render a room's own cameras with fixed settings, to compare the procedural source with its baked Unity derivative (bake_room.py) under the same lights:

    blender --background <room source or <room>_unity.blend> --python render_compare.py -- out_dir CAM1,CAM2,... --device GPU|CPU [--engine CYCLES|BLENDER_EEVEE] [--samples 32]

Same camera, resolution, samples, view transform and lights on both sides, so any difference is the material conversion (and, with EEVEE, the move to a
rasterised renderer, which is closer to what URP draws). Never saves the scene."""
import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import blender_device   # owner rule: GPU or CPU only as the owner says
a = sys.argv[sys.argv.index('--') + 1:]
out, cams = os.path.abspath(a[0]), a[1].split(',')
engine = a[a.index('--engine') + 1] if '--engine' in a else 'CYCLES'; samples = int(a[a.index('--samples') + 1]) if '--samples' in a else 32
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene; sc.render.engine = engine; sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1280, 720, 100
if engine == 'CYCLES': blender_device.apply(sc); sc.cycles.samples = samples; sc.cycles.use_denoising = True
else: sc.eevee.taa_render_samples = samples
sc.render.image_settings.file_format = 'PNG'
for c in cams:
    o = bpy.data.objects.get(c)
    if o is None or o.type != 'CAMERA': print('COMPARE missing camera', c); continue
    sc.camera = o; sc.render.filepath = os.path.join(out, c + '.png'); bpy.ops.render.render(write_still=True); print('COMPARE rendered', c)
