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
        k.torus("CD stiffener", (x, cy, body_c_z), ry + 0.03, 0.034, "cream", "X")
    k.text("CD-01 paint", "CD-01", (cx, cy - ry - 0.01, body_c_z + 0.15), 0.28, "ink", "S")
    # Hotwell belly
    k.box("CD hotwell", (cx, cy, (HW_Z0 + HW_Z1) / 2), (CD_LEN_X - 0.35, CD_WID_Y - 0.25, HW_Z1 - HW_Z0), "cream", 0.02)
    k.box("CD hotwell saddle band", (cx, cy, HW_Z1 + 0.02), (CD_LEN_X - 0.2, CD_WID_Y - 0.1, 0.05), "struct", 0.004)
    # Level glasses on south hotwell — large enough to read from C02/C03
    for x in (cx - 0.62, cx + 0.62):
        gy = cy - CD_WID_Y / 2 - 0.04
        k.cyl("level glass tube", (x, gy, (HW_Z0 + HW_Z1) / 2), 0.045, 0.62, "water", "Z", 16, 0.002)
        k.cyl("level glass guard", (x, gy, (HW_Z0 + HW_Z1) / 2), 0.062, 0.66, "steel", "Z", 12, 0.002)
        k.box("level glass top cock", (x, gy, HW_Z1 + 0.14), (0.09, 0.09, 0.09), "dark", 0.003)
        k.box("level glass bot cock", (x, gy, HW_Z0 + 0.06), (0.09, 0.09, 0.09), "dark", 0.003)
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
    # Steam chest as four walls so the 2.5 x 1.5 bore is open. Short so gallery can see bellows.
    t, h = 0.10, 0.52
    zc = 4.88
    k.box("CD chest wall Y-", (EXH_C[0], EXH_C[1] - EXH_Y / 2 - t / 2, zc), (EXH_X + 2 * t, t, h), "cream", 0.010)
    k.box("CD chest wall Y+", (EXH_C[0], EXH_C[1] + EXH_Y / 2 + t / 2, zc), (EXH_X + 2 * t, t, h), "cream", 0.010)
    k.box("CD chest wall X-", (EXH_C[0] - EXH_X / 2 - t / 2, EXH_C[1], zc), (t, EXH_Y, h), "cream", 0.010)
    k.box("CD chest wall X+", (EXH_C[0] + EXH_X / 2 + t / 2, EXH_C[1], zc), (t, EXH_Y, h), "cream", 0.010)
    k.box("CD chest flange Y-", (EXH_C[0], EXH_C[1] - EXH_Y / 2 - 0.14, 5.16), (EXH_X + 0.48, 0.12, 0.08), "struct", 0.006)
    k.box("CD chest flange Y+", (EXH_C[0], EXH_C[1] + EXH_Y / 2 + 0.14, 5.16), (EXH_X + 0.48, 0.12, 0.08), "struct", 0.006)
    k.box("CD chest flange X-", (EXH_C[0] - EXH_X / 2 - 0.14, EXH_C[1], 5.16), (0.12, EXH_Y + 0.24, 0.08), "struct", 0.006)
    k.box("CD chest flange X+", (EXH_C[0] + EXH_X / 2 + 0.14, EXH_C[1], 5.16), (0.12, EXH_Y + 0.24, 0.08), "struct", 0.006)
    ys = [EXH_C[1] - EXH_Y / 2 - 0.16, EXH_C[1] + EXH_Y / 2 + 0.16]
    for x in [EXH_C[0] + d * (EXH_X / 2 + 0.16) for d in (-1, -0.33, 0.33, 1)]:
        for y in ys:
            k.bolt("chest bolt", (x, y, 5.22), "Z", 0.016)
    # Open rectangular frames (not solid duct walls) so the 2.5 x 1.5 hole is visible from the gallery.
    def _rect_frame(prefix, z, h, lip, mat):
        k.box(prefix + " Y-", (EXH_C[0], EXH_C[1] - EXH_Y / 2 - lip / 2, z), (EXH_X + 2 * lip, lip, h), mat, 0.004)
        k.box(prefix + " Y+", (EXH_C[0], EXH_C[1] + EXH_Y / 2 + lip / 2, z), (EXH_X + 2 * lip, lip, h), mat, 0.004)
        k.box(prefix + " X-", (EXH_C[0] - EXH_X / 2 - lip / 2, EXH_C[1], z), (lip, EXH_Y, h), mat, 0.004)
        k.box(prefix + " X+", (EXH_C[0] + EXH_X / 2 + lip / 2, EXH_C[1], z), (lip, EXH_Y, h), mat, 0.004)

    _rect_frame("CD neck lower", 5.28, 0.10, 0.08, "cream")
    for i, z in enumerate((5.42, 5.54, 5.66, 5.78)):
        _rect_frame("bellow " + str(i), z, 0.035, 0.11 + 0.02 * (i % 2), "steel")
    _rect_frame("CD neck upper", 5.90, 0.08, 0.07, "cream")
    _rect_frame("CD mating flange", 5.985, 0.05, 0.12, "struct")
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
    # Jacketed box matching the shell, not a second orange cube.
    k.box(f"WB {side} body", (x, cy, cz), (WB_DEPTH, CD_WID_Y - 0.15, (CD_BODY_Z1 - CD_BODY_Z0) - 0.25), "cream", 0.016)
    k.box(f"WB {side} shell flange", (x_face + sign * 0.04, cy, cz), (0.10, CD_WID_Y - 0.08, (CD_BODY_Z1 - CD_BODY_Z0) - 0.18), "struct", 0.008)
    k.cyl(f"WB {side} tubesheet", (x_face, cy, cz), 1.05, 0.07, "iron", "X", 48, 0.008)
    face = x + sign * (WB_DEPTH / 2 + 0.05)
    k.cyl(f"WB {side} cover flange", (face - sign * 0.02, cy, cz), 1.02, 0.08, "steel", "X", 48, 0.010)
    k.cyl(f"WB {side} round cover", (face, cy, cz), 0.90, 0.08, "struct", "X", 48, 0.012)
    k.cyl(f"WB {side} gasket ring", (face - sign * 0.05, cy, cz), 0.88, 0.025, "rubber", "X", 40, 0.002)
    for i in range(16):
        a = i * math.tau / 16
        k.bolt(
            f"WB {side} cover bolt",
            (face + sign * 0.05, cy + 0.92 * math.cos(a), cz + 0.92 * math.sin(a)),
            "X",
            0.018,
        )
    k.cyl(f"WB {side} manway lid", (face + sign * 0.05, cy, cz + 0.10), 0.20, 0.045, "dark", "X", 24, 0.006)
    for i in range(8):
        a = i * math.tau / 8
        k.bolt(
            f"WB {side} manway bolt",
            (face + sign * 0.08, cy + 0.16 * math.cos(a), cz + 0.10 + 0.16 * math.sin(a)),
            "X",
            0.012,
        )
    k.cyl(f"WB {side} davit post", (x + sign * 0.05, cy + ry - 0.15, CD_BODY_Z1 + 0.25), 0.04, 0.7, "yellow", "Z", 16)
    k.cyl(f"WB {side} davit arm", (x + sign * 0.28, cy + ry - 0.15, CD_BODY_Z1 + 0.55), 0.035, 0.55, "yellow", "X", 16)
    k.torus(f"WB {side} davit eye", (x + sign * 0.48, cy + ry - 0.15, CD_BODY_Z1 + 0.48), 0.05, 0.012, "yellow", "Y")
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
            (P1[0] - 0.38, P1[1], 2.05),
            (P1[0] - 0.38, P1[1], 2.38),
            (6.4, P1[1], 2.38),
            (6.4, P2[1], 2.38),
            (P2[0] - 0.38, P2[1], 2.38),
            (P2[0] - 0.38, P2[1], 2.05),
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
    k.box("handoff tag", (IF_CONDENSATE_HANDOFF[0], 0.16, 5.62), (0.55, 0.03, 0.14), "dark", 0.003)
    k.text("handoff tag text", "TO TURBINE U02", (IF_CONDENSATE_HANDOFF[0], 0.18, 5.58), 0.07, "yellow", "N")
    k.empty("IF_CONDENSATE_HANDOFF", IF_CONDENSATE_HANDOFF, "0.2 m class liquid return; turbine U02 cap remains turbine-owned")
    k.rod("riser hang A", (6.4, 7.6, 5.5), (6.4, 7.6, 5.998), 0.012, "steel")
    k.rod("riser hang B", (IF_CONDENSATE_HANDOFF[0], 1.4, 5.5), (IF_CONDENSATE_HANDOFF[0], 1.4, 5.998), 0.012, "steel")
    k.anchor("riser hang A", (6.4, 7.6, 5.985), "Ceiling slab", (0, 0, 1), 0.02, 0.006)
    k.anchor("riser hang B", (IF_CONDENSATE_HANDOFF[0], 1.4, 5.985), "Ceiling slab", (0, 0, 1), 0.02, 0.006)


def _cep(name, x, y):
    z = 0.95
    k.box(name + " skid", (x, y, 0.08), (1.85, 0.95, 0.16), "dark", 0.008)
    k.box(name + " drip", (x, y, 0.18), (1.78, 0.88, 0.04), "steel", 0.004)
    for dx, dy in ((-0.72, -0.34), (-0.72, 0.34), (0.70, -0.34), (0.70, 0.34)):
        k.cyl(name + " anchor", (x + dx, y + dy, 0.04), 0.045, 0.08, "steel", "Z", 6, 0.002)
        k.anchor(name + f" ft{dx}", (x + dx, y + dy, 0), "Structural floor")
    vs = []
    n = 64
    cx = x - 0.38
    for xx in (cx - 0.18, cx + 0.18):
        for i in range(n):
            t = i / (n - 1)
            a = -math.pi / 2 + math.tau * t
            r = 0.32 + 0.16 * t
            vs.append((xx, y + math.cos(a) * r, z + math.sin(a) * r))
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [
        (i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)
    ]
    k.mesh(name + " volute", vs, faces, "oxide", 0.022, True)
    k.cyl(name + " back hub", (cx - 0.20, y, z), 0.11, 0.05, "iron", "X", 32, 0.008)
    k.cyl(name + " cover flange", (cx + 0.20, y, z), 0.34, 0.055, "steel", "X", 48, 0.010)
    k.cyl(name + " cover", (cx + 0.24, y, z), 0.30, 0.06, "oxide_light", "X", 48, 0.012)
    for i in range(10):
        a = i * math.tau / 10
        k.bolt(name + " cover stud", (cx + 0.28, y + math.cos(a) * 0.29, z + math.sin(a) * 0.29), "X", 0.016)
    k.box(name + " foot L", (cx, y - 0.28, 0.44), (0.32, 0.16, 0.52), "oxide", 0.012)
    k.box(name + " foot R", (cx, y + 0.28, 0.44), (0.32, 0.16, 0.52), "oxide", 0.012)
    k.cyl(name + " suction", (cx, y, z - 0.48), 0.10, 0.24, "steel", "Z", 24, 0.006)
    k.flange(name + " suction fl", (cx, y, z - 0.58), 0.15, "Z", "steel", 8, 0.05)
    k.pipe(
        name + " suction line",
        [
            (cx, y, z - 0.62),
            (cx, y, 0.52),
            (CD_C[0] + (0.4 if "A" in name else -0.4), y, 0.52),
            (CD_C[0] + (0.4 if "A" in name else -0.4), CD_C[1] + 0.95, 0.52),
            (CD_C[0] + (0.4 if "A" in name else -0.4), CD_C[1] + 0.55, HW_Z0 + 0.12),
        ],
        0.075,
        "cream",
        0.14,
    )
    k.pipe(name + " discharge neck", [(cx, y, z + 0.46), (cx, y, 2.05)], 0.08, "cream", 0.08)
    k.flange(name + " disch fl", (cx, y, 1.52), 0.14, "Z", "steel", 8, 0.05)
    k.cyl(name + " isol body", (cx, y, 1.72), 0.11, 0.16, "steel", "Z", 24, 0.008)
    k.cyl(name + " isol stem", (cx + 0.18, y, 1.72), 0.022, 0.22, "steel", "X", 12)
    k.wheel(name + " isol", (cx + 0.34, y, 1.72), 0.12, "X", "yellow")
    k.gauge(name + " out gauge", (cx + 0.22, y - 0.18, 1.95), "Y", 0.08)
    k.cyl(name + " seal housing", (x - 0.06, y, z), 0.14, 0.28, "dark", "X", 36, 0.012)
    k.annulus(name + " seal collar", (x + 0.04, y, z), 0.15, 0.06, 0.05, "iron", "X")
    k.cyl(name + " shaft", (x + 0.14, y, z), 0.055, 0.42, "steel", "X", 32)
    k.cyl(name + " jaw A", (x + 0.06, y, z), 0.11, 0.08, "steel", "X", 28, 0.008)
    k.cyl(name + " spider", (x + 0.16, y, z), 0.105, 0.07, "rubber", "X", 28, 0.006)
    k.cyl(name + " jaw B", (x + 0.26, y, z), 0.11, 0.08, "steel", "X", 28, 0.008)
    r_g = 0.22
    x0g, x1g = x + 0.00, x + 0.42
    for i in range(13):
        a = math.pi * i / 12
        k.rod(
            name + " guard bar",
            (x0g, y + r_g * math.cos(a), z + r_g * math.sin(a)),
            (x1g, y + r_g * math.cos(a), z + r_g * math.sin(a)),
            0.008,
            "yellow",
        )
    for xx in (x0g, (x0g + x1g) / 2, x1g):
        arc = [(xx, y + r_g * math.cos(math.pi * i / 30), z + r_g * math.sin(math.pi * i / 30)) for i in range(31)]
        k.pipe(name + " guard ring", arc, 0.011, "yellow", 0.03)
    mx = x + 0.78
    k.cyl(name + " motor", (mx, y, z), 0.26, 0.80, "struct", "X", 48, 0.018)
    for i in range(24):
        a = i * math.tau / 24
        o = k.box(name + " fin", (mx, y + math.cos(a) * 0.268, z + math.sin(a) * 0.268), (0.62, 0.012, 0.058), "struct", 0.002)
        o.rotation_euler.x = a - math.pi / 2
    k.cyl(name + " end bell", (mx + 0.42, y, z), 0.27, 0.12, "steel", "X", 40, 0.012)
    k.torus(name + " fan lip", (mx + 0.50, y, z), 0.22, 0.014, "steel", "X")
    for i in range(-6, 7):
        zz = i * 0.032
        d = math.sqrt(max(0.001, 0.20 ** 2 - zz ** 2))
        k.rod(name + " fan grille", (mx + 0.52, y - d, z + zz), (mx + 0.52, y + d, z + zz), 0.005, "steel")
    k.box(name + " terminal gasket", (mx, y, z + 0.32), (0.30, 0.28, 0.06), "rubber", 0.004)
    k.box(name + " terminal", (mx, y, z + 0.40), (0.32, 0.30, 0.12), "struct", 0.008)
    k.box(name + " terminal lid", (mx, y, z + 0.47), (0.31, 0.29, 0.02), "dark", 0.003)
    k.pipe(
        name + " motor feed",
        [(mx, y + 0.16, z + 0.47), (mx, y + 0.42, z + 0.47), (-0.88, y + 0.42, z + 0.47), (-0.88, y + 0.42, 5.40)],
        0.016,
        "rubber",
        0.14,
    )
    k.box(name + " motor foot", (mx, y, 0.46), (0.58, 0.40, 0.12), "dark", 0.008)
    for yy in (y - 0.14, y + 0.14):
        k.cyl(name + " foot bolt", (mx, yy, 0.54), 0.018, 0.03, "steel", "Z", 6)
    k.box(name + " ID plate", (mx, y - 0.27, z), (0.34, 0.016, 0.11), "dark", 0.002)
    k.text(name + " ID", name + " / CEP", (mx, y - 0.28, z - 0.02), 0.055, "white", "S")
    k.box(name + " floor ID", (x, y - 0.58, 0.02), (0.55, 0.12, 0.03), "dark", 0.003)
    k.text(name + " floor IDt", name, (x, y - 0.58, 0.04), 0.08, "white", "UP")
    k.hook("INTERACT_" + name, (x + 0.22, y - 0.45, 1.15), "start_stop_cep", name)


def cooling_water():
    k.group("12 Cooling water")
    ny = CD_C[1] + (CD_WID_Y - 0.15) / 2
    ex = CD_C[0] + CD_LEN_X / 2 + WB_DEPTH / 2
    wx = CD_C[0] - CD_LEN_X / 2 - WB_DEPTH / 2
    cz = CD_C[2]
    # Nozzles on the NORTH faces so covers stay solid
    k.box("CW east saddle", (ex, ny - 0.04, cz), (0.36, 0.10, 0.36), "struct", 0.008)
    k.flange("CW east nozzle fl", (ex, ny + 0.08, cz), 0.18, "Y", "steel", 10, 0.07)
    k.cyl("CW east nozzle", (ex, ny + 0.02, cz), 0.11, 0.16, "steel", "Y", 24, 0.006)
    k.box("CW west saddle", (wx, ny - 0.04, cz), (0.36, 0.10, 0.36), "struct", 0.008)
    k.flange("CW west nozzle fl", (wx, ny + 0.08, cz), 0.18, "Y", "steel", 10, 0.07)
    k.cyl("CW west nozzle", (wx, ny + 0.02, cz), 0.11, 0.16, "steel", "Y", 24, 0.006)
    k.pipe(
        "CW supply header",
        [
            IF_CW_SUPPLY,
            (8.55, 3.20, 3.15),
            (8.55, ny + 0.20, 3.15),
            (ex, ny + 0.20, 3.15),
            (ex, ny + 0.08, 3.15),
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
            (wx, 5.75, 3.15),
            (wx, ny + 0.08, 3.15),
        ],
        0.09,
        "cream",
        0.16,
    )
    k.box("CW wall bracket S", (X1 - 0.14, 3.20, 3.15), (0.18, 0.10, 0.24), "steel", 0.006)
    k.box("CW wall bracket N", (X1 - 0.14, 4.90, 3.15), (0.18, 0.10, 0.24), "steel", 0.006)
    k.flange("CW supply wall flange", (X1 - 0.04, 3.20, 3.15), 0.22, "X", "steel", 12, 0.10)
    k.flange("CW return wall flange", (X1 - 0.04, 4.90, 3.15), 0.22, "X", "steel", 12, 0.10)
    k.cyl("CW supply cap", (X1 + 0.10, 3.20, 3.15), 0.17, 0.07, "dark", "X", 28)
    k.cyl("CW return cap", (X1 + 0.10, 4.90, 3.15), 0.17, 0.07, "dark", "X", 28)
    k.empty("IF_CW_SUPPLY", IF_CW_SUPPLY, "provisional CW supply; remote cooling-plant bind unbound")
    k.empty("IF_CW_RETURN", IF_CW_RETURN, "provisional CW return; remote cooling-plant bind unbound")
    for y, tag in ((3.20, "SUPPLY"), (4.90, "RETURN")):
        k.box("CW tag " + tag, (X1 - 0.08, y, 3.52), (0.03, 0.72, 0.16), "dark", 0.003)
        k.text("CW tag t " + tag, "CW " + tag, (X1 - 0.12, y, 3.48), 0.09, "yellow", "W")
        k.globe_valve("CW isol " + tag, (8.55, y, 3.15), "Y", 0.13)
        k.gauge("CW gauge " + tag, (8.15, y, 3.48), "X", 0.09)
    for x, y in ((8.55, 3.60), (8.55, 4.40), (8.55, 5.55), (ex, ny + 0.22), (wx, ny + 0.22)):
        k.torus("CW clamp", (x, y, 3.15), 0.12, 0.012, "steel", "Y" if abs(x - 8.55) < 0.2 else "X")
        k.rod("CW hang", (x, y, 3.32), (x, y, 5.998), 0.012, "steel")
        k.anchor("CW hang " + f"{x:.1f}_{y:.1f}", (x, y, 5.985), "Ceiling slab", (0, 0, 1), 0.02, 0.006)
    k.hook("INTERACT_CW_ISOL_S", (8.55, 3.20, 3.55), "isolate_cw_supply", "CW")
    k.hook("INTERACT_CW_ISOL_R", (8.55, 4.90, 3.55), "isolate_cw_return", "CW")


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
    k.box("OP enclosure", (X0 + 0.20, y, 1.55), (0.38, 1.85, 1.70), "dark", 0.014)
    k.box("OP face", (X0 + 0.40, y, 1.55), (0.05, 1.70, 1.55), "struct", 0.008)
    k.box("OP kick", (X0 + 0.32, y, 0.12), (0.42, 1.80, 0.22), "struct", 0.006)
    k.box("OP lower cabinet", (X0 + 0.38, y, 0.55), (0.28, 1.55, 0.70), "dark", 0.008)
    k.box("OP desk", (X0 + 0.78, y, 0.94), (0.70, 1.05, 0.06), "wood", 0.008)
    k.box("OP desk apron", (X0 + 0.70, y, 0.82), (0.55, 1.00, 0.08), "dark", 0.004)
    k.box("OP desk leg L", (X0 + 0.58, y - 0.42, 0.46), (0.06, 0.06, 0.88), "dark", 0.003)
    k.box("OP desk leg R", (X0 + 0.58, y + 0.42, 0.46), (0.06, 0.06, 0.88), "dark", 0.003)
    k.box("OP chair seat", (X0 + 1.12, y - 0.62, 0.52), (0.38, 0.36, 0.06), "dark", 0.006)
    k.box("OP chair back", (X0 + 1.28, y - 0.62, 0.85), (0.05, 0.36, 0.42), "dark", 0.006)
    k.cyl("OP chair stem", (X0 + 1.12, y - 0.62, 0.26), 0.03, 0.48, "steel", "Z", 12)
    k.cyl("OP chair base", (X0 + 1.12, y - 0.62, 0.05), 0.18, 0.04, "steel", "Z", 16)
    labels = [("VAC", 0.52), ("LEVEL", 0.18), ("CW IN", -0.16), ("FLOW", -0.50)]
    for lab, dy in labels:
        k.gauge("OP " + lab, (X0 + 0.48, y + dy, 2.05), "X", 0.125)
        k.text("OP " + lab + " t", lab, (X0 + 0.44, y + dy, 1.84), 0.055, "white", "E")
    for i, dy in enumerate((0.48, 0.16, -0.16, -0.48)):
        k.box("OP switch box", (X0 + 0.44, y + dy, 1.38), (0.08, 0.10, 0.12), "dark", 0.004)
        k.cyl("OP switch body", (X0 + 0.50, y + dy, 1.38), 0.028, 0.05, "steel", "X", 16)
        k.cyl("OP switch knob", (X0 + 0.56, y + dy, 1.38), 0.022, 0.04, "yellow" if i == 0 else "dark", "X", 12)
        k.box("OP guard hood", (X0 + 0.50, y + dy, 1.46), (0.10, 0.12, 0.02), "yellow", 0.002)
    k.box("OP trip bezel", (X0 + 0.44, y, 1.12), (0.05, 0.10, 0.10), "dark", 0.004)
    k.cyl("OP trip stem", (X0 + 0.50, y, 1.12), 0.018, 0.05, "red", "X", 12)
    k.cyl("OP trip mushroom", (X0 + 0.56, y, 1.12), 0.042, 0.032, "red", "X", 16)
    k.box("OP title plate", (X0 + 0.42, y, 2.28), (0.03, 1.55, 0.14), "dark", 0.003)
    k.text("OP title", "CSB-01  CONDENSER", (X0 + 0.46, y, 2.26), 0.08, "white", "E")
    k.text("OP subtitle", "VACUUM  /  CEP  /  CW", (X0 + 0.46, y, 2.14), 0.055, "yellow", "E")
    k.box("OP clipboard", (X0 + 0.70, y + 0.18, 0.98), (0.24, 0.18, 0.01), "paper", 0.001)
    k.box("OP binder", (X0 + 0.92, y + 0.32, 1.02), (0.18, 0.14, 0.08), "burgundy", 0.004)
    k.cyl("OP mug", (X0 + 0.85, y - 0.28, 1.02), 0.035, 0.09, "burgundy", "Z", 20, 0.006)
    k.torus("OP mug handle", (X0 + 0.89, y - 0.28, 1.02), 0.028, 0.008, "burgundy", "Y")
    k.cyl("OP desk lamp post", (X0 + 0.52, y - 0.42, 1.15), 0.012, 0.42, "steel", "Z", 8)
    k.cyl("OP desk lamp", (X0 + 0.62, y - 0.42, 1.38), 0.05, 0.04, "lamp", "Z", 12)
    k.pipe("OP panel feed", [(X0 + 0.20, y, 2.35), (X0 + 0.20, y, 5.40), (-0.88, y, 5.40)], 0.014, "rubber", 0.12)
    k.hook("INTERACT_CSB_VACUUM", (X0 + 0.52, y + 0.32, 1.38), "set_vacuum_mode", "OP")
    k.hook("INTERACT_CSB_TRIP", (X0 + 0.52, y, 1.12), "vacuum_trip", "OP")
    k.hook("INTERACT_CSB_CEP", (X0 + 0.52, y - 0.12, 1.38), "cep_select", "OP")


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
    k.i_beam("hoist beam", (5.1, 3.55, 5.52), (9.2, 3.55, 5.52), 0.16, 0.24, "yellow")
    k.box("hoist trolley", (6.4, 3.55, 5.34), (0.28, 0.22, 0.16), "dark", 0.008)
    k.box("hoist gearbox", (6.4, 3.55, 5.12), (0.22, 0.18, 0.22), "yellow", 0.01)
    k.cyl("hoist hook shank", (6.4, 3.55, 4.88), 0.02, 0.28, "steel", "Z", 10)
    k.torus("hoist hook", (6.4, 3.55, 4.70), 0.07, 0.018, "steel", "Y")
    k.rod("hoist hang L", (5.3, 3.55, 5.64), (5.3, 3.55, 5.998), 0.014, "steel")
    k.rod("hoist hang R", (8.9, 3.55, 5.64), (8.9, 3.55, 5.998), 0.014, "steel")
    k.anchor("hoist L", (5.3, 3.55, 5.985), "Ceiling slab", (0, 0, 1), 0.02, 0.006)
    k.anchor("hoist R", (8.9, 3.55, 5.985), "Ceiling slab", (0, 0, 1), 0.02, 0.006)
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
    # Shift log on north wall, facing the aisle (south)
    k.box("log clipboard", (1.15, Y1 - 0.05, 1.52), (0.40, 0.02, 0.48), "paper", 0.002)
    k.box("log clip", (1.15, Y1 - 0.06, 1.74), (0.14, 0.03, 0.04), "steel", 0.002)
    k.text("log title", "SHIFT LOG", (1.15, Y1 - 0.08, 1.58), 0.08, "ink", "S")
    k.box("log board west", (X0 + 0.04, 8.15, 1.55), (0.03, 0.36, 0.42), "paper", 0.002)
    k.text("log title west", "SHIFT LOG", (X0 + 0.06, 8.15, 1.70), 0.08, "ink", "E")
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
