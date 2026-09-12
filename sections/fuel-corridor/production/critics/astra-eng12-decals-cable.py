import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

BASE=Path('C:/Users/Camer/.codex/worktrees/3598/critical-shift/sections/fuel-corridor/production')
OUT=BASE/'critics/astra-eng12-decals-cable-evidence.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def vec(v):return [float(x) for x in v]
def bounds(vs):return [[min(p[i] for p in vs) for i in range(3)],[max(p[i] for p in vs) for i in range(3)]]
def meshdata(o,dg,rootinv):
    e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles()
    try:
        vs=[rootinv@e.matrix_world@v.co for v in m.vertices]
        ts=[tuple(t.vertices) for t in m.loop_triangles]
        return {'vs':vs,'ts':ts,'bvh':BVHTree.FromPolygons(vs,ts,all_triangles=True)}
    finally:e.to_mesh_clear()
def hullplanes(points):
    # Temporary CPU bmesh only; never linked into either scene.
    bm=bmesh.new()
    for p in points:bm.verts.new(p)
    result=bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
    center=sum(points,Vector())/len(points);planes=[]
    for f in result['geom']:
        if not isinstance(f,bmesh.types.BMFace):continue
        a,b,c=[v.co.copy() for v in list(f.verts)[:3]];n=(b-a).cross(c-a)
        if n.length<1e-12:continue
        n.normalize()
        if n.dot(center-a)>0:n=-n
        planes.append((n,n.dot(a)))
    bm.free();return planes
def hullcheck(points,planes,tol=1e-6):
    margins=[max(n.dot(p)-d for n,d in planes) for p in points]
    return {'points':len(points),'plane_count':len(planes),'outside_1um':sum(d>tol for d in margins),'maximum_outward_halfspace_distance_m':max(margins)}

report={'method':'Independent CPU evaluated surfaces of frozen eng11 and eng12. No checkpoint source executed; no scene transform/save/render. Decal samples are barycentric grids on evaluated triangles. Signed nearest distances use intended-body evaluated face normals. Cable hulls are temporary convex hulls, not replacement scene geometry.','snapshots':{},'limits':['No visual scoring, ray visibility or renderer-depth-bias check.','Dense sampled decal attachment does not prove every interior point or shader displacement.','Cable hull containment is not cable-to-hardware collision or endpoint-attachment proof.']}
saved={}
for rev in ['eng11','eng12']:
    snap=BASE/'checkpoints'/rev;path=snap/'Fuel_Corridor.blend';before=sha(path)
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();root=scene.objects['Freight_gate_drive'];inv=root.matrix_world.inverted()
    manifest=json.loads((snap/'build_manifest.json').read_text());hj=json.loads(scene['engine_handoff_json']);registry={r['object']:r['policy'] for r in hj['collision']['geometry_registry']}
    hashes={n:sha(snap/n) for n in ['Fuel_Corridor.blend','build.py','valorant_details.py','interface.json','build_manifest.json']}
    rr={'hashes':hashes,'objects':len(scene.objects),'manifest_matches':{'blend':before==manifest['blend_sha256'],'build':hashes['build.py']==manifest['source_sha256']==scene['source_sha256'],'details':hashes['valorant_details.py']==manifest['detail_source_sha256']==scene['detail_source_sha256'],'interface':hashes['interface.json']==manifest['interface_sha256']==scene['interface_sha256'],'objects':manifest['objects']==len(scene.objects)},'decals':[]}
    geom={o.name:meshdata(o,dg,inv) for o in root.children_recursive if o.type in ['MESH','CURVE'] and (o.type=='MESH' or o.data.bevel_depth>0)}
    bodies={n:g for n,g in geom.items() if not scene.objects[n].get('surface_decal')}
    for n,g in geom.items():
        if not n.startswith(('Motor_fin_edge_wear','Motor_bell_edge_wear','Motor_guard_edge_wear')):continue
        o=scene.objects[n]
        prefix='Motor_cooling_fin' if n.startswith('Motor_fin') else 'Motor_end_bell' if n.startswith('Motor_bell') else 'Motor_reducer_guard'
        candidate={k:v for k,v in bodies.items() if k.startswith(prefix)}
        center=sum(g['vs'],Vector())/len(g['vs']);target=min(candidate,key=lambda k:candidate[k]['bvh'].find_nearest(center)[3]);bv=candidate[target]['bvh']
        samples=[]
        for tri in g['ts']:
            a,b,c=[g['vs'][i] for i in tri]
            for i in range(21):
                for j in range(21-i):samples.append(a+(b-a)*(i/20)+(c-a)*(j/20))
        distances=[];signed=[];other_nearest={};buried_other={}
        for p in samples:
            q,normal,idx,d=bv.find_nearest(p);distances.append(d);signed.append((p-q).dot(normal))
            nearest=min(((body['bvh'].find_nearest(p)[3],name) for name,body in bodies.items()),key=lambda t:t[0])
            other_nearest[nearest[1]]=other_nearest.get(nearest[1],0)+1
            # Query nearby convex manufactured parts for obvious burial using nearest-face sign.
            for name,body in bodies.items():
                if name==target:continue
                q2,n2,idx2,d2=body['bvh'].find_nearest(p)
                if d2<.005 and (p-q2).dot(n2)<-1e-5:buried_other[name]=buried_other.get(name,0)+1
        extra={}
        if n.startswith('Motor_guard_edge_wear'):
            bandplanes=hullplanes(bodies['Motor_guard_orange_band']['vs'])
            bandmargins=[max(p.dot(normal)-d for normal,d in bandplanes) for p in samples]
            extra={'orange_band_convex_inside_samples_over_10um':sum(d<-.00001 for d in bandmargins),'orange_band_maximum_interior_halfspace_depth_m':max(0,-min(bandmargins)),'own_surface_samples_over_1mm_gap':sum(d>.001 for d in distances)}
        rr['decals'].append({'name':n,'parent':o.parent.name,'surface_decal':bool(o.get('surface_decal')),'saved_collision_handoff':o.get('collision_handoff'),'export_collision_handoff':registry.get(n),'intended_surface':target,'bounds_drive_local':bounds(g['vs']),'vertex_count':len(g['vs']),'samples':len(samples),'nearest_distance_m':[min(distances),max(distances)],'signed_distance_m':[min(signed),max(signed)],'buried_intended_samples_over_10um':sum(x<-.00001 for x in signed),'nearest_body_sample_counts':other_nearest,'possible_other_body_burial_samples_over_10um':buried_other,**extra})
    cable=scene.objects['Motor_supply_cable'];cg=geom[cable.name]
    points=[inv@cable.matrix_world@Vector(p.co[:3]) for s in cable.data.splines for p in s.points]
    saved[rev]={'points':points,'verts':cg['vs']}
    rr['cable']={'type':cable.type,'splines':[s.type for s in cable.data.splines],'point_count':len(points),'points_drive_local':[vec(p) for p in points],'bevel_depth_m':cable.data.bevel_depth,'bevel_resolution':cable.data.bevel_resolution,'curve_matrix_world':[list(r) for r in cable.matrix_world],'root_matrix_world':[list(r) for r in root.matrix_world],'evaluated_vertices':len(cg['vs']),'centerline_bounds_drive_local':bounds(points),'tube_bounds_drive_local':bounds(cg['vs']),'surface_decal':bool(cable.get('surface_decal')),'saved_collision_handoff':cable.get('collision_handoff'),'export_collision_handoff':registry.get(cable.name)}
    rr['blend_hash_unchanged_after_read']=before==sha(path)
    report['snapshots'][rev]=rr

old=saved['eng11'];new=saved['eng12'];oldplanes=hullplanes(old['points']);oldtubeplanes=hullplanes(old['verts'])
report['cable_comparison']={'eng12_centerline_vs_eng11_centerline_hull':hullcheck(new['points'],oldplanes),'eng12_tube_vs_eng11_centerline_hull':hullcheck(new['verts'],oldplanes),'eng12_tube_vs_eng11_tube_hull':hullcheck(new['verts'],oldtubeplanes),'eng11_tube_hull_selftest':hullcheck(old['verts'],oldtubeplanes),'same_first_endpoint':(new['points'][0]-old['points'][0]).length,'same_last_endpoint':(new['points'][-1]-old['points'][-1]).length,'radius_distinction':'A centerline convex hull excludes tube radius. Uniform-radius tube lies in a radius-expanded centerline hull; this does not imply inclusion in the old unexpanded point hull or old evaluated tube hull.'}
OUT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('DECALS_CABLE_AUDIT_DONE',str(OUT),flush=True)
