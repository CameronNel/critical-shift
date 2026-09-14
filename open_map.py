"""Run with Blender --python open_map.py [-- --preview]."""
import json,os,runpy,sys
from pathlib import Path
import bpy
root=Path(__file__).resolve().parent
manifest=json.loads((root/'MAP.json').read_text(encoding='utf-8'))
preview='--preview' in sys.argv
scene=root/manifest['inspection_scene' if preview else 'authoring_scene']
with scene.open('rb') as stream:
 if stream.read(42).startswith(b'version https://git-lfs'):raise RuntimeError('Git LFS assets are not downloaded. Run git lfs pull first.')
if preview:
 os.environ['PREVIEW_SOURCE']=scene.name
 runpy.run_path(str(root/manifest['section_root']/'blender/open_material_preview.py'),run_name='__main__')
else:bpy.ops.wm.open_mainfile(filepath=str(scene),load_ui=True)
print('CURRENT_MAP_OPENED',scene,flush=True)
