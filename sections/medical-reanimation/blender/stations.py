"""Operator console, cartridges, power, decon, recovery, supplies, cart, props."""
from __future__ import annotations

import math

import labels
import mesh as g
from config import EQUIP, Y1


def build():
    with g.use("STATIONS"):
        _console()
        _cartridges()
        _battery()
        _decon()
        _power()
        _supplies()
        _bench()
        _wash()
        _recovery()
        _cart()
        _stools()
        _props()


def _console():
    x0, y0, x1, y1 = EQUIP["Console"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    depth = y1 - y0
    width = x1 - x0
    # Pedestal and top, flush to Y=9
    body = g.box_min("Con_body", (x0, y0 + 0.08, 0), (width, depth - 0.08, 0.72), "graphite", 0.005)
    g.support(body, "Floor", "WORLD_-Z", [(cx, cy, 0)])
    g.box_min("Con_kick", (x0 + 0.04, y0 + 0.08, 0), (width - 0.08, 0.04, 0.12), "hazard_fine", 0.0)
    g.box_min("Con_top", (x0 - 0.04, y0, 0.72), (width + 0.08, depth, 0.05), "graphite", 0.004)
    # Rear riser flush to wall; screens face the operator (-Y)
    g.box_min("Con_riser", (x0 + 0.04, y1 - 0.16, 0.77), (width - 0.08, 0.16, 1.08), "graphite", 0.004)
    fy = y1 - 0.17
    g.box("Con_screenA_bezel", (cx - 0.42, fy + 0.03, 1.42), (0.76, 0.05, 0.52), "graphite", 0.004)
    g.quad("Con_screenA", (cx - 0.42, fy - 0.005, 1.42), 0.66, 0.42, "screen_status", normal=(0, -1, 0))
    g.box("Con_screenB_bezel", (cx + 0.42, fy + 0.03, 1.42), (0.52, 0.05, 0.52), "graphite", 0.004)
    g.quad("Con_screenB", (cx + 0.42, fy - 0.005, 1.42), 0.42, 0.42, "screen_body", normal=(0, -1, 0))
    # Control deck
    g.box_min("Con_deck", (x0 + 0.08, y0 + 0.05, 0.77), (width - 0.16, 0.42, 0.08), "darksteel", 0.003)
    # Physical restart cluster — constructed housing, not loose primitives
    g.box("Con_restart_house", (cx - 0.48, y0 + 0.26, 0.86), (0.38, 0.28, 0.05), "graphite", 0.003)
    g.cyl("Con_guard_L", (cx - 0.62, y0 + 0.18, 0.88), (cx - 0.62, y0 + 0.18, 1.02), 0.012, "yellow", 10)
    g.cyl("Con_guard_R", (cx - 0.34, y0 + 0.18, 0.88), (cx - 0.34, y0 + 0.18, 1.02), 0.012, "yellow", 10)
    g.tube("Con_guard_arch", [(cx - 0.62, y0 + 0.18, 1.02), (cx - 0.62, y0 + 0.05, 1.08), (cx - 0.48, y0 + 0.02, 1.10), (cx - 0.34, y0 + 0.05, 1.08), (cx - 0.34, y0 + 0.18, 1.02)], 0.011, "yellow")
    g.cyl("Con_restart", (cx - 0.55, y0 + 0.22, 0.88), (cx - 0.55, y0 + 0.22, 0.98), 0.032, "amber", 16)
    g.cyl("Con_restart_collar", (cx - 0.55, y0 + 0.22, 0.86), (cx - 0.55, y0 + 0.22, 0.89), 0.04, "darksteel", 12)
    labels.text3d("Con_restart_t", "RESTART", (cx - 0.48, y0 + 0.08, 0.86), size=0.026, extrude=0.001, mat="yellow", normal=(0, -1, 0))
    g.cyl("Con_abort", (cx - 0.38, y0 + 0.26, 0.90), (cx - 0.38, y0 + 0.26, 0.97), 0.022, "red", 14)
    g.cyl("Con_abort_collar", (cx - 0.38, y0 + 0.26, 0.88), (cx - 0.38, y0 + 0.26, 0.90), 0.028, "darksteel", 10)
    labels.text3d("Con_abort_t", "ABORT", (cx - 0.38, y0 + 0.08, 0.86), size=0.022, extrude=0.001, mat="red", normal=(0, -1, 0))
    g.box("Con_key_plate", (cx + 0.12, y0 + 0.24, 0.86), (0.22, 0.26, 0.03), "darksteel", 0.002)
    for i in range(3):
        for j in range(4):
            g.box(f"Con_key_{i}_{j}", (cx + 0.04 + i * 0.06, y0 + 0.14 + j * 0.055, 0.88), (0.042, 0.038, 0.012), "plastic", 0.001)
    g.box("Con_knob_plate", (cx + 0.48, y0 + 0.26, 0.86), (0.34, 0.22, 0.025), "graphite", 0.002)
    for i, x in enumerate([cx + 0.36, cx + 0.48, cx + 0.60]):
        g.cyl(f"Con_knob_{i}", (x, y0 + 0.26, 0.87), (x, y0 + 0.26, 0.94), 0.016, "steel", 12)
        g.cyl(f"Con_knob_cap_{i}", (x, y0 + 0.26, 0.94), (x, y0 + 0.26, 0.955), 0.012, "yellow", 10)
    g.box("Con_slider", (cx + 0.72, y0 + 0.26, 0.87), (0.035, 0.20, 0.018), "darksteel", 0.001)
    g.box("Con_slider_grip", (cx + 0.72, y0 + 0.18, 0.89), (0.045, 0.035, 0.025), "yellow", 0.002)
    # Drawers
    for i, z in enumerate([0.18, 0.40]):
        g.box_min(f"Con_drawer_{i}", (x0 + 0.12, y0 + 0.06, z), (0.55, 0.08, 0.16), "shell", 0.003)
        g.box(f"Con_drawer_h_{i}", (x0 + 0.40, y0 + 0.05, z + 0.08), (0.12, 0.02, 0.02), "steel", 0.001)
    g.box_min("Con_drawer_R", (cx + 0.15, y0 + 0.06, 0.18), (0.55, 0.08, 0.38), "shell", 0.003)
    # Handover ledge
    g.box_min("Con_ledge", (x0 + 0.1, y0 - 0.08, 0.70), (0.35, 0.16, 0.03), "shell", 0.003)
    g.cyl("Con_flask", (x0 + 0.18, y0 - 0.02, 0.73), (x0 + 0.18, y0 - 0.02, 0.92), 0.025, "brushed", 12)
    g.cyl("Con_flask_liq", (x0 + 0.18, y0 - 0.02, 0.74), (x0 + 0.18, y0 - 0.02, 0.86), 0.022, "liquid", 10)


def _cartridges():
    x0, y0, x1, y1 = EQUIP["Cartridges"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # Open-front cabinet so bottles read from the room.
    body = g.box_min("CartBank", (x0, y1 - 0.08, 0), (x1 - x0, 0.08, 2.12), "shell", 0.005)
    g.support(body, "Floor", "WORLD_-Z", [(cx, y1 - 0.04, 0)])
    g.support(body, "Wall_N_W", "WORLD_+Y", [(cx, y1, 1.0)], gap=0.05)
    g.box_min("CartBank_L", (x0, y0, 0), (0.05, y1 - y0, 2.12), "shell", 0.004)
    g.box_min("CartBank_R", (x1 - 0.05, y0, 0), (0.05, y1 - y0, 2.12), "shell", 0.004)
    g.box_min("CartBank_top", (x0, y0, 2.06), (x1 - x0, y1 - y0, 0.06), "shell", 0.004)
    g.box_min("CartBank_bot", (x0, y0, 0), (x1 - x0, y1 - y0, 0.08), "graphite", 0.003)
    labels.text3d("CartBank_title", "MEDICAL CARTRIDGES", (cx, y0 - 0.01, 2.00), size=0.038, extrude=0.002, mat="floor_mark", normal=(0, -1, 0))
    rows = [("01 BIOMASS", 1.70), ("02 STABILISERS", 1.28), ("03 THERAPEUTICS", 0.86), ("04 CONSUMABLES", 0.44)]
    for ri, (lab, z) in enumerate(rows):
        g.box_min(f"CartShelf_{ri}", (x0 + 0.06, y0 + 0.04, z), (x1 - x0 - 0.12, y1 - y0 - 0.14, 0.03), "darksteel", 0.001)
        labels.text3d(f"CartLab_{ri}", lab, (x0 + 0.02, y0 - 0.01, z + 0.18), size=0.026, extrude=0.0015, mat="ink", normal=(0, -1, 0), align="LEFT")
        for k in range(3):
            bx = x0 + 0.18 + k * 0.18
            by = y0 + 0.22
            g.cyl(f"CartBot_{ri}_{k}", (bx, by, z + 0.03), (bx, by, z + 0.28), 0.035, "brushed", 12)
            g.cyl(f"CartLiq_{ri}_{k}", (bx, by, z + 0.05), (bx, by, z + 0.22), 0.032, "liquid" if (ri + k) % 2 == 0 else "glass", 10)
            g.cyl(f"CartCap_{ri}_{k}", (bx, by, z + 0.28), (bx, by, z + 0.32), 0.03, "plastic", 10)
    g.box_min("CartDrawer", (x0 + 0.06, y0, 0.08), (x1 - x0 - 0.12, 0.06, 0.22), "graphite", 0.003)
    labels.text3d("CartDrawer_t", "LOG RESTOCK REPEAT", (cx, y0 - 0.02, 0.18), size=0.022, extrude=0.001, mat="floor_mark", normal=(0, -1, 0))


def _battery():
    x0, y0, x1, y1 = EQUIP["ReservePower"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    b = g.box_min("Batt", (x0, y0, 0), (x1 - x0, y1 - y0, 1.18), "graphite", 0.005)
    g.support(b, "Floor", "WORLD_-Z", [(cx, cy, 0)])
    g.support(b, "Wall_N_W", "WORLD_+Y", [(cx, y1, 0.6)], gap=0.05)
    g.box_min("Batt_door", (x0 + 0.05, y0, 0.15), (x1 - x0 - 0.1, 0.04, 0.85), "graphite", 0.003)
    g.grille("Batt_vent", (cx, y0 + 0.03, 0.55), (0.42, 0.03, 0.35), "darksteel", bars=6, axis="X")
    g.handle("Batt_handle", ((x0 + x1) / 2, y0 - 0.03, 0.92), 0.14)
    g.box("Batt_lamp", (cx, y0 + 0.03, 1.05), (0.06, 0.04, 0.04), "led_amber", 0.0)
    labels.text3d("Batt_t", "RESERVE", (cx, y0 - 0.02, 1.08), size=0.035, extrude=0.002, mat="yellow", normal=(0, -1, 0))
    # Cable to console
    g.tube("Batt_cable", [(cx, y0 + 0.08, 1.14), (cx + 0.15, y0 + 0.25, 2.2), (cx + 0.4, 8.9, 3.15)], 0.016, "rubber")


def _decon():
    x0, y0, x1, y1 = EQUIP["Decon"]
    # Threshold frame
    g.box("Decon_frame_L", (1.55 - 0.06, 9.00, 1.10), (0.12, 0.14, 2.20), "shell", 0.004)
    g.box("Decon_frame_R", (2.75 + 0.06, 9.00, 1.10), (0.12, 0.14, 2.20), "shell", 0.004)
    g.box("Decon_frame_H", (2.15, 9.00, 2.22), (1.32, 0.14, 0.12), "shell", 0.004)
    g.box("Decon_haz_L", (1.55, 9.02, 1.10), (0.04, 0.06, 2.15), "hazard", 0.0)
    g.box("Decon_haz_R", (2.75, 9.02, 1.10), (0.04, 0.06, 2.15), "hazard", 0.0)
    labels.text3d("Decon_id", "DECONTAMINATION", (2.15, 8.92, 2.38), size=0.055, extrude=0.002, mat="ink", normal=(0, -1, 0))
    labels.text3d("Decon_sub", "RINSE   SANITIZE   RETURN TO WORK", (2.15, 11.05, 2.20), size=0.04, extrude=0.002, mat="ink", normal=(0, -1, 0))
    # Grate
    grate = g.box_min("Decon_grate", (x0 + 0.08, y0 + 0.15, 0.001), (x1 - x0 - 0.16, y1 - y0 - 0.35, 0.008), "grate", 0.0)
    g.support(grate, "Floor", "WORLD_-Z", [(2.33, 10.1, 0.002)])
    for i in range(8):
        g.box(f"Decon_gbar_{i}", (2.33, y0 + 0.3 + i * 0.22, 0.03), (1.4, 0.03, 0.012), "darksteel", 0.0)
    # Shower
    g.cyl("Decon_riser", (2.72, 10.85, 0.2), (2.72, 10.85, 2.05), 0.018, "brushed", 12)
    g.cyl("Decon_arm", (2.72, 10.85, 2.05), (2.35, 10.55, 2.05), 0.014, "brushed", 10)
    g.cyl("Decon_head", (2.35, 10.55, 2.00), (2.35, 10.55, 2.05), 0.055, "brushed", 16)
    g.box("Decon_valve", (2.72, 10.82, 1.15), (0.08, 0.08, 0.12), "yellow", 0.003)
    # Shelf + bottles
    g.box("Decon_shelf", (1.72, 10.95, 1.15), (0.38, 0.16, 0.04), "darksteel", 0.002)
    g.support(g.box("Decon_shelf_br", (1.72, 11.05, 1.05), (0.08, 0.04, 0.2), "steel", 0.001), "Wall_decon_N", "WORLD_+Y", [(1.72, 11.12, 1.15)])
    for i, x in enumerate([1.58, 1.72, 1.86]):
        g.cyl(f"Decon_bot_{i}", (x, 10.92, 1.19), (x, 10.92, 1.42), 0.028, "brushed", 10)
        g.cyl(f"Decon_cap_{i}", (x, 10.92, 1.42), (x, 10.92, 1.46), 0.022, "plastic", 8)
    # Yellow bin
    bin_ = g.box("Decon_bin", (2.72, 10.15, 0.265), (0.32, 0.28, 0.52), "yellow", 0.006)
    g.support(bin_, "Floor", "WORLD_-Z", [(2.72, 10.15, 0.002)])
    g.box("Decon_bin_lid", (2.72, 10.15, 0.56), (0.30, 0.26, 0.04), "graphite", 0.003)
    labels.text3d("Decon_bin_t", "BIO", (2.72, 10.00, 0.32), size=0.04, extrude=0.002, mat="ink", normal=(0, -1, 0))
    g.box_min("Decon_dado_W", (x0, y0, 0), (0.03, y1 - y0, 1.05), "trim", 0.0)
    g.box_min("Decon_dado_E", (x1 - 0.03, y0, 0), (0.03, y1 - y0, 1.05), "trim", 0.0)
    g.box_min("Decon_dado_N", (x0, y1 - 0.03, 0), (x1 - x0, 0.03, 1.05), "trim", 0.0)
    g.cyl("Decon_drain", (2.15, 10.4, -0.01), (2.15, 10.4, 0.03), 0.06, "darksteel", 12)


def _power():
    x0, y0, x1, y1 = EQUIP["PowerPanel"]
    cx = (x0 + x1) / 2
    p = g.box("Power_panel", (cx, 8.97, 1.50), (0.52, 0.06, 0.70), "shell", 0.004)
    g.support(p, "Wall_N_E", "WORLD_+Y", [(cx, 9.00, 1.50)], gap=0.05)
    g.box("Power_face", (cx, 8.94, 1.50), (0.44, 0.02, 0.58), "graphite", 0.002)
    labels.text3d("Power_t", "POWER", (cx, 8.93, 1.78), size=0.045, extrude=0.002, mat="floor_mark", normal=(0, -1, 0))
    for i, (lab, z, mat) in enumerate([("MAINS", 1.58, "led_green"), ("RESERVE", 1.46, "led_amber"), ("ISOLATE", 1.34, "led_red")]):
        g.cyl(f"Power_led_{i}", (cx - 0.14, 8.93, z), (cx - 0.14, 8.91, z), 0.016, mat, 10)
        labels.text3d(f"Power_lab_{i}", lab, (cx + 0.04, 8.93, z), size=0.03, extrude=0.0015, mat="floor_mark", normal=(0, -1, 0), align="LEFT")
    g.box("Power_switch", (cx + 0.14, 8.92, 1.22), (0.05, 0.04, 0.08), "yellow", 0.002)
    # Local breaker plate
    g.box("Breaker_plate", (2.15, 8.97, 2.85), (1.05, 0.04, 0.22), "shell", 0.003)
    labels.text3d("Breaker_t", "L3-01  LOCAL BREAKER  AND  RESERVE POWER", (2.15, 8.94, 2.85), size=0.038, extrude=0.002, mat="ink", normal=(0, -1, 0))


def _supplies():
    x0, y0, x1, y1 = EQUIP["SuppliesCabinet"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cab = g.box_min("SupCab", (x1 - 0.08, y0, 0.88), (0.08, y1 - y0, 1.32), "shell", 0.005)
    g.support(cab, "Wall_E", "WORLD_+X", [(x1, cy, 1.5)], gap=0.05)
    g.box_min("SupCab_base", (x0, y0, 0.78), (x1 - x0, y1 - y0, 0.10), "graphite", 0.003)
    g.box_min("SupCab_L", (x0, y0, 0.88), (x1 - x0, 0.05, 1.32), "shell", 0.004)
    g.box_min("SupCab_R", (x0, y1 - 0.05, 0.88), (x1 - x0, 0.05, 1.32), "shell", 0.004)
    g.box_min("SupCab_top", (x0, y0, 2.12), (x1 - x0, y1 - y0, 0.08), "shell", 0.004)
    g.box("SupCab_glass_S", (x0 + 0.01, y0 + 0.42, 1.52), (0.012, 0.62, 1.00), "glass", 0.001)
    g.box("SupCab_glass_N", (x0 + 0.01, y1 - 0.42, 1.52), (0.012, 0.62, 1.00), "glass", 0.001)
    g.box("SupCab_mullion", (x0 + 0.02, cy, 1.52), (0.03, 0.03, 1.1), "darksteel", 0.001)
    g.box("SupCab_frame_S", (x0 + 0.02, y0 + 0.08, 1.52), (0.04, 0.05, 1.12), "graphite", 0.002)
    g.box("SupCab_frame_N", (x0 + 0.02, y1 - 0.08, 1.52), (0.04, 0.05, 1.12), "graphite", 0.002)
    g.handle("SupCab_h", (x0 - 0.03, y1 - 0.25, 1.45), 0.12)
    labels.text3d("SupCab_t", "MEDICAL SUPPLIES", (x0 - 0.02, cy, 2.12), size=0.04, extrude=0.002, mat="ink", normal=(-1, 0, 0))
    # Interior shelves + bottles
    for i, z in enumerate([1.05, 1.40, 1.75]):
        g.box_min(f"SupShelf_{i}", (x0 + 0.08, y0 + 0.08, z), (x1 - x0 - 0.14, y1 - y0 - 0.16, 0.03), "darksteel", 0.001)
        for k in range(4):
            by = y0 + 0.25 + k * 0.38
            g.cyl(f"SupBot_{i}_{k}", (x0 + 0.28, by, z + 0.03), (x0 + 0.28, by, z + 0.26), 0.028, "brushed" if k % 2 == 0 else "plastic_light", 10)
    g.box("SupBox", (x0 + 0.28, y0 + 0.35, 1.10), (0.16, 0.22, 0.10), "yellow", 0.003)


def _bench():
    x0, y0, x1, y1 = EQUIP["SupplyBench"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    body = g.box_min("Bench", (x0, y0, 0), (x1 - x0, y1 - y0, 0.88), "graphite", 0.005)
    g.support(body, "Floor", "WORLD_-Z", [(cx, cy, 0)])
    g.box_min("Bench_top", (x0 - 0.02, y0 - 0.02, 0.88), (x1 - x0 + 0.04, y1 - y0 + 0.06, 0.04), "shell", 0.004)
    for i, y in enumerate([y0 + 0.25, y0 + 0.85, y0 + 1.45]):
        g.box(f"Bench_draw_{i}", (x0 + 0.02, y, 0.45), (0.06, 0.42, 0.28), "shell", 0.003)
        g.box(f"Bench_h_{i}", (x0 + 0.00, y, 0.45), (0.02, 0.12, 0.02), "steel", 0.001)
    g.box("Bench_haz", (x0 + 0.04, cy, 0.08), (0.03, y1 - y0 - 0.1, 0.10), "hazard_fine", 0.0)
    # Worktop items
    g.box("Bench_box", (cx, y0 + 0.35, 0.96), (0.22, 0.16, 0.08), "yellow", 0.003)
    g.box("Bench_clip", (cx + 0.15, y0 + 1.2, 0.93), (0.18, 0.22, 0.01), "paper", 0.0)
    g.support(g.box("Bench_clip_board", (cx + 0.15, y0 + 1.2, 0.925), (0.16, 0.20, 0.006), "plastic", 0.001), "Bench_top", "WORLD_-Z", [(cx + 0.15, y0 + 1.2, 0.92)])
    g.cyl("Bench_thermos", (x0 + 0.22, y1 - 0.25, 0.92), (x0 + 0.22, y1 - 0.25, 1.18), 0.035, "brushed", 12)
    g.box("Bench_glove", (x0 + 0.35, y0 + 0.7, 0.93), (0.12, 0.18, 0.03), "orange_pad", 0.006)
    g.box("Medcrate", (x0 + 0.22, y0 + 0.22, 0.55), (0.28, 0.38, 0.22), "graphite", 0.004)
    labels.text3d("Medcrate_t", "MEDICAL SUPPLIES", (x0 + 0.07, y0 + 0.22, 0.55), size=0.03, extrude=0.0015, mat="floor_mark", normal=(-1, 0, 0))


def _wash():
    x0, y0, x1, y1 = EQUIP["Wash"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    g.box_min("Wash_bracket", (x0, y0, 0.88), (x1 - x0, y1 - y0, 0.08), "darksteel", 0.003)
    basin = g.box("Wash_basin", (cx, cy, 0.92), (0.42, 0.38, 0.12), "brushed", 0.004)
    g.support(basin, "Wall_E", "WORLD_+X", [(x1, cy, 0.92)], gap=0.08)
    g.box("Wash_bowl", (cx, cy, 0.90), (0.32, 0.28, 0.08), "graphite", 0.002)
    g.cyl("Wash_tap", (cx + 0.12, cy, 0.98), (cx + 0.12, cy, 1.18), 0.016, "brushed", 10)
    g.cyl("Wash_spout", (cx + 0.12, cy, 1.18), (cx - 0.02, cy, 1.16), 0.012, "brushed", 8)
    g.box("Wash_soap", (cx - 0.12, cy + 0.12, 0.99), (0.06, 0.06, 0.10), "plastic_light", 0.002)


def _recovery():
    x0, y0, x1, y1 = EQUIP["Recovery"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # Gurney frame
    frame = g.box("Rec_frame", (cx, cy, 0.62), (0.78, 2.05, 0.08), "shell", 0.004)
    g.support(frame, "Floor", "WORLD_-Z", [(x0 + 0.12, y0 + 0.18, 0.003), (x1 - 0.12, y1 - 0.18, 0.003)])
    for y in (y0 + 0.18, y1 - 0.18):
        for x in (x0 + 0.12, x1 - 0.12):
            g.cyl(f"Rec_leg_{x:.2f}_{y:.2f}", (x, y, 0.10), (x, y, 0.62), 0.022, "steel", 10)
            g.wheel(f"Rec_w_{x:.2f}_{y:.2f}", (x, y, 0.055), r=0.05, width=0.028)
    g.box("Rec_pad", (cx, cy, 0.72), (0.72, 1.95, 0.08), "pad", 0.01)
    g.box("Rec_head", (cx, y1 - 0.22, 0.80), (0.42, 0.28, 0.10), "pad", 0.01)
    g.box("Rec_rail_W", (x0 + 0.04, cy, 0.82), (0.03, 1.6, 0.05), "brushed", 0.002)
    g.box("Rec_rail_E", (x1 - 0.04, cy, 0.82), (0.03, 1.6, 0.05), "brushed", 0.002)
    g.box("Rec_stripe", (cx, y0 + 0.15, 0.68), (0.78, 0.08, 0.03), "hazard_fine", 0.0)
    # Towel with thickness
    towel = g.box("Rec_towel", (cx, cy - 0.15, 0.78), (0.32, 0.38, 0.03), "fabric", 0.008)
    g.box("Rec_towel_fold", (cx, cy - 0.08, 0.80), (0.28, 0.16, 0.025), "fabric", 0.006)
    g.support(towel, "Rec_pad", "WORLD_-Z", [(cx, cy - 0.15, 0.76)])
    labels.text3d("Rec_t", "OCC HEALTH", (x0 + 0.02, cy, 0.70), size=0.04, extrude=0.002, mat="ink", normal=(-1, 0, 0))
    # Mat under
    mat = g.box("Rec_mat", (cx, cy, 0.005), (0.72, 1.85, 0.008), "rubber", 0.0)
    g.support(mat, "Floor", "WORLD_-Z", [(cx, cy, 0.002)])


def _cart():
    # Small utility cart beside the door, west of the arrival lane (reference language).
    cx, cy = -1.95, 1.72
    top = g.box("Util_top", (cx, cy, 0.92), (0.52, 0.78, 0.04), "shell", 0.004)
    g.support(top, "Floor", "WORLD_-Z", [(cx, cy, 0)])
    g.box("Util_shelf", (cx, cy, 0.48), (0.50, 0.74, 0.03), "graphite", 0.003)
    g.box("Util_base", (cx, cy, 0.12), (0.50, 0.74, 0.04), "graphite", 0.003)
    for y in (cy - 0.32, cy + 0.32):
        for x in (cx - 0.20, cx + 0.20):
            g.cyl(f"Util_leg_{x:.2f}_{y:.2f}", (x, y, 0.12), (x, y, 0.92), 0.016, "steel", 8)
            g.wheel(f"Util_w_{x:.2f}_{y:.2f}", (x, y, 0.055), r=0.048, width=0.026)
    g.box("Util_panel", (cx, cy - 0.40, 0.50), (0.48, 0.03, 0.55), "graphite", 0.003)
    labels.text3d("Util_t", "MEDICAL SUPPLIES", (cx, cy - 0.42, 0.52), size=0.032, extrude=0.0015, mat="floor_mark", normal=(0, -1, 0))
    g.cyl("Util_bot1", (cx - 0.12, cy + 0.1, 0.94), (cx - 0.12, cy + 0.1, 1.16), 0.03, "brushed", 10)
    g.cyl("Util_bot2", (cx + 0.08, cy - 0.05, 0.94), (cx + 0.08, cy - 0.05, 1.12), 0.028, "plastic_light", 10)
    g.box("Util_tray", (cx + 0.12, cy + 0.18, 0.96), (0.16, 0.22, 0.06), "yellow", 0.003)
    gx, gy = -2.70, 1.15
    g.box("Trolley_frame", (gx, gy, 0.58), (0.70, 2.05, 0.08), "shell", 0.004)
    g.box("Trolley_pad", (gx, gy, 0.68), (0.62, 1.95, 0.08), "pad", 0.01)
    for y in (gy - 0.90, gy + 0.90):
        for x in (gx - 0.28, gx + 0.28):
            g.cyl(f"Tr_leg_{x:.2f}_{y:.2f}", (x, y, 0.10), (x, y, 0.58), 0.02, "steel", 8)
            g.wheel(f"Tr_w_{x:.2f}_{y:.2f}", (x, y, 0.05), r=0.048, width=0.026)
    g.box("Trolley_haz", (gx, gy - 0.98, 0.62), (0.70, 0.10, 0.05), "hazard_fine", 0.0)


def _stools():
    def stool(name, x, y):
        seat = g.cyl(name + "_seat", (x, y, 0.52), (x, y, 0.56), 0.16, "pad", 16, 0.004)
        g.support(seat, "Floor", "WORLD_-Z", [(x, y, 0)])
        g.cyl(name + "_col", (x, y, 0.12), (x, y, 0.52), 0.028, "steel", 10)
        g.cyl(name + "_base", (x, y, 0.04), (x, y, 0.08), 0.18, "graphite", 16)
        for a in range(5):
            ang = a * 2 * math.pi / 5
            px, py = x + 0.16 * math.cos(ang), y + 0.16 * math.sin(ang)
            g.cyl(f"{name}_c_{a}", (px, py, 0.035), (px, py, 0.07), 0.018, "rubber", 8)
    stool("Stool_con", -0.35, 7.55)
    stool("Stool_bench", 2.85, 1.55)
    stool("Stool_rec", 2.95, 6.15)


def _props():
    # Clipboard on console
    g.box("Prop_clip", (-0.9, 8.25, 0.79), (0.16, 0.22, 0.008), "paper", 0.0)
    g.box("Prop_clip_clip", (-0.9, 8.34, 0.80), (0.12, 0.04, 0.012), "steel", 0.001)
    labels.text3d("Prop_clip_t", "CONTINUITY RECEIPT", (-0.9, 8.25, 0.81), size=0.02, extrude=0.001, mat="ink", normal=(0, 0, 1))
    # Mug
    g.cyl("Prop_mug", (-1.05, 8.22, 0.77), (-1.05, 8.22, 0.88), 0.035, "plastic", 12)
    g.torus("Prop_mug_h", (-1.01, 8.22, 0.83), 0.03, 0.007, "plastic")
    # Gloves on OCRU lip
    g.box("Prop_glove", (-1.38, 4.2, 0.54), (0.10, 0.16, 0.03), "orange_pad", 0.006)
    # Waste bin near bench
    bin_ = g.box("Prop_bin", (3.55, 2.85, 0.22), (0.22, 0.22, 0.42), "graphite", 0.005)
    g.support(bin_, "Floor", "WORLD_-Z", [(3.55, 2.85, 0)])
    g.box("Prop_bin_ring", (3.55, 2.85, 0.42), (0.23, 0.23, 0.03), "shell", 0.002)
    # Fire extinguisher
    g.cyl("Ext", (3.78, 0.55, 0.15), (3.78, 0.55, 0.70), 0.055, "red", 14)
    g.support(g.box("Ext_br", (3.97, 0.55, 0.50), (0.04, 0.08, 0.25), "steel", 0.001), "Wall_E", "WORLD_+X", [(3.99, 0.55, 0.50)], gap=0.02)
    g.box("Ext_head", (3.78, 0.55, 0.74), (0.06, 0.08, 0.08), "steel", 0.002)
    g.box("Ext_tag", (3.72, 0.55, 0.45), (0.01, 0.06, 0.08), "paper", 0.0)
    # Wall phone / intercom
    g.box("Intercom", (-3.92, 1.55, 1.45), (0.06, 0.16, 0.22), "graphite", 0.003)
    g.cyl("Intercom_g", (-3.88, 1.55, 1.42), (-3.86, 1.55, 1.42), 0.04, "plastic", 10)
    # Hose reel near wash
    g.cyl("HoseReel", (3.78, 3.15, 1.15), (3.90, 3.15, 1.15), 0.09, "darksteel", 14)
    g.tube("WashHose", [(3.70, 3.15, 1.15), (3.55, 3.05, 0.95), (3.48, 2.95, 0.92)], 0.012, "rubber")
