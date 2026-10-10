"""Move the complete waste-cask dial/boss clear of its two cooling fins."""
import json
import math

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from rh_blind_covers import components
import rh_support_registry as SUPPORT

OWNER = 'waste gauge stand-off'
OLD_CENTER = Vector((7.045, 7.645, 1.64))
AXIS = Vector((-1, -1, 0)).normalized()
OFFSET = AXIS*.071
BOSS_REAR_EXTENSION = .047


def build():
    scene = bpy.context.scene
    assert 'rh_waste_gauge_placement' not in scene
    changes = {}
    rear_extension_ids = []
    specs = [('STEEL', -.0851, .0001, .0721, 2),
             # The inherited bevel reaches R82.031 mm and axial -0.658
             # to +16.135 mm on this nominal R80 mm brass bezel.
             ('BRASS', -.001, .017, .083, 1),
             ('WHITE', .0119, .0166, .0673, 1),
             ('BLACK', .0157, .0261, .0801, 10),
             ('RED', .0181, .0239, .0801, 1),
             ('GLASS', .0274, .0286, .0673, 1)]

    def move(obj, low, high, radius, expected=None, extend_boss=False):
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        selected = []
        for island in components(bm):
            points = [obj.matrix_world @ vertex.co for vertex in island]
            axial = [(p-OLD_CENTER).dot(AXIS) for p in points]
            radial = [((p-OLD_CENTER)-AXIS*(p-OLD_CENTER).dot(AXIS)).length for p in points]
            if min(axial)>=low and max(axial)<=high and max(radial)<=radius:
                selected.append(island)
        assert selected and (expected is None or len(selected)==expected), (obj.name, len(selected), expected)
        ids = sorted(v.index for island in selected for v in island)
        rear_ids = []
        if extend_boss:
            boss = [island for island in selected
                    if len(island)==20 and max((obj.matrix_world @ v.co-OLD_CENTER).dot(AXIS) for v in island)<-.0296]
            assert len(boss)==1
            depths = [(v.index, (obj.matrix_world @ v.co-OLD_CENTER).dot(AXIS)) for v in boss[0]]
            rear = min(depth for _, depth in depths)
            rear_ids = [index for index, depth in depths if abs(depth-rear)<.00001]
            assert len(rear_ids)==10
        bm.free()
        selected_ids = set(ids)
        assert all(not (set(p.vertices)&selected_ids) or set(p.vertices)<=selected_ids
                   for p in obj.data.polygons), 'Partial face selection'
        local = obj.matrix_world.to_3x3().inverted() @ OFFSET
        for index in ids:
            obj.data.vertices[index].co += local
        if rear_ids:
            extension = obj.matrix_world.to_3x3().inverted() @ (-AXIS*BOSS_REAR_EXTENSION)
            for index in rear_ids:
                obj.data.vertices[index].co += extension
            rear_extension_ids.extend(rear_ids)
        obj.data.update()
        changes[obj.name] = ids

    for material, low, high, radius, count in specs:
        move(bpy.data.objects['RH stations east '+material], low, high, radius, count,
             extend_boss=material=='STEEL')
    # In an incremental saved candidate the two generated helpers already
    # exist. A cold pipeline calls this before generating them at NEW_CENTER.
    for name in ('RH refine gauge calibration ink', 'RH refine gauge glass retainers'):
        if name in bpy.data.objects:
            move(bpy.data.objects[name], -.0001, .032, .0801)
    for key, position_key in (('rh_gauge_information', 'face_center'),
                              ('rh_gauge_glass_seats', 'center')):
        if key in scene:
            records = json.loads(scene[key])
            matches = [r for r in records if r['tag']=='waste cask']
            assert len(matches)==1
            matches[0][position_key] = list(Vector(matches[0][position_key])+OFFSET)
            scene[key] = json.dumps(records)
    rows = json.loads(scene.get(SUPPORT.KEY, '[]'))
    for row in rows:
        if row['name'].startswith('waste cask ') and row['owner'] in ('gauge calibration', 'gauge glass seats'):
            row['anchors'] = [list(Vector(p)+OFFSET) for p in row['anchors']]
    scene[SUPPORT.KEY] = json.dumps(rows)

    # The retained closed boss still crosses the actual faceted cask skin.
    # Sample its ten outer longitudinal vertex lines where they meet that skin.
    SUPPORT.reset(OWNER)
    shell = bpy.data.objects['RH stations east YELLOW']
    tree = BVHTree.FromPolygons([shell.matrix_world @ v.co for v in shell.data.vertices],
                               [list(p.vertices) for p in shell.data.polygons])
    c = OLD_CENTER+OFFSET
    u = Vector((1, -1, 0)).normalized()
    v = Vector((0, 0, 1))
    anchors = []
    for k in range(10):
        theta = 2*math.pi*k/10
        radial = (u*math.cos(theta)+v*math.sin(theta))*.03
        hit, normal, _, _ = tree.ray_cast(c+radial+AXIS*.08, -AXIS, .25)
        assert hit is not None and normal.dot(AXIS)>.98
        axial = (hit-c).dot(AXIS)
        assert -.132 < axial < -.0296, (k, axial)
        anchors.append(hit)
    SUPPORT.register(OWNER, 'retained boss welded to cask skin', 'RH stations east STEEL', shell.name,
                     anchors, tuple(-AXIS), 'wall', gap=.0003, penetration=.0003, angle=12)
    scene['rh_waste_gauge_placement'] = json.dumps({
        'old_center': list(OLD_CENTER), 'new_center': list(c), 'axis': list(AXIS),
        'offset': list(OFFSET), 'changed_vertex_indices': changes,
        'boss_rear_extension_m': BOSS_REAR_EXTENSION,
        'boss_rear_ring_vertex_indices': rear_extension_ids,
        'boss_shell_contacts': [list(p) for p in anchors],
        'rear_seat_overlap_m': .03-.021*math.sqrt(2),
        'scope': 'Only complete gauge layers and its retained steel boss move. Cask shell, cooling fins, material graphs and all other station vertices remain unchanged.',
        'interface': 'Retained closed boss with controlled cask-skin weld overlap and a 0.30 mm rear gauge-seat overlap; no new internal pressure-flow model.',
    })
    bpy.context.view_layer.update()
    print('WASTE_GAUGE_PLACEMENT', {name: len(ids) for name, ids in changes.items()}, flush=True)
