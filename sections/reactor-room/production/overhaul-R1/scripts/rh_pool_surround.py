"""Reactor hall pass, POOL SURROUND builder.   usage: python rh_pool_surround.py -- <in.blend> <out.blend>
Owns (replaces) in `03 POOL AND RAIL`: steel aperture curb, rim stones, guardrail, posts, toe board, service gate, SCRAM / ACKNOWLEDGE / bypass consoles and annunciator, floor-level tread plates and
hazard stripes around the rim; and in `04 BANK MECHANISMS` the gantry girders, roof hangers, transfer bearings and gantry service lamps (never BANK_* / RP bank* / the R2 bank enamel/iron cassettes).
Kept: water, medium, caustics, depth markers, pool lamps, core light wells, submerged hardware, lining, `R2 detail pool rim glow GLOW*` (state-driven R2 state glow; the new tread plate sits under them).
Contract objects keep name and pivot: SCRAM_BUTTON, ALARM_ACK (geometry swapped in place), SERVICE_GATE_PIVOT, BYPASS_SWITCH_PIVOT (new gate leaf / lever are re-parented to them).
Everything is static geometry joined per (group, material); materials come from rh_mats.lib() plus a few `RH pool ...` ones.  Deterministic and re-runnable (own objects are deleted first)."""
import bpy,bmesh,sys,os,math,re
from mathutils import Vector,Matrix
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import crk,rh_mats
import rh_support_registry as SUPPORT
A=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A[0],A[1]
bpy.ops.wm.open_mainfile(filepath=SRC)
SUPPORT.reset('pool roof suspension')
SUPPORT.reset('pool rail feet')
crk.STATE=bpy.data.objects.get("REACTOR_STATE")
POOLC=bpy.data.collections["03 POOL AND RAIL"]; BANKC=bpy.data.collections["04 BANK MECHANISMS"]
D2R=math.pi/180
# ------------------------------------------------------------------------------------------------ materials
M=dict(rh_mats.lib())
def _tread():
    n="RH pool tread plate"; m=bpy.data.materials.get(n)
    if m: return m
    m=bpy.data.materials.new(n); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    N=lambda t,x=0,y=0:(lambda q:(setattr(q,'location',(x,y)),q)[1])(nt.nodes.new(t))
    out=N("ShaderNodeOutputMaterial",1200,0); b=N("ShaderNodeBsdfPrincipled",900,0); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    b.inputs['Metallic'].default_value=0.85; b.inputs['Roughness'].default_value=0.40
    geo=N("ShaderNodeNewGeometry",0,0); hs=[]
    for k,ang in enumerate((math.pi/4,-math.pi/4)):                         # two crossed rib patterns = diamond tread
        mp=N("ShaderNodeMapping",150,200-k*300); mp.inputs['Rotation'].default_value=(0,0,ang); nt.links.new(geo.outputs['Position'],mp.inputs['Vector'])
        wv=N("ShaderNodeTexWave",350,200-k*300); wv.wave_type='BANDS'; wv.bands_direction='X'; wv.inputs['Scale'].default_value=52.0; wv.inputs['Distortion'].default_value=0.0; wv.wave_profile='SAW'
        nt.links.new(mp.outputs['Vector'],wv.inputs['Vector'])
        sm=N("ShaderNodeMapRange",550,200-k*300); sm.inputs['From Min'].default_value=0.55; sm.inputs['From Max'].default_value=0.75; nt.links.new(wv.outputs['Fac'],sm.inputs['Value']); hs.append(sm)
    mu=N("ShaderNodeMath",750,0); mu.operation='MULTIPLY'; nt.links.new(hs[0].outputs[0],mu.inputs[0]); nt.links.new(hs[1].outputs[0],mu.inputs[1])
    bp=N("ShaderNodeBump",800,-250); bp.inputs['Strength'].default_value=0.9; bp.inputs['Distance'].default_value=0.004; nt.links.new(mu.outputs[0],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
    nz=N("ShaderNodeTexNoise",300,-500); nz.inputs['Scale'].default_value=3.0; nz.inputs['Detail'].default_value=5.0; nt.links.new(geo.outputs['Position'],nz.inputs['Vector'])
    mr=N("ShaderNodeMapRange",500,-500); mr.inputs['From Min'].default_value=0.3; mr.inputs['From Max'].default_value=0.7; mr.inputs['To Min'].default_value=0.5; mr.inputs['To Max'].default_value=1.15; nt.links.new(nz.outputs['Fac'],mr.inputs['Value'])
    cv=N("ShaderNodeVectorMath",700,-500); cv.operation='SCALE'; cv.inputs[0].default_value=(0.20,0.205,0.205); nt.links.new(mr.outputs[0],cv.inputs[3]); nt.links.new(cv.outputs[0],b.inputs['Base Color'])
    return m
M["TREAD"]=_tread()
M["AMBER"]=rh_mats.surf("RH pool amber paint",(0.62,0.33,0.02),0.5,0.0,mottle=0.2,scale=2.0,bump=0.0)
M["LAMPA"]=rh_mats.emit("RH pool annunciator amber",(1.0,0.42,0.04),1.3)
M["LAMPREAL"]=bpy.data.materials.get("lamp")
M["AMBERBTN"]=bpy.data.materials["R2 lamp amber"]; M["REDBTN"]=bpy.data.materials["R2 status lamp"]
# ------------------------------------------------------------------------------------------------ remove own objects
KEEP_POOL=("RP ","Water surface","Deep water medium","Deep cyan emitter","Core light well","Core bed side shield","Submerged guide","Guide rib","Shaft intake","R2 pool pool ")
def zmax(o): return max((o.matrix_world@Vector(v)).z for v in o.bound_box)
def kill(o):
    me=o.data if o.type in('MESH','CURVE','FONT') else None
    bpy.data.objects.remove(o,do_unlink=True)
    if me is not None and me.users==0:
        (bpy.data.meshes if isinstance(me,bpy.types.Mesh) else bpy.data.curves).remove(me)
for o in list(bpy.data.objects):
    if o.name.startswith("RH pool "): kill(o); continue
    cn=o.users_collection[0].name if o.users_collection else ""
    if cn=="03 POOL AND RAIL" and o.type in('MESH','CURVE','FONT'):
        if o.name in("SCRAM_BUTTON","ALARM_ACK"): continue
        if o.name.startswith(KEEP_POOL): continue
        if o.name.startswith("MERGED") and zmax(o)<-0.3: continue
        kill(o)
    elif cn=="04 BANK MECHANISMS" and o.type=='MESH':
        if o.name.startswith(("Gantry","Roof")) or (o.name.startswith("MERGED 04") and "hall_steel" in o.name): kill(o)
PIV_GATE=bpy.data.objects["SERVICE_GATE_PIVOT"]; PIV_BYP=bpy.data.objects["BYPASS_SWITCH_PIVOT"]
# ------------------------------------------------------------------------------------------------ geometry helpers
def sweep(K,key,prof,a0,a1,n,smooth=True,sharp=38,cx=0.0,cy=0.0):
    """sweep a CLOSED (r,z) profile about the vertical axis from angle a0 to a1 (radians) in n steps; caps at the ends when not a full circle; normals recalculated outward"""
    bm=K.get(key); full=abs((a1-a0)-2*math.pi)<1e-6; m=len(prof); cols=n if full else n+1; rings=[]
    for i in range(cols):
        a=a0+(a1-a0)*i/n; c,s=math.cos(a),math.sin(a)
        rings.append([bm.verts.new(Vector((cx+r*c,cy+r*s,z))) for (r,z) in prof])
    fs=[]
    for i in range(n):
        A_,B_=rings[i],rings[(i+1)%cols]
        for j in range(m):
            k=(j+1)%m; fs.append(bm.faces.new((A_[j],A_[k],B_[k],B_[j])))
    if not full:
        fs.append(bm.faces.new(rings[0])); fs.append(bm.faces.new(rings[-1][::-1]))
    bmesh.ops.recalc_face_normals(bm,faces=fs)
    for f in fs: f.smooth=smooth
    if smooth:
        for j in range(m):
            p0,p1,p2=prof[j-1],prof[j],prof[(j+1)%m]
            a_=math.atan2(p1[1]-p0[1],p1[0]-p0[0]); b_=math.atan2(p2[1]-p1[1],p2[0]-p1[0]); d=abs(math.degrees(math.atan2(math.sin(b_-a_),math.cos(b_-a_))))
            if d>sharp:
                for i in range(cols if full else n+1):
                    e=bm.edges.get((rings[i][j],rings[(i+1)%cols][j])) if (full or i<n) else None
                    if e: e.smooth=False
def circ(r0,z0,rho,n=10): return [(r0+rho*math.cos(2*math.pi*k/n),z0+rho*math.sin(2*math.pi*k/n)) for k in range(n)]
def rect(r0,r1,z0,z1,ch=0.0):
    if ch<=0: return [(r0,z0),(r0,z1),(r1,z1),(r1,z0)]
    return [(r0,z0),(r0,z1-ch),(r0+ch,z1),(r1-ch,z1),(r1,z1-ch),(r1,z0)]
def P(r,th,z=0.0): return (r*math.cos(th),r*math.sin(th),z)
def sector(K,key,r0,r1,t0,t1,z0,z1,ch=0.004,mid=True):
    """one chamfered ring-sector block (inner radius r0, outer r1, angle t0..t1) as a hull"""
    pts=[]
    tm=(t0+t1)/2
    for z in (z0,z1):
        pts+=[P(r0,t0,z),P(r1,t0,z),P(r0,t1,z),P(r1,t1,z)]
        if mid: pts+=[P(r0,tm,z),P(r1,tm,z)]
    K.hull(key,pts,ch)
def hbox(K,key,p0,p1,w,h,ch=0.004,roll=0.0):
    """box from p0 to p1 (any direction) with cross-section w x h (h along the world z-ish normal)"""
    a=Vector(p0); b=Vector(p1); d=(b-a); L=d.length; x=d/L; up=Vector((0,0,1)) if abs(x.z)<0.95 else Vector((0,1,0)); y=up.cross(x).normalized(); z=x.cross(y)
    pts=[a+x*t+y*(sy*w/2)+z*(sz*h/2) for t in (0,L) for sy in(-1,1) for sz in(-1,1)]
    K.hull(key,pts,ch)
def text3d(body,x,y,z,size,mat,facing='-y',name="RH pool legend",extr=0.002):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.size=size; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=extr; cu.resolution_u=2
    ob=bpy.data.objects.new(name,cu); ob.location=(x,y,z); ob.rotation_euler=(math.pi/2,0,crk.RZ[facing]); POOLC.objects.link(ob); cu.materials.append(mat); crk.TEXTS.append(ob); return ob
def swap(target,K,key,mat):
    """give a contract object new geometry (built in world coordinates under group key); it keeps name, parent and pivot"""
    objs=K.build(target.users_collection[0],"RHT",{key:mat}); t=objs[0]; me=t.data; me.transform(target.matrix_world.inverted()); old=target.data; target.data=me
    target.data.materials.clear(); target.data.materials.append(mat); bpy.data.objects.remove(t); bpy.data.meshes.remove(old); me.name=target.name
def reparent(objs,parent):
    for o in objs: o.parent=parent; o.matrix_parent_inverse=parent.matrix_world.inverted()
# ================================================================================================ POOL SURROUND
RR=3.62                                                                          # guardrail radius (the service gate chord sits at the same line)
Z0=0.20                                                                          # coping top
ZT=0.215                                                                         # tread plate top
GATE_X0,GATE_X1=-1.19,1.11                                                       # console pedestals = gate posts
th_start=-55.5*D2R                                                               # east end: the sample station
th_end=(270-math.degrees(math.asin(1.19/RR)))                                    # west end: the ACKNOWLEDGE pedestal
th_end=(180+ (90-math.degrees(math.asin(1.19/RR))) )*D2R                         # = 250.8 deg
# ---------------- curb, coping, step, drainage lip
K=crk.Kit()
sweep(K,("coping","GALV"),[(3.400,-0.20),(3.400,0.150),(3.412,0.185),(3.488,0.185),(3.500,0.17),(3.500,-0.20)],0,2*math.pi,120)          # stainless aperture curb with rounded nose
sweep(K,("coping","CONC_POUR"),[(3.50,-0.30),(3.50,0.10),(3.58,0.10),(3.58,0.19),(3.588,0.20),(3.962,0.20),(3.972,0.19),(3.972,-0.30)],0,2*math.pi,120)
sweep(K,("coping","CONC_POUR"),[(3.94,-0.04),(3.94,0.092),(3.952,0.10),(4.205,0.10),(4.225,0.088),(4.225,-0.04)],0,2*math.pi,120)        # lower step
sweep(K,("coping","BLACK"),[(3.502,0.050),(3.502,0.101),(3.578,0.101),(3.578,0.050)],0,2*math.pi,96,smooth=False)                            # dark drainage trough
for k in range(96):                                                                                                                          # flush stainless drain grating: radial slats + two rims
    th=k*2*math.pi/96; hbox(K,("coping","GALV"),P(3.503,th,0.165),P(3.577,th,0.165),0.011,0.020,0.001)
sweep(K,("coping","GALV"),rect(3.498,3.508,0.140,0.185),0,2*math.pi,96,smooth=False); sweep(K,("coping","GALV"),rect(3.572,3.582,0.140,0.185),0,2*math.pi,96,smooth=False)
# expansion joints (black sealant) across the concrete, every 45 deg
for k in range(8):
    th=(22.5+45*k)*D2R
    hbox(K,("coping","BLACK"),P(3.60,th,Z0+0.002),P(3.965,th,Z0+0.002),0.010,0.004,0.0)
    hbox(K,("coping","BLACK"),P(3.955,th,0.102),P(4.215,th,0.102),0.010,0.004,0.0)
# ---------------- non-slip tread plates (24 sectors, bolted) on the coping, under the rim glow strips
for k in range(24):
    t0=(k*15+0.45)*D2R; t1=((k+1)*15-0.45)*D2R
    sector(K,("tread","TREAD"),3.595,3.865,t0,t1,Z0-0.004,ZT,0.0035)
    for rr in (3.62,3.84):
        for tt in (t0+2.2*D2R,t1-2.2*D2R): K.cyl(("tread","STEEL"),rr*math.cos(tt),rr*math.sin(tt),ZT,ZT+0.007,0.0085,8,0.0)
# ---------------- hazard stripes on the lower step (black base ring, yellow slanted stripes)
sweep(K,("chev","BLACK"),rect(3.985,4.185,0.100,0.104),0,2*math.pi,96,smooth=False)
nstr=48
for k in range(nstr):
    # Local hazard patches at the four approach sectors keep the edge clear
    # without competing with the continuous guardrail and circulation line.
    if k%12>=2:continue
    t0=k*2*math.pi/nstr; w=2*math.pi/nstr
    p=[P(3.985,t0,0.1055),P(3.985,t0+0.5*w,0.1055),P(4.185,t0+1.5*w,0.1055),P(4.185,t0+w,0.1055)]
    bm=K.get(("chev","YELLOW")); vs=[bm.verts.new(Vector((x,y,z))) for (x,y,z) in p]; f=bm.faces.new(vs[::-1]); f.normal_update()
    if f.normal.z<0: f.normal_flip()
# ---------------- approach landing at the gate: raised tread plate with hazard nosing and two risers
def box_(key,x0,x1,y0,y1,z0,z1,ch=0.004): K.bx(key,x0,x1,y0,y1,z0,z1,ch)
box_(("landing","CONC_POUR"),-1.17,1.10,-4.34,-3.93,-0.04,0.10,0.006)
box_(("landing","TREAD"),-1.15,1.08,-4.30,-3.95,0.098,0.112,0.004)
box_(("landing","YELLOW"),-1.17,1.10,-4.355,-4.30,0.092,0.104,0.004)
for xx in (-1.08,-0.50,0.10,0.70,1.00):
    pass
for xx in (-1.10,1.03):
    for yy in (-4.27,-3.99): K.cyl(("landing","STEEL"),xx,yy,0.112,0.119,0.009,8,0.0)
# ---------------- guardrail: posts with base plates, bolts and gussets, through rails, toe board
def inpipe(x): return -1.62<x<-1.22
nposts=0; ths=[th_start+k*(243.7*D2R-th_start)/22 for k in range(23)]
for th in ths:
    x,y=RR*math.cos(th),RR*math.sin(th)
    if inpipe(x): continue
    # Keep the handrail radius, but seat posts and asymmetric foot plates
    # wholly over the tread instead of cantilevering their inner bolts over
    # the adjacent drainage channel.
    x,y=(RR+.015)*math.cos(th),(RR+.015)*math.sin(th)
    K.box(("rail","YELLOW"),x,y,ZT,1.31,0.050,0.050,th+math.pi/2,0.004)                                  # square-tube post
    K.box(("rail","YELLOW"),x,y,1.31,1.318,0.060,0.060,th+math.pi/2,0.003)                               # cap plate
    fx,fy=(RR+.030)*math.cos(th),(RR+.030)*math.sin(th)
    K.box(("rail","STEEL"),fx,fy,ZT,ZT+0.012,0.130,0.100,th+math.pi/2,0.003)
    foot_anchors=[]
    for sx in (-1,1):
        for sy in (-1,1):
            lx,ly=sx*0.047,sy*0.035
            # Avoid placing an anchor bolt in a tread-sector expansion gap.
            for offset in (0,.012,-.012,.020,-.020):
                bx_=fx+(lx+offset)*math.cos(th+math.pi/2)-ly*math.sin(th+math.pi/2)
                by_=fy+(lx+offset)*math.sin(th+math.pi/2)+ly*math.cos(th+math.pi/2)
                phase=math.degrees(math.atan2(by_,bx_))%15
                if .55<phase<14.45:break
            else:raise RuntimeError('Rail anchor coincides with a tread joint')
            K.cyl(("rail","STEEL"),bx_,by_,ZT+0.012,ZT+0.021,0.0095,6,0.0)
            foot_anchors.append((bx_,by_,ZT))
    SUPPORT.register('pool rail feet','rail foot '+str(th),'RH pool rail STEEL','RH pool tread TREAD',foot_anchors)
    for sgn in (-1,1):                                                                                    # two gussets along the rail direction
        tg=th+math.pi/2; c,s=math.cos(tg),math.sin(tg)
        a=(x+sgn*0.025*c,y+sgn*0.025*s); b=(x+sgn*0.060*c,y+sgn*0.060*s)
        K.hull(("rail","YELLOW"),[(a[0],a[1],ZT+0.012),(b[0],b[1],ZT+0.012),(a[0],a[1],ZT+0.16),(x+sgn*0.032*c,y+sgn*0.032*s,ZT+0.16)],0.0)
    nposts+=1
ra=th_end-2.2*D2R
sweep(K,("rail","YELLOW"),circ(RR,1.285,0.0215,10),th_start,ra,84)                                         # top rail
sweep(K,("rail","YELLOW"),circ(RR,0.760,0.0195,10),th_start,ra,84)                                         # mid rail
sweep(K,("rail","YELLOW"),rect(RR-0.012,RR+0.012,ZT+0.012,ZT+0.112,0.003),th_start,243.7*D2R,80,smooth=False)   # 100 mm toe board
sweep(K,("rail","BLACK"),rect(RR-0.0125,RR+0.0125,ZT+0.012,ZT+0.026),th_start,243.7*D2R,80,smooth=False)         # rubber toe-board gasket strip
for th in (th_start,th_end-2.2*D2R):                                                                         # rail ends: closed with a ball cap
    for z_,rho in ((1.285,0.0215),(0.760,0.0195)): K.cyl(("rail","YELLOW"),RR*math.cos(th),RR*math.sin(th),z_-rho*0.9,z_+rho*0.9,rho*1.15,8,0.0)
# ---------------- console pedestals (gate posts)
def pedestal(cx,tag,txt_head,plaque_mat,plaque_txt_mat,face_plate_mat):
    xa,xb=cx-0.165,cx+0.165
    box_((tag,"STEEL"),xa-0.02,xb+(0.02 if cx<0 else 0),-3.84,-3.36,Z0,Z0+0.06,0.004)
    for sx in (-1,1):
        for sy in (-1,1): K.cyl((tag,"STEEL"),cx+sx*(.13 if cx>0 and sx>0 else .16),-3.60+sy*0.21,Z0+0.06,Z0+0.068,0.0095,6,0.0)
    K.hull((tag,"AUDI_SATIN"),[(xa+0.008,-3.795,Z0+0.06),(xb-0.008,-3.795,Z0+0.06),(xa+0.008,-3.38,Z0+0.06),(xb-0.008,-3.38,Z0+0.06),(xa,-3.80,0.93),(xb,-3.80,0.93),(xa,-3.38,0.93),(xb,-3.38,0.93)],0.006)
    box_((tag,"IRON"),xa-0.005,xb+0.005,-3.805,-3.40,0.58,0.60,0.003)                                    # waist band
    K.louvre((tag,"BLACK"),'-x',xa,-3.72,-3.46,0.36,0.52,5,0.012); K.louvre((tag,"BLACK"),'+x',xb,-3.72,-3.46,0.36,0.52,5,0.012)
    K.hull((tag,"AUDI"),[(xa-0.008,-3.40,0.93),(xb+0.008,-3.40,0.93),(xa-0.008,-3.80,0.93),(xb+0.008,-3.80,0.93),(xa-0.008,-3.40,1.27),(xb+0.008,-3.40,1.27),(xa-0.008,-3.875,1.27),(xb+0.008,-3.875,1.27),(xa-0.008,-3.875,1.01),(xb+0.008,-3.875,1.01)],0.006)   # head, front panel leans in at the bottom
    box_((tag,"STEEL"),xa-0.016,xb+0.016,-3.90,-3.40,1.27,1.285,0.004)                                  # top cap
    K.screws((tag,"STEEL"),'-y',-3.8755,xa+0.02,xb-0.02,1.02,1.25,0.0055,0.014)
    box_((tag,"BLACK"),cx-0.15,cx+0.15,-3.40,-3.38,0.30,0.88,0.003)                                      # rear service door seam
    # label plaque standing on the head, text on its front
    for sx in (-1,1): K.cyl((tag,"STEEL"),cx+sx*.14,-3.5175,1.285,1.765,.009,12,0)
    box_((tag,plaque_mat),xa-0.01,xb+0.01,-3.53,-3.505,1.75,1.895,0.004)
    text3d(txt_head,cx,-3.5325,1.823,0.060 if txt_head=="SCRAM" else 0.031,M[plaque_txt_mat],'-y',"RH pool legend plaque")
pedestal(-1.025,"console","ACKNOWLEDGE","AUDI","AMBER","AUDI")
pedestal(0.94,"console","SCRAM","RED","WHITE","AUDI")
# ACKNOWLEDGE button (contract ALARM_ACK): amber lamp push button in a black guard collar with two yellow guard bars
cxa=-1.025; zb=1.08; yf=-3.875
Kb=crk.Kit(); Kb.prism(("b","AMBERBTN"),(cxa,yf-0.001,zb),(cxa,yf-0.024,zb),0.052,0.054,18,0.0,True,0.003); Kb.prism(("b","AMBERBTN"),(cxa,yf-0.024,zb),(cxa,yf-0.036,zb),0.050,0.034,18,0.0,True,0.0)
swap(bpy.data.objects["ALARM_ACK"],Kb,"AMBERBTN",M["AMBERBTN"])
K.prism(("console","BLACK"),(cxa,yf,zb),(cxa,yf-0.030,zb),0.082,0.078,24,0.0,False,0.0); K.prism(("console","BLACK"),(cxa,yf-0.030,zb),(cxa,yf-0.034,zb),0.082,0.062,24,0.0,True,0.0)   # shroud
K.prism(("console","BLACK"),(cxa,yf-0.034,zb),(cxa,yf-0.034,zb+0.0001),0.062,0.062,24,0.0,False,0.0)
for sx in (-1,1): K.cyly(("console","YELLOW"),cxa+sx*0.100,yf+0.001,yf-0.055,zb,0.0075,8)
text3d("ALARM ACK",cxa,yf-0.001,zb+0.135,0.017,M["WHITE"],'-y',"RH pool legend")
# annunciator window (2 x 2 amber tiles) below
ya=-3.795
box_(("console","BLACK"),cxa-0.115,cxa+0.115,ya-0.050,ya+0.001,0.655,0.905,0.004)
for i in range(2):
    for j in range(2):
        K.box(("console","LAMPA"),cxa-0.052+i*0.104,ya-0.050,0.690+j*0.100+0.0,0.690+j*0.100+0.075,0.092,0.004,0.0,0.0)
for j in range(2): box_(("console","IRON"),cxa-0.112,cxa+0.112,ya-0.0545,ya-0.0505,0.690+j*0.100+0.077,0.690+j*0.100+0.081,0.0)
box_(("console","IRON"),cxa-0.003,cxa+0.003,ya-0.0545,ya-0.0505,0.690,0.865,0.0)
text3d("ALARMS",cxa,ya-0.0545,0.672,0.020,M["WHITE"],'-y',"RH pool legend")
# SCRAM button (contract SCRAM_BUTTON): red mushroom cap in a yellow guard: two side ears and a hinged, raised flip cover
cxs=0.94; zb=1.09; yf=-3.875
Kb=crk.Kit(); Kb.prism(("b","REDBTN"),(cxs,yf-0.001,zb),(cxs,yf-0.020,zb),0.034,0.034,16,0.0,True,0.0)
Kb.prism(("b","REDBTN"),(cxs,yf-0.020,zb),(cxs,yf-0.036,zb),0.074,0.080,24,0.0,True,0.004); Kb.prism(("b","REDBTN"),(cxs,yf-0.036,zb),(cxs,yf-0.046,zb),0.080,0.050,24,0.0,True,0.0)
swap(bpy.data.objects["SCRAM_BUTTON"],Kb,"REDBTN",M["REDBTN"])
K.prism(("console","BLACK"),(cxs,yf,zb),(cxs,yf-0.026,zb),0.098,0.094,24,0.0,False,0.0); K.prism(("console","BLACK"),(cxs,yf-0.026,zb),(cxs,yf-0.030,zb),0.098,0.088,24,0.0,True,0.0)
for sx in (-1,1):
    K.hull(("console","YELLOW"),[(cxs+sx*0.128-0.006,yf,zb-0.12),(cxs+sx*0.128+0.006,yf,zb-0.12),(cxs+sx*0.128-0.006,yf-0.085,zb-0.12),(cxs+sx*0.128+0.006,yf-0.085,zb-0.12),
                                  (cxs+sx*0.128-0.006,yf,zb+0.13),(cxs+sx*0.128+0.006,yf,zb+0.13),(cxs+sx*0.128-0.006,yf-0.030,zb+0.13),(cxs+sx*0.128+0.006,yf-0.030,zb+0.13)],0.003)
zh=zb+0.132; yh=yf-0.030                                                                                  # hinge line above the button
K.cylx(("console","STEEL"),cxs-0.135,cxs+0.135,yh,zh,0.0085,10)
for sx in (-1,1): K.box(("console","STEEL"),cxs+sx*0.105,yf-0.016,zh-0.015,zh+0.005,0.020,0.030,0.0,0.002)
dirv=Vector((0,-math.sin(15*D2R),math.cos(15*D2R))); nrm=Vector((0,math.cos(15*D2R),math.sin(15*D2R)))      # flip cover opened almost vertical, leaning away from the button
def lid(t0,t1,hw,th): return [Vector((cxs+sx*hw,yh,zh))+dirv*t+nrm*(s_*th) for t in (t0,t1) for sx in (-1,1) for s_ in (-1,1)]
K.hull(("console","YELLOW"),lid(0.012,0.185,0.120,0.005),0.003)
K.hull(("console","BLACK"),lid(0.060,0.075,0.100,0.0065),0.002)                                          # grip rib across the lid
box_(("console","AUDI"),cxs-.13,cxs+.13,-3.815,-3.800,.85,.91,.002)
text3d("REACTOR TRIP",cxs,-3.816,.88,0.021,M["WHITE"],'-y',"RH pool legend")
# bypass selector (pivot empty keeps name and place): rotary lever on an orange-bordered plate; lever parented to the pivot
yb=PIV_BYP.matrix_world.translation.y; xb_=PIV_BYP.matrix_world.translation.x; zbp=PIV_BYP.matrix_world.translation.z
box_(("console","ORANGE"),xb_-0.105,xb_+0.105,yb-0.012,yb+0.012,zbp-0.095,zbp+0.095,0.004)
box_(("console","AUDI"),xb_-0.088,xb_+0.088,yb-0.024,yb+0.012,zbp-0.078,zbp+0.078,0.003)
for sx in (-1,1):
    for sz in (-1,1): K.cyly(("console","STEEL"),xb_+sx*0.095,yb-0.006,yb-0.015,zbp+sz*0.085,0.0055,6)
for k in range(5):
    th=(-60+k*30)*D2R; K.cyly(("console","WHITE"),xb_+0.062*math.sin(th),yb-0.024,yb-0.0275,zbp+0.062*math.cos(th),0.0035,6)
text3d("BYPASS",xb_,yb-0.0245,zbp+0.108,0.022,M["WHITE"],'-y',"RH pool legend")
text3d("AUTH ONLY",xb_,yb-0.0245,zbp-0.108,0.016,M["WHITE"],'-y',"RH pool legend")
Kl=crk.Kit()                                                                                                  # the lever (rest position, points at the operator)
Kl.cyly(("lever","STEEL"),xb_,yb-0.024,yb-0.040,zbp,0.022,14); Kl.cyly(("lever","ORANGE"),xb_,yb-0.040,yb-0.145,zbp,0.0085,10)
Kl.prism(("lever","BLACK"),(xb_,yb-0.145,zbp),(xb_,yb-0.185,zbp),0.020,0.026,14,0.0,True,0.002)
lev=Kl.build(POOLC,"RH pool bypass",M); reparent(lev,PIV_BYP)
# ---------------- service gate leaf (re-parented to SERVICE_GATE_PIVOT, hinge pin at the pivot), hinge straps on the ACKNOWLEDGE pedestal and the latch receiver on the SCRAM pedestal
gp=PIV_GATE.matrix_world.translation; gx,gy=gp.x,gp.y; GZ=gp.z
Kg=crk.Kit(); xe=0.665
def GB(key,x0,x1,z0,z1,ch=0.004,y0=gy-0.020,y1=gy+0.020): Kg.bx(key,x0,x1,y0,y1,z0,z1,ch)
GB(("gate","YELLOW"),gx+0.012,gx+0.062,GZ+0.03,1.31)                                                     # hinge stile
GB(("gate","YELLOW"),xe-0.05,xe,GZ+0.03,1.31)                                                            # latch stile
for z_,rho in ((1.285,0.0215),(0.760,0.0195)): Kg.cylx(("gate","YELLOW"),gx+0.06,xe-0.04,gy,z_,rho,10)
GB(("gate","YELLOW"),gx+0.06,xe-0.05,GZ+0.045,GZ+0.14,0.003,gy-0.015,gy+0.015)                              # toe plate
Kg.prism(("gate","YELLOW"),(gx+0.07,gy,GZ+0.15),(xe-0.06,gy,1.26),0.012,0.012,8,0.0,True,0.0)                  # diagonal brace
nP=int((xe-0.05-(gx+0.06))/0.115)
for i in range(1,nP): Kg.cyl(("gate","YELLOW"),gx+0.06+i*(xe-0.05-gx-0.06)/nP,gy,GZ+0.14,1.27,0.0085,8,0.0)
Kg.cylx(("gate","STEEL"),xe-0.05,xe+0.085,gy+0.004,0.775,0.0085,8)                                         # slide bolt
Kg.cyly(("gate","BLACK"),xe-0.02,gy-0.03,gy-0.075,0.795,0.0095,8)
Kg.prism(("gate","BLACK"),(xe-0.02,gy-0.075,0.795),(xe-0.02,gy-0.105,0.795),0.016,0.016,12,0.0,True,0.002)
Kg.box(("gate","STEEL"),xe-0.025,gy-0.027,0.745,0.835,0.034,0.010,0.0,0.002)
for z_ in (GZ+0.20,1.10):                                                                                 # moving hinge knuckles
    Kg.cyl(("gate","STEEL"),gx,gy,z_-0.045,z_+0.045,0.0155,10,0.0); Kg.bx(("gate","STEEL"),gx+0.0,gx+0.075,gy-0.012,gy+0.012,z_-0.035,z_+0.035,0.003)
gate=Kg.build(POOLC,"RH pool gate",M); reparent(gate,PIV_GATE)
for z_ in (GZ+0.20,1.10):                                                                                 # fixed hinge: pin, straps from the ACKNOWLEDGE pedestal's east face, nut
    K.cyl(("gatefix","STEEL"),gx,gy,z_-0.075,z_+0.075,0.0075,8,0.0); K.cyl(("gatefix","STEEL"),gx,gy,z_+0.075,z_+0.082,0.013,6,0.0)
    K.bx(("gatefix","STEEL"),-0.865,gx+0.012,gy-0.012,gy+0.012,z_-0.065,z_-0.047,0.003); K.bx(("gatefix","STEEL"),-0.865,gx+0.012,gy-0.012,gy+0.012,z_+0.047,z_+0.065,0.003)
    K.cyl(("gatefix","STEEL"),gx,gy,z_-0.047,z_-0.040,0.0145,10,0.0)
K.bx(("gatefix","YELLOW"),0.745,0.772,gy-0.045,gy+0.045,0.70,0.84,0.004)                                  # latch receiver on the SCRAM pedestal
K.bx(("gatefix","BLACK"),0.745,0.762,gy-0.02,gy+0.02,0.765,0.790,0.0)
# ---------------- bake the pool surround
objs=K.build(POOLC,"RH pool",M)
for o in objs:
    if o.name.endswith(" TREAD") or " tread " in o.name: pass
print("rh_pool_surround: pool surround objects",len(objs),"posts",nposts)
crk.mesh_texts()
for o in list(bpy.data.objects):
    if o.type=='MESH' and o.name.startswith("RH pool legend") and o.name!="": pass
# ================================================================================================ GANTRY (04 BANK MECHANISMS)
# two plate girders along x over the banks (y = +-0.52, the bank necks pass between them), top-running rails, cross ties, bolted end trucks that hang under two runway beams (x = +-7.6, hung from the
# roof by clevis-pinned hangers), a hoist trolley with drum, ropes, hook block and cable festoon on the -y girder, an inspection platform with handrail on the +y side, and two service luminaires.
G=crk.Kit(); XG=7.2
for sy in (-1,1):
    yc=sy*0.52
    G.bx(("girder","YELLOW"),-XG,XG,yc-0.010,yc+0.010,13.56,14.48,0.002)                             # web
    G.bx(("girder","YELLOW"),-XG,XG,yc-0.18,yc+0.18,14.48,14.52,0.004); G.bx(("girder","YELLOW"),-XG,XG,yc-0.18,yc+0.18,13.52,13.56,0.004)   # flanges
    G.bx(("girder","STEEL"),-XG,XG,yc-0.035,yc+0.035,14.52,14.60,0.006)                                  # crane rail
    for k in range(-7,8):                                                                               # stiffeners both sides, every 0.9 m
        for so in (-1,1): G.bx(("girder","YELLOW"),k*0.9-0.006,k*0.9+0.006,yc+so*0.010,yc+so*0.17 if so>0 else yc-0.17,13.56,14.48,0.002) if so>0 else G.bx(("girder","YELLOW"),k*0.9-0.006,k*0.9+0.006,yc-0.17,yc-0.010,13.56,14.48,0.002)
    for k in range(-1,2):                                                                               # rail splice plates and clamp bolts
        for xx in (k*3.6,):
            G.bx(("girder","STEEL"),xx-0.12,xx+0.12,yc-0.045,yc+0.045,14.60,14.612,0.003)
    for xx in [i*0.45-7.0 for i in range(32)]:
        for so in (-1,1): G.cyl(("girder","STEEL"),xx,yc+so*0.12,14.52,14.527,0.007,6,0.0)               # flange bolts
    for xx in (-1,1):                                                                                     # rail end stops (yellow buffers)
        G.bx(("girder","YELLOW"),xx*6.95-0.06,xx*6.95+0.06,yc-0.075,yc+0.075,14.60,14.74,0.006)
for xx in (-6.1,-4.5,-2.9,2.9,4.5,6.1):                                                                  # cross ties between the girders, with gusset plates
    G.bx(("girder","YELLOW"),xx-0.06,xx+0.06,-0.34,0.34,13.62,13.86,0.004)
    for sy in (-1,1): G.bx(("girder","STEEL"),xx-0.07,xx+0.07,sy*0.34-(0.012 if sy>0 else 0),sy*0.34+(0.012 if sy<0 else 0)+(0.0),13.60,13.88,0.003)
# ---- end trucks, runway beams, hangers
for sx in (-1,1):
    xc=sx*7.6; fx0,fx1=sorted((sx*7.2,sx*8.0))
    G.bx(("truck","YELLOW"),fx0,fx1,-1.05,1.05,13.50,14.50,0.012)                                          # end carriage frame
    G.bx(("truck","STEEL"),fx0+(0.0 if sx<0 else 0.0),fx1,-0.30,0.30,14.50,14.54,0.003)
    for yy in (-1,1):
        G.bx(("truck","YELLOW"),xc-0.14,xc+0.14,yy*1.05+(0.0 if yy<0 else 0.0),yy*1.05+yy*0.08,13.78,14.22,0.01)                       # buffers
        G.bx(("truck","BLACK"),xc-0.14,xc+0.14,yy*1.13,yy*1.13+yy*0.012,13.78,14.22,0.003)
    for xx in (xc-0.215,xc+0.215):                                                                       # cheek plates up each side of the runway flange
        G.bx(("truck","AUDI"),xx-0.015,xx+0.015,-0.46,0.46,13.90,14.96,0.006)
    for yy in (-0.32,0.32):
        for ox in (-0.145,0.145):                                                                         # wheels on the bottom flange
            G.cylx(("truck","STEEL"),xc+ox-0.03,xc+ox+0.03,yy,14.75,0.115,18,0.0)
        G.cylx(("truck","STEEL"),xc-0.215,xc-0.175,yy,14.75,0.022,8); G.cylx(("truck","STEEL"),xc+0.175,xc+0.215,yy,14.75,0.022,8)
        for ox in (-0.145,0.145): G.cylx(("truck","BLACK"),xc+ox-0.032,xc+ox+0.032,yy,14.75,0.045,10,0.0)
    G.bx(("truck","AUDI_SATIN"),xc+sx*0.30,xc+sx*0.62,0.45,1.02,13.95,14.35,0.01)                       # drive motor + gearbox on the outer face
    G.cylx(("truck","AUDI"),xc+sx*0.62,xc+sx*0.90,0.735,14.15,0.115,16,0.0); G.cylx(("truck","STEEL"),xc+sx*0.90,xc+sx*0.95,0.735,14.15,0.04,8)
    G.bx(("runway","STEEL"),xc-0.15,xc+0.15,-3.50,3.50,14.60,14.64,0.004); G.bx(("runway","STEEL"),xc-0.15,xc+0.15,-3.50,3.50,15.36,15.40,0.004)   # I beam flanges
    G.bx(("runway","STEEL"),xc-0.010,xc+0.010,-3.50,3.50,14.64,15.36,0.002)                                   # web
    for yy in range(-7,8):
        G.bx(("runway","STEEL"),xc-0.14,xc-0.011,yy*0.45-0.006,yy*0.45+0.006,14.64,15.36,0.002) if abs(yy)>0 else None
    for yy in (-3.50,3.50): G.bx(("runway","YELLOW"),xc-0.15,xc+0.15,yy-(0.01 if yy>0 else 0.0),yy+(0.0 if yy>0 else 0.01),14.60,15.40,0.004)   # end plates
    for yy in (-3.1,-1.2,1.2,3.1):                                                                        # roof hangers: clevis on the top flange, pinned tie rod, turnbuckle, roof plate
        for xx in (xc-0.085,xc+0.085): G.bx(("hanger","STEEL"),xx-0.008,xx+0.008,yy-0.07,yy+0.07,15.36,15.64,0.004)
        G.cylx(("hanger","IRON"),xc-0.115,xc+0.115,yy,15.57,0.022,10,0.0); G.cylx(("hanger","STEEL"),xc-0.115,xc-0.100,yy,15.57,0.031,8,0.0); G.cylx(("hanger","STEEL"),xc+0.100,xc+0.115,yy,15.57,0.031,8,0.0)
        G.cyl(("hanger","GALV"),xc,yy,15.60,15.90,0.024,10,0.0)
        G.lathe(("hanger","IRON"),xc,yy,[(0.0,15.70),(0.040,15.71),(0.040,15.80),(0.0,15.81)],seg=10) if False else G.cyl(("hanger","IRON"),xc,yy,15.70,15.80,0.040,10,0.0)
        upper_x=sx*7.5
        G.prism(('hanger','GALV'),(xc,yy,15.80),(upper_x,yy,16.565),.018,.018,12,0,True,0)
        G.bx(("hanger","STEEL"),upper_x-0.17,upper_x+0.17,yy-0.17,yy+0.17,16.565,16.60,0.004)
        for ox in (-1,1):
            for oy in (-1,1): G.cyl(("hanger","STEEL"),upper_x+ox*0.13,yy+oy*0.13,16.60,16.612,0.014,6,0.0)
        for ox in (-1,1): G.bx(("hanger","STEEL"),upper_x+ox*0.05-0.007,upper_x+ox*0.05+0.007,yy-0.06,yy+0.06,16.465,16.565,0.003)
        SUPPORT.register('pool roof suspension','gantry hanger '+str((xc,yy)),
            'RH pool hanger STEEL','RH walls girders STEEL',
            [(upper_x+dx,yy+dy,16.60) for dx in (-.10,.10) for dy in (-.10,.10)],
            (0,0,1),'suspension')
# ---- hoist trolley on the rails (x = 0), drum, ropes, hook block
HX=0.0
for sy in (-1,1):
    for ox in (-0.38,0.38): G.cyly(("hoist","STEEL"),HX+ox,sy*0.52-0.03,sy*0.52+0.03,14.69,0.095,16,0.0)
    G.bx(("hoist","ORANGE"),HX-0.52,HX+0.52,sy*0.52-0.11,sy*0.52+0.11,14.74,14.98,0.012)                     # trolley side frames
G.bx(("hoist","ORANGE"),HX-0.52,HX-0.43,-0.52,0.52,14.74,14.98,0.012); G.bx(("hoist","ORANGE"),HX+0.43,HX+0.52,-0.52,0.52,14.74,14.98,0.012)
G.cyly(("hoist","STEEL"),HX,-0.40,0.40,15.12,0.17,24,0.0)                                                    # rope drum
for k in range(6): G.cyly(("hoist","AUDI"),HX,-0.38+k*0.14,-0.38+k*0.14+0.012,15.12,0.19,24,0.0)
G.bx(("hoist","AUDI_SATIN"),HX-0.30,HX+0.30,0.40,0.70,14.98,15.34,0.012); G.cyly(("hoist","AUDI"),HX,0.70,1.02,15.16,0.14,16,0.0)   # gearbox + motor
G.bx(("hoist","STEEL"),HX-0.30,HX+0.30,-0.52,-0.40,14.98,15.34,0.01)
G.bx(("hoist","YELLOW"),HX-0.14,HX+0.14,-0.62,-0.585,15.05,15.22,0.004)                                      # name plate
for sx in (-1,1):
    G.tube(("hoist","BLACK"),[(HX+sx*0.075,-0.02,15.12-0.17),(HX+sx*0.075,-0.02,12.34)],0.009,6)                # two ropes down to the block
G.bx(("hoist","YELLOW"),HX-0.125,HX+0.125,-0.07,0.07,12.12,12.36,0.012); G.cyly(("hoist","STEEL"),HX,-0.085,0.085,12.24,0.055,16,0.0)
for sx in (-1,1): G.cyly(("hoist","STEEL"),HX+sx*0.075,-0.075,0.075,12.34,0.040,12,0.0)
G.bx(("hoist","BLACK"),HX-0.126,HX+0.126,-0.072,0.072,12.15,12.175,0.003)
G.cyl(("hoist","STEEL"),HX,0.0,12.04,12.12,0.032,10,0.0); G.cyl(("hoist","IRON"),HX,0.0,12.0,12.04,0.048,12,0.0)
pts=[(HX,0.0,12.0),(HX,0.0,11.90)]+[(HX+0.075+0.075*math.cos(a*D2R),0.0,11.90+0.075*math.sin(a*D2R)) for a in range(180,361,30)]+[(HX+0.15,0.0,11.98)]
G.tube(("hoist","IRON"),pts,0.022,8)
# ---- cable festoon along the -y girder: C-rail on brackets, carriers and hanging loops
G.bx(("festoon","STEEL"),-6.9,-0.20,-0.88,-0.84,14.20,14.25,0.003)
G.bx(("festoon","STEEL"),-.225,-.20,-.89,-.83,14.14,14.25,.002)
for k in range(0,14):
    xx=-6.8+k*0.5
    G.bx(("festoon","STEEL"),xx-0.012,xx+0.012,-0.84,-0.529,14.18,14.24,0.002)                                 # welded engagement with girder web
    G.bx(("festoon","BLACK"),xx-0.02,xx+0.02,-0.89,-0.83,14.14,14.20,0.004)                                    # carrier trolley
    if k==13:continue
    xn=xx+0.5*(1.0-0.04*k/13); sag=0.30-0.015*k
    loop=[(xx+0.5*t,-0.865,14.14-sag*math.sin(math.pi*t)**0.8-0.02*abs(math.sin(3*math.pi*t))) for t in (0,0.15,0.3,0.5,0.7,0.85,1.0)]
    G.tube(("festoon","BLACK"),loop,0.016,6)
G.tube(("festoon","BLACK"),[(-0.30,-0.865,14.14),(-0.25,-0.80,14.20),(HX-0.35,-0.65,14.65),(HX-0.30,-0.62,14.9)],0.016,6)         # final carrier into trolley lead
# ---- inspection platform on the +y side: grating deck, brackets, handrail, toe board (two stretches)
for (x0,x1) in ((2.8,7.0),(-7.0,-2.8)):
    G.bx(("platform","TREAD"),x0,x1,0.72,1.42,13.85,13.865,0.004)                                          # tread plate deck
    for yy in (0.74,1.40): G.bx(("platform","STEEL"),x0,x1,yy-0.025,yy+0.025,13.80,13.85,0.003)                 # edge angles
    n=int((x1-x0)/0.9)+1
    for i in range(n+1):
        xx=x0+(x1-x0)*i/n
        G.hull(("platform","STEEL"),[(xx-0.006,0.545,13.84),(xx+0.006,0.545,13.84),(xx-0.006,1.40,13.84),(xx+0.006,1.40,13.84),(xx-0.006,0.545,13.62),(xx+0.006,0.545,13.62)],0.0)
        G.bx(("platform","YELLOW"),xx-0.025,xx+0.025,1.395,1.445,13.865,14.97,0.004)                            # handrail post
    G.cylx(("platform","YELLOW"),x0,x1,1.42,14.95,0.0215,10,0.0); G.cylx(("platform","YELLOW"),x0,x1,1.42,14.42,0.0195,10,0.0)
    G.bx(("platform","YELLOW"),x0,x1,1.415,1.43,13.865,13.965,0.003)
    for xx in (x0,x1):                                                                                    # end rail returns
        # Build the positive-X access opening directly. Boolean-cutting the
        # merged rail assembly could erase disconnected returns at other ends.
        spans=((0.74,0.79),(1.35,1.42)) if abs(xx-7.0)<1e-6 else ((0.74,1.42),)
        for ya,yb in spans:
            G.cyly(("platform","YELLOW"),xx,ya,yb,14.95,0.0215,10,0.0)
            G.cyly(("platform","YELLOW"),xx,ya,yb,14.42,0.0195,10,0.0)
        G.bx(("platform","YELLOW"),xx-0.025,xx+0.025,0.715,0.765,13.865,14.97,0.004)
# ---- two service luminaires hung between the girders
for xx in (-3.7,3.7):
    for yy in (-0.46,0.46): G.bx(("lamp","STEEL"),xx-0.30,xx-0.27,yy-0.04,yy+0.04,13.44,13.52,0.002); G.bx(("lamp","STEEL"),xx+0.27,xx+0.30,yy-0.04,yy+0.04,13.44,13.52,0.002)
    G.bx(("lamp","STEEL"),xx-0.33,xx+0.33,-0.46,0.46,13.40,13.44,0.003)                                    # hanger bar under the lower flanges
    G.bx(("lamp","YELLOW"),xx-0.30,xx+0.30,-0.28,0.28,13.28,13.40,0.012)                                    # fixture body
    G.bx(("lamp","LAMPREAL"),xx-0.26,xx+0.26,-0.24,0.24,13.272,13.282,0.002)                                 # diffuser
    G.bx(("lamp","BLACK"),xx-0.31,xx+0.31,-0.29,-0.275,13.28,13.40,0.003)
gobj=G.build(BANKC,"RH pool",M)
print("rh_pool_surround: gantry objects",len(gobj))
# ================================================================================================ neutral lining (palette audit: teal -> neutral off-white tile)
mt=bpy.data.materials.get("R2 pool tile")
if mt:
    for nd in mt.node_tree.nodes:
        if nd.type=='MIX':
            for i in nd.inputs:
                if i.type=='RGBA' and not i.is_linked:
                    c=i.default_value
                    if abs(c[0]-0.069)<0.01 and abs(c[1]-0.172)<0.01: i.default_value=(0.32,0.325,0.32,1.0)      # tile body: off-white (was teal)
                    elif abs(c[0]-0.10)<0.01 and abs(c[1]-0.22)<0.01: i.default_value=(0.20,0.203,0.20,1.0)      # tile edge / chip colour (was teal)
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("rh_pool_surround: saved",DST)
