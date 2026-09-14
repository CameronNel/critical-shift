"""Original condenser, condensate, cooling-water, vacuum, operator and dressing."""
import math
from mathutils import Vector
import kit as k
from layout import *


def condenser():
    k.group("10 Condenser CD-01")
    cx, cy, cz = CD_C
    x0, x1 = cx - CD_LEN_X / 2, cx + CD_LEN_X / 2
    ry, rz = CD_WID_Y / 2, (CD_BODY_Z1 - CD_BODY_Z0) / 2
    body_c_z = (CD_BODY_Z0 + CD_BODY_Z1) / 2
    # Oval shell — not a cooling-plant cylinder clone: taller, fatter, with steam chest
    shell = k.shell_along_x("CD shell", x0, x1, cy, body_c_z, ry, rz, "cream", 32, 0)
    inlet = k.box("CD steam inlet cutter", (EXH_C[0], EXH_C[1], CD_BODY_Z1), (EXH_X - 0.12, EXH_Y - 0.12, 0.55), None, 0)
    k.boolean_cut(shell, inlet, "steam inlet")
    k.bevel(shell, 0.012)
    for i, x in enumerate((x0 + 0.35, cx, x1 - 0.35)):
        k.torus("CD stiffener", (x, cy, body_c_z), ry + 0.025, 0.028, "struct", "X")
    k.text("CD-01 paint", "CD-01", (cx, cy - ry - 0.01, body_c_z + 0.15), 0.28, "ink", "S")
    # Hotwell belly
    k.box("CD hotwell", (cx, cy, (HW_Z0 + HW_Z1) / 2), (CD_LEN_X - 0.35, CD_WID_Y - 0.25, HW_Z1 - HW_Z0), "cream", 0.02)
    k.box("CD hotwell saddle band", (cx, cy, HW_Z1 + 0.02), (CD_LEN_X - 0.2, CD_WID_Y - 0.1, 0.05), "struct", 0.004)
    # Level glasses on south hotwell
    for x in (cx - 0.55, cx + 0.55):
        k.cyl("level glass tube", (x, cy - CD_WID_Y / 2 + 0.02, (HW_Z0 + HW_Z1) / 2 + 0.15), 0.035, 0.55, "water", "Z", 16, 0.002)
        k.cyl("level glass guard", (x, cy - CD_WID_Y / 2 + 0.02, (HW_Z0 + HW_Z1) / 2 + 0.15), 0.05, 0.58, "steel", "Z", 12, 0.002)
        k.box("level glass top cock", (x, cy - CD_WID_Y / 2 + 0.02, HW_Z1 + 0.12), (0.08, 0.08, 0.08), "dark", 0.003)
        k.box("level glass bot cock", (x, cy - CD_WID_Y / 2 + 0.02, HW_Z0 + 0.08), (0.08, 0.08, 0.08), "dark", 0.003)
    # Concrete piers + saddles
    for i, x in enumerate((x0 + 0.55, x1 - 0.55)):
        k.box("CD pier", (x, cy, 0.42), (0.70, 1.15, 0.84), "concrete", 0.02)
        k.box("CD soleplate", (x, cy, 0.88), (0.78, 1.28, 0.08), "dark", 0.006)
        k.box("CD saddle", (x, cy, 1.15), (0.55, 1.05, 0.48), "struct", 0.016)
        k.box("CD saddle rib", (x, cy, 1.22), (0.12, 0.9, 0.55), "struct", 0.008)
        for dx in (-0.22, 0.22):
            for dy in (-0.38, 0.38):
                k.bolt("CD anchor", (x + dx, cy + dy, 0.94), "Z", 0.022)
        k.anchor("CD pier " + str(i), (x, cy, 0), "Structural floor")
    # Steam chest as four walls + ring flange so the 2.5 x 1.5 bore is actually open
    t, h = 0.12, 0.70
    zc = 4.95
    k.box("CD chest wall Y-", (EXH_C[0], EXH_C[1] - EXH_Y / 2 - t / 2, zc), (EXH_X + 2 * t, t, h), "cream", 0.012)
    k.box("CD chest wall Y+", (EXH_C[0], EXH_C[1] + EXH_Y / 2 + t / 2, zc), (EXH_X + 2 * t, t, h), "cream", 0.012)
    k.box("CD chest wall X-", (EXH_C[0] - EXH_X / 2 - t / 2, EXH_C[1], zc), (t, EXH_Y, h), "cream", 0.012)
    k.box("CD chest wall X+", (EXH_C[0] + EXH_X / 2 + t / 2, EXH_C[1], zc), (t, EXH_Y, h), "cream", 0.012)
    k.box("CD chest flange Y-", (EXH_C[0], EXH_C[1] - EXH_Y / 2 - 0.16, 5.28), (EXH_X + 0.55, 0.14, 0.10), "struct", 0.008)
    k.box("CD chest flange Y+", (EXH_C[0], EXH_C[1] + EXH_Y / 2 + 0.16, 5.28), (EXH_X + 0.55, 0.14, 0.10), "struct", 0.008)
    k.box("CD chest flange X-", (EXH_C[0] - EXH_X / 2 - 0.16, EXH_C[1], 5.28), (0.14, EXH_Y + 0.28, 0.10), "struct", 0.008)
    k.box("CD chest flange X+", (EXH_C[0] + EXH_X / 2 + 0.16, EXH_C[1], 5.28), (0.14, EXH_Y + 0.28, 0.10), "struct", 0.008)
    # Rectangular flange bolts
    xs = [EXH_C[0] - EXH_X / 2 - 0.18, EXH_C[0] + EXH_X / 2 + 0.18]
    ys = [EXH_C[1] - EXH_Y / 2 - 0.18, EXH_C[1] + EXH_Y / 2 + 0.18]
    for x in [EXH_C[0] + d * (EXH_X / 2 + 0.18) for d in (-1, -0.33, 0.33, 1)]:
        for y in ys:
            k.bolt("chest bolt", (x, y, 5.34), "Z", 0.018)
    for y in [EXH_C[1] + d * (EXH_Y / 2 + 0.18) for d in (-1, 1)]:
        for x in [EXH_C[0] + d * (EXH_X / 2 * 0.5) for d in (-1, 1)]:
            k.bolt("chest bolt b", (x, y, 5.34), "Z", 0.018)
    # Hollow neck + bellows (four walls / rings, not a solid plug)
    def _duct_walls(prefix, z, h, wall, mat, extra=0.0):
        k.box(prefix + " Y-", (EXH_C[0], EXH_C[1] - EXH_Y / 2 - wall / 2, z), (EXH_X + extra + 2 * wall, wall, h), mat, 0.006)
        k.box(prefix + " Y+", (EXH_C[0], EXH_C[1] + EXH_Y / 2 + wall / 2, z), (EXH_X + extra + 2 * wall, wall, h), mat, 0.006)
        k.box(prefix + " X-", (EXH_C[0] - EXH_X / 2 - wall / 2, EXH_C[1], z), (wall, EXH_Y + extra, h), mat, 0.006)
        k.box(prefix + " X+", (EXH_C[0] + EXH_X / 2 + wall / 2, EXH_C[1], z), (wall, EXH_Y + extra, h), mat, 0.006)

    _duct_walls("CD neck lower", 5.48, 0.22, 0.08, "cream", 0.04)
    for i, z in enumerate((5.62, 5.70, 5.78, 5.86)):
        _duct_walls("bellow " + str(i), z, 0.04, 0.05, "steel", 0.16)
    _duct_walls("CD neck upper", 5.95, 0.10, 0.07, "cream", 0.02)
    _duct_walls("CD mating flange", 5.995, 0.05, 0.10, "struct", 0.18)
    k.empty("IF_LP_EXHAUST_CONDENSER", EXH_C, "2.5 x 1.5 m receive of turbine U04; scenic mating only")
    # Atmospheric relief / vacuum breaker mushroom
    k.cyl("CD relief neck", (cx + 1.15, cy + 0.55, CD_BODY_Z1 + 0.12), 0.09, 0.22, "steel", "Z", 24)
    k.cyl("CD relief disc", (cx + 1.15, cy + 0.55, CD_BODY_Z1 + 0.28), 0.18, 0.05, "burgundy", "Z", 24)
    k.cyl("CD relief cap", (cx + 1.15, cy + 0.55, CD_BODY_Z1 + 0.34), 0.14, 0.06, "burgundy", "Z", 24)
    k.text("relief tag", "VAC BRK", (cx + 1.15, cy + 0.72, CD_BODY_Z1 + 0.18), 0.06, "white", "S")
    # Waterboxes
    _waterbox("west", x0, -1, cx, cy, body_c_z, ry, rz)
    _waterbox("east", x1, 1, cx, cy, body_c_z, ry, rz)
    # Inspection hatches on south shell
    for x in (cx - 0.85, cx + 0.85):
        k.cyl("CD hatch", (x, cy - ry + 0.02, body_c_z - 0.15), 0.22, 0.06, "oxide", "Y", 24, 0.008)
        k.cyl("CD hatch glass", (x, cy - ry - 0.01, body_c_z - 0.15), 0.12, 0.02, "glass", "Y", 20)
        for i in range(8):
            a = i * math.tau / 8
            k.bolt("hatch bolt", (x + 0.18 * math.cos(a), cy - ry + 0.04, body_c_z - 0.15 + 0.18 * math.sin(a)), "Y", 0.012)
    # Nameplate
    k.box("CD nameplate", (cx, cy - ry - 0.03, body_c_z - 0.55), (0.55, 0.02, 0.22), "dark", 0.003)
    k.text("CD nameplate text", "CD-01  SURFACE", (cx, cy - ry - 0.045, body_c_z - 0.52), 0.07, "white", "S")
    k.text("CD nameplate text2", "SCENIC  /  NO RATING", (cx, cy - ry - 0.045, body_c_z - 0.62), 0.055, "yellow", "S")
    # Air offtake from shell top to ejectors
    k.cyl("air offtake nozzle", (cx - 1.2, cy + 0.4, CD_BODY_Z1 + 0.06), 0.08, 0.14, "steel", "Z", 20)
    k.hook("INTERACT_CD_ISOLATE", (x0 - 0.35, cy, body_c_z), "isolate_cooling_waterbox", "CD-01")


def _waterbox(side, x_face, sign, cx, cy, cz, ry, rz):
    x = x_face + sign * (WB_DEPTH / 2)
    k.box(f"WB {side} body", (x, cy, cz), (WB_DEPTH, CD_WID_Y - 0.15, (CD_BODY_Z1 - CD_BODY_Z0) - 0.25), "oxide", 0.018)
    k.box(f"WB {side} tubesheet ring", (x_face, cy, cz), (0.08, CD_WID_Y - 0.05, CD_BODY_Z1 - CD_BODY_Z0 - 0.1), "steel", 0.008)
    # Bolted cover
    k.box(f"WB {side} cover", (x + sign * (WB_DEPTH / 2 + 0.03), cy, cz), (0.07, CD_WID_Y - 0.28, (CD_BODY_Z1 - CD_BODY_Z0) - 0.45), "oxide_light", 0.01)
    k.box(f"WB {side} gasket lip", (x + sign * (WB_DEPTH / 2 + 0.01), cy, cz), (0.03, CD_WID_Y - 0.20, (CD_BODY_Z1 - CD_BODY_Z0) - 0.35), "rubber", 0.002)
    for dy in (-0.85, -0.42, 0.0, 0.42, 0.85):
        for dz in (-0.95, -0.32, 0.32, 0.95):
            k.bolt(f"WB {side} cover bolt", (x + sign * (WB_DEPTH / 2 + 0.08), cy + dy, cz + dz), "X", 0.016)
    # Manway
    k.cyl(f"WB {side} manway", (x + sign * (WB_DEPTH / 2 + 0.05), cy, cz + 0.15), 0.22, 0.08, "dark", "X", 24, 0.008)
    k.cyl(f"WB {side} manway lid", (x + sign * (WB_DEPTH / 2 + 0.10), cy, cz + 0.15), 0.20, 0.05, "struct", "X", 24, 0.006)
    # Davit for cover
    k.cyl(f"WB {side} davit post", (x + sign * 0.05, cy + ry - 0.15, CD_BODY_Z1 + 0.25), 0.04, 0.7, "yellow", "Z", 16)
    k.cyl(f"WB {side} davit arm", (x + sign * 0.28, cy + ry - 0.15, CD_BODY_Z1 + 0.55), 0.035, 0.55, "yellow", "X", 16)
    k.torus(f"WB {side} davit eye", (x + sign * 0.48, cy + ry - 0.15, CD_BODY_Z1 + 0.48), 0.05, 0.012, "yellow", "Y")
    # Vent / drain
    k.cyl(f"WB {side} vent", (x, cy - 0.6, CD_BODY_Z1 - 0.15), 0.04, 0.16, "steel", "Z", 12)
    k.wheel(f"WB {side} vent wheel", (x, cy - 0.6, CD_BODY_Z1 + 0.02), 0.09, "Z", "yellow")
    k.cyl(f"WB {side} drain", (x, cy + 0.55, CD_BODY_Z0 + 0.22), 0.035, 0.12, "steel", "Z", 12)


def condensate_pumps():
    k.group("11 Condensate pumps")
    for name, px, py in (("CEP-A", P1[0], P1[1]), ("CEP-B", P2[0], P2[1])):
        _cep(name, px, py)
    # Common discharge header toward south-east handoff
    k.pipe(
        "CEP discharge header",
        [
            (P1[0] + 0.15, P1[1], 1.85),
            (P1[0] + 0.15, P1[1], 2.35),
            (6.4, P1[1], 2.35),
            (6.4, P2[1], 2.35),
            (P2[0] + 0.15, P2[1], 2.35),
        ],
        0.055,
        "cream",
        0.16,
    )
    k.pipe(
        "condensate riser",
        [
            (6.4, 7.6, 2.35),
            (6.4, 7.6, 5.42),
            (IF_CONDENSATE_HANDOFF[0], 7.6, 5.42),
            (IF_CONDENSATE_HANDOFF[0], IF_CONDENSATE_HANDOFF[1] + 0.12, 5.42),
        ],
        0.055,
        "cream",
        0.18,
    )
    k.flange("IF_CONDENSATE_HANDOFF flange", (IF_CONDENSATE_HANDOFF[0], 0.08, 5.42), 0.14, "Y", "steel", 8, 0.06)
    k.cyl("condensate blind", (IF_CONDENSATE_HANDOFF[0], 0.02, 5.42), 0.12, 0.04, "dark", "Y", 24)
    k.box("handoff tag", (IF_CONDENSATE_HANDOFF[0], 0.16, 5.62), (0.42, 0.03, 0.12), "dark", 0.003)
    k.text("handoff tag text", "TO TURBINE U02", (IF_CONDENSATE_HANDOFF[0], 0.18, 5.58), 0.06, "yellow", "S")
    k.empty("IF_CONDENSATE_HANDOFF", IF_CONDENSATE_HANDOFF, "0.2 m class liquid return; turbine U02 cap remains turbine-owned")
    k.rod("riser hang A", (6.4, 7.6, 5.5), (6.4, 7.6, 5.998), 0.012, "steel")
    k.rod("riser hang B", (IF_CONDENSATE_HANDOFF[0], 1.4, 5.5), (IF_CONDENSATE_HANDOFF[0], 1.4, 5.998), 0.012, "steel")
    k.anchor("riser hang A", (6.4, 7.6, 5.985), "Ceiling slab", (0, 0, 1), 0.02, 0.006)
    k.anchor("riser hang B", (IF_CONDENSATE_HANDOFF[0], 1.4, 5.985), "Ceiling slab", (0, 0, 1), 0.02, 0.006)


def _cep(name, x, y):
    z = 0.95
    k.box(name + " skid", (x, y, 0.08), (1.55, 0.85, 0.16), "dark", 0.008)
    k.box(name + " drip", (x, y, 0.17), (1.48, 0.78, 0.04), "steel", 0.004)
    for dx, dy in ((-0.6, -0.28), (-0.6, 0.28), (0.55, -0.28), (0.55, 0.28)):
        k.cyl(name + " anchor", (x + dx, y + dy, 0.04), 0.04, 0.08, "steel", "Z", 6, 0.002)
        k.anchor(name + f" ft{dx}", (x + dx, y + dy, 0), "Structural floor")
    # Cast volute, spiral, shaft along +X (discharge up)
    vs = []
    n = 56
    cx = x - 0.28
    for xx in (cx - 0.16, cx + 0.16):
        for i in range(n):
            t = i / (n - 1)
            a = -math.pi / 2 + math.tau * t
            r = 0.28 + 0.14 * t
            vs.append((xx, y + math.cos(a) * r, z + math.sin(a) * r))
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [
        (i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)
    ]
    k.mesh(name + " volute", vs, faces, "oxide", 0.02, True)
    k.cyl(name + " cover", (cx + 0.18, y, z), 0.26, 0.06, "oxide_light", "X", 40, 0.012)
    for i in range(8):
        a = i * math.tau / 8
        k.bolt(name + " cover stud", (cx + 0.22, y + math.cos(a) * 0.21, z + math.sin(a) * 0.21), "X", 0.014)
    k.box(name + " foot L", (cx, y - 0.22, 0.42), (0.28, 0.14, 0.5), "oxide", 0.012)
    k.box(name + " foot R", (cx, y + 0.22, 0.42), (0.28, 0.14, 0.5), "oxide", 0.012)
    k.cyl(name + " suction", (cx, y, z - 0.42), 0.09, 0.22, "steel", "Z", 24, 0.006)
    k.pipe(
        name + " suction line",
        [(cx, y, z - 0.52), (cx, y, 0.55), (CD_C[0] + (0.4 if "A" in name else -0.4), y, 0.55), (CD_C[0] + (0.4 if "A" in name else -0.4), CD_C[1] + 0.9, 0.55), (CD_C[0] + (0.4 if "A" in name else -0.4), CD_C[1] + 0.55, HW_Z0 + 0.12)],
        0.07,
        "cream",
        0.14,
    )
    k.cyl(name + " discharge nozzle", (cx, y, z + 0.42), 0.07, 0.18, "steel", "Z", 24)
    k.flange(name + " disch fl", (cx, y, z + 0.55), 0.12, "Z", "steel", 8, 0.05)
    k.wheel(name + " isol", (cx + 0.22, y, 1.55), 0.13, "X", "yellow")
    k.cyl(name + " isol stem", (cx, y, 1.55), 0.025, 0.28, "steel", "X", 12)
    # Coupling + guard + motor
    k.cyl(name + " shaft", (x + 0.05, y, z), 0.045, 0.28, "steel", "X", 24)
    k.cyl(name + " coupling", (x + 0.18, y, z), 0.09, 0.10, "dark", "X", 20, 0.008)
    for i in range(10):
        a = math.pi * i / 9
        k.rod(name + " guard bar", (x + 0.02, y + 0.16 * math.cos(a), z + 0.16 * math.sin(a)), (x + 0.34, y + 0.16 * math.cos(a), z + 0.16 * math.sin(a)), 0.006, "yellow")
    k.cyl(name + " motor", (x + 0.62, y, z), 0.22, 0.72, "struct", "X", 40, 0.018)
    for i in range(16):
        a = i * math.tau / 16
        o = k.box(name + " fin", (x + 0.62, y + math.cos(a) * 0.225, z + math.sin(a) * 0.225), (0.55, 0.012, 0.055), "struct", 0.002)
        o.rotation_euler.x = a - math.pi / 2
    k.cyl(name + " end bell", (x + 0.98, y, z), 0.20, 0.08, "steel", "X", 32, 0.01)
    k.cyl(name + " fan guard", (x + 1.04, y, z), 0.18, 0.04, "dark", "X", 24)
    k.box(name + " terminal", (x + 0.62, y, z + 0.28), (0.28, 0.18, 0.12), "dark", 0.008)
    k.pipe(name + " motor feed", [(x + 0.62, y, z + 0.35), (x + 0.62, y, 5.38), (-0.72, y, 5.38)], 0.016, "rubber", 0.12)
    k.box(name + " motor foot", (x + 0.62, y, 0.48), (0.55, 0.36, 0.12), "dark", 0.008)
    k.box(name + " ID plate", (x + 0.62, y - 0.23, z), (0.28, 0.02, 0.10), "dark", 0.002)
    k.text(name + " ID", name, (x + 0.62, y - 0.245, z - 0.02), 0.07, "white", "S")
    k.box(name + " floor ID", (x, y - 0.55, 0.02), (0.55, 0.12, 0.03), "dark", 0.003)
    k.text(name + " floor IDt", name, (x, y - 0.55, 0.04), 0.08, "white", "UP")
    k.hook("INTERACT_" + name, (x + 0.22, y - 0.45, 1.15), "start_stop_cep", name)


def cooling_water():
    k.group("12 Cooling water")
    # East-wall headers, isolation, drops to waterboxes
    k.pipe(
        "CW supply header",
        [
            IF_CW_SUPPLY,
            (8.55, 3.20, 3.15),
            (8.55, CD_C[1], 3.15),
            (CD_C[0] + CD_LEN_X / 2 + WB_DEPTH + 0.18, CD_C[1], 3.15),
        ],
        0.09,
        "cream",
        0.16,
    )
    k.pipe(
        "CW return header",
        [
            IF_CW_RETURN,
            (8.55, 4.90, 3.15),
            (8.55, 5.75, 3.15),
            (CD_C[0] - CD_LEN_X / 2 - WB_DEPTH - 0.18, 5.75, 3.15),
            (CD_C[0] - CD_LEN_X / 2 - WB_DEPTH - 0.18, CD_C[1], 3.15),
        ],
        0.09,
        "cream",
        0.16,
    )
    k.cyl("CW east nozzle", (CD_C[0] + CD_LEN_X / 2 + WB_DEPTH + 0.08, CD_C[1], 3.15), 0.10, 0.18, "steel", "X", 24, 0.006)
    k.flange("CW east nozzle fl", (CD_C[0] + CD_LEN_X / 2 + WB_DEPTH + 0.16, CD_C[1], 3.15), 0.14, "X", "steel", 8, 0.05)
    k.cyl("CW west nozzle", (CD_C[0] - CD_LEN_X / 2 - WB_DEPTH - 0.08, CD_C[1], 3.15), 0.10, 0.18, "steel", "X", 24, 0.006)
    k.flange("CW west nozzle fl", (CD_C[0] - CD_LEN_X / 2 - WB_DEPTH - 0.16, CD_C[1], 3.15), 0.14, "X", "steel", 8, 0.05)
    k.flange("CW supply wall flange", (X1 - 0.04, 3.20, 3.15), 0.16, "X", "steel", 10, 0.07)
    k.flange("CW return wall flange", (X1 - 0.04, 4.90, 3.15), 0.16, "X", "steel", 10, 0.07)
    k.cyl("CW supply cap", (X1 + 0.06, 3.20, 3.15), 0.14, 0.05, "dark", "X", 24)
    k.cyl("CW return cap", (X1 + 0.06, 4.90, 3.15), 0.14, 0.05, "dark", "X", 24)
    k.empty("IF_CW_SUPPLY", IF_CW_SUPPLY, "provisional CW supply; remote cooling-plant bind unbound")
    k.empty("IF_CW_RETURN", IF_CW_RETURN, "provisional CW return; remote cooling-plant bind unbound")
    for y, tag in ((3.20, "SUPPLY"), (4.90, "RETURN")):
        k.box("CW tag " + tag, (X1 - 0.08, y, 3.42), (0.03, 0.55, 0.12), "dark", 0.003)
        k.text("CW tag t " + tag, "CW " + tag, (X1 - 0.10, y, 3.38), 0.07, "yellow", "W")
        k.wheel("CW isol " + tag, (8.15, y, 3.15), 0.16, "Y", "yellow")
        k.cyl("CW isol body " + tag, (8.15, y, 3.15), 0.11, 0.18, "steel", "X", 20)
        k.gauge("CW gauge " + tag, (7.55, y, 3.42), "Y", 0.09)
    for x, y in ((8.6, 3.20), (8.6, 4.90), (5.55, 3.20), (5.55, 4.90)):
        k.torus("CW clamp", (x, y, 3.15), 0.12, 0.012, "steel", "X")
        k.rod("CW hang", (x, y, 3.28), (x, y, 5.998), 0.012, "steel")
        k.anchor("CW hang " + f"{x:.1f}_{y:.1f}", (x, y, 5.985), "Ceiling slab", (0, 0, 1), 0.02, 0.006)
    k.hook("INTERACT_CW_ISOL_S", (8.15, 3.20, 3.15), "isolate_cw_supply", "CW")
    k.hook("INTERACT_CW_ISOL_R", (8.15, 4.90, 3.15), "isolate_cw_return", "CW")


def vacuum_ejectors():
    k.group("13 Vacuum ejectors")
    x, y, z = EJ_C
    k.box("EJ skid", (x, y, 0.08), (1.15, 1.55, 0.16), "dark", 0.008)
    k.anchor("EJ skid", (x, y, 0), "Structural floor")
    # Two-stage stacked ejectors with intercondenser — distinctive vertical silhouette
    k.cyl("EJ1 body", (x - 0.22, y - 0.35, 1.15), 0.16, 1.10, "struct", "Z", 32, 0.014)
    k.cyl("EJ1 nozzle", (x - 0.22, y - 0.35, 1.78), 0.09, 0.22, "steel", "Z", 20)
    k.cyl("EJ1 diffuser", (x - 0.22, y - 0.35, 0.62), 0.12, 0.28, "steel", "Z", 20)
    k.cyl("EJ2 body", (x - 0.22, y + 0.35, 1.55), 0.14, 1.35, "struct", "Z", 32, 0.014)
    k.cyl("EJ2 nozzle", (x - 0.22, y + 0.35, 2.28), 0.08, 0.18, "steel", "Z", 20)
    k.cyl("EJ2 diffuser", (x - 0.22, y + 0.35, 0.85), 0.10, 0.24, "steel", "Z", 20)
    k.cyl("EJ intercondenser", (x + 0.28, y, 1.35), 0.22, 0.85, "cream", "Z", 28, 0.016)
    k.torus("EJ inter band", (x + 0.28, y, 1.35), 0.23, 0.025, "struct", "Z")
    k.text("EJ ID", "EJ-01", (x + 0.28, y - 0.24, 1.35), 0.09, "ink", "S")
    k.pipe(
        "EJ air suction",
        [(CD_C[0] - 1.2, CD_C[1] + 0.4, CD_BODY_Z1 + 0.14), (CD_C[0] - 1.2, CD_C[1] + 0.4, 4.85), (x - 0.22, CD_C[1] + 0.4, 4.85), (x - 0.22, y - 0.35, 4.85), (x - 0.22, y - 0.35, 1.90)],
        0.045,
        "cream",
        0.16,
    )
    k.pipe("EJ interstage", [(x - 0.22, y - 0.35, 0.48), (x + 0.28, y - 0.35, 0.48), (x + 0.28, y, 0.48), (x + 0.28, y, 0.95)], 0.04, "cream", 0.12)
    k.pipe("EJ2 suction", [(x + 0.28, y, 1.78), (x + 0.28, y + 0.35, 1.78), (x - 0.22, y + 0.35, 1.78), (x - 0.22, y + 0.35, 2.18)], 0.04, "cream", 0.1)
    k.pipe(
        "EJ exhaust",
        [(x - 0.22, y + 0.35, 0.72), (x - 0.22, y + 0.55, 0.72), (x - 0.22, y + 0.55, 5.55), (IF_VENT_OUT[0], y + 0.55, 5.55), (IF_VENT_OUT[0], IF_VENT_OUT[1] - 0.15, 5.55)],
        0.05,
        "cream",
        0.16,
    )
    k.wheel("EJ steam isol", (x - 0.55, y, 2.15), 0.12, "X", "yellow")
    k.box("EJ steam manifold", (x - 0.48, y, 2.15), (0.18, 0.85, 0.16), "cream", 0.008)
    k.gauge("EJ vacuum gauge", (x + 0.52, y, 1.85), "X", 0.1)
    k.box("EJ local panel", (X0 + 0.12, y, 1.45), (0.08, 0.55, 0.7), "dark", 0.008)
    k.hook("INTERACT_EJ", (x - 0.55, y, 2.15), "isolate_ejector_steam", "EJ-01")


def operator_station():
    k.group("14 Operator station")
    x, y, z = OP_C
    k.box("OP enclosure", (X0 + 0.18, y, 1.42), (0.32, 1.55, 1.35), "dark", 0.014)
    k.box("OP face", (X0 + 0.36, y, 1.42), (0.06, 1.42, 1.22), "struct", 0.008)
    k.box("OP kick", (X0 + 0.28, y, 0.12), (0.36, 1.5, 0.22), "struct", 0.006)
    k.box("OP desk", (X0 + 0.62, y, 0.92), (0.50, 0.78, 0.05), "wood", 0.008)
    k.box("OP desk leg L", (X0 + 0.52, y - 0.30, 0.46), (0.05, 0.05, 0.88), "dark", 0.003)
    k.box("OP desk leg R", (X0 + 0.52, y + 0.30, 0.46), (0.05, 0.05, 0.88), "dark", 0.003)
    labels = [("VAC", 0.42), ("LEVEL", 0.14), ("CW IN", -0.14), ("FLOW", -0.42)]
    for lab, dy in labels:
        k.gauge("OP " + lab, (X0 + 0.44, y + dy, 1.88), "X", 0.115)
        k.text("OP " + lab + " t", lab, (X0 + 0.41, y + dy, 1.70), 0.05, "white", "E")
    for i, dy in enumerate((0.36, 0.12, -0.12, -0.36)):
        k.cyl("OP switch body", (X0 + 0.40, y + dy, 1.22), 0.028, 0.05, "steel", "X", 16)
        k.cyl("OP switch knob", (X0 + 0.46, y + dy, 1.22), 0.02, 0.045, "yellow" if i == 0 else "dark", "X", 12)
        k.box("OP guard L", (X0 + 0.40, y + dy - 0.048, 1.22), (0.05, 0.012, 0.11), "yellow", 0.002)
        k.box("OP guard R", (X0 + 0.40, y + dy + 0.048, 1.22), (0.05, 0.012, 0.11), "yellow", 0.002)
        k.box("OP guard top", (X0 + 0.42, y + dy, 1.275), (0.06, 0.10, 0.012), "yellow", 0.002)
    k.box("OP trip bezel", (X0 + 0.38, y, 1.00), (0.04, 0.09, 0.09), "dark", 0.004)
    k.cyl("OP trip stem", (X0 + 0.42, y, 1.00), 0.018, 0.05, "red", "X", 12)
    k.cyl("OP trip mushroom", (X0 + 0.46, y, 1.00), 0.038, 0.028, "red", "X", 16)
    k.text("OP title", "CSB-01  CONDENSER", (X0 + 0.38, y, 2.12), 0.08, "white", "E")
    k.text("OP subtitle", "VACUUM  /  CEP  /  CW", (X0 + 0.38, y, 2.00), 0.055, "yellow", "E")
    k.box("OP clipboard", (X0 + 0.55, y + 0.12, 0.96), (0.22, 0.16, 0.01), "paper", 0.001)
    k.cyl("OP mug", (X0 + 0.68, y - 0.22, 1.00), 0.035, 0.09, "burgundy", "Z", 20, 0.006)
    k.torus("OP mug handle", (X0 + 0.72, y - 0.22, 1.00), 0.028, 0.008, "burgundy", "Y")
    k.hook("INTERACT_CSB_VACUUM", (X0 + 0.45, y + 0.28, 1.22), "set_vacuum_mode", "OP")
    k.hook("INTERACT_CSB_TRIP", (X0 + 0.45, y, 1.02), "vacuum_trip", "OP")
    k.hook("INTERACT_CSB_CEP", (X0 + 0.45, y - 0.08, 1.22), "cep_select", "OP")


def drainage_and_hoist():
    k.group("15 Drainage and hoist")
    x, y, _ = SUMP_C
    k.box("sump pit", (x, y, -0.12), (0.85, 0.85, 0.28), "dark", 0.008)
    k.box("sump grate A", (x - 0.2, y, 0.01), (0.38, 0.78, 0.02), "steel", 0.003)
    k.box("sump grate B", (x + 0.2, y, 0.01), (0.38, 0.78, 0.02), "steel", 0.003)
    k.cyl("sump pump", (x, y, 0.22), 0.09, 0.28, "oxide", "Z", 20, 0.008)
    k.cyl("sump motor", (x, y, 0.48), 0.08, 0.18, "struct", "Z", 16)
    k.pipe("sump discharge", [(x, y, 0.58), (x, y, 1.15), (IF_DRAIN_OUT[0] - 0.2, y, 1.15), (IF_DRAIN_OUT[0] - 0.05, y, IF_DRAIN_OUT[2] + 0.4)], 0.03, "cream", 0.1)
    k.empty("IF_DRAIN_OUT", IF_DRAIN_OUT, "local drain; remote destination unbound")
    k.box("floor drip pan CD", (CD_C[0], CD_C[1], 0.02), (CD_LEN_X + 1.3, CD_WID_Y + 0.8, 0.015), "dark", 0.003)
    # Yellow hoist over east waterbox / bundle
    k.i_beam("hoist beam", (5.1, 4.05, 5.35), (9.2, 4.05, 5.35), 0.16, 0.24, "yellow")
    k.box("hoist trolley", (6.4, 4.05, 5.18), (0.28, 0.22, 0.16), "dark", 0.008)
    k.box("hoist gearbox", (6.4, 4.05, 4.95), (0.22, 0.18, 0.22), "yellow", 0.01)
    k.cyl("hoist hook shank", (6.4, 4.05, 4.72), 0.02, 0.28, "steel", "Z", 10)
    k.torus("hoist hook", (6.4, 4.05, 4.55), 0.07, 0.018, "steel", "Y")
    k.rod("hoist hang L", (5.3, 4.05, 5.48), (5.3, 4.05, 5.998), 0.014, "steel")
    k.rod("hoist hang R", (8.9, 4.05, 5.48), (8.9, 4.05, 5.998), 0.014, "steel")
    k.anchor("hoist L", (5.3, 4.05, 5.985), "Ceiling slab", (0, 0, 1), 0.02, 0.006)
    k.anchor("hoist R", (8.9, 4.05, 5.985), "Ceiling slab", (0, 0, 1), 0.02, 0.006)
    k.hook("INTERACT_HOIST", (6.4, 3.55, 1.2), "position_bundle_hoist", "HOIST")


def dressing():
    k.group("16 Maintenance dressing")
    # Tool cart in west aisle north of operator, out of the 0.8 m cart route
    k.box("cart deck", (-0.95, 5.55, 0.72), (0.55, 0.85, 0.05), "steel", 0.006)
    k.box("cart shelf", (-0.95, 5.55, 0.32), (0.50, 0.80, 0.03), "dark", 0.004)
    for dx, dy in ((-0.2, -0.32), (-0.2, 0.32), (0.2, -0.32), (0.2, 0.32)):
        k.cyl("cart wheel", (-0.95 + dx, 5.55 + dy, 0.08), 0.06, 0.04, "rubber", "X", 16)
        k.cyl("cart caster", (-0.95 + dx, 5.55 + dy, 0.14), 0.02, 0.12, "steel", "Z", 8)
    k.box("wrench", (-0.95, 5.40, 0.76), (0.28, 0.05, 0.03), "steel", 0.004)
    k.box("gasket crate", (-0.95, 5.70, 0.42), (0.28, 0.22, 0.16), "wood", 0.006)
    k.box("spare gasket", (-0.95, 5.70, 0.52), (0.18, 0.18, 0.03), "rubber", 0.002)
    # PPE hooks south-west
    k.box("PPE rail", (-1.55, 1.55, 1.55), (0.04, 0.55, 0.04), "steel", 0.002)
    k.box("hardhat", (-1.52, 1.40, 1.42), (0.18, 0.16, 0.10), "yellow", 0.01)
    k.box("glove L", (-1.50, 1.62, 1.38), (0.08, 0.12, 0.04), "oxide", 0.004)
    k.box("glove R", (-1.50, 1.72, 1.38), (0.08, 0.12, 0.04), "oxide", 0.004)
    # Extinguisher
    k.cyl("ext body", (0.95, 0.35, 0.55), 0.08, 0.55, "red", "Z", 20, 0.01)
    k.box("ext bracket", (0.95, 0.28, 0.70), (0.04, 0.06, 0.35), "steel", 0.003)
    k.cyl("ext head", (0.95, 0.35, 0.86), 0.05, 0.08, "dark", "Z", 12)
    k.box("ext hose", (0.95, 0.42, 0.70), (0.03, 0.12, 0.03), "rubber", 0.002)
    # Shift log on north wall
    k.box("log clipboard", (1.15, Y1 - 0.04, 1.55), (0.28, 0.02, 0.38), "paper", 0.002)
    k.text("log title", "SHIFT LOG", (1.15, Y1 - 0.06, 1.68), 0.07, "ink", "N")
    k.box("log clip", (1.15, Y1 - 0.05, 1.72), (0.12, 0.03, 0.04), "steel", 0.002)
    # Tool cabinet east of pumps
    k.box("cabinet body", (5.55, 8.55, 0.85), (0.42, 0.70, 1.70), "struct", 0.012)
    k.box("cabinet door", (5.32, 8.55, 0.90), (0.04, 0.62, 1.50), "dark", 0.006)
    k.cyl("cabinet handle", (5.29, 8.38, 0.90), 0.015, 0.12, "steel", "Z", 8)
    k.box("cabinet ID", (5.32, 8.55, 1.65), (0.02, 0.35, 0.10), "dark", 0.002)
    k.text("cabinet IDt", "TOOLS", (5.30, 8.55, 1.62), 0.07, "white", "W")
    # Cone at pull-bay limit
    k.cyl("cone body", (6.35, 1.55, 0.22), 0.08, 0.42, "oxide", "Z", 16, 0.008)
    k.cyl("cone stripe", (6.35, 1.55, 0.28), 0.082, 0.06, "white", "Z", 16)
    k.box("no storage stencil", (7.7, 6.4, 0.014), (1.8, 0.25, 0.002), "ink", 0.001)


def build_equipment():
    condenser()
    condensate_pumps()
    cooling_water()
    vacuum_ejectors()
    operator_station()
    drainage_and_hoist()
    dressing()
