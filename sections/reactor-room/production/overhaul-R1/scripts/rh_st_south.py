"""STATIONS pass, south wall and centre: coolant pump set P-10 with starter, manifold with isolation valves, emergency-cooling accumulators EC-1 / EC-2 with header and control pedestal, sampling kiosk, tool cabinets.
World coordinates, south wall inner face y = -10.8.  The isolation valves are built into their own 'Manifold valve ...' objects so the checked pipe run may pass through them (clearance.py convention)."""
import math
from mathutils import Vector
import rh_stlib as S
def plinth(K,g,x0,x1,y0,y1,h=0.06): K.bx((g,'CONC_DARK'),x0,x1,y0,y1,0.0,h,0.012)
def pump(K):
    g='pump'; Y=-9.5; Z=0.55
    plinth(K,g,-4.74,-2.22,-10.08,-8.92,0.06)
    K.bx((g,'STEEL'),-4.66,-2.30,-9.97,-9.03,0.06,0.16,0.006)
    K.bx((g,'STEEL'),-4.66,-2.30,-9.97,-9.93,0.16,0.20,0.003); K.bx((g,'STEEL'),-4.66,-2.30,-9.07,-9.03,0.16,0.20,0.003)        # drip lip
    for (x,y) in ((-4.58,-9.90),(-2.38,-9.90),(-4.58,-9.10),(-2.38,-9.10)): S.anchor(K,g,x,y,0.16,0.014,0.04)
    # motor: finned frame, drive-end bell, fan cowl with grille, terminal box, feet
    K.prism((g,'ORANGE'),(-4.60,Y,Z),(-3.72,Y,Z),0.30,0.30,32,0.0,True,0.004)
    for k in range(9): xx=-4.55+k*0.095; K.prism((g,'ORANGE'),(xx,Y,Z),(xx+0.035,Y,Z),0.318,0.318,32,0.0,True,0.003)
    K.prism((g,'STEEL'),(-3.72,Y,Z),(-3.55,Y,Z),0.26,0.22,28,0.0,True,0.003)
    K.prism((g,'AUDI_SATIN'),(-4.60,Y,Z),(-4.80,Y,Z),0.29,0.24,28,0.0,True,0.003)
    for k in range(12):
        th=2*math.pi*k/12; K.tube((g,'BLACK'),[(-4.805,Y+0.03*math.cos(th),Z+0.03*math.sin(th)),(-4.805,Y+0.21*math.cos(th),Z+0.21*math.sin(th))],0.006,6)
    K.bx((g,'AUDI_SATIN'),-4.30,-4.06,Y-0.11,Y+0.11,Z+0.28,Z+0.46,0.01); S.screws(K,g,'+x',-4.06,Y-0.1,Y+0.1,Z+0.30,Z+0.44,0.0,0.005)
    K.cyl((g,'BRASS'),-4.18,Y,Z+0.46,Z+0.52,0.024,10,0.0); K.cyl((g,'BLACK'),-4.18,Y,Z+0.52,Z+0.58,0.015,10,0.0)
    for xx in (-4.42,-3.92): K.bx((g,'STEEL'),xx-0.07,xx+0.07,Y-0.30,Y+0.30,0.16,0.27,0.004)
    # coupling guard (yellow safety guard, slotted), pump casing with front cover and bolts, nozzles
    K.prism((g,'YELLOW'),(-3.55,Y,Z),(-3.40,Y,Z),0.21,0.21,24,0.0,False,0.0)
    K.prism((g,'IRON'),(-3.40,Y,Z),(-2.72,Y,Z),0.35,0.35,32,0.0,True,0.006)
    K.prism((g,'IRON'),(-3.30,Y,Z),(-3.0,Y,Z),0.375,0.375,32,0.0,True,0.004)
    S.bolts(K,g,'STEEL',(-2.72,Y,Z),(1,0,0),0.31,12,0.014,0.02,0.0); K.prism((g,'IRON'),(-2.72,Y,Z),(-2.69,Y,Z),0.33,0.30,28,0.0,True,0.002)
    K.prism((g,'IRON'),(-2.70,Y,Z),(-2.36,Y,Z),0.095,0.095,18,0.0,True,0.003)
    S.flange(K,g,(-2.36,Y,Z),(1,0,0),0.09,0.17,0.03,8,0.012,'IRON','STEEL',0.0)
    K.prism((g,'IRON'),(-2.75,Y,0.70),(-2.75,Y,1.17),0.068,0.068,16,0.0,True,0.003)
    S.flange(K,g,(-2.75,Y,1.18),(0,0,1),0.068,0.145,0.03,8,0.012,'IRON','STEEL',0.0)
    for xx in (-3.28,-2.90): K.bx((g,'IRON'),xx-0.10,xx+0.10,Y-0.30,Y+0.30,0.16,0.25,0.005)
    S.eyebolt(K,g,(-3.15,Y,0.90),(0,1,0),0.045,0.012,'YELLOW')
    S.nameplate(K,g,'+y',-9.03,-3.55,0.115,0.30,0.06)
    # gauge on a stand in front of the base, with capillary to the casing
    K.bx((g,'STEEL'),-3.875,-3.825,-9.00,-8.95,0.16,0.80,0.003); K.bx((g,'AUDI'),-4.02,-3.68,-8.99,-8.95,0.80,1.22,0.008)
    S.gauge(K,g,(-3.85,-8.95,1.02),(0,1,0),0.125,-25)
    # starter cabinet with kept START / STOP pushbuttons
    K.bx((g,'STEEL'),-3.22,-2.72,-8.60,-8.22,0.0,0.10,0.004); K.bx((g,'AUDI_SATIN'),-3.24,-2.70,-8.62,-8.20,0.10,1.55,0.012); K.bx((g,'STEEL'),-3.26,-2.68,-8.64,-8.19,1.55,1.62,0.005)
    K.bx((g,'AUDI'),-3.20,-2.74,-8.205,-8.19,0.94,1.38,0.004)
    S.door(K,g,'+y',-8.20,-3.20,-2.74,0.18,0.90,'l0','AUDI','T',hz=0.55); S.warn_tri(K,g,'+y',-8.19,-3.0,0.34,0.12,'YELLOW')
    K.prism((g,'BRASS'),(-2.70,-8.30,0.85),(-2.66,-8.30,0.85),0.026,0.026,10,0.0,True,0.0)
def manifold(K,Kv):
    g='mani'
    K.bx((g,'STEEL'),-1.71,0.61,-10.62,-8.92,0.0,0.04,0.004)
    K.bx((g,'STEEL'),-1.71,0.61,-10.62,-10.59,0.04,0.10,0.003); K.bx((g,'STEEL'),-1.71,0.61,-8.95,-8.92,0.04,0.10,0.003); K.bx((g,'STEEL'),-1.71,-1.68,-10.62,-8.92,0.04,0.10,0.003); K.bx((g,'STEEL'),0.58,0.61,-10.62,-8.92,0.04,0.10,0.003)
    for zc in (0.67,1.49):
        S.lagged(K,g,[(-1.58,-9.92,zc),(0.48,-9.92,zc)],0.15,0.40)
        for x,sg in ((0.48,1),(-1.58,-1)): S.flange(K,g,(x,-9.92,zc),(sg,0,0),0.15,0.22,0.04,12,0.013,'IRON','STEEL',0.0); K.prism((g,'STEEL'),(x+sg*0.04,-9.92,zc),(x+sg*0.056,-9.92,zc),0.19,0.19,24,0.0,True,0.002)
    for x in (0.31,-1.41):
        K.bx((g,'STEEL'),x-0.06,x+0.06,-10.03,-9.91,0.04,2.02,0.004); K.bx((g,'STEEL'),x-0.12,x+0.12,-10.09,-9.85,0.04,0.06,0.003)
        for zc in (0.67,1.49): K.prism((g,'STEEL'),(x-0.016,-9.92,zc),(x+0.016,-9.92,zc),0.172,0.172,24,0.0,True,0.0)
        K.bx((g,'STEEL'),x-0.05,x+0.05,-9.91,-9.86,1.90,2.02,0.003)
        S.anchor(K,g,x,-10.03,0.04,0.014,0.05)
    # isolation valves on the checked suction line (y -9.49, z 1.1): cast body, flanges, bonnet, yoke, packing; wheels and stems are the kept parts
    for x0 in (0.10,-1.20):
        y=-9.49; z=1.10
        Kv.prism(('valve cast body','IRON'),(x0-0.13,y,z),(x0+0.13,y,z),0.086,0.086,20,0.0,True,0.004)
        for sg in (-1,1): S.flange(Kv,'valve cast body',(x0+sg*0.12,y,z),(sg,0,0),0.07,0.125,0.03,6,0.011,'IRON','STEEL',0.0)
        Kv.prism(('valve cast body','IRON'),(x0,y,z),(x0,y+0.14,z),0.062,0.054,16,0.0,True,0.003)
        Kv.prism(('valve cast body','BRASS'),(x0,y+0.12,z),(x0,y+0.17,z),0.046,0.046,12,0.0,True,0.001)
        for s in (-1,1): Kv.prism(('valve cast body','STEEL'),(x0+s*0.052,y+0.14,z),(x0+s*0.052,y+0.24,z),0.008,0.008,6,0.0,True,0.0)
        Kv.bx(('valve cast body','STEEL'),x0-0.07,x0+0.07,y+0.235,y+0.255,z-0.02,z+0.02,0.003)
        Kv.bx(('valve cast body','BRASS'),x0-0.045,x0+0.045,y-0.075,y-0.06,z+0.095,z+0.135,0.002)
def ec(K):
    g='ec'
    for k,xc in enumerate((3.30,1.80)):
        yc=-9.65; R=0.46
        K.bx((g,'CONC_DARK'),xc-0.55,xc+0.55,yc-0.55,yc+0.55,0.0,0.05,0.012)
        for dx in (-0.30,0.30):
            for dy in (-0.30,0.30):
                K.bx((g,'STEEL'),xc+dx-0.035,xc+dx+0.035,yc+dy-0.035,yc+dy+0.035,0.05,0.62,0.004); S.anchor(K,g,xc+dx,yc+dy,0.05,0.014,0.045)
        for dx in (-0.30,0.30): K.bx((g,'STEEL'),xc+dx-0.04,xc+dx+0.04,yc-0.34,yc+0.34,0.40,0.46,0.003); K.bx((g,'STEEL'),xc-0.34,xc+0.34,yc+dx-0.04,yc+dx+0.04,0.46,0.52,0.003)
        K.lathe((g,'AUDI_SATIN'),xc,yc,[(0.0,0.60),(0.22,0.60),(0.34,0.63),(0.42,0.69),(0.455,0.78),(0.46,0.92),(0.46,2.22),(0.455,2.32),(0.42,2.42),(0.34,2.50),(0.22,2.55),(0.10,2.57),(0.0,2.57)],seg=40)
        for z in (0.95,1.75,2.20): K.prism((g,'STEEL'),(xc,yc,z),(xc,yc,z+0.05),0.468,0.468,40,0.0,True,0.003)
        K.prism((g,'YELLOW'),(xc,yc,1.30),(xc,yc,1.40),0.464,0.464,40,0.0,False,0.0)
        # top: charge nozzle with flange at the port, lifting lugs, manhole cover with bolts
        K.cyl((g,'IRON'),xc,yc,2.55,2.67,0.062,14,0.0); S.flange(K,g,(xc,yc,2.68),(0,0,1),0.062,0.14,0.03,8,0.011,'IRON','STEEL',0.0)
        for s in (-1,1): K.bx((g,'STEEL'),xc+s*0.30-0.05,xc+s*0.30+0.05,yc-0.10,yc+0.02,2.38,2.44,0.003)
        # side nozzle to the wall (port at the flange face), level glass, gauge, label
        K.prism((g,'IRON'),(xc,yc-R+0.01,1.05),(xc,-10.50,1.05),0.065,0.065,16,0.0,True,0.003)
        S.flange(K,g,(xc,-10.50,1.05),(0,-1,0),0.065,0.15,0.02,8,0.012,'IRON','STEEL',0.0)
        gx=xc+0.30
        K.prism((g,'GLASS'),(gx,yc+R+0.045,1.0),(gx,yc+R+0.045,2.15),0.014,0.014,10,0.0,True,0.0)
        for z in (1.0,2.15): K.prism((g,'BRASS'),(gx,yc+R-0.01,z),(gx,yc+R+0.07,z),0.016,0.016,10,0.0,True,0.0); K.prism((g,'BRASS'),(gx,yc+R+0.04,z-0.03),(gx,yc+R+0.05,z+0.03),0.026,0.026,10,0.0,True,0.0)
        S.gauge(K,g,(xc-0.02,yc+R+0.03,1.49),(0,1,0),0.075,-20)
        K.prism((g,'STEEL'),(xc-0.02,yc+R-0.01,1.49),(xc-0.02,yc+R+0.03,1.49),0.018,0.018,10,0.0,True,0.0)
        K.bx((g,'BLACK'),xc-0.18,xc+0.10,yc+R-0.005,yc+R+0.012,0.93,1.06,0.002)
        # header stub from the tank foot to the cross header
        K.prism((g,'IRON'),(xc,yc+R-0.01,0.78),(xc,-8.84,0.78),0.075,0.075,16,0.0,True,0.003)
    # cross header along x between the two tanks: blind flanges at both ends, two pipe stands
    S.lagged(K,g,[(1.62,-8.84,0.78),(3.48,-8.84,0.78)],0.10,0.38)
    for x,sg in ((3.48,1),(1.62,-1)):
        S.flange(K,g,(x,-8.84,0.78),(sg,0,0),0.10,0.19,0.04,10,0.012,'IRON','STEEL',0.0); K.prism((g,'IRON'),(x+sg*0.04,-8.84,0.78),(x+sg*0.06,-8.84,0.78),0.15,0.15,24,0.0,True,0.002)
    for x in (2.20,2.90): K.bx((g,'STEEL'),x-0.025,x+0.025,-8.865,-8.815,0.05,0.69,0.003); K.bx((g,'STEEL'),x-0.09,x+0.09,-8.93,-8.75,0.05,0.07,0.003); K.prism((g,'STEEL'),(x-0.014,-8.84,0.78),(x+0.014,-8.84,0.78),0.115,0.115,18,0.0,True,0.0)
    # emergency-cooling control pedestal with hood over the kept mushroom button
    K.bx((g,'STEEL'),2.30,2.80,-8.70,-8.46,0.0,0.10,0.004); K.bx((g,'AUDI_SATIN'),2.28,2.82,-8.72,-8.44,0.10,1.30,0.012)
    K.bx((g,'AUDI'),2.34,2.76,-8.445,-8.43,0.92,1.26,0.003); K.bx((g,'RED'),2.40,2.70,-8.436,-8.428,1.226,1.25,0.0015)
    K.bx((g,'STEEL'),2.26,2.84,-8.74,-8.40,1.30,1.35,0.006); K.bx((g,'HAZARD'),2.26,2.84,-8.405,-8.395,1.30,1.35,0.0015)
    K.bx((g,'STEEL'),2.40,2.70,-8.44,-8.34,1.25,1.28,0.003)
    S.warn_tri(K,g,'+y',-8.44,2.40,0.50,0.12,'YELLOW'); S.label_bar(K,g,'+y',-8.44,2.50,2.76,0.46,0.49,'RED')
def sampler(K):
    g='samp'
    K.bx((g,'STEEL'),1.12,2.08,-3.75,-3.10,0.0,0.06,0.005)
    K.bx((g,'AUDI_SATIN'),1.15,2.05,-3.72,-3.10,0.06,0.50,0.012)
    K.bx((g,'AUDI_SATIN'),1.15,2.05,-3.60,-3.10,0.50,1.57,0.012)
    for (a,b) in ((1.15,1.52),(1.96,2.05)): K.bx((g,'AUDI_SATIN'),a,b,-3.74,-3.60,0.50,0.95,0.01)
    K.bx((g,'AUDI_SATIN'),1.15,2.05,-3.74,-3.60,0.95,1.57,0.012)
    K.bx((g,'GALV'),1.20,2.00,-3.99,-3.72,0.50,0.54,0.004); K.bx((g,'STEEL'),1.20,2.00,-3.99,-3.97,0.54,0.58,0.002); K.bx((g,'STEEL'),1.20,1.22,-3.99,-3.72,0.54,0.58,0.002); K.bx((g,'STEEL'),1.98,2.00,-3.99,-3.72,0.54,0.58,0.002)
    for x in (1.26,1.94): K.bx((g,'STEEL'),x-0.03,x+0.03,-3.98,-3.92,0.06,0.50,0.003)
    S.door(K,g,'-y',-3.72,1.19,1.50,0.12,0.46,'l0','AUDI','T',hz=0.30); S.door(K,g,'-y',-3.72,1.55,2.01,0.12,0.46,'l1','AUDI','T',hz=0.30)
    S.gauge(K,g,(1.60,-3.74,1.14),(0,-1,0),0.085,-30)
    S.louvres(K,g,'STEEL','-y',-3.74,1.16,2.04,1.38,1.52,3,0.014,False)
    K.prism((g,'STEEL'),(1.72,-3.34,1.57),(1.72,-3.34,1.90),0.032,0.032,10,0.0,True,0.0)
    K.bx((g,'AUDI'),1.14,2.06,-3.74,-3.09,1.57,1.62,0.006)
def south_cabinets(K):
    g='tcab'
    for (x0,x1,cols) in ((-5.55,-4.72,1),(4.30,5.40,2)):
        K.bx((g,'STEEL'),x0+0.03,x1-0.03,-10.58,-10.04,0.05,0.14,0.004)
        K.bx((g,'AUDI_SATIN'),x0,x1,-10.62,-10.0,0.14,1.10,0.012)
        K.bx((g,'GALV'),x0-0.012,x1+0.012,-10.64,-9.985,1.10,1.15,0.006)
        for xw in (x0+0.10,x1-0.10):
            K.cyl((g,'BLACK'),xw,-10.52,0.0,0.05,0.04,12,0.0); K.cyl((g,'BLACK'),xw,-10.10,0.0,0.05,0.04,12,0.0)
        w=(x1-x0-0.08)/cols
        for c in range(cols):
            a=x0+0.04+c*w; b=a+w-0.01
            for (z0,z1) in ((0.20,0.46),(0.48,0.74),(0.76,1.06)):
                K.fb((g,'AUDI'),'+y',-10.0,a,b,z0,z1,0.016,0.003); S.handle_bar(K,g,'+y',-9.984,(a+b)/2,(z0+z1)/2+0.06,(b-a)*0.5,0.0,'STEEL',False); S.screws(K,g,'+y',-9.984,a,b,z0,z1,0.0,0.005)
        S.label_bar(K,g,'+y',-9.99,x0+0.04,x1-0.04,1.07,1.09,'ORANGE')
