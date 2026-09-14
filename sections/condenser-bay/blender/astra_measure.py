"""Saved evaluated geometry measurements and a local plan, CPU only."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent;s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
def box(names):
    points=[]
    for name in names:
        o=s.objects[name].evaluated_get(deps)
        points.extend(o.matrix_world@Vector(v) for v in o.bound_box)
    return {'min':[min(v[i] for v in points) for i in range(3)],'max':[max(v[i] for v in points) for i in range(3)]}
def names(prefix):return [o.name for o in s.objects if o.type=='MESH' and o.name.startswith(prefix)]
measure={}
for label,prefix in [('CD shell','CD shell'),('Hotwell','CD hotwell'),('WB west','WB west body'),('WB east','WB east body'),
                     ('CEP-A','CEP-A skid'),('CEP-B','CEP-B skid'),('Ejector','EJ skid'),('Operator','OP desk'),
                     ('Stair 1','stair1 tread'),('Stair 2','stair2 tread'),('Landing','mid landing'),
                     ('Gallery east','gallery east'),('Gallery west','gallery west'),('Gallery north','gallery north')]:
    if names(prefix):measure[label]=box(names(prefix))
walls={n:box([n]) for n in ['WestWall','EastWall','NorthWall','SouthWall header','Ceiling slab','Structural floor']}
inner={'x0':walls['WestWall']['max'][0],'x1':walls['EastWall']['min'][0],
       'y0':walls['SouthWall header']['max'][1],'y1':walls['NorthWall']['min'][1],
       'z0':walls['Structural floor']['max'][2],'z1':walls['Ceiling slab']['min'][2]}
report={'revision':s.get('source_revision'),'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'method':'Evaluated saved object bounding boxes in world metres, with object names retained in authoring source.',
        'inner_room':inner,'equipment':measure,'walls':walls}
out=ROOT/'production/validation'/str(s.get('source_revision'));out.mkdir(parents=True,exist_ok=True)
(out/'saved-measurements.json').write_text(json.dumps(report,indent=2))
scale=58;ox=80-inner['x0']*scale;oy=90+inner['y1']*scale
def rect(b,fill,stroke,dash=''):
    a,c=b['min'],b['max'];return f'<rect x="{ox+a[0]*scale:.2f}" y="{oy-c[1]*scale:.2f}" width="{(c[0]-a[0])*scale:.2f}" height="{(c[1]-a[1])*scale:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" {dash}/>'
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="800" viewBox="0 0 1120 800" font-family="Segoe UI,Arial,sans-serif">',
     '<rect width="1120" height="800" fill="#f1eee5"/>',
     '<text x="60" y="38" font-size="22" fill="#252a30">TURBINE CONDENSER BAY — SAVED GEOMETRY PLAN</text>',
     f'<text x="60" y="63" font-size="14" fill="#555">Revision {s.get("source_revision")} · local metres · +Y up on plan · no remote bind or engineering rating</text>',
     rect({'min':[inner['x0'],inner['y0'],0],'max':[inner['x1'],inner['y1'],0]},'#dedbd1','#222')]
for label,b in measure.items():
    if label in ['Hotwell','Landing']:continue
    gallery=label.startswith('Gallery');fill='none' if gallery else '#b76e40' if label.startswith('CEP') else '#b6b7af'
    svg.append(rect(b,fill,'#61746d' if gallery else '#454b51','stroke-dasharray="5 3"' if gallery else ''))
    if not gallery:
        x=ox+(b['min'][0]+b['max'][0])*scale/2;y=oy-(b['min'][1]+b['max'][1])*scale/2
        size=9 if label.startswith('WB ') else 10 if label=='Operator' else 12
        svg.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="middle" fill="#222">{label}</text>')
svg.append(rect({'min':[-.35,-.70,0],'max':[.45,6.20,0]},'none','#a58128','stroke-dasharray="8 4"'))
svg.append(rect({'min':[1.75,3.3,0],'max':[4.25,4.8,0]},'none','#843d35','stroke-dasharray="3 3"'))
lines=['LOCAL FRAME','11.40 × 9.40 × 6.00 m','D01 = (0, 0, 0)','Turbine = local + (1.6, 7.4, −6.0)','','U04 RECTANGULAR RECEIVE','Centre (3.00, 4.05, 6.00)','2.50 m X × 1.50 m Y throat','','GALLERY / DASHED GREEN','Deck datum z = 3.90 m','Walking surface ≈ 3.94 m','0.90 m nominal deck widths','','STRAIGHT CART / DASHED OCHRE','0.80 × 2.20 × 1.60 m body','Delivery centre ends y = 5.10','Reverses to exit; no turn claimed','','SCOPED VALIDATION','See same-revision saved audit','and independent warm/cold review.']
for i,t in enumerate(lines):svg.append(f'<text x="795" y="{115+i*24}" font-size="14" fill="#30363b">{t}</text>')
svg += [f'<rect x="{ox-scale}" y="{oy-2}" width="{2*scale}" height="4" fill="#dedbd1"/>',
        f'<text x="{ox}" y="{oy+25}" font-size="11" text-anchor="middle">D01 / 2.00 m</text>',
        '<text x="12" y="363" font-size="12">9.40 m Y</text>',
        '<text x="310" y="720" font-size="16">11.40 m clear X</text>',
        '<text x="55" y="765" font-size="13">Solid footprints from evaluated saved meshes. Dashed overlays identify upper gallery / aperture / disclosed cart delivery.</text>','</svg>']
(ROOT/'architecture/floorplan.svg').write_text('\n'.join(svg))
print('SAVED_MEASUREMENTS',json.dumps(inner),flush=True)
