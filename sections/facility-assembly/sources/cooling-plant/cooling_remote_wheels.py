"""Cooling plant remote valve wheels: make the pump isolation valves operable by a player.

Run once against `module_aaa_A1.blend`:
    blender -b module_aaa_A1.blend --python cooling_remote_wheels.py -- --output NEW.blend --receipt remote-wheels.json

The pump isolation handwheels sit at 2.45 m behind each pump skid, out of reach. This adds, for each pump, a drive rod from the
valve's outboard stem end along the wall side, a drop rod, a bevel box and a remote handwheel at 1.4 m in the open operator lane
(pump A front lane, pump B rear lane). The valve bodies and existing wheels are unchanged. New parts stay west of x = -4.95 below
2.2 m (outside every keep-clear volume) or above the pump envelopes.
"""
import json
import math
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

REV = 'Cooling plant remote valve wheels'
PUMPS = {
    'A': {'valve': Vector((-4.51, 4.15, 2.45)), 'lane_y': 2.95, 'id': 'CP-PUMP-A.isolate'},
    'B': {'valve': Vector((-4.51, 7.60, 2.45)), 'lane_y': 8.85, 'id': 'CP-PUMP-B.isolate'},
}
ROD_X, DROP_X, WHEEL_X, WHEEL_Z, ROD_Z, R = -4.38, -5.20, -5.00, 1.40, 2.45, .02


def opts():
    a = sys.argv[sys.argv.index('--') + 1:]
    return (a[a.index('--output') + 1] if '--output' in a else None,
            a[a.index('--receipt') + 1] if '--receipt' in a else None)


def mesh_obj(name, bm, mat):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(bpy.data.materials[mat])
    bpy.data.collections['MODULE_cooling-plant'].objects.link(ob)
    for p in me.polygons:
        p.use_smooth = True
    return ob


def rod(name, a, b, r=R, mat='steel'):
    a, b = Vector(a), Vector(b)
    bm = bmesh.new()
    d = b - a
    bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=r, radius2=r, depth=d.length)
    rot = d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=rot, verts=bm.verts)
    bmesh.ops.translate(bm, vec=(a + b) / 2, verts=bm.verts)
    return mesh_obj(name, bm, mat)


def box(name, c, size, mat='dark'):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bmesh.ops.translate(bm, vec=c, verts=bm.verts)
    return mesh_obj(name, bm, mat)


def wheel(name, c, mat='yellow'):
    """Handwheel in the YZ plane (axis X), 0.40 m across, like the valve's own wheel."""
    bm = bmesh.new()
    rim_r, tube = .20, .016
    seg, ring = 24, 6
    rows = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        row = []
        for j in range(ring):
            b = 2 * math.pi * j / ring
            rr = rim_r + tube * math.cos(b)
            row.append(bm.verts.new((tube * math.sin(b), rr * math.cos(a), rr * math.sin(a))))
        rows.append(row)
    for i in range(seg):
        for j in range(ring):
            bm.faces.new((rows[i][j], rows[(i + 1) % seg][j], rows[(i + 1) % seg][(j + 1) % ring], rows[i][(j + 1) % ring]))
    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=.04, radius2=.04, depth=.07,
                          matrix=Matrix.Rotation(math.pi / 2, 4, 'Y'))
    for k in range(4):
        a = k * math.pi / 2
        sp = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=.009, radius2=.009, depth=rim_r - .02)
        along = Vector((0, math.cos(a), math.sin(a)))
        m = along.to_track_quat('Z', 'X').to_matrix().to_4x4()
        bmesh.ops.transform(bm, matrix=m, verts=sp['verts'])
        bmesh.ops.translate(bm, vec=along * (rim_r / 2), verts=sp['verts'])
    bmesh.ops.translate(bm, vec=c, verts=bm.verts)
    return mesh_obj(name, bm, mat)


def build(tag, cfg):
    v, ly = cfg['valve'], cfg['lane_y']
    ids = []
    ids.append(box(f'CP-{tag} drive coupling box', (ROD_X, v.y, ROD_Z), (.10, .10, .10)))
    ids.append(rod(f'CP-{tag} stem stub', (v.x + .005, v.y, ROD_Z), (ROD_X + .05, v.y, ROD_Z), r=.015))
    ids.append(rod(f'CP-{tag} drive rod run', (ROD_X, v.y, ROD_Z), (ROD_X, ly, ROD_Z)))
    ids.append(box(f'CP-{tag} drive corner box', (ROD_X, ly, ROD_Z), (.09, .09, .09)))
    ids.append(rod(f'CP-{tag} drive rod cross', (ROD_X, ly, ROD_Z), (DROP_X, ly, ROD_Z)))
    ids.append(box(f'CP-{tag} drop corner box', (DROP_X, ly, ROD_Z), (.09, .09, .09)))
    ids.append(rod(f'CP-{tag} drop rod', (DROP_X, ly, ROD_Z), (DROP_X, ly, WHEEL_Z)))
    ids.append(box(f'CP-{tag} remote gearbox', (DROP_X, ly, WHEEL_Z), (.16, .14, .14)))
    ids.append(rod(f'CP-{tag} wheel shaft', (DROP_X + .06, ly, WHEEL_Z), (WHEEL_X - .03, ly, WHEEL_Z), r=.015))
    w = wheel(f'CP-{tag} remote isolation wheel', (WHEEL_X, ly, WHEEL_Z))
    w['interaction_id'] = cfg['id']
    w['purpose'] = 'player-operated pump isolation handwheel; drives the valve at 2.45 m'
    ids.append(w)
    ids.append(box(f'CP-{tag} wall arm', (-5.34, ly, WHEEL_Z), (.28, .08, .08)))
    ids.append(box(f'CP-{tag} wall clamp arm', (-5.34, ly, 1.95), (.28, .06, .06)))
    ids.append(box(f'CP-{tag} rod clamp', (DROP_X, ly, 1.95), (.08, .08, .08)))
    return ids


def apply():
    s = bpy.context.scene
    assert not s.get('cooling_remote_wheels'), 'Remote wheels already applied'
    out = {}
    for tag, cfg in PUMPS.items():
        out[tag] = [o.name for o in build(tag, cfg)]
    cam = bpy.data.cameras.new('AAA05_REMOTE_WHEEL_A')
    cam.lens = 22
    cam.clip_start = .05
    ob = bpy.data.objects.new('AAA05_REMOTE_WHEEL_A', cam)
    ob.location = (-2.6, 1.9, 1.7)
    ob.rotation_euler = (Vector((-5.0, 3.6, 1.9)) - ob.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.data.collections['MODULE_cooling-plant'].objects.link(ob)
    s['cooling_remote_wheels'] = REV
    bpy.context.view_layer.update()
    return {'revision': REV, 'objects': out}


if __name__ == '__main__':
    out, receipt = opts()
    result = apply()
    if receipt:
        json.dump(result, open(receipt, 'w'), indent=2)
    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out)
    print('REMOTE:', len(result['objects']['A']) * 2, 'objects')
