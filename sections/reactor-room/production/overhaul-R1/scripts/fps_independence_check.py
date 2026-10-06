"""Frame-rate independence check for driver-based animation.
usage: python fps_independence_check.py -- <blend> [--prefix CR] [--times 0.5,3,7.25,12,19.9] [--tol 1e-3]
Evaluates every driver whose owner name (or ID name) starts with --prefix at the SAME real time under several scene frame rates
(24/30/60/144/480) and reports drivers whose value differs. A driver that uses the raw `frame` variable (not seconds) fails.
Tolerance 1e-3 relative (Blender stores the subframe as float32, so very high rates show ~3e-4 noise on steep sine blinkers). Exit code 1 if any in-scope driver is frame-rate dependent."""
import bpy,sys
A=sys.argv[sys.argv.index("--")+1:]; SRC=A[0]
PFX=A[A.index("--prefix")+1] if "--prefix" in A else "CR"
TIMES=[float(x) for x in (A[A.index("--times")+1] if "--times" in A else "0.5,3,7.25,12,19.9").split(",")]
TOL=float(A[A.index("--tol")+1]) if "--tol" in A else 1e-3
FPS=[24,30,60,144,480]
bpy.ops.wm.open_mainfile(filepath=SRC); sc=bpy.context.scene
def idblocks():
    for coll in (bpy.data.objects,bpy.data.materials,bpy.data.lights,bpy.data.worlds,bpy.data.shape_keys,bpy.data.node_groups):
        for i in coll: yield i
def drivers():
    for i in idblocks():
        for host in (i,getattr(i,"node_tree",None),getattr(i,"data",None)):
            ad=getattr(host,"animation_data",None) if host is not None else None
            if ad:
                for fc in ad.drivers: yield i,host,fc
def val(host,fc):
    try: return host.path_resolve(fc.data_path)[fc.array_index] if fc.array_index>=0 and hasattr(host.path_resolve(fc.data_path),'__len__') else host.path_resolve(fc.data_path)
    except Exception: return None
D=[(i,h,fc) for i,h,fc in drivers() if i.name.startswith(PFX) or h.name.startswith(PFX)]
bad={}; res={}
for T in TIMES:
    for fps in FPS:
        sc.render.fps=fps; sc.render.fps_base=1.0
        # evaluate at the exact time: frame = T*fps (subframe) so every rate sees the same T
        sc.frame_set(int(T*fps),subframe=T*fps-int(T*fps)); bpy.context.view_layer.update()
        for i,h,fc in D:
            v=val(h,fc); res.setdefault((i.name,fc.data_path,fc.array_index,T),[]).append(v)
for k,vs in res.items():
    vs=[v for v in vs if isinstance(v,(int,float))]
    if vs and max(vs)-min(vs)>TOL*max(1,abs(max(vs))): bad.setdefault(k[:3],[]).append((k[3],min(vs),max(vs)))
print("drivers in scope (prefix %r): %d, times %s, fps %s"%(PFX,len(D),TIMES,FPS))
for k,v in sorted(bad.items()): print("FRAME-DEPENDENT",k,"first diff t=%.2f range %.5f..%.5f"%v[0])
print("RESULT",("FAIL: %d frame-dependent drivers"%len(bad)) if bad else "PASS: all in-scope drivers identical across frame rates")
sys.exit(1 if bad else 0)
