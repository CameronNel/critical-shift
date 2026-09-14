"""Cold validation of the batched Blender inspection artifact."""
import bpy,json,time,hashlib,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review';rev=os.environ.get('SPAWN_REV','R15');p=R/'blender'/('facility_spawn_material_preview_'+rev+'.blend')
t=time.perf_counter();bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False);elapsed=time.perf_counter()-t;s=bpy.context.scene
col=bpy.data.collections['27_MATERIAL_PREVIEW'];groups=[ob.get('preview_source') for ob in col.objects];missing=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.users and not im.packed_file and not Path(bpy.path.abspath(im.filepath,library=im.library)).exists():missing.append(im.name)
report={'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'cold_load_seconds':elapsed,'merged_groups':len(col.objects),'spawn_exterior_group':'EXTERIOR_INSTANCE_spawn-room' in groups,'new_spawn_details_group':'29_SPAWN_APPROVED_EXTERIOR' in groups,'native_spawn_details_hidden':bpy.data.collections['29_SPAWN_APPROVED_EXTERIOR'].hide_viewport,'missing_used_images':missing,'engine':s.render.engine,'raytracing':s.eevee.use_raytracing,'render_samples':s.eevee.taa_render_samples,'viewport_samples':s.eevee.taa_samples,'shadow_resolution_scale':s.eevee.shadow_resolution_scale,'baked_probes':[o.name for o in s.objects if o.type=='LIGHT_PROBE'],'packed_images':sum(bool(i.packed_file) for i in bpy.data.images),'viewport_fps':'UNVERIFIED','unity_runtime':'UNVERIFIED'}
report['pass']=report['spawn_exterior_group'] and report['new_spawn_details_group'] and report['native_spawn_details_hidden'] and not missing and not report['raytracing']
(O/('PREVIEW_VALIDATION_'+rev+'.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
