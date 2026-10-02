"""Keep tactile wired safety glass while making large forms visible through it."""
import bpy

def apply():
    scene=bpy.context.scene
    assert not scene.get('electrical_vision_finish_revision')
    material=bpy.data.materials['EOH | Wired vision glass']
    bs=material.node_tree.nodes.get('Principled BSDF')
    rough=bs.inputs['Roughness'].links[0].from_node
    assert rough.bl_idname=='ShaderNodeMapRange'
    before=[rough.inputs['To Min'].default_value,rough.inputs['To Max'].default_value,
            bs.inputs['Coat Roughness'].default_value]
    rough.inputs['To Min'].default_value=.025
    rough.inputs['To Max'].default_value=.075
    bs.inputs['Coat Roughness'].default_value=.075
    scene['electrical_vision_finish_revision']=1
    return {'material':material.name,'previous_roughness_min_max_coat':before,
            'roughness_min_max_coat':[rough.inputs['To Min'].default_value,
                                     rough.inputs['To Max'].default_value,
                                     bs.inputs['Coat Roughness'].default_value],
            'existing_color_variation_micro_normal_transmission_and_wires_preserved':True}
