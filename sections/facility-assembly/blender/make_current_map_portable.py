"""Relocate library paths only; preserve all scene geometry and frozen source inputs."""
import bpy,json,hashlib,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];root=R.parents[1];manifest=json.loads((root/'MAP.json').read_text());rows=[]
files=[R/'exteriors'/e['id']/('exterior-'+e['revision']+'.blend') for e in []]
# Inspect current exterior library files, not historical revisions or frozen inputs.
current=json.loads((R/'exteriors/CURRENT.json').read_text())
if isinstance(current,dict):
 for name,value in current.items():
  rev=value if isinstance(value,str) else value.get('revision','')
  candidate=R/'exteriors'/name/('exterior-'+rev+'.blend')
  if candidate.exists():files.append(candidate)
files += [root/manifest['authoring_scene'],root/manifest['inspection_scene']]
for p in files:
 before=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False);changes=[]
 for lib in bpy.data.libraries:
  raw=lib.filepath.replace('\\','/');absolute=bpy.path.abspath(lib.filepath).replace('\\','/')
  marker='/sections/facility-assembly/'
  if marker not in absolute:raise RuntimeError('Unmapped library: '+absolute)
  destination=R/absolute.split(marker,1)[1]
  if not destination.is_file():raise RuntimeError('Missing local library: '+str(destination))
  relative='//'+os.path.relpath(destination,p.parent).replace('\\','/')
  if raw!=relative:lib.filepath=relative;changes.append({'from':raw,'to':relative})
 if changes:
  bpy.context.preferences.filepaths.save_version=0
  bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True)
 rows.append({'file':str(p.relative_to(root)),'before_sha256':before,'after_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'changes':changes,'objects':len(bpy.context.scene.objects)})
(R/'production/PORTABLE_MAP_RELINK.json').write_text(json.dumps({'scope':'Library-path-only relocation for remote checkout. No art changes. Frozen accepted.blend inputs untouched. Prior visual reviews bind the pre-relocation hashes.','files':rows},indent=2));print('PORTABLE_RELINK_COMPLETE',flush=True)
