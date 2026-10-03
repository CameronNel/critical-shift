"""Read-only authoring-state fingerprint for an independent cold-start rebuild."""
import bpy, json, hashlib, sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
label=sys.argv[sys.argv.index('--')+1]
source=Path(bpy.data.filepath)
filehash=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=filehash(source)
def value(x):
 if x is None or isinstance(x,(str,bool,int)):return x
 if isinstance(x,float):return round(x,9)
 if isinstance(x,bpy.types.ID):return dict(id_type=type(x).__name__,name=x.name)
 try:return [value(v) for v in x]
 except TypeError:return type(x).__name__
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def properties(x,skip=()):
 out={}
 for prop in x.bl_rna.properties:
  key=prop.identifier
  if key in skip or key in {'rna_type','name'} or prop.type=='COLLECTION' or prop.is_readonly:continue
  if prop.type=='POINTER' and key not in {'object','texture','node_group','image'}:continue
  try:out[key]=value(getattr(x,key))
  except (AttributeError,TypeError):pass
 return out
def nodegraph(tree):
 if tree is None:return None
 nodes=[]
 for node in tree.nodes:
  item=dict(name=node.name,type=node.type,settings=properties(node,('location','dimensions','width','height','select','label','parent','inputs','outputs')),
            inputs={i.identifier:value(i.default_value) for i in node.inputs if hasattr(i,'default_value')})
  if hasattr(node,'color_ramp'):
   item['ramp']=dict(interpolation=node.color_ramp.interpolation,elements=[dict(position=value(e.position),color=value(e.color)) for e in node.color_ramp.elements])
  nodes.append(item)
 return dict(nodes=sorted(nodes,key=lambda n:n['name']),links=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in tree.links))
objects={}
for o in bpy.context.scene.objects:
 item=dict(type=o.type,matrix=value(o.matrix_world),parent=o.parent.name if o.parent else None,
           hide_render=o.hide_render,custom={k:value(o[k]) for k in o.keys()},
           modifiers=[dict(type=m.type,settings=properties(m)) for m in o.modifiers])
 if o.type=='MESH':
  item['mesh']=dict(vertices=[value(v.co) for v in o.data.vertices],
                    faces=[dict(vertices=list(p.vertices),smooth=p.use_smooth,material=p.material_index) for p in o.data.polygons],
                    corner_normals=[value(n.vector) for n in o.data.corner_normals],
                    materials=[m.name if m else None for m in o.data.materials])
 elif o.type=='FONT':
  item['font']=dict(body=o.data.body,size=value(o.data.size),extrude=value(o.data.extrude),
                    align_x=o.data.align_x,space_character=value(o.data.space_character),
                    materials=[m.name if m else None for m in o.data.materials])
 elif o.type=='CURVE':
  item['curve']=dict(bevel_depth=value(o.data.bevel_depth),bevel_mode=o.data.bevel_mode,
                     bevel_object=o.data.bevel_object.name if o.data.bevel_object else None,
                     fill_caps=o.data.use_fill_caps,dimensions=o.data.dimensions,fill_mode=o.data.fill_mode,
                     resolution=o.data.resolution_u,
                     splines=[dict(type=sp.type,cyclic=sp.use_cyclic_u,
                       points=[dict(co=value(p.co),left=value(p.handle_left),right=value(p.handle_right)) for p in sp.bezier_points] if sp.type=='BEZIER' else [value(p.co) for p in sp.points]) for sp in o.data.splines],
                     materials=[m.name if m else None for m in o.data.materials])
 elif o.type in {'CAMERA','LIGHT'}:item['data']=properties(o.data)
 objects[o.name]=digest(item)
materials={m.name:digest(dict(properties=properties(m,('preview','node_tree')),nodes=nodegraph(m.node_tree))) for m in bpy.data.materials if m.users}
scene=bpy.context.scene
scene_state=dict(world=nodegraph(scene.world.node_tree),
                 support_registry=scene.get('support_registry'),
                 printed_surface_registry=scene.get('printed_surface_registry'),
                 collections={c.name:dict(hidden=c.hide_render,objects=sorted(o.name for o in c.objects),children=sorted(ch.name for ch in c.children)) for c in bpy.data.collections if c.users})
report=dict(source=str(source),source_sha256=before,objects=objects,materials=materials,
            scene_state_sha256=digest(scene_state),source_unchanged=filehash(source)==before,
            limitations='Authoring geometry, poses, material graphs and fixtures. This does not replace pixel comparison or independent art acceptance.')
assert report['source_unchanged']
out=root/'production/coldstart'/f'fingerprint_{label}.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2))
print('FINGERPRINT_WRITTEN',label,len(objects),len(materials),flush=True)
