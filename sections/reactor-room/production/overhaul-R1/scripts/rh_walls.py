"""WALLS stage of the reactor-hall pass.   usage: python rh_walls.py -- <in.blend> <out.blend>
Rebuilds collection '22 R2 ARCHITECTURE' (everything except 'R2 floor', the wall graphics and the lamp fixtures), restyles '30 R2 DOOR STUBS',
'02 ROOF STRUCTURE' and 'RF APPROVED SKYLIGHT ROOF', and adds wall mounted small assets.  Own objects are named 'RH walls ...'; own materials 'RH walls ...'.
Design (all in the wall frame u along the wall, v into the hall, h height):
  mass        0.8 m thick cast concrete shell (v -0.8..0) with deep reveals at doors and clerestory windows
  0-0.3       stained plinth, 0.34-0.52 chamfered yellow bumper rail on brackets
  0.3-6.3     weathered cast-in-place concrete: three pours (lifts), running-bond formwork panels, tie holes, patches
  6.3-6.62    steel transom beam (wall step) with orange edge line
  6.62-10.8   dark Audi-grey rainscreen cladding on hat sections, expressed fixings, shadow gaps, acoustic louvre bays, wall fans
  11.0-13.3   clerestory: 0.5 m deep reveal, steel liner, smoky neutral glass, mullions and transom
  13.35-13.7  ring beam on column corbels that carries the roof girders;  13.7-14.4 frieze;  14.4-15 cornice with yellow line
  columns     steel I-sections at every bay: base plate, grout, anchor bolts, gussets, splices, hazard wrap, corbel; corner piers with hazard chevrons
  doors       steel architrave with hazard edge stripes, liner reveals, transfer girder (lintel), threshold, exit sign, door number, red lamp
Small assets are placed against an occupancy grid of everything else on the walls (and the pipe manifest), so they never intersect other builders' objects.
Deterministic and re-runnable.  Palette: weathered concrete, dark Audi grey, safety yellow / orange / red / white.  No teal, cyan, blue or purple."""
import bpy,bmesh,sys,os,math,json,re
import numpy as np
from mathutils import Vector,Matrix
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import crk,rh_mats
from r2lib import WALLS,V
A=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A[0],A[1]
bpy.ops.wm.open_mainfile(filepath=SRC)
sc=bpy.context.scene
MINE=("22 R2 ARCHITECTURE","30 R2 DOOR STUBS","02 ROOF STRUCTURE","RF APPROVED SKYLIGHT ROOF")
KEEP22=("R2 floor","R2 gfx","R2 lights fix")
# ------------------------------------------------------------------ clean own previous output and the old architecture
for o in list(bpy.data.objects):
    cn=o.users_collection[0].name if o.users_collection else ""
    if o.name.startswith("RH walls "): bpy.data.objects.remove(o,do_unlink=True)
    elif cn=="22 R2 ARCHITECTURE" and not o.name.startswith(KEEP22): bpy.data.objects.remove(o,do_unlink=True)
for me in list(bpy.data.meshes):
    if me.users==0: bpy.data.meshes.remove(me)
for cu in list(bpy.data.curves):
    if cu.users==0: bpy.data.curves.remove(cu)
def coll(n):
    c=bpy.data.collections.get(n) or bpy.data.collections.new(n)
    if c.name not in [x.name for x in sc.collection.children]: sc.collection.children.link(c)
    return c
C22=coll("22 R2 ARCHITECTURE"); C02=coll("02 ROOF STRUCTURE"); C30=coll("30 R2 DOOR STUBS")
M=rh_mats.lib()
def own_mat(name,rgb,emit,rough=0.3,base=None,alpha=None):
    m=bpy.data.materials.get(name)
    if m: bpy.data.materials.remove(m)
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; b=nt.nodes["Principled BSDF"]
    b.inputs['Base Color'].default_value=(*(base or [c*0.08 for c in rgb]),1); b.inputs['Roughness'].default_value=rough
    b.inputs['Emission Color'].default_value=(*rgb,1); b.inputs['Emission Strength'].default_value=emit
    return m
# wall-specific brightness variants of the shared recipes (the hall is lit dimly: walls need readable concrete / metal values)
M["CONC"]=rh_mats.surf("RH walls concrete",(0.36,0.35,0.325),0.86,0.0,mottle=0.8,streak=0.6,grime=0.5,scale=1.1,bump=0.05)
M["CONC_POUR"]=rh_mats.surf("RH walls concrete pour",(0.44,0.43,0.40),0.80,0.0,mottle=0.6,streak=0.5,grime=0.35,scale=0.8,bump=0.04)
M["CONC_DARK"]=rh_mats.surf("RH walls concrete plinth",(0.20,0.195,0.185),0.82,0.0,mottle=0.7,streak=0.3,grime=0.7,scale=1.6,bump=0.05)
M["AUDI"]=rh_mats.surf("RH walls audi grey",(0.060,0.064,0.070),0.36,0.65,mottle=0.35,streak=0.12,edge=(0.30,0.31,0.33),grime=0.2,scale=2.0,bump=0.0)
M["AUDI_SATIN"]=rh_mats.surf("RH walls audi satin",(0.105,0.110,0.118),0.50,0.5,mottle=0.45,streak=0.18,edge=(0.34,0.35,0.37),grime=0.25,scale=2.0,bump=0.01)
M["STEEL"]=rh_mats.surf("RH walls steel",(0.085,0.088,0.094),0.48,0.8,mottle=0.4,streak=0.2,edge=(0.36,0.37,0.38),grime=0.3,scale=2.2,bump=0.0)
# smoky neutral glass (opaque dark glass with a faint warm daylight glow, no blue tint); warm caged lamp; amber sign text
M["GLASS"]=own_mat("RH walls glass smoky",(0.80,0.74,0.62),0.14,rough=0.06,base=(0.016,0.016,0.017))
M["LAMP"]=own_mat("RH walls lamp warm",(1.0,0.80,0.52),3.0,rough=0.4,base=(0.5,0.4,0.25))
M["AMBER"]=own_mat("RH walls sign amber",(1.0,0.52,0.10),1.1,rough=0.5,base=(0.4,0.2,0.04))
M["REDLAMP"]=own_mat("RH walls beacon red",(1.0,0.07,0.03),4.0,rough=0.3,base=(0.5,0.03,0.015))
# the shared lavender task-lamp material is blue-grey: make it warm white in place (coordinator audit)
lv=bpy.data.materials.get("R2 lamp lavender")
if lv and lv.node_tree:
    for nd in lv.node_tree.nodes:
        if nd.type=='BSDF_PRINCIPLED':
            nd.inputs['Base Color'].default_value=(0.42,0.36,0.26,1); nd.inputs['Emission Color'].default_value=(1.0,0.84,0.60,1)
# ------------------------------------------------------------------ wall frame helpers
K=crk.Kit()
def pw(w,u,v): p=w.pt(u,v); return p.x,p.y
ENV=(-4.80,2.00,-11.91,-6.16,5.40,8.80)      # control-room envelope (cr_verify.py): nothing of the hall shell may enter it
def in_env(x,y,z,tol=0.0): return ENV[0]+tol<x<ENV[1]-tol and ENV[2]+tol<y<ENV[3]-tol and ENV[4]+tol<z<ENV[5]-tol
W0=WALLS[0]; EU=(ENV[0]-W0.P.x,ENV[1]-W0.P.x); EH=(ENV[4],ENV[5])
def wb(key,w,u0,u1,h0,h1,v0,v1,ch=0.006):
    if u1-u0<1e-4 or h1-h0<1e-4 or v1-v0<1e-4: return
    if w.i==0 and v0<1.0 and u1>EU[0] and u0<EU[1] and h1>EH[0] and h0<EH[1]:
        # carve the control-room envelope out of the box (4 pieces around it)
        if u0<EU[0]: wb(key,w,u0,EU[0],h0,h1,v0,v1,ch)
        if u1>EU[1]: wb(key,w,EU[1],u1,h0,h1,v0,v1,ch)
        a,b=max(u0,EU[0]),min(u1,EU[1])
        if h0<EH[0]: wb(key,w,a,b,h0,EH[0],v0,v1,ch)
        if h1>EH[1]: wb(key,w,a,b,EH[1],h1,v0,v1,ch)
        return
    p=w.pt((u0+u1)/2,(v0+v1)/2); K.box(key,p.x,p.y,h0,h1,u1-u0,v1-v0,w.angle,ch)
def wp(w,u,v,h): p=w.pt(u,v); return (p.x,p.y,h)
def hullw(key,w,pts,ch=0.003):
    """convex hull of (u,v,h) points"""
    if any(in_env(*wp(w,u,v,h)) for (u,v,h) in pts): return
    K.hull(key,[wp(w,u,v,h) for (u,v,h) in pts],ch)
def cylN(key,w,u,h,v0,v1,r,seg=12):            # axis along the wall normal
    if in_env(*wp(w,u,(v0+v1)/2,h)): return
    K.prism(key,wp(w,u,v0,h),wp(w,u,v1,h),r,r,seg)
def cylU(key,w,u0,u1,v,h,r,seg=8):             # axis along the wall
    if in_env(*wp(w,(u0+u1)/2,v,h)): return
    K.prism(key,wp(w,u0,v,h),wp(w,u1,v,h),r,r,seg,0.0,True)
def cylV(key,w,u,v,h0,h1,r,seg=10):            # vertical
    if in_env(*wp(w,u,v,(h0+h1)/2)): return
    K.prism(key,wp(w,u,v,h0),wp(w,u,v,h1),r,r,seg)
def jit(*a):
    h=0
    for x in a: h=(h*1000003+int(round(x*1000)))&0xffffff
    return (h%1000)/1000.0
# ------------------------------------------------------------------ openings, columns, bays
OPEN={1:(3.395,2.8),4:(6.0,2.8),6:(6.0,3.0)}; DOORH=5.0; LINT=5.4
H0,PL,BR0,BR1,CZ,TR1,CL1,WS,WH,RB0,RB1,FR1,CO0,TOP=0,0.30,0.34,0.52,6.30,6.62,10.80,11.0,13.3,13.35,13.70,14.4,14.4,15.0
def door(w): return (OPEN[w.i][0]-OPEN[w.i][1],OPEN[w.i][0]+OPEN[w.i][1]) if w.i in OPEN else None
def wall_cols(w):
    """returns list of (u, kind) kind: 'full' | 'jamb' | 'transfer'"""
    base=[3.0,6.0,9.0] if w.L>10 else [w.L/2]; dr=door(w); out=[]
    if not dr: return [(c,'full') for c in base]
    a,b=dr
    for c in base:
        if abs(c-a)<0.45 or abs(c-b)<0.45: continue
        out.append((c,'transfer' if a<c<b else 'full'))
    if a-0.30>0.9: out.append((a-0.30,'jamb'))
    if b+0.30<w.L-0.9: out.append((b+0.30,'jamb'))
    return sorted(out)
WCOLS={w.i:wall_cols(w) for w in WALLS}
def edges(w): return [0.0]+[c for c,_ in WCOLS[w.i]]+[w.L]
def bay_ranges(w,pier=0.62,colh=0.22):
    e=edges(w); out=[]
    for i in range(len(e)-1):
        a=e[i]+(pier if i==0 else colh); b=e[i+1]-(pier if i==len(e)-2 else colh)
        if b-a>0.25: out.append((a,b))
    return out
def spans_below(w,a,b,h):
    """split [a,b] around the door opening when the zone is below h (door height)"""
    dr=door(w)
    if not dr or h>LINT: return [(a,b)]
    out=[]
    if a<dr[0]: out.append((a,min(b,dr[0])))
    if b>dr[1]: out.append((max(a,dr[1]),b))
    return [s for s in out if s[1]-s[0]>0.12]
# ------------------------------------------------------------------ occupancy of everything that is not mine (so small assets never collide)
CELL=0.1; OCC={}
for w in WALLS: OCC[w.i]=np.full((int(math.ceil(w.L/CELL))+2,int(TOP/CELL)+2),9.0,dtype=np.float32)
def build_occ():
    dg=bpy.context.evaluated_depsgraph_get()
    for o in bpy.data.objects:
        if o.type!='MESH' or o.hide_render: continue
        cn=o.users_collection[0].name if o.users_collection else ""
        if cn in MINE or o.name.startswith(KEEP22[1:]) or o.name.startswith("RH walls "): continue
        if cn.startswith(("10 CAM","LP ")) or o.name.startswith(("LP haze","Water","Deep water")): continue
        me=o.data; n=len(me.vertices)
        if n==0: continue
        co=np.empty(n*3,dtype=np.float64); me.vertices.foreach_get('co',co); co=co.reshape(n,3)
        Mw=np.array(o.matrix_world); wco=co@Mw[:3,:3].T+Mw[:3,3]
        me.calc_loop_triangles(); nt=len(me.loop_triangles)
        if nt==0: continue
        tri=np.empty(nt*3,dtype=np.int64); me.loop_triangles.foreach_get('vertices',tri); tri=tri.reshape(nt,3)
        zmin,zmax=wco[:,2].min(),wco[:,2].max()
        if zmin>TOP: continue
        for w in WALLS:
            rel=wco[:,:2]-np.array([w.P.x,w.P.y]); u=rel@np.array([w.t.x,w.t.y]); v=rel@np.array([w.n.x,w.n.y]); h=wco[:,2]
            if v.max()<0.0 or v.min()>1.3 or u.max()<-0.2 or u.min()>w.L+0.2: continue
            tu=u[tri]; tv=v[tri]; th=h[tri]
            vmin=tv.min(1); vmax=tv.max(1); hmin=th.min(1); hmax=th.max(1)
            sel=(vmax>0.006)&(vmin<1.3)&~((hmax-hmin<0.03)&(hmax<0.08))&(tu.max(1)>0)&(tu.min(1)<w.L)
            for k in np.nonzero(sel)[0]:
                iu0=max(0,int(tu[k].min()/CELL)); iu1=min(OCC[w.i].shape[0]-1,int(tu[k].max()/CELL))
                ih0=max(0,int(th[k].min()/CELL)); ih1=min(OCC[w.i].shape[1]-1,int(th[k].max()/CELL))
                sub=OCC[w.i][iu0:iu1+1,ih0:ih1+1]; np.minimum(sub,max(vmin[k],0.0),out=sub)
    # pipe runs: manifest polylines (services builder will re-route them but ports are fixed)
    mf=os.path.join(HERE,"..","piping_runs_generated.json")
    if os.path.exists(mf):
        for r in json.load(open(mf)):
            pts=[Vector(p) for p in r["pts"]]; rad=r["r"]
            for a,b in zip(pts,pts[1:]):
                L=(b-a).length
                for s in range(int(L/0.08)+2):
                    p=a+(b-a)*min(1.0,s*0.08/max(L,1e-6))
                    for w in WALLS:
                        rel=Vector((p.x,p.y))-w.P; u=rel.dot(w.t); v=rel.dot(w.n)
                        if not(-0.3<v<1.5 and 0<u<w.L): continue
                        q=rad+0.10; iu0=max(0,int((u-q)/CELL)); iu1=min(OCC[w.i].shape[0]-1,int((u+q)/CELL)); ih0=max(0,int((p.z-q)/CELL)); ih1=min(OCC[w.i].shape[1]-1,int((p.z+q)/CELL))
                        sub=OCC[w.i][iu0:iu1+1,ih0:ih1+1]; np.minimum(sub,max(v-rad,0.0),out=sub)
build_occ()
OCC[0][int(EU[0]/CELL):int(EU[1]/CELL)+1,int(EH[0]/CELL):int(EH[1]/CELL)+1]=0.0
if os.environ.get('RHW_DUMP'): np.savez(os.environ['RHW_DUMP'],**{str(k):v for k,v in OCC.items()})
def free(w,u0,u1,h0,h1,d,pad=0.03):
    g=OCC[w.i]; iu0=max(0,int((u0)/CELL)); iu1=min(g.shape[0]-1,int((u1)/CELL)); ih0=max(0,int(h0/CELL)); ih1=min(g.shape[1]-1,int(h1/CELL))
    if iu1<iu0 or ih1<ih0: return False
    return float(g[iu0:iu1+1,ih0:ih1+1].min())>=d+pad
def claim(w,u0,u1,h0,h1):
    g=OCC[w.i]; iu0=max(0,int(u0/CELL)); iu1=min(g.shape[0]-1,int(u1/CELL)); ih0=max(0,int(h0/CELL)); ih1=min(g.shape[1]-1,int(h1/CELL))
    g[iu0:iu1+1,ih0:ih1+1]=0.0
def segs(w,u0,u1,h0,h1,d,step=0.25,minlen=0.4):
    """contiguous free sub-ranges of [u0,u1] for an element that sticks out by d"""
    out=[]; cur=None; u=u0
    while u<u1-1e-6:
        e=min(u1,u+step)
        if free(w,u,e,h0,h1,d):
            cur=(cur[0] if cur else u,e)
        else:
            if cur and cur[1]-cur[0]>=minlen: out.append(cur)
            cur=None
        u=e
    if cur and cur[1]-cur[0]>=minlen: out.append(cur)
    return out
SKIPPED={"asset":0,"beam":0}
# ------------------------------------------------------------------ text (curve -> mesh -> merged into the kit)
def text(key,w,body,u,h,v,size,extrude=0.004,spacing=1.0,align='CENTER',yaw_flip=False):
    cu=bpy.data.curves.new("rhw_t",'FONT'); cu.body=body; cu.size=size; cu.align_x=align; cu.align_y='CENTER'; cu.extrude=extrude; cu.resolution_u=2; cu.space_character=spacing
    ob=bpy.data.objects.new("rhw_t",cu); sc.collection.objects.link(ob); bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get(); me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    t=Vector((-w.t.x,-w.t.y,0)); up=Vector((0,0,1)); n=Vector((w.n.x,w.n.y,0))
    Mx=Matrix(((t.x,up.x,n.x,0),(t.y,up.y,n.y,0),(t.z,up.z,n.z,0),(0,0,0,1)))
    p=w.pt(u,v); T=Matrix.Translation((p.x,p.y,h))@Mx
    bm=K.get(key); vm={}
    for vt in me.vertices: vm[vt.index]=bm.verts.new(T@vt.co)
    for pl in me.polygons:
        try: bm.faces.new([vm[i] for i in pl.vertices])
        except Exception: pass
    bpy.data.objects.remove(ob); bpy.data.curves.remove(cu); bpy.data.meshes.remove(me)
# ================================================================== STRUCTURE
def mass(w):
    """0.8 m thick concrete shell with openings for doors and clerestory windows"""
    key=("mass","CONC_DARK")
    for (a,b) in bay_ranges(w,pier=0.0,colh=0.0):
        for (s0,s1) in spans_below(w,a,b,0): pass
    e=edges(w); dr=door(w)
    wins=[(x+(0.7 if i==0 else 0.5),y-(0.7 if i==len(e)-2 else 0.5)) for i,(x,y) in enumerate(zip(e[:-1],e[1:]))]
    w.wins=[s for s in wins if s[1]-s[0]>0.8]
    # below the clerestory: split around the door
    lo=[(0.0,w.L)]
    if dr: lo=[(0.0,dr[0]),(dr[1],w.L)]
    for (a,b) in lo:
        if b-a>0.02: wb(key,w,a,b,0,WS,-0.8,-0.02,0)
    if dr: wb(key,w,dr[0],dr[1],LINT,WS,-0.8,-0.02,0)
    # window level: piers between openings
    pts=[0.0]
    for (a,b) in w.wins: pts+= [a,b]
    pts.append(w.L)
    for i in range(0,len(pts),2):
        if pts[i+1]-pts[i]>0.02: wb(key,w,pts[i],pts[i+1],WS,WH,-0.8,-0.02,0)
    wb(key,w,0,w.L,WH,TOP,-0.8,-0.02,0)
    # clerestory reveal: liner steel, glass, bars
    for (a,b) in w.wins:
        for (x0,x1) in ((a,a+0.03),(b-0.03,b)): wb(("window","AUDI_SATIN"),w,x0,x1,WS,WH,-0.50,0.0,0.002)       # jamb liners
        wb(("window","AUDI_SATIN"),w,a,b,WH-0.03,WH,-0.50,0.0,0.002)                                              # head liner
        wb(("window","AUDI_SATIN"),w,a-0.03,b+0.03,WS,WS+0.04,-0.50,0.24,0.012)                                   # projecting sill
        wb(("window","AUDI_SATIN"),w,a-0.03,b+0.03,WS+0.04,WS+0.055,0.22,0.25,0.003)                              # sill lip
        wb(("window","GLASS"),w,a,b,WS+0.04,WH-0.03,-0.47,-0.455,0)
        n=max(2,int(round((b-a)/0.95))); wdt=(b-a)/n
        for k in range(n+1):
            x=a+k*wdt; wb(("window","AUDI_SATIN"),w,x-0.035,x+0.035,WS+0.04,WH-0.03,-0.50,-0.40,0.004)
        tz=WS+0.04+(WH-0.03-WS-0.04)*0.62
        wb(("window","AUDI_SATIN"),w,a,b,tz-0.03,tz+0.03,-0.50,-0.40,0.004)
        wb(("window","AUDI_SATIN"),w,a,b,WS+0.04,WS+0.09,-0.50,-0.40,0.004)
        # vent opener box on the transom of alternate panes
        for k in range(n):
            if (k+w.i)%3==0: wb(("window","STEEL"),w,a+k*wdt+wdt/2-0.12,a+k*wdt+wdt/2+0.12,tz+0.06,tz+0.14,-0.46,-0.36,0.004)
    # pier faces up the window storey: concrete stand-off panels with shadow joints
    for i in range(0,len(pts),2):
        a,b=pts[i],pts[i+1]
        if b-a>0.1: wb(("concrete","CONC_POUR"),w,a,b,WS,WH,-0.02,0.0,0.004)
def lower_concrete(w):
    """plinth, bumper rail, three pours of running-bond formwork panels, tie holes, patches"""
    for (a,b) in bay_ranges(w,pier=0.55):
        for (s0,s1) in spans_below(w,a,b,0):
            # plinth
            if s1-s0>0.1:
                hullw(("concrete","CONC_DARK"),w,[(u,v,h) for u in (s0+0.01,s1-0.01) for (v,h) in ((-0.02,0),(0.075,0),(0.075,PL-0.05),(0.045,PL),(-0.02,PL))],0.0)
            # bumper rail on brackets (only where free)
            for (r0,r1) in segs(w,s0+0.06,s1-0.06,BR0,BR1,0.12,minlen=0.6):
                hullw(("trim","YELLOW"),w,[(u,v,h) for u in (r0,r1) for (v,h) in ((0.045,BR0),(0.115,BR0+0.035),(0.115,BR1-0.035),(0.045,BR1))],0.004)
                for x in (r0+0.03,(r0+r1)/2,r1-0.03):
                    wb(("trim","STEEL"),w,x-0.04,x+0.04,BR0+0.02,BR1-0.02,0.0,0.05,0.003)
                for x in np.arange(r0+0.2,r1-0.1,0.55): wb(("trim","BLACK"),w,x,x+0.07,BR0+0.075,BR1-0.075,0.1148,0.118,0.0)
            # concrete lifts
            lifts=[(PL,2.4),(2.4,4.8),(4.8,CZ)]
            for ri,(h0,h1) in enumerate(lifts):
                ua=s0; wd=1.38+0.2*jit(w.i,ri)
                first=wd*(0.55 if ri%2 else 1.0)
                cuts=[]; x=ua+first
                while x<s1-0.5: cuts.append(x); x+=wd
                P=[ua]+cuts+[s1]
                for pi in range(len(P)-1):
                    pa,pb=P[pi],P[pi+1]; j=jit(w.i,ri,pi,s0)
                    mk="CONC" if j<0.58 else "CONC_POUR"
                    dep=0.0 if j<0.7 else 0.012
                    # panel stops short under the transom, above bumper rail
                    hh0=h0+(0.0 if ri else 0.0);
                    wb(("concrete",mk),w,pa+0.008,pb-0.008,hh0+0.008,h1-0.008,-0.02,dep+0.0001,0.0035)
                    # tie holes: 2 rows x (panel width / 0.6)
                    nx=max(1,int((pb-pa)/0.65));
                    for kk in range(nx+1):
                        tu=pa+0.22+kk*((pb-pa-0.44)/max(nx,1))
                        for fr in (0.27,0.73):
                            th=hh0+(h1-hh0)*fr
                            if th<BR1+0.05 and tu>0: pass
                            if free(w,tu-0.03,tu+0.03,th-0.03,th+0.03,0.0,0.0):
                                cylN(("concrete","BLACK"),w,tu,th,dep-0.0005,dep+0.004,0.021,8)
                                cylN(("concrete","CONC_DARK"),w,tu,th,dep-0.001,dep+0.002,0.034,10)
                    # occasional repair patch
                    if jit(w.i,ri,pi,3)>0.82 and pb-pa>1.0:
                        pu=pa+0.3+0.4*jit(pi,ri,w.i); ph=h0+0.4+0.9*jit(ri,pi)
                        wb(("concrete","CONC_POUR"),w,pu,pu+0.55,ph,ph+0.42,dep,dep+0.012,0.004)
    # door spandrel: concrete over the opening
    dr=door(w)
    if dr:
        wb(("concrete","CONC"),w,dr[0]-0.02,dr[1]+0.02,LINT+0.0,CZ,-0.02,0.0001,0.004)
def transom_and_cladding(w):
    # transom beam ("wall step")
    for _ in (0,):
        for (s0,s1) in segs(w,0.5,w.L-0.5,CZ,TR1,0.30,step=0.25,minlen=0.3):
            wb(("steel","AUDI"),w,s0,s1,CZ,TR1,0.0,0.30,0.012)
            wb(("trim","ORANGE"),w,s0,s1,CZ+0.015,CZ+0.060,0.30,0.302,0.0)
            wb(("steel","STEEL"),w,s0,s1,TR1,TR1+0.04,0.0,0.34,0.005)
    SKIPPED["beam"]+=0
    # cladding on hat sections
    for bi,(a,b) in enumerate(bay_ranges(w,pier=0.55)):
        n=max(2,int(round((b-a)/1.35))); wdt=(b-a)/n
        kind=(w.i*3+bi)%4      # 0 solid, 1 louvre lower, 2 solid + zone panel, 3 louvre upper
        for k in range(n+1):
            x=a+k*wdt
            wb(("steel","STEEL"),w,x-0.035,x+0.035,TR1+0.0,CL1,0.0,0.075,0.004)
        tiers=[(TR1+0.03,8.70),(8.74,CL1-0.03)]
        for ti,(h0,h1) in enumerate(tiers):
            for k in range(n):
                ua=a+k*wdt+0.04; ub=a+(k+1)*wdt-0.04
                louv=(kind==1 and ti==0 and k==n//2) or (kind==3 and ti==1 and k==n//2)
                dep=0.115 if free(w,ua,ub,h0,h1,0.12) else 0.06
                if louv:
                    wb(("steel","STEEL"),w,ua,ub,h0,h1,0.075,0.16,0.006)               # louvre frame
                    wb(("steel","BLACK"),w,ua+0.05,ub-0.05,h0+0.05,h1-0.05,0.0,0.08,0)
                    ns=int((h1-h0-0.1)/0.115)
                    for s in range(ns):
                        hz=h0+0.07+s*0.115
                        hullw(("steel","AUDI"),w,[(u,v,h) for u in (ua+0.04,ub-0.04) for (v,h) in ((0.085,hz+0.085),(0.15,hz),(0.15,hz+0.018),(0.085,hz+0.103))],0.0)
                    continue
                mk="AUDI" if (k+ti+bi)%3 else "AUDI_SATIN"
                wb(("cladding",mk),w,ua,ub,h0,h1,0.065,dep,0.008)
                # expressed fixings
                for fx in (ua+0.07,ub-0.07):
                    for fh in (h0+0.07,(h0+h1)/2,h1-0.07):
                        cylN(("cladding","GALV"),w,fx,fh,dep-0.001,dep+0.008,0.012,6)
        # batten / drip flashing between tiers
        wb(("steel","STEEL"),w,a-0.02,b+0.02,8.70,8.74,0.0,0.14,0.003)
def frieze_cornice(w):
    wb(("concrete","CONC_POUR"),w,0.0,w.L,RB1,FR1,-0.02,0.04,0.006)
    wb(("trim","ORANGE"),w,0.0,w.L,14.28,14.36,0.04,0.045,0.0)
    # ring beam on the corbels (the girders bear on it); gaps where other things (crane rails) are
    for (s0,s1) in segs(w,0.5,w.L-0.5,RB0,RB1,0.45,step=0.25,minlen=0.5):
        wb(("steel","STEEL"),w,s0,s1,RB0,RB1,0.0,0.45,0.012)
        wb(("trim","YELLOW"),w,s0,s1,RB0+0.02,RB0+0.07,0.45,0.452,0.0)
    # cornice: sloped steel hood with drip lip and a yellow safety line
    for (s0,s1) in [(0.0,w.L)]:
        hullw(("steel","AUDI"),w,[(u,v,h) for u in (s0+0.01,s1-0.01) for (v,h) in ((-0.02,CO0),(0.34,CO0),(0.38,CO0+0.08),(0.12,TOP-0.02),(-0.02,TOP))],0.006)
        wb(("trim","YELLOW"),w,s0,s1,CO0+0.02,CO0+0.07,0.338,0.342,0.0)
def column(w,u,kind):
    base=0.0 if kind!='transfer' else LINT
    h0=base+0.15 if kind!='transfer' else LINT; top=RB1
    big=1.0 if kind!='jamb' else 1.25
    fw=0.20*big; wt=0.03
    if kind!='transfer':
        # grout pedestal, base plate, anchor bolts, gussets
        wb(("concrete","CONC_DARK"),w,u-0.30,u+0.30,0,0.12,-0.02,0.50,0.01)
        wb(("steel","STEEL"),w,u-0.27,u+0.27,0.12,0.15,0.02,0.44,0.004)
        for du in (-0.22,0.22):
            for dv in (0.07,0.39):
                cylV(("steel","GALV"),w,u+du,dv,0.15,0.19,0.012,6); cylV(("steel","GALV"),w,u+du,dv,0.15,0.168,0.021,6)
    else:
        wb(("steel","STEEL"),w,u-0.27,u+0.27,LINT,LINT+0.03,0.02,0.44,0.004)
        for du in (-0.22,0.22):
            for dv in (0.07,0.39): cylV(("steel","GALV"),w,u+du,dv,LINT+0.03,LINT+0.066,0.014,6)
    # I-section: web perpendicular to the wall, front flange, wall-side flange
    y0=h0
    wb(("steel","STEEL"),w,u-wt,u+wt,y0,top,0.0,0.30,0.004)
    wb(("steel","STEEL"),w,u-fw,u+fw,y0,top,0.30,0.35,0.004)
    wb(("steel","STEEL"),w,u-fw,u+fw,y0,top,0.0,0.04,0.004)
    # stiffeners / gussets at the base
    if kind!='transfer':
        for sg in (-1,1):
            hullw(("steel","STEEL"),w,[(u+sg*(wt+0.002),0.04,0.15),(u+sg*(wt+0.002),0.34,0.15),(u+sg*(wt+0.002),0.34,0.55),(u+sg*(wt+0.002),0.04,0.34),(u+sg*(wt+0.022),0.04,0.15),(u+sg*(wt+0.022),0.34,0.15),(u+sg*(wt+0.022),0.34,0.55),(u+sg*(wt+0.022),0.04,0.34)],0.0)
        # hazard wrap + yellow band + guard plate
        wb(("trim","HAZARD"),w,u-fw-0.004,u+fw+0.004,0.55,1.35,0.295,0.356,0.004)
        wb(("trim","YELLOW"),w,u-fw-0.004,u+fw+0.004,1.35,1.52,0.295,0.356,0.004)
        wb(("steel","STEEL"),w,u-fw-0.004,u+fw+0.004,0.15,0.55,0.295,0.356,0.006)
    # splice plates + bolts at the transom, mid cladding and under the ring beam
    for zs in ([CZ+0.3,9.3] if kind!='transfer' else [9.3]):
        wb(("steel","GALV"),w,u-fw-0.01,u+fw+0.01,zs-0.22,zs+0.22,0.35,0.37,0.004)
        for du in (-fw*0.6,fw*0.6):
            for dz in (-0.14,0,0.14): cylN(("steel","GALV"),w,u+du,zs+dz,0.37,0.388,0.014,6)
    # stitch plate for the window
    # corbel under the ring beam + cap
    hullw(("steel","STEEL"),w,[(u-0.17,0.35,WH-0.05),(u+0.17,0.35,WH-0.05),(u-0.17,0.55,RB0),(u+0.17,0.55,RB0),(u-0.17,0.35,RB0),(u+0.17,0.35,RB0),(u-0.17,0.50,RB0-0.30),(u+0.17,0.50,RB0-0.30)],0.004)
    wb(("steel","STEEL"),w,u-0.24,u+0.24,RB0-0.01,RB0+0.0,0.0,0.55,0.0)
    # orange edge line on the flange
    wb(("trim","ORANGE"),w,u-0.004-fw*0.2,u+fw*0.2+0.004,2.1,WH-0.35,0.35,0.352,0.0)
def corner_pier(i):
    v0=Vector(V[i]); a=WALLS[i]; b=WALLS[i-1]; bis=(a.n+b.n).normalized(); ang=math.atan2(bis.y,bis.x); p=v0+bis*0.30
    def bx(key,z0,z1,s,ch=0.012,dx=0.0): K.box(key,p.x,p.y,z0,z1,s,s,ang,ch)
    bx(("concrete","CONC_DARK"),0,0.16,0.88,0.02)
    bx(("steel","STEEL"),0.16,0.19,0.74,0.004)
    for sx in (-1,1):
        for sy in (-1,1):
            q=Vector((sx*0.30,sy*0.30)); c,s=math.cos(ang),math.sin(ang)
            X=p.x+q.x*c-q.y*s; Y=p.y+q.x*s+q.y*c; K.prism(("steel","GALV"),(X,Y,0.19),(X,Y,0.225),0.014,0.014,6)
    # lower: hazard wrapped plinth with chamfers, then painted steel casing
    bx(("trim","HAZARD"),0.19,1.40,0.64,0.03)
    bx(("trim","YELLOW"),1.40,1.58,0.66,0.012)
    bx(("steel","AUDI"),1.58,CZ,0.60,0.015)
    bx(("steel","STEEL"),CZ,CZ+0.14,0.66,0.012)           # collar
    bx(("steel","AUDI"),CZ+0.14,10.8,0.60,0.015)
    bx(("steel","STEEL"),10.8,10.94,0.66,0.012)
    bx(("steel","AUDI"),10.94,RB1,0.60,0.015)
    bx(("steel","STEEL"),RB1,FR1,0.72,0.02)
def door_frame(w):
    c,h=OPEN[w.i]; a,b=c-h,c+h; v0=-0.80
    for (x0,x1,sg) in ((a-0.30,a,-1),(b,b+0.30,1)):
        x0=max(x0,0.70) if sg<0 else x0; x1=min(x1,w.L-0.70) if sg>0 else x1
        if x1-x0<0.05: continue
        # architrave: steel jamb with hazard stripe edging and a kick/corner guard
        wb(("doors","AUDI"),w,x0,x1,0,LINT,0.0,0.07,0.01)
        e0,e1=(x1-0.09,x1) if sg<0 else (x0,x0+0.09)
        wb(("doors","HAZARD"),w,e0,e1,0.0,DOORH,0.07,0.074,0.0)
        kk=(x1-0.13,x1) if sg<0 else (x0,x0+0.13)
        wb(("doors","STEEL"),w,kk[0],kk[1],0.0,0.9,0.07,0.12,0.012)          # kick / corner plate
        for z in (0.2,0.45,0.7):
            cylN(("doors","GALV"),w,(kk[0]+kk[1])/2,z,0.12,0.128,0.012,6)
    # reveal liners in the 0.8 m deep opening
    for (x0,x1) in ((a-0.03,a+0.012),(b-0.012,b+0.03)):
        wb(("doors","AUDI_SATIN"),w,x0,x1,0.0,DOORH,v0,0.0,0.0)
    wb(("doors","AUDI_SATIN"),w,a,b,DOORH-0.03,DOORH,v0,0.0,0.0)
    # transfer girder (lintel) with stiffeners, bolts, orange line
    wb(("doors","STEEL"),w,a-0.30,b+0.30,DOORH,LINT,-0.05,0.16,0.01)
    wb(("doors","AUDI"),w,a-0.30,b+0.30,DOORH-0.03,DOORH,0.0,0.16,0.004)
    wb(("doors","ORANGE"),w,a-0.30,b+0.30,DOORH+0.03,DOORH+0.06,0.16,0.162,0.0)
    for x in np.arange(a-0.2,b+0.25,0.62): wb(("doors","STEEL"),w,x-0.012,x+0.012,DOORH+0.07,LINT-0.04,0.16,0.19,0.0)
    # threshold: steel plate with chamfered nosings and a hazard strip
    hullw(("doors","STEEL"),w,[(u,v,h) for u in (a,b) for (v,h) in ((-0.8,0),(0.5,0),(0.5,0.015),(0.40,0.026),(-0.8,0.026))],0.0)
    wb(("doors","HAZARD"),w,a+0.04,b-0.04,0.0258,0.0262,0.28,0.50,0.0)
    # door number plate on the right jamb, red beacon + exit sign over the lintel
    wb(("doors","AUDI"),w,c-0.9,c+0.9,LINT+0.14,LINT+0.55,0.0,0.05,0.008)
    wb(("doors","ORANGE"),w,c-0.9,c+0.9,LINT+0.14,LINT+0.16,0.05,0.055,0.0)
def roof_girders():
    key_s=("girders","STEEL")
    def girder(p0,p1,z,tag):
        d=p1-p0; L=d.length; t=d/L; nrm=Vector((-t.y,t.x)); c=(p0+p1)/2; ang=math.atan2(t.y,t.x)
        K.box(key_s,c.x,c.y,z,z+0.07,L,0.42,ang,0.008); K.box(key_s,c.x,c.y,z+0.63,z+0.70,L,0.42,ang,0.008); K.box(key_s,c.x,c.y,z+0.07,z+0.63,L,0.035,ang,0.0)
        k=int(L/1.2)
        for i in range(k+1):
            s=-L/2+0.4+i*(L-0.8)/k; q=c+t*s
            K.box(("girders","STEEL"),q.x,q.y,z+0.07,z+0.63,0.03,0.30,ang,0.0)
        # end plates and bearing seats on the ring beam
        for e,sg in ((p0,1),(p1,-1)):
            q=e+t*sg*0.02
            K.box(("girders","STEEL"),q.x,q.y,z-0.02,z+0.72,0.02,0.46,ang,0.004)
            for dz in (0.1,0.6):
                for dn in (-0.14,0.14):
                    qq=q+t*sg*0.0+nrm*dn; K.prism(("girders","GALV"),(qq.x,qq.y,z+dz),(qq.x-t.x*sg*0.03,qq.y-t.y*sg*0.03,z+dz),0.015,0.015,6)
            K.box(("girders","GALV"),(e+t*sg*0.14).x,(e+t*sg*0.14).y,z-0.04,z,0.28,0.30,ang,0.004)
        # orange stripe on the lower flange edge
        K.box(("girders","ORANGE"),c.x,c.y,z+0.07,z+0.075,L-0.8,0.425,ang,0.0)
    def octa_hit(p,d):
        best=None
        for w in WALLS:
            den=d.dot(Vector((w.t.y,-w.t.x)))
            if abs(den)<1e-9: continue
            tt=(w.P-p).dot(Vector((w.t.y,-w.t.x)))/den
            q=p+d*tt; u=(q-w.P).dot(w.t)
            if tt>0 and -0.01<=u<=w.L+0.01: best=tt if best is None else min(best,tt)
        return best
    for x in (-7.5,-3.6,3.6,7.5):
        p=Vector((x,0)); a=octa_hit(p,Vector((0,1))); b=octa_hit(p,Vector((0,-1)))
        girder(Vector((x,-b+0.12)),Vector((x,a-0.12)),13.7,"x")
    for y in (-6.0,6.0):
        p=Vector((0,y)); a=octa_hit(p,Vector((1,0))); b=octa_hit(p,Vector((-1,0)))
        girder(Vector((-b+0.12,y)),Vector((a-0.12,y)),13.85,"y")
    # corbel packers lifting the y girders onto the ring beam
# ================================================================== SMALL ASSETS
PLACED=[]
def try_place(fn,w,u,h,hw,h0,h1,d,nudges=(0,0.35,-0.35,0.7,-0.7,1.05,-1.05),name=""):
    """place an asset whose footprint is [u-hw,u+hw] x [h0,h1] (relative to h) sticking out by d; nudge sideways until free"""
    for dn in nudges:
        uu=u+dn
        if uu-hw<0.6 or uu+hw>w.L-0.6: continue
        if free(w,uu-hw,uu+hw,h+h0,h+h1,d):
            fn(w,uu,h); claim(w,uu-hw-0.04,uu+hw+0.04,h+h0-0.04,h+h1+0.04); PLACED.append((name,w.i,round(uu,2),h)); return True
    SKIPPED["asset"]+=1; SKIPPED.setdefault(name,0); SKIPPED[name]+=1; return False
def a_cabinet(w,u,h):
    wb(("assets","RED"),w,u-0.26,u+0.26,h,h+0.74,0.0,0.22,0.012)
    wb(("assets","BLACK"),w,u-0.20,u+0.20,h+0.07,h+0.60,0.22,0.226,0.0)         # glass panel
    cylV(("assets","WHITE"),w,u-0.07,0.223,h+0.12,h+0.58,0.045,8); cylV(("assets","BLACK"),w,u+0.07,0.223,h+0.12,h+0.40,0.03,8)
    wb(("assets","WHITE"),w,u-0.22,u+0.22,h+0.62,h+0.71,0.22,0.224,0.0)
    wb(("assets","GALV"),w,u+0.21,u+0.235,h+0.30,h+0.42,0.22,0.24,0.004)
    wb(("assets","WHITE"),w,u-0.16,u+0.16,h+0.86,h+1.16,0.0,0.012,0.003)       # sign above
    hullw(("assets","RED"),w,[(u+x,0.013,h+1.01+y) for (x,y) in ((0,0.11),(0.11,0),(0,-0.11),(-0.11,0))]+[(u+x,0.02,h+1.01+y) for (x,y) in ((0,0.11),(0.11,0),(0,-0.11),(-0.11,0))],0.0)
def a_firstaid(w,u,h):
    wb(("assets","WHITE"),w,u-0.24,u+0.24,h,h+0.48,0.0,0.15,0.012)
    wb(("assets","RED"),w,u-0.15,u+0.15,h+0.19,h+0.29,0.15,0.156,0.0); wb(("assets","RED"),w,u-0.05,u+0.05,h+0.09,h+0.39,0.15,0.156,0.0)
    wb(("assets","GALV"),w,u+0.22,u+0.245,h+0.20,h+0.30,0.15,0.17,0.004)
    wb(("assets","WHITE"),w,u-0.15,u+0.15,h+0.60,h+0.82,0.0,0.012,0.003); wb(("assets","RED"),w,u-0.13,u+0.13,h+0.69,h+0.73,0.012,0.015,0.0)
def a_eyewash(w,u,h):
    wb(("assets","YELLOW"),w,u-0.22,u+0.22,h+0.1,h+0.80,0.0,0.05,0.008)
    wb(("assets","YELLOW"),w,u-0.22,u+0.22,h+0.1,h+0.30,0.05,0.30,0.02)
    for du in (-0.09,0.09):
        K.prism(("assets","BLACK"),wp(w,u+du,0.29,h+0.30),wp(w,u+du,0.30,h+0.38),0.075,0.095,12)
        cylV(("assets","GALV"),w,u+du,0.22,h+0.30,h+0.40,0.012,6)
    wb(("assets","RED"),w,u-0.03,u+0.03,h+0.37,h+0.42,0.20,0.30,0.004)             # push paddle
    wb(("assets","WHITE"),w,u-0.18,u+0.18,h+0.92,h+1.16,0.0,0.012,0.003); wb(("assets","BLACK"),w,u-0.14,u+0.14,h+0.99,h+1.09,0.012,0.014,0.0)
def a_hosereel(w,u,h):
    wb(("assets","STEEL"),w,u-0.40,u+0.40,h-0.40,h+0.40,0.0,0.04,0.01)
    cylN(("assets","RED"),w,u,h,0.04,0.26,0.36,24); cylN(("assets","STEEL"),w,u,h,0.26,0.28,0.38,24)
    cylN(("assets","BLACK"),w,u,h,0.06,0.24,0.30,24); cylN(("assets","RED"),w,u,h,0.04,0.275,0.12,16)
    cylN(("assets","BRASS"),w,u,h,0.275,0.31,0.05,10)
    K.prism(("assets","BRASS"),wp(w,u+0.30,0.12,h-0.43),wp(w,u+0.30,0.12,h-0.30),0.02,0.03,8)
    wb(("assets","RED"),w,u+0.26,u+0.42,h-0.46,h-0.40,0.0,0.18,0.004)
def a_junction(w,u,h):
    wb(("assets","GALV"),w,u-0.22,u+0.22,h,h+0.46,0.0,0.16,0.012)
    wb(("assets","STEEL"),w,u-0.19,u+0.19,h+0.02,h+0.44,0.16,0.172,0.004)
    for (x,z) in ((-0.17,0.04),(0.17,0.04),(-0.17,0.42),(0.17,0.42)): cylN(("assets","STEEL"),w,u+x,h+z,0.172,0.182,0.012,6)
    wb(("assets","YELLOW"),w,u-0.07,u+0.07,h+0.30,h+0.38,0.172,0.174,0.0)
    hullw(("assets","YELLOW"),w,[(u-0.04,0.174,h+0.37),(u+0.04,0.174,h+0.37),(u,0.174,h+0.31)]+[(u-0.04,0.176,h+0.37),(u+0.04,0.176,h+0.37),(u,0.176,h+0.31)],0.0)
    cylV(("assets","BLACK"),w,u+0.08,0.08,h-0.14,h,0.018,8); cylV(("assets","BLACK"),w,u-0.08,0.08,h-0.14,h,0.018,8)
def a_conduit_run(w,u0,u1,h):
    """two junction boxes joined by a clipped conduit"""
    a_junction(w,u0,h-0.23); a_junction(w,u1,h-0.23)
    cylU(("assets","GALV"),w,u0+0.22,u1-0.22,0.075,h,0.017,8)
    x=u0+0.4
    while x<u1-0.3:
        wb(("assets","STEEL"),w,x-0.02,x+0.02,h-0.03,h+0.03,0.0,0.056,0.002); wb(("assets","STEEL"),w,x-0.02,x+0.02,h-0.03,h+0.03,0.056,0.092,0.003); x+=0.5
def a_lamp(w,u,h):
    wb(("assets","GALV"),w,u-0.10,u+0.10,h-0.10,h+0.10,0.0,0.03,0.008)
    cylN(("assets","LAMP"),w,u,h,0.03,0.12,0.062,12)
    for k in range(6):
        a=k*math.pi/3; cylN(("assets","BLACK"),w,u+0.095*math.cos(a),h+0.095*math.sin(a),0.03,0.135,0.0045,5)
    for rv,rr in ((0.07,0.095),(0.135,0.07)): 
        pts=[wp(w,u+rr*math.cos(t),rv,h+rr*math.sin(t)) for t in [i*2*math.pi/16 for i in range(17)]]
        K.tube(("assets","BLACK"),pts,0.0045,5)
def a_beacon(w,u,h):
    wb(("assets","STEEL"),w,u-0.09,u+0.09,h-0.09,h+0.09,0.0,0.03,0.006)
    cylN(("assets","STEEL"),w,u,h,0.03,0.07,0.075,12); cylN(("assets","REDLAMP"),w,u,h,0.07,0.17,0.062,12)
    cylN(("assets","STEEL"),w,u,h,0.17,0.185,0.068,12)
def a_exit(w,u,h,left=True):
    wb(("assets","RED"),w,u-0.34,u+0.34,h,h+0.20,0.0,0.05,0.008)
    text(("text","WHITE"),w,"EXIT",u+0.05,h+0.10,0.052,0.11,0.003,1.1)
    s=1 if left else -1
    hullw(("text","WHITE"),w,[(u+s*(-0.27),0.052,h+0.10),(u+s*(-0.20),0.052,h+0.15),(u+s*(-0.20),0.052,h+0.05),(u+s*(-0.27),0.055,h+0.10),(u+s*(-0.20),0.055,h+0.15),(u+s*(-0.20),0.055,h+0.05)],0.0)
    cylV(("assets","STEEL"),w,u-0.28,0.025,h+0.20,h+0.30,0.008,6); cylV(("assets","STEEL"),w,u+0.28,0.025,h+0.20,h+0.30,0.008,6)
def a_plate(w,u,h,txt,width=0.8,hgt=0.26,mat="AUDI",tmat="AMBER"):
    wb(("assets",mat),w,u-width/2,u+width/2,h,h+hgt,0.0,0.03,0.006)
    wb(("assets","ORANGE"),w,u-width/2+0.02,u+width/2-0.02,h+0.02,h+0.035,0.03,0.032,0.0)
    text(("text",tmat),w,txt,u,h+hgt/2+0.01,0.032,hgt*0.42,0.003,1.05)
def a_arrow(w,u,h,left=True,mat="ORANGE"):
    s=1 if left else -1
    pts=[(u+s*-0.20,0.03,h),(u+s*0.0,0.03,h+0.14),(u+s*0.0,0.03,h-0.14)]
    hullw(("assets",mat),w,pts+[(a,0.046,b) for (a,_,b) in pts],0.0)
    wb(("assets",mat),w,min(u,u+s*0.20),max(u,u+s*0.20),h-0.05,h+0.05,0.03,0.046,0.0)
def a_fan(w,u,h):
    wb(("assets","STEEL"),w,u-0.52,u+0.52,h-0.52,h+0.52,0.0,0.05,0.012)
    cylN(("assets","AUDI_SATIN"),w,u,h,0.05,0.20,0.44,28); cylN(("assets","BLACK"),w,u,h,0.04,0.17,0.40,28)
    for k in range(7):
        a=k*2*math.pi/7
        hullw(("assets","STEEL"),w,[(u+0.05*math.cos(a),0.10,h+0.05*math.sin(a)),(u+0.37*math.cos(a-0.28),0.115,h+0.37*math.sin(a-0.28)),(u+0.37*math.cos(a+0.10),0.12,h+0.37*math.sin(a+0.10)),(u+0.05*math.cos(a+0.2),0.13,h+0.05*math.sin(a+0.2))],0.0)
    cylN(("assets","STEEL"),w,u,h,0.08,0.16,0.07,12)
    for rr in (0.15,0.28,0.41):
        pts=[wp(w,u+rr*math.cos(t),0.20,h+rr*math.sin(t)) for t in [i*2*math.pi/28 for i in range(29)]]
        K.tube(("assets","GALV"),pts,0.0055,5)
    for k in range(8):
        a=k*math.pi/4; K.prism(("assets","GALV"),wp(w,u,0.20,h),wp(w,u+0.43*math.cos(a),0.20,h+0.43*math.sin(a)),0.0045,0.0045,5)
def a_vent(w,u,h):
    wb(("assets","STEEL"),w,u-0.5,u+0.5,h-0.32,h+0.32,0.0,0.10,0.01); wb(("assets","BLACK"),w,u-0.44,u+0.44,h-0.26,h+0.26,0.0,0.06,0.0)
    for k in range(8):
        z=h-0.24+k*0.065
        hullw(("assets","AUDI"),w,[(u+s,v,hh) for s in (-0.44,0.44) for (v,hh) in ((0.04,z+0.05),(0.12,z),(0.12,z+0.014),(0.04,z+0.064))],0.0)
def a_clock(w,u,h):
    cylN(("assets","BLACK"),w,u,h,0.0,0.06,0.25,28); cylN(("assets","WHITE"),w,u,h,0.06,0.066,0.225,28)
    for k in range(12):
        a=k*math.pi/6; L=0.035 if k%3 else 0.06
        K.prism(("assets","BLACK"),wp(w,u+0.2*math.sin(a),0.066,h+0.2*math.cos(a)),wp(w,u+(0.2-L)*math.sin(a),0.066,h+(0.2-L)*math.cos(a)),0.006,0.006,4)
    K.prism(("assets","BLACK"),wp(w,u,0.07,h),wp(w,u+0.12*math.sin(2.1),0.07,h+0.12*math.cos(2.1)),0.008,0.006,5)
    K.prism(("assets","BLACK"),wp(w,u,0.074,h),wp(w,u+0.18*math.sin(0.4),0.074,h+0.18*math.cos(0.4)),0.006,0.004,5)
    K.prism(("assets","RED"),wp(w,u,0.078,h),wp(w,u+0.19*math.sin(4.0),0.078,h+0.19*math.cos(4.0)),0.0025,0.002,4)
def a_gauges(w,u,h):
    wb(("assets","AUDI"),w,u-0.30,u+0.30,h,h+0.22,0.0,0.07,0.008)
    for k,du in enumerate((-0.18,0,0.18)):
        cylN(("assets","BRASS"),w,u+du,h+0.11,0.07,0.10,0.062,16); cylN(("assets","WHITE"),w,u+du,h+0.11,0.10,0.104,0.052,16)
        a=-1.0+k*0.9
        K.prism(("assets","BLACK"),wp(w,u+du,0.106,h+0.11),wp(w,u+du+0.042*math.sin(a),0.106,h+0.11+0.042*math.cos(a)),0.0035,0.0025,4)
        cylV(("assets","GALV"),w,u+du,0.04,h-0.12,h,0.01,6)
    wb(("assets","ORANGE"),w,u-0.30,u+0.30,h+0.22,h+0.235,0.0,0.07,0.0)
def a_pullcord(w,u,h):
    wb(("assets","RED"),w,u-0.09,u+0.09,h,h+0.20,0.0,0.10,0.008)
    cylN(("assets","WHITE"),w,u,h+0.10,0.10,0.104,0.05,12)
    K.prism(("assets","RED"),wp(w,u,0.06,h),wp(w,u,0.07,h-1.15),0.004,0.004,5); cylV(("assets","YELLOW"),w,u,0.07,h-1.25,h-1.13,0.022,8)
def a_reel(w,u,h):
    """floor cable reel (drum on its side against the wall)"""
    cylU(("assets","ORANGE"),w,u-0.30,u-0.26,0.50,0.45,0.45,20); cylU(("assets","ORANGE"),w,u+0.26,u+0.30,0.50,0.45,0.45,20)
    cylU(("assets","BLACK"),w,u-0.26,u+0.26,0.50,0.45,0.37,20); cylU(("assets","GALV"),w,u-0.32,u+0.32,0.50,0.45,0.05,8)
    wb(("assets","RUBBER"),w,u-0.22,u-0.06,0.0,0.06,0.2,0.8,0.005); wb(("assets","RUBBER"),w,u+0.06,u+0.22,0.0,0.06,0.2,0.8,0.005)
def a_bollard(w,u,h):
    p=w.pt(u,0.80)
    K.lathe(("assets","YELLOW"),p.x,p.y,[(0.16,0),(0.16,0.02),(0.10,0.035),(0.095,0.95),(0.075,1.0),(0.0,1.02)],14)
    K.prism(("assets","BLACK"),(p.x,p.y,0.60),(p.x,p.y,0.78),0.098,0.098,14)
    K.prism(("assets","WHITE"),(p.x,p.y,0.84),(p.x,p.y,0.88),0.097,0.097,14)
    for k in range(4):
        a=k*math.pi/2+math.pi/4; K.prism(("assets","GALV"),(p.x+0.13*math.cos(a),p.y+0.13*math.sin(a),0.02),(p.x+0.13*math.cos(a),p.y+0.13*math.sin(a),0.034),0.013,0.013,6)
def a_ladder(w,u,h0,h1):
    wd=0.22; vs=0.20
    for sg in (-1,1): cylV(("assets","GALV"),w,u+sg*wd,vs,h0,h1+1.0,0.022,8)
    z=h0+0.30
    while z<h1+0.05:
        cylU(("assets","GALV"),w,u-wd,u+wd,vs,z,0.014,6); z+=0.30
    for z in np.arange(h0+0.5,h1,1.4):
        for sg in (-1,1): wb(("assets","STEEL"),w,u+sg*wd-0.025,u+sg*wd+0.025,z-0.03,z+0.03,0.0,vs,0.003)
    # cage
    r=0.32
    for z in np.arange(h0+2.3,h1+0.8,0.75):
        pts=[wp(w,u+r*math.sin(a),vs+0.05+r*(1-math.cos(a))*0.0+r*math.cos(a)*0.0+ (r*(1-abs(math.cos(a)))*0+ r*math.cos(a)),z) for a in [(-1.35+i*2.7/12) for i in range(13)]]
        pts=[wp(w,u+r*math.sin(a),vs+r*math.cos(a)*0.9+0.05,z) for a in [(-1.5+i*3.0/12) for i in range(13)]]
        K.tube(("assets","YELLOW"),pts,0.011,6)
    for a in (-1.2,-0.6,0,0.6,1.2): cylV(("assets","YELLOW"),w,u+r*math.sin(a),vs+r*math.cos(a)*0.9+0.05,h0+2.3,h1+0.8,0.008,5)
    # landing: grating, toe plate, hand rails and a gate chain
    wb(("assets","STEEL"),w,u-0.55,u+0.55,h1+0.0,h1+0.05,0.0,0.85,0.005)
    wb(("assets","GALV"),w,u-0.52,u+0.52,h1+0.05,h1+0.07,0.03,0.82,0.0)
    wb(("assets","YELLOW"),w,u-0.55,u+0.55,h1+0.05,h1+0.15,0.85,0.865,0.0)
    for sg in (-1,1):
        wb(("assets","YELLOW"),w,u+sg*0.55-0.012,u+sg*0.55+0.012,h1+0.05,h1+1.05,0.84,0.86,0.0); wb(("assets","YELLOW"),w,u+sg*0.55-0.012,u+sg*0.55+0.012,h1+1.0,h1+1.04,0.02,0.86,0.0)
    cylU(("assets","YELLOW"),w,u-0.55,u+0.55,0.85,h1+1.04,0.015,8)
    for sg in (-1,1): wb(("assets","STEEL"),w,u+sg*0.55-0.03,u+sg*0.55+0.03,h1-0.30,h1,0.0,0.30,0.004)
# ================================================================== DRIVER
NAMES={1:("COOLING PLANT","D3"),4:("FUEL HANDLING","D2"),6:("MAIN ACCESS","D1")}
# --- structure
for w in WALLS:
    mass(w); lower_concrete(w); transom_and_cladding(w); frieze_cornice(w)
    for (c,kind) in WCOLS[w.i]: column(w,c,kind)
    if w.i in OPEN: door_frame(w)
for i in range(8): corner_pier(i)
# --- wall graphics (kept objects): move onto the new faces, shrink to fit a bay
def relocate_gfx():
    for o in list(C22.objects):
        if not o.name.startswith("R2 gfx") or o.type!='MESH': continue
        me=o.data; n=len(me.vertices); co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(n,3)
        Mw=np.array(o.matrix_world); wco=co@Mw[:3,:3].T+Mw[:3,3]
        c=(wco.min(0)+wco.max(0))/2; best=None
        for w in WALLS:
            v=(Vector((c[0],c[1]))-w.P).dot(w.n); u=(Vector((c[0],c[1]))-w.P).dot(w.t)
            if -0.5<v<0.6 and 0<u<w.L and (best is None or abs(v)<abs(best[1])): best=(w,v,u)
        if not best: continue
        w=best[0]; rel=wco[:,:2]-np.array([w.P.x,w.P.y]); uu=rel@np.array([w.t.x,w.t.y]); vv=rel@np.array([w.n.x,w.n.y])
        wid=uu.max()-uu.min(); hh=wco[:,2].max()-wco[:,2].min(); hc=(wco[:,2].max()+wco[:,2].min())/2; ucur=(uu.max()+uu.min())/2
        numeral=hc>9.0 or re.fullmatch(r"R2 gfx \d+",o.name) is not None
        cand=[b for b in bay_ranges(w) if not (door(w) and not numeral and b[0]<door(w)[1] and b[1]>door(w)[0])]
        if not cand: cand=bay_ranges(w)
        a,b=min(cand,key=lambda r:abs((r[0]+r[1])/2-ucur))
        s=min(1.0,(b-a-0.35)/wid,1.0)
        if numeral: hnew=9.75
        elif hc>CZ-0.2: hnew=8.3
        else: hnew=hc
        unew=(a+b)/2; vt=0.016 if hnew<CZ else 0.122
        new=np.empty_like(wco)
        for k in range(n):
            pass
        loc=wco.copy()
        du=unew-ucur; dh=hnew-hc; dv=vt-vv.min()
        # scale about the centre then shift
        cu=np.array([(uu.max()+uu.min())/2,(vv.max()+vv.min())/2,hc])
        U=(uu-cu[0])*s+cu[0]+du; Vv=(vv-cu[1])*s+cu[1]; Hh=(wco[:,2]-cu[2])*s+cu[2]+dh
        Vv=Vv-(Vv.min())+vt
        P=np.array([w.P.x,w.P.y]); new_xy=P[None,:]+np.outer(U,[w.t.x,w.t.y])+np.outer(Vv,[w.n.x,w.n.y])
        newc=np.column_stack([new_xy,Hh])
        me.vertices.foreach_set('co',newc.ravel()); me.update(); o.matrix_world=Matrix.Identity(4)
        o.parent=None
        # material: orange numerals, white lettering; palette safe
        me.materials.clear(); me.materials.append(M["ORANGE"] if numeral else M["WHITE"])
        GFXCLAIMS.append((w,unew-wid*s/2-0.05,unew+wid*s/2+0.05,Hh.min()-0.05,Hh.max()+0.05))
GFXCLAIMS=[]
relocate_gfx()
for w in WALLS:                                   # structure claims first: assets never sit in columns or piers
    for (c,kind) in WCOLS[w.i]: claim(w,c-0.30,c+0.30,(LINT if kind=='transfer' else 0),RB1)
    claim(w,0,0.80,0,TOP); claim(w,w.L-0.80,w.L,0,TOP)
nl=0
for wi in (3,5,2,0,7,4,6,1):
    if nl>=2: break
    w=WALLS[wi]
    for u in [0.9+k*0.15 for k in range(int((w.L-1.8)/0.15))]:
        if free(w,u-0.35,u+0.35,0.2,2.6,0.26) and free(w,u-0.45,u+0.45,2.6,7.0,0.62):
            a_ladder(w,u,0.30,6.35); claim(w,u-0.6,u+0.6,0,7.6); PLACED.append(("ladder",wi,round(u,2),0.3)); nl+=1; break
for (w,a_,b_,c_,d_) in GFXCLAIMS: claim(w,a_,b_,c_,d_)
# --- door furniture
for wi,(nm,num) in NAMES.items():
    w=WALLS[wi]; c,h=OPEN[wi]
    a_plate(w,c,LINT+0.16,nm,2.1,0.34,"AUDI","AMBER")
    wb(("assets","ORANGE"),w,c+1.15,c+1.65,LINT+0.16,LINT+0.50,0.0,0.03,0.006); text(("text","WHITE"),w,num,c+1.40,LINT+0.335,0.032,0.18,0.003,1.0)
    a_beacon(w,c,CZ-0.20); claim(w,c-0.3,c+0.3,CZ-0.4,CZ)
    claim(w,c-h-0.5,c+h+0.5,0,CZ)
# --- small assets, placed where there is room, with a reason
for w in WALLS:                                   # structure claims first: assets never sit in columns or piers
    for (c,kind) in WCOLS[w.i]: claim(w,c-0.30,c+0.30,(LINT if kind=='transfer' else 0),RB1)
    claim(w,0,0.80,0,TOP); claim(w,w.L-0.80,w.L,0,TOP)
if os.environ.get('RHW_DUMP2'): np.savez(os.environ['RHW_DUMP2'],**{str(k):v for k,v in OCC.items()})
def scan(fn,wi,h,hw,h0,h1,d,n,gap,name,lo=0.9,hi=None,order=0):
    """put up to n assets of one kind on wall wi at height h, at free spots at least gap apart (scan order rotates per wall)"""
    w=WALLS[wi]; hi=hi or w.L-0.9; got=[]
    cand=[lo+k*0.15 for k in range(int((hi-lo)/0.15)+1)]
    k0=int(jit(wi,len(name),order)*len(cand)); cand=cand[k0:]+cand[:k0]
    for u in cand:
        if len(got)>=n: break
        if any(abs(u-g)<gap for g in got): continue
        if u-hw<0.8 or u+hw>w.L-0.8: continue
        for hh in (h if isinstance(h,(list,tuple)) else [h]):
            if free(w,u-hw,u+hw,hh+h0,hh+h1,d):
                fn(w,u,hh); claim(w,u-hw-0.05,u+hw+0.05,hh+h0-0.05,hh+h1+0.05); PLACED.append((name,wi,round(u,2),hh)); got.append(u); break
    if len(got)<n: SKIPPED.setdefault(name,0); SKIPPED[name]+=n-len(got)
    return got
for wi,(nm,num) in NAMES.items():
    w=WALLS[wi]; c,h=OPEN[wi]; a_,b_=c-h,c+h
    scan(lambda w_,u,hh:a_exit(w_,u,hh,c<u),wi,3.9,0.36,0,0.3,0.06,2,3.0,"exit",lo=max(0.9,a_-3.0),hi=min(w.L-0.9,b_+3.0))
    for sidew,ds in ((WALLS[(wi+1)%8],True),(WALLS[wi-1],False)):
        scan(lambda w_,u,hh,nm=nm,ds=ds:(a_plate(w_,u,hh,nm,1.35,0.30,"AUDI","AMBER"),a_arrow(w_,u+(0.95 if ds else -0.95),hh+0.15,ds)),sidew.i,2.9,0.78,0,0.3,0.06,1,3.0,"dirsign",lo=1.0 if ds else sidew.L-4.0,hi=4.0 if ds else sidew.L-1.0)
    for sh in (-1,1):                              # safety point either side of every door
        lo,hi=(max(0.9,a_-4.2),a_-0.6) if sh<0 else (b_+0.6,min(w.L-0.9,b_+4.2))
        if hi>lo+0.5:
            scan(a_cabinet,wi,[1.15,1.6,2.3],0.30,0,1.2,0.24,1,2.0,"cabinet",lo=lo,hi=hi,order=sh)
            scan(a_firstaid if sh>0 else a_eyewash,wi,[1.2,1.7,2.4],0.26,0,0.9,0.32,1,2.0,"firstaid" if sh>0 else "eyewash",lo=lo,hi=hi,order=sh)
            scan(a_pullcord,wi,[3.7,4.4],0.12,-1.3,0.2,0.12,1,2.0,"pullcord",lo=lo,hi=hi,order=sh)
            scan(a_clock,wi,[5.1,4.4],0.27,-0.27,0.27,0.08,1,2.0,"clock",lo=lo,hi=hi,order=sh)
for wi in range(8):
    w=WALLS[wi]
    scan(a_lamp,wi,5.85,0.16,-0.12,0.12,0.14,3 if w.L>10 else 2,2.2,"lamp",lo=0.9)
    scan(a_cabinet,wi,[1.15,1.6,2.3,3.0],0.30,0,1.2,0.24,1,3.0,"cabinet")
    scan(a_hosereel,wi,[1.45,2.1,3.0],0.42,-0.42,0.42,0.30,1,3.0,"reel") if wi in (0,2,3,5) else None
    scan(a_junction,wi,[1.55,2.2,3.2,4.0],0.24,0,0.5,0.19,2,2.5,"junction")
    scan(a_gauges,wi,[1.9,2.6,3.4],0.32,0,0.24,0.1,1,3.0,"gauges")
    scan(a_clock,wi,5.45,0.27,-0.27,0.27,0.08,1,3.0,"clock")
    scan(a_pullcord,wi,[3.75,4.4],0.12,-1.3,0.2,0.12,1,3.0,"pullcord")
    scan(a_reel,wi,0.0,0.36,0,0.9,0.95,1,3.0,"cablereel")
    scan(a_fan,wi,9.45,0.55,-0.55,0.55,0.22,1 if w.L<10 else 2,3.0,"fan")
    scan(a_vent,wi,[4.4,3.4,5.2],0.52,-0.34,0.34,0.13,1,3.0,"vent")
    scan(lambda w_,u,hh:a_conduit_run(w_,u-0.7,u+0.7,hh),wi,[2.45,3.3,4.2,5.0],0.95,-0.5,0.5,0.19,1,3.0,"conduit")
    if wi%2==0: scan(a_firstaid,wi,[1.2,1.7,2.4,3.1],0.26,0,0.9,0.19,1,3.0,"firstaid")
    else: scan(a_eyewash,wi,[1.2,1.7,2.4,3.1],0.26,0,1.2,0.34,1,3.0,"eyewash")
    scan(lambda w_,u,hh:a_plate(w_,u,hh,["ZONE A","ZONE B","ZONE C","ZONE D","ZONE E","ZONE F","ZONE G","ZONE H"][wi],1.0,0.26,"AUDI","AMBER"),wi,[2.6,3.4,4.3],0.52,0,0.3,0.06,1,3.0,"zoneplate")
# floor-standing bollards at column bases
for w in WALLS:
    for (c,kind) in WCOLS[w.i]:
        if kind=='transfer': continue
        if free(w,c-0.22,c+0.22,0.0,1.05,0.95): 
            a_bollard(w,c,0); claim(w,c-0.24,c+0.24,0,1.1); PLACED.append(("bollard",w.i,c,0))
# --- build the main collection
objs22=K.build(C22,"RH walls",M)
import collections
print("RH walls objects in 22:",len(objs22),"placed:",dict(collections.Counter(x[0] for x in PLACED)),"skipped:",SKIPPED)
# ================================================================== ROOF, DOOR STUBS, SKYLIGHT RESTYLE
K=crk.Kit(); roof_girders(); objs02=K.build(C02,"RH walls",M)
# stub dressing: far end frame, yellow dado stripes, floor hazard stripe
K=crk.Kit()
for wi,(nm,num) in NAMES.items():
    w=WALLS[wi]; c,h=OPEN[wi]; vf=-3.72
    for sg in (-1,1):
        wb(("stubs","AUDI"),w,(c+h-0.14) if sg>0 else c-h,c+h if sg>0 else c-h+0.14,0,5.45,vf,vf+0.12,0.01)
        wb(("stubs","YELLOW"),w,(c+h-0.14) if sg>0 else (c-h+0.128),(c+h-0.128) if sg>0 else (c-h+0.14),0,5.45,vf,vf+0.127,0.0)
        # corridor wainscot: yellow stripe along both stub walls
        uu=c+sg*(h-0.012)
        wb(("stubs","YELLOW"),w,min(uu,uu-sg*0.012),max(uu,uu-sg*0.012),1.1,1.2,vf+0.2,-0.8,0.0)
        wb(("stubs","ORANGE"),w,min(uu,uu-sg*0.012),max(uu,uu-sg*0.012),1.24,1.28,vf+0.2,-0.8,0.0)
    wb(("stubs","AUDI"),w,c-h,c+h,5.30,5.45,vf,vf+0.12,0.008)
    wb(("stubs","HAZARD"),w,c-h+0.14,c+h-0.14,0.0,0.004,vf+0.12,vf+0.55,0.0)
    wb(("stubs","STEEL"),w,c-h+0.14,c+h-0.14,0.0,0.015,-0.8,vf+0.55,0.0)
objs30=K.build(C30,"RH walls",M)
# material swaps on kept objects (geometry untouched)
SWAP={"R2 wall plum lower":"CONC","R2 floor tile":"CONC_DARK","R2 iron":"AUDI","R2 trim rust":"YELLOW","R2 door steel":"AUDI_SATIN","R2 door panel":"AUDI"}
def swap(o,key):
    for s,sl in enumerate(o.material_slots): sl.material=M[key]
for o in C30.objects:
    if o.type!='MESH' or o.name.startswith("RH walls"): continue
    nm=o.name
    if "link wall" in nm: swap(o,"CONC")
    elif "link roof" in nm: swap(o,"CONC_DARK")
    elif "link floor" in nm: swap(o,"CONC_DARK")
    elif "screw" in nm: swap(o,"GALV")
    elif "infill" in nm: swap(o,"AUDI")
    elif "meeting strip" in nm: swap(o,"STEEL")
    elif "stiffener" in nm: swap(o,"YELLOW")
    elif "door leaf" in nm: swap(o,"AUDI_SATIN")
    elif "closed distant doors" in nm: swap(o,"STEEL")
    else:
        for sl in o.material_slots:
            if sl.material and sl.material.name in SWAP: sl.material=M[SWAP[sl.material.name]]
RFMAP={"RF BATCH structure RF edge":"STEEL","RF BATCH structure RF gunmetal":"AUDI","RF BATCH services RF edge":"STEEL","RF BATCH services RF dark":"STEEL","RF BATCH services RF gunmetal":"AUDI",
       "RF BATCH services RF orange":"ORANGE","RF BATCH skylights RF orange":"ORANGE","RF BATCH skylights RF white":"CONC_POUR","RF BATCH services RF white":"CONC_POUR",
       "RF BATCH skylights RF edge":"AUDI_SATIN","RF BATCH skylights RF dark":"STEEL"}
for o in bpy.data.collections["RF APPROVED SKYLIGHT ROOF"].objects:
    base=re.sub(r"\.\d+$","",o.name)
    if base in RFMAP: swap(o,RFMAP[base])
for me in list(bpy.data.meshes):
    if me.users==0: bpy.data.meshes.remove(me)
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("saved",DST)
