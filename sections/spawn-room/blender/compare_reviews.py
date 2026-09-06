"""Compare fixed-camera manifests and decoded PNG pixels (Python 3 + Pillow)."""
import argparse,json,math
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
p=argparse.ArgumentParser();p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--cold',action='store_true');a=p.parse_args()
ca=json.loads((a.before/'cameras.json').read_text());cb=json.loads((a.after/'cameras.json').read_text())
rows=[]
for name in ca:
    old=Image.open(a.before/(name+'.png')).convert('RGB');new=Image.open(a.after/(name+'.png')).convert('RGB')
    assert old.size==new.size,(name,old.size,new.size)
    diff=ImageChops.difference(old,new);stat=ImageStat.Stat(diff)
    rows.append({'camera':name,'size':list(old.size),'mean_absolute_8bit':sum(stat.mean)/3,'rms_8bit':math.sqrt(sum(x*x for x in stat.rms)/3),'identical_pixels':diff.getbbox() is None})
same=ca==cb
result={'camera_manifests_identical':same,'purpose':'Cold-start regression' if a.cold else 'Same-camera visual-review evidence; numerical change is not an art score','images':rows}
if a.cold:result['status']='PASS' if same and max(r['mean_absolute_8bit'] for r in rows)<.5 else 'FAIL'
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if not same or (a.cold and result['status']!='PASS'):raise SystemExit(1)
