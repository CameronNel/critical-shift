"""Wet mud ground for the mine surface depot: terrain heightfield with tyre ruts and shallow pools, and a shader that reads a per-vertex mask.

Vertex colour 'Pud' (R = standing water, G = gravel haul road). Water is flat at WATER_Z; everything wetter than that is clamped to it.
Plan frame, like the rest of the module; heights are metres relative to the pad tops (0.0).
"""
import math, random
from fe_common import *
from fe_common import _node
import mathutils.noise as mnoise

WATER_Z = -0.042
BASE_Z = -0.012

def _sm(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0); return t * t * (3 - 2 * t)

def make_mud_material():
    name = 'mud_wet'
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    N = lambda kind, **kw: _node(nt, kind, **kw)
    L = lambda a, b: nt.links.new(a, b)
    out = N('ShaderNodeOutputMaterial'); bsdf = N('ShaderNodeBsdfPrincipled'); L(bsdf.outputs[0], out.inputs['Surface'])
    tc = N('ShaderNodeTexCoord')
    at = N('ShaderNodeAttribute'); at.attribute_name = 'Pud'
    sep = N('ShaderNodeSeparateColor'); L(at.outputs['Color'], sep.inputs['Color'])
    def mapping(scale):
        mp = N('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale, scale, scale); L(tc.outputs['Object'], mp.inputs['Vector']); return mp.outputs[0]
    def ramp(src, stops):
        r = N('ShaderNodeValToRGB'); r.color_ramp.elements[0].position = stops[0][0]; r.color_ramp.elements[0].color = stops[0][1]
        r.color_ramp.elements[1].position = stops[-1][0]; r.color_ramp.elements[1].color = stops[-1][1]
        for p, c in stops[1:-1]:
            e = r.color_ramp.elements.new(p); e.color = c
        L(src, r.inputs['Fac']); return r.outputs['Color']
    def noise(scale, detail=6, rough=0.6, w=None):
        n = N('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = scale; n.inputs['Detail'].default_value = detail; n.inputs['Roughness'].default_value = rough
        L(tc.outputs['Object'], n.inputs['Vector']); return n.outputs['Fac']
    def math_(op, a, b=None, val=None, clamp=True):
        n = N('ShaderNodeMath', operation=op); n.use_clamp = clamp
        if isinstance(a, float): n.inputs[0].default_value = a
        else: L(a, n.inputs[0])
        if b is not None: L(b, n.inputs[1])
        elif val is not None: n.inputs[1].default_value = val
        return n.outputs[0]
    def mix(fac, a, b, kind='RGBA'):
        n = N('ShaderNodeMix', data_type=kind)
        if isinstance(fac, float): n.inputs['Factor'].default_value = fac
        else: L(fac, n.inputs['Factor'])
        ia, ib = (6, 7) if kind == 'RGBA' else (2, 3)
        for s, v in ((ia, a), (ib, b)):
            if isinstance(v, tuple): n.inputs[s].default_value = v
            elif isinstance(v, float): n.inputs[s].default_value = v
            else: L(v, n.inputs[s])
        return n.outputs[2] if kind == 'RGBA' else n.outputs[0]
    def img(fn, cs, scale):
        t = N('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(TEXDIR, fn), check_existing=True); t.image.colorspace_settings.name = cs
        t.projection = 'BOX'; t.projection_blend = 0.3; t.interpolation = 'Cubic'; L(mapping(scale), t.inputs['Vector']); return t.outputs['Color']
    pud = sep.outputs['Red']; grv = sep.outputs['Green']
    # sharpen the pool edge with a little noise so the shoreline is not a perfect contour
    edge_n = noise(9.0, 4)
    pud_s = math_('MULTIPLY', math_('SUBTRACT', math_('ADD', pud, edge_n, clamp=False), val=0.42, clamp=False), val=7.0)   # >0.5 where wet
    puddle = math_('MAXIMUM', math_('MINIMUM', pud_s, val=1.0), val=0.0)
    # mud colour: large patches of drier, paler clay among dark wet brown, fine clod detail
    big = noise(0.22, 5); mid = noise(1.3, 7, 0.7); fine = noise(14.0, 4, 0.6)
    mud = ramp(mid, [(0.30, (0.040, 0.028, 0.018, 1)), (0.55, (0.058, 0.040, 0.026, 1)), (0.80, (0.082, 0.058, 0.037, 1))])
    dry = mix(math_('MULTIPLY', math_('SUBTRACT', big, val=0.50, clamp=False), val=1.2), mud, (0.105, 0.078, 0.052, 1))
    mud_col = mix(math_('MULTIPLY', fine, val=0.22), dry, (0.028, 0.019, 0.013, 1))
    gcol = mix(0.6, img('gravel_color.jpg', 'sRGB', 0.8), (0.07, 0.06, 0.05, 1))
    gwet = mix(0.55, gcol, (0.03, 0.026, 0.022, 1))
    ground = mix(math_('MINIMUM', math_('MULTIPLY', grv, val=1.6), val=1.0), mud_col, gwet)
    water_col = (0.012, 0.011, 0.010, 1)
    col = mix(math_('MULTIPLY', puddle, val=0.92), ground, water_col)
    L(col, bsdf.inputs['Base Color'])
    # roughness: wet mud is satin, gravel a little rougher, pools are mirror
    r_mud = mix(math_('MULTIPLY', fine, val=1.0), 0.38, 0.62, 'FLOAT')
    r_ground = mix(math_('MINIMUM', math_('MULTIPLY', grv, val=1.6), val=1.0), r_mud, 0.55, 'FLOAT')
    rough = mix(puddle, r_ground, 0.025, 'FLOAT'); L(rough, bsdf.inputs['Roughness'])
    if 'Specular IOR Level' in bsdf.inputs: bsdf.inputs['Specular IOR Level'].default_value = 0.55
    # wet sheen over the mud
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.0; L(math_('MAXIMUM', math_('MULTIPLY', math_('SUBTRACT', 1.0, grv, clamp=False), val=0.35), puddle), bsdf.inputs['Coat Weight'])
        bsdf.inputs['Coat Roughness'].default_value = 0.06
    # normal: clods and gravel grit, flat in water
    bump_h = mix(math_('MULTIPLY', grv, val=1.0), math_('ADD', math_('MULTIPLY', fine, val=0.7), math_('MULTIPLY', noise(5.0, 5), val=0.5)), img('gravel_rough.jpg', 'Non-Color', 0.8))
    bp = N('ShaderNodeBump'); bp.inputs['Distance'].default_value = 0.02
    L(bump_h, bp.inputs['Height']); L(math_('MULTIPLY', math_('SUBTRACT', 1.0, puddle, clamp=False), val=0.8), bp.inputs['Strength']); L(bp.outputs[0], bsdf.inputs['Normal'])
    # a displacement-free height cue for the gravel normal map
    return m

def build_terrain(F, C, YARD, ruts, pools, pads, gravel_zones, seed=77):
    """Heightfield 0.2 m grid over the yard. ruts: polylines (pts, half_gauge); pools: (x, y, r, depth); pads: rects kept dry and slightly high;
    gravel_zones: (x0, x1, y0, y1, soft) rects for the haul road mask."""
    yard = C['YARD']; rnd = random.Random(seed)
    x0, x1, y0, y1 = YARD[0], YARD[1], YARD[2], YARD[3]; st = 0.2
    NX = int(round((x1 - x0) / st)); NY = int(round((y1 - y0) / st))
    mat = make_mud_material()
    bm = bmesh.new(); lay = bm.loops.layers.color.new('Pud'); g = []
    def seg_dist(px, py, ax, ay, bx, by):
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy; t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
        qx, qy = ax + t * dx, ay + t * dy; return math.hypot(px - qx, py - qy), t
    for i in range(NX + 1):
        row = []
        for j in range(NY + 1):
            x = x0 + i * st; y = y0 + j * st
            z = BASE_Z + 0.012 * mnoise.noise(Vector((x * 0.45, y * 0.45, 1.3))) + 0.007 * mnoise.noise(Vector((x * 1.9, y * 1.9, 4.1))) + 0.004 * mnoise.noise(Vector((x * 6.0, y * 6.0, 2.2)))
            for (pts, hg) in ruts:
                best = 0.0
                for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
                    d, t = seg_dist(x, y, ax, ay, bx, by)
                    if d > hg + 0.7: continue
                    ang = math.atan2(by - ay, bx - ax); nx, ny = -math.sin(ang), math.cos(ang)
                    side = abs((x - ax) * nx + (y - ay) * ny)
                    broken = 0.55 + 0.45 * mnoise.noise(Vector((x * 0.5, y * 0.5, 9.0)))
                    best = max(best, math.exp(-((side - hg) / 0.17) ** 2) * broken * (1.0 if d < hg + 0.3 else 0.0))
                z -= 0.062 * best
            for (px, py, r, dep) in pools:
                d = math.hypot(x - px, y - py) + 0.35 * r * mnoise.noise(Vector((x * 0.7, y * 0.7, 5.0 + px)))
                z -= dep * math.exp(-(d / r) ** 2)
            wet = _sm(WATER_Z + 0.014, WATER_Z - 0.006, z)
            gr = 0.0
            for (gx0, gx1, gy0, gy1, soft) in gravel_zones:
                n = 0.3 * mnoise.noise(Vector((x * 0.8, y * 0.8, 7.0)))
                gr = max(gr, _sm(0.0, soft, min(x - gx0, gx1 - x, y - gy0, gy1 - y) + n))
            if gr > 0.5: z = max(z, BASE_Z + 0.006) ; wet *= (1 - gr)
            for (px0, px1, py0, py1) in pads:                                       # dry crown and a raised kerb of mud against the slab edge
                d = max(px0 - x, x - px1, py0 - y, y - py1)
                if d < 0.25: z = min(max(z, -0.04), -0.012); wet = 0.0
            if z < WATER_Z: z = WATER_Z
            row.append((x, y, z, wet, gr))
        g.append(row)
    vs = [[bm.verts.new(Vector((LX(x), LY(y), z))) for (x, y, z, wet, gr) in row] for row in g]
    for i in range(NX):
        for j in range(NY):
            f = bm.faces.new((vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]))
            for lp, (ii, jj) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                _, _, _, wet, gr = g[ii][jj]; lp[lay] = (wet, gr, 0.0, 1.0)
    o = mesh_obj('yard_earth', bm, mat, yard, smooth=True)
    return o
