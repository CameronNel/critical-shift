"""Control-room delivery derivative and Blender round trip (game-asset-pipeline / blender-uv-texturing checks).
usage: python cr_delivery.py -- <in.blend> <out_dir> [--no-render]
Scope: collection '31 CR CONTROL ROOM REDO' meshes (not the haze volume, not collision proxies) plus the room floor and back-wall slabs.
 1. the canonical blend is never saved: everything happens on copies in this process
 2. procedural materials cannot survive glTF/FBX, so each is baked once to a 256 px albedo tile (single-location bake on a 1.2 m horizontal plane; NOT seamless),
    emissive materials are frozen at frame 1, image materials that already use the UV map are kept, the floor tile keeps its seamless image (UV x 1/1.2)
 3. export GLB (copies only, no lights/cameras), re-import into an empty scene, compare object count, bounds, triangles, materials, UV coverage, render a neutrally lit check view
 4. writes control_room_delivery_report.json; engine import / Player behaviour is reported as Blocked (no asset-specific validator or working Unity target)"""
import bpy,sys,os,json,math,time
import numpy as np
from mathutils import Vector
A=sys.argv[sys.argv.index("--")+1:]; SRC,OUT=A[0],A[1]; RENDER="--no-render" not in A
os.makedirs(OUT,exist_ok=True); T0=time.time()
bpy.ops.wm.open_mainfile(filepath=SRC); sc=bpy.context.scene; sc.frame_set(1)
coll=bpy.data.collections["31 CR CONTROL ROOM REDO"]
src=[o for o in coll.objects if o.type=="MESH" and not o.name.startswith("CR haze")]
for n in ("R2 control cr floor FLOOR","R2 control cr back wall BACK"):
    if n in bpy.data.objects: src.append(bpy.data.objects[n])
print("scope objects",len(src))
def tris(o):
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); me=e.to_mesh(); me.calc_loop_triangles(); n=len(me.loop_triangles); e.to_mesh_clear(); return n
def bounds(objs):
    mn=np.array([1e9]*3); mx=np.array([-1e9]*3)
    dg=bpy.context.evaluated_depsgraph_get()
    for o in objs:
        e=o.evaluated_get(dg); me=e.to_mesh(); M=np.array(o.matrix_world)
        if len(me.vertices):
            a=np.empty(len(me.vertices)*3,dtype=np.float32); me.vertices.foreach_get("co",a); w=a.reshape(-1,3)@M[:3,:3].T+M[:3,3]; mn=np.minimum(mn,w.min(0)); mx=np.maximum(mx,w.max(0))
        e.to_mesh_clear()
    return mn,mx
src_tris=sum(tris(o) for o in src); src_min,src_max=bounds(src)
# ---------------------------------------------------------------- 2. materials
def principled(m): return next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m and m.node_tree else None
def uv_image(m):
    for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image and n.inputs[0].is_linked:
            f=n.inputs[0].links[0].from_node
            while f.type=='MAPPING' and f.inputs[0].is_linked: f=f.inputs[0].links[0].from_node            # a tiling Mapping node in between is fine
            if f.type in('UVMAP',) or (f.type=='TEX_COORD'): return n.image
    return None
def emission_strength(m):
    b=principled(m); return (b.inputs['Emission Strength'].default_value if b else 0.0)
mats=[]
for o in src:
    for s in o.material_slots:
        if s.material and s.material not in mats: mats.append(s.material)
plan={}
for m in mats:
    b=principled(m)
    if b is None: plan[m.name]="keep"; continue
    if m.name.startswith("CR FAM "): plan[m.name]="family"
    elif m.name=="CR floor tile": plan[m.name]="floor"
    elif emission_strength(m)>0.05 and not b.inputs['Emission Color'].is_linked: plan[m.name]="emit"
    elif emission_strength(m)>0.05: plan[m.name]="emit_img"
    elif uv_image(m) is not None: plan[m.name]="keep"
    elif b.inputs['Alpha'].default_value<0.99 or b.inputs['Alpha'].is_linked: plan[m.name]="keep"
    else: plan[m.name]="bake"
print({k:sum(1 for v in plan.values() if v==k) for k in set(plan.values())})
# bake tiles
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=6; sc.cycles.use_denoising=False
tiles={}; bake_t=time.time()
if any(v=="bake" for v in plan.values()):
    me=bpy.data.meshes.new("_bk"); me.from_pydata([(-0.6,-0.6,0),(0.6,-0.6,0),(0.6,0.6,0),(-0.6,0.6,0)],[],[(0,1,2,3)]); uv=me.uv_layers.new(name="UVMap")
    for lo,u in zip(me.loops,((0,0),(1,0),(1,1),(0,1))): uv.data[lo.index].uv=u
    po=bpy.data.objects.new("_bk",me); sc.collection.objects.link(po); po.location=(-2.0,-9.0,6.5)
    for name,kind in plan.items():
        if kind!="bake": continue
        m0=bpy.data.materials[name]; mc=m0.copy(); mc.name="_bk_"+name; nt=mc.node_tree
        im=bpy.data.images.new("tile_"+name,256,256,alpha=False); im.colorspace_settings.name='sRGB'
        tn=nt.nodes.new("ShaderNodeTexImage"); tn.image=im; nt.nodes.active=tn
        for n in nt.nodes: n.select=(n==tn)
        me.materials.clear(); me.materials.append(mc)
        bpy.ops.object.select_all(action='DESELECT'); po.select_set(True); bpy.context.view_layer.objects.active=po
        bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'},margin=4,use_clear=True)
        im.pack(); tiles[name]=im; bpy.data.materials.remove(mc)
    bpy.data.objects.remove(po); bpy.data.meshes.remove(me)
print("baked",len(tiles),"tiles in %.0f s"%(time.time()-bake_t))
# families (cr_families.py): colour+roughness live on the mesh ('Col' RGB base, A roughness; 'Mat' R metallic) -> glTF COLOR_0 x one shared neutral grain tile
fam_stats={}
for o in src:
    me=o.data
    if "Col" not in me.color_attributes: continue
    L=len(me.loops); ca=np.empty(L*4,dtype=np.float32); me.color_attributes["Col"].data.foreach_get("color",ca); ca=ca.reshape(-1,4)
    ma=np.empty(L*4,dtype=np.float32); me.color_attributes["Mat"].data.foreach_get("color",ma); ma=ma.reshape(-1,4)
    for p in me.polygons:
        sm=o.material_slots[p.material_index].material if p.material_index<len(o.material_slots) else None
        if sm is not None and plan.get(sm.name)=="family":
            li=list(p.loop_indices); r,mt_,n=fam_stats.get(sm.name,(0.0,0.0,0)); fam_stats[sm.name]=(r+float(ca[li,3].sum()),mt_+float(ma[li,0].sum()),n+len(li))
rng=np.random.default_rng(7); g=rng.random((64,64)).astype(np.float32); g=np.fft.irfft2(np.fft.rfft2(g)*np.exp(-((np.fft.fftfreq(64)[:,None]**2)+(np.fft.rfftfreq(64)[None,:]**2))*900),s=g.shape); g=(g-g.mean())/(g.std()+1e-6)
g=np.repeat(np.repeat(np.clip(0.96+0.03*g,0.88,1.06),4,0),4,1)                     # 256 px neutral +-4% mottling, tileable enough at 1.2 m
grain=bpy.data.images.new("CR family grain",256,256,alpha=False); grain.colorspace_settings.name='Non-Color'; grain.pixels.foreach_set(np.dstack([g,g,g,np.ones_like(g)]).astype(np.float32).reshape(-1)); grain.pack()
def rough_of(m):
    b=principled(m)
    if b is None: return 0.6
    if b.inputs['Roughness'].is_linked:
        f=b.inputs['Roughness'].links[0].from_node
        if f.type=='MAP_RANGE': return 0.5*(f.inputs['To Min'].default_value+f.inputs['To Max'].default_value)
        if f.type=='MATH': return f.inputs[2].default_value+0.5*f.inputs[1].default_value
    return b.inputs['Roughness'].default_value
def mk(name,base=None,tile=None,rough=0.6,metal=0.0,emit=None,emit_str=0.0,uvscale=(1,1,1),img=None):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled"); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    image=tile or img
    if image is not None:
        uvn=nt.nodes.new("ShaderNodeUVMap"); uvn.uv_map="UVMap"; tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=image; tx.extension='REPEAT'
        if uvscale!=(1,1,1):
            mp=nt.nodes.new("ShaderNodeMapping"); mp.inputs['Scale'].default_value=uvscale; nt.links.new(uvn.outputs['UV'],mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'],tx.inputs[0])
        else: nt.links.new(uvn.outputs['UV'],tx.inputs[0])
        nt.links.new(tx.outputs['Color'],b.inputs['Base Color'])
    elif base is not None: b.inputs['Base Color'].default_value=(*base[:3],1)
    if emit is not None:
        b.inputs['Emission Color'].default_value=(*emit[:3],1); b.inputs['Emission Strength'].default_value=emit_str
    return m
def mk_family(name,rough,metal):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled"); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    vc=nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name="Col"
    uvn=nt.nodes.new("ShaderNodeUVMap"); uvn.uv_map="UVMap"; tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=grain; tx.extension='REPEAT'; nt.links.new(uvn.outputs['UV'],tx.inputs[0])
    mx=nt.nodes.new("ShaderNodeMix"); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs[0].default_value=1.0
    nt.links.new(vc.outputs['Color'],mx.inputs[6]); nt.links.new(tx.outputs['Color'],mx.inputs[7]); nt.links.new(mx.outputs[2],b.inputs['Base Color'])
    return m
newmat={}; report_mats=collections=None
for name,kind in plan.items():
    m=bpy.data.materials[name]; b=principled(m)
    if kind=="keep": newmat[name]=m
    elif kind=="family":
        r,mt_,n=fam_stats.get(name,(0.6,0.0,1)); newmat[name]=mk_family("D "+name,r/max(n,1),mt_/max(n,1))
    elif kind=="bake": newmat[name]=mk("D "+name,tile=tiles[name],rough=rough_of(m),metal=b.inputs['Metallic'].default_value)
    elif kind=="floor":
        img=next(n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE'); newmat[name]=mk("D "+name,img=img,rough=0.42,uvscale=(1/1.2,1/1.2,1/1.2))
    elif kind=="emit":
        ec=b.inputs['Emission Color'].default_value; newmat[name]=mk("D "+name,base=b.inputs['Base Color'].default_value,rough=0.4,emit=ec,emit_str=emission_strength(m))
    else:   # emissive image (screens): keep the image through UV, freeze strength
        img=next((n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image),None); newmat[name]=mk("D "+name,img=img,rough=0.1,emit=(1,1,1,1),emit_str=emission_strength(m))
        nt=newmat[name].node_tree; tx=next(n for n in nt.nodes if n.type=='TEX_IMAGE'); bp=principled(newmat[name]); nt.links.new(tx.outputs['Color'],bp.inputs['Emission Color'])
# ---------------------------------------------------------------- 3. delivery copies + export
dcol=bpy.data.collections.new("CR_DELIVERY_COPIES"); sc.collection.children.link(dcol); copies=[]
for o in src:
    c=o.copy(); c.data=o.data.copy(); c.name="D_"+o.name; dcol.objects.link(c); copies.append(c)
    if "Mat" in c.data.color_attributes: c.data.color_attributes.remove(c.data.color_attributes["Mat"])      # a second colour attribute makes the glTF exporter write white COLOR_0 (tested); the Mat values are family constants in the export
    if "Col" in c.data.color_attributes: c.data.color_attributes.active_color=c.data.color_attributes["Col"]; c.data.color_attributes.render_color_index=c.data.color_attributes.find("Col")
    for i,s in enumerate(c.material_slots):
        if s.material: c.data.materials[i]=newmat[s.material.name]
bpy.ops.object.select_all(action='DESELECT')
for c in copies: c.select_set(True)
bpy.context.view_layer.objects.active=copies[0]
glb=os.path.join(OUT,"control_room_delivery.glb")
bpy.ops.export_scene.gltf(filepath=glb,export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_yup=True)
print("exported",glb,os.path.getsize(glb)//1024,"KiB")
inv_tiles=[(n,i.size[0],i.size[1]) for n,i in tiles.items()]
img_all={i.name:(i.size[0],i.size[1]) for m in newmat.values() if m.node_tree for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image for i in [n.image]}
rep={"source":os.path.basename(SRC),"scope_objects":len(src),"source_triangles":src_tris,"source_bounds_min":src_min.round(4).tolist(),"source_bounds_max":src_max.round(4).tolist(),
     "materials":{k:sum(1 for v in plan.values() if v==k) for k in set(plan.values())},"baked_tiles":len(tiles),"delivery_images":len(img_all),"delivery_image_megapixels":round(sum(w*h for w,h in img_all.values())/1e6,2),
     "glb_kib":os.path.getsize(glb)//1024,"note_tiles":"single-location 256 px albedo bake of procedural materials; not seamless; roughness/metal constant; no normal/AO; screens, LEDs, lamps frozen at frame 1; drivers, stability reactions and TV cycle are not exported"}
# ---------------------------------------------------------------- 4. round trip in an empty scene
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
imp=[o for o in bpy.data.objects if o.type=="MESH"]
i_tris=sum(tris(o) for o in imp); i_min,i_max=bounds(imp)
uvz=0; uvt=0
for o in imp:
    me=o.data
    if me.uv_layers:
        uv=me.uv_layers.active.data; a=np.empty(len(uv)*2,dtype=np.float32); uv.foreach_get("uv",a); a=a.reshape(-1,2); uvt+=len(a); uvz+=int((np.abs(a).sum(1)<1e-9).sum())
imats={m.name for o in imp for m in o.data.materials if m}; 
rep.update({"reimport_objects":len(imp),"reimport_triangles":i_tris,"reimport_bounds_min":i_min.round(4).tolist(),"reimport_bounds_max":i_max.round(4).tolist(),
            "bounds_max_abs_diff_m":float(max(np.abs(i_min-src_min).max(),np.abs(i_max-src_max).max())),"reimport_materials":len(imats),"reimport_uv_loops_at_origin_pct":round(100*uvz/max(1,uvt),1),
            "reimport_images":len([i for i in bpy.data.images if i.size[0]>0 and i.name not in("Render Result","Viewer Node")])})
# a glTF-compliant engine multiplies COLOR_0 into the base colour; Blender's importer keeps the attribute but not the multiply, so the check render adds it
vc_prims=0
for o in imp:
    ca=o.data.color_attributes
    if len(ca)==0: continue
    vc_prims+=1; nm=ca[0].name
    for m in o.data.materials:
        if not m or not m.use_nodes: continue
        nt=m.node_tree; b=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if b is None or any(n.type=='VERTEX_COLOR' for n in nt.nodes): continue
        vcn=nt.nodes.new("ShaderNodeVertexColor"); vcn.layer_name=nm; mx=nt.nodes.new("ShaderNodeMix"); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs[0].default_value=1.0
        lk=b.inputs['Base Color'].links
        if lk: nt.links.new(lk[0].from_socket,mx.inputs[6])
        else: mx.inputs[6].default_value=b.inputs['Base Color'].default_value
        nt.links.new(vcn.outputs['Color'],mx.inputs[7]); nt.links.new(mx.outputs[2],b.inputs['Base Color'])
rep["reimport_objects_with_vertex_colour"]=vc_prims
if RENDER:
    sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=16; sc.cycles.use_denoising=True
    w=bpy.data.worlds.new("w"); w.use_nodes=True; w.node_tree.nodes["Background"].inputs[0].default_value=(0.55,0.57,0.6,1); w.node_tree.nodes["Background"].inputs[1].default_value=1.0; sc.world=w
    for loc,e in (((-1.4,-8.0,8.3),500),((0.8,-10.4,8.3),300)):
        ld=bpy.data.lights.new("l","AREA"); ld.size=3; ld.energy=e; lo=bpy.data.objects.new("l",ld); lo.location=loc; sc.collection.objects.link(lo)
    cd=bpy.data.cameras.new("c"); cd.lens=20; co=bpy.data.objects.new("c",cd); sc.collection.objects.link(co); co.location=(-4.6,-6.8,6.9); co.rotation_euler=(Vector((0.5,-9.8,6.5))-Vector(co.location)).to_track_quat('-Z','Y').to_euler(); sc.camera=co
    sc.render.resolution_x,sc.render.resolution_y=1100,620; sc.view_settings.view_transform='AgX'; sc.render.filepath=os.path.join(OUT,"control_room_delivery_roundtrip.png"); bpy.ops.render.render(write_still=True)
rep["runtime_s"]=round(time.time()-T0)
rep["status"]={"technical_roundtrip":"see numbers (objects/triangles/bounds/materials/UV)","visual_roundtrip":"render written, must be opened and judged","engine_import_and_player":"Blocked: no asset-specific validator or working Unity target"}
json.dump(rep,open(os.path.join(OUT,"control_room_delivery_report.json"),"w"),indent=1); print(json.dumps(rep,indent=1))
