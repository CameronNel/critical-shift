"""Pairwise 2D footprint overlap check for the compact layout (short fuel corridor) (plain Python, no Blender):  python3 check_footprints.py
Rooms are measured outer plan bounds (COMBINED_MAP.md, MEASURED_ROOM_SIZES.md) transformed by the placement used in build_compact_map.py. Overlaps smaller than 0.5 m
are reported as touching (walls meeting at a door), larger ones as overlaps."""
import math, itertools
s2 = math.sqrt(0.5)
def poly(loc, rz, x0, x1, y0, y1):
    c, s = math.cos(math.radians(rz)), math.sin(math.radians(rz))
    return [(loc[0] + c * x - s * y, loc[1] + s * x + c * y) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
def box(x0, x1, y0, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
RY = -18.7   # reactor centre y (build_compact_map.RY); the reactor cluster below is reactor-local + RY
def r(*b): return box(b[0], b[1], b[2] + RY, b[3] + RY)
R = {   # placements of build_compact_map.py (short fuel corridor layout); module outer bounds as measured (COMBINED_MAP.md, MEASURED_ROOM_SIZES.md, plan cuts 2026-10-13)
 'reactor hall': r(-11.6, 11.6, -11.6, 11.6), 'reactor N stub': r(-2.8, 2.8, 11.6, 14.5), 'reactor W stub': r(-14.5, -11.6, -3.3, 3.3),
 'turbine': poly((0, 14.5 + RY), 0, -4.25, 10.25, -0.36, 24.25), 'electrical': poly((10.5, 33.0 + RY), -90, -5.75, 8.55, -0.25, 16.97),
 'condenser stair shaft': r(-6.95, -4.25, 16.9, 29.55),
 'waste': poly((11.94, 3.86 + RY), -90, -6.32, 7.61, -0.32, 18.32), 'cooling': poly((-14.5, RY), 90, -5.8, 5.8, 0, 13.3), 'dock': poly((12.15, -40.39), -90, -7.1, 7.21, -2.1, 16.08),
 'concourse': box(-5.76, 6.15, -38.6, -33.2), 'reactor south tunnel': box(-2.8, 2.8, -33.2, RY - 11.6), 'spine': box(5.85, 10.15, -48, -33.1),
 'fuel corridor entry': box(-24.74, -20.2, -43.6, -38.1), 'fuel corridor hall': box(-24.74, -5.46, -38.41, -30.77),
 'refinery': box(-33.8, -18.8, -57.7, -40.3), 'front-end hall': box(-4, 32, -60, -48), 'cafeteria': box(-8, 26, -86, -66), 'medical': box(26, 38.4, -75.5, -64.8), 'yard': box(-52, -12, -90, -60),
 'spawn': box(0, 17.4, -105.4, -92.4)}
def axes(p):
    for i in range(len(p)):
        a, b = p[i], p[(i + 1) % len(p)]; e = (b[0] - a[0], b[1] - a[1]); n = (-e[1], e[0]); l = math.hypot(*n); yield (n[0] / l, n[1] / l)
def sat(p, q):
    """Smallest penetration depth along any separating axis (<= 0 means separated)."""
    best = 1e9
    for ax in itertools.chain(axes(p), axes(q)):
        pp = [x * ax[0] + y * ax[1] for x, y in p]; qq = [x * ax[0] + y * ax[1] for x, y in q]
        ov = min(max(pp), max(qq)) - max(min(pp), min(qq))
        if ov <= 0: return ov
        best = min(best, ov)
    return best
bad = []
for (a, pa), (b, pb) in itertools.combinations(R.items(), 2):
    d = sat(pa, pb)
    if d > 0: bad.append((round(d, 2), a, b))
for d, a, b in sorted(bad, reverse=True): print(('OVERLAP' if d >= 0.5 else 'touching'), d, a, '|', b)
print('checked', len(R), 'footprints,', sum(1 for d, a, b in bad if d >= 0.5), 'overlaps >= 0.5 m')
xs = [x for p in R.values() for x, y in p]; ys = [y for p in R.values() for x, y in p]
print('extent x %.0f to %.0f, y %.0f to %.0f' % (min(xs), max(xs), min(ys), max(ys)))
