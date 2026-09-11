"""Rebuild the dimensioned, section-local architecture SVG without third-party packages."""
from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parent
contract = json.loads((ROOT.parent / "interface.json").read_text(encoding="utf-8"))
S, OX, OY = 42, 430, 1020
parts = []

def add(s): parts.append(s)
def X(x): return OX + x * S
def Y(y): return OY - y * S
def text(x,y,s,size=14,fill="#243646",anchor="start",weight=400,rotate=None):
    tf = f' transform="rotate({rotate} {x} {y})"' if rotate else ""
    add(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}"{tf}>{escape(str(s))}</text>')
def line(x1,y1,x2,y2,stroke="#536b7d",w=1,dash=None):
    da=f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{stroke}" stroke-width="{w}"{da}/>')
def rect(x,y,w,h,fill="#fff",stroke="#536b7d",sw=1,rx=0):
    add(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"/>')
def box(x0,y0,x1,y1,fill,stroke="#536b7d",sw=1): rect(X(x0),Y(y1),(x1-x0)*S,(y1-y0)*S,fill,stroke,sw)
def dimh(x0,x1,py,label,from_y=None):
    a,b=X(x0),X(x1)
    line(a,py,b,py)
    for x in [a,b]:
        line(x-4,py+5,x+4,py-5)
        if from_y is not None: line(x,Y(from_y),x,py-7 if py<Y(from_y) else py+7,"#9fb0b8",.7)
    text((a+b)/2,py-8,label,13,anchor="middle",weight=600)
def dimv(y0,y1,px,label,from_x=None):
    a,b=Y(y0),Y(y1)
    line(px,a,px,b)
    for y in [a,b]:
        line(px-5,y+4,px+5,y-4)
        if from_x is not None: line(X(from_x),y,px+7 if px>X(from_x) else px-7,y,"#9fb0b8",.7)
    text(px-10,(a+b)/2,label,13,anchor="middle",weight=600,rotate=-90)
def arrow(x0,y0,x1,y1,color="#875331",w=2):
    add(f'<path d="M {X(x0):.2f} {Y(y0):.2f} L {X(x1):.2f} {Y(y1):.2f}" stroke="{color}" stroke-width="{w}" fill="none" marker-end="url(#arrow)"/>')
def lines(x,y,rows,size=14,leading=23,fill="#243646"):
    for i,s in enumerate(rows): text(x,y+i*leading,s,size,fill)

add('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1350" viewBox="0 0 1600 1350">')
add('<title>Electrical Room — dimensioned architecture baseline</title>')
add('<desc>Metric floorplan, circulation, equipment envelopes, overhead routes and provisional section interfaces. Main hall 11 by 16.4 metres; side reserve bay 2.8 by 4.4 metres. See documented unresolved issues.</desc>')
add('''<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#875331"/></marker><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" stroke="#df7882" stroke-width="2"/></pattern></defs>''')
add('<g font-family="Segoe UI, Arial, sans-serif">')
rect(0,0,1600,1350,"#f4f3ed","none")
rect(35,35,1530,1280,"#fffefa","#bdc8c8",1)
text(70,89,"ELECTRICAL ROOM",31,weight=700)
text(70,120,"A-01  /  DIMENSIONED DESIGN CONTRACT  /  ALL DIMENSIONS IN METRES",15,"#506777",weight=600)
text(1525,82,f"REV {contract['revision']}  ·  11 SEP 2026",15,anchor="end",weight=700)
text(1525,111,"LOCAL +Y INWARD  /  +Z UP",13,"#506777",anchor="end")
line(70,141,1530,141,"#c4cdcb")

# Datum grid, outside dimensions and scale.
for xx in [-5.5,0,5.5]: line(X(xx),Y(-.25),X(xx),Y(16.65),"#d4dedd",.6,"3 6")
for yy in [0,4,8,12,16.4]: line(X(-5.75),Y(yy),X(8.55),Y(yy),"#d4dedd",.6,"3 6")
dimh(-5.75,8.55,193,"14.30 OVERALL EXTERIOR",16.65)
dimh(-5.75,5.75,242,"11.50 MAIN EXTERIOR",16.65)
dimh(-5.5,5.5,286,"11.00 MAIN CLEAR",16.4)
dimv(-.25,16.65,103,"16.90 MAIN EXTERIOR",-5.75)
dimv(0,16.4,149,"16.40 MAIN CLEAR",-5.5)

# Floors and walls. Shared east wall is retained outside the opening.
box(-5.75,-.25,5.75,16.65,"#56616a","#31404b",1.3)
box(-5.5,0,5.5,16.4,"#f0efe7","none")
box(5.5,10.75,8.55,15.65,"#56616a","#31404b",1.3)
box(5.75,11,8.3,15.4,"#ebece2","none")
box(5.5,12,5.75,14.4,"#ebece2","none")
box(-1.2,-.26,1.2,.01,"#e3f0e9","none")
box(-1.2,16.39,1.2,16.66,"#e3f0e9","none")

# Circulation and service zones from contract.
box(-1.2,0,1.2,16.4,"#d5e9dc","none")
box(1.2,12,7.35,14.4,"#dceadf","none")
for eq in contract["equipment_zones"]:
    a,b=eq["service_xy_min"],eq["service_xy_max"]
    box(*a,*b,"#dceaf0","#7799a9",.7)
for eq in contract["equipment_zones"]:
    a,b=eq["xy_min"],eq["xy_max"]
    fc={"SG":"#91a7ac","TX":"#b2b5ad","TD":"#c49d63","RB":"#95a7a2","WB":"#c3af91"}[eq["id"]]
    box(*a,*b,fc,"#344956",1.8)
    midx,midy=(a[0]+b[0])/2,(a[1]+b[1])/2
    text(X(midx),Y(midy)+5,eq["id"],19,anchor="middle",weight=700)
    dx=eq["service_front"][0]
    edge=b[0] if dx>0 else a[0]
    arrow(edge,midy,edge+dx*.48,midy)
    if eq["id"]=="SG":
        for yy in [4.5,5.7,6.9,8.1,9.3]: line(X(a[0]),Y(yy),X(b[0]),Y(yy),"#344956",1)
    if eq["id"]=="RB":
        for yy in [12.7,13.7]: line(X(a[0]),Y(yy),X(b[0]),Y(yy),"#344956",1)
    if eq["id"]=="TX":
        for yy in [4.95,5.25,7.55,7.85]: line(X(3.18),Y(yy),X(5.17),Y(yy),"#6a797b",1)

blocked=contract["circulation"]["reserve_branch_design"]["status"]!="clear_design_intent"
if blocked:
    box(4.35,12,5.3,14.4,"url(#hatch)","#b93b4c",1.6)
    text(X(4.82),Y(13.2)+40,"!",23,"#a82e42",anchor="middle",weight=700)

# Overhead bus, built centreline; utility bindings remain provisional.
line(X(-4.32),Y(0),X(-4.32),Y(16.4),"#b97026",5,"11 6")
line(X(-4.32),Y(6.4),X(4.175),Y(6.4),"#b97026",5,"11 6")
text(X(-4.32)-10,Y(1.7),"BUS CL z3.88",12,"#8b5620",rotate=-90)
text(X(.15),Y(6.4)-12,"OVERHEAD BRANCH",11,"#8b5620",anchor="middle",weight=600)

# Portals and paired sliding leaves parked parallel to hall-side walls.
for yy,label in [(0,"D01"),(16.4,"D02")]:
    line(X(-1.2),Y(yy),X(1.2),Y(yy),"#875331",3)
    text(X(0),Y(yy)+(23 if yy==0 else -15),label+" · 2.40 × 2.70",13,"#875331",anchor="middle",weight=700)
    py=yy+.30 if yy==0 else yy-.30
    for leaf_min,leaf_max in [(-2.49,-1.23),(1.23,2.49)]:
        line(X(leaf_min),Y(py),X(leaf_max),Y(py),"#9b8064",.07*S)
line(X(5.5),Y(12),X(5.5),Y(14.4),"#875331",3)
text(X(6.43),Y(15.08),"RESERVE BAY",12,anchor="middle",weight=700)
text(X(6.40),Y(11.27),"P03 · 2.40 × 3.20",11,"#875331",anchor="middle",weight=700)
arrow(0,.45,0,1.65)
arrow(0,14.5,0,15.75)
text(X(0),Y(12.7),"2.40 CLEAR",13,"#276246",anchor="middle",weight=700,rotate=-90)
dimh(-1.2,1.2,Y(2.3),"2.40 ROUTE")
dimh(-3.55,-1.2,Y(3.62),"2.35 WORK")
dimh(1.2,3.05,Y(5.38),"1.85 ACCESS")
dimh(5.75,7.35,Y(12.15),"1.60")
dimh(2.3,4.35,Y(9.65),"2.05 WORK")

# Stretcher test body, origin and axes.
box(-.4,8.65,.4,10.85,"#fafcf6","#3d7460",1.5)
line(X(-.34),Y(10.38),X(.34),Y(10.38),"#3d7460",1)
text(X(0),Y(9.75),"0.8 × 2.2",11,"#3d7460",anchor="middle",rotate=-90)
text(X(1.42),Y(9.95),"CART /",11,"#3d7460")
text(X(1.42),Y(9.60),"STRETCHER",11,"#3d7460")
add(f'<circle cx="{X(0)}" cy="{Y(0)}" r="5" fill="#875331"/>')
text(X(-1.55),Y(-.55),"(0,0,0)",12,"#875331",anchor="end")
arrow(-4.7,.6,-3.7,.6)
arrow(-4.7,.6,-4.7,1.6)
text(X(-3.58),Y(.6)+5,"+X",12)
text(X(-4.7),Y(1.75),"+Y",12,anchor="middle")

# Socket labels.
for p,label in [((-4.32,0),"U01"),((-4.32,16.65),"U02"),((8.55,14),"U03")]:
    add(f'<circle cx="{X(p[0])}" cy="{Y(p[1])}" r="6" fill="#fff8e9" stroke="#a56621" stroke-width="2"/>')
    text(X(p[0])-10,Y(p[1])-12,label,12,"#8b5620",anchor="end",weight=700)

# Outer bay perimeter dimensions and all stepped lengths.
dimv(10.75,15.65,843,"4.90 BAY EXTERIOR",8.55)
dimv(-.25,10.75,875,"11.00 LOWER EAST RUN",5.75)
dimv(15.65,16.65,843,"1.00",5.75)
dimh(5.75,8.55,Y(15.65)-35,"2.80 PROJECTION",15.65)
dimh(5.75,8.55,Y(10.75)+31,"2.80 PROJECTION",10.75)
dimh(-5.75,5.75,1100,"11.50 SOUTH EXTERIOR",-.25)
dimh(-5.5,-1.2,1142,"4.30",0)
dimh(-1.2,1.2,1142,"2.40",0)
dimh(1.2,5.5,1142,"4.30",0)
text(216,1188,"PLAN / orthographic top view; z=0 finished floor",15,weight=600)
text(216,1213,"Wall thickness 0.25 · hall ceiling 4.80 · reserve ceiling 3.60",13,"#506777")
for i in range(5): rect(216+i*S,1240,S,10,"#344956" if i%2==0 else "#fffefa","#344956",1)
for i in [0,1,2,3,4,5]: text(216+i*S,1270,str(i)+(" m" if i==5 else ""),11,anchor="middle")

# Right-hand schedule. Each row is parallel information, all exact bounds included.
RX=940
text(RX,192,"01  PORTALS & TOPOLOGY",19,weight=700)
lines(RX,219,["D01  (0, 0, 0) → Turbine Room; provisional", "D02  (0, 16.40, 0) → Waste Storage; provisional", "Both: 2.40 W × 2.70 H; leaves park hall-side, no swing.", "Leaves x=±1.23…2.49; depth 0.30; fittings ≤0.50.", "P03 (5.50,13.20,0); y=12.00…14.40; end gaps 1.00.", "Owned level seams: D01 to -0.25; D02 to 16.97.", "Measured mating transforms: see CONNECTIONS.md."],13,20)
line(RX,358,1515,358,"#c4cdcb")
text(RX,391,"02  EQUIPMENT ENVELOPES",19,weight=700)
rows=[
 ("SG · SWITCHGEAR", "1.55 × 7.70; front +X", "x −5.10…−3.55 / y 3.20…10.90"),
 ("TX · TRANSFORMER", "2.25 × 3.40; front −X", "x 3.05…5.30 / y 4.70…8.10"),
 ("TD · TRANSFER / PRIORITY", "0.95 × 1.70; front −X", "x 4.35…5.30 / y 9.45…11.15"),
 ("RB · RESERVE CABINETS", "0.80 × 3.00; front −X", "x 7.35…8.15 / y 11.70…14.70"),
 ("WB · REPAIR BENCH", "1.70 × 2.60; front +X", "x −5.25…−3.55 / y 12.60…15.20")]
for i,(a,b,c) in enumerate(rows):
    yy=422+i*69
    text(RX,yy,a,14,weight=700)
    text(RX+310,yy,b,13,anchor="start")
    text(RX,yy+22,c,13,"#506777")
line(RX,759,1515,759,"#c4cdcb")
text(RX,793,"03  HEADROOM & UTILITY SECTION",19,weight=700)
lines(RX,824,["Main ceiling z=4.80; reserve ceiling z=3.60.", "Main bus CL: x=−4.32, z=3.88; y=0…16.65.", "Transformer branch crosses at y=6.40, CL z=3.88.", "Route-crossing duct/support underside ≥3.50.", "D01/D02: 2.70 H; P03: 3.20 H; thresholds flush.", "U03 essential inlet: (8.55, 14.00, 2.80), +X.", "Dashed bus lines record the built centrelines.", "Ratings, capacity and utility bindings unresolved."],13,22)
line(RX,1007,1515,1007,"#c4cdcb")
text(RX,1041,"04  CIRCULATION / REVIEW STATUS",19,weight=700)
status_lines=(["TD overlaps the direct P03 reserve access path.", "Hatched conflict must be corrected before acceptance."] if blocked else ["TD placement revised to clear the P03 branch.", "Saved local geometry/sweeps pass; engine checks pending."])
lines(RX,1072,status_lines,13,22,"#a32e41" if blocked else "#276246")
lines(RX,1122,["Straight 0.80 × 2.20 cart: 0.80 side allowance.", "Turn envelope diagonal 2.341; test carriers in engine.", "Blue: working space. Green: keep-clear passage.", "Device doors/tools must stay out of main aisle.", "Dimensions are implementation decisions, not canon.", "Architecture + interface.json define the same baseline."],13,22)
add('</g></svg>')
(ROOT / "floorplan.svg").write_text("\n".join(parts),encoding="utf-8")
print(ROOT / "floorplan.svg")



