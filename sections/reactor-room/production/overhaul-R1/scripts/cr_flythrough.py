"""Control-room walk-through: a smooth eye-height camera route rendered as a numbered PNG sequence (no video encoder in the headless build) plus a contact sheet.
usage: python cr_flythrough.py -- <in.blend> <out_dir> [--frames 120] [--w 640] [--h 360] [--samples 14] [--check] [--sheet]
Route: door -> past the cot and shelves -> work table -> TV wall -> rack -> desk row -> window, then a look out over the hall and reactor.  The route is about 7 m long; at 120 frames and the scene's 30 fps that is a slow look-around walk (about 1.8 m/s, well below the layout's 4.5 m/s walking assumption), eye height 6.95 m (floor 5.4 m).  Scene frame = sequence frame, so the lights flicker, brown out and the TV cycles in scene time.
--check only tests the route for clearance (rays from the eye against all control-room geometry); --sheet builds the contact sheet from an existing sequence.  Resumable: existing frames are skipped."""
import bpy,sys,os,math,time
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=sys.argv[sys.argv.index("--")+1:]; SRC,OUT=A[0],A[1]
def opt(k,d,t=float): return t(A[A.index(k)+1]) if k in A else d
N=opt("--frames",120,int); W=opt("--w",640,int); H=opt("--h",360,int); S=opt("--samples",14,int)
os.makedirs(OUT,exist_ok=True)
WP=[((-4.60,-6.80,6.95),(0.50,-9.80,6.60)),((-3.80,-7.90,6.95),(-1.00,-9.50,6.60)),((-3.00,-9.00,6.95),(-1.50,-11.90,7.30)),((-2.00,-9.30,6.95),(-1.50,-11.90,7.35)),
    ((-1.00,-8.80,6.90),(1.60,-10.40,6.70)),((-0.60,-8.40,6.90),(0.60,-7.00,6.30)),((-1.40,-7.90,6.95),(-1.00,-6.90,6.40)),((-1.20,-7.90,7.00),(-1.00,-3.00,6.90)),((-1.20,-7.60,7.00),(-1.00,-1.00,6.80))]
def cr(p,t):                                  # Catmull-Rom through the waypoints, t in [0,1]
    n=len(p)-1; x=min(max(t,0),1)*n; i=min(int(x),n-1); u=x-i
    p0,p1,p2,p3=p[max(i-1,0)],p[i],p[i+1],p[min(i+2,n)]
    return tuple(0.5*((2*p1[k])+(-p0[k]+p2[k])*u+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*u*u+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*u**3) for k in range(3))
def ease(t): return t*t*(3-2*t)*0.6+t*0.4     # gentle ease in/out, never stalls
pos=[w[0] for w in WP]; tgt=[w[1] for w in WP]
def cam_at(t): return Vector(cr(pos,t)),Vector(cr(tgt,t))
if "--sheet" not in A:
    bpy.ops.wm.open_mainfile(filepath=SRC); sc=bpy.context.scene
    for col in bpy.data.collections: col.hide_render=False
    # clearance check: eight horizontal rays of 0.22 m plus up/down from every camera position along the route
    C=bpy.data.collections["31 CR CONTROL ROOM REDO"]; SH=bpy.data.collections["26 R2 CONTROL ROOM"]
    vs=[];fs=[]
    for o in list(C.all_objects)+list(SH.objects):
        if o.type!='MESH' or o.name.startswith(("COL ","CR haze")) or any(m and "glass" in m.name.lower() for m in o.data.materials): continue
        b=len(vs); vs+=[o.matrix_world@v.co for v in o.data.vertices]; fs+=[tuple(b+i for i in p.vertices) for p in o.data.polygons]
    T=BVHTree.FromPolygons(vs,fs); bad=0; worst=9.0
    for k in range(400):
        c,_=cam_at(k/399)
        for a in range(8):
            d=Vector((math.cos(a*math.pi/4),math.sin(a*math.pi/4),0)); h=T.ray_cast(c,d,0.22)
            if h[0] is not None: bad+=1; worst=min(worst,h[3]); print("CLEARANCE route t=%.3f dir %d hit at %.2f m near %s"%(k/399,a,h[3],tuple(round(x,2) for x in h[0]))) if bad<8 else None
        for d in (Vector((0,0,1)),Vector((0,0,-1))):
            h=T.ray_cast(c,d,0.25)
            if h[0] is not None and d.z<0: bad+=1; print("CLEARANCE route t=%.3f floor/obstacle %.2f m below"%(k/399,h[3])) if bad<8 else None
    print("route length %.1f m, clearance violations %d"%(sum((cam_at((k+1)/399)[0]-cam_at(k/399)[0]).length for k in range(399)),bad))
    if "--check" in A: sys.exit(0)
    cd=bpy.data.cameras.new("fly"); cd.lens=22; cd.clip_end=200; co=bpy.data.objects.new("fly",cd); sc.collection.objects.link(co); sc.camera=co
    sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=S; sc.cycles.use_denoising=True
    sc.render.resolution_x,sc.render.resolution_y=W,H; sc.render.resolution_percentage=100; sc.render.image_settings.file_format='PNG'
    T0=time.time()
    sc.render.use_persistent_data=True                     # keep the scene/BVH between frames: per-frame cost drops from ~40 s of setup to the pure render
    for i in range(N):
        t=ease(i/(N-1)); c,tg=cam_at(t); co.location=c; co.rotation_euler=(tg-c).to_track_quat('-Z','Y').to_euler()
        co.keyframe_insert("location",frame=i+1); co.keyframe_insert("rotation_euler",frame=i+1)
    sc.frame_start,sc.frame_end=1,N; sc.render.filepath=os.path.join(OUT,"fly_")
    bpy.ops.render.render(animation=True); print("sequence rendered in %.0f s"%(time.time()-T0),flush=True)
# contact sheet: 12 evenly spaced frames, 4 x 3
cols,rows=4,3; idx=[round(k*(N-1)/(cols*rows-1))+1 for k in range(cols*rows)]
tw,th=480,270; sheet=np.zeros((rows*th,cols*tw,4),dtype=np.float32); sheet[...,3]=1
for n,i in enumerate(idx):
    fp=os.path.join(OUT,"fly_%04d.png"%i)
    if not os.path.exists(fp): continue
    im=bpy.data.images.load(fp); w,h=im.size; a=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4); bpy.data.images.remove(im)
    ys=(np.arange(th)*h/th).astype(int); xs=(np.arange(tw)*w/tw).astype(int); r,c=divmod(n,cols)
    sheet[(rows-1-r)*th:(rows-r)*th,c*tw:(c+1)*tw]=a[ys][:,xs]
im=bpy.data.images.new("sheet",cols*tw,rows*th,alpha=False); im.pixels.foreach_set(sheet.reshape(-1)); im.filepath_raw=os.path.join(OUT,"fly_contact_sheet.png"); im.file_format='PNG'; im.save()
print("contact sheet written; frames",idx)
