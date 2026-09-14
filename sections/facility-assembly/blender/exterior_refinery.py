"""Refinery original wall skins, open receiving/dispatch and personnel apertures."""
cobalt=mat('EXT refinery muted cobalt',(.075,.115,.17),.63,.25)
paper=mat('EXT refinery receiving record',(.66,.62,.51),.9)
survey=json.loads((ROOT/'sources'/SID/'survey.json').read_text())
names=['North_wall','West_front_pier','West_main','East_front_pier','East_main','South_left','South_right','South_header','West_header','East_header']
for rec in survey['records']:
 if rec['name'] not in names or not rec.get('bounds'):continue
 lo,hi=rec['bounds'];d=rec['name'][0];ax=0 if d in 'WE' else 1;t=1-ax;sgn=-1 if d in 'WS' else 1;face=lo[ax] if sgn<0 else hi[ax]
 # Exact local utility window allowances; untouched original wall/flanges remain visible.
 holes={'West_main':[(-1.65,-1.14,3.70,4.22)],'East_main':[(.17,.69,3.70,4.22)],'North_wall':[(3.85,4.46,3.12,3.75)]}.get(rec['name'],[])
 cuts=sorted(set([lo[t],hi[t]]+[max(lo[t],min(hi[t],v)) for h in holes for v in h[:2]]))
 zs=sorted(set([lo[2],hi[2]]+[z for z in [.45,3.45] if lo[2]<z<hi[2]]+[v for h in holes for v in h[2:] if lo[2]<v<hi[2]]))
 for a,b in zip(cuts,cuts[1:]):
  for z0,z1 in zip(zs,zs[1:]):
   if any(h[0]<(a+b)/2<h[1] and h[2]<(z0+z1)/2<h[3] for h in holes):continue
   n=max(1,round((b-a)/2.4))
   for i in range(n):
    c=[0,0,(z0+z1)/2];c[ax]=face+sgn*.025;c[t]=a+(i+.5)*(b-a)/n
    size=[0,0,z1-z0-.006];size[ax]=.05;size[t]=(b-a)/n-.012
    box('Refinery exterior panel',c,size,cobalt if z0>=3.45 else base if z1<=.45 else cream,.004)
 c=[(lo[j]+hi[j])/2 for j in range(3)];c[ax]=face+sgn*.02;c[2]=hi[2]-.045
 size=[hi[j]-lo[j] for j in range(3)];size[ax]=.15;size[2]=.09;box('Refinery wall weather cap',c,size,steel,.004)
text('Refinery external title','REFINERY',(4.8,-6.787,3.85),.34);bpy.data.objects['Refinery external title'].rotation_euler.z=0
box('Refinery record mount',(.1,-6.819,1.6),(.5,.07,.65),cobalt)
box('Refinery receiving card',(.1,-6.858,1.65),(.38,.007,.43),paper,.002)
box('Refinery retaining clip',(.1,-6.871,1.87),(.12,.025,.055),steel,.004)
box('Refinery pocket back',(.1,-6.863,1.31),(.44,.025,.18),steel,.004)
box('Refinery pocket floor',(.1,-6.923,1.23),(.44,.14,.025),steel,.003)
box('Refinery pocket lip',(.1,-6.993,1.28),(.44,.025,.12),steel,.003)
for x in [-.12,.32]:box('Refinery pocket cheek',(x,-6.923,1.31),(.025,.14,.18),steel,.003)
camera_specs=[('FRONT',(0,-24,3.8),(0,0,2.4)),('OBLIQUE',(-24,-24,12),(0,0,2.4)),('REVERSE',(25,24,12),(0,0,2.4)),('DETAIL',(2,-11,1.65),(.1,-6.8,1.6))]
