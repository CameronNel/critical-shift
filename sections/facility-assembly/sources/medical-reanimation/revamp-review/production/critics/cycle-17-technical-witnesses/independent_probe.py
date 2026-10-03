import bpy, bmesh, json, math, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation')
W=R/'revamp-review/production/critics/cycle-17-technical-witnesses'
SOURCE=R/'module_overhaul_R2.blend'
before=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False)
s=bpy.data.scenes['REANIMATION_EDIT_LOCAL'];bpy.context.window.scene=s;bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
reg=json.loads((R/'revamp-review/production/support-registry.json').read_text())
registered={r['object'] for r in reg}; terminals=sorted({r['target'] for r in reg}-registered)
def dump(name,data): (W/name).write_text(json.dumps(data,indent=2)+'\n')
cache={}; inventory=[];uvs=[];wind=[]
def get(n):
    if n in cache:return cache[n]
    o=s.objects[n]; ev=o.evaluated_get(deps); md=ev.to_mesh();md.calc_loop_triangles()
    vs=[o.matrix_world@v.co for v in md.vertices];faces=[tuple(p.vertices) for p in md.polygons]
    data={'verts':vs,'faces':faces,'tree':BVHTree.FromPolygons(vs,faces),
          'triangles':[tuple(t.vertices) for t in md.loop_triangles],
          'normals':[(o.matrix_world.to_3x3().inverted().transposed()@p.normal).normalized() for p in md.polygons]}
    ev.to_mesh_clear();cache[n]=data;return data
def bounds(vs):return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
def nodes(nt,seen=()):
    if nt.name in seen:return []
    res=list(nt.nodes)
    for n in nt.nodes:
        if n.type=='GROUP' and n.node_tree:res+=nodes(n.node_tree,seen+(nt.name,))
    return res
for o in s.objects:
    if o.type!='MESH':continue
    g=get(o.name); attrs={k:o[k] for k in o.keys() if k in ('support_target','contact_check_surface_all_vertices','assembly_contact_contracts','support_components','art_equipment_part')}
    inventory.append({'name':o.name,'parent':o.parent.name if o.parent else None,'mesh':o.data.name,'bounds':bounds(g['verts']), 'dimensions':list(o.dimensions),'matrix_world':[list(row) for row in o.matrix_world], 'local':o.library is None and o.data.library is None,'vertices':len(g['verts']),'faces':len(g['faces']),'uv_layers':list(o.data.uv_layers.keys()),'materials':[m.name if m else None for m in o.data.materials],'properties':attrs})
    consumers={}
    for m in o.data.materials:
        if m and m.use_nodes:
            for n in nodes(m.node_tree):
                if n.type=='UVMAP' and n.outputs['UV'].is_linked:consumers.setdefault(n.uv_map,[]).append(m.name)
    if o.name.startswith('MED_R2 |') or o.data.name.startswith('MED | Skill revised'):consumers.setdefault('MED_Physical_1m',[])
    o.data.calc_loop_triangles()
    for name,mats in consumers.items():
        uv=o.data.uv_layers.get(name);finite=True;degenerate=[];ratios=[]
        if uv:
            for p in o.data.polygons:
                coords=[uv.data[li].uv for li in p.loop_indices]
                finite &= all(math.isfinite(x) for q in coords for x in q)
                area=abs(sum(coords[i].cross(coords[(i+1)%len(coords)]) for i in range(len(coords)))/2)
                if area<1e-12:degenerate.append(p.index)
            for tri in o.data.loop_triangles:
                q=[uv.data[i].uv for i in tri.loops];v=[o.matrix_world@o.data.vertices[i].co for i in tri.vertices]
                a3=(v[1]-v[0]).cross(v[2]-v[0]).length/2;a2=abs((q[1]-q[0]).cross(q[2]-q[0]))/2
                if a3>1e-12:ratios.append(a2/a3)
        uvs.append({'object':o.name,'layer':name,'material_consumers':sorted(set(mats)),'exists':bool(uv),'faces':len(o.data.polygons),'finite':finite if uv else False,'zero_face_area_indices':degenerate,'area_density_min':min(ratios) if ratios else None,'area_density_max':max(ratios) if ratios else None})
    # All authored/revised and all declared mount roots are included.
    if o.name.startswith('MED_R2 |') or o.data.name.startswith('MED | Skill revised') or o.name in terminals:
        bm=bmesh.new();bm.from_mesh(o.data);bad=sum(len(e.link_loops)==2 and e.link_loops[0].vert==e.link_loops[1].vert for e in bm.edges)
        pending=set(bm.faces);closed=0;negative=0;open_islands=0
        while pending:
            todo=[pending.pop()];isl=set(todo)
            while todo:
                f=todo.pop()
                for e in f.edges:
                    for n in e.link_faces:
                        if n in pending:pending.remove(n);isl.add(n);todo.append(n)
            if all(len(e.link_faces)==2 for f in isl for e in f.edges):
                closed+=1;vol=0
                for f in isl:
                    v=[l.vert.co for l in f.loops];vol+=sum(v[0].dot(v[i].cross(v[i+1]))/6 for i in range(1,len(v)-1))
                if vol< -1e-10:negative+=1
            else:open_islands+=1
        wind.append({'object':o.name,'inconsistent_edges':bad,'negative_closed_components':negative,'closed_components':closed,'open_components':open_islands});bm.free()
dump('geometry-inventory.json',inventory);dump('uv-consumers.json',uvs);dump('winding.json',wind)
# Directional, evaluated-face witnesses to registry targets, independently computed.
contacts=[]
for r in reg:
    own=get(r['object']);tg=get(r['target']);obj=s.objects[r['object']]
    for a in r['anchors']:
        pt=obj.matrix_world@Vector(a['local_point']);dr=Vector(a['approach_world']).normalized();hit,n,i,d=tg['tree'].ray_cast(pt-dr*.02,dr,.035)
        witness=own['tree'].find_nearest(pt)[3]
        contacts.append({'object':r['object'],'target':r['target'],'point_world':list(pt),'direction_world':list(dr),'target_surface_world':list(hit) if hit else None,'signed_gap_m':d-.02 if hit else None,'target_normal_world':list(n) if n else None,'normal_angle_deg':math.degrees(n.angle(Vector(a['expected_surface_normal_world']))) if n else None,'own_surface_distance_m':witness,'registered_tolerance_m':[r['max_gap_m'],r['max_penetration_m']]})
dump('directional-contacts.json',contacts)
# Intended retained terminal roots: candidates are only same-assembly members;
# these possible interfaces are observations, never automatic support passes.
term=[]
for name in terminals:
    o=s.objects[name];g=get(name);probes=[]
    # Real face centroid projected onto its polygon tree avoids empty n-gon centres.
    pts=list(g['verts']);pts.extend(sum((g['verts'][i] for i in f),Vector())/len(f) for f in g['faces'])
    same=[q for q in s.objects if q.type=='MESH' and q.name!=name and q.parent==o.parent and not q.name.startswith('MED_R2 |')]
    for q in same:
        tg=get(q.name);nearest=min((tg['tree'].find_nearest(pt) for pt in pts),key=lambda h:h[3])
        if nearest[3]<.012:
            probes.append({'candidate':q.name,'minimum_sampled_surface_distance_m':nearest[3],'point_target_world':list(nearest[0]),'normal_target_world':list(nearest[1])})
    term.append({'terminal':name,'parent':o.parent.name if o.parent else None,'bounds':bounds(g['verts']),'same_assembly_close_surfaces':sorted(probes,key=lambda p:p['minimum_sampled_surface_distance_m'])})
dump('retained-terminal-candidate-interfaces.json',term)
# The case-to-shelf path comes from each actual registry pair. Check both the case
# and its mount in gravity direction using bottom-facing evaluated face vertices.
stock=[]
for r in reg:
    if r.get('kind')!='stored_stock_downward_bearing':continue
    mount=r['target'];mountrec=next(x for x in reg if x['object']==mount);shelf=mountrec['target'];ob=get(r['object']);mg=get(mount);sg=get(shelf)
    def gravity(g,target):
        zs=min(p.z for p in g['verts']);ps=[p for p in g['verts'] if abs(p.z-zs)<.0001];out=[]
        for p in ps:
            hit,n,i,d=target['tree'].ray_cast(p+Vector((0,0,.01)),Vector((0,0,-1)),.2)
            if hit is not None:out.append({'point':list(p),'gap_m':d-.01,'normal_z':n.z,'hit':list(hit)})
        return {'bottom_z_m':zs,'points_tested':len(ps),'ray_hits':out}
    stock.append({'case':r['object'],'mount':mount,'shelf':shelf,'case_to_mount':gravity(ob,mg),'mount_to_shelf':gravity(mg,sg),'direct_case_to_shelf':gravity(ob,sg)})
dump('stock-gravity-load-paths.json',stock)
dump('probe-provenance.json',{'source_sha256':before,'source_sha_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==before,'blender':bpy.app.version_string,'scene':s.name,'scene_local':s.library is None,'objects':len(s.objects),'mesh_count':len(inventory),'registry_records':len(reg),'terminal_count':len(term),'uv_checks':len(uvs),'contact_anchors':len(contacts),'no_source_save':True})
print('INDEPENDENT_PROBE_COMPLETE',len(inventory),len(uvs),len(contacts),len(term),flush=True)
