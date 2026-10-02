"""Checkpoint palette/light changes, proving no geometry or assignment change."""
import argparse, hashlib, json, os, sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from palette_finish import apply

p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
p.add_argument('--receipt', required=True)
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
source = Path(bpy.data.filepath).resolve()
output = Path(a.output).resolve()
assert source != output
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
input_sha = sha(source)

def geometry_signature(o):
    value = {'type': o.type, 'matrix': sum((list(row) for row in o.matrix_world), []),
             'hidden': [o.hide_render, o.hide_viewport],
             'materials': [slot.material.name if slot.material else None for slot in o.material_slots],
             'properties': {key: str(v) for key, v in o.items()},
             'collections': sorted(c.name for c in o.users_collection)}
    if o.type == 'MESH':
        value['vertices'] = [list(v.co) for v in o.data.vertices]
        value['polygons'] = [(list(f.vertices), f.material_index, f.use_smooth) for f in o.data.polygons]
    elif o.type == 'FONT':
        value['body'] = o.data.body
    elif o.type == 'CAMERA':
        value['lens'] = o.data.lens
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()

before = {o.name: geometry_signature(o) for o in bpy.context.scene.objects}

def material_signature(mat):
    def plain(value):
        if isinstance(value, (str, bool, int, float)) or value is None:
            return value
        try:
            return list(value)
        except TypeError:
            return str(value)
    record = {'color': list(mat.diffuse_color), 'use_nodes': mat.use_nodes}
    if mat.use_nodes:
        record['nodes'] = []
        for node in mat.node_tree.nodes:
            item = {'name': node.name, 'type': node.bl_idname,
                    'inputs': [(s.identifier, plain(s.default_value)) for s in node.inputs if hasattr(s, 'default_value')]}
            for key in ['operation', 'blend_type', 'noise_dimensions', 'normalize']:
                if hasattr(node, key):
                    item[key] = plain(getattr(node, key))
            if hasattr(node, 'color_ramp'):
                item['ramp'] = [(stop.position, list(stop.color)) for stop in node.color_ramp.elements]
                item['ramp_interpolation'] = node.color_ramp.interpolation
            record['nodes'].append(item)
        record['links'] = [(link.from_node.name, link.from_socket.identifier,
                            link.to_node.name, link.to_socket.identifier) for link in mat.node_tree.links]
    return hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()

materials_before = {mat.name: material_signature(mat) for mat in bpy.data.materials}
lights_before = {o.name: [o.data.energy, list(o.data.color)] for o in bpy.context.scene.objects if o.type == 'LIGHT'}
unchanged_settings = [bpy.context.scene.view_settings.exposure, bpy.context.scene.view_settings.look,
                      bpy.context.scene.view_settings.view_transform]
changes = apply()
bpy.context.view_layer.update()
assert set(before) == {o.name for o in bpy.context.scene.objects}
assert all(geometry_signature(bpy.data.objects[name]) == signature for name, signature in before.items())
assert unchanged_settings == [bpy.context.scene.view_settings.exposure, bpy.context.scene.view_settings.look,
                             bpy.context.scene.view_settings.view_transform]
changed_materials = sorted(name for name, signature in materials_before.items()
                           if material_signature(bpy.data.materials[name]) != signature)
expected_materials = {'EOH | ' + name for name in changes['material_profiles']}
expected_materials.update('EOH | Leaf ' + str(i) + ' individual coating' for i in range(1, 5))
assert set(changed_materials) == expected_materials
assert set(materials_before) == {mat.name for mat in bpy.data.materials}
assert all([bpy.data.objects[name].data.energy, list(bpy.data.objects[name].data.color)] == values
           for name, values in lights_before.items() if name not in changes['practical_powers_watts'])
assert all(list(bpy.data.objects[name].data.color) == lights_before[name][1]
           for name in changes['practical_powers_watts'])
output.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
assert sha(source) == input_sha
receipt = {'repair_kind': 'owner_palette_and_light_balance', 'input_sha256': input_sha,
           'output_sha256': sha(output), 'declared_changes': changes,
           'all_geometry_matrices_cameras_assignments_visibility_properties_unchanged': True,
           'checked_objects': len(before), 'color_management_unchanged': True,
           'changed_material_definitions': changed_materials,
           'all_other_material_definitions_unchanged': True,
           'all_other_lights_and_all_light_colors_unchanged': True,
           'source_bytes_unchanged': True,
           'scope': 'Owner-directed material and existing practical-light finish. No object, topology, interface, placement, camera, material assignment, or color-management change.'}
Path(a.receipt).resolve().write_text(json.dumps(receipt, indent=2) + '\n')
print('PALETTE_FINISH_SAVED', output, flush=True)
sys.stdout.flush()
sys.stderr.flush()
os._exit(0)
