"""Read-only measurements of the saved, consolidated F15 source."""
import bpy, hashlib, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOM=Path(__file__).resolve().parents[3]
SOURCE=ROOM/'module_overhaul_R1.blend'
EXPECTED='d2514e668ea2b24e8b4ede6bde870e12f10c1afd6d6e1892b12c016266bd7b35'
sha=lambda:hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert sha()==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False)
scene=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=scene
bpy.context.view_layer.update()
def vertices(o):return [o.matrix_world@v.co for v in o.data.vertices]
def tree(o):return BVHTree.FromPolygons(vertices(o),[list(f.vertices) for f in o.data.polygons],all_triangles=False)
mast=tree(scene.objects['G1 guide tower east'])
metal=scene.objects['CD | Joined G1 Cart Bypass Gate / steel']
world=vertices(metal);guides=[]
for label,ylo,yhi,d in [('front',6.7575,6.83,1),('rear',7.17,7.2425,-1)]:
    faces=[list(f.vertices) for f in metal.data.polygons
           if all(2.91999<=world[i].x<=3.12001 and ylo-.00001<=world[i].y<=yhi+.00001
                  and .92999<=world[i].z<=1.07001 for i in f.vertices)]
    assert faces,'No actual saved guide heel triangles'
    shoe=BVHTree.FromPolygons(world,faces,all_triangles=False)
    p=Vector((3.02,yhi if d==1 else ylo,1));direction=Vector((0,d,0))
    a=shoe.ray_cast(p+direction*.02,-direction,.06)
    b=mast.ray_cast(p-direction*.02,direction,.06)
    assert a[0] is not None and b[0] is not None
    gap=(b[0]-a[0]).dot(direction)
    assert abs(gap)<.000025,(label,gap)
    guides.append(dict(label=label,actual_shoe_hit=list(a[0]),actual_mast_hit=list(b[0]),actual_gap_m=gap,selected_actual_faces=len(faces)))
rollers=[]
for o in scene.objects:
    if not o.name.startswith('Conveyor roller ') or o.type!='MESH':continue
    points=vertices(o);layer=o.data.uv_layers['CD_Physical_1m'];ratios=[];bad=[]
    for f in o.data.polygons:
        loops=list(f.loop_indices)
        for i,j in zip(loops,loops[1:]+loops[:1]):
            a,b=[o.data.loops[k].vertex_index for k in [i,j]]
            length=(points[a]-points[b]).length
            if length<.0001:continue
            ratio=(layer.data[i].uv-layer.data[j].uv).length/length;ratios.append(ratio)
            if abs(ratio-1)>.01:bad.append(dict(face=f.index,edge=[a,b],ratio=ratio))
    assert not bad,(o.name,bad[:3])
    rollers.append(dict(object=o.name,all_face_edge_min_ratio=min(ratios),all_face_edge_max_ratio=max(ratios),bad_edges=bad))
assert len(rollers)==29
assert sha()==EXPECTED
Path(__file__).with_suffix('.json').write_text(json.dumps(dict(source_sha256=EXPECTED,source_unchanged=True,scene_mutated=False,native_written=False,scope='Saved consolidated guide bearing and all29roller physical-edge checks; not visual acceptance or exhaustive support certification',guide_bearings=guides,rollers=rollers),indent=2)+'\n')
print('SAVED_GUIDE_AND_29_ROLLER_METRIC_PASS',flush=True)
