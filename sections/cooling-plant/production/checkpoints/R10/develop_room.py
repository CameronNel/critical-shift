"""Full-room Valorant construction pass; original geometry, no imported meshes."""
import bpy, math, bmesh
from math import pi, sin, cos
from mathutils import Vector
from kit import *

def wall_sign(name, label, p, width, height, size=.16, facing='front', mat='dark'):
    x,y,z=p; start=before()
    if facing=='front':
        box(name+' backing',(x,y,z),(width,.032,height),mat,.006)
        text(name+' lettering',label,(x,y-.018,z-size*.38),size,'paper')
        for dx in (-width/2+.055,width/2-.055):
            for dz in (-height/2+.045,height/2-.045):cyl(name+' fixing',(x+dx,y-.019,z+dz),.009,.012,'steel',(0,1,0),12,.001)
    else:
        box(name+' backing',(x,y,z),(.032,width,height),mat,.006)
        text(name+' lettering',label,(x-.018,y,z-size*.38),size,'paper',(pi/2,0,-pi/2))
    return start

def develop():
    scene=bpy.context.scene
    def attach(start,parent):
        for ob in list(scene.objects):
            if ob.name not in start and ob.parent is None:ob.parent=bpy.data.objects[parent]
    # Neutral motors and supports leave oxide only on cast pump bodies and selected covers.
    for ob in scene.objects:
        if ob.type not in ('MESH','CURVE','FONT'):continue
        if any(s in ob.name for s in ('induction motor','motor cast fin','end bell','terminal enclosure','separate pressed terminal lid','HX sculpted saddle','chain trolley','reserve isolator','reserve hinged','D02 recessed','D02 pressed')):
            ob.data.materials.clear();ob.data.materials.append(MAT['dark'])
        if 'HX bundle removable head' in ob.name or 'HX front dished head' in ob.name:
            ob.data.materials.clear();ob.data.materials.append(MAT['cream'])
        if ob.name.startswith(('HX primary inlet','HX cooled outlet','HX upper outlet','secondary water','secondary wall','secondary blue')):
            ob['envelope_role']='utility'
        if ob.name.startswith(('bundle pull I beam','bundle pull beam flange')):
            ob.data.materials.clear();ob.data.materials.append(MAT['yellow'])
    # Rounded feet join the motor through machined mounting flanges, with exposed bolts.
    for pname,yy in (('P-01',4.15),('P-02',7.6)):
        start=before()
        for yf in (yy-.36,yy+.36):
            box(pname+' motor mounting flange',(-2.65,yf,.61),(.72,.25,.065),'dark',.008)
            for xx in (-2.94,-2.38):
                cyl(pname+' motor mounting washer',(xx,yf,.652),.041,.018,'steel',verts=24,bevel=.002)
                cyl(pname+' motor mounting bolt',(xx,yf,.670),.027,.026,'edge',verts=6,bevel=.002)
        attach(start,pname)
    # Painted exchanger identification follows the cylinder, with no floating sign plate.
    start=before()
    label=text('HX painted shell ID','HX-01',(2.60,6.85,1.90),.26,'dark',(pi/2,0,-pi/2))
    label['authored_text']='HX-01';bpy.context.view_layer.objects.active=label;label.select_set(True)
    bpy.ops.object.convert(target='MESH');label=bpy.context.object
    bm=bmesh.new();bm.from_mesh(label.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=4,use_grid_fill=True);bm.to_mesh(label.data);bm.free()
    mw=label.matrix_world.copy();imw=mw.inverted()
    for vertex in label.data.vertices:
        v=mw@vertex.co;v.x=3.45-math.sqrt(max(.001,.82**2-(v.z-1.82)**2))-.002;vertex.co=imw@v
    label.select_set(False);attach(start,'HX-01 exchanger')
    # Cover lifting eyes and plugged inspection taps are connected to the exchanger shell.
    start=before()
    for yy in (5.65,8.00):
        box('HX lift pad',(3.45,yy,2.655),(.24,.26,.055),'steel',.006)
        torus('HX lifting eye',(3.45,yy,2.745),.075,.022,'steel',(0,1,0))
    for yy in (5.8,7.85):
        cyl('HX instrument boss',(3.0,yy,2.54),.061,.19,'steel')
        cyl('HX instrument plug',(3.0,yy,2.645),.040,.038,'edge',verts=6,bevel=.003)
    attach(start,'HX-01 exchanger')
    # Fill structural bay divisions with broad, intentionally quiet panel shapes.
    start=before()
    for x in (-4.65,-2.7,-.75,1.2,3.15,4.75):
        box('rear panel vertical joint',(x,12.992,3.45),(.012,.012,4.65),'dark',0)
    for z in (1.10,3.35):box('rear wall panel reveal',(0,12.987,z),(10.98,.026,.018),'dark',0)
    box('rear protective dado',(0,12.98,.55),(11,.038,1.10),'dark',.003)
    # High level ventilation with frame, radial fan, hub, guard and connected duct.
    box('extract fan wall gasket',(-.2,12.90,4.30),(1.25,.20,1.25),'dark',.015)
    box('extract fan steel frame',(-.2,12.78,4.30),(1.11,.10,1.11),'steel',.008)
    cyl('extract fan shadow',(-.2,12.71,4.30),.48,.055,'dark',(0,1,0),48)
    cyl('extract fan hub',(-.2,12.63,4.30),.12,.12,'steel',(0,1,0),32,.009)
    for i in range(7):
        a=i*2*pi/7
        v=[(-.2+.12*cos(a),12.66,4.30+.12*sin(a)),(-.2+.43*cos(a+.18),12.66,4.30+.43*sin(a+.18)),(-.2+.43*cos(a+.60),12.66,4.30+.43*sin(a+.60)),(-.2+.15*cos(a+.45),12.66,4.30+.15*sin(a+.45))]
        mesh('extract fan blade',v,[(0,1,2,3)],'steel',.003)
    for rad in (.22,.34,.47):torus('extract guard ring',(-.2,12.58,4.30),rad,.008,'dark',(0,1,0))
    for a in (0,pi/2):rod('extract guard stay',(-.2-.47*cos(a),12.58,4.30-.47*sin(a)),(-.2+.47*cos(a),12.58,4.30+.47*sin(a)),.009,'steel')
    group('rear panel and extract fixture',start,'RearWall',[[-.2,13,4.3]],(0,1,0))
    # Rear signage has its own wide backings and a consistent hierarchy.
    start=wall_sign('withdrawal instructions','HX-01  /  PULL-OUT BAY',(3.25,12.984,2.40),3.0,.38,.18)
    wall_sign('withdrawal clearance','3.5 m CLEAR  /  NO STORAGE',(3.25,12.984,1.96),3.0,.30,.135)
    group('withdrawal wall signage',start,'RearWall',[[3.25,13,2.40]],(0,1,0))
    start=wall_sign('workshop entrance identity','SERVICE',(-2.55,9.884,2.68),1.50,.38,.21)
    wall_sign('workshop door contract','CP-D02',(-2.55,9.884,2.35),1.05,.24,.12)
    group('workshop entry signs',start,'Alcove wall east',[[-2.55,9.90,2.68]],(0,1,0))
    # Panel frames, skirting and ceiling connect workshop visually to structural shell.
    start=before()
    box('workshop fascia',(-3.55,9.94,3.26),(3.90,.13,.15),'dark',.009)
    box('workshop side fascia',(-1.585,11.49,3.26),(.10,3.02,.15),'dark',.008)
    box('workshop side skirting',(-1.584,11.49,.13),(.03,3.02,.26),'dark',.004)
    architecture(start)
    # Cable ladder trays have side rails, rungs, hangers and real motor supply drops.
    start=before()
    for xx in (-4.65,-4.05):box('ladder tray side',(xx,6.45,4.66),(.045,12.2,.14),'steel',.004)
    for j in range(35):box('ladder tray rung',(-4.35,.5+j*.35,4.61),(.62,.034,.035),'dark',.003)
    for yy in (1.6,5.6,9.8,12.2):
        box('tray suspension crossbar',(-4.35,yy,4.56),(.78,.065,.055),'steel',.003)
        for xx in (-4.72,-3.98):rod('tray threaded hanger',(xx,yy,4.56),(xx,yy,5.8),.012,'steel')
    for xx in (-4.55,-4.43,-4.31):pipe('tray feeder cable',[(xx,.38,4.66),(xx,12.45,4.66)],.023,'rubber')
    for yy in (4.15,7.6):
        pipe('motor feeder drop',[(-4.55,yy+.52,4.66),(-5.30,yy+.52,4.66),(-5.30,yy+.52,.46),(-4.90,yy+.52,.46)],.025,'rubber',.15)
        for zz in (.75,2.2,3.7):box('motor drop cleat',(-5.31,yy+.52,zz),(.38,.10,.04),'steel',.003)
    group('electrical ladder and motor feeds',start,'Ceiling',[[-4.72,1.6,5.8],[-3.98,12.2,5.8]],(0,0,1))
    # Primary crossfeed hangs from the structure; it is not floating plumbing.
    start=before()
    for xx in (-3.0,-2.2,2.6):
        torus('crossfeed clamp',(xx,2.5,4.22),.155,.012,'steel',(1,0,0))
        rod('crossfeed threaded drop',(xx,2.5,4.385),(xx,2.5,5.8),.012,'steel')
    group('crossfeed supports',start,'Ceiling',[[-2.2,2.5,5.8],[2.6,2.5,5.8]],(0,0,1))
    # Hoist trolley uses paired cheekplates, four wheels and an axle connection.
    start=before()
    for xx in (3.20,3.70):
        box('hoist trolley cheek',(xx,10.15,4.69),(.06,.40,.35),'dark',.011)
        for yy in (10.04,10.26):
            cyl('hoist trolley axle',(xx,yy,4.77),.03,.14,'edge',(1,0,0),24,.003)
    rod('hoist suspension pin',(3.18,10.15,4.54),(3.72,10.15,4.54),.042,'edge')
    box('hoist gearbox',(3.45,10.15,4.37),(.35,.27,.36),'yellow',.025)
    attach(start,'HX dedicated hoist')
    # Floor guidance is paint at <=10mm; quiet continuous lanes and access limits.
    start=before()
    for xx in (-1.16,1.16):box('route worn edge continuous',(xx,6.65,.006),(.065,11.95,.002),'yellow',.001)
    for yy in (2.9,5.35,6.4,8.73):box('pump bay edge',(-3.45,yy,.007),(3.05,.045,.002),'yellow',.001)
    # Directional identity belongs on the wall; floor words reverse on the return route.
    for yy in (2.2,8.9):
        for side in (-1,1):
            ob=box('route arrow',(side*.13,yy,.008),(.07,.35,.002),'dark',.001);ob.rotation_euler.z=side*pi/4
    architecture(start)
    # Pump ID plates face the route; casing guards become broad punched metal.
    for pname,yy in (('P-01',4.15),('P-02',7.6)):
        start=before()
        wall_sign(pname+' aisle ID',pname,(-1.93,yy,.48),.65,.24,.14,'side')
        label=bpy.data.objects[pname+' aisle ID lettering'];label.location.x=-1.912;label.rotation_euler.z=pi/2
        box(pname+' ID bracket',(-2.04,yy,.41),(.22,.055,.19),'steel',.004)
        attach(start,pname)
        start=before()
        # Open cells are modeled between strips; the coupling stays serviceable.
        for j in range(10):
            a=.05+(pi-.10)*j/9
            for k in range(5):
                xx=-3.64+k*.12
                o=box(pname+' punched guard cross strip',(xx,yy+cos(a)*.247,.91+sin(a)*.247),(.035,.014,.070),'yellow',.002);o.rotation_euler.x=a
        for yfoot in (yy-.36,yy+.36):box(pname+' motor foot adapter',(-2.75,yfoot,.58),(.35,.18,.06),'dark',.006)
        attach(start,pname)
    # A full-size local status/control panel supports the gameplay functions.
    start=before()
    box('cooling controls wall plate',(-5.47,2.3,1.50),(.06,1.0,1.18),'steel',.009)
    box('cooling controls enclosure',(-5.29,2.3,1.50),(.32,.90,1.10),'dark',.015)
    # Display is made from native geometry/text and survives with no external textures.
    box('cooling status display',(-5.117,2.3,1.76),(.03,.75,.34),'cream',.005)
    text('cooling display text','FLOW  /  TEMP\nPRESSURE  /  PUMP',(-5.096,2.3,1.80),.055,'ink',(pi/2,0,pi/2))
    for yy in (2.05,2.30,2.55):
        cyl('local control switch',(-5.08,yy,1.28),.048,.08,'yellow',(1,0,0),24,.005)
    pipe('control cable conduit',[(-5.40,2.3,2.05),(-5.40,2.3,4.60),(-4.55,2.3,4.66)],.026,'dark',.10)
    group('local cooling controls',start,'WestWall',[[-5.5,2.3,1.50]],(-1,0,0))
    # Small wall tool board is purposefully placed over the existing workbench.
    start=before()
    box('service tool board',(-3.70,12.958,2.14),(2.40,.045,.82),'dark',.008)
    box('service tool board mounting spacer',(-3.70,12.99,2.14),(.12,.02,.12),'steel',.003)
    for i in range(5):
        xx=-4.60+i*.31
        cyl('tool board hanger',(xx,12.91,2.40),.014,.07,'steel',(0,1,0),12,.002)
        rod('hanging service wrench handle',(xx,12.90,2.35),(xx,12.90,1.98),.019,'steel')
        torus('hanging wrench ring',(xx,12.90,2.35),.043,.013,'edge',(0,1,0))
    group('workshop tool board',start,'RearWall',[[-3.7,13,2.14]],(0,1,0))
    # Clear, warm neutral light across the volume preserves Valorant readability.
    start=before()
    pipe('emergency secondary recovery branch',[(5.20,3.15,.78),(5.20,5.8,.78),(5.20,5.8,3.0)],.076,'steel',.14)
    for yy in (3.6,4.9):
        box('emergency branch wall pad',(5.479,yy,.72),(.042,.19,.24),'steel',.005)
        box('emergency branch support',(5.34,yy,.68),(.28,.06,.06),'steel',.004)
        torus('emergency branch clamp',(5.20,yy,.78),.085,.010,'steel',(0,1,0))
    group('emergency secondary backup branch',start,'EastWall',[[5.5,3.6,.72]],(1,0,0))
    start=before()
    pipe('contained drain collector',[(-1.58,10,-.10),(4.98,10,-.10),(5.5,10,-.10)],.055,'steel',.10)
    architecture(start)
    # Entry remains an unassembled boundary, clearly identified without invented corridor.
    start=before()
    box('entry connection sign backing',(0,.47,5.56),(3.80,.04,.32),'dark',.006)
    text('entry connection sign','CP-P01  /  REACTOR',(0,.494,5.49),.18,'paper',(pi/2,0,pi))
    box('entry sign spacer',(0,.435,5.56),(.18,.03,.12),'steel',.004)
    architecture(start)
    bpy.data.objects.remove(scene.objects['entry department'],do_unlink=True)
    start=before()
    box('entry eye height connection backing',(3.85,.335,2.25),(1.65,.055,.62),'dark',.008)
    text('entry eye height connection sign','CP-P01\nREACTOR',(3.85,.365,2.30),.18,'paper',(pi/2,0,pi))
    architecture(start)
    # Larger utility plates can be read from the operating apron.
    start=wall_sign('reserve operator instructions','RESERVE\nRESTART',(5.466,2.03,2.06),.80,.45,.11,'side')
    wall_sign('mine water instructions','BACKUP WATER',(5.466,3.35,2.10),1.10,.27,.11,'side')
    for yy,zz in ((2.03,2.0),(3.35,2.10)):box('utility sign mounting spacer',(5.491,yy,zz),(.018,.12,.12),'steel',.002)
    group('front utility signs',start,'EastWall',[[5.5,2.03,2.0]],(1,0,0))
    area('workshop lower service fill',(-2.95,11.05,2.5),(-3.8,12.6,.5),75,(1,.88,.71),1.0)
    start=before()
    box('bench underside work light',(-3.6,12.55,.878),(1.4,.055,.025),'lamp',.005)
    area('bench shelf practical',(-3.6,12.55,.854),(-3.6,12.55,.24),22,(1,.87,.67),.7)
    attach(start,'maintenance workbench')
    area('rear wall warm practical',(.6,11.9,4.2),(.6,12.98,2.0),180,(1,.79,.55),1.1)
    area('broad neutral ceiling fill',(0,6.3,5.25),(0,6.3,0),210,(.92,.93,1),4.0)
    for light in scene.objects:
        if light.type=='LIGHT' and any(t in light.name for t in ('pump task','lead pump','rear circulation')):
            light.data.color=(1,.83,.62)
    # Thin applied paint sits on the floor; it is not hovering plastic tape.
    for ob in scene.objects:
        if ob.name.startswith(('route worn edge','pump bay edge','route arrow','tube pull bay marking')):
            ob.location.z=.0006;ob.scale.z*=.5
        if ob.name in ('route floor identity','tube withdrawal floor label'):
            ob.location.z=.0007;ob.data.extrude=.0001
