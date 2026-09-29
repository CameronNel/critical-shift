import bpy,sys
def stats(f):
    bpy.ops.wm.open_mainfile(filepath=f); dg=bpy.context.evaluated_depsgraph_get()
    tris=0;objs=0;slots=0;mats=set();roof=0
    for o in bpy.data.objects:
        if o.type!='MESH' or o.hide_render: continue
        eo=o.evaluated_get(dg); me=eo.to_mesh(); t=sum(len(p.vertices)-2 for p in me.polygons); eo.to_mesh_clear()
        c=(o.users_collection[0].name if o.users_collection else "")
        if c.startswith("RF "): roof+=t; continue
        tris+=t; objs+=1; ms=[s.material for s in o.material_slots if s.material]; slots+=max(1,len(ms)); mats.update(m.name for m in ms)
    return tris,objs,slots,len(mats),roof
f=sys.argv[sys.argv.index("--")+1]
print("STATS tris=%d objects=%d draw-call-estimate=%d materials=%d roof-proxy-tris=%d"%stats(f))
