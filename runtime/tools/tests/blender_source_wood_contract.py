"""Run in Blender on the pinned mine module; never save the opened source.

blender -b module_r39_aaa.blend --disable-autoexec --python-exit-code 1 \
    --python runtime/tools/tests/blender_source_wood_contract.py -- report.json
"""
import hashlib
import json
from pathlib import Path
import sys
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from export_source_wood import inspect, RECIPE

source = Path(bpy.data.filepath)
before = hashlib.sha256(source.read_bytes()).hexdigest()
supported = [m for m in list(bpy.data.materials) if inspect(m)]
assert len(supported) == 8, [m.name for m in supported]
template = next(m for m in supported if any(n.type == "AMBIENT_OCCLUSION" for n in m.node_tree.nodes))
rejected = []
for case in ("nonlinear-grain", "grain-dependent-ao", "tilted-uv", "changed-image-wrap", "invalid-bump-width", "linked-bump-width"):
    material = template.copy()
    tree = material.node_tree
    grain = tree.nodes[inspect(material)["clampNode"]].outputs["Result"]
    if case == "nonlinear-grain":
        node = tree.nodes.new("ShaderNodeMath")
        node.operation = "MULTIPLY"
        tree.links.new(grain, node.inputs[0])
        tree.links.new(grain, node.inputs[1])
        bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
        tree.links.new(node.outputs[0], bsdf.inputs["Base Color"])
    elif case == "grain-dependent-ao":
        ao = next(n for n in tree.nodes if n.type == "AMBIENT_OCCLUSION")
        tree.links.new(grain, ao.inputs["Distance"])
    elif case == "tilted-uv":
        mapping = next(n for n in tree.nodes if n.type == "MAPPING")
        mapping.inputs["Rotation"].default_value.x = .25
    elif case == "invalid-bump-width":
        next(n for n in tree.nodes if n.type == "BUMP").inputs["Filter Width"].default_value = 0
    elif case == "linked-bump-width":
        node = tree.nodes.new("ShaderNodeValue")
        tree.links.new(node.outputs[0], next(n for n in tree.nodes if n.type == "BUMP").inputs["Filter Width"])
    else:
        image = next(n for n in tree.nodes if n.type == "TEX_IMAGE" and n.image.name == "rough_wood_diff_1k.jpg")
        image.extension = "CLIP"
    try:
        inspect(material)
    except ValueError as error:
        rejected.append({"case": case, "reason": str(error)})
    else:
        raise AssertionError("Unsupported shader was accepted: " + case)
    bpy.data.materials.remove(material)

assert hashlib.sha256(source.read_bytes()).hexdigest() == before
report = {
    "status": "Passed", "recipe": RECIPE,
    "supportedMaterials": sorted(m.name for m in supported), "negativeControls": rejected,
    "sourceSha256": before, "sourceModified": False,
    "scriptSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "limits": "Source graph contract only; final native lighting and appearance require separate validation."
}
output = Path(sys.argv[sys.argv.index("--") + 1])
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2) + "\n")
print("CS_SOURCE_WOOD_CONTRACT_OK; supported=8; rejected=6", flush=True)
