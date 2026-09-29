import bpy,sys,math,collections; sys.path.insert(0,"."); from lib import *
bpy.ops.wm.open_mainfile(filepath="/tmp/claude-0/-home-user-critical-shift/5ebcceb3-8a21-50cc-b118-020108004558/scratchpad/w16.blend")
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
# ---- stairs
st=[o.name for o in bpy.data.objects if 'stair' in o.name.lower()]
print("STAIRS: objects with 'stair' in name:",len(st),st[:5]); print("STAIRS: collections:",[c.name for c in bpy.data.collections if 'stair' in c.name.lower()])
tread=[o for o in bpy.data.objects if o.type=='MESH' and o.material_slots and any(s.material and s.material.name.startswith(('stair_tread','tread_wear')) for s in o.material_slots)]
print("STAIRS: meshes using stair/tread materials:",len(tread))
# ---- elevator
el=[o for o in bpy.data.objects if o.name.startswith("EL ")]
print("ELEVATOR: objects",len(el),"| car keyed:",bool(bpy.data.objects['EL car'].animation_data),"| counterweight keyed:",bool(bpy.data.objects['EL counterweight'].animation_data))
for f in (1,240):
    sc.frame_set(f); print("  frame",f,"car floor z=%.2f"%bpy.data.objects['EL car'].location.z,"counterweight z=%.2f"%bpy.data.objects['EL counterweight'].location.z)
sc.frame_set(1)
# ---- sight from control room
glass=set(o.name for o in bpy.data.objects if o.type=='MESH' and ("glass" in o.name.lower() or o.name.startswith("LP haze")))
def cast(o,d,maxd=60):
    o=Vector(o); d=Vector(d).normalized(); tot=0
    for _ in range(6):
        ok,loc,nrm,idx,obj,mw=sc.ray_cast(dg,o,d,distance=maxd-tot)
        if not ok: return None,None
        if obj.name in glass or obj.name.startswith("EL front glass"): o=loc+d*0.02; tot+=(loc-o).length; continue
        return obj,loc
    return None,None
def visible(eye,target,tol=0.5):
    tol=max(tol,0.45)
    obj,loc=cast(eye,Vector(target)-Vector(eye))
    return obj is not None and (Vector(loc)-Vector(target)).length<tol
eyes={"centre, 0.8 m from glass":(-1.9,-6.9,7.1),"left":(-3.4,-6.9,7.1),"right":(0.6,-6.9,7.1),"standing at the glass":(-1.9,-6.45,7.05)}
# targets: bank columns (A x=-1.4, B x=+1.4), several heights; pool surface ring; floor grid
cols={"Bank A drive column":[(-1.4,0,z) for z in (0,3,6,8)],"Bank B drive column":[(1.4,0,z) for z in (0,3,6,8)]}
for en,e in eyes.items():
    res={k:sum(visible(e,t) for t in v)/len(v) for k,v in cols.items()}
    pool=[(math.cos(a)*r,math.sin(a)*r,-0.5) for r in (1.0,2.0,3.0) for a in [i*math.pi/6 for i in range(12)]]
    pv=sum(visible(e,t,0.7) for t in pool)/len(pool)
    fl=[];vis=0;tot=0;blind=collections.Counter()
    for x in [i*1.0 for i in range(-10,11)]:
        for y in [i*1.0 for i in range(-10,11)]:
            if abs(x)+abs(y)>15.8 or abs(x)>10 or abs(y)>10: continue
            if x*x+y*y<3.6**2: continue   # pool interior counted separately
            tot+=1
            if visible(e,(x,y,0.05),0.6): vis+=1
            else: blind[("north" if y>0 else "south")+("-east" if x>0 else "-west")]+=1
    print("SIGHT from %-11s: bank A %3d%%, bank B %3d%%, pool water %3d%%, hall floor %3d%% (%d/%d cells); blind cells by quadrant: %s"%(en,res["Bank A drive column"]*100,res["Bank B drive column"]*100,pv*100,vis/tot*100,vis,tot,dict(blind)))
