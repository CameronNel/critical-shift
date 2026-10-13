# Disposable Source render: exact authored shed/frame object masks and shader/transport AOVs.
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
root=Path('/workspace/critical-shift-spawn-runtime');out=Path('/tmp/cs-mine-timber-source-final13');assert not out.exists();out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.seed=21947;scene.render.use_persistent_data=False;scene.cycles.use_denoising=False
scene.render.resolution_x=640;scene.render.resolution_y=360;scene.render.resolution_percentage=100;scene.render.pixel_aspect_x=1;scene.render.pixel_aspect_y=1
instance=bpy.data.objects['ROOM_mine'];dg=bpy.context.evaluated_depsgraph_get();names={'R39 | Shed boards':1,'R39 | Shed frame':2};selected=[]
for o in bpy.data.objects:
 if o.type in {'MESH','CURVE','FONT'}:o.pass_index=0
for name,index in names.items():
 o=next(o for o in instance.instance_collection.all_objects if o.name==name);o.pass_index=index
 positions=[i.matrix_world.copy() for i in dg.object_instances if i.object.original==o];assert len(positions)==1
 selected.append({'name':name,'index':index,'worldMatrix':[list(row) for row in positions[0]],'materials':[m.name for m in o.data.materials]})
# Mutate actual node trees in this disposable process; user_remap of linked users is ineffective.
removed=[]
for material in bpy.data.materials:
 if not material.use_nodes:continue
 for output in material.node_tree.nodes:
  if output.type!='OUTPUT_MATERIAL' or not output.is_active_output or not output.inputs['Volume'].is_linked:continue
  for link in list(output.inputs['Volume'].links):
   removed.append({'material':material.name,'output':output.name,'from':link.from_node.name});material.node_tree.links.remove(link)
assert len(removed)==2 and {r['material'] for r in removed}=={'R38 | Tunnel haze','R39 | Shed haze'}
assert not any(n.inputs['Volume'].is_linked for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
view=scene.view_layers[0]
for name in ['CsExactTimberMask','CsBaseColor','CsShadingNormal']:
 aov=view.aovs.add();aov.name=name;aov.type='COLOR'
for prop in ['use_pass_diffuse_color','use_pass_diffuse_direct','use_pass_diffuse_indirect','use_pass_glossy_color','use_pass_glossy_direct','use_pass_glossy_indirect','use_pass_emit']:setattr(view,prop,True)
for m in bpy.data.materials:
 if not m.use_nodes:continue
 nt=m.node_tree
 node=nt.nodes.new('ShaderNodeOutputAOV');node.aov_name='CsExactTimberMask';info=nt.nodes.new('ShaderNodeObjectInfo');nt.links.new(info.outputs['Object Index'],node.inputs['Color'])
 bsdf=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if bsdf is None:continue
 base=nt.nodes.new('ShaderNodeOutputAOV');base.aov_name='CsBaseColor';socket=bsdf.inputs['Base Color']
 if socket.is_linked:nt.links.new(socket.links[0].from_socket,base.inputs['Color'])
 else:base.inputs['Color'].default_value=socket.default_value
 normal=nt.nodes.new('ShaderNodeOutputAOV');normal.aov_name='CsShadingNormal';socket=bsdf.inputs['Normal'];source=socket.links[0].from_socket if socket.is_linked else nt.nodes.new('ShaderNodeNewGeometry').outputs['Normal']
 scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=.5;nt.links.new(source,scale.inputs[0]);add=nt.nodes.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=(.5,.5,.5);nt.links.new(scale.outputs[0],add.inputs[0]);nt.links.new(add.outputs[0],normal.inputs['Color'])
name='R39_04_SHED_FRONT';eye,aim,lens=json.loads((root/'runtime/out/mine-bake-audit/blender-views.json').read_text())['views'][name]
camera=bpy.data.objects.new('Timber diagnostic camera',bpy.data.cameras.new('Timber diagnostic camera'));scene.collection.objects.link(camera);camera.location=eye;camera.rotation_euler=(Vector(aim)-Vector(eye)).to_track_quat('-Z','Y').to_euler();camera.data.lens=lens;camera.data.sensor_width=36;camera.data.sensor_fit='AUTO';camera.data.clip_start=.05;camera.data.clip_end=800;scene.camera=camera
vfov=math.degrees(2*math.atan(36*360/640/(2*lens)));expected=next(v for v in json.loads((root/'runtime/out/mine-bake-audit/cameras.json').read_text())['views'] if v['name']==name);assert abs(vfov-expected['verticalFov'])<1e-4
scene.render.image_settings.media_type='MULTI_LAYER_IMAGE';scene.render.image_settings.file_format='OPEN_EXR_MULTILAYER';scene.render.image_settings.color_depth='32';scene.render.image_settings.exr_codec='ZIP';scene.render.filepath=str(out/(name+'.exr'));bpy.context.view_layer.update();bpy.ops.render.render(write_still=True)
(out/'provenance.json').write_text(json.dumps({'status':'RenderedSourceTimberMasksAwaitingPixelAudit','sourceSnapshotSha256':sha(root/'runtime/out/spawn-export-source/combined-runtime-source.blend'),'helperSha256':sha(Path(__file__)),'imageSha256':sha(out/(name+'.exr')),'selected':selected,'removedVolumeLinks':removed,'resolution':[640,360],'samples':32,'seed':21947,'camera':{'name':name,'eye':eye,'aim':aim,'lens':lens,'verticalFov':vfov},'limits':['Only shed/frame objects targeted; mask effectiveness/finite/matchedgeometry pending native pixel audit','No source save, new lighting bake, Player or visual grade']},indent=2)+'\n');print('CS_SOURCE_TIMBER_DIAGNOSTIC_OK',flush=True)
