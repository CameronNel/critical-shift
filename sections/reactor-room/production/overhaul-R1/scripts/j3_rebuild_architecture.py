import bpy,sys,math,re,collections; sys.path.insert(0,"."); from r2lib import *
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w18.blend"); sc=bpy.context.scene
# ---- 1. delete legacy architecture / services (doors' leaves and animated things are kept)
LEGACY=("01 ARCHITECTURE","15 REMAINING HALL WALLS","14 H01 WALL REFERENCE PASS","16 ANNEX WALL FINISH","09 AUTHORED FINISH","10 CONNECTED STRUCTURE AND SERVICES","06 UTILITIES","11 FLOOR SERVICE DETAILS","12 A05 HALL GRAPHICS","QA FLOOR MACHINE LABELS")
n=0
for o in list(bpy.data.objects):
    cn=o.users_collection[0].name if o.users_collection else ""
    if cn not in LEGACY: continue
    if (o.animation_data and o.animation_data.action): continue
    bpy.data.objects.remove(o,do_unlink=True); n+=1
print("legacy objects removed:",n)
# ---- 2. materials
M={}
M["WALL_L"]=r2mat("R2 wall plum lower",(0.078,0.030,0.072),0.62,edge=(0.22,0.10,0.22),grime=0.45,noise=(1.6,0),mottle=0.6)
M["WALL_U"]=r2mat("R2 wall plum upper",(0.050,0.022,0.062),0.68,edge=(0.14,0.08,0.20),grime=0.30,noise=(1.2,0),mottle=0.6)
M["INSET"] =r2mat("R2 wall inset",(0.092,0.036,0.088),0.55,edge=(0.26,0.12,0.26),grime=0.4,noise=(2.0,0),mottle=0.7)
M["DADO"]  =r2mat("R2 dado navy",(0.012,0.022,0.078),0.48,edge=(0.06,0.10,0.28),grime=0.8,noise=(1.8,0),mottle=0.5)
M["IRON"]  =r2mat("R2 iron",(0.022,0.020,0.034),0.42,edge=(0.60,0.17,0.03),grime=0.6,noise=(1.4,0),metal=0.35,mottle=0.5)
M["TRIM"]  =r2mat("R2 trim rust",(0.38,0.09,0.012),0.5,edge=(0.85,0.32,0.07),grime=0.3,noise=(2.5,0),mottle=0.4)
M["FLOOR"] =r2mat("R2 floor tile",(0.060,0.036,0.036),0.26,edge=None,grime=0.10,noise=(1.1,0),tile=(1.2,(0.036,0.032,0.052)),mottle=0.5)
M["BACK"]  =r2mat("R2 backing",(0.012,0.010,0.016),0.8,edge=None,grime=0.0,noise=(1,0),mottle=0.0)
gl=bpy.data.materials.new("R2 clerestory"); gl.use_nodes=True; b=gl.node_tree.nodes["Principled BSDF"]; b.inputs['Base Color'].default_value=(0.02,0.02,0.06,1); b.inputs['Emission Color'].default_value=(0.32,0.26,0.75,1); b.inputs['Emission Strength'].default_value=0.6; b.inputs['Roughness'].default_value=0.2; M["CLERE"]=gl
M["DOOR"]=r2mat("R2 door steel",(0.070,0.020,0.020),0.4,edge=(0.62,0.18,0.03),grime=0.5,noise=(2.0,0),metal=0.3,mottle=0.6)
M["DOORP"]=r2mat("R2 door panel",(0.040,0.012,0.016),0.5,edge=(0.45,0.12,0.02),grime=0.6,noise=(3.0,0),metal=0.2,mottle=0.7)
lm=bpy.data.materials.new("R2 status lamp"); lm.use_nodes=True; b=lm.node_tree.nodes["Principled BSDF"]; b.inputs['Base Color'].default_value=(0.6,0.05,0.02,1); b.inputs['Emission Color'].default_value=(1.0,0.10,0.04,1); b.inputs['Emission Strength'].default_value=6.0; M["LAMP"]=lm
tm=bpy.data.materials.new("R2 sign text"); tm.use_nodes=True; b=tm.node_tree.nodes["Principled BSDF"]; b.inputs['Base Color'].default_value=(0.02,0.01,0.01,1); b.inputs['Emission Color'].default_value=(1.0,0.55,0.20,1); b.inputs['Emission Strength'].default_value=2.2; M["TEXT"]=tm
# ---- 3. architecture
A=Acc(); H=15.0
OPEN={1:(3.395,2.8),4:(6.0,2.8),6:(6.0,3.0)}       # wall index -> (centre s, clear half width): COOLING PLANT, FUEL HANDLING, MAIN ACCESS
DOORH=5.0
def bays(w):
    cols=[0.0]+([3.0,6.0,9.0] if w.L>10 else [w.L/2])+[w.L]
    return cols
def door_ranges(w):
    if w.i in OPEN: c,h=OPEN[w.i]; return (c-h,c+h)
    return None
def spans(u0,u1,w,below_door):
    """split [u0,u1] around the door opening if this tier is below door height"""
    dr=door_ranges(w)
    if not(dr and below_door): return [(u0,u1)]
    out=[]
    if u0<dr[0]: out.append((u0,min(u1,dr[0])))
    if u1>dr[1]: out.append((max(u0,dr[1]),u1))
    return [s for s in out if s[1]-s[0]>0.05]
def cut_cols(w):
    dr=door_ranges(w); cs=bays(w)
    return [c for c in cs[1:-1] if not(dr and dr[0]-0.3<c<dr[1]+0.3)]
TIERS=[("plinth",0,0.35,0.16,"IRON",0.02,True),("dado",0.35,1.25,0.07,"DADO",0.015,True),("rail",1.25,1.38,0.11,"TRIM",0.012,True),
       ("lower",1.38,DOORH,0.05,"WALL_L",0.02,True),("band",DOORH,5.7,0.13,"IRON",0.02,False),("upper1",5.7,9.6,0.04,"WALL_U",0.02,False),("upper2",9.6,13.5,0.04,"WALL_U",0.02,False)]
for w in WALLS:
    for (a,b) in spans(0,w.L,w,True): A.wbox((f"w{w.i} back","BACK"),w,a,b,0,DOORH,-0.4,0,ch=0,gap=0)
    A.wbox((f"w{w.i} back","BACK"),w,0,w.L,DOORH,H,-0.4,0,ch=0,gap=0)
    cs=cut_cols(w); edges=[0.0]+[c for c in bays(w)[1:-1]]+[w.L]
    for i in range(len(edges)-1):
        u0=edges[i]+(0.35 if i==0 else 0.24); u1=edges[i+1]-(0.35 if i==len(edges)-2 else 0.24)
        if edges[i] in [c for c in bays(w)[1:-1] if c not in cs]: u0=edges[i]+0.0   # column omitted (door) -> panel runs to jamb
        for (nm,h0,h1,d1,mk,ch,below) in TIERS:
            for (a,b) in spans(u0,u1,w,below):
                # split long spans into ~1.5 m panels for lower tiers
                pw=1.5 if nm in("plinth","dado","rail","lower") else 3.0
                k=max(1,round((b-a)/pw)); 
                for j in range(k):
                    ua=a+(b-a)*j/k; ub=a+(b-a)*(j+1)/k
                    A.wbox((f"w{w.i} {nm}",mk),w,ua,ub,h0,h1,0,d1,ch)
                    if nm in("lower","upper1","upper2") and ub-ua>1.0 and h1-h0>1.0:
                        A.wbox((f"w{w.i} {nm} inset","INSET"),w,ua+0.28,ub-0.28,h0+0.28,h1-0.28,d1,d1+0.035,0.012)
    # band across door heads / continuous handled by tier; cornice + trim stripe + clerestory
    A.wbox((f"w{w.i} cornice","IRON"),w,0,w.L,14.4,15.0,0,0.38,0.03,0)
    A.wbox((f"w{w.i} corniceStripe","TRIM"),w,0,w.L,14.3,14.4,0,0.40,0.012,0)
    for i in range(len(edges)-1):
        u0=edges[i]+0.5; u1=edges[i+1]-0.5
        A.wbox((f"w{w.i} clerestory","CLERE"),w,u0,u1,13.62,14.25,-0.05,0.02,0.01,0.01)
    # columns
    for c in cs:
        p=w.pt(c,0.0)
        A.wbox((f"w{w.i} colweb","IRON"),w,c-0.07,c+0.07,0,14.4,0,0.30,0.012,0)
        A.wbox((f"w{w.i} colflange","IRON"),w,c-0.24,c+0.24,0,14.4,0.30,0.42,0.02,0)
        A.wbox((f"w{w.i} colbase","IRON"),w,c-0.34,c+0.34,0,0.07,0,0.55,0.02,0)
        A.wbox((f"w{w.i} colcap","IRON"),w,c-0.30,c+0.30,14.1,14.4,0,0.48,0.02,0)
    # doors: jambs + threshold
    if w.i in OPEN:
        c,h=OPEN[w.i]
        for sgn in(-1,1):
            u=c+sgn*(h+0.22)
            A.wbox((f"w{w.i} jamb","IRON"),w,u-0.22,u+0.22,0,DOORH+0.05,-0.05,0.34,0.02,0)
            A.wbox((f"w{w.i} jambTrim","TRIM"),w,u-0.24 if sgn<0 else u+0.20,u-0.20 if sgn<0 else u+0.24,0,DOORH+0.05,0.0,0.36,0.01,0)
        A.wbox((f"w{w.i} lintel","IRON"),w,c-h-0.44,c+h+0.44,DOORH-0.02,DOORH+0.30,-0.05,0.40,0.02,0)
        A.wbox((f"w{w.i} threshold","TRIM"),w,c-h,c+h,0,0.03,-0.6,1.1,0.01,0)
        for sgn in(-1,1): A.wbox((f"w{w.i} reveal","IRON"),w,c+sgn*h-0.05 if sgn<0 else c+sgn*h-0.05,c+sgn*h+0.05,0,DOORH,-0.55,0.0,0.01,0)
        A.wbox((f"w{w.i} reveal","IRON"),w,c-h,c+h,DOORH-0.06,DOORH,-0.55,0.0,0.01,0)
        for sgn,(ua,ub) in ((-1,(c-h+0.02,c-0.015)),(1,(c+0.015,c+h-0.02))):
            A.wbox((f"w{w.i} doorleaf","DOOR"),w,ua,ub,0.03,DOORH-0.08,-0.50,-0.35,0.03,0.0)
            A.wbox((f"w{w.i} doorleaf panel","DOORP"),w,ua+0.28,ub-0.28,0.65,DOORH-0.55,-0.35,-0.31,0.02,0.0)
            A.wbox((f"w{w.i} doorleaf hazard","TRIM"),w,ua+0.04,ub-0.04,0.03,0.42,-0.35,-0.32,0.01,0.0)
            A.wbox((f"w{w.i} doorleaf slit","CLERE"),w,(ua+ub)/2-0.30,(ua+ub)/2+0.30,3.25,3.75,-0.31,-0.29,0.005,0.0)
            hx=c+sgn*0.20; A.wbox((f"w{w.i} doorleaf handle","IRON"),w,hx-0.03,hx+0.03,1.0,1.9,-0.35,-0.24,0.008,0.0)
        A.wbox((f"w{w.i} doorleaf seam","IRON"),w,c-0.015,c+0.015,0.03,DOORH-0.08,-0.50,-0.30,0.0,0.0)
        A.wbox((f"w{w.i} statuslamp","LAMP"),w,c-0.16,c+0.16,DOORH+0.36,DOORH+0.52,0.40,0.46,0.01,0.0)
        A.wbox((f"w{w.i} signplate","IRON"),w,c-1.7,c+1.7,DOORH+0.06,DOORH+0.30,0.40,0.46,0.015,0.0)
# corner piers (vertex columns)
for i in range(8):
    v=Vector(V[i]); a=WALLS[i]; b=WALLS[i-1]
    bis=(a.n+b.n).normalized(); ang=math.atan2(bis.y,bis.x); p=v+bis*0.30
    A.box(("corners colmain","IRON"),p.x,p.y,0,14.4,0.62,0.62,ang,0.03)
    A.box(("corners colbase","IRON"),p.x,p.y,0,0.08,0.86,0.86,ang,0.03)
    A.box(("corners colcap","IRON"),p.x,p.y,14.0,14.4,0.74,0.74,ang,0.03)
    A.box(("corners colband","TRIM"),p.x,p.y,1.25,1.38,0.66,0.66,ang,0.01)
# roof girders (I-sections) across the hall
def girder(x0,y0,x1,y1,z):
    L=math.hypot(x1-x0,y1-y0); ang=math.atan2(y1-y0,x1-x0); cx,cy=(x0+x1)/2,(y0+y1)/2
    A.box(("roof girders","IRON"),cx,cy,z,z+0.08,L,0.42,ang,0.015); A.box(("roof girders","IRON"),cx,cy,z+0.62,z+0.70,L,0.42,ang,0.015); A.box(("roof girders","IRON"),cx,cy,z+0.08,z+0.62,L,0.10,ang,0.01)
for x in(-7.5,-3.6,3.6,7.5): girder(x,-10.4,x,10.4,13.7)
for y in(-6.0,6.0): girder(-10.4,y,10.4,y,13.85)
# ---- 4. floor (octagon with the pool opening)
bm=bmesh.new(); R=3.95
outer=[bm.verts.new((x,y,0)) for x,y in V]; inner=[bm.verts.new((R*math.cos(2*math.pi*i/48),R*math.sin(2*math.pi*i/48),0)) for i in range(48)]
oe=[bm.edges.new((outer[i],outer[(i+1)%8])) for i in range(8)]; ie=[bm.edges.new((inner[i],inner[(i+1)%48])) for i in range(48)]
bmesh.ops.bridge_loops(bm,edges=oe+ie)
me=bpy.data.meshes.new("R2 floor"); bm.to_mesh(me); bm.free(); fo=bpy.data.objects.new("R2 floor",me)
fc=bpy.data.collections.get("22 R2 ARCHITECTURE") or bpy.data.collections.new("22 R2 ARCHITECTURE")
if fc.name not in sc.collection.children: sc.collection.children.link(fc)
fc.objects.link(fo); me.materials.append(M["FLOOR"]); 
for p in me.polygons: p.normal  # ensure up
objs=A.build("22 R2 ARCHITECTURE","R2",M)
SIGNS={1:"COOLING PLANT",4:"FUEL HANDLING",6:"MAIN ACCESS"}
for wi,txt in SIGNS.items():
    w=WALLS[wi]; c,h=OPEN[wi]; p=w.pt(c,0.475)
    cu=bpy.data.curves.new(f"R2 sign {txt}",'FONT'); cu.body=txt; cu.size=0.15; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.space_character=1.2
    ob=bpy.data.objects.new(f"R2 sign {txt}",cu); ob.location=(p.x,p.y,DOORH+0.18); ob.rotation_euler=(math.pi/2,0,w.angle+math.pi); fc.objects.link(ob); cu.materials.append(M["TEXT"])
for o in bpy.data.objects:
    if o.name.startswith("R2 ") and o.type=='MESH': 
        for p in o.data.polygons: p.use_smooth=False
print("R2 objects:",len(objs)+1)
bpy.ops.wm.save_as_mainfile(filepath=S+"/w21.blend"); print("ok")
