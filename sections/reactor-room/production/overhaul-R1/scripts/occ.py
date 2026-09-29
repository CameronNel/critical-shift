import bpy,sys,math,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath="w41.blend")
CELL=0.25; N=int(22/CELL)
occ=[[0]*N for _ in range(N)]
def ij(x,y): return int((x+11)/CELL),int((y+11)/CELL)
skipc=("22 R2 ARCH","25 LIGHT","RF APPROVED","20 CONTROL","21 ELEVATOR","26 R2 CONTROL")
n=0
for o in bpy.data.objects:
    if o.type not in("MESH","CURVE","FONT"): continue
    c=o.users_collection[0].name if o.users_collection else ""
    if c.startswith(skipc) or o.name.startswith("LP haze"): continue
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]
    z0=min(p.z for p in bb); z1=max(p.z for p in bb)
    if z0>2.6 or z1<0.12: continue
    x0=min(p.x for p in bb);x1=max(p.x for p in bb);y0=min(p.y for p in bb);y1=max(p.y for p in bb)
    if (x1-x0)>4.5 and (y1-y0)>4.5 and c.startswith("23"): continue
    if max(x1-x0,y1-y0)>6.5 and not c.startswith("03"): continue
    if (x1-x0)*(y1-y0)>30 : continue
    i0,j0=ij(x0,y0); i1,j1=ij(x1,y1)
    for i in range(max(0,i0),min(N,i1+1)):
        for j in range(max(0,j0),min(N,j1+1)): occ[i][j]=1
    n+=1
# hard keepouts
def ko(cx,cy,r):
    for i in range(N):
        for j in range(N):
            x=i*CELL-11+CELL/2; y=j*CELL-11+CELL/2
            if (x-cx)**2+(y-cy)**2<r*r: occ[i][j]=2
ko(0,0,4.9)
def rect(x0,x1,y0,y1):
    for i in range(N):
        for j in range(N):
            x=i*CELL-11+CELL/2; y=j*CELL-11+CELL/2
            if x0<=x<=x1 and y0<=y<=y1: occ[i][j]=2
rect(-11,-6.0,-3.9,3.9)      # main access west
rect(-3.4,3.4,7.2,11)        # fuel handling north
rect(6.0,10.8,-10.8,-6.0)    # cooling plant SE
rect(-8.4,-5.2,-8.4,-5.2)    # elevator
rect(-5.2,2.4,-10.9,-5.6)    # control room footprint + zone
json.dump(occ,open("occ.json","w"))
with open("occ.txt","w") as f:
    for j in range(N-1,-1,-1):
        f.write("".join(".#X"[occ[i][j]] for i in range(N))+"\n")
print("occupied objs",n)
