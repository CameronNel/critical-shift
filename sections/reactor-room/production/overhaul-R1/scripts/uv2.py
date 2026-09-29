import bpy,bmesh,sys,math,collections; sys.path.insert(0,"."); from r2lib import *
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w44.blend")
# ---- world-scale box-projected UVs (1 UV unit = 2 m) so tileable textures apply directly
nu=0; TILE=2.0
for o in bpy.data.objects:
    if o.type!='MESH' or o.name.startswith(("LP haze",)) or not o.data.polygons: continue
    me=o.data; mw=o.matrix_world
    bm=bmesh.new(); bm.from_mesh(me); uv=bm.loops.layers.uv.verify()
    for f in bm.faces:
        nrm=(mw.to_3x3()@f.normal); ax=max(range(3),key=lambda i:abs(nrm[i]))
        for l in f.loops:
            p=mw@l.vert.co
            l[uv].uv=((p.y,p.z) if ax==0 else (p.x,p.z) if ax==1 else (p.x,p.y))
            l[uv].uv=(l[uv].uv[0]/TILE,l[uv].uv[1]/TILE)
    bm.to_mesh(me); bm.free(); nu+=1
print("meshes UV-mapped:",nu)
bpy.ops.wm.save_as_mainfile(filepath=S+"/w45.blend"); print("ok")
