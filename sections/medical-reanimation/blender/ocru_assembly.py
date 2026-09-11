"""Original manufactured OCRU within the inherited west-wall envelope."""
current='OCRU';p=assembly('OCRU',(-2.70875,4.63,0),math.pi/2,support='Floor',anchors=[[-1.8,-.9,0],[1.8,-.9,0],[-1.8,.9,0],[1.8,.9,0]])
p['equipment_type']='ocru';p['canonical_name']='Organic Continuity and Recommissioning Unit'
for x in [-1.80,1.80]:
    for y in [-.96,.96]:
        box('Chamber sole shoe',(x,y,.04),(.34,.32,.08),'rubber',p,.012)
        box('Fabricated chamber foot',(x,y,.14),(.28,.26,.14),'darkpaint',p,.006)
        for dx in [-.09,.09]:cyl('Base hold-down',(x+dx,y,.22),.024,.027,'metal',p,vertices=8)
for y in [-1.11,1.11]:box('Chassis longitudinal channel',(0,y,.25),(4.26,.16,.18),'darkpaint',p,.006)
for x in [-1.96,0,1.96]:box('Chassis cross member',(x,0,.25),(.14,2.38,.18),'darkpaint',p,.006)
box('Sealed chamber pan',(0,0,.365),(4.25,2.38,.07),'metal',p,.003)
box('Rear machine skin',(0,1.215,1.56),(4.29,.065,2.40),'pale',p,.004)
for x in [-2.09,2.09]:
    box('Chamber structural upright',(x,0,1.50),(.12,2.44,2.42),'darkpaint',p,.003)
    box('Formed end service panel',(x,-.03,1.52),(.13,2.30,2.24),'pale',p,.012)
    box('Access jamb graphite return',(x*.93,-1.15,1.45),(.22,.17,2.18),'darkpaint',p,.006)
    box('Jamb folded cover',(x*.94,-1.225,1.47),(.25,.06,2.13),'pale',p,.007)
    box('Orange latch rail',(x*.94,-1.262,1.75),(.072,.025,.67),'orange',p,.004)
    fasteners('Jamb captive fastener',[x*.94],[.55,1.05,2.18],-1.27,p,r=.013)
box('Chamber roof load beam',(0,0,2.73),(4.28,2.43,.17),'darkpaint',p,.006)
box('Chamber top folded fascia',(0,-1.18,2.76),(4.29,.15,.33),'pale',p,.009)
for x in [-1.65,-.60,.60,1.65]:fasteners('Top removable fascia fixing',[x],[2.68,2.84],-1.267,p,r=.014)
text('Canonical short machine ID','OCRU',(-1.32,-1.263,2.64),.24,'ink',p)
plaque(p,'ORGANIC CONTINUITY',(0,1.17,2.15),1.9,.15,mat='darkpaint',size=.080)
# Segmented shutter is rolled above the opening; separate host-actuated assembly.
sh=assembly('OCRU_ACCESS_SHUTTER',(0,-1.08,2.55),parent=p);sh['mechanism']='segmented roll shutter';sh['open_state']=True
cyl('Shutter winding drum',(0,0,.13),.16,3.62,'darkpaint',sh,'X',48)
for j in range(12):
    a=j*math.tau/12;y=math.cos(a)*.175;z=.13+math.sin(a)*.175
    ob=box('Rolled access slat',(0,y,z),(3.65,.075,.020),'metal',sh,.002);ob.rotation_euler.x=-a
for x in [-1.84,1.84]:
    cyl('Shutter end plate',(x,0,.13),.20,.06,'metal',sh,'X')
    box('Seal guide',(x,-.11,-1.06),(.042,.045,2.16),'rubber',sh,.002)
box('Chamber sill',(0,-1.15,.405),(3.70,.20,.07),'metal',p,.003)
# The adult berth is supported by floor-mounted lifting columns and twin rails.
tray=assembly('OCRU_BERTH',(0,-.61,0),parent=p);tray['equipment_type']='adult_berth';tray['berth_dimensions_m']=json.dumps([2.2,.88,1.02])
for x in [-.75,.75]:
    box('Berth pedestal foot',(x,0,.44),(.55,.64,.08),'darkpaint',tray,.010)
    box('Telescopic lift outer',(x,0,.64),(.26,.32,.33),'bus',tray,.010)
    box('Telescopic lift inner',(x,0,.80),(.18,.23,.29),'metal',tray,.006)
    box('Rail support crosshead',(x,0,.895),(.38,.80,.06),'darkpaint',tray,.004)
for y in [-.34,.34]:
    box('Captive transfer rail',(0,y,.93),(2.36,.075,.065),'metal',tray,.003)
    for x in [-.91,.91]:cyl('Tray captive roller',(x,y,.96),.035,.04,'black',tray,'Y')
box('Adult tray pressed pan',(0,0,.972),(2.26,.93,.046),'metal',tray,.008)
for x in [-.78,0,.78]:box('Segmented adult berth cushion',(x,0,1.005),(.70,.88,.03),'rubber',tray,.014)
box('Contoured head pad',(.88,0,1.065),(.32,.55,.09),'linen',tray,.04)
for x in [-.75,.45]:
    box('Safety restraint webbing',(x,0,1.025),(.045,.89,.010),'orange',tray,.002)
    box('Restraint buckle',(x,-.46,1.02),(.07,.045,.03),'metal',tray,.004)
for x in [-1.115,1.115]:box('Tray folded end flange',(x,0,.95),(.025,.94,.09),'metal',tray,.003)
bridge=assembly('OCRU_TRANSFER_BRIDGE',(0,-.48,.967),parent=tray);bridge['state']='parked vertical';bridge['deployed_angle_x']=0;bridge['parked_angle_x']=math.pi/2
bridge.rotation_euler.x=math.pi/2
box('Fold-down bridge leaf',(0,-.22,0),(1.92,.44,.018),'metal',bridge,.003)
cyl('Transfer bridge continuous hinge',(0,0,0),.021,1.96,'metal',bridge,'X')
for x in [-.8,.8]:box('Transfer bridge stop',(x,.012,-.026),(.08,.055,.055),'darkpaint',bridge,.003)
# Small local service panel is accessible at the chamber end, not a decorative monitor.
sp=assembly('OCRU_SUIT_SERVICE',(1.60,-1.235,1.25),parent=p)
box('Suit service enclosure',(0,.015,0),(.34,.09,.50),'darkpaint',sp,.01)
cyl('Suit port socket',(0,-.05,.11),.062,.04,'metal',sp,'Y')
ring('Suit coupling lock',(0,-.078,.11),.05,.009,'orange',sp,'Y')
tube('Suit service hose',[(0,-.095,.11),(-.1,-.1,-.05),(-.1,-.1,-.36),(.06,-.1,-.39),(.10,-.1,-.12)],.021,'rubber',sp)
cyl('Parked suit coupling',(.10,-.10,-.08),.037,.09,'metal',sp)
box('Coupling parking clip',(.10,-.025,-.14),(.085,.16,.045),'bus',sp,.003)
plaque(sp,'SUIT',(0,-.047,.32),.30,.10,size=.05)
cp=assembly('OCRU_CARTRIDGE_RECEIVER',(-1.63,-1.255,1.30),parent=p)
box('Receiver cast housing',(0,0,0),(.35,.14,.60),'bus',cp,.016)
box('Keyed cartridge throat',(0,-.08,.08),(.22,.02,.23),'black',cp,.004)
box('Cartridge retaining drawer',(0,-.15,.08),(.17,.16,.20),'pale',cp,.006)
box('Cartridge extraction tab',(0,-.245,.08),(.11,.03,.05),'orange',cp,.004)
plaque(cp,'INSERT',(0,-.077,.36),.33,.10,size=.047)
rotary(cp,0,-.083,-.20,'red')
plaque(cp,'RELEASE',(0,-.084,-.37),.33,.08,size=.04)
# Bolted service raceway runs to an actual rear terminal cabinet.
box('Chamber service raceway',(0,.91,2.91),(3.75,.22,.18),'bus',p,.008)
for x in [-1.5,0,1.5]:box('Raceway roof standoff',(x,.91,2.82),(.14,.20,.09),'darkpaint',p,.003)
for x in [-1.7,-1.45]:tube('Crown power loop',[(x,1.04,2.98),(x,-.75,2.98),(x,-1.06,2.77),(x,-1.08,2.52)],.025,'rubber',p)
for x in [-1.15,1.15]:
    box('Internal task light housing',(x,.25,2.53),(.16,.20,.08),'darkpaint',p,.006)
    box('Internal task lens',(x,.25,2.482),(.12,.16,.017),'task',p,.003)
for x in [-1.7,1.7]:
    box('Serviceable inner access panel',(x,.98,1.48),(.54,.11,1.47),'pale',p,.005)
    fasteners('Access panel fastener',[x-.21,x+.21],[.87,2.09],.914,p,r=.011)
