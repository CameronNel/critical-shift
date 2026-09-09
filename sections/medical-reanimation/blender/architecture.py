"""Room shell, door, ceiling services, floor markings."""
from __future__ import annotations

import math

import config
import labels
import mesh as g
from config import DECON, DOOR_H, DOOR_W, WALL_T, X0, X1, Y0, Y1, Z1


def _floor_panels():
    # 1.00 x 1.00 resin panels with 8 mm joints
    joint = 0.008
    tile = 1.00
    z = -0.05
    n = 0
    x = X0
    while x < X1 - 0.01:
        y = Y0
        w = min(tile, X1 - x)
        while y < Y1 - 0.01:
            d = min(tile, Y1 - y)
            g.box_min(f"Floor_{n:03d}", (x + joint * 0.5, y + joint * 0.5, -0.05), (w - joint, d - joint, 0.05), "floor", 0.0)
            n += 1
            y += tile
        x += tile
    # decon floor
    g.box_min("Floor_decon", (DECON["x0"] + 0.02, DECON["y0"] + 0.02, -0.05), (DECON["x1"] - DECON["x0"] - 0.04, DECON["y1"] - DECON["y0"] - 0.04, 0.05), "tile", 0.0)


def _wall_run(name, x, y, z, sx, sy, sz, mat="wall"):
    o = g.box_min(name, (x, y, z), (sx, sy, sz), mat, 0.002)
    g.support(o, "structure", "WORLD_-Y" if sy < sx else "WORLD_+X", [(x + sx / 2, y + sy / 2, z)])
    return o


def _walls():
    t = WALL_T
    h = Z1
    dado = 1.12
    # South wall left / right of door, plus header. Exterior in -Y.
    g.box_min("Wall_S_L", (X0 - t, Y0 - t, 0), ((-DOOR_W / 2) - (X0 - t), t, h), "wall", 0.0)
    g.box_min("Wall_S_R", (DOOR_W / 2, Y0 - t, 0), (X1 + t - DOOR_W / 2, t, h), "wall", 0.0)
    g.box_min("Wall_S_head", (-DOOR_W / 2, Y0 - t, DOOR_H), (DOOR_W, t, h - DOOR_H), "wall", 0.0)
    # North wall with decon opening 1.55..2.75, 0..2.15
    dx0, dx1 = 1.55, 2.75
    dh = 2.15
    g.box_min("Wall_N_W", (X0 - t, Y1, 0), ((dx0) - (X0 - t), t, h), "wall", 0.0)
    g.box_min("Wall_N_E", (dx1, Y1, 0), (X1 + t - dx1, t, h), "wall", 0.0)
    g.box_min("Wall_N_head", (dx0, Y1, dh), (dx1 - dx0, t, h - dh), "wall", 0.0)
    # West / east
    g.box_min("Wall_W", (X0 - t, Y0, 0), (t, Y1 - Y0, h), "wall", 0.0)
    g.box_min("Wall_E", (X1, Y0, 0), (t, Y1 - Y0, h), "wall", 0.0)
    # Decon stall walls
    g.box_min("Wall_decon_E", (DECON["x1"], DECON["y0"], 0), (t, DECON["y1"] - DECON["y0"], DECON["z1"]), "tile", 0.0)
    g.box_min("Wall_decon_W", (DECON["x0"] - t, DECON["y0"], 0), (t, DECON["y1"] - DECON["y0"], DECON["z1"]), "tile", 0.0)
    g.box_min("Wall_decon_N", (DECON["x0"], DECON["y1"], 0), (DECON["x1"] - DECON["x0"], t, DECON["z1"]), "tile", 0.0)
    g.box_min("Ceil_decon", (DECON["x0"] - t, DECON["y0"], DECON["z1"]), (DECON["x1"] - DECON["x0"] + 2 * t, DECON["y1"] - DECON["y0"] + t, 0.12), "wall", 0.0)
    # Dado band inside hall
    g.box_min("Dado_W", (X0, Y0, 0), (0.03, Y1 - Y0, dado), "trim", 0.0)
    g.box_min("Dado_E", (X1 - 0.03, Y0, 0), (0.03, Y1 - Y0, dado), "trim", 0.0)
    g.box_min("Dado_N_W", (X0, Y1 - 0.03, 0), (dx0 - X0, 0.03, dado), "trim", 0.0)
    g.box_min("Dado_N_E", (dx1, Y1 - 0.03, 0), (X1 - dx1, 0.03, dado), "trim", 0.0)
    g.box_min("Dado_S_L", (X0, Y0, 0), ((-DOOR_W / 2) - X0, 0.03, dado), "trim", 0.0)
    g.box_min("Dado_S_R", (DOOR_W / 2, Y0, 0), (X1 - DOOR_W / 2, 0.03, dado), "trim", 0.0)
    # Skirting
    for i, (mn, sz) in enumerate([
        ((X0, Y0, 0), (X1 - X0, 0.04, 0.10)),
        ((X0, Y1 - 0.04, 0), (dx0 - X0, 0.04, 0.10)),
        ((dx1, Y1 - 0.04, 0), (X1 - dx1, 0.04, 0.10)),
        ((X0, Y0, 0), (0.04, Y1 - Y0, 0.10)),
        ((X1 - 0.04, Y0, 0), (0.04, Y1 - Y0, 0.10)),
    ]):
        g.box_min(f"Skirt_{i}", mn, sz, "graphite", 0.002)
    # Corner guards
    for i, x in enumerate([X0 + 0.02, X1 - 0.02]):
        g.cyl(f"Guard_{i}", (x, Y0 + 0.04, 0.02), (x, Y0 + 0.04, 1.20), 0.025, "yellow", 10, 0.002)
    # Upper wall panel seams (quiet rhythm, not every metre of gadget)
    for i, y in enumerate([1.8, 3.6, 5.4, 7.2]):
        g.box_min(f"Seam_W_{i}", (X0 + 0.001, y, 1.2), (0.006, 0.02, 2.1), "trim", 0.0)
        g.box_min(f"Seam_E_{i}", (X1 - 0.007, y, 1.2), (0.006, 0.02, 2.1), "trim", 0.0)


def _door():
    # Pressure frame
    fw, fh, fd = DOOR_W + 0.28, DOOR_H + 0.22, 0.16
    g.box("Door_frame_head", (0, Y0 - 0.02, DOOR_H + 0.08), (fw, fd, 0.16), "shell", 0.006)
    g.box("Door_frame_L", (-DOOR_W / 2 - 0.08, Y0 - 0.02, DOOR_H / 2), (0.16, fd, DOOR_H + 0.08), "shell", 0.006)
    g.box("Door_frame_R", (DOOR_W / 2 + 0.08, Y0 - 0.02, DOOR_H / 2), (0.16, fd, DOOR_H + 0.08), "shell", 0.006)
    g.box("Door_sill", (0, Y0 - 0.01, 0.04), (DOOR_W + 0.2, 0.22, 0.08), "darksteel", 0.003)
    # Hazard jambs
    g.box("Door_haz_L", (-DOOR_W / 2 - 0.02, Y0 + 0.04, 1.15), (0.04, 0.06, 2.1), "hazard", 0.0)
    g.box("Door_haz_R", (DOOR_W / 2 + 0.02, Y0 + 0.04, 1.15), (0.04, 0.06, 2.1), "hazard", 0.0)
    # Sliding leaves (closed beauty pose)
    leaf_w = DOOR_W / 2 - 0.01
    for side, x in (("L", -leaf_w / 2 - 0.005), ("R", leaf_w / 2 + 0.005)):
        g.box(f"Door_leaf_{side}", (x, Y0 + 0.03, DOOR_H / 2 + 0.02), (leaf_w, 0.07, DOOR_H - 0.06), "shell", 0.004)
        g.box(f"Door_leaf_{side}_inner", (x, Y0 + 0.06, DOOR_H / 2 + 0.05), (leaf_w - 0.16, 0.02, DOOR_H - 0.35), "graphite", 0.002)
        g.box(f"Door_view_{side}", (x, Y0 + 0.075, 1.48), (0.08, 0.02, 0.55), "glass_dark", 0.001)
        g.box(f"Door_view_{side}_em", (x, Y0 + 0.07, 1.48), (0.05, 0.008, 0.42), "cyan", 0.0)
    # Cross bar / latch
    g.box("Door_latch", (0, Y0 + 0.08, 1.15), (0.18, 0.05, 0.12), "darksteel", 0.003)
    g.box("Door_kick_L", (-leaf_w / 2 - 0.005, Y0 + 0.05, 0.22), (leaf_w - 0.05, 0.04, 0.28), "graphite", 0.002)
    g.box("Door_kick_R", (leaf_w / 2 + 0.005, Y0 + 0.05, 0.22), (leaf_w - 0.05, 0.04, 0.28), "graphite", 0.002)
    # Reader and buttons
    g.box("Door_reader", (DOOR_W / 2 + 0.22, Y0 + 0.09, 1.22), (0.12, 0.06, 0.18), "graphite", 0.003)
    g.box("Door_reader_pad", (DOOR_W / 2 + 0.22, Y0 + 0.13, 1.22), (0.08, 0.01, 0.12), "plastic", 0.001)
    g.cyl("Door_btn_amber", (DOOR_W / 2 + 0.22, Y0 + 0.12, 1.42), (DOOR_W / 2 + 0.22, Y0 + 0.14, 1.42), 0.018, "led_amber", 10)
    g.cyl("Door_btn_red", (DOOR_W / 2 + 0.22, Y0 + 0.12, 1.02), (DOOR_W / 2 + 0.22, Y0 + 0.14, 1.02), 0.016, "led_red", 10)
    # Overhead ID
    g.box("Door_id_plate", (0, Y0 + 0.08, 2.72), (0.72, 0.04, 0.16), "shell", 0.003)
    labels.text3d("Door_id", "L3-01", (0, Y0 + 0.11, 2.72), size=0.09, extrude=0.003, mat="ink", normal=(0, 1, 0))
    labels.text3d("Door_auth", "AUTHORIZED PERSONNEL ONLY", (0, Y0 + 0.11, 1.72), size=0.045, extrude=0.002, mat="ink", normal=(0, 1, 0))
    # Threshold grate
    grate = g.box("Door_grate", (0, 0.22, 0.005), (2.05, 0.42, 0.008), "grate", 0.0)
    g.support(grate, "Floor", "WORLD_-Z", [(0, 0.22, 0.002)])
    for i in range(9):
        g.box(f"Door_grate_bar_{i}", (-0.9 + i * 0.22, 0.22, 0.022), (0.03, 0.38, 0.012), "darksteel", 0.0)
    labels.text3d("Door_thresh_txt", "KEEP CLEAR", (0, 0.22, 0.03), size=0.05, extrude=0.001, mat="floor_mark", normal=(0, 0, 1))


def _ceiling():
    g.box_min("Ceil", (X0 - WALL_T, Y0 - WALL_T, Z1), (X1 - X0 + 2 * WALL_T, Y1 - Y0 + 2 * WALL_T, 0.16), "wall_upper", 0.0)
    # Cable trays along Y, two main runs
    for i, x in enumerate([-2.4, -0.2, 1.6, 3.1]):
        g.box(f"Tray_{i}", (x, 4.5, 3.38), (0.28, 8.4, 0.05), "darksteel", 0.002)
        g.box(f"Tray_{i}_L", (x - 0.13, 4.5, 3.42), (0.02, 8.4, 0.12), "darksteel", 0.0)
        g.box(f"Tray_{i}_R", (x + 0.13, 4.5, 3.42), (0.02, 8.4, 0.12), "darksteel", 0.0)
        # bundled cables
        for k, off in enumerate([(-0.06, 0.03), (0.0, 0.04), (0.05, 0.025)]):
            g.tube(f"Cable_{i}_{k}", [(x + off[0], 0.4, 3.45 + off[1]), (x + off[0], 2.2, 3.38 + off[1]), (x + off[0], 4.5, 3.46 + off[1]), (x + off[0], 6.8, 3.40 + off[1]), (x + off[0], 8.6, 3.44 + off[1])], 0.018 + k * 0.004, "rubber")
        g.tube(f"CableLoop_{i}", [(x + 0.12, 3.2, 3.40), (x + 0.22, 3.4, 3.18), (x + 0.12, 3.7, 3.40)], 0.016, "rubber")
    # Cross trays
    for i, y in enumerate([2.2, 5.0, 7.6]):
        g.box(f"TrayX_{i}", (0.2, y, 3.30), (7.4, 0.22, 0.04), "darksteel", 0.002)
    # Linear fixtures (meshes; lights added in lighting.py)
    fixtures = [
        ("Fix_A", -1.8, 1.6), ("Fix_B", 1.5, 1.6),
        ("Fix_C", -1.8, 4.0), ("Fix_D", 1.5, 4.0),
        ("Fix_E", -1.8, 6.5), ("Fix_F", 1.5, 6.5),
        ("Fix_G", 0.0, 8.2), ("Fix_H", 2.4, 8.4),
    ]
    for name, x, y in fixtures:
        g.box(name, (x, y, 3.28), (1.22, 0.18, 0.07), "graphite", 0.002)
        g.box(name + "_lens", (x, y, 3.24), (1.12, 0.12, 0.03), "lamp", 0.0)
        g.box(name + "_endL", (x - 0.58, y, 3.28), (0.08, 0.18, 0.08), "darksteel", 0.002)
        g.box(name + "_endR", (x + 0.58, y, 3.28), (0.08, 0.18, 0.08), "darksteel", 0.002)
    # Orange emergency bars
    for i, (x, y) in enumerate([(-3.2, 2.0), (-3.2, 7.2), (3.3, 1.8), (3.3, 7.6)]):
        g.box(f"EmBar_{i}", (x, y, 3.22), (0.12, 0.85, 0.08), "graphite", 0.002)
        g.box(f"EmBar_{i}_lens", (x, y, 3.17), (0.08, 0.75, 0.03), "lamp_orange", 0.0)
    # Pipes along west/east high
    g.tube("Pipe_W", [(-3.55, 0.3, 3.05), (-3.55, 4.5, 3.08), (-3.55, 8.7, 3.05)], 0.045, "darksteel")
    g.tube("Pipe_W2", [(-3.35, 0.3, 2.92), (-3.35, 4.5, 2.90), (-3.35, 8.7, 2.94)], 0.028, "graphite")
    g.tube("Pipe_E", [(3.55, 0.4, 3.02), (3.55, 5.0, 3.05), (3.55, 8.7, 3.00)], 0.04, "darksteel")
    # Hangers
    for i, y in enumerate([1.5, 4.2, 7.0]):
        g.cyl(f"Hang_W_{i}", (-3.55, y, 3.05), (-3.55, y, 3.38), 0.01, "steel", 8)
        g.cyl(f"Hang_E_{i}", (3.55, y, 3.02), (3.55, y, 3.38), 0.01, "steel", 8)
    # Junction boxes
    for i, (x, y) in enumerate([(-2.4, 8.5), (1.6, 0.8), (3.1, 5.2)]):
        g.box(f"Jbox_{i}", (x, y, 3.18), (0.16, 0.22, 0.12), "graphite", 0.003)


def _markings():
    # Cart parking box
    x0, y0, x1, y1 = config.EQUIP["CartParking"]
    _box_outline("Mark_cart", x0, y0, x1, y1, "yellow")
    labels.text3d("Mark_cart_txt", "CART PARKING", ((x0 + x1) / 2, (y0 + y1) / 2, 0.012), size=0.11, extrude=0.001, mat="floor_mark", rot=(0, 0, math.pi / 2), normal=None)
    # Clean access field in apron
    g.box("Mark_access", (0.15, 4.6, 0.006), (2.6, 2.2, 0.004), "yellow", 0.0)
    g.box("Mark_access_in", (0.15, 4.6, 0.007), (2.42, 2.02, 0.004), "floor", 0.0)
    g.quad("Mark_access_txt", (0.15, 4.6, 0.016), 2.2, 0.28, "floor_stencil", normal=(0, 0, 1))
    # OCRU keep-clear stripe along machine face
    g.box("Mark_ocru_haz", (-1.40, 4.63, 0.01), (0.10, 4.1, 0.006), "hazard_fine", 0.0)
    # Door approach arrows (simple chevrons)
    for i, y in enumerate([0.7, 1.15]):
        g.box(f"Mark_chev_{i}", (0, y, 0.008), (0.22, 0.06, 0.003), "floor_mark", 0.0)


def _box_outline(name, x0, y0, x1, y1, mat, t=0.05, z=0.008):
    g.box(name + "_s", ((x0 + x1) / 2, y0 + t / 2, z), (x1 - x0, t, 0.005), mat, 0.0)
    g.box(name + "_n", ((x0 + x1) / 2, y1 - t / 2, z), (x1 - x0, t, 0.005), mat, 0.0)
    g.box(name + "_w", (x0 + t / 2, (y0 + y1) / 2, z), (t, y1 - y0 - 2 * t, 0.005), mat, 0.0)
    g.box(name + "_e", (x1 - t / 2, (y0 + y1) / 2, z), (t, y1 - y0 - 2 * t, 0.005), mat, 0.0)


def _signage():
    # West of door
    g.box("Sign_health", (-2.15, 0.05, 1.85), (0.55, 0.03, 0.85), "graphite", 0.003)
    labels.text3d("Sign_health_t", "OCCUPATIONAL\nHEALTH\nREANIMATION\nUNIT", (-2.15, 0.08, 1.95), size=0.055, extrude=0.002, mat="floor_mark", normal=(0, 1, 0))
    labels.text3d("Sign_health_s", "PEOPLE KEEP\nOPERATIONS RUNNING", (-2.15, 0.08, 1.45), size=0.032, extrude=0.0015, mat="yellow", normal=(0, 1, 0))
    # East of door
    g.box("Sign_fit", (2.15, 0.05, 1.95), (0.48, 0.03, 0.55), "graphite", 0.003)
    labels.text3d("Sign_fit_t", "FIT PEOPLE\nSAFER SITES", (2.15, 0.08, 1.95), size=0.05, extrude=0.002, mat="floor_mark", normal=(0, 1, 0))
    # Rear slogan
    g.box("Sign_value", (-0.35, 8.97, 2.55), (1.15, 0.03, 0.42), "shell", 0.003)
    labels.text3d("Sign_value_t", "HUMAN STABILITY.\nOPERATIONAL CONTINUITY.", (-0.35, 8.94, 2.55), size=0.045, extrude=0.002, mat="ink", normal=(0, -1, 0))
    # Triangle mark
    g.box("Mark_tri", (0.55, 8.97, 2.55), (0.28, 0.02, 0.28), "graphite", 0.002)
    labels.text3d("Mark_tri_t", "A", (0.55, 8.95, 2.55), size=0.16, extrude=0.003, mat="floor_mark", normal=(0, -1, 0))
    # Stabilize poster near bench
    g.box("Poster_stab", (3.93, 1.55, 1.85), (0.02, 0.42, 0.62), "paper", 0.001)
    g.support(g.box("Poster_stab_board", (3.975, 1.55, 1.85), (0.012, 0.46, 0.66), "graphite", 0.002), "Wall_E", "WORLD_+X", [(3.982, 1.55, 1.85)], gap=0.02)
    labels.text3d("Poster_stab_t", "STABILIZE\nTREAT\nRETURN", (3.91, 1.55, 1.90), size=0.055, extrude=0.002, mat="ink", normal=(-1, 0, 0))


def build():
    with g.use("ARCHITECTURE"):
        _floor_panels()
        _walls()
        _door()
        _ceiling()
        _markings()
        _signage()
        g.box_min("Ext_slab", (X0 - WALL_T, Y0 - 0.8, -0.08), (X1 - X0 + 2 * WALL_T, 0.8, 0.08), "floor", 0.0)
