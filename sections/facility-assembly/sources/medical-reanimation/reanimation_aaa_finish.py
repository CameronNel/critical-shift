"""Reanimation room AAA finish: deeper materials, crisper edges, harsher mood, lighter text legends.

Run once against `module_overhaul_R2.blend`:
    blender -b module_overhaul_R2.blend --python reanimation_aaa_finish.py -- --output NEW.blend --receipt REPORT.json

Same treatment as the electrical, refinery and fuel stages. The room's lighting contract is exactly four active lights
(one red OCRU area, one warm supply practical, two dim spots), checked by verify_overhaul.py, so no light is added, removed
or re-powered; mood comes from materials, exposure, a faint haze and tighter light spreads.
Changes: (1) wet, cracked floor with world-space puddles; (2) rough chipped wall plaster; (3) scratch/grime/edge-wear on
enamels, steel and ivory; (4) edge wear in the shader only (bevel modifiers untouched: they moved support gaps); (5) tighter spreads, exposure lowered
0.5 EV, faint cold haze lit only by the room's lights; (7) the interrupted-recovery care sheet (40k triangles, no contact assembly) gets a 0.35 collapse-decimate modifier; (6) newly authored text legends drop from 12 to 4 curve segments per span (inherited ones keep 12).
No geometry placement, camera, interface or light-count/energy change.
"""
import json
import math
import sys

import bpy

REV = 'Reanimation AAA finish'
SCENE = 'REANIMATION_EDIT_LOCAL'
FLOOR = ['MED | Matte plum-grey sealed floor / approved spawn graph', 'MED | Decon floor / measured 600mm tiles']
WALL = ['MED | Mauve mineral plaster / approved spawn graph', 'MED | Old utility damp plaster']
PAINT = ['MED | Navy impact enamel / approved spawn graph', 'MED | Institutional blue enamel / approved spawn graph',
         'MED | Terracotta equipment enamel / approved spawn graph', 'MED | Warm ivory porcelain / approved spawn graph',
         'MED | Worn warm ivory instrument enamel', 'MED | Ochre safety enamel', 'Structural warm graphite',
         'Switch housing phenolic', 'MED | Charcoal elastomer']
METAL = ['MED | Machined zinc steel / approved spawn graph', 'Exposed steel at contact wear', 'Bus copper - aged']


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
    base = g.mix('lift plaster', 1., base, (.85, .88, .85), 'MULTIPLY')
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


def sharpen_bevels():
    n = 0
    for o in bpy.data.objects:
        for md in o.modifiers:
            if md.type == 'BEVEL' and md.segments > 1:
                md.segments = 1
                md.width = max(md.width, .003)
                md.limit_method = 'ANGLE'
                md.angle_limit = math.radians(30)
                n += 1
    return n


def inherited_names():
    import pathlib
    base = pathlib.Path(__file__).resolve().parent / 'revamp-review' / 'baseline.json'
    return {rec['name'] for rec in json.loads(base.read_text())['objects']}


def decimate_new_dense(ratio=.35, min_tris=3000):
    """Collapse-decimate dense, newly authored meshes only (inherited objects are held to exact bounds)."""
    keep = inherited_names()
    n = 0
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name in keep or o.hide_render or o.hide_viewport:
            continue
        if sum(len(p.vertices) - 2 for p in o.data.polygons) < min_tris:
            continue
        if 'care sheet' not in o.name.lower():   # body bag / dispensing tray / etc. carry contact assemblies the verifier checks
            continue
        md = o.modifiers.new('R25 collapse', 'DECIMATE')
        md.decimate_type = 'COLLAPSE'
        md.ratio = ratio
        o.modifiers.move(len(o.modifiers) - 1, 0)
        n += 1
    return n


def lighten_text(res=4):
    """Only newly authored legends: inherited objects are held to a 1e-6 m dimension check."""
    n = 0
    keep = inherited_names()
    for o in bpy.data.objects:
        if o.type == 'FONT' and o.name not in keep and o.data.resolution_u > res:
            if o.data.users > 1:
                o.data = o.data.copy()
            o.data.resolution_u = res
            n += 1
    return n


def mood(scene):
    for o in bpy.data.objects:
        if o.type == 'LIGHT' and o.data.energy > 0 and o.data.type == 'AREA':
            o.data.spread = math.radians(min(math.degrees(o.data.spread), 130))
    scene.view_settings.exposure -= .5
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
    s = bpy.data.scenes[SCENE] if SCENE in bpy.data.scenes else bpy.context.scene
    assert not s.get('reanimation_aaa_revision'), 'Reanimation AAA finish already applied'
    lights = sorted((o.name, o.data.energy, tuple(o.data.color)) for o in bpy.data.objects if o.type == 'LIGHT')
    before = triangles()
    done = {'floor': [], 'wall': [], 'paint': [], 'metal': []}
    for n in FLOOR:
        if n in bpy.data.materials:
            floor_screed(n); done['floor'].append(n)
    for n in WALL:
        if n in bpy.data.materials:
            wall_plaster(n); done['wall'].append(n)
    for n in PAINT:
        if n in bpy.data.materials:
            machine_detail(n, (.55, .58, .56), .8, .6); done['paint'].append(n)
    for n in METAL:
        if n in bpy.data.materials:
            machine_detail(n, (.62, .64, .62), .7, .5); done['metal'].append(n)
    bevels = 0   # bevel changes shift small parts' bounds and support gaps; edges are sharpened by shader wear only
    texts = lighten_text()
    decimated = decimate_new_dense()
    mood(s)
    assert lights == sorted((o.name, o.data.energy, tuple(o.data.color)) for o in bpy.data.objects if o.type == 'LIGHT'), 'light changed'
    after = triangles()
    s['reanimation_aaa_revision'] = REV
    bpy.context.view_layer.update()
    return {'revision': REV, 'materials': done, 'font_objects_reduced_to_4': texts, 'bevel_modifiers_changed': bevels, 'new_dense_meshes_collapse_decimated_to_0.35': decimated,
            'lights_unchanged': True, 'triangles_before_total_visible': before,
            'triangles_after_total_visible': after, 'triangle_budget': 500000,
            'within_budget': after[1] <= 500000}


if __name__ == '__main__':
    out, receipt = opts()
    result = apply()
    if receipt:
        json.dump(result, open(receipt, 'w'), indent=2)
    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out)
    print('REANIM:', json.dumps(result)[:500])
