"""Cooling plant: move the pump isolation valves to where a player can turn them.

Run once against `module_aaa_A1.blend`:
    blender -b module_aaa_A1.blend --python cooling_valve_relocate.py -- --output NEW.blend --receipt valve-relocation.json

Each pump's return branch is one polyline pipe dropping from the wall header to the pump. The isolation valve sat on it at 2.45 m,
behind the pump skid. Here the branch drops from the header beside the open operator lane instead (pump A front lane, pump B rear
lane), runs along the floor to the pump suction, and the valve (flanges, bonnet, handwheel) is lowered to a 1.35 m wheel height and
turned so the wheel faces the lane. No valve is added, removed or rescaled; the wheel stays outside the pump envelopes.
"""
import json
import math
import sys

import bpy
from mathutils import Matrix, Vector

REV = 'Cooling plant pump valve relocation'
X_OLD, X_NEW, DZ = -5.03, -5.20, 1.35 - 2.45
PUMPS = {
    # curve, old/new riser y, stem turn (rad), height of the floor-level run (B lifted over a wall cable cleat)
    'A': dict(curve='P01 return branch', y0=4.15, y1=3.45, rot=-math.pi / 2, rz=.91,
              parts=lambda n: n.startswith(('P01 return isolation', 'P01 valve bonnet', 'P01 isolation'))),
    'B': dict(curve='pump return branch 7.6', y0=7.60, y1=8.60, rot=math.pi / 2, rz=1.0,
              parts=lambda n: n.startswith(('return isolation 7.6', 'return valve bonnet', 'return isolation wheel'))),
}


def opts():
    a = sys.argv[sys.argv.index('--') + 1:]
    return (a[a.index('--output') + 1] if '--output' in a else None,
            a[a.index('--receipt') + 1] if '--receipt' in a else None)


def reroute(curve, y0, y1, rz):
    sp = curve.data.splines[0]
    elbow_x = [-5.03, -5.02, -5.01, -5.0, -4.98, -4.96, -4.94, -4.91]
    elbow_z = [1.0, .98, .96, .94, .93, .92, .91, .91]
    sgn = 1 if y1 > y0 else -1
    dz = rz - .91
    # new path (world == local, the curve sits at the origin)
    pts = [(X_NEW, y1, 3.76), (X_NEW, y1, 1.03 + dz)]
    for dx, z in zip(elbow_x, elbow_z):       # elbow turning from the vertical drop toward the pump along y
        d = dx - X_OLD
        pts.append((X_NEW, y1 + sgn * d, z + dz))
    pts += [(X_NEW, y0 - sgn * .12, rz), (X_NEW + .01, y0 - sgn * .08, rz), (X_NEW + .03, y0 - sgn * .04, rz),
            (X_NEW + .07, y0, rz - .01), (X_NEW + .12, y0, rz - .02), (-4.69, y0, .91)]
    sp.points.add(len(pts) - len(sp.points))
    for p, c in zip(sp.points, pts):
        p.co = (*c, 1.0)
    return len(pts)


def move_valve(parts, y0, y1, rot):
    old = Matrix.Translation((X_OLD, y0, 0))
    new = Matrix.Translation((X_NEW, y1, DZ))
    m = new @ Matrix.Rotation(rot, 4, 'Z') @ old.inverted()
    for o in parts:
        o.matrix_world = m @ o.matrix_world


def apply():
    s = bpy.context.scene
    assert not s.get('cooling_valve_relocation'), 'Valve relocation already applied'
    out = {}
    for tag, c in PUMPS.items():
        curve = bpy.data.objects[c['curve']]
        parts = [o for o in bpy.data.objects if c['parts'](o.name)]
        assert parts, tag
        n = reroute(curve, c['y0'], c['y1'], c['rz'])
        move_valve(parts, c['y0'], c['y1'], c['rot'])
        out[tag] = {'curve_points': n, 'moved_objects': len(parts), 'riser': [X_NEW, c['y1']], 'wheel_height': 1.35}
    cam = bpy.data.cameras.new('AAA05_PUMP_VALVES')
    cam.lens = 22
    cam.clip_start = .05
    ob = bpy.data.objects.new('AAA05_PUMP_VALVES', cam)
    ob.location = (-2.6, 1.6, 1.7)
    ob.rotation_euler = (Vector((-5.1, 3.3, 1.5)) - ob.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.data.collections['MODULE_cooling-plant'].objects.link(ob)
    s['cooling_valve_relocation'] = REV
    bpy.context.view_layer.update()
    return {'revision': REV, 'pumps': out}


if __name__ == '__main__':
    out, receipt = opts()
    result = apply()
    if receipt:
        json.dump(result, open(receipt, 'w'), indent=2)
    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out)
    print('RELOCATE:', json.dumps(result))
