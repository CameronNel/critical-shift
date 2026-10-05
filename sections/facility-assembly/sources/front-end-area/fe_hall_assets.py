"""Hall props for an operations hub: PPE lockers, shift desk, workbench, tool wall, dispatch kit, safety station, blast-door console, ceiling fittings.
Every prop is a single multi-material mesh built at the origin, front toward +y, standing on z = 0 (wall items: back on y = 0). Lettering is never modelled here:
signs come from the baked atlas in fe_signs."""
from fe_kit import *
from fe_assets_int import STD, I, mb

STEEL = (0.72, 0.74, 0.76, 1); DARK = (0.08, 0.08, 0.09, 1)

def locker_bank(F, P, n=8, ajar=(2,), name='lockers'):
    """Bank of n steel PPE lockers 0.5 m wide. Open front (real cavity) with shelf, hanger rail, louvred door, handle; a few doors ajar showing a hard hat and hi-vis."""
    m = mb(F); w, d, h = 0.5, 0.5, 1.9; W = n * w; paint = (0.16, 0.26, 0.38, 1); inner = (0.1, 0.12, 0.15, 1)
    m.rbox(0, 0.0, 0.05, W, d - 0.02, 0.1, 0.01, mi=I['steel_charcoal'], rgba=DARK)                                  # plinth
    m.rbox(0, -d / 2 + 0.01, h / 2 + 0.1, W, 0.02, h, 0.004, mi=I['paint'], rgba=paint)                        # back
    m.rbox(0, 0, h + 0.1 - 0.01, W, d, 0.02, 0.006, mi=I['paint'], rgba=paint)                                # top
    m.rbox(0, 0.0, 0.11, W, d - 0.02, 0.02, 0.004, mi=I['paint'], rgba=inner)                                 # floor of lockers
    for k in range(n + 1):
        x = -W / 2 + k * w
        m.rbox(x, 0, h / 2 + 0.1, 0.02, d, h, 0.004, mi=I['paint'], rgba=paint)                               # partitions
    for k in range(n):
        x = -W / 2 + (k + 0.5) * w
        m.rbox(x, 0.0, 1.55, w - 0.03, d - 0.06, 0.012, 0.003, mi=I['paint'], rgba=inner)                      # shelf
        m.cylz(x - w / 2 + 0.03, 0.0, 0, 0, 0.001, seg=3, mi=I['steel_charcoal'], rgba=DARK) if False else None
        m.between((x - 0.2, 0.05, 1.45), (x + 0.2, 0.05, 1.45), 0.008, seg=6, mi=I['steel_brushed'], rgba=STEEL)       # hanger rail
        ang = 0.0
        if k in ajar: ang = 0.55 + 0.15 * (k % 2)
        hx = x - w / 2 + 0.015                                                                                         # hinge on the left edge
        cx = hx + (w - 0.03) / 2 * math.cos(ang); cy = d / 2 + (w - 0.03) / 2 * math.sin(ang)
        door = lambda dx, dy, dz, sx, sy, sz, mi, rgba, r=0.003: m.rbox(hx + dx * math.cos(ang) - dy * math.sin(ang), d / 2 + dx * math.sin(ang) + dy * math.cos(ang), dz, sx, sy, sz, r, rot=(0, 0, ang), mi=mi, rgba=rgba)
        door((w - 0.03) / 2, 0.0, h / 2 + 0.1, w - 0.03, 0.02, h - 0.02, I['paint'], paint, 0.004)           # leaf
        for j in range(5):
            door((w - 0.03) / 2, 0.012, 1.68 + j * 0.035, 0.28, 0.006, 0.012, I['steel_charcoal'], DARK, 0.002)       # louvres top
            door((w - 0.03) / 2, 0.012, 0.28 + j * 0.035, 0.28, 0.006, 0.012, I['steel_charcoal'], DARK, 0.002)       # louvres bottom
        door(w - 0.1, 0.018, 1.05, 0.02, 0.025, 0.14, I['steel_brushed'], STEEL, 0.006)                               # handle
        door((w - 0.03) / 2, 0.014, 1.82, 0.12, 0.004, 0.06, I['signage'], (0.9, 0.9, 0.86, 1), 0.001)                 # name tag holder
        if k in ajar:
            m.sphere(x, 0.0, 1.63, 0.1, 0.1, 0.07, rings=6, seg=10, mi=I['plastic'], rgba=(0.95, 0.75, 0.05, 1))       # hard hat on the shelf
            m.rbox(x, 0.0, 1.575, 0.2, 0.2, 0.012, 0.004, mi=I['plastic'], rgba=(0.95, 0.75, 0.05, 1))
            m.rbox(x, 0.08, 1.12, 0.3, 0.05, 0.62, 0.02, mi=I['fabric'], rgba=(0.92, 0.45, 0.05, 1))                    # hi-vis jacket on the rail
            m.rbox(x, 0.1, 1.12, 0.3, 0.012, 0.05, 0.003, mi=I['signage'], rgba=(0.85, 0.85, 0.8, 1))
    return m.finish('proto_' + name, P)

def locker_bench(F, P):
    """Changing-room bench: steel frame, timber slats, shoe shelf."""
    m = mb(F); L = 1.6
    for k in range(3): m.rbox(0, -0.12 + k * 0.12, 0.45, L, 0.1, 0.035, 0.008, mi=I['timber'], rgba=(0.5, 0.34, 0.18, 1))
    for sx in (-1, 1):
        m.rbox(sx * 0.7, 0, 0.22, 0.04, 0.34, 0.44, 0.006, mi=I['paint'], rgba=(0.16, 0.26, 0.38, 1))
        m.rbox(sx * 0.7, 0, 0.02, 0.06, 0.4, 0.04, 0.006, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(0, 0, 0.15, L - 0.1, 0.3, 0.02, 0.005, mi=I['paint'], rgba=(0.16, 0.26, 0.38, 1))
    return m.finish('proto_locker_bench', P)

def office_chair(F, P):
    m = mb(F); fab = (0.14, 0.17, 0.24, 1)
    for a in range(5):
        ang = a * 2 * math.pi / 5; ex, ey = math.cos(ang) * 0.28, math.sin(ang) * 0.28
        m.between((0, 0, 0.1), (ex, ey, 0.06), 0.017, seg=8, mi=I['steel_charcoal'], rgba=DARK)
        m.cylz(ex, ey, 0.0, 0.05, 0.028, seg=10, mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
    m.cylz(0, 0, 0.1, 0.46, 0.03, seg=12, mi=I['steel_brushed'], rgba=STEEL)
    m.cushion(0, 0, 0.5, 0.5, 0.48, 0.09, r=0.035, levels=1, mi=I['fabric'], rgba=fab)
    m.cushion(0, -0.22, 0.85, 0.46, 0.08, 0.5, r=0.035, levels=1, mi=I['fabric'], rgba=fab, rot=(-0.08, 0, 0))
    m.between((0, -0.06, 0.46), (0, -0.2, 0.6), 0.016, seg=8, mi=I['steel_charcoal'], rgba=DARK)
    for sx in (-1, 1):
        m.between((sx * 0.25, -0.1, 0.52), (sx * 0.25, 0.1, 0.52), 0.012, seg=6, mi=I['steel_charcoal'], rgba=DARK)
        m.between((sx * 0.25, -0.1, 0.52), (sx * 0.25, -0.1, 0.65), 0.012, seg=6, mi=I['steel_charcoal'], rgba=DARK)
        m.rbox(sx * 0.25, 0.0, 0.66, 0.05, 0.22, 0.03, 0.01, mi=I['plastic'], rgba=DARK)
    return m.finish('proto_office_chair', P)

def ops_desk(F, P):
    """Shift desk 3.2 m: laminate top, steel modesty panel and drawer pedestals, three monitors, keyboard, radio base, phone, lamp, paper trays, mug."""
    m = mb(F); L, D = 3.2, 0.9; top = 0.74; lam = (0.72, 0.68, 0.6, 1)
    m.rbox(0, 0.0, top, L, D, 0.04, 0.012, mi=I['laminate'], rgba=lam)
    m.rbox(0, 0.0, top - 0.025, L - 0.02, D - 0.02, 0.012, 0.004, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(0, -D / 2 + 0.05, 0.4, L - 0.2, 0.025, 0.62, 0.008, mi=I['steel_brushed'], rgba=(0.62, 0.64, 0.66, 1))        # modesty panel
    for sx in (-1, 1):
        m.rbox(sx * (L / 2 - 0.3), 0.0, 0.36, 0.5, D - 0.2, 0.72, 0.012, mi=I['paint'], rgba=(0.16, 0.26, 0.38, 1))
        for k in range(3):
            m.rbox(sx * (L / 2 - 0.3), D / 2 - 0.09, 0.12 + k * 0.22, 0.46, 0.02, 0.19, 0.005, mi=I['paint'], rgba=(0.2, 0.31, 0.44, 1))
            m.rbox(sx * (L / 2 - 0.3), D / 2 - 0.075, 0.12 + k * 0.22 + 0.06, 0.16, 0.014, 0.018, 0.004, mi=I['steel_brushed'], rgba=STEEL)
    for dx in (-0.85, 0.0, 0.85):
        m.rbox(dx, -0.2, 1.1, 0.56, 0.035, 0.34, 0.012, mi=I['plastic'], rgba=DARK)
        m.rbox(dx, -0.18, 1.1, 0.5, 0.006, 0.29, 0.004, mi=I['screen'], rgba=(0.2, 0.42, 0.55, 1) if dx else (0.25, 0.55, 0.4, 1))
        m.between((dx, -0.22, top + 0.02), (dx, -0.22, 0.93), 0.012, seg=8, mi=I['steel_charcoal'], rgba=DARK)
        m.rbox(dx, -0.22, top + 0.03, 0.18, 0.12, 0.012, 0.004, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(-0.3, 0.1, top + 0.03, 0.44, 0.15, 0.02, 0.006, mi=I['plastic'], rgba=(0.18, 0.18, 0.2, 1))                  # keyboard
    m.rbox(0.05, 0.12, top + 0.025, 0.06, 0.1, 0.03, 0.01, mi=I['plastic'], rgba=(0.18, 0.18, 0.2, 1))                    # mouse
    m.rbox(1.15, 0.1, top + 0.05, 0.26, 0.2, 0.06, 0.012, mi=I['plastic'], rgba=(0.22, 0.24, 0.26, 1))                    # radio base
    m.between((1.25, 0.15, top + 0.08), (1.27, 0.15, top + 0.4), 0.007, seg=6, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(-1.2, 0.05, top + 0.04, 0.22, 0.2, 0.07, 0.015, mi=I['plastic'], rgba=(0.82, 0.82, 0.8, 1))                    # phone
    m.rbox(-1.2, 0.13, top + 0.09, 0.14, 0.04, 0.02, 0.006, mi=I['plastic'], rgba=(0.3, 0.3, 0.32, 1))
    for k in range(2): m.rbox(-1.35 + k * 0.0, 0.3 - k * 0.0, top + 0.03 + k * 0.05, 0.3, 0.24, 0.035, 0.006, mi=I['plastic'], rgba=(0.2, 0.2, 0.22, 1)) if k == 0 else None
    for k in range(3): m.rbox(0.6, 0.25, top + 0.03 + k * 0.035, 0.3, 0.22, 0.03, 0.005, mi=I['plastic'], rgba=(0.2, 0.2, 0.22, 1)); m.rbox(0.6, 0.25, top + 0.04 + k * 0.035, 0.26, 0.18, 0.004, 0.001, mi=I['signage'], rgba=(0.9, 0.9, 0.86, 1))
    m.lathe([(0.0, 0.0), (0.04, 0.0), (0.04, 0.09), (0.0, 0.09)], loc=(-0.55, 0.3, top + 0.02), seg=14, mi=I['plastic'], rgba=(0.8, 0.8, 0.78, 1))
    m.between((1.0, -0.15, top + 0.02), (1.05, -0.1, top + 0.3), 0.006, seg=6, mi=I['steel_charcoal'], rgba=DARK); m.between((1.05, -0.1, top + 0.3), (0.95, 0.0, top + 0.42), 0.006, seg=6, mi=I['steel_charcoal'], rgba=DARK)
    m.cylz(0.95, 0.02, top + 0.4, top + 0.45, 0.05, seg=12, r2=0.025, mi=I['emissive'], rgba=(1.0, 0.9, 0.7, 1))             # lamp head
    return m.finish('proto_ops_desk', P)

def workbench(F, P):
    """Maintenance bench 1.8 m: butcher-block top, steel frame, drawer unit, lower shelf, vice, task lamp, power strip, parts tubs."""
    m = mb(F); L, D = 1.8, 0.7
    m.rbox(0, 0.0, 0.9, L, D, 0.06, 0.01, mi=I['timber'], rgba=(0.56, 0.4, 0.22, 1))
    for sx in (-1, 1):
        for sy in (-1, 1): m.rbox(sx * (L / 2 - 0.05), sy * (D / 2 - 0.05), 0.44, 0.06, 0.06, 0.88, 0.006, mi=I['paint'], rgba=(0.5, 0.1, 0.08, 1))
    m.rbox(0, -D / 2 + 0.05, 0.62, L - 0.1, 0.02, 0.5, 0.004, mi=I['paint'], rgba=(0.5, 0.1, 0.08, 1))
    m.rbox(0, 0, 0.2, L - 0.08, D - 0.1, 0.03, 0.006, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(L / 2 - 0.4, 0.0, 0.62, 0.62, D - 0.14, 0.4, 0.008, mi=I['paint'], rgba=(0.5, 0.1, 0.08, 1))
    for k in range(3):
        m.rbox(L / 2 - 0.4, D / 2 - 0.08, 0.48 + k * 0.13, 0.58, 0.02, 0.11, 0.004, mi=I['paint'], rgba=(0.58, 0.13, 0.1, 1)); m.rbox(L / 2 - 0.4, D / 2 - 0.065, 0.48 + k * 0.13, 0.2, 0.014, 0.016, 0.004, mi=I['steel_brushed'], rgba=STEEL)
    m.rbox(-0.55, 0.12, 0.99, 0.16, 0.14, 0.12, 0.012, mi=I['steel_charcoal'], rgba=(0.12, 0.2, 0.3, 1))                   # vice body
    m.rbox(-0.55, 0.2, 1.02, 0.12, 0.04, 0.06, 0.006, mi=I['steel_charcoal'], rgba=(0.12, 0.2, 0.3, 1))
    m.between((-0.55, 0.26, 1.0), (-0.55, 0.42, 1.0), 0.01, seg=8, mi=I['steel_brushed'], rgba=STEEL); m.between((-0.62, 0.42, 1.0), (-0.48, 0.42, 1.0), 0.008, seg=6, mi=I['steel_brushed'], rgba=STEEL)
    m.rbox(0.05, -0.28, 0.935, 0.5, 0.06, 0.03, 0.008, mi=I['steel_brushed'], rgba=(0.8, 0.8, 0.82, 1))                    # power strip
    for k in range(4): m.rbox(-0.1 + k * 0.1, -0.25, 0.953, 0.04, 0.012, 0.012, 0.003, mi=I['plastic'], rgba=DARK)
    for k in range(3): m.rbox(0.3 + k * 0.17, 0.05, 0.96, 0.15, 0.2, 0.08, 0.012, mi=I['plastic'], rgba=[(0.85, 0.5, 0.1, 1), (0.2, 0.4, 0.7, 1), (0.82, 0.82, 0.8, 1)][k])
    m.between((0.1, -0.28, 0.93), (0.1, -0.2, 1.3), 0.007, seg=6, mi=I['steel_charcoal'], rgba=DARK); m.between((0.1, -0.2, 1.3), (0.2, 0.0, 1.38), 0.007, seg=6, mi=I['steel_charcoal'], rgba=DARK)
    m.cylz(0.2, 0.02, 1.34, 1.4, 0.05, seg=12, r2=0.03, mi=I['emissive'], rgba=(1.0, 0.95, 0.8, 1))
    m.rbox(-0.15, 0.15, 0.935, 0.34, 0.16, 0.012, 0.004, mi=I['steel_charcoal'], rgba=(0.2, 0.2, 0.22, 1))                 # tool mat
    m.between((-0.28, 0.15, 0.95), (-0.02, 0.15, 0.95), 0.007, seg=6, mi=I['steel_brushed'], rgba=STEEL); m.between((-0.2, 0.2, 0.95), (-0.04, 0.1, 0.95), 0.006, seg=6, mi=I['steel_brushed'], rgba=STEEL)
    return m.finish('proto_workbench', P)

def tool_wall(F, P):
    """Pegboard tool wall 1.7 x 1.0 (back on y = 0): steel panel with hole grid, hooks, hammer, spanners, pliers, screwdrivers, tape, saw and shadow-board outlines."""
    m = mb(F); w, h = 1.7, 1.0; rnd = random.Random(12)
    m.rbox(0, 0.012, h / 2, w, 0.024, h, 0.006, mi=I['paint'], rgba=(0.2, 0.23, 0.26, 1))
    for r in range(8):
        for c in range(24): m.cylz(-w / 2 + 0.07 + c * 0.0705, 0.0245, 0.05 + r * 0.12, 0.05 + r * 0.12 + 0.002, 0.006, seg=6, mi=I['steel_charcoal'], rgba=(0.04, 0.04, 0.05, 1)) if (r + c) % 3 == 0 else None
    def outline(x, z, sx, sz): m.rbox(x, 0.0255, z, sx, 0.002, sz, 0.001, mi=I['signage'], rgba=(0.82, 0.8, 0.74, 1))
    # hammer
    outline(-0.68, 0.74, 0.1, 0.34); m.rbox(-0.68, 0.045, 0.7, 0.03, 0.02, 0.28, 0.006, mi=I['timber'], rgba=(0.55, 0.38, 0.2, 1)); m.rbox(-0.68, 0.045, 0.86, 0.1, 0.03, 0.04, 0.006, mi=I['steel_brushed'], rgba=STEEL)
    for k in range(5):                                                                                       # spanners, graded
        z = 0.84 - k * 0.0; x = -0.45 + k * 0.075; Ls = 0.34 - k * 0.03
        outline(x, 0.72, 0.045, Ls + 0.04); m.rbox(x, 0.04, 0.72, 0.026, 0.012, Ls, 0.004, mi=I['steel_brushed'], rgba=STEEL); m.cylz(x, 0.04, 0.72 + Ls / 2 - 0.01, 0.72 + Ls / 2 + 0.005, 0.025, seg=8, mi=I['steel_brushed'], rgba=STEEL)
    for k in range(4):                                                                                       # screwdrivers
        x = 0.1 + k * 0.07; outline(x, 0.72, 0.045, 0.3)
        m.cylz(x, 0.045, 0.7, 0.84, 0.012, seg=8, mi=I['plastic'], rgba=[(0.85, 0.5, 0.1, 1), (0.2, 0.4, 0.7, 1), (0.8, 0.12, 0.1, 1), (0.9, 0.8, 0.1, 1)][k]); m.cylz(x, 0.045, 0.58, 0.7, 0.004, seg=6, mi=I['steel_brushed'], rgba=STEEL)
    outline(0.62, 0.72, 0.16, 0.34)                                                                            # pliers
    for s in (-1, 1): m.between((0.62 + s * 0.02, 0.04, 0.78), (0.62 + s * 0.05, 0.04, 0.9), 0.012, seg=8, mi=I['plastic'], rgba=(0.8, 0.12, 0.1, 1)); m.between((0.62 + s * 0.02, 0.04, 0.78), (0.62 - s * 0.01, 0.04, 0.62), 0.008, seg=6, mi=I['steel_brushed'], rgba=STEEL)
    outline(-0.55, 0.3, 0.6, 0.2); m.rbox(-0.55, 0.04, 0.3, 0.52, 0.008, 0.07, 0.004, mi=I['steel_brushed'], rgba=STEEL)       # hand saw
    for k in range(7): m.rbox(-0.79 + k * 0.075, 0.042, 0.3, 0.008, 0.01, 0.07, 0.001, mi=I['steel_charcoal'], rgba=DARK) if False else None
    m.rbox(-0.55, 0.05, 0.22, 0.2, 0.025, 0.1, 0.012, mi=I['plastic'], rgba=(0.5, 0.35, 0.1, 1))
    outline(0.1, 0.28, 0.2, 0.2); m.cylz(0.1, 0.045, 0.2, 0.2 + 0.001, 0.0, seg=3, mi=I['plastic'], rgba=DARK) if False else None
    m.add(p_cyl(0.075, 0.03, 20), (0.1, 0.05, 0.28), (math.pi / 2, 0, 0), mi=I['plastic'], rgba=(0.9, 0.78, 0.1, 1))     # tape measure
    m.add(p_cyl(0.03, 0.032, 14), (0.1, 0.05, 0.28), (math.pi / 2, 0, 0), mi=I['steel_charcoal'], rgba=DARK)
    outline(0.52, 0.27, 0.26, 0.2)
    for k in range(3): m.cylz(0.46 + k * 0.06, 0.05, 0.2, 0.34, 0.016, seg=8, mi=I['plastic'], rgba=[(0.8, 0.12, 0.1, 1), (0.2, 0.4, 0.7, 1), (0.9, 0.8, 0.1, 1)][k])           # spray cans
    return m.finish('proto_tool_wall', P)

def tool_chest(F, P):
    m = mb(F); red = (0.62, 0.1, 0.08, 1)
    m.rbox(0, 0.0, 0.5, 0.68, 0.46, 0.84, 0.015, mi=I['paint'], rgba=red)
    m.rbox(0, 0.0, 0.94, 0.7, 0.48, 0.04, 0.012, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    for k in range(5):
        m.rbox(0, 0.236, 0.16 + k * 0.145, 0.62, 0.012, 0.125, 0.004, mi=I['paint'], rgba=tuple(c * 1.12 for c in red[:3]) + (1,))
        m.rbox(0, 0.248, 0.16 + k * 0.145 + 0.03, 0.5, 0.014, 0.014, 0.005, mi=I['steel_brushed'], rgba=STEEL)
    for sx in (-1, 1):
        for sy in (-1, 1): m.cylz(sx * 0.28, sy * 0.18, 0.0, 0.09, 0.03, seg=10, mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
    m.rbox(0, 0, 0.1, 0.62, 0.4, 0.02, 0.004, mi=I['steel_charcoal'], rgba=DARK)
    return m.finish('proto_tool_chest', P)

def bin_shelf(F, P):
    """Steel parts shelving 1.2 x 0.45 x 1.9 with labelled colour tubs."""
    m = mb(F); rnd = random.Random(5); blue = (0.16, 0.26, 0.38, 1)
    for sx in (-1, 1):
        for sy in (-1, 1): m.rbox(sx * 0.58, sy * 0.2, 0.95, 0.04, 0.04, 1.9, 0.004, mi=I['paint'], rgba=blue)
    for k in range(5): m.rbox(0, 0, 0.1 + k * 0.45, 1.2, 0.44, 0.025, 0.004, mi=I['paint'], rgba=blue)
    cols = [(0.82, 0.45, 0.1, 1), (0.2, 0.4, 0.7, 1), (0.8, 0.8, 0.78, 1), (0.8, 0.14, 0.12, 1), (0.25, 0.55, 0.3, 1)]
    for k in range(4):
        for j in range(4):
            c = cols[rnd.randrange(5)]; z = 0.125 + k * 0.45
            if rnd.random() < 0.15: continue
            m.rbox(-0.43 + j * 0.287, 0.02, z + 0.1, 0.26, 0.36, 0.2, 0.02, mi=I['plastic'], rgba=c)
            m.rbox(-0.43 + j * 0.287, 0.205, z + 0.12, 0.14, 0.006, 0.06, 0.002, mi=I['signage'], rgba=(0.92, 0.92, 0.88, 1))
    m.rbox(0, 0.0, 1.9 + 0.012, 1.2, 0.44, 0.025, 0.004, mi=I['paint'], rgba=blue)
    m.rbox(0, 0.0, 1.97, 0.6, 0.3, 0.12, 0.01, mi=I['plastic'], rgba=(0.8, 0.8, 0.78, 1))
    return m.finish('proto_bin_shelf', P)

def pallet_jack(F, P):
    m = mb(F); red = (0.7, 0.1, 0.08, 1)
    for sy in (-1, 1):
        m.rbox(0.3, sy * 0.28, 0.07, 1.0, 0.16, 0.06, 0.012, mi=I['paint'], rgba=red); m.rbox(0.82, sy * 0.28, 0.06, 0.12, 0.14, 0.04, 0.02, mi=I['paint'], rgba=red)
        m.cylz(0.78, sy * 0.28, 0.0, 0.0, 0.0, seg=3, mi=I['rubber'], rgba=DARK) if False else None
        m.add(p_cyl(0.04, 0.07, 14), (0.78, sy * 0.28, 0.04), (math.pi / 2, 0, 0), mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
    m.rbox(-0.2, 0.0, 0.14, 0.2, 0.62, 0.2, 0.02, mi=I['paint'], rgba=red)
    m.rbox(-0.3, 0.0, 0.17, 0.1, 0.5, 0.12, 0.02, mi=I['steel_charcoal'], rgba=DARK)
    m.between((-0.25, 0, 0.2), (-0.62, 0, 1.15), 0.02, seg=10, mi=I['steel_brushed'], rgba=STEEL)
    m.rbox(-0.64, 0.0, 1.17, 0.05, 0.4, 0.05, 0.02, mi=I['plastic'], rgba=(0.08, 0.08, 0.1, 1))
    for sy in (-1, 1): m.add(p_cyl(0.05, 0.05, 14), (-0.2, sy * 0.2, 0.05), (math.pi / 2, 0, 0), mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
    return m.finish('proto_pallet_jack', P)

def parcel_stack(F, P, seed=0, layers=3):
    """Palletised cardboard cartons (pallet included), taped, labelled, stretch-wrapped with a clear film shell."""
    m = mb(F); rnd = random.Random(seed); card = (0.58, 0.44, 0.28, 1)
    for x in (-0.5, 0.0, 0.5): m.rbox(x, 0, 0.075, 0.1, 1.0, 0.09, 0.006, mi=I['timber'], rgba=(0.55, 0.38, 0.2, 1))
    for i in range(7): m.rbox(0, -0.46 + i * 0.153, 0.16, 1.2, 0.1, 0.022, 0.004, mi=I['timber'], rgba=(0.55, 0.38, 0.2, 1))
    for y in (-0.45, 0.0, 0.45): m.rbox(0, y, 0.012, 1.2, 0.1, 0.022, 0.004, mi=I['timber'], rgba=(0.55, 0.38, 0.2, 1))
    z = 0.17
    for L in range(layers):
        h = 0.34 if L % 2 == 0 else 0.3
        for ix in (-0.3, 0.3):
            for iy in (-0.23, 0.23):
                tone = rnd.uniform(0.9, 1.08); c = tuple(v * tone for v in card[:3]) + (1,)
                m.rbox(ix, iy, z + h / 2, 0.57, 0.45, h - 0.01, 0.01, mi=I['props'], rgba=c)
                m.rbox(ix, iy, z + h, 0.57, 0.08, 0.004, 0.001, mi=I['signage'], rgba=(0.72, 0.58, 0.36, 1))
        for ix in (-0.3, 0.3): m.rbox(ix, 0.475, z + h * 0.6, 0.2, 0.004, 0.12, 0.001, mi=I['signage'], rgba=(0.92, 0.92, 0.88, 1))
        z += h
    m.rbox(0, 0, 0.17 + (z - 0.17) / 2, 1.2, 0.98, z - 0.17, 0.02, mi=I['glass'])
    return m.finish(f'proto_parcels_{seed}', P)

def roll_cage(F, P):
    """Wire roll cage on casters with a drop-gate, half full of parcels."""
    m = mb(F); w, d, h = 0.8, 0.7, 1.7; rnd = random.Random(3)
    m.rbox(0, 0, 0.17, w, d, 0.03, 0.006, mi=I['steel_brushed'], rgba=STEEL)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.cylz(sx * (w / 2 - 0.04), sy * (d / 2 - 0.04), 0.0, 0.12, 0.03, seg=10, mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
            m.cylz(sx * (w / 2 - 0.01), sy * (d / 2 - 0.01), 0.17, h, 0.012, seg=8, mi=I['steel_brushed'], rgba=STEEL)
    for z in (0.5, 0.85, 1.2, h):
        for sx in (-1, 1): m.between((sx * (w / 2 - 0.01), -d / 2, z), (sx * (w / 2 - 0.01), d / 2, z), 0.006, seg=6, mi=I['steel_brushed'], rgba=STEEL)
        m.between((-w / 2, -d / 2 + 0.01, z), (w / 2, -d / 2 + 0.01, z), 0.006, seg=6, mi=I['steel_brushed'], rgba=STEEL)
    for k in range(10):
        for sx in (-1, 1): m.between((sx * (w / 2 - 0.01), -d / 2 + k * d / 9, 0.17), (sx * (w / 2 - 0.01), -d / 2 + k * d / 9, h), 0.004, seg=5, mi=I['steel_brushed'], rgba=STEEL)
    for k in range(8): m.between((-w / 2 + k * w / 7, -d / 2 + 0.01, 0.17), (-w / 2 + k * w / 7, -d / 2 + 0.01, h), 0.004, seg=5, mi=I['steel_brushed'], rgba=STEEL)
    for L in range(3):
        for ix in (-0.19, 0.19):
            m.rbox(ix, 0.0, 0.34 + L * 0.3, 0.36, 0.5, 0.28, 0.01, mi=I['props'], rgba=tuple(v * rnd.uniform(0.9, 1.08) for v in (0.58, 0.44, 0.28)) + (1,))
    m.rbox(0, d / 2 - 0.01, 0.55, w - 0.04, 0.012, 0.7, 0.004, mi=I['steel_charcoal'], rgba=DARK) if False else None
    for k in range(9): m.between((-w / 2 + 0.02, d / 2 - 0.005, 0.2 + k * 0.045), (w / 2 - 0.02, d / 2 - 0.005, 0.2 + k * 0.045), 0.004, seg=5, mi=I['steel_brushed'], rgba=STEEL)   # lowered front gate
    return m.finish('proto_roll_cage', P)

def staging_shelf(F, P):
    """Dispatch shelving 1.8 m: uprights, beams, labelled boxes and a hand scanner dock."""
    m = mb(F); rnd = random.Random(14); orange = (0.8, 0.38, 0.05, 1)
    for sx in (-1, 1):
        for sy in (-1, 1): m.rbox(sx * 0.88, sy * 0.28, 1.1, 0.06, 0.05, 2.2, 0.005, mi=I['paint'], rgba=(0.16, 0.26, 0.38, 1))
    for k in range(4):
        for sy in (-1, 1): m.rbox(0, sy * 0.28, 0.4 + k * 0.55, 1.76, 0.05, 0.08, 0.005, mi=I['paint'], rgba=orange)
        m.rbox(0, 0, 0.44 + k * 0.55, 1.74, 0.6, 0.018, 0.003, mi=I['timber'], rgba=(0.5, 0.36, 0.2, 1))
    for k in range(3):
        x = -0.6
        while x < 0.7:
            wd = rnd.uniform(0.28, 0.5)
            if x + wd > 0.82: break
            ht = rnd.uniform(0.22, 0.4)
            m.rbox(x + wd / 2, 0.0, 0.453 + k * 0.55 + ht / 2, wd - 0.02, 0.46, ht, 0.008, mi=I['props'], rgba=tuple(v * rnd.uniform(0.9, 1.08) for v in (0.58, 0.44, 0.28)) + (1,))
            m.rbox(x + wd / 2, 0.232, 0.453 + k * 0.55 + ht * 0.6, wd * 0.5, 0.004, 0.07, 0.001, mi=I['signage'], rgba=(0.92, 0.92, 0.88, 1))
            x += wd + 0.02
    return m.finish('proto_staging_shelf', P)

def bollard_hall(F, P):
    m = mb(F)
    m.lathe([(0.0, 0.0), (0.13, 0.0), (0.13, 0.03), (0.1, 0.05), (0.095, 0.95), (0.1, 0.97), (0.08, 1.05), (0.0, 1.07)], seg=24, mi=I['paint'], rgba=(0.95, 0.75, 0.05, 1))
    for z in (0.35, 0.65): m.cylz(0, 0, z, z + 0.08, 0.1, seg=24, mi=I['steel_charcoal'], rgba=DARK)
    m.cylz(0, 0, 0.0, 0.015, 0.16, seg=24, mi=I['steel_charcoal'], rgba=DARK)
    return m.finish('proto_bollard_hall', P)

def blast_console(F, P):
    """Blast-door control post, wall mounted (back on y = 0): key switch, red mushroom e-stop, status lamps, card reader, keypad, recessed display."""
    m = mb(F); w, h = 0.5, 0.8
    m.rbox(0, 0.06, h / 2, w, 0.12, h, 0.02, mi=I['paint'], rgba=(0.2, 0.22, 0.26, 1))
    m.rbox(0, 0.122, 0.62, 0.38, 0.012, 0.24, 0.006, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(0, 0.13, 0.62, 0.34, 0.005, 0.2, 0.003, mi=I['screen'], rgba=(0.25, 0.55, 0.45, 1))
    for k, c in enumerate(((0.9, 0.2, 0.15, 1), (0.95, 0.65, 0.1, 1), (0.2, 0.85, 0.35, 1))): m.cylz(-0.12 + k * 0.12, 0.13, 0.0, 0.0, 0.0, seg=3, mi=I['emissive'], rgba=c) if False else m.add(p_cyl(0.022, 0.016, 12), (-0.12 + k * 0.12, 0.128, 0.46), (math.pi / 2, 0, 0), mi=I['emissive'], rgba=c)
    m.rbox(-0.11, 0.126, 0.3, 0.14, 0.01, 0.1, 0.004, mi=I['steel_charcoal'], rgba=(0.05, 0.05, 0.06, 1))
    for r in range(3):
        for c in range(3): m.rbox(0.06 + c * 0.04, 0.128, 0.34 - r * 0.04, 0.03, 0.008, 0.03, 0.003, mi=I['steel_brushed'], rgba=STEEL)
    m.add(p_cyl(0.05, 0.02, 18), (0.12, 0.135, 0.15), (math.pi / 2, 0, 0), mi=I['plastic'], rgba=(0.78, 0.08, 0.06, 1))
    m.add(p_cyl(0.075, 0.012, 18), (0.12, 0.128, 0.15), (math.pi / 2, 0, 0), mi=I['plastic'], rgba=(0.95, 0.75, 0.05, 1))
    m.add(p_cyl(0.028, 0.02, 14), (-0.12, 0.134, 0.15), (math.pi / 2, 0, 0), mi=I['steel_brushed'], rgba=STEEL); m.rbox(-0.12, 0.146, 0.15, 0.012, 0.012, 0.05, 0.003, mi=I['steel_charcoal'], rgba=DARK)
    return m.finish('proto_blast_console', P)

def ppe_dispenser(F, P):
    """Wall PPE station 1.3 x 0.9: four clear-fronted bays (hard hats, glasses, gloves, ear defenders) with colour stock."""
    m = mb(F); w, h = 1.3, 0.9
    m.rbox(0, 0.07, h / 2, w, 0.14, h, 0.015, mi=I['paint'], rgba=(0.16, 0.26, 0.38, 1))
    for k in range(4):
        x = -0.48 + k * 0.32
        m.rbox(x, 0.135, h / 2, 0.28, 0.012, h - 0.12, 0.006, mi=I['glass'])
        m.rbox(x, 0.1, h / 2, 0.26, 0.02, h - 0.16, 0.004, mi=I['steel_charcoal'], rgba=(0.06, 0.06, 0.07, 1))
    for k in range(3): m.sphere(-0.48, 0.1, 0.2 + k * 0.22, 0.1, 0.1, 0.07, rings=6, seg=10, mi=I['plastic'], rgba=(0.95, 0.75, 0.05, 1))
    for k in range(4): m.rbox(-0.16, 0.1, 0.18 + k * 0.17, 0.2, 0.04, 0.04, 0.012, mi=I['plastic'], rgba=(0.8, 0.9, 0.95, 1))
    for k in range(4): m.rbox(0.16, 0.1, 0.18 + k * 0.17, 0.16, 0.04, 0.12, 0.012, mi=I['fabric'], rgba=(0.85, 0.5, 0.1, 1))
    for k in range(3): m.rbox(0.48, 0.1, 0.2 + k * 0.22, 0.2, 0.06, 0.14, 0.03, mi=I['plastic'], rgba=(0.9, 0.35, 0.05, 1))
    m.rbox(0, 0.15, h + 0.02, w + 0.04, 0.2, 0.04, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    return m.finish('proto_ppe_dispenser', P)

def key_cabinet(F, P):
    m = mb(F)
    m.rbox(0, 0.06, 0.4, 0.5, 0.12, 0.8, 0.012, mi=I['paint'], rgba=(0.55, 0.1, 0.08, 1))
    m.rbox(0, 0.124, 0.4, 0.42, 0.012, 0.72, 0.004, mi=I['glass'])
    for r in range(4):
        for c in range(5): m.rbox(-0.17 + c * 0.085, 0.1, 0.12 + r * 0.17, 0.03, 0.02, 0.07, 0.006, mi=I['plastic'], rgba=[(0.9, 0.75, 0.1, 1), (0.8, 0.12, 0.1, 1), (0.2, 0.45, 0.75, 1), (0.82, 0.82, 0.8, 1)][(r + c) % 4]) if (r * 5 + c) % 7 else None
    m.rbox(0.2, 0.135, 0.4, 0.03, 0.012, 0.04, 0.004, mi=I['steel_brushed'], rgba=STEEL)
    return m.finish('proto_key_cabinet', P)

def radio_dock(F, P):
    """Wall shelf with eight radio chargers, status LEDs, and a handheld in each cradle."""
    m = mb(F)
    m.rbox(0, 0.1, 0.1, 1.2, 0.2, 0.05, 0.008, mi=I['paint'], rgba=(0.16, 0.26, 0.38, 1))
    m.rbox(0, 0.01, 0.35, 1.2, 0.02, 0.5, 0.006, mi=I['paint'], rgba=(0.16, 0.26, 0.38, 1))
    for k in range(8):
        x = -0.52 + k * 0.148
        m.rbox(x, 0.085, 0.16, 0.12, 0.13, 0.07, 0.012, mi=I['plastic'], rgba=(0.2, 0.2, 0.22, 1))
        m.rbox(x, 0.085, 0.31, 0.07, 0.04, 0.2, 0.012, mi=I['plastic'], rgba=(0.1, 0.1, 0.12, 1))
        m.between((x + 0.02, 0.085, 0.4), (x + 0.025, 0.085, 0.52), 0.006, seg=6, mi=I['steel_charcoal'], rgba=DARK)
        m.add(p_cyl(0.007, 0.012, 8), (x, 0.145, 0.164), (math.pi / 2, 0, 0), mi=I['emissive'], rgba=(0.2, 0.9, 0.3, 1) if k != 5 else (0.95, 0.65, 0.1, 1))
    return m.finish('proto_radio_dock', P)

def safety_station(F, P):
    """Wall-mounted emergency station 2.6 m wide (back on y = 0): green backboard with eyewash bowl and pull handle, first aid cabinet, AED, extinguisher on bracket, spill kit bin."""
    m = mb(F); green = (0.1, 0.5, 0.25, 1); W = 2.6
    m.rbox(0, 0.01, 1.1, W, 0.02, 1.7, 0.01, mi=I['paint'], rgba=green)
    m.rbox(0, 0.012, 1.98, W, 0.03, 0.06, 0.006, mi=I['signage'], rgba=(0.9, 0.9, 0.86, 1))
    # eyewash: bowl, pipe, flaps, handle
    m.rbox(-0.9, 0.12, 0.98, 0.5, 0.14, 0.05, 0.012, mi=I['steel_brushed'], rgba=STEEL)
    m.lathe([(0.0, 0.0), (0.2, 0.0), (0.22, 0.05), (0.16, 0.08), (0.0, 0.08)], loc=(-0.9, 0.2, 0.93), seg=20, mi=I['steel_brushed'], rgba=STEEL)
    m.between((-0.9, 0.04, 0.95), (-0.9, 0.08, 1.2), 0.016, seg=8, mi=I['steel_brushed'], rgba=STEEL)
    for sx in (-0.07, 0.07): m.cylz(-0.9 + sx, 0.1, 1.2, 1.26, 0.03, seg=10, mi=I['plastic'], rgba=(0.9, 0.2, 0.15, 1))
    m.rbox(-0.9, 0.05, 1.1, 0.06, 0.05, 0.26, 0.008, mi=I['plastic'], rgba=(0.95, 0.75, 0.05, 1))
    # first aid cabinet
    m.rbox(-0.2, 0.09, 1.45, 0.55, 0.18, 0.62, 0.015, mi=I['plastic'], rgba=(0.92, 0.92, 0.9, 1))
    m.rbox(-0.2, 0.182, 1.45, 0.5, 0.008, 0.56, 0.004, mi=I['plastic'], rgba=(0.96, 0.96, 0.94, 1))
    m.rbox(-0.2, 0.188, 1.45, 0.06, 0.006, 0.28, 0.002, mi=I['signage'], rgba=(0.1, 0.55, 0.3, 1)); m.rbox(-0.2, 0.188, 1.45, 0.28, 0.006, 0.06, 0.002, mi=I['signage'], rgba=(0.1, 0.55, 0.3, 1))
    m.rbox(0.03, 0.188, 1.45, 0.02, 0.012, 0.06, 0.004, mi=I['plastic'], rgba=(0.3, 0.3, 0.32, 1))
    # AED
    m.rbox(0.55, 0.08, 1.4, 0.4, 0.16, 0.42, 0.02, mi=I['plastic'], rgba=(0.9, 0.5, 0.1, 1))
    m.rbox(0.55, 0.162, 1.42, 0.3, 0.01, 0.28, 0.01, mi=I['plastic'], rgba=(0.85, 0.85, 0.82, 1))
    m.sphere(0.55, 0.172, 1.45, 0.07, 0.01, 0.07, rings=6, seg=10, mi=I['signage'], rgba=(0.8, 0.1, 0.1, 1))
    m.rbox(0.55, 0.172, 1.26, 0.2, 0.008, 0.02, 0.003, mi=I['emissive'], rgba=(0.2, 0.9, 0.3, 1))
    # extinguisher on bracket
    m.lathe([(0.0, 0.0), (0.06, 0.0), (0.075, 0.03), (0.08, 0.1), (0.08, 0.4), (0.07, 0.48), (0.04, 0.52), (0.0, 0.52)], loc=(1.05, 0.12, 0.75), seg=28, mi=I['plastic'], rgba=(0.7, 0.07, 0.05, 1))
    m.cylz(1.05, 0.12, 1.27, 1.34, 0.022, seg=12, mi=I['steel_charcoal'], rgba=DARK); m.rbox(1.08, 0.12, 1.36, 0.1, 0.03, 0.03, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(1.05, 0.04, 1.1, 0.2, 0.05, 0.04, 0.008, mi=I['steel_charcoal'], rgba=DARK); m.rbox(1.05, 0.1, 1.0, 0.18, 0.12, 0.016, 0.005, mi=I['steel_charcoal'], rgba=DARK) if False else None
    m.rbox(1.05, 0.12, 1.02, 0.18, 0.02, 0.05, 0.005, mi=I['signage'], rgba=(0.95, 0.85, 0.15, 1))
    # spill kit bin
    m.rbox(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0) if False else None
    m.rbox(0.45, 0.14, 0.2, 0.42, 0.26, 0.4, 0.03, mi=I['plastic'], rgba=(0.95, 0.75, 0.05, 1))
    m.rbox(0.45, 0.14, 0.42, 0.46, 0.3, 0.04, 0.012, mi=I['plastic'], rgba=(0.12, 0.12, 0.13, 1))
    m.rbox(0.45, 0.275, 0.2, 0.2, 0.01, 0.1, 0.002, mi=I['signage'], rgba=(0.85, 0.12, 0.1, 1))
    return m.finish('proto_safety_station', P)

def hose_cabinet(F, P):
    """Fire hose cabinet: red box, glazed door, hose reel with nozzle."""
    m = mb(F)
    m.rbox(0, 0.1, 0.55, 0.8, 0.2, 1.1, 0.02, mi=I['paint'], rgba=(0.7, 0.07, 0.05, 1))
    m.rbox(0, 0.203, 0.55, 0.7, 0.01, 1.0, 0.004, mi=I['glass'])
    m.rbox(0, 0.185, 0.55, 0.66, 0.012, 0.96, 0.004, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    m.add(p_cyl(0.28, 0.1, 28), (0, 0.12, 0.6), (math.pi / 2, 0, 0), mi=I['plastic'], rgba=(0.7, 0.62, 0.55, 1))
    m.add(p_cyl(0.22, 0.12, 28), (0, 0.12, 0.6), (math.pi / 2, 0, 0), mi=I['rubber'], rgba=(0.08, 0.3, 0.16, 1))
    m.add(p_cyl(0.05, 0.14, 12), (0, 0.12, 0.6), (math.pi / 2, 0, 0), mi=I['steel_brushed'], rgba=STEEL)
    m.between((0.2, 0.12, 0.9), (0.3, 0.12, 0.35), 0.012, seg=8, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(0.28, 0.2, 0.62, 0.03, 0.012, 0.16, 0.004, mi=I['steel_brushed'], rgba=STEEL)
    return m.finish('proto_hose_cabinet', P)

def cctv_dome(F, P):
    m = mb(F)
    m.cylz(0, 0, 0.0, 0.04, 0.07, seg=14, mi=I['steel_charcoal'], rgba=DARK)
    m.sphere(0, 0, -0.01, 0.075, 0.075, 0.07, rings=7, seg=14, mi=I['glass'])
    m.sphere(0, 0.01, -0.03, 0.03, 0.03, 0.025, rings=5, seg=8, mi=I['steel_charcoal'], rgba=(0.02, 0.02, 0.03, 1))
    return m.finish('proto_cctv_dome', P)

def ceiling_fitting(F, P, kind):
    """kind: 'smoke' (detector), 'horn' (PA speaker), 'sprinkler'."""
    m = mb(F)
    if kind == 'smoke':
        m.cylz(0, 0, -0.04, 0.0, 0.055, seg=16, mi=I['plastic'], rgba=(0.9, 0.9, 0.88, 1)); m.cylz(0, 0, -0.05, -0.04, 0.03, seg=12, mi=I['plastic'], rgba=(0.85, 0.85, 0.82, 1)); m.add(p_cyl(0.004, 0.008, 6), (0.035, 0, -0.04), mi=I['emissive'], rgba=(0.9, 0.2, 0.15, 1))
    elif kind == 'horn':
        m.lathe([(0.0, 0.0), (0.04, 0.0), (0.1, -0.12), (0.0, -0.12)], seg=16, mi=I['steel_charcoal'], rgba=(0.82, 0.82, 0.8, 1))
        m.cylz(0, 0, 0.0, 0.1, 0.012, seg=8, mi=I['steel_charcoal'], rgba=DARK)
    else:
        m.cylz(0, 0, -0.03, 0.0, 0.016, seg=10, mi=I['steel_brushed'], rgba=(0.8, 0.12, 0.1, 1)); m.cylz(0, 0, -0.045, -0.03, 0.03, seg=12, r2=0.008, mi=I['steel_brushed'], rgba=STEEL)
        m.add(p_sphere(0.012, rings=4, seg=8), (0, 0, -0.02), mi=I['glass'])
    return m.finish('proto_ceiling_' + kind, P)

def wet_cart(F, P):
    """Cleaner's cart: yellow bucket and wringer, bin bag, mop and brush, spray bottles, caution plate on the cart."""
    m = mb(F); y = (0.95, 0.78, 0.08, 1)
    m.rbox(0, 0.0, 0.3, 0.7, 0.45, 0.05, 0.012, mi=I['plastic'], rgba=(0.2, 0.2, 0.22, 1))
    m.rbox(-0.3, 0.0, 0.62, 0.05, 0.43, 0.66, 0.012, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(0.0, -0.2, 0.28, 0.6, 0.02, 0.5, 0.01, mi=I['plastic'], rgba=(0.2, 0.2, 0.22, 1)) if False else None
    for sx in (-1, 1):
        for sy in (-1, 1): m.cylz(sx * 0.3, sy * 0.19, 0.0, 0.055, 0.04, seg=10, mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
    m.rbox(0.12, 0.0, 0.5, 0.34, 0.34, 0.3, 0.03, mi=I['plastic'], rgba=y)
    m.rbox(0.12, 0.0, 0.66, 0.26, 0.26, 0.012, 0.004, mi=I['plastic'], rgba=(0.1, 0.1, 0.12, 1))
    m.between((-0.28, 0.1, 0.9), (0.02, 0.0, 0.32), 0.012, seg=8, mi=I['timber'], rgba=(0.55, 0.38, 0.2, 1))
    m.rbox(0.0, 0.0, 0.3, 0.1, 0.1, 0.1, 0.03, mi=I['fabric'], rgba=(0.8, 0.8, 0.78, 1))
    m.rbox(-0.3, -0.18, 1.0, 0.3, 0.2, 0.5, 0.05, mi=I['plastic'], rgba=(0.12, 0.12, 0.14, 1))
    return m.finish('proto_wet_cart', P)
