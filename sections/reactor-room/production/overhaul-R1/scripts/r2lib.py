"""Reactor room v2 architecture kit: chamfered panel builder + procedural stylised materials."""
import bpy,bmesh,math
from mathutils import Vector,Matrix
V=[(-6,-10.8),(6,-10.8),(10.8,-6),(10.8,6),(6,10.8),(-6,10.8),(-10.8,6),(-10.8,-6)]
class Wall:
    def __init__(s,i):
        s.i=i; s.P=Vector(V[i]); s.Q=Vector(V[(i+1)%8]); d=s.Q-s.P; s.L=d.length; s.t=d/s.L; s.n=Vector((-s.t.y,s.t.x))
        s.angle=math.atan2(s.t.y,s.t.x)
    def pt(s,u,v): p=s.P+s.t*u+s.n*v; return p          # u along wall, v into the hall
WALLS=[Wall(i) for i in range(8)]
# ---------- geometry accumulator: one bmesh per (group, material) -> one object each
class Acc:
    def __init__(s): s.bm={}
    def get(s,key):
        if key not in s.bm: s.bm[key]=bmesh.new()
        return s.bm[key]
    def box(s,key,cx,cy,z0,z1,sx,sy,ang,ch=0.02):
        """box centred at (cx,cy), size sx (along local x) x sy (local y), rotated by ang about z, from z0 to z1, chamfered."""
        bm=s.get(key); r=bmesh.ops.create_cube(bm,size=1.0); verts=r['verts']
        c,sn=math.cos(ang),math.sin(ang)
        for v in verts:
            lx=v.co.x*sx; ly=v.co.y*sy; v.co=Vector((cx+lx*c-ly*sn,cy+lx*sn+ly*c,z0+(v.co.z+.5)*(z1-z0)))
        if ch>0:
            edges=list({e for v in verts for e in v.link_edges})
            bmesh.ops.bevel(bm,geom=edges,offset=min(ch,0.4*min(sx,sy,z1-z0)),segments=1,affect='EDGES')
    def wbox(s,key,w,u0,u1,h0,h1,d0,d1,ch=0.02,gap=0.008):
        """box in wall frame: u along wall, d (v) into hall from the wall plane."""
        u0+=gap;u1-=gap;h0+=gap;h1-=gap
        if u1<=u0 or h1<=h0 or d1<=d0: return
        p=w.pt((u0+u1)/2,(d0+d1)/2); s.box(key,p.x,p.y,h0,h1,u1-u0,d1-d0,w.angle,ch)
    def build(s,collection,prefix,mats):
        coll=bpy.data.collections.get(collection) or bpy.data.collections.new(collection)
        if coll.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(coll)
        out=[]
        for (grp,mname),bm in s.bm.items():
            me=bpy.data.meshes.new(f"{prefix} {grp} {mname}"); bm.to_mesh(me); bm.free()
            o=bpy.data.objects.new(f"{prefix} {grp} {mname}",me); coll.objects.link(o); me.materials.append(mats[mname]); out.append(o)
        s.bm={}; return out
# ---------- stylised procedural material
def N(nt,t,x,y): n=nt.nodes.new(t); n.location=(x,y); return n
BR=2.3
def r2mat(name,base,rough=0.55,edge=None,grime=0.5,noise=(2.2,0.10),tile=None,metal=0.0,mottle=0.5):
    base=tuple(min(1.0,c*BR) for c in base)
    if tile: tile=(tile[0],tuple(min(1.0,c*BR) for c in tile[1]))
    m=bpy.data.materials.get(name)
    if m: bpy.data.materials.remove(m)
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out=N(nt,"ShaderNodeOutputMaterial",1900,0); b=N(nt,"ShaderNodeBsdfPrincipled",1650,0); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    geo=N(nt,"ShaderNodeNewGeometry",0,-400); sep=N(nt,"ShaderNodeSeparateXYZ",200,-400); nt.links.new(geo.outputs['Position'],sep.inputs['Vector'])
    # hand-painted mottling: low-frequency noise value 1-mottle*..1
    nz=N(nt,"ShaderNodeTexNoise",200,150); nz.inputs['Scale'].default_value=noise[0]; nz.inputs['Detail'].default_value=5; nz.inputs['Roughness'].default_value=0.65
    nz2=N(nt,"ShaderNodeTexNoise",200,-100); nz2.inputs['Scale'].default_value=noise[0]*7; nz2.inputs['Detail'].default_value=2
    nt.links.new(geo.outputs['Position'],nz.inputs['Vector']); nt.links.new(geo.outputs['Position'],nz2.inputs['Vector'])
    mr=N(nt,"ShaderNodeMapRange",450,150); mr.inputs['From Min'].default_value=0.3; mr.inputs['From Max'].default_value=0.7; mr.inputs['To Min'].default_value=1.0-mottle*0.55; mr.inputs['To Max'].default_value=1.0+mottle*0.25
    nt.links.new(nz.outputs['Fac'],mr.inputs['Value'])
    bc=N(nt,"ShaderNodeMix",700,150); bc.data_type='RGBA'; bc.blend_type='MULTIPLY'; bc.inputs[0].default_value=1.0
    col=base
    if tile:
        bt=N(nt,"ShaderNodeTexBrick",200,500); bt.inputs['Scale'].default_value=1.0/tile[0]; bt.inputs['Mortar Size'].default_value=0.012; bt.inputs['Bias'].default_value=0; bt.inputs['Brick Width'].default_value=1.0; bt.inputs['Row Height'].default_value=1.0
        bt.offset=0.0; bt.inputs['Color1'].default_value=(*base,1); bt.inputs['Color2'].default_value=(*tile[1],1); bt.inputs['Mortar'].default_value=(*[c*0.25 for c in base],1)
        nt.links.new(geo.outputs['Position'],bt.inputs['Vector']); nt.links.new(bt.outputs['Color'],bc.inputs[6])
    else: bc.inputs[6].default_value=(*base,1)
    # brick mapping is on XY; add mapping to keep tiles square
    nt.links.new(mr.outputs['Result'],bc.inputs[7]) if False else None
    mv=N(nt,"ShaderNodeMix",700,0); mv.data_type='RGBA'; mv.blend_type='MULTIPLY'; mv.inputs[0].default_value=1.0
    # convert scalar to colour for multiply
    cc=N(nt,"ShaderNodeCombineColor",560,150); nt.links.new(mr.outputs['Result'],cc.inputs[0]); nt.links.new(mr.outputs['Result'],cc.inputs[1]); nt.links.new(mr.outputs['Result'],cc.inputs[2])
    nt.links.new(cc.outputs['Color'],bc.inputs[7]); cur=bc.outputs[2]
    if edge:
        bev=N(nt,"ShaderNodeBevel",700,-500); bev.inputs['Radius'].default_value=0.025; bev.samples=4
        dot=N(nt,"ShaderNodeVectorMath",900,-500); dot.operation='DOT_PRODUCT'; nt.links.new(bev.outputs['Normal'],dot.inputs[0]); nt.links.new(geo.outputs['Normal'],dot.inputs[1])
        em=N(nt,"ShaderNodeMapRange",1100,-500); em.inputs['From Min'].default_value=0.998; em.inputs['From Max'].default_value=0.93
        nt.links.new(dot.outputs['Value'],em.inputs['Value'])
        e1=N(nt,"ShaderNodeMix",1300,0); e1.data_type='RGBA'; e1.inputs[7].default_value=(*edge,1); nt.links.new(cur,e1.inputs[6]); nt.links.new(em.outputs['Result'],e1.inputs[0]); cur=e1.outputs[2]
    if grime>0:
        gz=N(nt,"ShaderNodeMapRange",900,-800); gz.inputs['From Min'].default_value=0.0; gz.inputs['From Max'].default_value=5.0; gz.inputs['To Min'].default_value=1.0; gz.inputs['To Max'].default_value=0.0
        nt.links.new(sep.outputs['Z'],gz.inputs['Value'])
        gn=N(nt,"ShaderNodeMath",1100,-800); gn.operation='MULTIPLY'; nt.links.new(gz.outputs['Result'],gn.inputs[0]); nt.links.new(nz2.outputs['Fac'],gn.inputs[1])
        gs=N(nt,"ShaderNodeMath",1250,-800); gs.operation='MULTIPLY'; gs.inputs[1].default_value=grime*2.2; nt.links.new(gn.outputs['Value'],gs.inputs[0])
        g1=N(nt,"ShaderNodeMix",1450,0); g1.data_type='RGBA'; g1.inputs[7].default_value=(0.008,0.006,0.010,1); nt.links.new(cur,g1.inputs[6]); nt.links.new(gs.outputs['Value'],g1.inputs[0]); cur=g1.outputs[2]
    nt.links.new(cur,b.inputs['Base Color'])
    return m
