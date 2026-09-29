import bpy,re,collections
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath="w39.blend")
R={"grid":(9.0,10.9,-2.5,1.5),"turb":(8.4,10.9,-5.6,-2.1),"gen":(-10.9,-8.1,-4.7,-2.7),"resA":(-10.9,-8.7,2.9,4.3),"resB":(-10.9,-8.7,-5.8,-4.6),
"fuel":(-5.6,-2.6,8.7,10.9),"cart":(-10.0,-7.9,6.4,8.4),"bank":(2.5,4.8,9.5,10.9),"vent":(8.6,10.4,5.8,7.8),
"waste":(6.3,8.3,7.4,9.6),"ec":(1.0,4.2,-10.6,-8.0),"pump":(-4.7,-2.3,-10.3,-7.9),"samp":(1.0,2.3,-4.3,-3.1),"bench":(-10.8,-9.6,3.8,5.4)}
g=collections.defaultdict(list)
for o in bpy.data.objects:
    if o.type not in("MESH","CURVE","FONT") or o.name.startswith(("MERGED","R2 ","LP","WB B vent")): continue
    if o.users_collection[0].name[:2] in("22","23","24","25","26","27","20","21","03","04","RF"): continue
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]; cx=sum(v.x for v in bb)/8; cy=sum(v.y for v in bb)/8
    for k,(x0,x1,y0,y1) in R.items():
        if x0<=cx<=x1 and y0<=cy<=y1: g[(k,o.name.split(".")[0][:26])].append(bb); break
for (k,n),l in sorted(g.items()):
    p=[q for bb in l for q in bb]
    print("K",k,"|",n,len(l),"x%.2f..%.2f y%.2f..%.2f z%.2f..%.2f"%(min(q.x for q in p),max(q.x for q in p),min(q.y for q in p),max(q.y for q in p),min(q.z for q in p),max(q.z for q in p)))
