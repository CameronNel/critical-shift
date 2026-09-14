"""Electrical envelope with three exposed bus interfaces and original reserve annex."""
import ast
for node in ast.parse((ROOT/'blender/exterior_spawn.py').read_text()).body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),'exterior_spawn.py','exec'),globals())
PANEL_WIDTH=2.15;PLINTH_HEIGHT=.3;COPING_BASE_OFFSET=0
red=mat('EXT electrical brick identifier',(.24,.075,.055),.62,.2)
silver=mat('EXT electrical brushed hardware',(.34,.35,.33),.4,.78)
paper=mat('EXT lockout permit',(.66,.63,.53),.9)
for y,sgn in [(-.251,-1),(16.651,1)]:
 for a,b in [(-5.5,-4.72),(-3.92,-1.21),(1.21,5.5)]:sy(a,b,y,4.8,sgn)
 box('Bus lower facade field',(-4.32,y+sgn*.025,1.79),(.80,.05,3.58),cream)
 box('Bus upper facade field',(-4.32,y+sgn*.025,4.49),(.80,.05,.62),cream)
 box('Electrical portal lintel',(0,y+sgn*.025,3.75),(2.42,.05,2.1),cream)
 for x in [-4.77,-3.87]:box('Bus collar vertical',(x,y+sgn*.07,3.88),(.07,.10,.66),steel,.004)
 for z in [3.55,4.21]:box('Bus collar horizontal',(-4.32,y+sgn*.07,z),(.97,.10,.07),steel,.004)
 for x in [-4.77,-3.87]:
  for z in [3.60,4.16]:rod('Bus collar fastener',(x,y+sgn*.116,z),(x,y+sgn*.13,z),.02,silver)
 box('Electrical end coping',(0,y,4.86),(11.72,.22,.12),steel)
sx(0,16.4,-5.751,4.8,-1)
sx(0,10.75,5.751,4.8,1);sx(15.65,16.4,5.751,4.8,1)
sy(5.75,8.55,10.749,3.6);sy(5.75,8.55,15.651,3.6,1)
sx(10.75,13.64,8.551,3.6,1);sx(14.36,15.65,8.551,3.6,1)
box('Essential socket lower facade',(8.576,14,1.21),(.05,.72,2.42),cream)
box('Essential socket upper facade',(8.576,14,3.42),(.05,.72,.36),cream)
for y in [13.62,14.38]:box('Essential socket vertical rim',(8.61,y,2.8),(.09,.05,.80),steel,.004)
for z in [2.4,3.2]:box('Essential socket horizontal rim',(8.61,14,z),(.09,.81,.05),steel,.004)
for x in [-1.46,1.46]:box('Electrical entry vertical steel spine',(x,-.30,2.4),(.49,.06,4.8),steel)
box('Electrical upper department plate',(0,-.312,3.98),(2.42,.035,1.38),red)
text('Electrical exterior title','ELECTRICAL',(0,-.333,3.88),.22);bpy.data.objects['Electrical exterior title'].rotation_euler.z=0
box('Electrical lintel weather lip',(0,-.335,2.78),(2.94,.16,.045),steel,.004)
for x in [-5.34,5.34]:
 for dx in [-.10,0,.10]:box('Electrical upper folded seam',(x+dx,-.31,4.29),(.018,.09,.91),steel,.003)
em=mat('EXT electrical warm lens',(.65,.57,.43),.35);p=em.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.85,.63,1);p.inputs['Emission Strength'].default_value=2
for x in [-1.46,1.46]:
 box('Electrical entry shielded light',(x,-.368,2.85),(.23,.075,.29),steel)
 box('Electrical downlight lens',(x,-.402,2.694),(.16,.06,.025),em,.002)
 ld=bpy.data.lights.new('Electrical entry light','AREA');ld.energy=13;ld.color=(1,.87,.67);ld.size=.16;lo=bpy.data.objects.new(ld.name,ld);ext.objects.link(lo);lo.location=(x,-.414,2.68)
# Lockout station kept beyond the clear 2.4 m doorway.
box('Electrical permit case',(1.80,-.342,1.64),(.42,.13,.63),steel)
box('Permit card',(1.80,-.411,1.64),(.34,.007,.54),paper,.002)
box('Permit weather hood',(1.80,-.37,1.98),(.49,.21,.045),silver,.003)
st('Lockout permit title','LOCKOUT',(1.80,-.417,1.81),.045)
for z in [1.71,1.61,1.51]:box('Permit printed rule',(1.80,-.416,z),(.27,.002,.003),steel,.0005)
box('Lock hanger backplate',(2.28,-.304,1.65),(.28,.06,.30),red)
for x,m in [(2.20,accent),(2.36,ivory)]:
 rod('Lock hanger hook',(x,-.33,1.66),(x,-.395,1.66),.013,silver)
 box('Lockout padlock body',(x,-.389,1.51),(.083,.043,.105),m,.008)
 # U shackle is open space, not a painted symbol.
 rod('Padlock shackle leg L',(x-.028,-.389,1.56),(x-.028,-.389,1.64),.009,silver)
 rod('Padlock shackle top',(x-.028,-.389,1.64),(x+.028,-.389,1.64),.009,silver)
 rod('Padlock shackle leg R',(x+.028,-.389,1.64),(x+.028,-.389,1.56),.009,silver)
box('Entry service junction',(1.82,-.315,.71),(.24,.10,.22),steel)
rod('Permit station conduit',(1.82,-.32,.82),(1.82,-.32,1.32),.018,silver)
camera_specs=[('FRONT',(0,-16,2.5),(0,0,2.2)),('OBLIQUE',(-20,-19,9),(0,8,2.4)),('REVERSE',(23,36,9),(1,9,2.4)),('DETAIL',(4,-5,1.65),(1.7,-.25,1.65))]
