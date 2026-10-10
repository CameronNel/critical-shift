"""Cut a closed blind tap port in the actual steam-pipe skin under its saddle."""
import json
import math

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def build():
    scene = bpy.context.scene
    assert 'rh_steam_gauge_tap_port' not in scene
    assert 'rh_steam_gauge_seat' in scene
    center = Vector(json.loads(scene['rh_steam_gauge_placement'])['new_pipe_tap'])
    axis = Vector((0, -1, 0))
    u, v = Vector((1, 0, 0)), Vector((0, 0, 1))
    obj = bpy.data.objects['RH services R2 PIPING pipe PIPE']
    mesh = obj.data
    original = [tuple(p.co) for p in mesh.vertices]
    tree = BVHTree.FromPolygons([obj.matrix_world @ p.co for p in mesh.vertices],
                               [list(p.vertices) for p in mesh.polygons])
    hit, normal, index, _ = tree.ray_cast(center+axis*.3, -axis, .35)
    assert hit is not None and normal.dot(axis) > .9999
    front = (hit-center).dot(axis)
    radius, floor, segments = .0115, .0435, 32
    assert .08 < front < .095 and front > floor
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    face = bm.faces[index]
    assert len(face.verts)==4
    corners = [obj.matrix_world @ p.co for p in face.verts]
    xs = [(p-center).dot(u) for p in corners]
    zs = [(p-center).dot(v) for p in corners]
    assert min(xs)<-radius-.0002 and max(xs)>radius+.0002
    assert min(zs)<-radius-.0002 and max(zs)>radius+.0002
    assert max(abs((p-hit).dot(axis)) for p in corners)<.000001
    # Order the retained quad corners in the same X/Z plane as the port rim.
    ordered = sorted(face.verts, key=lambda p: math.atan2(
        (obj.matrix_world@p.co-center).dot(v), (obj.matrix_world@p.co-center).dot(u)))
    corner_map = {}
    for p in ordered:
        delta = obj.matrix_world@p.co-center
        corner_map[(delta.dot(u)>0, delta.dot(v)>0)] = p
    assert len(corner_map)==4
    outer = [corner_map[(True,True)], corner_map[(False,True)],
             corner_map[(False,False)], corner_map[(True,False)]]
    material, smooth = face.material_index, face.smooth
    old_volume = bm.calc_volume(signed=True)
    bm.faces.remove(face)
    inverse = obj.matrix_world.inverted()
    rows = []
    for axial in (front, floor):
        rows.append([bm.verts.new(inverse@(center+axis*axial+
                     (u*math.cos(2*math.pi*j/segments)+v*math.sin(2*math.pi*j/segments))*radius))
                     for j in range(segments)])
    top, bottom = rows
    created = []

    def new_face(points, desired, smooth_face):
        f = bm.faces.new(points)
        f.normal_update()
        local_normal = obj.matrix_world.to_3x3().transposed()@desired
        if f.normal.dot(local_normal)<0:
            f.normal_flip()
        f.material_index = material
        f.smooth = smooth_face
        created.append(f)

    # Four concave patches replace one quad without touching its outer edges.
    # Each patch shares a quarter of the circular rim with the closed bore.
    for i in range(4):
        start = (4+8*i)%segments
        finish = (start+8)%segments
        arc = [top[(finish-j)%segments] for j in range(9)]
        new_face([outer[i],outer[(i+1)%4]]+arc, axis, smooth)
    for j in range(segments):
        k = (j+1)%segments
        angle = 2*math.pi*(j+.5)/segments
        inward = -(u*math.cos(angle)+v*math.sin(angle))
        new_face((top[j],top[k],bottom[k],bottom[j]), inward, True)
    new_face(bottom, axis, False)
    bm.normal_update()
    assert all(edge.is_manifold for row in rows for p in row for edge in p.link_edges)
    removed_volume = (old_volume-bm.calc_volume(signed=True))*abs(obj.matrix_world.to_3x3().determinant())
    expected = segments*.5*radius*radius*math.sin(2*math.pi/segments)*(front-floor)
    assert abs(removed_volume-expected)<expected*.025+1e-8, (removed_volume,expected)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    assert [tuple(p.co) for p in mesh.vertices[:len(original)]]==original
    scene['rh_steam_gauge_tap_port'] = json.dumps({
        'pipe':obj.name, 'center':list(center), 'axis':list(axis),
        'radius_m':radius, 'front_axial_m':front, 'floor_axial_m':floor,
        'segments':segments, 'replaced_face_index':index,
        'original_vertex_count':len(original), 'added_vertices':64,
        'new_faces':37, 'removed_volume_m3':removed_volume,
        'stem_tip_axial_m':.044, 'nominal_radial_clearance_m':.0005,
        'nominal_tip_clearance_m':.0005,
        'scope':'One saved flat pipe-skin quad replaced by four annular patches, a bore wall and blind floor. Every inherited pipe vertex and all unrelated faces/materials are retained.'})
    bpy.context.view_layer.update()
    print('STEAM_GAUGE_PORT', radius, front-floor, removed_volume, flush=True)
