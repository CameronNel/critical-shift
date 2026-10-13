"""Package the portable native models and an actual-render presentation sheet."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
SCENE=HERE.parent/'front_end_area_cafeteria_revamp.blend'
FINAL=HERE/'renders'/'final'
CAMERAS=['R8_GAMES_HERO','R8_FOOSBALL_DETAIL','R8_DARTBOARD_DETAIL',
         'R8_BASKETBALL_DETAIL','R8_LOUNGE_HERO','R8_DINING_HERO','R8_COFFEE_DETAIL']

def preview():
    for name in CAMERAS:
        with Image.open(FINAL/(name+'.png')) as image:
            assert image.size==(1600,900),(name,image.size)
            image.verify()
    width,gap=1920,16
    sheet=Image.new('RGB',(width,1230),'#151b25')
    draw=ImageDraw.Draw(sheet)
    title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',27)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
    draw.text((gap,13),'THE RIDGE / CAFETERIA',font=title,fill='#efdcc5')
    draw.text((width-485,21),'Editable scene + separately authored games',font=font,fill='#b4bbc6')
    def cell(path,x,y,w,h,label):
        with Image.open(path) as source:
            im=source.convert('RGB');im.thumbnail((w,h),Image.Resampling.LANCZOS)
            sheet.paste(im,(x+(w-im.width)//2,y+(h-im.height)//2))
        draw.text((x,y+h+6),label,font=font,fill='#e7daca')
    top_w=(width-3*gap)//2;top_h=top_w*9//16
    cell(FINAL/'R8_GAMES_HERO.png',gap,62,top_w,top_h,'Games corner')
    cell(FINAL/'R8_LOUNGE_HERO.png',2*gap+top_w,62,top_w,top_h,'Staff lounge')
    bottom_w=(width-4*gap)//3;bottom_h=bottom_w*5//6;y=62+top_h+50
    for i,(kind,label) in enumerate([('foosball','Foosball'),('dartboard','Dart cabinet'),('basketball','Basketball arcade')]):
        cell(HERE/'renders'/'assets'/(kind+'.png'),gap+i*(bottom_w+gap),y,bottom_w,bottom_h,label)
    draw.text((gap,1194),'Native Blender models. Game assemblies appended and checked in the cafeteria scene.',font=font,fill='#aeb6c1')
    output=FINAL/'presentation.jpg';sheet.save(output,quality=96,subsampling=0)
    return output

def package(output):
    output.mkdir(parents=True,exist_ok=True);cover=preview()
    files={SCENE:SCENE.name,cover:'cafeteria-revamp/renders/final/presentation.jpg'}
    for kind in ('foosball','dartboard','basketball'):
        for suffix in ('.blend','.json'):
            path=HERE/'assets'/(kind+suffix);files[path]='cafeteria-revamp/assets/'+path.name
    for name in ('README.md','TASK_STATE.md','CAMERAS.md','RUBRIC.md','CHECKLIST.md','FONT_LICENSE.txt',
                 'validation_final.json','reimport_report.json','material_consolidation.json'):
        files[HERE/name]='cafeteria-revamp/'+name
    for name in ('review_r5.md','review_r6.md'):
        files[HERE/'critics'/name]='cafeteria-revamp/critics/'+name
    manifest=[{'path':name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path,name in files.items()]
    archive=output/'cafeteria_revamp.zip'
    readme=('Open front_end_area_cafeteria_revamp.blend with Blender 5.2.2 LTS or newer.\n'
            'The three standalone editable game models are in cafeteria-revamp/assets/.\n'
            'Images and fonts are packed; the native files have no linked dependencies.\n'
            'The preview sheet is cafeteria-revamp/renders/final/presentation.jpg.\n'
            'Full rebuild sources and per-camera render history are in the repository\n'
            'on branch codex/cafeteria-detail-revamp; the archive contains native models\n'
            'and brief evidence, rather than that complete historical source checkout.\n'
            'This is a Blender authoring delivery; combined-map and runtime integration are separate.\n')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_STORED) as z:
        for path,name in files.items():z.write(path,name)
        z.writestr('OPEN_ME.txt',readme);z.writestr('MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None,'Archive CRC failure'
        for row in manifest:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256'],row['path']
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'preview':str(cover),'native_models':4,'archive_verified':True},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args();package(a.output.resolve())
