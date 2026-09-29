import bpy,sys; sys.path.insert(0,".")
from cam import shoot
S=sys.argv[sys.argv.index("--")+1]; f=sys.argv[sys.argv.index("--")+2]; tag=sys.argv[sys.argv.index("--")+3]
bpy.ops.wm.open_mainfile(filepath=S+"/"+f); sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.use_denoising=True
import os
ALL={"grid":((6.5,-3.5,2.4),(10.2,-0.5,1.0)),"bank":((1.2,6.0,2.4),(3.6,10.2,0.9)),"gen":((-6.0,-2.0,2.3),(-9.6,-3.6,1.0)),"gen2":((-6.0,-2.0,2.6),(-9.8,3.6,1.0)),
"fuel":((-1.0,5.8,2.6),(-4.0,9.8,1.0)),"waste":((4.4,5.5,2.6),(7.6,8.3,1.3)),"ec":((-1.5,-5.2,2.6),(1.0,-9.5,1.2)),"turb":((5.8,-6.5,2.6),(9.8,-3.5,1.0)),
"samp":((-0.6,-0.8,2.2),(1.3,-3.7,0.9)),"vent":((6.0,3.5,2.6),(9.4,6.6,1.5)),"bench":((-6.5,1.5,2.4),(-10.2,4.6,1.0)),"cart":((-5.0,5.0,2.4),(-9.0,7.5,0.8)),"pump":((-1.0,-5.5,2.4),(-3.6,-9.4,0.9))}
sel=os.environ.get("VIEWS","").split(",")
V={k:v for k,v in ALL.items() if k in sel} if sel!=[""] else ALL
for k,(c,t) in V.items():
    shoot(k,c,t,f"{S}/{tag}_{k}.png",lens=22,res=(960,540),samples=14)
