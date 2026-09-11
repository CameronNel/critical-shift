"""W13: close measured attachment gaps; no decorative floating hardware."""
current='Architecture'
for p in [o for o in SC.objects if o.get('portal_id')]:
    h=3.2 if p.name=='WS_RECEIVING' else 2.8 if p.name=='WS_DISPATCH' else 2.3
    for x in [-.85,.85]:box('Door sign stand-off',(x,-.105,h+.77),(.055,.22,.12),'metal',p,.003)
for p in [o for o in SC.objects if o.name.startswith('Wall bay wayfinding')]:p.location.x=5.999 if p.location.x>0 else -5.999
current='Lighting'
for p in [o for o in SC.objects if o.name.startswith('Suspended practical')]:
    for x in [-.55,.55]:cyl('Suspension rod locknut',(x,0,.0725),.026,.035,'metal',p,vertices=6)
current='Casks'
for p in [o for o in SC.objects if o.get('equipment_type')=='shielded_cask']:
    for side in [-1,1]:cyl('Trunnion welded boss',(side*.53,0,2.3*.65),.12,.12,'metal',p,'X')
current='Monitoring';p=bpy.data.objects['Receiving dosimeter']
cyl('Dosimeter mounting collar',(0,-.06,.05),.07,.07,'metal',p,'Y')
current='Ventilation';p=bpy.data.objects['VF01_EXTRACTION']
box('Filter outlet bolted adapter',(.40,.03,1.4),(.12,.68,.68),'metal',p,.008)
for y in [-.235,.295]:
    for z in [1.135,1.665]:cyl('Filter outlet adapter bolt',(.47,y,z),.019,.04,'darkpaint',p,'X',6)
box('Gauge mounting bracket',(-.77,-.50,1.965),(.10,.14,.20),'bus',p,.006)
# A broader entrance view includes the booth and receiving apron. The change
# is recorded before the final fixed-camera baseline is frozen.
bpy.data.objects['C01_Entry'].data.lens=20
