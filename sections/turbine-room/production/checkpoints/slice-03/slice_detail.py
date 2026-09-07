"""Second-pass object-specific construction and sparse, use-driven wear."""
import math,random
import bpy
def details(a):
    box,cyl,beam,ring,torus,mesh,text,bolt,anchor=a.box,a.cyl,a.beam,a.ring,a.torus,a.mesh,a.text,a.bolt,a.anchor
    a.group('05 Maintenance bay')
    a.M['worn']=a.material('Exposed old primer','827e6b',.83,.16)
    a.M['oil']=a.material('Dry mineral oil residue','504b38',.66,variation=.1)
    a.M['wooddark']=a.material('Dark endgrain and old cuts','50432f',.9)
    a.M['edge']=a.material('Bare scuffed edge','8b9189',.58,.65)
    # Wood grain has physical long direction; it is confined to the timber.
    m=a.M['wood'];n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF')
    tx=n.new('ShaderNodeTexNoise');tx.inputs['Scale'].default_value=4;tx.inputs['Detail'].default_value=1.7;tx.inputs['Roughness'].default_value=.65
    co=n.new('ShaderNodeTexCoord');mp=n.new('ShaderNodeVectorMath');mp.operation='MULTIPLY';mp.inputs[1].default_value=(30,1,5);l.new(co.outputs['Generated'],mp.inputs[0]);l.new(mp.outputs[0],tx.inputs[0])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*a.rgb('67563e'),1);ramp.color_ramp.elements[0].position=.1;ramp.color_ramp.elements[1].color=(*a.rgb('9a8058'),1);ramp.color_ramp.elements[1].position=.9;l.new(tx.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],b.inputs['Base Color'])
    for x in [-3.47,-3.08]:box('Glued plank seam',(x,21.35,1.001),(.0018,2.98,.001),'wooddark',0)
    box('Bench front edge angle',(-2.619,21.35,.91),(.035,2.99,.06),'darkteal',.002)
    for y in [20.04,20.9,21.8,22.68]:bolt('Bench fascia screw',(-2.593,y,.912),'X',.012)
    # In-progress oil inspection leaves one localized contact patch, not blanket grunge.
    random.seed(517)
    center=(-3.21,21.27,1.002);verts=[center]
    for i in range(27):
        angle=i*math.tau/27;r=1+random.uniform(-.14,.14);verts.append((center[0]+.4*r*math.cos(angle),center[1]+.24*r*math.sin(angle),center[2]))
    stain=mesh('Old bearing oil witness',verts,[(0,i+1,(i+1)%27+1) for i in range(27)],'oil')
    attr=stain.data.color_attributes.new(name='wear_alpha',type='FLOAT_COLOR',domain='POINT')
    for i,c in enumerate(attr.data):c.color=(.32,.32,.32,1) if i==0 else (0,0,0,1)
    oil=a.M['oil'];nodes=oil.node_tree.nodes;links=oil.node_tree.links
    opaque=nodes.get('Principled BSDF');mix=nodes.new('ShaderNodeMixShader');transparent=nodes.new('ShaderNodeBsdfTransparent');attribute=nodes.new('ShaderNodeAttribute');attribute.attribute_name='wear_alpha'
    links.new(attribute.outputs['Color'],mix.inputs[0]);links.new(transparent.outputs[0],mix.inputs[1]);links.new(opaque.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],nodes.get('Material Output').inputs[0])
    for i in range(13):
        y=20.1+random.random()*2.5;x=-2.82-random.random()*.25
        o=box('Tool contact cut',(x,y,1.003),(.0009,random.uniform(.025,.095),.001),'wooddark',0);o.rotation_euler[2]=random.uniform(-.6,.6)
    for y in [20.12,20.38,21.63,22.49]:
        mesh('Edge paint loss',[(-2.599,y,.929),(-2.599,y+.058,.925),(-2.599,y+.09,.915),(-2.599,y+.01,.917)],[(0,1,2,3)],'edge')
    # Vise moving slide, fixed-jaw web, machined jaw faces, threaded screw and stop collars.
    box('Vise moving ram',(-2.8,20.18,1.18),(.13,.46,.105),'steel',.003)
    for y in [20.18,20.52]:
        box('Vise jaw back',(-2.8,y,1.24),(.29,.083,.13),'teal',.008)
        for i in range(10):
            x=-2.94+i*.03
            beam('Vise jaw grip tooth',(x,y-.035,1.285),(x+.018,y-.035,1.325),.0018,'dark')
        bolt('Replaceable jaw screw',(-2.89,y-.049,1.307),'Y',.01);bolt('Replaceable jaw screw',(-2.71,y-.049,1.307),'Y',.01)
    for y in [19.855+i*.013 for i in range(19)]:torus('Vise exposed screw thread',(-2.8,y,1.17),.028,.004,'steel','Y')
    cyl('Vise handwheel boss',(-2.8,19.82,1.17),.043,.048,'steel','Y')
    for x in [-2.96,-2.6]:cyl('Vise handle stopper',(x,19.83,1.17),.026,.025,'steel','X',24)
    box('Vise casting foot web',(-2.8,20.48,1.17),(.18,.14,.22),'teal',.016)
    # Bench frame uses plates, fillet seams, braces and visible attachment logic.
    for x in [-3.6,-2.85]:
        for y in [20.05,22.65]:
            box('Bench gusset',(x,y,.73),(.12,.11,.2),'darkteal',.003)
            bolt('Bench frame through bolt',(x+.069,y,.75),'X',.014)
    for y in [20.05,22.65]:beam('Bench knee tie',(-2.83,y,.63),(-3.17,y,.83),.018,'darkteal')
    # Scribed race identification, retainer pins, shallow machining grooves.
    for i in range(12):
        t=i*math.tau/12
        cyl('Bearing retainer rivet',(-3.22+.177*math.cos(t),21.188,1.28+.177*math.sin(t)),.006,.009,'yellow','Y',12,.001)
    ring('Race face machining line',(-3.22,21.198,1.28),.246,.244,.002,'dark')
    ring('Race bore machining line',(-3.22,21.188,1.28),.116,.114,.002,'dark')
    text('Bearing batch marking','T01  /  6208',(-3.3,21.188,1.473),.019,'ink')
    for x in [-3.46,-2.98]:bolt('Cradle foot bolt',(x,21.25,1.062),r=.014)
    # Forged table spanner: a tapered flat shank with twelve-sided sockets.
    for o in list(bpy.data.objects):
        if o.name.startswith('Maintenance spanner'):bpy.data.objects.remove(o,do_unlink=True)
    x,y,z=-2.95,21.55,1.008
    outline=[(-.026,-.15),(-.018,-.10),(-.013,.1),(-.026,.15),(.026,.15),(.013,.1),(.018,-.10),(.026,-.15)]
    N=len(outline);v=[(x+u,y+v,z+h) for h in [-.008,.008] for u,v in outline];f=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];mesh('Forged spanner shank',v,f,'steel',.002)
    sockets=[]
    for yy,rr in [(y-.15,.048),(y+.15,.043)]:
        o=ring('Twelve point ring socket',(0,0,0),rr,rr*.61,.018,'steel',segments=12);o.rotation_euler[0]=math.pi/2;o.location=(x,yy,z)
        sockets.append(o.name)
    anchor('table spanner',(x,y-.15,1.0),'Bench top',prop=sockets[0],members=['Forged spanner shank',sockets[1]])
    box('Spanner handle relief',(x,y,z+.009),(.012,.13,.001),'dark',.001)
    text('Spanner size stamp','19', (x-.009,y-.048,z+.011),.015,'ink','UP')
    # Actual filled-in shift notes; sparse information that explains the repair.
    text('Log measurements','02:10  T01-B\nVIB  4.2\nOIL  46\nRECHECK  03:00',(-3.1,22.35,1.029),.022,'ink','UP')
    cyl('Grease pencil',(-3.13,22.40,1.033),.007,.22,'yellow','Y',12)
    cyl('Pencil graphite',(-3.13,22.285,1.033),.005,.014,'ink','Y',12)
    anchor('grease pencil',(-3.13,22.4,1.026),'Shift log paper',prop='Grease pencil',members=['Pencil graphite'])
    # Cloth hem follows the existing cloth edge and deliberately differs from metal.
    for y in [21.82,22.12]:
        points=[(-3.23+i*.04,y,1.011+abs(.014*math.sin((i*.04+.02)*24+(y-21.8)*7)+.006*math.cos((y-21.8)*48))) for i in range(11)]
        a.pipe('Cotton stitched hem',points,.0008,'cloth')
    text('Oil stand grade','ISO 46',(-3.075,18.443,1.02),.07,'white')
    # Localized tank chips and latch: restraint at actual contact edges.
    for z in [.77,1.27]:
        mesh('Oil tank contact chip',[(-3.1,18.49,z),(-3.045,18.456,z+.02),(-3.025,18.46,z+.007),(-3.065,18.465,z-.009)],[(0,1,2,3)],'worn')
    cyl('Tank pump compression gland',(-2.95,18.75,1.49),.045,.052,'steel',verts=6)
    for y in [18.48,19.02]:bolt('Tank cradle fixing',(-3.21,y,.8),r=.015)
    # Wall joint, repair patch and mounting screws supply authored construction, not noise.
    for y in [19.75,22.9]:box('Wall casting joint',(-3.998,y,3.6),(.004,.008,5.2),'concrete',0)
    for y in [20.08,22.18]:bolt('Tool rail fastener',(-3.913,y,1.8),'X',.012)
    for y in [22.74,22.96]:
        for z in [1.21,1.43]:bolt('Junction lid screw',(-3.773,y,z),'X',.008)
    box('Junction lid seam',(-3.77,22.85,1.32),(.006,.26,.29),'darkteal',.012)
    box('Junction face',(-3.763,22.85,1.32),(.011,.246,.276),'cream',.008)
    # Door hydraulic rail hardware and maintenance edge wear.
    n='D02 electrical'
    for x in [-1.32,1.32]:
        for z in [.32,1.2,2.48]:bolt('Door reveal anchor',(x,23.672,z),'Y',.018)
    box('Door lock strike',(1.22,23.77,1.2),(.032,.12,.24),'steel',.005)
    for x in [-2.42,2.42]:
        mesh('Door kickplate scuff',[(x,23.845,.3),(x+.12,23.845,.32),(x+.16,23.845,.309),(x+.02,23.845,.283)],[(0,1,2,3)],'dark')
    # Dark rubber traces explain the bench's busy standing area.
    for i in range(7):
        xx=-2.28+random.uniform(-.13,.13);yy=20.15+random.random()*2.35
        o=box('Localized sole scuff',(xx,yy,.005),(.019,random.uniform(.08,.21),.001),'concrete',0);o.rotation_euler[2]=random.uniform(-.9,.9)
