"""Hallway production dress: chunky stylized lab, CC0 textures + Kenney kit."""
import math
import os
import bpy
from mathutils import Euler, Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(ROOT, "textures", "hallway")
PH = os.path.join(os.path.dirname(os.path.dirname(ROOT)), "Assets", "cc0", "polyhaven")
COL = "CS_HallwayDress"

# hallway inner faces
XE, XW = 2.93, -2.93
Y0, Y1 = 0.15, 14.25
Z0, ZC = 0.04, 3.52
DOOR0, DOOR1 = 7.35, 9.65


def dress_col():
    c = bpy.data.collections.get(COL)
    if c is None:
        c = bpy.data.collections.new(COL)
        bpy.context.scene.collection.children.link(c)
    for o in list(c.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    return c


def pbr(name, diff, nor=None, rough=None, tint=(1, 1, 1), metal=0.0, spec_rough=0.5, uv=4.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    pr = nt.nodes.new("ShaderNodeBsdfPrincipled")
    texc = nt.nodes.new("ShaderNodeTexImage")
    texc.image = bpy.data.images.load(diff, check_existing=True)
    texc.interpolation = "Smart"
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.inputs["Factor"].default_value = 0.55
    mul.inputs["A"].default_value = (tint[0], tint[1], tint[2], 1)
    nt.links.new(texc.outputs["Color"], mul.inputs["B"])
    nt.links.new(mul.outputs["Result"], pr.inputs["Base Color"])
    pr.inputs["Metallic"].default_value = metal
    pr.inputs["Roughness"].default_value = spec_rough
    if nor and os.path.isfile(nor):
        ntex = nt.nodes.new("ShaderNodeTexImage")
        ntex.image = bpy.data.images.load(nor, check_existing=True)
        ntex.image.colorspace_settings.name = "Non-Color"
        nrm = nt.nodes.new("ShaderNodeNormalMap")
        nrm.inputs["Strength"].default_value = 0.35
        nt.links.new(ntex.outputs["Color"], nrm.inputs["Color"])
        nt.links.new(nrm.outputs["Normal"], pr.inputs["Normal"])
    if rough and os.path.isfile(rough):
        rtex = nt.nodes.new("ShaderNodeTexImage")
        rtex.image = bpy.data.images.load(rough, check_existing=True)
        rtex.image.colorspace_settings.name = "Non-Color"
        nt.links.new(rtex.outputs["Color"], pr.inputs["Roughness"])
    uvn = nt.nodes.new("ShaderNodeTexCoord")
    mapn = nt.nodes.new("ShaderNodeMapping")
    mapn.inputs["Scale"].default_value = (uv, uv, uv)
    nt.links.new(uvn.outputs["UV"], mapn.inputs["Vector"])
    nt.links.new(mapn.outputs["Vector"], texc.inputs["Vector"])
    nt.links.new(pr.outputs["BSDF"], out.inputs["Surface"])
    return m


def mat(name, col, rough=0.45, metal=0.0, emit=None, estr=0.0):
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
    if emit is not None:
        if "Emission Color" in pr.inputs:
            pr.inputs["Emission Color"].default_value = (*emit, 1)
            pr.inputs["Emission Strength"].default_value = estr
    nt.links.new(pr.outputs["BSDF"], out.inputs["Surface"])
    return m


def box(name, loc, size, material, col, rot=(0, 0, 0)):
    bm_name = name + "_me"
    me = bpy.data.meshes.new(bm_name)
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = Euler(rot)
    if material:
        ob.data.materials.append(material)
    col.objects.link(ob)
    return ob


def cyl(name, loc, r, depth, material, col, segs=12, rot=(0, 0, 0)):
    import bmesh
    me = bpy.data.meshes.new(name + "_me")
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=r, depth=depth)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = Euler(rot)
    if material:
        ob.data.materials.append(material)
    col.objects.link(ob)
    return ob


def dup(src_name, name, loc, col, scale=(1, 1, 1), rot=(0, 0, 0), material=None):
    src = bpy.data.objects.get(src_name)
    if src is None:
        return None
    o = src.copy()
    o.data = src.data.copy()
    o.name = name
    o.location = loc
    o.scale = scale
    o.rotation_euler = Euler(rot)
    o.hide_viewport = False
    o.hide_render = False
    try:
        o.hide_set(False)
    except RuntimeError:
        pass
    for c in list(o.users_collection):
        c.objects.unlink(o)
    col.objects.link(o)
    if material:
        o.data.materials.clear()
        o.data.materials.append(material)
    return o


def in_door(y, pad=0.15):
    return (DOOR0 - pad) < y < (DOOR1 + pad)


def build():
    c = dress_col()
    # materials
    floor = pbr(
        "M_Hall_Floor",
        os.path.join(TEX, "floor_tiles_04_diff_2k.jpg"),
        os.path.join(TEX, "floor_tiles_04_nor_gl_2k.jpg"),
        os.path.join(TEX, "floor_tiles_04_rough_2k.jpg"),
        tint=(0.78, 0.82, 0.85),
        spec_rough=0.55,
        uv=3.5,
    )
    metal = pbr(
        "M_Hall_Metal",
        os.path.join(PH, "metal_plate_02", "metal_plate_02_diff_2k.jpg"),
        os.path.join(PH, "metal_plate_02", "metal_plate_02_nor_gl_2k.jpg"),
        tint=(0.72, 0.75, 0.78),
        metal=0.65,
        spec_rough=0.42,
        uv=2.2,
    )
    teal_tex = pbr(
        "M_Hall_TealPlate",
        os.path.join(PH, "blue_metal_plate", "blue_metal_plate_diff_2k.jpg"),
        os.path.join(PH, "blue_metal_plate", "blue_metal_plate_nor_gl_2k.jpg"),
        tint=(0.22, 0.50, 0.54),
        metal=0.25,
        spec_rough=0.4,
        uv=2.0,
    )
    wall = mat("M_Hall_Wall", (0.86, 0.88, 0.90), 0.58, 0.04)
    teal = mat("M_Hall_Teal", (0.14, 0.44, 0.48), 0.38, 0.18)
    brass = mat("M_Hall_Brass", (0.72, 0.52, 0.22), 0.32, 0.92)
    iron = mat("M_Hall_Iron", (0.14, 0.16, 0.18), 0.48, 0.82)
    stripe = mat("M_Hall_Stripe", (0.86, 0.72, 0.12), 0.38, 0.05)
    stripe_b = mat("M_Hall_StripeBlk", (0.06, 0.06, 0.07), 0.5, 0.1)
    emit = mat("M_Hall_Emit", (1.0, 0.92, 0.72), 0.2, 0.0, emit=(1.0, 0.9, 0.65), estr=5.5)
    emit_c = mat("M_Hall_EmitCool", (0.7, 0.88, 1.0), 0.2, 0.0, emit=(0.65, 0.85, 1.0), estr=3.5)
    pipe_m = mat("M_Hall_Pipe", (0.90, 0.92, 0.93), 0.28, 0.15)
    grate = mat("M_Hall_Grate", (0.18, 0.20, 0.22), 0.45, 0.7)

    # --- floor retouch ---
    fl = bpy.data.objects.get("Lock_Floor.002")
    if fl:
        fl.data.materials.clear()
        fl.data.materials.append(floor)
    # dual hazard stripes + black borders (concept)
    for x, w, m in (
        (-0.42, 0.07, stripe_b),
        (-0.32, 0.12, stripe),
        (-0.22, 0.07, stripe_b),
        (0.22, 0.07, stripe_b),
        (0.32, 0.12, stripe),
        (0.42, 0.07, stripe_b),
    ):
        box(f"HallDress_Stripe_{x}", (x, 7.2, 0.055), (w, 13.9, 0.012), m, c)
    # hide old single stripe
    old = bpy.data.objects.get("Hall_Stripe")
    if old:
        old.hide_viewport = True
        old.hide_render = True

    # floor edge rails
    box("HallDress_RailE", (2.55, 7.2, 0.07), (0.18, 14.1, 0.08), iron, c)
    box("HallDress_RailW", (-2.55, 7.2, 0.07), (0.18, 14.1, 0.08), iron, c)

    # drain grates
    for i, y in enumerate((1.8, 4.4, 11.2, 13.4)):
        box(f"HallDress_GrateE{i}", (2.35, y, 0.06), (0.38, 0.55, 0.03), grate, c)
        box(f"HallDress_GrateW{i}", (-2.35, y, 0.06), (0.38, 0.55, 0.03), grate, c)

    # door thresholds
    for x, tag in ((0.0, "C"),):
        pass
    box("HallDress_ThreshE", (2.55, 8.5, 0.06), (0.55, 2.5, 0.04), teal, c)
    box("HallDress_ThreshW", (-2.55, 8.5, 0.06), (0.55, 2.5, 0.04), teal, c)

    # --- wall panel grid ---
    # skip door bay
    panel_ys = [y for y in (0.95, 2.55, 4.15, 5.75, 10.55, 12.15, 13.55)]
    for side, xface, nsign in (("E", XE, -1), ("W", XW, 1)):
        for i, y in enumerate(panel_ys):
            x = xface + nsign * 0.04
            # inset plate
            box(f"HallDress_Panel{side}{i}", (x, y, 2.15), (0.05, 1.35, 1.55), wall, c)
            # teal frame
            box(f"HallDress_PFrame{side}{i}T", (x + nsign * 0.01, y, 2.95), (0.06, 1.45, 0.07), teal, c)
            box(f"HallDress_PFrame{side}{i}B", (x + nsign * 0.01, y, 1.35), (0.06, 1.45, 0.07), teal, c)
            box(f"HallDress_PFrame{side}{i}L", (x + nsign * 0.01, y - 0.69, 2.15), (0.06, 0.07, 1.65), teal, c)
            box(f"HallDress_PFrame{side}{i}R", (x + nsign * 0.01, y + 0.69, 2.15), (0.06, 0.07, 1.65), teal, c)
            # kenney wall-detail greeble on some panels
            if i % 2 == 0:
                dup(
                    "wall-detail",
                    f"HallDress_Detail{side}{i}",
                    (x + nsign * 0.09, y, 2.35),
                    c,
                    scale=(1.1, 1.1, 1.1),
                    rot=(math.pi / 2, 0, math.pi / 2 if side == "E" else -math.pi / 2),
                    material=iron,
                )

    # kick plate on wainscot
    box("HallDress_KickE", (XE - 0.02, 7.2, 0.18), (0.04, 14.1, 0.28), iron, c)
    box("HallDress_KickW", (XW + 0.02, 7.2, 0.18), (0.04, 14.1, 0.28), iron, c)
    # brass reveal at wainscot top
    box("HallDress_RevealE", (XE - 0.03, 7.2, 1.16), (0.03, 14.1, 0.04), brass, c)
    box("HallDress_RevealW", (XW + 0.03, 7.2, 1.16), (0.03, 14.1, 0.04), brass, c)

    # --- ceiling coffers + lights ---
    rib_ys = [0.35, 2.31, 4.35, 6.22, 8.18, 10.14, 12.09, 14.05]
    for i in range(len(rib_ys) - 1):
        y0, y1 = rib_ys[i], rib_ys[i + 1]
        ym = (y0 + y1) * 0.5
        box(f"HallDress_Coffer{i}", (0.0, ym, ZC - 0.04), (5.4, (y1 - y0) - 0.22, 0.08), metal, c)
        # recessed light bar
        box(f"HallDress_CLight{i}", (0.0, ym, ZC - 0.10), (1.15, min(0.85, y1 - y0 - 0.35), 0.04), emit, c)
        box(f"HallDress_CLightTrim{i}", (0.0, ym, ZC - 0.08), (1.28, min(0.98, y1 - y0 - 0.28), 0.03), brass, c)

    # thicken existing teal ribs visually with an underside lip
    for i, y in enumerate(rib_ys):
        box(f"HallDress_RibLip{i}", (0.0, y, 3.40), (5.7, 0.18, 0.08), teal, c)

    # --- cable tray west, coolant pipe east ---
    box("HallDress_Tray", (XW + 0.38, 7.2, 3.18), (0.42, 13.6, 0.08), iron, c)
    box("HallDress_TrayL", (XW + 0.20, 7.2, 3.18), (0.05, 13.6, 0.16), iron, c)
    box("HallDress_TrayR", (XW + 0.56, 7.2, 3.18), (0.05, 13.6, 0.16), iron, c)
    # cables as thin cylinders
    for i, xoff in enumerate((0.28, 0.38, 0.48)):
        cyl(f"HallDress_Cable{i}", (XW + xoff, 7.2, 3.22), 0.03, 13.4, brass if i == 1 else iron, c, 8, rot=(math.pi / 2, 0, 0))

    # Kenney pipes along east ceiling
    pipe_len = 0.5
    npipe = 26
    ystart = 0.6
    for i in range(npipe):
        y = ystart + i * pipe_len
        if in_door(y, 0.4):
            continue
        dup(
            "pipe",
            f"HallDress_Pipe{i}",
            (XE - 0.42, y, 3.22),
            c,
            scale=(0.85, 0.85, 1.0),
            rot=(math.pi / 2, 0, 0),
            material=pipe_m,
        )
    # hangers
    for i, y in enumerate((1.6, 4.0, 6.4, 10.8, 13.2)):
        box(f"HallDress_Hang{i}", (XE - 0.42, y, 3.38), (0.08, 0.08, 0.28), teal, c)
        box(f"HallDress_HangB{i}", (XE - 0.42, y, 3.48), (0.22, 0.08, 0.05), brass, c)
    dup("pipe-bend", "HallDress_PipeBendN", (XE - 0.42, 13.95, 3.22), c, scale=(0.85, 0.85, 0.85), rot=(0, 0, math.pi / 2), material=pipe_m)
    dup("pipe-bend", "HallDress_PipeBendS", (XE - 0.42, 0.45, 3.22), c, scale=(0.85, 0.85, 0.85), rot=(0, 0, -math.pi / 2), material=pipe_m)

    # --- bulkhead lamps (replace floating cubes with modeled fixtures) ---
    def bulkhead(tag, loc, yaw):
        box(f"{tag}_Back", loc, (0.08, 0.28, 0.22), iron, c, rot=(0, 0, yaw))
        box(f"{tag}_Cage", loc, (0.14, 0.22, 0.16), brass, c, rot=(0, 0, yaw))
        box(f"{tag}_Lens", loc, (0.06, 0.16, 0.12), emit, c, rot=(0, 0, yaw))

    # hallway kit lamps: rebuild on hall walls
    bulkhead("HallDress_LampEN", (HALL_E := XE - 0.12, 10.8, 2.78), -math.pi / 2)
    bulkhead("HallDress_LampES", (XE - 0.12, 3.6, 2.78), -math.pi / 2)
    bulkhead("HallDress_LampWN", (XW + 0.12, 10.8, 2.78), math.pi / 2)
    bulkhead("HallDress_LampWS", (XW + 0.12, 3.6, 2.78), math.pi / 2)
    # extra mid lamps
    bulkhead("HallDress_LampEM", (XE - 0.12, 12.6, 2.78), -math.pi / 2)
    bulkhead("HallDress_LampWM", (XW + 0.12, 12.6, 2.78), math.pi / 2)

    # hide old simple hallway lamps (keep brass kit ones if they sit on walls)
    for n in ("Lamp_Col_East_North", "Lamp_Col_East_South", "Lamp_Col_West_North", "Lamp_Col_West_South"):
        o = bpy.data.objects.get(n)
        if o:
            o.hide_viewport = True
            o.hide_render = True

    # --- door surrounds: extra depth, corner guards, switches ---
    for side, x, yaw in (("E", XE, -math.pi / 2), ("W", XW, math.pi / 2)):
        nsign = -1 if side == "E" else 1
        # inner lip
        box(f"HallDress_DoorLip{side}S", (x + nsign * 0.08, DOOR0 - 0.08, 1.24), (0.12, 0.10, 2.48), teal, c)
        box(f"HallDress_DoorLip{side}N", (x + nsign * 0.08, DOOR1 + 0.08, 1.24), (0.12, 0.10, 2.48), teal, c)
        box(f"HallDress_DoorLip{side}H", (x + nsign * 0.08, 8.5, 2.55), (0.12, 2.50, 0.12), teal, c)
        # corner guards
        box(f"HallDress_Guard{side}S", (x + nsign * 0.16, DOOR0 - 0.18, 0.45), (0.10, 0.10, 0.9), brass, c)
        box(f"HallDress_Guard{side}N", (x + nsign * 0.16, DOOR1 + 0.18, 0.45), (0.10, 0.10, 0.9), brass, c)
        dup(
            "wall-switch",
            f"HallDress_Switch{side}",
            (x + nsign * 0.05, DOOR0 - 0.55, 1.25),
            c,
            scale=(1.4, 1.4, 1.4),
            rot=(0, 0, yaw),
            material=iron,
        )

    # --- vents ---
    for i, y in enumerate((1.4, 5.2, 11.6, 13.6)):
        box(f"HallDress_VentE{i}", (XE - 0.05, y, 3.05), (0.06, 0.55, 0.32), iron, c)
        box(f"HallDress_VentSlatE{i}", (XE - 0.08, y, 3.05), (0.03, 0.48, 0.04), grate, c)
        box(f"HallDress_VentW{i}", (XW + 0.05, y, 3.05), (0.06, 0.55, 0.32), iron, c)
        box(f"HallDress_VentSlatW{i}", (XW + 0.08, y, 3.05), (0.03, 0.48, 0.04), grate, c)

    # --- south entrance extra frame ---
    box("HallDress_SouthHeader", (0.0, 0.22, 3.15), (5.9, 0.18, 0.22), teal, c)
    box("HallDress_SouthBrass", (0.0, 0.22, 3.28), (3.2, 0.10, 0.05), brass, c)

    # --- north end: deeper portal lip around existing plus ---
    box("HallDress_NorthLip", (0.0, 14.15, 1.8), (4.4, 0.16, 3.4), teal, c)
    box("HallDress_NorthInner", (0.0, 14.05, 1.7), (2.6, 0.10, 2.9), iron, c)

    # Kenney floor-panel as a couple of access hatches
    dup("floor-panel", "HallDress_HatchA", (1.35, 2.4, 0.12), c, scale=(0.55, 0.55, 0.25), material=iron)
    dup("floor-panel", "HallDress_HatchB", (-1.35, 12.2, 0.12), c, scale=(0.55, 0.55, 0.25), material=iron)

    # park kit originals
    kit = bpy.data.collections.get("CS_KenneyKit")
    if kit:
        for o in kit.objects:
            o.hide_viewport = True
            o.hide_render = True
            o.location.x = -45
        # exclude kit collection
        def walk(lc):
            if lc.name == "CS_KenneyKit":
                lc.exclude = True
            for ch in lc.children:
                walk(ch)
        walk(bpy.context.view_layer.layer_collection)

    bpy.context.view_layer.update()
    return {"objects": len(c.objects)}


result = build()
