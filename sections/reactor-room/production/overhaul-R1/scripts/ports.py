import bpy
bpy.ops.wm.open_mainfile(filepath="w39.blend")
for o in sorted(bpy.data.objects,key=lambda o:o.name):
    if o.name.startswith("PORT_"): print("P",o.name,tuple(round(x,2) for x in o.matrix_world.translation),o.get("medium"),o.get("dn"))
