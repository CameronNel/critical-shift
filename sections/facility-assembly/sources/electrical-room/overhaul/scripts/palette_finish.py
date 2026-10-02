"""Owner-directed gunmetal, damp concrete and functional safety-color finish."""
import bpy

PREFIX = 'EOH | '


def profile(name, color, roughness, grain, depth, metallic=0, coat=0):
    mat = bpy.data.materials[PREFIX + name]
    nt = mat.node_tree
    bs = nt.nodes.get('Principled BSDF')
    ramp = bs.inputs['Base Color'].links[0].from_node
    assert ramp.type == 'VALTORGB', name
    mat.diffuse_color = (*color, 1)
    variation = (.89, 1.08) if name in {'cream', 'floor', 'Coarse service epoxy'} else (.78, 1.18)
    for stop, factor in zip(ramp.color_ramp.elements, variation):
        stop.color = (*(min(1, v * factor) for v in color), 1)
    ramp.color_ramp.elements[0].position = .27
    ramp.color_ramp.elements[1].position = .73
    macro = ramp.inputs[0].links[0].from_node
    macro.inputs['Scale'].default_value = 2.8 if name == 'cream' else 2.0
    macro.inputs['Detail'].default_value = 3
    mapper = next(n for n in nt.nodes if n.type == 'MAP_RANGE')
    mapper.inputs['To Min'].default_value = roughness[0]
    mapper.inputs['To Max'].default_value = roughness[1]
    bump = next((n for n in nt.nodes if n.type == 'BUMP'), None)
    if bump:
        bump.inputs['Distance'].default_value = depth
        bump.inputs['Strength'].default_value = .55 if name in {'cream', 'floor'} else .38
        fine = bump.inputs['Height'].links[0].from_node
        fine.inputs['Scale'].default_value = grain
        fine.inputs['Detail'].default_value = 3
        fine.inputs['Roughness'].default_value = .72
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Coat Weight'].default_value = coat
    bs.inputs['Coat Roughness'].default_value = .34
    return mat


def damp_patch(mat, wall=False):
    """Irregular lower-wall/outer-floor dampness; no full-room gloss overlay."""
    nt = mat.node_tree
    bs = nt.nodes.get('Principled BSDF')
    tc = next(n for n in nt.nodes if n.type == 'TEX_COORD')
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.name = 'Palette | broken damp patches'
    noise.inputs['Scale'].default_value = 1.65
    noise.inputs['Detail'].default_value = 3
    noise.inputs['Roughness'].default_value = .7
    nt.links.new(tc.outputs['Object'], noise.inputs['Vector'])
    breakup = nt.nodes.new('ShaderNodeMapRange')
    breakup.clamp = True
    breakup.inputs['From Min'].default_value = .46 if wall else .40
    breakup.inputs['From Max'].default_value = .69 if wall else .54
    nt.links.new(noise.outputs['Fac'], breakup.inputs[0])
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    limit = nt.nodes.new('ShaderNodeMapRange')
    limit.clamp = True
    if wall:
        # Geometry Z avoids a damp-looking ceiling when the same mineral finish
        # is used on a shell object whose local coordinate origin is at its top.
        geometry = nt.nodes.new('ShaderNodeNewGeometry')
        nt.links.new(geometry.outputs['Position'], sep.inputs[0])
        nt.links.new(sep.outputs['Z'], limit.inputs[0])
        limit.inputs['From Min'].default_value = .30
        limit.inputs['From Max'].default_value = 2.25
        limit.inputs['To Min'].default_value = .75
        limit.inputs['To Max'].default_value = 0
    else:
        # Two bounded side-wall contact zones in the existing Floor object's
        # metre coordinates, away from the central route and insulating mats.
        zones = []
        for center in [(4.4, -6.2, 0), (4.85, 6.8, 0)]:
            offset = nt.nodes.new('ShaderNodeVectorMath')
            offset.operation = 'SUBTRACT'
            offset.inputs[1].default_value = center
            nt.links.new(tc.outputs['Object'], offset.inputs[0])
            stretch = nt.nodes.new('ShaderNodeVectorMath')
            stretch.operation = 'MULTIPLY'
            stretch.inputs[1].default_value = (1.35, .62, 0)
            nt.links.new(offset.outputs['Vector'], stretch.inputs[0])
            length = nt.nodes.new('ShaderNodeVectorMath')
            length.operation = 'LENGTH'
            nt.links.new(stretch.outputs['Vector'], length.inputs[0])
            fade = nt.nodes.new('ShaderNodeMapRange')
            fade.clamp = True
            fade.inputs['From Min'].default_value = .45
            fade.inputs['From Max'].default_value = 1.45
            fade.inputs['To Min'].default_value = 1
            fade.inputs['To Max'].default_value = 0
            nt.links.new(length.outputs['Value'], fade.inputs[0])
            zones.append(fade.outputs[0])
        joined = nt.nodes.new('ShaderNodeMath')
        joined.operation = 'MAXIMUM'
        for index, zone in enumerate(zones):
            nt.links.new(zone, joined.inputs[index])
        limit.inputs['From Min'].default_value = 0
        limit.inputs['From Max'].default_value = 1
        nt.links.new(joined.outputs[0], limit.inputs[0])
    mask = nt.nodes.new('ShaderNodeMath')
    mask.operation = 'MULTIPLY'
    nt.links.new(breakup.outputs[0], mask.inputs[0])
    nt.links.new(limit.outputs[0], mask.inputs[1])
    old_color = bs.inputs['Base Color'].links[0].from_socket
    old_roughness = bs.inputs['Roughness'].links[0].from_socket
    shade = nt.nodes.new('ShaderNodeMixRGB')
    shade.blend_type = 'MULTIPLY'
    shade.inputs[2].default_value = (.52, .61, .65, 1)
    nt.links.new(mask.outputs[0], shade.inputs[0])
    nt.links.new(old_color, shade.inputs[1])
    nt.links.new(shade.outputs[0], bs.inputs['Base Color'])
    response = nt.nodes.new('ShaderNodeMixRGB')
    response.blend_type = 'MIX'
    response.inputs[2].default_value = ((.38,)*3 + (1,)) if wall else ((.13,)*3 + (1,))
    nt.links.new(mask.outputs[0], response.inputs[0])
    nt.links.new(old_roughness, response.inputs[1])
    nt.links.new(response.outputs[0], bs.inputs['Roughness'])
    if not wall:
        # Moisture fills the micro-relief locally, allowing restrained practical
        # reflections while the surrounding worn slab stays coarse and dry.
        bump = next(n for n in nt.nodes if n.type == 'BUMP')
        smooth = nt.nodes.new('ShaderNodeMapRange')
        smooth.inputs['To Min'].default_value = bump.inputs['Strength'].default_value
        smooth.inputs['To Max'].default_value = .12
        nt.links.new(mask.outputs[0], smooth.inputs[0])
        nt.links.new(smooth.outputs[0], bump.inputs['Strength'])


def apply():
    scene = bpy.context.scene
    assert not scene.get('electrical_palette_revision'), 'Apply to the preserved pre-palette source'
    specifications = {
        'cream': ((.145, .169, .180), (.76, .95), 36, .0030, 0, 0),
        'floor': ((.077, .094, .102), (.74, .94), 43, .0025, 0, 0),
        'route': ((.047, .068, .080), (.53, .80), 68, .0010, 0, .08),
        'enamel': ((.097, .134, .153), (.36, .68), 64, .0010, .38, .16),
        'slate': ((.022, .032, .042), (.48, .78), 58, .0007, .22, .06),
        'replacement': ((.077, .112, .098), (.42, .76), 60, .0009, .22, .08),
        'steel': ((.135, .170, .193), (.33, .60), 78, .0003, .86, 0),
        'zinc': ((.225, .259, .269), (.43, .69), 64, .0005, .73, 0),
        'oxide': ((.66, .103, .024), (.46, .74), 63, .0008, .14, .08),
        'ochre': ((.79, .455, .026), (.43, .70), 63, .0007, .12, .06),
        'redrubber': ((.40, .023, .012), (.71, .91), 85, .0004, 0, 0),
        'Coarse service epoxy': ((.060, .073, .078), (.58, .85), 44, .0018, 0, 0),
        'Floor contact history': ((.023, .031, .035), (.68, .93), 48, .0010, 0, 0),
        'Moulded reserve cell casing': ((.046, .063, .072), (.49, .78), 68, .0007, 0, 0),
    }
    materials = {}
    for name, spec in specifications.items():
        materials[name] = profile(name, *spec)
    # These four already contain the fixed individual coating phases. Keep their
    # original coordinate graph/assignment and change their actual painted finish.
    for i in range(1, 5):
        name = 'Leaf ' + str(i) + ' individual coating'
        profile(name, *specifications['enamel'])
    damp_patch(materials['cream'], wall=True)
    damp_patch(materials['floor'])
    powers = {
        'Entry fluorescent light': 65,
        'Rear hall practical light': 65,
        'West task fluorescent light': 230,
        'West rear practical light': 190,
        'Transformer task practical light': 240,
        'Transfer task practical light': 150,
        'Reserve bay practical light': 200,
        'EOH | Bench practical': 36,
    }
    for name, power in powers.items():
        bpy.data.objects[name].data.energy = power
    background = scene.world.node_tree.nodes.get('Background')
    background.inputs['Strength'].default_value = .035
    scene['electrical_palette_revision'] = 'Gunmetal / damp concrete / safety colors P2'
    return {
        'material_profiles': list(specifications),
        'individual_leaf_profiles': 4,
        'localized_damp_materials': [materials['cream'].name, materials['floor'].name],
        'practical_powers_watts': powers,
        'world_strength': .035,
        'exposure_unchanged': scene.view_settings.exposure,
        'reserved_clear_route_is_dry': True,
        'existing_authored_contact_wear_and_geometry_preserved': True,
    }
