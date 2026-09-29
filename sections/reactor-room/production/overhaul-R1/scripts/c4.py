import bpy,sys,re; sys.path.insert(0,"."); from lib import *
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w9.blend")
ENAM=mat("hall_teal"); INK=mat("hall_steel"); MUST=mat("hall_yellow"); IVORY=mat("hall_pipe"); CHR=mat("GT_Chrome"); K="22 ASSET KIT 1"
# drop my duplicate tank labels/plates
for o in list(bpy.data.objects):
    if o.name.startswith(("AK1 EC-1 label","AK1 EC-2 label","AK1 EC-1 plate","AK1 EC-2 plate")): bpy.data.objects.remove(o,do_unlink=True)
pre=("Turbine compressed","Turbine formed","Turbine anchors","Drive longitudinal","Turbine return riser","Bearing foot","Jacket","Turbine pressure shell","Casing assembly","Turbine anchor foot","Turbine fan","Turbine service","Turbine inspection","Turbine split","Turbine latch","Turbine bearing foot")
n=0
for o in list(bpy.data.objects):
    if o.type=='MESH' and o.name.startswith(pre):
        b=bbw(o)
        if b[0][0]>8.3 and b[0][1]<10.9 and b[1][0]>-5.4 and b[1][1]<-2.2: bpy.data.objects.remove(o,do_unlink=True); n+=1
print("turbine old removed",n)
cx,cz,y0,y1,R=9.6,1.15,-4.74,-2.86,0.69
def ycyl(name,yy0,yy1,r,m,x=cx,z=cz,seg=28): return cyl_between(name,(x,yy0,z),(x,yy1,z),r,m,K,seg)
ycyl("AK1 T-06 casing",y0,y1,R,ENAM)
ycyl("AK1 T-06 end step N",y1,y1+0.14,0.5,INK); ycyl("AK1 T-06 end step S",y0-0.14,y0,0.5,INK)
ycyl("AK1 T-06 split flange",-3.86,-3.74,R+0.05,INK,seg=28)
for i,yy in enumerate((-4.5,-4.15,-3.45,-3.1)): ycyl(f"AK1 T-06 lagging band {i}",yy-0.04,yy+0.04,R+0.025,MUST)
for i,yy in enumerate((-4.35,-3.25)): box(f"AK1 T-06 saddle {i}",cx-0.45,cx+0.45,yy-0.14,yy+0.14,0.14,0.62,INK,K)
cyl("AK1 T-06 steam inlet",cx,-3.8,1.8,2.35,0.15,IVORY,K,14); cyl("AK1 T-06 steam inlet flange",cx,-3.8,2.31,2.36,0.23,INK,K,14)
cyl_between("AK1 T-06 exhaust",(cx+0.65,-3.3,cz),(10.55,-3.3,cz),0.15,IVORY,K,14); cyl_between("AK1 T-06 exhaust flange",(10.53,-3.3,cz),(10.58,-3.3,cz),0.23,INK,K,14)
box("AK1 T-06 governor",cx-0.28,cx+0.28,-3.28,-2.95,1.8,2.15,ENAM,K); cyl_between("AK1 T-06 governor dial",(cx,-2.95,1.98),(cx,-2.89,1.98),0.09,CHR,K,16)
box("AK1 T-06 hatch plate",cx-0.22,cx+0.22,-4.45,-4.1,1.83,1.89,INK,K)
for i,yy in enumerate((-4.4,-4.15)): box(f"AK1 T-06 hatch handle {i}",cx-0.15,cx+0.15,yy-0.015,yy+0.015,1.89,1.94,INK,K)
box("AK1 T-06 coupling guard",cx-0.32,cx+0.32,-2.58,-2.2,0.55,1.5,INK,K); 
port("PORT_T-06_steam_in",(cx,-3.8,2.36),"steam",150,(0,0,1)); port("PORT_T-06_exhaust",(10.58,-3.3,cz),"steam_exhaust",200,(1,0,0))
bpy.ops.wm.save_as_mainfile(filepath=S+"/w10.blend"); print("ok")
