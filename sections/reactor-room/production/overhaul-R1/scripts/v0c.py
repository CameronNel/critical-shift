import bpy,re
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath="w37.blend")
R={"grid":(9.0,10.9,-2.5,1.5),"turb":(8.4,10.9,-5.6,-2.1),"gen":(-10.9,-8.1,-4.7,-2.7),"resA":(-10.9,-8.7,2.9,4.3),"resB":(-10.9,-8.7,-5.8,-4.6),
"fuel":(-5.6,-2.6,8.7,10.9),"cart":(-10.0,-7.9,6.4,8.4),"bank":(2.5,4.8,9.5,10.9),"spares":(4.5,5.6,9.5,10.9),"vent":(8.6,10.4,5.8,7.8),
"waste":(6.3,8.3,7.4,9.6),"ec":(1.0,4.2,-10.6,-8.0),"pump":(-4.7,-2.3,-10.3,-7.9),"samp":(1.0,2.3,-4.3,-3.1),"bench":(-10.8,-9.6,3.8,5.4),"coolwall":(-5.6,5.4,-10.7,-9.95)}
def inside(bb):
    x0=min(p.x for p in bb);x1=max(p.x for p in bb);y0=min(p.y for p in bb);y1=max(p.y for p in bb);z1=max(p.z for p in bb)
    if z1>3.75: return False
    return any(a-0.05<=x0 and x1<=b+0.05 and c-0.05<=y0 and y1<=d+0.05 for a,b,c,d in R.values())
cols=[c for c in bpy.data.collections if c.name.startswith(("05 PER","MF W","W"))]
merged=[o for c in cols for o in c.objects if o.type=="MESH" and o.name.startswith("MERGED")]
print("merged objs",len(merged))
tot=0;dl=0
for o in merged:
    bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active=o; o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.separate(type='LOOSE'); bpy.ops.object.mode_set(mode='OBJECT')
parts=[o for c in cols for o in c.objects if o.type=="MESH" and o.name.startswith("MERGED")]
print("parts",len(parts))
for o in parts:
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]
    if inside(bb): bpy.data.objects.remove(o,do_unlink=True); dl+=1
for me in [m for m in bpy.data.meshes if m.users==0]: bpy.data.meshes.remove(me)
print("deleted parts",dl)
bpy.ops.wm.save_as_mainfile(filepath="w38.blend")
