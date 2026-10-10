"""Shared material library for the reactor-hall pass (rh_*.py).  One definition per material so every stage uses the SAME look and the hall stays on a handful of materials.
usage: import rh_mats; M=rh_mats.lib()   ->  dict key -> bpy Material (created once, reused by name)
Palette rules (owner brief): weathered concrete, dark Audi grey, safety colours (yellow / orange / red / white).  STRICTLY NO TEAL, cyan, aqua, turquoise, plum, navy or purple anywhere, in any
material, light or text.  The only green in the hall is the stability-driven pool/state glow (green -> orange -> red), which is lighting, not paint.
Procedural (Cycles) recipes; in an engine they are baked like the control room's (see cr_delivery.py).  Names start with 'RH '."""
import bpy,math
def _n(nt,t,x=0,y=0):
    n=nt.nodes.new(t); n.location=(x,y); return n
def surf(name,base,rough=0.6,metal=0.0,mottle=0.5,streak=0.0,edge=None,grime=0.0,scale=1.4,coat=0.0,bump=0.02,aniso=None,stain=0.0):
    """Principled surface with: low-frequency albedo mottling, fine grain, optional vertical rain-streak staining (streak 0..1), height grime (dark near the floor), painted-edge highlight."""
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    out=_n(nt,"ShaderNodeOutputMaterial",1800,0); b=_n(nt,"ShaderNodeBsdfPrincipled",1550,0); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough
    if coat>0: b.inputs['Coat Weight'].default_value=coat; b.inputs['Coat Roughness'].default_value=0.2
    geo=_n(nt,"ShaderNodeNewGeometry",0,-300); sep=_n(nt,"ShaderNodeSeparateXYZ",200,-300); nt.links.new(geo.outputs['Position'],sep.inputs['Vector'])
    vec=geo.outputs['Position']
    if aniso:
        mp=_n(nt,"ShaderNodeMapping",0,300); mp.inputs['Scale'].default_value=aniso; nt.links.new(vec,mp.inputs['Vector']); vec=mp.outputs['Vector']
    nz=_n(nt,"ShaderNodeTexNoise",250,300); nz.inputs['Scale'].default_value=scale; nz.inputs['Detail'].default_value=6.0; nz.inputs['Roughness'].default_value=0.62; nt.links.new(vec,nz.inputs['Vector'])
    mr=_n(nt,"ShaderNodeMapRange",450,300); mr.inputs['From Min'].default_value=0.3; mr.inputs['From Max'].default_value=0.72; mr.inputs['To Min'].default_value=1.0-0.6*mottle; mr.inputs['To Max'].default_value=1.0+0.25*mottle
    nt.links.new(nz.outputs['Fac'],mr.inputs['Value'])
    fz=_n(nt,"ShaderNodeTexNoise",250,0); fz.inputs['Scale'].default_value=90.0; fz.inputs['Detail'].default_value=3.0; nt.links.new(geo.outputs['Position'],fz.inputs['Vector'])
    fm=_n(nt,"ShaderNodeMapRange",450,0); fm.inputs['From Min'].default_value=0.3; fm.inputs['From Max'].default_value=0.7; fm.inputs['To Min'].default_value=0.93; fm.inputs['To Max'].default_value=1.07; nt.links.new(fz.outputs['Fac'],fm.inputs['Value'])
    g=_n(nt,"ShaderNodeMath",650,200); g.operation='MULTIPLY'; nt.links.new(mr.outputs['Result'],g.inputs[0]); nt.links.new(fm.outputs['Result'],g.inputs[1])
    col=_n(nt,"ShaderNodeVectorMath",850,200); col.operation='SCALE'; col.inputs[0].default_value=tuple(base[:3]); nt.links.new(g.outputs['Value'],col.inputs[3]); cur=col.outputs[0]
    if streak>0:                                                              # vertical rain streaks: noise stretched along z, darkening the albedo
        sm=_n(nt,"ShaderNodeMapping",250,-600); sm.inputs['Scale'].default_value=(6.0,6.0,0.35); nt.links.new(geo.outputs['Position'],sm.inputs['Vector'])
        sn=_n(nt,"ShaderNodeTexNoise",450,-600); sn.inputs['Scale'].default_value=1.0; sn.inputs['Detail'].default_value=4.0; nt.links.new(sm.outputs['Vector'],sn.inputs['Vector'])
        sr=_n(nt,"ShaderNodeMapRange",650,-600); sr.inputs['From Min'].default_value=0.45; sr.inputs['From Max'].default_value=0.75; sr.inputs['To Min'].default_value=0.0; sr.inputs['To Max'].default_value=streak; nt.links.new(sn.outputs['Fac'],sr.inputs['Value'])
        sx=_n(nt,"ShaderNodeMix",1050,200); sx.data_type='RGBA'; sx.inputs[7].default_value=(base[0]*0.35,base[1]*0.33,base[2]*0.30,1.0); nt.links.new(cur,sx.inputs[6]); nt.links.new(sr.outputs['Result'],sx.inputs[0]); cur=sx.outputs[2]
    if grime>0:                                                               # dirt gathers low on the wall
        gz=_n(nt,"ShaderNodeMapRange",450,-300); gz.inputs['From Min'].default_value=0.0; gz.inputs['From Max'].default_value=4.0; gz.inputs['To Min'].default_value=1.0; gz.inputs['To Max'].default_value=0.0; nt.links.new(sep.outputs['Z'],gz.inputs['Value'])
        gm=_n(nt,"ShaderNodeMath",650,-300); gm.operation='MULTIPLY'; gm.inputs[1].default_value=grime; nt.links.new(gz.outputs['Result'],gm.inputs[0])
        gx=_n(nt,"ShaderNodeMix",1250,200); gx.data_type='RGBA'; gx.inputs[7].default_value=(base[0]*0.22,base[1]*0.21,base[2]*0.2,1.0); nt.links.new(cur,gx.inputs[6]); nt.links.new(gm.outputs['Value'],gx.inputs[0]); cur=gx.outputs[2]
    if edge:
        bv=_n(nt,"ShaderNodeBevel",1000,-300); bv.inputs['Radius'].default_value=0.012; bv.samples=4
        dt=_n(nt,"ShaderNodeVectorMath",1200,-300); dt.operation='DOT_PRODUCT'; nt.links.new(bv.outputs['Normal'],dt.inputs[0]); nt.links.new(geo.outputs['Normal'],dt.inputs[1])
        em=_n(nt,"ShaderNodeMapRange",1380,-300); em.inputs['From Min'].default_value=0.9985; em.inputs['From Max'].default_value=0.94; nt.links.new(dt.outputs['Value'],em.inputs['Value'])
        ex=_n(nt,"ShaderNodeMix",1420,200); ex.data_type='RGBA'; ex.inputs[7].default_value=(*edge[:3],1.0); nt.links.new(cur,ex.inputs[6]); nt.links.new(em.outputs['Result'],ex.inputs[0]); cur=ex.outputs[2]
    nt.links.new(cur,b.inputs['Base Color'])
    rz=_n(nt,"ShaderNodeTexNoise",250,-900); rz.inputs['Scale'].default_value=3.5; rz.inputs['Detail'].default_value=3.0; nt.links.new(geo.outputs['Position'],rz.inputs['Vector'])
    rr=_n(nt,"ShaderNodeMapRange",450,-900); rr.inputs['From Min'].default_value=0.3; rr.inputs['From Max'].default_value=0.7; rr.inputs['To Min'].default_value=max(0.04,rough*0.82); rr.inputs['To Max'].default_value=min(1.0,rough*1.18); nt.links.new(rz.outputs['Fac'],rr.inputs['Value']); nt.links.new(rr.outputs['Result'],b.inputs['Roughness'])
    if bump>0:
        bz=_n(nt,"ShaderNodeTexNoise",250,-1100); bz.inputs['Scale'].default_value=150.0 if metal<0.5 else 60.0; bz.inputs['Detail'].default_value=4.0; nt.links.new(geo.outputs['Position'],bz.inputs['Vector'])
        bp=_n(nt,"ShaderNodeBump",1300,-900); bp.inputs['Strength'].default_value=bump*10; bp.inputs['Distance'].default_value=0.02; nt.links.new(bz.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
    return m
def emit(name,rgb,strength=3.0):
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    out=_n(nt,"ShaderNodeOutputMaterial",600,0); b=_n(nt,"ShaderNodeBsdfPrincipled",300,0); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    b.inputs['Base Color'].default_value=(*[c*0.1 for c in rgb[:3]],1); b.inputs['Emission Color'].default_value=(*rgb[:3],1); b.inputs['Emission Strength'].default_value=strength
    return m
def hazard(name="RH hazard stripes",a=(0.60,0.40,0.015),b_=(0.012,0.012,0.012),period=0.22):
    """diagonal yellow / black warning stripes, procedural in world space (x+y+z)"""
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    out=_n(nt,"ShaderNodeOutputMaterial",900,0); b=_n(nt,"ShaderNodeBsdfPrincipled",650,0); nt.links.new(b.outputs['BSDF'],out.inputs['Surface']); b.inputs['Roughness'].default_value=0.55
    geo=_n(nt,"ShaderNodeNewGeometry",0,0); sep=_n(nt,"ShaderNodeSeparateXYZ",150,0); nt.links.new(geo.outputs['Position'],sep.inputs['Vector'])
    s1=_n(nt,"ShaderNodeMath",300,100); s1.operation='ADD'; nt.links.new(sep.outputs['X'],s1.inputs[0]); nt.links.new(sep.outputs['Y'],s1.inputs[1])
    s2=_n(nt,"ShaderNodeMath",450,100); s2.operation='ADD'; nt.links.new(s1.outputs['Value'],s2.inputs[0]); nt.links.new(sep.outputs['Z'],s2.inputs[1])
    pm=_n(nt,"ShaderNodeMath",600,100); pm.operation='PINGPONG'; pm.inputs[1].default_value=period; nt.links.new(s2.outputs['Value'],pm.inputs[0])
    st=_n(nt,"ShaderNodeMath",750,100); st.operation='GREATER_THAN'; st.inputs[1].default_value=period*0.5; nt.links.new(pm.outputs['Value'],st.inputs[0])
    mx=_n(nt,"ShaderNodeMix",900,200); mx.data_type='RGBA'; mx.inputs[6].default_value=(*a,1); mx.inputs[7].default_value=(*b_,1); nt.links.new(st.outputs['Value'],mx.inputs[0]); nt.links.new(mx.outputs[2],b.inputs['Base Color'])
    return m
_LIB={}
def lib():
    """the shared hall palette; weathered concrete, dark Audi grey, structural steel, cast iron, safety colours, rubber, brass"""
    L={}
    L["CONC"]=surf("RH weathered concrete",(0.165,0.162,0.152),0.86,0.0,mottle=0.8,streak=0.55,grime=0.55,scale=1.1,bump=0.05)
    L["CONC_DARK"]=surf("RH concrete plinth",(0.095,0.093,0.088),0.82,0.0,mottle=0.7,streak=0.3,grime=0.7,scale=1.6,bump=0.05)
    L["CONC_POUR"]=surf("RH concrete cast panel",(0.205,0.200,0.190),0.80,0.0,mottle=0.6,streak=0.45,grime=0.35,scale=0.8,bump=0.04)
    L["AUDI"]=surf("RH dark audi grey",(0.029,0.029,0.030),0.38,0.65,mottle=0.35,streak=0.12,edge=(0.23,0.23,0.23),grime=0.25,scale=2.0,bump=0.0)
    L["AUDI_SATIN"]=surf("RH audi grey satin",(0.055,0.055,0.056),0.52,0.5,mottle=0.45,streak=0.18,edge=(0.27,0.27,0.27),grime=0.3,scale=2.0,bump=0.01)
    L["STEEL"]=surf("RH structural steel",(0.043,0.043,0.044),0.5,0.8,mottle=0.4,streak=0.2,edge=(0.31,0.31,0.31),grime=0.35,scale=2.2,bump=0.0)
    L["GALV"]=surf("RH galvanised steel",(0.31,0.31,0.30),0.36,0.9,mottle=0.5,streak=0.1,edge=(0.56,0.56,0.55),grime=0.2,scale=3.0,bump=0.0)
    L["IRON"]=surf("RH cast iron",(0.022,0.021,0.021),0.58,0.55,mottle=0.4,streak=0.15,edge=(0.16,0.15,0.14),grime=0.4,scale=2.5,bump=0.01)
    L["YELLOW"]=surf("RH safety yellow",(0.58,0.40,0.012),0.5,0.0,mottle=0.3,streak=0.15,edge=(0.85,0.62,0.10),grime=0.35,scale=2.0,bump=0.01)
    L["ORANGE"]=surf("RH safety orange",(0.50,0.13,0.010),0.5,0.0,mottle=0.3,streak=0.15,edge=(0.80,0.30,0.05),grime=0.35,scale=2.0,bump=0.01)
    L["RED"]=surf("RH safety red",(0.30,0.020,0.014),0.45,0.0,mottle=0.25,streak=0.1,edge=(0.55,0.08,0.05),grime=0.3,scale=2.0,bump=0.01)
    L["WHITE"]=surf("RH signal white",(0.48,0.48,0.44),0.5,0.0,mottle=0.3,streak=0.1,grime=0.3,scale=2.0,bump=0.01)
    L["BLACK"]=surf("RH black polymer",(0.013,0.013,0.014),0.55,0.0,mottle=0.2,edge=(0.08,0.08,0.08),scale=3.0,bump=0.02)
    L["RUBBER"]=surf("RH rubber",(0.018,0.018,0.018),0.88,0.0,mottle=0.2,scale=3.0,bump=0.08)
    L["BRASS"]=surf("RH brass",(0.44,0.30,0.095),0.3,0.95,mottle=0.4,scale=3.0,bump=0.0)
    L["HAZARD"]=hazard()
    return L
