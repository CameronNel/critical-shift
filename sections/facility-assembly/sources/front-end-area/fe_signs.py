"""Baked signage: every sign's lettering, icon and plate colour is painted into one texture atlas (textures/sign_atlas.png) with PIL;
each sign is a single plate mesh whose UVs point at its atlas cell. No text objects, no separate letter shapes.

Usage: sign(...) / hanging_sign(...) while building; call finalize_signs(F) once at the end (packs, paints, assigns UVs and materials)."""
import bpy, math, os, sys
_pl = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pylib')   # pillow installed with: blender-python -m pip install --target pylib pillow
if os.path.isdir(_pl) and _pl not in sys.path: sys.path.append(_pl)
from PIL import Image, ImageDraw, ImageFont
from fe_common import *

FONT_B = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
FONT_R = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
PXM = 420                       # atlas pixels per metre of sign
ATLAS_MAX = 4096
ROT = {'N': 0.0, 'S': math.pi, 'E': -math.pi / 2, 'W': math.pi / 2}

STYLES = {   # plate, ink, accent, border
    'nav':    ((20, 24, 38), (240, 238, 230), (222, 108, 22), (70, 78, 104)),
    'staff':  ((150, 30, 24), (248, 244, 238), (240, 190, 40), (210, 110, 100)),
    'exit':   ((18, 120, 64), (246, 250, 246), (246, 250, 246), (90, 180, 130)),
    'med':    ((236, 236, 230), (24, 120, 70), (200, 40, 36), (170, 170, 166)),
    'info':   ((214, 204, 180), (36, 30, 24), (180, 70, 30), (150, 130, 100)),
    'hazard': ((236, 188, 20), (20, 20, 22), (20, 20, 22), (150, 120, 10)),
    'board':  ((30, 34, 40), (238, 232, 214), (222, 108, 22), (78, 70, 56)),
    'green':  ((20, 74, 52), (240, 244, 238), (222, 108, 22), (80, 130, 106)),
}
SPECS = []      # dicts: key, text, sub, style, icon, w, h, lit
OBJS = []       # (obj, spec index, face kinds per polygon)

def _spec_index(spec):
    for i, s in enumerate(SPECS):
        if s['key'] == spec['key']: return i
    SPECS.append(spec); return len(SPECS) - 1

def _box_mesh(name, w, h, t, kinds_back=False):
    me = bpy.data.meshes.new(name); x0, x1, z0, z1 = -w / 2, w / 2, -h / 2, h / 2
    verts = [(x0, 0, z0), (x1, 0, z0), (x1, t, z0), (x0, t, z0), (x0, 0, z1), (x1, 0, z1), (x1, t, z1), (x0, t, z1)]
    # faces: front (+y), back (-y), top, bottom, left(-x), right(+x)  -- outward winding
    faces = [(2, 3, 7, 6), (0, 1, 5, 4), (4, 5, 6, 7), (3, 2, 1, 0), (0, 4, 7, 3), (1, 2, 6, 5)]
    me.from_pydata(verts, [], faces); me.update()
    me.uv_layers.new(name='UVMap')
    for p in me.polygons: p.use_smooth = False
    return me

def sign(coll, name, text, x, y, z, facing, w, h, sub=None, style='nav', icon=None, lit=False, t=0.03, hang=None, lines=None):
    """Wall-mounted sign. (x, y) is the plan point on the wall face, z the bottom edge, facing the direction the front looks."""
    spec = {'key': (text, sub, style, icon, round(w, 3), round(h, 3), tuple(lines or ())), 'text': text, 'sub': sub, 'style': style, 'icon': icon, 'w': w, 'h': h, 'lit': lit, 'lines': lines}
    si = _spec_index(spec)
    me = _box_mesh(name, w, h, t); o = bpy.data.objects.new(name, me); coll.objects.link(o)
    o.location = (LX(x), LY(y), z + h / 2); o.rotation_euler = (0, 0, ROT[facing])
    OBJS.append((o, si, 'single')); o['support'] = 'wall'; return o

def hanging_sign(coll, name, text, x, y, z, facing, w, h, sub=None, style='nav', icon=None, drop=0.9, ceiling=4.9, F=None, lines=None):
    """Double-sided sign hung on two rods from the ceiling. z is the bottom edge. Front faces `facing`, back shows the same artwork."""
    spec = {'key': (text, sub, style, icon, round(w, 3), round(h, 3), tuple(lines or ())), 'text': text, 'sub': sub, 'style': style, 'icon': icon, 'w': w, 'h': h, 'lit': False, 'lines': lines}
    si = _spec_index(spec)
    t = 0.05; me = _box_mesh(name, w, h, t); o = bpy.data.objects.new(name, me); coll.objects.link(o)
    o.location = (LX(x), LY(y), z + h / 2); o.rotation_euler = (0, 0, ROT[facing]); OBJS.append((o, si, 'double'))
    # rods
    for sx in (-w * 0.38, w * 0.38):
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=0.006, radius2=0.006, depth=ceiling - (z + h))
        rot = Matrix.Rotation(ROT[facing], 4, 'Z'); off = rot @ Vector((sx, t / 2, 0))
        for v in bm.verts: v.co = Vector((LX(x) + off.x + v.co.x, LY(y) + off.y + v.co.y, (z + h + ceiling) / 2 + v.co.z))
        mesh_obj(name + f'_rod{sx:+.1f}', bm, F['steel_charcoal'] if F else None, coll)
    o['support'] = 'hanging'; return o

# ----------------------------------------------------------------------------------------- painting
def _fit(draw, text, font_path, max_w, max_h, start):
    s = start
    while s > 8:
        f = ImageFont.truetype(font_path, s); b = draw.textbbox((0, 0), text, font=f)
        if b[2] - b[0] <= max_w and b[3] - b[1] <= max_h: return f, b
        s -= 2
    f = ImageFont.truetype(font_path, 8); return f, draw.textbbox((0, 0), text, font=f)

def _icon(d, kind, cx, cy, r, ink, accent):
    if kind in ('arrow_r', 'arrow_l', 'arrow_u', 'arrow_d'):
        pts = {'arrow_r': [(-.6, -.18), (.1, -.18), (.1, -.5), (.65, 0), (.1, .5), (.1, .18), (-.6, .18)],
               'arrow_l': [(.6, -.18), (-.1, -.18), (-.1, -.5), (-.65, 0), (-.1, .5), (-.1, .18), (.6, .18)],
               'arrow_u': [(-.18, .6), (-.18, -.1), (-.5, -.1), (0, -.65), (.5, -.1), (.18, -.1), (.18, .6)],
               'arrow_d': [(-.18, -.6), (-.18, .1), (-.5, .1), (0, .65), (.5, .1), (.18, .1), (.18, -.6)]}[kind]
        d.polygon([(cx + px * r, cy + py * r) for px, py in pts], fill=ink)
    elif kind == 'cross':
        d.rectangle([cx - r * .22, cy - r * .62, cx + r * .22, cy + r * .62], fill=accent); d.rectangle([cx - r * .62, cy - r * .22, cx + r * .62, cy + r * .22], fill=accent)
    elif kind == 'door':
        d.rectangle([cx - r * .45, cy - r * .7, cx + r * .45, cy + r * .7], outline=ink, width=max(2, int(r * .12)))
        d.polygon([(cx - r * .45, cy - r * .7), (cx + r * .15, cy - r * .55), (cx + r * .15, cy + r * .7), (cx - r * .45, cy + r * .7)], fill=ink)
        d.ellipse([cx + r * .02, cy, cx + r * .12, cy + r * .1], fill=accent)
    elif kind == 'cutlery':
        d.rectangle([cx - r * .38, cy - r * .1, cx - r * .28, cy + r * .75], fill=ink)
        for k in range(3): d.rectangle([cx - r * .5 + k * r * .12, cy - r * .7, cx - r * .42 + k * r * .12, cy - r * .1], fill=ink)
        d.rectangle([cx + r * .28, cy - r * .1, cx + r * .38, cy + r * .75], fill=ink); d.ellipse([cx + r * .12, cy - r * .72, cx + r * .54, cy + r * .05], fill=ink)
    elif kind == 'cup':
        d.rectangle([cx - r * .45, cy - r * .3, cx + r * .3, cy + r * .5], fill=ink); d.arc([cx + r * .12, cy - r * .15, cx + r * .6, cy + r * .3], -90, 90, fill=ink, width=max(2, int(r * .12)))
        for k in (-.2, .05): d.arc([cx + k * r - r * .08, cy - r * .75, cx + k * r + r * .12, cy - r * .35], 90, 270, fill=accent, width=max(2, int(r * .07)))
    elif kind == 'sofa':
        d.rounded_rectangle([cx - r * .7, cy - r * .1, cx + r * .7, cy + r * .45], radius=r * .12, fill=ink); d.rounded_rectangle([cx - r * .55, cy - r * .55, cx + r * .55, cy - r * .05], radius=r * .12, fill=ink)
    elif kind == 'game':
        d.rounded_rectangle([cx - r * .7, cy - r * .35, cx + r * .7, cy + r * .35], radius=r * .12, fill=ink)
        d.ellipse([cx - r * .4, cy - r * .15, cx - r * .12, cy + r * .13], fill=accent); d.rectangle([cx + r * .15, cy - r * .08, cx + r * .5, cy + r * .08], fill=accent)
    elif kind == 'person':
        d.ellipse([cx - r * .22, cy - r * .7, cx + r * .22, cy - r * .26], fill=ink); d.rounded_rectangle([cx - r * .4, cy - r * .2, cx + r * .4, cy + r * .75], radius=r * .2, fill=ink)
    elif kind == 'hat':
        d.pieslice([cx - r * .6, cy - r * .6, cx + r * .6, cy + r * .6], 180, 360, fill=ink); d.rectangle([cx - r * .78, cy - r * .02, cx + r * .78, cy + r * .16], fill=ink)
        d.rectangle([cx - r * .08, cy - r * .6, cx + r * .08, cy - r * .1], fill=accent)
    elif kind == 'wrench':
        d.line([(cx - r * .55, cy + r * .55), (cx + r * .25, cy - r * .25)], fill=ink, width=max(3, int(r * .22)))
        d.ellipse([cx + r * .05, cy - r * .7, cx + r * .62, cy - r * .13], fill=ink); d.polygon([(cx + r * .3, cy - r * .7), (cx + r * .42, cy - r * .7), (cx + r * .36, cy - r * .38)], fill=accent)
    elif kind == 'bolt':
        d.polygon([(cx + r * .1, cy - r * .75), (cx - r * .45, cy + r * .08), (cx - r * .05, cy + r * .08), (cx - r * .15, cy + r * .75), (cx + r * .45, cy - r * .12), (cx + r * .05, cy - r * .12)], fill=accent)
    elif kind == 'box':
        d.rectangle([cx - r * .6, cy - r * .5, cx + r * .6, cy + r * .55], fill=ink); d.rectangle([cx - r * .08, cy - r * .5, cx + r * .08, cy + r * .55], fill=accent)
        d.rectangle([cx - r * .6, cy - r * .5, cx + r * .6, cy - r * .3], fill=accent) if False else None
    elif kind == 'warn':
        d.polygon([(cx, cy - r * .72), (cx + r * .78, cy + r * .6), (cx - r * .78, cy + r * .6)], outline=ink, width=max(3, int(r * .12)))
        d.rectangle([cx - r * .06, cy - r * .22, cx + r * .06, cy + r * .2], fill=ink); d.ellipse([cx - r * .08, cy + r * .3, cx + r * .08, cy + r * .46], fill=ink)
    elif kind == 'muster':
        d.ellipse([cx - r * .75, cy - r * .75, cx + r * .75, cy + r * .75], outline=ink, width=max(3, int(r * .1)))
        d.ellipse([cx - r * .14, cy - r * .5, cx + r * .14, cy - r * .22], fill=ink); d.rounded_rectangle([cx - r * .26, cy - r * .16, cx + r * .26, cy + r * .5], radius=r * .12, fill=ink)
    elif kind == 'lock':
        d.arc([cx - r * .32, cy - r * .7, cx + r * .32, cy - r * .02], 180, 360, fill=ink, width=max(3, int(r * .12)))
        d.rounded_rectangle([cx - r * .5, cy - r * .15, cx + r * .5, cy + r * .65], radius=r * .1, fill=ink); d.ellipse([cx - r * .08, cy + r * .1, cx + r * .08, cy + r * .26], fill=accent)
    elif kind == 'run':
        d.ellipse([cx - r * .1, cy - r * .7, cx + r * .26, cy - r * .34], fill=ink); d.line([(cx, cy - r * .3), (cx - r * .15, cy + r * .2), (cx - r * .5, cy + r * .5)], fill=ink, width=int(r * .2))
        d.line([(cx - r * .15, cy + r * .2), (cx + r * .3, cy + r * .5)], fill=ink, width=int(r * .2)); d.line([(cx - .3 * r, cy - r * .15), (cx + r * .45, cy - r * .1)], fill=ink, width=int(r * .15))

def _size_for(d, text, font_path, max_w, max_h):
    """Largest font size whose line (ascender to descender) fits max_h and whose text fits max_w."""
    lo, hi = 8, int(max_h * 1.05)
    best = lo
    while lo <= hi:
        mid = (lo + hi) // 2; f = ImageFont.truetype(font_path, mid); b = d.textbbox((0, 0), text, font=f, anchor='ls')
        asc, desc = f.getmetrics()
        if b[2] - b[0] <= max_w and (asc + desc) <= max_h: best = mid; lo = mid + 1
        else: hi = mid - 1
    return best

def paint(spec, W, H):
    """Paint one sign at W x H pixels."""
    plate, ink, accent, border = STYLES[spec['style']]
    im = Image.new('RGB', (W, H), plate); d = ImageDraw.Draw(im)
    pad = H * 0.08; bar = spec['style'] in ('nav', 'staff', 'board', 'green')
    d.rounded_rectangle([pad * 0.4, pad * 0.4, W - pad * 0.4 - 1, H - pad * 0.4 - 1], radius=int(H * 0.12), outline=border, width=max(2, int(H * 0.025)))
    x0 = pad * 1.6; x1 = W - pad * 1.6
    zt = pad * 1.2; zb = H - pad * (2.3 if bar else 1.2)
    if bar: d.rectangle([x0, H - pad * 1.55, x1, H - pad * 1.55 + max(3, int(H * 0.05))], fill=accent)
    Z = zb - zt; cy = (zt + zb) / 2
    if spec['icon']:
        r = min(Z * 0.46, (x1 - x0) * 0.18); icx = x0 + r * 1.1
        _icon(d, spec['icon'], icx, cy, r, ink, accent); x0 = icx + r * 1.35
    tx = (x0 + x1) / 2; sub = spec['sub']
    if spec.get('lines'):
        sz = _size_for(d, spec['text'], FONT_B, x1 - x0, Z * 0.26); ft = ImageFont.truetype(FONT_B, sz)
        d.text((x0, zt), spec['text'], font=ft, fill=accent if spec['style'] == 'board' else ink, anchor='la')
        n = len(spec['lines']); ry = zt + sz * 1.25; rh = (zb - ry) / max(n, 1)
        rows = [ln.partition('  ') for ln in spec['lines']]
        szr = min(min(_size_for(d, l[0], FONT_R, (x1 - x0) * 0.72, rh * 0.95), _size_for(d, l[2].strip() or ' ', FONT_R, (x1 - x0) * 0.25, rh * 0.95)) for l in rows)
        fr = ImageFont.truetype(FONT_R, szr)
        for k, (left, _, right) in enumerate(rows):
            yy = ry + k * rh + rh * 0.5
            d.text((x0, yy), left, font=fr, fill=ink, anchor='lm')
            if right.strip(): d.text((x1, yy), right.strip(), font=fr, fill=ink, anchor='rm')
        return im
    if sub:
        s1 = _size_for(d, spec['text'], FONT_B, x1 - x0, Z * 0.62); s2 = _size_for(d, sub, FONT_R, x1 - x0, Z * 0.28)
        d.text((tx, zt + Z * 0.33), spec['text'], font=ImageFont.truetype(FONT_B, s1), fill=ink, anchor='mm')
        d.text((tx, zt + Z * 0.84), sub, font=ImageFont.truetype(FONT_R, s2), fill=tuple(int(c * 0.8 + p * 0.2) for c, p in zip(ink, plate)), anchor='mm')
    else:
        s1 = _size_for(d, spec['text'], FONT_B, x1 - x0, Z * 0.8)
        d.text((tx, cy), spec['text'], font=ImageFont.truetype(FONT_B, s1), fill=ink, anchor='mm')
    return im

def finalize_signs(F, atlas_name='sign_atlas'):
    """Pack every spec into one atlas, paint it, save it under textures/, and point every sign's UVs at its cell."""
    if not SPECS: return
    scale = 1.0
    while True:
        cells = []; x = y = rowh = 0; ok = True; pad = 6
        for i, s in enumerate(SPECS):
            W = max(16, int(s['w'] * PXM * scale)); H = max(16, int(s['h'] * PXM * scale))
            if x + W + pad > ATLAS_MAX: x = 0; y += rowh + pad; rowh = 0
            cells.append((x, y, W, H)); x += W + pad; rowh = max(rowh, H)
        if y + rowh + pad <= ATLAS_MAX: break
        scale *= 0.85
    AH = 1
    while AH < y + rowh + pad: AH *= 2
    AH = min(AH, ATLAS_MAX); AW = ATLAS_MAX
    atlas = Image.new('RGB', (AW, AH), (30, 30, 34))
    for s, (cx, cy, W, H) in zip(SPECS, cells): atlas.paste(paint(s, W, H), (cx, cy))
    path = os.path.join(TEXDIR, atlas_name + '.png'); atlas.save(path)
    img = bpy.data.images.load(path, check_existing=True); img.reload(); img.colorspace_settings.name = 'sRGB'
    mats = []
    for lit in (False, True):
        nm = atlas_name + ('_lit' if lit else '')
        m = bpy.data.materials.get(nm) or bpy.data.materials.new(nm); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
        out = nt.nodes.new('ShaderNodeOutputMaterial'); b = nt.nodes.new('ShaderNodeBsdfPrincipled'); t = nt.nodes.new('ShaderNodeTexImage'); t.image = img; t.interpolation = 'Cubic'
        nt.links.new(t.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.42
        if lit:
            b.inputs['Emission Color'].default_value = (1, 1, 1, 1); nt.links.new(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 1.4
        nt.links.new(b.outputs[0], out.inputs['Surface']); mats.append(m)
    for o, si, mode in OBJS:
        cx, cy, W, H = cells[SPECS[si]['w'] and si]; cx, cy, W, H = cells[si]
        u0, u1 = cx / AW, (cx + W) / AW; v1 = 1 - cy / AH; v0 = 1 - (cy + H) / AH
        me = o.data; me.materials.clear(); me.materials.append(mats[1 if SPECS[si]['lit'] else 0])
        uv = me.uv_layers['UVMap'].data
        du = 1.5 / AW
        for pi, p in enumerate(me.polygons):
            ls = p.loop_start
            if pi == 0:      # front (+y), verts x1z0, x0z0, x0z1, x1z1: seen from +y the viewer's left is +x
                for li, (u, v) in zip(range(ls, ls + 4), ((u0, v0), (u1, v0), (u1, v1), (u0, v1))): uv[li].uv = (u, v)
            elif pi == 1 and mode == 'double':   # back (-y), verts x0z0, x1z0, x1z1, x0z1: seen from -y the viewer's left is -x
                for li, (u, v) in zip(range(ls, ls + 4), ((u0, v0), (u1, v0), (u1, v1), (u0, v1))): uv[li].uv = (u, v)
            else:            # sides and single-sided back: sample a plate-coloured texel just inside the cell
                for li in range(ls, ls + 4): uv[li].uv = (u0 + du * 3, v0 + (v1 - v0) * 0.5)
    return path
