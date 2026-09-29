import bpy
bpy.ops.wm.open_mainfile(filepath="w36.blend")
for m in bpy.data.materials:
    if m.users: 
        bsdf=[n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'] if m.use_nodes else []
        print("MAT",m.name,m.users, tuple(round(x,2) for x in bsdf[0].inputs[0].default_value[:3]) if bsdf else "")
