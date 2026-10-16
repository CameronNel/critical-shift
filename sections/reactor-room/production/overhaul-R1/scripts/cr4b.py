import bpy,sys; sys.path.insert(0,".")
from cam import shoot
S=sys.argv[sys.argv.index("--")+1]; f=sys.argv[sys.argv.index("--")+2]; tag=sys.argv[sys.argv.index("--")+3]
bpy.ops.wm.open_mainfile(filepath=S+"/"+f); sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.use_denoising=True
bpy.data.objects["REACTOR_STATE"]["stability"]=0.85; sc.frame_set(1); bpy.context.view_layer.update()
V=[("back_wall_toward_window",(-1.4,-11.65,7.3),(-1.4,-6.0,6.7),15),
   ("window_toward_back_wall",(-1.4,-6.6,7.3),(-1.4,-11.9,6.6),15),
   ("back_east_corner_toward_door_side",(1.7,-11.5,7.3),(-4.2,-6.8,6.2),14),
   ("back_west_corner_toward_east_side",(-4.5,-11.5,7.3),(1.8,-6.8,6.2),14)]
for n,c,t,l in V: shoot(n,c,t,f"{S}/{tag}_{n}.png",lens=l,res=(960,540),samples=24)
