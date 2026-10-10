import bpy,sys,time; sys.path.insert(0,"."); from cam import shoot
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w15.blend"); sc=bpy.context.scene; st=bpy.data.objects["REACTOR_STATE"]
sc.render.engine='CYCLES'; sc.cycles.use_denoising=True; sc.cycles.volume_bounces=1
def setstate(v,f): st["stability"]=v; st.update_tag(); sc.frame_set(f); bpy.context.view_layer.update()
def hero(tag,v,f,W,H,smp):
    setstate(v,f); sc.cycles.samples=smp; sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage=W,H,100
    sc.camera=bpy.data.objects["01_HERO"]; sc.render.filepath=f"{S}/lit_{tag}.png"; bpy.ops.render.render(write_still=True); print("done",tag,flush=True)
hero("a_stable",1.0,180,1280,720,20)
hero("b_critical_beacons",0.25,170,1280,720,20)
setstate(0.5,180); shoot("cv",(-1.4,-8.4,7.1),(0,4.5,4.2),S+"/lit_c_control_room_view.png",lens=18,res=(1280,720),samples=20)
for i,f in enumerate((100,103,106,109)): hero(f"flicker_{i}",0.4,f,640,360,10)
