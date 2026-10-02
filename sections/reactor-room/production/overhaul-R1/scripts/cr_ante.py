"""Anteroom dressing and lift interior (owner brief 2026-10-01, second pass).  Called from cr_lift.build.
Anteroom (interior x -6.83..-4.83, y -7.70..-5.70, floor z 5.4): water cooler with a labelled 19 l jug and cups, loveseat with throw cushion and folded blanket,
small coffee table (magazine, remote, bowl of sweets, coffee on a coaster), a wall-mounted TV on the control room wall, a slim floor lamp, small potted plant, dark red worn Persian rug.  Lift: G / F1 button lamps and floor-indicator lamps that light for the ACTIVE floor, a flickering cabin
light and car lamp, a dome security camera with a blinking red LED, an expired inspection certificate, a capacity plate, and a wall clock (hands driven by scene time in seconds), formerly an analogue floor dial whose needle
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
def wood_tex(W=512,seed=5):
    """tileable walnut grain (u runs along the grain): warped growth rings, long pores, a few darker streaks"""
    rng=np.random.default_rng(seed); y=(np.arange(W)[:,None]/W).astype(np.float32); x=(np.arange(W)[None,:]/W).astype(np.float32)
    w=0.16*np.sin(2*np.pi*(2*y+0.5*np.sin(2*np.pi*x)))+0.07*np.sin(2*np.pi*(5*y+np.sin(2*np.pi*(2*x+0.3))))
    ring=0.5+0.5*np.sin(2*np.pi*(9*y+w*2.2)); pores=rng.random((W,W)).astype(np.float32)
    for k in range(1,9): pores+=np.roll(pores,k,axis=1)
    pores/=9; streak=np.clip(0.5+0.5*np.sin(2*np.pi*(31*y+3*w)),0,1)**6
    t=np.clip(0.55*ring+0.35*pores+0.1,0,1); lo=np.array((0.20,0.115,0.065),np.float32); hi=np.array((0.46,0.29,0.17),np.float32)
    a=lo+(hi-lo)*t[...,None]; a*=(1-0.30*streak[...,None]); return np.clip(a,0,1).astype(np.float32)
def burl_tex(W=512,seed=9):
    """tileable polished burl walnut for the lift panelling: swirling figured grain with dark 'eyes' and a warm red-brown ground (1980s luxury car trim)"""
    rng=np.random.default_rng(seed); y,x=np.mgrid[0:W,0:W].astype(np.float32)/W
    w=0.035*np.sin(2*np.pi*(2*x+1*y))+0.02*np.sin(2*np.pi*(3*y-2*x+0.3))+0.012*np.sin(2*np.pi*(6*x+5*y+0.7))
    ring=0.5+0.5*np.sin(2*np.pi*(22*(y+w)+1.2*np.sin(2*np.pi*x)))
    eyes=np.zeros((W,W),np.float32)
    for _ in range(22):
        cx,cy=rng.random(2); r=0.008+0.012*rng.random(); dx=np.abs(x-cx); dx=np.minimum(dx,1-dx); dy=np.abs(y-cy); dy=np.minimum(dy,1-dy)
        d=np.hypot(dx,dy)/r; eyes=np.maximum(eyes,np.clip(1-d,0,1)*(0.5+0.5*np.cos(d*9)))
    fine=rng.random((W,W)).astype(np.float32)
    for k in range(1,5): fine+=np.roll(fine,k,axis=1)
    fine/=5; t=np.clip(0.38*ring+0.40*fine+0.2*w*8+0.12,0,1)
    lo=np.array((0.20,0.10,0.05),np.float32); hi=np.array((0.46,0.26,0.12),np.float32)
    a=lo+(hi-lo)*t[...,None]; a=a*(1-0.28*eyes[...,None]); return np.clip(a,0,1).astype(np.float32)
def weave_tex(base,W=128,n=10,seed=7,var=0.10):
    """tileable plain-weave cloth: alternating over/under threads, per-thread tint, soft thread profile"""
    rng=np.random.default_rng(seed); y,x=np.mgrid[0:W,0:W].astype(np.float32); u=x/W*n; v=y/W*n; iu=np.floor(u).astype(int)%n; iv=np.floor(v).astype(int)%n
    fu=u-np.floor(u); fv=v-np.floor(v); over=((iu+iv)%2==0)
    h=np.where(over,np.sin(np.pi*fu),np.sin(np.pi*fv))*0.5+0.5
    tu=rng.normal(0,var,n).astype(np.float32); tv=rng.normal(0,var,n).astype(np.float32); tint=np.where(over,tv[iu],tu[iv])
    a=np.array(base,np.float32)[None,None,:]*(0.62+0.5*h[...,None])*(1+tint[...,None]); return np.clip(a,0,1).astype(np.float32)
def _drive(m,expr,extra): drv(m.node_tree,'nodes["Principled BSDF"].inputs["Emission Strength"].default_value',None,expr,var_s=False,extra=extra)
def lamp_mats(c,ctl):
    zv=[("z",ctl,'["car_z"]')]; M=c.M
    M["LAMP_G"]=emit_mat("CR lift lamp G",(1.0,0.62,0.12),4.0); _drive(M["LAMP_G"],"4.0*max(0,1-z/0.6)",zv)
    M["LAMP_F1"]=emit_mat("CR lift lamp F1",(1.0,0.62,0.12),4.0); _drive(M["LAMP_F1"],"4.0*min(1,max(0,(z-4.8)/0.6))",zv)
    M["LAMP_MOVE"]=emit_mat("CR lift lamp moving",(1.0,0.30,0.05),3.0); _drive(M["LAMP_MOVE"],"3.0*(1 if z>0.15 and z<5.25 else 0)",zv)
    M["CAB_LIGHT"]=emit_mat("CR lift cabin light",(1.0,0.74,0.46),16.0); _drive(M["CAB_LIGHT"],"16.0*(1-0.85*max(0,sin(T*47)*sin(T*11.3+1)-0.30)*1.6)*(1-0.7*bw)",[])
    M["DADO"]=tex_mat("CR lift burl wood",new_image("CR lift burl tex",burl_tex()),rough=0.08,bump=0.05,scale=(1.5,1.5),clamp=False,coat=1.0)
    M["LPHOTO"]=tex_mat("CR family photo lift",new_image("CR lift photo tex",crt.photo()),rough=0.45)
    M["COVE"]=emit_mat("CR lift cove",(1.0,0.74,0.42),7.0,expr="7.0*(1-0.35*min(1,fk))*(1-0.5*bw)")
    M["CAM_LED"]=emit_mat("CR lift camera led",(1.0,0.05,0.03),4.0); _drive(M["CAM_LED"],"4.0*(1 if fmod(T,2.4)<0.18 else 0)",[])
    M["LAMP_SHADE"]=emit_mat("CR lamp shade glow",(1.0,0.70,0.40),2.4)
    M["COFFEE"]=pm("CR coffee",(0.03,0.016,0.008),0.12,bump=0.0,scale=2.0)
    M["WOODG"]=tex_mat("CR wood grain",new_image("CR wood grain tex",wood_tex()),rough=0.42,bump=0.5,scale=(2.0,2.0),clamp=False)
    M["COUCH"]=tex_mat("CR couch weave teal",new_image("CR couch weave tex",weave_tex((0.20,0.36,0.37),seed=3)),rough=0.92,bump=1.0,scale=(24.0,24.0),clamp=False)
    M["COUCH_O"]=tex_mat("CR cushion weave mustard",new_image("CR cushion weave tex",weave_tex((0.72,0.43,0.10),seed=4)),rough=0.9,bump=1.0,scale=(24.0,24.0),clamp=False)
    M["BLANKET_W"]=tex_mat("CR blanket weave rust",new_image("CR blanket weave tex",weave_tex((0.55,0.19,0.08),n=6,seed=5,var=0.14)),rough=0.95,bump=1.4,scale=(16.0,16.0),clamp=False)
    M["MIRROR"]=pm("CR lift mirror",(0.80,0.84,0.86),0.035,metal=1.0,scale=2.0,bump=0.0,var=(0.97,1.0),grain=0.0)
    M["CERAMIC"]=pm("CR glazed ceramic",(0.52,0.50,0.44),0.12,scale=2.0,bump=0.0,coat=0.6,var=(0.96,1.02))
    M["ATVSCR"]=tex_mat("CR tv anteroom screen",new_image("CR tv anteroom tex",crt.tv_broadcast(384,216)),rough=0.25,emit=1.3); crk.drv(M["ATVSCR"].node_tree,'nodes["Principled BSDF"].inputs["Emission Strength"].default_value',None,"1.3*(1-0.30*min(1,fk))*(1-0.55*bw)",var_s=False)
    M["POSTER_A"]=tex_mat("CR poster anteroom shift",new_image("CR poster anteroom tex",crt.poster("shift",seed=61)),rough=0.5)
    M["BRUSH"]=pm("CR brushed steel panel",(0.50,0.51,0.51),0.34,metal=1.0,scale=3.0,bump=0.0,var=(0.88,1.04),aniso=(40.0,1.0,1.0))
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
def trim(c,yn):
    """skirting, picture rail style coving and the framed print above the couch (absolute coordinates, interior of the anteroom + alcove)"""
    A=c.A; g="antetrim"; AXW,AX0,AX1,AY0,AY1=-7.70,-6.83,-4.83,-8.95,-5.70; CZ=8.50
    H=0.10
    A.fb((g,"WOODG"),'+y',AY0,AXW,AX1,FZ,FZ+H,0.017,0.003); A.fb((g,"WOODG"),'+x',AXW,AY0,yn,FZ,FZ+H,0.017,0.003); A.fb((g,"WOODG"),'-y',yn,AXW,AX0,FZ,FZ+H,0.017,0.003)
    A.fb((g,"WOODG"),'+x',AX0,yn,-7.10,FZ,FZ+H,0.017,0.003); A.fb((g,"WOODG"),'+x',AX0,-5.70,AY1,FZ,FZ+H,0.017,0.003)
    A.fb((g,"WOODG"),'-y',AY1,AX0,AX1,FZ,FZ+H,0.017,0.003)
    A.fb((g,"WOODG"),'-x',-5.0,AY0,-7.34,FZ,FZ+H,0.017,0.003); A.fb((g,"WOODG"),'-x',-5.0,-6.26,AY1,FZ,FZ+H,0.017,0.003)
    K=0.055                                                                                       # ceiling coving
    A.fb((g,"WALL_HI"),'+y',AY0,AXW,AX1,CZ-K,CZ,0.03,0.006); A.fb((g,"WALL_HI"),'+x',AXW,AY0,yn,CZ-K,CZ,0.03,0.006); A.fb((g,"WALL_HI"),'-y',yn,AXW,AX0,CZ-K,CZ,0.03,0.006)
    A.fb((g,"WALL_HI"),'-y',AY1,AX0,AX1,CZ-K,CZ,0.03,0.006)
    # framed print over the couch (alcove west wall, seen from the east): wood frame, white mat, the poster decal
    cy,cz,w,h=-8.24,FZ+1.55,0.56,0.76
    for (y0,y1,z0,z1) in ((cy-w/2-0.03,cy+w/2+0.03,cz-h/2-0.03,cz-h/2),(cy-w/2-0.03,cy+w/2+0.03,cz+h/2,cz+h/2+0.03),(cy-w/2-0.03,cy-w/2,cz-h/2,cz+h/2),(cy+w/2,cy+w/2+0.03,cz-h/2,cz+h/2)):
        A.fb((g,"WOODG"),'+x',AXW+0.02,y0,y1,z0,z1,0.026,0.004)
    A.fb((g,"PAPER"),'+x',AXW+0.02,cy-w/2,cy+w/2,cz-h/2,cz+h/2,0.012,0.002)
    xp=AXW+0.0325
    A.plane((g,"POSTER_A"),(xp,cy-w/2+0.05,cz-h/2+0.05),(xp,cy+w/2-0.05,cz-h/2+0.05),(xp,cy+w/2-0.05,cz+h/2-0.05),(xp,cy-w/2+0.05,cz+h/2-0.05))      # viewed from the east: +y is on the viewer's right
    tv(c)
def tv(c):
    """slim wall-mounted TV on the control room's west wall (anteroom east wall), south of the door, facing the couch; the screen plays the management broadcast, flickering with the shared tube signal"""
    A,M=c.A,c.M; g="antetv"; X=-5.0; y0,y1=-8.62,-7.66; z0,z1=FZ+1.12,FZ+1.66
    A.pillow((g,"BLACK"),X-0.040,X-0.004,y0-0.012,y1+0.012,z0-0.012,z1+0.012,0.008,2)                         # body + bezel
    A.bx((g,"GREY"),X-0.012,X-0.004,y0+0.25,y1-0.25,z0+0.10,z1-0.10,0.002)                                      # wall bracket
    A.plane((g,"ATVSCR"),(X-0.0425,y1,z0),(X-0.0425,y0,z0),(X-0.0425,y0,z1),(X-0.0425,y1,z1),uv=((0,0),(1,0),(1,1),(0,1)))
    A.bx((g,"BLACK"),X-0.040,X-0.039,(y0+y1)/2-0.06,(y0+y1)/2+0.06,z0-0.014,z0-0.006,0.0005)
    tvl=crk.light(c.coll,"CR anteroom tv glow",(X-0.35,(y0+y1)/2,FZ+1.40),(0.62,0.88,0.90),5,'AREA',(0,math.radians(90),0),size=(0.9,0.5))
    tvl.visible_camera=False                                                                       # the area light is only illumination: its dark back panel must not show in shot
def _bead(A,key,x,y,z,r,seg=8):
    A.lathe(key,x,y,[(0.0,z-r),(r*0.8,z-r*0.55),(r,z),(r*0.8,z+r*0.55),(0.0,z+r)],seg=seg)
def _leg(A,key,x,y,h,w0,w1,ch=0.002,sp=(0.0,0.0)):
    """tapered, slightly splayed furniture leg from the floor (z FZ) up to height h"""
    pts=[(x+sx*w0/2,y+sy*w0/2,FZ+h) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]+[(x+sx*w1/2+sp[0],y+sy*w1/2+sp[1],FZ) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
    A.hull(key,pts,ch)
def props(c):
    A,M=c.A,c.M; g="anteprop"; Z=FZ; AY0=-8.95
    # ---------------- dark red worn Persian rug (alpha fringe in the texture) between the couch and the TV
    A.plane((g,"RUG"),(-6.88,-8.60,Z+0.006),(-5.43,-8.60,Z+0.006),(-5.43,-7.63,Z+0.006),(-6.88,-7.63,Z+0.006))
    # ---------------- water cooler on the north wall: rounded body, recessed tap bay, drip grille, cup dispenser, ribbed 19 l jug
    cx0,cx1,cy0,cy1=-5.62,-5.28,-6.08,-5.70; jx,jy=(cx0+cx1)/2,(cy0+cy1)/2
    A.pillow((g,"PORC"),cx0,cx1,cy0,cy1,Z+0.07,Z+1.10,0.022,3); A.pillow((g,"BLACK"),cx0+0.015,cx1-0.015,cy0+0.012,cy1-0.015,Z,Z+0.075,0.01,2)
    A.fb((g,"BLACK"),'-y',cy0+0.004,cx0+0.035,cx1-0.035,Z+0.34,Z+0.86,0.012,0.004)                    # recessed tap bay
    A.pillow((g,"PORC_O"),cx0+0.03,cx1-0.03,cy0-0.006,cy0+0.012,Z+0.90,Z+1.05,0.006,2)                # control strip
    A.cyly((g,"LED_ON"),cx0+0.075,cy0-0.006,cy0-0.010,Z+0.98,0.007,10); A.cyly((g,"LED_AON"),cx0+0.105,cy0-0.006,cy0-0.010,Z+0.98,0.007,10)
    A.cyly((g,"CERAMIC"),cx0+0.19,cy0-0.006,cy0-0.012,Z+0.98,0.012,12)
    for (x,key) in ((cx0+0.085,"JUG"),(cx1-0.085,"RED")):                                             # cold (blue) / hot (red) taps
        A.pillow((g,key),x-0.020,x+0.020,cy0-0.052,cy0-0.004,Z+0.70,Z+0.745,0.008,2); A.cyly((g,"STEEL_L"),x,cy0-0.052,cy0-0.036,Z+0.69,0.010,10); A.pillow((g,key),x-0.007,x+0.007,cy0-0.058,cy0-0.030,Z+0.745,Z+0.80,0.004,1)
    A.pillow((g,"GREY"),cx0+0.03,cx1-0.03,cy0-0.075,cy0+0.012,Z+0.55,Z+0.585,0.008,2)                  # drip tray
    for k in range(7): A.bx((g,"BLACK"),cx0+0.045+k*0.0385,cx0+0.045+k*0.0385+0.012,cy0-0.070,cy0+0.004,Z+0.585,Z+0.592,0.001)   # grille bars
    A.lathe((g,"GREY"),cx1+0.045,cy1-0.085,[(0.030,Z+0.56),(0.036,Z+0.575),(0.036,Z+1.05),(0.031,Z+1.062),(0.028,Z+1.062),(0.0,Z+1.062)] ,seg=14)   # cup dispenser tube
    A.lathe((g,"PAPER"),cx1+0.045,cy1-0.085,[(0.026,Z+1.045),(0.034,Z+1.085),(0.036,Z+1.092),(0.0,Z+1.092)],seg=12)   # top cup of the stack
    A.lathe((g,"GREY"),jx,jy,[(0.0,Z+1.10),(0.135,Z+1.10),(0.150,Z+1.115),(0.150,Z+1.15),(0.128,Z+1.155),(0.0,Z+1.155)],seg=26)   # bottle seat
    z0=Z+1.155
    A.lathe((g,"JUG"),jx,jy,[(0.0,z0),(0.095,z0),(0.122,z0+0.012),(0.130,z0+0.030),(0.136,z0+0.048),(0.136,z0+0.075),(0.128,z0+0.085),(0.136,z0+0.095),(0.136,z0+0.110),(0.128,z0+0.120),(0.136,z0+0.130),
                           (0.136,z0+0.305),(0.128,z0+0.320),(0.113,z0+0.348),(0.088,z0+0.376),(0.067,z0+0.392),(0.062,z0+0.402),(0.062,z0+0.428),(0.0,z0+0.428)],seg=28)
    A.lathe((g,"CERAMIC"),jx,jy,[(0.0,z0+0.440),(0.060,z0+0.428),(0.070,z0+0.436),(0.070,z0+0.452),(0.0,z0+0.452)],seg=20)                        # cap
    A.cyl((g,"PAPER"),jx,jy,z0+0.145,z0+0.305,0.1375,28)                                               # white label band
    crk.text(c.coll,"FAMILY CO.\nSPRING WATER",jx,jy-0.1385,z0+0.225,'-y',0.023,M["BLACK"],'CENTER',"CR jug label",spacing=1.0)
    # ---------------- couch in the alcove on the rug, back to the west wall, facing the TV (teal weave): tapered wooden legs, frame, arms, two seat + two back cushions, throw cushion, blanket
    A.begin(-7.30,-8.24,-math.pi/2,0.0)                                                                  # local frame: back at local y -0.38, front at +0.38, +y faces the TV (east)
    x0,x1,y0,y1=-0.68,0.68,-0.38,0.38; w=x1-x0
    for (lx_,ly_,sx) in ((x0+0.07,y0+0.07,-1),(x1-0.07,y0+0.07,1),(x0+0.07,y1-0.07,-1),(x1-0.07,y1-0.07,1)): _leg(A,(g,"WOODG"),lx_,ly_,0.13,0.05,0.032,0.002,(0.012*sx,0.0))
    A.pillow((g,"COUCH"),x0+0.02,x1-0.02,y0+0.01,y1-0.03,Z+0.11,Z+0.28,0.025,2)
    for (xa,xb) in ((x0,x0+0.14),(x1-0.14,x1)): A.pillow((g,"COUCH"),xa,xb,y0+0.01,y1-0.01,Z+0.11,Z+0.63,0.055,3)
    A.pillow((g,"COUCH"),x0+0.13,x1-0.13,y0+0.01,y0+0.20,Z+0.27,Z+0.80,0.05,2,tilt=0.10)
    cw=(w-0.28-0.01)/2
    for k in range(2):
        xa=x0+0.14+k*(cw+0.01)
        A.pillow((g,"COUCH"),xa,xa+cw,y0+0.17,y1-0.015,Z+0.27,Z+0.46,0.055,3)
        A.pillow((g,"COUCH"),xa+0.01,xa+cw-0.01,y0+0.07,y0+0.25,Z+0.42,Z+0.84,0.06,3,tilt=0.16)
    A.pillow((g,"COUCH_O"),x0+0.17,x0+0.47,y0+0.27,y0+0.39,Z+0.47,Z+0.79,0.05,3,yaw=0.38,tilt=0.24)
    A.pillow((g,"BLANKET_W"),x1-0.15,x1+0.012,y0+0.03,y1-0.01,Z+0.628,Z+0.668,0.016,2)
    A.pillow((g,"BLANKET_W"),x1+0.002,x1+0.022,y1-0.30,y1-0.01,Z+0.36,Z+0.66,0.012,2); A.pillow((g,"BLANKET_W"),x1-0.158,x1-0.138,y1-0.30,y1-0.01,Z+0.30,Z+0.64,0.012,2)
    A.pillow((g,"BLANKET_W"),x1-0.35,x1-0.15,y1-0.28,y1-0.03,Z+0.46,Z+0.49,0.014,2,yaw=-0.2)
    A.pillow((g,"BOOK"),x0+0.55,x0+0.66,y0+0.40,y0+0.56,Z+0.46,Z+0.485,0.003,1,yaw=0.3)                      # paperback left on the seat
    A.end()
    # ---------------- coffee table (walnut), long side along the couch: magazine, remote, coffee on a coaster, bowl of sweets
    tx0,tx1,ty0,ty1=-6.55,-6.15,-8.42,-7.72; tz=Z+0.40
    A.pillow((g,"WOODG"),tx0,tx1,ty0,ty1,tz-0.03,tz,0.010,2)
    for (xa,xb,ya,yb) in ((tx0+0.035,tx0+0.055,ty0+0.04,ty1-0.04),(tx1-0.055,tx1-0.035,ty0+0.04,ty1-0.04)): A.bx((g,"WOODG"),xa,xb,ya,yb,tz-0.085,tz-0.03,0.002)
    A.pillow((g,"WOODG"),tx0+0.04,tx1-0.04,ty0+0.05,ty1-0.05,Z+0.095,Z+0.115,0.005,1)
    for (lx_,ly_,sx) in ((tx0+0.04,ty0+0.045,-1),(tx1-0.04,ty0+0.045,1),(tx0+0.04,ty1-0.045,-1),(tx1-0.04,ty1-0.045,1)): _leg(A,(g,"WOODG"),lx_,ly_,0.37,0.04,0.026,0.002,(0.014*sx,0.0))
    mx,my,ma=-6.35,-8.24,math.pi/2+0.22; hw,hh=0.14,0.105
    A.box((g,"PAPER"),mx,my,tz,tz+0.007,2*hw,2*hh,ma,0.001)
    pts=[_rot(mx,my,dx,dy,ma) for (dx,dy) in ((-hw,-hh),(hw,-hh),(hw,hh),(-hw,hh))]
    A.plane((g,"MAG"),*[(p[0],p[1],tz+0.0073) for p in pts])
    A.pillow((g,"BLACK"),-6.30,-6.26,-8.02,-7.86,tz,tz+0.016,0.006,2,yaw=0.12)   # remote
    kx,ky=-6.43,-7.80                                                                                    # coaster with a coffee cup
    A.lathe((g,"CORK"),kx,ky,[(0.0,tz),(0.042,tz),(0.044,tz+0.002),(0.044,tz+0.005),(0.0,tz+0.005)],seg=22)
    A.lathe((g,"PORC_O"),kx,ky,[(0.0,tz+0.005),(0.024,tz+0.005),(0.028,tz+0.010),(0.036,tz+0.030),(0.038,tz+0.085),(0.035,tz+0.088),(0.033,tz+0.084),(0.0335,tz+0.072),(0.0,tz+0.072)],seg=22)
    A.cyl((g,"COFFEE"),kx,ky,tz+0.070,tz+0.0735,0.0335,22)
    A.tube((g,"PORC_O"),[(kx+0.036,ky,tz+0.070),(kx+0.060,ky,tz+0.066),(kx+0.062,ky,tz+0.038),(kx+0.037,ky,tz+0.026)],0.0058,6)
    A.lathe((g,"PORC_O"),-6.35,-7.98,[(0.0,tz),(0.032,tz),(0.040,tz+0.006),(0.070,tz+0.030),(0.078,tz+0.050),(0.074,tz+0.052),(0.066,tz+0.032),(0.034,tz+0.014),(0.0,tz+0.014)],seg=24)   # bowl
    for (dx,dy,dz,key) in ((-0.018,0.010,0.0,"RED"),(0.020,-0.008,0.0,"YELLOW"),(0.000,0.026,0.0,"ORANGE"),(-0.030,-0.018,0.0,"RED"),(0.026,0.022,0.012,"YELLOW"),(-0.004,-0.004,0.020,"ORANGE"),(0.034,-0.026,0.0,"RED")): _bead(A,(g,key),-6.35+dx,-7.98+dy,tz+0.030+dz,0.0105)
    # ---------------- slim floor lamp beside the plant in the south-east corner (replaces the bedside table lamp: the alcove has no room for a table)
    lx,ly=-5.55,-8.80
    A.lathe((g,"BRASS"),lx,ly,[(0.0,Z),(0.095,Z),(0.100,Z+0.008),(0.080,Z+0.020),(0.014,Z+0.030),(0.010,Z+0.045),(0.010,Z+1.30),(0.0,Z+1.31)],seg=22)
    A.lathe((g,"LAMP_SHADE"),lx,ly,[(0.150,Z+1.22),(0.085,Z+1.46),(0.081,Z+1.46),(0.146,Z+1.22)],seg=26)
    crk.light(c.coll,"CR floor lamp",(lx,ly,Z+1.36),(1.0,0.70,0.40),9,'POINT',soft=0.06)
    # ---------------- potted plant in the south-east corner (terracotta pot, 12 curved leaves)
    px,py=-5.17,-8.72
    A.lathe((g,"TERRA"),px,py,[(0.0,Z),(0.075,Z),(0.082,Z+0.01),(0.118,Z+0.20),(0.128,Z+0.24),(0.128,Z+0.275),(0.120,Z+0.285),(0.108,Z+0.275),(0.106,Z+0.255),(0.0,Z+0.255)],seg=24)
    A.cyl((g,"SOIL"),px,py,Z+0.250,Z+0.262,0.107,22)
    for k in range(12):
        a=k*2*math.pi/12+0.35; ca,sa=math.cos(a),math.sin(a); r_=0.02+0.012*(k%3); L=0.20+0.07*((k*5)%4)/3; h=0.18+0.14*((k*7)%5)/4
        base=(px+r_*ca,py+r_*sa,Z+0.26)
        A.tube((g,"PLANT"),[base,(px+(r_+0.03)*ca,py+(r_+0.03)*sa,Z+0.26+h*0.6),(px+(r_+0.06)*ca,py+(r_+0.06)*sa,Z+0.26+h)],0.0032,5)
        A.leaf((g,"PLANT"),(px+(r_+0.06)*ca,py+(r_+0.06)*sa,Z+0.26+h),(ca,sa),L,0.052,droop=0.55,n=5,t=0.0016)
def car_dressing(K,x0,x1,y0,y1):
    """car walls in three tones with sharp raised panels, brushed rails, an amber stripe, a big framed mirror, an emergency phone with a coiled cord, the inspection certificate and
    capacity plate (south wall), a floor display (G | arrow | 1) over the north door and glowing LED coves.  All inner faces: west x -8.63, south y -7.08, north lintel y -5.75."""
    g="lift_car"; xw=x0+0.07; ys=y0+0.07; yn=y1-0.10; xe=x1-0.10
    # olive dado: raised panels with a graphite field, on both wall sides
    for (ya,yb) in ((-7.04,-6.62),(-6.58,-6.16),(-6.12,-5.79)):
        K.fb((g,"BRASS"),'+x',xw,ya,yb,0.12,0.88,0.014,0.004); K.fb((g,"DADO"),'+x',xw+0.014,ya+0.03,yb-0.03,0.15,0.85,0.003,0.002)
    for (xa,xb) in ((-8.60,-8.20),(-8.16,-7.76),(-7.72,-7.32)):
        K.fb((g,"BRASS"),'+y',ys,xa,xb,0.12,0.88,0.014,0.004); K.fb((g,"DADO"),'+y',ys+0.014,xa+0.035,xb-0.035,0.16,0.84,0.003,0.002)
    K.fb((g,"BRASS"),'+x',xw,ys,yn,0.90,0.945,0.024,0.004); K.fb((g,"BRASS"),'+y',ys,xw,xe,0.90,0.945,0.024,0.004)                                  # chair rail
    K.fb((g,"ORANGE"),'+x',xw,ys,yn,2.10,2.15,0.010,0.003); K.fb((g,"ORANGE"),'+y',ys,xw,xe,2.10,2.15,0.010,0.003)                                 # amber stripe
    K.fb((g,"BRUSH"),'+x',xw,ys,yn,2.22,2.27,0.028,0.004); K.fb((g,"BRUSH"),'+y',ys,xw,xe,2.22,2.27,0.028,0.004)                                  # crown rail
    K.fb((g,"COVE"),'+x',xw,ys,yn,2.285,2.325,0.012,0.002); K.fb((g,"COVE"),'+y',ys,xw,xe,2.285,2.325,0.012,0.002)                                 # LED coves
    # big mirror on the west wall, above the handrail: heavy brushed frame, bevelled glass
    my0,my1,mz0,mz1=-6.80,-5.95,1.08,2.04; fw=0.045
    for (ya,yb,za,zb) in ((my0-fw,my1+fw,mz0-fw,mz0),(my0-fw,my1+fw,mz1,mz1+fw),(my0-fw,my0,mz0,mz1),(my1,my1+fw,mz0,mz1)): K.fb((g,"BRUSH"),'+x',xw,ya,yb,za,zb,0.024,0.004)
    K.fb((g,"MIRROR"),'+x',xw,my0,my1,mz0,mz1,0.010,0.004)
    # emergency phone box with handset and coiled cord, west wall south strip
    K.fb((g,"RED"),'+x',xw,-7.03,-6.83,1.05,1.42,0.070,0.006); K.fb((g,"PAPER"),'+x',xw+0.070,-7.00,-6.86,1.34,1.39,0.003,0.001)
    K.fb((g,"BLACK"),'+x',xw+0.070,-6.975,-6.915,1.12,1.31,0.024,0.008); K.fb((g,"BRUSH"),'+x',xw+0.070,-6.99,-6.90,1.08,1.12,0.012,0.003)
    pts=[(xw+0.105+0.011*math.cos(t),-6.855+0.011*math.sin(t),1.10-0.0045*t/(2*math.pi)*3.2) for t in [k*0.55 for k in range(32)]]
    K.tube((g,"BLACK"),pts,0.0024,4)
    # inspection certificate (expired) in a thin black frame and the brass capacity plate, south wall west end
    cx,cz,hw,hh=-8.38,1.62,0.085,0.11; yy=ys+0.0005
    K.plane((g,"LCERT"),(cx+hw,yy,cz-hh),(cx-hw,yy,cz-hh),(cx-hw,yy,cz+hh),(cx+hw,yy,cz+hh))
    for (xa,xb,za,zb) in ((cx-hw-0.012,cx+hw+0.012,cz-hh-0.012,cz-hh),(cx-hw-0.012,cx+hw+0.012,cz+hh,cz+hh+0.012),(cx-hw-0.012,cx-hw,cz-hh,cz+hh),(cx+hw,cx+hw+0.012,cz-hh,cz+hh)): K.fb((g,"BLACK"),'+y',ys,xa,xb,za,zb,0.006,0.002)
    K.fb((g,"BRASS"),'+y',ys,cx-0.11,cx+0.11,1.20,1.31,0.004,0.0015)
    px,pz,pw,ph=-8.08,1.50,0.095,0.125                                                                  # framed staff photo between the certificate and the dial
    K.plane((g,"LPHOTO"),(px+pw,ys+0.0005,pz-ph),(px-pw,ys+0.0005,pz-ph),(px-pw,ys+0.0005,pz+ph),(px+pw,ys+0.0005,pz+ph))
    for (xa,xb,za,zb) in ((px-pw-0.014,px+pw+0.014,pz-ph-0.014,pz-ph),(px-pw-0.014,px+pw+0.014,pz+ph,pz+ph+0.014),(px-pw-0.014,px-pw,pz-ph,pz+ph),(px+pw,px+pw+0.014,pz-ph,pz+ph)): K.fb((g,"BRASS"),'+y',ys,xa,xb,za,zb,0.008,0.002)
    for k in range(12): K.cyly((g,"BRUSH"),xw+0.06+k*0.105,ys+0.024,ys+0.029,0.9225,0.0055,6); K.cylx((g,"BRUSH"),xw+0.024,xw+0.029,ys+0.06+k*0.105,0.9225,0.0055,6) if k<12 else None   # rivets on the chair rail
    # floor display housing over the north door (letters + arrow are driven by the car height)
    K.fb((g,"BLACK"),'-y',yn,-8.26,-7.64,2.05,2.255,0.026,0.006)
    K.hull((g,"LAMP_MOVE"),[(-7.95-0.035,yn-0.027,2.09),(-7.95+0.035,yn-0.027,2.09),(-7.95,yn-0.027,2.215),(-7.95-0.035,yn-0.030,2.09),(-7.95+0.035,yn-0.030,2.09),(-7.95,yn-0.030,2.215)],0.0)
    # rubber floor: yellow edge strips and a stencilled G | 1 in the corner
    K.bx((g,"YELLOW"),xw,xw+0.03,ys,yn,0.096,0.100,0.0); K.bx((g,"YELLOW"),xw,xe,ys,ys+0.03,0.096,0.100,0.0)
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
        cx,cz=-7.75,1.92                                                                                                                                            # wall clock (replaces the analogue floor dial: the display over the door shows the floor)
        K.cyly((g,"BRASS"),cx,-7.08,-7.060,cz,0.128,40,0.003); K.cyly((g,"PAPER"),cx,-7.060,-7.056,cz,0.108,40)
        for k in range(12):
            th=math.radians(k*30); big=(k%3==0); r0=0.082 if big else 0.090; r1=0.103
            K.tube((g,"BLACK"),[(cx-math.sin(th)*r0,-7.0555,cz+math.cos(th)*r0),(cx-math.sin(th)*r1,-7.0555,cz+math.cos(th)*r1)],0.0030 if big else 0.0016,4)
        K.cyly((g,"BRASS"),cx,-7.056,-7.046,cz,0.009,12)
        # security dome camera in the south-west ceiling corner, red LED beside it
        dx,dy=-8.50,-6.95
        K.cyl((g,"STEEL_L"),dx,dy,2.378,2.40,0.070,22,0.003); K.cyl((g,"BLACK"),dx,dy,2.350,2.378,0.058,22,0.003); K.cyl((g,"BLACK"),dx,dy,2.322,2.350,0.045,20,0.003); K.cyl((g,"BLACK"),dx,dy,2.302,2.322,0.028,16,0.002)
        K.cyl((g,"BLACK"),dx+0.012,dy-0.02,2.300,2.306,0.012,10); K.cyl((g,"CAM_LED"),dx+0.082,dy,2.385,2.388,0.0065,8)
        K.tube((g,"CABLE_B"),[(dx-0.07,dy,2.399),(dx-0.13,dy,2.399),(dx-0.13,dy+0.1,2.399)],0.003,6)
    objs=_mover(c,"lift_car2",fn)
    for o in objs: o.parent=car
    for body,x,y,z,size,face,key in (("G",-7.46,-7.0575,1.40,0.036,'+y',"YELLOW"),("F1",-7.46,-7.0575,1.28,0.036,'+y',"YELLOW"),("MAX 8 PERSONS\n600 KG",-8.38,-7.0745,1.25,0.0145,'+y',"BLACK"),("G",-8.12,-5.7765,2.155,0.085,'-y',"LAMP_G"),("1",-7.80,-5.7765,2.155,0.085,'-y',"LAMP_F1")):
        t=crk.text(coll,body,x,y,z,face,size,M[key],'CENTER',"CR lift label"); t.parent=car
    for body,dx,dz in (("12",0.0,0.066),("3",-0.066,0.0),("6",0.0,-0.066),("9",0.066,0.0)):
        t=crk.text(coll,body,-7.75+dx,-7.0558,1.92+dz,'+y',0.020,M["BLACK"],'CENTER',"CR lift clock numeral"); t.parent=car
    # clock hands: pivots at the clock centre, driven by scene time in seconds (second hand 60 s per turn, minute hand 1 h, hour hand 12 h); the clock reads 10:08:35 at t = 0
    def hand(name,ln,w,tail,key,yoff,expr):
        def fn2(K):
            g="lift_hand"; K.bx((g,key),-w,w,-0.0006,0.0006,-tail,ln,0.0003)
        for o in _mover(c,name,fn2):
            o.parent=car; o.location=(-7.75,-7.0545+yoff,1.92); drv(o,'rotation_euler',1,expr,var_s=False,extra=[])
    hand("lift_clock_hour",0.060,0.0045,0.012,"BLACK",0.0,"-6.28319*(0.84167+T/43200)")
    hand("lift_clock_min",0.092,0.0030,0.016,"BLACK",0.0007,"-6.28319*(0.14333+T/3600)")
    hand("lift_clock_sec",0.100,0.0012,0.028,"RED",0.0014,"-6.28319*(0.58333+T/60)")
    lo=crk.light(coll,"CR lift car lamp",(-7.95,-6.40,2.25),(1.0,0.72,0.45),150,'AREA',(0,0,0),size=(0.55,0.28),expr="150*(1-0.85*max(0,sin(T*47)*sin(T*11.3+1)-0.30)*1.6)*(1-0.7*bw)",var_s=False)
    lo.parent=car
