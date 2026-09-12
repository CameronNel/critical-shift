"""Independent frozen eng05 branch audit. Read-only scene; CPU; no render/save."""
import bpy, json, math, hashlib, datetime, collections, time
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

START=time.time()
BASE=Path(__file__).resolve().parent
SNAP=BASE.parent/'checkpoints/eng05'
OUT=BASE/'astra-eng05-branch-evidence.json'
contract=json.loads((SNAP/'interface.json').read_text())
scene=bpy.context.scene
dg=bpy.context.evaluated_depsgraph_get()
def vec(v): return [round(float(x),7) for x in v]
def bounds(vs): return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
def chain(o):
    out=[]
    while o: out.append(o);o=o.parent
    return out
def descend(o): return [q for q in scene.objects if o in chain(q)[1:]]
def steps(lo,hi,pitch):
    n=max(1,math.ceil((hi-lo)/pitch));return [lo+(hi-lo)*i/n for i in range(n+1)]
def props(o):
    return {k:(v.to_list() if hasattr(v,'to_list') else v) for k,v in o.items() if k!='_RNA_UI'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
report={'schema':'astra-independent-eng05-branch/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blender':bpy.app.version_string,'opened_file':bpy.data.filepath,'blend_sha256':sha(SNAP/'Fuel_Corridor.blend'),'source_hashes':{p.name:sha(p) for p in SNAP.iterdir() if p.suffix in ['.json','.py']},'scene':{k:scene.get(k) for k in ['stage','revision','source_sha256','section']},'method':'Independent evaluated meshes and BVH rays. No checkpoint validator import. No scene save, render, neighbor import, or carriage movement. Counterfactual branch leaf exclusion is a filter only, not proof of stored open pose or motion.'}
roots={'F01_REFINERY':'REFINERY_BOUNDARY','F02_REACTOR':'REACTOR_BOUNDARY','S01_PLANT':'PLANT_PORT','S02_CLEAN':'CLEAN_PORT','S03_WASTE':'WASTE_PORT'}
ports=[]
for port in contract['ports']:
    p=dict(port);p['root']=roots[p['id']];p['c']=Vector(p['center']);p['n']=Vector(p['outward']);p['t']=Vector((-p['n'].y,p['n'].x,0));ports.append(p)
def local(v,p):
    d=v-p['c'];return Vector((d.dot(p['t']),d.dot(p['n']),v.z))
def world(u,d,z,p): return p['c']+p['t']*u+p['n']*d+Vector((0,0,z))
geoms={}
print('AUDIT evaluating',len(scene.objects),'objects',flush=True)
for o in scene.objects:
    if o.type not in {'MESH','CURVE','FONT','SURFACE'}:continue
    eo=o.evaluated_get(dg);mesh=eo.to_mesh()
    if not mesh:continue
    try:
        vs=[eo.matrix_world@v.co for v in mesh.vertices]
        if not vs:continue
        polygons=[tuple(q.vertices) for q in mesh.polygons]
        b=bounds(vs);lineage=chain(o)
        g={'name':o.name,'obj':o,'vs':vs,'b':b,'polygons':polygons,'root':lineage[-1].name,'carriage':next((q.name for q in lineage if q.get('component_role')=='sliding_leaf_carriage'),None),'cap':bool(o.get('external_presentation_cap',False)),'decal':bool(o.get('surface_decal',False)),'type':o.type}
        geoms[o.name]=g
    finally:eo.to_mesh_clear()
report['geometry_count']=len(geoms)
report['object_count']=len(scene.objects)
print('AUDIT evaluated',len(geoms),'geometry objects',flush=True)

def combined(gs):
    vs=[];polys=[];owners=[]
    for g in gs:
        start=len(vs);vs.extend(g['vs']);polys.extend(tuple(i+start for i in poly) for poly in g['polygons']);owners.extend([g['name']]*len(g['polygons']))
    return (BVHTree.FromPolygons(vs,polys),owners) if polys else (None,[])
def cast(pack,origin,direction,distance):
    if pack[0] is None:return None
    hit,normal,index,dist=pack[0].ray_cast(origin,direction,distance)
    return {'object':pack[1][index],'point':vec(hit),'distance':round(dist,7)} if hit is not None else None
report['ports']=[]
for p in ports:
    root=scene.objects.get(p['root']);members=descend(root) if root else []
    own=[geoms[q.name] for q in members if q.name in geoms]
    near=[]
    for g in geoms.values():
        if g['type']=='FONT' or g['decal']:continue
        corners=[Vector((x,y,z)) for x in [g['b'][0][0],g['b'][1][0]] for y in [g['b'][0][1],g['b'][1][1]] for z in [g['b'][0][2],g['b'][1][2]]]
        lb=bounds([local(v,p) for v in corners]);g.setdefault('local',{})[p['id']]=lb
        if lb[1][0]<-p['clear_width']/2-.65 or lb[0][0]>p['clear_width']/2+.65 or lb[1][1]<-1.5 or lb[0][1]>.10 or lb[1][2]<-.05 or lb[0][2]>p['clear_height']+.65:continue
        near.append(g)
    held=[g for g in near if not(g['root']==p['root'] and g['carriage'])]
    saved_pack=combined(near);held_pack=combined(held)
    def aperture(pack,width,height,d0=-1.25,d1=.03):
        hits=collections.Counter();samples=[];total=0
        for u in steps(-width/2+.002,width/2-.002,.04):
            for z in steps(.005,height-.005,.04):
                total+=1;h=cast(pack,world(u,d0,z,p),p['n'],d1-d0)
                if h:
                    hits[h['object']]+=1
                    if len(samples)<24:samples.append({'u':round(u,5),'z':round(z,5),**h})
        return {'dimensions':[width,height],'depth':[d0,d1],'rays':total,'blocked':sum(hits.values()),'objects':dict(hits),'sample_hits':samples}
    result={'id':p['id'],'root':p['root'],'nominal':[p['clear_width'],p['clear_height']],'root_properties':props(root) if root else None,'local_axes':'u transverse, d outward from seam, z up','own_geometry_bounds_local':[[round(x,7) for x in row] for row in bounds([local(v,p) for g in own for v in g['vs']])],'retained_component_bounds':{},'leaf_carriages':[],'cap_flagged_geometry':sorted(g['name'] for g in own if g['cap']),'own_carriage_geometry':sorted(g['name'] for g in own if g['carriage'])}
    for g in own:
        if any(q in g['name'] for q in ['flush_sill','channel_jamb','rear_jamb','track_wear','compression_seal','lintel','impact_boot']):result['retained_component_bounds'][g['name']]=[[round(x,7) for x in row] for row in bounds([local(v,p) for v in g['vs']])]
    foundation=[g for g in geoms.values() if g['name'].startswith(p['root']+'_frame_foundation')]
    result['foundation_bounds_local']={g['name']:[[round(x,7) for x in row] for row in bounds([local(v,p) for v in g['vs']])] for g in foundation}
    for o in members:
        if o.get('component_role')=='sliding_leaf_carriage':result['leaf_carriages'].append({'name':o.name,'properties':props(o),'children':sorted(c.name for c in o.children)})
    result['closed_saved_nominal']=aperture(saved_pack,p['clear_width'],p['clear_height'])
    result['retained_frame_nominal']=aperture(held_pack,p['clear_width'],p['clear_height'])
    result['retained_operating_envelope']=aperture(held_pack,2.4 if p['id'].startswith('F') else min(2,p['clear_width']),2.2)
    # Probe exact inner dressed boundaries, including sub-grid width loss.
    section=[]
    for d in [-.75,-.63,-.56,-.50,-.37,-.28,-.201,-.174,-.166,-.15,-.13,-.08,-.059,0]:
        for z in [.115,.18,.20,.245,.55,1.0,2.0,p['clear_height']-.10]:
            left=cast(held_pack,world(0,d,z,p),-p['t'],p['clear_width']/2+.5)
            right=cast(held_pack,world(0,d,z,p),p['t'],p['clear_width']/2+.5)
            if left and right:section.append({'d':d,'z':z,'clear_width':round(left['distance']+right['distance'],7),'left':left,'right':right})
    result['cross_sections']=section
    # Approach up to closed leaves; positive endpoint remains 80 mm from front dressing.
    result['saved_closed_approach']=aperture(saved_pack,min(2,p['clear_width']),2.2,-1.25,-.59)
    result['all_retained_inside_seam']=max(local(v,p).y for g in own if not g['carriage'] for v in g['vs'])<=1e-6
    result['shell_members_crossing_seam_aperture']=[]
    for g in near:
        lb=g['local'][p['id']]
        if lb[1][1]<=.00001 or min(lb[1][0],p['clear_width']/2)-max(lb[0][0],-p['clear_width']/2)<=.00001 or lb[1][2]<=.00001 or lb[0][2]>=p['clear_height']-.00001:continue
        result['shell_members_crossing_seam_aperture'].append({'object':g['name'],'bounds_ud_z':[[round(x,7) for x in row] for row in lb],'evidence':'Evaluated world bound crosses seam into nominal aperture; neighbor geometry not loaded.'})
    # Floor and head samples verify the retained threshold, independent of lateral aperture rays.
    result['floor_head_samples']=[]
    for d in [-1.20,-.75,-.50,-.25,-.01]:
        for u in [-.75,0,.75]:
            origin=world(u,d,.10,p)
            floor=cast(held_pack,origin,Vector((0,0,-1)),.30)
            head=cast(held_pack,origin,Vector((0,0,1)),p['clear_height']+1)
            result['floor_head_samples'].append({'u':u,'d':d,'floor':floor,'head':head})
    report['ports'].append(result)
    print('AUDIT port',p['id'],'saved blocked',result['closed_saved_nominal']['blocked'],'retained',result['retained_frame_nominal']['blocked'],flush=True)

handoff=json.loads(scene.get('engine_handoff_json','{}'))
hr={'schema':handoff.get('schema'),'revision':handoff.get('revision'),'encoded_sha256':hashlib.sha256(scene.get('engine_handoff_json','').encode()).hexdigest(),'interface_hash_matches_frozen':handoff.get('interface_sha256')==sha(SNAP/'interface.json'),'errors':[],'markers':[],'door_rows':len(handoff.get('doors',[])),'collision_counts':{},'visual_only_nondecal':[]}
hr['disk_handoff_matches_saved_json']=json.loads((SNAP/'handoff.json').read_text())==handoff
manifest=json.loads((SNAP/'build_manifest.json').read_text())
hr['manifest_matches']={
    'blend':manifest['blend_sha256']==report['blend_sha256'],
    'build':manifest['source_sha256']==sha(SNAP/'build.py')==scene.get('source_sha256'),
    'details':manifest['detail_source_sha256']==sha(SNAP/'valorant_details.py')==scene.get('detail_source_sha256'),
    'interface':manifest['interface_sha256']==sha(SNAP/'interface.json')==scene.get('interface_sha256'),
    'handoff':manifest['authored_handoff_sha256']==hr['encoded_sha256'],
    'objects':manifest['objects']==len(scene.objects)}
for category in ['spawn_markers','incident_hooks','audio_zones','network_boundaries']:
    for row in handoff.get(category,[]):
        ob=scene.objects.get(row['id']);entry={'category':category,'id':row['id'],'exists':bool(ob)}
        if not ob:hr['errors'].append(['missing_marker',row['id']]);continue
        entry['position']=vec(ob.matrix_world.translation);entry['position_matches']=(ob.matrix_world.translation-Vector(row['position'])).length<1e-5
        entry['kind_matches']=ob.get('handoff_kind')==row['kind'];data=json.loads(ob.get('handoff_data','{}'));entry['data_matches']=data=={k:v for k,v in row.items() if k not in ['id','kind','position']}
        if 'bounds_min' in data:
            low=ob.matrix_world@Vector((-1,-1,-1));high=ob.matrix_world@Vector((1,1,1));entry['display_bounds_match']=max((low-Vector(data['bounds_min'])).length,(high-Vector(data['bounds_max'])).length)<1e-5
        if 'target_assembly' in data:
            target=scene.objects.get(data['target_assembly']);entry['target']=data['target_assembly'];entry['target_exists']=bool(target);entry['target_role']=target.get('assembly_role') if target else None;entry['target_geometry_count']=sum(q.name in geoms for q in descend(target)) if target else 0
        if not all(v for k,v in entry.items() if k.endswith('_matches') or k.endswith('_match') or k.endswith('_exists')):hr['errors'].append(['marker_mismatch',row['id']])
        hr['markers'].append(entry)
hr['door_semantics']=[]
for row in handoff.get('doors',[]):
    ob=scene.objects.get(row['carriage'])
    if ob is None or row['members']!=sorted(c.name for c in ob.children) or row['pose']!=ob.get('current_pose') or Vector(row['closed_to_open_section_vector_m'])!=Vector(ob.get('closed_to_open_translation_m')):hr['errors'].append(['door_mapping',row['carriage']])
    if ob:
        parent=ob.parent;port_id=next((k for k,v in roots.items() if v==parent.name),'INTERNAL_FREIGHT_GATE')
        expected_cap=parent.name in {'REFINERY_BOUNDARY','REACTOR_BOUNDARY'}
        entry={'carriage':ob.name,'assembly':parent.name,'port_id':row.get('port_id'),'section_presentation_cap':row.get('section_presentation_cap'),'geometry_owner':row.get('geometry_owner'),
            'assembly_matches':row.get('assembly')==parent.name,
            'port_matches':row.get('port_id')==port_id==parent.get('port_id'),
            'owner_matches':row.get('geometry_owner')=='fuel-corridor'==parent.get('geometry_owner'),
            'cap_matches':row.get('section_presentation_cap')==expected_cap==parent.get('presentation_cap'),
            'member_cap_flags_match':all(bool(ch.get('external_presentation_cap'))==expected_cap for ch in ob.children if ch.name in geoms),
            'removal_scope_matches':row.get('cap_removal_scope')==('Only listed moving members; retain fixed frame/sill/rails. Neighbor closure unchanged.' if expected_cap else 'Not a presentation cap'),
            'translation_space_matches':row.get('translation_space')=='section-local metres',
            'parent_transform_identity':all(abs(parent.matrix_world[i][j]-(1 if i==j else 0))<1e-6 for i in range(4) for j in range(4))}
        if not all(v for k,v in entry.items() if k.endswith('_matches') or k.endswith('_match') or k=='parent_transform_identity'):hr['errors'].append(['door_semantics',ob.name])
        hr['door_semantics'].append(entry)
hr['navigation_matches_contract']=handoff.get('navigation',{}).get('route_centerlines')==contract['route_centerlines']
hr['branch_approaches']=handoff.get('navigation',{}).get('branch_approaches')
hr['branch_approaches_match_contract']=hr['branch_approaches']==[{'port':p['id'],'threshold':p['center'],'outward':p['outward'],'state':'closed termination; owner opening required'} for p in contract['ports'] if p['id'].startswith('S')]
hr['door_record_keys']=sorted({k for row in handoff.get('doors',[]) for k in row})
hr['cap_semantics_in_typed_json']=any('presentation_cap' in k or 'integration_cap' in k for row in handoff.get('doors',[]) for k in row)
registry=handoff.get('collision',{}).get('geometry_registry',[]);names=[r['object'] for r in registry]
hr['collision_counts']=dict(collections.Counter(r['policy'] for r in registry));hr['duplicate_registry_objects']=[n for n,c in collections.Counter(names).items() if c>1]
eligible={o.name for o in scene.objects if o.type=='MESH' or(o.type=='CURVE' and o.data.bevel_depth>0)}
hr['collision_missing']=sorted(eligible-set(names));hr['collision_extra']=sorted(set(names)-eligible)
for row in registry:
    ob=scene.objects.get(row['object'])
    if ob is None or ob.get('collision_handoff')!=row['policy']:hr['errors'].append(['collision_mapping',row['object']])
    if row['policy']=='visual_only' and ob and not ob.get('surface_decal'):
        g=geoms.get(ob.name);hr['visual_only_nondecal'].append({'object':ob.name,'bounds':g['b'] if g else None})
hr['engine_pending']={k:v for k,v in handoff.items() if k in ['integration_state','navigation','collision']}
hr['engine_pending']['collision'].pop('geometry_registry',None)
report['handoff']=hr
report['full_branch_approaches']=[]
# Straight walk-up portions terminate 90 mm before the inboard frame centre.
# CLEAN/WASTE perpendicular access starts at its existing circulation centreline.
for pid,start,width in [('S01_PLANT',(0,17.4,0),2.0),('S02_CLEAN',(6.6,19.2,0),2.0),('S03_WASTE',(14.2,16,0),2.0)]:
    p=next(q for q in ports if q['id']==pid);a=Vector(start);b=p['c']-p['n']*.59;n=(b-a).normalized();length=(b-a).length;t=Vector((-n.y,n.x,0));height=2.2
    corners=[a+t*u+Vector((0,0,z)) for u in [-width/2,width/2] for z in [0,height]]+[b+t*u+Vector((0,0,z)) for u in [-width/2,width/2] for z in [0,height]];roi=bounds(corners)
    gs=[g for g in geoms.values() if not g['decal'] and g['type']!='FONT' and all(g['b'][1][i]>=roi[0][i]-.1 and g['b'][0][i]<=roi[1][i]+.1 for i in range(3))];pack=combined(gs)
    counts=collections.Counter();hits=[];total=0
    def one(o,d,dist):
        global total
        total+=1;hit=cast(pack,o,d,dist)
        if hit:
            counts[hit['object']]+=1
            if len(hits)<20:hits.append(hit)
    for z in steps(.005,2.195,.05):
        for u in steps(-.998,.998,.05):one(a+t*u+Vector((0,0,z)),n,length)
        for distance in steps(0,length,.05):one(a+n*distance-t*.998+Vector((0,0,z)),t,1.996)
    floor_hits=[]
    for distance in steps(0,length,.10):
        for u in [-.9,0,.9]:
            hit=cast(pack,a+n*distance+t*u+Vector((0,0,.10)),Vector((0,0,-1)),.30)
            if not hit or abs(hit['point'][2])>.005:floor_hits.append({'distance':round(distance,5),'u':u,'hit':hit})
    report['full_branch_approaches'].append({'port':pid,'start':vec(a),'end':vec(b),'width':width,'height':height,'rays':total,'blocked':sum(counts.values()),'blocking_objects':dict(counts),'first_hits':hits,'floor_failures':floor_hits,'scope':'Sampled straight walk-up to saved CLOSED leaf, 0.05m crosshatch. No branch turn, door storage/motion, or neighboring passage proof.'})
report['seam_mappings']=[]
for p in ports[:2]:
    key='F01_connector_to_refinery' if p['id'].startswith('F01') else 'F02_connector_to_reactor';M=Matrix(contract['adjacent_measurements']['separate_mating_transforms'][key]['matrix4'])
    own=[g for g in geoms.values() if g['root']==p['root']]
    report['seam_mappings'].append({'id':p['id'],'mapped_seam':vec(M@p['c']),'mapped_outward':vec(M.to_3x3()@p['n']),'mapped_sill_bounds':{g['name']:[[round(x,7) for x in row] for row in bounds([M@v for v in g['vs']])] for g in own if '_flush_sill' in g['name']},'no_neighbor_geometry_loaded':len(bpy.data.libraries)==0})
report['elapsed_seconds']=round(time.time()-START,3)
report['saved']=False
OUT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('AUDIT_DONE',str(OUT),'elapsed',report['elapsed_seconds'],'handoff_errors',hr['errors'],flush=True)



