import bpy,sys; sys.path.insert(0,".")
from cam import shoot
S=sys.argv[sys.argv.index("--")+1]; f=sys.argv[sys.argv.index("--")+2]; tag=sys.argv[sys.argv.index("--")+3]
bpy.ops.wm.open_mainfile(filepath=S+"/"+f); sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.use_denoising=True
bpy.data.objects["REACTOR_STATE"]["stability"]=0.85
V=[("a_window_to_back_telemetry",282,(-1.4,-6.6,7.3),(-1.4,-11.9,6.6),15),
   ("b_window_to_back_broadcast",120,(-1.4,-6.6,7.3),(-1.4,-11.9,6.6),15),
   ("e_rack_and_east_wall",282,(-2.6,-9.2,7.0),(1.9,-9.6,6.4),16)]
for n,fr,c,t,l in V:
    sc.frame_set(fr); bpy.context.view_layer.update()
    shoot(n,c,t,f"{S}/{tag}_{n}.png",lens=l,res=(1280,720),samples=24)
