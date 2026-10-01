"""Control-room decal atlas (run on a built/optimised blend, before cr_delivery).
usage: python cr_atlas_decals.py -- <in.blend> <out.blend> [--size 2048]
Every image-with-UV-quad material (posters, notices, sticky notes, stains, floor paint, stencil, family photo; NOT the tiled floor tile, CRT/TV screens
or keyboard) is packed into ONE RGBA atlas with 4 px edge padding, the faces' UVs are remapped into their atlas cell, all of them share ONE material
('CR decals atlas') and the objects are joined into 'CR static decals'.  Typically 24 materials / 24 images / many draw calls -> 1 / 1 / 1.
The atlas is scaled uniformly (<= 1) only as much as needed to fit; stickies and small stains stay at native resolution unless that scale is < 1.
Look is unchanged apart from a shared roughness (0.75) and the resample."""
import bpy,sys,re,os,math
import numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import crk
A=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A[0],A[1]; SIZE=int(A[A.index("--size")+1]) if "--size" in A else 2048; PAD=4
bpy.ops.wm.open_mainfile(filepath=SRC)
PAT=re.compile(r"CR (decal|notice|poster|sticky|stencil|family photo|floor (arrow|operator))")
C=bpy.data.collections["31 CR CONTROL ROOM REDO"]
mats=[m for m in bpy.data.materials if PAT.match(m.name) and m.use_nodes and any(n.type=='TEX_IMAGE' and n.image for n in m.node_tree.nodes)]
def img_of(m): return next(n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image)
objs=[o for o in C.all_objects if o.type=='MESH' and any(x in mats for x in o.data.materials)]
# the decal must be a plain 0..1 quad texture
ok=[]
for m in mats:
    umax=0
    for o in objs:
        for p in o.data.polygons:
            if p.material_index<len(o.data.materials) and o.data.materials[p.material_index]==m:
                uv=o.data.uv_layers.active.data
                for li in p.loop_indices: umax=max(umax,abs(uv[li].uv[0]),abs(uv[li].uv[1]),0)
    if umax<=1.0001: ok.append(m)
    else: print("skip (tiled):",m.name)
mats=ok
def pack(scale):
    sizes={m:(max(4,int(round(img_of(m).size[0]*scale))),max(4,int(round(img_of(m).size[1]*scale)))) for m in mats}
    order=sorted(mats,key=lambda m:-sizes[m][1]); x=y=rowh=0; cells={}
    for m in order:
        w,h=sizes[m]
        if x+w+2*PAD>SIZE: x=0; y+=rowh; rowh=0
        if y+h+2*PAD>SIZE or w+2*PAD>SIZE: return None
        cells[m]=(x+PAD,y+PAD,w,h); x+=w+2*PAD; rowh=max(rowh,h+2*PAD)
    return cells
scale=1.0; cells=pack(scale)
while cells is None and scale>0.3: scale-=0.025; cells=pack(scale)
if cells is None: raise SystemExit("decals do not fit")
print("atlas %d px, %d materials, scale %.3f"%(SIZE,len(mats),scale))
atlas=np.zeros((SIZE,SIZE,4),dtype=np.float32); atlas[...,:3]=0.5
for m,(x,y,w,h) in cells.items():
    im=img_of(m).copy();
    if (w,h)!=tuple(im.size): im.scale(w,h)
    a=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4); bpy.data.images.remove(im)
    atlas[y:y+h,x:x+w]=a
    atlas[y-PAD:y,x:x+w]=a[0:1]; atlas[y+h:y+h+PAD,x:x+w]=a[-1:]                              # edge padding (no bleeding between cells)
    atlas[y-PAD:y+h+PAD,x-PAD:x]=atlas[y-PAD:y+h+PAD,x:x+1]; atlas[y-PAD:y+h+PAD,x+w:x+w+PAD]=atlas[y-PAD:y+h+PAD,x+w-1:x+w]
old=bpy.data.images.get("CR decals atlas")
if old: bpy.data.images.remove(old)
ai=bpy.data.images.new("CR decals atlas",SIZE,SIZE,alpha=True); ai.colorspace_settings.name='sRGB'; ai.pixels.foreach_set(atlas.reshape(-1)); ai.pack()
am=crk.decal_mat("CR decals atlas",ai,rough=0.75)
# remap UVs + materials
for o in objs:
    me=o.data; uv=me.uv_layers.active.data; mt=list(me.materials)
    for p in me.polygons:
        m=mt[p.material_index] if p.material_index<len(mt) else None
        if m in cells:
            x,y,w,h=cells[m]
            for li in p.loop_indices:
                u,v=uv[li].uv; uv[li].uv=((x+0.5+u*(w-1))/SIZE,(y+0.5+v*(h-1))/SIZE)
    new=[am if m in cells else m for m in mt]; uniq=[]
    for m in new:
        if m not in uniq: uniq.append(m)
    idx=[uniq.index(m) for m in new]
    for p in me.polygons: p.material_index=idx[p.material_index] if p.material_index<len(idx) else 0
    me.materials.clear()
    for m in uniq: me.materials.append(m)
# join the all-atlas objects
pure=[o for o in objs if len(o.data.materials)==1 and o.data.materials[0]==am]
for o in pure: o.data.uv_layers[0].name="UVMap"
for o in bpy.context.view_layer.objects: o.select_set(False)
for o in pure: o.select_set(True)
bpy.context.view_layer.objects.active=pure[0]; bpy.ops.object.join(); pure[0].name="CR static decals"
for m in cells:
    if m.users==0: bpy.data.materials.remove(m)
for im in [i for i in bpy.data.images if i.users==0 and i.name!="CR decals atlas" and i.name.startswith("CR ")]: bpy.data.images.remove(im)
nm=len({x.name for o in C.all_objects if o.type=='MESH' for x in o.data.materials if x})
print("decal objects %d -> %d, materials in the control room now %d"%(len(objs),1+len(objs)-len(pure),nm))
bpy.ops.wm.save_as_mainfile(filepath=DST)
