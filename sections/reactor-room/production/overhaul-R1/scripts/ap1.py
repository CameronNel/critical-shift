import bpy,sys,math,os
from mathutils import Vector
# usage: blender/python ap1.py -- <scene dir> <src.blend> <dst.blend> [module.blend]
# module.blend defaults to the repo-relative sources/reactor-room/module.blend
A=sys.argv[sys.argv.index("--")+1:]
S,src,dst=A[0],A[1],A[2]
bpy.ops.wm.open_mainfile(filepath=S+"/"+src); sc=bpy.context.scene
REPO=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),*([".."]*5)))   # scripts -> overhaul-R1 -> production -> reactor-room -> sections -> repo
ORIG=A[3] if len(A)>3 else os.path.join(REPO,"sections","facility-assembly","sources","reactor-room","module.blend")
if not os.path.isfile(ORIG): sys.exit("module.blend not found: "+ORIG+" (pass it as the 4th argument)")
pre=("MAIN ACCESS.","FUEL HANDLING.","COOLING PLANT.")
with bpy.data.libraries.load(ORIG,link=False) as (a,b):
    names=[n for n in a.objects if n.startswith(pre)]
    b.objects=names
coll=bpy.data.collections.new("30 R2 DOOR STUBS"); sc.collection.children.link(coll)
got=[o for o in b.objects if o]
for o in got: coll.objects.link(o)
print("appended",len(got))
R2={"hall_teal_dark":"R2 iron","hall_teal":"R2 door steel","hall_teal_light":"R2 trim rust","hall_steel":"R2 iron","hall_steel_light":"R2 trim rust","hall_mineral":"R2 wall plum lower","hall_floor":"R2 floor tile"}
import collections
cnt=collections.Counter()
for o in got:
    for slot in o.material_slots:
        m=slot.material
        if m and m.name.split(".")[0] in R2 or (m and m.name in R2):
            slot.material=bpy.data.materials[R2[m.name.split(".")[0] if m.name.split(".")[0] in R2 else m.name]]; cnt[slot.material.name]+=1
        elif m: cnt["UNMAPPED:"+m.name]+=1
print("materials",dict(cnt))
# purge orphan hall_* materials that came in
for m in [m for m in bpy.data.materials if m.users==0 and m.name.startswith("hall_")]: bpy.data.materials.remove(m)
# remove the hall-plane door leaves so the stubs are walkable
rm=[o for o in bpy.data.objects if o.name.startswith(("R2 w1 doorleaf","R2 w4 doorleaf","R2 w6 doorleaf"))]
for o in rm: bpy.data.objects.remove(o,do_unlink=True)
print("removed hall-plane door leaves",len(rm))
# stub lighting (dim, cold-amber) so the airlock stubs are not black holes
def lamp(name,loc,e=180,col=(1.0,0.62,0.30)):
    ld=bpy.data.lights.new(name,'POINT'); ld.energy=e; ld.color=col; ld.shadow_soft_size=0.25
    lo=bpy.data.objects.new(name,ld); lo.location=loc; coll.objects.link(lo)
lamp("stub lamp W",(-12.6,0,4.9)); lamp("stub lamp N",(0,12.6,4.5)); lamp("stub lamp SE",(9.6,-9.6,4.4))
bpy.ops.wm.save_as_mainfile(filepath=S+"/"+dst); print("ok")
