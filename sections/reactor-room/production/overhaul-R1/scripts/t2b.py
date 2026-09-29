import bpy,sys,os,re,math,collections
S=sys.argv[sys.argv.index("--")+1]; OUT=S+"/engine"
bpy.ops.wm.open_mainfile(filepath=S+"/w45.blend"); sc=bpy.context.scene; sc.frame_set(1); bpy.context.view_layer.update()
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=8; sc.cycles.use_denoising=False
def slug(n): return re.sub(r'[^A-Za-z0-9]+','_',n).strip('_')
used=collections.OrderedDict()
for o in bpy.data.objects:
    if o.type in('MESH','CURVE','FONT'):
        for s in o.material_slots:
            if s.material: used[s.material.name]=s.material
def prin(m): return next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
def emissive(m):
    b=prin(m)
    return bool(b and b.inputs['Emission Strength'].default_value>0.05 and sum(b.inputs['Emission Color'].default_value[:3])>0.05)
def glassy(m):
    b=prin(m); return bool(b and 'Transmission Weight' in b.inputs and b.inputs['Transmission Weight'].default_value>0.05)
SKIP=("RF ","LP haze","pool_medium","water","GT_")
bake=[n for n,m in used.items() if not emissive(m) and not glassy(m) and prin(m) and not n.startswith(("RF ","LP ")) and n not in("pool_medium","water","R2 puddle")]
print("materials to bake:",len(bake))
# ---- bake each onto a flat 2 m plane at z=2 m (horizontal), colour only
bpy.ops.mesh.primitive_plane_add(size=2.0,location=(0.0,0.0,2.0)); pl=bpy.context.active_object; pl.name="BAKEPLANE"
baked={}
for n in bake:
    m=used[n].copy(); m.name="BAKE_"+slug(n); pl.data.materials.clear(); pl.data.materials.append(m)
    nt=m.node_tree; img=bpy.data.images.new("bake_"+slug(n),512,512); tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=img; nt.nodes.active=tx
    for nd in nt.nodes: nd.select=False
    tx.select=True
    bpy.ops.object.select_all(action='DESELECT'); pl.select_set(True); bpy.context.view_layer.objects.active=pl
    try:
        bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'},margin=4)
        p=f"{OUT}/textures/{slug(n)}.png"; img.filepath_raw=p; img.file_format='PNG'; img.save(); baked[n]=p
    except Exception as e: print("bake failed",n,e)
    bpy.data.materials.remove(m)
print("baked:",len(baked))
bpy.data.objects.remove(pl,do_unlink=True)
# ---- engine materials (simple PBR: baked albedo, constant roughness/metal; emissive kept as colour)
eng={}
for n,m in used.items():
    b=prin(m); e=bpy.data.materials.new("ENG "+n); e.use_nodes=True; eb=e.node_tree.nodes["Principled BSDF"]
    rough=b.inputs['Roughness'].default_value if b else 0.6; metal=b.inputs['Metallic'].default_value if b else 0.0
    eb.inputs['Roughness'].default_value=rough; eb.inputs['Metallic'].default_value=metal
    if n in baked:
        t=e.node_tree.nodes.new("ShaderNodeTexImage"); t.image=bpy.data.images.load(baked[n]); e.node_tree.links.new(t.outputs['Color'],eb.inputs['Base Color'])
    elif b:
        eb.inputs['Base Color'].default_value=tuple(b.inputs['Base Color'].default_value)
        if emissive(m): eb.inputs['Emission Color'].default_value=tuple(b.inputs['Emission Color'].default_value); eb.inputs['Emission Strength'].default_value=b.inputs['Emission Strength'].default_value
        if glassy(m) or n in("water","observation_glass","glass") or "glazing" in n.lower():
            eb.inputs['Alpha'].default_value=0.28; e.blend_method='BLEND' if hasattr(e,'blend_method') else None
    eng[n]=e
for o in bpy.data.objects:
    if o.type in('MESH','CURVE','FONT'):
        for s in o.material_slots:
            if s.material and s.material.name in eng: s.material=eng[s.material.name]
# hide non-exportable helpers
for o in bpy.data.objects:
    if o.name.startswith(("LP haze","Water surface","Deep water")) or (o.type=='MESH' and any(s.material and s.material.name in("ENG RF outdoor sky","ENG pool_medium") for s in o.material_slots)): o.hide_viewport=True; o.hide_render=True
for o in bpy.data.objects: o.select_set(False)
try:
    bpy.ops.export_scene.gltf(filepath=OUT+"/reactor_room_R1.glb",export_format='GLB',use_visible=True,export_apply=True,export_animations=True,export_lights=False,export_cameras=False,export_image_format='AUTO')
    print("GLB exported",os.path.getsize(OUT+"/reactor_room_R1.glb")//1024,"KB")
except Exception as e: print("GLB export failed:",e)
print("ok")
