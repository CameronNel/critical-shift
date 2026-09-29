import bpy,collections
bpy.ops.wm.open_mainfile(filepath="w36.blend")
dg=bpy.context.evaluated_depsgraph_get()
def tris(o):
    e=o.evaluated_get(dg)
    try: m=e.to_mesh()
    except: return 0
    if not m: return 0
    n=sum(len(p.vertices)-2 for p in m.polygons); e.to_mesh_clear(); return n
c=collections.defaultdict(lambda:[0,0])
for o in bpy.context.scene.objects:
    if o.type in('LIGHT','CAMERA','EMPTY'): k="_"+o.type; c[k][0]+=1; continue
    col=o.users_collection[0].name if o.users_collection else "?"
    c[col][0]+=1; c[col][1]+=tris(o)
for k,v in sorted(c.items(),key=lambda x:-x[1][1]): print("CAT",k,v[0],v[1])
