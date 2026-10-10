"""STATIONS pass, north wall: fuel storage rack with overhead hoist and handling pole, fuel receiving table, service post and junction box, notice board.  World coordinates, north wall inner face y = 10.8."""
import math
from mathutils import Vector
import rh_stlib as S
def plinth(K,g,x0,x1,y0,y1,h=0.05): K.bx((g,'CONC_DARK'),x0,x1,y0,y1,0.0,h,0.012)
def fuel_rack(K):
    g='frack'
    plinth(K,g,-5.52,-3.93,8.82,10.62,0.05)
    posts=[(-5.355,9.02),(-4.085,9.02),(-5.355,10.445),(-4.085,10.445)]
    for (x,y) in posts:
        K.bx((g,'GALV'),x-0.04,x+0.04,y-0.04,y+0.04,0.05,2.50,0.004)
        K.bx((g,'STEEL'),x-0.075,x+0.075,y-0.075,y+0.075,0.05,0.068,0.003)
        for (dx,dy) in ((-1,-1),(1,-1),(-1,1),(1,1)): K.cyl((g,'STEEL'),x+dx*0.052,y+dy*0.052,0.068,0.088,0.008,6,0.0)
    for z in (2.44,):                                                                       # top frame
        for x in (-5.355,-4.085): K.bx((g,'GALV'),x-0.03,x+0.03,9.02,10.445,z,2.50,0.003)
        for y in (9.02,10.445): K.bx((g,'GALV'),-5.355,-4.085,y-0.03,y+0.03,z,2.50,0.003)
    for (x,sg) in ((-5.355,1),(-4.085,-1)):                                                  # side X-bracing (tubes with gusset plates)
        K.tube((g,'STEEL'),[(x,9.06,0.10),(x,10.40,2.40)],0.012,6); K.tube((g,'STEEL'),[(x,10.40,0.10),(x,9.06,2.40)],0.012,6)
    for zt in (0.36,1.36):                                                                   # two tiers: front tie beam, rails, cradles for three assemblies
        K.bx((g,'GALV'),-5.40,-4.05,8.90,8.97,zt-0.09,zt+0.06,0.004)
        K.bx((g,'YELLOW'),-5.40,-4.05,8.90,8.97,zt+0.06,zt+0.075,0.002)
        for xr in (-5.35,-4.72,-4.09):
            K.bx((g,'GALV'),xr-0.035,xr+0.035,9.02,10.45,zt,zt+0.03,0.003); K.bx((g,'GALV'),xr-0.01,xr+0.01,9.02,10.45,zt+0.03,zt+0.06,0.002)
        for xc in (-5.105,-4.715,-4.335):
            for yc in (9.30,10.15):
                K.hull((g,'RUBBER'),[(xc-0.16,yc-0.07,zt+0.03),(xc+0.16,yc-0.07,zt+0.03),(xc-0.16,yc+0.07,zt+0.03),(xc+0.16,yc+0.07,zt+0.03),(xc-0.09,yc-0.07,zt+0.115),(xc+0.09,yc-0.07,zt+0.115),(xc-0.09,yc+0.07,zt+0.115),(xc+0.09,yc+0.07,zt+0.115)],0.004)
        for xd in (-4.91,-4.525):                                                            # egg-crate dividers between the slots (the rack grid)
            K.bx((g,'GALV'),xd-0.008,xd+0.008,9.08,10.38,zt+0.03,zt+0.44,0.002)
            for yy in (9.45,9.75,10.05): K.bx((g,'STEEL'),xd-0.012,xd+0.012,yy-0.012,yy+0.012,zt+0.03,zt+0.44,0.002)
        S.warn_tri(K,g,'-y',8.90,-4.18,zt-0.015,0.085,'YELLOW')
    # overhead monorail with trolley hoist, chain and hook block
    for x in (-4.90,-4.50):
        K.bx((g,'STEEL'),x-0.055,x+0.055,9.0,10.50,2.50,2.52,0.003); K.bx((g,'STEEL'),x-0.012,x+0.012,9.0,10.50,2.52,2.54,0.002); K.bx((g,'STEEL'),x-0.055,x+0.055,9.0,10.50,2.54,2.56,0.003)
    for y in (9.0,10.5): K.bx((g,'YELLOW'),-4.96,-4.44,y-0.015 if y<10 else y-0.0,y+0.015 if y<10 else y+0.015,2.50,2.56,0.003)
    K.bx((g,'AUDI'),-4.93,-4.57,9.58,9.92,2.24,2.50,0.012); K.bx((g,'YELLOW'),-4.93,-4.57,9.58,9.92,2.44,2.47,0.002)
    for yw in (9.60,9.90):
        for xw in (-4.90,-4.50): K.prism((g,'STEEL'),(xw-0.02,yw,2.585),(xw+0.02,yw,2.585),0.028,0.028,12,0.0,True,0.0)
    K.prism((g,'STEEL'),(-4.75,9.75,1.96),(-4.75,9.75,2.24),0.011,0.011,8,0.0,True,0.0)
    K.bx((g,'YELLOW'),-4.80,-4.70,9.70,9.80,1.86,1.96,0.008); S.torus(K,g,'STEEL',(-4.75,9.75,1.82),(0,1,0),0.04,0.009,10,6)
    # handling pole parked on the west side with clips, fuel manifest board on the wall
    K.prism((g,'GALV'),(-5.455,10.20,0.10),(-5.455,10.20,2.30),0.014,0.014,8,0.0,True,0.0); K.prism((g,'STEEL'),(-5.455,10.20,2.30),(-5.455,10.20,2.40),0.03,0.02,10,0.0,True,0.002)
    for z in (0.7,1.6): K.bx((g,'STEEL'),-5.47,-5.395,10.185,10.215,z-0.02,z+0.02,0.002); K.prism((g,'STEEL'),(-5.455,10.20,z-0.01),(-5.455,10.20,z+0.01),0.024,0.024,12,0.0,False,0.0)
    K.bx((g,'WHITE'),-3.90,-3.40,10.578,10.594,2.02,2.34,0.003); K.bx((g,'STEEL'),-3.92,-3.38,10.594,10.627,2.0,2.36,0.003)
    for x in (-3.88,-3.42): K.bx((g,'STEEL'),x-0.012,x+0.012,10.597,10.80,2.30,2.34,0.002)
def fuel_table(K):
    g='ftab'
    K.bx((g,'STEEL'),-4.00,-2.90,9.04,10.36,0.0,0.12,0.004)
    K.bx((g,'AUDI_SATIN'),-4.05,-2.85,9.0,10.4,0.12,0.76,0.012)
    K.bx((g,'GALV'),-4.07,-2.83,8.98,10.42,0.76,0.80,0.005)
    for (x0,x1) in ((-4.07,-2.83),): K.bx((g,'STEEL'),x0,x1,10.40,10.42,0.80,0.84,0.003)
    for (a,b) in ((-4.0,-3.435),(-3.425,-2.89)):
        K.fb((g,'AUDI'),'-y',9.0,a,b,0.16,0.70,0.03,0.004); S.screws(K,g,'-y',8.97,a,b,0.16,0.70,0.0,0.005)
    for xx in (-3.84,-3.02): K.bx((g,'STEEL'),xx-0.018,xx+0.018,8.96,9.0,0.72,0.82,0.002)
    for xc in (-3.805,-3.425,-3.055):
        for yc in (9.30,10.10):
            K.hull(('ftab','RUBBER'),[(xc-0.16,yc-0.07,0.80),(xc+0.16,yc-0.07,0.80),(xc-0.16,yc+0.07,0.80),(xc+0.16,yc+0.07,0.80),(xc-0.09,yc-0.07,0.915),(xc+0.09,yc-0.07,0.915),(xc-0.09,yc+0.07,0.915),(xc+0.09,yc+0.07,0.915)],0.004)
def service_post(K):
    g='spost'
    plinth(K,g,4.64,5.36,9.74,10.54,0.05)
    K.bx((g,'AUDI_SATIN'),4.72,5.28,9.83,10.45,0.05,1.42,0.012); K.bx((g,'STEEL'),4.70,5.30,9.81,10.47,1.42,1.46,0.005)
    for k in range(4):
        z0=0.08+k*0.33; K.fb((g,'AUDI'),'-y',9.83,4.76,5.24,z0,z0+0.29,0.012,0.003); S.label_bar(K,g,'-y',9.82,4.80,5.20,z0+0.20,z0+0.255,'WHITE',0.003); S.label_bar(K,g,'-y',9.82,4.80,4.94,z0+0.05,z0+0.075,['RED','ORANGE','YELLOW','RED'][k],0.003)
    S.conduit_up(K,g,4.78,10.30,1.46,2.30,0.018)
    S.jbox(K,g,'-y',10.57,4.78,2.30,0.30,0.22,0.12,'AUDI_SATIN',2)
    S.lamp(K,g,(4.78,10.445,2.38),(0,-1,0),0.014,'LAMP_G')
def west_cart(K):
    g='cart'
    # fuel transfer cart: ribbed deck, rubber casters, push frame with grips, cradle rails with strap, control column with pendant
    K.bx((g,'STEEL'),-9.78,-8.22,6.70,8.20,0.28,0.34,0.006); K.bx((g,'YELLOW'),-9.80,-8.20,6.68,8.22,0.34,0.38,0.006)
    for y in (6.9,7.4,7.9): K.bx((g,'STEEL'),-9.74,-8.26,y-0.02,y+0.02,0.20,0.28,0.003)
    for (x,y) in ((-9.72,6.78),(-9.72,8.12),(-8.28,6.78),(-8.28,8.12)):
        K.bx((g,'STEEL'),x-0.05,x+0.05,y-0.05,y+0.05,0.20,0.28,0.003); K.cyl((g,'STEEL'),x,y,0.185,0.20,0.04,12,0.0)
        K.prism((g,'RUBBER'),(x-0.03,y,0.10),(x+0.03,y,0.10),0.10,0.10,20,0.0,True,0.004); K.prism((g,'STEEL'),(x-0.045,y,0.10),(x+0.045,y,0.10),0.022,0.022,10,0.0,True,0.0)
        K.bx((g,'STEEL'),x-0.055,x-0.04,y-0.03,y+0.03,0.10,0.20,0.002); K.bx((g,'STEEL'),x+0.04,x+0.055,y-0.03,y+0.03,0.10,0.20,0.002)
    for x in (-9.50,-8.50): K.bx((g,'GALV'),x-0.07,x+0.07,6.72,8.18,0.38,0.47,0.004)
    for y in (7.0,7.9):                                                                     # tie-down straps over the cradle rails
        K.bx((g,'ORANGE'),-9.60,-8.40,y-0.02,y+0.02,0.47,0.485,0.001)
    for x in (-9.52,-8.48): K.bx((g,'STEEL'),x-0.02,x+0.02,8.18,8.23,0.40,1.0,0.003)
    K.prism((g,'RUBBER'),(-9.55,8.205,1.0),(-8.45,8.205,1.0),0.017,0.017,10,0.0,True,0.0); K.bx((g,'STEEL'),-9.55,-8.45,8.17,8.24,0.95,0.965,0.002)
    K.bx((g,'STEEL'),-9.15,-8.75,7.97,8.35,0.40,1.42,0.006); K.bx((g,'AUDI_SATIN'),-9.18,-8.72,7.92,8.26,1.35,1.55,0.012)
    K.bx((g,'AUDI'),-9.13,-8.77,7.93,7.95,1.0,1.40,0.003)
    for k,(m,x) in enumerate((('GREEN',-9.04),('RED',-8.86))):
        S.pushbutton(K,g,(x,7.93,1.18),(0,-1,0),0.02,'RED' if m=='RED' else 'LAMP_G')
