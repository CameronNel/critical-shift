import bpy,sys,math,collections; sys.path.insert(0,"."); from lib import *
S=sys.argv[sys.argv.index("--")+1]; f=sys.argv[sys.argv.index("--")+2]
bpy.ops.wm.open_mainfile(filepath=S+"/"+f); sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
st=[o.name for o in bpy.data.objects if 'stair' in o.name.lower()]
print("STAIRS: objects named stair:",len(st),"| collections:",[c.name for c in bpy.data.collections if 'stair' in c.name.lower()])
el=[o for o in bpy.data.objects if o.name.startswith(("CR lift","CR ante"))]
print("LIFT: objects",len(el),"| car/cw/ropes/doors driven (seconds):",bool(bpy.data.objects['CR lift car'].animation_data),bool(bpy.data.objects['CR lift cw'].animation_data),sum(1 for o in bpy.data.objects if o.name.startswith("CR lift rope") and o.animation_data),sum(1 for o in bpy.data.objects if o.name.startswith(("CR lift_dg","CR lift_du")) and o.animation_data))
for fr in (1,240,330):                          # scene fps 30: t = (frame-1)/30 s -> ground, 8 s (riding up), 11 s (upper)
    sc.frame_set(fr); dgl=[o for o in bpy.data.objects if o.name.startswith("CR lift_dgL")][0]; du=[o for o in bpy.data.objects if o.name.startswith("CR lift_duL")][0]
    print("  frame",fr,"car z=%.2f"%bpy.data.objects['CR lift car'].location.z,"| ground door L dx=%.2f upper door L dy=%.2f"%(dgl.location.x,du.location.y))
sc.frame_set(1)
glass=set(o.name for o in bpy.data.objects if o.type=='MESH' and ("glass" in o.name.lower() or o.name.startswith(("LP haze","CR haze","COL "))))   # haze volume and collision proxies are not visible geometry
def cast(o,d,maxd=60):
    o=Vector(o); d=Vector(d).normalized(); tot=0
    for _ in range(16):                                   # skips glass, haze volumes and collision proxies (each pass-through costs one or two hits)
        ok,loc,n,i,obj,mw=sc.ray_cast(dg,o,d,distance=maxd-tot)
        if not ok: return None,None
        if obj.name in glass or obj.name.startswith("EL front glass"): tot+=(loc-o).length+0.02; o=loc+d*0.02; continue
        return obj,loc
    return None,None
def visible(eye,t,tol=0.5):
    obj,loc=cast(eye,Vector(t)-Vector(eye)); return obj is not None and (Vector(loc)-Vector(t)).length<max(tol,0.45)
eyes={"centre desk (0.8 m from glass)":(-1.55,-6.9,7.1),"left":(-3.4,-6.9,7.1),"right":(0.6,-6.9,7.1),"standing at the glass":(-1.55,-6.45,7.05)}
cols={"A":[(-1.4,0,z) for z in (0,3,6,8)],"B":[(1.4,0,z) for z in (0,3,6,8)]}
for en,e in eyes.items():
    pool=[(math.cos(a)*r,math.sin(a)*r,-0.5) for r in (1.0,2.0,3.0) for a in [i*math.pi/6 for i in range(12)]]
    pv=sum(visible(e,t,0.7) for t in pool)/len(pool); tot=vis=0
    for x in range(-10,11):
        for y in range(-10,11):
            if abs(x)+abs(y)>15.8 or x*x+y*y<3.6**2: continue
            tot+=1; vis+=visible(e,(x,y,0.05),0.6)
    print("SIGHT %-32s bank A %3d%% bank B %3d%% pool water %3d%% hall floor %3d%%"%(en,100*sum(visible(e,t) for t in cols["A"])/4,100*sum(visible(e,t) for t in cols["B"])/4,pv*100,100*vis/tot))
