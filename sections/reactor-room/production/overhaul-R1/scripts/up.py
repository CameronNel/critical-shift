import bpy,sys; sys.path.insert(0,".")
from cam import shoot
S=sys.argv[sys.argv.index("--")+1]; f=sys.argv[sys.argv.index("--")+2]; tag=sys.argv[sys.argv.index("--")+3]
bpy.ops.wm.open_mainfile(filepath=S+"/"+f); sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.use_denoising=True
st=bpy.data.objects["REACTOR_STATE"]; st["stability"]=0.85; sc.frame_set(150)
shoot("up1",(-2,-7.5,2.0),(0.5,2,13.5),f"{S}/{tag}_up1.png",lens=16,res=(1280,720),samples=16)
shoot("up2",(7.5,7.5,3.0),(-3,-2,12.5),f"{S}/{tag}_up2.png",lens=16,res=(1280,720),samples=16)
from mathutils import Vector
import collections
for o in bpy.data.objects:
    if o.users_collection and o.users_collection[0].name.startswith("RF APPROVED"):
        bb=[o.matrix_world@Vector(v) for v in o.bound_box]; print("ROOF",o.name[:40],"z%.1f..%.1f"%(min(p.z for p in bb),max(p.z for p in bb)),"x%.1f..%.1f"%(min(p.x for p in bb),max(p.x for p in bb)))
