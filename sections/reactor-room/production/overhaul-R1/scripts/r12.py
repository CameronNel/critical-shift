import bpy,sys,time; sys.path.insert(0,"."); from cam import shoot
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w14.blend"); sc=bpy.context.scene; st=bpy.data.objects["REACTOR_STATE"]; sc.frame_set(180)
sc.render.engine='CYCLES'; sc.cycles.samples=20; sc.cycles.use_denoising=True; sc.cycles.volume_bounces=1
sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage=1280,720,100
def setstate(v): st["stability"]=v; bpy.context.view_layer.update()
for tag,v in (("a_stable",1.0),("b_warning",0.5),("c_critical",0.08)):
    setstate(v); sc.camera=bpy.data.objects["01_HERO"]; sc.render.filepath=f"{S}/spooky_{tag}.png"; bpy.ops.render.render(write_still=True); print("done",tag,flush=True)
setstate(0.5); shoot("cv",(-1.4,-8.4,7.1),(0,4.5,4.2),S+"/spooky_d_control_room_view.png",lens=18,res=(1280,720),samples=20)
setstate(0.5); shoot("ev",(2.4,-5.6,1.9),(2.4,-9.6,1.3),S+"/spooky_e_emergency_cooling.png",lens=22,res=(1280,720),samples=20)
