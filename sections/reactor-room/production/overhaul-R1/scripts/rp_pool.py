"""Reactor pool interior pass: clearer water so the pool reads as water and the fuel lattice shows, moving caustics on the pool floor, painted depth markers on the lining, a ring of
underwater lamps.   usage: python rp_pool.py -- <in.blend> <out.blend>      (run after rp_rods.py; touches only the pool water volume material, the pool collection and new RP objects)
 * pool_medium (the volume object 'Deep water medium'): absorption cut from 0.075 to 0.028 and shifted to a clear teal-green, scatter cut to 0.006: the old values made 6 m of opaque green.
 * 'RP caustics': a disc on the pool floor, transparent except for a bright net (two layered 4D Voronoi edge patterns), drifting with scene time in SECONDS (driver on the Voronoi W input).
 * depth markers 1 M / 3 M / 5 M below the surface (surface z -0.47) painted on the lining at the four compass points; eight lamps (emissive bosses) on the lining at z -2.4.
Glow fix (owner: "blown out green"): with AgX a 3.4 / 2.2 emission strength clips to white, so the strengths in the driver expressions of pool_glow (3.4 -> 1.0) and R2 state glow (2.2 -> 0.45) are lowered
(instability still raises them by up to 60 %), the water absorption is made near-neutral so red and orange glow is not eaten by a green absorber, the in-scatter and the caustics follow the stability
colour (green -> orange -> red), and the pool lamps use the state-glow material.  Check all three states: stability 1.0 (green), 0.5 (orange), 0.1 (red).
Everything is static geometry or a seconds-based driver (the original hall glow drivers still use frames); nothing here needs the runtime."""
import bpy,sys,os,math,bmesh
from mathutils import Vector
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import crk
A=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A[0],A[1]
bpy.ops.wm.open_mainfile(filepath=SRC)
crk.STATE=bpy.data.objects.get("REACTOR_STATE")
POOLC=bpy.data.collections["03 POOL AND RAIL"]
# ---- water surface: the single-plane glass (transmission 1) read as a milky cream veil over the whole pool; replace it with a thin sheet, mostly transparent with a Fresnel sheen and the old ripple bump
wm=bpy.data.materials["water"]; wnt=wm.node_tree
bump=next(n for n in wnt.nodes if n.type=='BUMP'); outn=next(n for n in wnt.nodes if n.type=='OUTPUT_MATERIAL')
for n in [n for n in wnt.nodes if n.type=='BSDF_PRINCIPLED']: wnt.nodes.remove(n)
gl=wnt.nodes.new("ShaderNodeBsdfGlossy"); gl.inputs['Roughness'].default_value=0.04; gl.inputs['Color'].default_value=(0.30,0.45,0.40,1.0)
trn=wnt.nodes.new("ShaderNodeBsdfTransparent"); lw=wnt.nodes.new("ShaderNodeLayerWeight"); lw.inputs['Blend'].default_value=0.35
fm=wnt.nodes.new("ShaderNodeMath"); fm.operation='MULTIPLY'; fm.inputs[1].default_value=0.08; fm.use_clamp=True
mx=wnt.nodes.new("ShaderNodeMixShader")
wnt.links.new(bump.outputs['Normal'],gl.inputs['Normal']); wnt.links.new(bump.outputs['Normal'],lw.inputs['Normal'])
wnt.links.new(lw.outputs['Fresnel'],fm.inputs[0]); wnt.links.new(fm.outputs[0],mx.inputs[0]); wnt.links.new(trn.outputs[0],mx.inputs[1]); wnt.links.new(gl.outputs[0],mx.inputs[2]); wnt.links.new(mx.outputs[0],outn.inputs['Surface'])
# the pool's two big area lights are visible in the surface reflection (that was the milky disc): keep them as illumination only
for ln in ("Pool surface scattered cyan","Cyan from deep pool"):
    lo=bpy.data.objects.get(ln)
    if lo: lo.visible_camera=False; lo.visible_glossy=False
# ---- clearer water
nt=bpy.data.materials["pool_medium"].node_tree
for nd in nt.nodes:
    if nd.type=='VOLUME_ABSORPTION': nd.inputs['Density'].default_value=0.022; nd.inputs['Color'].default_value=(0.80,0.92,0.86,1.0)
    if nd.type=='VOLUME_SCATTER':
        nd.inputs['Density'].default_value=0.006; nd.name="PoolScatter"
        for i,ex in enumerate(("0.35+0.65*min(1,2*(1-s)+0.24)","0.35+0.65*(0.03+0.92*s)","0.35+0.65*(0.20*s)")): crk.drv(nt,'nodes["PoolScatter"].inputs["Color"].default_value',i,ex,var_s=True)
# glow strengths: lower the base so AgX does not clip to white
for mn,old,new in (("pool_glow","3.4*","1.0*"),("R2 state glow","2.2*","0.45*")):
    mt=bpy.data.materials[mn]
    for d in mt.node_tree.animation_data.drivers:
        if "Emission Strength" in d.data_path and old in d.driver.expression: d.driver.expression=d.driver.expression.replace(old,new,1)
    for nd in mt.node_tree.nodes:
        if nd.type=='BSDF_PRINCIPLED': nd.inputs['Emission Strength'].default_value*=new and (float(new[:-1])/float(old[:-1]))
# state-glow base colour: the driven base colour (the full state colour) was lit by the pool's 2.5 kW of area lights and turned the rings and walls it sits on near-white.  Keep the glow in the EMISSION and give the base colour 2 %.
for mn in ("pool_glow","R2 state glow"):
    mt=bpy.data.materials[mn]
    for d in mt.node_tree.animation_data.drivers:
        if 'Base Color' in d.data_path and not d.driver.expression.startswith("0.02*("): d.driver.expression="0.02*("+d.driver.expression+")"
    for nd in mt.node_tree.nodes:
        if nd.type=='BSDF_PRINCIPLED': bc=nd.inputs['Base Color'].default_value; nd.inputs['Base Color'].default_value=(bc[0]*0.02,bc[1]*0.02,bc[2]*0.02,1.0)
# ---- caustics: transparent disc with a drifting bright net
m=bpy.data.materials.get("RP caustics")
if m: bpy.data.materials.remove(m)
m=bpy.data.materials.new("RP caustics"); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); m.blend_method='HASHED'
def N(t,x=0,y=0,name=None):
    n=nt.nodes.new(t); n.location=(x,y)
    if name: n.name=name
    return n
out=N("ShaderNodeOutputMaterial",1200,0); mix=N("ShaderNodeMixShader",1000,0); tr=N("ShaderNodeBsdfTransparent",800,150); em=N("ShaderNodeEmission",800,-100)
em.inputs['Color'].default_value=(0.55,1.0,0.85,1.0); em.inputs["Strength"].default_value=0.9
nt.links.new(tr.outputs[0],mix.inputs[1]); nt.links.new(em.outputs[0],mix.inputs[2]); nt.links.new(mix.outputs[0],out.inputs[0])
tc=N("ShaderNodeTexCoord",-900,0); layers=[]
for i,(sc,spd,nm) in enumerate(((0.8,0.30,"CausticV1"),(1.5,-0.42,"CausticV2"))):
    mp=N("ShaderNodeMapping",-700,200-i*300); mp.inputs['Scale'].default_value=(sc,sc,sc); nt.links.new(tc.outputs['Object'],mp.inputs['Vector'])
    vo=N("ShaderNodeTexVoronoi",-450,200-i*300,nm); vo.voronoi_dimensions='4D'; vo.feature='DISTANCE_TO_EDGE'; nt.links.new(mp.outputs[0],vo.inputs['Vector'])
    cr=N("ShaderNodeMapRange",-200,200-i*300); cr.inputs['From Min'].default_value=0.0; cr.inputs['From Max'].default_value=0.16; cr.inputs['To Min'].default_value=1.0; cr.inputs['To Max'].default_value=0.0; cr.clamp=True
    nt.links.new(vo.outputs['Distance'],cr.inputs['Value']); layers.append(cr)
    crk.drv(nt,'nodes["%s"].inputs["W"].default_value'%nm,None,"T*%.2f"%spd,var_s=False)
ad=N("ShaderNodeMath",300,0); ad.operation='ADD'; nt.links.new(layers[0].outputs[0],ad.inputs[0]); nt.links.new(layers[1].outputs[0],ad.inputs[1])
sc2=N("ShaderNodeMath",550,0); sc2.operation='MULTIPLY'; sc2.inputs[1].default_value=0.5; sc2.use_clamp=True; nt.links.new(ad.outputs[0],sc2.inputs[0]); nt.links.new(sc2.outputs[0],mix.inputs[0])
bm=bmesh.new(); r=3.25; zc=-6.43; seg=48
vs=[bm.verts.new((r*math.cos(2*math.pi*k/seg),r*math.sin(2*math.pi*k/seg),zc)) for k in range(seg)]; bm.faces.new(vs)
me=bpy.data.meshes.new("RP caustics"); bm.to_mesh(me); bm.free()
co=bpy.data.objects.new("RP caustics",me); POOLC.objects.link(co); me.materials.append(m)
# ---- depth markers + lamps on the lining
M=dict(WHITE=crk.pm("RP depth paint",(0.70,0.70,0.62),0.5,scale=2.0,bump=0.0),LAMP=bpy.data.materials["R2 state glow"],GUN=crk.pm("RP lamp housing",(0.05,0.06,0.06),0.35,metal=0.8,scale=2.0,bump=0.0))
import crt,numpy as np
R=3.365                                                                           # depth markers: white text printed on curved strips that follow the lining (decal, alpha), so they bend with the wall instead of floating flat in front of it
for body,zz in (("1 M",-1.47),("3 M",-3.47),("5 M",-5.47)):
    msk=crt.text_mask(body,256,96,78); rgba=np.zeros((96,256,4),np.float32); rgba[...,:3]=(0.80,0.80,0.72); rgba[...,3]=msk
    mt=crk.decal_mat("RP depth paint "+body,crk.new_image("RP depth tex "+body,rgba),0.6); bm=bmesh.new(); n=10; hw=0.34/R; hh=0.26
    for th0 in (0.0,math.pi/2,math.pi,3*math.pi/2):
        rows=[[bm.verts.new((R*math.cos(th0+hw*(1-2*i/n)),R*math.sin(th0+hw*(1-2*i/n)),zz-hh/2+j*hh)) for i in range(n+1)] for j in (0,1)]
        uvl=bm.loops.layers.uv.verify()
        for i in range(n):
            f=bm.faces.new((rows[0][i],rows[0][i+1],rows[1][i+1],rows[1][i])); f.smooth=False
            for lo,uv in zip(f.loops,((i/n,0),((i+1)/n,0),((i+1)/n,1),(i/n,1))): lo[uvl].uv=uv
    me=bpy.data.meshes.new("RP depth "+body); bm.to_mesh(me); bm.free(); ob=bpy.data.objects.new("RP pool depth marker "+body,me); POOLC.objects.link(ob); me.materials.append(mt)
K=crk.Kit()
for k in range(8):
    th=k*math.pi/4+math.pi/8; cx,cy=3.34*math.cos(th),3.34*math.sin(th)
    K.prism(("rp","GUN"),(cx,cy,-2.4),(cx*0.985,cy*0.985,-2.4),0.16,0.16,16,0.0,True,0.0)        # housing boss (axis inward is approximate: a flat disc)
    K.prism(("rp","LAMP"),(cx*0.985,cy*0.985,-2.4),(cx*0.975,cy*0.975,-2.4),0.115,0.115,16,0.0,True,0.0)
K.build(POOLC,"RP pool lamps",M)
print("rp_pool: done")
bpy.ops.wm.save_as_mainfile(filepath=DST)
