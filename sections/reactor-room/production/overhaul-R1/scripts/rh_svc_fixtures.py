# Light FIXTURES for rh_services.py (exec'd inside its namespace: KS, KL, M, WALLS, bpy, Vector, helpers, COLL_LIGHT).
# Rebuilds the visible housings only: caged high-bay lamps, swing-arm task lamps (and stanchion lamps where no wall is near), beacon cages and domes, red emergency bulkheads, exit signs.
# The lights (and their stability drivers) are kept; static cool/blue lights are retinted neutral for the palette audit.
import colorsys
import rh_support_registry as SUPPORT
from mathutils.bvhtree import BVHTree
SUPPORT.reset('service fixtures')
_fixture_receivers=[]
for _ob in bpy.data.objects:
    if _ob.type!='MESH' or not _ob.name.startswith(('RH walls mass ','RH walls concrete ','RH walls cladding ','RH walls steel ','R2 floor')):continue
    _fixture_receivers.append((_ob.name,BVHTree.FromPolygons(
        [_ob.matrix_world@v.co for v in _ob.data.vertices],[list(f.vertices) for f in _ob.data.polygons])))
def fixture_hits(P,n,w,h):
    n=Vector(n).normalized();x=n.cross(Vector((0,0,1))).normalized();z=x.cross(n).normalized();seats=[]
    for sx in (-1,1):
        for sz in (-1,1):
            p=Vector(P)+x*(sx*w*.34)+z*(sz*h*.38);hits=[]
            for name,tree in _fixture_receivers:
                loc,normal,face,distance=tree.ray_cast(p+n,-n,2)
                if loc is not None and normal.dot(n)>.99:hits.append((distance,name,loc))
            if not hits:return None
            _,name,loc=min(hits,key=lambda row:row[0]);seats.append((p,name,loc))
    return seats
def fixture_seat(P,n,w=.12,h=.30):
    P=Vector(P);n=Vector(n).normalized();t=n.cross(Vector((0,0,1))).normalized()
    # Move a task bracket onto adjacent solid wall when its nominal position
    # falls inside a formed doorway. The arm still reaches the original lamp.
    offsets=[Vector((0,0,0))]
    for distance in (.25,.5,.75,1.,1.25,1.5):
        offsets.extend((Vector((0,0,distance)),t*distance,-t*distance))
    for offset in offsets:
        q=P+offset;hits=fixture_hits(q,n,w,h)
        if hits:return q+n*max((loc-p).dot(n) for p,name,loc in hits)
    raise RuntimeError('No actual wall seat for fixture '+str(tuple(P)))
_fixture_wall_plate=wall_plate
def wall_plate(K,P,n,w=.14,h=.22,t=.012,key=('R2 PIPING support','STEEL'),bk=('R2 PIPING bolt','STEEL'),up=(0,0,1)):
    P=fixture_seat(P,n,w,h);n=Vector(n).normalized()
    _fixture_wall_plate(K,P,n,w,h,t,key,bk,up)
    fixture_contact(P,n,w,h,'RH services '+key[0]+' '+key[1])
def fixture_contact(P,n,w,h,subject):
    n=Vector(n).normalized()
    for p,target,loc in fixture_hits(P,n,w,h):
        if (p-loc).dot(n)>.002:
            KL.prism(('fixture spacers','STEEL'),loc,p,.014,.014,12,0,True,0)
            SUPPORT.register('service fixtures','wall spacer','RH services fixture spacers STEEL',target,[loc],-n,'wall')
            target='RH services fixture spacers STEEL'
        SUPPORT.register('service fixtures','wall bearing',subject,target,[p],-n,'wall')
FX=lambda g,m: (g,m)
SHADOWLESS=("lens","cage","bulb","beacon")     # object visibility: these never block the lamp they surround
# ------------------------------------------------------------------ retint static blue/lavender lights (not the colour-driven state glow lights)
def _bad(c):
    h,s,v=colorsys.rgb_to_hsv(*[max(0,min(1,x)) for x in c[:3]]); return 150<=h*360<=310 and s>0.22 and v>0.02
retinted=[]
for o in bpy.data.objects:
    if o.type!='LIGHT': continue
    l=o.data; ad=l.animation_data
    driven_col=bool(ad and any(d.data_path=='color' for d in ad.drivers))
    if driven_col or not o.name.startswith("LP"): continue
    if _bad(l.color) or (l.color[2]>l.color[0]+0.08):               # bluish or lavender: neutral warm white, same energy
        l.color=(0.93,0.90,0.82); retinted.append(o.name)
print("lights retinted to neutral:",len(retinted))
# ------------------------------------------------------------------ helpers
def revolve(bm,c,axis,prof,seg=20,smooth=True):
    x,y,z=fr(axis); c=Vector(c); rings=[]
    for (r,t) in prof:
        if r<1e-6: rings.append([bm.verts.new(c+z*t)])
        else: rings.append([bm.verts.new(c+(x*math.cos(2*math.pi*k/seg)+y*math.sin(2*math.pi*k/seg))*r+z*t) for k in range(seg)])
    for a,b in zip(rings,rings[1:]):
        if len(a)==1 and len(b)==1: continue
        for k in range(seg):
            if len(a)==1: f=bm.faces.new((a[0],b[(k+1)%seg],b[k]))
            elif len(b)==1: f=bm.faces.new((a[k],a[(k+1)%seg],b[0]))
            else: f=bm.faces.new((a[k],a[(k+1)%seg],b[(k+1)%seg],b[k]))
            f.smooth=smooth
def wire_dome(K,key,c,axis,R,H,n=8,rings=(0.55,),wr=0.0045):
    """guard cage: n meridian wires from a base ring of radius R to an apex H along `axis`, plus latitude rings"""
    axis=Vector(axis).normalized(); x,y,z=fr(axis); c=Vector(c)
    torus(K,key,c,axis,R,wr*1.2,18,4)
    for i in range(n):
        a=2*math.pi*i/n; ra=x*math.cos(a)+y*math.sin(a); pts=[]
        for k in range(0,7):
            ph=math.pi/2*k/6; pts.append(c+ra*(R*math.cos(ph))+z*(H*math.sin(ph)))
        tube(K,key,pts,wr,4)
    for f in rings:
        ph=math.asin(f); torus(K,key,c+z*(H*f),axis,R*math.cos(ph),wr,18,4)
def dist_wall(P):
    wd=wall_of(WALLS,P); return wd
STEELK=FX("fixture","STEEL"); GALVK=FX("fixture","GALV"); BLK=FX("fixture","BLACK"); BOLT=FX("fixture bolt","STEEL")
# ------------------------------------------------------------------ 1. caged high-bay wash lamps on wall brackets (one per LP wash light)
for o in sorted([o for o in bpy.data.objects if o.type=='LIGHT' and o.name.startswith("LP wash")],key=lambda o:o.name):
    p=o.matrix_world.translation.copy(); wd=wall_of(WALLS,p)
    if not wd: continue
    w,d,u=wd; nn=Vector((w.n.x,w.n.y,0)); base=Vector((p.x,p.y,0))-nn*d
    za=p.z+0.20                                                # arm height above the lamp
    base=fixture_seat(Vector((base.x,base.y,za-.02)),nn,.12,.30)
    d=(Vector((p.x,p.y,za-.02))-base).dot(nn)
    # wall plate, cantilever arm, diagonal brace
    wall_plate(KL,Vector((base.x,base.y,za-0.02)),nn,0.12,0.30,0.012,STEELK,BOLT)
    bar(KL,STEELK,Vector((base.x,base.y,za))+nn*0.012,Vector((p.x,p.y,za)),0.05,0.04,(0,0,1),0.003)
    ln=d; bar(KL,STEELK,Vector((base.x,base.y,za-0.26))+nn*0.012,Vector((base.x,base.y,za))+nn*(ln*0.80)-Vector((0,0,0.03)),0.035,0.025,(0,0,1),0.002)
    # lamp: neck, cap, reflector dish, bulb (lens), guard cage
    KL.prism(STEELK,Vector((p.x,p.y,za)),Vector((p.x,p.y,za-0.07)),0.04,0.04,10,0.0,True,0.0)
    KL.prism(GALVK,Vector((p.x,p.y,za-0.07)),Vector((p.x,p.y,za-0.15)),0.11,0.10,18,0.0,True,0.0)
    KL.prism(FX("fixture dish","GALV"),Vector((p.x,p.y,za-0.15)),Vector((p.x,p.y,p.z-0.115)),0.10,0.27,22,0.0,False,0.0)
    torus(KL,GALVK,Vector((p.x,p.y,p.z-0.115)),(0,0,1),0.27,0.008,22,5)
    KL.prism(FX("bulb","LENS"),Vector((p.x,p.y,p.z-0.075)),Vector((p.x,p.y,p.z+0.06)),0.052,0.052,12,0.0,True,0.0)
    wire_dome(KL,FX("cage","GALV"),Vector((p.x,p.y,p.z-0.115)),(0,0,-1),0.27,0.15,8,(0.55,),0.0045)
    for k in range(4):                                         # cage clamp lugs
        a=math.pi/2*k+math.pi/4; obox(KL,STEELK,Vector((p.x,p.y,za-0.125))+Vector((math.cos(a),math.sin(a),0))*0.115,(1,0,0),(0,1,0),(0,0,1),0.012,0.012,0.012,0.002)
# ------------------------------------------------------------------ 2. task lamps: swing-arm jibs on the wall, stanchion lamps elsewhere
def _blockers():
    out=[]
    for ob in bpy.data.objects:
        if ob.type!='MESH' or ob.name.startswith(("RH services","LP ","CR ","CR_","R2 floor","MERGED 22","R2 w")): continue
        b=[ob.matrix_world@Vector(v) for v in ob.bound_box]; lo=Vector((min(v[i] for v in b) for i in range(3))); hi=Vector((max(v[i] for v in b) for i in range(3)))
        if (hi.x-lo.x)*(hi.y-lo.y)>40 or hi.z<0.15 or lo.z>3.0: continue
        out.append((lo,hi))
    return out
BLOCK=_blockers()
def free_spot(x,y,r=0.28):
    for lo,hi in BLOCK:
        if lo.x-r<x<hi.x+r and lo.y-r<y<hi.y+r and lo.z<2.2: return False
    for sx in (-1,1):
        for sy in (-1,1):
            p=Vector((x+sx*.11,y+sy*.11,.1))
            hits=[tree.ray_cast(p,Vector((0,0,-1)),.2) for name,tree in _fixture_receivers if name.startswith('R2 floor')]
            if not any(loc is not None and abs(loc.z)<.001 and normal.z>.99 for loc,normal,face,distance in hits):return False
    return True
def lamp_head(p,D):
    D=Vector(D).normalized(); x,y,z=fr(D); side=D.cross((0,0,1)); side=side.normalized() if side.length>0.1 else Vector((1,0,0))
    R0=p-D*0.10; F=p+D*0.14
    KL.prism(FX("fixture dish","GALV"),R0,F,0.075,0.145,18,0.0,False,0.0)
    KL.prism(STEELK,R0-D*0.03,R0,0.08,0.08,14,0.0,True,0.0); sphere(KL,STEELK,R0-D*0.03,0.07,12,6)
    torus(KL,GALVK,F,D,0.145,0.0065,18,4)
    KL.prism(FX("bulb","LENS"),p-D*0.02,p+D*0.09,0.045,0.05,12,0.0,True,0.0)
    wire_dome(KL,FX("cage","GALV"),F,D,0.145,0.07,6,(0.5,),0.0042)
    for s in(-1,1):                                           # pivot bolts and yoke ears
        c=p+side*(s*0.10)-D*0.01; KL.prism(BOLT,c,c+side*(s*0.025),0.012,0.012,6,0.0,True,0.0)
    return side
def jib(p,D,wall_hit):
    w,d,u=wall_hit; nn=Vector((w.n.x,w.n.y,0)); base=Vector((p.x,p.y,0))-nn*d; zm=p.z+0.42
    M0=Vector((base.x,base.y,zm)); H=Vector((p.x,p.y,p.z+0.24))
    M0=fixture_seat(M0,nn,.12,.22)
    wall_plate(KL,M0,nn,0.12,0.22,0.012,STEELK,BOLT)
    E=M0+(Vector((p.x,p.y,zm))-M0)*0.52+Vector((0,0,0.0)); E=Vector((E.x,E.y,zm+0.02))
    M1=M0+nn*0.05
    tube(KL,STEELK,[M1,E],0.017,8); tube(KL,STEELK,[E,H],0.015,8)
    for c in (M1,E,H): sphere(KL,STEELK,c,0.03,10,6)
    # spring strut for the parallel-arm look
    tube(KL,GALVK,[M1+Vector((0,0,-0.12)),E+Vector((0,0,-0.02))],0.006,6)
    side=lamp_head(p,D)
    for s in(-1,1): tube(KL,STEELK,[H,p+side*(s*0.10)+Vector((0,0,0.02))],0.009,6)
def stanchion_lamp(p,D):
    Dh=Vector((D.x,D.y,0)); Dh=Dh.normalized() if Dh.length>0.01 else Vector((1,0,0))
    for dist in (0.55,0.75,0.40):
        for rot in (0,60,-60,120,-120,180):
            q=Dh.copy(); q.rotate(__import__('mathutils').Matrix.Rotation(math.radians(rot),3,'Z')); b=Vector((p.x,p.y,0))-q*dist
            if free_spot(b.x,b.y,0.30): break
        else: continue
        break
    else: return False
    top=Vector((b.x,b.y,p.z+0.30))
    obox(KL,STEELK,Vector((b.x,b.y,0.008)),(1,0,0),(0,1,0),(0,0,1),0.15,0.15,0.008,0.003)
    for sx in(-1,1):
        for sy in(-1,1): hexnut(KL,BOLT,(b.x+sx*0.11,b.y+sy*0.11,0.02),(0,0,1),0.012,0.014)
    SUPPORT.register('service fixtures','task lamp floor base','RH services fixture STEEL','R2 floor',
        [(b.x+sx*.11,b.y+sy*.11,0) for sx in (-1,1) for sy in (-1,1)])
    KL.prism(STEELK,Vector((b.x,b.y,0.016)),top,0.032,0.026,10,0.0,True,0.0)
    for k in range(3):
        a=2*math.pi*k/3; bar(KL,STEELK,Vector((b.x,b.y,0.2)),Vector((b.x+math.cos(a)*0.14,b.y+math.sin(a)*0.14,0.02)),0.02,0.02,(0,0,1),0.002)
    H=Vector((p.x,p.y,p.z+0.24)); sphere(KL,STEELK,top,0.04,10,6); tube(KL,STEELK,[top,Vector((top.x,top.y,top.z+0.02)),H],0.017,8); sphere(KL,STEELK,H,0.03,10,6)
    side=lamp_head(p,D)
    for s in(-1,1): tube(KL,STEELK,[H,p+side*(s*0.10)+Vector((0,0,0.02))],0.009,6)
    return True
placed_task=[];skipped_task=[]
for o in sorted([o for o in bpy.data.objects if o.type=='LIGHT' and o.name.startswith("LP task")],key=lambda o:o.name):
    p=o.matrix_world.translation.copy(); D=o.matrix_world.to_quaternion()@Vector((0,0,-1)); wd=wall_of(WALLS,p)
    if o.name=='LP task console 8':
        # The original lamp is over the pool opening. A bolted console-cap
        # mount carries its arm; searching for a floor stand there is invalid.
        base=Vector((-1.12,-3.43,1.285));top=Vector((base.x,base.y,p.z+.24))
        obox(KL,STEELK,base+Vector((0,0,.008)),(1,0,0),(0,1,0),(0,0,1),.04,.04,.008,.002)
        KL.prism(STEELK,base+Vector((0,0,.016)),top,.022,.020,16,0,True,0)
        H=p+Vector((0,0,.24));tube(KL,STEELK,[top,H],.018,12);sphere(KL,STEELK,H,.03,12,6)
        side=lamp_head(p,D)
        for s in (-1,1):tube(KL,STEELK,[H,p+side*(s*.10)+Vector((0,0,.02))],.009,8)
        SUPPORT.register('service fixtures','console task lamp cap','RH services fixture STEEL','RH pool console STEEL',
            [(base.x+dx,base.y+dy,base.z) for dx in (-.025,.025) for dy in (-.025,.025)])
        placed_task.append(o.name+' (console mount)')
    elif wd and 0.25<wd[1]<1.7: jib(p,D,wd); placed_task.append(o.name)
    elif stanchion_lamp(p,D): placed_task.append(o.name+" (stanchion)")
    else: skipped_task.append(o.name)
print("task lamp housings:",placed_task,"skipped:",skipped_task)
# ------------------------------------------------------------------ 3. beacons (red rotating lights): static base + guard cage, lens dome rebuilt in place
for k in range(3):
    piv=bpy.data.objects.get(f"LP beacon {k} pivot"); lens=bpy.data.objects.get(f"LP beacon {k} lens")
    if not(piv and lens): continue
    P=piv.matrix_world.translation.copy(); wd=wall_of(WALLS,P)
    nn=Vector((wd[0].n.x,wd[0].n.y,0)) if wd else Vector((0,0,1))
    base=fixture_seat(Vector((P.x,P.y,P.z))-nn*(wd[1] if wd else 0),nn,.22,.22)
    fixture_contact(base,nn,.22,.22,'RH services beacon base STEEL')
    # dome in the lens object (world coordinates, object origin stays 0)
    me=lens.data; me.clear_geometry(); bm=bmesh.new()
    revolve(bm,base+nn*0.03,nn,[(0.085,0.0),(0.085,0.04),(0.07,0.085),(0.04,0.118),(0.0,0.132)],20)
    bm.to_mesh(me); bm.free(); lens.visible_shadow=False
    KL.prism(FX("beacon base","STEEL"),base,base+nn*0.035,0.15,0.15,22,0.0,True,0.0)
    KL.prism(FX("beacon base","STEEL"),base+nn*0.035,base+nn*0.06,0.115,0.115,22,0.0,True,0.0)
    x_,y_,z_=fr(nn)
    for i in range(4):
        a=2*math.pi*(i+0.5)/4; hexnut(KL,FX("beacon base","STEEL"),base+nn*0.04+(x_*math.cos(a)+y_*math.sin(a))*0.13,nn,0.011,0.012)
    wire_dome(KL,FX("beacon cage","GALV"),base+nn*0.06,nn,0.115,0.15,8,(0.5,),0.005)
# ------------------------------------------------------------------ 4. red emergency bulkhead lamps (caged, state-driven emission through the shared emergency lens material)
EM=[(2,1.5),(2,10.5),(4,2.5),(4,9.5),(6,1.5),(6,10.5)]
for wi,uu in EM:
    w=WALLS[wi]; zz=4.4; base=w.pt(uu,0.0); b3=Vector((base.x,base.y,zz)); nn=Vector((w.n.x,w.n.y,0))
    b3=fixture_seat(b3,nn,.20,.24)
    fixture_contact(b3,nn,.20,.24,'RH services emergency housing STEEL')
    obox(KL,FX("emergency housing","STEEL"),b3+nn*0.04,w.t.to_3d(),nn,(0,0,1),0.10,0.04,0.12,0.012)
    for sx in(-1,1):
        for sz in(-1,1): hexnut(KL,BOLT,b3+nn*0.082+w.t.to_3d()*(sx*0.075)+Vector((0,0,sz*0.095)),nn,0.008,0.008)
    KL.prism(FX("emergency lens","EMERG"),b3+nn*0.08,b3+nn*0.17,0.062,0.052,16,0.0,True,0.0)
    wire_dome(KL,FX("emergency cage","GALV"),b3+nn*0.08,nn,0.085,0.13,6,(0.5,),0.0045)
# ------------------------------------------------------------------ 5. exit signs (white face, small green pictogram), on two short brackets
for (x,y) in ((9.66,-6.55),(-2.2,10.39),(-10.39,-2.2)):
    wd=wall_of(WALLS,Vector((x,y,0))); w,dd,uu=wd; nn=Vector((w.n.x,w.n.y,0)); t=Vector((w.t.x,w.t.y,0)); zc=5.21
    c=Vector((x,y,zc)); base=c-nn*dd
    base=fixture_seat(base,nn,.50,.12)
    obox(KL,FX("exit housing","BLACK"),c,t,nn,(0,0,1),0.26,0.032,0.10,0.006)
    obox(KL,FX("exit face","EXITFACE"),c+nn*0.0335,t,nn,(0,0,1),0.235,0.002,0.08,0.0)
    # pictogram: door frame, running figure (head, body, legs) and arrow, all small and green
    g=FX("exit green","EXITGREEN"); cc=c+nn*0.036
    for sx,wd_ in((-0.115,0.012),(-0.04,0.012)): obox(KL,g,cc+t*(sx-0.12)+Vector((0,0,0)),t,nn,(0,0,1),wd_/2,0.0008,0.055,0.0)
    obox(KL,g,cc+t*(-0.2)+Vector((0,0,0.052)),t,nn,(0,0,1),0.036,0.0008,0.006,0.0)
    sphere(KL,g,cc+t*(-0.16)+nn*0.001+Vector((0,0,0.035)),0.011,8,5)
    bar(KL,g,cc+t*(-0.16)+Vector((0,0,0.02)),cc+t*(-0.14)+Vector((0,0,-0.01)),0.012,0.001,nn,0.0)
    bar(KL,g,cc+t*(-0.14)+Vector((0,0,-0.01)),cc+t*(-0.17)+Vector((0,0,-0.04)),0.011,0.001,nn,0.0)
    bar(KL,g,cc+t*(-0.14)+Vector((0,0,-0.01)),cc+t*(-0.11)+Vector((0,0,-0.04)),0.011,0.001,nn,0.0)
    bar(KL,g,cc+t*(0.01)+Vector((0,0,0)),cc+t*(0.12)+Vector((0,0,0)),0.012,0.001,nn,0.0)
    bar(KL,g,cc+t*(0.12)+Vector((0,0,0.02)),cc+t*(0.15)+Vector((0,0,0)),0.011,0.001,nn,0.0); bar(KL,g,cc+t*(0.12)+Vector((0,0,-0.02)),cc+t*(0.15)+Vector((0,0,0)),0.011,0.001,nn,0.0)
    for s in(-1,1):
        wall_plate(KL,Vector((base.x,base.y,zc))+t*(s*0.18),nn,0.07,0.12,0.01,STEELK,BOLT)
        bar(KL,STEELK,Vector((base.x,base.y,zc))+t*(s*0.18)+nn*0.01,c+t*(s*0.18)-nn*0.0,0.03,0.03,(0,0,1),0.002)
fobjs=KL.build(COLL_LIGHT,"RH services",M)
for o in fobjs:
    if any(k in o.name for k in SHADOWLESS): o.visible_shadow=False
print("fixture objects:",len(fobjs),"verts",sum(len(o.data.vertices) for o in fobjs))
