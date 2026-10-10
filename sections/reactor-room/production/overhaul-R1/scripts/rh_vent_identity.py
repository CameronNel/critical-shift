"""Identify the retained guarded vent assembly on its existing front plaque."""
import json
import bpy


def build():
    scene = bpy.context.scene
    assert 'rh_vent_identity_correction' not in scene, 'Vent identity already applied'
    plaque = bpy.data.objects['Vent label']
    legend = bpy.data.objects['Vent label.legend']
    assert plaque.type == legend.type == 'MESH'
    assert not legend.animation_data and not legend.data.animation_data
    assert len(legend.data.materials) == 1
    assert all(abs(v.co.z) < 1e-6 for v in legend.data.vertices)
    # Preserve the existing face plane, transform, ivory finish and plaque mount.
    curve = bpy.data.curves.new('RH vent identity temporary', 'FONT')
    curve.body = 'V-03\nVENT\nDAMPER'
    curve.size = .0675
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.resolution_u = 8
    temp = bpy.data.objects.new('RH vent identity temporary', curve)
    legend.users_collection[0].objects.link(temp)
    bpy.context.view_layer.update()
    mesh = bpy.data.meshes.new_from_object(temp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    inverse = legend.matrix_world.inverted()
    panel = [inverse @ (plaque.matrix_world @ v.co) for v in plaque.data.vertices]
    # Keep generous edge margins inside the measured 390 x 350 mm plaque.
    for axis in (0, 1):
        assert min(v.co[axis] for v in mesh.vertices) >= min(p[axis] for p in panel) + .025
        assert max(v.co[axis] for v in mesh.vertices) <= max(p[axis] for p in panel) - .025
    mesh.materials.append(legend.data.materials[0])
    old = legend.data
    legend.data = mesh
    bpy.data.objects.remove(temp, do_unlink=True)
    bpy.data.curves.remove(curve)
    if old.users == 0:
        bpy.data.meshes.remove(old)
    record = {'object': legend.name, 'body': 'V-03 / VENT / DAMPER',
              'size_m': .0675, 'mount': plaque.name,
              'scope': 'Existing front plaque and ivory finish retained; only legend mesh replaced.'}
    scene['rh_vent_identity_correction'] = json.dumps(record)
    bpy.context.view_layer.update()
    print('VENT_IDENTITY_CORRECTION', scene['rh_vent_identity_correction'], flush=True)
