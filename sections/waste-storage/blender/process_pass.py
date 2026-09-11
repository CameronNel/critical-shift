"""W11: separate intake/exhaust paths; manufacture filter interfaces."""
current='Ventilation';p=bpy.data.objects['VF01_EXTRACTION']
ob=bpy.data.objects['Rear intake crossheader'];ob.location.z=4.48;ob.dimensions.z=.30
ob=bpy.data.objects['Filter inlet drop'];ob.location=(-5.25,16.10,3.025);ob.dimensions=(.43,.43,2.01)
ob=bpy.data.objects['Filter inlet upper offset'];ob.location=(-5.35,16.10,4.03);ob.dimensions=(.65,.43,.45)
for x in [-5.45,5.45]:
    box('Raised intake bridge riser',(x,17.10,4.255),(.43,.43,.45),'bus',bevel=.006)
    for z in [4.10,4.40]:box('Intake bridge sleeve',(x,17.1,z),(.49,.49,.045),'metal',bevel=.003)
box('Filter inlet welded neck',(-.90,.05,2.035),(.52,.52,.09),'bus',p,.006)
for x in [-1.10,-.70]:
    for y in [-.15,.25]:cyl('Inlet neck flange bolt',(x,y,2.093),.015,.035,'metal',p,vertices=6)
# Filter cassette sealing rims, actual hinge pins and pressure sampling tubing.
for x in [-.78,.02]:
    for xx in [x-.285,x+.285]:box('Filter folded edge',(xx,-.532,1.20),(.025,.014,1.22),'metal',p,.003)
    for z in [.60,1.80]:box('Filter folded edge',(x,-.532,z),(.57,.014,.025),'metal',p,.003)
    for z in [.65,1.75]:
        cyl('Filter hinge pin',(x-.27,-.59,z),.017,.16,'metal',p)
        for zz in [z-.045,z+.045]:box('Filter hinge leaf',(x-.245,-.571,zz),(.10,.04,.045),'bus',p,.003)
    plaque(p,'F1 / IN' if x<-.3 else 'F2 / FINAL',(x,-.534,1.61),.43,.11,size=.045)
for x,z in [(-1.03,1.90),(.25,1.90)]:
    cyl('DP sample fitting',(x,-.475,z),.021,.055,'metal',p,'Y',12)
tube('DP upstream impulse line',[(-1.03,-.51,1.90),(-1.04,-.56,1.96),(-.86,-.575,1.99)],.007,'rubber',p)
tube('DP downstream impulse line',[(.25,-.51,1.90),(.25,-.55,2.095),(-.63,-.57,2.095),(-.66,-.575,2.02)],.007,'rubber',p)
for x in [-.45,-.05]:box('DP line retaining clip',(x,-.51,2.095),(.035,.12,.025),'metal',p,.002)
# Metric texture coordinates avoid stretched cloudy material on thin parts.
for m in bpy.data.materials:
    if not m.use_nodes or 'wood' in m.name.lower():continue
    nt=m.node_tree
    for tc in [n for n in nt.nodes if n.type=='TEX_COORD']:
        for shader_link in list(tc.outputs['Generated'].links):
            sock=shader_link.to_socket;nt.links.remove(shader_link);nt.links.new(tc.outputs['Object'],sock)
    for n in nt.nodes:
        if n.type=='TEX_NOISE':
            old=n.inputs['Scale'].default_value
            n.inputs['Scale'].default_value=250 if old>=80 else 4.5
# Fixed approach corrections are explicitly recorded as a new camera baseline.
for name,loc,target,lens in [('C08_Extraction',(-1.4,14.05,1.68),(-4.35,16.05,1.75),21),('C09_Inventory',(-2.6,2.2,1.68),(-4.1,1.65,1.30),25)]:
    o=bpy.data.objects[name];o.location=loc;o.data.lens=lens;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
