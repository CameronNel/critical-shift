"""Four fixed native-material exterior views for user concept approval."""
import bpy,json,hashlib,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review';O.mkdir(exist_ok=True,parents=True)
D=O/os.environ.get('SPAWN_OUTPUT','baseline-A14');D.mkdir(exist_ok=True)
source=R/'blender'/os.environ.get('SPAWN_FILE','facility_master_A14_exterior.blend')
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
if '30_RETAINED_INTERIOR_LIGHTING' in bpy.data.collections:
 bpy.data.collections['30_RETAINED_INTERIOR_LIGHTING'].hide_render=True
 bpy.data.collections['30_RETAINED_INTERIOR_LIGHTING'].hide_viewport=True
sources=['01_LINKED_ROOMS','06_LINKED_EXTERIORS','CONNECTION_C01_RESCUE_COURTYARD','09_FINISHED_HORIZONTAL_CONNECTIONS','13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY','17_REACTOR_EXTERIOR_FINISH','20_ROOF_SERVICE_GEOMETRY','22_EXTERIOR_FINISH_GEOMETRY']
for n in sources:bpy.data.collections[n].hide_viewport=False;bpy.data.collections[n].hide_render=False
for n in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE','18_REACTOR_FINISH_VIEWPORT_CACHE','21_ROOF_SERVICE_VIEWPORT_CACHE','23_EXTERIOR_FINISH_VIEWPORT_CACHE']:
 bpy.data.collections[n].hide_viewport=True;bpy.data.collections[n].hide_render=True
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.eevee.use_raytracing=False;s.eevee.use_fast_gi=False
s.eevee.taa_render_samples=int(os.environ.get('SPAWN_SAMPLES',str(s.eevee.taa_render_samples)))
pool=s.eevee.bl_rna.properties['shadow_pool_size'].enum_items
s.eevee.shadow_pool_size=max([i.identifier for i in pool if i.identifier.isdigit()],key=int)
print('SHADOW_POOL',s.eevee.shadow_pool_size,flush=True)
s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100
cam=bpy.data.objects.new('SPAWN_EXTERIOR_LOCKED',bpy.data.cameras.new('SPAWN_EXTERIOR_LOCKED'));s.collection.objects.link(cam);s.camera=cam;cam.data.clip_end=300
views=[{'id':'01_COURTYARD','eye':[-25,29,6],'target':[-28,8,2],'lens':32}, {'id':'02_SOUTH','eye':[-28,-11,6],'target':[-28,6,2],'lens':30}, {'id':'03_EAST','eye':[-9,7,7],'target':[-28,8,2],'lens':24}, {'id':'04_TOP','eye':[-27,15,90],'target':[-27,15,0],'ortho_scale':52}]
if (O/'FIXED_CAMERAS.json').exists():views=json.loads((O/'FIXED_CAMERAS.json').read_text())['views']
(D/'MANIFEST.json').write_text(json.dumps({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'resolution':[1600,1100],'views':views,'engine':'EEVEE','raytracing':False,'approved_concept':'SPAWN_EXTERIOR_CONCEPT_02.png','rule':'Cameras loaded from locked FIXED_CAMERAS.json.'},indent=2))
manifest=json.loads((D/'MANIFEST.json').read_text());manifest.update(render_samples=s.eevee.taa_render_samples,shadow_ray_count=s.eevee.shadow_ray_count,shadow_step_count=s.eevee.shadow_step_count,exposure=s.view_settings.exposure,view_transform=s.view_settings.view_transform,look=s.view_settings.look,baked_probe_objects=[o.name for o in s.objects if o.type=='LIGHT_PROBE']);(D/'MANIFEST.json').write_text(json.dumps(manifest,indent=2))
for v in views:
 if os.environ.get('SPAWN_VIEWS') and v['id'] not in os.environ['SPAWN_VIEWS'].split(','):continue
 cam.location=v['eye'];cam.rotation_euler=(Vector(v['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if 'ortho_scale' in v else 'PERSP';cam.data.lens=v.get('lens',32)
 if 'ortho_scale' in v:cam.data.ortho_scale=v['ortho_scale']
 s.render.filepath=str(D/(v['id']+'.png'));bpy.ops.render.render(write_still=True);print('LOCKED_VIEW_DONE',v['id'],flush=True)
print('FOUR_VIEWS_COMPLETE',flush=True)
