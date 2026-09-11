"""Original full hall assemblies. Metres; no imported models or textures."""
import math,json,hashlib
import bpy

def build_hall(a):
    box,cyl,beam,pipe,torus,text=a.box,a.cyl,a.beam,a.pipe,a.torus,a.text
    def pipe(n,points,r,m):
        o=a.pipe(n,points,r,m)
        for sp in o.data.splines:
            for bp in sp.bezier_points: bp.handle_left_type='VECTOR';bp.handle_right_type='VECTOR'
        return o
    a.group('02 Turbine train')
    def marker(n,p,kind):
        o=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(o);o.location=p;o['handoff']=kind;return o
    def foot(n,x,y,z=.45,top=1.6,w=.7):
        box(n+' soleplate',(x,y,z+.045),(w+.22,.75,.09),'darkteal',.01)
        a.extrude_profile(n+' tapered casting',[(x-w/2,z+.09),(x+w/2,z+.09),(x+w*.29,top),(x-w*.29,top)],y-.25,y+.25,'darkteal',.015)
        for dx in [-w*.43,w*.43]:
            for dy in [-.29,.29]:a.bolt(n+' anchor',(x+dx,y+dy,z+.10),r=.031)
    def flange(n,y,r,mat='cream',x=4.6,z=2):
        cyl(n,(x,y,z),r,.10,mat,'Y',64,.009)
        for i in range(16):
            t=i*math.tau/16;a.bolt(n+' stud',(x+(r-.07)*math.cos(t),y-.065,z+(r-.07)*math.sin(t)),'Y',.031)
    def casing(n,y0,y1,r0,r1):
        # Two individually removable half-castings; broad faceted crown, split seam.
        N=32
        for upper in [False,True]:
            verts=[]
            for y,r in [(y0,r0),(y1,r1)]:
                for i in range(N+1):
                    t=(0 if upper else math.pi)+math.pi*i/N
                    verts.append((4.6+r*math.cos(t),y,2+r*math.sin(t)+( .012 if upper else -.012)))
            faces=[tuple(range(N,-1,-1)),tuple(range(N+1,2*N+2))]+[(i,i+1,i+N+2,i+N+1) for i in range(N)]+[(0,N+1,2*N+1,N)]
            a.mesh(n+(' upper removable' if upper else ' lower casting'),verts,faces,'teal' if n=='HP01' else 'cream',.009)
        for side in [-1,1]:
            xs=[4.6+side*(r0+.055),4.6+side*(r1+.055)]
            a.mesh(n+' split flange',[(xs[0]- .12,y0,1.91),(xs[0]+.12,y0,1.91),(xs[1]+.12,y1,1.91),(xs[1]-.12,y1,1.91),(xs[0]-.12,y0,2.09),(xs[0]+.12,y0,2.09),(xs[1]+.12,y1,2.09),(xs[1]-.12,y1,2.09)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'cream',.008)
            count=max(3,int((y1-y0)/.3))
            for i in range(count):
                f=(i+.5)/count;a.bolt(n+' split bolt',(xs[0]*(1-f)+xs[1]*f,y0+(y1-y0)*f,2.105),r=.033)
    box('TRAIN foundation',(4.6,12.75,.205),(4.2,14.5,.41),'concrete',.03)
    box('TRAIN grout bed',(4.6,12.75,.43),(4.08,14.38,.04),'dark',.003)
    for y in [6,8.35,10.55,12.35,14.4,16.55,18.7]:
        box('Foundation construction joint',(4.6,y,.412),(4.15,.014,.004),'dark',0)
    casing('HP01',6.02,8.35,.80,.80);casing('HP LP transition',8.39,8.90,.80,1.35)
    casing('LP01 expansion',8.94,10.55,1.35,1.50);casing('LP01 exhaust',10.59,12.35,1.5,1.5)
    for y,r in [(6.02,.88),(8.36,.88),(8.92,1.43),(10.57,1.58),(12.36,1.58)]:flange('Turbine axial flange',y,r)
    # Full exhaust cross-section drops within foundation; no tiny condensate tube masquerading as steam exhaust.
    box('LP exhaust downhood',(4.6,11.45,.95),(2.65,1.7,1.2),'cream',.14)
    box('LP exhaust pit flange',(4.6,11.45,.48),(2.95,1.95,.12),'darkteal',.014)
    marker('IF_LP_EXHAUST_CONDENSER',(4.6,11.45,0),'2.5 x 1.5m downward steam exhaust; underfloor condenser module unresolved, no runtime thermodynamics')
    for y,r in [(6.55,.8),(8.0,.8),(9.4,1.4),(11.9,1.5)]:
        for side in [-1,1]:foot('Turbine casting foot',4.6+side*(r*.68),y,top=1.6)
    for y,r in [(7.2,.8),(9.6,1.4),(11.6,1.5)]:
        for dx in [-.42,.42]:
            z=2+math.sqrt(r*r-dx*dx)
            box('Lift lug foot',(4.6+dx,y,z),(.24,.27,.07),'cream',.015)
            torus('Rated lifting eye',(4.6+dx,y,z+.12),.095,.031,'darkteal','Y')
    for y in [5.76,12.82,14.22,19.05]:
        foot('Journal bearing pedestal',4.6,y,top=1.87,w=.8)
        cyl('Journal bearing housing',(4.6,y,2),.32,.32,'darkteal','Y',48,.018)
        flange('Journal end seal',y-.18,.24,'steel')
        cyl('Lubricator stem',(4.6,y,2.36),.045,.15,'steel')
        cyl('Lubricator cap',(4.6,y,2.44),.07,.04,'yellow')
    cyl('ANIM_TURBINE_SHAFT',(4.6,12.55,2),.11,13.0,'steel','Y')
    for y in [5.94,12.55,14.38,18.78]:cyl('Labyrinth gland',(4.6,y,2),.21,.15,'dark','Y')
    a.group('03 Generator and coupling')
    cyl('Generator stator body',(4.6,16.55,2),1.10,4.3,'darkteal','Y',64,.03)
    for y in [14.42,18.68]:
        flange('Generator end ring',y,1.19,'darkteal')
        # Circular vent field backed by dark body; slats terminate at ring radius.
        for z in [1.1+i*.13 for i in range(15)]:
            half=math.sqrt(max(0,1.03**2-(z-2)**2))
            box('Generator end vent louver',(4.6,y+(-.063 if y<16 else .063),z),(2*half,.055,.045),'steel',.004)
    for y in [14.85,18.15]:
        for dx in [-.72,.72]:foot('Generator foot',4.6+dx,y,top=1.4)
    # Broad folded jacket panels with axial cooling fins, rather than stacked primitive rings.
    for side in [-1,1]:
        box('Generator removable side jacket',(4.6+side*1.01,16.55,2),(.16,3.8,1.25),'cream',.09)
        for z in [1.48+i*.13 for i in range(9)]:box('Generator cooling fin',(4.6+side*1.13,16.55,z),(.10,3.74,.046),'cream',.007)
        for y in [15.1,18.0]:
            box('Generator service hatch',(4.6+side*1.19,y,2),(.035,.56,.42),'cream',.016)
            for dy in [-.22,.22]:
                for z in [1.85,2.15]:a.bolt('Jacket hatch fixing',(4.6+side*1.215,y+dy,z),'X',.014)
        for y in [15.0,18.1]:torus('Generator lifting eye',(4.6+side*.53,y,3.02),.09,.028,'red','Y')
    for x in [4.1+i*.13 for i in range(9)]:box('Generator roof cooling fin',(x,16.55,3.09),(.045,3.76,.12),'cream',.005)
    # Cage consists of actual rails with open gaps and anchored ends.
    for y in [13.04,13.98]:
        for dx in [-.47,.47]:box('Coupling guard mounting foot',(4.6+dx,y,.53),(.16,.19,.16),'yellow',.006)
        box('Coupling guard lower frame',(4.6,y,1.31),(1.05,.06,.06),'yellow')
        for dx in [-.50,.50]:box('Coupling guard upright',(4.6+dx,y,1.94),(.045,.055,1.2),'yellow')
        # skirt supports reach anchored feet
        for dx in [-.47,.47]:box('Coupling guard leg',(4.6+dx,y,.94),(.07,.08,.68),'darkteal')
        for i in range(13):
            t=math.pi*i/12;tor=None
            if i<12:
                t2=math.pi*(i+1)/12;beam('Guard arch',(4.6+.5*math.cos(t),y,2.0+.5*math.sin(t)),(4.6+.5*math.cos(t2),y,2.0+.5*math.sin(t2)),.025,'yellow')
    for i in range(23):
        t=math.pi*i/22;beam('Guard longitudinal mesh',(4.6+.5*math.cos(t),13.04,2+.5*math.sin(t)),(4.6+.5*math.cos(t),13.98,2+.5*math.sin(t)),.009,'yellow')
    for y in [13.1+i*.075 for i in range(12)]:
        for side in [-1,1]:beam('Guard side mesh',(4.6+side*.5,y,1.34),(4.6+side*.5,y,2),.007,'yellow')
    for y in [13.3,13.65]:flange('Flexible coupling hub',y,.24,'steel')
    box('Coupling identification plate',(5.115,13.52,1.65),(.025,.65,.24),'darkteal',.005)
    text('Coupling label','GUARD  /  01',(5.132,13.52,1.59),.072,face='E',align='CENTER')
    a.group('04 Process and power services')
    # Steam trunk kept east of lift volume; branch enters HP side.
    pipe('Steam insulated trunk',[(8.4,0,4.9),(8.4,6.55,4.9),(6.45,7.2,4.9),(6.45,7.2,2.65),(6.2,7.2,2.15),(5.3,7.2,2.15)],.20,'cream')
    for y in [1.2,3.8,6.2]:
        torus('Steam jacket band',(8.4,y,4.9),.205,.014,'steel','Y')
        box('Steam hanger crossbar',(8.4,y,4.64),(.65,.14,.10),'darkteal')
        for dx in [-.27,.27]:beam('Steam suspended rod',(8.4+dx,y,4.69),(8.4+dx,y,7.2),.017,'steel')
    for x in [5.8,6.15]:
        cyl('Steam branch flange',(x,7.2,2.15),.29,.09,'steel','X')
        for i in range(8):
            t=i*math.tau/8;a.bolt('Steam flange bolt',(x-.06,7.2+.23*math.cos(t),2.15+.23*math.sin(t)),'X',.023)
    box('Steam support base',(6.45,7.2,.06),(.62,.62,.12),'darkteal')
    beam('Steam support column',(6.45,7.2,.12),(6.45,7.2,1.94),.075,'darkteal')
    cyl('Steam shutoff bonnet',(6.05,7.2,2.49),.14,.46,'darkteal')
    cyl('Steam valve stem',(6.05,7.2,2.85),.035,.32,'steel')
    torus('Steam isolation handwheel',(6.05,7.2,3.03),.23,.025,'red')
    for t in [0,math.pi/2,math.pi,math.pi*1.5]:beam('Valve wheel spoke',(6.05,7.2,3.03),(6.05+.22*math.cos(t),7.2+.22*math.sin(t),3.03),.016,'red')
    # Bearings have connected supply and return pipes; compact oil cabinet stays on skid.
    box('Bearing oil service cabinet',(2.92,12.72,1.01),(.72,1.0,1.12),'darkteal',.045)
    box('Oil cabinet access panel',(2.545,12.72,1.03),(.025,.83,.83),'red',.012)
    text('Oil cabinet title','LUBE / 01',(2.531,12.72,1.34),.105,face='W',align='CENTER')
    for z in [.61,.70]:
        pipe('Oil main header',[(3.05,12.7,z),(3.05,6,z),(4.6,6,z)],.025,'steel')
        pipe('Oil generator header',[(3.05,12.7,z),(3.05,19.05,z),(4.6,19.05,z)],.025,'steel')
    for y in [5.76,12.82,14.22,19.05]:
        pipe('Journal feed',[(3.05,y,.7),(4.15,y,.7),(4.15,y,1.9),(4.33,y,2)],.018,'steel')
        pipe('Journal return',[(4.6,y,1.7),(4.6,y,.61),(3.05,y,.61)],.022,'dark')
    box('Generator terminal housing',(5.22,18.1,2.98),(.85,.65,.65),'darkteal',.045)
    for y in [17.9,18.1,18.3]:pipe('Flexible terminal lead',[(5.3,y,3.2),(5.6,y,3.5),(5.6,y,4.42)],.044,'rubber')
    # Outgoing bus shifts west above circulation to align latest Electrical U01 x=-4.32 z3.88.
    for n,p,d in [('riser',(5.6,18.1,4.15),(.40,.65,.9)),('cross',(1.3,18.1,4.48),(9.0,.40,.3)),('north',(-3.2,21.65,4.48),(.4,7.1,.3)),('adapter',(-3.76,25.2,4.48),(1.52,.4,.3))]:box('Bus '+n,p,d,'darkteal',.022)
    for x in [-2.6,0,2.6,5.4]:
        box('Bus suspension shoe',(x,18.1,4.26),(.22,.65,.08),'steel')
        for dy in [-.25,.25]:beam('Bus suspension rod',(x,18.1+dy,4.3),(x,18.1+dy,7.2),.012,'steel')
    for y in [20,23]:
        box('Bus wall bracket',(-3.60,y,4.26),(.90,.15,.08),'steel')
        beam('Bus bracket brace',(-3.97,y,3.9),(-3.2,y,4.26),.025,'steel')
    a.group('06 Operator controls')
    for y in [9.3,10.35,11.4]:
        box('Control pedestal',(-3.36,y,.51),(.88,.96,1.02),'darkteal',.025)
        box('Control instrument face',(-2.905,y,1.40),(.12,.96,.72),'cream',.018)
        box('Control work ledge',(-2.86,y,1.04),(.40,.97,.09),'darkteal',.015)
    for y,label,value in [(9.08,'SPEED','SYNC'),(9.53,'HEALTH','READY'),(10.12,'OUTPUT','MATCH'),(10.57,'DEMAND','STEADY'),(11.18,'RESERVE','SHARED'),(11.62,'SAFETY','ARMED')]:
        box('Instrument bezel',(-2.831,y,1.44),(.04,.37,.38),'dark',.01)
        text('Instrument heading '+label,label,(-2.841,y,1.70),.073,mat='ink',face='E',align='CENTER')
        text('Instrument readout '+label,value,(-2.809,y,1.42),.065,mat='screen',face='E',align='CENTER')
        for dz in [1.33,1.36]:box('Readout scale',(-2.809,y,dz),(.005,.24,.006),'white',0)
    for y,label in [(9.30,'THROTTLE'),(10.35,'LOAD')]:
        cyl(label+' spindle',(-2.73,y,1.13),.05,.13,'steel')
        beam(label+' lever',(-2.73,y,1.18),(-2.67,y+.16,1.31),.022,'dark')
        cyl(label+' grip',(-2.67,y+.16,1.32),.034,.10,'rubber','Y')
        text(label+' label',label,(-2.84,y-.31,1.086),.064,mat='white',face='UP')
    cyl('Emergency trip mushroom',(-2.71,11.4,1.13),.066,.10,'red')
    text('Emergency trip label','TRIP',(-2.84,11.12,1.086),.085,face='UP')
    # Human-readable headings fit shared backing, no individual text shrink to dodge structure.
    for y,title in [(10.25,'TURBINE CONTROL'),(21.3,'MAINTENANCE / 02')]:
        box('West title backing',(-3.50,y,2.85),(.08,3.1,.44),'darkteal')
        text('West title '+title,title,(-3.454,y,2.76),.18,face='E',align='CENTER')
        for dy in [-1.25,1.25]:beam('West sign standoff',(-4,y+dy,2.85),(-3.54,y+dy,2.85),.025,'darkteal')
    for y in [9.3,10.35,11.4]:
        pipe('Controls power conduit',[(-3.4,y,.3),(-3.88,y,.3),(-3.88,y,3.5)],.022,'dark')
    pipe('Control cable trunk',[(-3.88,8.8,3.5),(-3.88,12,3.5),(-3.88,18.1,3.5),(-3.2,18.1,4.35)],.035,'darkteal')
    a.group('07 Hoist and architectural finish')
    # Fixed longitudinal monorail; casing lift corridor below it remains unobstructed.
    box('Hoist rail web',(4.6,12.9,5.94),(.12,15.3,.45),'yellow')
    for z in [5.7,6.18]:box('Hoist rail flange',(4.6,12.9,z),(.42,15.3,.06),'yellow')
    for y in [6,11,16,21]:
        for x in [4.46,4.74]:beam('Hoist roof hanger',(x,y,6.2),(x,y,6.4),.035,'steel')
        box('Hoist girder cleat',(4.6,y,6.38),(.7,.48,.08),'darkteal')
    box('Hoist travelling trolley',(4.6,19.6,5.53),(.75,.65,.24),'darkteal',.025)
    for x in [4.40,4.80]:
        for y in [19.37,19.83]:cyl('Hoist trolley wheel',(x,y,5.80),.09,.14,'steel','X')
    box('Hoist motor housing',(4.6,19.6,5.23),(.58,.55,.42),'yellow',.045)
    for x in [4.52,4.68]:beam('Hoist chain',(x,19.6,5.06),(x,19.6,4.27),.012,'dark')
    torus('Hoist hook',(4.6,19.6,4.18),.10,.025,'steel','Y')
    for x in [-3.97,9.97]:
        for z in [2.4,4.0,6.4]:box('Wall panel horizontal reveal',(x,12,z),(.016,23.5,.018),'dark',0)
        for y in [3.5,8.5,13.5,18.5]:box('Wall panel vertical reveal',(x,y,3.55),(.016,.016,5.15),'dark',0)
        box('Wall oxide datum',(x,12,3.8),(.018,23.5,.14),'red',0)
    # Warm wall pools and high diffuse fill, no teal or theatrical coloured fog.
    for y in [3,8,13,18,23]:
        box('West wall lamp back',(-3.94,y,4.1),(.10,.4,.5),'darkteal',.015)
        box('West wall lamp lens',(-3.87,y,4.05),(.045,.29,.25),'lamp',.009)
        a.light('Wall light pool',(-3.76,y,4.05),(-2.2,y,1.0),130,(1,.90,.76),.5)
    a.light('Hall broad daylight',(9.55,10.5,5.4),(3,10,1),1800,(.91,.95,1),5)
    a.light('Entry broad fill',(1,1,5.6),(4.6,8,1.8),800,(1,.94,.83),4)
    for name,p,kind in [
        ('IF_PORTAL_D01_REACTOR',(0,0,0),'2.4x2.7m outward -Y; proposed main-access connector'),
        ('IF_PORTAL_D02_ELECTRICAL',(0,24,0),'2.4x2.7m outward +Y; owned reveal to25.2'),
        ('IF_STEAM_IN_REACTOR',(8.4,0,4.9),'nominal diameter .4m outward -Y; unbound'),
        ('IF_POWER_OUT_ELECTRICAL',(-4.32,25.2,4.48),'bus adapter requires .60m drop to Electrical3.88'),
        ('INTERACT_TURBINE_THROTTLE',(-2.67,9.46,1.31),'host-authoritative admission request'),
        ('INTERACT_TURBINE_LOAD',(-2.67,10.51,1.31),'host-authoritative load request'),
        ('INTERACT_OVERSPEED_TRIP',(-2.71,11.4,1.16),'trip and disconnect request'),
        ('INTERACT_BEARING_OIL_SERVICE',(2.52,12.72,1.03),'repair/oil service'),
        ('INTERACT_TURBINE_REPAIR',(-2.62,21.2,1.02),'component repair'),
        ('AUDIO_TRAIN_RUNNING',(4.6,11.5,2),'idle/start/running/stressed/warning/trip/repair'),
        ('HOOK_SHARED_RESERVE',(-2.8,11.18,1.44),'display shared Electrical reserve; no duplicate battery pool'),
        ('FAULT_STEAM_LEAK',(6,7.2,2.15),'actual inlet flange'),
        ('FAULT_BEARING_OIL',(4.6,12.82,2),'actual bearing')]:marker(name,p,kind)
    a.group('08 Graphic finish and service fittings')
    # Original large graphic fields: painted on quiet planes, not photoreal grunge.
    for x,face in [(-3.976,'E'),(9.976,'W')]:
        for y in [4.6,15.7]:
            a.mesh('Wall diagonal oxide field',[(x,y-1.2,1.3),(x,y-.55,1.3),(x,y+1.2,3.65),(x,y+.55,3.65)],[(0,1,2,3)],'teal')
    for y,r in [(7.3,.8),(9.8,1.43),(11.6,1.5)]:
        x=4.6-r-.025
        box('Turbine inspection pad',(x,y,2.0),(.08,.8,.62),'darkteal',.035)
        box('Turbine removable inspection hatch',(x-.045,y,2.0),(.045,.69,.50),'teal',.035)
        for dy in [-.27,.27]:
            for z in [1.82,2.18]:a.bolt('Inspection hatch fastener',(x-.075,y+dy,z),'X',.024)
        text('Turbine identification','HP / 01' if y<8 else 'LP / 01',(x-.070,y,1.96),.105,face='W',align='CENTER')
    # Folded angular roof and side covers establish the generator's larger silhouette.
    for side in [-1,1]:
        a.extrude_profile('Generator shoulder jacket',[(4.6+side*.52,3.14),(4.6+side*.80,3.14),(4.6+side*1.18,2.78),(4.6+side*1.18,2.63)],14.69,18.40,'cream',.015)
        box("Generator graphic service cover",(4.6+side*1.165,16.5,2.05),(.075,2.25,1.20),"cream",.018)
        x=4.6+side*1.205
        a.mesh('Generator oxide stripe',[(x,15.5,1.46),(x,16.0,1.46),(x,17.5,2.65),(x,17.0,2.65)],[(0,1,2,3)],'teal')
    for y in [9.3,10.35,11.4]:
        box('Control cabinet service door',(-2.91,y,.51),(.032,.79,.77),'dark',.018)
        box('Control cabinet orange datum',(-2.89,y,.78),(.015,.76,.10),'teal',.004)
        box('Control cabinet latch',(-2.879,y+.29,.57),(.025,.03,.11),'steel',.004)
        for dy in [-.34,.34]:
            for z in [.18,.85]:a.bolt('Control panel fixing',(-2.881,y+dy,z),'X',.012)
        for dz in [.24,.30,.36]:box('Control ventilation slot',(-2.89,y,dz),(.01,.44,.023),'rubber',.002)
    for y in [6,8,10,12,14,16,18,19.2]:
        box('Oil header clamp',(3.05,y,.65),(.12,.06,.19),'darkteal',.004)
        box('Oil header clamp foot',(3.05,y,.49),(.24,.15,.08),'darkteal',.005)
    # Remaining liquid return service has an explicit blind flange at the unfinished condenser connection.
    pipe('Condensate wall return',[(9.5,0,.45),(9.5,12.6,.45)],.10,'steel')
    cyl('Condensate boundary flange',(9.5,12.6,.45),.16,.055,'darkteal','Y')
    for y in [1.3,4.2,8.1,12.3]:
        box('Condensate pipe shoe',(9.5,y,.20),(.30,.18,.40),'darkteal',.007)
        torus('Condensate clamp',(9.5,y,.45),.11,.012,'steel','Y')
    marker('IF_CONDENSATE_RETURN',(9.5,0,.45),'diameter .2m liquid return outward -Y; blind terminated waiting for underfloor condenser design')
    box('Bus adapter drop',(-4.32,25.00,4.18),(.4,.4,.90),'darkteal',.018)
    box('Bus adapter mating end',(-4.32,25.10,3.88),(.4,.20,.3),'darkteal',.018)
    bpy.data.objects['IF_POWER_OUT_ELECTRICAL'].location=(-4.32,25.2,3.88)
    bpy.data.objects['IF_POWER_OUT_ELECTRICAL']['handoff']='.4 x .3m +Y mating face; same x/z as Electrical U01; connector translation still provisional'
    # Close the cage lower edge and attach its side wires to a continuous rail.
    for x in [4.1,5.1]:box('Guard lower longitudinal rail',(x,13.51,1.33),(.045,.99,.055),'yellow',.005)
    for x in [4.40,4.80]:
        for y in [19.37,19.83]:
            box('Hoist axle cheek',(x,y,5.69),(.09,.14,.30),'darkteal',.009)
            cyl('Hoist axle',(x,y,5.80),.032,.22,'steel','X')
    # Backing connection replaces a detached clamp rather than relaxing contact tolerance.
    for ob in list(a.S.objects):
        if ob.name.startswith('Oil header clamp foot'):ob.dimensions.z=.15;ob.location.z=.525
    box('D01 inside route sign',(0,.32,3.18),(2.55,.06,.34),'darkteal',.006)
    text('D01 inside legend','REACTOR / D01',(0,.352,3.09),.19,face='N',align='CENTER')
    beam('D01 inside sign bracket',(0,.16,3.18),(0,.30,3.18),.03,'darkteal')
    box('D01 inside sign mounting pad',(0,.24,3.18),(.2,.08,.18),'darkteal')
    # Physical button guard, terminal and local fault readback.
    torus('Trip protective collar',(-2.71,11.4,1.107),.083,.013,'yellow')
    for y in [9.08,9.53,10.12,10.57,11.18,11.62]:
        cyl('Instrument status lens',(-2.81,y,1.55),.021,.012,'yellow','X',24)
    for y in [7.3,9.8,11.6]:
        x=3.72 if y<8 else (3.095 if y>11 else 3.165)
        box('Casing service witness mark',(x,y+.20,1.90),(.005,.085,.016),'steel',0)
    # Sparse painted mineral variation on broad fields, no dense photographic grunge.
    for key,low,high in [('floor',.70,.89),('cream',.64,.82),('concrete',.81,.94)]:
        mat=a.M[key];nd=mat.node_tree.nodes;lk=mat.node_tree.links;bs=nd.get('Principled BSDF')
        tex=nd.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=6;tex.inputs['Detail'].default_value=1
        co=nd.new('ShaderNodeTexCoord');lk.new(co.outputs['Generated'],tex.inputs['Vector'])
        ramp=nd.new('ShaderNodeMapRange');ramp.inputs['To Min'].default_value=low;ramp.inputs['To Max'].default_value=high
        lk.new(tex.outputs['Fac'],ramp.inputs['Value']);lk.new(ramp.outputs['Result'],bs.inputs['Roughness'])
    a.S['machine_contract']=json.dumps({'axis_point':[4.6,0,2],'axis_direction':[0,1,0],'shaft_objects':['ANIM_TURBINE_SHAFT'],'centered_objects':['Generator stator body','HP01 upper removable','LP01 exhaust upper removable'],'mirror_pairs':[]})
    a.S['integration_scope']='Complete visible turbine hall; condenser below floor and reciprocal facility connectors unassembled; engine hooks only'
