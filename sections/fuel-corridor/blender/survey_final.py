"""Read-only saved Fuel Corridor survey; never saves or alters the artifact."""
import bpy,json,hashlib,sys,argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
s=bpy.context.scene
def val(v):
 if isinstance(v,(str,int,float,bool)) or v is None:return v
 try:return [val(x) for x in v]
 except:return str(v)
result={'filepath':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'objects':len(s.objects),'materials':len(bpy.data.materials),'properties':{k:val(s[k]) for k in s.keys()},'render':{'engine':s.render.engine,'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'cycles_samples':s.cycles.samples,'view':[s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure]},'cameras':[{ 'name':o.name,'location':list(o.location),'rotation':list(o.rotation_euler),'lens':o.data.lens} for o in s.objects if o.type=='CAMERA'],'images':[{'name':i.name,'path':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images],'libraries':[l.filepath for l in bpy.data.libraries],'lights':[{'name':o.name,'color':list(o.data.color),'energy':o.data.energy} for o in s.objects if o.type=='LIGHT']}
out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2),encoding='utf-8');print('SURVEY',result['sha256'],result['objects'],result['render'],[(k,result['properties'][k]) for k in ['revision','stage','wayfinding_revision'] if k in result['properties']])
