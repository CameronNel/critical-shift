"""Cooling side rainscreen; original front plane and 5m portal remain untouched."""
olive=mat('EXT cooling olive folded panel',(.19,.205,.14),.60,.32)
paper=mat('EXT cooling service record',(.67,.64,.52),.9)
def side(a,b,x,z0,z1,normal=1):
 n=max(1,round((b-a)/2.35))
 for i in range(n):
  y=a+(i+.5)*(b-a)/n;w=(b-a)/n-.015
  box('Cooling side mineral bay',(x+normal*.025,y,(z0+z1)/2),(.05,w,z1-z0),cream)
  if z0==0:box('Cooling low splash plinth',(x+normal*.055,y,.22),(.06,w,.44),base)
side(.06,13,-5.8,0,5.8,-1)
for a,b,z0,z1 in [(.06,5.5,0,5.8),(5.5,6.1,0,2.7),(5.5,6.1,3.3,5.8),(6.1,7.55,0,5.8),(7.55,8.15,0,3),(7.55,8.15,3.6,5.8),(8.15,9.7,0,5.8),(9.7,10.3,.25,5.8),(10.3,13,0,5.8)]:side(a,b,5.8,z0,z1)
for x,sgn in [(-5.8,-1),(5.8,1)]:
 box('Cooling folded upper field',(x+sgn*.069,6.65,5.29),(.044,13.18,1.02),olive,.005)
 box('Cooling upper drip sill',(x+sgn*.08,6.65,4.765),(.11,13.18,.04),steel,.004)
 box('Cooling roof edge flashing',(x+sgn*.04,6.65,6.02),(.16,13.18,.12),steel,.004)
 box('Cooling roof edge vertical fascia',(x+sgn*.025,6.65,5.94),(.05,13.18,.28),steel,.004)
 for y in [.12,13.18]:box('Cooling corner cover strip',(x+sgn*.075,y,2.9),(.08,.18,5.8),steel,.006)
 for y in [2.3,4.6,6.9,9.2,11.5]:box('Cooling upper panel seam',(x+sgn*.098,y,5.29),(.014,.025,1.02),steel,.002)
for i in range(5):
 x=-5.8+(i+.5)*11.6/5
 box('Cooling rear mineral bay',(x,13.325,2.9),(11.6/5-.016,.05,5.8),cream)
 box('Cooling rear splash base',(x,13.355,.22),(11.6/5-.016,.06,.44),base)
box('Cooling rear upper folded field',(0,13.369,5.29),(11.6,.044,1.02),olive,.004)
box('Cooling rear roof flashing',(0,13.32,6.02),(11.82,.16,.12),steel,.004)
box('Cooling rear vertical roof fascia',(0,13.325,5.94),(11.6,.05,.28),steel,.004)
text('Cooling exterior title','COOLING PLANT',(-5.853,5.3,3.95),.34)
bpy.data.objects['Cooling exterior title'].rotation_euler.z=-math.pi/2
# Weatherproof record case on west side, carried by two continuous mounting rails.
for y in [2.12,2.62]:box('Cooling case mounting rail',(-5.885,y,1.7),(.08,.08,.87),steel,.006)
box('Cooling service case',(-5.985,2.37,1.7),(.14,.65,.78),steel)
box('Cooling service case folded lid',(-5.99,2.37,2.105),(.18,.70,.035),steel,.004)
box('Cooling case door face',(-6.062,2.37,1.70),(.014,.59,.69),base,.005)
for z in [1.45,1.92]:box('Cooling case hinge',(-6.081,2.10,z),(.035,.045,.10),steel,.003)
rod('Cooling case latch spindle',(-6.063,2.59,1.7),(-6.105,2.59,1.7),.018,ivory)
rod('Cooling case latch lever',(-6.105,2.59,1.64),(-6.105,2.59,1.74),.012,ivory)
box('Cooling record label',(-6.072,2.37,1.86),(.004,.36,.12),ivory,.0008)
camera_specs=[('FRONT',(0,-20,3.5),(0,0,3)),('OBLIQUE',(-22,-20,10),(0,6.5,3)),('REVERSE',(22,32,10),(0,6.5,3)),('DETAIL',(-10,-.2,1.8),(-5.9,2.37,1.7))]
