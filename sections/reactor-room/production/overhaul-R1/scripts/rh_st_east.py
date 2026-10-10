"""STATIONS pass, east / north-east: grid switchgear, desk consoles (grid demand and bank control), turbine set, vent damper, waste cask.  World coordinates, east wall inner face x = 10.8."""
import math
from mathutils import Vector
import rh_stlib as S
def plinth(K,g,x0,x1,y0,y1,h=0.06): K.bx((g,'CONC_DARK'),x0,x1,y0,y1,0.0,h,0.012)
def console(K,g,cx,cy,yaw,W,D,F,top,hood_f,hood_h,tog_f,tog_l,gl=None,lamps_l=()):
    """desk console in a local frame (x out of the wall towards the hall, y lateral, back face at x = 0): kick plate, two-door lower body, side cheeks with yellow edge line, rolled desk top with rubber
    mat, toggle bank with guard bar, instrument upright with vented hood, status lamps and a cable gland on the hood"""
    K.begin(cx,cy,yaw); h=W/2
    K.bx((g,'STEEL'),0.04,D-0.04,-h+0.04,h-0.04,0.0,0.10,0.004)
    K.bx((g,'AUDI_SATIN'),0.0,D,-h+0.03,h-0.03,0.10,0.93,0.012)
    for s in (-1,1):
        a,b=(h-0.03,h) if s>0 else (-h,-h+0.03)
        K.bx((g,'AUDI'),0.0,D+0.015,a,b,0.10,0.975,0.006); K.bx((g,'YELLOW'),D+0.004,D+0.018,a,b,0.12,0.93,0.002)
    S.door(K,g,'+x',D,-h+0.05,-0.006,0.14,0.90,'l0','AUDI_SATIN','T',hz=0.52); S.door(K,g,'+x',D,0.006,h-0.05,0.14,0.90,'l1','AUDI_SATIN','T',hz=0.52)
    for sg in (-1,1): S.louvres(K,g,'STEEL','+x',D+0.005,sg*0.07 if sg>0 else -h+0.10,(h-0.10 if sg>0 else -0.07),0.70,0.86,4,0.018,False)
    K.pillow((g,'AUDI'),-0.0,D+0.045,-h-0.02,h+0.02,0.93,0.975,0.012,1)
    K.bx((g,'BLACK'),0.20,D-0.10,-h+0.12,h-0.12,0.975,0.981,0.002)
    lo,hi=min(tog_l)-0.14,max(tog_l)+0.14
    K.bx((g,'AUDI'),tog_f-0.08,tog_f+0.08,lo+0.04,hi-0.04,0.975,0.99,0.004)
    for yy in (lo,hi): K.prism((g,'STEEL'),(tog_f+0.12,yy,0.975),(tog_f+0.12,yy,1.12),0.011,0.011,8,0.0,True,0.0)
    K.prism((g,'STEEL'),(tog_f+0.12,lo,1.12),(tog_f+0.12,hi,1.12),0.009,0.009,8,0.0,True,0.0)
    K.bx((g,'AUDI_SATIN'),0.0,F,-h+0.03,h-0.03,0.975,top,0.012)
    K.bx((g,'STEEL'),F,F+0.006,-h+0.07,h-0.07,1.10,top-hood_h-0.02,0.002)
    for yy in (-h+0.07,h-0.07): K.bx((g,'STEEL'),F,F+0.02,yy-0.008,yy+0.008,1.10,top-hood_h-0.02,0.002)
    K.bx((g,'STEEL'),F,F+0.02,-h+0.07,h-0.07,1.10,1.115,0.002)
    K.bx((g,'AUDI'),0.0,hood_f,-h+0.025,h-0.025,top-hood_h,top,0.01)
    K.bx((g,'STEEL'),-0.0,hood_f+0.012,-h+0.02,h-0.02,top-0.012,top,0.003)
    S.louvres(K,g,'STEEL','+x',hood_f,-h+0.12,h-0.12,top-hood_h+0.04,top-0.04,2 if hood_h<0.2 else 4,0.014,False)
    for k,l in enumerate(lamps_l): S.lamp(K,g,(F+0.002,l,top-hood_h-0.07),(1,0,0),0.013,('LAMP_G','LAMP_G','LAMP_A','LAMP_R')[k%4])
    K.bx((g,'BRASS'),F+0.002,F+0.006,-h+0.10,-h+0.28,1.03,1.07,0.001)
    if gl: K.cyl((g,'BRASS'),gl[0],gl[1],top,top+0.025,0.026,10,0.0)
    K.end()
def switchgear(K):
    g='grid'
    cols=[(-2.23,-1.57),(-1.55,-0.89),(-0.87,-0.21)]; pivy=[-1.88,-1.20,-0.52]; ST=['LAMP_G','LAMP_G','LAMP_A']
    plinth(K,g,9.40,10.70,-2.30,-0.14,0.04)
    K.bx((g,'STEEL'),9.44,10.66,-2.27,-0.17,0.04,0.12,0.004)
    K.bx((g,'HAZARD'),9.34,9.40,-2.30,-0.14,0.0,0.012,0.002)
    for (a,b),py in zip(cols,pivy):
        K.bx((g,'AUDI_SATIN'),9.48,10.66,a,b,0.12,2.22,0.012)
        K.bx((g,'STEEL'),9.47,9.485,a-0.005,a+0.015,0.12,2.22,0.002); K.bx((g,'STEEL'),9.47,9.485,b-0.015,b+0.005,0.12,2.22,0.002)
        for k,(z0,z1) in enumerate(((0.22,0.66),(0.67,1.11),(1.12,1.56))):
            S.door(K,g,'-x',9.48,a+0.04,b-0.04,z0,z1,'l0','AUDI','none',proud=0.008)
            S.lamp(K,g,(9.46,py+0.19,z0+0.29),(-1,0,0),0.015,ST[k] if (py+k)%2==0 else 'LAMP_G')
            S.label_bar(K,g,'-x',9.469,py-0.26,py-0.06,z0+0.04,z0+0.062,'WHITE')
        S.louvres(K,g,'STEEL','-x',9.48,a+0.06,b-0.06,1.62,1.92,6,0.022)
        S.label_bar(K,g,'-x',9.469,a+0.05,b-0.05,1.585,1.605,'RED'); S.label_bar(K,g,'-x',9.469,a+0.05,b-0.05,2.165,2.185,'RED')
        S.warn_tri(K,g,'-x',9.467,b-0.10,2.065,0.10,'YELLOW')
        S.eyebolt(K,g,(10.2,(a+b)/2,2.25),(1,0,0),0.04,0.010,'YELLOW')
    K.bx((g,'STEEL'),9.42,10.68,-2.27,-0.17,2.22,2.27,0.006)
    K.cyl((g,'BRASS'),9.8,-0.7,2.27,2.34,0.028,10,0.0); K.cyl((g,'BLACK'),9.8,-0.7,2.34,2.42,0.017,10,0.0)
    # protective earth stud on the end cabinet
    K.cyl((g,'BRASS'),9.50,-2.265,0.2,0.3,0.011,8,0.0)
def turbine(K):
    g='turb'; X=9.95; Z=1.22
    plinth(K,g,8.80,10.72,-5.90,-2.35,0.14)
    # fabricated base frame with ribs and anchor plates
    for x in (8.97,10.54):
        K.bx((g,'STEEL'),x-.10,x+.10,-5.82,-2.42,.14,.18,.003)
        K.bx((g,'STEEL'),x-.025,x+.025,-5.82,-2.42,.18,.37,.002)
        K.bx((g,'STEEL'),x-.10,x+.10,-5.82,-2.42,.37,.42,.003)
    for y in (-5.70,-4.65,-3.60,-2.54):
        K.bx((g,'STEEL'),8.97,10.54,y-.055,y+.055,.18,.37,.003)
    K.bx((g,'STEEL'),8.85,10.66,-5.82,-2.42,.42,.455,.003)
    for y in (-5.7,-5.0,-4.3,-3.6,-2.9): K.bx((g,'STEEL'),8.84,8.87,y-0.015,y+0.015,0.14,0.42,0.002)
    K.bx((g,'HAZARD'),8.80,8.845,-5.84,-2.40,0.14,0.172,0.002)
    for (x,y) in ((8.95,-5.74),(10.55,-5.74),(8.95,-2.50),(10.55,-2.50),(8.95,-4.1),(10.55,-4.1)): S.anchor(K,g,x,y,0.14,0.016,0.05)
    for y in (-5.76,-2.48): S.eyebolt(K,g,(8.95,y,0.42),(0,1,0),0.05,0.012,'YELLOW'); S.eyebolt(K,g,(10.55,y,0.42),(0,1,0),0.05,0.012,'YELLOW')
    # front bearing pedestal, shaft neck, casing: lagged HP section, flanged IP section, exhaust hood, generator
    K.bx((g,'STEEL'),X-.43,X+.43,-5.82,-5.64,.455,.50,.003)
    for xx in (X-.36,X+.36): S.anchor(K,g,xx,-5.73,.50,.012,.025)
    K.bx((g,'IRON'),X-0.40,X+0.40,-5.85,-5.66,0.50,1.66,0.015); K.bx((g,'STEEL'),X-0.40,X+0.40,-5.87,-5.85,0.62,1.60,0.003)
    S.gauge(K,g,(X-0.18,-5.865,1.40),(0,-1,0),0.07,-40); S.gauge(K,g,(X+0.18,-5.865,1.40),(0,-1,0),0.07,10)
    K.prism((g,'BRASS'),(X,-5.865,0.95),(X,-5.88,0.95),0.045,0.045,16,0.0,True,0.0); K.prism((g,'GLASS'),(X,-5.88,0.95),(X,-5.882,0.95),0.04,0.04,16,0.0,True,0.0)
    K.prism((g,'STEEL'),(X,-5.66,Z),(X,-5.50,Z),0.14,0.14,16,0.0,True,0.0)
    K.prism((g,'STEEL'),(X,-5.66,Z),(X,-5.52,Z),0.20,0.20,20,0.0,False,0.0)
    K.prism((g,'IRON'),(X,-5.50,Z),(X,-5.40,Z),0.50,0.52,32,0.0,True,0.004)
    for ya,yb,ra,rb in ((-5.40,-5.24,.49,.545),(-5.24,-4.42,.545,.545),(-4.42,-4.20,.545,.49)):
        K.prism((g,'GALV'),(X,ya,Z),(X,yb,Z),ra,rb,40,0,True,.003)
    for y in (-5.30,-5.02,-4.74,-4.46,-4.28): K.prism((g,'STEEL'),(X,y-0.012,Z),(X,y+0.012,Z),0.552,0.552,32,0.0,True,0.0)
    K.bx((g,'GALV'),X-0.60,X+0.60,-5.38,-4.22,Z-0.02,Z+0.04,0.004)                                 # insulation seam / split line cover
    K.prism((g,'IRON'),(X,-4.20,Z),(X,-3.62,Z),0.50,0.50,32,0.0,True,0.004)
    for y in (-4.20,-3.64): K.prism((g,'IRON'),(X,y-0.025,Z),(X,y+0.025,Z),0.64,0.64,36,0.0,True,0.004); S.bolts(K,g,'STEEL',(X,y+0.0,Z),(0,1,0),0.58,20,0.014,0.03,0.025)
    # horizontal split-line flange with bolts both sides
    K.bx((g,'IRON'),X-0.66,X+0.66,-4.20,-3.62,Z-0.03,Z+0.03,0.004)
    for y in [-4.14+0.075*i for i in range(8)]:
        for s in (-1,1): K.prism((g,'STEEL'),(X+s*0.62,y,Z+0.03),(X+s*0.62,y,Z+0.075),0.016,0.016,6,0.0,True,0.0)
    # exhaust hood (cast box) with bolted side cover and the flanged outlet at the port
    K.hull((g,'IRON'),[(X-.55,-3.62,.52),(X+.50,-3.62,.52),(X-.45,-3.02,.52),(X+.50,-3.02,.52),(X-.55,-3.62,1.62),(X+.50,-3.62,1.62),(X-.35,-3.02,1.47),(X+.50,-3.02,1.47)],.015)
    K.bx((g,'STEEL'),X-0.57,X-0.545,-3.56,-3.08,0.60,1.55,0.003)
    for yy in (-3.52,-3.34,-3.16):
        for zz in (0.66,1.10,1.50): K.prism((g,'STEEL'),(X-0.57,yy,zz),(X-0.585,yy,zz),0.014,0.014,6,0.0,True,0.0)
    S.eyebolt(K,g,(X-0.2,-3.32,1.62),(1,0,0),0.05,0.012,'YELLOW')
    K.prism((g,'IRON'),(X+0.5,-3.3,1.15),(X+0.6,-3.3,1.15),0.17,0.17,24,0.0,True,0.0)
    S.flange(K,g,(10.545,-3.3,1.15),(1,0,0),0.10,0.19,0.04,8,0.013,'IRON','STEEL',0.0)
    # steam chest on the HP end: casting with cover flange, inlet flange at the port, servo actuator
    S.lathe(K,(g,'IRON'),9.6,-3.8,[(0.0,1.40),(0.24,1.40),(0.26,1.46),(0.22,1.62),(0.22,2.24),(0.26,2.27),(0.26,2.31),(0.0,2.31)],seg=28)
    S.bolts(K,g,'STEEL',(9.6,-3.8,2.31),(0,0,1),0.22,10,0.013,0.02,0.0)
    S.flange(K,g,(9.6,-3.8,2.30),(0,0,1),0.10,0.20,0.04,8,0.013,'IRON','STEEL',0.0)
    K.cyl((g,'IRON'),9.6,-3.8,1.46,1.62,0.30,24,0.003); S.bolts(K,g,'STEEL',(9.6,-3.8,1.62),(0,0,1),0.27,12,0.012,0.015,0.0)
    # throttle valve: flanged globe body, bonnet, yoke, packing; the wheel and spindle are the kept interactive parts
    K.prism((g,'IRON'),(9.38,-2.82,1.25),(9.38,-2.32,1.25),0.11,0.11,20,0.0,True,0.004)
    for y in (-2.80,-2.34): S.flange(K,g,(9.38,y,1.25),(0,-1 if y<-2.57 else 1,0),0.08,0.15,0.03,8,0.011,'IRON','STEEL',0.0)
    K.prism((g,'IRON'),(9.38,-2.57,1.25),(9.38,-2.57,1.62),0.075,0.06,16,0.0,True,0.003)
    K.prism((g,'IRON'),(9.38,-2.57,1.25),(9.18,-2.57,1.25),0.085,0.085,16,0.0,True,0.003)
    K.prism((g,'BRASS'),(9.18,-2.57,1.25),(9.14,-2.57,1.25),0.05,0.05,12,0.0,True,0.0)
    for s in (-1,1): K.prism((g,'STEEL'),(9.20,-2.57+s*0.06,1.25+0.0),(9.04,-2.57+s*0.10,1.25),0.014,0.014,8,0.0,True,0.0)
    K.bx((g,'STEEL'),9.02,9.06,-2.70,-2.44,1.17,1.33,0.004)
    K.bx((g,'STEEL'),9.00,9.06,-2.47,-2.40,0.42,1.50,0.003); K.bx((g,'STEEL'),9.00,9.06,-2.76,-2.69,0.42,1.50,0.003)    # gauge panel posts
    K.bx((g,'AUDI'),8.98,9.04,-2.78,-2.42,1.48,1.84,0.008)
    S.gauge(K,g,(8.975,-2.60,1.66),(-1,0,0),0.095,-20)
    S.lagged(K,g,[(9.38,-2.57,1.58),(9.38,-2.57,1.95),(9.38,-3.80,1.95),(9.60,-3.80,1.95)],0.05,0.35)
    # lube-oil console with the identification plate (re-placed on its face)
    K.bx((g,'AUDI_SATIN'),8.88,9.22,-4.50,-3.20,0.42,1.18,0.012); K.bx((g,'STEEL'),8.86,9.24,-4.52,-3.18,1.18,1.21,0.004)
    S.door(K,g,'-x',8.88,-4.46,-3.88,0.50,1.12,'l0','AUDI','T',hz=0.80); S.door(K,g,'-x',8.88,-3.82,-3.24,0.50,1.12,'l1','AUDI','T',hz=0.80)
    S.warn_tri(K,g,'-x',8.873,-4.38,0.62,0.10,'YELLOW'); S.louvres(K,g,'STEEL','-x',8.88,-3.74,-3.30,0.52,0.70,3,0.02,False)
    # junction box on a post: the generator-end instrument box with the containment sensor
    K.bx((g,'STEEL'),10.40,10.55,-2.72,-2.46,0.42,2.10,0.004)
    K.bx((g,'AUDI_SATIN'),10.28,10.66,-2.78,-2.40,2.10,2.46,0.012)
    S.gauge(K,g,(10.27,-2.58,2.28),(-1,0,0),0.065,25)
    K.cyl((g,'BRASS'),10.4,-2.58,2.46,2.53,0.026,10,0.0); K.cyl((g,'BLACK'),10.4,-2.58,2.53,2.60,0.016,10,0.0)
    # generator end: finned barrel with end bell, terminal box
    K.prism((g,'STEEL'),(X,-3.02,Z),(X,-3.0,Z),0.40,0.40,28,0.0,True,0.0)
    K.prism((g,'AUDI'),(X,-3.0,Z),(X,-2.50,Z),0.36,0.36,32,0.0,True,0.004)
    for k in range(7): yy=-2.98+k*0.07; K.prism((g,'AUDI'),(X,yy,Z),(X,yy+0.03,Z),0.385,0.385,32,0.0,True,0.003)
    K.prism((g,'STEEL'),(X,-2.50,Z),(X,-2.44,Z),0.37,0.28,32,0.0,True,0.003)
    K.bx((g,'AUDI_SATIN'),X-0.12,X+0.12,-2.92,-2.64,Z+0.35,Z+0.52,0.01); S.screws(K,g,'+x',X+0.12,-2.9,-2.66,Z+0.37,Z+0.50,0.0,0.005)
    for xx in (X-0.25,X+0.25): K.bx((g,'STEEL'),xx-0.06,xx+0.06,-2.98,-2.52,0.42,0.86,0.004)
    # supply lines: exhaust drain trap, condensate drain with valve
    S.lagged(K,g,[(X+0.30,-4.0,0.52),(X+0.30,-4.0,0.30)],0.035,0.3)
def vent(K):
    g='vent'; cx,cy=9.63,6.93; R=0.42
    K.bx((g,'CONC_DARK'),8.70,10.00,5.90,7.35,0.0,0.06,0.012)
    # guard cage: four posts with base plates, two rails, yellow top rail
    for (x,y) in ((8.85,6.05),(8.85,7.20),(9.85,6.05),(9.85,7.20)):
        K.bx((g,'STEEL'),x-0.04,x+0.04,y-0.04,y+0.04,0.06,1.92,0.004); K.bx((g,'STEEL'),x-0.075,x+0.075,y-0.075,y+0.075,0.06,0.075,0.003)
        for (dx,dy) in ((-1,-1),(1,-1),(-1,1),(1,1)): K.cyl((g,'STEEL'),x+dx*0.055,y+dy*0.055,0.075,0.10,0.009,6,0.0)
    for z0,m in ((0.88,'YELLOW'),(1.90,'YELLOW'),(1.40,'STEEL')):
        K.bx((g,m),8.82,9.89,6.01,6.09,z0,z0+0.05,0.004); K.bx((g,m),8.82,9.89,7.16,7.24,z0,z0+0.05,0.004); K.bx((g,m),8.81,8.89,6.01,7.24,z0,z0+0.05,0.004); K.bx((g,m),9.81,9.89,6.01,7.24,z0,z0+0.05,0.004)
    # vent stack: base flange, lagged duct with clamp bands, damper housing, flanged joints, top transition and wall bracket
    K.cyl((g,'STEEL'),cx,cy,0.06,0.10,0.50,32,0.003); S.bolts(K,g,'STEEL',(cx,cy,0.10),(0,0,1),0.46,16,0.014,0.025,0.0)
    K.cyl((g,'STEEL'),cx,cy,0.10,1.16,R,32,0.0)
    K.cyl((g,'GALV'),cx,cy,1.88,4.59,R,32,0.0)
    for z in [1.95+0.38*k for k in range(7)]: K.prism((g,'STEEL'),(cx,cy,z),(cx,cy,z+0.03),R*1.03,R*1.03,32,0.0,True,0.0)
    for z in (1.16,1.88,3.20):
        K.prism((g,'IRON'),(cx,cy,z-0.025),(cx,cy,z+0.025),0.50,0.50,36,0.0,True,0.004); S.bolts(K,g,'STEEL',(cx,cy,z+0.025),(0,0,1),0.46,18,0.014,0.025,0.0)
    K.cyl((g,'IRON'),cx,cy,1.16,1.88,0.46,32,0.006)                                              # damper housing
    for k in range(4):
        th=math.pi/4+k*math.pi/2; K.box((g,'STEEL'),cx+0.46*math.cos(th),cy+0.46*math.sin(th),1.22,1.82,0.05,0.05,th,0.002)
    K.cyl((g,'STEEL'),cx,cy,4.59,4.63,R*1.02,32,0.003)
    # gearbox on the south-west side with the extension shaft to the (kept) hand wheel, bearing bracket
    d=Vector((-1,-1,0)).normalized(); gb=Vector((cx,cy,1.52))+d*0.52
    K.box((g,'IRON'),gb.x,gb.y,1.40,1.64,0.20,0.20,math.radians(45),0.012)
    K.box((g,'AUDI'),gb.x+d.x*0.0,gb.y+d.y*0.0,1.64,1.69,0.12,0.12,math.radians(45),0.004)
    p0=Vector((cx,cy,1.52))+d*0.30; p1=Vector((cx,cy,1.52))+d*0.78
    K.prism((g,'STEEL'),p0,p1,0.022,0.022,10,0.0,True,0.0)
    S.flange(K,g,Vector((cx,cy,1.52))+d*0.36,d,0.05,0.10,0.04,6,0.01,'IRON','STEEL',0.0)
    br=Vector((cx,cy,0.0))+d*0.62
    K.bx((g,'STEEL'),br.x-0.03,br.x+0.03,br.y-0.03,br.y+0.03,0.06,1.36,0.003); K.box((g,'IRON'),br.x,br.y,1.36,1.50,0.10,0.07,math.radians(45),0.006)
    # power / limit-switch box on the wall bracket (port PORT_WALL_VENT_POWER at its east face)
    for z in (2.10,2.55): K.bx((g,'STEEL'),10.55,10.80,6.78,6.84,z,z+0.04,0.003); K.bx((g,'STEEL'),10.55,10.80,7.16,7.22,z,z+0.04,0.003)
    K.bx((g,'AUDI_SATIN'),10.15,10.66,6.75,7.25,2.0,2.72,0.015)
    # The stack stands immediately west of the box. Service access and
    # identification face south, leaving the retained east power port intact.
    S.door(K,g,'-y',6.75,10.20,10.61,2.06,2.58,'l0','AUDI','T',hz=2.32)
    S.lamp(K,g,(10.45,6.74,2.65),(0,-1,0),0.014,'LAMP_G'); S.lamp(K,g,(10.35,6.74,2.65),(0,-1,0),0.014,'LAMP_A')
    S.warn_tri(K,g,'-y',6.75,10.28,2.12,0.10,'YELLOW')
    K.cyl((g,'BRASS'),10.36,6.99,2.72,2.79,0.026,10,0.0)
    # warning sign on the cage
    S.warn_tri(K,g,'-y',6.00,9.35,1.20,0.16,'YELLOW')
def waste(K):
    g='waste'; cx,cy=7.52,8.12
    # spill bund, base plate with anchors
    K.bx((g,'CONC_DARK'),6.40,8.66,6.98,9.24,0.0,0.05,0.012)
    S.lathe(K,(g,'STEEL'),cx,cy,[(0.99,0.05),(0.99,0.17),(0.96,0.17),(0.96,0.05),(0.99,0.05)],seg=40)
    K.cyl((g,'STEEL'),cx,cy,0.05,0.26,0.90,40,0.004)
    for k in range(8):
        th=k*math.pi/4+math.pi/8; S.anchor(K,g,cx+0.80*math.cos(th),cy+0.80*math.sin(th),0.26,0.016,0.05)
    # cask shell: foot ring, shell, hazard band, shoulder, bolted lid with shield plug, vent nozzle
    prof=[(0.0,0.26),(0.68,0.26),(0.68,0.33),(0.62,0.35),(0.62,2.02),(0.66,2.05),(0.66,2.20),(0.60,2.22),(0.56,2.28),(0.56,2.62),(0.50,2.66),(0.0,2.67)]
    S.lathe(K,('waste','YELLOW'),cx,cy,prof,seg=44)
    K.prism(('waste','HAZARD'),(cx,cy,1.18),(cx,cy,1.32),0.625,0.625,44,0.0,False,0.0)
    for z in (0.78,1.62): K.prism(('waste','STEEL'),(cx,cy,z),(cx,cy,z+0.05),0.635,0.635,44,0.0,True,0.003)
    S.bolts(K,g,'STEEL',(cx,cy,2.20),(0,0,1),0.61,28,0.014,0.022,0.0)
    # radial cooling fins on the lower shell
    for k in range(36):
        th=2*math.pi*k/36; r=0.625+0.04; K.box(('waste','STEEL'),cx+r*math.cos(th),cy+r*math.sin(th),0.52,1.12 if True else 1.0,0.085,0.026,th,0.003)
        K.box(('waste','STEEL'),cx+r*math.cos(th),cy+r*math.sin(th),1.36,1.86,0.085,0.026,th,0.003)
    # trunnions (lifting), vent nozzle at the port, lifting-eye pads, gauge boss
    for s in (-1,1):
        d=Vector((0.7071,-0.7071,0)); c0=Vector((cx,cy,1.84))+d*s*0.60; c1=Vector((cx,cy,1.84))+d*s*0.82
        K.prism(('waste','IRON'),c0,c1,0.07,0.07,16,0.0,True,0.004); K.prism(('waste','YELLOW'),c1,c1+d*s*0.03,0.09,0.09,16,0.0,True,0.003)
    K.cyl(('waste','STEEL'),7.6,8.2,2.62-0.14,2.60,0.062,14,0.0)
    S.flange(K,g,(7.6,8.2,2.60),(0,0,1),0.05,0.11,0.026,6,0.009,'IRON','STEEL',0.0)
    for (x,y) in ((7.31,8.59),(7.99,7.91)): K.cyl(('waste','STEEL'),x+0.0,y,2.63,2.67,0.07,12,0.0)
    S.gauge(K,g,(7.045,7.645,1.64),(-0.7071,-0.7071,0),0.08,-15)
    K.prism(('waste','STEEL'),(7.045+0.021,7.645+0.021,1.64),(7.045+0.06,7.645+0.06,1.64),0.03,0.03,12,0.0,True,0.0)
    # transfer control pedestal: post, head with hazard edge, gland, warning
    K.bx((g,'AUDI_SATIN'),6.46,6.80,8.30,8.56,0.05,0.78,0.01); K.bx((g,'STEEL'),6.42,6.84,8.26,8.60,0.78,0.86,0.006); K.bx((g,'HAZARD'),6.42,6.84,8.26,8.28,0.78,0.86,0.002)
    K.bx((g,'AUDI_SATIN'),6.44,6.82,8.28,8.58,0.04,0.07,0.003)
    S.nameplate(K,g,'-x',6.46,8.43,0.55,0.20,0.07)
    # step plate / grating walkway up to the lid hint (a short hazard kerb at the front)
