"""Saved-scene swept player/cart envelopes; supplementary evidence, not engine physics."""
import bpy,json,sys,math,hashlib
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from validate import Validator
v=Validator(SimpleNamespace(revision=None,out=None,strict_exit=False));v.evaluated_geometry()
routes={
 'CP-P01 main cart return':{'half':[.60,.85],'path':[(0,.86),(0,11.5),(0,.86)]},
 'P-01 controls and front service':{'half':[.30,.30],'path':[(0,2.35),(-4.7,2.35),(-2.0,2.35),(0,2.35)]},
 'P-02 between-pump service':{'half':[.30,.30],'path':[(0,5.85),(-4.6,5.85),(0,5.85)]},
 'CP-D02 workshop and bench':{'half':[.30,.30],'path':[(0,9.25),(-4.1,9.25),(-4.1,10.6),(-3.5,11.8),(-4.3,11.8),(-3.5,11.8),(-4.1,10.6),(-4.1,9.25),(0,9.25)]},
 'HX-01 aisle service':{'half':[.30,.30],'path':[(0,3.4),(1.65,3.4),(1.65,12.25),(0,12.25)]},
 'HX-01 withdrawal bay':{'half':[.30,.30],'path':[(0,11.7),(3.45,11.7),(3.45,9.85),(3.45,11.7),(0,11.7)]},
 'CP-RESERVE and CP-MINE-WATER':{'half':[.30,.30],'path':[(0,1.05),(4.25,1.05),(4.25,3.5),(0,3.5)]},
 'secondary rear service access':{'half':[.30,.30],'path':[(3.45,11.7),(4.96,11.7),(4.96,9.2),(5.13,9.2),(5.13,6.3),(5.13,9.2),(4.96,9.2),(4.96,11.7),(3.45,11.7)]},
}
out={'revision':bpy.context.scene.get('revision'),'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'method':'Every <=0.12m along polylines: evaluated-world triangle clipping against conservative upright player/cart box. Floor paint <=10mm excluded. Eye 1.68m, player height1.85m, cart envelope2.0m. No real-time game engine or dynamic door simulation.','routes':[]}
for name,spec in routes.items():
    hits=[];count=0
    for a,b in zip(spec['path'],spec['path'][1:]):
        dist=math.dist(a,b);n=max(1,math.ceil(dist/.12))
        for step in range(n+1):
            t=step/n;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
            bb=(Vector((x-spec['half'][0],y-spec['half'][1],.012)),Vector((x+spec['half'][0],y+spec['half'][1],2.0 if 'cart' in name else 1.85)))
            count+=1
            for mesh in v.meshes.values():
                if v.is_flush(mesh):continue
                witness=mesh.volume_intersection(bb)
                if witness:hits.append({'at':[x,y],'object':mesh.obj.name,**witness})
    # Preserve first witness per object, plus total hit count.
    unique={h['object']:h for h in hits}
    out['routes'].append({'id':name,'path_xy':spec['path'],'footprint_m':[2*x for x in spec['half']],'sample_count':count,'collision_samples':len(hits),'clashing_objects':list(unique.values()),'status':'FAIL' if hits else 'PASS'})
out['status']='PASS' if all(r['status']=='PASS' for r in out['routes']) else 'FAIL'
p=HERE.parent/'production/technical'/f"{out['revision']}-walkthrough.json";p.write_text(json.dumps(out,indent=2))
print('WALK_AUDIT '+json.dumps({'status':out['status'],'routes':[(r['id'],r['status'],len(r['clashing_objects'])) for r in out['routes']]}))
