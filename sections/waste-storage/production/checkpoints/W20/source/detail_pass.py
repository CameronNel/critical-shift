"""W03: construction, utility topology, human-use clusters and tactile surfaces."""
M['floor']=material('Dry graphite traffic floor','59564E',.94,0,.18,0)
bpy.data.objects['Floor'].data.materials.clear();bpy.data.objects['Floor'].data.materials.append(M['floor'])
for mat in [M['wall'],M['pale'],M['paint'],M['bus']]:
    for n in mat.node_tree.nodes:
        if n.type=='TEX_NOISE' and n.inputs['Scale'].default_value<10:n.inputs['Scale'].default_value=4.0;n.inputs['Detail'].default_value=.5
for d in bpy.data.lights:d.color=(1,.93,.84)
current='Architecture'
# Concrete panel joints and genuine construction footing, quiet repeated bays.
for side in [-1,1]:
    x=side*5.996
    for y in [4.45,9.05,13.75,17.65]:
        box('Panel vertical seal',(x,y,2.4),(.009,.018,4.8),'joint',bevel=0)
    for z in [1.10,3.15]:box('Horizontal concrete joint',(x,10.9,z),(.009,14.1,.018),'joint',bevel=0)
    for y in [6.6,11.2,16.1]:
        for z in [1.55,2.75]:
            for yy in [y-1.0,y+1.0]:cyl('Precast tie plug',(x,yy,z),.031,.006,'patch',axis='X',vertices=16)
    for y,ln in [(6.8,3.65),(11.4,3.65),(16,3.3)]:box('Wall bumper plate',(side*5.95,y,.35),(.09,ln,.40),'bus',bevel=.006)
for ob in list(bpy.data.objects):
    if ob.name.startswith('Cell transverse concrete separator'):
        box('Cell impact coping',(ob.location.x,ob.location.y,1.12),(3.85,.23,.04),'bus',bevel=.006)
    if ob.name.startswith('Cell label'):
        for x in [-.60,.60]:box('Sign post extension',(x,0,-.25),(.035,.035,.35),'metal',ob,.002)
    if ob.name.startswith('Cell gate pocket'):
        for y in [-.40,-.20,0,.20,.40]:box('Nested retracting gate edge',(0,y,0),(.15,.026,2.10),'metal',ob,.002)
# Beam plate joints make the framing read as steel, not intersected cuboids.
for side in [-1,1]:
    for y in [4.45,9.05,13.75,17.65]:
        p=assembly('Bolted roof node',(side*5.83,y,4.53))
        box('Beam end plate',(0,0,0),(.025,.43,.43),'metal',p,.004)
        for yy in [-.14,.14]:
            for z in [-.13,.13]:cyl('End plate bolt',(side*-.022,yy,z),.020,.043,'darkpaint',p,'X',6)
# Purposeful cart marks, graphical rather than full-surface noisy grunge.
current='Architecture'
random.seed(211)
for k in range(65):
    x=random.choice([-1.1,1.1])+random.uniform(-.22,.22);y=random.uniform(1,17)
    w=random.uniform(.02,.08);ln=random.uniform(.08,.40)
    v=[(x-w,y-ln,.002),(x+w*.7,y-ln*.7,.002),(x+w,y+ln,.002),(x-w*.6,y+ln*.8,.002)]
    me=bpy.data.meshes.new('Traffic abrasion');me.from_pydata(v,[],[(0,1,2,3)]);o=bpy.data.objects.new('Localized wheel scuff',me);COL[current].objects.link(o);me.materials.append(M['scuff'])
# Mechanical plate labels seat on ribs; don't let text be cut by rib geometry.
for p in [o for o in bpy.data.objects if o.get('equipment_type') in ['shielded_cask','residue_overpack']]:
    current='Casks';tall=p.get('equipment_type')=='shielded_cask';r=.57 if tall else .43
    height=2.3 if tall else 1.3
    for ob in list(p.children):
        if ob.name.startswith('Longitudinal protection rib') or ob.name.startswith('Overpack impact stay'):bpy.data.objects.remove(ob,do_unlink=True)
    for j in range(6):
        a=j*math.tau/6
        # Six tapered cast impact shoes, leaving broad shell and a clear front.
        profile=[(-.075,.40),(.075,.40),(.11,.60),(.075,.71),(.075,height-.55),(.115,height-.43),(.085,height-.31),(-.085,height-.31),(-.115,height-.43),(-.075,height-.55),(-.075,.71),(-.11,.60)]
        verts=[(xx,yy,z) for yy in [r*.84,r*1.015] for xx,z in profile];n=len(profile)
        faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(k,(k+1)%n,(k+1)%n+n,k+n) for k in range(n)]
        me=bpy.data.meshes.new('Cast protection shoe profile');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('Tapered cask impact shoe',me);COL[current].objects.link(ob);ob.parent=p;ob.rotation_euler[2]=a;me.materials.append(M['darkpaint'])
        mod=ob.modifiers.new('Cast edge relief','BEVEL');mod.width=.007;mod.segments=2
    for o in p.children:
        if o.name.startswith('Recessed engraved plate') or o.name.startswith('Engraved '):o.location.y-=.06
    for z in [.38,(2.3 if tall else 1.3)-.20]:
        for j in range(12):
            a=j*math.tau/12;q=assembly('Collar radial fastener',(r*math.cos(a),r*math.sin(a),z),a+math.pi/2,parent=p)
            cyl('Captive collar hex',(0,-.014,0),.019,.035,'darkpaint',q,'Y',6)
    for z in [.56,.87]:contact_scars(p,.14,-r*.905-.013,z,.20,.035,seed=int(z*100))
    # Capped sampling connector below front gauge, attached through shell.
    cyl('Sample boss',(0,-r*.91-.025,.94 if tall else .49),.065,.075,'metal',p,'Y')
    cyl('Sample cap',(0,-r*.91-.071,.94 if tall else .49),.048,.03,'yellow',p,'Y',8)
    for xx in [-r*.70,r*.70]:
        for yy in [-r*.83,r*.83]:cyl('Skid fastening bolt',(xx,yy,.268),.025,.045,'darkpaint',p,vertices=6)
    p['support_anchors']=json.dumps([[-r*.70,0,0],[r*.70,0,0]])
# Hollow hoist hook and visible alternating chain links.
p=bpy.data.objects['HJ01_HANDLING_JIB'];current='Casks'
for o in list(p.children):
    if o.name.startswith('Hoist chain') or o.name.startswith('Load hook'):bpy.data.objects.remove(o,do_unlink=True)
for x in [-.055,.055]:
    for k in range(12):ring('Load chain link',(x,-1.45,2.91-k*.039),.023,.006,'metal',p,'Y' if k%2 else 'X')
box('Hook swivel block',(0,-1.45,2.42),(.16,.12,.12),'darkpaint',p,.015)
pts=[(.04,-1.45,2.39),(.10,-1.45,2.29),(.055,-1.45,2.20),(-.065,-1.45,2.20),(-.095,-1.45,2.27),(-.06,-1.45,2.31)]
tube('Forged open hook',pts,.027,'metal',p)
beam('Hook safety latch',(-.06,-1.45,2.31),(.03,-1.45,2.37),.012,'yellow',p)
for k in range(34):ring('Hand chain',( .16,-1.45,2.91-k*.045),.024,.005,'metal',p,'Y' if k%2 else 'X')
for z in [.25,2.8,3.35]:
    for j in range(8):
        a=j*math.tau/8;cyl('Mast collar stud',(.155*math.cos(a),.155*math.sin(a),z+.06),.018,.04,'darkpaint',p,vertices=6)
# Cart jack gains a real guided lift linkage and removable transport saddle.
p=bpy.data.objects['CT01_TRANSFER_CART'];current='Cart'
for x in [-.26,.26]:
    beam('Scissor link A',(x,-.31,.58),(x,.31,.82),.045,'metal',p)
    beam('Scissor link B',(x,.31,.58),(x,-.31,.82),.045,'metal',p)
    cyl('Scissor pivot',(x,0,.70),.048,.075,'darkpaint',p,'X')
beam('Jack crank shaft',(0,0,.70),(0,-.57,.70),.025,'metal',p)
beam('Jack crank arm',(0,-.57,.70),(.16,-.57,.70),.023,'metal',p)
beam('Jack crank grip',(.16,-.57,.70),(.16,-.68,.70),.035,'rubber',p)
for x in [-.39,.39]:
    for y in [-.62,.62]:cyl('Cart deck fastener',(x,y,.548),.015,.01,'metal',p,vertices=6)
p['support_anchors']=json.dumps([[-.35,-.57,0],[.35,-.57,0],[-.35,.57,0],[.35,.57,0]])
# Empty container interior; lid must have hinges and corners with grounding.
for p in [o for o in bpy.data.objects if o.get('equipment_type')=='dry_container']:
    current='Containers'
    for x in [-.78,.78]:
        cyl('Container hinge pin',(x,.475,1.08),.033,.24,'metal',p,'X')
        box('Hinge attachment leaf',(x,.478,.99),(.21,.025,.13),'metal',p,.004)
    for x in [-1.02,1.02]:
        for z in [.27,.95]:cyl('End-casting bolt',(x,-.535,z),.018,.02,'darkpaint',p,'Y',6)
    p['support_anchors']=json.dumps([[-.75,0,0],[.75,0,0]])
# Inventory: analog instrument, arm lamp, chair, real hand-use artifacts.
p=bpy.data.objects['IM01_INVENTORY'];current='Monitoring'
box('Dose meter cast housing',(.50,.18,1.48),(.35,.20,.31),'bus',p,.021)
gauge(p,.50,.065,1.48,.115,'DOSE',-.55)
box('Dose meter foot',(.50,.20,1.21),(.15,.15,.50),'darkpaint',p,.008)
for j in range(4):
    box('Printed logbook rule',(.43,-.28+j*.045,1.032),(.22,.002,.001),'ink',p,0)
cyl('Pen barrel',(.55,-.20,1.045),.007,.19,'darkpaint',p,'Y',12)
box('Task lamp foot',(-.62,.25,1.0),(.20,.18,.045),'darkpaint',p,.012)
beam('Task lamp lower arm',(-.62,.25,1.02),(-.62,.27,1.53),.025,'metal',p)
beam('Task lamp upper arm',(-.62,.27,1.53),(-.39,.05,1.73),.025,'metal',p)
cyl('Lamp hinge',(-.62,.27,1.53),.044,.045,'darkpaint',p,'X')
box('Task lamp hood',(-.39,-.04,1.73),(.35,.21,.075),'darkpaint',p,.012)
box('Task diffuser',(-.39,-.04,1.686),(.30,.16,.01),'lamp',p,.003)
for x in [-.47,.025]:
    for z in [1.22,1.61]:cyl('Monitor face screw',(x,-.051,z),.009,.010,'metal',p,'Y',8)
for j in range(8):box('Monitor rear louvre',(-.22,.296,1.24+j*.036),(.36,.012,.012),'darkpaint',p,.002)
p['support_anchors']=json.dumps([[-.64,-.30,0],[.64,-.30,0],[-.64,.30,0],[.64,.30,0]])
chair=root('Inventory chair',(-3.05,1.60,0),math.pi/2)
for x in [-.22,.22]:
    for y in [-.21,.21]:beam('Chair leg',(x,y,0),(x*.87,y*.87,.47),.028,'metal',chair)
box('Upholstered seat',(0,0,.49),(.49,.49,.07),'cloth',chair,.035)
for x in [-.2,.2]:beam('Chair back rail',(x,.20,.40),(x,.24,.94),.025,'metal',chair)
box('Padded backrest',(0,.25,.85),(.45,.065,.27),'cloth',chair,.028)
chair['support_anchors']=json.dumps([[-.22,-.21,0],[.22,-.21,0],[-.22,.21,0],[.22,.21,0]])
# Continuous extract network, intake headers converge above machinery.
current='Ventilation'
box('Rear intake crossheader',(0,17.1,4.03),(10.9,.43,.45),'bus',bevel=.008)
box('Filter inlet drop',(-4.73,16.55,2.97),(.43,.43,1.80),'bus',bevel=.008)
box('Filter inlet upper offset',(-4.73,16.83,4.03),(.43,.60,.45),'bus',bevel=.008)
box('Skid exhaust riser',(-3.53,16.15,3.35),(.42,.48,1.40),'bus',bevel=.008)
box('Exhaust offset',(-4.165,16.15,4.0),(1.69,.48,.60),'bus',bevel=.008)
box('Exhaust outlet',(-4.8,17.235,4),(.65,2.17,.60),'bus',bevel=.008)
box('Exterior extract collar',(-4.8,18.31,4),(.75,.025,.70),'metal',bevel=.003)
# Explicit wall bores: only owned walls, never neighbors.
for name,loc,dims,targets in [('Extract wall bore',(-4.8,18.16,4),(.68,.7,.63),[o for o in SC.objects if o.name.startswith('Dispatch wall') and o.location.x<0]),('Power wall bore',(6.16,16.8,3.6),(.7,.22,.22),[o for o in SC.objects if o.name.startswith('East Wall') and o.location.y>3]),('Data wall bore',(-6.16,1.2,2.8),(.7,.14,.14),[bpy.data.objects['West Wall']])]:
    cut=box(name,loc,dims,'wall',bevel=0)
    for target in targets:
        mod=target.modifiers.new(name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=target;bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cut,do_unlink=True)
box('Power boundary sleeve',(6.16,16.8,3.6),(.32,.20,.20),'darkpaint',bevel=.003)
box('Data boundary sleeve',(-6.16,1.2,2.8),(.32,.12,.12),'darkpaint',bevel=.002)
# Own capped connection faces do not assert live airflow/electric supply.
contract=json.loads((ROOT/'interface.json').read_text())
current='Validation'
for item in contract['portals']+contract['utility_interfaces']:
    e=assembly('IF_'+item['id'],item['center']);e['connection_id']=item['id'];e['outward_normal']=json.dumps(item['outward_normal'])
for name,loc in [('AUDIO_WASTE_HALL',(0,9,2)),('INCIDENT_WASTE_BREACH',(-4.5,11,1)),('INTERACT_INVENTORY',(-3.5,1.6,1.3)),('INTERACT_VENT_ISOLATE',(-3.2,15.5,1.2)),('INSPECT_QUARANTINE',(3.4,11.6,1.1)),('NAV_RECEIVING',(0,2.5,0)),('NAV_DISPATCH',(0,16,0))]:
    e=assembly(name,loc);e['authority']='engine_host';e['implemented']='anchor_only'
