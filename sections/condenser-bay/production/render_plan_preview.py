"""Preview this section's simple measured SVG plan without opening a GPU app."""
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parent.parent
svg=ET.parse(root/'architecture/floorplan.svg').getroot()
im=Image.new('RGB',(int(svg.attrib['width']),int(svg.attrib['height'])),'white')
d=ImageDraw.Draw(im)
for e in svg:
    a=e.attrib;tag=e.tag.rsplit('}',1)[-1]
    if tag=='rect':
        x=float(a.get('x',0));y=float(a.get('y',0));w=float(a['width']);h=float(a['height'])
        fill=a.get('fill');fill=None if fill=='none' else fill
        d.rectangle((x,y,x+w,y+h),fill=fill)
        stroke=a.get('stroke')
        if stroke:
            width=max(1,round(float(a.get('stroke-width',1))))
            dash=[float(v) for v in a.get('stroke-dasharray','').split()]
            if dash:
                for p,q in [((x,y),(x+w,y)),((x+w,y),(x+w,y+h)),((x+w,y+h),(x,y+h)),((x,y+h),(x,y))]:
                    length=abs(q[0]-p[0])+abs(q[1]-p[1]);t=0
                    while t<length:
                        end=min(length,t+dash[0])
                        d.line((p[0]+(q[0]-p[0])*t/length,p[1]+(q[1]-p[1])*t/length,p[0]+(q[0]-p[0])*end/length,p[1]+(q[1]-p[1])*end/length),fill=stroke,width=width)
                        t+=sum(dash)
            else:d.rectangle((x,y,x+w,y+h),outline=stroke,width=width)
    elif tag=='text':
        font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',int(a.get('font-size',14)))
        d.text((float(a['x']),float(a['y'])),e.text or '',font=font,fill=a.get('fill','#222'),anchor='ms' if a.get('text-anchor')=='middle' else 'ls')
    else:raise ValueError('Unsupported SVG element: '+tag)
out=root/'architecture/floorplan-preview.png';im.save(out);print(out)
