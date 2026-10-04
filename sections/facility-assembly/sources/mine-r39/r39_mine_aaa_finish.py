"""R39 mine AAA mood: dark, accent-lit, faint haze. Lighting only; geometry and painted materials are untouched.

Run once against `module_r39.blend` (extracted by extract_r39_mine.py):
    blender -b module_r39.blend --python r39_mine_aaa_finish.py -- --output module_r39_aaa.blend --receipt aaa-build.json

The mine's materials are hand-painted toon style, so no procedural grime is added. The daylight sky is cut to a dim cold dusk, a very
weak cool key gives rim light, and the lantern, oil lamp, candle and crystal lights stay as the accents. No light is removed; one
dim sun lamp is added for rim light. Four review cameras are added. Triangle count is unchanged (4,083,512): the owner asked to keep the detail.
"""
import json
import math
import sys

import bpy
from mathutils import Vector

REV = 'R39 mine AAA mood'


def opts():
    a = sys.argv[sys.argv.index('--') + 1:]
    return (a[a.index('--output') + 1] if '--output' in a else None,
            a[a.index('--receipt') + 1] if '--receipt' in a else None)


def triangles():
    dg = bpy.context.evaluated_depsgraph_get()
    total = 0
    for o in bpy.data.objects:
        if o.type in ('MESH', 'CURVE', 'FONT') and not o.hide_render:
            ev = o.evaluated_get(dg)
            m = ev.to_mesh()
            total += sum(len(p.vertices) - 2 for p in m.polygons)
            ev.to_mesh_clear()
    return total


def mood(scene):
    cut = {}
    for o in bpy.data.objects:
        if o.type != 'LIGHT':
            continue
        if o.name.startswith('R40 | Cliff crystal'):
            f = 1.0
        elif o.name.startswith('R39 | Crystal glow'):
            f = 1.2
        else:
            f = 1.0                      # lanterns, oil lamps, candles, notice lamp stay at full strength as accents
        o.data.energy *= f
        cut[o.name] = f
    scene.view_settings.exposure -= .6
    nt = scene.world.node_tree
    for n in nt.nodes:
        if n.type == 'BACKGROUND':
            n.inputs['Strength'].default_value *= .12
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD')
    if not out.inputs['Volume'].is_linked:
        vol = nt.nodes.new('ShaderNodeVolumeScatter')
        vol.label = 'AAA | cold haze'
        vol.inputs['Density'].default_value = .004
        vol.inputs['Anisotropy'].default_value = .5
        vol.inputs['Color'].default_value = (.62, .74, .84, 1)
        nt.links.new(vol.outputs['Volume'], out.inputs['Volume'])
    scene.cycles.volume_bounces = 1
    scene.cycles.volume_max_steps = 64
    sun = bpy.data.lights.new('AAA | cold rim key', 'SUN')
    sun.energy = .35
    sun.color = (.62, .74, 1.0)
    ob = bpy.data.objects.new('AAA | cold rim key', sun)
    ob.rotation_euler = (math.radians(62), 0, math.radians(35))
    bpy.data.collections['MODULE_mine-r39'].objects.link(ob)
    return cut


CAMERAS = {
    'R39_01_PORTAL_APPROACH': ((-18, -48, 3.2), (-30, -27, 2.0), 24),
    'R39_02_TUNNEL': ((-44, -29.2, 1.7), (-76, -29.0, 1.6), 22),
    'R39_03_YARD_WIDE': ((-8, -44, 9), (-50, -28, 2), 20),
    'R39_04_SHED_FRONT': ((-30, -45, 2.0), (-31, -30, 2.3), 28),
}


def add_cameras():
    col = bpy.data.collections['MODULE_mine-r39']
    for n, (loc, tgt, lens) in CAMERAS.items():
        cam = bpy.data.cameras.new(n)
        cam.lens = lens
        cam.clip_start = .05
        cam.clip_end = 600
        ob = bpy.data.objects.new(n, cam)
        ob.location = loc
        ob.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        col.objects.link(ob)


def apply():
    s = bpy.context.scene
    assert not s.get('r39_aaa_revision'), 'R39 AAA mood already applied'
    before = triangles()
    lights = len([o for o in bpy.data.objects if o.type == 'LIGHT'])
    cut = mood(s)
    add_cameras()
    after = triangles()
    s['r39_aaa_revision'] = REV
    bpy.context.view_layer.update()
    return {'revision': REV, 'lights_before': lights, 'lights_after': len([o for o in bpy.data.objects if o.type == 'LIGHT']),
            'exposure_now': s.view_settings.exposure, 'triangles_before': before, 'triangles_after': after,
            'new_cameras': list(CAMERAS), 'note': 'geometry unchanged by owner request; lighting only'}


if __name__ == '__main__':
    out, receipt = opts()
    result = apply()
    if receipt:
        json.dump(result, open(receipt, 'w'), indent=2)
    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
    print('R39:', json.dumps(result)[:500])
