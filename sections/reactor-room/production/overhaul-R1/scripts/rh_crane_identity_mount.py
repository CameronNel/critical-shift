"""Mount the unchanged crane identity on a clear, supported bridge nameplate."""
import json

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import crk
import rh_stlib as S
import rh_support_registry as SUPPORT

OWNER = 'crane identity mounting'
LABEL = 'RH refine crane identity'


def build(bridge, materials, label):
    assert label.name == LABEL and label.parent == bridge
    assert label.data.body == 'CRANE C-01 / CAPACITY: SEE CERTIFICATE'
    assert 'RH refine crane bridge identity plate PANEL' not in bpy.data.objects
    SUPPORT.reset(OWNER)
    bpy.context.view_layer.update()
    tree = BVHTree.FromPolygons(
        [bridge.matrix_world @ v.co for v in bridge.data.vertices],
        [list(p.vertices) for p in bridge.data.polygons])
    center_x, center_z = -4.2, 15.04
    back_y, front_y = 4.2048, 4.1948
    points = [(center_x+dx, center_z+dz)
              for dx in (-1.05, 1.05) for dz in (-.085, .085)]
    kit = crk.Kit()
    kit.bx(('crane bridge identity plate', 'PANEL'),
           center_x-1.325, center_x+1.325, front_y, back_y,
           center_z-.14, center_z+.14, .001)
    hosts = []
    for x, z in points:
        hit, normal, _, distance = tree.ray_cast(Vector((x, 4.0, z)), Vector((0, 1, 0)), .5)
        assert hit is not None and normal.y < -.99 and abs(hit.y-4.25) < .0001, (x, z, hit)
        seat = Vector((x, back_y, z))
        kit.prism(('crane bridge identity spacers', 'STEEL'), seat, hit,
                  .006, .006, 16, 0, True)
        S.disc(kit, 'crane bridge identity fixings', 'STEEL',
               (x, front_y, z), (0, -1, 0), .008, .004, seg=6)
        hosts.append(hit)
    made = kit.build(bridge.users_collection[0], 'RH refine', materials)
    for obj in made:
        obj.parent = bridge
        obj.matrix_parent_inverse = bridge.matrix_world.inverted()
    plate = 'RH refine crane bridge identity plate PANEL'
    spacers = 'RH refine crane bridge identity spacers STEEL'
    fixings = 'RH refine crane bridge identity fixings STEEL'
    SUPPORT.register(OWNER, 'stand-offs to bridge web', spacers, bridge.name,
                     hosts, (0, 1, 0), 'wall', gap=.0004, penetration=.0003)
    SUPPORT.register(OWNER, 'nameplate to stand-offs', plate, spacers,
                     [(x, back_y, z) for x, z in points], (0, 1, 0), 'wall',
                     gap=.0004, penetration=.0003)
    SUPPORT.register(OWNER, 'fixing heads to nameplate', fixings, plate,
                     [(x, front_y, z) for x, z in points], (0, 1, 0), 'wall',
                     gap=.0004, penetration=.0003)
    # Parent/inverse, font body, size, material and extrusion stay unchanged.
    # Its rear extrusion seats on the new plate front rather than in a rib.
    label.location.x = center_x
    label.location.y = front_y-label.data.extrude
    bpy.context.view_layer.update()
    bpy.context.scene['rh_crane_identity_mount'] = json.dumps({
        'owner': OWNER, 'label': label.name, 'plate': plate,
        'bridge': bridge.name, 'label_location': list(label.location),
        'plate_bounds': [center_x-1.325, center_x+1.325, front_y, back_y,
                         center_z-.14, center_z+.14],
        'web_seats': [list(p) for p in hosts], 'support_samples': 12,
        'scope': 'Unchanged identity wording on a closed nameplate with four web stand-offs and fixing heads. Three new meshes share the retained animated bridge parent. Existing material graphs, lights, camera, animation and other geometry are unchanged.',
        'intentional_interfaces': 'Closed stand-offs seat on the bridge web and plate rear; fixing heads seat on plate front; 0.4 mm glyph rear extrusion seats on plate front.',
    })
    return made
