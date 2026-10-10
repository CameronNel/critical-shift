"""Seat the EC header blind plates and expose their original fasteners."""
import bpy
import bmesh
import json
import math
from mathutils import Vector
import rh_support_registry as SUPPORT

OWNER = 'EC blind cover correction'


def components(bm):
    unseen = set(bm.verts)
    while unseen:
        start = unseen.pop()
        group = {start}
        todo = [start]
        while todo:
            for edge in todo.pop().link_edges:
                for vertex in edge.verts:
                    if vertex in unseen:
                        unseen.remove(vertex)
                        group.add(vertex)
                        todo.append(vertex)
        yield group


def bounds(obj, group, axis_x, sign):
    points = [obj.matrix_world @ v.co for v in group]
    offsets = [sign*(p.x-axis_x) for p in points]
    radii = [math.hypot(p.y+8.84, p.z-.78) for p in points]
    return min(offsets), max(offsets), min(radii), max(radii), points


def rebuild_plates(plate):
    bm = bmesh.new()
    inverse = plate.matrix_world.inverted()
    for axis_x, sign in ((1.62, -1), (3.48, 1)):
        rings = []
        for offset, radius in ((.040, 0), (.040, .1825), (.0415, .184),
                               (.0505, .184), (.052, .1825), (.052, 0)):
            rings.append([bm.verts.new(inverse @ Vector((axis_x+sign*offset,
                          -8.84+radius*math.cos(2*math.pi*i/64),
                          .78+radius*math.sin(2*math.pi*i/64))))
                          for i in range(1 if radius == 0 else 64)])
        for first, second in zip(rings, rings[1:]):
            for i in range(64):
                j = (i+1) % 64
                if len(first) == 1:
                    face = bm.faces.new((first[0], second[j], second[i]))
                elif len(second) == 1:
                    face = bm.faces.new((first[i], first[j], second[0]))
                else:
                    face = bm.faces.new((first[i], first[j], second[j], second[i]))
                face.smooth = len(first) > 1 and len(second) > 1
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges), 'Open replacement blind plate'
    assert bm.calc_volume(signed=True) > 0, 'Inverted replacement blind plate'
    bm.to_mesh(plate.data)
    bm.free()
    plate.data.update()


def build(K, M):
    scene = bpy.context.scene
    assert not scene.get('rh_blind_cover_correction'), 'Blind covers already corrected'
    scene.frame_set(1)
    iron = bpy.data.objects['RH stations south IRON']
    steel = bpy.data.objects['RH stations south STEEL']
    plate = bpy.data.objects['RH refine blind covers STEEL']
    SUPPORT.reset(OWNER)
    rows = []
    rebuild_plates(plate)
    for axis_x, sign in ((1.62, -1), (3.48, 1)):
        bm = bmesh.new()
        bm.from_mesh(iron.data)
        plugs = []
        for group in components(bm):
            lo, hi, rlo, rhi, points = bounds(iron, group, axis_x, sign)
            if .037 <= lo <= .041 and .059 <= hi <= .063 and .149 <= rhi <= .153:
                plugs.append(group)
        assert len(plugs) == 1, ('Expected one complete plug', axis_x, len(plugs))
        removed_faces = len({f for v in plugs[0] for f in v.link_faces})
        bmesh.ops.delete(bm, geom=list(plugs[0]), context='VERTS')
        bm.normal_update()
        bm.to_mesh(iron.data)
        bm.free()
        iron.data.update()

        bm = bmesh.new()
        bm.from_mesh(steel.data)
        inverse = steel.matrix_world.inverted()
        bolt_vertices = 0
        bolt_seats = []
        for group in components(bm):
            lo, hi, rlo, rhi, points = bounds(steel, group, axis_x, sign)
            if abs(lo-.040) < .000002 and abs(hi-.052) < .000002 and .139 <= rlo and rhi <= .165:
                bolt_seats.append((axis_x+sign*.052, sum(p.y for p in points)/len(points),
                                   sum(p.z for p in points)/len(points)))
                for vertex in group:
                    p = steel.matrix_world @ vertex.co
                    p.x += sign*.012
                    vertex.co = inverse @ p
                    bolt_vertices += 1
        assert len(bolt_seats) == 10, ('Expected ten original bolt heads', axis_x, len(bolt_seats))
        bm.normal_update()
        bm.to_mesh(steel.data)
        bm.free()
        steel.data.update()

        seats = [(axis_x+sign*.040, -8.84+.17*math.cos(a), .78+.17*math.sin(a))
                 for a in (math.pi/4+i*math.pi/2 for i in range(4))]
        SUPPORT.register(OWNER, 'plate seat '+str(axis_x), plate.name, iron.name,
                         seats, (-sign, 0, 0), 'bearing', gap=.001, penetration=.001)
        SUPPORT.register(OWNER, 'bolt seats '+str(axis_x), steel.name, plate.name,
                         bolt_seats, (-sign, 0, 0), 'bearing', gap=.001, penetration=.001)
        rows.append(dict(axis_x=axis_x, direction=sign, removed_plug_faces=removed_faces,
                         moved_bolt_vertices=bolt_vertices, plate_segments=64,
                         plate_back_offset=.040, plate_front_offset=.052,
                         bolt_front_offset=.064))
    bpy.context.view_layer.update()
    scene['rh_blind_cover_correction'] = json.dumps(rows)
    print('BLIND_COVERS_SEATED', json.dumps(rows), flush=True)
