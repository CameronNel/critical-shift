import bpy,bmesh,sys,math,json; sys.path.insert(0,"."); from r2lib import *; from lib import col,port,bbw
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w29.blend"); sc=bpy.context.scene
G=lambda n:bpy.data.materials[n]
M={"IRON":G("R2 iron"),"TRIM":G("R2 trim rust")}
M["COOL"]=r2mat("R2 pipe coolant",(0.16,0.15,0.30),0.42,edge=(0.45,0.42,0.75),grime=0.4,noise=(2.5,0),metal=0.25,mottle=0.5)
M["STEAM"]=r2mat("R2 pipe lagging",(0.28,0.26,0.30),0.85,edge=(0.55,0.50,0.55),grime=0.6,noise=(3,0),mottle=0.7)
M["HYD"]=r2mat("R2 pipe hydraulic",(0.05,0.045,0.07),0.4,edge=(0.6,0.3,0.06),grime=0.3,noise=(3,0),metal=0.4,mottle=0.4)
M["VENT"]=r2mat("R2 pipe vent",(0.11,0.09,0.09),0.7,edge=(0.5,0.25,0.1),grime=0.6,noise=(3,0),metal=0.2,mottle=0.6)
M["TRAY"]=r2mat("R2 cable tray",(0.10,0.10,0.14),0.5,edge=(0.55,0.5,0.6),grime=0.4,noise=(3,0),metal=0.6,mottle=0.5)
M["CABLE"]=r2mat("R2 cable",(0.008,0.008,0.010),0.6,edge=None,grime=0.0,noise=(3,0),mottle=0.0)
M["CONDUIT"]=r2mat("R2 conduit",(0.06,0.055,0.08),0.5,edge=(0.5,0.3,0.1),grime=0.4,noise=(3,0),metal=0.5,mottle=0.4)
DEAD=("Coolant header","Manifold valved drop","Manifold wall tie","ECCS maintained loop connection","Pump rising outlet","Pump gauge pressure connection","Turbine inlet","Turbine return outlet","WC C turbine wall coupling","Waste transfer closed line","Header clamp strap","WA A connected supply","WA A console back supply","WB B attached signal","WB B vent control feed","WB B wall feed","WC C demand feed","WC C grid supply","WC C grid wall feed","WD D starter drop","WD D starter wall feed","WE E bench outlet feed","MF14 A power drop","MF14 B power drop","MF10 starter conduit","Motor junction electrical feed")
nd=0
for o in list(bpy.data.objects):
    if o.type=='CURVE' and o.name.split('.')[0] in DEAD: bpy.data.objects.remove(o,do_unlink=True); nd+=1
print("dangling legacy pipe/feed curves removed:",nd)
A=Acc(); RUNS=[]; PORTS={o.name:o for o in bpy.data.objects if o.name.startswith("PORT_")}
def cyl(key,p0,p1,r,seg=8):
    p0=Vector(p0);p1=Vector(p1);d=p1-p0;L=d.length
    if L<1e-4: return
    bm=A.get(key); res=bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r,radius2=r,depth=L); q=d.to_track_quat('Z','Y'); m=(p0+p1)/2
    for v in res['verts']: v.co=q@v.co+m
def ball(key,p,r):
    bm=A.get(key); res=bmesh.ops.create_uvsphere(bm,u_segments=8,v_segments=5,radius=r)
    for v in res['verts']: v.co=v.co+Vector(p)
def wall_of(p):
    best=None
    for w in WALLS:
        d=(Vector((p[0],p[1]))-w.P).dot(w.n)   # distance in front of the wall plane (positive inside)
        u=(Vector((p[0],p[1]))-w.P).dot(w.t)
        if -0.1<=u<=w.L+0.1 and (best is None or abs(d)<abs(best[1])): best=(w,d,u)
    return best
def bracket(pt,r,mk):
    w,d,u=wall_of(pt)
    if 0.12<d<1.2:
        base=w.pt(u,0.0); A.box((f"bracket {mk}","IRON"),(pt[0]+base.x)/2,(pt[1]+base.y)/2,pt[2]-r-0.03,pt[2]-r+0.0,d,0.06,w.angle+math.pi/2,0.005)
        A.box((f"bracket {mk}","IRON"),pt[0],pt[1],pt[2]-r-0.05,pt[2]+r+0.03,0.05,0.16,w.angle+math.pi/2,0.005)
def sleeve(p,r,axis_dir):
    d=Vector(axis_dir); bm=A.get(("sleeve","IRON")); res=bmesh.ops.create_cone(bm,cap_ends=True,segments=8,radius1=r*1.9,radius2=r*1.9,depth=0.08); q=d.to_track_quat('Z','Y')
    for v in res['verts']: v.co=q@v.co+Vector(p)
def run(name,pts,r,mk,seg=8,tees=(),start_port=None,end_port=None,supports=True,bands=True,flange_ends=True):
    key=(name,mk); pts=[Vector(p) for p in pts]
    for a,b in zip(pts,pts[1:]):
        cyl(key,a,b,r,seg)
        L=(b-a).length
        if bands and L>1.0:
            n=int(L/1.4)
            for i in range(1,n+1):
                t=i/(n+1); c=a+(b-a)*t; d=(b-a).normalized(); cyl((name+" band","TRIM" if mk in("STEAM","HYD") else "IRON"),c-d*0.03,c+d*0.03,r*1.35,seg)
        if supports and L>1.2:
            n=int(L/1.6)
            for i in range(n+1):
                t=(i+0.5)/(n+1); c=a+(b-a)*t; bracket((c.x,c.y,c.z),r,mk)
    for p in pts[1:-1]: ball(key,p,r*1.06)
    if flange_ends:
        for p,q in ((pts[0],pts[1]),(pts[-1],pts[-2])):
            d=(q-p).normalized(); cyl((name+" flange","IRON"),p,p+d*0.04,r*1.7,seg)
    RUNS.append({"name":name,"pts":[tuple(p) for p in pts],"start":tuple(pts[0]),"end":tuple(pts[-1]),"tees":[tuple(t) for t in tees],"start_port":start_port,"end_port":end_port,"r":r})
def wallport(name,loc,medium,dn,dir_):
    e=port("PORT_WALL_"+name,loc,medium,dn,dir_); e["connected"]=True; return e
def use(pn): PORTS[pn]["connected"]=True; return tuple(PORTS[pn].location)
# ---- 1. coolant supply from the plant through the -Y wall, header along the wall to the EC tanks and pump
wallport("COOLANT_SUPPLY",(5.0,-10.95,3.9),"coolant",150,(0,1,0)); sleeve((5.0,-10.78,3.9),0.085,(0,1,0))
run("coolant supply header",[(5.0,-10.95,3.9),(5.0,-10.28,3.9),(0.55,-10.28,3.9)],0.085,"COOL",start_port="PORT_WALL_COOLANT_SUPPLY")
run("EC-1 feed",[(3.3,-10.28,3.9),(3.3,-9.65,3.9),use("PORT_EC-1_top")],0.06,"COOL",tees=[(3.3,-10.28,3.9)],end_port="PORT_EC-1_top",supports=False)
run("EC-2 feed",[(1.8,-10.28,3.9),(1.8,-9.65,3.9),use("PORT_EC-2_top")],0.06,"COOL",tees=[(1.8,-10.28,3.9)],end_port="PORT_EC-2_top",supports=False)
run("pump suction via isolation valves",[(0.55,-10.28,3.9),(0.55,-9.49,3.9),(0.55,-9.49,1.1),(-1.9,-9.49,1.1),(-1.9,-9.5,0.55),use("PORT_P-10_suction")],0.07,"COOL",tees=[(0.55,-10.28,3.9)],end_port="PORT_P-10_suction",supports=False)
for tag,x in (("EC-1",3.3),("EC-2",1.8)):
    wallport(f"{tag}_INJECTION",(x,-10.98,1.05),"coolant",65,(0,-1,0)); sleeve((x,-10.78,1.05),0.065,(0,1,0))
    run(f"{tag} injection line",[use(f"PORT_{tag}_wall"),(x,-10.98,1.05)],0.065,"COOL",end_port=f"PORT_WALL_{tag}_INJECTION",supports=False)
# ---- 2. pump discharge: riser, drop into the floor trench box, cover plates to the pool, submerged inlet riser
run("pump discharge",[use("PORT_P-10_discharge"),(-2.75,-9.5,2.3),(-2.75,-8.4,2.3),(-2.75,-8.4,0.08)],0.05,"COOL",start_port="PORT_P-10_discharge",end_port="TRENCH_JUNCTION_A")
A.box(("trench box","IRON"),-2.75,-8.4,0.0,0.14,0.55,0.55,0,0.02); A.box(("trench box trim","TRIM"),-2.75,-8.4,0.14,0.16,0.5,0.5,0,0.005)
def trench(p0,p1):
    L=math.hypot(p1[0]-p0[0],p1[1]-p0[1]); ang=math.atan2(p1[1]-p0[1],p1[0]-p0[0]); cx,cy=(p0[0]+p1[0])/2,(p0[1]+p1[1])/2
    A.box(("trench cover","IRON"),cx,cy,0.0,0.03,L,0.5,ang,0.005); nx,ny=-math.sin(ang),math.cos(ang)
    for s in(-1,1): A.box(("trench edge","TRIM"),cx+nx*s*0.22,cy+ny*s*0.22,0.03,0.045,L,0.05,ang,0.003)
    for i in range(int(L/0.5)): 
        t=(i+0.5)*0.5-L/2; A.box(("trench slat","IRON"),cx+math.cos(ang)*t,cy+math.sin(ang)*t,0.03,0.04,0.04,0.42,ang,0.002)
trench((-2.75,-8.4),(-2.75,-6.6)); trench((-2.75,-6.6),(-1.4,-4.9))
A.box(("pool inlet manifold","IRON"),-1.4,-4.9,0.0,0.40,0.6,0.6,0,0.02); A.box(("pool inlet manifold trim","TRIM"),-1.4,-4.9,0.40,0.42,0.5,0.5,0,0.005)
run("pool inlet",[(-1.4,-4.9,0.32),(-1.4,-3.2,0.32),(-1.4,-3.2,-3.0)],0.05,"COOL",start_port="TRENCH_JUNCTION_B",end_port="POOL_DIFFUSER",supports=False,flange_ends=False)
A.box(("pool diffuser","IRON"),-1.4,-3.2,-3.25,-2.95,0.34,0.34,0,0.02)
for k in range(4): A.box(("pool diffuser slot","TRIM"),-1.4,-3.2,-3.2+k*0.06,-3.17+k*0.06,0.36,0.30,0,0.0)
for z in(0.0,-1.5): A.box(("pool riser clamp","IRON"),-1.4,-3.12,z-0.05,z+0.05,0.16,0.10,0,0.005)
# ---- 3. steam in through the east wall, lagged drop to the turbine; exhaust through the wall
wallport("STEAM_SUPPLY",(10.95,-3.8,6.4),"steam",150,(-1,0,0)); sleeve((10.78,-3.8,6.4),0.10,(1,0,0))
run("steam supply",[(10.95,-3.8,6.4),(9.6,-3.8,6.4),use("PORT_T-06_steam_in")],0.10,"STEAM",start_port="PORT_WALL_STEAM_SUPPLY",end_port="PORT_T-06_steam_in",supports=True)
wallport("STEAM_EXHAUST",(10.95,-3.3,1.15),"steam_exhaust",200,(-1,0,0)); sleeve((10.78,-3.3,1.15),0.10,(1,0,0))
run("turbine exhaust",[use("PORT_T-06_exhaust"),(10.95,-3.3,1.15)],0.10,"STEAM",end_port="PORT_WALL_STEAM_EXHAUST",supports=False)
# ---- 4. waste cask vent to the north-east wall
wallport("WASTE_VENT",(8.6,9.2,5.2),"vent",50,(-1,-1,0)); sleeve((8.1,8.7,5.2),0.05,(1,1,0))
run("waste vent",[use("PORT_W-04_vent"),(7.6,8.2,5.2),(8.1,8.7,5.2),(8.6,9.2,5.2)],0.05,"VENT",start_port="PORT_W-04_vent",end_port="PORT_WALL_WASTE_VENT")
# ---- 5. bank hydraulics: pressure unit and return tank on the gantry, four lines
A.box(("hydraulic unit","IRON"),0,2.1,12.55,13.45,1.20,0.60,0,0.03); A.box(("hydraulic unit trim","TRIM"),0,2.1,12.95,13.05,1.24,0.64,0,0.01)
A.box(("hydraulic return tank","IRON"),0,-2.1,12.55,13.45,1.20,0.60,0,0.03); A.box(("hydraulic return tank trim","TRIM"),0,-2.1,12.95,13.05,1.24,0.64,0,0.01)
for x in(-0.45,0.45):
    for y in(2.1,-2.1): A.box(("hydraulic strut","IRON"),x,y,13.45,13.72,0.05,0.05,0,0.004)
def hyd(tag,sgn,bx):
    p=use(f"PORT_BANK_{tag}_hyd_{'N' if sgn>0 else 'S'}"); xo=bx+ (0.28 if bx<0 else 0.28)+0.62*0
    x1=p[0]+0.28; hpu_x=0.6 if bx>0 else -0.6
    if bx<0: pts=[p,(x1,p[1],p[2]),(x1,p[1],12.5),(x1,sgn*1.66,12.5),(x1,sgn*1.8,12.5)]; end=(x1,sgn*1.8,12.5)
    else:    pts=[p,(x1,p[1],p[2]),(x1,p[1],12.75),(x1,sgn*2.0,12.75),(hpu_x,sgn*2.0,12.75)]; end=(hpu_x,sgn*2.0,12.75)
    run(f"hydraulic {tag}{'N' if sgn>0 else 'S'}",pts,0.03,"HYD",start_port=f"PORT_BANK_{tag}_hyd_{'N' if sgn>0 else 'S'}",end_port=("HPU" if sgn>0 else "RETURN_TANK"),supports=False,seg=8)
hyd("A",1,-1.4); hyd("A",-1,-1.4); hyd("B",1,1.4); hyd("B",-1,1.4)
# ---- 6. perimeter cable ring at z=11.6 (inset 0.95 m) with risers from the powered equipment
Z=11.6; DI=0.95
lines=[(w.P+w.n*DI,w.t) for w in WALLS]
def inter(l1,l2):
    p,d=l1; q,e=l2; det=d.x*(-e.y)+e.x*d.y
    t=((q.x-p.x)*(-e.y)+e.x*(q.y-p.y))/det; return p+d*t
ring=[inter(lines[i-1],lines[i]) for i in range(8)]
for i in range(8):
    a=ring[i]; b=ring[(i+1)%8]; d=b-a; L=d.length; ang=math.atan2(d.y,d.x); c=(a+b)/2
    A.box(("cable tray floor","TRAY"),c.x,c.y,Z,Z+0.03,L,0.46,ang,0.005)
    for s in(-1,1): A.box(("cable tray rail","TRAY"),c.x-math.sin(ang)*s*0.23,c.y+math.cos(ang)*s*0.23,Z,Z+0.10,L,0.03,ang,0.004)
    n=int(L/0.5)
    for k in range(n): t=(k+0.5)/n*L-L/2; A.box(("cable tray rung","TRAY"),c.x+math.cos(ang)*t,c.y+math.sin(ang)*t,Z+0.03,Z+0.06,0.04,0.44,ang,0.003)
    for off in(-0.13,0,0.13): A.box(("cable bundle","CABLE"),c.x-math.sin(ang)*off,c.y+math.cos(ang)*off,Z+0.06,Z+0.12,L*0.985,0.05,ang,0.008)
    for k in range(int(L/2.6)+1):
        t=(k+0.5)*L/(int(L/2.6)+1)-L/2; q=c+Vector((math.cos(ang),math.sin(ang)))*t; nx,ny=-math.sin(ang),math.cos(ang)
        wall=WALLS[i]; base=q-wall.n*(DI); A.box(("tray bracket","IRON"),(q.x+base.x)/2,(q.y+base.y)/2,Z-0.05,Z-0.02,DI,0.05,wall.angle+math.pi/2,0.004)
        A.box(("tray bracket","IRON"),q.x,q.y,Z-0.4,Z-0.02,0.04,0.04,0,0.003)
def nearest_ring(p):
    best=None
    for i in range(8):
        a=ring[i]; b=ring[(i+1)%8]; ab=b-a; t=max(0,min(1,(Vector((p[0],p[1]))-a).dot(ab)/ab.length_squared)); q=a+ab*t; d=(q-Vector((p[0],p[1]))).length
        if best is None or d<best[0]: best=(d,q)
    return best[1]
def riser(name,start):
    q=nearest_ring(start); s=Vector(start)
    pts=[s,Vector((s.x,s.y,Z-0.0)) ] if (Vector((s.x,s.y))-q).length<0.02 else [s,Vector((s.x,s.y,Z-0.55)),Vector((q.x,q.y,Z-0.55)),Vector((q.x,q.y,Z+0.03))]
    run(name,pts,0.03,"CONDUIT",supports=False,bands=False,flange_ends=False,start_port=name.upper().replace(" ","_"),end_port="CABLE_RING")
riser("riser grid cabinets",(9.8,-0.7,2.25)); riser("riser turbine sensor",(10.4,-2.58,2.41)); riser("riser generator",(-10.2,-3.6,1.85)); riser("riser bank control",(3.6,10.3,1.75))
riser("riser control room",(-3.5,-9.85,9.0)); riser("riser elevator machine",(-7.6,-7.9,10.95))
def top_of(x,y,rad=0.35,zmax=3.0):
    best=None
    for o in bpy.data.objects:
        if o.type!='MESH' or o.name.startswith(("R2 ","LP ","EL ","MZ ")): continue
        b=bbw(o)
        if b[0][0]-rad<=x<=b[0][1]+rad and b[1][0]-rad<=y<=b[1][1]+rad and b[2][1]<=zmax and b[2][1]>0.4 and (best is None or b[2][1]>best[2]): best=((b[0][0]+b[0][1])/2,(b[1][0]+b[1][1])/2,b[2][1])
    return best
A.box(("bench socket","IRON"),-10.66,5.2,0.98,1.30,0.16,0.32,0,0.01); A.box(("bench socket lamp","TRIM"),-10.57,5.2,1.10,1.18,0.02,0.10,0,0.004)
riser("riser waste vent control",(10.16,6.79,2.40)); riser("riser west bench",(-10.66,5.2,1.30))
for nm,(x,y) in (("riser reserve power A",(-10.0,3.55)),("riser reserve power B",(-10.0,-5.25))):
    t=top_of(x,y); print(nm,"starts at",t); riser(nm,t if t else (x,y,1.8))
sp=top_of(-3.0,-8.2,0.3,2.0) or (-3.0,-8.2,1.4)
run("pump starter conduit",[(sp[0],sp[1],sp[2]),(sp[0],sp[1],0.05),(-2.75,-8.4,0.05)],0.025,"CONDUIT",start_port="RISER_STARTER",end_port="TRENCH_JUNCTION_A",supports=False,bands=False,flange_ends=False)
objs=A.build("24 R2 PIPING AND CABLES","R2 pipe",M)
for o in objs:
    for p in o.data.polygons: p.use_smooth=False
json.dump(RUNS,open(S+"/runs.json","w"),indent=1)
bpy.ops.wm.save_as_mainfile(filepath=S+"/w30.blend"); print("ok",len(objs),"runs",len(RUNS))
