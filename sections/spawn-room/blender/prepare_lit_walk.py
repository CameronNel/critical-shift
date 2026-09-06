"""Bake a separate EEVEE walking copy from the authored Cycles source.

Blender 5.2: named room volumes, local indirect light, no camera-dependent fill rig.
The source is preserved. Source/checksum/render evidence is written beside the review.
"""
import bpy,sys,json,hashlib,argparse,time,math
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--review-id',default='tactile-walk-01');p.add_argument('--no-bake',action='store_true');p.add_argument('--cameras',default='VALIDATE_Spawn,VALIDATE_LockerDoor,VALIDATE_BriefingDoor')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=HERE.parent/'production/renders/review'/a.review_id;out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;source=Path(bpy.data.filepath);source_hash=hashlib.sha256(source.read_bytes()).hexdigest();t=time.time()
s.render.engine='BLENDER_EEVEE';s.eevee.taa_samples=16;s.eevee.taa_render_samples=64
s.eevee.use_raytracing=True;s.eevee.use_fast_gi=True;s.eevee.fast_gi_method='AMBIENT_OCCLUSION_ONLY'
s.eevee.shadow_pool_size='512'
# EEVEE transmission is opt-in; the authored Cycles glass otherwise looks opaque.
bpy.data.materials['glass'].use_raytrace_refraction=True
# A bounded upward fill represents diffuse floor bounce in the interactive renderer.
# It is intentionally separate from the Cycles source; probes alone left ceilings black.
for name,pos,size,power in [('HALL',(0,4.6,.25),3.0,38),('BRIEFING',(-4.6,3.55,.25),3.7,30),('LOCKER',(5.0,4,.25),4.8,62),('SERVICE',(0,10.9,.25),2.3,15)]:
    d=bpy.data.lights.new('EEVEE_floor_bounce_'+name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=(.78,.83,.76);d.use_shadow=False
    o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler.x=math.pi
    o['purpose']='Realtime approximation of diffuse light reflected from the floor'
specs=[('HALL',(0,4.35,1.7),(1.50,4.55,1.48),(5,14,5)),
       ('BRIEFING',(-4.6,3.55,1.7),(2.40,2.34,1.48),(8,8,5)),
       ('LOCKER',(4.97,4,1.9),(2.90,3.08,1.68),(10,10,6)),
       ('SERVICE',(0,10.87,1.7),(1.5,1.16,1.48),(5,5,5))]
if not a.no_bake:
    for name,pos,scale,res in specs:
        d=bpy.data.lightprobes.new('BOUNCE_'+name,'VOLUME');d.resolution_x,d.resolution_y,d.resolution_z=res
        d.bake_samples=512;d.surfel_density=12;d.capture_distance=5;d.capture_world=True
        o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=pos;o.scale=scale
    bpy.context.view_layer.update()
    print('BAKING_ROOM_INDIRECT',flush=True)
    result=bpy.ops.object.lightprobe_cache_bake(subset='ALL');assert 'FINISHED' in result,result
    print('ROOM_INDIRECT_BAKED',flush=True)
cam=bpy.data.objects['VALIDATE_Spawn'];s.camera=cam
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type!='VIEW_3D':continue
        space=area.spaces.active;space.shading.type='MATERIAL';space.shading.use_scene_lights=True;space.shading.use_scene_world=True;space.overlay.show_overlays=False
        rv=space.region_3d;rv.view_perspective='PERSP';rv.view_rotation=cam.matrix_world.to_quaternion();rv.view_distance=1
        rv.view_location=cam.matrix_world.translation+rv.view_rotation@Vector((0,0,-1))
        space.lens=cam.data.lens;space.clip_start=.03
s['walking_copy']='EEVEE: four baked room volumes, bounded floor-bounce approximation. F3 > Walk Navigation.'
s['source_sha256']=source_hash
destination=HERE/'spawnroom_tactile_walk.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
for name in a.cameras.split(','):
    s.camera=bpy.data.objects[name];s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
report={'source':str(source),'source_sha256':source_hash,'output':str(destination),'output_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'engine':s.render.engine,'volumes':len(specs),'bake_samples':512,'render_samples':64,'viewport_samples':16,'time_seconds':time.time()-t}
camera_manifest={o.name:{'position':list(o.location),'rotation':list(o.rotation_euler),'lens':o.data.lens} for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('VALIDATE_')}
(out/'cameras.json').write_text(json.dumps(camera_manifest,indent=2))
(out/'walk_provenance.json').write_text(json.dumps(report,indent=2))
print('LIT_WALK_COMPLETE',json.dumps(report),flush=True)
