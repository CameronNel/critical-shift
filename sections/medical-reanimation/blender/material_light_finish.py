"""M05 shaped practical light, material-family separation and manufactured silhouettes."""
# Eliminate the remaining measured plaque/part interference.
SC.objects['Recovery identity bed bracket'].location.y=-1.139
for n in ['Engraved backing WASH / BEFORE LOAD','Engraved WASH / BEFORE LOAD','Wash instruction backing support']:
    SC.objects[n].location.x+=.11;SC.objects[n].location.z-=.28
# Short identity remains the same text height as other station signs.
SC.objects['Engraved RESTART STATION'].data.body='RESTART'
SC.objects['Engraved RESTART STATION'].location.x=-.42
SC.objects['Engraved backing RESTART STATION'].scale.x=.98/1.60
for o in SC.objects:
    if o.name.startswith('Restart sign support'):o.location.x=.39 if o.location.x>0 else -.39
# Specific broad material families. Fine tactile response is deliberately subpixel at room range.
recolor('wall','8A8983');recolor('floor','74736D');recolor('pale','ACADA7');recolor('bus','505350')
for key,rough,metallic in [('wall',1,0),('floor',.96,0),('pale',.76,.12),('darkpaint',.78,.25),('bus',.65,.55),('metal',.37,.90),('rubber',.98,0),('linen',.99,0),('blanket',.99,0)]:
    m=M[key];bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metallic
    for n in m.node_tree.nodes:
        if n.type=='MAP_RANGE':n.inputs['To Min'].default_value=max(.1,rough-.018);n.inputs['To Max'].default_value=min(1,rough+.018)
    if key in ['wall','floor']:bs.inputs['Specular IOR Level'].default_value=.12
    if key in ['pale','darkpaint']:bs.inputs['Specular IOR Level'].default_value=.25
    if key in ['linen','blanket']:
        nt=m.node_tree;tc=nt.nodes.new('ShaderNodeTexCoord');wv=nt.nodes.new('ShaderNodeTexWave');wv.wave_type='BANDS';wv.bands_direction='X';wv.inputs['Scale'].default_value=360;wv.inputs['Distortion'].default_value=.3
        bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.28;bump.inputs['Distance'].default_value=.0006;nt.links.new(tc.outputs['Object'],wv.inputs['Vector']);nt.links.new(wv.outputs['Color'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
# Clear lighting hierarchy: subdued middle circulation, usable task pools, warm secondary zones.
for o in SC.objects:
    if o.type!='LIGHT':continue
    if o.name.startswith('Ceiling practical output'):
        o.data.energy*=.58 if 3<o.location.y<6 else .72
        o.data.shape='RECTANGLE';o.data.size=1.0;o.data.size_y=.22;o.data.spread=math.radians(100)
    elif o.name.startswith('Wall grazed'):
        o.data.energy=90;o.data.shape='RECTANGLE';o.data.size=.55;o.data.size_y=.10;o.data.spread=math.radians(100)
    elif o.name.startswith('OCRU neutral'):o.data.energy=145;o.data.size=1.25
    elif o.name=='Decon task light':o.data.energy=40;o.data.size=.30;o.location=(1.8,10.15,2.36);o.rotation_euler=(Vector((2.65,10.8,1.25))-o.location).to_track_quat('-Z','Y').to_euler();o.data.color=(1,.89,.74)
current='Lighting';r=assembly('Recovery reading practical',(3.93,4.72,2.35),-math.pi/2)
box('Recovery light wall base',(0,.035,0),(.43,.07,.12),'darkpaint',r,.003)
box('Recovery shielded light',(0,-.03,-.005),(.49,.12,.07),'metal',r,.003)
box('Recovery opal diffuser',(0,-.06,-.047),(.39,.075,.012),'task',r,.001)
area_light('Recovery local pool',(3.73,4.72,2.25),(3.18,4.7,.73),38,.5,(1,.86,.69))
# Replace the large generic cast control boxes with shallow chamfered manufactured profiles.
def chamfered_panel(name,parent,loc,w,h,depth,c,mat):
    points=[(-w/2+c,-h/2),(w/2-c,-h/2),(w/2,-h/2+c),(w/2,h/2-c),(w/2-c,h/2),(-w/2+c,h/2),(-w/2,h/2-c),(-w/2,-h/2+c)]
    vv=[(x,yy,z) for yy in [-depth/2,depth/2] for x,z in points];faces=[tuple(range(7,-1,-1)),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
    me=bpy.data.meshes.new(name);me.from_pydata(vv,[],faces);me.update();o=bpy.data.objects.new(name,me);COL[current].objects.link(o);o.location=loc;o.parent=parent;me.materials.append(M[mat]);mod=o.modifiers.new('Folded edge radius','BEVEL');mod.width=.002;mod.segments=2;o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');return o
current='OCRU'
for name,root,loc,w,h,dep,c in [('Receiver cast housing','OCRU_CARTRIDGE_RECEIVER',(0,0,0),.35,.60,.14,.032),('Suit service enclosure','OCRU_SUIT_SERVICE',(0,.015,0),.34,.50,.09,.03)]:
    bpy.data.objects.remove(SC.objects[name],do_unlink=True);chamfered_panel(name,SC.objects[root],loc,w,h,dep,c,'bus')
p=SC.objects['OCRU_CARTRIDGE_RECEIVER'];box('Receiver recessed face',(0,-.073,0),(.28,.013,.47),'darkpaint',p,.002)
plaque(p,'C01',(0,-.247,.08),.09,.045,size=.023)
p=SC.objects['OCRU_SUIT_SERVICE']
for j in range(8):
    ang=j*math.tau/8;cyl('Suit collar lock lug',(.066*math.cos(ang),-.08,.11+.066*math.sin(ang)),.010,.021,'metal',p,'Y',8)
p=SC.objects['OCRU']
for x in [-1.98,1.98]:
    for z in [.70,1.97]:
        box('Service jamb narrow edge scuff',(x,-1.260,z),(.055,.003,.006),'edge',p,0)
# Cloth silhouette: a folded blanket has a soft uneven textile surface and a doubled hem.
current='Stations';p=SC.objects['RECOVERY_BERTH'];bpy.data.objects.remove(SC.objects['Folded recovery blanket'],do_unlink=True)
vv=[];faces=[];nx,ny=32,16
for j in range(ny+1):
    y=-.92+j*.5/ny
    for i in range(nx+1):
        x=-.49+i*.98/nx;z=.797+.006*math.sin(i*.8+j*.16)+.004*math.cos(j*.95)
        vv.append((x,y,z))
for j in range(ny):
    for i in range(nx):a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
me=bpy.data.meshes.new('Folded blanket textile');me.from_pydata(vv,[],faces);me.update();o=bpy.data.objects.new('Folded recovery blanket',me);COL[current].objects.link(o);o.parent=p;me.materials.append(M['blanket']);mod=o.modifiers.new('Folded textile thickness','SOLIDIFY');mod.thickness=.025
for o in SC.objects:
    if o.name.startswith('Blanket stitched fold'):o.location.z=.802
box('Blanket institutional tag',(.38,-.91,.81),(.12,.052,.002),'paper',p,.001)
text('Recovery blanket ID','PROPERTY / 01',(.33,-.92,.812),.013,'ink',p,rot=(0,0,0))
# Recovery use evidence: gloves and a folded release slip on the empty foot-end corner.
box('Recovery release slip',(-.32,-1.0,.791),(.18,.12,.003),'paper',p,.001)
text('Release slip','FIT FOR SHIFT',(-.40,-1.03,.794),.014,'ink',p,rot=(0,0,0))
current='Props';p=SC.objects['SUPPLY_BENCH']
for side in [-1,1]:
    box('Folded work glove palm',(-.1+side*.07,.17,.973),(.11,.12,.025),'cloth',p,.012)
    for i in range(4):box('Folded work glove finger',(-.15+side*.07+i*.028,.25,.97),(.025,.075,.020),'cloth',p,.007)
current='Architecture'
for i,(x,y) in enumerate([(-3.38,.65),(-2.85,1.9),(-.43,.68),(.30,1.1),(-3.3,1.8),(-.35,2.2)]):
    o=box('Localized cart contact mark',(x,y,.0014),(.016,.12+i*.006,.0007),'scuff',bevel=0);o.rotation_euler.z=.2*(i%3-1)
# Worktop dressing contact is measured against the actual Z=.945 working surface.
current='Props';p=SC.objects['SUPPLY_BENCH']
for o in list(SC.objects):
    if o.name.startswith('Sterile pack'):bpy.data.objects.remove(o,do_unlink=True)
for z in [.960,.992]:
    box('Sterile pack',(-.24,-.295,z),(.21,.25,.03),'paper',p,.004)
    box('Sterile pack seal',(-.24,-.295,z+.016),(.035,.24,.003),'orange',p,.001)
for o in SC.objects:
    if o.name.startswith('Folded work glove palm'):o.location.z=.9575
    if o.name.startswith('Folded work glove finger'):o.location.z=.955
    if o.name in ['Inventory clipboard','Inventory paper','Clipboard title'] or o.name.startswith('Inventory ruled line'):o.location.z-=.0075
    if o.name.startswith('Seal tool'):o.location.z=.973
o=SC.objects['Service tool tray'];o.scale.z=.01/.045;o.location.z=.950
for x in [.63,.97]:box('Tool tray folded rim',(x,-.04,.97),(.01,.43,.04),'darkpaint',p,.002)
for y in [-.25,.17]:box('Tool tray folded rim',(.8,y,.97),(.35,.01,.04),'darkpaint',p,.002)
# Final measured glyph clearance and paper support corrections.
SC.objects['Recovery release slip'].location.z=.7715
SC.objects['Release slip'].location.z=.774
for n in ['Engraved C01','Engraved backing C01']:SC.objects[n].location.y-=.022
for n in ['Engraved backing WASH / BEFORE LOAD','Engraved WASH / BEFORE LOAD']:SC.objects[n].location.y-=.038
o=SC.objects['Wash instruction backing support'];o.scale.y=.13/.065;o.location.y=1.062
# Targeted M06 concept: exposed manufactured edge at repeatedly handled interfaces.
for o in list(SC.objects):
    if o.type!='MESH':continue
    if any(o.name.startswith(n) for n in ['Adult tray pressed pan','Chamber sill','Receiver cast housing','Suit service enclosure','Reserve removable door','Cart deck','Tray folded end flange','Console working surface','Service tool tray']):
        o.data.materials.append(M['edge'])
        for mod in o.modifiers:
            if mod.type=='BEVEL':mod.material=len(o.data.materials)-1
current='OCRU';p=SC.objects['OCRU'];tray=SC.objects['OCRU_BERTH']
for x in [-.75,.75]:
    for xx in [x-.20,x+.20]:
        for y in [-.23,.23]:cyl('Berth base anchor',(xx,y,.515),.015,.018,'metal',tray,vertices=8)
for x in [-1.95,1.95]:
    for z in [.49,2.45]:
        box('Jamb threshold edge chip',(x,-1.2853,z),(.026,.001,.005),'edge',p,0)
current='Lighting'
for yy in [4.63-.72,4.63+.72]:
    box('Berth service inspection lamp',(-2.37,yy,.87),(.18,.10,.055),'darkpaint',bevel=.003)
    box('Berth service diffuser',(-2.37,yy,.835),(.14,.07,.015),'task',bevel=.001)
    area_light('Berth inspection pool',(-2.37,yy,.81),(-2.30,yy,.41),5,.18,(1,.95,.88))
current='Utilities'
bpy.data.objects.remove(SC.objects['Panel incoming conduit'],do_unlink=True)
tube('Panel incoming conduit',[(3.45,8.975,1.69),(3.45,8.975,2.68),(-2.15,8.975,2.68),(-2.15,9.18,2.65)],.021,'metal')
for x in [-1.4,.7,2.8]:box('Isolation feed wall clip',(x,8.975,2.68),(.07,.05,.07),'darkpaint',bevel=.002)
# Console conduit enters the actual rear housing instead of stopping in free space.
bpy.data.objects.remove(SC.objects['Console telemetry feed'],do_unlink=True)
tube('Console telemetry feed',[(-.4,9.175,2.65),(-.4,8.96,2.65),(-.4,8.96,1.50),(-.4,8.87,1.50)],.018,'metal')
# Visible sink supply and contained plumbing inside owned wall/floor service volume.
p=SC.objects['HANDWASH']
tube('Handwash supply tail',[(.12,.28,.60),(.12,.13,.60),(.12,.13,.925)],.012,'metal',p)
cyl('Sink service valve',(.12,.22,.60),.026,.085,'metal',p,'Y',12)
ring('Sink isolator handwheel',(.12,.17,.60),.036,.006,'orange',p,'Y')
tube('Concealed wash supply',[(3.36,10.70,.60),(3.05,10.70,.60),(3.05,10.70,-.12),(3.05,8.90,-.12),(4.0,8.90,-.12),(4.0,3.07,-.12),(4.0,3.07,.60)],.013,'metal')
tube('Concealed handwash drain',[(4.0,2.95,.15),(4.0,2.95,-.16),(4.0,8.95,-.16),(2.33,8.95,-.16),(2.33,11.12,-.16),(2.33,11.12,.15),(2.33,11.30,.15)],.025,'metal')
# Real extract penetration framed by wall panels, with an opaque capped service sleeve outside.
current='Architecture';bpy.data.objects.remove(SC.objects['Decon rear wall'],do_unlink=True)
for x in [1.715,2.945]:box('Decon rear wall pier',(x,11.21,1.275),(.83,.18,2.55),'wall')
box('Decon rear wall below extract',(2.33,11.21,1.05),(.40,.18,2.10),'wall')
box('Decon rear wall above extract',(2.33,11.21,2.475),(.40,.18,.15),'wall')
# Captive scissor tracks tie the cart's lower pivots to its frame and upper pivots to its lift deck.
current='Stations';p=SC.objects['BODY_CART'];deck=SC.objects['CART_LIFT_DECK']
for y in [-.64,.64]:box('Cart lift load crossmember',(0,y,.273),(.65,.075,.06),'darkpaint',p,.004)
for x in [-.20,.20]:
    box('Lower captive scissor track',(x,0,.312),(.085,1.72,.035),'metal',p,.003)
    box('Upper captive scissor track',(x,0,.795),(.085,1.72,.035),'metal',deck,.003)
    for y in [-.64,.63]:cyl('Scissor lower slider',(x,y,.315),.027,.07,'bus',p,'X',24)
# M10: put the decon instruction at the threshold, away from the wand's oblique sightline.
for n in ['Engraved backing WASH / BEFORE LOAD','Engraved WASH / BEFORE LOAD','Wash instruction backing support']:
    bpy.data.objects.remove(SC.objects[n],do_unlink=True)
current='Architecture';p=SC.objects['Decon identity']
o=SC.objects['Engraved backing DECON'];o.scale.z=.34/.24
box('Decon identity wall standoff',(0,.055,0),(1.20,.11,.30),'darkpaint',p,.002)
text('Decon threshold instruction','BEFORE LOADING',(-.58,-.006,-.115),.045,'paper',p)
SC.objects['Decon threshold instruction']['backing_object']='Engraved backing DECON'
