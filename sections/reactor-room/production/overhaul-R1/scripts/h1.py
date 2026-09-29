import bpy,sys; sys.path.insert(0,"."); import palette4
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w17.blend")
print("recoloured",palette4.apply())
bpy.ops.wm.save_as_mainfile(filepath=S+"/w18.blend"); print("ok")
