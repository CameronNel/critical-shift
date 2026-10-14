"""Capsule walk test for the grey-box fuel test (same method and capsule as walk_test.py, routes moved with the reactor). Run on the grey-box scene:

    blender --background <scratch>/greybox.blend --python greybox_walk.py -- <out.json>"""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import walk_test as W
DY = -20.6                                    # greybox_fuel_test.py: reactor centre y
def P(*pts): return [tuple(map(float, p)) for p in pts]
def s(*pts): return [(x, y + DY, z) for x, y, z in pts]
CY = DY - 17.2                                 # concourse centre line
ROUTES = {
    'spawn_to_reactor': P((8, -88, 0), (8, -80, 0), (8, -60, 0), (8, -49, 0), (8, -40, 0), (8, CY, 0), (0, CY, 0), (0, DY - 12, 0), (0, DY - 6, 0)),
    'refinery_fuel_to_reactor': P((-22.2, -46.5, 0), (-22.2, -43.6, 0), (-22.2, CY, 0), (-10.8, CY, 0), (0, CY, 0), (0, DY - 12, 0), (0, DY - 6, 0)),
    'medical_to_reactor': P((31, -70, 0), (26, -70, 0), (8, -70, 0), (8, -60, 0), (8, -49, 0), (8, -40, 0), (8, CY, 0), (0, CY, 0), (0, DY - 12, 0), (0, DY - 6, 0)),
    'reactor_to_turbine_to_electrical': s((0, 6.5, 0), (0, 10.5, 0), (0, 14.5, 0), (0, 16.5, 0), (8.2, 17.5, 0), (8.2, 33.0, 0), (10.4, 33.0, 0), (13.0, 33.0, 0), (19.0, 33.0, 0)),
    'reactor_to_condenser': s((0, 7.5, 0), (0, 14.5, 0), (0, 16.5, 0), (-2.4, 18.0, 0), (-2.6, 27.95, 0), (-4.2, 27.95, 0), (-5.6, 27.9, 0), (-5.6, 26.8, 0), (-5.6, 16.9, -6), (-5.6, 15.7, -6),
                              (1.6, 15.7, -6), (1.6, 19.3, -6), (1.6, 22.0, -6)),
    'reactor_to_cooling': s((-9.0, 0, 0), (-11.6, 0, 0), (-14.5, 0, 0), (-18, 0, 0), (-24, 0, 0)),
    'reactor_to_waste': s((0, -6.0, 0), (6.5, -6.5, 0), (7.5, 0, 0), (8.5, 3.6, 0), (10.8, 3.6, 0), (11.94, 3.6, 0), (16.0, 3.6, 0), (24.0, 3.6, 0)),
    'reactor_to_dock': P((0, DY - 6, 0), (0, DY - 12, 0), (0, CY, 0), (8, CY, 0), (8, -40.39, 0), (10.15, -40.39, 0), (12.15, -40.39, 0), (14.5, -40.39, 0)),
    'spawn_to_electrical': P((8, -88, 0), (8, -80, 0), (8, -60, 0), (8, -49, 0), (8, -40, 0), (8, CY, 0), (0, CY, 0), (0, DY - 12, 0), (0, DY - 7.5, 0), (6.5, DY - 6.5, 0), (7.5, DY, 0),
                           (6.5, DY + 6.5, 0), (0, DY + 7.5, 0), (0, DY + 10.5, 0), (0, DY + 14.5, 0), (0, DY + 16.5, 0), (8.2, DY + 17.5, 0), (8.2, DY + 33.0, 0), (10.4, DY + 33.0, 0), (13.0, DY + 33.0, 0)),
}
out = sys.argv[sys.argv.index('--') + 1]
t0 = time.time(); T, own, names = W.world_tris(-6.6, 2.3)
only = sys.argv[sys.argv.index('--') + 2:]
res = [W.test_route(k, v, T, own, names) for k, v in ROUTES.items() if not only or k in only]
json.dump(dict(capsule=dict(radius=W.R_CAP, height=W.H_CAP, step_offset=W.STEP), routes=res, note='grey-box fuel test; geometry only'), open(out, 'w'), indent=1)
print('GBWALK done %.0fs: %d/%d pass' % (time.time() - t0, sum(r['passed'] for r in res), len(res)))
