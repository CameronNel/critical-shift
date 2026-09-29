"""Static merge pass: join non-animated, non-interactive single-material meshes per (collection, material, 6x6x5 m cell)."""
import bpy,sys,re,collections,math
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w25.blend")
MERGE_COLS=("03 POOL AND RAIL","19 CONTROL FIDELITY","07 EAST CONTROL ROOM","18 CONTROL ROOM DRESSING","22 ASSET KIT 1","20 CONTROL MEZZANINE","21 ELEVATOR","23 R2 FLOOR AND DRESSING","GROK GT_Hero","GROK GT_Desk")
GAMEPLAY=re.compile(r"^[A-Z0-9][A-Z0-9_ /\-\.]{3,}$")   # ALL-CAPS names are interaction/logic objects (BANK_A_MOVING, SCRAM, ...)
KEEP=re.compile(r"(water|medium|glass|gate|hinge|door|pivot|hatch|EL |LP |sky|light well)",re.I)
def animated(o):
    p=o
    while p:
        if p.animation_data and (p.animation_data.action or p.animation_data.drivers): return True
        p=p.parent
    return False
cand=[];skipped=collections.Counter();baked=0
for o in bpy.data.objects:
    if o.type!='MESH': continue
    cn=o.users_collection[0].name if o.users_collection else ""
    if cn not in MERGE_COLS: continue
    if o.parent or animated(o): skipped["parented/animated"]+=1; continue
    if o.modifiers:
        types={m.type for m in o.modifiers}
        if not types<= {"BEVEL","WEIGHTED_NORMAL","TRIANGULATE","SOLIDIFY","MIRROR","ARRAY"}: skipped["other modifiers "+",".join(sorted(types))]+=1; continue
        dg=bpy.context.evaluated_depsgraph_get(); me=bpy.data.meshes.new_from_object(o.evaluated_get(dg)); old=o.data
        o.modifiers.clear(); o.data=me; baked+=1
        if old.users==0: bpy.data.meshes.remove(old)
    if GAMEPLAY.match(o.name.split('.')[0]) or KEEP.search(o.name): skipped["gameplay/keep-name"]+=1; continue
    ms=[s.material for s in o.material_slots if s.material]
    if len(ms)!=1: skipped["multi/no material"]+=1; continue
    if o.hide_render or o.hide_viewport: skipped["hidden"]+=1; continue
    c=o.matrix_world.translation
    b=[o.matrix_world@__import__('mathutils').Vector(v) for v in o.bound_box]; cx=sum(v.x for v in b)/8; cy=sum(v.y for v in b)/8; cz=sum(v.z for v in b)/8
    key=(cn,ms[0].name,math.floor(cx/6),math.floor(cy/6),math.floor(cz/5)); cand.append((key,o))
groups=collections.defaultdict(list)
for k,o in cand: groups[k].append(o)
before=len([o for o in bpy.data.objects if o.type=='MESH'])
joined=0
for k,objs in groups.items():
    if len(objs)<2: continue
    for o in bpy.context.view_layer.objects: o.select_set(False)
    act=objs[0]
    with bpy.context.temp_override(active_object=act,selected_editable_objects=objs,selected_objects=objs):
        bpy.ops.object.join()
    act.name=f"MERGED {k[0][:12]} {k[1][:18]} {k[2]}_{k[3]}_{k[4]}"; act["merged_from"]=len(objs); joined+=len(objs)
after=len([o for o in bpy.data.objects if o.type=='MESH'])
print("modifiers baked:",baked); print("groups merged:",sum(1 for g in groups.values() if len(g)>1),"objects consumed:",joined,"| mesh objects before/after:",before,after,"| skipped:",dict(skipped))
bpy.ops.wm.save_as_mainfile(filepath=S+"/w26.blend"); print("ok")
