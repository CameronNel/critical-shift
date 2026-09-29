"""Every SY mesh: exact surface-neighbour screen plus external support probes.

This is a sampled contact audit, not a complete collision/manifold certificate.
Writes transient JSON only. It does not modify the scene.
"""
import bpy,json,ctypes,re,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3];out=root/'runtime/out/spawn-integration';out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();coll=bpy.data.collections['ART | Spawn and medical courtyard']
items=[]
for o in coll.objects:
    if o.type!='MESH':continue
    vs=[o.matrix_world@v.co for v in o.data.vertices];faces=[list(p.vertices) for p in o.data.polygons]
    arr=np.array(vs);lo=arr.min(axis=0);hi=arr.max(axis=0)
    samples=vs[::max(1,len(vs)//32)]+[o.matrix_world@p.center for p in list(o.data.polygons)[::max(1,len(faces)//12)]]
    items.append(dict(o=o,lo=lo,hi=hi,samples=samples,tree=BVHTree.FromPolygons(vs,faces)))
los=np.array([a['lo'] for a in items]);his=np.array([a['hi'] for a in items]);edges=[set() for _ in items];distances={}
for i,a in enumerate(items):
    gap=np.maximum(0,np.maximum(los-a['hi'],a['lo']-his));candidates=np.where(np.linalg.norm(gap,axis=1)<.008)[0]
    for j in candidates:
        if j<=i:continue
        b=items[j];near=[]
        for p in a['samples']:
            q=b['tree'].find_nearest(p,.008)
            if q[0] is not None:near.append(q[3])
        if not near:
            for p in b['samples']:
                q=a['tree'].find_nearest(p,.008)
                if q[0] is not None:near.append(q[3])
        contact=min(near) if near else None
        if contact is None and np.all(gap[j]==0) and a['tree'].overlap(b['tree']):contact=0.
        if contact is not None:edges[i].add(int(j));edges[j].add(i);distances[(i,int(j))]=contact
    if i%300==0:print('SY_CONTACT_PROGRESS',i,flush=True)
# External surface probes: cast against individual evaluated objects, excluding SY.
external=[]
for inst in dg.object_instances:
    o=inst.object
    if o.type!='MESH' or o.original.name.startswith('SY |') or o.hide_render:continue
    mat=inst.matrix_world;pts=np.array([mat@Vector(v) for v in o.bound_box]);lo=pts.min(axis=0);hi=pts.max(axis=0)
    if hi[0]<-40 or lo[0]>5 or hi[1]<6 or lo[1]>43:continue
    gaps=np.maximum(0,np.maximum(los-hi,lo-his))
    if np.linalg.norm(gaps,axis=1).min()>.045:continue
    me=o.to_mesh(preserve_all_data_layers=False,depsgraph=dg)
    if me and me.polygons:
        tree=BVHTree.FromPolygons([mat@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons])
        external.append((o.original.name,tree,lo,hi))
    o.to_mesh_clear()
anchors={};rows=[]
directions=[Vector(v) for v in ((0,0,-1),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1))]
for i,a in enumerate(items):
    candidates=[b for b in external if np.linalg.norm(np.maximum(0,np.maximum(b[2]-a['hi'],a['lo']-b[3])))<.045]
    hits=[]
    for name,tree,lo,hi in candidates:
        if a['o'].name.startswith('SY | Cliff-foot') and a['tree'].overlap(tree):
            hits.append((name,0.));break
        for p in a['samples'][::2]:
            for dr in directions[:5]:
                # Starting 45 mm away catches embedded contact faces as well as gaps.
                origin=p-dr*.045;loc,n,face,dist=tree.ray_cast(origin,dr,.09)
                if loc is not None:
                    d=(loc-p).length
                    if d<.008:hits.append((name,d));break
            if hits:break
        if hits:break
    if hits:anchors[i]=hits[0]
    rows.append(dict(name=a['o'].name,bounds=[a['lo'].tolist(),a['hi'].tolist()],materials=[m.name for m in a['o'].data.materials if m],neighbours=[items[j]['o'].name for j in sorted(edges[i])],external_contact=hits[0] if hits else None))
visited=set();components=[]
for i in range(len(items)):
    if i in visited:continue
    stack=[i];group=set()
    while stack:
        j=stack.pop()
        if j in group:continue
        group.add(j);stack.extend(edges[j]-group)
    visited.update(group);anchored=[j for j in group if j in anchors]
    components.append(dict(count=len(group),external_contacts=[(items[j]['o'].name,anchors[j]) for j in anchored],objects=[items[j]['o'].name for j in sorted(group)]))
report=dict(source_sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),objects=rows,nonmesh=[dict(name=o.name,type=o.type) for o in coll.objects if o.type!='MESH'],components=components,method='All SY meshes; sampled nearest triangle surfaces and triangle overlaps, 8mm contact-screen threshold; component support rays against non-SY evaluated geometry. Must review unsupported components and intentional gaps; not full collision certification.')
(out/'sy-contacts.json').write_text(json.dumps(report,indent=2))
print('SY_CONTACT_SUMMARY',len(items),'components',len(components),'unanchored',[(c['count'],c['objects'][:4]) for c in components if not c['external_contacts']],flush=True)
