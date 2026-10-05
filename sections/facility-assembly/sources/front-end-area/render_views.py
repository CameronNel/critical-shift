import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fe_lighting
a = sys.argv[sys.argv.index('--') + 1:]
outdir = a[0]; names = a[1].split(','); samples = int(a[2]) if len(a) > 2 else 32
res = (int(a[3]), int(a[4])) if len(a) > 4 else (960, 540)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = samples; sc.cycles.use_denoising = True
sc.cycles.denoiser = 'OPENIMAGEDENOISE'; sc.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
if hasattr(sc.cycles, 'use_light_tree'): sc.cycles.use_light_tree = True
sc.cycles.sample_clamp_indirect = 8.0
sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'; sc.view_settings.exposure = float(a[5]) if len(a) > 5 else -0.5
try:
    sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
os.makedirs(outdir, exist_ok=True)
for n in names:
    ob = bpy.data.objects[n]; sc.camera = ob
    fe_lighting.hide_roofs('AERIAL' in n)
    sc.render.filepath = os.path.join(outdir, n + '.png'); bpy.ops.render.render(write_still=True)
print('RENDERED', names)
