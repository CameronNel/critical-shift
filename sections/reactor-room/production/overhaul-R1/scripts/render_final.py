import bpy,sys; sys.path.insert(0,"."); from cam import shoot
S=sys.argv[sys.argv.index("--")+1]; out=sys.argv[sys.argv.index("--")+2]
bpy.ops.wm.open_mainfile(filepath=S+"/w5.blend"); sc=bpy.context.scene
sc.frame_set(180)
R=(1280,720)
sc.camera=bpy.data.objects["01_HERO"]; sc.render.engine='CYCLES'; sc.cycles.samples=24; sc.cycles.use_denoising=True
sc.render.resolution_x,sc.render.resolution_y=R; sc.render.resolution_percentage=100
sc.render.filepath=out+"/01_hero.png"; bpy.ops.render.render(write_still=True); print("done hero",flush=True)
shoot("v1",(-1.4,-8.4,7.1),(0,4.5,4.2),out+"/02_control_room_view.png",lens=18,res=R,samples=24)
shoot("v2",(0,10,2.0),(0,-4,4.5),out+"/03_mezzanine_from_south.png",lens=18,res=R,samples=24)
shoot("v3",(-3.0,0.5,1.7),(-6.8,-6.5,4.0),out+"/04_elevator_and_ground_landing.png",lens=20,res=R,samples=24)
shoot("v5",(-1.0,-3.0,7.5),(-6.5,-7.0,6.0),out+"/06_upper_landing_and_control_window.png",lens=20,res=R,samples=24)
shoot("v4",(-7,3,3.0),(10.5,0,6.5),out+"/05_east_wall_patched.png",lens=20,res=R,samples=24)
