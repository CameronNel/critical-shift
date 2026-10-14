"""Make inspectable fixed-camera contact sheets and same-camera pixel comparisons."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

FIXED = [
    'CAF_01_ENTRY_NORTH', 'CAF_02_DINING', 'CAF_03_SERVING',
    'CAF_04_LOUNGE', 'CAF_05_GAME_CORNER', 'FE_05_CAFE_REVERSE_NORTH_TO_SOUTH',
    'CAF_X1_AIRLOCK_DOOR', 'CAF_X2_YARD_DOOR', 'CAF_X3_MEDICAL_DOOR',
]
HERO = ['R8_GAMES_HERO', 'R8_LOUNGE_HERO', 'R8_COFFEE_DETAIL', 'R8_DINING_HERO']

def sheet(folder, names, columns, output, title):
    cell_w, cell_h, caption_h, gutter = 480, 270, 28, 12
    rows = (len(names) + columns - 1) // columns
    canvas = Image.new('RGB', (columns*(cell_w+gutter)+gutter, rows*(cell_h+caption_h+gutter)+52), '#151b25')
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    draw.text((gutter, 12), title, font=font, fill='#efdbc3')
    for i, name in enumerate(names):
        x = gutter + i%columns*(cell_w+gutter); y = 44 + i//columns*(cell_h+caption_h+gutter)
        with Image.open(folder/(name+'.png')) as source:
            im = source.convert('RGB'); im.thumbnail((cell_w,cell_h), Image.Resampling.LANCZOS)
            canvas.paste(im, (x+(cell_w-im.width)//2,y+(cell_h-im.height)//2))
        draw.text((x,y+cell_h+4), name, font=font, fill='#dfd7ca')
    canvas.save(folder/output, quality=95)

def compare(current, previous):
    results = []
    for name in FIXED+HERO:
        before, after = previous/(name+'.png'), current/(name+'.png')
        if not before.exists() or not after.exists():
            continue
        with Image.open(before) as a, Image.open(after) as b:
            a, b = a.convert('RGB'), b.convert('RGB')
            if a.size != b.size:
                results.append({'camera':name, 'comparable':False, 'reason':'resolution differs'})
                continue
            delta = ImageChops.difference(a,b); channels = delta.split()
            maximum = ImageChops.lighter(ImageChops.lighter(channels[0],channels[1]),channels[2])
            results.append({'camera':name, 'comparable':True, 'pixel_identical':a.tobytes()==b.tobytes(),
                            'mean_absolute_rgb_delta_255':sum(ImageStat.Stat(delta).mean)/3,
                            'changed_pixels':a.width*a.height-maximum.histogram()[0],
                            'maximum_channel_delta_255':maximum.getextrema()[1]})
    (current/'comparison.json').write_text(json.dumps({'previous':str(previous),'current':str(current),'images':results},indent=2)+'\n')

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('--compare',type=Path);a=p.parse_args()
    sheet(a.folder,FIXED,3,'contact_sheet.jpg','Cafeteria — fixed camera review')
    if all((a.folder/(n+'.png')).exists() for n in HERO):
        sheet(a.folder,HERO,2,'hero_contact_sheet.jpg','Cafeteria — detail and function views')
    if a.compare:compare(a.folder,a.compare)
