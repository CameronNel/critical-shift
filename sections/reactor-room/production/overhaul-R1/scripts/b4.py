import bpy,sys; sys.path.insert(0,"."); from lib import *
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w3.blend")
def aim(name,loc,tgt,lens=None):
    c=bpy.data.objects[name]; c.location=loc
    c.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
aim("01_HERO",(-7.5,8.6,8.8),(0.5,-4.5,5.0))
aim("09_BANK_MECHANISMS",(-6.2,-3.6,9.2),(0.0,0.0,8.2))
bpy.data.objects.remove(bpy.data.objects["Control room external identifier.legend"],do_unlink=True)
for c in list(bpy.data.collections):
    if c.name.startswith("08 COMPACT EAST STAIR") and not c.all_objects and not c.children:
        bpy.data.collections.remove(c)
bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=S+"/w4.blend"); print("ok")
