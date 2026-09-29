import bpy,collections,re
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath="w36.blend")
dg=bpy.context.evaluated_depsgraph_get()
cols=[c for c in bpy.data.collections if c.name.startswith(("05 PER","MF W","W"))]
st=collections.defaultdict(list)
for c in cols:
    for o in c.objects:
        if o.type not in("MESH","CURVE","FONT"): continue
        key=o.name.split(".")[0]
        st[(c.name[:12],key)].append(o)
rows=[]
for (c,k),os in st.items():
    pts=[o.matrix_world@Vector(v) for o in os for v in o.bound_box]
    lo=[min(p[i] for p in pts) for i in range(3)]; hi=[max(p[i] for p in pts) for i in range(3)]
    rows.append((c,k,len(os),lo,hi))
for c,k,n,lo,hi in sorted(rows,key=lambda r:-r[2]):
    print("ST",c,"|",k[:40],n,"x%.1f..%.1f y%.1f..%.1f z%.1f..%.1f"%(lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]))
