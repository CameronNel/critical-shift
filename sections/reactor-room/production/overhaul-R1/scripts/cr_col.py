import bpy,sys
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=sys.argv[sys.argv.index("--")+1])
def ext(o):
    p=[o.matrix_world@Vector(v) for v in o.bound_box]; return (min(q.x for q in p),max(q.x for q in p),min(q.y for q in p),max(q.y for q in p),min(q.z for q in p),max(q.z for q in p))
R=(-5.0,2.4,-6.2,-3.85,4.7,9.1)   # new front strip of the mezzanine (x0,x1,y0,y1,z0,z1)
n=0
for o in bpy.data.objects:
    if o.type not in("MESH","CURVE","FONT") or o.name.startswith(("LP haze","RF ")): continue
    c=o.users_collection[0].name if o.users_collection else ""
    if c.startswith(("20","26","RF","25")): continue
    e=ext(o)
    if e[1]>R[0] and e[0]<R[1] and e[3]>R[2] and e[2]<R[3] and e[5]>R[4] and e[4]<R[5]:
        n+=1; print("HIT",c[:18],"|",o.name[:46],"x%.2f..%.2f y%.2f..%.2f z%.2f..%.2f"%e)
print("objects intersecting the new front strip:",n)
