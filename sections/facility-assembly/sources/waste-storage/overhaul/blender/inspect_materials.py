"""Read-only surfacing/coordinate inventory; no visual-acceptance inference."""
import bpy,sys,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];repo=root.parents[4]
revision=sys.argv[sys.argv.index('--')+1]
source=Path(bpy.data.filepath);before=hashlib.sha256(source.read_bytes()).hexdigest()
objects=[];images=[];uv_consumers=[];materials=[]
visible=[o for o in bpy.context.scene.objects if not o.hide_render]
used={m.name:m for o in visible if hasattr(o.data,'materials') for m in o.data.materials if m}
def material_nodes(tree,seen=None):
 seen=set() if seen is None else seen
 if tree.as_pointer() in seen:return
 seen.add(tree.as_pointer())
 for node in tree.nodes:
  yield node
  if node.type=='GROUP' and node.node_tree:
   yield from material_nodes(node.node_tree,seen)
for o in visible:
 if o.type!='MESH':continue
 objects.append(dict(object=o.name,uv_layers=[u.name for u in o.data.uv_layers],
                     modified=bool(o.get('overhaul_modified')),added=bool(o.get('overhaul_added'))))
for name,m in sorted(used.items()):
 spaces=set()
 if m.use_nodes:
  for n in material_nodes(m.node_tree):
   if n.type=='TEX_IMAGE':images.append(dict(material=name,image=n.image.name if n.image else None))
   if n.type=='NEW_GEOMETRY' and n.outputs['Position'].is_linked:spaces.add('world_position_meters')
   if n.type=='TEX_COORD':
    for out in n.outputs:
     if out.is_linked:spaces.add('texture_coordinate_'+out.name)
    if n.outputs['UV'].is_linked:uv_consumers.append(name)
   if n.type=='UVMAP':uv_consumers.append(name)
 materials.append(dict(material=name,coordinate_spaces=sorted(spaces)))
report=dict(revision=revision,source=source.resolve().relative_to(repo).as_posix(),source_sha256=before,
            visible_materials=materials,mesh_uv_inventory=objects,image_texture_consumers=images,
            uv_shader_consumers=sorted(set(uv_consumers)),
            source_unchanged=hashlib.sha256(source.read_bytes()).hexdigest()==before,
            scope='Coordinate/dependency inventory only; actual fixed-view material review is separate. No UV-map/export equivalence claim.')
(root/'production'/('material_contract_'+revision+'.json')).write_text(json.dumps(report,indent=2)+'\n')
print('MATERIAL_CONTRACT',revision,len(used),'image_nodes',len(images),'uv_consumers',len(set(uv_consumers)))
