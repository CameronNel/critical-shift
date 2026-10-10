"""Draw the wall-number stencil atlas: four wall rows (N, S, E, W) by five bays.

System Python with Pillow:  python3 make_wall_number_atlas.py OUT.png
Cells are 768x256 px (3:1, matching the 2.4 m x 0.8 m stencil in
rh_hall_moody_fixes.py). The result is a grayscale mask; the hall script packs it.
Numerals use a round geometric face and every corner is rounded by blur and
threshold, so the painted numbers have no sharp points.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

CELL_W, CELL_H, BAYS, ROWS = 768, 256, 5, 4
LETTERS = ['N', 'S', 'E', 'W']
FONT = '/mnt/skills/examples/canvas-design/canvas-fonts/Outfit-Bold.ttf'
assert os.path.exists(FONT), 'Round numeral font missing: ' + FONT

out = sys.argv[1]
big = ImageFont.truetype(FONT, 215)
atlas = Image.new('L', (CELL_W * BAYS, CELL_H * ROWS), 0)
draw = ImageDraw.Draw(atlas)
for r, letter in enumerate(LETTERS):
    for b in range(BAYS):
        x0, y0 = b * CELL_W, r * CELL_H
        text = f'{letter}-{b + 1}'
        gap = 30
        widths = [draw.textlength(ch, font=big) for ch in text]
        x = x0 + (CELL_W - (sum(widths) + gap * (len(text) - 1))) / 2
        for ch, cw in zip(text, widths):
            draw.text((x, y0 - 4), ch, font=big, fill=255, stroke_width=2, stroke_fill=255)
            x += cw + gap
        draw.rounded_rectangle((x0 + 160, y0 + CELL_H - 20, x0 + CELL_W - 160, y0 + CELL_H - 8), radius=6, fill=255)
# round every corner: blur, then threshold
atlas = atlas.filter(ImageFilter.GaussianBlur(4)).point(lambda v: 255 if v > 128 else 0)
atlas = atlas.filter(ImageFilter.GaussianBlur(1.2))
atlas.save(out)
print('wrote', out, atlas.size)
