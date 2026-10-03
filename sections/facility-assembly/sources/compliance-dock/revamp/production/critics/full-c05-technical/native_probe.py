"""Independent read-only native probe. Never saves the production scene."""
import bpy, bmesh, json, math, hashlib, pathlib, sys
from collections import Counter, defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=pathlib.Path('/workspace/critical-shift')
OUT=ROOT/'sections/facility-assembly/sources/compliance-dock/revamp/production/critics/full-c05-technical'
BASE=json.loads((OUT.parents[1]/'baseline.json').read_text())
def clean(v):
    if isinstance(v,(str,int,float,bool)) or v is None: return v
    if isinstance(v,dict): return {str(k):clean(x) for k,x in v.items()}
    try:return [clean(x) for x in v]
    except:return str(v)
def props(o):return {k:clean(o[k]) for k in o.keys()}
def bounds(vs):return {'min':[min(v[i] for v in vs) for i in range(3)],'max':[max(v[i] for v in vs) for i in range(3)]} if vs else None
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
local=[o for o in bpy.data.objects if o.library is None]
dep=bpy.context.evaluated_depsgraph_get()
report={'blender':bpy.app.version_string,'native':bpy.data.filepath,'sha256':sha(bpy.data.filepath),'scene':bpy.context.scene.name,'scene_properties':props(bpy.context.scene),'collections':[{'name':c.name,'library':c.library.filepath if c.library else None,'props':props(c)} for c in bpy.data.collections if not c.library],'objects':[],'materials':[],'images':[],'fonts':[],'libraries':[],'duplicate_geometry':[],'baseline_matrix_changes':[],'baseline_missing':[],'support_rays':[],'counters':{}}
trees={}; vertices={}; faces={}; duplicate=defaultdict(list)
tri=0; sub=0
for o in local:
    row={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':[list(r) for r in o.matrix_world],'dimensions':list(o.dimensions),'scale':list(o.scale),'determinant':o.matrix_world.to_3x3().determinant(),'props':props(o),'hidden_render':o.hide_render,'hidden_viewport':o.hide_viewport,'collections':[c.name for c in o.users_collection],'data_users':o.data.users if o.data else None,'modifiers':[{'name':m.name,'type':m.type,'show_render':m.show_render,'show_viewport':m.show_viewport} for m in o.modifiers]}
    if o.type=='CAMERA':row['camera']={'lens':o.data.lens,'type':o.data.type,'ortho_scale':o.data.ortho_scale}
    if o.type in {'MESH','FONT','CURVE'}:
        ev=o.evaluated_get(dep); me=ev.to_mesh(); me.calc_loop_triangles(); vs=[o.matrix_world@v.co for v in me.vertices]; fs=[list(p.vertices) for p in me.polygons]
        vertices[o.name]=vs;faces[o.name]=fs
        row.update(bounds=bounds(vs),triangles=len(me.loop_triangles),polygons=len(fs),material_slots=[m.name if m else None for m in me.materials],material_submeshes=len(set(p.material_index for p in me.polygons)),degenerate_faces=[p.index for p in me.polygons if p.area<1e-12],invalid_vertices=sum(not all(math.isfinite(x) for x in v) for v in vs))
        row['uv']={}
        for layer in me.uv_layers:
            zero=0;bad=0;areas=[]
            for p in me.polygons:
                uv=[layer.data[k].uv for k in p.loop_indices]; a=abs(sum(uv[i].x*uv[(i+1)%len(uv)].y-uv[(i+1)%len(uv)].x*uv[i].y for i in range(len(uv)))/2)
                zero+=a<1e-14;bad+=any(not math.isfinite(c) for u in uv for c in u);areas.append(a)
            row['uv'][layer.name]={'zero_area_faces':zero,'nonfinite_faces':bad,'loops':len(layer.data),'min_area':min(areas) if areas else None}
        bm=bmesh.new();bm.from_mesh(me)
        row['topology']={'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'loose_edges':sum(e.is_wire for e in bm.edges),'noncontiguous_manifold_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'signed_volume_local':bm.calc_volume(signed=True)};bm.free()
        if vs and fs: trees[o.name]=BVHTree.FromPolygons(vs,fs,all_triangles=False)
        if vs:
            sig=hashlib.sha256(repr((sorted(tuple(round(x,7) for x in v) for v in vs),sorted(tuple(sorted(tuple(round(x,7) for x in vs[j]) for j in p)) for p in fs))).encode()).hexdigest();duplicate[sig].append(o.name)
        tri+=row['triangles'];sub+=row['material_submeshes'];ev.to_mesh_clear()
    report['objects'].append(row)
report['duplicate_geometry']=[names for names in duplicate.values() if len(names)>1]
for b in BASE['objects']:
    o=bpy.data.objects.get(b['name'])
    if o is None:report['baseline_missing'].append(b['name']);continue
    err=max(abs(o.matrix_world[i][j]-b['matrix'][i][j]) for i in range(4) for j in range(4))
    if err>1e-6:report['baseline_matrix_changes'].append({'name':b['name'],'max_abs_matrix_delta':err})
for m in bpy.data.materials:
    if m.library:continue
    report['materials'].append({'name':m.name,'users':m.users,'props':props(m),'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if getattr(n,'image',None) else None,'inputs':{s.name:clean(s.default_value) for s in n.inputs if hasattr(s,'default_value') and not s.is_linked}} for n in m.node_tree.nodes] if m.use_nodes else [],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links] if m.use_nodes else []})
for im in bpy.data.images:
    p=bpy.path.abspath(im.filepath,library=im.library);report['images'].append({'name':im.name,'path':im.filepath,'resolved_path':p,'exists':pathlib.Path(p).exists(),'packed':bool(im.packed_file),'source':im.source,'size':list(im.size),'colorspace':im.colorspace_settings.name,'library':im.library.filepath if im.library else None,'users':im.users})
for f in bpy.data.fonts:report['fonts'].append({'name':f.name,'path':f.filepath,'resolved_path':bpy.path.abspath(f.filepath),'packed':bool(f.packed_file),'exists':pathlib.Path(bpy.path.abspath(f.filepath)).exists()})
for l in bpy.data.libraries:report['libraries'].append({'path':l.filepath,'resolved':bpy.path.abspath(l.filepath),'exists':pathlib.Path(bpy.path.abspath(l.filepath)).exists()})
for o in local:
    target=o.get('support_target')
    if not target:continue
    if target not in trees:report['support_rays'].append({'object':o.name,'target':target,'error':'target has no evaluated surface'});continue
    direction=Vector(o.get('support_direction',(0,0,-1))).normalized()
    anchors=[c for c in o.children_recursive if c.type=='EMPTY' and (c.get('contact_anchor') or c.get('support_anchor')) and c.parent==o]
    if anchors:
        points=[(a.name,a.matrix_world.translation.copy()) for a in anchors]
    elif o.type=='MESH':
        vs=vertices.get(o.name,[]);lowest=min((v.dot(-direction) for v in vs),default=0);points=[('extreme_'+str(i),v) for i,v in enumerate(vs) if abs(v.dot(-direction)-lowest)<1e-5][:12]
    else:points=[]
    for name,p in points:
        origin=p-direction*.025;hit=trees[target].ray_cast(origin,direction,1.)
        r={'object':o.name,'anchor':name,'target':target,'point':list(p),'direction':list(direction),'hit':hit[0] is not None}
        if hit[0] is not None:r.update(gap_m=hit[3]-.025,normal=list(hit[1]),angle_degrees=math.degrees(math.acos(max(-1,min(1,hit[1].dot(-direction))))))
        report['support_rays'].append(r)
report['counters']={'local_objects':len(local),'local_meshes':len(vertices),'evaluated_triangles':tri,'material_submeshes':sub,'local_materials':len(report['materials']),'scene_render_resolution':[bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y,bpy.context.scene.render.resolution_percentage],'engine':bpy.context.scene.render.engine}
report['registration']={'registered_assemblies':json.loads(bpy.context.scene.get('contact_assemblies','[]')),'unclassified_geometry':[o.name for o in local if o.type in {'MESH','CURVE','FONT'} and not o.get('support_class')],'orphan_components':[o.name for o in local if o.get('support_class')=='assembly_component' and not bpy.data.objects.get(o.get('assembly',''))]}
report['manifest_ink_vertices']={}
if 'Counter manifest paper' in trees:
    for name in ['Manifest header','Manifest line 1','Manifest line 2','Manifest line 3']:
        gaps=[];missing=0
        for v in vertices.get(name,[]):
            hit=trees['Counter manifest paper'].ray_cast(Vector((v.x,v.y,1.1)),Vector((0,0,-1)),.1)[0]
            if hit is None:missing+=1
            else:gaps.append(v.z-hit.z)
        report['manifest_ink_vertices'][name]={'vertices':len(vertices.get(name,[])),'missing_sheet_rays':missing,'minimum_gap_m':min(gaps) if gaps else None,'maximum_gap_m':max(gaps) if gaps else None,'buried_vertices':sum(g<-.000001 for g in gaps)}
report['machine_bearing_samples']=[]
def bearing_ray(label,support,point,direction,start_offset=.02,max_distance=.1):
    p=Vector(point);di=Vector(direction);hit=trees[support].ray_cast(p-di*start_offset,di,max_distance) if support in trees else (None,None,None,None)
    r={'label':label,'support':support,'point':point,'direction':direction,'hit':hit[0] is not None}
    if hit[0] is not None:r['gap_m']=hit[3]-start_offset;r['hit_point']=list(hit[0])
    report['machine_bearing_samples'].append(r)
for y in [9.04,9.36]:bearing_ray('drive_motor_plate_from_body','Drive motor mounting plate',(5.68,y,.535),(0,0,-1))
for x,y in [(4.05,6.65),(4.05,8.65),(5.25,6.65),(5.25,8.65)]:
    bearing_ray('forged_eye_stem_on_shield_roof','Lead tunnel main body',(x,y,2.15),(0,0,-1))
    bearing_ray('forged_eye_ring_on_stem',f'Lifting eyebolt stem {x}_{y}',(x,y,2.161),(0,0,-1))
for side in [-1,1]:
    for j in range(6):bearing_ray('optical_lens_to_mount', 'CD | Joined Person Scanner Arch / steel',(.62*side,7,.4+.36*j),(side,0,0),.02,.08)
for y in [6.4,8.9]:
    bearing_ray('return_idler_top_to_belt','Conveyor return belt',(4.65,y,.412),(0,0,1),.02,.08)
report['joined_connected_components']=[]
for name in ['CD | Joined Cargo Inspection Conveyor / steel','CD | Joined Cargo Inspection Conveyor / charcoal','CD | Joined Arrival Gate P2 / steel','CD | Joined P2 blast leaf west / steel','CD | Joined P2 blast leaf east / steel']:
    if name not in vertices:continue
    vs=vertices[name];adj=defaultdict(set)
    for f in faces[name]:
        for a,b in zip(f,f[1:]+f[:1]):adj[a].add(b);adj[b].add(a)
    unseen=set(range(len(vs)));components=[]
    while unseen:
        seed=next(iter(unseen));todo=[seed];ids=set()
        while todo:
            x=todo.pop()
            if x in ids:continue
            ids.add(x);todo.extend(adj[x]-ids)
        unseen-=ids;components.append({'vertex_count':len(ids),'bounds':bounds([vs[x] for x in ids]),'centroid':[sum(vs[x][i] for x in ids)/len(ids) for i in range(3)]})
    report['joined_connected_components'].append({'name':name,'components':components})
def tri_box(a,b,c,lo,hi):
    centre=(lo+hi)*.5; half=(hi-lo)*.5; vv=[a-centre,b-centre,c-centre];ee=[vv[1]-vv[0],vv[2]-vv[1],vv[0]-vv[2]]
    axes=[Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)),ee[0].cross(ee[1])]
    axes += [e.cross(u) for e in ee for u in axes[:3]]
    for axis in axes:
        if axis.length_squared<1e-18:continue
        pp=[v.dot(axis) for v in vv];r=sum(abs(axis[i])*half[i] for i in range(3))
        if min(pp)>r+1e-7 or max(pp)<-r-1e-7:return False
    return True
reservations={
 'R1_human_straight':((-.6,.28,.035),(.6,15.4,2.25)),
 'R2_cart_straight':((1.275,3.2,.035),(2.625,12.2,2.6)),
 'R3_office_straight':((-5.925,3.7,.035),(-4.875,9.5,2.2)),
 'support_screen_north_return':((-2.55,14.25,.035),(-2.25,15.76,2.6)),
 'P1_aperture':((-1.2,-.15,.035),(1.2,.15,2.6)),
 'P2_aperture':((-2.3,15.66,.035),(2.3,15.94,3.5))}
report['route_triangle_reservations']={}
for label,(low,high) in reservations.items():
    lo=Vector(low);hi=Vector(high);hits=[]
    for name,vs in vertices.items():
        ob=bpy.data.objects[name]
        if ob.hide_render:continue
        bb=bounds(vs)
        if any(bb['max'][i]<lo[i] or bb['min'][i]>hi[i] for i in range(3)):continue
        count=0
        for face in faces[name]:
            for j in range(1,len(face)-1):
                if tri_box(vs[face[0]],vs[face[j]],vs[face[j+1]],lo,hi):count+=1
        if count:hits.append({'name':name,'triangles_intersecting':count,'bounds':bb,'circulation_solid_metadata':clean(ob.get('circulation_solid'))})
    report['route_triangle_reservations'][label]={'bounds':{'min':low,'max':high},'intersections':hits,'meaning':'actual authored state; closed portal leaves intentionally remain included; route runtime state changes unverified'}
(OUT/'native-probe.json').write_text(json.dumps(report,indent=2))
print('INDEPENDENT_PROBE_DONE',json.dumps(report['counters']),flush=True)
