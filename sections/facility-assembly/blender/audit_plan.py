"""Conservative saved-geometry survey, reservation screening and readable plan."""
import json,math,heapq
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];L=json.loads((ROOT/'production/LAYOUT.json').read_text())
X0,Y0,X1,Y1=-110,-66,94,88;STEP=.25;NX=int((X1-X0)/STEP);NY=int((Y1-Y0)/STEP)
def transform(sid,p):
 pose=L['placements'][sid];a=math.radians(pose['rotation_z_degrees']);c,s=math.cos(a),math.sin(a);t=pose['translation']
 return [t[0]+c*p[0]-s*p[1],t[1]+s*p[0]+c*p[1],t[2]+p[2]]
def rect(sid,b):
 return [transform(sid,[x,y,0])[:2] for x,y in [(b[0][0],b[0][1]),(b[1][0],b[0][1]),(b[1][0],b[1][1]),(b[0][0],b[1][1])]]
def px(p):return (int((p[0]-X0)/STEP),int((Y1-p[1])/STEP))
occupancy={};footprints={};names={}
for sid in L['placements']:
 survey=json.loads((ROOT/'sources'/sid/'survey.json').read_text());mask=Image.new('1',(NX,NY));draw=ImageDraw.Draw(mask)
 for ob in survey['records']:
  b=ob.get('bounds');z=L['placements'][sid]['translation'][2]
  if not b or ob['hide_render'] or not (b[0][2]+z<1.6 and b[1][2]+z>.35):continue
  if ob['type'] not in ['MESH','CURVE','SURFACE']:continue
  draw.polygon([px(v) for v in rect(sid,b)],fill=1)
 occupancy[sid]=np.asarray(mask,dtype=bool)
 footprints[sid]=rect(sid,survey['all_visible_bounds'])
names_list=list(occupancy);overlaps=[]
for i,a in enumerate(names_list):
 for b in names_list[i+1:]:
  count=int(np.logical_and(occupancy[a],occupancy[b]).sum())
  if count:overlaps.append({'modules':[a,b],'conservative_headheight_overlap_m2':round(count*STEP*STEP,3)})
hits=[]
for route in L['routes']:
 for sid,grid in occupancy.items():
  samples=[]
  for a,b in zip(route['points'],route['points'][1:]):
   if abs(a[2])>.1 or abs(b[2])>.1:continue
   d=math.dist(a,b);n=max(2,int(d/.25));dx,dy=b[0]-a[0],b[1]-a[1];length=max(math.hypot(dx,dy),.01)
   for j in range(n+1):
    t=j/n;x=a[0]+dx*t;y=a[1]+dy*t
    # Four-metre end transitions may narrow to the existing aperture.
    near_end=min(math.dist([x,y,0],route['points'][0]),math.dist([x,y,0],route['points'][-1]))<4
    if near_end:continue
    for off in [-max(0,route['width_m']/2-.35),0,max(0,route['width_m']/2-.35)]:
     p=[x-dy/length*off,y+dx/length*off];ix,iy=px(p)
     if 0<=ix<NX and 0<=iy<NY and grid[iy,ix]:samples.append([round(x,2),round(y,2)]);break
  if samples:hits.append({'route':route['id'],'module':sid,'samples':len(samples),'first':samples[0],'last':samples[-1]})
# Planned connectivity graph. These are route budgets, never a controller/navmesh test.
segments=[]
for r in L['routes']:
 segments.extend(zip(r['points'],r['points'][1:]))
P=L['ports']
internal=[
 [[-88,-40,0],[-88,-29,0],P['mine.entry']],
 [P['refinery.intake'],[-4.58,-20,0],[-4.58,-16.6,0],[-4.58,-12,0],P['refinery.dispatch']],
 [P['refinery.personnel'],[-4.58,-18.4,0],[-4.58,-16.6,0]],
 [[0,0,0],[0,10,0],[14.2,10,0],[14.2,24,0]],
 [[0,10,0],[0,17.4,0],P['fuel.service']],
 [[0,17.4,0],[0,19.2,0],[6.6,19.2,0],P['fuel.clean']],
 [[6.6,19.2,0],[14.2,19.2,0]],
 [[14.2,16,0],P['fuel.waste']],
 [P['reactor.fuel'],[14.2,38,0],[24,38,0],[24,46.5,0],P['reactor.turbine']],
 [P['reactor.fuel'],[14.2,38,0],[4,38,0],[4,55,0],P['reactor.cooling']],
 [P['turbine.entry'],[42,46.5,0],[62,46.5,0],P['turbine.exit']],
 [P['electrical.entry'],[66,26,0],[66,17,0],P['electrical.exit']],
 [P['waste.entry'],[66,3.2,0],P['waste.personnel']],
 [[66,3.2,0],P['waste.dispatch']],
 [P['spawn.exit'],[-28,3.7,0]], [P['medical.entry'],[-29,43,0]],
 [P['compliance.entry'],[-56,16,0],P['compliance.arrival']],
]
for pts in internal:segments.extend(zip(pts,pts[1:]))
points={tuple(round(v,4) for v in p) for seg in segments for p in seg}
# Add intersections of ground-level segments so alternate loops actually connect.
for a,b in segments:
 for c,d in segments:
  if any(abs(p[2])>.01 for p in [a,b,c,d]):continue
  ux,uy=b[0]-a[0],b[1]-a[1];vx,vy=d[0]-c[0],d[1]-c[1];den=ux*vy-uy*vx
  if abs(den)<1e-8:continue
  wx,wy=c[0]-a[0],c[1]-a[1];t=(wx*vy-wy*vx)/den;s=(wx*uy-wy*ux)/den
  if 0<=t<=1 and 0<=s<=1:points.add((round(a[0]+t*ux,4),round(a[1]+t*uy,4),0))
graph={p:{} for p in points}
for a,b in segments:
 v=np.array(b)-a;length=np.linalg.norm(v)
 if length<.001:continue
 on=[]
 for p in points:
  t=float(np.dot(np.array(p)-a,v)/length**2)
  if -.0001<=t<=1.0001 and np.linalg.norm(np.array(a)+t*v-p)<.001:on.append((t,p))
 on.sort()
 for (_,p),(_,q) in zip(on,on[1:]):graph[p][q]=graph[q][p]=math.dist(p,q)
def distances(start):
 dist={start:0};queue=[(0,start)]
 while queue:
  d,p=heapq.heappop(queue)
  if d!=dist[p]:continue
  for q,w in graph[p].items():
   if d+w<dist.get(q,1e10):dist[q]=d+w;heapq.heappush(queue,(d+w,q))
 return dist
distances_all={p:distances(p) for p in points};diameter=max(v for ds in distances_all.values() for v in ds.values());connected=all(len(ds)==len(points) for ds in distances_all.values())
travel={'normal_speed_assumption_m_s':4.5,'loaded_speed_assumption_m_s':1.5,'graph_connected':connected,'diameter_endpoints':next([list(a),list(b)] for a,ds in distances_all.items() for b,v in ds.items() if v==diameter),'planned_graph_diameter_m':round(diameter,2),'diameter_normal_walk_seconds':round(diameter/4.5,2),'diameter_at_4m_s_seconds':round(diameter/4,2),'minimum_speed_for_60s_m_s':round(diameter/60,3),'full_crossing_under_60_at_assumed_speed':diameter/4.5<60,'not_runtime_verified':True,'internal_paths':'Planning centerlines, not fresh collision-certified room sweeps. Mine endpoint represents deep working area, not scenery backdrop.'}
report={'revision':L['revision'],'room_count':len(occupancy),'units':'metres','room_overlap_screen':overlaps,'reservation_clearance_candidates':hits,'screen_method':'0.25m conservative projected evaluated object bounds at occupied player height; excludes 4m connector end transitions; candidates need inspection, not exact mesh collision verdicts','travel':travel}
(ROOT/'production/PLAN_AUDIT.json').write_text(json.dumps(report,indent=2))
# Render a legible planning sheet with real-scale footprints and explicit gap reservations.
S=2;im=Image.new('RGB',(NX*S,NY*S+210),(24,29,34));dr=ImageDraw.Draw(im)
fontpath='C:/Windows/Fonts/arial.ttf';font=ImageFont.truetype(fontpath,23);small=ImageFont.truetype(fontpath,17);title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',36)
def ip(p):x,y=px(p);return(x*S,y*S+100)
colors={'freight':'#e5a04e','service':'#bdaf72','maintenance':'#8fae87','clean':'#ddd9c9','controlled':'#b27676','waste':'#b68e62'}
for x in range(-100,100,10):dr.line([ip((x,Y0)),ip((x,Y1))],fill=(40,47,53),width=1)
for y in range(-60,90,10):dr.line([ip((X0,y)),ip((X1,y))],fill=(40,47,53),width=1)
for i,(sid,grid) in enumerate(occupancy.items()):
 arr=np.zeros((NY,NX,4),dtype=np.uint8);arr[grid]=[105,116,125,220];overlay=Image.fromarray(arr).resize((NX*S,NY*S));im.paste(overlay,(0,100),overlay)
for sid,poly in footprints.items():
 if sid=='condenser-bay':continue
 dr.line([ip(p) for p in poly+[poly[0]]],fill=(108,120,130),width=2)
for r in L['routes']:
 pts=r['points'];col=colors[r['kind']]
 for a,b in zip(pts,pts[1:]):
  n=max(1,int(math.dist(a,b)/1.4))
  for j in range(n):
   p=[a[k]+(b[k]-a[k])*j/n for k in range(3)];q=[a[k]+(b[k]-a[k])*min((j+.55)/n,1) for k in range(3)];dr.line([ip(p),ip(q)],fill=col,width=max(2,int(r['width_m']/STEP*S*.10)))
 p=pts[len(pts)//2];dr.text(ip(p),r['id'],font=small,fill=col,stroke_width=2,stroke_fill=(24,29,34))
for r in L['reserved_volumes']:
 c=r['center'];s=r['size'];dr.rectangle([ip((c[0]-s[0]/2,c[1]+s[1]/2)),ip((c[0]+s[0]/2,c[1]-s[1]/2))],outline='#bba465',width=3)
anchors={'mine':(-68,-20),'spawn-room':(-28,6),'refinery':(-4,-16),'fuel-corridor':(7,11),'reactor-room':(14,47),'cooling-plant':(-8,69),'turbine-room':(54,48),'electrical-room':(66,20),'waste-storage':(66,-6),'medical-reanimation':(-29,43),'compliance-dock':(-56,16),'condenser-bay':(51,39)}
for sid,p in anchors.items():
 label=sid.replace('-',' ').upper()+('\nBELOW TURBINE  -6m' if sid=='condenser-bay' else '')
 dr.multiline_text(ip(p),label,font=font,fill='white',anchor='mm',align='center',stroke_width=3,stroke_fill=(24,29,34))
dr.text((35,20),'CRITICAL SHIFT  /  A04 FACILITY ASSEMBLY',font=title,fill='white')
dr.text((35,67),'12 existing modules at 1:1 scale. Dashed lines and outlined volumes = RESERVED, UNBUILT connections.',font=font,fill='#d7c89c')
dr.text((35,im.height-86),'FREIGHT: amber   |   CLEAN / RESCUE: ivory   |   MAINTENANCE: muted green   |   COMPLIANCE: burgundy',font=font,fill='#ddd9c9')
dr.text((35,im.height-49),'Grid: 10 metres. Geometry occupancy is conservative. Door closures, corridor construction and engine traversal remain pending.',font=small,fill='#c4c9cf')
im.save(ROOT/'production/FACILITY_PLAN.png')
print(json.dumps({'overlaps':overlaps,'reservation_candidates':hits,'travel':travel},indent=2))
