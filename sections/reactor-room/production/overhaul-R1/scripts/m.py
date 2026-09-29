import bpy,sys,re,collections
S=sys.argv[sys.argv.index("--")+1]; f=sys.argv[sys.argv.index("--")+2]
bpy.ops.wm.open_mainfile(filepath=S+"/"+f); dg=bpy.context.evaluated_depsgraph_get()
rows=collections.defaultdict(lambda:[0,0]); stems=collections.defaultdict(lambda:[0,0]); tot=0
big=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    eo=o.evaluated_get(dg); me=eo.to_mesh(); t=sum(len(p.vertices)-2 for p in me.polygons); eo.to_mesh_clear(); tot+=t
    c=(o.users_collection[0].name if o.users_collection else "?"); rows[c][0]+=t; rows[c][1]+=1
    s=re.sub(r'[.\d]+$','',o.name)[:32]; stems[s][0]+=t; stems[s][1]+=1
    if t>3000: big.append((t,o.name))
print("TOTAL",tot)
for c,(t,k) in sorted(rows.items(),key=lambda kv:-kv[1][0])[:10]: print("%8d %5d %s"%(t,k,c))
print("--stems")
for s,(t,k) in sorted(stems.items(),key=lambda kv:-kv[1][0])[:25]: print("%8d %5d %s"%(t,k,s))
print("--single objects >3000 tris:",len(big)); 
for t,n in sorted(big,reverse=True)[:12]: print(t,n)
