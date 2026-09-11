"""M02 manufactured construction, controlled material values, clear interactions."""
def recolor(key,hex):
    rgb=srgb(hex);m=M[key];m.diffuse_color=(*rgb,1);nt=m.node_tree;nt.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*rgb,1)
    for n in nt.nodes:
        if n.type=='VALTORGB':
            for e,f in zip(n.color_ramp.elements,[.975,1.025]):e.color=(*(v*f for v in rgb),1)
for key,h in [('wall','999A95'),('floor','71736E'),('pale','B5B7B1'),('darkpaint','292C2C'),('bus','555B5A'),('orange','D77C36'),('paper','D2CDBE')]:recolor(key,h)
for key in ['pale','bus','darkpaint']:
    bs=M[key].node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.64
    for n in M[key].node_tree.nodes:
        if n.type=='MAP_RANGE':n.inputs['To Min'].default_value=.61;n.inputs['To Max'].default_value=.67
for o in SC.objects:
    if o.type=='LIGHT':
        if o.name.startswith('Ceiling practical output'):o.data.energy*=.65;o.data.color=(1,.98,.94)
        elif o.name.startswith('OCRU neutral'):o.data.energy=125;o.data.color=(.96,.98,1)
        elif o.name.startswith('Wall grazed'):o.data.energy=65;o.data.color=(1,.82,.60)
SC.objects['OPERATOR_STOOL'].location.y=8.49
# Park the two-part transfer bridge folded inward below the berth, exposing the lift.
br=SC.objects['OCRU_TRANSFER_BRIDGE'];br.rotation_euler.x=math.pi;br['state']='folded inward under tray';br['parked_angle_x']=math.pi
SC.objects['Fold-down bridge leaf'].data.materials[0]=M['darkpaint']
# Factory mounting corrections, no equipment relocation.
current='Utilities';p=SC.objects['HANDWASH']
box('Sink load-bearing wall packer',(0,.265,.71),(.53,.030,.25),'darkpaint',p,.002)
p['support_target']='East wall';p['support_anchors']=json.dumps([[-.2,.28,.71],[.2,.28,.71]]);p['support_direction']=json.dumps([0,1,0])
p=SC.objects['Return to service notice'];box('Notice wall mounting pad',(0,.020,0),(.32,.020,.36),'darkpaint',p,.002)
for o in [o for o in SC.objects if o.name.startswith('Wall task practical')]:
    if o.location.x>3:
        o.rotation_euler.z=-math.pi/2
        box('Task fixture wall bracket',(0,.075,0),(.3,.09,.07),'darkpaint',o,.002)
    else:box('Task fixture wall bracket',(0,.085,0),(.3,.05,.07),'darkpaint',o,.002)
# Layered wall panels and physically attached column cover plates.
current='Architecture'
for y in [2.4,6.0]:
    for x in [-3.975,3.975]:
        box('Wall structural post cover',(x,y,2.36),(.05,.15,2.44),'bus',bevel=.003)
for x in [-3.2,-1.6,0]:
    box('Rear upper panel joint',(x,8.997,2.76),(.012,.006,1.56),'joint',bevel=0)
box('Rear horizontal panel joint',(-1.225,8.997,2.15),(5.55,.006,.012),'joint',bevel=0)
# Small bolted rail brackets explain cross-member to wall construction.
for y in [1,3.4,6,8.65]:
    for side in [-1,1]:
        r=assembly('Beam wall seat',(side*3.965,y,3.3),math.pi/2 if side<0 else -math.pi/2)
        box('Beam seat backing',(0,0,0),(.32,.07,.42),'darkpaint',r,.003)
        fasteners('Beam seat bolts',[-.11,.11],[-.14,.14],-.040,r,r=.018)
# Crisp restrained access graphics follow the actual apron, not an invented corridor.
for x in [-.98,2.18]:box('Transfer apron side marking',(x,4.65,.002),(.045,3.1,.002),'orange',bevel=0)
for y in [3.1,6.2]:box('Transfer apron end marking',(.60,y,.002),(3.20,.045,.002),'orange',bevel=0)
text('Transfer floor legend','TRANSFER / KEEP CLEAR',(-.6,3.28,.004),.10,'ink',rot=(0,0,0))
for y in [.8,2.2,7.25]:
    for x in [-.65,.65]:box('Rescue route margin tick',(x,y,.002),(.12,.04,.002),'paper',bevel=0)
# OCRU specific construction: layered removable skins, rails, service links and vents.
current='OCRU';p=SC.objects['OCRU']
SC.objects['Rear machine skin'].data.materials[0]=M['darkpaint']
for x in [-.86,0,.86]:
    box('Inner removable liner',(x,1.17,1.47),(.84,.04,1.85),'bus',p,.003)
    fasteners('Inner liner screw',[x-.34,x+.34],[.65,2.27],1.145,p,r=.012)
for x in [-1.69,1.69]:
    box('Inner service panel inset',(x,.915,1.49),(.41,.02,1.18),'darkpaint',p,.003)
    for z in [1.15,1.24,1.33]:box('Service panel vent blade',(x,.897,z),(.29,.023,.025),'metal',p,.002)
    handle(p,x,.885,1.85,height=.22)
    box('Vertical task strip housing',(x*.75,1.12,1.58),(.085,.10,.92),'darkpaint',p,.002)
    box('Vertical task strip lens',(x*.75,1.06,1.58),(.032,.014,.82),'task',p,.002)
    area_light('OCRU liner task',tuple(p.matrix_world@Vector((x*.75,.97,1.8))),tuple(p.matrix_world@Vector((x*.5,-.6,.98))),25,.45,(.96,.98,1))
for x in [-1.95,1.95]:
    box('Jamb service inset',(x,-1.262,.99),(.11,.014,.33),'darkpaint',p,.002)
    for z in [.9,1.01,1.12]:cyl('Jamb latch pin',(x,-1.28,z),.020,.015,'metal',p,'Y',12)
    box('Jamb removable outer flange',(x*1.065,-1.15,1.52),(.065,.16,2.21),'bus',p,.002)
for x in [-1.4,0,1.4]:box('Fascia panel split',(x,-1.259,2.76),(.008,.003,.28),'joint',p,0)
for x in [-1.98,1.98]:
    for z in [.47,2.47]:box('Shutter guide bolted shoe',(x,-1.22,z),(.25,.13,.085),'metal',p,.003)
for y in [-1.13,1.10]:
    for x in [-1.70,-.70,.70,1.70]:cyl('Skid riveted connection',(x,y,.35),.016,.028,'metal',p,vertices=8)
for x in [-1.9,1.9]:
    tube('Jamb actuator protected line',[(x,.9,2.88),(x,-.72,2.88),(x,-1.03,2.52),(x,-1.03,.60)],.018,'orange',p)
    for z in [.72,1.55,2.3]:box('Actuator pipe clip',(x,-1.08,z),(.085,.12,.06),'darkpaint',p,.002)
tray=SC.objects['OCRU_BERTH']
for x in [-.75,.75]:
    for z in [.54,.61,.68,.75]:box('Lift column protective bellows',(x,0,z),(.29,.36,.025),'rubber',tray,.004)
    cyl('Lift adjustment ram',(x,.2,.70),.037,.32,'metal',tray)
    box('Lift foot bolt flange',(x,0,.49),(.53,.62,.035),'metal',tray,.003)
for x in [-1.04,1.04]:
    tube('Tray locking lever',[(x,-.40,.94),(x,-.52,.94),(x,-.52,.85)],.012,'orange',tray)
for x in [-.85,-.45,0,.45,.85]:
    cyl('Bridge pivot knuckle',(x,-.48,.967),.028,.14,'metal',tray,'X')
cp=SC.objects['OCRU_CARTRIDGE_RECEIVER']
for x in [-.13,.13]:fasteners('Receiver captive bolt',[x],[-.24,.24],-.076,cp,r=.012)
sp=SC.objects['OCRU_SUIT_SERVICE'];plaque(sp,'01',(0,-.048,-.19),.11,.09,size=.05)
# Rear process wall: medium-scale panel construction, physical controls and readable states.
current='Stations';p=SC.objects['RESTART_CONSOLE']
SC.objects['Operator sloped panel'].rotation_euler.x=math.radians(-8)
box('Console lower equipment door',(.43,.07,.48),(.75,.63,.65),'bus',p,.004)
box('Console front removable panel',(.43,-.26,.48),(.67,.025,.55),'darkpaint',p,.003)
fasteners('Console maintenance fastener',[.15,.71],[.25,.71],-.28,p,r=.011)
for z in [.34,.40,.46]:box('Console cooling louver',(.43,-.281,z),(.46,.018,.026),'bus',p,.002)
for x in [-.86,.86]:box('Worktop reinforced edge',(x,0,.92),(.045,.89,.11),'metal',p,.003)
box('Console kick protector',(0,-.30,.12),(1.72,.10,.08),'orange',p,.003)
for x in [-.53,-.05,.43]:
    box('Switch face inset',(x,-.2,1.02),(.21,.23,.009),'metal',p,.002)
    for xx in [x-.09,x+.09]:cyl('Switch plate screw',(xx,-.28,1.028),.008,.004,'black',p,vertices=8)
# A large simplified human glyph on the waiting display, original geometry.
cyl('Employee status head',(.46,.096,1.43),.025,.003,'screen',p,'Y',16)
box('Employee status torso',(.46,.096,1.36),(.042,.003,.083),'screen',p,.001)
for side in [-1,1]:
    beam('Employee status arm',(.46+side*.027,.095,1.39),(.46+side*.06,.095,1.33),.010,'screen',p)
    beam('Employee status leg',(.46+side*.011,.095,1.32),(.46+side*.03,.095,1.26),.012,'screen',p)
SC.objects['Employee waiting'].location.z=1.20
for x in [-.76,-.53,-.30]:box('Telemetry status bar',(x,.095,1.18),(.18,.003,.012),'orange',p,.001)
for name in ['CARTRIDGE_BANK','RESERVE_POWER']:
    p=SC.objects[name]
    for x in [-.25,.25]:fasteners('Cabinet perimeter screw',[x],[.14,1.28],-.352,p,r=.012)
p=SC.objects['CARTRIDGE_BANK']
for i,z in enumerate([.44,.84,1.24,1.64]):plaque(p,f'{i*3+1:02}-{i*3+3:02}',(0,-.34,z+.015),.30,.055,size=.032)
p=SC.objects['RECOVERY_BERTH']
M['blanket']=material('Woven charcoal recovery blanket','555B58',.98,0,.025,.0005)
SC.objects['Folded recovery blanket'].data.materials[0]=M['blanket']
for y in [-.82,-.77,-.72]:box('Blanket stitched fold',(0,y,.838),(.87,.003,.001),'bus',p,0)
for x in [-.48,.48]:box('Mattress bound piping',(x,0,.75),(.012,1.97,.015),'paper',p,.003)
# Purposeful decon consumable receptacle occupies alcove rear corner, outside standing route.
current='Props';p=assembly('DECON_USED_PPE_BIN',(2.87,10.81,0),support='Decon floor')
box('PPE bin foot',(0,0,.025),(.36,.32,.05),'rubber',p,.005)
box('PPE return body',(0,0,.31),(.37,.34,.55),'orange',p,.008)
box('PPE sealed lid',(0,0,.60),(.40,.37,.045),'darkpaint',p,.006)
plaque(p,'USED PPE',(0,-.176,.37),.31,.095,size=.045)
box('PPE pedal',(0,-.20,.09),(.20,.14,.035),'metal',p,.004)
current='Architecture'
# Consistent short station signs on wall-mounted backing; no floating text.
for name,loc,rot,label in [('Recovery identity',(3.97,4.7,1.75),-math.pi/2,'RECOVERY'),('Supplies identity',(3.97,1.47,1.75),-math.pi/2,'SUPPLIES')]:
    p=assembly(name,loc,rot);box('Identity wall spacer',(0,.02,0),(.7,.02,.18),'darkpaint',p,.002);plaque(p,label,(0,0,0),.9,.19,size=.10)
