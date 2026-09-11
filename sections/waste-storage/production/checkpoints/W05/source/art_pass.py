"""W04 focused material/lighting and object-specific silhouette correction."""
# Strong broad response, microscopic detail deliberately absent.
for key,variation,rough in [('wall',.16,.93),('pale',.10,.72),('paint',.12,.70),('bus',.08,.60),('metal',.07,.48),('darkpaint',.07,.75)]:
    m=M[key];base=m.diffuse_color[:3]
    for n in m.node_tree.nodes:
        if n.type=='VALTORGB':
            n.color_ramp.elements[0].color=(*(v*(1-variation) for v in base),1)
            n.color_ramp.elements[1].color=(*(min(1,v*(1+variation)) for v in base),1)
        if n.type=='BSDF_PRINCIPLED':n.inputs['Roughness'].default_value=rough
        if n.type=='MAP_RANGE':n.inputs['To Min'].default_value=rough-.09;n.inputs['To Max'].default_value=min(.98,rough+.08)
# Quiet darker ceiling differentiates concrete soffit from walls.
M['ceiling']=material('Ceiling dust grey','777267',.94,0,.10,0)
bpy.data.objects['Ceiling'].data.materials.clear();bpy.data.objects['Ceiling'].data.materials.append(M['ceiling'])
# Remove the failed rectangular 'scuff' confetti; replace with broad irregular
# low-contrast abrasion at a few genuine cart turn/service locations.
for o in list(bpy.data.objects):
    if o.name.startswith('Localized wheel scuff'):bpy.data.objects.remove(o,do_unlink=True)
M['floorabrasion']=material('Dry floor abrasion','605C53',.94,0,.08,0)
current='Architecture'
for j,(x,y,rx,ry) in enumerate([(-1,3,.45,.85),(1.1,4.3,.36,.9),(-.9,8.1,.3,.8),(.9,12.5,.3,.8),(-.2,16,.8,.45)]):
    rng=random.Random(800+j);vv=[]
    for k in range(19):
        a=k*math.tau/19;rr=rng.uniform(.68,1);vv.append((x+math.cos(a)*rx*rr,y+math.sin(a)*ry*rr,.0015))
    me=bpy.data.meshes.new('Traffic polish island');me.from_pydata(vv,[],[tuple(range(len(vv)))]);me.update();ob=bpy.data.objects.new('Selective floor wear patch',me);COL[current].objects.link(ob);me.materials.append(M['floorabrasion'])
# Reduced gate cassette bulk exposes equipment silhouettes from the entrance.
for o in bpy.data.objects:
    if o.name.startswith('Cell gate pocket'):o.scale.z=.58;o.location.z=.609
    if o.name.startswith('Nested retracting gate edge'):o.scale.z=.58
# Original angular wall wash fixtures, actual light source and backing support.
current='Lighting'
for side in [-1,1]:
    for y in [5.6,10.7,16.0]:
        p=assembly('Cell task wall fixture',(side*5.98,y,3.5),-math.pi/2 if side>0 else math.pi/2,support='East Wall.001' if side>0 else 'West Wall',anchors=[[0,.02,0]],direction=[0,1,0])
        box('Wall fixture backplate',(0,0,0),(.25,.04,.30),'darkpaint',p,.01)
        box('Angled fixture housing',(0,-.075,.04),(.34,.16,.15),'bus',p,.018)
        box('Wall wash diffuser',(0,-.16,-.005),(.27,.025,.075),'lamp',p,.006)
        d=bpy.data.lights.new('Directed practical wash','SPOT');d.energy=550;d.color=(1,.90,.76);d.spot_size=math.radians(83);d.spot_blend=.65;d.shadow_soft_size=.14
        ob=bpy.data.objects.new('Directed practical wash',d);COL[current].objects.link(ob);ob.location=(side*5.72,y,3.4);ob.rotation_euler=(Vector((side*4.5,y,1.3))-ob.location).to_track_quat('-Z','Y').to_euler()
# Extraction fan: actual eccentric scroll profile instead of a simple cylinder.
p=bpy.data.objects['VF01_EXTRACTION'];current='Ventilation'
for ob in list(p.children):
    if ob.name.startswith('Centrifugal fan casing'):bpy.data.objects.remove(ob,do_unlink=True)
verts=[];N=40
for x in [.64,1.0]:
    for k in range(N):
        a=k*math.tau/N;r=.34+.13*k/(N-1);verts.append((x,.03+math.cos(a)*r,1.40+math.sin(a)*r))
faces=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N) for k in range(N)]
me=bpy.data.meshes.new('Fan scroll shell');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Centrifugal volute',me);COL[current].objects.link(o);o.parent=p;me.materials.append(M['paint']);mod=o.modifiers.new('Rolled scroll edge','BEVEL');mod.width=.006;mod.segments=2
for x in [.635,1.005]:
    ring('Fan casing bolted seam',(x,.03,1.4),.33,.025,'metal',p,'X')
    for k in range(10):
        a=k*math.tau/10;cyl('Fan seam bolt',(x,.03+.33*math.cos(a),1.4+.33*math.sin(a)),.014,.045,'darkpaint',p,'X',6)
for x in [-.78,.02]:
    for z in [.65,1.75]:
        box('Filter latch handle',(x+.25,-.55,z),(.03,.05,.18),'paint',p,.006)
        cyl('Filter clamp pivot',(x+.25,-.56,z+.05),.021,.07,'metal',p,'X')
    contact_scars(p,x+.18,-.531,1.23,.18,.07,seed=22)
box('Motor terminal box',(1.21,.03,1.64),(.19,.18,.13),'bus',p,.013)
box('Isolator enclosure',(.93,-.40,.65),(.32,.18,.37),'pale',p,.015)
rotary(p,.93,-.51,.67,'red')
plaque(p,'ISOLATE',(.93,-.50,.47),.30,.08,size=.035)
tube('Motor armored lead',[(1.21,.01,1.68),(1.20,-.18,1.62),(1.04,-.3,1.02),(.96,-.33,.83)],.025,'rubber',p)
box('Damper shaft bearing',(.83,-.17,2.37),(.13,.10,.13),'metal',p,.005)
cyl('Damper crank axle',(.83,-.25,2.37),.025,.18,'metal',p,'Y')
beam('Damper crank lever',(.83,-.35,2.37),(1.03,-.35,2.37),.034,'yellow',p)
# Container cast ends, restraint hardware and recessed panel identity.
current='Containers'
for p in [o for o in bpy.data.objects if o.get('equipment_type')=='dry_container']:
    for x in [-.72,.72]:
        # Four authentic recessed pull mounting pads.
        for z in [.55,.80]:box('Pull mounting pad',(x,-.51,z),(.10,.035,.09),'metal',p,.005)
        handle(p,x,-.555,.675,height=.25)
    for z in [.35,.93]:box('Rolled container reinforcing band',(0,-.503,z),(1.88,.025,.035),'bus',p,.003)
    for x in [-.50,.50]:contact_scars(p,x,-.504,.35,.22,.04,seed=99)
# Maintenance work evidence grounded on the actual benchtop.
p=bpy.data.objects['WB01_SEAL_REPAIR'];current='Workshop'
box('Fastener tray',(.45,.10,.98),(.37,.26,.03),'darkpaint',p,.008)
for x in [.31,.42,.53]:
    for y in [.035,.14]:cyl('Spare captive fastener',(x,y,1.01),.023,.035,'metal',p,vertices=6)
box('Service cloth',(-.16,-.22,.965),(.25,.25,.025),'cloth',p,.014)
for x in [-.78,.78]:
    for z in [1.1,1.6]:cyl('Backboard fastener',(x,.279,z),.012,.014,'metal',p,'Y',8)
