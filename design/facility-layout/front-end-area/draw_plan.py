from design_layout import *
S=13.5; X0=40; Y0=95; XMIN=-50; YMAX=-46
def P(x,y): return (X0+(x-XMIN)*S, Y0+(YMAX-y)*S)
out=[]
def add(t): out.append(t)
def R(x0,x1,y0,y1,fill='none',stroke='none',sw=1,dash=None,op=1):
    ax,ay=P(x0,y1); bx_,by=P(x1,y0)
    d=f' stroke-dasharray="{dash}"' if dash else ''
    add(f'<rect x="{ax:.1f}" y="{ay:.1f}" width="{bx_-ax:.1f}" height="{by-ay:.1f}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def T(x,y,t,fs=11,fill='#222',anchor='middle',bold=False,rot=None):
    px,py=P(x,y); r=f' transform="rotate({rot} {px:.1f} {py:.1f})"' if rot else ''
    b=' font-weight="700"' if bold else ''
    add(f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="{anchor}" font-size="{fs}" fill="{fill}"{b}{r}>{t}</text>')
def L(pts,stroke='#333',sw=2,dash=None,mk=None):
    d=' '.join(('M' if i==0 else 'L')+f'{P(*p)[0]:.1f} {P(*p)[1]:.1f}' for i,p in enumerate(pts))
    ds=f' stroke-dasharray="{dash}"' if dash else ''
    m=f' marker-end="url(#{mk})"' if mk else ''
    add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"{ds}{m}/>')
COL=dict(kitchen='#d9c9a8',counter='#a88b5a',table='#b98f55',chair='#7a6a50',booth='#8b6b4a',vending='#c0392b',appliance='#6b7b8b',tv='#222',couch='#a8553a',plant='#4f8a4a',sign='#555',
 bench='#8a6a45',desk='#6b7b8b',safety='#2d7a3a',gantry='#7b3fa0',cliff='#b9a98e',portal='#4a3b2a',rail='#555',cart='#8a5a2a',crate='#b98f55',pallet='#9a7a4a',barrel='#4a6a8a',drum='#6a6a6a',
 scrap='#7a5a4a',tarp='#5a7a5a',machine='#7a7a7a',canopy='#999',planter='#a0a0a0',tree='#3f7a3f',pole='#222')
add('<defs><marker id="rd" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L12 6 L0 12 Z" fill="#c0392b"/></marker><marker id="bl" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L12 6 L0 12 Z" fill="#2b6cb0"/></marker></defs>')
# ground / zones
R(-50,42,-96,-46,fill='#f4f1ea')
R(-52,-48,-84,-60,fill='#b9a98e',stroke='#7a6a50',sw=2)
T(-50,-72,'MOUNTAIN',12,'#4b3f2b',bold=True,rot=-90)
R(*YARD[:2],*YARD[2:],fill='#e5e0d4',stroke='none')
x=YARD[0]
while x<=YARD[1]:
    L([(x,YARD[2]),(x,YARD[3])],'#d3cdbf',0.8); x+=4
y=YARD[2]
while y<=YARD[3]:
    L([(YARD[0],y),(YARD[1],y)],'#d3cdbf',0.8); y+=4
R(*CAF[:2],*CAF[2:],fill='#f1dfc4')
R(*HALL[:2],*HALL[2:],fill='#dfe5ea')
R(*SPAWN[:2],*SPAWN[2:],fill='#fff',stroke='#333',sw=3)
R(*MEDICAL[:2],*MEDICAL[2:],fill='#fff',stroke='#333',sw=3)
R(-18.9,-4,-55.5,-52.5,fill='#cfd6dc',stroke='#555',sw=1.5)
T(-11.4,-54.6,'west colonnade (covered)',9,'#555')
# porch
R(-12,-8,-72,-66,fill='#d8cfbc',stroke='#999',sw=1,dash='4 3'); T(-10,-69,'porch',8,'#777',rot=-90)
# objects
for o in objs:
    c=COL.get(o['cat'] if o['cat'] in COL else o['color'],'#888')
    if o['kind']=='box':
        if o['cat']=='cliff': continue
        op=0.55 if o['cat'] in ('canopy','gantry') else 1
        R(o['x0'],o['x1'],o['y0'],o['y1'],fill=c,stroke='#444' if o['cat'] not in('rail',) else 'none',sw=0.6,op=op)
    else:
        px,py=P(o['x'],o['y']); add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{max(o["r"]*S,2):.1f}" fill="{c}" stroke="#333" stroke-width="0.6"/>')
# walls (0.3 m)
def walls(rc,col='#222',sw=4):
    R(*rc[:2],*rc[2:],stroke=col,sw=sw)
walls(CAF); walls(HALL); walls(SPAWN); walls(MEDICAL)
# yard perimeter: north fence, south fence
L([(-48,-60),(-12,-60)],'#555',3,'8 4'); L([(-48,-84),(-8,-84)],'#555',3,'8 4'); L([(-12,-60),(-8,-60)],'#222',4); L([(-12,-84),(-8,-84)],'#222',4)
# door gaps (cover wall) + ticks
def gap_h(x,y,w,col):  # opening in a horizontal wall
    R(x-w/2,x+w/2,y-0.3,y+0.3,fill=col,stroke='none'); R(x-w/2,x+w/2,y-0.12,y+0.12,fill='#c0392b')
def gap_v(x,y,w,col):
    R(x-0.3,x+0.3,y-w/2,y+w/2,fill=col,stroke='none'); R(x-0.12,x+0.12,y-w/2,y+w/2,fill='#c0392b')
gap_h(8,-80,2.6,'#fff'); gap_h(8,-60,6,'#f1dfc4'); gap_v(-8,-70,3,'#f1dfc4'); gap_v(26,-70,2.2,'#f1dfc4')
gap_v(-4,-54,2.4,'#dfe5ea'); gap_h(8,-48,3.6,'#dfe5ea'); gap_v(32,-54,2.4,'#dfe5ea')
gap_h(-22.2,-60,3,'#e5e0d4'); gap_h(-46,-60,2.4,'#e5e0d4'); gap_h(-28,-84,6,'#e5e0d4')
# axes
L([(8,-80),(8,-47)],'#c0392b',3,'10 6','rd'); T(9,-46.2,'to reactor: 34 m spine, 75 m clear sightline',10,'#c0392b',anchor='start',bold=True)
L([(-8,-70),(-47,-70)],'#2b6cb0',3,'10 6','bl'); T(-28,-69.3,'mine axis: 40 m across the yard to the portal',10,'#2b6cb0',bold=True)
# labels
T(-29,-66.2,'YARD  40 x 24 m',13,'#333',bold=True)
T(-29,-67.6,'open air: rails, junk, equipment',10,'#555')
T(17.5,-69.6,'CAFETERIA / CHILL ROOM',12,'#333',bold=True)
T(17.5,-71.0,'34 x 20 m',10,'#555')
T(20,-50.2,'HALL  36 x 12 m',12,'#333',bold=True)
T(8,-87.5,'SPAWN (measured 17.4 x 13.4 m)',11,'#333',bold=True)
T(32.5,-77.5,'MEDICAL',10,'#333',bold=True)
T(-4,-52.2,'to refinery',9,'#555'); T(8,-46.7,'',9)
L([(32,-54),(38,-54)],'#999',6); L([(36,-54),(36,-46)],'#999',6,mk=None); T(33,-55.4,'east trunk: dock + waste',9,'#555',anchor='start')
T(-22.2,-58.8,'refinery freight gate',9,'#555'); T(-46,-58.8,'to cooling',9,'#555'); T(-28,-85.2,'evacuation gate',9,'#2d7a3a',bold=True)
T(-48.6,-70,'mine portal',9,'#fff',rot=-90)
T(8,-81.2,'spawn airlock 2.6 m',9,'#555'); T(8,-58.6,'6 m opening',9,'#555'); T(-6.6,-67.4,'yard door',9,'#555',rot=-90)
T(26.9,-69.3,'medical',9,'#555',rot=-90)
T(8,-49.3,'heavy blast door (spine)',9,'#fff'); T(9,-50.7,'gantry landing, 4.2 m up',9,'#7b3fa0',bold=True)
# scale + north
sx,sy=P(-48,-94.6); add(f'<path d="M{sx:.1f} {sy:.1f} L{sx+10*S:.1f} {sy:.1f}" stroke="#222" stroke-width="3"/><text x="{sx:.1f}" y="{sy+14:.1f}" font-size="11">10 m</text>')
nx,ny=P(40,-94); add(f'<path d="M{nx:.1f} {ny:.1f} L{nx:.1f} {ny-30:.1f}" stroke="#222" stroke-width="3" marker-end="url(#rd)"/><text x="{nx-4:.1f}" y="{ny+14:.1f}" font-size="12" font-weight="700">N</text>')
body='\n'.join(out)
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1330 820" font-family="Helvetica, Arial, sans-serif">
<rect width="1330" height="820" fill="#f4f1ea"/>
<text x="40" y="36" font-size="22" font-weight="700" fill="#222">Cafeteria, hall and yard: one connected module (plan, to scale)</text>
<text x="40" y="58" font-size="12" fill="#555">Proposal. Two clear axes from the spawn door: north to the reactor, west to the mine. Red ticks = doors and openings. Furniture is representative; counts and triangle costs are in the budget sheet.</text>
{body}
<g font-size="11" fill="#222" transform="translate(40,790)">
<rect x="0" y="-12" width="12" height="12" fill="#f1dfc4" stroke="#333"/><text x="18" y="-2">cafeteria floor</text>
<rect x="130" y="-12" width="12" height="12" fill="#dfe5ea" stroke="#333"/><text x="148" y="-2">hall floor</text>
<rect x="230" y="-12" width="12" height="12" fill="#e5e0d4" stroke="#333"/><text x="248" y="-2">yard, 4 m concrete slabs</text>
<rect x="410" y="-12" width="12" height="12" fill="#7b3fa0" fill-opacity="0.55"/><text x="428" y="-2">gantry landing</text>
<rect x="540" y="-12" width="12" height="12" fill="#b98f55"/><text x="558" y="-2">tables, crates, pallets</text>
<rect x="710" y="-12" width="12" height="12" fill="#c0392b"/><text x="728" y="-2">doors, vending</text>
<rect x="830" y="-12" width="12" height="12" fill="#a8553a"/><text x="848" y="-2">couches</text>
</g></svg>'''
open('plan.svg','w').write(svg)
