import bpy,json,pathlib,hashlib,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=pathlib.Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock/revamp/production/critics/full-c05-technical')
dg=bpy.context.evaluated_depsgraph_get();trees={};uvmetrics=[]
for o in bpy.context.scene.objects:
    if o.library or o.type!='MESH':continue
    ev=o.evaluated_get(dg);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];fs=[list(p.vertices) for p in me.polygons]
    if vs and fs:trees[o.name]=BVHTree.FromPolygons(vs,fs,all_triangles=False)
    layer=me.uv_layers.get('CD_Physical_1m');err=0;checked=0
    if layer:
        for face in me.polygons:
            li=list(face.loop_indices)
            for i,a in enumerate(li):
                b=li[(i+1)%len(li)];ga=vs[me.loops[a].vertex_index];gb=vs[me.loops[b].vertex_index];length=(ga-gb).length
                if length>1e-6:err=max(err,abs((layer.data[a].uv-layer.data[b].uv).length-length)/length);checked+=1
    uvmetrics.append({'object':o.name,'metric_uv_exists':bool(layer),'checked_face_edges':checked,'max_relative_edge_length_error':err})
    ev.to_mesh_clear()
contacts=[]
for rootname in json.loads(bpy.context.scene['contact_assemblies']):
    root=bpy.data.objects[rootname];di=Vector(root['support_direction']).normalized();parts=[c.name for c in root.children_recursive if c.name in trees]
    for a in root.children:
        if not a.get('contact_anchor'):continue
        p=a.matrix_world.translation;hits=[]
        for name in parts:
            h=trees[name].ray_cast(p+di*.02,-di,.12)
            if h[0] is not None:hits.append({'name':name,'gap_m':h[3]-.02,'point':list(h[0])})
        contacts.append({'assembly':rootname,'anchor':a.name,'point':list(p),'geometry_hits':sorted(hits,key=lambda x:abs(x['gap_m']))[:4]})
printed=[]
papers=[n for n in trees if any(m and 'paper' in m.name.lower() for m in bpy.data.objects[n].data.materials)]
for o in bpy.context.scene.objects:
    if o.library or o.type!='FONT':continue
    normal=o.matrix_world.to_3x3()@Vector((0,0,1))
    if abs(normal.z)<.9:continue
    ev=o.evaluated_get(dg);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices]
    if not vs or not all(-4.3<v.x<-2.7 and 5.8<v.y<7.8 and .75<v.z<.9 for v in vs):ev.to_mesh_clear();continue
    witnesses=[];gaps=[];hidden=[];missing=0;surfaces=set()
    for i,v in enumerate(vs):
        hits=[]
        for name in papers:
            h=trees[name].ray_cast(Vector((v.x,v.y,1.4)),Vector((0,0,-1)),.7)
            if h[0] is not None:hits.append((h[0].z,name))
        if not hits:missing+=1;continue
        top,name=max(hits);gap=v.z-top;gaps.append(gap);surfaces.add(name)
        if gap<-.000001:witnesses.append({'vertex':i,'point':list(v),'top_paper':name,'top_z':top,'gap_m':gap})
        blockers=[]
        for meshname,tree in trees.items():
            h=tree.ray_cast(Vector((v.x,v.y,1.4)),Vector((0,0,-1)),.7)
            if h[0] is not None and h[0].z>v.z+.000001:blockers.append({'object':meshname,'z':h[0].z})
        if blockers:hidden.append({'vertex':i,'point':list(v),'higher_meshes':blockers})
    printed.append({'font':o.name,'glyph_vertices':len(vs),'top_paper_surfaces':sorted(surfaces),'missing_support_rays':missing,'minimum_gap_to_top_paper_m':min(gaps) if gaps else None,'maximum_gap_to_top_paper_m':max(gaps) if gaps else None,'buried_vertices':witnesses,'occluded_vertices':hidden})
    ev.to_mesh_clear()
R={'native_sha256':hashlib.sha256(pathlib.Path(bpy.data.filepath).read_bytes()).hexdigest(),'anchor_to_actual_assembly_geometry':contacts,'physical_uv_edge_metrics':uvmetrics,'desk_print_above_all_overlapping_paper':printed,'paper_meshes_considered':papers}
(OUT/'contact-uv-probe.json').write_text(json.dumps(R,indent=2));print('CONTACT_UV_DONE',len(contacts),len(uvmetrics),flush=True)
