"""Compliance Dock. Original geometry, factory-empty, metric, deterministic.
Run using run.ps1; every render is serialized by the shared facility GPU gate.
"""
import bpy, math, json, sys, argparse, random, hashlib
from pathlib import Path
from mathutils import Vector
from math import sin, cos, pi

ROOT = Path(__file__).resolve().parents[1]
random.seed(8217)
p=argparse.ArgumentParser()
p.add_argument('--stage', default='slice', choices=['slice','full'])
p.add_argument('--revision', default='s01')
p.add_argument('--render', default='')
p.add_argument('--samples', type=int, default=48)
p.add_argument('--width', type=int, default=1440)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene
S.unit_settings.system='METRIC'; S.unit_settings.scale_length=1
COL=None; ASM=None; MATERIALS={}; CONTACTS=[]

def collection(name):
    global COL, ASM
    COL=bpy.data.collections.new(name); S.collection.children.link(COL); ASM=None
    return COL

def put(o,name,mat=None,block=False):
    o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    COL.objects.link(o)
    if mat: o.data.materials.append(MATERIALS[mat] if isinstance(mat,str) else mat)
    if ASM: o.parent=ASM; o['assembly']=ASM.name
    o['circulation_solid']=block
    o['support_class']='assembly_component' if ASM else 'architectural'
    return o

def bevel(o,w=.01,seg=3):
    if w:
        b=o.modifiers.new('Manufactured edge radius','BEVEL'); b.width=w; b.segments=seg
        b.limit_method='ANGLE'
        n=o.modifiers.new('Face weighted normals','WEIGHTED_NORMAL'); n.keep_sharp=True; n.weight=40
    return o

def box(name,loc,dims,mat,w=.008,block=False):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=put(bpy.context.object,name,mat,block); o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return bevel(o,w)

def mesh(name,verts,faces,mat,w=0,block=False):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    o=bpy.data.objects.new(name,me); COL.objects.link(o)
    if mat: me.materials.append(MATERIALS[mat])
    if ASM: o.parent=ASM; o['assembly']=ASM.name
    o['support_class']='assembly_component' if ASM else 'architectural'
    o['circulation_solid']=block
    return bevel(o,w)

def profile(name,pts,depth,axis,offset,mat,w=.008,block=False):
    # Extruded authored section: pts in the other two coordinate axes.
    other=[i for i in range(3) if i!=axis]; vs=[]
    for d in [-depth/2,depth/2]:
        for q in pts:
            v=list(offset); v[axis]+=d
            v[other[0]]+=q[0]; v[other[1]]+=q[1]; vs.append(v)
    n=len(pts); fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    fs += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    o=mesh(name,vs,fs,mat,w,block)
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT'); o.select_set(False)
    return o

def cyl(name,loc,r,depth,mat,axis='Z',vertices=32,w=.003):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc)
    o=put(bpy.context.object,name,mat)
    if axis=='X': o.rotation_euler[1]=pi/2
    if axis=='Y': o.rotation_euler[0]=pi/2
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bevel(o,w,2)
    for f in o.data.polygons: f.use_smooth=(len(f.vertices)==4)
    return o

def line(name,points,r,mat):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=16; cu.bevel_depth=r; cu.bevel_resolution=3
    sp=cu.splines.new('POLY'); sp.points.add(len(points)-1)
    for v,co in zip(sp.points,points): v.co=(*co,1)
    o=bpy.data.objects.new(name,cu); COL.objects.link(o); cu.materials.append(MATERIALS[mat])
    if ASM: o.parent=ASM; o['assembly']=ASM.name
    o['support_class']='assembly_component' if ASM else 'architectural'
    return o

def tube(name,start,end,r,mat):
    v=Vector(end)-Vector(start)
    o=cyl(name,(Vector(start)+Vector(end))/2,r,v.length,mat)
    o.rotation_euler=v.to_track_quat('Z','Y').to_euler(); return o

def torus(name,loc,major,minor,mat,axis='Z'):
    bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=10,location=loc,major_radius=major,minor_radius=minor)
    o=put(bpy.context.object,name,mat)
    if axis=='X':o.rotation_euler[1]=pi/2
    if axis=='Y':o.rotation_euler[0]=pi/2
    for f in o.data.polygons:f.use_smooth=True
    return o

def txt(name,body,loc,size,mat,rot=(pi/2,0,0),align='LEFT'):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.size=size; cu.extrude=.0003; cu.resolution_u=6; cu.align_x=align
    o=bpy.data.objects.new(name,cu); COL.objects.link(o); o.location=loc; o.rotation_euler=rot; cu.materials.append(MATERIALS[mat])
    if ASM:o.parent=ASM;o['assembly']=ASM.name
    o['support_class']='assembly_component' if ASM else 'architectural'
    return o

def assembly(name,target,anchors,direction=(0,0,-1)):
    global ASM
    o=bpy.data.objects.new(name,None); COL.objects.link(o); ASM=o
    o['support_target']=target; o['support_direction']=direction; o['support_class']='supported_assembly'
    o['max_gap_m']=.005; o['max_penetration_m']=.002; o['angle_tolerance_deg']=12
    for i,pt in enumerate(anchors):
        e=bpy.data.objects.new(name+'__contact_'+str(i),None); COL.objects.link(e);e.location=pt;e.parent=o;e['contact_anchor']=True
    CONTACTS.append(name);return o

def bolt(name,loc,axis='Y',r=.013):
    cyl(name+' washer',loc,r*1.5,.004,'steel',axis,24,.001)
    return cyl(name,loc,r,.013,'steel',axis,6,.001)

def material(name,col,rough,metal=0,variation=.05,bump=.025):
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes; l=m.node_tree.links; bs=n.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    bs.inputs['Specular IOR Level'].default_value=.28 if metal<.2 else .4
    tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2.1;noise.inputs['Detail'].default_value=2
    l.new(tc.outputs['Object'],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.12;ramp.color_ramp.elements[1].position=.85
    ramp.color_ramp.elements[0].color=(*(max(0,c*(1-variation)) for c in col),1)
    ramp.color_ramp.elements[1].color=(*(min(1,c*(1+variation)) for c in col),1)
    l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],bs.inputs['Base Color'])
    mr=n.new('ShaderNodeMapRange');mr.inputs['To Min'].default_value=rough-.045;mr.inputs['To Max'].default_value=min(.99,rough+.045)
    l.new(noise.outputs['Fac'],mr.inputs[0]);l.new(mr.outputs[0],bs.inputs['Roughness'])
    if bump:
        fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=90;fine.inputs['Detail'].default_value=2
        l.new(tc.outputs['Object'],fine.inputs['Vector']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.2;b.inputs['Distance'].default_value=bump
        l.new(fine.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],bs.inputs['Normal'])
    MATERIALS[name]=m;return m

def palette():
    for args in [
        ('plaster',(.59,.535,.43),.88,0,.095,.002),('concrete',(.29,.30,.285),.85,0,.1,.0025),
        ('floor',(.32,.32,.29),.79,0,.075,.0017),('teal',(.07,.18,.185),.61,.32,.07,.00035),
        ('teal_light',(.14,.27,.27),.57,.25,.08,.0004),('frame',(.065,.09,.093),.52,.65,.07,.00025),
        ('steel',(.32,.37,.37),.43,.82,.04,.0002),('rubber',(.022,.027,.026),.93,0,.1,.001),
        ('ivory',(.73,.71,.62),.64,.15,.04,.0003),('yellow',(.71,.39,.065),.62,.1,.045,.0003),
        ('orange',(.57,.165,.055),.69,.18,.04,.0004),('red',(.42,.036,.025),.62,.2,.03,.0002),
        ('paper',(.78,.75,.61),.96,0,.025,0),('ink',(.035,.063,.065),.92,0,.01,0),
        ('fabric',(.30,.29,.22),.95,0,.15,.001),('blue_fabric',(.12,.18,.20),.97,0,.08,.0008),
        ('wear',(.24,.25,.22),.80,.15,.07,0),('ceramic',(.58,.57,.46),.31,0,.02,0),
        ('wood',(.25,.135,.062),.77,0,.13,.001),('lens',(.065,.10,.095),.23,.15,.01,0)]:material(*args)
    for name,col,strength in [('warm_lamp',(1,.8,.54),3),('white_lamp',(.72,.86,1),3),('green_lamp',(.35,.65,.42),1.5),('screen',(.09,.25,.18),.5)]:
        m=material(name,col,.5,0,0,0);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(*col,1);bs.inputs['Emission Strength'].default_value=strength
    m=material('glass',(.84,.92,.90),.065,0,.005,0);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.46
    for node in m.node_tree.nodes:
        if node.type=='MAP_RANGE':node.inputs['To Min'].default_value=.025;node.inputs['To Max'].default_value=.065

def light(name,loc,target,power,color=(1,.83,.64),size=1.2,size_y=None):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='RECTANGLE' if size_y else 'DISK';d.size=size
    if size_y:d.size_y=size_y
    o=bpy.data.objects.new(name,d);COL.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();return o

def camera(name,loc,target,lens=30):
    d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.04;d.clip_end=150
    o=bpy.data.objects.new(name,d);COL.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();return o

def door_front(x,y,name='Staff door',width=1.05,height=2.2):
    assembly(name,'Floor slab',[(x-width/2-.09,y,0),(x+width/2+.09,y,0)])
    # Folded, stepped steel jambs, with a rubber labyrinth seal and a recessed leaf.
    for side in [-1,1]:
        xx=x+side*(width/2+.065)
        box(name+' reveal', (xx,y,height/2),(.13,.23,height),'frame',.009,True)
        box(name+' outer flange',(xx,y-.13,height/2),(.19,.038,height+.10),'teal',.004)
        box(name+' gasket',(x+side*(width/2-.012),y-.069,height/2),(.025,.022,height),'rubber',.003)
        for z in [.17,1.02,2.02]:bolt(name+' frame fixing',(xx,y-.155,z))
    box(name+' head',(x,y,height+.065),(width+.26,.23,.13),'frame',.007,True)
    box(name+' head flange',(x,y-.134,height+.075),(width+.38,.035,.18),'teal',.003)
    leaf=box(name+' leaf',(x,y+.012,height/2),(width-.045,.073,height-.025),'teal',.007,True)
    leaf['interactive']='hinged_door';leaf['hinge_axis']='Z';leaf['hinge_world']=[x-width/2,y,height/2]
    for z,h in [(.39,.42),(1.05,.57),(1.78,.50)]:
        box(name+' pressed shadow',(x,y-.03,z),(width-.21,.012,h),'frame',.008)
        box(name+' pressed infill',(x,y-.043,z+.012),(width-.25,.012,h-.05),'teal_light',.006)
    box(name+' kickplate',(x,y-.059,.30),(width-.10,.006,.43),'steel',.003)
    for xx in [x-width/2+.11,x+width/2-.11]:
        for z in [.12,.48]:bolt(name+' kick rivet',(xx,y-.064,z),r=.005)
    for z in [.28,1.13,1.94]:
        cyl(name+' hinge',(x-width/2+.007,y-.058,z),.025,.15,'steel',w=.002)
        box(name+' hinge strap',(x-width/2+.066,y-.063,z),(.095,.012,.09),'steel',.002)
    box(name+' latch backplate',(x+width/2-.14,y-.071,1.01),(.09,.015,.25),'steel',.007)
    cyl(name+' lock',(x+width/2-.14,y-.087,1.08),.028,.02,'frame','Y')
    line(name+' lever',[(x+width/2-.14,y-.08,.97),(x+width/2-.14,y-.16,.97),(x+width/2-.31,y-.16,.97)],.015,'steel')
    box(name+' closer',(x+.17,y-.1,2.10),(.24,.07,.065),'frame',.008)
    line(name+' closer arm',[(x+.12,y-.14,2.125),(x-.14,y-.25,2.15),(x-.29,y-.13,2.23)],.008,'steel')
    box(name+' threshold',(x,y-.03,.009),(width,.29,.018),'steel',.002)
    # Handle and foot contact scars are selective; the rest remains maintained.
    for i in range(12):
        xx=x+random.uniform(-.38,.35);zz=random.uniform(.16,.34)
        box(name+' kick scar',(xx,y-.063,zz),(random.uniform(.018,.08),.001,random.uniform(.001,.004)),'wear',0)
    box(name+' ID',(x,y-.065,1.77),(.32,.009,.09),'ivory',.002)
    txt(name+' ID text','STAFF', (x,y-.071,1.745),.046,'ink',align='CENTER')
    return leaf

def papers(x,y,z):
    for i in range(4):
        o=box('Manifest paper',(x+.008*i,y+.006*i,z+.0008+i*.0012),(.215,.297,.001),'paper',.0003)
    txt('Manifest title','ARRIVAL / 041', (x-.084,y+.10,z+.0063),.018,'ink',rot=(0,0,0))
    for i in range(9):box('Manifest rule',(x,y+.055-i*.018,z+.006),(.165,.001,.0003),'ink',0)
    for i in range(3):box('Manifest entry',(x-.025,y+.043-i*.041,z+.0063),(.09,.002,.0003),'ink',0)
    cyl('Stamp handle',(x+.15,y-.09,z+.038),.018,.065,'wood',w=.004)
    box('Stamp base',(x+.15,y-.09,z+.009),(.055,.03,.016),'rubber',.003)

def mug(x,y,z):
    pts=[(.029,0),(.033,.012),(.036,.086),(.032,.096),(.027,.096),(.029,.084),(.026,.010),(0,.010),(0,0)]
    vs=[];fs=[];N=40
    for i in range(N):
        for r,h in pts:vs.append((x+r*cos(2*pi*i/N),y+r*sin(2*pi*i/N),z+h))
    n=len(pts)
    for i in range(N):
        for j in range(n-1):fs.append((i*n+j,((i+1)%N)*n+j,((i+1)%N)*n+j+1,i*n+j+1))
    o=mesh('Enamel mug',vs,fs,'ceramic',.001)
    for f in o.data.polygons:f.use_smooth=True
    torus('Mug rolled rim',(x,y,z+.094),.032,.002,'frame')
    line('Mug handle',[(x+.033,y,z+.077),(x+.061,y,z+.074),(x+.071,y,z+.055),(x+.062,y,z+.027),(x+.035,y,z+.025)],.007,'ceramic')
    cyl('Cold tea',(x,y,z+.073),.027,.002,'wood',w=0)

def cloth(name,x,y,z,w=.27,h=.20,mat='blue_fabric'):
    vs=[];fs=[];nx=20;ny=16
    for j in range(ny+1):
        for i in range(nx+1):
            xx=(i/nx-.5)*w;yy=(j/ny-.5)*h
            zz=z+.006+.005*(1+sin(i*.7+j*.27))+.007*(sin(i*.34)**2)
            vs.append((x+xx,y+yy,zz))
    for j in range(ny):
        for i in range(nx):q=j*(nx+1)+i;fs.append((q,q+1,q+nx+2,q+nx+1))
    lowest=min(v[2] for v in vs);vs=[(xx,yy,zz-lowest+z+.0015) for xx,yy,zz in vs]
    o=mesh(name,vs,fs,mat);sol=o.modifiers.new('Hem thickness','SOLIDIFY');sol.thickness=.0015
    if ASM:
        pt=min(vs,key=lambda v:v[2])
        for child in ASM.children:
            if child.get('contact_anchor'):child.location=(pt[0],pt[1],z)
    for f in o.data.polygons:f.use_smooth=True
    return o

def slice_architecture():
    global ASM
    collection('01 Architecture')
    box('Floor slab',(0,7.9,-.15),(14.16,16.36,.30),'floor',.001)
    # Narrow construction-joint inlays, continuous slab surface at z=0.
    for ix in range(7):
        box('Floor longitudinal joint',(-6.8+ix*1.945,7.9,.0003),(.007,15.8,.0006),'concrete',0)
    for iy in range(8):
        box('Floor transverse joint',(0,iy*1.975,.0003),(13.6,.007,.0006),'concrete',0)
    box('West perimeter wall',(-6.94,7.9,2.2),(.28,16.36,4.4),'plaster',.007,True)
    # Front office elevation: door at -5.4, transaction opening at -3.55.
    y=3.6
    for x,w in [(-6.375,.85),(-4.5625,.475),(-2.505,.21)]:box('Office front pier',(x,y,1.525),(w,.16,3.05),'plaster',.006,True)
    box('Office front head',(-4.6,y,2.70),(4.4,.16,.70),'plaster',.007,True)
    box('Hatch wall base',(-3.535,y,.50),(1.77,.16,1.0),'teal_light',.004,True)
    box('Office west ceiling',(-4.6,6.6,3.125),(4.4,6.0,.15),'concrete',.005)
    # Inset wall panels reveal real thickness, and a quiet patched plaster field.
    box('Office transom cap',(-4.6,3.487,2.52),(4.38,.048,.095),'frame',.003)
    for x in [-6.7,-4.36,-2.49]:
        box('Office base shoe',(x,y-.10,.08),(.09,.05,.16),'frame',.003)
    door_front(-5.4,3.6)
    collection('02 Check in')
    assembly('Transaction hatch','Hatch wall base',[(-4.1,3.519,.83),(-3.0,3.519,.83)],(0,1,0))
    for x in [-4.39,-2.63]:
        box('Hatch steel jamb',(x,3.54,1.74),(.075,.13,1.47),'frame',.004)
        box('Hatch satin reveal',(x+.014,3.452,1.76),(.017,.028,1.41),'steel',.002)
    for z in [1.068,1.45,2.43]:box('Hatch horizontal',( -3.51,3.54,z),(1.82,.13,.055),'frame',.003)
    box('Hatch laminated glass',(-3.51,3.555,1.94),(1.72,.012,.94),'glass',.002)
    for x in [-4.1,-3.0]:
        profile('Counter folded bracket',[(-.36,0),(.019,0),(.019,-.31),(-.02,-.31),(-.36,-.055)],.036,0,(x,3.50,.996),'frame',.003)
    counter=box('Transaction counter',(-3.51,3.28,1.019),(1.86,.61,.042),'steel',.006,True)
    box('Counter front rolled lip',(-3.51,2.975,1.01),(1.87,.02,.047),'steel',.007)
    # Pass-through tray has folded lips and a dark replaceable rubber bed.
    box('Rubber transaction mat',(-3.42,3.22,1.043),(.64,.37,.009),'rubber',.004)
    for xx in [-3.74,-3.10]:box('Pass tray lip',(xx,3.22,1.062),(.012,.37,.035),'steel',.003)
    assembly('Manifest and stamp','Transaction counter',[(-4.03,3.16,1.04)])
    papers(-4.03,3.16,1.04)
    assembly('Clerk mug','Transaction counter',[(-2.87,3.29,1.04)])
    mug(-2.87,3.29,1.04)
    assembly('Cleaning cloth','Transaction counter',[(-2.96,3.06,1.04)])
    cloth('Folded cleaning cloth',-2.96,3.10,1.04,.22,.16)
    assembly('Receipt clip','Transaction counter',[(-3.76,3.34,1.04)])
    line('Chained pen',[(-3.76,3.34,1.045),(-3.79,3.28,1.049),(-3.80,3.15,1.046)],.005,'orange')
    # Restrained actual procedure signage integrated with architecture.
    assembly('Arrival sign','Office front head',[(-3.51,3.52,2.78)],(0,1,0))
    box('Arrival sign plate',(-3.51,3.509,2.77),(1.63,.022,.27),'teal',.004)
    txt('Arrival sign lettering','01  /  CHECK IN',(-4.20,3.495,2.716),.112,'ivory')
    for x in [-4.255,-2.765]:bolt('Sign bolt',(x,3.489,2.77),r=.008)
    collection('03 Services and lighting')
    assembly('Office light','Office front head',[(-4.0,3.52,2.97)],(0,1,0))
    box('Light back rail',(-3.95,3.478,2.97),(1.30,.083,.07),'frame',.004)
    profile('Light folded shade',[(-.02,.06),(-.30,.04),(-.34,-.055),(-.32,-.07),(-.285,.018),(-.02,.035)],1.41,0,(-3.95,3.46,2.99),'ivory',.004)
    cyl('Fluorescent tube',(-3.95,3.27,2.981),.019,1.21,'warm_lamp','X',w=.001)
    light('Hatch practical pool',(-3.95,3.18,2.94),(-3.7,2.8,0),125,(1,.82,.61),1.22,.19)
    assembly('Office power riser','Office front pier',[(-6.49,3.52,1.63),(-6.49,3.52,2.70)],(0,1,0))
    line('Galvanized conduit',[(-6.49,3.477,.2),(-6.49,3.477,2.90),(-6.40,3.477,3.01),(-2.46,3.477,3.01)],.018,'steel')
    for z in [.31,1.63,2.70]:
        box('Conduit saddle',(-6.49,3.50,z),(.09,.04,.025),'steel',.002)
        for x in [-6.527,-6.453]:bolt('Saddle screw',(x,3.475,z),r=.006)
    box('Door access switch',(-6.49,3.426,1.15),(.13,.10,.20),'teal',.009)
    cyl('Access key barrel',(-6.49,3.364,1.17),.026,.02,'steel','Y')
    box('Access key slot',(-6.49,3.351,1.17),(.022,.002,.004),'ink',0)
    # Real wall mounted courtesy lamp at the door, with a hood and visible falloff.
    assembly('Door bulkhead','Office front head',[(-5.4,3.52,2.64)],(0,1,0))
    box('Bulkhead base',(-5.4,3.483,2.64),(.32,.075,.14),'frame',.014)
    box('Bulkhead glass',(-5.4,3.435,2.628),(.25,.026,.075),'warm_lamp',.012)
    for x in [-5.50,-5.30]:box('Bulkhead guard', (x,3.414,2.638),(.014,.02,.105),'frame',.003)
    light('Door courtesy light',(-5.4,3.36,2.61),(-5.4,3.0,.5),34,(1,.76,.47),.26,.08)
    # Soft off-camera bounce belongs to an actual front-apron practical in full room.
    light('Apron ceiling practical',(-1.8,1.2,3.15),(-4.6,3.0,.6),200,(.73,.84,1),2.0,1.0)
    light('Office internal practical',(-4.6,5.5,2.87),(-3.5,3.9,1.0),100,(1,.88,.7),1.2,.4)

def configure():
    global ASM
    collection('09 Fixed cameras')
    camera('S01_style',(-1.8,.55,1.65),(-4.5,3.58,1.45),26)
    camera('S02_material',(-3.05,1.65,1.65),(-3.98,3.45,1.45),42)
    S.render.engine='CYCLES';S.cycles.samples=a.samples;S.cycles.use_denoising=True
    S.cycles.seed=8217;S.cycles.use_animated_seed=False
    S.cycles.max_bounces=8;S.cycles.diffuse_bounces=4;S.cycles.glossy_bounces=4;S.cycles.transmission_bounces=8
    S.render.resolution_x=a.width;S.render.resolution_y=round(a.width*9/16);S.render.resolution_percentage=100
    S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.image_settings.color_depth='8'
    S.world=bpy.data.worlds.new('Dark industrial ambient');S.world.use_nodes=True
    S.world.node_tree.nodes.get('Background').inputs[0].default_value=(.21,.26,.30,1)
    S.world.node_tree.nodes.get('Background').inputs[1].default_value=.18
    S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=.25
    S.render.film_transparent=False
    S['section']='compliance-dock';S['revision']=a.revision;S['stage']=a.stage;S['build_seed']=8217
    S.camera=bpy.data.objects['S01_style']

palette();slice_architecture()
if a.stage=='full':
    # Imported only after the independently reviewed style slice passes.
    sys.path.insert(0,str(Path(__file__).parent))
    import full_dock
    full_dock.build(globals())
configure()
bpy.context.view_layer.update()
S['contact_assemblies']=json.dumps(CONTACTS)
out=ROOT/'production'/'renders'/'review'/a.revision;out.mkdir(parents=True,exist_ok=True)
blendpath=ROOT/'blender'/('compliance_dock.blend' if a.stage=='full' else 'style_slice.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(blendpath),compress=True)
cams={o.name:{'location':list(o.location),'rotation_euler':list(o.rotation_euler),'lens_mm':o.data.lens} for o in S.objects if o.type=='CAMERA'}
(out/'cameras.json').write_text(json.dumps(cams,indent=2))
(out/'build.json').write_text(json.dumps({'blender':bpy.app.version_string,'revision':a.revision,'stage':a.stage,'objects':len(S.objects),'materials':len(bpy.data.materials),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'blend':str(blendpath.relative_to(ROOT))},indent=2))
if a.render:
    pref=bpy.context.preferences.addons['cycles'].preferences
    try:
        pref.compute_device_type='HIP';pref.get_devices()
        devices=[d for d in pref.devices if d.type=='HIP']
        if not devices:raise RuntimeError('No HIP device found')
        for d in pref.devices:d.use=(d.type=='HIP')
        S.cycles.device='GPU';print('GPU_DEVICES',[(d.name,d.type,d.use) for d in pref.devices])
    except Exception as e:raise RuntimeError('GPU initialization failed; no silent CPU fallback') from e
    names=list(cams) if a.render=='all' else a.render.split(',')
    for name in names:
        S.camera=bpy.data.objects[name];S.render.filepath=str(out/(name+'.png'))
        bpy.ops.render.render(write_still=True)
print('BUILD_OK',a.revision,str(blendpath))
