"""Mine surface depot props. Vehicles are built with the length along +x (front toward +x), standing on z = 0; wheels use fe_assets_yard.wheel.
Lettering is never modelled: names and numbers come from the baked atlas (fe_signs) on instances."""
import math, random
from fe_kit import *
from fe_assets_int import STD, I, mb
from fe_assets_yard import wheel

WHITE = (0.86, 0.86, 0.84, 1); ORANGE = (0.9, 0.4, 0.05, 1); DARK = (0.06, 0.06, 0.07, 1); STEEL = (0.72, 0.74, 0.76, 1); AMBER = (1.0, 0.62, 0.1, 1)

def site_pickup(F, P, paint=WHITE):
    """Utility 4x4 pickup, 5.3 m: crew cab with raked screen and side glass, wheel-arch flares, bull bar, spot lamps, roof light bar, load bed with ladder rack, orange side band."""
    m = mb(F); L, W = 5.3, 1.95
    m.rbox(0, 0, 0.62, L - 0.2, W - 0.1, 0.56, 0.07, mi=I['paint'], rgba=paint)                                   # lower body
    m.rbox(0.55, 0, 1.0, 2.9, W - 0.12, 0.28, 0.06, mi=I['paint'], rgba=paint)                                     # shoulder
    m.rbox(2.0, 0, 0.98, 1.3, W - 0.14, 0.14, 0.05, rot=(0, 0.05, 0), mi=I['paint'], rgba=paint)                  # bonnet
    m.cushion(0.35, 0, 1.45, 1.55, W - 0.2, 0.52, r=0.1, levels=1, mi=I['paint'], rgba=paint)                     # cab roof and pillars
    m.rbox(1.2, 0, 1.38, 0.06, W - 0.32, 0.56, 0.02, rot=(0, -0.62, 0), mi=I['glass'])                              # windscreen
    for sy in (-1, 1):
        m.rbox(0.28, sy * (W / 2 - 0.06), 1.33, 1.3, 0.03, 0.44, 0.02, mi=I['glass'])                              # side glass
        m.rbox(0.28, sy * (W / 2 - 0.08), 1.33, 0.02, 0.03, 0.44, 0.005, mi=I['steel_charcoal'], rgba=DARK)
        m.rbox(0.58, sy * (W / 2 + 0.01), 1.05, 0.14, 0.04, 0.03, 0.01, mi=I['steel_charcoal'], rgba=DARK)           # door handle
        m.rbox(1.05, sy * (W / 2 + 0.04), 1.28, 0.1, 0.07, 0.14, 0.02, mi=I['plastic'], rgba=DARK)                  # mirror
        for sx in (-1, 1): wheel(m, sx * 1.62 + 0.0, sy * 0.86, 0.4, r=0.42, w=0.3, flip=sy)
        m.rbox(0.5, sy * (W / 2 - 0.045), 0.66, 3.2, 0.012, 0.14, 0.004, mi=I['signage'], rgba=ORANGE)                # orange side band
        for sx in (-1, 1): m.rbox(sx * 1.62, sy * 0.93, 0.62, 1.04, 0.05, 0.1, 0.03, mi=I['plastic'], rgba=DARK)     # arch flares
    m.rbox(-1.5, 0, 0.9, 1.8, W - 0.12, 0.05, 0.01, mi=I['steel_charcoal'], rgba=DARK)                              # bed floor
    for sy in (-1, 1): m.rbox(-1.5, sy * (W / 2 - 0.1), 0.98, 1.8, 0.06, 0.4, 0.02, mi=I['paint'], rgba=paint)       # bed sides
    m.rbox(-2.45, 0, 0.98, 0.06, W - 0.14, 0.4, 0.02, mi=I['paint'], rgba=paint)                                     # tailgate
    m.rbox(-0.65, 0, 0.98, 0.06, W - 0.14, 0.4, 0.02, mi=I['paint'], rgba=paint)                                     # bulkhead
    for sx in (-2.1, -0.95):
        m.between((sx, -0.9, 1.15), (sx, 0.9, 1.15), 0.02, seg=8, mi=I['steel_charcoal'], rgba=DARK)
        for sy in (-1, 1): m.between((sx, sy * 0.9, 0.95), (sx, sy * 0.9, 1.5), 0.02, seg=8, mi=I['steel_charcoal'], rgba=DARK)
    for sy in (-1, 1): m.between((-2.2, sy * 0.9, 1.5), (-0.85, sy * 0.9, 1.5), 0.02, seg=8, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(2.58, 0, 0.55, 0.14, W - 0.1, 0.3, 0.05, mi=I['plastic'], rgba=DARK)                                      # front bumper
    m.between((2.68, -0.55, 0.5), (2.68, -0.55, 1.1), 0.03, seg=8, mi=I['steel_charcoal'], rgba=DARK); m.between((2.68, 0.55, 0.5), (2.68, 0.55, 1.1), 0.03, seg=8, mi=I['steel_charcoal'], rgba=DARK)
    m.between((2.68, -0.55, 1.05), (2.68, 0.55, 1.05), 0.03, seg=8, mi=I['steel_charcoal'], rgba=DARK)                 # bull bar
    m.rbox(2.64, 0, 0.8, 0.04, 1.4, 0.16, 0.02, mi=I['plastic'], rgba=(0.12, 0.12, 0.14, 1))                          # grille
    for sy in (-1, 1):
        m.rbox(2.62, sy * 0.72, 0.84, 0.05, 0.2, 0.1, 0.02, mi=I['emissive'], rgba=(1.0, 0.95, 0.85, 1))             # headlamps
        m.rbox(-2.63, sy * 0.8, 0.95, 0.04, 0.12, 0.16, 0.015, mi=I['emissive'], rgba=(0.9, 0.1, 0.05, 1))            # tail lamps
        m.add(p_cyl(0.07, 0.07, 12), (2.7, sy * 0.3, 1.05), (0, math.pi / 2, 0), mi=I['emissive'], rgba=(1.0, 0.95, 0.85, 1))   # spot lamps
    m.rbox(0.35, 0, 1.76, 0.18, 1.2, 0.06, 0.02, mi=I['steel_charcoal'], rgba=DARK)                                  # light bar
    for k in range(5): m.rbox(0.35 + 0.0, -0.46 + k * 0.23, 1.79, 0.12, 0.17, 0.02, 0.005, mi=I['emissive'], rgba=AMBER)
    m.add(p_cyl(0.008, 0.9, 6), (-2.4, 0.88, 1.3), mi=I['steel_charcoal'], rgba=DARK)                                # whip aerial
    return m.finish('proto_site_pickup', P)

def crew_van(F, P, paint=WHITE):
    """Crew van 5.4 m: boxy body, screen, side windows, sliding door, rear doors, roof rack and ladder, amber beacon, orange band."""
    m = mb(F); L, W = 5.4, 2.0
    m.rbox(0, 0, 1.2, L - 0.2, W - 0.1, 1.6, 0.14, mi=I['paint'], rgba=paint)
    m.rbox(2.3, 0, 0.75, 0.9, W - 0.14, 0.6, 0.1, mi=I['paint'], rgba=paint)
    m.rbox(1.62, 0, 1.55, 0.06, W - 0.28, 0.8, 0.02, rot=(0, -0.38, 0), mi=I['glass'])
    for sy in (-1, 1):
        for sx in (-1, 1): wheel(m, sx * 1.65, sy * 0.88, 0.4, r=0.42, w=0.3, flip=sy)
        m.rbox(1.55, sy * (W / 2 - 0.05), 1.55, 0.85, 0.03, 0.52, 0.02, mi=I['glass'])
        m.rbox(-0.4, sy * (W / 2 - 0.05), 1.55, 1.7, 0.03, 0.5, 0.02, mi=I['glass'])
        m.rbox(-0.4, sy * (W / 2 - 0.05), 1.0, 0.02, 0.03, 1.3, 0.005, mi=I['steel_charcoal'], rgba=DARK)           # sliding door seam
        m.rbox(0.45, sy * (W / 2 - 0.04), 1.0, 0.14, 0.04, 0.05, 0.01, mi=I['steel_charcoal'], rgba=DARK)
        m.rbox(0.0, sy * (W / 2 - 0.04), 0.74, 4.6, 0.012, 0.16, 0.004, mi=I['signage'], rgba=ORANGE)
        m.rbox(1.45, sy * (W / 2 + 0.05), 1.55, 0.1, 0.07, 0.15, 0.02, mi=I['plastic'], rgba=DARK)
        m.rbox(2.58, sy * 0.72, 0.9, 0.05, 0.22, 0.1, 0.02, mi=I['emissive'], rgba=(1.0, 0.95, 0.85, 1))
        m.rbox(-2.68, sy * 0.78, 1.0, 0.04, 0.12, 0.2, 0.015, mi=I['emissive'], rgba=(0.9, 0.1, 0.05, 1))
    m.rbox(2.68, 0, 0.5, 0.16, W - 0.1, 0.3, 0.05, mi=I['plastic'], rgba=DARK); m.rbox(-2.68, 0, 0.5, 0.14, W - 0.1, 0.26, 0.05, mi=I['plastic'], rgba=DARK)
    m.rbox(2.66, 0, 0.75, 0.04, 1.2, 0.16, 0.02, mi=I['plastic'], rgba=(0.12, 0.12, 0.14, 1))
    m.rbox(-2.68, 0, 1.2, 0.02, 0.02, 1.4, 0.004, mi=I['steel_charcoal'], rgba=DARK)                                   # rear door seam
    m.rbox(-2.69, 0.2, 1.05, 0.03, 0.04, 0.16, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    for x in (-1.6, -0.2, 1.2): m.rbox(x, 0, 2.06, 0.05, W - 0.3, 0.05, 0.01, mi=I['steel_charcoal'], rgba=DARK)     # roof rack
    for sy in (-1, 1): m.rbox(-0.2, sy * (W / 2 - 0.2), 2.06, 3.0, 0.05, 0.05, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    for sy in (-0.2, 0.2): m.between((-1.6, sy, 2.16), (1.0, sy, 2.16), 0.02, seg=8, mi=I['steel_brushed'], rgba=STEEL)  # ladder rails
    for k in range(9): m.between((-1.55 + k * 0.28, -0.2, 2.16), (-1.55 + k * 0.28, 0.2, 2.16), 0.012, seg=6, mi=I['steel_brushed'], rgba=STEEL)
    m.add(p_cyl(0.11, 0.1, 14), (1.9, 0, 2.05), mi=I['emissive'], rgba=AMBER)
    return m.finish('proto_crew_van', P)

def ore_car(F, P):
    """Mine tipper car 2.4 m on rail (gauge 1.56 m): riveted tub with stiffening ribs, drop-sides, two axles with spoked wheels, buffers and couplings, heaped with ore."""
    m = mb(F); rnd = random.Random(4); body = (0.28, 0.2, 0.15, 1); rib = (0.2, 0.15, 0.12, 1)
    m.rbox(0, 0, 0.62, 2.3, 1.2, 0.08, 0.02, mi=I['paint'], rgba=rib)                                                  # floor frame
    for sy in (-1, 1):
        m.rbox(0, sy * 0.58, 0.98, 2.4, 0.06, 0.72, 0.02, rot=(sy * -0.1, 0, 0), mi=I['paint'], rgba=body)           # flared sides
        m.rbox(0, sy * 0.64, 1.36, 2.46, 0.09, 0.08, 0.025, mi=I['paint'], rgba=rib)                                  # top rim
        for k in range(5): m.rbox(-1.0 + k * 0.5, sy * 0.63, 0.98, 0.07, 0.04, 0.72, 0.01, rot=(sy * -0.1, 0, 0), mi=I['paint'], rgba=rib)
        for sx in (-0.8, 0.8):
            m.rbox(sx, sy * 0.78, 0.4, 0.14, 0.07, 0.3, 0.015, mi=I['steel_charcoal'], rgba=DARK)                      # axle boxes
            m.add(p_lathe([(0.0, 0.0), (0.2, 0.0), (0.21, 0.02), (0.21, 0.06), (0.0, 0.06)], 22), (sx, sy * 0.76, 0.26), (math.pi / 2, 0, 0), mi=I['steel_charcoal'], rgba=DARK)
            m.add(p_cyl(0.09, 0.04, 12), (sx, sy * 0.8, 0.26), (math.pi / 2, 0, 0), mi=I['steel_brushed'], rgba=STEEL)
    for sx in (-1, 1):
        m.rbox(sx * 1.18, 0, 1.0, 0.06, 1.14, 0.7, 0.02, rot=(0, sx * 0.1, 0), mi=I['paint'], rgba=body)
        m.between((sx * 1.4, 0.0, 0.55), (sx * 1.12, 0.0, 0.55), 0.04, seg=8, mi=I['steel_charcoal'], rgba=DARK)        # coupling
        m.cylz(sx * 1.2, 0.35, 0.5, 0.64, 0.04, seg=8, mi=I['steel_charcoal'], rgba=DARK); m.cylz(sx * 1.2, -0.35, 0.5, 0.64, 0.04, seg=8, mi=I['steel_charcoal'], rgba=DARK)
    for sx in (-0.8, 0.8): m.between((sx, -0.78, 0.26), (sx, 0.78, 0.26), 0.03, seg=8, mi=I['steel_charcoal'], rgba=DARK)  # axles
    for k in range(26):                                                                                                 # ore heap
        x = rnd.uniform(-1.0, 1.0); y = rnd.uniform(-0.45, 0.45); hh = 1.28 + 0.2 * (1 - (abs(x) / 1.1) ** 2) * (1 - (abs(y) / 0.5) ** 2) + rnd.uniform(0, 0.08)
        r = rnd.uniform(0.11, 0.2); m.sphere(x, y, hh, r * 1.1, r, r * 0.8, rings=4, seg=6, mi=I['props'], rgba=[(0.24, 0.22, 0.2, 1), (0.34, 0.3, 0.25, 1), (0.16, 0.15, 0.14, 1), (0.45, 0.33, 0.2, 1)][k % 4])
    return m.finish('proto_ore_car', P)

def ore_pile(F, P, seed=0, r=1.4, h=1.1):
    """Heap of broken ore: a displaced low-poly mound plus loose lumps; colour by grade via the instance material slot (dark = waste, brown = ore)."""
    rnd = random.Random(seed); m = mb(F)
    pb = bmesh.new(); res = bmesh.ops.create_icosphere(pb, subdivisions=3, radius=1.0)
    for v in res['verts']:
        z = max(v.co.z, 0.0); k = 1.0 + 0.16 * math.sin(v.co.x * 5 + seed) * math.cos(v.co.y * 4 - seed) + rnd.uniform(-0.05, 0.05)
        v.co = Vector((v.co.x * r * k, v.co.y * r * 0.86 * k, z * h * k - 0.02 if z > 0 else -0.05))
    for f in pb.faces: f.smooth = False
    col = [(0.22, 0.2, 0.18, 1), (0.34, 0.27, 0.19, 1), (0.14, 0.14, 0.15, 1)][seed % 3]
    m.add(pb, mi=I['props'], rgba=col)
    for k in range(22):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0.2, 1.0) * r; z = max(0.0, h * (1 - (d / r) ** 2) * 0.8)
        s = rnd.uniform(0.08, 0.2); m.sphere(math.cos(a) * d, math.sin(a) * d * 0.86, z + s * 0.5, s * 1.1, s, s * 0.8, rings=4, seg=6, mi=I['props'], rgba=tuple(c * rnd.uniform(0.7, 1.3) for c in col[:3]) + (1,))
    return m.finish(f'proto_ore_pile_{seed}', P)

def site_cabin(F, P):
    """Portable site cabin 6.0 x 2.6 x 2.7: pressed-steel body, plinth, roof overhang with gutter, two barred windows, glazed door with canopy, three steps and rails, AC unit, roof vent, lifting eyes, conduit. Front (door side) toward +y."""
    m = mb(F); L, D, H = 6.0, 2.6, 2.7; body = (0.5, 0.55, 0.58, 1)
    m.rbox(0, 0, 0.12, L, D, 0.24, 0.02, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(0, 0, 1.45, L - 0.1, D - 0.1, 2.5, 0.05, mi=I['paint'], rgba=body)
    for k in range(int(L / 0.6)):                                                                                       # pressed ribs
        x = -L / 2 + 0.3 + k * 0.6
        m.rbox(x, D / 2 - 0.045, 1.45, 0.025, 0.012, 2.4, 0.003, mi=I['paint'], rgba=tuple(c * 0.85 for c in body[:3]) + (1,)); m.rbox(x, -D / 2 + 0.045, 1.45, 0.025, 0.012, 2.4, 0.003, mi=I['paint'], rgba=tuple(c * 0.85 for c in body[:3]) + (1,))
    m.rbox(0, 0, 0.5, L - 0.08, D - 0.08, 0.34, 0.03, mi=I['paint'], rgba=(0.9, 0.4, 0.05, 1))                      # orange base band
    m.rbox(0, 0, H + 0.04, L + 0.3, D + 0.3, 0.1, 0.02, mi=I['paint'], rgba=tuple(c * 0.8 for c in body[:3]) + (1,))   # roof
    m.between((-L / 2 - 0.15, D / 2 + 0.15, H - 0.02), (L / 2 + 0.15, D / 2 + 0.15, H - 0.02), 0.03, seg=8, mi=I['steel_charcoal'], rgba=DARK)   # gutter
    for wx in (-1.8, 0.2):
        m.rbox(wx, D / 2 - 0.02, 1.6, 1.0, 0.06, 0.8, 0.01, mi=I['steel_charcoal'], rgba=DARK)
        m.rbox(wx, D / 2 + 0.005, 1.6, 0.9, 0.012, 0.7, 0.004, mi=I['glass'])
        for k in range(5): m.between((wx - 0.4 + k * 0.2, D / 2 + 0.05, 1.25), (wx - 0.4 + k * 0.2, D / 2 + 0.05, 1.95), 0.008, seg=6, mi=I['steel_charcoal'], rgba=DARK)
        m.rbox(wx, D / 2 + 0.05, 1.18, 1.1, 0.1, 0.04, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    dx = 2.1
    m.rbox(dx, D / 2 - 0.02, 1.1, 1.0, 0.07, 2.1, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(dx, D / 2 + 0.02, 1.1, 0.88, 0.05, 2.0, 0.01, mi=I['paint'], rgba=(0.2, 0.3, 0.4, 1))
    m.rbox(dx, D / 2 + 0.05, 1.55, 0.5, 0.012, 0.6, 0.004, mi=I['glass'])
    m.rbox(dx + 0.34, D / 2 + 0.07, 1.05, 0.04, 0.05, 0.16, 0.01, mi=I['steel_brushed'], rgba=STEEL)
    m.rbox(dx, D / 2 + 0.3, 2.3, 1.4, 0.6, 0.05, 0.01, mi=I['paint'], rgba=tuple(c * 0.8 for c in body[:3]) + (1,))   # door canopy
    for sx in (-0.65, 0.65): m.between((dx + sx, D / 2 + 0.02, 2.28), (dx + sx, D / 2 + 0.55, 2.28), 0.015, seg=6, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(dx, D / 2 + 0.3, 2.22, 0.3, 0.12, 0.05, 0.01, mi=I['emissive'], rgba=(1.0, 0.92, 0.75, 1))
    for k in range(3): m.rbox(dx, D / 2 + 0.3 + (2 - k) * 0.28, 0.24 + k * 0.2 - 0.1 + 0.1, 1.1, 0.26, 0.04, 0.008, mi=I['steel_brushed'], rgba=STEEL)   # steps
    for sx in (-0.58, 0.58):
        m.between((dx + sx, D / 2 + 0.2, 0.3), (dx + sx, D / 2 + 0.2, 1.0), 0.02, seg=6, mi=I['steel_charcoal'], rgba=DARK)
        m.between((dx + sx, D / 2 + 0.2, 1.0), (dx + sx, D / 2 + 0.85, 0.5), 0.02, seg=6, mi=I['steel_charcoal'], rgba=DARK)
        m.between((dx + sx, D / 2 + 0.85, 0.4), (dx + sx, D / 2 + 0.85, 0.5), 0.02, seg=6, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(-2.4, -D / 2 - 0.15, 1.9, 0.9, 0.3, 0.55, 0.03, mi=I['plastic'], rgba=(0.82, 0.82, 0.8, 1))                  # AC unit (rear)
    for k in range(6): m.rbox(-2.4, -D / 2 - 0.31, 1.7 + k * 0.07, 0.8, 0.012, 0.03, 0.004, mi=I['steel_charcoal'], rgba=DARK)
    m.cylz(1.6, 0.4, H + 0.09, H + 0.32, 0.18, seg=14, mi=I['steel_brushed'], rgba=STEEL); m.cylz(1.6, 0.4, H + 0.32, H + 0.36, 0.24, seg=14, mi=I['steel_brushed'], rgba=STEEL)
    for sx in (-1, 1):
        for sy in (-1, 1): m.rbox(sx * (L / 2 - 0.15), sy * (D / 2 - 0.15), H + 0.14, 0.14, 0.14, 0.08, 0.02, mi=I['steel_charcoal'], rgba=DARK)
    m.between((-0.3, D / 2 + 0.02, 2.4), (-0.3, D / 2 + 0.02, H), 0.014, seg=6, mi=I['steel_charcoal'], rgba=DARK)
    return m.finish('proto_site_cabin', P)

def track_scale(F, P):
    """Flush rail weighbridge 4.2 x 2.4: steel deck set into the apron with a yellow frame and checker plate. The deck stays below the sleepers so the rail runs over it."""
    m = mb(F); L, W = 4.2, 2.4
    m.rbox(0, 0, -0.04, L, W, 0.1, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(0, 0, 0.0, L - 0.12, W - 0.12, 0.012, 0.003, mi=I['steel_brushed'], rgba=(0.6, 0.62, 0.64, 1))
    for k in range(int((L - 0.3) / 0.12)): m.rbox(-L / 2 + 0.2 + k * 0.12, 0, 0.008, 0.012, W - 0.2, 0.006, 0.001, mi=I['steel_charcoal'], rgba=DARK)
    for sy in (-1, 1): m.rbox(0, sy * (W / 2 - 0.03), 0.004, L, 0.06, 0.012, 0.002, mi=I['signage'], rgba=(0.92, 0.72, 0.06, 1))
    for sx in (-1, 1): m.rbox(sx * (L / 2 - 0.03), 0, 0.004, 0.06, W, 0.012, 0.002, mi=I['signage'], rgba=(0.92, 0.72, 0.06, 1))
    return m.finish('proto_track_scale', P)

def scale_post(F, P):
    """Weighbridge display on a post: pole, sloped cabinet with a screen, amber beacon, hand rail."""
    m = mb(F)
    m.cylz(0, 0, 0.0, 1.5, 0.05, seg=10, mi=I['steel_charcoal'], rgba=DARK); m.cylz(0, 0, 0.0, 0.02, 0.14, seg=14, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(0, 0.1, 1.5, 0.55, 0.22, 0.4, 0.03, rot=(-0.2, 0, 0), mi=I['paint'], rgba=(0.2, 0.22, 0.26, 1))
    m.rbox(0, 0.205, 1.52, 0.46, 0.012, 0.26, 0.004, rot=(-0.2, 0, 0), mi=I['screen'], rgba=(0.5, 0.9, 0.55, 1))
    m.add(p_cyl(0.07, 0.12, 14), (0, 0, 1.84), mi=I['emissive'], rgba=AMBER)
    return m.finish('proto_scale_post', P)

def skid_loader(F, P):
    """Compact skid-steer loader 3.0 m: orange body, ROPS cab with glass, lift arms and bucket, four tyres. Front toward +x."""
    m = mb(F); org = (0.9, 0.42, 0.06, 1)
    m.rbox(-0.15, 0, 0.62, 1.8, 1.45, 0.62, 0.08, mi=I['paint'], rgba=org)
    m.rbox(-0.75, 0, 1.12, 0.6, 1.3, 0.5, 0.08, mi=I['paint'], rgba=org)                                             # engine hood
    m.rbox(-0.1, 0, 0.95, 0.4, 1.0, 0.05, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    for sy in (-1, 1):
        for sx in (-1, 1): wheel(m, sx * 0.75 - 0.1, sy * 0.76, 0.34, r=0.34, w=0.28, flip=sy)
        m.between((0.45, sy * 0.46, 0.8), (0.45, sy * 0.46, 1.9), 0.04, seg=8, mi=I['steel_charcoal'], rgba=DARK)           # ROPS posts
        m.between((-0.35, sy * 0.46, 1.9), (0.45, sy * 0.46, 1.9), 0.04, seg=8, mi=I['steel_charcoal'], rgba=DARK)
        m.between((-0.35, sy * 0.46, 0.9), (-0.35, sy * 0.46, 1.9), 0.04, seg=8, mi=I['steel_charcoal'], rgba=DARK)
        m.rbox(0.05, sy * 0.46, 1.4, 0.7, 0.02, 0.8, 0.005, mi=I['glass'])
        m.between((0.2, sy * 0.58, 0.95), (1.25, sy * 0.58, 0.8), 0.06, seg=8, mi=I['paint'], rgba=org)                   # lift arms
    m.rbox(-0.2, 0, 1.95, 0.9, 1.0, 0.05, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(1.5, 0, 0.45, 0.5, 1.7, 0.4, 0.04, mi=I['steel_charcoal'], rgba=(0.14, 0.14, 0.15, 1)); m.rbox(1.62, 0, 0.62, 0.3, 1.7, 0.08, 0.02, mi=I['steel_charcoal'], rgba=(0.14, 0.14, 0.15, 1))
    for sy in (-0.8, -0.4, 0.4, 0.8): m.rbox(1.78, sy, 0.3, 0.1, 0.07, 0.1, 0.01, mi=I['steel_brushed'], rgba=STEEL)  # cutting teeth
    m.rbox(0.0, 0, 1.2, 0.3, 0.5, 0.45, 0.03, mi=I['fabric'], rgba=(0.15, 0.15, 0.17, 1))                              # seat
    m.add(p_cyl(0.06, 0.08, 12), (-0.65, 0.25, 1.65), mi=I['emissive'], rgba=AMBER)
    return m.finish('proto_skid_loader', P)

def fuel_station(F, P):
    """Bunded diesel station 4.6 x 3.0: concrete bund wall, two horizontal tanks on saddles with filler caps, vent pipes and gauges, and a pump with hose, nozzle holster and reel. Pump side toward +x."""
    m = mb(F); Lb, Wb = 4.6, 3.0
    for sy in (-1, 1): m.rbox(0, sy * (Wb / 2 - 0.1), 0.2, Lb, 0.2, 0.4, 0.02, mi=I['concrete_slab'], rgba=(0.6, 0.6, 0.58, 1))
    for sx in (-1, 1): m.rbox(sx * (Lb / 2 - 0.1), 0, 0.2, 0.2, Wb - 0.2, 0.4, 0.02, mi=I['concrete_slab'], rgba=(0.6, 0.6, 0.58, 1))
    m.rbox(0, 0, 0.02, Lb - 0.2, Wb - 0.2, 0.04, 0.01, mi=I['concrete_slab'], rgba=(0.5, 0.5, 0.48, 1))
    for k, y in enumerate((-0.75, 0.75)):
        for sx in (-0.9, 0.9): m.rbox(sx, y, 0.2, 0.2, 0.9, 0.4, 0.02, mi=I['steel_charcoal'], rgba=DARK)
        pb = p_lathe([(0.0, -1.3), (0.55, -1.3), (0.62, -1.15), (0.62, 1.15), (0.55, 1.3), (0.0, 1.3)], 28); xf(pb, (0, y, 0.95), (0, math.pi / 2, 0)); m.add(pb, mi=I['paint'], rgba=(0.82, 0.8, 0.74, 1) if k == 0 else (0.9, 0.55, 0.1, 1))
        m.cylz(-0.3, y, 1.54, 1.62, 0.16, seg=14, mi=I['steel_charcoal'], rgba=DARK); m.cylz(0.5, y, 1.54, 2.2, 0.03, seg=8, mi=I['steel_charcoal'], rgba=DARK)
        m.rbox(0.0, y - 0.05, 1.62, 0.2, 0.12, 0.2, 0.02, mi=I['plastic'], rgba=(0.82, 0.82, 0.8, 1))
        m.add(p_torus(0.62, 0.015, 30, 6), (-1.15, y, 0.95), (0, math.pi / 2, 0), mi=I['steel_charcoal'], rgba=DARK) if False else None
    px = Lb / 2 + 0.6
    m.rbox(px, 0, 0.04, 1.0, 1.0, 0.08, 0.02, mi=I['concrete_slab'], rgba=(0.6, 0.6, 0.58, 1))
    m.rbox(px, 0, 0.8, 0.5, 0.36, 1.5, 0.04, mi=I['paint'], rgba=(0.82, 0.12, 0.08, 1))
    m.rbox(px + 0.26, 0, 1.2, 0.02, 0.28, 0.2, 0.01, mi=I['screen'], rgba=(0.5, 0.9, 0.55, 1)); m.rbox(px + 0.26, 0, 0.9, 0.03, 0.2, 0.26, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(px, 0, 1.58, 0.56, 0.4, 0.06, 0.02, mi=I['steel_charcoal'], rgba=DARK)
    m.add(p_torus(0.2, 0.018, 24, 6), (px + 0.3, 0.18, 0.9), (math.pi / 2, 0, 0), mi=I['rubber'], rgba=(0.04, 0.04, 0.05, 1))
    m.between((px + 0.3, -0.12, 1.15), (px + 0.5, -0.12, 0.7), 0.025, seg=8, mi=I['steel_brushed'], rgba=STEEL)
    for sy in (-1, 1): m.cylz(px + 0.7, sy * 0.55, 0.0, 1.0, 0.09, seg=12, mi=I['steel_painted'] if 'steel_painted' in I else I['paint'], rgba=(0.95, 0.75, 0.05, 1))
    return m.finish('proto_fuel_station', P)

def bay_walls(F, P, w=3.2, d=3.4, h=1.8):
    """Push-wall ore bay: interlocking concrete blocks on three sides (open front toward +y), each wall with block joints and stud tops. Origin at the back centre."""
    m = mb(F); blk = (0.62, 0.6, 0.56, 1); t = 0.8
    def wall(cx, cy, sx, sy):
        m.rbox(cx, cy, h / 2, sx, sy, h, 0.02, mi=I['concrete_slab'], rgba=blk)
        n = int(max(sx, sy) / 1.6)
        for k in range(1, 3): m.rbox(cx, cy, k * h / 3, sx + 0.004, sy + 0.004, 0.012, 0.002, mi=I['steel_charcoal'], rgba=DARK)
        for k in range(n + 1):
            if sx > sy: m.rbox(cx - sx / 2 + k * sx / max(n, 1), cy, h / 2, 0.012, sy + 0.004, h, 0.002, mi=I['steel_charcoal'], rgba=DARK)
            else: m.rbox(cx, cy - sy / 2 + k * sy / max(n, 1), h / 2, sx + 0.004, 0.012, h, 0.002, mi=I['steel_charcoal'], rgba=DARK)
        for k in range(max(int(max(sx, sy) / 0.8), 2)):
            if sx > sy: m.cylz(cx - sx / 2 + 0.4 + k * 0.8, cy, h, h + 0.06, 0.13, seg=8, mi=I['concrete_slab'], rgba=blk)
            else: m.cylz(cx, cy - sy / 2 + 0.4 + k * 0.8, h, h + 0.06, 0.13, seg=8, mi=I['concrete_slab'], rgba=blk)
    wall(0, t / 2, w, t); wall(-w / 2 + t / 2, d / 2, t, d); wall(w / 2 - t / 2, d / 2, t, d)
    return m.finish('proto_bay_walls', P)

def rock_bolt(F, P):
    m = mb(F)
    m.rbox(0, 0.01, 0, 0.22, 0.02, 0.22, 0.004, mi=I['steel_charcoal'], rgba=(0.3, 0.3, 0.32, 1))
    m.add(p_cyl(0.045, 0.05, 6), (0, 0.04, 0), (math.pi / 2, 0, 0), mi=I['steel_charcoal'], rgba=(0.35, 0.34, 0.33, 1))
    m.between((0, 0.0, 0), (0, -0.3, 0), 0.012, seg=5, mi=I['steel_charcoal'], rgba=(0.25, 0.2, 0.15, 1))
    return m.finish('proto_rock_bolt', P)

def safety_mesh(F, P, w=2.4, h=1.6):
    """Rock-face safety mesh panel: welded diamond mesh in a bolted steel border (front toward +y)."""
    m = mb(F); steel = (0.22, 0.22, 0.24, 1)
    for z in (0.0, h): m.between((-w / 2, 0.01, z), (w / 2, 0.01, z), 0.02, seg=6, mi=I['steel_charcoal'], rgba=steel)
    for x in (-w / 2, w / 2): m.between((x, 0.01, 0), (x, 0.01, h), 0.02, seg=6, mi=I['steel_charcoal'], rgba=steel)
    n = int(w / 0.2)
    for k in range(n + 1):
        x = -w / 2 + k * w / n; m.between((x, 0.0, 0.0), (min(x + h * 0.5, w / 2), 0.0, h), 0.005, seg=4, mi=I['steel_charcoal'], rgba=steel)
        m.between((x, 0.0, 0.0), (max(x - h * 0.5, -w / 2), 0.0, h), 0.005, seg=4, mi=I['steel_charcoal'], rgba=steel)
    return m.finish('proto_safety_mesh', P)

def led_pole(F, P, h=6.2):
    """Yard floodlight pole: tapered steel pole on a base plate, two LED heads on a short arm, access hatch."""
    m = mb(F); steel = (0.18, 0.19, 0.21, 1)
    m.rbox(0, 0, 0.02, 0.4, 0.4, 0.04, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    m.lathe([(0.0, 0.0), (0.14, 0.0), (0.12, 0.15), (0.09, 1.0), (0.05, h), (0.0, h)], seg=14, mi=I['steel_charcoal'], rgba=steel)
    m.rbox(0.0, 0.1, 0.9, 0.16, 0.03, 0.4, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    m.between((0, 0, h - 0.2), (0.7, 0, h + 0.1), 0.03, seg=8, mi=I['steel_charcoal'], rgba=steel)
    for sy in (-0.25, 0.25):
        m.rbox(0.8, sy, h + 0.1, 0.5, 0.36, 0.08, 0.02, mi=I['steel_charcoal'], rgba=DARK)
        m.rbox(0.8, sy, h + 0.05, 0.44, 0.3, 0.02, 0.005, mi=I['emissive'], rgba=(1.0, 0.95, 0.85, 1))
    return m.finish('proto_led_pole', P)

def wheel_stop(F, P):
    m = mb(F)
    m.rbox(0, 0, 0.06, 1.6, 0.16, 0.12, 0.03, mi=I['concrete_slab'], rgba=(0.62, 0.6, 0.56, 1))
    for sx in (-0.65, 0.65): m.rbox(sx, 0, 0.125, 0.12, 0.17, 0.006, 0.002, mi=I['signage'], rgba=(0.92, 0.72, 0.06, 1))
    return m.finish('proto_wheel_stop', P)

def dock_platform(F, P, L=6.0, D=2.6, H=0.95):
    """Loading dock platform with kerb nosing, hazard edge, steps at one end, toe rail and tie-down eyes. Long edge toward +y."""
    m = mb(F)
    m.rbox(0, 0, H / 2, L, D, H, 0.02, mi=I['concrete_slab'], rgba=(0.62, 0.6, 0.56, 1))
    m.rbox(0, D / 2 - 0.12, H + 0.004, L, 0.24, 0.012, 0.002, mi=I['signage'], rgba=(0.92, 0.72, 0.06, 1))
    m.rbox(0, D / 2 + 0.03, H - 0.1, L, 0.08, 0.2, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    for k in range(3): m.rbox(-L / 2 - 0.3 - k * 0.0, -0.2 - k * 0.0, 0.25 + k * 0.2 - 0.12, 0.6, 1.0, 0.04, 0.01, mi=I['steel_brushed'], rgba=STEEL) if False else None
    for k in range(4): m.rbox(-L / 2 - 0.15 - (3 - k) * 0.3, -0.3, 0.2 + k * 0.22, 0.3, 1.1, 0.05, 0.008, mi=I['steel_brushed'], rgba=STEEL)
    for sy in (-0.85, 0.25):
        m.between((-L / 2 - 1.2, sy, 0.95), (-L / 2 - 0.1, sy, 1.0 + 0.0), 0.02, seg=6, mi=I['steel_charcoal'], rgba=DARK) if False else None
    for sx in (-0.4 * L, 0.4 * L): m.torus(sx, -D / 2 + 0.2, H + 0.02, 0.07, 0.014, ns=14, nt=6, mi=I['steel_charcoal'], rgba=DARK)
    return m.finish('proto_dock_platform', P)

def beacon_post(F, P, h=3.0):
    """Gate warning light: post with two amber heads and a lamp hood."""
    m = mb(F)
    m.cylz(0, 0, 0.0, h, 0.06, seg=10, mi=I['paint'], rgba=(0.95, 0.75, 0.05, 1)); m.cylz(0, 0, 0.0, 0.03, 0.16, seg=12, mi=I['steel_charcoal'], rgba=DARK)
    for sx in (-1, 1): m.add(p_cyl(0.09, 0.1, 14), (sx * 0.13, 0.0, h + 0.08), mi=I['emissive'], rgba=AMBER)
    m.rbox(0, 0, h - 0.4, 0.3, 0.12, 0.2, 0.02, mi=I['steel_charcoal'], rgba=DARK)
    return m.finish('proto_beacon_post', P)

def vent_fan(F, P):
    """Mine ventilation fan unit 2.4 m: cylindrical shroud with inlet bell, grille, motor, flanged outlet, steel cradle and electrical box. Axis along x, intake toward -x (cliff)."""
    m = mb(F); grey = (0.55, 0.58, 0.6, 1)
    pb = p_lathe([(0.0, -1.2), (0.95, -1.2), (1.0, -1.1), (1.0, 1.0), (0.9, 1.2), (0.0, 1.2)], 36); xf(pb, (0, 0, 1.15), (0, math.pi / 2, 0)); m.add(pb, mi=I['paint'], rgba=grey)
    pb2 = p_lathe([(0.0, -2.6), (0.88, -2.6), (0.88, -1.2), (0.0, -1.2)], 28); xf(pb2, (0, 0, 1.15), (0, math.pi / 2, 0)); m.add(pb2, mi=I['steel_brushed'], rgba=(0.6, 0.62, 0.64, 1))      # duct stub into the cliff
    m.add(p_torus(0.98, 0.04, 36, 8), (-1.2, 0, 1.15), (0, math.pi / 2, 0), mi=I['steel_brushed'], rgba=STEEL)
    m.add(p_torus(0.9, 0.05, 36, 8), (1.2, 0, 1.15), (0, math.pi / 2, 0), mi=I['steel_brushed'], rgba=STEEL)
    for k in range(7): m.between((-1.25, 0, 1.15 - 0.9 + k * 0.3), (-1.25, 0, 1.15 - 0.9 + k * 0.3), 0.001, seg=3, mi=I['steel_charcoal'], rgba=DARK) if False else None
    for k in range(6):
        a = k * math.pi / 3; m.between((-1.26, 0, 1.15), (-1.26, math.cos(a) * 0.95, 1.15 + math.sin(a) * 0.95), 0.012, seg=5, mi=I['steel_charcoal'], rgba=DARK)
    for r in (0.3, 0.6): m.add(p_torus(r, 0.01, 28, 5), (-1.26, 0, 1.15), (0, math.pi / 2, 0), mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(0.2, 0, 2.28, 0.8, 0.5, 0.3, 0.04, mi=I['paint'], rgba=(0.2, 0.3, 0.45, 1))                                  # motor housing on top
    for sx in (-0.8, 0.8):
        for sy in (-0.5, 0.5): m.rbox(sx, sy, 0.1, 0.1, 0.1, 0.2, 0.01, mi=I['steel_charcoal'], rgba=DARK)
        m.rbox(sx, 0, 0.18, 0.1, 1.2, 0.08, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(0.0, 0, 0.1, 2.4, 0.1, 0.08, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(-0.1, -1.05, 1.3, 0.5, 0.18, 0.7, 0.02, mi=I['paint'], rgba=(0.7, 0.72, 0.74, 1))
    m.rbox(-0.1, -1.15, 1.45, 0.3, 0.012, 0.18, 0.004, mi=I['screen'], rgba=(0.4, 0.8, 0.5, 1))
    return m.finish('proto_vent_fan', P)
