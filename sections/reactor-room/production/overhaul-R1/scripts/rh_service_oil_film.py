"""A small, reflective service-oil film on the exposed generator floor.

The concrete shader and existing lights stay intact. This thin closed mesh uses
an oil Fresnel interface over tinted transparency, with a clear underside.
"""
import bpy
import bmesh
import json
import math
from mathutils import Vector
import rh_support_registry as SUPPORT

OWNER = 'service oil film'
OBJECT = 'RH floor service oil film'
SURFACE = 'RH floor service oil surface'
UNDERSIDE = 'RH floor service oil underside'
CENTRE = (-8.58, -4.24)
SEGMENTS = 96


def material(name):
    old = bpy.data.materials.get(name)
    if old:
        assert old.users == 0, ('Unexpected oil material users', name)
        bpy.data.materials.remove(old)
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.node_tree.nodes.clear()
    return result


def build():
    old = bpy.data.objects.get(OBJECT)
    if old:
        old_mesh = old.data
        assert old.type == 'MESH' and old_mesh.users == 1
        bpy.data.objects.remove(old, do_unlink=True)
        bpy.data.meshes.remove(old_mesh)
    surface = material(SURFACE)
    tree = surface.node_tree
    out = tree.nodes.new('ShaderNodeOutputMaterial')
    tint = tree.nodes.new('ShaderNodeBsdfTransparent')
    tint.inputs['Color'].default_value = (.78, .65, .42, 1)
    gloss = tree.nodes.new('ShaderNodeBsdfGlossy')
    gloss.inputs['Color'].default_value = (1, 1, 1, 1)
    gloss.inputs['Roughness'].default_value = .025
    fresnel = tree.nodes.new('ShaderNodeFresnel')
    fresnel.inputs['IOR'].default_value = 1.47
    interface = tree.nodes.new('ShaderNodeMixShader')
    tree.links.new(fresnel.outputs[0], interface.inputs[0])
    tree.links.new(tint.outputs[0], interface.inputs[1])
    tree.links.new(gloss.outputs[0], interface.inputs[2])
    path = tree.nodes.new('ShaderNodeLightPath')
    shadow = tree.nodes.new('ShaderNodeMixShader')
    clear = tree.nodes.new('ShaderNodeBsdfTransparent')
    clear.inputs['Color'].default_value = (.9, .9, .9, 1)
    tree.links.new(path.outputs['Is Shadow Ray'], shadow.inputs[0])
    tree.links.new(interface.outputs[0], shadow.inputs[1])
    tree.links.new(clear.outputs[0], shadow.inputs[2])
    tree.links.new(shadow.outputs[0], out.inputs['Surface'])
    underside = material(UNDERSIDE)
    tree = underside.node_tree
    out = tree.nodes.new('ShaderNodeOutputMaterial')
    clear = tree.nodes.new('ShaderNodeBsdfTransparent')
    clear.inputs['Color'].default_value = (.95, .95, .95, 1)
    tree.links.new(clear.outputs[0], out.inputs['Surface'])

    vertices, faces = [], []
    x, y = CENTRE
    for radius, z in ((.92, .002), (.97, .002), (.99, .0014),
                      (1, .00052), (1, 0.0)):
        for i in range(SEGMENTS):
            angle = 2 * math.pi * i / SEGMENTS
            irregular = radius * (1 + .12 * math.cos(3 * angle + .3)
                                  + .06 * math.sin(5 * angle + .7))
            vertices.append((x + .20 * irregular * math.cos(angle),
                             y + .12 * irregular * math.sin(angle), z))
    for ring in range(4):
        for i in range(SEGMENTS):
            j = (i + 1) % SEGMENTS
            faces.append((ring * SEGMENTS + i, (ring + 1) * SEGMENTS + i,
                          (ring + 1) * SEGMENTS + j, ring * SEGMENTS + j))
    top, bottom = len(vertices), len(vertices) + 1
    for i in range(SEGMENTS):
        j = (i + 1) % SEGMENTS
        faces.extend(((top, i, j), (bottom, 4 * SEGMENTS + j, 4 * SEGMENTS + i)))
    vertices.extend(((x, y, .002), (x, y, 0.0)))
    # Check the centre and five radial rings across the entire footprint,
    # including the outer perimeter, before adding the film.
    graph = bpy.context.evaluated_depsgraph_get()
    samples = [(x, y)] + [(x+(px-x)*fraction, y+(py-y)*fraction)
                         for px, py, _ in vertices[4 * SEGMENTS:5 * SEGMENTS]
                         for fraction in (.2, .4, .6, .8, 1.0)]
    for px, py in samples:
        hit, position, _, _, obj, _ = bpy.context.scene.ray_cast(
            graph, Vector((px, py, .02)), Vector((0, 0, -1)), distance=.03)
        assert hit and obj.name == 'R2 floor' and abs(position.z) < 1e-6, (
            'Oil footprint overlaps another surface', px, py, obj.name if hit else None)
    mesh = bpy.data.meshes.new(OBJECT)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(surface)
    mesh.materials.append(underside)
    for polygon in mesh.polygons:
        polygon.use_smooth = polygon.loop_total == 4
        if polygon.index >= 4 * SEGMENTS and (polygon.index - 4 * SEGMENTS) % 2:
            polygon.material_index = 1
    bm = bmesh.new()
    bm.from_mesh(mesh)
    assert all(edge.is_manifold for edge in bm.edges)
    assert all(face.calc_area() > 1e-12 for face in bm.faces)
    volume = bm.calc_volume(signed=True)
    assert volume > 0
    bm.free()
    obj = bpy.data.objects.new(OBJECT, mesh)
    bpy.data.collections['23 R2 FLOOR AND DRESSING'].objects.link(obj)
    SUPPORT.reset(OWNER)
    SUPPORT.register(OWNER, 'generator service-floor film', OBJECT, 'R2 floor',
                     [(x, y, 0.0), (x-.10, y, 0.0), (x+.10, y, 0.0),
                      (x, y-.06, 0.0), (x, y+.06, 0.0)],
                     gap=.00002, penetration=.00002)
    report = {'object': OBJECT, 'closed_positive_volume_m3': volume,
              'perimeter_samples_clear': SEGMENTS,
              'footprint_samples_clear': len(samples), 'floor_gap_m': 0.0,
              'maximum_height_m': .002, 'source_floor_shader_unchanged': True,
              'scope': 'One local closed film, two owned materials and five support anchors; existing floor, paint, water, machinery and lighting unchanged'}
    bpy.context.scene['rh_service_oil_film'] = json.dumps(report, sort_keys=True)
    return report
