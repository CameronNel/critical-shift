"""A labelled plan cutaway of the condenser bay (rubric 2.2: cutaways must say they are cutaways): an orthographic camera looking down,
its near clip plane at module z 4.9 m, so the roof slab, the crane runway and the ceiling services are cut away and everything below shows
lit by the room's own lights. CPU only (the owner's choice for review renders). Not a player view.

    blender -b --factory-startup module_aaa_A3.blend --python render_cutaway_A3.py -- <out.png> <size_px> <samples>
"""
import bpy, sys
from mathutils import Euler

a = sys.argv[sys.argv.index('--') + 1:]
out, rx, spp = a[0], int(a[1]), int(a[2])
CUT, TOP = 4.9, 30.0                    # below the crane runway beams (5.0..5.4), through the gallery rail tops
sc = bpy.context.scene
cam = bpy.data.objects.new('CUTAWAY plan', bpy.data.cameras.new('CUTAWAY plan')); sc.collection.objects.link(cam)
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 12.8; cam.data.clip_start = TOP - CUT; cam.data.clip_end = TOP + 2.0
cam.location = (3.85, 3.55, TOP); cam.rotation_euler = Euler((0, 0, 0))          # module x -2.3..10.0, y -2.6..9.7, looking down
sc.camera = cam; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = spp
sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'
sc.render.resolution_x = rx; sc.render.resolution_y = rx; sc.render.resolution_percentage = 100      # square: the room is about 12.3 x 12.3 m
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print('CUTAWAY written', out, 'clip above module z %.1f m' % CUT)
