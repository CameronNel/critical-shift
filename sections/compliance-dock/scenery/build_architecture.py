"""Reproduce the authored Compliance Dock dimensional contract and A2 SVG sheet.

This produces documentation only. It does not inspect or validate Blender geometry.
Run with Python 3; optional PNG rendering uses resvg_py when available.
"""
from pathlib import Path
import json
import math
from html import escape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REV = "P01"
S = 60  # A2 594 mm / 1782 SVG units: 60 units / metre = 1:50.
OX, OY = 570, 1120
INK = "#263b42"
BLUE = "#1872a1"
PINK = "#a24c6d"
GREEN = "#377b61"
ORANGE = "#b57620"
parts = []


def add(s):
    parts.append(s)


def xy(x, y):
    return OX + S*x, OY-S*y


def text(x, y, value, size=14, fill=INK, anchor="start", weight="400", rotate=None):
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate else ""
    add(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}"{transform}>{escape(str(value))}</text>')


def line(x1, y1, x2, y2, color=INK, width=1.3, dash=None, extra=""):
    dashed = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}"{dashed} {extra}/>')


def worldline(x1, y1, x2, y2, **kwargs):
    line(*xy(x1, y1), *xy(x2, y2), **kwargs)


def rect(x, y, w, h, fill="none", stroke=INK, sw=1.2, extra=""):
    add(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def room(x0, y0, x1, y1, fill, stroke="none", sw=1.2, extra=""):
    x, y = xy(x0, y1)
    rect(x, y, (x1-x0)*S, (y1-y0)*S, fill, stroke, sw, extra)


def label(x, y, lines, size=14, fill=INK):
    px, py = xy(x, y)
    for i, item in enumerate(lines):
        text(px, py+i*(size+5), item, size, fill, "middle", "600" if i == 0 else "400")


def dimx(a, b, y, caption, ref_y=None):
    p, q = xy(a, 0)[0], xy(b, 0)[0]
    line(p, y, q, y, width=.9)
    for u in [p, q]:
        line(u-4, y+4, u+4, y-4, width=1.4)
        if ref_y is not None:
            line(u, ref_y, u, y-6 if y < ref_y else y+6, color="#91a0a0", width=.6)
    tw = max(38, len(caption)*8)
    rect((p+q-tw)/2, y-18, tw, 18, "#fbfaf6", "none")
    text((p+q)/2, y-4, caption, 13, anchor="middle")


def dimy(a, b, x, caption, ref_x=None):
    p, q = xy(0, a)[1], xy(0, b)[1]
    line(x, p, x, q, width=.9)
    for v in [p, q]:
        line(x-4, v+4, x+4, v-4, width=1.4)
        if ref_x is not None:
            line(ref_x, v, x-6 if x < ref_x else x+6, v, color="#91a0a0", width=.6)
    text(x-7, (p+q)/2, caption, 13, anchor="middle", rotate=-90)


def route(points, color, width=2.5, dash="9 5", arrow=True):
    p = " ".join(f'{xy(x,y)[0]:.2f},{xy(x,y)[1]:.2f}' for x,y in points)
    add(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}" stroke-linejoin="round" stroke-linecap="round"'+ (f' marker-end="url(#{color[1:]}-arrow)"' if arrow else "") + '/>')


def marker(x, y, name, color=INK):
    px, py = xy(x,y)
    add(f'<circle cx="{px}" cy="{py}" r="10" fill="#fbfaf6" stroke="{color}" stroke-width="1.5"/>')
    text(px, py+4, name, 11, color, "middle", "700")


def panel(x, y, w, h, number, title):
    rect(x, y, w, h, "#f6f5ef", "#bdc7c4", .8)
    rect(x, y, 35, 30, INK, "none")
    text(x+17.5, y+21, number, 14, "#ffffff", "middle", "700")
    text(x+48, y+21, title, 16, weight="700")


def rows(x, y, lines, size=14, step=22):
    for i, item in enumerate(lines):
        text(x, y+i*step, item, size)


def build_svg():
    add('<?xml version="1.0" encoding="UTF-8"?>')
    add('<svg xmlns="http://www.w3.org/2000/svg" width="594mm" height="420mm" viewBox="0 0 1782 1260" role="img" aria-labelledby="title desc">')
    add('<title id="title">Compliance Dock — dimensioned architectural floorplan, revision P01</title>')
    add('<desc id="desc">A2 sheet at 1 to 50. A 13.6 by 15.8 metre contained dock with a west office and concealed support bay, human and cargo scanners, cart bypass, sealed north access, route allowances, door swings and dimension chains. Authored planning contract; unverified in final geometry and runtime.</desc>')
    add('<defs><pattern id="service-hatch" width="9" height="9" patternUnits="userSpaceOnUse"><path d="M-2,2 L2,-2 M0,9 L9,0 M7,11 L11,7" stroke="#b6c7c8" stroke-width="1"/></pattern>')
    for color in [BLUE, PINK, GREEN, ORANGE, INK]:
        add(f'<marker id="{color[1:]}-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{color}"/></marker>')
    add('</defs><g font-family="Arial, Helvetica, sans-serif">')
    rect(0,0,1782,1260,"#fbfaf6","none")
    text(55,54,"CRITICAL SHIFT",17,weight="700")
    text(55,91,"COMPLIANCE DOCK",32,weight="700")
    text(660,52,"ARCHITECTURE / INTERFACE CONTRACT",15)
    text(660,83,"Contained arrival • controlled inspection • staff support",16)
    text(1730,52,"CD–A01 / P01",19,anchor="end",weight="700")
    text(1730,82,"AUTHORED PLAN • VERIFICATION PENDING",13,ORANGE,"end","700")
    line(55,104,1730,104,width=2)

    # Room surfaces and architectural bounds.
    room(-6.8,0,6.8,15.8,"#e8ece7")
    room(-6.8,0,6.8,3.6,"#edf2ed")
    room(-6.8,3.6,-2.4,9.6,"#e4e8de")
    room(-6.8,9.8,-2.4,15.8,"#d9e0d8")
    room(-2.4,10.2,3.4,15.8,"#edf2ed")
    room(3.4,11,6.8,15.8,"#e1e9e6")
    for y in [3.6,10.2]:
        worldline(-2.3,y,6.8,y,color="#a9b5b0",width=.9,dash="10 4 2 4")
    # Reserved service strip is east of conveyor. All 0.90 m remains free.
    room(5.9,5.3,6.8,10.0,"url(#service-hatch)","#879b9a",.8)
    # Cart swept corridor: 1.35 m planning allowance, with 1.50 m-radius end turns.
    add('<g id="movement-envelopes">')
    room(1.275,3.2,2.625,12.2,"#c7dfea","none",extra='opacity="0.65"')
    for cx,cy in [(1.0,2.0),(1.25,12.1)]:
        px,py=xy(cx,cy)
        add(f'<circle cx="{px}" cy="{py}" r="90" fill="none" stroke="{BLUE}" stroke-dasharray="3 6" stroke-width="1.1"/>')
    # Nominal cart, body and opposing personnel allowances (not physical props).
    room(1.575,8.1,2.325,10.2,"#eef7fc",BLUE,1.5,extra='stroke-dasharray="6 3"')
    for xx in [1.56,2.34]:
        for yy in [8.35,9.95]:
            room(xx-.035,yy-.14,xx+.035,yy+.14,BLUE,"none")
    room(1.6,10.65,2.3,12.45,"#f8f0e1",ORANGE,1.5,extra='rx="18" stroke-dasharray="6 3"')
    px,py=xy(1.95,12.17)
    add(f'<circle cx="{px}" cy="{py}" r="11" fill="none" stroke="{ORANGE}"/>')
    add('</g>')
    # External wall thickness projects out from clear interior bounds.
    room(-7.08,-.28,-6.8,16.08,INK)
    room(6.8,-.28,7.08,16.08,INK)
    room(-6.8,-.28,-1.2,0,INK)
    room(1.2,-.28,6.8,0,INK)
    room(-6.8,15.8,-2.3,16.08,INK)
    room(2.3,15.8,6.8,16.08,INK)
    # Pocket/sliding leaves: dashed operating threshold, leaves stowed outside opening.
    for y,hw in [(0,1.2),(15.8,2.3)]:
        worldline(-hw,y,hw,y,color=INK,width=2,dash="9 4")
        worldline(-hw-.7,y-.12,-hw-.08,y-.12,width=4)
        worldline(hw+.08,y-.12,hw+.7,y-.12,width=4)
    # Office partitions use the nominal room zoning datums as centrelines.
    for yy in [3.6,9.6]:
        room(-6.8,yy-.08,-5.925,yy+.08,INK)
        room(-4.875,yy-.08,-2.32,yy+.08,INK)
    # Transaction hatch is a sill-level front-wall opening, not a walkable cut.
    worldline(-4.35,3.6,-2.67,3.6,color="#85a9aa",width=4)
    # Office east solid ends and observation glazing to y8.90.
    room(-2.48,3.6,-2.32,4.0,INK)
    room(-2.48,8.9,-2.32,9.6,INK)
    for xx in [-2.43,-2.37]:
        worldline(xx,4.0,xx,8.9,color="#498c98",width=2)
    # Door hinges on west jamb: inward office swing, front +Y, rear -Y.
    for yy,sgn in [(3.6,1),(9.6,-1)]:
        hx,hy=xy(-5.925,yy)
        ex,ey=xy(-4.875,yy)
        ox,oy=xy(-5.925,yy+sgn*1.05)
        worldline(-5.925,yy,-5.925,yy+sgn*1.05,width=2,dash="4 3" if sgn==1 else None)
        if sgn==1:
            worldline(-5.925,yy,-4.875,yy,width=2.2)
        sweep=0 if sgn==1 else 1
        add(f'<path d="M{ex},{ey} A63,63 0 0,{sweep} {ox},{oy}" fill="none" stroke="#7a8988" stroke-width="1.1"/>')
    # North opening around an opaque screen: no external portal.
    room(-2.48,9.8,-2.32,14.25,INK)
    worldline(-2.4,14.25,-2.4,15.8,color="#b8c0ba",width=1,dash="4 4")
    # Office working furniture lies east of the straight staff lane.
    room(-4.25,5.8,-2.75,7.8,"#c4ccbf",INK)
    room(-4.35,3.25,-2.67,3.95,"#c4ccbf",INK)
    label(-3.5,7.0,["LOGS /", "CHECK-IN"],12)
    label(-3.51,4.42,["CHECK-IN HATCH", "+1.04"],11)
    label(-5.4,3.27,["D1 LOCKED"],10)
    # Scanner human portal footprint, outer 1.70, clear 1.20.
    for a,b in [(-.85,-.6),(.6,.85)]:
        room(a,6.55,b,7.45,"#b6c6c7",INK,1.7)
    worldline(-.6,7,.6,7,color=PINK,width=1.7,dash="3 3")
    # Cart gate carries no swing into route. Side pocket is in the separator.
    worldline(1.05,7,2.85,7,color=INK,width=2,dash="7 4")
    room(2.86,6.75,3.36,7.25,"#a8bbb8",INK,1)
    # Conveyor scanner: belt and hood retain distinct silhouettes on plan.
    room(3.4,5.3,5.9,10,"#c0cbcb",INK,1.8)
    room(3.65,5.3,5.65,10,"#8c9f9d",INK,1)
    for yy in [5.5,5.75,6,6.25,9.0,9.25,9.5,9.75]:
        worldline(3.65,yy,5.65,yy,color="#d5dfda",width=1.6)
    room(3.4,6.7,5.9,8.7,"#a5b6b8",INK,2)
    label(4.65,7.8,["CARGO", "INSPECTION", "belt +0.80"],14)
    # Support bay props and their candidate hiding capacities.
    room(-6.4,12.0,-5.3,14.5,"#aebbab",INK,1.2,extra='rx="8"')
    label(-5.85,13.6,["TARP", "TROLLEY", "H1"],12)
    room(-6.45,14.8,-4.7,15.55,"#b9c5b7",INK)
    label(-5.575,15.23,["EVIDENCE / H2"],11)
    # East nook wall gear and a bounded hand-cart berth.
    room(6.05,12.0,6.7,14.2,"#b4c5c3",INK)
    room(4.0,14.65,5.9,15.55,"#b4c5c3",INK)
    label(5.0,15.15,["WALL UTILITIES"],11)
    room(4.05,11.65,4.8,13.75,"#c4d1ca",INK,1,extra='stroke-dasharray="4 3"')
    label(4.43,12.9,["HAND", "CART"],11)
    # Dashed route centre lines.
    route([(0,15.0),(0,10.5),(0,7),(0,1.2),(0,-.65)],PINK)
    route([(0,15.25),(1.25,13.45),(1.95,12.2),(1.95,3.2),(1,2),(0,1),(0,-.7)],BLUE)
    route([(-4.65,1.85),(-5.4,2.7),(-5.4,10.65),(-4.2,11.8),(-3.5,14.05),(-3.5,15.025),(-1.7,15.025)],GREEN)
    # Inspection sightline rays through the office glass; not visibility results.
    add('<g id="sightline-intent">')
    for end in [(0,7),(1.95,7),(0,12.8)]:
        route([(-3.05,5.3),end],ORANGE,1.2,"2 6",False)
    marker(-3.05,5.3,"E",ORANGE)
    add('</g>')
    # Runtime interest markers keyed to documentation.
    for x,y,name in [(0,14,"A"),(-3.51,2.6,"B"),(0,8.3,"C"),(4.65,10.55,"D"),(-3.55,13.5,"F")]:
        marker(x,y,name)
    # Room labels placed away from route intersections.
    label(-4.55,3.0,["01  RELEASE APRON", "clear ceiling 3.40"],14)
    label(-4.63,8.8,["02  STAFF OFFICE", "4.40 × 6.00 datums", "clear ceiling 3.05"],13)
    label(-4.48,11.45,["05  SUPPORT BAY", "concealment / staff shortcut"],13)
    label(-.3,9.75,["03  CONTROLLED CHECK", "clear ceiling 4.40"],13)
    label(.1,13.5,["04  ARRIVAL DOCK"],14)
    label(4.8,11.35,["06  EQUIPMENT NOOK"],12)
    label(0,6.17,["HUMAN SCAN", "1.20 clear"],12)
    label(1.95,5.28,["CART BYPASS", "1.80 clear"],12,BLUE)
    text(*xy(6.38,7.66),"0.90 SERVICE",11,INK,"middle",rotate=-90)
    label(3.06,9.5,["0.75 × 2.10", "cart allowance"],11,BLUE)
    label(3.03,12.4,["0.70 × 1.80", "body allowance"],11,ORANGE)
    label(1.65,1.1,["R1.50", "turn allowance"],11,BLUE)
    # Local axes and true dimension chains.
    marker(0,0,"0")
    route([(0,0),(.95,0)],INK,1.6,"1 0")
    route([(0,0),(0,.95)],INK,1.6,"1 0")
    text(*xy(.99,-.06),"+X",12)
    text(*xy(-.13,1.10),"+Y / IN",12,anchor="end")
    dimx(-6.8,6.8,122,"13.60 clear between perimeter faces",172)
    for a,b,cap in [(-6.8,-2.4,"4.40"),(-2.4,3.4,"5.80"),(3.4,6.8,"3.40")]:
        dimx(a,b,151,cap,172)
    dimy(0,15.8,79,"15.80 clear between perimeter faces",162)
    for a,b,cap in [(0,3.6,"3.60"),(3.6,9.6,"6.00"),(9.6,15.8,"6.20")]:
        dimy(a,b,120,cap,162)
    for a,b,cap in [(0,3.6,"3.60 apron"),(3.6,10.2,"6.60 check zone"),(10.2,15.8,"5.60 dock apron")]:
        dimy(a,b,1021,cap,978)
    dimx(-1.2,1.2,1156,"P1 / 2.40 × 2.60 clear",1120)
    # North access callout and north arrow.
    text(570,207,"P2  SEALED EXTERNAL ACCESS",13,anchor="middle",weight="700")
    text(570,228,"4.60 × 3.50 clear / sliding leaves",12,anchor="middle")
    line(1070,259,1070,178,width=2,extra=f'marker-end="url(#{INK[1:]}-arrow)"')
    text(1070,159,"N*",19,anchor="middle",weight="700")
    text(1070,280,"LOCAL",10,anchor="middle")
    text(1070,295,"+Y",11,anchor="middle")
    text(162,1182,"PLAN / 1:50 @ A2    ALL DIMENSIONS IN METRES    Z=0 FINISHED FLOOR",13,weight="700")
    # Reference elevation, supplementary schedule and interpretation legend.
    panel(1110,124,620,302,"02","CLEAR HEIGHTS / DIAGRAMMATIC ELEVATION")
    fx,fy,es=1145,366,42
    line(fx,fy,1695,fy,width=2)
    line(fx,fy-4.4*es,1695,fy-4.4*es,color="#99aaa6",width=1,dash="8 5")
    text(1685,fy-4.4*es-7,"MAIN +4.40",12,anchor="end")
    # Three doorway/equipment comparison silhouettes.
    for x,w,h,name in [(1170,1.2,2.25,"HUMAN SCAN"),(1300,2.4,2.6,"FACILITY P1"),(1465,4.6,3.5,"SEALED P2")]:
        rect(x,fy-h*es,w*es,h*es,"#e0e9e7",INK,1.8)
        text(x+w*es/2,fy+19,name,11,anchor="middle",weight="700")
        text(x+w*es/2,fy-h*es-8,f"{h:.2f}",12,anchor="middle")
    text(1130,412,"Office ceiling +3.05 • front apron +3.40 • cargo top +2.10",13)
    panel(1110,441,620,279,"03","OPENINGS / ROUTE RESERVATIONS")
    rows(1130,494,[
        "P1   (0, 0, 0)               2.40 W × 2.60 H  / sliding",
        "P2   (0, 15.80, 0)       4.60 W × 3.50 H  / sealed slide",
        "D1   (−5.40, 3.60)      1.05 W × 2.20 H  / locked shut",
        "D2   (−5.40, 9.60)      1.05 W × 2.20 H  / open alternative",
        "G1   (1.95, 7.00)        1.80 W clear  / retracting side gate",
        "R1   Person inspection    1.20 minimum at scanner",
        "R2   Cart/body bypass    1.35 swept allowance; gate 1.80",
        "R3   Staff shortcut         requires D1 unlock + doors open",
        "H1   Tarp trolley              1 body capacity, candidate",
        "H2   Evidence cabinet     0 bodies / 6 small-item slots"
    ],14,21)
    panel(1110,735,620,277,"04","READ THIS WITH ARCHITECTURE.MD")
    rows(1130,788,[
        "01  Perimeter 0.28 thick, outward from clear inside face.",
        "02  Office / screen 0.16 thick, centred on named datums.",
        "      Office net clear ≈ 4.32 × 5.84 before fixtures.",
        "03  East glass +1.05…+2.50; front hatch counter +1.04.",
        "04  North screen return leaves 1.55 nominal access.",
        "05  Thresholds flush; overhead/door collision still pending.",
        "06  Medical 2.20 × 2.50 interface needs connector transition.",
        "      Adjacency has no agreed world transform or new cut.",
        "07  Circles / dashed bodies are planning allowances only.",
        "      No physics, travel-time or visibility test is claimed."
    ],14,21)
    panel(1110,1027,620,155,"05","LEGEND / GAMEPLAY INTENT")
    for y,col,cap,dash in [(1079,PINK,"R1 personnel / inspection centreline","9 5"),(1107,BLUE,"R2 cart / body centreline + swept allowance","9 5"),(1135,GREEN,"R3 staff shortcut; locked-door runtime hook","9 5"),(1163,ORANGE,"E sightline intent / body footprint; unverified","2 6")]:
        line(1130,y-4,1180,y-4,color=col,width=2,dash=dash)
        text(1195,y,cap,13)
    line(55,1204,1730,1204,width=1.7)
    text(55,1230,"CD–A01",17,weight="700")
    text(210,1230,"P01 · 08 SEP 2026 · AUTHORED DIMENSIONS · NOT ACCEPTANCE EVIDENCE",12)
    text(1110,1230,"* North denotes local +Y; geographic bearing unresolved.",11)
    # 0–5 m scale bar, 1 m alternating subdivisions.
    for i in range(5):
        rect(660+i*60,1160,60,10,INK if i%2==0 else "#fbfaf6",INK,.8)
        text(660+i*60,1186,str(i),11,anchor="middle")
    text(960,1186,"5 m",11,anchor="middle")
    add('</g></svg>')
    (HERE/"floorplan.svg").write_text("\n".join(parts),encoding="utf-8")


def build_interface():
    data = {
      "schema_version": 1,
      "section": "compliance-dock",
      "revision": REV,
      "status": "authored dimensional contract; final-geometry and runtime verification pending",
      "units": "metres",
      "coordinate_system": {"origin":[0,0,0],"origin_description":"centre of clear facility entry threshold at finished floor","right":"+X","inward":"+Y","up":"+Z","north_note":"drawing north means local +Y, not geographic bearing","global_transform":None},
      "source_authority": {
        "game_spec":"C:/Users/Camer/Games/critical-shift/worktrees/reactor-valorant/design/GAME_SPEC.md",
        "build_brief":"C:/Users/Camer/Games/critical-shift/ops/facility-run/BUILD_BRIEF.md",
        "section_brief":"C:/Users/Camer/Games/critical-shift/ops/facility-run/briefs/compliance-dock.md",
        "dimension_basis":"builder-authored section layout; dimensions are implementation decisions rather than canonical measurements",
        "traceability":["GAME_SPEC §14.1–14.6", "GAME_SPEC §16.1–16.5", "GAME_SPEC §23.1–23.4", "GAME_SPEC §30.5", "GAME_SPEC §31.2"]
      },
      "interior": {
        "bounds_xy":[-6.8,0,6.8,15.8],"floor_z":0,"gross_interior_area_m2":214.88,
        "area_note":"perimeter clear-face rectangle before internal partitions, equipment and route deductions",
        "perimeter_wall_thickness_m":0.28,"perimeter_wall_convention":"outside stated interior bounds",
        "office_partition_thickness_m":0.16,"internal_wall_convention":"centred on the named office and screen datums",
        "maximum_exterior_bounds_xy":[-7.08,-0.28,7.08,16.08],
        "ceiling_zones":[{"id":"release_apron","bounds_xy":[-6.8,0,6.8,3.6],"clear_height_m":3.4,"note":"front office partition projects 0.08 m into this zoning rectangle"},{"id":"office","bounds_xy":[-6.8,3.6,-2.4,9.6],"clear_height_m":3.05},{"id":"main_dock_and_support","bounds_xy":[-6.8,3.6,6.8,15.8],"clear_height_m":4.4,"exclude_zones":["office"]}]
      },
      "portals":[
        {"id":"facility_entry","label":"P1","type":"facility_connector","threshold":[0,0,0],"width_axis":"+X","inward_normal":[0,1,0],"clear_width_m":2.4,"clear_height_m":2.6,"clear_bounds":{"min":[-1.2,0,0],"max":[1.2,0,2.6]},"mechanism":"sliding along X in perimeter wall; no swinging leaf","threshold_step_m":0,"connected_section":None,"connection_status":"connector network target pending; medical adjacency only"},
        {"id":"sealed_external_access","label":"P2","type":"sealed_external_arrival","threshold":[0,15.8,0],"width_axis":"+X","inward_normal":[0,-1,0],"clear_width_m":4.6,"clear_height_m":3.5,"clear_bounds":{"min":[-2.3,15.8,0],"max":[2.3,15.8,3.5]},"mechanism":"opposed sliding leaves along X","threshold_step_m":0,"connected_section":None,"default_state":"sealed","connection_status":"exterior presentation/arrival boundary; exterior scene and transport unassigned"},
        {"id":"staff_front","label":"D1","type":"internal_staff_door","threshold":[-5.4,3.6,0],"clear_width_m":1.05,"clear_height_m":2.2,"hinge_xy":[-5.925,3.6],"swing_into":"office +Y","swing_radius_m":1.05,"threshold_step_m":0,"connects_local_spaces":["release_apron","office"]},
        {"id":"staff_rear","label":"D2","type":"internal_staff_door","threshold":[-5.4,9.6,0],"clear_width_m":1.05,"clear_height_m":2.2,"hinge_xy":[-5.925,9.6],"swing_into":"office -Y","swing_radius_m":1.05,"threshold_step_m":0,"connects_local_spaces":["office","concealed_support_bay"]},
        {"id":"cart_gate","label":"G1","type":"internal_control_gate","threshold":[1.95,7,0],"clear_width_m":1.8,"clear_height_m":4.4,"clear_x_range":[1.05,2.85],"mechanism":"telescoping side-pocket leaf retracts east; no swing","storage_pocket_bounds_xy":[2.86,6.75,3.08,7.25],"threshold_step_m":0,"connects_local_spaces":["release_apron","arrival_dock"],"mechanical_design_status":"compact telescoping/retracting mechanism allowance; detailed constructability pending"},
        {"id":"support_screen_north_return","type":"internal_opening","threshold":[-2.4,15.025,0],"width_axis":"+Y","clear_width_m":1.55,"clear_height_m":4.4,"clear_y_range":[14.25,15.8],"mechanism":"no leaf","connects_local_spaces":["concealed_support_bay","arrival_dock"]}
      ],
      "external_boundary_cut_count":2,
      "adjacency": {
        "canonical_sequence":"Reanimation and Medical → Compliance Dock (GAME_SPEC §23.1)",
        "route_via":"facility connector network; no direct medical-to-dock wall cut authored",
        "adjacent_section":"medical-reanimation",
        "read_only_source":"C:/Users/Camer/.codex/worktrees/1edf/critical-shift/sections/medical-reanimation/scenery/interface.json",
        "source_revision":"P01",
        "medical_entry":{"threshold_local":[0,0,0],"width_m":2.2,"height_m":2.5},
        "dock_entry":{"threshold_local":[0,0,0],"width_m":2.4,"height_m":2.6},
        "transition_required":"connector transitions to the smaller medical aperture; do not move either existing module",
        "relative_transform":None,"connector_id":None,"connector_length_m":None,
        "geometry_confirmed":False,"travel_time_confirmed":False,
        "travel_target_seconds":[10,20]
      },
      "zones":[
        {"id":"release_apron","bounds_xy":[-6.8,0,6.8,3.6],"purpose":"facility release, check-in queue and lower cart turn"},
        {"id":"office","datum_bounds_xy":[-6.8,3.6,-2.4,9.6],"net_clear_bounds_xy":[-6.8,3.68,-2.48,9.52],"net_clear_area_before_fixtures_m2":25.2288,"purpose":"staff check-in, log review and controlled shortcut"},
        {"id":"controlled_check","bounds_xy":[-2.32,3.6,6.8,10.2]},
        {"id":"arrival_dock","bounds_xy":[-2.32,10.2,3.4,15.8],"purpose":"officer arrival, cargo receipt and clear central approach"},
        {"id":"concealed_support_bay","datum_bounds_xy":[-6.8,9.8,-2.4,15.8],"screen_bounds":{"min":[-2.48,9.8,0],"max":[-2.32,14.25,2.7]},"purpose":"tarp trolley and evidence storage behind opaque screen; search remains possible"},
        {"id":"equipment_nook","bounds_xy":[3.4,11,6.8,15.8],"purpose":"wall utilities and parked hand cart"}
      ],
      "equipment": {
        "human_scanner":{"centre":[0,7,0],"outer_bounds_xy":[-0.85,6.55,0.85,7.45],"clear_width_m":1.2,"clear_height_m":2.25,"clear_x_range":[-0.6,0.6],"outer_width_m":1.7,"overall_top_z_allowance":2.55},
        "cargo_scanner":{"centre":[4.65,7.7,0],"bounds":{"min":[3.4,5.3,0],"max":[5.9,10,2.1]},"belt_top_z":0.8,"maintenance_side":"east","maintenance_clearance_m":0.9,"maintenance_bounds_xy":[5.9,5.3,6.8,10],"standing_load_positions":[[4.65,4.5,0],[4.65,10.55,0]]},
        "check_in_hatch":{"centre_on_glass":[-2.4,5,1.05],"counter_bounds_xy":[-3.05,4.5,-2.4,5.5],"counter_top_z":1.05,"public_use_position":[-1.1,5,0]},
        "observation_glass":{"plane_x":-2.4,"y_range":[4,8.9],"bottom_z":1.05,"top_z":2.5,"normal":[1,0,0]},
        "staff_workbench":{"bounds_xy":[-4.25,5.8,-2.75,7.8],"operator_clearance_side":"west; preserve staff lane at x−5.4"},
        "tarp_trolley":{"bounds_xy":[-6.4,12,-5.3,14.5],"maximum_top_z":1.3},
        "evidence_storage":{"bounds_xy":[-4.6,14.8,-2.8,15.55],"maximum_top_z":1.6,"front_access":"south"},
        "parked_hand_cart":{"bounds_xy":[4.05,11.65,4.8,13.75]},
        "wall_utilities":{"bounds_xy":[6.05,12,6.7,14.2]},
        "rear_utility_console":{"bounds_xy":[4,14.65,5.9,15.55]}
      },
      "reserved_routes":[
        {"id":"R1","purpose":"routine officer/person inspection then facility release","centreline_xy":[[0,15],[0,10.5],[0,7],[0,1.2],[0,0]],"nominal_clear_width_m":1.2,"limiting_element":"human_scanner","traversal_direction":"bidirectional; arrival proceeds -Y","headroom_min_m":2.25},
        {"id":"R2","purpose":"loaded cart and body transport bypasses human scanner","centreline_xy":[[0,15.25],[1.25,13.45],[1.95,12.2],[1.95,3.2],[1,2],[0,1],[0,0]],"swept_width_allowance_m":1.35,"straight_swept_bounds_xy":[1.275,3.2,2.625,12.2],"limiting_gate_clear_width_m":1.8,"portal_clear_width_m":2.4,"headroom_min_m":2.6,"turn_allowances":[{"centre_xy":[1,2],"radius_m":1.5},{"centre_xy":[1.25,12.1],"radius_m":1.5}],"turn_note":"circles are local manoeuvre reservations, not the Minkowski sweep of this schematic centreline; actual curved turning path requires runtime verification"},
        {"id":"R3","purpose":"staff shortcut from apron through office to concealed support bay and around screen north end","centreline_xy":[[-4.65,1.85],[-5.4,2.7],[-5.4,10.65],[-4.2,11.8],[-3.5,14.7],[-1.7,14.7]],"limiting_door_clear_width_m":1.05,"headroom_min_m":2.2,"access_hook":"staff-authorised lock; officer can open selected access points","cart_note":"0.75 m cart nominally fits straight through, leaving 0.15 m each side; turning, door operation and body dragging are unverified"}
      ],
      "swept_objects": {
        "cart":{"nominal_footprint_m":[0.75,2.1],"straight_swept_allowance_width_m":1.35,"depicted_bounds_xy":[1.575,8.1,2.325,10.2]},
        "body":{"nominal_footprint_m":[0.7,1.8],"depicted_bounds_xy":[1.6,10.65,2.3,12.45],"note":"offline/unconscious body transport; limb/ragdoll extents and handler space not resolved"},
        "obstruction_cases":[{"id":"transverse_cart_at_P1","nominal_footprint_m":[2.1,0.75],"expected_issue":"cart can obstruct the 2.4 m entry despite nominal side gaps; manual clearing/drag needed"},{"id":"body_at_human_scanner","nominal_footprint_m":[1.8,0.7],"expected_issue":"human lane can be blocked; authorised cart bypass is alternate local path"}],
        "physics_verified":False
      },
      "sightlines": {
        "status":"authored inspection intent, not raycast results",
        "office_eye":{"label":"E","position":[-3.05,5.3,1.6]},
        "targets":[{"position":[0,7,1.1],"purpose":"worker scan"},{"position":[1.95,7,1.1],"purpose":"cart-gate approach"},{"position":[0,12.8,1.4],"purpose":"north arrival approach"}],
        "occlusion_intent":"2.7 m opaque support screen blocks routine central-eye view of low trolley; visibility from north return or opened tarp remains possible",
        "required_checks":["glass actually transmits intended eye rays","screen and equipment occlusion","standing and crouched player views","officer search from north return"]
      },
      "hiding_spaces":[
        {"id":"H1_tarp_trolley","type":"tarp/cart","bounds_xy":[-6.4,12,-5.3,14.5],"capacity":{"bodies":1,"small_items":2},"visibility":{"closed_cover":"low from central route; concealment is conditional","open_cover":"high at close range","candidate_normalized_closed":0.2},"sound_transmission":{"candidate_factor":0.7,"note":"fabric attenuates lightly; waking occupant can be heard"},"search_probability":{"routine_candidate":0.15,"formal_audit_candidate":0.65,"active_search_candidate":0.9,"status":"tuning placeholders, not canonical or implemented"},"escape_possibility":"unrestrained occupant lifts tarp and exits east into support aisle; staff doors and north return provide onward routes","environmental_risk":"trolley movement transports occupant; wake-up sound, discovery and obstruction possible; no lethal machinery in hiding berth","interaction_hooks":["cover_open","cover_close","stow","retrieve","wake_noise","escape","inspect"],"implemented":False},
        {"id":"H2_evidence_cabinet","type":"staff evidence storage","bounds_xy":[-4.6,14.8,-2.8,15.55],"capacity":{"bodies":0,"small_items":6},"visibility":{"closed":"opaque cabinet; registration/log record may remain discoverable","open":"contents visible","candidate_normalized_closed":0.05},"sound_transmission":{"candidate_factor":0.25,"note":"closed metal cabinet, rattling possible"},"search_probability":{"routine_candidate":0.25,"formal_audit_candidate":0.85,"active_search_candidate":1.0,"status":"tuning placeholders, not canonical or implemented"},"escape_possibility":"not applicable to zero-body container; retrieval from south face","environmental_risk":"evidence logged, confiscated or linked to owner; cabinet is not radiation shielding","interaction_hooks":["unlock","open","register_evidence","stow","retrieve","inspect","confiscate"],"implemented":False}
      ],
      "runtime_markers":[
        {"id":"officer_arrival","label":"A","type":"spawn","position":[0,14,0],"facing":[0,-1,0],"enabled_when":"external access arrival event","requires_nav_and_collision_validation":True},
        {"id":"check_in","label":"B","type":"interest_target","position":[-1.1,5,0],"facing":[-1,0,0],"hooks":["headcount","read_logs","guided_tour","distraction"]},
        {"id":"worker_inspection","label":"C","type":"interest_target","position":[0,8.3,0],"facing":[0,-1,0],"hooks":["scan_worker","inspect_injury","missing_registration"]},
        {"id":"cargo_inspection","label":"D","type":"interest_target","position":[4.65,10.55,0],"facing":[0,-1,0],"hooks":["scan_waste","collect_evidence","cargo_confiscation"]},
        {"id":"support_search","label":"F","type":"interest_target","position":[-3.55,13.5,0],"facing":[-1,0,0],"hooks":["search_cover","search_cabinet","body_discovery"]},
        {"id":"officer_departure","type":"route_target","position":[0,14.8,0],"facing":[0,1,0]},
        {"id":"facility_handoff","type":"connector_navigation_boundary","position":[0,0,0],"neighbour_transform":None}
      ],
      "service_interfaces":[
        {"id":"power","wall":"east","anchor":[6.8,13.6,1.15],"outward_normal":[1,0,0],"connected_section":None,"capacity":None},
        {"id":"data","wall":"east","anchor":[6.8,13.2,2.6],"outward_normal":[1,0,0],"connected_section":None,"protocol":None}
      ],
      "runtime_handoff": {
        "implemented_or_verified":False,
        "incident_hooks":["audit_arrival","scanner_fault","destroyed_sensor","restricted_door","body_discovery","cargo_contraband","falsified_log","evidence_collected","officer_disabled","lockdown_override"],
        "audio_zones":[{"id":"dock","bounds_xy":[-2.32,0,6.8,15.8],"intent":"contained bay with practical machinery and scanner chirps"},{"id":"office","bounds_xy":[-6.8,3.6,-2.4,9.6],"intent":"partly isolated staff speech and console cues"},{"id":"support","bounds_xy":[-6.8,9.8,-2.4,15.8],"intent":"tarp and occupant noise audible around screen; tune occlusion"}],
        "network_relevance_boundary":{"bounds_xy":[-7.08,-0.28,7.08,16.08],"z_range":[0,4.4],"handoff_at":["facility_entry","sealed_external_access"],"status":"authored allowance; engine implementation pending"},
        "evidence_state_fields":["evidence_id","type","location","visibility","owner","related_event","compliance_value","resistance_value","hidden","discovered"],
        "required_validation":["final geometry against dimensional contract","door leaf, frame and lock collision","scanner clear opening and overhead services","cart trajectory and swept volume","body dragging and ragdoll limb extent","occupied shortcut and open-door blocking","north screen-return manoeuvre","tarp retrieval and occupant escape","officer interest-target reachability","sensor rays through observation glass","inspection and escalation event hooks","navigation recovery under obstruction","network ownership and relevance handoff","audio propagation","medical connector width/height transition","adjacent travel time 10–20 seconds"],
        "validation_or_acceptance_claimed":False
      }
    }
    # Final author decisions from the section builder: front transaction hatch,
    # observation-only east glass, locked D1 and alternate open-state D2.
    data["design_decisions"] = [
        "Section builder confirmed support screen x−2.4, y9.8…14.25, h2.7 and 1.55 m north return.",
        "Section builder moved primary transaction hatch to front office wall y3.6, centre x−3.51, counter z1.04; east glass is observation only.",
        "D1 is authored locked shut. D2 is an alternate open-state route; R3 is a conditional shortcut, not default traversability.",
        "Candidate evidence cabinet moved to west end of rear wall so the schematic north-return approach has space; alignment to final geometry pending."
    ]
    hatch = data["equipment"]["check_in_hatch"]
    hatch.pop("centre_on_glass")
    hatch.update({"centre_on_front_wall":[-3.51,3.6,1.04],"opening_x_range":[-4.35,-2.67],"counter_bounds_xy":[-4.35,3.25,-2.67,3.95],"counter_top_z":1.04,"public_use_position":[-3.51,2.6,0],"upper_opening_z":None,"note":"front-wall sill-level transaction opening; no walkable portal, upper frame height to follow final geometry"})
    data["equipment"]["evidence_storage"]["bounds_xy"] = [-6.45,14.8,-4.7,15.55]
    data["hiding_spaces"][1]["bounds_xy"] = [-6.45,14.8,-4.7,15.55]
    data["reserved_routes"][2]["centreline_xy"] = [[-4.65,1.85],[-5.4,2.7],[-5.4,10.65],[-4.2,11.8],[-3.5,14.05],[-3.5,15.025],[-1.7,15.025]]
    data["reserved_routes"][2]["default_traversable"] = False
    data["reserved_routes"][2]["default_obstruction"] = "staff_front D1 locked shut"
    data["runtime_markers"][1]["position"] = [-3.51,2.6,0]
    data["runtime_markers"][1]["facing"] = [0,1,0]
    data["portals"][2]["default_state"] = "locked_closed"
    data["portals"][3]["default_state"] = "alternate_open_state_shown; authored final-state check pending"
    data["portals"][4]["storage_pocket_bounds_xy"] = [2.86,6.75,3.36,7.25]
    data["portals"][4]["mechanism"] = "four-panel telescoping side-pocket leaf retracts east; no swing"
    for portal in data["portals"]:
        portal.setdefault("width_axis", "+X")
        portal["aperture_wall_axis"] = "Y" if portal["width_axis"] == "+X" else "X"
        portal["aperture_depth_m"] = 0.28 if portal["id"] in ["facility_entry", "sealed_external_access"] else (0.16 if portal["id"] != "cart_gate" else 0.5)
    for route in data["reserved_routes"]:
        route["route_state_for_clearance_check"] = {"R1":"facility_entry and sealed_external_access open; scanner operational", "R2":"facility_entry and sealed_external_access open; cart_gate fully retracted", "R3":"staff_front unlocked and staff_front/staff_rear held at 90 degrees open into office; differs from authored front locked state"}[route["id"]]
    (ROOT/"interface.json").write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")


if __name__ == "__main__":
    HERE.mkdir(parents=True,exist_ok=True)
    build_svg()
    build_interface()
    try:
        import resvg_py
        png = resvg_py.svg_to_bytes(svg_string=(HERE/"floorplan.svg").read_text(encoding="utf-8"), width=2376, dpi=96)
        (HERE/"floorplan.png").write_bytes(png)
        print("Authored SVG, PNG and interface.json. No model/runtime verification performed.")
    except ImportError:
        print("Authored SVG and interface.json; optional resvg_py unavailable for PNG.")
