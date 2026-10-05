"""Second-pass cafeteria assets: detailed arcade basketball, kiosk with rear detail, food-service dressing, lounge softs, rugs with baked patterns."""
from fe_kit import *
from fe_assets_int import STD, I, mb
import os, sys
_pl = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pylib')
if os.path.isdir(_pl) and _pl not in sys.path: sys.path.append(_pl)

def arcade_basketball(F, P):
    """Two-lane arcade basketball machine. Shooters stand at -X; backboards and hoops at +X. About 2.6 m long, 1.5 m wide, 2.5 m high."""
    m = mb(F); L, W = 2.5, 1.5
    navy = (0.07, 0.1, 0.26, 1); red = (0.62, 0.12, 0.08, 1); orange = (0.88, 0.4, 0.1, 1); dark = (0.07, 0.07, 0.09, 1); chrome = (0.72, 0.74, 0.76, 1)
    # plinth and cabinet: rounded side cheeks, raked ramp
    m.rbox(0, 0, 0.06, L, W, 0.12, 0.02, mi=I['steel_charcoal'], rgba=dark)
    for sy in (-1, 1):
        m.rbox(0.05, sy * (W / 2 - 0.09), 0.55, L - 0.1, 0.18, 0.86, 0.05, mi=I['plastic'], rgba=navy)
        m.rbox(0.05, sy * (W / 2 - 0.005), 0.4, L - 0.3, 0.012, 0.05, 0.004, mi=I['emissive'], rgba=(0.55, 0.22, 0.05, 1))      # lit side stripe
        m.rbox(0.05, sy * (W / 2 - 0.19), 1.02, L - 0.14, 0.04, 0.1, 0.02, mi=I['steel_charcoal'], rgba=chrome)                   # top rail
    # lane ramp (raked) with ball channels
    m.rbox(0.0, 0, 0.72, L - 0.5, W - 0.5, 0.05, 0.012, mi=I['plastic'], rgba=(0.12, 0.13, 0.16, 1), rot=(0, -0.1, 0))
    for sy in (-0.37, 0.37):
        m.rbox(0.0, sy, 0.76, L - 0.55, 0.5, 0.012, 0.004, mi=I['plastic'], rgba=(0.2, 0.55, 0.3, 1), rot=(0, -0.1, 0))
        m.rbox(0.0, sy - 0.27, 0.8, L - 0.55, 0.03, 0.08, 0.008, mi=I['steel_charcoal'], rgba=chrome, rot=(0, -0.1, 0))
    m.rbox(0.0, 0, 0.8, L - 0.55, 0.04, 0.1, 0.01, mi=I['steel_charcoal'], rgba=chrome, rot=(0, -0.1, 0))
    # front ball well and balls
    m.rbox(-L / 2 + 0.28, 0, 0.62, 0.5, W - 0.5, 0.2, 0.03, mi=I['plastic'], rgba=red)
    for k in range(5): m.sphere(-L / 2 + 0.28 + (k % 2) * 0.1 - 0.05, -0.42 + k * 0.21, 0.78, 0.065, rings=8, seg=12, mi=I['plastic'], rgba=orange)
    # hoop gantry
    for sy in (-1, 1):
        m.rbox(L / 2 - 0.12, sy * (W / 2 - 0.09), 1.42, 0.1, 0.12, 2.0, 0.03, mi=I['steel_charcoal'], rgba=chrome)
    m.rbox(L / 2 - 0.12, 0, 2.38, 0.12, W - 0.1, 0.14, 0.03, mi=I['steel_charcoal'], rgba=chrome)
    m.rbox(L / 2 - 0.12, 0, 2.58, 0.16, 1.0, 0.28, 0.04, mi=I['plastic'], rgba=navy)
    m.rbox(L / 2 - 0.2, 0, 2.58, 0.02, 0.86, 0.2, 0.005, mi=I['emissive'], rgba=(0.95, 0.35, 0.12, 1))
    for sy in (-0.37, 0.37):
        m.rbox(L / 2 - 0.2, sy, 1.95, 0.04, 0.6, 0.42, 0.015, mi=I['glass'])
        m.rbox(L / 2 - 0.2, sy, 1.95, 0.05, 0.62, 0.44, 0.0, mi=I['steel_charcoal'], rgba=chrome) if False else None
        m.rbox(L / 2 - 0.22, sy, 1.88, 0.015, 0.2, 0.14, 0.004, mi=I['plastic'], rgba=(0.85, 0.2, 0.14, 1))
        for z in (1.74, 2.16): m.rbox(L / 2 - 0.2, sy, z, 0.05, 0.6, 0.025, 0.008, mi=I['steel_charcoal'], rgba=chrome)
        for sy2 in (-0.3, 0.3): m.rbox(L / 2 - 0.2, sy + sy2, 1.95, 0.05, 0.025, 0.46, 0.008, mi=I['steel_charcoal'], rgba=chrome)
        m.add(p_torus(0.115, 0.009, 28, 6), (L / 2 - 0.36, sy, 1.72), (0, 0, 0), mi=I['steel_accent'], rgba=orange)
        m.rbox(L / 2 - 0.24, sy, 1.72, 0.1, 0.04, 0.02, 0.006, mi=I['steel_accent'], rgba=orange)
        for k in range(16):
            a = k * 2 * math.pi / 16
            m.between((L / 2 - 0.36 + math.cos(a) * 0.113, sy + math.sin(a) * 0.113, 1.715), (L / 2 - 0.36 + math.cos(a) * 0.07, sy + math.sin(a) * 0.07, 1.42), 0.0035, seg=4, mi=I['fabric'], rgba=(0.9, 0.9, 0.88, 1))
        for r in range(3):
            z = 1.68 - r * 0.1; rr = 0.113 - r * 0.012
            m.add(p_torus(rr, 0.0025, 20, 4), (L / 2 - 0.36, sy, z), (0, 0, 0), mi=I['fabric'], rgba=(0.9, 0.9, 0.88, 1))
        m.rbox(L / 2 - 0.2, sy, 1.12, 0.05, 0.4, 0.24, 0.02, mi=I['screen'], rgba=(0.2, 0.9, 0.35, 1))                      # per-lane score
    # catch chute at the back
    m.rbox(L / 2 - 0.3, 0, 0.55, 0.45, W - 0.5, 0.5, 0.03, mi=I['plastic'], rgba=navy)
    m.rbox(L / 2 - 0.3, 0, 0.82, 0.45, W - 0.5, 0.02, 0.006, mi=I['plastic'], rgba=(0.12, 0.13, 0.16, 1))
    # coin slot console
    m.rbox(-L / 2 + 0.05, 0, 1.0, 0.18, 0.5, 0.45, 0.03, mi=I['plastic'], rgba=red); m.rbox(-L / 2 - 0.045, 0, 1.08, 0.02, 0.34, 0.1, 0.005, mi=I['emissive'], rgba=(0.95, 0.85, 0.3, 1))
    m.rbox(-L / 2 - 0.04, 0, 0.95, 0.02, 0.1, 0.12, 0.006, mi=I['steel_charcoal'], rgba=chrome)
    return m.finish('proto_arcade_basketball', P)

def kiosk_v2(F, P):
    """Self-order kiosk: tilted touchscreen, card reader, receipt slot, ticket printer, rear vent grille and service door."""
    m = mb(F); body = (0.1, 0.12, 0.2, 1); chrome = (0.72, 0.74, 0.76, 1); orange = (0.86, 0.42, 0.08, 1)
    m.rbox(0, 0, 0.55, 0.62, 0.42, 1.1, 0.035, mi=I['plastic'], rgba=body)
    m.rbox(0, 0.03, 1.28, 0.62, 0.3, 0.52, 0.045, rot=(-0.32, 0, 0), mi=I['plastic'], rgba=body)
    m.rbox(0, 0.196, 1.29, 0.5, 0.012, 0.4, 0.006, rot=(-0.32, 0, 0), mi=I['steel_charcoal'], rgba=(0.02, 0.02, 0.03, 1))
    m.quad_image(0, 0.204, 1.295, 0.46, 0.36, I['tv_slide']) if False else m.rbox(0, 0.204, 1.295, 0.46, 0.006, 0.36, 0.003, rot=(-0.32, 0, 0), mi=I['screen'], rgba=(0.95, 0.7, 0.3, 1))
    m.rbox(0, 0.215, 0.98, 0.26, 0.05, 0.12, 0.014, mi=I['steel_charcoal'], rgba=(0.06, 0.06, 0.07, 1)); m.rbox(0, 0.242, 0.98, 0.18, 0.006, 0.02, 0.003, mi=I['emissive'], rgba=(0.3, 0.9, 0.5, 1))
    m.rbox(0, 0.213, 0.76, 0.22, 0.03, 0.02, 0.006, mi=I['steel_charcoal'], rgba=(0.01, 0.01, 0.01, 1)); m.rbox(0, 0.215, 0.62, 0.3, 0.015, 0.2, 0.01, mi=I['steel_charcoal'], rgba=(0.14, 0.14, 0.16, 1))
    m.rbox(0, 0.0, 1.62, 0.66, 0.36, 0.06, 0.025, mi=I['steel_accent'], rgba=orange)
    for k in range(10): m.rbox(0, -0.215, 0.5 + k * 0.045, 0.34, 0.01, 0.014, 0.003, mi=I['steel_charcoal'], rgba=(0.04, 0.04, 0.05, 1))
    m.rbox(0, -0.215, 0.95, 0.4, 0.006, 0.5, 0.004, mi=I['steel_charcoal'], rgba=(0.14, 0.15, 0.2, 1)); m.rbox(0.12, -0.222, 0.95, 0.03, 0.02, 0.08, 0.008, mi=I['steel_charcoal'], rgba=chrome)
    m.rbox(0, 0, 0.02, 0.7, 0.5, 0.04, 0.012, mi=I['steel_charcoal'], rgba=(0.07, 0.07, 0.08, 1))
    m.between((0.2, -0.21, 0.09), (0.28, -0.4, 0.02), 0.012, seg=6, mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
    return m.finish('proto_kiosk_v2', P)

def tray_stack(F, P, n=8):
    m = mb(F); cols = [(0.12, 0.35, 0.5, 1), (0.8, 0.45, 0.15, 1)]
    for k in range(n): m.rbox(0, 0, 0.012 + k * 0.026, 0.44, 0.32, 0.022, 0.008, mi=I['plastic'], rgba=cols[k % 2])
    return m.finish('proto_tray_stack', P)

def plate_stack(F, P):
    m = mb(F)
    for k in range(10): m.lathe([(0.0, 0.0), (0.07, 0.0), (0.11, 0.012), (0.115, 0.018), (0.0, 0.01)], loc=(0, 0, k * 0.014), seg=24, mi=I['plastic'], rgba=(0.92, 0.92, 0.9, 1))
    return m.finish('proto_plate_stack', P)

def cup_stack(F, P):
    m = mb(F)
    for k in range(3): m.lathe([(0.0, 0.0), (0.03, 0.0), (0.042, 0.1), (0.044, 0.105), (0.0, 0.105)], loc=(0, 0, k * 0.03 + 0.0), seg=16, mi=I['plastic'], rgba=(0.9, 0.9, 0.88, 1))
    return m.finish('proto_cup_stack', P)

def bread_basket(F, P):
    m = mb(F)
    m.lathe([(0.0, 0.0), (0.12, 0.0), (0.17, 0.08), (0.18, 0.09), (0.16, 0.09), (0.11, 0.015)], seg=20, mi=I['timber'], rgba=(0.55, 0.38, 0.2, 1))
    rnd = random.Random(1)
    for k in range(6): m.sphere(math.cos(k) * 0.06, math.sin(k) * 0.06, 0.1, 0.06, 0.04, 0.035, rings=6, seg=10, mi=I['props'], rgba=(0.62 + rnd.uniform(-0.05, 0.05), 0.4, 0.18, 1))
    return m.finish('proto_bread_basket', P)

def cutlery_bin(F, P):
    m = mb(F)
    m.rbox(0, 0, 0.1, 0.34, 0.2, 0.2, 0.012, mi=I['steel_charcoal'], rgba=(0.7, 0.72, 0.74, 1))
    for k in range(3): m.rbox(-0.11 + k * 0.11, 0, 0.225, 0.08, 0.14, 0.12, 0.008, mi=I['steel_charcoal'], rgba=(0.82, 0.84, 0.86, 1))
    return m.finish('proto_cutlery_bin', P)

def sanitiser_station(F, P):
    m = mb(F)
    m.lathe([(0.0, 0.0), (0.16, 0.0), (0.17, 0.02), (0.1, 0.04), (0.04, 0.06)], seg=20, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    m.cylz(0, 0, 0.05, 1.05, 0.03, seg=10, mi=I['steel_charcoal'], rgba=(0.72, 0.74, 0.76, 1))
    m.rbox(0, 0.05, 1.12, 0.12, 0.1, 0.22, 0.02, mi=I['plastic'], rgba=(0.88, 0.88, 0.86, 1)); m.rbox(0, 0.1, 1.2, 0.05, 0.05, 0.03, 0.01, mi=I['plastic'], rgba=(0.2, 0.5, 0.8, 1))
    return m.finish('proto_sanitiser', P)

def recycling_bins(F, P):
    m = mb(F)
    for k, c in enumerate(((0.15, 0.4, 0.2, 1), (0.15, 0.25, 0.55, 1), (0.1, 0.1, 0.1, 1))):
        x = (k - 1) * 0.56
        m.rbox(x, 0, 0.45, 0.5, 0.45, 0.9, 0.03, mi=I['plastic'], rgba=c)
        m.rbox(x, 0.23, 0.78, 0.3, 0.012, 0.12, 0.006, mi=I['plastic'], rgba=(0.03, 0.03, 0.03, 1))
        m.rbox(x, 0.23, 0.55, 0.26, 0.012, 0.18, 0.004, mi=I['signage'], rgba=(0.9, 0.9, 0.88, 1))
    return m.finish('proto_recycling', P)

def tray_trolley(F, P):
    m = mb(F); steel = (0.72, 0.74, 0.76, 1)
    for sx in (-1, 1):
        for sy in (-1, 1): m.cylz(sx * 0.4, sy * 0.28, 0.12, 1.5, 0.014, seg=8, mi=I['steel_charcoal'], rgba=steel); m.add(p_cyl(0.05, 0.03, 12), (sx * 0.4, sy * 0.28, 0.06), (math.pi / 2, 0, 0), mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
    for z in (0.35, 0.8, 1.25):
        m.rbox(0, 0, z, 0.9, 0.64, 0.02, 0.006, mi=I['steel_charcoal'], rgba=steel)
        for k in range(4 if z < 1.2 else 2): m.rbox(-0.3 + k * 0.2, 0, z + 0.03 + 0.0, 0.02, 0.5, 0.04, 0.004, mi=I['steel_charcoal'], rgba=steel) if False else m.rbox(0, -0.1 + k * 0.07, z + 0.02, 0.4, 0.06, 0.02, 0.006, mi=I['plastic'], rgba=[(0.12, 0.35, 0.5, 1), (0.8, 0.45, 0.15, 1)][k % 2])
    m.between((-0.42, -0.34, 1.5), (0.42, -0.34, 1.5), 0.016, seg=8, mi=I['steel_charcoal'], rgba=steel)
    return m.finish('proto_tray_trolley', P)

def bean_bag(F, P, rgba=(0.8, 0.35, 0.1, 1)):
    m = mb(F)
    m.add(p_cushion(0.8, 0.8, 0.55, 0.2, 2), (0, 0, 0.3), (0, 0, 0), mi=I['fabric'], rgba=rgba)
    return m.finish('proto_bean_bag', P)

def stool(F, P, rgba=(0.12, 0.17, 0.35, 1)):
    m = mb(F)
    m.cylz(0, 0, 0.62, 0.68, 0.18, seg=20, bevel=0.02, mi=I['fabric'], rgba=rgba)
    for k in range(4): a = k * math.pi / 2 + 0.4; m.between((math.cos(a) * 0.1, math.sin(a) * 0.1, 0.62), (math.cos(a) * 0.2, math.sin(a) * 0.2, 0.0), 0.014, seg=8, mi=I['steel_charcoal'], rgba=(0.72, 0.74, 0.76, 1))
    m.add(p_torus(0.17, 0.01, 20, 5), (0, 0, 0.25), (0, 0, 0), mi=I['steel_charcoal'], rgba=(0.72, 0.74, 0.76, 1))
    return m.finish('proto_stool', P)

def side_table(F, P):
    m = mb(F)
    m.cylz(0, 0, 0.45, 0.48, 0.25, seg=24, bevel=0.01, mi=I['laminate'], rgba=(0.72, 0.64, 0.52, 1))
    for k in range(3): a = k * 2.094 + 0.5; m.between((math.cos(a) * 0.14, math.sin(a) * 0.14, 0.45), (math.cos(a) * 0.2, math.sin(a) * 0.2, 0.0), 0.016, seg=8, mi=I['timber'], rgba=(0.3, 0.17, 0.08, 1))
    return m.finish('proto_side_table', P)

def throw_cushion(F, P, rgba=(0.82, 0.62, 0.2, 1)):
    m = mb(F); m.add(p_cushion(0.42, 0.14, 0.42, 0.04, 1), (0, 0, 0.21), (0, 0, 0), mi=I['fabric'], rgba=rgba); return m.finish('proto_cushion', P)

def table_lamp(F, P):
    m = mb(F)
    m.lathe([(0.0, 0.0), (0.07, 0.0), (0.075, 0.02), (0.04, 0.2), (0.03, 0.3), (0.0, 0.3)], seg=20, mi=I['plastic'], rgba=(0.82, 0.78, 0.7, 1))
    m.lathe([(0.1, 0.28), (0.07, 0.42), (0.13, 0.43), (0.17, 0.3)], seg=24, mi=I['fabric'], rgba=(0.9, 0.82, 0.62, 1))
    m.sphere(0, 0, 0.35, 0.04, rings=6, seg=10, mi=I['emissive'], rgba=(1.0, 0.85, 0.55, 1))
    return m.finish('proto_table_lamp', P)

def rug_texture(name, kind, size=(1024, 768)):
    """Paint a rug pattern into textures/<name>.png (baked, no geometry)."""
    from PIL import Image, ImageDraw
    from fe_common import TEXDIR
    W, H = size; im = Image.new('RGB', size); d = ImageDraw.Draw(im)
    if kind == 'game':
        base, a, b = (20, 26, 66), (230, 120, 30), (240, 232, 214)
        d.rectangle([0, 0, W, H], fill=base)
        step = 64
        for iy in range(0, H, step):
            for ix in range(0, W, step):
                if ((ix // step) + (iy // step)) % 2 == 0: d.rectangle([ix, iy, ix + step - 1, iy + step - 1], fill=(30, 38, 88))
        for off, col in ((22, a), (44, b), (66, a)): d.rectangle([off, off, W - off - 1, H - off - 1], outline=col, width=5)
        for k in range(5):
            cx = W * (k + 0.5) / 5; cy = H / 2
            d.polygon([(cx, cy - 70), (cx + 70, cy), (cx, cy + 70), (cx - 70, cy)], fill=a if k % 2 == 0 else b)
            d.polygon([(cx, cy - 36), (cx + 36, cy), (cx, cy + 36), (cx - 36, cy)], fill=base)
    else:
        base, a, b = (130, 44, 28), (214, 190, 140), (60, 30, 24)
        d.rectangle([0, 0, W, H], fill=base)
        for off, col, wd in ((20, b, 10), (40, a, 5), (58, b, 4)): d.rectangle([off, off, W - off - 1, H - off - 1], outline=col, width=wd)
        d.rectangle([90, 90, W - 91, H - 91], fill=a)
        for k in range(0, W - 180, 56):
            for l in range(0, H - 180, 56):
                if (k // 56 + l // 56) % 2 == 0: d.ellipse([100 + k, 100 + l, 100 + k + 40, 100 + l + 40], outline=base, width=4)
                else: d.rectangle([108 + k, 108 + l, 108 + k + 26, 108 + l + 26], outline=(150, 100, 60), width=3)
        d.rectangle([110, 110, W - 111, H - 111], outline=base, width=6)
    # woven noise
    import random as _r
    rnd = _r.Random(3); px = im.load()
    for _ in range(W * H // 6):
        x = rnd.randrange(W); y = rnd.randrange(H); r, g, bl = px[x, y]; k = rnd.randint(-14, 14); px[x, y] = (max(0, min(255, r + k)), max(0, min(255, g + k)), max(0, min(255, bl + k)))
    path = os.path.join(TEXDIR, name + '.png'); im.save(path); return path
