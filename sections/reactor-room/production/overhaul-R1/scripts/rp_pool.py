"""Reactor pool interior pass: clearer water so the pool reads as water and the fuel lattice shows, moving caustics on the pool floor, painted depth markers on the lining, a ring of
underwater lamps.   usage: python rp_pool.py -- <in.blend> <out.blend>      (run after rp_rods.py; touches only the pool water volume material, the pool collection and new RP objects)
 * pool_medium (the volume object 'Deep water medium'): absorption cut from 0.075 to 0.028 and shifted to a clear teal-green, scatter cut to 0.006: the old values made 6 m of opaque green.
 * 'RP caustics': a disc on the pool floor, transparent except for a bright net (two layered 4D Voronoi edge patterns), drifting with scene time in SECONDS (driver on the Voronoi W input).
 * depth markers 1 M / 3 M / 5 M below the surface (surface z -0.47) painted on the lining at the four compass points; eight lamps (emissive bosses) on the lining at z -2.4.
Everything is static geometry or a seconds-based driver; nothing here needs the runtime."""
import bpy,sys,os,math,bmesh
from mathutils import Vector
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import crk
A=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A[0],A[1]
bpy.ops.wm.open_mainfile(filepath=SRC)
crk.STATE=bpy.data.objects.get("REACTOR_STATE")
POOLC=bpy.data.collections["03 POOL AND RAIL"]
# ---- clearer water
nt=bpy.data.materials["pool_medium"].node_tree
for nd in nt.nodes:
    if nd.type=='VOLUME_ABSORPTION': nd.inputs['Density'].default_value=0.028; nd.inputs['Color'].default_value=(0.45,0.95,0.72,1.0)
    if nd.type=='VOLUME_SCATTER': nd.inputs['Density'].default_value=0.006; nd.inputs['Color'].default_value=(0.35,0.95,0.78,1.0)
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
M=dict(WHITE=crk.pm("RP depth paint",(0.70,0.70,0.62),0.5,scale=2.0,bump=0.0),LAMP=crk.emit_mat("RP pool lamp",(0.55,1.0,0.85),5.0),GUN=crk.pm("RP lamp housing",(0.05,0.06,0.06),0.35,metal=0.8,scale=2.0,bump=0.0))
R=3.36
for (face,x,y) in (('-x',R,0.0),('+x',-R,0.0),('-y',0.0,R),('+y',0.0,-R)):
    for zz,body in ((-1.47,"1 M"),(-3.47,"3 M"),(-5.47,"5 M")):
        crk.text(POOLC,body,x,y,zz,face,0.22,M["WHITE"],'CENTER',"RP pool depth marker")
K=crk.Kit()
for k in range(8):
    th=k*math.pi/4+math.pi/8; cx,cy=3.34*math.cos(th),3.34*math.sin(th)
    K.prism(("rp","GUN"),(cx,cy,-2.4),(cx*0.985,cy*0.985,-2.4),0.16,0.16,16,0.0,True,0.0)        # housing boss (axis inward is approximate: a flat disc)
    K.prism(("rp","LAMP"),(cx*0.985,cy*0.985,-2.4),(cx*0.975,cy*0.975,-2.4),0.115,0.115,16,0.0,True,0.0)
K.build(POOLC,"RP pool lamps",M)
print("rp_pool: done")
bpy.ops.wm.save_as_mainfile(filepath=DST)
