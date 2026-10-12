# Disposable high-sample context reference; no additional lighting-field bakes.
from pathlib import Path
import hashlib,json,math
helper=Path('/tmp/cs-mine-source-hybrid-board-final12.py').read_text();prefix=helper.split("source.hide_render=True;scene.render.engine='CYCLES'")[0]
prefix=prefix.replace("out=Path('/tmp/cs-mine-source-hybrid-board-final12')", "out=Path('/tmp/cs-mine-source-stable-board-final12')")
exec(compile(prefix,'bounded-board-construction','exec'))
source.hide_render=True;target=targets[0];scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=256;scene.cycles.use_denoising=False
materials={m:m for m in target.data.materials};view=scene.view_layers[0];view.use_pass_diffuse_color=True;view.use_pass_diffuse_direct=True;view.use_pass_diffuse_indirect=True;view.use_pass_glossy_color=True;view.use_pass_glossy_direct=True;view.use_pass_glossy_indirect=True
for name in ['SourceShedBoard','SourceBoardBaseColor','SourceBoardShadingNormal']:
 aov=view.aovs.add();aov.name=name;aov.type='COLOR'
material_inputs=[]
for material in materials.values():
 nt=material.node_tree;principled=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'];assert len(principled)==1;bsdf=principled[0];entry={'material':material.name,'closure':bsdf.type,'inputs':{}}
 for name in ['Diffuse Roughness','Roughness','Metallic','Subsurface Weight','Sheen Weight','Coat Weight','IOR','Specular IOR Level']:
  socket=bsdf.inputs.get(name)
  if socket:entry['inputs'][name]={'linked':socket.is_linked,'default':float(socket.default_value)}
 material_inputs.append(entry)
 for name in ['SourceShedBoard','SourceBoardBaseColor','SourceBoardShadingNormal']:
  node=nt.nodes.new('ShaderNodeOutputAOV');node.aov_name=name
  if name=='SourceShedBoard':node.inputs['Color'].default_value=(1,1,1,1)
  elif name=='SourceBoardBaseColor':
   socket=bsdf.inputs['Base Color']
   if socket.is_linked:nt.links.new(socket.links[0].from_socket,node.inputs['Color'])
   else:node.inputs['Color'].default_value=socket.default_value
  else:
   socket=bsdf.inputs['Normal'];normal=socket.links[0].from_socket if socket.is_linked else nt.nodes.new('ShaderNodeNewGeometry').outputs['Normal'];scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=.5;nt.links.new(normal,scale.inputs[0]);add=nt.nodes.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=(.5,.5,.5);nt.links.new(scale.outputs[0],add.inputs[0]);nt.links.new(add.outputs[0],node.inputs['Color'])
(out/'actual-board-bsdf-inputs.json').write_text(json.dumps(material_inputs,indent=2)+'\n')
camera=bpy.data.objects.new('Stable source board camera',bpy.data.cameras.new('Stable source board camera'));scene.collection.objects.link(camera);sourceEye,sourceAim,lens=json.loads((root/'runtime/out/mine-bake-audit/blender-views.json').read_text())['views']['R39_04_SHED_FRONT'];camera.location=sourceEye;camera.rotation_euler=(Vector(sourceAim)-Vector(sourceEye)).to_track_quat('-Z','Y').to_euler();camera.data.lens=lens;camera.data.sensor_width=36;camera.data.sensor_fit='AUTO';camera.data.clip_start=.05;camera.data.clip_end=800;scene.camera=camera
scene.render.resolution_x=640;scene.render.resolution_y=360;scene.render.resolution_percentage=100;scene.render.pixel_aspect_x=1;scene.render.pixel_aspect_y=1
actualvfov=2*math.atan(36*360/640/(2*lens));assert abs(actualvfov-vfov)<1e-6
scene.render.image_settings.media_type='MULTI_LAYER_IMAGE';scene.render.image_settings.file_format='OPEN_EXR_MULTILAYER';scene.render.image_settings.color_depth='32';scene.render.filepath=str(out/'SourceContextShed-256.exr');bpy.ops.render.render(write_still=True)
files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
(out/'provenance.json').write_text(json.dumps({'status':'HighSampleBoundedDiagnosticOnly','sourceSha256':hashlib.sha256((root/'runtime/out/spawn-export-source/combined-runtime-source.blend').read_bytes()).hexdigest(),'samples':256,'resolution':[640,360],'volumesDisabledInMemory':suppressed,'canonicalSourceSaved':False,'files':files},indent=2)+'\n');print('CS_STABLE_SOURCE_BOARD_REFERENCE_OK',flush=True)
