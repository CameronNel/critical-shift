"""Anteroom dressing and lift interior (owner brief 2026-10-01, second pass).  Called from cr_lift.build.
Anteroom (interior x -6.83..-4.83, y -7.70..-5.70, floor z 5.4): water cooler with a labelled 19 l jug and cups, loveseat with throw cushion and folded blanket,
small coffee table (magazine, remote, bowl of sweets, paper cup), bedside table (lamp, wireless charger with cable to a wall socket, coaster with a coffee cup, paperback,
keys, pill bottle), small potted plant, dark red worn Persian rug.  Lift: G / F1 button lamps and floor-indicator lamps that light for the ACTIVE floor, a flickering cabin
light and car lamp, a dome security camera with a blinking red LED, an expired inspection certificate, a capacity plate, and an analogue floor-position dial whose needle
swings with the car.  Everything that moves or lights up is driven by the CR_LIFT car height (seconds-based schedule), never by frames."""
import bpy,math
import numpy as np
import crk,crt
from crk import pm,drv,decal_mat,tex_mat,emit_mat,new_image
FZ=5.40
def persian_rug(W=512,H=340,seed=11):
    """dark red, worn Persian rug: medallion, spandrels, sawtooth border, ochre lattice, faded foot-path, threadbare patches, a stain, alpha fringe at both ends"""
    rng=np.random.default_rng(seed); X,Y=crt.XY(W,H); fm=34; bx=X-fm; Wb=W-2*fm; by=Y
    inb=((X>=fm)&(X<W-fm)).astype(np.float32)
    C=dict(red=(0.20,0.022,0.026),red2=(0.15,0.018,0.020),cream=(0.60,0.50,0.34),ochre=(0.52,0.32,0.07),olive=(0.17,0.19,0.07),char=(0.055,0.045,0.045))
    a=np.zeros((H,W,3),np.float32); a[...]=C["red"]
    px=(bx%34)-17; py=(by%34)-17; d=np.abs(px)+np.abs(py)
    crt.over(a,(d<7).astype(np.float32),C["ochre"],0.9); crt.over(a,(d<3).astype(np.float32),C["char"])
    cx,cy=Wb/2,H/2; dd=np.abs(bx-cx)/1.55+np.abs(by-cy)
    for r,col in ((118,C["char"]),(110,C["cream"]),(100,C["red2"]),(78,C["olive"]),(70,C["ochre"]),(52,C["red2"]),(26,C["cream"]),(12,C["char"])): crt.over(a,(dd<r).astype(np.float32),col)
    for (sx,sy) in ((0,0),(Wb,0),(0,H),(Wb,H)):
        dq=np.abs(bx-sx)/1.55+np.abs(by-sy); crt.over(a,((dq<88)&(dq>80)).astype(np.float32),C["cream"]); crt.over(a,((dq<76)&(dq>64)).astype(np.float32),C["ochre"],0.8)
    e=np.minimum(np.minimum(bx,Wb-bx),np.minimum(by,H-by))
    crt.over(a,(e<14).astype(np.float32),C["char"]); crt.over(a,((e>=14)&(e<19)).astype(np.float32),C["cream"])
    band=(e>=19)&(e<54); crt.over(a,band.astype(np.float32),C["red2"])
    t=np.where(np.minimum(bx,Wb-bx)<np.minimum(by,H-by),by,bx); zz=np.abs((t%32)-16)
    crt.over(a,(band&(zz<(e-19)*0.5)).astype(np.float32),C["ochre"]); crt.over(a,(band&(zz<(e-19)*0.22)).astype(np.float32),C["cream"],0.8)
    crt.over(a,((e>=54)&(e<59)).astype(np.float32),C["cream"]); crt.over(a,((e>=59)&(e<63)).astype(np.float32),C["char"])
    n1=crt.smooth_noise(H,W,48,rng); n2=crt.smooth_noise(H,W,20,rng); n3=crt.smooth_noise(H,W,9,rng)
    path=np.exp(-((Y-H*0.52)/(H*0.14))**2)*0.55; edge=np.clip(1-e/30,0,1)
    wear=np.clip(np.clip((n1*0.6+n2*0.4-0.45)*3.0,0,1)*0.7+path*0.5+edge*0.55,0,1)
    gray=a.mean(2,keepdims=True); a=a*(1-0.55*wear[...,None])+(gray*1.4+0.05)*0.55*wear[...,None]                     # faded, pink-grey where worn
    tb=np.clip((n1*0.5+n3*0.5-0.64)*7,0,1)*(wear>0.45); a=a*(1-tb[...,None])+np.array((0.30,0.24,0.17),np.float32)*tb[...,None]   # threadbare foundation
    a*=(1+0.04*(np.sin(Y*1.9)*0.5+np.sin(X*2.1)*0.5))[...,None]
    st=np.clip(1-np.hypot(X-0.72*W,Y-0.36*H)/38,0,1); a*=(1-0.45*st**0.6)[...,None]                                       # coffee stain
    al=inb.copy()
    fr=((X<fm)|(X>=W-fm))&(Y>6)&(Y<H-6)&((Y%5)<2.3); fx=np.where(X<fm,fm-X,X-(W-fm))/fm; fr=fr&(fx<0.85+0.15*rng.random((H,W)))
    fc=np.array((0.55,0.48,0.36),np.float32)*(0.75+0.25*n3[...,None]); a=np.where(fr[...,None],fc,a); al=np.maximum(al,fr.astype(np.float32))
    return np.concatenate([np.clip(a,0,1),al[...,None]],2).astype(np.float32)
def magazine_cover(W=168,H=224):
    X,Y=crt.XY(W,H); a=crt.canvas(W,H,(0.80,0.62,0.12)); crt.over(a,crt.m_rect(X,Y,0,0,W,58),(0.58,0.07,0.05))
    crt.put_text(a,"GRID",W/2-26,22,30,(0.92,0.86,0.70)); crt.put_text(a,"& WIRE",W/2+30,24,20,(0.92,0.86,0.70))
    crt.over(a,crt.m_circle(X,Y,W/2,132,48),(0.12,0.13,0.12)); crt.over(a,crt.m_tri(X,Y,(W/2-26,176),(W/2+26,176),(W/2,96)),(0.80,0.62,0.12)); crt.over(a,crt.m_rect(X,Y,W/2-3,126,W/2+3,176),(0.12,0.13,0.12))
    for k in range(3): crt.over(a,crt.m_line(X,Y,W/2-34,118+k*12,W/2+34,118+k*12,2),(0.12,0.13,0.12))
    crt.put_text(a,"THE LIGHTS STAY ON:\nINSIDE THE NIGHT SHIFT",W/2,196,10.5,(0.12,0.13,0.12),line=1.05); crt.put_text(a,"ISSUE 04   $1.50",W/2,215,8,(0.30,0.12,0.06))
    return a
def _drive(m,expr,extra): drv(m.node_tree,'nodes["Principled BSDF"].inputs["Emission Strength"].default_value',None,expr,var_s=False,extra=extra)
def lamp_mats(c,ctl):
    zv=[("z",ctl,'["car_z"]')]; M=c.M
    M["LAMP_G"]=emit_mat("CR lift lamp G",(1.0,0.62,0.12),4.0); _drive(M["LAMP_G"],"4.0*max(0,1-z/0.6)",zv)
    M["LAMP_F1"]=emit_mat("CR lift lamp F1",(1.0,0.62,0.12),4.0); _drive(M["LAMP_F1"],"4.0*min(1,max(0,(z-4.8)/0.6))",zv)
    M["LAMP_MOVE"]=emit_mat("CR lift lamp moving",(1.0,0.30,0.05),3.0); _drive(M["LAMP_MOVE"],"3.0*(1 if z>0.15 and z<5.25 else 0)",zv)
    M["CAB_LIGHT"]=emit_mat("CR lift cabin light",(1.0,0.74,0.46),9.0); _drive(M["CAB_LIGHT"],"9.0*(1-0.85*max(0,sin(T*47)*sin(T*11.3+1)-0.30)*1.6)*(1-0.7*bw)",[])
    M["CAM_LED"]=emit_mat("CR lift camera led",(1.0,0.05,0.03),4.0); _drive(M["CAM_LED"],"4.0*(1 if fmod(T,2.4)<0.18 else 0)",[])
    M["LAMP_SHADE"]=emit_mat("CR lamp shade glow",(1.0,0.70,0.40),2.4)
    M["COFFEE"]=pm("CR coffee",(0.03,0.016,0.008),0.12,bump=0.0,scale=2.0)
    M["BOOK"]=pm("CR book cover",(0.045,0.085,0.06),0.6,scale=3.0,bump=0.04)
    M["PILL"]=pm("CR pill bottle",(0.38,0.14,0.02),0.18,bump=0.0,scale=2.0,coat=0.3)
    M["RUG"]=decal_mat("CR rug persian",new_image("CR rug persian tex",persian_rug()),0.95)
    M["MAG"]=tex_mat("CR notice magazine cover",new_image("CR magazine cover tex",magazine_cover()),rough=0.35)
    M["LCERT"]=tex_mat("CR notice lift certificate",new_image("CR lift cert tex",crt.notice("safety",seed=77)),rough=0.8)
def _rot(cx,cy,dx,dy,ang): ca,sa=math.cos(ang),math.sin(ang); return (cx+dx*ca-dy*sa,cy+dx*sa+dy*ca)
def indicators(c,ctl):
    """floor-indicator lamps (G | moving | F1) over the lift door in the anteroom and beside the ground door in the hall"""
    A=c.A; M=c.M; g="ante"
    A.fb((g,"BLACK"),'+x',-6.83,-6.66,-6.14,7.78,8.04,0.024,0.004)
    for (y0,key,lab) in ((-6.60,"LAMP_G","G"),(-6.43,"LAMP_MOVE",None),(-6.26,"LAMP_F1","1")):
        A.fb((g,key),'+x',-6.83+0.024,y0,y0+0.10 if lab else y0+0.10,7.90,8.00,0.004,0.0)
        if lab: crk.text(c.coll,lab,-6.83+0.0285,y0+0.05,7.835,'+x',0.05,M["YELLOW"],'CENTER',"CR lift floor label")
    gh="lift"; wy=-5.28
    A.fb((gh,"BLACK"),'+y',wy,-7.30,-6.86,2.46,2.74,0.024,0.004)
    for (x0,key,lab) in ((-7.25,"LAMP_G","G"),(-7.14,"LAMP_MOVE",None),(-7.03,"LAMP_F1","1")):
        A.fb((gh,key),'+y',wy+0.024,x0,x0+0.08,2.60,2.69,0.004,0.0)
        if lab: crk.text(c.coll,lab,x0+0.04,wy+0.0285,2.515,'+y',0.045,M["YELLOW"],'CENTER',"CR lift floor label")
def props(c):
    A,M=c.A,c.M; g="anteprop"
    # everything that hugs the south (back) wall is built in a shifted frame: the back wall was pushed 1.25 m south
    DY=-1.25; A.begin(0,DY,0,0)
    # ---------------- dark red worn Persian rug (alpha fringe in the texture)
    A.plane((g,"RUG"),(-6.76,-6.98,FZ+0.005),(-5.28,-6.98,FZ+0.005),(-5.28,-6.00,FZ+0.005),(-6.76,-6.00,FZ+0.005))
    A.end()
    # ---------------- water cooler on the north wall (label, cups, drip tray, taps)
    cx0,cx1,cy0,cy1=-5.62,-5.28,-6.08,-5.70; jx,jy=(cx0+cx1)/2,(cy0+cy1)/2
    A.bx((g,"PORC"),cx0,cx1,cy0,cy1,FZ+0.05,FZ+1.15,0.012); A.bx((g,"BLACK"),cx0+0.02,cx1-0.02,cy0+0.01,cy1-0.02,FZ,FZ+0.05,0.004)
    A.bx((g,"PORC_O"),cx0-0.003,cx1+0.003,cy0-0.004,cy0+0.012,FZ+1.00,FZ+1.15,0.004)
    A.bx((g,"GREY"),cx0+0.04,cx1-0.04,cy0-0.045,cy0+0.004,FZ+0.52,FZ+0.57,0.005); A.bx((g,"BLACK"),cx0+0.05,cx1-0.05,cy0-0.004,cy0+0.004,FZ+0.58,FZ+0.84,0.003)
    A.bx((g,"JUG"),cx0+0.08,cx0+0.14,cy0-0.022,cy0-0.004,FZ+0.74,FZ+0.79,0.004); A.bx((g,"RED"),cx1-0.14,cx1-0.08,cy0-0.022,cy0-0.004,FZ+0.74,FZ+0.79,0.004)
    A.cyl((g,"JUG"),jx,jy,FZ+1.15,FZ+1.60,0.135,28,0.006); A.cyl((g,"JUG"),jx,jy,FZ+1.60,FZ+1.67,0.060,18,0.004); A.cyl((g,"PORC"),jx,jy,FZ+1.67,FZ+1.70,0.075,18,0.003)
    A.cyl((g,"PAPER"),jx,jy,FZ+1.28,FZ+1.48,0.1365,28)                                                   # white label band
    crk.text(c.coll,"FAMILY CO.\nSPRING WATER",jx,jy-0.1385,FZ+1.38,'-y',0.023,M["BLACK"],'CENTER',"CR jug label",spacing=1.0)
    A.cyl((g,"PORC"),cx1+0.045,cy1-0.075,FZ+0.55,FZ+1.05,0.035,16,0.003)
    for k in range(4): A.cyl((g,"PORC_O"),cx1+0.045,cy1-0.075,FZ+0.55+k*0.12,FZ+0.58+k*0.12,0.032,16,0.0)
    A.begin(0,DY,0,0)
    # ---------------- loveseat on the south wall
    sx0,sx1,sy0,sy1=-6.72,-5.62,-7.70,-7.00
    A.bx((g,"BLACK"),sx0,sx1,sy0+0.02,sy1-0.02,FZ+0.09,FZ+0.30,0.012)
    for xa,xb in ((sx0+0.10,(sx0+sx1)/2-0.005),((sx0+sx1)/2+0.005,sx1-0.10)): A.bx((g,"FABRIC"),xa,xb,sy0+0.17,sy1-0.03,FZ+0.30,FZ+0.46,0.03)
    A.bx((g,"FABRIC"),sx0+0.10,sx1-0.10,sy0+0.03,sy0+0.25,FZ+0.46,FZ+0.90,0.04)
    for xa,xb in ((sx0,sx0+0.10),(sx1-0.10,sx1)): A.bx((g,"FABRIC"),xa,xb,sy0+0.03,sy1-0.03,FZ+0.30,FZ+0.64,0.03)
    for (x,y) in ((sx0+0.06,sy0+0.06),(sx1-0.06,sy0+0.06),(sx0+0.06,sy1-0.06),(sx1-0.06,sy1-0.06)): A.cyl((g,"BLACK"),x,y,FZ,FZ+0.09,0.022,10)
    A.bx((g,"FABRIC_O"),sx0+0.14,sx0+0.46,sy0+0.25,sy0+0.33,FZ+0.46,FZ+0.78,0.02)                         # orange throw cushion
    A.bx((g,"BLANKET"),sx1-0.10,sx1+0.0,sy0+0.05,sy1-0.04,FZ+0.64,FZ+0.665,0.012); A.bx((g,"BLANKET"),sx1-0.10,sx1-0.02,sy1-0.20,sy1-0.04,FZ+0.46,FZ+0.64,0.01)   # folded blanket over the right arm
    # ---------------- coffee table with things on it
    tx0,tx1,ty0,ty1=-6.45,-5.90,-6.88,-6.58; tz=FZ+0.38
    A.bx((g,"WOOD"),tx0,tx1,ty0,ty1,tz-0.025,tz,0.004); A.bx((g,"WOOD"),tx0+0.03,tx1-0.03,ty0+0.03,ty1-0.03,FZ+0.10,FZ+0.115,0.003)
    for (x,y) in ((tx0+0.02,ty0+0.02),(tx1-0.02,ty0+0.02),(tx0+0.02,ty1-0.02),(tx1-0.02,ty1-0.02)): A.bx((g,"BLACK"),x-0.012,x+0.012,y-0.012,y+0.012,FZ,tz-0.025,0.002)
    mx,my,ma=-6.31,-6.76,0.18; hw,hh=0.14,0.105                                                         # magazine
    A.box((g,"PAPER"),mx,my,tz,tz+0.006,2*hw,2*hh,ma,0.0008)
    pts=[_rot(mx,my,dx,dy,ma) for (dx,dy) in ((-hw,-hh),(hw,-hh),(hw,hh),(-hw,hh))]
    A.plane((g,"MAG"),*[(p[0],p[1],tz+0.0063) for p in pts])
    A.box((g,"BLACK"),-6.10,-6.63,tz,tz+0.014,0.15,0.042,-0.25,0.004); A.box((g,"GREY"),-6.11,-6.627,tz+0.014,tz+0.0155,0.10,0.026,-0.25,0.0)     # remote
    A.cyl((g,"PORC"),-5.99,-6.80,tz,tz+0.012,0.040,16,0.003); A.prism((g,"PORC"),(-5.99,-6.80,tz+0.012),(-5.99,-6.80,tz+0.05),0.038,0.058,18,0.0,False,0.0)   # bowl
    for (dx,dy,key) in ((-0.012,0.008,"RED"),(0.014,-0.006,"YELLOW"),(0.0,0.018,"ORANGE"),(-0.02,-0.014,"RED")): A.cyl((g,key),-5.99+dx,-6.80+dy,tz+0.012,tz+0.026,0.010,8)   # sweets
    A.cyl((g,"PAPER"),-6.00,-6.65,tz,tz+0.075,0.028,14)                                                 # paper cup
    # ---------------- bedside table: lamp, charger + cable, coaster + cup, paperback, keys, pills
    bx0,bx1,by0,by1=-5.56,-5.22,-7.70,-7.34; bz=FZ+0.525
    A.bx((g,"WOOD"),bx0,bx1,by0,by1,bz-0.025,bz,0.004); A.bx((g,"WOOD"),bx0+0.01,bx1-0.01,by0+0.01,by1-0.01,FZ+0.30,FZ+0.50,0.004); A.bx((g,"WOOD"),bx0+0.015,bx1-0.015,by0+0.015,by1-0.015,FZ+0.12,FZ+0.135,0.003)
    for (x,y) in ((bx0+0.02,by0+0.02),(bx1-0.02,by0+0.02),(bx0+0.02,by1-0.02),(bx1-0.02,by1-0.02)): A.bx((g,"BLACK"),x-0.014,x+0.014,y-0.014,y+0.014,FZ,FZ+0.50,0.002)
    A.fb((g,"WOOD"),'+y',by1-0.012,bx0+0.012,bx1-0.012,FZ+0.31,FZ+0.49,0.012,0.003); A.cyly((g,"BRASS"),(bx0+bx1)/2,by1,by1+0.016,FZ+0.40,0.011,12)
    lx,ly=-5.47,-7.61                                                                                   # table lamp
    A.cyl((g,"BRASS"),lx,ly,bz,bz+0.015,0.032,16); A.cyl((g,"BRASS"),lx,ly,bz+0.015,bz+0.13,0.007,10); A.prism((g,"LAMP_SHADE"),(lx,ly,bz+0.11),(lx,ly,bz+0.22),0.085,0.052,20,0.0,True,0.0)
    crk.light(c.coll,"CR bedside lamp",(lx,ly+DY,bz+0.17),(1.0,0.70,0.38),5,'POINT',soft=0.04)
    qx,qy=-5.30,-7.62                                                                                   # wireless charger + cable to the wall socket
    A.cyl((g,"BLACK"),qx,qy,bz,bz+0.009,0.045,22,0.002); A.cyl((g,"LED_ON"),qx,qy+0.040,bz+0.009,bz+0.0115,0.004,8)
    A.tube((g,"CABLE_B"),[(qx,qy-0.04,bz+0.004),(qx,by0+0.005,bz+0.004),(qx,by0+0.005,FZ+0.36)],0.0028,6)
    A.fb((g,"PORC"),'+y',by0,qx-0.04,qx+0.04,FZ+0.30,FZ+0.37,0.008,0.002); A.bx((g,"BLACK"),qx-0.012,qx+0.012,by0+0.008,by0+0.013,FZ+0.318,FZ+0.332,0.001); A.bx((g,"BLACK"),qx-0.012,qx+0.012,by0+0.008,by0+0.013,FZ+0.338,FZ+0.352,0.001)
    kx,ky=-5.285,-7.455                                                                                 # coaster with a coffee cup
    A.cyl((g,"CORK"),kx,ky,bz,bz+0.004,0.043,20); A.cyl((g,"PORC_O"),kx,ky,bz+0.004,bz+0.088,0.036,20,0.003); A.cyl((g,"COFFEE"),kx,ky,bz+0.082,bz+0.0855,0.031,20)
    A.tube((g,"PORC_O"),[(kx+0.034,ky,bz+0.07),(kx+0.058,ky,bz+0.068),(kx+0.058,ky,bz+0.034),(kx+0.034,ky,bz+0.024)],0.006,6)
    A.box((g,"PAPER"),-5.465,-7.455,bz,bz+0.026,0.10,0.155,0.2,0.0015); A.box((g,"BOOK"),-5.465,-7.455,bz+0.0,bz+0.003,0.103,0.158,0.2,0.0008); A.box((g,"BOOK"),-5.465,-7.455,bz+0.023,bz+0.026,0.103,0.158,0.2,0.0008)   # paperback
    A.tube((g,"BRASS"),[(-5.395+0.014*math.cos(t),-7.40+0.014*math.sin(t),bz+0.003) for t in np.linspace(0,2*math.pi,11)],0.0022,5)                                 # keys
    A.box((g,"BRASS"),-5.365,-7.385,bz,bz+0.004,0.05,0.012,0.7,0.001); A.box((g,"STEEL_L"),-5.405,-7.375,bz,bz+0.004,0.045,0.012,-0.5,0.001)
    A.cyl((g,"PILL"),-5.385,-7.575,bz,bz+0.058,0.016,12,0.002); A.cyl((g,"PORC"),-5.385,-7.575,bz+0.058,bz+0.07,0.0175,12)
    A.end()
    # ---------------- small potted plant in the north-west corner
    px,py,s=-6.60,-5.93,0.62
    A.prism((g,"TERRA"),(px,py,FZ),(px,py,FZ+0.30),0.095,0.135,20,0.0,True,0.003); A.cyl((g,"SOIL"),px,py,FZ+0.30,FZ+0.32,0.12,18)
    for k in range(8):
        a=k*2*math.pi/8+0.3; ca,sa=math.cos(a),math.sin(a); nx,ny=-sa,ca; h=(0.34+0.18*((k*7)%3)/2)
        top=(px+0.13*s*ca,py+0.13*s*sa,FZ+0.32+h)
        A.tube((g,"PLANT"),[(px+0.015*ca,py+0.015*sa,FZ+0.32),(px+0.06*s*ca,py+0.06*s*sa,FZ+0.32+h*0.6),top],0.0045,6)
        L=0.22; d=(0.80*ca,0.80*sa,0.35); k1=0.15*L*1.2; k2=0.5*L*1.2
        pts=[top,(top[0]+k1*d[0]+0.02*nx,top[1]+k1*d[1]+0.02*ny,top[2]+0.15*L*d[2]),(top[0]+k1*d[0]-0.02*nx,top[1]+k1*d[1]-0.02*ny,top[2]+0.15*L*d[2]),
             (top[0]+k2*d[0]+0.058*nx,top[1]+k2*d[1]+0.058*ny,top[2]+0.5*L*d[2]+0.008),(top[0]+k2*d[0]-0.058*nx,top[1]+k2*d[1]-0.058*ny,top[2]+0.5*L*d[2]+0.008),
             (top[0]+L*d[0]*1.2,top[1]+L*d[1]*1.2,top[2]+L*d[2]-0.04)]
        A.hull((g,"PLANT"),pts,0.0015)
def car_interior(c,ctl,car,zv,_mover):
    """everything inside the car that moves with it: control panel with G / F1 lamp buttons, analogue floor dial, security camera, certificate, capacity plate, car lamp"""
    M=c.M; coll=c.coll
    def fn(K):
        g="lift_car"
        K.fb((g,"STEEL"),'+y',-7.08,-7.56,-7.28,0.90,1.60,0.014,0.004); K.fb((g,"BLACK"),'+y',-7.08,-7.545,-7.295,0.915,1.585,0.018,0.003)               # control panel
        for (z,key) in ((1.40,"LAMP_G"),(1.28,"LAMP_F1")):
            K.cyly((g,"STEEL_L"),-7.42,-7.062,-7.052,z,0.024,18,0.002); K.cyly((g,key),-7.42,-7.052,-7.047,z,0.017,18)
        K.cyly((g,"STEEL_L"),-7.42,-7.062,-7.054,1.14,0.020,16,0.002); K.cyly((g,"RED"),-7.42,-7.054,-7.049,1.14,0.014,14)                                       # alarm
        for k in range(5): K.bx((g,"STEEL"),-7.52,-7.32,-7.062,-7.056,0.945+k*0.018,0.953+k*0.018,0.001)                                                         # intercom grille
        cx,cz=-7.75,1.92                                                                                                                                            # analogue floor dial
        K.cyly((g,"STEEL_L"),cx,-7.08,-7.064,cz,0.125,30,0.003); K.cyly((g,"BLACK"),cx,-7.064,-7.058,cz,0.108,30)
        for k in range(9):
            th=math.radians(-57+k*14.25); r0,r1=0.074,0.098 if k in (0,4,8) else 0.090
            K.tube((g,"PAPER"),[(cx+math.sin(th)*r0,-7.0585,cz+math.cos(th)*r0),(cx+math.sin(th)*r1,-7.0585,cz+math.cos(th)*r1)],0.0028,4)
        K.cyly((g,"STEEL_L"),cx,-7.058,-7.050,cz,0.012,10)
        # security dome camera in the south-west ceiling corner, red LED beside it
        dx,dy=-8.50,-6.95
        K.cyl((g,"STEEL_L"),dx,dy,2.378,2.40,0.070,22,0.003); K.cyl((g,"BLACK"),dx,dy,2.350,2.378,0.058,22,0.003); K.cyl((g,"BLACK"),dx,dy,2.322,2.350,0.045,20,0.003); K.cyl((g,"BLACK"),dx,dy,2.302,2.322,0.028,16,0.002)
        K.cyl((g,"BLACK"),dx+0.012,dy-0.02,2.300,2.306,0.012,10); K.cyl((g,"CAM_LED"),dx+0.082,dy,2.385,2.388,0.0065,8)
        K.tube((g,"CABLE_B"),[(dx-0.07,dy,2.399),(dx-0.13,dy,2.399),(dx-0.13,dy+0.1,2.399)],0.003,6)
        # expired inspection certificate + capacity plate on the west wall
        x=-8.629; hw,hh=0.085,0.11; yc,zc=-6.55,1.62
        K.plane((g,"LCERT"),(x,yc-hw,zc-hh),(x,yc+hw,zc-hh),(x,yc+hw,zc+hh),(x,yc-hw,zc+hh))
        K.fb((g,"BLACK"),'+x',-8.63,yc-hw-0.01,yc+hw+0.01,zc-hh-0.01,zc+hh+0.01,0.003,0.0005)
        K.fb((g,"BRASS"),'+x',-8.63,-6.64,-6.46,1.28,1.36,0.004,0.001)
    objs=_mover(c,"lift_car2",fn)
    for o in objs: o.parent=car
    for body,x,y,z,size,face,key in (("G",-7.46,-7.0575,1.40,0.036,'+y',"YELLOW"),("F1",-7.46,-7.0575,1.28,0.036,'+y',"YELLOW"),("MAX 8 PERSONS\n600 KG",-8.6265,-6.55,1.32,0.017,'+x',"BLACK")):
        t=crk.text(coll,body,x,y,z,face,size,M[key],'CENTER',"CR lift label"); t.parent=car
    for body,x,z in (("G",-7.65,1.835),("1",-7.855,1.835)):
        t=crk.text(coll,body,x,-7.0575,z,'+y',0.026,M["YELLOW"],'CENTER',"CR lift dial label"); t.parent=car
    # dial needle: pivot at the dial centre, driven by the car height (G on the east side, F1 on the west side as seen from the doors)
    def needle(K):
        g="lift_needle"; K.bx((g,"RED"),-0.0025,0.0025,-0.0015,0.0015,-0.012,0.088,0.0005); K.cyl((g,"RED"),0,0,-0.0015,0.0015,0.0,6) if False else None
    ob=_mover(c,"lift_needle",needle)
    for o in ob:
        o.parent=car; o.location=(-7.75,-7.052,1.92); drv(o,'rotation_euler',1,"1.0*(1-2*z/5.4)",var_s=False,extra=zv)
    lo=crk.light(coll,"CR lift car lamp",(-7.95,-6.40,2.25),(1.0,0.72,0.45),30,'AREA',(0,0,0),size=(0.55,0.28),expr="30*(1-0.85*max(0,sin(T*47)*sin(T*11.3+1)-0.30)*1.6)*(1-0.7*bw)",var_s=False)
    lo.parent=car
