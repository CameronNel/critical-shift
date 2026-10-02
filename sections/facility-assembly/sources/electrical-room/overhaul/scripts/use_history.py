"""Grounded safety/maintenance clusters, portal construction and selective use."""
import random
rng=random.Random(613)
k.collection('Service history and safety')
def ring_y(name,pos,w,h,thick,depth,mat):
    ob=k.ring(name,0,0,0,w,h,thick,depth,mat)
    ob.data.transform(Matrix.Translation(Vector(pos))@Matrix.Rotation(math.pi/2,4,'Z'))
    return ob
# A ray-cast in the R2 ceiling sliver hit no surface at the bevelled shell joint.
# Seated folded closure covers that join without moving the protected shell.
k.root('East ceiling joint closure','Ceiling',[[5.445,12.0,4.8],[5.445,15.8,4.8]],'WORLD_+Z')
k.box('Ceiling closure horizontal flange',(5.441,8.2,4.794),(.118,16.4,.012),m['enamel'],.001)
k.box('Ceiling closure vertical return',(5.488,8.2,4.755),(.024,16.4,.078),m['enamel'],.001)
for y in [2.5,5,8.5,12,14.5,15.8]:
    k.bolt('Ceiling closure captive fixing',(5.443,y,4.787),(0,0,-1),m['zinc'],.005)
# Wrap the existing wall finish into the portal ends, with folded impact liners.
for y,normal,suffix in [(0,1,''),(16.4,-1,'.002')]:
    for side in [-1,1]:
        target='Portal wall return'+(suffix if side<0 else ('.001' if y==0 else '.003'))
        k.root('Portal return finish '+str((y,side)),target,[[side*3.6,y,.8]],'WORLD_-Y' if y==0 else 'WORLD_+Y')
        for x in [side*2.30,side*3.58,side*4.86]:
            k.box('Portal mineral returned panel',(x,y+normal*.016,2.97),(1.256,.032,2.42),m['cream'],.003)
            k.box('Portal folded lower liner',(x,y+normal*.021,.85),(1.256,.042,1.48),m['slate'],.004)
            k.box('Portal liner seated cap',(x,y+normal*.04,1.605),(1.265,.080,.025),m['zinc'])
# A wall-mounted electrical rescue station, with actual clips and equipment.
k.root('Electrical rescue station','Portal wall return.001',[[3.06,0,.72],[4.85,0,.90]],'WORLD_-Y')
for x,z in [(3.06,.72),(3.06,1.56),(4.85,.90),(4.85,1.23)]:
    k.box('Rescue equipment mounting plate',(x,.055,z),(.13,.11,.18),m['slate'],.004)
    for zz in [z-.057,z+.057]:k.bolt('Rescue station anchor',(x,.113,zz),(0,1,0),m['zinc'],.009)
    k.tube('Rescue retaining clip',[(x-.045,.11,z),(x-.045,.23,z),(x+.045,.23,z),(x+.045,.11,z)],.011,m['zinc'])
k.tube('Insulating rescue pole',[(3.06,.18,.39),(3.06,.18,2.15),(3.12,.18,2.30),(3.30,.18,2.33),(3.43,.18,2.22),(3.42,.18,2.10)],.024,m['ochre'])
k.cyl('Rescue pole rubber grip',(3.06,.18,.44),(3.06,.18,.77),.030,m['rubber'])
for z in [.46,.52,.58,.64,.70,.76]:k.lathe('Rescue grip moulding',(3.06,.18,z),[(.031,0),(.031,.009),(.028,.009),(.028,0),(.031,0)],m['rubber'],24)
k.lathe('CO2 pressure bottle',(4.85,.23,.42),[(0,0),(.079,0),(.093,.027),(.096,.14),(.096,.65),(.090,.69),(.063,.74),(.022,.79),(0,.79)],m['oxide'],40)
k.lathe('Extinguisher printed sleeve',(4.85,.23,.67),[(.097,0),(.097,.21),(.094,.21),(.094,0),(.097,0)],m['paper'],40)
k.box('Bottle valve block',(4.85,.23,1.25),(.058,.044,.094),m['zinc'],.004)
k.tube('Extinguisher operating lever',[(4.82,.23,1.28),(4.76,.23,1.34),(4.94,.23,1.34)],.011,m['slate'])
k.tube('Bottle discharge hose',[(4.88,.23,1.27),(5.04,.23,1.24),(5.08,.23,.89),(5.04,.23,.80),(4.99,.23,.91)],.014,m['rubber'])
k.lathe('Discharge horn',(4.99,.23,.91),[(.017,0),(.019,.08),(.052,.21),(.056,.24),(.046,.24),(.012,.075),(.012,0),(.017,0)],m['rubber'],32)
k.lathe('Bottle safety pin ring',(4.90,.27,1.29),[(.027,-.004),(.027,.004),(.018,.004),(.018,-.004),(.027,-.004)],m['steel'],24,Matrix.Rotation(math.pi/2,3,'X'))
k.box('Rescue station equipment heading',(3.94,.052,2.59),(1.99,.062,.17),m['slate'],.005)
k.text('Rescue station heading','ELECTRICAL  /  RESCUE',(4.74,.088,2.551),.081,m['paper'],'Y')
# Clipped, dimensional maintenance records rather than a flat wall graphic.
k.box('Shift record backboard',(4.05,.049,1.94),(1.08,.066,.76),m['wood'],.007)
ring_y('Shift board folded frame',(4.05,.09,1.94),1.12,.80,.025,.025,m['zinc'])
for x in [3.81,4.30]:
    k.box('Inspection paper sheet',(x,.089,1.96),(.40,.004,.53),m['paper'],.001)
    k.box('Inspection spring clip',(x,.099,2.218),(.09,.014,.039),m['steel'],.003)
    for z in [1.76,1.82,1.88,1.94,2]:k.box('Inspection ruled row',(x,.093,z),(.31,.0015,.002),m['ink'],0)
k.text('Isolation shift record','SHIFT 06',(3.98,.095,2.098),.038,m['ink'],'Y')
k.text('Reserve inspection record','RESERVE TEST',(4.47,.095,2.098),.034,m['ink'],'Y')
k.text('Isolation record status','SERVICE / OPEN',(3.98,.095,2.022),.025,m['ink'],'Y')
k.text('Inspection time record','07:40   /   PASS',(4.47,.095,2.022),.027,m['ink'],'Y')
# A compact rear maintenance cluster: supported cable coils and stored runner.
k.root('Rear test lead storage','Portal wall return.003',[[3.5,16.4,1.55],[4.45,16.4,1.55]],'WORLD_+Y')
k.box('Lead storage folded backing',(4,16.365,1.55),(1.20,.070,.13),m['slate'],.006)
for x in [3.64,4.30]:
    k.tube('Lead reel hook',[(x,16.33,1.55),(x,16.10,1.55),(x,16.10,1.61)],.013,m['zinc'])
    path=[]
    for j in range(129):
        t=j/128;angle=t*math.tau*4;path.append((x+.205*math.sin(angle),16.08+t*.065,1.32+.205*math.cos(angle)))
    k.tube('Coiled test lead',path,.009,m['redrubber'] if x<4 else m['rubber'])
    k.tube('Test lead hanging tail',[path[-1],(x+.10,16.10,1.05),(x+.06,16.10,.90)],.009,m['rubber'])
    k.cyl('Lead terminal insulated grip',(x+.06,16.10,.90),(x+.06,16.10,.80),.016,m['ochre'])
    k.cyl('Lead exposed contact pin',(x+.06,16.10,.80),(x+.06,16.10,.77),.006,m['zinc'])
k.root('Stored insulating runner','Floor',[[3.62,15.88,0],[4.58,15.88,0],[3.62,16.15,0],[4.58,16.15,0]])
roll_z=.30;roll_y=16.03
# Purpose-built pressed-steel floor cradle: four seated feet, returned cheeks,
# core axle and pinned end stops make storage clear even in the route overview.
for x in [3.62,4.58]:
    for y in [15.88,16.15]:
        k.box('Mat cradle rubber foot',(x,y,.008),(.12,.11,.016),m['rubber'],.003)
        k.box('Mat cradle pressed shoe',(x,y,.024),(.12,.11,.016),m['zinc'],.002)
    k.tube('Mat cradle folded support',[(x,15.88,.032),(x,15.88,.15),(x,16.00,.28),(x,16.06,.28),(x,16.15,.15),(x,16.15,.032)],.018,m['zinc'])
    k.lathe('Mat cradle axle boss',(x,roll_y,roll_z),[(0,-.023),(.055,-.023),(.055,.023),(0,.023)],m['slate'],32,Matrix.Rotation(math.pi/2,3,'Y'))
    k.bolt('Mat cradle axle keeper',(x+(-.029 if x<4 else .029),roll_y,roll_z),(-1 if x<4 else 1,0,0),m['zinc'],.017)
k.cyl('Runner seated core axle',(3.60,roll_y,roll_z),(4.60,roll_y,roll_z),.026,m['zinc'])
k.lathe('Runner hollow core spindle',(3.64,roll_y,roll_z),[(.073,0),(.073,.92),(.027,.92),(.027,0),(.073,0)],m['zinc'],40,Matrix.Rotation(math.pi/2,3,'Y'))
k.lathe('Rolled insulating runner',(3.67,roll_y,roll_z),[(.16,0),(.16,.86),(.073,.86),(.073,0),(.16,0)],m['rubber'],48,Matrix.Rotation(math.pi/2,3,'Y'))
# Layered exposed roll edges distinguish a rubber runner from a solid drum.
for x in [3.671,4.529]:
    for rad in [.087,.105,.124,.143]:
        k.lathe('Runner layered edge',(x,roll_y,roll_z),[(rad-.0015,-.002),(rad+.0015,-.002),(rad+.0015,.002),(rad-.0015,.002),(rad-.0015,-.002)],m['cloth'],40,Matrix.Rotation(math.pi/2,3,'Y'))
for x in [3.87,4.32]:
    k.lathe('Runner retaining fabric band',(x,roll_y,roll_z),[(.163,0),(.163,.035),(.159,.035),(.159,0),(.163,0)],m['cloth'],40,Matrix.Rotation(math.pi/2,3,'Y'))
    k.box('Runner strap buckle',(x+.017,15.864,roll_z),(.042,.008,.047),m['zinc'],.002)
k.tube('Mat cradle front cross brace',[(3.62,15.88,.104),(3.62,15.852,.104),(4.58,15.852,.104),(4.58,15.88,.104)],.012,m['zinc'])
k.box('Mat cradle folded front lip',(4.10,15.843,.104),(1.05,.018,.126),m['slate'],.003)
k.box('Insulating mat storage label',(4.10,15.832,.104),(.74,.004,.083),m['paper'],.001)
k.text('Runner storage purpose','INSULATING MAT',(3.784,15.828,.086),.044,m['ink'],'-Y')
# Broad material zoning at the equipment margins keeps the central aisle quiet.
service_floor=k.material('Coarse service epoxy',(.15,.174,.187),.89,0,.0008)
k.root('Service approach floor','Floor',[[2.0,5.0,0],[-2.0,6.0,0]])
for side in [-1,1]:
    for j in range(8):
        y=3.0+j*1.15
        for x in [side*1.61,side*2.42,side*3.23]:
            k.box('Service zone epoxy panel',(x,y,.00065),(.798,1.138,.0013),service_floor,.0003)
# Trolley arcs and intermittent foot/contact scuffs cluster at work positions.
k.root('Trolley and service floor history','Floor',[[-3.4,2.6,0],[2.05,8.25,0]])
wear=k.material('Floor contact history',(.155,.16,.146),.93,0,.0002)
for x,y in [(-3.4,2.6),(2.05,8.25)]:
    k.box('Measured service contact mark',(x,y,.0018),(.014,.10,.0004),wear,0)
for cx,cy in [(-3.4,2.6),(2.05,8.25),(-1.42,12.6),(1.40,14.8)]:
    for j in range(8):
        x=cx+rng.uniform(-.17,.17);y=cy+rng.uniform(-.28,.28)
        k.box('Localized footwear contact',(x,y,.0018),(.008+rng.random()*.006,.07+rng.random()*.17,.0004),wear,0,Matrix.Rotation(rng.uniform(-.3,.3),3,'Z'))
for dx in [0,.24]:
    path=[(-3.4+dx+.19*math.sin(i*.1),2.50+.19*math.cos(i*.1),.0017) for i in range(13)]
    k.tube('Trolley turning wear',path,.0006,wear)
