"""Headless source entrypoint. Refuses interactive Blender to protect other work."""
import sys, json, time, argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
import config, materials, geometry as g, architecture, cart, machines, dressing, cameras, states, validate

def manifest():
    doc={'units':'metres','machine_order':config.MACHINES,'material_chain':config.CHAIN,'machines':[],'markers':[],'moving_parts':[],'state_presets':states.PRESETS,'runtime_boundary':'Unity owns interactions, collision response, networked objects, simulation, audio, VFX, optimization and material translation.'}
    for obj in bpy.context.scene.objects:
        if obj.get('machine_id'):doc['machines'].append({'name':obj.name,'id':obj['machine_id'],'collection':[c.name for c in obj.users_collection]})
        if obj.name.startswith('INT_'):doc['markers'].append({'name':obj.name,'position':list(obj.matrix_world.translation),'properties':{k:obj[k] for k in obj.keys() if k not in ['_RNA_UI']}})
        if obj.get('moving_part') or obj.get('component')=='cart_tip_pivot':doc['moving_parts'].append({'name':obj.name,'pivot_world':list(obj.matrix_world.translation),'parent':obj.parent.name if obj.parent else None,'role':obj.get('moving_part',obj.get('component'))})
    (config.PRODUCTION/'machine_manifest.json').write_text(json.dumps(doc,indent=2),encoding='utf-8')

def render_batch(directory,names):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    for name in names:
        bpy.context.scene.camera=bpy.data.objects[name]
        bpy.context.scene.render.filepath=str(directory/(name+'.png'))
        print('RENDER_CAMERA',name,flush=True);bpy.ops.render.render(write_still=True)

def main():
    if not bpy.app.background:raise RuntimeError('Run in a new --background --factory-startup Blender process; never the occupied GUI.')
    parser=argparse.ArgumentParser();parser.add_argument('--render',choices=['all','none'],default='all');parser.add_argument('--pass-name',default='review');parser.add_argument('--samples',type=int,default=24);parser.add_argument('--states',action='store_true');parser.add_argument('--cold-start',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    start=time.time();config.PRODUCTION.mkdir(parents=True,exist_ok=True)
    if args.cold_start:
        states.recover_materials();states.apply('idle')
        report=validate.run(config.PRODUCTION/'cold_start_report.json',check_saved=True)
        if args.render=='all':render_batch(config.PRODUCTION/'renders'/'cold-start',config.CAMERAS)
        report['rendered_cameras']=list(config.CAMERAS) if args.render=='all' else [];report['elapsed_seconds']=time.time()-start
        (config.PRODUCTION/'cold_start_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.name='CRITICAL_SHIFT_REFINERY';scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    for name in config.COLLECTIONS:g.collection('REFINERY_'+name)
    materials.build();architecture.build();cart.build();architecture.feeder();machines.build();dressing.build();cameras.build()
    scene.cycles.samples=args.samples
    # Receiving operator station remains on the accessible east side of the cradle.
    with g.use('MACHINE_RECEIVING',bpy.data.objects['ROOT_RECEIVING']):
        for role,p in {'CART_DOCK':(-5.15,-3.65,.2),'HOPPER':(-5.15,-1.6,.65),'SPILL_CLEANUP':(-4.0,-2.35,.2)}.items():g.marker('RECEIVING',role,p)
        g.control_panel('RECEIVING',-3.70,-2.40,1.10,['BRAKE','LATCH','TIP','SIZE_GATE'],.63)
        foot=g.box('Receiving_control_foot',(-3.7,-2.38,.035),(.31,.3,.07),'steel');g.support(foot,'Floor','WORLD_-Z',[(-3.7,-2.38,0)])
        g.rod('Receiving_control_pedestal',(-3.7,-2.38,.07),(-3.7,-2.38,.88),.045,'darksteel')
        gate=g.empty('Hopper_size_gate_PIVOT',(-5.15,-.89,.73),moving_part='adjustable size gate',axis='Z')
        with g.use('MACHINE_RECEIVING',gate):
            for x in [-5.55,-5.35,-5.15,-4.95,-4.75]:g.rod('Hopper_size_gate_finger',(x,-1.38,.50),(x,-.88,.74),.024,'steel')
        # Flush rail heads align with cradle; flange slots remain below the tread.
        for y in [-4.2,-3.1]:g.box('Mine_approach_rail',(-7.50,y,.135),(2.02,.09,.05),'steel',.004)
    states.build();bpy.context.view_layer.update();manifest()
    try:report=validate.run()
    except Exception:
        bpy.ops.wm.save_as_mainfile(filepath=str(config.PRODUCTION/'checkpoints'/'Refinery_diagnostic.blend'))
        raise
    scene.camera=bpy.data.objects['CAM_ENTRY'];scene['source_entrypoint']='build_refinery.py';scene['production_status']='One coordinated production pass; formal four-cycle acceptance not claimed'
    bpy.ops.wm.save_as_mainfile(filepath=str(config.BLEND))
    validate.run(check_saved=True)
    if args.render=='all':render_batch(config.PRODUCTION/'renders'/args.pass_name,config.CAMERAS)
    if args.states:
        directory=config.PRODUCTION/'renders'/'states';directory.mkdir(parents=True,exist_ok=True)
        scene.render.resolution_percentage=75
        for name,(cam,_) in states.PRESETS.items():
            states.apply(name);scene.camera=bpy.data.objects[cam];scene.render.filepath=str(directory/(name+'.png'));bpy.ops.render.render(write_still=True)
        states.apply('idle')
        scene.render.resolution_percentage=100
    (config.PRODUCTION/'build_report.json').write_text(json.dumps({'status':'PASS','elapsed_seconds':time.time()-start,'blender_version':bpy.app.version_string,'source':str(Path(__file__).resolve()),'output':str(config.BLEND),'render_batch':args.pass_name,'samples':args.samples},indent=2),encoding='utf-8')
    print('REFINERY_BUILD_COMPLETE',time.time()-start,flush=True)

if __name__=='__main__':main()
