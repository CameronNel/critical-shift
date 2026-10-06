"""Helper kit for the reactor-hall STATIONS pass (rh_stations.py): construction details on top of crk.Kit (flanges with bolt rings, gauges, lamps, hinged doors with handles,
louvres, lifting eyes, valves, lagged pipes, name / warning plates ...).  Everything takes world (or begin()/end() local) coordinates, a Kit and a group name; material keys are the
rh_mats.lib() keys (AUDI, AUDI_SATIN, STEEL, GALV, IRON, YELLOW, ORANGE, RED, WHITE, BLACK, RUBBER, BRASS, HAZARD, CONC_DARK) plus LAMP_A / LAMP_R / LAMP_G / GLASS.
Authoring code only (bpy / bmesh through crk), no engine dependency."""
import math
from mathutils import Vector
FACE={'+x':((1,0,0),(0,1,0)),'-x':((-1,0,0),(0,1,0)),'+y':((0,1,0),(1,0,0)),'-y':((0,-1,0),(1,0,0))}
def fp(face,p,l,z,d=0.0):
    """point on a face frame: p = plane coordinate along the facing axis, l = lateral coordinate, z = height, d = distance out of the face"""
    n=FACE[face][0]
    return Vector((p+n[0]*d,l,z)) if face in('+x','-x') else Vector((l,p+n[1]*d,z))
def nrm(face): return Vector(FACE[face][0])
def basis(ax):
    a=Vector(ax).normalized(); u=Vector((1,0,0)) if abs(a.x)<0.9 else Vector((0,1,0)); u=(u-a*u.dot(a)).normalized(); return a,u,a.cross(u)
def G(g,m): return (g,m)
# ------------------------------------------------------------------ round parts
def disc(K,g,m,c,ax,r,t,off=0.0,seg=24,ch=0.0):
    a=Vector(ax).normalized(); c=Vector(c); K.prism((g,m),c+a*off,c+a*(off+t),r,r,seg,0.0,True,ch)
def ring_pts(c,ax,R,n,ph=0.0):
    a,u,v=basis(ax); c=Vector(c); return [c+u*(R*math.cos(ph+2*math.pi*k/n))+v*(R*math.sin(ph+2*math.pi*k/n)) for k in range(n)]
def torus(K,g,m,c,ax,R,r,n=16,seg=6):
    P=ring_pts(c,ax,R,n); P.append(P[0]); K.tube((g,m),P,r,seg)
def bolts(K,g,m,c,ax,R,n,br=0.011,h=0.012,off=0.0,ph=0.0):
    a=Vector(ax).normalized()
    for p in ring_pts(c,ax,R,n,ph): K.prism((g,m),p+a*off,p+a*(off+h),br,br,6,0.0,True,0.0)
def flange(K,g,c,ax,rp,rf,t=0.03,n=8,br=0.011,mf='IRON',mb='STEEL',neck=0.05,face_bolts=True):
    """pipe flange facing +ax from c: disc rf thick t, tapered neck on the -ax side, bolt heads (and a thin gasket line) on the +ax face"""
    a=Vector(ax).normalized(); c=Vector(c)
    K.prism((g,mf),c-a*neck,c,rp*1.0,rp*1.45,16,0.0,False,0.0); K.prism((g,mf),c,c+a*t,rf,rf,28,0.0,True,0.0025)
    if face_bolts: bolts(K,g,mb,c,ax,rf*0.80,n,br,0.012,t)
def pipe(K,g,m,pts,r,seg=10): K.tube((g,m),pts,r,seg)
def lagged(K,g,pts,r,band=0.40,mb='STEEL'):
    """insulated pipe: galvanised cladding with a clamp band every `band` metres"""
    K.tube((g,'GALV'),pts,r,12)
    for a,b in zip(pts[:-1],pts[1:]):
        a=Vector(a); b=Vector(b); L=(b-a).length
        if L<0.1: continue
        d=(b-a)/L; k=band*0.5
        while k<L-0.05: K.prism((g,mb),a+d*(k-0.012),a+d*(k+0.012),r*1.12,r*1.12,12,0.0,True,0.0); k+=band
def eyebolt(K,g,c,ax=(0,1,0),R=0.05,r=0.011,m='YELLOW',base=True):
    c=Vector(c); torus(K,g,m,c+Vector((0,0,R)),ax,R,r,12,6)
    if base: K.cyl((g,'STEEL'),c.x,c.y,c.z-0.004,c.z+0.012,R*0.65,10,0.0)
def hexnut(K,g,m,c,ax,r,h): a=Vector(ax).normalized(); K.prism((g,m),Vector(c),Vector(c)+a*h,r,r,6,0.0,True,0.0)
def stud(K,g,x,y,z,r=0.012,h=0.06):
    K.cyl((g,'STEEL'),x,y,z,z+h,r*0.6,8,0.0); K.prism((g,'STEEL'),(x,y,z+h*0.35),(x,y,z+h*0.35+0.02),r,r,6,0.0,True,0.0)
def anchor(K,g,x,y,z,r=0.014,plate=0.05):
    """base plate + stud + nut + washer, the anchor bolt of a skid foot"""
    K.box((g,'STEEL'),x,y,z,z+0.008,plate*2,plate*2,0.0,0.002); K.cyl((g,'STEEL'),x,y,z+0.008,z+0.07,r*0.7,8,0.0); K.prism((g,'STEEL'),(x,y,z+0.008),(x,y,z+0.034),r*1.5,r*1.5,6,0.0,True,0.0)
# ------------------------------------------------------------------ instruments
def gauge(K,g,c,ax,R=0.07,deg=-30.0,body=True):
    """pressure gauge: brass bezel ring, white face, black ticks and hub, red needle, glass; faces +ax"""
    a,u,v=basis(ax); c=Vector(c)
    if body: K.prism((g,'STEEL'),c-a*0.03,c,R*0.9,R*0.9,16,0.0,True,0.0)
    K.prism((g,'BRASS'),c,c+a*0.016,R,R,24,0.0,True,0.002)
    K.prism((g,'WHITE'),c+a*0.012,c+a*0.0165,R*0.84,R*0.84,24,0.0,True,0.0)
    for k in range(9):
        th=math.radians(-135+k*33.75); p0=c+a*0.018+(u*math.cos(th)+v*math.sin(th))*R*0.64; p1=c+a*0.018+(u*math.cos(th)+v*math.sin(th))*R*(0.78 if k%2==0 else 0.72)
        K.tube((g,'BLACK'),[p0,p1],0.0022,4)
    th=math.radians(deg)
    K.tube((g,'RED'),[c+a*0.021,c+a*0.021+(u*math.cos(th)+v*math.sin(th))*R*0.66],0.0028,4)
    K.prism((g,'BLACK'),c+a*0.016,c+a*0.026,R*0.1,R*0.1,10,0.0,True,0.0)
    K.prism((g,'GLASS'),c+a*0.0275,c+a*0.0285,R*0.84,R*0.84,20,0.0,True,0.0)
def lamp(K,g,c,ax,r=0.016,m='LAMP_A',hood=False):
    a=Vector(ax).normalized(); c=Vector(c)
    K.prism((g,'STEEL'),c,c+a*0.012,r*1.5,r*1.5,12,0.0,True,0.0015); K.prism((g,m),c+a*0.010,c+a*0.022,r,r*0.9,12,0.0,True,0.0)
def pushbutton(K,g,c,ax,r=0.02,m='RED'):
    a=Vector(ax).normalized(); c=Vector(c); K.prism((g,'STEEL'),c,c+a*0.014,r*1.5,r*1.5,14,0.0,True,0.0015); K.prism((g,m),c+a*0.012,c+a*0.03,r,r*0.95,14,0.0,True,0.002)
def nameplate(K,g,face,p,l,z,w=0.22,h=0.06,m='BRASS',rivets=True):
    K.fb((g,m),face,p,l-w/2,l+w/2,z-h/2,z+h/2,0.004,0.0015)
    if rivets:
        for s in (-1,1):
            for t in (-1,1):
                c=fp(face,p,l+s*(w/2-0.012),z+t*(h/2-0.012),0.004); K.prism((g,'STEEL'),c,c+nrm(face)*0.004,0.0035,0.0035,6,0.0,True,0.0)
def warn_tri(K,g,face,p,l,z,s=0.14,m='YELLOW'):
    """warning triangle: yellow plate, black rim line and exclamation mark (safety colours only)"""
    n=nrm(face); t=Vector(FACE[face][1]); b=fp(face,p,l,z,0.0)
    P=[b+t*(-s/2)+Vector((0,0,-s*0.29)),b+t*(s/2)+Vector((0,0,-s*0.29)),b+Vector((0,0,s*0.58))]
    K.hull((g,m),[q for q in P]+[q+n*0.004 for q in P],0.0)
    Q=[b+n*0.004+t*(-s*0.36)+Vector((0,0,-s*0.19)),b+n*0.004+t*(s*0.36)+Vector((0,0,-s*0.19)),b+n*0.004+Vector((0,0,s*0.41))]
    K.hull((g,'BLACK'),Q+[q+n*0.0015 for q in Q],0.0)
    K.hull((g,m),[q+n*0.0015 for q in ([b+n*0.004+t*(-s*0.3)+Vector((0,0,-s*0.16)),b+n*0.004+t*(s*0.3)+Vector((0,0,-s*0.16)),b+n*0.004+Vector((0,0,s*0.34))])]+[q+n*0.003 for q in ([b+n*0.004+t*(-s*0.3)+Vector((0,0,-s*0.16)),b+n*0.004+t*(s*0.3)+Vector((0,0,-s*0.16)),b+n*0.004+Vector((0,0,s*0.34))])],0.0)
    K.fb((g,'BLACK'),face,p+0.0,l-s*0.02,l+s*0.02,z-s*0.12,z+s*0.12,0.0065,0.0)
    K.fb((g,'BLACK'),face,p+0.0,l-s*0.025,l+s*0.025,z-s*0.2,z-s*0.15,0.0065,0.0)
def label_bar(K,g,face,p,l0,l1,z0,z1,m='RED',t=0.003):
    K.fb((g,m),face,p,l0,l1,z0,z1,t,0.0008)
# ------------------------------------------------------------------ doors, louvres, hinges
def hinge(K,g,face,p,l,z0,z1,d=0.012,r=0.01,m='STEEL',n=2):
    """knuckle hinge: n barrels spread over z0..z1, with a small leaf plate"""
    for k in range(n):
        zc=z0+(z1-z0)*(k+0.5)/n; hh=min(0.09,(z1-z0)/n*0.55)
        K.prism((g,m),fp(face,p,l,zc-hh/2,d),fp(face,p,l,zc+hh/2,d),r,r,10,0.0,True,0.0)
def handle_t(K,g,face,p,l,z,d=0.0,vertical=True,m='BLACK',L=0.11):
    """quarter-turn T handle: boss, stem and cross bar"""
    c0=fp(face,p,l,z,d); n=nrm(face); K.prism((g,'STEEL'),c0,c0+n*0.012,0.017,0.017,14,0.0,True,0.0015); c1=c0+n*0.032
    K.prism((g,'STEEL'),c0+n*0.01,c1,0.007,0.007,8,0.0,True,0.0)
    t=Vector(FACE[face][1]) if not vertical else Vector((0,0,1)); K.prism((g,m),c1-t*L/2,c1+t*L/2,0.009,0.009,10,0.0,True,0.002)
def handle_bar(K,g,face,p,l,z,L=0.14,d=0.0,m='STEEL',vertical=True):
    """pull handle: bar on two standoffs"""
    n=nrm(face); t=Vector((0,0,1)) if vertical else Vector(FACE[face][1]); c=fp(face,p,l,z,d)
    for s in (-1,1): K.prism((g,m),c+t*(s*L*0.42),c+t*(s*L*0.42)+n*0.03,0.007,0.007,8,0.0,True,0.0)
    K.prism((g,m),c+n*0.03-t*L/2,c+n*0.03+t*L/2,0.008,0.008,10,0.0,True,0.0015)
def screws(K,g,face,p,l0,l1,z0,z1,d=0.0,r=0.0055,m='STEEL',inset=0.016):
    for l in (l0+inset,l1-inset):
        for z in (z0+inset,z1-inset):
            c=fp(face,p,l,z,d); K.prism((g,m),c,c+nrm(face)*0.005,r,r,8,0.0,True,0.0)
def door(K,g,face,p,l0,l1,z0,z1,hinge_at='l0',m='AUDI_SATIN',handle='T',t=0.016,gap=0.006,proud=0.006,hz=None):
    """hinged access door on a cabinet face: slightly proud panel with a seam gap round it, screws, hinge knuckles on one edge and a T handle or pull bar on the other"""
    K.fb((g,m),face,p+proud-t,l0+gap,l1-gap,z0+gap,z1-gap,t,0.003)
    screws(K,g,face,p+proud,l0+gap,l1-gap,z0+gap,z1-gap,0.0)
    ph=l0+0.0 if hinge_at=='l0' else l1
    hinge(K,g,face,p+proud-0.002,ph,z0+0.04,z1-0.04,0.0,0.009,'STEEL',2 if z1-z0<0.9 else 3)
    lh=(l1-0.07) if hinge_at=='l0' else (l0+0.07); zh=(z0+z1)/2 if hz is None else hz
    if handle=='T': handle_t(K,g,face,p+proud,lh,zh,0.0,True)
    elif handle=='bar': handle_bar(K,g,face,p+proud,lh,zh,min(0.22,(z1-z0)*0.5),0.0)
def louvres(K,g,m,face,p,l0,l1,z0,z1,n=6,t=0.03,frame=True,mf='STEEL'):
    """vent grille: a frame (optional) and n slats slanted in section (built as thin hulls)"""
    if frame:
        K.fb((g,mf),face,p,l0,l0+0.014,z0,z1,0.012,0.0015); K.fb((g,mf),face,p,l1-0.014,l1,z0,z1,0.012,0.0015)
        K.fb((g,mf),face,p,l0,l1,z0,z0+0.014,0.012,0.0015); K.fb((g,mf),face,p,l0,l1,z1-0.014,z1,0.012,0.0015)
    h=(z1-z0-0.03)/n
    for i in range(n):
        za=z0+0.015+i*h
        pts=[fp(face,p,l0+0.012,za,0.0),fp(face,p,l1-0.012,za,0.0),fp(face,p,l0+0.012,za+h*0.35,t),fp(face,p,l1-0.012,za+h*0.35,t),
             fp(face,p,l0+0.012,za+h*0.6,t),fp(face,p,l1-0.012,za+h*0.6,t),fp(face,p,l0+0.012,za+h*0.25,0.0),fp(face,p,l1-0.012,za+h*0.25,0.0)]
        K.hull((g,m),pts,0.0015)
def mesh_grille(K,g,face,p,l0,l1,z0,z1,m='BLACK',pitch=0.03):
    """perforated / woven guard: a dark backing with a lattice of thin bars"""
    K.fb((g,m),face,p,l0,l1,z0,z1,0.004,0.0)
    l=l0+pitch/2
    while l<l1: K.fb((g,'GALV'),face,p+0.004,l-0.0035,l+0.0035,z0,z1,0.004,0.0); l+=pitch
    z=z0+pitch/2
    while z<z1: K.fb((g,'GALV'),face,p+0.008,l0,l1,z-0.0035,z+0.0035,0.003,0.0); z+=pitch
# ------------------------------------------------------------------ boxes / cabinets
def cabinet_shell(K,g,m,x0,x1,y0,y1,z0,z1,ch=0.012,kick=0.10,kick_m='STEEL',lip=True):
    """sheet-steel cabinet body: set-back kick plate, body with chamfered edges, top lip"""
    K.bx((g,kick_m),x0+0.02,x1-0.02,y0+0.02,y1-0.02,z0,z0+kick,0.004)
    K.bx((g,m),x0,x1,y0,y1,z0+kick,z1,ch)
    if lip: K.bx((g,m),x0-0.012,x1+0.012,y0-0.012,y1+0.012,z1-0.022,z1,0.005)
def jbox(K,g,face,p,l,z,w=0.20,h=0.16,t=0.09,m='AUDI_SATIN',glands=(1,),cover=True):
    """surface junction box with screwed cover and cable glands underneath"""
    K.fb((g,m),face,p,l-w/2,l+w/2,z-h/2,z+h/2,t,0.006)
    if cover: K.fb((g,'STEEL'),face,p+t,l-w/2+0.012,l+w/2-0.012,z-h/2+0.012,z+h/2-0.012,0.008,0.002); screws(K,g,face,p+t+0.008,l-w/2+0.012,l+w/2-0.012,z-h/2+0.012,z+h/2-0.012,0.0,0.005)
    for i in range(glands):
        lg=l+(i-(glands-1)/2)*0.07; c=fp(face,p+t*0.5,lg,z-h/2); K.prism((g,'BRASS'),c,c-Vector((0,0,0.035)),0.014,0.014,8,0.0,True,0.0); K.prism((g,'BLACK'),c-Vector((0,0,0.03)),c-Vector((0,0,0.075)),0.0085,0.0085,8,0.0,True,0.0)
def toggle_guard(K,g,c,ax,L=0.07):
    a=Vector(ax).normalized(); c=Vector(c); K.prism((g,'STEEL'),c,c+a*0.01,0.016,0.016,12,0.0,True,0.0)
def cable_run(K,g,pts,r=0.012,m='BLACK'): K.tube((g,m),pts,r,8)
def conduit_up(K,g,x,y,z0,z1,r=0.016):
    K.cyl((g,'GALV'),x,y,z0,z1,r,10,0.0)
    for k in range(int((z1-z0)/0.45)+1):
        zz=z0+0.2+k*0.45
        if zz<z1-0.05: K.prism((g,'STEEL'),(x,y,zz),(x,y,zz+0.02),r*1.35,r*1.35,10,0.0,True,0.0)
def wheel(K,g,c,ax,R=0.16,r=0.014,n_sp=4,m='RED',hub='BLACK'):
    """hand wheel: round rim, spokes, hub boss with nut"""
    a,u,v=basis(ax); c=Vector(c); torus(K,g,m,c,ax,R,r,18,6)
    for k in range(n_sp):
        th=2*math.pi*k/n_sp+math.pi/4; K.tube((g,m),[c+(u*math.cos(th)+v*math.sin(th))*0.03,c+(u*math.cos(th)+v*math.sin(th))*(R-r*0.5)],r*0.62,6)
    K.prism((g,hub),c-a*0.02,c+a*0.03,0.032,0.026,12,0.0,True,0.0015); K.prism((g,'STEEL'),c+a*0.03,c+a*0.042,0.014,0.014,6,0.0,True,0.0)
def gate_valve(K,g,c,flow,stem,Rp=0.05,wheel_m='RED',with_wheel=True,body_m='IRON'):
    """flanged gate valve: cast body, end flanges with bolts, bonnet, yoke, stem, packing gland and a hand wheel"""
    c=Vector(c); f,u,v=basis(flow); s=Vector(stem).normalized()
    K.prism((g,body_m),c-f*Rp*2.3,c+f*Rp*2.3,Rp*1.45,Rp*1.45,18,0.0,True,0.004)
    K.prism((g,body_m),c,c+s*Rp*2.4,Rp*1.2,Rp*1.0,16,0.0,True,0.003)
    for sg in (-1,1): flange(K,g,c+f*sg*Rp*2.15,f*sg,Rp*0.95,Rp*2.05,Rp*0.5,8 if Rp>0.05 else 6,Rp*0.2,body_m,'STEEL',0.0)
    b=c+s*Rp*2.4; K.prism((g,body_m),b,b+s*Rp*0.45,Rp*1.65,Rp*1.65,16,0.0,True,0.004)
    for sg in (-1,1): K.prism((g,'STEEL'),b+u*sg*Rp*1.3+s*Rp*0.45,b+u*sg*Rp*0.55+s*Rp*3.3,Rp*0.22,Rp*0.22,8,0.0,True,0.0)
    K.prism((g,'STEEL'),b+s*Rp*3.2,b+s*Rp*3.7,Rp*1.1,Rp*1.1,12,0.0,True,0.002); K.prism((g,'STEEL'),b+s*Rp*0.4,b+s*Rp*4.4,Rp*0.28,Rp*0.28,8,0.0,True,0.0)
    K.prism((g,'BRASS'),b+s*Rp*0.45,b+s*Rp*0.95,Rp*0.5,Rp*0.5,10,0.0,True,0.001)
    if with_wheel: wheel(K,g,b+s*Rp*3.9,s,Rp*2.6,Rp*0.22,4,wheel_m)
# ------------------------------------------------------------------ barrels / drums / cones (props)
def drum(K,g,x,y,m='RED',h=0.88,r=0.29,lid='STEEL',z=0.0,bung=True,band=True,grimed=True):
    """200 l steel drum: rolled top and bottom chimes, two rolling hoops, recessed lid with two bungs and a seam"""
    prof=[(r*0.93,z),(r*0.96,z+0.012),(r,z+0.03),(r,z+0.06),(r*0.985,z+0.075),(r*0.985,z+h*0.30),(r,z+h*0.34),(r,z+h*0.38),(r*0.985,z+h*0.42),(r*0.985,z+h*0.60),(r,z+h*0.64),(r,z+h*0.68),(r*0.985,z+h*0.72),
          (r*0.985,z+h-0.075),(r,z+h-0.06),(r,z+h-0.03),(r*0.96,z+h-0.012),(r*0.93,z+h),(r*0.84,z+h-0.012),(r*0.80,z+h-0.022),(0.0,z+h-0.022)]
    K.lathe((g,m),x,y,prof,seg=28)
    if bung:
        for ang,rb in ((0.6,r*0.42),(3.4,r*0.30)):
            bx,by=x+rb*math.cos(ang),y+rb*math.sin(ang); K.prism((g,lid),(bx,by,z+h-0.026),(bx,by,z+h-0.004),0.028,0.028,12,0.0,True,0.002); K.prism((g,'BLACK'),(bx,by,z+h-0.004),(bx,by,z+h-0.001),0.016,0.016,10,0.0,True,0.0)
def cone(K,g,x,y,h=0.7,r=0.17,z=0.0):
    """traffic cone: square rubber base, orange tapered body with two white reflective bands"""
    K.pillow((g,'RUBBER'),x-r*1.05,x+r*1.05,y-r*1.05,y+r*1.05,z,z+0.03,0.012,2)
    K.prism((g,'ORANGE'),(x,y,z+0.03),(x,y,z+h*0.34),r*0.85,r*0.58,20,0.0,False,0.0)
    K.prism((g,'WHITE'),(x,y,z+h*0.34),(x,y,z+h*0.52),r*0.58,r*0.46,20,0.0,False,0.0)
    K.prism((g,'ORANGE'),(x,y,z+h*0.52),(x,y,z+h*0.60),r*0.46,r*0.41,20,0.0,False,0.0)
    K.prism((g,'WHITE'),(x,y,z+h*0.60),(x,y,z+h*0.76),r*0.41,r*0.31,20,0.0,False,0.0)
    K.prism((g,'ORANGE'),(x,y,z+h*0.76),(x,y,z+h),r*0.31,r*0.10,20,0.0,True,0.0)
