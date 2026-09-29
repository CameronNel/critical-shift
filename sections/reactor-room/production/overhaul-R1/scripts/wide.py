import bpy,sys,os; sys.path.insert(0,".")
from cam import shoot
S=sys.argv[sys.argv.index("--")+1]; f=sys.argv[sys.argv.index("--")+2]; tag=sys.argv[sys.argv.index("--")+3]
bpy.ops.wm.open_mainfile(filepath=S+"/"+f); sc=bpy.context.scene; st=bpy.data.objects["REACTOR_STATE"]; st["stability"]=0.85; sc.frame_set(150); bpy.context.view_layer.update()
sc.render.engine='CYCLES'; sc.cycles.use_denoising=True
V={"w_east":((-8.5,-2.0,4.5),(9.5,-0.5,1.5),18),"w_west":((8.0,2.0,4.5),(-9.5,0.0,1.5),18),"w_north":((-2.0,-7.0,6.0),(1.0,9.5,2.0),16),"w_south":((3.0,8.0,6.5),(-1.0,-9.5,2.5),16),"stubW":((-6.0,0.0,1.7),(-14.4,0.0,2.2),20),"stubN":((0.0,6.0,1.7),(0.0,14.4,2.2),20),"stubSE":((6.0,-6.0,1.7),(11.0,-11.0,2.2),20),"crane":((-9.0,-8.0,8.0),(0.0,4.6,14.0),18),"w_high":((-9.0,-9.0,13.0),(1.0,1.0,3.0),18)}
sel=os.environ.get("VIEWS","").split(",")
for k,(c,t,l) in V.items():
    if sel!=[""] and k not in sel: continue
    shoot(k,c,t,f"{S}/{tag}_{k}.png",lens=l,res=(1280,720),samples=16)
sc.camera=bpy.data.objects["01_HERO"]; sc.render.resolution_x,sc.render.resolution_y=1280,720; sc.cycles.samples=20; sc.render.filepath=f"{S}/{tag}_hero.png"; bpy.ops.render.render(write_still=True)
