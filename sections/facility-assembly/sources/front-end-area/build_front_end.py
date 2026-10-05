import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
import fe_common, fe_shell, fe_lighting, fe_props, fe_yard, fe_cafeteria, fe_hall, fe_dress, fe_minefront, fe_hallsite, fe_yard2
from fe_common import *
from fe_shell import *
from fe_lighting import build_lighting, build_cameras
import fe_yard, fe_cafeteria, fe_hall, fe_dress, fe_minefront, fe_yard2, fe_cafdoors, fe_signs, fe_wear

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
    fe_yard2.build_ground(F, C)
    fe_yard.build_trench(F, C, 'trench_N', -44.0, -26.0, -61.4); fe_yard.build_trench(F, C, 'trench_S', -20.0, -12.0, -82.6); fe_yard.build_trench(F, C, 'trench_porch', -11.7, -8.4, -62.4)
    fe_yard2.build_cliff(F, C); fe_yard2.build_rails(F, C); fe_yard2.build_fences(F, C); fe_yard.build_canopies(F, C)
    MINE_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mine-r39', 'module_r39_aaa.blend')
    if not os.path.exists(MINE_SRC): MINE_SRC = '/home/user/critical-shift/sections/facility-assembly/sources/mine-r39/module_r39_aaa.blend'
    fe_minefront.build_mine_front(F, C, MINE_SRC)
    for k, yy in enumerate((-72.6, -67.4)):
        box(f'portal_lamp{k}', -47.7, -47.45, yy - 0.12, yy + 0.12, 3.5, 3.7, F['emissive'], C['YARD'], rgba=(1.0, 0.75, 0.4, 1), bev=0.01)
    fe_yard2.build_props(F, C)
if 'cafeteria' in stages:
    fe_cafeteria.build_cafeteria(F, C)
if 'hall' in stages:
    fe_hall.build_hall(F, C); fe_hall.build_connectors(F, C)
    fe_hallsite.build_hall_site(F, C, collection('PROTOTYPES'))
if 'cafdress' in stages:
    fe_dress.build_dressing(F, C, parts=('caf',))
if 'cafdoors' in stages or 'dress' in stages:
    fe_cafdoors.build_cafe_doors_and_signs(F, C)
if 'dress' in stages:
    fe_dress.build_dressing(F, C)
if 'wear' in stages or 'dress' in stages:
    print('WEAR_DECALS', fe_wear.build_wear(F, C))
fe_signs.finalize_signs(F)
build_lighting(F, C); build_cameras(C)
_lc = bpy.context.view_layer.layer_collection.children.get('PROTOTYPES')
if _lc: _lc.exclude = True
for n in ('YARD', 'CAFETERIA', 'HALL', 'SHARED'):
    report[n] = tri_count_coll(C[n])
report['TOTAL'] = sum(report.values())
print('TRIANGLES', json.dumps(report))
for _im in bpy.data.images:
    if _im.filepath and not _im.packed_file:
        try: _im.pack()
        except Exception: pass
if out: bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
