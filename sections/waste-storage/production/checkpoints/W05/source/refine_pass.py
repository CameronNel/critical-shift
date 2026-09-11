"""W05 structural readability and tactile construction pass."""
# Low cell barriers replace the stall-like overhead frame rhythm.
for object_name in list(bpy.data.objects.keys()):
    o=bpy.data.objects.get(object_name)
    if o is None: continue
    if o.name.startswith('Cell sliding gate header'):
        o.location.z=1.30
    if o.name.startswith('Cell boundary post'):
        o.dimensions.z=1.34;o.location.z=.67
    if o.name.startswith('Cell label'):
        for child in list(o.children):bpy.data.objects.remove(child,do_unlink=True)
        bpy.data.objects.remove(o,do_unlink=True)
current='Architecture'
for side in [-1,1]:
    for y,ident,label in [(4.8,'A' if side<0 else 'C','RESIDUE' if side<0 else 'DRY'),(9.4,'B' if side<0 else 'D','SHIELDED' if side<0 else 'HOLD')]:
        p=assembly('Cell boundary identity',(side*3.9,y-.085,.62))
        box('Cell identity plate',(0,0,0),(1.45,.014,.65),'paint',p,.003)
        text('Cell large ID',ident,(-.56,-.009,-.20),.48,'paper',p)
        text('Cell function',label,(-.10,-.009,.04),.09,'paper',p)
        text('Cell small descriptor','SEALED STORE',(-.10,-.009,-.12),.055,'paper',p)
        for x in [-.66,.66]:
            for z in [-.25,.25]:cyl('Identity plate rivet',(x,-.010,z),.011,.012,'metal',p,'Y',8)
# Supple low-amplitude normal response; clear material-specific roughness.
for key,scale,distance,strength in [('wall',85,.0012,.15),('floor',110,.0009,.13),('pale',170,.00035,.10),('paint',150,.00045,.10),('metal',100,.0002,.08)]:
    m=M[key];nt=m.node_tree;bs=nt.nodes.get('Principled BSDF')
    tc=nt.nodes.new('ShaderNodeTexCoord');n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;n.inputs['Detail'].default_value=1
    nt.links.new(tc.outputs['Generated'],n.inputs['Vector']);b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=strength;b.inputs['Distance'].default_value=distance
    nt.links.new(n.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],bs.inputs['Normal'])
# Broad concrete panel differences, stopping before door and control faces.
M['panelpatch']=material('Replacement cast concrete','A59D8C',.94,0,.16,.001)
for side in [-1,1]:
    for y in [7.0,11.7]:
        box('Repaired lower wall panel',(side*5.987,y,.67),(.018,2.0,.48),'panelpatch',bevel=.002)
# Utility conduits with bends, clamps, real device terminations and no route intrusion.
current='Monitoring'
for side in [-1,1]:
    for z in [3.38,3.48]:
        tube('Wall service conduit',[(side*5.89,3.6,z),(side*5.89,10,z),(side*5.89,17.5,z)],.016,'metal')
        for y in [4,7.5,11.5,15,17]:box('Conduit stand-off clamp',(side*5.92,y,z),(.12,.055,.08),'darkpaint',bevel=.003)
    for y in [6.3,11.2]:
        p=assembly('Cell monitoring head',(side*5.92,y,1.70),math.pi/2 if side<0 else -math.pi/2)
        box('Sensor housing',(0,0,0),(.24,.16,.32),'pale',p,.022)
        box('Sensor recess',(0,-.088,.04),(.14,.018,.13),'black',p,.006)
        cyl('Sensor sampling face',(0,-.103,.04),.05,.012,'metal',p,'Y',24)
        plaque(p,'MONITOR',(0,-.09,-.11),.20,.055,size=.022)
        tube('Sensor riser',[(side*5.85,y,1.86),(side*5.85,y,3.18),(side*5.89,y+.15,3.38)],.018,'metal')
# Compact sensor on the receiving side, separate from the main inventory table.
p=assembly('Receiving dosimeter',(-1.80,.04,1.5),math.pi)
box('Receiving sensor backing',(0,0,0),(.34,.08,.48),'bus',p,.012)
gauge(p,0,-.09,.05,.12,'DOSE',-.5)
plaque(p,'SCAN / LOG',(0,-.05,-.15),.30,.065,size=.035)
# Textile/hand-tool evidence at inventory, correctly placed rather than floor litter.
current='Monitoring';p=bpy.data.objects['IM01_INVENTORY']
box('Seal tag holder',(.66,-.25,1.03),(.13,.16,.10),'paint',p,.012)
for j in range(3):box('Loose serialized tag',(.66,-.25+j*.026,1.09+j*.002),(.11,.05,.003),'paper',p,.001)
text('Tag serial','104',(.625,-.248,1.099),.022,'ink',p,rot=(0,0,0))
box('Small tool tray',(-.60,-.13,1.015),(.19,.29,.045),'metal',p,.005)
beam('Seal pliers handle',(-.62,-.23,1.05),(-.59,-.07,1.05),.021,'paint',p)
beam('Seal pliers handle2',(-.54,-.23,1.05),(-.59,-.07,1.05),.021,'paint',p)
beam('Seal pliers jaw',(-.59,-.07,1.05),(-.62,.005,1.05),.021,'metal',p)
# Replace toy square push-bar with a formed tubular handle and real grips.
current='Cart';p=bpy.data.objects['CT01_TRANSFER_CART']
for ob in list(p.children):
    if ob.name.startswith('Handle upright') or ob.name.startswith('Push bar'):bpy.data.objects.remove(ob,do_unlink=True)
tube('Bent tubular push handle',[(-.37,-.64,.48),(-.37,-.84,.97),(-.32,-.86,1.05),(.32,-.86,1.05),(.37,-.84,.97),(.37,-.64,.48)],.023,'metal',p)
beam('Rubber push grip',(-.29,-.86,1.05),(.29,-.86,1.05),.052,'rubber',p)
# Exact support datums are physical feet, never arbitrary root origins.
for p in [o for o in bpy.data.objects if o.get('portal_id')]:
    width=3 if p.name=='WS_RECEIVING' else 2.4 if p.name=='WS_DISPATCH' else 1.2
    p['support_anchors']=json.dumps([[-width/2-.065,0,0],[width/2+.065,0,0]])
bpy.data.objects['VF01_EXTRACTION']['support_anchors']=json.dumps([[-1,0,0],[1,0,0]])
bpy.data.objects['WB01_SEAL_REPAIR']['support_anchors']=json.dumps([[-.72,-.29,0],[.72,-.29,0],[-.72,.29,0],[.72,.29,0]])
# Correct invalid occluded camera approaches before the final fixed baseline.
camera_repairs={'C06_Dry':((1.0,6.7,1.68),(4.25,7.55,1),26),'C07_Quarantine':((1.0,11.2,1.68),(4.5,11.8,1),26),'C08_Extraction':((-2.9,13.9,1.68),(-4.35,16.05,1.5),24),'W01_Personnel':((3.0,2.4,1.68),(6,2.4,1.7),20),'W02_ReceivingReturn':((0,5.0,1.68),(0,0,1.8),22),'W03_Dispatch':((0,14.0,1.68),(0,18,1.8),22),'W04_CellService':((-2.9,12.9,1.68),(-4.5,11.6,1.3),24)}
for name,(loc,target,lens) in camera_repairs.items():
    o=bpy.data.objects[name];o.location=loc;o.data.lens=lens;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
# Warm-neutral directional light, not uniform ceiling fill.
for d in bpy.data.lights:
    if d.name.startswith('Practical pool'):d.energy*=.75
    if d.type=='SPOT':d.energy*=1.7;d.spot_size=math.radians(60)

