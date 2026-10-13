import bpy,json,math
from pathlib import Path
out=Path('/tmp/cs-mine-world-control-final11');out.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=128;scene.cycles.use_denoising=False;scene.render.resolution_x=scene.render.resolution_y=128;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Black');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
bpy.ops.mesh.primitive_plane_add(size=2);plane=bpy.context.object;m=bpy.data.materials.new('Lambert18percent');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();diffuse=nt.nodes.new('ShaderNodeBsdfDiffuse');diffuse.inputs['Color'].default_value=(.18,.18,.18,1);diffuse.inputs['Roughness'].default_value=0;output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(diffuse.outputs[0],output.inputs['Surface']);plane.data.materials.append(m)
light=bpy.data.objects.new('100 W point',bpy.data.lights.new('100 W point','POINT'));scene.collection.objects.link(light);light.data.energy=100;light.data.color=(1,1,1);light.data.shadow_soft_size=.001
camera=bpy.data.objects.new('Frontal',bpy.data.cameras.new('Frontal'));scene.collection.objects.link(camera);camera.data.type='ORTHO';camera.data.ortho_scale=.8;camera.location=(0,0,5);scene.camera=camera
scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_depth='32'
light.data.energy=0
for label,color in [('white',(1,1,1)),('assembly',(.045,.055,.09))]:
 scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(*color,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=1;scene.render.filepath=str(out/('Blender-world-'+label+'.exr'));bpy.ops.render.render(write_still=True)
(out/'source.json').write_text(json.dumps({'albedoLinear':.18,'BSDF':'Diffuse roughness0','worldColors':{'white':[1,1,1],'assembly':[.045,.055,.09]},'worldStrength':1,'pointPower':0,'samples':128},indent=2)+'\n');print('CS_BLENDER_WORLD_CONTROL_OK',flush=True)
