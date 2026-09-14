"""Dimensioned SVG floorplan. No Blender. Implementation decision, not a certified drawing."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "blender"))
from layout import *

OUT = Path(__file__).resolve().parent
scale = 42  # px per metre
pad = 80


def sx(x):
    return pad + (x - X0) * scale


def sy(y):
    return pad + (Y1 - y) * scale  # Y up in plan


W = int((X1 - X0) * scale + pad * 2)
H = int((Y1 - Y0) * scale + pad * 2 + 70)


def rect(x0, y0, x1, y1, fill, stroke="#2a2d32", sw=1.5, extra=""):
    return f'<rect x="{sx(x0):.1f}" y="{sy(y1):.1f}" width="{(x1-x0)*scale:.1f}" height="{(y1-y0)*scale:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">',
    '<rect width="100%" height="100%" fill="#d8d4c8"/>',
    f'<text x="{W/2:.0f}" y="28" text-anchor="middle" font-size="18" fill="#2a2d32">CSB-01 Turbine Condenser Bay — dimensioned floorplan (metres)</text>',
    f'<text x="{W/2:.0f}" y="48" text-anchor="middle" font-size="11" fill="#5a5550">Local origin D01. Turbine = local + {ORIGIN_IN_TURBINE}. Agent-authored implementation, not a certified engineering drawing.</text>',
    rect(X0, Y0, X1, Y1, "#c4c0b4", "#2a2d32", 3),
]
# Equipment
cx, cy = CD_C[0], CD_C[1]
parts.append(rect(cx - CD_LEN_X / 2, cy - CD_WID_Y / 2, cx + CD_LEN_X / 2, cy + CD_WID_Y / 2, "#c8c5b9", "#6a4a2a"))
parts.append(rect(cx - CD_LEN_X / 2 - WB_DEPTH, cy - CD_WID_Y / 2 + 0.1, cx - CD_LEN_X / 2, cy + CD_WID_Y / 2 - 0.1, "#b56d38", "#6a4a2a"))
parts.append(rect(cx + CD_LEN_X / 2, cy - CD_WID_Y / 2 + 0.1, cx + CD_LEN_X / 2 + WB_DEPTH, cy + CD_WID_Y / 2 - 0.1, "#b56d38", "#6a4a2a"))
parts.append(rect(EXH_C[0] - EXH_X / 2, EXH_C[1] - EXH_Y / 2, EXH_C[0] + EXH_X / 2, EXH_C[1] + EXH_Y / 2, "none", "#a34332", 2, 'stroke-dasharray="6 4"'))
parts.append(rect(P1[0] - 0.75, P1[1] - 0.4, P1[0] + 0.75, P1[1] + 0.4, "#41444a"))
parts.append(rect(P2[0] - 0.75, P2[1] - 0.4, P2[0] + 0.75, P2[1] + 0.4, "#41444a"))
parts.append(rect(EJ_C[0] - 0.55, EJ_C[1] - 0.75, EJ_C[0] + 0.55, EJ_C[1] + 0.75, "#41444a"))
parts.append(rect(X0, OP_C[1] - 0.75, X0 + 0.55, OP_C[1] + 0.75, "#30383c"))
parts.append(rect(6.2, 1.2, 9.45, 7.2, "none", "#c49c40", 2, 'stroke-dasharray="8 5"'))
parts.append(rect(STAIR_X0, STAIR_Y0, STAIR_X1, STAIR_Y1, "#7c878a"))
# Door
parts.append(rect(-D01_W / 2, Y0 - 0.12, D01_W / 2, Y0 + 0.08, "#b56d38", "#2a2d32", 2))
# Labels
def lab(x, y, t, fill="#233037", size=11):
    return f'<text x="{sx(x):.1f}" y="{sy(y):.1f}" text-anchor="middle" font-size="{size}" fill="{fill}">{t}</text>'

parts += [
    lab(cx, cy, "CD-01"),
    lab(EXH_C[0], EXH_C[1] + 1.05, "U04 receive 2.5×1.5", "#a34332", 10),
    lab(P1[0], P1[1], "CEP-A", "#eee", 10),
    lab(P2[0], P2[1], "CEP-B", "#eee", 10),
    lab(EJ_C[0], EJ_C[1], "EJ-01", "#eee", 10),
    lab(X0 + 0.28, OP_C[1], "OP", "#eee", 10),
    lab(7.8, 4.05, "3.5 m bundle clear", "#8a6a20", 10),
    lab(0, -0.45, "D01 2.0×2.4  −Y", "#6a4a2a", 10),
    lab(IF_CW_SUPPLY[0] - 0.4, 3.2, "CW S", "#6a4a2a", 10),
    lab(IF_CW_RETURN[0] - 0.4, 4.9, "CW R", "#6a4a2a", 10),
    lab(IF_CONDENSATE_HANDOFF[0], 0.35, "U02 handoff", "#6a4a2a", 10),
]
# Dimensions
parts.append(f'<text x="{sx((X0+X1)/2):.1f}" y="{sy(Y0)-28:.1f}" text-anchor="middle" font-size="12">{X1-X0:.2f} m clear X</text>')
parts.append(f'<text x="{sx(X0)-24:.1f}" y="{sy((Y0+Y1)/2):.1f}" text-anchor="middle" font-size="12" transform="rotate(-90 {sx(X0)-24:.1f} {sy((Y0+Y1)/2):.1f})">{Y1-Y0:.2f} m clear Y</text>')
parts.append(f'<text x="{pad}" y="{H-18}" font-size="10" fill="#5a5550">Height 6.00 m. Floor at turbine Z −6.00. Ceiling opening maps to turbine (4.60, 11.45, 0). Do not treat this SVG as saved-geometry proof.</text>')
parts.append("</svg>")
(OUT / "floorplan.svg").write_text("\n".join(parts), encoding="utf-8")
print("wrote", OUT / "floorplan.svg")
