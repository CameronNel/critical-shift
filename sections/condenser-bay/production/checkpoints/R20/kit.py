"""Original condenser-bay construction vocabulary. Metres, Z up. No imports."""
import math
import bpy
from mathutils import Vector

S = None
M = {}
GROUP = "00 Scene"
SUPPORT = []
HOOKS = []


def rgb(h):
    v = [int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c < 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in v)


def material(name, h, rough, metal=0, variation=0, bump=0, emission=0, trans=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb(h), 1)
    m.use_nodes = True
    n = m.node_tree.nodes
    l = m.node_tree.links
    b = n.get("Principled BSDF")
    col = rgb(h)
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emission:
        b.inputs["Emission Color"].default_value = (*col, 1)
        b.inputs["Emission Strength"].default_value = emission
    if trans:
        b.inputs["Transmission Weight"].default_value = trans
        b.inputs["IOR"].default_value = 1.45
    if variation or bump:
        tex = n.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 2.8
        tex.inputs["Detail"].default_value = 2
        coord = n.new("ShaderNodeTexCoord")
        l.new(coord.outputs["Generated"], tex.inputs["Vector"])
        ramp = n.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.20
        ramp.color_ramp.elements[1].position = 0.80
        ramp.color_ramp.elements[0].color = (*[max(0, c * (1 - variation)) for c in col], 1)
        ramp.color_ramp.elements[1].color = (*[min(1, c * (1 + variation)) for c in col], 1)
        l.new(tex.outputs["Fac"], ramp.inputs[0])
        l.new(ramp.outputs[0], b.inputs["Base Color"])
        rr = n.new("ShaderNodeMapRange")
        rr.inputs["From Min"].default_value = 0
        rr.inputs["From Max"].default_value = 1
        rr.inputs["To Min"].default_value = max(0, rough - 0.07)
        rr.inputs["To Max"].default_value = min(1, rough + 0.07)
        l.new(tex.outputs["Fac"], rr.inputs[0])
        l.new(rr.outputs[0], b.inputs["Roughness"])
        if bump:
            fine = n.new("ShaderNodeTexNoise")
            fine.inputs["Scale"].default_value = 110
            fine.inputs["Detail"].default_value = 1
            l.new(coord.outputs["Generated"], fine.inputs["Vector"])
            bn = n.new("ShaderNodeBump")
            bn.inputs["Strength"].default_value = 0.18
            bn.inputs["Distance"].default_value = bump
            l.new(fine.outputs["Fac"], bn.inputs["Height"])
            l.new(bn.outputs[0], b.inputs["Normal"])
    return m


def palette():
    global M
    M = {
        "wall": material("Warm mineral plaster", "B3AFA2", 0.88, variation=0.04, bump=0.0018),
        "dado": material("Charcoal impact dado", "3E4248", 0.72, 0.18, 0.04),
        "concrete": material("Dense cast concrete", "86837B", 0.91, variation=0.05, bump=0.0022),
        "floor": material("Basement coated concrete", "6A6760", 0.82, variation=0.06, bump=0.004),
        "patch": material("Replacement floor patch", "7A776E", 0.84, variation=0.02, bump=0.002),
        "oxide": material("Oxide orange enamel", "B56D38", 0.52, 0.18, 0.04, 0.0006),
        "oxide_light": material("Light oxide enamel", "C4844C", 0.56, 0.12, 0.035, 0.0005),
        "struct": material("Structural painted steel", "41444A", 0.62, 0.35, 0.05),
        "cream": material("Thermal jacket ivory", "C8C5B9", 0.78, 0.04, 0.07, 0.0024),
        "steel": material("Machined steel", "7C878A", 0.48, 0.72, 0.06),
        "dark": material("Oiled iron", "30383C", 0.70, 0.48, 0.08),
        "rubber": material("Matte vulcanized rubber", "232829", 0.94, variation=0.05, bump=0.003),
        "yellow": material("Service ochre enamel", "C49C40", 0.58, 0.12, 0.05),
        "red": material("Emergency red enamel", "A34332", 0.52, 0.15),
        "burgundy": material("Safety burgundy", "6E2E2A", 0.60, 0.12, 0.04),
        "wood": material("Worn beech work surface", "826949", 0.82, variation=0.12, bump=0.005),
        "paper": material("Offwhite shift paper", "D4D0B5", 0.97),
        "ink": material("Printed dark ink", "233037", 0.87),
        "cloth": material("Cotton rag", "777268", 0.98, variation=0.06, bump=0.003),
        "white": material("Warm label lettering", "E2DECA", 0.78),
        "lamp": material("Warm diffusing glass", "FFE2B1", 0.52, emission=1.6),
        "glass": material("Clear instrument glass", "9AA3A8", 0.06, 0.02, trans=0.82),
        "water": material("Sight-glass condensate", "7A8A82", 0.08, trans=0.62),
        "iron": material("Machined cast iron", "5A5854", 0.48, 0.62, 0.04, 0.0012),
        "brass": material("Service brass", "8A7040", 0.46, 0.55, 0.03),
    }
    return M


def group(name):
    global GROUP
    GROUP = name
    if name not in bpy.data.collections:
        c = bpy.data.collections.new(name)
        S.collection.children.link(c)
    return bpy.data.collections[name]


def reg(o, name, mat):
    o.name = name
    if mat and hasattr(o.data, "materials"):
        o.data.materials.clear()
        o.data.materials.append(M[mat] if isinstance(mat, str) else mat)
    if GROUP not in bpy.data.collections:
        group(GROUP)
    for c in list(o.users_collection):
        c.objects.unlink(o)
    bpy.data.collections[GROUP].objects.link(o)
    o["construction"] = "authored structural or assembly component"
    return o


def bevel(o, w=0.01):
    if w and o.type == "MESH":
        m = o.modifiers.new("Manufactured edge radius", "BEVEL")
        m.width = w
        m.segments = 2
        o.modifiers.new("Weighted surface normals", "WEIGHTED_NORMAL")
    return o


def _active(o):
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    return o


def box(n, p, d, m, b=0.006):
    bpy.ops.mesh.primitive_cube_add(size=1, location=p)
    o = reg(bpy.context.object, n, m)
    o.dimensions = d
    _active(o)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return bevel(o, min(b, min(d) * 0.22) if min(d) > 0 else 0)


def cyl(n, p, r, length, m, axis="Z", verts=48, b=0.004):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=length, location=p)
    o = reg(bpy.context.object, n, m)
    if axis == "Y":
        o.rotation_euler[0] = math.pi / 2
    if axis == "X":
        o.rotation_euler[1] = math.pi / 2
    for f in o.data.polygons:
        f.use_smooth = len(f.vertices) == 4
    return bevel(o, min(b, r * 0.25, length * 0.2))


def sphere(n, p, r, m, segs=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=max(8, segs // 2), radius=r, location=p)
    o = reg(bpy.context.object, n, m)
    for f in o.data.polygons:
        f.use_smooth = True
    return o


def torus(n, p, R, r, m, axis="Z"):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=R, minor_radius=r, major_segments=48, minor_segments=10, location=p
    )
    o = reg(bpy.context.object, n, m)
    if axis == "Y":
        o.rotation_euler[0] = math.pi / 2
    if axis == "X":
        o.rotation_euler[1] = math.pi / 2
    for f in o.data.polygons:
        f.use_smooth = True
    return o


def mesh(n, verts, faces, m, b=0, smooth=False):
    me = bpy.data.meshes.new(n)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(n, me)
    S.collection.objects.link(o)
    reg(o, n, m)
    if smooth:
        for f in o.data.polygons:
            f.use_smooth = True
    return bevel(o, b)


def beam(n, a, b, r, m):
    a, b = Vector(a), Vector(b)
    o = cyl(n, (a + b) / 2, r, (b - a).length, m, verts=16, b=0.002)
    o.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    return o


def rod(n, a, b, r, m, verts=16):
    return beam(n, a, b, r, m)


def pipe(n, points, r, m, bend=0.22):
    pts = [Vector(p) for p in points]
    samples = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        u = (a - b).normalized()
        v = (c - b).normalized()
        d = min(bend, (a - b).length * 0.34, (c - b).length * 0.34)
        if abs(u.dot(v)) > 0.999:
            samples.append(b)
            continue
        p, q = b + u * d, b + v * d
        samples.append(p)
        for k in range(1, 8):
            t = k / 8
            samples.append((1 - t) ** 2 * p + 2 * (1 - t) * t * b + t * t * q)
    samples.append(pts[-1])
    cu = bpy.data.curves.new(n, "CURVE")
    cu.dimensions = "3D"
    cu.resolution_u = 8
    cu.bevel_depth = r
    cu.bevel_resolution = 3
    sp = cu.splines.new("POLY")
    sp.points.add(len(samples) - 1)
    for p, co in zip(sp.points, samples):
        p.co = (*co, 1)
    o = bpy.data.objects.new(n, cu)
    S.collection.objects.link(o)
    reg(o, n, m)
    o["start_m"] = list(points[0])
    o["end_m"] = list(points[-1])
    a0, a1 = Vector(points[0]), Vector(points[1])
    b0, b1 = Vector(points[-1]), Vector(points[-2])
    for label, p, q in ((" start cap", a0, a1), (" end cap", b0, b1)):
        u = (q - p).normalized()
        cap = cyl(n + label, p + u * r * 0.2, r * 1.12, r * 0.45, m, verts=16, b=0.002)
        cap.rotation_euler = u.to_track_quat("Z", "Y").to_euler()
    return o


def text(n, t, p, size=0.12, mat="white", face="S", align="CENTER"):
    cu = bpy.data.curves.new(n, "FONT")
    cu.body = t
    cu.size = size
    cu.extrude = 0.0006
    cu.align_x = align
    o = bpy.data.objects.new(n, cu)
    S.collection.objects.link(o)
    reg(o, n, mat)
    o.location = p
    o.rotation_euler = {
        "S": (math.pi / 2, 0, 0),
        "N": (math.pi / 2, 0, math.pi),
        "E": (math.pi / 2, 0, math.pi / 2),
        "W": (math.pi / 2, 0, -math.pi / 2),
        "UP": (0, 0, 0),
    }[face]
    o["authored_text"] = t
    return o


def bolt(n, p, axis="Z", r=0.018):
    """Washer + hex head + short shank so pixels read as fasteners, not cubes."""
    u = Vector((0, 0, 1) if axis == "Z" else ((1, 0, 0) if axis == "X" else (0, 1, 0)))
    pv = Vector(p)
    cyl(n + " washer", pv, r * 1.85, max(0.005, r * 0.32), "steel", axis, 24, 0.001)
    cyl(n + " head", pv + u * (r * 0.85), r * 1.35, r * 0.95, "steel", axis, 6, 0.001)
    return cyl(n + " shank", pv - u * (r * 0.55), r * 0.72, r * 1.6, "steel", axis, 12, 0.001)


def flange(n, p, r, axis="Z", mat="cream", bolts=12, thick=0.08):
    cyl(n + " rim", p, r, thick, mat, axis, 48, 0.008)
    cyl(n + " gasket", p, r * 0.86, thick * 0.22, "rubber", axis, 32, 0.002)
    u = Vector((0, 0, 1) if axis == "Z" else ((1, 0, 0) if axis == "X" else (0, 1, 0)))
    a = u.orthogonal().normalized()
    b = u.cross(a).normalized()
    pv = Vector(p)
    for i in range(bolts):
        t = i * math.tau / bolts
        q = pv + (a * math.cos(t) + b * math.sin(t)) * (r * 0.82)
        bolt(n + f" stud{i}", q, axis, 0.014 if r < 0.35 else 0.02)


def wheel(n, p, r=0.16, axis="X", mat="yellow"):
    torus(n + " rim", p, r, 0.018, mat, axis)
    u = Vector((1, 0, 0) if axis == "X" else ((0, 1, 0) if axis == "Y" else (0, 0, 1)))
    a = u.orthogonal().normalized()
    b = u.cross(a).normalized()
    pv = Vector(p)
    for k in range(3):
        d = a * math.cos(k * math.tau / 3) + b * math.sin(k * math.tau / 3)
        rod(n + f" spoke{k}", pv, pv + d * r, 0.012, mat)
    cyl(n + " hub", p, 0.038, 0.07, "dark", axis, 24)
    o = bpy.data.objects.get(n + " rim")
    if o:
        o["interaction"] = "manual valve rotate"
    return o


def gauge(n, p, axis="X", r=0.11):
    u = Vector((1, 0, 0) if axis == "X" else ((0, 1, 0) if axis == "Y" else (0, 0, 1)))
    a = u.orthogonal().normalized()
    b = u.cross(a).normalized()
    pv = Vector(p)
    cyl(n + " can", p, r * 1.08, 0.07, "dark", axis, 40, 0.005)
    cyl(n + " bezel", pv + u * 0.012, r, 0.028, "steel", axis, 40, 0.003)
    torus(n + " rim", pv + u * 0.024, r * 0.96, 0.008, "steel", axis)
    face = pv + u * 0.028
    cyl(n + " glass", face, r * 0.86, 0.008, "glass", axis, 32)
    cyl(n + " dial", face - u * 0.006, r * 0.82, 0.008, "paper", axis, 32)
    for i in range(11):
        ang = math.pi * 0.15 + math.pi * 1.7 * i / 10
        d0, d1 = r * 0.58, r * 0.74
        aa = face + (a * math.cos(ang) + b * math.sin(ang)) * d0 + u * 0.006
        bb = face + (a * math.cos(ang) + b * math.sin(ang)) * d1 + u * 0.006
        rod(n + f" tick{i}", aa, bb, 0.0022, "ink")
    tip = face + (a * math.cos(math.pi * 0.55) + b * math.sin(math.pi * 0.55)) * r * 0.52 + u * 0.008
    rod(n + " needle", face + u * 0.006, tip, 0.0035, "burgundy")
    cyl(n + " pivot", face + u * 0.006, 0.012, 0.012, "dark", axis, 12)
    return face


def rotary(n, p, axis="X", r=0.042, accent="dark"):
    """Industrial panel rotary: knurled skirt, pointer, scale ticks."""
    u = Vector((1, 0, 0) if axis == "X" else ((0, 1, 0) if axis == "Y" else (0, 0, 1)))
    a = u.orthogonal().normalized()
    b = u.cross(a).normalized()
    pv = Vector(p)
    cyl(n + " boss", pv - u * 0.012, r * 1.55, 0.028, "dark", axis, 32, 0.003)
    cyl(n + " skirt", p, r * 1.15, 0.022, "steel", axis, 36, 0.003)
    torus(n + " knurl", pv + u * 0.006, r * 1.05, 0.006, "steel", axis)
    cyl(n + " barrel", pv + u * 0.018, r * 0.72, 0.028, accent, axis, 28, 0.003)
    cyl(n + " cap", pv + u * 0.036, r * 0.55, 0.012, "dark", axis, 24, 0.002)
    tip = pv + u * 0.042 + b * r * 0.82
    rod(n + " pointer", pv + u * 0.042, tip, 0.005, "yellow")
    for i in range(7):
        ang = math.pi * 0.2 + math.pi * 1.6 * i / 6
        d = a * math.cos(ang) + b * math.sin(ang)
        rod(n + f" scale{i}", pv + d * r * 1.35 - u * 0.004, pv + d * r * 1.58 - u * 0.004, 0.002, "white")
    return p


def light(n, p, target, power, color=(1.0, 0.86, 0.68), size=1.2, shape="DISK", size_y=None, shadows=True):
    d = bpy.data.lights.new(n, "AREA")
    d.energy = power
    d.color = color
    d.shape = shape
    d.size = size
    d.use_shadow = shadows
    if size_y and shape == "RECTANGLE":
        d.size_y = size_y
    o = bpy.data.objects.new(n, d)
    S.collection.objects.link(o)
    reg(o, n, None)
    o.location = p
    o.rotation_euler = (Vector(target) - Vector(p)).to_track_quat("-Z", "Y").to_euler()
    return o


def camera(n, p, target, lens=28):
    d = bpy.data.cameras.new(n)
    d.lens = lens
    d.clip_start = 0.06
    d.clip_end = 80
    o = bpy.data.objects.new(n, d)
    S.collection.objects.link(o)
    reg(o, n, None)
    o.location = p
    o.rotation_euler = (Vector(target) - Vector(p)).to_track_quat("-Z", "Y").to_euler()
    return o


def empty(n, p, kind="handoff"):
    o = bpy.data.objects.new(n, None)
    bpy.data.collections[GROUP].objects.link(o)
    o.location = p
    o.empty_display_size = 0.12
    o["handoff"] = kind
    return o


def anchor(n, p, target, direction=(0, 0, -1), gap=0.008, penetration=0.003):
    o = bpy.data.objects.new("SUPPORT_" + n, None)
    bpy.data.collections[GROUP].objects.link(o)
    o.location = p
    o.empty_display_size = 0.04
    SUPPORT.append(
        dict(
            anchor=o.name,
            target=target,
            direction=list(direction),
            max_gap=gap,
            max_penetration=penetration,
        )
    )
    return o


def hook(hid, p, action, equipment):
    HOOKS.append(dict(id=hid, centre=list(p), action=action, equipment=equipment, status="design_contract_not_runtime"))
    o = empty(hid, p, "interaction")
    o["action"] = action
    return o


def shell_along_x(n, x0, x1, cy, cz, ry, rz, m, segs=28, b=0.012):
    verts = []
    for x in (x0, x1):
        for i in range(segs):
            a = i * math.tau / segs
            verts.append((x, cy + ry * math.cos(a), cz + rz * math.sin(a)))
    faces = [tuple(range(segs - 1, -1, -1)), tuple(range(segs, 2 * segs))]
    faces += [(i, (i + 1) % segs, segs + (i + 1) % segs, segs + i) for i in range(segs)]
    return mesh(n, verts, faces, m, b, True)


def boolean_cut(target, cutter, name="cut"):
    import bpy

    bpy.context.view_layer.objects.active = target
    target.select_set(True)
    mod = target.modifiers.new(name, "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cutter
    try:
        bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=0)
    except Exception:
        pass
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return target


def annulus(n, p, r_out, r_in, thick, m, axis="X"):
    return torus(n, p, (r_out + r_in) * 0.5, max(0.008, (r_out - r_in) * 0.5), m, axis)


def globe_valve(n, p, pipe_axis="Y", r=0.13):
    x, y, z = p
    sphere(n + " globe", p, r, "steel", 28)
    if pipe_axis == "Y":
        cyl(n + " port A", (x, y + r * 0.7, z), r * 0.72, r * 0.55, "steel", "Y", 24, 0.006)
        cyl(n + " port B", (x, y - r * 0.7, z), r * 0.72, r * 0.55, "steel", "Y", 24, 0.006)
        flange(n + " fl A", (x, y + r * 0.95, z), r * 0.95, "Y", "steel", 8, 0.04)
        flange(n + " fl B", (x, y - r * 0.95, z), r * 0.95, "Y", "steel", 8, 0.04)
    else:
        cyl(n + " port A", (x + r * 0.7, y, z), r * 0.72, r * 0.55, "steel", "X", 24, 0.006)
        cyl(n + " port B", (x - r * 0.7, y, z), r * 0.72, r * 0.55, "steel", "X", 24, 0.006)
        flange(n + " fl A", (x + r * 0.95, y, z), r * 0.95, "X", "steel", 8, 0.04)
        flange(n + " fl B", (x - r * 0.95, y, z), r * 0.95, "X", "steel", 8, 0.04)
    cyl(n + " bonnet", (x, y, z + r * 0.85), r * 0.42, r * 0.55, "steel", "Z", 24, 0.006)
    box(n + " yoke L", (x - r * 0.28, y, z + r * 1.35), (0.03, 0.04, r * 0.55), "steel", 0.003)
    box(n + " yoke R", (x + r * 0.28, y, z + r * 1.35), (0.03, 0.04, r * 0.55), "steel", 0.003)
    cyl(n + " stem", (x, y, z + r * 1.55), 0.022, r * 0.7, "steel", "Z", 12)
    wheel(n + " handwheel", (x, y, z + r * 1.95), r * 1.15, "Z", "yellow")


def i_beam(n, a, b, width=0.18, depth=0.28, mat="yellow"):
    a, b = Vector(a), Vector(b)
    mid = (a + b) / 2
    length = (b - a).length
    axis = "X" if abs(b.x - a.x) > abs(b.y - a.y) else "Y"
    if axis == "X":
        box(n + " web", mid, (length, 0.028, depth - 0.04), "struct", 0.003)
        box(n + " top fl", (mid.x, mid.y, mid.z + depth / 2 - 0.018), (length, width, 0.036), mat, 0.004)
        box(n + " bot fl", (mid.x, mid.y, mid.z - depth / 2 + 0.018), (length, width, 0.036), mat, 0.004)
    else:
        box(n + " web", mid, (0.028, length, depth - 0.04), "struct", 0.003)
        box(n + " top fl", (mid.x, mid.y, mid.z + depth / 2 - 0.018), (width, length, 0.036), mat, 0.004)
        box(n + " bot fl", (mid.x, mid.y, mid.z - depth / 2 + 0.018), (width, length, 0.036), mat, 0.004)
