"""Hall fixes: darker wet concrete, moodier lighting, baked wall numbers, triangle cut.

Blender 5.2.2 LTS:
  blender --background --disable-autoexec -noaudio reactorroom.blend --python-exit-code 1 \
    --python rh_hall_moody_fixes.py -- --atlas wall_numbers.png --out OUT.blend [--skip-decimate]

Make the atlas first with make_wall_number_atlas.py (system Python with Pillow).
Wall numbers are texture work: a stencil layer inside the two wall concrete
materials, keyed to world position and wall normal, so no geometry is added.
The atlas is packed into the saved scene.
"""
import argparse
import sys
from pathlib import Path

import bpy

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument('--atlas', type=Path, required=True)
ap.add_argument('--out', type=Path, required=True)
ap.add_argument('--skip-decimate', action='store_true')
args = ap.parse_args(argv)

# Wall-number layout. Four walls (N, S, E, W) by five bays, pitch 4.1 m.
BAY_PITCH, BAYS, ROWS = 4.1, 5, 4
STENCIL_W, STENCIL_H, STENCIL_Z0 = 2.4, 0.8, 3.3

FLOOR_DARKEN = 0.36      # base-colour multiplier on the wet floor concrete
FLOOR_ROUGH = 0.55       # roughness multiplier: wetter, glossier
WALL_DARKEN = 0.58
LIGHT_SCALE = [          # (name prefix, energy multiplier, optional tint)
    ('LP wash', 0.4, (0.72, 0.83, 1.0)),
    ('LP roof shaft', 2.2, None),
    ('LP bank A uplight', 0.55, None),
    ('LP bank B uplight', 0.55, None),
    ('LP task', 0.75, None),
    ('LP bank A gantry', 0.75, None),
    ('LP bank B gantry', 0.75, None),
    ('RH refine circulation area', 0.4, None),
    ('RH refine roof bay', 1.6, None),
    ('LP rim', 0.5, None),
]
WORLD_STRENGTH = 0.05

# name -> collapse ratio. Over-tessellated, non-interactive meshes only.
DECIMATE = {
    'R2 crane trolley crane CABLE': 0.25,
    'RH refine crane hoist rope rope CRANE_ROPE': 0.35,
    'R2 bank A moving bank A rod band TRIM': 0.3,
    'R2 bank B moving bank B rod band TRIM': 0.3,
    'RH services R2 PIPING clip GALV': 0.5,
    'RH services R2 PIPING bolt STEEL': 0.45,
    'RH services R2 PIPING clamp GALV': 0.5,
    'RH services R2 PIPING sleeve IRON': 0.5,
    'RH roof crossings washers GALV': 0.4,
    'RF BATCH services RF edge': 0.5,
    'RH walls steel STEEL': 0.7,
    'RH stations props STEEL': 0.6,
    'RH stations east STEEL': 0.6,
    'RH walls concrete CONC_DARK': 0.6,
    'RH walls assets GALV': 0.7,
    'RH services cage GALV': 0.6,
    'RH walls concrete BLACK': 0.6,
    'RH walls cladding GALV': 0.7,
    'RH stations south STEEL': 0.6,
    'RF BATCH services RF gunmetal': 0.6,
    'RH walls window AUDI_SATIN': 0.6,
    'RH refine water film FILM': 0.5,
    'R2 crane trolley crane IRON': 0.6,
    'RH walls assets BLACK': 0.7,
    'RH stations west STEEL': 0.6,
    'RF BATCH structure RF edge': 0.5,
    'RH services fixture STEEL': 0.6,
}


def tri_count():
    dg = bpy.context.evaluated_depsgraph_get()
    total = 0
    for o in bpy.context.scene.objects:
        if o.type in ('MESH', 'CURVE', 'FONT', 'SURFACE') and not o.hide_render:
            e = o.evaluated_get(dg)
            m = e.to_mesh()
            m.calc_loop_triangles()
            total += len(m.loop_triangles)
            e.to_mesh_clear()
    return total


def bsdf(mat):
    return next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


def insert_before(mat, socket_name, make_node, link_in, link_out):
    """Put a node between whatever feeds a BSDF input and that input."""
    tree = mat.node_tree
    b = bsdf(mat)
    sock = b.inputs[socket_name]
    src = sock.links[0].from_socket if sock.links else None
    node = make_node(tree)
    if src is not None:
        tree.links.new(src, node.inputs[link_in])
    else:
        node.inputs[link_in].default_value = sock.default_value
    tree.links.new(node.outputs[link_out], sock)
    return node


def mix_multiply(tree, amount):
    n = tree.nodes.new('ShaderNodeMix')
    n.data_type = 'RGBA'
    n.blend_type = 'MULTIPLY'
    n.inputs['Factor'].default_value = 1.0
    n.inputs[7].default_value = (amount, amount, amount * 1.02, 1)
    return n


def darken(mat_name, amount, rough_mult=None):
    mat = bpy.data.materials[mat_name]
    insert_before(mat, 'Base Color', lambda t: mix_multiply(t, amount), 6, 2)
    if rough_mult is not None:
        def rough(t):
            n = t.nodes.new('ShaderNodeMath')
            n.operation = 'MULTIPLY'
            n.inputs[1].default_value = rough_mult
            return n
        insert_before(mat, 'Roughness', rough, 0, 0)


def wet_floor(mat_name):
    """Puddle patches and drag streaks: darker, mirror-smooth, with a clear coat."""
    mat = bpy.data.materials[mat_name]
    t = mat.node_tree
    b = bsdf(mat)
    geo = t.nodes.new('ShaderNodeNewGeometry')
    pos = geo.outputs['Position']

    def noise(scale, lo, hi, stretch=None):
        src = pos
        if stretch is not None:
            vm = t.nodes.new('ShaderNodeVectorMath')
            vm.operation = 'MULTIPLY'
            vm.inputs[1].default_value = stretch
            t.links.new(pos, vm.inputs[0])
            src = vm.outputs[0]
        n = t.nodes.new('ShaderNodeTexNoise')
        n.inputs['Scale'].default_value = scale
        n.inputs['Detail'].default_value = 4.0
        t.links.new(src, n.inputs['Vector'])
        r = t.nodes.new('ShaderNodeMapRange')
        r.inputs['From Min'].default_value = lo
        r.inputs['From Max'].default_value = hi
        t.links.new(n.outputs['Fac'], r.inputs['Value'])
        return r.outputs['Result']

    puddle = noise(0.45, 0.50, 0.58)
    streak = math(t, 'MULTIPLY', noise(1.3, 0.52, 0.64, (0.5, 4.0, 1.0)), 0.7)
    wet = math(t, 'MAXIMUM', puddle, streak)
    # darker under water
    sock = b.inputs['Base Color']
    dark = t.nodes.new('ShaderNodeMix')
    dark.data_type = 'RGBA'
    dark.blend_type = 'MULTIPLY'
    dark.inputs[7].default_value = (0.5, 0.5, 0.52, 1)
    t.links.new(wet, dark.inputs['Factor'])
    t.links.new(sock.links[0].from_socket, dark.inputs[6])
    t.links.new(dark.outputs[2], sock)
    # smoother where wet: r' = r*(1-wet) + 0.05*wet
    rs = b.inputs['Roughness']
    r_src = rs.links[0].from_socket
    keep = math(t, 'MULTIPLY', r_src, math(t, 'SUBTRACT', 1.0, wet))
    t.links.new(math(t, 'ADD', keep, math(t, 'MULTIPLY', wet, 0.05)), rs)
    # sharp clear coat for lamp and pool reflections
    t.links.new(math(t, 'MULTIPLY', wet, 0.95), b.inputs['Coat Weight'])
    b.inputs['Coat Roughness'].default_value = 0.03


def add_roof_accents():
    """Warm spots from roof level so girders and the crane keep their structure."""
    coll = bpy.data.collections['25 LIGHTING']
    for i, (x, y) in enumerate([(-6, -5), (6, -5), (-6, 5), (6, 5), (0, 8), (0, -8)]):
        data = bpy.data.lights.new(f'RH hall roof accent {i}', 'SPOT')
        data.energy = 9000
        data.color = (1.0, 0.78, 0.55)
        data.spot_size = 1.05
        data.spot_blend = 0.7
        data.shadow_soft_size = 0.15
        obj = bpy.data.objects.new(data.name, data)
        obj.location = (x, y, 16.2)
        coll.objects.link(obj)


def math(tree, op, a=None, b=None):
    n = tree.nodes.new('ShaderNodeMath')
    n.operation = op
    if a is not None and not hasattr(a, 'is_output'):
        n.inputs[0].default_value = a
    if b is not None and not hasattr(b, 'is_output'):
        n.inputs[1].default_value = b
    for i, v in enumerate((a, b)):
        if v is not None and hasattr(v, 'is_output'):
            tree.links.new(v, n.inputs[i])
    return n.outputs[0]


def add_numbers(mat_name, atlas, paint=(0.95, 0.91, 0.8, 1.0)):
    mat = bpy.data.materials[mat_name]
    t = mat.node_tree
    geo = t.nodes.new('ShaderNodeNewGeometry')
    pos = t.nodes.new('ShaderNodeSeparateXYZ')
    nor = t.nodes.new('ShaderNodeSeparateXYZ')
    t.links.new(geo.outputs['Position'], pos.inputs[0])
    t.links.new(geo.outputs['Normal'], nor.inputs[0])
    x, y, z = pos.outputs
    nx, ny, _ = nor.outputs
    is_n = math(t, 'LESS_THAN', ny, -0.7)
    is_s = math(t, 'GREATER_THAN', ny, 0.7)
    is_e = math(t, 'LESS_THAN', nx, -0.7)
    is_w = math(t, 'GREATER_THAN', nx, 0.7)
    valid_wall = math(t, 'ADD', math(t, 'ADD', is_n, is_s), math(t, 'ADD', is_e, is_w))
    # distance along the wall as the viewer inside the hall reads it
    u = math(t, 'ADD',
             math(t, 'MULTIPLY', math(t, 'SUBTRACT', is_n, is_s), x),
             math(t, 'MULTIPLY', math(t, 'SUBTRACT', is_w, is_e), y))
    row = math(t, 'ADD', math(t, 'ADD', is_s, math(t, 'MULTIPLY', is_e, 2.0)),
               math(t, 'MULTIPLY', is_w, 3.0))
    cu = math(t, 'DIVIDE', math(t, 'ADD', u, BAYS / 2 * BAY_PITCH), BAY_PITCH)
    cell = math(t, 'FLOOR', cu)
    frac = math(t, 'SUBTRACT', cu, cell)
    sx = math(t, 'ADD', math(t, 'MULTIPLY', math(t, 'SUBTRACT', frac, 0.5), BAY_PITCH / STENCIL_W), 0.5)
    sy = math(t, 'DIVIDE', math(t, 'SUBTRACT', z, STENCIL_Z0), STENCIL_H)
    inside = math(t, 'MULTIPLY',
                  math(t, 'MULTIPLY', math(t, 'GREATER_THAN', sx, 0.0), math(t, 'LESS_THAN', sx, 1.0)),
                  math(t, 'MULTIPLY', math(t, 'GREATER_THAN', sy, 0.0), math(t, 'LESS_THAN', sy, 1.0)))
    inside = math(t, 'MULTIPLY', inside,
                  math(t, 'MULTIPLY', math(t, 'GREATER_THAN', cell, -0.5), math(t, 'LESS_THAN', cell, BAYS - 0.5)))
    inside = math(t, 'MULTIPLY', inside, valid_wall)
    sxc = math(t, 'MINIMUM', math(t, 'MAXIMUM', sx, 0.0), 1.0)
    syc = math(t, 'MINIMUM', math(t, 'MAXIMUM', sy, 0.0), 1.0)
    atlas_u = math(t, 'DIVIDE', math(t, 'ADD', math(t, 'MAXIMUM', cell, 0.0), sxc), float(BAYS))
    atlas_v = math(t, 'DIVIDE', math(t, 'ADD', math(t, 'SUBTRACT', ROWS - 1.0, row), syc), float(ROWS))
    comb = t.nodes.new('ShaderNodeCombineXYZ')
    t.links.new(atlas_u, comb.inputs['X'])
    t.links.new(atlas_v, comb.inputs['Y'])
    tex = t.nodes.new('ShaderNodeTexImage')
    tex.image = atlas
    tex.interpolation = 'Linear'
    tex.extension = 'EXTEND'
    t.links.new(comb.outputs[0], tex.inputs['Vector'])
    glyph = t.nodes.new('ShaderNodeSeparateColor')
    t.links.new(tex.outputs['Color'], glyph.inputs[0])
    # chipped, faded stencil paint
    chip = t.nodes.new('ShaderNodeTexNoise')
    chip.inputs['Scale'].default_value = 34.0
    chip.inputs['Detail'].default_value = 3.0
    t.links.new(geo.outputs['Position'], chip.inputs['Vector'])
    rng = t.nodes.new('ShaderNodeMapRange')
    rng.inputs['From Min'].default_value = 0.35
    rng.inputs['From Max'].default_value = 0.62
    rng.inputs['To Min'].default_value = 0.8
    rng.inputs['To Max'].default_value = 1.0
    t.links.new(chip.outputs['Fac'], rng.inputs['Value'])
    mask = math(t, 'MULTIPLY', math(t, 'MULTIPLY', glyph.outputs[0], inside), rng.outputs['Result'])
    mask = math(t, 'MULTIPLY', mask, 1.0)
    mixer = t.nodes.new('ShaderNodeMix')
    mixer.data_type = 'RGBA'
    mixer.inputs[7].default_value = paint
    t.links.new(mask, mixer.inputs['Factor'])
    b = bsdf(mat)
    sock = b.inputs['Base Color']
    t.links.new(sock.links[0].from_socket, mixer.inputs[6])
    t.links.new(mixer.outputs[2], sock)


# --- run --------------------------------------------------------------
before = tri_count()
print('TRIS_BEFORE', before)

atlas = bpy.data.images.load(str(args.atlas), check_existing=False)
atlas.name = 'RH wall number stencils'
atlas.colorspace_settings.name = 'Non-Color'
atlas.pack()

darken('RH floor wet concrete', FLOOR_DARKEN, FLOOR_ROUGH)
wet_floor('RH floor wet concrete')
for name in ('RH refine wall concrete', 'RH refine cast concrete'):
    darken(name, WALL_DARKEN)
    add_numbers(name, atlas)

for light in (o for o in bpy.context.scene.objects if o.type == 'LIGHT'):
    for prefix, mult, tint in LIGHT_SCALE:
        if light.name.startswith(prefix):
            light.data.energy *= mult
            if tint:
                light.data.color = tint
            break
add_roof_accents()
bg = next(n for n in bpy.context.scene.world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Strength'].default_value = WORLD_STRENGTH

if not args.skip_decimate:
    for name, ratio in DECIMATE.items():
        o = bpy.data.objects.get(name)
        if o is None or o.type != 'MESH':
            print('DECIMATE_MISSING', name)
            continue
        if o.data.users > 1:
            o.data = o.data.copy()
        n0 = len(o.data.polygons)
        mod = o.modifiers.new('hall_decimate', 'DECIMATE')
        mod.ratio = ratio
        with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o]):
            bpy.ops.object.modifier_apply(modifier=mod.name)
        print('DECIMATE', name, n0, '->', len(o.data.polygons))

after = tri_count()
print('TRIS_AFTER', after)
bpy.ops.wm.save_as_mainfile(filepath=str(args.out), compress=True)
print('SAVED', args.out)
