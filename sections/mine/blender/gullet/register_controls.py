"""Run inside Blender after reopening the generated .blend. Does not rebuild."""
from pathlib import Path
import runpy
import bpy
scene=bpy.context.scene
if not scene.get('csm_generator'):
    raise RuntimeError('Select the generated Critical Shift - Gullet scene first.')
root=Path(scene.get('csm_source_dir',''))
if not (root/'build_mine.py').is_file():
    text=getattr(getattr(bpy.context,'space_data',None),'text',None)
    root=Path(bpy.path.abspath(text.filepath)).resolve().parent if text and text.filepath else Path(__file__).resolve().parent
if not (root/'build_mine.py').is_file():
    raise FileNotFoundError('Place register_controls.py beside build_mine.py in the mine package.')
ns=runpy.run_path(str(root/'build_mine.py'),run_name='csm_controls_module')
ns['register_controls']()
ns['install_api'](scene)
print('Gullet controls registered. 3D View > N > Gullet. Existing scene geometry was not changed.')
