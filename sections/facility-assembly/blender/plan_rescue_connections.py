"""Compare rescue travel before/after the open-court diagonal using A04 graph law."""
import json,heapq
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
original=json.loads((ROOT/'production/LAYOUT.json').read_text())
planned=json.loads(json.dumps(original));planned['revision']='A06_CONNECTION_PLAN'
planned['placements']['medical-reanimation']['translation']=[-18,31,0]
planned['ports']['medical.entry']=[-18,30.31,0]
for r in planned['routes']:
 if r['id']=='R11':r['points']=[[-18,30.31,0],[-18,28,0]]
 if r['id']=='R15':r['points']=[[-15,28,0],[-26,28,0],[-26,55,0],[-5,55,0],[-1.7,59.5,0],[-.5,61.2,0],[-2.5,63.2,0]]
planned['routes'].append({'id':'R22','kind':'clean','width_m':4,'height_m':3.5,'points':[[-15,15,0],[-18,28,0]],'status':'COURTYARD_CANDIDATE','note':'Open-air diagonal rescue shortcut. Medical assembly moves +11m X, -6m Y; source room unchanged.'})
(ROOT/'production/LAYOUT_CONNECTIONS_PLAN.json').write_text(json.dumps(planned,indent=2))
code=(ROOT/'blender/audit_plan.py').read_text().split("report={'revision'")[0]
def run(new=False):
 ns={'__file__':str(ROOT/'blender/audit_plan.py')}
 modified=code.replace("production/LAYOUT.json","production/LAYOUT_CONNECTIONS_PLAN.json").replace("[-29,43,0]","[-18,37,0]")
 exec(modified if new else code,ns)
 return ns
before=run();after=run(True)
P=original['ports']
def route(ns,start):
 target=tuple(round(v,4) for v in ns['L']['ports']['medical.entry'])
 g=ns['graph'];start=tuple(round(v,4) for v in start);q=[(0,start)];dist={start:0};parent={}
 while q:
  d,p=heapq.heappop(q)
  if d!=dist[p]:continue
  if p==target:break
  for other,w in g[p].items():
   if d+w<dist.get(other,1e99):dist[other]=d+w;parent[other]=p;heapq.heappush(q,(d+w,other))
 path=[target]
 while path[-1]!=start:path.append(parent[path[-1]])
 return dist[target],list(reversed(path))
rows=[]
for label,key in [('Mine portal','mine.entry'),('Refinery personnel','refinery.personnel'),('Refinery dispatch','refinery.dispatch'),('Fuel clean exit','fuel.clean'),('Reactor fuel entrance','reactor.fuel'),('Turbine entrance','turbine.entry'),('Electrical entrance','electrical.entry'),('Waste personnel','waste.personnel'),('Cooling entrance','cooling.entry'),('Spawn exit','spawn.exit')]:
 a,_=route(before,P[key]);b,path=route(after,P[key]);rows.append({'origin':label,'before_m':round(a,2),'after_m':round(b,2),'saved_m':round(a-b,2),'path':path})
report={'routes':rows,'all_planned_nodes_connected':after['connected'],'diameter_m':round(after['diameter'],2),'changed_route_obstacle_candidates':[r for r in after['hits'] if r['route'] in ['R11','R15','R22']],'room_overlap_screen':after['overlaps'],'scope':'Centerline planning distance between named doors, including assumed internal room paths where selected by Dijkstra. Not game navmesh, door interlocks, or collision acceptance.'}
(ROOT/'production/RESCUE_ROUTE_COMPARISON.json').write_text(json.dumps(report,indent=2))
print(json.dumps({**report,'routes':[{k:v for k,v in r.items() if k!='path'} for r in rows]},indent=2))
