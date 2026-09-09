"""Human-scale Organic Continuity and Recommissioning Unit. Original construction."""
from __future__ import annotations

import math

import labels
import mesh as g
from config import EQUIP

# Housing lining-flush on west wall.
OX0, OY0, OX1, OY1 = EQUIP["OCRU"]
# Derived
CX = (OX0 + OX1) / 2
CY = (OY0 + OY1) / 2
DEPTH = OX1 - OX0
LENGTH = OY1 - OY0
HEIGHT = 2.52
FACE_X = OX1  # opening faces +X


def build():
    root = g.empty("OCRU_ROOT", (CX, CY, 0), size=0.4, machine="OCRU")
    with g.use("OCRU"):
        _plinth()
        _shell()
        _opening()
        _chamber()
        _berth()
        _fascia()
        _status()
        _service()
        _maintenance()
        _graphics()
    return root


def _plinth():
    p = g.box("OCRU_plinth", (CX, CY, 0.06), (DEPTH + 0.04, LENGTH + 0.06, 0.12), "graphite", 0.006)
    g.support(p, "Floor", "WORLD_-Z", [(CX, CY, 0), (OX0 + 0.2, OY0 + 0.2, 0), (OX1 - 0.2, OY1 - 0.2, 0)])
    g.box("OCRU_kick", (FACE_X - 0.01, CY, 0.14), (0.04, LENGTH - 0.15, 0.16), "hazard", 0.0)
    g.box("OCRU_base_trim", (CX, CY, 0.18), (DEPTH - 0.02, LENGTH - 0.08, 0.04), "darksteel", 0.002)


def _shell():
    # Outer casing: not a single box. Split into roof, sides, rear, front cheeks.
    g.box("OCRU_rear", (OX0 + 0.06, CY, HEIGHT / 2 + 0.06), (0.12, LENGTH - 0.08, HEIGHT - 0.12), "shell", 0.005)
    g.box("OCRU_side_S", (CX, OY0 + 0.05, HEIGHT / 2 + 0.06), (DEPTH - 0.04, 0.10, HEIGHT - 0.12), "shell", 0.005)
    g.box("OCRU_side_N", (CX, OY1 - 0.05, HEIGHT / 2 + 0.06), (DEPTH - 0.04, 0.10, HEIGHT - 0.12), "shell", 0.005)
    g.box("OCRU_roof", (CX, CY, HEIGHT - 0.05), (DEPTH - 0.02, LENGTH - 0.04, 0.10), "shell", 0.006)
    # Front cheeks around the opening
    open_y0, open_y1 = OY0 + 0.55, OY1 - 0.45
    open_z0, open_z1 = 0.48, 2.18
    g.box("OCRU_cheek_S", (FACE_X - 0.07, (OY0 + open_y0) / 2, HEIGHT / 2 + 0.06), (0.14, open_y0 - OY0, HEIGHT - 0.12), "shell", 0.004)
    g.box("OCRU_cheek_N", (FACE_X - 0.07, (open_y1 + OY1) / 2, HEIGHT / 2 + 0.06), (0.14, OY1 - open_y1, HEIGHT - 0.12), "shell", 0.004)
    g.box("OCRU_brow", (FACE_X - 0.08, CY, (open_z1 + HEIGHT) / 2), (0.16, LENGTH - 0.12, HEIGHT - open_z1), "shell", 0.004)
    g.box("OCRU_sill", (FACE_X - 0.08, CY, open_z0 / 2 + 0.04), (0.16, LENGTH - 0.12, open_z0), "shell", 0.004)
    # Recessed panel bands
    g.box("OCRU_band", (CX, CY, 2.22), (DEPTH - 0.18, LENGTH - 0.22, 0.06), "graphite", 0.002)
    # Roof vents
    for i, y in enumerate([OY0 + 0.6, CY, OY1 - 0.6]):
        g.grille(f"OCRU_vent_{i}", (CX, y, HEIGHT + 0.02), (0.55, 0.28, 0.05), "darksteel", bars=5, axis="X")
    # Fastener rows on front cheeks
    g.bolts("OCRU_boltS", (FACE_X + 0.01, OY0 + 0.22, 0.7), (1, 0, 0), 6, 0.22, r=0.006, length=0.01)
    g.bolts("OCRU_boltN", (FACE_X + 0.01, OY1 - 0.22, 0.7), (1, 0, 0), 6, 0.22, r=0.006, length=0.01)


def _opening():
    open_y0, open_y1 = OY0 + 0.55, OY1 - 0.45
    open_z0, open_z1 = 0.48, 2.18
    oc = ((open_y0 + open_y1) / 2)
    # Deep jambs
    g.box("OCRU_jamb_S", (FACE_X - 0.22, open_y0 + 0.04, (open_z0 + open_z1) / 2), (0.42, 0.08, open_z1 - open_z0 + 0.08), "graphite", 0.004)
    g.box("OCRU_jamb_N", (FACE_X - 0.22, open_y1 - 0.04, (open_z0 + open_z1) / 2), (0.42, 0.08, open_z1 - open_z0 + 0.08), "graphite", 0.004)
    g.box("OCRU_jamb_top", (FACE_X - 0.22, oc, open_z1 + 0.03), (0.42, open_y1 - open_y0, 0.06), "graphite", 0.003)
    g.box("OCRU_jamb_bot", (FACE_X - 0.22, oc, open_z0 - 0.02), (0.42, open_y1 - open_y0, 0.06), "darksteel", 0.003)
    # Inner reveal as a frame only — do not plug the chamber.
    g.box("OCRU_reveal_S", (FACE_X - 0.28, open_y0 + 0.10, (open_z0 + open_z1) / 2), (0.28, 0.04, open_z1 - open_z0 - 0.10), "chamber", 0.002)
    g.box("OCRU_reveal_N", (FACE_X - 0.28, open_y1 - 0.10, (open_z0 + open_z1) / 2), (0.28, 0.04, open_z1 - open_z0 - 0.10), "chamber", 0.002)
    g.box("OCRU_reveal_T", (FACE_X - 0.28, oc, open_z1 - 0.04), (0.28, open_y1 - open_y0 - 0.16, 0.04), "chamber", 0.002)
    g.box("OCRU_reveal_B", (FACE_X - 0.28, oc, open_z0 + 0.04), (0.28, open_y1 - open_y0 - 0.16, 0.04), "chamber", 0.002)
    g.box("OCRU_seal_S", (FACE_X - 0.01, open_y0 + 0.06, (open_z0 + open_z1) / 2), (0.03, 0.03, open_z1 - open_z0 - 0.08), "rubber", 0.001)
    g.box("OCRU_seal_N", (FACE_X - 0.01, open_y1 - 0.06, (open_z0 + open_z1) / 2), (0.03, 0.03, open_z1 - open_z0 - 0.08), "rubber", 0.001)
    g.box("OCRU_seal_T", (FACE_X - 0.01, oc, open_z1 - 0.04), (0.03, open_y1 - open_y0 - 0.10, 0.03), "rubber", 0.001)
    g.box("OCRU_seal_B", (FACE_X - 0.01, oc, open_z0 + 0.04), (0.03, open_y1 - open_y0 - 0.10, 0.03), "rubber", 0.001)
    # Upper glass visor as a thin bar, not a plug
    g.box("OCRU_glass", (FACE_X - 0.03, oc, open_z1 - 0.12), (0.02, open_y1 - open_y0 - 0.22, 0.16), "glass", 0.001)
    g.box("OCRU_glass_frame", (FACE_X - 0.04, oc, open_z1 - 0.12), (0.04, open_y1 - open_y0 - 0.18, 0.20), "darksteel", 0.002)
    # Transfer lip / roller
    g.box("OCRU_lip", (FACE_X + 0.08, oc, 0.50), (0.18, 1.85, 0.05), "brushed", 0.003)
    g.cyl("OCRU_roller", (FACE_X + 0.14, oc - 0.8, 0.54), (FACE_X + 0.14, oc + 0.8, 0.54), 0.018, "steel", 12)
    # Track
    g.box("OCRU_track_S", (FACE_X - 0.15, open_y0 + 0.12, 0.46), (0.55, 0.03, 0.03), "steel", 0.001)
    g.box("OCRU_track_N", (FACE_X - 0.15, open_y1 - 0.12, 0.46), (0.55, 0.03, 0.03), "steel", 0.001)


def _chamber():
    open_y0, open_y1 = OY0 + 0.55, OY1 - 0.45
    inner_x0 = OX0 + 0.22
    inner_x1 = FACE_X - 0.42
    # Inner walls
    g.box_min("OCRU_inner_W", (inner_x0, open_y0 + 0.08, 0.48), (0.04, open_y1 - open_y0 - 0.16, 1.68), "chamber", 0.002)
    g.box_min("OCRU_inner_S", (inner_x0, open_y0 + 0.08, 0.48), (inner_x1 - inner_x0, 0.04, 1.68), "chamber", 0.002)
    g.box_min("OCRU_inner_N", (inner_x0, open_y1 - 0.12, 0.48), (inner_x1 - inner_x0, 0.04, 1.68), "chamber", 0.002)
    g.box_min("OCRU_inner_ceil", (inner_x0, open_y0 + 0.08, 2.10), (inner_x1 - inner_x0, open_y1 - open_y0 - 0.16, 0.06), "graphite", 0.002)
    for i, y in enumerate([open_y0 + 0.45, CY, open_y1 - 0.45]):
        g.box(f"OCRU_cyan_{i}", ((inner_x0 + inner_x1) / 2, y, 2.06), (inner_x1 - inner_x0 - 0.15, 0.05, 0.04), "cyan", 0.0)
        g.box(f"OCRU_cyan_side_{i}", (inner_x1 - 0.06, y, 1.55), (0.03, 0.04, 0.7), "cyan", 0.0)
    # Side interior rails
    g.box("OCRU_int_rail_S", (inner_x0 + 0.35, open_y0 + 0.18, 1.15), (0.9, 0.03, 0.04), "steel", 0.002)
    g.box("OCRU_int_rail_N", (inner_x0 + 0.35, open_y1 - 0.18, 1.15), (0.9, 0.03, 0.04), "steel", 0.002)
    # Floor of chamber
    g.box_min("OCRU_chamber_floor", (inner_x0, open_y0 + 0.08, 0.42), (inner_x1 - inner_x0, open_y1 - open_y0 - 0.16, 0.06), "steel", 0.002)


def _berth():
    # Adult berth 0.88 x 2.20, surface 1.02, along Y, centered in chamber
    bw, bl, bz = 0.88, 2.20, 1.02
    bx = FACE_X - 0.78
    by = CY + 0.08
    frame = g.box("OCRU_berth_frame", (bx, by, bz - 0.08), (bw + 0.08, bl + 0.08, 0.08), "darksteel", 0.004)
    g.support(frame, "OCRU_chamber_floor", "WORLD_-Z", [(bx, by, 0.48)])
    for y in (by - 0.85, by + 0.85):
        g.box(f"OCRU_leg_{y:.2f}", (bx, y, 0.62), (0.07, 0.07, 0.28), "steel", 0.002)
    g.box("OCRU_rail_W", (bx - bw / 2 - 0.02, by, bz + 0.04), (0.03, bl - 0.2, 0.05), "brushed", 0.002)
    g.box("OCRU_rail_E", (bx + bw / 2 + 0.02, by, bz + 0.04), (0.03, bl - 0.2, 0.05), "brushed", 0.002)
    # Segmented pads
    g.box("OCRU_pad_0", (bx, by, bz), (bw - 0.04, bl - 0.18, 0.08), "pad", 0.02)
    for i in range(4):
        y = by - 0.85 + i * 0.42
        g.box(f"OCRU_seam_{i}", (bx, y, bz + 0.042), (bw - 0.10, 0.012, 0.006), "rubber", 0.0)
    # Orange headrest toward +Y
    g.box("OCRU_head", (bx, by + bl / 2 - 0.12, bz + 0.07), (0.42, 0.22, 0.12), "orange_pad", 0.01)
    g.box("OCRU_head_base", (bx, by + bl / 2 - 0.12, bz + 0.01), (0.36, 0.18, 0.04), "graphite", 0.002)
    # Restraint buckles
    for i, y in enumerate([by - 0.4, by + 0.35]):
        g.box(f"OCRU_buckle_{i}", (bx + bw / 2 - 0.06, y, bz + 0.04), (0.08, 0.05, 0.03), "yellow", 0.002)
        g.box(f"OCRU_strap_{i}", (bx, y, bz + 0.035), (bw - 0.1, 0.02, 0.008), "rubber", 0.0)
    # Handles
    g.handle("OCRU_handle_S", (bx + bw / 2 + 0.08, by - 0.7, bz - 0.05), width=0.16)
    g.handle("OCRU_handle_N", (bx + bw / 2 + 0.08, by + 0.7, bz - 0.05), width=0.16)


def _fascia():
    # Top identity band on +X face
    g.box("OCRU_fascia", (FACE_X + 0.01, CY, 2.36), (0.06, LENGTH - 0.2, 0.28), "shell", 0.004)
    labels.text3d("OCRU_name", "OCRU", (FACE_X + 0.05, CY - 0.55, 2.40), size=0.13, extrude=0.004, mat="ink", normal=(1, 0, 0), align="LEFT")
    labels.text3d("OCRU_long", "ORGANIC CONTINUITY AND RECOMMISSIONING UNIT", (FACE_X + 0.05, CY - 0.55, 2.26), size=0.035, extrude=0.002, mat="ink", normal=(1, 0, 0), align="LEFT")
    labels.text3d("OCRU_t01", "T-01", (FACE_X + 0.05, CY + 1.55, 2.40), size=0.11, extrude=0.004, mat="ink", normal=(1, 0, 0), align="RIGHT")
    # Caution
    g.box("OCRU_caution_plate", (FACE_X + 0.02, CY - 0.15, 0.36), (0.03, 0.9, 0.12), "shell", 0.002)
    labels.text3d("OCRU_caution", "CAUTION  KEEP CLEAR  AUTOMATED SYSTEM", (FACE_X + 0.05, CY - 0.15, 0.36), size=0.028, extrude=0.0015, mat="ink", normal=(1, 0, 0))


def _status():
    # Local module on north jamb
    jx, jy, jz = FACE_X + 0.02, OY1 - 0.32, 1.55
    g.box("OCRU_status_body", (jx, jy, jz), (0.08, 0.16, 0.42), "graphite", 0.003)
    g.quad("OCRU_status_screen", (jx + 0.055, jy, jz + 0.06), 0.12, 0.16, "screen_small", normal=(1, 0, 0))
    for i, (z, mat) in enumerate([(jz - 0.12, "led_green"), (jz - 0.18, "led_amber")]):
        g.cyl(f"OCRU_led_{i}", (jx + 0.05, jy, z), (jx + 0.07, jy, z), 0.012, mat, 10)
    g.box("OCRU_key", (jx + 0.04, jy, jz - 0.28), (0.03, 0.08, 0.04), "yellow", 0.002)
    # South side small panel
    g.box("OCRU_south_mod", (FACE_X + 0.02, OY0 + 0.32, 1.55), (0.07, 0.14, 0.32), "graphite", 0.003)
    g.cyl("OCRU_south_knob", (FACE_X + 0.07, OY0 + 0.32, 1.48), (FACE_X + 0.09, OY0 + 0.32, 1.48), 0.018, "steel", 10)


def _service():
    # Suit-service stack on +Y end of machine
    sx, sy, sz = FACE_X - 0.35, OY1 - 0.02, 1.35
    g.box("OCRU_service", (sx, sy, sz), (0.55, 0.14, 1.55), "graphite", 0.004)
    g.box("OCRU_service_plate", (sx, sy + 0.08, sz), (0.42, 0.04, 1.2), "shell_dark", 0.002)
    labels.text3d("OCRU_life", "LIFE REBUILDS VALUE", (sx, sy + 0.12, 1.85), size=0.04, extrude=0.002, mat="floor_mark", normal=(0, 1, 0))
    # Couplings
    for i, z in enumerate([0.85, 1.15, 1.45, 1.75, 2.05]):
        g.cyl(f"OCRU_coup_{i}", (sx + 0.12, sy + 0.08, z), (sx + 0.12, sy + 0.16, z), 0.028, "brushed", 12)
        g.torus(f"OCRU_coup_ring_{i}", (sx + 0.12, sy + 0.16, z), 0.032, 0.006, "rubber")
    # Black corrugated hoses up to trays
    paths = [
        [(sx + 0.12, sy + 0.18, 0.85), (sx + 0.35, sy + 0.35, 1.6), (sx + 0.2, sy + 0.5, 2.6), (-2.4, 6.9, 3.42)],
        [(sx + 0.12, sy + 0.18, 1.15), (sx + 0.45, sy + 0.4, 1.9), (-2.15, 7.1, 3.40)],
        [(sx + 0.12, sy + 0.18, 1.45), (sx + 0.5, sy + 0.55, 2.3), (-2.35, 7.4, 3.44)],
        [(sx + 0.12, sy + 0.18, 1.75), (sx + 0.25, sy + 0.7, 2.8), (-2.55, 7.6, 3.40)],
        [(sx + 0.12, sy + 0.18, 2.05), (sx + 0.05, sy + 0.45, 2.9), (-2.45, 6.6, 3.43)],
    ]
    for i, pts in enumerate(paths):
        g.tube(f"OCRU_hose_{i}", pts, 0.022 + (i % 3) * 0.004, "rubber")
    # Suit port labelled
    g.box("OCRU_port_label", (sx + 0.22, sy + 0.09, 0.62), (0.18, 0.02, 0.06), "yellow", 0.001)
    labels.text3d("OCRU_port_t", "SUIT SERVICE", (sx + 0.22, sy + 0.11, 0.62), size=0.025, extrude=0.001, mat="ink", normal=(0, 1, 0))


def _maintenance():
    # Hatch on south end
    hx, hy = CX, OY0 + 0.02
    g.box("OCRU_hatch", (hx, hy, 1.15), (0.55, 0.05, 0.85), "shell", 0.004)
    g.box("OCRU_hatch_inset", (hx, hy + 0.02, 1.15), (0.42, 0.02, 0.65), "graphite", 0.002)
    g.handle("OCRU_hatch_handle", (hx, hy - 0.04, 1.15), width=0.18)
    g.box("OCRU_hatch_latch", (hx + 0.18, hy - 0.03, 1.45), (0.08, 0.04, 0.05), "yellow", 0.002)
    labels.text3d("OCRU_hatch_t", "MAINT", (hx, hy - 0.04, 0.85), size=0.04, extrude=0.002, mat="ink", normal=(0, -1, 0))


def _graphics():
    # Side slogan already on service. Occupancy stripe on south cheek.
    g.box("OCRU_stripe_S", (FACE_X + 0.02, OY0 + 0.18, 1.9), (0.03, 0.08, 0.55), "hazard_fine", 0.0)
    g.box("OCRU_stripe_N", (FACE_X + 0.02, OY1 - 0.18, 1.9), (0.03, 0.08, 0.55), "hazard_fine", 0.0)
    # Suit-service visible on the north jamb, facing the room
    jx, jy = FACE_X + 0.06, OY1 - 0.38
    g.box("OCRU_suit_block", (jx, jy, 1.45), (0.10, 0.18, 0.85), "graphite", 0.003)
    for i, z in enumerate([1.15, 1.40, 1.65, 1.90]):
        g.cyl(f"OCRU_suit_c_{i}", (jx + 0.06, jy, z), (jx + 0.12, jy, z), 0.022, "brushed", 12)
        g.tube(f"OCRU_suit_h_{i}", [(jx + 0.12, jy, z), (jx + 0.35, jy + 0.15, z + 0.25), (jx + 0.2, jy + 0.4, 2.6), (-2.2, 6.9, 3.40)], 0.018 + i * 0.003, "rubber")
    labels.text3d("OCRU_suit_t", "SUIT SERVICE", (jx + 0.08, jy - 0.02, 0.95), size=0.028, extrude=0.0015, mat="yellow", normal=(1, 0, 0))
