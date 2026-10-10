"""Finite drive-cavity regression and every-frame retained-stroke intersection check."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=sys.argv[sys.argv.index('--')+1:];source,output=map(Path,A[:2])
bpy.ops.wm.open_mainfile(filepath=str(source));sc=bpy.context.scene;sc.frame_set(1)
def tree(o):
    return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])
failures=[];rows=[];cases=[]
for tag,x in (('A',-1.4),('B',1.4)):
    h=bpy.data.objects['BANK_'+tag+'_FIXED_HOUSING'];ht=tree(h)
    hit=ht.ray_cast(Vector((x,0,9.61)),Vector((0,0,1)),3.10)[0]
    radial=[]
    for i in range(64):
        d=Vector((math.cos(2*math.pi*(i+.5)/64),math.sin(2*math.pi*(i+.5)/64),0));p=Vector((x,0,10.6));loc,n,index,dist=ht.ray_cast(p,d,2)
        radial.append(dist if loc is not None else None)
    good=hit is None and all(r is not None and .343<r<.347 for r in radial)
    if not good:failures.append('Housing has no clear coaxial .345m service cavity: '+tag)
    g=bpy.data.objects.get('RH refine bank guide '+tag+' STEEL');gt=tree(g) if g else None
    if gt is None:failures.append('Missing fixed guide bushing: '+tag)
    guide_r=[]
    if gt:
        for i in range(64):
            d=Vector((math.cos(2*math.pi*(i+.5)/64),math.sin(2*math.pi*(i+.5)/64),0));loc,n,index,dist=gt.ray_cast(Vector((x,0,9.8)),d,.6)
            if loc is None:failures.append('Missing actual guide inner face: '+tag);break
            guide_r.append(dist)
    stem=bpy.data.objects['R2 bank '+tag+' moving bank '+tag+' stem IRON']
    if stem.parent!=bpy.data.objects['BANK_'+tag+'_MOVING']:failures.append('Stem parent changed: '+tag)
    row=dict(bank=tag,cavity_clear=good,housing_radial_min=min(r for r in radial if r is not None),housing_radial_max=max(r for r in radial if r is not None),guide_inner_min=min(guide_r) if guide_r else None,guide_inner_max=max(guide_r) if guide_r else None,poses=0,housing_surface_intersections=0,guide_surface_intersections=0,min_flange_bottom=None,max_shaft_radius_at_guide=0)
    rows.append(row);cases.append((x,stem,ht,gt,row))
for frame in range(1,481):
    sc.frame_set(frame);bpy.context.view_layer.update()
    for x,stem,ht,gt,row in cases:
        st=tree(stem);a=len(st.overlap(ht));b=len(st.overlap(gt)) if gt else 0
        row['poses']+=1;row['housing_surface_intersections']+=a;row['guide_surface_intersections']+=b
        vertices=[stem.matrix_world@v.co for v in stem.data.vertices]
        cap=[p.z for p in vertices if math.hypot(p.x-x,p.y)>.2475]
        low=min(cap);row['min_flange_bottom']=low if row['min_flange_bottom'] is None else min(low,row['min_flange_bottom'])
        shaft=[math.hypot(p.x-x,p.y) for p in vertices if 9.60<p.z<9.99]
        if shaft:row['max_shaft_radius_at_guide']=max(row['max_shaft_radius_at_guide'],max(shaft))
for row in rows:
    if row['housing_surface_intersections'] or row['guide_surface_intersections']:failures.append('Moving stem intersects fixed cavity/guide: '+row['bank'])
    if row['min_flange_bottom']<=9.94:failures.append('Moving cap enters lower guide: '+row['bank'])
    if row['guide_inner_min'] is not None and row['guide_inner_min']-row['max_shaft_radius_at_guide']<.005:failures.append('Insufficient nominal guide running clearance: '+row['bank'])
sc.frame_set(1);bpy.context.view_layer.update();grid_fits=[]
for tag,x in (('A',-1.4),('B',1.4)):
    grid=next(o for o in bpy.data.objects if o.name.startswith('R2 bank '+tag+' ') and 'rod band TRIM' in o.name)
    col=bpy.data.objects['BANK_'+tag+'_DRIVE_COLUMN'];gg=tree(grid);cc=tree(col)
    endpoints=sorted({round((grid.matrix_world@v.co).z,5) for v in grid.data.vertices if abs(math.hypot((grid.matrix_world@v.co).x-x,(grid.matrix_world@v.co).y)-.1125)<.000005})
    if len(endpoints)!=14:failures.append('Expected seven tighter central sleeves: '+tag);continue
    gaps=[];misses=0
    for z0,z1 in zip(endpoints[::2],endpoints[1::2]):
        for j in range(41):
            z=z0+.0001+(z1-z0-.0002)*j/40
            for i in range(64):
                d=Vector((math.cos(2*math.pi*i/64),math.sin(2*math.pi*i/64),0));origin=Vector((x,0,z))
                a=cc.ray_cast(origin,d,.30);b=gg.ray_cast(origin,d,.30)
                if a[0] is None or b[0] is None:misses+=1
                else:gaps.append(b[3]-a[3])
    good=not misses and bool(gaps) and .005<min(gaps)<=max(gaps)<.010
    grid_fits.append(dict(bank=tag,sleeves=7,rays=len(gaps),misses=misses,min_gap=min(gaps) if gaps else None,max_gap=max(gaps) if gaps else None,pass_check=good))
    if not good:failures.append('Central grid bore fit outside 5–10mm running clearance: '+tag)
r=dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),banks=rows,central_grid_fits=grid_fits,failures=failures,pass_check=not failures,scope='Actual housing bore/guide BVH faces, retained stem parent, evaluated rigid stem meshes in480 frame poses per bank, surface-intersection and nominal running-clearance/cap-height checks. Existing corner suspension seats are tested separately; this is not a global collision audit or arbitrary runtime stroke claim.')
output.write_text(json.dumps(r,indent=2));print('ROD_GUIDE', 'PASS' if r['pass_check'] else 'FAIL',len(failures),flush=True)
