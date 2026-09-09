"""Stylized but tactile materials. Low-frequency variation only. No teal paint."""
import bpy

M = {}


def _principled(mat):
    return mat.node_tree.nodes.get("Principled BSDF")


def make(name, color, rough=0.7, metal=0.0, spec=0.35, variation=0.05, bump=0.0, scale=1.6, trans=0.0, ior=1.45, emit=None, emit_str=0.0, coat=0.0):
    mat = bpy.data.materials.new("OCRU_" + name)
    mat.use_nodes = True
    mat.diffuse_color = (*color, 1.0)
    nt = mat.node_tree
    n, l = nt.nodes, nt.links
    p = _principled(mat)
    p.inputs["Base Color"].default_value = (*color, 1.0)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Specular IOR Level"].default_value = spec
    p.inputs["IOR"].default_value = ior
    if "Transmission Weight" in p.inputs:
        p.inputs["Transmission Weight"].default_value = trans
    if coat and "Coat Weight" in p.inputs:
        p.inputs["Coat Weight"].default_value = coat
        p.inputs["Coat Roughness"].default_value = 0.35
    if emit is not None:
        p.inputs["Emission Color"].default_value = (*emit, 1.0)
        p.inputs["Emission Strength"].default_value = emit_str
        mat.use_nodes = True
    if variation:
        coord = n.new("ShaderNodeTexCoord")
        noise = n.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = scale
        noise.inputs["Detail"].default_value = 1.4
        noise.inputs["Roughness"].default_value = 0.45
        l.new(coord.outputs["Object"], noise.inputs["Vector"])
        ramp = n.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.35
        ramp.color_ramp.elements[0].color = tuple(max(0, c * (1 - variation)) for c in color) + (1,)
        ramp.color_ramp.elements[1].position = 0.72
        ramp.color_ramp.elements[1].color = tuple(min(1, c * (1 + variation)) for c in color) + (1,)
        l.new(noise.outputs["Fac"], ramp.inputs[0])
        l.new(ramp.outputs["Color"], p.inputs["Base Color"])
        rmap = n.new("ShaderNodeMapRange")
        rmap.inputs["To Min"].default_value = max(0.03, rough - 0.05)
        rmap.inputs["To Max"].default_value = min(0.98, rough + 0.06)
        l.new(noise.outputs["Fac"], rmap.inputs[0])
        l.new(rmap.outputs[0], p.inputs["Roughness"])
        if bump:
            b = n.new("ShaderNodeBump")
            b.inputs["Strength"].default_value = 0.18
            b.inputs["Distance"].default_value = bump
            l.new(noise.outputs["Fac"], b.inputs["Height"])
            l.new(b.outputs["Normal"], p.inputs["Normal"])
    mat["family"] = name
    mat["roughness_base"] = rough
    M[name] = mat
    return mat


def stripe(name, a, b, scale=18.0, angle=45.0):
    mat = make(name, a, rough=0.55, metal=0.04, variation=0.0)
    nt = mat.node_tree
    n, l = nt.nodes, nt.links
    p = _principled(mat)
    coord = n.new("ShaderNodeTexCoord")
    mapn = n.new("ShaderNodeMapping")
    mapn.inputs["Rotation"].default_value[2] = angle * 3.14159 / 180.0
    mapn.inputs["Scale"].default_value = (scale, scale, scale)
    wave = n.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "DIAGONAL"
    wave.inputs["Scale"].default_value = 1.0
    wave.inputs["Distortion"].default_value = 0.0
    mix = n.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*a, 1)
    mix.inputs["B"].default_value = (*b, 1)
    l.new(coord.outputs["Object"], mapn.inputs["Vector"])
    l.new(mapn.outputs["Vector"], wave.inputs["Vector"])
    l.new(wave.outputs["Color"], mix.inputs["Factor"])
    l.new(mix.outputs["Result"], p.inputs["Base Color"])
    return mat


def image_mat(name, image, rough=0.55, emit=0.0, trans=0.0):
    mat = bpy.data.materials.new("OCRU_" + name)
    mat.use_nodes = True
    nt = mat.node_tree
    n, l = nt.nodes, nt.links
    p = _principled(mat)
    tex = n.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Closest"
    coord = n.new("ShaderNodeTexCoord")
    l.new(coord.outputs["UV"], tex.inputs["Vector"])
    l.new(tex.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    if emit:
        l.new(tex.outputs["Color"], p.inputs["Emission Color"])
        p.inputs["Emission Strength"].default_value = emit
    if trans:
        p.inputs["Transmission Weight"].default_value = trans
        mat.blend_method = "BLEND"
        p.inputs["Alpha"].default_value = 0.92
    M[name] = mat
    return mat


def build():
    M.clear()
    make("wall", (0.28, 0.29, 0.30), rough=0.92, variation=0.07, bump=0.0012, scale=0.5)
    make("wall_upper", (0.32, 0.325, 0.33), rough=0.90, variation=0.05, bump=0.0007, scale=0.65)
    make("trim", (0.18, 0.19, 0.20), rough=0.62, metal=0.08, variation=0.04, scale=2.2)
    make("floor", (0.14, 0.15, 0.155), rough=0.82, variation=0.14, bump=0.0024, scale=0.4, coat=0.02)
    make("floor_mark", (0.78, 0.78, 0.76), rough=0.55, variation=0.02, scale=3)
    make("shell", (0.48, 0.47, 0.44), rough=0.64, metal=0.08, variation=0.05, bump=0.0005, scale=1.4)
    make("shell_dark", (0.22, 0.23, 0.24), rough=0.55, metal=0.10, variation=0.03, scale=2)
    make("chamber", (0.10, 0.14, 0.16), rough=0.48, metal=0.08, variation=0.04, scale=1.8)
    make("graphite", (0.10, 0.105, 0.11), rough=0.48, metal=0.18, variation=0.03, scale=2.4)
    make("steel", (0.38, 0.40, 0.41), rough=0.28, metal=0.82, spec=0.5, variation=0.04, scale=4.0)
    make("darksteel", (0.08, 0.085, 0.09), rough=0.42, metal=0.72, variation=0.03, scale=3.5)
    make("brushed", (0.48, 0.50, 0.51), rough=0.36, metal=0.78, variation=0.03, scale=6)
    make("rubber", (0.035, 0.036, 0.038), rough=0.92, spec=0.18, variation=0.04, bump=0.0006, scale=8)
    make("pad", (0.028, 0.03, 0.032), rough=0.92, spec=0.16, variation=0.05, scale=3)
    make("orange_pad", (0.55, 0.22, 0.05), rough=0.74, variation=0.04, scale=2.5)
    make("fabric", (0.42, 0.42, 0.40), rough=0.95, spec=0.12, variation=0.06, bump=0.001, scale=5)
    make("glass", (0.72, 0.82, 0.86), rough=0.04, spec=0.6, variation=0.0, trans=1.0, ior=1.48)
    make("glass_dark", (0.12, 0.16, 0.18), rough=0.06, variation=0.0, trans=0.85, ior=1.5)
    make("plastic", (0.16, 0.17, 0.18), rough=0.46, variation=0.03, scale=4)
    make("plastic_light", (0.55, 0.56, 0.54), rough=0.44, variation=0.02, scale=3)
    make("paper", (0.78, 0.74, 0.62), rough=0.96, variation=0.02, scale=8)
    make("ink", (0.07, 0.08, 0.08), rough=0.85, variation=0.0)
    make("tile", (0.58, 0.57, 0.54), rough=0.48, variation=0.05, bump=0.0005, scale=3.2, coat=0.08)
    make("grate", (0.12, 0.13, 0.13), rough=0.40, metal=0.55, variation=0.04, scale=5)
    make("yellow", (0.62, 0.42, 0.06), rough=0.55, metal=0.04, variation=0.03, scale=3)
    make("amber", (0.70, 0.28, 0.04), rough=0.48, variation=0.02)
    make("red", (0.48, 0.05, 0.04), rough=0.46, variation=0.02)
    make("wood", (0.28, 0.18, 0.10), rough=0.72, variation=0.06, scale=2)
    make("liquid", (0.55, 0.72, 0.62), rough=0.12, variation=0.0, trans=0.7, ior=1.38)
    make("screen", (0.02, 0.06, 0.08), rough=0.22, variation=0.0, emit=(0.15, 0.55, 0.62), emit_str=3.2)
    make("lamp", (1.0, 0.84, 0.62), rough=0.35, variation=0.0, emit=(1.0, 0.82, 0.58), emit_str=6.0)
    make("lamp_orange", (1.0, 0.45, 0.12), rough=0.4, variation=0.0, emit=(1.0, 0.42, 0.08), emit_str=8.0)
    make("cyan", (0.25, 0.85, 0.95), rough=0.25, variation=0.0, emit=(0.2, 0.75, 0.95), emit_str=12.0)
    make("led_amber", (1.0, 0.45, 0.05), rough=0.3, variation=0.0, emit=(1.0, 0.4, 0.02), emit_str=18.0)
    make("led_red", (1.0, 0.08, 0.04), rough=0.3, variation=0.0, emit=(1.0, 0.05, 0.02), emit_str=10.0)
    make("led_green", (0.15, 0.85, 0.25), rough=0.3, variation=0.0, emit=(0.1, 0.9, 0.2), emit_str=8.0)
    stripe("hazard", (0.72, 0.52, 0.08), (0.06, 0.06, 0.06), scale=9.0, angle=45)
    stripe("hazard_fine", (0.72, 0.52, 0.08), (0.06, 0.06, 0.06), scale=22.0, angle=45)
