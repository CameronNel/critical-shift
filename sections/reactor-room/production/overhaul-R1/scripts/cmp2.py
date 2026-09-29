import bpy,sys,re,math,collections
from mathutils import Vector
f=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=f); sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def bb(o): return [o.matrix_world@Vector(v) for v in o.bound_box]
def ext(p): return (min(q.x for q in p),max(q.x for q in p),min(q.y for q in p),max(q.y for q in p),min(q.z for q in p),max(q.z for q in p))
print("FILE",f.split("/")[-1])
# 1. objects outside the hall wall (beyond 11.2 m from centre along the three door axes)
def summarize(name,cond):
    objs=[o for o in sc.objects if o.type in("MESH","CURVE","FONT") and not o.name.startswith(("LP haze","RF outdoor")) and not (o.users_collection and o.users_collection[0].name.startswith("RF ")) and cond(ext(bb(o)))]
    p=[q for o in objs for q in bb(o)]
    if objs:
        e=ext(p); print("BEYOND",name,len(objs),"objs  x%.2f..%.2f y%.2f..%.2f z%.2f..%.2f"%e)
        c=collections.Counter((o.users_collection[0].name if o.users_collection else "?") for o in objs); print("   collections:",dict(c))
    else: print("BEYOND",name,"0 objects")
summarize("west  (x<-11.6)",lambda e:e[0]<-11.6)
summarize("north (y>11.6)",lambda e:e[3]>11.6 and e[2]>-11)
summarize("SE diag (x>11.6,y<-9)",lambda e:e[1]>11.6 and e[3]<-8 and e[2]<-9)
summarize("east (x>11.6,|y|<8)",lambda e:e[1]>11.6 and e[2]>-8 and e[3]<8)
# 2. ray casts for inner shell distance at z=7.5 and z=2.0 from radius 6 outward (8 directions incl. axes)
def ray(o,d):
    hit,loc,n,idx,ob,mat=sc.ray_cast(dg,o,d)
    return (round((loc-o).length,2),ob.name[:34]) if hit else None
for z in (7.5,2.0):
    print("RAYS z=",z)
    for k in range(8):
        a=k*math.pi/4; o=Vector((6*math.cos(a),6*math.sin(a),z)); d=Vector((math.cos(a),math.sin(a),0))
        r=ray(o,d); print("   dir %3d deg"%round(math.degrees(a)),"start r=6 -> hit at r=%.2f"%(6+r[0]) if r else "no hit",r[1] if r else "")
# 3. up ray for ceiling underside from a clear floor spot
for pt in ((6.5,6.5,1.0),(-6.5,6.5,1.0)):
    r=ray(Vector(pt),Vector((0,0,1))); print("UP from",pt,"->",r)
