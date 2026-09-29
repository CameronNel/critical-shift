import bpy,bmesh,sys,re,math,collections
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w35.blend"); sc=bpy.context.scene
GAME=re.compile(r"^[A-Z0-9][A-Z0-9_ /\-\.]{3,}$")
# 1. decorative gauge ticks are micro detail: drop them
n=0
for o in list(bpy.data.objects):
    if o.type=='CURVE' and o.name.split('.')[-1].startswith("tick") or (o.type=='CURVE' and ".tick" in o.name): bpy.data.objects.remove(o,do_unlink=True); n+=1
print("gauge tick curves removed:",n)
# 2. cheap glyph and curve tessellation
for cu in bpy.data.curves:
    if cu.users==0: continue
    cu.resolution_u=1 if hasattr(cu,'body') else 2
    if hasattr(cu,'body'): cu.extrude=0.0; cu.bevel_depth=0.0
    else: cu.bevel_resolution=0
# 3. convert non-gameplay text/curve objects to meshes
cv=[o for o in bpy.data.objects if o.type in('FONT','CURVE') and not GAME.match(o.name.split('.')[0]) and not o.animation_data]
for o in bpy.context.view_layer.objects: o.select_set(False)
for o in cv: o.select_set(True)
bpy.context.view_layer.objects.active=cv[0]
with bpy.context.temp_override(active_object=cv[0],selected_objects=cv,selected_editable_objects=cv): bpy.ops.object.convert(target='MESH')
print("converted text/curve objects to meshes:",len(cv))
# 4. merge them (and anything else small and static) per collection/material/cell
def animated(o):
    p=o
    while p:
        if p.animation_data and (p.animation_data.action or p.animation_data.drivers): return True
        p=p.parent
    return False
groups=collections.defaultdict(list)
for o in bpy.data.objects:
    if o.type!='MESH' or o.parent or animated(o) or o.modifiers or GAME.match(o.name.split('.')[0]) or o.hide_render: continue
    if o.name.startswith(("MERGED","R2 ","LP ","EL ")) and o not in cv: continue
    ms=[s.material for s in o.material_slots if s.material]
    if len(ms)!=1 or not o.data.polygons: continue
    b=[o.matrix_world@v.co for v in o.data.vertices[:1]] or [o.matrix_world.translation]
    cn=o.users_collection[0].name if o.users_collection else ""
    if cn.startswith("RF "): continue
    groups[(cn,ms[0].name,math.floor(b[0].x/6),math.floor(b[0].y/6),math.floor(b[0].z/5))].append(o)
joined=0
for k,objs in groups.items():
    if len(objs)<2: continue
    for o in bpy.context.view_layer.objects: o.select_set(False)
    act=objs[0]
    with bpy.context.temp_override(active_object=act,selected_editable_objects=objs,selected_objects=objs): bpy.ops.object.join()
    act.name=f"MERGED {k[0][:12]} {k[1][:18]} {k[2]}_{k[3]}_{k[4]}"; joined+=len(objs)
print("small objects merged:",joined)
# 5. UVs for anything new
TILE=2.0; nu=0
for o in bpy.data.objects:
    if o.type!='MESH' or not o.data.polygons or o.data.uv_layers: continue
    me=o.data; mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(me); uv=bm.loops.layers.uv.verify()
    for f in bm.faces:
        nrm=(mw.to_3x3()@f.normal); ax=max(range(3),key=lambda i:abs(nrm[i]))
        for l in f.loops:
            p=mw@l.vert.co; a=(p.y,p.z) if ax==0 else (p.x,p.z) if ax==1 else (p.x,p.y); l[uv].uv=(a[0]/TILE,a[1]/TILE)
    bm.to_mesh(me); bm.free(); nu+=1
print("new meshes UV-mapped:",nu)
bpy.ops.wm.save_as_mainfile(filepath=S+"/w36.blend"); print("ok")
