"""Control room: increase window-to-back-wall depth by 50% (3.94 m -> 5.91 m) by moving the front assembly forward (+Y).
usage: python cr1.py -- <src.blend> <dst.blend>
Rules per loose piece of collections 20 CONTROL MEZZANINE / 26 R2 CONTROL ROOM (and lights inside the room):
  west of x=-4.75 (elevator landing, rails, posts, west wall around the door) : stay, except the west wall front panel which grows forward
  y-length > 2.5 m (floor, roof, soffit, side walls, long beams)                : stretch (vertices in front of the split move)
  east storage run (cabinets, cot, wall text)                                    : stay
  everything else in front of the split (window, desk, monitors, chairs, lamps)  : move forward as a rigid piece
"""
import bpy,sys
from mathutils import Vector
A=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A[0],A[1]
D=1.97; S=-8.85
bpy.ops.wm.open_mainfile(filepath=SRC)
cols=[bpy.data.collections["20 CONTROL MEZZANINE"],bpy.data.collections["26 R2 CONTROL ROOM"]]
for o in [o for c in cols for o in c.objects if o.type=="MESH" and o.name.startswith("MERGED")]:
    bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active=o; o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.separate(type='LOOSE'); bpy.ops.object.mode_set(mode='OBJECT')
def ext(o):
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return (min(q.x for q in p),max(q.x for q in p),min(q.y for q in p),max(q.y for q in p),min(q.z for q in p),max(q.z for q in p))
def classify(o,e):
    cx=(e[0]+e[1])/2; cy=(e[2]+e[3])/2; ylen=e[3]-e[2]
    if o.name.startswith("MERGED 20 CONTROL M CF gunmetal") and abs(e[2]+6.30)<0.03 and abs(e[3]+5.90)<0.03: return ("front",-6.1)   # west wall panel in front of the door
    if cx<=-4.75: return ("stay",)
    if ylen>2.5: return ("stretch",S)
    if cx>=1.4 and e[2]>=-9.75 and e[3]<=-7.3 and (e[5]-e[4])<3: return ("stay",)                                             # east storage run
    return ("move",) if cy>S else ("stay",)
def stretch(o,thr):
    mw=o.matrix_world; inv=mw.inverted(); me=o.data
    for v in me.vertices:
        w=mw@v.co
        if w.y>thr: w.y+=D; v.co=inv@w
    me.update()
stats={"stay":0,"move":0,"stretch":0,"front":0,"lights":0}
for c in cols:
    for o in list(c.objects):
        if o.type not in("MESH","CURVE","FONT") or o.name.startswith(("East wall patch","MZ landing")): continue
        e=ext(o); r=classify(o,e)
        if r[0]=="move":
            if o.parent: raise SystemExit("parented object: "+o.name)
            o.location.y+=D
            if -1.75<e[0] and e[1]<-1.05 and e[4]<0.1 and e[5]>-0.1 and o.name.startswith("MERGED 20 CONTROL M hall_steel"):
                o.location.x-=0.8      # middle front post + base plate: slide off the pool-inlet trench pipe (x=-1.4)
        elif r[0] in("stretch","front"):
            if o.type!="MESH": raise SystemExit("cannot stretch non-mesh: "+o.name)
            stretch(o,r[1])
        stats[r[0]]+=1
for l in bpy.data.objects:
    if l.type=="LIGHT":
        p=l.matrix_world.translation
        if -4.8<=p.x<=2.2 and 5.0<=p.z<=9.6 and -10.6<=p.y<=-5.5 and p.y>S: l.location.y+=D; stats["lights"]+=1
bpy.context.view_layer.update()
print("CR1",stats)
bpy.ops.wm.save_as_mainfile(filepath=DST)
