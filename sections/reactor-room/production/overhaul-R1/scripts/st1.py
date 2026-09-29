import bpy,sys,math; sys.path.insert(0,"."); from hs import *
S=sys.argv[sys.argv.index("--")+1]; src=sys.argv[sys.argv.index("--")+2]; dst=sys.argv[sys.argv.index("--")+3]
bpy.ops.wm.open_mainfile(filepath=S+"/"+src); sc=bpy.context.scene
M=mats(); A=K()
def profile(g,face,pw,pf,l0,l1,prof):
    """extrude an (depth-from-wall, z) convex profile across lateral l0..l1"""
    pts=[]
    for (d,z) in prof:
        c=(pw+d*(1 if face=='+x' else -1) if face in('-x','+x') else None)
    sg=(-1 if face in('-x','-y') else 1)
    # d measured from wall plane toward the hall
    P=[]
    for l in (l0,l1):
        for (d,z) in prof:
            c=pw-sg*d
            P.append((c,l,z) if face in('-x','+x') else (l,c,z))
    A.hull((g,"IRON"),P,0.014)
# ============ GRID (east wall, front faces -x) ============
g="grid"; F='-x'; PW=10.66; PF=9.48
for (l0,l1) in ((-0.87,-0.21),(-1.55,-0.89),(-2.23,-1.57)):
    lc=(l0+l1)/2
    A.db((g,"TRIM"),F,PW,PF-0.02,l0-0.015,l1+0.015,0,0.12,0.01)                 # plinth
    A.db((g,"IRON"),F,PW,PF,l0,l1,0.12,2.25)                                     # carcass
    A.fb((g,"ENAM"),F,PF,l0+0.04,l1-0.04,0.22,1.62,0.03,0.008)                    # door panel
    for zc in (0.5,0.95,1.4):
        A.fb((g,"INK"),F,PF-0.03,lc-0.24,lc+0.24,zc-0.19,zc+0.19,0.02,0.004)     # breaker slot
        A.led((g,"STAT"),F,PF-0.03,l1-0.08,zc+0.13)
        A.led((g,"LAMPA"),F,PF-0.03,l0+0.08,zc+0.13)
    A.fb((g,"TRIM"),F,PF,l0+0.04,l1-0.04,1.66,1.86,0.03,0.006)                    # label band
    A.louvre((g,"IRON"),F,PF,l0+0.05,l1-0.05,1.9,2.18,n=5,t=0.03,back=(g,"INK"))
    A.db((g,"IRON"),F,PW,PF-0.05,l0-0.02,l1+0.02,2.25,2.31,0.012)                  # cap
    A.hull((g,"TRIM"),[(PF-0.05,l0+0.05,2.31),(PF-0.05,l1-0.05,2.31),(PF+0.0,l0+0.1,2.36),(PF+0.0,l1-0.1,2.36),(PF+0.3,l0+0.1,2.31),(PF+0.3,l1-0.1,2.31)],0.004) if False else None
    A.led((g,"LAMPA"),F,PF-0.03,lc,2.28,0.05,0.04)                                  # beacon
    for zz in (0.3,1.7,2.05): A.fb((g,"IRON"),F,PF+0.005,l0-0.005,l0+0.012,zz,zz+0.6 if zz<1 else zz+0.25,0.01,0.002)
# demand console
l0,l1=-0.09,1.19
profile(g,F,PW,PF+0.28 if False else 9.75,l0,l1,[(0,0),(0.91,0),(0.91,0.9),(0.24,1.27),(0,1.3)])
A.db((g,"ENAM"),F,PW,PW-0.27,l0,l1,1.2,2.06,0.012)                                  # instrument riser
A.hull((g,"IRON"),[(10.39,l0,2.06),(10.39,l1,2.06),(10.66,l0,2.06),(10.66,l1,2.06),(10.39,l0,2.14),(10.39,l1,2.14),(10.55,l0,2.24),(10.55,l1,2.24)],0.01)
A.fb((g,"TRIM"),F,9.755,l0-0.01,l1+0.01,0.02,0.22,0.02,0.006)                       # kick plate
for zc in (0.5,0.75): A.louvre((g,"IRON"),F,9.75,l0+0.08,l1-0.08,zc-0.13,zc+0.13,n=4,t=0.025,back=(g,"INK"))
for l in (l0,l1): A.bx((g,"IRON"),9.75,10.66,l-0.02 if l==l0 else l,l if l==l0 else l+0.02,0,0.95,0.01)
A.led((g,"STAT"),F,9.75,l0+0.08,0.85,0.03); A.led((g,"LAMPA"),F,9.75,l0+0.18,0.85,0.03)
# ============ BANK CONTROL (north wall, front faces -y) ============
g="bank"; F='-y'; PW=10.70
profile(g,F,PW,9.72,2.78,4.52,[(0,0),(0.98,0),(0.98,0.86),(0.45,1.12),(0,1.16)])
A.db((g,"ENAM"),F,PW,PW-0.28,2.78,4.52,1.1,1.76,0.012)
A.hull((g,"IRON"),[(x,10.28,1.76) for x in (2.78,4.52)]+[(x,10.70,1.76) for x in (2.78,4.52)]+[(x,10.28,1.84) for x in (2.78,4.52)]+[(x,10.55,2.05) for x in (2.78,4.52)],0.01)
A.fb((g,"TRIM"),F,9.725,2.77,4.53,0.02,0.22,0.02,0.006)
for zc in (0.45,0.72): A.louvre((g,"IRON"),F,9.72,2.86,4.44,zc-0.13,zc+0.13,n=5,t=0.025,back=(g,"INK"))
for x in (2.78,4.52): A.bx((g,"IRON"),x-0.02 if x==2.78 else x,x if x==2.78 else x+0.02,9.72,10.7,0,1.0,0.01)
for x in (2.95,3.1,3.25): A.led((g,"STAT"),F,9.72,x,0.86,0.03)
# ============ GENERATOR (west wall, front faces +x) ============
g="gen"; F='+x'; PW=-10.65
A.db((g,"IRON"),F,PW,-8.85,-4.40,-2.85,0,0.28,0.02)                                   # skid
for y in (-4.3,-2.95):
    for x in (-10.5,-9.2): A.bx((g,"TRIM"),x,x+0.14,y,y+0.1,0.28,0.34,0.01)
A.db((g,"OLIVE"),F,PW,-9.0,-4.25,-2.95,0.28,1.85,0.02)                                # engine enclosure
A.hull((g,"IRON"),[(-10.62,-4.28,1.85),(-10.62,-2.92,1.85),(-8.98,-4.28,1.85),(-8.98,-2.92,1.85),(-10.3,-4.15,2.05),(-10.3,-3.05,2.05),(-9.3,-4.15,2.05),(-9.3,-3.05,2.05)],0.012)
A.fb((g,"INK"),F,-9.0,-4.19,-3.01,1.09,1.31,0.02,0.004)                                # legend band (plaque sits here)
A.louvre((g,"IRON"),F,-9.0,-4.15,-3.05,1.4,1.8,n=7,t=0.035,back=(g,"INK"))
A.louvre((g,"IRON"),F,-9.0,-4.15,-3.55,0.4,1.0,n=8,t=0.035,back=(g,"INK"))
A.fb((g,"TRIM"),F,-9.0,-3.5,-3.05,0.42,0.98,0.03,0.008)                               # hatch
A.wheel((g,"TRIM"),-8.96,-3.28,0.7,0.06,'x',3) if False else None
for y in (-4.05,-3.15): A.led((g,"STAT"),F,-9.0,y,1.2,0.03)
A.prism((g,"IRON"),(-10.05,-3.15,2.0),(-10.05,-3.15,2.85),0.19,0.19,8)                # silencer
A.prism((g,"TRIM"),(-10.05,-3.15,2.4),(-10.05,-3.15,2.5),0.22,0.22,8)
A.prism((g,"IRON"),(-10.05,-3.15,2.85),(-10.62,-3.15,2.85),0.11,0.11,8)                # exhaust to wall gland
A.flange((g,"TRIM"),(-10.6,-3.15,2.85),(-10.64,-3.15,2.85),0.11,0.2)
A.prism((g,"ENAM"),(-9.9,-2.95,0.95),(-9.9,-2.45,0.95),0.42,0.42,8)                   # alternator
A.prism((g,"IRON"),(-9.9,-2.45,0.95),(-9.9,-2.40,0.95),0.30,0.30,8)
A.db((g,"IRON"),'+x',-10.62,-9.4,-2.85,-2.45,0.28,0.6,0.01)
# ============ RESERVE POWER A / B ============
def battery(g,l0,l1):
    F='+x'; PW=-10.65; PF=-9.15
    A.db((g,"TRIM"),F,PW,PF+0.02,l0-0.015,l1+0.015,0,0.12,0.01)
    A.db((g,"IRON"),F,PW,PF,l0,l1,0.12,1.79)
    A.fb((g,"OLIVE"),F,PF,l0+0.04,l1-0.04,0.2,0.78,0.03,0.008)
    n=max(2,int((l1-l0)/0.36))
    for i in range(n):
        a=l0+0.06+i*(l1-l0-0.12)/n; b=a+(l1-l0-0.12)/n-0.03
        for z in (0.24,0.5):
            A.fb((g,"INK"),F,PF+0.03,a,b,z,z+0.2,0.02,0.004); A.led((g,"STAT" if (i+int(z*10))%3 else "LAMPA"),F,PF+0.03,(a+b)/2,z+0.1,0.02)
    A.fb((g,"TRIM"),F,PF,l0+0.04,l1-0.04,0.82,0.98,0.03,0.006)
    A.louvre((g,"IRON"),F,PF,l0+0.05,l1-0.05,1.75-0.02,1.79,n=1,t=0.01) if False else None
    A.db((g,"IRON"),F,PW,PF-0.06,l0-0.02,l1+0.02,1.79,1.85,0.012)
    A.hull((g,"TRIM"),[(-10.62,l0+0.05,1.85),(-10.62,l1-0.05,1.85),(-9.3,l0+0.05,1.85),(-9.3,l1-0.05,1.85),(-10.5,l0+0.12,2.02),(-10.5,l1-0.12,2.02),(-9.4,l0+0.12,2.02),(-9.4,l1-0.12,2.02)],0.01)
battery("resA",2.75,4.25); battery("resB",-5.5,-4.5)
objs=A.build("28 R2 HERO STATIONS","R2 hero",M)
for o in objs:
    for p in o.data.polygons: p.use_smooth=False
print("objs",len(objs),"tris",sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objs))
bpy.ops.wm.save_as_mainfile(filepath=S+"/"+dst)
