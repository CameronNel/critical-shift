"""Lighting readability at walking height: renders each junction view and measures the image as displayed (scene view transform and exposure). Run on a built scene:

    blender --background combined_map.blend --python measure_lighting.py -- out_dir [report.json] [--only name,name]

Cycles CPU, 640 x 360, 14 samples, denoised; the mine is hidden for speed (no view looks into it). Per view: median and mean display luma (Rec. 709 weights on the
8-bit sRGB-encoded image, 0..1), 10th percentile, share of near-black pixels (luma < 0.04) and of clipped pixels (any channel > 0.98; clipped_white: all three channels). Readability bar used in
ASSEMBLY_REPORT.md (set here, not an art-direction rule): median >= 0.15, near-black <= 25 %, clipped <= 5 %. Renders are scratch output; delete them after reading."""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]
out = a[0]; rep = a[1] if len(a) > 1 and not a[1].startswith('--') else os.path.join(out, 'lighting.json')
only = a[a.index('--only') + 1].split(',') if '--only' in a else None
VIEWS = {   # name: eye, target, lens (mm); plan metres
    'reactor_N_stub': ((0, 7.5, 1.6), (0, 16, 1.4), 18), 'turbine_entry': ((0, 16.0, 1.6), (0, 30, 1.6), 18),
    'turbine_east_aisle_to_electrical': ((7.8, 29.0, 1.6), (12, 33, 1.4), 18), 'electrical_inside': ((11.5, 33, 1.6), (24, 33, 1.4), 18),
    'reactor_W_stub_to_cooling': ((-11.2, 0, 1.6), (-20, 0, 1.4), 18), 'cooling_inside': ((-15.5, 0, 1.6), (-26, 0, 1.4), 18),
    'spine_to_waste': ((8.5, -25.48, 1.6), (20, -25.48, 1.4), 18), 'waste_inside': ((12.0, -25.48, 1.6), (26, -25.48, 1.2), 18),
    'spine_to_dock': ((8.5, -40.39, 1.6), (20, -40.39, 1.3), 18), 'dock_inside': ((13.8, -40.39, 1.6), (26, -40.39, 1.2), 18),
    'concourse': ((5, -17.2, 1.6), (-8, -17.2, 1.4), 18), 'spine_mid': ((8, -44, 1.6), (8, -20, 1.6), 18), 'reactor_from_south': ((0, -16.5, 1.6), (0, -4, 1.6), 18),
    'transfer_hall': ((5, -27.6, 1.6), (-6, -27.6, 1.4), 18), 'stair_top': ((-5.6, 28.8, 1.6), (-5.6, 20, -2), 18), 'stair_bottom': ((-5.6, 15.7, -4.4), (1.6, 15.7, -4.6), 18),
    'condenser_D01': ((1.6, 16.2, -4.4), (1.6, 26, -4.6), 18), 'condenser_inside': ((1.6, 22.6, -4.4), (6, 29, -4.8), 18),
}
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 14; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 640, 360; sc.render.image_settings.file_format = 'PNG'
for n in ('ROOM_mine',):
    o = bpy.data.objects.get(n)
    if o: o.hide_render = True
os.makedirs(out, exist_ok=True); res = {}
if os.path.exists(rep):
    try: res = json.load(open(rep))['views']
    except Exception: res = {}

for name, (eye, tgt, lens) in VIEWS.items():
    if only and name not in only: continue
    c = bpy.data.cameras.new(name); c.lens = lens; c.clip_start = 0.05; o = bpy.data.objects.new(name, c); sc.collection.objects.link(o)
    o.location = eye; o.rotation_euler = (Vector(tgt) - Vector(eye)).to_track_quat('-Z', 'Y').to_euler(); sc.camera = o
    path = os.path.join(out, name + '.png'); sc.render.filepath = path; bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(path); px = np.array(im.pixels[:], np.float32).reshape(-1, 4)[:, :3]; bpy.data.images.remove(im)
    # Blender returns float pixels of a PNG in linear space; re-encode to sRGB to measure what is displayed
    srgb = np.where(px <= 0.0031308, px * 12.92, 1.055 * np.power(np.clip(px, 0, 1), 1 / 2.4) - 0.055)
    y = srgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    m = dict(median=round(float(np.median(y)), 3), mean=round(float(y.mean()), 3), p10=round(float(np.percentile(y, 10)), 3),
             near_black=round(float((y < 0.04).mean()), 3), clipped=round(float((srgb > 0.98).any(1).mean()), 3), clipped_white=round(float((srgb > 0.98).all(1).mean()), 3), eye=list(eye), target=list(tgt))
    m['readable'] = m['median'] >= 0.15 and m['near_black'] <= 0.25 and m['clipped'] <= 0.05
    res[name] = m; print('LIGHT %-34s median %.3f mean %.3f p10 %.3f black %.2f clip %.3f %s' % (name, m['median'], m['mean'], m['p10'], m['near_black'], m['clipped'], 'ok' if m['readable'] else 'DARK/HOT'))
    json.dump(dict(settings='Cycles CPU 640x360 14 spp denoised; view transform %s exposure %.2f' % (sc.view_settings.view_transform, sc.view_settings.exposure), views=res), open(rep, 'w'), indent=1)
