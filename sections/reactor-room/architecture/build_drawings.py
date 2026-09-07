"""Original 2D CAD / A2 schematic drawing set. No 3D assets are opened."""
from pathlib import Path
import sys,math,json,html
from contextlib import contextmanager
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.deps'))
import ezdxf
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from pypdf import PdfReader
OUT=ROOT/'output'
OUT.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('Draft','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('DraftBold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Mono','C:/Windows/Fonts/consola.ttf'))
INK='#233136'; GRAY='#6e7a7d'; LIGHT='#d9e0e1'; WALL='#899799'
CYAN='#279cad'; PALE='#e6f5f7'; GOLD='#ab732c'; CREAM='#fcf5e8'; PAPER='#ffffff'
P=594; H=420
SHELL=[(-6,10.8),(6,10.8),(10.8,6),(10.8,-6),(6,-10.8),(-6,-10.8),(-10.8,-6),(-10.8,6)]
CORE=(12.46,2.0,18.71,5.2)
ROOM=(11.16,-4.4,14.76,2.0)
# The reusable stair/room module uses its P01 local coordinates. P02 translates
# every PLAN entity +1.20 m north; sections retain their own declared axes.
NORTH_SHIFT=1.20
CORE_WORLD=(CORE[0],CORE[1]+NORTH_SHIFT,CORE[2],CORE[3]+NORTH_SHIFT)
ROOM_WORLD=(ROOM[0],ROOM[1]+NORTH_SHIFT,ROOM[2],ROOM[3]+NORTH_SHIFT)
R=2.5/14; G=.25
STATIONS=[
('01','FUEL RECEIVING',-4.4,8.5,2.4,2.4,'cabinet'),
('02','NEW FUEL RACK',4.4,8.5,2.4,1.8,'rack'),
('03','BANK / REACTIVITY',0,7.6,1.8,1.8,'console'),
('04','WASTE TRANSFER',7.2,7.8,2.4,2.4,'tank'),
('05','CONTAINMENT VENT',9.4,5.7,1.2,1.2,'valve'),
('06','TURBINE / THROTTLE',7.5,-3,2.1,4.2,'machine'),
('07','GRID BREAKERS',9,.8,1.2,3,'cabinet'),
('08','GRID DEMAND',7.2,4.5,1.8,1.2,'console'),
('09','CONTAINMENT SENSOR',9,-4.5,.48,.48,'sensor'),
('10','COOLANT PUMP',-4.8,-7.8,2.4,2.4,'machine'),
('11','COOLANT VALVES',-1.2,-8.4,2.4,1.8,'valve'),
('12','EMERGENCY COOLING',3,-7.8,3,2.4,'twin'),
('13','BACKUP GENERATOR',-8.4,-4.2,2.4,2.4,'cabinet'),
('14','RESERVE POWER',-9,1.2,1.5,3,'cabinet'),
('15','REPAIR / SPARES',-7.8,5.4,1.8,1.8,'console')]
PDF=OUT/'reactor_compact_stair_architectural_set.pdf'
C=canvas.Canvas(str(PDF),pagesize=(P*mm,H*mm))
C.setTitle('Critical Shift - Reactor / Centered East Control - P02 Architectural Set')
C.setAuthor('Critical Shift / Environment Design')
DOC=ezdxf.new('R2010',setup=True)
DOC.units=4
for name,color,lw in [('A-WALL',8,50),('A-OUTLINE',7,25),('A-EQUIP',3,18),('A-GLAZ',4,18),('A-DIMS',8,13),('A-ANNO',7,18),('A-ROUTE',30,25),('A-HIDDEN',8,13),('A-DOOR',7,25)]:
    DOC.layers.new(name,dxfattribs={'color':color,'lineweight':lw})
DOC.layers.get('A-HIDDEN').dxf.linetype='DASHED'
SVG=[]; SHEETS=[]; TEXT_BOUNDS=[]; VIEWS=[]; DRAWING_POINTS=[]

def rgb(c):
    return tuple(int(c[i:i+2],16)/255 for i in (1,3,5))
def p_line(a,b,color=INK,lw=.2,dash=None):
    C.setStrokeColorRGB(*rgb(color));C.setLineWidth(lw*mm)
    C.setDash([d*mm for d in dash] if dash else [])
    C.line(a[0]*mm,a[1]*mm,b[0]*mm,b[1]*mm)
    d=f' stroke-dasharray="{" ".join(map(str,dash))}"' if dash else ''
    SVG.append(f'<line x1="{a[0]:.4f}" y1="{H-a[1]:.4f}" x2="{b[0]:.4f}" y2="{H-b[1]:.4f}" stroke="{color}" stroke-width="{lw}"{d}/>')
def p_poly(points,fill=None,color=INK,lw=.2,dash=None,closed=True):
    path=C.beginPath();path.moveTo(points[0][0]*mm,points[0][1]*mm)
    for x,y in points[1:]:path.lineTo(x*mm,y*mm)
    if closed:path.close()
    C.setLineWidth(lw*mm);C.setStrokeColorRGB(*rgb(color))
    if fill:C.setFillColorRGB(*rgb(fill))
    C.setDash([d*mm for d in dash] if dash else [])
    C.drawPath(path,stroke=1,fill=int(fill is not None))
    d=f' stroke-dasharray="{" ".join(map(str,dash))}"' if dash else ''
    tag='polygon' if closed else 'polyline'
    SVG.append(f'<{tag} points="{" ".join(f"{x:.4f},{H-y:.4f}" for x,y in points)}" fill="{fill or "none"}" stroke="{color}" stroke-width="{lw}"{d}/>')
def p_rect(x,y,w,h,**kw):p_poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],**kw)
def p_text(s,x,y,size=2.5,bold=False,color=INK,align='left',angle=0,font=None):
    f=font or ('DraftBold' if bold else 'Draft')
    C.saveState();C.translate(x*mm,y*mm);C.rotate(angle)
    C.setFont(f,size*mm);C.setFillColorRGB(*rgb(color))
    {'left':C.drawString,'center':C.drawCentredString,'right':C.drawRightString}[align](0,0,s)
    C.restoreState()
    anchor={'left':'start','center':'middle','right':'end'}[align]
    SVG.append(f'<text x="{x:.4f}" y="{H-y:.4f}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="{color}" text-anchor="{anchor}" transform="rotate({-angle} {x} {H-y})">{html.escape(s)}</text>')
    width=pdfmetrics.stringWidth(s,f,size*mm)/mm
    if angle==0:
        xmin=x-{'left':0,'center':width/2,'right':width}[align]
        TEXT_BOUNDS.append((SHEETS[-1]['id'] if SHEETS else '',s,xmin,y-size*.2,xmin+width,y+size))
def p_circle(x,y,r,color=INK,lw=.2,fill=None):
    C.setStrokeColorRGB(*rgb(color));C.setLineWidth(lw*mm);C.setDash([])
    if fill:C.setFillColorRGB(*rgb(fill))
    C.circle(x*mm,y*mm,r*mm,stroke=1,fill=int(bool(fill)))
    SVG.append(f'<circle cx="{x}" cy="{H-y}" r="{r}" stroke="{color}" stroke-width="{lw}" fill="{fill or "none"}"/>')

class View:
    def __init__(self,name,scale,origin,cad=True):
        self.name=name;self.scale=scale;self.k=1000/scale;self.ox,self.oy=origin
        self.dx=0.;self.dy=0.
        self.block=DOC.blocks.new(name) if cad else None
        if cad:
            n=len(VIEWS);DOC.modelspace().add_blockref(name,(n%3*60000,n//3*60000))
            VIEWS.append({'name':name,'scale':scale,'insert_mm':[n%3*60000,n//3*60000]})
    def world(self,p):return p[0]+self.dx,p[1]+self.dy
    @contextmanager
    def translated(self,x=0.,y=0.):
        previous=self.dx,self.dy
        self.dx+=x;self.dy+=y
        try:yield self
        finally:self.dx,self.dy=previous
    def q(self,p):
        x,y=self.world(p)
        q=self.ox+x*self.k,self.oy+y*self.k
        DRAWING_POINTS.append((self.name,*q))
        return q
    def attrs(self,layer,dash=None):
        a={'layer':layer}
        if dash:
            name='DASH_'+str(self.scale).replace('.','_')+'_'+'_'.join(str(d) for d in dash)
            if name not in DOC.linetypes:
                seq=[d*self.scale*(1 if i%2==0 else -1) for i,d in enumerate(dash)]
                DOC.linetypes.new(name,dxfattribs={'pattern':[sum(abs(d) for d in seq),*seq]})
            a['linetype']=name
        return a
    def line(self,a,b,color=INK,lw=.2,dash=None,layer='A-OUTLINE'):
        p_line(self.q(a),self.q(b),color,lw,dash)
        if self.block is not None:self.block.add_line(tuple(c*1000 for c in self.world(a)),tuple(c*1000 for c in self.world(b)),dxfattribs=self.attrs(layer,dash))
    def poly(self,pts,fill=None,color=INK,lw=.2,dash=None,layer='A-OUTLINE',closed=True):
        p_poly([self.q(p) for p in pts],fill,color,lw,dash,closed)
        if self.block is not None:self.block.add_lwpolyline([tuple(c*1000 for c in self.world(p)) for p in pts],close=closed,dxfattribs=self.attrs(layer,dash))
    def rect(self,x,y,w,h,**kw):self.poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],**kw)
    def circle(self,x,y,r,color=INK,lw=.2,fill=None,layer='A-EQUIP'):
        xx,yy=self.q((x,y));p_circle(xx,yy,r*self.k,color,lw,fill)
        if self.block is not None:self.block.add_circle(tuple(c*1000 for c in self.world((x,y))),r*1000,dxfattribs={'layer':layer})
    def text(self,s,x,y,size=2.5,bold=False,color=INK,align='left',angle=0):
        xx,yy=self.q((x,y));p_text(s,xx,yy,size,bold,color,align,angle)
        if self.block is not None:
            e=self.block.add_text(s,dxfattribs={'height':size*self.scale,'rotation':angle,'layer':'A-ANNO'})
            from ezdxf.enums import TextEntityAlignment
            e.set_placement(tuple(c*1000 for c in self.world((x,y))),align={'left':TextEntityAlignment.LEFT,'center':TextEntityAlignment.CENTER,'right':TextEntityAlignment.RIGHT}[align])
    def arrow(self,a,b,color=GOLD,lw=.35):
        self.line(a,b,color,lw,layer='A-ROUTE')
        dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy);ux,uy=dx/l,dy/l
        t=2.4/self.k;w=.8/self.k
        self.poly([b,(b[0]-ux*t-uy*w,b[1]-uy*t+ux*w),(b[0]-ux*t+uy*w,b[1]-uy*t-ux*w)],color,color,.1,layer='A-ROUTE')
    def tag(self,s,x,y):
        self.circle(x,y,2.8/self.k,CYAN,.25,PAPER)
        self.text(s,x,y-.85/self.k,2.2,True,CYAN,'center')
    def dimh(self,x1,x2,y,base,text=None):
        for x in (x1,x2):
            self.line((x,base),(x,y+.13),GRAY,.13,layer='A-DIMS')
            t=.10*self.scale/100
            self.line((x-t,y-t),(x+t,y+t),INK,.2,layer='A-DIMS')
        self.line((x1,y),(x2,y),GRAY,.13,layer='A-DIMS')
        self.text(text or f'{(x2-x1)*1000:,.0f}'.replace(',',' '),(x1+x2)/2,y+1.2/self.k,2.5,False,INK,'center')
    def dimv(self,y1,y2,x,base,text=None):
        for y in (y1,y2):
            self.line((base,y),(x+.13,y),GRAY,.13,layer='A-DIMS')
            t=.10*self.scale/100
            self.line((x-t,y-t),(x+t,y+t),INK,.2,layer='A-DIMS')
        self.line((x,y1),(x,y2),GRAY,.13,layer='A-DIMS')
        self.text(text or f'{(y2-y1)*1000:,.0f}'.replace(',',' '),x-1.2/self.k,(y1+y2)/2,2.5,False,INK,'center',90)
    def dimalign(self,a,b,text):
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);ux,uy=dx/length,dy/length
        self.line(a,b,GRAY,.13,layer='A-DIMS')
        for x,y in (a,b):self.line((x-uy*.1,y+ux*.1),(x+uy*.1,y-ux*.1),INK,.2,layer='A-DIMS')
        self.text(text,(a[0]+b[0])/2-uy*.15,(a[1]+b[1])/2+ux*.15,2.2,align='center',angle=math.degrees(math.atan2(dy,dx)))
    def level(self,z,x,txt):
        self.line((x,z),(x+.7,z),CYAN,.22)
        self.poly([(x,z),(x+.12,z+.12),(x+.24,z)],PAPER,CYAN,.2)
        self.text(txt,x+.28,z+.10,2.35,color=CYAN)
    def door(self,hinge,closed,opened):
        hx,hy=hinge;cx,cy=closed;ox,oy=opened
        self.line(hinge,opened,INK,.35,layer='A-DOOR' if 'A-DOOR' in DOC.layers else 'A-OUTLINE')
        a0=math.atan2(cy-hy,cx-hx);a1=math.atan2(oy-hy,ox-hx)
        delta=(a1-a0+math.pi)%(2*math.pi)-math.pi
        rad=math.hypot(cx-hx,cy-hy)
        self.poly([(hx+rad*math.cos(a0+delta*i/24),hy+rad*math.sin(a0+delta*i/24)) for i in range(25)],color=GRAY,lw=.13,closed=False)
        self.line(hinge,closed,GRAY,.13,dash=[1,1],layer='A-HIDDEN')

def title(id,name,scale):
    global SVG
    SVG=[];SHEETS.append({'id':id,'title':name,'scale':scale})
    p_rect(10,10,574,400,color=INK,lw=.45)
    p_line((10,40),(584,40),INK,.45)
    p_line((10,375),(584,375),INK,.35)
    p_text('CRITICAL SHIFT',20,395,6,True)
    p_text('REACTOR / CENTERED EAST CONTROL ROOM',20,383,3.3,color=GRAY)
    p_text(id,574,389,8,True,align='right')
    p_text(name,574,380,3.0,align='right')
    for x in (300,418,514):p_line((x,10),(x,40),INK,.2)
    p_text('SCHEMATIC DESIGN / GAME ENVIRONMENT',20,29,3,True)
    p_text('Dimensions: mm   |   Levels: m relative to hall FFL 0.000',20,21,2.6)
    p_text('A2 / 594 x 420 mm / print at 100% for stated scales',20,14,2.35,color=GRAY)
    p_text('DRAWING',309,32,2.2,color=GRAY)
    p_text(name,309,23,2.8,True)
    p_text('SCALE',427,32,2.2,color=GRAY)
    p_text(scale,427,23,2.8,True)
    p_text('REV  P02',524,30,3.0,True)
    p_text('07 SEP 2026',524,21,2.5)
    p_text(f'{len(SHEETS):02d} / 05',524,14,2.35,color=GRAY)

def finish():
    id=SHEETS[-1]['id']
    (OUT/(id+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="594mm" height="420mm" viewBox="0 0 594 420"><rect width="594" height="420" fill="white"/>'+'\n'.join(SVG)+'</svg>',encoding='utf-8')
    C.showPage()

def scale_bar(x,y,scale,length=5):
    w=length*1000/scale
    for i in range(5):p_rect(x+i*w/5,y,w/5,1.7,fill=INK if i%2==0 else PAPER,lw=.15)
    for i,t in enumerate((0,length/2,length)):p_text(f'{t:g}',x+i*w/2,y-3,2.2,align='center')
    p_text('m',x+w+4,y-3,2.2)
    p_text(f'1:{scale}',x,y+4,2.4,True)

def wall(v,a,b,th=.36):
    dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy);nx,ny=-dy/l,dx/l
    v.poly([a,b,(b[0]+nx*th,b[1]+ny*th),(a[0]+nx*th,a[1]+ny*th)],WALL,INK,.35,layer='A-WALL')
def hall(v,doors=True):
    openings={0:('FUEL',6,5),2:('CONTROL',2.4,4),3:('COOLING',math.sqrt(4.8**2*2)/2,5),6:('MAIN',6,6)}
    for i,a in enumerate(SHELL):
        b=SHELL[(i+1)%8];dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy);u=(dx/l,dy/l)
        if doors and i in openings:
            name,at,w=openings[i];p=(a[0]+u[0]*(at-w/2),a[1]+u[1]*(at-w/2));q=(a[0]+u[0]*(at+w/2),a[1]+u[1]*(at+w/2))
            wall(v,a,p);wall(v,q,b)
            out=(-u[1],u[0])
            v.line(p,q,GRAY,.13,dash=[2,1],layer='A-HIDDEN')
            for t,s in ((p,-1),(q,1)):
                v.line((t[0]+out[0]*.48,t[1]+out[1]*.48),(t[0]+out[0]*.48+u[0]*s*w/2,t[1]+out[1]*.48+u[1]*s*w/2),GRAY,.4)
        else:wall(v,a,b)
def pool(v,labels=True):
    v.circle(0,0,5.2,CYAN,.25,PALE)
    v.circle(0,0,3.9,INK,.35,PAPER)
    v.circle(0,0,3.4,CYAN,.35,PALE)
    gate=math.asin(.70/3.84)
    pts=[(3.84*math.sin(gate+(2*math.pi-2*gate)*i/120),-3.84*math.cos(gate+(2*math.pi-2*gate)*i/120)) for i in range(121)]
    v.poly(pts,color=INK,lw=.25,closed=False)
    for i in range(18):
        a=gate+(2*math.pi-2*gate)*i/17
        v.circle(3.84*math.sin(a),-3.84*math.cos(a),.045,INK,.1,INK)
    for x,label in [(-1.4,'A'),(1.4,'B')]:
        v.circle(x,0,.725,GRAY,.15,None)
        v.line((x-.15,0),(x+.15,0),CYAN,.18);v.line((x,-.15),(x,.15),CYAN,.18)
        if labels:v.text(label,x,-.10,2.3,True,CYAN,'center')
    v.line((-.7,-3.775),(.7,-3.775),GOLD,.4)
    v.rect(-.9,-6,1.8,1.8,color=GOLD,lw=.25,dash=[1,1],layer='A-ROUTE')
    v.arrow((0,-5.9),(0,-4.05))
    for x in (-.99,.99):v.rect(x-.14,-3.8,.28,.28,fill=GOLD,color=GOLD)
    if labels:
        v.text('REACTOR POOL',0,1.7,3.0,True,align='center')
        v.text('WATER -0.450',0,-1.5,2.45,color=CYAN,align='center')
        v.text('SHAFT -6.500',0,-1.9,2.45,color=CYAN,align='center')
def plant(v):
    for code,name,x,y,w,d,kind in STATIONS:
        if kind=='tank':
            v.circle(x,y,min(w,d)/2,GRAY,.18,'#f0f2f2')
        else:
            v.rect(x-w/2,y-d/2,w,d,fill='#f0f2f2',color=GRAY,lw=.18,layer='A-EQUIP')
        if kind in ('tank','twin'):
            for xx in ([x] if kind=='tank' else [x-w*.25,x+w*.25]):
                v.circle(xx,y,min(w,d)*(.43 if kind=='tank' else .26),INK,.2)
        elif kind=='valve':
            v.circle(x,y,.32,INK,.2)
            v.line((x-.32,y),(x+.32,y),INK,.2)
        elif kind=='rack':
            for k in (-.25,0,.25):v.line((x-w*.42,y+k*d),(x+w*.42,y+k*d),INK,.16)
        elif kind=='machine':
            v.rect(x-w*.35,y-d*.4,w*.7,d*.8,color=INK,lw=.2)
            v.line((x,y-d*.42),(x,y+d*.42),GRAY,.12,dash=[1,1])
        elif kind=='console':
            v.line((x-w*.45,y),(x+w*.45,y),INK,.16)
        if code=='09':
            v.tag(code,x+1.0,y-.3);v.line((x+.24,y),(x+.8,y-.3),GRAY,.15)
        else:v.tag(code,x,y)
    v.rect(-5.025,-5.225,1.25,.85,color=GOLD,lw=.2)
    v.text('CADDY',-4.4,-5.02,1.9,color=GOLD,align='center')
    v.circle(3.7,-4.8,.19,GOLD,.2)
def core(v,level=0,detail=False,grounddoor=True,topdoor=False):
    x0,y0,x1,y1=CORE
    v.rect(x0,y0,x1-x0,y1-y0,fill=CREAM,color=INK,lw=.45,layer='A-WALL')
    v.rect(x0+.2,y0+.2,x1-x0-.4,y1-y0-.4,fill=PAPER,color=INK,lw=.25)
    wl=x0+.2;rs=wl+1.3;re=rs+3.25;er=re+1.3
    bands=[(2.2,3.5),(3.7,5.0)]
    index=min(3,int(level/2.5));active=index%2
    west_current=(level in (0,5,10))
    for is_west,xx in ((True,wl),(False,re)):
        current=(is_west==west_current)
        landing_z=level if current else (level-2.5 if level==10 else level+2.5)
        v.rect(xx,2.2,1.3,2.8,fill=CREAM if current else None,color=GRAY,lw=.18,dash=None if current or level==10 else [1.2,.7],layer='A-OUTLINE' if current else 'A-HIDDEN')
        if not detail:
            v.text(f'{landing_z:+.3f}',xx+.65,4.55 if is_west else 3.6,2.0,True,GOLD if current else GRAY,'center',90)
    for k,(lo,hi) in enumerate(bands):
        active_up=k==active and level<10
        whole_above=level==0 and k==1
        rev=k==1
        cutx=re-1.625 if rev else rs+1.625
        def hidden(xx):return whole_above or (active_up and (xx<cutx if rev else xx>cutx))
        for j in range(14):
            xx=rs+j*G
            v.line((xx,lo),(xx,hi),GRAY,.15,dash=[1,.7] if hidden(xx) else None,layer='A-HIDDEN' if hidden(xx) else 'A-OUTLINE')
        for yy in (lo+.025,hi-.025):
            if active_up:
                a,b=(re,rs) if rev else (rs,re)
                v.line((a,yy),(cutx,yy),INK,.3 if detail else .18)
                v.line((cutx,yy),(b,yy),GRAY,.18,dash=[1,.7],layer='A-HIDDEN')
            else:v.line((rs,yy),(re,yy),GRAY if whole_above else INK,.18,dash=[1,.7] if whole_above else None,layer='A-HIDDEN' if whole_above else 'A-OUTLINE')
        if active_up:
            # Paired diagonal break at the conventional +1.20 m plan cut.
            for shift in (-.055,.055):
                v.line((cutx-.11+shift,lo-.04),(cutx+.11+shift,hi+.04),INK,.28)
    v.rect(rs,3.5,3.25,.2,fill='#e7e9e9',color=GRAY,lw=.15)
    # UP flight at the tagged level; preceding flight reads down to its source.
    if level<10:
        lo,hi=bands[index%2];yy=(lo+hi)/2
        a,b=((rs+.2,yy),(rs+1.25,yy)) if index%2==0 else ((re-.2,yy),(re-1.25,yy))
        v.arrow(a,b)
        labelx=rs+.75 if detail else (rs+re)/2+.85*(1 if index%2==0 else -1)
        v.text(f'UP F{index+1}',labelx,yy+.25 if detail else yy+.17,2.0,True,GOLD,'center')
        if level>0:
            py=sum(bands[1-active])/2
            v.text(f'DN F{index}',(rs+re)/2,py+.17,1.95,color=GRAY,align='center')
        elif not detail:v.text('F2 ABOVE',(rs+re)/2,4.35,1.95,color=GRAY,align='center')
    else:
        v.arrow((rs+.12,4.35),(rs+1.15,4.35))
        v.text('DN F4',(rs+re)/2,4.55,2.1,True,GOLD,'center')
        v.text('F3 BELOW',(rs+re)/2,2.85,1.95,color=GRAY,align='center')
    if grounddoor:
        v.rect(x0-.01,3.0,.22,1.2,fill=PAPER,color=PAPER,lw=.05)
        v.door((x0,4.2),(x0,3.0),(x0-1.2,4.2))
    if topdoor:
        v.rect(12.71,1.99,1.2,.22,fill=PAPER,color=PAPER,lw=.05)
        v.door((13.91,2),(12.71,2),(13.91,.8))
    if detail:
        v.text('WEST LANDING',wl+.65,4.60,2.45,True,align='center',angle=90)
        v.text('EAST LANDING',re+.65,3.60,2.45,True,align='center',angle=90)
    return wl,rs,re,er
def control(v,furniture=True):
    v.rect(10.8,-4.6,4.16,6.8,fill=WALL,color=INK,lw=.4,layer='A-WALL')
    v.rect(11.16,-4.4,3.6,6.4,fill=PAPER,color=INK,lw=.22)
    # Observation opening, including the wall-depth reveal and shallow toe strip.
    v.rect(10.79,-3.9,.38,5.4,fill=PALE,color=CYAN,lw=.2)
    for x in (10.88,10.94):v.line((x,-3.9),(x,1.5),CYAN,.2,layer='A-GLAZ')
    v.rect(11.16,-3.9,.65,5.4,fill=PALE,color=CYAN,lw=.15)
    for y in (-2.1,-.3):v.line((11.16,y),(11.81,y),CYAN,.12)
    v.rect(12.71,1.99,1.2,.22,fill=PAPER,color=PAPER,lw=.05)
    v.door((13.91,2),(12.71,2),(13.91,.8))
    if furniture:
        for y in (-.6,-2.7):
            v.rect(12.46,y-.6,.7,1.2,fill='#e4eaeb',color=INK,lw=.2,layer='A-EQUIP')
            v.rect(12.55,y-.30,.27,.50,color=INK,lw=.15)
            v.rect(13.41,y-.30,.60,.60,color=GRAY,lw=.16)
            v.circle(13.71,y,.22,GRAY,.13)
        v.rect(14.60,-2.0,.16,1.4,color=GRAY,lw=.15)
    v.text('CONTROL',11.95,-1.10,2.8,True,align='center',angle=90)
    v.text('FFL +10.000',14.35,-3.8,2.35,color=CYAN,align='center',angle=90)
def note_block(x,y,title_,lines,width=170):
    p_text(title_,x,y,3.2,True)
    p_line((x,y-3),(x+width,y-3),INK,.25)
    yy=y-9
    for line_ in lines:
        p_text(line_,x,yy,2.6);yy-=5.1
    return yy
def north(x,y):
    p_line((x,y-15),(x,y+3),INK,.4)
    p_poly([(x,y+3),(x-2,y-3),(x,y-1),(x+2,y-3)],INK,INK,.2)
    p_text('N',x,y+6,3.6,True,align='center')
def cut(v,a,b,letter,sheet):
    v.line(a,b,CYAN,.18,dash=[5,1,1,1],layer='A-HIDDEN')
    for pt in (a,b):
        v.circle(*pt,2.8/v.k,CYAN,.3,PAPER)
        v.text(letter,pt[0],pt[1]-.85/v.k,2.45,True,CYAN,'center')
        v.text(sheet,pt[0],pt[1]-6.2/v.k,2.0,color=CYAN,align='center')

# A100 ----------------------------------------------------------------------
title('A100','GENERAL ARRANGEMENT','1:100')
v=View('A100_GROUND_0',100,(155,197))
for x,label in [(-10.8,'A'),(0,'B'),(10.8,'C')]:
    v.line((x,-12),(x,11.5),LIGHT,.12,dash=[4,1,1,1],layer='A-HIDDEN')
    v.circle(x,11.5,.28,GRAY,.15,PAPER);v.text(label,x,11.41,2.2,align='center')
hall(v);pool(v);plant(v)
v.rect(11.16,1.6,1.3,4,fill=CREAM,color=GRAY,lw=.2)
v.rect(11.16,1.4,1.5,.2,fill=WALL,color=INK,lw=.3,layer='A-WALL')
v.rect(11.16,5.6,1.3,.2,fill=WALL,color=INK,lw=.3,layer='A-WALL')
v.rect(12.46,1.6,.2,1.6,fill=WALL,color=INK,lw=.3,layer='A-WALL')
with v.translated(y=NORTH_SHIFT):
    v.rect(10.8,-4.6,4.16,6.8,color=GRAY,lw=.15,dash=[2,1],layer='A-HIDDEN')
    core(v,0,grounddoor=True)
    v.text('ENCLOSED STAIR',15.585,5.72,2.65,True,GOLD,'center')
    v.text('20.00 m2 GROSS',15.585,1.4,2.45,color=GOLD,align='center')
    v.text('CONTROL ABOVE',12.9,-1.5,2.55,color=GRAY,align='center')
    v.text('+10.000',12.9,-1.9,2.4,color=CYAN,align='center')
v.arrow((10.2,3.6),(11.8,3.6))
v.arrow((11.8,3.6),(11.8,4.8))
v.arrow((11.8,4.8),(12.9,4.8))
v.text('HALL FFL 0.000',-6.5,-1.6,2.6,True,align='center')
v.text('420.48 m2',-6.5,-2.0,2.45,align='center')
v.dimh(-10.8,10.8,12.9,10.8)
v.dimh(-6,6,12.0,10.8)
v.dimv(-10.8,10.8,-13.7,-10.8)
with v.translated(y=NORTH_SHIFT):
    v.dimh(12.46,18.71,6.7,5.2)
    v.dimv(2,5.2,19.8,18.71)
v.dimh(-3.4,3.4,-11.8,-3.4,'POOL OPENING 6 800')
v.text('MAIN / 6 000 CLEAR',-12.7,-4.0,2.45,angle=90)
v.text('FUEL / 5 000 CLEAR',0,10.95,2.35,color=GRAY,align='center')
v.text('COOLING / 5 000',9.1,-9.2,2.35,color=GRAY,angle=45)
v.text('EAST ROUTE 4 000',9.95,3.5,2.15,color=GRAY,angle=90)
# The main circulation ring itself remains the bypass; no exposed stair cuts it.
v.arrow((-5.8,1.0),(-5.8,3.4),CYAN,.2)
v.arrow((-.6,6.0),(2.5,6.0),CYAN,.2)
gap_end=(6.45,-.9);gap_radius=math.hypot(*gap_end)
v.dimalign(tuple(c*5.2/gap_radius for c in gap_end),gap_end,'1 312*')
v.dimv(8.5,10.8,1.7,.9,'2 300')
v.dimh(-3.2,-.9,9.1,8.5,'2 300')
v.dimh(.9,3.2,9.1,8.5,'2 300')
cut(v,(-11.7,0),(15.0,0),'A','A201')
north(29,354);scale_bar(47,57,100,10)
p_text('01 / GROUND FLOOR',47,352,3.5,True)
p_text('Control and observation window centered on the east wall.',47,344,2.8,color=GRAY)
p_line((391,53),(391,363),LIGHT,.25)
p_text('EQUIPMENT / RETAINED GAMEPLAY SECTORS',405,352,3.2,True)
p_line((405,347),(574,347),INK,.25)
p_text('ID',405,342,2.3,True);p_text('STATION',418,342,2.3,True);p_text('FOOTPRINT / m',574,342,2.3,True,align='right')
for i,(code,name,x,y,w,d,kind) in enumerate(STATIONS):
    yy=334-i*7
    p_text(code,405,yy,2.55,True,CYAN);p_text(name,418,yy,2.55)
    p_text(f'{w:.2f} x {d:.2f}',574,yy,2.4,align='right')
    p_line((405,yy-2.5),(574,yy-2.5),LIGHT,.12)
note_block(405,214,'LAYOUT INTENT',[
'01  Four short flights stack in one 20.00 m2 core.',
'02  Control and window align with the reactor axis.',
'03  Top landing opens into the Control room.',
'04  North-hinged D01 clears the vestibule approach.',
'05  Two banks and the pool retain their spec scale.',
'06  North workstations flank a clear entry apron.'])
note_block(405,161,'CIRCULATION / KEY',[
'Pool service ring: 1 300 radial width.',
'Maintain at least 1 200 usable circulation.',
'* Turbine-to-ring minimum: 1 312 measured.',
'South rail gate: 1 400 clear; approach: 1 800.',
'Grey dashed: upper Control room outline.',
'Amber: compact stair / access route.',
'Cyan: pool, glazing and observation zones.'])
note_block(405,106,'COORDINATES / SOURCE',[
'Plan north is up. Dimensions are millimetres.',
'Hall datum 0.000; Control datum +10.000.',
'Current reactor scenery spec governs the envelope.',
'This is a new 2D proposal; no old 3D assets used.',
'Style direction retained: brighter second concept.'])
finish()

# A101 ----------------------------------------------------------------------
title('A101','CONTROL + STACKED STAIR PLANS','1:50')
p_text('02 / CONTROL FLOOR +10.000',27,355,3.5,True)
p_text('P02: room and glazing centerline is exactly Y = 0.000.',27,346,2.8,color=CYAN)
u=View('A101_CONTROL_10',50,(-185,181-NORTH_SHIFT*20))
u.dy=NORTH_SHIFT
control(u);core(u,10,grounddoor=False,topdoor=True)
u.arrow((13.31,4.3),(13.31,1.4))
u.arrow((13.2,1.1),(11.95,1.1))
u.dimh(11.16,14.76,-5.25,-4.4,'3 600 CLEAR')
u.dimv(-4.4,2,10.0,11.16,'6 400 CLEAR')
u.dimh(12.46,18.71,6.35,5.2)
u.dimv(2,5.2,19.4,18.71)
u.dimh(10.8,11.16,-5.85,-4.6,'360 WALL')
u.dimh(11.16,11.81,-3.65,-3.9,'650')
for left,right in [(10.4,11.85),(12.08,15.3)]:
    u.line((left,-1.2),(right,-1.2),CYAN,.15,dash=[4,1,1,1],layer='A-HIDDEN')
u.text('W01 / 5 400',10.45,-1.2,2.5,color=CYAN,align='center',angle=90)
u.text('23.04 m2 CLEAR',12.0,-2.5,2.3,color=GRAY,align='center',angle=90)
u.text('D02',13.31,2.35,2.3,True,color=GOLD,align='center')
# Schematic view arrows leave the actual window plane.
for y in (-3.25,-1.2,.9):
    u.arrow((11.75,y),(10.3,y-.5),CYAN,.2)
p_text('V01 / WINDOW + VIEW STRIP',215,194,2.8,True,CYAN)
p_text('5 400 x 2 600 main pane',215,187,2.5)
p_text('650 interior glazed floor strip',215,181,2.5)
p_text('See V01 detail on A202.',215,175,2.5)
p_text('Y = 0 / HALL + REACTOR AXIS',215,161,2.4,True,CYAN)
u.tag('V',11.48,-3.0)
cut(u,(12.15,2.85),(19.10,2.85),'B','A201')
cut(u,(13.31,0),(13.31,5.7),'C','A202')
p_text('ROOM USE',231,142,2.8,True)
for i,s in enumerate(['Two seated operator positions.','Clear 1 300 walk-up zone.','Desks face the hall glazing.','Plant mimic on rear wall.','No separate gallery corridor.']):
    p_text(s,231,135-i*5.5,2.5)
scale_bar(33,57,50,5);north(258,327)
p_line((284,54),(284,365),LIGHT,.25)
for j,level in enumerate((0,2.5,5,7.5)):
    px=310+(j%2)*138;py=254-(j//2)*111
    p_text(f'0{j+3} / LEVEL {level:+.3f}',px,py+73,2.9,True)
    w=View(f'A101_STAIR_LEVEL_{j}',50,(px-12.46*20,py-(2+NORTH_SHIFT)*20))
    w.dy=NORTH_SHIFT
    core(w,level,grounddoor=(level==0))
    p_text(f'F{j+1}: 14R @ 178.571 / 13G @ 250',px,py-7,2.35)
    p_text(f'UP TO {level+2.5:+.3f}'+(f' / DN TO {level-2.5:+.3f}' if level else ' / D01 ENTRY'),px,py-13,2.35,True,GOLD)
note_block(296,116,'STACKING LOGIC',[
'F1 east / F2 west / F3 east / F4 west.',
'Plan cut: 1 200 above each tagged level; cut flight shown broken.',
'Dashed stair is above cut; tinted slab is the current landing.',
'Top exit returns to the west landing at +10.000.',
'56 risers total; no exposed hall stair or overlook.',
'Landing doors swing out of the stair clear rectangles.'],278)
finish()

# A201 ----------------------------------------------------------------------
title('A201','SECTIONS + SIGHTLINES','1:100 / 1:50')
p_text('A-A / REACTOR + CONTROL',28,352,3.5,True)
s=View('A201_HALL_SECTION',100,(158,148))
# floor slab, wall cuts and deep shaft
s.rect(-11.16,-.32,7.76,.32,fill=WALL,color=INK,lw=.35,layer='A-WALL')
s.rect(3.4,-.32,11.56,.32,fill=WALL,color=INK,lw=.35,layer='A-WALL')
s.rect(-11.16,0,.36,16,fill=WALL,color=INK,lw=.4,layer='A-WALL')
s.rect(10.8,0,.36,8,fill=WALL,color=INK,lw=.4,layer='A-WALL')
s.rect(10.8,12.9,.36,3.1,fill=WALL,color=INK,lw=.4,layer='A-WALL')
s.rect(-11.16,16,22.32,.25,fill=WALL,color=INK,lw=.35)
for x in (-3.7,3.4):s.rect(x,-6.7,.3,6.7,fill=WALL,color=INK,lw=.35)
s.rect(-3.7,-6.7,7.4,.2,fill=WALL,color=INK,lw=.35)
s.rect(-3.4,-6.5,6.8,6.05,fill=PALE,color=CYAN,lw=.15)
s.line((-3.4,-.45),(3.4,-.45),CYAN,.4,layer='A-GLAZ')
s.line((-3.9,0),(-3.9,1.1),INK,.25);s.line((3.9,0),(3.9,1.1),INK,.25)
s.rect(-8.5,13.92,17,.56,fill='#b8c2c4',color=INK,lw=.25)
for x,label in [(-1.4,'A'),(1.4,'B')]:
    s.rect(x-.9,9.8,1.8,2.6,fill='#dce8e9',color=INK,lw=.25)
    s.rect(x-.725,7.825,1.45,1.55,fill='#dce8e9',color=INK,lw=.25)
    s.rect(x-.23,-4.5,.46,12.35,fill='#e9eeef',color=GRAY,lw=.2)
    s.line((x,12.4),(x,13.92),INK,.35)
    s.text(label,x,10.75,3.5,True,align='center')
# compact control section and observation detail
s.rect(11.81,9.8,3.15,.2,fill=WALL,color=INK,lw=.3)
s.rect(11.16,13.4,3.8,.2,fill=WALL,color=INK,lw=.3)
s.rect(14.76,10,.2,3.4,fill=WALL,color=INK,lw=.3)
s.line((10.9,8),(10.9,12.9),CYAN,.35,layer='A-GLAZ')
s.line((10.88,10.0),(11.81,10.0),CYAN,.35,layer='A-GLAZ')
s.rect(10.84,10.20,.20,.10,fill=INK,color=INK,lw=.2)
s.rect(10.84,7.92,.20,.08,fill=INK,color=INK,lw=.2)
s.rect(12.46,10.0,.7,1.05,color=INK,lw=.2)
s.circle(13.71,10.5,.25,GRAY,.18)
eye=(11.5,11.7)
s.circle(*eye,.09,GOLD,.2,GOLD)
for target in [(-9.8,.1),(0,-.45),(9.2,1.25)]:
    s.line(eye,target,CYAN,.18,dash=[2,1])
s.line((11.5,10),(11.5,11.47),GRAY,.35)
s.circle(11.5,11.57,.13,GRAY,.2)
s.text('V01 / A202',12.0,8.5,2.55,True,CYAN)
s.line((11.1,9.95),(12.0,8.9),CYAN,.18)
s.text('CONTROL',13.35,12.75,2.8,True,align='center')
s.level(0,-12.9,'0.000')
s.line((-8.8,-.45),(-7.2,-.45),CYAN,.18)
s.line((-7.2,-.45),(-6.8,-1.1),CYAN,.18)
s.text('-0.450 WATER',-6.7,-1.2,2.35,color=CYAN)
s.level(-6.5,-12.9,'-6.500')
s.level(16,-12.9,'+16.000')
s.level(14.2,-7.7,'+14.200')
s.level(10,15.2,'+10.000')
s.dimv(0,16,-13.8,-11.16,'16 000 CLEAR')
s.dimv(-6.5,-.45,5.0,3.7,'6 050 BELOW WATER')
s.dimv(9.8,12.4,4.8,2.3,'2 600 FIXED')
s.dimh(-1.4,1.4,13.0,12.4,'2 800 AXES')
s.dimh(-3.4,3.4,-7.7,-6.7,'6 800 APERTURE')
p_text('SCHEMATIC SIGHTLINES / PLAN OCCLUSION NOT TESTED',29,64,2.7,True,CYAN)
p_text('Targets: far floor / pool water / near-wall work zone. Glazing detail V01 on A202.',29,57,2.5)
s.text('FAR FLOOR',-9.1,.75,2.2,color=CYAN)
s.text('POOL',-.4,-1.1,2.2,color=CYAN)
s.text('NEAR WORK',8.8,2.1,2.2,color=CYAN,align='right')
scale_bar(292,76,100,5)
p_line((359,53),(359,364),LIGHT,.25)
p_text('B-B / LONGITUDINAL STAIR SECTION',375,352,3.5,True)
t=View('A201_STAIR_SECTION',50,(387-12.46*20,82))
x0,_,x1,_=CORE;wl=x0+.2;rs=wl+1.3;re=rs+3.25;er=re+1.3
t.rect(x0,-.2,x1-x0,.2,fill=WALL,color=INK,lw=.35)
t.rect(x0,0,.2,12.4,fill=WALL,color=INK,lw=.35)
t.rect(x1-.2,0,.2,12.4,fill=WALL,color=INK,lw=.35)
t.rect(x0,12.4,x1-x0,.2,fill=WALL,color=INK,lw=.35)
for z in (0,5,10):t.rect(wl,z-.2,1.3,.2,fill=WALL,color=INK,lw=.25)
for z in (2.5,7.5):t.rect(re,z-.2,1.3,.2,fill=WALL,color=INK,lw=.25)
for f in range(4):
    z0=f*2.5;rev=f%2==1
    pts=[(re if rev else rs,z0)]
    for n in range(14):
        xx=re-n*G if rev else rs+n*G
        pts.append((xx,z0+(n+1)*R))
        if n<13:pts.append((xx-G if rev else xx+G,z0+(n+1)*R))
    t.poly(pts,color=GRAY if rev else INK,lw=.22,dash=[1,1] if rev else None,closed=False)
    t.line((re if rev else rs,z0-.2),(rs if rev else re,z0+2.5-.2),GRAY,.18,dash=[1,1] if rev else None)
    t.text(f'F{f+1}',15.55,z0+1.55,2.45,True,GOLD,align='center')
for z in (0,2.5,5,7.5,10):t.level(z,19.25,f'{z:+.3f}')
t.dimv(0,10,21.0,18.71,'10 000 TOTAL RISE')
t.dimv(0,2.3,17.85,17.25,'2 300')
t.dimh(x0,x1,-.7,0,'6 250 GROSS')
t.text('F2 / F4 beyond: dashed',15.55,11.5,2.4,color=GRAY,align='center')
p_text('Nosing pitch: 35.54 deg',375,56,2.6)
p_text('Same-band flights repeat at 5.00 m vertical separation.',375,50,2.5)
finish()

# A202 ----------------------------------------------------------------------
title('A202','ENTRANCE + OBSERVATION DETAILS','1:50 / 1:10')
p_text('E01 / EAST WALL - VIEWED FROM HALL',28,355,3.5,True)
e=View('A202_EAST_ELEVATION',50,(148,75))
# Elevation horizontal axis is -Y: north is left when looking east.
e.rect(-6,0,12,13.5,fill='#f0f2f2',color=INK,lw=.3)
e.rect(-5.6,0,4,5,fill=CREAM,color=INK,lw=.35)
e.rect(-5.4,0,1.2,2.1,fill=PAPER,color=INK,lw=.3)
e.line((-4.28,.95),(-4.40,.95),INK,.3)
e.text('D01',-4.8,1.55,2.4,True,GOLD,'center')
e.text('STAIR',-3.6,2.65,2.5,True,GOLD,'center')
e.text('INNER DOOR AT NORTH END',-3.6,2.35,2.1,color=GRAY,align='center')
e.rect(-2.7,8,5.4,2.2,fill=PALE,color=CYAN,lw=.25,layer='A-GLAZ')
e.rect(-2.7,10.3,5.4,2.6,fill=PALE,color=CYAN,lw=.25,layer='A-GLAZ')
e.rect(-2.7,10.2,5.4,.10,fill=INK,color=INK,lw=.1)
for xx in (-.9,.9):e.line((xx,8),(xx,12.9),INK,.4)
e.text('CONTROL / W01',0,11.65,3,True,CYAN,'center')
e.text('LOWER VIEW PANE',0,8.9,2.4,color=CYAN,align='center')
e.line((0,0),(0,7.0),CYAN,.15,dash=[4,1,1,1],layer='A-HIDDEN')
e.text('HALL / REACTOR / WINDOW AXIS',.3,6.5,2.3,True,CYAN)
e.dimh(-6,-2.7,7.25,8,'3 300')
e.dimh(2.7,6,7.25,8,'3 300')
e.dimh(-5.6,-1.6,-.60,0,'OUTER ROUTE 4 000')
e.dimv(0,5,-6.50,-5.6,'5 000 OUTER OPENING')
e.dimh(-2.7,2.7,13.25,12.9,'5 400 W01 / CENTERED')
e.dimv(10.3,12.9,3.55,2.7,'2 600 W01')
e.level(0,4.65,'0.000')
e.level(10,4.65,'+10.000')
p_text('North',32,69,2.3,color=GRAY)
p_text('South',252,69,2.3,color=GRAY)
p_text('Existing route: 4 000 x 5 000. Inner D01: 1 200 x 2 100.',28,53,2.6)
p_text('Enclosure continues to the +16.000 hall roof above this view.',28,46,2.5,color=GRAY)
p_line((302,53),(302,364),LIGHT,.25)
p_text('C-C / WEST LANDING + CONTROL DOOR',318,355,3.2,True)
c=View('A202_WEST_LANDING_SECTION',50,(320-(-.25+NORTH_SHIFT)*20,70))
c.dx=NORTH_SHIFT
# Horizontal axis is Y, cut at X13.31 through the actual west landing.
c.rect(-.25,9.8,2.25,.2,fill=WALL,color=INK,lw=.3)
for z in (0,5,10):c.rect(2.2,z-.2,2.8,.2,fill=WALL,color=INK,lw=.3)
c.rect(5,0,.2,12.4,fill=WALL,color=INK,lw=.35)
c.rect(2,0,.2,10,fill=WALL,color=INK,lw=.35)
c.rect(2,12.1,.2,1.3,fill=WALL,color=INK,lw=.35)
c.rect(-.25,13.4,2.45,.2,fill=WALL,color=INK,lw=.3)
c.rect(2.2,12.4,3,.2,fill=WALL,color=INK,lw=.3)
c.line((2.0,10),(2.0,12.1),GOLD,.4)
c.text('D02',1.45,11.0,2.4,True,GOLD,'right')
c.text('CONTROL',.8,12.65,2.55,True,align='center')
c.text('WEST LANDING',3.6,10.55,2.4,True,align='center')
c.text('DOOR OPENS INTO CONTROL',2.3,11.7,2.05,color=GOLD,align='center')
c.arrow((2.0,10.35),(.8,10.35))
c.dimv(10,12.1,.2,2,'2 100 HEAD')
c.dimv(10,12.4,6.0,5.2,'2 400 CLEAR')
for z in (0,5,10):c.level(z,5.45,f'{z:+.3f}')
c.text('0 / 5 / 10 m LANDINGS',3.6,7.5,2.25,color=GRAY,align='center',angle=90)
c.dimh(2.2,5,-.8,0,'2 800 SLAB WIDTH')
p_text('D01 / ENTRY SECTION',463,355,3.0,True)
k=View('A202_ENTRY_SECTION',50,(468-10.8*20,244))
k.rect(10.8,-.2,3.16,.2,fill=WALL,color=INK,lw=.3)
k.rect(12.46,2.1,.2,2.9,fill=WALL,color=INK,lw=.3)
k.rect(10.8,5,1.86,.2,fill=WALL,color=INK,lw=.3)
k.line((12.46,0),(12.46,2.1),GOLD,.35)
k.rect(12.66,4.8,1.3,.2,fill=WALL,color=INK,lw=.3)
k.dimv(0,2.1,14.6,12.66,'2 100 D01')
k.dimv(0,5,10.25,10.8,'5 000 VESTIBULE')
k.dimh(11.16,12.46,-.65,0,'1 300 CLEAR')
k.text('HALL',10.3,.65,2.3,align='center',angle=90)
k.text('D01',12.1,1.0,2.2,True,GOLD,'right')
k.text('LANDING',13.3,.55,2.2,align='center')
k.text('+5.000 SLAB',13.3,5.35,2.0,color=GRAY,align='center')
p_text('D01 shown in elevation through entry axis Y4.800.',461,224,2.35)
p_text('Leaf swings into vestibule; see plan 07 / A301.',461,218,2.35)
p_text('V01 / OBSERVATION SECTION - 1:10',461,205,3.0,True,CYAN)
g=View('A202_V01_GLAZING',10,(468-10.8*100,66-9.8*100))
# Cropped enlarged section: exact frame and horizontal floor detail.
g.line((10.90,9.8),(10.90,10.2),CYAN,.4,layer='A-GLAZ')
g.line((10.90,10.3),(10.90,11.0),CYAN,.4,layer='A-GLAZ')
g.rect(10.84,10.2,.20,.10,fill=INK,color=INK,lw=.2)
g.line((10.88,10),(11.81,10),CYAN,.5,layer='A-GLAZ')
g.rect(11.81,9.8,.13,.2,fill=WALL,color=INK,lw=.3)
g.dimh(11.16,11.81,10.7,10,'650 INTERIOR STRIP')
g.dimh(10.88,11.16,9.7,10,'280 REVEAL')
g.text('+10.000',11.46,10.06,2.2,color=CYAN,align='center')
g.text('FRAME +10.200 / +10.300',10.85,11.08,2.2)
p_text('Main pane: +10.300 to +12.900.',461,51,2.4)
p_text('Lower pane: +8.000 to +10.200. Detail cropped.',461,45,2.4)
finish()

# A301 ----------------------------------------------------------------------
title('A301','STAIR DETAIL + SCHEDULES','1:25 / 1:20 / 1:5')
p_text('07 / ENCLOSED STAIR - ENLARGED',30,355,3.5,True)
d=View('A301_STAIR_DETAIL',25,(100-12.46*40,100-NORTH_SHIFT*40))
d.dy=NORTH_SHIFT
core(d,0,detail=True)
d.rect(11.16,1.8,1.3,2.6,color=GRAY,lw=.16,dash=[2,1])
d.rect(11.16,4.4,1.3,.2,fill=WALL,color=INK,lw=.25,layer='A-WALL')
d.poly([(11.16,1.8),(11.7,1.8),(11.76,1.87),(11.84,1.73),(11.90,1.8),(12.46,1.8)],color=INK,lw=.2,closed=False)
p_text('VESTIBULE CONTINUES SOUTH / SEE A100',34,165.5,2.4,color=GRAY)
d.dimh(12.46,18.71,6.20,5.2,'6 250 GROSS / NOMINAL')
for aa,bb in [(12.46,12.66),(12.66,13.96),(13.96,17.21),(17.21,18.51),(18.51,18.71)]:
    d.dimh(aa,bb,5.62,5.2)
d.dimv(2,5.2,19.30,18.71,'3 200 GROSS')
for aa,bb in [(2,2.2),(2.2,3.5),(3.5,3.7),(3.7,5),(5,5.2)]:
    d.dimv(aa,bb,18.95,18.71)
# Clear dimension between the INNER rail faces.
d.dimv(2.25,3.45,16.5,16.35,'1 200 CLEAR')
d.dimv(3.75,4.95,16.5,16.35,'1 200 CLEAR')
d.dimh(12.71,13.96,1.48,2.2,'1 250 CLEAR LANDING')
d.text('D01 / 1 200 CLEAR',11.1,3.6,2.6,True,GOLD,align='center',angle=90)
d.text('200 WELL',15.585,3.575,2.3,align='center')
p_text('08 / HANDRAIL CLEARANCE - 1:20',34,159,3.1,True)
rview=View('A301_RAIL_DETAIL',20,(60,75))
rview.rect(0,-.12,1.3,.12,fill=WALL,color=INK,lw=.3)
for x in (.025,1.275):
    rview.line((x,0),(x,1.1),INK,.45)
    rview.circle(x,1.1,.025,INK,.25,INK)
    rview.circle(x,.55,.016,INK,.2,INK)
rview.dimh(.05,1.25,.72,1.1,'1 200 BETWEEN RAILS')
rview.dimh(0,1.3,-.25,0,'1 300 TREAD BAND')
rview.dimv(0,1.1,1.48,1.3,'1 100 GUARD')
p_text('09 / RISE + GOING - 1:5',224,164,3.1,True)
rr=View('A301_RISER_DETAIL',5,(229,49))
prof=[(0,0),(0,R),(.25,R),(.25,2*R),(.5,2*R),(.5,3*R),(.75,3*R)]
rr.poly(prof,color=INK,lw=.5,closed=False)
rr.dimh(0,.25,-.015,R,'250')
rr.dimv(0,R,-.07,0,'178.571')
rr.text('NOSING LINE',.46,.10,2.4,color=GRAY,angle=35.54)
rr.line((0,R),(.5,3*R),GRAY,.15,dash=[2,1])
p_line((399,53),(399,364),LIGHT,.25)
yy=note_block(412,350,'STAIR SCHEDULE',[
'Core gross: 6 250 x 3 200 = 20.00 m2.',
'Flight band: 1 300 gross / 1 200 rail-clear.',
'Central well: 200 between flight edges.',
'End landings: 1 300 gross / 1 250 clear.',
'Outer enclosure: 200 nominal.',
'Per flight: 14 risers / 13 goings.',
'Riser: 10 000 / 56 = 178.571 mm.',
'Going: 250 mm; nosing pitch: 35.54 deg.',
'2R + G = 607.143 mm.',
'Lowest landing underside: +2.300.',
'Main floor to Control: +10.000 exactly.'],162)
yy=note_block(412,yy-8,'LEVEL / FLIGHT SCHEDULE',[
'F1  0.000 to +2.500 / eastbound.',
'F2  +2.500 to +5.000 / westbound.',
'F3  +5.000 to +7.500 / eastbound.',
'F4  +7.500 to +10.000 / westbound.',
'Historic +4.8 overlook is removed.'],162)
yy=note_block(412,yy-8,'OPENINGS / ROOM SCHEDULE',[
'D01  Stair entry: 1 200 clear x 2 100 high.',
'D02  Control entry: 1 200 clear x 2 100 high.',
'W01  Main observation: 5 400 x 2 600.',
'V01  Interior glazed strip: 650 + 280 reveal.',
'Control clear: 3 600 x 6 400 = 23.04 m2.',
'Vestibule clear: 1 300 x 4 000 = 5.20 m2.',
'East hall route remains 4 000 x 5 000.'],162)
note_block(412,yy-8,'COORDINATION NOTES',[
'D01 north-hinged into vestibule; D02 into Control.',
'Flight guards stay inside the tread bands.',
'Gross dimensions are nominal exact-fit chains.',
'Room and window are centered on east-wall Y=0.',
'Print A2 at 100%; use dimensions, not screen size.'],162)
finish()

C.save()
from ezdxf import bbox
for view in VIEWS:
    ext=bbox.extents(DOC.blocks.get(view['name']))
    ix,iy=view['insert_mm']
    DOC.modelspace().add_text(view['name']+' / MILLIMETRES',dxfattribs={'height':400,'layer':'A-ANNO','insert':(ix+ext.extmin.x,iy+ext.extmax.y+1000)})
DOC.saveas(OUT/'reactor_compact_stair_editable.dxf')
REOPENED=ezdxf.readfile(OUT/'reactor_compact_stair_editable.dxf')
audit=REOPENED.audit()
areas=[]
for code,name,x,y,w,d,kind in STATIONS:
    distance=math.hypot(max(0,abs(x)-w/2),max(0,abs(y)-d/2))-5.2
    areas.append({'id':code,'station':name,'center_m':[x,y],'footprint_m':[w,d],'ring_gap_m':distance})
checks={
'revision':'P02 - centered east-wall Control room',
'module_plan_translation_m':[0,NORTH_SHIFT],
'control_clear_bounds_m':list(ROOM_WORLD),
'control_center_y_m':(ROOM_WORLD[1]+ROOM_WORLD[3])/2,
'observation_window_y_m':[-3.9+NORTH_SHIFT,1.5+NORTH_SHIFT],
'observation_window_center_y_m':(-3.9+1.5)/2+NORTH_SHIFT,
'window_clear_end_jambs_m':[(-3.9+NORTH_SHIFT)-ROOM_WORLD[1],ROOM_WORLD[3]-(1.5+NORTH_SHIFT)],
'core_world_bounds_m':list(CORE_WORLD),
'vestibule_clear_bounds_m':[11.16,1.6,12.46,5.6],
'D01_clear_y_m':[3.0+NORTH_SHIFT,4.2+NORTH_SHIFT],
'D01_hinge_m':[12.46,4.2+NORTH_SHIFT],
'D01_open_leaf_m':[[12.46,4.2+NORTH_SHIFT],[11.26,4.2+NORTH_SHIFT]],
'D02_clear_x_m':[12.71,13.91],
'D02_wall_y_m':2+NORTH_SHIFT,
'D02_reserved_door_space_m':[12.71,.8+NORTH_SHIFT,13.91,2+NORTH_SHIFT],
'hall_octagon_area_m2':abs(sum(SHELL[i][0]*SHELL[(i+1)%8][1]-SHELL[(i+1)%8][0]*SHELL[i][1] for i in range(8)))/2,
'core_gross_m':[6.25,3.2],'core_area_m2':6.25*3.2,
'core_length_chain_m':.2+1.3+13*.25+1.3+.2,
'core_width_chain_m':.2+1.3+.2+1.3+.2,
'clear_flight_width_m':1.3-2*.05,'clear_landing_m':1.3-.05,
'flight_riser_count':14,'flight_going_count':13,'riser_mm':R*1000,
'total_risers':56,'total_rise_m':56*R,'nosing_pitch_deg':math.degrees(math.atan(R/G)),
'control_clear_area_m2':3.6*6.4,'stair_hall_overlap_m2':0.0,
'turbine_to_ring_m':next(a['ring_gap_m'] for a in areas if a['id']=='06'),
'stations':areas,'cad_units':'millimetres','cad_audit_errors':len(audit.errors),
'cad_audit_fixes':len(audit.fixes),'views':VIEWS,
'cad_block_entities':{v['name']:len(REOPENED.blocks.get(v['name'])) for v in VIEWS},
'cad_format_note':'Geometry-only model-space blocks in mm; PDF/SVG are the complete paper sheets.',
'pdf_pages':len(PdfReader(str(PDF)).pages),
'drawing_points_outside_content':[x for x in DRAWING_POINTS if x[1]<10 or x[1]>584 or x[2]<40 or x[2]>375],
'text_outside_sheet':[x for x in TEXT_BOUNDS if x[2]<9 or x[3]<9 or x[4]>585 or x[5]>411],
'source_policy':'All 2D linework newly authored from current written specification. No 3D files opened.',
'limitations':['Schematic architectural game layout, for user review before more 3D work.','Sightline section is an architectural ray diagram, not a completed 3D occlusion audit.']}
(OUT/'drawing_validation.json').write_text(json.dumps(checks,indent=2))
assert checks['pdf_pages']==5
assert abs(checks['control_center_y_m'])<1e-9
assert abs(checks['observation_window_center_y_m'])<1e-9
assert all(abs(j-.5)<1e-9 for j in checks['window_clear_end_jambs_m'])
assert 1.6 <= checks['D01_clear_y_m'][0] < checks['D01_clear_y_m'][1] <= 5.6
assert abs(checks['D02_wall_y_m']-CORE_WORLD[1])<1e-9
assert abs(checks['D02_wall_y_m']-ROOM_WORLD[3])<1e-9
assert abs(checks['total_rise_m']-10)<1e-9
assert checks['cad_audit_errors']==0
assert all(n>0 for n in checks['cad_block_entities'].values())
assert checks['drawing_points_outside_content']==[]
assert checks['text_outside_sheet']==[]
assert checks['turbine_to_ring_m']>=1.31
assert all(s['ring_gap_m']>=1.31 for s in areas)
print(json.dumps({k:v for k,v in checks.items() if k not in ('stations','views')},indent=2))
