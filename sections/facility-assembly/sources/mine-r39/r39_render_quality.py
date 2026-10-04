"""R39 mine render quality: saved Cycles settings that stop the grain, plus a better shed camera.

Run once against `module_r39_aaa.blend`:
    blender -b module_r39_aaa.blend --python r39_render_quality.py -- --output module_r39_aaa.blend

The module inherited a 4-sample draft setting from the map. This saves 96 samples with adaptive sampling, OpenImageDenoise using albedo and
normal passes, the light tree, and a slightly thinner haze. R39_04_SHED_FRONT is re-aimed at the lantern-lit side of the shed (the old
front view was almost black).
"""
import sys

import bpy
from mathutils import Vector


def main():
    s = bpy.context.scene
    assert not s.get('r39_render_quality'), 'already applied'
    c = s.cycles
    c.samples = 96
    c.use_adaptive_sampling = True
    c.adaptive_threshold = .02
    c.adaptive_min_samples = 16
    c.use_denoising = True
    c.denoiser = 'OPENIMAGEDENOISE'
    c.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    c.denoising_prefilter = 'ACCURATE'
    c.sample_clamp_indirect = 8.0
    c.sample_clamp_direct = 0.0
    if hasattr(c, 'use_light_tree'):
        c.use_light_tree = True
    s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = 960, 540, 100
    for n in s.world.node_tree.nodes:
        if n.type == 'VOLUME_SCATTER':
            n.inputs['Density'].default_value = .003
    cam = bpy.data.objects['R39_04_SHED_FRONT']
    cam.location = (-20, -36, 2.0)
    cam.rotation_euler = (Vector((-29, -29, 2.3)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    s['r39_render_quality'] = '96 spp adaptive + OIDN albedo/normal'


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:]
    main()
    bpy.ops.wm.save_as_mainfile(filepath=a[a.index('--output') + 1], compress=True)
    print('QUALITY: ok')
