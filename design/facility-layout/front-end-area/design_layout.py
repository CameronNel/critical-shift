"""Shared layout objects for the plan drawing and the greybox renders (plan frame, metres)."""
from design_data import *
objs=[]   # dict(kind='box'|'cyl', cat, x0,x1,y0,y1,z0,z1 | x,y,r,z0,z1, color)
def box(cat,x0,x1,y0,y1,z0,z1,color): objs.append(dict(kind='box',cat=cat,x0=x0,x1=x1,y0=y0,y1=y1,z0=z0,z1=z1,color=color))
def cyl(cat,x,y,r,z0,z1,color): objs.append(dict(kind='cyl',cat=cat,x=x,y=y,r=r,z0=z0,z1=z1,color=color))
def bx(cat,cx,cy,w,d,h,color,z0=0): box(cat,cx-w/2,cx+w/2,cy-d/2,cy+d/2,z0,z0+h,color)

# ---------------- CAFETERIA ----------------
# kitchen block + serving counter (NE)
box('kitchen',14,26,-64,-60,0,3.2,'kitchen')
box('counter',10.8,25.2,-66,-64.4,0,1.1,'counter')
for tx,ty in [(-3.5,-63),(2.5,-63),(-3.5,-66.2),(2.5,-66.2),(-3.5,-74.5),(2.5,-74.5)]:
    bx('table',tx,ty,1.8,0.9,0.75,'table')
    for dx in (-0.5,0.5):
        bx('chair',tx+dx,ty-0.85,0.45,0.45,0.9,'chair'); bx('chair',tx+dx,ty+0.85,0.45,0.45,0.9,'chair')
for i,cx in enumerate((-5.5,-1.5,2.5)):
    box('booth',cx-1.5,cx+1.5,-80,-77.6,0,1.4,'booth')
# chairs: 6 tables x 4 = 24
for vy in (-62.2,-63.6,-65.0): bx('vending',-7.3,vy,0.9,1.2,2.0,'vending')
bx('appliance',12.4,-60.6,0.8,0.8,1.1,'appliance'); bx('appliance',13.4,-60.6,0.6,0.6,1.5,'appliance'); bx('appliance',14.2,-60.6,0.8,0.7,1.8,'appliance')
# lounge SE
box('tv',18,24,-79.9,-79.6,1.0,2.4,'screen')
bx('couch',18,-75.8,2.2,0.9,0.9,'couch'); bx('couch',24,-75.8,2.2,0.9,0.9,'couch'); bx('table',21,-77.4,1.2,0.6,0.45,'table')
cyl('plant',25.2,-79.2,0.4,0,1.4,'plant'); cyl('plant',16.6,-79.2,0.4,0,1.4,'plant'); cyl('plant',-7.2,-79.2,0.4,0,1.4,'plant'); cyl('plant',25.2,-61.0,0.4,0,1.4,'plant')
box('board',-7.9,-7.7,-76.5,-73,1.2,2.2,'sign')
# ---------------- HALL ----------------
for bxm in (0,16,28): bx('bench',bxm,-58.9,2.0,0.5,0.45,'bench')
bx('desk',22.5,-58.4,3.0,1.6,1.1,'desk')
box('safety',-3.4,0.8,-49.6,-48.2,0,2.0,'safety')
bx('safety',13.5,-59.6,2.0,0.6,2.0,'safety')
box('board',16,26,-48.2,-48.05,2.0,3.4,'sign')
# gantry landing over the spine door
box('gantry',3,13,-50.2,-48.2,4.2,4.4,'gantry')
for gx in (3,13): box('gantry',gx-0.05,gx+0.05,-50.2,-48.2,4.4,5.3,'gantry')
# ---------------- YARD ----------------
# mine portal (west edge) and cliff wall
box('cliff',-48.0,-52.0,-84,-60,0,H_YARD_WALL,'cliff')
box('portal',-48.4,-48.0,-73.6,-66.4,0,3.6,'portal')
# rails
for ty in (-72.35,-71.65): box('rail',-47.5,-22.2,ty-0.05,ty+0.05,0,0.15,'rail')
for tx in (-22.55,-21.85): box('rail',tx-0.05,tx+0.05,-72.4,-60.2,0,0.15,'rail')
for cx in (-40,-35.5): bx('cart',cx,-72,2.4,1.3,1.3,'cart',0.2)
# junk clusters
import random
rnd=random.Random(7)
def cluster(x0,x1,y0,y1,n,kinds):
    for i in range(n):
        k=rnd.choice(kinds); x=rnd.uniform(x0,x1); y=rnd.uniform(y0,y1)
        if k=='crate': bx('crate',x,y,1.0,1.0,1.0+rnd.choice((0,0,1.0)),'crate')
        elif k=='pallet': bx('pallet',x,y,1.2,1.0,0.15,'pallet')
        elif k=='barrel': cyl('barrel',x,y,0.3,0,0.9,'barrel')
        elif k=='drum': cyl('drum',x,y,0.55,0,0.9,'drum')
        elif k=='scrap': bx('scrap',x,y,2.4,1.6,1.1,'scrap')
        elif k=='tarp': bx('tarp',x,y,2.0,1.6,1.0,'tarp')
cluster(-46.5,-39,-64.5,-61,6,['crate','barrel','barrel','pallet'])
cluster(-46.5,-37,-83,-77,8,['scrap','scrap','drum','barrel'])
cluster(-30,-18,-83.5,-79,7,['pallet','tarp','crate'])
cluster(-14,-9.5,-83,-76,3,['crate','barrel'])
bx('gen',-13,-80,3.0,1.6,1.8,'machine'); cyl('tank',-16.5,-81,1.1,0,2.4,'machine'); cyl('tank',-11,-62.6,0.9,0,2.0,'machine')
# canopies
box('canopy',-12,-8,-76,-64,3.4,3.6,'canopy'); box('canopy',-26,-18,-64,-60,3.4,3.6,'canopy')
for px_,py_ in ((-12,-76),(-12,-64),(-26,-64),(-18,-64)): box('canopy',px_-0.08,px_+0.08,py_-0.08,py_+0.08,0,3.4,'canopy')
# benches, planters, trees
for cx,cy in ((-10.5,-64.8),(-10.5,-75.2),(-10.5,-77.2)): bx('bench',cx,cy,0.5,1.6,0.45,'bench')
for cx,cy in ((-9,-62),(-9,-65),(-9,-75),(-9,-78),(-9,-81),(-14,-63)): bx('planter',cx,cy,1.2,1.2,0.6,'planter')
for cx,cy in ((-45,-62),(-45,-82),(-34,-62),(-16,-82)): cyl('tree',cx,cy,1.4,0,4.5,'tree')
# pole lights
for cx,cy in ((-40,-66),(-30,-66),(-20,-66.5),(-34,-80),(-14,-66.5)): cyl('pole',cx,cy,0.1,0,5.0,'pole')
# axes
AXES=dict(reactor=((AXIS_X,-80),(AXIS_X,-13.75)), mine=((-8,MINE_Y),(-48,MINE_Y)))
