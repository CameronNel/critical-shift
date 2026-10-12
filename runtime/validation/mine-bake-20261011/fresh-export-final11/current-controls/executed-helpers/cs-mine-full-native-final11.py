from pathlib import Path
import subprocess,json,sys,hashlib
root=Path('/workspace/critical-shift-spawn-runtime');audit=root/'runtime/out/mine-bake-audit';python='/home/agent/.local/share/critical-shift/venv/bin/python'
sys.path.insert(0,str(root/'runtime/tools'));from prepare_mine import export_recipe,validate_cache
source=root/'runtime/out/spawn-export-source/combined-runtime-source.blend';config=json.loads((source.parent/'map-config.json').read_text());version=subprocess.check_output(['/home/agent/.local/bin/blender','--version'],text=True).splitlines()[0];cache=json.loads((audit/'surface-cache.json').read_text());recipe=export_recipe(root,version,True,hashlib.sha256(source.read_bytes()).hexdigest());validate_cache(cache,config,4096,recipe)
assert json.loads((audit/'preservation.json').read_text())['status']=='Passed'
with (audit/'native-bake-source-wood-final11-wrapper.log').open('w') as f:subprocess.run([python,'/tmp/cs-mine-bake-source-wood-final11.py'],cwd=root,stdout=f,stderr=subprocess.STDOUT,check=True)
print('CS_FINAL11_FRESH_NATIVE_LIGHTING_AND_SPAWN_CAPTURES_READY',flush=True)
with (audit/'after-bake-source-wood-final11-wrapper.log').open('w') as f:subprocess.run([python,'/tmp/cs-mine-after-bake-source-wood-final11.py'],cwd=root,stdout=f,stderr=subprocess.STDOUT,check=True)
print('CS_FINAL11_FRESH_MINE_VIEWS_AND_CURRENT_GAMEPLAY_READY_FOR_REVIEW',flush=True)
