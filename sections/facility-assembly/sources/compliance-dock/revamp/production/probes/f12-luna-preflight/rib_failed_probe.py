import bpy,json
from mathutils import Vector
from pathlib import Path
f='/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock/revamp/production/checkpoints/full-f12-interrupted.blend'
with bpy.data.libraries.load(f,link=False) as (src,dst):
    dst.scenes=[n for n in src.scenes if n=='COMPLIANCE_EDIT_LOCAL']
s=next(x for x in bpy.data.scenes if x.name.startswith('COMPLIANCE_EDIT_LOCAL'))
if bpy.context.window: bpy.context.window.scene=s
bpy.context.view_layer.update()
def worldverts(o):return [o.matrix_world@v.co for v in o.data.vertices]
def rec(o):
 v=worldverts(o)
 return {'name':o.name,'parent':o.parent.name if o.parent else None,'verts':len(v),'bounds':[[min(p[k] for p in v) for k in range(3)],[max(p[k] for p in v) for k in range(3)]],'scale':list(o.scale),'loc':list(o.matrix_world.translation),'sample_vertices':[[round(p.x,6),round(p.y,6),round(p.z,6)] for p in v[:24]]}
body=s.objects.get('Lead tunnel main body')
res={'scene':s.name,'objects':len(s.objects),'body':rec(body),'ribs':[],'screws':[]}
for o in s.objects:
 if o.name.startswith('Tunnel stiffener '):
  rv=worldverts(o);east=o.matrix_world.translation.x>4.65;side=1 if east else -1
  # report boundary vertices and expected main-body skin x at each vertex height
  exp=[]
  for p in rv:
   skin=(5.4 if east else 3.9)+(0 if p.z<=1.98 else -side*.12*min(1,(p.z-1.98)/.17))
   exp.append({'xyz':[round(p.x,6),round(p.y,6),round(p.z,6)],'skin_x':round(skin,6),'x_offsets_to_skin_m':[round(skin-p.x,6),round(max(0,p.x-(.034 if east else 0))-skin,6)]})
  res['ribs'].append({'summary':rec(o),'vertex_compare':exp})
for o in s.objects:
 if o.name.startswith('CD | Cargo rib captive screw'):
  res['screws'].append(rec(o))
# exact edge interpolation through old part's longest vertical-profile edges
Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock/revamp/production/probes/f12-luna-preflight/failed_rib_geometry.json').write_text(json.dumps(res,indent=2))
print('FAILED_ARCHIVE_SCENE_APPENDED_READ_ONLY',s.name,'ribs',len(res['ribs']),'screws',len(res['screws']))
