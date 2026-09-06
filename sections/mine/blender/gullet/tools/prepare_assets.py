"""Author the supplied original geology and texture assets.
Offline authoring utility, not a Blender dependency. Requires numpy,
scikit-image and Pillow. The Blender entrypoint consumes the generated NPZ/PNG.
All cut values below are fictional gameplay indices, not engineering data.
"""
from pathlib import Path
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from skimage.measure import marching_cubes
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'; TEX=ROOT/'textures'
ASSETS.mkdir(exist_ok=True); TEX.mkdir(exist_ok=True)
SEED=92026
SLOPE=.025
# Each segment is an authored excavated volume, not a visible primitive.
# Smooth unions and a layered displacement field form a single geological skin.
SEGMENTS=[
 ((0,-2),(0,11),3.18,2.38,1.78),
 ((0,11),(0,26),3.42,2.48,1.82),
 ((0,26),(0,39),3.12,2.35,1.78),
 ((2.6,12),(7.8,14.5),1.46,1.9,1.23),
 ((7.8,14.5),(9.0,22),1.57,1.94,1.28),
 ((9.0,22),(7.5,27.1),1.58,1.94,1.28),
 ((7.5,27.1),(2.6,28.3),1.48,1.9,1.23),
 ((8.5,20.3),(9.1,22.6),2.65,2.05,1.35),
 ((-2.2,17.8),(-6.7,17.8),1.62,1.93,1.25),
 ((-6.1,17.8),(-10.6,17.8),2.35,2.15,1.43),
 ((-10,17.8),(-13.7,17.8),3.05,2.6,1.72),
 ((-12.9,17.7),(-16.6,20.1),1.70,2.05,1.32),
 ((-12.6,16.8),(-15.2,13.9),1.50,1.90,1.22),
 ((2.3,33),(6.5,33),1.70,1.94,1.26),
 ((6.0,33),(10.6,33),2.40,2.30,1.50),
 ((10.1,33),(14,33.6),3.05,2.54,1.70),
 ((12.6,34),(15.7,37.4),1.80,2.15,1.40),
 ((0,37),(0,43),2.65,2.42,1.63),
 ((0,42),(0,47.5),3.20,2.85,1.90),
 ((0,47),(0,52.0),4.45,3.25,2.17),
 ((-2,51),(-6.6,54.2),2.1,2.40,1.6),
 ((2,51),(6.4,54.7),2.30,2.5,1.68),
]
def floor_z(y): return -SLOPE*np.maximum(y,0.)
def field(x,y,z):
 out=None
 for a,b,r,h,zc in SEGMENTS:
  vx,vy=b[0]-a[0],b[1]-a[1]
  t=np.clip(((x-a[0])*vx+(y-a[1])*vy)/(vx*vx+vy*vy),0,1)
  dx=x-(a[0]+t*vx); dy=y-(a[1]+t*vy)
  rr=np.sqrt(dx*dx+dy*dy)/r
  zz=np.abs((z-floor_z(y)-zc)/h)
  d=(np.power(np.power(rr,2.65)+np.power(zz,2.65),1/2.65)-1)*min(r,h)
  if out is None: out=d
  else:
   k=.38; q=np.maximum(k-np.abs(out-d),0)/k
   out=np.minimum(out,d)-q*q*k*.25
 displacement=(.16*np.sin(.72*x+.25*y+.61*z)
             +.095*np.sin(1.42*y-.67*x+1.8*z)
             +.065*np.sin(3.45*z+.31*x+.19*y)
             +.030*np.sin(5.1*x+2.33*y+1.6*z))
 return out+displacement

def geology():
 step=.21
 xs=np.arange(-20.8,20.8,step,dtype=np.float32)
 ys=np.arange(-1.2,60.1,step,dtype=np.float32)
 zs=np.arange(-4.2,8,step,dtype=np.float32)
 x,y,z=xs[:,None,None],ys[None,:,None],zs[None,None,:]
 f=field(x,y,z).astype(np.float32)
 v,faces,n,val=marching_cubes(f,0,spacing=(step,step,step),allow_degenerate=False)
 v+=np.array([xs[0],ys[0],zs[0]])
 tri=v[faces]; nn=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); nn/=np.maximum(np.linalg.norm(nn,axis=1)[:,None],1e-8)
 cc=tri.mean(axis=1); sample=np.arange(0,len(faces),max(1,len(faces)//250)); test=cc[sample]+nn[sample]*.045
 if np.mean(field(test[:,0],test[:,1],test[:,2]))>0: faces=faces[:,::-1]
 tri=v[faces]
 keep=np.any(tri[:,:,2]>floor_z(tri[:,:,1])-.12,axis=1)&np.all(tri[:,:,1]>=.65,axis=1)
 faces=faces[keep]; used,inv=np.unique(faces,return_inverse=True); v=v[used]; faces=inv.reshape(-1,3).astype(np.int32)
 payload={'cave_vertices':v.astype(np.float32),'cave_faces':faces}
 sx=.30; xx=np.arange(-20.7,20.8,sx); yy=np.arange(-1.2,60,sx)
 X,Y=np.meshgrid(xx,yy,indexing='ij'); F=floor_z(Y); Z=F+.018*np.sin(2.5*X+.2*Y)*np.sin(.6*Y); Z=np.where(np.abs(X)<1.1,F,Z)
 valid=(field(X,Y,F+.12)<.075)&(Y>=1.0); valid &= ~((X>8.30)&(X<10.60)&(Y>20.0)&(Y<23.1))
 vv=np.column_stack((X.ravel(),Y.ravel(),Z.ravel())).astype(np.float32); ny=len(yy); ff=[]
 for i in range(len(xx)-1):
  for j in range(ny-1):
   if valid[i:i+2,j:j+2].all():
    a=i*ny+j;b=(i+1)*ny+j;c=b+1;d=a+1; ff.extend(((a,b,c),(a,c,d)))
 ff=np.array(ff,dtype=np.int32); used,inv=np.unique(ff,return_inverse=True)
 payload.update(floor_vertices=vv[used],floor_faces=inv.reshape(-1,3).astype(np.int32))
 gates={'A':[(-3.9,17.8),(-7.5,17.8),(-10.9,17.8)],'B':[(3.9,33),(7.6,33),(11,33)],'C':[(0,39.2),(0,43.7),(0,48.0)]}
 for sec,pts in gates.items():
  axis=np.array([-1.,0,0]) if sec=='A' else np.array([1.,0,0]) if sec=='B' else np.array([0,1.,0]); side=np.array([-axis[1],axis[0],0.])
  for level,(cx,cy) in enumerate(pts):
   du=.16; us=np.arange(-(2.8+level*.8) if sec=='B' else -6,(2.8+level*.8+du) if sec=='B' else 6+du,du); ws=np.arange(-.35,7+du,du)
   U,W=np.meshgrid(us,ws,indexing='ij'); base=np.array([cx,cy,float(floor_z(cy))]); plane=base+U[:,:,None]*side+W[:,:,None]*np.array([0,0,1])
   mask=field(plane[:,:,0],plane[:,:,1],plane[:,:,2])<.15
   displacement=.13*np.sin(U*2.7+W*.8)+.065*np.sin(W*5.1-U*.55)+.1*np.sin(U*.6-W*1.4)
   front=plane+displacement[:,:,None]*axis; back=plane+(displacement+.38)[:,:,None]*axis
   vertices=np.concatenate((front.reshape(-1,3),back.reshape(-1,3))); nvert=front.shape[0]*front.shape[1]; nv=len(ws); fs=[]; boundary={}
   for i in range(len(us)-1):
    for j in range(nv-1):
     if mask[i:i+2,j:j+2].any():
      a=i*nv+j;b=(i+1)*nv+j;c=b+1;d=a+1; fs.extend(((a,c,b),(a,d,c),(a+nvert,b+nvert,c+nvert),(a+nvert,c+nvert,d+nvert)))
      for e in [(a,b),(b,c),(c,d),(d,a)]:
       key=tuple(sorted(e))
       if key in boundary: del boundary[key]
       else: boundary[key]=e
   for a,b in boundary.values(): fs.extend(((a,b,b+nvert),(a,b+nvert,a+nvert)))
   fs=np.array(fs,dtype=np.int32); used,inv=np.unique(fs,return_inverse=True)
   payload[f'gate_{sec}{level}_vertices']=vertices[used].astype(np.float32); payload[f'gate_{sec}{level}_faces']=inv.reshape(-1,3).astype(np.int32)
 np.savez_compressed(ASSETS/'geology.npz',**payload)
 stats={k:int(len(a)) for k,a in payload.items()}; (ASSETS/'geology_manifest.json').write_text(json.dumps(stats,indent=2)); print('Geology:',len(v),'vertices;',len(faces),'triangles',flush=True)

PALETTE={'rock':((.36,.385,.365),.89,0),'rock_dark':((.25,.285,.275),.9,0),'rock_fresh':((.48,.495,.455),.91,0),'ground':((.29,.275,.235),.94,0),'concrete':((.53,.545,.50),.86,0),'paint_teal':((.255,.365,.335),.68,.0),'paint_cream':((.70,.72,.65),.66,.0),'paint_ochre':((.66,.45,.20),.66,.0),'paint_red':((.52,.22,.16),.69,.0),'steel':((.29,.325,.33),.46,.82),'dark_steel':((.16,.195,.20),.57,.72),'rubber':((.085,.105,.105),.88,0),'timber':((.265,.215,.15),.89,0),'ore':((.19,.27,.21),.74,.08),'paper':((.80,.775,.65),.85,0),'fabric':((.40,.445,.35),.96,0)}
def textures():
 n=1024; u,v=np.meshgrid(np.linspace(0,2*np.pi,n,endpoint=False),np.linspace(0,2*np.pi,n,endpoint=False)); noise=(np.sin(u+2*v)+.51*np.sin(3*u-v+.7)+.25*np.cos(7*u+5*v)+.13*np.sin(13*u-11*v)+.045*np.cos(37*u+29*v))/1.95
 for name,(col,rough,metal) in PALETTE.items():
  if name.startswith('rock'):
   layer=np.sin(v*8+1.15*np.sin(u)+.5*np.sin(3*u)); height=.5+.15*noise+.055*layer+.015*np.sin(37*v+3*np.sin(u)); mod=.96+.060*noise+.012*layer
  elif name=='timber':
   layer=np.sin(v*22+2*np.sin(u)+np.cos(3*u)); height=.5+.10*noise+.07*layer; mod=.88+.12*noise+.06*layer
  else: height=.5+.08*noise; mod=.96+.045*noise
  rgb=np.stack([np.clip(c*mod,0,1) for c in col],axis=2); Image.fromarray(np.uint8(rgb*255),'RGB').save(TEX/f'{name}_basecolor.png',optimize=True)
  rr=np.clip(rough+noise*(.045 if name not in ['steel','dark_steel'] else .07),.05,1); Image.fromarray(np.uint8(rr*255),'L').save(TEX/f'{name}_roughness.png',optimize=True)
  gx=np.roll(height,-1,axis=1)-np.roll(height,1,axis=1); gy=np.roll(height,-1,axis=0)-np.roll(height,1,axis=0); norm=np.stack((-gx*4,-gy*4,np.ones_like(gx)),axis=2); norm/=np.linalg.norm(norm,axis=2)[:,:,None]
  Image.fromarray(np.uint8((norm*.5+.5)*255),'RGB').save(TEX/f'{name}_normal.png',optimize=True)
 (ASSETS/'materials.json').write_text(json.dumps({k:{'color':c,'roughness':r,'metallic':m} for k,(c,r,m) in PALETTE.items()},indent=2))

FONT_CANDIDATES=['C:/Windows/Fonts/arial.ttf','C:/Windows/Fonts/segoeui.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','DejaVuSans.ttf']
BOLD_CANDIDATES=['C:/Windows/Fonts/arialbd.ttf','C:/Windows/Fonts/seguisb.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','DejaVuSans-Bold.ttf']
def ft(n,bold=False):
 for candidate in (BOLD_CANDIDATES if bold else FONT_CANDIDATES):
  try:return ImageFont.truetype(candidate,n)
  except OSError:pass
 try:return ImageFont.load_default(size=n)
 except TypeError:return ImageFont.load_default()
def poster():
 W,H=2048,1536; im=Image.new('RGB',(W,H),(205,205,183)); d=ImageDraw.Draw(im); ink=(31,48,45); muted=(87,99,87); orange=(169,104,33)
 d.rectangle((0,0,W,205),fill=ink); d.text((76,48),'GULLET / SHIFT CARD',font=ft(86,True),fill=(233,227,204)); d.text((80,243),'01   READ THE FACE. LEAVE A WAY BACK.',font=ft(47,True),fill=ink); d.line((80,321,1968,321),fill=muted,width=3)
 d.rounded_rectangle((80,363,620,954),radius=7,outline=muted,width=4); d.text((112,390),'WORKING ROUTE',font=ft(34,True),fill=ink); points=[(350,860),(350,750),(350,640),(350,525)]; d.line(points,fill=ink,width=12); d.line((350,710,190,710),fill=ink,width=8); d.line((350,625,490,625),fill=ink,width=8); d.line([(350,770),(495,740),(530,680),(495,610),(350,580)],fill=muted,width=7)
 for xy in [(350,860),(190,710),(490,625),(350,525)]: d.ellipse((xy[0]-13,xy[1]-13,xy[0]+13,xy[1]+13),fill=orange)
 for xy,text in [((185,895),'GATE / BAY'),((115,735),'A'),((515,630),'B'),((380,498),'C')]:d.text(xy,text,font=ft(30,True),fill=ink)
 d.text((704,365),'CUT INDEX',font=ft(57,True),fill=ink); d.text((704,443),'game tokens x face response',font=ft(42),fill=ink); d.text((704,504),'Fictional game values. No physical units.',font=ft(28),fill=muted)
 bands=[('1 - 2','SHALLOW POCKET'),('3 - 4','EXTENDED CHAMBER'),('5 - 6','DEEP SEAM'),('7 +','COLLAPSE / CLEAR RUBBLE')]
 for i,(a,b) in enumerate(bands):
  y=583+i*92; d.rectangle((704,y,844,y+64),fill=orange if i==3 else ink); d.text((721,y+8),a,font=ft(33,True),fill=(239,233,207)); d.text((880,y+9),b,font=ft(31,True),fill=ink)
 d.line((80,1014,1968,1014),fill=muted,width=3); d.text((80,1060),'CHECK SUPPORT  /  CLEAR CREW  /  CLOSE GATE',font=ft(42,True),fill=ink); d.text((80,1150),'Oversized cuts do not reward you with a clear chamber.',font=ft(39),fill=ink); d.text((80,1210),'Remove the fall before returning to the seam.',font=ft(39),fill=ink); d.rectangle((0,1385,W,H),fill=ink); d.text((80,1431),'CRITICAL SHIFT   /   SIMULATION ONLY   /   FORM M-01',font=ft(34),fill=(230,223,199)); im.save(TEX/'shift_card.png')
 labels=[('portal','01 / GULLET'),('magazine','CHARGE ISSUE'),('return','FACILITY / INTAKE'),('pump','SUMP / SERVICE'),('cart','TARE  /  CS-04'),('door','GATE CONTROL'),('sector_a','A / DRY SEAM'),('sector_b','B / WET SEAM'),('sector_c','C / DEEP CUT')]
 for name,txt in labels:
  im=Image.new('RGB',(1024,224),ink); d=ImageDraw.Draw(im); d.rectangle((0,0,28,224),fill=orange); font=ft(74,True)
  while d.textbbox((0,0),txt,font=font)[2]>910:font=ft(font.size-2,True)
  bb=d.textbbox((0,0),txt,font=font); th=bb[3]-bb[1]; d.text((66,(224-th)/2-bb[1]),txt,font=font,fill=(224,222,193)); im.save(TEX/f'label_{name}.png')
 n=512; rng=np.random.default_rng(81); im=Image.new('RGBA',(n,n),(0,0,0,0));d=ImageDraw.Draw(im)
 for i in range(48):
  x=int(rng.integers(30,480));y=int(rng.integers(25,485));rx=int(rng.integers(3,18));ry=int(rng.integers(7,36)); d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=(48,44,35,int(rng.integers(12,40))))
 im=im.filter(ImageFilter.GaussianBlur(2));im.save(TEX/'localized_scuff.png'); print('Textures and original signage authored.',flush=True)
if __name__=='__main__':
 textures();poster();geology()
