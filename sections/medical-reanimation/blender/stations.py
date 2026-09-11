"""Recovery, cart, operator station and consumables in preserved R09 positions."""
current='Stations'
def caster(parent,x,y,r=.08):
    cyl('Caster rubber tyre',(x,y,r),r,.045,'rubber',parent,'X',32)
    for side in [-1,1]:
        cyl('Wheel hub',(x+side*.025,y,r),r*.49,.01,'metal',parent,'X',20)
        box('Pressed caster fork',(x+side*.040,y,r+.045),(.018,.10,.13),'metal',parent,.006)
    cyl('Caster swivel',(x,y,r+.12),.06,.028,'metal',parent)
    box('Caster mounting plate',(x,y,r+.146),(.15,.16,.02),'darkpaint',parent,.003)
    box('Foot brake pedal',(x,y-.082,r+.07),(.08,.105,.022),'orange',parent,.003)

def cartridge(parent,x,y,z,index):
    cyl('Cartridge steel body',(x,y,z+.11),.045,.22,'metal',parent,vertices=24)
    cyl('Keyed consumable cap',(x,y,z+.23),.050,.035,'orange',parent,vertices=12)
    cyl('Cartridge bottom seal',(x,y,z+.005),.047,.016,'rubber',parent)
    box('Consumable paper ID',(x,y-.046,z+.11),(.057,.004,.10),'paper',parent,.001)
    text('Cartridge serial',f'{index:02}',(x,y-.049,z+.09),.031,'ink',parent)

p=assembly('BODY_CART',(-3.12,1.33,0),support='Floor',anchors=[[-.27,-.83,0],[.27,-.83,0],[-.27,.83,0],[.27,.83,0]])
p['equipment_type']='body_cart';p['nominal_dimensions']=json.dumps([.74,2.10,.92])
for x in [-.27,.27]:
    for y in [-.83,.83]:caster(p,x,y)
for x in [-.29,.29]:box('Cart lower frame rail',(x,0,.27),(.065,1.87,.065),'darkpaint',p,.005)
for y in [-.83,.83]:box('Cart axle cross brace',(0,y,.27),(.65,.06,.07),'darkpaint',p,.004)
for x in [-.20,.20]:
    beam('Cart lift scissor',(x,-.64,.30),(x,.63,.80),.055,'metal',p)
    beam('Cart lift scissor',(x,.64,.30),(x,-.63,.80),.055,'bus',p)
    cyl('Scissor fulcrum',(x,0,.55),.044,.082,'metal',p,'X')
box('Cart deck',(0,0,.83),(.74,2.10,.065),'metal',p,.013)
for y in [-.69,0,.69]:box('Cart segmented mattress',(0,y,.89),(.66,.65,.06),'rubber',p,.025)
for x in [-.35,.35]:
    box('Stretcher side retaining rim',(x,0,.86),(.025,2.03,.035),'metal',p,.004)
for y in [-1.02,1.02]:
    tube('Stretcher grab loop',[(-.22,y,.83),(-.22,y,.91),(.22,y,.91),(.22,y,.83)],.014,'orange',p)
plaque(p,'TRANSFER',(0,-1.055,.77),.46,.09,size=.045)

p=assembly('RESTART_CONSOLE',(-.41,8.55,0),support='Floor',anchors=[[-.75,-.3,0],[.75,-.3,0],[-.75,.3,0],[.75,.3,0]])
p['equipment_type']='restart_console'
for x in [-.77,.77]:
    for y in [-.30,.30]:box('Console steel leg',(x,y,.44),(.065,.065,.88),'darkpaint',p,.005)
box('Console cable apron',(0,.32,.70),(1.72,.12,.40),'bus',p,.005)
box('Console working surface',(0,0,.93),(1.84,.90,.065),'pale',p,.007)
box('Operator sloped panel',(0,.26,1.27),(1.76,.16,.65),'darkpaint',p,.015)
for x in [-.46,.43]:
    box('Monitor bezel',(x,.155,1.38),(.71,.08,.40),'bus',p,.012)
    box('Monitor dark face',(x,.108,1.38),(.64,.012,.33),'black',p,.002)
text('OCRU status title','OCRU 01',(-.74,.098,1.49),.056,'screen',p)
for k,t in enumerate(['POWER / READY','SUIT / PARKED','CARTRIDGE / WAIT','CHAMBER / OPEN']):text('Physical process status',t,(-.74,.098,1.40-k*.047),.030,'screen',p)
text('Employee display title','EMPLOYEE',(.18,.098,1.49),.048,'screen',p)
text('Employee waiting','AWAITING TRANSFER',(.15,.098,1.34),.035,'paper',p)
# Actual guarded switches and a deliberate three-stage physical restart sequence.
for x,label,col in [(-.53,'ARM','yellow'),(-.05,'CONNECT','orange'),(.43,'RESTART','red')]:
    box('Switch base',(x,-.20,.99),(.25,.27,.055),'darkpaint',p,.006)
    cyl('Push button surround',(x,-.20,1.026),.048,.018,'metal',p)
    cyl('Physical pushbutton',(x,-.20,1.042),.035,.022,col,p)
    for xx in [x-.075,x+.075]:beam('Switch finger guard',(xx,-.27,1.025),(xx,-.27,1.13),.014,'metal',p)
    beam('Guarded switch bridge',(x-.075,-.27,1.13),(x+.075,-.27,1.13),.014,'metal',p)
    text('Restart step label',label,(x,-.36,.970),.037,'ink',p,rot=(0,0,0),align='CENTER')
box('Console drawer carcass',(-.53,.02,.50),(.55,.70,.74),'pale',p,.01)
for z in [.40,.63,.82]:
    box('Console drawer front',(-.53,-.342,z),(.51,.025,.17),'pale',p,.005)
    box('Drawer finger pull',(-.53,-.362,z),(.18,.045,.025),'metal',p,.003)
plaque(p,'RESTART STATION',(0,.155,1.76),1.60,.20,size=.105)
st=assembly('OPERATOR_STOOL',(.10,7.95,0));st['mobile_prop']=True
for a in range(5):
    ang=a*math.tau/5;x,y=.20*math.cos(ang),.20*math.sin(ang)
    beam('Stool cast spider',(0,0,.12),(x,y,.08),.03,'metal',st)
    cyl('Stool glide',(x,y,.025),.037,.05,'rubber',st)
cyl('Operator stool pedestal',(0,0,.30),.037,.43,'metal',st)
cyl('Operator stool seat',(0,0,.535),.20,.055,'rubber',st,vertices=48)

p=assembly('CARTRIDGE_BANK',(1.00,8.65,0),support='Floor',anchors=[[-.27,-.23,0],[.27,-.23,0],[-.27,.23,0],[.27,.23,0]])
p['equipment_type']='cartridge_bank'
for x in [-.315,.315]:box('Cartridge bank formed upright',(x,0,1.12),(.075,.69,2.24),'pale',p,.005)
box('Cartridge rack rear',(0,.31,1.12),(.66,.07,2.24),'darkpaint',p,.003)
for z in [.08,.42,.82,1.22,1.62,2.02,2.20]:box('Folded storage shelf',(0,-.005,z),(.64,.63,.035),'metal',p,.004)
for row,z in enumerate([.44,.84,1.24,1.64]):
    for col,x in enumerate([-.18,0,.18]):cartridge(p,x,-.05,z,1+row*3+col)
    box('Shelf retaining lip',(0,-.325,z+.025),(.63,.022,.065),'darkpaint',p,.002)
plaque(p,'CARTRIDGES',(0,-.365,2.13),.65,.13,size=.06)

p=assembly('RESERVE_POWER',(-2.15,8.72,0),support='Floor',anchors=[[-.34,-.22,0],[.34,-.22,0],[-.34,.22,0],[.34,.22,0]])
p['equipment_type']='reserve_power'
box('Battery plinth',(0,0,.07),(.86,.56,.14),'darkpaint',p,.005)
box('Reserve cabinet carcass',(0,0,.74),(.82,.53,1.25),'bus',p,.009)
box('Reserve removable door',(0,-.29,.77),(.75,.05,1.18),'pale',p,.006)
for x in [-.34,.34]:fasteners('Reserve door fastener',[x],[.26,1.24],-.32,p,r=.013)
handle(p,.24,-.35,.79,height=.20)
gauge(p,-.13,-.35,1.10,.09,'RES',.25)
rotary(p,-.13,-.34,.77,'orange')
plaque(p,'RESERVE',(0,-.325,.44),.58,.13,size=.07)
for z in [.35,.43,.51]:box('Cabinet louver',(0,.28,z),(.60,.025,.04),'darkpaint',p,.003)

p=assembly('RECOVERY_BERTH',(3.23,4.70,0),support='Floor',anchors=[[-.42,-.94,0],[.42,-.94,0],[-.42,.94,0],[.42,.94,0]])
p['equipment_type']='recovery_berth'
for x in [-.42,.42]:
    for y in [-.94,.94]:
        cyl('Bed non-marking foot',(x,y,.025),.045,.05,'rubber',p)
        beam('Tubular recovery leg',(x,y,.05),(x,y,.66),.040,'metal',p)
    box('Recovery longitudinal support',(x,0,.59),(.055,2.20,.07),'darkpaint',p,.004)
box('Recovery bed pan',(0,0,.66),(1.13,2.26,.08),'pale',p,.018)
box('Recovery foam cushion',(0,0,.73),(1.02,2.12,.08),'linen',p,.045)
box('Recovery pillow',(0,.73,.81),(.67,.44,.11),'linen',p,.045)
box('Folded recovery blanket',(0,-.70,.80),(.97,.42,.07),'linen',p,.018)
for y in [-1.12,1.12]:tube('Recovery end rail',[(-.49,y,.63),(-.49,y,.90),(.49,y,.90),(.49,y,.63)],.023,'metal',p)
plaque(p,'RECOVERY',(0,-1.17,.58),.67,.10,size=.055)

p=assembly('SUPPLY_BENCH',(3.52,1.47,0),-math.pi/2,support='Floor',anchors=[[-.88,-.3,0],[.88,-.3,0],[-.88,.3,0],[.88,.3,0]])
p['equipment_type']='supply_bench'
for x in [-.88,.88]:
    for y in [-.31,.31]:box('Supply bench leg',(x,y,.43),(.065,.065,.86),'darkpaint',p,.004)
box('Supply bench top',(0,0,.91),(2.07,.85,.07),'pale',p,.009)
box('Bench lower shelf',(0,0,.22),(1.94,.72,.04),'bus',p,.004)
box('Bench rear apron',(0,.35,.59),(1.95,.08,.59),'darkpaint',p,.005)
for x in [-.66,.05,.61]:
    box('Sealed consumable carton',(x,.02,.34),(.39,.49,.20),'paper',p,.012)
    box('Carton adhesive seal',(x,.02,.445),(.043,.49,.008),'orange',p,.001)
box('Folded cleaning cloth',(-.52,0,.976),(.39,.34,.06),'linen',p,.010)
box('Inventory clipboard',(.38,-.07,.965),(.29,.40,.025),'darkpaint',p,.004)
box('Inventory paper',(.38,-.07,.980),(.26,.36,.003),'paper',p,.001)
text('Clipboard title','SHIFT LOG',(.28,.04,.984),.028,'ink',p,rot=(0,0,0))
for y in [-.16,-.11,-.06,-.01]:box('Inventory ruled line',(.38,y,.984),(.20,.001,.001),'ink',p,bevel=0)

p=assembly('SUPPLY_CABINET',(3.61,7.47,0),-math.pi/2,support='East wall',anchors=[[-.7,.39,1.8],[.7,.39,1.8]],direction=[0,1,0]);p['equipment_type']='supplies'
for x in [-.70,.70]:
    for z in [1.4,2.3]:box('Cabinet wall spacer',(x,.3775,z),(.12,.025,.12),'darkpaint',p,.002)
box('Supply cabinet back',(0,.32,1.88),(1.88,.09,1.18),'darkpaint',p,.004)
for x in [-.91,.91]:box('Cabinet formed edge',(x,0,1.88),(.065,.67,1.22),'pale',p,.006)
for z in [1.28,1.69,2.09,2.48]:box('Supply cabinet shelf',(0,0,z),(1.88,.67,.04),'metal',p,.004)
for x in [-.63,-.19,.26,.68]:
    for z in [1.32,1.74,2.13]:
        box('Sealed supply case',(x,.04,z+.13),(.32,.46,.24),'paper',p,.006)
        box('Supply case tab',(x,-.195,z+.13),(.05,.006,.17),'orange',p,.001)
for x in [-.47,.47]:box('Clear cabinet sliding pane',(x,-.36,1.89),(.90,.022,1.10),'glass',p,.002)
for x in [-.12,.12]:handle(p,x,-.39,1.86,height=.16)
