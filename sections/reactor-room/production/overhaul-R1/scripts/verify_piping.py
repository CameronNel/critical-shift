import bpy,sys,json,math,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from lib import bbw; from mathutils import Vector
# usage: blender/python verify_piping.py -- <scene dir> <scene.blend> [runs manifest .json]
# manifest defaults to the checked-in ../piping_runs_generated.json
A=sys.argv[sys.argv.index("--")+1:]
S=A[0]; f=A[1] if len(A)>1 else "w30.blend"
MANIFEST=A[2] if len(A)>2 else os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","piping_runs_generated.json")
bpy.ops.wm.open_mainfile(filepath=S+"/"+f); RUNS=json.load(open(MANIFEST))
print("runs manifest:",os.path.normpath(MANIFEST))
ports=[(o.name,o.matrix_world.translation.copy()) for o in bpy.data.objects if o.name.startswith("PORT_")]
devs=[(o.name,bbw(o)) for o in bpy.data.objects if o.type=='MESH' and not (o.name.startswith("R2 pipe") and "socket" not in o.name) and not o.name.startswith(("LP ","R2 corners","R2 w","R2 floor","R2 lights","R2 lamps","R2 detail"))]
def near_port(p,tol=0.06):
    for n,l in ports:
        if (l-Vector(p)).length<tol: return n
def in_bbox(p,b,tol): return all(b[i][0]-tol<=p[i]<=b[i][1]+tol for i in range(3))
def touches_device(p,tol=0.08):
    for n,b in devs:
        if in_bbox(p,b,tol): return n
def on_segment(p,pts,tol=0.04):
    P=Vector(p)
    for a,b in zip(pts,pts[1:]):
        A=Vector(a);B=Vector(b);ab=B-A;t=max(0,min(1,(P-A).dot(ab)/ab.length_squared)); 
        if (A+ab*t-P).length<tol: return True
    return False
byname={r["name"]:r for r in RUNS}
# ring polyline
walls=[]; import r2lib
ring=[]
DI=0.95;Z=11.6
lines=[(w.P+w.n*DI,w.t) for w in r2lib.WALLS]
def inter(l1,l2):
    p,d=l1;q,e=l2;det=d.x*(-e.y)+e.x*d.y;t=((q.x-p.x)*(-e.y)+e.x*(q.y-p.y))/det;return p+d*t
ringp=[inter(lines[i-1],lines[i]) for i in range(8)]
ring_pts=[(v.x,v.y,Z+0.03) for v in ringp]+[(ringp[0].x,ringp[0].y,Z+0.03)]
def end_ok(run,p,kind):
    n=near_port(p)
    if n: return f"port {n}"
    if kind=="TRENCH_JUNCTION_A" and abs(p[0]+2.1)<0.3 and abs(p[1]+8.15)<0.3 and p[2]<0.2: return "trench junction box"
    if (kind or "").startswith("RISER") and touches_device(p): return "device ("+touches_device(p)[:26]+")"
    if kind=="TRENCH_JUNCTION_B" and abs(p[0]+1.4)<0.3 and abs(p[1]+4.9)<0.3 and p[2]<0.45: return "pool inlet manifold"
    if kind=="POOL_DIFFUSER" and in_bbox(p,((-1.6,-1.2),(-3.25,-2.75),(-3.3,-2.9)),0.05): return "pool diffuser"
    if kind=="HPU" and in_bbox(p,((-0.6,0.6),(1.8,2.4),(12.55,13.45)),0.06): return "hydraulic unit"
    if kind=="RETURN_TANK" and in_bbox(p,((-0.6,0.6),(-2.4,-1.8),(12.55,13.45)),0.06): return "return tank"
    if kind=="CABLE_RING" and on_segment(p,ring_pts,0.06): return "cable ring"
    for o in RUNS:
        if o is not run and (Vector(o["start"])-Vector(p)).length<0.02: return f"junction with '{o['name']}'"
    d=touches_device(p)
    if d and (kind or "").startswith("RISER"): return f"device ({d[:30]})"
    return None
bad=0
print("%-26s %-30s %-30s"%("run","start","end"))
for r in RUNS:
    s=end_ok(r,r["start"],r["start_port"]) if r["start_port"] and not r["start_port"].startswith("PORT_WALL") else (end_ok(r,r["start"],r["start_port"]) or ("port" if r["start_port"] and near_port(r["start"]) else None))
    if r["start_port"] is None and r["tees"]:
        s=None
    e=end_ok(r,r["end"],r["end_port"])
    # tee starts: a run without a port start whose start lies on another run
    if s is None and r["start_port"] is None:
        for o in RUNS:
            if o is not r and on_segment(r["start"],o["pts"]): s=f"tee on '{o['name']}'"
    if s is None and r["start_port"] is None: s=touches_device(r["start"]) and "device"
    ok=bool(s) and bool(e); bad+=0 if ok else 1
    print("%-26s %-30s %-30s %s"%(r["name"][:26],str(s)[:30],str(e)[:30],"OK" if ok else "<<< DANGLING"))
print("RUNS:",len(RUNS),"dangling:",bad)
un=[o.name for o in bpy.data.objects if o.name.startswith("PORT_") and not o.get("connected")]
print("PORTS unconnected:",len(un),un)
if bad or un:
    print("FAIL: %d dangling run(s), %d unconnected port(s)"%(bad,len(un))); sys.exit(1)
print("PASS")
