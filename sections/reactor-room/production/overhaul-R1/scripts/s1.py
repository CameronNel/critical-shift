import bpy,bmesh,sys,math; sys.path.insert(0,"."); from r2lib import *; from lib import col
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w32.blend"); sc=bpy.context.scene
G=lambda n:bpy.data.materials[n]
M={"IRON":G("R2 iron"),"TRIM":G("R2 trim rust"),"TEXT":G("R2 sign text"),"PLATE":G("R2 iron"),"LANE":G("R2 lane")}
class A2(Acc):
    def frustum(s,key,cx,cy,z0,z1,r0,r1,seg=8,rot=math.pi/8):
        bm=s.get(key); r=bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r0,radius2=r1,depth=1.0)
        for v in r['verts']:
            x,y=v.co.x,v.co.y; c,sn=math.cos(rot),math.sin(rot); v.co=Vector((cx+x*c-y*sn,cy+x*sn+y*c,z0+(v.co.z+.5)*(z1-z0)))
A=A2(); coll=col("27 R2 STATIONS")
def outline(x0,x1,y0,y1,w=0.09,z=0.012):
    for (a,b,c,d) in ((x0,x1,y0,y0+w),(x0,x1,y1-w,y1),(x0,x0+w,y0,y1),(x1-w,x1,y0,y1)):
        A.box(("station stencil","TRIM"),(a+b)/2,(c+d)/2,z,z+0.014,b-a,d-c,0,0.003)
    # corner ticks (hazard hatch) on the diagonal
    for (cx,cy) in ((x0,y0),(x1,y0),(x0,y1),(x1,y1)):
        A.box(("station corner","IRON"),cx,cy,z,z+0.02,0.22,0.22,math.pi/4,0.003)
def bollard(x,y,h=0.95):
    A.frustum(("bollard","IRON"),x,y,0,h,0.075,0.075,8,0); A.frustum(("bollard band","TRIM"),x,y,h*0.72,h*0.72+0.10,0.085,0.085,8,0); A.frustum(("bollard cap","IRON"),x,y,h,h+0.03,0.09,0.06,8,0)
def wall_sign(txt,wi,x,y,z,width=None):
    width=len(txt)*0.078+0.35
    w=WALLS[wi]; u=(Vector((x,y))-w.P).dot(w.t)
    A.wbox(("station sign plate","IRON"),w,u-width/2,u+width/2,z,z+0.34,0.06,0.12,0.012,0.0)
    A.wbox(("station sign rim","TRIM"),w,u-width/2,u+width/2,z,z+0.03,0.06,0.125,0.004,0.0)
    p=w.pt(u,0.13); cu=bpy.data.curves.new("R2 station "+txt,'FONT'); cu.body=txt; cu.size=0.10; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=0.0
    ob=bpy.data.objects.new("R2 station sign "+txt.replace("\n"," "),cu); ob.location=(p.x,p.y,z+0.17); ob.rotation_euler=(math.pi/2,0,w.angle+math.pi); coll.objects.link(ob); cu.materials.append(M["TEXT"])
# stencils + bollards + signs   (wall indices: 0 S, 1 SE, 2 E, 3 NE, 4 N, 5 NW, 6 W, 7 SW)
ST=[("grid",(9.15,10.75,-2.45,1.45),2,(10.7,-0.6),"GRID / DEMAND",[(9.0,-2.6),(9.0,1.6)]),
    ("turbine",(8.45,10.75,-5.55,-2.1),2,(10.7,-3.8),"TURBINE HALL",[(8.3,-5.7),(8.3,-1.95)]),
    ("generator",(-10.75,-8.15,-4.6,-2.75),6,(-10.7,-3.2),"STANDBY GENERATOR",[(-8.0,-4.75),(-8.0,-2.6)]),
    ("reserve A",(-10.75,-8.9,2.95,4.15),6,(-10.7,3.6),"RESERVE POWER A",[(-8.75,3.0),(-8.75,4.1)]),
    ("reserve B",(-10.75,-8.9,-5.75,-4.65),6,(-10.7,-5.7),"RESERVE POWER B",[(-8.75,-5.8),(-8.75,-4.6)]),
    ("fuel racks",(-5.55,-2.65,8.9,10.65),4,(-4.1,10.7),"FUEL RECEIVING",[(-5.7,8.75),(-2.5,8.75)]),
    ("fuel cart",(-9.95,-8.05,6.55,8.35),5,(-9.0,7.5),"FUEL CART BAY",[(-10.0,6.4),(-7.95,6.4),(-7.95,8.5)]),
    ("bank control",(2.55,4.75,9.55,10.75),4,(3.6,10.7),"BANK CONTROL",[(2.4,9.4),(4.9,9.4)]),
    ("vent",(8.75,10.35,5.85,7.75),3,(9.7,7.0),"VENT CONTROL",[(8.6,5.7),(10.5,5.7)]),
    ("emergency cooling",(1.0,4.15,-10.45,-8.0),0,(2.6,-10.7),"EMERGENCY COOLING",[(0.85,-7.85),(4.3,-7.85)]),
    ("coolant pump",(-4.15,-2.35,-10.15,-7.95),0,(-3.2,-10.7),"COOLANT PUMP P-10",[(-4.3,-7.8)]),
    ("sampling",(1.1,2.15,-4.3,-3.15),0,None,None,[])]
for name,(x0,x1,y0,y1),wi,sp,txt,bols in ST:
    outline(x0,x1,y0,y1)
    for b in bols: bollard(*b)
    if txt and sp: wall_sign(txt,wi,sp[0],sp[1],3.05 if wi!=4 or True else 3.05)
# waste cask ring
n=40
for i in range(n):
    a=2*math.pi*(i+0.5)/n; r=1.6; L=2*r*math.sin(math.pi/n)+0.01
    A.box(("station stencil","TRIM"),7.6+r*math.cos(a),8.2+r*math.sin(a),0.012,0.026,L,0.09,a+math.pi/2,0.003)
for a in (0.9,2.2,3.4,5.4): bollard(7.6+1.9*math.cos(a),8.2+1.9*math.sin(a))
wall_sign("WASTE TRANSFER",3,8.4,8.6,3.05)
# pool console canopy (over the SCRAM / ACK console) - slanted hood, keeps every control reachable
A.box(("console hood","IRON"),0.0,-3.78,1.55,1.62,2.7,0.62,0,0.02); A.box(("console hood trim","TRIM"),0.0,-3.47,1.55,1.60,2.7,0.03,0,0.004)
for x in (-1.25,1.25): A.box(("console hood post","IRON"),x,-3.78,0.0,1.55,0.08,0.08,0,0.006)
objs=A.build("27 R2 STATIONS","R2 stations",{"IRON":M["IRON"],"TRIM":M["TRIM"]})
for o in objs:
    for p in o.data.polygons: p.use_smooth=False
print("station kit objects:",len(objs))
bpy.ops.wm.save_as_mainfile(filepath=S+"/w33.blend"); print("ok")
