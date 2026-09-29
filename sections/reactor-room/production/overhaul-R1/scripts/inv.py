import bpy,collections,re
bpy.ops.wm.open_mainfile(filepath="w36.blend")
for col in bpy.data.collections:
    if col.name.startswith(("05 PER","MF W","W")) :
        objs=[o for o in col.objects]
        print("COL",col.name,len(objs))
        # group by name prefix (first token / strip digits)
        g=collections.Counter(re.sub(r'[\.\d_ ]+$','',o.name)[:34] for o in objs)
        for k,v in g.most_common(25):
            ex=[o for o in objs if o.name.startswith(k)][0]
            print("  ",v,k,ex.type,tuple(round(x,1) for x in ex.location),tuple(round(x,1) for x in ex.dimensions))
