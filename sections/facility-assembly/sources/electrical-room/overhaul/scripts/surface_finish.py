"""Tactile broad finishes and restrained service-edge history, judged in pixels."""
import bpy


def apply(k, m):
    # Concrete remains mineral and matte; painted steel/epoxy have finer relief
    # and more selective highlights. All noise is3D, not an image/flat decal map.
    profiles = {
        'cream':((.48,.46,.39), .83,1.14, 3.8, (.73,.96), .0026,.50,38),
        'slate':((.071,.092,.114), .70,1.18, 2.6, (.43,.83), .00090,.40,65),
        'enamel':((.38,.395,.365), .76,1.15, 3.0, (.32,.70), .00065,.36,75),
        'floor':((.225,.24,.226), .64,1.20, 1.3, (.74,.95), .0018,.50,55),
        'route':((.32,.295,.244), .73,1.15, 1.55, (.60,.88), .00065,.34,90),
    }
    for name,(color,low,high,macro,rough,depth,strength,grain) in profiles.items():
        mat=m[name];nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF')
        mat.diffuse_color=(*color,1)
        ramp=next(n for n in nt.nodes if n.type=='VALTORGB')
        ramp.color_ramp.elements[0].color=(*(v*low for v in color),1)
        ramp.color_ramp.elements[1].color=(*(v*high for v in color),1)
        ramp.color_ramp.elements[0].position=.30;ramp.color_ramp.elements[1].position=.70
        noise=ramp.inputs[0].links[0].from_node
        noise.inputs['Scale'].default_value=macro;noise.inputs['Detail'].default_value=3
        mapper=next(n for n in nt.nodes if n.type=='MAP_RANGE')
        mapper.inputs['To Min'].default_value=rough[0];mapper.inputs['To Max'].default_value=rough[1]
        bump=next(n for n in nt.nodes if n.type=='BUMP')
        bump.inputs['Distance'].default_value=depth;bump.inputs['Strength'].default_value=strength
        fine=bump.inputs['Height'].links[0].from_node
        fine.inputs['Scale'].default_value=grain;fine.inputs['Detail'].default_value=3
        if name in {'enamel','slate','route'}:
            bs.inputs['Coat Weight'].default_value=.10
            bs.inputs['Coat Roughness'].default_value=.40

    # Fixed phases keep coating breakup distinct across the four separately
    # maintained leaves, including when this library is instanced in the map.
    # Object Info randomness would change with the consuming instance context.
    leaves=sorted((o for o in bpy.data.objects if o.name.startswith('Parked sliding leaf')),key=lambda o:o.name)
    assert len(leaves)==4
    phases=[]
    for i,leaf in enumerate(leaves):
        phase=(1.43*i,.57*i,.23*i)
        mat=m['enamel'].copy();mat.name=k.PREFIX+'Leaf '+str(i+1)+' individual coating'
        nt=mat.node_tree;tc=next(n for n in nt.nodes if n.type=='TEX_COORD')
        offset=nt.nodes.new('ShaderNodeVectorMath');offset.operation='ADD'
        offset.inputs[1].default_value=phase
        nt.links.new(tc.outputs['Object'],offset.inputs[0])
        for noise in [n for n in nt.nodes if n.type=='TEX_NOISE']:
            nt.links.new(offset.outputs['Vector'],noise.inputs['Vector'])
        assigned=0
        for slot in leaf.material_slots:
            if slot.material==m['enamel']:
                slot.material=mat;assigned+=1
        assert assigned==1,leaf.name
        phases.append({'leaf':leaf.name,'coordinate_offset':phase,'material':mat.name})

    # A broken, restrained polish band follows actual central foot traffic in
    # the epoxy. It changes surface response without raising the walking floor.
    nt=m['route'].node_tree;bs=nt.nodes.get('Principled BSDF')
    tc=next(n for n in nt.nodes if n.type=='TEX_COORD')
    sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(tc.outputs['Object'],sep.inputs[0])
    absx=nt.nodes.new('ShaderNodeMath');absx.operation='ABSOLUTE';nt.links.new(sep.outputs['X'],absx.inputs[0])
    band=nt.nodes.new('ShaderNodeMapRange');band.clamp=True
    band.inputs['From Min'].default_value=.18;band.inputs['From Max'].default_value=.76
    band.inputs['To Min'].default_value=1;band.inputs['To Max'].default_value=0
    nt.links.new(absx.outputs[0],band.inputs[0])
    noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7;noise.inputs['Detail'].default_value=3
    nt.links.new(tc.outputs['Object'],noise.inputs['Vector'])
    product=nt.nodes.new('ShaderNodeMath');product.operation='MULTIPLY'
    nt.links.new(band.outputs[0],product.inputs[0]);nt.links.new(noise.outputs['Fac'],product.inputs[1])
    strength=nt.nodes.new('ShaderNodeMath');strength.operation='MULTIPLY';strength.inputs[1].default_value=.22
    nt.links.new(product.outputs[0],strength.inputs[0])
    subtract=nt.nodes.new('ShaderNodeMath');subtract.operation='SUBTRACT';subtract.use_clamp=True
    old=bs.inputs['Roughness'].links[0].from_socket;nt.links.new(old,subtract.inputs[0])
    nt.links.new(strength.outputs[0],subtract.inputs[1]);nt.links.new(subtract.outputs[0],bs.inputs['Roughness'])

    history=bpy.data.materials[k.PREFIX+'Floor contact history']
    ramp=next(n for n in history.node_tree.nodes if n.type=='VALTORGB')
    for e,factor in zip(ramp.color_ramp.elements,(.83,1.08)):
        e.color=(*[v*factor for v in (.125,.132,.12)],1)

    # Existing work-position wear and material traffic response carry the floor
    # history. The rejected separate polygon-patch layer is deliberately absent.

    # The light hierarchy remains tied to the existing practicals. Lower bridge
    # illumination slightly and strengthen the actual repair/transformer pools.
    powers={'Entry fluorescent light':85,'Rear hall practical light':105,
            'West rear practical light':250,'Transformer task practical light':375,
            'Reserve bay practical light':255,'EOH | Bench practical':42}
    for name,power in powers.items():
        bpy.data.objects[name].data.energy=power
    bpy.context.scene['electrical_surface_finish_revision']='R6'
    return {'material_profiles':list(profiles),'practical_powers_watts':powers,
            'individual_leaf_coating_phases':phases,
            'new_registered_service_assemblies':0,'localized_floor_contacts':0,
            'new_floor_polygon_layer_omitted':True}
