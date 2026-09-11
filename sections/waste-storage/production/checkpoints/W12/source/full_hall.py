"""Original full Waste Storage geometry, executed in builder namespace."""
M['floor']=material('Dry charcoal ground concrete','777368',.94,0,.035,0)
M['wall']=material('Warm architectural concrete','BCB5A4',.91,0,.035,0)
M['pale']=material('Ivory industrial enamel','C7C1AB',.73,.10,.035,0)
M['paint']=material('Oxide painted steel','AC633E',.72,.1,.04,0)
M['wood']=material('Used bench plywood','928064',.87,0,.04,0)

def root(name,loc,rot=0):
    return assembly(name,loc,rot,'Floor',[[0,0,0]],[0,0,-1])

def bolts_circle(parent,z,r,n=12):
    for j in range(n):
        a=j*math.tau/n;cyl('Captive lid bolt',(r*math.cos(a),r*math.sin(a),z),.022,.045,'metal',parent,vertices=6)

def cask(name,loc,tall=False,rot=0):
    global current
    current='Casks';p=root(name,loc,rot);p['equipment_type']='shielded_cask' if tall else 'residue_overpack';p['capacity_state']='sealed';p['interaction']='inspect_seal;scan;unlock;transfer';p['incident']='seal_damage;contamination;unregistered_waste'
    r=.57 if tall else .43;h=2.30 if tall else 1.30
    for x in [-r*.70,r*.70]:
        box('Fork skid runner',(x,0,.08),(.16,r*2+.15,.16),'darkpaint',p,.014)
    box('Carrier bearing plate',(0,0,.20),(r*2+.20,r*2+.2,.09),'metal',p,.024)
    cyl('Sealed vessel lower shoulder',(0,0,.33),r,.20,'darkpaint',p)
    cyl('Continuous inner vessel',(0,0,(h+.45)/2),r*.89,h-.45,'pale',p,vertices=48)
    for z in [.43,h-.20]:
        cyl('Protective forged collar',(0,0,z),r*1.02,.15,'paint' if not tall else 'metal',p,vertices=48)
        ring('Collar rolled edge',(0,0,z+.075),r,.014,'edge',p)
    if tall:
        for j in range(20):
            a=j*math.tau/20;ob=box('Longitudinal protection rib',(r*.94*math.cos(a),r*.94*math.sin(a),(h+.40)/2),(.055,.075,h-.70),'bus',p,.012);ob.rotation_euler[2]=a
    else:
        for a in [0,math.pi/2,math.pi,math.pi*1.5]:
            ob=box('Overpack impact stay',(r*.92*math.cos(a),r*.92*math.sin(a),(h+.40)/2),(.065,.055,h-.60),'pale',p,.009);ob.rotation_euler[2]=a
    cyl('Lid gasket',(0,0,h-.085),r*.96,.035,'rubber',p)
    lid=assembly(name+'_LID',(0,0,h-.055),parent=p);lid['interaction']='unlock_and_lift';lid['lift_axis']='+Z'
    cyl('Machined lid rim',(0,0,0),r*1.02,.09,'metal',lid,vertices=48)
    cyl('Shallow dished cover',(0,0,.055),r*.86,.07,'pale',lid,vertices=48)
    bolts_circle(lid,.06,r*.94,12)
    for x in [-r*.55,r*.55]:
        box('Lift eye welded base',(x,0,.11),(.19,.15,.06),'metal',lid,.015)
        ring('Forged lifting eye',(x,0,.19),.07,.026,'metal',lid,'Y')
    for a in [math.pi*.25,math.pi*.75,math.pi*1.25,math.pi*1.75]:
        q=assembly('Captive toggle clamp',(r*math.cos(a),r*math.sin(a),h-.22),a+math.pi/2,parent=p)
        box('Clamp clevis',(0,0,0),(.11,.09,.24),'darkpaint',q,.01)
        cyl('Clamp cross pin',(0,-.055,.025),.027,.14,'metal',q,'X')
        box('Over-center lever',(0,-.07,-.07),(.045,.04,.23),'metal',q,.008)
        box('Seal tag',(0,-.095,-.12),(.06,.005,.055),'yellow',q,.002)
    for x in [-r-.06,r+.06]:
        cyl('Lifting trunnion',(x,0,h*.65),.10,.18,'metal',p,'X')
        cyl('Trunnion retaining flange',(x+(.08 if x>0 else -.08),0,h*.65),.14,.035,'darkpaint',p,'X')
    plaque(p,name,(0,-r*.90-.02,.79),.42,.18,size=.065)
    gauge(p,0,-r*.91-.035,1.10 if tall else .62,.075,'SEAL',-.4)
    return p

def container(name,loc,open_lid=False,rot=0):
    global current
    current='Containers';p=root(name,loc,rot);p['equipment_type']='dry_container';p['interaction']='scan;inspect;seal;carry';p['hiding_volume_m']='1.85x0.65x0.65' if open_lid else 'none'
    w=2.15;d=.95;h=1.1
    for x in [-.75,.75]:box('Forklift box section',(x,0,.08),(.19,d,.16),'darkpaint',p,.012)
    box('Tub lower pan',(0,0,.21),(w,d,.12),'metal',p,.018)
    box('Tub floor',(0,0,.285),(w-.10,d-.10,.03),'pale',p,.004)
    for x in [-w/2+.035,w/2-.035]:box('Sealed end panel',(x,0,.66),(.07,d,.78),'pale',p,.015)
    for y in [-d/2+.025,d/2-.025]:
        box('Folded sidewall',(0,y,.66),(w,.05,.78),'pale',p,.012)
        for x in [-.87,-.35,.35,.87]:box('Pressed panel reinforcement',(x,y+(.032 if y>0 else -.032),.65),(.08,.045,.71),'bus',p,.006)
    for x in [-1.02,1.02]:
        for y in [-.44,.44]:box('Container corner casting',(x,y,.65),(.15,.16,.94),'metal',p,.012)
    for y in [-d/2+.04,d/2-.04]:box('Long lid gasket',(0,y,1.066),(w-.08,.035,.025),'rubber',p,.006)
    for x in [-w/2+.04,w/2-.04]:box('End lid gasket',(x,0,1.066),(.035,d-.08,.025),'rubber',p,.006)
    lid=assembly(name+'_LID',(0,d/2,1.08),parent=p)
    box('Folded lid',(0,-d/2,.025),(w,d,.07),'pale',lid,.02)
    for x in [-.78,.78]:
        box('Lid top reinforcement',(x,-d/2,.082),(.13,d-.06,.045),'metal',lid,.006)
        handle(lid,x,-d/2,.11,height=.22)
    if open_lid:lid.rotation_euler[0]=math.radians(-72)
    for x in [-.78,.78]:
        box('Over-center latch plate',(x,-d/2-.025,.92),(.14,.03,.23),'metal',p,.007)
        box('Latch pull',(x,-d/2-.055,.92),(.035,.04,.13),'darkpaint',p,.006)
    plaque(p,name,(0,-d/2-.029,.67),.62,.18,size=.07)
    return p

def trolley(loc):
    global current
    current='Cart';p=root('CT01_TRANSFER_CART',loc);p['equipment_type']='cart';p['envelope_m']='1.0x1.8x1.8';p['interaction']='push;brake;clamp;release';p['incident']='brake_fault;overload;spill'
    for x in [-.35,.35]:
        for y in [-.57,.57]:
            q=assembly('Caster fork',(x,y,0),parent=p)
            cyl('Rubber load tire',(0,0,.15),.15,.105,'rubber',q,'X')
            cyl('Cast wheel hub',(0,0,.15),.088,.115,'metal',q,'X')
            cyl('Axle cap',(0,0,.15),.030,.145,'darkpaint',q,'X',8)
            for xx in [-.075,.075]:box('Caster fork cheek',(xx,0,.22),(.025,.16,.20),'metal',q,.008)
            cyl('Swivel bearing',(0,0,.35),.10,.065,'darkpaint',q)
            box('Caster mounting plate',(0,0,.393),(.23,.23,.025),'metal',q,.006)
            if y<0:box('Foot brake pedal',(0,-.13,.23),(.12,.18,.035),'yellow',q,.004)
    for x in [-.40,.40]:box('Welded cart main rail',(x,0,.45),(.09,1.5,.10),'darkpaint',p,.012)
    for y in [-.68,0,.68]:box('Cart crossmember',(0,y,.45),(.89,.09,.10),'darkpaint',p,.008)
    box('Folded load deck',(0,0,.52),(.94,1.48,.045),'paint',p,.012)
    for x in [-.445,.445]:box('Upturned deck edge',(x,0,.56),(.035,1.48,.065),'metal',p,.008)
    for x in [-.37,.37]:beam('Handle upright',(x,-.66,.5),(x,-.86,1.05),.044,'metal',p)
    beam('Push bar',(-.37,-.86,1.05),(.37,-.86,1.05),.044,'rubber',p)
    cyl('Screw lift thrust bearing',(0,0,.60),.15,.1,'darkpaint',p)
    cyl('Mechanical lift screw',(0,0,.72),.035,.22,'metal',p)
    for z in [.65,.69,.73,.77]:ring('Screw thread land',(0,0,z),.037,.008,'metal',p)
    box('Load saddle',(0,0,.86),(.67,.87,.09),'pale',p,.015)
    for y in [-.39,.39]:box('Load restraint dog',(0,y,.93),(.33,.06,.16),'darkpaint',p,.008)
    plaque(p,'CT01',(0,-.755,.55),.3,.12,size=.05)
    return p

def jib(loc):
    global current
    current='Casks';p=root('HJ01_HANDLING_JIB',loc);p['equipment_type']='handling_jib';p['interaction']='hoist;lower;slew';p['incident']='hoist_fault'
    box('Anchored pedestal',(0,0,.06),(.8,.8,.12),'darkpaint',p,.025)
    for x in [-.28,.28]:
        for y in [-.28,.28]:cyl('Foundation stud',(x,y,.14),.035,.10,'metal',p,vertices=6)
    cyl('Jib mast',(0,0,1.75),.14,3.38,'paint',p)
    for z in [.30,2.82,3.36]:cyl('Mast collar',(0,0,z),.18,.13,'metal',p)
    box('Jib boom web',(0,-.90,3.40),(.085,1.9,.28),'paint',p,.004)
    for z in [3.25,3.55]:box('Jib boom flange',(0,-.9,z),(.24,1.9,.035),'yellow',p,.003)
    beam('Jib brace',(0,0,2.75),(0,-1.75,3.32),.075,'metal',p)
    box('Hoist trolley',(0,-1.45,3.14),(.32,.30,.18),'darkpaint',p,.02)
    cyl('Chainwheel housing',(0,-1.45,2.98),.16,.18,'paint',p,'X')
    for x in [-.06,.06]:beam('Hoist chain',(x,-1.45,2.9),(x,-1.45,2.42),.012,'metal',p)
    ring('Load hook',(0,-1.45,2.34),.10,.025,'metal',p,'Y')
    return p

def vent_skid(loc):
    global current
    current='Ventilation';p=root('VF01_EXTRACTION',loc);p['equipment_type']='ventilation';p['interaction']='isolate;replace_filter;reset;repair';p['incident']='filter_blockage;fan_fault;contamination'
    for x in [-1,1]:box('Skid foot',(x,0,.09),(.17,1.1,.18),'darkpaint',p,.01)
    box('Skid bed',(0,0,.23),(2.45,1.15,.10),'metal',p,.012)
    box('Connected filter plenum',(-.38,.05,1.16),(1.55,1.02,1.72),'bus',p,.035)
    for x in [-.78,.02]:
        box('Filter gasket',(x,-.478,1.2),(.70,.028,1.38),'rubber',p,.015)
        box('Removable filter cassette',(x,-.508,1.2),(.64,.04,1.32),'pale',p,.018)
        handle(p,x,-.57,1.23,height=.30)
        for z in [.65,1.75]:
            box('Filter clamp',(x-.27,-.55,z),(.085,.07,.14),'metal',p,.008)
    # Fan casing and motor have a real shared centerline and connecting intake.
    cyl('Fan inlet collar',(.55,.03,1.40),.31,.27,'metal',p,'X')
    cyl('Centrifugal fan casing',(.82,.03,1.40),.43,.36,'paint',p,'X',48)
    cyl('Motor coupling',(1.05,.03,1.40),.09,.14,'metal',p,'X')
    cyl('Finned drive motor',(1.21,.03,1.40),.19,.23,'darkpaint',p,'X')
    for x in [1.12,1.16,1.20,1.24,1.28]:cyl('Cooling fin',(x,.03,1.40),.205,.016,'bus',p,'X')
    for x in [.79,1.20]:box('Motor support stand',(x,.03,.80),(.12,.46,1.05),'darkpaint',p,.007)
    box('Fan tangential outlet',(.82,.10,1.92),(.35,.43,.60),'paint',p,.02)
    box('Rising exhaust duct',(.82,.10,2.45),(.42,.48,.50),'bus',p,.006)
    gauge(p,-.77,-.57,2.02,.13,'DP',.35)
    plaque(p,'VF01 / FILTERS',(-.30,-.535,.49),1.02,.16,size=.075)
    return p

def inventory(loc):
    global current
    current='Monitoring';p=root('IM01_INVENTORY',loc);p['equipment_type']='inventory';p['interaction']='receive;scan;register;release;falsify';p['incident']='sensor_drift;inventory_discrepancy'
    for x in [-.64,.64]:
        for y in [-.30,.30]:box('Desk square leg',(x,y,.46),(.055,.055,.92),'darkpaint',p,.004)
    box('Steel desk top',(0,0,.95),(1.55,.78,.06),'pale',p,.015)
    box('Rear cable tray',(0,.3,.75),(1.35,.12,.15),'bus',p,.004)
    box('Terminal foot',(-.22,.10,1.01),(.38,.28,.06),'darkpaint',p,.014)
    box('Terminal stem',(-.22,.19,1.15),(.09,.10,.26),'metal',p,.008)
    box('Instrument rear casing',(-.22,.13,1.40),(.62,.32,.48),'pale',p,.05)
    folded_panel(p,(-.22,-.045,1.42),.62,.45,'darkpaint')
    box('Recessed screen',(-.22,-.036,1.42),(.49,.005,.30),'black',p,.014)
    text('Inventory screen heading','INVENTORY',(-.43,-.041,1.51),.037,'paper',p)
    for n,t in enumerate(['A  03 / SEALED','B  02 / SEALED','C  02 / CHECK','D  01 / HOLD']):text('Inventory row',t,(-.43,-.042,1.45-n*.047),.023,'paper',p)
    box('Keyboard housing',(-.22,-.20,1.006),(.56,.22,.045),'darkpaint',p,.016)
    for y in range(3):
        for x in range(12):box('Keycap',(-.46+x*.043,-.27+y*.054,1.035),(.033,.04,.016),'pale',p,.003)
    box('Spacebar',(-.20,-.29,1.04),(.23,.022,.012),'pale',p,.003)
    box('Scanner cradle',(.50,.03,1.01),(.14,.24,.055),'black',p,.012)
    box('Scanner grip',(.50,.04,1.12),(.06,.06,.20),'rubber',p,.02)
    box('Scanner head',(.50,.025,1.24),(.15,.14,.09),'yellow',p,.025)
    tube('Scanner lead',[(.50,.10,1.12),(.65,.2,1.05),(.67,.31,.82),(.2,.32,.79)],.012,'rubber',p)
    box('Bound logbook',(.43,-.21,1.006),(.28,.26,.035),'paint',p,.003)
    box('Logbook pages',(.43,-.21,1.026),(.26,.24,.009),'paper',p,.001)
    text('Logbook title','SHIFT LOG',(.33,-.20,1.032),.028,'ink',p,rot=(0,0,0))
    return p

def workshop(loc):
    global current
    current='Workshop';p=root('WB01_SEAL_REPAIR',loc);p['equipment_type']='repair_bench';p['interaction']='repair;replace_seal'
    for x in [-.72,.72]:
        for y in [-.29,.29]:box('Bench angle leg',(x,y,.44),(.065,.065,.88),'darkpaint',p,.005)
    box('Bench lower shelf',(0,0,.26),(1.48,.61,.055),'bus',p,.005)
    box('Thick plywood worktop',(0,0,.92),(1.70,.76,.075),'wood',p,.008)
    box('Tool backboard',(0,.32,1.34),(1.55,.065,.76),'paint',p,.008)
    for j in range(5):
        x=-.56+j*.26;beam('Wrench shank',(x,.267,1.13),(x,.267,1.50),.023,'metal',p)
        ring('Ring wrench end',(x,.267,1.52),.040,.013,'metal',p,'Y')
    box('Seal service case',(-.40,-.10,1.02),(.55,.34,.14),'pale',p,.018)
    for x in [-.61,-.19]:box('Case latch',(x,-.279,1.03),(.07,.018,.075),'metal',p,.003)
    ring('Replacement seal',(.40,-.04,.968),.14,.018,'rubber',p)
    box('Inventory tag stack',(.17,-.22,.973),(.17,.12,.022),'paper',p,.002)
    plaque(p,'SEAL SERVICE',(0,.278,1.70),.82,.12,size=.056)
    return p

def light(name,loc,target,power,size=1.5):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=(1,.87,.69)
    o=bpy.data.objects.new(name,d);COL['Lighting'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o

def fixture(loc,power=650):
    global current
    current='Lighting';x,y,z=loc
    p=assembly('Suspended practical',loc,support='Ceiling',anchors=[[0,0,4.8-z]],direction=[0,0,1])
    for xx in [-.55,.55]:beam('Suspension rod',(xx,0,.08),(xx,0,4.8-z),.016,'metal',p)
    box('Luminaire folded body',(0,0,0),(1.5,.27,.13),'darkpaint',p,.014)
    box('Prismatic warm diffuser',(0,0,-.075),(1.36,.21,.025),'lamp',p,.005)
    light('Practical pool',(x,y,z-.11),(x,y,0),power,1.3)

def portal(name,x,y,w,h,rot,label):
    global current
    current='Architecture';p=root(name,(x,y,0),rot);p['portal_id']=name
    for xx in [-w/2-.065,w/2+.065]:
        box('Steel portal reveal',(xx,0,h/2),(.13,.32,h),'darkpaint',p,.012)
        box('Seal track',(xx,-.18,h/2),(.055,.065,h),'rubber',p,.004)
    box('Portal head',(0,0,h+.11),(w+.40,.40,.22),'darkpaint',p,.014)
    # Open roller door stores above soffit; real cylinder and guides outside aperture.
    cyl('Roller door barrel',(0,.10,h+.37),.21,w+.05,'bus',p,'X',48)
    for xx in [-w/2-.13,w/2+.13]:box('Barrel bearing bracket',(xx,.10,h+.34),(.11,.40,.46),'paint',p,.018)
    box('Door sign backing',(0,-.228,h+.77),(max(w,2.7),.05,.34),'pale',p,.01)
    text('Portal identifier',label,(0,-.26,h+.68),.15,'ink',p,align='CENTER')
    return p

def architecture():
    global current
    current='Architecture'
    box('Floor',(0,9,-.15),(12.64,18.64,.30),'floor',bevel=0)
    box('Ceiling',(0,9,4.95),(12.64,18.64,.30),'wall',bevel=0)
    box('West Wall',(-6.16,9,2.4),(.32,18,4.8),'wall',bevel=0)
    for y,ln in [(.9,1.8),(10.5,15)]:box('East Wall',(6.16,y,2.4),(.32,ln,4.8),'wall',bevel=0)
    box('Personnel lintel',(6.16,2.4,3.55),(.32,1.2,2.5),'wall',bevel=0)
    for side,y,w,h in [('Receiving',-.16,3,3.2),('Dispatch',18.16,2.4,2.8)]:
        for x in [-(6+w/2)/2,(6+w/2)/2]:box(side+' wall',(x,y,2.4),(6-w/2,.32,4.8),'wall',bevel=0)
        box(side+' lintel',(0,y,(h+4.8)/2),(w,.32,4.8-h),'wall',bevel=0)
    portal('WS_RECEIVING',0,0,3,3.2,math.pi,'ELECTRICAL / RECEIVING')
    portal('WS_DISPATCH',0,18,2.4,2.8,0,'DISPATCH / SERVICE')
    portal('WS_PERSONNEL',6,2.4,1.2,2.3,-math.pi/2,'PERSONNEL')
    for x in [-5.87,5.87]:
        for y in [4.45,9.05,13.75,17.65]:
            box('Column shoe',(x,y,.06),(.24,.42,.12),'metal',bevel=.008)
            box('Column web',(x,y,2.35),(.11,.28,4.5),'darkpaint',bevel=.004)
            for xx in [x-.065,x+.065]:box('Column flange',(xx,y,2.35),(.04,.37,4.5),'darkpaint',bevel=.003)
    for y in [4.45,9.05,13.75,17.65]:
        box('Roof beam web',(0,y,4.55),(11.8,.11,.34),'darkpaint',bevel=.004)
        for z in [4.36,4.74]:box('Roof beam flange',(0,y,z),(11.8,.35,.04),'darkpaint',bevel=.003)
    for x in [-3,0,3]:box('Longitudinal roof purlin',(x,9,4.77),(.09,18,.06),'bus',bevel=.003)
    for x in [-1.81,1.81]:box('Cart lane paint',(x,9,.001),(.065,17.9,.002),'yellow',bevel=0)
    for y in [4.45,9.05,13.75]:box('Floor construction joint',(0,y,.0005),(12,.012,.001),'joint',bevel=0)
    for x in [-3,3]:box('Floor slab seam',(x,9,.0005),(.012,18,.001),'joint',bevel=0)
    # Four storage bays, curb only on side/rear; aisle access remains flush.
    for side in [-1,1]:
        for y,title in [(4.8,'A / RESIDUE' if side<0 else 'C / DRY'),(9.4,'B / SHIELDED' if side<0 else 'D / HOLD')]:
            for yy in [y,y+4]:box('Cell transverse concrete separator',(side*4.075,yy,.55),(3.85,.16,1.10),'wall',bevel=.012)
            # Retraction pocket at one end leaves2.55m clear side opening.
            box('Cell gate pocket',(side*2.08,y+.55,1.05),(.13,.95,2.10),'darkpaint',bevel=.008)
            for yy in [y+.11,y+3.89]:box('Cell boundary post',(side*2.04,yy,1.16),(.12,.12,2.32),'metal',bevel=.009)
            box('Cell sliding gate header',(side*2.04,y+2,2.34),(.16,3.92,.12),'darkpaint',bevel=.006)
            p=assembly('Cell label',(side*2.035,y+2,2.65),math.pi/2 if side<0 else -math.pi/2)
            box('Cell sign backing',(0,0,0),(1.70,.04,.27),'paint',p,.008)
            text('Cell identifier',title,(0,-.025,-.055),.12,'paper',p,align='CENTER')
    # Booth lower walls and glazing, open1.1m side door at y1.65..2.75.
    box('Booth rear divider',(-4.16,3.9,1.35),(3.68,.10,2.70),'pale',bevel=.01)
    for y,ln in [(1.025,1.25),(3.325,1.15)]:
        box('Booth side base',(-2.4,y,.48),(.10,ln,.96),'pale',bevel=.006)
        box('Booth window glass',(-2.4,y,1.72),(.016,ln-.08,1.45),'glass',bevel=.002)
        for z in [.99,2.47]:box('Booth glazing rail',(-2.4,y,z),(.065,ln,.055),'darkpaint',bevel=.004)
    box('Booth header',(-2.4,2.15,2.61),(.13,3.60,.18),'darkpaint',bevel=.008)
    for y in [.4,1.65,2.75,3.9]:box('Booth jamb',(-2.4,y,1.3),(.11,.08,2.6),'darkpaint',bevel=.005)
    # Utility routing, capped exterior ends pending shared network.
    current='Ventilation'
    for x in [-5.45,5.45]:
        box('Longitudinal extract header',(x,10.95,4.03),(.43,13.70,.45),'bus',bevel=.01)
        for y in [5.4,8.4,11,13.5,16.6]:
            box('Duct joint flange',(x,y,4.03),(.49,.055,.51),'metal',bevel=.003)
            for xx in [x-.31,x+.31]:beam('Duct hanger',(xx,y,3.78),(xx,y,4.8),.025,'metal')
            box('Duct trapeze',(x,y,3.77),(.75,.045,.05),'darkpaint',bevel=.003)
        for y in [6.6,11.2]:
            box('Cell extract drop',(x,y,3.30),(.32,.35,1.0),'bus',bevel=.005)
            box('Extract grille frame',(x,y,2.78),(.51,.48,.10),'darkpaint',bevel=.008)
            for j in range(6):box('Extract grille vane',(x-.20+j*.08,y,2.71),(.023,.38,.045),'metal',bevel=.001)

architecture()
cask('RA01',(-4.55,5.6,0),rot=math.pi/2);cask('RA02',(-4.55,7.7,0),rot=math.pi/2);cask('RA03',(-3.15,7.7,0),rot=math.pi/2)
cask('SC01',(-4.65,10.75,0),True,math.pi/2);cask('SC02',(-4.65,12.35,0),True,math.pi/2)
container('DR01',(4.25,5.65,0));container('DR02',(4.25,7.55,0))
container('QH01',(4.65,11.75,0),True,-math.pi/2)
trolley((3.4,3.82,0));hj=jib((-3.15,10.3,0));hj.rotation_euler[2]=math.pi;vent_skid((-4.35,16.05,0));inv=inventory((-4.1,1.65,0));inv.rotation_euler[2]=math.pi/2;workshop((4.55,16.75,0))
for x,y,power in [(-2.9,2.1,650),(2.6,3.1,600),(-3.9,6.5,800),(3.9,6.5,700),(-3.9,11.2,950),(3.9,11.2,700),(-3.5,16,750),(3.8,16,650),(0,8,500),(0,14,500)]:fixture((x,y,4.1),power)

current='Cameras'
CAMERAS=[('C01_Entry',(0,.55,1.68),(0,11,1.75),24),('C02_Casks',(-1.0,8.8,1.68),(-4.1,11.5,1.5),28),('C03_Reverse',(0,17.35,1.68),(0,3,1.7),24),('C04_Route',(.45,4.15,1.68),(.1,16.9,1.4),25),('C05_Transfer',(1.4,1.5,1.68),(3.45,3.4,.75),30),('C06_Dry',(1.0,5.0,1.68),(4.3,7.0,1.0),28),('C07_Quarantine',(1.0,10.0,1.68),(4.3,11.6,1.0),28),('C08_Extraction',(-1.1,14.7,1.68),(-4.2,16.05,1.5),28),('C09_Inventory',(-2.8,2.9,1.68),(-4.0,1.7,1.3),25),('C10_Workbench',(2.1,15.5,1.68),(4.55,16.75,1.2),30),('W01_Personnel',(4.3,2.4,1.68),(6,2.4,1.4),22),('W02_ReceivingReturn',(0,4,1.68),(0,0,1.7),24),('W03_Dispatch',(0,15.2,1.68),(0,18,1.6),24),('W04_CellService',(-2.85,10.2,1.68),(-4.6,12,1.3),25)]
for name,loc,target,lens in CAMERAS:
    if name=='C02_Casks':loc=(-1,10.6,1.68);target=(-4.3,11.6,1.45);lens=24
    if name=='C08_Extraction':loc=(-1.5,14.3,1.68);lens=24
    d=bpy.data.cameras.new(name);d.lens=lens;d.clip_start=.04;d.clip_end=120;o=bpy.data.objects.new(name,d);COL['Cameras'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
exec(compile((Path(__file__).parent/'detail_pass.py').read_text(),str(Path(__file__).parent/'detail_pass.py'),'exec'))
exec(compile((Path(__file__).parent/'art_pass.py').read_text(),str(Path(__file__).parent/'art_pass.py'),'exec'))
exec(compile((Path(__file__).parent/'refine_pass.py').read_text(),str(Path(__file__).parent/'refine_pass.py'),'exec'))
exec(compile((Path(__file__).parent/'finish_pass.py').read_text(),str(Path(__file__).parent/'finish_pass.py'),'exec'))
exec(compile((Path(__file__).parent/'access_pass.py').read_text(),str(Path(__file__).parent/'access_pass.py'),'exec'))
exec(compile((Path(__file__).parent/'surface_pass.py').read_text(),str(Path(__file__).parent/'surface_pass.py'),'exec'))
exec(compile((Path(__file__).parent/'clearance_pass.py').read_text(),str(Path(__file__).parent/'clearance_pass.py'),'exec'))
exec(compile((Path(__file__).parent/'pedestal_pass.py').read_text(),str(Path(__file__).parent/'pedestal_pass.py'),'exec'))
exec(compile((Path(__file__).parent/'process_pass.py').read_text(),str(Path(__file__).parent/'process_pass.py'),'exec'))
exec(compile((Path(__file__).parent/'light_pass.py').read_text(),str(Path(__file__).parent/'light_pass.py'),'exec'))
SC.camera=bpy.data.objects['C01_Entry'];SC.render.engine='CYCLES';SC.cycles.samples=48;SC.cycles.use_denoising=True
SC.render.resolution_x=1440;SC.render.resolution_y=900;SC.render.resolution_percentage=100
SC.world=bpy.data.worlds.new('Neutral ambient');SC.world.use_nodes=True;SC.world.node_tree.nodes['Background'].inputs[0].default_value=(.20,.18,.15,1);SC.world.node_tree.nodes['Background'].inputs[1].default_value=.25
SC.view_settings.view_transform='AgX';SC.view_settings.look='AgX - Medium High Contrast';SC.view_settings.exposure=0
for d in bpy.data.lights:d.energy*=.25
SC['authoring_sources']=json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')},sort_keys=True)
SC['interface_json']=(ROOT/'interface.json').read_text()
CAMERAS=[{'name':o.name,'location':list(o.location),'rotation_euler':list(o.rotation_euler),'lens':o.data.lens} for o in SC.objects if o.type=='CAMERA']
SC['camera_manifest']=json.dumps(CAMERAS)
bpy.context.view_layer.update()
out=Path(args.output) if args.output else ROOT/'blender/waste_storage.blend';out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out))
manifest={'revision':args.revision,'objects':len(SC.objects),'materials':len(bpy.data.materials),'cameras':CAMERAS,'source_sha256':SC['source_sha256'],'blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
dest=ROOT/'production/checkpoints'/args.revision;dest.mkdir(parents=True,exist_ok=True);(dest/'build_manifest.json').write_text(json.dumps(manifest,indent=2))
print('BUILD_COMPLETE',json.dumps({'revision':args.revision,'objects':len(SC.objects),'path':str(out)}),flush=True)

