"""Waste's receiving, dispatch and personnel interfaces remain open and unchanged."""
import ast
tree=ast.parse((ROOT/'blender/exterior_spawn.py').read_text())
for node in tree.body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),str(ROOT/'blender/exterior_spawn.py'),'exec'),globals())
PANEL_WIDTH=2.35;PLINTH_HEIGHT=1.4
cream=mat('EXT waste washable mineral panels',(.40,.38,.32),.77)
ochre=mat('EXT receiving ochre',(.50,.28,.065),.56,.2)
silver=mat('EXT waste service galvanizing',(.32,.34,.32),.44,.72)
paper=mat('EXT consignment paper',(.61,.60,.50),.88)
for a,b in [(-6,-1.51),(1.51,6)]:sy(a,b,-.321,4.8)
box('Receiving lintel mineral skin',(0,-.347,4.0),(3.02,.05,1.6),cream)
sx(0,18,-6.321,4.8,-1)
sx(0,1.79,6.321,4.8,1);sx(3.01,18,6.321,4.8,1)
box('Personnel lintel skin',(6.346,2.4,3.56),(.05,1.22,2.50),cream)
for a,b in [(-6,-1.21),(1.21,6)]:sy(a,b,18.321,4.8,1)
box('Dispatch lintel mineral skin',(0,18.347,3.8),(2.42,.05,2.0),cream)
for y in [-.32,18.32]:box('Waste end coping',(0,y,4.91),(12.72,.20,.12),steel)
for x in [-6.36,6.36]:
 for y in [.04,17.96]:box('Waste corner folded steel',(x,y,2.4),(.08,.14,4.8),steel,.004)
for a,b in [(-6,-1.51),(1.51,6)]:
 box('Receiving horizontal panel joint',((a+b)/2,-.374,2.45),(b-a,.006,.017),rubber,.001)
 for x in [a+.12,b-.12]:rod('Plinth panel fixing',(x,-.4,.12),(x,-.411,.12),.022,silver)
box('Receiving identifier',(0,-.38,3.58),(3.55,.02,.34),ochre,.003)
st('Waste receiving exterior title','WASTE RECEIVING',(0,-.394,3.50),.19)
box('Door lintel drip',(0,-.38,3.32),(3.3,.12,.035),steel,.003)
box('Dispatch identifier',(0,18.38,3.15),(3.1,.02,.32),ochre,.003)
text('Dispatch external title','SEALED DISPATCH',(0,18.394,3.07),.17);bpy.data.objects['Dispatch external title'].data.materials.clear();bpy.data.objects['Dispatch external title'].data.materials.append(steel)
em=mat('EXT waste service lens',(.63,.57,.42),.35);p=em.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.86,.65,1);p.inputs['Emission Strength'].default_value=2
for x in [-3.55,3.55]:
 box('Receiving service light',(x,-.399,4.04),(.38,.07,.18),steel)
 box('Receiving service lens',(x,-.426,3.94),(.29,.07,.02),em,.002)
 ld=bpy.data.lights.new('Waste exterior light','AREA');ld.energy=18;ld.color=(1,.88,.68);ld.size=.26;lo=bpy.data.objects.new(ld.name,ld);ext.objects.link(lo);lo.location=(x,-.44,3.92)
box('Waste weatherproof isolation box',(4.70,-.435,1.55),(.40,.15,.57),silver)
box('Isolation door inset',(4.70,-.518,1.55),(.34,.02,.49),steel)
rod('Isolation switch boss',(4.70,-.531,1.57),(4.70,-.56,1.57),.075,accent)
box('Isolation switch handle',(4.70,-.58,1.56),(.032,.035,.21),accent,.005)
rod('Isolation sealed conduit',(4.70,-.43,1.835),(4.70,-.43,4.86),.022,silver)
for z in [2.1,3.2,4.3]:box('Isolation conduit clamp',(4.70,-.397,z),(.11,.08,.045),silver,.003)
box('Isolation coping termination',(4.70,-.39,4.86),(.15,.14,.18),steel,.004)
# Small receiving paper station, both assemblies physically attached to facade.
box('Waste manifest clipboard',(-2.65,-.405,1.56),(.37,.065,.55),steel)
box('Waste manifest sheet',(-2.65,-.441,1.56),(.31,.007,.48),paper,.001)
box('Waste clipboard clip',(-2.65,-.45,1.82),(.13,.025,.055),silver,.005)
st('Waste manifest heading','MANIFEST',(-2.65,-.447,1.70),.038)
for z in [1.60,1.52,1.44]:box('Waste ruled form',(-2.65,-.446,z),(.24,.002,.003),steel,.0005)
box('Sealed consignment pocket',(-2.12,-.442,1.53),(.34,.15,.42),silver)
box('Consignment pocket lid',(-2.12,-.451,1.76),(.36,.18,.055),steel)
rod('Pocket closure stud',(-2.12,-.521,1.53),(-2.12,-.54,1.53),.025,steel)
camera_specs=[('FRONT',(0,-17.5,2.6),(0,0,2.3)),('OBLIQUE',(-21,-20,9),(0,8,2.4)),('REVERSE',(21,38,9),(0,10,2.4)),('DETAIL',(-4,-5,1.65),(-1.9,-.32,1.65))]
