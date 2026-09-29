"""Fresh-open verification and final CPU gallery. No scene writes."""
import bpy,bmesh,ast,hashlib,json,ctypes,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/refinery-build'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report=json.loads((OUT/'build-verification.json').read_text());src=Path(bpy.data.filepath);assert sha(src)==report['saved_sha256']
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
tree=ast.parse(Path(__file__).with_name('build_transition_courtyard.py').read_text());fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='fingerprint');exec(compile(ast.Module(body=[fun],type_ignores=[]),'<audit>','exec'))
objects={o.name_full:o for o in s.objects};changed=[n for n,h in report['protected_fingerprints'].items() if n not in objects or fingerprint(objects[n])!=h]
assert not changed,changed
badlibs=[p for p,h in report['libraries'].items() if not Path(p).exists() or sha(p)!=h];assert not badlibs,badlibs
missing=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath and not im.packed_file and not Path(bpy.path.abspath(im.filepath,library=im.library)).exists():missing.append(im.name)
assert not missing,missing
dg=bpy.context.evaluated_depsgraph_get();floors=[]
for p in report['route_samples']:
 x,y=p['xy'];hit,co,n,f,o,m=s.ray_cast(dg,Vector((x,y,.27)),Vector((0,0,-1)),distance=.65)
 floors.append(dict(route=p['route'],xy=p['xy'],floor=round(co.z,5) if hit else None,object=o.name if hit else None))
gaps=[v for v in floors if v['floor'] is None];assert not gaps,gaps
audit=dict(source_sha256=sha(src),protected_objects_checked=len(report['protected_fingerprints']),protected_changes=changed,missing_libraries=badlibs,missing_images=missing,floor_samples=floors,floor_gaps=gaps,new_route_blockers=report['new_route_blockers'],removed_pavilion_components=13,runtime_collision_navigation='not tested')
(OUT/'cold-open.json').write_text(json.dumps(audit,indent=2));print('REFINERY_COLD_READBACK',len(floors),flush=True)
manifest=dict(source=str(src),source_sha256=sha(src),settings=dict(engine='CYCLES',device='CPU',threads=1,resolution=[1280,720],denoiser='CPU OIDN',seed=73),views=[],complete=False)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
# Repeat first view under the build worker's identical settings, compare decoded pixels.
s.camera=bpy.data.objects['RFX CAMERA | 01_SW'];s.render.filepath=str(OUT/'cold-repeat.png');bpy.ops.render.render(write_still=True)
def pixels(p):
 im=bpy.data.images.load(str(p),check_existing=False);a=np.empty(len(im.pixels),np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);return a.reshape(-1,4)
a=pixels(OUT/'01_SW.png');b=pixels(OUT/'cold-repeat.png');d=np.abs(a-b)
audit.update(changed_pixels=int(np.any(d>0,axis=1).sum()),max_channel_difference=float(d.max()),mean_channel_difference=float(d.mean()),source_unchanged=sha(src)==report['saved_sha256'])
(OUT/'cold-open.json').write_text(json.dumps(audit,indent=2))
manifest['views'].append(dict(name='01_SW',path=str(OUT/'01_SW.png'),sha256=sha(OUT/'01_SW.png'),samples=8,camera='RFX CAMERA | 01_SW'))
for name in ('02_SE','05_WALK_MINE','06_WALK_ENTRY','04_NW','03_NE'):
 s.camera=bpy.data.objects['RFX CAMERA | '+name];s.cycles.samples=4;p=OUT/(name+'.png');s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
 manifest['views'].append(dict(name=name,path=str(p),sha256=sha(p),samples=4,camera=s.camera.name,position=list(s.camera.location),rotation=list(s.camera.rotation_euler),lens_mm=s.camera.data.lens))
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('REFINERY_FINAL_VIEW',name,flush=True)
manifest.update(complete=True,source_unchanged=sha(src)==report['saved_sha256']);assert manifest['source_unchanged'];(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
