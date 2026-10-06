"""STATIONS pass, props: wall lockers, roller tool chests, water-filled barriers, spill pallets with drums, stools, floor drains, bollards, traffic cones, fire extinguishers, a leaning ladder.
All grouped with intent around the stations (positions follow the previous dressing so routes stay as they were)."""
import math
from mathutils import Vector
import rh_stlib as S
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
    g='barr'; K.begin(cx,cy,yaw); L=1.2
    K.hull((g,'ORANGE'),[(-L/2,-0.20,0.0),(L/2,-0.20,0.0),(-L/2,0.20,0.0),(L/2,0.20,0.0),(-L/2+0.04,-0.095,0.70),(L/2-0.04,-0.095,0.70),(-L/2+0.04,0.095,0.70),(L/2-0.04,0.095,0.70)],0.012)
    for s in (-1,1):
        K.hull((g,'HAZARD'),[(-L/2+0.10,s*0.186,0.30),(L/2-0.10,s*0.186,0.30),(-L/2+0.10,s*0.152,0.52),(L/2-0.10,s*0.152,0.52),(-L/2+0.10,s*0.19,0.30),(L/2-0.10,s*0.19,0.30),(-L/2+0.10,s*0.156,0.52),(L/2-0.10,s*0.156,0.52)],0.0)
        K.hull((g,'WHITE'),[(-L/2+0.10,s*0.178,0.58),(L/2-0.10,s*0.178,0.58),(-L/2+0.10,s*0.168,0.65),(L/2-0.10,s*0.168,0.65),(-L/2+0.10,s*0.181,0.58),(L/2-0.10,s*0.181,0.58),(-L/2+0.10,s*0.171,0.65),(L/2-0.10,s*0.171,0.65)],0.0)
    K.cyl((g,'BLACK'),0.0,0.0,0.70,0.725,0.05,12,0.0)
    K.end()
def spill_pallet(K,cx,cy,w=1.0,d=1.0):
    g='pal'
    K.bx((g,'YELLOW'),cx-w/2,cx+w/2,cy-d/2,cy+d/2,0.0,0.10,0.008)
    K.bx((g,'BLACK'),cx-w/2+0.03,cx+w/2-0.03,cy-d/2+0.03,cy+d/2-0.03,0.085,0.10,0.001)
    for k in range(10): K.bx((g,'GALV'),cx-w/2+0.03+k*(w-0.06)/9-0.012,cx-w/2+0.03+k*(w-0.06)/9+0.012,cy-d/2+0.03,cy+d/2-0.03,0.10,0.135,0.002)
    for sy in (-1,1): K.bx((g,'YELLOW'),cx-w/2,cx+w/2,cy+sy*d/2-(0.025 if sy>0 else 0),cy+sy*d/2+(0.0 if sy>0 else 0.025),0.10,0.13,0.003)
    for sx in (-1,1): K.bx((g,'YELLOW'),cx+sx*w/2-(0.025 if sx>0 else 0),cx+sx*w/2+(0.0 if sx>0 else 0.025),cy-d/2,cy+d/2,0.10,0.13,0.003)
def stool(K,x,y):
    g='stool'
    K.prism((g,'RUBBER'),(x,y,0.43),(x,y,0.47),0.17,0.17,20,0.0,True,0.008); K.prism((g,'STEEL'),(x,y,0.40),(x,y,0.43),0.15,0.15,20,0.0,True,0.0)
    for k in range(3):
        th=k*2*math.pi/3+0.4; K.prism((g,'STEEL'),(x+0.11*math.cos(th),y+0.11*math.sin(th),0.40),(x+0.19*math.cos(th),y+0.19*math.sin(th),0.0),0.014,0.014,8,0.0,True,0.0)
    S.torus(K,g,'STEEL',(x,y,0.20),(0,0,1),0.155,0.008,14,5)
def drain(K,x,y,yaw):
    g='drain'; K.begin(x,y,yaw)
    K.bx((g,'IRON'),-0.33,0.33,-0.24,0.24,0.0,0.014,0.003)
    K.bx((g,'BLACK'),-0.30,0.30,-0.21,0.21,0.0,0.012,0.0)
    for k in range(9): xx=-0.27+k*0.0675; K.bx((g,'IRON'),xx-0.015,xx+0.015,-0.21,0.21,0.0,0.016,0.002)
    K.end()
def bollard(K,x,y):
    g='boll'
    K.bx((g,'STEEL'),x-0.12,x+0.12,y-0.12,y+0.12,0.0,0.012,0.002)
    for dx in (-0.085,0.085):
        for dy in (-0.085,0.085): K.cyl((g,'STEEL'),x+dx,y+dy,0.012,0.03,0.011,6,0.0)
    K.prism((g,'YELLOW'),(x,y,0.012),(x,y,0.90),0.075,0.075,18,0.0,True,0.0)
    K.prism((g,'STEEL'),(x,y,0.90),(x,y,0.94),0.082,0.082,18,0.0,True,0.004); K.lathe((g,'STEEL'),x,y,[(0.082,0.94),(0.066,0.965),(0.03,0.985),(0.0,0.99)],seg=18)
    K.prism((g,'BLACK'),(x,y,0.30),(x,y,0.45),0.077,0.077,18,0.0,False,0.0); K.prism((g,'WHITE'),(x,y,0.62),(x,y,0.68),0.078,0.078,18,0.0,False,0.0)
def extinguisher(K,x,y,face):
    """CO2 / powder extinguisher on a wall bracket; face = direction away from the wall"""
    g='ext'; n=S.nrm(face)
    c=Vector((x,y,0.0))
    K.lathe((g,'RED'),x,y,[(0.0,0.30),(0.06,0.30),(0.075,0.33),(0.077,0.40),(0.077,0.62),(0.072,0.70),(0.04,0.74),(0.0,0.745)],seg=20)
    K.cyl((g,'BRASS'),x,y,0.74,0.80,0.022,10,0.0); K.prism((g,'BLACK'),(x,y,0.78),(x+n.x*0.07,y+n.y*0.07,0.78),0.012,0.012,6,0.0,True,0.0)
    K.prism((g,'BLACK'),(x,y,0.80),(x+n.x*0.05,y+n.y*0.05,0.84),0.010,0.010,6,0.0,True,0.0)
    K.tube((g,'BLACK'),[(x+0.02,y+0.02,0.76),(x+n.x*0.10+0.03,y+n.y*0.10+0.03,0.60),(x+n.x*0.10+0.04,y+n.y*0.10+0.04,0.46),(x+n.x*0.04,y+n.y*0.04,0.40)],0.008,6)
    for z in (0.46,0.62): K.prism((g,'STEEL'),(x,y,z),(x,y,z+0.03),0.081,0.081,20,0.0,True,0.0)
    K.box((g,'STEEL'),x-n.x*0.095,y-n.y*0.095,0.40,0.70,0.02 if face in('+x','-x') else 0.10,0.10 if face in('+x','-x') else 0.02,0.0,0.003)
def ladder(K,x,y):
    """aluminium straight ladder leaning on the east wall"""
    g='ladd'; z1=2.55; lean=0.22
    for s in (-1,1):
        K.prism((g,'GALV'),(x,y+s*0.20,0.0),(x+lean,y+s*0.20,z1),0.017,0.017,8,0.0,True,0.0)
        K.bx((g,'RUBBER'),x-0.03,x+0.03,y+s*0.20-0.02,y+s*0.20+0.02,0.0,0.03,0.002)
    for k in range(9):
        t=0.08+k*0.105; z=t*z1; K.prism((g,'GALV'),(x+lean*t,y-0.20,z),(x+lean*t,y+0.20,z),0.012,0.012,8,0.0,True,0.0)
