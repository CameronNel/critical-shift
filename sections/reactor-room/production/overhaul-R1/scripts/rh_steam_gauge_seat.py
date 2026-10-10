"""A measured welded saddle and neck for the retained steam pressure nipple."""
import json
import math

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import rh_support_registry as SUPPORT

NAME = 'RH refine steam gauge weld saddle'
OWNER = 'steam gauge welded seat'


def build():
    assert NAME not in bpy.data.objects
    scene = bpy.context.scene
    placement = json.loads(scene['rh_steam_gauge_placement'])
    center = Vector(placement['new_pipe_tap'])
    axis = Vector((0, -1, 0))
    u, v = Vector((1, 0, 0)), Vector((0, 0, 1))
    pipe = bpy.data.objects['RH services R2 PIPING pipe PIPE']
    body = bpy.data.objects['RH services R2 PIPING valve body IRON']
    tree = BVHTree.FromPolygons([pipe.matrix_world @ p.co for p in pipe.data.vertices],
                               [list(p.vertices) for p in pipe.data.polygons])
    angles = [2*math.pi*i/64 for i in range(64)]

    def skin(radius, angle):
        radial = (u*math.cos(angle)+v*math.sin(angle))*radius
        hit, normal, _, distance = tree.ray_cast(center+radial+axis*.3, -axis, .35)
        assert hit is not None and .07 < (hit-center).dot(axis) < .095
        assert normal.dot(axis) > .9, (angle, normal)
        return hit

    # The bottom and weld toe follow the saved faceted pipe skin, rather than
    # embedding a guessed flat collar. A 0.35 mm weld overlap seals that seam.
    # The 9.5 mm bore embraces the retained 11 mm nipple; the neck ends before
    # its existing union. These are intentional welded/threaded intersections.
    profile = [( .0095, 'skin', -.00035),
               ( .0270, 'skin', -.00035),
               ( .0280, 'skin',  .00150),
               ( .0230, 'skin',  .00650),
               ( .0160, 'axis',  .10350),
               ( .0135, 'axis',  .10700),
               ( .0095, 'axis',  .10700)]
    bm = bmesh.new()
    rows = []
    for radius, mode, depth in profile:
        row = []
        for angle in angles:
            radial = (u*math.cos(angle)+v*math.sin(angle))*radius
            point = skin(radius, angle)+axis*depth if mode=='skin' else center+radial+axis*depth
            row.append(bm.verts.new(point))
        rows.append(row)
    for i, row in enumerate(rows):
        following = rows[(i+1)%len(rows)]
        for j in range(len(angles)):
            k = (j+1)%len(angles)
            bm.faces.new((row[j], row[k], following[k], following[j]))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(edge.is_manifold for edge in bm.edges)
    volume = bm.calc_volume(signed=True)
    assert volume > 0
    mesh = bpy.data.meshes.new(NAME)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(NAME, mesh)
    pipe.users_collection[0].objects.link(obj)
    mesh.materials.append(body.data.materials[0])
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    SUPPORT.reset(OWNER)
    bearing = [skin(.027, angle)-axis*.00035 for angle in angles[::4]]
    SUPPORT.register(OWNER, 'formed saddle to steam pipe', NAME, pipe.name,
                     bearing, -axis, 'wall', gap=.0001, penetration=.0005, angle=25)
    # Top-rim anchors lie within 0.75 mm of the actual retained nipple surface;
    # the independent component audit additionally checks their solid overlap.
    neck = [center+axis*.107+(u*math.cos(angle)+v*math.sin(angle))*.01175
            for angle in angles[::8]]
    SUPPORT.register(OWNER, 'retained nipple in welded neck', body.name, NAME,
                     neck, -axis, 'wall', gap=.0001, penetration=.0001)
    scene['rh_steam_gauge_seat'] = json.dumps({
        'object': NAME, 'pipe': pipe.name, 'nipple_and_union': body.name,
        'center': list(center), 'axis': list(axis), 'segments': 64,
        'profile': profile, 'weld_overlap_m': .00035, 'bore_radius_m': .0095,
        'volume_m3': volume,
        'scope': 'Closed formed saddle covering the intentional retained pipe/nipple penetration; existing pipe, nipple, union and gauge meshes remain intact. No hydraulic internals are modeled.'})
    bpy.context.view_layer.update()
    print('STEAM_GAUGE_SEAT', len(mesh.vertices), len(mesh.polygons), volume, flush=True)
