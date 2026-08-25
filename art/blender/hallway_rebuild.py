"""Rebuild connecting hallway as repeating bulkhead bays matching concept panel 5."""
import math
import os
import bpy
import bmesh
from mathutils import Euler, Vector

COL = "CS_HallwayBays"
TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures", "spawn")
HALL_TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures", "hallway")


def getcol():
    c = bpy.data.collections.get(COL)
    if c is None:
        c = bpy.data.collections.new(COL)
        bpy.context.scene.collection.children.link(c)
    for o in list(c.objects):
        bpy.data.objects.remove(o, do_unlink=True)
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


def texmat(name, path, emit=False, rough=0.45, uv_scale=(1, 1)):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path, check_existing=True)
    tex.interpolation = "Closest" if emit else "Linear"
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (uv_scale[0], uv_scale[1], 1)
    coord = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(coord.outputs["UV"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
    if emit:
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = 1.6
        nt.links.new(tex.outputs["Color"], em.inputs["Color"])
        pr = nt.nodes.new("ShaderNodeBsdfPrincipled")
        pr.inputs["Roughness"].default_value = 0.28
        nt.links.new(tex.outputs["Color"], pr.inputs["Base Color"])
        add = nt.nodes.new("ShaderNodeAddShader")
        nt.links.new(pr.outputs["BSDF"], add.inputs[0])
        nt.links.new(em.outputs["Emission"], add.inputs[1])
        nt.links.new(add.outputs["Shader"], out.inputs["Surface"])
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


def box(name, loc, size, material, col, rot=(0, 0, 0), bevel=0.016):
    me = bpy.data.meshes.new(name + "_me")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    off = min(bevel, min(size) * 0.18)
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


def cyl(name, loc, r, depth, material, col, segs=14, rot=(0, 0, 0)):
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


def bulkhead(tag, y, p, c, posts=True, door=False):
    """One receding portal ring — the silhouette of concept panel 5."""
    # chunky floor threshold
    box(f"{tag}_Sill", (0.0, y, 0.07), (5.70, 0.46, 0.12), p["iron"], c, bevel=0.02)
    box(f"{tag}_SillTeal", (0.0, y, 0.14), (5.20, 0.22, 0.04), p["teal"], c, bevel=0.01)
    if posts:
        for sx, s in ((-2.52, "L"), (2.52, "R")):
            # main structural post (proud of the wall)
            box(f"{tag}_Post{s}", (sx, y, 1.78), (0.52, 0.46, 3.42), p["struct"], c, bevel=0.03)
            # teal inner face so the ring reads as a painted portal
            inward = 0.28 if sx < 0 else -0.28
            box(f"{tag}_PostFace{s}", (sx + inward, y, 1.78), (0.08, 0.36, 3.22), p["teal"], c, bevel=0.012)
            # outer dark iron edge
            outward = -0.24 if sx < 0 else 0.24
            box(f"{tag}_PostOut{s}", (sx + outward, y, 1.78), (0.06, 0.50, 3.42), p["iron"], c, bevel=0.008)
            # brass capital
            box(f"{tag}_Cap{s}", (sx, y, 3.46), (0.58, 0.52, 0.12), p["brass"], c, bevel=0.02)
            cyl(f"{tag}_CapKnob{s}", (sx, y, 3.54), 0.12, 0.08, p["brass"], c, 12)
            # iron plinth
            box(f"{tag}_Base{s}", (sx, y, 0.12), (0.62, 0.54, 0.22), p["iron"], c, bevel=0.02)
            box(f"{tag}_BaseTeal{s}", (sx, y, 0.24), (0.50, 0.40, 0.06), p["teal"], c, bevel=0.01)
    # header beam spanning the ring
    box(f"{tag}_Header", (0.0, y, 3.40), (5.80, 0.48, 0.38), p["struct"], c, bevel=0.025)
    box(f"{tag}_HeaderTeal", (0.0, y, 3.20), (5.10, 0.28, 0.12), p["teal"], c, bevel=0.012)
    box(f"{tag}_HeaderBrass", (0.0, y, 3.54), (2.20, 0.22, 0.06), p["brass"], c, bevel=0.01)
    if door:
        return
    # ceiling coffer of this bay (sits just south of the ring so it recedes behind it)
    box(f"{tag}_Ceil", (0.0, y - 0.92, 3.50), (5.05, 1.70, 0.12), p["ceil"], c, bevel=0.01)
    box(f"{tag}_CeilEdgeL", (-2.48, y - 0.92, 3.42), (0.10, 1.70, 0.08), p["teal"], c, bevel=0.008)
    box(f"{tag}_CeilEdgeR", (2.48, y - 0.92, 3.42), (0.10, 1.70, 0.08), p["teal"], c, bevel=0.008)
    # recessed rectangular light
    box(f"{tag}_LightWell", (0.0, y - 0.92, 3.42), (1.05, 0.62, 0.08), p["iron"], c, bevel=0.01)
    box(f"{tag}_Light", (0.0, y - 0.92, 3.38), (0.88, 0.48, 0.05), p["emit"], c, bevel=0.008)
    box(f"{tag}_LightRim", (0.0, y - 0.92, 3.44), (1.12, 0.68, 0.03), p["brass"], c, bevel=0.006)


def bay_walls(tag, y0, y1, p, c, skip_sides=False):
    """Wall module BETWEEN two rings — recessed panel + teal wainscot."""
    ym = (y0 + y1) * 0.5
    yl = max(0.35, (y1 - y0) - 0.50)
    if skip_sides:
        # ceiling only across the side-door bay
        box(f"{tag}_Ceil", (0.0, ym, 3.50), (5.05, (y1 - y0) - 0.20, 0.12), p["ceil"], c, bevel=0.01)
        box(f"{tag}_LightWell", (0.0, ym, 3.42), (1.05, 0.62, 0.08), p["iron"], c, bevel=0.01)
        box(f"{tag}_Light", (0.0, ym, 3.38), (0.88, 0.48, 0.05), p["emit"], c, bevel=0.008)
        return
    for side, x, nsign in (("E", 2.88, -1), ("W", -2.88, 1)):
        # upper wall sheet
        box(f"{tag}_{side}_Up", (x, ym, 2.38), (0.10, yl, 2.20), p["wall"], c, bevel=0.01)
        # teal wainscot
        box(f"{tag}_{side}_Low", (x, ym, 0.64), (0.14, yl, 1.22), p["teal"], c, bevel=0.014)
        # brass chair rail
        box(f"{tag}_{side}_Rail", (x + nsign * 0.05, ym, 1.26), (0.04, yl - 0.08, 0.05), p["brass"], c, bevel=0.006)
        # recessed panel (real depth so it reads as a kit piece)
        box(f"{tag}_{side}_Recess", (x + nsign * 0.08, ym, 2.32), (0.08, max(0.55, yl - 0.42), 1.28), p["recess"], c, bevel=0.012)
        box(f"{tag}_{side}_PFrame", (x + nsign * 0.04, ym, 2.32), (0.05, max(0.70, yl - 0.28), 1.48), p["teal"], c, bevel=0.008)
        # kick plate
        box(f"{tag}_{side}_Kick", (x, ym, 0.08), (0.16, yl, 0.14), p["iron"], c, bevel=0.01)


def build():
    hide_col("CS_HallwayDress")
    hide_col("01_Hallway_Assembled")
    hide_col("01_Production_Hallway_Assets")
    c = getcol()
    # un-exclude the new collection if a previous run excluded it
    vl = bpy.context.view_layer.layer_collection

    def unex(lc):
        if lc.name == COL:
            lc.exclude = False
        for ch in lc.children:
            unex(ch)

    unex(vl)

    p = {
        "struct": mat("M_Bay_Struct", (0.74, 0.77, 0.80), 0.46, 0.18),
        "teal": mat("M_Bay_Teal", (0.18, 0.48, 0.50), 0.36, 0.22),
        "brass": mat("M_Bay_Brass", (0.78, 0.56, 0.20), 0.28, 0.92),
        "iron": mat("M_Bay_Iron", (0.14, 0.15, 0.17), 0.48, 0.78),
        "wall": mat("M_Bay_Wall", (0.86, 0.88, 0.89), 0.58, 0.03),
        "recess": mat("M_Bay_Recess", (0.78, 0.81, 0.83), 0.62, 0.04),
        "ceil": mat("M_Bay_Ceil", (0.52, 0.58, 0.61), 0.50, 0.10),
        "emit": mat("M_Bay_Emit", (1.0, 0.94, 0.78), 0.18, 0.0, (1.0, 0.93, 0.72), 6.5),
        "stripe": mat("M_Bay_Stripe", (0.90, 0.74, 0.12), 0.38, 0.02),
        "sblk": mat("M_Bay_SBlk", (0.07, 0.07, 0.08), 0.5, 0.04),
        "door": mat("M_Bay_Door", (0.20, 0.22, 0.25), 0.40, 0.42),
        "pipe": mat("M_Bay_Pipe", (0.90, 0.92, 0.93), 0.26, 0.10),
        "plus": mat("M_Bay_Plus", (0.35, 0.85, 0.80), 0.22, 0.05, (0.30, 0.95, 0.88), 4.0),
    }

    floor_path = os.path.join(TEX, "floor_tiles.jpg")
    if os.path.isfile(floor_path):
        p["floor"] = texmat("M_Bay_Floor", floor_path, rough=0.55, uv_scale=(8.0, 20.0))
    else:
        p["floor"] = mat("M_Bay_Floor", (0.78, 0.82, 0.84), 0.55, 0.02)

    # Receding rings. Skip posts in the side-door bay (y ~ 8.5).
    ring_ys = [1.05, 2.95, 4.85, 6.75, 10.25, 12.15, 14.05]
    door_rings = {6.75, 10.25}
    for i, y in enumerate(ring_ys):
        posts = y not in door_rings
        bulkhead(f"Bay{i:02d}", y, p, c, posts=posts, door=False)

    # Wall modules BETWEEN rings. Skip the side-door opening.
    pairs = list(zip(ring_ys[:-1], ring_ys[1:]))
    for i, (y0, y1) in enumerate(pairs):
        skip = (y0 == 6.75 and y1 == 10.25)
        bay_walls(f"BayW{i:02d}", y0, y1, p, c, skip_sides=skip)

    # Extra header over the side-door bay so the tunnel rhythm continues
    box("BayDoor_Header", (0.0, 8.50, 3.40), (5.80, 0.42, 0.38), p["struct"], c, bevel=0.02)
    box("BayDoor_HeaderTeal", (0.0, 8.50, 3.20), (5.10, 0.24, 0.12), p["teal"], c, bevel=0.01)

    # Painterly tiled floor overlay (slightly above existing slabs)
    box("Bay_Floor", (0.0, 7.55, 0.035), (5.55, 14.6, 0.05), p["floor"], c, bevel=0.0)

    # Far end door — concept: dark double leaf, teal frame, glowing plus
    box("End_Frame", (0.0, 14.18, 1.78), (3.55, 0.34, 3.48), p["teal"], c, bevel=0.025)
    box("End_FrameIron", (0.0, 14.08, 1.70), (2.70, 0.16, 3.18), p["iron"], c, bevel=0.012)
    box("End_DoorL", (-0.64, 14.02, 1.48), (1.22, 0.10, 2.88), p["door"], c, bevel=0.012)
    box("End_DoorR", (0.64, 14.02, 1.48), (1.22, 0.10, 2.88), p["door"], c, bevel=0.012)
    for i, z in enumerate((0.72, 1.48, 2.24)):
        box(f"End_RibL{i}", (-0.64, 13.96, z), (1.10, 0.04, 0.06), p["iron"], c, bevel=0.006)
        box(f"End_RibR{i}", (0.64, 13.96, z), (1.10, 0.04, 0.06), p["iron"], c, bevel=0.006)
    box("End_PlusH", (0.0, 13.94, 2.42), (0.55, 0.05, 0.12), p["plus"], c, bevel=0.008)
    box("End_PlusV", (0.0, 13.94, 2.42), (0.12, 0.05, 0.55), p["plus"], c, bevel=0.008)
    box("End_HandleL", (-0.16, 13.96, 1.48), (0.06, 0.07, 0.32), p["brass"], c, bevel=0.008)
    box("End_HandleR", (0.16, 13.96, 1.48), (0.06, 0.07, 0.32), p["brass"], c, bevel=0.008)
    box("End_Sill", (0.0, 14.12, 0.10), (3.20, 0.36, 0.16), p["iron"], c, bevel=0.015)

    # Dual yellow hazard stripes with black borders (concept panel 5)
    box("Bay_StripeBlkL", (-0.42, 7.55, 0.062), (0.055, 14.4, 0.012), p["sblk"], c, bevel=0.0)
    box("Bay_StripeL", (-0.32, 7.55, 0.064), (0.12, 14.4, 0.014), p["stripe"], c, bevel=0.0)
    box("Bay_StripeBlkR", (0.42, 7.55, 0.062), (0.055, 14.4, 0.012), p["sblk"], c, bevel=0.0)
    box("Bay_StripeR", (0.32, 7.55, 0.064), (0.12, 14.4, 0.014), p["stripe"], c, bevel=0.0)

    # Lower-right teal cabinets / conduit run
    for i, y in enumerate((1.55, 2.35, 3.15, 3.95, 4.75, 5.55, 11.05, 11.85, 12.65)):
        box(f"Bay_Cab{i}", (2.58, y, 0.52), (0.36, 0.68, 0.88), p["teal"], c, bevel=0.016)
        box(f"Bay_CabFace{i}", (2.40, y, 0.58), (0.05, 0.52, 0.58), p["iron"], c, bevel=0.008)
        box(f"Bay_CabKnob{i}", (2.37, y, 0.42), (0.04, 0.08, 0.08), p["brass"], c, bevel=0.006)

    # Hung white pipe along east, BETWEEN bulkheads (reads as a run, not a blob)
    cyl("Bay_Pipe", (2.28, 7.55, 3.05), 0.07, 13.2, p["pipe"], c, 12, rot=(math.pi / 2, 0, 0))
    for i, y in enumerate((2.0, 3.9, 5.7, 10.9, 12.7)):
        box(f"Bay_PipeHang{i}", (2.28, y, 3.26), (0.06, 0.06, 0.24), p["teal"], c, bevel=0.006)
        cyl(f"Bay_PipeRing{i}", (2.28, y, 3.05), 0.09, 0.06, p["teal"], c, 12, rot=(math.pi / 2, 0, 0))

    # Signs — concept plates, flush to west/east skins of the first full bay
    sign_a = os.path.join(TEX, "sign_authorized.jpg")
    sign_f = os.path.join(TEX, "sign_facility_level.jpg")
    if os.path.isfile(sign_a):
        sm = texmat("M_Bay_SignAuth", sign_a, emit=True)
        box("Bay_SignAuth", (-2.76, 3.90, 1.92), (0.04, 0.78, 0.92), sm, c, bevel=0.006)
    else:
        box("Bay_SignAuth", (-2.76, 3.90, 1.92), (0.04, 0.78, 0.92), p["teal"], c, bevel=0.006)
    if os.path.isfile(sign_f):
        sm = texmat("M_Bay_SignFac", sign_f, emit=True)
        box("Bay_SignFac", (2.76, 3.90, 1.92), (0.04, 0.78, 0.92), sm, c, bevel=0.006)
    else:
        box("Bay_SignFac", (2.76, 3.90, 1.92), (0.04, 0.78, 0.92), p["teal"], c, bevel=0.006)

    # Hide leftover stick-on hallway dress and assembled hall pieces still in other cols
    for o in bpy.data.objects:
        if o.name.startswith("HallDress_") or o.name.startswith("Modular_Floor_Guide") or o.name == "Hall_Stripe":
            o.hide_viewport = True
            o.hide_render = True
            try:
                o.hide_set(True)
            except RuntimeError:
                pass

    # Hide SOT hallway volume pieces so they don't z-fight the new bays
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        cols = [c.name for c in o.users_collection]
        if not any(n.startswith("SOT_") or n.startswith("01_") for n in cols):
            continue
        loc = o.matrix_world.translation
        if abs(loc.x) < 3.4 and 0.0 < loc.y < 14.6 and loc.z < 4.2:
            # keep cameras, keep mine
            if "07_Transit" in "".join(cols):
                continue
            o.hide_viewport = True
            o.hide_render = True
            try:
                o.hide_set(True)
            except RuntimeError:
                pass

    bpy.context.view_layer.update()
    return {"n": len(c.objects), "col": COL}


result = build()
