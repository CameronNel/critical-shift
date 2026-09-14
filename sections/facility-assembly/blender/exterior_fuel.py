"""Articulated corridor skins derived from each actual cardinal exterior wall."""
import re
ochre=mat('EXT fuel route ochre',(.43,.285,.075),.74)
survey=json.loads((ROOT/'sources'/SID/'survey.json').read_text())
for rec in survey['records']:
 m=re.match(r'^Wall_([NSEW]).*_concrete$',rec['name'])
 if not m or not rec.get('bounds'):continue
 lo,hi=rec['bounds'];d=m[1];ax=0 if d in 'WE' else 1;t=1-ax;sgn=-1 if d in 'WS' else 1;face=lo[ax] if sgn<0 else hi[ax]
 n=max(1,round((hi[t]-lo[t])/2.25))
 for i in range(n):
  c=[(lo[j]+hi[j])/2 for j in range(3)];c[ax]=face+sgn*.025;c[t]=lo[t]+(i+.5)*(hi[t]-lo[t])/n
  size=[hi[j]-lo[j] for j in range(3)];size[ax]=.05;size[t]=(hi[t]-lo[t])/n-.012
  ob=box('Fuel mineral exterior bay',c,size,cream,.006);ob['source_wall']=rec['name']
  if lo[2]<.1:
   c[2]=.35;c[ax]=face+sgn*.055;size[ax]=.06;size[2]=.70;box('Fuel exterior impact base',c,size,base,.005)
   c[2]=1.25;c[ax]=face+sgn*.052;size[ax]=.008;size[2]=.14;box('Fuel exterior route stripe',c,size,ochre,.001)
 c=[(lo[j]+hi[j])/2 for j in range(3)];c[ax]=face+sgn*.03;c[2]=hi[2]-.04
 size=[hi[j]-lo[j] for j in range(3)];size[ax]=.16;size[2]=.08
 box('Fuel folded wall top cap',c,size,steel,.004)
text('Fuel west exterior identification','FUEL TRANSFER',(-2.595,5,2.7),.29)
bpy.data.objects['Fuel west exterior identification'].rotation_euler.z=-math.pi/2
camera_specs=[('FRONT',(5,-28,7),(5,9,2.5)),('OBLIQUE',(-25,-20,20),(6,11,2.5)),('REVERSE',(36,43,20),(6,11,2.5)),('DETAIL',(-8,1.2,2.6),(-2.55,5,2.6))]

bpy.data.objects['Fuel west exterior identification'].data.materials.clear();bpy.data.objects['Fuel west exterior identification'].data.materials.append(steel)
