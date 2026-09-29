import bpy,sys,math
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w10.blend")
objs=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith(("AK1 ","EL ","MZ ")))]
for o in bpy.context.view_layer.objects: o.select_set(False)
n=0
for o in objs:
    if o.name not in bpy.context.view_layer.objects: continue
    o.select_set(True); bpy.context.view_layer.objects.active=o; n+=1
bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
print("smoothed",n)
bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=S+"/w11.blend"); print("ok")
