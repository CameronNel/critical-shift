"""Spawn's stepped briefing/locker/service volumes; executed by build_exteriors."""
olive=mat('EXT locker olive rainscreen',(.19,.21,.145),.56,.35)
paper=mat('EXT shift paper',(.67,.63,.50),.9)
def sy(a,b,y,h,normal=-1,metal=False,z0=0):
 n=max(1,round((b-a)/globals().get('PANEL_WIDTH',1.55)));depth=.05
 for i in range(n):
  x=a+(i+.5)*(b-a)/n;w=(b-a)/n-.016
  box('Spawn mineral wall panel',(x,y+normal*.025,(h+z0)/2),(w,depth,h-z0),cream)
  ph=globals().get('PLINTH_HEIGHT',.44)
  if z0==0:box('Spawn low concrete skirt',(x,y+normal*.054,ph/2),(w,.06,ph),base)
  if metal:
   box('Locker folded metal panel',(x,y+normal*.058,(h+1.1)/2),(w,.038,h-1.1),olive,.006)
   for u in [-w/2+.035,w/2-.035]:box('Locker standing rib',(x+u,y+normal*.086,(h+1.1)/2),(.026,.025,h-1.1),steel,.003)
 box('Spawn coping',( (a+b)/2,y,h+globals().get('COPING_BASE_OFFSET',.05)+.06),(b-a+.10,.20,.12),steel)
def sx(a,b,x,h,normal=1,metal=False):
 before=set(ext.objects);sy(a,b,0,h,normal,metal)
 for ob in set(ext.objects)-before:
  old=ob.location.copy();ob.location=(x+old.y,old.x,old.z);ob.rotation_euler.z=math.pi/2
# Exterior surfaces follow each existing wing, never the bounding rectangle.
sy(-7.3,-2.31,.839,3.4)
sy(1.86,8.1,.539,3.8,metal=True)
sx(.84,6.26,-7.462,3.4,-1)
sy(-7.3,-1.86,6.262,3.4,1)
sx(.54,7.46,8.262,3.8,1,True)
sy(1.86,8.1,7.462,3.8,1,True)
sy(-1.7,-.66,-.501,3.4);sy(.66,1.7,-.501,3.4)
box('Entry concrete lintel',(0,-.527,2.93),(1.32,.05,.94),cream)
box('Entry top continuous coping',(0,-.51,3.51),(3.52,.22,.12),steel)
for x,sign,lo in [(-1.862,-1,6.26),(1.862,1,7.46)]:sx(lo,12.30,x,3.4,sign)
# Preserve central rear connection cap as supplied; dress only flanking edges/top.
for x in [-1.7405,1.7405]:box('Service rear corner flashing',(x,12.47,1.7),(.08,.04,3.4),steel,.004)
box('Service rear top coping',(0,12.47,3.51),(3.52,.22,.12),steel)
for name,a,b,z in [('Hall',(-1.78,-.575),(1.78,9.375),3.56),('Briefing',(-7.38,.84),(-1.78,6.26),3.56),('Locker',(1.7,.54),(8.26,7.46),3.96),('Service',(-1.75,9.4),(1.75,12.4),3.56)]:
 box(name+' exterior opaque roof membrane',((a[0]+b[0])/2,(a[1]+b[1])/2,z+.004),(b[0]-a[0],b[1]-a[1],.008),base,.001)
for a,b,y,h in [(-7.3,-2.31,.839,3.4),(1.86,8.1,.539,3.8)]:
 x=a+.16 if a<0 else b-.16
 rod('Spawn rain leader',(x,y-.15,.09),(x,y-.15,h+.11),.05,steel)
 rod('Spawn drain shoe',(x,y-.15,.09),(x,y-.28,.06),.05,steel)
 for z in [.3,1.6,h-.3]:box('Rain leader strap',(x,y-.1,z),(.15,.14,.055),steel,.003)
 # Bracketed roof outlet returns to the coping.
 rod('Rain leader roof elbow',(x,y-.15,h+.10),(x,y,h+.10),.05,steel)
# A shallow hood over the unchanged narrow staff door; clear height stays 2.45 m.
box('Shift entry folded canopy',(0,-.72,3.26),(2.95,.44,.065),steel)
box('Shift entry canopy fascia',(0,-.93,3.19),(2.95,.04,.15),steel)
for x in [-1.28,1.28]:
 box('Entry canopy bearing',(x,-.55,3.0),(.10,.06,.52),steel)
 rod('Entry canopy brace',(x,-.58,2.78),(x,-.89,3.23),.025,steel)
def st(name,body,loc,size):
 text(name,body,loc,size);ob=bpy.data.objects[name];ob.rotation_euler.z=0;ob.data.materials.clear();ob.data.materials.append(steel)
st('Shift entry external title','SHIFT ENTRY',(0,-.565,2.66),.16)
em=mat('EXT entry warm glass',(.71,.56,.31),.35);pr=em.node_tree.nodes.get('Principled BSDF');pr.inputs['Emission Color'].default_value=(1,.76,.42,1);pr.inputs['Emission Strength'].default_value=2
for x in [-1.16,1.16]:
 box('Entry sconce backing',(x,-.55,2.39),(.15,.045,.31),steel)
 box('Entry sconce glass',(x,-.61,2.39),(.12,.10,.22),em)
 for z in [2.29,2.39,2.49]:box('Entry sconce guard',(x,-.67,z),(.15,.018,.016),steel,.002)
 ld=bpy.data.lights.new('Shift entry pool','AREA');ld.energy=12;ld.color=(1,.8,.58);ld.size=.18;lo=bpy.data.objects.new(ld.name,ld);ext.objects.link(lo);lo.location=(x,-.69,2.34);lo.rotation_euler=(0,0,0)
box('Shift reader',(1.05,-.57,1.36),(.14,.09,.27),steel)
box('Reader tactile button',(1.05,-.619,1.31),(.05,.008,.05),base,.003)
# Original briefing-wing wall supports a weather notice case and four human-use items.
box('Shift notice weather case',(-3.1,.77,1.59),(1.1,.12,.84),steel)
box('Notice cork backing',(-3.1,.699,1.59),(.98,.035,.72),base)
for x,z,w,h in [(-3.36,1.65,.33,.47),(-2.96,1.69,.25,.36),(-2.96,1.38,.25,.17)]:
 box('Shift pinned sheet',(x,.675,z),(w,.007,h),paper,.001)
 rod('Paper retaining pin',(x,.667,z+h/2-.025),(x,.657,z+h/2-.025),.013,accent)
st('Shift notice title','SHIFT NOTICE',(-3.36,.668,1.78),.036)
for z in [1.67,1.59,1.51]:box('Notice printed rule',(-3.36,.667,z),(.25,.004,.004),steel,.001)
box('Notice case drip hood',(-3.1,.69,2.05),(1.2,.31,.035),steel,.003)
box('Found property shelf',(1.1,-.63,1.09),(.46,.25,.23),steel)
box('Folded recovered notebook',(1.09,-.64,1.24),(.27,.14,.045),paper,.005)
rod('Found pencil',(.98,-.62,1.27),(1.21,-.64,1.27),.007,accent)
st('Found property label','FOUND',(1.1,-.759,1.08),.055)
camera_specs=[('FRONT',(.4,-20.7,2.22),(.4,5.6,1.81)),('OBLIQUE',(-21,-20,10),(.4,5.6,1.7)),('REVERSE',(21,32,10),(.4,5.6,1.7)),('DETAIL',(-2.2,-5,1.65),(-.6,.2,1.7))]
