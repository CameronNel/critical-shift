"""Read-only saved-geometry evidence; CPU only, never grants visual acceptance."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from validate import opening_clear, ray
ROOT=HERE.parent
S=bpy.context.scene
deps=bpy.context.evaluated_depsgraph_get()
cache={}

def tree(name):
    if name not in cache:
        o=S.objects.get(name)
        if not o or o.type not in {'MESH','CURVE'}: return None
        ev=o.evaluated_get(deps); me=ev.to_mesh()
        try:
            cache[name]=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],
                                            [list(f.vertices) for f in me.polygons])
        finally: ev.to_mesh_clear()
    return cache[name]

report={'revision':S.get('source_revision'),'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'process_id':__import__('os').getpid(),'scope':'Local saved geometry; no engineering rating or engine/navmesh claim.', 'checks':{}}
checks=report['checks']
# Scan the full nominal clear aperture, within 15 mm of the edge.
checks['U04_nominal_bore']=opening_clear((3,4.05,5.60),(2.47/.86,0,0),(0,1.47/.86,0),11,(0,0,1),.78)
checks['D01']=opening_clear((0,-.15,1.235),(1.96/.86,0,0),(0,0,2.31/.86),9,(0,1,0),1.0)
checks['D01']['foot_clearance_start_m']=.08
checks['D01']['note']='Clear passage above the authored sill; sill height checked separately.'
sill=S.objects.get('D01 sill nosing')
sill_top=max((sill.matrix_world@Vector(v)).z for v in sill.bound_box)
checks['D01_sill']={'ok':sill_top<=.045,'maximum_height_m':sill_top}
supports=[]
for item in json.loads(S.get('support_registry','[]')):
    anchor=S.objects.get(item['anchor']); target=tree(item['target'])
    row={**item,'ok':False}
    if anchor and target:
        p=anchor.matrix_world.translation
        hit=target.find_nearest(p)
        if hit and hit[0] is not None:
            row['surface_distance_m']=hit[3]
            row['ok']=hit[3] <= max(item['max_gap'],item['max_penetration'])+.0001
    supports.append(row)
checks['named_support_targets']={'ok':all(x['ok'] for x in supports),'items':supports}

# Conservative upright 0.8m-wide cart lane, sampled both across and along the actual lane.
# The reserved broader aisle contains workstations, so it is not claimed wholly empty.
routes=[]
for name,x0,x1,y0,y1 in [('west cart lane',-.35,.45,.05,6.25),
                        ('south crossover',.75,5.10,1.40,2.15),
                        ('north pump approach',.75,5.00,5.72,6.42),
                        ('east pull approach',6.65,8.55,2.0,6.80)]:
    failures=[]; count=0
    nx=max(2,int((x1-x0)/.16)); ny=max(2,int((y1-y0)/.16))
    for i in range(nx+1):
        for j in range(ny+1):
            x=x0+(x1-x0)*i/nx; y=y0+(y1-y0)*j/ny; count+=1
            hit,loc,obj=ray((x,y,.06),(0,0,1),2.14)
            if hit: failures.append({'xy':[x,y],'object':obj,'height_m':loc.z})
    routes.append({'route':name,'bounds_xy':[x0,x1,y0,y1],'samples':count,'ok':not failures,'failures':failures})
checks['route_headroom']={'ok':all(r['ok'] for r in routes),'routes':routes,
                         'limits':'Sampled straight standing volumes; does not certify carried-body turns or engine movement.'}
interface=json.loads((ROOT/'interface.json').read_text())
markers=[]
for entry in interface['portals']+interface['utilities']:
    o=S.objects.get(entry['marker']); error=99
    if o: error=(o.matrix_world.translation-Vector(entry['centre'])).length
    markers.append({'marker':entry['marker'],'position_error_m':error,'ok':error<.0001})
checks['interface_markers']={'ok':all(m['ok'] for m in markers),'items':markers}
images=[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]
checks['dependencies']={'ok':not images and not bpy.data.libraries,'missing_images':images,'linked_libraries':[l.filepath for l in bpy.data.libraries]}
camera_data={o.name:{'matrix':[list(row) for row in o.matrix_world],'lens':o.data.lens} for o in S.objects if o.type=='CAMERA'}
checks['fixed_cameras']={'ok':len(camera_data)==18,'cameras':camera_data}
report['status']='PASS' if all(c.get('ok',False) for c in checks.values()) else 'FAIL'
out=ROOT/'production'/'validation'/str(S.get('source_revision'))/'astra-saved-audit.json'
out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2))
print('ASTRA_SAVED_AUDIT',report['status'],str(out),flush=True)
for name,c in checks.items(): print(name,c.get('ok'),flush=True)
sys.exit(0 if report['status']=='PASS' else 1)
