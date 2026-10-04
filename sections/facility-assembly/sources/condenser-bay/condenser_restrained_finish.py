"""Condenser bay restrained finish: art-direction-friendly materials and lighting, trimmed to the 400k triangle budget.

Run once against `module.blend` (the original R34 room) to produce an additive module:
    blender -b module.blend --python condenser_restrained_finish.py -- --output module_restrained_A1.blend --receipt restrained-build.json

Follows design/ART_DIRECTION.md: broad tonal variation, localized wear, a few puddles, no blanket grime, no scratch noise or
rust everywhere. Layout, interfaces, existing cameras and light placement are unchanged; no light is added or removed. Four new
review cameras are added. Changes: (1) calm slab floor with sparse cracks and a few puddles; (2) plaster and concrete with
broad staining and low wall scuffs only; (3) paint and steel with floor-level grime, cavity dirt and light edge wear at
contact materials; (4) practicals trimmed slightly, world fill lowered; (5) faint cool haze; (6) text, curve and small-object
bevel resolution lowered to fit 400,000 triangles.
"""
import json
import math
import sys

import bpy
from mathutils import Vector

REV = 'Condenser bay restrained finish'
BUDGET = 400000
FLOOR = ['Basement coated concrete', 'Replacement floor patch']
WALL = ['Warm mineral plaster', 'Dense cast concrete']
PAINT = ['Astra ivory painted steel', 'Service ochre enamel', 'Structural painted steel', 'Oxide orange enamel',
         'Light oxide enamel', 'Safety burgundy', 'Charcoal impact dado']
METAL = ['Astra brushed fastener steel', 'Oiled iron', 'Machined cast iron', 'Service brass', 'Matte vulcanized rubber']
CONTACT_EDGE = ('Service brass', 'Machined cast iron', 'Service ochre enamel', 'Astra brushed fastener steel')


def opts():
    a = sys.argv[sys.argv.index('--') + 1:]
    return (a[a.index('--output') + 1] if '--output' in a else None,
            a[a.index('--receipt') + 1] if '--receipt' in a else None)


def M(name):
    return bpy.data.materials[name]


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




def floor_calm(name):
    g = G(M(name))
    base = g.mix('floor darken', 1., g.base(), (.86, .86, .88), 'MULTIPLY')
    tone = g.mix('broad tone', g.rng('tone range', g.noise('tone noise', .9, 3, .5), .35, .65, 0, .3), base, (.55, .56, .56), 'MULTIPLY')
    cells = g.n('ShaderNodeTexVoronoi', 'crack cells', voronoi_dimensions='3D', feature='DISTANCE_TO_EDGE')
    cells.inputs['Scale'].default_value = .45
    g.L(g.pos(), cells.inputs['Vector'])
    line = g.rng('crack line', cells.outputs['Distance'], 0., .012, 1., 0.)
    crack = g.m('crack broken', 'MULTIPLY', line, g.rng('crack gaps', g.noise('crack gap noise', 1.0, 2, .5), .52, .6))
    c = g.mix('sparse cracks', g.m('crack strength', 'MULTIPLY', crack, .5), tone, (.05, .05, .055))
    pool = g.noise('puddle field', .3, 4, .55)
    wet = g.rng('puddle mask', pool, .67, .71)
    c = g.mix('wet darkening', g.m('wet dark', 'MULTIPLY', wet, .55), c, (.4, .42, .42), 'MULTIPLY')
    g.L(c, g.bs.inputs['Base Color'])
    r = g.mix('wet roughness', wet, g.rough() if not isinstance(g.rough(), float) else (g.rough(),) * 3, (.08,) * 3)
    g.L(g.m('rough floor', 'MAXIMUM', r, .06), g.bs.inputs['Roughness'])
    g.L(g.m('wet coat', 'MULTIPLY', wet, .6), g.bs.inputs['Coat Weight'])
    g.bs.inputs['Coat Roughness'].default_value = .05
    h = g.m('slab relief', 'ADD', g.m('swirl', 'MULTIPLY', g.noise('swirl', 3.5, 3, .5), .4), g.m('grain', 'MULTIPLY', g.noise('grain', 160, 3, .7), .3))
    g.bump('slab relief', h, .35, .003)


def wall_calm(name):
    g = G(M(name))
    base = g.base()
    blot = g.rng('blotch range', g.noise('blotches', 1.4, 4, .6), .35, .65, 0, .35)
    tone = g.mix('blotch tone', blot, base, (.45, .45, .44), 'MULTIPLY')
    geo = g.n('ShaderNodeNewGeometry', 'wall height')
    sep = g.n('ShaderNodeSeparateXYZ', 'wall height split')
    g.L(geo.outputs['Position'], sep.inputs[0])
    low = g.rng('low wall wear', sep.outputs['Z'], .05, .9, 1., 0.)
    scuff = g.m('scuff amount', 'MULTIPLY', low, g.rng('scuff breakup', g.noise('scuff noise', 5., 4, .6), .4, .62))
    c = g.mix('low scuffs', g.m('scuff strength', 'MULTIPLY', scuff, .45), tone, (.3, .3, .29), 'MULTIPLY')
    vor = g.n('ShaderNodeTexVoronoi', 'chip cells', voronoi_dimensions='3D', feature='F1')
    vor.inputs['Scale'].default_value = 2.2
    g.L(g.pos(), vor.inputs['Vector'])
    chip = g.rng('chip threshold', g.m('chip field', 'MULTIPLY', g.m('chip low', 'MULTIPLY', low, g.rng('chip cells range', vor.outputs['Distance'], .3, .75)), g.rng('chip grit', g.noise('chip grit', 30, 4, .7), .35, .8)), .22, .26)
    c = g.mix('few chips show primer', chip, c, (.2, .19, .18))
    c = g.mix('cavity grime', g.m('grime amount', 'MULTIPLY', g.cavity(.08), .3), c, (.45, .45, .43), 'MULTIPLY')
    g.L(c, g.bs.inputs['Base Color'])
    h = g.m('relief', 'ADD', g.m('peel relief', 'MULTIPLY', g.noise('orange peel', 80, 3, .6), .35), g.m('wave relief', 'MULTIPLY', g.noise('trowel', 3., 2, .5), .5))
    g.bump('plaster relief', h, .4, .004)
    g.L(g.m('plaster rough', 'ADD', .86, g.m('chip rough', 'MULTIPLY', chip, .08), clamp=True), g.bs.inputs['Roughness'])


def machine_calm(name, edge=None, edge_amount=.4, grime=.35, rust=0.):
    g = G(M(name))
    c = g.base()
    geo = g.n('ShaderNodeNewGeometry', 'dirt height')
    sep = g.n('ShaderNodeSeparateXYZ', 'dirt height split')
    g.L(geo.outputs['Position'], sep.inputs[0])
    low = g.rng('low dirt', sep.outputs['Z'], .0, .6, 1., 0.)
    breakup = g.rng('dirt breakup', g.noise('dirt noise', 5., 4, .6), .35, .65)
    c = g.mix('floor-level grime', g.m('grime gradient', 'MULTIPLY', low, g.m('grime breakup', 'MULTIPLY', breakup, .5)), c, (.5, .48, .45), 'MULTIPLY')
    if rust:
        rs = g.m('rust patch', 'MULTIPLY', g.m('rust low', 'MULTIPLY', low, g.rng('rust pick', g.noise('rust bloom', 8., 4, .65), .6, .68)), rust)
        c = g.mix('rust patch', rs, c, (.3, .11, .035))
    c = g.mix('mottle', g.rng('mottle range', g.noise('mottle', 10, 3, .6), .35, .65, 0, .2), c, (.7, .7, .7), 'MULTIPLY')
    c = g.mix('cavity grime', g.m('grime', 'MULTIPLY', g.cavity(.045), grime), c, (.45, .44, .42), 'MULTIPLY')
    if edge is not None:
        wear = g.m('edge wear', 'MULTIPLY', g.edges(.012), edge_amount)
        broken = g.rng('wear breakup', g.noise('edge breakup', 18, 3, .6), .42, .66)
        c = g.mix('edge highlight', g.m('edge broken', 'MULTIPLY', wear, broken), c, edge)
    g.L(c, g.bs.inputs['Base Color'])



def mood(scene):
    cut = {}
    for o in bpy.data.objects:
        if o.type != 'LIGHT' or o.data.energy <= 0:
            continue
        f = .85 if o.name.startswith('batten') else .9
        o.data.energy *= f
        cut[o.name] = f
        r, g, b = o.data.color
        o.data.color = (r * .97, g, min(1., b * 1.04))
    scene.view_settings.exposure -= .15
    nt = scene.world.node_tree
    for n in nt.nodes:
        if n.type == 'BACKGROUND':
            n.inputs['Strength'].default_value = .08
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD')
    vol = nt.nodes.new('ShaderNodeVolumeScatter')
    vol.label = 'AAA | cool haze'
    vol.inputs['Density'].default_value = .003
    vol.inputs['Anisotropy'].default_value = .5
    vol.inputs['Color'].default_value = (.7, .8, .86, 1)
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
    n = 0
    for limit in (1.0, 1.5, 2.5, 99):
        for o in bpy.data.objects:
            if o.type == 'MESH' and max(o.dimensions) < limit:
                for m in o.modifiers:
                    if m.type == 'BEVEL' and m.segments > 1:
                        m.segments = 1
                        n += 1
        if triangles() <= BUDGET - 8000:
            return n, limit
    return n, 99


CAMERAS = {
    'AAA01_WIDE_NE': ((9.3, 8.8, 3.0), (3.2, 3.2, 1.7), 21),
    'AAA02_PUMPS': ((1.2, 5.8, 1.5), (4.0, 7.9, 1.0), 24),
    'AAA03_OPERATOR': ((0.0, 1.6, 1.6), (-1.2, 4.3, 1.3), 22),
    'AAA04_PULL_BAY': ((6.4, 6.4, 1.6), (9.0, 2.5, 1.8), 22),
}


def add_cameras():
    col = bpy.data.collections['90 Evidence cameras']
    for n, (loc, tgt, lens) in CAMERAS.items():
        cam = bpy.data.cameras.new(n)
        cam.lens = lens
        cam.clip_start = .05
        ob = bpy.data.objects.new(n, cam)
        ob.location = loc
        ob.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        col.objects.link(ob)


def apply():
    s = bpy.context.scene
    assert not s.get('condenser_restrained_revision'), 'Condenser restrained finish already applied'
    before = triangles()
    lights = len([o for o in bpy.data.objects if o.type == 'LIGHT'])
    bevels_cut, limit = trim_geometry()
    done = {'floor': [], 'wall': [], 'paint': [], 'metal': []}
    for n in FLOOR:
        floor_calm(n); done['floor'].append(n)
    for n in WALL:
        wall_calm(n); done['wall'].append(n)
    for n in PAINT:
        machine_calm(n, (.6, .6, .57) if n in CONTACT_EDGE else None, .45, .35); done['paint'].append(n)
    for n in METAL:
        machine_calm(n, (.62, .64, .62) if n in CONTACT_EDGE else None, .4, .3, rust=.2 if n == 'Oiled iron' else 0.0); done['metal'].append(n)
    cut = mood(s)
    add_cameras()
    assert lights == len([o for o in bpy.data.objects if o.type == 'LIGHT'])
    after = triangles()
    s['condenser_restrained_revision'] = REV
    bpy.context.view_layer.update()
    return {'revision': REV, 'bevel_segments_cut': bevels_cut, 'bevel_cut_size_limit_m': limit, 'materials': done, 'light_scale': cut,
            'light_count_unchanged': True, 'exposure_now': s.view_settings.exposure, 'triangles_before': before,
            'triangles_after': after, 'triangle_budget': BUDGET, 'within_budget': after <= BUDGET, 'new_cameras': list(CAMERAS)}


if __name__ == '__main__':
    out, receipt = opts()
    result = apply()
    if receipt:
        json.dump(result, open(receipt, 'w'), indent=2)
    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out)
    print('CONDENSER:', json.dumps(result)[:700])
