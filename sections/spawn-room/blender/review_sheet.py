"""Lossless-source contact sheet for visual QA; originals remain unchanged."""
import argparse,math
from pathlib import Path
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
files=sorted(a.directory.glob('VALIDATE_*.png'));assert files
w,h=480,324;sheet=Image.new('RGB',(w*3,h*math.ceil(len(files)/3)),(27,33,32));draw=ImageDraw.Draw(sheet)
for i,path in enumerate(files):
    x=(i%3)*w;y=(i//3)*h;im=Image.open(path).convert('RGB');im.thumbnail((w,300),Image.Resampling.LANCZOS)
    sheet.paste(im,(x,y));draw.text((x+8,y+305),path.stem,fill=(228,227,213))
a.output.parent.mkdir(parents=True,exist_ok=True);sheet.save(a.output);print(a.output)
