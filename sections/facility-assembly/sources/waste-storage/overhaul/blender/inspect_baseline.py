"""Read-only scene inventory and original protection records."""
import bpy,json,hashlib
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parents[1];s=bpy.context.scene
records=[]
for o in sorted(s.objects,key=lambda x:x.name):
 r={'name':o.name,'type':o.type,'location':list(o.location),'dimensions':list(o.dimensions),'matrix_world':[list(x) for x in o.matrix_world],'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection],'hide_render':o.hide_render,'properties':{k:str(v) for k,v in o.items()},'materials':[m.name if m else None for m in o.data.materials] if o.type in {'MESH','CURVE','FONT'} else []}
 if o.type=='LIGHT':r.update(energy=o.data.energy,light_type=o.data.type,color=list(o.data.color),size=getattr(o.data,'size',None))
 if o.type=='CAMERA':r.update(lens=o.data.lens,sensor_width=o.data.sensor_width)
 if o.type=='FONT':r['text']=o.data.body
 if o.type=='MESH':r['triangles']=sum(len(p.vertices)-2 for p in o.data.polygons)
 records.append(r)
materials=[]
for m in bpy.data.materials:
 bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
 materials.append({'name':m.name,'diffuse':list(m.diffuse_color),'nodes':m.use_nodes,'base':list(bs.inputs['Base Color'].default_value) if bs else None,'roughness':bs.inputs['Roughness'].default_value if bs else None,'metallic':bs.inputs['Metallic'].default_value if bs else None,'emission':bs.inputs['Emission Strength'].default_value if bs else None})
source=Path(bpy.data.filepath)
report={'source':source.relative_to(root.parents[4]).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scene':s.name,'object_count':len(records),'collections':dict(Counter(c.name for o in s.objects for c in o.users_collection)),'render_engine':s.render.engine,'world_strength':s.world.node_tree.nodes.get('Background').inputs['Strength'].default_value if s.world and s.world.use_nodes else None,'color_management':{'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure},'objects':records,'materials':materials,'libraries':[l.filepath for l in bpy.data.libraries],'images':[{'name':i.name,'filepath':i.filepath,'packed':bool(i.packed_file),'source':i.source} for i in bpy.data.images]}
(root/'production/baseline_inventory.json').write_text(json.dumps(report,indent=2)+'\n')
protected={r['name']:r for r in records if r['type'] in {'EMPTY','CAMERA'} or r['properties'].get('assembly_root')=='1' or r['properties'].get('assembly_root')=='True'}
(root/'production/protected_original.json').write_text(json.dumps({'source_sha256':report['source_sha256'],'objects':protected},indent=2)+'\n')
print('BASELINE_INVENTORY',len(records),'protected',len(protected),'materials',len(materials),flush=True)
