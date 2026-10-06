"""Control-room furniture and equipment: server rack, copier + printer corner, tall shelving, cot, lockers, break corner, work table, TV credenza."""
import math
from crk import text
FZ=5.40
def ledk(c,kind="G"): return c.R.choice({"G":["LED_G0","LED_G1","LED_G2","LED_G3"],"A":["LED_A0","LED_A1","LED_A2","LED_A3"],"R":["LED_R0","LED_R1","LED_R2"]}[kind])
def wall_quad(c,face,p,lc,zc,w,h,key,frame=True,fkey="BLACK",g="deco",off=None,paper=True):
    A=c.A; hw,hh=w/2,h/2; d=0.004
    p=p+(-1 if face in('-x','-y') else 1)*0.022 if off is None else p+(-1 if face in('-x','-y') else 1)*off
    if face=='+y': pts=[(lc+hw,p+d,zc-hh),(lc-hw,p+d,zc-hh),(lc-hw,p+d,zc+hh),(lc+hw,p+d,zc+hh)]
    elif face=='-x': pts=[(p-d,lc+hw,zc-hh),(p-d,lc-hw,zc-hh),(p-d,lc-hw,zc+hh),(p-d,lc+hw,zc+hh)]
    elif face=='+x': pts=[(p+d,lc-hw,zc-hh),(p+d,lc+hw,zc-hh),(p+d,lc+hw,zc+hh),(p+d,lc-hw,zc+hh)]
    else: pts=[(lc-hw,p-d,zc-hh),(lc+hw,p-d,zc-hh),(lc+hw,p-d,zc+hh),(lc-hw,p-d,zc+hh)]
    A.plane((g,key),*pts)
    if paper: A.fb((g,"PAPER"),face,p,lc-hw-0.006,lc+hw+0.006,zc-hh-0.006,zc+hh+0.006,0.003,0.0005)
    if frame:
        for (a,b,z0,z1) in ((lc-hw-0.01,lc+hw+0.01,zc+hh+0.006,zc+hh+0.014),(lc-hw-0.01,lc+hw+0.01,zc-hh-0.014,zc-hh-0.006),(lc-hw-0.01,lc-hw-0.006,zc-hh-0.014,zc+hh+0.014),(lc+hw+0.006,lc+hw+0.01,zc-hh-0.014,zc+hh+0.014)):
            A.fb((g,fkey),face,p,a,b,z0,z1,0.009,0.0015)
    for (u,v) in ((-hw,hh),(hw,hh)):                                                                       # tape at the top corners
        if face in('+y','-y'): A.fb((g,"PAPER"),face,p+(0.0035 if face=='+y' else -0.0035),lc+u-0.02*(1 if u>0 else -1)*0.0-0.02,lc+u+0.02,zc+v-0.03,zc+v+0.01,0.0015,0.0)
def rack(c):
    A,M=c.A,c.M; g="rack"; xf=1.05; xb=1.95; yc=-10.35; W=0.60
    y0,y1=yc-W/2,yc+W/2
    A.bx((g,"STEEL"),xf,xb,y0,y1,FZ+0.07,FZ+0.09,0.004)                                                       # base plate
    A.bx((g,"TRIM"),xf,xb,y0,y1,FZ+0.03,FZ+0.07,0.004)                                                        # plinth
    for (x,y) in ((xf+0.03,y0+0.03),(xf+0.03,y1-0.03),(xb-0.03,y0+0.03),(xb-0.03,y1-0.03)): A.cyl((g,"BLACK"),x,y,FZ,FZ+0.03,0.022,14)
    for x in (xf,xb-0.032):
        for y in (y0,y1-0.032): A.bx((g,"STEEL"),x,x+0.032,y,y+0.032,FZ+0.07,FZ+2.05,0.003)                 # posts
    A.bx((g,"STEEL"),xf,xb,y0,y1,FZ+2.05,FZ+2.075,0.004)
    for (ya,yb) in ((y0,y0+0.012),(y1-0.012,y1)): A.bx((g,"TRIM"),xf+0.032,xb-0.032,ya,yb,FZ+0.09,FZ+2.05,0.003)   # side panels
    for k in range(7): A.bx((g,"BLACK"),xf+0.15+k*0.10,xf+0.15+k*0.10+0.04,y0-0.001,y0+0.013,FZ+1.6,FZ+1.9,0.0)  # louvre slots
    for x in (xf+0.1,xf+0.4,xf+0.7): A.bx((g,"BLACK"),x,x+0.02,y0-0.001,y0+0.013,FZ+1.6,FZ+1.9,0.0) if False else None
    yl,yr=yc-0.2415,yc+0.2415; U=0.0445; z=FZ+0.16
    def plate(u,mk="BLACK",inset=0.0,pull=0.0):
        nonlocal z
        px=xf-pull
        z0,z1=z+0.003,z+u*U-0.003; A.fb((g,mk),'-x',px,yl,yr,z0,z1,0.012,0.002)
        for zz in (z0+0.011,z1-0.011):
            for yy in (yl+0.011,yr-0.011): A.screw((g,"STEEL_L"),'-x',px-0.012,yy,zz,0.0045)
        r=(z0,z1); z+=u*U; return r
    # UPS (2U, heavy) with display
    z0,z1=plate(2,"BLACK"); text(c.coll,"VOLTEX  UPS 1500",xf-0.0125,yl+0.03,(z0+z1)/2+0.012,'-x',0.011,M["STEEL_L"],'LEFT',"CR rack label")
    A.fb((g,"LED_AON"),'-x',xf-0.012,yr-0.10,yr-0.045,z0+0.018,z0+0.03,0.002,0.0); A.fb((g,"LED_ON"),'-x',xf-0.012,yr-0.035,yr-0.025,z0+0.02,z0+0.028,0.002,0.0)
    for k in range(6): A.fb((g,"LED_ON" if k<4 else "LED_AON"),'-x',xf-0.012,yl+0.03+k*0.014,yl+0.037+k*0.014,z0+0.014,z0+0.021,0.002,0.0)
    plate(1,"BLACK")
    # patch panel (1U, 24 ports)
    z0,z1=plate(1,"GREY")
    for k in range(24): A.fb((g,"BLACK"),'-x',xf-0.012,yl+0.018+k*0.0175,yl+0.018+k*0.0175+0.012,z0+0.012,z0+0.026,0.004,0.0)
    for k in range(24):
        if c.R.random()<0.7: A.fb((g,ledk(c,"G") if c.R.random()<0.7 else ledk(c,"A")),'-x',xf-0.016,yl+0.022+k*0.0175,yl+0.026+k*0.0175,z0+0.028,z0+0.031,0.001,0.0)
    # patch cords
    for k in range(9):
        yy=yl+0.03+k*0.0175*2.6; c.A.tube((g,"CABLE_G" if k%3 else "CABLE_B"),[(xf-0.012,yy,z0+0.018),(xf-0.05,yy-0.005,z0+0.0),(xf-0.06,yl-0.02,z0-0.10-k*0.006),(xf-0.03,yl-0.03,max(z0-0.35,FZ+0.05))],0.0032,6)
    for k in range(9):                                                                                      # coloured tags on the patch cords
        yy=yl+0.03+k*0.0175*2.6; A.bx((g,("ORANGE","YELLOW","RED")[k%3]),xf-0.058,xf-0.046,yy-0.007,yy+0.007,z0-0.055-k*0.006,z0-0.040-k*0.006,0.001)
    loomx=xf-0.07
    for k in range(6):                                                                                      # cable loom down the right-hand duct with cable ties
        dy=(k%3-1)*0.006; dz=(k//3-0.5)*0.006
        A.tube((g,"CABLE" if k%2 else "CABLE_G"),[(loomx+dz,y1+0.05+dy,FZ+1.95),(loomx+dz-0.01,y1+0.06+dy,FZ+1.2),(loomx+dz-0.03,y1+0.07+dy,FZ+0.55),(loomx+dz-0.05,y1+0.085+dy,FZ+0.05)],0.0055,8)
    for zz in (FZ+1.75,FZ+1.45,FZ+1.15,FZ+0.85,FZ+0.55,FZ+0.30): A.bx((g,"ORANGE"),loomx-0.012,loomx+0.012,y1+0.04,y1+0.085,zz,zz+0.006,0.001)
    plate(1,"BLACK")
    for s in range(2):                                                                                      # two 3U servers; the second one is slid half out on its rails
        pull=0.20 if s==1 else 0.0; px=xf-pull
        z0,z1=plate(3,"BEIGE_D" if s==0 else "GREY",pull=pull)
        for k in range(4):
            ya=yl+0.03+k*0.083; A.fb((g,"BLACK"),'-x',px-0.012,ya,ya+0.074,z0+0.024,z0+0.104,0.004,0.001)
            A.fb((g,"STEEL"),'-x',px-0.016,ya+0.006,ya+0.068,z0+0.05,z0+0.058,0.003,0.0005)
            A.fb((g,ledk(c,"G")),'-x',px-0.016,ya+0.007,ya+0.014,z0+0.030,z0+0.036,0.002,0.0); A.fb((g,ledk(c,"A")),'-x',px-0.016,ya+0.018,ya+0.025,z0+0.030,z0+0.036,0.002,0.0)
        A.prism((g,"BRASS"),(px-0.012,yr-0.035,z0+0.016),(px-0.016,yr-0.035,z0+0.016),0.008,0.008,12)
        text(c.coll,"MERIDIAN  MS-"+str(200+s*30),px-0.0125,yr-0.02,z0+0.118,'-x',0.0085,M["KEY"],'RIGHT',"CR rack label")
        if s==1:                                                                                          # rails, open tray, board, fan
            for yy in (yl+0.010,yr-0.010): A.bx((g,"STEEL_L"),px,xf+0.03,yy-0.006,yy+0.006,z0+0.030,z0+0.042,0.002)
            A.bx((g,"BLACK"),px,xf+0.03,yl+0.02,yr-0.02,z0+0.012,z0+0.020,0.002)
            for (ya,yb) in ((yl+0.02,yl+0.03),(yr-0.03,yr-0.02)): A.bx((g,"BLACK"),px,xf+0.03,ya,yb,z0+0.012,z0+0.115,0.002)
            A.bx((g,"GREY"),px+0.03,xf-0.01,yl+0.05,yr-0.05,z0+0.034,z0+0.040,0.001)
            for kk in range(6): A.bx((g,"BLACK"),px+0.05+kk*0.02,px+0.066+kk*0.02,yl+0.07+(kk%3)*0.07,yl+0.10+(kk%3)*0.07,z0+0.040,z0+0.052,0.001)
            A.cylx((g,"BLACK"),px+0.02,px+0.05,(yl+yr)/2,z0+0.085,0.032,18); A.cylx((g,"STEEL"),px+0.0195,px+0.0505,(yl+yr)/2,z0+0.085,0.012,12)
            A.tube((g,"CABLE_G"),[(px+0.10,yr-0.06,z0+0.042),(px+0.05,yr-0.03,z0+0.05),(px-0.02,yr+0.005,z0+0.0)],0.004,6)              # ribbon dangling out of the tray
        plate(1,"BLACK")
    z0,z1=plate(2,"BEIGE_D")                                                                                # tape drive
    A.fb((g,"BLACK"),'-x',xf-0.012,yl+0.03,yl+0.30,z0+0.02,z0+0.06,0.004,0.001); A.fb((g,"GREY"),'-x',xf-0.016,yl+0.05,yl+0.28,z0+0.036,z0+0.042,0.003,0.0005)
    A.fb((g,"BLACK"),'-x',xf-0.012,yr-0.14,yr-0.04,z0+0.03,z0+0.058,0.003,0.001); A.fb((g,"LED_AON"),'-x',xf-0.015,yr-0.13,yr-0.05,z0+0.036,z0+0.046,0.002,0.0)
    z0,z1=plate(1,"GREY")                                                                                   # fan panel
    for k in range(4):
        yy=yl+0.06+k*0.12; A.prism((g,"BLACK"),(xf-0.012,yy,(z0+z1)/2),(xf-0.014,yy,(z0+z1)/2),0.017,0.017,20)
        for r in (0.006,0.012): A.prism((g,"STEEL"),(xf-0.013,yy,(z0+z1)/2),(xf-0.0165,yy,(z0+z1)/2),r,r,16,0,False)
    for u in (1,1,2):
        z0,z1=plate(u,"BLACK")
    def f_switch():                                                                                           # 1U switch: two rows of ports + link LEDs
        z0,z1=plate(1,"GREY")
        for r in range(2):
            for k in range(12): A.fb((g,"BLACK"),'-x',xf-0.012,yl+0.02+k*0.0185+r*0.0,yl+0.02+k*0.0185+0.012,z0+0.010+r*0.016,z0+0.022+r*0.016,0.004,0.0)
        for k in range(12):
            if c.R.random()<0.7: A.fb((g,ledk(c,"G") if c.R.random()<0.75 else ledk(c,"A")),'-x',xf-0.016,yl+0.022+k*0.0185,yl+0.026+k*0.0185,z0+0.034,z0+0.037,0.001,0.0)
    def f_modem():                                                                                            # 2U modem bank: columns of status LEDs
        z0,z1=plate(2,"BEIGE_D")
        for k in range(8):
            x_=yl+0.03+k*0.055; A.fb((g,"BLACK"),'-x',xf-0.012,x_,x_+0.040,z0+0.012,z0+0.075,0.003,0.001)
            for r in range(3): A.fb((g,ledk(c,"G" if r<2 else "A")),'-x',xf-0.016,x_+0.012,x_+0.020,z0+0.020+r*0.018,z0+0.027+r*0.018,0.001,0.0)
        text(c.coll,"TAKAMI MB-8",xf-0.0125,yr-0.03,z0+0.082,'-x',0.0085,M["KEY_D"],'RIGHT',"CR rack label")
    def f_kvm():                                                                                              # 1U keyboard drawer
        z0,z1=plate(1,"BLACK"); A.fb((g,"STEEL_L"),'-x',xf-0.012,(yl+yr)/2-0.09,(yl+yr)/2+0.09,(z0+z1)/2-0.004,(z0+z1)/2+0.004,0.014,0.003)
        A.fb((g,"YELLOW"),'-x',xf-0.012,yr-0.08,yr-0.03,z0+0.010,z0+0.022,0.001,0.0)
    def f_vent():                                                                                             # perforated blank
        z0,z1=plate(1,"BLACK")
        for k in range(8): A.fb((g,"GREY"),'-x',xf-0.012,yl+0.03,yr-0.03,z0+0.006+k*0.0045,z0+0.0085+k*0.0045,0.0015,0.0)
    seq=[f_switch,lambda: plate(1,"BLACK"),f_modem,f_vent,f_kvm,lambda: plate(1,"BLACK"),f_switch,f_vent,lambda: plate(1,"BLACK"),f_modem,f_kvm]
    i_=0
    while z+U<FZ+1.98:
        seq[i_%len(seq)](); i_+=1
    # side cable duct (front-left) and trunking to ceiling
    A.bx((g,"BLACK"),xf-0.04,xf-0.005,y1-0.005,y1+0.045,FZ+0.16,FZ+2.05,0.003)
    A.bx((g,"BLACK"),xb-0.30,xb,yc-0.14,yc+0.14,FZ+2.075,8.50,0.005)                                          # trunking up to the ceiling
    A.bx((g,"TRIM"),xb-0.31,xb+0.0,yc-0.15,yc+0.15,8.44,8.50,0.005)
    A.bx((g,"STEEL"),xf,xb,y0,y1,FZ+2.075,FZ+2.11,0.004) if False else None
    for k in range(5): A.tube((g,"CABLE_G"),[(xf-0.03,yl-0.03+0.0,FZ+0.9),(xf-0.045+k*0.004,y1+0.02,FZ+0.7-k*0.02),(xf-0.02,y1+0.03,FZ+0.2)],0.004,6) if False else None
    text(c.coll,"SERVER 04 - DO NOT POWER DOWN",xf-0.0,y0-0.0,FZ+2.0,'-y',0.02,M["ORANGE"],'LEFT',"CR rack sign") if False else None
    A.fb((g,"YELLOW"),'-x',xf,y0+0.04,y1-0.04,FZ+2.012,FZ+2.048,0.003,0.001)                                 # rack header label
    text(c.coll,"SERVER 04  -  DO NOT POWER DOWN",xf-0.0035,(y0+y1)/2,FZ+2.030,'-x',0.0135,M["BLACK"],'CENTER',"CR rack head")
def copier(c):
    A,M=c.A,c.M; g="copier"; xf=1.30; xb=2.0; y0,y1=-8.85,-7.95; ym=(y0+y1)/2
    A.bx((g,"BEIGE"),xf,xb,y0,y1,FZ+0.03,FZ+0.62,0.008); A.bx((g,"BEIGE_D"),xf+0.02,xb,y0+0.01,y1-0.01,FZ,FZ+0.03,0.004)
    for k in range(2):
        za=FZ+0.06+k*0.27; A.fb((g,"BEIGE_D"),'-x',xf,y0+0.03,y1-0.03,za,za+0.24,0.008,0.003); A.fb((g,"STEEL_L"),'-x',xf-0.008,ym-0.12,ym+0.12,za+0.16,za+0.175,0.02,0.004)
        A.fb((g,"PAPER"),'-x',xf-0.008,y1-0.16,y1-0.06,za+0.04,za+0.10,0.001,0.0)
    A.bx((g,"BEIGE"),xf,xb,y0,y1,FZ+0.62,FZ+0.94,0.008)                                                       # scanner body
    A.hull((g,"BEIGE_D"),[(xf,y0+0.03,FZ+0.94),(xf,y1-0.03,FZ+0.94),(xf+0.34,y0+0.03,FZ+0.94),(xf+0.34,y1-0.03,FZ+0.94),(xf,y0+0.03,FZ+0.99),(xf,y1-0.03,FZ+0.99),(xf+0.34,y0+0.03,FZ+0.99),(xf+0.34,y1-0.03,FZ+0.99)],0.005) if False else None
    A.bx((g,"BEIGE"),xf+0.02,xb-0.02,y0+0.02,y1-0.02,FZ+0.94,FZ+0.99,0.008)                                   # platen lid
    A.bx((g,"GLASS"),xf+0.06,xb-0.06,y0+0.06,y1-0.06,FZ+0.935,FZ+0.94,0.0) if False else None
    A.hull((g,"BEIGE_D"),[(xf-0.05,y0+0.05,FZ+0.82),(xf-0.05,y1-0.05,FZ+0.82),(xf,y0+0.05,FZ+0.94),(xf,y1-0.05,FZ+0.94),(xf-0.05,y0+0.05,FZ+0.86),(xf-0.05,y1-0.05,FZ+0.86),(xf,y0+0.05,FZ+0.86),(xf,y1-0.05,FZ+0.86)],0.004) if False else None
    A.hull((g,"BEIGE_D"),[(xf-0.06,y1-0.42,FZ+0.70),(xf-0.06,y1-0.04,FZ+0.70),(xf,y1-0.42,FZ+0.70),(xf,y1-0.04,FZ+0.70),(xf-0.06,y1-0.42,FZ+0.76),(xf-0.06,y1-0.04,FZ+0.76),(xf,y1-0.42,FZ+0.82),(xf,y1-0.04,FZ+0.82)],0.004)   # control console
    for r in range(3):
        for k in range(5): A.bx((g,"BLACK" if (r+k)%3 else "ORANGE"),xf-0.052+r*0.018,xf-0.040+r*0.018,y1-0.38+k*0.028,y1-0.365+k*0.028,FZ+0.76+r*0.018,FZ+0.77+r*0.018,0.001) if False else None
    A.fb((g,"BLACK"),'-x',xf-0.05,y1-0.40,y1-0.28,FZ+0.755,FZ+0.79,0.004,0.001); A.fb((g,"LED_AON"),'-x',xf-0.054,y1-0.39,y1-0.29,FZ+0.762,FZ+0.782,0.002,0.0)
    for k in range(6): A.fb((g,"BLACK" if k%3 else "ORANGE"),'-x',xf-0.05,y1-0.26+k*0.03,y1-0.24+k*0.03+0.012,FZ+0.755,FZ+0.775,0.004,0.001)
    A.fb((g,"LED_RON"),'-x',xf-0.05,y1-0.07,y1-0.06,FZ+0.79,FZ+0.80,0.002,0.0)
    A.hull((g,"BLACK"),[(xf-0.20,y0+0.10,FZ+0.44),(xf-0.20,y0+0.42,FZ+0.44),(xf,y0+0.10,FZ+0.46),(xf,y0+0.42,FZ+0.46),(xf-0.20,y0+0.10,FZ+0.45),(xf-0.20,y0+0.42,FZ+0.45),(xf,y0+0.10,FZ+0.47),(xf,y0+0.42,FZ+0.47)],0.003)   # output tray
    A.bx((g,"PAPER"),xf-0.18,xf-0.02,y0+0.13,y0+0.39,FZ+0.47,FZ+0.51,0.001)
    text(c.coll,"RIVEN 3100",xf-0.0085,ym,FZ+0.53,'-x',0.022,M["KEY_D"],'CENTER',"CR copier brand")
    A.fb((g,"YELLOW"),'-x',xf,y0+0.03,y0+0.24,FZ+0.86,FZ+0.90,0.002,0.0005) if False else None
def printer(c):
    A,M=c.A,c.M; g="printer"; xf=1.52; xb=2.0; y0,y1=-9.55,-8.97; ym=(y0+y1)/2; ZT=FZ+0.62
    for (x,y) in ((xf+0.02,y0+0.02),(xf+0.02,y1-0.02),(xb-0.02,y0+0.02),(xb-0.02,y1-0.02)): A.bx((g,"STEEL"),x-0.012,x+0.012,y-0.012,y+0.012,FZ,ZT,0.002)   # stand
    A.bx((g,"STEEL"),xf,xb,y0,y1,ZT,ZT+0.02,0.003); A.bx((g,"STEEL"),xf+0.02,xb-0.02,y0+0.02,y1-0.02,FZ+0.24,FZ+0.256,0.002)
    A.bx((g,"PAPER"),xf+0.10,xf+0.33,ym-0.14,ym+0.14,FZ+0.256,FZ+0.42,0.001)                                    # fan-fold stack
    for k in range(9): A.bx((g,"PAPER"),xf+0.10,xf+0.33,ym-0.141,ym+0.141,FZ+0.256+k*0.018,FZ+0.256+k*0.018+0.0025,0.0) if False else None
    for k in range(10): A.bx((g,"BEIGE_D"),xf+0.10,xf+0.33,ym-0.14,ym-0.128,FZ+0.27+k*0.015,FZ+0.272+k*0.015,0.0) if False else None
    A.bx((g,"BEIGE"),xf+0.03,xb-0.06,ym-0.20,ym+0.20,ZT+0.02,ZT+0.12,0.006)                                      # printer body
    A.hull((g,"BEIGE"),[(xf+0.03,ym-0.20,ZT+0.12),(xf+0.03,ym+0.20,ZT+0.12),(xb-0.06,ym-0.20,ZT+0.12),(xb-0.06,ym+0.20,ZT+0.12),(xf+0.06,ym-0.19,ZT+0.16),(xf+0.06,ym+0.19,ZT+0.16),(xb-0.10,ym-0.19,ZT+0.19),(xb-0.10,ym+0.19,ZT+0.19)],0.006)
    A.fb((g,"BEIGE_D"),'-x',xf+0.03,ym-0.18,ym+0.18,ZT+0.04,ZT+0.095,0.004,0.002)
    A.fb((g,"BLACK"),'-x',xf+0.026,ym-0.16,ym-0.03,ZT+0.055,ZT+0.075,0.003,0.001)
    for k in range(5): A.fb((g,"KEY_D" if k%2 else "KEY"),'-x',xf+0.026,ym+0.01+k*0.032,ym+0.032+k*0.032,ZT+0.055,ZT+0.070,0.004,0.001)
    A.fb((g,"LED_ON"),'-x',xf+0.026,ym-0.17,ym-0.16,ZT+0.085,ZT+0.09,0.002,0.0)
    text(c.coll,"AXON LQ-2",xf+0.0255,ym+0.10,ZT+0.106,'-x',0.011,M["KEY_D"],'CENTER',"CR printer brand")
    A.bx((g,"PAPER"),xf+0.30,xf+0.32,ym-0.13,ym+0.13,ZT+0.19,ZT+0.42,0.0)                                         # sheet rising from rear slot
    A.hull((g,"PAPER"),[(xf+0.03,ym-0.13,ZT+0.12),(xf+0.03,ym+0.13,ZT+0.12),(xf-0.14,ym-0.13,ZT+0.06),(xf-0.14,ym+0.13,ZT+0.06),(xf+0.03,ym-0.13,ZT+0.122),(xf+0.03,ym+0.13,ZT+0.122),(xf-0.14,ym-0.13,ZT+0.062),(xf-0.14,ym+0.13,ZT+0.062)],0.0)   # printed page draping out the front
    A.plane((g,"N_log"),(xf-0.145,ym+0.115,ZT+0.0615),(xf-0.145,ym-0.115,ZT+0.0615),(xf-0.145+0.13,ym-0.115,ZT+0.124),(xf-0.145+0.13,ym+0.115,ZT+0.124)) if False else None
def shelving(c):
    A,M=c.A,c.M; g="shelf"; x0,x1=-4.80,-4.40; ya,yb=-9.90,-8.30
    for y in (ya,(ya+yb)/2,yb-0.04): A.bx((g,"STEEL"),x0,x1,y,y+0.04,FZ,FZ+2.25,0.003)
    zs=[FZ+0.18+0.42*k for k in range(5)]
    for z in zs:
        A.bx((g,"STEEL"),x0+0.005,x1,ya,yb,z,z+0.022,0.002); A.bx((g,"STEEL"),x1-0.012,x1,ya,yb,z+0.022,z+0.05,0.0015)
    A.bx((g,"STEEL"),x0,x1,ya,yb,FZ+2.25,FZ+2.27,0.003)
    R=c.R; cols=["ORANGE","YELLOW","RED","LOCKER","BLACK","STEEL_L","KEY_D","BEIGE_D"]
    for si,z in enumerate(zs):
        y=ya+0.06; z0=z+0.022; lim=yb-0.05
        while y<lim-0.1:
            kind=R.random()
            if si in(0,1) and kind<0.45:                                        # cardboard boxes
                w=R.uniform(0.15,0.30); h=R.uniform(0.16,0.30); d=R.uniform(0.28,0.34)
                if y+w>lim: break
                A.bx((g,"CARD"),x0+0.02,x0+0.02+d,y,y+w,z0,z0+h,0.004); A.bx((g,"PAPER"),x0+0.02+d-0.001,x0+0.02+d+0.001,y+0.02,y+w-0.03,z0+h*0.55,z0+h*0.55+0.05,0.0)
                y+=w+0.02
            elif kind<0.85:                                                       # binders
                n=R.randint(3,7); h=R.uniform(0.28,0.33) if si>1 else R.uniform(0.26,0.31)
                for k in range(n):
                    w=R.uniform(0.04,0.065)
                    if y+w>lim: break
                    mk=R.choice(cols); lean=R.random()<0.08
                    A.bx((g,mk),x0+0.03,x0+0.03+0.30,y,y+w-0.004,z0,z0+h,0.003)
                    A.bx((g,"PAPER"),x0+0.03+0.30-0.001,x0+0.03+0.30+0.001,y+0.008,y+w-0.012,z0+h*0.5,z0+h*0.5+0.05,0.0)
                    y+=w
                y+=0.02
            else:
                y+=R.uniform(0.04,0.10)
    # loose items on top
    A.hull((g,"YELLOW"),[(x0+0.08,-9.30,FZ+2.27),(x0+0.30,-9.30,FZ+2.27),(x0+0.08,-9.06,FZ+2.27),(x0+0.30,-9.06,FZ+2.27),(x0+0.12,-9.26,FZ+2.36),(x0+0.26,-9.26,FZ+2.36),(x0+0.12,-9.10,FZ+2.36),(x0+0.26,-9.10,FZ+2.36)],0.012)   # hard hat
    A.bx((g,"YELLOW"),x0+0.05,x0+0.32,-9.42,-9.34,FZ+2.27,FZ+2.29,0.003) if False else None
    A.bx((g,"RED"),x0+0.06,x0+0.30,-8.68,-8.44,FZ+2.27,FZ+2.36,0.004); A.fb((g,"PAPER"),'+x',x0+0.30,-8.60,-8.52,FZ+2.29,FZ+2.34,0.002,0.0)   # first-aid box
    text(c.coll,"SUPPLIES",x0+0.312,-9.60,FZ+2.14,'+x',0.02,M["BLACK"],'CENTER',"CR shelf label") if False else None
def cot(c):
    A,M=c.A,c.M; g="cot"; x0,x1=-4.72,-3.98; y0,y1=-11.86,-10.08; zt=FZ+0.40
    for (ya,yb) in ((y0,y0+0.03),(y1-0.03,y1)): A.bx((g,"STEEL"),x0,x1,ya,yb,zt-0.05,zt,0.003)
    for (xa,xb) in ((x0,x0+0.03),(x1-0.03,x1)): A.bx((g,"STEEL"),xa,xb,y0,y1,zt-0.05,zt,0.003)
    A.bx((g,"CANVAS"),x0+0.03,x1-0.03,y0+0.03,y1-0.03,zt-0.028,zt-0.014,0.004)
    for yy in (y0+0.04,y1-0.04):
        for s in (0,1):
            xa,xb=(x0+0.03,x1-0.03) if s==0 else (x1-0.03,x0+0.03)
            A.prism((g,"STEEL"),(xa,yy,FZ+0.01),(xb,yy,zt-0.05),0.013,0.013,10)
            A.prism((g,"STEEL"),(xa,yy,FZ+0.01),(xa,yy,FZ+0.0),0.02,0.02,10,0,True) if False else None
    for yy in (y0+0.04,y1-0.04): A.cylx((g,"STEEL_L"),x0+0.03,x1-0.03,yy,FZ+0.185,0.009,10); A.cylx((g,"BLACK"),x0+0.02,x0+0.06,yy,FZ+0.012,0.018,12); A.cylx((g,"BLACK"),x1-0.06,x1-0.02,yy,FZ+0.012,0.018,12)
    A.hull((g,"PILLOW"),[(x0+0.10,y0+0.10,zt-0.014),(x1-0.10,y0+0.10,zt-0.014),(x0+0.10,y0+0.42,zt-0.014),(x1-0.10,y0+0.42,zt-0.014),(x0+0.12,y0+0.12,zt+0.09),(x1-0.12,y0+0.12,zt+0.09),(x0+0.12,y0+0.40,zt+0.07),(x1-0.12,y0+0.40,zt+0.07)],0.02)
    A.hull((g,"BLANKET"),[(x0+0.04,y0+0.55,zt-0.014),(x1-0.04,y0+0.55,zt-0.014),(x0+0.04,y1-0.06,zt-0.014),(x1-0.04,y1-0.06,zt-0.014),(x0+0.05,y0+0.58,zt+0.07),(x1-0.05,y0+0.58,zt+0.07),(x0+0.05,y1-0.10,zt+0.05),(x1-0.05,y1-0.10,zt+0.05)],0.015)
    A.bx((g,"BLANKET"),x0+0.04,x1-0.04,y0+0.56,y0+0.62,zt+0.07,zt+0.078,0.004)
    for k in range(3): A.bx((g,"YELLOW"),x0+0.04,x1-0.04,y1-0.30-k*0.012,y1-0.29-k*0.012,zt+0.058,zt+0.06,0.0)
    A.hull((g,"BLACK"),[(x1+0.06,-11.20,FZ),(x1+0.20,-11.20,FZ),(x1+0.06,-11.02,FZ),(x1+0.20,-11.02,FZ),(x1+0.07,-11.18,FZ+0.16),(x1+0.16,-11.18,FZ+0.16),(x1+0.07,-11.04,FZ+0.16),(x1+0.16,-11.04,FZ+0.16)],0.012) # boot
def lockers(c):
    A,M=c.A,c.M; g="lockers"; xf=1.55; xb=2.0; y0=-11.86; w=0.28
    for k in range(3):
        ya,yb=y0+k*w,y0+(k+1)*w
        A.bx((g,"LOCKER"),xf,xb,ya+0.001,yb-0.001,FZ+0.06,FZ+1.90,0.006)
        A.fb((g,"LOCKER"),'-x',xf,ya+0.008,yb-0.008,FZ+0.09,FZ+1.87,0.018,0.004)                                # door
        for i in range(4): A.fb((g,"BLACK"),'-x',xf-0.018,ya+0.05,yb-0.05,FZ+1.60+i*0.045,FZ+1.63+i*0.045,0.002,0.0005)   # slits
        for i in range(3): A.fb((g,"BLACK"),'-x',xf-0.018,ya+0.05,yb-0.05,FZ+0.14+i*0.045,FZ+0.17+i*0.045,0.002,0.0005)
        A.fb((g,"STEEL_L"),'-x',xf-0.018,yb-0.06,yb-0.045,FZ+0.95,FZ+1.15,0.03,0.004)
        A.fb((g,"BRASS"),'-x',xf-0.018,ya+0.10,ya+0.18,FZ+1.48,FZ+1.53,0.002,0.0005); text(c.coll,f"{k+4:02d}",xf-0.021,ya+0.14,FZ+1.505,'-x',0.03,M["BLACK"],'CENTER',"CR locker no") if False else None
        A.prism((g,"BRASS"),(xf-0.018,yb-0.09,FZ+1.02),(xf-0.045,yb-0.09,FZ+1.02),0.013,0.011,14) if k!=1 else None      # padlocks
    A.hull((g,"LOCKER"),[(xf,y0,FZ+1.90),(xb,y0,FZ+1.90),(xf,y0+3*w,FZ+1.90),(xb,y0+3*w,FZ+1.90),(xf,y0,FZ+1.93),(xb,y0,FZ+1.98),(xf,y0+3*w,FZ+1.93),(xb,y0+3*w,FZ+1.98)],0.004)
    A.bx((g,"CARD"),xf+0.08,xf+0.36,y0+0.08,y0+0.55,FZ+1.98,FZ+2.18,0.004) if False else None
def break_corner(c):
    A,M=c.A,c.M; g="break"; yb=-11.91; xa,xz=0.15,1.02
    A.begin(-0.60,0.0,0.0,0.0)
    A.bx((g,"LOCKER"),xa,xz,yb,yb+0.55,FZ+0.08,FZ+0.86,0.006); A.bx((g,"BLACK"),xa+0.02,xz,yb,yb+0.52,FZ,FZ+0.08,0.003)
    for k in range(2): A.fb((g,"LOCKER"),'+y',yb+0.55,xa+0.02+k*0.42,xa+0.02+k*0.42+0.40,FZ+0.11,FZ+0.83,0.016,0.004); A.fb((g,"STEEL_L"),'+y',yb+0.571,xa+0.25+k*0.42,xa+0.29+k*0.42,FZ+0.62,FZ+0.76,0.02,0.004) if False else A.fb((g,"STEEL_L"),'+y',yb+0.566,xa+0.26+k*0.42-0.02,xa+0.26+k*0.42+0.02,FZ+0.62,FZ+0.76,0.018,0.004)
    A.bx((g,"STEEL_L"),xa-0.01,xz+0.01,yb,yb+0.58,FZ+0.86,FZ+0.89,0.004)                                          # steel worktop
    A.bx((g,"STEEL"),xa-0.01,xz+0.01,yb,yb+0.05,FZ+0.89,FZ+0.99,0.003)                                            # splashback
    fx0,fx1=1.06,1.52
    A.bx((g,"FRIDGE"),fx0,fx1,yb,yb+0.50,FZ,FZ+0.86,0.008); A.fb((g,"FRIDGE"),'+y',yb+0.50,fx0+0.005,fx1-0.005,FZ+0.03,FZ+0.86,0.012,0.004)
    A.fb((g,"BLACK"),'+y',yb+0.512,fx0+0.005,fx1-0.005,FZ+0.65,FZ+0.655,0.002,0.0005); A.fb((g,"STEEL_L"),'+y',yb+0.512,fx1-0.05,fx1-0.038,FZ+0.68,FZ+0.80,0.02,0.004); A.fb((g,"STEEL_L"),'+y',yb+0.512,fx1-0.05,fx1-0.038,FZ+0.30,FZ+0.58,0.02,0.004)
    A.fb((g,"CABLE"),'+y',yb+0.512,fx0+0.02,fx0+0.12,FZ+0.70,FZ+0.71,0.002,0.0) if False else None
    A.fb((g,"YELLOW"),'+y',yb+0.512,fx0+0.05,fx0+0.15,FZ+0.14,FZ+0.16,0.001,0.0)
    text(c.coll,"FROSTLINE",fx0+0.15,yb+0.5135,FZ+0.76,'+y',0.016,M["KEY_D"],'CENTER',"CR fridge brand") if False else None
    # microwave on the fridge
    A.bx((g,"BEIGE"),fx0+0.02,fx1-0.02,yb+0.04,yb+0.40,FZ+0.86,FZ+1.10,0.006); A.fb((g,"BLACK"),'+y',yb+0.40,fx0+0.04,fx1-0.13,FZ+0.89,FZ+1.07,0.004,0.002); A.fb((g,"BEIGE_D"),'+y',yb+0.40,fx1-0.115,fx1-0.03,FZ+0.89,FZ+1.07,0.004,0.002)
    for k in range(4): A.fb((g,"KEY_D"),'+y',yb+0.404,fx1-0.105,fx1-0.04,FZ+0.90+k*0.038,FZ+0.925+k*0.038,0.003,0.001)
    A.fb((g,"LED_AON"),'+y',yb+0.404,fx1-0.10,fx1-0.05,FZ+1.052,FZ+1.062,0.001,0.0)
    # kettle (stainless jug), mugs, tea tin, sugar jar
    kx,ky=0.40,yb+0.30; z0=FZ+0.89
    A.cyl((g,"BLACK"),kx,ky,z0,z0+0.02,0.09,24,0.003); A.prism((g,"STEEL_L"),(kx,ky,z0+0.02),(kx,ky,z0+0.20),0.078,0.062,24,0,True,0.004)
    A.prism((g,"BLACK"),(kx,ky,z0+0.20),(kx,ky,z0+0.225),0.045,0.038,16); A.bx((g,"BLACK"),kx+0.06,kx+0.10,ky-0.012,ky+0.012,z0+0.03,z0+0.19,0.006)
    A.bx((g,"LED_ON") if False else (g,"BLACK"),kx+0.05,kx+0.08,ky-0.02,ky+0.02,z0+0.06,z0+0.075,0.002)
    for i,(mx,my,mk) in enumerate(((0.62,yb+0.20,"PORC"),(0.74,yb+0.33,"PORC_O"),(0.28,yb+0.12,"PORC"))):
        A.prism((g,mk),(mx,my,z0),(mx,my,z0+0.095),0.038,0.042,20,0,True,0.002); A.bx((g,mk),mx+0.038,mx+0.062,my-0.006,my+0.006,z0+0.03,z0+0.075,0.003)
    A.prism((g,"YELLOW"),(0.86,yb+0.16,z0),(0.86,yb+0.16,z0+0.14),0.055,0.055,24,0,True,0.003); A.prism((g,"STEEL_L"),(0.86,yb+0.16,z0+0.14),(0.86,yb+0.16,z0+0.155),0.058,0.058,24)
    A.prism((g,"PORC"),(0.12,yb+0.13,z0),(0.12,yb+0.13,z0+0.10),0.04,0.04,20,0,True,0.002) if False else None
    A.cyl((g,"KEY_D"),0.94,yb+0.40,FZ,FZ+0.32,0.14,24,0.004) if False else None
    A.bx((g,"CABLE"),0.34,0.46,yb+0.34,yb+0.42,z0,z0+0.004,0.0) if False else None
    A.tube((g,"CABLE_B"),[(kx+0.08,ky-0.01,z0+0.03),(kx+0.15,yb+0.20,z0+0.005),(kx+0.20,yb+0.08,z0+0.07),(kx+0.20,yb+0.03,z0+0.12)],0.0035,8)
    # wall shelf with tins above + wall clock
    A.bx((g,"STEEL"),xa,xz,yb,yb+0.20,FZ+1.55,FZ+1.575,0.003)
    for k,(tx,mk) in enumerate(((0.28,"ORANGE"),(0.40,"YELLOW"),(0.52,"RED"),(0.68,"STEEL_L"))):
        A.prism((g,mk),(tx,yb+0.10,FZ+1.575),(tx,yb+0.10,FZ+1.575+0.12+0.02*(k%2)),0.045,0.045,20,0,True,0.002)
    A.bx((g,"CARD"),0.80,0.98,yb+0.03,yb+0.18,FZ+1.575,FZ+1.70,0.004)
    A.cyl((g,"BLACK"),0,0,0,0,0,3) if False else None
    A.prism((g,"BEIGE_D"),(xa+0.35,yb+0.03,FZ+2.30),(xa+0.35,yb+0.055,FZ+2.30),0.17,0.17,32,0,True,0.004); A.prism((g,"PAPER"),(xa+0.35,yb+0.055,FZ+2.30),(xa+0.35,yb+0.058,FZ+2.30),0.148,0.148,32,0,True)
    for k in range(12):
        a=k*math.pi/6; A.prism((g,"BLACK"),(xa+0.35+math.sin(a)*0.125,yb+0.058,FZ+2.30+math.cos(a)*0.125),(xa+0.35+math.sin(a)*0.138,yb+0.059,FZ+2.30+math.cos(a)*0.138),0.003,0.003,6)
    A.prism((g,"BLACK"),(xa+0.35,yb+0.058,FZ+2.30),(xa+0.35+0.0,yb+0.06,FZ+2.30+0.10),0.004,0.002,6); A.prism((g,"BLACK"),(xa+0.35,yb+0.058,FZ+2.30),(xa+0.35+0.075,yb+0.06,FZ+2.30-0.02),0.004,0.002,6)
    A.end()
    A.cyl((g,"STEEL"),1.78,-6.95,FZ,FZ+0.30,0.13,24,0.004)    # waste bin at the desk end
def worktable(c):
    A,M=c.A,c.M; g="wtable"; x0,x1,y0,y1=-3.40,-1.80,-10.30,-9.50; zt=FZ+0.79
    A.bx((g,"WOOD"),x0,x1,y0,y1,zt-0.04,zt,0.004); A.bx((g,"EDGE"),x0,x1,y0-0.003,y0,zt-0.04,zt,0.0015); A.bx((g,"EDGE"),x0,x1,y1,y1+0.003,zt-0.04,zt,0.0015)
    for (xa,xb) in ((x0+0.06,x0+0.10),(x1-0.10,x1-0.06)):
        for (ya,yb2) in ((y0+0.05,y0+0.09),(y1-0.09,y1-0.05)): A.bx((g,"STEEL"),xa,xb,ya,yb2,FZ+0.02,zt-0.04,0.003); A.cyl((g,"BLACK"),(xa+xb)/2,(ya+yb2)/2,FZ,FZ+0.02,0.02,12)
    A.bx((g,"STEEL"),x0+0.10,x1-0.10,y0+0.05,y0+0.09,zt-0.09,zt-0.04,0.003); A.bx((g,"STEEL"),x0+0.10,x1-0.10,y1-0.09,y1-0.05,zt-0.09,zt-0.04,0.003)
    A.bx((g,"STEEL"),x0+0.06,x1-0.06,(y0+y1)/2-0.02,(y0+y1)/2+0.02,FZ+0.18,FZ+0.21,0.003)
    # site map + plans
    A.plane((g,"N_log"),(x0+0.20,y0+0.10,zt+0.001),(x0+0.62,y0+0.10,zt+0.001),(x0+0.62,y0+0.70,zt+0.001),(x0+0.20,y0+0.70,zt+0.001))
    A.bx((g,"PAPER"),x0+0.62,x0+1.30,y0+0.14,y0+0.66,zt,zt+0.002,0.0)
    for k in range(6): A.bx((g,"BLACK"),x0+0.66,x0+0.66+0.10+((k*37)%5)*0.09,y0+0.20+k*0.07,y0+0.204+k*0.07,zt+0.002,zt+0.0028,0.0)
    for k,(rx,ry) in enumerate(((x1-0.30,y1-0.22),(x1-0.20,y1-0.28))): A.cylx((g,"PAPER"),rx-0.32,rx+0.0,ry,zt+0.032,0.032,20); A.cylx((g,"RED" if k else "YELLOW"),rx-0.322,rx-0.30,ry,zt+0.032,0.033,20)   # rolled drawings
    A.bx((g,"ORANGE"),x0+1.35,x0+1.52,y0+0.15,y0+0.32,zt,zt+0.10,0.006); A.bx((g,"STEEL_L"),x0+1.42,x0+1.45,y0+0.14,y0+0.16,zt+0.07,zt+0.09,0.002)            # toolbox
    A.prism((g,"PORC_O"),(x1-0.10,y0+0.16,zt),(x1-0.10,y0+0.16,zt+0.095),0.038,0.042,20,0,True,0.002)
    A.bx((g,"BLACK"),x0+0.12,x0+0.32,y1-0.30,y1-0.10,zt,zt+0.012,0.004); A.bx((g,"PAPER"),x0+0.14,x0+0.30,y1-0.28,y1-0.12,zt+0.012,zt+0.014,0.0); A.bx((g,"STEEL_L"),x0+0.19,x0+0.25,y1-0.115,y1-0.10,zt+0.012,zt+0.03,0.002)   # clipboard
    # articulated work lamp
    lx,ly=x1-0.12,y1-0.12
    A.cyl((g,"BLACK"),lx,ly,zt,zt+0.03,0.07,24,0.004); A.prism((g,"STEEL"),(lx,ly,zt+0.03),(lx-0.10,ly-0.10,zt+0.36),0.008,0.008,8); A.prism((g,"STEEL"),(lx-0.10,ly-0.10,zt+0.36),(lx-0.30,ly-0.20,zt+0.42),0.008,0.008,8)
    A.prism((g,"OLIVE") if False else (g,"LOCKER"),(lx-0.30,ly-0.20,zt+0.44),(lx-0.34,ly-0.22,zt+0.30),0.045,0.10,24,0,True,0.003); A.prism((g,"BULB"),(lx-0.325,ly-0.215,zt+0.30),(lx-0.335,ly-0.22,zt+0.28),0.035,0.035,14,0,True)
    c.WORKLAMP=(lx-0.335,ly-0.22,zt+0.27)
    # pendant over the table
    px,py=(x0+x1)/2,(y0+y1)/2
    A.cyl((g,"BLACK"),px,py,8.50,8.53,0.04,16); A.prism((g,"CABLE"),(px,py,8.50),(px,py,7.74),0.006,0.006,8)
    A.prism((g,"SHADE"),(px,py,7.74),(px,py,7.52),0.045,0.24,32,0,True,0.004); A.prism((g,"LAMPFACE"),(px,py,7.531),(px,py,7.527),0.225,0.225,32,0,True)   # matte enamel shade, emissive diffuser (was a bumpy paper disc that sparkled)
    A.prism((g,"BULB"),(px,py,7.68),(px,py,7.58),0.04,0.06,16); c.PENDANT=(px,py,7.52)
def credenza(c):
    A,M=c.A,c.M; g="cred"; x0,x1=-2.35,-0.65; yb=-11.91; d=0.46; zt=FZ+0.86
    A.bx((g,"LOCKER"),x0,x1,yb,yb+d,FZ+0.08,zt-0.03,0.006); A.bx((g,"BLACK"),x0+0.03,x1-0.03,yb,yb+d-0.03,FZ,FZ+0.08,0.003)
    for k in range(3):
        xa=x0+0.02+k*(x1-x0-0.04)/3; xb=xa+(x1-x0-0.04)/3-0.004
        A.fb((g,"LOCKER"),'+y',yb+d,xa,xb,FZ+0.10,zt-0.05,0.016,0.004); A.fb((g,"STEEL_L"),'+y',yb+d+0.016,(xa+xb)/2-0.06,(xa+xb)/2+0.06,zt-0.12,zt-0.105,0.018,0.004)
    A.bx((g,"WOOD"),x0-0.02,x1+0.02,yb,yb+d+0.02,zt-0.03,zt,0.004); A.bx((g,"EDGE"),x0-0.02,x1+0.02,yb+d+0.02,yb+d+0.023,zt-0.03,zt,0.0015)
    # VCR + VHS tapes + remote
    vx,vy=-1.55,yb+0.14
    A.bx((g,"BLACK"),vx-0.215,vx+0.215,vy-0.11,vy+0.12,zt,zt+0.085,0.006); A.fb((g,"GREY"),'+y',vy+0.12,vx-0.20,vx+0.20,zt+0.006,zt+0.079,0.004,0.002)
    A.fb((g,"BLACK"),'+y',vy+0.124,vx-0.19,vx+0.02,zt+0.030,zt+0.060,0.003,0.001); A.fb((g,"LED_AON"),'+y',vy+0.127,vx+0.05,vx+0.13,zt+0.048,zt+0.060,0.002,0.0)
    for k in range(5): A.fb((g,"KEY_D"),'+y',vy+0.124,vx+0.06+k*0.026,vx+0.079+k*0.026,zt+0.018,zt+0.032,0.004,0.001)
    text(c.coll,"TAKAMI  VX-200",vx-0.19,vy+0.1265,zt+0.070,'+y',0.010,M["KEY"],'LEFT',"CR vcr brand")
    A.bx((g,"BLACK"),vx-0.20,vx+0.06,vy-0.10,vy+0.10,zt+0.085,zt+0.10,0.002) if False else None
    for k in range(3):
        A.bx((g,"BLACK"),-2.28+k*0.0,-2.28+0.19,yb+0.10,yb+0.19-0.0,zt+k*0.026,zt+(k+1)*0.026-0.001,0.002) if False else A.bx((g,"BLACK"),-2.28,-2.09,yb+0.10,yb+0.29,zt+k*0.026,zt+(k+1)*0.026-0.001,0.002)
        A.fb((g,"PAPER"),'+y',yb+0.29,-2.26,-2.12,zt+k*0.026+0.006,zt+k*0.026+0.018,0.0015,0.0)
    A.bx((g,"BLACK"),-1.10,-1.03,yb+0.22,yb+0.42,zt,zt+0.02,0.004)
    # dead plant
    A.prism((g,"PORC_O"),(-0.86,yb+0.15,zt),(-0.86,yb+0.15,zt+0.16),0.06,0.075,24,0,True,0.003); A.prism((g,"SOIL"),(-0.86,yb+0.15,zt+0.16),(-0.86,yb+0.15,zt+0.164),0.062,0.062,24)
    rr=c.R
    for k in range(7):
        a=k*0.9; ex=math.cos(a)*(0.05+rr.random()*0.09); ey=math.sin(a)*(0.05+rr.random()*0.09)
        A.prism((g,"LEAF"),(-0.86,yb+0.15,zt+0.164),(-0.86+ex,yb+0.15+ey,zt+0.20+rr.random()*0.14),0.004,0.002,5)
        A.hull((g,"LEAF"),[(-0.86+ex,yb+0.15+ey,zt+0.22),(-0.86+ex*1.3,yb+0.15+ey*1.3,zt+0.19),(-0.86+ex+0.02,yb+0.15+ey,zt+0.21),(-0.86+ex*1.2,yb+0.15+ey*1.2+0.02,zt+0.20)],0.0) if False else None
