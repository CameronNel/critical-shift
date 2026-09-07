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
    # Stronger cast/forged support silhouette and visible under-bench tool storage.
    for o in list(bpy.data.objects):
        if o.name.startswith('Cradle cheek'):bpy.data.objects.remove(o,do_unlink=True)
    cx,cy,cz=-3.22,21.25,1.28
    for yy in [21.13,21.33]:
        profile=[(cx-.3,1.05),(cx+.3,1.05),(cx+.3,1.11),(cx+.255,1.2),(cx+.195,1.17),(cx+.13,1.08),(cx-.13,1.08),(cx-.195,1.17),(cx-.255,1.2),(cx-.3,1.11)]
        a.extrude_profile('Contoured bearing saddle',profile,yy-.02,yy+.02,'darkteal',.003)
    for x in [cx-.25,cx+.25]:
        beam('Saddle folded return',(x,21.1,1.075),(x,21.36,1.075),.018,'darkteal')
    # Tank stand is open formed-angle construction, with real pump fittings.
    for o in list(bpy.data.objects):
        if o.name.startswith('Oil stand leg'):bpy.data.objects.remove(o,do_unlink=True)
    for x in [-3.2,-2.7]:
        for y in [18.51,18.99]:
            box('Oil frame flange',(x,y,.4),(.05,.027,.67),'darkteal',.002)
            box('Oil frame web',(x+.012,y+.012,.4),(.026,.05,.67),'darkteal',.002)
    box('Tank support saddle',(-2.95,18.75,.67),(.56,.54,.06),'darkteal',.005)
    beam('Oil stand diagonal',(-3.2,18.99,.14),(-2.7,18.99,.63),.013,'darkteal')
    for z in [.78,1.22]:
        a.ring('Rolled tank band',(0,0,0),.306,.296,.035,'steel').rotation_euler[0]=0
        o=bpy.context.scene.objects.get('Rolled tank band' if z==.78 else 'Rolled tank band.001');o.rotation_euler[0]=math.pi/2;o.location=(-2.95,18.75,z)
    for i in range(6):
        ang=i*math.tau/6;bolt('Reservoir lid stud',(-2.95+.26*math.cos(ang),18.75+.26*math.sin(ang),1.355),r=.014)
    # A sight glass in a protected frame on the front of the tank.
    for x in [-3.04,-2.91]:box('Sight gauge guard',(x,18.431,1.01),(.014,.026,.28),'darkteal',.002)
    box('Sight gauge recess',(-2.975,18.437,1.01),(.11,.025,.26),'dark',.005)
    box('Amber oil sightglass',(-2.975,18.42,1.00),(.035,.013,.18),'yellow',.004)
    for z in [.89,1.13]:box('Sight gauge end',(-2.975,18.415,z),(.12,.05,.04),'steel',.003)
    for z in [.94,1.02,1.10]:box('Oil sight index',(-2.93,18.402,z),(.025,.005,.002),'white',0)
    cyl('Outlet hex union',(-2.64,18.75,1.28),.045,.1,'steel','X',6)
    # Old repair case rests on the rack; lid lip, hinges, corners and recessed handle.
    case=box('Bearing toolcase body',(-3.21,21.4,.40),(.66,.86,.26),'teal',.02)
    for z in [.3,.51]:box('Toolcase folded perimeter',(-3.21,21.4,z),(.68,.88,.025),'darkteal',.005)
    for y in [21.05,21.75]:
        box('Case draw latch',(-2.864,y,.455),(.026,.075,.11),'steel',.008)
        box('Case latch catch',(-2.862,y,.51),(.03,.085,.035),'dark',.003)
    box('Case handle inset',(-2.871,21.4,.405),(.018,.3,.1),'dark',.009)
    a.pipe('Case bail handle',[(-2.85,21.29,.43),(-2.81,21.29,.385),(-2.81,21.51,.385),(-2.85,21.51,.43)],.013,'rubber')
    for y in [21.03,21.77]:box('Case reinforced corner',(-2.871,y,.34),(.027,.075,.1),'dark',.005)
    anchor('toolcase',(-3.21,21.52,.27),'Open lower shelf.004',prop=case.name)
    # Grubby cup base and imperfect, short material scuffs at heavy contact corners.
    torus('Mug base enamel bead',(-3.48,22.23,1.013),.067,.006,'darkteal')
    text('Mug hand marked initial','C',(-3.505,22.155,1.05),.04,'darkteal')
    for name in ['Bench front edge angle','Vise casting foot web','Oil stand feet','D02 electrical parked leaf']:
        ob=bpy.data.objects.get(name)
        if ob:ob['localized_wear']='selected hand/tool contact edge accents'
    # Paper now records an actual maintenance task and is fixed with two strips of tape.
    for y in [19.22,19.58]:box('Chart masking tape',(-3.984,y,1.965),(.012,.07,.10),'cream',.001)
    text('Service chart procedure','ISOLATE  /  LOCK\nCHECK OIL LEVEL\nRECORD VIBRATION\n\nB1   INSPECTED 02:10',(-3.983,19.18,1.63),.029,'ink','E')
    # The conduit continues to its socket: no loose wire tail below the junction.
    conduit=bpy.data.objects['Bench electrical conduit'];conduit.data.splines[0].bezier_points[-1].co.z=1.485
    # Readable reveal depth and a physically local door-light pool.
    for y in [24.35,24.85]:
        box('Door return construction seam',(-1.198,y,1.4),(.006,.009,2.68),'concrete',0)
        box('Threshold tile seam',(0,y,.002),(2.4,.012,.003),'dark',0)
    box('Return wall bumper',(-1.17,24.6,.78),(.06,1.16,.14),'darkteal',.004)
    for y in [24.16,25.04]:bolt('Return bumper anchor',(-1.136,y,.78),'X',.015)
    # Restrict secondary fill; the work light and exit practical lead the slice.
    for ob in bpy.context.scene.objects:
        if ob.type=='LIGHT':
            if ob.name.startswith('Practical pool'):ob.data.energy=170
            if ob.name.startswith('Clerestory broad fill'):ob.data.energy=260
            if ob.name.startswith('Bench fluorescent pool'):ob.data.energy=135;ob.data.color=(1,.84,.61)
    a.light('Door downlight pool',(0,23.48,3.13),(0,23.4,.2),90,(1,.81,.54),.45)
    box('Door downlight body',(0,23.52,3.18),(.5,.18,.15),'darkteal',.008)
    box('Door downlight lens',(0,23.5,3.099),(.4,.12,.012),'lamp',.003)
    # Small manufactured variations preserve broad color fields.
    for key,rough,metal in [('teal',.59,.05),('darkteal',.64,.28)]:
        bs=a.M[key].node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
