"""Draws plan_v7.svg: a to-scale connectivity plan of the proposed facility layout.

Run:  python3 generate_plan.py      (writes plan_v7.svg next to this file)
Render to PNG with any browser, e.g. chromium --headless --screenshot=plan_v7.png --window-size=1400,900 plan_v7.svg

Coordinates are metres, north up, origin at the reactor centre. Real rooms use the outer sizes in MEASURED_ROOM_SIZES.md.
Orange rooms (cafeteria, hall, yard, lobby) have no source sizes; they are proposals. Door positions are not taken from
the room meshes: this plan assumes new doors wherever a link needs one.
"""
import math
SC=4.4; X0=30; Y0=90
def P(x,y): return (X0+(x+110)*SC, Y0+(42.5-y)*SC)
out=[]
def add(t): out.append(t)
def rect(x0,x1,y0,y1,fill='#fff',stroke='#333',sw=2,dash=None,label=None,sub=None,fs=11,tc='#222',subfs=9):
    ax,ay=P(x0,y1); bx,by=P(x1,y0)
    d=f' stroke-dasharray="{dash}"' if dash else ''
    add(f'<rect x="{ax:.1f}" y="{ay:.1f}" width="{bx-ax:.1f}" height="{by-ay:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
    cx=(ax+bx)/2; cy=(ay+by)/2
    if label:
        add(f'<text x="{cx:.1f}" y="{cy-(3 if sub else -4):.1f}" text-anchor="middle" font-size="{fs}" font-weight="700" fill="{tc}">{label}</text>')
    if sub:
        add(f'<text x="{cx:.1f}" y="{cy+11:.1f}" text-anchor="middle" font-size="{subfs}" fill="#666">{sub}</text>')
def line(pts,stroke='#b9b9b9',w=4,dash=None,mk=None):
    d=' '.join(('M' if i==0 else 'L')+f'{P(*p)[0]:.1f} {P(*p)[1]:.1f}' for i,p in enumerate(pts))
    ds=f' stroke-dasharray="{dash}"' if dash else ''
    m=f' marker-start="url(#r)" marker-end="url(#r)"' if mk else ''
    add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{w}"{ds}{m} stroke-linejoin="round"/>')
def dot(x,y,r=4,fill='#444'):
    px,py=P(x,y); add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r}" fill="{fill}"/>')
def text(x,y,t,fs=10,fill='#555',anchor='middle',bold=False,rot=None):
    px,py=P(x,y); r=f' transform="rotate({rot} {px:.1f} {py:.1f})"' if rot else ''
    bw=' font-weight="700"' if bold else ''
    add(f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="{anchor}" font-size="{fs}" fill="{fill}"{bw}{r}>{t}</text>')
def plen(pts): return sum(math.dist(pts[i],pts[i+1]) for i in range(len(pts)-1))


fuel=[(-22.2,-40.4),(-22.2,-30.4),(-8,-30.4),(-8,-16.4),(-8,-13.75)]
# connectors (under rooms)
line(fuel,'#b9b9b9',18)
line([(8,-48),(8,-13.75)],'#d4d4d4',16)                        # spine
line([(-10,-54),(-18.9,-54)],'#b9b9b9',12)                    # hall left -> refinery east
line([(32,-48),(32,-38)],'#b9b9b9',10)               # hall right -> waste
line([(9,-60),(9,-66)],'#b9b9b9',12)                          # hall -> cafeteria
line([(9,-86),(9,-92)],'#b9b9b9',12)                          # cafeteria -> spawn
line([(-8,-76),(-14,-76)],'#b9b9b9',12)                       # cafeteria -> yard
line([(26,-76),(32,-76)],'#b9b9b9',10)                        # cafeteria -> medical
line([(38.5,-71.7),(38.5,-54)],'#b9b9b9',9)
line([(-48,-64),(-48,-30)],'#b9b9b9',9)                         # medical direct door to east arm
RING='#6b6b6b'
line([(-33.7,-49),(-38,-49),(-38,30),(-7.4,30)],RING,4)
line([(-44.1,-24),(-38,-24)],RING,4)
line([(7.4,34),(14,34)],RING,4)
line([(34,-54),(56,-54),(56,34),(29.4,34)],RING,4)
line([(56,-54),(56,-79),(60,-79)],RING,3,dash='6 4')
# rooms
line([(-52,-77),(-56,-77)],'#b9b9b9',10)
rect(-112,-56,-104,-60,fill='#b9a98e',stroke='#7a6a50',label='MOUNTAIN',sub='mine inside (R39)',fs=13,tc='#4b3f2b')
rect(-52,-14,-90,-64,fill='#fde9d0',stroke='#d9822b',sw=2.5)
text(-33,-83,'YARD',13,'#222',bold=True)
text(-33,-86,'new, proposed 38x26 m',9,'#666')
rect(-8,26,-86,-66,fill='#fde9d0',stroke='#d9822b',sw=2.5,label='CAFETERIA',sub='chill room, new, 34x20 m',fs=12)
rect(-10,34,-60,-48,fill='#fde9d0',stroke='#d9822b',sw=2.5,label='HALL',sub='new, proposed 44x12 m',fs=12)
rect(0.3,17.7,-105.4,-92,label='SPAWN',sub='measured 17.4x13.4 m',fs=12)
rect(32,45,-81.5,-71.7,label='MED',sub='',fs=9)
rect(60,78.7,-87,-71.2,label='DOCK',sub='measured 18.7x15.8 m',fs=11)
rect(-33.7,-18.9,-57.6,-40.4,label='REFINERY',sub='measured 14.8x17.6 m',fs=10,subfs=8)
rect(-57,-44.1,-30,-15,fill='#e6f3f5',stroke='#0a7e8c',sw=3,label='COOLING',sub='measured 12.9x15',fs=10,subfs=8)
rect(-13.75,13.75,-13.75,13.75,stroke='#c0392b',sw=5,label='REACTOR',sub='measured 27.5x27.5 m',fs=14,tc='#c0392b')
rect(13.75,20.25,-4.96,6.44,stroke='#c0392b',sw=3,label='ANNEX',sub='',fs=8)
rect(-7.4,7.4,17,42.5,label='TURBINE',sub='+ condenser 14.8x25.5',fs=11,subfs=8)
rect(14,29.4,26,43.2,label='ELECTRICAL',sub='measured 15.4x17.2',fs=10,subfs=8)
rect(28,42.9,-38,-17.2,fill='#fff',stroke='#888',sw=2,label='WASTE',sub='measured 14.9x20.8 m',fs=11,subfs=8)
rect(-50,-16,-102,-94,fill='#e3f0e3',stroke='#2d7a3a',sw=2,label='OUTSIDE: evacuation gate',fs=10,tc='#2d7a3a')
line([(-33,-90),(-33,-94)],'#2d7a3a',3)
text(38.5,-84,'MEDICAL measured 13x9.8 m',9,'#222',bold=True)
text(66,-88.5,'',9)
# gantry
ax,ay=P(-11,11); bx,by=P(11,-11)
add(f'<rect x="{ax:.1f}" y="{ay:.1f}" width="{bx-ax:.1f}" height="{by-ay:.1f}" rx="10" fill="none" stroke="#7b3fa0" stroke-width="2.5" stroke-dasharray="10 5"/>')
for pts in [[(-3,11),(-3,18)],[(11,8),(17,26)],[(11,-8),(30,-16)],[(11,-11),(11,-48)],[(-11,-9),(-8,-17)],[(-11,-4),(-47,-14)]]:
    line(pts,'#7b3fa0',2.5,dash='10 5')
add('<defs><marker id="r" markerWidth="10" markerHeight="10" refX="7" refY="5" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0 0 L10 5 L0 10 Z" fill="#c0392b"/></marker></defs>')
SP={'turbine':[(0,13.75),(0,17)],'elec':[(10,13.75),(18,26)],'waste':[(13.75,-6),(28,-24)],'cool':[(-13.75,-5),(-30,-19),(-44.1,-19)]}
for k,pts in SP.items(): line(pts,'#c0392b',3,mk=True,dash='8 5' if k=='waste' else None)
dot(-38,-19,5,'#444'); dot(-38,-49,4)
line([(-22.2,-64),(-22.2,-57.6)],'#2b6cb0',3)
line([(-22.2,-80),(-22.2,-64)],'#2b6cb0',3,dash='8 5')
dot(-22.2,-80,4,'#2b6cb0')
line([(-58,-60),(-58,-34),(-51,-34),(-51,-30)],'#0a7e8c',4.5)
text(-60,-47,'mine-water pipe',10,'#0a7e8c',bold=True,rot=-90)
text(-35,-8,'west arm of the outer ring',10,'#555',rot=-90)
text(59,-10,'east arm',10,'#555',rot=-90)
text(12,-32,'spine',10,'#777',rot=-90)
text(-16,-26,'fuel corridor ~38 m',9,'#777',rot=-90)
text(-41.5,-26,'link 7 m',8,'#555')
text(-47,-46,'yard-to-cooling link 36 m',9,'#555',rot=-90)
text(-24,-72,'shortcut: yard to refinery',9,'#2b6cb0',bold=True,anchor='end')
text(-14,-51.5,'LEFT',9,'#333',bold=True); text(8,-46,'MIDDLE',9,'#333',bold=True); text(32,-45.5,'RIGHT',9,'#333',bold=True)
text(41,-62,'medical direct door',9,'#555',anchor='start')
text(61,-70,'locked link',8,'#555',anchor='start')
# travel
W,L=4.5,1.5
R={}
R['Spawn door to mine door']=([(9,-92),(9,-86),(-8,-76),(-14,-76),(-56,-77)],W)
R['Mine door to refinery freight door']=([(-56,-77),(-22.2,-66),(-22.2,-56.5)],L)
R['Refinery fuel door to reactor (cart)']=(fuel,L)
R['Hall to reactor (spine)']=([(8,-48),(8,-13.75)],W)
R['Spawn door to reactor']=([(9,-92),(9,-48),(8,-48),(8,-13.75)],W)
R['Medical to reactor']=([(38.5,-71.7),(38.5,-54),(8,-54),(8,-13.75)],W)
R['Reactor to turbine']=([(0,13.75),(0,17)],W)
R['Reactor to electrical']=([(10,13.75),(18,26)],W)
R['Reactor to waste']=([(13.75,-6),(28,-24)],W)
R['Reactor to cooling']=([(-13.75,-5),(-30,-19),(-44.1,-19)],W)
R['Mine-water pipe length']=([(-58,-60),(-58,-34),(-51,-34),(-51,-30)],W)
R['Spawn door to cooling (new yard link)']=([(9,-92),(9,-86),(-8,-76),(-14,-76),(-45,-70),(-48,-64),(-48,-30)],W)
R['Spawn door to electrical (now farthest)']=([(9,-92),(9,-48),(8,-48),(8,-13.75),(10,13.75),(18,26)],W)
R['Cooling to electrical, round the ring']=([(-45,-24),(-38,-24),(-38,30),(-7,30),(-7,34),(14,34)],W)
R['Cooling to electrical, through the reactor']=([(-45,-19),(-30,-19),(-13.75,-5),(10,13.75),(18,26)],W)
rows=[(k,plen(p),plen(p)/s,s) for k,(p,s) in R.items()]
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 900" font-family="Helvetica, Arial, sans-serif">
<rect width="1400" height="900" fill="#f4f1ea"/>
<text x="40" y="36" font-size="22" font-weight="700" fill="#222">To-scale plan v7: measured room sizes</text>
<text x="40" y="58" font-size="12" fill="#555">North up. Every real room now uses its measured outer size. Orange = new room (my proposed sizes). Red = kite routes, dark grey = outer ring, light grey = connectors, purple = gantry, teal = mine water.</text>
'''+'\n'.join(out)
px=895
svg+=f'<rect x="{px-10}" y="75" width="500" height="810" fill="#fff" stroke="#bbb"/>'
svg+=f'<text x="{px+6}" y="100" font-size="15" font-weight="700" fill="#1d6b3a">Travel times along this plan</text>'
svg+=f'<text x="{px+6}" y="117" font-size="10.5" fill="#666">Walking 4.5 m/s, loaded cart 1.5 m/s (spec assumptions), straight-line connectors.</text>'
y=140
for k,l,t,s_ in rows:
    kind='cart' if s_==L else 'walk'
    svg+=f'<text x="{px+6}" y="{y}" font-size="11.5" fill="#222">{k}</text><text x="{px+350}" y="{y}" font-size="11.5" fill="#222" text-anchor="end">{l:.0f} m</text><text x="{px+484}" y="{y}" font-size="11.5" font-weight="700" fill="#222" text-anchor="end">{t:.0f} s {kind}</text>'
    y+=20
y+=14
svg+=f'<text x="{px+6}" y="{y}" font-size="14" font-weight="700" fill="#8a2d1a">What the measurements changed</text>'; y+=20
notes=["Measured in Blender (outer size incl. sills, roofs, annexes):",
"- Reactor 27.5 x 27.5 m (+ 6.5 m east annex): I had 29 x 29.",
"- Spawn 17.4 x 13.4 m: I had 14 x 28. It is wide and shallow.",
"- Dock 14.2 x 18.2 m shell (18.7 x 15.8 m laid out sideways).",
"- Refinery 14.8 x 17.6, electrical 15.4 x 17.2 (incl. reserve),",
"  waste 14.9 x 20.8, cooling 12.9 x 15, medical 13 x 9.8.",
"- Fuel corridor envelope 23.1 x 24 m: matches the 38 m L path.",
"Outer sizes are bigger than the contract interior sizes I used",
"before (e.g. waste 12 x 18 inside, 14.9 x 20.8 outside).",
"",
"Effect on the plan:",
"- Spawn column is shorter, so the front end is less tall.",
"- Fuel connector at the reactor is now 2.7 m (corridor sill",
"  fixes the start), so fuel run stays ~27 s loaded.",
"- Nothing overlaps; the east trunk and waste still fit.",
"",
"Still proposals: cafeteria, hall, yard (no source sizes).",
"Not built, not saved in the repo."]
for n in notes:
    svg+=f'<text x="{px+6}" y="{y}" font-size="11.5" fill="#222">{n}</text>'; y+=16.5
svg+='</svg>'
import pathlib
pathlib.Path(__file__).with_name('plan_v7.svg').write_text(svg)
for k,l,t,s_ in rows: print(f'{k:46s} {l:6.1f} m {t:5.1f} s')
