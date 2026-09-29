import bpy, bmesh, math
from mathutils import Vector, Matrix
def bbw(o):
    p=[o.matrix_world@Vector(c) for c in o.bound_box]; return tuple((min(q[i] for q in p),max(q[i] for q in p)) for i in range(3))
def mat(name):
    m=bpy.data.materials.get(name); 
    if not m: raise KeyError(name)
    return m
_col={}
def col(name):
    if name not in _col:
        c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
        if c.name not in [x.name for x in bpy.context.scene.collection.children_recursive] and c not in list(bpy.context.scene.collection.children):
            bpy.context.scene.collection.children.link(c)
        _col[name]=c
    return _col[name]
def box(name,x0,x1,y0,y1,z0,z1,m,c="20 REDESIGN"):
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    bmesh.ops.create_cube(bm,size=1.0)
    for v in bm.verts: v.co=Vector(((v.co.x+.5)*(x1-x0)+x0,(v.co.y+.5)*(y1-y0)+y0,(v.co.z+.5)*(z1-z0)+z0))
    bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(name,me); col(c).objects.link(o)
    if m: o.data.materials.append(m if not isinstance(m,str) else mat(m))
    return o
def cyl(name,x,y,z0,z1,r,m,c="20 REDESIGN",seg=16,axis='Z'):
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r,radius2=r,depth=1.0)
    for v in bm.verts: v.co.z=(v.co.z+.5)*(z1-z0)+z0
    bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(name,me); o.location=(x,y,0); col(c).objects.link(o)
    if m: o.data.materials.append(m if not isinstance(m,str) else mat(m))
    return o
def cyl_between(name,p0,p1,r,m,c="20 REDESIGN",seg=12):
    p0=Vector(p0);p1=Vector(p1);d=p1-p0
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r,radius2=r,depth=d.length)
    bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(name,me); col(c).objects.link(o)
    o.location=(p0+p1)/2; o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    if m: o.data.materials.append(m if not isinstance(m,str) else mat(m))
    return o
