"""Medical mineral envelope and entry transfer station; original open portal preserved."""
import ast
tree=ast.parse((ROOT/'blender/exterior_spawn.py').read_text())
for node in tree.body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),str(ROOT/'blender/exterior_spawn.py'),'exec'),globals())
red=mat('EXT medical muted brick',(.30,.085,.065),.6,.15)
stainless=mat('EXT brushed stainless trim',(.35,.37,.36),.4,.85)
paper=mat('EXT clean transfer card',(.72,.71,.63),.9)
for a,b in [(-4.18,-1.11),(1.11,4.18)]:sy(a,b,-.181,3.6)
box('Medical lintel skin',(0,-.207,3.05),(2.22,.05,1.10),cream)
sx(-.18,9.18,-4.181,3.6,-1);sx(-.18,9.18,4.181,3.6,1)
sy(-4,1.3,9.181,3.6,1);sy(3.36,4,9.181,3.6,1)
sx(9.18,11.3,1.299,2.55,-1);sx(9.18,11.3,3.361,2.55,1)
# Rear decon closure stays original, with perimeter trim only.
box('Decon rear top flashing',(2.33,11.3,2.62),(2.18,.16,.09),steel)
for x in [1.30,3.36]:box('Decon corner folded trim',(x,11.31,1.28),(.08,.05,2.55),steel,.004)
box('Medical top front coping',(0,-.18,3.71),(8.5,.22,.12),steel)
box('Medical rear coping',(0,9.18,3.71),(8.45,.22,.12),steel)
box('Medical identification band',(0,-.239,2.97),(8.30,.023,.34),red,.004)
for x in [-1.17,1.17]:box('Medical external jamb trim',(x,-.22,1.25),(.12,.085,2.50),stainless,.007)
box('Medical head trim',(0,-.22,2.58),(2.46,.085,.16),stainless,.007)
text('Medical facade title','MEDICAL',(0,-.255,2.89),.19);bpy.data.objects['Medical facade title'].rotation_euler.z=0
for x in [-1.50,1.50]:
 box('Medical downlight wall plate',(x,-.24,2.98),(.25,.065,.20),steel)
 em=mat('EXT medical warm lens '+str(x),(.65,.59,.44),.35);p=em.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.86,.64,1);p.inputs['Emission Strength'].default_value=2
 box('Medical downward lens',(x,-.269,2.875),(.19,.075,.015),em,.002)
 ld=bpy.data.lights.new('Medical external light','AREA');ld.energy=14;ld.color=(1,.88,.7);ld.size=.2;lo=bpy.data.objects.new(ld.name,ld);ext.objects.link(lo);lo.location=(x,-.30,2.86)
rod('Medical rain leader',(-4.02,-.31,.10),(-4.02,-.31,3.70),.05,steel)
for z in [.28,1.65,3.4]:box('Medical rain leader clamp',(-4.02,-.27,z),(.14,.15,.05),steel,.003)
rod('Medical rain outlet',(-4.02,-.31,.10),(-4.02,-.45,.07),.05,steel)
box('Emergency call station',(-1.58,-.266,1.40),(.29,.12,.46),stainless)
box('Call button red surround',(-1.58,-.329,1.30),(.17,.014,.15),red,.003)
rod('Call tactile button',(-1.58,-.34,1.30),(-1.58,-.36,1.30),.042,steel)
for z in [1.47,1.50,1.53]:box('Call speaker slot',(-1.58,-.329,z),(.15,.005,.008),rubber,.001)
st('Medical call label','CALL',(-1.58,-.33,1.58),.044)
# Wall-supported clean transfer supplies and card, beyond stretcher clear width.
box('Transfer backing',(2.34,-.259,1.53),(1.20,.085,.98),stainless)
box('Transfer hood',(2.34,-.34,2.06),(1.28,.26,.035),steel,.004)
for z in [1.31,1.65]:
 box('Glove cradle rear plate',(2.06,-.313,z),(.41,.025,.28),stainless,.005)
 for x in [1.864,2.256]:box('Glove cradle side',(x,-.379,z),(.018,.13,.28),stainless,.003)
 for zz in [z-.131,z+.131]:box('Glove cradle rim',(2.06,-.379,zz),(.41,.13,.018),stainless,.003)
 # Four carton-face rails make a real open slot into a recessed dispenser.
 for zz in [z-.07,z+.07]:box('Glove carton face rail',(2.06,-.444,zz),(.34,.014,.08),paper,.002)
 for x in [1.9225,2.1975]:box('Glove carton face return',(x,-.444,z),(.065,.014,.06),paper,.002)
 for zz in [z-.115,z+.115]:box('Dispenser face retaining lip',(2.06,-.446,zz),(.38,.014,.025),stainless,.002)
 box('Glove packet shadow liner',(2.06,-.334,z),(.34,.012,.22),rubber,.004)
 cuff=mat('EXT neutral glove cuff',(.45,.47,.42),.8)
 box('Folded glove packet supported on liner',(2.06,-.353,z),(.18,.034,.17),cuff,.004)
 box('Folded glove cuff visible through slot',(2.06,-.390,z-.003),(.14,.070,.023),cuff,.008)
box('Transfer clipboard',(2.65,-.314,1.52),(.32,.025,.53),steel,.005)
box('Transfer checklist',(2.65,-.33,1.52),(.28,.007,.46),paper,.002)
box('Transfer checklist clip',(2.65,-.337,1.77),(.12,.025,.045),stainless,.005)
st('Transfer checklist title','TRANSFER',(2.65,-.336,1.67),.038)
for z in [1.57,1.49,1.41]:box('Transfer form line',(2.65,-.335,z),(.23,.002,.003),steel,.0005)
box('Medical transfer ID backing',(2.34,-.251,2.30),(1.16,.06,.32),steel)
text('Medical transfer ID','PATIENT TRANSFER',(2.34,-.283,2.27),.074);bpy.data.objects['Medical transfer ID'].rotation_euler.z=0
camera_specs=[('FRONT',(0,-12.5,2.0),(0,0,1.8)),('OBLIQUE',(-13,-14,7),(0,4.5,1.8)),('REVERSE',(13,23,7),(0,5,1.8)),('DETAIL',(4,-4.5,1.65),(1.8,-.18,1.65))]
