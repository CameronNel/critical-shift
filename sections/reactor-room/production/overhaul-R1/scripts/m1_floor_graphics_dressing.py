import bpy,sys,math; sys.path.insert(0,"."); import r2lib; from r2lib import *
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w22.blend"); sc=bpy.context.scene
M={n:bpy.data.materials["R2 "+m] for n,m in (("IRON","iron"),("TRIM","trim rust"),("DADO","dado navy"))}
M["LANE"]=r2mat("R2 lane",(0.020,0.030,0.090),0.32,edge=(0.6,0.17,0.03),grime=0.15,noise=(1.5,0),mottle=0.5)
M["PAINT"]=r2mat("R2 paint rust",(0.50,0.12,0.02),0.85,edge=None,grime=0.5,noise=(3.0,0),mottle=0.9)
M["DRUMR"]=r2mat("R2 drum red",(0.30,0.03,0.02),0.5,edge=(0.8,0.2,0.05),grime=0.5,noise=(2.5,0),metal=0.2,mottle=0.6)
M["DRUMB"]=r2mat("R2 drum blue",(0.03,0.06,0.20),0.5,edge=(0.3,0.4,0.8),grime=0.5,noise=(2.5,0),metal=0.2,mottle=0.6)
M["CRATE"]=r2mat("R2 crate",(0.16,0.09,0.05),0.8,edge=(0.4,0.25,0.12),grime=0.4,noise=(3.0,0),mottle=0.7)
A=Acc(); Z=0.012
def floorbox(key,cx,cy,sx,sy,ang,z0=Z,z1=Z+0.012,ch=0.004): A.box(key,cx,cy,z0,z1,sx,sy,ang,ch)
# safety ring around the pool
ring=[]; n=48
for i in range(n):
    a0=2*math.pi*i/n; a1=2*math.pi*(i+1)/n; am=(a0+a1)/2; r=4.55; L=2*r*math.sin(math.pi/n)+0.02
    floorbox(("floor ring","TRIM"),r*math.cos(am),r*math.sin(am),L,0.16,am+math.pi/2,ch=0.003)
    if i%2==0: floorbox(("floor ring hatch","IRON"),(r+0.17)*math.cos(am),(r+0.17)*math.sin(am),L,0.10,am+math.pi/2,ch=0.003)
# route lanes from the doors to the ring, with chevrons pointing at the pool
def lane(x0,y0,x1,y1,w=2.4):
    L=math.hypot(x1-x0,y1-y0); ang=math.atan2(y1-y0,x1-x0); cx,cy=(x0+x1)/2,(y0+y1)/2; ux,uy=math.cos(ang),math.sin(ang); nx,ny=-uy,ux
    A.box(("lane plate","LANE"),cx,cy,Z,Z+0.010,L,w,ang,0.004)
    for s in(-1,1): A.box(("lane edge","TRIM"),cx+nx*s*(w/2-0.06),cy+ny*s*(w/2-0.06),Z,Z+0.016,L,0.10,ang,0.003)
    k=int(L/1.1)
    for i in range(k):
        t=0.55+i*1.1; px,py=x0+ux*t,y0+uy*t
        for s in(-1,1): A.box(("lane chevron","TRIM"),px-ux*0.13+nx*s*0.20,py-uy*0.13+ny*s*0.20,Z,Z+0.014,0.62,0.10,ang+s*math.radians(-38)*1,0.003)
lane(-10.3,0,-5.0,0)       # MAIN ACCESS -> pool
lane(0,10.3,0,5.0)         # FUEL HANDLING -> pool  (drawn toward the pool)
lane(7.9,-7.9,3.7,-3.7)    # COOLING PLANT -> pool
# drain grates
for x,y in ((-6,-6),(6,6),(-6,6),(6,-6)):
    A.box(("drain","IRON"),x,y,Z,Z+0.02,0.9,0.5,math.pi/4,0.006)
# barrels and crates near the waste cask / west wall (sketchy dressing, angular 8-sided drums)
def drum(x,y,mk,h=0.95,r=0.30):
    bm=A.get(("drums",mk)); r_=bmesh.ops.create_cone(bm,cap_ends=True,segments=8,radius1=r,radius2=r,depth=h)
    for v in r_['verts']: v.co=Vector((v.co.x+x,v.co.y+y,v.co.z+h/2+0.0))
    A.box(("drum rings","IRON"),x,y,h*0.30,h*0.30+0.05,r*2.1,r*2.1,0.4,0.005); A.box(("drum rings","IRON"),x,y,h*0.70,h*0.70+0.05,r*2.1,r*2.1,0.4,0.005)
for i,(x,y,mk) in enumerate(((5.2,9.5,"DRUMR"),(5.9,9.9,"DRUMB"),(5.5,8.9,"DRUMR"),(-9.4,-8.0,"DRUMB"),(-9.9,-7.4,"DRUMR"))): drum(x,y,mk)
for x,y,a in ((-9.3,4.8,0.3),(-9.7,5.6,-0.2)): A.box(("crates","CRATE"),x,y,0,0.7,0.9,0.9,a,0.03)
A.box(("crates","CRATE"),-9.5,5.2,0.7,1.35,0.8,0.8,0.6,0.03)
mats={"LANE":M["LANE"],"TRIM":M["TRIM"],"IRON":M["IRON"],"DRUMR":M["DRUMR"],"DRUMB":M["DRUMB"],"CRATE":M["CRATE"]}
objs=A.build("23 R2 FLOOR AND DRESSING","R2 floor",mats)
# smooth off for angular look
for o in objs:
    for p in o.data.polygons: p.use_smooth=False
# ---- wall graphics: painted (non-emissive) numerals and stencils
coll=bpy.data.collections["22 R2 ARCHITECTURE"]
def text(txt,w,u,h,size,mat="PAINT",d=0.09,extra=0.0):
    p=w.pt(u,d); cu=bpy.data.curves.new("R2 gfx "+txt,'FONT'); cu.body=txt; cu.size=size; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=0.004
    ob=bpy.data.objects.new("R2 gfx "+txt.replace("\n"," "),cu); ob.location=(p.x,p.y,h); ob.rotation_euler=(math.pi/2,0,w.angle+math.pi); coll.objects.link(ob); cu.materials.append(M["PAINT"]); return ob
for i,w in enumerate(WALLS):
    text(f"0{i+1}",w,w.L/2 if i not in(1,4,6) else (w.L*0.2 if i!=4 else 9.4),10.4,1.9)
text("CRITICAL SHIFT\nENERGY SYSTEMS",WALLS[2],6.0,7.6,0.55)
text("DANGER\nAUTHORISED PERSONNEL ONLY",WALLS[0],6.0,3.4,0.22)
text("WATCH THE GREEN.\nIF IT TURNS, DON'T RUN.",WALLS[3],3.4,3.3,0.22)
text("SHIFT 04 - HANDOVER\nSYSTEMS NOMINAL",WALLS[5],3.4,3.3,0.20)
# hazard chevron bands on the door lintel bands
for wi in(1,4,6):
    w=WALLS[wi]; c={1:3.395,4:6.0,6:6.0}[wi]
bpy.ops.wm.save_as_mainfile(filepath=S+"/w23.blend"); print("ok",len(objs))
