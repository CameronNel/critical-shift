import bpy,os,json,hashlib,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sid=os.environ.get('EXTERIOR_SECTION','compliance-dock');out=ROOT/'exteriors'/sid
requested_rev=os.environ.get('EXTERIOR_REVISION','R05')
current=ROOT/'exteriors/CURRENT.json'
rev=json.loads(current.read_text()).get(sid,requested_rev) if current.exists() and os.environ.get('EXTERIOR_USE_CURRENT','1')=='1' else requested_rev
source=out/f'exterior-{rev}.blend'
baseline=os.environ.get('EXTERIOR_BASELINE')=='1'
if baseline:source=ROOT/'sources'/sid/'module.blend';out.mkdir(parents=True,exist_ok=True)
before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='GPU'
if baseline:
 b=json.loads((ROOT/'sources'/sid/'survey.json').read_text())['all_visible_bounds'];cx=(b[0][0]+b[1][0])/2;cy=(b[0][1]+b[1][1])/2;h=b[1][2];w=b[1][0]-b[0][0];dep=b[1][1]-b[0][1];dist=max(w,dep)*1.25
 for name,loc,target in [('FRONT',(cx,b[0][1]-dist,max(2,h*.55)),(cx,cy,h*.45)),('OBLIQUE',(cx-dist,b[0][1]-dist,h+dist*.32),(cx,cy,h*.4)),('REVERSE',(cx+dist,b[1][1]+dist,h+dist*.32),(cx,cy,h*.4)),('DETAIL',(cx,b[0][1]-5,1.65),(cx,b[0][1],1.65))]:
  cu=bpy.data.cameras.new(name);ob=bpy.data.objects.new('BASELINE_'+name,cu);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();cu.lens=32;cu.clip_end=500
 world=bpy.data.worlds.new('Baseline neutral daylight');world.use_nodes=True;world.node_tree.nodes.get('Background').inputs[0].default_value=(.65,.72,.8,1);world.node_tree.nodes.get('Background').inputs[1].default_value=.45;scene.world=world
 ld=bpy.data.lights.new('Baseline sun','SUN');ld.energy=2;ld.angle=.15;ob=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(ob);ob.rotation_euler=(.4,-.5,-.5)
 scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.exposure=0
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='HIP';p.refresh_devices()
assert any(d.type=='HIP' for d in p.devices)
for d in p.devices:d.use=d.type=='HIP'
if hasattr(p,'use_hiprt'):p.use_hiprt=True
scene.render.use_persistent_data=False;scene.render.threads_mode='AUTO'
scene.cycles.samples=32;scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.04;scene.cycles.use_denoising=True;scene.cycles.denoiser='OPENIMAGEDENOISE'
if hasattr(scene.cycles,'denoising_use_gpu'):scene.cycles.denoising_use_gpu=True
scene.cycles.max_bounces=8;scene.cycles.sample_clamp_indirect=3
round_name=os.environ.get('EXTERIOR_ROUND','review-'+rev)
if round_name=='review-'+requested_rev:round_name='review-'+rev
dest=out/round_name;dest.mkdir(exist_ok=True)
records=[]
for name in (['FRONT','OBLIQUE'] if baseline else ['FRONT','OBLIQUE','REVERSE','DETAIL']):
 scene.camera=bpy.data.objects[('BASELINE_' if baseline else '')+name];scene.render.filepath=str(dest/(name+'.png'));bpy.ops.render.render(write_still=True)
 records.append({'camera':name,'sha256':hashlib.sha256((dest/(name+'.png')).read_bytes()).hexdigest()});print('EXTERIOR_RENDER_DONE',sid,name,flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
(dest/'manifest.json').write_text(json.dumps({'source_sha256':before,'engine':'Cycles HIP','samples':32,'saved_unchanged':True,'views':records},indent=2))
