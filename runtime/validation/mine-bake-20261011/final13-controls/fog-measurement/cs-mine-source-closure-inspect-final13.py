# Read-only Blender inspection. Does not render or save any source scene.
import bpy,json,hashlib
from mathutils import Vector
from pathlib import Path
root=Path('/workspace/critical-shift-spawn-runtime');snapshot=root/'runtime/out/spawn-export-source/combined-runtime-source.blend';output=Path('/tmp/cs-mine-source-closure-inspect-final13.json')
assert not output.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
scene=bpy.context.scene;instance=bpy.data.objects['ROOM_mine'];dg=bpy.context.evaluated_depsgraph_get();volumes=[];selected=[];fonts=[]
def value(socket):
 v=socket.default_value
 if isinstance(v,(str,bool,int,float)):return v
 try:return list(v)
 except TypeError:return repr(v)
for o in instance.instance_collection.all_objects:
 if o.type not in {'MESH','FONT','CURVE'}:continue
 if o.type=='FONT':fonts.append({'object':o.name,'body':o.data.body,'extrude':o.data.extrude,'bevelDepth':o.data.bevel_depth})
 if o.name in {'R39 | Shed frame','R39 | Shed boards','R39 | Post number','R39 | Shed signs','R39 | Sign text','R39 | Sign boards'}:
  d={'name':o.name,'type':o.type,'matrixLocal':list(o.matrix_local),'visibleShadow':o.visible_shadow,'materials':[m.name if m else None for m in o.data.materials]}
  if o.type=='FONT':d.update({'text':o.data.body,'extrude':o.data.extrude,'bevelDepth':o.data.bevel_depth})
  selected.append(d)
 for material in o.data.materials:
  if not material or not material.use_nodes:continue
  for node in material.node_tree.nodes:
   if node.type!='PRINCIPLED_VOLUME':continue
   outputs=[n for n in material.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output]
   actual_instances=[i.matrix_world.copy() for i in dg.object_instances if i.object.original==o];assert len(actual_instances)==1;world=actual_instances[0];bounds=[world@Vector(v) for v in o.bound_box]
   attributes=[{'name':a.name,'type':a.data_type,'domain':a.domain} for a in getattr(o.data,'attributes',[])]
   volumes.append({'worldMatrix':[list(row) for row in world],'worldBounds':{'minimum':[min(v[i] for v in bounds) for i in range(3)],'maximum':[max(v[i] for v in bounds) for i in range(3)]},'meshAttributes':attributes,'visibility':{k:getattr(o,k) for k in ['visible_camera','visible_diffuse','visible_glossy','visible_transmission','visible_volume_scatter','visible_shadow']},'hideRender':o.hide_render,'library':o.library.filepath if o.library else None,'object':o.name,'material':material.name,'node':node.name,'visibleShadow':o.visible_shadow,'outputs':[{'name':n.name,'volumeLinks':[{'node':l.from_node.name,'socket':l.from_socket.name} for l in n.inputs['Volume'].links]} for n in outputs],'inputs':{s.name:{'default':value(s),'linked':s.is_linked,'links':[{'node':l.from_node.name,'type':l.from_node.type,'socket':l.from_socket.name} for l in s.links]} for s in node.inputs if hasattr(s,'default_value')}})
assert len(volumes)==2 and {v['object'] for v in volumes}=={'R38 | Tunnel haze','R39 | Shed haze'}
for v in volumes:
 assert len(v['outputs'])==1 and len(v['outputs'][0]['volumeLinks'])==1
 assert v['outputs'][0]['volumeLinks'][0]['node']==v['node'], 'Unsupported active volume topology'
 v['activePrincipledClosureDirect']=True
result={'status':'ReadOnlySourceClosureInspection','snapshotSha256':sha(snapshot),'helperSha256':sha(Path(__file__)),'blenderVersion':bpy.app.version_string,'scene':scene.name,'volumes':volumes,'selectedObjects':selected,'fonts':fonts,'zeroOneFonts':[f for f in fonts if f['body'].strip()=='01'],'signCheck':'CompleteForFoundFontsOnly' if any(f['body'].strip()=='01' for f in fonts) else 'IncompleteNo01FontFound','limits':['No render, source save, native match or visual acceptance','Linked source closure inputs inspected, not procedural density reevaluated']}
# Matrix row objects require numeric conversion for serialization.
for o in result['selectedObjects']:o['matrixLocal']=[list(v) for v in o['matrixLocal']]
output.write_text(json.dumps(result,indent=2)+'\n');print('CS_SOURCE_CLOSURE_INSPECTION_OK',flush=True)
