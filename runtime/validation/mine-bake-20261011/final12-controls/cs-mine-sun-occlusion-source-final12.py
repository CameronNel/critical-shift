import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
root=Path('/workspace/critical-shift-spawn-runtime');out=Path('/tmp/cs-mine-sun-occlusion-source-final12');out.mkdir(exist_ok=True);scene=bpy.context.scene;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();views=json.loads((root/'runtime/out/mine-bake-audit/blender-views.json').read_text())['views'];eye,aim,lens=views['R39_04_SHED_FRONT'];eye=Vector(eye);q=(Vector(aim)-eye).to_track_quat('-Z','Y');vfov=39.760704040527344;aspect=1440/810
suns=[]
for inst in dg.object_instances:
 if inst.object.type=='LIGHT' and inst.object.data.type=='SUN':
  matrix=inst.matrix_world.copy();suns.append({'name':inst.object.name,'direction':matrix.to_quaternion()@Vector((0,0,1)),'energy':inst.object.data.energy,'color':list(inst.object.data.color)})
records=[]
for x,y in [(330,280),(400,350),(540,340),(750,320),(890,220),(800,570)]:
 ray=q@Vector(((2*x/1440-1)*math.tan(math.radians(vfov/2))*aspect,(1-2*y/810)*math.tan(math.radians(vfov/2)),-1));ray.normalize();hit=scene.ray_cast(dg,eye,ray,distance=300)
 if not hit[0]:continue
 _,point,normal,face,obj,matrix=hit;r={'pixel':[x,y],'object':obj.name,'point':list(point),'normal':list(normal),'sourceShadowVisible':obj.visible_shadow,'suns':[]}
 for sun in suns:
  position=point+normal*.002;skipped=[];occlusion=None
  for _ in range(64):
   h=scene.ray_cast(dg,position,sun['direction'],distance=800)
   if not h[0]:break
   if h[4].visible_shadow and not h[4].hide_render:occlusion={'object':h[4].name,'point':list(h[1]),'distanceFromReceiver':(h[1]-point).length};break
   skipped.append(h[4].name);position=h[1]+sun['direction']*.002
  r['suns'].append({'name':sun['name'],'energy':sun['energy'],'color':sun['color'],'toLight':list(sun['direction']),'cosine':normal.dot(sun['direction']),'occluder':occlusion,'skippedShadowExcluded':skipped})
 records.append(r)
source=root/'runtime/out/spawn-export-source/combined-runtime-source.blend';(out/'audit.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cameraEye':list(eye),'cameraVFov':vfov,'records':records,'limit':'Centre-ray geometric occlusion with explicit source shadow flags; not finite-angle lighting integration'},indent=2)+'\n');print('CS_SOURCE_SUN_OCCLUSION_AUDIT_OK',len(records),flush=True)
