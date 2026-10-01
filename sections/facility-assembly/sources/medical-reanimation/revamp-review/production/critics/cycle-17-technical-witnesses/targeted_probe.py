import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation');W=R/'revamp-review/production/critics/cycle-17-technical-witnesses'
before=hashlib.sha256((R/'module_overhaul_R2.blend').read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(R/'module_overhaul_R2.blend'),load_ui=False)
s=bpy.data.scenes['REANIMATION_EDIT_LOCAL'];bpy.context.window.scene=s;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
cache={}
def get(name):
    if name in cache:return cache[name]
    o=s.objects[name];ev=o.evaluated_get(deps);m=ev.to_mesh();vs=[o.matrix_world@v.co for v in m.vertices];fs=[tuple(f.vertices) for f in m.polygons];ed=[tuple(e.vertices) for e in m.edges]
    tr=BVHTree.FromPolygons(vs,fs);ps=list(vs)+[(vs[a]+vs[b])/2 for a,b in ed]
    for f in fs:
        p=sum((vs[i] for i in f),Vector())/len(f);q=tr.find_nearest(p)
        if q[0] is not None:ps.append(q[0])
    ev.to_mesh_clear();cache[name]=(vs,fs,ed,tr,ps);return cache[name]
def pair(own,target):
    ov,of,oe,ot,op=get(own);tv,tf,te,tt,tp=get(target)
    ps=list(op)+[ot.find_nearest(p)[0] for p in tp]
    for a,b in oe:
        seg=ov[b]-ov[a]
        if seg.length>1e-8:
            hit=tt.ray_cast(ov[a],seg.normalized(),seg.length)[0]
            if hit is not None:ps.append(hit)
    h,p=min(((tt.find_nearest(p),p) for p in ps if p is not None),key=lambda x:x[0][3]);q,n,i,d=h
    return {'object':own,'intended_target':target,'minimum_sampled_surface_distance_m':d,'own_surface_point_world':list(p),'target_surface_point_world':list(q),'target_normal_world':list(n),'own_surface_witness_m':ot.find_nearest(p)[3],'signed_surface_offset_m':(p-q).dot(n)}
targets=[
('Supply cabinet back','Cabinet wall spacer'),('Cabinet wall spacer','East wall'),('Identity wall spacer','East wall'),('Identity wall spacer.001','East wall'),
('Cabinet formed edge','Supply cabinet back'),('Cabinet formed edge.001','Supply cabinet back'),('Supply cabinet shelf','Supply cabinet back'),('Supply cabinet shelf.001','Supply cabinet back'),('Supply cabinet shelf.002','Supply cabinet back'),
('Handwash soap dispenser','East wall'),('Basin bottom','Sink wall bracket'),('Sink wall bracket','Sink load-bearing wall packer'),('Sink load-bearing wall packer','East wall'),('Tap rear rim mounting plate','Basin folded rim.001'),
('Supply bench top','Bench rear apron'),('Bench rear apron','Supply bench leg.001'),('Supply bench leg.001','Floor'),('Console working surface','Console cable apron'),('Console cable apron','Console steel leg.001'),('Console steel leg.001','Floor'),
('Recovery bed pan','Recovery longitudinal support'),('Recovery longitudinal support','Tubular recovery leg'),('Tubular recovery leg','Bed non-marking foot'),('Bed non-marking foot','Floor'),
('Reserve folded back','Reserve folded side'),('Reserve folded side','Reserve folded cap'),('Reserve removable door','Reserve service hinge'),('Reserve service hinge','Reserve folded side'),
('Jamb folded cover','Chamber structural upright'),('Jamb folded cover.001','Chamber structural upright.001'),('Formed end service panel','Chamber structural upright'),('Chamber structural upright','Sealed chamber pan'),('Chamber roof load beam','Chamber structural upright'),('Chamber top folded fascia','Chamber roof load beam'),
('Inner removable liner.001','Rear machine skin'),('Serviceable inner access panel','Inner service panel rear support'),('Inner service panel rear support','Rear machine skin'),('Sealed chamber pan','Chassis longitudinal channel'),('Chassis longitudinal channel','Fabricated chamber foot'),('Fabricated chamber foot','Chamber sole shoe'),('Chamber sole shoe','Floor'),
('Telescopic lift outer','Lift foot bolt flange'),('Lift foot bolt flange','Berth pedestal foot'),('Berth pedestal foot','Sealed chamber pan'),('Rail support crosshead','Telescopic lift inner'),('Captive transfer rail','Rail support crosshead'),('Adult tray pressed pan','Tray captive roller'),('Tray captive roller','Captive transfer rail'),
('Cart deck','Upper captive scissor track'),('Cart lift scissor','Upper captive scissor track'),('Cart lift scissor','Lower captive scissor track'),('Lower captive scissor track','Cart lower frame rail'),('Cart lower frame rail','Caster mounting plate'),('Caster mounting plate','Caster swivel'),('Caster swivel','Pressed caster fork'),('Pressed caster fork','Caster rubber tyre'),('Caster rubber tyre','Floor')]
results=[]
for own,target in targets:
    if own not in s.objects or target not in s.objects:results.append({'object':own,'intended_target':target,'missing_object':True});continue
    results.append(pair(own,target))
# Derive cartridge shelves geometrically by maximum evaluated top face below the
# case bottom, avoiding assumptions about numbered shelf order.
for o in s.objects:
    if not o.name.startswith('Cartridge steel body'):continue
    bottom=min(v.z for v in get(o.name)[0]); shelves=[q.name for q in s.objects if q.name.startswith('Folded storage shelf') and max(v.z for v in get(q.name)[0])<=bottom+.000001]
    shelf=max(shelves,key=lambda n:max(v.z for v in get(n)[0]));results.append(pair(o.name,shelf));results.append(pair(shelf,'Cartridge bank formed upright'))
(W/'intended-retained-load-paths.json').write_text(json.dumps(results,indent=2)+'\n')
uvs=[]
for o in s.objects:
    if o.type!='MESH':continue
    mats={}; implicit={}
    for index,m in enumerate(o.data.materials):
        if not m or not m.use_nodes:continue
        for n in m.node_tree.nodes:
            if n.type=='UVMAP' and n.outputs['UV'].is_linked:mats.setdefault(n.uv_map,set()).add(index)
            if n.type=='TEX_IMAGE' and n.image and not n.inputs['Vector'].is_linked:
                name=next((u.name for u in o.data.uv_layers if u.active_render),None)
                if name:implicit.setdefault(name,set()).add(index)
    qualifies=o.name.startswith('MED_R2 |') or o.data.name.startswith(('MED | Skill revised','MED_R2 |'))
    if qualifies:mats.setdefault('MED_Physical_1m',set()).update(range(len(o.data.materials)))
    for name,indices in implicit.items():mats.setdefault(name,set()).update(indices)
    for name,indices in mats.items():
        layer=o.data.uv_layers.get(name);polys=[p for p in o.data.polygons if p.material_index in indices];bad=[];tiny=[];finite=bool(layer)
        if layer:
            for p in polys:
                q=[layer.data[i].uv for i in p.loop_indices];finite &= all(math.isfinite(x) for v in q for x in v)
                area=abs(sum(q[i].x*q[(i+1)%len(q)].y-q[(i+1)%len(q)].x*q[i].y for i in range(len(q))))/2
                if area<5e-13:bad.append(p.index)
                elif area<1e-12:tiny.append({'face':p.index,'uv_area':area})
        uvs.append({'object':o.name,'layer':name,'consumer_face_count':len(polys),'exists':bool(layer),'finite':finite,'zero_consumer_faces':bad,'tiny_nonzero_faces':tiny,'active_render_layer':next((u.name for u in o.data.uv_layers if u.active_render),None)})
(W/'uv-consumer-face-checks.json').write_text(json.dumps(uvs,indent=2)+'\n')
# Distinguish ray-start sensitivity at real joined corners from actual gaps.
reg=json.loads((R/'revamp-review/production/support-registry.json').read_text());alternates=[]
for r in reg:
    o=s.objects[r['object']];tt=get(r['target'])[3]
    for a in r['anchors']:
        p=o.matrix_world@Vector(a['local_point']);d=Vector(a['approach_world']).normalized();runs=[]
        for offset in (.01,.015,.02):
            q,n,i,g=tt.ray_cast(p-d*offset,d,offset+.008)
            runs.append({'offset_m':offset,'gap_m':g-offset if q else None,'normal_angle_deg':math.degrees(n.angle(Vector(a['expected_surface_normal_world']))) if n else None})
        if any(x['normal_angle_deg'] is None or x['normal_angle_deg']>12.001 for x in runs):alternates.append({'object':o.name,'target':r['target'],'point_world':list(p),'runs':runs})
(W/'corner-ray-start-sensitivity.json').write_text(json.dumps(alternates,indent=2)+'\n')
(W/'targeted-provenance.json').write_text(json.dumps({'source_sha256':before,'source_unchanged':hashlib.sha256((R/'module_overhaul_R2.blend').read_bytes()).hexdigest()==before,'intended_pairs':len(results),'uv_records':len(uvs),'no_source_save':True},indent=2)+'\n')
print('TARGETED_PROBE_COMPLETE',len(results),len(uvs),flush=True)
