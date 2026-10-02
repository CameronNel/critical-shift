"""Control-room lightmaps: the Low-quality tier's lighting (design/QUALITY_TIERS.md).
usage: python cr_lightmaps.py -- <in.blend> <out_dir> <ship.blend> <emulate.blend> [--size 2048] [--samples 64]
Dev practice (Unity docs: lighting that is never computed at runtime is the cheapest): bake the static lighting once with Cycles and ship textures.
Four lightmaps share ONE second UV layer ('Lightmap', smart-project + uniform-density pack), so a Low-tier material is  albedo x sum_k(scale_k * mod_k * lightmap_k):
  static  - the 12 baked lights, world ambient and all steady emissive surfaces            (modulator 1, steady)
  troffer - the three troffers + their tubes at the reference energy 32 W / strength 5      (modulator = troffer expression / 32: flicker, brownout, stability)
  tv      - the TV light (white, reference 80 W) + TV screen glow                          (modulator = TV colour x energy / 80: follows the picture)
  beacon  - the two red beacons at reference 40 W                                           (modulator = beacon energy / 40: pulse)
The modulators are tiny per-frame scalars computed on the CPU from the seconds-based runtime spec: the whole room flickers at zero GPU cost, no real-time light, no shadow map.
Writes <out_dir>/control_room_lm_<name>.png (Non-Color / sRGB unchecked on import; value = (lightmap / scale)^(1/2.2), decode with pow 2.2 x scale) and control_room_lightmaps.json (scales, modulator reference values, texel density);
<ship.blend> = the input plus the 'Lightmap' UV layer (render UV unchanged); <emulate.blend> = scratch scene where every surface shows albedo x lightmaps (what the Low tier should look like)."""
import bpy,sys,os,math,json,time
import numpy as np
A=sys.argv[sys.argv.index("--")+1:]; SRC,OUT,SHIP,EMU=A[0],A[1],A[2],A[3]
SIG=float(A[A.index("--sigma")+1]) if "--sigma" in A else 1.6
SIZE=int(A[A.index("--size")+1]) if "--size" in A else 2048; SAMPLES=int(A[A.index("--samples")+1]) if "--samples" in A else 64
os.makedirs(OUT,exist_ok=True); T0=time.time()
bpy.ops.wm.open_mainfile(filepath=SRC); sc=bpy.context.scene; sc.frame_set(1)
C=bpy.data.collections["31 CR CONTROL ROOM REDO"]; SH=bpy.data.collections["26 R2 CONTROL ROOM"]
SKIP=("COL ","CR haze","CR static decals")
objs=[o for o in list(C.all_objects)+list(SH.objects) if o.type=='MESH' and not o.name.startswith(SKIP) and len(o.data.polygons)>0 and not any(m and "glass" in m.name.lower() for m in o.data.materials)]
objs=list({o.name:o for o in objs}.values()); print("lightmapped objects",len(objs))
# ------------------------------------------------------------ 1. second UV layer
for o in bpy.context.view_layer.objects: o.select_set(False)
for o in objs:
    me=o.data
    if "Lightmap" in me.uv_layers: me.uv_layers.remove(me.uv_layers["Lightmap"])
    me.uv_layers.new(name="Lightmap"); me.uv_layers.active=me.uv_layers["Lightmap"]; o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(89),island_margin=0.0007,area_weight=0.0,correct_aspect=True,scale_to_bounds=False)
bpy.ops.uv.average_islands_scale(); bpy.ops.uv.pack_islands(margin=0.0007,rotate=True)
bpy.ops.object.mode_set(mode='OBJECT')
# texel density and utilisation (uv area vs 3D area)
a3=a2=0.0
for o in objs:
    me=o.data; uv=me.uv_layers["Lightmap"].data
    for p in me.polygons:
        a3+=p.area; li=p.loop_indices; pts=[uv[i].uv for i in li]
        a2+=abs(sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts))))/2
texels_per_m=math.sqrt(a2/a3)*SIZE if a3>0 else 0
print("surface %.0f m2, uv area %.2f of the atlas, %.1f texels/m at %d px"%(a3,a2,texels_per_m,SIZE))
for o in objs:
    me=o.data; me.uv_layers.active=me.uv_layers[0]
    for l in me.uv_layers: l.active_render=(l.name==me.uv_layers[0].name)
bpy.ops.wm.save_as_mainfile(filepath=SHIP,copy=True)       # ship file: Lightmap UV layer added, everything else unchanged
for o in objs: o.data.uv_layers.active=o.data.uv_layers["Lightmap"]
# ------------------------------------------------------------ 2. bake passes
LIGHTS={o.name:o for o in bpy.data.objects if o.type=='LIGHT' and o.name.startswith("CR ")}
def lname(o): return o.name
TROF=[n for n in LIGHTS if n.startswith("CR troffer")]; TVL=["CR tv light"]; BEA=[n for n in LIGHTS if n.startswith("CR beacon")]
REFS={"troffer":32.0,"tv":80.0,"beacon":40.0}
set_energy={}
for n in TROF: set_energy[n]=REFS["troffer"]
for n in TVL: set_energy[n]=REFS["tv"]
for n in BEA: set_energy[n]=REFS["beacon"]
# evaluated frame-1 values (modulators)
ev={n:LIGHTS[n].data.energy for n in LIGHTS}; tvcol=list(LIGHTS["CR tv light"].data.color)
mods={"troffer":float(np.mean([ev[n] for n in TROF])/REFS["troffer"]),"tv":[tvcol[i]*ev["CR tv light"]/REFS["tv"] for i in range(3)],"beacon":float(np.mean([ev[n] for n in BEA])/REFS["beacon"])}
for n in LIGHTS:                                              # drivers would re-evaluate during baking: freeze every light at its pass value
    ld=LIGHTS[n].data
    if ld.animation_data:
        for fc in list(ld.animation_data.drivers): ld.driver_remove(fc.data_path)
for n,e in set_energy.items(): LIGHTS[n].data.energy=e
TV_WHITE=(1.0,1.0,1.0)
bpy.data.lights["CR tv light"].color=TV_WHITE
for n in BEA: LIGHTS[n].data.color=(1.0,0.10,0.04)
# emissive materials: group by role; freeze (remove drivers) at frame-1 values
EM={}
for m in bpy.data.materials:
    if not m.use_nodes: continue
    b=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if b is None: continue
    if m.node_tree.animation_data:
        for fc in list(m.node_tree.animation_data.drivers): pass
    s=b.inputs['Emission Strength'].default_value
    if s>0.01 and (m.name.startswith("CR ") ): EM[m.name]=(b,s)
def role(name):
    if "tungsten tube" in name: return "troffer"
    if "emergency beacon" in name: return "beacon"
    if name=="CR tv screen": return "tv"
    return "static"
for m in list(EM):
    mt=bpy.data.materials[m]
    if mt.node_tree.animation_data:
        for fc in list(mt.node_tree.animation_data.drivers): mt.node_tree.animation_data.drivers.remove(fc)
EMV={k:b.inputs['Emission Strength'].default_value for k,(b,s) in EM.items()}
ref_em={"troffer":5.0}
world_nt=sc.world.node_tree if sc.world else None; world_bg=[n for n in world_nt.nodes if n.type=='BACKGROUND'] if world_nt else []; world_s=[n.inputs[1].default_value for n in world_bg]
def set_pass(name):
    for n,l in LIGHTS.items():
        on=(name=="static" and n not in set_energy) or (name=="troffer" and n in TROF) or (name=="tv" and n in TVL) or (name=="beacon" and n in BEA)
        l.hide_render=not on
    for k,(b,s) in EM.items():
        r=role(k); b.inputs['Emission Strength'].default_value=(ref_em.get(r,EMV[k]) if r==name else 0.0)
        if r=="static" and name=="static": b.inputs['Emission Strength'].default_value=EMV[k]
    for n,v in zip(world_bg,world_s): n.inputs[1].default_value=(v if name=="static" else 0.0)
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=SAMPLES; sc.cycles.use_denoising=False; sc.cycles.use_adaptive_sampling=False
sc.cycles.sample_clamp_indirect=8.0; sc.cycles.sample_clamp_direct=0.0
sc.cycles.max_bounces=6; sc.cycles.diffuse_bounces=4; sc.cycles.film_exposure=1.0
sc.view_settings.view_transform='Standard'
# image node in every material of the lightmapped objects (target of the bake)
mats=[]
for o in objs:
    for s in o.material_slots:
        if s.material and s.material not in mats: mats.append(s.material)
def bake_one(name,size):
    im=bpy.data.images.new("LM "+name,size,size,alpha=False,float_buffer=True); im.colorspace_settings.name='Non-Color'
    for m in mats:
        nt=m.node_tree; tn=nt.nodes.get("_LM") or nt.nodes.new("ShaderNodeTexImage"); tn.name="_LM"; tn.image=im; nt.nodes.active=tn
        for n in nt.nodes: n.select=(n==tn)
    for o in bpy.context.view_layer.objects: o.select_set(False)
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    set_pass(name)
    if os.environ.get('CR_LM_REUSE') and os.path.exists(os.path.join(OUT,'_raw_%s.npy'%name)): return im
    bpy.ops.object.bake(type='DIFFUSE',pass_filter={'DIRECT','INDIRECT'},margin=3,margin_type='EXTEND',use_clear=True)
    return im
lm={}; scales={}; sizes={}
for name in ("static","troffer","tv","beacon"):
    t=time.time(); sz=SIZE if name=="static" else SIZE//2; sc.cycles.samples=SAMPLES if name=="static" else max(16,SAMPLES//2); im=bake_one(name,sz)
    rp=os.path.join(OUT,'_raw_%s.npy'%name)
    if os.environ.get('CR_LM_REUSE') and os.path.exists(rp): px=np.load(rp)
    else:
        px=np.array(im.pixels[:],dtype=np.float32).reshape(sz,sz,4)[...,:3]; np.save(rp,px)
    print("raw bake %s: mean %.4f max %.3f nonzero %.1f%%"%(name,px.mean(),px.max(),100*(px.sum(2)>0).mean()))
    if os.environ.get("CR_LM_ONLY"): sys.exit(0)
    # noise filter: firefly clamp, then coverage-aware (normalised) gaussian blur, so islands do not bleed into empty texels
    px=np.nan_to_num(px); cov=(px.sum(2)>0).astype(np.float32)
    lum=px.max(2); cap=float(np.percentile(lum[cov>0],99.7))*1.5 if (cov>0).any() else 1.0; px=np.minimum(px,cap)
    def blur(a,sig):
        r=int(3*sig); k=np.exp(-0.5*(np.arange(-r,r+1)/sig)**2); k/=k.sum(); o=a
        for ax in (0,1): o=sum(w*np.roll(o,i-r,ax) for i,w in enumerate(k))
        return o
    num=blur(px*cov[...,None],SIG); den=blur(cov,SIG)[...,None]; px=np.where(cov[...,None]>0,num/np.maximum(den,1e-6),0.0).astype(np.float32)
    scale=float(max(np.percentile(px.max(2),99.9),1e-4)); enc=np.clip(px/scale,0,1)**(1/2.2)
    out=bpy.data.images.new("LMO "+name,sz,sz,alpha=False); out.colorspace_settings.name='Non-Color'
    out.pixels.foreach_set(np.dstack([enc,np.ones((sz,sz),np.float32)]).astype(np.float32).reshape(-1)); out.filepath_raw=os.path.join(OUT,"control_room_lm_%s.png"%name); out.file_format='PNG'; out.save()
    lm[name]=out; scales[name]=scale; sizes[name]=sz; print("baked %-8s scale %.3f in %.0f s"%(name,scale,time.time()-t))
meta={"uv_layer":"Lightmap","size_px":sizes,"samples":SAMPLES,"texels_per_metre":round(texels_per_m,1),"surface_m2":round(a3,1),"objects":len(objs),
      "decode":"linear_irradiance = scale * pixel_srgb_decoded_gamma22(pixel)   (pixel stored as (v/scale)^(1/2.2))","scales":scales,
      "reference_energy_W_cycles":REFS,"reference_tube_emission":5.0,"modulators_at_frame1_stability1":mods,
      "runtime_formula":"light = albedo * (scale_s*lm_static + scale_t*mod_troffer(t,s)*lm_troffer + scale_v*mod_tv_rgb(t,s)*lm_tv + scale_b*mod_beacon(t,s)*lm_beacon); modulators from control_room_runtime_behaviour.json",
      "status":{"engine_implementation":"Blocked (no Unity target)","measured_performance":"NotRun"}}
json.dump(meta,open(os.path.join(OUT,"control_room_lightmaps.json"),"w"),indent=1)
# ------------------------------------------------------------ 3. emulate the Low tier: every surface = albedo x lightmaps (no lights)
for l in LIGHTS.values(): l.hide_render=True
for n,v in zip(world_bg,world_s): n.inputs[1].default_value=0.0
for k,(b,s) in EM.items(): b.inputs['Emission Strength'].default_value=EMV[k]       # screens, LEDs, tubes stay self-lit as in the scene
mod_rgb={"static":(1,1,1),"troffer":(mods["troffer"],)*3,"tv":tuple(mods["tv"]),"beacon":(mods["beacon"],)*3}
for m in mats:
    nt=m.node_tree; b=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if b is None or EM.get(m.name): continue
    nt.nodes.remove(nt.nodes["_LM"]) if "_LM" in nt.nodes else None
    bc=b.inputs['Base Color']; src=bc.links[0].from_socket if bc.is_linked else None; val=tuple(bc.default_value)
    uvn=nt.nodes.new("ShaderNodeUVMap"); uvn.uv_map="Lightmap"; acc=None
    for name in ("static","troffer","tv","beacon"):
        tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=lm[name]; tx.interpolation='Linear'; tx.extension='EXTEND'; nt.links.new(uvn.outputs['UV'],tx.inputs[0])
        g=nt.nodes.new("ShaderNodeGamma"); g.inputs['Gamma'].default_value=2.2; nt.links.new(tx.outputs['Color'],g.inputs['Color'])
        sc_=nt.nodes.new("ShaderNodeVectorMath"); sc_.operation='MULTIPLY'; sc_.inputs[1].default_value=tuple(scales[name]*c for c in mod_rgb[name]); nt.links.new(g.outputs['Color'],sc_.inputs[0])
        if acc is None: acc=sc_.outputs[0]
        else:
            ad=nt.nodes.new("ShaderNodeVectorMath"); ad.operation='ADD'; nt.links.new(acc,ad.inputs[0]); nt.links.new(sc_.outputs[0],ad.inputs[1]); acc=ad.outputs[0]
    mx=nt.nodes.new("ShaderNodeVectorMath"); mx.operation='MULTIPLY'; nt.links.new(acc,mx.inputs[0])
    if src is not None: nt.links.new(src,mx.inputs[1])
    else: mx.inputs[1].default_value=val[:3]
    for l in list(bc.links): nt.links.remove(l)
    bc.default_value=(0,0,0,1); b.inputs['Metallic'].default_value=0.0
    for nm in ('Specular IOR Level',):
        if nm in b.inputs: b.inputs[nm].default_value=0.0
    nt.links.new(mx.outputs[0],b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value=1.0
for m in bpy.data.materials:                                  # surfaces without a lightmap (decal atlas): the engine lights them as ambient, here a flat 0.25
    if m in mats or not m.use_nodes or m.name in EM: continue
    b=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if b is None or b.inputs['Alpha'].default_value<0.5 and not b.inputs['Alpha'].is_linked or "glass" in m.name.lower() or m.name=="CR haze": continue
    if m.name.startswith("CR decals"):
        bc=b.inputs['Base Color']
        if bc.is_linked: m.node_tree.links.new(bc.links[0].from_socket,b.inputs['Emission Color'])
        b.inputs['Emission Strength'].default_value=0.25
bpy.ops.wm.save_as_mainfile(filepath=EMU,copy=True)
print("done in %.0f s"%(time.time()-T0))
