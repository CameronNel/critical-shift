"""Check actual saved wall openings through every enclosure layer.

A skin Boolean can leave structural steel across a pipe core. Test the core
and sleeve clearance independently against evaluated owned enclosure meshes.
Run with rh_stage_runner.py -- rh_wall_bore_audit.py SCENE REPORT.
"""
import bpy,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
args=sys.argv[sys.argv.index('--')+1:]
scene_path=Path(args[0]);report_path=Path(args[1])
bpy.ops.wm.open_mainfile(filepath=str(scene_path))
dg=bpy.context.evaluated_depsgraph_get();trees=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH' or not any(obj.name.startswith('RH walls '+group+' ') for group in ('mass','concrete','cladding','steel')):continue
    ev=obj.evaluated_get(dg);mesh=ev.to_mesh()
    tree=BVHTree.FromPolygons([obj.matrix_world@v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons],all_triangles=False)
    trees.append((obj.name,tree));ev.to_mesh_clear()
ports=[('EC vent',(5,-10.8,3.9),(0,1,0),.085),('EC-A drain',(3.3,-10.8,1.05),(0,1,0),.038),('EC-B drain',(1.8,-10.8,1.05),(0,1,0),.038),('turbine steam',(10.8,-3.8,6.4),(-1,0,0),.088),('turbine exhaust',(10.8,-3.3,1.15),(-1,0,0),.11),('waste vent',(8.1,8.7,5.2),(-.707,-.707,0),.03),('bank A service',(2.9,10.8,8.9),(0,-1,0),.057),('bank B service',(-5.4,10.8,8.9),(0,-1,0),.057)]
rows=[]
for name,point,direction,radius in ports:
    p=Vector(point);d=Vector(direction).normalized();u=d.cross(Vector((0,0,1))).normalized();v=d.cross(u);hits=[];rays=0
    for r in (0,radius*.98,(radius*1.55+.015)*.99):
        for i in range(1 if r==0 else 32):
            a=i*2*math.pi/32;q=p+(u*math.cos(a)+v*math.sin(a))*r;rays+=1
            for obj,tree in trees:
                loc,normal,index,distance=tree.ray_cast(q-d*1.5,d,3)
                if loc is not None:hits.append({'object':obj,'point':list(loc),'radius':r})
    rows.append({'name':name,'rays':rays,'hits':hits,'pass':not hits})
report={'source':str(scene_path),'sha256':hashlib.sha256(scene_path.read_bytes()).hexdigest(),'scope':'Eight active service cores and sleeve envelopes against evaluated owned concrete, mass, cladding and steel enclosure layers','ports':rows,'all_pass':all(row['pass'] for row in rows)}
report_path.write_text(json.dumps(report,indent=2)+'\n')
print('WALL_BORES', 'PASS' if report['all_pass'] else 'FAIL', 'ports',len(rows),'blocked',sum(len(row['hits']) for row in rows),flush=True)
if not report['all_pass']:raise RuntimeError('Saved enclosure still obstructs service cores or sleeves')
