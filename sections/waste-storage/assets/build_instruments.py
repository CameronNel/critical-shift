"""Original flat instrument artwork for the Waste Storage Blender source.

Run with bundled Python/Pillow. These are authored UI/dial textures, not generated
reference images or composited render evidence. Final PNGs are packed in Blender.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT = Path(__file__).resolve().parent


def font(size, bold=False, mono=False):
    family = 'consola' if mono else ('arialbd' if bold else 'arial')
    windows = Path('C:/Windows/Fonts') / (family + '.ttf')
    if windows.is_file():
        return ImageFont.truetype(str(windows), size)
    try:
        return ImageFont.truetype('DejaVuSansMono.ttf' if mono else 'DejaVuSans.ttf', size)
    except OSError:
        return ImageFont.load_default(size=size)


def screen():
    # 1.6:1 matches the authored instrument aperture. Quiet early digital grammar.
    im = Image.new('RGB', (800, 500), (14, 26, 20))
    d = ImageDraw.Draw(im)
    lit, quiet, line = (163, 192, 153), (109, 141, 110), (50, 77, 57)
    d.text((30, 19), 'WS / RECEIVING', font=font(29, bold=True), fill=lit)
    d.text((615, 27), 'LOCAL', font=font(20, mono=True), fill=quiet)
    d.line((30, 64, 770, 64), fill=line, width=2)
    d.text((30, 87), 'INCOMING CASK', font=font(18, mono=True), fill=quiet)
    d.text((30, 112), 'W-042', font=font(51, mono=True), fill=lit)
    d.text((478, 105), 'SEAL VERIFIED', font=font(25, bold=True), fill=lit)
    d.text((478, 141), 'RECEIPT 042 / SHIFT 04', font=font(17, mono=True), fill=quiet)
    d.line((30, 181, 770, 181), fill=line, width=2)
    rows = [('REGISTRY', 'MATCH'), ('DOSE CHECK', 'COMPLETE'), ('DESTINATION', 'A2 / SHIELDED')]
    for index, (label, value) in enumerate(rows):
        y = 204 + index * 52
        d.text((34, y), label, font=font(23, mono=True), fill=quiet)
        d.text((363, y), value, font=font(24, mono=True), fill=lit)
        d.line((34, y + 38, 764, y + 38), fill=(30, 48, 36), width=1)
    d.rectangle((30, 385, 770, 450), outline=line, width=2)
    d.text((50, 400), 'AWAITING OPERATOR RELEASE', font=font(26, bold=True), fill=lit)
    d.text((34, 469), 'F1  INSPECT', font=font(15, mono=True), fill=quiet)
    d.text((286, 469), 'F2  HOLD', font=font(15, mono=True), fill=quiet)
    d.text((531, 469), 'F3  RELEASE', font=font(15, mono=True), fill=quiet)
    im.save(ROOT / 'inventory-screen.png')


def dial():
    # Draw at double resolution for printed edges; needle remains real geometry.
    size, c = 1024, 512
    im = Image.new('RGB', (size, size), (216, 208, 177))
    d = ImageDraw.Draw(im)
    ink = (48, 50, 43)
    d.ellipse((49, 49, 975, 975), outline=(150, 146, 125), width=3)
    def xy(deg, radius):
        a = math.radians(deg)
        return (c + radius * math.cos(a), c + radius * math.sin(a))
    for index in range(51):
        angle = 140 + 260 * index / 50
        major = index % 5 == 0
        d.line((xy(angle, 423), xy(angle, 368 if major else 399)), fill=ink, width=7 if major else 3)
    for index in range(0, 11, 2):
        angle = 140 + 260 * index / 10
        x, y = xy(angle, 314)
        label = str(index)
        f = font(65)
        bounds = d.textbbox((0, 0), label, font=f)
        d.text((x-(bounds[2]-bounds[0])/2, y-(bounds[3]-bounds[1])/2-bounds[1]), label, fill=ink, font=f)
    def centered(y, text, size):
        f = font(size)
        bounds = d.textbbox((0, 0), text, font=f)
        d.text(((1024-(bounds[2]-bounds[0]))/2, y), text, fill=ink, font=f)
    centered(288, 'AREA DOSE', 40)
    centered(640, 'mSv/h', 69)
    centered(775, 'WS  /  04', 31)
    im.resize((512, 512), Image.Resampling.LANCZOS).save(ROOT / 'dose-dial.png')


if __name__ == '__main__':
    screen()
    dial()
    print('Wrote original inventory-screen.png (800x500) and dose-dial.png (512x512).')
