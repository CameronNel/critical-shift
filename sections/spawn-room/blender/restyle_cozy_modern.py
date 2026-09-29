#!/usr/bin/env python3
"""
Spawn Room palette/lighting restyle: highly stylized, modern, cozy.

Run headlessly (Blender 5.2 / bpy):
    python restyle_cozy_modern.py <input.blend> <output.blend>

Recolours through the existing "Reference palette balance" multiply nodes so the
procedural material graphs stay intact, flattens photographic texture contrast
toward a painted read, and re-tints lights (warm practicals, cooler ambient).
Re-running on its own output is safe: it only ever sets absolute values.
"""

import sys

import bpy

# sRGB hex targets, converted to linear at apply time.
PALETTE = {
    # hall
    "V13_HALL_wall": "#8E7F92",
    "V13_HALL_dado": "#2B3350",
    "V13_SERVICE_wall": "#8E7F92",
    "wall": "#8E7F92",
    "dado": "#2B3350",
    # briefing (cozy meeting room)
    "V13_BRIEFING_wall": "#B9776A",
    "V13_BRIEFING_dado": "#2B3350",
    # locker room
    "V13_LOCKER_wall": "#56709F",
    "V13_LOCKER_dado": "#262C45",
    # floors and ceiling
    "floor0": "#4B4E5C",
    "floor1": "#4B4E5C",
    "floor2": "#4B4E5C",
    "floor3": "#4B4E5C",
    "floor4": "#4B4E5C",
    "V_tile0": "#6E7387",
    "V_tile1": "#666B80",
    "V_tile2": "#767B90",
    "V_tile3": "#6E7387",
    "V_tile4": "#7A7F93",
    "V_tile5": "#62677B",
    "V_ceiling_mineral": "#CDC5CA",
    "V13_LOCKER_V_ceiling_mineral": "#CDC5CA",
    # lockers, rug
    "V_locker_steel": "#B55B4B",
    "rug_field": "#2B3350",
    "rug_cream": "#E8A33D",
    "rug_border": "#1D2238",
    # briefing floor timber, benches
    "floor_timber_0": "#8E6038",
    "floor_timber_1": "#885B34",
    "floor_timber_2": "#93663E",
    "floor_timber_3": "#8B5D36",
    "floor_timber_4": "#8E6038",
    # neutral machine-grey metals (the source tint read teal on the airlock hatch)
    "steel": "#9A9EA5",
    "pressure_metal": "#8C9097",
    "V_pod_satin_metal": "#7E8288",
    "V_brushed": "#94989E",
    "darksteel": "#2A2C31",
    "V_graphite": "#33353A",
    "V_reference_charcoal": "#666A71",
    "bench_worn_timber": "#5A3826",
}

# Metals that read as tinted because they mirror coloured rooms: let the base grey show through.
METAL_TWEAKS = {"V_brushed": 0.35, "steel": 0.7, "pressure_metal": 0.7}

# 0 keeps the source texture contrast, 1 flattens to a plain painted colour.
FLATTEN = 0.65


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_to_linear(h):
    h = h.lstrip("#")
    return tuple(srgb_to_linear(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))


def principled(mat):
    for n in mat.node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED":
            return n
    return None


def recolor_by_luminance(nt, base, target):
    """Keep the source texture's brightness variation, replace its hue with target."""
    if nt.nodes.get("CS_lum") is None:
        src_socket = base.links[0].from_socket
        bw = nt.nodes.new("ShaderNodeRGBToBW")
        bw.name = "CS_lum"
        rng = nt.nodes.new("ShaderNodeMapRange")
        rng.name = "CS_lum_range"
        rng.clamp = True
        rng.inputs["From Min"].default_value = 0.0
        rng.inputs["From Max"].default_value = 0.6
        rng.inputs["To Min"].default_value = 0.8
        rng.inputs["To Max"].default_value = 1.2
        mul = nt.nodes.new("ShaderNodeMixRGB")
        mul.name = "CS_recolor"
        mul.blend_type = "MULTIPLY"
        mul.inputs["Fac"].default_value = 1.0
        nt.links.new(src_socket, bw.inputs["Color"])
        nt.links.new(bw.outputs["Val"], rng.inputs["Value"])
        nt.links.new(rng.outputs["Result"], mul.inputs["Color2"])
        nt.links.new(mul.outputs["Color"], base)
    nt.nodes["CS_recolor"].inputs["Color1"].default_value = (*target, 1.0)
    return True


def recolor(mat, hex_color):
    nt = mat.node_tree
    bsdf = principled(mat)
    if bsdf is None:
        return False
    target = hex_to_linear(hex_color)
    base = bsdf.inputs["Base Color"]
    if not base.is_linked:
        base.default_value = (*target, 1.0)
        return True

    # Each graph carries a named "Reference palette balance" multiply node; walls
    # add a further detail-overlay multiply after it, so find it by name.
    tint = next((n for n in nt.nodes if n.name.startswith("Reference palette balance")), None)
    if tint is None:
        src = base.links[0].from_node
        if src.type == "MIX_RGB" and src.blend_type == "MULTIPLY":
            return recolor_by_luminance(nt, base, target)
        tint = nt.nodes.new("ShaderNodeMixRGB")
        tint.blend_type = "MULTIPLY"
        tint.inputs["Fac"].default_value = 1.0
        nt.links.new(base.links[0].from_socket, tint.inputs["Color1"])
        nt.links.new(tint.outputs["Color"], base)

    # Flatten texture contrast toward mid grey once (idempotent by node name).
    flat = nt.nodes.get("CS_flatten")
    if flat is None:
        flat = nt.nodes.new("ShaderNodeMixRGB")
        flat.name = flat.label = "CS_flatten"
        flat.blend_type = "MIX"
        flat.inputs["Color2"].default_value = (0.5, 0.5, 0.5, 1.0)
        c1 = tint.inputs["Color1"]
        if c1.is_linked:
            nt.links.new(c1.links[0].from_socket, flat.inputs["Color1"])
        else:
            flat.inputs["Color1"].default_value = c1.default_value
        nt.links.new(flat.outputs["Color"], c1)
    flat.inputs["Fac"].default_value = FLATTEN

    # Mid-grey (0.5) x 2 = identity, so Color2 = target x 2 lands on the target.
    tint.inputs["Color2"].default_value = (*(min(v * 2.0, 4.0) for v in target), 1.0)
    return True


def retint_lights():
    warm = (1.0, 0.86, 0.70)
    neutral = (0.98, 0.95, 0.92)
    for light in bpy.data.lights:
        light.color = neutral
    for obj in bpy.data.objects:
        if obj.type != "LIGHT" or obj.name.startswith("COZY_"):
            continue
        name = obj.name.upper()
        if "BRIEFING" in name or "LOCKER" in name or "PPE" in name:
            obj.data.color = warm
            # Dim the ceiling fluorescents so lamps and string lights carry the mood.
            # The original energy is stored once so re-runs stay idempotent.
            if "photometric" in obj.name:
                if "cs_base_energy" not in obj.data:
                    obj.data["cs_base_energy"] = obj.data.energy
                obj.data.energy = obj.data["cs_base_energy"] * 0.55
    world = bpy.context.scene.world
    if world and world.node_tree:
        for n in world.node_tree.nodes:
            if n.type == "BACKGROUND":
                n.inputs["Color"].default_value = (0.32, 0.36, 0.55, 1.0)


def main():
    src, dst = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[-2:]
    bpy.ops.wm.open_mainfile(filepath=src)
    done, missing = [], []
    for name, hex_color in PALETTE.items():
        mat = bpy.data.materials.get(name)
        if mat is None or not mat.use_nodes:
            missing.append(name)
            continue
        if recolor(mat, hex_color):
            done.append(name)
    for name, metallic in METAL_TWEAKS.items():
        mat = bpy.data.materials.get(name)
        b = principled(mat) if mat is not None and mat.use_nodes else None
        if b is not None:
            b.inputs["Metallic"].default_value = min(b.inputs["Metallic"].default_value, metallic)
    retint_lights()
    bpy.context.scene.view_settings.look = "AgX - Medium High Contrast"
    bpy.context.scene.view_settings.exposure = -0.2
    print("RESTYLE recoloured=%d missing=%s" % (len(done), missing))
    bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True)


if __name__ == "__main__":
    main()
