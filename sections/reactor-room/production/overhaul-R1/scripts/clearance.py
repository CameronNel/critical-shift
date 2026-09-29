import bpy,sys,json,math,collections,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from lib import *
# usage: blender/python clearance.py -- <scene dir> <scene.blend> [runs manifest .json]
# manifest defaults to the checked-in ../piping_runs_generated.json
A=sys.argv[sys.argv.index("--")+1:]
S=A[0]; f=A[1]
MANIFEST=A[2] if len(A)>2 else os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","piping_runs_generated.json")
bpy.ops.wm.open_mainfile(filepath=S+"/"+f); sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get(); RUNS=json.load(open(MANIFEST))
print("runs manifest:",os.path.normpath(MANIFEST))
hits=collections.defaultdict(list)
for r in RUNS:
    pts=[Vector(p) for p in r["pts"]]; rad=r["r"]
    for a,b in zip(pts,pts[1:]):
        d=b-a; L=d.length
        if L<0.05: continue
        dn=d.normalized(); up=Vector((0,0,1)) if abs(dn.z)<0.9 else Vector((1,0,0)); s=dn.cross(up).normalized(); t=dn.cross(s).normalized()
        for off in (Vector(),s*rad,-s*rad,t*rad,-t*rad):
            o=a+off; dist=0.0
            for _ in range(8):
                ok,loc,n,i,obj,mw=sc.ray_cast(dg,o,dn,distance=L-dist)
                if not ok: break
                nm=obj.name
                dl=(loc-a).length; dr=(loc-b).length
                if "R2 PIPING" in nm or nm.startswith(("Water surface","COOLANT_VALVE","Manifold valve","Manifold support","Deep water","LP haze")) or nm.startswith(("R2 pipe","LP ","R2 lights","R2 lamps")) or nm.startswith("PORT") or dl<0.32 or dr<0.32:
                    o=loc+dn*0.02; dist=(o-(a+off)).length; 
                    if dist>=L: break
                    continue
                hits[(r["name"],nm)].append(tuple(round(v,2) for v in loc)); break
print("RUNS checked:",len(RUNS))
bad=0
for (run,obj),locs in sorted(hits.items()):
    print("CLASH run '%s' passes through '%s' at %s (%d ray hits)"%(run,obj[:40],locs[0],len(locs))); bad+=1
print("CLASHES:",bad)
if bad:
    print("FAIL: %d clash(es)"%bad); sys.exit(1)
print("PASS")
