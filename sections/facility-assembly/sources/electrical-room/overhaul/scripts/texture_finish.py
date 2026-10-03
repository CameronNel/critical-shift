"""Owner-directed texture rework: rough rustic wall paint, detailed wet concrete, grip pads, crisp hero-prop edges.

Run once against the palette-finished source (the reviewed R11 module):
    blender -b module.blend --python texture_finish.py -- --output NEW.blend --receipt REPORT.json

What it changes (nothing else is touched):
  1. Wall/ceiling paint (`EOH | cream`): chipped paint over dark primer with rust staining, vertical streaks, an
     orange-peel/trowel relief, cavity grime and matte-to-gritty roughness.
  2. Floor concrete (`EOH | floor`, `Floor contact history`, `route`): aggregate flecks, pits, hairline cracks, and wet,
     dark, glossy patches by the transformer, transfer cabinet, reserve bay, switchgear draw-out, workbench and doors.
     The wet patches are bounded zones with noisy edges; the rest of the slab stays dry and rough.
  3. Metals, enamels and rubber: micro-scratch roughness breakup, cavity grime, and (enamel/oxide/ochre) edge wear that
     reads as crisp bright edge highlights. Rubber gets a stipple relief.
  4. Hero props (switchgear, transformer, transfer cabinet, reserve modules, cabinet frames, door frames): the bevel
     modifiers become single-segment 4 mm chamfers instead of two-segment 2 mm roundings, for a crisper, more angular edge.
  5. Eight rubber grip pads (ribbed, chamfered, registered to the Floor like the existing insulating mats) scattered at
     stations and thresholds, not over the floor.
Never run this twice against the same source.
"""
import json
import math
import sys

import bmesh
import bpy
from mathutils import Vector

P = 'EOH | '
FLOOR_OBJECT = 'Floor'


def args():
    a = sys.argv[sys.argv.index('--') + 1:]
    out = receipt = None
    for i, v in enumerate(a):
        if v == '--output':
            out = a[i + 1]
        if v == '--receipt':
            receipt = a[i + 1]
    return out, receipt


# ---------------------------------------------------------------------------------------------------------- helpers
class G:
    """Tiny node-graph helper bound to one material."""

    def __init__(self, mat):
        self.mat = mat
        self.nt = mat.node_tree
        self.bs = self.nt.nodes['Principled BSDF']
        self.tc = next((n for n in self.nt.nodes if n.type == 'TEX_COORD'), None) or self.nt.nodes.new('ShaderNodeTexCoord')

    def n(self, kind, name, **kw):
        node = self.nt.nodes.new(kind)
        node.label = 'T1 | ' + name
        for k, v in kw.items():
            setattr(node, k, v)
        return node

    def link(self, a, b):
        self.nt.links.new(a, b)

    def src(self, key):
        sock = self.bs.inputs[key]
        return sock.links[0].from_socket if sock.is_linked else None

    def noise(self, name, scale, detail=3, rough=.6, coords='Object', distortion=0):
        node = self.n('ShaderNodeTexNoise', name)
        node.inputs['Scale'].default_value = scale
        node.inputs['Detail'].default_value = detail
        node.inputs['Roughness'].default_value = rough
        node.inputs['Distortion'].default_value = distortion
        self.link(self.tc.outputs[coords], node.inputs['Vector'])
        return node.outputs['Fac']

    def rng(self, name, sock, a, b, lo=0, hi=1, clamp=True):
        node = self.n('ShaderNodeMapRange', name)
        node.clamp = clamp
        node.inputs['From Min'].default_value = a
        node.inputs['From Max'].default_value = b
        node.inputs['To Min'].default_value = lo
        node.inputs['To Max'].default_value = hi
        self.link(sock, node.inputs[0])
        return node.outputs[0]

    def math(self, name, op, a, b=None, clamp=False):
        node = self.n('ShaderNodeMath', name, operation=op, use_clamp=clamp)
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                node.inputs[i].default_value = v
            else:
                self.link(v, node.inputs[i])
        return node.outputs[0]

    def mixc(self, name, fac, c1, c2, blend='MIX'):
        node = self.n('ShaderNodeMixRGB', name, blend_type=blend)
        self.link(fac, node.inputs[0]) if not isinstance(fac, (int, float)) else setattr(node.inputs[0], 'default_value', fac)
        for i, c in ((1, c1), (2, c2)):
            if isinstance(c, tuple):
                node.inputs[i].default_value = (*c[:3], 1)
            else:
                self.link(c, node.inputs[i])
        return node.outputs[0]

    def ao(self, name, dist=.05, samples=6):
        node = self.n('ShaderNodeAmbientOcclusion', name, samples=samples)
        node.inputs['Distance'].default_value = dist
        return node.outputs['AO']

    def edge(self, name, radius=.012):
        """1 on convex edges and creases, 0 on flat faces (Cycles Bevel node)."""
        bevel = self.n('ShaderNodeBevel', name + ' bevel', samples=4)
        bevel.inputs['Radius'].default_value = radius
        geo = self.n('ShaderNodeNewGeometry', name + ' geometry')
        dot = self.n('ShaderNodeVectorMath', name + ' dot', operation='DOT_PRODUCT')
        self.link(bevel.outputs['Normal'], dot.inputs[0])
        self.link(geo.outputs['Normal'], dot.inputs[1])
        inv = self.math(name + ' invert', 'SUBTRACT', 1.0, dot.outputs['Value'])
        return self.rng(name + ' mask', inv, .004, .09)

    def bump_in(self, name, height, strength, distance):
        """Chain a bump after whatever already drives the Normal input."""
        prev = self.src('Normal')
        node = self.n('ShaderNodeBump', name)
        node.inputs['Strength'].default_value = strength
        node.inputs['Distance'].default_value = distance
        self.link(height, node.inputs['Height'])
        if prev is not None:
            self.link(prev, node.inputs['Normal'])
        self.link(node.outputs['Normal'], self.bs.inputs['Normal'])

    def set_base(self, sock):
        self.link(sock, self.bs.inputs['Base Color'])

    def set_rough(self, sock):
        self.link(sock, self.bs.inputs['Roughness'])


def mat(name):
    return bpy.data.materials[P + name]


def scratch_rough(g, amount, scale=60):
    """Roughness breakup from fine stretched scratches; keeps the existing roughness as the mean."""
    rough = g.src('Roughness')
    base = rough if rough is not None else None
    t = g.n('ShaderNodeMapping', 'scratch stretch')
    t.inputs['Scale'].default_value = (scale * .25, scale, scale * .25)
    g.link(g.tc.outputs['Object'], t.inputs['Vector'])
    node = g.n('ShaderNodeTexNoise', 'scratch noise')
    node.inputs['Scale'].default_value = 1
    node.inputs['Detail'].default_value = 2
    g.link(t.outputs['Vector'], node.inputs['Vector'])
    delta = g.rng('scratch delta', node.outputs['Fac'], .35, .65, -amount, amount, clamp=False)
    total = g.math('scratch add', 'ADD', base if base is not None else g.bs.inputs['Roughness'].default_value, delta, clamp=True)
    g.set_rough(total)


# ------------------------------------------------------------------------------------------------------- 1. wall paint
def rustic_wall_paint():
    g = G(mat('cream'))
    base = g.src('Base Color')
    # coarse blotches in the paint tone (cooler/warmer by patch)
    blot = g.noise('paint blotches', 1.6, 4, .62)
    tone = g.mixc('paint blotch tone', g.rng('blotch range', blot, .35, .65, 0, .55), base, (.075, .082, .088), 'MULTIPLY')
    # chipped paint exposing dark primer: warped Voronoi cells give irregular chip outlines
    warp = g.noise('chip warp', 4.5, 3, .6)
    voro = g.n('ShaderNodeTexVoronoi', 'chip cells', voronoi_dimensions='3D', feature='F1')
    voro.inputs['Scale'].default_value = 3.2
    voro.inputs['Randomness'].default_value = 1
    mapn = g.n('ShaderNodeMixRGB', 'chip warp color')
    g.link(g.tc.outputs['Object'], mapn.inputs[1])
    g.link(warp, mapn.inputs[0])
    mapn.inputs[2].default_value = (.4, .4, .4, 1)
    g.link(mapn.outputs[0], voro.inputs['Vector'])
    fine = g.noise('chip grit', 38, 4, .7)
    chip_field = g.math('chip field', 'MULTIPLY', g.rng('chip cell range', voro.outputs['Distance'], .25, .75), g.rng('chip grit range', fine, .35, .8))
    ao_edge = g.ao('wall cavity', .08)
    cavity = g.rng('wall cavity amount', ao_edge, .1, 1, 1, 0)
    geo = g.n('ShaderNodeNewGeometry', 'wall position')
    sep = g.n('ShaderNodeSeparateXYZ', 'wall position split')
    g.link(geo.outputs['Position'], sep.inputs[0])
    low = g.rng('lower wall wear', sep.outputs['Z'], .05, 1.9, 1, .0)
    wear = g.math('chip likelihood', 'ADD', g.math('chip base', 'MULTIPLY', g.rng('chip pick', chip_field, .45, .75), .7), g.math('chip extra', 'MULTIPLY', low, .5), clamp=True)
    wear = g.math('chip wear with cavities', 'ADD', wear, g.math('cavity chips', 'MULTIPLY', cavity, .3), clamp=True)
    chip = g.rng('chip threshold', wear, .40, .47)
    primer = (.032, .036, .041)
    rust = (.24, .092, .034)
    rust_mask = g.math('rust where chips are deep', 'MULTIPLY', chip, g.rng('rust pick', g.noise('rust spots', 7, 3, .6), .46, .6))
    c1 = g.mixc('chips show primer', chip, tone, primer)
    c2 = g.mixc('rust in deep chips', rust_mask, c1, rust)
    # vertical drip streaks below the ceiling line, rust-tinted and soft
    stretch = g.n('ShaderNodeMapping', 'streak stretch')
    stretch.inputs['Scale'].default_value = (11, 11, .55)
    g.link(g.tc.outputs['Object'], stretch.inputs['Vector'])
    sn = g.n('ShaderNodeTexNoise', 'streak noise')
    sn.inputs['Scale'].default_value = 1
    sn.inputs['Detail'].default_value = 3
    g.link(stretch.outputs['Vector'], sn.inputs['Vector'])
    streak = g.rng('streaks', sn.outputs['Fac'], .48, .72, 0, .62)
    c3 = g.mixc('drip streaks', streak, c2, (.075, .052, .038), 'MULTIPLY')
    c4 = g.mixc('cavity grime', g.math('grime amount', 'MULTIPLY', cavity, .65), c3, (.28, .27, .25), 'MULTIPLY')
    g.set_base(c4)
    # relief: orange-peel grit + trowel undulation + chipped steps; paint is matte, chips gritty
    peel = g.noise('orange peel', 95, 3, .7)
    wave = g.noise('trowel undulation', 3.2, 2, .55)
    height = g.math('relief', 'ADD', g.math('relief grit', 'MULTIPLY', peel, .7), g.math('relief wave', 'MULTIPLY', wave, .9))
    height = g.math('relief with chips', 'SUBTRACT', height, g.math('chip depth', 'MULTIPLY', chip, .35))
    g.bump_in('rough paint relief', height, .85, .006)
    rough = g.math('paint roughness', 'ADD', .86, g.math('chip roughness', 'MULTIPLY', chip, .12), clamp=True)
    g.set_rough(g.math('rough with grit', 'ADD', rough, g.rng('grit roughness', peel, .3, .7, -.05, .05), clamp=True))


# ----------------------------------------------------------------------------------------------- 2. wet / detailed concrete
def wet_zones(g, zones):
    """Bounded wet patches in the Floor object's coordinates with noisy edges; returns (mask, rim)."""
    mask = None
    for cx, cy, rx, ry in zones:
        off = g.n('ShaderNodeVectorMath', 'wet offset', operation='SUBTRACT')
        off.inputs[1].default_value = (cx, cy, 0)
        g.link(g.tc.outputs['Object'], off.inputs[0])
        scale = g.n('ShaderNodeVectorMath', 'wet ellipse', operation='MULTIPLY')
        scale.inputs[1].default_value = (1 / rx, 1 / ry, 0)
        g.link(off.outputs['Vector'], scale.inputs[0])
        length = g.n('ShaderNodeVectorMath', 'wet radius', operation='LENGTH')
        g.link(scale.outputs['Vector'], length.inputs[0])
        edge_noise = g.noise('wet edge noise', 3.4, 4, .62)
        pushed = g.math('wet edge push', 'ADD', length.outputs['Value'], g.math('wet noise offset', 'MULTIPLY', g.math('wet noise centred', 'SUBTRACT', edge_noise, .5), .85))
        inside = g.rng('wet inside', pushed, .6, 1.0, 1, 0)
        mask = inside if mask is None else g.math('wet union', 'MAXIMUM', mask, inside)
    rim = g.math('wet rim', 'MULTIPLY', g.rng('rim band', mask, .02, .22), g.rng('rim fade', mask, .55, .3, 0, 1))
    return mask, rim


def wet_concrete(name, zones, offset_y=0.0):
    """`zones` are in room metres; `offset_y` converts to the object's coordinates (the Floor object is centred at y 8.2)."""
    g = G(mat(name))
    zones = [(cx, cy - offset_y, rx, ry) for cx, cy, rx, ry in zones]
    base = g.src('Base Color')
    # aggregate flecks, pits, hairline cracks and trowel swirls on the dry slab
    fleck = g.n('ShaderNodeTexVoronoi', 'aggregate', voronoi_dimensions='3D', feature='F1')
    fleck.inputs['Scale'].default_value = 140
    fleck.inputs['Randomness'].default_value = 1
    g.link(g.tc.outputs['Object'], fleck.inputs['Vector'])
    light = g.rng('light aggregate', fleck.outputs['Distance'], .16, .05, 0, .55)
    dark = g.rng('dark pits', g.noise('pit noise', 210, 2, .7), .6, .72, 0, .6)
    c = g.mixc('flecks', light, base, (.34, .35, .34))
    c = g.mixc('pits', dark, c, (.012, .013, .015))
    warp = g.noise('crack warp', 2.2, 3, .55)
    cells = g.n('ShaderNodeTexVoronoi', 'crack cells', voronoi_dimensions='3D', feature='DISTANCE_TO_EDGE')
    cells.inputs['Scale'].default_value = .55
    mixw = g.n('ShaderNodeMixRGB', 'crack warp color')
    g.link(g.tc.outputs['Object'], mixw.inputs[1])
    g.link(warp, mixw.inputs[0])
    mixw.inputs[2].default_value = (.8, .8, .8, 1)
    g.link(mixw.outputs[0], cells.inputs['Vector'])
    crack_line = g.rng('crack line', cells.outputs['Distance'], .0, .012, 1, 0)
    crack = g.math('crack broken up', 'MULTIPLY', crack_line, g.rng('crack gaps', g.noise('crack gaps noise', 1.3, 2, .5), .46, .58))
    c = g.mixc('cracks', g.math('crack strength', 'MULTIPLY', crack, .9), c, (.008, .009, .01))
    # wet zones: darker, near-mirror gloss, lower relief, thin dark rim where water pools
    wet, rim = wet_zones(g, zones)
    c = g.mixc('wet darkening', g.math('wet dark amount', 'MULTIPLY', wet, .78), c, (.18, .2, .22), 'MULTIPLY')
    c = g.mixc('wet rim dirt', g.math('rim dirt amount', 'MULTIPLY', rim, .6), c, (.02, .022, .024), 'MULTIPLY')
    g.set_base(c)
    base_rough = g.src('Roughness')
    r = g.mixc('wet roughness', wet, base_rough, (.07, .07, .07))
    g.set_rough(g.math('rough clamp', 'MAXIMUM', r, .05))
    g.link(g.math('wet coat', 'MULTIPLY', wet, .7), g.bs.inputs['Coat Weight'])
    g.bs.inputs['Coat Roughness'].default_value = .04
    swirl = g.noise('trowel swirls', 4.5, 3, .5)
    micro = g.noise('slab grain', 260, 3, .75)
    height = g.math('slab relief', 'ADD', g.math('swirl relief', 'MULTIPLY', swirl, .5), g.math('grain relief', 'MULTIPLY', micro, .7))
    height = g.math('slab relief + cracks', 'SUBTRACT', height, g.math('crack depth', 'MULTIPLY', crack, 1.4))
    height = g.math('wet fills relief', 'MULTIPLY', height, g.math('wet relief factor', 'SUBTRACT', 1.0, g.math('wet 85', 'MULTIPLY', wet, .85)))
    g.bump_in('slab relief', height, .6, .004)


def concrete_extras(name):
    g = G(mat(name))
    base = g.src('Base Color')
    grit = g.noise('grit', 180, 3, .7)
    g.set_base(g.mixc('grit tone', g.rng('grit tone range', grit, .3, .7, 0, .35), base, (.01, .011, .013), 'MULTIPLY'))
    g.bump_in('grit relief', grit, .35, .003)


# ------------------------------------------------------------------------------------------- 3. metals, enamels, rubber
def metal_detail(name, edge_color=None, edge=.8, grime=.5):
    g = G(mat(name))
    base = g.src('Base Color')
    c = base
    mottle = g.noise('mottle', 14, 3, .6)
    c = g.mixc('mottle', g.rng('mottle range', mottle, .35, .65, 0, .35), c, (.5, .5, .5), 'MULTIPLY')
    cav = g.rng('cavity amount', g.ao('cavity', .045), .15, 1, 1, 0)
    c = g.mixc('cavity grime', g.math('grime', 'MULTIPLY', cav, grime), c, (.22, .21, .2), 'MULTIPLY')
    if edge_color is not None:
        e = g.edge('edge wear')
        wear = g.math('edge wear amount', 'MULTIPLY', e, edge)
        broken = g.rng('wear breakup', g.noise('edge breakup', 30, 3, .65), .32, .62)
        c = g.mixc('edge highlight', g.math('edge wear broken', 'MULTIPLY', wear, broken), c, edge_color)
    g.set_base(c)
    scratch_rough(g, .1)


def make_grip_rubber():
    src = mat('rubber')
    new = src.copy()
    new.name = P + 'grip rubber'
    nt = new.node_tree
    bs = nt.nodes['Principled BSDF']
    ramp = bs.inputs['Base Color'].links[0].from_node
    if ramp.type == 'VALTORGB':
        for stop in ramp.color_ramp.elements:
            stop.color = tuple(min(1, v * 3.4 + .012) if i < 3 else 1 for i, v in enumerate(stop.color))
    else:
        bs.inputs['Base Color'].default_value = (.075, .08, .085, 1)
    return new


def rubber_detail():
    for name in ('rubber', 'redrubber', 'grip rubber'):
        g = G(mat(name))
        base = g.src('Base Color')
        vor = g.n('ShaderNodeTexVoronoi', 'stipple', voronoi_dimensions='3D', feature='F1')
        vor.inputs['Scale'].default_value = 320
        g.link(g.tc.outputs['Object'], vor.inputs['Vector'])
        stip = g.rng('stipple height', vor.outputs['Distance'], .05, .55, 1, 0)
        g.set_base(g.mixc('rubber dust', g.rng('dust', g.noise('rubber dust noise', 9, 3, .6), .4, .7, 0, .22), base, (.2, .2, .2), 'ADD'))
        g.bump_in('stipple relief', stip, .55, .0015)


# --------------------------------------------------------------------------------------------------- 4. crisp hero props
HERO_ROOTS = ('SG0', 'TX01', 'TD01', 'RB0')
HERO_NAME_PARTS = ('Cabinet folded front frame', 'Door face folded', 'Portal mineral returned', 'Reserve opening', 'Reserve bay opening')


def sharpen_hero_props():
    count = 0
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        top = o
        while top.parent:
            top = top.parent
        hero = top.name.startswith(HERO_ROOTS) or any(p in o.name for p in HERO_NAME_PARTS)
        if not hero:
            continue
        for md in o.modifiers:
            if md.type == 'BEVEL':
                md.segments = 1
                md.width = max(md.width, .006)
                md.limit_method = 'ANGLE'
                md.angle_limit = math.radians(30)
                count += 1
    return count


# ---------------------------------------------------------------------------------------------------- 5. rubber grip pads
PAD_COLLECTION = 'EOH | Texture finish T1'


def build_pad(name, cx, cy, w, d, rot_deg, rib_along='x'):
    """A chamfered backing with parallel moulded ribs, one mesh, registered to Floor like the insulating mats."""
    bm = bmesh.new()
    cut = .035
    pts = [(-w / 2 + cut, -d / 2), (w / 2 - cut, -d / 2), (w / 2, -d / 2 + cut), (w / 2, d / 2 - cut),
           (w / 2 - cut, d / 2), (-w / 2 + cut, d / 2), (-w / 2, d / 2 - cut), (-w / 2, -d / 2 + cut)]
    verts = [bm.verts.new((x, y, 0)) for x, y in pts]
    face = bm.faces.new(verts)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    top = [v for v in res['geom'] if isinstance(v, bmesh.types.BMVert)]
    for v in top:
        v.co.z = .009
    bmesh.ops.delete(bm, geom=[face], context='FACES_ONLY')
    step = .032
    rw = .013
    n = int((d - .08) / step)
    for i in range(n):
        y = -d / 2 + .05 + i * step + rw / 2
        x0, x1 = -w / 2 + .05, w / 2 - .05
        corners = [(x0, y - rw / 2), (x1, y - rw / 2), (x1, y + rw / 2), (x0, y + rw / 2)]
        lo = [bm.verts.new((x, yy, .009)) for x, yy in corners]
        hi = [bm.verts.new((x, yy, .015)) for x, yy in corners]
        bm.faces.new(lo[::-1])
        bm.faces.new(hi)
        for k in range(4):
            bm.faces.new((lo[k], lo[(k + 1) % 4], hi[(k + 1) % 4], hi[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat('grip rubber'))
    coll = bpy.data.collections[PAD_COLLECTION]
    root = bpy.data.objects.new(name, None)
    root.location = (cx, cy, 0)
    root.rotation_euler = (0, 0, math.radians(rot_deg))
    root['assembly_root'] = True
    root['support_target'] = 'Floor'
    root['support_anchors'] = '[[0, 0, 0]]'
    root['support_direction'] = '[0, 0, -1]'
    root['electrical_grip_pad'] = True
    coll.objects.link(root)
    body = bpy.data.objects.new(name + ' moulded body', mesh)
    body.parent = root
    body['assembly_member'] = name
    coll.objects.link(body)
    mod = body.modifiers.new('Bevel', 'BEVEL')
    mod.width = .002
    mod.segments = 1
    mod.limit_method = 'ANGLE'
    body.modifiers.new('Weighted Normal', 'WEIGHTED_NORMAL')
    return root


def station_positions():
    """Pad layout from measured equipment extents (metres, room coordinates), so pads sit beside stations and never on the
    sampled walking lines (main aisle x=-.88/0/.88, reserve y=13.2, transfer y=10.3, bench y=13.9, switchgear y=4.0).

    Extents used: transformer plinth x3.08-5.28 y4.72-8.07; transfer cabinet x4.22-5.30 y9.46-11.14; reserve opening
    returns x5.50-5.75 (y11-12 and 14.4-15.4); repair bench x-5.2..-3.65 y12.7-15.2.
    """
    tx = bpy.data.objects['TX01_Guarded_dry_transformer'].matrix_world.translation
    return [
        # name, x, y, width, depth, rotation degrees
        ('Grip pad transformer gate', 2.35, tx.y + .0, .90, .70, 3),
        ('Grip pad transformer service', 2.5, 4.3, .60, .50, -6),
        ('Grip pad transfer cabinet', 3.6, 9.0, .80, .62, 4),
        ('Grip pad reserve threshold', 4.7, 12.5, .70, .90, 0),
        ('Grip pad workbench', -3.2, 12.2, .95, .62, 2),
        ('Grip pad draw-out end', -2.55, 2.55, .70, .55, 8),
        ('Grip pad entry side', 1.95, .95, .80, .55, 0),
        ('Grip pad rear side', -1.95, 15.45, .85, .55, -3),
    ]


# ---------------------------------------------------------------------------------------------------------- main
def apply():
    scene = bpy.context.scene
    assert scene.get('electrical_palette_revision'), 'Apply to the palette-finished source'
    assert not scene.get('electrical_texture_revision'), 'Texture finish already applied'
    pads = station_positions()
    zones = [
        (pads[0][1] - .1, pads[0][2] - .5, 1.7, 1.2),    # leak by the transformer gate
        (pads[2][1] + .2, pads[2][2] + .5, 1.5, 1.1),    # transfer cabinet
        (pads[3][1] - .4, pads[3][2] + .2, 1.5, 1.1),    # reserve bay approach
        (-2.9, 7.2, 1.2, 2.0),                           # switchgear draw-out
        (pads[4][1] + .3, pads[4][2] - .4, 1.5, 1.1),    # by the workbench
        (1.0, .8, 1.1, .8),                              # D01 threshold, off the centre line
        (-1.0, 15.6, 1.1, .8),                           # D02 threshold
    ]
    coll = bpy.data.collections.new(PAD_COLLECTION)
    bpy.data.collections['MODULE_electrical-room'].children.link(coll)

    rustic_wall_paint()
    wet_concrete('floor', zones, offset_y=8.2)
    wet_concrete('route', zones)
    wet_concrete('Coarse service epoxy', zones)
    concrete_extras('Floor contact history')
    for name, edge in (('enamel', (.62, .66, .7)), ('oxide', (.74, .28, .08)), ('ochre', (.86, .62, .14)), ('replacement', (.5, .56, .55))):
        metal_detail(name, edge, .85, .55)
    for name in ('steel', 'zinc', 'slate', 'Moulded reserve cell casing'):
        metal_detail(name, (.55, .6, .64) if name in ('steel', 'zinc') else None, .6, .5)
    make_grip_rubber()
    rubber_detail()
    bevels = sharpen_hero_props()
    pad_roots = [build_pad(*p).name for p in pads]
    scene['electrical_texture_revision'] = 'Rustic paint / wet concrete / grip pads / crisp hero edges T1'
    return {
        'wall_paint': 'chips over primer + rust, streaks, orange-peel relief, cavity grime',
        'concrete': 'flecks, pits, hairline cracks and %d bounded wet zones on the floor, aisle epoxy and service epoxy' % len(zones),
        'metal_materials_detailed': ['enamel', 'oxide', 'ochre', 'replacement', 'steel', 'zinc', 'slate', 'Moulded reserve cell casing'],
        'hero_bevel_modifiers_set_to_single_segment_chamfer': bevels,
        'grip_pads': pad_roots,
        'wet_zones_room_metres_cx_cy_rx_ry': [list(map(lambda v: round(v, 2), z)) for z in zones],
    }


if __name__ == '__main__':
    out, receipt = args()
    result = apply()
    if receipt:
        with open(receipt, 'w') as f:
            json.dump(result, f, indent=2)
    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out)
    print('texture_finish:', json.dumps(result)[:400])
