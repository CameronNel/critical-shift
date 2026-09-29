import bpy,sys,math,collections; sys.path.insert(0,"."); from lib import *
S=sys.argv[sys.argv.index("--")+1]; f=sys.argv[sys.argv.index("--")+2]
bpy.ops.wm.open_mainfile(filepath=S+"/"+f); sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
st=[o.name for o in bpy.data.objects if 'stair' in o.name.lower()]
print("STAIRS: objects named stair:",len(st),"| collections:",[c.name for c in bpy.data.collections if 'stair' in c.name.lower()])
el=[o for o in bpy.data.objects if o.name.startswith("EL ")]
print("ELEVATOR: objects",len(el),"| car keyed:",bool(bpy.data.objects['EL car'].animation_data),"| counterweight keyed:",bool(bpy.data.objects['EL counterweight'].animation_data),"| landing doors keyed:",sum(1 for o in bpy.data.objects if o.name.startswith("EL landing door") and o.animation_data))
for fr in (1,240):
    sc.frame_set(fr); print("  frame",fr,"car floor z=%.2f"%bpy.data.objects['EL car'].location.z,"| ground door L x=%.2f upper door L x=%.2f"%(bpy.data.objects['EL landing door ground L'].location.x,bpy.data.objects['EL landing door upper L'].location.x))
sc.frame_set(1)
glass=set(o.name for o in bpy.data.objects if o.type=='MESH' and ("glass" in o.name.lower() or o.name.startswith("LP haze")))
def cast(o,d,maxd=60):
    o=Vector(o); d=Vector(d).normalized(); tot=0
    for _ in range(6):
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
