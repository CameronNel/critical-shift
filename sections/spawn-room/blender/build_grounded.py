"""Headless source build; validation slice is deliberately the default scope."""
import bpy, sys, json, argparse, math
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import grounded_kit as k

def camera(name,p,target,lens=30):
    d=bpy.data.cameras.new(name);d.lens=lens;d.clip_start=.03;d.clip_end=150
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=p
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o

def settings(samples):
    s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=samples;s.cycles.use_denoising=True
    s.cycles.max_bounces=8;s.cycles.diffuse_bounces=4;s.cycles.transmission_bounces=6
    s.render.resolution_x=1440;s.render.resolution_y=900;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.render.film_transparent=False
    s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.3
    world=bpy.data.worlds.new('Enclosed workplace ambient');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.5,.57,.65,1)
    world.node_tree.nodes['Background'].inputs[1].default_value=.13;s.world=world
    s.render.threads_mode='FIXED';s.render.threads=8

def slice_scene(stage):
    f=k.floor('SLICE_floor',-3.1,3.1,-5.8,.4)
    w1=k.wall('SLICE_wall_left',-3.1,-2.4,0)
    w2=k.wall('SLICE_wall_main',-1.10,3.1,0)
    k.box('SLICE_door_lintel',(-1.75,.08,2.80),(1.3,.16,1.2),'wall',.001)
    ceil=k.box('SLICE_ceiling',(0,-2.7,3.48),(6.2,6.2,.16),'wall',.001)
    k.door('SLICE_personnel',(-1.75,0,0))
    bay,feet=k.bay('SLICE_station',(0,-.302,0))
    k.support(bay,f,'WORLD_-Z',feet)
    bench,feet=k.bench('SLICE_bench',(1.91,-.42,0));k.support(bench,f,'WORLD_-Z',feet)
    light,anchors=k.practical('SLICE_practical',(.15,-1.16,3.4),power=240,length=1.7)
    k.support(light,ceil,'WORLD_+Z',anchors,'CEILING')
    pipe,anchors=k.utility('SLICE_utility',(-2.78,0,0));k.support(pipe,w1,'LOCAL_+Y',anchors,'WALL')
    if stage>=2:
        o=k.mug('SLICE_mug',(2.39,-.45,.45));k.support(o,bpy.data.objects['SLICE_bench_laminate_slat.001'],'WORLD_-Z',[(0,0,0)])
        o=k.clipboard('SLICE_clipboard',(1.45,-.44,.45),-.12);k.support(o,bpy.data.objects['SLICE_bench_laminate_slat.001'],'WORLD_-Z',[(0,0,0)])
        o=k.use_marks('SLICE_threshold_traffic',(-1.70,-.30,0));k.support(o,f,'WORLD_-Z',[(0,0,.0007)])
        o=k.use_marks('SLICE_boot_traffic',(.05,-1.04,0));k.support(o,f,'WORLD_-Z',[(0,0,.0007)])
        o=k.use_marks('SLICE_seat_contact',(2.02,-.56,.45));k.support(o,bpy.data.objects['SLICE_bench_laminate_slat'],'WORLD_-Z',[(0,0,.0007)])
        replacement=k.box('SLICE_replaced_tile',(-.5,-1.5,.0003),(.991,.991,.0006),'floor4',0)
        k.support(replacement,f,'WORLD_-Z',[(0,0,-.0003)])
    camera('SLICE_Gameplay',(1.7,-5.7,1.63),(0,-.05,1.51),28)
    camera('SLICE_Detail',(1.1,-2.60,1.63),(.0,-.27,1.18),42)
    camera('SLICE_Reverse',(-2.7,-3.9,1.63),(.60,-.1,1.35),32)
    return ['SLICE_Gameplay','SLICE_Detail','SLICE_Reverse']

def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',type=int,default=3);p.add_argument('--review-id',default='slice-01');p.add_argument('--samples',type=int,default=40);p.add_argument('--cameras',default='');p.add_argument('--scope',default='slice');p.add_argument('--no-render',action='store_true')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    review=(HERE.parent/'production/REFERENCE_REVIEW.md').read_text(encoding='utf-8')
    assert 'Reference review complete: **YES**' in review,'Complete reference review before modeling'
    bpy.ops.wm.read_factory_settings(use_empty=True);k.materials(args.stage);settings(args.samples)
    import worn_surfaces
    if args.stage>=3:worn_surfaces.materials(k)
    for name in ['CS_SUPPORT_REQUIRED','CS_WALL_DRESSING','CS_FLOOR_DRESSING','CS_CEILING_DRESSING']:k.collection(name)
    if args.scope=='slice':names=slice_scene(args.stage)
    else:
        import grounded_room
        names=grounded_room.build()
    if args.stage>=3:worn_surfaces.geometry(k,args.scope)
    s=bpy.context.scene;s.camera=bpy.data.objects[names[0]]
    s['build_scope']=args.scope;s['art_direction']='Grounded stylized semi-realism';s['reference_base']='8603063';s['review_id']=args.review_id
    if args.scope=='room':
        # Organize source independently of overlapping support-audit collections.
        for o in list(bpy.data.objects):
            root=o
            while root.parent:root=root.parent
            name=root.name
            category=('REVIEW_CAMERAS' if o.type=='CAMERA' else 'GAMEPLAY_HOOKS' if name.startswith(('SPAWN_','AUDIO_','INTERACT_')) else 'PPE_STATIONS' if name.startswith('PPE_') else 'INTEGRITY_MACHINE' if name.startswith('INTEGRITY') else 'BRIEFING_ROOM' if name.startswith('BRIEFING') else 'LOCKER_ROOM' if name.startswith('LOCKER') else 'FACILITY_HALL')
            c=k.collection(category)
            if o.name not in c.objects:c.objects.link(o)
            default=bpy.data.collections.get('Collection')
            if default and o.name in default.objects:default.objects.unlink(o)
        for img in bpy.data.images:
            if img.source=='FILE' and not img.filepath.startswith('//'):
                img.filepath='//../assets/portraits/'+Path(img.filepath).name
    bpy.context.view_layer.update()
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_perspective='CAMERA'
                # Open without eagerly compiling the full material-preview GPU workload.
                area.spaces.active.shading.type='SOLID'
                area.spaces.active.shading.color_type='MATERIAL'
                area.spaces.active.overlay.show_overlays=False
    output=HERE/('spawnroom_style_slice.blend' if args.scope=='slice' else 'spawnroom.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
    out=HERE.parent/'production/renders/review'/args.review_id;out.mkdir(parents=True,exist_ok=True)
    import validate_contacts
    result=validate_contacts.main()
    if args.scope=='room':
        import validate_grounded
        result=max(result,validate_grounded.main(out/'objective_validation.json'))
    report=HERE.parent/'production/contact_validation.json';(out/'contact_validation.json').write_bytes(report.read_bytes())
    manifest={n:{'position':list(bpy.data.objects[n].location),'rotation':list(bpy.data.objects[n].rotation_euler),'lens':bpy.data.objects[n].data.lens} for n in names}
    (out/'cameras.json').write_text(json.dumps(manifest,indent=2))
    inventory={'objects':len(bpy.data.objects),'mesh_datablocks':len(bpy.data.meshes),'source_vertices_before_modifiers':sum(len(m.vertices) for m in bpy.data.meshes),'source_polygons_before_modifiers':sum(len(m.polygons) for m in bpy.data.meshes),'materials':len(bpy.data.materials),'packed_images':[i.name for i in bpy.data.images if i.packed_file],'runtime_note':'Editable authoring source. Engine export, LODs, rigging and draw-call optimization are separate handoff work.'}
    (out/'source_inventory.json').write_text(json.dumps(inventory,indent=2))
    if not args.no_render:
        for name in (args.cameras.split(',') if args.cameras else names):
            s.camera=bpy.data.objects[name];s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    if result:raise RuntimeError('Geometry or contact validation failed; review renders retained for diagnosis.')
    print('GROUNDED_BUILD_COMPLETE',str(output))

if __name__=='__main__':main()
