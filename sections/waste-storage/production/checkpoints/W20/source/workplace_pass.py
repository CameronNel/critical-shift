"""W15: useful seal-work setup and distinct quiet material response."""
current='Workshop';p=bpy.data.objects['WB01_SEAL_REPAIR']
for ob in p.children:
    if ob.name.startswith(('Seal service case','Case latch')):ob.location.z-=.665
for y in [-.29,.29]:box('Workbench longitudinal apron',(0,y,.835),(1.51,.055,.10),'darkpaint',p,.004)
for x in [-.72,.72]:
    box('Workbench side apron',(x,0,.835),(.055,.61,.10),'darkpaint',p,.004)
    box('Tool board rear upright',(x,.35,1.30),(.04,.05,.87),'darkpaint',p,.003)
    for z in [1.05,1.57]:cyl('Board through bolt',(x,.278,z),.014,.09,'metal',p,'Y',6)
for j in range(5):cyl('Tool hanging pin',(-.56+j*.26,.282,1.547),.007,.055,'metal',p,'Y',12)
box('Vice cast base',(-.40,-.08,.9775),(.30,.25,.040),'paint',p,.008)
box('Vice sliding bed',(-.40,-.08,1.02),(.24,.22,.045),'metal',p,.005)
for y in [.04,-.08]:
    box('Vice jaw body',(-.40,y,1.09),(.25,.045,.12),'paint',p,.008)
    box('Vice replaceable jaw',(-.40,y-.025,1.115),(.23,.010,.065),'metal',p,.002)
cyl('Vice feed screw',(-.40,-.16,1.035),.018,.24,'metal',p,'Y',20)
ring('Vice handwheel',(-.40,-.285,1.035),.07,.009,'metal',p,'Y')
for x in [-.47,-.33]:beam('Vice handwheel spoke',(-.40,-.285,1.035),(x,-.285,1.035),.009,'metal',p)
for x in [-.50,-.30]:cyl('Vice mounting bolt',(x,-.08,1.005),.012,.04,'darkpaint',p,vertices=6)
current='Monitoring';p=bpy.data.objects['IM01_INVENTORY']
box('Scanner optical window',(.50,-.049,1.24),(.10,.008,.035),'black',p,.004)
box('Scanner trigger',(.50,-.007,1.115),(.035,.018,.04),'paint',p,.003)
for ob in p.children:
    if ob.name=='Logbook title':ob.location.y=-.145
rules=sorted([o for o in p.children if o.name.startswith('Printed logbook rule')],key=lambda o:o.name)
for j,ob in enumerate(rules):ob.location.y=-.20-j*.035
for key,var in [('wall',.055),('floor',.08),('pale',.04)]:
    m=M[key];base=m.diffuse_color[:3]
    for n in m.node_tree.nodes:
        if n.type=='VALTORGB':
            n.color_ramp.elements[0].color=(*(v*(1-var) for v in base),1);n.color_ramp.elements[1].color=(*(v*(1+var) for v in base),1)
for key in ['paint','pale']:M[key].node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=0
for ob in [o for o in SC.objects if o.type=='LIGHT' and o.name.startswith('Practical pool') and abs(o.location.x)<.1]:ob.data.energy*=.80
