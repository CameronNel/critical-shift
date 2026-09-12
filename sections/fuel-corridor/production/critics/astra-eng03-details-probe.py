"""Read-only evaluated checks of eng03's new physical wall details and recess assembly."""
from pathlib import Path
import runpy,json,hashlib
HERE=Path(__file__).resolve().parent
ctx=runpy.run_path(str(HERE/'astra-eng03-engineering-probe.py'))
globals().update({k:ctx[k] for k in ['bpy','Vector','Mesh','scene','meshes','ancestors','intersection','bounds','overlap_bounds','SAVED','EXPECTED']})
names=['Service_air_station','East_distribution','Bypass_isolation','Bypass_first_aid','Bypass_work_permit',
       'Plant_work_permit','Clean_distribution','Reactor_turn_key','Refinery_approach_key','Reactor_left_key','Reactor_right_key']
names += ['Route_guide_%02d'%i for i in range(11)]
roots=[scene.objects[n] for n in names]
for obj in scene.objects:
    if obj.type not in {'MESH','CURVE'} or obj.get('surface_decal'):continue
    if obj.type=='CURVE' and obj.data.bevel_depth==0:continue
    if (any(o in roots for o in ancestors(obj)) or any(c.name=='01_Architecture' for c in obj.users_collection)) and obj.name not in meshes:
        meshes[obj.name]=Mesh(obj)
architecture=[m for m in meshes.values() if any(c.name=='01_Architecture' for c in m.obj.users_collection)]

def nearest_ray(mesh_list,start,direction,max_distance):
    hits=[]
    for mesh in mesh_list:
        p,n,tri,d=mesh.bvh.ray_cast(start,direction,max_distance)
        if p is not None:hits.append({'object':mesh.obj.name,'point':list(p),'normal':list(n),'distance':d})
    return min(hits,key=lambda h:h['distance']) if hits else None

result=[]
for root in roots:
    members=[m for m in meshes.values() if root in list(ancestors(m.obj))]
    bb=bounds([p for m in members for p in m.bounds])
    candidates=[m for m in architecture if overlap_bounds(m.bounds,bb,pad=.002)]
    positive=[];contacts=[]
    for m in members:
        for fixed in candidates:
            if m.obj==fixed.obj:continue
            hit=intersection(m,fixed)
            if hit:
                (contacts if hit['aabb_contact_only_within_1um'] else positive).append({'a':m.obj.name,'b':fixed.obj.name,**hit})
    anchor_results=[]
    anchors=json.loads(root.get('support_anchors','[]'))
    targets=json.loads(root.get('support_targets','[]'))
    direction=Vector(root.get('support_direction',[0,0,0]))
    if direction.length:direction.normalize()
    for i,xyz in enumerate(anchors):
        anchor=Vector(xyz)
        wall=nearest_ray(architecture,anchor-direction*.10,direction,.25)
        own=nearest_ray(members,anchor+direction*.012,-direction,.15)
        if wall:wall['signed_anchor_gap_m']=(Vector(wall['point'])-anchor).dot(direction)
        if own:own['signed_back_face_to_anchor_m']=(Vector(own['point'])-anchor).dot(direction)
        anchor_results.append({'anchor':xyz,'direction':list(direction),'declared_target':targets[i] if i<len(targets) else None,
                               'actual_architecture_ray':wall,'actual_assembly_back_ray':own})
    result.append({'assembly':root.name,'members':len(members),'world_bounds_m':[list(p) for p in bb],
                   'positive_architecture_intersections':positive,'zero_thickness_architecture_contacts':contacts,
                   'support_anchors':anchor_results})

report={'revision':'eng03','blend':str(SAVED),'blend_sha256':EXPECTED,'object_count':len(scene.objects),
        'method':'Actual evaluated world meshes against local architecture; direct independent wall/assembly rays at declared anchors.',
        'limits':['Declared anchors do not exhaust distributed mounting faces.','Positive intersections require interpretation for deliberately embedded fasteners; no intended exemption applied silently.',
                  'New fixture versus architecture checks do not establish all intra-assembly support, route controller or runtime behavior.'],
        'assemblies':result,'no_save_render_or_scene_transform_mutation':True}
assert hashlib.sha256(SAVED.read_bytes()).hexdigest()==EXPECTED
(HERE/'astra-eng03-details-evidence.json').write_text(json.dumps(report,indent=2))
print(json.dumps([{'assembly':r['assembly'],'positive_pairs':[(p['a'],p['b']) for p in r['positive_architecture_intersections']],
                   'anchor_readings':[{'target':p['declared_target'],'wall_gap':p['actual_architecture_ray']['signed_anchor_gap_m'] if p['actual_architecture_ray'] else None,
                                      'back_gap':p['actual_assembly_back_ray']['signed_back_face_to_anchor_m'] if p['actual_assembly_back_ray'] else None} for p in r['support_anchors']]} for r in result],indent=2))
