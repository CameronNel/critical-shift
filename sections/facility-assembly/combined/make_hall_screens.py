"""Draw the wall-screen images for the combined map's halls: python3 make_hall_screens.py textures/
Four designs per zone colour (schematic, status table, route map, trace), 1024x620, drawn dark with glowing lines so the emissive material reads as a lit display.
Content is placeholder facility signage, not a data feed."""
import math, os, random, sys, zlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FD = '/mnt/skills/examples/canvas-design/canvas-fonts/'
BOLD = ImageFont.truetype(FD + 'GeistMono-Bold.ttf', 40); REG = ImageFont.truetype(FD + 'GeistMono-Regular.ttf', 26); SM = ImageFont.truetype(FD + 'GeistMono-Regular.ttf', 20); BIG = ImageFont.truetype(FD + 'GeistMono-Bold.ttf', 64)
W, H = 1024, 620
ZONES = {'turbine-room': ((255, 140, 30), 'TURBINE HALL'), 'electrical-room': ((60, 150, 255), 'ELECTRICAL'), 'waste-storage': ((255, 200, 30), 'WASTE STORAGE'),
         'cooling-plant': ((30, 235, 220), 'COOLING PLANT'), 'bridge': ((255, 140, 30), 'TURBINE - ELECTRICAL'), 'tunnel': ((215, 235, 255), 'REACTOR CONCOURSE'), 'trunk': ((140, 255, 115), 'EAST TRUNK'), 'dock': ((215, 90, 255), 'COMPLIANCE DOCK'),
         'ring': ((230, 230, 242), 'OUTER RING'), 'passage': ((255, 205, 75), 'YARD PASSAGE'), 'service': ((80, 240, 230), 'PLANT SERVICE')}
def mix(c, f): return tuple(int(v * f) for v in c)
def base(col, title, sub):
    im = Image.new('RGB', (W, H), (4, 7, 10)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W - 1, 78), fill=mix(col, 0.16)); d.line((0, 78, W, 78), fill=col, width=3)
    d.text((28, 16), title, font=BOLD, fill=col); d.text((W - 28, 28), sub, font=REG, fill=mix(col, 0.75), anchor='ra')
    d.rectangle((2, 2, W - 3, H - 3), outline=mix(col, 0.55), width=3)
    return im, d
def schematic(col, name, rnd):
    im, d = base(col, name, 'SYSTEM SCHEMATIC'); y0 = 130
    nodes = [(120, 300, 'SRC'), (330, 220, 'P-1'), (330, 400, 'P-2'), (560, 310, 'HX'), (790, 220, 'V-3'), (790, 410, 'LOAD'), (940, 310, 'OUT')]
    for a, b in ((0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 6), (5, 6)):
        d.line((nodes[a][0], nodes[a][1], nodes[b][0], nodes[b][1]), fill=mix(col, 0.8), width=5)
    for x, y, t in nodes:
        d.ellipse((x - 34, y - 34, x + 34, y + 34), fill=(5, 9, 12), outline=col, width=5); d.text((x, y), t, font=SM, fill=col, anchor='mm')
    for i in range(5): d.rectangle((60 + i * 80, 520, 60 + i * 80 + 60, 560), fill=mix(col, 0.3 + 0.14 * i))
    d.text((W - 40, 540), 'NOMINAL', font=REG, fill=col, anchor='rm'); return im
def table(col, name, rnd):
    im, d = base(col, name, 'STATUS BOARD')
    rows = ['LINE A', 'LINE B', 'PUMP 1', 'PUMP 2', 'VALVE 3', 'BUS 4', 'SEAL 5']
    for i, r in enumerate(rows):
        y = 112 + i * 70; v = rnd.uniform(0.35, 0.95)
        d.text((30, y), r, font=REG, fill=col); d.rectangle((250, y + 4, 800, y + 38), outline=mix(col, 0.6), width=2)
        d.rectangle((254, y + 8, 254 + int(542 * v), y + 34), fill=mix(col, 0.55 + 0.4 * v)); d.text((990, y), '%3d%%' % int(v * 100), font=REG, fill=col, anchor='ra')
    return im
def route(col, name, rnd):
    im, d = base(col, name, 'YOU ARE HERE')
    d.line((100, 330, 330, 330, 330, 190, 700, 190, 700, 440, 930, 440), fill=mix(col, 0.7), width=18, joint='curve')
    for x, y, t in ((100, 330, 'HALL'), (330, 190, 'LIFT'), (700, 190, 'BUS'), (930, 440, name.split()[0])):
        d.rectangle((x - 46, y - 24, x + 46, y + 24), fill=(4, 7, 10), outline=col, width=4); d.text((x, y), t[:6], font=SM, fill=col, anchor='mm')
    d.polygon([(480, 330), (520, 310), (520, 350)], fill=col); d.text((480, 380), 'YOU', font=SM, fill=col, anchor='mm')
    d.text((40, 560), 'EXITS: 2   AIRLOCK: AHEAD', font=REG, fill=mix(col, 0.85)); return im
def trace(col, name, rnd):
    im, d = base(col, name, 'LIVE TRACE')
    for gy in range(120, 560, 55): d.line((30, gy, W - 30, gy), fill=mix(col, 0.18), width=1)
    for gx in range(30, W, 96): d.line((gx, 110, gx, 560), fill=mix(col, 0.18), width=1)
    for k, f in enumerate((1.0, 0.6)):
        pts = [(30 + i * 8, 330 + math.sin(i * 0.19 + k * 2) * (90 - 30 * k) + rnd.uniform(-9, 9)) for i in range(120)]
        d.line(pts, fill=mix(col, f), width=4)
    d.text((40, 570), 'RPM 3000', font=REG, fill=col); d.text((W - 40, 570), 'LOAD 82%', font=REG, fill=col, anchor='ra'); return im
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for z, (col, name) in ZONES.items():
    for k, fn in enumerate((schematic, table, route, trace)):
        im = fn(col, name, random.Random(zlib.crc32(f'{z}{k}'.encode())))
        glow = im.filter(ImageFilter.GaussianBlur(4)); im = Image.blend(im, Image.eval(Image.merge('RGB', [Image.eval(c, lambda v: min(255, v * 2)) for c in glow.split()]), lambda v: v), 0.0)
        im.save(os.path.join(out, f'hall_screen_{z}_{k}.png'))
print('wrote', len(ZONES) * 4)
