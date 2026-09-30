import bpy,sys; sys.path.insert(0,".")
from cam import shoot
S=sys.argv[sys.argv.index("--")+1]; f=sys.argv[sys.argv.index("--")+2]; tag=sys.argv[sys.argv.index("--")+3]
bpy.ops.wm.open_mainfile(filepath=S+"/"+f); sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.use_denoising=True
bpy.data.objects["REACTOR_STATE"]["stability"]=0.85; sc.frame_set(1); bpy.context.view_layer.update()
V=[("north_toward_window",(-1.4,-9.75,7.3),(-1.4,-4.0,6.7),15),
   ("south_toward_back_wall",(-1.4,-4.45,7.3),(-1.4,-9.9,6.6),15),
   ("east_toward_door",(1.75,-7.0,7.2),(-4.7,-7.0,6.5),15),
   ("west_toward_east_wall",(-4.5,-7.0,7.2),(2.0,-7.0,6.4),15)]
for n,c,t,l in V: shoot(n,c,t,f"{S}/{tag}_{n}.png",lens=l,res=(960,540),samples=24)
