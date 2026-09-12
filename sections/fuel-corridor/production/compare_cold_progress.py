"""Read-only early pixel check; full manifest-bound comparison remains required."""
from pathlib import Path
from PIL import Image
import numpy as np,json,sys
r=Path(__file__).resolve().parent/'renders/review';rev=sys.argv[1];rows=[]
for p in sorted((r/(rev+'-cold')).glob('*.png')):
 a=np.array(Image.open(r/rev/p.name).convert('RGB'),dtype=np.int16)
 b=np.array(Image.open(p).convert('RGB'),dtype=np.int16);d=np.abs(a-b)
 rows.append({'view':p.stem,'max_255':int(d.max()),'mean_255':float(d.mean()),'within_pixel_threshold':bool(d.max()<=2 and d.mean()<=.02)})
print(json.dumps({'scope':'Partial numeric check only; no complete cold acceptance','views':len(rows),'rows':rows},indent=2))
