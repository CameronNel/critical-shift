"""World-space construction kit. Avoids bpy.ops mesh primitives."""
from __future__ import annotations

import math
from contextlib import contextmanager

import bpy
from mathutils import Matrix, Vector

from materials import M

_collection = "ARCHITECTURE"
_parent = None
_supports: list[dict] = []


def supports():
    return _supports


def collection(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        host = collection(parent) if parent else bpy.context.scene.collection
        host.children.link(c)
    return c


@contextmanager
def use(name, parent=None):
    global _collection, _parent
    before = _collection, _parent
    _collection, _parent = name, parent
    collection(name)
    try:
        yield
    finally:
        _collection, _parent = before


def _link(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection(_collection).objects.link(obj)
    if _parent:
        bpy.context.view_layer.update()
        world = obj.matrix_world.copy()
        obj.parent = _parent
        obj.matrix_world = world
    obj["ocru_authored"] = True
    return obj


def finish(obj, name, mat=None, edge=0.0, smooth=False):
    obj.name = name
    if obj.data:
        obj.data.name = name
    _link(obj)
    if mat:
        slot = M[mat] if isinstance(mat, str) else mat
        if slot.name not in obj.data.materials:
            obj.data.materials.append(slot)
    if edge and obj.type == "MESH":
        bev = obj.modifiers.new("Edge", "BEVEL")
        bev.width = edge
        bev.segments = 2
        bev.limit_method = "ANGLE"
        bev.angle_limit = math.radians(30)
        wn = obj.modifiers.new("WN", "WEIGHTED_NORMAL")
        wn.keep_sharp = True
    if smooth and obj.type == "MESH":
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def mesh(name, verts, faces, mat, edge=0.0, smooth=False, loc=None, rot=None):
    d = bpy.data.meshes.new(name)
    d.from_pydata(verts, [], faces)
    d.update()
    o = bpy.data.objects.new(name, d)
    if loc is not None:
        o.location = loc
    if rot is not None:
        o.rotation_euler = rot
    return finish(o, name, mat, edge, smooth)


def box(name, pos, size, mat, edge=0.008, origin="center"):
    sx, sy, sz = size
    if origin == "min":
        x0, y0, z0 = 0, 0, 0
        x1, y1, z1 = sx, sy, sz
        loc = pos
    else:
        x0, y0, z0 = -sx / 2, -sy / 2, -sz / 2
        x1, y1, z1 = sx / 2, sy / 2, sz / 2
        loc = pos
    v = [
        (x0, y0, z0), (x0, y0, z1), (x0, y1, z0), (x0, y1, z1),
        (x1, y0, z0), (x1, y0, z1), (x1, y1, z0), (x1, y1, z1),
    ]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return mesh(name, v, f, mat, edge, loc=loc)


def box_min(name, mn, size, mat, edge=0.008):
    return box(name, mn, size, mat, edge, origin="min")


def quad(name, pos, width, height, mat, normal=(0, -1, 0), emit=False):
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1)) if abs(n.z) < 0.85 else Vector((0, 1, 0))
    t = up.cross(n)
    if t.length < 1e-6:
        t = Vector((1, 0, 0))
    t.normalize()
    b = t.cross(n).normalized()
    p = Vector(pos)
    hw, hh = width / 2, height / 2
    verts = [
        tuple(p - t * hw - b * hh),
        tuple(p + t * hw - b * hh),
        tuple(p + t * hw + b * hh),
        tuple(p - t * hw + b * hh),
    ]
    d = bpy.data.meshes.new(name)
    d.from_pydata(verts, [], [(0, 1, 2, 3)])
    d.update()
    uv = d.uv_layers.new(name="UVMap")
    for loop in d.loops:
        uv.data[loop.index].uv = [(0, 1), (1, 1), (1, 0), (0, 0)][loop.vertex_index]
    o = bpy.data.objects.new(name, d)
    return finish(o, name, mat, 0.0)


def cyl(name, a, b, r, mat, segs=16, edge=0.002, smooth=True):
    a, b = Vector(a), Vector(b)
    h = (b - a).length
    if h < 1e-6:
        h = 1e-6
    verts = []
    faces = []
    for i in range(segs):
        ang = 2 * math.pi * i / segs
        x, y = r * math.cos(ang), r * math.sin(ang)
        verts.append((x, y, -h / 2))
        verts.append((x, y, h / 2))
    bot = []
    top = []
    for i in range(segs):
        i0 = 2 * i
        i1 = 2 * ((i + 1) % segs)
        faces.append((i0, i1, i1 + 1, i0 + 1))
        bot.append(i0)
        top.append(2 * i + 1)
    faces.append(tuple(reversed(bot)))
    faces.append(tuple(top))
    quat = (b - a).to_track_quat("Z", "Y")
    return mesh(name, verts, faces, mat, edge, smooth, loc=(a + b) / 2, rot=quat.to_euler())


def tube(name, points, r, mat, cyclic=False):
    d = bpy.data.curves.new(name, "CURVE")
    d.dimensions = "3D"
    d.resolution_u = 8
    d.bevel_depth = r
    d.bevel_resolution = 3
    d.fill_mode = "FULL"
    s = d.splines.new("NURBS")
    s.points.add(len(points) - 1)
    for p, v in zip(s.points, points):
        p.co = (*v, 1.0)
    s.use_cyclic_u = cyclic
    s.order_u = min(4, len(points))
    s.use_endpoint_u = True
    o = bpy.data.objects.new(name, d)
    return finish(o, name, mat)


def torus(name, pos, major, minor, mat, segs=24, minor_segs=8):
    verts = []
    faces = []
    for i in range(segs):
        u = 2 * math.pi * i / segs
        cx, cy = major * math.cos(u), major * math.sin(u)
        for j in range(minor_segs):
            v = 2 * math.pi * j / minor_segs
            x = (major + minor * math.cos(v)) * math.cos(u)
            y = (major + minor * math.cos(v)) * math.sin(u)
            z = minor * math.sin(v)
            verts.append((x, y, z))
    for i in range(segs):
        for j in range(minor_segs):
            a = i * minor_segs + j
            b = i * minor_segs + (j + 1) % minor_segs
            c = ((i + 1) % segs) * minor_segs + (j + 1) % minor_segs
            d = ((i + 1) % segs) * minor_segs + j
            faces.append((a, b, c, d))
    return mesh(name, verts, faces, mat, 0.0, True, loc=pos)


def empty(name, pos=(0, 0, 0), size=0.12, **meta):
    o = bpy.data.objects.new(name, None)
    o.empty_display_size = size
    o.location = pos
    _link(o)
    o.name = name
    for k, v in meta.items():
        o[k] = v
    return o


def support(obj, target, direction, anchors, gap=0.005, pen=0.003):
    rec = {
        "object": obj.name,
        "target": target,
        "direction": direction,
        "anchors": [list(a) for a in anchors],
        "max_gap": gap,
        "max_pen": pen,
    }
    obj["support_target"] = target
    obj["support_dir"] = direction
    _supports.append(rec)
    return obj


def marker(name, pos, **meta):
    return empty(name, pos, 0.08, **meta)


def bolts(prefix, origin, axis, count, spacing, r=0.007, length=0.012, mat="steel"):
    ax = Vector(axis).normalized()
    side = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    n = ax.cross(side).normalized()
    out = []
    for i in range(count):
        p = Vector(origin) + n * (i * spacing)
        out.append(cyl(f"{prefix}_{i:02d}", p, p + ax * length, r, mat, segs=8, edge=0.0))
    return out


def grille(name, pos, size, mat, bars=7, axis="X", edge=0.002):
    sx, sy, sz = size
    px, py, pz = pos
    box(name + "_frame", pos, size, "darksteel", 0.003)
    if axis == "X":
        gap = sx / (bars + 1)
        for i in range(bars):
            box(f"{name}_bar_{i}", (px - sx / 2 + gap * (i + 1), py, pz), (0.012, sy * 0.92, sz * 0.7), mat, edge)
    else:
        gap = sy / (bars + 1)
        for i in range(bars):
            box(f"{name}_bar_{i}", (px, py - sy / 2 + gap * (i + 1), pz), (sx * 0.92, 0.012, sz * 0.7), mat, edge)
    return bpy.data.objects[name + "_frame"]


def handle(name, pos, width=0.14, mat="steel"):
    p = Vector(pos)
    cyl(name + "_a", p + Vector((-width / 2, 0, 0)), p + Vector((-width / 2, -0.04, 0)), 0.008, mat, 10)
    cyl(name + "_b", p + Vector((width / 2, 0, 0)), p + Vector((width / 2, -0.04, 0)), 0.008, mat, 10)
    cyl(name + "_bar", p + Vector((-width / 2, -0.04, 0)), p + Vector((width / 2, -0.04, 0)), 0.009, mat, 10)
    return bpy.data.objects[name + "_bar"]


def wheel(name, pos, r=0.055, width=0.032, mat="rubber"):
    o = cyl(name, (pos[0], pos[1] - width / 2, pos[2]), (pos[0], pos[1] + width / 2, pos[2]), r, mat, 18, 0.002)
    hub = cyl(name + "_hub", (pos[0], pos[1] - width / 2 - 0.006, pos[2]), (pos[0], pos[1] + width / 2 + 0.006, pos[2]), r * 0.35, "steel", 12, 0.0)
    return o, hub
