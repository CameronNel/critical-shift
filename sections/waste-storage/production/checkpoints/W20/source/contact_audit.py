"""Conservative contact candidates and root envelopes, saved artifact only."""
from pathlib import Path
exec(compile((Path(__file__).parent/'validate_scene.py').read_text(),'validate_scene.py','exec'))
names=[n for n,g in geometry.items() if g['object'].type!='FONT'];parent=list(range(len(names)))
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
def join(i,j):
 a,b=find(i),find(j)
 if a!=b:parent[b]=a
tol=.012
for i,n in enumerate(names):
 a=geometry[n]
 for j in range(i):
  b=geometry[names[j]]
  if all(a['lo'][k]<=b['hi'][k]+tol and a['hi'][k]>=b['lo'][k]-tol for k in range(3)):join(i,j)
groups={}
for i,n in enumerate(names):groups.setdefault(find(i),[]).append(n)
components=[]
for g in groups.values():
 components.append({'anchored':'Floor' in g or 'Ceiling' in g or 'West Wall' in g,'objects':g,'min':[min(geometry[n]['lo'][k] for n in g) for k in range(3)],'max':[max(geometry[n]['hi'][k] for n in g) for k in range(3)]})
envelopes=[]
for root in s.objects:
 if not root.get('equipment_type'):continue
 members=[]
 for n,g in geometry.items():
  o=g['object']
  while o is not None and o!=root:o=o.parent
  if o==root:members.append(n)
 envelopes.append({'id':root.name,'type':root['equipment_type'],'origin':list(root.location),'rotation_euler':list(root.rotation_euler),'min':[min(geometry[n]['lo'][k] for n in members) for k in range(3)],'max':[max(geometry[n]['hi'][k] for n in members) for k in range(3)],'members':len(members)})
result={'revision':s.get('revision'),'tolerance_m':tol,'method':'Conservative evaluated AABB contact candidate graph. A disconnected component is a real gap >12mm in this representation; connected is NOT exact mesh contact proof.','components':components,'equipment_envelopes':envelopes}
(dest/'contact_candidates.json').write_text(json.dumps(result,indent=2));(R/'architecture/equipment-measured.json').write_text(json.dumps(envelopes,indent=2));print('UNANCHORED',[(c['objects'][:8],len(c['objects'])) for c in components if not c['anchored']])
