import bpy,sys,json,math,hashlib,subprocess
from pathlib import Path
from mathutils import Vector
root=Path('/workspace/critical-shift-spawn-runtime');audit=root/'runtime/out/mine-bake-audit';out=Path('/tmp/cs-mine-aov-no-volume-final11');out.mkdir(exist_ok=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16;scene.cycles.use_denoising=False
scene.render.resolution_x=640;scene.render.resolution_y=360;scene.render.resolution_percentage=100
scene.render.image_settings.media_type='MULTI_LAYER_IMAGE';scene.render.image_settings.file_format='OPEN_EXR_MULTILAYER';scene.render.image_settings.color_depth='32';scene.render.image_settings.exr_codec='ZIP'
layer=scene.view_layers[0]
for name in ['BaseColor','Roughness','Metallic','ShadingNormal','DiagnosticOne']:
 aov=layer.aovs.add();aov.name=name;aov.type='COLOR'
for prop in ['use_pass_diffuse_color','use_pass_diffuse_direct','use_pass_diffuse_indirect','use_pass_glossy_color','use_pass_glossy_direct','use_pass_glossy_indirect','use_pass_transmission_color','use_pass_transmission_direct','use_pass_transmission_indirect','use_pass_emit','use_pass_environment']:
 if hasattr(layer,prop):setattr(layer,prop,True)
suppressed=[]
for original in list(bpy.data.materials):
 if not original.use_nodes:continue
 active=next((n for n in original.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output),None)
 if active is None or not active.inputs['Volume'].is_linked:continue
 local=original.copy();original.user_remap(local);active=next(n for n in local.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
 for link in list(active.inputs['Volume'].links):local.node_tree.links.remove(link)
 suppressed.append(original.name)
materials=[];wood=[]
for original in list(bpy.data.materials):
 if not original.use_nodes:continue
 bsdf=next((n for n in original.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if bsdf is None:continue
 local=original.copy();original.user_remap(local);nt=local.node_tree;bsdf=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');materialout=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
 root_socket=materialout.inputs['Surface'].links[0].from_socket
 for name,field in [('BaseColor','Base Color'),('Roughness','Roughness'),('Metallic','Metallic')]:
  node=nt.nodes.new('ShaderNodeOutputAOV');node.name=name;node.aov_name=name
  s=bsdf.inputs[field]
  if s.is_linked:nt.links.new(s.links[0].from_socket,node.inputs['Color'])
  else:
   v=s.default_value;node.inputs['Color'].default_value=tuple(v) if hasattr(v,'__len__') else (v,v,v,1)
 normal=nt.nodes.new('ShaderNodeOutputAOV');normal.name='ShadingNormal';normal.aov_name='ShadingNormal'
 source=bsdf.inputs['Normal']
 if source.is_linked:
  scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=.5;nt.links.new(source.links[0].from_socket,scale.inputs[0]);add=nt.nodes.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=(.5,.5,.5);nt.links.new(scale.outputs[0],add.inputs[0]);nt.links.new(add.outputs[0],normal.inputs['Color'])
 else:
  geometry=nt.nodes.new('ShaderNodeNewGeometry');scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=.5;nt.links.new(geometry.outputs['Normal'],scale.inputs[0]);add=nt.nodes.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=(.5,.5,.5);nt.links.new(scale.outputs[0],add.inputs[0]);nt.links.new(add.outputs[0],normal.inputs['Color'])
 diagnostic_one=nt.nodes.new('ShaderNodeOutputAOV');diagnostic_one.name='DiagnosticOne';diagnostic_one.aov_name='DiagnosticOne';diagnostic_one.inputs['Color'].default_value=(1,1,1,1)
 materials.append(local)
 if any(n.type=='TEX_IMAGE' and n.image and n.image.name=='rough_wood_diff_1k.jpg' for n in nt.nodes):wood.append((local,bsdf,materialout,root_socket))
records={'sourceBlenderSha256':hashlib.sha256((root/'runtime/out/spawn-export-source/combined-runtime-source.blend').read_bytes()).hexdigest(),'resolution':[640,360],'samples':16,'purpose':'Diagnostic source BaseColor AOV with original BSDF and bump normal graphs; separate emission-only normal-context control; no canonical file changes','materials':len(materials),'woodMaterials':len(wood),'diagnosticVolumesDisabledInMemory':suppressed,'files':[]}
views=json.loads((audit/'blender-views.json').read_text())['views']
for name,(eye,target,lens) in views.items():
 camera=bpy.data.objects.new('AOV '+name,bpy.data.cameras.new('AOV '+name));scene.collection.objects.link(camera);camera.location=eye;camera.rotation_euler=(Vector(target)-Vector(eye)).to_track_quat('-Z','Y').to_euler();camera.data.lens=lens;camera.data.clip_start=.05;camera.data.clip_end=800;scene.camera=camera
 for mode in ['original']:
  for m,bsdf,materialout,root_socket in wood:m.node_tree.links.new(root_socket,materialout.inputs['Surface'])
  if mode=='emission-context':
   for m,bsdf,materialout,root_socket in wood:
    emit=m.node_tree.nodes.new('ShaderNodeEmission');s=bsdf.inputs['Base Color']
    if s.is_linked:m.node_tree.links.new(s.links[0].from_socket,emit.inputs['Color'])
    else:emit.inputs['Color'].default_value=s.default_value
    m.node_tree.links.new(emit.outputs[0],materialout.inputs['Surface'])
  path=out/(name+'-'+mode+'.exr');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);subprocess.run(['/home/agent/.local/share/critical-shift/venv/bin/python','/tmp/cs-mine-aov-check-final11.py',str(path)],check=True);records['files'].append({'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mode':mode,'view':name});print('CS_SOURCE_AOV_DONE',name,mode,flush=True)
(out/'provenance.json').write_text(json.dumps(records,indent=2)+'\n');print('CS_SOURCE_AOV_DIAGNOSTIC_OK',flush=True)
