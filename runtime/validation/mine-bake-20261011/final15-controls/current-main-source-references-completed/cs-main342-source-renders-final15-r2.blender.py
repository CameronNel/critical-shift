from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
root=Path('/tmp/cs-compact-main342-final14');out=Path('/tmp/cs-main342-source-renders-final15-r2')
assert not out.exists();out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
config=json.loads((root/'map-config.json').read_text());scene=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==root/'combined-runtime-source.blend'
assert config['map_commit']=='342af0003fec9dbe80b5acb40d1477c23b5a3169'
assert all(sha(root/'map'/r['path'])==r['sha256'] for r in config['sources'])
views=json.loads(Path('/workspace/critical-shift-spawn-runtime/runtime/out/mine-bake-audit/cameras.json').read_text())['views']
assert len(views)==3 and {v['name'] for v in views}=={'R39_01_PORTAL_APPROACH','R39_02_TUNNEL','R39_04_SHED_FRONT'}
translation=Vector(next(r[3] for r in config['rooms'] if r[0]=='mine'))
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=64;scene.cycles.use_denoising=True
scene.cycles.use_adaptive_sampling=False;scene.cycles.seed=0
scene.render.resolution_x=1440;scene.render.resolution_y=810;scene.render.resolution_percentage=100
scene.render.pixel_aspect_x=1;scene.render.pixel_aspect_y=1
records=[]
for view in views:
 name=view['name'];camera=bpy.data.objects.new('Current-source validation '+name,bpy.data.cameras.new(name));scene.collection.objects.link(camera)
 forward=Vector(view['forward']).normalized();up=Vector(view['up']).normalized();right=forward.cross(up).normalized()
 camera.location=translation+Vector(view['position']);camera.rotation_euler=Matrix((right,up,-forward)).transposed().to_quaternion().to_euler()
 camera.data.sensor_fit='HORIZONTAL';camera.data.sensor_width=36
 camera.data.lens=36/(2*math.tan(math.radians(view['verticalFov'])/2)*(1440/810));camera.data.clip_start=.05;camera.data.clip_end=250;scene.camera=camera
 scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_depth='32';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.exr_codec='ZIP'
 scene.render.filepath=str(out/(name+'-linear.exr'));bpy.ops.render.render(write_still=True)
 scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_depth='8';scene.render.image_settings.color_mode='RGB'
 bpy.data.images['Render Result'].save_render(str(out/(name+'.png')),scene=scene)
 q=camera.rotation_euler.to_quaternion()
 records.append({'name':name,'camera':view,'worldPosition':list(camera.location),'worldQuaternionWXYZ':list(q),
  'worldForward':list(q@Vector((0,0,-1))),'worldUp':list(q@Vector((0,1,0))),
  'verticalFov':math.degrees(2*math.atan(math.tan(camera.data.angle_x/2)*810/1440)),
  'nearClip':camera.data.clip_start,'farClip':camera.data.clip_end,
  'pngSha256':sha(out/(name+'.png')),'hdrSha256':sha(out/(name+'-linear.exr'))})
 print('CS_CURRENT_MAIN_SOURCE_FRAME',name,flush=True)
assert all(sha(root/'map'/r['path'])==r['sha256'] for r in config['sources'])
(out/'provenance.json').write_text(json.dumps({'status':'CompletedCurrentCompactSourceRenders_NotUnityAcceptance','mapCommit':config['map_commit'],'sourceSha256':sha(root/'combined-runtime-source.blend'),'configSha256':sha(root/'map-config.json'),'sourceRecords':config['sources'],'blenderVersion':bpy.app.version_string,'samples':64,'adaptiveSampling':False,'seed':0,'denoised':True,'dimensions':[1440,810],'pixelAspect':[1,1],'sourceView':{'transform':scene.view_settings.view_transform,'look':scene.view_settings.look,'exposure':scene.view_settings.exposure,'gamma':scene.view_settings.gamma},'views':records,'limits':['Source graph and authored lights intact; cameras/output settings changed only in disposable process','No canonical Source save or Unity/98 acceptance']},indent=2)+'\n')
