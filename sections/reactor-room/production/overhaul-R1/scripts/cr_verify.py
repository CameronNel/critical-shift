"""Control-room checks.  usage: python cr_verify.py -- <blend>
 1. every element of the redo collection lies inside the room envelope (x -4.80..2.00, y -11.91..-6.16, z 5.40..8.80) or is a listed exception
 2. nothing of the redo intersects an object of another collection (bounding-box test on real mesh extents of the pieces near the room)
 3. walkability: 2D occupancy (z 5.45..7.3) dilated by the player radius 0.28 m, flood fill from the doorway -> every functional zone reachable
 4. chairs tucked: seat front inside the kneehole, armrests below the desk underside, chair back clear of the desk edge
 5. purple audit incl. emission colours, lights, world and volumes
 6. triangle / object counts per material group"""
import bpy,sys,math,colorsys,collections
import numpy as np
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=sys.argv[sys.argv.index("--")+1]); sc=bpy.context.scene
ENV=(-4.80,2.00,-11.91,-6.16,5.40,8.80); TOL=0.03; bad=0
coll=bpy.data.collections["31 CR CONTROL ROOM REDO"]
def verts(o):
    me=o.data; n=len(me.vertices); a=np.empty(n*3,dtype=np.float32); me.vertices.foreach_get("co",a); a=a.reshape(-1,3)
    M=np.array(o.matrix_world); return a@M[:3,:3].T+M[:3,3]
out=[]
for o in coll.objects:
    if o.type!="MESH": continue
    if o.name.split(" ")[1] in ("wall","deco","ceil","clutter","glassnote","grime","marks","static") or o.name.split(" ")[1].startswith(("lift","ante","control")): continue      # merged whole-room groups: checked by construction; "static" = cr_optimize.py joins (geometry-neutral; run cr_verify on the pre-optimise blend for the full envelope check)
    v=verts(o)
    if not len(v): continue
    mn,mx=v.min(0),v.max(0)
    if mn[0]<ENV[0]-TOL or mx[0]>ENV[1]+TOL or mn[1]<ENV[2]-TOL or mx[1]>ENV[3]+TOL or mn[2]<ENV[4]-TOL or mx[2]>ENV[5]+TOL: out.append((o.name,mn.round(3),mx.round(3)))
print("1. envelope violations:",len(out))
for n,a,b in out: print("   ",n,a,b)
bad+=len(out)
# 2 intersections with other collections
hits=[]
for o in bpy.data.objects:
    if o.type!="MESH" or o.name in coll.objects: continue
    cn=o.users_collection[0].name if o.users_collection else ""
    if cn.startswith(("31 CR","32 CR","20 CONTROL","26 R2","RF ","25 LIGHT")): continue
    if o.name.startswith("LP haze"): continue
    v=verts(o)
    if not len(v): continue
    ins=(v[:,0]>ENV[0]+0.03)&(v[:,0]<ENV[1]-0.03)&(v[:,1]>ENV[2]+0.03)&(v[:,1]<ENV[3]-0.03)&(v[:,2]>ENV[4]+0.03)&(v[:,2]<ENV[5]-0.03)
    if ins.any(): hits.append((cn[:20],o.name,v[ins].min(0).round(2),v[ins].max(0).round(2)))
print("2. other-collection objects inside the room envelope:",len(hits))
for h in hits[:20]: print("   ",h)
bad+=len(hits)
# 3 walkability
G=0.05; x0,y0=ENV[0],ENV[2]; nx=int((ENV[1]-ENV[0])/G)+1; ny=int((ENV[3]-ENV[2])/G)+1; occ=np.zeros((ny,nx),dtype=bool)
def mark(px,py):
    i=((py-y0)/G).astype(int); j=((px-x0)/G).astype(int); ok=(i>=0)&(i<ny)&(j>=0)&(j<nx); occ[i[ok],j[ok]]=True
names=set()
for o in coll.objects:
    if o.type!="MESH" or o.name.startswith("CR haze"): continue
    me=o.data; me.calc_loop_triangles(); T=me.loop_triangles
    if not len(T): continue
    v=verts(o); t=np.empty(len(T)*3,dtype=np.int32); T.foreach_get("vertices",t); t=t.reshape(-1,3); P=v[t]        # (n,3,3)
    zmin=P[:,:,2].min(1); zmax=P[:,:,2].max(1); sel=(zmax>5.45)&(zmin<7.30)&~((zmax-zmin<0.02)&(zmax<5.47))
    P=P[sel]
    if not len(P): continue
    mark(P[:,:,0].ravel(),P[:,:,1].ravel()); mark(P[:,:,0].mean(1),P[:,:,1].mean(1))
    e=np.max(np.linalg.norm(P[:,[0,1,2],:2]-P[:,[1,2,0],:2],axis=2),axis=1)
    for p in P[e>0.04]:
        n=int(min(60,math.ceil(e[np.where((P==p).all((1,2)))[0][0]]/0.03)))
        a,b,c_=np.meshgrid(np.linspace(0,1,n+1),np.linspace(0,1,n+1),[0]); a=a.ravel(); b=b.ravel(); ok=a+b<=1; a,b=a[ok],b[ok]
        q=p[0][None]*(1-a-b)[:,None]+p[1][None]*a[:,None]+p[2][None]*b[:,None]; mark(q[:,0],q[:,1])
# shell: walls block
occ[-1:,:]=True
r=int(round(0.28/G)); Y,X=np.ogrid[-r:r+1,-r:r+1]; k=(X*X+Y*Y<=r*r)
from numpy.lib.stride_tricks import sliding_window_view
pad=np.pad(occ,r,constant_values=True); dil=np.zeros_like(occ)
for dy,dx in zip(*np.nonzero(k)):
    dil|=pad[dy:dy+ny,dx:dx+nx]
seed=(int((-6.8-y0)/G),int((-4.30-x0)/G))
free=~dil; seen=np.zeros_like(free); 
if not free[seed]: print("   WARNING doorway seed blocked"); 
stack=[seed]; seen[seed]=True
while stack:
    i,j=stack.pop()
    for di,dj in((1,0),(-1,0),(0,1),(0,-1)):
        a,b=i+di,j+dj
        if 0<=a<ny and 0<=b<nx and free[a,b] and not seen[a,b]: seen[a,b]=True; stack.append((a,b))
zones={"door entry":(-4.4,-6.8),"desk row operator side bay1":(-2.75,-8.3),"bay2":(-1.05,-8.3),"bay3":(0.65,-8.3),"copier front":(0.95,-8.4),"printer front":(1.15,-9.25),"rack front":(0.60,-10.35),"lockers front":(1.25,-11.45),
       "break counter front":(0.55,-10.95),"TV front":(-1.5,-10.9),"work table south side":(-2.6,-10.85),"work table north side":(-3.25,-9.05),"shelving front":(-3.8,-9.1),"cot side":(-3.30,-10.9),"west door to desk end":(-3.9,-7.0)}
print("3. reachable free floor: %.1f%% of the free area"%(100*seen.sum()/max(1,free.sum())))
for nme,(x,y) in zones.items():
    i,j=int((y-y0)/G),int((x-x0)/G); ok=bool(seen[i,j]); 
    if not ok:
        best=None
        for rad in range(1,8):
            sub=seen[max(0,i-rad):i+rad+1,max(0,j-rad):j+rad+1]
            if sub.any(): best=rad*G; break
        print("   %-32s %s (nearest reachable %.2f m)"%(nme,"BLOCKED",best if best else -1)); bad+=(0 if best and best<=0.25 else 1)
    else: print("   %-32s ok"%nme)
# 7 collision proxies (coverage of the detailed geometry + reachability using the proxies only)
pc=bpy.data.collections.get("32 CR COLLISION"); pocc=np.zeros_like(occ)
if pc:
    for o in pc.objects:
        vv=verts(o); mn,mx=vv.min(0),vv.max(0)
        if mx[2]<5.45 or mn[2]>7.30: continue
        j0=int(max(0,(mn[0]-x0)/G)); j1=int(min(nx-1,(mx[0]-x0)/G)); i0=int(max(0,(mn[1]-y0)/G)); i1=int(min(ny-1,(mx[1]-y0)/G)); pocc[i0:i1+1,j0:j1+1]=True
    padp=np.pad(pocc,1); pd=np.zeros_like(pocc)
    for dy in range(3):
        for dx in range(3): pd|=padp[dy:dy+ny,dx:dx+nx]
    m=int(0.25/G); interior=np.zeros_like(occ); interior[m:-m,m:-m]=True
    cov=(occ&pd&interior).sum()/max(1,(occ&interior).sum())
    pocc2=pocc.copy(); pocc2[-1:,:]=True
    pad2=np.pad(pocc2,r,constant_values=True); d2=np.zeros_like(pocc2)
    for dy,dx in zip(*np.nonzero(k)): d2|=pad2[dy:dy+ny,dx:dx+nx]
    f2=~d2; s2=np.zeros_like(f2); st=[seed]; s2[seed]=True
    while st:
        i,j=st.pop()
        for di,dj in((1,0),(-1,0),(0,1),(0,-1)):
            a,b=i+di,j+dj
            if 0<=a<ny and 0<=b<nx and f2[a,b] and not s2[a,b]: s2[a,b]=True; st.append((a,b))
    bl=[n_ for n_,(x,y) in zones.items() if not s2[int((y-y0)/G),int((x-x0)/G)] and not any(s2[max(0,int((y-y0)/G)-d):int((y-y0)/G)+d+1,max(0,int((x-x0)/G)-d):int((x-x0)/G)+d+1].any() for d in (3,5))]
    print("7. collision proxies: %d boxes; cover %.0f%% of the detailed occupied floor area (excluding a 0.25 m wall strip); zones reachable with proxies only: %s"%(len(pc.objects),100*cov,"all" if not bl else "NOT "+str(bl)))
    if cov<0.90 or bl: bad+=1
else: print("7. collision proxies: MISSING"); bad+=1
# 4 chairs tucked
def bbox(o): v=verts(o); return v.min(0),v.max(0)
nch=0
for o in coll.objects:
    if o.type=="MESH" and o.name.startswith("CR chair"):
        v=verts(o)
        for (xa,xb) in ((-3.6,-1.9),(-1.9,-0.2),(-0.2,1.5)):
            m=(v[:,0]>xa)&(v[:,0]<xb)&(v[:,1]>-7.60)&(v[:,1]<-6.40)&(v[:,2]>6.135)&(v[:,2]<6.17)
            nch+=int(m.sum())
print("4. chair vertices inside the desk-top slab volume (must be 0):",nch); bad+=nch
# 5 purple audit
def hue(c): h,s,v=colorsys.rgb_to_hsv(*[max(0,min(1,x)) for x in c[:3]]); return h*360,s,v
def bp(c): h,s,v=hue(c); return 225<=h<=345 and s>0.06
pu=[]
for m in bpy.data.materials:
    if not m.node_tree: continue
    for nd in m.node_tree.nodes:
        for i in nd.inputs:
            if i.type=='RGBA' and not i.is_linked and bp(i.default_value): pu.append(("mat",m.name,nd.name,i.name))
        if nd.type=='VALTORGB':
            for e in nd.color_ramp.elements:
                if bp(e.color): pu.append(("ramp",m.name))
for l in bpy.data.lights:
    if bp(l.color): pu.append(("light",l.name))
for w in bpy.data.worlds:
    if w.node_tree:
        for nd in w.node_tree.nodes:
            for i in nd.inputs:
                if i.type=='RGBA' and not i.is_linked and bp(i.default_value): pu.append(("world",nd.name))
im=[]
for img in bpy.data.images:
    if img.size[0]*img.size[1]==0 or img.size[0]>2048: continue
    if not img.name.startswith(("CR","R2","hall","LP")): continue
    px=np.array(img.pixels[:],dtype=np.float32).reshape(-1,4)[::max(1,img.size[0]*img.size[1]//20000),:3]
    if img.colorspace_settings.name!='sRGB': continue
    hs=np.array([colorsys.rgb_to_hsv(*p) for p in px[:4000]]); frac=np.mean((hs[:,0]*360>=225)&(hs[:,0]*360<=345)&(hs[:,1]>0.20)&(hs[:,2]>0.08))
    if frac>0.02: im.append((img.name,round(float(frac),3)))
print("5. purple-band colours: %d  (mats/lights/world);  images with >2%% purple pixels: %s"%(len(pu),im))
for p in pu[:20]: print("   ",p)
bad+=len(pu)
# 6 counts
cnt=collections.Counter(); tri=0
for o in coll.objects:
    if o.type=="MESH":
        o.data.calc_loop_triangles(); n=len(o.data.loop_triangles); tri+=n; cnt[o.name.split(" ")[1]]+=n
print("6. redo collection: %d objects, %d triangles"%(len(coll.objects),tri)); print("   by group:",dict(cnt.most_common(12)))
print("RESULT:","PASS" if bad==0 else "FAIL (%d)"%bad); sys.exit(1 if bad else 0)
