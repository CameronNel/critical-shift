import bpy,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cam import shoot
A=sys.argv[sys.argv.index("--")+1:]; src=A[0]; out=A[1]; names=A[2:]
bpy.ops.wm.open_mainfile(filepath=src)
V={"1_door":((-4.6,-6.8,6.9),(0.5,-9.8,6.5),20,0,False),"2_desk":((-3.2,-9.6,7.0),(-1.0,-6.9,6.2),22,0,True),"3_tv":((-2.9,-8.7,6.9),(-1.5,-11.9,7.2),22,1,False),"4_rack":((-0.6,-8.8,6.6),(1.8,-10.4,6.6),26,1,False),
   "5_wide":((-4.6,-11.6,8.15),(0.6,-7.0,6.2),19,1,True),"6_hall":((-1.0,-1.6,7.6),(-1.0,-7.0,6.5),22,1,True),
   "tv_telemetry":((-1.5,-9.2,6.9),(-1.5,-11.9,7.35),34,1,False),"tv_broadcast":((-1.5,-9.2,6.9),(-1.5,-11.9,7.35),34,250,False),"tv_static":((-1.5,-9.2,6.9),(-1.5,-11.9,7.35),34,163,False),"tv_s1":((-1.5,-9.2,6.9),(-1.5,-11.9,7.35),34,5,False),"tv_s2":((-1.5,-9.2,6.9),(-1.5,-11.9,7.35),34,200,False),"tv_s3":((-1.5,-9.2,6.9),(-1.5,-11.9,7.35),34,400,False),"tv_nosignal":((-1.5,-9.2,6.9),(-1.5,-11.9,7.35),34,380,False)}
keep=("31 CR","26 R2","20 CONTROL","25 LIGHTING","22 R2 ARCH","24 REACTOR STATE")
for n in names:
    l,t,ln,fr,full=V[n]
    for col in bpy.data.collections: col.hide_render=False
    if not full:
        for col in bpy.data.collections:
            if not col.name.startswith(keep): col.hide_render=True
    bpy.context.scene.frame_set(fr)
    shoot("cam_"+n,l,t,os.path.join(out,f"control_room_{n}.png"),ln,(int(os.environ.get('CR_W',1280)),int(os.environ.get('CR_H',720))),int(os.environ.get('CR_S',40)))
