"""Plan drawing of the built map from a plan cut (plan_cut.py) with the walk-test lanes and the door table on top (plain Python: numpy + Pillow).

    python3 draw_assembly_plan.py cut.npz validation/walk_report.json validation/doors.json out.png [x0,y0,x1,y1] [px_per_m] [greybox]

Walls: the section at z 1.1 m (z -5.0 m for the condenser level, drawn lighter). Lanes: the continuous capsule lanes the walk test found (green), failed routes red.
Doors: open green dot, closed red bar across the opening."""
import sys, json, colorsys
import numpy as np
from PIL import Image, ImageDraw
cut, walk, doors, out = sys.argv[1:5]
box = [float(v) for v in sys.argv[5].split(',')] if len(sys.argv) > 5 else [-60, -108, 42, 44]
ppm = float(sys.argv[6]) if len(sys.argv) > 6 else 7.0
D = np.load(cut); x0, y0, x1, y1 = box
W, H = int((x1 - x0) * ppm), int((y1 - y0) * ppm)
im = Image.new('RGB', (W, H), (247, 246, 242)); dr = ImageDraw.Draw(im)
P = lambda x, y: ((x - x0) * ppm, (y1 - y) * ppm)
for g in range(int(x0 // 10) * 10, int(x1) + 1, 10): dr.line([P(g, y0), P(g, y1)], fill=(228, 228, 224)); dr.text(P(g + 0.3, y1 - 0.4), str(g), fill=(150, 150, 150))
for g in range(int(y0 // 10) * 10, int(y1) + 1, 10): dr.line([P(x0, g), P(x1, g)], fill=(228, 228, 224)); dr.text(P(x0 + 0.3, g + 1.4), str(g), fill=(150, 150, 150))
owners = sorted({k.split('|')[0] for k in D.files if '|' in k})
col = {o: tuple(int(c * 255) for c in colorsys.hsv_to_rgb((i * 0.618) % 1, 0.65, 0.55)) for i, o in enumerate(owners)}
for z, light in (('-5.00', True), ('1.10', False)):
    for k in D.files:
        if not k.endswith('|' + z): continue
        o = k.split('|')[0]; c = col[o]
        if light: c = tuple(int(v * 0.35 + 255 * 0.65) for v in c)
        for s in D[k]: dr.line([P(s[0], s[1]), P(s[2], s[3])], fill=c, width=1)
R = json.load(open(walk))
for r in R['routes']:
    if 'lane' in r: dr.line([P(p[0], p[1]) for p in r['lane']], fill=(30, 160, 60), width=2)
    elif r.get('stuck_at'): dr.ellipse([P(r['stuck_at'][0] - 0.6, r['stuck_at'][1] + 0.6), P(r['stuck_at'][0] + 0.6, r['stuck_at'][1] - 0.6)], outline=(210, 30, 30), width=2)
for d in json.load(open(doors))['doors']:
    x, y = d['plan'][0], d['plan'][1]; ox, oy = d['outward']; tx, ty = -oy, ox; h = d['clear_w'] / 2
    if d['state'] == 'open': dr.ellipse([P(x - 0.35, y + 0.35), P(x + 0.35, y - 0.35)], fill=(30, 160, 60))
    else: dr.line([P(x - tx * h, y - ty * h), P(x + tx * h, y + ty * h)], fill=(210, 30, 30), width=4)
RY = -18.7      # build_compact_map.RY: the reactor cluster's labels are reactor-local + RY
LABELS = {'ROOM_front-end-area': (8, -66, 'cafeteria'), 'ROOM_spawn-room': (8, -99, 'spawn'), 'ROOM_mine': (-50, -76, 'mine portal'), 'ROOM_refinery': (-26, -49, 'refinery'),
          'ROOM_medical-reanimation': (32, -70, 'medical'), 'ROOM_fuel-corridor': (-15, -34, 'fuel corridor'), 'ROOM_reactor-room': (0, RY, 'REACTOR'), 'ROOM_turbine-room': (2.8, 36 + RY, 'turbine'),
          'ROOM_electrical-room': (19, 25 + RY, 'electrical'), 'ROOM_condenser-bay': (6, 30.5 + RY, '(condenser, -6 m)'), 'ROOM_waste-storage': (21, 4 + RY, 'waste'), 'ROOM_cooling-plant': (-22, 4 + RY, 'cooling'),
          'ROOM_compliance-dock': (21, -45, 'dock'), 'hall': (8, -54, 'hall'), 'yard': (-32, -80, 'yard'), 'spine': (8, -44, 'spine'), 'concourse': (0, -36, 'concourse'), 'stair': (-9.5, 22 + RY, 'stair')}
if len(sys.argv) > 7 and sys.argv[7] == 'greybox':        # greybox_fuel_test.py (reactor centre y -20.6, grey fuel corridor)
    for k in ('ROOM_reactor-room', 'ROOM_turbine-room', 'ROOM_electrical-room', 'ROOM_condenser-bay', 'ROOM_cooling-plant', 'ROOM_waste-storage', 'stair'):
        x, y, t = LABELS[k]; LABELS[k] = (x, y - 20.6 - RY, t)
    LABELS['ROOM_fuel-corridor'] = (-17, -33, 'grey fuel corridor')
for k, (x, y, t) in LABELS.items():
    if x0 < x < x1 and y0 < y < y1:
        p = P(x, y); w = 6 * len(t); dr.rectangle([p[0] - w / 2 - 2, p[1] - 6, p[0] + w / 2 + 2, p[1] + 7], fill=(255, 255, 255)); dr.text((p[0] - w / 2, p[1] - 5), t, fill=(0, 0, 0))
im.save(out); print('PLAN', W, 'x', H, '->', out)
