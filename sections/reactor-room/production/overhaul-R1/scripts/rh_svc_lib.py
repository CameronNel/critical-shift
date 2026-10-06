"""Geometry helpers for rh_services.py (hall pass, SERVICES builder).  Authoring code only (bpy / bmesh), no engine dependency.
Everything writes into crk.Kit accumulators keyed (group, material key); rh_services.py turns them into a few dozen joined objects.
Primitives: arbitrary-axis box, sweep tube along a rounded polyline (forged elbows), torus, flange pair with gasket and bolts, valves, gauges, supports."""
import bpy,bmesh,math
from mathutils import Vector
import crk

def fr(d):
    z=Vector(d).normalized(); x=Vector((1,0,0)) if abs(z.x)<0.9 else Vector((0,1,0)); x=(x-z*x.dot(z)).normalized(); return x,z.cross(x),z

def obox(K,key,c,ax,ay,az,hx,hy,hz,ch=0.0):
    """box centred c, local axes ax,ay,az (unit), half sizes hx,hy,hz (any orientation)."""
    bm=K.get(key); c=Vector(c); ax=Vector(ax).normalized(); ay=Vector(ay).normalized(); az=Vector(az).normalized()
    vs=[bm.verts.new(c+ax*(sx*hx)+ay*(sy*hy)+az*(sz*hz)) for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)]
    # vertex order: index = (sx<0?0:4)+(sy<0?0:2)+(sz<0?0:1)
    q=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    fs=[]
    for f in q:
        try: fs.append(bm.faces.new([vs[i] for i in f]))
        except ValueError: pass
    bm.normal_update()
    # make normals point outwards
    for f in fs:
        if (f.calc_center_median()-c).dot(f.normal)<0: f.normal_flip()
    if ch>0.0008:
        es=list({e for v in vs for e in v.link_edges})
        try:
            r=bmesh.ops.bevel(bm,geom=es,offset=min(ch,0.34*min(hx,hy,hz)*2),segments=1,affect='EDGES',clamp_overlap=True)
            for f in r['faces']: f.smooth=True
        except Exception: pass
    return vs

def bar(K,key,p0,p1,w,h=None,up=(0,0,1),ch=0.003):
    """flat bar / angle leg from p0 to p1, cross-section w (across) x h (along `up`)."""
    p0=Vector(p0); p1=Vector(p1); d=p1-p0; L=d.length
    if L<1e-5: return
    ax=d/L; up=Vector(up); ay=ax.cross(up)
    if ay.length<1e-4: ay=ax.cross(Vector((1,0,0)))
    ay.normalize(); az=ay.cross(ax).normalized()
    obox(K,key,(p0+p1)/2,ax,ay,az,L/2,w/2,(h if h else w)/2,ch)

def tube(K,key,pts,r,seg=8,caps=False):
    bm=K.get(key); sweep(bm,[Vector(p) for p in pts],[r]*len(pts),seg,cap_start=caps,cap_end=caps)

def sweep(bm,pts,radii,seg=12,cap_start=False,cap_end=False,smooth=True):
    n=len(pts)
    if n<2: return
    T=[]
    for i in range(n):
        t=pts[min(n-1,i+1)]-pts[max(0,i-1)]
        T.append(t.normalized() if t.length>1e-9 else (T[-1] if T else Vector((0,0,1))))
    X=fr(T[0])[0]; prev=T[0]; rings=[]
    for i in range(n):
        if i>0: X=prev.rotation_difference(T[i])@X
        Z=T[i]; Xi=(X-Z*X.dot(Z)).normalized(); Yi=Z.cross(Xi); X=Xi; prev=Z
        rings.append([bm.verts.new(pts[i]+(Xi*math.cos(2*math.pi*k/seg)+Yi*math.sin(2*math.pi*k/seg))*radii[i]) for k in range(seg)])
    for a,b in zip(rings,rings[1:]):
        for k in range(seg):
            f=bm.faces.new((a[k],a[(k+1)%seg],b[(k+1)%seg],b[k])); f.smooth=smooth
    if cap_start: bm.faces.new(rings[0][::-1])
    if cap_end: bm.faces.new(rings[-1])

def torus(K,key,c,axis,R,r,sm=20,sn=6):
    bm=K.get(key); x,y,z=fr(axis); c=Vector(c); ring=[]
    for i in range(sm):
        a=2*math.pi*i/sm; ctr=c+(x*math.cos(a)+y*math.sin(a))*R; radial=(x*math.cos(a)+y*math.sin(a))
        ring.append([bm.verts.new(ctr+(radial*math.cos(b)+z*math.sin(b))*r) for b in [2*math.pi*j/sn for j in range(sn)]])
    for i in range(sm):
        for j in range(sn):
            f=bm.faces.new((ring[i][j],ring[(i+1)%sm][j],ring[(i+1)%sm][(j+1)%sn],ring[i][(j+1)%sn])); f.smooth=True

def sphere(K,key,c,r,seg=10,rings=6):
    bm=K.get(key); res=bmesh.ops.create_uvsphere(bm,u_segments=seg,v_segments=rings,radius=r)
    for v in res['verts']: v.co=v.co+Vector(c)
    for f in {f for v in res['verts'] for f in v.link_faces}: f.smooth=True

def cyl(K,key,p0,p1,r,seg=12,r1=None):
    K.prism(key,p0,p1,r,r1,seg,0.0,True,0.0)

def hexnut(K,key,c,axis,r,L):
    a=Vector(axis).normalized(); K.prism(key,Vector(c)-a*L/2,Vector(c)+a*L/2,r,r,6,0.0,True,0.0)

def thin_prism(K,key,pts2d,c,x,y,n,t):
    """convex outline (list of (u,v)) on the plane spanned by x,y at centre c, thickness t along n (centred)."""
    pts=[]
    for (u,v) in pts2d:
        for s in(-0.5,0.5): pts.append(Vector(c)+Vector(x)*u+Vector(y)*v+Vector(n)*(t*s))
    K.hull(key,pts,0.0)

def arrow(K,key,c,d,n,L=0.30,W=0.07,t=0.004):
    """flat flow arrow lying on a surface with outward normal n, pointing along d, centred c."""
    d=Vector(d).normalized(); n=Vector(n).normalized(); y=n.cross(d).normalized(); d=y.cross(n).normalized()
    sh=L*0.58; hd=L*0.42
    c=Vector(c)
    thin_prism(K,key,[(-L/2,-W*0.18),(-L/2,W*0.18),(-L/2+sh,-W*0.18),(-L/2+sh,W*0.18)],c,d,y,n,t)
    thin_prism(K,key,[(-L/2+sh,-W*0.5),(-L/2+sh,W*0.5),(L/2,0.0)],c,d,y,n,t)

class Path:
    """polyline with long-radius forged bends; dense points with arc length.  at(s) -> (pos, tangent)."""
    def __init__(s,pts,rb=0.3,narc=7):
        pts=[Vector(p) for p in pts]; s.src=pts; out=[pts[0]]; s.bends=[]; flags=[False]; arcs=[]
        for i in range(1,len(pts)-1):
            a,b,c=pts[i-1],pts[i],pts[i+1]; u=(b-a).normalized(); v=(c-b).normalized(); cs=max(-1,min(1,u.dot(v))); ang=math.acos(cs)
            if ang<1e-3: out.append(b); flags.append(False); continue
            t=rb*math.tan(ang/2); t=min(t,0.46*(b-a).length,0.46*(c-b).length); rbe=t/math.tan(ang/2)
            nrm=(v-u*cs).normalized(); p0=b-u*t; cen=p0+nrm*rbe
            ia=len(out)
            for k in range(narc+1):
                ph=ang*k/narc; out.append(cen+(-nrm*math.cos(ph)+u*math.sin(ph))*rbe); flags.append(True)
            arcs.append((ia,len(out)-1))
        out.append(pts[-1]); flags.append(False)
        s.P=out; s.flag=flags; s.S=[0.0]
        for a,b in zip(out,out[1:]): s.S.append(s.S[-1]+(b-a).length)
        s.L=s.S[-1]; s.arcs=[(s.S[a],s.S[b]) for a,b in arcs]; s.arc_idx=arcs
    def straights(s):
        out=[]; cur=0.0
        for a,b in s.arcs:
            if a-cur>1e-4: out.append((cur,a))
            cur=b
        if s.L-cur>1e-4: out.append((cur,s.L))
        return out
    def at(s,sv):
        sv=max(0.0,min(s.L,sv))
        for i in range(1,len(s.S)):
            if s.S[i]>=sv-1e-9:
                a,b=s.P[i-1],s.P[i]; l=s.S[i]-s.S[i-1]; t=0 if l<1e-9 else (sv-s.S[i-1])/l
                return a+(b-a)*t,(b-a).normalized() if l>1e-9 else Vector((0,0,1))
        return s.P[-1],(s.P[-1]-s.P[-2]).normalized()
    def in_bend(s,sv,pad=0.0):
        return any(a-pad<=sv<=b+pad for a,b in s.arcs)
    def slice(s,s0,s1,sag=None):
        s0=max(0.0,s0); s1=min(s.L,s1)
        pts=[s.at(s0)[0]]
        for i in range(len(s.S)):
            if s0+1e-6<s.S[i]<s1-1e-6: pts.append(s.P[i])
        pts.append(s.at(s1)[0]); return pts
    def dense(s,step=0.25):
        """path with extra points on long straights (needed for sag)"""
        out=[s.P[0]]; ss=[0.0]
        for i in range(1,len(s.P)):
            a,b=s.P[i-1],s.P[i]; l=(b-a).length; n=int(l/step)
            for k in range(1,n+1): out.append(a+(b-a)*(k/(n+1))); ss.append(s.S[i-1]+l*k/(n+1))
            out.append(b); ss.append(s.S[i])
        return out,ss

def wall_of(WALLS,p):
    best=None
    for w in WALLS:
        q=Vector((p[0],p[1])); d=(q-w.P).dot(w.n); u=(q-w.P).dot(w.t)
        if -0.1<=u<=w.L+0.1 and (best is None or abs(d)<abs(best[1])): best=(w,d,u)
    return best

# ------------------------------------------------------------------ fittings
def flange_pair(K,P,d,r,gk=("R2 PIPING flange","IRON"),bk=("R2 PIPING bolt","STEEL"),gask=("R2 PIPING gasket","RUBBER"),n=None,t=0.032):
    """two raised-face flanges with a gasket and bolt ring, centred at P, pipe axis d."""
    d=Vector(d).normalized(); x,y,z=fr(d); R=r*1.75+0.02; n=n or (4 if r<0.05 else 6 if r<0.1 else 8); g=0.007
    for s in(-1,1):
        a=P+d*(s*(g/2)); b=P+d*(s*(g/2+t)); K.prism(gk,a,b,R,R,max(14,n*3),0.0,True,0.0)
        K.prism(gk,P+d*(s*(g/2+t)),P+d*(s*(g/2+t+0.006)),r*1.25,r*1.25,12,0.0,True,0.0)             # weld neck collar
    K.prism(gask,P-d*g/2,P+d*g/2,R*0.97,R*0.97,max(14,n*3),0.0,True,0.0)
    rb=R*0.76; bl=2*(t+g/2)+0.03
    for i in range(n):
        a=2*math.pi*(i+0.5)/n; o=(x*math.cos(a)+y*math.sin(a))*rb
        K.prism(bk,P+o-d*bl/2,P+o+d*bl/2,0.0055,0.0055,6,0.0,True,0.0)
        for s in(-1,1): hexnut(K,bk,P+o+d*(s*(g/2+t+0.006)),d,0.0105,0.012)

def end_flange(K,P,d,r,gk=("R2 PIPING flange","IRON"),bk=("R2 PIPING bolt","STEEL"),gask=("R2 PIPING gasket","RUBBER"),t=0.034,n=None):
    """single flange at a nozzle (P = joint face, d points back along the pipe), gasket against the device, bolt heads on the pipe side."""
    d=Vector(d).normalized(); x,y,z=fr(d); R=r*1.75+0.02; n=n or (4 if r<0.05 else 6 if r<0.1 else 8)
    K.prism(gask,P,P+d*0.005,R*0.97,R*0.97,max(14,n*3),0.0,True,0.0)
    K.prism(gk,P+d*0.005,P+d*(0.005+t),R,R,max(14,n*3),0.0,True,0.0); K.prism(gk,P+d*(0.005+t),P+d*(0.011+t),r*1.25,r*1.25,12,0.0,True,0.0)
    rb=R*0.76
    for i in range(n):
        a=2*math.pi*(i+0.5)/n; o=(x*math.cos(a)+y*math.sin(a))*rb
        hexnut(K,bk,P+o+d*(0.005+t+0.006),d,0.0105,0.014)

def clamp_ring(K,key,P,d,r,w=0.04):
    d=Vector(d).normalized(); K.prism(key,P-d*w/2,P+d*w/2,r*1.13,r*1.13,max(12,int(r*200)),0.0,True,0.0)

def band(K,key,P,d,r,w=0.06):
    d=Vector(d).normalized(); K.prism(key,P-d*w/2,P+d*w/2,r*1.012,r*1.012,max(12,int(r*220)),0.0,True,0.0)

def handwheel(K,key_wheel,key_iron,C,axis,R,r_rim=0.008):
    axis=Vector(axis).normalized(); x,y,z=fr(axis)
    torus(K,key_wheel,C,axis,R,r_rim,18,5)
    K.prism(key_iron,C-axis*0.02,C+axis*0.02,0.022,0.022,10,0.0,True,0.0)
    K.prism(key_iron,C+axis*0.02,C+axis*0.03,0.011,0.011,6,0.0,True,0.0)
    for a in (0.0,math.pi/3,2*math.pi/3):
        v=x*math.cos(a)+y*math.sin(a)
        bar(K,key_wheel,C-v*(R-0.004),C+v*(R-0.004),0.012,0.008,axis,0.0)

def gate_valve(K,P,d,r,up,wheel_key,iron=("R2 PIPING valve body","IRON"),wk="R2 PIPING handwheel",gk=("R2 PIPING flange","IRON"),bk=("R2 PIPING bolt","STEEL"),gask=("R2 PIPING gasket","RUBBER"),stem=("R2 PIPING stem","GALV")):
    d=Vector(d).normalized(); up=Vector(up).normalized(); up=(up-d*up.dot(d)).normalized()
    Lv=max(0.20,r*3.4); half=Lv/2
    K.prism(iron,P-d*(half-0.02),P+d*(half-0.02),r*1.42,r*1.42,max(14,int(r*260)),0.0,True,0.0)          # body barrel
    flange_pair_half(K,P-d*half,d,r,gk,bk,gask,face=+1); flange_pair_half(K,P+d*half,d,r,gk,bk,gask,face=-1)
    H=r*1.7+0.05                                                             # bonnet neck
    K.prism(iron,P+up*(r*0.8),P+up*(r*1.4+0.06),r*0.95,r*0.78,14,0.0,True,0.0)
    K.prism(iron,P+up*(r*1.4+0.06),P+up*(r*1.4+0.09),r*1.15,r*1.15,14,0.0,True,0.0)
    yk=r*1.4+0.09; yh=r*2.1+0.14
    x,y,z=fr(up); side=d.cross(up).normalized()
    for s in(-1,1): bar(K,iron,P+up*yk+side*(s*r*0.62),P+up*(yk+yh)+side*(s*r*0.5),0.014,0.014,d,0.0)
    bar(K,iron,P+up*(yk+yh)-side*(r*0.62),P+up*(yk+yh)+side*(r*0.62),0.022,0.018,d,0.002)       # yoke crosshead
    K.prism(stem,P+up*(yk-0.01),P+up*(yk+yh+0.07),0.0075,0.0075,6,0.0,True,0.0)                  # rising stem
    R=max(0.07,min(0.17,r*1.5)); handwheel(K,(wk,wheel_key),iron,P+up*(yk+yh+0.07),up,R)

def flange_pair_half(K,P,d,r,gk,bk,gask,face=1,t=0.032):
    """one valve-end flange (the mating pipe flange is added with flange_pair-like halves); P = flange mid-plane, d pipe axis, face=+1 means pipe lies in +d"""
    d=Vector(d).normalized(); x,y,z=fr(d); R=r*1.75+0.02; n=4 if r<0.05 else 6 if r<0.1 else 8
    a=P; b=P+d*(face*t)
    K.prism(gk,P-d*(face*t*0.0),b,R,R,max(14,n*3),0.0,True,0.0)
    K.prism(gk,b,P+d*(face*(t+0.006)),r*1.25,r*1.25,12,0.0,True,0.0)
    K.prism(gk,P-d*(face*0.02),P,R*0.98,R*0.98,max(14,n*3),0.0,True,0.0)
    rb=R*0.76
    for i in range(n):
        ang=2*math.pi*(i+0.5)/n; o=(x*math.cos(ang)+y*math.sin(ang))*rb
        hexnut(K,bk,P+o+d*(face*(t+0.006)),d,0.0105,0.013)

def check_valve(K,P,d,r,up,iron=("R2 PIPING valve body","IRON"),gk=("R2 PIPING flange","IRON"),bk=("R2 PIPING bolt","STEEL"),gask=("R2 PIPING gasket","RUBBER")):
    d=Vector(d).normalized(); up=(Vector(up)-d*Vector(up).dot(d)).normalized(); Lv=max(0.2,r*3.6); half=Lv/2; side=d.cross(up).normalized()
    K.prism(iron,P-d*(half-0.02),P+d*(half-0.02),r*1.35,r*1.35,max(14,int(r*260)),0.0,True,0.0)
    sphere(K,iron,P+up*0.0,r*1.75,14,8)
    K.prism(iron,P+up*(r*1.2),P+up*(r*1.75),r*1.15,r*1.15,14,0.0,True,0.0)                       # cover plate
    for i in range(6):
        a=2*math.pi*i/6; o=(side*math.cos(a)+d*math.sin(a))*(r*1.0); hexnut(K,bk,P+up*(r*1.8)+o,up,0.011,0.012)
    flange_pair_half(K,P-d*half,d,r,gk,bk,gask,face=+1); flange_pair_half(K,P+d*half,d,r,gk,bk,gask,face=-1)

def ball_valve(K,P,d,r,up,lever_key,iron=("R2 PIPING valve body","IRON"),bk=("R2 PIPING bolt","STEEL"),handle_dir=None):
    d=Vector(d).normalized(); up=(Vector(up)-d*Vector(up).dot(d)).normalized(); side=d.cross(up).normalized(); L=max(0.1,r*3.0)
    K.prism(iron,P-d*L*0.5,P+d*L*0.5,r*1.2,r*1.2,12,0.0,True,0.0); sphere(K,iron,P,r*1.5,10,6)
    K.prism(iron,P,P+up*(r*1.5+0.02),r*0.55,r*0.55,8,0.0,True,0.0)
    hd=side if handle_dir is None else Vector(handle_dir)
    bar(K,lever_key,P+up*(r*1.5+0.025),P+up*(r*1.5+0.025)+hd*0.11,0.014,0.008,up,0.0)
    K.prism(lever_key,P+up*(r*1.5+0.01),P+up*(r*1.5+0.04),0.009,0.009,6,0.0,True,0.0)

def gauge(K,P,out,r,mk=("R2 PIPING gauge bezel","GALV"),face=("R2 PIPING gauge face","WHITE"),iron=("R2 PIPING valve body","IRON")):
    out=Vector(out).normalized(); x,y,z=fr(out)
    K.prism(iron,P+out*r*0.5,P+out*(r+0.045),0.011,0.011,8,0.0,True,0.0)
    K.prism(iron,P+out*(r+0.04),P+out*(r+0.05),0.02,0.02,6,0.0,True,0.0)
    c=P+out*(r+0.075)
    K.prism(mk,c-out*0.027,c+out*0.027,0.054,0.054,16,0.0,True,0.0)
    K.prism(face,c+out*0.026,c+out*0.0295,0.045,0.045,16,0.0,True,0.0)
    bar(K,("R2 PIPING gauge needle","BLACK"),c+out*0.031,c+out*0.031+(x*0.5+y*0.5).normalized()*0.036,0.004,0.002,out,0.0)

def thermowell(K,P,out,r,iron=("R2 PIPING valve body","IRON"),cap=("R2 PIPING gauge bezel","GALV")):
    out=Vector(out).normalized(); x,y,z=fr(out)
    K.prism(iron,P+out*r*0.6,P+out*(r+0.035),0.021,0.021,6,0.0,True,0.0)
    K.prism(cap,P+out*(r+0.03),P+out*(r+0.125),0.011,0.008,8,0.0,True,0.0)
    obox(K,iron,P+out*(r+0.15),x,y,out,0.028,0.028,0.026,0.004)

def drain(K,P,down,r,lever_key,iron=("R2 PIPING valve body","IRON"),side=(1,0,0)):
    down=Vector(down).normalized(); K.prism(iron,P+down*r*0.6,P+down*(r+0.06),0.014,0.014,8,0.0,True,0.0)
    ball_valve(K,P+down*(r+0.1),down,0.014,side,lever_key,iron)
    K.prism(iron,P+down*(r+0.15),P+down*(r+0.19),0.016,0.016,6,0.0,True,0.0)        # plug

def tee_boss(K,P,d,rb,rh,iron=("R2 PIPING flange","IRON")):
    """forged branch connection where a branch of radius rb leaves a header of radius rh at P in direction d"""
    d=Vector(d).normalized()
    K.prism(iron,P+d*rh*0.5,P+d*(rh+0.06),rb*1.32,rb*1.12,14,0.0,True,0.0)
    K.prism(iron,P+d*(rh+0.055),P+d*(rh+0.068),rb*1.2,rb*1.2,14,0.0,True,0.0)

def wall_plate(K,P,n,w=0.14,h=0.22,t=0.012,key=("R2 PIPING support","STEEL"),bk=("R2 PIPING bolt","STEEL"),up=(0,0,1)):
    """plate with 4 bolts on a wall plane at P, normal n (pointing into the hall)"""
    n=Vector(n).normalized(); up=Vector(up); x=n.cross(up).normalized(); z=x.cross(n).normalized()
    obox(K,key,P+n*t/2,x,n,z,w/2,t/2,h/2,0.002)
    for sx in(-1,1):
        for sz in(-1,1): hexnut(K,bk,P+n*t+x*(sx*w*0.34)+z*(sz*h*0.38),n,0.0095,0.012)

def wall_arm(K,WALLS,P,r,vertical=False,dpipe=None,key=("R2 PIPING support","STEEL"),saddle=("R2 PIPING saddle","STEEL"),clampkey=("R2 PIPING clamp","GALV"),maxd=1.6):
    """cantilever arm from the nearest wall plane to the pipe at P (total outer radius r): wall plate with bolts, arm, diagonal brace, saddle and U-bolt ring."""
    wd=wall_of(WALLS,P)
    if wd is None: return False
    w,d,u=wd
    if not(0.10<d<maxd): return False
    P=Vector(P); nn=Vector((w.n.x,w.n.y,0)); base=P-nn*d
    if vertical:
        tip=P-nn*(r*1.13+0.004); bar(K,key,base+nn*0.012,tip,0.05,0.05,(0,0,1),0.003)
        wall_plate(K,base,nn,0.13,0.26,0.012,key)
        ln=(tip-base).length; bp=base+nn*(ln*0.78)+Vector((0,0,-0.03))
        bar(K,key,base+nn*0.012+Vector((0,0,-min(0.32,ln*0.6))),bp,0.035,0.025,(0,0,1),0.002)
        clamp_ring(K,clampkey,P,(0,0,1),r,0.045)
    else:
        zb=P.z-r-0.035; a0=Vector((base.x,base.y,zb)); a1=Vector((P.x,P.y,zb)); bar(K,key,a0+nn*0.012,a1,0.055,0.05,(0,0,1),0.003)
        wall_plate(K,Vector((base.x,base.y,zb-0.04)),nn,0.13,0.28,0.012,key)
        ln=(a1-a0).length; bp=a0+nn*(ln*0.78)+Vector((0,0,-0.03))
        bar(K,key,a0+nn*0.012+Vector((0,0,-min(0.34,ln*0.65))),bp,0.04,0.025,(0,0,1),0.002)
        dp=Vector(dpipe) if dpipe is not None else Vector((-nn.y,nn.x,0)); dp.normalize()
        sd=dp.cross((0,0,1)); sd=sd.normalized() if sd.length>0.1 else Vector((1,0,0))
        obox(K,saddle,Vector((P.x,P.y,zb+0.025+0.012)),dp,sd,(0,0,1),0.07,0.035,0.012,0.002)
        clamp_ring(K,clampkey,P,dp,r,0.04)
    return True

def stanchion(K,P,r,key=("R2 PIPING support","STEEL"),saddle=("R2 PIPING saddle","STEEL"),bk=("R2 PIPING bolt","STEEL"),zfloor=0.0,d_pipe=(0,1,0)):
    zt=P.z-r-0.035; x=P.x; y=P.y
    obox(K,key,(x,y,(zfloor+zt)/2),(1,0,0),(0,1,0),(0,0,1),0.035,0.035,(zt-zfloor)/2,0.002)
    obox(K,key,(x,y,zfloor+0.006),(1,0,0),(0,1,0),(0,0,1),0.11,0.11,0.006,0.002)
    for sx in(-1,1):
        for sy in(-1,1): hexnut(K,bk,(x+sx*0.08,y+sy*0.08,zfloor+0.016),(0,0,1),0.0095,0.013)
    obox(K,key,(x,y,zt+0.006),Vector(d_pipe),Vector(d_pipe).cross((0,0,1)) if abs(Vector(d_pipe).z)<0.9 else Vector((0,1,0)),(0,0,1),0.06,0.06,0.006,0.002)
    obox(K,saddle,(x,y,zt+0.0125+0.012),Vector(d_pipe),Vector(d_pipe).cross((0,0,1)) if abs(Vector(d_pipe).z)<0.9 else Vector((0,1,0)),(0,0,1),0.06,0.035,0.012,0.002)

def hanger(K,P,r,ztop,key=("R2 PIPING support","STEEL"),clampkey=("R2 PIPING clamp","GALV"),bk=("R2 PIPING bolt","STEEL"),d_pipe=(0,1,0)):
    """clevis hanger: threaded rods from ztop down to a clevis strap around the pipe"""
    dp=Vector(d_pipe).normalized(); side=dp.cross((0,0,1)).normalized() if abs(dp.z)<0.9 else Vector((1,0,0)); zc=P.z+r*0.2
    for s in(-1,1):
        o=side*(s*(r+0.025)); K.prism(key,Vector((P.x,P.y,zc))+o,Vector((P.x,P.y,ztop))+o,0.007,0.007,6,0.0,True,0.0)
        hexnut(K,bk,Vector((P.x,P.y,zc+0.02))+o,(0,0,1),0.0105,0.012)
    bar(K,key,Vector((P.x,P.y,P.z-r-0.02))-side*(r+0.03),Vector((P.x,P.y,P.z-r-0.02))+side*(r+0.03),0.05,0.012,dp,0.002)
    clamp_ring(K,clampkey,P,dp,r,0.035)
    bar(K,key,Vector((P.x,P.y,ztop-0.01))-side*(r+0.05),Vector((P.x,P.y,ztop-0.01))+side*(r+0.05),0.04,0.012,dp,0.002)

def drip_tray(K,P,r,w=0.5,l=0.34,key=("R2 PIPING drip tray","GALV"),support=("R2 PIPING support","STEEL"),ang=0.0):
    c=Vector((P.x,P.y,P.z-r-0.2)); x=Vector((math.cos(ang),math.sin(ang),0)); y=Vector((-math.sin(ang),math.cos(ang),0))
    obox(K,key,c,x,y,(0,0,1),w/2,l/2,0.004,0.002)
    for s in(-1,1):
        obox(K,key,c+x*(s*(w/2-0.006))+Vector((0,0,0.03)),x,y,(0,0,1),0.006,l/2,0.034,0.0015)
        obox(K,key,c+y*(s*(l/2-0.006))+Vector((0,0,0.03)),x,y,(0,0,1),w/2,0.006,0.034,0.0015)
    for s in(-1,1): K.prism(support,Vector((P.x,P.y,P.z-r-0.2))+x*(s*w*0.35),Vector((P.x,P.y,P.z-r-0.01))+x*(s*w*0.35),0.005,0.005,6,0.0,True,0.0)
