import bpy,sys,re,collections; sys.path.insert(0,"."); import lib
from lib import *
lib.SEGCAP=8
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w8.blend")
ENAM=mat("hall_teal"); INK=mat("hall_steel"); MUST=mat("hall_yellow"); IVORY=mat("hall_pipe"); RUB=mat("hall_rubber"); CHR=mat("GT_Chrome"); LAMP=mat("lamp"); PLATE=mat("hall_ink")
K="22 ASSET KIT 1"
def remove(prefixes,xr,yr,zr=(-1,9)):
    n=0
    for o in list(bpy.data.objects):
        if o.type!='MESH' or not o.name.startswith(prefixes): continue
        b=bbw(o)
        if b[0][0]>=xr[0]-.05 and b[0][1]<=xr[1]+.05 and b[1][0]>=yr[0]-.05 and b[1][1]<=yr[1]+.05 and b[2][0]>=zr[0]:
            bpy.data.objects.remove(o,do_unlink=True); n+=1
    return n
# ---------- accumulator tank (emergency cooling) ----------
def accumulator(tag,cx,cy,facing=(0,1)):
    r=0.5; z0,z1=0.5,2.2
    cyl(f"AK1 {tag} shell",cx,cy,z0,z1,r,ENAM,K,24)
    dome(f"AK1 {tag} dome top",cx,cy,z1,r,0.28,True,ENAM); dome(f"AK1 {tag} dome bottom",cx,cy,z0,r,0.22,False,ENAM)
    for i,z in enumerate((0.95,1.75)): cyl(f"AK1 {tag} band {i}",cx,cy,z,z+0.06,r+0.02,MUST,K,24)
    for i in range(3):
        a=math.radians(90+120*i); lx,ly=cx+math.cos(a)*(r-0.05),cy+math.sin(a)*(r-0.05)
        box(f"AK1 {tag} leg {i}",lx-.05,lx+.05,ly-.05,ly+.05,0.05,0.75,INK,K); box(f"AK1 {tag} foot {i}",lx-.12,lx+.12,ly-.12,ly+.12,0.0,0.05,INK,K)
    cyl(f"AK1 {tag} top nozzle",cx,cy,2.48,2.7,0.07,IVORY,K,12); cyl(f"AK1 {tag} top flange",cx,cy,2.66,2.7,0.11,INK,K,12)
    # side nozzle toward the wall (-y)
    cyl_between(f"AK1 {tag} wall nozzle",(cx,cy-0.5,1.05),(cx,cy-0.85,1.05),0.07,IVORY,K,12)
    cyl_between(f"AK1 {tag} wall flange",(cx,cy-0.83,1.05),(cx,cy-0.87,1.05),0.11,INK,K,12)
    # gauge + plate facing +y
    cyl_between(f"AK1 {tag} gauge",(cx+0.2,cy+r-0.01,1.45),(cx+0.2,cy+r+0.06,1.45),0.09,CHR,K,16)
    box(f"AK1 {tag} plate",cx-0.2,cx+0.12,cy+r-0.02,cy+r+0.02,1.2,1.32,PLATE,K)
    label(f"AK1 {tag} label",tag,(cx-0.04,cy+r+0.03,1.26),0.09,m="white")
    box(f"AK1 {tag} lug L",cx-r-0.06,cx-r+0.02,cy-.04,cy+.04,2.0,2.1,INK,K); box(f"AK1 {tag} lug R",cx+r-0.02,cx+r+0.06,cy-.04,cy+.04,2.0,2.1,INK,K)
    port(f"PORT_{tag}_top",(cx,cy,2.7),"coolant",50,(0,0,1)); port(f"PORT_{tag}_wall",(cx,cy-0.87,1.05),"coolant",65,(0,-1,0))
print("removed EC",remove(("EC-1",),(2.6,4.0),(-10.3,-9.0)),remove(("EC-2",),(1.1,2.5),(-10.3,-9.0)))
accumulator("EC-1",3.3,-9.65); accumulator("EC-2",1.8,-9.65)
# ---------- coolant pump ----------
def pump(tag,cx,cy):
    box(f"AK1 {tag} base",cx-0.7,cx+0.7,cy-0.4,cy+0.4,0.1,0.2,INK,K)
    box(f"AK1 {tag} skid feet L",cx-0.7,cx-0.5,cy-0.4,cy+0.4,0.0,0.1,INK,K); box(f"AK1 {tag} skid feet R",cx+0.5,cx+0.7,cy-0.4,cy+0.4,0.0,0.1,INK,K)
    cyl_between(f"AK1 {tag} motor",(cx-0.65,cy,0.55),(cx+0.05,cy,0.55),0.3,ENAM,K,20)
    for i in range(5): xx=cx-0.55+i*0.12; cyl_between(f"AK1 {tag} fin {i}",(xx,cy,0.55),(xx+0.04,cy,0.55),0.325,ENAM,K,20)
    box(f"AK1 {tag} motor foot",cx-0.55,cx-0.05,cy-0.22,cy+0.22,0.2,0.26,INK,K)
    box(f"AK1 {tag} terminal box",cx-0.5,cx-0.25,cy-0.1,cy+0.1,0.83,1.0,MUST,K)
    box(f"AK1 {tag} coupling guard",cx+0.05,cx+0.28,cy-0.16,cy+0.16,0.35,0.75,INK,K)
    cyl_between(f"AK1 {tag} volute",(cx+0.28,cy,0.55),(cx+0.62,cy,0.55),0.34,ENAM,K,20)
    cyl_between(f"AK1 {tag} suction",(cx+0.6,cy,0.55),(cx+0.85,cy,0.55),0.1,IVORY,K,12); cyl_between(f"AK1 {tag} suction flange",(cx+0.83,cy,0.55),(cx+0.87,cy,0.55),0.15,INK,K,12)
    cyl(f"AK1 {tag} discharge",cx+0.45,cy,0.85,1.2,0.08,IVORY,K,12); cyl(f"AK1 {tag} discharge flange",cx+0.45,cy,1.17,1.21,0.13,INK,K,12)
    cyl_between(f"AK1 {tag} gauge",(cx+0.45,cy+0.34,0.68),(cx+0.45,cy+0.42,0.68),0.07,CHR,K,16)
    port(f"PORT_{tag}_suction",(cx+0.87,cy,0.55),"coolant",100,(1,0,0)); port(f"PORT_{tag}_discharge",(cx+0.45,cy,1.21),"coolant",80,(0,0,1))
print("removed pump",remove(("Duty coolant pump","Pump mounting rail"),(-4.0,-2.4),(-10.0,-9.0)))
pump("P-10",-3.2,-9.5)
# ---------- waste cask ----------
def cask(tag,cx,cy):
    cyl(f"AK1 {tag} plinth",cx,cy,0.0,0.12,1.05,INK,K,32)
    cyl(f"AK1 {tag} body",cx,cy,0.12,2.3,0.72,ENAM,K,28); dome(f"AK1 {tag} lid",cx,cy,2.3,0.72,0.28,True,ENAM,K,28)
    for i,z in enumerate((0.7,1.5)): cyl(f"AK1 {tag} band {i}",cx,cy,z,z+0.09,0.745,MUST,K,28)
    cyl(f"AK1 {tag} lid ring",cx,cy,2.28,2.33,0.76,INK,K,28); cyl(f"AK1 {tag} handle post",cx,cy,2.5,2.62,0.05,INK,K,10)
    box(f"AK1 {tag} handle",cx-0.28,cx+0.28,cy-0.04,cy+0.04,2.6,2.68,INK,K)
    box(f"AK1 {tag} transfer hatch",cx-0.3,cx+0.3,cy-0.78,cy-0.68,0.9,1.4,INK,K); box(f"AK1 {tag} hatch window",cx-0.2,cx+0.2,cy-0.79,cy-0.76,1.05,1.25,mat("observation_glass"),K)
    for i in range(3):
        a=math.radians(30+120*i); cyl_between(f"AK1 {tag} trunnion {i}",(cx+math.cos(a)*0.72,cy+math.sin(a)*0.72,0.45),(cx+math.cos(a)*0.9,cy+math.sin(a)*0.9,0.45),0.06,INK,K,10)
    port(f"PORT_{tag}_vent",(cx,cy,2.62),"vent",50,(0,0,1))
# keep original centre: bbox centre of 04 WASTE
print("removed waste",remove(("04 WASTE",),(6.4,8.8),(7.0,9.4)))
cask("W-04",7.6,8.2)
bpy.ops.wm.save_as_mainfile(filepath=S+"/w9.blend"); print("ok")
