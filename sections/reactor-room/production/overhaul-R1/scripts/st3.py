import bpy,sys,math,json,random; sys.path.insert(0,"."); from hs import *
S=sys.argv[sys.argv.index("--")+1]; src=sys.argv[sys.argv.index("--")+2]; dst=sys.argv[sys.argv.index("--")+3]
bpy.ops.wm.open_mainfile(filepath=S+"/"+src); sc=bpy.context.scene
M=mats(); A=K(); R=random.Random(11)
occ=json.load(open(S+"/occ.json")); CELL=0.25; N=len(occ)
def cell(x,y): return int((x+11)/CELL),int((y+11)/CELL)
def free(x,y,r):
    i0,j0=cell(x-r,y-r); i1,j1=cell(x+r,y+r)
    for i in range(i0,i1+1):
        for j in range(j0,j1+1):
            if not(0<=i<N and 0<=j<N) or occ[i][j]: return False
    return True
def mark(x,y,r,v=1):
    i0,j0=cell(x-r,y-r); i1,j1=cell(x+r,y+r)
    for i in range(i0,i1+1):
        for j in range(j0,j1+1):
            if 0<=i<N and 0<=j<N: occ[i][j]=v
# ---------------- prop library (local frame: +y = front/into hall for wall props; z up) ----------------
def crate(g,x,y,w=0.7,h=0.6,d=0.7,z=0.0):
    A.bx((g,"CRATE"),x-w/2,x+w/2,y-d/2,y+d/2,z,z+h,0.02)
    for dx in (-w/2,w/2-0.06): A.bx((g,"IRON"),x+dx,x+dx+0.06,y-d/2-0.008,y+d/2+0.008,z,z+h,0.004)
    for dz in (0.12,h-0.18): A.bx((g,"TRIM"),x-w/2-0.008,x+w/2+0.008,y-d/2-0.008,y+d/2+0.008,z+dz,z+dz+0.06,0.004)
def drum(g,x,y,z=0.0,m="DRUM",h=0.88,r=0.29,tip=False):
    if not tip:
        A.prism((g,m),(x,y,z),(x,y,z+h),r,r,8); 
        for zz in (0.22,0.62): A.prism((g,"IRON"),(x,y,z+zz),(x,y,z+zz+0.05),r*1.04,r*1.04,8)
        A.prism((g,"IRON"),(x,y,z+h),(x,y,z+h+0.02),r*0.9,r*0.9,8); A.prism((g,"TRIM"),(x+0.1,y,z+h+0.02),(x+0.1,y,z+h+0.05),0.045,0.045,6)
    else:
        A.prism((g,m),(x-h/2,y,z+r),(x+h/2,y,z+r),r,r,8)
        for xx in (-0.28,0.08): A.prism((g,"IRON"),(x+xx,y,z+r),(x+xx+0.05,y,z+r),r*1.04,r*1.04,8)
def toolcart(g,x,y):
    A.bx((g,"OLIVE"),x-0.35,x+0.35,y-0.22,y+0.22,0.16,0.85,0.02)
    for i in range(4): A.bx((g,"IRON"),x-0.31,x+0.31,y+0.22,y+0.235,0.2+i*0.16,0.32+i*0.16,0.004); A.bx((g,"TRIM"),x-0.1,x+0.1,y+0.235,y+0.25,0.24+i*0.16,0.27+i*0.16,0.004)
    A.bx((g,"IRON"),x-0.37,x+0.37,y-0.24,y+0.24,0.85,0.89,0.01)
    A.bx((g,"IRON"),x-0.36,x-0.32,y-0.26,y-0.22,0.85,1.05,0.004); A.bx((g,"IRON"),x+0.32,x+0.36,y-0.26,y-0.22,0.85,1.05,0.004); A.bx((g,"TRIM"),x-0.36,x+0.36,y-0.27,y-0.23,1.0,1.05,0.006)
    for dx in (-0.3,0.3):
        for dy in (-0.17,0.17): A.prism((g,"IRON"),(x+dx,y+dy,0.0),(x+dx,y+dy,0.14),0.07,0.07,6)
def locker(g,x,y,n=3):
    w=0.42
    for i in range(n):
        a=x+(i-(n-1)/2)*w
        A.bx((g,"IRON"),a-w/2+0.005,a+w/2-0.005,y,y+0.45,0.12,1.9,0.012)
        A.fb((g,"ENAM"),'+y',y+0.45,a-w/2+0.02,a+w/2-0.02,0.2,1.82,0.02,0.006)
        A.louvre((g,"IRON"),'+y',y+0.47,a-w/2+0.05,a+w/2-0.05,1.55,1.75,n=4,t=0.015,back=(g,"INK"))
        A.bx((g,"TRIM"),a+0.1,a+0.14,y+0.47,y+0.5,0.95,1.1,0.003)
    A.bx((g,"IRON"),x-n*w/2-0.01,x+n*w/2+0.01,y-0.01,y+0.47,0.0,0.12,0.006); A.bx((g,"IRON"),x-n*w/2,x+n*w/2,y,y+0.5,1.9,1.97,0.01)
def ext(g,x,y):
    A.prism((g,"RUST"),(x,y+0.09,0.85),(x,y+0.09,1.32),0.075,0.075,8); A.prism((g,"IRON"),(x,y+0.09,1.32),(x,y+0.09,1.4),0.04,0.06,8); A.bx((g,"IRON"),x-0.03,x+0.03,y+0.03,y+0.18,1.4,1.46,0.004)
    A.bx((g,"IRON"),x-0.05,x+0.05,y,y+0.03,0.95,1.05,0.003); A.bx((g,"IRON"),x-0.05,x+0.05,y,y+0.03,1.2,1.3,0.003)
    A.bx((g,"RUST"),x-0.25,x+0.25,y,y+0.02,1.6,2.05,0.004); A.bx((g,"PAPER"),x-0.2,x+0.2,y+0.02,y+0.024,1.65,1.98,0.001)
def firstaid(g,x,y):
    A.bx((g,"OLIVE"),x-0.2,x+0.2,y,y+0.12,1.2,1.55,0.012); A.bx((g,"PAPER"),x-0.05,x+0.05,y+0.12,y+0.125,1.28,1.47,0.001); A.bx((g,"PAPER"),x-0.14,x+0.14,y+0.12,y+0.125,1.34,1.41,0.001)
def gascyl(g,x,y):
    for dx in (-0.14,0.14):
        A.prism((g,"IRON"),(x+dx,y+0.14,0.0),(x+dx,y+0.14,1.05),0.1,0.1,8); A.prism((g,"IRON"),(x+dx,y+0.14,1.05),(x+dx,y+0.14,1.22),0.1,0.03,8); A.bx((g,"TRIM"),x+dx-0.04,x+dx+0.04,y+0.1,y+0.18,1.22,1.3,0.004)
        A.prism((g,"TRIM"),(x+dx,y+0.14,0.7),(x+dx,y+0.14,0.8),0.104,0.104,8)
    A.bx((g,"TRIM"),x-0.28,x+0.28,y+0.01,y+0.03,0.75,0.8,0.003)
def ladder(g,x,y,h=2.6,lean=0.5):
    for dx in (-0.22,0.22): A.prism((g,"TRIM"),(x+dx,y+0.03,0.0),(x+dx,y+lean,h),0.025,0.025,4,math.pi/4) if False else A.hull((g,"TRIM"),[(x+dx-0.02,y+lean+0.02*0,h),(x+dx+0.02,y+lean,h),(x+dx-0.02,y+0.4,0),(x+dx+0.02,y+0.4,0),(x+dx-0.02,y+lean-0.05,h),(x+dx+0.02,y+lean-0.05,h),(x+dx-0.02,y+0.3,0),(x+dx+0.02,y+0.3,0)],0.002)
    for i in range(1,9):
        t=i/9; zz=t*h; yy=0.35+(lean-0.02-0.35)*t; A.bx((g,"IRON"),x-0.22,x+0.22,y+yy-0.02,y+yy+0.02,zz,zz+0.03,0.002)
def board(g,x,y,w=0.9,h=0.6,z=1.3):
    A.bx((g,"IRON"),x-w/2,x+w/2,y,y+0.03,z,z+h,0.008); A.bx((g,"TRIM"),x-w/2-0.02,x+w/2+0.02,y,y+0.035,z-0.02,z,0.004)
    A.bx((g,"INSET"),x-w/2+0.03,x+w/2-0.03,y+0.03,y+0.04,z+0.03,z+h-0.03,0.002)
    for i in range(R.randint(3,5)):
        px=x-w/2+0.08+R.random()*(w-0.3); pz=z+0.06+R.random()*(h-0.3); A.bx((g,"PAPER"),px,px+0.14+R.random()*0.05,y+0.04,y+0.046,pz,pz+0.2,0.001)
def sign_a(g,x,y,yaw=0):
    A.hull((g,"CONE"),[(x-0.2,y-0.2,0),(x+0.2,y-0.2,0),(x-0.2,y+0.2,0),(x+0.2,y+0.2,0),(x-0.16,y,0.62),(x+0.16,y,0.62),(x-0.16,y+0.02,0.62),(x+0.16,y+0.02,0.62)],0.006)
    A.bx((g,"INK"),x-0.12,x+0.12,y-0.005,y+0.005,0.3,0.5,0.001) if False else None
def barrier(g,x,y,L=1.4):
    A.hull((g,"CONE"),[(x-L/2,y-0.28,0),(x+L/2,y-0.28,0),(x-L/2,y+0.28,0),(x+L/2,y+0.28,0),(x-L/2,y-0.09,0.7),(x+L/2,y-0.09,0.7),(x-L/2,y+0.09,0.7),(x+L/2,y+0.09,0.7)],0.015)
    for i in range(4): A.bx((g,"INK"),x-L/2+0.1+i*0.35,x-L/2+0.25+i*0.35,y-0.291,y-0.28,0.32,0.58,0.002) if False else None
    A.bx((g,"INK"),x-L/2,x+L/2,y-0.285,y-0.27,0.3,0.42,0.002); A.bx((g,"INK"),x-L/2,x+L/2,y+0.27,y+0.285,0.3,0.42,0.002)
def reel(g,x,y):
    for dy in (-0.2,0.2): A.prism((g,"CRATE"),(x,y+dy,0.45),(x,y+dy+0.03*(1 if dy>0 else -1),0.45),0.45,0.45,12,0)
    A.prism((g,"CABLE"),(x,y-0.2,0.45),(x,y+0.2,0.45),0.3,0.3,12,0); A.prism((g,"IRON"),(x,y-0.23,0.45),(x,y+0.23,0.45),0.1,0.1,8)
    A.bx((g,"IRON"),x-0.45,x-0.4,y-0.25,y+0.25,0.0,0.06,0.003) if False else None
def hose(g,x,y):
    for k in range(3):
        for i in range(16):
            a=2*math.pi*i/16; b=a+2*math.pi/16; r=0.36-k*0.03
            A.prism((g,"CABLE"),(x+r*math.cos(a),y+r*math.sin(a),0.05+k*0.075),(x+r*math.cos(b),y+r*math.sin(b),0.05+k*0.075),0.035,0.035,5,0)
def bin_(g,x,y):
    A.prism((g,"IRON"),(x,y,0),(x,y,0.7),0.2,0.24,8); A.prism((g,"TRIM"),(x,y,0.7),(x,y,0.73),0.26,0.26,8)
def pallet(g,x,y,n=None):
    A.bx((g,"CRATE"),x-0.55,x+0.55,y-0.45,y+0.45,0.0,0.13,0.01)
    for i in range(3): A.bx((g,"CRATE"),x-0.55+i*0.49,x-0.55+i*0.49+0.12,y-0.45,y+0.45,0.13,0.16,0.003)
    for k in range(R.randint(2,4)):
        A.bx((g,"INK"),x-0.5+(k%2)*0.5+R.uniform(-.02,.02),x-0.05+(k%2)*0.5,y-0.4+(k//2)*0.42,y-0.02+(k//2)*0.42,0.16,0.62,0.02)
        A.bx((g,"TRIM"),x-0.5+(k%2)*0.5,x-0.05+(k%2)*0.5,y-0.4+(k//2)*0.42,y-0.02+(k//2)*0.42,0.38,0.41,0.004)
def puddle(g,x,y,r=0.6):
    pts=[]
    n=9
    for i in range(n):
        a=2*math.pi*i/n; rr=r*(0.75+R.random()*0.45); pts.append((x+rr*math.cos(a),y+rr*math.sin(a)*0.75))
    A.hull((g,"PUD"),[(px,py,z) for (px,py) in pts for z in (0.004,0.009)],0.0)
def paper_spill(g,x,y):
    for i in range(R.randint(4,7)):
        ang=R.uniform(0,3.14); px=x+R.uniform(-0.4,0.4); py=y+R.uniform(-0.4,0.4)
        A.box((g,"PAPER"),px,py,0.006+i*0.0012,0.008+i*0.0012,0.21,0.3,ang,0.0)
def stool(g,x,y):
    A.prism((g,"FAB"),(x,y,0.44),(x,y,0.5),0.17,0.17,8)
    for a in range(3): t=a*2*math.pi/3; A.prism((g,"IRON"),(x+0.14*math.cos(t),y+0.14*math.sin(t),0.0),(x+0.03*math.cos(t),y+0.03*math.sin(t),0.44),0.015,0.015,4)
def drain(g,x,y):
    A.prism((g,"INK"),(x,y,0.0),(x,y,0.012),0.32,0.32,8)
    for i in range(-2,3): A.bx((g,"IRON"),x-0.24,x+0.24,y+i*0.09-0.02,y+i*0.09+0.02,0.011,0.02,0.002)
# ---------------- placement ----------------
placed=[]
def try_floor(fn,kind,r,n,tries,bandmin=5.9,bandmax=9.3,lane=True):
    c=0
    for _ in range(tries):
        if c>=n: break
        a=R.uniform(0,2*math.pi); rad=R.uniform(bandmin,bandmax); x=rad*math.cos(a); y=rad*math.sin(a)
        if max(abs(x),abs(y))>10.0 or abs(x)+abs(y)>14.2: continue
        if not free(x,y,r+0.25): continue
        if any((x-px)**2+(y-py)**2<(r+pr+0.4)**2 for px,py,pr in placed): continue
        placed.append((x,y,r)); mark(x,y,r+0.1); fn(x,y,R.uniform(0,2*math.pi)); c+=1
    return c
def cands():
    L=[(wi,0.6+k*0.3) for wi in range(8) for k in range(int((WALLS[wi].L-1.2)/0.3))]
    R.shuffle(L); return L
def wall_props(fn,r,n,w_ok=None,depth=0.55,clear=0.6,**kw):
    c=0
    for wi,u in cands():
        if c>=n: break
        if w_ok and wi not in w_ok: continue
        w=WALLS[wi]; p=w.pt(u,depth/2+0.1)
        if not free(p.x,p.y,r*clear): continue
        if any((p.x-px)**2+(p.y-py)**2<(r+pr)**2*0.6 for px,py,pr in placed): continue
        placed.append((p.x,p.y,r)); mark(p.x,p.y,r*clear+0.05); pw=w.pt(u,0.0)
        A.begin(pw.x,pw.y,w.angle); fn(); A.end(); c+=1
    return c
def wall_flat(fn,n,**kw): return wall_props(fn,0.3,n,depth=0.3,clear=1.0)
def fl(f): 
    def g_(x,y,yaw): A.begin(x,y,yaw); f(); A.end()
    return g_
g="dress"
nW={}
nW["locker"]=wall_props(lambda:locker(g,0,0.02,3),0.9,3,tries=3000)
nW["cart"]=wall_props(lambda:toolcart(g,0,0.32),0.5,3)
nW["gas"]=wall_props(lambda:gascyl(g,0,0.02),0.4,3)
nW["ladder"]=wall_props(lambda:ladder(g,0,0.02),0.45,2)
nW["reel"]=wall_props(lambda:reel(g,0,0.5),0.55,2)
nW["pallet"]=wall_props(lambda:pallet(g,0,0.55),0.7,3)
nW["drum"]=wall_props(lambda:(drum(g,-0.3,0.35),drum(g,0.3,0.4,m=R.choice(["DRUM","RUST","OLIVE"])),drum(g,0,0.85,m="DRUM")),0.8,3)
nW["crate"]=wall_props(lambda:(crate(g,-0.4,0.4),crate(g,0.35,0.42,0.6,0.5,0.6),crate(g,-0.4,0.4,0.55,0.5,0.55,z=0.6)),0.8,3)
nW["bin"]=wall_props(lambda:bin_(g,0,0.3),0.3,3)
nW["hose"]=wall_props(lambda:hose(g,0,0.45),0.5,2)
for k in ("ext","aid","board"):
    pass
nW["ext"]=wall_flat(lambda:ext(g,0,0.02),5)
nW["aid"]=wall_flat(lambda:firstaid(g,0,0.02),3)
nW["board"]=wall_flat(lambda:board(g,0,0.02),4)
nF={}
nF["barrier"]=try_floor(fl(lambda:barrier(g,0,0)),"b",0.8,3,200)
nF["drums"]=try_floor(fl(lambda:(drum(g,0,0),drum(g,0.55,0.1,m="RUST"),drum(g,0.25,0.55,tip=True,m="DRUM"))),"d",0.9,2,200)
nF["sign"]=try_floor(fl(lambda:sign_a(g,0,0)),"s",0.3,5,200)
nF["stool"]=try_floor(fl(lambda:stool(g,0,0)),"t",0.25,2,200)
nF["paper"]=try_floor(fl(lambda:paper_spill(g,0,0)),"p",0.5,4,200)
nF["puddle"]=try_floor(fl(lambda:puddle(g,0,0,R.uniform(0.5,0.9))),"u",0.6,7,200,5.2,9.5)
nF["drain"]=try_floor(fl(lambda:drain(g,0,0)),"r",0.4,5,200,5.3,9.3)
print("wall",nW,"floor",nF)
objs=A.build("29 R2 DRESSING 2","R2 dress",M)
for o in objs:
    for p in o.data.polygons: p.use_smooth=False
print("objs",len(objs),"tris",sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objs))
bpy.ops.wm.save_as_mainfile(filepath=S+"/"+dst)
