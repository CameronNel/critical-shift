"""Saved-file, interface, support and sampled-route checks; no scene mutation/save."""
import bpy,bmesh,json,sys,hashlib,argparse,math,os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--baseline',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);final=Path(bpy.data.filepath);out=Path(a.out).resolve();out.parent.mkdir(parents=True,exist_ok=True)
report={'source':str(final),'source_sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'failures':[],
 'scope':'Blender source checks, registered assembly support anchors and sampled 0.60 m route envelopes. Not exhaustive intersection/physics, Unity/navmesh or runtime performance certification.'}
def geom(o):
    data={'matrix':sum((list(r) for r in o.matrix_world),[]),'type':o.type}
    if o.type=='MESH':data['vertices']=[list(v.co) for v in o.data.vertices];data['polygons']=[list(p.vertices) for p in o.data.polygons]
    elif o.type=='CAMERA':data['lens']=o.data.lens
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
def worldbounds(o):
    vs=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [[min(p[i] for p in vs) for i in range(3)],[max(p[i] for p in vs) for i in range(3)]]
routes={'main':[(x,.50+j*.2) for x in [-.88,0,.88] for j in range(79)],
 'reserve':[(2+j*.2,13.2) for j in range(25)],'bench':[(-1.4-j*.15,13.9) for j in range(12)],
 'switchgear':[(-1.4-j*.15,4.0) for j in range(12)],'transfer':[(1.4+j*.15,10.3) for j in range(17)]}
bpy.ops.wm.open_mainfile(filepath=str(Path(a.baseline).resolve()),load_ui=False)
ref_dg=bpy.context.evaluated_depsgraph_get();baseline_floor={}
for pts in routes.values():
    for x,y in pts:
        hit,loc,*_=bpy.context.scene.ray_cast(ref_dg,Vector((x,y,.1)),Vector((0,0,-1)),distance=.25)
        baseline_floor[(x,y)]=loc.z if hit else None
baseline={o.name:geom(o) for o in bpy.context.scene.objects if ('Architecture' in [c.name for c in o.users_collection] and not o.name.startswith(('Precast horizontal reveal','Precast vertical reveal'))) or o.type=='CAMERA' or (o.type=='EMPTY' and o.name.startswith(('IF_','INTERACT_','HOOK_','NAV_','PLAYER_','INCIDENT_','AUDIO_')))}
door_finish={o.name:geom(o) for o in bpy.context.scene.objects
             if o.type=='MESH' and o.get('assembly_member') in {'D01_Turbine','D02_Waste'}
             and o.name.startswith(('Localized chipped paint','Wear at repeatedly handled edge'))}
remodel_bounds={o.name:worldbounds(o) for o in bpy.context.scene.objects if o.name.startswith(('Parked sliding leaf','Door recessed vision trim'))}
remodel_matrix={n:sum((list(r) for r in bpy.data.objects[n].matrix_world),[]) for n in remodel_bounds}
wire_baseline={o.name:{'world_vertices':[list(o.matrix_world@v.co) for v in o.data.vertices],
    'polygons':[list(p.vertices) for p in o.data.polygons],
    'matrix':sum((list(r) for r in o.matrix_world),[])} for o in bpy.context.scene.objects if o.name.startswith('Vision glass wire')}
bpy.ops.wm.open_mainfile(filepath=str(final),load_ui=False);scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
remodelled=[];embedded_wires=[];bad=[]
retired_finish=[]
declared_retirement=set()
if scene.get('electrical_door_history_revision'):
    declared_retirement=set(json.loads(scene.get('electrical_retired_door_wear','[]')))
    if (scene['electrical_door_history_revision']!='R6' or len(door_finish)!=104
            or declared_retirement!=set(door_finish)):
        report['failures'].append('door finish retirement differs from exact104 baseline decorative objects')
for n,sig in baseline.items():
    o=bpy.data.objects.get(n)
    if o and geom(o)==sig:continue
    if n in door_finish and n in declared_retirement and o is None:
        retired_finish.append({'object':n,'baseline_geometry_sha256':door_finish[n],
                               'reason':'Replaced duplicated decorative door wear with individual supported contact history'})
    elif o and n in remodel_bounds and o.get('electrical_remodelled'):
        current=worldbounds(o);error=max(abs(current[j][i]-remodel_bounds[n][j][i]) for i in range(3) for j in range(2))
        matrix_error=max(abs(v-w) for v,w in zip(sum((list(r) for r in o.matrix_world),[]),remodel_matrix[n]))
        remodelled.append({'object':n,'outer_bounds_error_m':error,'matrix_error':matrix_error,'pass':error<.0001 and matrix_error<.000001})
        if error>=.0001 or matrix_error>=.000001:bad.append(n)
    elif o and n in wire_baseline and o.get('electrical_embedded_wire'):
        ref=wire_baseline[n];pane=bpy.data.objects.get(o['electrical_embedded_wire'])
        sign=1 if sum(v[1] for v in ref['world_vertices'])/len(ref['world_vertices'])<1 else -1
        current=[list(o.matrix_world@v.co) for v in o.data.vertices]
        expected=[[v[0],v[1]-sign*.007,v[2]] for v in ref['world_vertices']]
        error=max(abs(a-b) for p,q in zip(current,expected) for a,b in zip(p,q)) if len(current)==len(expected) else 1e6
        matrix_error=max(abs(v-w) for v,w in zip(sum((list(r) for r in o.matrix_world),[]),ref['matrix']))
        topology_same=[list(p.vertices) for p in o.data.polygons]==ref['polygons']
        bounds=worldbounds(pane) if pane else None
        inside=bool(bounds) and all(bounds[0][axis]-.000001<=v[axis]<=bounds[1][axis]+.000001 for v in current for axis in range(3))
        passed=error<.000001 and matrix_error<.000001 and topology_same and inside
        embedded_wires.append({'object':n,'pane':pane.name if pane else None,'permitted_depth_shift_m':.007,
                               'other_geometry_error_m':error,'matrix_error':matrix_error,'topology_same':topology_same,'entirely_inside_glass':inside,'pass':passed})
        if not passed:bad.append(n)
    else:bad.append(n)
report['protected_geometry_and_cameras']={'checked':len(baseline),'changed':bad,
    'explicit_cosmetic_retirements':len(retired_finish),
    'geometry_checks_excluding_retired_cosmetic_wear':len(baseline)-len(retired_finish),'pass':not bad}
report['replaced_original_door_finish']=retired_finish
if declared_retirement and len(retired_finish)!=104:
    report['failures'].append('declared retired door-only wear still exists or lacks exact baseline identity')
report['remodelled_door_apertures']=remodelled
report['recessed_existing_vision_wires']=embedded_wires
report['failures']+=['protected:'+n for n in bad]
def bvh(o):
    e=o.evaluated_get(dg);me=e.to_mesh()
    try:return BVHTree.FromPolygons([e.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons],all_triangles=False)
    finally:e.to_mesh_clear()
cache={}
def tree(o):
    if o.name not in cache:cache[o.name]=bvh(o)
    return cache[o.name]
roots=[o for o in scene.objects if o.get('cs_support_required')]
members={r.name:[o for o in scene.objects if o.get('cs_assembly')==r.name and o.type=='MESH'] for r in roots}
unregistered=[o.name for o in scene.objects if o.name.startswith('EOH | ') and o.type in {'MESH','CURVE','FONT','LIGHT'} and not o.get('cs_assembly')]
report['failures']+=['unregistered:'+n for n in unregistered]
support=[]
axes={'WORLD_-Z':Vector((0,0,-1)),'WORLD_+Z':Vector((0,0,1)),'WORLD_-X':Vector((-1,0,0)),'WORLD_+X':Vector((1,0,0)),'WORLD_-Y':Vector((0,-1,0)),'WORLD_+Y':Vector((0,1,0))}
for r in roots:
    result={'assembly':r.name,'target':r.get('cs_support_target'),'samples':[],'failures':[]}
    target=bpy.data.objects.get(r.get('cs_support_target',''));direction=axes[r.get('cs_support_direction')]
    if not target or target.type!='MESH':result['failures'].append('missing target')
    else:
        for xyz in r['cs_support_anchors']:
            origin=Vector(xyz);hit,normal,idx,distance=tree(target).ray_cast(origin-direction*.012,direction,.05)
            nearest=[tree(o).find_nearest(origin)[3] for o in members[r.name]]
            member_distance=min(d for d in nearest if d is not None) if nearest else 1e6
            gap=(distance-.012) if hit is not None else None
            angle=math.degrees(normal.angle(-direction)) if normal else None
            passed=gap is not None and -.00201<=gap<=.00501 and angle<=12 and member_distance<=.00501
            result['samples'].append({'anchor':list(origin),'gap_m':gap,'support_angle_deg':angle,'assembly_surface_distance_m':member_distance,'pass':passed})
            if not passed:result['failures'].append('anchor:'+str(xyz))
    support.append(result)
    if result['failures']:report['failures'].append('support:'+r.name)
report['support']={'registered_assemblies':len(roots),'unregistered':unregistered,'results':support,'pass':all(not r['failures'] for r in support) and not unregistered}
missing=[]
for lib in bpy.data.libraries:
    if not Path(bpy.path.abspath(lib.filepath)).is_file():missing.append('library:'+lib.filepath)
for im in bpy.data.images:
    if im.users and im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath,library=im.library)).is_file():missing.append('image:'+im.name)
report['dependencies']={'missing':missing,'pass':not missing};report['failures']+=missing
tri=0;draws=0
for o in scene.objects:
    if o.type in {'MESH','CURVE','FONT'}:
        e=o.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);draws+=len(set(p.material_index for p in me.polygons));e.to_mesh_clear()
report['authoring_cost']={'triangles':tri,'estimated_material_submesh_draws':draws,'objects':len(scene.objects),'measured_engine_draw_calls':None,'budget_status':'No room overhaul budget supplied; record cost, do not invent a pass.'}
manufactured=[]
for o in scene.objects:
    if o.type!='MESH' or not (o.name.startswith('EOH | ') or o.get('electrical_remodelled')):continue
    bm=bmesh.new();bm.from_mesh(o.data)
    edges=sum(1 for e in bm.edges if not e.is_manifold)
    degenerate=sum(1 for f in bm.faces if f.calc_area()<1e-12)
    volume=bm.calc_volume(signed=True);bm.free()
    if edges or degenerate or volume<=0:manufactured.append({'object':o.name,'non_manifold_edges':edges,'degenerate_faces':degenerate,'signed_volume':volume})
report['manufactured_meshes']={'issues':manufactured,'pass':not manufactured}
report['failures']+=['manufactured:'+r['object'] for r in manufactured]
# Main aisle and approaches sampled using horizontal capsule perimeter rays and floor support.
route_results=[]
for name,pts in routes.items():
    defects=[]
    for x,y in pts:
        hit,loc,n,idx,obj,_=scene.ray_cast(dg,Vector((x,y,.1)),Vector((0,0,-1)),distance=.25)
        expected=baseline_floor[(x,y)]
        if not hit or expected is None or abs(loc.z-expected)>.003:
            defects.append({'xy':[x,y],'reason':'walking support differs from baseline','baseline_z':expected,'final_z':loc.z if hit else None})
        for z in [.3,1,1.68]:
            for i in range(8):
                angle=i*math.tau/8;d=Vector((math.cos(angle),math.sin(angle),0))
                hit,loc,n,idx,obj,_=scene.ray_cast(dg,Vector((x,y,z)),d,distance=.30)
                if hit:defects.append({'xy':[x,y],'z':z,'object':obj.name});break
    route_results.append({'route':name,'sampled_positions':len(pts),'defects':defects,'pass':not defects})
    if defects:report['failures'].append('route:'+name)
report['routes']=route_results
report['pass']=not report['failures'];out.write_text(json.dumps(report,indent=2));print('VALIDATION',report['pass'],report['failures'],flush=True)
sys.stdout.flush();sys.stderr.flush();os._exit(0 if report['pass'] else 1)
