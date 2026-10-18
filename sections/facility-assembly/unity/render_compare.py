"""Render a room's own cameras with fixed settings, to compare the procedural source with its baked Unity derivative (bake_room.py) under the same lights:

    blender --background <room source or <room>_unity.blend> --python render_compare.py -- out_dir CAM1,CAM2,... --device GPU|CPU [--engine CYCLES|BLENDER_EEVEE] [--samples 32]
        [--percent 100] [--cameras-from <room source>]   (map mode: the map's room collections carry no review cameras; take them from the room file, same frame)

Same camera, resolution, samples, view transform and lights on both sides, so any difference is the material conversion (and, with EEVEE, the move to a
rasterised renderer, which is closer to what URP draws). Never saves the scene."""
import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import blender_device   # owner rule: GPU or CPU only as the owner says
a = sys.argv[sys.argv.index('--') + 1:]
out, cams = os.path.abspath(a[0]), a[1].split(',')
engine = a[a.index('--engine') + 1] if '--engine' in a else 'CYCLES'; samples = int(a[a.index('--samples') + 1]) if '--samples' in a else 32
os.makedirs(out, exist_ok=True)
src = a[a.index('--cameras-from') + 1] if '--cameras-from' in a else None
def camera(name):
    """The scene's own or appended camera of that name: the map links every room file, and two rooms both have a C01_ENTRY."""
    found = [o for o in bpy.data.objects if o.name == name and o.type == 'CAMERA']
    local = next((o for o in found if o.library is None), None)
    return local if (local or src) else (found[0] if len(found) == 1 else None)     # with --cameras-from, only a local or appended camera counts
missing = [c for c in cams if camera(c) is None]
if src and missing:
    with bpy.data.libraries.load(os.path.abspath(src), link=False) as (have, want): want.objects = [c for c in missing if c in have.objects]
    for o in want.objects:
        if o is not None: bpy.context.scene.collection.objects.link(o); print('COMPARE camera from', os.path.basename(src), o.name)
pct = int(a[a.index('--percent') + 1]) if '--percent' in a else 100     # bake_room.ps1 -Quality rehearsal: 25
sc = bpy.context.scene; sc.render.engine = engine; sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1280, 720, pct
if engine == 'CYCLES': blender_device.apply(sc); sc.cycles.samples = samples; sc.cycles.use_denoising = True
else: sc.eevee.taa_render_samples = samples
sc.render.image_settings.file_format = 'PNG'
for c in cams:
    o = camera(c)
    if o is None: raise SystemExit('COMPARE missing camera %s (not in this file%s)' % (c, ' or ' + os.path.basename(src) if src else ''))
    sc.camera = o; sc.render.filepath = os.path.join(out, c + '.png'); bpy.ops.render.render(write_still=True); print('COMPARE rendered', c)
