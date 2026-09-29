import bpy,sys,math,collections
from mathutils import Vector
S=sys.argv[sys.argv.index("--")+1]; src=sys.argv[sys.argv.index("--")+2]; dst=sys.argv[sys.argv.index("--")+3]
bpy.ops.wm.open_mainfile(filepath=S+"/"+src); sc=bpy.context.scene
coll=bpy.data.collections["30 R2 DOOR STUBS"]
r2=1/math.sqrt(2); dl=[];keep=[]
for o in list(coll.objects):
    if o.type not in("MESH","CURVE","FONT"): continue
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]
    beyond=(min(p.x for p in bb)<-11.1) or (max(p.y for p in bb)>11.1) or (max((p.x-p.y)*r2 for p in bb)>12.2)
    (keep if beyond else dl).append(o)
print("keep",len(keep),"drop",len(dl))
print("dropped groups:",collections.Counter(o.name.split(".")[0] for o in dl))
for o in dl: bpy.data.objects.remove(o,do_unlink=True)
for m in [m for m in bpy.data.materials if m.users==0 and (m.name.startswith("hall_") or m.name.startswith("lamp"))]: bpy.data.materials.remove(m)
un=collections.Counter(s.material.name for o in keep if o.name in bpy.data.objects for s in o.material_slots if s.material and not s.material.name.startswith("R2"))
print("unmapped left",dict(un))
bpy.ops.wm.save_as_mainfile(filepath=S+"/"+dst); print("ok")
