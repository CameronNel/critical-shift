"""Restore Gullet controls after reopening, without rebuilding or changing geometry."""
from pathlib import Path
import runpy
import bpy
scene=bpy.context.scene
if not scene.get('csm_generator'):
    raise RuntimeError('Select the generated Critical Shift - Gullet scene first.')
if scene.get('q50_revision'):
    embedded=bpy.data.texts.get('RUN_GULLET_CONTROLS.py')
    if embedded is not None:
        namespace={'__name__':'gullet_embedded_controls'}
        exec(compile(embedded.as_string(),'RUN_GULLET_CONTROLS.py','exec'),namespace,namespace)
        namespace['register']()
    else:
        root=Path(__file__).resolve().parent
        namespace=runpy.run_path(str(root/'quality50'/'controls.py'),run_name='gullet_quality_controls')
        namespace['register']()
else:
    root=Path(scene.get('csm_source_dir',''))
    if not (root/'build_mine.py').is_file():
        text=getattr(getattr(bpy.context,'space_data',None),'text',None)
        root=Path(bpy.path.abspath(text.filepath)).resolve().parent if text and text.filepath else Path(__file__).resolve().parent
    if not (root/'build_mine.py').is_file():
        raise FileNotFoundError('Place register_controls.py beside build_mine.py in the mine package.')
    namespace=runpy.run_path(str(root/'build_mine.py'),run_name='csm_controls_module')
    namespace['register_controls']()
    namespace['install_api'](scene)
print('Gullet controls restored: 3D View > N > Gullet. Geometry was not rebuilt.')
