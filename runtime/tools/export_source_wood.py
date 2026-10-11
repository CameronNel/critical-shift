"""Retain authored wood detail images; bake only their spatial colour coefficients."""
import hashlib
import math
from pathlib import Path

RECIPE = "authored-uv-affine-colour-ao16-v1"


def inspect(material):
    tree = material.node_tree
    images = [n for n in tree.nodes if n.type == "TEX_IMAGE" and n.image]
    diffuse = next((n for n in images if n.image.name == "rough_wood_diff_1k.jpg"), None)
    if diffuse is None:
        return None
    normal = next((n for n in images if n.image.name == "rough_wood_nor_gl_1k.jpg"), None)
    if diffuse.image.colorspace_settings.name != "sRGB" or (normal is not None and normal.image.colorspace_settings.name != "Non-Color"):
        raise ValueError("Unsupported source wood image colour spaces: " + material.name)
    if any(n.projection != "FLAT" or n.extension != "REPEAT" or n.interpolation != "Linear"
           for n in (diffuse, normal) if n is not None):
        raise ValueError("Unsupported source wood image sampling: " + material.name)
    def upstream(socket):
        if not socket.is_linked: raise ValueError("Missing source wood input: " + material.name)
        return socket.links[0].from_node
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    bump = upstream(bsdf.inputs["Normal"])
    if normal is None or bump.type != "BUMP" or bump.invert:
        raise ValueError("Unsupported source wood normal: " + material.name)
    normal_map = upstream(bump.inputs["Normal"])
    clamp = upstream(bump.inputs["Height"])
    if normal_map.type != "NORMAL_MAP" or normal_map.space != "TANGENT" or upstream(normal_map.inputs["Color"]) != normal or clamp.type != "CLAMP":
        raise ValueError("Unsupported source wood detail graph: " + material.name)
    divide = upstream(clamp.inputs["Value"])
    luminance = upstream(divide.inputs[0])
    if divide.type != "MATH" or divide.operation != "DIVIDE" or divide.inputs[1].is_linked or luminance.type != "RGBTOBW" or upstream(luminance.inputs["Color"]) != diffuse:
        raise ValueError("Unsupported source wood grayscale: " + material.name)
    mapping = upstream(diffuse.inputs["Vector"])
    uv = upstream(mapping.inputs["Vector"])
    if mapping.type != "MAPPING" or mapping.vector_type != "POINT" or upstream(normal.inputs["Vector"]) != mapping or uv.type != "UVMAP" or normal_map.uv_map != uv.uv_map:
        raise ValueError("Source wood images must share their authored UV frame: " + material.name)
    for socket in [divide.inputs[1], clamp.inputs["Min"], clamp.inputs["Max"], normal_map.inputs["Strength"], bump.inputs["Strength"], bump.inputs["Distance"], bump.inputs["Filter Width"], *list(mapping.inputs)[1:]]:
        if socket.is_linked: raise ValueError("Linked wood detail parameter requires an explicit export: " + material.name)
    width = float(bump.inputs["Filter Width"].default_value)
    if not math.isfinite(width) or width <= 0:
        raise ValueError("Invalid source wood bump filter width: " + material.name)
    rotation = mapping.inputs["Rotation"].default_value
    if abs(rotation.x) > 1e-7 or abs(rotation.y) > 1e-7:
        raise ValueError("Unsupported tilted source wood UV mapping: " + material.name)
    if divide.inputs[1].default_value <= 0:
        raise ValueError("Invalid source wood grayscale divisor")
    if clamp.clamp_type != "MINMAX" or clamp.inputs["Min"].default_value > clamp.inputs["Max"].default_value:
        raise ValueError("Unsupported source wood clamp: " + material.name)

    # The base colour must be affine in the clamped grain signal. Multiplication
    # by spatial weathering and mixes with independent paint remain affine.
    memo = {}
    def depends(socket):
        if not socket.is_linked: return False
        output = socket.links[0].from_socket
        node = output.node
        if node == clamp: return True
        key = (node.name, output.name)
        if key in memo: return memo[key]
        if node.type == "AMBIENT_OCCLUSION":
            if any(depends(s) for s in node.inputs if s.name != "Color"):
                raise ValueError("Grain-dependent source wood AO: " + material.name)
            if output.name == "AO": return False
        values = [depends(s) for s in node.inputs]
        dependent = any(values)
        if dependent:
            if node.type == "MATH":
                valid = node.operation in {"ADD", "SUBTRACT"} or (node.operation == "MULTIPLY" and sum(values[:2]) <= 1) or (node.operation == "DIVIDE" and not values[1])
                valid = valid and not node.use_clamp
            elif node.type == "MIX_RGB":
                valid = not values[0] and (node.blend_type == "MIX" or (node.blend_type == "MULTIPLY" and sum(values[1:]) <= 1)) and not node.use_clamp
            elif node.type == "COMBINE_COLOR": valid = node.mode == "RGB"
            elif node.type == "AMBIENT_OCCLUSION": valid = output.name == "Color"
            else: valid = False
            if not valid: raise ValueError("Non-affine source wood colour node: " + material.name + " / " + node.name)
        memo[key] = dependent
        return dependent
    if not depends(bsdf.inputs["Base Color"]) or depends(bsdf.inputs["Roughness"]):
        raise ValueError("Unsupported wood colour/roughness coupling: " + material.name)
    return dict(clampNode=clamp.name, diffuse=diffuse.image, normal=normal.image,
        divisor=float(divide.inputs[1].default_value), minimum=float(clamp.inputs["Min"].default_value),
        maximum=float(clamp.inputs["Max"].default_value), normalStrength=float(normal_map.inputs["Strength"].default_value),
        bumpStrength=float(bump.inputs["Strength"].default_value), bumpDistance=float(bump.inputs["Distance"].default_value), bumpFilterWidth=width,
        uvScale=list(mapping.inputs["Scale"].default_value)[:2], uvOffset=list(mapping.inputs["Location"].default_value)[:2],
        uvRotation=float(rotation.z), sourceUvLayer=uv.uv_map)


def export(material, output):
    detail = inspect(material)
    if detail is None: return None
    result = {key: value for key, value in detail.items() if key not in {"diffuse", "normal"}}
    for key, color_space in (("diffuse", "sRGB"), ("normal", "linear")):
        image = detail[key]
        file = output / "Surfaces/source-wood" / image.name
        file.parent.mkdir(parents=True, exist_ok=True)
        if image.packed_file: data = image.packed_file.data
        else:
            import bpy
            data = Path(bpy.path.abspath(image.filepath, library=image.library)).read_bytes()
        if not file.exists() or file.read_bytes() != data: file.write_bytes(data)
        result[key] = dict(file=file.relative_to(output).as_posix(), sha256=hashlib.sha256(data).hexdigest(),
            colorSpace=color_space, size=max(image.size))
    return result
