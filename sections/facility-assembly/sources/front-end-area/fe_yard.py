"""Shared yard constants and the instancing helper used across the front-end modules. The yard itself is built by fe_yard3 (shell) and fe_depot (contents)."""
from fe_common import *
from fe_props import *

YARD = (-48.0, -8.0, -84.0, -60.0)
RAIL_Y = -70.0
RAIL_X = -22.2
GATE = 0.78    # half gauge

def inst(proto, name, x, y, coll, rz=0.0, z=0.0, scale=(1, 1, 1), support='floor'):
    o = bpy.data.objects.new(name, proto.data)
    o.location = (LX(x), LY(y), z); o.rotation_euler = (0, 0, rz); o.scale = scale
    coll.objects.link(o)
    if support: o['support'] = support
    return o
