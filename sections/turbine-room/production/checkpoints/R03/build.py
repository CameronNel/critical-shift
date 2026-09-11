"""Original metric Critical Shift turbine hall. Factory-empty, no imported geometry.
Run through run.ps1. Geometry, shader families and camera evidence are reproducible.
"""
import bpy, math, json, sys, argparse, random
from mathutils import Vector
from pathlib import Path

P=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(); ap.add_argument('--phase',default='slice',choices=['slice','full']); ap.add_argument('--revision',default='slice-01'); ap.add_argument('--render',default=''); ap.add_argument('--samples',type=int,default=48)
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene; S.unit_settings.system='METRIC'; S.unit_settings.scale_length=1
random.seed(28); SUPPORT=[]; GROUP='Architecture'

def rgb(h):
    v=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(c/12.92 if c<.04045 else ((c+.055)/1.055)**2.4 for c in v)
def material(name,h,rough,metal=0,variation=0,bump=0,emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*rgb(h),1); m.use_nodes=True
    n=m.node_tree.nodes; l=m.node_tree.links; b=n.get('Principled BSDF')
    b.inputs['Base Color'].default_value=(*rgb(h),1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    if emission: b.inputs['Emission Color'].default_value=(*rgb(h),1); b.inputs['Emission Strength'].default_value=emission
    if variation or bump:
        tex=n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=3.2; tex.inputs['Detail'].default_value=2
        coord=n.new('ShaderNodeTexCoord'); l.new(coord.outputs['Generated'],tex.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.18; ramp.color_ramp.elements[1].position=.82
        ramp.color_ramp.elements[0].color=(*[c*(1-variation) for c in rgb(h)],1); ramp.color_ramp.elements[1].color=(*[min(1,c*(1+variation)) for c in rgb(h)],1)
        l.new(tex.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs[0],b.inputs['Base Color'])
        if bump:
            fine=n.new('ShaderNodeTexNoise'); fine.inputs['Scale'].default_value=125; fine.inputs['Detail'].default_value=1
            l.new(coord.outputs['Generated'],fine.inputs['Vector']); bn=n.new('ShaderNodeBump'); bn.inputs['Strength'].default_value=.22; bn.inputs['Distance'].default_value=bump
            l.new(fine.outputs['Fac'],bn.inputs['Height']); l.new(bn.outputs[0],b.inputs['Normal'])
    return m
M={
 'wall':material('Warm mineral plaster','b4b0a3',.87,variation=.045,bump=.002),
 'concrete':material('Dense cast concrete','87847C',.9,variation=.045,bump=.002),
 'floor':material('Dry worn terrazzo concrete','96928A',.77,variation=.07,bump=.005),
 'teal':material('Oxide orange enamel','B56D38',.48,.22,.09,.003),
 'darkteal':material('Structural painted steel','41444A',.61,.35,.06),
 'cream':material('Thermal jacket warm grey','C8C5B9',.7,.08,.05,.002),
 'steel':material('Machined steel','7c878a',.43,.88,.06),
 'dark':material('Oiled iron','30383c',.62,.65,.09),
 'rubber':material('Matte vulcanized rubber','232829',.94,variation=.06,bump=.003),
 'yellow':material('Service ochre enamel','c49c40',.58,.12,.06),
 'red':material('Emergency red enamel','a34332',.52,.15),
 'wood':material('Worn beech work surface','826949',.82,variation=.15,bump=.006),
 'paper':material('Offwhite shift paper','d4d0b5',.97),
 'ink':material('Printed dark ink','233037',.87),
 'cloth':material('Cotton cleaning rag','777268',.98,variation=.07,bump=.004),
 'white':material('Warm label lettering','e2deca',.78),
 'lamp':material('Warm diffusing glass','ffe2b1',.4,emission=3),
 'coollamp':material('Cool daylight glass','bed4dc',.45,emission=2),
 'screen':material('Instrument phosphor','E4C992',.5,emission=.25),
 'glass':material('Smoked instrument glass','62616A',.21,.25),
}
def group(name):
    global GROUP; GROUP=name
    if name not in bpy.data.collections:
        c=bpy.data.collections.new(name); S.collection.children.link(c)
def reg(o,name,mat):
    o.name=name
    if mat: o.data.materials.append(M[mat])
    if GROUP not in bpy.data.collections: group(GROUP)
    for c in list(o.users_collection): c.objects.unlink(o)
    bpy.data.collections[GROUP].objects.link(o)
    o['construction']='authored structural or assembly component'
    return o
def bevel(o,w=.01):
    if w:
        m=o.modifiers.new('Manufactured edge radius','BEVEL');m.width=w;m.segments=2
        m=o.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL')
    return o
def box(n,p,d,m,b=.005):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=reg(bpy.context.object,n,m);o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return bevel(o,min(b,min(d)*.2))
def cyl(n,p,r,length,m,axis='Z',verts=48,b=.004):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=length,location=p);o=reg(bpy.context.object,n,m)
    if axis=='Y':o.rotation_euler[0]=math.pi/2
    if axis=='X':o.rotation_euler[1]=math.pi/2
    for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
    return bevel(o,min(b,r*.25,length*.2))
def beam(n,a,b,r,m):
    a,b=Vector(a),Vector(b);o=cyl(n,(a+b)/2,r,(b-a).length,m,verts=16,b=.002);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def torus(n,p,R,r,m,axis='Z'):
    bpy.ops.mesh.primitive_torus_add(major_radius=R,minor_radius=r,major_segments=48,minor_segments=10,location=p);o=reg(bpy.context.object,n,m)
    if axis=='Y':o.rotation_euler[0]=math.pi/2
    if axis=='X':o.rotation_euler[1]=math.pi/2
    for f in o.data.polygons:f.use_smooth=True
    return o
def mesh(n,verts,faces,m,b=0):
    me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);S.collection.objects.link(o);reg(o,n,m);return bevel(o,b)
def extrude_profile(n,profile,y0,y1,m,b=.005):
    N=len(profile);v=[(x,y,z) for y in [y0,y1] for x,z in profile];f=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
    return mesh(n,v,f,m,b)
def pipe(n,points,r,m):
    cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=r;cu.bevel_resolution=4
    sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for bp,p in zip(sp.bezier_points,points):bp.co=p;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
    o=bpy.data.objects.new(n,cu);S.collection.objects.link(o);return reg(o,n,m)
def text(n,t,p,size=.12,mat='white',face='S',align='LEFT'):
    cu=bpy.data.curves.new(n,'FONT');cu.body=t;cu.size=size;cu.extrude=.0005;cu.align_x=align
    o=bpy.data.objects.new(n,cu);S.collection.objects.link(o);reg(o,n,mat);o.location=p
    o.rotation_euler={'S':(math.pi/2,0,0),'E':(math.pi/2,0,math.pi/2),'W':(math.pi/2,0,-math.pi/2),'N':(math.pi/2,0,math.pi),'UP':(0,0,0)}[face];return o
def anchor(n,p,target,direction=(0,0,-1),gap=.005,penetration=.002,prop=None,members=None):
    o=bpy.data.objects.new('SUPPORT_'+n,None);bpy.data.collections[GROUP].objects.link(o);o.location=p;o.empty_display_size=.04
    SUPPORT.append(dict(anchor=o.name,target=target,prop=prop,members=members or [],direction=direction,max_gap=gap,max_penetration=penetration,angle_deg=12));return o
def light(n,p,target,power,color=(1,.84,.62),size=1.4,shape='DISK',size_y=None):
    d=bpy.data.lights.new(n,'AREA');d.energy=power;d.color=color;d.shape=shape;d.size=size
    if size_y and shape=='RECTANGLE':d.size_y=size_y
    o=bpy.data.objects.new(n,d);S.collection.objects.link(o);reg(o,n,None);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def bolt(n,p,axis='Z',r=.022):return cyl(n,p,r,.024,'steel',axis,6,.002)
def plate_bolts(n,p,w,h,face='S'):
    for i,x in enumerate([-.5*w+.045,.5*w-.045]):
        for j,z in enumerate([-.5*h+.045,.5*h-.045]):
            if face=='S':bolt(n+str(i)+str(j),(p[0]+x,p[1]-.016,p[2]+z),'Y',.012)
            else:bolt(n+str(i)+str(j),(p[0]+.016,p[1]+x,p[2]+z),'X',.012)

def door(y,n):
    # Own pockets sit inside thick reveals, outside the 2.4m cart opening.
    for x in [-1.32,1.32]:
        box(n+' jamb',(x,y-.08,1.4),(.24,.48,2.8),'darkteal',.014)
        box(n+' rubber seal',(x+(.104 if x<0 else -.104),y-.21,1.35),(.025,.06,2.7),'rubber',.002)
    box(n+' lintel',(0,y-.08,2.85),(2.88,.48,.3),'darkteal',.018)
    for side in [-1,1]:
        x=side*1.98
        yp=y+(.075 if y==0 else -.075)
        box(n+' parked leaf',(x,yp,1.34),(1.18,.11,2.65),'teal',.009)
        box(n+' leaf inset',(x,yp-.064,1.66),(.9,.025,1.45),'darkteal',.007)
        box(n+' kick plate',(x,yp-.069,.35),(.92,.027,.4),'steel',.003)
        box(n+' pull pocket',(x-side*.4,yp-.086,1.1),(.07,.024,.3),'rubber',.006)
        for z in [.6,2.5]:
            for dx in [-.44,.44]:bolt(n+' leaf fastener',(x+dx,yp-.067,z),'Y',.012)
        for dx in [-.42,.42]:
            cyl(n+' suspension roller',(x+dx,yp,2.75),.062,.07,'dark','Y',24)
        box(n+' running rail',(x,yp,2.81),(1.25,.06,.04),'steel',.002)
    box(n+' threshold',(0,y, -.01),(2.4,.45,.02),'steel',.001)
    box(n+' sign',(0,y-.33,3.18),(2.55,.05,.34),'darkteal',.007)
    text(n+' direction','ELECTRICAL   /   03' if y>12 else 'REACTOR   /   01',(0,y-.36,3.09),.19,align='CENTER')
    bracket=box(n+' sign bracket',(0,y-.08,3.09),(.18,.18,.18),'darkteal',.004)
    beam(n+' sign standoff',(0,y-.08,3.18),(0,y-.305,3.18),.028,'darkteal')
    anchor(n+' sign',(0,y-.08,3.0),n+' lintel',prop=bracket.name,members=[n+' sign',n+' sign standoff',n+' direction'])
    # A short section-owned threshold reveal; no neighboring room geometry.
    if y>12:
        for x in [-1.325,1.325]:box(n+' portal return',(x,y+.6,1.45),(.25,1.2,2.9),'concrete',.008)
        box(n+' return soffit',(0,y+.6,2.82),(2.9,1.2,.2),'concrete')
        box(n+' return floor',(0,y+.6,-.12),(2.9,1.2,.24),'floor')
        light(n+' threshold light',(0,y+.55,2.6),(0,y+.5,0),100,(.63,.8,1),1)

def architecture(slice=False):
    group('01 Architecture')
    ya=17 if slice else 0;depth=24-ya
    floor=box('Structural floor',(3,(24+ya)/2,-.17),(14.5,depth+.5,.34),'floor',.005)
    # Inlaid expansion joints, quiet large floor modules.
    for y in range(ya,25,3):box('Floor expansion joint',(3,y,.001),(14,.012,.003),'dark',0)
    for x in [-4,-1,2,5,8,10]:box('Floor longitudinal joint',(x,(24+ya)/2,.001),(.01,depth,.003),'dark',0)
    for x in [-4.125,10.125]:
        box('West wall' if x<0 else 'East wall',(x,(24+ya)/2,3.6),(.25,depth,7.2),'wall',.006)
        box('Concrete impact plinth',(x+(.13 if x<0 else -.13),(24+ya)/2,.46),(.12,depth,.92),'concrete',.008)
        box('Impact cap',(x+(.19 if x<0 else -.19),(24+ya)/2,.95),(.06,depth,.07),'darkteal',.003)
    for y in ([24] if slice else [0,24]):
        for a,b in [(-4,-1.2),(1.2,10)]:box('End wall',(a+(b-a)/2,y+.125,3.6),(b-a,.25,7.2),'wall',.006)
        box('Overdoor wall',(0,y+.125,5.02),(2.4,.25,4.36),'wall',.006)
        door(y,'D02 electrical' if y else 'D01 reactor')
    box('Roof deck',(3,(24+ya)/2,7.32),(14.5,depth+.5,.24),'dark',.005)
    for y in [v for v in [1,6,11,16,21,23.6] if v>=ya]:
        for x in [-3.8,9.8]:
            box('Column web',(x,y,3.55),(.16,.27,7.1),'darkteal',.003)
            for dy in [-.2,.2]:box('Column flange',(x,y+dy,3.55),(.4,.055,7.1),'darkteal',.003)
            box('Column foot',(x,y,.06),(.64,.64,.12),'darkteal',.005)
            for dx in [-.23,.23]:
                for dy in [-.23,.23]:bolt('Column anchor',(x+dx,y+dy,.13))
        box('Roof girder web',(3,y,6.72),(13.6,.12,.64),'darkteal',.003)
        for z in [6.38,7.04]:box('Roof girder flange',(3,y,z),(13.6,.42,.06),'darkteal',.003)
        for x in [-3,9]:beam('Knee brace',(x,y,5.65),(x+(1.1 if x<0 else -1.1),y,6.62),.06,'darkteal')
    # Longitudinal structural purlins and practical housings.
    for x in [-1,3,7]:box('Roof purlin',(x,(24+ya)/2,7.02),(.1,depth,.16),'darkteal')
    for y in [v for v in [3.5,9,14.5,20] if v>=ya]:
        for x in [.5,7.8]:
            back=box('Suspended luminaire back',(x,y,6.05),(.28,1.7,.1),'darkteal',.025)
            diffuser=box('Prismatic diffuser',(x,y,5.985),(.2,1.54,.035),'lamp',.006)
            for dy in [-.6,.6]:
                hanger=beam('Fixture hanger',(x,y+dy,6.1),(x,y+dy,7.2),.011,'steel')
                anchor('fixture '+hanger.name,(x,y+dy,7.2),'Roof deck',(0,0,1),prop=hanger.name,members=[back.name,diffuser.name])
            light('Practical pool',(x,y,5.92),(x,y,0),350,(1,.86,.68),1.4,'RECTANGLE',.22)
    for y in [v for v in [5,12.5,20] if v>=ya]:
        box('Clerestory frame',(9.96,y,5.3),(.12,3.1,1.6),'darkteal',.009)
        box('Frosted daylight glazing',(9.88,y,5.3),(.035,2.9,1.38),'coollamp',.002)
        for dy in [-.97,0,.97]:box('Window mullion',(9.84,y+dy,5.3),(.08,.06,1.4),'darkteal')
        light('Clerestory broad fill',(9.77,y,5.3),(2,y-1,1),550,(.69,.82,1),2.8,'RECTANGLE',1.3)
    for x in [-1.2,1.2]:box('Clear route margin',(x,(24+ya)/2,.005),(.055,depth,.008),'yellow',.001)

def ring(n,p,outer,inner,depth,mat='steel',axis='Y',segments=64):
    x,y,z=p;v=[]
    for yy,rr in [(-depth/2,outer),(depth/2,outer),(-depth/2,inner),(depth/2,inner)]:
        for i in range(segments):
            a=i*math.tau/segments;v.append((x+rr*math.cos(a),y+yy,z+rr*math.sin(a)))
    f=[]
    for i in range(segments):
        j=(i+1)%segments
        f.extend([(i,j,segments+j,segments+i),(2*segments+i,3*segments+i,3*segments+j,2*segments+j),(i,2*segments+i,2*segments+j,j),(segments+i,segments+j,3*segments+j,3*segments+i)])
    o=mesh(n,v,f,mat,min(.002,(outer-inner)*.2,depth*.2))
    for poly in o.data.polygons:poly.use_smooth=poly.index%4<2
    return o
def bearing(n,p,r=.22):
    ring(n+' outer race',p,r+.03,r-.009,.1);ring(n+' inner race',p,r*.65,r*.48,.12)
    ring(n+' retainer',(p[0],p[1]-.048,p[2]),r-.012,r*.65,.013,'dark')
    for i in range(12):
        a=i*math.tau/12;cyl(n+' roller',(p[0]+r*.8*math.cos(a),p[1],p[2]+r*.8*math.sin(a)),.029,.065,'steel','Y',16)
def wrench(n,p,length=.34,rot=0):
    o=box(n+' shank',(p[0],p[1],p[2]),(.033,length*.72,.016),'steel',.008);o.rotation_euler[2]=rot
    for s in [-1,1]:
        c=(p[0]-math.sin(rot)*s*length*.4,p[1]+math.cos(rot)*s*length*.4,p[2]);torus(n+' jaw',c,.044,.014,'steel')
def mug(p):
    # Lathed thick open cup with dark coffee below the lip.
    x,y,z=p;profile=[(.0,0),(.065,0),(.077,.02),(.08,.12),(.073,.135),(.064,.126),(.063,.02),(.0,.018)]
    N=48;v=[(x+r*math.cos(a*math.tau/N),y+r*math.sin(a*math.tau/N),z+h) for r,h in profile for a in range(N)]
    f=[]
    for k in range(len(profile)-1):
        for a in range(N):f.append((k*N+a,k*N+(a+1)%N,(k+1)*N+(a+1)%N,(k+1)*N+a))
    mesh('Enamel shift mug',v,f,'cream');torus('Mug handle',(x+.096,y,z+.078),.041,.012,'cream','Y');cyl('Coffee',(x,y,z+.1),.062,.004,'dark')
def cloth(p):
    x,y,z=p;N=12;v=[]
    for j in range(N+1):
        for i in range(N+1):
            xx=i/N*.46; yy=j/N*.34;v.append((x+xx,y+yy,z+.004+abs(.014*math.sin(xx*24+yy*7)+.006*math.cos(yy*48))))
    f=[(j*(N+1)+i,j*(N+1)+i+1,(j+1)*(N+1)+i+1,(j+1)*(N+1)+i) for j in range(N) for i in range(N)]
    o=mesh('Used folded cotton rag',v,f,'cloth');s=o.modifiers.new('Cloth thickness','SOLIDIFY');s.thickness=.004

def bench():
    group('05 Maintenance bay')
    # Bench is a trestle frame with open lower rack, not a cabinet cube.
    for x in [-3.6,-2.85]:
        for y in [20.05,22.65]:
            foot=box('Bench foot',(x,y,.028),(.18,.16,.056),'rubber',.014)
            box('Bench upright',(x,y,.45),(.06,.06,.86),'darkteal',.004)
            anchor('bench foot '+str(x)+str(y),(x,y,0),'Structural floor',prop=foot.name)
    box('Bench top',(-3.245,21.35,.94),(1.25,3,.12),'wood',.006)
    for x in [-3.64,-2.8]:
        angle=box('Bench top angle', (x,21.35,.835),(.07,2.78,.09),'darkteal')
        anchor('bench top '+str(x),(x,21.35,.88),angle.name,prop='Bench top')
        box('Lower shelf rail',(x,21.35,.22),(.05,2.78,.05),'darkteal')
    for y in [20.04,22.66]:box('Trestle crossmember',(-3.245,y,.45),(.85,.06,.08),'darkteal')
    for i in range(8):box('Open lower shelf',(-3.245,20.12+i*.35,.25),(.9,.05,.04),'darkteal')
    beam('Bench rear diagonal',(-3.6,20.06,.24),(-3.6,22.63,.82),.018,'steel')
    # Old vise: flared cast body, moving jaw, screw, rotating handle.
    box('Vise bolt base',(-2.80,20.3,1.025),(.35,.35,.05),'dark',.016)
    cyl('Vise swivel',(-2.80,20.3,1.09),.13,.1,'darkteal')
    extrude_profile('Cast vise body',[(-2.95,1.09),(-2.65,1.09),(-2.61,1.21),(-2.68,1.29),(-2.92,1.29),(-2.99,1.21)],20.22,20.53,'teal',.012)
    for y in [20.18,20.52]:box('Vise serrated jaw',(-2.80,y,1.3),(.32,.065,.07),'steel',.002)
    cyl('Vise lead screw',(-2.80,20.05,1.17),.028,.45,'steel','Y')
    beam('Vise T handle',(-2.95,19.83,1.17),(-2.61,19.83,1.17),.016,'steel')
    for x in [-2.93,-2.67]:bolt('Vise anchor',(x,20.39,1.06))
    anchor('vise',(-2.80,20.3,1.0),'Bench top',prop='Vise bolt base')
    # Bearing removed for inspection, stand and log laid alongside it.
    box('Bearing inspection cradle',(-3.22,21.25,1.025),(.64,.32,.05),'darkteal',.007)
    for x in [-3.43,-3.01]:extrude_profile('Cradle cheek',[(x-.045,1.05),(x+.045,1.05),(x+.025,1.22),(x-.025,1.22)],21.15,21.35,'darkteal')
    bearing('Spare journal bearing',(-3.22,21.25,1.28))
    anchor('bearing cradle',(-3.22,21.25,1.0),'Bench top',prop='Bearing inspection cradle')
    mug((-3.48,22.23,1.0));anchor('mug',(-3.48,22.23,1.0),'Bench top',prop='Enamel shift mug')
    cloth((-3.25,21.8,1.0))
    rag=bpy.data.objects['Used folded cotton rag'];pv=min(rag.data.vertices,key=lambda v:v.co.z).co
    anchor('rag',(pv.x,pv.y,1.0),'Bench top',prop=rag.name)
    wrench('Maintenance spanner',(-2.95,21.55,1.015),.36,.35)
    box('Clipboard',(-2.99,22.36,1.012),(.33,.44,.02),'wood',.008)
    box('Shift log paper',(-2.99,22.35,1.024),(.29,.38,.004),'paper',.001)
    text('Shift log heading','T-01  /  SHIFT LOG',(-3.11,22.44,1.028),.027,'ink','UP')
    for i in range(6):box('Log ruled line',(-2.99,22.37-i*.038,1.028),(.24,.001,.001),'ink',0)
    box('Clipboard clip',(-2.99,22.54,1.04),(.12,.045,.025),'steel',.005)
    anchor('clipboard',(-2.99,22.36,1.002),'Bench top',prop='Clipboard')
    # Wall panel and task practical, secured to the masonry.
    box('Tool rail back',(-3.965,21.15,1.8),(.07,2.35,.14),'darkteal',.009)
    anchor('tool rail',(-4,21.15,1.8),'West wall',(-1,0,0),prop='Tool rail back')
    for y in [20.4,20.9,21.4]:
        beam('Tool hook',(-3.93,y,1.79),(-3.8,y,1.79),.012,'steel')
        torus('Hanging ring spanner',(-3.8,y,1.75),.045,.011,'steel','X')
        box('Hanging spanner shank',(-3.8,y,1.6),(.018,.035,.22),'steel',.008)
        torus('Lower wrench jaw',(-3.8,y,1.46),.038,.012,'steel','X')
    box('Task lamp wall foot',(-3.95,21.3,2.45),(.1,.22,.22),'darkteal',.012)
    beam('Task lamp outreach',(-3.9,21.3,2.45),(-3.15,21.3,2.45),.025,'darkteal')
    box('Task lamp shade',(-3.12,21.3,2.42),(.29,1.5,.12),'darkteal',.025)
    box('Task lamp diffuser',(-3.12,21.3,2.347),(.22,1.38,.025),'lamp',.008)
    light('Bench fluorescent pool',(-3.12,21.3,2.3),(-2.7,21.3,.95),115,(1,.89,.71),1.25,'RECTANGLE',.18)
    anchor('task lamp',(-4,21.3,2.45),'West wall',(-1,0,0),prop='Task lamp wall foot')
    # Purposeful mismatched repair to the conduit and a restrained wall notice.
    conduit=pipe('Bench electrical conduit',[(-3.92,18.2,4.4),(-3.92,22.35,4.4),(-3.92,22.70,4.25),(-3.92,22.85,3.9),(-3.92,22.85,1.4)],.024,'steel')
    bp=conduit.data.splines[0].bezier_points
    bp[0].handle_right_type='VECTOR';bp[1].handle_left_type='VECTOR';bp[3].handle_right_type='VECTOR';bp[4].handle_left_type='VECTOR'
    for z in [1.8,3.2,3.8]:
        saddle=box('Conduit saddle',(-3.96,22.85,z),(.08,.13,.05),'darkteal');anchor('conduit saddle '+str(z),(-4,22.85,z),'West wall',(-1,0,0),prop=saddle.name)
    jb=box('Replacement junction box',(-3.89,22.85,1.32),(.22,.3,.33),'cream',.009)
    anchor('junction box',(-4,22.85,1.32),'West wall',(-1,0,0),prop=jb.name)
    box('Lubrication chart',(-3.994,19.4,1.65),(.012,.5,.68),'paper',.003)
    text('Chart title','BEARING\nSERVICE',(-3.985,19.18,1.85),.068,'ink','E')
    for z in [1.64,1.57,1.5,1.43]:box('Chart rule',(-3.984,19.4,z),(.002,.39,.003),'ink',0)
    anchor('lubrication chart',(-4,19.4,1.65),'West wall',(-1,0,0),prop='Lubrication chart')
    # Tall narrow oil dispensing stand, shaped tank, fill neck, manual pump.
    box('Oil stand feet',(-2.95,18.75,.04),(.72,.65,.08),'darkteal',.009)
    for x in [-3.21,-2.69]:box('Oil stand leg',(x,18.75,.41),(.06,.55,.75),'darkteal',.003)
    cyl('Oil reservoir',(-2.95,18.75,1.02),.3,.65,'teal')
    torus('Oil tank lower bead',(-2.95,18.75,.7),.3,.018,'steel');torus('Oil tank upper bead',(-2.95,18.75,1.34),.3,.018,'steel')
    cyl('Oil fill neck',(-2.95,18.75,1.41),.085,.14,'steel');cyl('Oil pump piston',(-2.95,18.75,1.58),.026,.25,'steel')
    beam('Oil pump handle',(-3.15,18.75,1.69),(-2.75,18.75,1.69),.023,'rubber')
    pipe('Oil hose',[(-2.68,18.75,1.32),(-2.5,18.75,1.15),(-2.53,18.72,.72),(-2.62,18.67,.56)],.022,'rubber')
    anchor('oil stand',(-2.95,18.75,0),'Structural floor',prop='Oil stand feet')

CAMERAS=[
 ('C01_entry',(0,1.2,1.68),(3.4,10.7,2.0),23),
 ('C02_hero',(-.6,5.0,1.68),(4.6,11,2.05),25),
 ('C03_reverse',(.0,22.5,1.68),(4.2,12,2),24),
 ('C04_route',(0,9,1.68),(0,22.9,1.6),24),
 ('C05_east_service',(8.3,18.9,1.68),(6.1,9,1.6),24),
 ('C06_throttle',(-.55,8.8,1.68),(-2.7,11,1.25),31),
 ('C07_coupling',(7.65,13.75,1.5),(4.6,13.65,1.65),36),
 ('C08_maintenance',(1.6,17.7,1.68),(-2.45,21.5,1.55),26),
 ('C09_generator',(7.8,21.4,1.68),(4.6,17,2),28),
 ('C10_materials',(-1.42,20.5,1.68),(-2.9,21.15,1.12),41),
]
SUPPLEMENT=[
 ('W01_entry_return',(0,2,1.68),(0,0,1.6),22),
 ('W02_controls_full',(0,10.3,1.68),(-3,10.3,1.35),22),
 ('W03_south_cross',(8.1,3,1.68),(0,3,1.5),23),
 ('W04_north_cross',(8.1,21.7,1.68),(0,21.7,1.5),23),
 ('W05_oil_service',(1.45,12.1,1.68),(3,12.8,1.2),26),
 ('W06_steam_service',(8.4,8.7,1.68),(6.2,7.2,2.4),23),
]

def cameras():
    group('09 Fixed evidence cameras')
    for n,p,t,lens in CAMERAS+SUPPLEMENT:
        d=bpy.data.cameras.new(n);d.lens=lens;d.clip_start=.08;d.clip_end=150;o=bpy.data.objects.new(n,d);S.collection.objects.link(o);reg(o,n,None);o.location=p;o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
    S.camera=bpy.data.objects['C08_maintenance' if args.phase=='slice' else 'C02_hero']
def settings():
    S.render.engine='CYCLES';S.cycles.samples=args.samples;S.cycles.use_denoising=True;S.cycles.seed=28
    S.cycles.max_bounces=8;S.cycles.diffuse_bounces=4;S.cycles.glossy_bounces=4
    S.render.resolution_x=1440;S.render.resolution_y=900;S.render.resolution_percentage=100
    S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.film_transparent=False
    S.world=bpy.data.worlds.new('Dim atmospheric ambient');S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.20,.25,.3,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.18
    S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=.45
    S.render.image_settings.color_depth='8';S.render.fps=30
def main():
    architecture(args.phase=='slice');bench()
    from slice_detail import details
    details(sys.modules[__name__])
    from wear import author
    author(sys.modules[__name__])
    if args.phase=='full':
        from hall import build_hall
        build_hall(sys.modules[__name__])
    cameras();settings();S['section_id']='turbine-room';S['source_revision']=args.revision;S['build_phase']=args.phase
    import hashlib
    S['authoring_source_sha256']=json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')})
    S['support_registry']=json.dumps(SUPPORT);S['camera_contract']=json.dumps(CAMERAS);S['supplementary_cameras']=json.dumps(SUPPLEMENT)
    out=P/'production'/'renders'/'review'/args.revision;out.mkdir(parents=True,exist_ok=True)
    (P/'production'/'cameras.json').write_text(json.dumps(CAMERAS,indent=2))
    import shutil
    checkpoint=P/'production'/'checkpoints'/args.revision;checkpoint.mkdir(parents=True,exist_ok=True)
    for source in Path(__file__).parent.glob('*.py'):shutil.copy2(source,checkpoint/source.name)
    (out/'build_manifest.json').write_text(json.dumps({'phase':args.phase,'revision':args.revision,'objects':len(S.objects),'cameras':CAMERAS,'source':'blender/build.py + blender/hall.py','imports':[],'support_anchors':len(SUPPORT)},indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(P/'blender'/'turbine-room.blend'),compress=True)
    if args.render:
        from render import render_set
        render_set(P,args.revision,args.render,args.samples)
if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).parent));main()
