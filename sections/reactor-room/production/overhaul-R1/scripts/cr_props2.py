"""Wall dressing, desk clutter and small fittings: posters, pinboard + forms, aircon, extinguisher, hooks, PA horn, camera, outlets, phone, lamps, floppies, pens."""
import math
from cr_props1 import wall_quad,FZ
from crk import text
ZT=6.17
def desk_clutter(c):
    A,M,R=c.A,c.M,c.R; g="clutter"
    # bay 1: notepad + pen + mug + floppies
    A.box((g,"PAPER"),-3.36,-7.30,ZT,ZT+0.02,0.15,0.21,0.18,0.002); A.box((g,"CARD"),-3.36,-7.30,ZT+0.02,ZT+0.0215,0.145,0.205,0.18,0.0)
    for i in range(6): A.box((g,"BLACK"),-3.36,-7.35+i*0.02,ZT+0.0216,ZT+0.0219,0.11,0.002,0.18,0.0)
    A.prism((g,"BLUE_PEN") if False else (g,"ORANGE"),(-3.30,-7.36,ZT+0.026),(-3.22,-7.18,ZT+0.026),0.0055,0.0055,10); A.prism((g,"BLACK"),(-3.22,-7.18,ZT+0.026),(-3.205,-7.15,ZT+0.026),0.0055,0.0025,10)
    A.prism((g,"PORC"),(-3.46,-7.02,ZT),(-3.46,-7.02,ZT+0.095),0.038,0.042,20,0,True,0.002); A.bx((g,"PORC"),-3.42-0.0,-3.395,-7.028,-7.016,ZT+0.03,ZT+0.075,0.003); A.prism((g,"BLACK"),(-3.46,-7.02,ZT+0.09),(-3.46,-7.02,ZT+0.0915),0.034,0.034,20,0,True)
    for k,(fx,fy,ang) in enumerate(((-3.38,-6.86,0.4),(-3.33,-6.83,-0.2),(-3.42,-6.90,0.9))):
        A.box((g,"BLACK"),fx,fy,ZT+k*0.0035,ZT+0.0035+k*0.0035,0.09,0.09,ang,0.0008); A.box((g,"STEEL_L"),fx+0.012*math.cos(ang),fy+0.012*math.sin(ang),ZT+0.0035+k*0.0035,ZT+0.0042+k*0.0035,0.04,0.03,ang,0.0)
    A.bx((g,"CARD"),-3.55,-3.20,-6.55,-6.40,ZT,ZT+0.09,0.004)                                                # paper ream box at the back
    A.fb((g,"PAPER"),'-y',-6.55,-3.50,-3.30,ZT+0.03,ZT+0.06,0.0015,0.0)
    # bay 2: push-button phone with curly cord + stapler
    px,py=-1.52,-7.15
    A.hull((g,"BEIGE"),[(px-0.11,py-0.10,ZT),(px+0.11,py-0.10,ZT),(px-0.11,py+0.10,ZT),(px+0.11,py+0.10,ZT),(px-0.10,py-0.09,ZT+0.045),(px+0.10,py-0.09,ZT+0.045),(px-0.10,py+0.10,ZT+0.075),(px+0.10,py+0.10,ZT+0.075)],0.006)
    for r in range(4):
        for k in range(3): A.bx((g,"KEY"),px-0.045+k*0.034,px-0.045+k*0.034+0.026,py-0.075+r*0.03,py-0.075+r*0.03+0.022,ZT+0.048+r*0.006,ZT+0.056+r*0.006,0.002)
    A.hull((g,"BEIGE"),[(px-0.13,py-0.03,ZT+0.09),(px+0.13,py-0.03,ZT+0.09),(px-0.13,py+0.05,ZT+0.09),(px+0.13,py+0.05,ZT+0.09),(px-0.10,py-0.03,ZT+0.125),(px+0.10,py-0.03,ZT+0.125),(px-0.10,py+0.05,ZT+0.125),(px+0.10,py+0.05,ZT+0.125)],0.008)
    prev=None
    for t in range(0,49):
        a=t/48*2*math.pi*7; p=(px+0.135+(t/48)*0.06,py-0.06+0.014*math.cos(a),ZT+0.04+0.014*math.sin(a))
        if prev: A.prism((g,"CABLE_B"),prev,p,0.0028,0.0028,5,0,False)
        prev=p
    A.bx((g,"RED"),-1.95,-1.86,-7.32,-7.20,ZT,ZT+0.03,0.004); A.bx((g,"STEEL_L"),-1.95,-1.86,-7.32,-7.30,ZT+0.03,ZT+0.045,0.002)   # stapler
    A.prism((g,"STEEL"),(-1.68,-6.62,ZT),(-1.68,-6.62,ZT+0.10),0.04,0.04,18,0,True,0.002)                     # pen cup
    for k,mk in enumerate(("ORANGE","BLACK","YELLOW","RED","BLACK")): A.prism((g,mk),(-1.68,-6.62,ZT+0.09),(-1.68+0.018*(k-2),-6.62+0.010*(k-2),ZT+0.19),0.0045,0.0045,8)
    # bay 3: banker lamp, in-tray, diskette box, binder, mug, calculator
    lx,ly=1.18,-6.78
    A.cyl((g,"BLACK"),lx,ly,ZT,ZT+0.025,0.08,24,0.004); A.prism((g,"BRASS"),(lx,ly,ZT+0.025),(lx-0.03,ly-0.03,ZT+0.30),0.008,0.008,8); A.prism((g,"BRASS"),(lx-0.03,ly-0.03,ZT+0.30),(lx-0.16,ly-0.12,ZT+0.36),0.008,0.008,8)
    A.prism((g,"LOCKER"),(lx-0.16,ly-0.12,ZT+0.38),(lx-0.20,ly-0.14,ZT+0.28),0.045,0.115,24,0,True,0.003); A.prism((g,"BULB"),(lx-0.19,ly-0.135,ZT+0.285),(lx-0.195,ly-0.14,ZT+0.27),0.03,0.03,12,0,True)
    c.DESKLAMP=(lx-0.19,ly-0.14,ZT+0.26)
    for k in range(3): A.bx((g,"STEEL"),0.92,1.12,-6.62-k*0.0,-6.42,ZT+0.005+k*0.045,ZT+0.012+k*0.045,0.002) if False else A.bx((g,"STEEL"),0.98,1.18,-6.56,-6.43,ZT+0.005+k*0.045,ZT+0.012+k*0.045,0.002)
    for k in range(3): A.bx((g,"PAPER"),0.99,1.17,-6.55,-6.44,ZT+0.012+k*0.045,ZT+0.03+k*0.045,0.0)
    A.bx((g,"BLACK"),0.40,0.60,-6.98,-6.80,ZT,ZT+0.09,0.004); A.fb((g,"PAPER"),'-y',-6.98,0.44,0.56,ZT+0.03,ZT+0.07,0.0015,0.0)                                        # disk box
    A.bx((g,"RED"),0.30,0.55,-7.45,-7.20,ZT,ZT+0.035,0.004); A.bx((g,"PAPER"),0.315,0.535,-7.435,-7.215,ZT+0.035,ZT+0.05,0.0)
    for i in range(5): A.bx((g,"BLACK"),0.33,0.51,-7.42+i*0.04,-7.415+i*0.04,ZT+0.0505,ZT+0.0512,0.0)
    A.prism((g,"PORC_O"),(0.95,-7.45,ZT),(0.95,-7.45,ZT+0.09),0.038,0.042,20,0,True,0.002); A.bx((g,"PORC_O"),0.99,1.015,-7.456,-7.444,ZT+0.03,ZT+0.07,0.003)
    A.bx((g,"BLACK"),1.22,1.34,-7.48,-7.36,ZT,ZT+0.02,0.003)                                                 # calculator
    for r in range(4):
        for k in range(3): A.bx((g,"KEY"),1.235+k*0.032,1.235+k*0.032+0.024,-7.465+r*0.028,-7.465+r*0.028+0.021,ZT+0.02,ZT+0.026,0.001)
    A.bx((g,"LED_AON"),1.235,1.325,-7.372,-7.362,ZT+0.02,ZT+0.024,0.0) if False else None
    # scattered sheets
    for (x,y,a,mk) in ((-2.20,-7.35,0.2,"PAPER"),(-0.30,-7.42,-0.15,"PAPER"),(0.05,-7.02,0.3,"PAPER"),(-1.20,-7.50,0.05,"PAPER")):
        A.box((g,mk),x,y,ZT,ZT+0.0012,0.21,0.297,a,0.0)
        for i in range(5): A.box((g,"BLACK"),x,y-0.08+i*0.035,ZT+0.0013,ZT+0.0016,0.15,0.004,a,0.0)
def wall_decor(c):
    A,M=c.A,c.M; g="deco"; yb=-11.91
    for (k,lc,zc,w,h) in (("machine",-4.25,7.28,0.70,0.98),("shift",-3.20,7.28,0.70,0.98),("hydrate",1.37,7.45,0.40,0.56)):
        wall_quad(c,'+y',yb,lc,zc,w,h,"P_"+k)
    wall_quad(c,'+x',-4.80,-10.97,7.30,0.70,0.98,"P_report"); wall_quad(c,'-x',2.00,-9.85,7.30,0.70,0.98,"P_questions")
    wall_quad(c,'-x',2.00,-11.45,7.95,0.70,0.98,"P_comply")
    # pinboard behind the desk end (east wall) with forms
    A.fb((g,"CORK"),'-x',1.985,-7.55,-6.40,6.83,7.78,0.016,0.004)
    for (a,b,z0,z1) in ((-7.58,-6.37,6.80,6.83),(-7.58,-6.37,7.78,7.81)): A.fb((g,"TRIM"),'-x',1.985,a,b,z0,z1,0.026,0.003)
    for (a,b) in ((-7.58,-7.55),(-6.40,-6.37)): A.fb((g,"TRIM"),'-x',1.985,a,b,6.80,7.81,0.026,0.003)
    for (k,lc,zc,w,h) in (("roster",-6.62,7.34,0.20,0.27),("form",-6.95,7.40,0.20,0.27),("log",-7.27,7.33,0.20,0.27),("passcard",-7.12,7.03,0.12,0.16),("safety",-6.72,7.04,0.14,0.19)):
        wall_quad(c,'-x',1.985,lc,zc,w,h,"N_"+k,frame=False,off=0.017)
        A.cyl((g,"RED"),1.98,lc,zc+h/2-0.02,zc+h/2-0.02,0,3) if False else A.prism((g,"RED" if k in("roster","log") else "YELLOW"),(1.964,lc,zc+h/2-0.02),(1.952,lc,zc+h/2-0.02),0.006,0.006,10)
    # forms by the copier and near the door
    wall_quad(c,'-x',2.00,-8.42,7.05,0.24,0.32,"N_rules",frame=False); wall_quad(c,'-x',2.00,-8.82,7.02,0.20,0.27,"N_form",frame=False)
    wall_quad(c,'+x',-4.80,-8.02,7.75,0.20,0.27,"N_safety",frame=False)
    # coat hooks + hard hat + work jacket (west wall south of the door)
    A.fb((g,"TRIM"),'+x',-4.785,-8.12,-7.50,7.02,7.08,0.03,0.003)
    for y in (-8.03,-7.80,-7.57): A.prism((g,"STEEL_L"),(-4.77,y,7.05),(-4.64,y,7.10),0.008,0.008,8)
    A.hull((g,"YELLOW"),[(-4.60,-8.11,6.90),(-4.75,-8.11,6.90),(-4.60,-7.95,6.90),(-4.75,-7.95,6.90),(-4.65,-8.10,7.0),(-4.73,-8.10,7.0),(-4.65,-7.96,7.0),(-4.73,-7.96,7.0)],0.02)
    A.bx((g,"YELLOW"),-4.60,-4.56,-8.12,-7.94,6.90,6.905,0.0)
    A.hull((g,"FABRIC"),[(-4.76,-7.83,6.18),(-4.62,-7.83,6.18),(-4.76,-7.55,6.18),(-4.62,-7.55,6.18),(-4.76,-7.80,7.03),(-4.68,-7.80,7.03),(-4.76,-7.58,7.03),(-4.68,-7.58,7.03)],0.02)
    A.bx((g,"ORANGE"),-4.70,-4.685,-7.84,-7.54,6.60,6.66,0.002)                                              # hi-vis stripe on the jacket
    # fire extinguisher (west wall, by the door)
    A.fb((g,"STEEL"),'+x',-4.774,-7.60,-7.46,5.95,6.03,0.04,0.003); A.fb((g,"STEEL"),'+x',-4.774,-7.60,-7.46,6.25,6.32,0.04,0.003)
    A.prism((g,"RED"),(-4.72,-7.53,5.72),(-4.72,-7.53,6.32),0.07,0.07,26,0,True,0.006); A.prism((g,"BLACK"),(-4.72,-7.53,5.72),(-4.72,-7.53,5.745),0.071,0.071,26)
    A.prism((g,"BRASS"),(-4.72,-7.53,6.32),(-4.72,-7.53,6.38),0.028,0.02,16); A.bx((g,"BLACK"),-4.76,-4.66,-7.545,-7.515,6.38,6.405,0.003); A.tube((g,"CABLE"),[(-4.70,-7.53,6.36),(-4.62,-7.60,6.28),(-4.62,-7.62,6.06),(-4.68,-7.56,5.98)],0.007,8)
    A.fb((g,"RED"),'+x',-4.774,-7.66,-7.40,6.74,7.00,0.005,0.001); A.fb((g,"PAPER"),'+x',-4.769,-7.62,-7.44,6.82,6.86,0.002,0.0)
    text(c.coll,"FIRE",-4.789,-7.53,6.68,'+x',0.04,M["PAPER"],'CENTER',"CR fire sign") if False else None
    # aircon (east wall, above the copier)
    ya,yb2=-9.30,-8.05
    A.fb((g,"AC"),'-x',2.0,ya,yb2,7.72,8.22,0.22,0.02); A.fb((g,"AC"),'-x',1.78,ya+0.01,yb2-0.01,7.74,8.20,0.02,0.012)
    A.hull((g,"BEIGE_D"),[(1.78,ya+0.04,7.70),(1.78,yb2-0.04,7.70),(1.70,ya+0.04,7.78),(1.70,yb2-0.04,7.78),(1.78,ya+0.04,7.75),(1.78,yb2-0.04,7.75),(1.74,ya+0.04,7.77),(1.74,yb2-0.04,7.77)],0.004)
    for k in range(9): A.fb((g,"BLACK"),'-x',1.78,ya+0.05,yb2-0.05,7.79+k*0.04,7.805+k*0.04,0.006,0.0008)
    A.fb((g,"BLACK"),'-x',1.78,yb2-0.28,yb2-0.06,8.12,8.17,0.003,0.001); A.fb((g,"LED_ON"),'-x',1.78,yb2-0.26,yb2-0.245,8.132,8.148,0.004,0.0); A.fb((g,"LED_AON"),'-x',1.78,yb2-0.22,yb2-0.205,8.132,8.148,0.004,0.0)
    text(c.coll,"CIRRUS",1.779,ya+0.14,8.145,'-x',0.022,M["KEY_D"],'LEFT',"CR ac brand")
    A.prism((g,"STEEL_L"),(1.98,ya+0.06,7.76),(1.98,ya+0.06,8.50),0.013,0.013,10); A.prism((g,"CABLE"),(1.985,ya+0.11,7.74),(1.985,ya+0.11,8.50),0.009,0.009,8)   # pipe run to the ceiling
    A.tube((g,"CABLE_G"),[(1.90,ya+0.20,7.72),(1.92,ya+0.20,7.58),(1.94,ya+0.17,7.48)],0.005,6)
    # PA horn + CCTV dome (back wall high corners)
    A.bx((g,"STEEL"),-4.55,-4.47,yb,yb+0.11,8.10,8.16,0.003) if False else None
    hx,hz=-4.40,8.20
    A.fb((g,"STEEL"),'+y',yb,hx-0.05,hx+0.05,hz-0.05,hz+0.05,0.03,0.004); A.prism((g,"STEEL_L"),(hx,yb+0.03,hz),(hx,yb+0.24,hz),0.045,0.15,24,0,True,0.003); A.prism((g,"BLACK"),(hx,yb+0.24,hz),(hx,yb+0.245,hz),0.14,0.14,24) 
    A.prism((g,"BLACK"),(hx,yb+0.03,hz),(hx,yb+0.235,hz),0.035,0.13,20,0,False)
    cx_,cz=1.75,8.12
    A.fb((g,"STEEL"),'+y',yb,cx_-0.06,cx_+0.06,cz-0.06,cz+0.06,0.03,0.004); A.prism((g,"STEEL"),(cx_,yb+0.03,cz),(cx_-0.10,yb+0.10,cz-0.02),0.016,0.016,10)
    A.prism((g,"GREY"),(cx_-0.10,yb+0.10,cz-0.02),(cx_-0.19,yb+0.17,cz-0.11),0.075,0.075,24,0,True,0.003); A.prism((g,"BLACK"),(cx_-0.185,yb+0.165,cz-0.105),(cx_-0.20,yb+0.18,cz-0.12),0.05,0.05,24)
    A.prism((g,"LED_RON"),(cx_-0.10,yb+0.13,cz-0.0),(cx_-0.10,yb+0.13,cz+0.0),0.0,0.0,3) if False else None
    A.bx((g,"LED_RON"),cx_-0.115,cx_-0.105,yb+0.09,yb+0.10,cz+0.03,cz+0.04,0.0)
    # outlets / switch plates / thermostat / conduit
    def plate(face,p,l,z,n=2,mk="BEIGE"):
        p=p+(-1 if face in('-x','-y') else 1)*0.027
        A.fb((g,mk),face,p,l-0.04,l+0.04,z-0.06,z+0.06,0.008,0.003)
        for k in range(n): A.fb((g,"BLACK"),face,p+(0.0 if face in('+y','+x') else 0.0),l-0.008+ (k-0.5*(n-1))*0.04,l+0.008+(k-0.5*(n-1))*0.04,z-0.012,z+0.012,0.010,0.0008)
    plate('+y',yb,0.15,5.70); plate('+y',yb,-3.90,5.70); plate('-x',2.0,-10.05,5.70); plate('-x',2.0,-7.75,5.70); plate('-x',2.0,-8.95,6.20); plate('+y',yb,-0.50,5.70,1)
    A.fb((g,"BEIGE"),'-x',2.0,-6.55,-6.42,7.60,7.72,0.02,0.004) if False else None
    A.fb((g,"BEIGE"),'-x',1.98,-11.30,-11.18,7.00,7.12,0.02,0.004); A.fb((g,"LED_ON"),'-x',1.96,-11.27,-11.21,7.06,7.08,0.002,0.0)   # thermostat
    A.fb((g,"STEEL_L"),'-x',2.0,-11.5,-7.30,6.90,6.96,0.028,0.003) if False else None
    A.fb((g,"STEEL_L"),'-x',1.973,-11.45,-9.05,6.48,6.54,0.03,0.003)                                            # raceway between rack, copier and desk
    for k in range(6): A.screw((g,"STEEL"),'-x',1.943,-11.40+k*0.4,6.51,0.005)
    A.prism((g,"STEEL_L"),(1.96,-9.05,6.51),(1.96,-9.05,5.75),0.012,0.012,10)
    A.prism((g,"STEEL_L"),(-4.78,-11.60,8.50),(-4.78,-11.60,6.00),0.011,0.011,10) if False else None
    # window cassette blind (rolled up) and sill items
    A.bx((g,"STEEL_L"),-4.55,1.75,-6.17,-6.11,8.30,8.40,0.004); A.bx((g,"BLACK"),-4.55,1.75,-6.17,-6.12,8.25,8.30,0.002)
    for k in range(3): A.bx((g,"BEIGE_D"),-4.55,1.75,-6.165,-6.13,8.24-k*0.012,8.245-k*0.012,0.0)
    A.tube((g,"CABLE_G"),[(-4.45,-6.15,8.25),(-4.45,-6.15,7.6),(-4.44,-6.15,7.55)],0.003,6)
    A.cyl((g,"BEIGE_D"),-4.44,-6.15,7.5,7.55,0.01,12)
def ceiling_bits(c):
    A=c.A; g="ceilbits"
    for (x,y) in ((-1.8,-9.55),(0.6,-10.9)):                                                                 # smoke detectors
        A.prism((g,"BEIGE"),(x,y,8.47),(x,y,8.50),0.055,0.058,24,0,True,0.002); A.prism((g,"BLACK"),(x,y,8.465),(x,y,8.472),0.03,0.03,16); A.prism((g,"LED_RON"),(x+0.04,y,8.462),(x+0.04,y,8.47),0.004,0.004,8)
    for (x,y) in ((-2.4,-9.0),(-0.6,-11.2),(0.3,-8.4)):                                                       # sprinkler heads
        A.prism((g,"BRASS"),(x,y,8.50),(x,y,8.46),0.014,0.014,12); A.prism((g,"BRASS"),(x,y,8.46),(x,y,8.445),0.022,0.024,14); A.prism((g,"RED"),(x,y,8.445),(x,y,8.44),0.008,0.008,8); A.prism((g,"STEEL_L"),(x,y,8.45),(x,y,8.447),0.032,0.032,16)

