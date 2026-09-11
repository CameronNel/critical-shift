"""Read-only canonical saved-artifact fingerprint for cold reopen and source-replay comparison."""
import bpy,json,hashlib,sys,argparse
from pathlib import Path
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
def val(x):
 if isinstance(x,(str,int,bool)) or x is None:return x
 if isinstance(x,float):return round(x,7)
 try:return [val(v) for v in x]
 except:return str(x)
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
objects={}
for o in sorted(s.objects,key=lambda o:o.name):
 row={'type':o.type,'matrix':val(o.matrix_world),'parent':o.parent.name if o.parent else None,'properties':{k:val(o[k]) for k in o.keys()},'hidden_render':o.hide_render}
 if o.type in ['MESH','FONT','CURVE']:
  e=o.evaluated_get(dg);m=e.to_mesh();row['mesh']=digest({'vertices':[val(v.co) for v in m.vertices],'faces':[list(f.vertices) for f in m.polygons],'face_materials':[f.material_index for f in m.polygons]});e.to_mesh_clear();row['materials']=[m.name if m else None for m in o.data.materials]
 if o.type=='FONT':row['text']={'body':o.data.body,'size':o.data.size,'font':o.data.font.name}
 if o.type=='CAMERA':row['camera']={k:val(getattr(o.data,k)) for k in ['lens','sensor_width','clip_start','clip_end','type']}
 if o.type=='LIGHT':row['light']={k:val(getattr(o.data,k,None)) for k in ['type','energy','color','size','size_y','shape','spread']}
 objects[o.name]=row
def nodes(nt):
 return {'nodes':{n.name:{'type':n.bl_idname,'inputs':{i.name:val(i.default_value) for i in n.inputs if hasattr(i,'default_value')},'ramp':[[e.position,val(e.color)] for e in n.color_ramp.elements] if n.type=='VALTORGB' else None} for n in nt.nodes},'links':sorted([(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in nt.links])}
materials={m.name:nodes(m.node_tree) for m in bpy.data.materials if m.use_nodes}
state={'objects':objects,'materials':materials,'world':nodes(s.world.node_tree),'contract':json.loads(s['interface_json']),'camera_manifest':json.loads(s['camera_manifest']),'units':[s.unit_settings.system,s.unit_settings.scale_length],'view':[s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,s.view_settings.gamma],'saved_render':[s.render.engine,s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.cycles.samples,s.cycles.seed],'sources':json.loads(s['authoring_sources'])}
out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps({'revision':s.get('revision'),'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'state_sha256':digest(state),'state':state},indent=2));print('COLD_FINGERPRINT',s.get('revision'),digest(state),len(objects))
