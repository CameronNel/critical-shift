"""R25 AAA finish: deeper materials, crisper hero edges, harsher and scarier practical-only lighting.

Run once against the R24 candidate:
    blender -b module_overhaul_R1.blend --python revision_R25_aaa_finish.py -- --output NEW.blend --receipt REPORT.json

Changes: (1) wet, cracked, stained floor screed with bounded puddles; (2) rough chipped wall plaster with rust streaks and
cavity grime; (3) scratch/grime/edge-wear detail on painted and bare metal; (4) the thinnest machine bevels widen to 4 mm angle-limited
chamfers; (5) three more fixtures fail (nine of twenty-one), the rest are dimmer, tighter and sicklier; (6) a faint cold
haze volume lit only by the modelled fixtures. No geometry, camera, pose or interface change; world illumination stays 0.
"""
import json
import math
import sys

import bpy

REV = 'R25 AAA finish'
FLOOR = [f'RF1_screed_{i}' for i in range(4)]
WALL = ['RF1_cool_service_plaster', 'RF1_warmwall', 'RF1_dado']
PAINT = ['RF1_green', 'RF1_oxide', 'RF1_ochre', 'RF1_ivory', 'RF1_red', 'RF1_thermal_jacket_finish',
         'RF1_cast_hydraulic_powdercoat', 'RF1_muted_service_trunk', 'RF1_dark']
METAL = ['RF1_steel', 'RF1_black', 'RF1_brass', 'RF1_oxide_edge']
HERO_COLLECTIONS = ('MACHINE_',)
NEW_FAILURES = ['Wall service lamp 3', 'Eyewash service practical', 'Mine transfer wall bulkhead']


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
        node.label = 'R25 | ' + label
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


def floor_screed(name):
    g = G(M(name))
    base = g.base()
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
    wet = g.rng('puddle mask', pool, .56, .64)
    rim = g.m('puddle rim', 'MULTIPLY', g.rng('rim band', pool, .53, .6), g.rng('rim fade', pool, .66, .6, 0., 1.))
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
    base = g.mix('lift plaster', 1., base, (2.1, 2.2, 2.0), 'MULTIPLY')
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


def machine_detail(name, edge, edge_amount=.8, grime=.55):
    g = G(M(name))
    c = g.base()
    c = g.mix('mottle', g.rng('mottle range', g.noise('mottle', 14, 3, .6), .35, .65, 0, .35), c, (.5, .5, .5), 'MULTIPLY')
    c = g.mix('cavity grime', g.m('grime', 'MULTIPLY', g.cavity(.045), grime), c, (.22, .21, .2), 'MULTIPLY')
    if edge is not None:
        wear = g.m('edge wear', 'MULTIPLY', g.edges(.012), edge_amount)
        broken = g.rng('wear breakup', g.noise('edge breakup', 30, 3, .65), .32, .62)
        c = g.mix('edge highlight', g.m('edge broken', 'MULTIPLY', wear, broken), c, edge)
    g.L(c, g.bs.inputs['Base Color'])
    t = g.n('ShaderNodeMapping', 'scratch stretch')
    t.inputs['Scale'].default_value = (14, 56, 14)
    g.L(g.pos(), t.inputs['Vector'])
    sc = g.noise('scratch', 1., 2, .5, vec=t.outputs['Vector'])
    delta = g.rng('scratch delta', sc, .35, .65, -.1, .1, clamp=False)
    g.L(g.m('scratch rough', 'ADD', g.rough(), delta, clamp=True), g.bs.inputs['Roughness'])


def sharpen_hero():
    count = 0
    for o in bpy.data.objects:
        if o.type != 'MESH' or not any(c.name.startswith(HERO_COLLECTIONS) for c in o.users_collection):
            continue
        # keep support-registered assemblies' evaluated geometry exactly as validated
        if any(c.name == 'CS_SUPPORT_REQUIRED' for c in o.users_collection) or any(
                ch.name.startswith('SUPPORT_') for ch in o.children_recursive) or o.parent is not None and any(
                ch.name.startswith('SUPPORT_') for ch in o.parent.children_recursive):
            continue
        for md in o.modifiers:
            if md.type == 'BEVEL' and md.width < .004:
                md.segments = 1
                md.width = .004
                md.limit_method = 'ANGLE'
                md.angle_limit = math.radians(30)
                count += 1
    return count


def lighting(scene):
    registry = json.loads(scene['failed_fixture_registry'])
    lens_black = (.043, .055, .044)
    for key in NEW_FAILURES:
        light = bpy.data.objects['RF1 LIGHT | ' + key]
        assert light.data.energy > 0
        light.data.energy = 0
        lens = bpy.data.objects[light['fixture_lens']]
        for slot in lens.material_slots:
            for node in slot.material.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    node.inputs['Emission Strength'].default_value = 0
                    node.inputs['Base Color'].default_value = (*lens_black, 1)
        lens['electrical_state'] = light['electrical_state'] = 'failed'
        registry.append(dict(light=light.name, lens=lens.name, energy=0, shader_emission=0))
    scene['failed_fixture_registry'] = json.dumps(registry)
    scale = {'Ceiling pendant 0': 1.0, 'Ceiling pendant 1': 1.0, 'Ceiling pendant 2': 1.1, 'Ceiling pendant 4': .9,
             'PV hood 0': 1.3, 'Press task bar': 1.3, 'Mine threshold practical': .8,
             'Personnel threshold practical': .8, 'Fuel transfer threshold practical': .9,
             'Inspection sample practical': 1.2, 'Work nook lamp': 1.0}
    for key, f in scale.items():
        light = bpy.data.objects['RF1 LIGHT | ' + key]
        light.data.energy *= f
    for o in bpy.data.objects:
        if o.type == 'LIGHT' and o.data.energy > 0:
            o.data.spread = math.radians(130 if o.data.size > .5 else 150)
            r, g, b = o.data.color
            o.data.color = (r * .96, min(1, g * 1.02), b * .93)   # a little sicker
    # faint cold haze: lit only by the modelled fixtures; world emission stays zero
    nt = scene.world.node_tree
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD')
    vol = nt.nodes.new('ShaderNodeVolumeScatter')
    vol.label = 'R25 | cold haze'
    vol.inputs['Density'].default_value = .004
    vol.inputs['Anisotropy'].default_value = .45
    vol.inputs['Color'].default_value = (.62, .78, .70, 1)
    nt.links.new(vol.outputs['Volume'], out.inputs['Volume'])
    scene.cycles.volume_bounces = 1
    scene.cycles.volume_max_steps = 64


def lighten_text(res=6):
    """Printed legends are flat; 12 curve segments per Bezier span is far more than they need."""
    n = 0
    for o in bpy.data.objects:
        if o.type == 'FONT' and o.data.resolution_u > res:
            if o.data.users > 1:
                o.data = o.data.copy()
            o.data.resolution_u = res
            n += 1
    return n


def triangles():
    dg = bpy.context.evaluated_depsgraph_get()
    total = vis = 0
    for o in bpy.data.objects:
        if o.type not in ('MESH', 'CURVE', 'FONT'):
            continue
        ev = o.evaluated_get(dg)
        m = ev.to_mesh()
        t = sum(len(p.vertices) - 2 for p in m.polygons)
        ev.to_mesh_clear()
        total += t
        if not (o.hide_render or o.hide_viewport):
            vis += t
    return total, vis


def apply():
    s = bpy.context.scene
    assert not s.get('refinery_aaa_revision'), 'R25 already applied'
    before = triangles()
    for n in FLOOR:
        floor_screed(n)
    for n in WALL:
        wall_plaster(n)
    for n in PAINT:
        machine_detail(n, (.55, .58, .56) if n != 'RF1_dark' else None, .8, .6)
    for n in METAL:
        machine_detail(n, (.62, .64, .62), .7, .5)
    bevels = sharpen_hero()
    text_objects = lighten_text()
    lighting(s)
    after = triangles()
    s['refinery_aaa_revision'] = REV
    bpy.context.view_layer.update()
    return {'revision': REV, 'floor_materials': FLOOR, 'wall_materials': WALL, 'paint_materials': PAINT,
            'metal_materials': METAL, 'hero_bevels_to_single_segment': bevels,
            'font_objects_resolution_reduced_to_6': text_objects, 'new_failed_fixtures': NEW_FAILURES, 'triangles_before_total_visible': before,
            'triangles_after_total_visible': after, 'triangle_budget_visible': 400000,
            'within_budget': after[1] <= 400000}


if __name__ == '__main__':
    out, receipt = opts()
    result = apply()
    if receipt:
        json.dump(result, open(receipt, 'w'), indent=2)
    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out)
    print('R25:', json.dumps(result)[:500])
