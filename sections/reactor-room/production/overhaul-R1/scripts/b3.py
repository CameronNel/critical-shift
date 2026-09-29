import bpy,sys,math; sys.path.insert(0,"."); import palette
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w2.blend"); sc=bpy.context.scene
palette.apply()
# pool lights + medium -> cyan
for o in bpy.data.objects:
    if o.type=='LIGHT' and tuple(round(x,2) for x in o.data.color)==(1.0,0.52,0.17): o.data.color=(0.12,0.72,1.0)
pm=bpy.data.materials["pool_medium"]
for n in pm.node_tree.nodes:
    if n.type=='VOLUME_ABSORPTION': n.inputs['Color'].default_value=(0.18,0.85,1.0,1)
    if n.type=='VOLUME_SCATTER': n.inputs['Color'].default_value=(0.08,0.65,1.0,1)
# operating animation: banks move out of phase, pool glow follows rod position
for n,phase in (("BANK_A_MOVING",0),("BANK_B_MOVING",1)):
    o=bpy.data.objects[n]; o.animation_data_clear()
    vals=[(1,8.4),(120,7.2),(240,8.2),(360,7.0),(480,8.4)] if phase==0 else [(1,7.4),(120,8.5),(240,7.0),(360,8.3),(480,7.4)]
    for f,z in vals: o.location.z=z; o.keyframe_insert("location",index=2,frame=f)
pg=bpy.data.materials["pool_glow"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for f,v in ((1,2.0),(60,2.6),(120,1.7),(180,2.8),(240,1.9),(300,2.6),(360,1.7),(420,2.7),(480,2.0)):
    pg.default_value=v; pg.keyframe_insert("default_value",frame=f)
sc.frame_set(1); sc.frame_end=480
bpy.ops.wm.save_as_mainfile(filepath=S+"/w3.blend"); print("ok")
