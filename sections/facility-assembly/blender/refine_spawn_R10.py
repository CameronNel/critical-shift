"""R09 -> R10: integrate generated painted pigment texture; pack dependency."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_spawn_concept02_R09.blend'),load_ui=False)
path=R/'blender/textures/spawn_painted_mineral_01.png';image=bpy.data.images.load(str(path),check_existing=True);image.pack();changed=[]
for name in ['S01 warm mineral ivory','S01 deep olive painted sheet','S01 courtyard limestone concrete','S01 plinth stone']:
 m=bpy.data.materials[name];nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.get('Principled BSDF');old=p.inputs['Base Color'].links[0].from_socket
 geo=nodes.new('ShaderNodeNewGeometry');scale=nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=.26
 tex=nodes.new('ShaderNodeTexImage');tex.image=image;tex.projection='BOX';tex.projection_blend=.12;tex.extension='REPEAT'
 mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.65 if 'ivory' in name else .42
 links.new(geo.outputs['Position'],scale.inputs[0]);links.new(scale.outputs['Vector'],tex.inputs['Vector']);links.new(old,mix.inputs[1]);links.new(tex.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],p.inputs['Base Color']);changed.append(name)
s=bpy.context.scene;s.name='FACILITY_SPAWN_CONCEPT02_R10';dest=R/'blender/facility_spawn_concept02_R10.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
b=json.loads((O/'BUILD_R09.json').read_text());b.update(revision='R10',file=str(dest),painted_texture={'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'packed':True,'materials':changed,'generator':'Built-in ChatGPT image_gen','purpose':'Subtle broad painted surface variation based on approved art direction'});(O/'BUILD_R10.json').write_text(json.dumps(b,indent=2));print('R10_SAVED',flush=True)
