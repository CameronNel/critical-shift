"""Capture sampled dim states in the assembled map without saving source files.

blender -b -t 4 --factory-startup --disable-autoexec --python-exit-code 1 \
 --python sections/fuel-corridor/blender/render_main_dim_states.py -- --review-cycle F19ci
"""
from pathlib import Path
import argparse,datetime,hashlib,json,runpy,sys
import bpy

ROOT=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser();parser.add_argument('--review-cycle',dest='cycle',required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
source=ROOT/'sections/facility-assembly/sources/fuel-corridor/module.blend'
main=ROOT/'sections/facility-assembly/blender/facility_environment.blend'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
native_sha,main_sha=sha(source),sha(main)
build=json.loads((ROOT/'sections/fuel-corridor/production/BUILD_MANIFEST.json').read_text())
assert native_sha==build['sha256']
out=ROOT/'sections/fuel-corridor/production/renders/temporal'/(args.cycle+'-main-dim')
out.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(main),load_ui=False)
module,instance,cache,hidden=runpy.run_path(str(ROOT/'open_fuel_overhaul.py'),run_name='fuel_dim_import')['install_live_fuel']()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU'
scene.cycles.samples=32;scene.cycles.seed=7;scene.cycles.use_denoising=True
scene.render.resolution_x=960;scene.render.resolution_y=640
scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.15
report={'schema':'fuel-assembled-map-dim-state-evidence/1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'native_sha256':native_sha,'recipe_sha256':build['recipe_sha256'],'canonical_map_sha256':main_sha,
        'lighting_installer_sha256':sha(ROOT/'open_fuel_overhaul.py'),'renderer_sha256':sha(Path(__file__)),
        'lighting_policy':json.loads(instance['fc_lighting_policy']),'source_saved':False,
        'settings':{'blender':bpy.app.version_string,'resolution':[960,640],'samples':32,'seed':7,'denoise':True,
                    'engine':'CYCLES','device':'CPU','view_transform':'AgX','look':'AgX - Medium High Contrast','exposure':-.15},
        'scope':'Sampled still readability and local light response; no continuous cadence or runtime acceptance.','images':[]}
for name,frame in [('C01_ENTRY',110),('C03_HERO',29),('C05_EAST_TURN',1),('C08_SERVICE_JUNCTION',1)]:
    scene.frame_set(frame);graph=bpy.context.evaluated_depsgraph_get()
    scene.camera=next(o for o in module.all_objects if o.type=='CAMERA' and o.name==name)
    image=out/(name+f'_F{frame:04d}.png');scene.render.filepath=str(image)
    bpy.ops.render.render(write_still=True)
    values=[]
    for row in build['atmosphere']['flicker']+build['atmosphere']['alarms']:
        obj=next(o for o in module.all_objects if o.name==row['light'])
        energy=float(obj.evaluated_get(graph).data.energy)
        values.append({'light':obj.name,'energy_w':energy,'factor':energy/row['energy_base_w']})
    dead=next(o for o in module.all_objects if o.name=='FC | East fluorescent pool')
    assert dead.evaluated_get(graph).data.energy==0
    report['images'].append({'camera':name,'frame':frame,'image':str(image.relative_to(ROOT)),
                             'sha256':sha(image),'keyed_sources':values,
                             'failed_east_fixture':{'light':dead.name,'energy_w':0,'fixture':dead.parent.name}})
    assert sha(source)==native_sha and sha(main)==main_sha
    (out/'RENDER_MANIFEST.json').write_text(json.dumps(report,indent=2)+'\n')
    print('MAIN_FUEL_DIM_STATE',args.cycle,name,frame,flush=True)
print('MAIN_FUEL_DIM_COMPLETE',args.cycle,flush=True)
