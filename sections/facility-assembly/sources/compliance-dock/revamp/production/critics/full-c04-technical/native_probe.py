"""Independent read-only frozen native audit. No operators or scene writes."""
import argparse, hashlib, json, math, sys
from collections import defaultdict
from pathlib import Path
import bmesh, bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
REPO=ROOT.parents[3]
p=argparse.ArgumentParser();p.add_argument('--expected-sha',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
native=Path(bpy.data.filepath)
assert sha(native)==a.expected_sha,'Frozen input hash mismatch'
S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL']
assert bpy.context.scene==S,'Must open the authoritative local scene'
deps=bpy.context.evaluated_depsgraph_get()
report={'native':str(native),'native_sha256':sha(native),'runtime':bpy.app.version_string,
        'scene':S.name,'revision':S.get('revision'),'probe_sha256':sha(__file__),
        'baseline':{},'counters':{},'focused_islands':[],'mesh_defects':[],
        'dependency_defects':[],'protected_inputs':[],'recipe_integrity':[],
        'physical_contacts':[],'exact_duplicate_triangle_pairs':[]}
baseline=json.loads((ROOT/'revamp/production/baseline.json').read_text())
base_objects={o['name']:o for o in baseline['objects']}
changed=[];missing=[]
for name,rec in base_objects.items():
    o=S.objects.get(name)
    if o is None:missing.append(name);continue
    delta=max(abs(o.matrix_world[i][j]-rec['matrix'][i][j]) for i in range(4) for j in range(4))
    if delta>1e-6:changed.append({'object':name,'matrix_delta':delta})
report['baseline']={'sha256':baseline['source_sha256'],'objects':len(base_objects),
    'triangles':baseline['evaluated_triangles'],'material_submeshes':baseline['authoring_material_submeshes'],
    'missing_objects':missing,'changed_original_matrices':changed}
for rel,expected in json.loads((ROOT/'revamp/production/protected-inputs.json').read_text()).items():
    actual=sha(REPO/rel);report['protected_inputs'].append({'path':rel,'expected':expected,'actual':actual,'pass':actual==expected})
for name,expected in json.loads(S['recipe_sha256']).items():
    actual=sha(ROOT/name);report['recipe_integrity'].append({'path':name,'expected':expected,'actual':actual,'pass':actual==expected})
for lib in bpy.data.libraries:
    # Loaded Library.filepath is already resolved/rebased to the main-file
    # context; passing its parent again incorrectly adds that context twice.
    raw=bpy.path.abspath(lib.filepath)
    if not Path(raw).is_file():report['dependency_defects'].append({'type':'library','name':lib.name,'path':raw})
for image in bpy.data.images:
    if image.source in {'FILE','MOVIE','SEQUENCE','TILED'} and not image.packed_file and not getattr(image,'packed_files',()):
        raw=bpy.path.abspath(image.filepath,library=image.library)
        paths=[raw.replace('<UDIM>',str(t.number)) for t in image.tiles] if image.source=='TILED' else [raw]
        if not all(Path(path).is_file() for path in paths):report['dependency_defects'].append({'type':'image','name':image.name,'paths':paths})
for font in bpy.data.fonts:
    if font.filepath and font.filepath!='<builtin>' and not font.packed_file:
        raw=bpy.path.abspath(font.filepath,library=font.library)
        if not Path(raw).is_file():report['dependency_defects'].append({'type':'font','name':font.name,'path':raw})

def box(vs):return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
def ancestor_names(o):
    names=[]
    while o:names.append(o.name);o=o.parent
    return names
def contains(tree,point):
    # Closed native topology, two non-axis rays; do not infer solids from bounds.
    votes=[]
    for direction in [Vector((1,.3713907,.529173)).normalized(),Vector((.219471,1,.681703)).normalized()]:
        origin=point.copy();count=0
        for _ in range(200):
            hit=tree.ray_cast(origin,direction,100)
            if hit[0] is None:break
            # Native world Y is ~16m: 1e-7m is below float32 precision there.
            count+=1;origin=hit[0]+direction*2e-5
        votes.append(count%2==1)
    return all(votes)
islands=[];objects={};triangles=0;submeshes=0;materials=set();seen={};mesh_count=0
for o in S.objects:
    if o.type not in {'MESH','CURVE','FONT','SURFACE','META'}:continue
    ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles()
    vs=[o.matrix_world@v.co for v in me.vertices]
    faces=[list(f.vertices) for f in me.polygons]
    trees=BVHTree.FromPolygons(vs,faces,all_triangles=False) if vs else None
    objects[o.name]=(trees,vs,faces)
    triangles+=len(me.loop_triangles);submeshes+=len({f.material_index for f in me.polygons})
    materials.update(m.name for m in me.materials if m)
    for t in me.loop_triangles:
        key=tuple(sorted(tuple(round(float(vs[i][k]),7) for k in range(3)) for i in t.vertices))
        if key in seen and seen[key]!=o.name and len(report['exact_duplicate_triangle_pairs'])<200:
            report['exact_duplicate_triangle_pairs'].append([seen[key],o.name])
        seen[key]=o.name
    bm=bmesh.new();bm.from_mesh(me)
    boundary=sum(e.is_boundary for e in bm.edges)
    nonmanifold=sum(not e.is_manifold for e in bm.edges)
    zero=sum(f.calc_area()<=1e-14 for f in bm.faces)
    if zero or (o.type=='MESH' and nonmanifold):
        report['mesh_defects'].append({'object':o.name,'type':o.type,'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'near_zero_faces':zero})
    focus=any(name=='Arrival Gate P2' or name=='CD | Office key cabinet' for name in ancestor_names(o))
    if focus and vs:
        adj=[set() for _ in vs]
        for e in me.edges:
            i,j=e.vertices;adj[i].add(j);adj[j].add(i)
        remaining=set(range(len(vs)))
        while remaining:
            start=next(iter(remaining));component={start};queue=[start];remaining.remove(start)
            while queue:
                for j in adj[queue.pop()]:
                    if j in remaining:remaining.remove(j);component.add(j);queue.append(j)
            cv=[vs[i] for i in component];mapping={index:i for i,index in enumerate(sorted(component))}
            selected_faces=[f for f in faces if f and f[0] in component]
            iv=[vs[i] for i in sorted(component)];iff=[[mapping[i] for i in f] for f in selected_faces]
            tree=BVHTree.FromPolygons(iv,iff,all_triangles=False) if iff else None
            origin=sum(iv,Vector())/len(iv)
            # Translate to a nearby origin before accumulating tiny volumes;
            # world-coordinate cross products lose precision on small keys.
            volume=sum((vs[t.vertices[0]]-origin).dot((vs[t.vertices[1]]-origin).cross(vs[t.vertices[2]]-origin))/6 for t in me.loop_triangles if t.vertices[0] in component)
            rec={'object':o.name,'ancestry':ancestor_names(o),'island':len(islands),
                 'world_bounds':box(cv),'vertices':len(cv),'faces':len(selected_faces),'signed_volume_m3':volume}
            report['focused_islands'].append(rec);islands.append((rec,tree,iv))
    bm.free();ev.to_mesh_clear();mesh_count+=1
report['counters']={'geometry_objects':mesh_count,'scene_objects':len(S.objects),'evaluated_triangles':triangles,
    'material_submeshes':submeshes,'used_material_count':len(materials),'used_material_names':sorted(materials),
    'targets':{'triangles_max':450000,'material_submeshes_max':1150,'material_families_max':36}}
# Contact witnesses originate from actual surfaces and must strike actual mesh,
# independently of support labels and joined-object ancestry.
rail=objects['P2 frame head lintel'][0]
for rec,tree,iv in islands:
    lo,hi=rec['world_bounds'];cx=(lo[0]+hi[0])/2
    if 'P2 blast leaf' not in ' '.join(rec['ancestry']):continue
    is_hanger=abs(lo[2]-3.48)<.0002 and abs(hi[2]-3.579)<.0002 and .04<hi[0]-lo[0]<.06
    is_roller=abs(lo[2]-3.52)<.0002 and abs(hi[2]-3.60)<.0002 and .07<hi[0]-lo[0]<.09
    if is_hanger:
        target=objects[next(n for n in rec['ancestry'] if n.startswith('P2 blast leaf'))][0]
        y=(lo[1]+hi[1])/2
        for dx in [-.020,0,.020]:
            point=Vector((cx+dx,y,3.48));hit=target.ray_cast(point+Vector((0,0,.01)),Vector((0,0,-1)),.03)
            report['physical_contacts'].append({'part':'hanger_foot','island':rec['island'],'point':list(point),
                'leaf_hit':list(hit[0]) if hit[0] is not None else None,'distance_from_foot_m':hit[3]-.01 if hit[0] is not None else None})
        witnesses=[];inside_samples=0;separations=[]
        # Probe the continuous neck where it crosses the real lower-web height.
        # The final track may contain a real slot; global Y bounds prove nothing.
        for z in [3.501,3.505,3.51,3.515,3.519]:
            for dx in [-.015,-.0075,0,.0075,.015]:
                for yy in [lo[1]+.0001,y,hi[1]-.0001]:
                    point=Vector((cx+dx,yy,z))
                    if not contains(tree,point):continue
                    inside_samples+=1
                    if contains(rail,point):witnesses.append(list(point))
                    nearest=rail.find_nearest(point)
                    if nearest[0] is not None:separations.append(nearest[3])
        report['physical_contacts'].append({'part':'hanger_vs_actual_rail_lower_flange','island':rec['island'],
            'actual_hanger_solid_samples':inside_samples,'actual_rail_intersection_witnesses':witnesses,
            'minimum_sampled_clearance_m':min(separations) if separations else None,
            'interpretation':'Samples test actual closed connected-island topology and actual track solid; parent ancestry and bounding boxes are not contact evidence.'})
    if is_roller:
        point=Vector((cx,(lo[1]+hi[1])/2,lo[2]));hit=rail.ray_cast(point+Vector((0,0,.01)),Vector((0,0,-1)),.03)
        report['physical_contacts'].append({'part':'roller_lower_rail_contact','island':rec['island'],'point':list(point),
            'rail_hit':list(hit[0]) if hit[0] is not None else None,'distance_from_roller_m':hit[3]-.01 if hit[0] is not None else None})
assert sha(native)==a.expected_sha,'Input changed during audit'
(HERE/'native-independent.json').write_text(json.dumps(report,indent=2)+'\n')
print('INDEPENDENT_NATIVE_PROBE',json.dumps({'revision':report['revision'],'counters':report['counters'],
    'matrix_changes':len(changed),'missing_originals':len(missing),'mesh_defect_rows':len(report['mesh_defects']),
    'dependency_defects':len(report['dependency_defects']),'physical_contacts':report['physical_contacts']}))
