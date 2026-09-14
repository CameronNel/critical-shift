"""Turbine long-span facade; four contracted utility envelopes remain unobstructed."""
import ast
for node in ast.parse((ROOT/'blender/exterior_spawn.py').read_text()).body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),'exterior_spawn.py','exec'),globals())
PANEL_WIDTH=2.75;PLINTH_HEIGHT=.28;COPING_BASE_OFFSET=.24
olive=mat('EXT turbine upper folded metal',(.18,.19,.14),.58,.36)
silver=mat('EXT turbine weather hardware',(.32,.33,.30),.46,.70)
paper=mat('EXT turbine handover card',(.64,.60,.47),.88)
sy(-4,-1.21,0,7.2);sy(1.21,7.99,0,7.2)
box('Turbine door overwall skin',(0,-.025,5.03),(2.42,.05,4.34),cream)
# Retain openings around steam inlet and the source-owned condensate return cap.
for a,b,z0,z1 in [(7.99,8.81,0,4.48),(7.99,8.81,5.32,7.2),(8.81,9.18,0,7.2),(9.18,9.82,.78,7.2),(9.82,10,0,7.2)]:
 box('Turbine utility-clear facade',((a+b)/2,-.025,(z0+z1)/2),(b-a,.05,z1-z0),cream)
sx(0,24,-4.251,7.2,-1);sx(0,24,10.251,7.2,1)
sy(-4,-1.21,24.251,7.2,1);sy(1.21,10,24.251,7.2,1)
box('Turbine exit overwall skin',(0,24.276,5.03),(2.42,.05,4.34),cream)
for y in [0,24.25]:box('Turbine end roof coping',(3,y,7.50),(14.6,.24,.12),steel)
for y,sgn in [(0,-1),(24.25,1)]:
 box('Turbine upper rainscreen field',(3,y+sgn*.069,6.29),(14.0,.045,1.82),olive,.006)
 for i in range(21):box('Turbine upper standing seam',(-3.8+i*.68,y+sgn*.103,6.29),(.025,.024,1.82),steel,.003)
 box('Turbine upper band folded sill',(3,y+sgn*.09,5.365),(14.05,.11,.04),steel,.003)
for x,sgn in [(-4.25,-1),(10.25,1)]:
 box('Turbine side upper rainscreen',(x+sgn*.069,12,6.29),(.045,24,1.82),olive,.006)
 for y in [i*1.2+.5 for i in range(20)]:box('Turbine side standing seam',(x+sgn*.103,y,6.29),(.024,.025,1.82),steel,.003)
 for y in [1,6,11,16,21,23.6]:box('Turbine structural exterior pilaster',(x+sgn*.08,y,3.72),(.16,.21,7.44),cream,.015)
 box('Turbine side band sill',(x+sgn*.09,12,5.365),(.11,24,.04),steel,.003)
rod('Turbine rain leader',(-3.65,-.13,.10),(-3.65,-.13,7.47),.055,steel)
for z in [.35,2.5,4.8,7.1]:box('Turbine rain leader bearing',(-3.65,-.066,z),(.16,.075,.06),steel,.004)
rod('Turbine drain shoe',(-3.65,-.13,.10),(-3.65,-.28,.07),.055,steel)
box('Turbine external identity',(0,-.095,3.91),(3.2,.09,.39),steel)
text('Turbine hall exterior title','TURBINE HALL',(0,-.142,3.82),.22);bpy.data.objects['Turbine hall exterior title'].rotation_euler.z=0
box('Turbine identity task light',(0,-.095,4.20),(.44,.09,.15),steel)
em=mat('EXT turbine warm task lens',(.65,.58,.43),.35);p=em.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.85,.61,1);p.inputs['Emission Strength'].default_value=2
box('Turbine task light lens',(0,-.132,4.115),(.35,.07,.02),em,.002)
ld=bpy.data.lights.new('Turbine entrance pool','AREA');ld.energy=25;ld.color=(1,.88,.67);ld.size=.30;lo=bpy.data.objects.new(ld.name,ld);ext.objects.link(lo);lo.location=(0,-.15,4.10)
box('Turbine handover mounting board',(3.1,-.083,1.73),(.64,.065,.80),steel)
box('Handover card backing',(3.0,-.13,1.83),(.38,.035,.52),silver)
box('Handover card',(3.0,-.151,1.83),(.32,.007,.46),paper,.002)
box('Handover retaining clip',(3.0,-.16,2.07),(.13,.025,.045),silver,.004)
st('Turbine handover heading','HANDOVER',(3.0,-.156,1.96),.041)
for z in [1.86,1.78,1.7]:box('Handover ruled line',(3.0,-.156,z),(.25,.002,.003),steel,.0005)
box('Inspection key hook shoe',(3.29,-.13,1.57),(.1,.035,.09),silver,.003)
rod('Inspection key hook',(3.29,-.14,1.58),(3.29,-.20,1.58),.012,silver)
rod('Inspection key bow',(3.27,-.20,1.53),(3.31,-.20,1.53),.014,silver)
rod('Inspection key neck',(3.29,-.20,1.52),(3.29,-.20,1.43),.012,silver)
box('Inspection key tooth',(3.30,-.20,1.44),(.04,.02,.018),silver,.003)
rod('Key retaining tether',(3.29,-.20,1.54),(3.29,-.20,1.59),.004,rubber)
box('Handover pencil holder',(3.29,-.13,1.89),(.07,.035,.20),silver,.003)
rod('Handover pencil',(3.29,-.155,1.91),(3.29,-.155,2.16),.008,accent)
# Condenser's source-owned ceiling slab meets the east wall base at Z0..0.30.
# Trim only new facade parts away from that established stacked interface.
for part in list(ext.objects):
 if part.type!='MESH' or part.location.x<10:continue
 y=part.location.y
 # Side panel orientation is Z-only, so world Z equals vertex Z + location Z.
 if not 5.5<y<18.8:continue
 zs=[v.co.z+part.location.z for v in part.data.vertices]
 if min(zs)>=.305:continue
 if max(zs)<=.305:bpy.data.objects.remove(part,do_unlink=True)
 else:
  for v in part.data.vertices:
   if v.co.z+part.location.z<.305:v.co.z=.305-part.location.z
camera_specs=[('FRONT',(3,-21,3.5),(3,0,3.3)),('OBLIQUE',(-26,-27,14),(3,11,3.6)),('REVERSE',(30,51,14),(3,12,3.6)),('DETAIL',(5,-5,1.65),(2.3,0,1.8))]
