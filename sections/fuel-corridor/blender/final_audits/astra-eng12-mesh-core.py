"""Independent evaluated eng12 checks. CPU only, no render or scene save.
Moving states are mathematical translations of evaluated vertex copies; scene state stays unchanged.
"""
from pathlib import Path
import bpy, hashlib, json, math, time
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
SECTION=HERE.parents[1]
SAVED=SECTION/'production/checkpoints/final-F04/blender/Fuel_Corridor.blend'
EXPECTED='a55c877781ffe1cea94b66e7598fce35204d3b76d12edd482544a08472eb362a'
assert hashlib.sha256(SAVED.read_bytes()).hexdigest()==EXPECTED
assert not bpy.data.filepath
bpy.ops.wm.open_mainfile(filepath=str(SAVED),load_ui=False)
scene=bpy.context.scene
assert scene.get('stage')=='full' and scene.get('revision')=='final-F04'
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
start=time.perf_counter()

def ancestors(o):
    while o:
        yield o
        o=o.parent

def bounds(points):
    return tuple(Vector([fn(p[a] for p in points) for a in range(3)]) for fn in [min,max])

def overlap_bounds(a,b,pad=0):
    return all(a[0][i]<=b[1][i]+pad and b[0][i]<=a[1][i]+pad for i in range(3))

def gap_bounds(a,b):
    return math.sqrt(sum(max(0,a[0][i]-b[1][i],b[0][i]-a[1][i])**2 for i in range(3)))

class Mesh:
    def __init__(self,obj,offset=None,base=None):
        self.obj=obj
        if base is not None:
            self.points=[p+offset for p in base.points]
            self.tris=base.tris
        else:
            ev=obj.evaluated_get(deps)
            me=ev.to_mesh()
            self.points=[ev.matrix_world@v.co for v in me.vertices]
            me.calc_loop_triangles()
            self.tris=[tuple(t.vertices) for t in me.loop_triangles]
            ev.to_mesh_clear()
        self.bounds=bounds(self.points)
        self.bvh=BVHTree.FromPolygons(self.points,self.tris,all_triangles=True,epsilon=0)

def inside(mesh,point):
    """Parity containment supplement; two deterministic non-axis rays agree."""
    votes=[]
    for xyz in [(0.911,.313,.269),(-.237,.927,.289)]:
        direction=Vector(xyz).normalized();origin=point.copy();count=0
        for _ in range(32):
            loc,normal,index,distance=mesh.bvh.ray_cast(origin,direction,100)
            if loc is None:break
            if distance<1e-6:return False
            count+=1;origin=loc+direction*1e-5
        votes.append(count%2==1)
    return all(votes)

def intersection(a,b):
    if not overlap_bounds(a.bounds,b.bounds):return None
    overlap_xyz=[min(a.bounds[1][i],b.bounds[1][i])-max(a.bounds[0][i],b.bounds[0][i]) for i in range(3)]
    diagnostic={'aabb_overlap_xyz_m':overlap_xyz,'a_bounds_world_m':[list(p) for p in a.bounds],
                'b_bounds_world_m':[list(p) for p in b.bounds],
                'aabb_contact_only_within_1um':min(overlap_xyz)<=1e-6}
    pairs=a.bvh.overlap(b.bvh)
    if pairs:
        ia,ib=pairs[0]
        return {'method':'evaluated_triangle_surface_overlap','triangle_pairs':len(pairs),**diagnostic,
                'first_triangle_a':[list(a.points[k]) for k in a.tris[ia]],
                'first_triangle_b':[list(b.points[k]) for k in b.tris[ib]]}
    # Surface tests miss a fully contained closed part. Sample a bounded vertex set.
    for test,container in [(a,b),(b,a)]:
        for p in test.points[::max(1,len(test.points)//8)][:9]:
            if inside(container,p):return {'method':'two_ray_containment_sample','contained_object':test.obj.name,'point':list(p),**diagnostic}
    return None








