"""Check crane travel against fixed structure and its installed running rails.

Run via rh_stage_runner.py -- rh_motion_audit.py CANDIDATE OUTPUT.json.
Triangle intersections are evidence, including small penetrations; they are
not silently classified as intended contacts. This does not certify all props.
"""
import bpy, sys, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

args=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=args[0])
scene=bpy.context.scene
scene.frame_set(1)
moving=[o for o in bpy.data.objects if o.type=='MESH' and
        o.name.startswith(('R2 crane bridge ','R2 crane trolley ','RH refine crane bridge ',
                           'RH refine crane hoist rope ', 'RH refine main hook ','RH refine bridge web light mount ',
                           'RH refine bridge web service ','RH refine running gear lamp ',
                           'RH refine running gear service ','RH refine hook inspection '))]
fixed=[o for o in bpy.data.objects if o.type=='MESH' and
       o.name.startswith(('RH walls girders ', 'RH walls roof posts ',
                          'RH walls roof braces ', 'RH walls roof enclosure ',
                          'RH refine roof shaft ', 'RH refine roof bay ', 'RH refine circulation ceiling rail ',
                          'RH refine roof utility ',
                          'RF BATCH structure ',
                          'RF BATCH services ', 'RF BATCH skylights ',
                          'RH pool runway ', 'RH pool girder '))]
def tree(o):
    mesh=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    points=[o.matrix_world@v.co for v in mesh.vertices]
    polygons=[list(p.vertices) for p in mesh.polygons]
    o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
    return BVHTree.FromPolygons(points,polygons,all_triangles=False)
fixed_trees={o.name:tree(o) for o in fixed}
findings=[]
bridge=bpy.data.objects['R2 crane bridge crane OLIVE']
trolley=bpy.data.objects['R2 crane trolley crane IRON']
rail=bpy.data.objects['R2 crane rails crane TRIM']
rail_points=[rail.matrix_world@Vector(v) for v in rail.bound_box]
rail_min=min(p.y for p in rail_points); rail_max=max(p.y for p in rail_points)
# Evaluate every integer pose for wheel containment and dense inspection
# poses for triangle collision. Include every turning-point keyframe.
poses=sorted(set(range(1,901,30))|{1,150,225,300,450,600,900})
for frame in range(1,901):
    scene.frame_set(frame)
    dy=bridge.matrix_world.translation.y
    for y in (4.25+dy,4.95+dy):
        if y-.19<rail_min or y+.19>rail_max:
            findings.append(dict(frame=frame,kind='wheel outside runway',y=y))
    if frame not in poses: continue
    for o in moving:
        current=tree(o)
        for name,target in fixed_trees.items():
            overlaps=current.overlap(target)
            if overlaps:
                findings.append(dict(frame=frame,kind='triangle intersection',
                                     moving=o.name,fixed=name,pairs=len(overlaps)))
    print('motion pose',frame,'findings',len(findings),flush=True)
scene.frame_set(1)
report=dict(source=args[0],wheel_poses=900,collision_poses=poses,
            fixed_objects=list(fixed_trees),moving_objects=[o.name for o in moving],
            findings=findings,pass_check=not findings,
            scope='Main crane against listed roof and pool-crane structures; whole-room clearance remains separate.')
Path(args[1]).write_text(json.dumps(report,indent=2))
print('MOTION PASS' if not findings else 'MOTION FAIL',len(findings),flush=True)
