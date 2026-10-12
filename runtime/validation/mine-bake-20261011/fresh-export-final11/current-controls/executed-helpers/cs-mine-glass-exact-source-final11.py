"""Actual authored depot glass under a known uniform world, no source save."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
root=Path('/workspace/critical-shift-spawn-runtime');out=Path('/tmp/cs-mine-glass-exact-final11');out.mkdir(exist_ok=True)
if any(out.glob('Source-*-angle*.exr')):raise ValueError('Archive previous source glass evidence before retry')
vehicle=bpy.data.objects.get('crew_van')
if vehicle is None:raise ValueError('Actual authored crew_van missing')
mats=[m for m in vehicle.data.materials if m and m.use_nodes and any(n.type=='BSDF_GLASS' for n in m.node_tree.nodes)]
if len(mats)!=1:raise ValueError('Expected one actual depot glass material')
material=mats[0];nodes=[n for n in material.node_tree.nodes if n.type=='BSDF_GLASS']
if len(nodes)!=1:raise ValueError('Ambiguous authored glass closure')
glass=nodes[0]
if any(glass.inputs[k].is_linked for k in ['Color','Roughness','IOR','Normal']):raise ValueError('Source glass control needs authored constants')
color=list(glass.inputs['Color'].default_value);rough=float(glass.inputs['Roughness'].default_value);ior=float(glass.inputs['IOR'].default_value)
scene=bpy.data.scenes.new('Diagnostic actual source glass');bpy.context.window.scene=scene
world=bpy.data.worlds.new('Known uniform diagnostic glass world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.1,.3,.8,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=1;scene.world=world
bpy.ops.mesh.primitive_plane_add(size=10,location=(0,0,0));pane=bpy.context.object;pane.data.materials.append(material)
bpy.ops.mesh.primitive_plane_add(size=20,location=(0,0,-1));plate=bpy.context.object;black=bpy.data.materials.new('Diagnostic black backplate');black.use_nodes=True;nt=black.node_tree;nt.nodes.clear();emit=nt.nodes.new('ShaderNodeEmission');emit.inputs['Color'].default_value=(0,0,0,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(emit.outputs[0],output.inputs['Surface']);plate.data.materials.append(black)
camera=bpy.data.objects.new('Glass diagnostic camera',bpy.data.cameras.new('Glass diagnostic camera'));scene.collection.objects.link(camera);camera.data.type='ORTHO';camera.data.ortho_scale=.8;camera.data.clip_start=.01;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.render.resolution_x=128;scene.render.resolution_y=128;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='32';scene.render.image_settings.exr_codec='ZIP'
files={}
for backdrop,background in [('black',[0,0,0]),('colour',[.04,.2,.3])]:
 emit.inputs['Color'].default_value=(*background,1)
 for angle in [0,40,65]:
  theta=math.radians(angle);camera.location=(math.sin(theta)*4,0,math.cos(theta)*4);camera.rotation_euler=(-camera.location).to_track_quat('-Z','Y').to_euler();p=out/f'Source-{backdrop}-angle{angle}.exr';scene.render.filepath=str(p);bpy.ops.render.render(write_still=True);files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
proof={'status':'Bounded actual-source glass reflection diagnostic; no final glass acceptance','sourceBlenderSha256':hashlib.sha256((root/'runtime/out/spawn-export-source/combined-runtime-source.blend').read_bytes()).hexdigest(),'sourceObject':'crew_van','material':material.name,'materialLibrary':material.library.filepath if material.library else None,'authoredNodes':[n.type for n in material.node_tree.nodes],'glassDistribution':glass.distribution,'color':color,'roughness':rough,'ior':ior,'f0':((ior-1)/(ior+1))**2,'worldLinear':[.1,.3,.8],'backplates':{'black':[0,0,0],'colour':[.04,.2,.3]},'resolution':[128,128],'anglesDegrees':[0,40,65],'samples':32,'canonicalSourceSaved':False,'limits':['Reflection-only uniform world control','No full vehicle cubemap, BTDF/background tint or Player acceptance'],'files':files}
(out/'source-provenance.json').write_text(json.dumps(proof,indent=2)+'\n');print('CS_SOURCE_EXACT_GLASS_BLACK_AND_COLOUR_OK',flush=True)
