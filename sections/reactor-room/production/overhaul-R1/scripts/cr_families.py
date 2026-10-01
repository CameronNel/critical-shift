"""Shared material families for the control room (design/MATERIAL_BUDGETS.md, approved budgets).
usage: python cr_families.py -- <in.blend> <out.blend>   (run after cr_build, cr_optimize and cr_atlas_decals)
Every procedural spawn-recipe material ('pm' materials carry their recipe as pm_* custom props) is replaced by ONE of seven family materials.
The per-surface values of the old recipe travel on the mesh instead of in a material:
    colour attribute 'Col'  = RGB base colour (linear), A = roughness
    colour attribute 'Mat'  = R metallic, G bump strength, B albedo-variation strength, A painted-edge highlight (0/1)
The family shader reads those two attributes (same recipe: low-frequency albedo variation, fine grain, roughness noise, fine bump, bevel-edge
highlight), so one material draws what used to be many.  Objects of the same group and family are then joined.
Emissive, image (decals, screens, keyboard), glass and haze materials are NOT touched here (next step of the budget).
In an engine the two attributes collapse to the glTF vertex colour (tint + roughness) plus a baked family tile; the Cycles bevel highlight is not exported."""
import bpy,sys,os,re,collections
import numpy as np
A=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A[0],A[1]
bpy.ops.wm.open_mainfile(filepath=SRC)
C=bpy.data.collections["31 CR CONTROL ROOM REDO"]
FAM=[  # (family, noise scale for the low-frequency variation, regexes of the old materials)
 ("S01 painted metal",2.5,r"hazard|signal red|locker|lamp shade|fridge|aircon|trim charcoal|desk edge|mug|terracotta"),
 ("S02 bare metal",3.0,r"galvanised|graphite|brass|ceiling grid"),
 ("S03 plaster and tile",2.0,r"wall |ceiling tile"),
 ("S05 plastic and rubber",2.5,r"black plastic|grey plastic|platinum|keycap|rubber|jug|pill"),
 ("S06 fabric",3.0,r"fabric|canvas|blanket|pillow"),
 ("S07 wood paper organic",4.0,r"laminate|cardboard|paper|cork|dead leaf|dry soil|plant leaf|coffee|book cover"),
 ("S09 cable",3.0,r"cable"),
]
def family_of(name):
    for fam,sc,rx in FAM:
        if re.search(rx,name.lower().replace("cr ","",1)): return fam
    return None
def _n(nt,t,x=0,y=0):
    n=nt.nodes.new(t); n.location=(x,y); return n
def build_family(name,scale):
    old=bpy.data.materials.get(name)
    if old: bpy.data.materials.remove(old)
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    out=_n(nt,"ShaderNodeOutputMaterial",2000,0); b=_n(nt,"ShaderNodeBsdfPrincipled",1700,0); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    col=_n(nt,"ShaderNodeAttribute",0,300); col.attribute_type='GEOMETRY'; col.attribute_name="Col"
    mat=_n(nt,"ShaderNodeAttribute",0,-100); mat.attribute_type='GEOMETRY'; mat.attribute_name="Mat"
    sepm=_n(nt,"ShaderNodeSeparateColor",250,-100); nt.links.new(mat.outputs['Color'],sepm.inputs[0])
    geo=_n(nt,"ShaderNodeNewGeometry",0,-450)
    nz=_n(nt,"ShaderNodeTexNoise",250,500); nz.inputs['Scale'].default_value=scale; nz.inputs['Detail'].default_value=2.0; nz.inputs['Roughness'].default_value=0.55
    nt.links.new(geo.outputs['Position'],nz.inputs['Vector'])
    mr=_n(nt,"ShaderNodeMapRange",450,500); mr.inputs['From Min'].default_value=0.32; mr.inputs['From Max'].default_value=0.68; mr.inputs['To Min'].default_value=0.87; mr.inputs['To Max'].default_value=1.05
    nt.links.new(nz.outputs['Fac'],mr.inputs['Value'])
    dv=_n(nt,"ShaderNodeMath",650,500); dv.operation='SUBTRACT'; dv.inputs[1].default_value=1.0; nt.links.new(mr.outputs['Result'],dv.inputs[0])
    sv=_n(nt,"ShaderNodeMath",800,500); sv.operation='MULTIPLY_ADD'; sv.inputs[2].default_value=1.0; nt.links.new(dv.outputs['Value'],sv.inputs[0]); nt.links.new(sepm.outputs[2],sv.inputs[1])   # 1 + (v-1)*var
    fz=_n(nt,"ShaderNodeTexNoise",250,150); fz.inputs['Scale'].default_value=70.0; fz.inputs['Detail'].default_value=3.0; nt.links.new(geo.outputs['Position'],fz.inputs['Vector'])
    fm=_n(nt,"ShaderNodeMapRange",450,150); fm.inputs['From Min'].default_value=0.3; fm.inputs['From Max'].default_value=0.7; fm.inputs['To Min'].default_value=0.96; fm.inputs['To Max'].default_value=1.04
    nt.links.new(fz.outputs['Fac'],fm.inputs['Value'])
    g=_n(nt,"ShaderNodeMath",950,300); g.operation='MULTIPLY'; nt.links.new(sv.outputs['Value'],g.inputs[0]); nt.links.new(fm.outputs['Result'],g.inputs[1])
    vs=_n(nt,"ShaderNodeVectorMath",1100,300); vs.operation='SCALE'; nt.links.new(col.outputs['Color'],vs.inputs[0]); nt.links.new(g.outputs['Value'],vs.inputs[3])
    bev=_n(nt,"ShaderNodeBevel",900,-450); bev.inputs['Radius'].default_value=0.004; bev.samples=4
    dt=_n(nt,"ShaderNodeVectorMath",1100,-450); dt.operation='DOT_PRODUCT'; nt.links.new(bev.outputs['Normal'],dt.inputs[0]); nt.links.new(geo.outputs['Normal'],dt.inputs[1])
    em=_n(nt,"ShaderNodeMapRange",1300,-450); em.inputs['From Min'].default_value=0.9985; em.inputs['From Max'].default_value=0.94; nt.links.new(dt.outputs['Value'],em.inputs['Value'])
    ef=_n(nt,"ShaderNodeMath",1450,-450); ef.operation='MULTIPLY'; nt.links.new(em.outputs['Result'],ef.inputs[0]); nt.links.new(mat.outputs['Alpha'],ef.inputs[1])
    hi=_n(nt,"ShaderNodeVectorMath",1300,150); hi.operation='SCALE'; hi.inputs[3].default_value=1.35; nt.links.new(vs.outputs[0],hi.inputs[0])
    mx=_n(nt,"ShaderNodeMix",1500,150); mx.data_type='RGBA'; nt.links.new(ef.outputs['Value'],mx.inputs[0]); nt.links.new(vs.outputs[0],mx.inputs[6]); nt.links.new(hi.outputs[0],mx.inputs[7])
    nt.links.new(mx.outputs[2],b.inputs['Base Color']); nt.links.new(sepm.outputs[0],b.inputs['Metallic'])
    rz=_n(nt,"ShaderNodeTexNoise",250,-800); rz.inputs['Scale'].default_value=4.0; rz.inputs['Detail'].default_value=2.0; nt.links.new(geo.outputs['Position'],rz.inputs['Vector'])
    rr=_n(nt,"ShaderNodeMapRange",450,-800); rr.inputs['From Min'].default_value=0.3; rr.inputs['From Max'].default_value=0.7; rr.inputs['To Min'].default_value=0.9; rr.inputs['To Max'].default_value=1.1
    nt.links.new(rz.outputs['Fac'],rr.inputs['Value'])
    rm=_n(nt,"ShaderNodeMath",700,-800); rm.operation='MULTIPLY'; rm.use_clamp=True; nt.links.new(col.outputs['Alpha'],rm.inputs[0]); nt.links.new(rr.outputs['Result'],rm.inputs[1])
    nt.links.new(rm.outputs['Value'],b.inputs['Roughness'])
    bz=_n(nt,"ShaderNodeTexNoise",250,-1000); bz.inputs['Scale'].default_value=140.0; bz.inputs['Detail'].default_value=3.0; nt.links.new(geo.outputs['Position'],bz.inputs['Vector'])
    bp=_n(nt,"ShaderNodeBump",1500,-800); bp.inputs['Distance'].default_value=0.02; nt.links.new(sepm.outputs[1],bp.inputs['Strength']); nt.links.new(bz.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
    return m
fams={}; stats=collections.Counter(); skipped=collections.Counter()
for fam,sc,_ in FAM: fams[fam]=build_family("CR FAM "+fam,sc)
objs=[o for o in C.all_objects if o.type=='MESH']
for o in objs:
    me=o.data; mt=list(me.materials)
    tgt=[None]*len(mt)
    for i,m in enumerate(mt):
        if m is not None and m.get("pm_base") is not None:
            f=family_of(m.name)
            if f: tgt[i]=f
            else: skipped[m.name]+=1
    if not any(tgt): continue
    L=len(me.loops); col=np.tile(np.array([0.5,0.5,0.5,0.5],dtype=np.float32),(L,1)); mat=np.tile(np.array([0,0.06,1,0],dtype=np.float32),(L,1))
    for p in me.polygons:
        i=p.material_index
        if i<len(mt) and tgt[i]:
            m=mt[i]; b=m["pm_base"]; li=list(p.loop_indices)
            col[li]=(b[0],b[1],b[2],m["pm_rough"]); mat[li]=(m["pm_metal"],m["pm_bump"],m["pm_var"],1.0 if len(m["pm_edge"]) else 0.0)
            stats[m.name]+=len(li)
    for nm,arr in (("Col",col),("Mat",mat)):
        ca=me.color_attributes.get(nm) or me.color_attributes.new(nm,'FLOAT_COLOR','CORNER'); ca.data.foreach_set("color",arr.reshape(-1))
    # slots: one per family, untouched materials keep theirs
    new=[fams[t] if t else m for t,m in zip(tgt,mt)]; uniq=[]
    for m in new:
        if m not in uniq: uniq.append(m)
    idx=[uniq.index(m) for m in new]
    for p in me.polygons: p.material_index=idx[p.material_index] if p.material_index<len(idx) else 0
    me.materials.clear()
    for m in uniq: me.materials.append(m)
# join objects of the same (group, family) that carry exactly one material
def group(o): mm=re.match(r"CR (\w+)",o.name); return mm.group(1) if mm else ""
SKIP=("tv","text","beacon","haze","COL","glassnote","grime","marks")
by=collections.defaultdict(list)
for o in [o for o in C.all_objects if o.type=='MESH' and not o.name.startswith(("COL ","CR haze"))]:
    if len(o.data.materials)==1 and o.data.materials[0] in fams.values() and group(o) not in SKIP and not o.animation_data and o.data.uv_layers:
        o.data.uv_layers[0].name="UVMap"; by[(group(o),o.data.materials[0].name)].append(o)
for (g,mn),lst in by.items():
    if len(lst)<2: continue
    for o in bpy.context.view_layer.objects: o.select_set(False)
    for o in lst: o.select_set(True)
    bpy.context.view_layer.objects.active=lst[0]; bpy.ops.object.join(); lst[0].name="CR %s %s"%(g,mn[7:].split(" ")[0])
for m in [m for m in bpy.data.materials if m.get("pm_base") is not None and m.users==0]: bpy.data.materials.remove(m)
used={x.name for o in C.all_objects if o.type=='MESH' for x in o.data.materials if x}
print("families built",len(fams),"; old recipe materials replaced:",len(stats),"; left alone (no family rule):",dict(skipped))
print("control-room materials in use now:",len(used),"; mesh objects:",sum(1 for o in C.all_objects if o.type=='MESH' and not o.name.startswith(("COL ","CR haze"))))
bpy.ops.wm.save_as_mainfile(filepath=DST)
