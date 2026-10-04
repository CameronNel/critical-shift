"""Hall refit: the hall is mid-refit, so the free width is reduced by site kit, barriers, scaffolds and one modest cordoned ceiling collapse.
Clear lanes stay on the cafeteria-spine axis (x 6.8..9.2) and the west-east door line (y -55.3..-52.7)."""
from fe_kit import *
from fe_assets_site import *
from fe_assets_yard import crate, pallet, cable_drum, pipe_stack
from fe_assets_int import stanchion
from fe_yard import inst

def build_hall_site(F, C, P):
    hall = C['HALL']; rnd = random.Random(909)
    jer = jersey(F, P); sb = [sandbags(F, P, s) for s in range(2)]; sc = scaffold(F, P); pbd = plasterboard(F, P); lad = ladder(F, P); bk = bucket(F, P)
    cb = [cement_bags(F, P, s) for s in range(2)]; wb = wheelbarrow(F, P); tb = toolbox(F, P); ch = [rubble_chunk(F, P, s, 0.22 + 0.04 * (s % 5)) for s in range(9)]
    rk = [rack(F, P, s, 2) for s in range(3)]; crt = [crate(F, P, v) for v in range(4)]; pal = pallet(F, P); drum = cable_drum(F, P); pipes = pipe_stack(F, P, 3); st = stanchion(F, P)
    lane_ns = (6.8, 9.2, -60.0, -48.0); lane_ew = (-4.0, 32.0, -55.3, -52.7)
    # ---- funnel at the cafeteria opening: two barriers leave exactly the 2.4 m axis lane
    for i, x in enumerate((5.6, 10.4)): inst(jer, f'chicane_jersey_{i}', x, -57.7, hall, rz=0.0)
    inst(sb[0], 'chicane_sandbags_0', 5.5, -56.7, hall, rz=0.1, z=0.0); inst(sb[1], 'chicane_sandbags_1', 10.5, -56.7, hall, rz=-0.1, z=0.0)
    # ---- south-west refit bay
    inst(sc, 'refit_scaffold', 0.6, -58.3, hall, rz=0.0)
    inst(pbd, 'refit_plasterboard_0', -2.2, -58.6, hall, rz=0.12); inst(pbd, 'refit_plasterboard_1', -2.2, -58.6, hall, rz=0.12, z=0.22, support='stack')
    inst(cb[0], 'refit_cement_0', 3.2, -58.9, hall, rz=0.1); inst(cb[1], 'refit_cement_1', 3.6, -57.1, hall, rz=-0.2)
    inst(lad, 'refit_ladder', -1.0, -59.15, hall, rz=0.0, support='lean'); inst(wb, 'refit_wheelbarrow', 1.9, -56.6, hall, rz=0.5)
    inst(tb, 'refit_toolbox', -0.6, -57.1, hall, rz=0.3); inst(bk, 'refit_bucket_0', -0.2, -56.9, hall); inst(bk, 'refit_bucket_1', 0.1, -56.8, hall, rz=1.0)
    for i, (x, rz) in enumerate(((-3.0, 1.57), (4.6, 1.57))): inst(jer, f'sw_jersey_{i}', x, -56.6 - (0 if i else 0.0), hall, rz=rz)
    # ---- north-west store
    for i, (x, y, rz) in enumerate(((-1.6, -51.2, 0.08), (0.9, -51.3, -0.05))): inst(jer, f'nw_jersey_{i}', x, y, hall, rz=rz)
    inst(drum, 'nw_cable_drum_0', -2.9, -50.9, hall); inst(drum, 'nw_cable_drum_1', -2.0, -50.5, hall, rz=1.0)
    inst(pipes, 'nw_pipes', 0.4, -50.4, hall, rz=0.0, scale=(0.8, 0.8, 0.8))
    for i, (x, y) in enumerate(((-1.1, -50.8), (-1.1, -50.8))): inst(crt[i], f'nw_crate_{i}', x, y, hall, rz=0.1, z=0.0 if i == 0 else 0.96, scale=(1, 1, 1), support='floor' if i == 0 else 'stack')
    # ---- under the gantry: barriers funnel to the spine door
    for i, (x, y, rz) in enumerate(((5.0, -51.5, 0.0), (11.0, -51.5, 0.0))): inst(jer, f'mid_jersey_{i}', x, y, hall, rz=rz)
    inst(sb[0], 'mid_sandbags_0', 4.7, -50.5, hall, rz=0.3, z=0.0); inst(sb[1], 'mid_sandbags_1', 11.3, -50.5, hall, rz=-0.2, z=0.0)
    # ---- south-east cordoned ceiling collapse
    pcs = []
    for i in range(90):
        a = rnd.uniform(0, 6.283); r = math.sqrt(rnd.random()); x = 16.8 + math.cos(a) * 2.5 * r; y = -58.4 + math.sin(a) * 1.0 * r
        z = 0.7 * (1 - r ** 1.4) * rnd.uniform(0.4, 1.0)
        o = inst(ch[rnd.randrange(9)], f'cavein_chunk_{i}', x, y, hall, rz=rnd.uniform(0, 6.28), z=max(z - 0.05, 0.0) if False else z - 0.05, scale=(rnd.uniform(0.8, 1.7),) * 3, support='heap')
        o.rotation_euler = (rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), o.rotation_euler[2])
    for nm, (x, y, z, sx, sy, sz, rx, ry, rz) in {'cavein_panel_a': (16.4, -58.2, 0.62, 1.2, 0.6, 0.03, 0.3, -0.25, 0.4), 'cavein_panel_b': (17.8, -58.8, 0.5, 1.2, 0.6, 0.03, -0.2, 0.2, -0.3), 'cavein_panel_c': (15.6, -58.9, 0.4, 1.2, 0.6, 0.03, 0.15, 0.3, 0.9)}.items():
        o = box(nm, -sx / 2, sx / 2, -sy / 2, sy / 2, -sz / 2, sz / 2, F['plaster'], hall, bev=0.004, plan=False); o.location = (LX(x), LY(y), z); o.rotation_euler = (rx, ry, rz); o['support'] = 'heap'
    for i, (x, y, rz) in enumerate(((13.6, -57.4, 1.57), (20.0, -57.4, 1.57), (16.8, -56.3, 0.0))): inst(jer, f'se_jersey_{i}', x, y, hall, rz=rz)
    cb2 = bmesh.new()
    for i in range(10):
        x = 14.4 + rnd.uniform(0, 4.8); y = -58.9 + rnd.uniform(0, 1.0); L = rnd.uniform(0.8, 2.0)
        bm_cyl(cb2, LX(x), LY(y), 5.9 - L, 5.9, 0.012, seg=6)
    mesh_obj('cavein_hanging_cables', cb2, F['steel_charcoal'], hall, rgba=(0.04, 0.04, 0.04, 1))
    # ---- north-east storage racks and stock
    for i, x in enumerate((25.2, 27.8, 30.4)):
        o = inst(rk[i % 3], f'ne_rack_{i}', x, -48.8, hall, rz=math.pi if False else 0.0)
    for i, (x, y) in enumerate(((26.6, -57.8), (27.8, -57.9), (27.2, -57.8), (29.6, -58.0), (30.5, -58.6))):
        inst(crt[(i + 1) % 4], f'se_crate_{i}', x, y, hall, rz=0.1 * i, z=0.0 if i != 2 else 0.96, support='floor' if i != 2 else 'stack')
    inst(pal, 'se_pallet_0', 29.4, -57.0, hall, rz=0.2); inst(pal, 'se_pallet_1', 26.5, -56.8, hall, rz=-0.1)
    inst(jer, 'se_jersey_b', 24.2, -56.4, hall, rz=0.0); inst(jer, 'se_jersey_c', 31.0, -57.6, hall, rz=1.57)
    # ---- weave on the door line
    inst(jer, 'weave_jersey_0', 19.5, -56.0, hall, rz=0.0); inst(jer, 'weave_jersey_1', 23.0, -51.9, hall, rz=0.0)
    # ---- stanchions with tape around the collapse
    return [lane_ns, lane_ew]
