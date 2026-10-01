"""Root-authored dock expansion; called only after the independent slice gate.

Native placements and named interaction parts survive all construction repairs.
This file uses the parent builder's measured metric construction helpers.
"""

def full_palette():
    mapping={'brass_plate':'brass','burgundy_authority':'coral','cast_iron':'charcoal',
        'emissive_amber':'amber_lamp','emissive_green':'green_lamp','emissive_red':'red_lamp',
        'emissive_warm_white':'warm_lamp','fabric_canvas':'fabric','floor_concrete':'concrete',
        'glass_clean':'glass','ink_black':'ink','paper_sheet':'paper','rubber_dark':'rubber',
        'safety_amber':'yellow','safety_stripe':'yellow','screen_amber':'screen','steel_frame':'navy',
        'steel_gunmetal':'charcoal','steel_machined':'steel','wall_dark':'charcoal',
        'wall_neutral':'plaster','wall_wainscot':'navy','webbing_strap':'rubber','wood_laminate':'wood'}
    for o in S.objects:
        if o.type not in {'MESH','CURVE','FONT'}:continue
        for i,m in enumerate(list(o.data.materials)):
            if m and m.name in mapping:o.data.materials[i]=MATERIALS[mapping[m.name]]
        if o.type=='MESH':uv(o)
    # Inset plates are painted steel; rubber remains only at real seals, feet,
    # curtains and grip surfaces. Broad concrete stays quiet.
    for o in S.objects:
        if o.type!='MESH':continue
        if 'column inset' in o.name:assign(o,'blue')
        elif 'Sensor emitter' in o.name:assign(o,'charcoal')
        elif 'Tunnel stiffener' in o.name:assign(o,'blue')
        elif 'Filing cabinet body' in o.name:assign(o,'blue')
        elif 'Drawer face' in o.name:assign(o,'navy')
        elif 'Vault carcass' in o.name:assign(o,'navy')
        elif 'Locker door' in o.name:assign(o,'blue')
        elif 'Fixture Housing' in o.name:assign(o,'ivory')
        elif 'Tube ' in o.name:assign(o,'warm_lamp')
    handling_wear(S.objects['Floor slab'],'Floor traffic polish',(1.1,7.9,0),(2.15,6.4,.015),(.24,.245,.25),.24)

def octagon(w,h,cut):
    return [(-w/2+cut,-h/2),(w/2-cut,-h/2),(w/2,-h/2+cut),(w/2,h/2-cut),
        (w/2-cut,h/2),(-w/2+cut,h/2),(-w/2,h/2-cut),(-w/2,-h/2+cut)]

def tapered(name,loc,dims,axis,key,taper=.80,cut=.018,w=.001):
    # A clipped rectangular front, drafted shoulder and smaller rear shell.
    other=[k for k in range(3) if k!=axis];ww,hh=[dims[k] for k in other];depth=dims[axis]
    vs=[]
    for d,scale in [(-depth/2,1),(-depth*.32,1),(depth/2,taper)]:
        for q in octagon(ww*scale,hh*scale,min(cut,ww*.12,hh*.12)):
            v=list(loc);v[axis]+=d;v[other[0]]+=q[0];v[other[1]]+=q[1];vs.append(v)
    fs=[tuple(range(7,-1,-1)),tuple(range(16,24))]
    for k in range(2):fs.extend((k*8+i,k*8+(i+1)%8,(k+1)*8+(i+1)%8,(k+1)*8+i) for i in range(8))
    o=mesh(name,vs,fs,key,w);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();return o

def reposition_parent(o,parent):
    world=o.matrix_world.copy();o.parent=parent;o.matrix_world=world;o['assembly']=parent.name
    if o.get('support_class')!='supported_assembly':o['support_class']='assembly_component'

def contact_fixture(name,target,points,direction,children):
    root=asset_root(name,target,points,direction)
    for o in children:reposition_parent(o,root)
    return root

def scanner_detail():
    use_root('Person Scanner Arch')
    # Retain the 1.20m inner clearance; shape only outside the interface.
    for side in [-1,1]:
        x=.73*side
        pts=[(x-.12,-.18),(x+.12,-.18),(x+.12,.12),(x+.09,.18),(x-.09,.18),(x-.12,.12)]
        replace('Scanner portal column '+str(side),profile('TEMP scanner extrusion',pts,2.7,2,(0,7,1.35),'navy',.003),'Folded six-face inspection column; native pose and inner clearance preserved')
        for z in [.18,2.52]:
            box('CD | Scanner service collar',(x,6.811,z),(.18,.018,.105),'blue',.001)
            for xx in [x-.067,x+.067]:bolt('CD | Scanner collar screw',(xx,6.797,z),r=.004)
        for j in range(6):
            z=.4+.36*j
            replace(f'Sensor optic {side}_{j}',cyl('TEMP optic',(.615*side,7,z),.035,.01,'lens','X',vertices=16,w=.0007),'Optical axis faces the passage; original origin/matrix retained')
            cyl('CD | Sensor metal lens seat',(.62*side,7,z),.042,.007,'steel','X',vertices=16,w=.0005)
        for z in [.62,.78,.94]:
            box('CD | Scanner ventilation slit',(x,7.181,z),(.15,.001,.009),'ink',.0003)
    replace('Scanner portal lintel',profile('TEMP scanner header',octagon(1.7,.26,.045),.36,1,(0,7,2.78),'navy',.003),'Angular folded inspection bridge, unchanged outer header dimensions')
    for x in [-.65,.65]:box('CD | Scanner bridge joint',(x,6.813,2.78),(.09,.024,.20),'steel',.002)
    # Central instruction is retained; hardware makes it a real sign face.
    for x in [-.69,.69]:bolt('CD | Scanner instruction screw',(x,6.791,2.78),r=.005)

def cargo_detail():
    use_root('Cargo Inspection Conveyor')
    pts=[(-.75,-.7),(-.60,-.7),(-.60,.30),(.60,.30),(.60,-.7),(.75,-.7),(.75,.62),(.67,.7),(-.67,.7),(-.75,.62)]
    replace('Lead tunnel main body',profile('TEMP real cargo U shell',pts,2.3,1,(4.65,7.65,1.45),'blue',.004),'Open-ended U-shaped shield housing replaces inherited solid cube; same outer envelope, belt passage is real')
    liner=[(-.60,-.50),(-.596,-.50),(-.596,.496),(.596,.496),(.596,-.50),(.60,-.50),(.60,.50),(-.60,.50)]
    replace('Lead tunnel inner chamber',profile('TEMP real cargo liner',liner,2.32,1,(4.65,7.65,1.25),'charcoal',0),'4mm manufactured inner U liner, open along belt; inherited local/world matrix retained')
    # Remove duplicate buried fin volumes with true shallow external ribs.
    for o in list(S.objects):
        if not o.name.startswith('Tunnel stiffener '):continue
        x,y,z=o.matrix_world.translation
        side=-1 if x<4.65 else 1
        shape=[(-.025,-.66),(.025,-.66),(.025,.61),(.013,.66),(-.013,.66),(-.025,.61)]
        replace(o.name,profile('TEMP tunnel rib',shape,.034,0,(3.883 if side<0 else 5.417,y,z),'blue',.001),'Exterior pressed shield stiffener physically bears on outer skin')
        for zz in [.89,2.01]:cyl('CD | Cargo rib captive screw',(3.863 if side<0 else 5.437,y,zz),.007,.006,'steel','X',vertices=6,w=.0005)
    for y in [6.486,8.814]:
        box('CD | Shield mouth hem',(4.65,y,2.10),(1.24,.028,.042),'steel',.002)
    # Individual hanging leaves have restrained folds rather than plastic slabs.
    for o in list(S.objects):
        if not o.name.startswith('Lead curtain strip '):continue
        x,y,z=o.matrix_world.translation
        pts=[(-.065,-.48),(.052,-.48),(.065,-.466),(.065,.48),(-.065,.48)]
        replace(o.name,profile('TEMP rubber curtain',pts,.015,1,(x,y,z),'rubber',.001),'Clipped heavy rubber curtain leaves, retained curtain opening and hang points')
    for x,y in [(4.05,6.65),(4.05,8.65),(5.25,6.65),(5.25,8.65)]:
        old=f'Lifting eyebolt ring {x}_{y}'
        if old not in S.objects:continue
        replace(old,torus('TEMP lifting eye',(x,y,2.205),.035,.009,'steel','Y'),'Vertical forged lifting eye joined to retained stem; original pose matrix preserved')
    # Real side access plates and service hatch, kept within the east service lane.
    for y in [7.1,8.17]:
        q=profile('CD | Cargo service access cover',octagon(.50,.45,.035),.006,0,(5.403,y,1.28),'navy',.001)
        for yy in [y-.20,y+.20]:
            for z in [1.105,1.455]:cyl('CD | Cargo captive cover screw',(5.409,yy,z),.006,.006,'steel','X',vertices=6,w=.0005)
    for i in [0,1]:
        y=7.35+i*.6
        replace('Conveyor monitor housing '+str(i),tapered('TEMP cargo monitor',(3.35,y,1.3),(.28,.38,.30),0,'plastic',.75,.021),'Drafted industrial monitor housing; retained screen and console anchors')
        # Existing east-facing screen is backed by the housing, not floating.
        for zz in [1.18,1.22,1.26]:box('CD | Cargo monitor rear vent',(3.208,y,zz),(.002,.22,.009),'ink',0)
        box('CD | Cargo monitor pedestal',(3.35,y,1.058),(.075,.10,.236),'charcoal',.003)
    for x in [3.98,5.32]:
        # Chassis cross member actually joins retained leg/roller supports.
        box('CD | Cargo chassis lower tie',(x,7.65,.59),(.05,4.48,.07),'navy',.001)
    for y in [5.4,9.9]:box('CD | Cargo chassis end tie',(4.65,y,.67),(1.34,.05,.10),'navy',.001)
    # Two steel bands, captive corner guards and lid seam articulate the crate.
    for y in [5.56,6.14]:
        box('CD | Cargo crate band',(4.65,y,1.443),(.76,.024,.006),'steel',.001)
        for x in [4.272,5.028]:box('CD | Cargo crate band side',(x,y,1.13),(.006,.024,.62),'steel',.001)
    for x in [4.32,4.98]:
        box('CD | Cargo crate front corner',(x,5.371,1.115),(.045,.008,.47),'charcoal',.001)
        for z in [.96,1.26]:bolt('CD | Crate corner rivet',(x,5.365,z),r=.004)
    handling_wear(S.objects['Cargo crate lid'],'Crate handling polish',(4.68,5.75,1.44),(.32,.37,.01),(.26,.19,.11),.35)

def office_detail():
    use_root('Staff Desk Assembly')
    replace('Terminal monitor housing',tapered('TEMP CRT housing',(-3.35,6.8,1.05),(.34,.42,.32),0,'plastic',.66,.035,.002),'Drafted CRT shell and shoulder, existing screen plane/pivot retained')
    for y in [6.665,6.69,6.715,6.74,6.765,6.79,6.815,6.84,6.865,6.89,6.915,6.94]:
        box('CD | CRT top ventilation slot',(-3.27,y,1.193),(.105,.009,.002),'ink',0)
    for y in [6.69,6.79,6.89]:cyl('CD | CRT rear cover screw',(-3.178,y,1.075),.0035,.004,'steel','X',vertices=6,w=.0003)
    # Existing rows become disconnected, closed individual molded keycaps.
    for row in range(5):
        x=-3.74+row*.022;vs=[];fs=[]
        for j in range(12):
            y=6.652+j*.0268;start=len(vs)
            vs.extend((xx,yy,zz) for zz in [.784,.795] for yy in [y-.0105,y+.0105] for xx in [x-.0065,x+.0065])
            fs.extend(tuple(start+k for k in f) for f in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)])
        replace('Keyboard keyrow '+str(row),mesh('TEMP keycaps',vs,fs,'ivory',.0007),'Individual keycaps with real spacing, preserved keyboard row object and pose')
    # Table joinery, modesty-panel folded hem, and useful cable management.
    for x in [-4.05,-2.95]:
        for y in [6.05,7.55]:
            box('CD | Desk top support shoe',(x,y,.708),(.12,.12,.024),'steel',.001)
            for yy in [y-.042,y+.042]:cyl('CD | Desk captive top fixing',(x,yy,.722),.004,.004,'steel',vertices=6,w=.0003)
    box('CD | Desk cable trough',(-2.985,6.8,.66),(.12,1.28,.035),'charcoal',.002)
    box('CD | Desk modesty lower hem',(-2.952,6.8,.374),(.035,1.45,.012),'navy',.001)
    # Grounded handset with both receivers resting in an actual cradle.
    replace('Handset earpiece',tapered('TEMP handset front receiver',(-3.30,7.35,.81),(.06,.065,.04),2,'plastic',.88,.01),'Molded handset receiver seated on retained cradle')
    box('CD | Handset second receiver',(-3.41,7.35,.81),(.06,.065,.04),'plastic',.008)
    profile('CD | Handset curved bridge',[(-.085,-.006),(.085,-.006),(.075,.008),(.025,.021),(-.025,.021),(-.075,.008)],.029,1,(-3.355,7.35,.827),'plastic',.002)
    for x in [-3.30,-3.41]:box('CD | Handset cradle perch',(x,7.35,.798),(.032,.045,.016),'charcoal',.002)
    # Separate unrelated furniture from the rotating chair assembly.
    for k,y in enumerate([8.3,9.1]):
        children=[o for o in S.objects if o.parent and o.parent.name=='Ergonomic Swivel Chair' and (o.name=='Filing cabinet body '+str(k) or any(o.name.startswith(s+str(k)+'_') for s in ['Drawer face ','Drawer pull ','Drawer cardholder ']))]
        contact_fixture('Office file cabinet '+str(k),'Floor slab',[(-6.5,y-.22,0),(-6.18,y+.22,0)],(0,0,-1),children)
    children=[o for o in S.objects if o.name.startswith(('Office coat rack','Coat hook '))]
    contact_fixture('Office coat stand','Floor slab',[(-6.5,4.2,0)],(0,0,-1),children)
    children=[S.objects[n] for n in ['Office key box cabinet','Key box glass','Key box label']]
    contact_fixture('Office key cabinet','Office rear wall east',[(-3,9.52,1.5)],(0,1,0),children)
    # Box rear formerly stopped 50mm shy of the wall. Extend its back only.
    o=S.objects['Office key box cabinet'];inv=o.matrix_world.inverted()
    for v in o.data.vertices:
        q=o.matrix_world@v.co
        if q.y>9.42:q.y=9.52;v.co=inv@q
    EXCEPTIONS[o.name]='Extend key cabinet backing to actual office wall, preserve visible front and original matrix'
    use_root('Ergonomic Swivel Chair')
    for i in range(5):
        o=S.objects['Chair wheel '+str(i)];x,y,z=o.matrix_world.translation
        replace(o.name,cyl('TEMP chair vertical caster',(x,y,.025),.025,.03,'rubber','Y',vertices=16,w=.001),'Vertical floor-bearing caster tire, inherited matrix retained')
        profile('CD | Chair caster yoke',[(-.021,-.025),(.021,-.025),(.021,.016),(.013,.026),(-.013,.026),(-.021,.016)],.027,1,(x,y,.052),'charcoal',.001)
        cyl('CD | Chair caster axle',(x,y,.025),.004,.036,'steel','Y',vertices=8,w=.0005)
    replace('Chair seat cushion',tapered('TEMP upholstered seat',(-4.45,6.8,.49),(.46,.48,.08),2,'fabric',.88,.045,.004),'Tapered upholstered cushion with manufactured seam, original seat datum retained')
    for n,loc,dims in [('Chair back lumbar',(-4.68,6.8,.68),(.05,.42,.22)),('Chair back upper',(-4.66,6.8,.86),(.05,.4,.18))]:
        replace(n,tapered('TEMP chair upholstery',loc,dims,0,'fabric',.84,.035,.003),'Drafted fabric back cushion, retained spine and seat interfaces')
    line('CD | Chair seat welt',[(-4.647,6.611,.505),(-4.647,6.989,.505),(-4.61,7.025,.505),(-4.29,7.025,.505),(-4.253,6.989,.505),(-4.253,6.611,.505),(-4.29,6.575,.505),(-4.61,6.575,.505),(-4.647,6.611,.505)],.0014,'cotton')
    for side in [-1,1]:
        name='Chair armrest pad '+str(side);loc=S.objects[name].matrix_world.translation
        replace(name,profile('TEMP shaped arm grip',octagon(.24,.08,.018),.03,2,loc,'rubber',.002),'Molded arm grip with clipped outline, retained support uprights')
    # Preserve rear leaf, add real pressed skins and captive hinge construction.
    use_root('D2 Staff Rear Door')
    for z,h in [(.58,.42),(1.63,.70)]:panel('D2 pressed skin',-5.4,9.545,z,.80,h,'coral')
    for z in [.3,1.1,1.96]:cyl('CD | D2 hinge barrel',(-5.918,9.55,z),.021,.10,'steel',vertices=12,w=.001)

def trolley_detail():
    use_root('Covered Trolley H1')
    for o in list(S.objects):
        if o.name.startswith('Trolley wheel '):
            x,y,z=o.matrix_world.translation
            replace(o.name,cyl('TEMP trolley tire',(x,y,z),.08,.04,'rubber','X',vertices=24,w=.002),'Floor-bearing vertical tire replaces horizontal disc, original caster location retained')
            cyl('CD | Trolley wheel hub',(x,y,z),.033,.042,'steel','X',vertices=16,w=.001)
    # Cloth on the retained hidden silhouette. Author folds onto the original
    # source rather than replacing the concealed mass with a visible body.
    tarp=S.objects['Covered Trolley Draped Tarp'];inv=tarp.matrix_world.inverted()
    for v in tarp.data.vertices:
        q=tarp.matrix_world@v.co
        if q.z>.90:
            q.z+=.013*sin((q.y-12.1)*24+.9*sin(q.x*13))*.7+.009*sin(q.x*31+q.y*12)
            v.co=inv@q
    tarp.data.update();assign(tarp,'fabric');EXCEPTIONS[tarp.name]='Authored shallow tension folds on retained concealed load silhouette; footprint and privacy screen remain'
    for x in [-6.20,-5.50]:
        line('CD | Trolley tarp sewn side hem',[(x,12.19,.827),(x,12.48,.838),(x,13.0,.833),(x,13.5,.834),(x,14.15,.827)],.0018,'cotton')
    for i,y in enumerate([12.55,13.05,13.55,14.05]):
        box('CD | Ratchet buckle folded shell',(-5.47,y,.851),(.045,.065,.006),'steel',.001)
        cyl('CD | Ratchet captive pin',(-5.47,y,.85),.004,.046,'steel','X',vertices=8,w=.0004)
    for x in [-6.2,-5.5]:
        for y in [12.2,14.3]:
            profile('CD | Trolley welded support gusset',[(0,0),(.14,0),(0,-.15)],.018,0,(x,y,.748),'steel',.001)
    # Same floor footprint and bedding datum; actual welded ties carry the deck.
    for y in [12.2,14.3]:box('CD | Trolley top cross tie',(-5.85,y,.749),(.70,.035,.04),'steel',.001)
    use_root('Parked Hand Cart')
    for o in list(S.objects):
        if not o.name.startswith('Hand cart wheel '):continue
        x,y,z=o.matrix_world.translation
        replace(o.name,cyl('TEMP cart tire',(x,y,z),.075,.04,'rubber','X',vertices=20,w=.002),'Vertical floor-bearing handcart caster, retained position')
    replace('Cart perimeter bumper',profile('TEMP cart bumper',octagon(.79,2.14,.045),.04,2,(4.425,12.7,.22),'rubber',.001),'Clipped rubber deck bumper, same parked cart footprint')

def cabinetry_detail():
    use_root('Evidence Cabinet H2')
    for k,x in enumerate([-6.1,-5.575,-5.05]):
        for j,z in enumerate([.48,1.18]):
            replace(f'Locker door {k}_{j}',profile('TEMP vault door',octagon(.5,.66,.028),.02,1,(x,14.79,z),'blue',.002),'Clipped reinforced vault door, retained lock/hinge/plaque positions')
            panel('Vault raised pressing',x,14.773,z,.405,.55,'blue')
            for xx in [x-.178,x+.178]:
                for zz in [z-.245,z+.245]:bolt('CD | Vault captive pressing screw',(xx,14.7605,zz),r=.004)
            cyl('CD | Vault lock escutcheon',(x+.14,14.755,z),.042,.006,'steel','Y',vertices=16,w=.001)
    box('CD | Evidence folded crown edge',(-5.575,14.787,1.619),(1.72,.01,.037),'steel',.001)
    # Purposeful sealed custody docket on cabinet, no scattered gore.
    box('CD | Custody docket taped sheet',(-4.94,14.758,1.27),(.13,.001,.20),'paper',0)
    for x in [-4.985,-4.895]:box('CD | Custody tape',(x,14.757,1.36),(.023,.001,.05),'yellow',0)
    txt('CD | Custody disposition','DO NOT RELEASE',(-4.94,14.7558,1.29),.014,'ink',align='CENTER')
    txt('CD | Custody file','731 / PENDING',(-4.94,14.7558,1.26),.010,'ink',align='CENTER')
    use_root('Wall Utilities Rack')
    for n in ['Transformer box 1','Transformer box 2','Main breaker disconnect']:
        o=S.objects[n];x,y,z=o.matrix_world.translation;dims=tuple(o.dimensions)
        replace(n,tapered('TEMP electrical enclosure',(x,y,z),dims,0,'blue',.91,.025),'Folded electrical enclosure with drafted cover, native wall assembly retained')
        for yy in [y-dims[1]*.36,y+dims[1]*.36]:
            for zz in [z-dims[2]*.38,z+dims[2]*.38]:cyl('CD | Disconnect cover captive screw',(x-dims[0]/2-.002,yy,zz),.005,.004,'steel','X',vertices=6,w=.0005)
    use_root('Switchgear Console Unit')
    for i,x in enumerate([4.45,5.45]):
        replace('Switchgear door '+str(i),profile('TEMP switchgear door',octagon(.84,1.9,.032),.02,1,(x,14.69,1.15),'blue',.002),'Folded recessed switchgear door, unchanged native cabinet footprint')
        # Actual open louver vanes replace the featureless slab.
        verts=[];faces=[]
        for j in range(9):
            z=1.73+j*.03;first=len(verts)
            verts.extend((xx,yy,zz) for zz in [z-.003,z+.003] for yy in [14.658,14.678] for xx in [x-.325,x+.325])
            faces.extend(tuple(first+k for k in f) for f in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)])
        replace('Louver bank '+str(i),mesh('TEMP switchgear louvers',verts,faces,'charcoal',.0007),'Nine separated ventilation vanes; retained cabinet object and native pose')
        box('CD | Switchgear folded pull',(x+.32,14.657,1.18),(.026,.042,.14),'steel',.003)
        cyl('CD | Switchgear barrel lock',(x+.32,14.654,1.02),.012,.006,'brass','Y',vertices=12,w=.0007)

def architectural_detail():
    global ASM
    ASM=None
    # Real rolled I sections within each inherited chord envelope.
    for o in list(S.objects):
        if o.name.startswith(('Truss top chord','Truss bot chord')):
            y=o.matrix_world.translation.y;z=o.matrix_world.translation.z
            pts=[(-.06,-.05),(.06,-.05),(.06,-.038),(.006,-.038),(.006,.038),(.06,.038),(.06,.05),(-.06,.05),(-.06,.038),(-.006,.038),(-.006,-.038),(-.06,-.038)]
            replace(o.name,profile('TEMP rolled roof chord',pts,13.6,0,(0,y,z),'navy',.001),'Rolled I-profile roof chord inside original architecture bounds, retained placement')
    # Inherited fixtures become registered suspended assemblies with genuine
    # two-point rods between housing top and roof underside.
    fixtures=[o for o in S.objects if o.name.endswith('Fixture Housing')]
    for housing in fixtures:
        prefix=housing.name.removesuffix(' Fixture Housing');x,y,z=housing.matrix_world.translation
        children=[housing]+[o for o in S.objects if o.name.startswith(prefix+' Tube ')]
        contact_fixture(prefix+' suspended fixture','Roof deck ceiling slab',[(x,y-.46,4.4),(x,y+.46,4.4)],(0,0,1),children)
        for yy in [y-.46,y+.46]:
            cyl('CD | Fixture suspension rod',(x,yy,(4.4+z+.04)/2),.006,4.4-z-.04,'steel',vertices=8,w=.0005)
            box('CD | Fixture roof plate',(x,yy,4.394),(.055,.055,.012),'steel',.001)
            box('CD | Fixture lamp end cap',(x,yy,z),(.34,.045,.086),'charcoal',.002)
        # Profile forms the folded shade, not another generic top slab.
        pts=[(-.16,-.04),(-.147,-.04),(-.13,.027),(.13,.027),(.147,-.04),(.16,-.04),(.145,.04),(-.145,.04)]
        replace(housing.name,profile('TEMP folded lamp shade',pts,1.25,1,(x,y,z),'ivory',.001),'Folded fluorescent reflector and explicit roof hangers; same fixture envelope')
    # Broad duct flanges and actual ceiling support; sparse specific rhythm.
    for n in ['Main ventilation supply trunk','Return ventilation trunk']:
        o=S.objects[n];x,y,z=o.matrix_world.translation;w,d,h=o.dimensions
        contact_fixture(n+' suspension','Roof deck ceiling slab',[(x-w*.43,1,4.4),(x+w*.43,14.8,4.4)],(0,0,1),[o])
        for yy in [1,4,7,10,14.8]:
            for xx in [x-w*.43,x+w*.43]:cyl('CD | Duct hanger',(xx,yy,(z+h/2+4.4)/2),.005,4.4-z-h/2,'steel',vertices=8,w=.0003)
            box('CD | Duct strap top',(x,yy,z+h/2+.007),(w,.045,.014),'steel',.001)
    ASM=None

def full_lighting():
    # Existing authored practical locations are immutable; energy is purpose-led.
    powers={'Warm Fluorescent SW':28,'Warm Fluorescent S-Mid':45,'Warm Fluorescent SE':22,
        'Office Task Fluorescent':55,'Office Rear Fluorescent':20,'Scanner Overhead Key':115,
        'Conveyor Hero Key':70,'Arrival Bay Key':58,'Bay Utility Key':60,
        'Support Concealed Accent':45,'Ambient Fill Center':15,'Ceiling Wash 4.0':12,
        'Ceiling Wash 11.0':10,'P2 Gate Amber Spotlight':12,'Lead Tunnel Hazard Spotlight':5,
        'G1 Gate Amber Downlight':5}
    for o in S.objects:
        if o.type!='LIGHT' or o.name.startswith('CD |'):continue
        o.data.energy=powers.get(o.name,10)
        if o.data.type=='AREA':o.data.color=(.64,.76,1) if o.name in ['Scanner Overhead Key','Conveyor Hero Key','Arrival Bay Key','Bay Utility Key'] else (1,.76,.52)
    S['light_contract']='Inherited practical poses; localized warm clerk pool, cool inspection keys, dim storage; no runtime light-budget claim'

def full_work():
    full_palette();scanner_detail();cargo_detail();office_detail();trolley_detail();cabinetry_detail();architectural_detail()
    exec(compile((ROOT/'full_repairs.py').read_text(),str(ROOT/'full_repairs.py'),'exec'),globals())
    repair_full_candidate()
    S['full_construction_recipe']='full_detail.py; root sole author; original named objects and pose interfaces retained'

def consolidate_new_details():
    # Consolidate only new cosmetic meshes after applying their authored shape
    # modifiers and UVs. Original interaction parts and support targets survive.
    targets={S.objects[n].get('support_target') for n in CONTACTS}
    groups={}
    for o in list(S.objects):
        if o.type!='MESH' or o.name in ORIGINAL or o.name in targets:continue
        key=(o.parent.name if o.parent else None,tuple(m.name for m in o.data.materials if m))
        groups.setdefault(key,[]).append(o)
    for (parent,mats),parts in groups.items():
        if len(parts)<2:continue
        names=[o.name for o in parts]
        for selected in list(bpy.context.selected_objects):selected.select_set(False)
        for o in parts:
            bpy.context.view_layer.objects.active=o
            for mod in list(o.modifiers):
                if mod.type=='WEIGHTED_NORMAL':bpy.ops.object.modifier_apply(modifier=mod.name)
            o.select_set(True)
        active=parts[0];bpy.context.view_layer.objects.active=active;bpy.ops.object.join()
        active.name='CD | Joined '+(parent or 'architecture')+' / '+mats[0].removeprefix('CD | ')
        active['component_names']=json.dumps(names);active['consolidation_contract']='Only new cosmetic geometry; original parts/support targets retained; disconnected closed components intentionally editable'
        # One authored family per group; remove duplicate material slots.
        if len(mats)==1:
            material=active.data.materials[0];active.data.materials.clear();active.data.materials.append(material)
            for f in active.data.polygons:f.material_index=0
        active.select_set(False)
