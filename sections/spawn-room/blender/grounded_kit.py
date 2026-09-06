"""Original metric facility kit. Front is -Y, Z up; no legacy scene imports."""
import bpy, math, random
from mathutils import Vector
from math import sin, cos, pi
STAGE=3
M={}

def collection(name):
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c

def finish(o,name,mat=None):
    o.name=name
    if mat: o.data.materials.append(M['grey'] if STAGE==1 else M[mat])
    return o

def mesh(name,v,f,mat,smooth=False):
    d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update()
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);finish(o,name,mat)
    for p in d.polygons:p.use_smooth=smooth
    return o

def bevel(o,w=.004,n=2):
    if w:
        m=o.modifiers.new('Manufactured edge','BEVEL');m.width=w;m.segments=n
        m=o.modifiers.new('Area weighted normals','WEIGHTED_NORMAL');m.keep_sharp=True
    return o

def box(name,p,s,mat,edge=.003):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.scale=s
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(o,name,mat);return bevel(o,edge)

def tube(name,pts,r,mat,cyclic=False):
    d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=2;d.bevel_depth=r;d.bevel_resolution=3
    s=d.splines.new('POLY');s.points.add(len(pts)-1)
    for q,p in zip(s.points,pts):q.co=(*p,1)
    s.use_cyclic_u=cyclic
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);finish(o,name,mat);return o

def rod(name,a,b,r,mat,verts=24):
    a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=(b-a).length,location=(a+b)/2)
    o=bpy.context.object;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();finish(o,name,mat)
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    return bevel(o,.0015,2)

def lathe(name,profile,mat,n=48):
    v=[(r*cos(2*pi*j/n),r*sin(2*pi*j/n),z) for r,z in profile for j in range(n)]
    f=[(k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for k in range(len(profile)-1) for j in range(n)]
    return mesh(name,v,f,mat,True)

def outline(w,h,r,n=8):
    return [(cx+r*cos(a),cz+r*sin(a)) for cx,cz,t in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,pi/2),(-w/2+r,-h/2+r,pi),(w/2-r,-h/2+r,3*pi/2)] for a in [t+j*pi/2/n for j in range(n+1)]]

def panel(name,p,w,h,depth,r,mat):
    q=outline(w,h,r);N=len(q)
    v=[(p[0]+x,p[1]+y,p[2]+z) for y in [-depth/2,depth/2] for x,z in q]
    f=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)]
    return bevel(mesh(name,v,f,mat),.001,2)

def frame(name,p,w,h,b,depth,mat,r=.025):
    outer=outline(w,h,r);inner=outline(w-2*b,h-2*b,max(.002,r-b));N=len(outer)
    v=[(p[0]+x,p[1]+y,p[2]+z) for y in [-depth/2,depth/2] for pts in [outer,inner] for x,z in pts]
    f=[]
    for i in range(N):
        j=(i+1)%N
        f.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
    return bevel(mesh(name,v,f,mat),.002,2)

def label(name,body,p,size,mat='ink',rot=(pi/2,0,0),align='LEFT'):
    d=bpy.data.curves.new(name,'FONT');d.body=body;d.size=size;d.align_x=align;d.extrude=0
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=p;o.rotation_euler=rot;finish(o,name,mat);return o

def start(): return set(bpy.data.objects)
def group(name,before,p=(0,0,0),angle=0):
    parts=set(bpy.data.objects)-before
    o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o)
    for c in parts:
        if c.parent is None:c.parent=o
    o.location=p;o.rotation_euler.z=angle;return o

def support(o,target,direction,anchors,kind='FLOOR'):
    for c in ['CS_SUPPORT_REQUIRED','CS_'+kind+'_DRESSING']:
        collection(c).objects.link(o)
    o['cs_support_target']=target.name;o['cs_support_direction']=direction
    for i,p in enumerate(anchors):
        a=bpy.data.objects.new(o.name+'_contact_%02d'%i,None);bpy.context.collection.objects.link(a)
        a.parent=o;a.location=p;a['cs_support_anchor']=True;a.empty_display_size=.025

def material(name,colour,rough=.65,metal=0,variation=.08,bump=.001,scale=3):
    m=bpy.data.materials.new(name);m.diffuse_color=(*colour,1);m.use_nodes=True
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*colour,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if variation:
        t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=scale;t.inputs['Detail'].default_value=2
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.15;ramp.color_ramp.elements[1].position=.85
        ramp.color_ramp.elements[0].color=(*(v*(1-variation) for v in colour),1)
        ramp.color_ramp.elements[1].color=(*(min(1,v*(1+variation)) for v in colour),1)
        l.new(t.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
        r=n.new('ShaderNodeMapRange');r.inputs['To Min'].default_value=rough-.08;r.inputs['To Max'].default_value=min(1,rough+.07)
        l.new(t.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Roughness'])
        if bump:
            b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.22;b.inputs['Distance'].default_value=bump
            l.new(t.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
    M[name]=m;return m

def materials(stage=3):
    global STAGE;STAGE=stage;M.clear()
    specs=[('grey',(.32,.32,.32),.78,0,0,0,1),('wall',(.62,.59,.51),.86,0,.10,.008,1.8),
      ('dado',(.20,.27,.25),.79,0,.10,.003,3),('paint',(.17,.25,.23),.60,.08,.10,.002,4),
      ('pale',(.56,.56,.49),.65,.05,.08,.001,3),('steel',(.22,.25,.25),.40,.85,.10,.0006,5),
      ('darksteel',(.065,.078,.076),.60,.55,.1,.001,4),('rubber',(.028,.033,.032),.9,0,.18,.001,8),
      ('cloth',(.35,.235,.08),.91,0,.13,.002,5),('seam',(.26,.165,.047),.93,0,.08,.0004,9),
      ('yellow',(.64,.43,.10),.65,.1,.1,.002,4),('plastic',(.36,.38,.33),.48,0,.06,.0005,4),
      ('wood',(.29,.19,.10),.66,0,.14,.001,4),('paper',(.80,.75,.62),.91,0,.03,.0003,6),
      ('ink',(.028,.042,.039),.8,0,0,0,1),('red',(.44,.075,.045),.68,0,.1,.001,4),
      ('blue',(.12,.24,.30),.65,.08,.08,.001,4),('vinyl',(.23,.30,.26),.81,0,.10,.002,5),
      ('wear',(.32,.34,.30),.75,.15,.1,.001,3),('coffee',(.037,.017,.009),.25,0,0,0,1)]
    for args in specs:material(*args)
    M['cloth'].node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.19
    M['cloth'].node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.14
    # Family-specific micro response: cloth nap, directional laminate, ceramic enamel.
    n=M['cloth'].node_tree.nodes;l=M['cloth'].node_tree.links;p=n.get('Principled BSDF')
    nap=n.new('ShaderNodeTexNoise');nap.inputs['Scale'].default_value=190;nap.inputs['Detail'].default_value=2
    micro=n.new('ShaderNodeBump');micro.inputs['Strength'].default_value=.20;micro.inputs['Distance'].default_value=.0006
    oldnormal=[q.from_socket for q in l if q.to_socket==p.inputs['Normal']]
    if oldnormal:l.new(oldnormal[0],micro.inputs['Normal'])
    l.new(nap.outputs['Fac'],micro.inputs['Height']);l.new(micro.outputs[0],p.inputs['Normal'])
    n=M['wood'].node_tree.nodes;l=M['wood'].node_tree.links
    coord=n.new('ShaderNodeTexCoord');stretch=n.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=(1.3,26,5)
    l.new(coord.outputs['Generated'],stretch.inputs[0])
    for noise in [q for q in n if q.type=='TEX_NOISE']:l.new(stretch.outputs[0],noise.inputs['Vector'])
    material('enamel',(.50,.51,.43),.26,.03,.025,.00015,6)
    for i in range(5):material('floor%d'%i,tuple(v*(.96+i*.02) for v in (.19,.215,.20)),.76,0,.10,.002,3)
    m=material('glass',(.76,.83,.81),.13,0,.025,.0001,2);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=.93;p.inputs['IOR'].default_value=1.46
    for link in list(m.node_tree.links):
        if link.to_socket==p.inputs['Roughness']:m.node_tree.links.remove(link)
    p.inputs['Roughness'].default_value=.035;p.inputs['Transmission Weight'].default_value=1
    m=material('visor',(.016,.025,.023),.18,0,.045,.0001,2)
    m.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.28
    for name,c,power in [('lamp',(1,.88,.67),5),('ready',(.20,.64,.31),2),('screen',(.12,.27,.25),.3)]:
        m=material(name,c,.5,0,0,0,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=power

def floor(name,x0,x1,y0,y1):
    o=box(name,((x0+x1)/2,(y0+y1)/2,-.085),(x1-x0,y1-y0,.17),'floor2',0)
    # Broad joints on the actual surface: single support mesh, tiled material and shallow routed seams.
    for x in range(math.ceil(x0),math.floor(x1)):
        box(name+'_jointX', (x,(y0+y1)/2,.0002),(.005,y1-y0,.0004),'darksteel',0)
    for y in range(math.ceil(y0),math.floor(y1)):
        box(name+'_jointY', ((x0+x1)/2,y,.0002),(x1-x0,.005,.0004),'darksteel',0)
    return o

def wall(name,x0,x1,y,h=3.4):
    o=box(name,((x0+x1)/2,y+.08,h/2),(x1-x0,.16,h),'wall',.001)
    box(name+'_washable_dado',((x0+x1)/2,y-.004,.59),(x1-x0,.008,1.18),'dado',.001)
    box(name+'_coved_skirt',((x0+x1)/2,y-.019,.08),(x1-x0,.038,.16),'darksteel',.008)
    box(name+'_dado_cap',((x0+x1)/2,y-.008,1.186),(x1-x0,.016,.012),'pale',.002)
    return o

def door(name,p=(0,0,0),angle=0,w=1.3,h=2.2,opened=0,heavy=False,hinge_right=False):
    b=start();colour='yellow' if heavy else 'paint'
    for s in [-1,1]:
        box(name+'_jamb',(s*(w/2+.045),.035,h/2),(.09,.25,h+.02),'darksteel',.005)
        box(name+'_rebate',(s*(w/2+.008),-.028,h/2),(.024,.08,h),'pale',.002)
        box(name+'_gasket',(s*(w/2-.003),.012,h/2),(.012,.024,h),'rubber',.002)
    box(name+'_head',(0,.035,h+.05),(w+.18,.25,.1),'darksteel',.004)
    box(name+'_head_seal',(0,.012,h-.004),(w,.023,.012),'rubber',.002)
    box(name+'_threshold',(0,0,.006),(w,.25,.012),'steel',.002)
    leafbefore=start();lw=w-.032;lh=h-.025;wy=.035
    # Specific leaf construction with a real aperture, four continuous steel fields.
    vx=-.12;vw=.30;vz=1.52;vh=.61
    # Continuous planar sheet around the aperture: no false seams across the leaf.
    outer=[(-lw/2,.015),(lw/2,.015),(lw/2,lh),(-lw/2,lh)]
    inner=[(vx-vw/2,vz-vh/2),(vx+vw/2,vz-vh/2),(vx+vw/2,vz+vh/2),(vx-vw/2,vz+vh/2)]
    verts=[(x,y,z) for y in [wy-.029,wy+.029] for loop in [outer,inner] for x,z in loop]
    faces=[]
    for i in range(4):
        j=(i+1)%4
        faces.extend([(i,j,4+j,4+i),(8+i,12+i,12+j,8+j),(i,8+i,8+j,j),(4+i,4+j,12+j,12+i)])
    bevel(mesh(name+'_continuous_leaf',verts,faces,colour),.002,2)
    frame(name+'_viewport_retainer',(vx,-.002,vz),vw+.054,vh+.054,.027,.022,'steel',.025)
    panel(name+'_wired_glazing',(vx,.035,vz),vw,vh,.008,.006,'glass')
    if STAGE>=2:
        for x in range(5):rod(name+'_wire',(vx-vw/2+.025+x*.06,.042,vz-vh/2),(vx-vw/2+.025+x*.06,.042,vz+vh/2),.0007,'steel',8)
        for z in range(10):rod(name+'_wire',(vx-vw/2,.042,vz-vh/2+.02+z*.06),(vx+vw/2,.042,vz-vh/2+.02+z*.06),.0007,'steel',8)
        box(name+'_kickplate',(0,.003,.185),(lw-.06,.012,.29),'steel',.003)
        panel(name+'_handle_escutcheon',(lw/2-.115,-.007,1.015),.046,.22,.02,.015,'steel')
        tube(name+'_lever',[(lw/2-.11,-.03,1.04),(lw/2-.11,-.089,1.04),(lw/2-.27,-.089,1.04)],.011,'steel')
        hx=(lw/2+.013)*(1 if hinge_right else -1)
        for z in [.23,1.09,1.95]:rod(name+'_hinge',(hx,.025,z-.05),(hx,.025,z+.05),.016,'steel')
        box(name+'_closer_body',(-.30,-.004,h-.15),(.28,.065,.065),'steel',.008)
        tube(name+'_closer_arm',[(-.3,-.04,h-.15),(-.08,-.12,h-.12),(.08,.02,h+.015)],.008,'steel')
        polish=use_marks(name+'_handle_contact_wear',(lw/2-.145,.006,1.04),surface='wall');polish.scale=(.32,.32,.32)
        support(polish,bpy.data.objects[name+'_continuous_leaf'],'LOCAL_+Y',[(0,0,0)],'WALL')
    leaf=group(name+'_LEAF',leafbefore)
    # Hinge origin without altering local mesh positions.
    hx=lw/2*(1 if hinge_right else -1)
    for child in leaf.children:child.location.x-=hx
    leaf.location.x=hx;leaf.rotation_euler.z=opened
    if opened:
        leaf.location.y=.24
        for z in [.23,1.09,1.95]:
            box(name+'_hinge_receiver',(hx+(.015 if hinge_right else -.015),.125,z),(.055,.25,.10),'darksteel',.003)
    leaf['interaction']='hinged door';leaf['closed_angle']=0.0
    return group(name,b,p,angle)

def garment_loft(name,rings,mat='cloth',n=40):
    # Rings: center x,y,z, elliptical radii. Broad diagonal creases, not faceted anatomy.
    v=[]
    for k,(x,y,z,rx,ry) in enumerate(rings):
        for j in range(n):
            a=j*2*pi/n
            wr=1+.055*sin(3*a+k*.85)+.035*sin(7*a-k*.65)
            v.append((x+rx*cos(a)*wr,y+ry*sin(a)*wr,z+.009*sin(4*a+k*.7)))
    f=[tuple(range(n-1,-1,-1))]+[(k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for k in range(len(rings)-1) for j in range(n)]+[tuple(range((len(rings)-1)*n,len(rings)*n))]
    o=mesh(name,v,f,mat,True);sub=o.modifiers.new('Soft tailored volume','SUBSURF');sub.levels=2
    bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=sub.name)
    return o

def suit(name,p=(0,0,0),angle=0,variant=0):
    b=start();bodyparts=[]
    bodyparts.append(garment_loft(name+'_torso',[(0,.014,.92,.16,.11),(.003,0,1.01,.23,.115),(0,.008,1.1,.225,.12),(-.01,0,1.16,.21,.12),(0,0,1.21,.205,.115),(0,0,1.3,.215,.13),(0,.008,1.42,.235,.145),(0,.02,1.49,.25,.13),(0,.035,1.55,.205,.105),(0,.025,1.6,.12,.085)]))
    for side in [-1,1]:
        bodyparts.append(garment_loft(name+'_leg',[(side*.125,0,.24,.061,.065),(side*.126,0,.27,.073,.076),(side*.132,.02,.31,.077,.075),(side*.136,.015,.38,.072,.071),(side*.14,.01,.47,.083,.075),(side*.141,-.01,.54,.09,.09),(side*.14,-.015,.575,.084,.080),(side*.137,.007,.615,.105,.097),(side*.126,.013,.67,.100,.094),(side*.124,.009,.75,.112,.105),(side*.118,.007,.86,.113,.108),(side*.107,.01,.96,.12,.109),(side*.10,.01,1.02,.11,.10)]))
        bodyparts.append(garment_loft(name+'_sleeve',[(side*.34,-.015,.92,.046,.055),(side*.35,-.005,.96,.055,.065),(side*.36,.015,1.03,.061,.065),(side*.357,.028,1.1,.061,.065),(side*.35,.026,1.18,.077,.074),(side*.347,.04,1.22,.068,.065),(side*.335,.046,1.27,.086,.08),(side*.31,.05,1.35,.095,.086),(side*.275,.039,1.44,.105,.097),(side*.235,.02,1.49,.10,.09)]))
    # Join the actual garment volumes into one continuous, editable soft shell.
    bpy.ops.object.select_all(action='DESELECT')
    for o in bodyparts:o.select_set(True)
    bpy.context.view_layer.objects.active=bodyparts[0];bpy.ops.object.join();body=bodyparts[0];body.name=name+'_continuous_coverall'
    rem=body.modifiers.new('Joined sewn garment','REMESH');rem.mode='VOXEL';rem.voxel_size=.007
    bpy.ops.object.modifier_apply(modifier=rem.name)
    sm=body.modifiers.new('Relax fabric joins','SMOOTH');sm.factor=.65;sm.iterations=4;bpy.ops.object.modifier_apply(modifier=sm.name)
    # Sculpt broad compression and tension folds into the connected garment.
    # Each fold has a slanted trough with a softer raised lip, localized to a cloth region.
    from math import exp
    for vert in body.data.vertices:
        x,y,z=vert.co;ax=abs(x)
        front=max(0,min(1,(-y+.008)/.08));rear=max(0,min(1,(y-.025)/.085))
        displacement=0
        folds=[(1.17+.24*x,.14,.022,.021), (1.27-.32*x,.21,.026,.019),
               (1.41+.35*ax,.27,.023,.019), (1.02-.24*x,.18,.023,.016)]
        if ax<.26 and z>.96:
            for center,width,spread,amp in folds:
                mask=exp(-((x/width)**4))
                dz=z-center
                displacement+=mask*amp*(-exp(-(dz/spread)**2)+.65*exp(-((dz-spread*1.6)/(spread*1.2))**2))
        if z<1.02:
            for cz,slope,amp in [(.36,.32,.010),(.565,-.45,.018),(.65,.62,.021),(.81,-.50,.017),(.91,.40,.013)]:
                dz=z-(cz+slope*(ax-.13));mask=exp(-((ax-.13)/.10)**4)
                displacement+=mask*amp*(-exp(-(dz/.015)**2)+.7*exp(-((dz-.025)/.018)**2))
        if ax>.24 and .95<z<1.48:
            for cz,amp in [(1.06,.011),(1.22,.016),(1.30,.011),(1.40,.013)]:
                dz=z-cz-.5*(ax-.34)
                displacement+=amp*(-exp(-(dz/.014)**2)+.6*exp(-((dz-.024)/.017)**2))
        vert.co.y-=displacement*front*.45
        vert.co.y+=displacement*rear*.25
        # Empty cloth droops inward rather than suggesting a posed mannequin.
        if z<1.04:vert.co.x+=.012*sin(z*4.8)*(1-z)
    for q in body.data.polygons:q.use_smooth=True
    # Hood is a cloth shape surrounding a curved visor rather than a cube helmet.
    garment_loft(name+'_hood',[(0,.025,1.53,.08,.07),(0,.01,1.6,.12,.11),(0,.018,1.68,.135,.125),(0,.018,1.77,.13,.12),(0,.025,1.85,.11,.10),(0,.03,1.89,.055,.05),(0,.03,1.9,.01,.01)])
    rim=frame(name+'_visor_seal',(0,-.112,1.745),.23,.20,.014,.018,'rubber',.065)
    shield=panel(name+'_laminated_visor',(0,-.127,1.745),.202,.172,.006,.049,'visor')
    for part in [rim,shield]:
        for vert in part.data.vertices:vert.co.y+=.025*(vert.co.x/.115)**2
    if STAGE>=2:
        def on_cloth(x,z):
            ok,loc,nor,idx=body.ray_cast(Vector((x,-.5,z)),Vector((0,1,0)))
            return (x,loc.y-.0016,z) if ok else None
        strip=[]
        for i in range(46):
            z=1.02+i*.0122
            for x in [-.009,.011]:
                q=on_cloth(x,z);strip.append(q or (x,-.10,z))
        mesh(name+'_sewn_storm_flap',strip,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(45)],'seam',True)
        zipper=[on_cloth(.015,1.18+i*.010) for i in range(39)]
        tube(name+'_zipper',[q for q in zipper if q],.0015,'darksteel')
        panel(name+'_dosimeter',(.105,-.147,1.36),.045,.077,.018,.006,'plastic')
        box(name+'_dosimeter_window',(.105,-.158,1.375),(.030,.002,.016),'ink',.001)
        for side in [-1,1]:
            points=[on_cloth(side*(.08+i*.006),1.56-i*.003) for i in range(31)]
            tube(name+'_shoulder_seam',[q for q in points if q],.0017,'seam')
            points=[on_cloth(side*.184,.31+i*.012) for i in range(58)]
            tube(name+'_outer_seam',[q for q in points if q],.0013,'seam')
            glove(name+'_glove',(side*.34,-.015,.92),side)
        panel(name+'_filter_pack',(0,.15,1.34),.25,.35,.115,.03,'plastic')
        tube(name+'_rescue_loop',[(-.07,.17,1.55),(-.06,.19,1.63),(.06,.19,1.63),(.07,.17,1.55)],.012,'rubber')
    root=group(name,b,p,angle);root['asset_role']='primary_PPE';root['plate']='05 / 21';return root

def glove(name,p,side=1):
    b=start()
    garment_loft(name+'_palm',[(0,0,-.095,.032,.017),(0,0,-.075,.044,.021),(0,0,-.025,.039,.023),(0,0,.014,.039,.023)],'rubber',24)
    for i,x in enumerate([-.031,-.010,.012,.033]):
        z=-.148+abs(i-1)*.009
        garment_loft(name+'_finger',[(x,-.01,z,.003,.004),(x,-.008,z+.014,.010,.011),(x,-.002,-.095,.012,.012),(x,0,-.072,.011,.013)],'rubber',16)
    garment_loft(name+'_thumb',[(side*.067,-.015,-.10,.004,.005),(side*.065,-.014,-.075,.013,.012),(side*.048,-.003,-.045,.016,.015),(side*.028,0,-.028,.021,.017)],'rubber',16)
    return group(name,b,p)

def boot(name,p=(0,0,0),angle=0):
    b=start()
    garment_loft(name+'_upper',[(0,-.018,.035,.059,.122),(0,-.025,.058,.066,.135),(0,-.030,.092,.064,.131),(0,-.011,.128,.058,.106),(0,.04,.16,.052,.057),(0,.047,.24,.052,.057),(0,.047,.265,.055,.062)],'rubber',32)
    sole=lathe(name+'_sole',[(0,.012),(.9,.012),(1,.021),(1,.04),(.90,.049),(0,.049)],'darksteel',48);sole.scale=(.072,.142,1);sole.location.y=-.025
    ring=lathe(name+'_open_cuff',[(.057,.253),(.061,.262),(.058,.274),(.048,.274),(.047,.249)],'rubber',32);ring.location.y=.047
    panel(name+'_heel_tab',(0,.110,.22),.022,.06,.008,.003,'yellow')
    return group(name,b,p,angle)

def bench(name,p=(0,0,0),angle=0,length=1.8):
    b=start();feet=[]
    for x in [-length*.34,length*.34]:
        # Bent tubular trestle, splayed at the floor. Seat top is exactly .45 m.
        tube(name+'_bent_trestle',[(x,-.22,.022),(x,-.17,.34),(x,-.13,.395),(x,.13,.395),(x,.17,.34),(x,.22,.022)],.016,'darksteel')
        for y in [-.22,.22]:
            box(name+'_rubber_foot',(x,y,.010),(.053,.070,.020),'rubber',.005);feet.append((x,y,0))
        box(name+'_seat_bracket',(x,0,.406),(.08,.41,.025),'steel',.003)
    rod(name+'_tie_rail',(-length*.34,0,.29),(length*.34,0,.29),.014,'darksteel')
    # Three narrow laminate boards reveal actual section thickness rather than one huge cushion.
    for y in [-.151,0,.151]:box(name+'_laminate_slat',(0,y,.432),(length,.143,.036),'wood',.008)
    if STAGE>=2:
        for x in [-length*.34,length*.34]:
            for y in [-.15,.15]:rod(name+'_seat_bolt',(x,y,.449),(x,y,.451),.006,'steel',12)
    root=group(name,b,p,angle);root['asset_role']='bench';return root,feet

def bay(name,p=(0,0,0),angle=0,variant=0):
    b=start()
    back=box(name+'_back',(0,.285,1.15),(1.05,.022,2.20),'paint',.003)
    # Sheet sides with returned lips, shallow tapered toe space and open lower boot tray.
    for x in [-.515,.515]:
        box(name+'_folded_side',(x,0,1.15),(.02,.60,2.20),'pale',.002)
        box(name+'_return_lip',(x,-.293,1.15),(.052,.02,2.20),'pale',.002)
    for z in [.085,2.23]:box(name+'_folded_shelf',(0,-.005,z),(1.05,.61,.025),'pale',.002)
    box(name+'_upper_cubby_shelf',(0,.10,2.04),(1.00,.37,.018),'pale',.002)
    box(name+'_cubby_divider',(.22,.10,2.14),(.012,.37,.19),'pale',.002)
    for x in [-.43,.43]:box(name+'_plinth_foot',(x,.15,.028),(.08,.19,.056),'darksteel',.001)
    hook=rod(name+'_hanger_rail',(-.30,.15,1.997),(.30,.15,1.997),.011,'steel')
    tube(name+'_garment_hanger',[(-.20,.14,1.57),(0,.14,1.67),(.20,.14,1.57),(-.20,.14,1.57)],.008,'steel')
    tube(name+'_suspension',[(0,.14,1.64),(0,.14,1.978),(0,.15,1.997)],.006,'steel')
    s=suit(name+'_PPE',(0,-.005,.10),variant=variant)
    for x in [-.13,.13]:
        shoe=boot(name+'_work_boot',(x,-.12,.0855),(-.045 if x<0 else .025)+variant*.01)
        support(shoe,bpy.data.objects[name+'_folded_shelf'],'LOCAL_-Z',[(0,-.025,.012)])
    mat=box(name+'_standing_mat',(0,-.57,.006),(.93,.47,.012),'rubber',.006)
    if STAGE>=2:
        if variant in [0,2]:
            cartridge=filter_can(name+'_spare_cartridge',(.37,.08,2.049))
            support(cartridge,bpy.data.objects[name+'_upper_cubby_shelf'],'LOCAL_-Z',[(0,0,0)])
        if variant in [1,3]:
            card=box(name+'_inspection_card',(-.13,.273,2.129),(.17,.002,.115),'paper',.001)
            support(card,back,'LOCAL_+Y',[(0,.001,0)],'WALL')
            label(name+'_inspection_type','SERVICED',(-.199,.270,2.146),.025,'ink')
            label(name+'_inspection_date',['04 / 09','05 / 09'][variant//2],(-.199,.270,2.109),.021,'ink')
        for y in range(11):box(name+'_mat_rib',(0,-.77+y*.037,.013),(.87,.007,.003),'rubber',.001)
        label(name+'_ID',f'{variant+1:02d}',(-.455,-.306,2.11),.064,'ink')
        box(name+'_identity_band',(.43,-.306,2.125),(.035,.012,.13),['yellow','blue','red','paint'][variant],.001)
        rod(name+'_indicator',(.455,-.314,1.9),(.455,-.328,1.9),.013,'ready')
        for z in [2.08,.21]:
            for x in [-.485,.485]:rod(name+'_mount_screw',(x,-.309,z),(x,-.315,z),.007,'steel',12)
    root=group(name,b,p,angle);root['asset_role']='suit_station';root['station_id']=variant+1
    return root,[(-.43,.15,0),(.43,.15,0),(0,-.57,0)]

def practical(name,p=(0,0,3.3),angle=0,power=230,length=1.4):
    b=start()
    # Folded reflector enclosure with end caps and diffuser; source follows real diffuser footprint.
    box(name+'_backpan',(0,0,-.045),(length,.29,.09),'pale',.005)
    for y in [-.14,.14]:box(name+'_folded_lip',(0,y,-.101),(length,.025,.062),'steel',.002)
    for x in [-length/2,length/2]:box(name+'_endcap',(x,0,-.09),(.025,.3,.09),'pale',.004)
    box(name+'_diffuser',(0,0,-.107),(length-.07,.238,.025),'lamp',.007)
    d=bpy.data.lights.new(name+'_photometric','AREA');d.energy=power;d.shape='RECTANGLE';d.size=length-.08;d.size_y=.23;d.color=(1,.92,.78)
    o=bpy.data.objects.new(name+'_photometric',d);bpy.context.collection.objects.link(o);o.location.z=-.127
    root=group(name,b,p,angle);return root,[(-length*.32,0,0),(length*.32,0,0)]

def utility(name,p=(0,0,0),angle=0,height=3.4):
    b=start();rod(name+'_service_riser',(0,-.115,.06),(0,-.115,height+.06),.036,'pale')
    for z in [.35,1.72,2.97]:
        box(name+'_mount_pad',(0,-.019,z),(.13,.038,.09),'steel',.005)
        box(name+'_standoff',(0,-.059,z),(.035,.079,.035),'steel',.002)
        pts=[(.042*cos(a),-.115+.042*sin(a),z) for a in [j*2*pi/32 for j in range(33)]]
        tube(name+'_strap_clamp',pts,.009,'steel')
    if STAGE>=2:
        rod(name+'_repair_sleeve',(0,-.115,.91),(0,-.115,1.065),.043,'darksteel')
        rod(name+'_inspection_band',(0,-.115,.945),(0,-.115,.969),.046,'yellow')
    return group(name,b,p,angle),[(0,0,z) for z in [.35,1.72,2.97]]

def mug(name,p=(0,0,0)):
    b=start();lathe(name+'_enamel',[(0,0),(.035,0),(.044,.010),(.046,.091),(.045,.103),(.041,.103),(.040,.017),(0,.017)],'enamel')
    tube(name+'_handle',[(.043+.031*cos(a),0,.055+.032*sin(a)) for a in [(-pi/2)+i*pi/20 for i in range(41)]],.006,'enamel')
    rod(name+'_coffee',(0,0,.078),(0,0,.079),.041,'coffee')
    return group(name,b,p)

def clipboard(name,p=(0,0,0),angle=0):
    b=start();base=box(name+'_board',(0,0,.004),(.22,.31,.008),'wood',.005)
    # Slightly bowed paper physically touches the board near clip.
    v=[(-.10,-.14,.009),(.10,-.14,.009),(.10,.08,.009),(.095,.13,.017),(-.10,.13,.009),(-.10,.08,.009)]
    mesh(name+'_paper',v,[(0,1,2,5),(5,2,3,4)],'paper')
    box(name+'_clip',(0,.10,.014),(.092,.028,.012),'steel',.004)
    if STAGE>=2:
        label(name+'_heading','SEAL CHECK',(-.082,.058,.010),.020,'ink',rot=(0,0,0))
        for i in range(5):
            box(name+'_rule',(.013,.013-i*.027,.0098),(.13,.0014,.0004),'ink',0)
            box(name+'_checkbox',(-.079,.013-i*.027,.0098),(.008,.008,.0004),'ink',0)
    return group(name,b,p,angle)

def filter_can(name,p=(0,0,0)):
    b=start();lathe(name+'_cartridge',[(0,0),(.046,0),(.050,.007),(.050,.058),(.045,.07),(.041,.074),(0,.074)],'plastic',32)
    for z in [.008,.025,.042,.058]:
        lathe(name+'_flute',[(.049,z),(.053,z+.002),(.049,z+.006)],'darksteel',32)
    rod(name+'_cap',(0,0,.074),(0,0,.079),.035,'yellow');return group(name,b,p)

def use_marks(name,p=(0,0,0),angle=0,surface='floor'):
    """Small curated contact-wear cluster, never a global dirt overlay."""
    b=start();rng=random.Random(name)
    for i in range(9):
        x=rng.uniform(-.23,.23);y=rng.uniform(-.12,.12);length=rng.uniform(.025,.11);width=rng.uniform(.0015,.005)
        pts=[(x-length/2,y,.0007),(x-length*.2,y+width,.0007),(x+length/2,y+width*.4,.0007),(x+length*.2,y-width*.7,.0007)]
        if surface=='wall':pts=[(xx,-zz,yy) for xx,yy,zz in pts]
        mesh(name+'_rub_mark',pts,[(0,1,2,3)],'wear')
    return group(name,b,p,angle)
