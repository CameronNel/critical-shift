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

def dome(name,cx,cy,zbase,r,h,up,m,c="22 ASSET KIT 1",seg=20,rings=6):
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    bmesh.ops.create_uvsphere(bm,u_segments=seg,v_segments=rings*2,radius=1.0)
    bm.verts.ensure_lookup_table()
    dele=[v for v in bm.verts if (v.co.z< -1e-4 if up else v.co.z>1e-4)]
    bmesh.ops.delete(bm,geom=dele,context='VERTS')
    for v in bm.verts: v.co=Vector((v.co.x*r,v.co.y*r,v.co.z*h))
    bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(name,me); o.location=(cx,cy,zbase); col(c).objects.link(o)
    o.data.materials.append(m if not isinstance(m,str) else mat(m)); return o
def port(name,loc,medium,dn,direction=(0,0,1),c="23 ASSET PORTS"):
    e=bpy.data.objects.new(name,None); e.empty_display_type='ARROWS'; e.empty_display_size=0.12
    e.location=loc; e.rotation_euler=Vector(direction).to_track_quat('Z','Y').to_euler(); col(c).objects.link(e)
    e["medium"]=medium; e["nominal_dn_mm"]=dn; e["connected"]=False; return e
def label(name,text,loc,size,rot=(math.pi/2,0,0),m="hall_ink",c="22 ASSET KIT 1"):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=text; cu.size=size; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=0.0
    o=bpy.data.objects.new(name,cu); o.location=loc; o.rotation_euler=rot; col(c).objects.link(o)
    o.data.materials.append(mat("QA label white") if m=="white" else mat("QA label charcoal")); return o
