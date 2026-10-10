"""Check every leaf-facing part and each grip/barrel support chain, on saved geometry."""
import bpy,json,hashlib,sys,math
from collections import Counter
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from rh_door_hardware_seats import components,frame
from r2lib import WALLS

def tree(o,inds=None):
    ids=list(range(len(o.data.vertices))) if inds is None else inds
    index={old:new for new,old in enumerate(ids)}
    vs=[o.matrix_world@o.data.vertices[i].co for i in ids]
    fs=[tuple(index[i] for i in p.vertices) for p in o.data.polygons if all(i in index for i in p.vertices)]
    return BVHTree.FromPolygons(vs,fs),vs

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if args and Path(args[0]).suffix=='.blend':
    bpy.ops.wm.open_mainfile(filepath=args[0]);args=args[1:]
assert len(args)<=1 and (not args or Path(args[0]).suffix=='.json'), 'Expected scene.blend and optional output.json'
records=json.loads(bpy.context.scene.get('rh_door_hardware_seats','[]'));assert len(records)==36
rows=[];failures=[];leaves={}
for r in records:
    o=bpy.data.objects[r['subject']];leaf=bpy.data.objects[r['leaf']];lt,_=tree(leaf);ct,vs=tree(o,r['vertices'])
    samples=vs+[sum((o.matrix_world@o.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices) for p in o.data.polygons if all(i in set(r['vertices']) for i in p.vertices)]
    gap=min(lt.find_nearest(p)[3] for p in samples);overlap=len(ct.overlap(lt))
    anchor_errors=[ct.find_nearest(Vector(p))[3] for p in r['anchors']]
    ok=gap<=.0015 and overlap>0 and max(anchor_errors)<=.0007
    row={'leaf':leaf.name,'role':r['role'],'component':r['component'],'nearest_leaf_m':gap,'intersections':overlap,'rear_bearing_anchor_error_m':max(anchor_errors),'pass':ok};rows.append(row)
    if not ok:failures.append(row)
    leaves.setdefault(leaf.name,[]).append(r)
connections=[]
for name,rs in leaves.items():
    steel=bpy.data.objects[rs[0]['subject']];wi=rs[0]['wall_index'];w=WALLS[wi];parts=components(steel.data);claimed={r['component'] for r in rs};free=[i for i in range(len(parts)) if i not in claimed];assert len(free)==1,(name,free)
    grip,_=tree(steel,parts[free[0]])
    for r in rs:
        if r['role']!='handle stem':continue
        t,_=tree(steel,r['vertices']);pairs=len(t.overlap(grip));connections.append({'leaf':name,'joint':'stem to grip','intersections':pairs,'pass':pairs>0})
    galv=bpy.data.objects['RH refine door hardware '+name+' GALV'];barrels=components(galv.data);assert len(barrels)==3
    plates=[r for r in rs if r['role']=='hinge plate']
    for inds in barrels:
        z=sum((galv.matrix_world@galv.data.vertices[i].co).z for i in inds)/len(inds)
        r=min(plates,key=lambda r:abs(sum((steel.matrix_world@steel.data.vertices[i].co).z for i in r['vertices'])/len(r['vertices'])-z))
        a,_=tree(galv,inds);b,_=tree(steel,r['vertices']);pairs=len(a.overlap(b));connections.append({'leaf':name,'joint':'barrel to hinge plate','intersections':pairs,'pass':pairs>0})
failures += [r for r in connections if not r['pass']]
assert len(leaves)==6 and len(connections)==30
topology=[]
for name,rs in leaves.items():
    o=bpy.data.objects[rs[0]['subject']];mesh=o.data;parts=components(mesh)
    usage=Counter(tuple(sorted(e)) for p in mesh.polygons for e in p.edge_keys)
    bad_edges=sum(usage[tuple(sorted(e.vertices))]!=2 for e in mesh.edges)
    mesh.calc_loop_triangles();component={v:ci for ci,inds in enumerate(parts) for v in inds}
    # Use a local origin for each volume sum to avoid cancellation at distant walls.
    origins=[o.matrix_world@mesh.vertices[inds[0]].co for inds in parts]
    volumes=[0. for _ in parts];degenerate=0
    for tri in mesh.loop_triangles:
        ci=component[tri.vertices[0]]
        a,b,c=[o.matrix_world@mesh.vertices[i].co-origins[ci] for i in tri.vertices]
        area=(b-a).cross(c-a).length*.5
        degenerate+=int(not math.isfinite(area) or area<1e-12)
        volumes[ci]+=a.dot(b.cross(c))/6
    ok=bad_edges==0 and degenerate==0 and len(parts)==7 and all(v>1e-10 for v in volumes)
    row={'subject':o.name,'components':len(parts),'edges_not_used_twice':bad_edges,'degenerate_triangles':degenerate,'component_signed_volume_m3':volumes,'pass':ok}
    topology.append(row)
failures += [r for r in topology if not r['pass']]
report={'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'leaf_count':6,'leaf_facing_parts':rows,'support_connections':connections,'mesh_topology':topology,'failures':failures,'pass_check':not failures,'scope':'36 owned leaf-facing parts and 30 specific stem/grip or barrel/plate triangle-intersection joints; shallow 0.5 mm mounting seats. Six changed meshes must have seven closed positive-volume components and no degenerate triangles. Does not require standoff grips or hinge barrels to touch the leaf directly. Not an exhaustive scene collision test.'}
if args:Path(args[0]).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True);print('RESULT: '+('PASS' if report['pass_check'] else 'FAIL'),flush=True)
if failures:raise SystemExit(1)
