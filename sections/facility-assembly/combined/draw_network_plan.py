"""Draw the combined-map network plan (rooms as measured footprints, halls as drawn by the build) to a PNG. System Python with Pillow:
    blender --background --python dump_network.py -- /tmp/net.json && python3 draw_network_plan.py /tmp/net.json renders/network_plan.png
Room footprints are the measured plan rectangles recorded in COMBINED_MAP.md (axis-aligned outer bounds); they are labels for the drawing, not geometry."""
import json, sys
from PIL import Image, ImageDraw, ImageFont
d = json.load(open(sys.argv[1])); out = sys.argv[2]
FD = '/mnt/skills/examples/canvas-design/canvas-fonts/'
F = ImageFont.truetype(FD + 'GeistMono-Bold.ttf', 15); S = ImageFont.truetype(FD + 'GeistMono-Regular.ttf', 12); T = ImageFont.truetype(FD + 'GeistMono-Bold.ttf', 24)
ROOMS = {  # name: (x0, x1, y0, y1) plan outer bounds
 'REACTOR HALL': (-11.6, 11.6, -11.6, 11.6), 'TURBINE': (-4.52, 10.25, 16.64, 42.4), 'ELECTRICAL': (14.0, 28.3, 26.0, 43.22), 'WASTE': (27.68, 46.7, -31.6, -17.7),
 'COOLING': (-57.4, -44.1, -24.8, -13.2), 'FUEL CORRIDOR': (-27.9, -4.9, -43.6, -19.6), 'REFINERY': (-33.8, -18.8, -57.7, -40.3), 'FRONT-END HALL': (-4, 32, -60, -48),
 'CAFETERIA': (-8, 26, -86, -66), 'SPAWN': (0, 17.4, -105.4, -92.4), 'MEDICAL': (26, 38.4, -75.5, -64.8), 'COMPLIANCE DOCK': (57.9, 76.1, -86.2, -71.8), 'YARD': (-52, -12, -90, -60),
 'CONCOURSE': (-11.1, 6.15, -19.9, -14.5), 'SPINE': (5.85, 10.15, -48, -14.5), 'MINE': (-112, -52, -80, -60)}
ZC = {'turbine-room': (255, 140, 30), 'electrical-room': (60, 150, 255), 'waste-storage': (255, 200, 30), 'cooling-plant': (30, 220, 205), 'bridge': (255, 140, 30), 'tunnel': (200, 220, 245),
      'trunk': (120, 235, 100), 'dock': (210, 90, 255), 'ring': (225, 225, 240), 'passage': (255, 205, 75), 'service': (80, 235, 225)}
x0, x1, y0, y1 = -115, 82, -108, 58; SC = 5.2; M = 40
W = int((x1 - x0) * SC) + 2 * M; H = int((y1 - y0) * SC) + 2 * M + 70
im = Image.new('RGB', (W, H), (10, 13, 18)); dr = ImageDraw.Draw(im)
def P(x, y): return (M + (x - x0) * SC, M + 50 + (y1 - y) * SC)
for gx in range(-110, 90, 10):
    dr.line([P(gx, y0), P(gx, y1)], fill=(22, 27, 34)); dr.text(P(gx, y1 + 0.5), str(gx), font=S, fill=(70, 80, 92))
for gy in range(-100, 60, 10):
    dr.line([P(x0, gy), P(x1, gy)], fill=(22, 27, 34)); dr.text(P(x0 + 0.3, gy), str(gy), font=S, fill=(70, 80, 92))
for k, L in d['links'].items():
    col = ZC.get(L['zone'], (200, 200, 200)); pts = [P(*q) for q in L['line']]
    dr.line(pts, fill=tuple(int(c * 0.35) for c in col), width=int(L['w'] * SC), joint='curve')
    dr.line(pts, fill=col, width=2, joint='curve')
for n, (a, b, c, e) in ROOMS.items():
    p0, p1 = P(a, e), P(b, c); dr.rectangle([p0, p1], outline=(230, 235, 245), width=2, fill=(26, 32, 42))
    dr.text(((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2), n, font=F, fill=(235, 238, 245), anchor='mm')
for k, L in d['links'].items():
    mid = L['line'][len(L['line']) // 2]; col = ZC.get(L['zone'], (200, 200, 200)); dr.text(P(mid[0] + 1.2, mid[1] + 1.2), k, font=S, fill=col)
dr.text((M, 12), 'COMBINED MAP: rooms and halls (plan m, +x east, +y north), unreviewed', font=T, fill=(235, 238, 245))
im.save(out); print('wrote', out, im.size)
