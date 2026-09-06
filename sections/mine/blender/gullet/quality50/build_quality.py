"""Continue the saved Gullet scene with the implemented quality pass.
Run inside Blender with Gullet_MaterialReview.blend open and -- --output PATH.
The original checkpoint is preserved; no unrelated scene is cleared.
"""
import bpy,argparse,json,sys,time,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from materials import weather_existing
from coarse_repair import gameplay_scale_surface_repair
import geometry
from geology_repairs import rebuild_collapse,settle_resources
from dressing import all_dressing,excavation_lamps
from cameras import build_cameras,set_review_state
from refinements import refine
from contact_repair import continuous_floor,natural_resources
from review_corrections import apply as review_corrections
REVISION='quality50-r5'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    scene=next((s for s in bpy.data.scenes if s.get('csm_material_revision')),None)
    if scene is None:raise RuntimeError('Open Gullet_MaterialReview.blend first.')
    if scene.get('q50_revision'):raise RuntimeError('Use the unmodified material-review source to reproduce this pass.')
    if bpy.context.window:bpy.context.window.scene=scene
    args.output.mkdir(parents=True,exist_ok=True);start=time.time()
    report={'revision':REVISION,'blender':bpy.app.version_string,'renderer':'Cycles','source_blend':Path(bpy.data.filepath).name,'visual_acceptance':'This build report is not visual approval. Read the subsequent fifty-camera review.'}
    geometry.collection(scene)
    print('QUALITY: material and weathering pass',flush=True)
    mats,records=weather_existing(scene);report['materials']=records
    mats['rock']=scene.objects['CSM_Continuous_stratified_mine_skin'].material_slots[0].material
    print('QUALITY: rebuild wooden carts',flush=True);report['carts']=geometry.new_carts(scene,mats)
    report['dented_panels']=geometry.roughen_panels(scene);report['surface_age']=geometry.surface_age(scene,mats);report['coarse_surface_repair']=gameplay_scale_surface_repair(scene,mats)
    print('QUALITY: close floor seams and settle actual fractured geometry',flush=True)
    report['floor_seams']=continuous_floor(scene)
    report['resources']=settle_resources(scene);report['collapse']=rebuild_collapse(scene,mats)
    report['natural_resource_placement']=natural_resources(scene)
    print('QUALITY: authored webs, rot, dark work lighting',flush=True)
    report['dressing']=all_dressing(scene,mats);report['excavation_practicals']=excavation_lamps(scene,mats)
    report['render_driven_refinements']=refine(scene,mats)
    report['cameras']=build_cameras(scene);report['camera_and_light_refinements']=review_corrections(scene,report['cameras']);set_review_state(scene,report['cameras'][0])
    scene['q50_revision']=REVISION;scene['q50_verified_art_status']='See the subsequent fifty-camera review and correction record.'
    import controls
    controls.register()
    text=bpy.data.texts.new('RUN_GULLET_CONTROLS.py');text.write((HERE/'controls.py').read_text());text.use_module=False
    scene['q50_source_dir']=str(HERE);scene['q50_cart_spec']='Wood planks; 1.10 m rim; 1.67 m body; 1.10 m rail gauge preserved.'
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=True
    scene.cycles.max_bounces=6;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3
    scene.render.resolution_x=1100;scene.render.resolution_y=688;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    for image in bpy.data.images:
        if image.source=='FILE' and image.has_data and not image.packed_file:image.pack()
    for path in sorted(HERE.glob('*.py')):
        text=bpy.data.texts.get('QUALITY_SOURCE_'+path.name) or bpy.data.texts.new('QUALITY_SOURCE_'+path.name)
        text.clear();text.write(path.read_text());text.use_module=False
    report['elapsed_build_seconds']=round(time.time()-start,2);report['mesh_objects']=sum(o.type=='MESH' for o in scene.objects);report['visible_triangles']=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in scene.objects if o.type=='MESH' and not o.hide_render and not o.get('q50_volumetric'))
    report['scene_saved']=str(args.output/'Gullet_Quality50.blend')
    (args.output/'build_report.json').write_text(json.dumps(report,indent=2));(args.output/'camera_manifest.json').write_text(json.dumps(report['cameras'],indent=2))
    shutil.copytree(HERE.parents[2]/'assets'/'pbr'/'quality50',args.output/'weathering_sources',dirs_exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output/'Gullet_Quality50.blend'),compress=True)
    print('QUALITY_BUILD_COMPLETE',json.dumps({k:report[k] for k in ['elapsed_build_seconds','mesh_objects','visible_triangles','blender']}),flush=True)
if __name__=='__main__':main()
