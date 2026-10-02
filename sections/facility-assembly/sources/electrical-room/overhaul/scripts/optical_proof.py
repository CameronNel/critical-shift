"""Read-only glazing experiment with an existing detailed fuse as contrast specimen."""
import bpy,sys,json,hashlib,time,os,argparse
from pathlib import Path
from mathutils import Vector,Matrix
p=argparse.ArgumentParser();p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
source=Path(bpy.data.filepath);sha=hashlib.sha256(source.read_bytes()).hexdigest();scene=bpy.context.scene
temporary=[];shift=Vector((-1.86,.18,1.96))-Vector((-4.18,13.73,1.107))
for o in list(scene.objects):
    if o.get('cs_assembly')!='EOH | Spare fuses' or o.type not in {'MESH','FONT'}:continue
    points=[o.matrix_world@Vector(p) for p in o.bound_box]
    cy=(min(p.y for p in points)+max(p.y for p in points))/2
    if abs(cy-13.73)>.12:continue
    copy=o.copy();copy.name='OPTICAL SPECIMEN | '+o.name;copy.parent=None
    copy.matrix_world=Matrix.Translation(shift)@o.matrix_world
    scene.collection.objects.link(copy);temporary.append(copy.name)
assert temporary,'Detailed original fuse specimen not found'
d=bpy.data.cameras.new('Optical proof camera');cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam)
cam.location=(-1.65,2.10,1.98);cam.rotation_euler=(Vector((-1.86,.30,1.95))-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=70;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.render.threads_mode='FIXED';scene.render.threads=4
scene.cycles.samples=24;scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.025
scene.cycles.use_denoising=True;scene.cycles.denoiser='OPENIMAGEDENOISE';scene.cycles.seed=73
scene.cycles.max_bounces=8;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3;scene.cycles.transmission_bounces=6
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
pane=bpy.data.objects['Door wired vision glass.001']
bs=pane.material_slots[0].material.node_tree.nodes.get('Principled BSDF')
bpy.context.view_layer.update()
assert (cam.matrix_world.translation-cam.location).length<1e-6
report={'source_sha256':sha,'purpose':'Controlled optical experiment only; duplicated existing fuse behind parked pane is temporary and is never saved as room dressing.',
        'temporary_specimen_objects':temporary,'specimen_translation':list(shift),'camera_matrix':sum((list(r) for r in cam.matrix_world),[]),
        'lens':d.lens,'samples':24,'transmission_weight':bs.inputs['Transmission Weight'].default_value,
        'views':[]}
for name,hidden in [('OP01_Through_Glass',False),('OP02_No_Pane_Control',True)]:
    pane.hide_render=hidden;scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    assert sum((list(r) for r in cam.matrix_world),[])==report['camera_matrix']
    report['views'].append({'file':name+'.png','pane_hidden':hidden,'sha256':hashlib.sha256(Path(scene.render.filepath).read_bytes()).hexdigest()})
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
report['saved_source_unchanged']=True
(out/'manifest.json').write_text(json.dumps(report,indent=2));print('OPTICAL_PROOF_COMPLETE',flush=True)
sys.stdout.flush();sys.stderr.flush();os._exit(0)
