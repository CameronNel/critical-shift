"""Cold-load current map and bundled preview controls from a hydrated checkout."""
import bpy,json,hashlib,runpy,sys,time,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[3]
manifest=json.loads((root/'MAP.json').read_text(encoding='utf-8'))
report={'scope':'Cold native/preview load, dependency containment and bundled-control registration. No renders or Unity/FPS certification.','scenes':[]}
for key in ('authoring_scene','inspection_scene'):
 p=root/manifest[key];start=time.perf_counter()
 if key=='inspection_scene':
  sys.argv+=['--','--preview'];runpy.run_path(str(root/'open_map.py'),run_name='__main__')
 else:bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False)
 deps=[];failures=[]
 for lib in bpy.data.libraries:
  resolved=Path(bpy.path.abspath(lib.filepath)).resolve()
  inside=resolved.is_relative_to(root.resolve());exists=resolved.is_file()
  deps.append({'stored':lib.filepath,'relative_to_checkout':str(resolved.relative_to(root)) if inside else str(resolved),'exists':exists,'inside_checkout':inside})
  if not inside or not exists:failures.append('library:'+lib.filepath)
 for im in bpy.data.images:
  if im.source=='FILE' and im.users and not im.packed_file:
   resolved=Path(bpy.path.abspath(im.filepath,library=im.library)).resolve()
   if not resolved.is_file() or not resolved.is_relative_to(root.resolve()):failures.append('image:'+im.name)
 sources=[]
 for entry in json.loads((root/manifest['section_root']/'production/SOURCES.json').read_text()):
  frozen=root/manifest['section_root']/entry['frozen'];ok=hashlib.sha256(frozen.read_bytes()).hexdigest()==entry['source_sha256'];sources.append({'section':entry['id'],'frozen_hash_pass':ok})
  if not ok:failures.append('source:'+entry['id'])
 controls=key!='inspection_scene' or (hasattr(bpy.types.Scene,'facility_fast_walkthrough') and hasattr(bpy.types.Scene,'facility_auto_doors'))
 if not controls:failures.append('bundled controls not registered')
 report['scenes'].append({'kind':key,'file':manifest[key],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'cold_load_seconds':time.perf_counter()-start,'libraries':deps,'sources':sources,'objects':len(bpy.context.scene.objects),'raytracing':bpy.context.scene.eevee.use_raytracing,'bundled_controls_pass':controls,'failures':failures,'pass':not failures})
report['pass']=all(s['pass'] for s in report['scenes'])
out=root/manifest['section_root']/'production/MAIN_CHECKOUT_VALIDATION.json';out.write_text(json.dumps(report,indent=2));print('MAP_CHECKOUT_PASS',report['pass'],flush=True)
if not report['pass']:raise RuntimeError('Map checkout verification failed; inspect MAIN_CHECKOUT_VALIDATION.json')
