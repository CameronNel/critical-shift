"""Dimensioned equipment plan; data is authored and audited separately in Blender."""
from pathlib import Path
from html import escape
import json
R=Path(__file__).resolve().parent
S=43; ox=370; oy=960
def xy(x,y):return ox+x*S,oy-y*S
v=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1120" viewBox="0 0 1200 1120"><rect width="1200" height="1120" fill="#eee9df"/><g font-family="Arial" fill="#292723">']
def rect(x,y,w,h,fill,stroke='#554e45',dash=''):
 a,b=xy(x,y+h);v.append(f'<rect x="{a}" y="{b}" width="{w*S}" height="{h*S}" fill="{fill}" stroke="{stroke}" stroke-width="1" stroke-dasharray="{dash}"/>')
def label(x,y,t,size=11):
 a,b=xy(x,y);v.append(f'<text x="{a}" y="{b}" font-size="{size}">{escape(t)}</text>')
def line(points,col='#ab742b',width=2,dash=''):
 p=' '.join(f'{xy(x,y)[0]},{xy(x,y)[1]}' for x,y in points);v.append(f'<polyline points="{p}" fill="none" stroke="{col}" stroke-width="{width}" stroke-dasharray="{dash}"/>')
v+=['<text x="65" y="45" font-size="27" font-weight="bold">WASTE STORAGE / ARCHITECTURAL PLAN</text>','<text x="65" y="73" font-size="14">Metres · floor Z 0 · ceiling 4.80 · wall 0.32 · equipment and service envelopes</text>']
rect(-6.32,-.32,12.64,18.64,'#514b44');rect(-6,0,12,18,'#d2c9b8')
rect(-1.8,0,3.6,18,'#e4d6ad','#c4a55d')
for x,y,w,h in [(-1.5,-.32,3,.32),(-1.2,18,2.4,.32),(6,1.8,.32,1.2)]:rect(x,y,w,h,'#e4d6ad')
for side in [-1,1]:
 for y in [4.8,9.4]:
  for yy in [y,y+4]:rect(-6 if side<0 else 2.15,yy-.08,3.85,.16,'#898072')
  rect(side*2.08-.065,y+.075,.13,.95,'#514b44')
  line([(side*2.04,y+.11),(side*2.04,y+3.89)],'#777063',1,'3 3')
measured=json.loads((R/'equipment-measured.json').read_text())
for e in measured:
 if e['id']=='HJ01_HANDLING_JIB':continue
 x,y=e['min'][:2];w=e['max'][0]-x;h=e['max'][1]-y
 rect(x,y,w,h,'#b9926f');label(x+.03,y+h*.5,e['id'].split('_')[0],10)
 if e['type'] in ['residue_overpack','shielded_cask']:
  a,b=xy(*e['origin'][:2]);r=.43 if e['type']=='residue_overpack' else .57;v.append(f'<circle cx="{a}" cy="{b}" r="{r*S}" fill="none" stroke="#554e45"/>')
# Work strips separate from freight passage. Their labels are dimensions to verify.
for x,y,w,h in [(-3.86,10.45,.90,.90),(-3.86,11.8,.90,.95),(3.175,4.925,2.15,.90),(3.175,7.775,2.15,.90),(-4,5.05,.9,.9),(-4,6.35,.9,.9),(-4,7.65,.9,.9),(3.14,10.70,.90,2.10),(-5.65,14.46,2.55,.90),(3.70,15.47,1.7,.9)]:rect(x,y,w,h,'none','#946931','5 3')
rect(-5.95,.4,3.55,3.5,'none','#514b44');label(-5.7,3.35,'IM01 / INVENTORY',11)
line([(-2.4,.4),(-2.4,1.65)],'#514b44',3);line([(-2.4,2.75),(-2.4,3.9)],'#514b44',3)
label(-2.28,2.4,'1.10',9)
line([(-2.48,2.815),(-3.62,2.815)],'#514b44',3)
line([(6.36,3.065),(7.61,3.065)],'#514b44',3)
line([(6.36,3.065),(6.36,1.815)],'#514b44',1,'3 3')
a,b=xy(-3.15,9.95);v.append(f'<circle cx="{a}" cy="{b}" r="10" fill="#a8663b"/>');line([(-3.15,9.95),(-2.125,8.925)],'#a8663b',4);label(-3.0,10,'HJ01',10)
for path in [[(0,.1),(0,17.9)],[(0,2.4),(6,2.4)],[(0,6.6),(-3.50,6.6)],[(0,11),(-3,11)],[(0,6.7),(2.8,6.7)],[(0,11),(3.15,11)],[(0,16),(-2.45,16),(-2.45,14.8),(-4.4,14.8)],[(0,16),(3.3,16)]]:line(path,'#79573c',1,'5 3')
for x,y,r in [(0,2.5,1.8),(0,16,1.5)]:
 a,b=xy(x,y);v.append(f'<circle cx="{a}" cy="{b}" r="{r*S}" fill="none" stroke="#ae843b" stroke-dasharray="7 4"/>')
label(-1.5,8.65,'3.60 CLEAR SPINE',11)
label(-1.55,-.98,'WS_RECEIVING 3.00 × 3.20',11);label(-1.65,18.9,'WS_DISPATCH 2.40 × 2.80',11)
label(6.5,4.0,'WS_PERSONNEL',11);label(6.5,3.6,'1.20 × 2.30',11)
line([(-6,19.65),(6,19.65)],'#514b44',1);label(-1.5,19.8,'12.00 CLEAR',13)
line([(-7.1,0),(-7.1,18)],'#514b44',1);label(-7.05,9,'18.00',12)
notes=['DESIGN + MEASURED INTERFACE','Floor footprint 12.64 × 18.64 incl. walls.','Receiving center (0,0,0), outward −Y.','Dispatch center (0,18,0), outward +Y.','Personnel center (6,2.4,0), outward +X.','All opening dimensions width × height.','','EQUIPMENT / FUNCTIONS','RA01–03: three residue overpacks.','SC01–02: two tall shielded casks.','DR01–02: sealed dry containers.','QH01: quarantine; open inspectable lid.','CT01: 1.00 × 1.80 transfer cart envelope.','HJ01: floor mounted manual handling jib.','VF01: filter / fan extraction skid.','IM01: inventory booth / scan / dose.','WB01: seal and container maintenance.','','WORKING + CIRCULATION','Dashed ochre boxes: ≥0.90 service strips.','Dashed brown lines: sampled player routes.','Cart spine 3.60; reserved turns Ø3.60/3.00.','Player audit uses 0.60 × 0.60 × 1.825 body.','Cart geometry and actual sweeps separately audited.','','ELECTRICAL PROPOSAL','Waste origin there = (0,16.97,0), Rz 0.','Waste exterior −0.32 meets D02 exterior 16.65.','Electrical owns receiving floor Y−.32…0.','','EXACT UTILITY SOCKET CENTERS','WS_POWER (6.32,16.8,3.6), +X; 0.20 × 0.20','WS_EXTRACT (−4.8,18.32,4), +Y; 0.65 × 0.60','WS_DATA (−6.32,1.2,2.8), −X; 0.12 × 0.12','Utilities and onward networks remain unbound.']
for n,t in enumerate(notes):v.append(f'<text x="755" y="{118+n*23}" font-size="{13 if n in [0,7,18,25,30] else 11}" font-weight="{700 if n in [0,7,18,25,30] else 400}">{escape(t)}</text>')
v.append('<text x="65" y="1080" font-size="12">Architectural / gameplay intent. No neighboring section modified. Scene measurements and cold-open evidence govern acceptance.</text></g></svg>')
(R/'floorplan.svg').write_text('\n'.join(v),encoding='utf-8')

