"""W07: contract-specific doors, quarantine identity and physical access hardware."""
current='Architecture'
# Correct personnel geometry to the inherited outward-swing contract.
portal=bpy.data.objects['WS_PERSONNEL']
for ob in list(portal.children):
    if ob.name.startswith(('Roller door barrel','Barrel bearing bracket','Seal track')):bpy.data.objects.remove(ob,do_unlink=True)
p=assembly('WS_PERSONNEL_LEAF',(6.17,2.98,0),0)
p['door_id']='WS_PERSONNEL';p['closed_angle_z']=-math.pi/2;p['open_angle_z']=0.;p['hinge_axis']='+Z';p['state']='parked_open';p['sweep_ownership']='Waste-owned leaf; exterior sector reserved, neighboring network unbound'
box('Personnel leaf inner core',(.575,0,1.155),(1.15,.05,2.27),'pale',p,.008)
for x in [.03,1.12]:box('Personnel leaf folded edge',(x,0,1.155),(.055,.065,2.27),'bus',p,.005)
for z in [.045,2.265]:box('Personnel leaf end rail',(.575,0,z),(1.15,.065,.055),'bus',p,.005)
box('Personnel kick plate',(.575,-.032,.26),(1.04,.014,.34),'metal',p,.004)
box('Panic bar bracket',(.26,-.060,1.04),(.075,.10,.10),'darkpaint',p,.009)
box('Panic bar bracket',(.93,-.060,1.04),(.075,.10,.10),'darkpaint',p,.009)
beam('Personnel panic bar',(.26,-.13,1.04),(.93,-.13,1.04),.042,'metal',p)
for z in [.24,1.15,2.03]:
    cyl('Personnel hinge pin',(0,0,z),.024,.14,'metal',p)
    box('Personnel jamb hinge leaf',(-.018,.026,z),(.08,.075,.11),'metal',p,.003)
box('Personnel closer body',(.15,.06,2.13),(.23,.12,.10),'bus',p,.007)
beam('Personnel closer linkage',(.18,.10,2.14),(-.02,.21,2.14),.022,'metal',p)
plaque(p,'WS_PERSONNEL',(.58,-.033,1.72),.96,.16,size=.083)
# Booth framing has an exact 1.10 x 2.30 clear aperture.
for ob in bpy.data.objects:
    if ob.name.startswith('Booth jamb'):
        if abs(ob.location.y-1.65)<.001:ob.location.y=1.61
        if abs(ob.location.y-2.75)<.001:ob.location.y=2.79
box('Booth door transom',(-2.4,2.2,2.40),(.10,1.10,.20),'darkpaint',bevel=.006)
p=assembly('WS_MONITOR_BOOTH_LEAF',(-2.4,2.735,0),-math.pi)
p['door_id']='WS_MONITOR_BOOTH';p['closed_angle_z']=-math.pi/2;p['open_angle_z']=-math.pi;p['hinge_axis']='+Z';p['state']='parked_open'
box('Booth door lower panel',(.52,0,.47),(1.04,.038,.90),'pale',p,.004)
box('Booth door glazing',(.52,0,1.55),(.95,.012,1.19),'glass',p,.002)
for x in [.025,1.015]:box('Booth leaf stile',(x,0,1.145),(.05,.05,2.25),'darkpaint',p,.003)
for z in [.045,.945,2.245]:box('Booth leaf rail',(.52,0,z),(1.04,.05,.05),'darkpaint',p,.003)
for z in [.25,1.15,2.03]:cyl('Booth hinge',(0,0,z),.021,.13,'metal',p)
for y in [-.055,.055]:
    beam('Booth lever mount',(.92,0,1.03),(.92,y,1.03),.025,'metal',p)
    beam('Booth lever grip',(.92,y,1.03),(.81,y,1.03),.022,'metal',p)
e=assembly('IF_WS_MONITOR_BOOTH',(-2.4,2.2,0));e['connection_id']='WS_MONITOR_BOOTH';e['outward_normal']=json.dumps([1,0,0]);e['internal_only']=True
# Semantic quarantine is not an unclassified third dry store.
q=bpy.data.objects['QH01'];q['equipment_type']='quarantine_container';q['interaction']='scan;inspect_quarantine;seal;search;escape';q['inspection_hook']='INSPECT_QUARANTINE';q['capacity_state']='open_inspection';q['host_state']='anchor_only'
e=assembly('VOLUME_QH01_HIDE',(0,0,.64),parent=q);e['dimensions_m']=json.dumps([1.85,.65,.65]);e['volume_role']='searchable_hiding';e['authority']='engine_host';e['implemented']='anchor_only'
e=bpy.data.objects['INSPECT_QUARANTINE'];e['target_id']='QH01'
for name,target in [('INTERACT_INVENTORY','IM01_INVENTORY'),('INTERACT_VENT_ISOLATE','VF01_EXTRACTION'),('INCIDENT_WASTE_BREACH','SC01')]:bpy.data.objects[name]['target_id']=target
