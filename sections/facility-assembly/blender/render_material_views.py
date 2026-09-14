"""Cycles HIP material renders; temporary neutral daylight, master untouched."""
import ast, bpy, hashlib, json, math, os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'blender'/os.environ.get('ASSEMBLY_MASTER','facility_master.blend')
before=hashlib.sha256(source.read_bytes()).hexdigest()
tree=ast.parse((ROOT/'blender/render_connections.py').read_text())
views=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='views' for t in n.targets))
views.append(('E03_COMPLETE_EXTERIOR','All twelve assembled sections with connecting space reserved',(-155,-170,185),(-9,10,0),45))
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene
scene.render.engine='CYCLES'
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='HIP';prefs.refresh_devices()
assert any(d.type=='HIP' for d in prefs.devices),'HIP GPU unavailable'
for d in prefs.devices:d.use=d.type=='HIP'
if hasattr(prefs,'use_hiprt'):prefs.use_hiprt=True
scene.cycles.device='GPU';scene.render.threads_mode='AUTO'
scene.render.use_persistent_data=False
samples=int(os.environ.get('ASSEMBLY_RENDER_SAMPLES','32'))
scene.cycles.samples=samples;scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.04
scene.cycles.use_denoising=True;scene.cycles.denoiser='OPENIMAGEDENOISE'
if hasattr(scene.cycles,'denoising_use_gpu'):scene.cycles.denoising_use_gpu=True
scene.cycles.max_bounces=10;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3
scene.cycles.transmission_bounces=8;scene.cycles.transparent_max_bounces=8;scene.cycles.sample_clamp_indirect=3
scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=0
world=bpy.data.worlds.new('REVIEW_ONLY_Neutral_Daylight');world.use_nodes=True
world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.65,.72,.8,1)
world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.45;scene.world=world
light=bpy.data.lights.new('REVIEW_ONLY_Sun','SUN');light.energy=2;light.angle=math.radians(12)
sun=bpy.data.objects.new(light.name,light);scene.collection.objects.link(sun);sun.rotation_euler=(.45,-.55,-.5)
bpy.data.collections['04_PLANNING_LABELS'].hide_render=True
out=ROOT/'production'/os.environ.get('ASSEMBLY_RENDER_DIR','material-views');out.mkdir(exist_ok=True)
manifest={'source_sha256':before,'master_saved':False,'renderer':'Cycles HIP','samples':samples,'lighting':'Source practical lights plus temporary neutral exterior world and sun; provisional review lighting','views':[]}
selected=os.environ.get('ASSEMBLY_RENDER_VIEWS','J04_REACTOR_TURBINE,E02_FACILITY_EXTERIOR').split(',')
for name,caption,loc,target,lens in sorted(views,key=lambda v:selected.index(v[0]) if v[0] in selected else 999):
 if name not in selected:continue
 data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob)
 ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
 data.lens=lens;data.clip_start=.05;data.clip_end=500;scene.camera=ob
 scene.render.filepath=str(out/f'{name}.png');bpy.ops.render.render(write_still=True)
 manifest['views'].append({'id':name,'caption':caption,'location':loc,'target':target,'lens_mm':lens,'sha256':hashlib.sha256((out/f'{name}.png').read_bytes()).hexdigest()})
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2));print('MATERIAL_VIEW_DONE',name,flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
print('MATERIAL_VIEWS_COMPLETE_MASTER_UNCHANGED',flush=True)
