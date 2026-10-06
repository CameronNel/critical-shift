"""Scatter of worked-in depot clutter on the mud: a fire barrel, tyre stacks, drums, sandbags, barriers, cones, crates on pallets, tools.
Every candidate position is tested against the bounds of everything already standing in the yard and against the required clear lanes,
so nothing is placed inside anything or across a route. Deterministic."""
import math, random
from fe_common import *
from fe_assets_int import STD, I, mb
from fe_assets_yard import barrel, tyre, cone, crate, pallet, cable_drum
from fe_assets_site import jersey, sandbags, bucket, wheelbarrow, toolbox
from fe_yard import inst
from fe_yard3 import on_pad

SKIP = ('yard_earth', 'pad_', 'floor_', 'context_', 'yard_base', 'ground_cracks', 'stone_', 'ballast', 'cliff', 'streak', 'stain', 'rail_', 'wear', 'sign_', 'board_', 'drain_')
CLEAR = [(-49.0, -8.0, -71.4, -68.6), (-23.6, -20.8, -71.0, -59.5), (-29.8, -26.2, -84.5, -71.0), (-47.5, -44.7, -69.0, -59.5), (-12.7, -7.8, -85.0, -59.0)]

def _boxes():
    out = []; bpy.context.view_layer.update()
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name.startswith(SKIP) or o.hide_render: continue
        try: cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
        except Exception: continue
        if min(c.z for c in cs) > 3.0 or max(c.z for c in cs) < 0.02: continue
        out.append((min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs)))
    return out

def build_yard_props(F, C):
    yard = C['YARD']; P = collection('PROTOTYPES'); rnd = random.Random(2026)
    boxes = _boxes()
    pr = {'drum_blue': barrel(F, P, (0.07, 0.09, 0.20, 1), 'drum_blue'), 'drum_red': barrel(F, P, (0.52, 0.23, 0.14, 1), 'drum_red'), 'drum_yel': barrel(F, P, (0.85, 0.62, 0.12, 1), 'drum_yel'),
          'drum_rust': barrel(F, P, (0.14, 0.14, 0.16, 1), 'drum_rust'), 'tyre3': tyre(F, P, 3, 'tyre3'), 'tyre2': tyre(F, P, 2, 'tyre2'), 'cone': cone(F, P), 'pallet': pallet(F, P),
          'crate0': crate(F, P, 0), 'crate1': crate(F, P, 1), 'jersey': jersey(F, P), 'sand0': sandbags(F, P, 0), 'sand1': sandbags(F, P, 1), 'bucket': bucket(F, P), 'barrow': wheelbarrow(F, P),
          'toolbox': toolbox(F, P), 'drum_cable': cable_drum(F, P)}
    # fire barrel: rust drum with a ragged emissive flame (the lighting stage adds the flickering warm light at 'fire_barrel')
    m = mb(F)
    m.lathe([(0.0, 0.0), (0.27, 0.0), (0.285, 0.05), (0.285, 0.85), (0.27, 0.9), (0.0, 0.9)], seg=24, mi=I['props'], rgba=(0.12, 0.07, 0.05, 1))
    for k in range(5):
        a = k * 1.26; r = 0.12 if k else 0.0
        m.lathe([(0.0, 0.0), (0.11, 0.0), (0.10, 0.12), (0.06, 0.34), (0.03, 0.55), (0.0, 0.78 + 0.16 * (k % 3))], loc=(math.cos(a) * r, math.sin(a) * r, 0.9), seg=8, mi=I['emissive'], rgba=(1.0, 0.30 + 0.12 * (k % 2), 0.04, 1))
    pr['fire'] = m.finish('proto_fire_barrel', P)
    footprint = {'drum_blue': 0.36, 'drum_red': 0.36, 'drum_yel': 0.36, 'drum_rust': 0.36, 'tyre3': 0.42, 'tyre2': 0.42, 'cone': 0.2, 'pallet': 0.75, 'crate0': 0.5, 'crate1': 0.5, 'jersey': 1.05,
                 'sand0': 1.0, 'sand1': 1.0, 'bucket': 0.25, 'barrow': 0.6, 'toolbox': 0.3, 'drum_cable': 0.6, 'fire': 0.45}
    def free(x, y, r):
        if not (-47.3 < x < -8.7 and -83.6 < y < -60.4): return False
        for (a, b, c, d) in CLEAR:
            if a - r < x < b + r and c - r < y < d + r: return False
        for (a, b, c, d) in boxes:
            if a - r < x < b + r and c - r < y < d + r: return False
        return True
    placed = []
    def put(kind, region, n, name, stack_crate=False, tries=300, mud_only=False, **kw):
        a, b, c, d = region; got = 0
        for _ in range(tries):
            if got >= n: break
            x = rnd.uniform(a, b); y = rnd.uniform(c, d); r = footprint[kind]
            if mud_only and on_pad(x, y, 0.4): continue
            if not free(x, y, r) or any(math.hypot(x - px, y - py) < r + pr_ for px, py, pr_ in placed): continue
            inst(pr[kind], f'{name}_{got}', x, y, yard, rz=kw.get('rz', rnd.uniform(0, 6.28)), support='floor'); placed.append((x, y, r)); got += 1
            if stack_crate and kind == 'pallet': inst(pr[rnd.choice(('crate0', 'crate1'))], f'{name}_crate_{got}', x, y, yard, rz=rnd.uniform(-0.3, 0.3), z=0.17, support='stack')
        return got
    put('fire', (-43.6, -37.0, -67.6, -64.4), 1, 'fire_barrel', mud_only=True)
    put('tyre3', (-40.0, -31.0, -67.8, -64.4), 2, 'tyre_stack_a', mud_only=True); put('tyre2', (-40.0, -31.0, -67.8, -64.4), 2, 'tyre_stack_b', mud_only=True)
    put('drum_cable', (-38.0, -30.0, -76.0, -72.8), 1, 'cable_drum', mud_only=True)
    put('pallet', (-39.0, -30.0, -76.0, -72.8), 2, 'pallet_m', stack_crate=True, mud_only=True)
    for k, nm in enumerate(('drum_blue', 'drum_red', 'drum_yel', 'drum_rust')): put(nm, (-47.0, -30.0, -83.0, -73.0), 2, f'drum_{k}')
    put('jersey', (-47.0, -13.0, -83.4, -82.4), 3, 'jersey_x')
    put('sand0', (-30.0, -13.0, -77.0, -72.5), 1, 'sandbags_a', mud_only=True); put('sand1', (-47.0, -30.0, -67.8, -64.0), 1, 'sandbags_b', mud_only=True)
    put('cone', (-40.0, -29.0, -78.8, -76.0), 3, 'cone', tries=500)
    put('crate0', (-25.0, -9.0, -83.0, -72.5), 3, 'crate_a'); put('crate1', (-25.0, -9.0, -83.0, -72.5), 3, 'crate_b')
    put('pallet', (-25.0, -9.0, -83.0, -72.5), 2, 'pallet_p', stack_crate=True)
    put('barrow', (-47.0, -13.0, -67.8, -60.5), 1, 'wheelbarrow', mud_only=True); put('bucket', (-47.0, -13.0, -83.0, -60.5), 4, 'bucket'); put('toolbox', (-47.0, -13.0, -83.0, -60.5), 1, 'toolbox')
    return placed
