"""M04 service completeness, contact and sign corrections; original R09 arrangement retained."""
current='OCRU'
for o in SC.objects:
    if o.name.startswith('Interface label mounting stem'):
        o.location.y=-.015
        # Stay behind all glyph planes; short extension joins label backing to enclosure.
        o.scale.y=(.05 if o.parent.name=='OCRU_SUIT_SERVICE' else .13)/o.dimensions.y
for n in ['Engraved backing ORGANIC CONTINUITY','Engraved ORGANIC CONTINUITY']:SC.objects[n].location.y-=.06
# Long chamber identity belongs on its own rear fascia, clear of panels and handles.
current='Stations';p=SC.objects['RESTART_CONSOLE']
for o in list(SC.objects):
    if o.name.startswith('Restart step label'):bpy.data.objects.remove(o,do_unlink=True)
for x,t in [(-.53,'ARM'),(-.05,'CONNECT'),(.43,'RESTART')]:plaque(p,t,(x,-.459,.93),.34,.060,mat='darkpaint',size=.032)
SC.objects['Employee waiting'].location.z=1.255;SC.objects['Employee waiting'].data.size=.026
for o in SC.objects:
    if o.name.startswith('Telemetry status bar'):o.location.z=1.255
# Add fabricated monitor surrounds and face fixings rather than enlarging screens.
for x in [-.46,.43]:
    for xx in [x-.34,x+.34]:fasteners('Monitor bezel fixing',[xx],[1.22,1.54],.11,p,r=.007)
for x in [-.53,-.05,.43]:
    tube('Guarded control orange cap',[(x-.075,-.27,1.12),(x-.075,-.27,1.13),(x+.075,-.27,1.13),(x+.075,-.27,1.12)],.009,'orange',p)
# Reserve cabinet is hollow manufactured sheet construction with real serviceable battery trays.
p=SC.objects['RESERVE_POWER'];bpy.data.objects.remove(SC.objects['Reserve cabinet carcass'],do_unlink=True)
for x in [-.40,.40]:box('Reserve folded side',(x,0,.74),(.035,.53,1.25),'bus',p,.004)
for z in [.13,1.355]:box('Reserve folded cap',(0,0,z),(.82,.53,.035),'bus',p,.004)
box('Reserve folded back',(0,.255,.74),(.80,.025,1.25),'bus',p,.003)
for z in [.30,.71]:
    box('Battery supported drawer rail',(0,0,z),(.70,.43,.035),'metal',p,.003)
    box('Reserve battery module',(0,0,z+.16),(.63,.39,.27),'darkpaint',p,.006)
    for x in [-.25,.25]:cyl('Battery terminal',(x,.11,z+.31),.023,.025,'copper',p)
    tube('Battery carry handle',[(-.17,-.20,z+.19),(-.17,-.24,z+.23),(.17,-.24,z+.23),(.17,-.20,z+.19)],.012,'orange',p)
plaque(p,'MAINS / RESERVE',(0,-.322,.60),.60,.085,size=.041)
door=assembly('RESERVE_SERVICE_DOOR',(-.375,-.29,.77),parent=p);door['closed_angle']=0;door['service_angle']=math.radians(100)
# Door, gauge and front controls travel together; preserve their local placements.
front_names=['Reserve removable door','Reserve door fastener','Screwdriver slot','Handle','Gauge','Dial','Needle','Engraved','Rotary']
for o in list(p.children):
    if o==door:continue
    if o.name=='Reserve removable door' or (o.type in {'MESH','FONT','CURVE'} and o.location.y<-.285 and not o.name.startswith('Cabinet perimeter')):
        o.parent=door;o.location-=door.location
for z in [-.38,.38]:
    cyl('Reserve service hinge',(0,0,z),.021,.13,'metal',door)
# Rear east supply isolation panel occupies the existing PowerPanel reserved position.
current='Utilities';p=assembly('MEDICAL_ISOLATION',(3.45,8.94,1.35),support='Rear east wall',anchors=[[-.18,.06,-.2],[.18,.06,.2]],direction=[0,1,0])
box('Isolation wall cabinet',(0,0,0),(.50,.12,.68),'darkpaint',p,.005)
box('Isolation removable face',(0,-.07,0),(.44,.018,.60),'bus',p,.004)
rotary(p,0,-.09,.04,'orange');plaque(p,'MED POWER',(0,-.083,.21),.39,.10,size=.042)
plaque(p,'ISOLATE',(0,-.083,-.21),.32,.08,size=.039)
fasteners('Isolation face screw',[-.18,.18],[-.25,.25],-.084,p,r=.010)
tube('Panel incoming conduit',[(3.45,8.975,1.69),(3.45,8.975,2.68),(3.45,9.18,2.68)],.021,'metal')
# Spring reel stores 5m wash hose; fittings join regulator, shower and captive wand.
p=SC.objects['DECON_WASH'];reel=assembly('DECON_HOSE_REEL',(.42,.93,1.94),parent=p);reel['usable_hose_length_m']=5.0
box('Reel wall backing',(0,.10,0),(.40,.06,.43),'darkpaint',reel,.004)
box('Reel support boss',(0,.045,0),(.11,.08,.11),'metal',reel,.003)
for y in [-.065,.035]:cyl('Reel formed cheek',(0,y,0),.185,.025,'orange',reel,'Y',32)
cyl('Reel hose drum',(0,-.015,0),.12,.09,'darkpaint',reel,'Y')
for j in range(4):ring('Stored wash hose',(0,-.055+j*.022,0),.146,.012,'rubber',reel,'Y')
cyl('Reel axle',(0,-.09,0),.045,.06,'metal',reel,'Y')
plaque(reel,'5 m',(0,-.12,0),.09,.065,size=.035)
tube('Regulator reel feed',[(.45,.91,1.40),(.63,.91,1.40),(.63,.96,1.78),(.42,.96,1.94)],.017,'metal',p)
tube('Regulator shower branch',[(.45,1.04,1.40),(-.30,1.04,1.40),(-.30,1.03,1.50)],.017,'metal',p)
# Replace the original disconnected parked hose with one continuous reel-to-wand run.
bpy.data.objects.remove(SC.objects['Wand service hose'],do_unlink=True)
tube('Wand service hose',[(.42,.84,1.78),(.38,.83,1.42),(.32,.83,.90),(.10,.83,.72),(-.14,.83,.74),(-.30,.88,1.12)],.020,'rubber',p)
for x,z in [(.45,1.4),(-.30,1.40)]:
    cyl('Wash fitting union',(x,1.025,z),.026,.08,'metal',p,'X',12)
    box('Wash pipe wall clip',(x,1.04,z+.1),(.07,.07,.07),'metal',p,.002)
plaque(p,'WASH / BEFORE LOAD',(-.10,1.035,1.72),.76,.12,size=.048)
box('Wash instruction backing support',(-.10,1.065,1.72),(.68,.065,.10),'darkpaint',p,.002)
# Fresh small maintenance artifacts are original and remain on the supply worktop.
current='Props';p=SC.objects['SUPPLY_BENCH']
box('Service tool tray',(.80,-.04,.968),(.35,.43,.045),'darkpaint',p,.004)
for x in [.70,.88]:
    cyl('Seal tool grip',(x,-.04,1.00),.018,.23,'orange',p,'Y',16)
    cyl('Seal tool shaft',(x,.09,1.00),.006,.12,'metal',p,'Y',12)
# Controlled localized contact wear: specific touch points, not an overall noise wash.
for name in ['Console working surface','Reserve removable door','Cart deck','Supply bench top']:
    o=SC.objects.get(name)
    if o:o['finish_note']='matte coating; localized exposed edge at handles and rims'
for x in [-.82,.78]:box('Console edge contact abrasion',(x,-.447,.949),(.06,.006,.008),'edge',SC.objects['RESTART_CONSOLE'],.001)
# Strong consistent wayfinding typography uses the bundled Blender font with increased weight via tiny bevel.
for o in SC.objects:
    if o.type=='FONT' and o.data.size>=.075:o.data.offset=.0007
