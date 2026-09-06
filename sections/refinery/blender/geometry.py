"""Small Blender-native construction kit. All helpers use WORLD coordinates.

Parenting preserves world transforms. Articulated roots therefore have real pivots.
"""
import bpy, math
from contextlib import contextmanager
from mathutils import Vector, Matrix
from materials import M
_collection = 'REFINERY_ARCHITECTURE'
_parent = None

def collection(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (collection(parent).children if parent else bpy.context.scene.collection.children).link(c)
    return c

@contextmanager
def use(name, parent=None):
    global _collection, _parent
    before = _collection, _parent
    _collection, _parent = name, parent
    collection(name)
    try: yield
    finally: _collection, _parent = before

def finish(o,name,mat=None):
    o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    collection(_collection).objects.link(o)
    if mat: o.data.materials.append(M[mat] if isinstance(mat,str) else mat)
    if _parent:
        bpy.context.view_layer.update()
        world=o.matrix_world.copy(); o.parent=_parent; o.matrix_world=world
    o['refinery_authored']=True
    return o

def bevel(o,width=.01):
    if width:
        mod=o.modifiers.new('Manufactured edge radii','BEVEL'); mod.width=width;mod.segments=2
        mod=o.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');mod.keep_sharp=True
    return o

def mesh(name,verts,faces,mat,edge=0):
    d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update()
    o=bpy.data.objects.new(name,d);collection(_collection).objects.link(o)
    return bevel(finish(o,name,mat),edge)

def box(name,pos,size,mat,bevel=.01):
    x,y,z=[v/2 for v in size]
    v=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]
    f=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
    o=mesh(name,v,[tuple(reversed(face)) for face in f],mat,bevel);o.location=pos
    if _parent: o.matrix_world=Matrix.Translation(Vector(pos))
    return o

def rod(name,a,b,r,mat,verts=24):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=(b-a).length,location=(a+b)/2)
    o=bpy.context.object;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    return bevel(finish(o,name,mat),.003)

def tube(name,points,r,mat,cyclic=False):
    d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=2;d.bevel_depth=r;d.bevel_resolution=3
    s=d.splines.new('POLY');s.points.add(len(points)-1)
    for p,v in zip(s.points,points):p.co=(*v,1)
    s.use_cyclic_u=cyclic
    o=bpy.data.objects.new(name,d);collection(_collection).objects.link(o)
    return finish(o,name,mat)

def torus(name,pos,major,minor,mat,rotation=(math.pi/2,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=36,minor_segments=10,location=pos,major_radius=major,minor_radius=minor,rotation=rotation)
    return finish(bpy.context.object,name,mat)

def empty(name,pos=(0,0,0),**meta):
    o=bpy.data.objects.new(name,None);collection(_collection).objects.link(o);o.location=pos;o.empty_display_size=.12
    finish(o,name)
    for k,v in meta.items():o[k]=v
    return o

def marker(machine,role,pos,kind='interaction',**meta):
    with use('REFINERY_INTERACTION',None):
        return empty('INT_'+machine+'_'+role,pos,machine=machine,role=role,kind=kind,**meta)

def root(machine,pos=(0,0,0)):
    name='MACHINE_'+machine
    collection(name,'REFINERY_MACHINES')
    with use(name):return empty('ROOT_'+machine,pos,machine_id=machine)

def label(name,text,pos,size=.1,mat='ink',rotation=(math.pi/2,0,0),align='LEFT'):
    d=bpy.data.curves.new(name,'FONT');d.body=text;d.size=size;d.align_x=align;d.extrude=0
    o=bpy.data.objects.new(name,d);collection(_collection).objects.link(o);o.location=pos;o.rotation_euler=rotation
    return finish(o,name,mat)

def support(obj,target,direction,world_points,kind='FLOOR'):
    for name in ['CS_SUPPORT_REQUIRED','CS_'+kind+'_DRESSING']:
        c=collection(name)
        if obj.name not in c.objects:c.objects.link(obj)
    obj['cs_support_target']=target.name if hasattr(target,'name') else target
    obj['cs_support_direction']=direction
    obj['support_dependent']=True
    bpy.context.view_layer.update()
    for i,p in enumerate(world_points):
        with use('REFINERY_VALIDATION',None):a=empty('SUPPORT_'+obj.name+'_%02d'%i,p,cs_support_anchor=True)
        a.parent=obj;a.matrix_world=Matrix.Translation(Vector(p));a.empty_display_size=.02
    return obj

def beam(name,a,b,width,depth,mat='darksteel'):
    a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(width,depth,(b-a).length),mat,.005)
    world=Matrix.Translation((a+b)/2) @ (b-a).to_track_quat('Z','Y').to_matrix().to_4x4()
    o.matrix_world=world
    return o

def frame(name,x,y,w,d,h,mat='darksteel'):
    parts=[]
    for sx in [-1,1]:
        for sy in [-1,1]:
            px,py=x+sx*(w/2-.07),y+sy*(d/2-.07)
            foot=box(name+'_foot',(px,py,.04),(.24,.24,.08),'steel',.012)
            support(foot,'Floor','WORLD_-Z',[(px,py,0)])
            parts.append(box(name+'_leg',(px,py,h/2+.08),(.10,.10,h),'darksteel'))
    for py in [y-d/2+.07,y+d/2-.07]:parts.append(box(name+'_rail',(x,py,h),(w,.12,.15),mat))
    for px in [x-w/2+.07,x+w/2-.07]:parts.append(box(name+'_cross',(px,y,h),(.12,d,.15),mat))
    return parts

def tapered(name,lower,upper,mat,thickness=.035):
    # Four-sided open sheet-metal hopper, two loops each (x,y,z) clockwise.
    n=len(lower);v=list(lower)+list(upper);f=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    o=mesh(name,v,f,mat,.008);m=o.modifiers.new('Sheet thickness','SOLIDIFY');m.thickness=thickness
    return o

def control_panel(machine,x,y,z,labels,width=.7):
    panel=box(machine+'_Control_enclosure',(x,y,z),(width,.18,.54),'pale',.03)
    for i,title in enumerate(labels):
        px=x-width*.34+(i%3)*width*.34;pz=z+.11-(i//3)*.21
        mat='red' if any(k in title for k in ['STOP','EMERGENCY']) else 'yellow' if 'BYPASS' in title else 'plastic'
        rod(machine+'_'+title+'_button',(px,y-.095,pz),(px,y-.14,pz),.037,mat)
        label(machine+'_'+title+'_engraving',title.replace('_',' '),(px,y-.095,pz-.071),.031,'ink',align='CENTER')
        marker(machine,title,(px,y-.18,pz),kind='control',reach_m=.65)
    return panel

def valve(name,pos,r=.14,mat='red'):
    x,y,z=pos;torus(name+'_wheel',pos,r,.018,mat)
    rod(name+'_spindle',(x,y-.035,z),(x,y+.17,z),.025,'steel')
    for a in [0,2.094,4.189]:rod(name+'_spoke',pos,(x+r*math.cos(a),y,z+r*math.sin(a)),.012,mat)

def gauge(name,pos,r=.115):
    x,y,z=pos;rod(name+'_case',(x,y+.04,z),(x,y,z),r,'steel')
    rod(name+'_dial',(x,y-.001,z),(x,y-.007,z),r*.86,'paper')
    rod(name+'_needle',(x,y-.012,z),(x+r*.53,y-.012,z+r*.29),.006,'ink',12)
    for i in range(7):
        a=math.radians(35+i*45)
        rod(name+'_tick',(x+r*.65*math.cos(a),y-.013,z+r*.65*math.sin(a)),(x+r*.76*math.cos(a),y-.013,z+r*.76*math.sin(a)),.004,'ink',8)

def conveyor(name,a,b,width=.72,support_ts=(.06,.5,.94),motor_at='head'):
    a,b=Vector(a),Vector(b);axis=(b-a).normalized();side=axis.cross(Vector((0,0,1))).normalized()
    mid=(a+b)/2;length=(b-a).length
    for sign in [-1,1]:
        beam(name+'_sideframe',a+side*sign*(width/2+.06),b+side*sign*(width/2+.06),.08,.13,'teal')
    belt=box(name+'_upper_belt',mid,(width,length,.045),'rubber',.004)
    # Local Y travels down belt; local Z its surface normal.
    q=axis.to_track_quat('Y','Z');belt.matrix_world=Matrix.Translation(mid) @ q.to_matrix().to_4x4()
    ret=box(name+'_visible_return',mid-Vector((0,0,.20)),(width,length,.024),'rubber',.003);ret.matrix_world=Matrix.Translation(mid-Vector((0,0,.20))) @ q.to_matrix().to_4x4()
    for i in range(int(length/.36)+1):
        fraction=i/max(1,int(length/.36))
        if name=='Sorter':fraction=.05+.90*fraction
        c=a+(b-a)*fraction
        roller=rod(name+'_roller',c-side*(width/2+.03)-Vector((0,0,.07)),c+side*(width/2+.03)-Vector((0,0,.07)),.075,'steel')
        roller['moving_part']='belt roller'
    for t in support_ts:
        c=a+(b-a)*t
        for sign in [-1,1]:
            p=c+side*sign*(width/2+.06)
            foot=box(name+'_support_foot',(p.x,p.y,.03),(.23,.23,.06),'steel');support(foot,'Floor','WORLD_-Z',[(p.x,p.y,0)])
            beam(name+'_support',(p.x,p.y,.06),p-Vector((0,0,.12)),.09,.09)
    drive=(a+(b-a)*.12) if motor_at=='tail' else b
    m=drive+side*(width/2+.22)-Vector((0,0,.12))
    if motor_at=='tail':rod(name+'_drive_shaft',drive-side*(width/2+.03)-Vector((0,0,.12)),m,.032,'steel')
    rod(name+'_drive_motor',m,m+side*.35,.16,'darksteel')
    box(name+'_gearbox',m,(.28,.28,.28),'teal')
    return belt
