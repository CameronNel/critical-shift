"""Retain rock image/normal detail while removing the inherited blue pigment mix."""
import bpy,json,hashlib,ctypes
from pathlib import Path
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/ground-finish';SRC=Path(bpy.data.filepath);MAIN=SRC.with_name('facility_environment.blend');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((OUT/'verification.json').read_text());assert sha(SRC)==r['candidate_sha256'] and sha(MAIN)==r['before_sha256'];made={}
for name in r['changed']:
 if not name.startswith('CY | Existing boulder'):continue
 o=bpy.data.objects[name];original=o.data.materials[0]
 if original.name not in made:
  source=original.node_tree;diff=source.nodes['Image Texture'].image;normal=source.nodes['Image Texture.001'].image
  m=bpy.data.materials.new('GF | Mineral '+diff.name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();f=nt.nodes.new('NodeFrame');f.label='Weathered Mineral And Buried Foot'
  def n(kind,x,y=0):
   node=nt.nodes.new(kind);node.parent=f;node.location=(x,y);node.width=160;return node
  uv=n('ShaderNodeUVMap',0);uv.uv_map='UVMap';tex=n('ShaderNodeTexImage',230);tex.image=diff
  grey=n('ShaderNodeRGBToBW',460);ramp=n('ShaderNodeValToRGB',690);ramp.width=200
  ramp.color_ramp.elements[0].position=.12;ramp.color_ramp.elements[0].color=(.075,.071,.063,1);ramp.color_ramp.elements[1].position=.65;ramp.color_ramp.elements[1].color=(.245,.229,.199,1)
  nt.links.new(uv.outputs[0],tex.inputs[0]);nt.links.new(tex.outputs['Color'],grey.inputs[0]);nt.links.new(grey.outputs[0],ramp.inputs[0])
  geo=n('ShaderNodeNewGeometry',0,-270);sep=n('ShaderNodeSeparateXYZ',230,-310);wet=n('ShaderNodeMapRange',460,-160);wet.inputs['From Min'].default_value=-.08;wet.inputs['From Max'].default_value=.65;wet.inputs['To Min'].default_value=.8;wet.inputs['To Max'].default_value=0
  nt.links.new(geo.outputs['Position'],sep.inputs[0]);nt.links.new(sep.outputs['Z'],wet.inputs['Value'])
  mix=n('ShaderNodeMixRGB',960);mix.inputs[2].default_value=(.113,.098,.077,1);nt.links.new(wet.outputs['Result'],mix.inputs[0]);nt.links.new(ramp.outputs[0],mix.inputs[1])
  normtex=n('ShaderNodeTexImage',230,-520);normtex.image=normal;norm=n('ShaderNodeNormalMap',960,-210);norm.inputs['Strength'].default_value=.55;nt.links.new(uv.outputs[0],normtex.inputs[0]);nt.links.new(normtex.outputs['Color'],norm.inputs['Color'])
  bs=n('ShaderNodeBsdfPrincipled',1210);bs.inputs['Roughness'].default_value=.86;bs.inputs['Specular IOR Level'].default_value=.25;nt.links.new(mix.outputs[0],bs.inputs['Base Color']);nt.links.new(norm.outputs[0],bs.inputs['Normal'])
  output=n('ShaderNodeOutputMaterial',1460);nt.links.new(bs.outputs[0],output.inputs['Surface']);made[original.name]=m
 o.data.materials[0]=made[original.name]
r['rock_scope']='Southern yard boulders: retained original diffuse/normal image detail, neutral mineral palette, dusty buried-foot gradient; local cliff shadow response and ground contact blend. No geometry changes.'
bpy.ops.wm.save_as_mainfile(filepath=str(SRC),check_existing=False);r['candidate_sha256']=sha(SRC);(OUT/'verification.json').write_text(json.dumps(r,indent=2))
s=bpy.context.scene;s.camera=bpy.data.objects['GF CAMERA | mine-cliff-yard'];s.render.filepath=str(OUT/'mine-cliff-yard.png');s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=4;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;bpy.ops.render.render(write_still=True);print('MINERAL_MATERIALS_CORRECTED',flush=True)
