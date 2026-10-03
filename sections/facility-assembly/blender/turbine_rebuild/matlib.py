"""Materials shared by the room build and the prop test harness."""
import bpy

RIM_STRENGTH = {'MACH': .24, 'PROPS': .21, 'ARCH': .14, 'SHAFT': .24}

def make_mats(atlas, orm, grp):
    """Bake-ready PBR material (albedo atlas on UV0) and the emissive twin for lamps / screens."""
    def mk(name, emissive):
        m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
        out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (700, 0)
        uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'UVMap'; uvn.location = (-500, 0)
        tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = atlas; tex.interpolation = 'Linear'; tex.name = 'ALBEDO'; tex.location = (-250, 0)
        nt.links.new(uvn.outputs[0], tex.inputs[0])
        if emissive:
            e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Strength'].default_value = 2.0; e.location = (300, 0)
            nt.links.new(tex.outputs[0], e.inputs['Color']); nt.links.new(e.outputs[0], out.inputs['Surface'])
        else:
            p = nt.nodes.new('ShaderNodeBsdfPrincipled'); p.location = (300, 0)
            nt.links.new(tex.outputs[0], p.inputs['Base Color'])
            ot = nt.nodes.new('ShaderNodeTexImage'); ot.image = orm; ot.name = 'ORM'; ot.location = (-250, -300); nt.links.new(uvn.outputs[0], ot.inputs[0])
            sp = nt.nodes.new('ShaderNodeSeparateColor'); sp.location = (50, -300); nt.links.new(ot.outputs[0], sp.inputs[0])
            nt.links.new(sp.outputs['Green'], p.inputs['Roughness']); nt.links.new(sp.outputs['Blue'], p.inputs['Metallic'])
            # stylised silhouette rim (cool, thin, grazing-angle only): keeps dark hero forms readable. Must be reproduced in the runtime shader.
            lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = .3; lw.location = (50, 300)
            cr = nt.nodes.new('ShaderNodeValToRGB'); cr.location = (250, 300); cr.color_ramp.elements[0].position = .78; cr.color_ramp.elements[1].position = .985
            nt.links.new(lw.outputs['Facing'], cr.inputs['Fac'])
            mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = RIM_STRENGTH.get(grp, .5); mu.location = (450, 300); nt.links.new(cr.outputs['Color'], mu.inputs[0])
            em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (.5, .6, .8, 1); em.inputs['Strength'].default_value = 1.5; em.location = (450, 150)
            mx = nt.nodes.new('ShaderNodeMixShader'); mx.location = (550, 0)
            nt.links.new(mu.outputs[0], mx.inputs['Fac']); nt.links.new(p.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs['Surface'])
        return m
    return mk(f'M_{grp}', False), mk(f'M_{grp}_emissive', True)

def make_decal_mat(name, image, emissive, strength=2.2):
    """Alpha-blended decal: lit (Principled) or emissive screen (Emission through alpha). Runtime needs alpha blend + shadow-off + depth bias."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (600, 0)
    uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'UVMap'
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = image; tex.interpolation = 'Linear'; tex.extension = 'CLIP'; tex.name = 'DECAL'
    nt.links.new(uvn.outputs[0], tex.inputs[0])
    if emissive:
        e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Strength'].default_value = strength; nt.links.new(tex.outputs['Color'], e.inputs['Color'])
        tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader')
        nt.links.new(tex.outputs['Alpha'], mx.inputs['Fac']); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(e.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs['Surface'])
    else:
        p = nt.nodes.new('ShaderNodeBsdfPrincipled'); p.inputs['Roughness'].default_value = .55; p.inputs['Specular IOR Level'].default_value = .35
        nt.links.new(tex.outputs['Color'], p.inputs['Base Color']); nt.links.new(tex.outputs['Alpha'], p.inputs['Alpha']); nt.links.new(p.outputs[0], out.inputs['Surface'])
    m.surface_render_method = 'BLENDED'
    return m
