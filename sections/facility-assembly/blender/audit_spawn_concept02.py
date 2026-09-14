"""Cold-load, source, route-margin and targeted exact contact evidence. No scene save."""
import bpy,json,hashlib,os,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review';rev=os.environ.get('SPAWN_REV','R02');path=R/'blender'/('facility_spawn_concept02_'+rev+'.blend')
bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
s=bpy.context.scene;col=bpy.data.collections['29_SPAWN_APPROVED_EXTERIOR'];build=json.loads((O/('BUILD_'+rev+'.json')).read_text())
objects=list(col.objects);ground=[]
for o in objects:
 if o.type=='MESH' and (any(o.name.startswith(n) for n in ['Wall planting bed','Spare pipe rack foot']) or 'laid membrane field' in o.name):
  p=o.matrix_basis.translation;ground.append((o.name,p.copy(),o.dimensions.z/2))
col.hide_viewport=True;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
contacts=[]
for name,p,half in ground:
 hit,loc,norm,index,obj,mat=s.ray_cast(dg,Vector((p.x,p.y,p.z+.12 if 'laid membrane field' in name else .35)),Vector((0,0,-1)),distance=.8)
 gap=p.z-half-loc.z if hit else None
 contacts.append({'object':name,'support':obj.name if hit else None,'ground_z':loc.z if hit else None,'base_z':p.z-half,'signed_gap_m':gap,'pass':hit and -.06<=gap<=.012})
anchors=[]
for prefix,c,n in [('South service',Vector((-33.65,.70,1.10)),Vector((0,-1,0))),('East service',Vector((-19.64,3,1.12)),Vector((1,0,0)))]:
 tangent=Vector((-n.y,n.x,0))
 for dx in [-.37,.37]:
  for z in [-.43,.43]:
   start=c+tangent*dx+Vector((0,0,z))+n*.09
   hit,loc,*rest=s.ray_cast(dg,start,-n,distance=.25)
   anchors.append({'fixture':prefix,'point':list(start),'hit':hit,'distance_m':(loc-start).length if hit else None,'support':rest[-2].name if hit else None,'pass':hit})
returns=[]
for prefix,ends,n in [('South',[(-34.8,.35,.45),(-31.45,.35,.45)],Vector((0,-1,0))),('East',[(-19.34,2,.65),(-19.34,6.25,.65)],Vector((1,0,0)))]:
 for p in ends:
  hit,loc,*rest=s.ray_cast(dg,Vector(p),-n,distance=.5)
  support=rest[-2].name if hit else ''
  wall_hit=hit and any(word in support.lower() for word in ['panel','wall']) and 'downpipe' not in support.lower()
  returns.append({'run':prefix,'start':p,'hit':hit,'wall_distance_m':(loc-Vector(p)).length if hit else None,'support':support,'pass':wall_hit})
sources=[]
for row in json.loads((R/'production/SOURCES.json').read_text()):
 p=R/row['frozen'];digest=hashlib.sha256(p.read_bytes()).hexdigest();sources.append({'section':row['id'],'frozen_sha256':digest,'pass':digest==row['source_sha256']})
missing=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.users and not im.packed_file:
  p=Path(bpy.path.abspath(im.filepath,library=im.library))
  if not p.exists():missing.append({'image':im.name,'path':str(p)})
placements=json.loads((R/'production/LAYOUT_A12.json').read_text())['placements'];poses=[]
for sid,pose in placements.items():
 ob=bpy.data.objects.get(sid)
 if ob:
  distance=(ob.location-Vector(pose['translation'])).length;angle=abs(math.degrees(ob.rotation_euler.z)-pose['rotation_z_degrees'])%360;angle=min(angle,360-angle)
  poses.append({'section':sid,'translation_error':distance,'rotation_error':angle,'pass':distance<.0001 and angle<.001})
report={'revision':rev,'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'cold_load':'PASS','new_object_count':len(objects),'new_mesh_faces':sum(len(o.data.polygons) for o in objects if o.type=='MESH'),'ground_contacts':contacts,'wall_anchor_contacts':anchors,'utility_wall_returns':returns,'source_preservation':sources,'placements':poses,'missing_used_images':missing,'scope':'Exact targeted ray intersections for new bed/rack bases and wall anchors/returns, not blanket structural certification of every retained source object. Leaf geometry and illustrative finish marks are decorative.'}
report['targeted_checks_pass']=all(x['pass'] for group in [contacts,anchors,returns,sources,poses] for x in group) and not missing
(O/('TECHNICAL_'+rev+'.json')).write_text(json.dumps(report,indent=2));print('TECHNICAL',report['targeted_checks_pass'],'ground',contacts,'anchors',anchors,'returns',returns,flush=True)

