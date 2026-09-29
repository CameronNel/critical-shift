"""Hero-station kit (world-space, axis-aligned stations).  face = direction the front points: '-x','+x','-y','+y'."""
import bpy,bmesh,math,sys; sys.path.insert(0,".")
from r2lib import *
from mathutils import Vector,Matrix
G=lambda n:bpy.data.materials.get(n) or bpy.data.materials["R2 iron"]
MATS={"IRON":"R2 iron","TRIM":"R2 trim rust","ENAM":"R2 machine enamel","OLIVE":"R2 machine olive","RUST":"R2 paint rust","INK":"R2 ink",
      "LAMPA":"R2 lamp amber","STAT":"R2 status lamp","SCR":"R2 state screen","GLOW":"R2 state glow","LANE":"R2 lane","CABLE":"R2 cable","COND":"R2 conduit",
      "PIPE":"R2 pipe coolant","LAG":"R2 pipe lagging","CHROME":"GT_Chrome","GLASS":"observation_glass","LAV":"R2 lamp lavender","HYD":"R2 pipe hydraulic","SIGN":"R2 sign text","DRUM":"R2 drum red","CRATE":"R2 crate","PAPER":"R2 paper","CONE":"R2 cone","BIND":"R2 binder a","FAB":"R2 fabric","DESK":"R2 desk","PUD":"R2 puddle","EXIT":"R2 exit sign","INSET":"R2 wall inset"}
class K(Acc):
    def begin(s,cx,cy,yaw,z=0.0):
        s._piv=(cx,cy,yaw,z); s._main=s.bm; s.bm={}
    def end(s):
        cx,cy,yaw,z=s._piv; c,sn=math.cos(yaw),math.sin(yaw)
        for k,bm in s.bm.items():
            for v in bm.verts:
                x,y=v.co.x,v.co.y; v.co.x=cx+x*c-y*sn; v.co.y=cy+x*sn+y*c; v.co.z+=z
            me=bpy.data.meshes.new("_tmp"); bm.to_mesh(me); bm.free()
            tgt=s._main.get(k)
            if tgt is None: tgt=bmesh.new(); s._main[k]=tgt
            tgt.from_mesh(me)              # from_mesh appends to the accumulator
            bpy.data.meshes.remove(me)
        s.bm=s._main
    def hull(s,key,pts,ch=0.012):
        bm=s.get(key); vs=[bm.verts.new(Vector(p)) for p in pts]
        r=bmesh.ops.convex_hull(bm,input=vs,use_existing_faces=False)
        bmesh.ops.delete(bm,geom=r['geom_interior'],context='VERTS');
        fs=[f for f in r['geom'] if isinstance(f,bmesh.types.BMFace)]
        bmesh.ops.dissolve_limit(bm,angle_limit=0.02,verts=list({v for f in fs for v in f.verts}),edges=list({e for f in fs for e in f.edges}))
        if ch>0:
            es=[e for e in bm.edges if e.is_valid and len(e.link_faces)==2 and any(v in vs for v in e.verts)]
            try: bmesh.ops.bevel(bm,geom=es,offset=ch,segments=1,affect='EDGES')
            except Exception: pass
    def prism(s,key,p0,p1,r0,r1=None,seg=8,rot=math.pi/8,cap=True):
        r1=r0 if r1 is None else r1; bm=s.get(key); a=Vector(p0); b=Vector(p1); d=b-a; L=d.length
        if L<1e-6: return
        z=d/L; x=(Vector((1,0,0)) if abs(z.x)<0.9 else Vector((0,1,0))); x=(x-z*x.dot(z)).normalized(); y=z.cross(x)
        r=bmesh.ops.create_cone(bm,cap_ends=cap,segments=seg,radius1=r0,radius2=r1,depth=1.0)
        c,sn=math.cos(rot),math.sin(rot)
        for v in r['verts']:
            lx=v.co.x*c-v.co.y*sn; ly=v.co.x*sn+v.co.y*c; t=v.co.z+0.5
            rad=1.0
            v.co=a+z*(t*L)+x*lx+y*ly
    def bx(s,key,x0,x1,y0,y1,z0,z1,ch=0.015):
        if x1<=x0 or y1<=y0 or z1<=z0: return
        s.box(key,(x0+x1)/2,(y0+y1)/2,z0,z1,x1-x0,y1-y0,0,ch)
    # face helpers: lateral axis = y for x-facing, x for y-facing.  p = plane coord along facing axis, t = thickness outward
    def fb(s,key,face,p,l0,l1,z0,z1,t,ch=0.01):
        if face=='-x': s.bx(key,p-t,p,l0,l1,z0,z1,ch)
        elif face=='+x': s.bx(key,p,p+t,l0,l1,z0,z1,ch)
        elif face=='-y': s.bx(key,l0,l1,p-t,p,z0,z1,ch)
        else: s.bx(key,l0,l1,p,p+t,z0,z1,ch)
    def db(s,key,face,pw,pf,l0,l1,z0,z1,ch=0.015):
        """box from wall plane pw to front plane pf"""
        a,b=(min(pw,pf),max(pw,pf))
        if face in('-x','+x'): s.bx(key,a,b,l0,l1,z0,z1,ch)
        else: s.bx(key,l0,l1,a,b,z0,z1,ch)
    def louvre(s,key,face,p,l0,l1,z0,z1,n=6,t=0.035,back=None):
        if back: s.fb(back,face,p,l0,l1,z0,z1,0.012,0.0)
        h=(z1-z0)/n
        for i in range(n): s.fb(key,face,p,l0+0.02,l1-0.02,z0+i*h+h*0.35,z0+i*h+h*0.75,t,0.004)
    def screen(s,g,face,p,l0,l1,z0,z1,t=0.035):
        sg=-1 if face in('-x','-y') else 1
        s.fb((g,"IRON"),face,p,l0-0.03,l1+0.03,z0-0.03,z1+0.03,t,0.006)
        s.fb((g,"SCR"),face,p+sg*(t-0.006),l0,l1,z0,z1,0.008,0.0)
    def led(s,key,face,p,l,z,r=0.022,t=0.02): s.fb(key,face,p,l-r,l+r,z-r,z+r,t,0.004)
    def wheel(s,key,cx,cy,cz,r,axis='y',spokes=4,tube=0.012):
        # valve handwheel as a ring of boxes + spokes (axis = normal direction)
        n=16
        for i in range(n):
            a=2*math.pi*i/n; b=a+2*math.pi/n;
            p0=(cx+math.cos(a)*r*(axis=='y'),cy+math.cos(a)*r*(axis=='x'),cz+math.sin(a)*r); p1=(cx+math.cos(b)*r*(axis=='y'),cy+math.cos(b)*r*(axis=='x'),cz+math.sin(b)*r)
            s.prism(key,p0,p1,tube,tube,4,math.pi/4)
        for i in range(spokes):
            a=2*math.pi*i/spokes
            p1=(cx+math.cos(a)*r*(axis=='y'),cy+math.cos(a)*r*(axis=='x'),cz+math.sin(a)*r)
            s.prism(key,(cx,cy,cz),p1,tube,tube,4,math.pi/4)
    def flange(s,key,p0,p1,r,rr=None,n=8):
        s.prism(key,p0,p1,rr or r*1.45,rr or r*1.45,n,math.pi/8)
def mats():
    return {k:G(v) for k,v in MATS.items()}
