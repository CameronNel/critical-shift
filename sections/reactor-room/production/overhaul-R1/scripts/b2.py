import bpy,sys; sys.path.insert(0,"."); from lib import *
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w1.blend")
pan=bpy.data.objects["Shell 3 field.014"].data.materials[0]
DK=mat("hall_steel"); SG=mat("hall_steel_light"); GL=mat("observation_glass"); FL=mat("hall_floor"); LAMP=mat("lamp"); WH=mat("hall_white")
MZ="20 CONTROL MEZZANINE"; EL="21 ELEVATOR"
# --- patch east wall
box("East wall patch door",10.8,11.08,1.6,5.6,0.0,5.0,pan,MZ)
box("East wall patch window low",10.8,11.08,-2.7,1.6,8.0,10.2,pan,MZ)
box("East wall patch window high",10.8,11.08,-2.7,1.6,10.2,12.9,pan,MZ)
# --- mezzanine shell
XW,XE=-4.8,2.0; YB,YF=-10.06,-5.9; ZF=5.4
# front wall with 5.4 x 2.4 window
WX0,WX1=-4.1,1.3; WZ0,WZ1=6.1,8.5
box("MZ front sill wall",XW,XE,YF-0.2,YF,ZF,WZ0,SG,MZ)
box("MZ front head wall",XW,XE,YF-0.2,YF,WZ1,8.8,SG,MZ)
box("MZ front pier W",XW,WX0,YF-0.2,YF,WZ0,WZ1,SG,MZ)
box("MZ front pier E",WX1,XE,YF-0.2,YF,WZ0,WZ1,SG,MZ)
box("MZ window glass",WX0,WX1,YF-0.13,YF-0.09,WZ0,WZ1,GL,MZ)
for i,x in enumerate([WX0,WX1]): box(f"MZ window jamb {i}",x-0.06,x+0.06,YF-0.24,YF+0.02,WZ0-0.06,WZ1+0.06,DK,MZ)
for i,z in enumerate([WZ0,WZ1]): box(f"MZ window rail {i}",WX0-0.06,WX1+0.06,YF-0.24,YF+0.02,z-0.06,z+0.06,DK,MZ)
for i in range(1,3): x=WX0+(WX1-WX0)*i/3; box(f"MZ window mullion {i}",x-0.03,x+0.03,YF-0.2,YF-0.02,WZ0,WZ1,DK,MZ)
box("MZ front deep sill",WX0-0.1,WX1+0.1,YF-0.3,YF+0.12,WZ0-0.1,WZ0,DK,MZ)
# east wall of room with door to landing
box("MZ east wall lower",XE,XE+0.2,YB,YF,ZF,8.8,SG,MZ) 
# (door opening y -7.3..-6.3 z 5.4..7.6 -> cut by replacing with pieces)
bpy.data.objects.remove(bpy.data.objects["MZ east wall lower"],do_unlink=True)
box("MZ east wall back",XE,XE+0.2,YB,-7.3,ZF,8.8,SG,MZ)
box("MZ east wall front",XE,XE+0.2,-6.3,YF,ZF,8.8,SG,MZ)
box("MZ east wall header",XE,XE+0.2,-7.3,-6.3,7.6,8.8,SG,MZ)
for i,y in enumerate([-7.3,-6.3]): box(f"MZ door jamb {i}",XE-0.03,XE+0.23,y-0.04,y+0.04,ZF,7.6,DK,MZ)
box("MZ door head",XE-0.03,XE+0.23,-7.34,-6.26,7.56,7.64,DK,MZ)
# landing slab + rails
box("MZ landing slab",XE,4.6,-7.6,YF,ZF-0.2,ZF,FL,MZ)
box("MZ landing edge angle",XE,4.6,YF-0.05,YF+0.05,ZF-0.3,ZF-0.2,DK,MZ)
# structure: front columns + beams
for i,x in enumerate([XW+0.15,-1.4,XE+0.1,4.5]):
    box(f"MZ column {i}",x-0.14,x+0.14,YF-0.3,YF-0.02,0.0,ZF-0.2,DK,MZ)
    box(f"MZ column base {i}",x-0.26,x+0.26,YF-0.42,YF+0.1,0.0,0.05,DK,MZ)
box("MZ front beam",XW,4.6,YF-0.28,YF-0.02,ZF-0.55,ZF-0.2,DK,MZ)
for i,x in enumerate([-4.4,-2.4,-0.4,1.6,3.4]): box(f"MZ joist {i}",x-0.05,x+0.05,YB,YF-0.28,ZF-0.5,ZF-0.2,DK,MZ)
box("MZ soffit panel",XW,XE,YB,YF-0.28,ZF-0.24,ZF-0.2,SG,MZ)
# guard rail on landing front and east edge
def rail(name,p0,p1):
    for k,(h,r) in enumerate(((1.05,0.025),(0.55,0.018))): cyl_between(f"{name} rail {k}",(p0[0],p0[1],ZF+h),(p1[0],p1[1],ZF+h),r,DK,MZ)
    n=max(2,int(((p1[0]-p0[0])**2+(p1[1]-p0[1])**2)**.5/1.0)+1)
    for j in range(n+1):
        t=j/n; x=p0[0]+(p1[0]-p0[0])*t; y=p0[1]+(p1[1]-p0[1])*t
        cyl(f"{name} post {j}",x,y,ZF,ZF+1.05,0.028,DK,MZ,8)
rail("MZ landing front",(XE,YF-0.06),(4.6,YF-0.06)); rail("MZ landing east",(4.6-0.06,YF-0.06),(4.6-0.06,-7.6))
# --- elevator
SX0,SX1=2.2,4.6; SY0,SY1=YB,-7.6; SZ1=10.8
box("EL shaft west wall",SX0,SX0+0.14,SY0,SY1,0.0,SZ1,SG,EL)
box("EL shaft east wall",SX1-0.14,SX1,SY0,SY1,0.0,SZ1,SG,EL)
box("EL shaft back wall",SX0,SX1,SY0,SY0+0.16,0.0,SZ1,SG,EL)
box("EL shaft roof",SX0,SX1,SY0,SY1,SZ1,SZ1+0.15,DK,EL)
box("EL pit floor",SX0,SX1,SY0,SY1,-0.3,0.0,DK,EL)
# front: frames at both landings, glass above/between
FYc=SY1
for z0,z1,tag in ((0.0,2.4,"ground"),(ZF,ZF+2.4,"upper")):
    for i,x in enumerate([SX0+0.14,SX1-0.14]): box(f"EL {tag} jamb {i}",x-0.07 if i==0 else x-0.07,x+0.07 if i==0 else x+0.07,FYc-0.08,FYc+0.1,z0,z1+0.1,DK,EL)
    box(f"EL {tag} head",SX0+0.07,SX1-0.07,FYc-0.08,FYc+0.1,z1,z1+0.12,DK,EL)
    box(f"EL {tag} indicator",3.1,3.7,FYc+0.1,FYc+0.13,z1+0.16,z1+0.34,mat("hall_ink"),EL)
    box(f"EL {tag} indicator lamp",3.35,3.45,FYc+0.13,FYc+0.15,z1+0.21,z1+0.29,LAMP,EL)
    box(f"EL {tag} call panel",4.72-0.14,4.72-0.06,FYc-0.06,FYc+0.06,z0+1.0,z0+1.35,DK,EL) if False else None
# glazed front: below upper landing (z 2.6..5.4) and above (7.9..10.8) + solid apron below ground head
box("EL front glass lower",SX0+0.14,SX1-0.14,FYc,FYc+0.04,2.55,ZF,GL,EL)
box("EL front glass upper",SX0+0.14,SX1-0.14,FYc,FYc+0.04,ZF+2.55,SZ1,GL,EL)
for i,z in enumerate([3.9,7.0,9.0]): box(f"EL front transom {i}",SX0+0.14,SX1-0.14,FYc-0.03,FYc+0.06,z-0.04,z+0.04,DK,EL)
# guide rails, machine, sheave
for i,x in enumerate([2.62,4.18]): box(f"EL guide rail {i}",x-0.03,x+0.03,-9.2,-9.0,0.0,SZ1-0.2,DK,EL)
box("EL machine beam A",SX0,SX1,-9.6,-9.4,8.85,9.05,DK,EL); box("EL machine beam B",SX0,SX1,-8.95,-8.75,8.85,9.05,DK,EL)
box("EL traction motor",3.85,4.45,-9.5,-8.9,9.05,9.65,mat("hall_teal"),EL)
sh=cyl("EL sheave",3.1,-9.2,-0.275,0.275,0.55,DK,EL,seg=24); sh.location=(3.1,-9.2,9.8); sh.rotation_euler=(0,math.radians(90),0)
# car
CW=(2.62,4.18); 
car=bpy.data.objects.new("EL car",None); col(EL).objects.link(car)
def cp(name,x0,x1,y0,y1,z0,z1,m):
    o=box(name,x0,x1,y0,y1,z0,z1,m,EL); o.parent=car; return o
cp("EL car floor",2.65,4.15,-9.45,-7.85,0.0,0.08,DK); cp("EL car roof",2.65,4.15,-9.45,-7.85,2.4,2.48,DK)
cp("EL car back",2.65,4.15,-9.45,-9.37,0.08,2.4,SG); cp("EL car west",2.65,2.73,-9.37,-7.85,0.08,2.4,SG); cp("EL car east",4.07,4.15,-9.37,-7.85,0.08,2.4,SG)
cp("EL car door glass",2.73,4.07,-7.92,-7.88,0.08,2.35,GL); cp("EL car door frame top",2.73,4.07,-7.94,-7.86,2.3,2.4,DK)
cp("EL car cabin light",3.1,3.7,-8.9,-8.4,2.36,2.4,LAMP)
cp("EL car handrail",2.73,4.07,-9.37,-9.31,0.95,1.0,mat("hall_pipe")) 
cp("EL car control strip",4.0,4.07,-8.3,-8.1,1.0,1.4,mat("hall_ink"))
# counterweight + ropes
cw=box("EL counterweight",2.9,3.9,-9.95,-9.6,0,1.9,DK,EL)
r1=cyl("EL rope car",3.1,-8.65,0,1,0.012,mat("hall_ink"),EL,6); r2=cyl("EL rope counterweight",3.1,-9.75,0,1,0.012,mat("hall_ink"),EL,6)
r3=cyl("EL rope car B",3.5,-8.65,0,1,0.012,mat("hall_ink"),EL,6); r4=cyl("EL rope cw B",3.5,-9.75,0,1,0.012,mat("hall_ink"),EL,6)
# animation: car floor z_f keyed 0 <-> 5.4
def key(f_z):
    car.location.z=f_z; car.keyframe_insert("location",index=2)
    cw.location.z=7.45-f_z; cw.keyframe_insert("location",index=2)
    for r,base,L in ((r1,car.location.z+2.48,None),):
        pass
    top_c=f_z+2.48; L1=9.8-top_c
    for r in (r1,r3):
        r.location.z=top_c; r.scale.z=L1; r.keyframe_insert("location",index=2); r.keyframe_insert("scale",index=2)
    cwtop=(7.45-f_z)+1.9; L2=9.8-cwtop
    for r in (r2,r4):
        r.location.z=cwtop; r.scale.z=L2; r.keyframe_insert("location",index=2); r.keyframe_insert("scale",index=2)
sc=bpy.context.scene
for f,z in ((1,0.0),(120,0.0),(240,5.4),(360,5.4),(480,0.0)):
    sc.frame_set(f); key(z)
sc.frame_set(1); sc.frame_end=480
bpy.ops.wm.save_as_mainfile(filepath=S+"/w2.blend")
print("ok")
