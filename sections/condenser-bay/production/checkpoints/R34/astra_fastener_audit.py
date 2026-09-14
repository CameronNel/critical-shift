"""Measure the eight lower chest fastener stacks against their actual flanges."""
import bpy,json,hashlib,sys
from mathutils import Vector
from pathlib import Path
s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
def bounds(o):
    e=o.evaluated_get(deps);p=[e.matrix_world@Vector(v) for v in e.bound_box]
    return [min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]
flanges=[(o,*bounds(o)) for o in s.objects if o.name.startswith('CD chest flange')]
rows=[]
for washer in s.objects:
    if not washer.name.startswith('chest bolt washer'):continue
    lo,hi=bounds(washer);x,y=washer.matrix_world.translation.xy
    candidates=[(o,a,b) for o,a,b in flanges if a[0]<=x<=b[0] and a[1]<=y<=b[1]]
    assert candidates,f'No flange over {washer.name}'
    flange,flo,fhi=min(candidates,key=lambda r:abs(r[1][2]-hi[2]))
    suffix=washer.name[len('chest bolt washer'):]
    head=s.objects['chest bolt head'+suffix];shank=s.objects['chest bolt shank'+suffix]
    hlo,hhi=bounds(head);slo,shi=bounds(shank)
    gap=flo[2]-hi[2];head_gap=lo[2]-hhi[2]
    ok=abs(gap)<=.001 and abs(head_gap)<=.001 and shi[2]>=flo[2] and slo[2]<=hhi[2]
    rows.append({'washer':washer.name,'flange':flange.name,'flange_bottom_z':flo[2],
                 'washer_top_z':hi[2],'washer_to_flange_gap_m':gap,
                 'head_to_washer_gap_m':head_gap,'shank_enters_flange':shi[2]>=flo[2],
                 'shank_touches_head':slo[2]<=hhi[2],'ok':ok})
rev=str(s.get('source_revision'));root=Path(__file__).resolve().parent.parent
report={'revision':rev,'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'scope':'Eight named lower chest fastener stacks only. Evaluated saved bounds, 1mm seating tolerance; not a structural-strength test.',
        'status':'PASS' if len(rows)==8 and all(r['ok'] for r in rows) else 'FAIL','samples':rows}
out=root/'production/validation'/rev/'chest-fastener-contact.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2)+'\n')
print('CHEST_FASTENER_CONTACT',rev,report['status'],[(r['washer'],r['washer_to_flange_gap_m']) for r in rows],flush=True)
sys.exit(0 if report['status']=='PASS' else 1)
