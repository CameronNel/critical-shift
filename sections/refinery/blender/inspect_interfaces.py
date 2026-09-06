"""Read-only evaluated-mesh interface audit; never saves the inspected .blend."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
OUT=HERE.parent/'production'/'interface_audit.json'
if '--output' in sys.argv:OUT=Path(sys.argv[sys.argv.index('--output')+1])

def meshdata(o,dg):
    e=o.evaluated_get(dg);m=e.to_mesh()
    try:
        m.calc_loop_triangles();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(t.vertices) for t in m.loop_triangles]
        if not v or not f:return None
        bounds=[[min(p[k] for p in v) for k in range(3)],[max(p[k] for p in v) for k in range(3)]]
        return v,f,bounds,BVHTree.FromPolygons(v,f,all_triangles=True)
    finally:e.to_mesh_clear()

def intersects(a,b):return all(a[0][i]<b[1][i] and a[1][i]>b[0][i] for i in range(3))

def run():
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cache={}
    for o in bpy.context.scene.objects:
        if o.type in {'MESH','CURVE','FONT'} and not o.hide_render:
            val=meshdata(o,dg)
            if val:cache[o.name]=val
    def names(prefixes):return [n for n in cache if n.startswith(prefixes)]
    groups=[('FEEDER_CRUSHER',names(('FEEDER_',)),names(('Crusher_cast','Crusher_feed','Crusher_hood','Crusher_service','Crusher_bearing','Crusher_tooth','Crusher_control'))),
        ('FEEDER_RECEIVING',names(('FEEDER_',)),names(('Receiving_hopper','Hopper_support','Hopper_cleanout'))),
        ('CRUSHER_SORTER',names(('Crusher_discharge','Crusher_cast','Crusher_dust')),names(('Sorter_',))),
        ('SORTER_PROCESSOR',names(('Sorter_',)),names(('Processor_',))),
        ('PROCESSOR_DRYER',names(('Processor_',)),names(('Dryer_',)))]
    collisions=[]
    for group,left,right in groups:
        for a in left:
            for b in right:
                av,af,ab,at=cache[a];bv,bf,bb,bt=cache[b]
                if not intersects(ab,bb):continue
                hit=at.overlap(bt)
                if hit:
                    coords=[av[i] for ti,_ in hit for i in af[ti]]
                    collisions.append({'interface':group,'a':a,'b':b,'triangle_pairs':len(hit),
                        'a_bounds':ab,'b_bounds':bb,
                        'aabb_overlap_size':[min(ab[1][k],bb[1][k])-max(ab[0][k],bb[0][k]) for k in range(3)],
                        'intersecting_triangle_extent':[[min(p[k] for p in coords) for k in range(3)],[max(p[k] for p in coords) for k in range(3)]]})
    bays={}
    for o in bpy.context.scene.objects:
        if o.name.startswith('ROOT_'):
            meshes=[cache[c.name][2] for c in o.children_recursive if c.name in cache]
            if meshes:bays[o.name]=[[min(bb[0][k] for bb in meshes) for k in range(3)],[max(bb[1][k] for bb in meshes) for k in range(3)]]
    approaches=[]
    for o in bpy.context.scene.objects:
        if o.get('kind')!='control':continue
        p=o.matrix_world.translation;west=o.get('machine') in {'ASSEMBLY','INSPECTION','DISPATCH'}
        c=p+Vector((.65,0,0) if o.get('machine')=='RECEIVING' else (-.65,0,0) if west else (0,-.65,0))
        bb=((c.x-.25,c.y-.25,.10),(c.x+.25,c.y+.25,1.75))
        # First identify conservative operating envelope collisions; report them
        # as candidates, not verified triangle collisions or navigation failures.
        hits=[n for n,(_,_,b,_) in cache.items() if intersects(b,bb)]
        bv=[Vector((x,y,z)) for x in [bb[0][0],bb[1][0]] for y in [bb[0][1],bb[1][1]] for z in [bb[0][2],bb[1][2]]]
        bf=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
        bt=BVHTree.FromPolygons(bv,bf)
        verified=[n for n in hits if cache[n][3].overlap(bt) or any(all(bb[0][i]<p[i]<bb[1][i] for i in range(3)) for p in cache[n][0])]
        approaches.append({'control':o.name,'approach_box':bb,'evaluated_aabb_candidates':hits,'triangle_or_vertex_confirmed':verified})
    result={'source_blend':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
      'read_only':True,'saved':False,'evaluated_mesh_count':len(cache),'interface_collisions':collisions,'machine_bay_bounds':bays,'control_approach_candidates':approaches,
      'limits':['Interface collisions are actual evaluated triangle-BVH overlaps; intentional joints may overlap and need contextual interpretation.',
                'Operating boxes are conservative AABB candidate tests, not capsule or navigation acceptance.','Complete mesh containment is not detected by triangle surface intersection.']}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('INTERFACE_AUDIT',str(OUT),'triangle intersections',len(collisions),'approach candidate boxes',sum(bool(p['evaluated_aabb_candidates']) for p in approaches))
    for c in collisions:print(c['interface'],c['a'],c['b'],'pairs',c['triangle_pairs'])

run()
