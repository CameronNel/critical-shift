"""Generate original CP-A02 vector plan and validate the section-local contract.

This validates architectural reservations, not Blender geometry or game physics.
Uses the Python standard library. Optional SVG rasterization is separate.
"""
from pathlib import Path
import json
import math
import textwrap
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE.parent / "interface.json").read_text(encoding="utf-8"))
SCALE, OX, OY = 55, 420, 960
INK, MUTED, GRID = "#203237", "#586c71", "#d8e0df"
TEAL, TEAL_LIGHT = "#276b70", "#d5ece8"
AMBER, AMBER_LIGHT = "#936621", "#fcf0cf"
SVG = []


def px(x):
    return OX + x * SCALE


def py(y):
    return OY - y * SCALE


def text(x, y, value, size=14, color=INK, anchor="start", weight="normal", rotate=None):
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    SVG.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}"{transform}>{escape(str(value))}</text>')


def line(x1, y1, x2, y2, color=INK, width=1.2, dash=None):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    SVG.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}"{ds}/>')


def rect(x, y, w, h, fill="none", stroke=INK, width=1.2, dash=None, radius=0):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    SVG.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"{ds}/>')


def bounds_rect(b, fill="none", stroke=INK, width=1.2, dash=None):
    a, z = b["min"], b["max"]
    rect(px(a[0]), py(z[1]), (z[0]-a[0])*SCALE, (z[1]-a[1])*SCALE, fill, stroke, width, dash)


def dim_h(a, b, y, reference_y, label):
    for x in (a, b):
        line(px(x), py(reference_y), px(x), y, MUTED, .8)
        line(px(x)-4, y+4, px(x)+4, y-4, INK, 1)
    line(px(a), y, px(b), y, INK, 1)
    text((px(a)+px(b))/2, y-8, label, 13, INK, "middle")


def dim_v(a, b, x, reference_x, label):
    for y in (a, b):
        line(px(reference_x), py(y), x, py(y), MUTED, .8)
        line(x-4, py(y)+4, x+4, py(y)-4, INK, 1)
    line(x, py(a), x, py(b), INK, 1)
    text(x-9, (py(a)+py(b))/2, label, 13, INK, "middle", rotate=-90)


def paragraph(x, y, content, columns=58, size=14, leading=20, color=MUTED):
    for row in textwrap.wrap(content, columns):
        text(x, y, row, size, color)
        y += leading
    return y


def transform(x, y):
    c, s = math.cos(math.radians(-135)), math.sin(math.radians(-135))
    return [8.4+c*x-s*y, -8.4+s*x+c*y]


def overlap(a, b):
    return all(min(a["max"][i], b["max"][i])-max(a["min"][i], b["min"][i]) > 1e-7 for i in range(3))


def validate():
    clear = DATA["shell"]["clear_bounds"]
    equipment = DATA["equipment_envelopes"]
    solids = equipment + DATA["partitions"]
    conflicts = []
    declared_interfaces = []
    for solid in solids:
        for reserved in DATA["keep_clear_volumes"]:
            if overlap(solid["bounds"], reserved["bounds"]):
                declaration = next((x for x in reserved.get("intentional_fixed_interface_overlap", []) if x["object_id"] == solid["id"]), None)
                if declaration:
                    declared_interfaces.append({"solid": solid["id"], "reserved_volume": reserved["id"], "reason": declaration["reason"]})
                else:
                    conflicts.append([solid["id"], reserved["id"]])
    outside = [e["id"] for e in solids if any(e["bounds"]["min"][i] < clear["min"][i]-1e-7 or e["bounds"]["max"][i] > clear["max"][i]+1e-7 for i in range(3))]
    equipment_clashes = [[a["id"], b["id"]] for i, a in enumerate(solids) for b in solids[i+1:] if overlap(a["bounds"], b["bounds"])]
    low, high = DATA["shell"]["outer_bounds"]["min"], DATA["shell"]["outer_bounds"]["max"]
    polygon = [transform(x, y) for x, y in [(low[0], low[1]), (high[0], low[1]), (high[0], high[1]), (low[0], high[1])]]
    endpoints = [transform(-2.5, 0), transform(2.5, 0)]
    reference = DATA["proposed_reactor_connection"]
    endpoint_error = max(math.dist(a, b) for a, b in zip(endpoints, reference["reactor_portal_endpoints_xy"]))
    ymax = max(p[1] for p in polygon)
    control_gap = reference["reactor_control_gross_xy"]["min"][1]-ymax
    stair_gap = reference["reactor_stair_gross_xy"]["min"][1]-ymax
    main = next(z for z in DATA["keep_clear_volumes"] if z["id"] == "KC-MAIN")["bounds"]
    pump_a = next(e for e in equipment if e["id"] == "CP-PUMP-A")["bounds"]
    pump_b = next(e for e in equipment if e["id"] == "CP-PUMP-B")["bounds"]
    hx = next(e for e in equipment if e["id"] == "CP-HX-01")["bounds"]
    result = {
        "revision": DATA["revision"], "scope": "Section-local JSON envelope arithmetic and original SVG generation; not Blender collision or engine certification",
        "checks": {"permanent_solids_vs_keep_clear_conflicts": conflicts, "permanent_solid_pair_conflicts": equipment_clashes, "solids_outside_clear_hall": outside,
                   "declared_fixed_interface_overlaps": declared_interfaces, "main_lane_width_m": main["max"][0]-main["min"][0], "main_lane_headroom_m": main["max"][2], "between_pumps_operator_lane_m": pump_b["min"][1]-pump_a["max"][1],
                   "exchanger_reach_strip_width_m": hx["min"][0]-main["max"][0], "section_min_y_m": low[1], "proposed_portal_endpoint_max_error_m": endpoint_error,
                   "proposed_outer_shell_reactor_polygon_xy": polygon, "control_y_separation_m": control_gap, "stair_y_separation_m": stair_gap,
                   "reactor_inner_hall_separating_halfplane_min_x_minus_y": min(p[0]-p[1] for p in polygon), "reactor_se_facet_x_minus_y": 16.8},
        "acceptance_status": "S03 design target alignment only; as-built acceptance pending",
        "unverified": ["Actual Blender geometry and support contacts", "S03 bench depth/upstand trim to target Y12.3..13", "West edge of bench standing strip beside fully open D02 leaf", "Runtime cart/rescue navigation, interactions, power, failures and recovery", "Shared facade seam against 0.36m reactor exterior wall", "New turbine-room footprint and utility endpoints", "Cold-start visual acceptance"],
        "status": "PASS"
    }
    assert not conflicts and not equipment_clashes and not outside, result
    assert abs(result["checks"]["main_lane_width_m"]-2.2) < 1e-7
    assert result["checks"]["between_pumps_operator_lane_m"] >= 1.3-1e-7
    assert result["checks"]["exchanger_reach_strip_width_m"] >= 1.2-1e-7
    assert endpoint_error < 1e-6 and control_gap > 0 and stair_gap > 0
    assert low[1] >= 0
    (HERE / "validation.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    return result


def draw():
    rect(0, 0, 1450, 1130, "#fbfcfa", "none")
    rect(28, 28, 1394, 1074, "none", GRID)
    text(58, 74, "CRITICAL SHIFT  /  COOLING SUPPORT PLANT", 27, INK, weight="bold")
    text(58, 104, "CP-A02  ·  DIMENSIONED LOCAL PLAN + PORTAL SECTION  ·  08 SEP 2026", 15, MUTED)
    text(58, 130, "METRES  |  entry (0,0,0)  |  +Y into room  |  +Z up  |  proposed module, connection not applied", 14, MUTED)
    line(58, 148, 1392, 148, GRID)
    for x, col, label in [(60, TEAL_LIGHT, "Permanent cart lane"), (285, AMBER_LIGHT, "Service / working clearance"), (588, "#dce0dd", "Permanent equipment")]:
        rect(x, 164, 22, 14, col, MUTED, .6)
        text(x+31, 176, label, 12, MUTED)

    bounds_rect(DATA["shell"]["outer_bounds"], "#bec9c5", INK, 2)
    bounds_rect(DATA["shell"]["clear_bounds"], "#f5f6f0", INK, 1.5)
    for x in range(-5, 6):
        line(px(x), py(0), px(x), py(13), GRID, .55)
    for y in range(1, 13):
        line(px(-5.5), py(y), px(5.5), py(y), GRID, .55)
    for keep in DATA["keep_clear_volumes"]:
        if keep["id"] == "KC-HX-HOIST":
            continue  # Above-plan hoist zone has the same footprint as withdrawal.
        fill = TEAL_LIGHT if keep["id"] == "KC-MAIN" else AMBER_LIGHT
        stroke = TEAL if keep["id"] == "KC-MAIN" else AMBER
        bounds_rect(keep["bounds"], fill, stroke, 1, "5 3")
    for part in DATA["partitions"]:
        bounds_rect(part["bounds"], "#83968f", INK, 1)
    for a, b in [(-5.5, -2.5), (2.5, 5.5)]:
        bounds_rect({"min": [a, 0, 0], "max": [b, .3, 5.8]}, "#bec9c5", INK, 1.5)
    for eq in DATA["equipment_envelopes"]:
        bounds_rect(eq["bounds"], "#dce0dd", INK, 1.6)
    for name, cy in [("A", 4.15), ("B", 7.55)]:
        # Authored pump symbols: cast casing, shaft/coupling and aisle-facing motor.
        SVG.append(f'<circle cx="{px(-4.18):.2f}" cy="{py(cy):.2f}" r="25" fill="#87a5a0" stroke="{INK}" stroke-width="1.5"/>')
        line(px(-3.73), py(cy), px(-3.05), py(cy), INK, 4)
        rect(px(-3.15), py(cy+.4), .98*SCALE, .8*SCALE, "#77988f", INK, 1.2, radius=8)
        for y in [cy-.2, cy, cy+.2]:
            line(px(-3.05), py(y), px(-2.28), py(y), TEAL, 1)
        text(px(-3.425), py(cy+.79), f"PUMP {name}  /  3.05 × 2.10", 12, INK, "middle", "bold")
        text(px(-3.425), py(cy-.78), "SHAFT X  →  MOTOR TO AISLE", 10, MUTED, "middle")
    rect(px(2.6), py(8.8), 1.7*SCALE, 3.8*SCALE, "#739a9a", INK, 1.5, radius=32)
    for y in [4.95, 5.2, 8.6, 8.85]:
        line(px(2.58), py(y), px(4.32), py(y), INK, 2)
    text(px(3.45), py(6.9), "HX-01", 18, "#ffffff", "middle", "bold")
    text(px(3.45), py(6.52), "HEAT EXCHANGER", 10, "#ffffff", "middle")
    text(px(3.45), py(6.15), "2.30 × 4.70 ENV.", 11, "#ffffff", "middle")
    text(px(3.3), py(11.6), "TUBE WITHDRAWAL", 13, AMBER, "middle", "bold")
    text(px(3.3), py(11.15), "2.60 × 3.50  /  KEEP EMPTY", 10, AMBER, "middle")
    text(px(3.3), py(10.86), "HOIST WORK ZONE ABOVE", 9, AMBER, "middle")
    line(px(3.3), py(9.65), px(3.3), py(10.65), AMBER, 2)
    line(px(3.3), py(10.65), px(3.15), py(10.42), AMBER, 2)
    line(px(3.3), py(10.65), px(3.45), py(10.42), AMBER, 2)
    text(px(1.72), py(7.5), "1.20 REACH STRIP", 10, AMBER, "middle", rotate=-90)
    text(px(0), py(6.5), "PERMANENT CART / RESCUE LANE  ·  2.20 m", 15, TEAL, "middle", "bold", -90)
    for y, label in [(2.35, "1.40 OPERATOR LANE"), (5.85, "1.30 SHARED OPERATOR LANE"), (9.3, "1.40 ALCOVE / PUMP ACCESS")]:
        text(px(-3.05), py(y), label, 11, AMBER, "middle")
    # Door leaf and quarter-circle swept arc.
    door = DATA["portals"][1]["door"]
    h = (px(door["hinge"][0]), py(door["hinge"][1]))
    closed = (px(door["closed_leaf_end"][0]), py(door["closed_leaf_end"][1]))
    opened = (px(door["open_leaf_end"][0]), py(door["open_leaf_end"][1]))
    reserved_open = (h[0], py(door["hinge"][1]+door["leaf_length"]))
    door_radius = door["leaf_length"] * SCALE
    line(*h, *opened, INK, 2)
    line(*h, *closed, MUTED, 1, "4 3")
    SVG.append(f'<path d="M {closed[0]:.2f} {closed[1]:.2f} A {door_radius} {door_radius} 0 0 0 {reserved_open[0]:.2f} {reserved_open[1]:.2f}" fill="none" stroke="{AMBER}" stroke-width="1.3" stroke-dasharray="4 3"/>')
    text(px(-4.1), py(10)-8, "D02 / 1.20", 10, INK, "middle")
    text(px(-3.65), py(12.61), "BENCH 2.80 × 0.70", 11, INK, "middle", "bold")
    text(px(-3.65), py(11.78), "0.90 STANDING STRIP", 10, AMBER, "middle")
    text(px(-2.39365), py(10.95), "CART", 9, INK, "middle")
    text(px(4.85), py(1.37), "WALL RESTART", 9, INK, "middle", "bold")
    text(px(4.125), py(2.19), "1.45", 10, AMBER, "middle")
    line(px(4.86), py(3.15), px(5.15), py(3.15), TEAL, 5)
    text(px(4.32), py(3.5), "CAPPED HOSE PORT", 9, TEAL, "middle")
    # Fixed-open entry: erase no shell outside portal, preserve five-metre aperture.
    line(px(-2.5), py(0), px(2.5), py(0), "#fbfcfa", 5)
    line(px(-2.5), py(0), px(2.5), py(0), TEAL, 1.5, "5 3")
    for x in [-2.5, 2.5]:
        line(px(x), py(0), px(x), py(.6), INK, 3)
    SVG.append(f'<circle cx="{px(0)}" cy="{py(0)}" r="4" fill="{TEAL}"/>')
    text(px(0), py(0)+63, "P01  /  5.00 W × 5.00 H  /  OVERHEAD DOOR FIXED OPEN", 12, INK, "middle", "bold")
    dim_h(-5.5, 5.5, 213, 13, "11.00 CLEAR  /  11.60 OUTSIDE WALLS")
    dim_v(0, 13, 63, -5.5, "13.00 CLEAR  /  13.30 OUTSIDE REAR WALL")
    dim_v(9.3, 12.8, 777, 4.6, "3.50 WITHDRAWAL")
    dim_h(-2.5, 2.5, 990, 0, "5.00 CLEAR ENTRY")
    dim_h(-1.1, 1.1, 924, .7, "2.20")
    line(px(0), py(.4), px(0), py(1.2), TEAL, 2)
    line(px(0), py(1.2), px(-.13), py(1.0), TEAL, 2)
    line(px(0), py(1.2), px(.13), py(1.0), TEAL, 2)
    text(px(.3), py(.95), "+Y", 11, TEAL)

    x, y = 845, 212
    text(x, y, "ACCESS + CONSTRUCTION", 17, INK, weight="bold")
    y = paragraph(x, y+28, "5.80m clear ceiling. Walls 0.30m thick. S03 design targets; as-built acceptance pending. Floor is flush; no raised platform. Section stays at local Y ≥ 0.")
    y = paragraph(x, y+17, "The 2.20m centre lane is permanent. The east 1.20m strip is equipment reach space, and the rear withdrawal box is a reserved work volume. Neither is a public cart route.")
    y = paragraph(x, y+17, "Reserve terminal and capped mine-water connection support later emergency recovery. No external utility endpoints are installed or invented.")
    text(x, y+30, "P02 REACTOR CONNECTION  /  PROPOSED", 17, INK, weight="bold")
    y = paragraph(x, y+58, "Threshold in reactor: (8.4, −8.4, 0). Rotate local module −135° about Z. Entry endpoints match the 5m P02 southeast portal. Transform remains unapplied.")
    y = paragraph(x, y+16, "Whole-shell plan separation: Control ≥0.899m in Y; east stair ≥7.499m in Y. Shared 0.36m reactor wall seam requires connector coordination. New turbine-room fit remains unverified.")
    # Entry section schematic at same numeric drawing scale.
    ex, fy, s = 905, 957, 36
    text(x, 720, "ENTRY ELEVATION  /  LOOKING INTO +Y", 15, INK, weight="bold")
    rect(ex, fy-5.8*s, 5.6*s, 5.8*s, "#bec9c5", INK, 1.5)
    rect(ex+.3*s, fy-5*s, 5*s, 5*s, "#f5f6f0", INK, 1.5)
    rect(ex+.3*s, fy-5.7*s, 5*s, .7*s, "#6b827d", INK, 1)
    for n in range(1, 5):
        line(ex+.3*s, fy-(5+n*.14)*s, ex+5.3*s, fy-(5+n*.14)*s, GRID, .7)
    text(ex+2.8*s, fy-5.31*s, "FIXED OPEN", 11, "#ffffff", "middle", "bold")
    line(ex, fy, ex+5.6*s, fy, INK, 2)
    text(ex+2.8*s, fy-2.5*s, "5.00 × 5.00 CLEAR", 13, TEAL, "middle", "bold")
    text(ex+2.8*s, fy+24, "FFL 0.000  /  NO FLOOR SWING", 12, INK, "middle")
    line(ex+6*s, fy, ex+6*s, fy-5.8*s, INK, 1)
    text(ex+6.5*s, fy-2.9*s, "5.80 CLEAR HALL", 11, MUTED, "middle", rotate=-90)

    line(58, 1055, 1392, 1055, GRID)
    text(58, 1082, "Source: interface.json  /  original vector geometry  /  dimensions govern  /  plan arithmetic ≠ Blender or runtime validation", 12, MUTED)
    text(1390, 1082, "CP-A02  ·  1 / 1", 12, INK, "end", "bold")
    head = '<svg xmlns="http://www.w3.org/2000/svg" width="1450" height="1130" viewBox="0 0 1450 1130"><title>Cooling plant CP-A02 dimensioned architecture plan</title><desc>Original section-local architectural floorplan, service reserves, machinery and proposed reactor connector. Dimensions in metres. Not runtime validation.</desc><g font-family="Arial, Helvetica, sans-serif">'
    (HERE / "floorplan.svg").write_text(head+"\n".join(SVG)+"</g></svg>\n", encoding="utf-8")


if __name__ == "__main__":
    result = validate()
    draw()
    print(json.dumps({"status": result["status"], "svg": str(HERE / "floorplan.svg"), "checks": result["checks"]}, indent=2))
