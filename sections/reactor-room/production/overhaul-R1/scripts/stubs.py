import bpy,sys
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath="/home/user/critical-shift/sections/facility-assembly/sources/reactor-room/module.blend")
def bb(o): return [o.matrix_world@Vector(v) for v in o.bound_box]
def ext(p): return (min(q.x for q in p),max(q.x for q in p),min(q.y for q in p),max(q.y for q in p),min(q.z for q in p),max(q.z for q in p))
sets={"W":lambda e:e[0]<-11.6,"N":lambda e:e[3]>11.6 and e[2]>-11,"SE":lambda e:e[1]>11.6 and e[3]<-8 and e[2]<-9}
for k,c in sets.items():
    print("SET",k)
    for o in sorted(bpy.data.objects,key=lambda o:o.name):
        if o.type in("MESH","CURVE","FONT") and o.users_collection and o.users_collection[0].name=="01 ARCHITECTURE" and c(ext(bb(o))):
            e=ext(bb(o)); print("  ",o.name[:46],o.type,[m.name[:22] for m in (o.data.materials if o.type=="MESH" else o.data.materials) if m],"x%.2f..%.2f y%.2f..%.2f z%.2f..%.2f"%e)
