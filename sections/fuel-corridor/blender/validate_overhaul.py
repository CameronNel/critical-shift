"""Cold-open checks for the owned corridor; never saves the loaded scene.

Reuse spawn's support-ray validator, plus task-specific interface/route checks.
Run: blender -b module.blend --python-exit-code 1 --python validate_overhaul.py
"""
from pathlib import Path
import sys,json,math,hashlib
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sections/spawn-room/blender'))
from validate_contacts import TargetBVH,validate_object
TASK=ROOT/'sections/fuel-corridor'
manifest=json.loads((TASK/'production/BUILD_MANIFEST.json').read_text()) if (TASK/'production/BUILD_MANIFEST.json').exists() else json.loads((TASK/'production/SLICE_BUILD.json').read_text())
scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();cache={};failures=[]
def bvh(o):
    if o.name not in cache:cache[o.name]=TargetBVH(o,deps)
    return cache[o.name].bvh

def bounds(o):
    p=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]

contacts=[]
for o in list(scene.objects):
    if not o.get('support_anchors') or not o.get('fc_revision'):continue
    targets=json.loads(o['support_targets']);points=json.loads(o['support_anchors']);direction=Vector(o['support_direction'])
    axis=max(range(3),key=lambda i:abs(direction[i]));axisname='WORLD_'+('+' if direction[axis]>0 else '-')+'XYZ'[axis]
    # One temporary proxy per explicit point allows different supports in one assembly.
    results=[]
    for i,(target,point) in enumerate(zip(targets,points)):
        if o.get('support_directions'):
            direction=Vector(json.loads(o['support_directions'])[i]);axis=max(range(3),key=lambda k:abs(direction[k]));axisname='WORLD_'+('+' if direction[axis]>0 else '-')+'XYZ'[axis]
        proxy=bpy.data.objects.new('QA support sample',None);scene.collection.objects.link(proxy);proxy.matrix_world.translation=Vector(point)
        proxy['cs_support_target']=target;proxy['cs_support_direction']=axisname
        r=validate_object(proxy,cache,deps);r['object']=o.name;r['anchor_index']=i;results.append(r)
        bpy.data.objects.remove(proxy,do_unlink=True)
    good=all(r['status']=='PASS' for r in results)
    contacts.append({'object':o.name,'status':'PASS' if good else 'FAIL','anchors':results})
    if not good:failures.append('Contact: '+o.name)

attachments=[]
for o in list(scene.objects):
    target=o.get('fc_attachment_to')
    if not target or o.type not in ['MESH','FONT']:continue
    p=bpy.data.objects.get(target)
    if not p or p.type!='MESH':
        attachments.append({'object':o.name,'target':target,'status':'FAIL','reason':'missing mesh support'});failures.append('Attachment: '+o.name);continue
    e=o.evaluated_get(deps);mesh=e.to_mesh()
    try:
        nearest=[];tree=bvh(p)
        for v in mesh.vertices:
            point=e.matrix_world@v.co;q,n,idx,d=tree.find_nearest(point)
            if q is not None:nearest.append((float(d),list(point),list(q)))
        for face in mesh.polygons:
            point=e.matrix_world@face.center;q,n,idx,d=tree.find_nearest(point)
            if q is not None:nearest.append((float(d),list(point),list(q)))
        # A mounting stalk can contact the middle of a broad plate face while
        # none of the plate's corner vertices are near it. Sample both surfaces.
        child_tree=bvh(o)
        pe=p.evaluated_get(deps);pm=pe.to_mesh()
        try:
            for v in pm.vertices:
                point=pe.matrix_world@v.co;q,n,idx,d=child_tree.find_nearest(point)
                if q is not None:nearest.append((float(d),list(q),list(point)))
        finally:pe.to_mesh_clear()
        nearest.sort(key=lambda x:x[0]);best=nearest[0] if nearest else None
        good=bool(best and best[0]<=.005)
        attachments.append({'object':o.name,'target':target,'status':'PASS' if good else 'FAIL','nearest_gap_m':best[0] if best else None,'contact_points':nearest[:3], 'scope':'evaluated vertex/face-center and reverse surface proximity; intended assembly overlaps checked in fixed oblique views'})
        if not good:failures.append('Attachment: '+o.name)
    finally:e.to_mesh_clear()

exteriors=[]
for before in manifest['protected_exterior_cores']:
    o=bpy.data.objects.get(before['name']);after=bounds(o) if o else None
    error=max(abs(after[j][i]-before['bounds'][j][i]) for i in range(3) for j in range(2)) if after else float('inf')
    exteriors.append({'object':before['name'],'max_bound_delta_m':error,'status':'PASS' if error<1e-5 else 'FAIL'})
    if error>=1e-5:failures.append('Exterior footprint '+before['name'])

budget={'source_triangles':0,'evaluated_triangles':0,'mesh_objects':0,'material_batch_upper_bound':0};uv=[]
for o in scene.objects:
    if o.type!='MESH':continue
    budget['mesh_objects']+=1;o.data.calc_loop_triangles();budget['source_triangles']+=len(o.data.loop_triangles)
    e=o.evaluated_get(deps);m=e.to_mesh()
    try:m.calc_loop_triangles();budget['evaluated_triangles']+=len(m.loop_triangles);budget['material_batch_upper_bound']+=len(set(p.material_index for p in m.polygons))
    finally:e.to_mesh_clear()
    if o.name.startswith('FC |'):
        layer=o.data.uv_layers.active
        good=bool(layer and all(math.isfinite(c) for v in layer.data for c in v.uv))
        zero=0
        if layer:
            for tri in o.data.loop_triangles:
                a,b,c=[layer.data[i].uv for i in tri.loops]
                if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<1e-13:zero+=1
        uv.append({'object':o.name,'finite_uv':good,'degenerate_uv_triangles':zero})
        if not good:failures.append('UV '+o.name)

missing=[];packed=[]
used_images={n.image for m in bpy.data.materials if m.users and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
for i in used_images:
    good=bool(i.packed_file or i.source in ['GENERATED','VIEWER'] or Path(bpy.path.abspath(i.filepath)).is_file())
    packed.append({'name':i.name,'packed':bool(i.packed_file),'available':good})
    if not good:missing.append(i.name)
for f in bpy.data.fonts:
    if f.users and f.filepath!='<builtin>' and not f.packed_file and not Path(bpy.path.abspath(f.filepath)).is_file():missing.append(f.name)
if missing:failures.append('Missing dependencies '+str(missing))

# Cross-section rays through walking-height envelopes, with closed external leaves
# excluded only at their documented authored boundary pose. This is a geometric
# clearance sample, not a controller/turning or Unity physics certification.
contract=json.loads((ROOT/'sections/facility-assembly/sources/fuel-corridor/contracts/interface.json').read_text())
fixed_cameras=[];runtime=[]
for group,key in [(fixed_cameras,'baseline_cameras'),(runtime,'baseline_runtime')]:
    for before in manifest.get(key,[]):
        obj=bpy.data.objects.get(before['name'])
        delta=max(abs(obj.matrix_world[j][i]-before['matrix'][j][i]) for i in range(4) for j in range(4)) if obj else float('inf')
        lens=abs(obj.data.lens-before['lens']) if key=='baseline_cameras' and obj else 0
        good=delta<1e-6 and lens<1e-6
        group.append({'object':before['name'],'matrix_delta':delta,'lens_delta':lens,'status':'PASS' if good else 'FAIL'})
        if not good:failures.append('Fixed transform '+before['name'])
floor_footprints=[]
for cell in contract['floor_cells']:
    obj=bpy.data.objects['Floor_'+cell['id']];lo,hi=bounds(obj);a=cell['bounds']
    delta=max(abs(x-y) for x,y in zip([lo[0],hi[0],lo[1],hi[1]],a))
    floor_footprints.append({'cell':cell['id'],'xy_bound_delta_m':delta,'walking_height_m':0,'status':'PASS' if delta<1e-5 else 'FAIL'})
    if delta>=1e-5:failures.append('Floor footprint '+cell['id'])
route_results=[]
if manifest['stage']=='full':
    obstacles=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and bounds(o)[1][2]>.08 and bounds(o)[0][2]<2.56 and not 'boundary' in o.name and not 'Plant service' in o.name and not 'Clean service' in o.name and not 'Waste transfer' in o.name]
    trees=[(o.name,bvh(o)) for o in obstacles]
    for name,line,width in [('freight',contract['route_centerlines']['freight'],2.6),('service_bypass',contract['route_centerlines']['service_bypass'],2.0),('plant_header',contract['route_centerlines']['plant_header'],2.0)]:
        hits=[];samples=0
        for start,end in zip(line,line[1:]):
            a=Vector((*start,0));b=Vector((*end,0));d=(b-a).normalized();perp=Vector((-d.y,d.x,0));length=(b-a).length
            for i in range(1,int(length/.2)):
                p=a+d*(i*.2)
                if name=='freight' and (p.y<1.1 or p.y>23.1):continue
                if name=='plant_header' and p.x<-4.6:continue
                for z in [.18,.75,1.3,1.8,2.35]:
                    q=Vector((p.x,p.y,z));samples+=1
                    for obj,tree in trees:
                        for s in [-1,1]:
                            hp,hn,idx,dist=tree.ray_cast(q,perp*s,width/2-.0005)
                            if hp is not None:
                                hits.append({'object':obj,'point':list(hp),'station':list(q),'side':s,'distance_m':dist})
        dedup={h['object']:h for h in hits}
        route_results.append({'route':name,'width_m':width,'sample_cross_sections':samples,'status':'PASS' if not hits else 'FAIL','obstructions':list(dedup.values())})
        if hits:failures.append('Route '+name)

report={'schema':'fuel-overhaul-cold-validation/1','file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'blender':bpy.app.version_string,'status':'PASS' if not failures else 'FAIL','failures':failures,'exterior_bounds':exteriors,'floor_footprints':floor_footprints,'fixed_cameras':fixed_cameras,'runtime_transforms':runtime,'support_contacts':contacts,'attachment_contacts':attachments,'geometry_budget':budget,'uv':uv,'dependencies':packed,'missing_dependencies':missing,'routes':route_results,'limitations':['Sampled geometric clearance is not continuous cart/player simulation.','Unity importer, batching, colliders and controller are not executed in this Blender environment.']}
out=TASK/'production'/('COLD_VALIDATION.json' if manifest['stage']=='full' else 'SLICE_VALIDATION.json');out.write_text(json.dumps(report,indent=2));print('FUEL_VALIDATION',report['status'],len(failures),'failures',budget,flush=True)
for f in failures:print('FAIL',f,flush=True)
if failures:raise RuntimeError('Fuel cold validation failed; inspect '+str(out))
