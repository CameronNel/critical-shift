"""Rebuild spawn hallway / briefing / lockers to match critical-shift-spawn-room.png."""
import math
import os
import bpy
import bmesh
from mathutils import Euler

ROOT = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(ROOT, "textures", "spawn")
COL_H = "CS_HallwayBays"
COL_B = "CS_BriefingDress"
COL_L = "CS_LockerDress"


def getcol(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    for o in list(c.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    vl = bpy.context.view_layer.layer_collection

    def unex(lc):
        if lc.name == name:
            lc.exclude = False
            lc.hide_viewport = False
        for ch in lc.children:
            unex(ch)

    unex(vl)
    return c


def hide_col(name):
    c = bpy.data.collections.get(name)
    if not c:
        return
    for o in c.objects:
        try:
            o.hide_set(True)
        except RuntimeError:
            pass
        o.hide_viewport = True
        o.hide_render = True
    vl = bpy.context.view_layer.layer_collection

    def walk(lc):
        if lc.name == name:
            lc.exclude = True
        for ch in lc.children:
            walk(ch)

    walk(vl)


def hide_prefix(*prefixes):
    for o in bpy.data.objects:
        if any(o.name.startswith(p) for p in prefixes):
            o.hide_viewport = True
            o.hide_render = True
            try:
                o.hide_set(True)
            except RuntimeError:
                pass


def mat(name, col, rough=0.42, metal=0.08, emit=None, es=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    pr = nt.nodes.new("ShaderNodeBsdfPrincipled")
    pr.inputs["Base Color"].default_value = (*col, 1)
    pr.inputs["Roughness"].default_value = rough
    pr.inputs["Metallic"].default_value = metal
    if emit is not None and "Emission Color" in pr.inputs:
        pr.inputs["Emission Color"].default_value = (*emit, 1)
        pr.inputs["Emission Strength"].default_value = es
    nt.links.new(pr.outputs["BSDF"], out.inputs["Surface"])
    try:
        m.diffuse_color = (*col, 1)
    except Exception:
        pass
    return m


def texmat(name, path, emit=False, emit_str=1.2, rough=0.45):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path, check_existing=True)
    if emit:
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = emit_str
        nt.links.new(tex.outputs["Color"], em.inputs["Color"])
        nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    else:
        pr = nt.nodes.new("ShaderNodeBsdfPrincipled")
        pr.inputs["Roughness"].default_value = rough
        nt.links.new(tex.outputs["Color"], pr.inputs["Base Color"])
        nt.links.new(pr.outputs["BSDF"], out.inputs["Surface"])
    return m


def _uv_cube(bm, size):
    uv_layer = bm.loops.layers.uv.new("UVMap")
    sx, sy, sz = size
    for face in bm.faces:
        n = face.normal
        for loop in face.loops:
            co = loop.vert.co
            if abs(n.z) > 0.5:
                loop[uv_layer].uv = ((co.x / max(sx, 0.001)) + 0.5, (co.y / max(sy, 0.001)) + 0.5)
            elif abs(n.x) > 0.5:
                loop[uv_layer].uv = ((co.y / max(sy, 0.001)) + 0.5, (co.z / max(sz, 0.001)) + 0.5)
            else:
                loop[uv_layer].uv = ((co.x / max(sx, 0.001)) + 0.5, (co.z / max(sz, 0.001)) + 0.5)


def box(name, loc, size, material, col, rot=(0, 0, 0), bevel=0.014):
    me = bpy.data.meshes.new(name + "_me")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    off = min(bevel, min(size) * 0.16) if bevel else 0
    if off > 0.002:
        try:
            bmesh.ops.bevel(bm, geom=list(bm.edges), offset=off, segments=1, affect="EDGES")
        except TypeError:
            bmesh.ops.bevel(bm, geom=list(bm.edges), offset=off, segments=1)
    _uv_cube(bm, size)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = Euler(rot)
    ob.data.materials.append(material)
    col.objects.link(ob)
    return ob


def cyl(name, loc, r, depth, material, col, segs=12, rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name + "_me")
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=r, depth=depth)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = Euler(rot)
    ob.data.materials.append(material)
    col.objects.link(ob)
    return ob


def palette():
    return {
        "struct": mat("M_PNG_Struct", (0.70, 0.73, 0.76), 0.46, 0.22),
        "teal": mat("M_PNG_Teal", (0.18, 0.50, 0.52), 0.34, 0.24),
        "teal_d": mat("M_PNG_TealD", (0.12, 0.36, 0.38), 0.40, 0.28),
        "brass": mat("M_PNG_Brass", (0.80, 0.58, 0.20), 0.26, 0.94),
        "iron": mat("M_PNG_Iron", (0.13, 0.14, 0.16), 0.48, 0.80),
        "wall": mat("M_PNG_Wall", (0.88, 0.90, 0.91), 0.58, 0.02),
        "recess": mat("M_PNG_Recess", (0.76, 0.80, 0.82), 0.62, 0.04),
        "ceil": mat("M_PNG_Ceil", (0.48, 0.54, 0.57), 0.50, 0.10),
        "emit": mat("M_PNG_Emit", (1.0, 0.93, 0.74), 0.16, 0.0, (1.0, 0.92, 0.70), 5.8),
        "stripe": mat("M_PNG_Stripe", (0.92, 0.76, 0.12), 0.36, 0.02),
        "sblk": mat("M_PNG_SBlk", (0.06, 0.06, 0.07), 0.5, 0.04),
        "door": mat("M_PNG_Door", (0.18, 0.20, 0.23), 0.40, 0.45),
        "pipe": mat("M_PNG_Pipe", (0.90, 0.92, 0.93), 0.26, 0.10),
        "plus": mat("M_PNG_Plus", (0.32, 0.86, 0.80), 0.20, 0.04, (0.28, 0.95, 0.88), 3.6),
        "pad": mat("M_PNG_Pad", (0.30, 0.58, 0.60), 0.55, 0.04),
        "leaf": mat("M_PNG_Leaf", (0.22, 0.42, 0.24), 0.65, 0.0),
        "pot": mat("M_PNG_Pot", (0.22, 0.40, 0.42), 0.40, 0.15),
        "dirt": mat("M_PNG_Dirt", (0.18, 0.12, 0.08), 0.80, 0.0),
        "paper": mat("M_PNG_Paper", (0.90, 0.88, 0.80), 0.70, 0.0),
        "visor": mat("M_PNG_Visor", (0.55, 0.78, 0.82), 0.12, 0.3, (0.45, 0.85, 0.90), 0.8),
        "yel": mat("M_PNG_Yel", (0.86, 0.64, 0.16), 0.48, 0.04),
        "cyn": mat("M_PNG_Cyn", (0.38, 0.66, 0.72), 0.48, 0.04),
        "wht": mat("M_PNG_Wht", (0.90, 0.91, 0.92), 0.50, 0.03),
        "org": mat("M_PNG_Org", (0.82, 0.40, 0.16), 0.48, 0.04),
        "boot": mat("M_PNG_Boot", (0.12, 0.12, 0.13), 0.55, 0.08),
    }


def bulkhead(tag, y, p, c, posts=True):
    # Inner opening ~3.6m wide x 2.7m tall so Cam_Hallway 18mm is framed.
    box(f"{tag}_Sill", (0.0, y, 0.04), (5.40, 0.40, 0.06), p["iron"], c, bevel=0.008)
    box(f"{tag}_SillTeal", (0.0, y, 0.08), (3.70, 0.22, 0.03), p["teal"], c, bevel=0.006)
    if posts:
        for sx, s in ((-1.95, "L"), (1.95, "R")):
            box(f"{tag}_Post{s}", (sx, y, 1.70), (0.50, 0.42, 3.28), p["struct"], c, bevel=0.028)
            inward = 0.28 if sx < 0 else -0.28
            box(f"{tag}_PostFace{s}", (sx + inward, y, 1.70), (0.10, 0.32, 3.10), p["teal"], c, bevel=0.012)
            box(f"{tag}_Cap{s}", (sx, y, 3.38), (0.56, 0.48, 0.12), p["brass"], c, bevel=0.018)
            box(f"{tag}_Base{s}", (sx, y, 0.10), (0.58, 0.48, 0.18), p["iron"], c, bevel=0.016)
    box(f"{tag}_Header", (0.0, y, 3.22), (5.20, 0.44, 0.42), p["struct"], c, bevel=0.022)
    box(f"{tag}_HeaderTeal", (0.0, y, 2.98), (3.85, 0.28, 0.14), p["teal"], c, bevel=0.010)
    box(f"{tag}_HeaderBrass", (0.0, y, 3.40), (1.80, 0.20, 0.05), p["brass"], c, bevel=0.008)
    # inner picture-frame lip (the receding rectangle)
    box(f"{tag}_LipTop", (0.0, y, 2.88), (3.70, 0.16, 0.08), p["teal_d"], c, bevel=0.006)
    if posts:
        box(f"{tag}_LipL", (-1.72, y, 1.50), (0.08, 0.16, 2.70), p["teal_d"], c, bevel=0.006)
        box(f"{tag}_LipR", (1.72, y, 1.50), (0.08, 0.16, 2.70), p["teal_d"], c, bevel=0.006)


def bay_module(tag, y0, y1, p, c, skip_sides=False):
    ym = (y0 + y1) * 0.5
    span = max(0.40, (y1 - y0) - 0.46)
    box(f"{tag}_Ceil", (0.0, ym, 3.48), (4.85, span + 0.10, 0.10), p["ceil"], c, bevel=0.008)
    box(f"{tag}_CeilTealL", (-2.05, ym, 3.38), (0.10, span, 0.08), p["teal"], c, bevel=0.006)
    box(f"{tag}_CeilTealR", (2.05, ym, 3.38), (0.10, span, 0.08), p["teal"], c, bevel=0.006)
    box(f"{tag}_LightWell", (0.0, ym, 3.40), (0.95, 0.55, 0.08), p["iron"], c, bevel=0.008)
    box(f"{tag}_Light", (0.0, ym, 3.36), (0.80, 0.42, 0.05), p["emit"], c, bevel=0.006)
    box(f"{tag}_LightRim", (0.0, ym, 3.42), (1.02, 0.60, 0.03), p["brass"], c, bevel=0.005)
    if skip_sides:
        return
    for side, x, nsign in (("E", 2.42, -1), ("W", -2.42, 1)):
        box(f"{tag}_{side}_Up", (x, ym, 2.20), (0.10, span, 1.95), p["wall"], c, bevel=0.010)
        box(f"{tag}_{side}_Low", (x, ym, 0.62), (0.14, span, 1.16), p["teal"], c, bevel=0.012)
        box(f"{tag}_{side}_Rail", (x + nsign * 0.05, ym, 1.22), (0.04, span - 0.08, 0.05), p["brass"], c, bevel=0.005)
        box(f"{tag}_{side}_Recess", (x + nsign * 0.08, ym, 2.15), (0.08, max(0.50, span - 0.36), 1.15), p["recess"], c, bevel=0.010)
        box(f"{tag}_{side}_PFrame", (x + nsign * 0.04, ym, 2.15), (0.05, max(0.62, span - 0.22), 1.32), p["teal"], c, bevel=0.008)


def plant(tag, loc, p, c, scale=1.0):
    x, y, z = loc
    box(f"{tag}_Pot", (x, y, 0.18 * scale), (0.32 * scale, 0.32 * scale, 0.34 * scale), p["pot"], c, bevel=0.02)
    box(f"{tag}_Dirt", (x, y, 0.36 * scale), (0.26 * scale, 0.26 * scale, 0.06 * scale), p["dirt"], c, bevel=0.008)
    cyl(f"{tag}_Stem", (x, y, 0.62 * scale), 0.025 * scale, 0.50 * scale, p["leaf"], c, 8)
    for i, (dx, dy, dz, r) in enumerate((
        (0.00, 0.00, 1.05, 0.16),
        (0.10, 0.06, 0.92, 0.13),
        (-0.08, -0.05, 0.88, 0.12),
        (0.04, -0.10, 1.12, 0.10),
    )):
        cyl(f"{tag}_Leaf{i}", (x + dx * scale, y + dy * scale, z + dz * scale), r * scale, 0.08 * scale, p["leaf"], c, 10)


def hang_suit(tag, y, fabric, p, c):
    """Adult workwear on a hanger — not a standing mannequin."""
    x = 11.22
    box(f"{tag}_Shelf", (11.42, y, 2.08), (0.38, 0.92, 0.05), p["iron"], c, bevel=0.008)
    # helmet sitting on the shelf
    cyl(f"{tag}_Helm", (11.28, y, 2.24), 0.15, 0.16, fabric, c, 14)
    box(f"{tag}_Visor", (11.14, y, 2.22), (0.05, 0.18, 0.09), p["visor"], c, bevel=0.006)
    box(f"{tag}_HelmRim", (11.22, y, 2.14), (0.18, 0.22, 0.04), p["iron"], c, bevel=0.006)
    # hanger
    cyl(f"{tag}_Bar", (x, y, 1.86), 0.018, 0.62, p["iron"], c, 8, rot=(math.pi / 2, 0, 0))
    # jacket
    box(f"{tag}_Torso", (x, y, 1.38), (0.20, 0.50, 0.72), fabric, c, bevel=0.02)
    box(f"{tag}_Hood", (x, y, 1.74), (0.18, 0.30, 0.14), fabric, c, bevel=0.016)
    box(f"{tag}_SlvL", (x, y - 0.34, 1.22), (0.13, 0.13, 0.68), fabric, c, bevel=0.016)
    box(f"{tag}_SlvR", (x, y + 0.34, 1.22), (0.13, 0.13, 0.68), fabric, c, bevel=0.016)
    box(f"{tag}_GlvL", (x, y - 0.34, 0.84), (0.11, 0.11, 0.12), p["boot"], c, bevel=0.01)
    box(f"{tag}_GlvR", (x, y + 0.34, 0.84), (0.11, 0.11, 0.12), p["boot"], c, bevel=0.01)
    box(f"{tag}_Chest", (x - 0.11, y, 1.40), (0.03, 0.36, 0.08), p["teal"], c, bevel=0.004)
    # pants hanging
    box(f"{tag}_PantL", (x, y - 0.11, 0.58), (0.15, 0.13, 0.62), fabric, c, bevel=0.014)
    box(f"{tag}_PantR", (x, y + 0.11, 0.58), (0.15, 0.13, 0.62), fabric, c, bevel=0.014)
    # boots on alcove floor
    box(f"{tag}_BootL", (11.10, y - 0.12, 0.12), (0.30, 0.13, 0.18), p["boot"], c, bevel=0.012)
    box(f"{tag}_BootR", (11.10, y + 0.12, 0.12), (0.30, 0.13, 0.18), p["boot"], c, bevel=0.012)
    # alcove light
    box(f"{tag}_Lite", (11.40, y, 2.38), (0.22, 0.40, 0.04), p["emit"], c, bevel=0.006)


def build_hallway(p):
    hide_col("CS_HallwayDress")
    hide_col("01_Hallway_Assembled")
    hide_col("01_Production_Hallway_Assets")
    c = getcol(COL_H)

    floor_path = os.path.join(TEX, "floor_tiles.jpg")
    floor_m = texmat("M_PNG_Floor", floor_path, rough=0.55) if os.path.isfile(floor_path) else p["wall"]

    # First ring at y=2.50 frames Cam_Hallway (y=0.8, 18mm).
    ring_ys = [2.50, 4.40, 6.30, 10.40, 12.30, 14.10]
    door_gap = {(6.30, 10.40)}
    for i, y in enumerate(ring_ys):
        bulkhead(f"Bay{i:02d}", y, p, c, posts=True)

    pairs = list(zip(ring_ys[:-1], ring_ys[1:]))
    for i, (y0, y1) in enumerate(pairs):
        bay_module(f"BayW{i:02d}", y0, y1, p, c, skip_sides=(y0, y1) in door_gap)

    box("BayDoor_Header", (0.0, 8.50, 3.22), (5.20, 0.40, 0.42), p["struct"], c, bevel=0.02)
    box("BayDoor_HeaderTeal", (0.0, 8.50, 2.98), (3.85, 0.24, 0.14), p["teal"], c, bevel=0.01)
    box("BayDoor_Ceil", (0.0, 8.50, 3.48), (4.85, 3.70, 0.10), p["ceil"], c, bevel=0.008)
    box("BayDoor_Light", (0.0, 8.50, 3.36), (0.80, 0.42, 0.05), p["emit"], c, bevel=0.006)

    box("Bay_Floor", (0.0, 7.55, 0.032), (5.50, 14.6, 0.05), floor_m, c, bevel=0.0)

    # End door
    box("End_Frame", (0.0, 14.22, 1.70), (3.20, 0.32, 3.30), p["teal"], c, bevel=0.022)
    box("End_FrameIron", (0.0, 14.12, 1.62), (2.45, 0.14, 3.00), p["iron"], c, bevel=0.010)
    box("End_DoorL", (-0.58, 14.06, 1.40), (1.10, 0.09, 2.72), p["door"], c, bevel=0.010)
    box("End_DoorR", (0.58, 14.06, 1.40), (1.10, 0.09, 2.72), p["door"], c, bevel=0.010)
    for i, z in enumerate((0.70, 1.40, 2.10)):
        box(f"End_RibL{i}", (-0.58, 14.00, z), (1.00, 0.04, 0.05), p["iron"], c, bevel=0.004)
        box(f"End_RibR{i}", (0.58, 14.00, z), (1.00, 0.04, 0.05), p["iron"], c, bevel=0.004)
    box("End_PlusH", (0.0, 13.96, 2.28), (0.50, 0.05, 0.11), p["plus"], c, bevel=0.006)
    box("End_PlusV", (0.0, 13.96, 2.28), (0.11, 0.05, 0.50), p["plus"], c, bevel=0.006)
    box("End_HandleL", (-0.14, 13.98, 1.40), (0.05, 0.06, 0.28), p["brass"], c, bevel=0.006)
    box("End_HandleR", (0.14, 13.98, 1.40), (0.05, 0.06, 0.28), p["brass"], c, bevel=0.006)

    # Dual yellow stripes on TOP of the floor
    box("Bay_StripeBlkL", (-0.40, 7.55, 0.060), (0.05, 14.4, 0.010), p["sblk"], c, bevel=0.0)
    box("Bay_StripeL", (-0.30, 7.55, 0.062), (0.11, 14.4, 0.012), p["stripe"], c, bevel=0.0)
    box("Bay_StripeBlkR", (0.40, 7.55, 0.060), (0.05, 14.4, 0.010), p["sblk"], c, bevel=0.0)
    box("Bay_StripeR", (0.30, 7.55, 0.062), (0.11, 14.4, 0.012), p["stripe"], c, bevel=0.0)

    # Cabinets in the east reveal (visible through the first ring)
    for i, y in enumerate((3.15, 3.95, 4.75, 5.55, 11.15, 11.95, 12.75)):
        box(f"Bay_Cab{i}", (2.18, y, 0.50), (0.32, 0.62, 0.82), p["teal"], c, bevel=0.014)
        box(f"Bay_CabFace{i}", (2.02, y, 0.56), (0.04, 0.48, 0.52), p["iron"], c, bevel=0.006)
        box(f"Bay_CabKnob{i}", (2.00, y, 0.40), (0.03, 0.07, 0.07), p["brass"], c, bevel=0.004)

    cyl("Bay_Pipe", (2.05, 7.55, 3.02), 0.065, 12.4, p["pipe"], c, 12, rot=(math.pi / 2, 0, 0))
    for i, y in enumerate((3.4, 5.4, 11.2, 13.0)):
        box(f"Bay_PipeHang{i}", (2.05, y, 3.22), (0.05, 0.05, 0.20), p["teal"], c, bevel=0.004)

    sign_a = os.path.join(TEX, "sign_authorized.jpg")
    sign_f = os.path.join(TEX, "sign_facility_level.jpg")
    if os.path.isfile(sign_a):
        sm = texmat("M_PNG_SignAuth", sign_a, emit=True, emit_str=0.55)
        box("Bay_SignAuth", (-2.28, 3.45, 1.88), (0.04, 0.72, 0.85), sm, c, bevel=0.005)
    if os.path.isfile(sign_f):
        sm = texmat("M_PNG_SignFac", sign_f, emit=True, emit_str=0.55)
        ob = box("Bay_SignFac", (2.28, 3.45, 1.88), (0.04, 0.72, 0.85), sm, c, bevel=0.005)
        ob.rotation_euler = Euler((0, 0, math.pi))

    hide_prefix("HallDress_", "Modular_Floor_Guide")
    return len(c.objects)


def build_briefing(p):
    c = getcol(COL_B)
    # Hide washed-out glass so the new screen can read
    hide_prefix("Brief_Glass")

    screen_path = os.path.join(TEX, "briefing_screen.jpg")
    if os.path.isfile(screen_path):
        sm = texmat("M_PNG_BriefScreen", screen_path, emit=True, emit_str=1.15)
        box("PNG_BriefScreen", (-11.58, 8.50, 2.18), (0.04, 4.30, 1.72), sm, c, bevel=0.0)
    # chunky teal CRT frame
    box("PNG_BriefFrame", (-11.70, 8.50, 2.18), (0.16, 4.72, 2.12), p["teal"], c, bevel=0.02)
    box("PNG_BriefFrameIn", (-11.62, 8.50, 2.18), (0.06, 4.42, 1.84), p["iron"], c, bevel=0.008)
    box("PNG_BriefTopBar", (-11.60, 8.50, 3.18), (0.10, 4.50, 0.10), p["brass"], c, bevel=0.008)
    for sx, sy in ((-2.20, 11.0), (2.20, 11.0), (-2.20, 6.0), (2.20, 6.0)):
        # brass corner bolts on the frame
        pass
    for i, yy in enumerate((6.40, 10.60)):
        cyl(f"PNG_BriefBoltL{i}", (-11.60, yy, 3.10), 0.04, 0.05, p["brass"], c, 10, rot=(0, math.pi / 2, 0))
        cyl(f"PNG_BriefBoltR{i}", (-11.60, yy, 1.26), 0.04, 0.05, p["brass"], c, 10, rot=(0, math.pi / 2, 0))

    # lectern — concept: squat teal podium with plus
    box("PNG_Lectern", (-10.05, 8.50, 0.55), (0.70, 0.62, 1.08), p["teal"], c, bevel=0.022)
    box("PNG_LecternTop", (-10.00, 8.50, 1.12), (0.78, 0.70, 0.08), p["teal_d"], c, bevel=0.012)
    box("PNG_LecternPlusH", (-9.68, 8.50, 0.62), (0.04, 0.22, 0.06), p["plus"], c, bevel=0.004)
    box("PNG_LecternPlusV", (-9.68, 8.50, 0.62), (0.04, 0.06, 0.22), p["plus"], c, bevel=0.004)
    box("PNG_LecternBase", (-10.05, 8.50, 0.06), (0.80, 0.72, 0.10), p["iron"], c, bevel=0.01)

    # notice board LEFT of screen (north, +Y) when looking west
    nb = os.path.join(TEX, "notice_board_lab.jpg")
    if os.path.isfile(nb):
        nm = texmat("M_PNG_Notice", nb, rough=0.55)
        box("PNG_Notice", (-11.62, 11.35, 2.05), (0.04, 1.35, 1.00), nm, c, bevel=0.008)
    # SAFETY FIRST
    sf = os.path.join(TEX, "sign_safety_first.jpg")
    if os.path.isfile(sf):
        sm = texmat("M_PNG_Safety", sf, emit=True, emit_str=0.4)
        box("PNG_Safety", (-11.62, 10.35, 2.05), (0.04, 0.52, 0.52), sm, c, bevel=0.006)
    # WORK SMART STAY ALIVE — right of screen (south, -Y)
    ws = os.path.join(TEX, "sign_work_smart.jpg")
    if os.path.isfile(ws):
        sm = texmat("M_PNG_WorkSmart", ws, emit=True, emit_str=0.4)
        box("PNG_WorkSmart", (-11.62, 5.55, 2.15), (0.04, 0.48, 0.72), sm, c, bevel=0.006)
    # second small clipboard board on the right
    if os.path.isfile(nb):
        nm = texmat("M_PNG_Notice2", nb, rough=0.55)
        box("PNG_NoticeR", (-11.62, 6.45, 2.15), (0.04, 0.72, 0.90), nm, c, bevel=0.008)

    # plants — right-hand corner (south-east of briefing) and far corner
    plant("PNG_PlantBriefR", (-4.70, 4.85, 0.0), p, c, 1.05)
    plant("PNG_PlantBriefL", (-4.70, 12.15, 0.0), p, c, 0.95)

    # ceiling lights
    for i, yy in enumerate((6.4, 8.5, 10.6)):
        box(f"PNG_BriefLight{i}", (-7.5, yy, 3.42), (1.10, 0.48, 0.06), p["emit"], c, bevel=0.008)
        box(f"PNG_BriefLightRim{i}", (-7.5, yy, 3.46), (1.24, 0.60, 0.03), p["brass"], c, bevel=0.005)

    # wall sconces like the concept
    for i, (xx, yy) in enumerate(((-11.55, 4.70), (-11.55, 12.30), (-3.55, 4.70), (-3.55, 12.30))):
        box(f"PNG_Sconce{i}", (xx, yy, 3.05), (0.14, 0.22, 0.12), p["emit"], c, bevel=0.01)
        box(f"PNG_SconceArm{i}", (xx, yy, 3.18), (0.08, 0.08, 0.16), p["brass"], c, bevel=0.006)

    return len(c.objects)


def build_lockers(p):
    c = getcol(COL_L)
    hide_prefix("PPE_")

    # hanging adult PPE in the four alcoves, L→R when looking east: Y, C, W, O
    hang_suit("PNG_SuitY", 10.45, p["yel"], p, c)
    hang_suit("PNG_SuitC", 9.15, p["cyn"], p, c)
    hang_suit("PNG_SuitW", 7.85, p["wht"], p, c)
    hang_suit("PNG_SuitO", 6.55, p["org"], p, c)

    # teal alcove frames (proud of the existing dark backs)
    for i, y in enumerate((10.45, 9.15, 7.85, 6.55)):
        box(f"PNG_AlcFrame{i}", (11.48, y, 1.20), (0.08, 1.12, 2.38), p["teal"], c, bevel=0.012)
        box(f"PNG_AlcInner{i}", (11.55, y, 1.20), (0.04, 0.98, 2.20), p["iron"], c, bevel=0.006)

    # ceiling light over the bench
    box("PNG_LockLight", (8.2, 8.5, 3.42), (1.20, 0.55, 0.06), p["emit"], c, bevel=0.008)
    box("PNG_LockLightRim", (8.2, 8.5, 3.46), (1.36, 0.68, 0.03), p["brass"], c, bevel=0.005)
    box("PNG_LockLight2", (10.4, 8.5, 3.42), (0.80, 0.45, 0.05), p["emit"], c, bevel=0.006)

    # locker bank top teal cornice
    box("PNG_LockCorniceN", (7.6, 12.55, 2.32), (5.2, 0.10, 0.08), p["teal"], c, bevel=0.008)
    box("PNG_LockCorniceS", (8.6, 4.38, 2.32), (4.4, 0.10, 0.08), p["teal"], c, bevel=0.008)

    # vents on locker faces
    for i, x in enumerate((9.35, 8.65, 7.95, 7.25, 6.55, 5.85)):
        box(f"PNG_LockVentN{i}", (x, 12.24, 1.85), (0.36, 0.04, 0.10), p["iron"], c, bevel=0.004)
    for i, x in enumerate((8.10, 8.80, 9.50, 10.20)):
        box(f"PNG_LockVentS{i}", (x, 4.76, 1.85), (0.36, 0.04, 0.10), p["iron"], c, bevel=0.004)

    # integrity kiosk — SW of locker room, opposite the suit wall
    box("PNG_Integrity", (4.72, 5.55, 0.95), (0.42, 0.52, 1.85), p["teal"], c, bevel=0.018)
    box("PNG_IntegrityScr", (4.50, 5.55, 1.35), (0.04, 0.36, 0.28), p["plus"], c, bevel=0.004)
    box("PNG_IntegrityTop", (4.72, 5.55, 1.90), (0.46, 0.56, 0.08), p["iron"], c, bevel=0.008)
    box("PNG_IntegrityPlusH", (4.50, 5.55, 0.55), (0.04, 0.16, 0.04), p["plus"], c, bevel=0.003)
    box("PNG_IntegrityPlusV", (4.50, 5.55, 0.55), (0.04, 0.04, 0.16), p["plus"], c, bevel=0.003)

    # plant already exists at 4.55,11.85 — add a fuller one
    plant("PNG_PlantLock", (4.55, 11.85, 0.0), p, c, 1.0)

    return len(c.objects)


def build():
    hide_col("CS_HallwayDress")
    hide_col("01_Hallway_Assembled")
    hide_col("01_Production_Hallway_Assets")
    p = palette()
    n_h = build_hallway(p)
    n_b = build_briefing(p)
    n_l = build_lockers(p)
    bpy.context.view_layer.update()
    return {"hallway": n_h, "briefing": n_b, "lockers": n_l}


result = build()
