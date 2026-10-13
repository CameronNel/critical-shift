import bpy,math,json,hashlib,numpy as np
from pathlib import Path
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;out=Path('/tmp/cs-mine-probe-camera-only-preflight-final12');out.mkdir(exist_ok=True)
world=bpy.data.worlds.new('Known uniformlinearWorld');world.use_nodes=True;background=world.node_tree.nodes.get('Background');background.inputs['Color'].default_value=(.25,.5,.75,1);background.inputs['Strength'].default_value=1;scene.world=world
bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=.01);sphere=bpy.context.object
for p in sphere.data.polygons:p.use_smooth=True
m=bpy.data.materials.new('WhiteLambert');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();d=nt.nodes.new('ShaderNodeBsdfDiffuse');d.inputs['Color'].default_value=(1,1,1,1);d.inputs['Roughness'].default_value=0;o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(d.outputs[0],o.inputs['Surface']);sphere.data.materials.append(m)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=64;scene.cycles.use_denoising=False;scene.render.bake.use_clear=True;scene.render.bake.margin=0;scene.render.bake.use_selected_to_active=False;scene.render.bake.use_pass_color=False;scene.render.bake.use_pass_direct=True;scene.render.bake.use_pass_indirect=False
coverageImage=bpy.data.images.new('Coverage1',64,32,alpha=True,float_buffer=True);coverageImage.colorspace_settings.name='Non-Color';tex=nt.nodes.new('ShaderNodeTexImage');tex.image=coverageImage;emission=nt.nodes.new('ShaderNodeEmission');emission.inputs['Color'].default_value=(1,1,1,1);nt.links.new(emission.outputs[0],o.inputs['Surface'])
for node in nt.nodes:node.select=node==tex
nt.nodes.active=tex;bpy.ops.object.bake(type='EMIT');coverageRaw=np.array(coverageImage.pixels[:],dtype=np.float32).reshape((32,64,4));coverage=coverageRaw[...,0]>.99;assert coverage.sum()>1800
scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='32';scene.render.image_settings.exr_codec='ZIP';coveragePath=out/'coverage.exr';coverageImage.save_render(str(coveragePath),scene=scene);nt.nodes.remove(tex);nt.nodes.remove(emission);bpy.data.images.remove(coverageImage);nt.links.new(d.outputs[0],o.inputs['Surface'])
records=[];raws=[]
for mode in ['visible','hidden-ray-receiver']:
 if mode!='visible':
  # Keep the receiver in Cycles' bake scene without exposing it to transport rays.
  for name in ['visible_shadow','visible_diffuse','visible_glossy','visible_transmission','visible_volume_scatter']:setattr(sphere,name,False)
  sphere.visible_camera=True
 image=bpy.data.images.new('Uniform_'+mode,64,32,alpha=True,float_buffer=True);image.colorspace_settings.name='Non-Color';node=nt.nodes.new('ShaderNodeTexImage');node.image=image;nt.nodes.active=node
 for n in nt.nodes:n.select=n==node
 bpy.ops.object.bake(type='DIFFUSE');raw=np.array(image.pixels[:],dtype=np.float32).reshape((32,64,4));assert np.isfinite(raw).all();valid=coverage;assert valid.sum()>1800
 raws.append(raw);mean=raw[valid,:3].mean(0);assert np.max(np.abs(mean-np.array([.25,.5,.75])))<.015
 scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='32';scene.render.image_settings.exr_codec='ZIP';path=out/(mode+'.exr');image.save_render(str(path),scene=scene);records.append({'mode':mode,'validPixels':int(valid.sum()),'mean':mean.tolist(),'expected':[.25,.5,.75],'meanAbsError':np.abs(raw[valid,:3]-np.array([.25,.5,.75])).mean(0).tolist(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});nt.nodes.remove(node);bpy.data.images.remove(image)
shared=coverage;hiddenDiff=np.abs(raws[0][shared,:3]-raws[1][shared,:3]);hiddenMean=hiddenDiff.mean(0);assert float(hiddenMean.max())<.015
(out/'provenance.json').write_text(json.dumps({'status':'PassedUniformWorldBakePreflightOnly','quantity':'White Lambert outgoing radiance E/pi equals constantWorldradiance','shader':'BSDF_DIFFUSE white roughness0','size':[64,32],'samples':64,'canonicalSaved':False,'receiverCameraVisibleForBakeAdmission':True,'receiverTransportRayVisible':False,'noBeautyCameraRender':True,'helperSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'coverageMask':'RGB EMIT1, not alpha','coverageSha256':hashlib.sha256(coveragePath.read_bytes()).hexdigest(),'cases':records,'hiddenVsVisibleMeanAbsDifference':hiddenMean.tolist(),'hiddenVsVisibleMaxAbsDifference':hiddenDiff.max(0).tolist()},indent=2)+'\n');print('CS_PROBE_UNIFORM_PREFLIGHT_OK',flush=True)
