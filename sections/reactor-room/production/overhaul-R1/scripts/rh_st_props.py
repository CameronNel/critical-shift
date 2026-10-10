"""STATIONS pass, props: wall lockers, roller tool chests, water-filled barriers, spill pallets with drums, stools, floor drains, bollards, traffic cones, fire extinguishers, a leaning ladder.
All grouped with intent around the stations (positions follow the previous dressing so routes stay as they were)."""
import math
from mathutils import Vector
import rh_stlib as S
import rh_support_registry as SUPPORT
def locker_bank(K,origin,yaw,n,step,door_m,tag):
    """n steel lockers side by side; origin = back-centre of the first locker, local x out of the wall, y along the row (step per locker)"""
    g='lock'
    for i in range(n):
        K.begin(origin[0]+0,origin[1]+0,yaw)
        c=i*step; D=0.42; w=0.40
        K.bx((g,'STEEL'),0.02,D-0.02,c-w/2+0.01,c+w/2-0.01,0.0,0.10,0.003)
        K.bx((g,'AUDI_SATIN'),0.0,D,c-w/2,c+w/2,0.10,1.90,0.008)
        K.hull((g,'AUDI_SATIN'),[(0.0,c-w/2,1.90),(D,c-w/2,1.90),(0.0,c+w/2,1.90),(D,c+w/2,1.90),(0.02,c-w/2,1.97),(D*0.55,c-w/2,1.93),(0.02,c+w/2,1.97),(D*0.55,c+w/2,1.93)],0.004)
        S.door(K,g,'+x',D,c-w/2+0.006,c+w/2-0.006,0.13,1.88,'l0',door_m,'none',proud=0.006)
        S.louvres(K,g,'STEEL','+x',D+0.005,c-w/2+0.05,c+w/2-0.05,1.58,1.82,4,0.012,False)
        S.louvres(K,g,'STEEL','+x',D+0.005,c-w/2+0.05,c+w/2-0.05,0.19,0.36,3,0.010,False)
        S.handle_bar(K,g,'+x',D+0.006,c+w/2-0.055,1.02,0.16,0.0,'STEEL',True)
        K.bx((g,'STEEL'),D+0.006,D+0.014,c+w/2-0.12,c+w/2-0.03,0.84,0.90,0.002)                       # hasp
        K.bx((g,'BRASS'),D+0.014,D+0.04,c+w/2-0.095,c+w/2-0.055,0.80,0.86,0.003); S.torus(K,g,'STEEL',(D+0.027,c+w/2-0.075,0.865),(0,1,0),0.012,0.0035,8,4)
        K.bx((g,'WHITE'),D+0.006,D+0.011,c-0.09,c-0.01,1.52,1.57,0.001)
        K.end()
def tool_chest(K,cx,cy,yaw,m_front='RED'):
    g='chest'; K.begin(cx,cy,yaw); W=0.80; D=0.52
    K.bx((g,'STEEL'),-D/2+0.03,D/2-0.03,-W/2+0.03,W/2-0.03,0.12,0.22,0.004)
    for sy in (-1,1):
        for sx in (-1,1):
            x,y=sx*(D/2-0.07),sy*(W/2-0.07); K.cyl((g,'STEEL'),x,y,0.075,0.12,0.012,8,0.0); K.prism((g,'RUBBER'),(x-0.014,y,0.065),(x+0.014,y,0.065),0.065,0.065,16,0.0,True,0.003)
    K.bx((g,'AUDI_SATIN'),-D/2,D/2,-W/2,W/2,0.22,0.86,0.01)
    K.bx((g,'GALV'),-D/2-0.01,D/2+0.01,-W/2-0.01,W/2+0.01,0.86,0.89,0.005)
    for (z0,z1) in ((0.25,0.40),(0.42,0.57),(0.59,0.72),(0.74,0.84)):
        S.door(K,g,'+x',D/2,-W/2+0.02,W/2-0.02,z0,z1,'l0',m_front,'bar',proud=0.004,gap=0.004)
    K.bx((g,'STEEL'),-D/2-0.03,-D/2+0.01,-W/2+0.1,W/2-0.1,0.89,1.02,0.004)                  # back rail
    for k in range(4): K.prism((g,'STEEL'),(-D/2-0.02,-0.30+k*0.2,0.95),(-D/2+0.12,-0.30+k*0.2,0.95),0.007,0.007,8,0.0,True,0.0)
    K.end()
def barrier(K,cx,cy,yaw):
    """Fabricated portable rail: two weighted feet, uprights, open handholds."""
    g='barr'; K.begin(cx,cy,yaw)
    for x in (-.43,.43):
        K.pillow((g,'RUBBER'),x-.14,x+.14,-.20,.20,0,.065,.015,2)
        K.bx((g,'STEEL'),x-.09,x+.09,-.12,.12,.065,.09,.008)
        K.bx((g,'ORANGE'),x-.035,x+.035,-.045,.045,.09,.72,.008)
        for y in (-.09,.09): S.anchor(K,g,x,y,.09,.008,.022)
    K.bx((g,'ORANGE'),-.57,.57,-.035,.035,.57,.66,.008)
    K.bx((g,'ORANGE'),-.57,.57,-.035,.035,.29,.38,.008)
    for x in (-.535,.535):
        K.bx((g,'ORANGE'),x-.035,x+.035,-.035,.035,.38,.57,.008)
    for face,p in (('-y',-.035),('+y',.035)):
        for x in (-.32,0,.32):
            S.nameplate(K,g,face,p,x,.335,.18,.065,'WHITE',False)
    K.end()
def spill_pallet(K,cx,cy,w=1.0,d=1.0):
    """Open containment pan with a recessed bottom and removable grate."""
    g='pal'
    for dx in (-w*.37,w*.37):
        K.bx((g,'BLACK'),cx+dx-.07,cx+dx+.07,cy-d/2,cy+d/2,0,.055,.005)
    K.bx((g,'YELLOW'),cx-w/2,cx+w/2,cy-d/2,cy+d/2,.055,.075,.005)
    for sy in (-1,1):
        yy=cy+sy*(d/2-.0175)
        K.bx((g,'YELLOW'),cx-w/2,cx+w/2,yy-.0175,yy+.0175,.075,.145,.004)
    for sx in (-1,1):
        xx=cx+sx*(w/2-.0175)
        K.bx((g,'YELLOW'),xx-.0175,xx+.0175,cy-d/2+.035,cy+d/2-.035,.075,.145,.004)
    # No slab immediately beneath the grate: the recessed pan is visibly open.
    for sy in (-1,1):
        yy=cy+sy*d*.26
        K.bx((g,'IRON'),cx-w/2+.035,cx+w/2-.035,yy-.015,yy+.015,.075,.110,.002)
    for k in range(13):
        xx=cx-w/2+.055+k*(w-.11)/12
        K.bx((g,'GALV'),xx-.012,xx+.012,cy-d/2+.035,cy+d/2-.035,.110,.135,.002)
def stool(K,x,y):
    g='stool'
    K.prism((g,'RUBBER'),(x,y,0.48),(x,y,0.535),0.175,0.17,20,0.0,True,0.008); K.prism((g,'STEEL'),(x,y,0.445),(x,y,0.48),0.15,0.15,20,0.0,True,0.0)
    for k in range(3):
        th=k*2*math.pi/3+0.4; K.prism((g,'STEEL'),(x+0.11*math.cos(th),y+0.11*math.sin(th),0.445),(x+0.19*math.cos(th),y+0.19*math.sin(th),0.025),0.019,0.019,12,0.0,True,0.0)
    for k in range(3):
        th=k*2*math.pi/3+.4
        K.cyl((g,'RUBBER'),x+.19*math.cos(th),y+.19*math.sin(th),0,.03,.028,12,0)
    S.torus(K,g,'STEEL',(x,y,0.22),(0,0,1),0.154,0.014,20,6)
def drain(K,x,y,yaw):
    """Recessed removable grille seated in the matching floor-stage pocket."""
    g='drain'; K.begin(x,y,yaw)
    for xx in (-.315,.315): K.bx((g,'IRON'),xx-.015,xx+.015,-.24,.24,-.04,.002,.002)
    for yy in (-.225,.225): K.bx((g,'IRON'),-.30,.30,yy-.015,yy+.015,-.04,.002,.002)
    K.bx((g,'BLACK'),-.30,.30,-.21,.21,-.18,-.17,0)
    for k in range(9):
        xx=-.27+k*.0675
        K.bx((g,'IRON'),xx-.015,xx+.015,-.21,.21,-.035,.001,.002)
    for yy in (-.12,.12): K.bx((g,'STEEL'),-.30,.30,yy-.008,yy+.008,-.055,-.035,0)
    K.end()
def bollard(K,x,y):
    g='boll'
    K.bx((g,'STEEL'),x-0.12,x+0.12,y-0.12,y+0.12,0.0,0.022,0.003)
    for dx in (-0.085,0.085):
        for dy in (-0.085,0.085): K.cyl((g,'STEEL'),x+dx,y+dy,0.022,0.04,0.011,6,0.0)
    K.cyl((g,'STEEL'),x,y,.022,.065,.092,24,0)
    K.prism((g,'YELLOW'),(x,y,0.022),(x,y,0.90),0.075,0.075,18,0.0,True,0.0)
    K.prism((g,'STEEL'),(x,y,0.90),(x,y,0.94),0.082,0.082,18,0.0,True,0.004); S.lathe(K,(g,'YELLOW'),x,y,[(.080,.94),(.078,.949),(.067,.953),(0,.953)],seg=24)
    K.prism((g,'BLACK'),(x,y,0.30),(x,y,0.45),0.077,0.077,18,0.0,False,0.0); K.prism((g,'WHITE'),(x,y,0.62),(x,y,0.68),0.078,0.078,18,0.0,False,0.0)
def extinguisher(K,x,y,face):
    """CO2 / powder extinguisher on a wall bracket; face = direction away from the wall"""
    g='ext'; n=S.nrm(face)
    old={mk:set(bm.verts) for (gg,mk),bm in K.bm.items() if gg==g}
    sc=SUPPORT.bpy.context.scene; dg=SUPPORT.bpy.context.evaluated_depsgraph_get()
    origin=Vector((x,y,1.0))+n*.60; target=None
    for _ in range(24):
        hit,loc,normal,idx,ob,mw=sc.ray_cast(dg,origin,-n,distance=1.50)
        if not hit: break
        if ob.name.startswith('RH walls '): target=ob.name; break
        origin=loc-n*.001
    if target is None: raise RuntimeError('No wall support for extinguisher')
    actual_n=Vector((normal.x,normal.y,0)).normalized()
    p=loc+actual_n*.088; x,y=p.x,p.y
    rotation=n.rotation_difference(actual_n)
    c=Vector((x,y,0.0))
    S.lathe(K,(g,'RED'),x,y,[(0.0,0.30),(0.06,0.30),(0.075,0.33),(0.077,0.40),(0.077,0.62),(0.072,0.70),(0.04,0.74),(0.0,0.745)],seg=20)
    K.cyl((g,'BRASS'),x,y,0.74,0.80,0.022,10,0.0); K.prism((g,'BLACK'),(x,y,0.78),(x+n.x*0.07,y+n.y*0.07,0.78),0.012,0.012,6,0.0,True,0.0)
    K.prism((g,'BLACK'),(x,y,0.80),(x+n.x*0.05,y+n.y*0.05,0.84),0.010,0.010,6,0.0,True,0.0)
    K.tube((g,'BLACK'),[(x+0.02,y+0.02,0.76),(x+n.x*0.10+0.03,y+n.y*0.10+0.03,0.60),(x+n.x*0.10+0.04,y+n.y*0.10+0.04,0.46),(x+n.x*0.04,y+n.y*0.04,0.40)],0.008,6)
    for z in (0.46,0.62): K.prism((g,'STEEL'),(x,y,z),(x,y,z+0.03),0.081,0.081,20,0.0,True,0.0)
    K.box((g,'STEEL'),x-n.x*0.078,y-n.y*0.078,0.40,0.70,0.02 if face in('+x','-x') else 0.10,0.10 if face in('+x','-x') else 0.02,0.0,0.003)
    for (gg,mk),bm in K.bm.items():
        if gg==g:
            for v in bm.verts:
                if v not in old.get(mk,set()):
                    v.co=c+rotation@(v.co-c);v.co.z+=.45
    SUPPORT.register('stations props','extinguisher wall bracket','RH stations props',target,[(loc.x,loc.y,z) for z in (.89,1.11)],tuple(-v for v in actual_n),'wall')

def _registered(fn):
    def wrapped(K,*a,**kw):
        result=fn(K,*a,**kw); name=fn.__name__; target='R2 floor'; d=(0,0,-1); kind='floor'
        if name=='locker_bank':
            origin,yaw,n,step=a[:4]
            pts=SUPPORT.world(origin,yaw,[(x,i*step+dy,0) for i in range(n) for x in (.08,.34) for dy in (-.12,.12)])
        elif name=='tool_chest':
            x,y,yaw=a[:3];pts=SUPPORT.world((x,y),yaw,[(sx*.19,sy*.33,0) for sx in (-1,1) for sy in (-1,1)])
        elif name=='barrier':
            x,y,yaw=a[:3];pts=SUPPORT.world((x,y),yaw,[(sx*.43,0,0) for sx in (-1,1)])
        elif name=='spill_pallet':
            x,y=a[:2];w=a[2] if len(a)>2 else 1.;pts=[(x+dx*w*.37,y+dy*.25,0) for dx in (-1,1) for dy in (-1,1)]
        elif name=='stool':
            x,y=a[:2];pts=[(x+.19*math.cos(k*2*math.pi/3+.4),y+.19*math.sin(k*2*math.pi/3+.4),0) for k in range(3)]
        elif name=='drain':
            x,y,yaw=a[:3];pts=SUPPORT.world((x,y),yaw,[(sx*.315,sy*.20,-.04) for sx in (-1,1) for sy in (-1,1)])
        elif name=='bollard':
            x,y=a[:2];pts=[(x+dx*.07,y+dy*.07,0) for dx in (-1,1) for dy in (-1,1)]
        elif name=='extinguisher':
            x,y,face=a[:3];n=S.nrm(face);pts=[(x-n.x*.088,y-n.y*.088,z) for z in (.44,.66)]
            target='RH walls concrete CONC_POUR';d=tuple(-v for v in n);kind='wall'
        elif name=='ladder':
            x,y=a[:2];pts=[(x,y+dy*.20,0) for dy in (-1,1)]
        else: raise RuntimeError(name)
        subject='RH stations spill pallets' if name=='spill_pallet' else 'RH stations props'
        SUPPORT.register('stations props',name,subject,target,pts,d,kind)
        return result
    return wrapped

for _name in ('locker_bank','tool_chest','barrier','spill_pallet','stool','drain','bollard'):
    globals()[_name]=_registered(globals()[_name])
def ladder(K,x,y):
    """aluminium straight ladder leaning on the east wall"""
    g='ladd'; z1=2.55
    from mathutils import Vector
    sc=SUPPORT.bpy.context.scene;dg=SUPPORT.bpy.context.evaluated_depsgraph_get()
    origin=Vector((x,y,z1));obj=None
    for _ in range(24):
        hit,loc,normal,idx,found,mw=sc.ray_cast(dg,origin,Vector((1,0,0)),distance=1.)
        if not hit: break
        if found.name.startswith('RH walls'): obj=found;break
        origin=loc+Vector((.0001,0,0))
    if obj is None: raise RuntimeError('No east wall contact for leaning ladder')
    lean=loc.x-x-.017
    for s in (-1,1):
        K.prism((g,'GALV'),(x,y+s*0.20,0.0),(x+lean,y+s*0.20,z1),0.017,0.017,8,0.0,True,0.0)
        K.bx((g,'RUBBER'),x-0.03,x+0.03,y+s*0.20-0.02,y+s*0.20+0.02,0.0,0.03,0.002)
    for k in range(9):
        t=0.08+k*0.105; z=t*z1; K.prism((g,'GALV'),(x+lean*t,y-0.20,z),(x+lean*t,y+0.20,z),0.012,0.012,8,0.0,True,0.0)
    SUPPORT.register('stations props','leaning ladder top','RH stations props',obj.name,[(loc.x,y+dy*.20,z1) for dy in (-1,1)],(1,0,0),'wall')

ladder=_registered(ladder)
