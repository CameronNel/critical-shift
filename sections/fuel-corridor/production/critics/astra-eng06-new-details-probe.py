"""eng06 extra actual-geometry checks: pressed leaf borders and both sign connections."""
from pathlib import Path
import runpy,json,hashlib
HERE=Path(__file__).resolve().parent
c=runpy.run_path(str(HERE/'astra-eng06-details-probe.py'))
globals().update({k:c[k] for k in ['meshes','Mesh','scene','Vector','ancestors','intersection','overlap_bounds','SAVED','EXPECTED']})
new=[m for n,m in meshes.items() if n.startswith(('REACTOR_BOUNDARY_leaf_pressed_border','REACTOR_BOUNDARY_leaf_pressed_fastener'))]
assert len(new)==10
def nearest_witness(a,b):
    samples=[]
    for source,target in [(a,b),(b,a)]:
        for p in source.points:
            q,n,i,d=target.bvh.find_nearest(p)
            if q is not None:samples.append({'source':source.obj.name,'point':list(p),'target':target.obj.name,'nearest':list(q),'distance_m':d})
    return min(samples,key=lambda p:p['distance_m'])
parts=[]
for m in new:
    roots=[a for a in ancestors(m.obj) if a.get('component_role')=='sliding_leaf_carriage']
    assert len(roots)==1
    root=roots[0]
    siblings=[other for other in meshes.values() if root in list(ancestors(other.obj)) and other.obj!=m.obj]
    outside=[other for other in meshes.values() if root not in list(ancestors(other.obj)) and overlap_bounds(m.bounds,other.bounds)]
    body=[s for s in siblings if s.obj.name.startswith('REACTOR_BOUNDARY_sliding_leaf')]
    assert len(body)==1
    internal=[];external=[]
    for group,record in [(siblings,internal),(outside,external)]:
        for other in group:
            hit=intersection(m,other)
            if hit:record.append({'other':other.obj.name,**hit})
    body=body[0]
    # Shared world Y is the depth axis for this reactor door. Determine the
    # mating face from actual nearest body distance, without relying on source intent.
    distances=[]
    for p in m.points:
        q,n,i,d=body.bvh.find_nearest(p)
        distances.append({'point':list(p),'nearest':list(q),'distance_m':d})
    minimum=min(v['distance_m'] for v in distances)
    contact_vertices=[v for v in distances if v['distance_m']<=5e-6]
    parts.append({'part':m.obj.name,'carriage':root.name,'presentation_cap':bool(m.obj.get('external_presentation_cap')),
                  'world_bounds_m':[list(p) for p in m.bounds],'own_leaf':body.obj.name,
                  'own_leaf_intersection':intersection(m,body),'nearest_leaf_witness':min(distances,key=lambda v:v['distance_m']),
                  'leaf_contact_vertex_count_within_5um':len(contact_vertices),'vertex_count':len(m.points),
                  'own_carriage_intersections':internal,'outside_carriage_intersections':external})

connections=[]
for a,b in [('Clean_blade_panel','Clean_blade_drop'),('Clean_blade_panel','Clean_blade_drop.001'),
            ('Plant_blade_panel','Plant_blade_drop'),('Plant_blade_panel','Plant_blade_drop.001'),
            ('Bypass_isolation_termination_spacer.001','Bypass_isolation_termination.001')]:
    connections.append({'a':a,'b':b,'nearest':nearest_witness(meshes[a],meshes[b]),'intersection':intersection(meshes[a],meshes[b])})
prior=json.loads((SAVED.parent.parent/'eng05/build_manifest.json').read_text())
now=json.loads((SAVED.parent/'build_manifest.json').read_text())
camera_readback=[]
for row in now['cameras']+now['diagnostic_cameras']:
    obj=scene.objects[row[0]]
    camera_readback.append({'camera':row[0],'actual_position':list(obj.matrix_world.translation),'manifest_position':row[1],
                           'position_error_m':(obj.matrix_world.translation-Vector(row[1])).length,
                           'actual_lens':obj.data.lens,'manifest_lens':row[3]})
report={'revision':'eng06','blend_sha256':EXPECTED,'pressed_leaf_parts':parts,'direct_connections':connections,
        'formal_ten_manifest_cameras_unchanged':prior['cameras']==now['cameras'],
        'diagnostic_camera_manifest_changes':[{'previous':a,'current':b} for a,b in zip(prior['diagnostic_cameras'],now['diagnostic_cameras']) if a!=b],
        'camera_saved_readback':camera_readback,
        'limits':['Saved closed reactor leaf detail only; no external door motion/storage proof.',
                  'Geometric contact does not certify material joining, fastening capacity, or load strength.',
                  'Few-micrometre numeric contacts retained separately from real penetration.'],
        'no_save_render_or_transform_mutation':True}
assert hashlib.sha256(SAVED.read_bytes()).hexdigest()==EXPECTED
(HERE/'astra-eng06-new-details-evidence.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'new_parts':[{'name':p['part'],'parent':p['carriage'],'own_leaf_contact_vertices':p['leaf_contact_vertex_count_within_5um'],
                  'own_hits':[(x['other'],x['aabb_overlap_xyz_m']) for x in p['own_carriage_intersections']],
                  'outside_hits':[(x['other'],x['aabb_overlap_xyz_m']) for x in p['outside_carriage_intersections']]} for p in parts],
                  'connections':[{'a':r['a'],'b':r['b'],'distance':r['nearest']['distance_m']} for r in connections]},indent=2))
