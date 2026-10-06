"""Reactor hall pass, FLOOR stage: wet weathered concrete slab with rain puddles, draining grates and worn safety paint.
usage: python rh_floor.py -- <in.blend> <out.blend>        (deterministic, re-runnable; owns object 'R2 floor' and every 'RH floor ...' object)

What it builds
  * 'R2 floor' (same object, same collection) gets a NEW mesh: a 0.45 m thick octagonal slab with the r 3.95 pool opening, expansion joints on a 4.5 m grid cut as real grooves,
    a trench-drain ring (r 4.12-4.50) round the pool, three straight trench runs to wall catch basins, square / round point drains, two manhole rebates, a cable trench
    and a hatch pit.  All recesses are made with an exact boolean, so there is real depth (trench floor -0.32 m, drain pits -0.40 m).
  * 'RH floor ...' objects: bar gratings with frames and anchor bolts, manhole covers, cable-trench chequer plates, worn safety paint (yellow / white / black), all joined per (group, material).
  * one slab shader (cracks, aggregate, trowel, oil, rust, scuffs, joints, dry matte vs wet sheen, mirror puddles with soft edges / meniscus, ripples) built on the node group
    'RH floor wet'.  Ripples are driven by scene SECONDS: a Value node inside that group is driven through crk.drv with `T` (never the raw frame).
Colour rules: concrete greys / browns, safety yellow, white, black, rust.  No teal / cyan / blue / purple anywhere."""
import bpy,bmesh,sys,os,math,random
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import crk,rh_mats,r2lib
from mathutils import Vector
A=sys.argv[sys.argv.index("--")+1:]
bpy.ops.wm.open_mainfile(filepath=A[0])
sc=bpy.context.scene
crk.STATE=bpy.data.objects.get('REACTOR_STATE')
COLL_NAME="23 R2 FLOOR AND DRESSING"
TOP=0.0; SLAB_T=0.45
# ----------------------------------------------------------------------------------------------------------------------------- layout (metres)
RING=(4.12,4.50)                                   # trench drain ring round the pool
RUNS=[(45.0,7.5),(135.0,7.5),("S",3.0)]            # trench runs: (angle deg, end radius along the axis) or ("S", x) = straight south run at x
RUN_W=0.34
POINT_SQ=[(6.6,-4.2),(-5.6,-3.4),(-6.2,3.9)]       # square point drains (0.54 pit)
POINT_RD=[(5.6,2.6),(-2.6,7.0),(2.2,-6.4)]         # round point drains
MANHOLES=[(-6.2,-1.9),(7.2,4.4)]
CABLE_TR=[(5.4,9.2,-2.0)]                          # (x0,x1,y) cable trench running in x
CABLE_TR_Y=[(2.0,5.0,8.3)]                         # reuse (x0,x1,y) running in x further north
HATCH=(-4.2,7.7)
JOINT=4.5; JW=0.022; JD=0.03
PUD=[ # cx,cy,rx,ry,rot : irregular rain puddles in low spots, beside drains and along the walkways
 (6.3,-3.7,1.15,0.72,0.5),(-5.4,-2.6,1.3,0.8,-0.3),(-3.0,4.7,1.2,0.7,0.8),(3.4,-5.6,1.5,0.7,0.1),(5.2,4.9,1.5,0.9,0.7),
 (-5.9,5.2,1.3,0.8,-0.7),(0.5,7.0,1.3,0.75,0.3),(7.6,0.2,1.6,0.8,0.1),(-8.0,-0.6,1.2,0.6,0.2),(1.9,-8.0,1.2,0.6,-0.2),
 (-1.2,-6.7,1.0,0.55,0.4),(4.7,-8.4,1.1,0.6,0.9),(-7.4,8.0,0.9,0.5,0.2),(2.3,3.5,0.5,0.35,0.0),(-3.2,-5.2,0.7,0.45,0.6)]
DRAINS=[(6.6,-4.2),(-5.6,-3.4),(-6.2,3.9),(5.6,2.6),(-2.6,7.0),(2.2,-6.4),(5.3,5.3),(-5.3,5.3),(3.0,-7.4),(-6.2,-1.9),(7.2,4.4)]
# ----------------------------------------------------------------------------------------------------------------------------- node builder
class NB:
    def __init__(s,nt): s.nt=nt; s.i=0
    def n(s,t,**kw):
        o=s.nt.nodes.new(t); o.location=((s.i%16)*210,-(s.i//16)*240); s.i+=1
        for k,v in kw.items(): setattr(o,k,v)
        return o
    def _s(s,inp,v):
        if v is None: return
        if isinstance(v,bpy.types.NodeSocket): s.nt.links.new(v,inp)
        else:
            if inp.type=='RGBA' and not isinstance(v,(int,float)) and len(v)==3: v=(*v,1.0)
            inp.default_value=v
    def M(s,op,a,b=None,c=None,clamp=False):
        n=s.n('ShaderNodeMath',operation=op,use_clamp=clamp); s._s(n.inputs[0],a); s._s(n.inputs[1],b); s._s(n.inputs[2],c); return n.outputs[0]
    def V(s,op,a,b=None,scale=None):
        n=s.n('ShaderNodeVectorMath',operation=op); s._s(n.inputs[0],a); s._s(n.inputs[1],b)
        if scale is not None: s._s(n.inputs[3],scale)
        return n.outputs[0]
    def L(s,a): n=s.n('ShaderNodeVectorMath',operation='LENGTH'); s._s(n.inputs[0],a); return n.outputs[1]
    def R(s,v,a,b,c,d,smooth=False,clamp=True):
        n=s.n('ShaderNodeMapRange',data_type='FLOAT',interpolation_type='SMOOTHSTEP' if smooth else 'LINEAR',clamp=clamp)
        for i,x in enumerate((v,a,b,c,d)): s._s(n.inputs[i],x)
        return n.outputs[0]
    def Xc(s,f,a,b): n=s.n('ShaderNodeMix',data_type='RGBA'); s._s(n.inputs[0],f); s._s(n.inputs[6],a); s._s(n.inputs[7],b); return n.outputs[2]
    def Xf(s,f,a,b): n=s.n('ShaderNodeMix',data_type='FLOAT'); s._s(n.inputs[0],f); s._s(n.inputs[2],a); s._s(n.inputs[3],b); return n.outputs[0]
    def noise(s,vec,scale,detail=4.0,rough=0.55,out=0):
        n=s.n('ShaderNodeTexNoise',noise_dimensions='3D'); n.inputs['Scale'].default_value=scale; n.inputs['Detail'].default_value=detail; n.inputs['Roughness'].default_value=rough
        s._s(n.inputs['Vector'],vec); return n.outputs[out]
    def vor(s,vec,scale,feature='F1',rnd=1.0):
        n=s.n('ShaderNodeTexVoronoi',voronoi_dimensions='3D',feature=feature); n.inputs['Scale'].default_value=scale; n.inputs['Randomness'].default_value=rnd; s._s(n.inputs['Vector'],vec); return n
    def mapping(s,vec,rot_z=0.0,scale=(1,1,1),loc=(0,0,0)):
        n=s.n('ShaderNodeMapping'); n.inputs['Rotation'].default_value=(0,0,rot_z); n.inputs['Scale'].default_value=scale; n.inputs['Location'].default_value=loc; s._s(n.inputs['Vector'],vec); return n.outputs[0]
    def sep(s,v): n=s.n('ShaderNodeSeparateXYZ'); s._s(n.inputs[0],v); return n.outputs[0],n.outputs[1],n.outputs[2]
    def comb(s,x,y,z): n=s.n('ShaderNodeCombineXYZ'); s._s(n.inputs[0],x); s._s(n.inputs[1],y); s._s(n.inputs[2],z); return n.outputs[0]
def cc(v,k=1.0): return (v[0]*k,v[1]*k,v[2]*k)
# ----------------------------------------------------------------------------------------------------------------------------- wet node group (puddles, damp, ripples)
def wet_group():
    old=bpy.data.node_groups.get("RH floor wet")
    if old: bpy.data.node_groups.remove(old)
    ng=bpy.data.node_groups.new("RH floor wet",'ShaderNodeTree')
    for nm in ("Puddle","Damp","Rim","Ripple","DrainProx","Streak"): ng.interface.new_socket(nm,in_out='OUTPUT',socket_type='NodeSocketFloat')
    nb=NB(ng); go=nb.n('NodeGroupOutput')
    pos=nb.n('ShaderNodeNewGeometry').outputs['Position']
    half=(0.5,0.5,0.5)
    w1=nb.noise(pos,0.75,3.0,0.5,out=1); w2=nb.noise(pos,4.5,3.0,0.5,out=1)
    wv=nb.V('MULTIPLY',nb.V('SUBTRACT',w1,half),(1.7,1.7,0.0)); wv2=nb.V('MULTIPLY',nb.V('SUBTRACT',w2,half),(0.30,0.30,0.0))
    pw=nb.V('ADD',pos,nb.V('ADD',wv,wv2))
    F=None
    for (cx,cy,rx,ry,rot) in PUD:
        d=nb.V('SUBTRACT',pw,(cx,cy,0.0)); r=nb.n('ShaderNodeVectorRotate',rotation_type='Z_AXIS'); nb._s(r.inputs['Vector'],d); r.inputs['Angle'].default_value=-rot
        L=nb.L(nb.V('MULTIPLY',r.outputs[0],(1.0/rx,1.0/ry,0.0)))
        F=L if F is None else nb.M('MINIMUM',F,L)
    puddle=nb.R(F,1.0,0.80,0.0,1.0,smooth=True)
    halo=nb.R(F,2.6,0.95,0.0,0.85,smooth=True)
    DD=None
    for (dx,dy) in DRAINS:
        L=nb.L(nb.V('SUBTRACT',pos,(dx,dy,0.0))); DD=L if DD is None else nb.M('MINIMUM',DD,L)
    dprox=nb.R(DD,1.7,0.25,0.0,1.0,smooth=True)
    patch=nb.R(nb.noise(pos,0.9,3.0,0.55),0.35,0.65,0.45,1.0)
    dampd=nb.M('MULTIPLY',nb.R(DD,2.3,0.3,0.0,0.95,smooth=True),patch)
    # wet streak trails: noise stretched along a walking direction, gated to some places only
    sm=nb.mapping(pos,rot_z=0.55,scale=(0.30,3.2,1.0)); streak=nb.R(nb.noise(sm,1.1,3.0,0.5),0.46,0.56,0.0,1.0,smooth=True)
    sm2=nb.mapping(pos,rot_z=-1.05,scale=(0.28,3.6,1.0),loc=(3.0,7.0,0.0)); streak2=nb.R(nb.noise(sm2,1.1,3.0,0.5),0.48,0.58,0.0,1.0,smooth=True)
    gate=nb.R(nb.noise(pos,0.22,3.0,0.5),0.40,0.58,0.0,1.0,smooth=True)
    streak=nb.M('MULTIPLY',nb.M('MAXIMUM',streak,streak2),gate)
    damp=nb.M('MAXIMUM',nb.M('MAXIMUM',halo,dampd),nb.M('MULTIPLY',streak,0.85))
    rim=nb.M('MULTIPLY',nb.M('MULTIPLY',puddle,nb.M('SUBTRACT',1.0,puddle)),4.0)
    # ripples: drip points on a jittered grid (Voronoi feature points), each one emitting an expanding ring every ~1.7 s, driven by scene seconds
    T=nb.n('ShaderNodeValue'); T.name="RH T seconds"; T.label="T (seconds, driven)"
    v=nb.vor(pos,0.85); dist=nb.M('DIVIDE',v.outputs['Distance'],0.85)
    sc_=nb.n('ShaderNodeSeparateColor'); nb._s(sc_.inputs[0],v.outputs['Color']); ph=sc_.outputs[0]; amp=nb.R(sc_.outputs[1],0.15,0.35,0.0,1.0)
    age=nb.M('FRACT',nb.M('ADD',nb.M('MULTIPLY',T.outputs[0],0.6),nb.M('MULTIPLY',ph,5.0)))
    delta=nb.M('SUBTRACT',dist,nb.M('MULTIPLY',age,0.5))
    wave=nb.M('SINE',nb.M('MULTIPLY',delta,72.0)); env=nb.M('EXPONENT',nb.M('MULTIPLY',nb.M('MULTIPLY',delta,delta),-200.0))
    fade=nb.M('POWER',nb.M('SUBTRACT',1.0,age),2.0)
    rip=nb.M('MULTIPLY',nb.M('MULTIPLY',wave,env),nb.M('MULTIPLY',fade,amp))
    for nm,val in (("Puddle",puddle),("Damp",damp),("Rim",rim),("Ripple",rip),("DrainProx",dprox),("Streak",streak)): ng.links.new(val,go.inputs[nm])
    crk.drv(ng,'nodes["RH T seconds"].outputs[0].default_value',None,'T',var_s=False)
    return ng
def group_node(nb,ng):
    g=nb.n('ShaderNodeGroup'); g.node_tree=ng; return g
# ----------------------------------------------------------------------------------------------------------------------------- materials
def new_mat(name):
    m=bpy.data.materials.get(name)
    if m: bpy.data.materials.remove(m)
    m=bpy.data.materials.new(name); m.use_nodes=True; m.node_tree.nodes.clear(); return m
def slab_mat(ng):
    m=new_mat("RH floor wet concrete"); nt=m.node_tree; nb=NB(nt)
    out=nb.n('ShaderNodeOutputMaterial'); b=nb.n('ShaderNodeBsdfPrincipled'); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    pos=nb.n('ShaderNodeNewGeometry').outputs['Position']; x,y,z=nb.sep(pos)
    g=group_node(nb,ng); puddle=g.outputs['Puddle']; damp=g.outputs['Damp']; ripple=g.outputs['Ripple']; dprox=g.outputs['DrainProx']; streak=g.outputs['Streak']
    # --- albedo: weathered concrete, big mottling + medium cloud + aggregate speckle + trowel drift
    base=(0.245,0.238,0.218)
    big=nb.R(nb.noise(pos,0.33,4.0,0.55),0.30,0.70,0.72,1.22); med=nb.R(nb.noise(pos,2.3,6.0,0.6),0.30,0.70,0.88,1.10)
    vag=nb.vor(pos,95.0); sepc=nb.n('ShaderNodeSeparateColor'); nt.links.new(vag.outputs['Color'],sepc.inputs[0]); agg=nb.R(sepc.outputs[0],0.0,1.0,0.84,1.16)
    tm=nb.mapping(pos,rot_z=0.5,scale=(0.7,5.0,1.0)); trowel=nb.noise(tm,1.0,3.0,0.5)
    tcol=nb.R(trowel,0.3,0.7,0.94,1.06)
    shade=nb.M('MULTIPLY',nb.M('MULTIPLY',big,med),nb.M('MULTIPLY',agg,tcol))
    col=nb.V('SCALE',base,scale=shade)
    # warm / cool drift (browns only)
    warm=nb.R(nb.noise(pos,0.5,2.0,0.5),0.35,0.65,0.0,1.0)
    col=nb.Xc(nb.M('MULTIPLY',warm,0.45),col,(0.24,0.20,0.15))
    # --- stains
    oil=nb.R(nb.noise(nb.V('ADD',pos,(13.0,7.0,0.0)),0.85,5.0,0.6),0.60,0.68,0.0,1.0,smooth=True)
    rr=nb.M('ABSOLUTE',nb.M('SUBTRACT',nb.L(nb.V('MULTIPLY',pos,(1.0,1.0,0.0))),4.3)); ringprox=nb.R(rr,1.5,0.15,0.0,1.0,smooth=True)
    rustp=nb.M('MAXIMUM',ringprox,nb.M('MAXIMUM',dprox,0.12))
    rust=nb.M('MULTIPLY',nb.R(nb.noise(nb.V('ADD',pos,(-9.0,4.0,0.0)),1.6,5.0,0.6),0.52,0.66,0.0,1.0,smooth=True),rustp)
    sc1=nb.mapping(pos,rot_z=0.6,scale=(0.5,9.0,1.0)); sc2=nb.mapping(pos,rot_z=-0.95,scale=(0.45,10.0,1.0),loc=(5,3,0))
    scuff=nb.M('MAXIMUM',nb.R(nb.noise(sc1,1.0,3.0,0.5),0.60,0.66,0.0,1.0),nb.R(nb.noise(sc2,1.0,3.0,0.5),0.62,0.68,0.0,1.0))
    scuff=nb.M('MULTIPLY',scuff,nb.R(nb.noise(pos,0.3,2.0,0.5),0.35,0.65,0.0,1.0))
    # hairline cracks (Voronoi cell borders, warped), only in some zones
    wpos=nb.V('ADD',pos,nb.V('MULTIPLY',nb.V('SUBTRACT',nb.noise(pos,3.0,4.0,0.5,out=1),(0.5,0.5,0.5)),(0.35,0.35,0.0)))
    ve=nb.vor(wpos,0.5,'DISTANCE_TO_EDGE'); crk1=nb.R(ve.outputs['Distance'],0.0065,0.0015,0.0,0.85)
    ve2=nb.vor(wpos,1.6,'DISTANCE_TO_EDGE'); crk2=nb.R(ve2.outputs['Distance'],0.009,0.002,0.0,0.5)
    czone=nb.R(nb.noise(pos,0.27,3.0,0.5),0.55,0.68,0.0,1.0,smooth=True)
    crack=nb.M('MULTIPLY',nb.M('MAXIMUM',crk1,crk2),czone)
    # expansion joints on a 4.5 m grid: distance to nearest grid line in x / y
    def gl(c):
        u=nb.M('DIVIDE',nb.M('ADD',c,JOINT/2),JOINT); return nb.M('MULTIPLY',nb.M('ABSOLUTE',nb.M('SUBTRACT',u,nb.M('ROUND',u))),JOINT)
    jd=nb.M('MINIMUM',gl(x),gl(y)); joint=nb.R(jd,0.016,0.008,0.0,1.0,smooth=True); jedge=nb.R(jd,0.07,0.012,0.0,0.6,smooth=True)
    below=nb.R(z,-0.02,-0.10,0.0,1.0,smooth=True); water=nb.R(z,-0.22,-0.28,0.0,1.0)       # inside trenches / pits: wet dark void, standing water at the bottom
    # compose albedo
    col=nb.Xc(nb.M('MULTIPLY',jedge,0.55),col,cc(base,0.45))
    col=nb.Xc(nb.M('MULTIPLY',nb.M('MULTIPLY',scuff,0.55),nb.M('SUBTRACT',1.0,puddle)),col,(0.035,0.033,0.03))
    col=nb.Xc(nb.M('MULTIPLY',oil,0.92),col,(0.020,0.017,0.012))
    col=nb.Xc(nb.M('MULTIPLY',rust,0.85),col,(0.20,0.075,0.028))
    col=nb.Xc(nb.M('MULTIPLY',damp,0.42),col,nb.V('SCALE',col,scale=0.50))
    col=nb.Xc(nb.M('MULTIPLY',nb.M('MAXIMUM',crack,joint),0.92),col,(0.014,0.013,0.012))
    col=nb.Xc(puddle,col,nb.V('SCALE',col,scale=0.33))
    col=nb.Xc(nb.M('MULTIPLY',below,0.95),col,(0.012,0.012,0.011))
    nt.links.new(col,b.inputs['Base Color'])
    # --- roughness: dry matte patches vs damp sheen vs oil slick vs mirror puddles
    rdry=nb.R(nb.noise(pos,1.3,4.0,0.55),0.30,0.70,0.72,1.0); rdry=nb.M('MULTIPLY',rdry,nb.R(trowel,0.3,0.7,0.88,1.0))
    rough=nb.Xf(nb.M('MULTIPLY',damp,0.88),rdry,0.30)
    rough=nb.Xf(nb.M('MULTIPLY',oil,0.8),rough,0.16)
    rough=nb.Xf(nb.M('MULTIPLY',rust,0.6),rough,0.80)
    rough=nb.Xf(nb.M('MULTIPLY',nb.M('MAXIMUM',crack,joint),0.9),rough,0.95)
    rough=nb.Xf(puddle,rough,0.02)
    rough=nb.Xf(below,rough,0.10); rough=nb.Xf(water,rough,0.02)
    nt.links.new(rough,b.inputs['Roughness'])
    nt.links.new(nb.Xf(puddle,0.5,0.55),b.inputs['Specular IOR Level']); b.inputs['IOR'].default_value=1.33
    # --- relief: fine grain + aggregate + hairlines + joints in the dry, expanding ripple rings in the puddles / trench water
    grain=nb.noise(pos,160.0,5.0,0.6); aggd=nb.R(vag.outputs['Distance'],0.0,0.7,0.0,1.0)
    wetm=nb.M('MAXIMUM',puddle,water)
    h=nb.M('SUBTRACT',nb.M('ADD',nb.M('MULTIPLY',grain,0.6),nb.M('MULTIPLY',aggd,0.45)),nb.M('ADD',nb.M('MULTIPLY',crack,0.9),nb.M('MULTIPLY',joint,1.2)))
    h=nb.M('ADD',nb.M('MULTIPLY',h,nb.M('SUBTRACT',1.0,nb.M('MULTIPLY',wetm,0.92))),nb.M('MULTIPLY',nb.M('MULTIPLY',ripple,wetm),1.0))
    bp=nb.n('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.55; bp.inputs['Distance'].default_value=0.008; nt.links.new(h,bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
    return m
def paint_mat(name,rgb,rough=0.78):
    m=new_mat(name); nt=m.node_tree; nb=NB(nt)
    out=nb.n('ShaderNodeOutputMaterial'); b=nb.n('ShaderNodeBsdfPrincipled'); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    pos=nb.n('ShaderNodeNewGeometry').outputs['Position']; g=group_node(nb,bpy.data.node_groups["RH floor wet"])
    puddle=g.outputs['Puddle']; damp=g.outputs['Damp']; ripple=g.outputs['Ripple']
    # wear: broken, chipped edges (alpha reveals the slab), scuffed and dirty, heavier in traffic bands
    wn=nb.noise(pos,3.2,6.0,0.6); wf=nb.noise(pos,38.0,4.0,0.55); sc1=nb.mapping(pos,rot_z=0.4,scale=(0.6,14.0,1.0)); ws=nb.noise(sc1,1.0,3.0,0.5)
    gone=nb.M('ADD',nb.R(wn,0.58,0.80,0.0,0.9),nb.M('MULTIPLY',nb.R(wf,0.55,0.75,0.0,0.5),nb.R(wn,0.35,0.6,0.0,1.0)))
    gone=nb.M('ADD',gone,nb.M('MULTIPLY',nb.R(ws,0.60,0.7,0.0,0.6),0.8))
    alpha=nb.R(gone,0.85,1.35,1.0,0.0,smooth=True)
    dirt=nb.R(nb.noise(pos,1.7,5.0,0.6),0.3,0.7,0.0,0.5)
    col=nb.Xc(dirt,rgb,(0.045,0.040,0.030)); col=nb.Xc(nb.M('MULTIPLY',damp,0.4),col,nb.V('SCALE',col,scale=0.5))
    col=nb.Xc(puddle,col,nb.V('SCALE',col,scale=0.5))
    nt.links.new(col,b.inputs['Base Color']); nt.links.new(alpha,b.inputs['Alpha'])
    r=nb.Xf(nb.M('MULTIPLY',damp,0.8),rough,0.30); r=nb.Xf(puddle,r,0.02); nt.links.new(r,b.inputs['Roughness'])
    h=nb.M('ADD',nb.M('MULTIPLY',wf,0.35),nb.M('MULTIPLY',nb.M('MULTIPLY',ripple,puddle),1.0))
    bp=nb.n('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.4; bp.inputs['Distance'].default_value=0.006; nt.links.new(h,bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
    return m
# ----------------------------------------------------------------------------------------------------------------------------- geometry helpers
def cbox(bm,cx,cy,z0,z1,sx,sy,ang=0.0):
    r=bmesh.ops.create_cube(bm,size=1.0); c,s=math.cos(ang),math.sin(ang)
    for v in r['verts']:
        lx=v.co.x*sx; ly=v.co.y*sy; v.co=Vector((cx+lx*c-ly*s,cy+lx*s+ly*c,z0+(v.co.z+.5)*(z1-z0)))
def ccyl(bm,cx,cy,z0,z1,rad,seg=48):
    r=bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=rad,radius2=rad,depth=1.0)
    for v in r['verts']: v.co=Vector((cx+v.co.x,cy+v.co.y,z0+(v.co.z+.5)*(z1-z0)))
def cbox(bm,cx,cy,z0,z1,sx,sy,ang=0.0):
    r=bmesh.ops.create_cube(bm,size=1.0); c,s=math.cos(ang),math.sin(ang)
    for v in r['verts']:
        lx=v.co.x*sx; ly=v.co.y*sy; v.co=Vector((cx+lx*c-ly*s,cy+lx*s+ly*c,z0+(v.co.z+.5)*(z1-z0)))
def ccyl(bm,cx,cy,z0,z1,rad,seg=48):
    r=bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=rad,radius2=rad,depth=1.0)
    for v in r['verts']: v.co=Vector((cx+v.co.x,cy+v.co.y,z0+(v.co.z+.5)*(z1-z0)))
def ringprism(bm,r0,r1,z0,z1,n=128,cx=0.0,cy=0.0):
    P=lambda r,k,z:bm.verts.new((cx+r*math.cos(2*math.pi*k/n),cy+r*math.sin(2*math.pi*k/n),z))
    ib=[P(r0,k,z0) for k in range(n)]; ob=[P(r1,k,z0) for k in range(n)]; it=[P(r0,k,z1) for k in range(n)]; ot=[P(r1,k,z1) for k in range(n)]
    for k in range(n):
        j=(k+1)%n
        bm.faces.new((it[k],it[j],ot[j],ot[k])); bm.faces.new((ib[k],ob[k],ob[j],ib[j])); bm.faces.new((it[k],ib[k],ib[j],it[j])); bm.faces.new((ot[k],ot[j],ob[j],ob[k]))
def arcbar(bm,r0,r1,a0,a1,z0,z1,step=0.10,cx=0.0,cy=0.0):
    n=max(1,int(abs(a1-a0)/step)+1); ang=[a0+(a1-a0)*i/n for i in range(n+1)]
    P=lambda r,a,z:bm.verts.new((cx+r*math.cos(a),cy+r*math.sin(a),z))
    ib=[P(r0,a,z0) for a in ang]; ob=[P(r1,a,z0) for a in ang]; it=[P(r0,a,z1) for a in ang]; ot=[P(r1,a,z1) for a in ang]
    for i in range(n):
        bm.faces.new((it[i],it[i+1],ot[i+1],ot[i])); bm.faces.new((ib[i],ob[i],ob[i+1],ib[i+1])); bm.faces.new((it[i],ib[i],ib[i+1],it[i+1])); bm.faces.new((ot[i],ot[i+1],ob[i+1],ob[i]))
    bm.faces.new((it[0],ot[0],ob[0],ib[0])); bm.faces.new((it[-1],ib[-1],ob[-1],ot[-1]))
def poly(bm,pts,z0,z1):
    b=[bm.verts.new((p[0],p[1],z0)) for p in pts]; t=[bm.verts.new((p[0],p[1],z1)) for p in pts]; n=len(pts)
    bm.faces.new(t); bm.faces.new(b[::-1])
    for i in range(n): j=(i+1)%n; bm.faces.new((b[i],b[j],t[j],t[i]))
K=crk.Kit()
def kb(grp,mk): return K.get((grp,mk))
RECT_BLOCK=[]                                                       # (cx,cy,hx,hy,ang): footprints of grates / pits; paint is not laid over them
def blocked(x,y,pad=0.06):
    for (cx,cy,hx,hy,a) in RECT_BLOCK:
        dx,dy=x-cx,y-cy; c,s=math.cos(-a),math.sin(-a); lx=dx*c-dy*s; ly=dx*s+dy*c
        if abs(lx)<hx+pad and abs(ly)<hy+pad: return True
    return False
# ----------------------------------------------------------------------------------------------------------------------------- cleanup of the old floor dressing this stage owns
def cleanup():
    kill=[]
    for o in bpy.data.objects:
        n=o.name
        if n.startswith("RH floor "): kill.append(o); continue
        if n.startswith(("R2 floor floor ring","R2 floor lane plate","R2 floor drain","R2 detail puddle")): kill.append(o); continue
        if n.startswith("MERGED 23 R2 FLOOR  R2 trim rust") and o.type=='MESH':
            zmax=max((o.matrix_world@Vector(v)).z for v in o.bound_box)
            if zmax<0.05: kill.append(o)
    for o in kill:
        me=o.data; bpy.data.objects.remove(o,do_unlink=True)
        if me and me.users==0: bpy.data.meshes.remove(me)
    return len(kill)
# ----------------------------------------------------------------------------------------------------------------------------- layout helpers
def run_axes():
    out=[]
    for r in RUNS:
        if r[0]=="S": p0=Vector((r[1],-3.3)); p1=Vector((r[1],-7.7)); ang=-math.pi/2
        else:
            a=math.radians(r[0]); ang=a; p0=Vector((math.cos(a),math.sin(a)))*4.3; p1=Vector((math.copysign(r[1],math.cos(a)),r[1]*math.copysign(1,math.sin(a))))
        out.append((p0,p1,ang))
    return out
def build():
    ng=wet_group(); slabm=slab_mat(ng)
    PY=paint_mat("RH floor paint yellow",(0.50,0.34,0.010)); PW=paint_mat("RH floor paint white",(0.40,0.395,0.36)); PK=paint_mat("RH floor paint black",(0.020,0.020,0.019))
    L=rh_mats.lib()
    WET=rh_mats.surf("RH floor wet iron",(0.034,0.030,0.027),0.42,0.72,mottle=0.6,streak=0.0,edge=(0.26,0.22,0.17),grime=0.0,scale=3.5,bump=0.01)
    mats={"WET":WET,"GALV":L["GALV"],"IRON":L["IRON"],"BLACK":L["BLACK"],"RUBBER":L["RUBBER"],"ORANGE":L["ORANGE"],"Y":PY,"W":PW,"K":PK}
    runs=run_axes()
    # ---------------- cutter: one mesh of overlapping closed pieces, self-union boolean
    cut=bmesh.new()
    ccyl(cut,0,0,-1.0,1.0,3.95,128)                                          # pool opening
    ringprism(cut,RING[0],RING[1],-0.32,0.1,128)                              # trench drain ring
    for c in (-6.75,-2.25,2.25,6.75): cbox(cut,c,0,-JD,0.1,JW,26.0); cbox(cut,0,c,-JD,0.1,26.0,JW)   # expansion joints on a 4.5 m grid
    for (p0,p1,ang) in runs:
        m=(p0+p1)/2; cbox(cut,m.x,m.y,-0.30,0.1,(p1-p0).length,RUN_W,ang); cbox(cut,p1.x,p1.y,-0.40,0.1,0.70,0.70,ang)
    for (x,y) in POINT_SQ: cbox(cut,x,y,-0.40,0.1,0.54,0.54); cbox(cut,x,y,-0.03,0.1,0.66,0.66)
    for (x,y) in POINT_RD: ccyl(cut,x,y,-0.40,0.1,0.20,32); ccyl(cut,x,y,-0.03,0.1,0.28,32)
    for (x,y) in MANHOLES: ccyl(cut,x,y,-0.05,0.1,0.395,40)
    for (x0,x1,y) in CABLE_TR: cbox(cut,(x0+x1)/2,y,-0.26,0.1,x1-x0,0.56)
    cbox(cut,HATCH[0],HATCH[1],-0.20,0.1,1.04,0.74)
    cm=bpy.data.meshes.new("rh_floor_cut"); cut.to_mesh(cm); cut.free(); co=bpy.data.objects.new("rh_floor_cut",cm); sc.collection.objects.link(co)
    bm=bmesh.new(); top=[bm.verts.new((x,y,TOP)) for x,y in r2lib.V]; bot=[bm.verts.new((x,y,TOP-SLAB_T)) for x,y in r2lib.V]
    bm.faces.new(top); bm.faces.new(bot[::-1])
    for i in range(8): j=(i+1)%8; bm.faces.new((bot[i],bot[j],top[j],top[i]))
    sm=bpy.data.meshes.new("rh_slab_tmp"); bm.to_mesh(sm); bm.free()
    so=bpy.data.objects.new("rh_slab_tmp",sm); sc.collection.objects.link(so)
    md=so.modifiers.new("cut",'BOOLEAN'); md.operation='DIFFERENCE'; md.solver='EXACT'; md.operand_type='OBJECT'; md.object=co; md.use_self=True
    dg=bpy.context.evaluated_depsgraph_get(); newme=bpy.data.meshes.new_from_object(so.evaluated_get(dg),depsgraph=dg)
    bpy.data.objects.remove(so); bpy.data.meshes.remove(sm); bpy.data.objects.remove(co); bpy.data.meshes.remove(cm)
    fl=bpy.data.objects['R2 floor']; oldme=fl.data; newme.name="R2 floor"; fl.data=newme; newme.materials.clear(); newme.materials.append(slabm)
    for p in newme.polygons: p.use_smooth=False
    if oldme.users==0: bpy.data.meshes.remove(oldme)
    # ---------------- trench ring: frames, bar grating panels, anchor bolts
    G="trench ring"; NP=30; rm=0.5*(RING[0]+RING[1]); rw=RING[1]-RING[0]
    for i in range(NP):
        a0=2*math.pi*i/NP+0.006; a1=2*math.pi*(i+1)/NP-0.006; am=(a0+a1)/2
        arcbar(kb(G+" frame","GALV"),RING[0]-0.01,RING[0]+0.04,a0,a1,-0.05,0.003,0.08); arcbar(kb(G+" frame","GALV"),RING[1]-0.04,RING[1]+0.01,a0,a1,-0.05,0.003,0.08)
        K.box((G+" frame","GALV"),rm*math.cos(a0),rm*math.sin(a0),-0.05,0.0,rw-0.05,0.014,a0,0.0)
        r0=RING[0]+0.052
        while r0+0.014<RING[1]-0.04: arcbar(kb(G+" grate","WET"),r0,r0+0.014,a0+0.012,a1-0.004,-0.04,0.002,0.12); r0+=0.046
        for fr in (0.25,0.75):
            a=a0+(a1-a0)*fr; K.box((G+" grate","WET"),rm*math.cos(a),rm*math.sin(a),-0.06,-0.032,rw-0.08,0.012,a,0.0)
        for rr_ in (RING[0]+0.015,RING[1]-0.015): K.cyl((G+" bolts","GALV"),rr_*math.cos(am),rr_*math.sin(am),0.0,0.008,0.009,8)
    # ---------------- straight trench runs to wall catch basins
    for (p0,p1,ang) in runs:
        d=p1-p0; Ln=d.length; u=d/Ln; nrm=Vector((-u.y,u.x)); G="trench run"; mid=(p0+p1)/2
        RECT_BLOCK.append((mid.x,mid.y,Ln/2,RUN_W/2+0.05,ang)); RECT_BLOCK.append((p1.x,p1.y,0.40,0.40,ang))
        for s_ in (-1,1):
            c=mid+nrm*s_*(RUN_W/2-0.012); K.box((G+" frame","GALV"),c.x,c.y,-0.05,0.003,Ln,0.044,ang,0.0)
        npn=max(1,int(Ln/0.9)); pl=Ln/npn
        for i in range(npn):
            q0=p0+u*(pl*i); qm=q0+u*(pl/2)
            for j in range(7):
                c=qm+nrm*(-RUN_W/2+0.05+j*(RUN_W-0.10)/6); K.box((G+" grate","WET"),c.x,c.y,-0.04,0.002,pl-0.025,0.014,ang,0.0)
            for fr in (0.2,0.8): c=q0+u*(pl*fr); K.box((G+" grate","WET"),c.x,c.y,-0.06,-0.032,0.012,RUN_W-0.06,ang,0.0)
            c=q0+u*0.006; K.box((G+" frame","GALV"),c.x,c.y,-0.05,0.0,0.012,RUN_W-0.04,ang,0.0)
            for s_ in (-1,1): c=qm+nrm*s_*(RUN_W/2-0.012); K.cyl((G+" bolts","GALV"),c.x,c.y,0.0,0.008,0.009,8)
        # catch basin: heavy square cast-iron frame with 8 bars across the opening, wet void below
        G="catch basin"; fr_=0.35
        for s_ in (-1,1):
            c=p1+nrm*s_*(fr_-0.04); K.box((G+" frame","IRON"),c.x,c.y,-0.04,0.004,0.70,0.08,ang,0.004); c=p1+u*s_*(fr_-0.04); K.box((G+" frame","IRON"),c.x,c.y,-0.04,0.004,0.08,0.54,ang,0.004)
        for j in range(8):
            c=p1+nrm*(-0.235+j*0.47/7); K.box((G+" grate","WET"),c.x,c.y,-0.05,0.002,0.54,0.026,ang+math.pi/2,0.0)
        K.box((G+" grate","WET"),p1.x,p1.y,-0.07,-0.045,0.02,0.54,ang,0.0)
        for sx_ in (-1,1):
            for sy_ in (-1,1): c=p1+u*sx_*(fr_-0.04)+nrm*sy_*(fr_-0.04); K.cyl((G+" bolts","GALV"),c.x,c.y,0.0,0.010,0.012,8)
    # ---------------- point drains: 3 square (bar grating) and 3 round (radial grating)
    G="point drain"
    for (x,y) in POINT_SQ:
        RECT_BLOCK.append((x,y,0.34,0.34,0.0))
        for s_ in (-1,1):
            K.box((G+" frame","IRON"),x+s_*0.30,y,-0.03,0.004,0.06,0.66,0.0,0.003); K.box((G+" frame","IRON"),x,y+s_*0.30,-0.03,0.004,0.54,0.06,0.0,0.003)
        for j in range(9): K.box((G+" grate","WET"),x,y-0.22+j*0.44/8,-0.05,0.002,0.54,0.013,0.0,0.0)
        for fr in (-0.12,0.12): K.box((G+" grate","WET"),x+fr,y,-0.07,-0.04,0.014,0.54,0.0,0.0)
        for sx_ in (-1,1):
            for sy_ in (-1,1): K.cyl((G+" bolts","GALV"),x+sx_*0.30,y+sy_*0.30,0.0,0.009,0.012,8)
    for (x,y) in POINT_RD:
        RECT_BLOCK.append((x,y,0.30,0.30,0.0))
        ringprism(kb(G+" frame","IRON"),0.20,0.28,-0.03,0.004,36,x,y)
        for r0,r1 in ((0.08,0.092),(0.145,0.157)): ringprism(kb(G+" grate","WET"),r0,r1,-0.05,0.002,28,x,y)
        K.cyl((G+" grate","WET"),x,y,-0.05,0.003,0.04,16)
        for k in range(12):
            a=2*math.pi*k/12+0.13; K.box((G+" grate","WET"),x+0.12*math.cos(a),y+0.12*math.sin(a),-0.05,0.002,0.16,0.012,a,0.0)
        for k in range(6): a=2*math.pi*k/6+0.3; K.cyl((G+" bolts","GALV"),x+0.24*math.cos(a),y+0.24*math.sin(a),0.0,0.009,0.011,8)
    # ---------------- manhole covers (cast iron: frame, raised ring ridges, radial ribs, studs, lifting slots)
    G="manhole"
    for (x,y) in MANHOLES:
        RECT_BLOCK.append((x,y,0.40,0.40,0.0))
        ringprism(kb(G+" frame","IRON"),0.30,0.385,-0.04,0.004,40,x,y)
        K.cyl((G+" cover","IRON"),x,y,-0.02,0.006,0.298,40)
        for r0,r1 in ((0.245,0.262),(0.155,0.170),(0.075,0.088)): ringprism(kb(G+" cover","IRON"),r0,r1,0.006,0.0105,36,x,y)
        K.cyl((G+" cover","IRON"),x,y,0.006,0.012,0.045,20)
        for k in range(8):
            a=2*math.pi*k/8; K.box((G+" cover","IRON"),x+0.165*math.cos(a),y+0.165*math.sin(a),0.006,0.0105,0.17,0.016,a,0.0)
        for k in range(16):
            a=2*math.pi*(k+0.5)/16; rr_=0.205 if k%2==0 else 0.115; K.cyl((G+" cover","IRON"),x+rr_*math.cos(a),y+rr_*math.sin(a),0.006,0.0095,0.011,8)
        for s_ in (-1,1): K.box((G+" slots","BLACK"),x+s_*0.205,y,0.0055,0.0068,0.012,0.075,0.0,0.0)
        for k in range(6): a=2*math.pi*k/6+0.5; K.cyl((G+" frame","GALV"),x+0.343*math.cos(a),y+0.343*math.sin(a),0.0,0.009,0.011,8)
    # ---------------- hatch (service pit, cast-iron cover with ribs, lifting recesses, hinge blocks, yellow keep-clear outline)
    G="hatch"; hx,hy=HATCH; RECT_BLOCK.append((hx,hy,0.52,0.37,0.0))
    for s_ in (-1,1):
        K.box((G+" frame","IRON"),hx+s_*0.485,hy,-0.03,0.004,0.07,0.74,0.0,0.003); K.box((G+" frame","IRON"),hx,hy+s_*0.335,-0.03,0.004,0.90,0.07,0.0,0.003)
    K.box((G+" cover","IRON"),hx,hy,-0.02,0.006,0.90,0.60,0.0,0.004)
    for j in range(6): K.box((G+" cover","IRON"),hx,hy-0.225+j*0.09,0.006,0.0105,0.80,0.016,0.0,0.0)
    for s_ in (-1,1): K.box((G+" slots","BLACK"),hx+s_*0.30,hy,0.0058,0.0068,0.012,0.12,0.0,0.0)
    for s_ in (-1,1): K.box((G+" frame","GALV"),hx+s_*0.28,hy+0.355,0.0,0.012,0.10,0.026,0.0,0.002)
    for sx_ in (-1,1):
        for sy_ in (-1,1): K.cyl((G+" frame","GALV"),hx+sx_*0.485,hy+sy_*0.335,0.0,0.009,0.012,8)
    # ---------------- cable trench: galvanised frames, chequer plates with lifting keys; one plate lifted away exposing cables
    G="cable trench"
    for ti,(x0,x1,y) in enumerate(CABLE_TR):
        Ln=x1-x0; RECT_BLOCK.append(((x0+x1)/2,y,Ln/2,0.30,0.0)); npn=max(1,int(Ln/0.95)); pl=Ln/npn
        for s_ in (-1,1): K.box((G+" frame","GALV"),(x0+x1)/2,y+s_*0.26,-0.04,0.003,Ln,0.044,0.0,0.0)
        K.box((G+" frame","GALV"),x0,y,-0.04,0.003,0.044,0.56,0.0,0.0); K.box((G+" frame","GALV"),x1,y,-0.04,0.003,0.044,0.56,0.0,0.0)
        for i in range(npn):
            q0=x0+pl*i; qm=q0+pl/2; K.box((G+" frame","GALV"),q0,y,-0.04,0.0,0.014,0.52,0.0,0.0)
            if i==1:
                for cj,(cy_,mk,rr_) in enumerate(((-0.14,"RUBBER",0.028),(0.0,"ORANGE",0.022),(0.13,"RUBBER",0.034))): K.cylx((G+" cables",mk),q0,q0+pl,y+cy_,-0.26+rr_,rr_,12)
                continue
            K.box((G+" plate","GALV"),qm,y,-0.012,0.004,pl-0.014,0.50,0.0,0.0015)
            for ci in range(8):
                for cj in range(3):
                    px=qm-(pl/2-0.14)+ci*(pl-0.28)/7; py=y-0.14+cj*0.14; ang=math.pi/4*(1 if (ci+cj)%2==0 else -1)
                    K.box((G+" plate","GALV"),px,py,0.004,0.0085,0.085,0.013,ang,0.0)
            for s_ in (-1,1): K.box((G+" keys","BLACK"),qm+s_*(pl/2-0.07),y+0.19,0.0035,0.0045,0.075,0.022,0.0,0.0)
    # ---------------- worn safety paint (yellow / white / black), laid only where no grate or cover is
    Z0,Z1=0.0,0.003
    def pbox(grp,mk,cx,cy,sx,sy,ang):
        if blocked(cx,cy,0.0): return
        K.box((grp,mk),cx,cy,Z0,Z1,sx,sy,ang,0.0)
    for k in range(0,360,2):                                                  # yellow ring round the trench
        a=math.radians(k+1)
        if not blocked(4.70*math.cos(a),4.70*math.sin(a),0.10): arcbar(kb("paint ring","Y"),4.62,4.78,math.radians(k)+0.002,math.radians(k+2)-0.002,Z0,Z1,0.2)
    for k in range(48):                                                       # outer hatch ticks
        a=2*math.pi*(k+0.5)/48
        if k%2==0 and not blocked(5.15*math.cos(a),5.15*math.sin(a),0.10): K.box(("paint ring ticks","Y"),5.15*math.cos(a),5.15*math.sin(a),Z0,Z1,0.42,0.09,a,0.0)
    for (x,y) in POINT_SQ+[(HATCH[0],HATCH[1])]:                              # keep-clear outlines round the drains and hatch
        hw=0.44 if (x,y)!=HATCH else 0.62; hh=0.44 if (x,y)!=HATCH else 0.47
        for s_ in (-1,1): pbox("paint outline","Y",x+s_*hw,y,0.07,2*hh+0.07,0.0); pbox("paint outline","Y",x,y+s_*hh,2*hw-0.07,0.07,0.0)
    for (x,y) in MANHOLES+POINT_RD:
        for k in range(24):
            a=2*math.pi*k/24; rr_=0.50 if (x,y) in MANHOLES else 0.42
            if k%3!=2: pbox("paint outline","Y",x+rr_*math.cos(a),y+rr_*math.sin(a),0.14,0.065,a+math.pi/2)
    W=r2lib.WALLS
    for wi,c,hw in ((6,6.0,3.0),(4,6.0,2.8),(1,3.395,2.8)):                    # door thresholds: hazard bars, then walkway edge lines and chevrons towards the pool
        w=W[wi]; n=int(2*hw/0.30)
        for i in range(n):
            u0=c-hw+i*(2*hw/n); u1=u0+2*hw/n
            P=[w.pt(u0,0.30),w.pt(u1,0.30),w.pt(u1+0.25,0.78),w.pt(u0+0.25,0.78)]
            poly(kb("paint threshold","Y" if i%2==0 else "K"),[(p.x,p.y) for p in P],Z0,Z1)
        tgt=Vector((0,0)); d=(tgt-w.pt(c,0.0)); dist=d.length-5.25; dn=Vector((w.n.x,w.n.y)); a=math.atan2(dn.y,dn.x)
        lw=1.20; nn=Vector((-dn.y,dn.x))
        t=1.1
        while t<dist:
            for s_ in (-1,1):
                p=w.pt(c,0.0)+dn*(t+0.25)+nn*s_*lw; pbox("paint lane","Y",p.x,p.y,0.5,0.10,a)
            t+=0.5
        t=1.9
        while t<dist-0.4:
            p=w.pt(c,0.0)+dn*t
            for s_ in (-1,1):
                q=p-dn*0.13+nn*s_*0.20; pbox("paint chevron","W",q.x,q.y,0.62,0.10,a+s_*math.radians(-38)*1)
            t+=1.25
    objs=K.build(COLL_NAME,"RH floor",mats)
    for o in objs:
        for bmn in (o.data,): bmn.update()
    return objs
# ----------------------------------------------------------------------------------------------------------------------------- main
n_removed=cleanup()
objs=build()
for m in list(bpy.data.materials):
    if m.name in ("R2 lane","R2 puddle") and m.users==0: bpy.data.materials.remove(m)
tris=sum(len(o.data.polygons) for o in objs)+len(bpy.data.objects['R2 floor'].data.polygons)
print("rh_floor: removed %d old floor objects; built %d RH floor objects, ~%d faces; R2 floor faces %d"%(n_removed,len(objs),tris,len(bpy.data.objects['R2 floor'].data.polygons)))
bpy.ops.wm.save_as_mainfile(filepath=A[1]); print("saved",A[1])
