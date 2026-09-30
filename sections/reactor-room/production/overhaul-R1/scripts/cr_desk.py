"""Operator desk row (three bays with real kneeholes), early-90s CRT terminals, keyboards, mice, PC cases, task chairs (tucked)."""
import math,bpy
import numpy as np
import crk,crt
from crk import text,tex_mat,_n,_new
FZ=5.40; ZT=6.17                                       # floor and desk-top surface
BAYS=[(-3.60,-1.90),(-1.90,-0.20),(-0.20,1.50)]
DY0,DY1=-7.60,-6.40
def crt_glass_mat(name,img,strength):
    m=_new(name); nt=m.node_tree
    out=_n(nt,"ShaderNodeOutputMaterial",900,0); b=_n(nt,"ShaderNodeBsdfPrincipled",600,0); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    b.inputs['Base Color'].default_value=(0.012,0.014,0.013,1); b.inputs['Roughness'].default_value=0.10; b.inputs['Coat Weight'].default_value=0.6; b.inputs['Coat Roughness'].default_value=0.05
    uv=_n(nt,"ShaderNodeTexCoord",-500,0); tx=_n(nt,"ShaderNodeTexImage",-200,0); tx.image=img; tx.extension='EXTEND'; nt.links.new(uv.outputs['UV'],tx.inputs[0])
    nt.links.new(tx.outputs['Color'],b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value=strength
    crk.drv(nt,'nodes["Principled BSDF"].inputs["Emission Strength"].default_value',None,f"{strength}*(0.93+0.07*sin(frame*1.7+{strength})*sin(frame*0.31))",var_s=False)
    return m
def desk(c):
    A,M=c.A,c.M; g="desk"
    for (x0,x1) in BAYS:
        A.bx((g,"WOOD"),x0+0.003,x1-0.003,DY0,DY1,ZT-0.035,ZT,0.003)                                  # laminate top
        A.bx((g,"EDGE"),x0+0.003,x1-0.003,DY0-0.003,DY0,ZT-0.035,ZT,0.0015)                            # edge banding front
        A.bx((g,"EDGE"),x0+0.003,x1-0.003,DY1,DY1+0.003,ZT-0.035,ZT,0.0015)
        A.bx((g,"STEEL"),x0+0.06,x1-0.06,-7.50,-7.48,ZT-0.075,ZT-0.035,0.002)                          # front apron
        A.bx((g,"STEEL"),x0+0.06,x1-0.06,-6.50,-6.48,ZT-0.075,ZT-0.035,0.002)
        A.bx((g,"STEEL"),x0+0.06,x1-0.06,-6.72,-6.66,ZT-0.075,ZT-0.035,0.003)                          # cable tray channel
        for k in range(3): A.cylx((g,"CABLE"),x0+0.15,x1-0.15,-6.71+k*0.02,ZT-0.06,0.006,6)
        xm=(x0+x1)/2
        A.cyl((g,"BLACK"),xm+0.5,-6.55,ZT,ZT+0.003,0.032,16)                                          # cable grommet
        A.bx((g,"LOCKER"),x0+0.05,x1-0.05,-6.62,-6.59,FZ+0.22,ZT-0.035,0.004)                          # modesty panel
        for k in range(3): A.bx((g,"BLACK"),xm-0.5+k*0.5,xm-0.5+k*0.5+0.22,-6.625,-6.62,ZT-0.13,ZT-0.115,0.001)
    for xp,side in ((-3.60,1),(-1.90,0),(-0.20,0),(1.50,-1)):                                            # end panels (double at shared joints)
        offs=(0.028,) if side else (-0.021,0.021)
        for o in offs:
            xc=xp+(side*o if side else o)
            A.bx((g,"LOCKER"),xc-0.0135,xc+0.0135,-7.52,-6.48,FZ+0.03,ZT-0.035,0.004)
            for zz in (FZ+0.35,ZT-0.12):
                for yy in (-7.42,-6.58): A.screw((g,"STEEL_L"),'+x' if o>=0 else '-x',xc+(0.0135 if o>=0 else -0.0135),yy,zz,0.006)
            for yy in (-7.48,-6.52): A.cyl((g,"BLACK"),xc,yy,FZ,FZ+0.03,0.022,12)                         # levelling glides
    return
def keyboard(c,cx,y0,rot_tag=""):
    A,M=c.A,c.M; g="kb"; z0=ZT
    A.hull((g,"BEIGE"),[(cx-0.24,y0,z0),(cx+0.24,y0,z0),(cx-0.24,y0+0.19,z0),(cx+0.24,y0+0.19,z0),
                        (cx-0.24,y0,z0+0.017),(cx+0.24,y0,z0+0.017),(cx-0.24,y0+0.19,z0+0.034),(cx+0.24,y0+0.19,z0+0.034)],0.004)
    A.bx((g,"BEIGE_D"),cx-0.225,cx+0.225,y0+0.015,y0+0.175,z0+0.017,z0+0.020,0.001)                         # key well
    p=0.0185; kx=cx-0.225+0.012
    def key(x,y,r,w=1.0,mk="KEY"):
        zb=z0+0.02+0.0045*r; A.bx((g,mk),x,x+p*w-0.002,y,y+p-0.002,zb,zb+0.011,0.0012)
    for r in range(6):
        y=y0+0.02+r*0.0255
        if r==0:
            key(kx+0.0,y,r,1.3,"KEY_D"); key(kx+0.0245,y,r,1.3,"KEY_D"); key(kx+0.0555,y,r,5.7); key(kx+0.176,y,r,1.3,"KEY_D"); key(kx+0.2,y,r,1.3,"KEY_D")   # space row
            continue
        n=14 if r<5 else 12
        for i in range(n): key(kx+i*p,y,r,1.0,"KEY_D" if (i==0 or i==n-1) else "KEY")
    for i in range(3):
        for r in (2,3): key(kx+0.30+i*p,y0+0.02+r*0.0255,r,1.0,"KEY_D")                                     # nav cluster
    for i in range(3): key(kx+0.30+i*p,y0+0.02+0.0255,1,1.0,"KEY_D")
    for i in range(4):
        for r in range(1,6): key(kx+0.372+i*p*0.86,y0+0.02+r*0.0255,r,0.86,"KEY_D" if i==3 else "KEY")     # numpad
    for k,xx in enumerate((cx+0.32,cx+0.345,cx+0.37)): A.bx((g,"LED_ON" if k==0 else "GREY"),xx,xx+0.010,y0+0.18,y0+0.187,z0+0.030,z0+0.034,0.0)
    A.bx((g,"BEIGE_D"),cx-0.06,cx+0.06,y0+0.002,y0+0.020,z0+0.0,z0+0.0,0.0) if False else None
    A.tube((g,"CABLE"),[(cx,y0+0.19,z0+0.025),(cx,y0+0.28,z0+0.006),(cx+0.12,y0+0.42,z0+0.006),(cx+0.30,y0+0.62,z0+0.012)],0.0032,8)     # curly-less kb cable
def mouse(c,cx,y):
    A,M=c.A,c.M; g="mouse"; z0=ZT
    A.bx((g,"RUBBER"),cx-0.11,cx+0.11,y-0.09,y+0.09,z0,z0+0.004,0.0015)                                      # mouse mat
    A.hull((g,"BEIGE"),[(cx-0.032,y-0.05,z0+0.004),(cx+0.032,y-0.05,z0+0.004),(cx-0.03,y+0.05,z0+0.004),(cx+0.03,y+0.05,z0+0.004),
                        (cx-0.028,y-0.045,z0+0.030),(cx+0.028,y-0.045,z0+0.030),(cx-0.025,y+0.03,z0+0.022),(cx+0.025,y+0.03,z0+0.022)],0.007)
    A.bx((g,"BEIGE_D"),cx-0.003,cx+0.003,y-0.005,y+0.028,z0+0.028,z0+0.032,0.0005); A.bx((g,"BEIGE_D"),cx-0.030,cx+0.030,y+0.0,y+0.003,z0+0.026,z0+0.0285,0.0005)
    A.tube((g,"CABLE_B"),[(cx,y+0.05,z0+0.018),(cx-0.01,y+0.14,z0+0.006),(cx-0.10,y+0.30,z0+0.006),(cx-0.20,y+0.55,z0+0.012)],0.0028,8)
def pc_desktop(c,cx,mk="BEIGE"):
    A,M=c.A,c.M; g="pc"; y0,y1=-7.08,-6.68; z0=ZT; h=0.115
    A.bx((g,mk),cx-0.235,cx+0.235,y0,y1,z0,z0+h,0.005)
    A.fb((g,"BEIGE_D"),'-y',y0,cx-0.225,cx+0.225,z0+0.006,z0+0.108,0.008,0.003)                                # front panel inset
    for k,(xa,w) in enumerate(((-0.205,0.145),(-0.045,0.145))):                                               # 5.25" bays
        A.fb((g,"BLACK"),'-y',y0-0.006,cx+xa,cx+xa+w,z0+0.052,z0+0.098,0.003,0.001)
        A.fb((g,"GREY"),'-y',y0-0.008,cx+xa+0.012,cx+xa+w-0.012,z0+0.070,z0+0.076,0.004,0.0005)                 # disk slot
        A.fb((g,"BEIGE_D"),'-y',y0-0.008,cx+xa+w-0.05,cx+xa+w-0.02,z0+0.056,z0+0.062,0.004,0.001)               # eject button
    A.fb((g,"BLACK"),'-y',y0-0.006,cx+0.125,cx+0.215,z0+0.056,z0+0.098,0.003,0.001); A.fb((g,"GREY"),'-y',y0-0.008,cx+0.135,cx+0.205,z0+0.082,z0+0.086,0.003,0.0005)   # 3.5" drive
    A.fb((g,"LED_ON"),'-y',y0-0.006,cx+0.195,cx+0.202,z0+0.062,z0+0.066,0.002,0.0)
    A.fb((g,"BLACK"),'-y',y0-0.006,cx-0.205,cx-0.135,z0+0.012,z0+0.040,0.003,0.001)                            # display strip
    for k,xx in enumerate((-0.195,-0.178,-0.155,-0.138)): A.fb((g,"LED_A" if k<2 else "LED_R"),'-y',y0-0.007,cx+xx,cx+xx+0.012,z0+0.018,z0+0.034,0.001,0.0) if False else None
    A.fb((g,"LED_AON"),'-y',y0-0.007,cx-0.195,cx-0.185,z0+0.018,z0+0.032,0.0015,0.0); A.fb((g,"LED_ON"),'-y',y0-0.007,cx-0.170,cx-0.160,z0+0.018,z0+0.032,0.0015,0.0)
    A.fb((g,"BEIGE_D"),'-y',y0-0.006,cx+0.020,cx+0.050,z0+0.014,z0+0.040,0.006,0.002)                          # power button
    A.cyl((g,"BRASS"),cx+0.11,y0-0.003,z0+0.030,z0+0.031,0.009,12) if False else None
    A.prism((g,"BRASS"),(cx+0.095,y0,z0+0.028),(cx+0.095,y0-0.004,z0+0.028),0.009,0.009,12)                    # key lock
    text(c.coll,"KESTREL 486",cx-0.02,y0-0.0075,z0+0.027,'-y',0.011,M["KEY_D"],'LEFT',"CR pc badge")
    for k in range(9): A.bx((g,"BEIGE_D"),cx-0.235-0.0015,cx-0.235,y0+0.10+k*0.02,y0+0.112+k*0.02,z0+0.02,z0+0.095,0.0)   # side vents
    for k in range(9): A.bx((g,"BEIGE_D"),cx+0.235,cx+0.2365,y0+0.10+k*0.02,y0+0.112+k*0.02,z0+0.02,z0+0.095,0.0)
    A.prism((g,"BLACK"),(cx-0.12,y1,z0+0.058),(cx-0.12,y1+0.004,z0+0.058),0.038,0.038,20)                        # rear fan grille
    for k in range(3): A.prism((g,"STEEL_L"),(cx-0.12,y1+0.002,z0+0.058),(cx-0.12,y1+0.006,z0+0.058),0.010+k*0.011,0.010+k*0.011,16,0.0,False)
    for k in range(5): A.bx((g,"BLACK"),cx+0.02+k*0.03,cx+0.04+k*0.03,y1,y1+0.003,z0+0.03,z0+0.06,0.0)         # rear ports
    return z0+h
def pc_tower(c,cx,cy_front=-7.10):
    A,M=c.A,c.M; g="tower"; z0=ZT; x0,x1=cx-0.095,cx+0.095; y0,y1=cy_front,cy_front+0.42; h=0.42
    A.bx((g,"BEIGE"),x0,x1,y0,y1,z0,z0+h,0.005)
    A.fb((g,"BEIGE_D"),'-y',y0,x0+0.01,x1-0.01,z0+0.01,z0+h-0.01,0.006,0.003)
    for k in range(3):
        zz=z0+0.30-k*0.048; A.fb((g,"BLACK"),'-y',y0-0.006,x0+0.02,x1-0.02,zz,zz+0.040,0.003,0.001); A.fb((g,"GREY"),'-y',y0-0.008,x0+0.03,x1-0.03,zz+0.014,zz+0.018,0.003,0.0004)
    A.fb((g,"BLACK"),'-y',y0-0.006,x0+0.02,x1-0.02,z0+0.135,z0+0.170,0.003,0.001); A.fb((g,"GREY"),'-y',y0-0.008,x0+0.03,x1-0.03,z0+0.150,z0+0.154,0.003,0.0004)
    A.fb((g,"BEIGE_D"),'-y',y0-0.006,cx-0.012,cx+0.012,z0+0.075,z0+0.100,0.006,0.002); A.fb((g,"LED_ON"),'-y',y0-0.007,cx+0.04,cx+0.048,z0+0.085,z0+0.091,0.0015,0.0)
    A.fb((g,"LED_AON"),'-y',y0-0.007,cx+0.055,cx+0.063,z0+0.085,z0+0.091,0.0015,0.0)
    A.fb((g,"BLACK"),'-y',y0-0.006,x0+0.02,x1-0.02,z0+0.030,z0+0.060,0.003,0.001); text(c.coll,"KESTREL 486DX",cx,y0-0.0065,z0+0.045,'-y',0.008,M["KEY"],'CENTER',"CR pc badge")
    for k in range(10): A.bx((g,"BEIGE_D"),x0-0.0015,x0,y0+0.05+k*0.03,y0+0.062+k*0.03,z0+0.06,z0+0.34,0.0)
def crt(c,cx,zb,scr_key,label,y_f=-6.90):
    """14-inch beige CRT.  front bezel plane y_f facing -y, body runs to +y.  zb = bottom of the housing"""
    A,M=c.A,c.M; g="crt"; W,H=0.375,0.335
    A.bx((g,"BEIGE_D"),cx-0.10,cx+0.10,y_f+0.12,y_f+0.32,zb-0.038,zb-0.010,0.004)                          # swivel base plate
    A.cyl((g,"BEIGE_D"),cx,y_f+0.22,zb-0.02,zb+0.004,0.075,24,0.003)
    A.bx((g,"BEIGE"),cx-W/2,cx+W/2,y_f,y_f+0.10,zb,zb+H,0.010)                                              # front housing
    A.hull((g,"BEIGE"),[(cx-W/2+0.012,y_f+0.10,zb+0.012),(cx+W/2-0.012,y_f+0.10,zb+0.012),(cx-W/2+0.012,y_f+0.10,zb+H-0.012),(cx+W/2-0.012,y_f+0.10,zb+H-0.012),
                        (cx-0.105,y_f+0.36,zb+0.075),(cx+0.105,y_f+0.36,zb+0.075),(cx-0.105,y_f+0.36,zb+H-0.075),(cx+0.105,y_f+0.36,zb+H-0.075)],0.006)   # rear cone
    A.bx((g,"BEIGE_D"),cx-0.145,cx+0.145,y_f-0.004,y_f,zb+0.055,zb+0.297,0.004)                             # screen surround
    A.dome((g,scr_key),(cx,y_f-0.006,zb+0.176),(1,0,0),(0,0,1),(0,-1,0),0.272,0.204,0.010,14,10)              # glass
    A.bx((g,"BEIGE_D"),cx-0.15,cx+0.15,y_f-0.003,y_f,zb+0.052,zb+0.058,0.0015); A.bx((g,"BEIGE_D"),cx-0.15,cx+0.15,y_f-0.003,y_f,zb+0.294,zb+0.300,0.0015)
    A.bx((g,"BEIGE_D"),cx-0.15,cx-0.144,y_f-0.003,y_f,zb+0.052,zb+0.300,0.0015); A.bx((g,"BEIGE_D"),cx+0.144,cx+0.15,y_f-0.003,y_f,zb+0.052,zb+0.300,0.0015)
    A.fb((g,"BEIGE_D"),'-y',y_f,cx-0.17,cx-0.02,zb+0.014,zb+0.040,0.003,0.001)                               # badge plate
    text(c.coll,label,cx-0.16,y_f-0.0035,zb+0.027,'-y',0.013,M["KEY_D"],'LEFT',"CR crt badge")
    for k,xx in enumerate((0.085,0.115,0.145)): A.cyl((g,"BLACK"),cx+xx,y_f,zb+0.027,zb+0.027,0.008,12) if False else A.prism((g,"BLACK"),(cx+xx,y_f,zb+0.027),(cx+xx,y_f-0.012,zb+0.027),0.0075,0.0075,14,0.0,True,0.001)
    A.fb((g,"LED_ON"),'-y',y_f,cx+0.155,cx+0.163,zb+0.023,zb+0.031,0.002,0.0)
    for k in range(9): A.bx((g,"BLACK"),cx-0.125+k*0.028,cx-0.112+k*0.028,y_f+0.11,y_f+0.31,zb+H-0.002,zb+H+0.001,0.0)   # top vents
    for k in range(6): A.bx((g,"BLACK"),cx-0.085+k*0.03,cx-0.075+k*0.03,y_f+0.20,y_f+0.28,zb+H-0.002,zb+H+0.001,0.0) if False else None
    A.cyl((g,"BLACK"),cx,y_f+0.36,zb+0.16,zb+0.16,0.03,12) if False else A.prism((g,"BLACK"),(cx,y_f+0.355,zb+0.176),(cx,y_f+0.372,zb+0.176),0.035,0.032,16)   # neck boss
    A.tube((g,"CABLE_G"),[(cx,y_f+0.372,zb+0.176),(cx+0.02,y_f+0.42,zb+0.10),(cx+0.06,y_f+0.44,zb-0.02)],0.006,8)
def terminal(c,cx,scr_key,label,tower_side=None,case=True):
    A=c.A
    keyboard(c,cx,-7.535)
    mouse(c,cx+0.36,-7.43)
    if case:
        top=pc_desktop(c,cx); crt(c,cx,top+0.045,scr_key,label,y_f=-6.90)
    else:
        A.bx(("stand","BEIGE_D"),cx-0.12,cx+0.12,-6.99,-6.70,ZT,ZT+0.022,0.004); crt(c,cx,ZT+0.055,scr_key,label,y_f=-6.90)
        pc_tower(c,cx+0.36 if tower_side is None else tower_side,-7.10)
def chair(c,cx,cy,yaw=0.0):
    A,M=c.A,c.M; g="chair"; A.begin(cx,cy,yaw,0.0)
    # star base
    for k in range(5):
        a=math.radians(90+72*k); ux,uy=math.cos(a),math.sin(a); vx,vy=-uy,ux
        def P(r,l,z): return (ux*r+vx*l,uy*r+vy*l,z)
        A.hull((g,"STEEL"),[P(0.03,-0.032,FZ+0.076),P(0.03,0.032,FZ+0.076),P(0.03,-0.032,FZ+0.122),P(0.03,0.032,FZ+0.122),P(0.31,-0.018,FZ+0.058),P(0.31,0.018,FZ+0.058),P(0.31,-0.018,FZ+0.088),P(0.31,0.018,FZ+0.088)],0.004)
        cx0,cy0=ux*0.30,uy*0.30
        A.prism((g,"STEEL_L"),(cx0,cy0,FZ+0.058),(cx0,cy0,FZ+0.074),0.007,0.007,10)                              # caster stem
        A.bx((g,"BLACK"),cx0-0.012,cx0+0.012,cy0-0.012,cy0+0.012,FZ+0.050,FZ+0.062,0.002) if False else None
        for s in (-1,1):
            p0=(cx0+vx*s*0.014-ux*0.0,cy0+vy*s*0.014,FZ+0.026); A.prism((g,"BLACK"),(p0[0]-ux*0.0-vx*s*0.007,p0[1]-vy*s*0.007,p0[2]),(p0[0]+vx*s*0.007,p0[1]+vy*s*0.007,p0[2]),0.026,0.026,16,0.0,True,0.002)
        A.bx((g,"BLACK"),cx0-0.005-abs(vx)*0.02,cx0+0.005+abs(vx)*0.02,cy0-0.005-abs(vy)*0.02,cy0+0.005+abs(vy)*0.02,FZ+0.05,FZ+0.058,0.002)
    A.cyl((g,"STEEL"),0,0,FZ+0.070,FZ+0.128,0.052,20,0.004)                                                     # hub
    A.prism((g,"BLACK"),(0,0,FZ+0.128),(0,0,FZ+0.22),0.048,0.034,18)                                            # cover cone
    A.cyl((g,"STEEL_L"),0,0,FZ+0.22,FZ+0.40,0.026,18); A.cyl((g,"BLACK"),0,0,FZ+0.30,FZ+0.44,0.036,18,0.003)   # gas lift + bellows
    A.bx((g,"BLACK"),-0.13,0.13,-0.12,0.14,FZ+0.44,FZ+0.475,0.005)                                              # mechanism plate
    A.cylx((g,"STEEL_L"),0.08,0.15,-0.09,FZ+0.455,0.006,10)                                                     # tilt lever
    A.bx((g,"BLACK"),-0.235,0.235,-0.225,0.235,FZ+0.455,FZ+0.475,0.006)                                          # seat pan
    A.hull((g,"FABRIC"),[(-0.235,-0.225,FZ+0.475),(0.235,-0.225,FZ+0.475),(-0.235,0.225,FZ+0.475),(0.235,0.225,FZ+0.475),
                         (-0.225,-0.215,FZ+0.545),(0.225,-0.215,FZ+0.545),(-0.225,0.185,FZ+0.545),(0.225,0.185,FZ+0.545),(-0.235,0.235,FZ+0.500),(0.235,0.235,FZ+0.500),(-0.230,0.20,FZ+0.535),(0.230,0.20,FZ+0.535)],0.012)
    A.bx((g,"FABRIC_O"),-0.19,0.19,0.205,0.215,FZ+0.497,FZ+0.507,0.002) if False else None
    A.bx((g,"STEEL"),-0.02,0.02,-0.215,-0.185,FZ+0.475,FZ+0.68,0.004)                                          # back spine
    A.bx((g,"BLACK"),-0.205,0.205,-0.256,-0.230,FZ+0.65,FZ+1.02,0.012)                                           # back shell
    A.bx((g,"FABRIC"),-0.192,0.192,-0.230,-0.192,FZ+0.66,FZ+1.01,0.014)                                          # back cushion
    A.bx((g,"FABRIC_O"),-0.184,0.184,-0.193,-0.189,FZ+0.72,FZ+0.78,0.001)                                        # lumbar band
    for sx in (-1,1):
        xa=sx*0.262
        A.bx((g,"STEEL"),xa-0.014,xa+0.014,-0.060,-0.030,FZ+0.475,FZ+0.665,0.004)                                # arm post
        A.bx((g,"BLACK"),xa-0.032,xa+0.032,-0.14,0.13,FZ+0.665,FZ+0.692,0.009)                                   # arm pad
    A.end()
