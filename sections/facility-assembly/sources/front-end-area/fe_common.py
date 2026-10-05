"""Shared helpers for the front-end area module (cafeteria, hall, yard).

All builder functions take PLAN coordinates (metres, the facility plan frame in design/facility-layout) and convert to the module's
local frame: origin at the spawn airlock threshold centre on the floor, +Y inward (north), +X east, +Z up.
"""
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix

OX, OY = -8.0, 80.0          # plan -> local
def LX(x): return x + OX
def LY(y): return y + OY

TEXDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'textures')
ROOT = 'MODULE_front-end-area'
_cols = {}
def collection(name, parent=None):
    if name in _cols: return _cols[name]
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    _cols[name] = c
    return c

def setup_collections():
    root = collection(ROOT)
    for n in ('YARD', 'CAFETERIA', 'HALL', 'SHARED', 'LIGHTS', 'CAMERAS', 'INTERFACES'):
        collection(n, root)
    return root

# --------------------------------------------------------------------------- materials
_mats = {}
def _node(nt, kind, **kw):
    n = nt.nodes.new(kind)
    for k, v in kw.items():
        if k == 'loc': n.location = v
        else:
            try: setattr(n, k, v)
            except Exception: pass
    return n

def make_mat(name, base=(0.5, 0.5, 0.5), rough=0.6, metallic=0.0, var=0.12, var_scale=0.6, wear=None, bump=0.0,
             attr=False, emission=0.0, glass=False, tile=None, grain=None, strata=None, sheen=0.0, spec=0.5, pointy=False, grime=0.0, dirt=(0.52, 0.47, 0.42), tex=None):
    if name in _mats: return _mats[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = _node(nt, 'ShaderNodeOutputMaterial')
    tc = _node(nt, 'ShaderNodeTexCoord')
    if glass:
        g = _node(nt, 'ShaderNodeBsdfGlass'); g.inputs['Color'].default_value = (*base, 1); g.inputs['Roughness'].default_value = 0.03; g.inputs['IOR'].default_value = 1.45
        t = _node(nt, 'ShaderNodeBsdfTransparent')
        lp = _node(nt, 'ShaderNodeLightPath'); mix = _node(nt, 'ShaderNodeMixShader')
        nt.links.new(lp.outputs['Is Shadow Ray'], mix.inputs[0]); nt.links.new(g.outputs[0], mix.inputs[1]); nt.links.new(t.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs['Surface']); _mats[name] = m; return m
    bsdf = _node(nt, 'ShaderNodeBsdfPrincipled')
    bsdf.inputs['Metallic'].default_value = metallic
    if 'Specular IOR Level' in bsdf.inputs: bsdf.inputs['Specular IOR Level'].default_value = spec
    if sheen and 'Sheen Weight' in bsdf.inputs: bsdf.inputs['Sheen Weight'].default_value = sheen
    nt.links.new(bsdf.outputs[0], out.inputs['Surface'])
    # colour source
    if attr:
        a = _node(nt, 'ShaderNodeAttribute'); a.attribute_name = 'Col'
        colsrc = a.outputs['Color']
    elif tile:
        br = _node(nt, 'ShaderNodeTexBrick'); br.inputs['Color1'].default_value = (*tile['a'], 1); br.inputs['Color2'].default_value = (*tile['b'], 1)
        br.inputs['Mortar'].default_value = (*tile['grout'], 1); br.inputs['Scale'].default_value = 1.0
        br.inputs['Mortar Size'].default_value = tile.get('mortar', 0.012); br.inputs['Brick Width'].default_value = tile.get('w', 0.6); br.inputs['Row Height'].default_value = tile.get('h', 0.6)
        br.offset = 0.0; br.offset_frequency = 2
        nt.links.new(tc.outputs['Object'], br.inputs['Vector']); colsrc = br.outputs['Color']
        bumpsrc = br.outputs['Fac']
    elif tex:
        def _img(fn, cs):
            n_ = _node(nt, 'ShaderNodeTexImage'); n_.image = bpy.data.images.load(os.path.join(TEXDIR, fn), check_existing=True)
            n_.image.colorspace_settings.name = cs; n_.projection = 'BOX'; n_.projection_blend = tex.get('blend', 0.25); n_.interpolation = 'Cubic'
            nt.links.new(tmap.outputs[0], n_.inputs['Vector']); return n_
        tmap = _node(nt, 'ShaderNodeMapping'); s_ = tex.get('scale', 0.5); tmap.inputs['Scale'].default_value = (s_, s_, s_); nt.links.new(tc.outputs['Object'], tmap.inputs['Vector'])
        ti = _img(tex['color'] + '_color.jpg', 'sRGB')
        tint = _node(nt, 'ShaderNodeMix', data_type='RGBA', blend_type='MULTIPLY'); tint.inputs['Factor'].default_value = 1.0
        tc_ = _node(nt, 'ShaderNodeRGB'); tc_.outputs[0].default_value = (*tex.get('tint', (1, 1, 1)), 1)
        nt.links.new(ti.outputs['Color'], tint.inputs[6]); nt.links.new(tc_.outputs[0], tint.inputs[7]); colsrc = tint.outputs[2]
        tex_rough = _img(tex['color'] + '_rough.jpg', 'Non-Color') if tex.get('rough', True) else None
        tex_norm = _img(tex['color'] + '_normal.jpg', 'Non-Color') if tex.get('normal', False) else None
        tex_h = _img(tex['color'] + '_height.jpg', 'Non-Color') if tex.get('height', False) else None
    else:
        rgb = _node(nt, 'ShaderNodeRGB'); rgb.outputs[0].default_value = (*base, 1); colsrc = rgb.outputs[0]
    # low-frequency variation
    mp = _node(nt, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (var_scale, var_scale, var_scale)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    nz = _node(nt, 'ShaderNodeTexNoise'); nz.inputs['Detail'].default_value = 6; nz.inputs['Roughness'].default_value = 0.55
    nt.links.new(mp.outputs[0], nz.inputs['Vector'])
    vmix = _node(nt, 'ShaderNodeMix', data_type='RGBA', blend_type='MULTIPLY')
    vmix.inputs['Factor'].default_value = var
    nt.links.new(colsrc, vmix.inputs[6]); nt.links.new(nz.outputs['Color'], vmix.inputs[7])
    col = vmix.outputs[2]
    # grain / strata for timber and rock
    if grain:
        wv = _node(nt, 'ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.bands_direction = 'X'; wv.inputs['Scale'].default_value = grain; wv.inputs['Distortion'].default_value = 3.0
        nt.links.new(tc.outputs['Object'], wv.inputs['Vector'])
        gm = _node(nt, 'ShaderNodeMix', data_type='RGBA', blend_type='MULTIPLY'); gm.inputs['Factor'].default_value = 0.35
        nt.links.new(col, gm.inputs[6]); nt.links.new(wv.outputs['Color'], gm.inputs[7]); col = gm.outputs[2]
    if strata:
        wv = _node(nt, 'ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.bands_direction = 'Z'; wv.inputs['Scale'].default_value = strata; wv.inputs['Distortion'].default_value = 6.0
        nt.links.new(tc.outputs['Object'], wv.inputs['Vector'])
        sm = _node(nt, 'ShaderNodeMix', data_type='RGBA', blend_type='MULTIPLY'); sm.inputs['Factor'].default_value = 0.22
        nt.links.new(col, sm.inputs[6]); nt.links.new(wv.outputs['Color'], sm.inputs[7]); col = sm.outputs[2]
    if pointy:
        gp = _node(nt, 'ShaderNodeNewGeometry'); cr = _node(nt, 'ShaderNodeValToRGB')
        cr.color_ramp.elements[0].position = 0.40; cr.color_ramp.elements[1].position = 0.62
        cr.color_ramp.elements[0].color = (0.25, 0.22, 0.2, 1); cr.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1)
        nt.links.new(gp.outputs['Pointiness'], cr.inputs['Fac'])
        pm = _node(nt, 'ShaderNodeMix', data_type='RGBA', blend_type='MULTIPLY'); pm.inputs['Factor'].default_value = 1.0
        nt.links.new(col, pm.inputs[6]); nt.links.new(cr.outputs['Color'], pm.inputs[7]); col = pm.outputs[2]
    # edge wear from a bevel node
    if wear:
        bv = _node(nt, 'ShaderNodeBevel'); bv.samples = 4; bv.inputs['Radius'].default_value = wear.get('r', 0.012)
        gn = _node(nt, 'ShaderNodeNewGeometry')
        dp = _node(nt, 'ShaderNodeVectorMath', operation='DOT_PRODUCT')
        nt.links.new(bv.outputs['Normal'], dp.inputs[0]); nt.links.new(gn.outputs['Normal'], dp.inputs[1])
        mr = _node(nt, 'ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.985; mr.inputs['From Max'].default_value = 0.88
        nt.links.new(dp.outputs['Value'], mr.inputs['Value'])
        wm = _node(nt, 'ShaderNodeMix', data_type='RGBA', blend_type='MIX')
        wc = _node(nt, 'ShaderNodeRGB'); wc.outputs[0].default_value = (*wear['color'], 1)
        nt.links.new(mr.outputs[0], wm.inputs['Factor']); nt.links.new(col, wm.inputs[6]); nt.links.new(wc.outputs[0], wm.inputs[7]); col = wm.outputs[2]
    dirt_f = None
    if grime:
        # run-down look: low-height dirt, vertical streaks and big blotches, multiplied into the colour; also matte-ens the surface
        def mr(src, a, b, lo=0.0, hi=1.0):
            n_ = _node(nt, 'ShaderNodeMapRange'); n_.inputs['From Min'].default_value = a; n_.inputs['From Max'].default_value = b
            n_.inputs['To Min'].default_value = lo; n_.inputs['To Max'].default_value = hi; n_.clamp = True
            nt.links.new(src, n_.inputs['Value']); return n_.outputs[0]
        def mth(op, a, b=None, val=None):
            n_ = _node(nt, 'ShaderNodeMath', operation=op); n_.use_clamp = True
            nt.links.new(a, n_.inputs[0])
            if b is not None: nt.links.new(b, n_.inputs[1])
            else: n_.inputs[1].default_value = val
            return n_.outputs[0]
        m1 = _node(nt, 'ShaderNodeMapping'); m1.inputs['Scale'].default_value = (2.2, 2.2, 2.2); nt.links.new(tc.outputs['Object'], m1.inputs['Vector'])
        nb = _node(nt, 'ShaderNodeTexNoise'); nb.inputs['Detail'].default_value = 10; nb.inputs['Roughness'].default_value = 0.7; nt.links.new(m1.outputs[0], nb.inputs['Vector'])
        m2 = _node(nt, 'ShaderNodeMapping'); m2.inputs['Scale'].default_value = (3.5, 3.5, 0.45); nt.links.new(tc.outputs['Object'], m2.inputs['Vector'])
        ns = _node(nt, 'ShaderNodeTexNoise'); ns.inputs['Detail'].default_value = 3; ns.inputs['Scale'].default_value = 1.0; nt.links.new(m2.outputs[0], ns.inputs['Vector'])
        sx = _node(nt, 'ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sx.inputs[0])
        low = mr(sx.outputs['Z'], 0.0, 1.7, 1.0, 0.0)
        big = mr(nb.outputs['Fac'], 0.42, 0.68); stk = mr(ns.outputs['Fac'], 0.45, 0.70)
        tot = mth('ADD', mth('MULTIPLY', big, None, 0.3), mth('MULTIPLY', stk, None, 0.25))
        tot = mth('ADD', tot, mth('MULTIPLY', low, None, 0.5))
        dirt_f = mth('MULTIPLY', tot, None, grime)
        dm = _node(nt, 'ShaderNodeMix', data_type='RGBA', blend_type='MULTIPLY'); nt.links.new(dirt_f, dm.inputs['Factor'])
        dc = _node(nt, 'ShaderNodeRGB'); dc.outputs[0].default_value = (*dirt, 1)
        nt.links.new(col, dm.inputs[6]); nt.links.new(dc.outputs[0], dm.inputs[7]); col = dm.outputs[2]
    nt.links.new(col, bsdf.inputs['Base Color'])
    # roughness variation
    rv = _node(nt, 'ShaderNodeMapRange'); rv.inputs['To Min'].default_value = max(rough - 0.22, 0.05); rv.inputs['To Max'].default_value = min(rough + 0.22, 1.0)
    nt.links.new(nz.outputs['Fac'], rv.inputs['Value'])
    if tex and tex_rough is not None:
        rm_ = _node(nt, 'ShaderNodeMath', operation='MULTIPLY'); rm_.inputs[1].default_value = tex.get('rough_mul', 1.0); nt.links.new(tex_rough.outputs['Color'], rm_.inputs[0]); rv = rm_
    if dirt_f is not None:
        ra = _node(nt, 'ShaderNodeMath', operation='ADD'); ra.use_clamp = True
        rm = _node(nt, 'ShaderNodeMath', operation='MULTIPLY'); rm.inputs[1].default_value = 0.3; nt.links.new(dirt_f, rm.inputs[0])
        nt.links.new(rv.outputs[0], ra.inputs[0]); nt.links.new(rm.outputs[0], ra.inputs[1]); nt.links.new(ra.outputs[0], bsdf.inputs['Roughness'])
    else: nt.links.new(rv.outputs[0], bsdf.inputs['Roughness'])
    if tex and (tex_norm is not None or tex_h is not None):
        if tex_norm is not None:
            nm_ = _node(nt, 'ShaderNodeNormalMap'); nm_.inputs['Strength'].default_value = tex.get('nstrength', 0.8); nt.links.new(tex_norm.outputs['Color'], nm_.inputs['Color']); nt.links.new(nm_.outputs[0], bsdf.inputs['Normal'])
        else:
            bp_ = _node(nt, 'ShaderNodeBump'); bp_.inputs['Strength'].default_value = tex.get('nstrength', 0.5); bp_.inputs['Distance'].default_value = 0.02; nt.links.new(tex_h.outputs['Color'], bp_.inputs['Height']); nt.links.new(bp_.outputs[0], bsdf.inputs['Normal'])
    elif not emission:
        n2 = _node(nt, 'ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 150 if not tile else 40; n2.inputs['Detail'].default_value = 4
        nt.links.new(tc.outputs['Object'], n2.inputs['Vector'])
        bp = _node(nt, 'ShaderNodeBump'); bp.inputs['Strength'].default_value = bump or 0.08; bp.inputs['Distance'].default_value = 0.004
        nt.links.new((bumpsrc if tile else n2.outputs['Fac']), bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], bsdf.inputs['Normal'])
    if emission:
        e = _node(nt, 'ShaderNodeEmission'); e.inputs['Strength'].default_value = emission
        nt.links.new(colsrc, e.inputs['Color'])
        ad = _node(nt, 'ShaderNodeAddShader'); nt.links.new(bsdf.outputs[0], ad.inputs[0]); nt.links.new(e.outputs[0], ad.inputs[1])
        nt.links.new(ad.outputs[0], out.inputs['Surface'])
    _mats[name] = m
    return m

def make_img_mat(name, fn, emission=0.0, rough=0.6, bump=0.0):
    """Flat image material (posters, TV slide) mapped from the object's UVs."""
    if name in _mats: return _mats[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = _node(nt, 'ShaderNodeOutputMaterial'); b = _node(nt, 'ShaderNodeBsdfPrincipled'); t = _node(nt, 'ShaderNodeTexImage')
    t.image = bpy.data.images.load(os.path.join(TEXDIR, fn), check_existing=True); t.image.colorspace_settings.name = 'sRGB'
    nt.links.new(t.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = rough
    if bump:
        bp = _node(nt, 'ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; bp.inputs['Distance'].default_value = 0.004; nt.links.new(t.outputs['Color'], bp.inputs['Height']); nt.links.new(bp.outputs[0], b.inputs['Normal'])
    if emission:
        b.inputs['Emission Color'].default_value = (1, 1, 1, 1); nt.links.new(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = emission
    nt.links.new(b.outputs[0], out.inputs['Surface']); _mats[name] = m; return m

def families():
    try:
        import fe_textures; fe_textures.ensure()
    except Exception as e: print('texture generation failed', e)
    """Shared material families. Palette follows the spawn room: dusty-lilac plaster over a navy dado, terracotta tile, rust-red,
    mustard and graphite accents, warm concrete outside. Wear is light: two years of use, not twenty."""
    F = {}
    F['concrete_slab'] = make_mat('concrete_slab', (0.40, 0.375, 0.34), 0.82, var=0.15, var_scale=0.35, grime=0.45, wear={'color': (0.66, 0.63, 0.58), 'r': 0.02}, tex={'color': 'concrete', 'scale': 0.5, 'tint': (0.44, 0.40, 0.47), 'normal': True, 'nstrength': 0.7})
    F['apron'] = make_mat('apron', (0.30, 0.285, 0.265), 0.86, var=0.22, var_scale=0.5, grime=0.7, dirt=(0.4, 0.37, 0.33), wear={'color': (0.5, 0.48, 0.44), 'r': 0.02}, tex={'color': 'concrete', 'scale': 0.5, 'tint': (0.36, 0.33, 0.40), 'normal': True, 'nstrength': 0.8})
    F['plaster'] = make_mat('plaster', (0.47, 0.35, 0.43), 0.88, var=0.1, var_scale=0.3, grime=0.4, tex={'color': 'plaster5', 'scale': 0.5, 'tint': (1.46, 1.04, 1.30), 'normal': True, 'nstrength': 0.55})
    F['dado'] = make_mat('dado', (0.028, 0.034, 0.095), 0.5, var=0.1, grime=0.5, wear={'color': (0.12, 0.13, 0.2), 'r': 0.006})
    F['ceiling'] = make_mat('ceiling', (0.66, 0.63, 0.60), 0.9, var=0.06, grime=0.3, tex={'color': 'plaster5', 'scale': 0.6, 'tint': (1.5, 1.45, 1.4), 'normal': True, 'nstrength': 0.3})
    F['gravel'] = make_mat('gravel', (0.3, 0.24, 0.15), 0.9, var=0.2, grime=0.0, tex={'color': 'gravel', 'scale': 0.8, 'tint': (0.8, 0.78, 0.74), 'normal': True, 'nstrength': 1.0})
    F['trim'] = make_mat('trim', (0.62, 0.60, 0.55), 0.55, var=0.06, grime=0.4)
    F['steel_charcoal'] = make_mat('steel_charcoal', (0.085, 0.09, 0.105), 0.5, 0.2, var=0.1, grime=0.3, wear={'color': (0.30, 0.22, 0.17), 'r': 0.01}, tex={'color': 'metal5', 'scale': 1.0, 'tint': (0.17, 0.18, 0.21), 'normal': True, 'nstrength': 0.3})
    F['steel_painted'] = make_mat('steel_painted', (0.17, 0.19, 0.26), 0.45, 0.3, var=0.08, grime=0.2, wear={'color': (0.5, 0.5, 0.52), 'r': 0.01})
    F['paint'] = make_mat('paint', (0.5, 0.5, 0.5), 0.5, 0.3, var=0.1, attr=True, grime=0.8, dirt=(0.42, 0.36, 0.30), wear={'color': (0.6, 0.6, 0.62), 'r': 0.006})
    F['steel_accent'] = make_mat('steel_accent', (0.72, 0.36, 0.06), 0.5, 0.1, var=0.15, grime=0.4, wear={'color': (0.35, 0.18, 0.08), 'r': 0.01})
    F['steel_rust'] = make_mat('steel_rust', (0.40, 0.19, 0.09), 0.82, 0.3, var=0.5, var_scale=1.2, grime=0.3, bump=0.25)
    F['corrugated'] = make_mat('corrugated', (0.52, 0.52, 0.50), 0.55, 0.55, var=0.25, var_scale=0.5, grime=0.5, dirt=(0.45, 0.40, 0.34))
    F['cafe_tile'] = make_mat('cafe_tile', tile={'a': (0.52, 0.28, 0.18), 'b': (0.38, 0.21, 0.15), 'grout': (0.28, 0.25, 0.22), 'w': 0.5, 'h': 0.5, 'mortar': 0.008}, rough=0.32, var=0.2, grime=0.45, bump=0.35)
    F['tile_blue'] = make_mat('tile_blue', tile={'a': (0.05, 0.07, 0.21), 'b': (0.045, 0.06, 0.19), 'grout': (0.30, 0.26, 0.23), 'w': 0.6, 'h': 0.6, 'mortar': 0.012}, rough=0.5, var=0.1, grime=0.5)
    F['rubber'] = make_mat('rubber', (0.04, 0.04, 0.045), 0.9, var=0.08, bump=0.08, grime=0.3)
    F['timber'] = make_mat('timber', (0.42, 0.25, 0.115), 0.65, var=0.12, grime=0.25, wear={'color': (0.55, 0.38, 0.2), 'r': 0.008}, tex={'color': 'wood5', 'scale': 0.8, 'tint': (1.0, 1.0, 1.0), 'normal': True, 'nstrength': 0.35})
    F['cork'] = make_mat('cork', (0.5, 0.36, 0.22), 0.92, var=0.08, grime=0.15, tex={'color': 'cork5', 'scale': 1.6, 'tint': (1.0, 1.0, 1.0), 'normal': True, 'nstrength': 0.5})
    F['steel_brushed'] = make_mat('steel_brushed', (0.45, 0.46, 0.48), 0.4, 0.9, var=0.05, grime=0.2, wear={'color': (0.75, 0.75, 0.77), 'r': 0.006}, tex={'color': 'metal5', 'scale': 1.0, 'tint': (0.9, 0.92, 0.96), 'normal': True, 'nstrength': 0.25})
    F['laminate'] = make_mat('laminate', (0.70, 0.64, 0.54), 0.4, var=0.08, grime=0.45, wear={'color': (0.80, 0.76, 0.68), 'r': 0.006})
    F['glass'] = make_mat('glass', (0.82, 0.92, 0.95), glass=True)
    F['fabric'] = make_mat('fabric', (0.45, 0.17, 0.11), 0.96, var=0.2, var_scale=4, sheen=0.4, bump=0.2, attr=True, grime=0.4)
    F['plastic'] = make_mat('plastic', (0.2, 0.22, 0.24), 0.45, var=0.08, attr=True, grime=0.4, wear={'color': (0.5, 0.5, 0.5), 'r': 0.006})
    F['signage'] = make_mat('signage', (0.9, 0.9, 0.9), 0.5, attr=True, var=0.05, grime=0.35)
    F['foliage'] = make_mat('foliage', (0.12, 0.30, 0.08), 0.75, attr=True, var=0.3, var_scale=3)
    F['rock'] = make_mat('rock', (0.42, 0.31, 0.21), 0.9, var=0.35, var_scale=0.3, pointy=True, grime=0.3, dirt=(0.55, 0.5, 0.45), strata=14, tex={'color': 'rock', 'scale': 0.35, 'tint': (0.55, 0.55, 0.72), 'normal': True, 'nstrength': 1.7, 'blend': 0.3})
    F['props'] = make_mat('props', (0.5, 0.4, 0.3), 0.75, attr=True, var=0.3, var_scale=1.5, grime=0.75, wear={'color': (0.7, 0.6, 0.45), 'r': 0.01}, bump=0.12)
    F['emissive'] = make_mat('emissive', (1, 1, 1), 0.4, attr=True, var=0.0, emission=7.0)
    F['screen'] = make_mat('screen', (1, 1, 1), 0.2, attr=True, var=0.0, emission=1.6)
    F['poster_land'] = make_img_mat('poster_land', 'poster_art_landscape.jpg', 0.0)
    F['poster_port'] = make_img_mat('poster_port', 'poster_art_portrait.jpg', 0.0)
    F['tv_slide'] = make_img_mat('tv_slide', 'tv_briefing_slide.jpg', 1.1)
    return F

# --------------------------------------------------------------------------- geometry
def _link(obj, coll):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    coll.objects.link(obj)

def color_attr(me, rgba):
    a = me.color_attributes.new('Col', 'FLOAT_COLOR', 'CORNER')
    n = len(me.loops)
    a.data.foreach_set('color', [v for _ in range(n) for v in rgba])

def mesh_obj(name, bm, mat, coll, rgba=None, smooth=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    if mat: me.materials.append(mat)
    if rgba: color_attr(me, rgba)
    o = bpy.data.objects.new(name, me); coll.objects.link(o)
    return o

def bevel_bm(bm, w, seg=1):
    if w <= 0: return
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=w, segments=seg, affect='EDGES', profile=0.5)

def box(name, x0, x1, y0, y1, z0, z1, mat, coll, rgba=None, bev=0.0, seg=1, plan=True):
    """Axis-aligned box. plan=True: x/y are plan coords."""
    if plan: x0, x1, y0, y1 = LX(x0), LX(x1), LY(y0), LY(y1)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = (x0 + x1) / 2 + v.co.x * (x1 - x0)
        v.co.y = (y0 + y1) / 2 + v.co.y * (y1 - y0)
        v.co.z = (z0 + z1) / 2 + v.co.z * (z1 - z0)
    bevel_bm(bm, min(bev, 0.45 * min(x1 - x0, y1 - y0, z1 - z0)), seg)
    return mesh_obj(name, bm, mat, coll, rgba)

def cylinder(name, cx, cy, r, z0, z1, mat, coll, rgba=None, verts=16, bev=0.0, plan=True, r2=None):
    if plan: cx, cy = LX(cx), LY(cy)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=r, radius2=(r if r2 is None else r2), depth=(z1 - z0))
    for v in bm.verts: v.co.x += cx; v.co.y += cy; v.co.z += (z0 + z1) / 2
    if bev: bevel_bm(bm, min(bev, 0.4 * r), 1)
    return mesh_obj(name, bm, mat, coll, rgba, smooth=False)

def tri_count(objs=None):
    dg = bpy.context.evaluated_depsgraph_get(); total = 0
    for o in (objs if objs is not None else bpy.data.objects):
        if o.type in ('MESH', 'CURVE', 'FONT') and not o.hide_render:
            ev = o.evaluated_get(dg); m = ev.to_mesh()
            total += sum(len(p.vertices) - 2 for p in m.polygons); ev.to_mesh_clear()
    return total

def tri_count_coll(coll):
    objs = []
    def walk(c):
        objs.extend(c.objects)
        for ch in c.children: walk(ch)
    walk(coll)
    return tri_count(objs)

WALL_ITEMS = []   # (object, axis 'x'|'y' of the wall normal, plane coordinate in local metres, sign: +1 if the prop sits on the +normal side)
def wall_item(o, axis, plane_plan, sign):
    plane = (LX(plane_plan) if axis == 'x' else LY(plane_plan))
    WALL_ITEMS.append((o.name, axis, plane, sign)); o['support'] = 'wall'; return o
