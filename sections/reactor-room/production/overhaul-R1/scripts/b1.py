import bpy,sys; sys.path.insert(0,"."); from lib import *
S=sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=S+"/work.blend")
X0=-1.4; T=Matrix.Translation((X0,5.0,-4.6))@Matrix.Rotation(-math.pi/2,4,'Z')
# 1. classify
room=[];delete=[]
for o in list(bpy.data.objects):
    if o.type not in('MESH','EMPTY','LIGHT','CURVE','FONT'): continue
    b=bbw(o) if o.type in('MESH','FONT','CURVE') else tuple((o.matrix_world.translation[i],)*2 for i in range(3))
    cx=(b[0][0]+b[0][1])/2; cy=(b[1][0]+b[1][1])/2; cz=(b[2][0]+b[2][1])/2
    cn=[c.name for c in o.users_collection]
    if any(c.startswith("08 COMPACT EAST STAIR") for c in cn): delete.append(o); continue
    if o.name.startswith(("Control route","AW Vestibule","D02 recessed")): delete.append(o); continue
    if 10.85<cx<15.1 and -3.5<cy<3.5 and 9.7<cz<13.7:
        if o.name.startswith(("Window","W01")): delete.append(o)
        else: room.append(o)
print("room",len(room),"delete",len(delete))
for o in room:
    if o.parent and o.parent in room: continue
    o.matrix_world=T@o.matrix_world
for o in delete: bpy.data.objects.remove(o,do_unlink=True)
# empty stair collection remains; keep
bpy.ops.wm.save_as_mainfile(filepath=S+"/w1.blend")
