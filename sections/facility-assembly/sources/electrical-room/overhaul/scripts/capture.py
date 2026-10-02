"""Read-only fixed-camera inspection; run with Blender 5.2 LTS."""
import bpy, json, sys, hashlib, argparse, time
from pathlib import Path
from mathutils import Vector

p=argparse.ArgumentParser()
p.add_argument('--out',required=True)
p.add_argument('--views',default='all')
p.add_argument('--samples',type=int,default=24)
p.add_argument('--width',type=int,default=1280)
p.add_argument('--diagnostics',action='store_true',help='Supplemental close-ups; never replace the14 formal cameras')
p.add_argument('--floor-proof',action='store_true',help='One read-only resolving floor view; never changes the saved scene')
p.add_argument('--palette-proof',action='store_true',help='Read-only damp-to-dry concrete and rough-wall detail views')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(a.out).resolve(); out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
source=Path(bpy.data.filepath)
if a.diagnostics or a.floor_proof or a.palette_proof:
    diagnostic_views=[
        ('DG01_Rescue',(3.2,3.8,1.56),(4.02,.15,1.55),32),
        ('DG02_Lead_Storage',(2.5,13.3,1.45),(4.0,16.05,.85),35),
        ('DG03_Trolley',(-2.6,1.72,1.55),(-4.45,1.8,.62),32),
        ('DG04_Meter',(-3.8,1.90,1.43),(-4.47,1.8,.93),50),
        ('DG05_Door_Glass',(-1.65,2.10,1.98),(-1.86,.30,1.95),70),
    ]
    if scene.get('electrical_floor_contact_revision'):
        diagnostic_views.append(('DG06_Service_Contact',(-1.60,3.55,.35),(-2.22,3.48,.0017),48))
    if scene.get('electrical_lead_finish_revision'):
        diagnostic_views.append(('DG07_Probe_Junction',(-3.80,1.58,1.30),(-4.30,1.88,.887),65))
    if a.floor_proof:
        diagnostic_views=[('FP01_Route_Surface',(-.72,7.40,.48),(.10,8.75,.005),38)]
    if a.palette_proof:
        diagnostic_views=[
            ('PF01_Damp_Concrete',(2.35,1.0,.48),(4.30,2.45,.005),38),
            ('PF02_Rough_Wall',(3.15,14.95,1.60),(4.90,16.38,1.35),50),
            ('PF03_Grazing_Damp_Response',(5.20,2.25,.45),(4.65,2.30,.005),40),
        ]
    for name,pos,target,lens in diagnostic_views:
        data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data)
        scene.collection.objects.link(o);o.location=pos
        o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();data.lens=lens
    if a.views=='all':a.views=','.join(v[0] for v in diagnostic_views)
def bounds(o):
    vs=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
records=[]
for o in scene.objects:
    records.append({'name':o.name,'type':o.type,'location':list(o.location),'matrix':list(sum((list(r) for r in o.matrix_world),[])),
      'bounds':bounds(o) if o.type in {'MESH','CURVE','FONT'} else None,'collections':[c.name for c in o.users_collection],
      'materials':[slot.material.name if slot.material else None for slot in o.material_slots] if hasattr(o,'material_slots') else [],'properties':{k:str(v) for k,v in o.items()}})
(out/'inspection.json').write_text(json.dumps({'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'records':records},indent=2))
scene.render.engine='CYCLES'; scene.cycles.device='CPU'
scene.render.threads_mode='FIXED';scene.render.threads=4
scene.cycles.samples=a.samples;scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.025
scene.cycles.use_denoising=True;scene.cycles.denoiser='OPENIMAGEDENOISE'
scene.cycles.max_bounces=8;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3;scene.cycles.transmission_bounces=6
scene.cycles.seed=73;scene.render.resolution_x=a.width;scene.render.resolution_y=round(a.width*9/16);scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.use_file_extension=True
views=sorted([o for o in scene.objects if o.type=='CAMERA'],key=lambda o:o.name)
if a.views!='all': views=[o for o in views if o.name in a.views.split(',')]
else:views=[o for o in views if o.name.startswith(('C','W'))]
manifest={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'embedded_python':sys.version,'samples':a.samples,'resolution':[scene.render.resolution_x,scene.render.resolution_y],'renderer':'Cycles CPU','purpose':'Read-only palette surface resolving views' if a.palette_proof else 'Read-only floor surface resolving view' if a.floor_proof else 'Supplemental diagnostic close-ups' if a.diagnostics else 'Fixed formal review views','views':[]}
for o in views:
    scene.camera=o;scene.render.filepath=str(out/(o.name+'.png'));start=time.time()
    bpy.ops.render.render(write_still=True)
    manifest['views'].append({'camera':o.name,'matrix':list(sum((list(r) for r in o.matrix_world),[])),'lens':o.data.lens,'seconds':time.time()-start,'sha256':hashlib.sha256(Path(scene.render.filepath).read_bytes()).hexdigest()})
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2));print('CAPTURE_DONE',o.name,flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['source_sha256']
import os
sys.stdout.flush();sys.stderr.flush();os._exit(0)
