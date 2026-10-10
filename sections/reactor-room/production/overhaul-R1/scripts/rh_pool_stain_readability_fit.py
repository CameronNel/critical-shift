"""Second, pixel-driven mineral-trail revision; no water or light changes."""
import json


def apply(scene, materials):
    if 'rh_pool_stain_readability_fit' in scene:
        return json.loads(scene['rh_pool_stain_readability_fit'])
    material = materials['RH refine quiet pool lining']
    tree = material.node_tree
    shader = next(n for n in tree.nodes if n.type == 'BSDF_PRINCIPLED')
    terminal = shader.inputs['Base Color'].links[0].from_node
    assert terminal.name == 'RH mineral trail contrast modulation'
    product = terminal.inputs[0].links[0].from_node
    maximum = product.inputs[0].links[0].from_node
    assert maximum.type == 'MATH' and maximum.operation == 'MAXIMUM'
    trails = []
    for index, old_end, end in [(0,-2.80,-3.40),(1,-2.20,-3.05)]:
        clipped = maximum.inputs[index].links[0].from_node
        mask = clipped.inputs[0].links[0].from_node
        width = mask.inputs[0].links[0].from_node
        fade = mask.inputs[1].links[0].from_node
        top = clipped.inputs[1].links[0].from_node
        assert width.type == fade.type == 'MAP_RANGE'
        assert abs(width.inputs[2].default_value-.17) < 1e-6
        assert abs(fade.inputs[1].default_value-old_end) < 1e-6
        assert top.operation == 'LESS_THAN' and abs(top.inputs[1].default_value+1.135) < 1e-6
        width.inputs[2].default_value = .24
        width.inputs[3].default_value = .95
        width.interpolation_type = 'SMOOTHSTEP'
        fade.inputs[1].default_value = end
        fade.inputs[2].default_value = end+.65
        fade.interpolation_type = 'SMOOTHSTEP'
        trails.append({'end_z':end,'soft_fade_m':.65,'xy_soft_support_m':[.02,.24],'top_clip_z':-1.135})
    variation = tree.nodes['RH mineral trail restrained variation']
    for index,value in enumerate((.30,.70,.45,1),1):
        variation.inputs[index].default_value = value
    variation.interpolation_type = 'SMOOTHSTEP'
    noise = tree.nodes['RH mineral trail irregularity']
    noise.inputs['Scale'].default_value = 4.0
    noise.inputs['Detail'].default_value = 3
    noise.inputs['Roughness'].default_value = .65
    terminal.inputs[2].default_value = (.68,.58,.42,1)
    report = {'trails':trails,'mineral_color':[.68,.58,.42],'maximum_strength':.95,
              'irregular_strength_range':[.45,1],'noise_scale':4,
              'scope':'Only the existing joint-origin liner mineral material. Soft spatial falloff and stronger irregular breakup; all geometry, exact origins, water optics, illumination and other materials unchanged.',
              'art_acceptance':False,'prior_full21_visual_verdict':'Failed on 45eb; this revision requires new full pixels.'}
    scene['rh_pool_stain_readability_fit'] = json.dumps(report,sort_keys=True)
    return report
