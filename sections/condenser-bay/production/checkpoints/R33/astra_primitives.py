"""Data API versions of Grok kit primitives for fast, local polish additions.

Same dimensions, segment counts, material and bevel policy; avoids global operator
dependency-graph refresh on every new bolt. Existing R21 geometry is untouched.
"""
import math
import bmesh
import kit as k


def box(n,p,d,m,b=.006):
    x,y,z=[v/2 for v in d]
    v=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]
    f=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
    o=k.mesh(n,v,f,m);o.location=p
    return k.bevel(o,min(b,min(d)*.22) if min(d)>0 else 0)


def cyl(n,p,r,length,m,axis='Z',verts=48,b=.004):
    bm=bmesh.new()
    bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=False,segments=verts,radius1=r,radius2=r,depth=length)
    me=k.bpy.data.meshes.new(n);bm.to_mesh(me);bm.free()
    o=k.bpy.data.objects.new(n,me);k.S.collection.objects.link(o);k.reg(o,n,m);o.location=p
    if axis=='Y':o.rotation_euler.x=math.pi/2
    if axis=='X':o.rotation_euler.y=math.pi/2
    for f in me.polygons:f.use_smooth=len(f.vertices)==4
    return k.bevel(o,min(b,r*.25,length*.2))


def torus(n,p,R,r,m,axis='Z'):
    v=[]
    for i in range(48):
        a=i*math.tau/48
        for j in range(10):
            b=j*math.tau/10
            v.append(((R+r*math.cos(b))*math.cos(a),(R+r*math.cos(b))*math.sin(a),r*math.sin(b)))
    f=[]
    for i in range(48):
        for j in range(10):
            f.append((i*10+j,((i+1)%48)*10+j,((i+1)%48)*10+(j+1)%10,i*10+(j+1)%10))
    o=k.mesh(n,v,f,m,0,True);o.location=p
    if axis=='Y':o.rotation_euler.x=math.pi/2
    if axis=='X':o.rotation_euler.y=math.pi/2
    return o


def install():
    k.box=box;k.cyl=cyl;k.torus=torus
