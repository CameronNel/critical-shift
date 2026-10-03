import bpy,json,hashlib,math,sys,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation')
P=ROOT/'revamp-review/production'
OUT=Path('/tmp/medical15-technical')
verifier=ROOT/'verify_overhaul.py'
code=verifier.read_text().replace("(P/'dependency-manifest.json')", "(REPORT_DIR/'dependency-manifest.json')").replace("(P/('cold-verification.json' if '--cold' in sys.argv else 'objective-verification.json'))", "(REPORT_DIR/('cold-verification.json' if '--cold' in sys.argv else 'objective-verification.json'))")
namespace={'__file__':str(verifier),'__name__':'__main__','REPORT_DIR':OUT}
sys.argv += ['--cold','--dependencies']
exec(compile(code,str(verifier),'exec'),namespace)
scene=bpy.data.scenes['REANIMATION_EDIT_LOCAL'];bpy.context.window.scene=scene
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
baseline=json.loads((ROOT/'revamp-review/baseline.json').read_text());registry=json.loads((P/'support-registry.json').read_text())
base_names={r['name'] for r in baseline['objects']}
objects={};geometries={}
for o in scene.objects:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    bounds=[[min(c[i] for c in bb) for i in range(3)],[max(c[i] for c in bb) for i in range(3)]] if bb else None
    rec={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'dimensions':list(o.dimensions),'bounds':bounds,'location':list(o.matrix_world.translation),'hidden':o.hide_render,'collections':[c.name for c in o.users_collection],'inherited':o.name in base_names,'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else [],'mesh':o.data.name if o.type=='MESH' else None,'custom_properties':{k:str(o[k]) for k in o.keys()}}
    if o.type=='MESH':
        ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles()
        vertices=[o.matrix_world@v.co for v in me.vertices]
        faces=[tuple(t.vertices) for t in me.loop_triangles]
        if vertices and faces:
            geometries[o.name]=(vertices,faces,BVHTree.FromPolygons(vertices,faces,all_triangles=True))
        rec['vertices']=len(me.vertices);rec['triangles']=len(me.loop_triangles)
        rec['uv_layers']=[u.name for u in me.uv_layers]
        rec['mesh_material_count']=len(me.materials)
        rec['uv_finite']=all(math.isfinite(x) for uv in me.uv_layers for d in uv.data for x in d.uv)
        ev.to_mesh_clear()
    objects[o.name]=rec
(OUT/'inventory.json').write_text(json.dumps(objects,indent=2))
# AABB connection is a conservative screen: disconnected boxes prove detachment;
# connected boxes never constitute evidence of a physical support path.
names=list(geometries);parents=list(range(len(names)))
def root(i):
    while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
    return i
def near(a,b,tol=.005):return all(a['bounds'][0][k]<=b['bounds'][1][k]+tol and b['bounds'][0][k]<=a['bounds'][1][k]+tol for k in range(3))
edges=[]
for i in range(len(names)):
    for j in range(i):
        if near(objects[names[i]],objects[names[j]]):
            parents[root(i)]=root(j);edges.append((names[i],names[j]))
clusters={}
for i,n in enumerate(names):clusters.setdefault(root(i),[]).append(n)
(OUT/'aabb-clusters.json').write_text(json.dumps({'tolerance_m':.005,'clusters':sorted(clusters.values(),key=len,reverse=True),'bounds_overlap_edges':len(edges),'scope':'Mesh objects in editable room only; connected bounds do not prove contact.'},indent=2))
# Registered paths terminate at inherited hosts. Each terminal needs actual architecture proof.
paths={}
for r in registry:paths.setdefault(r['object'],[]).append(r['target'])
def terminals(n,seen=()):
    if n in seen:return ['CYCLE:'+n]
    if n in paths:return sorted(set(v for p in paths[n] for v in terminals(p,seen+(n,))))
    return [n]
terms=sorted(set(v for n in paths for v in terminals(n)))
(OUT/'registered-terminal-hosts.json').write_text(json.dumps({'registered_objects':len(paths),'terminals':terms,'registered_paths':paths},indent=2))
# Bounded proximity/contact diagnostic for the declared terminal hosts. Sample
# full vertices, triangle centroids and edge midpoints, then both directions.
def contact(a,b):
    av,af,at=geometries[a];bv,bf,bt=geometries[b]
    best=(math.inf,None,None)
    for vs,fs,tree,rev in [(av,af,bt,False),(bv,bf,at,True)]:
        # Vertices and face centroids capture most bearings; edge midpoints
        # are included to reduce false gaps across coarse triangulation.
        points=list(vs)
        points.extend((vs[f[0]]+vs[f[1]]+vs[f[2]])/3 for f in fs)
        es={tuple(sorted((f[k],f[(k+1)%3]))) for f in fs for k in range(3)}
        points.extend((vs[i]+vs[j])/2 for i,j in es)
        for v in points:
            p,no,index,d=tree.find_nearest(v)
            if d is not None and d<best[0]:best=(d,list(p) if rev else list(v),list(v) if rev else list(p))
    overlaps=at.overlap(bt)
    return {'minimum_sampled_distance_m':best[0],'point_on_a':best[1],'point_on_b':best[2],'triangle_intersections':len(overlaps),'qualification':'Closest sampled vertices, edge midpoints and triangle centroids in both directions; intersection count from evaluated BVH; no parental/AABB support assumption.'}
proximity={}
for term in terms:
    if term not in geometries:continue
    candidates=[n for n in names if n!=term and near(objects[term],objects[n])]
    rows=[]
    for n in candidates:
        c=contact(term,n)
        if c['minimum_sampled_distance_m']<=.005 or c['triangle_intersections']:
            rows.append({'other':n,**c})
    proximity[term]=sorted(rows,key=lambda x:x['minimum_sampled_distance_m'])
    print('TERMINAL_AUDIT',term,len(rows),flush=True)
(OUT/'terminal-contacts.json').write_text(json.dumps(proximity,indent=2))
print('INDEPENDENT_AUDIT_COMPLETE',len(objects),len(geometries),len(clusters),len(terms),flush=True)
