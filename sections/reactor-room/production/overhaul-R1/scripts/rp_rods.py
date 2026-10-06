"""Reactor pool centrepiece pass: control-rod banks A and B (turned rod columns with collars, tip, sleeve stem, crosshead carriage, guide shoe, rod bands) and their fixed drive
housings (machined housings with corner posts, cooling fins, louvres, access hatch, pressure gauge, cable glands, lifting lugs), plus a fuel-assembly lattice on the pool floor.
usage: python rp_rods.py -- <in.blend> <out.blend>      (run after the control-room pipeline; touches only collections 03 POOL AND RAIL and 04 BANK MECHANISMS)
Contract objects keep their NAMES, parents and pivots: BANK_A_MOVING / BANK_B_MOVING (empties, the runtime moves them), BANK_x_DRIVE_COLUMN, BANK_x_CARRIAGE, BANK_x_FIXED_HOUSING get new
geometry in place (same bounding box, same materials), so anything bound to them keeps working.  The glowing state bands and state rings keep their driver-fed material (R2 state glow).
New detail is added as RP objects, parented to the moving empty where it moves.  Both banks are identical and level: B's rest height and keyframes are copied from A (they used to be 7.4 vs 8.4 m and out of phase).  Nothing here is time-driven; the motion stays with the runtime."""
import bpy,sys,os,math,collections
import numpy as np
from mathutils import Vector
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import crk
A=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A[0],A[1]
bpy.ops.wm.open_mainfile(filepath=SRC)
def bank_channels(ob):
    ad=ob.animation_data; act=ad.action if ad else None
    return [f for l in act.layers for st in l.strips for cb in st.channelbags for f in cb.fcurves] if act else []
# ---- symmetry: bank B used to rest 1 m lower than A and its demo animation ran out of phase (A 8.4 / B 7.4 m).  Both banks now rest at A's height and share A's keyframes, so they always move together.
_a=bpy.data.objects["BANK_A_MOVING"]; _b=bpy.data.objects["BANK_B_MOVING"]; _fa=[f for f in bank_channels(_a) if f.data_path=="location" and f.array_index==2]; _fb=[f for f in bank_channels(_b) if f.data_path=="location" and f.array_index==2]
if _fa and _fb:
    for ka,kb in zip(_fa[0].keyframe_points,_fb[0].keyframe_points):
        kb.co[1]=ka.co[1]; kb.handle_left[1]=ka.handle_left[1]; kb.handle_right[1]=ka.handle_right[1]
_b.location.z=_a.location.z; bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
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
    """one control-rod bank as a real rod-cluster control assembly, identical for A and B (radially symmetric about the rod axis x,0): handle (stem), spider hub with 8 vanes, top plate (carriage),
    17-rod absorber cage (16 pins + central drive tube) with spacer grids, glowing grid rings and glowing pin tips, end plate and nose; housing with four identical sides"""
    piv=bpy.data.objects["BANK_%s_MOVING"%tag]; col=bpy.data.objects["BANK_%s_DRIVE_COLUMN"%tag]; car=bpy.data.objects["BANK_%s_CARRIAGE"%tag]; hou=bpy.data.objects["BANK_%s_FIXED_HOUSING"%tag]
    def find(sub): return next(o for o in bpy.data.objects if o.name.startswith("R2 bank %s "%tag) and sub in o.name)
    RING=[(0.0,k*math.pi/4) for k in range(0)]
    # ---- central drive tube (the contract DRIVE_COLUMN): slim collared tube from the plate down to the end plate
    prof=[(0.0,pz-13.4),(0.105,pz-13.4)]; z=pz-12.8
    while z<pz-0.5:
        prof+=[(0.105,z-0.05),(0.135,z-0.03),(0.135,z+0.03),(0.105,z+0.05)]; z+=1.5
    prof+=[(0.105,pz-0.30),(0.0,pz-0.30)]
    K=crk.Kit(); K.lathe(("rp","IRON"),x,0.0,prof,seg=20); swap(col,K,"IRON")
    # ---- 16 absorber pins: 8 on the outer ring (r 0.40, under the vane tips), 8 on the inner ring (r 0.28, between them); polished, with glowing tips
    K=crk.Kit(); G=crk.Kit()
    for k in range(8):
        for r,off in ((0.40,0.0),(0.28,math.pi/8)):
            th=k*math.pi/4+off; px,py=x+r*math.cos(th),r*math.sin(th)
            K.cyl(("rp","CHROME"),px,py,pz-13.28,pz-0.30,0.026,6,0.0)
            K.lathe(("rp","CHROME"),px,py,[(0.026,pz-13.28),(0.026,pz-13.33),(0.014,pz-13.36),(0.0,pz-13.37)],seg=6)
            G.lathe(("rp","GLOW"),px,py,[(0.0,pz-13.43),(0.034,pz-13.41),(0.040,pz-13.36),(0.034,pz-13.31),(0.0,pz-13.29)],seg=8)
    attach(K.build(BANKC,"RP bank %s absorber pins"%tag,M),piv); attach(G.build(BANKC,"RP bank %s pin tips"%tag,M),piv)
    for o in [o for o in bpy.data.objects if o.name.startswith("R2 bank %s moving bank %s carriage plate"%(tag,tag))]: bpy.data.objects.remove(o,do_unlink=True)   # the old flat plate on the old crosshead
    # ---- end plate + nose (the contract rod tip)
    tip=find("rod tip"); K=crk.Kit()
    K.lathe(("rp","IRON"),x,0.0,[(0.0,pz-13.62),(0.09,pz-13.60),(0.16,pz-13.54),(0.20,pz-13.47),(0.46,pz-13.47),(0.48,pz-13.45),(0.48,pz-13.40),(0.0,pz-13.40)],seg=24)
    swap(tip,K,"IRON")
    # ---- spacer grids at the old TRIM band heights (egg-crate: outer frame + 8 spokes), glowing rings at the old GLOW band heights
    def levels(sub):
        L=z_levels(find(sub)); out=[]
        for i in range(0,len(L)-1,2):
            if L[i+1]-L[i]<=0.6: out.append((L[i],L[i+1]))
        return out
    K=crk.Kit()
    for (z0,z1) in levels("rod band TRIM"):
        K.lathe(("rp","IRON"),x,0.0,[(0.455,z0),(0.48,z0+0.02),(0.48,z1-0.02),(0.455,z1)],seg=24); K.lathe(("rp","IRON"),x,0.0,[(0.425,z0),(0.455,z0),(0.455,z1),(0.425,z1)],seg=24)
        for k in range(8):
            th=k*math.pi/4+math.pi/8; K.box(("rp","IRON"),x+0.27*math.cos(th),0.27*math.sin(th),z0+0.02,z1-0.02,0.34,0.03,th,0.0)
    swap(find("rod band TRIM"),K,"IRON")
    K=crk.Kit()
    for (z0,z1) in levels("rod band GLOW"):
        zc=(z0+z1)/2; K.lathe(("rp","IRON"),x,0.0,[(0.425,zc-0.07),(0.47,zc-0.05),(0.485,zc-0.03),(0.485,zc+0.03),(0.47,zc+0.05),(0.425,zc+0.07)],seg=24)
    swap(find("rod band GLOW"),K,"IRON")
    # ---- spider hub + 8 vanes (the contract guide shoe), top plate (the contract carriage), handle (the contract stem)
    shoe=find("guide shoe"); K=crk.Kit()
    K.lathe(("rp","IRON"),x,0.0,[(0.0,pz-0.12),(0.30,pz-0.12),(0.30,pz-0.04),(0.22,pz+0.08),(0.17,pz+0.30),(0.20,pz+0.50),(0.22,pz+0.56),(0.0,pz+0.56)],seg=24)
    t=0.04
    for k in range(8):
        th=k*math.pi/4; c,sn=math.cos(th),math.sin(th); pts=[]
        for rr,w0,w1 in ((0.20,-0.12,0.42),(0.43,-0.12,0.10)):
            for dt in (-t/2,t/2):
                for w in (w0,w1): pts.append((x+rr*c-dt*sn,rr*sn+dt*c,pz+w))
        K.hull(("rp","IRON"),pts,0.004)
        K.cyl(("rp","IRON"),x+0.43*c,0.43*sn,pz-0.14,pz+0.12,0.045,8,0.0)            # vane-tip post
    swap(shoe,K,"IRON")
    cb=crk.Kit(); cb.pillow(("rp","ENAM"),x-0.47,x+0.47,-0.47,0.47,pz-0.32,pz-0.14,0.035,1); swap(car,cb,"ENAM")
    stem=find("stem"); prof=[(0.0,pz+0.50),(0.24,pz+0.50)]; z=pz+0.85
    while z<pz+3.0:
        prof+=[(0.21,z-0.05),(0.24,z-0.03),(0.24,z+0.03),(0.21,z+0.05)]; z+=0.35
    prof+=[(0.24,pz+3.02),(0.30,pz+3.04),(0.30,pz+3.10),(0.20,pz+3.10),(0.0,pz+3.10)]
    K=crk.Kit(); K.lathe(("rp","IRON"),x,0.0,prof,seg=24); swap(stem,K,"IRON")
    # ---- glow on the assembly: vane-edge strips, top-plate corner lamps
    K=crk.Kit()
    for k in range(8):
        th=k*math.pi/4; c,sn=math.cos(th),math.sin(th); K.box(("rp","GLOW"),x+0.435*c,0.435*sn,pz-0.10,pz+0.08,0.025,0.055,th,0.002)
    for sx in (-1,1):
        for sy in (-1,1): K.cyl(("rp","GLOW"),x+sx*0.41,sy*0.41,pz-0.14,pz-0.10,0.035,10,0.0)
    attach(K.build(BANKC,"RP bank %s spider glow"%tag,M),piv)
    # ---- fixed housing: four identical sides (fins above and below a lamp-and-gauge panel), corner posts, roof crown, hazard skirt, corner cable glands
    hb=crk.Kit(); hb.pillow(("rp","IRON"),x-0.88,x+0.88,-0.88,0.88,9.70,12.62,0.035,1); swap(hou,hb,"IRON")
    K=crk.Kit()
    for sx in (-1,1):
        for sy in (-1,1): K.bx(("rp","TRIM"),x+sx*0.88-0.06,x+sx*0.88+0.06,sy*0.88-0.06,sy*0.88+0.06,9.70,12.62,0.012)
    for face in range(4):
        th=face*math.pi/2; c,sn=math.cos(th),math.sin(th)                         # outward normal (c,sn), tangent (-sn,c)
        def P(r,tt,z): return (x+r*c-tt*sn,r*sn+tt*c,z)
        for k in range(4):                                                        # cooling fins above and below the panel
            for zb in (10.00+k*0.18,11.98+k*0.18): K.box(("rp","GUN"),x+0.905*c,0.905*sn,zb,zb+0.075,0.05,1.10,th,0.008)
        if face==3: continue                                                      # the front face already carries the face plate and the bank letter
        K.box(("rp","GUN"),x+0.895*c,0.895*sn,10.92,11.93,0.03,1.10,th,0.006)     # instrument panel
        for tt in (-0.38,0.0,0.38):                                               # three glowing lamps
            K.prism(("rp","GLOW"),P(0.905,tt,11.72),P(0.935,tt,11.72),0.040,0.040,12,0.0,True,0.0)
        K.prism(("rp","BRASS"),P(0.905,0.0,11.28),P(0.925,0.0,11.28),0.15,0.15,28,0.0,True,0.003); K.prism(("rp","WHITE"),P(0.925,0.0,11.28),P(0.929,0.0,11.28),0.125,0.125,28,0.0,True,0.0)
        for kk in range(11):
            ang=math.radians(-120+kk*24); r0,r1=0.085,0.115 if kk%5==0 else 0.105
            K.tube(("rp","BLK"),[P(0.9295,-math.sin(ang)*r0,11.28+math.cos(ang)*r0),P(0.9295,-math.sin(ang)*r1,11.28+math.cos(ang)*r1)],0.0028,4)
        K.tube(("rp","RED"),[P(0.930,0.0,11.28),P(0.930,-0.07,11.28+0.055)],0.0045,4)
    for face in range(4):                                                         # hazard skirt strip on every side
        th=face*math.pi/2; c,sn=math.cos(th),math.sin(th)
        K.box(("rp","HAZ"),x+0.885*c,0.885*sn,9.70,9.80,0.03,1.76,th,0.004)
    for sx in (-1,1):                                                             # cable glands at the four roof corners, cables up to the gantry
        for sy in (-1,1):
            gx,gy=x+sx*0.70,sy*0.70; K.cyl(("rp","GUN"),gx,gy,12.62,12.76,0.05,10,0.0)
            K.tube(("rp","BLK"),[(gx,gy,12.74),(gx,gy,13.0),(gx+sx*0.12,gy+sy*0.12,13.4),(gx+sx*0.30,gy+sy*0.30,13.8)],0.022,8)
    K.lathe(("rp","GUN"),x,0.0,[(0.60,12.62),(0.60,12.69),(0.46,12.76),(0.30,12.76),(0.30,12.92),(0.22,12.98),(0.0,12.98)],seg=24)   # roof crown
    for k in range(8):
        th=k*math.pi/4; K.prism(("rp","BRASS"),(x+0.52*math.cos(th),0.52*math.sin(th),12.69),(x+0.52*math.cos(th),0.52*math.sin(th),12.735),0.03,0.03,6,0.0,True,0.0)
    attach(K.build(BANKC,"RP bank %s housing detail"%tag,M),None)
bank("A",-1.4,_a.location.z); bank("B",1.4,_b.location.z)
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
