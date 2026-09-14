"""Subgrade condenser facade. No added roof, floor or connector geometry."""
concrete=mat('EXT condenser cast mineral',(.40,.395,.36),.88)
ochre=mat('EXT condenser service ochre',(.43,.29,.075),.75)
paper=mat('EXT condenser maintenance card',(.65,.62,.52),.9)
def formed(a,b,plane,z0,z1,axis='Y',normal=-1):
 n=max(1,round((b-a)/2.6))
 for i in range(n):
  c=a+(i+.5)*(b-a)/n;w=(b-a)/n-.012
  for lo,hi in [(z0,min(z1,.65)),(max(z0,.662),z1)]:
   if hi<=lo:continue
   loc=(c,plane+normal*.023,(lo+hi)/2);size=(w,.046,hi-lo)
   if axis=='X':loc=(loc[1],loc[0],loc[2]);size=(size[1],size[0],size[2])
   box('Condenser formed concrete lift',loc,size,base if hi<=.65 else concrete,.004)
  for z in [1.15,3.8]:
   if z0+.15<z<z1-.15:
    for u in [-w*.34,w*.34]:
     a1=(c+u,plane+normal*.043,z);b1=(c+u,plane+normal*.049,z)
     if axis=='X':a1=(a1[1],a1[0],z);b1=(b1[1],b1[0],z)
     rod('Condenser flush form tie plug',a1,b1,.023,base)
formed(-1.8,-1.47,-.28,0,5.1);formed(1.47,9.6,-.28,0,5.1)
formed(-1.47,1.47,-.28,2.95,5.1)
formed(-.14,9.54,-2.08,0,5.1,'X',-1)
# East water flanges and low drain remain exposed through generous local windows.
for a,b,z0,z1 in [(-.14,2.80,0,5.1),(2.80,3.60,0,2.75),(2.80,3.60,3.55,5.1),(3.60,4.50,0,5.1),(4.50,5.30,0,2.75),(4.50,5.30,3.55,5.1),(5.30,8.20,0,5.1),(8.20,8.90,.30,5.1),(8.90,9.54,0,5.1)]:formed(a,b,9.88,z0,z1,'X',1)
formed(-2.08,9.88,9.68,0,5.1,'Y',1)
for x,sgn in [(-1.46,-1),(1.46,1)]:formed(-2.50,-.30,x,0,2.7,'X',sgn)
# Closed source stub end remains untouched for future connector removal.
box('Condenser maintenance board',(2.2,-.35,1.65),(.56,.094,.64),steel)
box('Condenser card',(2.2,-.402,1.72),(.44,.01,.41),paper,.002)
box('Condenser card lower pocket',(2.2,-.418,1.46),(.48,.03,.18),steel,.005)
box('Condenser retaining clip',(2.2,-.414,1.935),(.13,.03,.055),ochre,.004)
for z in [1.82,1.74,1.66]:box('Condenser ruled record',(2.2,-.409,z),(.34,.003,.004),steel,.0005)
text('Condenser external identification','CONDENSER BAY',(5.3,-.328,3.45),.5)
ob=bpy.data.objects['Condenser external identification'];ob.rotation_euler.z=0;ob.data.materials.clear();ob.data.materials.append(ochre)
camera_specs=[('FRONT',(3.9,-19,3.5),(3.9,0,3)),('OBLIQUE',(-17,-20,10),(3.9,4.7,3)),('REVERSE',(25,25,10),(3.9,4.7,3)),('DETAIL',(4.3,-5,1.8),(2.2,-.3,1.7))]
