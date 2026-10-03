"""Cooling plant AAA finish: weathered materials, harsher gloomy lighting, haze, trimmed to the 400k triangle budget.

Run once against `module.blend` (the original R10 room) to produce an additive module:
    blender -b module.blend --python cooling_aaa_finish.py -- --output module_aaa_A1.blend --receipt aaa-build.json

Geometry layout, interfaces, existing cameras and light placement are unchanged; no light is added or removed. Four new review
cameras are added. Changes: (1) wet cracked stained floor; (2) rough chipped rusted wall paint; (3) grime, scratches, rust and edge
wear on paint and steel; (4) fills cut, practicals tinted cooler; (5) exposure and world fill lowered; (6) a faint cold haze lit by
the room's own lights; (7) text/curve resolution and small-object bevel segments reduced to fit 400,000 triangles.
"""
import json
import math
import sys

import bpy
from mathutils import Vector

REV = 'Cooling plant AAA finish'
BUDGET = 400000
FLOOR = ['floor', 'patch']
WALL = ['mineral']
PAINT = ['cream', 'yellow', 'oxide paint', 'oxide paint light', 'orange', 'red', 'dark', 'neutral service steel']
RUSTY = ('dark', 'yellow', 'oxide paint', 'cream')
METAL = ['steel', 'edge', 'rubber']


def opts():
    a = sys.argv[sys.argv.index('--') + 1:]
    return (a[a.index('--output') + 1] if '--output' in a else None,
            a[a.index('--receipt') + 1] if '--receipt' in a else None)


class G:
    def __init__(self, mat):
        self.nt, self.mat = mat.node_tree, mat
        self.bs = self.nt.nodes['Principled BSDF']

    def n(self, kind, label, **kw):
        node = self.nt.nodes.new(kind)
        node.label = 'AAA | ' + label
        for k, v in kw.items():
            setattr(node, k, v)
        return node

    def L(self, a, b):
        self.nt.links.new(a, b)

    def src(self, key):
        s = self.bs.inputs[key]
        return s.links[0].from_socket if s.is_linked else None

    def pos(self):
        geo = self.n('ShaderNodeNewGeometry', 'geometry')
        return geo.outputs['Position']

    def noise(self, label, scale, detail=3, rough=.6, vec=None):
        node = self.n('ShaderNodeTexNoise', label)
        node.inputs['Scale'].default_value = scale
        node.inputs['Detail'].default_value = detail
        node.inputs['Roughness'].default_value = rough
        self.L(vec if vec is not None else self.pos(), node.inputs['Vector'])
        return node.outputs['Fac']

    def rng(self, label, sock, a, b, lo=0., hi=1., clamp=True):
        node = self.n('ShaderNodeMapRange', label)
        node.clamp = clamp
        node.inputs['From Min'].default_value = a
        node.inputs['From Max'].default_value = b
        node.inputs['To Min'].default_value = lo
        node.inputs['To Max'].default_value = hi
        self.L(sock, node.inputs[0])
        return node.outputs[0]

    def m(self, label, op, a, b=None, clamp=False):
        node = self.n('ShaderNodeMath', label, operation=op, use_clamp=clamp)
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                node.inputs[i].default_value = v
            else:
                self.L(v, node.inputs[i])
        return node.outputs[0]

    def mix(self, label, fac, c1, c2, blend='MIX'):
        node = self.n('ShaderNodeMixRGB', label, blend_type=blend)
        if isinstance(fac, (int, float)):
            node.inputs[0].default_value = fac
        else:
            self.L(fac, node.inputs[0])
        for i, c in ((1, c1), (2, c2)):
            if isinstance(c, tuple):
                node.inputs[i].default_value = (*c[:3], 1)
            else:
                self.L(c, node.inputs[i])
        return node.outputs[0]

    def base(self):
        s = self.src('Base Color')
        if s is not None:
            return s
        node = self.n('ShaderNodeRGB', 'base constant')
        node.outputs[0].default_value = self.bs.inputs['Base Color'].default_value
        return node.outputs[0]

    def rough(self):
        s = self.src('Roughness')
        if s is not None:
            return s
        return self.bs.inputs['Roughness'].default_value

    def bump(self, label, height, strength, distance):
        prev = self.src('Normal')
        node = self.n('ShaderNodeBump', label)
        node.inputs['Strength'].default_value = strength
        node.inputs['Distance'].default_value = distance
        self.L(height, node.inputs['Height'])
        if prev is not None:
            self.L(prev, node.inputs['Normal'])
        self.L(node.outputs['Normal'], self.bs.inputs['Normal'])

    def cavity(self, dist=.06):
        ao = self.n('ShaderNodeAmbientOcclusion', 'cavity', samples=6)
        ao.inputs['Distance'].default_value = dist
        return self.rng('cavity amount', ao.outputs['AO'], .1, 1., 1., 0.)

    def edges(self, radius=.01):
        bev = self.n('ShaderNodeBevel', 'edge bevel', samples=4)
        bev.inputs['Radius'].default_value = radius
        geo = self.n('ShaderNodeNewGeometry', 'edge geometry')
        dot = self.n('ShaderNodeVectorMath', 'edge dot', operation='DOT_PRODUCT')
        self.L(bev.outputs['Normal'], dot.inputs[0])
        self.L(geo.outputs['Normal'], dot.inputs[1])
        inv = self.m('edge invert', 'SUBTRACT', 1., dot.outputs['Value'])
        return self.rng('edge mask', inv, .004, .08)


def M(name):
    return bpy.data.materials[name]


def floor_screed(name, dark=1.0, wet_lo=.56, wet_hi=.64):
    g = G(M(name))
    base = g.mix('floor darken', 1., g.base(), (dark, dark, dark * 1.02), 'MULTIPLY')
    fleck = g.n('ShaderNodeTexVoronoi', 'aggregate', voronoi_dimensions='3D', feature='F1')
    fleck.inputs['Scale'].default_value = 120
    g.L(g.pos(), fleck.inputs['Vector'])
    c = g.mix('light aggregate', g.rng('aggregate range', fleck.outputs['Distance'], .16, .05, 0, .5), base, (.30, .32, .30))
    c = g.mix('pits', g.rng('pit range', g.noise('pit noise', 190, 2, .7), .6, .72, 0, .6), c, (.01, .012, .012))
    cells = g.n('ShaderNodeTexVoronoi', 'crack cells', voronoi_dimensions='3D', feature='DISTANCE_TO_EDGE')
    cells.inputs['Scale'].default_value = .5
    g.L(g.pos(), cells.inputs['Vector'])
    line = g.rng('crack line', cells.outputs['Distance'], 0., .014, 1., 0.)
    crack = g.m('crack broken', 'MULTIPLY', line, g.rng('crack gaps', g.noise('crack gap noise', 1.1, 2, .5), .46, .58))
    c = g.mix('cracks', g.m('crack strength', 'MULTIPLY', crack, .95), c, (.006, .007, .007))
    # world-space puddles, about a fifth of the slab, with noisy edges and a dark pooled rim
    pool = g.noise('puddle field', .42, 4, .55)
    wet = g.rng('puddle mask', pool, wet_lo, wet_hi)
    rim = g.m('puddle rim', 'MULTIPLY', g.rng('rim band', pool, wet_lo - .03, wet_lo + .04), g.rng('rim fade', pool, wet_hi + .02, wet_lo + .04, 0., 1.))
    c = g.mix('wet darkening', g.m('wet dark', 'MULTIPLY', wet, .8), c, (.16, .19, .18), 'MULTIPLY')
    c = g.mix('wet rim grime', g.m('rim amount', 'MULTIPLY', rim, .6), c, (.02, .024, .022), 'MULTIPLY')
    g.L(c, g.bs.inputs['Base Color'])
    r = g.mix('wet roughness', wet, g.rough() if not isinstance(g.rough(), float) else (g.rough(),) * 3, (.06,) * 3)
    g.L(g.m('rough floor', 'MAXIMUM', r, .05), g.bs.inputs['Roughness'])
    g.L(g.m('wet coat', 'MULTIPLY', wet, .7), g.bs.inputs['Coat Weight'])
    g.bs.inputs['Coat Roughness'].default_value = .04
    h = g.m('slab relief', 'ADD', g.m('swirl', 'MULTIPLY', g.noise('swirl', 4., 3, .5), .5), g.m('grain', 'MULTIPLY', g.noise('grain', 240, 3, .75), .7))
    h = g.m('relief with cracks', 'SUBTRACT', h, g.m('crack depth', 'MULTIPLY', crack, 1.4))
    h = g.m('wet fills relief', 'MULTIPLY', h, g.m('relief factor', 'SUBTRACT', 1., g.m('wet85', 'MULTIPLY', wet, .85)))
    g.bump('slab relief', h, .6, .004)


def wall_plaster(name):
    g = G(M(name))
    base = g.base()
    blot = g.rng('blotch range', g.noise('blotches', 1.7, 4, .62), .35, .65, 0, .55)
    base = g.mix('lift plaster', 1., base, (.92, .94, .94), 'MULTIPLY')
    tone = g.mix('blotch tone', blot, base, (.20, .21, .20), 'MULTIPLY')
    vor = g.n('ShaderNodeTexVoronoi', 'chip cells', voronoi_dimensions='3D', feature='F1')
    vor.inputs['Scale'].default_value = 3.0
    g.L(g.pos(), vor.inputs['Vector'])
    grit = g.noise('chip grit', 36, 4, .7)
    field = g.m('chip field', 'MULTIPLY', g.rng('chip cells range', vor.outputs['Distance'], .25, .75), g.rng('grit range', grit, .35, .8))
    geo = g.n('ShaderNodeNewGeometry', 'wall height')
    sep = g.n('ShaderNodeSeparateXYZ', 'wall height split')
    g.L(geo.outputs['Position'], sep.inputs[0])
    cav = g.cavity(.08)
    low = g.rng('low wall wear', sep.outputs['Z'], .1, 2.0, 1., 0.)
    wear = g.m('chip likelihood', 'ADD', g.m('chip base', 'MULTIPLY', g.rng('chip pick', field, .45, .75), .7), g.m('chip low', 'MULTIPLY', low, .5), clamp=True)
    wear = g.m('chip with cavities', 'ADD', wear, g.m('cavity chips', 'MULTIPLY', cav, .3), clamp=True)
    chip = g.rng('chip threshold', wear, .40, .47)
    rust = g.m('rust in chips', 'MULTIPLY', chip, g.rng('rust pick', g.noise('rust spots', 7, 3, .6), .46, .6))
    c = g.mix('chips show primer', chip, tone, (.05, .056, .052))
    c = g.mix('rust', rust, c, (.20, .075, .028))
    stretch = g.n('ShaderNodeMapping', 'streak stretch')
    stretch.inputs['Scale'].default_value = (11, 11, .5)
    g.L(g.pos(), stretch.inputs['Vector'])
    sn = g.noise('streak noise', 1., 3, .5, vec=stretch.outputs['Vector'])
    c = g.mix('drip streaks', g.rng('streaks', sn, .48, .72, 0, .6), c, (.07, .06, .05), 'MULTIPLY')
    c = g.mix('cavity grime', g.m('grime amount', 'MULTIPLY', cav, .65), c, (.26, .26, .24), 'MULTIPLY')
    g.L(c, g.bs.inputs['Base Color'])
    peel = g.noise('orange peel', 95, 3, .7)
    wave = g.noise('trowel', 3.2, 2, .55)
    h = g.m('relief', 'ADD', g.m('peel relief', 'MULTIPLY', peel, .7), g.m('wave relief', 'MULTIPLY', wave, .9))
    h = g.m('relief chips', 'SUBTRACT', h, g.m('chip depth', 'MULTIPLY', chip, .35))
    g.bump('rough plaster relief', h, .85, .006)
    rough = g.m('paint roughness', 'ADD', .86, g.m('chip rough', 'MULTIPLY', chip, .12), clamp=True)
    g.L(g.m('rough grit', 'ADD', rough, g.rng('grit rough', peel, .3, .7, -.05, .05), clamp=True), g.bs.inputs['Roughness'])


def machine_detail(name, edge, edge_amount=1.0, grime=.7, rust=0.0):
    g = G(M(name))
    c = g.base()
    geo = g.n('ShaderNodeNewGeometry', 'dirt height')
    sep = g.n('ShaderNodeSeparateXYZ', 'dirt height split')
    g.L(geo.outputs['Position'], sep.inputs[0])
    low = g.rng('low dirt', sep.outputs['Z'], .0, 1.2, 1., 0.)
    breakup = g.rng('dirt breakup', g.noise('dirt noise', 6., 4, .6), .35, .65)
    c = g.mix('floor-level grime', g.m('grime gradient', 'MULTIPLY', low, g.m('grime breakup', 'MULTIPLY', breakup, .85)), c, (.30, .28, .25), 'MULTIPLY')
    if rust:
        rs = g.m('rust gradient', 'MULTIPLY', g.m('rust low', 'MULTIPLY', low, g.rng('rust pick', g.noise('rust bloom', 9., 4, .65), .5, .66)), rust)
        c = g.mix('rust bloom', rs, c, (.30, .11, .035))
    c = g.mix('mottle', g.rng('mottle range', g.noise('mottle', 14, 3, .6), .35, .65, 0, .35), c, (.5, .5, .5), 'MULTIPLY')
    c = g.mix('cavity grime', g.m('grime', 'MULTIPLY', g.cavity(.045), grime), c, (.22, .21, .2), 'MULTIPLY')
    if edge is not None:
        wear = g.m('edge wear', 'MULTIPLY', g.edges(.015), edge_amount)
        broken = g.rng('wear breakup', g.noise('edge breakup', 30, 3, .65), .32, .62)
        c = g.mix('edge highlight', g.m('edge broken', 'MULTIPLY', wear, broken), c, edge)
    g.L(c, g.bs.inputs['Base Color'])
    t = g.n('ShaderNodeMapping', 'scratch stretch')
    t.inputs['Scale'].default_value = (14, 56, 14)
    g.L(g.pos(), t.inputs['Vector'])
    sc = g.noise('scratch', 1., 2, .5, vec=t.outputs['Vector'])
    delta = g.rng('scratch delta', sc, .3, .7, -.2, .2, clamp=False)
    g.L(g.m('scratch rough', 'ADD', g.rough(), delta, clamp=True), g.bs.inputs['Roughness'])



def mood(scene):
    cut = {}
    scale = {'broad neutral ceiling fill': .2, 'soft motor return': .25, 'workshop lower service fill': .4, 'west wall rake': .5,
             'entry borrowed corridor light': .5, 'exchanger side wall shaping': .6}
    for o in bpy.data.objects:
        if o.type != 'LIGHT' or o.data.energy <= 0:
            continue
        f = scale.get(o.name, .8)
        o.data.energy *= f
        cut[o.name] = f
        r, g, b = o.data.color
        o.data.color = (r * .93, g * .97, min(1., b * 1.03))
        if o.data.type == 'AREA':
            o.data.spread = math.radians(min(math.degrees(o.data.spread), 100))
    scene.view_settings.exposure -= .5
    nt = scene.world.node_tree
    for n in nt.nodes:
        if n.type == 'BACKGROUND' and n.inputs['Strength'].default_value < .5:
            n.inputs['Strength'].default_value = .02
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD')
    vol = nt.nodes.new('ShaderNodeVolumeScatter')
    vol.label = 'AAA | cold haze'
    vol.inputs['Density'].default_value = .007
    vol.inputs['Anisotropy'].default_value = .5
    vol.inputs['Color'].default_value = (.66, .78, .84, 1)
    nt.links.new(vol.outputs['Volume'], out.inputs['Volume'])
    scene.cycles.volume_bounces = 1
    scene.cycles.volume_max_steps = 64
    return cut


def triangles():
    dg = bpy.context.evaluated_depsgraph_get()
    total = 0
    for o in bpy.data.objects:
        if o.type not in ('MESH', 'CURVE', 'FONT'):
            continue
        ev = o.evaluated_get(dg)
        m = ev.to_mesh()
        total += sum(len(p.vertices) - 2 for p in m.polygons)
        ev.to_mesh_clear()
    return total


def trim_geometry():
    for o in bpy.data.objects:
        if o.type in ('CURVE', 'FONT'):
            d = o.data
            d.resolution_u = max(1, min(d.resolution_u, 2))
            d.render_resolution_u = 0
            d.bevel_resolution = 0
    small = 0
    for o in bpy.data.objects:
        if o.type == 'MESH' and max(o.dimensions) < 1.0:
            for m in o.modifiers:
                if m.type == 'BEVEL' and m.segments > 1:
                    m.segments = 1
                    small += 1
    return small


CAMERAS = {
    'AAA01_WIDE_REAR': ((-1.2, 12.5, 3.3), (1.0, 2.0, 1.5), 20),
    'AAA02_EXCHANGER_LOW': ((-.9, 3.0, .75), (2.6, 6.3, 1.2), 26),
    'AAA03_PUMP_ROW': ((.8, 9.6, 2.1), (-3.4, 4.6, 1.0), 24),
    'AAA04_WORKSHOP': ((1.0, 8.6, 1.7), (-4.0, 12.2, 1.4), 24),
}


def add_cameras():
    col = bpy.data.collections['MODULE_cooling-plant']
    for n, (loc, tgt, lens) in CAMERAS.items():
        cam = bpy.data.cameras.new(n)
        cam.lens = lens
        cam.clip_start = .05
        ob = bpy.data.objects.new(n, cam)
        ob.location = loc
        d = Vector(tgt) - Vector(loc)
        ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        col.objects.link(ob)


def apply():
    s = bpy.context.scene
    assert not s.get('cooling_aaa_revision'), 'Cooling AAA finish already applied'
    before = triangles()
    lights = len([o for o in bpy.data.objects if o.type == 'LIGHT'])
    small = trim_geometry()
    done = {'floor': [], 'wall': [], 'paint': [], 'metal': []}
    for n in FLOOR:
        if n in bpy.data.materials:
            floor_screed(n, dark=.55, wet_lo=.47, wet_hi=.55); done['floor'].append(n)
    for n in WALL:
        if n in bpy.data.materials:
            wall_plaster(n); done['wall'].append(n)
    for n in PAINT:
        if n in bpy.data.materials:
            machine_detail(n, (.58, .6, .58), 1.0, .7, rust=.4 if n in RUSTY else 0.0); done['paint'].append(n)
    for n in METAL:
        if n in bpy.data.materials:
            machine_detail(n, (.62, .64, .62), .9, .6, rust=.5 if n == 'steel' else 0.0); done['metal'].append(n)
    cut = mood(s)
    add_cameras()
    assert lights == len([o for o in bpy.data.objects if o.type == 'LIGHT'])
    after = triangles()
    s['cooling_aaa_revision'] = REV
    bpy.context.view_layer.update()
    return {'revision': REV, 'bevel_segments_cut_on_small_objects': small, 'materials': done, 'light_scale': cut,
            'light_count_unchanged': True, 'exposure_now': s.view_settings.exposure, 'triangles_before': before,
            'triangles_after': after, 'triangle_budget': BUDGET, 'within_budget': after <= BUDGET, 'new_cameras': list(CAMERAS)}


if __name__ == '__main__':
    out, receipt = opts()
    result = apply()
    if receipt:
        json.dump(result, open(receipt, 'w'), indent=2)
    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out)
    print('COOLING:', json.dumps(result)[:700])
