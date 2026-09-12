"""Promote exact reviewed candidate bytes; reject changed canonical/source inputs."""
from pathlib import Path
import hashlib,json,sys,shutil,datetime
r=Path(__file__).resolve().parent.parent;revision,expected_old=sys.argv[1:3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
src=r/f'production/checkpoints/{revision}/blender/Fuel_Corridor.blend';dst=r/'blender/Fuel_Corridor.blend'
assert sha(dst)==expected_old,'Canonical changed; preserve user edits'
if '--pre-render' in sys.argv:
 prefix=revision.replace('final-','');e=r/'production/evidence/final-pass'
 technical=json.loads((e/(prefix+'-technical.json')).read_text());assert technical['status']=='PASS'
 replay=json.loads((e/(prefix+'-source-replay.json')).read_text());assert not any(replay[k] for k in ['missing','added','changed','matrix_differences'])
 mats=json.loads((e/(prefix+'-material-replay.json')).read_text())['differences'];assert not any(mats[k][v] for k in ['materials','uv','textures'] for v in ['changed','missing','added'])
else:
 manifest=json.loads((r/f'production/renders/review/{revision}/cold_render_manifest.json').read_text())
 assert len(manifest['renders'])==16 and manifest['saved_file_unchanged'] and manifest['blend_sha256_before']==sha(src)
for name in ['build.py','valorant_details.py','wayfinding.py']:
 assert sha(r/'blender'/name)==sha(src.parent/name),'Source changed since candidate'
shutil.copy2(src,dst);assert sha(src)==sha(dst)
shutil.copy2(src.parent.parent/'scenery/handoff.json',r/'scenery/handoff.json')
out=r/f'production/evidence/final-pass/{revision.replace("final-","")}-promotion.json'
out.write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(src),'canonical':str(dst),'previous_sha256':expected_old,'new_sha256':sha(dst),'method':'Byte-for-byte copy; no scene resave','final_approval':'Separate independent cold/player review required'},indent=2))
print('PROMOTED',revision,sha(dst))
