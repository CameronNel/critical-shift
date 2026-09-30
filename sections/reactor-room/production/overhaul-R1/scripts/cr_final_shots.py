import bpy,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cam import shoot
A=sys.argv[sys.argv.index("--")+1:]; src=A[0]; out=A[1]; names=A[2:]
bpy.ops.wm.open_mainfile(filepath=src)
V={"1_door":((-4.6,-6.8,6.9),(0.5,-9.8,6.5),20,0,False),"2_desk":((-3.2,-9.6,7.0),(-1.0,-6.9,6.2),22,0,True),"3_tv":((-2.9,-8.7,6.9),(-1.5,-11.9,7.2),22,1,False),"4_rack":((-0.6,-8.8,6.6),(1.8,-10.4,6.6),26,1,False),
   "5_wide":((-4.6,-11.6,8.15),(0.6,-7.0,6.2),19,1,True),"6_hall":((-1.0,-1.6,7.6),(-1.0,-7.0,6.5),22,1,True),
   "tv_telemetry":((-1.5,-9.2,6.9),(-1.5,-11.9,7.35),34,1,False),"tv_broadcast":((-1.5,-9.2,6.9),(-1.5,-11.9,7.35),34,250,False),"tv_static":((-1.5,-9.2,6.9),(-1.5,-11.9,7.35),34,163,False),"stain":((-2.2,-9.2,7.3),(-2.48,-11.9,7.8),30,1,False),"ceil":((-0.6,-8.3,7.0),(-1.0,-9.3,8.5),30,1,False),"kb":((-2.75,-7.62,6.78),(-2.75,-7.42,6.19),42,1,False),"chair":((-1.6,-9.3,6.9),(-1.05,-7.4,6.0),26,1,False),"pend":((-2.6,-8.4,6.6),(-2.6,-9.9,7.6),30,1,False),"doorin":((-2.4,-8.0,6.9),(-4.3,-6.45,6.6),26,1,False),"floor":((-2.0,-8.6,7.6),(0.6,-9.6,5.4),26,1,False),"beacon":((-2.0,-8.6,7.3),(-4.5,-6.8,8.0),22,1,False),"poster":((1.2,-8.6,7.2),(2.0,-9.85,7.3),30,1,False),"deskp":((-2.2,-8.3,7.0),(-2.4,-6.95,6.3),34,1,False),"deskp3":((0.5,-8.3,7.0),(0.5,-6.95,6.3),34,1,False),"poster":((1.0,-9.0,7.3),(2.0,-9.85,7.3),36,1,False),"glass":((-0.6,-3.2,7.1),(-0.6,-6.0,7.0),30,1,True),"floorm":((-3.4,-8.9,7.0),(-4.0,-6.9,5.4),30,1,False),"stencil":((-1.5,-8.6,7.4),(-1.5,-11.9,8.0),30,1,False),"rackv":((-0.4,-9.6,6.5),(1.4,-10.35,6.6),30,1,False),"haze":((-4.6,-11.6,7.6),(1.0,-8.0,6.4),22,1,False),"tv_s1":((-1.5,-9.2,6.9),(-1.5,-11.9,7.35),34,5,False),"tv_s2":((-1.5,-9.2,6.9),(-1.5,-11.9,7.35),34,200,False),"tv_s3":((-1.5,-9.2,6.9),(-1.5,-11.9,7.35),34,400,False),"tv_nosignal":((-1.5,-9.2,6.9),(-1.5,-11.9,7.35),34,380,False)}
keep=("31 CR","26 R2","20 CONTROL","25 LIGHTING","22 R2 ARCH","24 REACTOR STATE")
for n in names:
    l,t,ln,fr,full=V[n]
    for col in bpy.data.collections: col.hide_render=False
    if not full:
        for col in bpy.data.collections:
            if not col.name.startswith(keep): col.hide_render=True
    if os.environ.get('CR_STAB'): bpy.data.objects['REACTOR_STATE']['stability']=float(os.environ['CR_STAB'])
    if os.environ.get('CR_FRAME'): fr=int(os.environ['CR_FRAME'])
    bpy.context.scene.frame_set(fr)
    shoot("cam_"+n,l,t,os.path.join(out,f"control_room_{n}.png"),ln,(int(os.environ.get('CR_W',1280)),int(os.environ.get('CR_H',720))),int(os.environ.get('CR_S',40)))
