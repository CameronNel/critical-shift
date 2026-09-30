"""Control room overhaul: 1990s look.  usage: python co1.py -- <src.blend> <dst.blend>
Removes the modern monitors / lockers / mimic panel / cold ceiling panel, then builds: 3 CRT terminals with keyboards and desktop cases,
desk clutter (phone, printer, lamp, floppies, notes, mugs), server rack with flickering LEDs, wall TV whose light follows its picture,
credenza + VCR, five propaganda posters, corkboard, aircon, clock, coat hooks, filing cabinet + boombox, dead plant, warm dim lighting."""
import bpy,sys,math,random
from mathutils import Vector
sys.path.insert(0,".")
from hs import K
import co_mat as CM
A_=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A_[0],A_[1]
bpy.ops.wm.open_mainfile(filepath=SRC); sc=bpy.context.scene
CM.STATE=bpy.data.objects["REACTOR_STATE"]
R=random.Random(1990)
# ================= 1. clean-out =================
def ext(o):
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return (min(q.x for q in p),max(q.x for q in p),min(q.y for q in p),max(q.y for q in p),min(q.z for q in p),max(q.z for q in p))
gone=0
for c in (bpy.data.collections["26 R2 CONTROL ROOM"],bpy.data.collections["20 CONTROL MEZZANINE"]):
    for o in list(c.objects):
        if o.type not in("MESH","CURVE","FONT"): continue
        e=ext(o); nm=o.name; kill=False
        if e[4]>=6.15 and -7.7<e[2] and e[3]<-6.3 and e[0]>=-4.5 and e[1]<=1.4: kill=True                       # modern monitors, keyboards, stands, desk papers, mug
        elif e[3]<-11.6 and e[4]>=6.7 and "mimic" in nm.lower() or (e[3]<-11.6 and e[4]>=6.7 and ("readout amber" in nm or "lamp amber" in nm or "state screen" in nm or "trim rust" in nm)): kill=True   # back-wall mimic panel and gizmos
        elif e[0]>=1.45 and e[1]<=2.0 and e[4]>=5.39 and e[5]<=7.05 and e[2]>=-11.6 and e[3]<=-9.3: kill=True    # storage lockers
        elif "cabinet handle" in nm or "ceiling panel" in nm: kill=True
        if kill: bpy.data.objects.remove(o,do_unlink=True); gone+=1
for l in list(bpy.data.objects):
    if l.type=="LIGHT" and l.name.startswith("LP control"): bpy.data.objects.remove(l,do_unlink=True)
print("CO1 removed",gone,"old pieces")
# ================= 2. materials / helpers =================
M=CM.make_materials(); imgA,imgB=CM.tv_images(); M["TVSCR"]=CM.tv_material(imgA,imgB)
M["MUG"]=CM.r2mat("R2 90s mug",(0.24,0.21,0.17),0.35,edge=None,grime=0.1,noise=(3,0),mottle=0.2)
coll=bpy.data.collections.new("31 R2 CONTROL 1990"); sc.collection.children.link(coll)
A=K()
RZ={'-y':0.0,'+y':math.pi,'-x':-math.pi/2,'+x':math.pi/2}
def text(body,x,y,z,facing,size,mat,align='CENTER',name="R2 cr text"):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.size=size; cu.align_x=align; cu.align_y='CENTER'; cu.extrude=0.0; cu.resolution_u=1
    ob=bpy.data.objects.new(name,cu); ob.location=(x,y,z); ob.rotation_euler=(math.pi/2,0,RZ[facing]); coll.objects.link(ob); cu.materials.append(mat); return ob
def quad(name,pts,uvs,mat):
    me=bpy.data.meshes.new(name); me.from_pydata(pts,[],[(0,1,2,3)]); me.update()
    uv=me.uv_layers.new(name="UVMap")
    for i,l in enumerate(me.loops): uv.data[l.index].uv=uvs[i]
    ob=bpy.data.objects.new(name,me); coll.objects.link(ob); me.materials.append(mat); return ob
def pt_light(name,loc,rgb,energy,expr=None,kind='POINT',rot=None,spot=None,size=None):
    ld=bpy.data.lights.new(name,kind); ld.color=rgb; ld.energy=energy
    if kind=='POINT': ld.shadow_soft_size=0.12
    if kind=='SPOT': ld.spot_size=math.radians(spot or 80); ld.spot_blend=0.6; ld.shadow_soft_size=0.05
    if kind=='AREA': ld.shape='RECTANGLE'; ld.size,ld.size_y=size
    lo=bpy.data.objects.new(name,ld); lo.location=loc
    if rot: lo.rotation_euler=rot
    coll.objects.link(lo)
    if expr: CM.drv(ld,'energy',None,expr,var_s=False)
    return lo
DESK_Z=6.20
# ================= 3. three CRT terminals =================
g="crt"
def terminal(cx,scr,phos_lines,case_h,tag):
    zc=DESK_Z
    A.bx((g,"PLASTIC"),cx-0.22,cx+0.22,-7.42,-6.92,zc,zc+case_h,0.012)                                   # desktop case
    A.fb((g,"PLASTICD"),'-y',-7.42,cx-0.19,cx+0.19,zc+0.012,zc+case_h-0.012,0.006,0.002)
    A.bx((g,"INK"),cx+0.02,cx+0.17,-7.425,-7.415,zc+0.02,zc+0.026,0.001); A.bx((g,"INK"),cx+0.02,cx+0.17,-7.425,-7.415,zc+0.045,zc+0.051,0.001)   # floppy slots
    A.bx((g,"PLASTICD"),cx-0.17,cx-0.06,-7.425,-7.415,zc+0.02,zc+0.05,0.002)
    A.fb(("crtled","LED_G0"),'-y',-7.42,cx-0.18,cx-0.165,zc+0.03,zc+0.04,0.008,0.0)
    z0=zc+case_h
    A.bx((g,"PLASTIC"),cx-0.11,cx+0.11,-7.14,-6.96,z0,z0+0.03,0.008)                                      # swivel base
    A.bx((g,"PLASTIC"),cx-0.06,cx+0.06,-7.10,-7.00,z0+0.03,z0+0.06,0.006)
    zb=z0+0.06
    A.bx((g,"PLASTIC"),cx-0.205,cx+0.205,-7.22,-7.04,zb,zb+0.34,0.02)                                     # front housing
    A.hull((g,"PLASTIC"),[(cx-0.19,-7.04,zb+0.02),(cx+0.19,-7.04,zb+0.02),(cx-0.19,-7.04,zb+0.32),(cx+0.19,-7.04,zb+0.32),
                          (cx-0.09,-6.66,zb+0.09),(cx+0.09,-6.66,zb+0.09),(cx-0.09,-6.66,zb+0.25),(cx+0.09,-6.66,zb+0.25)],0.008)   # rear cone
    A.fb((g,"PLASTIC"),'-y',-7.22,cx-0.212,cx+0.212,zb-0.005,zb+0.345,0.018,0.01)                          # bezel
    A.fb((g,"PLASTICD"),'-y',-7.238,cx-0.165,cx+0.165,zb+0.055,zb+0.315,0.006,0.002)                        # screen surround
    A.fb((g,"SCRBG_"+scr[-1]),'-y',-7.244,cx-0.15,cx+0.15,zb+0.07,zb+0.30,0.004,0.0)                                     # phosphor glass
    A.fb((g,"KEY"),'-y',-7.238,cx-0.16,cx-0.07,zb+0.012,zb+0.026,0.004,0.001)                              # badge
    A.fb(("crtled","LED_G1"),'-y',-7.238,cx+0.135,cx+0.148,zb+0.015,zb+0.027,0.004,0.0)                     # power lamp
    for k in range(2): A.prism((g,"KEY"),(cx+0.17-k*0.028,-7.239,zb+0.021),(cx+0.17-k*0.028,-7.25,zb+0.021),0.009,0.009,8)   # knobs
    for k in range(7): A.bx((g,"INK"),cx-0.13+k*0.043,cx-0.115+k*0.043,-7.16,-6.98,zb+0.34,zb+0.342,0.0)                       # top vents
    # keyboard (legacy 101-key): tray + key grid
    kx=cx
    A.hull((g,"PLASTIC"),[(kx-0.23,-7.585,zc),(kx+0.23,-7.585,zc),(kx-0.23,-7.385,zc),(kx+0.23,-7.385,zc),
                          (kx-0.23,-7.585,zc+0.016),(kx+0.23,-7.585,zc+0.016),(kx-0.23,-7.385,zc+0.03),(kx+0.23,-7.385,zc+0.03)],0.004)
    for r in range(5):
        y=-7.565+r*0.033; zz=zc+0.016+r*0.0035
        n=13 if r<4 else 0
        for i in range(n): A.bx((g,"KEY"),kx-0.20+i*0.0325,kx-0.20+i*0.0325+0.027,y,y+0.027,zz,zz+0.012,0.002)
    A.bx((g,"KEY"),kx-0.09,kx+0.09,-7.565+4*0.033,-7.565+4*0.033+0.027,zc+0.016+4*0.0035,zc+0.016+4*0.0035+0.012,0.002)   # space bar
    A.bx((g,"KEY"),kx+0.20,kx+0.225,-7.565,-7.42,zc+0.02,zc+0.03,0.002)                                      # numpad edge cue
    A.prism((g,"CABLE"),(kx,-7.385,zc+0.02),(kx,-7.30,zc+0.005),0.004,0.004,6); A.prism((g,"CABLE"),(kx,-7.30,zc+0.005),(kx+0.04,-7.0,zc+0.02),0.004,0.004,6)
    # mouse + pad
    mx=cx+0.33
    A.bx((g,"INK"),mx-0.10,mx+0.10,-7.56,-7.40,zc,zc+0.004,0.001)
    A.hull((g,"PLASTIC"),[(mx-0.03,-7.50,zc+0.004),(mx+0.03,-7.50,zc+0.004),(mx-0.028,-7.43,zc+0.004),(mx+0.028,-7.43,zc+0.004),
                          (mx-0.025,-7.49,zc+0.03),(mx+0.025,-7.49,zc+0.03),(mx-0.022,-7.44,zc+0.026),(mx+0.022,-7.44,zc+0.026)],0.006)
    A.prism((g,"CABLE"),(mx,-7.43,zc+0.012),(mx-0.03,-7.36,zc+0.006),0.003,0.003,6); A.prism((g,"CABLE"),(mx-0.03,-7.36,zc+0.006),(cx+0.21,-7.10,zc+0.03),0.003,0.003,6)
    # phosphor text (separate curve objects, same material family)
    for i,line in enumerate(phos_lines):
        text(line,cx-0.135,-7.2495,zb+0.285-i*0.032,'-y',0.021,M[scr],'LEFT',f"R2 crt text {tag}")
    z_light=zb+0.185
    pt_light(f"R2 crt glow {tag}",(cx,-7.55,z_light),(0.2,1.0,0.3) if scr=="SCR_G" else (1.0,0.55,0.1),9,"9*(0.92+0.08*sin(frame*1.7))")
terminal(-3.35,"SCR_G",["> BANK A  8.4 M  OK","> BANK B  7.4 M  OK","> COOLANT  P-10  RUN","> GRID  DEMAND  74%","> STABILITY","> _"],0.10,"T1")
terminal(-1.75,"SCR_A",["LOAD SHEDDING PLAN","SECTOR 1   ....  ON","SECTOR 2   ....  ON","SECTOR 3   ....  ON","SECTOR 4   ....  OFF","READY_"],0.12,"T2")
terminal(-0.15,"SCR_G",["SHIFT LOG  04","22:41  ROUTINE","23:10  ROUTINE","00:02  NOTHING","       UNUSUAL","> _"],0.09,"T3")
# ================= 4. desk clutter =================
g="desk"
def cyl(key,x,y,z0,z1,r,seg=10): A.prism(key,(x,y,z0),(x,y,z1),r,r,seg,0)
# desk lamp (banker style gooseneck)
lx,ly=1.12,-6.72
cyl((g,"PLASTICD"),lx,ly,DESK_Z,DESK_Z+0.025,0.075); A.prism((g,"RACK"),(lx,ly,DESK_Z+0.025),(lx-0.05,ly-0.05,DESK_Z+0.28),0.008,0.008,6)
A.prism((g,"RACK"),(lx-0.05,ly-0.05,DESK_Z+0.28),(lx-0.16,ly-0.14,DESK_Z+0.36),0.008,0.008,6)
A.hull((g,"PLASTICD"),[(lx-0.26,ly-0.24,DESK_Z+0.33),(lx-0.10,ly-0.10,DESK_Z+0.33),(lx-0.25,ly-0.09,DESK_Z+0.33),(lx-0.11,ly-0.25,DESK_Z+0.33),
                       (lx-0.23,ly-0.21,DESK_Z+0.40),(lx-0.13,ly-0.13,DESK_Z+0.40),(lx-0.22,ly-0.12,DESK_Z+0.40),(lx-0.14,ly-0.22,DESK_Z+0.40)],0.006)
A.prism((g,"LAMP"),(lx-0.18,ly-0.17,DESK_Z+0.33),(lx-0.18,ly-0.17,DESK_Z+0.31),0.03,0.02,8)
pt_light("R2 desk lamp",(lx-0.18,ly-0.17,DESK_Z+0.30),(1.0,0.66,0.34),55,None,'SPOT',(math.pi,0,0),85)
# push-button phone with coiled handset cord
px,py=0.86,-7.22
A.hull((g,"PLASTIC"),[(px-0.11,py-0.10,DESK_Z),(px+0.11,py-0.10,DESK_Z),(px-0.11,py+0.10,DESK_Z),(px+0.11,py+0.10,DESK_Z),
                      (px-0.10,py-0.09,DESK_Z+0.045),(px+0.10,py-0.09,DESK_Z+0.045),(px-0.10,py+0.10,DESK_Z+0.075),(px+0.10,py+0.10,DESK_Z+0.075)],0.006)
for r_ in range(4):
    for c_ in range(3): A.bx((g,"KEY"),px-0.045+c_*0.034,px-0.045+c_*0.034+0.026,py-0.075+r_*0.03,py-0.075+r_*0.03+0.022,DESK_Z+0.048+r_*0.006,DESK_Z+0.056+r_*0.006,0.002)
A.hull((g,"PLASTIC"),[(px-0.13,py-0.03,DESK_Z+0.09),(px+0.13,py-0.03,DESK_Z+0.09),(px-0.13,py+0.05,DESK_Z+0.09),(px+0.13,py+0.05,DESK_Z+0.09),
                      (px-0.10,py-0.03,DESK_Z+0.125),(px+0.10,py-0.03,DESK_Z+0.125),(px-0.10,py+0.05,DESK_Z+0.125),(px+0.10,py+0.05,DESK_Z+0.125)],0.008)   # handset
A.hull((g,"PLASTIC"),[(px-0.075,py-0.03,DESK_Z+0.06),(px-0.045,py-0.03,DESK_Z+0.06),(px-0.075,py+0.05,DESK_Z+0.06),(px-0.045,py+0.05,DESK_Z+0.06),
                      (px-0.075,py-0.03,DESK_Z+0.09),(px-0.045,py-0.03,DESK_Z+0.09),(px-0.075,py+0.05,DESK_Z+0.09),(px-0.045,py+0.05,DESK_Z+0.09)],0.004)   # cradle post
prev=None
for t in range(0,49):
    a=t/48*2*math.pi*7; p=(px+0.135+0.02*math.cos(a)*0.0+ (t/48)*0.06, py-0.06+0.014*math.cos(a), DESK_Z+0.04+0.014*math.sin(a)+ (t/48)*0.0)
    if prev: A.prism((g,"CABLE"),prev,p,0.0028,0.0028,5)
    prev=p
# floppies, disk box, notepad + pens, mugs, calculator, stapler, binder
for k,(fx,fy,ang) in enumerate(((-2.62,-7.02,0.4),(-2.50,-6.95,-0.2),(-2.42,-7.08,0.9))):
    A.box((g,"PLASTICD"),fx,fy,DESK_Z,DESK_Z+0.004,0.09,0.09,ang,0.001); A.box((g,"RACK"),fx+0.01*math.cos(ang),fy+0.03*math.sin(ang+1.0),DESK_Z+0.004,DESK_Z+0.006,0.04,0.03,ang,0.0)
    A.box((g,"PAPER"),fx,fy-0.02,DESK_Z+0.004,DESK_Z+0.0055,0.06,0.03,ang,0.0)
A.bx((g,"PLASTICD"),-2.22,-2.02,-7.15,-7.03,DESK_Z,DESK_Z+0.09,0.006)
A.bx((g,"PAPER"),-2.18,-2.06,-7.152,-7.15,DESK_Z+0.03,DESK_Z+0.07,0.0)
A.box((g,"PAPER"),-2.55,-7.27,DESK_Z,DESK_Z+0.02,0.15,0.21,0.15,0.002); A.box((g,"PAPER"),-2.55,-7.27,DESK_Z+0.02,DESK_Z+0.0205,0.14,0.20,0.15,0.0)
for i in range(6): A.bx((g,"P_INK"),-2.62,-2.48,-7.33+i*0.02,-7.325+i*0.02,DESK_Z+0.0206,DESK_Z+0.0208,0.0)
A.prism((g,"P_NAVY"),(-2.47,-7.34,DESK_Z+0.027),(-2.40,-7.16,DESK_Z+0.027),0.0055,0.0055,6); A.prism((g,"P_GOLD"),(-2.60,-7.40,DESK_Z+0.006),(-2.50,-7.44,DESK_Z+0.006),0.0045,0.0045,6)
for mx_,my_,cf in ((-0.95,-7.45,0),(0.38,-6.62,1)):
    cyl((g,"MUG"),mx_,my_,DESK_Z,DESK_Z+0.09,0.038,10); A.prism((g,"MUG"),(mx_+0.06,my_,DESK_Z+0.06),(mx_+0.06,my_,DESK_Z+0.03),0.02,0.02,8,0) if False else None
    A.bx((g,"MUG"),mx_+0.036,mx_+0.062,my_-0.005,my_+0.005,DESK_Z+0.03,DESK_Z+0.07,0.002); cyl((g,"INK"),mx_,my_,DESK_Z+0.084,DESK_Z+0.086,0.032,10)
cyl((g,"RACK"),-1.20,-6.72,DESK_Z,DESK_Z+0.10,0.04,10)                                                     # pen cup
for k in range(5): A.prism((g,["P_RED","P_NAVY","P_GOLD","P_INK","P_RED"][k]),(-1.20,-6.72,DESK_Z+0.09),(-1.20+0.02*(k-2),-6.72+0.012*(k-2),DESK_Z+0.19),0.004,0.004,6)
A.bx((g,"PLASTICD"),0.30,0.42,-7.55,-7.42,DESK_Z,DESK_Z+0.02,0.004)                                          # calculator
for r_ in range(4):
    for c_ in range(3): A.bx((g,"KEY"),0.312+c_*0.034,0.312+c_*0.034+0.026,-7.535+r_*0.03,-7.535+r_*0.03+0.022,DESK_Z+0.02,DESK_Z+0.026,0.0)
A.bx((g,"P_RED"),-3.98,-3.72,-7.18,-6.92,DESK_Z,DESK_Z+0.035,0.004); A.bx((g,"PAPER"),-3.96,-3.74,-7.16,-6.94,DESK_Z+0.035,DESK_Z+0.05,0.0)   # open shift binder
for i in range(5): A.bx((g,"P_INK"),-3.94,-3.76,-7.13+i*0.04,-7.125+i*0.04,DESK_Z+0.0505,DESK_Z+0.0515,0.0)
# ================= 5. printer stand + dot-matrix printer =================
g="printer"
A.bx((g,"IRON"),1.28,1.72,-7.30,-6.80,0.0+5.4,5.4+0.03,0.004)
for x_ in (1.30,1.70):
    for y_ in (-7.28,-6.82): A.bx((g,"IRON"),x_-0.015,x_+0.015,y_-0.015,y_+0.015,5.4,5.4+0.66,0.003)
A.bx((g,"IRON"),1.28,1.72,-7.30,-6.80,5.4+0.66,5.4+0.69,0.004)
A.bx((g,"PAPER"),1.36,1.62,-7.22,-6.90,5.4+0.06,5.4+0.32,0.004)                                            # box of tractor paper
for i in range(9): A.bx((g,"P_NAVY"),1.36,1.62,-7.221,-7.22,5.4+0.08+i*0.026,5.4+0.083+i*0.026,0.0)
A.hull((g,"PLASTIC"),[(1.33,-7.26,6.09),(1.67,-7.26,6.09),(1.33,-6.86,6.09),(1.67,-6.86,6.09),(1.35,-7.24,6.21),(1.65,-7.24,6.21),(1.35,-6.92,6.29),(1.65,-6.92,6.29)],0.008)
A.bx((g,"PLASTICD"),1.37,1.63,-7.20,-6.96,6.29,6.295,0.0)                                                 # platen slot
A.hull((g,"PAPER"),[(1.40,-6.91,6.29),(1.60,-6.91,6.29),(1.40,-6.90,6.29),(1.60,-6.90,6.29),(1.40,-6.93,6.62),(1.60,-6.93,6.62),(1.40,-6.925,6.62),(1.60,-6.925,6.62)],0.0)  # paper ribbon
A.bx((g,"PAPER"),1.40,1.60,-7.05,-6.93,6.62,6.625,0.0)
A.hull((g,"PAPER"),[(1.40,-7.24,6.09),(1.60,-7.24,6.09),(1.40,-7.242,6.09),(1.60,-7.242,6.09),(1.40,-7.30,5.98),(1.60,-7.30,5.98),(1.40,-7.302,5.98),(1.60,-7.302,5.98)],0.0)  # printed sheet spilling out
for i in range(4): A.fb(("printled","LED_G2" if i%2 else "LED_A1"),'-y',-7.26,1.38+i*0.045,1.395+i*0.045,6.13,6.145,0.004,0.0)
# ================= 6. server rack (east wall, front faces -x) =================
g="rack"; RX=1.15; RY0,RY1=-10.75,-10.15
A.bx((g,"PLASTICD"),RX,2.0,RY0,RY1,5.4,5.5,0.006)
for yy in (RY0,RY1-0.03):
    A.bx((g,"RACK"),RX,2.0,yy,yy+0.03,5.5,7.36,0.004)
A.bx((g,"RACK"),RX,2.0,RY0,RY1,7.33,7.37,0.004)
A.bx((g,"RACK"),1.97,2.0,RY0,RY1,5.5,7.36,0.003)
for yy in (RY0+0.03,RY1-0.06): A.bx((g,"INK"),RX-0.012,RX+0.02,yy,yy+0.03,5.5,7.33,0.0)                    # mounting rails
z=5.53
def face(h,mat="RACK"): A.fb((g,mat),'-x',RX,RY0+0.03,RY1-0.03,z,z+h-0.004,0.022,0.002)
def rled(y,zz,col,size=0.0075):
    A.fb(("rackled",f"LED_{col}{R.randrange(4)}"),'-x',RX-0.02,y-size,y+size,zz-size,zz+size,0.004,0.0)
cx_=(RY0+RY1)/2
# UPS
face(0.28); A.fb((g,"INK"),'-x',RX-0.02,RY0+0.06,RY1-0.16,z+0.04,z+0.24,0.003,0.0)
for i in range(6): rled(RY1-0.10,z+0.05+i*0.032,"G" if i<4 else "A")
z+=0.28
face(0.045,"PLASTICD"); z+=0.045
# disk array
face(0.36)
for r_ in range(6):
    for c_ in range(2):
        y0=RY0+0.05+c_*0.245
        A.fb((g,"PLASTICD"),'-x',RX-0.02,y0,y0+0.235,z+0.02+r_*0.055,z+0.065+r_*0.055,0.006,0.001)
        A.fb((g,"INK"),'-x',RX-0.026,y0+0.02,y0+0.15,z+0.03+r_*0.055,z+0.04+r_*0.055,0.002,0.0)
        rled(y0+0.19,z+0.043+r_*0.055,"G"); rled(y0+0.21,z+0.043+r_*0.055,"A")
z+=0.36
# network switch (24 ports)
face(0.045,"PLASTICD")
for i in range(24): A.fb((g,"INK"),'-x',RX-0.02,RY0+0.06+i*0.0225,RY0+0.075+i*0.0225,z+0.008,z+0.022,0.003,0.0); rled(RY0+0.0675+i*0.0225,z+0.036,"G")
z+=0.045
# modem bank
face(0.18)
for i in range(8):
    y0=RY0+0.05+i*0.061; A.fb((g,"PLASTICD"),'-x',RX-0.02,y0,y0+0.055,z+0.02,z+0.16,0.005,0.001)
    for k in range(3): rled(y0+0.028,z+0.05+k*0.04,["G","A","R"][k])
z+=0.18
# tape drive
face(0.27); A.fb((g,"INK"),'-x',RX-0.02,RY0+0.07,RY0+0.36,z+0.05,z+0.22,0.004,0.0)
A.prism((g,"RACK"),(RX-0.03,RY0+0.135,z+0.135),(RX-0.03,RY0+0.135,z+0.135),0.0,0.0,4) if False else None
for k in range(2): A.prism((g,"PLASTIC"),(RX-0.026,RY0+0.13+k*0.13,z+0.135),(RX-0.032,RY0+0.13+k*0.13,z+0.135),0.05,0.05,12,0)
for k in range(4): rled(RY1-0.10,z+0.05+k*0.045,["G","A","G","R"][k])
z+=0.27
# patch panel with hanging cables
face(0.09,"PLASTICD")
for i in range(24): A.fb((g,"INK"),'-x',RX-0.02,RY0+0.06+i*0.0225,RY0+0.075+i*0.0225,z+0.02,z+0.05,0.003,0.0)
for i in range(0,24,3): A.prism((g,"CABLE"),(RX-0.03,RY0+0.0675+i*0.0225,z+0.02),(RX-0.06,RY0+0.0675+i*0.0225+0.03*((i%2)*2-1),z-0.17),0.004,0.004,5)
z+=0.09
# second disk array
face(0.36)
for r_ in range(6):
    for c_ in range(2):
        y0=RY0+0.05+c_*0.245
        A.fb((g,"PLASTICD"),'-x',RX-0.02,y0,y0+0.235,z+0.02+r_*0.055,z+0.065+r_*0.055,0.006,0.001)
        rled(y0+0.19,z+0.043+r_*0.055,"G"); rled(y0+0.21,z+0.043+r_*0.055,"A")
z+=0.36
face(0.045,"PLASTICD"); z+=0.045
face(0.09); A.fb((g,"PLASTICD"),'-x',RX-0.02,RY0+0.06,RY1-0.06,z+0.03,z+0.06,0.02,0.002); z+=0.09       # keyboard drawer
# plate + cable bundle to ceiling + activity light
A.fb((g,"PAPER"),'-x',RX,cx_-0.14,cx_+0.14,7.36+0.0,7.36+0.001,0.001,0.0)
A.prism((g,"CABLE"),(1.90,cx_-0.10,7.37),(1.92,cx_-0.10,8.80),0.03,0.03,8); A.prism((g,"CABLE"),(1.86,cx_+0.12,7.37),(1.94,cx_+0.12,8.80),0.022,0.022,8)
pt_light("R2 rack glow",(RX-0.35,cx_,6.5),(0.5,1.0,0.35),11,"11*(0.65+0.35*max(0,sin(frame*0.9)*sin(frame*0.31)))")
pt_light("R2 rack glow amber",(RX-0.30,cx_,6.0),(1.0,0.5,0.1),8,"8*(0.6+0.4*max(0,sin(frame*1.4+1)*sin(frame*0.23)))")
# ================= 7. TV wall (back wall, front faces +y) =================
g="tv"; BW=-11.84
CX=-1.30
A.bx((g,"DESK"),CX-1.25,CX+1.25,-11.90,-11.42,5.4,6.05,0.012)                                        # credenza
A.bx((g,"DESK"),CX-1.29,CX+1.29,-11.90,-11.40,6.05,6.075,0.008)
for i in range(4):
    x0=CX-1.20+i*0.60; A.fb((g,"INK"),'+y',-11.42,x0+0.02,x0+0.56,5.5,6.0,0.008,0.004); A.fb((g,"TRIM"),'+y',-11.42+0.008,x0+0.24,x0+0.34,5.72,5.76,0.012,0.002)
A.bx((g,"PLASTICD"),CX-0.20,CX+0.20,-11.84,-11.52,6.075,6.165,0.008)                                # VCR
A.fb((g,"INK"),'+y',-11.52,CX-0.17,CX+0.02,6.09,6.14,0.003,0.0); A.fb((g,"RACK"),'+y',-11.52,CX+0.05,CX+0.17,6.11,6.13,0.002,0.0)
for k in range(4): A.fb(("vcrled","LED_A0"),'+y',-11.52,CX+0.10+k*0.0,CX+0.115+k*0.0,6.14,6.15,0.0,0.0) if False else None
A.fb(("vcrled","LED_A1"),'+y',-11.52,CX-0.02,CX+0.03,6.12,6.15,0.004,0.0)
for k,(ty,zz) in enumerate(((0,6.165),(0,6.195),(0,6.225))):                                            # stack of VHS tapes
    A.bx((g,"PLASTICD"),CX+0.42,CX+0.61,-11.80,-11.70,zz-0.09+0.0,zz-0.09+0.03,0.002); A.fb((g,"PAPER"),'+y',-11.70,CX+0.43,CX+0.6,zz-0.085,zz-0.065,0.001,0.0)
for sgn in (-1,1):
    sx=CX+sgn*1.03; A.bx((g,"PLASTICD"),sx-0.09,sx+0.09,-11.86,-11.62,6.075,6.40,0.01); A.prism((g,"INK"),(sx,-11.62,6.16),(sx,-11.615,6.16),0.055,0.055,14,0); A.prism((g,"INK"),(sx,-11.62,6.30),(sx,-11.615,6.30),0.03,0.03,12,0)
TVW,TVH,TVZ=1.26,0.71,7.02
A.bx((g,"PLASTICD"),CX-TVW/2-0.02,CX+TVW/2+0.02,-11.84,-11.79,TVZ-TVH/2-0.02,TVZ+TVH/2+0.02,0.012)  # TV body
A.bx((g,"PLASTICD"),CX-0.2,CX+0.2,-11.84,-11.80,TVZ-0.2,TVZ+0.2,0.006)
A.bx((g,"RACK"),CX-0.16,CX+0.16,-11.86,-11.84,TVZ-0.15,TVZ+0.15,0.004)                              # wall bracket
scr=quad("R2 tv screen",[(CX+TVW/2,-11.787,TVZ-TVH/2),(CX-TVW/2,-11.787,TVZ-TVH/2),(CX-TVW/2,-11.787,TVZ+TVH/2),(CX+TVW/2,-11.787,TVZ+TVH/2)],[(0,0),(1,0),(1,1),(0,1)],M["TVSCR"])
A.prism((g,"CABLE"),(CX+0.4,-11.83,TVZ-0.34),(CX+0.42,-11.82,6.08),0.005,0.005,6)
CM.tv_light((CX,-11.70,TVZ),size=(TVW*0.9,TVH*0.9),energy=320)
# ================= 8. posters (face +y on back wall, -x on east wall, +x on west wall) =================
def poster(face,p,lc,zc,w,h,kind,head,sub,field,art):
    def P(u,v,d):
        if face=='+y': return (lc-u,p+d,zc+v)
        if face=='-y': return (lc+u,p-d,zc+v)
        if face=='-x': return (p-d,lc-u,zc+v)
        return (p+d,lc+u,zc+v)
    def rect(key,u0,u1,v0,v1,d0,d1,ang=0.0,uc=None,vc=None,ch=0.002):
        uc=(u0+u1)/2 if uc is None else uc; vc=(v0+v1)/2 if vc is None else vc; pts=[]
        for uu in (u0,u1):
            for vv in (v0,v1):
                du,dv=uu-(u0+u1)/2,vv-(v0+v1)/2; ru=(u0+u1)/2+du*math.cos(ang)-dv*math.sin(ang); rv=(v0+v1)/2+du*math.sin(ang)+dv*math.cos(ang)
                for d in (d0,d1): pts.append(P(ru,rv,d))
        A.hull(key,pts,ch)
    def disc(key,u,v,r,d0,d1,seg=18): A.prism(key,P(u,v,d0),P(u,v,d1),r,r,seg,0)
    g="poster"; hw,hh=w/2,h/2
    rect((g,"PAPER"),-hw,hw,-hh,hh,0,0.008)
    rect((g,field),-hw+0.025,hw-0.025,-hh+0.025,hh-0.025,0.008,0.011)
    ink="P_GOLD" if field!="P_GOLD" else "P_RED"; d0,d1=0.011,0.014
    if art=="gear":
        disc((g,ink),0,0.06,0.15,d0,d1); disc((g,field),0,0.06,0.075,d1,d1+0.001)
        for k in range(8): rect((g,ink),-0.03,0.03,0.13,0.21,d0,d1,ang=k*math.pi/4,uc=0,vc=0.06)
        rect((g,"P_RED"),-hw+0.025,hw-0.025,-hh+0.025,-hh+0.20,d1,d1+0.001)
    elif art=="bulb":
        disc((g,ink),0,0.10,0.13,d0,d1); rect((g,ink),-0.05,0.05,-0.08,0.0,d0,d1); rect((g,"P_INK"),-0.05,0.05,-0.075,-0.06,d1,d1+0.001)
        for k in range(8): rect((g,ink),-0.008,0.008,0.17,0.24,d0,d1,ang=(k-3.5)*0.5,uc=0,vc=0.10)
        rect((g,"P_NAVY"),-hw+0.025,hw-0.025,-hh+0.025,-hh+0.20,d1,d1+0.001)
    elif art=="check":
        disc((g,ink),0,0.05,0.19,d0,d1,24); disc((g,field),0,0.05,0.155,d1,d1+0.001,24)
        rect((g,ink),-0.09,-0.06,-0.03,0.03,d1,d1+0.002,ang=0.75,uc=-0.075,vc=0.0); rect((g,ink),-0.03,0.0,-0.02,0.15,d1,d1+0.002,ang=-0.6,uc=0.05,vc=0.06)
    elif art=="eye":
        pts=[]
        for k in range(14):
            a=2*math.pi*k/14; pts+= [P(0.16*math.cos(a)*1.2,0.05+0.085*math.sin(a),d0),P(0.16*math.cos(a)*1.2,0.05+0.085*math.sin(a),d1)]
        A.hull((g,"P_RED"),pts,0.002); disc((g,"P_INK"),0,0.05,0.06,d1,d1+0.002); disc((g,"PAPER"),0.02,0.07,0.014,d1+0.002,d1+0.003,10)
        for k in range(9): rect((g,"P_RED"),-0.006,0.006,0.16,0.20,d0,d1,ang=(k-4)*0.32,uc=0,vc=0.05)
    elif art=="warn":
        A.hull((g,ink),[P(-0.20,-0.10,d0),P(0.20,-0.10,d0),P(0,0.24,d0),P(-0.20,-0.10,d1),P(0.20,-0.10,d1),P(0,0.24,d1)],0.002)
        rect((g,"P_INK"),-0.018,0.018,-0.05,0.12,d1,d1+0.002); disc((g,"P_INK"),0,-0.075,0.022,d1,d1+0.002,10)
    tz=hh-0.075
    for i,ln in enumerate(head.split("\n")): text(ln,*P(0,tz-i*0.062,0.0165),face,0.052,M["PAPER"] if field in("P_NAVY","P_RED") else M["P_INK"],'CENTER',"R2 poster head")
    for i,ln in enumerate(sub.split("\n")): text(ln,*P(0,-hh+0.115-i*0.05,d1+0.0035),face,0.034,M["P_GOLD"] if field!="P_GOLD" else M["P_INK"],'CENTER',"R2 poster sub")
BWP=-11.84
poster('+y',BWP,-3.75,7.35,0.70,0.98,"", "THE MACHINE\nPROVIDES.","YOU SUSTAIN.","P_NAVY","gear")
poster('+y',BWP,0.45,7.30,0.70,0.98,"", "YOUR SHIFT KEEPS\nTHE LIGHTS ON","THANK YOU,\nVALUED EMPLOYEE","P_RED","bulb")
poster('-x',2.0,-7.75,6.95,0.70,0.98,"", "COMPLIANCE\nIS COMFORT.","","P_NAVY","check")
poster('-x',2.0,-6.75,6.95,0.70,0.98,"", "QUESTIONS ARE\nINEFFICIENCY.","TRUST THE OUTPUT.","P_GOLD","eye")
poster('+x',-4.8,-6.05+0.0,7.55,0.0001,0.0001,"","","","P_RED","") if False else None
poster('+x',-4.8,-8.95,7.95,0.60,0.80,"", "REPORT NOTHING\nUNUSUAL.","NOTHING UNUSUAL\nIS REPORTED.","P_RED","warn")
# ================= 9. wall fittings =================
g="wall"
# corkboard (west wall, faces +x)
A.fb((g,"CORK"),'+x',-4.8,-9.75,-8.15,6.2,6.75,0.018,0.004) if False else None
A.fb((g,"CORK"),'+x',-4.8,-9.75,-9.35,6.55,7.15,0.018,0.004) if False else None
# corkboard sits under the poster: y -9.75..-8.15, z 6.05..6.95 would overlap the poster; place lower
A.fb((g,"CORK"),'+x',-4.8,-9.70,-8.20,6.02,6.72,0.018,0.004)
for (y0,y1,z0,z1) in ((-9.70,-8.20,6.02,6.045),(-9.70,-8.20,6.695,6.72)): A.fb((g,"TRIM"),'+x',-4.8,y0-0.02,y1+0.02,z0-0.0,z1,0.024,0.002)
for (y0,y1,z0,z1) in ((-9.72,-9.70,6.02,6.72),(-8.20,-8.18,6.02,6.72)): A.fb((g,"TRIM"),'+x',-4.8,y0,y1,z0,z1,0.024,0.002)
for k in range(9):
    y=-9.62+R.random()*1.32; zz=6.08+R.random()*0.5; pw=0.11+R.random()*0.06; ph=0.14+R.random()*0.05
    A.fb((g,"PAPER"),'+x',-4.782,y,y+pw,zz,zz+ph,0.004,0.0); A.fb((g,"RACK" if k%2 else "P_RED"),'+x',-4.778,y+pw/2-0.005,y+pw/2+0.005,zz+ph-0.02,zz+ph-0.01,0.004,0.0)
    for j in range(3): A.fb((g,"P_INK"),'+x',-4.778,y+0.015,y+pw-0.015,zz+0.02+j*0.03,zz+0.024+j*0.03,0.001,0.0)
text("SHIFT 04 ROSTER\nA. VANCE   B. OKAFOR\nC. LINDQVIST",-4.775,-9.06,6.62,'+x',0.019,M["P_INK"],'CENTER',"R2 roster")
A.fb((g,"PAPER"),'+x',-4.782,-9.30,-8.78,6.55,6.68,0.004,0.0) if False else None
# coat hooks + hard hat + jacket (west wall)
A.fb((g,"IRON"),'+x',-4.8,-8.10,-7.60,7.05,7.10,0.03,0.003)
for y in (-8.03,-7.85,-7.67): A.prism((g,"TRIM"),(-4.77,y,7.07),(-4.66,y,7.10),0.008,0.008,6)
A.hull((g,"P_GOLD"),[(-4.76,-8.03+0.0,6.86),(-4.60,-8.03,6.86),(-4.76,-8.03+0.0,7.05),(-4.60,-8.03,7.05),(-4.76,-8.11,6.86),(-4.60,-8.11,6.86),(-4.76,-8.07,7.03),(-4.62,-8.07,7.03)],0.01) if False else None
for k in range(10):
    a=math.pi*k/9; A.prism((g,"P_GOLD"),(-4.70,-8.03,6.98),(-4.70+0.10*math.cos(a)*0.3,-8.03+0.0,6.98+0.02),0.0,0.0,4) if False else None
A.hull((g,"P_GOLD"),[(-4.74+0.10*math.cos(a),-8.03+0.10*math.sin(a)*0.0,6.90+0.09*math.sin(a)) for a in [math.pi*k/8 for k in range(9)]]+[(-4.74+0.10*math.cos(a),-8.03-0.0,6.90+0.09*math.sin(a)) for a in [math.pi*k/8 for k in range(9)]],0.004) if False else None
A.hull((g,"P_GOLD"),[(-4.60,-8.10,6.90),(-4.75,-8.10,6.90),(-4.60,-7.96,6.90),(-4.75,-7.96,6.90),(-4.65,-8.09,7.0),(-4.73,-8.09,7.0),(-4.65,-7.97,7.0),(-4.73,-7.97,7.0)],0.02)   # hard hat on hook
A.hull((g,"FAB"),[(-4.74,-7.82,6.2),(-4.62,-7.82,6.2),(-4.74,-7.58,6.2),(-4.62,-7.58,6.2),(-4.74,-7.80,7.0),(-4.66,-7.80,7.0),(-4.74,-7.60,7.0),(-4.66,-7.60,7.0)],0.02)          # work jacket hanging
# aircon (east wall, faces -x), high
g="ac"; ACY0,ACY1=-9.95,-8.75
A.fb((g,"ACW"),'-x',2.0,ACY0,ACY1,7.72,8.22,0.20,0.03)
A.fb((g,"ACW"),'-x',1.80,ACY0+0.02,ACY1-0.02,7.74,8.20,0.02,0.02)
A.hull((g,"PLASTICD"),[(1.76,ACY0+0.05,7.70),(1.76,ACY1-0.05,7.70),(1.72,ACY0+0.05,7.78),(1.72,ACY1-0.05,7.78),(1.76,ACY0+0.05,7.74),(1.76,ACY1-0.05,7.74),(1.74,ACY0+0.05,7.76),(1.74,ACY1-0.05,7.76)],0.004)  # louvre flap
for k in range(8): A.fb((g,"INK"),'-x',1.80,ACY0+0.05,ACY1-0.05,7.86+k*0.04,7.875+k*0.04,0.004,0.0)
A.fb((g,"INK"),'-x',1.80,ACY1-0.30,ACY1-0.10,8.12,8.17,0.003,0.0); A.fb(("acled","LED_G3"),'-x',1.80,ACY1-0.27,ACY1-0.25,8.135,8.15,0.005,0.0); A.fb(("acled","LED_A2"),'-x',1.80,ACY1-0.22,ACY1-0.20,8.135,8.15,0.005,0.0)
A.prism((g,"TRIM"),(1.98,ACY0+0.05,7.76),(1.98,ACY0+0.05,8.80),0.012,0.012,8); A.prism((g,"CABLE"),(1.99,ACY0+0.09,7.74),(1.99,ACY0+0.09,8.80),0.009,0.009,8)   # refrigerant / condensate lines to ceiling
A.prism((g,"CABLE"),(1.90,ACY0+0.2,7.72),(1.92,ACY0+0.2,7.55),0.006,0.006,6)                              # drip line
# ceiling: warm fixtures, vents, smoke detector
g="ceil"
for k,(y,mk) in enumerate(((-7.55,"CEIL"),(-9.55,"CEIL_F"),(-11.35,"CEIL"))):
    A.bx((g,"IRON"),-2.05,-0.75,y-0.16,y+0.16,8.72,8.80,0.006); A.bx((g,mk),-2.01,-0.79,y-0.13,y+0.13,8.70,8.725,0.004)
    fl="1.0" if mk=="CEIL" else "(1-0.75*max(0,sin(frame*1.9)*sin(frame*0.37)-0.55)*2.2)"
    pt_light(f"R2 cr ceiling {k}",(-1.40,y,8.66),(1.0,0.63,0.34),115 if k==1 else 100,f"{115 if k==1 else 100}*{fl}",'AREA',(0,0,0),None,(1.25,0.24))
for x in (-3.3,0.3):
    A.bx((g,"ACW"),x-0.22,x+0.22,-9.25,-8.95,8.75,8.80,0.004)
    for i in range(6): A.bx((g,"INK"),x-0.19,x+0.19,-9.23+i*0.05,-9.215+i*0.05,8.745,8.75,0.0)
A.prism((g,"ACW"),(0.9,-8.3,8.795),(0.9,-8.3,8.76),0.06,0.06,12,0); A.fb(("smoke","LED_R2"),'-x',0.9,-8.31,-8.29,8.755,8.765,0.0,0.0) if False else None
A.bx(("smoke","LED_R2"),0.89,0.91,-8.31,-8.29,8.755,8.762,0.0)
# analogue wall clock (back wall east part)
g="clock"; CLX,CLZ=0.75,8.15
A.prism((g,"IRON"),(CLX,-11.84,CLZ),(CLX,-11.80,CLZ),0.19,0.19,24,0); A.prism((g,"PAPER"),(CLX,-11.80,CLZ),(CLX,-11.795,CLZ),0.165,0.165,24,0)
for k in range(12): a=k*math.pi/6; A.bx((g,"P_INK"),CLX-0.006+0.14*math.sin(a),CLX+0.006+0.14*math.sin(a),-11.795,-11.79,CLZ-0.006+0.14*math.cos(a),CLZ+0.006+0.14*math.cos(a),0.0)
A.hull((g,"P_INK"),[(CLX-0.006,-11.792,CLZ),(CLX+0.006,-11.792,CLZ),(CLX-0.006,-11.788,CLZ),(CLX+0.006,-11.788,CLZ),(CLX-0.05,-11.792,CLZ+0.12),(CLX-0.04,-11.792,CLZ+0.12),(CLX-0.05,-11.788,CLZ+0.12),(CLX-0.04,-11.788,CLZ+0.12)],0.0)
A.hull((g,"P_RED"),[(CLX-0.004,-11.788,CLZ),(CLX+0.004,-11.788,CLZ),(CLX-0.004,-11.786,CLZ),(CLX+0.004,-11.786,CLZ),(CLX+0.09,-11.788,CLZ-0.05),(CLX+0.097,-11.788,CLZ-0.05),(CLX+0.09,-11.786,CLZ-0.05),(CLX+0.097,-11.786,CLZ-0.05)],0.0)
# ================= 10. east wall filing cabinet + boombox, wastebasket, dead plant =================
g="floor"
A.fb((g,"RACK"),'-x',2.0,-9.70,-9.10,5.4,6.85,0.50,0.01)
for k in range(2):
    z0=5.45+k*0.70; A.fb((g,"PLASTICD"),'-x',1.50,-9.68,-9.12,z0,z0+0.66,0.02,0.004); A.fb((g,"TRIM"),'-x',1.48,-9.48,-9.32,z0+0.44,z0+0.48,0.02,0.004); A.fb((g,"PAPER"),'-x',1.48,-9.55,-9.45,z0+0.52,z0+0.60,0.002,0.0)
A.bx((g,"PLASTICD"),1.62,1.95,-9.62,-9.19,6.85,6.98,0.012)                                                 # boombox
A.fb((g,"INK"),'-x',1.62,-9.60,-9.40,6.88,6.96,0.004,0.0); A.fb((g,"INK"),'-x',1.62,-9.36,-9.22,6.88,6.96,0.004,0.0)
for yy in (-9.55,-9.28): A.prism((g,"RACK"),(1.62,yy,6.925),(1.612,yy,6.925),0.04,0.04,14,0)
A.fb((g,"RACK"),'-x',1.62,-9.50,-9.30,6.955,6.975,0.004,0.0); A.prism((g,"RACK"),(1.70,-9.52,6.98),(1.70,-9.30,6.98+0.02),0.006,0.006,6)
for k in range(5): A.fb((g,"P_RED" if k==0 else "KEY"),'-x',1.62,-9.585+k*0.02,-9.575+k*0.02,6.985,6.994,0.004,0.0) if False else None
A.prism((g,"IRON"),(1.0,-8.6,5.4),(1.0,-8.6,5.66),0.12,0.15,10,0)                                            # wastebasket
for k in range(5): A.prism((g,"PAPER"),(1.0+R.uniform(-0.07,0.07),-8.6+R.uniform(-0.07,0.07),5.62+R.uniform(0,0.05)),(1.0+R.uniform(-0.07,0.07),-8.6+R.uniform(-0.07,0.07),5.68+R.uniform(0,0.05)),0.035,0.035,6,0)
A.prism((g,"CONE"),(1.65,-6.30,5.4),(1.65,-6.30,5.56),0.10,0.12,10,0)                                        # dead plant pot
for k in range(7):
    a=k*0.9; A.prism((g,"P_RED" if k%3==0 else "TRIM"),(1.65,-6.30,5.56),(1.65+0.14*math.cos(a),-6.30+0.14*math.sin(a),5.95+0.10*(k%3)),0.008,0.004,5)
    A.hull((g,"CORK"),[(1.65+0.14*math.cos(a)+dx,-6.30+0.14*math.sin(a)+dy,5.95+0.10*(k%3)+dz) for dx,dy,dz in ((0.03,0,0),(-0.03,0,0),(0,0.03,-0.05),(0,-0.03,-0.05),(0,0,0.02))],0.003)

# ================= 11. more small stuff =================
g="trink"
A.fb((g,"P_GOLD"),'-y',-7.2385,-3.20,-3.15,6.60,6.65,0.004,0.0); A.fb((g,"P_RED"),'-y',-7.2385,-1.65,-1.60,6.62,6.67,0.004,0.0); A.fb((g,"P_GOLD"),'-y',-7.2385,-0.30,-0.25,6.58,6.63,0.004,0.0)   # sticky notes on the bezels
for k in range(2):                                                                                       # in / out trays
    zz=DESK_Z+0.005+k*0.045
    A.bx((g,"PLASTICD"),0.05,0.30,-6.78,-6.52,zz,zz+0.006,0.001)
    for xa,xb,ya,yb in ((0.05,0.056,-6.78,-6.52),(0.294,0.30,-6.78,-6.52),(0.05,0.30,-6.78,-6.774),(0.05,0.30,-6.526,-6.52)): A.bx((g,"PLASTICD"),xa,xb,ya,yb,zz,zz+0.03,0.001)
    for j in range(3+k): A.bx((g,"PAPER"),0.07,0.27,-6.75,-6.55,zz+0.006+j*0.004,zz+0.009+j*0.004,0.0)
A.prism((g,"P_NAVY"),(-1.55,-6.58,DESK_Z),(-1.55,-6.58,DESK_Z+0.20),0.038,0.038,10,0); A.prism((g,"RACK"),(-1.55,-6.58,DESK_Z+0.20),(-1.55,-6.58,DESK_Z+0.235),0.03,0.03,10,0)   # thermos
A.bx((g,"P_INK"),-1.12,-0.98,-6.60,-6.56,DESK_Z,DESK_Z+0.045,0.004)                                     # stapler
A.hull((g,"PLASTICD"),[(-0.55,-6.62,DESK_Z),(-0.42,-6.62,DESK_Z),(-0.55,-6.52,DESK_Z),(-0.42,-6.52,DESK_Z),(-0.53,-6.60,DESK_Z+0.05),(-0.44,-6.60,DESK_Z+0.05),(-0.53,-6.54,DESK_Z+0.03),(-0.44,-6.54,DESK_Z+0.03)],0.006)   # tape dispenser
A.box((g,"IRON"),-3.85,-6.50,DESK_Z,DESK_Z+0.16,0.13,0.012,0.35,0.002); A.box((g,"PAPER"),-3.855,-6.50,DESK_Z+0.02,DESK_Z+0.14,0.10,0.004,0.35,0.0)   # framed photo
A.box((g,"P_RED"),-3.6,-6.55,DESK_Z,DESK_Z+0.03,0.16,0.10,-0.3,0.003)                                   # ID card holder
# ================= build =================
objs=A.build("31 R2 CONTROL 1990","R2 cr90",M)
for o in objs:
    for p in o.data.polygons: p.use_smooth=False
# emission-strength driven materials need no shadow catching; TV screen must not cast a hard shadow
scr.visible_shadow=False
for o in bpy.data.objects:
    if o.name.startswith("R2 cr SHIFT 04"): o.rotation_euler=(math.pi/2,0,-math.pi/2); o.location.z=7.58
print("CO1 objects",len(objs),"tris",sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objs))
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=DST)
