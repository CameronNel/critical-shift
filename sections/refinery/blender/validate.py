"""Blender geometric QA. This is neither physics nor final art acceptance."""
import json, math
from pathlib import Path
from collections import Counter
import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
import config
import support_contacts as contacts

EPS=0.002
ROUTE=((-3.35,-.6,.08),(3.7,1.6,2.15))


def geom(obj,dg):
    e=obj.evaluated_get(dg);m=e.to_mesh()
    try:
        m.calc_loop_triangles()
        vs=[e.matrix_world@v.co for v in m.vertices]
        fs=[tuple(t.vertices) for t in m.loop_triangles]
        return vs,fs
    finally:e.to_mesh_clear()


def bounds(v):
    return tuple(min(p[i] for p in v) for i in range(3)),tuple(max(p[i] for p in v) for i in range(3))


def overlap(a,b):
    return all(a[0][i]<b[1][i]-1e-7 and a[1][i]>b[0][i]+1e-7 for i in range(3))


def inside(p,bb):
    return all(bb[0][i]+1e-7<p[i]<bb[1][i]-1e-7 for i in range(3))


def boxgeom(bb):
    lo,hi=bb
    v=[Vector((x,y,z)) for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]]
    f=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
    return v,f


def bvh(v,f):return BVHTree.FromPolygons(v,f,all_triangles=all(len(a)==3 for a in f),epsilon=0)


def run(output_path=None,check_saved=False):
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    report={'status':'PENDING','errors':[],'warnings':[], 'statistics':{}, 'support_contacts':[],
      'scope':'Automated Blender scene geometry and metadata checks; not final visual acceptance or Unity physics/navigation/networking validation.',
      'tolerances':{'contact_gap_m':.005,'contact_penetration_m':.002,'route_box_m':ROUTE,'cart_floor_penetration_m':EPS,'cart_sweep_step_deg':1},
      'limitations':['BVH overlap checks triangle surfaces, supplemented by vertex containment for route checks; complete solid containment in cart obstacles is not a physics simulation.',
        'Open sheet meshes have no signed-volume orientation test. Closed-mesh signed volume detects global reversal, not every local flipped face.',
        'Control approach floor rays establish a standing surface only; reaching pose, occlusion and full character controller clearance require runtime checks.',
        'Transfer markers are checked against authored guide geometry when declared; ore dynamics and collision response are not simulated.']}
    errors=report['errors'];warnings=report['warnings']
    meshes=[o for o in bpy.context.scene.objects if o.type in {'MESH','CURVE','FONT'} and not o.hide_render]
    cache={};degenerate=[];closed=0;open_meshes=0
    for o in meshes:
        try:v,f=geom(o,dg)
        except Exception as exc:errors.append('Cannot evaluate '+o.name+': '+str(exc));continue
        if not v or not f:continue
        if not all(math.isfinite(c) for p in v for c in p):errors.append('Nonfinite mesh '+o.name);continue
        cache[o.name]=(v,f,bounds(v),bvh(v,f))
        if not len(o.data.materials) or any(m is None for m in o.data.materials):errors.append('Missing material '+o.name)
        zero=sum((v[b]-v[a]).cross(v[c]-v[a]).length<1e-12 for a,b,c in f)
        if zero:degenerate.append({'object':o.name,'zero_area_triangles':zero})
        edges=Counter(tuple(sorted((a,b))) for tri in f for a,b in zip(tri,tri[1:]+tri[:1]))
        if edges and all(n==2 for n in edges.values()):
            closed+=1
            center=sum(v,Vector())/len(v)
            volume=sum((v[a]-center).dot((v[b]-center).cross(v[c]-center))/6 for a,b,c in f)
            if volume < -1e-9:errors.append('Closed mesh has inward signed volume: '+o.name)
        else:open_meshes+=1
    if degenerate:warnings.append({'zero_area_triangle_objects':degenerate})
    for im in bpy.data.images:
        if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).is_file():errors.append('Missing external image '+im.name)
    if bpy.data.libraries:errors.append('Linked libraries remain: '+', '.join(l.filepath for l in bpy.data.libraries))
    for machine in config.MACHINES:
        roots=[o for o in bpy.context.scene.objects if o.get('machine_id')==machine and o.name=='ROOT_'+machine]
        if len(roots)!=1:errors.append('Expected one ROOT_'+machine)
    for name in config.CAMERAS:
        o=bpy.data.objects.get(name)
        if o is None or o.type!='CAMERA':errors.append('Missing camera '+name)
    floor=cache.get('Floor');ceiling=cache.get('Ceiling')
    if floor is None or ceiling is None:errors.append('Missing Floor/Ceiling mesh')
    else:
        fb=floor[2];cb=ceiling[2]
        dims=[fb[1][0]-fb[0][0],fb[1][1]-fb[0][1],cb[0][2]-fb[1][2]]
        report['room_dimensions_m']=dims
        if any(abs(a-b)>.015 for a,b in zip(dims,config.ROOM)):errors.append('Room dimensions disagree with 14x12x4.8m')
    required=contacts.get_collection_objects(contacts.REQUIRED_COLLECTION)
    candidate=set().union(*(contacts.get_collection_objects(n) for n in contacts.CANDIDATE_COLLECTIONS))
    candidate.update(o for o in bpy.context.scene.objects if o.get('support_dependent'))
    for o in candidate-required:errors.append('Unregistered support-dependent object '+o.name)
    target_bvhs={}
    for o in sorted(required,key=lambda a:a.name):
        result=contacts.validate_object(o,target_bvhs,dg);report['support_contacts'].append(result)
        if result['status']!='PASS':errors.append('Support contact failure: '+o.name)
    required_markers=getattr(config,'REQUIRED_MARKERS',[])
    control_roles={'CRUSHER':['START','STOP','REVERSE','SPEED','EMERGENCY_RELEASE','SAFETY_BYPASS'],
                   'SORTER':['BELT_SPEED','DIVERTER','RECALIBRATION','MANUAL_OVERRIDE'],
                   'PROCESSOR':['PRESSURE','TEMPERATURE','EMERGENCY_DUMP','SEAL_REPAIR','SERVICE_ACCESS'],
                   'DRYER':['INCREASE_HEAT','MOISTURE_CHECK','FILTER_BYPASS','FILTER_REPAIR'],
                   'ASSEMBLY':['PRESS','HIGH_SPEED','ALIGNMENT','SEAL_STAGE','STOP'],
                   'INSPECTION':['APPROVE','REJECT','REPROCESS','BLEND','FALSIFY','SEND_UNINSPECTED'],
                   'DISPATCH':['REACTOR_ROUTE','BRAKE']}
    for machine,roles in control_roles.items():
        for role in roles:
            if bpy.data.objects.get('INT_'+machine+'_'+role) is None:errors.append('Missing required control INT_'+machine+'_'+role)
    if not any(bpy.data.objects.get('INT_SORTER_'+role) for role in ['SCANNER_SENSITIVITY','SENSITIVITY']):errors.append('Missing sorter scanner sensitivity control')
    for name in required_markers:
        if bpy.data.objects.get(name) is None:errors.append('Missing required marker '+name)
    if not required_markers:warnings.append('No config.REQUIRED_MARKERS list supplied; enforcing INPUT/OUTPUT per machine and recording controls.')
    for machine in config.MACHINES:
        for role in ['INPUT','OUTPUT']:
            if bpy.data.objects.get('INT_'+machine+'_'+role) is None:errors.append('Missing interface INT_'+machine+'_'+role)
    controls=[]
    for o in bpy.context.scene.objects:
        if o.get('kind')!='control':continue
        p=o.matrix_world.translation
        entry={'name':o.name,'position':list(p),'floor_approach':False}
        if not .75<=p.z<=1.65:errors.append('Unreachable control height '+o.name)
        if floor:
            approach=Vector((p.x,p.y-.45,.3));hit=floor[3].ray_cast(approach,Vector((0,0,-1)),.6)
            entry['floor_approach']=hit[0] is not None
            if not entry['floor_approach']:errors.append('No floor below control approach '+o.name)
        controls.append(entry)
    report['controls']=controls
    rv,rf=boxgeom(ROUTE);rb=bvh(rv,rf);route_hits=[]
    for name,(v,f,bb,tree) in cache.items():
        if overlap(bb,ROUTE) and (any(inside(p,ROUTE) for p in v) or tree.overlap(rb)):
            route_hits.append(name)
    report['route']={'reserved_bbox':ROUTE,'intersections':route_hits}
    if route_hits:errors.append('Reserved route blocked: '+', '.join(route_hits))
    # Door passages are measured against real geometry, not just metadata.
    doors=[]
    for name,center,width,height,axis in [('MINE',(-7,-3.65),2.4,2.2,0),('REACTOR',(7,-3.65),2.4,2.2,0),('ENTRY',(-1.8,-6),2.2,2.2,1)]:
        hits=[]
        for u in range(13):
            offset=-width/2+.01+(width-.02)*u/12
            for j in range(8):
                z=.18+(height-.18)*j/7
                start=Vector((center[0]-.32,center[1]+offset,z)) if axis==0 else Vector((center[0]+offset,center[1]-.32,z))
                direction=Vector((1,0,0)) if axis==0 else Vector((0,1,0))
                for objname,(_,_,bb,tree) in cache.items():
                    if bb[0][axis] > center[axis]+.32 or bb[1][axis] < center[axis]-.32:continue
                    hit=tree.ray_cast(start,direction,.64)
                    if hit[0] is not None:hits.append(objname)
        rec={'door':name,'sampled_width_m':width,'sampled_height_m':height,'rays':104,'obstructions':sorted(set(hits))};doors.append(rec)
        if hits:errors.append('Door clearance obstruction '+name+': '+', '.join(sorted(set(hits))))
    report['doorway_clearance']=doors
    floor_penetrations=[]
    for name,(_,_,bb,_) in cache.items():
        if name=='Floor' or 'external_sill' in name:continue
        if bb[0][2]<-.005 and bb[1][0]>-7 and bb[0][0]<7 and bb[1][1]>-6 and bb[0][1]<6:
            floor_penetrations.append({'object':name,'min_z':bb[0][2]})
    report['unintended_floor_penetrations']=floor_penetrations
    if floor_penetrations:errors.append('Geometry penetrates floor: '+', '.join(x['object'] for x in floor_penetrations))
    hidden=[o.name for o in bpy.context.scene.objects if o.type in {'MESH','CURVE','FONT'} and o.hide_render and not o.get('intentional_hidden')]
    report['unexplained_hidden_geometry']=hidden
    if hidden:errors.append('Unexplained hidden geometry: '+', '.join(hidden))
    pivot=bpy.data.objects.get('CART_SIDE_TIP_PIVOT');cart=bpy.data.objects.get('AUTHENTIC_GULLET_CART')
    report['cart_sweep']={}
    if pivot is None or cart is None:errors.append('Missing cart pivot or authentic root')
    else:
        descendants=set(pivot.children_recursive);moving=[o for o in descendants if o.name in cache]
        static={o.name:cache[o.name] for o in bpy.context.scene.objects if o.name in cache and o not in descendants and (o.get('collision_role') in {'cart_obstacle','architecture'} or o.name.lower().startswith('wall'))}
        initial=pivot.matrix_world.copy();angle=pivot.rotation_euler.copy();collisions=[];mins=Vector((1e9,1e9,1e9));maxs=-mins
        # Saved evaluated vertices transformed rigidly around the authored pivot.
        try:
            for degree in range(51):
                rot=Matrix.Translation(initial.translation)@Matrix.Rotation(math.radians(-degree),4,'X')@Matrix.Translation(-initial.translation)
                for o in moving:
                    v,f,bb,_=cache[o.name];vv=[rot@p for p in v];bb=bounds(vv)
                    for k in range(3):mins[k]=min(mins[k],bb[0][k]);maxs[k]=max(maxs[k],bb[1][k])
                    if bb[0][2]<-EPS:collisions.append({'degree':degree,'moving':o.name,'obstacle':'floor','min_z':bb[0][2]})
                    moving_tree=None
                    for name,(_,_,sb,st) in static.items():
                        if overlap(bb,sb):
                            if moving_tree is None:moving_tree=bvh(vv,f)
                            if moving_tree.overlap(st):collisions.append({'degree':degree,'moving':o.name,'obstacle':name})
            lip=Matrix.Translation(initial.translation)@Matrix.Rotation(math.radians(-50),4,'X')@Matrix.Translation(-initial.translation)@Vector((-5.15,-2.86,1.44))
            lip_inside=(-6.2<lip.x<-4.1 and -2.375<lip.y<-.825 and lip.z-.65>.05)
            report['cart_sweep']={'angles':51,'moving_objects':len(moving),'aabb':[list(mins),list(maxs)],'collisions':collisions,'lip_at_50deg':list(lip),'lip_inside_hopper':lip_inside,'vertical_drop_m':lip.z-.65}
            if collisions:errors.append('Cart tip sweep collisions: '+str(len(collisions)))
            if not lip_inside:errors.append('Discharge lip misses receiving hopper')
        finally:pivot.rotation_euler=angle
        approach_hits=[]
        walls={n:c for n,c in cache.items() if bpy.data.objects[n].get('collision_role')=='architecture' or n.startswith(('MINE_door','MINE_hazard','MINE_slide')) or n.lower().startswith('wall')}
        for step in range(30):
            dx=-2.85+2.85*step/29
            for o in cart.children_recursive:
                if o.name not in cache:continue
                v,f,_,_=cache[o.name];vv=[p+Vector((dx,0,0)) for p in v];bb=bounds(vv)
                for name,(_,_,wb,wt) in walls.items():
                    if overlap(bb,wb) and bvh(vv,f).overlap(wt):approach_hits.append({'step':step,'cart_part':o.name,'wall':name})
        report['cart_approach']={'start_root':[-8,-3.65,.02],'end_root':[-5.15,-3.65,.02],'samples':30,'wall_collisions':approach_hits}
        if approach_hits:errors.append('Cart approach wall collisions: '+str(len(approach_hits)))
    transfers=[]
    for a,b in zip(config.MACHINES,config.MACHINES[1:]):
        out=bpy.data.objects.get('INT_'+a+'_OUTPUT');inp=bpy.data.objects.get('INT_'+b+'_INPUT')
        if out and inp:
            gap=(out.matrix_world.translation-inp.matrix_world.translation).length
            rec={'from':out.name,'to':inp.name,'from_position':list(out.matrix_world.translation),'to_position':list(inp.matrix_world.translation),'marker_gap_m':gap,'mode':'carry or intermediate authored processing; no conveyor assumed'}
            if (a,b) in [('RECEIVING','FEEDER'),('FEEDER','CRUSHER'),('CRUSHER','SORTER')]:
                rec['mode']='mechanized coincident interfaces';rec['max_marker_gap_m']=.02
                if gap>.02:errors.append('Mechanized interface marker gap '+a+' to '+b)
                candidates=[]
                for machine in [a,b]:
                    root=bpy.data.objects.get('ROOT_'+machine)
                    if root:candidates.extend(o.name for o in root.children_recursive if o.name in cache)
                near=[]
                for name in set(candidates):
                    hit=cache[name][3].find_nearest(out.matrix_world.translation,.20)
                    if hit[0] is not None:near.append({'geometry':name,'distance_m':hit[3]})
                rec['interface_geometry_within_20cm']=sorted(near,key=lambda h:h['distance_m'])[:8]
                if not near:errors.append('No physical geometry within .20m of mechanized interface '+a+' to '+b)
                rec['verification_boundary']='Matching interface coordinates and nearest physical surfaces; not a simulated ore traversal.'
            transfers.append(rec)
    report['transfers']=transfers
    declared_paths=[]
    for o in bpy.context.scene.objects:
        if not o.get('transfer_from') or o.name not in cache:continue
        source=bpy.data.objects.get('INT_'+o['transfer_from']+'_OUTPUT')
        destination=bpy.data.objects.get('INT_'+o.get('transfer_to','')+'_INPUT')
        rec={'geometry':o.name,'from_machine':o['transfer_from'],'to_machine':o.get('transfer_to'),
             'world_bounds':cache[o.name][2],'endpoint_surface_tolerance_m':.20,'endpoint_results':[]}
        for marker in [source,destination]:
            if marker:
                nearest=cache[o.name][3].find_nearest(marker.matrix_world.translation)
                dist=nearest[3] if nearest[0] is not None else None
                rec['endpoint_results'].append({'marker':marker.name,'distance_m':dist})
                if dist is None or dist>.20:errors.append('Declared transfer geometry misses endpoint '+o.name+' / '+marker.name)
        declared_paths.append(rec)
    report['declared_transfer_geometry']=declared_paths
    report['feeder_expected']={'start':[-5.15,-1.25,.32],'end':[-5.15,4.2,2.78],'length_m':math.sqrt(5.45**2+2.46**2),'reason_for_head_height':'Return belt clears crusher bearing cheeks; no upstairs manual loading.'}
    if check_saved and Path(bpy.data.filepath).resolve()!=Path(config.BLEND).resolve():errors.append('Saved file path is not config.BLEND')
    report['statistics']={'scene_objects':len(bpy.context.scene.objects),'evaluated_geometry_objects':len(cache),'closed_meshes_volume_checked':closed,'open_meshes':open_meshes,'support_objects':len(required),'control_markers':len(controls),'errors':len(errors),'warnings':len(warnings)}
    report['status']='FAIL' if errors else 'PASS'
    path=Path(output_path) if output_path else config.PRODUCTION/'validation_report.json'
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('REFINERY_VALIDATION',report['status'],len(errors),'errors:',str(path))
    if errors:raise RuntimeError('Refinery validation failed: '+'; '.join(errors[:15]))
    return report
