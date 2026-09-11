"""Original Cooling Plant construction vocabulary. Metres, Z up. No imports."""
import bpy, math, random
from mathutils import Vector
from math import sin, cos, pi

MAT={}; CONTACTS=[]; ASSEMBLIES=[]
def material(name,color,rough=.6,metal=0,variation=.035,bump=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if variation:
        tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=2.4;tex.inputs['Detail'].default_value=2
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[1].position=.82
        ramp.color_ramp.elements[0].color=(*(max(0,c-variation) for c in color),1)
        ramp.color_ramp.elements[1].color=(*(min(1,c+variation) for c in color),1)
        m.node_tree.links.new(tex.outputs['Fac'],ramp.inputs[0]);m.node_tree.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
        rr=n.new('ShaderNodeMapRange');rr.inputs['From Min'].default_value=0;rr.inputs['From Max'].default_value=1
        rr.inputs['To Min'].default_value=max(0,rough-.07);rr.inputs['To Max'].default_value=min(1,rough+.07)
        m.node_tree.links.new(tex.outputs['Fac'],rr.inputs[0]);m.node_tree.links.new(rr.outputs[0],p.inputs['Roughness'])
    if bump:
        tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=115;tex.inputs['Detail'].default_value=2
        b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.19;b.inputs['Distance'].default_value=bump
        m.node_tree.links.new(tex.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs[0],p.inputs['Normal'])
    MAT[name]=m;return m

def palette():
    material('mineral',(0.34,.319,.26),.88,variation=.025,bump=.004)
    material('floor',(.135,.132,.125),.86,variation=.028,bump=.003)
    material('patch',(.345,.352,.327),.85,variation=.012,bump=.002)
    # Legacy material keys retained for reproducibility; user-directed oxide/ivory palette.
    material('teal',(.25,.095,.042),.68,.12,.008,.0006)
    material('teal_light',(.40,.19,.09),.70,.10,.010,.0006)
    material('steel',(.15,.155,.16),.50,.75,.010)
    material('edge',(.23,.23,.22),.43,.85,.011)
    material('dark',(.042,.043,.047),.68,.35,.006)
    material('rubber',(.025,.028,.025),.91,0,.006,.0008)
    material('cream',(.39,.385,.32),.66,.18,.017,.0008)
    material('yellow',(.42,.25,.028),.58,.30,.012)
    material('orange',(.55,.205,.065),.61,.15,.014)
    material('red',(.36,.044,.025),.53,.15,.008)
    material('paper',(.70,.66,.51),.95,0,.008)
    material('ink',(.035,.049,.043),.88,0,0)
    material('cloth',(.09,.118,.087),.97,0,.012,.002)
    MAT['cloth'].node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.38
    material('cloth_thread',(.17,.185,.137),1,0,.005)
    material('teal_worn',(.32,.145,.07),.78,.12,.008,.0006)
    material('blue',(.23,.225,.22),.65,.18,.010)
    material('leak',(.23,.255,.225),.39,.03,.005)
    material('wood',(.19,.115,.049),.78,0,.009,.001)
    material('wood_wear',(.25,.16,.075),.88,0,0)
    material('glass',(.29,.38,.35),.14,0,0)
    MAT['glass'].node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.84
    material('lamp',(.82,.85,.77),.32,0,0)
    p=MAT['lamp'].node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.95,.87,.73,1);p.inputs['Emission Strength'].default_value=3
    for key,label in [('teal','oxide paint'),('teal_light','oxide paint light'),('teal_worn','oxide contact wear'),('blue','neutral service steel')]:MAT[key].name=label

def finish(o,name,mat,bevel=0,smooth=False):
    o.name=name
    if mat:o.data.materials.append(MAT[mat] if isinstance(mat,str) else mat)
    if smooth and o.type=='MESH':
        for p in o.data.polygons:p.use_smooth=True
    if bevel:
        b=o.modifiers.new('manufactured edge','BEVEL');b.width=bevel;b.segments=2
        b=o.modifiers.new('weighted normals','WEIGHTED_NORMAL');b.keep_sharp=True;b.weight=35
    o['construction']='integral assembly component'
    return o
def box(name,loc,dim,mat,bevel=.012):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,mat,bevel)
def cyl(name,loc,r,depth,mat,axis=(0,0,1),verts=48,bevel=.007):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc);o=bpy.context.object
    o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler()
    return finish(o,name,mat,bevel,True)
def sphere(name,loc,dim,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,radius=1,location=loc);o=bpy.context.object;o.scale=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,name,mat,0,True)
def torus(name,loc,r,minor,mat,axis=(0,0,1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=minor,major_segments=64,minor_segments=10,location=loc)
    o=bpy.context.object;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();return finish(o,name,mat,0,True)
def annulus(name,p,outer,inner,depth,mat,axis=(0,0,1)):
    p=Vector(p);u=Vector(axis).normalized();a=u.orthogonal().normalized();b=u.cross(a).normalized();n=64
    vs=[p+u*h+(a*cos(i*2*pi/n)+b*sin(i*2*pi/n))*r for h,r in [(-depth/2,outer),(depth/2,outer),(-depth/2,inner),(depth/2,inner)] for i in range(n)]
    fs=[]
    for i in range(n):
        j=(i+1)%n;fs.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(n+i,n+j,3*n+j,3*n+i),(i,2*n+i,2*n+j,j)])
    return mesh(name,vs,fs,mat,.002,True)
def rod(name,a,b,r,mat,verts=24):
    a,b=Vector(a),Vector(b);return cyl(name,(a+b)/2,r,(b-a).length,mat,b-a,verts,.003)
def mesh(name,verts,faces,mat,bevel=0,smooth=False):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
    return finish(o,name,mat,bevel,smooth)
def pipe(name,points,r,mat,bend=.22):
    # Exact straight ends with authored circular fillets at every elbow.
    pts=[Vector(p) for p in points];samples=[pts[0]]
    for i in range(1,len(pts)-1):
        a,b,c=pts[i-1],pts[i],pts[i+1];u=(a-b).normalized();v=(c-b).normalized()
        d=min(bend,(a-b).length*.35,(c-b).length*.35)
        if abs(u.dot(v))>.999:samples.append(b);continue
        p,q=b+u*d,b+v*d;center=b+(u+v)*d
        samples.append(p)
        # quadratic fillet for smooth purpose-routed manufactured elbows
        for k in range(1,9):
            t=k/8;samples.append((1-t)**2*p+2*(1-t)*t*b+t*t*q)
    samples.append(pts[-1])
    cr=bpy.data.curves.new(name,'CURVE');cr.dimensions='3D';cr.resolution_u=1;cr.bevel_depth=r;cr.bevel_resolution=4
    sp=cr.splines.new('POLY');sp.points.add(len(samples)-1)
    for p,co in zip(sp.points,samples):p.co=(*co,1)
    ob=bpy.data.objects.new(name,cr);bpy.context.collection.objects.link(ob);finish(ob,name,mat)
    ob['start_m']=list(points[0]);ob['end_m']=list(points[-1]);return ob
def text(name,body,loc,size,mat='paper',rot=(pi/2,0,0),align='CENTER'):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x=align;cu.extrude=.0003;cu.space_character=1.12
    ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=rot;return finish(ob,name,mat)
def flange(name,loc,r,axis=(0,1,0),mat='cream',bolts=10,pitch=.81):
    u=Vector(axis).normalized();a=u.orthogonal().normalized();b=u.cross(a).normalized();p=Vector(loc)
    cyl(name+' cast flange',p,r,.10,mat,u)
    cyl(name+' gasket',p+u*.055,r*.93,.018,'rubber',u)
    cyl(name+' mating flange',p+u*.11,r,.09,mat,u)
    for i in range(bolts):
        q=p+u*.168+(a*cos(2*pi*i/bolts)+b*sin(2*pi*i/bolts))*r*pitch
        cyl(name+' washer',q,.055 if r>.5 else .036,.009,'edge',u,20,.001)
        cyl(name+' hex nut',q+u*.015,.044 if r>.5 else .027,.032,'dark',u,6,.002)
def gauge(name,p,r=.13,axis=(0,-1,0)):
    p=Vector(p);u=Vector(axis);cyl(name+' bezel',p,r,.07,'edge',u)
    face=p+u*.041;cyl(name+' ivory dial',face,r*.87,.008,'paper',u)
    # Gauge axis for the wall-facing -Y standard, with separate needle pivot.
    if tuple(axis)==(0,-1,0):
        for i in range(11):
            a=pi*.15+pi*1.7*i/10
            aa=face+Vector((cos(a)*r*.65,-.007,sin(a)*r*.65));bb=face+Vector((cos(a)*r*.78,-.007,sin(a)*r*.78))
            rod(name+' tick',aa,bb,.003,'ink',8)
        rod(name+' needle',face+Vector((0,-.012,0)),face+Vector((r*.34,-.012,r*.46)),.006,'ink',10)
        cyl(name+' pivot',face+u*.014,.014,.018,'dark',u,16,.001)
        text(name+' scale','bar',(face.x,face.y-.016,face.z-r*.48),r*.22,'ink')
    return p
def wheel(name,p,r=.23,axis=(0,-1,0),mat='yellow'):
    p=Vector(p);u=Vector(axis).normalized();a=u.orthogonal().normalized();b=u.cross(a).normalized()
    ob=torus(name+' rim',p,r,.021,mat,u)
    for k in range(3):rod(name+' spoke',p,p+(a*cos(k*2*pi/3)+b*sin(k*2*pi/3))*r,.016,mat)
    cyl(name+' hub',p,.049,.085,'edge',u,24);ob['interaction']='manual valve rotate around shaft'
    return ob
def group(name,before,support=None,anchors=None,direction=(0,0,-1)):
    root=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(root);root['assembly']=True
    children=[o for o in bpy.context.scene.objects if o.name not in before and o!=root and o.parent is None and not o.get('assembly')]
    for ob in children:ob.parent=root
    ASSEMBLIES.append(root.name)
    if support:
        root['support_target']=support;root['support_anchors']=anchors;root['support_direction']=list(direction);root['max_gap_m']=.005;root['max_penetration_m']=.002;root['support_angle_tolerance_deg']=12
        CONTACTS.append(dict(object=root.name,target=support,anchors=anchors,direction=list(direction)))
    return root
def before():return set(o.name for o in bpy.context.scene.objects)
def architecture(start):
    for o in bpy.context.scene.objects:
        if o.name not in start and o.parent is None and not o.get('assembly'):o['validation_role']='architecture'
def area(name,loc,target,power,color,size=2,shape='DISK',size_y=None):
    ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.color=color;ld.shape=shape;ld.size=size
    if size_y and shape=='RECTANGLE':ld.size_y=size_y
    ob=bpy.data.objects.new(name,ld);bpy.context.collection.objects.link(ob);ob.location=loc
    ob.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();return ob
def camera(name,loc,target,lens=30):
    cd=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,cd);bpy.context.collection.objects.link(ob);ob.location=loc
    ob.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();cd.lens=lens;cd.clip_start=.06;cd.clip_end=120
    return ob

def pump(name,y):
    start=before();x=-3.45;z=.91
    for yy in (y-.69,y+.69):
        box(name+' anchor rail',(x,yy,.135),(3.00,.14,.27),'dark',.008)
    box(name+' drip tray',(x,y,.29),(3.00,1.65,.05),'steel',.006)
    for xx in (-4.68,-2.22):
        for yy in (y-.62,y+.62):cyl(name+' concrete anchor',(xx,yy,.04),.073,.08,'edge',verts=6,bevel=.003)
    # Cast volute: non-concentric rising spiral silhouette extruded along shaft X.
    vs=[];n=80;cx=-4.10
    for xx in (cx-.19,cx+.19):
        for i in range(n):
            t=i/(n-1);a=-pi/2+2*pi*t;r=.39+.17*t
            vs.append((xx,y+cos(a)*r,z+sin(a)*r))
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh(name+' spiral volute casting',vs,faces,'teal',.025,True)
    cyl(name+' casing cover',(cx+.22,y,z),.37,.075,'teal_light',(1,0,0),64,.017)
    for i in range(10):
        a=2*pi*i/10;cyl(name+' cover stud',(cx+.271,y+cos(a)*.315,z+sin(a)*.315),.027,.032,'edge',(1,0,0),6,.002)
    for xx,zz in ((cx,.48),(-2.75,.43)):
        for yy in (y-.36,y+.36):box(name+' cast foot',(xx,yy,zz),(.35,.18,(zz-.31)*2),'teal',.018)
    # Mechanical seal and exposed metal shaft; removable open-slot guard.
    cyl(name+' seal housing',(-3.76,y,z),.175,.34,'dark',(1,0,0),48,.014)
    cyl(name+' coupling shaft',(-3.45,y,z),.071,.42,'edge',(1,0,0),40,.006)
    for xx in (-3.56,-3.32):cyl(name+' jaw coupling', (xx,y,z),.12,.095,'edge',(1,0,0),36,.012)
    cyl(name+' elastomer spider',(-3.44,y,z),.113,.10,'rubber',(1,0,0),36,.009)
    for i in range(13):
        a=pi*i/12
        rod(name+' ventilated coupling guard',(-3.65,y+cos(a)*.24,z+sin(a)*.24),(-3.13,y+cos(a)*.24,z+sin(a)*.24),.007,'yellow',12)
    for xx in (-3.64,-3.14):
        arc=[(xx,y+cos(pi*i/30)*.24,z+sin(pi*i/30)*.24) for i in range(31)];pipe(name+' guard rolled end',arc,.010,'yellow',.03)
    cyl(name+' induction motor',(-2.65,y,z),.32,.88,'teal',(1,0,0),64,.026)
    for i in range(24):
        a=i*2*pi/24
        # Longitudinal cooling fins with actual fin edge profile.
        ob=box(name+' motor cast fin',(-2.64,y+cos(a)*.328,z+sin(a)*.328),(.70,.014,.068),'teal',.0025)
        ob.rotation_euler.x=a-pi/2
    cyl(name+' end bell',(-2.14,y,z),.335,.16,'teal',(1,0,0),64,.015)
    cyl(name+' fan shadow',(-2.049,y,z),.274,.012,'dark',(1,0,0),48,.002)
    for i in range(-6,7):
        zz=i*.036;d=math.sqrt(.245**2-zz**2);rod(name+' fan grille',(-2.035,y-d,z+zz),(-2.035,y+d,z+zz),.006,'steel',10)
    for yy in (-.14,0,.14):rod(name+' vertical grille stay',(-2.044,y+yy,z-.21),(-2.044,y+yy,z+.21),.005,'dark',10)
    torus(name+' fan lip',(-2.032,y,z),.278,.016,'edge',(1,0,0))
    box(name+' terminal gasket',(-2.65,y,1.25),(.35,.34,.09),'rubber',.008)
    box(name+' terminal enclosure',(-2.65,y,1.34),(.38,.37,.14),'teal',.018)
    box(name+' terminal lid seam',(-2.65,y,1.404),(.383,.373,.008),'dark',.002)
    box(name+' separate pressed terminal lid',(-2.65,y,1.412),(.382,.372,.014),'teal_light',.005)
    for yy in (y-.125,y+.125):cyl(name+' terminal screw',(-2.52,yy,1.418),.016,.01,'edge',verts=6,bevel=.001)
    pipe(name+' armored power tail',[(-2.74,y+.18,1.3),(-2.74,y+.52,1.3),(-3.25,y+.52,.46),(-4.9,y+.52,.46)],.025,'rubber',.16)
    # Axial inlet and vertical discharge are real hydraulic interfaces.
    cyl(name+' suction neck',(-4.48,y,z),.155,.40,'cream',(1,0,0),48,.012)
    flange(name+' suction union',(-4.69,y,z),.23,(1,0,0))
    pipe(name+' discharge neck',[(-4.1,y-.34,1.29),(-4.1,y-.34,1.88)],.135,'cream')
    flange(name+' discharge union',(-4.1,y-.34,1.63),.21,(0,0,1))
    pipe(name+' pressure tapping',[(-4.1,y-.34,1.85),(-3.84,y-.34,1.85),(-3.84,y-.64,1.85)],.023,'edge',.07)
    gauge(name+' outlet gauge',(-3.84,y-.68,1.85),.112)
    box(name+' nameplate',(-2.65,y-.324,.95),(.38,.012,.13),'dark',.005)
    text(name+' rating',name+' / 18 kW',(-2.65,y-.332,.92),.039)
    # Purposeful touch wear: short cast flange scuffs, not universal edge noise.
    # Hand-authored chips at handled cover edges and the terminal lid corner.
    for dx,dy,sz in [(-.17,-.164,.025),(-.143,-.164,.012),(-.10,-.167,.019),(.13,-.16,.009)]:
        vs=[(-2.65+dx,y+dy,1.420),(-2.65+dx+sz,y+dy+.003,1.420),(-2.65+dx+sz*.6,y+dy+.008,1.420),(-2.65+dx-.003,y+dy+.005,1.420)]
        mesh(name+' terminal edge paint loss',vs,[(0,1,2,3)],'edge')
    # Cast rim wear follows the machined circular face rather than floating strips.
    for j in range(7):
        a=.50+j*.019;r=.366;pts=[(-3.841,y+cos(a+t)*rr,z+sin(a+t)*rr) for t,rr in [(0,r),(.018,r),(.015,r-.014),(.003,r-.009)]]
        mesh(name+' local worn cover rim',pts,[(0,1,2,3)],'edge')
    # Packed bearing gland, split seam and foot fasteners complete a maintainable assembly.
    annulus(name+' seal collar',(-3.66,y,z),.18,.077,.048,'edge',(1,0,0))
    for xx in (-4.10,-2.75):
        for yy in (y-.36,y+.36):cyl(name+' foot hold-down',(xx,yy,.565 if xx==-4.10 else .525),.029,.032,'edge',verts=6,bevel=.002)
    return group(name,start,'Floor',[[x,y-.69,0],[x,y+.69,0]])

def wrench(name,p,angle=0):
    x,y,z=p;verts2=[(-.027,-.19),(.027,-.19),(.027,.12),(.073,.16),(.073,.235),(.034,.235),(.034,.19),(-.034,.19),(-.034,.235),(-.073,.235),(-.073,.16),(-.027,.12)]
    vs=[(x+a*cos(angle)-b*sin(angle),y+a*sin(angle)+b*cos(angle),z+h) for h in (0,.009) for a,b in verts2];n=len(verts2)
    ob=mesh(name,vs,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'edge',.002)
    a=box(name+' forged handle inset',(x+.016*sin(angle),y-.016*cos(angle),z+.0095),(.014,.22,.001),'steel',.001);a.rotation_euler.z=angle
    text(name+' stamped size','24',(x-.155*sin(angle),y+.155*cos(angle),z+.0105),.019,'ink',(0,0,angle))
    return ob
def cloth(name,p,w=.39,d=.32):
    x,y,z=p;vs=[];nx=18;ny=16
    for j in range(ny+1):
        for i in range(nx+1):
            u=i/nx;v=j/ny;h=max(0,.018*sin(u*3*pi+v*1.2)+.009*sin(v*2*pi))
            vs.append((x+(u-.5)*w+.005*sin(v*9+u*4),y+(v-.5)*d+.004*sin(u*8),z+h))
    faces=[(j*(nx+1)+i,j*(nx+1)+i+1,(j+1)*(nx+1)+i+1,(j+1)*(nx+1)+i) for j in range(ny) for i in range(nx)]
    ob=mesh(name,vs,faces,'cloth',0,True);so=ob.modifiers.new('cloth hem thickness','SOLIDIFY');so.thickness=.003;so.offset=1
    for j in range(11):
        yy=y-d*.5+.028+j*d*.075
        # Loose hem stitches remain short and fine at human scale.
        rod(name+' frayed hem',(x-w*.5+.002,yy,z+.003),(x-w*.5-.008,yy+.003,z+.001),.0009,'cloth_thread',6)
    return ob
def cart(name,x,y):
    start=before()
    for xx in (x-.35,x+.35):
        for yy in (y-.23,y+.23):
            cyl(name+' rubber caster',(xx,yy,.09),.09,.047,'rubber',(1,0,0),32,.007)
            box(name+' caster fork',(xx,yy,.175),(.062,.1,.075),'edge',.008)
            box(name+' folded upright',(xx,yy,.53),(.036,.036,.69),'dark',.004)
    for z in (.26,.87):
        box(name+' tray',(x,y,z),(.83,.60,.026),'teal',.009)
        for xx in (x-.406,x+.406):box(name+' tray return',(xx,y,z+.037),(.017,.6,.065),'teal',.004)
        for yy in (y-.292,y+.292):box(name+' tray lip',(x,yy,z+.027),(.83,.017,.045),'teal',.004)
    pipe(name+' handle',[(x+.38,y-.23,.89),(x+.55,y-.23,1.03),(x+.55,y+.23,1.03),(x+.38,y+.23,.89)],.018,'edge',.05)
    group(name,start,'Floor',[[x-.35,y-.23,0],[x+.35,y+.23,0]])
    start=before();cloth(name+' wiping cloth',(x-.17,y-.06,.883));group(name+' cloth prop',start,name+' tray.001',[[x-.17,y-.06,.883]])
    start=before();wrench(name+' open jaw spanner',(x+.19,y-.015,.883),.3);group(name+' spanner prop',start,name+' tray.001',[[x+.19,y-.015,.883]])
    start=before();torus(name+' replacement seal',(x-.12,y+.16,.907),.065,.024,'rubber');group(name+' seal prop',start,name+' tray.001',[[x-.185,y+.16,.883]])
    start=before()
    box(name+' parts bin bottom',(x-.10,y,.282),(.46,.34,.018),'paper',.002)
    for xx in (x-.323,x+.123):box(name+' carton folded side',(xx,y,.36),(.014,.34,.17),'paper',.002)
    for yy in (y-.163,y+.163):box(name+' carton end',(x-.1,yy,.36),(.46,.014,.17),'paper',.002)
    cyl(name+' spare bearing',(x-.09,y,.322),.091,.067,'edge',verts=40)
    cyl(name+' bearing dark bore',(x-.09,y,.357),.055,.002,'dark',verts=40,bevel=0)
    group(name+' bearing carton',start,name+' tray',[[x-.1,y,.273]])
