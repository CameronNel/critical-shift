"""M03 measured contact fixes and explicit movable transfer mechanisms."""
current='Architecture';p=SC.objects['Main entry identity']
box('Entry identity wall standoff',(0,.036,0),(2.2,.072,.18),'darkpaint',p,.002)
current='OCRU'
for root,z,depth in [('OCRU_SUIT_SERVICE',.265,.13),('OCRU_CARTRIDGE_RECEIVER',.31,.14),('OCRU_CARTRIDGE_RECEIVER',-.325,.14)]:
    p=SC.objects[root];box('Interface label mounting stem',(0,-.045,z),(.07,depth,.12),'darkpaint',p,.002)
p=SC.objects['OCRU']
for x in [-1.7,1.7]:box('Inner service panel rear support',(x,1.105,1.48),(.40,.16,1.20),'bus',p,.003)
for x in [-1.15,1.15]:box('Inner luminaire roof hanger',(x,.25,2.61),(.09,.11,.16),'darkpaint',p,.003)
# The bridge is supported on telescoping pivot slides below the pan when parked.
br=SC.objects['OCRU_TRANSFER_BRIDGE'];br.location.z=.924;br['deploy_z']=.999;br['park_z']=.924
tray=SC.objects['OCRU_BERTH']
for x in [-.8,.8]:
    box('Bridge pivot slide sleeve',(x,-.465,.917),(.065,.055,.08),'darkpaint',tray,.002)
    box('Bridge lift slide',(x,-.465,.97),(.035,.031,.11),'metal',tray,.002)
for o in list(SC.objects):
    if o.name.startswith('Bridge pivot knuckle'):o.location.z=.924
current='Stations';p=SC.objects['RESTART_CONSOLE']
for x in [-.64,.64]:box('Restart sign support',(x,.19,1.63),(.045,.07,.25),'darkpaint',p,.002)
p=SC.objects['CARTRIDGE_BANK'];box('Stock sign mounting rail',(0,-.35,2.13),(.65,.035,.10),'darkpaint',p,.002)
p=SC.objects['RECOVERY_BERTH'];box('Recovery identity bed bracket',(0,-1.15,.615),(.40,.06,.10),'metal',p,.003)
for o in SC.objects:
    if o.name.startswith('Telemetry status bar'):o.location.z=1.235
current='Utilities';p=SC.objects['HANDWASH'];box('Tap rear rim mounting plate',(.12,.15,.925),(.16,.14,.012),'metal',p,.002)
# The monitor is an upright service panel: keep screen face and housing coplanar.
SC.objects['Operator sloped panel'].rotation_euler.x=0
# Editable cart lift deck, preserving world placements in the default parked pose.
current='Stations';cart=SC.objects['BODY_CART'];deck=assembly('CART_LIFT_DECK',(0,0,0),parent=cart);deck['parked_surface_z']=.92;deck['transfer_surface_z']=1.008
prefixes=['Cart deck','Cart segmented mattress','Stretcher side retaining rim','Stretcher grab loop','Engraved backing TRANSFER','Engraved TRANSFER']
for o in list(cart.children):
    if any(o.name.startswith(t) for t in prefixes):o.parent=deck
cart['docking_center']=json.dumps([-1.08,4.63,0]);cart['extraction_route']=json.dumps([[-3.12,1.33],[-3.12,1.42],[0,1.42]])
# Additional authored state cameras live only in the evidence script, preserving 14 fixed cameras.
