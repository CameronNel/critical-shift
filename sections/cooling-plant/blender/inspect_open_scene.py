"""Presentation-only UI setup for this section's own Blender window. Does not save."""
import bpy
from pathlib import Path
expected=Path(__file__).resolve().parent/'cooling_plant.blend'
if Path(bpy.data.filepath).resolve()!=expected.resolve():raise RuntimeError('Wrong file; no UI changes made')
bpy.context.scene.camera=bpy.data.objects['C01_ENTRY']
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.region_3d.view_perspective='CAMERA'
            space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.shading.light='STUDIO'
            space.shading.show_cavity=True;space.overlay.show_overlays=False
print('COOLING_UI_READY '+bpy.data.filepath)
