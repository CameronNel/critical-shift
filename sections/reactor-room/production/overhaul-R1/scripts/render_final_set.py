import bpy,sys; sys.path.insert(0,"."); from cam import shoot
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w32.blend"); sc=bpy.context.scene; st=bpy.data.objects["REACTOR_STATE"]
sc.render.engine='CYCLES'; sc.cycles.use_denoising=True; sc.cycles.volume_bounces=1; sc.render.resolution_percentage=100
def setstate(v,fr): st["stability"]=v; st.update_tag(); sc.frame_set(fr); bpy.context.view_layer.update()
for tag,v in (("a_stable",1.0),("b_warning",0.5),("c_critical",0.05)):
    setstate(v,150); sc.camera=bpy.data.objects["01_HERO"]; sc.cycles.samples=22; sc.render.resolution_x,sc.render.resolution_y=1280,720; sc.render.filepath=f"{S}/final_hero_{tag}.png"; bpy.ops.render.render(write_still=True); print("done",tag,flush=True)
setstate(0.6,150); shoot("eye",(-1.55,-6.9,7.1),(-0.2,3.0,3.6),S+"/final_eye_from_desk.png",lens=14,res=(1280,720),samples=22)
shoot("pool",(-4.2,-5.0,3.2),(0,0,-0.5),S+"/final_pool.png",lens=24,res=(1280,720),samples=22)
shoot("cr",(1.2,-7.0,7.4),(-2.0,-9.6,6.3),S+"/final_control_room_inside.png",lens=18,res=(1280,720),samples=22)
