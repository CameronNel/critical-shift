"""
Spawn-room art pass: clean stylized modern lab (chunky forms, not pirate).
Matches critical-shift-spawn-room concept board.
Does not touch mine / transit collections.
"""
import math
import os
import bpy
import bmesh
from mathutils import Euler

TEX = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "textures", "spawn"
)
COL_NAME = "CS_LabArtPass"
SKIP_COL = ("07_Transit_and_Mine", "Transit", "Mine")

# T-layout, rooms mid-hallway
HX0, HX1 = -3.05, 3.05
HY0, HY1 = 0.0, 14.4
RY0, RY1 = 4.25, 12.75
LX0, LX1 = 3.12, 11.88
BX0, BX1 = -11.88, -3.12
WALL = 0.30
CEIL = 3.62
DOOR_W, DOOR_H = 2.30, 2.48


def _is_mine(obj):
    for c in obj.users_collection:
        n = c.name
        if "Mine" in n or "Transit" in n:
            return True
    return False


def col():
    c = bpy.data.collections.get(COL_NAME)
    if c is None:
        c = bpy.data.collections.new(COL_NAME)
        bpy.context.scene.collection.children.link(c)
    return c


def clear_pass():
    c = bpy.data.collections.get(COL_NAME)
    if not c:
        return
    for ob in list(c.objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def mat(name, color, rough=0.48, metal=0.0, emit=None, emit_str=0.0, img=None, emit_img=False):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (420, 0)
    pr = nt.nodes.new("ShaderNodeBsdfPrincipled")
    pr.location = (80, 0)
    pr.inputs["Base Color"].default_value = (*color, 1.0)
    pr.inputs["Roughness"].default_value = rough
    pr.inputs["Metallic"].default_value = metal
    shader = pr.outputs["BSDF"]
    if img and os.path.isfile(img):
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.location = (-280, 40)
        tex.image = bpy.data.images.load(img, check_existing=True)
        tex.interpolation = "Smart"
        if emit_img:
            em = nt.nodes.new("ShaderNodeEmission")
            em.location = (80, -180)
            em.inputs["Strength"].default_value = 4.2
            nt.links.new(tex.outputs["Color"], em.inputs["Color"])
            add = nt.nodes.new("ShaderNodeAddShader")
            add.location = (280, -40)
            nt.links.new(tex.outputs["Color"], pr.inputs["Base Color"])
            pr.inputs["Roughness"].default_value = 0.22
            nt.links.new(pr.outputs["BSDF"], add.inputs[0])
            nt.links.new(em.outputs["Emission"], add.inputs[1])
            shader = add.outputs["Shader"]
        else:
            nt.links.new(tex.outputs["Color"], pr.inputs["Base Color"])
    if emit is not None:
        if "Emission Color" in pr.inputs:
            pr.inputs["Emission Color"].default_value = (*emit, 1.0)
            pr.inputs["Emission Strength"].default_value = emit_str
        elif "Emission" in pr.inputs:
            pr.inputs["Emission"].default_value = (*emit, 1.0)
    nt.links.new(shader, out.inputs["Surface"])
    return m


def box(name, loc, size, material, collection, bevel=0.025, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    me = bpy.data.meshes.new(name + "_me")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = Euler(rot)
    if material:
        ob.data.materials.append(material)
    if bevel > 0.001:
        md = ob.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = 2
        md.limit_method = "ANGLE"
    collection.objects.link(ob)
    return ob


def cyl(name, loc, radius, depth, material, collection, segs=18, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=True, segments=segs, radius1=radius, radius2=radius, depth=depth
    )
    me = bpy.data.meshes.new(name + "_me")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = Euler(rot)
    if material:
        ob.data.materials.append(material)
    collection.objects.link(ob)
    return ob


def hide_name(name):
    ob = bpy.data.objects.get(name)
    if not ob or _is_mine(ob):
        return
    ob.hide_set(True)
    ob.hide_viewport = True
    ob.hide_render = True


def hide_prefixes(prefixes):
    for ob in bpy.data.objects:
        if _is_mine(ob):
            continue
        if ob.type == "CAMERA":
            continue
        if any(ob.name.startswith(p) for p in prefixes):
            ob.hide_set(True)
            ob.hide_viewport = True
            ob.hide_render = True


def uv_cube_project(ob, scale=1.0):
    me = ob.data
    me.uv_layers.new(name="UVMap") if not me.uv_layers else None
    uv = me.uv_layers.active.data
    for loop in me.loops:
        pass
    # Simple generated: each face 0-1
    me.calc_loop_triangles()
    idx = 0
    for poly in me.polygons:
        for li in poly.loop_indices:
            loop = me.loops[li]
            v = me.vertices[loop.vertex_index].co
            n = poly.normal
            if abs(n.z) > 0.6:
                uv[li].uv = (v.x * scale, v.y * scale)
            elif abs(n.y) > 0.6:
                uv[li].uv = (v.x * scale, v.z * scale)
            else:
                uv[li].uv = (v.y * scale, v.z * scale)


def palette():
    p = {}
    p["wall"] = mat("M_Lab_Wall", (0.82, 0.84, 0.86), 0.62, 0.02)
    p["wainscot"] = mat("M_Lab_Wainscot", (0.22, 0.48, 0.52), 0.42, 0.12)
    p["teal"] = mat("M_Lab_Teal", (0.18, 0.46, 0.50), 0.40, 0.18)
    p["iron"] = mat("M_Lab_Iron", (0.16, 0.18, 0.20), 0.48, 0.82)
    p["brass"] = mat("M_Lab_Brass", (0.70, 0.50, 0.22), 0.32, 0.92)
    p["panel"] = mat("M_Lab_Panel", (0.70, 0.72, 0.74), 0.50, 0.08)
    p["locker"] = mat("M_Lab_Locker", (0.78, 0.80, 0.82), 0.38, 0.12)
    p["pad"] = mat("M_Lab_Pad", (0.20, 0.50, 0.54), 0.55, 0.04)
    p["rubber"] = mat("M_Lab_Rubber", (0.10, 0.11, 0.12), 0.55, 0.05)
    p["floor"] = mat(
        "M_Lab_Floor",
        (0.74, 0.76, 0.77),
        0.55,
        0.02,
        img=os.path.join(TEX, "floor_tiles.jpg"),
    )
    p["inlay"] = mat("M_Lab_Inlay", (0.24, 0.50, 0.54), 0.45, 0.08)
    p["stripe"] = mat("M_Lab_Stripe", (0.84, 0.70, 0.16), 0.40, 0.06)
    p["screen"] = mat(
        "M_Lab_Screen",
        (0.05, 0.22, 0.26),
        0.18,
        0.05,
        img=os.path.join(TEX, "briefing_screen.jpg"),
        emit_img=True,
    )
    p["glass"] = mat("M_Lab_Glass", (0.25, 0.55, 0.58), 0.08, 0.05, emit=(0.20, 0.70, 0.75), emit_str=0.6)
    p["leaf"] = mat("M_Lab_Leaf", (0.18, 0.42, 0.22), 0.62, 0.0)
    p["soil"] = mat("M_Lab_Soil", (0.18, 0.14, 0.10), 0.85, 0.0)
    p["warm"] = mat("M_Lab_WarmEmit", (1.0, 0.88, 0.62), 0.25, 0.0, emit=(1.0, 0.86, 0.55), emit_str=6.0)
    p["cool"] = mat("M_Lab_CoolEmit", (0.75, 0.88, 1.0), 0.25, 0.0, emit=(0.70, 0.85, 1.0), emit_str=3.5)
    p["paper"] = mat("M_Lab_Paper", (0.90, 0.91, 0.88), 0.72, 0.0)
    p["visor"] = mat("M_Lab_Visor", (0.12, 0.42, 0.48), 0.08, 0.15, emit=(0.15, 0.55, 0.60), emit_str=0.45)
    p["sy"] = mat("M_Lab_SuitY", (0.78, 0.58, 0.16), 0.58, 0.04)
    p["sc"] = mat("M_Lab_SuitC", (0.30, 0.62, 0.70), 0.58, 0.04)
    p["sw"] = mat("M_Lab_SuitW", (0.86, 0.88, 0.90), 0.55, 0.04)
    p["so"] = mat("M_Lab_SuitO", (0.80, 0.40, 0.14), 0.58, 0.04)
    p["helm"] = mat("M_Lab_Helm", (0.22, 0.26, 0.28), 0.35, 0.35)
    p["boot"] = mat("M_Lab_Boot", (0.12, 0.12, 0.13), 0.50, 0.08)
    return p


def wall_slab(name, x0, x1, y0, y1, z0, z1, m, c, bevel=0.02):
    loc = ((x0 + x1) * 0.5, (y0 + y1) * 0.5, (z0 + z1) * 0.5)
    size = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    return box(name, loc, size, m, c, bevel)


def airlock(prefix, x, y, facing_x, p, c):
    """Open double door in a wall at x, centered on y. facing_x +1 means room is +X."""
    zc = DOOR_H * 0.5
    thick = 0.22
    frame_d = 0.46
    # opening carved by not placing wall there; we add frame around it
    jamb = 0.18
    # left/right jambs (along Y)
    wall_slab(prefix + "_JambS", x - frame_d * 0.5, x + frame_d * 0.5,
              y - DOOR_W * 0.5 - jamb, y - DOOR_W * 0.5, 0, DOOR_H + 0.18, p["teal"], c)
    wall_slab(prefix + "_JambN", x - frame_d * 0.5, x + frame_d * 0.5,
              y + DOOR_W * 0.5, y + DOOR_W * 0.5 + jamb, 0, DOOR_H + 0.18, p["teal"], c)
    wall_slab(prefix + "_Header", x - frame_d * 0.5, x + frame_d * 0.5,
              y - DOOR_W * 0.5 - jamb, y + DOOR_W * 0.5 + jamb, DOOR_H, DOOR_H + 0.22, p["teal"], c)
    wall_slab(prefix + "_BrassBar", x - frame_d * 0.5 - 0.01, x + frame_d * 0.5 + 0.01,
              y - DOOR_W * 0.35, y + DOOR_W * 0.35, DOOR_H + 0.16, DOOR_H + 0.24, p["brass"], c, 0.01)
    # doors slid open along Y
    slide = DOOR_W * 0.42
    dw, dd, dh = 0.95, 0.08, DOOR_H - 0.12
    ys = y - DOOR_W * 0.5 - slide * 0.15
    yn = y + DOOR_W * 0.5 + slide * 0.15
    d1 = box(prefix + "_DoorS", (x + facing_x * 0.08, y - DOOR_W * 0.55 - 0.15, dh * 0.5 + 0.04),
             (dd, dw, dh), p["iron"], c, 0.015)
    d2 = box(prefix + "_DoorN", (x + facing_x * 0.08, y + DOOR_W * 0.55 + 0.15, dh * 0.5 + 0.04),
             (dd, dw, dh), p["iron"], c, 0.015)
    # round windows
    cyl(prefix + "_WinS", (x + facing_x * 0.13, y - DOOR_W * 0.55 - 0.15, 1.55),
        0.16, 0.06, p["glass"], c, 12, rot=(0, math.pi / 2, 0))
    cyl(prefix + "_WinN", (x + facing_x * 0.13, y + DOOR_W * 0.55 + 0.15, 1.55),
        0.16, 0.06, p["glass"], c, 12, rot=(0, math.pi / 2, 0))
    # brass handles
    box(prefix + "_HdlS", (x + facing_x * 0.14, y - DOOR_W * 0.35, 1.15),
        (0.04, 0.04, 0.22), p["brass"], c, 0.008)
    box(prefix + "_HdlN", (x + facing_x * 0.14, y + DOOR_W * 0.35, 1.15),
        (0.04, 0.04, 0.22), p["brass"], c, 0.008)
    return d1, d2


def column(name, loc, p, c, h=CEIL):
    box(name + "_Post", (loc[0], loc[1], h * 0.5), (0.32, 0.32, h), p["teal"], c, 0.03)
    cyl(name + "_Cap", (loc[0], loc[1], h - 0.08), 0.22, 0.10, p["brass"], c, 16)
    box(name + "_Base", (loc[0], loc[1], 0.08), (0.38, 0.38, 0.16), p["iron"], c, 0.02)


def lamp(name, loc, rot_z, p, c):
    box(name + "_Arm", loc, (0.08, 0.18, 0.08), p["brass"], c, 0.01, rot=(0, 0, rot_z))
    box(name + "_Shade", (loc[0], loc[1], loc[2] - 0.06), (0.16, 0.22, 0.10), p["panel"], c, 0.012, rot=(0, 0, rot_z))
    box(name + "_Bulb", (loc[0], loc[1], loc[2] - 0.10), (0.10, 0.10, 0.04), p["warm"], c, 0.005)


def locker_unit(name, loc, yaw, p, c):
    """Single tall locker facing +local Y after yaw."""
    root = box(name + "_Body", loc, (0.62, 0.42, 2.20), p["locker"], c, 0.018, rot=(0, 0, yaw))
    box(name + "_Door", loc, (0.54, 0.08, 2.04), p["panel"], c, 0.012, rot=(0, 0, yaw))
    # offset door toward facing
    fx, fy = math.sin(yaw), math.cos(yaw)
    # yaw 0 => door toward +Y
    root  # keep
    d = bpy.data.objects[name + "_Door"]
    d.location = (loc[0] + fy * 0.18, loc[1] + fx * 0.0, loc[2])
    # actually: yaw=0 along +Y is south-facing if we place on north wall...
    # Simpler: place door slightly in front along the rotation
    from mathutils import Vector
    off = Euler((0, 0, yaw)).to_matrix() @ Vector((0, 0.20, 0))
    d.location = (loc[0] + off.x, loc[1] + off.y, loc[2])
    bpy.data.objects[name + "_Body"].location = loc
    hloc = Euler((0, 0, yaw)).to_matrix() @ Vector((0.18, 0.24, 0.15))
    box(name + "_Handle", (loc[0] + hloc.x, loc[1] + hloc.y, loc[2] + 0.15),
        (0.05, 0.05, 0.14), p["brass"], c, 0.006, rot=(0, 0, yaw))
    tloc = Euler((0, 0, yaw)).to_matrix() @ Vector((0.0, 0.22, 0.95))
    box(name + "_Trim", (loc[0] + tloc.x, loc[1] + tloc.y, loc[2] + 0.95),
        (0.56, 0.03, 0.04), p["teal"], c, 0.005, rot=(0, 0, yaw))
    return root


def locker_bank(prefix, origin, count, yaw, p, c, spacing=0.68):
    from mathutils import Vector
    right = Euler((0, 0, yaw)).to_matrix() @ Vector((1, 0, 0))
    start = Vector(origin) - right * ((count - 1) * spacing * 0.5)
    for i in range(count):
        loc = start + right * (i * spacing)
        locker_unit(f"{prefix}_{i:02d}", (loc.x, loc.y, 1.12), yaw, p, c)


def alcove(name, loc, p, c):
    """Open bay in the east wall for a hanging suit. loc is bay center on floor."""
    x, y, z = loc
    box(name + "_Back", (x + 0.22, y, 1.15), (0.10, 1.10, 2.30), p["iron"], c, 0.015)
    box(name + "_L", (x, y - 0.56, 1.15), (0.42, 0.08, 2.30), p["teal"], c, 0.015)
    box(name + "_R", (x, y + 0.56, 1.15), (0.42, 0.08, 2.30), p["teal"], c, 0.015)
    box(name + "_Top", (x, y, 2.28), (0.42, 1.16, 0.08), p["teal"], c, 0.012)
    box(name + "_Rail", (x - 0.02, y, 2.05), (0.06, 0.90, 0.05), p["iron"], c, 0.008)
    cyl(name + "_Hook", (x - 0.02, y, 1.96), 0.03, 0.10, p["brass"], c, 10)


def adult_suit(name, loc, yaw, fabric, p, c):
    """Adult industrial PPE, hanging. No mascot proportions."""
    x, y, z = loc
    # boots on alcove deck
    box(name + "_BootL", (x, y - 0.12, 0.10), (0.22, 0.14, 0.20), p["boot"], c, 0.02, rot=(0, 0, yaw))
    box(name + "_BootR", (x, y + 0.12, 0.10), (0.22, 0.14, 0.20), p["boot"], c, 0.02, rot=(0, 0, yaw))
    box(name + "_LegL", (x, y - 0.12, 0.58), (0.16, 0.13, 0.78), fabric, c, 0.02, rot=(0, 0, yaw))
    box(name + "_LegR", (x, y + 0.12, 0.58), (0.16, 0.13, 0.78), fabric, c, 0.02, rot=(0, 0, yaw))
    box(name + "_Hip", (x, y, 0.98), (0.28, 0.40, 0.16), fabric, c, 0.02, rot=(0, 0, yaw))
    box(name + "_Torso", (x, y, 1.38), (0.26, 0.48, 0.70), fabric, c, 0.025, rot=(0, 0, yaw))
    box(name + "_Collar", (x, y, 1.74), (0.24, 0.36, 0.10), p["rubber"], c, 0.015, rot=(0, 0, yaw))
    box(name + "_ArmL", (x, y - 0.30, 1.28), (0.14, 0.12, 0.62), fabric, c, 0.02, rot=(0, 0, yaw))
    box(name + "_ArmR", (x, y + 0.30, 1.28), (0.14, 0.12, 0.62), fabric, c, 0.02, rot=(0, 0, yaw))
    box(name + "_GloveL", (x, y - 0.30, 0.94), (0.12, 0.11, 0.12), p["rubber"], c, 0.015, rot=(0, 0, yaw))
    box(name + "_GloveR", (x, y + 0.30, 0.94), (0.12, 0.11, 0.12), p["rubber"], c, 0.015, rot=(0, 0, yaw))
    # enclosed adult helmet, not a giant head
    cyl(name + "_Helm", (x, y, 1.92), 0.16, 0.22, p["helm"], c, 14, rot=(0, 0, yaw))
    box(name + "_Visor", (x - 0.12, y, 1.90), (0.04, 0.22, 0.12), p["visor"], c, 0.01, rot=(0, 0, yaw))
    box(name + "_Pack", (x + 0.14, y, 1.42), (0.10, 0.22, 0.32), p["iron"], c, 0.015, rot=(0, 0, yaw))
    cyl(name + "_Gauge", (x + 0.18, y, 1.52), 0.04, 0.03, p["brass"], c, 10, rot=(0, math.pi / 2, 0))


def bench(name, loc, yaw, length, p, c):
    box(name + "_Pad", loc, (length, 0.46, 0.09), p["pad"], c, 0.02, rot=(0, 0, yaw))
    box(name + "_Frame", (loc[0], loc[1], loc[2] - 0.16), (length - 0.1, 0.34, 0.08), p["iron"], c, 0.015, rot=(0, 0, yaw))
    from mathutils import Vector
    for sx in (-length * 0.38, length * 0.38):
        off = Euler((0, 0, yaw)).to_matrix() @ Vector((sx, 0, 0))
        box(name + f"_Leg{sx:.0f}", (loc[0] + off.x, loc[1] + off.y, 0.22),
            (0.10, 0.28, 0.44), p["iron"], c, 0.015, rot=(0, 0, yaw))
        box(name + f"_Foot{sx:.0f}", (loc[0] + off.x, loc[1] + off.y, 0.04),
            (0.14, 0.32, 0.06), p["brass"], c, 0.008, rot=(0, 0, yaw))


def lectern(name, loc, p, c):
    box(name + "_Body", loc, (0.70, 0.55, 1.05), p["iron"], c, 0.02)
    box(name + "_Top", (loc[0], loc[1], loc[2] + 0.58), (0.78, 0.62, 0.08), p["teal"], c, 0.015)
    box(name + "_PlusH", (loc[0], loc[1] - 0.29, loc[2] + 0.15), (0.22, 0.04, 0.06), p["cool"], c, 0.005)
    box(name + "_PlusV", (loc[0], loc[1] - 0.29, loc[2] + 0.15), (0.06, 0.04, 0.22), p["cool"], c, 0.005)


def plant(name, loc, p, c):
    cyl(name + "_Pot", (loc[0], loc[1], 0.22), 0.18, 0.44, p["teal"], c, 12)
    cyl(name + "_Dirt", (loc[0], loc[1], 0.42), 0.15, 0.08, p["soil"], c, 10)
    box(name + "_Stem", (loc[0], loc[1], 0.70), (0.04, 0.04, 0.55), p["leaf"], c, 0.01)
    for i, (dx, dy, dz) in enumerate(((-0.12, 0.05, 0.95), (0.10, -0.08, 1.05), (0.02, 0.14, 1.15), (-0.06, -0.12, 0.85))):
        box(name + f"_Leaf{i}", (loc[0] + dx, loc[1] + dy, dz), (0.22, 0.10, 0.03), p["leaf"], c, 0.008)


def sign_plane(name, loc, size, path, c, rot=(0, 0, 0)):
    m = mat(name + "_Mat", (0.8, 0.8, 0.8), 0.45, 0.05, img=path)
    ob = box(name, loc, size, m, c, 0.008, rot=rot)
    uv_cube_project(ob, 0.5)
    return ob


def roof(name, x0, x1, y0, y1, p, c, rib_axis="y"):
    wall_slab(name + "_Slab", x0, x1, y0, y1, CEIL - 0.10, CEIL + 0.06, p["panel"], c, 0.01)
    # teal ribs
    if rib_axis == "y":
        n = max(3, int((y1 - y0) / 1.7))
        for i in range(n):
            t = i / max(n - 1, 1)
            y = y0 + 0.35 + t * (y1 - y0 - 0.7)
            wall_slab(f"{name}_Rib{i}", x0 + 0.08, x1 - 0.08, y - 0.07, y + 0.07,
                      CEIL - 0.22, CEIL - 0.04, p["teal"], c, 0.012)
    else:
        n = max(3, int((x1 - x0) / 1.7))
        for i in range(n):
            t = i / max(n - 1, 1)
            x = x0 + 0.35 + t * (x1 - x0 - 0.7)
            wall_slab(f"{name}_Rib{i}", x - 0.07, x + 0.07, y0 + 0.08, y1 - 0.08,
                      CEIL - 0.22, CEIL - 0.04, p["teal"], c, 0.012)


def tile_floor(name, x0, x1, y0, y1, p, c):
    ob = wall_slab(name, x0, x1, y0, y1, 0.00, 0.04, p["floor"], c, 0.0)
    uv_cube_project(ob, 0.55)
    return ob


def add_area_light(name, loc, size, energy, color, collection):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.color = color
    data.size = size[0]
    if hasattr(data, "size_y"):
        data.shape = "RECTANGLE"
        data.size_y = size[1]
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    ob.rotation_euler = (0, 0, 0)
    collection.objects.link(ob)
    return ob


def build():
    clear_pass()
    c = col()
    p = palette()

    # Hide old spawn dressing we are replacing. Keep cameras, mine, hallway kit bones.
    hide_prefixes((
        "Hero_Hazmat_Suit_",
        "Assembled_Hero_Suit_Wall_Rack",
        "Assembled_SOT_Changing_Bench",
        "Assembled_SOT_Team_Bench",
        "Assembled_SOT_Tactical_Screen",
        "Assembled_SOT_Speaker_Podium",
        "Assembled_SOT_Notice_Board",
        "Assembled_SOT_LockerBank_",
        "Assembled_SOT_Ceiling_Pendant",
        "SOT_Wall_South_Lockers",
        "SOT_Wall_North_Lockers",
        "SOT_Wall_South_Brief",
        "SOT_Wall_North_Brief",
        "SOT_Floor_Locker_Wing",
        "SOT_Floor_Briefing_Wing",
    ))
    hide_name("Assembled_Hero_Suit_Wall_Rack")

    # --- Hallway partitions (keep corridor, punch room doors) ---
    y_door0 = 8.50 - DOOR_W * 0.5
    y_door1 = 8.50 + DOOR_W * 0.5
    # east hallway wall (locker side), north and south of door, plus bulkheads
    wall_slab("Hall_East_S", HX1 - 0.08, HX1 + WALL, HY0, RY0, 0, CEIL, p["wainscot"], c)
    wall_slab("Hall_East_S2", HX1 - 0.08, HX1 + WALL, RY0, y_door0, 0, CEIL, p["wall"], c)
    wall_slab("Hall_East_N2", HX1 - 0.08, HX1 + WALL, y_door1, RY1, 0, CEIL, p["wall"], c)
    wall_slab("Hall_East_N", HX1 - 0.08, HX1 + WALL, RY1, HY1, 0, CEIL, p["wainscot"], c)
    wall_slab("Hall_East_Over", HX1 - 0.08, HX1 + WALL, y_door0, y_door1, DOOR_H, CEIL, p["wall"], c)
    # west hallway wall (briefing)
    wall_slab("Hall_West_S", HX0 - WALL, HX0 + 0.08, HY0, RY0, 0, CEIL, p["wainscot"], c)
    wall_slab("Hall_West_S2", HX0 - WALL, HX0 + 0.08, RY0, y_door0, 0, CEIL, p["wall"], c)
    wall_slab("Hall_West_N2", HX0 - WALL, HX0 + 0.08, y_door1, RY1, 0, CEIL, p["wall"], c)
    wall_slab("Hall_West_N", HX0 - WALL, HX0 + 0.08, RY1, HY1, 0, CEIL, p["wainscot"], c)
    wall_slab("Hall_West_Over", HX0 - WALL, HX0 + 0.08, y_door0, y_door1, DOOR_H, CEIL, p["wall"], c)

    airlock("Air_Locker", LX0 + 0.02, 8.50, +1, p, c)
    airlock("Air_Brief", BX1 - 0.02, 8.50, -1, p, c)

    # --- Locker room envelope ---
    wall_slab("Lock_South", LX0, LX1, RY0 - WALL, RY0, 0, CEIL, p["wall"], c)
    wall_slab("Lock_North", LX0, LX1, RY1, RY1 + WALL, 0, CEIL, p["wall"], c)
    wall_slab("Lock_WainS", LX0 + 0.2, LX1 - 0.2, RY0, RY0 + 0.04, 0, 1.15, p["wainscot"], c)
    wall_slab("Lock_WainN", LX0 + 0.2, LX1 - 0.2, RY1 - 0.04, RY1, 0, 1.15, p["wainscot"], c)
    wall_slab("Lock_WainE", LX1 - 0.06, LX1, RY0 + 0.1, RY1 - 0.1, 0, 1.15, p["wainscot"], c)
    # interior liner on existing east wall
    wall_slab("Lock_EastLiner", LX1 - 0.08, LX1, RY0, RY1, 1.15, CEIL, p["wall"], c)
    # bulkheads south/north of room so the T reads as rooms not open wings
    wall_slab("Lock_BulkS", LX0, LX1, HY0, RY0 - WALL, 0, CEIL, p["iron"], c)
    wall_slab("Lock_BulkN", LX0, LX1, RY1 + WALL, HY1, 0, CEIL, p["iron"], c)

    tile_floor("Lock_Floor", LX0 + 0.05, LX1 - 0.05, RY0 + 0.05, RY1 - 0.05, p, c)
    wall_slab("Lock_Inlay", 6.6, 10.4, 7.55, 9.45, 0.035, 0.055, p["inlay"], c, 0.01)
    roof("Lock_Roof", LX0, LX1, RY0, RY1, p, c, rib_axis="x")

    # --- Briefing envelope ---
    wall_slab("Brief_South", BX0, BX1, RY0 - WALL, RY0, 0, CEIL, p["wall"], c)
    wall_slab("Brief_North", BX0, BX1, RY1, RY1 + WALL, 0, CEIL, p["wall"], c)
    wall_slab("Brief_WainS", BX0 + 0.2, BX1 - 0.2, RY0, RY0 + 0.04, 0, 1.15, p["wainscot"], c)
    wall_slab("Brief_WainN", BX0 + 0.2, BX1 - 0.2, RY1 - 0.04, RY1, 0, 1.15, p["wainscot"], c)
    wall_slab("Brief_WainW", BX0, BX0 + 0.06, RY0 + 0.1, RY1 - 0.1, 0, 1.15, p["wainscot"], c)
    wall_slab("Brief_WestLiner", BX0, BX0 + 0.08, RY0, RY1, 1.15, CEIL, p["wall"], c)
    wall_slab("Brief_BulkS", BX0, BX1, HY0, RY0 - WALL, 0, CEIL, p["iron"], c)
    wall_slab("Brief_BulkN", BX0, BX1, RY1 + WALL, HY1, 0, CEIL, p["iron"], c)
    tile_floor("Brief_Floor", BX0 + 0.05, BX1 - 0.05, RY0 + 0.05, RY1 - 0.05, p, c)
    wall_slab("Brief_Inlay", -10.2, -5.0, 7.55, 9.45, 0.035, 0.055, p["inlay"], c, 0.01)
    roof("Brief_Roof", BX0, BX1, RY0, RY1, p, c, rib_axis="x")

    # hallway roof + yellow runner
    roof("Hall_Roof", HX0, HX1, HY0, HY1, p, c, rib_axis="y")
    wall_slab("Hall_Stripe", -0.12, 0.12, 0.4, 14.0, 0.03, 0.05, p["stripe"], c, 0.005)

    # columns / brass caps
    for i, (x, y) in enumerate((
        (HX1 - 0.05, RY0 + 0.15), (HX1 - 0.05, RY1 - 0.15),
        (HX0 + 0.05, RY0 + 0.15), (HX0 + 0.05, RY1 - 0.15),
        (LX1 - 0.25, RY0 + 0.25), (LX1 - 0.25, RY1 - 0.25),
        (BX0 + 0.25, RY0 + 0.25), (BX0 + 0.25, RY1 - 0.25),
    )):
        column(f"Col_{i:02d}", (x, y), p, c)

    # wall lamps
    lamp("Lamp_LockN", (7.5, RY1 - 0.18, 2.55), math.pi, p, c)
    lamp("Lamp_LockS", (7.5, RY0 + 0.18, 2.55), 0.0, p, c)
    lamp("Lamp_LockE", (LX1 - 0.22, 8.5, 2.70), -math.pi / 2, p, c)
    lamp("Lamp_BriefN", (-7.5, RY1 - 0.18, 2.55), math.pi, p, c)
    lamp("Lamp_BriefS", (-7.5, RY0 + 0.18, 2.55), 0.0, p, c)
    lamp("Lamp_BriefW", (BX0 + 0.22, 8.5, 2.70), math.pi / 2, p, c)

    # --- Locker interior ---
    # side-wall lockers (north + south). South-west reserved for integrity pod.
    locker_bank("LockN", (7.6, RY1 - 0.28, 0), 6, math.pi, p, c, spacing=0.70)
    locker_bank("LockS", (9.15, RY0 + 0.28, 0), 4, 0.0, p, c, spacing=0.70)

    # suit alcoves on east wall
    suit_ys = (6.55, 7.85, 9.15, 10.45)
    fabrics = (p["sy"], p["sc"], p["sw"], p["so"])
    tags = ("Y", "C", "W", "O")
    for y, fab, tag in zip(suit_ys, fabrics, tags):
        alcove(f"Alcove_{tag}", (LX1 - 0.38, y, 0), p, c)
        adult_suit(f"PPE_{tag}", (LX1 - 0.52, y, 0), math.pi / 2, fab, p, c)

    bench("LockBench", (8.35, 8.50, 0.48), math.pi / 2, 2.6, p, c)

    # MOVE integrity / decon pod to SW of locker room (not with suits/bench)
    pod = bpy.data.objects.get("Assembled_SOT_Decon_Chamber")
    if pod and not _is_mine(pod):
        pod.hide_set(False)
        pod.hide_viewport = False
        pod.hide_render = False
        pod.location = (4.70, 5.62, 0.0)
        pod.rotation_euler = (0.0, 0.0, math.pi / 2)
    dl = bpy.data.objects.get("Light_Decon_Chamber")
    if dl:
        dl.location = (4.70, 5.62, 1.7)

    plant("LockPlant", (4.55, 11.85, 0), p, c)
    # shelf by door
    box("LockShelf", (4.55, 11.15, 1.15), (0.36, 0.70, 1.80), p["panel"], c, 0.015)
    box("LockToteA", (4.55, 11.00, 0.55), (0.28, 0.28, 0.22), p["teal"], c, 0.01)
    box("LockToteB", (4.55, 11.35, 0.55), (0.28, 0.28, 0.22), p["iron"], c, 0.01)

    # --- Briefing interior ---
    # cyan board
    box("Brief_Frame", (-11.55, 8.50, 2.15), (0.16, 5.10, 2.20), p["teal"], c, 0.02)
    box("Brief_Inner", (-11.46, 8.50, 2.15), (0.05, 4.70, 1.85), p["iron"], c, 0.01)
    scr = box("Brief_Glass", (-11.42, 8.50, 2.15), (0.03, 4.50, 1.70), p["screen"], c, 0.0)
    uv_cube_project(scr, 0.22)
    lectern("Brief_Lectern", (-9.55, 8.50, 0.55), p, c)
    # 2x2 benches facing west (toward screen)
    bench("BriefBench_NE", (-6.15, 10.15, 0.48), math.pi / 2, 2.35, p, c)
    bench("BriefBench_SE", (-6.15, 6.85, 0.48), math.pi / 2, 2.35, p, c)
    bench("BriefBench_NW", (-7.85, 10.15, 0.48), math.pi / 2, 2.35, p, c)
    bench("BriefBench_SW", (-7.85, 6.85, 0.48), math.pi / 2, 2.35, p, c)

    # signs — 3D plates, not pirate boards. Photos used only where full-bleed.
    box("Sign_Safety", (-11.42, 11.55, 1.85), (0.04, 0.55, 0.70), p["teal"], c, 0.01)
    box("Sign_SafetyPlusH", (-11.39, 11.55, 2.00), (0.03, 0.28, 0.08), p["paper"], c, 0.004)
    box("Sign_SafetyPlusV", (-11.39, 11.55, 2.00), (0.03, 0.08, 0.28), p["paper"], c, 0.004)
    box("Sign_Work", (-11.42, 5.45, 1.90), (0.04, 0.42, 0.78), p["panel"], c, 0.01)
    box("Sign_WorkBar", (-11.39, 5.45, 1.90), (0.03, 0.28, 0.04), p["teal"], c, 0.004)

    # memo board (metal, papers) north wall
    box("Memo_Back", (-7.4, RY1 - 0.08, 1.85), (1.55, 0.05, 1.05), p["iron"], c, 0.012)
    box("Memo_P0", (-7.75, RY1 - 0.11, 2.05), (0.38, 0.02, 0.50), p["paper"], c, 0.004)
    box("Memo_P1", (-7.25, RY1 - 0.11, 1.95), (0.34, 0.02, 0.42), p["paper"], c, 0.004)
    box("Memo_P2", (-6.85, RY1 - 0.11, 2.10), (0.30, 0.02, 0.38), p["teal"], c, 0.004)

    plant("BriefPlant", (-4.85, 11.95, 0), p, c)

    # hallway signs on partitions
    box("HallSign_Auth", (HX0 + 0.06, 6.35, 1.85), (0.04, 0.70, 0.80), p["teal"], c, 0.01)
    box("HallSign_Lvl", (HX1 - 0.06, 6.35, 1.85), (0.04, 0.70, 0.80), p["teal"], c, 0.01)
    # far door plus
    box("HallEndPlusH", (0.0, HY1 - 0.42, 2.55), (0.28, 0.06, 0.08), p["cool"], c, 0.004)
    box("HallEndPlusV", (0.0, HY1 - 0.42, 2.55), (0.08, 0.06, 0.28), p["cool"], c, 0.004)

    # lighting — cool lab fill, warm brass accents
    add_area_light("LabLight_Lock", (8.2, 8.5, CEIL - 0.28), (4.5, 4.0), 450, (0.85, 0.92, 1.0), c)
    add_area_light("LabLight_Brief", (-7.6, 8.5, CEIL - 0.28), (4.5, 4.0), 480, (0.85, 0.92, 1.0), c)
    add_area_light("LabLight_Hall", (0.0, 7.2, CEIL - 0.28), (2.2, 8.0), 380, (0.88, 0.93, 1.0), c)
    # point warms at lectern / suits
    for nm, loc, e in (
        ("LabWarm_Suits", (10.2, 8.5, 2.6), 80),
        ("LabWarm_Lectern", (-9.4, 8.5, 2.4), 55),
        ("LabWarm_HallN", (0.0, 11.0, 2.6), 40),
        ("LabWarm_HallS", (0.0, 3.6, 2.6), 40),
    ):
        d = bpy.data.lights.new(nm, "POINT")
        d.energy = e
        d.color = (1.0, 0.82, 0.58)
        o = bpy.data.objects.new(nm, d)
        o.location = loc
        c.objects.link(o)

    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = None
    for n in world.node_tree.nodes:
        if n.type == "BACKGROUND":
            bg = n
            break
    if bg:
        bg.inputs[0].default_value = (0.42, 0.50, 0.56, 1.0)
        bg.inputs[1].default_value = 0.55

    scene = bpy.context.scene
    if hasattr(scene.eevee, "use_bloom"):
        scene.eevee.use_bloom = True
        if hasattr(scene.eevee, "bloom_intensity"):
            scene.eevee.bloom_intensity = 0.12
    if hasattr(scene.eevee, "use_gtao"):
        scene.eevee.use_gtao = True
    eng = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in dir(bpy.types) or True else "BLENDER_EEVEE"
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception:
        scene.render.engine = "BLENDER_EEVEE"

    # bump existing fill lights if present
    for nm, energy in (
        ("Light_Locker_Ambient", 220),
        ("Light_Briefing_Ambient", 240),
        ("Light_Hero_Suits_Spot", 180),
        ("Light_Screen_Glow", 90),
        ("Light_Briefing_Spot", 160),
    ):
        ob = bpy.data.objects.get(nm)
        if ob and ob.type == "LIGHT":
            ob.data.energy = energy
            ob.data.color = (0.86, 0.92, 1.0)

    bpy.context.view_layer.update()
    return {"ok": True, "objects": len(c.objects)}


result = build()
