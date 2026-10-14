"""Room-to-room intrusion check on a plan-cut file (plain Python + numpy; the cut comes from plan_cut.py):

    python3 check_overlaps.py validation/plan_cut.npz

For every room R and every cut height, R's outline is the axis-aligned rectangle of R's own cut segments in R's module frame (placement read from the
npz metadata), shrunk by 0.3 m. Any segment midpoint of another owner (room or connector) inside that rectangle is an intrusion. Doorways are expected to show
a few (thresholds, the dock P1 tube in the spine wall), so the report lists counts per pair and height; it is a geometry screen, not a collision test."""
import sys, json, numpy as np, math
D = np.load(sys.argv[1]); meta = json.loads(str(D['__meta__']))
place = meta['placements']; ZS = sorted({k.split('|')[1] for k in D.files if '|' in k})
SKIP_PAIRS = {('ROOM_front-end-area', 'ROOM_spawn-room'), ('ROOM_front-end-area', 'ROOM_mine')}   # the yard and mine share terrain and a portal; the spawn stub sits in the cafeteria wall
out = []
for z in ZS:
    segs = {k.split('|')[0]: D[k] for k in D.files if k.endswith('|' + z)}
    for r, (loc, rz) in place.items():
        if r not in segs: continue
        c, s = math.cos(math.radians(-rz)), math.sin(math.radians(-rz))
        def to_local(P): q = P - np.array(loc[:2]); return np.stack([c * q[:, 0] - s * q[:, 1], s * q[:, 0] + c * q[:, 1]], 1)
        own = to_local(segs[r].reshape(-1, 2)); lo = np.percentile(own, 0.5, 0) + 0.3; hi = np.percentile(own, 99.5, 0) - 0.3
        for o, S in segs.items():
            if o == r or (r, o) in SKIP_PAIRS or (o, r) in SKIP_PAIRS: continue
            mid = to_local((S[:, :2] + S[:, 2:]) / 2); inside = np.all((mid > lo) & (mid < hi), 1)
            if inside.sum(): out.append((z, r, o, int(inside.sum()), [round(float(v), 2) for v in mid[inside].min(0)], [round(float(v), 2) for v in mid[inside].max(0)]))
for row in out: print('INTRUSION z=%s %s <- %s: %d segments, local x/y %s..%s' % row)
print('checked', len(place), 'rooms at', len(ZS), 'heights;', len(out), 'pairs with intrusions')
