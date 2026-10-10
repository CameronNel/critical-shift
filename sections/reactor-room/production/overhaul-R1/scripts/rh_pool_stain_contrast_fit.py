"""Improve only the two existing joint-origin mineral trails on the pool liner."""
import json


def apply(scene, materials):
    material = materials['RH refine quiet pool lining']
    tree = material.node_tree
    shader = next(node for node in tree.nodes if node.type == 'BSDF_PRINCIPLED')
    terminal = shader.inputs['Base Color'].links[0].from_node
    if terminal.name == 'RH mineral trail contrast modulation':
        return json.loads(scene['rh_pool_stain_contrast_fit'])
    assert terminal.type == 'MIX_RGB' and terminal.blend_type == 'MIX'
    assert all(abs(a-b) < 1e-6 for a,b in zip(terminal.inputs[2].default_value, (.48,.46,.42,1)))
    maximum = terminal.inputs[0].links[0].from_node
    assert maximum.type == 'MATH' and maximum.operation == 'MAXIMUM'
    origins = []
    for index, old_end, new_end in [(0,-2.10,-2.80), (1,-1.85,-2.20)]:
        clipped = maximum.inputs[index].links[0].from_node
        mask = clipped.inputs[0].links[0].from_node
        width = mask.inputs[0].links[0].from_node
        fade = mask.inputs[1].links[0].from_node
        top = clipped.inputs[1].links[0].from_node
        assert width.type == fade.type == 'MAP_RANGE'
        assert abs(width.inputs[1].default_value-.02) < 1e-6
        assert abs(width.inputs[2].default_value-.17) < 1e-6
        assert abs(width.inputs[3].default_value-.55) < 1e-6
        assert abs(fade.inputs[1].default_value-old_end) < 1e-6
        assert top.operation == 'LESS_THAN' and abs(top.inputs[1].default_value+1.135) < 1e-6
        width.inputs[3].default_value = .80
        fade.inputs[1].default_value = new_end
        fade.inputs[2].default_value = new_end+.5
        origins.append({'old_end_z':old_end,'new_end_z':new_end,'top_clip_z':-1.135,'radial_width_m':[.02,.17]})
    position = next(node for node in tree.nodes if node.type == 'NEW_GEOMETRY')
    noise = tree.nodes.new('ShaderNodeTexNoise')
    noise.name = 'RH mineral trail irregularity'
    noise.inputs['Scale'].default_value = 6
    noise.inputs['Detail'].default_value = 2
    noise.inputs['Roughness'].default_value = .55
    tree.links.new(position.outputs['Position'], noise.inputs['Vector'])
    modulation = tree.nodes.new('ShaderNodeMapRange')
    modulation.name = 'RH mineral trail restrained variation'
    modulation.clamp = True
    for i,value in enumerate((.20,.80,.65,1),1):
        modulation.inputs[i].default_value = value
    tree.links.new(noise.outputs['Fac'], modulation.inputs[0])
    product = tree.nodes.new('ShaderNodeMath')
    product.name = 'RH mineral trail irregular mask'
    product.operation = 'MULTIPLY'
    tree.links.new(maximum.outputs[0], product.inputs[0])
    tree.links.new(modulation.outputs[0], product.inputs[1])
    tree.links.new(product.outputs[0], terminal.inputs[0])
    terminal.name = 'RH mineral trail contrast modulation'
    terminal.inputs[2].default_value = (.12,.125,.10,1)
    report = {'trails':origins,'mineral_color':[.12,.125,.10],'maximum_strength':.80,'irregular_strength_range':[.65,1],
              'scope':'Only the existing liner mineral masks and their color; exact grout origins, top clip, liner geometry and all water optics retained.',
              'art_acceptance':False}
    scene['rh_pool_stain_contrast_fit'] = json.dumps(report,sort_keys=True)
    return report
