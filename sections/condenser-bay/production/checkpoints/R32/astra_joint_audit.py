"""Independent saved chest-to-shell contact test; no rendering or saving."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
o=s.objects['CD shell'].evaluated_get(deps);me=o.to_mesh()
body=BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);o.to_mesh_clear()
rows=[]
for wall in s.objects:
    if not wall.name.startswith('CD chest wall'):continue
    o=wall.evaluated_get(deps);points=[o.matrix_world@Vector(v) for v in o.bound_box]
    lower=[min(v[i] for v in points) for i in range(3)];upper=[max(v[i] for v in points) for i in range(3)]
    for t in [.1,.5,.9]:
        x=(lower[0]+upper[0])/2;y=(lower[1]+upper[1])/2
        if 'Y' in wall.name:x=lower[0]+t*(upper[0]-lower[0])
        else:y=lower[1]+t*(upper[1]-lower[1])
        hit=body.ray_cast(Vector((x,y,6)),Vector((0,0,-1)),6)
        z=hit[0].z if hit[0] is not None else None
        rows.append({'wall':wall.name,'xy':[x,y],'wall_bottom_z':lower[2],'shell_surface_z':z,
                     'gap_m':lower[2]-z if z is not None else None,'ok':z is not None and lower[2]<=z+.005 and upper[2]>=z})
rev=str(s.get('source_revision'));root=Path(__file__).resolve().parent.parent
report={'revision':rev,'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'scope':'Twelve vertical contact probes using evaluated saved chest wall bounds and the actual shell surface. A 5mm positive gap is the maximum allowed; this is not a weld strength calculation.',
        'status':'PASS' if len(rows)==12 and all(r['ok'] for r in rows) else 'FAIL','samples':rows}
out=root/'production/validation'/rev/'chest-shell-contact.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2))
print('CHEST_SHELL_CONTACT',rev,report['status'],[(r['wall'],r['gap_m']) for r in rows],flush=True)
sys.exit(0 if report['status']=='PASS' else 1)
