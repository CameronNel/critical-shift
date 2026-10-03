import bpy, json, math
from mathutils import Vector
from pathlib import Path
path='/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock/module_overhaul_R1.blend'
bpy.ops.wm.open_mainfile(filepath=path, load_ui=False)
s=bpy.context.scene
names=['Lead tunnel main body','Lead tunnel inner chamber','Tunnel stiffener left','Tunnel stiffener right','Covered Trolley Draped Tarp','Trolley strap 1','Trolley strap 2','Trolley strap 3','Trolley strap 4','Checkin Counter Hatch','Counter writing surface','Counter queue tray','Authority stamp rubber base','Ink pad tin base','Counter pen holder base','Forms waiting stack','Unprocessed forms','G1 leaf 1 panel','G1 leaf 1','D1 frame jamb -1','D1 frame jamb 1','D2 frame jamb -1','D2 frame jamb 1','P2 frame jamb -1','P2 frame jamb 1']
def ob(o):
    if o is None:return None
    b=[o.matrix_world@Vector(corner) for corner in o.bound_box]
    d=o.dimensions
    return {'name':o.name,'type':o.type,'loc':list(o.matrix_world.translation),'dims':list(d),'world_aabb':[[min(p[i] for p in b) for i in range(3)],[max(p[i] for p in b) for i in range(3)]], 'scale':list(o.scale),'rot':list(o.rotation_euler),'parent':o.parent.name if o.parent else None,'props':{k:o[k] for k in o.keys() if k in ['support_class','contact_anchor','assembly','support_geometry','textile_grid','fabric_uv_contract']}, 'verts':len(o.data.vertices) if o.type=='MESH' else None,'uvs':[u.name for u in o.data.uv_layers] if o.type=='MESH' else None,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else None}
found={n:ob(s.objects.get(n)) for n in names}
# full inventory candidates and existing contacts
cand=[]
for o in s.objects:
    if any(k in o.name.lower() for k in ['cover','cassette','pressed panel bay','captive screw','forms','manifest','docket','jacket','cloth','tarp','contact','anchor','foot','frame jamb']):cand.append(ob(o))
contacts=[]
for o in s.objects:
    if o.get('contact_anchor') or o.get('support_class') or o.get('support_geometry'):
        contacts.append(ob(o))
# selected global metadata
meta={k:s[k] for k in s.keys() if any(x in k.lower() for x in ['support','contact','budget','triangle','route','interface'])}
result={'filepath':path,'scene':s.name,'object_count':len(s.objects),'named':found,'candidates':cand,'contacts':contacts,'metadata':meta}
out='/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock/revamp/production/probes/f12-luna-preflight/f11_inventory.json'
Path(out).write_text(json.dumps(result,indent=2,default=str))
print('READ_ONLY_F11',len(s.objects),'objects; wrote',out)
