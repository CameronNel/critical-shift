import bpy,bmesh,sys,math,random; sys.path.insert(0,"."); from r2lib import *; from r2state import *; from lib import col
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w28.blend"); sc=bpy.context.scene; st=bpy.data.objects["REACTOR_STATE"]
G=lambda n:bpy.data.materials[n]
M={"IRON":G("R2 iron"),"TRIM":G("R2 trim rust"),"DOOR":G("R2 door steel"),"DOORP":G("R2 door panel"),"GLOW":G("R2 state glow"),"TEXT":G("R2 sign text"),"PAPER":G("R2 paper"),"AMB":G("R2 lamp amber"),"CLERE":G("R2 clerestory")}
M["INK"]=r2mat("R2 ink",(0.006,0.006,0.008),0.7,edge=None,grime=0.0,noise=(1,0),mottle=0.0)
M["CONE"]=r2mat("R2 cone",(0.55,0.11,0.01),0.5,edge=(0.9,0.4,0.1),grime=0.4,noise=(4,0),mottle=0.4)
M["PUDDLE"]=bpy.data.materials.new("R2 puddle"); M["PUDDLE"].use_nodes=True; b=M["PUDDLE"].node_tree.nodes["Principled BSDF"]; b.inputs['Base Color'].default_value=(0.004,0.004,0.008,1); b.inputs['Roughness'].default_value=0.03; b.inputs['Metallic'].default_value=0.0
M["EXIT"]=emit_mat("R2 exit sign",(0.25,1.0,0.35),3.0)
class A2(Acc):
    def frustum(s,key,cx,cy,z0,z1,r0,r1,seg=8,rot=math.pi/8):
        bm=s.get(key); r=bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r0,radius2=r1,depth=1.0)
        for v in r['verts']:
            x,y=v.co.x,v.co.y; c,sn=math.cos(rot),math.sin(rot); v.co=Vector((cx+x*c-y*sn,cy+x*sn+y*c,z0+(v.co.z+.5)*(z1-z0)))
A=A2()
# ---------- (a) elevator landing doors, keyed to the car
doors=[]
def door_pair(tag,z0,z1,open_frames):
    for nm,x0,x1,dirn in (("L",-7.86,-6.80,-1),("R",-6.80,-5.74,1)):
        bm=bmesh.new(); r=bmesh.ops.create_cube(bm,size=1.0)
        for v in r['verts']: v.co=Vector((x0+(v.co.x+.5)*(x1-x0-0.01),-5.62+(v.co.y+.5)*0.07-0.07,z0+0.05+(v.co.z+.5)*(z1-z0-0.1)))
        bmesh.ops.bevel(bm,geom=list({e for v in r['verts'] for e in v.link_edges}),offset=0.015,segments=1,affect='EDGES')
        me=bpy.data.meshes.new(f"EL landing door {tag} {nm}"); bm.to_mesh(me); bm.free(); o=bpy.data.objects.new(f"EL landing door {tag} {nm}",me); col("21 ELEVATOR").objects.link(o); me.materials.append(M["DOOR"])
        # keyframes: closed=0, open=dirn*0.98
        for f,val in open_frames: o.location.x=dirn*0.98*val; o.keyframe_insert("location",index=0,frame=f)
        doors.append(o)
door_pair("ground",0.0,2.5,[(1,1),(122,1),(136,0),(464,0),(478,1)])
door_pair("upper",5.4,7.9,[(1,0),(228,0),(242,1),(362,1),(376,0),(480,0)])
# indicators, call panels, floor numbers, hazard stripe
A.box(("el frame","TRIM"),-6.8,-5.65,0.0,0.16,2.4,0.12,0,0.01)
for z0,tag in ((2.62,"G"),(8.02,"1")):
    A.box(("el indicator","IRON"),-6.8,-5.60,z0,z0+0.26,0.7,0.06,0,0.01); A.box(("el indicator lamp","AMB"),-6.8,-5.565,z0+0.06,z0+0.20,0.5,0.012,0,0.004)
for z0 in (0.0,5.4):
    A.box(("el call panel","IRON"),-5.45,-5.60,z0+1.05,z0+1.45,0.16,0.06,0,0.01); A.box(("el call button","AMB"),-5.45,-5.565,z0+1.22,z0+1.28,0.06,0.012,0,0.004)
# ---------- (b) pool rim glow + underwater slots
n=48
for i in range(n):
    a0=2*math.pi*i/n; a1=2*math.pi*(i+1)/n; am=(a0+a1)/2; r=3.74; L=2*r*math.sin(math.pi/n)+0.02
    A.box(("pool rim glow","GLOW"),r*math.cos(am),r*math.sin(am),0.20,0.235,L,0.08,am+math.pi/2,0.004)
for i in range(8):
    am=i*math.pi/4+math.pi/8; r=3.36; A.box(("pool wall slot","GLOW"),r*math.cos(am),r*math.sin(am),-5.6,-0.9,0.10,0.03,am+math.pi/2,0.0)
# ---------- (c) dressing
random.seed(11)
def poster(w,u,h,txt,size=0.07):
    W,Hh=0.62,0.86
    A.wbox(("poster frame","TRIM"),w,u-W/2-0.03,u+W/2+0.03,h-0.03,h+Hh+0.03,0.048,0.074,0.008,0.0)
    A.wbox(("poster paper","PAPER"),w,u-W/2,u+W/2,h,h+Hh,0.074,0.078,0.0,0.0)
    p=w.pt(u,0.082); cu=bpy.data.curves.new("R2 poster "+txt,'FONT'); cu.body=txt; cu.size=size; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=0.0
    ob=bpy.data.objects.new("R2 poster "+txt.replace("\n"," "),cu); ob.location=(p.x,p.y,h+Hh/2); ob.rotation_euler=(math.pi/2,0,w.angle+math.pi); col("23 R2 FLOOR AND DRESSING").objects.link(ob); cu.materials.append(M["INK"])
for wi,u,h,t in ((2,9.4,2.2,"SAFETY\nIS A\nSHARED\nDUTY"),(2,10.6,2.2,"REPORT\nANY\nANOMALY"),(5,1.7,2.2,"WATCH\nTHE\nGREEN"),(5,4.7,2.2,"IF IT\nTURNS\nDO NOT\nRUN"),(6,1.3,2.2,"PLEASE\nSIGN\nOUT"),(6,10.7,2.2,"NO\nLONE\nWORKING"),(0,5.7,2.3,"HANDS\nCLEAR")):
    poster(WALLS[wi],u,h,t)
# exit signs over the three doors (small emissive) + hazard strips
for wi,c in ((1,3.395),(4,6.0),(6,6.0)):
    w=WALLS[wi]; A.wbox(("exit sign","EXIT"),w,c+1.9,c+2.5,DOORH:=5.0+0.12,5.0+0.30,0.40,0.43,0.003,0.0) if False else A.wbox(("exit sign","EXIT"),w,c+1.9,c+2.5,5.12,5.30,0.40,0.43,0.003,0.0)
# caution-tape barriers round the waste cask and the generator
def barrier(pts):
    for (x,y) in pts: A.frustum(("barrier post","IRON"),x,y,0,1.05,0.04,0.04,8,0)
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        L=math.hypot(x1-x0,y1-y0); ang=math.atan2(y1-y0,x1-x0); cx,cy=(x0+x1)/2,(y0+y1)/2
        A.box(("tape","TRIM"),cx,cy,0.88,0.96,L,0.012,ang,0.0); A.box(("tape band","IRON"),cx,cy,0.90,0.94,L,0.014,ang,0.0)
barrier([(5.2,6.2),(5.2,4.6),(7.2,4.6)]); barrier([(-8.0,2.0),(-7.2,2.0),(-7.2,-2.4)])
for x,y in((6.4,5.6),(7.6,5.1),(-6.7,0.4)):
    A.frustum(("cone","CONE"),x,y,0,0.55,0.20,0.05,8,0.3); A.box(("cone base","CONE"),x,y,0,0.03,0.42,0.42,0.3,0.005)
# wet-floor A-frame and puddles
A.box(("wet sign","TRIM"),-1.8,-4.9,0,0.62,0.42,0.05,0.4,0.01); A.box(("wet sign","TRIM"),-1.55,-5.05,0,0.62,0.42,0.05,0.4+math.pi,0.01)
for x,y,rx,ry in((-3.0,3.6,0.9,0.5),(4.6,3.0,0.6,0.4),(-5.4,-2.2,0.7,0.45),(2.4,-5.4,0.8,0.4),(5.9,-2.4,0.5,0.35)):
    bm=A.get(("puddle","PUDDLE")); r=bmesh.ops.create_cone(bm,cap_ends=True,segments=8,radius1=1,radius2=1,depth=0.004)
    for v in r['verts']: v.co=Vector((x+v.co.x*rx,y+v.co.y*ry,0.016+v.co.z))
objs=A.build("23 R2 FLOOR AND DRESSING","R2 detail",M)
for o in objs:
    for p in o.data.polygons: p.use_smooth=False
# elevator floor labels
coll=bpy.data.collections["21 ELEVATOR"]
for txt,z in (("G",2.95),("1",8.35)):
    cu=bpy.data.curves.new("EL floor "+txt,'FONT'); cu.body=txt; cu.size=0.18; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=0.0
    ob=bpy.data.objects.new("EL floor "+txt,cu); ob.location=(-6.3,-5.555,z); ob.rotation_euler=(math.pi/2,0,0); coll.objects.link(ob); cu.materials.append(M["TEXT"])
bpy.ops.wm.save_as_mainfile(filepath=S+"/w29.blend"); print("ok",len(objs))
