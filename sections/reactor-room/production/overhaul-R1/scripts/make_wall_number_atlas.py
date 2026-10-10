"""Draw the wall-number stencil atlas: four wall rows (N, S, E, W) by five bays.

System Python with Pillow:  python3 make_wall_number_atlas.py OUT.png
Cells are 768x256 px (3:1, matching the 1.8 m x 0.6 m stencil in
rh_hall_moody_fixes.py). The result is a grayscale mask; the hall script packs it.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

CELL_W, CELL_H, BAYS, ROWS = 768, 256, 5, 4
LETTERS = ['N', 'S', 'E', 'W']

out = sys.argv[1]
atlas = Image.new('L', (CELL_W * BAYS, CELL_H * ROWS), 0)
draw = ImageDraw.Draw(atlas)
big = ImageFont.load_default(size=170)
small = ImageFont.load_default(size=58)
for r, letter in enumerate(LETTERS):
    for b in range(BAYS):
        x0, y0 = b * CELL_W, r * CELL_H
        text = f'{letter}-{b + 1}'
        w = draw.textlength(text, font=big)
        draw.text((x0 + (CELL_W - w) / 2, y0 + 14), text, font=big, fill=255, stroke_width=7, stroke_fill=255)
        # painted bay bar under the number, like a column-line stencil
        draw.rectangle((x0 + 120, y0 + CELL_H - 34, x0 + CELL_W - 120, y0 + CELL_H - 22), fill=255)
atlas.save(out)
print('wrote', out, atlas.size)
