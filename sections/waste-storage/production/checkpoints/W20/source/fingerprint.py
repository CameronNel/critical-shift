"""Deterministic evaluated fingerprint of an opened artifact; no build/save."""
import bpy,json,hashlib,sys,argparse
from pathlib import Path
from collections import Counter
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
def val(x):
 if isinstance(x,(str,bool,int)) or x is None:return x
 if isinstance(x,float):return round(x,6)
 try:return [val(v) for v in x]
 except TypeError:return getattr(x,'name',str(type(x)))
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
objects=[];open_meshes=[]
for o in sorted(s.objects,key=lambda o:o.name):
 row={'name':o.name,'type':o.type,'matrix':val([v for r in o.matrix_world for v in r]),'parent':o.parent.name if o.parent else None}
 if o.type in ['MESH','FONT','CURVE']:
  e=o.evaluated_get(dg);m=e.to_mesh();vs=[val(e.matrix_world@v.co) for v in m.vertices];fs=[list(f.vertices) for f in m.polygons];edges=Counter()
  for f in m.polygons:
   ids=list(f.vertices)
   for i,j in zip(ids,ids[1:]+ids[:1]):edges[tuple(sorted((i,j)))]+=1
  boundary=sum(n==1 for n in edges.values());nonmanifold=sum(n>2 for n in edges.values())
  if boundary or nonmanifold:open_meshes.append({'name':o.name,'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'role':'coating plane' if o.name.startswith(('Wear at repeatedly handled edge','Divider oxide lower band')) else 'requires classification'})
  row.update(geometry_hash=digest([vs,fs]),vertices=len(vs),polygons=len(fs),materials=[m.name if m else None for m in o.data.materials]);e.to_mesh_clear()
 if o.type=='CAMERA':row['camera']={'lens':val(o.data.lens),'clip_start':val(o.data.clip_start),'clip_end':val(o.data.clip_end)}
 if o.type=='LIGHT':row['light']={'type':o.data.type,'energy':val(o.data.energy),'color':val(o.data.color),'size':val(getattr(o.data,'size',None)),'spot_size':val(getattr(o.data,'spot_size',None))}
 if o.type=='FONT':row['text']={'body':o.data.body,'size':val(o.data.size),'font':o.data.font.name}
 row['hooks']={k:val(o[k]) for k in ['equipment_type','connection_id','outward_normal','target_id','door_id','closed_angle_z','open_angle_z','authority','implemented','dimensions_m'] if k in o}
 objects.append(row)
materials=[]
for m in sorted([m for m in bpy.data.materials if m.users],key=lambda m:m.name):
 nodes=[];links=[]
 if m.use_nodes:
  for n in sorted(m.node_tree.nodes,key=lambda n:n.name):
   r={'name':n.name,'type':n.bl_idname,'inputs':{str(i)+':'+v.name:val(v.default_value) for i,v in enumerate(n.inputs) if hasattr(v,'default_value')}}
   if n.type=='VALTORGB':r['ramp']=[{'position':val(e.position),'color':val(e.color)} for e in n.color_ramp.elements]
   nodes.append(r)
  links=sorted((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links)
 materials.append({'name':m.name,'diffuse':val(m.diffuse_color),'nodes':nodes,'links':links})
result={'revision':s.get('revision'),'source_file':bpy.data.filepath,'file_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'object_hash':digest(objects),'material_hash':digest(materials),'objects':objects,'materials':materials,'open_meshes':open_meshes,'contract_sha256':hashlib.sha256(s.get('interface_json','').encode()).hexdigest(),'external_libraries':[l.filepath for l in bpy.data.libraries],'images':[{'name':i.name,'source':i.source,'packed':bool(i.packed_file)} for i in bpy.data.images]}
out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2));print('FINGERPRINT',json.dumps({k:result[k] for k in ['revision','object_hash','material_hash']}),flush=True)
