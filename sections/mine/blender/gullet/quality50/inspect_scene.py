"""Inspect the actual source scene; output scene-local bounds, lights and controls."""
import bpy, json
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parents[1]/'production'/'quality50'
OUT.mkdir(parents=True, exist_ok=True)
s = bpy.context.scene
records=[]
for o in s.objects:
    keep = (o.type in {'LIGHT','CAMERA'} or o.get('csm_component') == 'cart_root' or any(x in o.name for x in ['Leaf_outer','Magazine','Apron_concrete','Side_apron','Sump','Pump','Walkway','Cart','Continuous_I_rail']))
    if not keep or o.get('csm_collision_only'): continue
    rec={'name':o.name,'type':o.type,'position':list(o.matrix_world.translation),'parent':o.parent.name if o.parent else None,'meta':{k:v for k,v in o.items() if isinstance(v,(str,int,float,bool))}}
    if o.type=='MESH':
        bb=[o.matrix_world@Vector(p) for p in o.bound_box]
        rec['bounds']=[[min(p[i] for p in bb) for i in range(3)],[max(p[i] for p in bb) for i in range(3)]]
        rec['materials']=[x.material.name if x.material else None for x in o.material_slots]
    if o.type=='LIGHT':rec.update(energy=o.data.energy,colour=list(o.data.color))
    if o.type=='CAMERA':rec.update(lens=o.data.lens,matrix=[list(row) for row in o.matrix_world])
    records.append(rec)
(OUT/'source_inventory.json').write_text(json.dumps({'blender':bpy.app.version_string,'scene':s.name,'objects':len(s.objects),'records':records},indent=2))
for r in records:
    if r['type'] in {'LIGHT','CAMERA'} or r.get('meta',{}).get('csm_component')=='cart_root' or any(x in r['name'] for x in ['Leaf_outer','Magazine_casing','Sump_concrete']):
        print('SOURCE_INVENTORY',json.dumps(r),flush=True)
