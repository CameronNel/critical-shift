"""Fixed fuel cameras rendered in the actual assembled map, without saving it.

blender -b --factory-startup --disable-autoexec --python-exit-code 1 \
 --python sections/fuel-corridor/blender/render_live_map_views.py -- --review-cycle F18ci
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,runpy,sys
import bpy

ROOT=Path(__file__).resolve().parents[3]
TASK=ROOT/'sections/fuel-corridor/production'
parser=argparse.ArgumentParser();parser.add_argument('--review-cycle',dest='cycle',required=True);parser.add_argument('--cameras')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
source=ROOT/'sections/facility-assembly/sources/fuel-corridor/module.blend'
main=ROOT/'sections/facility-assembly/blender/facility_environment.blend'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
native_sha=sha(source);main_sha=sha(main)
build=json.loads((TASK/'BUILD_MANIFEST.json').read_text())
assert native_sha==build['sha256']
out=TASK/'renders/review'/('main-'+args.cycle)
out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(main),load_ui=False)
installer=runpy.run_path(str(ROOT/'open_fuel_overhaul.py'),run_name='fuel_map_review_import')
module,instance,cache,hidden=installer['install_live_fuel']()
scene=bpy.context.scene;scene.frame_set(1)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=int(os.environ.get('SAMPLES','32'))
scene.cycles.seed=7;scene.cycles.use_denoising=True
scene.render.resolution_x,scene.render.resolution_y=map(int,os.environ.get('RES','960x640').split('x'))
scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.15
default='C01_ENTRY,C02_PRIMARY_ROUTE,C03_HERO,C04_REVERSE,C05_EAST_TURN,C06_REACTOR_THRESHOLD,C07_BYPASS,C08_SERVICE_JUNCTION,C09_MATERIALS,C10_PLANT_HEADER,D01_CARRIER_OPERATION,D02_WORKBENCH,D03_UTILITY,D04_REACTOR_WIDE,D05_GATE_MECHANISM,D06_SERVICE_RECESS,E01_WASTE_APPROACH,E02_CLEAN_APPROACH,E03_FREIGHT_LEAF'
cameras=(args.cameras or default).split(',')
report={'schema':'fuel-assembled-map-fixed-view-evidence/1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scene':str(source.relative_to(ROOT)),'scene_sha256':native_sha,'canonical_map_sha256':main_sha,
        'recipe_sha256':build['recipe_sha256'],'lighting_installer_sha256':sha(ROOT/'open_fuel_overhaul.py'),
        'renderer_sha256':sha(Path(__file__)),
        'lighting_policy':json.loads(instance['fc_lighting_policy']),'blender':bpy.app.version_string,
        'engine':'CYCLES','device':'CPU','samples':scene.cycles.samples,'seed':7,'denoise':True,
        'resolution':[scene.render.resolution_x,scene.render.resolution_y],'view_transform':scene.view_settings.view_transform,
        'look':scene.view_settings.look,'exposure':scene.view_settings.exposure,'frames':[1],
        'fps':scene.render.fps,'fps_base':scene.render.fps_base,'source_saved':False,'cameras':[]}
for name in cameras:
    camera=next(o for o in module.all_objects if o.type=='CAMERA' and o.name==name)
    scene.camera=camera;image=out/(name+'.png');scene.render.filepath=str(image)
    bpy.ops.render.render(write_still=True)
    report['cameras'].append({'name':name,'frame':1,'matrix_world':[list(row) for row in camera.matrix_world],
                              'lens':camera.data.lens,'image':image.name,'sha256':sha(image)})
    assert sha(source)==native_sha and sha(main)==main_sha
    (out/'RENDER_MANIFEST.json').write_text(json.dumps(report,indent=2)+'\n')
    print('MAIN_FUEL_VIEW',args.cycle,name,len(report['cameras']),'/',len(cameras),flush=True)
print('MAIN_FUEL_FULL_REVIEW_COMPLETE',args.cycle,len(report['cameras']),flush=True)
