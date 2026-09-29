import bpy,sys; sys.path.insert(0,".")
from cam import shoot
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w45.blend"); sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.use_denoising=True
bpy.data.objects["REACTOR_STATE"]["stability"]=0.85; sc.frame_set(150)
shoot("crane",(8.5,-6.5,9.0),(-1.0,4.6,14.0),S+"/v45_crane.png",lens=18,res=(1280,720),samples=22)
