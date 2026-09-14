import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'connections/access'
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(O/'access-A08.blend'),link=False) as (src,dst):dst.collections=src.collections
for c in dst.collections:bpy.context.scene.collection.children.link(c)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True
s.render.resolution_x=1000;s.render.resolution_y=900;s.render.resolution_percentage=100
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.location=(40,51,14);c.rotation_euler=(Vector((33,40,-2))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=20;s.camera=c
s.render.filepath=str(O/'asset-review.png');bpy.ops.render.render(write_still=True)
