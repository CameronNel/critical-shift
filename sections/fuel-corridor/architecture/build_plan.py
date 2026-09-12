"""Generate the editable P07 plan from interface.json using only Python stdlib.

No Blender or adjacent geometry is opened. SVG text and vector geometry remain
editable. The drawing's dimensions are metres; the displayed scale bar governs.
"""
from __future__ import annotations

import html
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE.parent / "interface.json").read_text(encoding="utf-8"))
OUT = HERE / "A101-plan.svg"
W, H = 1800, 1440
S = 36.0
OX, OY = 345.0, 1090.0
C = {"ink": "#20343b", "muted": "#60757b", "line": "#96aaaf", "paper": "#f5f7f5",
     "freight": "#167d89", "bypass": "#a36d22", "red": "#a54338", "light": "#e6efec"}
parts: list[str] = []


def attrs(**kw):
    return " ".join(f'{k.replace("_", "-")}="{html.escape(str(v), quote=True)}"' for k, v in kw.items() if v is not None)


def add(tag, body=None, **kw):
    parts.append(f"<{tag} {attrs(**kw)}/>" if body is None else f"<{tag} {attrs(**kw)}>{body}</{tag}>")


def text(x, y, value, size=18, color=None, weight=400, anchor="start", **kw):
    add("text", html.escape(str(value)), x=x, y=y, font_size=size, fill=color or C["ink"], font_weight=weight,
        text_anchor=anchor, **kw)


def lines(x, y, values, size=17, leading=25, color=None, weight=400):
    for i, value in enumerate(values):
        text(x, y+i*leading, value, size, color, weight)


def line(x1, y1, x2, y2, color=None, width=1.4, **kw):
    add("line", x1=x1, y1=y1, x2=x2, y2=y2, stroke=color or C["line"], stroke_width=width, **kw)


def rect(x, y, w, h, fill="none", stroke=None, width=1, **kw):
    add("rect", x=x, y=y, width=w, height=h, fill=fill, stroke=stroke, stroke_width=width, **kw)


def xy(x, y):
    return OX+x*S, OY-y*S


def point_line(points, color, width, dash=None):
    add("polyline", points=" ".join(f"{xy(*p)[0]:.2f},{xy(*p)[1]:.2f}" for p in points),
        fill="none", stroke=color, stroke_width=width, stroke_linejoin="round", stroke_linecap="round",
        stroke_dasharray=dash)


def dimension(x1, y1, x2, y2, label, horizontal=True, color=None):
    color = color or C["muted"]
    line(x1,y1,x2,y2,color,1)
    if horizontal:
        for x in (x1,x2): line(x-4,y1+5,x+4,y1-5,color,1.5)
        text((x1+x2)/2,y1-10,label,16,color,500,"middle")
    else:
        for y in (y1,y2): line(x1-5,y-4,x1+5,y+4,color,1.5)
        x,y=x1-12,(y1+y2)/2
        text(x,y,label,16,color,500,"middle",transform=f"rotate(-90 {x} {y})")


def world_dim_x(x0,x1,y,label):
    a=xy(x0,y); b=xy(x1,y); dimension(*a,*b,label)


def world_dim_y(x,y0,y1,label):
    a=xy(x,y0); b=xy(x,y1); dimension(*a,*b,label,False)


def section_title(y,n,title):
    text(1120,y,n,17,C["freight"],700)
    text(1170,y,title,21,C["ink"],700)
    line(1120,y+15,1740,y+15,C["line"],1)


parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
parts.append('<title>Fuel Corridor P07 — dimensioned architectural plan</title>')
parts.append('<desc>Editable plan from interface.json. Freight route, service bypass, independent mating seams, original long-cask carrier envelopes and unverified service headers. Existing rooms are not included or relocated.</desc>')
parts.append('<style>text{font-family:Arial,Helvetica,sans-serif} .tabular{font-variant-numeric:tabular-nums}</style>')
rect(0,0,W,H,C["paper"])
text(60,68,"CRITICAL SHIFT  /  FACILITY CONNECTORS",18,C["muted"],700,letter_spacing=2)
text(60,112,"Fuel Corridor",40,C["ink"],700)
text(1718,72,"A101",38,C["ink"],700,"end")
text(1718,105,"P07  ·  metres  ·  editable SVG",17,C["muted"],400,"end")
line(60,132,1740,132,C["ink"],2)
text(60,167,"01  /  DIMENSIONED FLOORPLAN",17,C["ink"],700)
line(1080,165,1080,1210,C["line"],1)

# Subtle metric grid, for orientation only.
for x in range(-5,19):
    a=xy(x,0);b=xy(x,24);line(*a,*b,"#e2e9e5",.7)
for y in range(0,25):
    a=xy(-5.4,y);b=xy(16.7,y);line(*a,*b,"#e2e9e5",.7)

cells=DATA["floor_cells"]
for cell in cells:
    x0,x1,y0,y1=cell["bounds"]
    p=xy(x0,y1)
    fill="#e9e4d8" if cell["id"].startswith("bypass") or cell["id"]=="plant_header" else "#dde9e7"
    rect(*p,(x1-x0)*S,(y1-y0)*S,fill)

# Exact outer boundary of the union; shared cell lines do not become walls.
xs=sorted({v for c in cells for v in c["bounds"][:2]})
ys=sorted({v for c in cells for v in c["bounds"][2:]})
occupied=set()
for i,(x0,x1) in enumerate(zip(xs,xs[1:])):
    for j,(y0,y1) in enumerate(zip(ys,ys[1:])):
        cx,cy=(x0+x1)/2,(y0+y1)/2
        if any(a<=cx<=b and c<=cy<=d for a,b,c,d in (cell["bounds"] for cell in cells)):
            occupied.add((i,j))
for i,j in sorted(occupied):
    x0,x1,y0,y1=xs[i],xs[i+1],ys[j],ys[j+1]
    for neighbour,a,b in [((i-1,j),(x0,y0),(x0,y1)),((i+1,j),(x1,y0),(x1,y1)),
                           ((i,j-1),(x0,y0),(x1,y0)),((i,j+1),(x0,y1),(x1,y1))]:
        if neighbour not in occupied: line(*xy(*a),*xy(*b),C["ink"],3)

# Routes and clearance circles. The latter are design envelopes, not physics.
freight=DATA["route_centerlines"]["freight"]
bypass=DATA["route_centerlines"]["service_bypass"]
point_line(freight,C["freight"],6)
point_line(bypass,C["bypass"],4,"10 8")
point_line(DATA["route_centerlines"]["plant_header"],C["bypass"],4,"10 8")
bare=DATA["handling"]["cart_rotation_sweep_diameter"]
operating=DATA["handling"]["cart_turn_operating_diameter"]
for p in freight[1:-1]:
    x,y=xy(*p)
    add("circle",cx=x,cy=y,r=operating*S/2,fill=C["paper"],fill_opacity=.82,stroke=C["freight"],stroke_width=1.5)
    add("circle",cx=x,cy=y,r=bare*S/2,fill="none",stroke=C["freight"],stroke_width=1.3,stroke_dasharray="5 4")
    line(x-7,y,x+7,y,C["freight"],1);line(x,y-7,x,y+7,C["freight"],1)
    text(x,y-66,"Ø3.00 m turn allowance",15,C["freight"],600,"middle")
    text(x,y+77,"Ø2.377 conservative sweep",14,C["muted"],400,"middle")

# Actual parked carrier pose: axis+X, wholly north of freight and east of bypass.
cx,cy=xy(2.65,12.32)
rect(cx-1.6*S/2,cy-.9*S/2,1.6*S,.9*S,"#f7fbf8",C["freight"],2,rx=5)
rect(cx-1.245*S/2,cy-.34*S/2,1.245*S,.34*S,"#b7d4d1",C["freight"],1,rx=7)
line(cx-.73*S,cy-.36*S,cx-.73*S,cy+.36*S,C["ink"],2)
text(cx+40,cy,"STAGED CART",14,C["freight"],700)
text(cx+40,cy+19,"1.60 × 0.90",14,C["freight"])

# Nominal architectural clear dimensions, before dressed clearance validation.
world_dim_x(-2.2,2.2,6.4,"4.40 m gross")
world_dim_y(8.4,7.8,12.2,"4.40 m gross")
world_dim_x(12,16.4,14.1,"4.40 m gross")
world_dim_x(-1.2,1.2,15.2,"2.40")
line(*xy(-1.65,14.95),245,556,C["bypass"],1.2)
lines(65,537,["SERVICE AIR RECESS","0.45 deep × 1.40 long","2.45 high; see projection contract"],13,18,C["bypass"])
line(*xy(6.425,13.85),610,560,C["muted"],1.2)
lines(610,524,["PAIRED GATE POCKETS","0.71 × 1.65 m each; H 4.40 m","Outside the freight route"],13,18,C["muted"])
world_dim_y(10.6,18.0,21,"3.00")
world_dim_x(11.4,17.0,22.35,"5.60 enclosure")
label_x,label_y=xy(0,2.2)
rect(label_x-48,label_y-16,96,21,"#dde9e7")
text(label_x,label_y,"ENTRY / Z 0",15,C["ink"],700,"middle")
text(*xy(6.6,11.4),"FREIGHT SPINE",15,C["freight"],700,"middle")
# Internal threshold, showing the actual open storage pose and nominal opening.
for y0,y1 in [(6.4625,8.1375),(11.8625,13.5375)]:
    line(*xy(6.35,y0),*xy(6.35,y1),C["ink"],3.0)
line(*xy(6.35,8.3),*xy(6.35,11.7),C["freight"],1.2,stroke_dasharray="3 4")
line(*xy(6.35,9.4),*xy(8.4,6.25),C["muted"],1.0)
text(*xy(9.2,5.8),"FG01 / 3.40 W × 3.40 H",13,C["muted"],500,"middle")
text(*xy(6.6,18.65),"SERVICE BYPASS",15,C["bypass"],700,"middle")
label_x,label_y=xy(14.2,17.9)
rect(label_x-47,label_y-16,94,21,"#dde9e7")
text(label_x,label_y,"DELIVERY",15,C["freight"],700,"middle")
text(*xy(14.2,21.4),"5.90 m CEILING",13,C["muted"],400,"middle")
text(*xy(-3.3,16.65),"PLANT HEADER",13,C["bypass"],700,"middle")

# Port symbols erase the boundary only over each specified clear opening.
for port in DATA["ports"]:
    x,y,_=port["center"]; nx,ny,_=port["outward"]; tx,ty=-ny,nx
    a=(x-tx*port["clear_width"]/2,y-ty*port["clear_width"]/2)
    b=(x+tx*port["clear_width"]/2,y+ty*port["clear_width"]/2)
    line(*xy(*a),*xy(*b),C["paper"],7)
    line(*xy(*a),*xy(*b),C["red"] if port["id"].startswith("F02") else C["freight"],3)
    for p in (a,b):
        line(*xy(p[0]-.12*nx,p[1]-.12*ny),*xy(p[0]+.12*nx,p[1]+.12*ny),C["ink"],2)

# Labels and leaders stay outside the occupied plan wherever possible.
line(*xy(0,0),300,1120,C["freight"],1.2)
lines(230,1148,["F01 / REFINERY SEAM","2.60 W × 3.00 H  ·  (0,0,0)"],16,23,C["ink"],600)
line(*xy(14.2,24),900,202,C["red"],1.2)
lines(720,202,["F02 / REACTOR OUTER SEAM","5.00 W × 5.00 H"],15,21,C["red"],600)
line(*xy(-5.4,17.4),145,420,C["bypass"],1.2)
lines(120,388,["S01 / PLANT","2.00 × 2.50"],15,22,C["bypass"],600)
line(*xy(6.6,21),555,284,C["bypass"],1.2)
lines(453,262,["S02 / CLEAN HEADER","2.00 × 2.50"],15,22,C["bypass"],600)
line(*xy(16.4,16),975,550,C["bypass"],1.2)
lines(985,576,["S03 / WASTE","2.40 × 3.00"],14,22,C["bypass"],600)

# Overall envelope and centerline chains.
left=xy(-5.4,24)[0];right=xy(17.0,24)[0]
for x in (left,right):line(x,226,x,182,C["line"],1)
dimension(left,183,right,183,"22.40 m overall floor envelope")
for y in (226,1090):line(92,y,145,y,C["line"],1)
dimension(94,226,94,1090,"24.00 m overall",False)
world_dim_x(0,14.2,-3.0,"14.20 m centerline offset")
world_dim_y(17.5,0,10,"10.00")
world_dim_y(17.5,10,24,"14.00")
text(145,1225,"+Y",17,C["muted"],700)
line(157,1210,157,1178,C["muted"],1.5)
add("path",d="M151 1187 L157 1176 L163 1187",fill="none",stroke=C["muted"],stroke_width=1.5)
text(220,1231,"Metres",15,C["muted"])
for i in range(5):rect(300+i*S,1212,S,12,C["ink"] if i%2==0 else C["paper"],C["ink"],.8)
text(300,1244,"0",14,C["muted"],400,"middle");text(480,1244,"5 m",14,C["muted"],400,"middle")

section_title(198,"02","ROUTES & CLEAR HEIGHTS")
lines(1120,246,["Freight centerline: 38.20 m; two 90° turns.","Ceilings: freight 4.40; inlet 3.90; terminal 5.90 m.","Port openings: 2.60 × 3.00 and 5.00 × 5.00 m.","Bypass: 2.40 m nominal; 2.00 m dressed minimum.","Service ceiling 3.00 m; tested headroom 2.20 m.","New finished floor: Z 0; upstand target ≤5 mm."],17,27)

section_title(435,"03","ORIGINAL LONG-CASK CARRIER")
lines(1120,480,["1.60 L × 0.90 W × 1.30 H maximum.","Current payload: 1.245 L × Ø0.340 m.","Conservative route allowance: Ø2.377 m.","Main-turn allowance: Ø3.00 m."],18,28)
line(1130,615,1210,615,C["freight"],2)
text(1230,621,"Operating allowance",16,C["muted"])
line(1130,645,1210,645,C["freight"],1.5,stroke_dasharray="5 4")
text(1230,651,"Bare rectangle sweep",16,C["muted"])
lines(1120,690,["Carrier follows freight route. Main CPU checks","pass a 2.00 m bypass and assumed stretcher turn.","No wheel-steering or runtime collision claim."],17,25,C["muted"])

section_title(800,"04","ADJACENT OWNERSHIP / PLAN DETAILS")
# Two independent source-local sketches, not part of the plan's global assembly.
text(1130,845,"F01 / REFINERY",17,C["ink"],700)
rect(1150,872,2.6*38,1.1*38,"#dde9e7",C["ink"],1.4)
line(1150,914,1248.8,914,C["freight"],3)
text(1265,892,"1.10 m owned sill",15,C["muted"])
text(1265,915,"Connector seam",15,C["freight"])
lines(1130,947,["Nominal 2.60 W × 3.00 H; floor Z 0.","Upstream bollards: 2.49 m clear.","Stored ray check: 2.40 W × 2.20 H."],16,23)

text(1130,1048,"F02 / REACTOR",17,C["red"],700)
rect(1150,1070,5*25,3.7*25,"#dde9e7",C["ink"],1.4)
rect(1150,1070+(3.59*25),125,.1*25,C["red"])
line(1150,1162.5,1275,1162.5,C["red"],3)
lines(1300,1088,["3.70 m owned link stub.","Existing closed door slab:","Y 14.39–14.49 (reactor).", "Outer seam Y 14.50; floor Z 0.","Opening state unresolved."],15,23,C["muted"])

# Bottom notes and legend.
line(60,1270,1740,1270,C["ink"],1.6)
text(60,1304,"HANDOFF LIMITS",16,C["ink"],700)
lines(60,1335,["Separate local mating transforms only; existing refinery and reactor poses are unchanged. No shared assembly proof.","S01 plant, S02 medical/compliance and S03 waste are proposed headers; all external destinations remain unverified.","25.47 s connector-only at assumed 1.50 m/s; room legs, doors and turns excluded. The full 15–30 s target is unverified."],16,25,C["muted"])
text(1735,1405,"SOURCE: interface.json P07  /  CONNECTION_CONTRACTS.md",14,C["muted"],400,"end")
parts.append("</svg>")
OUT.write_text("\n".join(parts)+"\n",encoding="utf-8")

# Meaningful geometry consistency checks for the drawing's analytical claims.
length=lambda pts:sum(math.dist(a,b) for a,b in zip(pts,pts[1:]))
assert math.isclose(length(freight),38.2,abs_tol=1e-9)
assert math.isclose(length(bypass),23.4,abs_tol=1e-9)
assert math.isclose(math.hypot(2.2,.9),bare,abs_tol=1e-6)
for x,y in freight[1:-1]:
    r=operating/2
    assert all(any(a<=x+r*math.cos(t)<=b and c<=y+r*math.sin(t)<=d for a,b,c,d in (cell["bounds"] for cell in cells)) for t in [i*math.tau/360 for i in range(360)])
print(json.dumps({"svg":str(OUT),"freight_m":length(freight),"bypass_m":length(bypass),"bare_turn_diameter":math.hypot(2.2,.9),"turn_allowance_contained_in_plan":True,"scope":"Floor-cell envelope only; no dressed geometry, adjacent rooms or runtime proof"},indent=2))

