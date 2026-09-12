"""Read-only evaluated eng07 attachments and independent camera near-field crosshatches."""
from pathlib import Path
import runpy,json,hashlib,math
HERE=Path(__file__).resolve().parent
c=runpy.run_path(str(HERE/'astra-eng07-details-probe.py'))
globals().update({k:c[k] for k in ['meshes','Mesh','scene','Vector','ancestors','intersection','overlap_bounds','SAVED','EXPECTED','bpy']})
roles=('leaf_identity_field','leaf_identity_fastener','leaf_stiffener','leaf_pull_','leaf_pressed_')
selected=[m for n,m in meshes.items() if n.startswith('REACTOR_BOUNDARY_') and any(t in n for t in roles)]
parts=[]
def nearest_pair(a,b):
    samples=[]
    for source,target in [(a,b),(b,a)]:
        for p in source.points:
            q,n,i,d=target.bvh.find_nearest(p)
            if q is not None:samples.append({'source':source.obj.name,'point':list(p),'target':target.obj.name,'nearest':list(q),'distance_m':d})
    return min(samples,key=lambda p:p['distance_m'])
for m in selected:
    roots=[a for a in ancestors(m.obj) if a.get('component_role')=='sliding_leaf_carriage'];assert len(roots)==1
    root=roots[0]
    own=[other for other in meshes.values() if root in list(ancestors(other.obj)) and other.obj!=m.obj]
    outside=[other for other in meshes.values() if root not in list(ancestors(other.obj)) and overlap_bounds(m.bounds,other.bounds)]
    internal=[];external=[]
    for group,out in [(own,internal),(outside,external)]:
        for other in group:
            hit=intersection(m,other)
            if hit:out.append({'other':other.obj.name,**hit})
    # Candidate AABB proximity chooses local attachment witnesses; nearest point
    # is measured on actual surfaces, not inferred from boxes.
    nearby=[other for other in own if overlap_bounds(m.bounds,other.bounds,pad=.007)]
    attachment=[nearest_pair(m,other) for other in nearby]
    parts.append({'part':m.obj.name,'carriage':root.name,'cap':bool(m.obj.get('external_presentation_cap')),
                  'bounds_m':[list(p) for p in m.bounds],'own_carriage_intersections':internal,
                  'outside_carriage_intersections':external,'nearby_attachment_witnesses':attachment})

deps=bpy.context.evaluated_depsgraph_get()
def frame_rays(cam,count=17):
    corners=cam.data.view_frame(scene=scene)
    x0,x1=min(p.x for p in corners),max(p.x for p in corners)
    y0,y1=min(p.y for p in corners),max(p.y for p in corners)
    z=corners[0].z
    for j in range(count):
        for i in range(count):
            # Cell centers cover the whole frustum, including the center.
            local=Vector((x0+(x1-x0)*(i+.5)/count,y0+(y1-y0)*(j+.5)/count,z)).normalized()
            yield i,j,(cam.matrix_world.to_3x3()@local).normalized()
camera_results=[]
for cam in [o for o in scene.objects if o.type=='CAMERA']:
    origin=cam.matrix_world.translation;hits=[];hist={};central=None
    for i,j,direction in frame_rays(cam):
        hit,p,n,index,obj,mat=scene.ray_cast(deps,origin,direction,distance=30)
        if hit:
            distance=(p-origin).length
            row={'grid':[i,j],'object':obj.name,'distance_m':distance,'point':list(p)}
            hist[obj.name]=hist.get(obj.name,0)+1
            if distance<.12:hits.append(row)
            if i==8 and j==8:central=row
    camera_results.append({'name':cam.name,'rays':289,'near_distance_m':.12,'near_hits':hits,
                            'central_first_hit':central,'all_first_hit_counts':hist,
                            'position':list(origin),'lens':cam.data.lens,'clip_start':cam.data.clip_start})

# Replay the previous D05 pose mathematically through the same eng07 scene.
# No camera or scene object transform is changed.
prior=json.loads((SAVED.parent.parent/'eng06/build_manifest.json').read_text())
row=next(r for r in prior['diagnostic_cameras'] if r[0]=='D05_GATE_MECHANISM')
origin=Vector(row[1]);direction=(Vector(row[2])-origin).normalized()
hit,p,n,index,obj,mat=scene.ray_cast(deps,origin,direction,distance=30)
prior_center={'from_eng06_manifest':row,'hit_object':obj.name if hit else None,'distance_m':(p-origin).length if hit else None,
              'point':list(p) if hit else None,'scope':'Previous camera centerline tested against eng07 retained gate-region geometry; no old scene reload.'}

# Surface decals added to moving reactor leaves remain attached/exported with
# the owning carriage; their material appearance is reserved for actual pixels.
decals=[]
for obj in scene.objects:
    if not obj.name.startswith(('REACTOR_BOUNDARY_leaf_handling_wear','REACTOR_BOUNDARY_leaf_identity_mark')):continue
    parents=[o.name for o in ancestors(obj) if o.get('component_role')=='sliding_leaf_carriage']
    decals.append({'name':obj.name,'type':obj.type,'decal':bool(obj.get('surface_decal')),
                    'cap':bool(obj.get('external_presentation_cap')),'carriages':parents})
report={'revision':'eng07','blend_sha256':EXPECTED,'object_count':len(scene.objects),
        'selected_leaf_parts':parts,'camera_frustum_near_field':camera_results,'previous_d05_centerline':prior_center,
        'new_reactor_surface_decals':decals,
        'method':'Evaluated triangles/containment, actual nearest-surface attachment witnesses, and independent17x17 camera-frustum first-hit rays.',
        'limits':['No render or visual judgment; clear near-field does not guarantee useful composition or exposure.',
                  'Finite camera ray lattice is not a full image occlusion proof; first hits up to30m only.',
                  'Actual saved closed leaves only, no external opening/storage or continuous motion simulation.',
                  'Attachment contacts do not certify load strength or every fastening connection.'],
        'no_save_render_or_transform_mutation':True}
assert hashlib.sha256(SAVED.read_bytes()).hexdigest()==EXPECTED
(HERE/'astra-eng07-leaf-camera-evidence.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'leaf_parts':len(parts),'outside_hits':[(p['part'],q['other']) for p in parts for q in p['outside_carriage_intersections']],
                  'cameras':[{'name':r['name'],'near_hits':len(r['near_hits']),'center':r['central_first_hit']} for r in camera_results],
                  'previous_center':prior_center,'surface_decals':len(decals)},indent=2))
