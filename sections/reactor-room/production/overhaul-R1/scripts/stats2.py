import bpy,sys,collections
f=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=f); dg=bpy.context.evaluated_depsgraph_get()
tot=collections.Counter(); objs=collections.Counter(); mats=set(); roof=0
for o in bpy.data.objects:
    if o.type not in('MESH','CURVE','FONT') or o.hide_render: continue
    c=(o.users_collection[0].name if o.users_collection else "")
    e=o.evaluated_get(dg)
    try: me=e.to_mesh()
    except Exception: continue
    t=sum(len(p.vertices)-2 for p in me.polygons); e.to_mesh_clear()
    if c.startswith("RF "): roof+=t; continue
    tot[o.type]+=t; objs[o.type]+=1
    for s in o.material_slots:
        if s.material: mats.add(s.material.name)
print("STATS2 total tris=%d objects=%d | mesh %d/%d curve %d/%d font %d/%d | materials=%d roof-proxy=%d"%(sum(tot.values()),sum(objs.values()),tot['MESH'],objs['MESH'],tot['CURVE'],objs['CURVE'],tot['FONT'],objs['FONT'],len(mats),roof))
