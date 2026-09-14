"""Architectural shell: floor, walls, ceiling opening, D01, structure, stairs, gallery."""
import math
from mathutils import Vector
import kit as k
from layout import *


def _cx():
    return (X0 + X1) / 2, (Y0 + Y1) / 2


def floor():
    k.group("01 Architecture")
    mx, my = _cx()
    k.box("Structural floor", (mx, my, -FLOOR_THICK / 2), (X1 - X0 + WALL * 2, Y1 - Y0 + WALL, FLOOR_THICK), "floor", 0.002)
    k.box("Floor coating field", (mx, my, 0.004), (X1 - X0 - 0.08, Y1 - Y0 - 0.08, 0.006), "floor", 0.001)
    for x in (0.9, 3.0, 5.4, 7.8):
        k.box("floor saw cut x", (x, my, 0.008), (0.012, Y1 - Y0 - 0.2, 0.003), "dark", 0)
    for y in (2.2, 4.05, 6.4, 8.2):
        k.box("floor saw cut y", (mx, y, 0.008), (X1 - X0 - 0.2, 0.012, 0.003), "dark", 0)
    k.box("patched concrete A", (7.4, 2.6, 0.01), (1.6, 0.55, 0.004), "patch", 0.003)
    k.box("patched concrete B", (-0.4, 8.3, 0.01), (1.2, 0.4, 0.004), "patch", 0.003)
    # West and south route paint
    k.box("west route edge L", (-0.15, my, 0.012), (0.045, Y1 - 0.3, 0.002), "yellow", 0.001)
    k.box("west route edge R", (0.75, my, 0.012), (0.045, Y1 - 0.3, 0.002), "yellow", 0.001)
    k.box("south walk edge", (3.4, 1.18, 0.012), (6.4, 0.04, 0.002), "yellow", 0.001)
    k.box("pull bay edge N", (7.7, 7.22, 0.012), (3.4, 0.045, 0.002), "yellow", 0.001)
    k.box("pull bay edge S", (7.7, 1.22, 0.012), (3.4, 0.045, 0.002), "yellow", 0.001)
    k.box("pull bay hatch", (7.85, 4.05, 0.011), (3.1, 5.7, 0.002), "yellow", 0.001)
    k.text("pull bay legend", "3.5 m  BUNDLE CLEAR", (7.85, 4.05, 0.016), 0.16, "ink", "UP")
    # Drain trench along east, flush grates
    k.box("drain channel", (8.95, 5.2, -0.04), (0.22, 6.4, 0.07), "dark", 0.004)
    for i in range(42):
        k.box("drain grate", (8.95, 2.1 + i * 0.15, -0.002), (0.20, 0.04, 0.008), "steel", 0.002)
    k.anchor("floor slab", (mx, my, 0), "Structural floor")


def walls():
    k.group("01 Architecture")
    mx, my = _cx()
    h = Z1
    # West / east / north solid walls
    k.box("WestWall", (X0 - WALL / 2, my, h / 2), (WALL, Y1 - Y0 + WALL, h), "wall", 0.016)
    k.box("EastWall", (X1 + WALL / 2, my, h / 2), (WALL, Y1 - Y0 + WALL, h), "wall", 0.016)
    k.box("NorthWall", (mx, Y1 + WALL / 2, h / 2), (X1 - X0 + WALL * 2, WALL, h), "wall", 0.016)
    # South wall split around D01
    door_l, door_r = D01_C[0] - D01_W / 2, D01_C[0] + D01_W / 2
    left_w = door_l - X0
    right_w = X1 - door_r
    k.box("SouthWall west", (X0 + left_w / 2, Y0 - WALL / 2, h / 2), (left_w, WALL, h), "wall", 0.016)
    k.box("SouthWall east", (door_r + right_w / 2, Y0 - WALL / 2, h / 2), (right_w, WALL, h), "wall", 0.016)
    k.box("SouthWall header", (D01_C[0], Y0 - WALL / 2, D01_H + (h - D01_H) / 2), (D01_W, WALL, h - D01_H), "wall", 0.012)
    # Dado / panel rhythm
    for name, x, axis in (("West dado", X0 + 0.012, "X"), ("East dado", X1 - 0.012, "X")):
        if axis == "X":
            k.box(name, (x, my, 0.55), (0.02, Y1 - Y0 - 0.1, 1.10), "dado", 0.004)
    k.box("North dado", (mx, Y1 - 0.012, 0.55), (X1 - X0 - 0.1, 0.02, 1.10), "dado", 0.004)
    k.box("South dado west", (X0 + left_w / 2, Y0 + 0.012, 0.55), (left_w - 0.05, 0.02, 1.10), "dado", 0.004)
    k.box("South dado east", (door_r + right_w / 2, Y0 + 0.012, 0.55), (right_w - 0.05, 0.02, 1.10), "dado", 0.004)
    # Panel reveals
    for z in (1.12, 3.15, 4.85):
        k.box("west reveal", (X0 + 0.014, my, z), (0.008, Y1 - Y0 - 0.2, 0.014), "dark", 0)
        k.box("east reveal", (X1 - 0.014, my, z), (0.008, Y1 - Y0 - 0.2, 0.014), "dark", 0)
        k.box("north reveal", (mx, Y1 - 0.014, z), (X1 - X0 - 0.2, 0.008, 0.014), "dark", 0)
    for y in (2.0, 4.05, 6.2, 8.3):
        k.box("west joint", (X0 + 0.015, y, 3.4), (0.006, 0.01, 4.4), "dark", 0)
        k.box("east joint", (X1 - 0.015, y, 3.4), (0.006, 0.01, 4.4), "dark", 0)
    # Columns transferring turbine slab
    for x, y in ((-1.35, 2.15), (-1.35, 6.55), (5.55, 2.15), (5.55, 6.55), (9.15, 2.15), (9.15, 8.15)):
        k.box("steel column", (x, y, 3.0), (0.22, 0.26, 5.95), "struct", 0.01)
        k.box("column base shoe", (x, y, 0.08), (0.34, 0.40, 0.16), "dark", 0.006)
        k.box("column cap plate", (x, y, 5.88), (0.36, 0.40, 0.08), "steel", 0.004)
        k.anchor("column " + f"{x:.1f}_{y:.1f}", (x, y, 0), "Structural floor")


def ceiling():
    k.group("01 Architecture")
    mx, my = _cx()
    # Slab with a real 2.5 x 1.5 opening at EXH_C
    slab = k.box("Ceiling slab", (mx, my, Z1 + CEIL_THICK / 2), (X1 - X0 + WALL * 2, Y1 - Y0 + WALL, CEIL_THICK), "concrete", 0.01)
    cutter = k.box("U04 opening cutter", (EXH_C[0], EXH_C[1], Z1 + CEIL_THICK / 2), (EXH_X, EXH_Y, CEIL_THICK + 0.2), None, 0)
    mod = slab.modifiers.new("exhaust aperture", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cutter
    import bpy

    bpy.context.view_layer.objects.active = slab
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    slab["validation_role"] = "ceiling_with_U04_opening"
    # Opening curb / pit flange matching turbine pit language
    k.box("exhaust curb X-", (EXH_C[0] - EXH_X / 2 - 0.08, EXH_C[1], Z1 - 0.05), (0.16, EXH_Y + 0.32, 0.10), "dark", 0.008)
    k.box("exhaust curb X+", (EXH_C[0] + EXH_X / 2 + 0.08, EXH_C[1], Z1 - 0.05), (0.16, EXH_Y + 0.32, 0.10), "dark", 0.008)
    k.box("exhaust curb Y-", (EXH_C[0], EXH_C[1] - EXH_Y / 2 - 0.08, Z1 - 0.05), (EXH_X + 0.32, 0.16, 0.10), "dark", 0.008)
    k.box("exhaust curb Y+", (EXH_C[0], EXH_C[1] + EXH_Y / 2 + 0.08, Z1 - 0.05), (EXH_X + 0.32, 0.16, 0.10), "dark", 0.008)
    for i, (dx, dy) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):
        k.bolt("curb bolt" + str(i), (EXH_C[0] + dx * (EXH_X / 2 + 0.08), EXH_C[1] + dy * (EXH_Y / 2 + 0.08), Z1 - 0.01), "Z", 0.016)
    # Girders under slab — they frame the opening, they do not cross it
    for y in (1.4, 2.7, 5.5, 7.3, 8.9):
        k.box("roof girder bot", (mx, y, 5.52), (X1 - X0 - 0.3, 0.22, 0.05), "steel", 0.006)
        k.box("roof girder web", (mx, y, 5.68), (X1 - X0 - 0.3, 0.03, 0.28), "struct", 0.004)
        k.box("roof girder top", (mx, y, 5.84), (X1 - X0 - 0.3, 0.22, 0.05), "steel", 0.006)
    # Opening-side header beams
    k.box("opening header Y-", (EXH_C[0], EXH_C[1] - EXH_Y / 2 - 0.28, 5.62), (EXH_X + 1.4, 0.20, 0.26), "struct", 0.008)
    k.box("opening header Y+", (EXH_C[0], EXH_C[1] + EXH_Y / 2 + 0.28, 5.62), (EXH_X + 1.4, 0.20, 0.26), "struct", 0.008)
    k.box("opening header X-", (EXH_C[0] - EXH_X / 2 - 0.32, EXH_C[1], 5.62), (0.20, EXH_Y + 0.9, 0.26), "struct", 0.008)
    k.box("opening header X+", (EXH_C[0] + EXH_X / 2 + 0.32, EXH_C[1], 5.62), (0.20, EXH_Y + 0.9, 0.26), "struct", 0.008)


def door_d01():
    k.group("02 Access D01")
    y = Y0 + 0.02
    # Jambs and threshold
    k.box("D01 west jamb", (-1.08, y, D01_H / 2), (0.16, 0.22, D01_H + 0.08), "struct", 0.01)
    k.box("D01 east jamb", (1.08, y, D01_H / 2), (0.16, 0.22, D01_H + 0.08), "struct", 0.01)
    k.box("D01 header bar", (0, y, D01_H + 0.06), (2.32, 0.22, 0.12), "struct", 0.008)
    k.box("D01 threshold plate", (0, 0.04, 0.012), (2.04, 0.28, 0.02), "steel", 0.003)
    k.box("D01 identity beam", (0, y - 0.02, 2.62), (2.5, 0.18, 0.16), "dark", 0.008)
    k.text("D01 identity", "CONDENSER  /  CSB-01", (0, y - 0.12, 2.58), 0.13, "white", "S")
    k.text("D01 contract", "D01", (0, y - 0.12, 2.42), 0.09, "yellow", "S")
    # Two opposed sliding leaves parked in wall pockets (open presentation)
    k.box("D01 west leaf parked", (-1.52, 0.08, 1.18), (0.96, 0.07, 2.28), "oxide", 0.008)
    k.box("D01 west leaf panel", (-1.52, 0.12, 1.22), (0.78, 0.02, 1.7), "oxide_light", 0.004)
    k.box("D01 east leaf parked", (1.52, 0.08, 1.18), (0.96, 0.07, 2.28), "oxide", 0.008)
    k.box("D01 east leaf panel", (1.52, 0.12, 1.22), (0.78, 0.02, 1.7), "oxide_light", 0.004)
    for x in (-1.52, 1.52):
        k.box("leaf window frame", (x, 0.13, 1.85), (0.42, 0.03, 0.55), "dark", 0.004)
        k.box("leaf window glass", (x, 0.145, 1.85), (0.34, 0.012, 0.46), "glass", 0.002)
        k.box("leaf kick plate", (x, 0.125, 0.28), (0.86, 0.02, 0.36), "steel", 0.003)
    k.box("D01 track", (0, 0.16, 2.42), (4.2, 0.06, 0.05), "dark", 0.003)
    k.box("D01 floor guide", (0, 0.10, 0.03), (4.1, 0.04, 0.03), "dark", 0.002)
    k.empty("IF_PORTAL_D01_SERVICE", (0, 0, 0), "2.0 x 2.4 m service portal, outward -Y, unbound receiving connector")
    k.hook("INTERACT_D01", (0.85, 0.35, 1.05), "slide_leaf", "D01")


def stairs_and_gallery():
    k.group("03 Stairs and gallery")
    # Flight 1: along south wall, east of door pocket, rise to mid landing
    treads = 11
    rise = 2.07 / treads
    going = (STAIR_MID - STAIR_X0) / treads
    for i in range(treads):
        x = STAIR_X0 + (i + 0.5) * going
        z = (i + 1) * rise
        k.box("stair1 tread", (x, (STAIR_Y0 + STAIR_Y1) / 2, z - 0.02), (going - 0.01, 0.88, 0.04), "steel", 0.003)
        k.box("stair1 riser", (x - going / 2 + 0.01, (STAIR_Y0 + STAIR_Y1) / 2, z - rise / 2), (0.02, 0.88, rise), "struct", 0.002)
    k.box("stair1 stringer L", (STAIR_X0 + (STAIR_MID - STAIR_X0) / 2, STAIR_Y0 + 0.04, 1.05), (STAIR_MID - STAIR_X0 + 0.1, 0.05, 2.2), "struct", 0.004)
    k.box("stair1 stringer R", (STAIR_X0 + (STAIR_MID - STAIR_X0) / 2, STAIR_Y1 - 0.04, 1.05), (STAIR_MID - STAIR_X0 + 0.1, 0.05, 2.2), "struct", 0.004)
    # Mid landing
    k.box("mid landing", ((STAIR_MID + STAIR_X1) / 2, (STAIR_Y0 + STAIR_Y1) / 2, 2.07), (STAIR_X1 - STAIR_MID + 0.15, 0.95, 0.06), "steel", 0.005)
    k.box("mid landing plate", ((STAIR_MID + STAIR_X1) / 2, (STAIR_Y0 + STAIR_Y1) / 2, 2.11), (STAIR_X1 - STAIR_MID, 0.88, 0.02), "dark", 0.003)
    # Flight 2: north along east of condenser to gallery
    t2 = 12
    y0, y1 = STAIR_Y1, 3.95
    rise2 = (GAL_Z - 2.07) / t2
    going2 = (y1 - y0) / t2
    sx = (STAIR_MID + STAIR_X1) / 2
    for i in range(t2):
        y = y0 + (i + 0.5) * going2
        z = 2.07 + (i + 1) * rise2
        k.box("stair2 tread", (sx, y, z - 0.02), (0.88, going2 - 0.01, 0.04), "steel", 0.003)
        k.box("stair2 riser", (sx, y - going2 / 2 + 0.01, z - rise2 / 2), (0.88, 0.02, rise2), "struct", 0.002)
    k.box("stair2 stringer L", (sx - 0.42, (y0 + y1) / 2, 3.15), (0.05, y1 - y0 + 0.1, 2.3), "struct", 0.004)
    k.box("stair2 stringer R", (sx + 0.42, (y0 + y1) / 2, 3.15), (0.05, y1 - y0 + 0.1, 2.3), "struct", 0.004)
    # Railings flight 1
    for y in (STAIR_Y0 + 0.02, STAIR_Y1 - 0.02):
        k.pipe("stair1 rail", [(STAIR_X0, y, 1.05), (STAIR_MID, y, 3.12)], 0.018, "yellow", 0.08)
        for i in range(0, treads, 2):
            x = STAIR_X0 + (i + 0.5) * going
            z = (i + 1) * rise
            k.rod("stair1 baluster", (x, y, z), (x, y, z + 0.95), 0.012, "yellow")
    # Railings flight 2
    for xoff in (-0.44, 0.44):
        k.pipe("stair2 rail", [(sx + xoff, y0, 3.12), (sx + xoff, y1, GAL_Z + GAL_RAIL)], 0.018, "yellow", 0.08)
    # Gallery deck around condenser (open U, south side left as stair approach)
    cx, cy = CD_C[0], CD_C[1]
    inner_x0 = cx - CD_LEN_X / 2 - 0.15
    inner_x1 = cx + CD_LEN_X / 2 + WB_DEPTH + 0.05
    inner_y0 = cy - CD_WID_Y / 2 - 0.12
    inner_y1 = cy + CD_WID_Y / 2 + 0.12
    gx0, gx1 = inner_x0 - GAL_W, inner_x1 + GAL_W
    gy0, gy1 = inner_y0 - GAL_W, inner_y1 + GAL_W
    k.box("gallery east deck", (inner_x1 + GAL_W / 2, (inner_y0 + inner_y1) / 2, GAL_Z), (GAL_W, inner_y1 - inner_y0 + GAL_W * 2, 0.06), "steel", 0.005)
    k.box("gallery west deck", (inner_x0 - GAL_W / 2, (inner_y0 + inner_y1) / 2, GAL_Z), (GAL_W, inner_y1 - inner_y0 + GAL_W * 2, 0.06), "steel", 0.005)
    k.box("gallery north deck", (cx, inner_y1 + GAL_W / 2, GAL_Z), (inner_x1 - inner_x0, GAL_W, 0.06), "steel", 0.005)
    k.box("gallery south deck", (cx + 0.4, inner_y0 - GAL_W / 2, GAL_Z), (inner_x1 - inner_x0 - 0.8, GAL_W, 0.06), "steel", 0.005)
    # Gallery posts down to condenser saddles / columns
    for x, y in (
        (inner_x1 + GAL_W / 2, inner_y0),
        (inner_x1 + GAL_W / 2, inner_y1),
        (inner_x0 - GAL_W / 2, inner_y0),
        (inner_x0 - GAL_W / 2, inner_y1),
        (cx, inner_y1 + GAL_W / 2),
    ):
        k.box("gallery hanger", (x, y, (GAL_Z + Z1) / 2), (0.06, 0.06, Z1 - GAL_Z - 0.08), "struct", 0.003)
        k.anchor("gallery hang " + f"{x:.1f}", (x, y, Z1), "Ceiling slab", (0, 0, 1), 0.02, 0.01)
    # Outer rail
    z_r = GAL_Z + GAL_RAIL
    k.pipe("gal rail E", [(gx1, gy0, z_r), (gx1, gy1, z_r)], 0.016, "yellow", 0.05)
    k.pipe("gal rail N", [(gx1, gy1, z_r), (gx0, gy1, z_r)], 0.016, "yellow", 0.05)
    k.pipe("gal rail W", [(gx0, gy1, z_r), (gx0, gy0, z_r)], 0.016, "yellow", 0.05)
    k.pipe("gal rail S E", [(gx1, gy0, z_r), (cx + 0.9, gy0, z_r)], 0.016, "yellow", 0.05)
    k.pipe("gal rail S W", [(gx0, gy0, z_r), (cx - 0.6, gy0, z_r)], 0.016, "yellow", 0.05)
    for x, y in ((gx1, gy0), (gx1, gy1), (gx0, gy1), (gx0, gy0), (cx, gy1), (cx + 0.9, gy0)):
        k.rod("gal post", (x, y, GAL_Z + 0.03), (x, y, z_r), 0.014, "yellow")
    k.box("kick plate E", (gx1 - 0.02, (gy0 + gy1) / 2, GAL_Z + 0.08), (0.03, gy1 - gy0, 0.10), "dark", 0.002)
    k.anchor("stair foot", (STAIR_X0 + 0.2, (STAIR_Y0 + STAIR_Y1) / 2, 0), "Structural floor")


def ceiling_services():
    k.group("04 Ceiling services")
    # Cable tray west
    for xx in (-1.15, -0.62):
        k.box("tray side", (xx, 4.7, 5.42), (0.04, 8.6, 0.12), "steel", 0.003)
    for i in range(24):
        k.box("tray rung", (-0.88, 0.6 + i * 0.36, 5.38), (0.55, 0.03, 0.03), "dark", 0.002)
    for y in (1.5, 4.05, 7.2, 8.9):
        k.rod("tray hanger", (-0.88, y, 5.48), (-0.88, y, 5.95), 0.01, "steel")
        k.anchor("tray " + str(y), (-0.88, y, 5.95), "Ceiling slab", (0, 0, 1))
    k.pipe("tray feeder A", [(-1.05, 0.5, 5.44), (-1.05, 9.0, 5.44)], 0.018, "rubber", 0.05)
    k.pipe("tray feeder B", [(-0.72, 0.5, 5.44), (-0.72, 9.0, 5.44)], 0.016, "rubber", 0.05)
    # Extract fan on north wall
    k.box("extract frame", (3.0, Y1 - 0.12, 5.15), (1.15, 0.10, 1.15), "steel", 0.008)
    k.box("extract gasket", (3.0, Y1 - 0.04, 5.15), (1.28, 0.08, 1.28), "dark", 0.01)
    k.cyl("extract hub", (3.0, Y1 - 0.22, 5.15), 0.12, 0.12, "steel", "Y", 24, 0.006)
    for i in range(7):
        a = i * math.tau / 7
        k.mesh(
            "extract blade",
            [
                (3.0 + 0.10 * math.cos(a), Y1 - 0.20, 5.15 + 0.10 * math.sin(a)),
                (3.0 + 0.42 * math.cos(a + 0.2), Y1 - 0.20, 5.15 + 0.42 * math.sin(a + 0.2)),
                (3.0 + 0.42 * math.cos(a + 0.55), Y1 - 0.20, 5.15 + 0.42 * math.sin(a + 0.55)),
                (3.0 + 0.12 * math.cos(a + 0.4), Y1 - 0.20, 5.15 + 0.12 * math.sin(a + 0.4)),
            ],
            [(0, 1, 2, 3)],
            "steel",
            0.003,
        )
    for rad in (0.20, 0.32, 0.46):
        k.torus("extract guard", (3.0, Y1 - 0.28, 5.15), rad, 0.008, "dark", "Y")
    k.empty("IF_VENT_OUT", IF_VENT_OUT, "unbound extract; no remote HVAC owner")


def practical_lights():
    k.group("05 Lighting")
    warm = (1.0, 0.86, 0.68)
    # Aisle battens — warm, not cyan
    for i, (x, y) in enumerate(
        [
            (-0.2, 1.6),
            (-0.2, 4.05),
            (-0.2, 6.6),
            (-0.2, 8.5),
            (3.0, 1.55),
            (7.4, 2.4),
            (7.4, 5.5),
            (7.4, 8.2),
            (3.0, 7.4),
        ]
    ):
        n = f"batten{i}"
        k.box(n + " channel", (x, y, 5.18), (0.22, 1.35, 0.10), "steel", 0.01)
        k.box(n + " diffuser", (x, y, 5.12), (0.16, 1.22, 0.03), "lamp", 0.012)
        k.rod(n + " drop L", (x, y - 0.5, 5.24), (x, y - 0.5, 5.92), 0.008, "dark")
        k.rod(n + " drop R", (x, y + 0.5, 5.24), (x, y + 0.5, 5.92), 0.008, "dark")
        k.light(n, (x, y, 5.08), (x, y, 0), 220, warm, 1.2, "RECTANGLE", 0.16)
        k.anchor(n, (x, y, 5.92), "Ceiling slab", (0, 0, 1))
    # Task on condenser
    k.light("task CD south", (3.0, 2.35, 4.55), (3.0, 4.05, 3.2), 90, warm, 0.7)
    k.light("task CD east", (5.6, 4.05, 3.8), (4.6, 4.05, 3.0), 80, warm, 0.6)
    k.light("task pumps", (3.2, 7.5, 3.4), (3.2, 7.5, 1.0), 70, (1.0, 0.84, 0.64), 0.8)
    k.light("task operator", (-0.6, 4.05, 2.55), (-1.2, 4.05, 1.3), 55, (1.0, 0.78, 0.55), 0.45)
    k.light("entry wash", (0.0, 1.1, 2.7), (0.0, 2.5, 1.2), 70, warm, 0.9)
    k.light("gallery task", (5.3, 4.05, 5.35), (3.0, 4.05, 4.8), 50, warm, 0.5)


def signs():
    k.group("06 Signage")
    k.box("ID board", (3.0, Y1 - 0.04, 2.55), (2.8, 0.04, 0.42), "dark", 0.006)
    k.text("ID board text", "CSB-01  TURBINE CONDENSER BAY", (3.0, Y1 - 0.07, 2.48), 0.16, "white", "N")
    k.box("haz board", (3.0, Y1 - 0.04, 2.12), (2.4, 0.04, 0.28), "dark", 0.005)
    k.text("haz text", "VACUUM  /  HOT SURFACES  /  HEARING", (3.0, Y1 - 0.07, 2.06), 0.11, "yellow", "N")
    k.box("entry side ID", (-1.55, 0.18, 2.05), (0.04, 0.9, 0.32), "dark", 0.004)
    k.text("entry side text", "CSB-01", (-1.52, 0.18, 1.98), 0.14, "white", "E")


def build_architecture():
    floor()
    walls()
    ceiling()
    door_d01()
    stairs_and_gallery()
    ceiling_services()
    practical_lights()
    signs()
