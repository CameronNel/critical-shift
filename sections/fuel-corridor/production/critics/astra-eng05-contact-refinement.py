"""Resolve a numerically missed spacer contact without changing the scene."""
from pathlib import Path
import runpy,json
HERE=Path(__file__).resolve().parent
c=runpy.run_path(str(HERE/'astra-eng05-mesh-core.py'))
Mesh,scene,Vector=c['Mesh'],c['scene'],c['Vector']
pairs=[('Bypass_isolation_termination_spacer.001','Bypass_isolation_termination.001'),
       ('Clean_blade_panel','Clean_blade_drop'),('Clean_blade_panel','Clean_blade_drop.001')]
out=[]
for an,bn in pairs:
    a,b=[Mesh(scene.objects[n]) for n in [an,bn]]
    witnesses=[]
    for source,target in [(a,b),(b,a)]:
        for p in source.points:
            q,normal,index,d=target.bvh.find_nearest(p)
            if q is not None:witnesses.append({'source':source.obj.name,'target':target.obj.name,'point':list(p),'nearest':list(q),'distance_m':d})
    out.append({'a':an,'b':bn,'nearest_vertex_surface_witness':min(witnesses,key=lambda x:x['distance_m']),
                'a_bounds':[list(p) for p in a.bounds],'b_bounds':[list(p) for p in b.bounds],
                'triangle_overlap':c['intersection'](a,b)})
r={'revision':'eng05','blend_sha256':c['EXPECTED'],'pairs':out,'no_save_render_or_mutation':True}
(HERE/'astra-eng05-contact-refinement.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
