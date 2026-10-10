"""A wall-supported neutral practical for the otherwise unreadable P-10 casing.

This adds a local lamp and welded triangular bracket. Existing scene meshes,
materials, lights, exposure and machinery transforms are untouched.
"""
import json
import math

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import rh_stlib as S
import rh_support_registry as SUPPORT

OWNER = 'P10 service practical'
LIGHT = 'RH refine P10 service practical'


def build(K, M):
    assert LIGHT not in bpy.data.objects
    collection = bpy.data.collections['RH REFINEMENT']
    scene = bpy.context.scene
    SUPPORT.reset(OWNER)
    walls = []
    for name in ('RH walls concrete CONC', 'RH walls concrete CONC_POUR'):
        obj = bpy.data.objects[name]
        tree = BVHTree.FromPolygons([obj.matrix_world @ v.co for v in obj.data.vertices],
                                   [list(p.vertices) for p in obj.data.polygons])
        walls.append((obj, tree))

    def wall_point(x, z):
        hits = []
        for obj, tree in walls:
            point, normal, _, distance = tree.ray_cast(Vector((x, -8, z)), Vector((0, -1, 0)), 3.1)
            if point is not None and normal.y > .99:
                hits.append((distance, obj.name, point))
        assert hits, (x, z)
        return min(hits, key=lambda h: h[0])

    x = -3.6
    tip_y = -8.90
    plates = []
    for tag, z in (('upper', 2.78), ('lower', 2.32)):
        _, host, p = wall_point(x, z)
        corners = [(x+sx*.065, z+sz*.045) for sx in (-1, 1) for sz in (-1, 1)]
        for cx, cz in corners:
            _, actual_host, hit = wall_point(cx, cz)
            assert actual_host == host and abs(hit.y-p.y) < .0001
        group = 'P10 '+tag+' wallplate'
        K.bx((group, 'STEEL'), x-.09, x+.09, p.y+.0002, p.y+.0282, z-.065, z+.065, .003)
        for cx, cz in corners:
            S.disc(K, group, 'STEEL', (cx, p.y+.0282, cz), (0, 1, 0), .010, .008, seg=6)
        name = 'RH refine '+group+' STEEL'
        SUPPORT.register(OWNER, tag+' wall fixings', name, host,
                         [(cx, p.y+.0002, cz) for cx, cz in corners], (0, -1, 0), 'wall',
                         gap=.0004, penetration=.0002)
        plates.append({'tag': tag, 'host': host, 'wall_y': p.y, 'z': z, 'object': name})

    upper, lower = plates
    top_root = Vector((x, upper['wall_y']+.0282, upper['z']))
    brace_root = Vector((x, lower['wall_y']+.0282, lower['z']))
    tip = Vector((x, tip_y, upper['z']))
    K.prism(('P10 service bracket', 'STEEL'), top_root, tip, .022, .022, 24, 0, True)
    K.prism(('P10 service bracket', 'STEEL'), brace_root, tip, .015, .015, 24, 0, True)
    bracket = 'RH refine P10 service bracket STEEL'
    for plate, root in ((upper, top_root), (lower, brace_root)):
        SUPPORT.register(OWNER, plate['tag']+' welded bracket root', bracket, plate['object'],
                         [root], (0, -1, 0), 'wall', gap=.0003, penetration=.0003)

    lens = Vector((x, tip_y, 2.65))
    target = Vector((-3.0, -9.40, .60))
    axis = (target-lens).normalized()
    K.prism(('P10 task housing', 'STEEL'), lens-axis*.14, lens-axis*.004,
            .07, .135, 32, 0, True, .002)
    S.disc(K, 'P10 task diffuser', 'PRACTICAL', lens, axis, .108, .004, seg=32)
    # The small top yoke is welded to the triangular arm and housing. Its
    # intentional welded overlaps are confined to this new fixture assembly.
    K.bx(('P10 task housing', 'STEEL'), x-.028, x+.028, tip_y-.04, tip_y+.04, 2.75, 2.802, .003)
    SUPPORT.register(OWNER, 'housing to arm yoke', 'RH refine P10 task housing STEEL', bracket,
                     [(x, tip_y-.025, 2.8019)], (0, 0, -1), 'floor', gap=.0004, penetration=.0003, angle=25)
    SUPPORT.register(OWNER, 'diffuser to housing face', 'RH refine P10 task diffuser PRACTICAL',
                     'RH refine P10 task housing STEEL', [lens], tuple(-axis), 'wall',
                     gap=.006, penetration=.0004)
    K.tube(('P10 lamp supply', 'BLACK'),
           [Vector((x, upper['wall_y']+.03, 2.807)),
            Vector((x, tip_y, 2.807)), lens-axis*.14], .005, 12)
    for yy in (-10.2, -9.5):
        S.torus(K, 'P10 service bracket', 'STEEL', (x, yy, 2.807), (0, 1, 0), .007, .003, 16, 8)
    SUPPORT.register(OWNER, 'supply cable on arm', 'RH refine P10 lamp supply BLACK', bracket,
                     [(x, -9.9, 2.802)], (0, 0, -1), 'floor', gap=.0005, penetration=.0004, angle=25)

    light = bpy.data.lights.new(LIGHT, 'SPOT')
    light.energy = 120
    light.color = (.96, .97, .96)
    light.spot_size = math.radians(70)
    light.spot_blend = .6
    light.shadow_soft_size = .07
    obj = bpy.data.objects.new(LIGHT, light)
    collection.objects.link(obj)
    obj.location = lens+axis*.006
    obj.rotation_euler = axis.to_track_quat('-Z', 'Y').to_euler()
    scene['rh_p10_service_practical'] = json.dumps({
        'owner': OWNER, 'light': LIGHT, 'power_w': light.energy,
        'color': list(light.color), 'location': list(obj.location), 'target': list(target),
        'wall_plates': plates, 'arm_tip': list(tip), 'housing_lens': list(lens),
        'scope': 'Local static task practical; triangular welded bracket on two measured south-wall faces. Existing scene objects and material graphs remain unchanged.',
        'intentional_interfaces': 'Bracket tubes welded to wallplates and arm/yoke; diffuser seated ahead of closed reflector face. Supply cable follows arm.',
    })
