"""Drum label decal sheet: transparent RGBA, stripes and stencil text drawn into the image (no geometry). Run with system python (PIL): python3 drumdecal.py out.png"""
import sys
from PIL import Image, ImageDraw, ImageFont
W, H = 768, 512
LABELS = [('DIESEL', 'FLAMMABLE'), ('LUBE OIL', 'ISO 46')]
def font(sz):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf'):
        try: return ImageFont.truetype(p, sz)
        except OSError: pass
    return ImageFont.load_default()
def make(path):
    im = Image.new('RGBA', (W, H * len(LABELS)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k, (t1, t2) in enumerate(LABELS):
        y0 = k * H
        d.rectangle([0, y0 + 20, W, y0 + 52], fill=(156, 124, 44, 255)); d.rectangle([0, y0 + H - 52, W, y0 + H - 20], fill=(156, 124, 44, 255))   # amber hazard stripes
        for t, sz, cy in ((t1, 118, y0 + 205), (t2, 62, y0 + 330)):
            f = font(sz); w = d.textlength(t, font=f); d.text(((W - w) / 2, cy), t, font=f, fill=(206, 204, 192, 255), anchor='lm')
    im.save(path)
if __name__ == '__main__': make(sys.argv[1])
