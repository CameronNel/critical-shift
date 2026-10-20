"""Dimensioned plan of the condenser bay: annotates the cutaway made by render_cutaway_A3.py (2048 px square, orthographic 12.8 m wide,
centred on module (3.85, 3.55), north up) with the room's measured dimensions, levels, a scale bar and the main items. No Blender.

    python3 annotate_plan_A3.py <cutaway.png> <out.png>

Every dimension is in metres in the module frame, read from the saved module_aaa_A3.blend (walls: WestWall, EastWall, NorthWall,
SouthWall west/east/header, D01 stub walls; levels from reach-A3.json; the west escape door from combined/build_compact_map.py, ESC).
"""
import sys
from PIL import Image, ImageDraw, ImageFont

src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB'); N = im.size[0]; S = N / 12.8; X0, Y1 = 3.85 - 6.4, 3.55 + 6.4
HEAD = 150
def P(x, y): return ((x - X0) * S, (Y1 - y) * S + HEAD)
canvas = Image.new('RGB', (N, N + HEAD), (18, 18, 18)); canvas.paste(im, (0, HEAD)); d = ImageDraw.Draw(canvas)
def font(sz, bold=False):
    try: return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if bold else ''), sz)
    except OSError: return ImageFont.load_default()
F, FB, FS = font(30), font(46, True), font(26)
Y, W = (255, 205, 60), (235, 235, 235)

d.text((24, 12), 'CUTAWAY - condenser bay A3, dimensioned plan', fill=Y, font=FB)
d.text((24, 74), 'Everything above module z 4.9 m (roof, crane runway, ceiling services) is clipped. Not a player view. North (+y) up.', fill=W, font=FS)
d.text((24, 108), 'Metres, module frame. Floor z 0.00; gallery deck z 3.90; roof underside 5.995 in the map (bay at map z -6.3).', fill=W, font=FS)

def dim(a, b, off, text, vertical=False):
    """Dimension line between plan points a and b, offset `off` metres (perpendicular), with end ticks and a centred label."""
    if vertical: pa, pb = P(a[0] + off, a[1]), P(b[0] + off, b[1])
    else: pa, pb = P(a[0], a[1] + off), P(b[0], b[1] + off)
    d.line([pa, pb], fill=Y, width=4)
    for p in (pa, pb):
        d.line([(p[0] - 14, p[1]), (p[0] + 14, p[1])] if vertical else [(p[0], p[1] - 14), (p[0], p[1] + 14)], fill=Y, width=4)
    mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
    tw = int(d.textlength(text, font=F))
    tag = Image.new('RGB', (tw + 16, 44), (18, 18, 18)); ImageDraw.Draw(tag).text((8, 4), text, fill=Y, font=F)
    if vertical: tag = tag.rotate(90, expand=True)                          # along the line: stays inside the image at the edges
    canvas.paste(tag, (int(mx - tag.size[0] / 2), int(my - tag.size[1] / 2)))

dim((-1.80, 9.40), (9.60, 9.40), 0.40, '11.40 inside')                       # west wall face to east wall face
dim((9.60, 0.00), (9.60, 9.40), 0.38, '9.40 inside', vertical=True)            # south wall face to north wall face
dim((-1.00, 0.00), (1.00, 0.00), -0.30, 'D01 2.00')                           # the opening in the south wall
dim((-1.24, -2.50), (1.24, -2.50), -0.20, 'stub 2.48')                        # the D01 stub between its walls
dim((-1.80, 8.40), (-1.80, 9.40), -0.45, '1.00', vertical=True)                # the west escape door (cut in the map)

def label(x, y, text, dx=0.0, dy=0.0):
    p = P(x, y); q = P(x + dx, y + dy)
    d.ellipse([p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7], fill=Y)
    if dx or dy: d.line([p, q], fill=Y, width=3)
    tw = d.textlength(text, font=FS); bx = q[0] + (8 if dx >= 0 else -tw - 8)
    d.rectangle((bx - 6, q[1] - 18, bx + tw + 6, q[1] + 18), fill=(18, 18, 18)); d.text((bx, q[1] - 15), text, fill=W, font=FS)

label(3.0, 4.05, 'CD-01 condenser shell', 0.0, 0.0)
label(0.6, 4.05, 'west waterbox', 0.0, -1.2)
label(5.4, 4.05, 'east waterbox', 0.6, -1.0)
label(2.0, 7.0, 'CEP-A', -0.2, 0.9)
label(3.7, 8.2, 'CEP-B', 0.6, 0.6)
label(-0.85, 4.1, 'operator desk (TRIP, CD ISOL)', 0.0, -2.2)
label(8.55, 3.2, 'CW SUPPLY isolation, chain op.', -0.3, -1.1)
label(8.33, 4.9, 'CW RETURN isolation, chain op.', -0.4, 1.3)
label(-0.7, 7.3, 'ejector skid, chain op.', 0.4, 1.4)
label(4.0, 0.5, 'stair to gallery (deck z 3.90)', 0.0, 0.0)
label(0.45, 2.6, 'gallery round the U04 neck (z 3.90)', 0.6, -1.3)
label(0.0, -1.3, 'D01: to the stair corridor (map)', 1.6, 0.0)
label(-1.95, 8.9, 'west escape door (cut in the map)', 0.3, 0.75)

# scale bar, 0..2 m in 0.5 m steps
x0, y0 = 7.2, -2.3
for k in range(4):
    a, b = P(x0 + 0.5 * k, y0), P(x0 + 0.5 * (k + 1), y0)
    d.rectangle([a[0], a[1] - 10, b[0], b[1] + 10], fill=Y if k % 2 == 0 else W)
for k, t in ((0, '0'), (2, '1'), (4, '2 m')):
    p = P(x0 + 0.5 * k, y0); d.text((p[0] - 10, p[1] + 16), t, fill=W, font=FS)
canvas.save(out)
print('PLAN written', out)
