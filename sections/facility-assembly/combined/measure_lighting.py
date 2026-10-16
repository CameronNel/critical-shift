"""Lighting readability at walking height: renders each junction view and measures the image as displayed (scene view transform and exposure). Run on a built scene:

    blender --background combined_map.blend --python measure_lighting.py -- out_dir [report.json] [--only name,name]

Cycles CPU, 640 x 360, 14 samples, denoised; the mine is hidden for speed (no view looks into it). Per view: median and mean display luma (Rec. 709 weights on the
8-bit sRGB-encoded image, 0..1), 10th percentile, share of near-black pixels (luma < 0.04) and of clipped pixels (any channel > 0.98; clipped_white: all three channels). Readability bar used in
ASSEMBLY_REPORT.md (set here, not an art-direction rule): median >= 0.15, near-black <= 25 %, clipped <= 5 %. Renders are scratch output; delete them after reading."""
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import blender_device   # owner rule: GPU or CPU only as the owner says
import numpy as np
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]
out = a[0]; rep = a[1] if len(a) > 1 and not a[1].startswith('--') else os.path.join(out, 'lighting.json')
only = a[a.index('--only') + 1].split(',') if '--only' in a else None
RY = float(bpy.context.scene.get('reactor_y', 0.0))      # reactor centre y (build_compact_map.py); views that moved with the reactor are reactor-local + RY
def r(x, y, z): return (x, y + RY, z)
CY = RY - 17.2; WY = RY + 3.86
VIEWS = {   # name: eye, target, lens (mm); plan metres
    'reactor_N_stub': (r(0, 7.5, 1.6), r(0, 16, 1.4), 18), 'turbine_entry': (r(0, 16.0, 1.6), r(0, 30, 1.6), 18),
    'turbine_east_aisle_to_electrical': (r(7.55, 22.0, 1.6), r(12, 27.0, 1.4), 18), 'electrical_inside': (r(11.5, 27.0, 1.6), r(24, 27.0, 1.4), 18),
    'reactor_W_stub_to_cooling': (r(-11.2, 0, 1.6), r(-20, 0, 1.4), 18), 'cooling_inside': (r(-15.5, 0, 1.6), r(-26, 0, 1.4), 18),
    'reactor_to_waste': ((7.0, WY, 1.6), (20, WY, 1.4), 18), 'waste_inside': ((12.6, WY, 1.6), (26, WY, 1.2), 18),
    'spine_to_dock': ((8.5, -40.39, 1.6), (20, -40.39, 1.3), 18), 'dock_inside': ((13.8, -40.39, 1.6), (26, -40.39, 1.2), 18),
    'concourse': ((5, CY, 1.6), (-8, CY, 1.4), 18), 'spine_mid': ((8, -46, 1.6), (8, -30, 1.6), 18), 'reactor_from_south': ((0, CY + 0.7, 1.6), (0, RY - 4, 1.6), 18),
    'fuel_F02E_to_concourse': ((-8.0, -36.4, 1.6), (4, -36.0, 1.4), 18), 'fuel_corridor_east': ((-20.5, -36.0, 1.6), (-6, -36.4, 1.4), 18),
    'stair_top': (r(-5.6, 28.8, 1.6), r(-5.6, 20, -2), 18), 'stair_bottom': (r(-5.6, 15.7, -4.4), r(1.6, 15.7, -4.6), 18),
    'condenser_D01': (r(1.6, 16.2, -4.4), r(1.6, 26, -4.6), 18), 'condenser_inside': (r(1.6, 22.6, -4.4), r(6, 29, -4.8), 18),
    # evacuation routes at night (evacuation.py): the east road, the east yard behind the reactor, the west path
    'evac_east_road': ((34.4, 10.0, 1.6), (34.4, -12.0, 1.0), 18), 'evac_east_yard': ((26.0, -27.0, 1.6), (12.0, -30.5, 1.4), 18), 'evac_west_path': ((-36.5, -21.0, 1.6), (-36.5, -45.0, 1.0), 18),
    'concourse_blast_door': ((0.0, -37.8, 1.6), (0.0, -33.5, 2.4), 18),
    # condenser bay second exit: along the escape tunnel to the ladder, and the hatch house outside at night
    'condenser_escape_tunnel': (r(0.6, 30.8, -4.4), r(-5.6, 30.8, -4.6), 18), 'escape_house_night': ((-4.6, 17.5, 1.6), (-5.6, 13.2, 1.2), 18),
    # cafeteria (the revamp since 2026-10-14): its own camera spots (cafeteria-revamp/CAMERAS.md, module-local + (8, -80)) at walking height
    'cafeteria_entry': ((8.0, -79.2, 1.6), (8.0, -74.2, 1.6), 18), 'cafeteria_dining': ((9.5, -78.8, 1.6), (13.9, -76.5, 1.3), 18),
    'cafeteria_lounge': ((3.4, -71.2, 1.6), (-0.7, -74.0, 1.3), 18), 'cafeteria_games': ((3.0, -67.0, 1.6), (-1.35, -64.55, 1.4), 18),
    'cafeteria_medical_door': ((18.5, -70.0, 1.6), (23.5, -70.0, 1.6), 18),
}
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; blender_device.apply(sc); sc.cycles.samples = 14; sc.cycles.use_denoising = True
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
