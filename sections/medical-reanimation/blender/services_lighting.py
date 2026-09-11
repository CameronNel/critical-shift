"""Purposeful decontamination, service routes, lights and sparse human artifacts."""
current='Utilities'
p=assembly('DECON_WASH',(2.33,10.06,0),support='Decon floor',anchors=[[-.55,-.7,0],[.55,-.7,0],[-.55,.7,0],[.55,.7,0]]);p['equipment_type']='decontamination'
# Grating is flush with the floor; cart washing occurs on the adjoining apron.
for x in [-.68,.68]:box('Flush drain edge',(x,0,.002),(.045,1.82,.004),'metal',p,.001)
for y in [-.89,.89]:box('Flush drain cross edge',(0,y,.002),(1.40,.045,.004),'metal',p,.001)
for j in range(21):box('Drain grating bar',(0,-.84+j*.084,.002),(1.32,.024,.004),'darkpaint',p,.001)
box('Rear wash control backing',(.45,.99,1.40),(.40,.10,.45),'pale',p,.008)
rotary(p,.45,.925,1.4,'orange')
tube('Wash supply riser',[(1.025,.64,.60),(.72,.64,.60),(.72,.85,1.40),(.45,.92,1.40)],.020,'metal',p)
tube('Wand service hose',[(.45,.92,1.29),(.40,.88,.85),(.15,.88,.62),(-.15,.88,.64),(-.30,.88,1.12)],.020,'rubber',p)
beam('Decon wand grip',(-.30,.88,1.12),(-.30,.88,1.42),.034,'darkpaint',p)
beam('Decon wash nozzle',(-.30,.88,1.42),(-.30,.76,1.50),.027,'metal',p)
box('Wand captive holder',(-.30,.97,1.20),(.10,.20,.12),'bus',p,.005)
tube('Shower arch',[(-.30,1.03,1.50),(-.30,1.03,2.10),(-.30,.4,2.10)],.02,'metal',p)
cyl('Wash rose',(-.30,.40,2.07),.085,.032,'metal',p)
box('Controlled drain sump cover',(0,.98,.15),(.30,.10,.20),'darkpaint',p,.004)
tube('Contained drain connection',[(0,.99,.15),(0,1.24,.15)],.045,'metal',p)
box('Decon extraction grille',(0,1.10,2.25),(.40,.06,.30),'darkpaint',p,.004)
for x in [-.15,-.075,0,.075,.15]:box('Extract grille blade',(x,1.062,2.25),(.025,.045,.26),'metal',p,.002)
box('Extract wall sleeve',(0,1.18,2.25),(.4,.12,.3),'bus',p,.003)

p=assembly('HANDWASH',(3.72,2.95,0),-math.pi/2);p['equipment_type']='handwash'
box('Sink wall bracket',(0,.20,.71),(.53,.10,.25),'darkpaint',p,.005)
box('Basin bottom',(0,-.015,.78),(.53,.43,.04),'metal',p,.006)
for x in [-.25,.25]:box('Basin folded side',(x,-.015,.85),(.03,.43,.14),'metal',p,.006)
for y in [-.22,.20]:box('Basin folded rim',(0,y,.85),(.53,.03,.14),'metal',p,.005)
tube('Handwash tap',[(.12,.13,.92),(.12,.13,1.12),(.12,-.03,1.12)],.016,'metal',p)
tube('Sink waste pipe',[(0,0,.76),(0,0,.53),(0,.26,.53),(0,.28,.15)],.025,'metal',p)
box('Handwash soap dispenser',(-.18,.22,1.2),(.14,.12,.22),'pale',p,.012)

# Bounded, clamped conduits join explicit utility sockets to normal/reserve feed.
tube('Medical power distribution',[(-2.15,9.175,2.65),(-2.15,8.93,2.65),(-2.15,8.85,1.35)],.026,'rubber')
tube('OCRU supply route',[(-2.15,8.85,1.35),(-2.15,8.85,3.13),(-3.80,8.85,3.13),(-3.80,4.63,3.13),(-3.65,4.63,2.91)],.028,'rubber')
for y in [5,6,7,8]:box('Supply conduit wall clamp',(-3.90,y,3.13),(.20,.08,.10),'metal',bevel=.003)
for x in [-3.5,-2.7]:box('Rear cable wall clamp',(x,8.965,3.13),(.09,.07,.10),'metal',bevel=.003)
tube('Console telemetry feed',[(-.4,9.175,2.65),(-.4,8.96,2.65),(-.4,8.96,1.50)],.018,'metal')
for z in [1.8,2.3]:box('Telemetry clip',(-.4,8.99,z),(.07,.02,.07),'darkpaint',bevel=.003)
# Boundary couplers are capped. No neighboring network is invented.
contract=json.loads((ROOT/'interface.json').read_text())
for port in contract['utilities']:
    center=Vector(port['center']);normal=Vector(port['outward']);axis='X' if abs(normal.x) else 'Y'
    cyl(port['id']+' termination',center,.048,.02,'metal',axis=axis)
    mark=assembly('IF_'+port['id'],center);mark['connection_id']=port['id'];mark['outward_normal']=json.dumps(port['outward'])

current='Props'
# Small maintained workplace artifacts stay on proper supports.
for x,y,z in [(3.52,1.80,.975),(3.52,1.32,.975)]:
    box('Sterile pack',(x,y,z),(.25,.21,.03),'paper',bevel=.007)
    box('Sterile pack seal',(x,y,z+.017),(.035,.20,.005),'orange',bevel=.001)
p=assembly('Return to service notice',(3.97,3.15,1.95),-math.pi/2)
box('Notice backing',(0,0,0),(.42,.02,.48),'darkpaint',p,.005)
box('Notice paper',(0,-.013,0),(.36,.003,.42),'paper',p,.001)
text('Notice heading','RETURN TO',(-.15,-.016,.105),.043,'ink',p)
text('Notice heading 2','SERVICE',(-.15,-.016,.045),.043,'ink',p)
text('Notice instruction','SIGN BEFORE LEAVING',(-.15,-.016,-.105),.022,'ink',p)

current='Lighting'
def area_light(name,loc,target,energy,size,color=(1,.85,.67)):
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color
    o=bpy.data.objects.new(name,d);COL[current].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
for x,y,power in [(-1.65,1.4,120),(1.65,1.4,110),(-1.2,4.8,110),(1.5,4.8,100),(-1.3,7.6,140),(1.55,7.6,110)]:
    root=assembly('Ceiling practical',(x,y,3.18))
    for xx in [-.45,.45]:beam('Luminaire suspension',(xx,0,0),(xx,0,.42),.012,'metal',root)
    box('Luminaire folded housing',(0,0,0),(1.1,.26,.09),'darkpaint',root,.009)
    box('Luminaire frosted diffuser',(0,0,-.055),(1.01,.20,.015),'task',root,.002)
    area_light('Ceiling practical output',(x,y,3.11),(x,y,0),power,1.0,(1,.91,.79))
for x,y,target in [(-.4,8.89,(-.4,9,1.6)),(3.88,1.5,(4,1.5,1.4)),(3.88,7.45,(4,7.45,1.7))]:
    root=assembly('Wall task practical',(x,y,2.92))
    box('Wall luminaire',(0,0,0),(.50,.13,.085),'darkpaint',root,.007)
    box('Wall task lens',(0,-.02,-.05),(.42,.09,.014),'task',root,.002)
    area_light('Wall grazed work zone',(x,y,2.85),target,85,.5)
area_light('OCRU neutral inner light',(-2.68,4.63,2.4),(-2.0,4.63,.95),75,1.7,(1,.97,.91))
area_light('Decon task light',(2.2,10.15,2.35),(2.2,10.15,0),55,.7)
box('Decon ceiling lamp',(2.2,10.15,2.50),(.46,.28,.08),'darkpaint',bevel=.006)
box('Decon diffuser',(2.2,10.15,2.451),(.39,.22,.015),'task',bevel=.002)
