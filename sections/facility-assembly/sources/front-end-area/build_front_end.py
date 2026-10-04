import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
import fe_common, fe_shell, fe_lighting, fe_props, fe_yard, fe_cafeteria, fe_hall, fe_dress, fe_scrap, fe_minefront
from fe_common import *
from fe_shell import *
from fe_lighting import build_lighting, build_cameras
import fe_yard, fe_cafeteria, fe_hall, fe_dress, fe_scrap, fe_minefront

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
out = args[args.index('--output') + 1] if '--output' in args else None
stages = args[args.index('--stages') + 1].split(',') if '--stages' in args else ['shell']

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.system = 'METRIC'; sc.unit_settings.scale_length = 1.0
root = setup_collections()
C = {n: collection(n) for n in ('YARD', 'CAFETERIA', 'HALL', 'SHARED', 'LIGHTS', 'CAMERAS', 'INTERFACES')}
F = families()
report = {}
if 'shell' in stages:
    build_shell(F, C); build_roofs(F, C)
if 'yard' in stages:
    fe_yard.build_ground(F, C)
    fe_yard.build_trench(F, C, 'trench_N', -44.0, -26.0, -61.4); fe_yard.build_trench(F, C, 'trench_S', -20.0, -12.0, -82.6); fe_yard.build_trench(F, C, 'trench_porch', -11.7, -8.4, -62.4)
    fe_yard.build_cliff(F, C); fe_yard.build_rails(F, C); fe_yard.build_fences(F, C); fe_yard.build_canopies(F, C)
    MINE_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mine-r39', 'module_r39_aaa.blend')
    fe_minefront.build_mine_front(F, C, MINE_SRC)
    for k, yy in enumerate((-72.6, -67.4)):
        box(f'portal_lamp{k}', -47.7, -47.45, yy - 0.12, yy + 0.12, 3.5, 3.7, F['emissive'], C['YARD'], rgba=(1.0, 0.7, 0.35, 1), bev=0.01)
    _sl = bpy.data.lights.new('PORTAL_SPOT', 'SPOT'); _sl.energy = 2500; _sl.spot_size = math.radians(70); _sl.spot_blend = 0.7; _sl.color = (1.0, 0.72, 0.4)
    _so = bpy.data.objects.new('PORTAL_SPOT', _sl); _so.location = (LX(-41.0), LY(-70.0), 4.8)
    _so.rotation_euler = (Vector((LX(-48.0) - _so.location.x, LY(-70.0) - _so.location.y, 2.0 - _so.location.z))).to_track_quat('-Z', 'Y').to_euler(); C['LIGHTS'].objects.link(_so)
    P = collection('PROTOTYPES'); X = fe_scrap.make_protos(F, P)
    rects = fe_scrap.build_scrapyard(F, C, P, X)
    fe_yard.build_props(F, C, extra_avoid=rects)
if 'cafeteria' in stages:
    fe_cafeteria.build_cafeteria(F, C)
if 'hall' in stages:
    fe_hall.build_hall(F, C); fe_hall.build_connectors(F, C)
    _P = collection('PROTOTYPES'); _X = fe_scrap.make_protos(F, _P) if 'X' not in globals() else X
    fe_scrap.build_hall_clutter(F, C, _P, _X)
if 'dress' in stages:
    fe_dress.build_dressing(F, C)
    _P = collection('PROTOTYPES'); fe_scrap.build_grime(F, C, _P, None)
build_lighting(F, C); build_cameras(C)
for n in ('YARD', 'CAFETERIA', 'HALL', 'SHARED'):
    report[n] = tri_count_coll(C[n])
report['TOTAL'] = sum(report.values())
print('TRIANGLES', json.dumps(report))
if out: bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
