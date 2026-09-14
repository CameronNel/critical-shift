"""R16 non-RT real-time lighting: baked volume probes, cleaner shadow maps and AA."""
import bpy,json,hashlib,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_spawn_concept02_R15.blend'),load_ui=False)
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';e=s.eevee
e.use_raytracing=False;e.use_fast_gi=False;e.taa_render_samples=256;e.taa_samples=64;e.shadow_pool_size='2048';e.shadow_ray_count=4;e.shadow_step_count=12;e.use_shadow_jitter_viewport=True;e.shadow_resolution_scale=1
for ob in s.objects:
 if ob.type=='LIGHT' and not ob.library:
  if ob.name.startswith('S01 ') and ('sky fill' in ob.name or 'broad exterior skylight' in ob.name):ob.data.energy=0
  elif not ob.name.startswith('INTERIOR_'):
   if ob.data.library:ob.data=ob.data.copy()
   ob.data.use_shadow_jitter=True
   ob.data.shadow_jitter_overblur=2
interior=bpy.data.collections['30_RETAINED_INTERIOR_LIGHTING'];interior.hide_render=True;interior.hide_viewport=True
for n in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE','18_REACTOR_FINISH_VIEWPORT_CACHE','21_ROOF_SERVICE_VIEWPORT_CACHE','23_EXTERIOR_FINISH_VIEWPORT_CACHE']:
 bpy.data.collections[n].hide_viewport=True;bpy.data.collections[n].hide_render=True
col=bpy.data.collections.new('32_SPAWN_BAKED_DAYLIGHT');s.collection.children.link(col)
p=bpy.data.lightprobes.new('Spawn courtyard baked indirect','VOLUME');p.resolution_x=20;p.resolution_y=24;p.resolution_z=8;p.bake_samples=512;p.surfel_density=12;p.capture_world=True;p.capture_indirect=True;p.capture_emission=True;p.capture_distance=45
ob=bpy.data.objects.new(p.name,p);col.objects.link(ob);ob.location=(-26,12,4);ob.scale=(18,23,6)
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.context.view_layer.update()
print('BAKE_START',flush=True);t=time.perf_counter();result=bpy.ops.object.lightprobe_cache_bake(subset='ACTIVE');elapsed=time.perf_counter()-t;print('BAKE_RESULT',result,elapsed,flush=True)
if 'FINISHED' not in result:raise RuntimeError('Baked light cache not completed')
interior.hide_render=False;interior.hide_viewport=False
s.name='FACILITY_SPAWN_CONCEPT02_R16';s['realtime_quality']='Non-RT EEVEE, baked diffuse light probe, 256 offline AA samples, 64 viewport samples, jittered shadow maps'
dest=R/'blender/facility_spawn_concept02_R16.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
b=json.loads((O/'BUILD_R15.json').read_text());b.update(revision='R16',file=str(dest),render_quality={'engine':'EEVEE','raytracing':False,'fast_gi':False,'render_samples':256,'viewport_samples':64,'shadow_pool_mb':2048,'shadow_samples':4,'shadow_steps':12,'baked_probe_grid':[20,24,8],'bake_samples':512,'bake_seconds':elapsed,'bake_result':list(result),'artificial_sky_fill_lights_disabled':True});(O/'BUILD_R16.json').write_text(json.dumps(b,indent=2));print('R16_SAVED',flush=True)
