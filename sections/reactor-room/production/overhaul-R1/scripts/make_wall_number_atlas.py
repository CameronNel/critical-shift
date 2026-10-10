"""Draw the wall-number stencil atlas: four wall rows (N, S, E, W) by five bays.

System Python with Pillow:  python3 make_wall_number_atlas.py OUT.png
Cells are 768x256 px (3:1, matching the 2.4 m x 0.8 m stencil in
rh_hall_moody_fixes.py). The result is a grayscale mask; the hall script packs it.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

CELL_W, CELL_H, BAYS, ROWS = 768, 256, 5, 4
LETTERS = ['N', 'S', 'E', 'W']

out = sys.argv[1]
atlas = Image.new('L', (CELL_W * BAYS, CELL_H * ROWS), 0)
draw = ImageDraw.Draw(atlas)
FONTS = ['/mnt/skills/examples/canvas-design/canvas-fonts/BigShoulders-Bold.ttf']  # condensed industrial face
try:
    big = ImageFont.truetype(next(f for f in FONTS if __import__('os').path.exists(f)), 215)
except StopIteration:
    big = ImageFont.load_default(size=170)
for r, letter in enumerate(LETTERS):
    for b in range(BAYS):
        x0, y0 = b * CELL_W, r * CELL_H
        text = f'{letter}-{b + 1}'
        w = draw.textlength(text, font=big)
        draw.text((x0 + (CELL_W - w) / 2, y0 + 4), text, font=big, fill=255, stroke_width=3, stroke_fill=255)
        # stencil bridges: thin cuts through every letter stroke
        for fy in (0.36, 0.64):
            draw.rectangle((x0, y0 + int(fy * CELL_H) - 4, x0 + CELL_W, y0 + int(fy * CELL_H) + 4), fill=0)
        # painted bay bar under the number, like a column-line stencil
        draw.rectangle((x0 + 160, y0 + CELL_H - 18, x0 + CELL_W - 160, y0 + CELL_H - 8), fill=255)
atlas.save(out)
print('wrote', out, atlas.size)
