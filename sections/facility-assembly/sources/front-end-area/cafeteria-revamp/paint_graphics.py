"""Original albedo graphics, typography and display artwork. No baked lighting."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, random
OUT=Path(__file__).resolve().parent/'textures';OUT.mkdir(parents=True,exist_ok=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
MONO='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
INK=(17,25,39);CREAM=(235,226,200);ORANGE=(223,130,47);RED=(163,56,39)
def font(n,bold=False,mono=False):return ImageFont.truetype(MONO if mono else BOLD if bold else FONT,n)
def txt(d,p,s,n=32,c=CREAM,b=False,a=None):d.text(p,s,font=font(n,b),fill=c,anchor=a)
def save(im,n):im.save(OUT/n)
def plate(n,title,sub,size=(1024,256)):
 im=Image.new('RGB',size,INK);d=ImageDraw.Draw(im);w,h=size
 d.rounded_rectangle((7,7,w-8,h-8),radius=20,outline=(143,143,129),width=4)
 d.rectangle((28,h-30,w-28,h-23),fill=ORANGE)
 txt(d,(w/2,h*.37),title,60,CREAM,True,'mm');txt(d,(w/2,h*.69),sub,23,(164,172,169),False,'mm');save(im,n)
plate('foosball_plate.png','BREAKTIME','TOURNAMENT SERIES  /  SOLID WOOD  /  Nº 01')
plate('basket_marquee.png','SHIFT SHOT','60 SECOND CHALLENGE', (1024,300))
plate('basket_control.png','PRESS TO PLAY','FREE PLAY  •  KEEP HANDS CLEAR', (1024,360))
plate('dart_plaque.png','301 CLUB','HOUSE LEAGUE  /  DOUBLE OUT', (1024,192))
plate('coffee_label.png','SHIFT ROAST','FRESH GROUND  /  HOT COFFEE', (768,256))
plate('game_sign.png','AFTER HOURS','FOOSBALL  /  HOOPS  /  DARTS', (1024,256))
im=Image.new('RGB',(1400,400),INK);d=ImageDraw.Draw(im)
for k in range(5):
 x=720+k*130;d.polygon([(x,400),(x+360,0),(x+420,0),(x+60,400)],fill=RED if k%2 else (39,52,76))
txt(d,(166,195),'01',240,CREAM,True,'mm');txt(d,(358,107),'SHIFT SHOT',89,CREAM,True)
txt(d,(368,259),'60 SECOND CHALLENGE',30,CREAM);save(im,'basket_side.png')
# Chalk score cards on the inside of the open cabinet leaves.
for side,values,deductions in [('left',[301,241,196,136,91,31],[60,45,60,45,60,None]),('right',[301,256,196,156,101,61],[45,60,40,55,40,None])]:
 im=Image.new('RGB',(512,1024),(26,37,34));d=ImageDraw.Draw(im)
 txt(d,(256,72),'HOME' if side=='left' else 'AWAY',42,CREAM,True,'mm');d.line((55,116,455,116),fill=CREAM,width=3)
 for i,v in enumerate(values):
  y=155+i*100;txt(d,(175,y),str(v),50,(208,211,182),False,'mm');txt(d,(359,y),str(deductions[i]) if deductions[i] else '—',31,(160,171,145),False,'mm')
  if i<5:d.line((80,y-12,274,y+12),fill=(177,186,159),width=2)
 txt(d,(256,847),'DOUBLE OUT',22,(167,174,150),False,'mm');d.line((78,888,427,888),fill=(104,128,112),width=2)
 save(im,'chalk_'+side+'.png')
# Kiosk display: a designed cafeteria interface instead of a luminous blank.
im=Image.new('RGB',(768,1024),(229,222,207));d=ImageDraw.Draw(im)
d.rectangle((0,0,768,128),fill=INK);txt(d,(44,61),'SHIFT KITCHEN',43,CREAM,True)
txt(d,(44,193),'Good food.',62,INK,True);txt(d,(44,270),'Short break.',62,INK,True)
txt(d,(44,384),'Choose your lunch',28,(81,85,78))
for i,(s,price) in enumerate([('Soup + bread','3.20'),('Hot lunch','6.50'),('Coffee + pastry','2.80')]):
 y=454+i*125;d.rounded_rectangle((44,y,724,y+98),radius=13,fill=(250,247,237));txt(d,(73,y+31),s,29,INK,True);txt(d,(681,y+31),price,29,INK,False,'ra')
d.rounded_rectangle((44,870,724,960),radius=14,fill=RED);txt(d,(384,915),'START ORDER  →',30,CREAM,True,'mm');save(im,'kiosk_menu.png')
im=Image.new('RGB',(2700,246),INK);d=ImageDraw.Draw(im)
for i,(title,lines) in enumerate([('SOUP + BREAD',[('Tomato & basil','3.20'),('Leek & potato','3.20'),('Fresh bread roll','0.80')]),('HOT LUNCH',[('Pie of the day','6.50'),('Vegetable lasagne','6.20'),('Rice & curry','6.00')]),('DRINKS',[('Fresh coffee','1.80'),('Tea, any blend','1.20'),('Fruit juice','1.50')])]):
 x=39+i*900;txt(d,(x,14),title,41,ORANGE,True)
 for j,(s,p) in enumerate(lines):
  y=82+j*49;txt(d,(x,y),s,33);txt(d,(x+798,y),p,33,CREAM,False,'ra')
 if i<2:d.line((x+840,18,x+840,225),fill=(69,78,82),width=3)
save(im,'menu_board.png')
# Local broadcast still, restrained mountain graphic and an actual information bar.
im=Image.new('RGB',(1600,900),(61,85,102));d=ImageDraw.Draw(im)
d.ellipse((1080,85,1220,225),fill=(228,210,163))
for k,clr in enumerate([(83,106,112),(59,84,95),(35,62,75)]):
 pts=[(-40,460+k*102)]+[(i*145,350+k*105+int(math.sin(i*1.4+k)*89)) for i in range(13)]+[(1700,930),(-40,930)]
 d.polygon(pts,fill=clr)
d.rectangle((0,683,1600,900),fill=INK);txt(d,(52,711),'THE RIDGE',65,CREAM,True);txt(d,(52,808),'LOCAL WEATHER  /  12°C  /  CLEARING BY MORNING',26,CREAM)
d.rectangle((1273,707,1535,765),fill=RED);txt(d,(1404,736),'LIVE',31,CREAM,True,'mm');save(im,'lounge_tv.png')
# Game-area carpet: quiet wool texture, inset stripe and a simple compass motif.
im=Image.new('RGB',(1400,1100),(31,41,65));d=ImageDraw.Draw(im)
for off,col,w in [(25,(87,82,65),8),(47,(144,105,59),4),(64,(53,67,92),4)]:d.rectangle((off,off,1399-off,1099-off),outline=col,width=w)
r=random.Random(51);px=im.load()
for y in range(1100):
 for x in range(1400):
  c=px[x,y];v=r.choice((-2,-1,0,0,0,1,2));px[x,y]=tuple(max(0,min(255,j+v)) for j in c)
save(im,'game_carpet.png')
# A small collection of distinct original prints, selected for specific wall clusters.
im=Image.new('RGB',(900,1200),(218,203,169));d=ImageDraw.Draw(im)
txt(d,(65,67),'STAFF LEAGUE',69,INK,True);txt(d,(65,164),'FRIDAY / 18:00',43,RED,True)
d.ellipse((247,398,653,804),fill=RED)
for a in (0,math.pi/2):
 d.line([(450+203*math.cos(a),601+203*math.sin(a)),(450-203*math.cos(a),601-203*math.sin(a))],fill=INK,width=14)
d.arc((295,398,605,804),80,280,fill=INK,width=10);d.arc((145,457,757,749),-35,35,fill=INK,width=10)
txt(d,(65,934),'HOOPS + DOUBLES',44,INK,True);txt(d,(65,1010),'All shifts welcome.',34,INK);txt(d,(65,1086),'Sign up at the notice board.',25,INK);save(im,'league_poster.png')
im=Image.new('RGB',(1400,900),(176,185,177));d=ImageDraw.Draw(im)
for k,col in enumerate([(145,162,153),(97,122,111),(57,91,80),(32,64,58)]):
 pts=[(0,430+k*91)]+[(i*110,350+k*103+int(math.sin(i*.9+k)*55)) for i in range(14)]+[(1400,900),(0,900)]
 d.polygon(pts,fill=col)
for i in range(11):
 x=80+i*132;y=470+int(math.sin(i)*51);d.polygon([(x,y-144),(x-45,y),(x+45,y)],fill=(43,75,68));d.rectangle((x-3,y-35,x+3,y+112),fill=(43,75,68))
txt(d,(55,47),'THE NORTH RIDGE',31,INK,True);save(im,'ridge_print.png')
im=Image.new('RGB',(1400,900),(217,202,174));d=ImageDraw.Draw(im)
for j in range(12):
 pts=[(x,130+j*54+30*math.sin(x/180+j*.27)+17*math.cos(x/110)) for x in range(0,1400,12)]
 d.line(pts,fill=(76,105,99) if j%3 else (153,95,57),width=4)
d.ellipse((965,141,1124,300),fill=(190,116,54));txt(d,(60,58),'RIDGE TRAILS / FIELD STUDY 04',28,INK,True);save(im,'contour_print.png')
print('PAINTED',len(list(OUT.glob('*.png'))),'original textures')
