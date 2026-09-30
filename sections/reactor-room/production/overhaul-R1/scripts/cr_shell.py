"""Control-room shell: wall cladding (dado panels, plaster modules, rails, base cove), door frame, corner guards, floor markings,
suspended ceiling (T-bar grid, tiles, missing tiles, plenum), troffer fixtures, window fittings."""
import math
from crk import text
X0,X1,Y0,YF,FZ,CZ,TOP=-4.80,2.00,-11.91,-6.16,5.40,8.50,8.80
DADO=6.65
def build(c):
    A,M,R=c.A,c.M,c.R
    g="wall"
    # ---------------- base cove + dado + plaster modules on the three solid walls
    def run(face,p,l0,l1):
        sg=-1 if face in('-x','-y') else 1
        A.fb((g,"RUBBER"),face,p,l0,l1,FZ,FZ+0.09,0.008,0.002)                       # rubber cove base
        n=max(1,round((l1-l0)/0.75)); w=(l1-l0)/n
        for i in range(n):                                                             # dado panels
            a,b=l0+i*w+0.003,l0+(i+1)*w-0.003
            A.fb((g,"WALL_LO"),face,p+sg*0.008,a,b,FZ+0.09,DADO-0.03,0.018,0.004)
            for zz in (FZ+0.16,DADO-0.10):                                            # panel screws
                for u in (a+0.03,b-0.03): A.screw((g,"STEEL_L"),face,p+sg*0.026,u,zz,0.005)
        A.fb((g,"TRIM"),face,p+sg*0.004,l0,l1,DADO-0.03,DADO+0.02,0.038,0.004)          # dado rail
        A.fb((g,"YELLOW"),face,p+sg*0.004,l0,l1,DADO+0.02,DADO+0.028,0.030,0.001)       # painted hazard line on the rail top edge
        m=max(1,round((l1-l0)/1.2)); w2=(l1-l0)/m
        for i in range(m):                                                             # mineral plaster modules with reveal joints
            a,b=l0+i*w2+0.004,l0+(i+1)*w2-0.004
            A.fb((g,"WALL_HI"),face,p+sg*0.004,a,b,DADO+0.02,CZ-0.03,0.016,0.004)
        A.fb((g,"TRIM"),face,p+sg*0.004,l0,l1,CZ-0.03,CZ+0.0,0.026,0.003)                # picture-rail / ceiling angle
    run('+x',X0,-11.91,-7.34)                        # west wall south of the door
    run('-x',X1,Y0,YF)                                # east wall
    run('+y',Y0,X0,X1)                                # back wall
    # front (window) wall: base cove + sill plate only
    A.fb((g,"RUBBER"),'-y',YF+0.06,X0,X1,FZ,FZ+0.09,0.008,0.002)
    # ---------------- door frame (west wall, opening y -7.26 .. -6.34, z to 7.6)
    dy0,dy1,dz=-7.26,-6.34,7.60
    for (a,b) in ((dy0-0.075,dy0),(dy1,dy1+0.075)):
        A.fb((g,"TRIM"),'+x',X0,a,b,FZ,dz+0.07,0.06,0.006)
    A.fb((g,"TRIM"),'+x',X0,dy0-0.075,dy1+0.075,dz,dz+0.075,0.06,0.006)
    for zz in (FZ+0.25,FZ+1.1,FZ+1.9):                                                   # hinge plates + strike
        A.fb((g,"STEEL_L"),'+x',X0+0.06,dy1+0.015,dy1+0.06,zz,zz+0.11,0.008,0.002)          # hinge plates on the NORTH jamb (the door leaf is hinged there)
        for k in range(3): A.screw((g,"STEEL"),'+x',X0+0.068,dy1+0.0375,zz+0.02+k*0.035,0.004)
    A.fb((g,"STEEL_L"),'+x',X0+0.06,dy0-0.06,dy0-0.02,FZ+1.02,FZ+1.22,0.008,0.002)          # strike plate on the south jamb
    A.bx((g,"STEEL"),X0,X0+0.16,dy0,dy1,FZ,FZ+0.014,0.003)                                # threshold plate
    for k in range(6): A.bx((g,"YELLOW"),X0+0.02,X0+0.14,dy0+0.05+k*0.15,dy0+0.10+k*0.15,FZ+0.014,FZ+0.016,0.0)
    A.fb((g,"BLACK"),'+x',X0+0.06,dy0-0.02,dy1+0.02,dz+0.075,dz+0.30,0.03,0.005)          # door sign box
    text(c.coll,"AUTHORISED\nPERSONNEL ONLY",X0+0.093,(dy0+dy1)/2,dz+0.19,'+x',0.036,M["YELLOW"],'CENTER',"CR door sign",spacing=1.0)
    # ---------------- corner guards + column covers
    for (x,y,sx,sy) in ((X0,Y0,1,1),(X1,Y0,-1,1),(X1,YF,-1,-1)):
        A.bx((g,"TRIM"),min(x,x+sx*0.06),max(x,x+sx*0.06),min(y,y+sy*0.06),max(y,y+sy*0.06),FZ,FZ+1.25,0.006)
        A.bx((g,"YELLOW"),min(x,x+sx*0.062),max(x,x+sx*0.062),min(y,y+sy*0.062),max(y,y+sy*0.062),FZ+0.55,FZ+0.65,0.001)
    # ---------------- floor markings (thin paint)
    A.bx((g,"YELLOW"),-3.65,1.55,-7.80,-7.74,FZ,FZ+0.0025,0.0)                              # operator line at the desk row
    for k in range(9): A.bx((g,"HAZARD"),-0.55+k*0.0,-0.55,0,0,0,0) if False else None
    # ---------------- suspended ceiling
    xs=[X0+0.6*k for k in range(0,12)]+[X1]; xs=[x for x in xs if x<=X1+1e-6]
    if xs[-1]-xs[-2]<0.05: xs.pop(-2)
    ys=[YF-0.6*k for k in range(0,10)]+[Y0]; ys=[y for y in ys if y>=Y0-1e-6]
    if ys[-2]-ys[-1]<0.05: ys.pop(-2)
    g="ceil"
    tr=set(c.TROFFERS)                                                                     # (i,j) tile cells replaced by fixtures
    missing=set(c.MISSING)
    for i in range(len(xs)-1):
        for j in range(len(ys)-1):
            xa,xb,ya,yb=xs[i],xs[i+1],ys[j+1],ys[j]
            if (i,j) in tr or (i,j) in missing: continue
            A.bx((g,"CEIL"),xa+0.013,xb-0.013,ya+0.013,yb-0.013,CZ+0.012,CZ+0.03,0.004)
    for x in xs[1:-1]: A.bx((g,"CEIL_GRID"),x-0.012,x+0.012,Y0,YF,CZ,CZ+0.032,0.002)
    for y in ys[1:-1]: A.bx((g,"CEIL_GRID"),X0,X1,y-0.012,y+0.012,CZ,CZ+0.032,0.002)
    A.bx((g,"CEIL_GRID"),X0,X1,Y0,Y0+0.03,CZ-0.002,CZ+0.03,0.002)                          # wall angle
    A.bx((g,"CEIL_GRID"),X0,X0+0.03,Y0,YF,CZ-0.002,CZ+0.03,0.002); A.bx((g,"CEIL_GRID"),X1-0.03,X1,Y0,YF,CZ-0.002,CZ+0.03,0.002)
    # plenum: cable tray + duct above the missing tiles
    A.bx((g,"STEEL"),X0+0.2,X1-0.2,-9.05,-8.85,8.62,8.70,0.004); A.bx((g,"STEEL"),X0+0.2,X1-0.2,-9.05,-9.03,8.70,8.74,0.002); A.bx((g,"STEEL"),X0+0.2,X1-0.2,-8.87,-8.85,8.70,8.74,0.002)
    for k in range(9): A.cylx((g,"CABLE"),X0+0.25+k*0.0,X1-0.25,-8.99+k*0.02,8.715,0.006,6)
    A.bx((g,"STEEL_L"),X0+0.3,X1-0.6,-10.55,-10.05,8.60,8.78,0.006)                       # duct
    for k in range(7): A.bx((g,"STEEL"),X0+0.6+k*0.9,X0+0.66+k*0.9,-10.57,-10.03,8.59,8.79,0.003)
    # troffer fixtures
    for (i,j,flick) in c.TROFFER_LIST:
        xa,xb,ya,yb=xs[i],xs[i+2],ys[j+1],ys[j]
        A.bx((g,"CEIL_GRID"),xa+0.012,xb-0.012,ya+0.012,yb-0.012,CZ-0.005,CZ+0.06,0.004)    # housing lip
        A.bx((g,"BLACK"),xa+0.03,xb-0.03,ya+0.03,yb-0.03,CZ+0.02,CZ+0.05,0.002)
        for k in range(2): A.bx((g,"TUBE_F" if flick else "TUBE"),xa+0.10,xb-0.10,ya+0.12+k*(yb-ya-0.30),ya+0.16+k*(yb-ya-0.30),CZ+0.004,CZ+0.02,0.001)
        for k in range(8): A.bx((g,"CEIL_GRID"),xa+0.03+k*((xb-xa-0.06)/8),xa+0.036+k*((xb-xa-0.06)/8),ya+0.03,yb-0.03,CZ-0.012,CZ+0.0,0.001)   # louvre ribs
    return xs,ys
