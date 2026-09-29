import bpy,bmesh,sys,math,random; sys.path.insert(0,"."); from r2lib import *; from r2state import *; from lib import col
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w27.blend"); sc=bpy.context.scene; st=bpy.data.objects["REACTOR_STATE"]
# ---- clear the legacy control-room dressing/shell pieces
LEG=("07 EAST CONTROL ROOM","18 CONTROL ROOM DRESSING","19 CONTROL FIDELITY","GROK GT_Hero","GROK GT_Desk","17 CONTROL PROPAGANDA")
n=0
for o in list(bpy.data.objects):
    cn=o.users_collection[0].name if o.users_collection else ""
    if cn in LEG: bpy.data.objects.remove(o,do_unlink=True); n+=1
print("legacy control-room objects removed:",n)
G=lambda n:bpy.data.materials["R2 "+n]
M={"IRON":G("iron"),"TRIM":G("trim rust"),"WALL":G("wall plum lower"),"DADO":G("dado navy"),"FLOOR":G("floor tile"),"BACK":G("backing")}
M["DESK"]=r2mat("R2 desk",(0.11,0.055,0.030),0.55,edge=(0.55,0.28,0.10),grime=0.3,noise=(3,0),mottle=0.7)
M["FAB"]=r2mat("R2 fabric",(0.060,0.030,0.070),0.9,edge=None,grime=0.2,noise=(4,0),mottle=0.8)
M["BLANK"]=r2mat("R2 blanket",(0.10,0.05,0.045),0.95,edge=None,grime=0.2,noise=(5,0),mottle=0.9)
M["PAPER"]=r2mat("R2 paper",(0.30,0.28,0.24),0.9,edge=None,grime=0.1,noise=(6,0),mottle=0.3)
M["MUG"]=r2mat("R2 mug",(0.22,0.05,0.03),0.4,edge=(0.6,0.2,0.1),grime=0.1,noise=(6,0),mottle=0.2)
M["SCREEN"]=state_mat("R2 state screen",0.8,st); M["AMBER"]=emit_mat("R2 readout amber",(1.0,0.52,0.14),1.0); M["LAVL"]=emit_mat("R2 ceiling panel",(0.6,0.5,1.0),4.0)
M["BIND1"]=r2mat("R2 binder a",(0.03,0.05,0.14),0.6,edge=None,grime=0.1,noise=(6,0),mottle=0.2); M["BIND2"]=r2mat("R2 binder b",(0.26,0.05,0.03),0.6,edge=None,grime=0.1,noise=(6,0),mottle=0.2)
A=Acc(); X0,X1,YB,YF,ZF,ZC=-4.6,1.95,-10.0,-6.15,5.4,8.8
def b(key,x0,x1,y0,y1,z0,z1,ch=0.012,ang=0.0): A.box(key,(x0+x1)/2,(y0+y1)/2,z0,z1,x1-x0,y1-y0,ang,ch)
# shell pieces the legacy layers provided
b(("cr floor","FLOOR"),X0-0.2,X1+0.2,YB,YF,5.2,5.4,0.0); b(("cr roof","IRON"),X0-0.2,X1+0.2,YB-0.06,YF,8.8,9.0,0.01)
b(("cr back wall","BACK"),X0-0.2,X1+0.2,YB-0.06,YB+0.06,5.4,8.8,0.0)
b(("cr back dado","DADO"),X0,X1,YB+0.06,YB+0.10,5.4,6.35); b(("cr back rail","TRIM"),X0,X1,YB+0.06,YB+0.13,6.35,6.47); b(("cr back upper","WALL"),X0,X1,YB+0.06,YB+0.10,6.47,8.8)
for i in range(6): b(("cr back inset","WALL"),X0+0.15+i*1.08,X0+1.0+i*1.08,YB+0.10,YB+0.13,6.75,8.5)
# console desk along the window
b(("desk top","DESK"),-4.0,1.3,-7.6,-6.4,6.10,6.20,0.015)
for x in(-4.0,-1.35,1.22): b(("desk panel","IRON"),x,x+0.08,-7.5,-6.5,5.4,6.10)
b(("desk kick","IRON"),-4.0,1.3,-6.48,-6.42,5.4,6.10,0.005)
for i,cx in enumerate((-3.4,-2.35,-1.3,-0.25,0.8)):
    b(("monitor bezel","IRON"),cx-0.44,cx+0.44,-6.86,-6.70,6.32,6.86,0.02)
    b(("monitor stand","IRON"),cx-0.07,cx+0.07,-6.80,-6.72,6.20,6.32,0.005)
    b(("monitor screen","SCREEN" if i in(0,2,4) else "AMBER"),cx-0.38,cx+0.38,-6.872,-6.862,6.38,6.80,0.0)
    b(("keyboard","IRON"),cx-0.25,cx+0.25,-7.38,-7.12,6.20,6.23,0.008)
for i,(cx,cy) in enumerate(((-3.7,-7.0),(-2.7,-7.05),(-0.6,-6.95),(0.5,-7.1))): b(("desk paper","PAPER"),cx-0.10,cx+0.10,cy-0.14,cy+0.14,6.20,6.205,0.0)
for cx,cy in((-1.9,-7.15),(1.05,-7.3)):
    bm=A.get(("mug","MUG")); r=bmesh.ops.create_cone(bm,cap_ends=True,segments=8,radius1=0.05,radius2=0.05,depth=0.10)
    for v in r['verts']: v.co=Vector((v.co.x+cx,v.co.y+cy,v.co.z+6.25))
# chairs
for cx,cy,ang in((-2.9,-8.15,0.15),(-0.5,-8.3,-0.35),(-3.7,-8.6,0.9)):
    A.box(("chair seat","FAB"),cx,cy,5.95,6.06,0.56,0.56,ang,0.03); A.box(("chair back","FAB"),cx+math.sin(ang)*0.28,cy-math.cos(ang)*0.28,6.06,6.80,0.56,0.09,ang,0.03)
    bm=A.get(("chair base","IRON")); r=bmesh.ops.create_cone(bm,cap_ends=True,segments=8,radius1=0.05,radius2=0.05,depth=0.55)
    for v in r['verts']: v.co=Vector((v.co.x+cx,v.co.y+cy,v.co.z+5.68))
    A.box(("chair base","IRON"),cx,cy,5.4,5.46,0.62,0.10,ang,0.01); A.box(("chair base","IRON"),cx,cy,5.4,5.46,0.10,0.62,ang,0.01)
# wall mimic panel (schematic) on the back wall
b(("mimic frame","TRIM"),-3.7,0.9,YB+0.10,YB+0.16,6.75,8.55,0.02); b(("mimic panel","IRON"),-3.62,0.82,YB+0.16,YB+0.19,6.83,8.47,0.005)
def line(x0,z0,x1,z1,w=0.035,key=("mimic line","AMBER")):
    L=math.hypot(x1-x0,z1-z0); ang=math.atan2(z1-z0,x1-x0)
    bm=A.get(key); r=bmesh.ops.create_cube(bm,size=1.0)
    for v in r['verts']:
        lx=v.co.x*L; lz=v.co.z*w; c,s=math.cos(ang),math.sin(ang); v.co=Vector(((x0+x1)/2+lx*c-lz*s,YB+0.205+v.co.y*0.01,(z0+z1)/2+lx*s+lz*c))
for pts in (((-3.3,7.2),(-2.2,7.2),(-2.2,7.9),(-1.4,7.9)),((-1.4,7.9),(0.0,7.9),(0.0,7.2),(0.6,7.2)),((-2.2,7.2),(-2.2,8.2),(-3.3,8.2)),((0.0,7.9),(0.0,8.2),(0.6,8.2))):
    for a,c in zip(pts,pts[1:]): line(a[0],a[1],c[0],c[1])
for cx,cz in((-3.3,7.2),(-3.3,8.2),(0.6,7.2),(0.6,8.2)): b(("mimic node","SCREEN"),cx-0.09,cx+0.09,YB+0.20,YB+0.215,cz-0.09,cz+0.09,0.0)
b(("mimic core","SCREEN"),-1.75,-1.05,YB+0.20,YB+0.215,7.55,8.25,0.0)
# east wall cabinets + west shelves
for i,y0 in enumerate((-9.6,-8.85,-8.1)): b(("cabinet","IRON"),1.5,1.95,y0,y0+0.72,5.4,7.0,0.02); b(("cabinet handle","TRIM"),1.46,1.50,y0+0.32,y0+0.40,6.4,6.9,0.005)
for i in range(4): b(("shelf","IRON"),-4.6,-4.25,-9.8,-8.0,5.9+i*0.55,5.95+i*0.55,0.005)
random.seed(3)
for i in range(4):
    y=-9.75
    for j in range(7):
        w=random.uniform(0.05,0.09); h=random.uniform(0.28,0.42); k="BIND1" if (i+j)%2 else "BIND2"
        b(("binder",k),-4.58,-4.32,y,y+w,5.95+i*0.55,5.95+i*0.55+h,0.004); y+=w+0.02
# the cot in the corner
b(("cot frame","IRON"),-0.3,1.4,-9.95,-9.05,5.4,5.62,0.015); b(("cot mattress","BLANK"),-0.25,1.35,-9.9,-9.1,5.62,5.74,0.03)
b(("cot blanket","FAB"),0.15,1.35,-9.9,-9.1,5.74,5.83,0.04); b(("cot pillow","PAPER"),-0.22,0.08,-9.85,-9.35,5.74,5.82,0.03)
# ceiling fixtures + duct
for cx in(-2.9,-0.4): b(("ceiling panel","LAVL"),cx-0.6,cx+0.6,-8.4,-8.05,8.74,8.80,0.005)
b(("duct","IRON"),-4.5,1.9,-9.6,-9.0,8.35,8.75,0.02)
# floor papers scattered
for i in range(9):
    x=random.uniform(-4.2,1.2); y=random.uniform(-9.4,-7.7); a=random.uniform(0,3.14); A.box(("floor paper","PAPER"),x,y,5.402,5.407,0.22,0.30,a,0.0)
objs=A.build("26 R2 CONTROL ROOM","R2 control",M)
for o in objs:
    for p in o.data.polygons: p.use_smooth=False
# labels
coll=bpy.data.collections["26 R2 CONTROL ROOM"]
def txt(t,x,y,z,size,mat,rot):
    cu=bpy.data.curves.new("R2 cr "+t,'FONT'); cu.body=t; cu.size=size; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=0.002
    ob=bpy.data.objects.new("R2 cr "+t.replace("\n"," "),cu); ob.location=(x,y,z); ob.rotation_euler=rot; coll.objects.link(ob); cu.materials.append(mat)
txt("REACTOR STATUS",-1.4,YB+0.215,8.65,0.12,M["AMBER"],(math.pi/2,0,math.pi))
txt("BANK A          BANK B",-1.4,YB+0.215,6.95,0.08,M["AMBER"],(math.pi/2,0,math.pi))
txt("SHIFT 04 - DO NOT LEAVE UNATTENDED",1.94,-8.4,7.4,0.09,M["AMBER"],(math.pi/2,0,math.pi/2))
# lamps: warm desk lamp + screen glow already via emission; dim task light over the desk
from lib import col as _c
ld=bpy.data.lights.new("LP control desk lamp",'SPOT'); ld.spot_size=math.radians(70); ld.spot_blend=0.6; ld.energy=350; ld.color=(1.0,0.55,0.2)
o=bpy.data.objects.new("LP control desk lamp",ld); _c("25 LIGHTING").objects.link(o); o.location=(-1.4,-8.0,8.6); o.rotation_euler=(Vector((-1.4,-7.0,6.4))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=S+"/w28.blend"); print("ok",len(objs))
