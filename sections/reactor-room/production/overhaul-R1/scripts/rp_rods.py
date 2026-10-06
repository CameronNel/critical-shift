"""Reactor pool centrepiece pass: control-rod banks A and B (turned rod columns with collars, tip, sleeve stem, crosshead carriage, guide shoe, rod bands) and their fixed drive
housings (machined housings with corner posts, cooling fins, louvres, access hatch, pressure gauge, cable glands, lifting lugs), plus a fuel-assembly lattice on the pool floor.
usage: python rp_rods.py -- <in.blend> <out.blend>      (run after the control-room pipeline; touches only collections 03 POOL AND RAIL and 04 BANK MECHANISMS)
Contract objects keep their NAMES, parents and pivots: BANK_A_MOVING / BANK_B_MOVING (empties, the runtime moves them), BANK_x_DRIVE_COLUMN, BANK_x_CARRIAGE, BANK_x_FIXED_HOUSING get new
geometry in place (same bounding box, same materials), so anything bound to them keeps working.  The glowing state bands and state rings keep their driver-fed material (R2 state glow).
New detail is added as RP objects, parented to the moving empty where it moves.  Nothing here is time-driven; the motion stays with the runtime."""
import bpy,sys,os,math,collections
import numpy as np
from mathutils import Vector
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import crk
A=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A[0],A[1]
bpy.ops.wm.open_mainfile(filepath=SRC)
def mat(n): return bpy.data.materials[n]
M=dict(IRON=mat("R2 iron"),ENAM=mat("R2 bank enamel"),TRIM=mat("R2 trim rust"),GLOW=mat("R2 state glow"))
M["CHROME"]=crk.pm("RP chrome rod",(0.60,0.63,0.64),0.16,metal=1.0,scale=3.0,bump=0.0,var=(0.90,1.04),edge=(0.9,0.92,0.92))
M["BRASS"]=crk.pm("RP brass",(0.50,0.34,0.10),0.28,metal=0.95,scale=3.0,bump=0.0,var=(0.88,1.06))
M["GUN"]=crk.pm("RP gunmetal",(0.045,0.055,0.058),0.34,metal=0.8,scale=2.5,bump=0.0,edge=(0.30,0.32,0.32))
M["HAZ"]=crk.pm("RP hazard yellow",(0.62,0.42,0.03),0.45,edge=(0.85,0.62,0.10),scale=2.0,bump=0.02)
M["BLK"]=crk.pm("RP black rubber",(0.014,0.015,0.016),0.8,scale=3.0,bump=0.05)
M["WHITE"]=crk.pm("RP gauge white",(0.62,0.62,0.56),0.5,scale=2.0,bump=0.0)
M["RED"]=crk.pm("RP signal red",(0.34,0.022,0.015),0.4,edge=(0.6,0.1,0.06),scale=2.0,bump=0.02)
POOLC=bpy.data.collections["03 POOL AND RAIL"]; BANKC=bpy.data.collections["04 BANK MECHANISMS"]
def swap(target,K,key):
    """give an existing object new geometry (built in world coordinates in K under ('rp',key)); the object keeps name, parent, pivot and material"""
    coll=target.users_collection[0]; objs=K.build(coll,"RPT",{key:target.data.materials[0]})
    t=objs[0]; me=t.data; me.transform(target.matrix_world.inverted()); old=target.data; target.data=me
    bpy.data.objects.remove(t); bpy.data.meshes.remove(old); me.name=target.name
def attach(objs,parent=None,prefix="RP"):
    for o in objs:
        if parent: o.parent=parent; o.matrix_parent_inverse=parent.matrix_world.inverted()
def z_levels(o):
    zs=sorted({round((o.matrix_world@v.co).z,3) for v in o.data.vertices}); out=[]
    for z in zs:
        if out and z-out[-1][-1]<0.03: out[-1].append(z)
        else: out.append([z])
    return [sum(g)/len(g) for g in out]
tris0=sum(len(p.vertices)-2 for c in (POOLC,BANKC) for o in c.all_objects if o.type=='MESH' for p in o.data.polygons)
def bank(tag,x,pz):
    piv=bpy.data.objects["BANK_%s_MOVING"%tag]; col=bpy.data.objects["BANK_%s_DRIVE_COLUMN"%tag]; car=bpy.data.objects["BANK_%s_CARRIAGE"%tag]; hou=bpy.data.objects["BANK_%s_FIXED_HOUSING"%tag]
    def find(sub): return next(o for o in bpy.data.objects if o.name.startswith("R2 bank %s "%tag) and sub in o.name)
    # ---- turned drive column: collars every 1.25 m, chamfered
    prof=[(0.0,-5.0),(0.165,-5.0)]
    z=-4.4
    while z<7.6:
        prof+= [(0.165,z-0.075),(0.205,z-0.045),(0.205,z+0.045),(0.165,z+0.075)]; z+=1.25
    prof+=[(0.165,7.75),(0.0,7.75)]
    K=crk.Kit(); K.lathe(("rp","IRON"),x,0.0,prof,seg=24)
    swap(col,K,"IRON")
    # polished stripes between the collars (chrome sleeves)
    K=crk.Kit(); z=-3.775
    while z<7.5:
        K.lathe(("rp","CHROME"),x,0.0,[(0.172,z+0.02),(0.176,z+0.04),(0.176,z+0.98),(0.172,z+1.0)],seg=24); z+=1.25
    attach(K.build(BANKC,"RP bank %s rod sleeves"%tag,M),piv)
    # ---- rod tip: bullet nose
    tip=find("rod tip")
    K=crk.Kit(); K.lathe(("rp","IRON"),x,0.0,[(0.0,-5.27),(0.10,-5.255),(0.19,-5.20),(0.25,-5.11),(0.27,-5.03),(0.27,-5.0)],seg=24); swap(tip,K,"IRON")
    # ---- state bands: turned rings at the same heights
    for sub in ("rod band GLOW","rod band TRIM"):
        b=find(sub); L=z_levels(b); K=crk.Kit()
        for i in range(0,len(L)-1,2):
            z0,z1=L[i],L[i+1]
            if z1-z0>0.6: continue
            K.lathe(("rp","IRON"),x,0.0,[(0.18,z0),(0.222,z0+0.025),(0.222,z1-0.025),(0.18,z1)],seg=24)
        if K.bm: swap(b,K,"IRON")
    # ---- stem: ribbed sleeve between carriage and housing
    stem=find("stem"); prof=[(0.0,9.05),(0.30,9.05),(0.30,9.12)]; z=9.30
    while z<11.4:
        prof+=[(0.26,z-0.05),(0.30,z-0.03),(0.30,z+0.03),(0.26,z+0.05)]; z+=0.30
    prof+=[(0.30,11.4),(0.30,11.5),(0.0,11.5)]
    for i,(r,zz) in enumerate(prof): prof[i]=(r,zz-8.4+pz)
    K=crk.Kit(); K.lathe(("rp","IRON"),x,0.0,prof,seg=24); swap(stem,K,"IRON")
    # ---- guide shoe: clamp block with two arms and vertical rollers
    shoe=find("guide shoe"); K=crk.Kit(); c0=pz-0.45
    K.pillow(("rp","IRON"),x-0.30,x+0.30,-0.36,0.36,c0+0.12,c0+0.78,0.03,1)
    for s in (-1,1):
        K.pillow(("rp","IRON"),x-0.20,x+0.20,0.30*s if s>0 else -0.70,0.70 if s>0 else -0.30,c0+0.28,c0+0.62,0.04,2)
        K.lathe(("rp","IRON"),x,0.66*s,[(0.0,c0+0.18),(0.13,c0+0.18),(0.14,c0+0.21),(0.14,c0+0.69),(0.13,c0+0.72),(0.0,c0+0.72)],seg=18)
    swap(shoe,K,"IRON")
    # ---- carriage: crosshead block (same box), then detail
    cb=crk.Kit(); cb.pillow(("rp","ENAM"),x-0.72,x+0.72,-0.52,0.52,pz-0.65,pz+0.65,0.035,1); swap(car,cb,"ENAM")
    K=crk.Kit()
    for sx in (-1,1):                                                   # side flanges with hex bolts, vertical hazard stripes, rubber bumpers
        xs=x+sx*0.72
        K.fb(("rp","GUN"),'+x' if sx>0 else '-x',xs,-0.40,0.40,pz-0.55,pz+0.55,0.035,0.01)
        for k in range(3): K.fb(("rp","HAZ"),'+x' if sx>0 else '-x',xs+0.035*sx,-0.36+k*0.30,-0.28+k*0.30,pz-0.45,pz+0.45,0.008,0.002)
        for yy in (-0.30,0.30):
            for zz in (pz-0.48,pz+0.48): K.prism(("rp","BRASS"),(xs+0.035*sx,yy,zz),(xs+0.05*sx,yy,zz),0.028,0.028,6,0.0,True,0.0)
    for k in range(6): K.fb(("rp","GUN"),'+y',0.52,x-0.55,x+0.55,pz-0.45+k*0.14,pz-0.40+k*0.14,0.03,0.004)   # louvres on the back face
    for sx in (-0.45,0.45):                                              # lifting eyes on top
        K.tube(("rp","IRON"),[(x+sx+0.07*math.cos(t),0.0+0.0,pz+0.65+0.045+0.07*math.sin(t)) for t in np.linspace(0,2*math.pi,13)],0.016,6)
    for k in range(3):                                                   # status lamps on the front face above the plate
        K.cyly(("rp","GLOW"),x-0.28+k*0.28,-0.52,-0.545,pz+0.43,0.045,14,0.0); K.cyly(("rp","GUN"),x-0.28+k*0.28,-0.52,-0.535,pz+0.43,0.062,14,0.0)
    attach(K.build(BANKC,"RP bank %s carriage detail"%tag,M),piv)
    # ---- fixed housing: pillow body, corner posts, fins, hatch, gauge, glands, lugs
    hb=crk.Kit(); hb.pillow(("rp","IRON"),x-0.88,x+0.88,-0.88,0.88,9.70,12.62,0.035,1); swap(hou,hb,"IRON")
    K=crk.Kit()
    for sx in (-1,1):
        for sy in (-1,1): K.bx(("rp","TRIM"),x+sx*0.88-0.06,x+sx*0.88+0.06,sy*0.88-0.06,sy*0.88+0.06,9.70,12.62,0.012)   # corner posts
    for k in range(9):                                                   # cooling fins on the outer side (away from the other bank)
        so=-1 if x<0 else 1; xo=x+so*0.88
        K.fb(("rp","GUN"),'+x' if so>0 else '-x',xo,-0.62,0.62,10.15+k*0.24,10.15+k*0.24+0.085,0.07,0.01)
    K.fb(("rp","GUN"),'+y',0.88,x-0.55,x+0.55,10.1,12.2,0.025,0.01)       # access hatch on the back face with hinges, handle and bolts
    for zz in (10.35,11.95): K.cylx(("rp","IRON"),x-0.60,x-0.52,0.915,zz,0.035,10,0.0)
    K.fb(("rp","BRASS"),'+y',0.905,x+0.30,x+0.44,11.0,11.30,0.03,0.006)
    for xx in (x-0.45,x+0.45):
        for zz in (10.2,12.1): K.prism(("rp","BRASS"),(xx,0.905,zz),(xx,0.93,zz),0.03,0.03,6,0.0,True,0.0)
    gx,gz=x-0.05,11.15; gy=0.95                                          # pressure gauge on the hatch
    K.cyly(("rp","BRASS"),gx,0.905,0.94,gz,0.14,28,0.004); K.cyly(("rp","WHITE"),gx,0.94,0.944,gz,0.115,28,0.0)
    for k in range(11):
        th=math.radians(-120+k*24); r0,r1=0.085,0.108 if k%5==0 else 0.100
        K.tube(("rp","BLK"),[(gx-math.sin(th)*r0,0.9445,gz+math.cos(th)*r0),(gx-math.sin(th)*r1,0.9445,gz+math.cos(th)*r1)],0.0025,4)
    K.tube(("rp","RED"),[(gx,0.9455,gz),(gx-0.065,0.9455,gz+0.05)],0.004,4)
    for (xx,yy) in ((x-0.35,0.6),(x-0.15,-0.6),(x+0.15,0.6),(x+0.35,-0.6)): K.cyl(("rp","GUN"),xx,yy,12.62,12.76,0.05,10,0.0)   # cable glands
    for (xx,yy,dx) in ((x-0.35,0.6,-0.25),(x+0.35,-0.6,0.25)):
        K.tube(("rp","BLK"),[(xx,yy,12.74),(xx,yy,13.0),(xx+dx*0.3,yy+0.0,13.35),(xx+dx,yy*0.6,13.75)],0.022,8)
    for sx in (-0.5,0.5):                                                # lifting lugs on the roof
        K.tube(("rp","IRON"),[(x+sx,0.0+0.075*math.cos(t),12.62+0.045+0.075*math.sin(t)) for t in np.linspace(0,2*math.pi,13)],0.018,6)
        K.cyl(("rp","GUN"),x+sx,0.0,12.62,12.665,0.07,12,0.0)
    K.bx(("rp","HAZ"),x-0.88,x+0.88,-0.88,-0.855,9.70,9.80,0.003); K.bx(("rp","HAZ"),x-0.88,x+0.88,0.855,0.88,9.70,9.80,0.003)   # hazard skirt strips
    attach(K.build(BANKC,"RP bank %s housing detail"%tag,M),None)
bank("A",-1.4,8.4); bank("B",1.4,7.4)
# ---- fuel-assembly lattice on the pool floor (under the water): 8 bundles around the rod tips, caps tinted by the shared state glow
K=crk.Kit(); zf=-6.18
for xx in (-2.05,-0.75,0.75,2.05):
    for yy in (-0.45,0.45):
        K.pillow(("rp","GUN"),xx-0.17,xx+0.17,yy-0.17,yy+0.17,zf,zf+0.95,0.03,2)
        for ii in range(4):
            for jj in range(4): K.cyl(("rp","CHROME"),xx-0.105+ii*0.07,yy-0.105+jj*0.07,zf+0.95,zf+1.04,0.011,6,0.0)
        K.lathe(("rp","GLOW"),xx,yy,[(0.07,zf+1.04),(0.07,zf+1.10),(0.045,zf+1.13),(0.0,zf+1.13)],seg=12)
        for sx in (-1,1): K.bx(("rp","BRASS"),xx+sx*0.17-(0.01 if sx>0 else 0.0),xx+sx*0.17+(0.0 if sx>0 else 0.01),yy-0.10,yy+0.10,zf+0.2,zf+0.8,0.002)
fl=K.build(POOLC,"RP fuel lattice",M)
tris1=sum(len(p.vertices)-2 for c in (POOLC,BANKC) for o in c.all_objects if o.type=='MESH' for p in o.data.polygons)
print("rp_rods: triangles in 03+04 %d -> %d"%(tris0,tris1))
bpy.ops.wm.save_as_mainfile(filepath=DST)
