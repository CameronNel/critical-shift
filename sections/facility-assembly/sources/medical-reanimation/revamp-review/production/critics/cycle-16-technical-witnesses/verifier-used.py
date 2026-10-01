"""Objective checks on the isolated art overhaul; no scene or map mutation."""
import bpy, bmesh, json, hashlib, math, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent
P=ROOT/'revamp-review/production'
source_before=hashlib.sha256((ROOT/'module_overhaul_R2.blend').read_bytes()).hexdigest()
if '--cold' in sys.argv:
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'module_overhaul_R2.blend'),load_ui=False)
else:
    with bpy.data.libraries.load(str(ROOT/'module_overhaul_R2.blend'),link=False) as (a,b):b.scenes=['REANIMATION_EDIT_LOCAL']
s=bpy.data.scenes['REANIMATION_EDIT_LOCAL'];bpy.context.window.scene=s;bpy.context.view_layer.update()
baseline=json.loads((ROOT/'revamp-review/baseline.json').read_text())
inherited_names={rec['name'] for rec in baseline['objects']}
pose_updates=set(json.loads((P/'build-state.json').read_text()).get('intentional_prop_pose_updates',[]))
errors=[];checks={};deps=bpy.context.evaluated_depsgraph_get()
for rec in baseline['objects']:
    o=s.objects.get(rec['name'])
    if not o:errors.append('Missing inherited object: '+rec['name']);continue
    if o.name not in pose_updates and rec['type']!='LIGHT' and max(abs(o.matrix_world[i][j]-rec['matrix_world'][i][j]) for i in range(4) for j in range(4))>1e-6:errors.append('Moved inherited object: '+o.name)
    if max(abs(o.dimensions[i]-rec['dimensions'][i]) for i in range(3))>1e-6:errors.append('Resized inherited object: '+o.name)
checks['inherited_layout_objects']=len(baseline['objects'])
checks['intentional_small_dressing_pose_updates']=sorted(pose_updates)
for path,expected in baseline['protected_sha256'].items():
    if hashlib.sha256((ROOT.parents[1]/path).read_bytes()).hexdigest()!=expected:errors.append('Changed protected file: '+path)
checks['protected_files_unchanged']=not any('protected' in e for e in errors)
spawn_path=ROOT.parent/'spawn-room/module.blend'
spawn_expected=json.loads((P/'build-state.json').read_text()).get('approved_spawn_source_sha256')
checks['approved_spawn_unchanged']=hashlib.sha256(spawn_path.read_bytes()).hexdigest()==spawn_expected
if not checks['approved_spawn_unchanged']:errors.append('Changed approved spawn source')
lights=[o for o in s.objects if o.type=='LIGHT' and o.data.energy>0]
red=[o for o in lights if o.data.color[0]>o.data.color[1]*3 and o.data.color[0]>o.data.color[2]*3]
warm=[o for o in lights if o.data.type=='AREA' and o.data.color[0]>o.data.color[2]*1.5 and o not in red]
spots=[o for o in lights if o.data.type=='SPOT']
checks['lighting']={'active':len(lights),'red':len(red),'warm_practicals':len(warm),'directional_accents':len(spots)}
if (len(lights),len(red),len(warm),len(spots))!=(4,1,1,2):errors.append('Lighting count does not match user contract')
registry=json.loads((P/'support-registry.json').read_text());reports=[]
for rec in registry:
    o=s.objects.get(rec['object']);t=s.objects.get(rec['target'])
    if not o or not t:errors.append('Missing support pair: '+str(rec));continue
    ev=t.evaluated_get(deps);tm=ev.to_mesh();verts=[t.matrix_world@v.co for v in tm.vertices]
    tree=BVHTree.FromPolygons(verts,[tuple(f.vertices) for f in tm.polygons],all_triangles=False)
    anchor_reports=[]
    if not rec.get('anchors'):errors.append('Missing declared contact anchors: '+o.name)
    for a in rec.get('anchors',[]):
        point=o.matrix_world@Vector(a['local_point']);direction=Vector(a['approach_world']).normalized()
        start=point-direction*.01
        surface,normal,index,distance=tree.ray_cast(start,direction,.018)
        if surface is None:
            anchor_reports.append({'status':'FAIL','reason':'No surface in declared approach direction'});continue
        signed=.01-distance
        # Signed gap is positive outside the support, negative for penetration.
        signed=-signed
        angle=math.degrees(normal.angle(Vector(a['expected_surface_normal_world'])))
        passed=signed<=rec['max_gap_m']+1e-7 and signed>=-rec['max_penetration_m']-1e-7 and angle<=rec['max_angle_degrees']
        # The attachment witness must still lie on the actual authored object.
        obj=o.evaluated_get(deps);om=obj.to_mesh()
        otree=BVHTree.FromPolygons([o.matrix_world@v.co for v in om.vertices],[tuple(p.vertices) for p in om.polygons])
        witness_distance=otree.find_nearest(point)[3]
        obj.to_mesh_clear()
        if witness_distance>.0011:passed=False
        anchor_reports.append({'signed_gap_m':signed,'angle_degrees':angle,'object_witness_distance_m':witness_distance,'contact_anchor':list(point),'surface_anchor':list(surface),'status':'PASS' if passed else 'FAIL'})
    passed=bool(anchor_reports) and all(a['status']=='PASS' for a in anchor_reports)
    report={**rec,'anchor_results':anchor_reports,'status':'PASS' if passed else 'FAIL'}
    reports.append(report)
    if not passed:errors.append('Support contact: '+o.name+' / '+str(anchor_reports))
    ev.to_mesh_clear()
registered={r['object'] for r in registry}
unregistered=[o.name for o in s.objects if o.name.startswith('MED_R2 |') and o.type=='MESH' and o.name not in registered]
if unregistered:errors.append('Unregistered support-dependent art: '+str(unregistered))
checks['support_contact']={'registered':len(registry),'passed':sum(r['status']=='PASS' for r in reports),'unregistered':unregistered}
checks['support_contact']['anchors_checked']=sum(len(r.get('anchor_results',[])) for r in reports)
registered_paths={}
for rec in registry:registered_paths.setdefault(rec['object'],[]).append(rec['target'])
def object_supported(name,seen=()):
    if name in seen or not s.objects.get(name):return False
    if name in registered_paths:
        return all(object_supported(target,seen+(name,)) for target in registered_paths[name])
    return name in inherited_names
checks['support_contact']['terminal_rule']='Explicit retained mounts are traversed before unregistered inherited geometry. Architectural contact for unregistered inherited geometry requires the independent broad physical audit.'
for name in registered_paths:
    if not object_supported(name):errors.append('Cyclic or unrooted declared support path: '+name)
surface_contacts=[]
for o in s.objects:
    if o.type!='MESH' or not o.get('contact_check_surface_all_vertices'):continue
    target=s.objects[o['support_target']];ev=target.evaluated_get(deps);tm=ev.to_mesh()
    tree=BVHTree.FromPolygons([target.matrix_world@v.co for v in tm.vertices],[tuple(p.vertices) for p in tm.polygons])
    obj=o.evaluated_get(deps);om=obj.to_mesh();signed=[]
    for vertex in om.vertices:
        point=o.matrix_world@vertex.co;surface,normal,index,distance=tree.find_nearest(point)
        signed.append((point-surface).dot(normal))
    outside=sum(gap>.005+1e-7 for gap in signed);inside=sum(gap<-.002-1e-7 for gap in signed)
    record={'object':o.name,'target':target.name,'vertices_checked':len(signed),'maximum_gap_m':max(signed),'maximum_penetration_m':max(0,-min(signed)),'outside_gap_tolerance':outside,'outside_penetration_tolerance':inside,'status':'PASS' if not outside and not inside else 'FAIL'}
    surface_contacts.append(record)
    if outside or inside:errors.append('Sewn surface contact: '+str(record))
    obj.to_mesh_clear();ev.to_mesh_clear()
checks['sewn_surface_contact']=surface_contacts
component_contacts=[]
for o in s.objects:
    if o.type!='MESH' or not o.get('support_components'):continue
    obj=o.evaluated_get(deps);om=obj.to_mesh()
    for comp in json.loads(o['support_components']):
        parent_inverse=s.objects[comp['coordinate_parent']].matrix_world.inverted()
        selected=set()
        for poly in om.polygons:
            if om.materials[poly.material_index].name!=comp['material']:continue
            if all(comp.get('z_min',-math.inf)<=(parent_inverse@(o.matrix_world@om.vertices[i].co)).z<=comp.get('z_max',math.inf) for i in poly.vertices):selected.update(poly.vertices)
        target=s.objects[comp['target']];ev=target.evaluated_get(deps);tm=ev.to_mesh()
        tree=BVHTree.FromPolygons([target.matrix_world@v.co for v in tm.vertices],[tuple(p.vertices) for p in tm.polygons])
        signed=[]
        for i in selected:
            point=o.matrix_world@om.vertices[i].co;surface,normal,index,distance=tree.find_nearest(point);signed.append((point-surface).dot(normal))
        passed=bool(signed) and all(-.002-1e-7<=gap<=.005+1e-7 for gap in signed)
        record={'object':o.name,'component':comp['label'],'target':target.name,'vertices_checked':len(signed),'maximum_gap_m':max(signed) if signed else None,'maximum_penetration_m':max(0,-min(signed)) if signed else None,'status':'PASS' if passed else 'FAIL'}
        component_contacts.append(record)
        if not passed:errors.append('Component support contact: '+str(record))
        ev.to_mesh_clear()
    obj.to_mesh_clear()
checks['component_support_contact']=component_contacts
assembly_contacts=[]
for o in s.objects:
    if not o.get('assembly_contact_contracts'):continue
    obj=o.evaluated_get(deps);om=obj.to_mesh();ids=om.attributes.get('med_assembly_part')
    contracts=json.loads(o['assembly_contact_contracts']);by_id={rec['part_id']:rec for rec in contracts}
    def rooted(part,seen=()):
        if part in seen or part not in by_id:return False
        rec=by_id[part]
        return object_supported(rec.get('target_object')) if 'target_part_id' not in rec else rooted(rec['target_part_id'],seen+(part,))
    for comp in contracts:
        selected={v.index for v in om.vertices if ids and ids.data[v.index].value==comp['part_id']}
        if 'target_part_id' in comp:
            target=o;tm=om
            faces=[tuple(p.vertices) for p in tm.polygons if ids and all(ids.data[i].value==comp['target_part_id'] for i in p.vertices)]
        else:
            target=s.objects[comp['target_object']];ev=target.evaluated_get(deps);tm=ev.to_mesh();faces=[tuple(p.vertices) for p in tm.polygons]
        tree=BVHTree.FromPolygons([target.matrix_world@v.co for v in tm.vertices],faces)
        a=comp['anchor'];point=o.matrix_world@Vector(a['local_point']);direction=Vector(a['approach_world']).normalized()
        surface,normal,index,distance=tree.ray_cast(point-direction*.01,direction,.018)
        own_faces=[tuple(p.vertices) for p in om.polygons if all(i in selected for i in p.vertices)]
        own_tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in om.vertices],own_faces)
        witness=own_tree.find_nearest(point)[3] if own_faces else math.inf
        signed=distance-.01 if surface is not None else math.inf
        angle=math.degrees(normal.angle(Vector(a['expected_surface_normal_world']))) if normal is not None else math.inf
        passed=bool(selected) and rooted(comp['part_id']) and -.002-1e-7<=signed<=.005+1e-7 and angle<=12 and witness<=.0011
        record={'object':o.name,'part':comp['part_name'],'part_id':comp['part_id'],'target_object':target.name,'target_part_id':comp.get('target_part_id'),'part_vertices':len(selected),'signed_gap_m':signed,'normal_angle_degrees':angle,'part_witness_distance_m':witness,'support_path_reaches_declared_inherited_support':rooted(comp['part_id']),'status':'PASS' if passed else 'FAIL'}
        assembly_contacts.append(record)
        if not passed:errors.append('Assembly part contact: '+str(record))
        if target!=o:ev.to_mesh_clear()
    obj.to_mesh_clear()
checks['assembly_part_contact']=assembly_contacts
missing_physical_uv=[]
for o in s.objects:
    if o.type!='MESH':continue
    for mat in o.data.materials:
        if mat and mat.use_nodes and any(n.type=='UVMAP' and n.uv_map=='MED_Physical_1m' and n.outputs['UV'].is_linked for n in mat.node_tree.nodes) and not o.data.uv_layers.get('MED_Physical_1m'):
            missing_physical_uv.append({'object':o.name,'material':mat.name})
checks['material_users_missing_physical_uv']=missing_physical_uv
if missing_physical_uv:errors.append('Active material users lack named physical UV: '+str(missing_physical_uv))
normal_reports=[]
for o in s.objects:
    authored=o.name.startswith('MED_R2 |') or (o.type=='MESH' and o.data.name.startswith('MED | Skill revised')) or any(o.name.startswith(n) for n in ['Contoured head pad','Segmented adult berth cushion','Folded work glove palm','Folded work glove finger','Folded cleaning cloth','Recovery foam cushion','Recovery pillow','Cart segmented mattress','Receiver cast housing','Suit service enclosure','Formed end service panel'])
    if not authored or o.type!='MESH':continue
    ev=o.evaluated_get(deps);md=ev.to_mesh();bm=bmesh.new();bm.from_mesh(md)
    inconsistent=sum(len(e.link_loops)==2 and e.link_loops[0].vert==e.link_loops[1].vert for e in bm.edges)
    pending=set(bm.faces);negative=0;closed=0
    while pending:
        todo=[pending.pop()];island=set(todo)
        while todo:
            f=todo.pop()
            for e in f.edges:
                for neighbor in e.link_faces:
                    if neighbor in pending:pending.remove(neighbor);island.add(neighbor);todo.append(neighbor)
        if all(len(e.link_faces)==2 for f in island for e in f.edges):
            closed+=1;volume=0
            for f in island:
                v=[loop.vert.co for loop in f.loops]
                volume+=sum(v[0].dot(v[i].cross(v[i+1]))/6 for i in range(1,len(v)-1))
            if volume < -1e-10:negative+=1
    normal_reports.append({'object':o.name,'inconsistent_edges':inconsistent,'closed_components':closed,'negative_closed_components':negative})
    if inconsistent or negative:errors.append('Invalid surface winding: '+o.name)
    bm.free();ev.to_mesh_clear()
checks['normals']=normal_reports
guard=s.objects.get('MED_R2 | Transfer cart folded guards and pivot')
if guard and guard.parent!=s.objects['CART_LIFT_DECK']:errors.append('New cart deck guards do not follow lift deck')
for suffix in ('','.001'):
    face=s.objects.get('MED_R2 | Medical cabinet fabricated face '+suffix)
    if face and face.parent!=s.objects['Clear cabinet sliding pane'+suffix]:errors.append('Cabinet glazing does not follow sliding pane: '+face.name)
checks['cart_lift_guards_follow_deck']=guard is not None and guard.parent==s.objects['CART_LIFT_DECK']
checks['major_room_boundary']='Inherited floor, all walls, portals and utilities retain original transforms and dimensions'
checks['new_geometry_clearance']=[]
for o in s.objects:
    if not o.name.startswith('MED_R2 |') or o.type!='MESH':continue
    bb=[o.matrix_world@Vector(p) for p in o.bound_box]
    lo=[min(p[i] for p in bb) for i in range(3)];hi=[max(p[i] for p in bb) for i in range(3)]
    # Preserve the broad central evacuation lane, x -1.35 .. 2.45 m.
    in_lane=lo[0]<2.45 and hi[0]>-1.35 and lo[1]<8.0 and hi[1]>.18 and hi[2]>.05 and lo[2]<2.5
    if in_lane:errors.append('Added solid enters the reserved rescue lane: '+o.name)
    checks['new_geometry_clearance'].append({'object':o.name,'bounds':[lo,hi],'rescue_lane_clear':not in_lane})
missing=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]
if missing:errors.append('Missing image dependencies: '+str(missing))
if '--cold' in sys.argv:
    missing_libs=[lib.filepath for lib in bpy.data.libraries if not Path(bpy.path.abspath(lib.filepath)).exists()]
    map_scene=any(sc.library and Path(bpy.path.abspath(sc.library.filepath)).name=='facility_environment.blend' for sc in bpy.data.scenes)
    if missing_libs or not map_scene:errors.append('Missing linked map/dependencies: '+str(missing_libs))
    if s.library is not None:errors.append('Editable room scene is not local')
    checks['cold_open']={'linked_map':map_scene,'missing_libraries':missing_libs,'editable_room_local':s.library is None}
    if '--dependencies' in sys.argv:
        inventory={'schema_version':1,'source_sha256':source_before,'blender_version':bpy.app.version_string,'cold_open':True,'source_saved':False,'linked_libraries':[],'file_images':[],'unpacked_files':[],'missing_libraries':missing_libs,'missing_unpacked_images':[]}
        for lib in bpy.data.libraries:
            path=Path(bpy.path.abspath(lib.filepath)).resolve()
            inventory['linked_libraries'].append({'stored_path':lib.filepath,'absolute_path':str(path),'exists':path.is_file(),'parent_stored_path':lib.parent.filepath if lib.parent else None})
        for im in bpy.data.images:
            if im.source!='FILE':continue
            path=Path(bpy.path.abspath(im.filepath,library=im.library)).resolve() if im.filepath else None
            item={'name':im.name,'stored_path':im.filepath,'absolute_path':str(path) if path else None,'packed':bool(im.packed_file),'pixel_size':list(im.size),'valid_loaded_pixels':min(im.size)>0}
            inventory['file_images'].append(item)
            if not im.packed_file:
                if path and path.is_file() and min(im.size)>0:inventory['unpacked_files'].append({'absolute_path':str(path),'required_for_cold_open':True})
                else:inventory['missing_unpacked_images'].append(item)
        inventory['source_checksum_unchanged']=hashlib.sha256((ROOT/'module_overhaul_R2.blend').read_bytes()).hexdigest()==source_before
        (W/'dependency-manifest.json').write_text(json.dumps(inventory,indent=2)+'\n')
        if inventory['missing_unpacked_images']:errors.append('Unavailable cold-open file images')
elif '--dependencies' in sys.argv:
    raise RuntimeError('Dependency inventory requires --cold')
if hashlib.sha256((ROOT/'module_overhaul_R2.blend').read_bytes()).hexdigest()!=source_before:errors.append('Saved source changed during read-only verification')
result={'status':'PASS' if not errors else 'FAIL','checks':checks,'support_contacts':reports,'errors':errors,'source_sha256':hashlib.sha256((ROOT/'module_overhaul_R2.blend').read_bytes()).hexdigest()}
(W/('cold-verification.json' if '--cold' in sys.argv else 'objective-verification.json')).write_text(json.dumps(result,indent=2))
print('OVERHAUL_VERIFY',result['status'],checks['support_contact'],errors,flush=True)
if errors:raise RuntimeError('Overhaul objective validation failed')
