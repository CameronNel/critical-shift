"""W12: purposeful wall grazing and legible doorway hierarchy."""
current='Lighting'
for ob in [o for o in SC.objects if o.type=='LIGHT' and o.data.type=='SPOT']:
    side=-1 if ob.location.x<0 else 1
    ob.rotation_euler=(Vector((side*5.998,ob.location.y,2.20))-ob.location).to_track_quat('-Z','Y').to_euler()
    ob.data.spot_size=math.radians(64);ob.data.spot_blend=.50
for x in [-4,0,4]:
    p=assembly('Dispatch wall washer',(x,17.98,4.05))
    box('Washer fixed backplate',(0,-.02,0),(.30,.06,.30),'darkpaint',p,.008)
    box('Washer cantilever housing',(0,-.15,-.04),(.40,.26,.17),'bus',p,.016)
    box('Washer underside glass',(0,-.12,-.13),(.30,.15,.015),'lamp',p,.004)
    d=bpy.data.lights.new('Dispatch practical wall cone','SPOT');d.energy=500;d.color=(1,.77,.52);d.spot_size=math.radians(64);d.spot_blend=.50;d.shadow_soft_size=.12
    ob=bpy.data.objects.new('Dispatch practical wall cone',d);COL[current].objects.link(ob);ob.location=(x,17.78,3.88);ob.rotation_euler=(Vector((x,18,2.55))-ob.location).to_track_quat('-Z','Y').to_euler()
current='Architecture'
for p in [o for o in SC.objects if o.get('portal_id')]:
    h=3.2 if p.name=='WS_RECEIVING' else 2.8 if p.name=='WS_DISPATCH' else 2.3
    for ob in p.children:
        if ob.type=='FONT' and ob.name.startswith('Portal identifier'):ob.data.size=.17;ob.location.z=h+.78
    text('Exact connection label',p.name,(0,-.260,h+.64),.065,'ink',p,align='CENTER')
