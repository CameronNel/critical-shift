"""Expansion of the reviewed workshop construction language. Executed by build.py."""
# Material families retain broad values and selective use marks, not uniform gloss.
mapping={'Warm precast concrete':'cream','Dry ground concrete':'floor','Warm grey enamel':'enamel',
 'Oxide orange painted steel':'oxide','Structural warm graphite':'slate','Brushed galvanized steel':'steel',
 'Galvanized bus casing':'zinc','Bus copper - aged':'copper','Insulating rubber':'rubber',
 'Porcelain standoff':'ceramic','Standby ochre enamel':'ochre','Ochre safety enamel':'ochre',
 'Exposed ochre primer':'oxide','Work order paper':'paper','Cotton electrician rag':'cloth',
 'Switch housing phenolic':'rubber','Printed charcoal':'ink','Elastomer joint filler':'rubber',
 'Replacement concrete':'cream','Instrument glass':'glass','Exposed steel at contact wear':'steel'}
for o in bpy.data.objects:
    if not o.name.startswith(k.PREFIX) and hasattr(o.data,'materials'):
        for slot in o.material_slots:
            if slot.material and slot.material.name in mapping:slot.material=m[mapping[slot.material.name]]
# Remove painted-on wall reveals, retain exact owned shell/threshold geometry.
k.remove_members(['Precast horizontal reveal','Precast vertical reveal'])
k.collection('Architectural finish')
k.root('West wall finish','West wall',[[-5.5,1,2],[-5.5,10,2]],'WORLD_-X')
for y in [1.2,3.44,5.68,7.92,10.16]:
    k.box('West mineral return panel',(-5.49,y,2.87),(.02,2.218,2.54),m['cream'],.002)
    k.box('West folded impact liner',(-5.482,y,.85),(.036,2.218,1.48),m['slate'],.003)
    k.box('West liner seated cap',(-5.46,y,1.605),(.072,2.218,.025),m['zinc'])
k.root('East wall finish','East wall south field',[[5.5,2,2]],'WORLD_+X')
# Resolve the measured support target from the saved architecture, not an invented name.
east=[o for o in bpy.data.objects if o.type=='MESH' and 'Architecture' in [c.name for c in o.users_collection] and o.name.startswith('East')]
if east:k.ASSEMBLY['cs_support_target']=east[0].name
for y in [1.15,3.45,5.75,8.05,10.2]:
    w=2.27 if y!=10.2 else 1.55
    k.box('East mineral return panel',(5.49,y,2.88),(.02,w,2.52),m['cream'],.002)
    k.box('East folded impact liner',(5.482,y,.85),(.036,w,1.48),m['slate'],.003)
    k.box('East liner seated cap',(5.46,y,1.605),(.072,w,.025),m['zinc'])
# Walk-height-preserving finish: 1.4 mm dimensional epoxy panel overlays.
k.root('Aisle floor finish','Floor',[[-.6,.6,0],[.6,15.68,0]])
for j in range(14):
    y=.6+j*1.16
    if y>16.3:continue
    for x in [-.60,.60]:
        ob=k.box('Aisle epoxy slab',(x,y,.0007),(1.188,1.148,.0014),m['route'],.0003)
        ob['intentional_surface_overlay']=True
for x in [-1.205,1.205]:
    for y in [1.2,4.4,7.6,10.8,14.0]:k.box('Recessed route boundary',(x,y,.0006),(.024,1.2,.0012),m['ochre'],.0002)
# Switchgear: physical door returns, compression seals and variant removable cassettes.
k.collection('Switchgear construction')
for i,y in enumerate([3.9,5.1,6.3,7.5,8.7,9.9]):
    member=['SG01_Incoming_turbine','SG02_Main_bus','SG03_COOLING','SG04_PRODUCTION','SG05_FACILITY','SG06_SERVICE'][i]
    k.root('Switchgear '+str(i+1), 'Anchored channel plinth' if i==0 else 'Anchored channel plinth.'+str(i).zfill(3),[[-3.695,y,.13]])
    k.box('Cabinet lower frame seat',(-3.695,y,.15),(.05,1.09,.04),m['slate'])
    k.ring('Cabinet folded front frame',-3.693,y,1.47,1.09,2.48,.021,.05,m['slate'])
    if i<5:
        k.ring('Door recessed compression seal',-3.70,y,1.12,1.045,1.255,.012,.01,m['rubber'])
        k.ring('Door rolled edge return',-3.656,y,1.12,1.038,1.238,.009,.016,m['steel'])
        if i==3:
            for o in bpy.data.objects:
                if o.get('assembly_member')==member and o.name.startswith('Breaker access door'):
                    o.data.materials.clear();o.data.materials.append(m['replacement'])
                    for slot in o.material_slots:slot.material=m['replacement']
        # Wear is at the latch/contact zone, with irregular length and a quiet door field.
        for j in range(5):k.box('Latch contact edge nick',(-3.642,y+.405,1.05+j*.019),(.002,.024+j%2*.008,.003),m['steel'],.0005)
    k.ring('Instrument cassette returned rim',-3.656,y,2.20,1.03,.88,.018,.026,m['zinc'])
    for yy in [y-.43,y+.43]:
        for z in [1.84,2.53]:k.bolt('Cassette captive fixing',(-3.637,yy,z),(1,0,0),m['steel'],.008)
    # Casing takeoff is maintained. Add folded joint collar, fixings and cable boots.
    k.box('Takeoff joint return',(-3.969,y,3.41),(.028,.64,.045),m['slate'])
    for yy in [y-.25,y+.25]:k.bolt('Takeoff panel screw',(-3.948,yy,3.425),(1,0,0),m['zinc'],.010)
    k.cyl('Protection wiring compression gland',(-4.99,y,2.20),(-5.08,y,2.20),.025,m['slate'],12)
    k.tube('Cabinet grounding tail',[(-4.90,y,.22),(-5.10,y,.20),(-5.20,y,.20)],.006,m['copper'])
# Incoming and service mechanisms stay separately editable and in their original positions.
for o in bpy.data.objects:
    if o.name.startswith(('Tapered tap-off transition','Tap flange','Crown rain lip')):
        o.data.materials.clear();o.data.materials.append(m['slate'])
        for slot in o.material_slots:slot.material=m['slate']
# Differing maintenance histories: quiet cooling paint, new production panel,
# frequently handled incoming/service units. Avoid cloning identical wear arrays.
wear_counts={}
for o in sorted(list(bpy.data.objects),key=lambda o:o.name):
    member=o.get('assembly_member','')
    if o.name.startswith(('Localized chipped paint','Wear at repeatedly handled edge')) and member in ['SG02_Main_bus','SG03_COOLING','SG04_PRODUCTION','SG05_FACILITY']:
        index=wear_counts.get(member,0);wear_counts[member]=index+1
        keep=(index%3==0) if member=='SG02_Main_bus' else (index%4==0) if member=='SG03_COOLING' else (index%2==0) if member=='SG05_FACILITY' else False
        if not keep:bpy.data.objects.remove(o,do_unlink=True)
for o in bpy.data.objects:
    if o.type=='FONT' and o.get('assembly_member')=='SG06_SERVICE' and o.name.startswith('Relay reading'):
        o.data=o.data.copy();o.data.body='SERVICE';o.data.size*=.78
# Rebuild all three hero windings as assembled coils with stacked cooling channels.
k.collection('Transformer winding rebuild')
k.remove_members(['Cast resin coil body','Cast coil cooling band'])
for i,y in enumerate([5.49,6.40,7.31]):
    k.root('Transformer coil '+str(i+1),'Coil insulating saddle' + ('.'+str(4-i*2).zfill(3) if i<2 else ''),[[4.295,y,.785]])
    prof=[(0,0),(.275,0),(.325,.024),(.341,.066),(.337,.11)]
    for j in range(7):
        z=.12+j*.14;prof.extend([(.337,z),(.346,z+.015),(.346,z+.05),(.322,z+.067),(.322,z+.078),(.337,z+.095)])
    prof.extend([(.337,1.17),(.32,1.215),(.28,1.235),(0,1.235)])
    k.lathe('Cast resin winding channel', (4.295,y,.785),prof,m['oxide'],48)
    # Copper taps emerge from side cooling windows and meet the top terminal hardware.
    for j in range(3):
        z=1.03+j*.28
        k.tube('Exposed copper winding tap',[(3.967,y-.19,z),(3.943,y-.12,z),(3.943,y+.12,z),(3.967,y+.19,z)],.013,m['copper'])
    for z in [.814,1.968]:
        k.lathe('Winding compression band',(4.295,y,z),[(.349,0),(.349,.042),(.324,.042),(.324,0),(.349,0)],m['ochre'],48)
    for yy in [y-.25,y+.25]:
        k.box('Coil spacer shoe',(4.295,yy,.75),(.52,.10,.07),m['ceramic'],.007)
        k.bolt('Coil clamping nut',(4.01,yy,2.087),(0,0,1),m['steel'])
# Actual end connection on the earth strap, fine cross strands, no floating endpoints.
k.root('Transformer earth braid','Transformer earth anchor',[[5.085,4.95,.36]])
for j in range(6):
    path=[(5.055,5.2,.42),(5.10+j*.003,5.18,.38),(5.085+j*.003,5.08,.31),(5.085+j*.003,4.95,.30)]
    k.tube('Earth braid strand',path,.0025,m['copper'])
for y in [5.2,4.95]:k.bolt('Earth strap terminal',(5.085,y,.361 if y==4.95 else .46),(0,0,1),m['steel'],.008)
# Lifting eyes in the original upper yoke, not decorative greebling.
for y in [5.05,7.73]:
    k.root('TX lift bracket '+str(y),'Laminated core yoke.001',[[4.315,y,2.5]])
    k.box('Lifting eye base',(4.315,y,2.512),(.28,.20,.024),m['steel'])
    k.lathe('Lifting eye',(4.315,y,2.58),[(.071,-.012),(.071,.012),(.041,.012),(.041,-.012),(.071,-.012)],m['steel'],rot=Matrix.Rotation(math.pi/2,3,'X'))
    for x in [4.22,4.41]:k.bolt('Lifting eye anchor',(x,y,2.524),(0,0,1),m['zinc'])
# Reserve racks: individually returned access panels, cell banks and seat hardware.
k.collection('Reserve and transfer refinements')
k.remove_members(['Sealed reserve cell module'])
cellcase=k.material('Moulded reserve cell casing',(.16,.18,.17),.76,0,.0003)
for i,y in enumerate([12.18,13.20,14.22]):
    k.root('Reserve service rack '+str(i+1),'Reserve anchored base'+('' if i==0 else '.'+str(i).zfill(3)),[[7.45,y,.20]])
    k.box('Rack service toe rail',(7.45,y,.226),(.032,.88,.052),m['slate'])
    k.ring('Reserve panel seal',7.44,y,2.09,.86,.456,.009,.013,m['rubber'])
    for yy in [y-.364,y+.364]:
        for z in [1.91,2.27]:k.bolt('Reserve quarter turn fastener',(7.425,yy,z),(-1,0,0),m['zinc'],.008)
    for j,z in enumerate([.55,1.08,1.61]):
        bottom=[.35,.90,1.45][j]
        # Ribbed two-piece moulded battery case, with lid joint, returned flange,
        # recessed service face and terminal cover. Original tray and handles stay.
        k.box('Reserve moulded cell case',(7.785,y,bottom+.198),(.54,.782,.396),cellcase,.018)
        k.box('Cell seated top lid',(7.785,y,bottom+.400),(.56,.79,.028),m['replacement'],.008)
        k.box('Cell front lid seam',(7.505,y,bottom+.372),(.014,.746,.012),m['rubber'],.002)
        for yy in [y-.355,y-.272,y-.19,y+.19,y+.272,y+.355]:
            k.box('Cell moulded reinforcing rib',(7.50,yy,bottom+.198),(.025,.013,.31),cellcase,.004)
        k.box('Cell recessed service face',(7.492,y,bottom+.195),(.028,.45,.228),m['replacement'],.007)
        k.box('Cell embossed record plate',(7.474,y,bottom+.265),(.009,.23,.036),m['ceramic'],.002)
        k.text('Cell batch record',f'{i+1}{j+1} / 48V',(7.468,y+.098,bottom+.254),.021,m['ink'],'-X')
        for yy in [y-.205,y+.205]:
            k.bolt('Cell service face fixing',(7.472,yy,bottom+.30),(-1,0,0),m['zinc'],.006)
        k.box('Battery retained front rail',(7.45,y,z-.16),(.034,.77,.053),m['slate'])
        for yy in [y-.30,y+.30]:k.bolt('Battery tray keeper',(7.431,yy,z-.16),(-1,0,0),m['zinc'],.008)
        k.box('Cell interconnect cover',(7.49,y,z+.05),(.05,.54,.115),m['rubber'],.012)
        for yy in [y-.22,y+.22]:
            k.cyl('Cell covered terminal',(7.44,yy,z+.08),(7.48,yy,z+.08),.025,m['copper'])
        for yy in [y-.32,y+.32]:
            k.tube('Battery pull loop',[(7.452,yy-.028,z),(7.40,yy-.028,z),(7.40,yy+.028,z),(7.452,yy+.028,z)],.007,m['rubber'])
    for yy in [y-.33,y+.33]:k.box('Rack vent lower return',(7.457,yy,2.19),(.025,.016,.19),m['steel'])
    if i==1:
        # The real visible fascia carries the replacement finish; no hidden overlay.
        panel=bpy.data.objects['Reserve upper panel.001']
        panel.data.materials.clear();panel.data.materials.append(m['replacement'])
        for slot in panel.material_slots:slot.material=m['replacement']
        k.box('Rack dated inspection card',(7.426,y-.29,1.88),(.004,.18,.08),m['paper'],.001)
        k.box('Rack inspection spring clip',(7.422,y-.29,1.915),(.008,.037,.019),m['steel'],.002)
        k.text('Rack inspection record','TEST 06',(7.421,y-.215,1.907),.021,m['ink'],'-X')
k.root('Transfer panel bezel','Transfer base',[[4.414,10.3,.18]])
k.box('Transfer frame lower seat',(4.414,10.3,.35),(.026,.10,.34),m['slate'])
# Rear side of -X-facing annulus is sealed by the existing service fascia.
k.ring('Transfer stepped fascia rim',4.414,10.3,1.39,1.50,1.74,.016,.026,m['slate'])
k.ring('Transfer recessed control cassette',4.382,10.3,1.3725,1.42,1.365,.012,.022,m['zinc'])
for y in [9.60,11.00]:
    for z in [.82,2.02]:k.bolt('Transfer captive cassette screw',(4.36,y,z),(-1,0,0),m['steel'],.008)
# Maintenance trolley rebuild; retain actual position and circulation footprint.
cart=bpy.data.objects.get('Electrician service cart')
if cart:
    descendants=set(cart.children_recursive);descendants.add(cart)
    for o in descendants:bpy.data.objects.remove(o,do_unlink=True)
k.collection('Trolley and lockout details')
k.root('Maintenance trolley','Floor',[[-4.71,1.5,0],[-4.19,1.5,0],[-4.71,2.1,0],[-4.19,2.1,0]])
for x in [-4.71,-4.19]:
    for y in [1.5,2.1]:
        k.lathe('Castor rubber tyre',(x,y,.085),[(.065,-.022),(.077,-.02),(.085,-.01),(.085,.01),(.077,.02),(.055,.02),(.055,-.022),(.065,-.022)],m['rubber'],rot=Matrix.Rotation(math.pi/2,3,'Y'))
        k.cyl('Castor wheel axle',(x-.028,y,.085),(x+.028,y,.085),.029,m['zinc'])
        for xx in [x-.024,x+.024]:k.box('Castor pressed fork',(xx,y,.14),(.009,.064,.12),m['steel'])
        k.cyl('Castor swivel stem',(x,y,.19),(x,y,.23),.025,m['steel'])
        k.box('Trolley post',(x,y,.565),(.024,.024,.67),m['slate'])
for z in [.27,.86]:
    k.box('Trolley tray floor',(-4.45,1.8,z),(.65,.77,.026),m['replacement'],.003)
    for x in [-4.774,-4.126]:k.box('Trolley tray side return',(x,1.8,z+.024),(.015,.77,.055),m['replacement'])
    for y in [1.422,2.178]:k.box('Trolley tray end return',(-4.45,y,z+.024),(.63,.015,.055),m['replacement'])
k.tube('Trolley bowed pushbar',[(-4.71,2.12,.87),(-4.71,2.25,1.02),(-4.19,2.25,1.02),(-4.19,2.12,.87)],.016,m['slate'])
k.tube('Pushbar rubber grip',[(-4.6,2.25,1.02),(-4.3,2.25,1.02)],.022,m['rubber'])
# Molded multimeter has open guard returns, inset display and a physical selector.
k.root('Tray seated multimeter','EOH | Trolley tray floor.001',[[-4.50,1.75,.873]])
k.box('Meter protective bumper',(-4.50,1.75,.917),(.19,.29,.086),m['ochre'],.014)
k.box('Meter recessed body',(-4.50,1.75,.929),(.155,.265,.075),m['slate'],.012)
k.box('Meter LCD inset',(-4.50,1.82,.969),(.13,.072,.005),m['glass'],.002)
k.text('Meter readout','240.0',(-4.557,1.807,.972),.029,m['paper'],'Z')
k.cyl('Meter rotary bezel',(-4.50,1.714,.967),(-4.50,1.714,.973),.049,m['steel'])
k.box('Meter range selector',(-4.50,1.714,.981),(.019,.083,.016),m['rubber'],.003)
for i in range(8):
    angle=i*math.tau/8;k.box('Meter range tick',(-4.50+.059*math.cos(angle),1.714+.059*math.sin(angle),.968),(.006,.003,.001),m['paper'],0)
for y,color in [(1.64,m['redrubber']),(1.675,m['rubber'])]:
    k.cyl('Meter test jack',(-4.45,y,.9665),(-4.45,y,.982),.008,m['zinc'])
for j,(x,base_y,color) in enumerate([(-4.25,1.87,m['redrubber']),(-4.30,1.91,m['rubber'])]):
    k.root('Tray seated probe '+str(j),'EOH | Trolley tray floor.001',[[x,base_y+.01,.873],[x,base_y+.119,.873]])
    k.lathe('Probe moulded heel and finger guard',(x,base_y,.887),[(0,0),(.012,0),(.014,.006),(.014,.016),(.010,.022),(.010,.110),(.014,.115),(.014,.124),(.006,.130),(.003,.150),(0,.150)],color,32,Matrix.Rotation(-math.pi/2,3,'X'))
    for offset in [.04,.066,.092]:
        k.lathe('Probe grip knurl band',(x,base_y+offset,.887),[(.0105,0),(.0105,.006),(.009,.006),(.009,0),(.0105,0)],color,24,Matrix.Rotation(-math.pi/2,3,'X'))
    k.cyl('Probe metal contact tip',(x,base_y+.145,.887),(x,base_y+.20,.887),.002,m['steel'])
    jack_y=[1.64,1.675][j]
    k.tube('Resting test lead',[(-4.45,jack_y,.980),(-4.37,jack_y,.928),(-4.33,1.57+j*.025,.885),(-4.22+j*.025,1.59+j*.025,.877),(-4.20+j*.025,1.73,.877),(x,base_y,.887)],.003,color)
k.root('Tray clipped service record','EOH | Trolley tray floor.001',[[-4.62,2.04,.873]])
k.box('Trolley service record',(-4.62,2.04,.8745),(.18,.22,.003),m['paper'],.0006)
k.box('Trolley record folded clip',(-4.62,2.143,.879),(.040,.014,.009),m['steel'],.002)
k.text('Trolley repair tag','06  /  REPAIR',(-4.70,2.055,.8762),.014,m['ink'],'Z')
for y in [2,2.02,2.04]:k.box('Trolley record rule',(-4.62,y,.8762),(.14,.001,.0004),m['ink'],0)
k.root('Lower tray folded wiping cloth','EOH | Trolley tray floor',[[-4.43,1.77,.283]])
def rag(b):
    b.ribbon([(1.68,.284),(1.74,.284),(1.83,.288),(1.94,.285),(1.98,.295),(1.94,.306),(1.79,.312),(1.73,.317),(1.84,.327),(1.95,.326)],-4.60,-4.28,.006,m['cloth'])
k.add('Layered folded lower tray rag',rag)
for x in [-4.593,-4.287]:
    k.tube('Rag returned stitched hem',[(x,1.73,.320),(x,1.84,.330),(x,1.95,.329)],.002,m['paper'])
# Mounted utilities: galvanized conduit, proper saddles and compression glands.
k.root('Workbench service conduit','West wall',[[-5.5,12,2.4],[-5.5,15.4,2.4]],'WORLD_-X')
k.tube('Workshop service conduit',[(-5.443,11.8,2.44),(-5.443,15.45,2.44),(-5.443,15.56,2.34),(-5.443,15.56,1.90)],.017,m['zinc'])
k.box('Workshop supply junction box',(-5.446,11.79,2.44),(.108,.21,.19),m['slate'],.006)
k.ring('Supply junction returned cover',-5.384,11.79,2.44,.194,.174,.01,.016,m['zinc'])
for yy in [11.72,11.86]:k.bolt('Supply cover captive fixing',(-5.374,yy,2.44),(1,0,0),m['steel'],.007)
for y in [12,13.7,15.4]:
    k.box('Conduit saddle wall plate',(-5.489,y,2.44),(.022,.11,.14),m['slate'])
    k.tube('Conduit saddle', [(-5.478,y-.036,2.44),(-5.42,y-.036,2.44),(-5.42,y+.036,2.44),(-5.478,y+.036,2.44)],.007,m['steel'])
k.box('Workshop termination box',(-5.44,15.56,1.85),(.10,.22,.18),m['slate'],.006)
k.ring('Termination removable cover',-5.379,15.56,1.85,.204,.164,.009,.012,m['zinc'])
# Practical hierarchy. Each source fixture remains present; tune its actual light.
energies={'Entry fluorescent light':100,'West task fluorescent light':245,'West rear practical light':225,
 'Transformer task practical light':340,'Transfer task practical light':200,'Rear hall practical light':130,'Reserve bay practical light':240}
for o in bpy.data.objects:
    if o.type=='LIGHT' and o.name in energies:
        o.data.energy=energies[o.name];o.data.color=(.80,.87,1) if 'West' in o.name or 'Reserve' in o.name else (1,.86,.68)
# Quiet architecture gets broad bounce while work stations receive local falloff.
if bpy.context.scene.world and bpy.context.scene.world.use_nodes:
    bg=bpy.context.scene.world.node_tree.nodes.get('Background')
    if bg:bg.inputs['Strength'].default_value=.055
exec((Path(__file__).with_name('refine_doors.py')).read_text(),globals())
exec((Path(__file__).with_name('use_history.py')).read_text(),globals())
