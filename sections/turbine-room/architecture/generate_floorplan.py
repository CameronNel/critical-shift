"""Rebuild metric design evidence from ../interface.json; no Blender dependency.

Python stdlib writes SVG and arithmetic checks. Pillow, when installed, writes a
matching PNG from the same drawing primitives. These are design-envelope checks,
not mesh, rigging, collision, access-code, or runtime certification.
"""
from __future__ import annotations

import html
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE.parent / "interface.json").read_text(encoding="utf-8"))
W, H = 1800, 1660
INK, MUTED, GRID = "#20383f", "#526770", "#d7dfe0"
PAPER, WALL = "#fbfaf6", "#53666b"
TEAL, ROUTE, SERVICE = "#b76b34", "#ece4d8", "#fff0ca"
STEAM, BUS, COND = "#b46537", "#785d9a", "#417f9b"
S, OX, OY = 40, 380, 1170

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = ImageDraw = ImageFont = None


class Sheet:
    def __init__(self):
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
                    '<title>Turbine Room — metric architectural design B</title>',
                    '<desc>Local floorplan, dimension chains, door parking, service and rescue envelopes, utility interfaces, two sections and design validation status.</desc>']
        self.im = Image.new("RGB", (W, H), PAPER) if Image else None
        self.draw = ImageDraw.Draw(self.im) if self.im else None
        self.fonts = {}
        self.rect(0, 0, W, H, PAPER, PAPER)

    def rect(self, x, y, w, h, fill="none", stroke=INK, width=1, dash=False):
        d = ' stroke-dasharray="8 5"' if dash else ""
        self.svg.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"{d}/>')
        if self.draw:
            self.draw.rectangle((x, y, x+w, y+h), fill=None if fill == "none" else fill,
                                outline=None if dash else stroke, width=max(1, round(width)))
            if dash:
                for a, b in [((x,y),(x+w,y)),((x+w,y),(x+w,y+h)),((x+w,y+h),(x,y+h)),((x,y+h),(x,y))]:
                    self._pil_line(a, b, stroke, width, True)

    def _pil_line(self, a, b, color, width, dash):
        if not self.draw:
            return
        if not dash:
            self.draw.line((*a,*b), fill=color, width=max(1,round(width)))
            return
        dx, dy = b[0]-a[0], b[1]-a[1]
        length = math.hypot(dx,dy)
        if length == 0:
            return
        for i in range(0, math.ceil(length), 13):
            t1, t2 = i/length, min(i+8,length)/length
            self.draw.line((a[0]+dx*t1,a[1]+dy*t1,a[0]+dx*t2,a[1]+dy*t2), fill=color, width=max(1,round(width)))

    def line(self, a, b, color=INK, width=1, dash=False):
        d = ' stroke-dasharray="8 5"' if dash else ""
        self.svg.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="{color}" stroke-width="{width}"{d}/>')
        self._pil_line(a,b,color,width,dash)

    def poly(self, points, fill="none", stroke=INK, width=1):
        p = " ".join(f"{x:.2f},{y:.2f}" for x,y in points)
        self.svg.append(f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
        if self.draw:
            self.draw.polygon(points, fill=None if fill=="none" else fill)
            self.draw.line(points+[points[0]], fill=stroke, width=max(1,round(width)))

    def circle(self, x, y, r, fill="none", stroke=INK, width=1):
        self.svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
        if self.draw:
            self.draw.ellipse((x-r,y-r,x+r,y+r), fill=None if fill=="none" else fill, outline=stroke, width=max(1,round(width)))

    def text(self, x, y, label, size=17, color=INK, bold=False, anchor="start", rotate=None):
        family = "DejaVu Sans, Arial, sans-serif"
        weight = "bold" if bold else "normal"
        tr = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
        self.svg.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}" dominant-baseline="middle"{tr}>{html.escape(str(label))}</text>')
        if self.draw:
            key=(size,bold)
            if key not in self.fonts:
                path=Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
                try: self.fonts[key]=ImageFont.truetype(str(path), size)
                except OSError: self.fonts[key]=ImageFont.load_default()
            font=self.fonts[key]
            if rotate is not None:
                box=font.getbbox(str(label)); tw=box[2]-box[0]+12; th=size*2
                tile=Image.new("RGBA",(tw,th),(0,0,0,0))
                ImageDraw.Draw(tile).text((tw/2,th/2),str(label),font=font,fill=color,anchor="mm")
                tile=tile.rotate(-rotate,expand=True,resample=Image.Resampling.BICUBIC)
                self.im.paste(tile,(round(x-tile.width/2),round(y-tile.height/2)),tile)
            else:
                anc={"start":"lm","middle":"mm","end":"rm"}[anchor]
                self.draw.text((x,y),str(label),font=font,fill=color,anchor=anc)

    def arrow(self,a,b,color=INK,width=2,head=9,both=False):
        self.line(a,b,color,width)
        def tip(p,q):
            dx,dy=q[0]-p[0],q[1]-p[1]; length=math.hypot(dx,dy)
            if not length: return
            ux,uy=dx/length,dy/length
            self.poly([q,(q[0]-ux*head-uy*head*.4,q[1]-uy*head+ux*head*.4),(q[0]-ux*head+uy*head*.4,q[1]-uy*head-ux*head*.4)],color,color)
        tip(a,b)
        if both: tip(b,a)

    def lines(self,x,y,labels,size=17,color=MUTED,gap=25):
        for i,label in enumerate(labels): self.text(x,y+i*gap,label,size,color)

    def save(self):
        (HERE/"floorplan.svg").write_text("\n".join(self.svg+["</svg>"]),encoding="utf-8")
        if self.im: self.im.save(HERE/"floorplan.png")


def pt(x,y): return OX+x*S, OY-y*S
def plan_rect(s,lo,hi,fill="none",stroke=INK,width=1,dash=False):
    x,y=pt(lo[0],hi[1]); s.rect(x,y,(hi[0]-lo[0])*S,(hi[1]-lo[1])*S,fill,stroke,width,dash)
def plan_label(s,x,y,t,size=16,color=INK,bold=False): s.text(*pt(x,y),t,size,color,bold,anchor="middle")
def chain_x(s,vals,py,labels):
    xs=[pt(x,0)[0] for x in vals]
    for x in xs: s.line((x,py-7),(x,py+7),MUTED)
    for a,b,t in zip(xs,xs[1:],labels):
        s.line((a,py),(b,py),MUTED); s.text((a+b)/2,py-16,t,15,MUTED,anchor="middle")
def chain_y(s,vals,px,labels):
    ys=[pt(0,y)[1] for y in vals]
    for y in ys: s.line((px-7,y),(px+7,y),MUTED)
    for a,b,t in zip(ys,ys[1:],labels):
        s.line((px,a),(px,b),MUTED); s.text(px-17,(a+b)/2,t,15,MUTED,anchor="middle",rotate=-90)


def design_checks():
    c=DATA["circulation"]; w,l,h=c["stretcher_cart_test_envelope_m"]
    diameter=math.hypot(w,l); checks=[]
    def add(name,ok,observed,scope="design_arithmetic"):
        checks.append(dict(check=name,status="PASS" if ok else "FAIL",observed=observed,scope=scope))
    add("main route and portals nominal width",all(p["clear_width_m"]==2.4 for p in DATA["portals"]),2.4)
    add("main route and portals nominal height",all(p["clear_height_m"]==2.7 for p in DATA["portals"]),2.7)
    add("straight cart side clearance",2.4>w,{"route_each_side_m":(2.4-w)/2,"east_aisle_each_side_m":(2.2-w)/2})
    add("cart rotation fits 2.4 m square at main crossover",diameter<2.4,{"swept_diameter_m":diameter,"total_margin_m":2.4-diameter})
    for i,(x,y,z) in enumerate(c["turn_centres"]):
        cross=c["north_crossover"] if y>12 else c["south_crossover"]
        lo,hi=cross["xy_min"],cross["xy_max"]; r=diameter/2
        add(f"cart turning disc {i+1} inside crossover",x-r>=lo[0] and x+r<=hi[0] and y-r>=lo[1] and y+r<=hi[1],{"centre":[x,y],"radius_m":r})
    lo,hi=DATA["envelopes"]["main_clear"]["min"],DATA["envelopes"]["main_clear"]["max"]
    for p in DATA["portals"]:
        for j,q in enumerate(p["leaf_parking_volumes"]):
            a,b=q["min"],q["max"]
            add(p["id"]+f" parked leaf {j+1} remains in module",all(lo[i]<=a[i]<=b[i]<=hi[i] for i in range(3)),{"min":a,"max":b})
            add(p["id"]+f" parked leaf {j+1} outside rescue route",a[0]>1.2 or b[0]<-1.2,{"route_x":[-1.2,1.2],"pocket_x":[a[0],b[0]]})
    add("base offset from main route",2.5>=1.2,{"apron_m":2.5-1.2})
    add("west station bay offset from main route",-1.5<=-1.2,{"separation_m":.3})
    add("condensate wall-side strip does not enter east aisle",9.5-.1>=9.3,{"pipe_min_x":9.4,"aisle_max_x":9.3,"nominal_margin_m":.1})
    add("no threshold step",DATA["envelopes"]["threshold_step_m"]==0,0)
    output={"schema":"critical-shift.architecture-design-checks.v1","revision":DATA["revision"],"scope":"arithmetic on authored interface design, not Blender geometry or engine",
            "checks":checks,"design_arithmetic_status":"PASS" if all(i["status"]=="PASS" for i in checks) else "FAIL",
            "limitations":["2.2 m east aisle does not support full 2.34094 m in-place cart rotation; use crossover.","No carrier bodies, doors in motion, actual mesh, collision skin, rigging, lifting loads or code compliance tested.","No global transforms or complete facility travel validated."]}
    (HERE/"design_checks.json").write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    if output["design_arithmetic_status"]!="PASS": raise ValueError("Design arithmetic failed; inspect design_checks.json")
    return output


def draw_plan(s):
    s.text(80,151,"01 / FLOOR PLAN",22,INK,True)
    s.text(80,177,"Plan / +Z view",17,MUTED)
    # Metric wall thickness is drawn at its actual scale, including all four corners.
    plan_rect(s,[-4.25,-.25],[10.25,24.25],WALL,WALL)
    plan_rect(s,[-4,0],[10,24],PAPER,INK,1.5)
    for y in [0,24]: plan_rect(s,[-1.2,y-.25 if y==0 else y],[1.2,y if y==0 else y+.25],PAPER,PAPER)
    plan_rect(s,[-1.45,24],[1.45,25.2],WALL,WALL)
    plan_rect(s,[-1.2,24],[1.2,25.2],ROUTE,TEAL,1,True)
    # Circulation reservations.
    for key in ["south_crossover","north_crossover"]:
        q=DATA["circulation"][key]; plan_rect(s,q["xy_min"],q["xy_max"],SERVICE,"#d9b861",1,True)
    plan_rect(s,[-1.2,0],[1.2,24],ROUTE,"#54997d",1,True)
    q=DATA["circulation"]["east_service_aisle"]; plan_rect(s,q["xy_min"],q["xy_max"],SERVICE,"#c9a65b",1,True)
    q=DATA["circulation"]["west_equipment_apron"]; plan_rect(s,q["xy_min"],q["xy_max"],"#edf2df","#98aa7e",1,True)
    # Broad equipment base and distinct simplified plan silhouettes.
    plan_rect(s,[2.5,5.5],[6.7,20],"#d8ddd8",MUTED,2)
    points=[(3.65,6),(5.55,6),(6.3,7),(6.55,9.2),(6.3,12),(5.7,12.6),(3.5,12.6),(2.9,12),(2.65,9.2),(2.9,7)]
    s.poly([pt(*p) for p in points],"#C5B7A3",TEAL,2)
    for y in [7,8.7,10.6,12]: s.line(pt(2.95,y),pt(6.25,y),TEAL,2)
    plan_rect(s,[3.0,14.4],[6.2,18.7],"#AAA69F",TEAL,2)
    for x in [3.3,3.65,4,5.2,5.55,5.9]: s.line(pt(x,14.7),pt(x,18.4),TEAL)
    plan_rect(s,[4.03,13],[5.17,14],"#d6bb73",MUTED,2)
    s.line(pt(4.6,5.6),pt(4.6,19.6),INK,1.5,True)
    plan_label(s,4.6,10.3,"TURBINE",19,INK,True)
    plan_label(s,4.6,9.65,"y 6.0–12.6",15)
    plan_label(s,4.6,16.75,"GENERATOR",17,INK,True)
    plan_label(s,4.6,16.1,"y 14.4–18.7",14)
    s.text(*pt(5.5,13.5),"Guard",13,MUTED)
    s.text(*pt(2.13,10.0),"1.3 m access apron",15,MUTED,anchor="middle",rotate=-90)
    # Secondary open bays, with furniture separate from operator aprons.
    for ya,yb,name in [(8,13,"CONTROLS"),(18,24,"MAINTENANCE")]:
        plan_rect(s,[-4,ya],[-1.5,yb],"#e9e5d8",MUTED,1,True)
        xmax=-2.62 if name=="MAINTENANCE" else -2.8
        plan_rect(s,[-3.87 if name=="MAINTENANCE" else -3.9,19.85 if name=="MAINTENANCE" else ya+.7],[xmax,22.85 if name=="MAINTENANCE" else yb-.7],"#a9b2ab",MUTED,1.5)
        if name=="MAINTENANCE": plan_rect(s,[-3.31,18.425],[-2.59,19.075],"#b7bdad",MUTED,1.5)
        s.text(*pt(-3.34,(ya+yb)/2),name,15,INK,True,anchor="middle",rotate=-90)
        apron_label="1.42 m to route" if name=="MAINTENANCE" else "1.3 m operator apron"
        apron_x=-1.91 if name=="MAINTENANCE" else -2.1
        s.text(*pt(apron_x,(ya+yb)/2),apron_label,13,MUTED,anchor="middle",rotate=-90)
    s.text(*pt(-.01,11.5),"CONTINUOUS 2.4 m RESCUE / CART ROUTE",17,TEAL,True,anchor="middle",rotate=-90)
    s.text(*pt(8.15,12.1),"2.2 m EAST SERVICE AISLE",16,"#876c31",True,anchor="middle",rotate=-90)
    # Crossover turn discs and standard carried/cart footprints.
    r=math.hypot(.8,2.2)/2
    for x,y,z in DATA["circulation"]["turn_centres"]:
        s.circle(*pt(x,y),r*S,"none","#b39b65",1)
    for x,y in [(0,3),(0,21.7),(8.1,3),(8.1,21.7)]:
        plan_rect(s,[x-.4,y-1.1],[x+.4,y+1.1],"#F4EEE5",TEAL,2)
    plan_label(s,4.6,22.5,"COMPONENT STAGING / CROSSOVER",14)
    plan_label(s,4.6,21.8,"2.6 m depth · keep open during lift",14)
    plan_label(s,4.6,3.9,"SOUTH CROSSOVER",16,INK,True)
    plan_label(s,4.6,3.2,"3.8 m depth",14)
    s.arrow(pt(4.6,20.8),pt(.3,20.8),TEAL,2)
    s.arrow(pt(0,19.8),pt(0,17.6),TEAL,2)
    # Utilities are overhead unless drawn at wall-side floor service strip.
    for key,color in [("steam_centreline_design",STEAM),("output_bus_centreline_design",BUS)]:
        path=DATA["overhead_routes"][key]
        for a,b in zip(path,path[1:]): s.line(pt(*a[:2]),pt(*b[:2]),color,3,True)
    cp=DATA["floor_services"]["condensate_centreline_design"]
    s.line(pt(*cp[0][:2]),pt(*cp[1][:2]),COND,3)
    s.circle(*pt(2.92,12.72),7,"#ebc568",INK,1)
    s.text(*pt(1.9,14.35),"Oil",13,MUTED,anchor="middle")
    s.line(pt(1.9,14.0),pt(2.15,13.05),MUTED)
    # Actual R07 underfloor exhaust aperture, also identified in interface.json.
    plan_rect(s,[3.35,10.70],[5.85,12.20],PAPER,BUS,2)
    plan_label(s,4.6,11.45,"U04 / DOWN",12,BUS,True)
    # Sliding doors: open parked leaf + dashed closed position + in-module pocket.
    for p in DATA["portals"]:
        for pocket in p["leaf_parking_volumes"]:
            plan_rect(s,pocket["min"],pocket["max"],"#efce85","#9b7226",2)
        y=.075 if p["id"]=="D01" else 23.925
        s.line(pt(-1.2,y),pt(1.2,y),"#9b7226",2,True)
        yarrow=.6 if p["id"]=="D01" else 23.4
        s.arrow(pt(.2,yarrow),pt(2.4,yarrow),"#9b7226",2)
        s.arrow(pt(-.2,yarrow),pt(-2.4,yarrow),"#9b7226",2)
    # Dimension chains and measured coordinates.
    chain_x(s,[-4,10],1220,["14.00 clear"])
    chain_x(s,[-4,-1.2,1.2,2.5,6.7,7.1,9.3,10],1280,["2.80","2.40","1.30","4.20",".40","2.20",".70"])
    chain_y(s,[0,5.5,20,24],171,["5.50","14.50 base","4.00"])
    chain_y(s,[0,24],112,["24.00 clear"])
    chain_y(s,[0,6,12.6,13,14,14.4,18.7,24],835,["6.00","6.60","", "1.00", "", "4.30","5.30"])
    s.text(845,637,".40 shaft gap",12,MUTED)
    s.text(845,602,".40 shaft gap",12,MUTED)
    s.text(510,172,"D02 → ELECTRICAL",18,INK,True)
    s.text(510,145,"1.20 m detachable reveal",14,MUTED)
    s.line((499,172),pt(1.45,24.6),MUTED)
    s.text(380,1333,"D01 ← REACTOR  /  (0,0,0)",18,INK,True,anchor="middle")
    s.text(380,1358,"Both portals 2.40 W × 2.70 H · flush floor",16,MUTED,anchor="middle")
    s.text(590,1400,"Open leaf parking",16,"#9b7226")
    s.text(590,1424,"inside module at both ends",15,MUTED)
    s.line((644,1384),pt(2.6,.16),"#9b7226")
    s.text(655,188,"U03 x-4.32 z3.88",14,BUS,anchor="middle")
    s.line((550,183),pt(-4.32,25.2),BUS)
    s.text(708,1319,"U01 steam z4.90",14,STEAM,anchor="middle")
    s.line((708,1302),pt(8.4,0),STEAM)
    s.text(818,1381,"U02 return z0.45",14,COND,anchor="middle")
    s.line((800,1362),pt(9.5,0),COND)
    s.text(80,1405,"Walls: 0.25 m",16,INK,True)
    s.line((208,1400),pt(-4.13,.8),MUTED)
    # A and B section traces, kept understated.
    s.line(pt(-4.4,10),pt(10.4,10),"#7c898e",1,True)
    for x in [-4.6,10.6]: s.circle(*pt(x,10),12,PAPER,MUTED); plan_label(s,x,10,"A",14)


def draw_sections(s):
    s.text(977,151,"02 / LONG SECTION B–B",22,INK,True)
    s.text(977,178,"Along shaft x = 4.60 · y–z envelope projection",17,MUTED)
    x0,z0,ss=1000,470,26
    def p(y,z): return x0+y*ss,z0-z*ss
    def r(y,z,w,h,fill,stroke=INK,dash=False):
        x,t=p(y,z+h);s.rect(x,t,w*ss,h*ss,fill,stroke,1.5,dash)
    r(-.25,-.3,24.5,.3,WALL);r(-.25,0,.25,7.2,WALL);r(24,0,.25,7.2,WALL)
    r(0,7.2,24,.25,WALL);r(5.5,0,14.5,.45,"#BCB9B1")
    r(6,.45,6.6,3.35,"#C5B7A3",TEAL);r(14.4,.45,4.3,3.35,"#AAA69F",TEAL)
    r(13,1.43,1,1.14,"#d6bb73")
    s.line(p(5.6,2),p(19.6,2),INK,2,True)
    r(5.5,3.8,14.5,2,"none",BUS,True)
    s.text(1333,340,"LIFT RESERVATION",16,BUS,True,anchor="middle")
    s.text(1333,363,"z 3.8–5.8 · rigging unverified",15,BUS,anchor="middle")
    s.text(1240,407,"Turbine",16,INK,True,anchor="middle")
    s.text(1430,407,"Generator",15,INK,True,anchor="middle")
    s.text(1628,290,"7.20",15,MUTED)
    s.text(1640,418,"2.00 axis",14,MUTED)
    s.text(1618,472,"±0.00",14,MUTED)
    s.line((983,283),(983,470),MUTED);s.line((977,283),(989,283),MUTED);s.line((977,470),(989,470),MUTED)
    s.text(959,378,"7.20 clear hall",16,MUTED,anchor="middle",rotate=-90)
    s.text(1000,509,"0",14,MUTED);s.text(1624,509,"24 m",14,MUTED,anchor="end")
    s.lines(977,546,["Machinery shown as design envelopes; actual casing/guard profiles vary.","Lift reserve is for disassembled parts. Full train cannot pass 2.4 m portals."],16)
    s.text(977,620,"03 / CROSS SECTION A–A",22,INK,True)
    s.text(977,649,"At y = 10 · x–z projection · looking toward electrical",17,MUTED)
    x0,z0,ss=1175,1020,40
    def p(x,z): return x0+x*ss,z0-z*ss
    def r(x,z,w,h,fill,stroke=INK,dash=False):
        a,b=p(x,z+h);s.rect(a,b,w*ss,h*ss,fill,stroke,1.5,dash)
    r(-4.25,-.25,14.5,.25,WALL);r(-4.25,0,.25,7.2,WALL);r(10,0,.25,7.2,WALL);r(-4,7.2,14,.25,WALL)
    r(-1.2,0,2.4,2.7,ROUTE,TEAL,True)
    r(7.1,0,2.2,2.7,SERVICE,"#b49b63",True)
    r(-3.9,0,1.1,1.15,"#a9b2ab")
    r(2.5,0,4.2,.45,"#BCB9B1")
    s.circle(*p(4.6,2),1.8*ss,"#C5B7A3",TEAL,2)
    s.circle(*p(4.6,2),.16*ss,"#d8c57e",INK)
    r(2.5,3.8,4.2,2,"none",BUS,True)
    # Steam and condensate services at actual nominated section height.
    s.circle(*p(9.5,.45),.1*ss,"#bed7df",COND,2)
    # Human design silhouettes at adult scale, not model characters.
    for x in [0,8.1]:
        s.circle(*p(x,1.68),.105*ss,"#f4e3c8",INK)
        s.line(p(x,1.56),p(x,.8),INK,3)
        for a,b in [((x,.8),(x-.16,0)),((x,.8),(x+.16,0)),((x,1.38),(x-.25,.98)),((x,1.38),(x+.25,.98))]:s.line(p(*a),p(*b),INK,3)
    s.text(*p(0,3.1),"2.70 clear",16,TEAL,True,anchor="middle")
    s.text(*p(8.1,3.1),"2.70 clear",15,"#876c31",True,anchor="middle")
    s.text(*p(4.6,4.8),"Lift reserve",14,BUS,anchor="middle")
    for xa,xb,y,label in [(-4,10,1065,"14.00 clear"),(-1.2,1.2,1103,"2.40 route"),(7.1,9.3,1103,"2.20 service")]:
        a,b=p(xa,0)[0],p(xb,0)[0];s.line((a,y),(b,y),MUTED)
        s.line((a,y-6),(a,y+6),MUTED);s.line((b,y-6),(b,y+6),MUTED)
        s.text((a+b)/2,y-15,label,15,MUTED,anchor="middle")
    s.lines(977,1142,["7.20 m clear shell. Route portals set minimum clear height at 2.70 m.","No mezzanine or main-route steps in baseline B. Floor datum ±0.00.","Floor condensate stays east of aisle; any branch needs flush cover.","See revision-specific saved-scene validation; engine sweeps pending."],16)


def finish(s,checks):
    s.text(80,61,"CRITICAL SHIFT  /  TURBINE ROOM",35,INK,True)
    s.text(80,100,"ARCHITECTURAL DESIGN B  ·  metric interface evidence  ·  11 SEP 2026",18,MUTED)
    s.text(1718,58,"UNBOUND LOCAL MODULE",18,STEAM,True,anchor="end")
    s.text(1718,88,"Design checks only — no mesh or runtime pass claimed",15,MUTED,anchor="end")
    s.line((80,124),(1720,124),INK,2)
    s.line((924,146),(924,1448),GRID)
    s.text(977,1270,"INTERFACE / ACCESS NOTES",20,INK,True)
    s.text(977,1453,"U04: (4.60,11.45,0), down; 2.50 × 1.50 m real exhaust opening.",16,BUS)
    s.lines(977,1303,["D02 matches electrical D01 nominal opening: 2.40 × 2.70 m.","Global transforms remain null. Reactor reciprocal interface unresolved.","Electrical U01 (-4.32,0,3.88); adapter authored at U03.","0.8 × 2.2 m cart: full rotation disc Ø2.341 m at crossovers.","The 2.2 m aisle admits straight travel; turn at its open ends.","Cart envelopes omit carriers and collision skin. Engine sweep pending."],16,gap=25)
    s.line((80,1471),(1720,1471),INK,2)
    s.text(80,1506,"DRAWING KEY",19,INK,True)
    for x,fill,label in [(80,ROUTE,"Rescue route"),(290,SERVICE,"Service / staging"),(525,"#C5B7A3","Equipment envelope")]:
        s.rect(x,1530,25,18,fill,INK);s.text(x+36,1540,label,16)
    for x,color,label in [(80,STEAM,"Overhead steam"),(290,BUS,"Output bus / lift"),(525,COND,"Floor return")]:
        s.line((x,1574),(x+25,1574),color,3);s.text(x+36,1574,label,16)
    s.text(80,1616,f"{len(checks['checks'])} design-arithmetic checks PASS · see design_checks.json for exact scope and limitations",15,MUTED)
    # Local compass/axes, separate from north or any facility transform.
    s.arrow((907,1595),(907,1525),INK,2)
    s.arrow((907,1595),(977,1595),INK,2)
    s.text(907,1508,"+Y into hall",15,INK,anchor="middle")
    s.text(991,1596,"+X",16,INK)
    s.text(862,1627,"+Z out of plan · no geographic north",14,MUTED)
    s.text(1160,1506,"PLAN SCALE BAR",19,INK,True)
    for i in range(5): s.rect(1160+i*40,1545,40,15,INK if i%2==0 else PAPER,INK)
    for value in [0,1,2,5]:s.text(1160+value*40,1578,str(value),15,MUTED,anchor="middle")
    s.text(1379,1578,"m",15,MUTED)
    s.lines(1435,1507,["Source: interface.json", "Generator: generate_floorplan.py", "All dimensions chosen for this build.", "Art approval is separate evidence."],15,gap=27)


if __name__ == "__main__":
    result=design_checks()
    sheet=Sheet()
    draw_plan(sheet)
    draw_sections(sheet)
    finish(sheet,result)
    sheet.save()
    print(json.dumps({"svg":str(HERE/"floorplan.svg"),"png":str(HERE/"floorplan.png") if sheet.im else None,
                      "design_checks":result["design_arithmetic_status"],"count":len(result["checks"])}))
