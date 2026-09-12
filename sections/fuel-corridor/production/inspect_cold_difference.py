"""Locate actual RGB differences without changing acceptance thresholds."""
from pathlib import Path
from PIL import Image
import numpy as np,json,sys
r=Path(__file__).resolve().parent
rev=sys.argv[1] if len(sys.argv)>1 else 'final-F05';cam=sys.argv[2] if len(sys.argv)>2 else 'C08_SERVICE_JUNCTION'
a=np.array(Image.open(r/f'renders/review/{rev}/{cam}.png').convert('RGB'),dtype=np.int16)
b=np.array(Image.open(r/f'renders/review/{rev}-cold/{cam}.png').convert('RGB'),dtype=np.int16)
d=np.abs(a-b);m=d.max(axis=2);ys,xs=np.where(m>2)
out=r/'evidence/final-pass'
report={'over_2_pixels':len(xs),'bbox_xyxy':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())], 'histogram':{str(i):int((m==i).sum()) for i in range(int(m.max())+1)}}
boxes=[]
for y in range(0,960,120):
 for x in range(0,1440,120):
  count=int((m[y:y+120,x:x+120]>2).sum())
  if count:boxes.append({'xy':[x,y],'pixels_over_2':count})
report['tiles']=boxes
stem=rev+'-'+cam
(out/(stem+'-cold-difference.json')).write_text(json.dumps(report,indent=2))
Image.fromarray(np.uint8(np.clip(d*30,0,255))).save(out/(stem+'-cold-difference-x30.png'))
print(json.dumps(report))
