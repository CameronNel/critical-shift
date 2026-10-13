# Read-only actual emitter modifiers and closures, no map edits/renders/saves.
from pathlib import Path
import bpy,json,hashlib
root=Path('/workspace/critical-shift-spawn-runtime');out=Path('/tmp/cs-mine-front-spot-emitter-inspect-final14.json');assert not out.exists();front=bpy.data.objects['ROOM_front-end-area'];records=[]
def value(s):
 v=s.default_value
 if isinstance(v,(str,bool,int,float)):return v
 try:return list(v)
 except TypeError:return repr(v)
for o in front.instance_collection.all_objects:
 if o.type!='LIGHT' or o.data.type!='SPOT':continue
 d=o.data;entry={'name':o.name,'useNodes':d.use_nodes,'properties':{k:getattr(d,k,None) for k in ['exposure','use_temperature','temperature','diffuse_factor','specular_factor','volume_factor','normalize','use_soft_falloff']},'nodes':[]}
 if d.node_tree:
  for n in d.node_tree.nodes:
   if n.type not in {'OUTPUT_LIGHT','EMISSION','BLACKBODY'}:continue
   entry['nodes'].append({'name':n.name,'type':n.type,'inputs':{s.name:{'default':value(s),'linked':s.is_linked,'links':[{'node':l.from_node.name,'socket':l.from_socket.name} for l in s.links]} for s in n.inputs if hasattr(s,'default_value')}})
 records.append(entry)
assert len(records)==6;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();out.write_text(json.dumps({'status':'ReadOnlyActualSourceEmitterModifiers','sourceSnapshotSha256':sha(root/'runtime/out/spawn-export-source/combined-runtime-source.blend'),'helperSha256':sha(Path(__file__)),'emitters':records,'limits':['Inventory only; actual modifiers may block numericfixture adoption; no source save or Native parity']},indent=2)+'\n');print('CS_ACTUAL_SPOT_EMITTER_INSPECT_OK',flush=True)
