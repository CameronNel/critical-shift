"""Control-room kit: world-space modelling helpers with tight per-element bevels (spawn-room recipe), stylised materials,
emissive/driver helpers, text and light helpers.  Everything here is authoring code (Blender bpy), no engine dependency."""
import bpy,bmesh,math,random
import numpy as np
from mathutils import Vector
STATE=None                      # REACTOR_STATE empty (set by caller)
# ------------------------------------------------------------------ geometry kit
BEVSEG=1      # bevel segments: 1 = a single smooth-shaded chamfer (half the bevel triangles; reads the same at 2-12 mm)
def prism_seg(r,seg): return max(8,min(seg,2*int(3+r*80)))     # small cylinders do not need 16-20 sides
class Kit:
    """Accumulates bmeshes per (group, material key).  All edges get a per-element bevel of `ch` metres, 2 segments.
    Bevel facets are smooth shaded, big faces stay flat (crisp planes, soft highlights on the edge only)."""
    def __init__(s): s.bm={}; s._main=None; s._piv=None
    def get(s,key):
        if key not in s.bm:
            b=bmesh.new(); b.loops.layers.uv.verify(); s.bm[key]=b
        return s.bm[key]
    # --- rotation buffer: everything built between begin/end is rotated about z by yaw around (cx,cy) and lifted by z
    def begin(s,cx,cy,yaw,z=0.0): s._piv=(cx,cy,yaw,z); s._main=s.bm; s.bm={}
    def end(s):
        cx,cy,yaw,z=s._piv; c,sn=math.cos(yaw),math.sin(yaw)
        for k,bm in s.bm.items():
            for v in bm.verts:
                x,y=v.co.x,v.co.y; v.co.x=cx+x*c-y*sn; v.co.y=cy+x*sn+y*c; v.co.z+=z
            me=bpy.data.meshes.new("_t"); bm.to_mesh(me); bm.free()
            tgt=s._main.get(k) if k in s._main else None
            if tgt is None: tgt=bmesh.new(); tgt.loops.layers.uv.verify(); s._main[k]=tgt
            tgt.from_mesh(me); bpy.data.meshes.remove(me)
        s.bm=s._main; s._main=None
    # --- primitives
    @staticmethod
    def _bevel(bm,verts,w):
        if w<0.0008: return
        edges=list({e for v in verts for e in v.link_edges if e.is_valid})
        try:
            r=bmesh.ops.bevel(bm,geom=edges,offset=w,segments=BEVSEG,affect='EDGES',profile=0.5,clamp_overlap=True)
            for f in r['faces']: f.smooth=True
        except Exception: pass
    def box(s,key,cx,cy,z0,z1,sx,sy,ang=0.0,ch=0.004):
        if sx<=0 or sy<=0 or z1<=z0: return
        bm=s.get(key); r=bmesh.ops.create_cube(bm,size=1.0); vs=r['verts']; c,sn=math.cos(ang),math.sin(ang)
        for v in vs:
            lx=v.co.x*sx; ly=v.co.y*sy; v.co=Vector((cx+lx*c-ly*sn,cy+lx*sn+ly*c,z0+(v.co.z+.5)*(z1-z0)))
        s._bevel(bm,vs,min(ch,0.34*min(sx,sy,z1-z0)))
    def bx(s,key,x0,x1,y0,y1,z0,z1,ch=0.004):
        if x1<=x0 or y1<=y0 or z1<=z0: return
        s.box(key,(x0+x1)/2,(y0+y1)/2,z0,z1,x1-x0,y1-y0,0.0,ch)
    def fb(s,key,face,p,l0,l1,z0,z1,t,ch=0.003):
        """slab standing on plane p (coordinate along the facing axis), thickness t towards the room. lateral axis: y for x-facing, x for y-facing"""
        if face=='-x': s.bx(key,p-t,p,l0,l1,z0,z1,ch)
        elif face=='+x': s.bx(key,p,p+t,l0,l1,z0,z1,ch)
        elif face=='-y': s.bx(key,l0,l1,p-t,p,z0,z1,ch)
        else: s.bx(key,l0,l1,p,p+t,z0,z1,ch)
    def hull(s,key,pts,ch=0.004):
        bm=s.get(key); vs=[bm.verts.new(Vector(p)) for p in pts]
        r=bmesh.ops.convex_hull(bm,input=vs,use_existing_faces=False)
        bmesh.ops.delete(bm,geom=r['geom_interior'],context='VERTS')
        fs=[f for f in r['geom'] if isinstance(f,bmesh.types.BMFace)]
        bmesh.ops.dissolve_limit(bm,angle_limit=0.02,verts=list({v for f in fs for v in f.verts}),edges=list({e for f in fs for e in f.edges}))
        vv=[v for v in vs if v.is_valid]
        if ch>0 and vv:
            es=list({e for v in vv for e in v.link_edges if e.is_valid and len(e.link_faces)==2})
            try:
                rr=bmesh.ops.bevel(bm,geom=es,offset=ch,segments=BEVSEG,affect='EDGES',profile=0.5,clamp_overlap=True)
                for f in rr['faces']: f.smooth=True
            except Exception: pass
    def prism(s,key,p0,p1,r0,r1=None,seg=16,rot=0.0,cap=True,ch=0.0):
        r1=r0 if r1 is None else r1; bm=s.get(key); a=Vector(p0); b=Vector(p1); d=b-a; L=d.length
        if L<1e-6: return
        z=d/L; x=(Vector((1,0,0)) if abs(z.x)<0.9 else Vector((0,1,0))); x=(x-z*x.dot(z)).normalized(); y=z.cross(x)
        seg=prism_seg(max(r0,r1 if r1 is not None else r0),seg)
        r=bmesh.ops.create_cone(bm,cap_ends=cap,segments=seg,radius1=r0,radius2=r1,depth=1.0)
        c,sn=math.cos(rot),math.sin(rot); vs=r['verts']
        fset={f for v in vs for f in v.link_faces}
        for f in fset: f.smooth=(len(f.verts)<=4 and seg>=8) or (len(f.verts)==3 and seg>=8)
        for v in vs:
            lx=v.co.x*c-v.co.y*sn; ly=v.co.x*sn+v.co.y*c; t=v.co.z+0.5; v.co=a+z*(t*L)+x*lx+y*ly
        if ch>0 and min(r0,r1)>3*ch and cap:
            es=[e for f in fset if len(f.verts)>4 for e in f.edges if e.is_valid]
            try:
                rr=bmesh.ops.bevel(bm,geom=list(set(es)),offset=ch,segments=BEVSEG,affect='EDGES',profile=0.5,clamp_overlap=True)
                for f in rr['faces']: f.smooth=True
            except Exception: pass
    def cyl(s,key,x,y,z0,z1,r,seg=20,ch=0.0): s.prism(key,(x,y,z0),(x,y,z1),r,r,seg,0.0,True,ch)
    def cylx(s,key,x0,x1,y,z,r,seg=16,ch=0.0): s.prism(key,(x0,y,z),(x1,y,z),r,r,seg,0.0,True,ch)
    def cyly(s,key,x,y0,y1,z,r,seg=16,ch=0.0): s.prism(key,(x,y0,z),(x,y1,z),r,r,seg,0.0,True,ch)
    def tube(s,key,pts,r,seg=8):
        for a,b in zip(pts[:-1],pts[1:]): s.prism(key,a,b,r,r,seg,0.0,False)
    def plane(s,key,p0,p1,p2,p3,uv=((0,0),(1,0),(1,1),(0,1))):
        bm=s.get(key); vs=[bm.verts.new(Vector(p)) for p in (p0,p1,p2,p3)]
        f=bm.faces.new(vs); uvl=bm.loops.layers.uv.verify()
        for lo,u in zip(f.loops,uv): lo[uvl].uv=u
        f.smooth=False
    def dome(s,key,c,u,v,n,w,h,bulge,nu=12,nv=9):
        """gently bulging screen surface centred on c: u,v = in-plane unit axes, n = outward unit normal; UV covers 0..1"""
        bm=s.get(key); c=Vector(c); u=Vector(u); v=Vector(v); n=Vector(n); uvl=bm.loops.layers.uv.verify(); vs=[]
        for j in range(nv+1):
            row=[]
            for i in range(nu+1):
                a=i/nu*2-1; b=j/nv*2-1; row.append(bm.verts.new(c+u*(a*w/2)+v*(b*h/2)+n*bulge*(1-a*a*0.85)*(1-b*b*0.85)))
            vs.append(row)
        for j in range(nv):
            for i in range(nu):
                quad=[(vs[j][i],(i,j)),(vs[j][i+1],(i+1,j)),(vs[j+1][i+1],(i+1,j+1)),(vs[j+1][i],(i,j+1))]
                if u.cross(v).dot(n)<0: quad=quad[::-1]
                f=bm.faces.new([q[0] for q in quad]); f.smooth=True
                for lo,q in zip(f.loops,quad): lo[uvl].uv=(q[1][0]/nu,q[1][1]/nv)
    def louvre(s,key,face,p,l0,l1,z0,z1,n=6,t=0.03,tilt=0.6):
        h=(z1-z0)/n
        for i in range(n): s.fb(key,face,p,l0,l1,z0+i*h+h*0.30,z0+i*h+h*0.70,t,0.002)
    def screw(s,key,face,p,l,z,r=0.006):
        sg=-1 if face in('-x','-y') else 1
        if face in('-x','+x'): s.cylx(key,p,p+sg*0.005,l,z,r,8)
        else: s.cyly(key,l,p,p+sg*0.005,z,r,8)
    def screws(s,key,face,p,l0,l1,z0,z1,r=0.006,inset=0.02):
        for l in (l0+inset,l1-inset):
            for z in (z0+inset,z1-inset): s.screw(key,face,p,l,z,r)
    def build(s,collection,prefix,mats):
        coll=collection if not isinstance(collection,str) else (bpy.data.collections.get(collection) or bpy.data.collections.new(collection))
        if coll.name not in bpy.context.scene.collection.children_recursive and coll.name not in [c.name for c in bpy.context.scene.collection.children]:
            bpy.context.scene.collection.children.link(coll)
        out=[]
        for (grp,mk),bm in s.bm.items():
            if not bm.faces: bm.free(); continue
            _box_uv(bm)
            nm=f"{prefix} {grp} {mk}"; me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free()
            o=bpy.data.objects.new(nm,me); coll.objects.link(o); me.materials.append(mats[mk]); out.append(o)
        s.bm={}; return out
def _box_uv(bm):
    """world-scaled box projection (1 UV unit = 1 m) for every face that has no authored UV; faces from plane() / dome() keep theirs.
    Gives tiling image materials a valid, uniform texel density and lets the delivery derivative bake / export."""
    uvl=bm.loops.layers.uv.verify(); bm.normal_update()
    for f in bm.faces:
        if all(abs(l[uvl].uv.x)+abs(l[uvl].uv.y)<1e-9 for l in f.loops):
            n=f.normal; ax=max(range(3),key=lambda i:abs(n[i]))
            for l in f.loops:
                p=l.vert.co; l[uvl].uv=(p.x,p.y) if ax==2 else ((p.x,p.z) if ax==1 else (p.y,p.z))
# ------------------------------------------------------------------ materials
def _new(name):
    m=bpy.data.materials.get(name)
    if m: bpy.data.materials.remove(m)
    m=bpy.data.materials.new(name); m.use_nodes=True; m.node_tree.nodes.clear(); return m
def _n(nt,t,x=0,y=0):
    n=nt.nodes.new(t); n.location=(x,y); return n
def _scale(c,k): return (c[0]*k,c[1]*k,c[2]*k,1.0)
def pm(name,base,rough=0.5,metal=0.0,var=(0.87,1.05),scale=2.5,bump=0.06,edge=None,edge_w=0.004,grime=0.0,rvar=0.10,coat=0.0,grain=0.04,zfloor=5.4,aniso=None):
    """spawn-room recipe: Principled BSDF, low-frequency noise albedo variation, fine bump on non-metals, painted edge highlight, floor grime."""
    m=_new(name); nt=m.node_tree
    out=_n(nt,"ShaderNodeOutputMaterial",1900,0); b=_n(nt,"ShaderNodeBsdfPrincipled",1650,0); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    b.inputs['Metallic'].default_value=metal
    if coat>0: b.inputs['Coat Weight'].default_value=coat; b.inputs['Coat Roughness'].default_value=0.25
    geo=_n(nt,"ShaderNodeNewGeometry",0,-300)
    nz=_n(nt,"ShaderNodeTexNoise",150,250); nz.inputs['Scale'].default_value=scale; nz.inputs['Detail'].default_value=2.0; nz.inputs['Roughness'].default_value=0.55
    vec=geo.outputs['Position']
    if aniso:
        mp=_n(nt,"ShaderNodeMapping",0,250); mp.inputs['Scale'].default_value=aniso; nt.links.new(geo.outputs['Position'],mp.inputs['Vector']); vec=mp.outputs['Vector']
    nt.links.new(vec,nz.inputs['Vector'])
    mr=_n(nt,"ShaderNodeMapRange",350,250); mr.inputs['From Min'].default_value=0.32; mr.inputs['From Max'].default_value=0.68
    nt.links.new(nz.outputs['Fac'],mr.inputs['Value'])
    ramp=_n(nt,"ShaderNodeValToRGB",550,250); ramp.color_ramp.elements[0].color=_scale(base,var[0]); ramp.color_ramp.elements[1].color=_scale(base,var[1])
    nt.links.new(mr.outputs['Result'],ramp.inputs['Fac']); cur=ramp.outputs['Color']
    if grain>0:
        fz=_n(nt,"ShaderNodeTexNoise",150,-50); fz.inputs['Scale'].default_value=70.0; fz.inputs['Detail'].default_value=3.0; nt.links.new(geo.outputs['Position'],fz.inputs['Vector'])
        fm=_n(nt,"ShaderNodeMapRange",350,-50); fm.inputs['From Min'].default_value=0.3; fm.inputs['From Max'].default_value=0.7; fm.inputs['To Min'].default_value=1.0-grain; fm.inputs['To Max'].default_value=1.0+grain
        nt.links.new(fz.outputs['Fac'],fm.inputs['Value'])
        cc=_n(nt,"ShaderNodeCombineColor",550,-50)
        for i in range(3): nt.links.new(fm.outputs['Result'],cc.inputs[i])
        mx=_n(nt,"ShaderNodeMix",800,200); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs[0].default_value=1.0
        nt.links.new(cur,mx.inputs[6]); nt.links.new(cc.outputs['Color'],mx.inputs[7]); cur=mx.outputs[2]
    if edge:
        bev=_n(nt,"ShaderNodeBevel",800,-450); bev.inputs['Radius'].default_value=edge_w; bev.samples=4
        dt=_n(nt,"ShaderNodeVectorMath",1000,-450); dt.operation='DOT_PRODUCT'; nt.links.new(bev.outputs['Normal'],dt.inputs[0]); nt.links.new(geo.outputs['Normal'],dt.inputs[1])
        em=_n(nt,"ShaderNodeMapRange",1200,-450); em.inputs['From Min'].default_value=0.9985; em.inputs['From Max'].default_value=0.94
        nt.links.new(dt.outputs['Value'],em.inputs['Value'])
        e1=_n(nt,"ShaderNodeMix",1400,150); e1.data_type='RGBA'; e1.inputs[7].default_value=(*edge,1.0)
        nt.links.new(cur,e1.inputs[6]); nt.links.new(em.outputs['Result'],e1.inputs[0]); cur=e1.outputs[2]
    if grime>0:
        sep=_n(nt,"ShaderNodeSeparateXYZ",150,-250); nt.links.new(geo.outputs['Position'],sep.inputs['Vector'])
        gz=_n(nt,"ShaderNodeMapRange",350,-250); gz.inputs['From Min'].default_value=zfloor; gz.inputs['From Max'].default_value=zfloor+0.7; gz.inputs['To Min'].default_value=1.0; gz.inputs['To Max'].default_value=0.0
        nt.links.new(sep.outputs['Z'],gz.inputs['Value'])
        gm=_n(nt,"ShaderNodeMath",550,-250); gm.operation='MULTIPLY'; gm.inputs[1].default_value=grime; nt.links.new(gz.outputs['Result'],gm.inputs[0])
        g1=_n(nt,"ShaderNodeMix",1600,150); g1.data_type='RGBA'; g1.inputs[7].default_value=_scale(base,0.35)
        nt.links.new(cur,g1.inputs[6]); nt.links.new(gm.outputs['Value'],g1.inputs[0]); cur=g1.outputs[2]
    nt.links.new(cur,b.inputs['Base Color'])
    rz=_n(nt,"ShaderNodeTexNoise",150,-650); rz.inputs['Scale'].default_value=4.0; rz.inputs['Detail'].default_value=2.0; nt.links.new(geo.outputs['Position'],rz.inputs['Vector'])
    rr=_n(nt,"ShaderNodeMapRange",350,-650); rr.inputs['From Min'].default_value=0.3; rr.inputs['From Max'].default_value=0.7
    rr.inputs['To Min'].default_value=max(0.05,rough*(1-rvar)); rr.inputs['To Max'].default_value=min(1.0,rough*(1+rvar)); nt.links.new(rz.outputs['Fac'],rr.inputs['Value']); nt.links.new(rr.outputs['Result'],b.inputs['Roughness'])
    if bump>0 and metal<0.5:
        bz=_n(nt,"ShaderNodeTexNoise",150,-850); bz.inputs['Scale'].default_value=140.0; bz.inputs['Detail'].default_value=3.0; nt.links.new(geo.outputs['Position'],bz.inputs['Vector'])
        bp=_n(nt,"ShaderNodeBump",1300,-750); bp.inputs['Strength'].default_value=bump; bp.inputs['Distance'].default_value=0.02
        nt.links.new(bz.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
    return m
def tex_mat(name,img,rough=0.7,metal=0.0,emit=0.0,scale=(1,1),bump=0.0,clamp=True):
    m=_new(name); nt=m.node_tree
    out=_n(nt,"ShaderNodeOutputMaterial",900,0); b=_n(nt,"ShaderNodeBsdfPrincipled",600,0); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    uv=_n(nt,"ShaderNodeTexCoord",-500,0)
    tx=_n(nt,"ShaderNodeTexImage",-200,0); tx.image=img; tx.interpolation='Linear'
    if clamp: tx.extension='EXTEND'
    nt.links.new(uv.outputs['UV'],tx.inputs[0]); nt.links.new(tx.outputs['Color'],b.inputs['Base Color'])
    if emit>0:
        nt.links.new(tx.outputs['Color'],b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value=emit
    return m
def decal_mat(name,img,rough=0.85,emit=0.0):
    """image with alpha on a plane (stains, floor paint, stencils); Principled alpha, no geometry needed"""
    m=_new(name); nt=m.node_tree
    out=_n(nt,"ShaderNodeOutputMaterial",900,0); b=_n(nt,"ShaderNodeBsdfPrincipled",600,0); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    b.inputs['Roughness'].default_value=rough
    uv=_n(nt,"ShaderNodeTexCoord",-500,0); tx=_n(nt,"ShaderNodeTexImage",-200,0); tx.image=img; tx.extension='EXTEND'
    nt.links.new(uv.outputs['UV'],tx.inputs[0]); nt.links.new(tx.outputs['Color'],b.inputs['Base Color']); nt.links.new(tx.outputs['Alpha'],b.inputs['Alpha'])
    if emit>0: nt.links.new(tx.outputs['Color'],b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value=emit
    return m
def _fps_vars(d):
    """scene frame-rate variables so that drivers can work in seconds: seconds = frame*fb/fps"""
    for nm,dp in (("fps","render.fps"),("fb","render.fps_base")):
        v=d.variables.new(); v.name=nm; v.type='SINGLE_PROP'; v.targets[0].id_type='SCENE'; v.targets[0].id=bpy.context.scene; v.targets[0].data_path=dp
def to_seconds(expr):
    """All control-room driver expressions are TIME based, never frame based.
    Write `T` for scene time in seconds.  Legacy `frame` (older constants were tuned at 30 fps) is mapped to `T*30`, so the look is unchanged at 30 fps
    and identical in real time at every other frame rate."""
    import re
    e=re.sub(r'\bframe\b','(T*30)',expr)
    return re.sub(r'\bT\b','(frame*fb/fps)',e)
import re
def setup_flicker():
    """two shared time signals on REACTOR_STATE: cr_flick (fast tube stutter bursts) and cr_brown (slow brownout dips, ~0..1); both in seconds"""
    for nm,ex in (("cr_flick","max(0,sin(T*81)*sin(T*15.9)*sin(T*5.7+1)-0.42)*3"),("cr_brown","max(0,sin(T*2.1)*sin(T*5.3+1)-0.45)*1.8")):
        STATE[nm]=0.0
        try: STATE.driver_remove('["%s"]'%nm)
        except Exception: pass
        drv(STATE,'["%s"]'%nm,None,ex,var_s=False)
def drv(idblock,path,idx,expr,var_s=True,extra=None):
    fc=idblock.driver_add(path,idx) if idx is not None else idblock.driver_add(path)
    d=fc.driver; d.type='SCRIPTED'
    if var_s:
        v=d.variables.new(); v.name='s'; v.type='SINGLE_PROP'; v.targets[0].id=STATE; v.targets[0].data_path='["stability"]'
    for (nm,ident,dp) in (extra or []):
        v=d.variables.new(); v.name=nm; v.type='SINGLE_PROP'; v.targets[0].id=ident; v.targets[0].data_path=dp
    for nm,pr in (("fk","cr_flick"),("bw","cr_brown")):          # shared flicker / brownout signals (props on REACTOR_STATE, see setup_flicker)
        if re.search(r'\b%s\b'%nm,expr) and not any(v.name==nm for v in d.variables):
            v=d.variables.new(); v.name=nm; v.type='SINGLE_PROP'; v.targets[0].id=STATE; v.targets[0].data_path='["%s"]'%pr
    ex=to_seconds(expr)
    if ex!=expr: _fps_vars(d)
    d.expression=ex; return fc
def emit_mat(name,rgb,strength,expr=None,base=None,use_s=False):
    m=_new(name); nt=m.node_tree
    out=_n(nt,"ShaderNodeOutputMaterial",600,0); b=_n(nt,"ShaderNodeBsdfPrincipled",300,0); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    b.inputs['Base Color'].default_value=(*(base or [c*0.12 for c in rgb]),1); b.inputs['Emission Color'].default_value=(*rgb,1); b.inputs['Emission Strength'].default_value=strength; b.inputs['Roughness'].default_value=0.4
    if expr: drv(nt,'nodes["Principled BSDF"].inputs["Emission Strength"].default_value',None,expr,var_s=use_s)
    return m
def glass_mat(name,tint=(0.62,0.72,0.70),rough=0.03,alpha=0.12):
    m=_new(name); nt=m.node_tree
    out=_n(nt,"ShaderNodeOutputMaterial",600,0); b=_n(nt,"ShaderNodeBsdfPrincipled",300,0); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    b.inputs['Base Color'].default_value=(*tint,1); b.inputs['Roughness'].default_value=rough; b.inputs['Alpha'].default_value=alpha; b.inputs['IOR'].default_value=1.45
    m.blend_method='BLEND' if hasattr(m,'blend_method') else None
    return m
# ------------------------------------------------------------------ images
def new_image(name,arr,cs='sRGB'):
    """arr: HxWx3/4 float array (4th channel = alpha), row 0 = TOP."""
    h,w=arr.shape[:2]; has_a=arr.shape[2]==4
    if arr.shape[2]==3: arr=np.concatenate([arr,np.ones((h,w,1),dtype=arr.dtype)],axis=2)
    im=bpy.data.images.get(name)
    if im: bpy.data.images.remove(im)
    im=bpy.data.images.new(name,w,h,alpha=has_a); im.colorspace_settings.name=cs
    if has_a: im.alpha_mode='STRAIGHT'
    im.pixels.foreach_set(np.flipud(arr).astype(np.float32).reshape(-1)); im.pack(); return im
# ------------------------------------------------------------------ text / lights
RZ={'-y':0.0,'+y':math.pi,'-x':-math.pi/2,'+x':math.pi/2}
TEXTS=[]
def text(coll,body,x,y,z,facing,size,mat,align='CENTER',name="CR text",rollz=0.0,spacing=1.0):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.size=size; cu.align_x=align; cu.align_y='CENTER'; cu.extrude=0.0; cu.resolution_u=2; cu.space_character=spacing
    ob=bpy.data.objects.new(name,cu); ob.location=(x,y,z); ob.rotation_euler=(math.pi/2,rollz,RZ[facing]); coll.objects.link(ob); cu.materials.append(mat); TEXTS.append(ob); return ob
def mesh_texts():
    """convert the text curves created so far to meshes (portable to the engine export)"""
    if not TEXTS: return
    bpy.ops.object.select_all(action='DESELECT')
    for o in TEXTS:
        if o.name in bpy.context.view_layer.objects: o.select_set(True)
    bpy.context.view_layer.objects.active=TEXTS[0]
    bpy.ops.object.convert(target='MESH'); TEXTS.clear()
def light(coll,name,loc,rgb,energy,kind='POINT',rot=None,spot=None,blend=0.5,size=None,soft=0.1,expr=None,var_s=False):
    ld=bpy.data.lights.new(name,kind); ld.color=rgb; ld.energy=energy
    if kind in('POINT','SPOT'): ld.shadow_soft_size=soft
    if kind=='SPOT': ld.spot_size=math.radians(spot or 80); ld.spot_blend=blend
    if kind=='AREA': ld.shape='RECTANGLE'; ld.size,ld.size_y=size
    lo=bpy.data.objects.new(name,ld); lo.location=loc
    if rot: lo.rotation_euler=rot
    coll.objects.link(lo)
    if expr: drv(ld,'energy',None,expr,var_s=var_s)
    return lo
def stab_expr(i): return ("min(1,2*(1-s)+0.24)","0.03+0.92*s","0.20*s")[i]
