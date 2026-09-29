import bpy,sys,re,collections; sys.path.insert(0,"."); from lib import *
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w5.blend")
dg=bpy.context.evaluated_depsgraph_get()
def tris(o):
    eo=o.evaluated_get(dg); me=eo.to_mesh(); t=sum(len(p.vertices)-2 for p in me.polygons); eo.to_mesh_clear(); return t
def total(): return sum(tris(o) for o in bpy.data.objects if o.type=='MESH' and not o.hide_render), sum(1 for o in bpy.data.objects if o.type=='MESH' and not o.hide_render)
print("before",total())
# 1. orphaned stair residue: anything outside the shell in the old stair core volume, not mine
res=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.name.startswith(("EL ","MZ ","East wall patch")): continue
    b=bbw(o)
    if b[0][0]>11.0 and b[0][1]<19.0 and b[1][0]>1.2 and b[1][1]<6.6 and b[2][1]<13.0:
        res.append(o)
print("stair residue objs",len(res),collections.Counter(re.sub(r'[.\d]+$','',o.name)[:26] for o in res).most_common(6))
for o in res: bpy.data.objects.remove(o,do_unlink=True)
# 2. fastener micro-geometry
pat=re.compile(r"(washer|screw|drive slot|drive recess|rivet|\bbolt|nut\b|fixing|fastener|\.anchor|standoff|grub|hex head|cap head)",re.I)
rm=[];byname=collections.Counter()
for o in bpy.data.objects:
    if o.type!='MESH' or o.name.startswith(("EL ","MZ ")): continue
    if pat.search(o.name) and tris(o)<300:
        rm.append(o); byname[re.sub(r'[.\d]+$','',o.name)[:26]]+=1
print("fasteners",len(rm),byname.most_common(8))
for o in rm: bpy.data.objects.remove(o,do_unlink=True)
# purge orphan data
for _ in range(3): bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
dg=bpy.context.evaluated_depsgraph_get()
print("after",total())
bpy.ops.wm.save_as_mainfile(filepath=S+"/w7.blend")
