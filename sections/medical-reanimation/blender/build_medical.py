"""Original OCRU room. Blender 5.2; factory-empty, deterministic, no asset imports.
Run through run.ps1. All dimensions metres. Native Blender + Python only.
"""
import bpy, math, json, sys, argparse, random
from pathlib import Path
from mathutils import Vector
from math import sin, cos, pi

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('--phase', default='slice', choices=['slice','full'])
ap.add_argument('--revision', default='s01')
ap.add_argument('--cameras', default='C00_slice')
ap.add_argument('--samples', type=int, default=32)
ap.add_argument('--width', type=int, default=1280)
ap.add_argument('--render', action='store_true')
ap.add_argument('--cpu', action='store_true')
args = ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
random.seed(841)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system='METRIC'
scene.unit_settings.length_unit='METERS'
scene.render.engine='CYCLES'
scene.cycles.samples=args.samples
scene.cycles.use_denoising=True
scene.cycles.seed=841
scene.render.resolution_x=args.width
scene.render.resolution_y=round(args.width*0.625)
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.world=bpy.data.worlds.new('Soft industrial ambient')
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.20,0.25,0.3,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.10
scene.render.film_transparent=False
scene['section']='medical-reanimation'
scene['revision']=args.revision
scene['source']='blender/build_medical.py'
COL=None
ANCHORS=[]

def collection(name):
    global COL
    COL=bpy.data.collections.new(name); scene.collection.children.link(COL)
    return COL

def finish(o,name,mat=None):
    o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    COL.objects.link(o)
    if mat: o.data.materials.append(mat)
    o['construction']='component; support via connected assembly'
    return o

def material(name,color,rough=.65,metal=0,texture=0,emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1);m.use_nodes=True
    n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if emission:
        p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
    if texture:
        tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=texture;tex.inputs['Detail'].default_value=1.5
        coords=n.new('ShaderNodeTexCoord');m.node_tree.links.new(coords.outputs['Object'],tex.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.15;ramp.color_ramp.elements[1].position=.85
        ramp.color_ramp.elements[0].color=(*(v*(.77 if name in ['plaster','floor'] else .97 if name=='steel' else .90) for v in color),1)
        ramp.color_ramp.elements[1].color=(*(min(v*(1.01 if name=='steel' else 1.045),1) for v in color),1)
        m.node_tree.links.new(tex.outputs['Fac'],ramp.inputs[0]);m.node_tree.links.new(ramp.outputs[0],p.inputs['Base Color'])
        rr=n.new('ShaderNodeMapRange');rr.inputs['From Min'].default_value=.15;rr.inputs['From Max'].default_value=.85
        rr.inputs['To Min'].default_value=max(.05,rough-(.015 if name=='steel' else .085));rr.inputs['To Max'].default_value=min(1,rough+(.015 if name=='steel' else .06))
        m.node_tree.links.new(tex.outputs['Fac'],rr.inputs['Value']);m.node_tree.links.new(rr.outputs['Result'],p.inputs['Roughness'])
        fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=90 if texture<10 else texture;fine.inputs['Detail'].default_value=2
        m.node_tree.links.new(coords.outputs['Object'],fine.inputs['Vector'])
        bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.0025 if name in ['floor','plaster','concrete'] else .00065
        m.node_tree.links.new(fine.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs[0],p.inputs['Normal'])
    return m

M={}
for k,c,r,met,t in [
 ('plaster',(.57,.525,.445),.88,0,.85),('concrete',(.24,.27,.26),.9,0,3),
 ('floor',(.285,.28,.255),.80,0,1.8),('teal',(.025,.105,.12),.50,.3,4),
 ('ivory',(.7,.72,.64),.49,.15,4),('steel',(.34,.39,.39),.27,.9,5),
 ('dark',(.055,.078,.08),.56,.5,4),('rubber',(.026,.032,.032),.91,0,42),
 ('orange',(.65,.25,.067),.57,.12,0),('yellow',(.67,.49,.12),.6,.1,0),
 ('red',(.40,.044,.029),.46,.05,0),('fabric',(.10,.16,.15),.95,0,55),
 ('paper',(.77,.735,.61),.9,0,0),('ink',(.08,.125,.12),.84,0,0),
 ('vinyl',(.13,.23,.21),.7,0,18),('scuff',(.23,.27,.25),.93,0,0),
 ('glass',(.17,.30,.30),.24,.15,0),('screen',(.013,.047,.043),.32,.1,0)]:
    M[k]=material(k,c,r,met,t)
M['lamp']=material('warm practical diffuser',(.90,.85,.65),.5,0,0,3)
M['led']=material('muted status green',(.23,.66,.45),.45,0,0,1.4)
M['amber']=material('amber pilot lens',(.95,.39,.06),.4,0,0,1.5)
M['glass'].node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.75
M['steel'].node_tree.nodes.get('Principled BSDF').inputs['Anisotropic'].default_value=.45
M['fabric'].node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.32
M['linen']=material('cotton linen',(.43,.405,.335),.98,0,75)
M['linen'].node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.25
M['glove']=material('used nitrile rubber',(.39,.23,.07),.82,0,24)
M['bristle']=material('stiff polymer bristles',(.13,.16,.145),.88,0,0)

def bevel(o,w,segments=3):
    if w:
        b=o.modifiers.new('Manufactured edge radius','BEVEL');b.width=w;b.segments=segments
        b=o.modifiers.new('Face-weighted normals','WEIGHTED_NORMAL');b.keep_sharp=True
    return o

def box(name,loc,size,mat='teal',b=.01):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object
    o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(o,name,M.get(mat,mat));bevel(o,b);return o

def cyl(name,loc,r,depth,mat='steel',axis='Z',verts=40):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc)
    o=finish(bpy.context.object,name,M.get(mat,mat))
    if axis=='Y':o.rotation_euler[0]=pi/2
    if axis=='X':o.rotation_euler[1]=pi/2
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    bevel(o,.004,2);return o

def sphere(name,loc,scale,mat='rubber'):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=loc)
    o=finish(bpy.context.object,name,M[mat]);o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for p in o.data.polygons:p.use_smooth=True
    return o

def soft_pad(name,loc,dim,mat='fabric',bulge=.014):
    # Closed sewn cushion/towel with flattened contact base and broad yielding top.
    cx,cy,cz=loc;w,l,h=dim;N=12;verts=[];faces=[]
    for side in [0,1]:
        for j in range(N+1):
            v=j/N
            for i in range(N+1):
                u=i/N;a=2*u-1;b=2*v-1
                x=cx+a*w*.5*(1-.035*abs(b)**8);y=cy+b*l*.5*(1-.035*abs(a)**8)
                z=cz-h*.5 if not side else cz+h*.5+bulge*(1-a**4)*(1-b**4)+.002*sin(u*pi*3)*sin(v*pi)
                verts.append((x,y,z))
    K=(N+1)**2
    for s in [0,1]:
        for j in range(N):
            for i in range(N):
                a=s*K+j*(N+1)+i;f=(a,a+1,a+N+2,a+N+1);faces.append(f if s else tuple(reversed(f)))
    ring=list(range(N+1))+[j*(N+1)+N for j in range(1,N+1)]+[N*(N+1)+i for i in range(N-1,-1,-1)]+[j*(N+1) for j in range(N-1,0,-1)]
    for i,a in enumerate(ring):b=ring[(i+1)%len(ring)];faces.append((a,b,b+K,a+K))
    o=mesh(name,verts,faces,mat,.005)
    for p in o.data.polygons:p.use_smooth=True
    return o

def mesh(name,verts,faces,mat,b=0):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new(name,me);COL.objects.link(o);o.data.materials.append(M[mat]);o['construction']='authored connected component';bevel(o,b);return o

def tube(name,pts,r=.018,mat='steel',cyclic=False):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=16;cu.bevel_depth=r;cu.bevel_resolution=3;cu.use_fill_caps=True
    sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
    for v,p in zip(sp.points,pts):v.co=(*p,1)
    sp.use_cyclic_u=cyclic;o=bpy.data.objects.new(name,cu);COL.objects.link(o);cu.materials.append(M[mat]);o['construction']='continuous pipe or seam';return o

def beam(name,a,b,r=.015,mat='steel'):
    mid=(Vector(a)+Vector(b))*.5;o=cyl(name,mid,r,(Vector(b)-Vector(a)).length,mat)
    o.rotation_euler=(Vector(b)-Vector(a)).to_track_quat('Z','Y').to_euler();return o

def text(name,body,loc,size=.09,mat='paper',rot=(pi/2,0,0),align='LEFT'):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.extrude=.0002;cu.align_x=align
    o=bpy.data.objects.new(name,cu);COL.objects.link(o);cu.materials.append(M[mat]);o.location=loc;o.rotation_euler=rot;o['construction']='applied ink / text';return o

def support(o,target,point,direction=(0,0,-1),gap=.005,penetration=.002):
    o['support_target']=target.name;o['support_anchor']=list(point);o['support_direction']=list(direction)
    o['support_gap_tolerance']=gap;o['support_penetration_tolerance']=penetration
    ANCHORS.append(o)

def bolts_y(name,x,y,z,w,h,mat='steel'):
    for dx in [-w/2,w/2]:
        for dz in [-h/2,h/2]:cyl(name,(x+dx,y,z+dz),.015,.008,mat,'Y',12)

def chip(name,center,w,h,face='Y',mat='steel'):
    # Authored localized edge damage, placed only where hands/carts hit.
    x,y,z=center;shape=[(-.50,-.28),(-.39,.21),(-.16,.36),(.13,.48),(.50,.29),(.40,-.12),(.12,-.37),(-.2,-.49)]
    vs=[(x+u*w,y,z+v*h) if face=='Y' else (x,y+u*w,z+v*h) for u,v in shape]
    return mesh(name,vs,[tuple(range(len(vs)))],mat)

def wall_sign(name,body,x,y,z,w=.8,h=.3,fontsize=.10):
    o=box(name,(x,y,z),(w,.018,h),'teal',.004)
    text(name+' legend',body,(x,y-.010,z-fontsize*.32),fontsize,'paper',align='CENTER')
    bolts_y(name+' fixings',x,y-.016,z,w-.045,h-.045)
    return o

def light(name,loc,target,power,color=(1,.88,.70),size=2.0):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);COL.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o

def practical(x,y,z,length=1.3,power=230):
    shell=box('Suspended steel luminaire',(x,y,z),(length,.22,.10),'dark',.025)
    box('Prismatic diffuser',(x,y,z-.053),(length-.08,.16,.025),'lamp',.009)
    for dx in [-length*.35,length*.35]:beam('Fixture drop',(x+dx,y,z+.05),(x+dx,y,3.6),.009)
    l=light('Practical pool',(x,y,z-.11),(x,y,0),power,(1,.91,.79),size=length)
    l.data.shape='RECTANGLE';l.data.size=length;l.data.size_y=.16
    return shell

collection('01 Architecture | metric shell')
floor=box('Finished seamless resin slab',(0,4.5,-.10),(8,9,.2),'floor',0)
west=box('West reinforced plaster wall',(-4.12,4.5,1.8),(.24,9,3.6),'plaster',.015)
frontparts=[]
for x in [-2.55,2.55]:frontparts.append(box('Entry solid pier',(x,-.12,1.8),(2.9,.24,3.6),'plaster',.015))
fronthead=box('Door lintel',(0,-.12,3.05),(2.2,.24,1.1),'plaster',.012)
ceiling=box('Ceiling soffit',(0,1.65,3.69),(8,3.3,.18),'concrete',.01)
for y in [.07,3.2]:
    box('Ceiling steel channel',(0,y,3.43),(8,.12,.20),'dark',.008)
box('West coved skirting',(-3.965,4.5,.10),(.07,9,.20),'dark',.025)
box('West cart buffer',(-3.92,4.5,.91),(.16,9,.14),'teal',.025)
for x in [-2.55,2.55]:box('Front coved skirting',(x,.035,.10),(2.9,.07,.20),'dark',.025)
for y in [0,2.75]:
    box('Wash zone expansion strip',(0,y,.001),(7.9,.013,.002),'dark',0)
for i in range(24):
    x=random.uniform(-1.2,.9);y=random.uniform(.25,2.7)
    o=box('Sparse wheel scuff',(x,y,.002),(random.uniform(.015,.030),random.uniform(.06,.30),.0006),'scuff',0);o.rotation_euler[2]=random.uniform(-.12,.12)
collection('02 Entry | telescoping rescue door')
for x in [-1.15,1.15]:
    o=box('Door steel jamb',(x,0,1.26),(.10,.30,2.52),'dark',.012);support(o,floor,(x,0,0))
    box('Door rubber seal',(x+(.039 if x<0 else -.039),.04,1.24),(.018,.12,2.46),'rubber',.004)
box('Door track hood',(0,.03,2.61),(2.60,.30,.18),'teal',.025)
for x in [-1.74,1.74]:
    o=box('Parked sliding leaf',(x,.175,1.245),(1.10,.11,2.49),'teal',.035)
    box('Door kick plate',(x,.239,.30),(.96,.015,.42),'steel',.005)
    box('Recessed observation rim',(x,.245,1.71),(.48,.025,.66),'dark',.045)
    box('Observation glass',(x,.261,1.71),(.40,.010,.58),'glass',.035)
    box('Pull recess',(x+(.34 if x<0 else -.34),.247,1.04),(.14,.03,.29),'rubber',.018)
    hx=x+(.34 if x<0 else -.34)
    tube('Recessed door pull',[(hx,.261,.94),(hx,.296,.96),(hx,.296,1.13),(hx,.261,1.15)],.014)
    for z in [.58,2.11]:box('Door panel folded seam',(x,.235,z),(1.02,.012,.011),'dark',.002)
    for z in [.63,2.08]:
        for dx in [-.46,.46]:cyl('Door removable panel screw',(x+dx,.242,z),.009,.008,'steel','Y',12)
    for i in range(6):
        z=.99+i*.023;box('Localized pull wear',(hx-.07+random.uniform(-.014,.018),.239,z),(.007,.003,random.uniform(.008,.032)),'steel',.001)
    for i in range(10):
        px=x+(.48 if i<6 else -.48)+random.uniform(-.017,.008)
        pz=.63+random.uniform(0,.22) if i<6 else 1.1+random.uniform(-.20,.25)
        chip('Door edge primer exposed',(px,.231,pz),random.uniform(.009,.026),random.uniform(.018,.065),'Y','paper')
    for i in range(5):
        chip('Kickplate cart scratch',(x+random.uniform(-.35,.35),.249,.28+random.uniform(-.12,.12)),random.uniform(.02,.11),.004,'Y','dark')
    # Door-facing-in lettering, local text normal +Y.
    text('Sliding leaf number','03',(x,.239,2.22),.14,'paper',(pi/2,0,pi),align='CENTER')
box('Flush crossing threshold',(0,0,.004),(2.2,.34,.008),'steel',.004)
text('Entry department title','ORGANIC CONTINUITY',(0,.017,2.96),.145,'ink',(pi/2,0,pi),align='CENTER')
collection('03 Gross decontamination | fitted wash station')
# Basin is a thick formed annulus with a depressed inner bowl, not a solid block.
cx,cy=-3.40,1.65
verts=[]
for z,rx,ry in [(1.01,.49,.59),(1.01,.41,.50),(.77,.31,.40),(.75,.33,.42),(.99,.49,.59)]:
    for i in range(48):
        a=2*pi*i/48;verts.append((cx+rx*cos(a),cy+ry*sin(a),z))
faces=[]
for j in range(4):
    for i in range(48):faces.append((j*48+i,j*48+(i+1)%48,(j+1)*48+(i+1)%48,(j+1)*48+i))
faces.append(tuple(2*48+i for i in range(48)))
faces.append(tuple(3*48+i for i in range(47,-1,-1)))
for i in range(48):faces.append((4*48+i,4*48+(i+1)%48,(i+1)%48,i))
basin=mesh('Pressed stainless wash basin',verts,faces,'steel',.006)
for p in basin.data.polygons:p.use_smooth=True
cyl('Basin drain',(cx,cy,.782),.035,.008,'dark')
for y in [1.38,1.92]:
    tube('Triangular wall bracket',[(-3.97,y,.48),(-3.4,y,.732),(-3.97,y,.732)],.018)
    foot=box('Basin bracket wall plate',(-3.987,y,.77),(.026,.12,.34),'steel',.006);support(foot,west,(-4,y,.77),(-1,0,0))
tube('Trapped basin drain',[(cx,cy,.77),(cx,cy,.45),(-3.6,cy,.33),(-3.78,cy,.43),(-4.01,cy,.43)],.032)
for z in [.58,.75]:cyl('Wastepipe compression nut',(cx,cy,z),.042,.040,'steel',verts=8)
for y in [1.38,1.92]:
    for z in [.66,.86]:cyl('Basin bracket anchor',(-3.968,y,z),.016,.020,'dark','X',12)
tube('Swan neck tap',[(-3.72,1.95,1.01),(-3.72,1.95,1.29),(-3.60,1.95,1.38),(-3.4,1.95,1.38),(-3.36,1.95,1.25)],.019)
for y in [1.82,2.06]:
    cyl('Ceramic isolation tap',(-3.76,y,1.055),.042,.05,'ivory');box('Tap lever',(-3.69,y,1.09),(.17,.035,.022),'steel',.006)
profile=[(.94,.96),(.94,1.48),(1.10,1.65),(2.20,1.65),(2.36,1.48),(2.36,.96)]
verts=[(x,y,z) for x in [-4,-3.969] for y,z in profile]
faces=[tuple(range(5,-1,-1)),tuple(range(6,12))]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]
o=mesh('Formed enamel decon backsplash',verts,faces,'teal',.008);support(o,west,(-4,1.65,1.26),(-1,0,0))
tube('Backsplash folded perimeter',[(-3.963,y,z) for y,z in profile],.008,'teal',True)
for y in [1.02,2.28]:
    for z in [1.06,1.43]:cyl('Backsplash captive screw',(-3.951,y,z),.013,.016,'steel','X',12)
for y,z in [(1.01,1.07),(1.10,.978),(1.28,.978),(1.51,.977),(2.29,1.06),(2.25,1.58)]:
    chip('Enamel edge wear',(-3.951,y,z),.035,.010,'X','paper')
text('Wash zone identification','GROSS RINSE',(-3.946,1.18,1.555),.040,'paper',(pi/2,0,pi/2))
for y in [1.38,1.92]:
    vs=[(x,yy,z) for yy in [y-.008,y+.008] for x,z in [(-3.978,.48),(-3.978,.75),(-3.4,.75)]]
    mesh('Pressed triangular basin gusset',vs,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'teal',.005)
o=box('Hose utility riser',(-3.925,.62,1.19),(.15,.11,1.18),'teal',.02);support(o,west,(-4,.62,1.19),(-1,0,0))
pts=[(-3.86,.62,.97),(-3.70,.62,.90)]
for i in range(121):
    t=i/120;a=t*pi*12;pts.append((-3.66+.045*cos(a),.65+.05*sin(a),.90+t*.70))
pts.extend([(-3.61,.61,1.64),(-3.60,.61,1.66)])
tube('Coiled rinse hose',pts,.012,'rubber')
beam('Spray grip',(-3.60,.61,1.65),(-3.66,.61,1.77),.027,'ivory')
cyl('Spray barrel',(-3.59,.61,1.775),.032,.16,'ivory','X')
cyl('Spray nozzle ferrule',(-3.505,.61,1.775),.026,.024,'steel','X')
cyl('Spray perforated face',(-3.489,.61,1.775),.021,.007,'dark','X')
beam('Spray thumb trigger',(-3.63,.587,1.70),(-3.595,.587,1.746),.009,'orange')
box('Wall hose cradle',(-3.92,.61,1.65),(.16,.14,.15),'teal',.008)
tube('Rinse supply pipe',[(-4,.62,2.98),(-3.86,.62,2.98),(-3.86,.62,2.08),(-3.86,.62,1.72)],.021,'steel')
for z in [2.24,2.82]:
    o=box('Rinse pipe saddle',(-3.94,.62,z),(.12,.075,.042),'dark',.006);support(o,west,(-4,.62,z),(-1,0,0))
cyl('Rinse isolator stem',(-3.79,.62,2.08),.042,.10,'steel','X')
wheelpts=[(-3.73,.62+.093*cos(i*pi/24),2.08+.093*sin(i*pi/24)) for i in range(48)]
tube('Rinse isolation handwheel',wheelpts,.011,'teal',True)
for a in [0,2*pi/3,4*pi/3]:beam('Handwheel spoke',(-3.73,.62,2.08),(-3.73,.62+.08*cos(a),2.08+.08*sin(a)),.008,'teal')
cyl('Rinse pressure instrument case',(-3.80,.62,2.46),.091,.11,'dark','X')
cyl('Pressure dial ivory face',(-3.741,.62,2.46),.078,.012,'paper','X')
for i in range(13):
    a=-.75*pi+i*1.5*pi/12
    beam('Pressure dial graduation',(-3.732,.62+.057*sin(a),2.46+.057*cos(a)),(-3.732,.62+.069*sin(a),2.46+.069*cos(a)),.0018,'ink')
beam('Pressure pointer',(-3.724,.62,2.46),(-3.724,.58,2.50),.003,'red')
cyl('Dial center pin',(-3.72,.62,2.46),.006,.006,'steel','X')
for x in [-.87,.87]:box('Decon mat edge',(x,1.1,.008),(.025,1.65,.016),'yellow',.002)
box('Flush perforated wash grate',(0,1.1,.008),(1.70,1.65,.016),'rubber',.014)
for y in [0.36+i*.10 for i in range(16)]:box('Grate tread',(0,y,.018),(1.62,.014,.012),'steel',.002)
box('Drain rim',(-1.29,1.65,.01),(.20,1.24,.02),'steel',.004)
for y in [1.12+i*.07 for i in range(16)]:box('Drain slot',(-1.29,y,.021),(.155,.028,.003),'dark',.004)
practical(-2.9,1.40,3.21,1.4,240)
light('Entry bounce',(1.8,1.8,2.7),(-3.3,1.6,.8),28,(.75,.88,1),2)
for z in [1.48]:
    cut=box('temporary joint cutter',(-4,4.5,z),(.012,9,.014),'concrete',0)
    mod=west.modifiers.new('Recessed horizontal panel joint','BOOLEAN');mod.object=cut;mod.operation='DIFFERENCE'
    bpy.context.view_layer.objects.active=west;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
for y in [2.97,5.97]:
    cut=box('temporary joint cutter',(-4,y,1.8),(.012,.014,3.6),'concrete',0)
    mod=west.modifiers.new('Recessed vertical panel joint','BOOLEAN');mod.object=cut;mod.operation='DIFFERENCE'
    bpy.context.view_layer.objects.active=west;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
box('Localized wall repair',(-3.996,2.83,.46),(.006,.15,.09),'plaster',.003)
collection('04 Human detail | decon')
# 4 lived-in props: towel, pump bottle, brush, dated procedure card.
shelf=box('Towel shelf folded sheet',(-3.67,2.40,1.025),(.66,.38,.028),'ivory',.008);support(shelf,west,(-4,2.40,1.025),(-1,0,0))
box('Shelf front return',(-3.348,2.40,1.00),(.016,.38,.035),'ivory',.005)
cross=[]
for i in range(19):cross.append((-3.90+i*.43/18,1.043))
for i in range(1,19):
    a=-pi/2+i*pi/18;cross.append((-3.47+.021*cos(a),1.064+.021*sin(a)))
for i in range(1,19):cross.append((-3.47-i*.395/18,1.085))
verts=[];faces=[];N=22
for j,(x,z) in enumerate(cross):
    t=j/(len(cross)-1)
    for i in range(N+1):
        u=i/N;y=2.255+u*.29+.003*sin(t*pi*3+u*pi)
        zz=z+(.005*sin(u*pi*2.3)+.003*sin(u*pi*5))*sin(t*pi*.5)**2
        xx=x+(.012*sin(u*pi*1.3)+.005*sin(u*pi*4))*t**3
        verts.append((xx,y,zz))
for j in range(len(cross)-1):
    for i in range(N):a=j*(N+1)+i;faces.append((a,a+1,a+N+2,a+N+1))
o=mesh('Folded linen towel',verts,faces,'linen');sol=o.modifiers.new('Woven towel thickness','SOLIDIFY');sol.thickness=.004
for p in o.data.polygons:p.use_smooth=True
support(o,shelf,(-3.8,2.4,1.041))
for edge in [1,N-1]:tube('Folded towel sewn edge',[verts[j*(N+1)+edge] for j in range(len(cross))],.0012,'ivory')
cyl('Rinse bottle',(-3.69,1.12,1.13),.056,.23,'ivory');cyl('Bottle pump collar',(-3.69,1.12,1.26),.023,.035,'dark')
box('Rinse bottle label',(-3.633,1.12,1.135),(.002,.070,.10),'paper',.001)
text('Rinse bottle batch','RINSE\nR-03',(-3.631,1.092,1.16),.017,'ink',(pi/2,0,pi/2))
tube('Bottle spout',[(-3.69,1.12,1.285),(-3.59,1.12,1.285),(-3.59,1.12,1.27)],.009,'dark')
brush=box('Cleaning brush',(-3.41,1.15,1.038),(.21,.08,.026),'orange',.028)
for i in range(8):
    for j in range(5):cyl('Brush bristle tuft',(-3.5+i*.025,1.125+j*.012,1.059+random.uniform(-.002,.002)),.0027,.022,'bristle',verts=8)
board=box('Decon procedure clipboard',(-3.990,2.62,1.71),(.020,.27,.36),'dark',.01);support(board,west,(-4,2.62,1.71),(-1,0,0))
paper=box('Revised paper form',(-3.978,2.62,1.71),(.004,.24,.32),'paper',.002);support(paper,board,(-3.98,2.62,1.71),(-1,0,0))
text('Decon form','RINSE / RETURN\n\nUnit 03 / 07 SEP\nInitials: HN\n\nRest is not\nrestart time.',(-3.975,2.51,1.82),.023,'ink',(pi/2,0,pi/2))
# Fabric hand towel with gravity drape, rolled hem and stitched stripe.
rod=tube('Towel rail',[(-4,2.80,1.12),(-3.71,2.80,1.12),(-3.71,3.20,1.12),(-4,3.20,1.12)],.012)
verts=[];faces=[]
for j in range(25):
    v=j/24
    for i in range(19):
        u=i/18;y=2.85+u*.30
        x=-3.696+.008*sin(u*pi*3.3)*(0.4+v)+.013*v*v
        z=1.12-v*.46+.018*sin(u*pi*1.4)*v
        verts.append((x,y,z))
for j in range(24):
    for i in range(18):a=j*19+i;faces.append((a,a+1,a+20,a+19))
o=mesh('Hanging linen towel',verts,faces,'linen');mod=o.modifiers.new('Woven fabric thickness','SOLIDIFY');mod.thickness=.003
for p in o.data.polygons:p.use_smooth=True
tube('Towel sewn hem',[(-3.683+.0112*sin(i*pi*3.3/18),2.85+i*.30/18,.665+.018*sin(i*pi*1.4/18)) for i in range(19)],.002,'ivory')
box('Clipboard metal spring clip',(-3.970,2.62,1.87),(.012,.075,.025),'steel',.004)
# Maintained contaminated-linen bin. Rolled rim, lid hinge, foot pedal and used glove.
binbase=cyl('Linen bin rubber plinth',(-3.57,.32,.043),.225,.086,'rubber');support(binbase,floor,(-3.57,.32,0))
cyl('Pressed metal linen drum',(-3.57,.32,.325),.216,.48,'ivory',verts=64)
for z in [.10,.55]:tube('Bin rolled bead',[(-3.57+.218*cos(i*pi/32),.32+.218*sin(i*pi/32),z) for i in range(64)],.009,'steel',True)
lid=cyl('Hinged linen-bin lid',(-3.57,.32,.580),.235,.042,'teal',verts=64)
box('Lid hinge',(-3.77,.32,.575),(.07,.15,.06),'steel',.008)
box('Foot pedal',(-3.285,.32,.052),(.20,.13,.023),'dark',.008)
beam('Pedal linkage',(-3.77,.32,.08),(-3.77,.32,.55),.009)
tube('Bin lid grip',[(-3.54,.26,.60),(-3.50,.26,.636),(-3.50,.38,.636),(-3.54,.38,.60)],.010,'steel')
# Glove rests on the lid; broad molded palm and five relaxed bent fingers.
sphere('Discarded cleaning glove palm',(-3.55,.33,.621),(.080,.056,.018),'glove')
for i,ln in enumerate([.078,.102,.11,.095]):
    y=.29+i*.026
    tube('Glove finger',[(-3.49,y,.626),(-3.46,y,.625),(-3.46+ln*.4,y+.005,.614)],.013,'glove')
    sphere('Closed glove fingertip',(-3.46+ln*.4,y+.005,.614),(.013,.013,.013),'glove')
tube('Glove thumb',[(-3.56,.28,.625),(-3.52,.235,.622),(-3.49,.230,.615)],.018,'glove')
sphere('Closed thumb tip',(-3.49,.230,.615),(.018,.018,.015),'glove')
box('Bin modest inventory mark',(-3.343,.32,.365),(.003,.075,.065),'yellow',.003)
for i in range(5):
    o=box('Localized pedal scuff',(-3.3+random.uniform(-.04,.04),.32+random.uniform(-.03,.03),.064),(.025,.004,.001),'steel',0)

CAMERAS={
 'C00_slice':((1.65,3.25,1.66),(-2.0,.62,1.47),22),
 'C00b_workstation':((-.75,2.95,1.62),(-3.55,1.53,1.10),38),
 'C01_entry':((0,.34,1.68),(.1,6.0,1.23),22),
 'C02_hero':((-2.65,3.45,1.66),(.60,6.3,1.18),29),
 'C03_reverse':((2.82,8.40,1.67),(-.1,2.10,1.12),23),
 'C04_route':((-1.95,1.95,1.65),(.80,5.60,.9),24),
 'C05_controls':((-2.40,5.00,1.55),(-.30,6.20,1.22),42),
 'C06_service':((2.6,8.6,1.60),(-.25,7.25,1.1),28),
 'C07_recovery':((3.05,4.3,1.64),(5.15,6.90,1.05),27),
 'C08_decon':((1.5,3.05,1.66),(-2.1,.58,1.25),24),
 'C09_materials':((-2.2,7.7,1.48),(-3.53,7.15,1.05),44),
 'C10_clearance':((3.15,2.92,1.68),(2.12,7.18,.85),23),
}

def make_cameras():
    collection('90 Evidence cameras | fixed transforms')
    for name,(loc,target,lens) in CAMERAS.items():
        d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);COL.objects.link(o);o.location=loc
        o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.05;d.clip_end=100
        if name=='C00_slice' and args.phase=='full':o.hide_render=True
    scene.camera=bpy.data.objects['C00_slice' if args.phase=='slice' else 'C01_entry']

# Full-room expansion is added only after independent slice approval.
if args.phase=='full':
    exec(compile((ROOT/'blender/full_room.py').read_text(),str(ROOT/'blender/full_room.py'),'exec'))
make_cameras()
bpy.context.view_layer.update()
scene['support_registry_count']=len(ANCHORS)
scene['phase']=args.phase
out=ROOT/'production/renders/review'/args.revision;out.mkdir(parents=True,exist_ok=True)
(ROOT/'production/cameras.json').write_text(json.dumps(CAMERAS,indent=2))
blend=ROOT/'blender'/('medical_reanimation.blend' if args.phase=='full' else 'style_slice.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
exec(compile((ROOT/'blender/validate.py').read_text(),str(ROOT/'blender/validate.py'),'exec'))
if args.render:
    prefs=bpy.context.preferences.addons['cycles'].preferences
    try:
        prefs.compute_device_type='HIP';prefs.get_devices()
        for d in prefs.devices:d.use=d.type=='HIP'
        scene.cycles.device='GPU' if any(d.use for d in prefs.devices) and not args.cpu else 'CPU'
    except Exception:scene.cycles.device='CPU'
    print('MEDICAL_RENDER_DEVICE',scene.cycles.device,flush=True)
    for name in args.cameras.split(','):
        scene.camera=bpy.data.objects[name];scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    print('MEDICAL_RENDER_COMPLETE',args.revision,flush=True)
