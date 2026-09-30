"""Control room redo: usage python cr_build.py -- <src cr2.blend> <dst.blend> [stage]   stage: shell|desk|all"""
import bpy,sys,math,random,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector
import crk,crt,cr_pal,cr_mats,cr_shell,cr_desk,cr_props1,cr_props2,cr_tv,cr_light
A_=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A_[0],A_[1]; STAGE=A_[2] if len(A_)>2 else "all"
bpy.ops.wm.open_mainfile(filepath=SRC); sc=bpy.context.scene
print("PAL",cr_pal.retune())
crk.STATE=bpy.data.objects["REACTOR_STATE"]
def ext(o):
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return (min(q.x for q in p),max(q.x for q in p),min(q.y for q in p),max(q.y for q in p),min(q.z for q in p),max(q.z for q in p))
# ---- idempotence: a previous run of this script is removed first
old=bpy.data.collections.get("31 CR CONTROL ROOM REDO")
if old:
    for o in list(old.objects): bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.collections.remove(old)
# ---- clean-out: everything inside the room except the structural shell
KEEP=("R2 control cr floor FLOOR","R2 control cr back wall BACK")
gone=0
for o in list(bpy.data.collections["26 R2 CONTROL ROOM"].objects):
    if o.name in KEEP: continue
    e=ext(o)
    if o.name.startswith("MERGED 26 R2 CONTRO R2 iron") and e[4]>=8.79: continue          # ceiling slab
    bpy.data.objects.remove(o,do_unlink=True); gone+=1
for o in list(bpy.data.objects):
    if o.type=="LIGHT" and o.name.startswith("LP control"): bpy.data.objects.remove(o,do_unlink=True)
print("removed",gone)
class Ctx: pass
c=Ctx(); c.R=random.Random(1990); c.A=crk.Kit(); c.M=cr_mats.make(c.R)
c.coll=bpy.data.collections.new("31 CR CONTROL ROOM REDO"); sc.collection.children.link(c.coll)
c.TROFFER_LIST=[(2,1,False),(6,1,False),(9,1,True)]
c.TROFFERS=[(i+d,j) for (i,j,f) in c.TROFFER_LIST for d in (0,1)]
c.MISSING=[(4,4),(5,4),(3,7),(4,7),(10,5)]
# floor / back wall finish
bpy.data.objects["R2 control cr floor FLOOR"].data.materials.clear(); bpy.data.objects["R2 control cr floor FLOOR"].data.materials.append(c.M["FLOOR"])
bpy.data.objects["R2 control cr back wall BACK"].data.materials.clear(); bpy.data.objects["R2 control cr back wall BACK"].data.materials.append(c.M["WALL_BAND"])
cr_shell.build(c)
import numpy as np
import cr_desk as D
if STAGE in("desk","all"):
    D.desk(c)
    scr=[("SCR1",["KESTREL OS 4.2","","> BANK A   8.4 M   OK","> BANK B   7.4 M   OK","> COOLANT  P-10  RUN","> GRID DEMAND    74 %","> STABILITY","> _"],(0.15,1.0,0.25)),
         ("SCR2",["LOAD SHEDDING PLAN","SECTOR 1 ....... ON","SECTOR 2 ....... ON","SECTOR 3 ....... ON","SECTOR 4 ...... OFF","","READY_"],(1.0,0.55,0.08)),
         ("SCR3",["SHIFT LOG  04","22:41  ROUTINE","23:10  ROUTINE","00:02  NOTHING","       UNUSUAL","> _"],(0.15,1.0,0.25))]
    for k,(nm,lines,col) in enumerate(scr):
        img=crk.new_image("CR crt tex "+nm,crt.crt_screen(lines,seed=k)*np.array(col,dtype=np.float32))
        c.M[nm]=D.crt_glass_mat("CR crt "+nm,img,2.2)
    for (cx,nm,tower) in ((-2.75,"SCR1",False),(-1.05,"SCR2",True),(0.65,"SCR3",False)):
        D.terminal(c,cx,nm,"KESTREL 14",case=not tower)
    for cx in (-2.75,-1.05,0.65): D.chair(c,cx,-7.37,0.0)
if STAGE=="all":
    P1,P2=cr_props1,cr_props2
    for f in (P1.rack,P1.copier,P1.printer,P1.shelving,P1.cot,P1.lockers,P1.break_corner,P1.worktable,P1.credenza): f(c)
    P2.desk_clutter(c); P2.wall_decor(c); P2.ceiling_bits(c)
    cr_tv.build(c)
    D.chair(c,-2.60,-9.12,math.pi)
    cr_light.build(c)
elif STAGE in("shell","desk"):
    crk.light(c.coll,"CR test key",(-1.2,-8.0,8.4),(1.0,0.66,0.34),900,'AREA',(0,0,0),size=(3.0,1.5))
mats=dict(c.M)
for k,v in list(mats.items()):
    if isinstance(v,list):
        for i,m in enumerate(v): mats[f"{k}{i}"]=m
mats.update({k:c.M[k] for k in ("SCR1","SCR2","SCR3","TVSCR") if k in c.M})
c.A.build(c.coll,"CR",mats)
crk.mesh_texts()
bpy.ops.wm.save_as_mainfile(filepath=DST)
