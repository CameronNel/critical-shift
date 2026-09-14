"""Mine handoff exterior only. Original rock, canopy and transition closures preserved."""
slate=mat('EXT mine slate coating',(.105,.12,.125),.66,.3)
paper=mat('EXT mine shift card',(.62,.59,.49),.9)
for a,b in [(-7.9,-2.63),(2.63,7.9)]:
 n=4
 for i in range(n):
  x=a+(i+.5)*(b-a)/n;w=(b-a)/n-.014
  box('Mine handoff mineral panel',(x,-20.395,1.15),(w,.05,2.3),cream,.006)
  box('Mine handoff slate panel',(x,-20.395,3.65),(w,.05,2.7),slate,.006)
  box('Mine orange exterior datum',(x,-20.424,2.45),(w,.008,.18),accent,.001)
  for dx in [-w/2+.07,w/2-.07]:
   for z in [.18,2.12,2.78,4.84]:rod('Mine exterior panel bolt',(x+dx,-20.420,z),(x+dx,-20.434,z),.018,ivory)
 box('Mine handoff folded top',((a+b)/2,-20.37,4.96),(b-a,.22,.08),steel,.004)
for x,sgn in [(-2.62,-1),(2.62,1)]:
 for a,b in [(-22,-20.48),(-20.08,-14)]:
  n=max(1,round((b-a)/1.7))
  for i in range(n):
   y=a+(i+.5)*(b-a)/n;w=(b-a)/n-.015
   box('Mine transition mineral lower',(x+sgn*.025,y,.65),(.05,w,1.3),cream,.006)
   box('Mine transition slate upper',(x+sgn*.025,y,2.55),(.05,w,2.5),slate,.006)
   box('Mine transition orange datum',(x+sgn*.054,y,1.42),(.008,w,.16),accent,.001)
  box('Mine transition top edge',(x+sgn*.03,(a+b)/2,3.76),(.16,b-a,.08),steel,.004)
text('Mine exterior identification','GULLET MINE',(5.25,-20.423,3.3),.38);bpy.data.objects['Mine exterior identification'].rotation_euler.z=0
box('Mine shift record case',(6.8,-20.475,1.65),(.62,.11,.74),slate)
box('Mine shift record face',(6.8,-20.535,1.65),(.53,.012,.63),steel,.004)
box('Mine shift card',(6.8,-20.543,1.68),(.39,.004,.47),paper,.001)
for x in [6.555,7.045]:
 for z in [1.38,1.92]:rod('Mine case retaining screw',(x,-20.542,z),(x,-20.555,z),.020,ivory)
box('Mine record lower retaining lip',(6.8,-20.551,1.43),(.42,.018,.07),accent,.002)
camera_specs=[('FRONT',(0,-45,7),(0,-17,3)),('OBLIQUE',(-23,-38,14),(0,-13,3)),('REVERSE',(25,-5,13),(0,-18,3)),('DETAIL',(9,-25,1.8),(6.8,-20.4,1.65))]
