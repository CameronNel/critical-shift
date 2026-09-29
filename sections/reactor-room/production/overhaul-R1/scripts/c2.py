import bpy,sys,re,collections; sys.path.insert(0,"."); from lib import *
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w7.blend")
dg=bpy.context.evaluated_depsgraph_get()
def tris(o):
    eo=o.evaluated_get(dg); me=eo.to_mesh(); t=sum(len(p.vertices)-2 for p in me.polygons); eo.to_mesh_clear(); return t
pat=re.compile(r"(washer|screw|drive slot|drive recess|rivet|\bbolt|\bnut\b|tension nut|fixing|fastener|\.anchor|anchors?$|anchor plate|standoff|stud|hardware|locking|keeper|clamp cap|saddle cap|cross bar|flange\.|\bcap\b.*tool|set collar)",re.I)
keep=re.compile(r"^(EL |MZ )")
rm=[];byname=collections.Counter();tt=0
for o in bpy.data.objects:
    if o.type!='MESH' or keep.match(o.name) or o.animation_data or (o.parent and o.parent.animation_data): continue
    if pat.search(o.name):
        t=tris(o)
        if t<1000: rm.append(o); byname[re.sub(r'[.\d]+$','',o.name)[:30]]+=1; tt+=t
print("removing",len(rm),"objs",tt,"tris",byname.most_common(10))
for o in rm: bpy.data.objects.remove(o,do_unlink=True)
for _ in range(3): bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=S+"/w8.blend")
