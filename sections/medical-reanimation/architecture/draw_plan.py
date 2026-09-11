"""Dimensioned vector plan from the preserved local contract. No scene edits."""
import json,html
from pathlib import Path
R=Path(__file__).resolve().parents[1];d=json.loads((R/'interface.json').read_text());out=[]
def emit(s):out.append(s)
def xy(x,y):return 440+x*60,830-y*60
def line(x1,y1,x2,y2,col='#2c3030',width=2,dash=''):
 a,b=xy(x1,y1),xy(x2,y2);emit(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{col}" stroke-width="{width}" stroke-dasharray="{dash}"/>')
def rect(x1,y1,x2,y2,col,stroke='#414744'):
 a,b=xy(x1,y2),xy(x2,y1);emit(f'<rect x="{a[0]}" y="{a[1]}" width="{b[0]-a[0]}" height="{b[1]-a[1]}" fill="{col}" stroke="{stroke}"/>')
def label(x,y,t,size=13,col='#242a29'):
 a=xy(x,y);emit(f'<text x="{a[0]}" y="{a[1]}" font-size="{size}" text-anchor="middle" fill="{col}">{html.escape(t)}</text>')
emit('<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="1000" viewBox="0 0 1280 1000"><rect width="1280" height="1000" fill="#f3f1e9"/><g font-family="Arial,sans-serif">')
emit('<text x="70" y="55" font-size="28" fill="#242a29">MEDICAL / REANIMATION</text><text x="70" y="83" font-size="15">Preserved Grok R09 layout · metres · local floor Z=0 · +Y inward / +Z up</text>')
rect(-4,0,4,9,'#e4e2da');rect(1.48,9,3.18,11.12,'#e4e2da')
pts=d['interior']['floor_outline_xy'];emit('<polyline points="'+' '.join(f'{xy(*p)[0]},{xy(*p)[1]}' for p in pts+[pts[0]])+'" fill="none" stroke="#343938" stroke-width="10"/>')
line(-1.1,0,1.1,0,'#f3f1e9',12);line(1.55,9,2.75,9,'#e4e2da',12)
colors={'OCRU':'#838b87','Console':'#b6b8ac','Cartridges':'#ccad85','ReservePower':'#a6aaa3','Recovery':'#bbbcb2','CartParking':'#d5bb98','Decon':'none','PowerPanel':'#9ba099'}
names={'Console':['RESTART','1.86 × 0.90'],'Cartridges':['STOCK'],'ReservePower':['RESERVE'],'Recovery':['RECOVERY','1.30 × 2.36'],'SupplyBench':['SUPPLIES'],'Wash':['WASH'],'SuppliesCabinet':['STORAGE'],'CartParking':['CART','0.74 × 2.10'],'OCRU':['OCRU','2.50 × 4.30']}
for n,b in d['equipment_bounds_xy_m'].items():
 if n in ['Decon','PowerPanel']:continue
 rect(*b,colors.get(n,'#cacbc0'));x=(b[0]+b[2])/2;y=(b[1]+b[3])/2
 for j,t in enumerate(names.get(n,[n])):label(x,y-j*.25,t,11)
# Reserved central clear apron and conservative straight cart operating path.
rect(-3.90,6.785,-1.75,8.3125,'none','#6c766e');label(-2.825,7.57,'REAR SERVICE',10);label(-2.825,7.30,'1.5275 m band',10)
rect(-.98,3.1,2.18,6.2,'none','#c47a3a');label(.60,5.75,'TRANSFER APRON',12)
for a,b in zip([(0,-.8),(0,6.95),(2.15,6.95),(2.15,10.2)],[(0,6.95),(2.15,6.95),(2.15,10.2)]):line(*a,*b,'#bd672b',3,'7 5')
for a,b in [((0,4.63),(-1.08,4.63)),((-3.12,1.33),(0,1.33))]:line(*a,*b,'#bd672b',3,'7 5')
label(2.33,10.28,'DECON',13);label(2.33,9.98,'1.70 × 2.12',11)
label(0,-.40,'main_entry · 2.20 W × 2.50 H',14);label(2.15,8.66,'1.20 × 2.15',11)
line(-4,-.9,4,-.9);line(-4,-.75,-4,-1.05);line(4,-.75,4,-1.05);label(0,-1.2,'8.00 m',15)
line(-4.7,0,-4.7,9);line(-4.55,0,-4.85,0);line(-4.55,9,-4.85,9);label(-5.4,4.5,'9.00 m',15)
line(1.48,11.7,3.18,11.7);line(1.48,11.55,1.48,11.85);line(3.18,11.55,3.18,11.85);label(2.33,11.95,'1.70 m',13)
line(4.55,9,4.55,11.12);label(5.1,10.1,'2.12 m',13)
for y in [0,3,6,9]:label(-4.22,y,f'{y}',10)
notes=[('ARCHITECTURE',['Main clear shell 8.00 × 9.00 × 3.60 m','Decon clear height 2.55 m','Walls 0.18 m; ceiling beams lowest Z=3.32','One external portal; no new rear doorway']),('CIRCULATION / SERVICE',['Player test envelope 0.60 × 0.60 × 1.825 m','Cart sweep 0.74 × 2.124 m + tolerance','Main entry clear 2.20 m; decon opening 1.20 m','OCRU berth 2.20 × 0.88 m, surface Z=1.02','Cart parks southwest; extract at Y=1.33','Decon wand serves cart on adjacent apron']),('INTERFACE OWNERSHIP',['main_entry outward (0,-1,0), threshold (0,0,0)','Exterior face Y=-0.18; medical owns door','MED_POWER / MED_DATA: rear wall caps','MED_WATER: east alcove exterior cap','MED_DRAIN / MED_EXTRACT: rear alcove caps','Exact positions and sizes: interface.json']),('INTEGRATION LIMITS',['Neighbor transforms remain UNBOUND','Fuel S02_CLEAN is 2.00 × 2.50 m','Connector owner supplies clean-service junction','No adjacent section geometry moved or imported','Runtime ragdoll/state logic belongs to host'])]
yy=160
for title,lines in notes:
 emit(f'<text x="835" y="{yy}" font-size="17" font-weight="bold">{title}</text>');yy+=27
 for t in lines:emit(f'<text x="835" y="{yy}" font-size="13">{html.escape(t)}</text>');yy+=23
 yy+=24
emit('<text x="70" y="967" font-size="13">Equipment rectangles show inherited reserved envelopes. Actual projected bounds and route samples are in the saved-artifact technical report.</text></g></svg>')
(R/'architecture/floorplan.svg').write_text('\n'.join(out),encoding='utf-8');print('PLAN_SAVED')
