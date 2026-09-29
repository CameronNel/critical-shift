import bpy,sys
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w24.blend")
n=0
for o in bpy.data.objects:
    if o.type=='MESH' and (o.name.startswith(("R2 lights ","R2 lamps ")) or (o.name.startswith("LP beacon") and "lens" in o.name)):
        o.visible_shadow=False; n+=1
print("fixture objects no longer casting shadow:",n)
bpy.ops.wm.save_as_mainfile(filepath=S+"/w25.blend"); print("ok")
