import bpy,sys,math; sys.path.insert(0,"."); from hs import *
S=sys.argv[sys.argv.index("--")+1]; src=sys.argv[sys.argv.index("--")+2]; dst=sys.argv[sys.argv.index("--")+3]
bpy.ops.wm.open_mainfile(filepath=S+"/"+src); sc=bpy.context.scene
M=mats()
coll=bpy.data.collections.get("29 R2 DRESSING 2") or bpy.data.collections.new("29 R2 DRESSING 2")
if coll.name not in sc.collection.children: sc.collection.children.link(coll)
# ================= bridge crane (fuel-handling crane over the hall) =================
Z=14.0; YR=5.6; Yg=4.6
A=K(); g="crane"
for sx in (-1,1):
    x=sx*10.0
    A.bx((g,"IRON"),x-0.22,x+0.22,-YR,YR,Z,Z+0.36,0.02)                       # runway beam
    A.bx((g,"TRIM"),x-0.08,x+0.08,-YR,YR,Z+0.36,Z+0.42,0.006)                 # rail
    for y in range(-5,6,2):
        A.hull((g,"IRON"),[(x+sx*0.55,y-0.06,Z),(x+sx*0.55,y+0.06,Z),(x+sx*0.22,y-0.06,Z-0.6),(x+sx*0.22,y+0.06,Z-0.6),(x+sx*0.55,y-0.06,Z+0.36),(x+sx*0.55,y+0.06,Z+0.36),(x+sx*0.1,y-0.06,Z),(x+sx*0.1,y+0.06,Z)],0.01)
    A.bx((g,"IRON"),x-0.5,x+0.5,-YR-0.2,-YR,Z,Z+0.5,0.02); A.bx((g,"IRON"),x-0.5,x+0.5,YR,YR+0.2,Z,Z+0.5,0.02)
static=A.build("29 R2 DRESSING 2","R2 crane rails",M)
B=K()   # bridge (moves in y)
by=Yg
for dx in (-10.0,10.0):
    B.bx((g,"OLIVE"),dx-0.35,dx+0.35,by-0.5,by+0.5,Z+0.42,Z+0.85,0.03)        # end truck
B.bx((g,"OLIVE"),-10.0,10.0,by-0.35,by+0.35,Z+0.5,Z+1.35,0.04)               # box girder
B.bx((g,"TRIM"),-10.0,10.0,by-0.36,by-0.3,Z+0.62,Z+0.74,0.006); B.bx((g,"TRIM"),-10.0,10.0,by+0.3,by+0.36,Z+0.62,Z+0.74,0.006)
B.bx((g,"IRON"),-10.0,10.0,by-0.55,by+0.55,Z+1.35,Z+1.4,0.01)               # walkway plate
for x in range(-9,10,2): B.bx((g,"IRON"),x-0.03,x+0.03,by-0.6,by-0.55,Z+1.35,Z+1.9,0.004)
B.bx((g,"TRIM"),-10.0,10.0,by-0.62,by-0.58,Z+1.85,Z+1.9,0.004)
for x in (-9,-3,3,9): B.led((g,"LAMPA"),'-y',by-0.36,x,Z+1.0,0.05,0.03)
bridge=B.build("29 R2 DRESSING 2","R2 crane bridge",M)
T=K()   # trolley + hoist (moves in x)
T.bx((g,"IRON"),-0.7,0.7,by-0.5,by+0.5,Z+1.4,Z+1.7,0.03)
T.bx((g,"OLIVE"),-0.55,0.55,by-0.4,by+0.4,Z+1.7,Z+2.35,0.03)
T.prism((g,"IRON"),(0.0,by-0.45,Z+2.0),(0.0,by+0.45,Z+2.0),0.32,0.32,10,0)
T.bx((g,"TRIM"),-0.6,0.6,by-0.42,by+0.42,Z+2.35,Z+2.42,0.01)
T.led((g,"STAT"),'-y',by-0.4,0.35,Z+2.05,0.04,0.03)
T.prism((g,"CABLE"),(-0.12,by,Z+1.4),(-0.12,by,10.9),0.02,0.02,4); T.prism((g,"CABLE"),(0.12,by,Z+1.4),(0.12,by,10.9),0.02,0.02,4)
T.bx((g,"TRIM"),-0.3,0.3,by-0.14,by+0.14,10.55,10.95,0.03)
T.hull((g,"IRON"),[(-0.1,by-0.06,10.55),(0.1,by-0.06,10.55),(-0.03,by-0.05,10.05),(0.03,by-0.05,10.05),(-0.1,by+0.06,10.55),(0.1,by+0.06,10.55),(-0.03,by+0.05,10.05),(0.03,by+0.05,10.05)],0.006)
T.bx((g,"LAMPA"),-0.05,0.05,by-0.05,by+0.05,10.0,10.06,0.004)
trol=T.build("29 R2 DRESSING 2","R2 crane trolley",M)
def keyloop(ob,idx,frames,vals):
    for f,v in zip(frames,vals):
        ob.location[idx]=v; ob.keyframe_insert("location",index=idx,frame=f)
for o in trol:
    o.location=(0,0,0); keyloop(o,0,[1,300,600],[-6.5,6.5,-6.5])
for o in bridge:
    o.location=(0,0,0); keyloop(o,1,[1,450,900],[0.0,1.6,0.0])
for o in static+bridge+trol:
    for p in o.data.polygons: p.use_smooth=False
# ================= wall status boards (stability-driven glow) =================
def board(wi,u,z0,label):
    w=WALLS[wi]; A=K(); g="board"; W=3.4; H=1.35
    A.wbox((g,"IRON"),w,u-W/2,u+W/2,z0,z0+H,0.0,0.14,0.02,0.0)
    A.wbox((g,"TRIM"),w,u-W/2,u+W/2,z0,z0+0.06,0.14,0.17,0.006,0.0)
    A.wbox((g,"TRIM"),w,u-W/2,u+W/2,z0+H-0.06,z0+H,0.14,0.17,0.006,0.0)
    A.wbox((g,"INK"),w,u-W/2+0.1,u+W/2-0.1,z0+0.1,z0+H-0.1,0.14,0.16,0.004,0.0)
    n=10
    for i in range(n):
        a=u-W/2+0.25+i*(W-0.5)/n; b=a+(W-0.5)/n-0.06
        A.wbox((g,"GLOW"),w,a,b,z0+0.2,z0+0.5,0.16,0.19,0.004,0.0)
    for i in range(6): A.wbox((g,"LAMPA" if i%2 else "STAT"),w,u-W/2+0.3+i*0.5,u-W/2+0.4+i*0.5,z0+H-0.28,z0+H-0.2,0.16,0.18,0.003,0.0)
    ob=A.build("29 R2 DRESSING 2","R2 board "+label,M)
    p=w.pt(u,0.19); cu=bpy.data.curves.new("board "+label,'FONT'); cu.body=label; cu.size=0.2; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=0.0; cu.resolution_u=1
    t=bpy.data.objects.new("R2 board text "+label,cu); t.location=(p.x,p.y,z0+0.85); t.rotation_euler=(math.pi/2,0,w.angle+math.pi); coll.objects.link(t); cu.materials.append(M["SIGN"])
    for o in ob:
        for q in o.data.polygons: q.use_smooth=False
board(2,6.0,6.4,"REACTOR STABILITY")   # east wall, y=0
board(6,6.0,6.4,"COOLANT / POWER")     # west wall
board(4,6.0,7.0,"CONTAINMENT")         # north wall
bpy.ops.wm.save_as_mainfile(filepath=S+"/"+dst); print("ok")
