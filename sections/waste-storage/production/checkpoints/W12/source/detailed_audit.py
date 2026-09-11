"""Independent read-only measured detail checks on an already saved artifact."""
from pathlib import Path
exec(compile((Path(__file__).parent/'validate_scene.py').read_text(),'validate_scene.py','exec'))
detail=[]
def record(id,ok,evidence):detail.append({'id':id,'pass':bool(ok),'evidence':evidence})
# Font surfaces must have real nearby backing at sampled glyph vertices.
# This does not replace readable pixels from a player approach.
labels=[]
for name,g in geometry.items():
    ob=g['object']
    if ob.type!='FONT':continue
    e=ob.evaluated_get(dg);me=e.to_mesh();pts=[e.matrix_world@v.co for v in me.vertices];e.to_mesh_clear()
    normal=(ob.matrix_world.to_3x3()@Vector((0,0,1))).normalized();missing=[];supports=Counter();overlap_hits=[]
    for pt in pts[::max(1,len(pts)//24)]:
        candidates=[]
        for n,h in geometry.items():
            if n==name or h['object'].type=='FONT':continue
            if any(pt[a]<h['lo'][a]-.045 or pt[a]>h['hi'][a]+.045 for a in range(3)):continue
            hit=h['bvh'].ray_cast(pt+normal*.003,-normal,.043)
            if hit[0] is not None:candidates.append((hit[3],n))
        if candidates:supports[min(candidates)[1]]+=1
        else:missing.append(list(pt))
    labels.append({'name':name,'body':ob.data.body,'size_m':ob.data.size,'unsupported_samples':missing,'support_objects':dict(supports)})
record('glyph_backing',all(not r['unsupported_samples'] for r in labels),labels)
# Contract-derived aperture grids and solid-wall positive controls.
openings=[]
for item in contract['portals']+contract['internal_portals']:
    center=Vector(item['center']);normal=Vector(item.get('outward_normal',item.get('normal')));tangent=Vector((-normal.y,normal.x,0));w=item['clear_width'];h=item['clear_height'];bad=[];controls=[]
    for j in range(13):
        u=-w/2+.015+(w-.03)*j/12
        for k in range(11):
            z=.02+(h-.04)*k/10;p=center+tangent*u+Vector((0,0,z))-normal*.40
            hit=[n for n,g in geometry.items() if g['bvh'].ray_cast(p,normal,.8)[0] is not None]
            if hit:bad.append({'u':u,'z':z,'objects':hit})
    for u in [-w/2-.10,w/2+.10]:
        p=center+tangent*u+Vector((0,0,1.2))-normal*.4
        hits=[n for n,g in geometry.items() if g['bvh'].ray_cast(p,normal,.8)[0] is not None];controls.append({'u':u,'solid_detected':bool(hits),'objects':hits})
    openings.append({'id':item['id'],'width':w,'height':h,'obstructions':bad,'positive_controls':controls})
record('contract_aperture_grid',all(not x['obstructions'] and all(c['solid_detected'] for c in x['positive_controls']) for x in openings),openings)
# Ordinary walkway and two-person rescue are distinct envelopes.
clearance=[]
for name,points,half in [('main_walk',[(0,0),(0,18)],.50),('main_carry',[(0,0),(0,18)],.90),('personnel_walk',[(0,2.4),(6.32,2.4)],.50),('booth_walk',[(-1.8,2.2),(-3.2,2.2)],.50),('residue_access',[(0,6.6),(-3.50,6.6)],.50),('shielded_access',[(0,11),(-3,11)],.50),('dry_access',[(0,6.7),(2.8,6.7)],.50),('quarantine_access',[(0,11),(3.15,11)],.50)]:
    bad=[]
    for a,b in zip(points,points[1:]):
        a=Vector(a);b=Vector(b);steps=max(1,math.ceil((b-a).length/.08))
        for k in range(steps+1):
            p=a.lerp(b,k/steps);lo=Vector((p.x-half,p.y-half,.025));hi=Vector((p.x+half,p.y+half,1.90));hits=[n for n,g in geometry.items() if overlap(lo,hi,g)]
            if hits:bad.append({'center':list(p),'objects':hits})
    clearance.append({'id':name,'body_width':2*half,'obstructions':bad})
record('required_walk_and_carry',all(not x['obstructions'] for x in clearance),clearance)
# Actual 0.90-deep maintenance boxes, separate from mere route centerlines.
maintenance=[]
for name,lo,hi in [('SC01_face',(-3.86,10.45,.025),(-2.96,11.35,1.9)),('SC02_face',(-3.86,11.80,.025),(-2.96,12.75,1.9)),('DR02_face',(3.175,6.20,.025),(5.325,7.10,1.9)),('QH01_face',(3.14,10.70,.025),(4.04,12.80,1.9)),('VF01_filters',(-5.65,14.46,.025),(-3.10,15.36,1.9)),('WB01_face',(3.70,15.47,.025),(5.40,16.37,1.9))]:
    hits=[n for n,g in geometry.items() if overlap(Vector(lo),Vector(hi),g)];maintenance.append({'id':name,'min':lo,'max':hi,'objects':hits})
record('maintenance_boxes',all(not x['objects'] for x in maintenance),maintenance)
# Socket center, normal, geometry at boundary and semantic ownership.
sockets=[]
for item in contract['utility_interfaces']:
    ob=s.objects.get('IF_'+item['id']);p=Vector(item['center']);near=[]
    for name,g in geometry.items():
        if g['object'].type=='FONT':continue
        hit=g['bvh'].find_nearest(p,.025)
        if hit[0] is not None:near.append({'object':name,'distance':hit[3]})
    normal_ok=ob is not None and json.loads(ob['outward_normal'])==item['outward_normal'];sockets.append({'id':item['id'],'normal_match':normal_ok,'boundary_surface':near})
record('physical_socket_faces',all(x['normal_match'] and x['boundary_surface'] for x in sockets),sockets)
hooks=[]
for name,target in [('INTERACT_INVENTORY','IM01_INVENTORY'),('INTERACT_VENT_ISOLATE','VF01_EXTRACTION'),('INSPECT_QUARANTINE','QH01'),('INCIDENT_WASTE_BREACH','SC01')]:
    ob=s.objects.get(name);hooks.append({'id':name,'target':target,'pass':ob is not None and ob.get('target_id')==target and target in s.objects})
record('host_hook_targets',all(x['pass'] for x in hooks),hooks)
record('font_dependencies',all(f.filepath in ['','<builtin>'] or f.packed_file for f in bpy.data.fonts),[{'name':f.name,'path':f.filepath,'packed':bool(f.packed_file)} for f in bpy.data.fonts])
record('saved_camera_manifest',json.loads(s['camera_manifest'])==[{'name':o.name,'location':list(o.location),'rotation_euler':list(o.rotation_euler),'lens':o.data.lens} for o in s.objects if o.type=='CAMERA'],json.loads(s['camera_manifest']))
result={'revision':s.get('revision'),'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'pass':all(x['pass'] for x in detail),'checks':detail,'limitations':['Static measured envelopes, not engine physics or animation.','Glyph backing sampling does not establish pixel readability.','Socket contact does not alone establish an entire utility connection graph.']}
(dest/'detail.json').write_text(json.dumps(result,indent=2));print('DETAIL_AUDIT',[(x['id'],x['pass']) for x in detail])

