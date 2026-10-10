"""STATIONS pass, west wall: diesel generator set, reserve power cabinets A / B, repair bench, fuel cart bay.  World coordinates (the west wall inner face is x = -10.8)."""
import math
from mathutils import Vector
import rh_stlib as S
def plinth(K,g,x0,x1,y0,y1,h=0.06): K.bx((g,'CONC_DARK'),x0,x1,y0,y1,0.0,h,0.012)
def generator(K):
    g='gen'
    plinth(K,g,-10.72,-8.78,-4.46,-2.34,0.06)
    # skid: two longitudinal I-beams, cross members, deck plate with hazard front edge, anchor plates at the corners, lifting lugs
    for xc in (-10.50,-9.20): K.bx((g,'STEEL'),xc-0.07,xc+0.07,-4.40,-2.42,0.06,0.26,0.006); K.bx((g,'STEEL'),xc-0.10,xc+0.10,-4.40,-2.42,0.06,0.075,0.003); K.bx((g,'STEEL'),xc-0.10,xc+0.10,-4.40,-2.42,0.245,0.26,0.003)
    K.bx((g,'STEEL'),-10.64,-8.86,-4.38,-2.44,0.26,0.30,0.004)
    K.bx((g,'HAZARD'),-8.905,-8.86,-4.38,-2.44,0.26,0.302,0.002)
    for (x,y) in ((-10.58,-4.34),(-8.92,-4.34),(-10.58,-2.48),(-8.92,-2.48)): S.anchor(K,g,x,y,0.06,0.016,0.05)
    for y in (-4.30,-2.50): S.eyebolt(K,g,(-10.45,y,0.30),(1,0,0),0.045,0.011,'YELLOW'); S.eyebolt(K,g,(-9.06,y,0.30),(1,0,0),0.045,0.011,'YELLOW')
    # canopy
    K.bx((g,'AUDI_SATIN'),-10.60,-9.03,-4.27,-2.93,0.30,1.85,0.014)
    K.bx((g,'STEEL'),-10.60,-9.03,-4.27,-2.93,0.30,0.36,0.004)                       # bottom drip rail
    for yy in (-4.27,-3.60,-2.93):  K.bx((g,'STEEL'),-10.61,-9.02,yy-0.012,yy+0.012,0.36,1.84,0.004)   # vertical corner / post rails
    # doors: three lower service doors, louvred intake bank above the identity plate
    for (a,b,h) in ((-4.255,-3.85,'l0'),(-3.835,-3.43,'l1'),(-3.415,-2.945,'l0')): S.door(K,g,'+x',-9.0,a,b,0.37,1.05,h,'AUDI','T')
    S.louvres(K,g,'STEEL','+x',-9.0,-4.255,-3.62,1.40,1.80,7,0.03)
    S.louvres(K,g,'STEEL','+x',-9.0,-3.58,-2.945,1.40,1.80,7,0.03)
    S.warn_tri(K,g,'+x',-8.995,-4.15,1.27+0.0,0.12); S.warn_tri(K,g,'+x',-8.995,-3.05,1.27,0.12,'ORANGE')
    S.label_bar(K,g,'+x',-8.995,-4.22,-3.0,1.335,1.355,'YELLOW')
    # roof: cap with overhang, rain lip, corner lifting eyes, cable gland where the riser leaves
    K.bx((g,'STEEL'),-10.64,-8.99,-4.30,-2.90,1.85,1.90,0.006)
    K.bx((g,'AUDI'),-10.58,-9.05,-4.24,-2.96,1.90,2.0,0.012)
    for (x,y) in ((-10.50,-4.17),(-9.12,-4.17),(-10.50,-3.03),(-9.12,-3.03)): S.eyebolt(K,g,(x,y,2.0),(0,1,0),0.04,0.010,'YELLOW')
    K.cyl((g,'BRASS'),-10.2,-3.6,2.0,2.07,0.026,10,0.0); K.cyl((g,'BLACK'),-10.2,-3.6,2.07,2.14,0.016,10,0.0)
    # exhaust: flexible bellows, vertical silencer with bands, lagged pipe up to the wall sleeve
    bel=[(0.07,2.0)]
    for k in range(5): z=2.0+0.025+k*0.025; bel+=[(0.07,z),(0.095,z+0.0125),(0.07,z+0.025)]
    S.lathe(K,(g,'STEEL'),-10.05,-3.15,bel+[(0.07,2.16),(0.0,2.16)],seg=16)
    S.lathe(K,(g,'GALV'),-10.05,-3.15,[(0.0,2.16),(0.10,2.16),(0.165,2.20),(0.17,2.26),(0.17,2.68),(0.165,2.74),(0.12,2.80),(0.0,2.82)],seg=24)
    for z in (2.30,2.52,2.68): K.prism((g,'STEEL'),(-10.05,-3.15,z),(-10.05,-3.15,z+0.025),0.175,0.175,24,0.0,True,0.002)
    K.prism((g,'YELLOW'),(-10.05,-3.15,2.40),(-10.05,-3.15,2.46),0.172,0.172,24,0.0,True,0.0)     # hot-surface band
    S.lagged(K,g,[(-10.05,-3.15,2.60),(-10.42,-3.15,2.60),(-10.42,-3.15,2.85),(-10.64,-3.15,2.85)],0.062,0.30)
    K.prism((g,'STEEL'),(-10.64,-3.15,2.85),(-10.78,-3.15,2.85),0.085,0.085,16,0.0,True,0.0)
    S.flange(K,g,(-10.655,-3.15,2.85),(1,0,0),0.065,0.17,0.03,8,0.011,'IRON','STEEL',0.0)
    # alternator end: coupling flange, finned stator, end cap, terminal box
    K.prism((g,'STEEL'),(-9.90,-2.97,0.95),(-9.90,-2.92,0.95),0.40,0.40,28,0.0,True,0.003)
    K.prism((g,'AUDI'),(-9.90,-2.92,0.95),(-9.90,-2.50,0.95),0.37,0.37,32,0.0,True,0.004)
    for k in range(7): yy=-2.90+k*0.06; K.prism((g,'AUDI'),(-9.90,yy,0.95),(-9.90,yy+0.025,0.95),0.395,0.395,32,0.0,True,0.003)
    K.prism((g,'STEEL'),(-9.90,-2.50,0.95),(-9.90,-2.44,0.95),0.38,0.30,32,0.0,True,0.003)
    for k in range(10):
        th=2*math.pi*k/10; K.tube(('gen','BLACK'),[(-9.90+0.04*math.cos(th),-2.443,0.95+0.04*math.sin(th)),(-9.90+0.27*math.cos(th),-2.443,0.95+0.27*math.sin(th))],0.006,6)
    for xx in (-10.20,-9.60): K.bx((g,'STEEL'),xx-0.05,xx+0.05,-2.90,-2.52,0.30,0.58,0.004)             # alternator feet
    K.bx((g,'AUDI_SATIN'),-10.02,-9.78,-2.84,-2.60,1.31,1.49,0.008); K.bx((g,'STEEL'),-10.0,-9.8,-2.82,-2.62,1.49,1.505,0.003)
    S.screws(K,g,'+x',-9.78,-2.82,-2.62,1.33,1.47,0.0,0.005)
    for dy in (-0.04,0.04): K.prism((g,'BRASS'),(-9.90,-2.72+dy,1.31),(-9.90,-2.72+dy,1.275),0.015,0.015,8,0.0,True,0.0); K.prism((g,'BLACK'),(-9.90,-2.72+dy,1.28),(-9.90,-2.72+dy,1.20),0.009,0.009,8,0.0,True,0.0)
    # radiator end (the -y face): frame, mesh guard, filler cap, hot warning
    K.bx((g,'STEEL'),-10.52,-9.16,-4.40,-4.27,0.36,1.78,0.006)
    S.mesh_grille(K,g,'-y',-4.40,-10.46,-9.22,0.42,1.72,'BLACK',0.034)
    K.cyl((g,'RED'),-9.40,-4.20,1.85,1.93,0.035,12,0.0); K.cyl((g,'BRASS'),-9.40,-4.20,1.93,1.95,0.028,12,0.0)
    S.warn_tri(K,g,'-y',-4.405,-9.55,1.62,0.11,'YELLOW')
    # instrument line from the canopy to the start pod (clip-on conduit along the skid)
    S.conduit_up(K,g,-10.45,-4.30,0.30,0.60,0.012)
def reserve(K,tag,y0,y1,door_a,door_b,hinge,vent=None):
    g='res'+tag
    plinth(K,g,-10.70,-9.06,y0-0.05,y1+0.05,0.05)
    S_=S
    K.bx((g,'STEEL'),-10.62,-9.14,y0+0.02,y1-0.02,0.05,0.14,0.004)                              # kick plate
    K.bx((g,'AUDI_SATIN'),-10.65,-9.14,y0,y1,0.14,1.85,0.014)
    for yy in (y0+0.012,y1-0.012): K.bx((g,'STEEL'),-10.66,-9.13,yy-0.012,yy+0.012,0.14,1.84,0.004)
    # header band with vents, door with hinges and handle, battery-gas vent bay
    S.door(K,g,'+x',-9.12,door_a,door_b,0.22,1.50,hinge,'AUDI','bar',hz=0.60)
    if vent: S.louvres(K,g,'STEEL','+x',-9.12,vent[0],vent[1],0.26,1.48,9,0.028)
    if vent: S.louvres(K,g,'STEEL','+x',-9.12,vent[0],vent[1],1.56,1.78,3,0.02)
    S.warn_tri(K,g,'+x',-9.12,door_a+0.20,0.42,0.12,'YELLOW')
    S.label_bar(K,g,'+x',-9.12,door_a+0.02,door_b-0.02,1.515,1.535,'RED')
    # roof cap with gland where the cable riser leaves
    K.bx((g,'STEEL'),-10.68,-9.10,y0-0.03,y1+0.03,1.85,1.90,0.006); K.bx((g,'AUDI'),-10.62,-9.18,y0+0.03,y1-0.03,1.90,1.98,0.010)
    yc=(y0+y1)/2
    K.cyl((g,'BRASS'),-9.89,3.3 if tag=='A' else -4.93,1.98,2.05,0.026,10,0.0); K.cyl((g,'BLACK'),-9.89,3.3 if tag=='A' else -4.93,2.05,2.11,0.016,10,0.0)
    for (x,y) in ((-10.50,y0+0.1),(-9.30,y0+0.1),(-10.50,y1-0.1),(-9.30,y1-0.1)): S.eyebolt(K,g,(x,y,1.98),(0,1,0),0.038,0.010,'YELLOW')
    # charge-status lamps over the identity plate and an earth stud
    K.cyl((g,'BRASS'),-9.16,y1-0.08,0.20,0.30,0.012,8,0.0)
def bench(K):
    g='bench'
    yA,yB=4.38,5.33
    plinth(K,g,-10.66,-9.80,yA-0.02,yB+0.02,0.04)
    # steel frame: four legs, rails, lower shelf
    for (x,y) in ((-10.60,yA+0.04),(-9.90,yA+0.04),(-10.60,yB-0.04),(-9.90,yB-0.04)): K.bx((g,'STEEL'),x-0.035,x+0.035,y-0.035,y+0.035,0.04,0.88,0.004)
    K.bx((g,'STEEL'),-10.64,-9.86,yA,yB,0.88,0.93,0.006)                                             # worktop frame
    K.bx((g,'GALV'),-10.63,-9.84,yA-0.01,yB+0.01,0.93,0.955,0.004)                                   # stainless-look top
    K.bx((g,'RUBBER'),-10.54,-10.00,yA+0.08,yB-0.40,0.955,0.962,0.002)                               # rubber mat
    K.bx((g,'STEEL'),-9.845,-9.83,yA,yB,0.93,0.96,0.003)                                             # front lip
    K.bx((g,'STEEL'),-10.62,-9.88,yA+0.03,yB-0.03,0.24,0.28,0.004)                                   # lower shelf
    # drawer unit: 2 columns x 3 rows, handles, labels
    K.bx((g,'AUDI_SATIN'),-10.60,-9.86,yA+0.02,yB-0.02,0.30,0.88,0.008)
    yc=[yA+0.07,(yA+yB)/2+0.01,yB-0.07]
    for ci,(c0,c1) in enumerate(((yA+0.05,(yA+yB)/2-0.015),((yA+yB)/2+0.015,yB-0.05))):
        for (z0,z1) in ((0.33,0.52),(0.54,0.70),(0.72,0.86)):
            K.fb(('bench','AUDI'),'+x',-9.86,c0,c1,z0,z1,0.016,0.003); S.handle_bar(K,g,'+x',-9.846,(c0+c1)/2,(z0+z1)/2,(c1-c0)*0.55,0.0,'STEEL',False)
    S.label_bar(K,g,'+x',-9.845,yA+0.06,yA+0.30,0.865,0.88,'ORANGE')
    # back panel: perforated pegboard on posts with tools, shelf hood with a work lamp
    K.bx((g,'STEEL'),-10.66,-10.58,yA+0.0,yB,0.97,2.08,0.004)
    S.mesh_grille(K,g,'+x',-10.58,yA+0.04,yB-0.06,1.02,1.92,'BLACK',0.04)
    for k,(yy,z0,z1) in enumerate(((yA+0.16,1.18,1.62),(yA+0.36,1.30,1.78),(yA+0.58,1.20,1.55),(yA+0.80,1.25,1.70))):
        K.prism((g,'STEEL'),(-10.54,yy,z0),(-10.54,yy,z1),0.007,0.007,8,0.0,True,0.0); K.prism((g,'BLACK'),(-10.54,yy,z0-0.10),(-10.54,yy,z0+0.12),0.014,0.014,8,0.0,True,0.0)
    K.bx((g,'AUDI_SATIN'),-10.64,-10.36,yA,yB-0.2,1.94,2.12,0.008)
    S.louvres(K,g,'STEEL','+x',-10.36,yA+0.05,yB-0.25,1.97,2.09,2,0.012,False)
    # bench vice with a long ratchet handle
    K.bx((g,'IRON'),-9.98,-9.90,4.58,4.90,0.962,1.02,0.005); K.bx((g,'IRON'),-9.98,-9.92,4.62,4.86,1.02,1.08,0.004)
    K.prism((g,'STEEL'),(-9.92,4.74,0.99),(-9.84,4.74,0.99),0.011,0.011,8,0.0,True,0.0); K.prism((g,'ORANGE'),(-9.84,4.64,0.99),(-9.84,4.84,0.99),0.0085,0.0085,8,0.0,True,0.0)
    # tool tray with spanners
    K.bx((g,'STEEL'),-10.45,-10.15,yB-0.38,yB-0.05,0.962,0.985,0.003)
