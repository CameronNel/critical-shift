"""Give stability bars a left-to-right fill and a correctly aligned scale.

Wall-local positive u appears screen-left. Keep the ten existing threshold
materials/drivers, move only their display cells, and space the scale labels.
"""
import bpy
import json
from mathutils import Vector
from r2lib import WALLS

BOARDS = ((2, 9.6, 'REACTOR STABILITY'), (6, 6.0, 'COOLANT / POWER'),
          (4, 6.0, 'CONTAINMENT'))


def apply(scene, objects):
    report = []
    for index, centre, label in BOARDS:
        wall = WALLS[index]
        changed = 0
        for level in range(10):
            obj = objects['RH refine board '+label+' LEVEL'+str(level)]
            assert obj.type == 'MESH' and len(obj.data.materials) == 1
            assert obj.data.materials[0].name == 'RH refine stability level '+str(level)
            points = [obj.matrix_world @ v.co for v in obj.data.vertices]
            midpoint = sum(points, Vector()) / len(points)
            current = (Vector((midpoint.x, midpoint.y))-wall.P).dot(wall.t)
            original = centre-1.40+level*.285+.1125
            desired = centre-1.40+(9-level)*.285+.1125
            assert min(abs(current-original), abs(current-desired)) < 1e-4, (obj.name, current)
            delta = desired-current
            if abs(delta) > 1e-5:
                inverse = obj.matrix_world.inverted()
                offset = Vector((wall.t.x*delta, wall.t.y*delta, 0))
                for vertex in obj.data.vertices:
                    vertex.co = inverse @ (obj.matrix_world @ vertex.co + offset)
                obj.data.update()
                changed += 1
        template = objects['RH refine '+label+' scale']
        assert template.type == 'FONT'
        template.data.body = '50'
        template.data.size = .075
        template.data.align_x = 'CENTER'
        template.data.align_y = 'CENTER'
        for percentage in (0, 25, 50, 75, 100):
            if percentage == 50:
                obj = template
            else:
                name = 'RH refine '+label+' scale '+str(percentage)
                obj = objects.get(name)
                if obj is None:
                    curve = template.data.copy()
                    curve.name = name
                    obj = bpy.data.objects.new(name, curve)
                    bpy.data.collections['RH REFINEMENT'].objects.link(obj)
                assert obj.type == 'FONT'
                obj.data.body = str(percentage)+(' %' if percentage == 100 else '')
                obj.rotation_euler = template.rotation_euler
            point = wall.pt(centre+1.39-2.79*percentage/100, .502)
            obj.location = (point.x, point.y, 6.56)
        report.append({'board': label, 'cells_moved': changed,
                       'fill_direction': 'left to right', 'scale_percentages': [0, 25, 50, 75, 100]})
    result = {'boards': report,
              'scope': 'Thirty owned display cells and five aligned labels per board; thresholds, state bindings, seconds-based drivers, boards and supports preserved'}
    scene['rh_stability_board_scale'] = json.dumps(result, sort_keys=True)
    return result
