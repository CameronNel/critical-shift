"""SERVICES stage of the reactor-hall pass: pipes, lagging, valves, supports, cable trays, conduits, junction boxes and the visible light fixtures.
usage: python rh_services.py -- <in.blend> <out.blend>
Owns collection '24 R2 PIPING AND CABLES' (everything in it is replaced) and new objects 'RH services ...'; in '25 LIGHTING' only fixture housings (lamps, cages, beacon lens
geometry, exit signs) are replaced: the lights themselves and their state drivers are kept (only static cool/blue light colours are retinted to neutral/warm for the palette audit).
Run centrelines come from ../piping_runs_generated.json (the verified manifest): ports, devices and run end points are NOT moved, only the geometry around them is rebuilt.
Object names carry the token 'R2 PIPING' so that clearance.py, which ray-casts along every run centreline, ignores the run's own pipe / fittings."""
import bpy,bmesh,sys,os,math,json,re
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from mathutils import Vector
import crk,r2lib,rh_mats
import rh_support_registry as SUPPORT
from rh_svc_lib import *
A=sys.argv[sys.argv.index("--")+1:]; SRC,OUT=A[0],A[1]
bpy.ops.wm.open_mainfile(filepath=SRC); sc=bpy.context.scene
SUPPORT.reset('piping gantry mounts')
SUPPORT.reset('piping supports')
WALLS=r2lib.WALLS
MANIFEST=json.load(open(os.path.join(HERE,"..","piping_runs_generated.json"))); RUN={r["name"]:r for r in MANIFEST}
COLL_PIPE="24 R2 PIPING AND CABLES"; COLL_LIGHT="25 LIGHTING"
Z_RING=11.6; DI=0.95
# ------------------------------------------------------------------ clean own objects
def rm(o):
    me=o.data if o.type=='MESH' else None
    bpy.data.objects.remove(o,do_unlink=True)
    if me and me.users==0: bpy.data.meshes.remove(me)
c24=bpy.data.collections.get(COLL_PIPE)
if c24:
    for o in list(c24.objects): rm(o)
for o in list(bpy.data.objects):
    if o.name.startswith("RH services"): rm(o)
OLD_FIX=("R2 lights fix lamp","R2 lamps task lamp face","R2 detail exit sign")
for o in list(bpy.data.objects):
    if o.name.startswith(OLD_FIX): rm(o)
# ------------------------------------------------------------------ materials (shared RH library + a handful of RH services materials)
M=rh_mats.lib()
def S(name,*a,**k): return rh_mats.surf(name,*a,**k)
M["PIPE"]=S("RH services pipe paint",(0.20,0.205,0.20),0.46,0.15,mottle=0.45,streak=0.2,edge=(0.42,0.43,0.41),grime=0.4,scale=2.5,bump=0.0)
M["OIL"]=S("RH services oil brown",(0.15,0.078,0.034),0.5,0.2,mottle=0.45,streak=0.15,edge=(0.34,0.17,0.06),grime=0.4,scale=2.5,bump=0.0)
M["WOOL"]=S("RH services mineral wool",(0.34,0.29,0.17),0.95,0.0,mottle=0.6,streak=0.0,grime=0.2,scale=6.0,bump=0.12)
M["CABLEG"]=S("RH services cable grey",(0.07,0.07,0.072),0.55,0.0,mottle=0.2,scale=3.0,bump=0.02)
M["LENS"]=rh_mats.emit("RH services lamp lens",(1.0,0.74,0.40),5.0)
M["EXITFACE"]=rh_mats.emit("RH services exit face",(0.85,0.85,0.78),0.9)
M["EXITGREEN"]=rh_mats.emit("RH services exit green",(0.10,0.80,0.18),2.2)
rs=bpy.data.objects.get("REACTOR_STATE"); crk.STATE=rs
if "RH services emergency lens" not in bpy.data.materials:
    em=crk.emit_mat("RH services emergency lens",(1.0,0.05,0.03),1.0,"0.5+3.5*min(1,2*(1-s))*(0.6+0.4*sin(T*5))",base=(0.05,0.005,0.004),use_s=True)
M["EMERG"]=bpy.data.materials["RH services emergency lens"]
# legacy blue-grey pipe material still used by the station pipe stubs (palette audit): neutralise its colours in place, name and node tree untouched
import colorsys as _cs
_lm=bpy.data.materials.get("R2 pipe coolant")
if _lm and _lm.node_tree:
    for _n in _lm.node_tree.nodes:
        for _i in _n.inputs:
            if _i.type=='RGBA' and not _i.is_linked:
                _h,_s,_v=_cs.rgb_to_hsv(*[max(0,min(1,x)) for x in _i.default_value[:3]])
                if 150<=_h*360<=310 and _s>0.22 and _v>0.02: _i.default_value=(_v*0.96,_v*0.97,_v*0.93,1.0)
KS=crk.Kit(); KL=crk.Kit()
G=lambda g,m: ("R2 PIPING "+g,m)
def band_key(c): return G("band",c)
SUP=G("support","STEEL"); SAD=G("saddle","STEEL"); CLP=G("clamp","GALV"); BLT=G("bolt","STEEL")
IRON=G("valve body","IRON")
OUT_VALVES=[]; HARD={}          # per run: list of (s, halfwidth)
# ------------------------------------------------------------------ generic pipe run
def nearest_s(path,pt):
    pt=Vector(pt); best=(1e9,0.0)
    for a,b,sa,sb in zip(path.P,path.P[1:],path.S,path.S[1:]):
        ab=b-a; l2=ab.length_squared
        if l2<1e-12: continue
        t=max(0,min(1,(pt-a).dot(ab)/l2)); q=a+ab*t; d=(q-pt).length
        if d<best[0]: best=(d,sa+(sb-sa)*t)
    return best[1]
def out_dir(P,T):
    """horizontal direction perpendicular to the pipe, pointing into the hall (away from the nearest wall)"""
    wd=wall_of(WALLS,P)
    n=Vector((wd[0].n.x,wd[0].n.y,0)) if wd else Vector((0,1,0))
    o=n-T*n.dot(T)
    if o.length<0.2: o=Vector((0,0,1)).cross(T)
    return o.normalized()
def pipe_run(name,path,rad,paint,bandc,lagspec=None,valves=(),extras=(),flanges=True,end_f=(True,True),joint_every=3.0,supports=True,ztop=None,arrows=True,bands=True,tees=(),sag=0.0,nobands=()):
    """path: Path; rad(s)->pipe radius; paint: material key; bandc: colour key for the identification bands and arrows;
    lagspec: dict(t,mat,end) jacket thickness; valves: [(point,kind,dict)], extras: [(point,'gauge'|'thermo'|'drain'|'drainside',dict)]"""
    L=path.L; hard=[(0.0,0.05),(L,0.05)]; plan=[]
    rmax=lambda s: rad(s)
    # --- valves and fixed fittings first (they define hard zones)
    for pt,kind,kw in valves:
        s=nearest_s(path,pt); r=rad(s); Lv=max(0.2,r*3.6 if kind=="check" else r*3.4) if kind!="ball" else max(0.1,r*3.0)
        plan.append(("valve",s,kind,kw)); hard.append((s,Lv/2+0.07))
    for pt,kind,kw in extras:
        s=nearest_s(path,pt); plan.append((kind,s,None,kw)); hard.append((s,0.07))
    for pt in tees: hard.append((nearest_s(path,pt),0.12))
    # --- flange joints along straights
    joints=[]
    if flanges and joint_every:
        # walk the straights between bends
        straights=[(a,b) for a,b in path.straights()]
        for a,b in straights:
            Ls=b-a; n=int(Ls/joint_every)
            for k in range(1,n+1):
                s=a+Ls*k/(n+1)
                for off in (0,0.3,-0.3,0.6,-0.6):
                    ss=s+off
                    if a+0.25<ss<b-0.25 and all(abs(ss-h)>w+0.18 for h,w in hard): joints.append(ss); hard.append((ss,0.1)); break
    # --- supports
    sups=[]
    if supports:
        for a,b in path.straights():
            Ls=b-a
            if Ls<0.9: continue
            n=max(1,int(math.ceil(Ls/2.3)))
            for k in range(n):
                s0=a+Ls*(k+0.5)/n
                for off in (0,0.2,-0.2,0.4,-0.4,0.6,-0.6,0.8,-0.8,1.0,-1.0):
                    ss=s0+off
                    if a+0.15<ss<b-0.15 and all(abs(ss-h)>w+0.05 for h,w in hard): sups.append(ss); break
    # --- sag (lagged horizontal spans only): displace dense points between supports
    d_pts,d_s=path.dense(0.2)
    # --- bare pipe body (sweep) in intervals not covered by the jacket
    cuts=[]
    lag_iv=[]
    if lagspec:
        t=lagspec["t"]; ends=lagspec.get("end",0.0)
        zones=[(h-w-0.06,h+w+0.06) for h,w in hard[2:]]       # lag stops around valves / fittings / joints / gauges
        zones+= [(s-0.17,s+0.17) for s in joints]
        zones+=[(0,lagspec.get("start",0.30)),(L-lagspec.get("stop",0.30),L)]
        for c in lagspec.get("cutouts",[]): zones.append((c-0.22,c+0.22))
        zones.sort(); iv=[]; cur=0.0
        for a,b in zones:
            if a>cur+0.12: iv.append((cur,a))
            cur=max(cur,b)
        if L>cur+0.12: iv.append((cur,L))
        lag_iv=iv
    def seg_pts(s0,s1,sagA=0.0,step=0.2):
        pts=path.slice(s0,s1)
        # refine
        dense=[pts[0]]
        for a,b in zip(pts,pts[1:]):
            n=max(1,int((b-a).length/step))
            for k in range(1,n+1): dense.append(a+(b-a)*(k/n))
        return dense
    bm=KS.get(G("pipe",paint)); seg=lambda r: max(10,min(28,int(r*220)))
    # body as one sweep with varying radius (reducers handled by rad(s))
    body_s=[0.0]; pts=seg_pts(0.0,L,0.0,0.18); ss=[0.0]
    for a,b in zip(pts,pts[1:]): ss.append(ss[-1]+(b-a).length)
    sweep(bm,pts,[rad(s) for s in ss],seg(max(rad(s) for s in ss)),False,False,True)
    # --- butt-weld beads where each forged bend meets its straights
    for (a_,b_) in path.arcs:
        for sv in (a_,b_):
            Pw,Tw=path.at(sv); KS.prism(G("pipe",paint),Vector(Pw)-Tw*0.007,Vector(Pw)+Tw*0.007,rad(sv)*1.05,rad(sv)*1.05,seg(rad(sv)),0.0,True,0.0)
    # --- lagging jackets
    if lagspec:
        for (a,b) in lag_iv:
            if b-a<0.15: continue
            lp=seg_pts(a,b,0.0,0.18); ls=[a]
            for p,q in zip(lp,lp[1:]): ls.append(ls[-1]+(q-p).length)
            # sag: dip gently between supports on horizontal parts
            lp2=[]
            for p,sv in zip(lp,ls):
                z=p.z
                if sag>0:
                    _,T=path.at(sv)
                    if abs(T.z)<0.2:
                        prev=max([x for x in sups if x<=sv]+[a-0.3]); nxt=min([x for x in sups if x>sv]+[b+0.3])
                        if nxt>prev: z-=sag*math.sin(math.pi*(sv-prev)/(nxt-prev))**1.0*min(1.0,(nxt-prev)/2.0)
                lp2.append(Vector((p.x,p.y,z)))
            t=lagspec["t"]; rl=lambda s: rad(s)+t
            lagkey=G("lag",lagspec["mat"]); lb=KS.get(lagkey); r0=rl(a); sg=max(14,min(30,int((r0)*200)))
            # end caps: tapered ring (jacket sweep tapers 4 cm at each end)
            radii=[]
            for i,sv in enumerate(ls):
                rr=rl(sv)
                radii.append(rr)
            sweep(lb,lp2,radii,sg,True,True,True)
            for (sv,dirn) in ((a,1),(b,-1)):
                P_,T_=path.at(sv); P_=Vector(P_)
                K=KS; K.prism(G("lag",lagspec["mat"]),P_-T_*0.0*dirn,P_+T_*(0.02*dirn),rl(sv)*1.06,rl(sv)*1.06,sg,0.0,True,0.0)    # end flange of the jacket
                if dirn>0: K.prism(G("lag band","STEEL"),P_+T_*0.03,P_+T_*0.05,rl(sv)*1.03,rl(sv)*1.03,sg,0.0,True,0.0)
                else: K.prism(G("lag band","STEEL"),P_-T_*0.03,P_-T_*0.05,rl(sv)*1.03,rl(sv)*1.03,sg,0.0,True,0.0)
            # metal banding every 0.45 m + seam rib
            n=int((b-a)/0.45)
            for k in range(1,n+1):
                sv=a+(b-a)*k/(n+1)
                if path.in_bend(sv,0.0): pass
                P_,T_=path.at(sv); P_=Vector(P_)
                # follow sag
                bandz=0.0
                if sag>0 and abs(T_.z)<0.2:
                    prev=max([x for x in sups if x<=sv]+[a-0.3]); nxt=min([x for x in sups if x>sv]+[b+0.3])
                    if nxt>prev: bandz=-sag*math.sin(math.pi*(sv-prev)/(nxt-prev))*min(1.0,(nxt-prev)/2.0)
                P_=P_+Vector((0,0,bandz)); rr=rl(sv)
                KS.prism(G("lag band","STEEL"),P_-T_*0.012,P_+T_*0.012,rr*1.025,rr*1.025,sg,0.0,True,0.0)
                u=Vector((0,0,1)) if abs(T_.z)<0.9 else Vector((1,0,0)); side=T_.cross(u).normalized()
                obox(KS,G("lag band","STEEL"),P_+side*(rr*1.03),T_,side,T_.cross(side).normalized(),0.02,0.012,0.012,0.002)           # buckle
            # cut-outs: show mineral wool and the pipe inside
        for c in lagspec.get("cutouts",[]):
            P_,T_=path.at(c); P_=Vector(P_); rr=rad(c)+lagspec["t"]
            KS.prism(G("wool","WOOL"),P_-T_*0.21,P_+T_*0.21,rr*0.97,rr*0.97,20,0.0,True,0.0)
            KS.prism(G("pipe",paint),P_-T_*0.2,P_+T_*0.2,rad(c)*1.0,rad(c)*1.0,seg(rad(c)),0.0,True,0.0)
            for sg_ in(-1,1): KS.prism(G("lag",lagspec["mat"]),P_+T_*(sg_*0.21),P_+T_*(sg_*0.225),rr*1.04,rr*1.04,20,0.0,True,0.0)
    # --- identification bands and flow arrows on the visible pipe (on the jacket where lagged)
    def covered(s):
        for a,b in lag_iv:
            if a<=s<=b: return True
        return False
    if bands:
        n=int(L/1.5)
        for k in range(1,n+1):
            s=L*k/(n+1)
            if path.in_bend(s,0.15) or any(abs(s-h)<w+0.12 for h,w in hard[2:]): continue
            if any(abs(s-x)<0.3 for x in nobands): continue
            P_,T_=path.at(s); P_=Vector(P_); r=rad(s)+(lagspec["t"]+0.004 if lagspec and covered(s) else 0)
            if sag>0 and lagspec and covered(s) and abs(T_.z)<0.2:
                prev=max([x for x in sups if x<=s]+[-1]); nxt=min([x for x in sups if x>s]+[L+1])
                if nxt>prev: P_=P_+Vector((0,0,-sag*math.sin(math.pi*(s-prev)/(nxt-prev))*min(1.0,(nxt-prev)/2.0)))
            band(KS,band_key(bandc),P_,T_,r,0.11)
            if arrows:
                up=Vector((0,0,1)) if abs(T_.z)<0.9 else out_dir(P_,T_)
                o=out_dir(P_,T_)
                nrm=o if abs(T_.z)>0.9 else (o if abs(o.z)>0.0 and False else Vector((0,0,1)))
                arrow(KS,band_key(bandc),P_+T_*0.22+nrm*(r+0.002),T_,nrm,L=min(0.42,max(0.26,r*4.2)),W=min(0.12,max(0.06,r*1.4)),t=0.005)
    # --- end flanges
    if flanges:
        for (s,sgn,en) in ((0.0,1,end_f[0]),(L,-1,end_f[1])):
            if not en: continue
            P_,T_=path.at(s); P_=Vector(P_); end_flange(KS,P_,T_*sgn,rad(s),G("flange","IRON"),G("bolt","STEEL"),G("gasket","RUBBER"))
        for s in joints:
            P_,T_=path.at(s); flange_pair(KS,Vector(P_),T_,rad(s),G("flange","IRON"),G("bolt","STEEL"),G("gasket","RUBBER"))
    # --- valves and extras
    for kind,s,k2,kw in plan:
        P_,T_=path.at(s); P_=Vector(P_); r=rad(s)
        up=Vector(kw.get("up",(0,0,1))); wk=kw.get("wheel","WHITE")
        if kind=="valve":
            if k2=="gate": gate_valve(KS,P_,T_,r,up,wk)
            elif k2=="check": check_valve(KS,P_,T_,r,up)
            elif k2=="ball": ball_valve(KS,P_,T_,r,up,G("lever",wk))
        elif kind=="gauge": gauge(KS,P_,Vector(kw.get("out",(0,1,0))),r+(lagspec["t"] if lagspec and covered(s) else 0))
        elif kind=="thermo": thermowell(KS,P_,Vector(kw.get("out",(0,0,1))),r+(lagspec["t"] if lagspec and covered(s) else 0))
        elif kind=="drain": drain(KS,P_,Vector((0,0,-1)),r,G("lever",kw.get("wheel","WHITE")))
        elif kind=="drainside": drain(KS,P_,Vector(kw.get("out",(0,1,0))),r,G("lever",kw.get("wheel","WHITE")),side=(0,0,1))
    # --- supports
    emitted=[]
    for s in sups:
        P_,T_=path.at(s); P_=Vector(P_); r=rad(s)+(lagspec["t"] if lagspec and covered(s) else 0)
        r=fitted_pipe_radius(KS,P_,T_,r)
        if sag>0 and lagspec and covered(s): pass
        vertical=abs(T_.z)>0.8
        wd=wall_of(WALLS,P_); d=wd[1] if wd else 9.0
        if wall_arm(KS,WALLS,P_,r,vertical,T_): emitted.append(s);continue
        if not vertical and P_.z-r<2.7:
            stanchion(KS,P_,r,SUP,SAD,BLT,0.0,T_);emitted.append(s)
        elif not vertical and ztop:
            hanger(KS,P_,r,ztop,SUP,CLP,BLT,T_);emitted.append(s)
    HARD[name]=(hard,emitted,joints); print('run %-28s L=%.2f supports=%d planned=%d joints=%d'%(name,L,len(emitted),len(sups),len(joints)))
    return sups,joints

def sleeve_wall(P,d,r,esc=True):
    """Hollow wall sleeve and bored escutcheon, with real wall bearing legs."""
    P=Vector(P);d=Vector(d).normalized();u,v,axis=fr(d)
    key=G('sleeve','IRON');bm=KS.get(key)
    def annulus(ri,ro,a,b):
        old=set(bm.verts)
        KS.lathe(key,0,0,[(ri,a),(ro,a),(ro,b),(ri,b),(ri,a)],seg=64)
        new=[p for p in bm.verts if p not in old];bmesh.ops.remove_doubles(bm,verts=new,dist=1e-7)
        for p in bm.verts:
            if p not in old:
                q=p.co.copy();p.co=P+u*q.x+v*q.y+d*q.z
    clamp_ring(KS,G('sleeve seal','IRON'),P+d*.04,d,fitted_pipe_radius(KS,P+d*.04,d,r),.025)
    w=r*3.6+.14;wall=service_wall_seat(P,d,w,w)
    backz=max(.112,(wall-P).dot(d)+.037);frontz=backz+.016
    annulus(r+.001,r*1.55+.015,-.18,max(.30,frontz+.02))
    annulus(r+.001,r*1.85+.025,frontz,frontz+.04)
    if esc:
        up=Vector((0,0,1));sd=d.cross(up).normalized();rings=[]
        for z,inner in ((backz,True),(backz,False),(frontz,False),(frontz,True)):
            ring=[]
            for i in range(64):
                a=2*math.pi*i/64;c,s=math.cos(a),math.sin(a)
                radius=r+.001 if inner else w/2/max(abs(c),abs(s))
                ring.append(bm.verts.new(P+d*z+sd*(radius*c)+up*(radius*s)))
            rings.append(ring)
        # Use the same outward-oriented annular winding as the shared lathe.
        for j in range(4):
            a=rings[j];b=rings[(j+1)%4]
            for i in range(64):
                q=(i+1)%64;f=bm.faces.new((a[i],a[q],b[q],b[i]))
                # Determine outwardness directly from the expected radial or
                # axial surface normal; no global/shared normal alteration.
                f.normal_update();mid=sum((p.co for p in f.verts),Vector())/4
                expected=-d if j==0 else d if j==2 else (mid-P-d*(mid-P).dot(d))*(1 if j==1 else -1)
                if f.normal.dot(expected)<0:f.normal_flip()
        wall_plate(KS,wall,d,w,w,.012,G('sleeve mount','STEEL'))
        for sx in (-1,1):
            for sz in (-1,1):
                off=sd*(sx*(w/2-.035))+up*(sz*(w/2-.035))
                back=P+d*backz+off;start=wall+d*.012+off
                KS.prism(G('sleeve mount','STEEL'),start,back-d*.004,.009,.009,12,0,True,0)
                obox(KS,G('sleeve mount','STEEL'),back-d*.004,sd,up,d,.012,.012,.004,0)
                SUPPORT.register('piping supports','escutcheon onto wall legs','RH services R2 PIPING sleeve IRON','RH services R2 PIPING sleeve mount STEEL',[back],-d,'wall')
                hexnut(KS,BLT,P+d*frontz+off,d,.0095,.012)

def R(name): return RUN[name]
def P3(name): return [Vector(p) for p in R(name)["pts"]]
def tee_at(name,pt,rh): 
    pts=P3(name); d=(pts[1]-pts[0]).normalized(); tee_boss(KS,pts[0],d,{"EC-1 feed":0.032,"EC-2 feed":0.032}.get(name,0.03),rh,G("flange","IRON"))
# ================================================================== 1. coolant: supply header + pump suction (one continuous chain), EC feeds, injection lines
hdr=P3("coolant supply header"); suc=P3("pump suction via isolation valves")
chain=hdr+suc[1:]
cpath=Path(chain,0.30); s_junction=nearest_s(cpath,hdr[-1])
RH_HDR=0.085; RH_SUC=0.062
def crad(s):
    if s<s_junction-0.25: return RH_HDR
    if s>s_junction+0.1: return RH_SUC
    t=(s-(s_junction-0.25))/0.35; return RH_HDR+(RH_SUC-RH_HDR)*max(0,min(1,t))
chain_valves=[((4.15,-10.28,3.9),"gate",dict(up=(0,0,1),wheel="WHITE")),((0.55,-9.49,2.65),"gate",dict(up=(0,1,0),wheel="WHITE"))]
chain_extras=[((2.55,-10.28,3.9),"gauge",dict(out=(0,1,0))),((1.1,-10.28,3.9),"thermo",dict(out=(0,0,1))),((-0.55,-9.49,1.1),"drain",dict(wheel="WHITE"))]
pipe_run("coolant chain",cpath,crad,"PIPE","WHITE",lagspec=dict(t=0.045,mat="GALV",start=0.55,stop=0.0,cutouts=[]),
         valves=chain_valves,extras=chain_extras,tees=[(3.3,-10.28,3.9),(1.8,-10.28,3.9)],sag=0.016,ztop=None,end_f=(False,True))
# the jacket must stop at the elbow into the suction: re-run lag limits through lagspec 'stop' handled by hard zones; wall penetration
sleeve_wall(Vector((5.0,-10.8,3.9)),(0,1,0),RH_HDR)
for tag,x in (("EC-1",3.3),("EC-2",1.8)):
    pts=P3(f"{tag} feed"); pth=Path(pts,0.20)
    pipe_run(f"{tag} feed",pth,lambda s:0.032,"PIPE","WHITE",valves=[((x,-9.65,3.35),"gate",dict(up=(0,1,0),wheel="WHITE"))],extras=[],tees=[],flanges=True,end_f=(False,True),supports=True,joint_every=0)
    tee_boss(KS,pts[0],(pts[1]-pts[0]).normalized(),0.032,RH_HDR+0.045,G("flange","IRON"))
    pts=P3(f"{tag} injection line"); pth=Path(pts,0.1)
    pipe_run(f"{tag} injection line",pth,lambda s:0.038,"PIPE","WHITE",extras=[((x,-10.66,1.05),"gauge",dict(out=(0,0,1)))],end_f=(True,False),joint_every=0,supports=False,bands=False,arrows=False)
    sleeve_wall(Vector((x,-10.8,1.05)),(0,1,0),0.038)
# ================================================================== 2. pump discharge, trench, pool inlet
pts=P3("pump discharge"); pth=Path(pts,0.22)
pipe_run("pump discharge",pth,lambda s:0.046,"PIPE","WHITE",valves=[((-2.75,-9.5,1.72),"check",dict(up=(1,0,0))),((-2.75,-8.72,2.3),"gate",dict(up=(0,0,1),wheel="WHITE"))],
         extras=[((-2.75,-9.0,2.3),"gauge",dict(out=(0,0,1)))],end_f=(True,True),supports=False,joint_every=2.8)
# L-frame: post beside the drop leg with two clamps and an outrigger under the corner
px,py=-1.82,-8.15
obox(KS,SUP,(px,py,1.2),(1,0,0),(0,1,0),(0,0,1),0.04,0.04,1.2,0.003); obox(KS,SUP,(px,py,0.006),(1,0,0),(0,1,0),(0,0,1),0.12,0.12,0.006,0.002)
for sx in(-1,1):
    for sy in(-1,1): hexnut(KS,BLT,(px+sx*0.085,py+sy*0.085,0.016),(0,0,1),0.0095,0.013)
bar(KS,SUP,(px,py,2.2),(-2.75,-8.45,2.2),0.05,0.05,(0,0,1),0.003); bar(KS,SUP,(px,py,1.55),(px-0.55,py,2.15),0.035,0.025,(0,0,1),0.002)
obox(KS,SAD,(-2.75,-8.45,2.2+0.025+0.012),(1,0,0),(0,1,0),(0,0,1),0.06,0.035,0.012,0.002); clamp_ring(KS,CLP,Vector((-2.75,-8.45,2.3)),(0,1,0),0.046,0.04)
for z in(0.75,1.5):
    bar(KS,SUP,(px,py,z),(-2.1+0.058,py,z),0.04,0.04,(0,0,1),0.002); clamp_ring(KS,CLP,Vector((-2.1,py,z)),(0,0,1),0.046,0.04)
SUPPORT.register('piping supports','pump discharge L frame floor','RH services R2 PIPING support STEEL','R2 floor',[(px+sx*.085,py+sy*.085,0) for sx in (-1,1) for sy in (-1,1)])
# trench box, cover plates, pool inlet manifold
def trench_box(c,sz=0.55):
    x,y=c
    obox(KS,G("trench","STEEL"),(x,y,0.07),(1,0,0),(0,1,0),(0,0,1),sz/2,sz/2,0.07,0.012)
    obox(KS,G("trench","GALV"),(x,y,0.155),(1,0,0),(0,1,0),(0,0,1),sz/2+0.015,sz/2+0.015,0.015,0.004)
    for sx in(-1,1):
        for sy in(-1,1):
            hexnut(KS,BLT,(x+sx*(sz/2-0.03),y+sy*(sz/2-0.03),0.178),(0,0,1),0.012,0.014)
    KS.prism(G("flange","IRON"),(x,y,0.17),(x,y,0.205),0.098,0.098,18,0.0,True,0.0)
    for i in range(6):
        a=2*math.pi*(i+0.5)/6; hexnut(KS,BLT,(x+math.cos(a)*0.075,y+math.sin(a)*0.075,0.212),(0,0,1),0.0105,0.014)
    for s in(-1,1): obox(KS,G("trench","GALV"),(x+s*(sz/2+0.02),y,0.07),(1,0,0),(0,1,0),(0,0,1),0.012,0.05,0.035,0.002)    # lifting lugs
def trench(p0,p1):
    L=math.hypot(p1[0]-p0[0],p1[1]-p0[1]); ang=math.atan2(p1[1]-p0[1],p1[0]-p0[0]); cx,cy=(p0[0]+p1[0])/2,(p0[1]+p1[1])/2
    ux,uy=math.cos(ang),math.sin(ang); nx,ny=-uy,ux
    n=max(1,int(round(L/1.0)))
    for i in range(n):
        t0=-L/2+L*i/n; t1=-L/2+L*(i+1)/n; tc=(t0+t1)/2; lp=t1-t0-0.012
        x=cx+ux*tc; y=cy+uy*tc
        KS.box(G("trench cover","GALV"),x,y,0.0,0.028,lp,0.5,ang,0.004)
        for k in range(-3,4): KS.box(G("trench cover rib","GALV"),x+nx*k*0.062,y+ny*k*0.062,0.028,0.034,lp-0.05,0.012,ang,0.002)
        for s in(-1,1): KS.cyl(G("trench cover lug","IRON"),x+ux*s*lp*0.36,y+uy*s*lp*0.36,0.026,0.032,0.022,10,0.0)
    for s in(-1,1):
        KS.box(G("trench frame","STEEL"),cx+nx*s*0.26,cy+ny*s*0.26,0.0,0.05,L+0.04,0.035,ang,0.003)
trench_box((-2.1,-8.15)); trench((-2.1,-8.15),(-2.1,-6.5)); trench((-2.1,-6.5),(-1.4,-4.9))
# pool inlet manifold
mx,my=-1.4,-4.9
obox(KS,G("trench","STEEL"),(mx,my,0.19),(1,0,0),(0,1,0),(0,0,1),0.26,0.26,0.19,0.015)
obox(KS,G("trench","GALV"),(mx,my,0.39),(1,0,0),(0,1,0),(0,0,1),0.32,0.32,0.02,0.005)
obox(KS,G("trench","STEEL"),(mx,my,0.02),(1,0,0),(0,1,0),(0,0,1),0.33,0.33,0.02,0.004)
for sx in(-1,1):
    for sy in(-1,1):
        hexnut(KS,BLT,(mx+sx*0.28,my+sy*0.28,0.415),(0,0,1),0.012,0.014); hexnut(KS,BLT,(mx+sx*0.29,my+sy*0.29,0.05),(0,0,1),0.012,0.012)
for k in(-1,0,1): obox(KS,G("trench","STEEL"),(mx+k*0.14,my-0.265,0.19),(1,0,0),(0,1,0),(0,0,1),0.012,0.012,0.17,0.002)
pts=P3("pool inlet"); pth=Path(pts,0.22)
pipe_run("pool inlet",pth,lambda s:0.05,"PIPE","WHITE",end_f=(True,False),supports=False,joint_every=0,bands=True)
# Two narrow beams bridge the drain beneath the outer inlet support. Their
# inner ends bear on the coping step; outer standoffs bear on solid slab.
inlet_bridge=G('pool inlet bridge','STEEL')
for yy in (-4.02,-4.18):
    inner=-math.sqrt(4.195**2-yy**2);outer=-math.sqrt(4.58**2-yy**2)
    KS.box(inlet_bridge,(inner+outer)/2,yy,.10,.12,inner-outer+.04,.03,0,.002)
    KS.cyl(inlet_bridge,outer,yy,0,.10,.025,16,0)
    SUPPORT.register('piping supports','inlet bridge inner bearing','RH services R2 PIPING pool inlet bridge STEEL',
        'RH pool coping CONC_POUR',[(inner,yy,.10)])
    SUPPORT.register('piping supports','inlet bridge outer foot','RH services R2 PIPING pool inlet bridge STEEL','R2 floor',[(outer,yy,0)])
for yy in(-4.1,-3.5):
    stanchion(KS,Vector((-1.4,yy,0.32)),0.05,SUP,SAD,BLT,.20 if yy==-3.5 else .12,Vector((0,1,0)),
        target='RH pool coping CONC_POUR' if yy==-3.5 else 'RH services R2 PIPING pool inlet bridge STEEL')
for z in(-0.3,-1.6):
    P_=Vector((-1.4,-3.0,z)); clamp_ring(KS,CLP,P_,(0,0,1),0.05,0.045); rad_=Vector((-1.4,-3.0,0)).normalized()
    bar(KS,SUP,P_+rad_*0.05,P_+rad_*0.12,0.04,0.04,(0,0,1),0.002)
# diffuser head (submerged)
KS.prism(G("diffuser","STEEL"),(-1.4,-3.0,-3.28),(-1.4,-3.0,-2.98),0.17,0.17,20,0.0,True,0.0)
KS.prism(G("flange","IRON"),(-1.4,-3.0,-3.0),(-1.4,-3.0,-2.96),0.12,0.12,18,0.0,True,0.0)
for k in range(5): KS.prism(G("diffuser slot","BLACK"),(-1.4,-3.0,-3.23+k*0.05),(-1.4,-3.0,-3.215+k*0.05),0.172,0.172,20,0.0,True,0.0)
# ================================================================== 3. steam supply, turbine exhaust
pts=P3("steam supply"); pth=Path(pts,0.34)
pipe_run("steam supply",pth,lambda s:0.088,"PIPE","ORANGE",lagspec=dict(t=0.06,mat="GALV",start=1.05,stop=0.95,cutouts=[3.0]),
         valves=[((10.38,-3.8,6.4),"gate",dict(up=(0,0,1),wheel="ORANGE"))],extras=[((10.7,-3.8,6.4),"gauge",dict(out=(0,-1,0))),((9.6,-3.8,2.78),"drainside",dict(out=(-1,0,0),wheel="ORANGE"))],
         end_f=(False,True),joint_every=2.6,sag=0.02,nobands=[])
sleeve_wall(Vector((10.8,-3.8,6.4)),(-1,0,0),0.088)
pts=P3("turbine exhaust"); pth=Path(pts,0.1)
pipe_run("turbine exhaust",pth,lambda s:0.11,"PIPE","ORANGE",end_f=(True,False),joint_every=0,supports=False,bands=False,arrows=False)
sleeve_wall(Vector((10.8,-3.3,1.15)),(-1,0,0),0.11)
# orange identification collar on the exhaust stub
band(KS,band_key("ORANGE"),Vector((10.68,-3.3,1.15)),Vector((1,0,0)),0.11,0.08)
# ================================================================== 4. waste vent (yellow gas line), bank hydraulics
pts=P3("waste vent"); pth=Path(pts,0.24)
pipe_run("waste vent",pth,lambda s:0.03,"YELLOW","BLACK",valves=[((7.6,8.2,3.45),"ball",dict(up=(1,0,0),wheel="BLACK"))],extras=[((7.6,8.2,4.2),"gauge",dict(out=(0.707,-0.707,0)))],
         end_f=(True,False),joint_every=2.0,bands=True)
sleeve_wall(Vector((8.1,8.7,5.2)),(-0.707,-0.707,0),0.03)
# Outboard service arms mount to the actual gantry web. The original rods
# terminated above empty space at y1.7–2.3 instead of meeting the girders.
for xx,width in ((-.475,.20),(1.45,.15),(.45,.04)):
    for sg in (-1,1):
        key=G('gantry service mounts','STEEL')
        obox(KS,key,(xx,sg*.536,13.83),(1,0,0),(0,1,0),(0,0,1),max(.06,width*.55),.006,.12,.002)
        KS.box(key,xx,sg*1.501,13.80,13.86,width,1.918,0,.002)
        bar(KS,key,Vector((xx,sg*.542,13.72)),Vector((xx,sg*.80,13.80)),.03,.018,(1,0,0),.002)
        SUPPORT.register('piping gantry mounts','gantry web bracket '+str((xx,sg)),
            'RH services R2 PIPING gantry service mounts STEEL','RH pool girder YELLOW',
            [(xx+dx,sg*.530,z) for dx in (-.035,.035) for z in (13.76,13.90)],(0,-sg,0),'wall')
for tag,sgn,bx in (("AN",1,-1.4),("AS",-1,-1.4),("BN",1,1.4),("BS",-1,1.4)):
    pts=P3(f"hydraulic {tag}"); pth=Path(pts,0.14)
    pipe_run(f"hydraulic {tag}",pth,lambda s:0.026,"OIL","WHITE",end_f=(True,False),joint_every=0,supports=False,ztop=None,arrows=True)
    # hanger rod to the gantry deck above the horizontal run
    e=pts[-1]; p4=pts[-2]; mid=(e+p4)/2
    hanger(KS,Vector(mid),0.026,13.80,SUP,CLP,BLT,(e-p4).normalized())
    axis=(e-p4).normalized();side=axis.cross(Vector((0,0,1))).normalized()
    SUPPORT.register('piping gantry mounts','hydraulic hanger '+tag,'RH services R2 PIPING support STEEL',
        'RH services R2 PIPING gantry service mounts STEEL',
        [Vector((mid.x,mid.y,13.80))+side*(s*.051) for s in (-1,1)],(0,0,1),'suspension')
    # fitting block where the line meets the tank / skid
    d=(e-p4).normalized(); KS.box(G("fitting","IRON"),e.x+d.x*0.06,e.y+d.y*0.06,e.z-0.07,e.z+0.07,0.16 if abs(d.x)>0.5 else 0.14,0.12 if abs(d.x)>0.5 else 0.16,0.0,0.01)
# hydraulic power pack and return tank, hung from the gantry deck
def tank(cy,motor):
    cx=0.0
    KS.box(G("hpu","STEEL"),cx,cy,12.55,12.62,1.20,0.60,0.0,0.01)              # skid frame
    KS.box(G("hpu","PIPE"),cx,cy,12.62,13.40,1.16,0.56,0.0,0.02)               # tank body
    KS.box(G("hpu","STEEL"),cx,cy,13.40,13.45,1.20,0.60,0.0,0.01)              # top plate
    for k in range(-2,3):
        for s in(-1,1): KS.box(G("hpu","STEEL"),cx+k*0.24,cy+s*0.292,12.66,13.38,0.04,0.012,0.0,0.002)    # stiffener ribs
    for s in(-1,1): KS.box(G("hpu","STEEL"),cx+s*0.592,cy,12.66,13.38,0.012,0.4,0.0,0.002)
    # level sight gauge, filler cap, breather
    sgn=1 if cy>0 else -1
    KS.box(G("hpu gauge","BLACK"),cx+0.38,cy-sgn*0.30,12.78,13.30,0.06,0.016,0.0,0.002); KS.box(G("hpu gauge","WHITE"),cx+0.38,cy-sgn*0.309,12.84,13.22,0.034,0.004,0.0,0.001)
    KS.cyl(G("hpu","IRON"),cx-0.3,cy,13.45,13.52,0.05,14,0.0); KS.cyl(G("hpu","GALV"),cx-0.3,cy,13.52,13.56,0.04,10,0.0)
    if motor:
        KS.prism(G("hpu motor","YELLOW"),(cx-0.2,cy,13.60),(cx+0.35,cy,13.60),0.11,0.11,18,0.0,True,0.0)
        for k in range(8): KS.prism(G("hpu motor","YELLOW"),(cx-0.15+k*0.055,cy,13.60),(cx-0.15+k*0.055+0.012,cy,13.60),0.122,0.122,18,0.0,True,0.0)
        obox(KS,G("hpu","IRON"),(cx+0.46,cy,13.57),(1,0,0),(0,1,0),(0,0,1),0.1,0.09,0.09,0.008)
        obox(KS,G("hpu","IRON"),(cx-0.2,cy,13.5),(1,0,0),(0,1,0),(0,0,1),0.14,0.1,0.02,0.004)
    # hanger rods to the gantry deck
    for x in(-0.45,0.45):
        for yy in(cy-0.2*sgn,cy+0.2*sgn):
            KS.prism(G("hpu","STEEL"),(x,yy,13.45),(x,yy,13.80),0.016,0.016,8,0.0,True,0.0)
            SUPPORT.register('piping gantry mounts','hydraulic tank hanger '+str((x,yy)),
                'RH services R2 PIPING hpu STEEL','RH services R2 PIPING gantry service mounts STEEL',
                [(x,yy,13.80)],(0,0,1),'suspension')
            hexnut(KS,BLT,(x,yy,13.47),(0,0,1),0.026,0.02); hexnut(KS,BLT,(x,yy,13.44),(0,0,1),0.026,0.02)
tank(2.1,True); tank(-2.1,False)
# ================================================================== 4b. red fire main along the north wall (new run: not part of the verified process manifest, decorative service with a blind tee)
fpts=[Vector(p) for p in ((2.9,10.95,8.9),(2.9,10.25,8.9),(-5.4,10.25,8.9),(-5.4,10.95,8.9))]
fpath=Path(fpts,0.26)
pipe_run("fire main",fpath,lambda s:0.057,"RED","WHITE",valves=[((0.6,10.25,8.9),"gate",dict(up=(0,0,1),wheel="YELLOW"))],extras=[((-2.8,10.25,8.9),"gauge",dict(out=(0,-1,0)))],end_f=(False,False),joint_every=2.6)
sleeve_wall(Vector((2.9,10.8,8.9)),(0,-1,0),0.057); sleeve_wall(Vector((-5.4,10.8,8.9)),(0,-1,0),0.057)
tee_boss(KS,Vector((-1.4,10.25,8.9)),Vector((0,0,-1)),0.04,0.057,G("flange","IRON"))
KS.prism(G("flange","IRON"),Vector((-1.4,10.25,8.9-0.1)),Vector((-1.4,10.25,8.9-0.22)),0.04,0.04,14,0.0,True,0.0)
flange_pair(KS,Vector((-1.4,10.25,8.9-0.27)),Vector((0,0,-1)),0.04)
KS.prism(G("flange","IRON"),Vector((-1.4,10.25,8.9-0.30)),Vector((-1.4,10.25,8.9-0.325)),0.09,0.09,16,0.0,True,0.0)
# drip trays under the heavier valves on horizontal runs
drip_tray(KS,Vector((4.15,-10.28,3.9)),0.14,0.5,0.34,G("drip tray","GALV"),SUP,0.0)
drip_tray(KS,Vector((10.38,-3.8,6.4)),0.15,0.5,0.34,G("drip tray","GALV"),SUP,0.0)
drip_tray(KS,Vector((-2.75,-8.72,2.3)),0.075,0.34,0.5,G("drip tray","GALV"),SUP,math.pi/2)
# ================================================================== 5. cable ring with ladder tray, covers, splice plates, clamps and bundles
lines=[(w.P+w.n*DI,w.t) for w in WALLS]
def inter(l1,l2):
    p,d=l1; q,e=l2; det=d.x*(-e.y)+e.x*d.y
    t=((q.x-p.x)*(-e.y)+e.x*(q.y-p.y))/det; return p+d*t
def offset_ring(off):
    ls=[(w.P+w.n*DI+w.n*off,w.t) for w in WALLS]
    return [Vector((inter(ls[i-1],ls[i]).x,inter(ls[i-1],ls[i]).y,0.0)) for i in range(8)]
ring=offset_ring(0.0); RL=offset_ring(-0.23); RR=offset_ring(0.23)       # tray centre, wall-side rail, hall-side rail (corner i = start of wall i)
GAL=G("tray","GALV"); TRD=G("tray dark","STEEL")
for i in range(8):
    j=(i+1)%8; a=ring[i]; b=ring[j]; d=(b-a); L=d.length; d.normalize(); ang=math.atan2(d.y,d.x); w=WALLS[i]; nn=Vector((w.n.x,w.n.y,0.0))
    for rail,off in ((RL,-0.23),(RR,0.23)):
        p0=rail[i]; p1=rail[j]; ln=(p1-p0).length; c=(p0+p1)/2
        KS.box(GAL,c.x,c.y,Z_RING+0.0,Z_RING+0.115,ln,0.004,ang,0.0015)                       # web
        KS.box(GAL,c.x-nn.x*0.0+(nn.x*(0.014 if off<0 else -0.014)),c.y+(nn.y*(0.014 if off<0 else -0.014)),Z_RING+0.111,Z_RING+0.115,ln,0.032,ang,0.0015)   # top return lip
        KS.box(GAL,c.x+(nn.x*(0.014 if off<0 else -0.014)),c.y+(nn.y*(0.014 if off<0 else -0.014)),Z_RING,Z_RING+0.004,ln,0.032,ang,0.0015)
    # rungs every 0.3 m between the rails
    n=int((L-0.4)/0.30)
    for k in range(n+1):
        t=0.2+(L-0.4)*k/max(1,n); q=a+d*t
        KS.box(TRD,q.x,q.y,Z_RING+0.012,Z_RING+0.032,0.03,0.43,ang,0.0)
    # brackets: cantilever arm to the wall, diagonal brace, plate with bolts (every ~2.4 m); splice plates at both ends
    nb=max(1,int(L/2.4)+1)
    for k in range(nb):
        t=L*(k+0.5)/nb; q=a+d*t; base=q-nn*DI
        for s in(-0.15,0.15):
            qq=q+d*s; bb=qq-nn*DI
            seat=service_wall_seat(Vector((bb.x,bb.y,Z_RING-.17)),Vector((nn.x,nn.y,0)),.1,.3)
            bb.x,bb.y=seat.x,seat.y
            bearing=Vector((qq.x,qq.y,Z_RING-.045))
            # Wall seats can shift sideways to a mullion. The diagonal arm
            # meets a separate straight boom beneath both ladder rails.
            bar(KS,TRD,Vector((bb.x,bb.y,Z_RING-.045))+nn*.012,bearing-nn*.27,0.05,0.045,(0,0,1),0.003)
            bar(KS,TRD,bearing-nn*.27,bearing+nn*.27,0.05,0.045,(0,0,1),0.003)
        for s in(-0.15,0.15):
            bb=q+d*s-nn*DI
            seat=service_wall_seat(Vector((bb.x,bb.y,Z_RING-.17)),Vector((nn.x,nn.y,0)),.1,.3)
            bb.x,bb.y=seat.x,seat.y
            wall_plate(KS,Vector((bb.x,bb.y,Z_RING-0.17)),Vector((nn.x,nn.y,0)),0.1,0.3,0.012,SUP)
            bar(KS,TRD,Vector((bb.x,bb.y,Z_RING-0.40))+nn*0.012,Vector((bb.x,bb.y,Z_RING-0.045))+nn*0.62,0.04,0.028,(0,0,1),0.002)
        # Both cantilever arms directly bear both ladder rails.
        # The former center cross-channel never met the two side arms.
        for station in (-.15,.15):
            for offset in (-.23,.23):
                seat=q+d*station+nn*offset
                KS.box(G('tray seats','STEEL'),seat.x,seat.y,Z_RING-.0225,Z_RING,.050,.032,ang,0)
                SUPPORT.register('piping supports','tray seat onto cantilever arm','RH services R2 PIPING tray seats STEEL','RH services R2 PIPING tray dark STEEL',[(seat.x,seat.y,Z_RING-.0225)])
                SUPPORT.register('piping supports','tray rail onto seat','RH services R2 PIPING tray GALV','RH services R2 PIPING tray seats STEEL',[(seat.x,seat.y,Z_RING)])
    for end in (a+d*0.0,):
        pass
    # splice plates at the mitre joints (both rails) with 4 bolts each
for i in range(8):
    for rail,off in ((RL,-0.23),(RR,0.23)):
        p=rail[i]; w=WALLS[i]; ang=math.atan2(WALLS[i].t.y,WALLS[i].t.x)
        KS.box(CLP,p.x,p.y,Z_RING+0.02,Z_RING+0.098,0.28,0.01,ang+math.radians(22.5)*(1),0.001)
        for s in(-1,1):
            for z in(0.04,0.08): hexnut(KS,BLT,Vector((p.x,p.y,Z_RING+z))+Vector((math.cos(ang+math.radians(22.5)),math.sin(ang+math.radians(22.5)),0))*(s*0.09)+Vector((math.sin(ang+math.radians(22.5)),-math.cos(ang+math.radians(22.5)),0))*(0.008*(-1 if off<0 else 1)),Vector((math.sin(ang+math.radians(22.5)),-math.cos(ang+math.radians(22.5)),0)),0.008,0.01)
# cables: parallel sweeps around the loop at four offsets, rounded at the mitres; ties (cleats) every metre; covers on some spans
def loop(off):
    r=offset_ring(off); pts=[]
    mid=(r[0]+r[1])/2
    pts=[Vector((mid.x,mid.y,Z_RING+0.056))]+[Vector((r[k%8].x,r[k%8].y,Z_RING+0.056)) for k in range(1,9)]+[Vector((mid.x,mid.y,Z_RING+0.056))]
    return Path(pts,0.28,6)
for off,rr,mk in ((-0.17,0.024,"BLACK"),(-0.085,0.02,"CABLEG"),(0.085,0.024,"BLACK"),(0.17,0.02,"CABLEG")):
    lp=loop(off); pts,_=lp.dense(0.4)
    sweep(KS.get(G("cable",mk)),pts,[rr]*len(pts),8,False,False,True)
for i in range(8):
    j=(i+1)%8; a=ring[i]; b=ring[j]; d=(b-a); L=d.length; d.normalize(); ang=math.atan2(d.y,d.x)
    for k in range(int(L/1.0)):
        t=0.5+k*1.0
        if t>L-0.4: break
        q=a+d*t; KS.box(G("cable tie","BLACK"),q.x,q.y,Z_RING+0.082,Z_RING+0.094,0.012,0.40,ang,0.0)
        KS.box(G("cable tie","BLACK"),q.x,q.y,Z_RING+0.094,Z_RING+0.102,0.024,0.02,ang,0.001)
    # a perforated cover on every third wall, held by clips; louvre slots modelled as ribs
    if i%3==1:
        n=int((L-0.6)/0.02)
        c=(a+b)/2; cl=L*0.55
        KS.box(GAL,c.x,c.y,Z_RING+0.118,Z_RING+0.124,cl,0.50,ang,0.002)
        for k in range(-int(cl/0.35/2),int(cl/0.35/2)+1):
            q=c+d*(k*0.35); KS.box(TRD,q.x,q.y,Z_RING+0.124,Z_RING+0.131,0.02,0.50,ang,0.001)
        for s in(-1,1):
            for k in(-1,0,1):
                q=c+d*(s*cl*0.48)+Vector((-d.y,d.x,0))*(k*0.2); KS.cyl(BLT,q.x,q.y,Z_RING+0.124,Z_RING+0.133,0.009,6,0.0)
# ================================================================== 6. conduit risers, junction boxes, clips and wall ties
RING_Z=Z_RING+0.03
def nearest_ring(p):
    best=None
    for i in range(8):
        a=ring[i]; b=ring[(i+1)%8]; ab=b-a; t=max(0,min(1,(Vector((p[0],p[1],0))-a).dot(ab)/ab.length_squared)); q=a+ab*t; dd=(q-Vector((p[0],p[1],0))).length
        if best is None or dd<best[0]: best=(dd,q,i)
    return best
CR=0.021
_junction_hosts=[]
for _o in bpy.data.objects:
    if _o.type!='MESH':continue
    if not (_o.name.startswith('RH stations') or _o.name.startswith('RH walls')):continue
    if any(t in _o.name.upper() for t in ('GLASS','LENS','BRASS','BOLT','TEXT')):continue
    if not _o.data.polygons:continue
    _junction_hosts.append((_o.name,BVHTree.FromPolygons([_o.matrix_world@v.co for v in _o.data.vertices],[list(p.vertices) for p in _o.data.polygons])))

def junction_box(P0,d,label):
    # Seat the box outside a real casing/wall face, retaining the port and
    # connecting it with a gland stub. Legacy centers put several boxes inside
    # casing sheets; a mount cannot repair that intersection.
    original=P0-d*.02;options=[]
    for host,tree in _junction_hosts:
        if not any(t in host for t in ('AUDI','IRON','STEEL','concrete','mass','cladding')):continue
        faces={}
        for loc,n,idx,dist in tree.find_nearest_range(original,.9):
            key=tuple(round(float(q),3) for q in n)+(round(n.dot(loc),3),)
            if key not in faces or dist<faces[key][3]:faces[key]=(loc,n,idx,dist)
        for loc,n,idx,dist in sorted(faces.values(),key=lambda h:h[3])[:32]:
            n.normalize();u,v,axis=fr(n)
            for du,dv in ((0,0),(.05,0),(-.05,0),(0,.05),(0,-.05),(.15,0),(-.15,0),(0,.15),(0,-.15),(.3,0),(-.3,0),(0,.3),(0,-.3)):
                face=loc+u*du+v*dv;back=face+n*.025;contacts=[]
                for side in (-1,1):
                    p=back+u*(side*.035)
                    hit,hn,idx,dd=tree.ray_cast(p+n*.001,-n,.15)
                    if hit is None or hn.dot(n)<.98:break
                    contacts.append((p,hit,hn))
                if len(contacts)==2:options.append(((back-original).length,host,n.copy(),u.copy(),v.copy(),back,contacts))
    if not options:raise RuntimeError('No two seated junction bearings '+label)
    _,host,n,u,v,back,contacts=min(options,key=lambda h:h[0]);center=back+n*.05
    obox(KS,G('jbox','STEEL'),center,u,v,n,.085,.065,.05,.006)
    mount=G('junction mounts','STEEL');target='RH services R2 PIPING junction mounts STEEL'
    for side,(p,hit,hn) in zip((-1,1),contacts):
        obox(KS,mount,p-n*.004,u,v,n,.013,.013,.004,0)
        hu,hv,ha=fr(hn);obox(KS,mount,hit+hn*.004,hu,hv,hn,.013,.013,.004,0)
        KS.prism(mount,p-n*.004,hit+hn*.004,.009,.009,12,0,True,0)
        SUPPORT.register('piping supports',label+' case onto mount','RH services R2 PIPING jbox STEEL',target,[p],-n,'wall')
        SUPPORT.register('piping supports',label+' mount onto host',target,host,[hit],-hn,'wall')
        hexnut(KS,BLT,center+n*.055+u*(side*.06),n,.008,.008)
    KS.prism(G('jbox','IRON'),P0,center,CR*1.5,CR*1.5,12,0,True,0)
    print('junction mounted',label,host,'center',tuple(center))

def conduit(name,jbox=True,drop=True,ties=True):
    pts=P3(name); pth=Path(pts,0.14)
    sweep(KS.get(G("conduit","GALV")),pth.dense(0.4)[0],[CR]*len(pth.dense(0.4)[0]),8,False,False,True)
    L=pth.L
    # clips every ~0.9 m on straights
    n=int(L/0.9)
    for k in range(1,n+1):
        s=L*k/(n+1)
        if pth.in_bend(s,0.1): continue
        P_,T_=pth.at(s); P_=Vector(P_); clamp_ring(KS,G("clip","GALV"),P_,T_,CR,0.016)
        u=Vector((0,0,1)) if abs(T_.z)<0.9 else Vector((1,0,0)); sd=T_.cross(u).normalized()
        for sg in(-1,1): hexnut(KS,BLT,P_+sd*(sg*(CR*1.18)),sd,0.005,0.006)
    # wall ties on tall verticals
    for k in range(1,int(L/2.6)+1):
        s=L*k/(int(L/2.6)+1); P_,T_=pth.at(s); P_=Vector(P_)
        if abs(T_.z)>0.8 and not pth.in_bend(s,0.2): wall_arm(KS,WALLS,P_,CR,True,T_,maxd=1.7)
    if jbox:                                              # junction box where the conduit leaves the equipment
        P0=pts[0]; d=(pts[1]-pts[0]).normalized()
        junction_box(P0,d,name)
    return pth
for nm in ("riser grid cabinets","riser turbine sensor","riser generator","riser bank control","riser control room","riser elevator machine","riser west bench","riser reserve power A","riser reserve power B"):
    pth=conduit(nm,jbox=(nm not in ("riser control room","riser west bench")))
    e=pth.P[-1]; d=Vector((0,0,1))
    # drop-out under the tray: sheet-steel chute box and flared bell mouth where the cable leaves the conduit
    obox(KS,G("dropout","STEEL"),Vector((e.x,e.y,Z_RING-0.09)),(1,0,0),(0,1,0),(0,0,1),0.11,0.11,0.07,0.006)
    KS.prism(G("dropout","GALV"),Vector((e.x,e.y,Z_RING-0.02)),Vector((e.x,e.y,Z_RING+0.03)),CR*2.4,CR*1.1,12,0.0,True,0.0)
    _,q,wi=nearest_ring(e);wn=Vector((WALLS[wi].n.x,WALLS[wi].n.y,0))
    mount=G('dropout mounts','STEEL');qc=Vector((q.x,q.y,Z_RING-.01));ec=Vector((e.x,e.y,Z_RING-.01))
    bar(KS,mount,qc-wn*.27,qc+wn*.27,.055,.02,(0,0,1),0)
    if (qc-ec).length>.001:bar(KS,mount,ec,qc,.055,.02,(0,0,1),0)
    KS.box(mount,e.x,e.y,Z_RING-.02,Z_RING,.055,.055,0,0)
    SUPPORT.register('piping supports',nm+' dropout onto carrier','RH services R2 PIPING dropout STEEL','RH services R2 PIPING dropout mounts STEEL',[(e.x+.014,e.y,Z_RING-.02)],(0,0,1),'wall')
    SUPPORT.register('piping supports',nm+' carrier onto tray','RH services R2 PIPING dropout mounts STEEL','RH services R2 PIPING tray GALV',[(q.x+wn.x*off,q.y+wn.y*off,Z_RING) for off in (-.23,.23)],(0,0,1),'wall')
conduit("vent control feed",jbox=True)
conduit("pump starter conduit",jbox=True)
# bench socket outlet at the west wall (the west-bench riser starts on top of it)
bx,by=-10.66,5.2
obox(KS,G("socket","IRON"),(bx+0.0,by,1.14),(1,0,0),(0,1,0),(0,0,1),0.08,0.16,0.16,0.008)
obox(KS,G("socket","STEEL"),(bx+0.08,by,1.14),(1,0,0),(0,1,0),(0,0,1),0.01,0.13,0.13,0.004)
for k in(-1,1): KS.prism(G("socket","ORANGE"),(bx+0.09,by+k*0.065,1.12),(bx+0.12,by+k*0.065,1.12),0.032,0.032,12,0.0,True,0.0)
KS.prism(G("socket","RED"),(bx+0.09,by,1.24),(bx+0.105,by,1.24),0.012,0.012,8,0.0,True,0.0)
socket_p=service_wall_seat(Vector((-10.74,by,1.14)),Vector((1,0,0)),.16,.32)
wall_plate(KS,socket_p,(1,0,0),.16,.32,.012,G('socket mount','STEEL'))
for dy in (-.10,.10):
    for dz in (-.10,.10):
        back=Vector((-10.74,by+dy,1.14+dz));start=Vector((socket_p.x+.012,back.y,back.z))
        KS.prism(G('socket mount','STEEL'),start,back,.012,.012,16,0,True,0)
        SUPPORT.register('piping supports','socket case to wall spacers','RH services R2 PIPING socket IRON','RH services R2 PIPING socket mount STEEL',[back],(-1,0,0),'wall')
# ================================================================== objects
objs=KS.build(COLL_PIPE,"RH services",M)
for o in objs:
    for p in o.data.polygons: pass
print("services objects:",len(objs),"verts",sum(len(o.data.vertices) for o in objs))
exec(open(os.path.join(HERE,"rh_svc_fixtures.py")).read()) if os.path.exists(os.path.join(HERE,"rh_svc_fixtures.py")) else None
bpy.ops.wm.save_as_mainfile(filepath=OUT); print("saved",OUT)
